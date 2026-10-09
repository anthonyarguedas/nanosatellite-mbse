#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = []
# ///
"""Check current lifecycle scenarios and black-box traceability with licensed Syside.

All current model dependencies are included. The checks below assess scenario
and black-box consistency. No model-quality check is framework or EPS product
V&V. Negative cases change temporary copies only.
"""
from __future__ import annotations

import argparse
import importlib.util
from itertools import product
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import audit_report as report_tables

CURRENT_FILES = tuple(f'{n}.sysml' for n in (
    '00-domain', '01-concerns', '02-needs-context', '03-requirements',
    '04-logical', '05-verification', '06-system-context', '07-report-views',
    '08-physical-vocabulary', '09-scenarios', '10-interface-views',
    '11-logical-responsibilities')) + tuple(
    f'candidates/{n}.sysml' for n in ('comet', 'custom', 'git-yaml', 'nanospace', 'valispace'))
SC_MRS = {1: {1}, 2: {2, 3, 4, 5}, 3: {3, 4},
          4: {5, 6}, 5: {1, 2, 3, 4, 5, 6}}
FR_IDS = {f"FR_{n:02}" for n in range(1, 43) if n not in (12, 40)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def evaluate_guard(api, expression, environment):
    """Evaluate a small Boolean/enum subset of the genuine Syside semantic tree.

    Inputs are reference decisions for specification checks, not observations of
    an implemented framework. Unknown references/operators fail closed.
    """
    if expression is None:
        return True
    if isinstance(expression, api.FeatureReferenceExpression):
        feature = expression.referent
        require(feature in environment,
                f"BaselineControl: uncontrolled guard reference {feature.qualified_name}")
        return environment[feature]
    if isinstance(expression, api.FeatureChainExpression):
        operands = list(expression.operands)
        require(len(operands) == 1, "BaselineControl: invalid feature chain")
        record = evaluate_guard(api, operands[0], environment)
        require(isinstance(record, dict) and expression.target_feature in record,
                "BaselineControl: disposition is not from the accepted decision payload")
        return record[expression.target_feature]
    if isinstance(expression, api.LiteralBoolean):
        return expression.value
    require(isinstance(expression, api.OperatorExpression),
            "BaselineControl: unsupported native guard expression")
    operator = str(expression.operator)
    operands = [evaluate_guard(api, operand, environment) for operand in expression.operands]
    if operator in ("and", "or", "not"):
        require(all(type(v) is bool for v in operands), "BaselineControl: non-Boolean guard operand")
        require(len(operands) == (1 if operator == "not" else 2),
                "BaselineControl: invalid Boolean operator arity")
        return (not operands[0] if operator == "not" else
                all(operands) if operator == "and" else any(operands))
    require(operator in ("==", "!=") and len(operands) == 2,
            f"BaselineControl: unsupported native guard operator {operator}")
    equal = operands[0] == operands[1]
    return equal if operator == "==" else not equal


def check_review_control(elements, by, api):
    state = by["ScenarioViews::BaselineControl"]
    event = by["ScenarioViews::DecideReview"]
    decision_type = by["FrameworkDomain::TechnicalReviewDecision"]
    disposition = by["FrameworkDomain::TechnicalReviewDecision::disposition"]
    enumeration = by["FrameworkDomain::ReviewDisposition"]
    enums = {name: by[f"FrameworkDomain::ReviewDisposition::{name}"]
             for name in ("accepted", "conditional", "progressionBlocked")}
    require(event.conforms(decision_type) and enumeration in disposition.types,
            "BaselineControl: review event lacks the recorded decision/disposition type")
    flags = {name: by[f"ScenarioViews::BaselineControl::{name}"] for name in
             ("authorizedCurrent", "blocking", "conditionalRecordsComplete", "closureComplete")}
    require(all(any(str(t.qualified_name) == "ScalarValues::Boolean" for t in f.types)
                for f in flags.values()),
            "BaselineControl: invalid Boolean control type")
    states = {name: by[f"ScenarioViews::BaselineControl::{name}"] for name in
              ("underReview", "acceptedBaseline", "conditional", "progressionBlocked")}
    transitions = [e for e in state.owned_features if isinstance(e, api.TransitionUsage)]
    reviews = []
    payload_references = {}
    for transition in transitions:
        trigger = transition.trigger_action
        payload = trigger.payload_parameter if trigger is not None else None
        if payload is not None and event in payload.types:
            require(len(transition.trigger_actions) == 1,
                    "BaselineControl: ambiguous review trigger")
            reviews.append(transition)
            # Syside binds the transition's named payload to accepter.payload by
            # a Subsetting whose target is a resolved FeatureChaining.
            refs = {payload}
            for relation in elements:
                if type(relation).__name__ == "Subsetting" and any(
                    list(target.chaining_features) == [trigger, payload] for target in relation.targets
                ):
                    refs.update(relation.sources)
            payload_references[transition] = refs
        if transition.target in (states["acceptedBaseline"], states["conditional"],
                                  states["progressionBlocked"]):
            require(transition in reviews, "BaselineControl: disposition path bypasses the review decision")
    require(not any(type(e).__name__ == "SuccessionAsUsage" and e.owner == state and
                    states["acceptedBaseline"] in e.target_features for e in elements),
            "BaselineControl: unguarded acceptance bypass")
    paths = {(t.source, t.target) for t in reviews}
    for source in ("underReview", "conditional"):
        for target in ("acceptedBaseline", "conditional", "progressionBlocked"):
            require((states[source], states[target]) in paths,
                    f"BaselineControl: missing {'renewed' if source == 'conditional' else 'initial'} {target} decision path")
    require(all(t.source in (states["underReview"], states["conditional"]) for t in reviews),
            "BaselineControl: decision can bypass review submission")

    def enabled(source, chosen, values):
        environment = {flags[name]: v for name, v in values.items()}
        environment.update({v: v for v in enums.values()})
        record = {disposition: enums[chosen]}
        admitted = []
        for transition in reviews:
            if transition.source != states[source]:
                continue
            inputs = environment | {ref: record for ref in payload_references[transition]}
            guard = evaluate_guard(api, transition.guard_expression, inputs)
            require(type(guard) is bool, "BaselineControl: non-Boolean transition guard")
            if guard:
                admitted.append(transition)
        return admitted

    counterexample = dict(authorizedCurrent=True, blocking=False,
                          conditionalRecordsComplete=True, closureComplete=True)
    admitted = enabled("conditional", "conditional", counterexample)
    require(len(admitted) == 1 and admitted[0].target == states["conditional"],
            "BaselineControl: closed prior conditions override renewed conditional disposition")
    count = 0
    for source, chosen, bits in product(("underReview", "conditional"), enums, product((False, True), repeat=4)):
        values = dict(zip(flags, bits))
        authorized, blocking, complete, closed = bits
        expected = None
        if authorized:
            if chosen == "progressionBlocked":
                expected = states["progressionBlocked"]
            elif not blocking:
                if chosen == "accepted" and (source == "underReview" or closed):
                    expected = states["acceptedBaseline"]
                elif chosen == "conditional" and complete:
                    expected = states["conditional"]
        actual = enabled(source, chosen, values)
        require([t.target for t in actual] == ([] if expected is None else [expected]),
                f"BaselineControl: review transition mismatch from {source}, disposition={chosen}, "
                f"{values}, enabled={[t.name for t in actual]}")
        count += 1
    return {"source": "Syside semantic expression tree", "review_transitions": len(reviews),
            "truth_table_cases": count, "closed_prior_conditions_renewed_conditional": "remains conditional",
            "renewed_dispositions": {"accepted": "acceptedBaseline", "conditional": "conditional",
                                     "progressionBlocked": "progressionBlocked"}}


def validate_report_contract(requirements_text, io_text, ledger):
    published = report_tables.parse_fr_tables(requirements_text, io_text)
    ledger_fr = report_tables.unique(ledger['framework_requirements'], 'ledger FR')
    require(set(ledger_fr) == set(published), 'FR report/ledger active ID mismatch')
    for rid, row in published.items():
        for direction in ('inputs', 'outputs'):
            require(row[direction] == ledger_fr[rid][direction], f'{rid}: report/ledger {direction} disagreement')
    return published


def report_parent_numbers(text, identifier):
    rows = re.findall(rf'^FR-{identifier} & [^\n]*? & (MR-[^\n]*?)\.\\par ', text, re.M)
    require(len(rows) == 1, f'FR-{identifier}: missing/duplicate current report row')
    parents = []
    for term in rows[0].split(','):
        bounds = re.fullmatch(r'MR-(\d{2})(?:--(?:MR-)?(\d{2}))?', term.strip())
        require(bounds is not None, 'Malformed current MR parent reference')
        first, last = int(bounds[1]), int(bounds[2] or bounds[1])
        require(last >= first, 'Reversed current MR parent range')
        parents.extend(f'{n:02}' for n in range(first, last + 1))
    require(len(parents) == len(set(parents)), 'Duplicate current MR parent reference')
    return set(parents)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--model-root", type=Path,
                        help="alternate complete current slice for negative checks")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--ledger", type=Path,
                        default=Path(__file__).resolve().parent.parent / "traceability/framework-baseline.json")
    parser.add_argument("--negative-cases", action="store_true")
    args = parser.parse_args()
    root = args.model_root or Path(__file__).resolve().parent
    config = args.config or Path(__file__).resolve().parent / "scenarios.toml"
    report = args.report or Path(__file__).resolve().parent.parent / "requirements.tex"
    spec = importlib.util.spec_from_file_location("scenario_native_tool", args.tool.resolve())
    require(spec is not None and spec.loader is not None, "Cannot load native wrapper")
    tool = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = tool
    spec.loader.exec_module(tool)
    result = tool.validate([root / n for n in CURRENT_FILES], [],
                           warnings_as_errors=True, config=config)
    try:
        model, api = tool.require_semantic_model(result)
    except tool.ToolError as error:
        if error.exit_code == 1:
            details = '; '.join(d.message for d in result.diagnostics[:6])
            raise ValueError('Native model invalid: ' + (details or str(error))) from error
        raise RuntimeError('Native tooling unavailable: ' + str(error)) from error
    elements = list(model.nodes(api.Element, include_subtypes=True))
    by_qn = {str(e.qualified_name): e for e in elements if e.qualified_name}
    compiler = api.Compiler()
    styles = tomllib.loads(config.read_text())["viz"]["style"]["group"]

    def qn(e):
        return str(e.qualified_name)

    def value(feature, scope):
        evaluated, diagnostics = compiler.evaluate_feature(feature, scope)
        require(bool(diagnostics), f"Cannot evaluate {feature.name}")
        return evaluated

    def fields(annotation):
        return {f.name: value(f, annotation) for f in annotation.owned_features}

    def endpoint(e):
        return e.referenced_feature or e

    def dependencies(source):
        return [e for e in elements if isinstance(e, api.Dependency)
                and source in e.sources]

    def targets(source):
        return {qn(t) for d in dependencies(source) for t in d.targets}

    scenarios = [by_qn[f"ScenarioViews::SC{n:02}"] for n in range(1, 6)]
    summaries = [by_qn[f"ScenarioViews::SC{n:02}Summary"] for n in range(1, 6)]
    for n, scenario in enumerate(scenarios, 1):
        ts = targets(scenario)
        require(f"FrameworkNeeds::UC{n:02}" in ts, f"SC{n:02}: missing UC derivation")
        actual = {int(t.rsplit("_", 1)[1]) for t in ts if t.startswith("FrameworkNeeds::MR_")}
        require(actual == SC_MRS[n], f"SC{n:02}: wrong MR derivation")
        uc = by_qn[f"FrameworkNeeds::UC{n:02}"]
        uc_mrs = {int(t.rsplit("_", 1)[1]) for t in targets(uc)
                  if t.startswith("FrameworkNeeds::MR_")}
        require(actual == uc_mrs, f"SC{n:02}: disagrees with approved UC/MR links")
        if n < 5:
            require("ScenarioViews::SC05" in ts, f"SC{n:02}: missing shared review/change behavior")
        require(qn(scenario) in targets(summaries[n-1]), "Summary lacks full scenario link")

    tasks = [e for e in elements if type(e).__name__ in ("ActionUsage", "PerformActionUsage")
             and e.owner in scenarios + summaries and e.declared_name]
    allocations = [e for e in elements if type(e).__name__ == "AllocationUsage"
                   and qn(e.owner) == "ScenarioViews"]
    tags = {"ScenarioViews::FrameworkAction": ("ActionUsage", "framework"),
            "ScenarioViews::ExternalAction": ("PerformActionUsage", "external")}
    metadata = [e for e in elements if isinstance(e, api.MetadataUsage)
                and any(qn(t) in tags for t in e.types)]
    allowed_actors = {f"ScenarioViews::{n}" for n in (
        "framework", "systemsEngineer", "epsEngineer", "analysisTools",
        "hostToolchain", "reviewers", "reviewAuthority")}
    for task in tasks:
        attached = [m for m in metadata if task in m.annotated_elements]
        require(len(attached) == 1, f"{qn(task)}: missing responsibility")
        annotation = attached[0]
        tag = next(qn(t) for t in annotation.types if qn(t) in tags)
        kind, group = tags[tag]
        require(type(task).__name__ == kind, "Actor/style metaclass disagreement")
        f = fields(annotation)
        actor = f["performer"].element
        require(qn(actor) in allowed_actors, f"{qn(task)}: out-of-scope performer")
        require((qn(actor) == "ScenarioViews::framework") == (group == "framework"),
                "Framework/external allocation disagreement")
        require(f["fillColor"] == styles[group]["fill_header"] == styles[group]["fill_body"],
                "Responsibility/native color disagreement")
        require(styles[group]["members"] == [kind], "Wrong native style selector")
        assigned = [a for a in allocations if a.source_feature == task]
        require(len(assigned) == 1 and list(assigned[0].target_features) == [actor],
                f"{qn(task)}: allocation mismatch")
        if group == "framework":
            require(qn(f["function"].element) in {f"BoundaryViews::F{n:02}" for n in range(1, 9)},
                    "Framework action lacks current black-box function")
        else:
            require(any(isinstance(t, api.ActionDefinition) and qn(t).startswith("ScenarioViews::")
                        for t in task.types), "External call lacks genuine behavior")
        if task.owner in summaries:
            require(any(t.startswith(qn(scenarios[summaries.index(task.owner)]))
                        for t in targets(task)), "Summary action lacks full action reference")
    require(len(tasks) == len(allocations) == len(metadata) == 53,
            "Incomplete action responsibility coverage")

    transitions = [e for e in elements if type(e).__name__ == "TransitionUsage"
                   and e.owner in scenarios]
    require(len(transitions) == 12, "Expected twelve alternative guarded paths")
    for transition in transitions:
        links = [f for f in transition.owned_features if type(f).__name__ == "SuccessionAsUsage"]
        require(len(links) == 1, "Guarded alternative lacks native link")
        link = links[0]
        guard = " ".join(api.pprint(transition.guard_expression).split())
        require(link.name == f"[{guard}]", f"Guard label disagrees: {guard}")
        require(link.source_feature == transition.source
                and list(link.target_features) == [transition.target], "Guard endpoint mismatch")
        lower, lr = compiler.evaluate(link.multiplicity.lower_bound)
        upper, ur = compiler.evaluate(link.multiplicity.upper_bound)
        require(bool(lr) and bool(ur) and (lower, upper) == (0, 1), "Alternative must be optional")
        bindings = [f for f in transition.owned_features
                    if type(f).__name__ == "BindingConnectorAsUsage" and f.source_feature == link]
        require(len(bindings) == 1, "Guarded link lost its transition control")
        bt = list(bindings[0].target_features)
        require(len(bt) == 1 and bt[0].owner == transition and bt[0].name == "transitionLink",
                "Guarded-link binding target mismatch")
    scenario_flows = [e for e in elements if type(e).__name__ == "FlowUsage" and e.owner in scenarios]
    require(len(scenario_flows) == 28, "Incomplete typed scenario exchanges")
    def check_typed_flow(flow):
        require(flow.source_feature is not None and list(flow.target_features), "Flow lacks endpoints")
        payloads = [t for t in flow.payload_types if qn(t).startswith("BoundaryViews::")]
        require(len(payloads) == 1, f"{qn(flow)}: missing or ambiguous current payload type")
        ends = {e.name: e for e in flow.owned_features if type(e).__name__ == "FlowEnd"}
        require(set(ends) == {"source", "target"}, "Flow lacks typed source/target ends")
        for end_name, end in ends.items():
            typed = [t for f in end.owned_features for t in f.types
                     if qn(t).startswith("BoundaryViews::")]
            require(typed, f"{qn(flow)}: {end_name} lacks typed parameter")
            if end_name == "source":
                compatible = any(t.conforms(payloads[0]) for t in typed)
            else:
                compatible = any(payloads[0].conforms(t) for t in typed)
            require(compatible, f"{qn(flow)}: payload does not conform to {end_name} parameter")

    for flow in scenario_flows:
        check_typed_flow(flow)

    context = by_qn["FrameworkContext::Context"]
    interfaces = [e for e in context.owned_features if type(e).__name__ == "InterfaceUsage"]
    require({e.name for e in interfaces} == {"IF01", "IF02", "IF03", "IF04", "IF06"},
            "Wrong active interfaces, IF-05 must remain absent")
    exact_flows = [e for e in elements if type(e).__name__ == "FlowUsage" and e.owner in interfaces]
    expected_flows = {f'FrameworkContext::Context::{interface}::{name}' for interface, names in {
        'IF01': ('engineeringInputs', 'engineeringOutputs'), 'IF02': ('sourceData', 'sourceRequest'),
        'IF03': ('analysisPlan', 'analysisRequest', 'analysisResult', 'analysisStatus', 'epsResponses', 'spacecraftInputs'),
        'IF04': ('codingRequest', 'codingStatus', 'interfaceSpecification', 'softwareProduct', 'softwareResult'),
        'IF06': ('reviewFindingsDecisions', 'reviewPackage')}.items() for name in names}
    require(len(exact_flows) == 17 and {qn(f) for f in exact_flows} == expected_flows, "Incomplete typed interface exchanges")
    for flow in exact_flows:
        check_typed_flow(flow)
    forbidden = {"FrameworkDomain::TestingFacilityTechnician", "FrameworkDomain::EPSHardware",
                 "FrameworkDomain::AsIs::TestingFacility"}
    for e in elements:
        if type(e).__name__ == "PartUsage" and (qn(e).startswith("FrameworkContext::")
                                               or qn(e).startswith("FrameworkDomain::ToBe::")):
            require(not forbidden.intersection(qn(t) for t in e.types), "Physical participant leaked into future context")
    future = by_qn["FrameworkDomain::ToBe::FutureFramework"]
    require({e.name for e in future.owned_features if type(e).__name__ == "PortUsage"}
            == {"p01", "p02", "p03", "p04", "p06"}, "Wrong future framework ports")

    requirements = [e for e in elements if type(e).__name__ == "RequirementUsage"
                    and qn(e.owner) == "FrameworkRequirements"]
    require({e.name for e in requirements} == FR_IDS, "Current FR set changed or retired FR-12/FR-40 restored")
    ledger = json.loads(args.ledger.read_text())
    published = validate_report_contract(report.read_text(),
                    (report.parent / report_tables.FR_IO_SOURCE).read_text(), ledger)
    report_tables.audit_io_body(report.parent, published)
    checks = [e for e in elements if isinstance(e, api.MetadataUsage)
              and any(qn(t) == "FrameworkRequirements::PlannedRequirementCheck" for t in e.types)]
    derivations = [e for e in elements if type(e).__name__ == "ConnectionUsage"
                   and qn(e).startswith("FrameworkRequirements::derive_MR_")]
    require(len(derivations) == 169, "Incomplete MR derivations")
    parent_map = {r: set() for r in requirements}
    for d in derivations:
        # Syside resolves source/target reference subsetting to actual requirements.
        ends = list(d.owned_features)
        refs = [endpoint(e) for e in ends if e.referenced_feature is not None]
        parents = [e for e in refs if qn(e).startswith("FrameworkNeeds::MR_")]
        children = [e for e in refs if e in requirements]
        require(len(parents) == len(children) == 1, "Unresolved derivation endpoints")
        parent_map[children[0]].add(parents[0].name[-2:])
    for r in requirements:
        text = " ".join(" ".join(r.texts).split())
        row = published[r.name.replace('_', '-')]
        require(text.startswith('The framework shall ') and text == row['text'], f"{r.name}: report/model statement disagreement")
        require(parent_map[r], "Requirement has no current MR parent")
        expected_parents = {mid[-2:] for mid in row['parents']}
        require(expected_parents == parent_map[r], f"{r.name}: report/model MR disagreement")
        attached = [c for c in checks if r in c.annotated_elements]
        require(len(attached) == 1, "Requirement lacks planned method/check")
        c = fields(attached[0])
        require(set(c["methods"].split(",")) <= {"I", "A", "D", "T"} and c["checkSummary"],
                "Invalid planned verification method/check")
        ts = targets(r)
        require(any(t.startswith("ScenarioViews::SC") for t in ts), "Missing scenario requirement derivation")
        require(any(t.startswith("BoundaryViews::F") for t in ts), "Missing black-box function link")
    review_control = check_review_control(elements, by_qn, api)
    for state, needed in {
        "GuidanceControl": {"sameContext", "authorized"},
    }.items():
        s = by_qn[f"ScenarioViews::{state}"]
        gs = " ".join(api.pprint(e.guard_expression) for e in s.owned_features
                      if type(e).__name__ == "TransitionUsage" and e.guard_expression is not None)
        require(all(x in gs for x in needed), f"{state}: lost authorization/currency guards")
    for state, transition, conditions in (
        ("GuidanceControl", "apply", ("sameContext", "authorized")),
        ("GuidanceControl", "response", ("sameContext",)),
    ):
        t = by_qn[f"ScenarioViews::{state}::{transition}"]
        guard = " ".join(api.pprint(t.guard_expression).split())
        require(all(c in guard for c in conditions), f"{state}::{transition}: missing guard")
    for name in ("editCurrent", "editPending"):
        require(by_qn[f"ScenarioViews::GuidanceControl::{name}"].target.name == "stale",
                "A context edit must invalidate guidance immediately")
    require("deliverable coding is blocked" in " ".join(
        d.body for d in by_qn["ScenarioViews::SC04::'FW: block coding'"].documentation).lower(),
        "Missing unreleased-coding failure behavior")
    fr42 = by_qn["FrameworkRequirements::FR_42"]
    row42 = next(r for r in ledger["framework_requirements"] if r["id"] == "FR-42")
    require(row42["text"] == " ".join(" ".join(fr42.texts).split()),
            "V42: report/native/ledger FR-42 statement disagreement")
    v42 = by_qn["FrameworkVerification::V42"]
    objectives = [e for e in elements if isinstance(e, api.RequirementUsage)
                  and qn(e).startswith(qn(v42) + "::") and e.referenced_feature == fr42]
    require(objectives, "V42: native objective is not FR-42")
    planned = [e for e in elements if isinstance(e, api.MetadataUsage) and v42 in e.annotated_elements
               and by_qn["FrameworkVerification::PlannedProcedure"] in e.types]
    require(len(planned) == 1, "V42: missing unique planned procedure")
    native = fields(planned[0])
    for name in ("status", "executed", "observedVerdict"):
        feature = next((f for f in planned[0].owned_features if f.name == name),
                       by_qn[f"FrameworkVerification::PlannedProcedure::{name}"])
        native[name] = value(feature, planned[0])
    case42 = next(r for r in ledger["verification_cases"] if r["id"] == "V42")
    require(case42["framework_requirement_id"] == "FR-42" and row42["verification_case_ids"] == ["V42"],
            "V42: ledger requirement link disagreement")
    for name in ("subjectDescription", "configuration", "prerequisites", "procedure", "stimulus_conditions",
                 "expected_response", "criteria_comparison_basis", "retained_evidence", "status", "executed"):
        key = "subject" if name == "subjectDescription" else name
        require(native[name] == case42[key], f"V42: native/ledger {key} disagreement")
    require(native["methods"].split(",") == case42["methods"] == ["I", "T"] and
            native["status"] == "planned, not executed" and native["executed"] is False and
            native["observedVerdict"] == "none" and case42["verdict"] is None,
            "V42: procedure must remain planned with no observed verdict")
    result = {"status": "passed specification checks, not empirical V&V", "native_errors": 0, "native_warnings": 0,
                      "scenarios": 5, "summary_views": 5, "actor_allocations": len(tasks),
                      "guarded_alternatives": len(transitions), "scenario_typed_flows": len(scenario_flows),
                      "interface_typed_flows": len(exact_flows), "requirements": len(requirements),
                      "mr_derivations": len(derivations), "joined_io_rows": len(published),
                      "retired_requirement": "FR-40",
                      "review_control": review_control,
                      "V42": "report FR-42 statement and native/ledger procedure agree, planned, not executed"}
    if args.negative_cases:
        result['negative_cases'] = negative_checks(root, args.tool, config, report, args.ledger, baseline_checked=True)
        result['negative_baseline_passed'] = True
    print(json.dumps(result, indent=2))
    return 0


