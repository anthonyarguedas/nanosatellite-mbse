#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = []
# ///
"""Audit six logical responsibilities using real licensed Syside semantics.

--source-only checks the final report contract and the seven-file native source
boundary. --core-only checks the nine-file logical boundary independently of
physical candidates. A pending native ledger never counts as an architecture
pass. This checks planned design consistency, not executed framework/EPS V&V.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import tomllib

SOURCE_FILES = tuple(f"{n}.sysml" for n in (
    "00-domain", "01-concerns", "02-needs-context", "03-requirements",
    "06-system-context", "09-scenarios", "10-interface-views"))
CORE_FILES = SOURCE_FILES + ("04-logical.sysml", "11-logical-responsibilities.sysml")
FILES = CORE_FILES + ("05-verification.sysml", "07-report-views.sysml", "08-physical-vocabulary.sysml") + tuple(
    f"candidates/{n}.sysml" for n in ("comet", "custom", "git-yaml", "nanospace", "valispace"))
GROUPS = {
    "L01": ("Requirements and guidance", "RequirementsAssistance", (1, 2, 3, 4, 17, 29, 39, 41)),
    "L02": ("Mission and EPS design", "MissionDesign", (13, 14, 15, 20, 25, 33, 35)),
    "L03": ("Simulation and software integration", "SimulationIntegration", (10, 16, 18, 19, 23, 24, 26, 27, 34, 36)),
    "L04": ("Model credibility", "ModelCredibility", (21, 22, 31, 32)),
    "L05": ("Evidence and technical review", "EvidenceReview", (11, 28, 37, 38, 42)),
    "L06": ("Configuration and controlled exchange", "ConfigurationExchange", (5, 6, 7, 8, 9, 30)),
}
RETIRED = {"FR-12", "FR-40"}
# Independent invariants, rather than acceptance conditions invented by a ledger.
SAFETY_FAMILIES = {
    "compatibility_before_registration", "immediate_context_invalidation",
    "latest_context_before_presentation", "authorized_current_requested_application",
    "authorized_current_successor", "exact_detailed_design_release_before_build",
    "raw_missing_invalid_inactive_samples", "independent_calibration_assessment",
    "critical_gaps_block_claims", "authorized_current_consistent_review",
    "renewed_authorized_condition_closure", "replay_dependencies_and_fixed_rules",
    "all_execution_statuses_optional_numerical_payloads",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def qn(element):
    return str(element.qualified_name) if element is not None and element.qualified_name else ""


def compact(text):
    return re.sub(r"\s+", "", text)


def unique_rows(rows, key, label):
    counts = Counter(row[key] for row in rows)
    require(all(n == 1 for n in counts.values()), f"Duplicate {label}")
    return {row[key]: row for row in rows}


def expand_numbers(cell):
    numbers = []
    for term in cell.strip().split(","):
        term = term.strip()
        require(bool(re.fullmatch(r"\d{2}(?:--\d{2})?", term)), f"Invalid number list: {cell}")
        bounds = list(map(int, term.split("--")))
        require(bounds[0] <= bounds[-1], "Reversed range")
        numbers.extend(range(bounds[0], bounds[-1] + 1))
    require(len(numbers) == len(set(numbers)), "Duplicate number in row")
    return numbers


def parse_requirements(text):
    # This parses TeX only. Native models are always parsed by Syside.
    pattern = r"^FR-(\d{2}) & (.*?)\\par \\textit\{Inputs:\} (.*?)\\par \\textit\{Outputs:\} (.*?) & ([\d, -]+) \\\\"
    rows = [{"FR": f"FR-{m[1]}", "statement": m[2], "inputs_verbatim": m[3],
             "outputs_verbatim": m[4], "parents": [f"MR-{n:02}" for n in expand_numbers(m[5])]}
            for m in re.finditer(pattern, text, re.M)]
    require(rows, "No report requirement rows")
    return unique_rows(rows, "FR", "report FR")


def parse_logical_table(text):
    # Column 1 is name plus ID. Column 2 is FRs. Column 3 is interfaces.
    pattern = r"^(L\d{2}) ([^&\n]+) & ([\d, -]+) & (.+?) \\\\"
    rows = [{"id": m[1], "name": m[2].strip(), "FR": [f"FR-{n:02}" for n in expand_numbers(m[3])],
             "interfaces": m[4]} for m in re.finditer(pattern, text, re.M)]
    return unique_rows(rows, "id", "logical table component")


def expected_union(allocations, cid, direction):
    fields = {}
    for row in allocations:
        if row["primary"] == cid:
            for field in row[direction]:
                require(isinstance(field, str) and field, "Empty/non-string IO field")
                fields.setdefault(field, set()).add(row["FR"])
    return fields


def validate_source_contract(ledger, requirements_text, logical_text):
    source = parse_requirements(requirements_text)
    active = {f"FR-{n:02}" for _, _, group in GROUPS.values() for n in group}
    require(set(source) == active and not RETIRED.intersection(source), "Missing or retired report FR")
    allocations = unique_rows(ledger["allocations"], "FR", "allocation")
    require(set(allocations) == set(source), "Missing or retired allocation")
    contract = unique_rows(ledger["source_contract"]["entries"], "FR", "source contract FR")
    require(set(contract) == set(source), "Source contract coverage")
    components = unique_rows(ledger["components"], "id", "component")
    require(set(components) == set(GROUPS), "Wrong logical component set")
    table = parse_logical_table(logical_text)
    require(set(table) == set(GROUPS), "Missing/obsolete logical table rows")
    counts = Counter(fr for row in table.values() for fr in row["FR"])
    require(set(counts) == set(source) and all(n == 1 for n in counts.values()), "Missing/duplicate/retired table allocation")
    for cid, (name, definition, group) in GROUPS.items():
        expected = {f"FR-{n:02}" for n in group}
        component = components[cid]
        require(component["name"] == table[cid]["name"] == name, "Logical name disagreement")
        require(len(component["primary_FR"]) == len(set(component["primary_FR"])) and
                set(table[cid]["FR"]) == set(component["primary_FR"]) == expected,
                "Logical table/ledger primary mismatch")
        require(component["native_part"] == f"FrameworkLogical::LogicalFramework::{cid}" and
                component["native_type"] == f"FrameworkLogical::{definition}", "Unapproved public export")
        for fr in expected:
            require(allocations[fr]["primary"] == cid, "Wrong primary allocation")
        for direction in ("inputs", "outputs"):
            union = unique_rows(component["io_union"][direction], "field", "union field")
            expected_fields = expected_union(ledger["allocations"], cid, direction)
            require(set(union) == set(expected_fields), "IO union mismatch")
            for field, provenance in expected_fields.items():
                refs = union[field]["provenance"]
                require(len(refs) == len(set(refs)) and set(refs) == provenance, "IO union provenance mismatch")
    for fr, row in allocations.items():
        for direction in ("inputs", "outputs"):
            require(row[direction] and len(row[direction]) == len(set(row[direction])), "Missing/duplicate per-FR IO field")
        for key in ("statement", "inputs_verbatim", "outputs_verbatim", "parents"):
            require(row[key] == contract[fr][key] == source[fr][key], f"Stale final FR contract: {fr} {key}")
        for key in ("inputs", "outputs", "verification", "native_mop"):
            require(row[key] == contract[fr][key], f"Changed final source contract: {fr} {key}")
        require(row["verification"]["status"] == "planned, not executed", "False verification outcome")
        require(row["native_mop"] == f"FrameworkRequirements::MOP_FR{fr[-2:]}", "Obsolete MOP name")
    exchanges = unique_rows(ledger["exchanges"], "name", "exchange")
    for row in exchanges.values():
        require(row["source_component"] in GROUPS and row["target_component"] in GROUPS, "Exchange component missing")
        require(row["source_component"] != row["target_component"], "Non-peer exchange")
        require(row["kind"] in {"information", "control"} and row["bindings"], "Untyped/empty exchange intent")
        for binding in row["bindings"]:
            require(binding["source_direction"] == "out" and binding["target_direction"] == "in", "Exchange direction mismatch")
            for end, direction in (("source", "outputs"), ("target", "inputs")):
                fr = binding[f"{end}_FR"]
                require(fr in allocations and allocations[fr]["primary"] == row[f"{end}_component"], "Exchange FR provenance/owner mismatch")
                fields = binding[f"{end}_fields"]
                categories = allocations[fr]["native_io"][direction] if ledger.get("native_status") in {"ready", "verified"} else allocations[fr][direction]
                require(fields and len(fields) == len(set(fields)) and set(fields) <= set(categories), "Exchange IO field provenance mismatch")
            require(bool(binding["mapping"]), "Differently named fields need an explicit mapping")
    return source


def validate_guard(actual, expected, target, expected_target):
    require(compact(actual) == compact(expected), "Lost required safety guard")
    require(target == expected_target, "Safety guard controls wrong action")


def reachable_without_gate(edges, starts):
    reachable = set(starts)
    while True:
        expanded = reachable | {b for a, b in edges if a in reachable}
        if expanded == reachable:
            return reachable
        reachable = expanded


def mutate_exact(text, selector, replacement):
    # Crucially outside a rejection-catching try block. No match is a failed test.
    require(selector and text.count(selector) == 1, "Negative mutation selector must match exactly once")
    require(selector != replacement, "Negative mutation must change source")
    return text.replace(selector, replacement, 1)


class Native:
    def __init__(self, tool, root, files):
        result = tool.validate([root / f for f in files], [], warnings_as_errors=True, config=None)
        try:
            self.model, self.api = tool.require_semantic_model(result)
        except tool.ToolError as error:
            if error.exit_code == 1:
                details = "; ".join(d.message for d in result.diagnostics[:6])
                raise ValueError(f"Native model invalid ({result.summary}): {details or error}") from error
            raise RuntimeError(f"Native tooling unavailable: {error}") from error
        self.elements = list(self.model.nodes(self.api.Element, include_subtypes=True))
        self.by = {qn(e): e for e in self.elements if e.qualified_name}
        for element in self.elements:
            if isinstance(element, self.api.Feature):
                for typename in element.types:
                    if typename.qualified_name:
                        self.by.setdefault(qn(typename), typename)
        self.compiler = self.api.Compiler()

    def annotations(self, element, typename):
        return [e for e in self.elements if isinstance(e, self.api.MetadataUsage)
                and element in e.annotated_elements and any(qn(t) == typename for t in e.types)]

    def values(self, annotation):
        values = {}
        for feature in annotation.owned_features:
            value, diagnostics = self.compiler.evaluate_feature(feature, annotation)
            require(bool(diagnostics), f"Cannot evaluate native feature {feature.name}")
            values[feature.name] = value
        return values

    def dependencies(self, element):
        return {t for e in self.elements if isinstance(e, self.api.Dependency)
                and element in e.sources for t in e.targets}

    def require_element(self, name):
        require(name in self.by, f"Unresolved native export: {name}")
        return self.by[name]


def chain(feature):
    return list(feature.chaining_features) or [feature]


def array(value):
    return [value] if isinstance(value, str) else list(value)


def check_native_source(native, ledger, source):
    by, elements, api = native.by, native.elements, native.api
    actual = {e.name.replace("FR_", "FR-") for e in elements
              if type(e).__name__ == "RequirementUsage" and qn(e.owner) == "FrameworkRequirements"}
    require(actual == set(source), "Native active FR set differs from report")
    for row in ledger["allocations"]:
        fr = native.require_element(row["native_requirement"])
        metadata = native.annotations(fr, "FrameworkDomain::SourceRecord")
        require(len(metadata) == 1 and native.values(metadata[0])["sourceText"] == row["statement"], "Native/report requirement meaning mismatch")
        checks = native.annotations(fr, "FrameworkRequirements::PlannedRequirementCheck")
        require(len(checks) == 1, "Missing planned requirement check")
        check = native.values(checks[0])
        require(check["methods"] == row["verification"]["methods"] and check["checkSummary"] == row["verification"]["need"], "Changed planned check meaning")
        io = native.annotations(fr, "FrameworkRequirements::RequirementExchange")
        if io:
            require(len(io) == 1, "Duplicate source IO metadata")
            fields = native.values(io[0])
            for direction in ("inputs", "outputs"):
                require(array(fields[direction]) == row[direction], "Native final source IO mismatch")
        else:
            for direction in ("inputs", "outputs"):
                require(row[direction] == [row[f"{direction}_verbatim"]], "Invented source IO partition")
        # Native derivation ends, not a regex over model source or inferred MR parents.
        parents = set()
        for connection in elements:
            if type(connection).__name__ != "ConnectionUsage" or qn(connection.owner) != "FrameworkRequirements":
                continue
            ends = {e.name: getattr(e, "referenced_feature", None) for e in connection.owned_features}
            if ends.get("target") == fr and qn(ends.get("source")).startswith("FrameworkNeeds::MR_"):
                parents.add(ends["source"].name.replace("MR_", "MR-"))
        require(parents == set(row["parents"]), "Native/report MR derivation mismatch")
        mop = native.require_element(row["native_mop"])
        require(fr in native.dependencies(mop), "MOP lost direct final FR dependency")


GUARDS = {'AssistanceRealization': {'admitInput': ['receive.compatible', 'capture'], 'admitReply': ['checkReply.sameContext', 'present'], 'admitDisposition': ['dispose.authorized and checkApplication.sameContext', 'applyCorrection'], 'applyAuthorized': ['dispose.applyRequested', 'derive'], 'validRequirements': ['validate.resolved', 'retainValidation']}, 'DesignRealization': {'admitInput': ['receive.compatible', 'configure'], 'admitResult': ['receiveResult.compatible', 'preserve'], 'admitModel': ['checkCurrent.current and credibility.numericallyValid and credibility.applicable', 'assess'], 'admitCriteria': ['assess.claimSupported', 'compare'], 'admitSelection': ['compare.feasible and select.accepted and checkSelection.authorizedCurrent', 'retainSelection']}, 'SoftwareRealization': {'admitInput': ['receive.compatible', 'interfaces'], 'admitMIL': ['receiveMIL.compatible', 'preserveMIL'], 'authorizeCoding': ['checkRelease.authorizedDetailedDesign and checkRelease.currentDesign and checkRelease.blockersClear and interfaces.profileCompatible and mapping.profileCompatible', 'coordinate'], 'admitSIL': ['receiveSIL.compatible', 'preserveSIL'], 'admitProducts': ['checkCurrent.current and credibility.numericallyValid and credibility.applicable and assess.claimSupported', 'present'], 'admitApproval': ['checkProducts.authorizedCurrent', 'retainProducts']}, 'ChangeReviewRealization': {'admitInput': ['receive.compatible', 'invalidate'], 'proposedChange': ['invalidate.hasChange', 'changeDecision'], 'admitChange': ['checkChange.authorizedCurrent and checkChange.acceptedChange', 'successor'], 'repeatAffected': ['checkChange.reassessmentRequired', 'planRepeat'], 'admitResult': ['receiveResult.compatible', 'preserve'], 'preparePackage': ['prepare.entranceComplete', 'reviewers'], 'admitReviewDecision': ['checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete)', 'record']}, 'ReplayRealization': {'admitReplay': ['prepare.dependenciesComplete and prepare.rulesFixed', 'execute'], 'admitResult': ['receive.compatible', 'preserve']}, 'CalibrationRealization': {'admitData': ['receive.compatible', 'checkData'], 'admitCalibration': ['checkData.dataUsable and checkData.independentSeparation', 'propose'], 'admitCalibrationChange': ['checkChange.authorizedCurrent and checkChange.acceptedChange', 'successor'], 'admitReassessedResult': ['receiveResult.compatible', 'preserve']}, 'ConceptRealization': {'admitInput': ['receive.compatible', 'makeConfiguration'], 'admitResult': ['receiveResult.compatible', 'preserve'], 'admitModel': ['checkCurrent.current and credibility.numericallyValid and credibility.applicable', 'assess'], 'admitCriteria': ['assess.claimSupported', 'compare'], 'admitSelection': ['compare.feasible and select.accepted and checkSelection.authorizedCurrent', 'retainSelection']}}

RECORD_FIELDS = [('FrameworkLogical::RunWork::result', 'BoundaryViews::AnalysisResult', '0..1', False), ('FrameworkLogical::RunWork::milResult', 'BoundaryViews::AnalysisResult', '0..1', False), ('FrameworkLogical::ReplayComparison::result', 'BoundaryViews::AnalysisResult', '0..1', False), ('BoundaryViews::HistorySample::numericValue', 'ScalarValues::Real', '0..1', True), ('BoundaryViews::HistorySample::sampleTimeSeconds', 'ScalarValues::Real', '0..1', True), ('BoundaryViews::HistorySample::receiptTimeSeconds', 'ScalarValues::Real', '0..1', True), ('BoundaryViews::HistorySample::rawValue', 'ScalarValues::String', '1', False), ('BoundaryViews::HistorySample::validInvalidMissingInactive', 'ScalarValues::String', '1', False), ('BoundaryViews::HistorySample::processingMaskAndReason', 'ScalarValues::String', '1', False), ('BoundaryViews::HistorySample::modelScenarioEntityChannelRevision', 'ScalarValues::String', '1', False), ('BoundaryViews::HistorySample::quantityKindUnitSignFrame', 'ScalarValues::String', '1', False), ('BoundaryViews::HistorySample::scenarioTimeBase', 'ScalarValues::String', '1', False), ('BoundaryViews::SoftwareRunResult::product', 'BoundaryViews::HostSoftwareProduct', '0..1', False), ('BoundaryViews::ReferenceData::samples', 'BoundaryViews::HistorySample', '0..*', False), ('BoundaryViews::ModelAssessment::calibrationDataRevision', 'ScalarValues::String', '0..1', False), ('BoundaryViews::ModelAssessment::independentAssessmentDataRevision', 'ScalarValues::String', '0..1', False), ('BoundaryViews::AnalysisResult::executionSuccessFailedCancelledPartial', 'ScalarValues::String', '1', False), ('FrameworkLogical::ExecutionStatusRecord::successFailedCancelledPartial', 'ScalarValues::String', '1', False), ('FrameworkLogical::ExecutionStatusRecord::numericalPayload', 'BoundaryViews::ReferenceData', '0..*', False), ('FrameworkLogical::RetainSuccessor::decision', 'BoundaryViews::EngineeringDecision', '1', False), ('FrameworkLogical::DetailedDesignAuthorization::decision', 'BoundaryViews::EngineeringDecision', '1', False), ('FrameworkLogical::DetailedDesignAuthorization::context', 'BoundaryViews::ContextRevision', '1', False)]

def direction(feature):
    return str(feature.direction).split(".")[-1].lower() if feature.direction is not None else None


def multiplicity(feature):
    value = feature.multiplicity
    if value is None:
        return "1"
    low, high = value.lower_bound, value.upper_bound
    require(type(low).__name__ == "LiteralInteger", "Unresolved multiplicity lower bound")
    upper = "*" if type(high).__name__ == "LiteralInfinity" else str(high.value)
    return str(low.value) if str(low.value) == upper else f"{low.value}..{upper}"


def flow_record(native, flow):
    ends = {e.name: e for e in flow.owned_features if type(e).__name__ == "FlowEnd"}
    require(set(ends) == {"source", "target"}, "Flow lacks two actual native ends")
    result = {"native": qn(flow), "ends": {}}
    for name, context in (("source", flow.source_feature), ("target", list(flow.target_features)[0])):
        parameters = list(ends[name].owned_features)
        require(len(parameters) == 1, "Flow end parameter missing/ambiguous")
        parameter = parameters[0]
        redefinitions = list(parameter.owned_redefinitions)
        require(len(redefinitions) == 1, "Flow end must redefine its resolved declared parameter")
        declaration = redefinitions[0].redefined_feature
        result["ends"][name] = {"context": [qn(e) for e in chain(context)], "parameter": qn(declaration)}
    payloads = list(flow.payload_types)
    result["payload_basis"] = "explicit flow type" if payloads else "resolved producer parameter type"
    if not payloads:
        payloads = list(native.require_element(result["ends"]["source"]["parameter"]).types)
    leaves = [t for t in payloads if not any(t != other and other.conforms(t) and not t.conforms(other) for other in payloads)]
    require(len(leaves) == 1, f"Flow payload missing/ambiguous: {qn(flow)} {[qn(t) for t in payloads]}")
    result["payload"] = qn(leaves[0])
    for name, end in result["ends"].items():
        parameter = native.require_element(end["parameter"])
        require(any(t.conforms(leaves[0]) if name == "source" else leaves[0].conforms(t) for t in parameter.types), "Flow payload/parameter conformance mismatch")
    return result


def binding_record(binding):
    targets = list(binding.target_features)
    require(len(targets) == 1, "Ambiguous native binding")
    return {"source": [qn(e) for e in chain(binding.source_feature)],
            "target": [qn(e) for e in chain(targets[0])]}


def check_native_architecture(native, ledger):
    require(ledger["native_status"] in {"ready", "verified"} and ledger["native_contract"] is not None,
            "Native architecture synchronization incomplete")
    by, elements, api = native.by, native.elements, native.api
    logical = native.require_element("FrameworkLogical::LogicalFramework")
    require(logical.conforms(native.require_element("FrameworkDomain::ToBe::FutureFramework")), "Logical root changed black-box meaning")
    parts = {p.name: p for p in logical.owned_features if type(p).__name__ == "PartUsage"}
    require(set(parts) == set(GROUPS), "Native component coverage")
    for name in ledger["native_contract"]["retired_exports"]:
        require(name not in by, "Obsolete logical export restored")
    owned = [e for e in elements if qn(e).startswith(("FrameworkLogical::", "LogicalRealization::"))]
    require(not any(type(e).__name__ == "SatisfyRequirementUsage" for e in owned), "Planned architecture asserts satisfaction")
    require(not any(direction(e) == "inout" for e in owned if isinstance(e, api.Feature)), "Generic inout logical work interface restored")
    forbidden = {"FrameworkDomain::TestingFacilityTechnician", "FrameworkDomain::EPSHardware", "FrameworkDomain::AsIs::TestingFacility"}
    require(not any(type(e).__name__ == "PartUsage" and forbidden.intersection(qn(t) for t in e.types) for e in owned), "Physical participant leaked into logical design")
    components = {r["id"]: r for r in ledger["components"]}
    for cid, part in parts.items():
        require(qn(part) == components[cid]["native_part"] and native.require_element(components[cid]["native_type"]) in part.types, "Native component type disagreement")
    allocations = [e for e in elements if type(e).__name__ == "AllocationUsage"]
    primary = [a for a in allocations if native.annotations(a, "FrameworkDomain::primaryResponsibility")]
    require(len(primary) == len(ledger["allocations"]), "Native missing/duplicate primary allocation")
    owners = set()
    for row in ledger["allocations"]:
        fr = native.require_element(row["native_requirement"])
        assigned = [a for a in primary if a.source_feature == fr]
        require(len(assigned) == 1, "Native FR primary allocation exactness")
        allocation = assigned[0]
        target = chain(list(allocation.target_features)[0])
        require(len(target) == 2 and qn(target[0]) == "FrameworkLogical::logical" and target[-1] == parts[row["primary"]], "Native wrong primary owner")
        require(fr not in owners, "Duplicate primary FR")
        owners.add(fr)
        require(qn(allocation) == row["native_allocation"], "Native allocation path disagreement")
        meta = native.annotations(allocation, "FrameworkLogical::LogicalAllocation")
        require(len(meta) == 1, "Missing allocation rationale/check metadata")
        fields = native.values(meta[0]); operation = fields["operation"].element
        require(qn(operation) == row["operation"] and operation.owner in parts[row["primary"]].types and operation in native.dependencies(fr), "Native FR operation owner/dependency mismatch")
        require(fields["rationale"] == row["rationale"] and fields["plannedCheck"] == row["verification"]["methods"] + ": " + row["verification"]["need"], "Allocation changed planned check/rationale")
        helpers = {chain(list(a.target_features)[0])[-1].name for a in allocations if a.source_feature == fr and native.annotations(a, "FrameworkDomain::supportingResponsibility")}
        require(helpers == set(row["support"]) and row["primary"] not in helpers, "Supporting allocation mismatch")
        ports = {qn(t) for t in native.dependencies(fr) if type(t).__name__ == "PortUsage"}
        require(ports == set(row["interfaces"]), "Invented/default boundary interface trace")
        actual_behaviors = {qn(t) for t in native.dependencies(fr) if type(t).__name__ == "PerformActionUsage" and qn(t).startswith("LogicalRealization::")}
        require(actual_behaviors and actual_behaviors == set(row["behaviors"]), "FR behavior provenance mismatch")
        for name in row["behaviors"]:
            task = native.require_element(name); metadata = native.annotations(task, "LogicalRealization::LogicalStep")
            require(len(metadata) == 1, "Behavior logical owner missing")
            assignment = native.values(metadata[0])
            require(assignment["component"].element == parts[row["primary"]] and assignment["operation"].element == operation, "FR behavior/operation/component disagreement")
        io = row["native_io"]; contract = native.require_element(io["model_path"])
        require(contract.owner == operation.owner and native.require_element(io["contract_action_type"]) in contract.types, "FR contract operation/type ownership")
        metadata = native.annotations(contract, "FrameworkLogical::NativeIO")
        require(len(metadata) == 1, "Native complete IO contract missing")
        values = native.values(metadata[0])
        require(values["fr"] == row["FR"] and values["primary"] == row["primary"] and values["operation"].element == operation, "Native IO responsible-operation provenance")
        definition = native.require_element(components[row["primary"]]["native_type"])
        bindings = [binding_record(e) for e in definition.owned_features if type(e).__name__ == "BindingConnectorAsUsage"]
        for d, parameter_name, port_name in (("inputs", "subjects", "Inputs"), ("outputs", "products", "Outputs")):
            require(array(values[d]) == io[d], "Native IO exact partition mismatch")
            subject = native.require_element(io[d + "_path"])
            fields_by_name = {f.name: f for f in subject.owned_features if type(f).__name__ == "ItemUsage"}
            require(len(fields_by_name) == len(io["field_contracts"][d]), "Native IO union field missing/extra")
            for field in io["field_contracts"][d]:
                feature = native.require_element(field["path"])
                require(feature in fields_by_name.values() and native.require_element(field["type"]) in feature.types and multiplicity(feature) == field["multiplicity"], "Native IO subject type/multiplicity mismatch")
                metas = native.annotations(feature, "FrameworkLogical::Subject")
                require(len(metas) == 1, "Native IO field provenance missing")
                provenance = native.values(metas[0])
                require(provenance == field["subject_metadata"], "Native IO field source/direction/provenance mismatch")
                require(provenance["fr"] == row["FR"] and provenance["direction"] == d and provenance["exactField"] == field["exact_field"], "Native FR IO field direction/provenance mismatch")
            port = native.require_element(f"FrameworkLogical::{row['primary']}Subjects::fr{row['FR'][-2:]}{port_name}")
            require(direction(port) == ("in" if d == "inputs" else "out") and subject in port.types, "Native complete union port direction/type")
            parameter = native.require_element(io["contract_action_type"] + "::" + parameter_name)
            require(direction(parameter) == direction(port) and subject in parameter.types, "Native contract parameter direction/type")
            a = [components[row["primary"]]["native_type"] + "::io", qn(port)]
            b = [qn(contract), qn(parameter)]
            expected = {"source": a if d == "inputs" else b, "target": b if d == "inputs" else a}
            require(expected in bindings, "Contract complete IO is not bound to its owning directed port")
    # Source unions and typed partitions are independently retained and compared.
    for component in ledger["components"]:
        rows = [r for r in ledger["allocations"] if r["primary"] == component["id"]]
        for d in ("inputs", "outputs"):
            actual = {}
            for row in rows:
                for f in row["native_io"]["field_contracts"][d]: actual.setdefault(f["exact_field"], []).append({"FR": row["FR"], "native": f["path"], "type": f["type"]})
            require(component["typed_io_union"][d] == actual, "Typed native union/provenance disagreement")
    root_bindings = [binding_record(e) for e in logical.owned_features if type(e).__name__ == "BindingConnectorAsUsage"]
    exchanges = ledger["exchanges"]
    require(len(exchanges) == 20 and sum(len(e["mappings"]) for e in exchanges) == 203, "Pairwise native mapping coverage")
    mapped_flows = set()
    for row in exchanges:
        aggregate = native.require_element(row["native"])
        require(native.require_element(row["payload_type"]) in aggregate.types, "Aggregate typed record mismatch")
        record = native.require_element(row["payload_type"])
        actual_fields = [f for f in record.owned_features if native.annotations(f, "FrameworkLogical::ExchangeField")]
        require(len(actual_fields) == len(row["mappings"]), "Aggregate member coverage mismatch")
        for mapping in row["mappings"]:
            op = native.require_element(mapping["operation_path"])
            require(type(op).__name__ == "PerformActionUsage" and op.owner == logical and native.require_element(mapping["action_type"]) in op.types, "Projection is not an actual performed mapping operation")
            field = native.require_element(mapping["aggregate_field"])
            metadata = native.annotations(field, "FrameworkLogical::ExchangeField")
            require(len(metadata) == 1 and native.values(metadata[0]) == mapping["metadata"], "Exchange FR field provenance/translation mismatch")
            require(field in actual_fields, "Aggregate field not owned by aggregate type")
            for side, d in (("source", "outputs"), ("target", "inputs")):
                fr = next(a for a in ledger["allocations"] if a["FR"] == mapping[f"{side}_fr"])
                require(fr["primary"] == row[f"{side}_component"] and mapping["source_output" if side == "source" else "target_input"] in fr["native_io"][d], "Exchange native field direction/owner provenance")
                declaration = native.require_element(mapping[f"{side}_declaration"])
                parameter = native.require_element(mapping["action_type"] + "::" + side)
                require(direction(parameter) == ("in" if side == "source" else "out") and any(t in parameter.types for t in declaration.types if qn(t) == mapping[f"{side}_qualified_type"]), "Projection declared parameter type/direction mismatch")
                flow = native.require_element(mapping[f"{side}_flow"]["native"])
                require(flow_record(native, flow) == mapping[f"{side}_flow"], "Projection flow actual parameter chain mismatch")
                mapped_flows.add(qn(flow))
            require({"source": [qn(aggregate), qn(field)], "target": [qn(op), mapping["action_type"] + "::source"]} in root_bindings, "Aggregate field is not bound to actual producer projection")
    for row in ledger["native_contract"]["boundary_flows"]:
        require(flow_record(native, native.require_element(row["native"])) == row, "Boundary directed dispatch parameter chain mismatch")
    actual_root_flows = {qn(e) for e in logical.owned_features if type(e).__name__ == "FlowUsage"}
    require(actual_root_flows == mapped_flows | {r["native"] for r in ledger["native_contract"]["boundary_flows"]}, "Unrecorded or missing logical root flow")
    require(root_bindings == ledger["native_contract"]["root_bindings"], "Boundary/aggregate native binding coverage mismatch")
    require(len(ledger["external_exchanges"]) == 5, "Visible external aggregate coverage")
    for row in ledger["external_exchanges"]:
        aggregate = native.require_element(row["native"]); endpoint = native.require_element(row["endpoint_declaration"])
        require(native.require_element(row["type"]) in aggregate.types and direction(endpoint) == row["direction"], "External platform aggregate type/direction")
        require(row["binding"] in root_bindings and row["binding"]["source"] == [qn(aggregate)], "External aggregate lacks real boundary binding")
    require(native.require_element("FrameworkContext::Engines").conforms(native.require_element("FrameworkDomain::ToBe::CUBICSSimulationEnvironment")), "Whole-CUBICS platform scope lost")
    check_native_safety(native, ledger)
    return {"components": len(parts), "current_FRs": len(primary), "pairwise_aggregates": len(exchanges), "field_mappings": len(mapped_flows)//2, "external_aggregates": 5}


def evaluate_guard(api, expression, environment):
    if isinstance(expression, api.FeatureReferenceExpression):
        require(expression.referent in environment, "Uncontrolled native guard reference")
        return environment[expression.referent]
    if isinstance(expression, api.FeatureChainExpression):
        operands = list(expression.operands)
        require(len(operands) == 1, "Invalid guard chain")
        record = evaluate_guard(api, operands[0], environment)
        require(isinstance(record, dict) and expression.target_feature in record, "Guard outcome is not the resolved decision/operation payload")
        return record[expression.target_feature]
    if isinstance(expression, api.LiteralBoolean):
        return expression.value
    require(isinstance(expression, api.OperatorExpression), "Unsupported native guard expression")
    op = str(expression.operator); values = [evaluate_guard(api, e, environment) for e in expression.operands]
    if op in ("and", "or", "not"):
        require(all(type(v) is bool for v in values), "Non-Boolean safety operand")
        return not values[0] if op == "not" else all(values) if op == "and" else any(values)
    require(op in ("==", "!=") and len(values) == 2, "Unsupported guard operator")
    return (values[0] == values[1]) if op == "==" else (values[0] != values[1])


def check_native_safety(native, ledger):
    from itertools import product
    from types import SimpleNamespace
    safety = ledger["safety_contract"]
    require(safety and set(safety["families"]) == SAFETY_FAMILIES, "Safety contract incomplete")
    expected_guards = [{"native": f"LogicalRealization::{name}::{gate}", "expression": expr, "target": f"LogicalRealization::{name}::{target}"}
                       for name, rows in GUARDS.items() for gate, (expr, target) in rows.items()]
    require(safety["guards"] == expected_guards, "Independent safety guard basis changed")
    require([(r["native"], r["type"], r["multiplicity"], r.get("no_default", False)) for r in safety["record_fields"]] == RECORD_FIELDS, "Independent raw/status/authority record basis changed")
    api, elements = native.api, native.elements
    actions = {native.require_element(row["native"]) for row in safety["realizations"]}
    allocations = [e for e in elements if type(e).__name__ == "AllocationUsage" and qn(e.owner) == "LogicalRealization"]
    tasks = [e for e in elements if type(e).__name__ == "PerformActionUsage" and e.owner in actions]
    require({qn(t) for t in tasks} == {r["native"] for r in safety["tasks"]}, "Logical task coverage")
    for row in safety["tasks"]:
        task = native.require_element(row["native"])
        require(native.require_element(row["action_type"]) in task.types, "Task operation type changed")
        assignments = [a for a in allocations if a.source_feature == task]
        require(len(assignments) == 1, "Task allocation exactness")
        require([qn(x) for x in chain(list(assignments[0].target_features)[0])] == row["allocated_target"], "Task native owner/actor changed")
        logical = native.annotations(task, "LogicalRealization::LogicalStep")
        external = native.annotations(task, "LogicalRealization::ExternalStep")
        require(len(logical) + len(external) == 1, "Unowned/multiply owned task")
        values = native.values((logical or external)[0])
        if logical:
            component, operation = values["component"].element, values["operation"].element
            require(qn(component) == row["component"] and qn(operation) == row["operation"] and operation.owner in component.types and set(task.types) == set(operation.types), "Task operation/component mismatch")
        else:
            actor = values["performer"].element
            require(qn(actor) == row["actor"] and actor.name in {"systemsEngineer", "epsEngineer", "analysisTools", "hostToolchain", "reviewers", "reviewAuthority"}, "External authority actor changed")
    all_flows = [flow_record(native, e) for e in elements if type(e).__name__ == "FlowUsage" and e.owner in actions]
    require(all_flows == safety["flows"], "Actual realization data producer/consumer parameter chain changed")
    for row in safety["realizations"]:
        action = native.require_element(row["native"])
        require(set(row["scenarios"]) <= {qn(t) for t in native.dependencies(action)}, "Scenario realization basis changed")
    truth_cases = 0
    for row in safety["guards"]:
        transition = native.require_element(row["native"])
        require(type(transition).__name__ == "TransitionUsage" and transition.guard_expression is not None and qn(transition.target) == row["target"], "Safety guard lost or controls wrong action")
        owner = transition.owner
        predicates = sorted(set(re.findall(r"\b(\w+)\.(\w+)\b", row["expression"])))
        for bits in product((False, True), repeat=len(predicates)):
            environment, expected_environment = {}, {}
            for (opname, fieldname), bit in zip(predicates, bits):
                operation = native.require_element(qn(owner) + "::" + opname)
                field = next(f for t in operation.types for f in t.owned_features if f.name == fieldname)
                require(type(operation).__name__ == "PerformActionUsage" and any(qn(t) == "ScalarValues::Boolean" for t in field.types), "Guard is not an owned operation Boolean result")
                environment.setdefault(operation, {})[field] = bit
                expected_environment.setdefault(opname, SimpleNamespace()).__dict__[fieldname] = bit
            expected = eval(row["expression"], {"__builtins__": {}}, expected_environment)
            actual = evaluate_guard(api, transition.guard_expression, environment)
            require(type(actual) is bool and actual == expected, "Native safety guard counterexample")
            truth_cases += 1
        require(not any(type(e).__name__ == "SuccessionAsUsage" and e.owner == owner and transition.target in e.target_features for e in elements), "Unguarded protected entry")
        require(any(type(e).__name__ == "TransitionUsage" and e.owner == owner and e.source == transition.source and e != transition and e.guard_expression is not None for e in elements), "Safety gate lost rejection/alternative")
    for row in safety["dominance"]:
        owner = native.require_element(row["realization"]); gate = native.require_element(row["gate"]); protected = native.require_element(row["protected"])
        edges = [(e.source_feature, t) for e in elements if type(e).__name__ == "SuccessionAsUsage" and e.owner == owner for t in e.target_features]
        edges += [(e.source, e.target) for e in elements if type(e).__name__ == "TransitionUsage" and e.owner == owner and e != gate]
        starts = {a for a, _ in edges if a.name == "start"}
        require(starts and protected not in reachable_without_gate(edges, starts), "Safety gate bypass reaches protected action")
    for row in safety["immediate_successions"]:
        a, b = native.require_element(row["source"]), native.require_element(row["target"])
        require(any(type(e).__name__ == "SuccessionAsUsage" and e.source_feature == a and list(e.target_features) == [b] for e in elements), "Immediate context invalidation removed")
    for cid, member, state, mappingname, inherited in (("L06", "assistanceCurrency", "GuidanceControl", "guidanceControlOwner", "guidanceControl"), ("L05", "reviewState", "BaselineControl", "baselineControlOwner", "baselineControl")):
        definition = native.require_element(next(c["native_type"] for c in ledger["components"] if c["id"] == cid))
        feature = native.require_element(qn(definition) + "::" + member)
        require(native.require_element("ScenarioViews::" + state) in feature.types, "Responsible component state missing")
        mapping = native.require_element("FrameworkLogical::" + mappingname)
        require(chain(mapping.source_feature)[-1].name == inherited and [x.name for x in chain(list(mapping.target_features)[0])][-2:] == [cid, member], "Black-box state ownership changed")
    for edit in ("editCurrent", "editPending"):
        require(native.require_element("ScenarioViews::GuidanceControl::" + edit).target.name == "stale", "Edit fails immediate pending/current invalidation")
    for row in safety["state_guards"]:
        transition = native.require_element(row["native"])
        require(transition.guard_expression is not None and qn(transition.target) == row["target"], "Guidance/review state guard or target missing")
    guidance = native.require_element("ScenarioViews::GuidanceControl")
    for member, expected in (("apply", lambda current, authorized: current and authorized), ("response", lambda current, authorized: current)):
        transition = native.require_element(qn(guidance) + "::" + member)
        for current, authorized in product((False, True), repeat=2):
            environment = {native.require_element(qn(guidance) + "::sameContext"): current,
                           native.require_element(qn(guidance) + "::authorized"): authorized}
            require(evaluate_guard(api, transition.guard_expression, environment) == expected(current, authorized), "Guidance state authority/currency counterexample")
    check_review_control(elements, native.by, api)
    for row in safety["record_fields"]:
        feature = native.require_element(row["native"])
        require(native.require_element(row["type"]) in feature.types and multiplicity(feature) == row["multiplicity"], "Raw sample/result/evidence record type or optionality changed")
        if row.get("no_default"):
            require(feature.feature_value_expression is None, "Missing sample/time fabricated with a default value")
    ledger_summary = ledger["native_contract"]["source_query_basis"]
    query = native.require_element(ledger_summary["operation"])
    require(native.require_element("FrameworkLogical::RequestApplicableSource") in query.types and ledger_summary["FR"] == ["FR-03", "FR-13"], "Unbounded source-query basis")
    require(ledger_summary["binding"] in ledger["native_contract"]["root_bindings"], "Source query disconnected from declared guidance input")
    return truth_cases


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
    from itertools import product
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

def check(tool, root, ledger_path, report_path, *, core_only=False, source_only=False):
    ledger = json.loads(ledger_path.read_text())
    requirements = report_path.parent / "requirements.tex"
    source = validate_source_contract(ledger, requirements.read_text(), report_path.read_text())
    config = tomllib.loads((root / "logical-responsibilities.toml").read_text())
    require(config["validation"]["pending_native_is_failure"], "Pending architecture cannot pass")
    native = Native(tool, root, SOURCE_FILES if source_only else CORE_FILES if core_only else FILES)
    check_native_source(native, ledger, source)
    figure = ledger["figure"]
    for pathkey, hashkey in (("source", "source_sha256"), ("pdf", "pdf_sha256")):
        require(hashlib.sha256((report_path.parent / figure[pathkey]).read_bytes()).hexdigest() == figure[hashkey], "Approved custom figure identity changed")
    result = {"status": "passed", "scope": "source contract only" if source_only else "core logical model" if core_only else "full model",
              "native_errors": 0, "native_warnings": 0, "active_FRs": len(source),
              "MR_parent_links": sum(len(r["parents"]) for r in source.values()),
              "native_architecture_checked": not source_only, "verification": "planned only"}
    if not source_only:
        result.update(check_native_architecture(native, ledger))
    return result


def require_native_mutation_rejection(returncode, reason):
    require(returncode == 1 and reason.startswith("FAIL:")
            and "Native tooling unavailable" not in reason and "Traceback" not in reason,
            "Mutation was not rejected by native semantic/policy checking")


def negative_checks(tool, root, ledger, report, *, core_only=False):
    import subprocess
    from concurrent.futures import ThreadPoolExecutor
    check(tool, root, ledger, report, core_only=core_only)
    data = json.loads(ledger.read_text())
    cases = data["safety_contract"]["mutations"]
    require({r["family"] for r in cases} >= SAFETY_FAMILIES, "Missing safety negative cases")
    with tempfile.TemporaryDirectory(prefix="logical-negative-") as directory:
        base = Path(directory)
        frozen_checker = base / "frozen-checker.py"
        shutil.copy2(Path(__file__).resolve(), frozen_checker)
        frozen_ledger = base / "frozen-ledger.json"
        shutil.copy2(ledger, frozen_ledger)
        frozen_report = base / "report/logical.tex"
        frozen_report.parent.mkdir()
        shutil.copy2(report, frozen_report)
        shutil.copy2(report.parent / "requirements.tex", frozen_report.parent / "requirements.tex")
        for key in ("source", "pdf"):
            destination = frozen_report.parent / data["figure"][key]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(report.parent / data["figure"][key], destination)
        jobs = []
        for row in cases:
            require(row["file"] in CORE_FILES, "Negative mutation outside logical core")
            case = Path(directory) / row["name"]
            case.mkdir()
            for name in CORE_FILES if core_only else FILES:
                target = case / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / name, target)
            shutil.copy2(root / "logical-responsibilities.toml", case / "logical-responsibilities.toml")
            path = case / row["file"]
            text = path.read_text()
            if row.get("scope_start"):
                require(text.count(row["scope_start"]) == 1, "Negative scope must match exactly once")
                start = text.index(row["scope_start"])
                end = text.index(row["scope_end"], start + len(row["scope_start"])) if row.get("scope_end") else len(text)
                mutated = text[:start] + mutate_exact(text[start:end], row["selector"], row["replacement"]) + text[end:]
            else:
                mutated = mutate_exact(text, row["selector"], row["replacement"])
            path.write_text(mutated)
            jobs.append((row, case))

        def run(job):
            row, case = job
            command = [sys.executable, str(frozen_checker), "--tool", str(Path(tool.__file__).resolve()),
                       "--model-root", str(case), "--ledger", str(frozen_ledger), "--report", str(frozen_report)]
            if core_only:
                command.append("--core-only")
            completed = subprocess.run(command, capture_output=True, text=True, timeout=180)
            reason = completed.stderr.strip()
            require_native_mutation_rejection(completed.returncode, reason)
            print(f"Native mutation rejected: {row['name']}: {reason[:130]}", file=sys.stderr, flush=True)
            return {"case": row["name"], "selector_matched": True, "native_check_executed": True,
                    "rejected": True, "reason": reason[6:][:300]}

        # Isolated native processes, not shared concurrent Syside API models.
        with ThreadPoolExecutor(max_workers=4) as pool:
            return list(pool.map(run, jobs))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", type=Path, default=Path("/Users/antho/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py"))
    parser.add_argument("--model-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--ledger", type=Path, default=Path(__file__).resolve().parent.parent / "traceability/logical-architecture.json")
    parser.add_argument("--report", type=Path, default=Path(__file__).resolve().parent.parent / "logical.tex")
    boundary = parser.add_mutually_exclusive_group()
    boundary.add_argument("--core-only", action="store_true")
    boundary.add_argument("--source-only", action="store_true")
    parser.add_argument("--negative-cases", action="store_true")
    args = parser.parse_args()
    require(not (args.source_only and args.negative_cases), "Safety mutations require a complete native architecture baseline")
    spec = importlib.util.spec_from_file_location("logical_native_tool", args.tool.resolve())
    require(spec and spec.loader, "Cannot load native wrapper")
    tool = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = tool
    spec.loader.exec_module(tool)
    result = check(tool, args.model_root, args.ledger, args.report, core_only=args.core_only, source_only=args.source_only)
    if args.negative_cases:
        result["negative_cases"] = negative_checks(tool, args.model_root, args.ledger, args.report, core_only=args.core_only)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, AttributeError, RuntimeError, OSError, StopIteration) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
