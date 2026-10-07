#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = []
# ///
"""Check the current logical specification through licensed Syside semantics.

This checks planned allocations, typed information, actual guarded behavior and
report/ledger agreement. It executes no framework or EPS product V&V. Run the
whole model check separately as well. All current dependencies are included.

Run: uv run check_logical_responsibilities.py --negative-cases
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

FILES = tuple(f'{n}.sysml' for n in (
    '00-domain', '01-concerns', '02-needs-context', '03-requirements',
    '04-logical', '05-verification', '06-system-context', '07-report-views',
    '08-physical-vocabulary', '09-scenarios', '10-interface-views',
    '11-logical-responsibilities')) + tuple(
    f'candidates/{n}.sysml' for n in ('comet', 'custom', 'git-yaml', 'nanospace', 'valispace'))
EXPECTED = {
    "L01": {8: "checkTransfer", 37: "makeViews"},
    "L02": {2: "checkDraft", 3: "recommend", 29: "dispose", 39: "recommend", 41: "acknowledge"},
    "L03": {1: "retainRequirements", 4: "traceLinks", 17: "deriveAllocate"},
    "L04": {12: "budgetSize", 13: "budgetSize", 14: "compareDesigns", 15: "defineDesign",
            20: "budgetSize", 25: "defineDesign", 33: "defineInterfaces",
            34: "defineInterfaces", 35: "defineInterfaces"},
    "L05": {10: "replay", 16: "planAnalysis", 18: "planAnalysis", 19: "planMIL",
            23: "planAnalysis", 24: "compareMILSil", 26: "planAnalysis",
            27: "planAnalysis", 36: "coordinateCoding"},
    "L06": {21: "assessModel", 22: "proposeCalibration", 31: "assessModel", 32: "assessModel"},
    "L07": {11: "assessProduct", 28: "planAssessment", 38: "prepareReview", 42: "recordReview"},
    "L08": {5: "invalidate", 6: "successor", 7: "retrieveBaseline", 9: "preserveRun", 30: "invalidate"},
}
PORTS = {8: {1, 2, 3, 4, 6}, 9: {3, 4}, 10: {3, 4}, 11: {1, 6}, 18: {3}, 19: {3},
         21: {2, 3}, 22: {1, 2}, 23: {3, 4}, 24: {3, 4}, 27: {3}, 31: {2, 3, 4},
         32: {2, 3, 4}, 36: {4}, 38: {1, 6}, 42: {6}, 3: {1, 2}}
# Independent control invariants. These resolve to native TransitionUsage guards
# and their actual targets, rather than dependencies to prose guard descriptions.
GUARDS = {
    "AssistanceRealization": {
        "admitInput": ("receive.compatible", "capture"),
        "admitReply": ("checkReply.sameContext", "present"),
        "admitDisposition": ("dispose.authorized and checkApplication.sameContext", "applyCorrection"),
        "applyAuthorized": ("dispose.applyRequested", "derive"),
        "validRequirements": ("validate.resolved", "retainValidation"),
    },
    "DesignRealization": {
        "admitInput": ("receive.compatible", "configure"),
        "admitResult": ("receiveResult.compatible", "preserve"),
        "admitModel": ("checkCurrent.current and credibility.numericallyValid and credibility.applicable", "assess"),
        "admitCriteria": ("assess.claimSupported", "compare"),
        "admitSelection": ("compare.feasible and select.accepted and checkSelection.authorizedCurrent", "retainSelection"),
    },
    "SoftwareRealization": {
        "admitInput": ("receive.compatible", "interfaces"),
        "admitMIL": ("receiveMIL.compatible", "preserveMIL"),
        "authorizeCoding": ("checkRelease.authorizedDetailedDesign and checkRelease.currentDesign and checkRelease.blockersClear and interfaces.profileCompatible", "coordinate"),
        "admitSIL": ("receiveSIL.compatible", "preserveSIL"),
        "admitProducts": ("checkCurrent.current and credibility.numericallyValid and credibility.applicable and assess.claimSupported", "present"),
        "admitApproval": ("checkProducts.authorizedCurrent", "retainProducts"),
    },
    "ChangeReviewRealization": {
        "admitInput": ("receive.compatible", "invalidate"),
        "proposedChange": ("invalidate.hasChange", "changeDecision"),
        "admitChange": ("checkChange.authorizedCurrent and checkChange.acceptedChange", "successor"),
        "repeatAffected": ("checkChange.reassessmentRequired", "planRepeat"),
        "admitResult": ("receiveResult.compatible", "preserve"),
        "preparePackage": ("prepare.entranceComplete", "reviewers"),
        "admitReviewDecision": ("checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete)", "record"),
    },
    "ReplayRealization": {
        "admitReplay": ("prepare.dependenciesComplete and prepare.rulesFixed", "execute"),
        "admitResult": ("receive.compatible", "preserve"),
    },
    "CalibrationRealization": {
        "admitData": ("receive.compatible", "checkData"),
        "admitCalibration": ("checkData.dataUsable and checkData.independentSeparation", "propose"),
        "admitCalibrationChange": ("checkChange.authorizedCurrent and checkChange.acceptedChange", "successor"),
        "admitReassessedResult": ("receiveResult.compatible", "preserve"),
    },
}


GUARDS["ConceptRealization"] = dict(GUARDS["DesignRealization"])
GUARDS["ConceptRealization"]["admitInput"] = ("receive.compatible", "makeConfiguration")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def qn(element):
    return str(element.qualified_name) if element.qualified_name else ""


def compact(text):
    return re.sub(r"\s+", "", text)


def check(tool, root, ledger_path, report_path):
    ledger = json.loads(ledger_path.read_text())
    result = tool.validate([root / name for name in FILES], [], warnings_as_errors=True,
                           config=root / "logical-responsibilities.toml")
    model, api = tool.require_semantic_model(result)
    elements = list(model.nodes(api.Element, include_subtypes=True))
    by = {qn(e): e for e in elements if e.qualified_name}
    compiler = api.Compiler()

    def values(annotation):
        out = {}
        for feature in annotation.owned_features:
            value, diagnostics = compiler.evaluate_feature(feature, annotation)
            require(bool(diagnostics), f"Cannot evaluate {feature.name}")
            out[feature.name] = value
        return out

    def annotations(element, typename):
        return [e for e in elements if isinstance(e, api.MetadataUsage)
                and element in e.annotated_elements and any(qn(t) == typename for t in e.types)]

    def dependencies(element):
        return {t for e in elements if isinstance(e, api.Dependency) and element in e.sources
                for t in e.targets}

    def chain(feature):
        return list(feature.chaining_features) or [feature]

    logical = by["FrameworkLogical::LogicalFramework"]
    require(logical.conforms(by["FrameworkDomain::ToBe::FutureFramework"]),
            "Logical design must specialize the current black box")
    parts = {p.name: p for p in logical.owned_features if type(p).__name__ == "PartUsage"}
    require(set(parts) == set(EXPECTED), "Wrong current logical component set")
    require({r.name for r in elements if type(r).__name__ == "RequirementUsage"
             and qn(r.owner) == "FrameworkRequirements"}
            == {f"FR_{n:02}" for n in range(1, 40)} | {"FR_41", "FR_42"},
            "Current FR set changed or retired FR-40 restored")
    require(not any(type(e).__name__ == "SatisfyRequirementUsage" and
                    qn(e).startswith(("FrameworkLogical::", "LogicalRealization::"))
                    for e in elements), "Planned allocations must not assert satisfaction")
    forbidden = {"FrameworkDomain::TestingFacilityTechnician", "FrameworkDomain::EPSHardware",
                 "FrameworkDomain::AsIs::TestingFacility"}
    require(not any(type(e).__name__ == "PartUsage" and
                    qn(e).startswith(("FrameworkLogical::", "LogicalRealization::")) and
                    forbidden.intersection(qn(t) for t in e.types) for e in elements),
            "Physical participant or execution obligation leaked into logical design")

    component_rows = {row["id"]: row for row in ledger["components"]}
    require(set(component_rows) == set(parts), "Ledger component coverage")
    for cid, part in parts.items():
        row = component_rows[cid]
        require(row["native_part"] == qn(part), "Ledger component path")
        definition = by[row["native_type"]]
        require(definition in part.types, "Ledger component definition")
        source = annotations(definition, "FrameworkDomain::SourceRecord")
        require(len(source) == 1, "Component lacks source rationale")
        fields = values(source[0])
        require(fields["sourceText"] == row["derivation"] and fields["citationRecord"] == row["sources"],
                "Ledger/native source rationale disagreement")
        expected_targets = {"BoundaryViews::" + f for f in row["functions"]} | {
            "ScenarioViews::" + s for s in row["scenarios"]} | {
            "FrameworkNeeds::" + m.replace("-", "_") for m in row["moes"]}
        require(expected_targets <= {qn(t) for t in dependencies(definition)},
                "Unresolved component function/scenario/MOE derivation")
        require(row["category"] in {"external interface", "application", "infrastructure"},
                "Missing OOSEM component distinction")
    require(component_rows["L01"]["category"] == "external interface" and
            component_rows["L08"]["category"] == "infrastructure", "Boundary/infrastructure ownership")

    bindings = [e for e in logical.owned_features if type(e).__name__ == "BindingConnectorAsUsage"]
    require(len(bindings) == 5, "Five external port delegations are required")
    for binding in bindings:
        target = chain(list(binding.target_features)[0])
        require(len(target) == 2 and target[0] == parts["L01"]
                and target[1].name in {"p01", "p02", "p03", "p04", "p06"},
                "External port must delegate to the exchange component")
        source_types = {qn(t) for t in binding.source_feature.types if qn(t).startswith("BoundaryViews::")}
        target_types = {qn(t) for t in target[-1].types if qn(t).startswith("BoundaryViews::")}
        require(len(source_types) == 1 and source_types == target_types, "External delegation type mismatch")

    allocations = [e for e in elements if type(e).__name__ == "AllocationUsage"]
    primary = [a for a in allocations if annotations(a, "FrameworkDomain::primaryResponsibility")]
    support = [a for a in allocations if annotations(a, "FrameworkDomain::supportingResponsibility")]
    require(len(primary) == 41, "Every current FR needs one primary owner")
    rows = {r["FR"]: r for r in ledger["allocations"]}
    require(set(rows) == {f"FR-{n:02}" for group in EXPECTED.values() for n in group}, "Ledger FR coverage")
    owners = {}
    for allocation in primary:
        r = allocation.source_feature
        require(type(r).__name__ == "RequirementUsage", "Primary source is not a requirement")
        number = int(r.name[-2:])
        target = chain(list(allocation.target_features)[0])
        require(len(target) == 2 and qn(target[0]) == "FrameworkLogical::logical"
                and target[-1] in parts.values(), "Primary allocation is not an actual logical part path")
        cid = target[-1].name
        require(number in EXPECTED[cid] and r not in owners, "Wrong or duplicate semantic FR owner")
        owners[r] = cid
        row = rows[f"FR-{number:02}"]
        require(row["primary"] == cid, "Ledger/native primary mismatch")
        require(row["verification"]["status"] == "planned, not executed", "False verification outcome")
        attached = annotations(allocation, "FrameworkLogical::LogicalAllocation")
        require(len(attached) == 1, "Allocation lacks rationale/planned check/operation")
        fields = values(attached[0])
        operation = fields["operation"].element
        definition = by[component_rows[cid]["native_type"]]
        require(operation.owner == definition and operation.name == EXPECTED[cid][number]
                and qn(operation) == row["operation"] and operation in dependencies(r),
                "FR operation does not belong to its allocated component")
        planned = annotations(r, "FrameworkRequirements::PlannedRequirementCheck")
        require(len(planned) == 1, "FR lacks current planned verification need")
        plan = values(planned[0])
        require((plan["methods"], plan["checkSummary"]) ==
                (row["verification"]["methods"], row["verification"]["need"]),
                "Ledger changed approved planned verification needs")
        require(fields["rationale"] == row["rationale"] and fields["plannedCheck"] ==
                plan["methods"] + ": " + plan["checkSummary"], "Allocation rationale/check mismatch")
        helpers = set()
        for a in support:
            if a.source_feature == r:
                end = chain(list(a.target_features)[0])
                require(len(end) == 2 and end[-1] in parts.values(), "Unresolved supporting owner")
                helpers.add(end[-1].name)
        require(helpers == set(row["support"]) and cid not in helpers, "Supporting allocation mismatch")
        ports = {f"FrameworkLogical::Exchange::p{n:02}" for n in PORTS.get(number, {1})}
        actual_ports = {qn(t) for t in dependencies(r) if type(t).__name__ == "PortUsage"}
        require(actual_ports == set(row["interfaces"]) == ports, "FR interface allocation mismatch")
        behaviors = {t for t in dependencies(r) if type(t).__name__ == "PerformActionUsage"
                     and qn(t).startswith("LogicalRealization::")}
        require(behaviors and {qn(t) for t in behaviors} == set(row["behaviors"]),
                "FR lacks its exact realization actions")
        for behavior in behaviors:
            meta = annotations(behavior, "LogicalRealization::LogicalStep")
            require(len(meta) == 1, "Behavior has no resolved component/operation")
            assignment = values(meta[0])
            require(assignment["component"].element == parts[cid]
                    and assignment["operation"].element == operation, "FR behavior ownership mismatch")

    # Resolve all behavior owners and calls, including external authority/tool roles.
    realizations = [by["LogicalRealization::" + name] for name in GUARDS]
    require({r["native"] for r in ledger["realizations"]} == {qn(r) for r in realizations},
            "Logical realization coverage")
    tasks = [e for e in elements if type(e).__name__ == "PerformActionUsage" and e.owner in realizations]
    allowed = {"systemsEngineer", "epsEngineer", "analysisTools", "hostToolchain", "reviewers", "reviewAuthority"}
    for task in tasks:
        internal = annotations(task, "LogicalRealization::LogicalStep")
        external = annotations(task, "LogicalRealization::ExternalStep")
        require(len(internal) + len(external) == 1, "Unowned or multiply owned logical task")
        tagged = values((internal or external)[0])
        # Full dependencies also allocate the same behavior to each candidate.
        # Check the logical assignment at its own level. Physical assignments
        # are checked independently by check_physical_allocations.py.
        assigned = [a for a in allocations if a.source_feature == task
                    and qn(a.owner) == "LogicalRealization"]
        require(len(assigned) == 1, "Task needs exactly one real logical allocation")
        if internal:
            component, operation = tagged["component"].element, tagged["operation"].element
            end = chain(list(assigned[0].target_features)[0])
            require(len(end) == 2 and end[-1] == component and operation.owner in component.types,
                    "Task allocation, parent operation and component disagree")
            require(set(task.types) == set(operation.types), "Task invokes a different operation type")
        else:
            actor = tagged["performer"].element
            require(qn(actor).startswith("ScenarioViews::") and actor.name in allowed
                    and list(assigned[0].target_features) == [actor], "External authority/tool allocation mismatch")
    for flow_name, scenario, actors in (
        ("ConceptRealization", "SC01", {"submit": (1, "systemsEngineer"), "execute": (3, "analysisTools"), "select": (5, "systemsEngineer")}),
        ("DesignRealization", "SC03", {"submit": (1, "epsEngineer"), "execute": (3, "analysisTools"), "select": (5, "epsEngineer")}),
        ("SoftwareRealization", "SC04", {"submit": (1, "epsEngineer"), "executeMIL": (3, "analysisTools"), "codeBuildSil": (5, "hostToolchain"), "approve": (7, "epsEngineer")}),
    ):
        for name, (number, actor_name) in actors.items():
            task = by[f"LogicalRealization::{flow_name}::{name}"]
            require(by[f"ScenarioViews::{scenario}External{number}"] in task.types
                    and values(annotations(task, "LogicalRealization::ExternalStep")[0])["performer"].element
                    == by["ScenarioViews::" + actor_name], "Logical realization changed approved scenario actor/operation authority")
    for row in ledger["realizations"]:
        require({"ScenarioViews::" + s for s in row["scenarios"]} <=
                {qn(t) for t in dependencies(by[row["native"]])}, "Missing scenario realization derivation")

    # Check typed port-to-port exchanges, including hidden overview detail links.
    interfaces = {e.name: e for e in logical.owned_features if type(e).__name__ == "InterfaceUsage"}
    require(set(interfaces) == {row["name"] for row in ledger["exchanges"]}, "Exchange coverage")
    for row in ledger["exchanges"]:
        interface = interfaces[row["name"]]
        require(qn(interface) == row["native"], "Exchange native path mismatch")
        ends = [chain(interface.source_feature), chain(list(interface.target_features)[0])]
        for path, end in zip((row["source"], row["target"]), ends):
            cid, name = path.split(".")
            require(len(end) == 2 and end[0] == parts[cid] and end[1].name == name,
                    "Exchange component/port endpoint mismatch")
            require(by[row["port_type"]] in end[-1].types, "Exchange port type mismatch")
        port = by[row["port_type"]]
        payload = next(f for f in port.owned_features if f.name == "work")
        require(any(t.name == row["payload"] for t in payload.types), "Exchange payload mismatch")
    for name, fields in ledger["item_types"].items():
        item = by["FrameworkLogical::" + name]
        for field, typename in fields.items():
            feature = next(f for f in item.owned_features if f.name == field.split()[-1])
            type_name = typename.split()[0]
            require(any(t.name == type_name for t in feature.types), "Logical record field type mismatch")

    typed_flows = [e for e in elements if type(e).__name__ == "FlowUsage" and e.owner in realizations]
    for flow in typed_flows:
        payloads = [t for t in flow.payload_types if qn(t).startswith(
            ("FrameworkLogical::", "BoundaryViews::", "FrameworkDomain::", "ScalarValues::"))]
        require(len(payloads) == 1, "Missing/ambiguous typed realization payload")
        ends = {e.name: e for e in flow.owned_features if type(e).__name__ == "FlowEnd"}
        require(set(ends) == {"source", "target"}, "Flow lacks resolved ends")
        for name, end in ends.items():
            types = [t for feature in end.owned_features for t in feature.types
                     if qn(t).startswith(("FrameworkLogical::", "BoundaryViews::", "FrameworkDomain::", "ScalarValues::"))]
            types = [t for t in types if not any(other != t and other.conforms(t)
                     and not t.conforms(other) for other in types)]
            compatible = any(t.conforms(payloads[0]) if name == "source" else
                             payloads[0].conforms(t) for t in types)
            require(compatible, f"{qn(flow)}: payload/parameter conformance mismatch")

    # Every positive gate has resolved Boolean result features and no unguarded
    # succession into its protected action. Alternative guards must be present.
    transitions = [e for e in elements if type(e).__name__ == "TransitionUsage" and e.owner in realizations]
    def references(expr):
        if type(expr).__name__ == "FeatureChainExpression":
            operands = list(expr.operands)
            require(len(operands) == 1 and type(operands[0]).__name__ == "FeatureReferenceExpression",
                    "Guard outcome must reference a resolved operation result")
            yield [operands[0].referent, expr.target_feature]
        else:
            for operand in expr.operands:
                yield from references(operand)
    for flow_name, specs in GUARDS.items():
        flow = by["LogicalRealization::" + flow_name]
        for gate, (expected, destination) in specs.items():
            transition = by[qn(flow) + "::" + gate]
            require(compact(api.pprint(transition.guard_expression)) == compact(expected),
                    f"{flow_name}::{gate}: lost required guard")
            require(transition.target == by[qn(flow) + "::" + destination], "Guard controls wrong action")
            for ref in references(transition.guard_expression):
                require(len(ref) == 2 and ref[0].owner == flow and
                        type(ref[0]).__name__ == "PerformActionUsage" and
                        ref[-1].owner in ref[0].types and any(qn(t) == "ScalarValues::Boolean" for t in ref[-1].types),
                        "Guard is not a resolved outcome of an owned logical/external operation")
            require(not any(type(e).__name__ == "SuccessionAsUsage" and e.owner == flow
                            and transition.target in e.target_features for e in elements),
                    "Unguarded path bypasses a required control gate")
            alternatives = [t for t in transitions if t.owner == flow and t.source == transition.source
                            and t != transition and t.guard_expression is not None]
            require(alternatives, "Control gate lost its alternative response")
    software = by["LogicalRealization::SoftwareRealization"]
    release = by[qn(software) + "::authorizeCoding"]
    edges = [(e.source_feature, target) for e in elements
             if type(e).__name__ == "SuccessionAsUsage" and e.owner == software
             for target in e.target_features]
    edges += [(t.source, t.target) for t in transitions if t.owner == software and t != release]
    reachable = {source for source, _ in edges if source.name == "start"}
    require(reachable, "Software realization has no native start")
    changed = True
    while changed:
        updated = reachable | {target for source, target in edges if source in reachable}
        changed, reachable = updated != reachable, updated
    require(by[qn(software) + "::codeBuildSil"] not in reachable,
            "External host work bypasses the detailed-design release gate")
    assistance = by["LogicalRealization::AssistanceRealization"]
    for source, target in (("capture", "invalidateOnEdit"), ("invalidateOnEdit", "acknowledge")):
        a, b = by[qn(assistance) + "::" + source], by[qn(assistance) + "::" + target]
        require(any(type(e).__name__ == "SuccessionAsUsage" and e.owner == assistance
                    and e.source_feature == a and list(e.target_features) == [b] for e in elements),
                "New edits must immediately invalidate old work before assistance starts")
    # Component state ownership preserves the approved pending/current/stale and
    # prepared/accepted/conditional/blocked semantics, rather than prose-only links.
    for cid, name, state in (("L08", "assistanceCurrency", "GuidanceControl"),
                             ("L07", "reviewState", "BaselineControl")):
        definition = by[component_rows[cid]["native_type"]]
        owned = next(e for e in definition.owned_features if e.name == name)
        require(by["ScenarioViews::" + state] in owned.types, "Component state ownership missing")
        mapping = by["FrameworkLogical::" + ("guidanceControlOwner" if cid == "L08" else "baselineControlOwner")]
        source, target = chain(mapping.source_feature), chain(list(mapping.target_features)[0])
        require(len(source) == 2 and source[-1].name == ("guidanceControl" if cid == "L08" else "baselineControl")
                and len(target) == 3 and target[-2] == parts[cid] and target[-1] == owned,
                "Black-box state is not allocated to the responsible component state")
    for edit in ("editCurrent", "editPending"):
        require(by["ScenarioViews::GuidanceControl::" + edit].target.name == "stale",
                "Edit must invalidate current and pending assistance")
    for name, fragments in (("apply", ("sameContext", "authorized")), ("response", ("sameContext",))):
        guard = api.pprint(by["ScenarioViews::GuidanceControl::" + name].guard_expression)
        require(all(x in guard for x in fragments), "Shared assistance state lost authority/currency")

    prose = report_path.read_text()
    for cid, expected in EXPECTED.items():
        row = re.search(rf"^{cid} & .*? & ([\d, -]+) \\\\", prose, re.M)
        require(row is not None, "Report responsibility summary missing")
        numbers = set()
        for term in row[1].split(", "):
            bounds = [int(x) for x in term.split("--")]
            numbers.update(range(bounds[0], bounds[-1] + 1))
        require(numbers == set(expected), "Report/native primary FR summary disagreement")
        require(set(component_rows[cid]["primary_FR"]) == {f"FR-{n:02}" for n in expected},
                "Ledger component FR summary disagreement")
    return {"status": "passed", "native_errors": 0, "native_warnings": 0,
            "components": len(parts), "current_FRs": len(primary), "supporting_allocations": len(support),
            "allocated_actions": len(tasks), "guarded_alternatives": len(transitions),
            "typed_realization_flows": len(typed_flows), "typed_internal_exchanges": len(interfaces),
            "report_and_ledger_match": True, "verification": "planned only"}


def negative_checks(tool, root, ledger, report):
    cases = [
        ("wrong_primary_owner", "04-logical.sysml",
         "responsibility_FR_02_L02 allocate FrameworkRequirements::FR_02 to logical.L02 {",
         "responsibility_FR_02_L02 allocate FrameworkRequirements::FR_02 to logical.L03 {"),
        ("wrong_action_owner", "11-logical-responsibilities.sysml",
         "allocate AssistanceRealization::checkDraft to logical.L02;",
         "allocate AssistanceRealization::checkDraft to logical.L03;"),
        ("wrong_FR_operation", "04-logical.sysml", "operation_FR02 from FrameworkRequirements::FR_02 to Assistance::checkDraft;",
         "operation_FR02 from FrameworkRequirements::FR_02 to Requirements::deriveAllocate;"),
        ("wrong_payload", "11-logical-responsibilities.sysml", "of AssistanceWork from acknowledge.work to checkDraft.work;",
         "of DesignStudy from acknowledge.work to checkDraft.work;"),
        ("wrong_host_interface", "04-logical.sysml", "interface_FR36_04 from FrameworkRequirements::FR_36 to Exchange::p04;",
         "interface_FR36_04 from FrameworkRequirements::FR_36 to Exchange::p03;"),
        ("edit_invalidation_removed", "11-logical-responsibilities.sysml", "first capture then invalidateOnEdit;", "first capture then acknowledge;"),
        ("late_response_current", "11-logical-responsibilities.sysml", "if checkReply.sameContext then present;", "if true then present;"),
        ("unauthorized_suggestion", "11-logical-responsibilities.sysml", "if dispose.authorized and checkApplication.sameContext then applyCorrection;",
         "if checkApplication.sameContext then applyCorrection;"),
        ("stale_design_coding", "11-logical-responsibilities.sysml", "checkRelease.authorizedDetailedDesign and checkRelease.currentDesign and checkRelease.blockersClear and interfaces.profileCompatible then coordinate;",
         "checkRelease.authorizedDetailedDesign and checkRelease.blockersClear and interfaces.profileCompatible then coordinate;"),
        ("stale_result_claim", "11-logical-responsibilities.sysml", "checkCurrent.current and credibility.numericallyValid and credibility.applicable then assess;",
         "credibility.numericallyValid and credibility.applicable then assess;"),
        ("unauthorized_review", "11-logical-responsibilities.sysml", "if checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete) then record;",
         "if checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete) then record;"),
        ("inconsistent_blocking_review", "11-logical-responsibilities.sysml", "if checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete) then record;",
         "if checkDecision.authorized and checkDecision.current and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete) then record;"),
        ("incomplete_conditional_review", "11-logical-responsibilities.sysml", "if checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete) then record;",
         "if checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent then record;"),
        ("unfixed_replay_rules", "11-logical-responsibilities.sysml", "if prepare.dependenciesComplete and prepare.rulesFixed then execute;",
         "if prepare.dependenciesComplete then execute;"),
        ("calibration_as_validation", "11-logical-responsibilities.sysml", "if checkData.dataUsable and checkData.independentSeparation then propose;",
         "if checkData.dataUsable then propose;"),
        ("unauthorized_calibration_update", "11-logical-responsibilities.sysml",
         "succession admitCalibrationChange first authorizedChange if checkChange.authorizedCurrent and checkChange.acceptedChange then successor;",
         "succession admitCalibrationChange first authorizedChange if checkChange.acceptedChange then successor;"),
        ("physical_participant", "04-logical.sysml", "part def LogicalFramework :> ToBe::FutureFramework {",

         "part def LogicalFramework :> ToBe::FutureFramework {\n        part L09 : TestingFacilityTechnician;"),
        ("restored_FR40", "03-requirements.sysml", "requirement <'FR-42'> FR_42 {",
         "requirement FR_40 { subject framework : ToBe::FutureFramework; doc /* Obsolete evaluation obligation. */ }\n    requirement <'FR-42'> FR_42 {"),
        ("external_host_bypass", "11-logical-responsibilities.sysml", "first checkRelease then codingRelease;",
         "first checkRelease then codingRelease;\n        first checkRelease then codeBuildSil;"),
        ("unguarded_coding_bypass", "11-logical-responsibilities.sysml", "first checkRelease then codingRelease;",

         "first checkRelease then codingRelease;\n        first checkRelease then coordinate;"),
    ]
    outcomes = []
    with tempfile.TemporaryDirectory(prefix="logical-negative-") as directory:
        base = Path(directory)
        for name, filename, old, new in cases:
            case = base / name
            case.mkdir()
            for source in FILES + ("logical-responsibilities.toml",):
                (case / source).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / source, case / source)
            path = case / filename
            text = path.read_text()
            begin, end = 0, len(text)
            if name == "stale_result_claim":
                begin = text.index("    action def DesignRealization {")
                end = text.index("    action def ConceptRealization {")
            fragment = text[begin:end]
            require(fragment.count(old) == 1, f"Negative test no longer precise: {name}")
            path.write_text(text[:begin] + fragment.replace(old, new) + text[end:])
            try:
                check(tool, case, ledger, report)
            except (ValueError, KeyError, AttributeError, RuntimeError) as error:
                outcomes.append({"case": name, "rejected": True, "reason": str(error)[:220]})
            else:
                raise ValueError(f"Negative case accepted: {name}")
        false_ledger = json.loads(ledger.read_text())
        false_ledger["allocations"][0]["verification"]["status"] = "executed, passed"
        path = base / "false-verification.json"
        path.write_text(json.dumps(false_ledger))
        try:
            check(tool, root, path, report)
        except ValueError as error:
            outcomes.append({"case": "false_verification_outcome", "rejected": True, "reason": str(error)})
        else:
            raise ValueError("Negative case accepted: false_verification_outcome")
    return outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", type=Path, default=Path("/Users/antho/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py"))
    parser.add_argument("--model-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--ledger", type=Path, default=Path(__file__).resolve().parent.parent / "traceability/logical-architecture.json")
    parser.add_argument("--report", type=Path, default=Path(__file__).resolve().parent.parent / "logical.tex")
    parser.add_argument("--negative-cases", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("logical_native_tool", args.tool.resolve())
    require(spec is not None and spec.loader is not None, "Cannot load native wrapper")
    tool = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = tool
    spec.loader.exec_module(tool)
    result = check(tool, args.model_root, args.ledger, args.report)
    if args.negative_cases:
        result["negative_cases"] = negative_checks(tool, args.model_root, args.ledger, args.report)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, AttributeError, RuntimeError, OSError, StopIteration) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