def negative_checks(root, tool, config, report, ledger, *, baseline_checked=False):
    require(baseline_checked, 'A passing current scenario baseline is required before mutation')
    cases = [
        ('actor-allocation', '09-scenarios.sysml', "allocate SC02::'FW: check and recommend' to framework;", "allocate SC02::'FW: check and recommend' to epsEngineer;"),
        ('typed-flow', '09-scenarios.sysml', "flow exchange1 of MissionDefinition from 'SE: define mission'.mission to 'FW: plan concepts'.mission;", "flow exchange1 of HostSoftwareProduct from 'SE: define mission'.mission to 'FW: plan concepts'.mission;"),
        ('scenario-mr', '09-scenarios.sysml', 'dependency scenario_SC03_MR03 from SC03 to FrameworkNeeds::MR_03;', 'dependency scenario_SC03_MR03 from SC03 to FrameworkNeeds::MR_01;'),
        ('uc-mr', '02-needs-context.sysml', 'dependency refine_UC02_MR02 from UC02 to MR_02;', 'dependency refine_UC02_MR02 from UC02 to MR_03;'),
        ('stale-guidance', '09-scenarios.sysml', 'accept ApplySuggestion if sameContext and authorized then current;', 'accept ApplySuggestion if authorized then current;'),
        ('edit-invalidation', '09-scenarios.sysml', 'transition editCurrent first current accept EditContext then stale;', 'transition editCurrent first current accept EditContext then current;'),
        ('review-authority', '09-scenarios.sysml',
         'transition approve first underReview accept decision : DecideReview if authorizedCurrent and not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;',
         'transition approve first underReview accept decision : DecideReview if not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;',
         'BaselineControl: review transition mismatch from underReview'),
        ('initial-accepted-disposition', '09-scenarios.sysml',
         'transition approve first underReview accept decision : DecideReview if authorizedCurrent and not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;',
         'transition approve first underReview accept decision : DecideReview if authorizedCurrent and not blocking then acceptedBaseline;',
         'BaselineControl: review transition mismatch from underReview'),
        ('renewal-accepted-disposition', '09-scenarios.sysml',
         'transition closeConditions first conditional accept decision : DecideReview if authorizedCurrent and closureComplete and not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;',
         'transition closeConditions first conditional accept decision : DecideReview if authorizedCurrent and closureComplete and not blocking then acceptedBaseline;',
         'BaselineControl: closed prior conditions override renewed conditional disposition'),
        ('blocked-renewal-path', '09-scenarios.sysml',
         '        transition blockRenewal first conditional accept decision : DecideReview if authorizedCurrent and decision.disposition == ReviewDisposition::progressionBlocked then progressionBlocked;\n', '',
         'BaselineControl: missing renewed progressionBlocked decision path'),
        ('conditional-renewal-record', '09-scenarios.sysml',
         '        transition renewConditional first conditional accept decision : DecideReview if authorizedCurrent and not blocking and decision.disposition == ReviewDisposition::conditional and conditionalRecordsComplete then conditional;\n', '',
         'BaselineControl: missing renewed conditional decision path'),
        ('closure-override-counterexample', '09-scenarios.sysml',
         'transition closeConditions first conditional accept decision : DecideReview if authorizedCurrent and closureComplete and not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;',
         'transition closeConditions first conditional accept decision : DecideReview if authorizedCurrent and closureComplete and not blocking and (decision.disposition == ReviewDisposition::accepted or closureComplete) then acceptedBaseline;',
         'BaselineControl: closed prior conditions override renewed conditional disposition'),
        ('prior-closure-evidence', '09-scenarios.sysml',
         'transition closeConditions first conditional accept decision : DecideReview if authorizedCurrent and closureComplete and not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;',
         'transition closeConditions first conditional accept decision : DecideReview if authorizedCurrent and not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;',
         'BaselineControl: review transition mismatch from conditional'),
        ('blocked-disposition-renewal', '09-scenarios.sysml',
         'transition blockRenewal first conditional accept decision : DecideReview if authorizedCurrent and decision.disposition == ReviewDisposition::progressionBlocked then progressionBlocked;',
         'transition blockRenewal first conditional accept decision : DecideReview if authorizedCurrent and blocking then progressionBlocked;',
         'BaselineControl: review transition mismatch from conditional'),
        ('independent-approval-flag', '09-scenarios.sysml',
         'transition closeConditions first conditional accept decision : DecideReview if authorizedCurrent and closureComplete and not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;',
         'attribute acceptedDecision : Boolean;\n        transition closeConditions first conditional accept decision : DecideReview if authorizedCurrent and closureComplete and not blocking and acceptedDecision then acceptedBaseline;',
         'BaselineControl: uncontrolled guard reference'),
        ('V42-procedure-agreement', '05-verification.sysml',
         ' From conditional status, submit renewed accepted, conditional and blocked decisions.', '',
         'V42: native/ledger stimulus_conditions disagreement'),
        ('physical-participant', '06-system-context.sysml', 'part def Context {', 'part def Context { ref part technician : TestingFacilityTechnician;'),
        ('retired-FR40', '03-requirements.sysml', 'package FrameworkRequirements {', 'package FrameworkRequirements { requirement FR_40 { subject framework : ToBe::FutureFramework; doc /* The framework shall complete two cases. */ }'),
    ]
    outcomes = []
    with tempfile.TemporaryDirectory(prefix='scenario-negative-') as directory:
        for case in cases:
            name, filename, old, new, *expected_reason = case
            target = Path(directory)/name
            for source in CURRENT_FILES:
                path = target/source
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root/source, path)
            path = target/filename
            text = path.read_text()
            matches = text.count(old)
            require(old != new and matches == 1, 'Negative mutation must change exactly one selector: '+name)
            path.write_text(text.replace(old,new,1))
            run = subprocess.run(['uv','run',str(Path(__file__).resolve()),'--tool',str(tool.resolve()),
                                  '--model-root',str(target),'--report',str(report.resolve()),
                                  '--config',str(config.resolve()), '--ledger',str(ledger.resolve())],
                                 capture_output=True,text=True)
            require(run.returncode == 1 and run.stderr.strip().startswith('FAIL:') and
                    'Traceback' not in run.stderr and 'Native tooling unavailable' not in run.stderr,
                    'Negative case not meaningfully rejected: '+name)
            if expected_reason:
                require('FAIL: ' + expected_reason[0] in run.stderr,
                        f'Negative case did not reach the expected semantic check: {name}: {run.stderr[-350:]}')
            outcomes.append({'case':name,'rejected':True,'reason':run.stderr[-350:].strip(),
                             'mutation_matches': matches, 'native_check_executed': True,
                             'native_validation_passed': True if expected_reason else None})
    return outcomes


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, ValueError, KeyError, AttributeError, OSError, StopIteration, RuntimeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
