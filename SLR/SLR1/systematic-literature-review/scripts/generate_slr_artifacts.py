#!/usr/bin/env python3
"""Build deterministic, controlled-code SLR evidence artifacts.

The generator is deliberately offline and reads only the reviewed corpus metadata,
the extraction codebook, structured controlled-code summaries, and canonical
claim-level controlled fields.  It never derives an aggregate from claim prose,
keywords, or emergent codes.  Run from any directory with:

    python3 SLR/SLR1/systematic-literature-review/scripts/generate_slr_artifacts.py

All paths are resolved relative to this file.  SVG, PDF, and PNG figure triplets
are rendered transactionally: a missing or failing SVG converter removes stale
target derivatives and makes the run fail.
"""
from __future__ import annotations

import csv
import html
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Sequence, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
REPORT_DIR = SCRIPT_DIR.parent
SLR1_DIR = REPORT_DIR.parent
EXTRACTIONS_DIR = SLR1_DIR / "extractions"
EXTRACTION_INDEX = SLR1_DIR / "extraction.json"
CODEBOOK_PATH = SLR1_DIR / "extraction_codebook.json"
PROTOCOL_PATH = SLR1_DIR / "protocol.md"
SCOPING_TEX = SLR1_DIR / "scoping-review" / "scoping-review.tex"
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"
DRAFTS_DIR = REPORT_DIR / "drafts"

EXPECTED_CODEBOOK_VERSION = "1.1"
CLAIM_PREFIX = "claimed_outcomes_value_mechanisms_evidence[]"

# These two QA classes are intentionally not codebook labels.  They keep missing
# and invalid values visible without recoding either into a substantive category.
UNMAPPED = "unmapped/invalid controlled value"
UNASSIGNED_VALUE = "unassigned/no controlled value"
UNASSIGNED_STATUS = "unassigned/no explicit status"

# Frequently used controlled-field paths.
P_TIER = "bibliographic_review_management.tier_status"
P_RQ1 = "bibliographic_review_management.rq1_relevance"
P_RQ2 = "bibliographic_review_management.rq2_relevance"
P_RQ3 = "bibliographic_review_management.rq3_relevance"
P_LIFECYCLE = "study_context_population.lifecycle_stage_addressed"
P_DEVELOPMENT_CONTEXT = "study_context_population.development_context"
P_EPS = "study_context_population.eps_relevance"
P_MATURITY = "study_context_population.model_maturity"
P_ARTIFACTS = "mbse_objective_scope_artifacts.model_artifacts_used"
P_GENERALITY = "mbse_objective_scope_artifacts.generality_reuse_mechanism"
P_APPROACH = "implementation_pathway_tailoring.approach_classification"
P_INTEROP = "toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms"
P_TOOL_LIMITATIONS = "toolchain_interoperability_lifecycle_continuity.toolchain_limitations"
P_EPS_ELEMENTS = "eps_verification_specific.eps_elements_modeled"
P_VV_ARTIFACTS = "eps_verification_specific.verification_validation_artifacts"
P_PREPHYSICAL = "eps_verification_specific.pre_physical_development_verification_mechanism"
P_IVV = "eps_verification_specific.ivv_integration_level"
P_TEST_READINESS = "eps_verification_specific.integration_test_readiness"
P_GOVERNANCE = "governance_roi_project_decision_linkage.model_governance_strategy"
P_ROI = "governance_roi_project_decision_linkage.roi_value_realization_evidence"
P_GOVERNANCE_GAP = "gap_mapping.governance_project_deliverables_roi"
P_EXTRACTION_CONFIDENCE = "synthesis_consistency.extraction_confidence"

P_CLAIM_OUTCOME = f"{CLAIM_PREFIX}.outcome_category"
P_CLAIM_RELIABILITY = f"{CLAIM_PREFIX}.reliability_subtype"
P_CLAIM_SPECIFICITY = f"{CLAIM_PREFIX}.specificity_of_claim"
P_CLAIM_MECHANISM = f"{CLAIM_PREFIX}.mbse_mechanism"
P_CLAIM_LIFECYCLE = f"{CLAIM_PREFIX}.lifecycle_stage"
P_CLAIM_EVIDENCE_TYPE = f"{CLAIM_PREFIX}.evidence_type"
P_CLAIM_METRIC = f"{CLAIM_PREFIX}.metric_or_value_indicator"
P_CLAIM_BASELINE = f"{CLAIM_PREFIX}.baseline_comparator"
P_CLAIM_CONFIDENCE = f"{CLAIM_PREFIX}.evidence_confidence_rating"

# Only documented claim aliases are accepted as controlled canonical fields.
# In particular, free-text ``baseline`` and prose detail fields are not aliases
# for baseline_comparator and cannot enter an aggregate.
CLAIM_FIELD_ALIASES: Dict[str, Tuple[str, ...]] = {
    P_CLAIM_OUTCOME: ("outcome_category", "category"),
    P_CLAIM_RELIABILITY: ("reliability_subtype",),
    P_CLAIM_SPECIFICITY: ("specificity_of_claim", "specificity"),
    P_CLAIM_MECHANISM: ("mbse_mechanism", "mechanism"),
    P_CLAIM_LIFECYCLE: ("lifecycle_stage",),
    P_CLAIM_EVIDENCE_TYPE: ("evidence_type",),
    P_CLAIM_METRIC: ("metric_or_value_indicator",),
    P_CLAIM_BASELINE: ("baseline_comparator",),
    P_CLAIM_CONFIDENCE: ("evidence_confidence_rating", "evidence_confidence"),
}

# A few older claim records carry field-specific statuses beside an unwrapped
# list/string.  The generic claim ``status`` is intentionally not borrowed: it
# is not a documented status for every individual controlled field.
CLAIM_STATUS_SIBLINGS: Dict[str, Tuple[str, ...]] = {
    P_CLAIM_BASELINE: ("baseline_status",),
    P_CLAIM_METRIC: ("metric_or_value_indicator_status", "metric_status"),
}

QUALITY_SCORE = {"No": 0.0, "Insufficiently": 0.5, "Yes": 1.0}

# This is a fixed, exact-code mapping used solely for the existing outcome-domain
# synthesis.  No claim wording is inspected.  A controlled outcome may support
# more than one deliberately declared synthesis domain.
OUTCOME_DOMAIN_ORDER = [
    "Reliability / mission assurance / risk",
    "Reproducibility / reuse / openness",
    "Integrability / interoperability / lifecycle continuity",
    "Traceability / consistency / requirements quality",
    "Cost / schedule / effort / efficiency / automation",
    "Governance / ROI / project decisions",
    "Decision support / analysis / trade-space / feasibility",
    "Communication / collaboration / knowledge",
    "Generality / scalability / tailoring",
    "Other / uncategorized controlled outcome",
    UNMAPPED,
    UNASSIGNED_VALUE,
]
OUTCOME_DOMAIN_MAP: Dict[str, Tuple[str, ...]] = {
    "reliability": ("Reliability / mission assurance / risk",),
    "mission assurance": ("Reliability / mission assurance / risk",),
    "risk reduction": ("Reliability / mission assurance / risk",),
    "defect/error reduction": ("Reliability / mission assurance / risk",),
    "reproducibility": ("Reproducibility / reuse / openness",),
    "generality/reuse": (
        "Reproducibility / reuse / openness",
        "Generality / scalability / tailoring",
    ),
    "integrability/interoperability": (
        "Integrability / interoperability / lifecycle continuity",
    ),
    "lifecycle continuity": ("Integrability / interoperability / lifecycle continuity",),
    "traceability": ("Traceability / consistency / requirements quality",),
    "consistency": ("Traceability / consistency / requirements quality",),
    "completeness": ("Traceability / consistency / requirements quality",),
    "cost reduction": ("Cost / schedule / effort / efficiency / automation",),
    "schedule reduction": ("Cost / schedule / effort / efficiency / automation",),
    "effort reduction": ("Cost / schedule / effort / efficiency / automation",),
    "automation": ("Cost / schedule / effort / efficiency / automation",),
    "governance/ROI": ("Governance / ROI / project decisions",),
    "decision support": ("Decision support / analysis / trade-space / feasibility",),
    "communication/stakeholder alignment": ("Communication / collaboration / knowledge",),
    "other": ("Other / uncategorized controlled outcome",),
}

# Controlled-code-only mapping for the retained derived V&V linkage output.
# This is a mixed-source category map, not a direct controlled field: it unions
# coded values from V&V artifacts, explicitly pre-physical mechanisms, and
# integration/test readiness without inspecting prose.  The generic/planned
# fallback additionally uses the controlled RQ3-relevance value when no coded
# artifact or pre-physical mechanism is selected.
VV_DERIVATION_BASIS = (
    "Derived mixed-source union of coded values from verification/validation artifacts, "
    "explicitly pre-physical verification mechanisms, and integration/test readiness; "
    "the generic/planned fallback additionally uses controlled RQ3 relevance when no "
    "coded artifact or pre-physical mechanism is selected"
)
VV_LINKAGE_ORDER = [
    "Requirements-to-model traceability or verification matrix",
    "Executable simulation or scenario analysis",
    "Parametric/budget/constraint checks",
    "Test cases/procedures/V&V activity packages",
    "External tool or data-flow coupling for V&V",
    "Physical/SIL/HIL/integration-test readiness link",
    "EPS/power-relevant V&V artifact/mechanism co-reporting",
    "No coded V&V artifact or pre-physical mechanism",
    "Generic/planned V&V linkage only",
]
VV_CODE_MAP: Dict[str, Tuple[str, ...]] = {
    "verification matrix": ("Requirements-to-model traceability or verification matrix",),
    "test cases": ("Test cases/procedures/V&V activity packages",),
    "test procedures": ("Test cases/procedures/V&V activity packages",),
    "simulation scenarios": ("Executable simulation or scenario analysis",),
    "acceptance criteria": ("Test cases/procedures/V&V activity packages",),
    "executable checks": (
        "Test cases/procedures/V&V activity packages",
        "Parametric/budget/constraint checks",
    ),
    "generated test artifacts": (
        "Test cases/procedures/V&V activity packages",
        "External tool or data-flow coupling for V&V",
    ),
    "SIL/HIL links": ("Physical/SIL/HIL/integration-test readiness link",),
    "automated tests": (
        "Test cases/procedures/V&V activity packages",
        "External tool or data-flow coupling for V&V",
    ),
    "requirements-in-the-loop": ("Requirements-to-model traceability or verification matrix",),
    "simulation-in-the-loop": ("Executable simulation or scenario analysis",),
    "parametric checks": ("Parametric/budget/constraint checks",),
    "model checking": (
        "Requirements-to-model traceability or verification matrix",
        "Test cases/procedures/V&V activity packages",
    ),
    "trade-study verification": (
        "Parametric/budget/constraint checks",
        "Executable simulation or scenario analysis",
    ),
    "virtual integration": ("External tool or data-flow coupling for V&V",),
    "links to hardware integration": ("Physical/SIL/HIL/integration-test readiness link",),
    "software integration": ("Physical/SIL/HIL/integration-test readiness link",),
    "flat-sat/testbed": ("Physical/SIL/HIL/integration-test readiness link",),
    "environmental test": ("Physical/SIL/HIL/integration-test readiness link",),
    "operational validation": ("Physical/SIL/HIL/integration-test readiness link",),
}

# Regression expectations are controlled values and statuses already present in
# the reviewed extractions. They prevent this display from silently recoding
# direct RQ3 fields or changing the retained derived counts.
VV_DIRECT_EXPECTED_COUNTS: Dict[str, Dict[str, int]] = {
    P_PREPHYSICAL: {
        "requirements-in-the-loop": 17,
        "simulation-in-the-loop": 15,
        "parametric checks": 19,
        "model checking": 0,
        "trade-study verification": 15,
        "virtual integration": 10,
        "not reported": 0,
        UNMAPPED: 0,
        UNASSIGNED_VALUE: 14,
    },
    P_VV_ARTIFACTS: {
        "verification matrix": 4,
        "test cases": 5,
        "test procedures": 6,
        "simulation scenarios": 15,
        "acceptance criteria": 10,
        "executable checks": 14,
        "generated test artifacts": 0,
        "SIL/HIL links": 2,
        "automated tests": 1,
        UNMAPPED: 0,
        UNASSIGNED_VALUE: 16,
    },
    P_TEST_READINESS: {
        "links to hardware integration": 6,
        "software integration": 8,
        "flat-sat/testbed": 0,
        "environmental test": 0,
        "operational validation": 4,
        "not reported": 0,
        UNMAPPED: 0,
        UNASSIGNED_VALUE: 30,
    },
}
VV_DIRECT_EXPECTED_STATUS_COUNTS: Dict[str, Dict[str, int]] = {
    P_PREPHYSICAL: {
        "coded": 26, "not_reported": 9, "not_applicable": 2,
        "none": 3, "uncertain": 0, UNASSIGNED_STATUS: 0,
    },
    P_VV_ARTIFACTS: {
        "coded": 24, "not_reported": 9, "not_applicable": 2,
        "none": 4, "uncertain": 1, UNASSIGNED_STATUS: 0,
    },
    P_TEST_READINESS: {
        "coded": 10, "not_reported": 29, "not_applicable": 1,
        "none": 0, "uncertain": 0, UNASSIGNED_STATUS: 0,
    },
}
VV_DERIVED_EXPECTED_COUNTS = {
    "Requirements-to-model traceability or verification matrix": 19,
    "Executable simulation or scenario analysis": 22,
    "Parametric/budget/constraint checks": 23,
    "Test cases/procedures/V&V activity packages": 21,
    "External tool or data-flow coupling for V&V": 11,
    "Physical/SIL/HIL/integration-test readiness link": 10,
    "EPS/power-relevant V&V artifact/mechanism co-reporting": 25,
    "No coded V&V artifact or pre-physical mechanism": 12,
    "Generic/planned V&V linkage only": 3,
}

GAP_FIELDS: List[Tuple[str, str]] = [
    ("gap_mapping.practical_implementation_pathway", "Practical implementation pathway"),
    ("gap_mapping.toolchain_fragmentation_interoperability", "Toolchain fragmentation/interoperability"),
    ("gap_mapping.lightweight_resource_constrained_tailoring", "Lightweight/resource-constrained tailoring"),
    (P_GOVERNANCE_GAP, "Governance/project deliverables/ROI/value"),
    ("gap_mapping.newspace_agile_distributed_rapid_iteration_alignment", "NewSpace/agile/distributed/rapid iteration"),
]

# Selected evidence-map membership is retained exactly rather than inferred
# from author names, titles, or prose. All values displayed for these reports
# are read afresh from controlled fields. The selection is not used for any
# corpus-wide count or decision. Display labels are concise title-derived aids;
# the CSV retains corpus IDs and short IDs for audit.
CURATED_LINEAGE_IDS = (
    "paper-0003", "paper-0001", "paper-0008", "paper-0004", "paper-0022",
    "paper-0016", "paper-0031", "paper-0002", "paper-0005", "paper-0015",
    "paper-0007", "paper-0013", "paper-0077", "paper-0011", "paper-0039",
    "paper-0014",
)
CURATED_EPS_IDS = ("paper-0026", "paper-0059")
CURATED_BOUNDARY_ID = "paper-0053"
CURATED_REFERENCE_LANE = "Reference-model lineage"
CURATED_EPS_LANE = "EPS-focused reports and protocol boundary"
CURATED_DISPLAY_LABELS = {
    "paper-0003": "RAX scenarios",
    "paper-0001": "Integrated simulation",
    "paper-0008": "Enterprise model",
    "paper-0004": "CRM interim 1",
    "paper-0022": "CRM concept application",
    "paper-0016": "CRM interim 2",
    "paper-0031": "CRM distribution",
    "paper-0002": "CubeSat behavior",
    "paper-0005": "CRM interim 3",
    "paper-0015": "CRM V&V",
    "paper-0007": "Technical measures",
    "paper-0013": "CRM interim 4",
    "paper-0077": "CRM interim 5",
    "paper-0011": "CSRM application",
    "paper-0039": "Standardized template",
    "paper-0014": "Mission engineering",
    "paper-0026": "Open-source EPS",
    "paper-0059": "Requirements-in-loop",
    "paper-0053": "Electrical architecture",
}

FIGURE_NAMES = (
    "prisma_flow",
    "eps_relevance_counts",
    "claim_evidence_by_outcome",
    "vv_linkage_counts",
    "gap_mapping_counts",
    "kaslow_eps_lineage_timeline",
    "model_maturity_by_eps_relevance",
    "eps_elements_modeled",
    "toolchain_mechanisms_limitations",
    "claim_evidence_anatomy",
    "lifecycle_ivv_heatmap",
)

EXISTING_CSV_NAMES = (
    "study_characteristics.csv",
    "eps_relevance_counts.csv",
    "approach_classification_counts.csv",
    "claim_evidence_by_outcome.csv",
    "vv_linkage_counts.csv",
    "gap_mapping_counts.csv",
    "generality_reuse_mechanism_counts.csv",
    "ivv_integration_level_counts.csv",
    "reliability_subtype_counts.csv",
    "top_value_claims.csv",
    "kaslow_eps_lineage_timeline.csv",
)
PLANNED_CSV_NAMES = (
    "pre_physical_verification_mechanism_counts.csv",
    "verification_validation_artifacts_counts.csv",
    "integration_test_readiness_counts.csv",
    "lifecycle_stage_counts.csv",
    "model_maturity_counts.csv",
    "model_maturity_by_eps_relevance.csv",
    "model_artifacts_counts.csv",
    "eps_elements_modeled_counts.csv",
    "interoperability_mechanisms_counts.csv",
    "toolchain_limitations_counts.csv",
    "claim_specificity_counts.csv",
    "evidence_type_counts.csv",
    "baseline_comparator_counts.csv",
    "lifecycle_by_ivv_integration_level.csv",
    "governance_roi_counts.csv",
)
ADDITIONAL_CSV_NAMES = (
    "claim_specificity_by_evidence_confidence.csv",
    "evidence_type_by_baseline_comparator.csv",
    "eps_elements_by_vv_artifact.csv",
    "field_coverage_status.csv",
)


class ValidationError(RuntimeError):
    """Raised when a source corpus no longer satisfies the registered schema."""


@dataclass
class FieldObservation:
    """One controlled field as represented for one report or one claim."""

    field_path: str
    status: str
    values: Tuple[str, ...]
    invalid_values: Tuple[str, ...]
    source: str
    present: bool


@dataclass
class ClaimRecord:
    corpus_id: str
    claim_id: str
    claim_id_source: str
    claim_index: int
    claim_ref: str
    fields: Dict[str, FieldObservation]
    raw: Mapping[str, Any]


@dataclass
class StudyRecord:
    corpus_id: str
    raw: Mapping[str, Any]
    extraction: Mapping[str, Any]
    fields: Dict[str, FieldObservation]
    claims: List[ClaimRecord]

    @property
    def year(self) -> int:
        value = self.raw.get("year", self.extraction.get("year", 9999))
        try:
            return int(value)
        except (TypeError, ValueError):
            return 9999


# ---------------------------------------------------------------------------
# Source loading and validation


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str("" if value is None else value)).strip()


def unique_ordered(values: Iterable[str]) -> Tuple[str, ...]:
    seen: set[str] = set()
    ordered: List[str] = []
    for value in values:
        value = clean_text(value)
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return tuple(ordered)


def unwrap_values(value: Any) -> Tuple[str, ...]:
    """Normalize scalar/list/typed-wrapper values without splitting labels.

    ``values``, ``value``, ``label``, ``classification``, and ``rating`` are
    the wrapper forms present in the extraction family.  This intentionally
    never tokenizes a string on commas or semicolons: doing so would transform
    an uncontrolled prose value into invented controlled labels.
    """
    if value is None:
        return ()
    if isinstance(value, Mapping):
        for key in ("values", "value", "label", "classification", "rating"):
            if key in value:
                return unwrap_values(value[key])
        return ()
    if isinstance(value, (list, tuple)):
        flattened: List[str] = []
        for item in value:
            flattened.extend(unwrap_values(item))
        return unique_ordered(flattened)
    text = clean_text(value)
    return (text,) if text else ()


def wrapper_status(value: Any) -> str:
    if isinstance(value, Mapping) and "status" in value:
        return clean_text(value.get("status"))
    return ""


def codebook_allowed(codebook: Mapping[str, Any], field_path: str) -> Tuple[str, ...]:
    return tuple(codebook["controlled_fields"][field_path]["allowed_values"])


def status_column_name(status: str) -> str:
    """Return a stable CSV-safe status column name."""
    return "status_" + re.sub(r"[^A-Za-z0-9]+", "_", status).strip("_")


def status_columns(status_order: Sequence[str]) -> List[str]:
    return [status_column_name(status) for status in (*status_order, UNASSIGNED_STATUS)]


def status_dict(observations: Sequence[FieldObservation], status_order: Sequence[str]) -> Dict[str, int]:
    counts = Counter(obs.status for obs in observations)
    return {
        status_column_name(status): counts.get(status, 0)
        for status in (*status_order, UNASSIGNED_STATUS)
    }


def validate_codebook(codebook: Mapping[str, Any], index: Mapping[str, Any]) -> None:
    if codebook.get("codebook_version") != EXPECTED_CODEBOOK_VERSION:
        raise ValidationError(
            f"codebook_version must be {EXPECTED_CODEBOOK_VERSION!r}; "
            f"found {codebook.get('codebook_version')!r}"
        )
    if index.get("codebook_version") != codebook.get("codebook_version"):
        raise ValidationError(
            "extraction.json codebook_version does not match extraction_codebook.json: "
            f"{index.get('codebook_version')!r} != {codebook.get('codebook_version')!r}"
        )
    statuses = codebook.get("status_values")
    if not isinstance(statuses, list) or not statuses:
        raise ValidationError("extraction_codebook.json has no non-empty status_values list")
    if len(statuses) != len(set(statuses)):
        raise ValidationError("extraction_codebook.json status_values contains duplicates")
    fields = codebook.get("controlled_fields")
    if not isinstance(fields, Mapping) or not fields:
        raise ValidationError("extraction_codebook.json has no controlled_fields mapping")
    for path, spec in fields.items():
        if spec.get("type") not in {"single_select", "multi_select", "ordinal"}:
            raise ValidationError(f"Unsupported controlled field type at {path}: {spec.get('type')!r}")
        allowed = spec.get("allowed_values")
        if not isinstance(allowed, list) or not allowed:
            raise ValidationError(f"Missing allowed_values at {path}")
        if len(allowed) != len(set(allowed)):
            raise ValidationError(f"Duplicate allowed_values at {path}")
    missing_claim_paths = set(CLAIM_FIELD_ALIASES) - set(fields)
    if missing_claim_paths:
        raise ValidationError(f"Codebook is missing canonical claim fields: {sorted(missing_claim_paths)}")


def make_observation(
    *,
    field_path: str,
    raw_value: Any,
    source: str,
    present: bool,
    codebook: Mapping[str, Any],
    explicit_status: str = "",
    enforce_cardinality: bool,
    allow_invalid_values: bool,
    record_ref: str,
) -> FieldObservation:
    """Normalize and validate a controlled field without recoding invalid labels."""
    status_order = tuple(codebook["status_values"])
    values = unwrap_values(raw_value)
    status = explicit_status or wrapper_status(raw_value)
    if status:
        if status not in status_order:
            raise ValidationError(
                f"{record_ref}: {field_path} has invalid status {status!r}; "
                f"expected one of {status_order!r}"
            )
    elif values:
        # An unwrapped selected label is still an explicit value, but its status
        # was not separately serialized.  Retain it as coded rather than
        # silently turning it into a not_reported/none status.
        status = "coded"
    else:
        status = UNASSIGNED_STATUS

    spec = codebook["controlled_fields"][field_path]
    if enforce_cardinality and spec["type"] in {"single_select", "ordinal"} and len(values) > 1:
        raise ValidationError(
            f"{record_ref}: {field_path} is {spec['type']} but has {len(values)} values: {values!r}"
        )
    allowed = set(spec["allowed_values"])
    valid_values = tuple(value for value in values if value in allowed)
    invalid_values = tuple(value for value in values if value not in allowed)
    if invalid_values and not allow_invalid_values:
        raise ValidationError(
            f"{record_ref}: {field_path} has non-codebook value(s) {invalid_values!r}"
        )
    return FieldObservation(
        field_path=field_path,
        status=status,
        values=unique_ordered(valid_values),
        invalid_values=unique_ordered(invalid_values),
        source=source,
        present=present,
    )


def claim_status_sibling(claim: Mapping[str, Any], field_path: str) -> str:
    for key in CLAIM_STATUS_SIBLINGS.get(field_path, ()):
        if key in claim:
            status = clean_text(claim[key])
            if status:
                return status
    return ""


def canonical_claim_observation(
    claim: Mapping[str, Any],
    field_path: str,
    codebook: Mapping[str, Any],
    claim_ref: str,
) -> FieldObservation:
    aliases = CLAIM_FIELD_ALIASES[field_path]
    source = next((alias for alias in aliases if alias in claim), "")
    if not source:
        raise ValidationError(
            f"{claim_ref}: missing canonical claim field {field_path}; accepted keys are {aliases!r}"
        )
    raw_value = claim[source]
    explicit_status = wrapper_status(raw_value) or claim_status_sibling(claim, field_path)
    return make_observation(
        field_path=field_path,
        raw_value=raw_value,
        source=source,
        present=True,
        codebook=codebook,
        explicit_status=explicit_status,
        enforce_cardinality=True,
        allow_invalid_values=True,
        record_ref=claim_ref,
    )


def claim_identifier(claim: Mapping[str, Any], index: int) -> Tuple[str, str]:
    value = clean_text(claim.get("claim_id"))
    if value:
        return value, "claim_id"
    # ``id`` is a legacy identifier field, not a value classification.  It is
    # normalized solely to preserve a stable reference before 1-based fallback.
    value = clean_text(claim.get("id"))
    if value:
        return value, "id alias"
    return str(index), "1-based index fallback"


def validate_and_load_studies(codebook: Mapping[str, Any], index: Mapping[str, Any]) -> List[StudyRecord]:
    paths = sorted(EXTRACTIONS_DIR.glob("paper-*.json"))
    if not paths:
        raise ValidationError(f"No extraction JSON files found in {EXTRACTIONS_DIR}")

    index_studies = index.get("studies")
    if not isinstance(index_studies, list):
        raise ValidationError("extraction.json has no studies list for ID-coverage validation")
    index_ids = [clean_text(item.get("corpus_id")) for item in index_studies if isinstance(item, Mapping)]
    file_ids = [path.stem for path in paths]
    if len(index_ids) != len(set(index_ids)):
        raise ValidationError("extraction.json studies contains duplicate corpus IDs")
    if set(index_ids) != set(file_ids):
        raise ValidationError(
            "Exact extraction ID coverage failed: "
            f"missing files={sorted(set(index_ids) - set(file_ids))}; "
            f"unexpected files={sorted(set(file_ids) - set(index_ids))}"
        )
    if int(index.get("study_count", -1)) != len(paths):
        raise ValidationError(
            f"extraction.json study_count={index.get('study_count')!r}, but found {len(paths)} extraction files"
        )

    fields_spec = codebook["controlled_fields"]
    expected_field_paths = set(fields_spec)
    studies: List[StudyRecord] = []
    for path in paths:
        raw = read_json(path)
        corpus_id = clean_text(raw.get("corpus_id"))
        if corpus_id != path.stem:
            raise ValidationError(f"{path}: top-level corpus_id {corpus_id!r} does not match filename")
        extraction = raw.get("extraction", raw)
        if not isinstance(extraction, Mapping):
            raise ValidationError(f"{path}: extraction must be an object")
        bib = extraction.get("bibliographic_review_management", {})
        nested_id = clean_text(bib.get("corpus_id")) if isinstance(bib, Mapping) else ""
        if nested_id and nested_id != corpus_id:
            raise ValidationError(f"{path}: nested corpus_id {nested_id!r} does not match {corpus_id!r}")

        summary = raw.get("structured_code_summary")
        if not isinstance(summary, Mapping):
            raise ValidationError(f"{path}: structured_code_summary is missing or invalid")
        missing = expected_field_paths - set(summary)
        extra = set(summary) - expected_field_paths
        if missing or extra:
            raise ValidationError(
                f"{path}: structured-code fields differ from codebook; "
                f"missing={sorted(missing)}, extra={sorted(extra)}"
            )

        observations: Dict[str, FieldObservation] = {}
        for field_path in fields_spec:
            entry = summary[field_path]
            if not isinstance(entry, Mapping):
                raise ValidationError(f"{path}: summary entry {field_path} is not an object")
            # Claim-summary values are intentionally study-level aggregates of
            # several claims.  Thus single-select cardinality is validated in
            # canonical claim records below, not on this aggregate list.
            enforce = not field_path.startswith(CLAIM_PREFIX)
            observations[field_path] = make_observation(
                field_path=field_path,
                raw_value=entry,
                source="structured_code_summary",
                present=True,
                codebook=codebook,
                explicit_status=wrapper_status(entry),
                enforce_cardinality=enforce,
                allow_invalid_values=False,
                record_ref=corpus_id,
            )

        raw_claims = extraction.get("claimed_outcomes_value_mechanisms_evidence")
        if not isinstance(raw_claims, list):
            raise ValidationError(f"{path}: claimed_outcomes_value_mechanisms_evidence must be a list")
        claims: List[ClaimRecord] = []
        seen_refs: set[str] = set()
        for claim_index, raw_claim in enumerate(raw_claims, start=1):
            if not isinstance(raw_claim, Mapping):
                raise ValidationError(f"{path}: claim {claim_index} is not an object")
            claim_id, claim_id_source = claim_identifier(raw_claim, claim_index)
            claim_ref = f"{corpus_id}:{claim_id}"
            if claim_ref in seen_refs:
                raise ValidationError(f"{path}: duplicate stable claim reference {claim_ref!r}")
            seen_refs.add(claim_ref)
            claim_fields = {
                field_path: canonical_claim_observation(raw_claim, field_path, codebook, claim_ref)
                for field_path in CLAIM_FIELD_ALIASES
            }
            claims.append(
                ClaimRecord(
                    corpus_id=corpus_id,
                    claim_id=claim_id,
                    claim_id_source=claim_id_source,
                    claim_index=claim_index,
                    claim_ref=claim_ref,
                    fields=claim_fields,
                    raw=raw_claim,
                )
            )
        studies.append(StudyRecord(corpus_id, raw, extraction, observations, claims))

    return sorted(studies, key=lambda study: (study.year, study.corpus_id))


def validate_index_quality_statistics(
    index: Mapping[str, Any],
    studies: Sequence[StudyRecord],
) -> None:
    """Reject a stale extraction-index quality summary.

    The per-report controlled summaries are the source of truth.  Checking the
    convenience statistics here prevents manuscript and index totals from
    silently diverging after extraction-schema repairs.
    """
    totals: List[float] = []
    for study in studies:
        total = 0.0
        for field_path, observation in study.fields.items():
            if field_path.startswith("quality_checklist.") and observation.values:
                total += QUALITY_SCORE.get(observation.values[0], 0.0)
        totals.append(total)
    if not totals:
        raise ValidationError("No quality totals could be computed from controlled summaries")

    declared = index.get("statistics", {}).get("quality_score_total", {})
    if not isinstance(declared, Mapping):
        raise ValidationError("extraction.json has no quality_score_total statistics")
    expected_counts = {
        f"{score:.1f}": count
        for score, count in sorted(Counter(totals).items())
    }
    declared_counts = {
        clean_text(score): int(count)
        for score, count in declared.get("counts", {}).items()
    } if isinstance(declared.get("counts"), Mapping) else {}
    expected = {
        "min": min(totals),
        "mean": sum(totals) / len(totals),
        "max": max(totals),
    }
    numeric_mismatch = any(
        not math.isclose(float(declared.get(key, math.nan)), value, rel_tol=0.0, abs_tol=1e-9)
        for key, value in expected.items()
    )
    if numeric_mismatch or declared_counts != expected_counts:
        raise ValidationError(
            "extraction.json quality statistics are stale: "
            f"declared={dict(declared)!r}; expected={expected | {'counts': expected_counts}!r}"
        )


# ---------------------------------------------------------------------------
# Controlled aggregation utilities


def all_claims(studies: Sequence[StudyRecord]) -> List[ClaimRecord]:
    return [claim for study in studies for claim in study.claims]


def category_memberships(observation: FieldObservation) -> Tuple[str, ...]:
    """Return the explicit controlled/QA memberships for one record.

    Multi-select fields contribute each selected controlled label once.  Invalid
    values are never replaced with a guessed label; they contribute only the
    explicit QA class.  An empty record contributes an explicit unassigned class.
    """
    categories: List[str] = list(observation.values)
    if observation.invalid_values:
        categories.append(UNMAPPED)
    if not categories:
        categories.append(UNASSIGNED_VALUE)
    return unique_ordered(categories)


def single_category(observation: FieldObservation) -> str:
    categories = category_memberships(observation)
    if len(categories) != 1:
        # Canonical single-select cardinality is validated when loading.  This
        # protects against accidental use of a multi-label field as single.
        raise ValidationError(
            f"Expected one category for {observation.field_path}, found {categories!r}"
        )
    return categories[0]


def record_identifier(record: StudyRecord | ClaimRecord) -> str:
    return record.corpus_id if isinstance(record, StudyRecord) else record.claim_ref


def observations_for_studies(studies: Sequence[StudyRecord], field_path: str) -> List[Tuple[str, FieldObservation]]:
    return [(study.corpus_id, study.fields[field_path]) for study in studies]


def observations_for_claims(claims: Sequence[ClaimRecord], field_path: str) -> List[Tuple[str, FieldObservation]]:
    return [(claim.claim_ref, claim.fields[field_path]) for claim in claims]


def count_rows(
    observations: Sequence[Tuple[str, FieldObservation]],
    field_path: str,
    codebook: Mapping[str, Any],
    *,
    unit: str,
    id_column: str,
) -> List[dict]:
    """Count unique report/claim memberships in codebook order, including zeroes."""
    allowed = list(codebook_allowed(codebook, field_path))
    categories = [*allowed, UNMAPPED, UNASSIGNED_VALUE]
    members: Dict[str, set[str]] = {category: set() for category in categories}
    invalid_records: set[str] = set()
    unassigned_records: set[str] = set()
    raw_status_observations = [observation for _, observation in observations]
    for record_id, observation in observations:
        if observation.invalid_values:
            invalid_records.add(record_id)
        if not observation.values and not observation.invalid_values:
            unassigned_records.add(record_id)
        for category in category_memberships(observation):
            members[category].add(record_id)
    denominator = len(observations)
    coverage = status_dict(raw_status_observations, codebook["status_values"])
    rows: List[dict] = []
    for category in categories:
        count = len(members[category])
        row = {
            "category": category,
            "count": count,
            "unit": unit,
            "denominator": denominator,
            "percent_of_denominator": f"{(100 * count / denominator) if denominator else 0:.1f}",
            **coverage,
            "unmapped_invalid_records": len(invalid_records),
            "unassigned_value_records": len(unassigned_records),
            id_column: "; ".join(sorted(members[category])),
        }
        rows.append(row)
    return rows


def count_headers(id_column: str, status_order: Sequence[str]) -> List[str]:
    return [
        "category",
        "count",
        "unit",
        "denominator",
        "percent_of_denominator",
        *status_columns(status_order),
        "unmapped_invalid_records",
        "unassigned_value_records",
        id_column,
    ]


def matrix_rows(
    observations: Sequence[Tuple[str, FieldObservation, FieldObservation]],
    field_a: str,
    field_b: str,
    codebook: Mapping[str, Any],
    *,
    a_column: str,
    b_column: str,
    unit: str,
    id_column: str,
) -> List[dict]:
    """Create a complete controlled-code matrix of unique record memberships."""
    categories_a = [*codebook_allowed(codebook, field_a), UNMAPPED, UNASSIGNED_VALUE]
    categories_b = [*codebook_allowed(codebook, field_b), UNMAPPED, UNASSIGNED_VALUE]
    members: Dict[Tuple[str, str], set[str]] = {
        (a, b): set() for a in categories_a for b in categories_b
    }
    observations_a = [a for _, a, _ in observations]
    observations_b = [b for _, _, b in observations]
    for record_id, observation_a, observation_b in observations:
        for category_a in category_memberships(observation_a):
            for category_b in category_memberships(observation_b):
                members[(category_a, category_b)].add(record_id)
    denominator = len(observations)
    coverage_a = {
        f"{a_column}_{key}": value
        for key, value in status_dict(observations_a, codebook["status_values"]).items()
    }
    coverage_b = {
        f"{b_column}_{key}": value
        for key, value in status_dict(observations_b, codebook["status_values"]).items()
    }
    rows: List[dict] = []
    for category_a in categories_a:
        for category_b in categories_b:
            count = len(members[(category_a, category_b)])
            rows.append(
                {
                    a_column: category_a,
                    b_column: category_b,
                    "count": count,
                    "unit": unit,
                    "denominator": denominator,
                    "percent_of_denominator": f"{(100 * count / denominator) if denominator else 0:.1f}",
                    **coverage_a,
                    **coverage_b,
                    id_column: "; ".join(sorted(members[(category_a, category_b)])),
                }
            )
    return rows


def matrix_headers(
    a_column: str,
    b_column: str,
    id_column: str,
    status_order: Sequence[str],
) -> List[str]:
    status = status_columns(status_order)
    return [
        a_column,
        b_column,
        "count",
        "unit",
        "denominator",
        "percent_of_denominator",
        *[f"{a_column}_{column}" for column in status],
        *[f"{b_column}_{column}" for column in status],
        id_column,
    ]


def metadata_text(value: Any) -> str:
    if isinstance(value, Mapping):
        for key in ("value", "text", "title", "name"):
            if key in value:
                return metadata_text(value[key])
        return ""
    return clean_text(value)


def study_bibliography(study: StudyRecord) -> Mapping[str, Any]:
    section = study.extraction.get("bibliographic_review_management", {})
    return section if isinstance(section, Mapping) else {}


def study_title(study: StudyRecord) -> str:
    bib = study_bibliography(study)
    citation = bib.get("citation", {})
    if not isinstance(citation, Mapping):
        citation = {}
    return metadata_text(bib.get("title") or citation.get("title") or study.corpus_id)


def study_authors(study: StudyRecord) -> str:
    bib = study_bibliography(study)
    citation = bib.get("citation", {})
    if not isinstance(citation, Mapping):
        citation = {}
    authors = bib.get("authors") or citation.get("authors") or []
    if isinstance(authors, list):
        values: List[str] = []
        for author in authors:
            if isinstance(author, Mapping):
                values.append(metadata_text(author.get("name") or author.get("value")))
            else:
                values.append(metadata_text(author))
        return "; ".join(value for value in values if value)
    return metadata_text(authors)


def study_field_text(study: StudyRecord, field_path: str) -> str:
    return "; ".join(study.fields[field_path].values)


def claim_text(claim: ClaimRecord) -> str:
    for key in ("claim_text_or_paraphrase", "claim_text", "claim", "claim_paraphrase"):
        if key in claim.raw:
            return clean_text(claim.raw[key])
    return ""


def evidence_text(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(filter(None, (evidence_text(item) for item in value)))
    if isinstance(value, Mapping):
        quote = clean_text(value.get("quote") or value.get("evidence_quote") or value.get("text"))
        location = clean_text(value.get("location") or value.get("source"))
        if quote and location:
            return f"{location}: {quote}"
        return quote or location
    return clean_text(value)


def claim_evidence_source(claim: ClaimRecord) -> str:
    return evidence_text(
        claim.raw.get("evidence_source")
        or claim.raw.get("quote_location")
        or claim.raw.get("quote_or_location")
        or claim.raw.get("evidence_source_quote_location")
    )


def claim_direct_quote(claim: ClaimRecord) -> str:
    return clean_text(
        claim.raw.get("direct_quote")
        or claim.raw.get("evidence_quote")
        or claim.raw.get("quote")
        or claim_evidence_source(claim)
        or ""
    )


def field_value_count(rows: Sequence[Mapping[str, Any]], category: str) -> int:
    for row in rows:
        if row.get("category") == category:
            return int(row.get("count", 0))
    return 0


def status_coverage_text(observations: Sequence[FieldObservation], status_order: Sequence[str]) -> str:
    counts = Counter(obs.status for obs in observations)
    values = [f"{status}={counts.get(status, 0)}" for status in (*status_order, UNASSIGNED_STATUS)]
    return "; ".join(values)


# ---------------------------------------------------------------------------
# Artifact data construction


def study_characteristic_rows(studies: Sequence[StudyRecord], codebook: Mapping[str, Any]) -> List[dict]:
    confidence_allowed = codebook_allowed(codebook, P_CLAIM_CONFIDENCE)
    rows: List[dict] = []
    for study in studies:
        quality_total = 0.0
        for path in codebook["controlled_fields"]:
            if path.startswith("quality_checklist."):
                values = study.fields[path].values
                if values:
                    quality_total += QUALITY_SCORE.get(values[0], 0.0)
        confidence_counts = Counter(
            single_category(claim.fields[P_CLAIM_CONFIDENCE]) for claim in study.claims
        )
        bib = study_bibliography(study)
        citation = bib.get("citation", {}) if isinstance(bib.get("citation"), Mapping) else {}
        rows.append(
            {
                "corpus_id": study.corpus_id,
                "tier": study_field_text(study, P_TIER),
                "year": study.year if study.year != 9999 else "",
                "title": study_title(study),
                "authors": study_authors(study),
                "venue": metadata_text(bib.get("venue") or citation.get("venue")),
                "venue_type": metadata_text(bib.get("venue_type") or citation.get("venue_type")),
                "doi_or_url": metadata_text(
                    bib.get("doi_or_url") or bib.get("doi") or bib.get("url") or citation.get("doi") or citation.get("url")
                ),
                "quality_total_score": f"{quality_total:.1f}",
                "quality_normalized_score": f"{quality_total / 8.0:.3f}",
                "RQ1_relevance": study_field_text(study, P_RQ1),
                "RQ2_relevance": study_field_text(study, P_RQ2),
                "RQ3_relevance": study_field_text(study, P_RQ3),
                "eps_relevance": study_field_text(study, P_EPS),
                "eps_relevance_status": study.fields[P_EPS].status,
                "approach_classification": study_field_text(study, P_APPROACH),
                "model_maturity": study_field_text(study, P_MATURITY),
                "model_maturity_status": study.fields[P_MATURITY].status,
                "lifecycle_stage": study_field_text(study, P_LIFECYCLE),
                "lifecycle_stage_status": study.fields[P_LIFECYCLE].status,
                "development_context": study_field_text(study, P_DEVELOPMENT_CONTEXT),
                "development_context_status": study.fields[P_DEVELOPMENT_CONTEXT].status,
                "claim_count": len(study.claims),
                "unsupported_claims": confidence_counts.get("Unsupported", 0),
                "weak_claims": confidence_counts.get("Weak", 0),
                "moderate_claims": confidence_counts.get("Moderate", 0),
                "strong_claims": confidence_counts.get("Strong", 0),
                "unmapped_invalid_confidence_claims": confidence_counts.get(UNMAPPED, 0),
                "unassigned_confidence_claims": confidence_counts.get(UNASSIGNED_VALUE, 0),
                "extraction_confidence": study_field_text(study, P_EXTRACTION_CONFIDENCE),
            }
        )
    return rows


def outcome_domains_for_claim(claim: ClaimRecord) -> Tuple[str, ...]:
    observation = claim.fields[P_CLAIM_OUTCOME]
    domains: List[str] = []
    for value in observation.values:
        # A complete map is validated below so unmapped codebook labels cannot
        # drift into an inferred domain.
        domains.extend(OUTCOME_DOMAIN_MAP[value])
    if observation.invalid_values:
        domains.append(UNMAPPED)
    if not domains:
        domains.append(UNASSIGNED_VALUE)
    return unique_ordered(domains)


def validate_outcome_domain_map(codebook: Mapping[str, Any]) -> None:
    allowed = set(codebook_allowed(codebook, P_CLAIM_OUTCOME))
    missing = allowed - set(OUTCOME_DOMAIN_MAP)
    extra = set(OUTCOME_DOMAIN_MAP) - allowed
    if missing or extra:
        raise ValidationError(
            f"Controlled outcome-domain map drifted: missing={sorted(missing)}, extra={sorted(extra)}"
        )


def claim_evidence_rows(studies: Sequence[StudyRecord], codebook: Mapping[str, Any]) -> Tuple[List[dict], List[dict]]:
    claims = all_claims(studies)
    confidence_categories = [*codebook_allowed(codebook, P_CLAIM_CONFIDENCE), UNMAPPED, UNASSIGNED_VALUE]
    counts: Dict[str, Counter] = {domain: Counter() for domain in OUTCOME_DOMAIN_ORDER}
    domain_claims: Dict[str, set[str]] = {domain: set() for domain in OUTCOME_DOMAIN_ORDER}
    domain_studies: Dict[str, set[str]] = {domain: set() for domain in OUTCOME_DOMAIN_ORDER}
    domain_eps_or_power: Dict[str, set[str]] = {domain: set() for domain in OUTCOME_DOMAIN_ORDER}
    by_study = {study.corpus_id: study for study in studies}

    for claim in claims:
        confidence = single_category(claim.fields[P_CLAIM_CONFIDENCE])
        report_eps = set(by_study[claim.corpus_id].fields[P_EPS].values)
        claim_specificity = single_category(claim.fields[P_CLAIM_SPECIFICITY])
        eps_or_power = (
            claim_specificity == "EPS-specific"
            or bool(report_eps & {"EPS-specific", "power-budget/electrical-architecture"})
        )
        for domain in outcome_domains_for_claim(claim):
            counts[domain][confidence] += 1
            domain_claims[domain].add(claim.claim_ref)
            domain_studies[domain].add(claim.corpus_id)
            if eps_or_power:
                domain_eps_or_power[domain].add(claim.claim_ref)

    rows: List[dict] = []
    for domain in OUTCOME_DOMAIN_ORDER:
        confidence_counts = counts[domain]
        total = sum(confidence_counts.values())
        rows.append(
            {
                "outcome_domain": domain,
                "total_claim_domain_memberships": total,
                "unsupported": confidence_counts.get("Unsupported", 0),
                "weak": confidence_counts.get("Weak", 0),
                "moderate": confidence_counts.get("Moderate", 0),
                "strong": confidence_counts.get("Strong", 0),
                "unmapped_invalid": confidence_counts.get(UNMAPPED, 0),
                "unassigned": confidence_counts.get(UNASSIGNED_VALUE, 0),
                "unit": "claim-domain membership (unique nested claim)",
                "denominator_claims": len(claims),
                "study_count": len(domain_studies[domain]),
                "eps_specific_or_power_relevant_claims": len(domain_eps_or_power[domain]),
                "study_ids": "; ".join(sorted(domain_studies[domain])),
                "claim_refs": "; ".join(sorted(domain_claims[domain])),
            }
        )

    # Preserve the old top-claim artifact without constructing a heuristic value
    # score.  It is a deterministic list of all controlled Moderate/Strong claims
    # ordered by confidence then stable claim reference.
    confidence_rank = {"Strong": 0, "Moderate": 1}
    selected = [
        claim for claim in claims
        if single_category(claim.fields[P_CLAIM_CONFIDENCE]) in confidence_rank
    ]
    selected.sort(key=lambda claim: (confidence_rank[single_category(claim.fields[P_CLAIM_CONFIDENCE])], claim.claim_ref))
    top_rows: List[dict] = []
    for rank, claim in enumerate(selected, start=1):
        top_rows.append(
            {
                "rank": rank,
                "claim_ref": claim.claim_ref,
                "study_id": claim.corpus_id,
                "claim_id": claim.claim_id,
                "claim_id_source": claim.claim_id_source,
                "claim_index": claim.claim_index,
                "year": by_study[claim.corpus_id].year,
                "title": study_title(by_study[claim.corpus_id]),
                "claim": claim_text(claim),
                "outcome_domain": "; ".join(outcome_domains_for_claim(claim)),
                "original_outcome_category": "; ".join(category_memberships(claim.fields[P_CLAIM_OUTCOME])),
                "specificity": single_category(claim.fields[P_CLAIM_SPECIFICITY]),
                "evidence_type": "; ".join(category_memberships(claim.fields[P_CLAIM_EVIDENCE_TYPE])),
                "baseline_comparator": single_category(claim.fields[P_CLAIM_BASELINE]),
                "evidence_confidence": single_category(claim.fields[P_CLAIM_CONFIDENCE]),
                "evidence_source": claim_evidence_source(claim),
                "direct_quote": claim_direct_quote(claim),
            }
        )
    return rows, top_rows


def vv_derived_values(observation: FieldObservation) -> Tuple[str, ...]:
    """Return values eligible for the derived mixed-source V&V categories.

    The derived map is intentionally stricter than general field coverage: a
    selected label enters it only when its source field is ``coded``. The
    codebook's literal ``not reported`` is a status-like placeholder, not a
    V&V artifact, pre-physical mechanism, or readiness link, even if it is
    serialized in a selected-value wrapper.
    """
    if observation.status != "coded":
        return ()
    return tuple(value for value in observation.values if value != "not reported")


def validate_vv_status_semantics(codebook: Mapping[str, Any]) -> None:
    """Guard against status-like V&V values creating derived memberships."""
    literal = "not reported"
    if literal not in codebook_allowed(codebook, P_PREPHYSICAL):
        raise ValidationError("V&V semantics check requires the controlled 'not reported' literal")
    for status in codebook["status_values"]:
        if status == "coded":
            continue
        observation = FieldObservation(
            field_path=P_PREPHYSICAL,
            status=status,
            values=("simulation-in-the-loop", literal),
            invalid_values=(),
            source="internal V&V status-semantics check",
            present=True,
        )
        if vv_derived_values(observation):
            raise ValidationError(
                f"Non-coded V&V values under status {status!r} entered the derived mixed-source V&V path"
            )
    coded_literal = FieldObservation(
        field_path=P_PREPHYSICAL,
        status="coded",
        values=(literal,),
        invalid_values=(),
        source="internal V&V status-semantics check",
        present=True,
    )
    if vv_derived_values(coded_literal):
        raise ValidationError("The V&V 'not reported' literal entered the derived mixed-source V&V path")


def vv_linkage_rows(studies: Sequence[StudyRecord], codebook: Mapping[str, Any]) -> List[dict]:
    members: Dict[str, set[str]] = {category: set() for category in VV_LINKAGE_ORDER}
    for study in studies:
        categories: set[str] = set()
        prephysical_values = vv_derived_values(study.fields[P_PREPHYSICAL])
        for path in (P_VV_ARTIFACTS, P_PREPHYSICAL):
            values = prephysical_values if path == P_PREPHYSICAL else vv_derived_values(study.fields[path])
            for value in values:
                categories.update(VV_CODE_MAP.get(value, ()))
        for value in vv_derived_values(study.fields[P_TEST_READINESS]):
            categories.update(VV_CODE_MAP.get(value, ()))
        if prephysical_values and set(study.fields[P_EPS].values) & {
            "EPS-specific", "power-budget/electrical-architecture", "EPS-adjacent"
        }:
            categories.add("EPS/power-relevant V&V artifact/mechanism co-reporting")
        if not any(vv_derived_values(study.fields[path]) for path in (P_VV_ARTIFACTS, P_PREPHYSICAL)):
            categories.add("No coded V&V artifact or pre-physical mechanism")
            if set(study.fields[P_RQ3].values) & {"partial", "high"}:
                categories.add("Generic/planned V&V linkage only")
        for category in categories:
            members[category].add(study.corpus_id)

    source_observations = [
        study.fields[path]
        for study in studies
        for path in (P_VV_ARTIFACTS, P_PREPHYSICAL, P_TEST_READINESS)
    ]
    source_statuses = status_coverage_text(source_observations, codebook["status_values"])
    return [
        {
            "vv_linkage_category": category,
            "count": len(members[category]),
            "unit": "derived study membership (unique report; mixed-source union)",
            "denominator": len(studies),
            "percent_of_denominator": f"{100 * len(members[category]) / len(studies):.1f}",
            "derivation_basis": VV_DERIVATION_BASIS,
            "source_field_statuses": source_statuses,
            "study_ids": "; ".join(sorted(members[category])),
        }
        for category in VV_LINKAGE_ORDER
    ]


def gap_mapping_rows(studies: Sequence[StudyRecord], codebook: Mapping[str, Any]) -> List[dict]:
    rows: List[dict] = []
    for field_path, label in GAP_FIELDS:
        field_rows = count_rows(
            observations_for_studies(studies, field_path),
            field_path,
            codebook,
            unit="study membership (unique report)",
            id_column="study_ids",
        )
        for row in field_rows:
            rows.append(
                {
                    "gap_key": field_path.rsplit(".", 1)[-1],
                    "gap_label": label,
                    "classification": row.pop("category"),
                    **row,
                }
            )
    return rows


def governance_roi_rows(studies: Sequence[StudyRecord], codebook: Mapping[str, Any]) -> List[dict]:
    groups = [
        ("model governance strategy", P_GOVERNANCE),
        ("ROI/value-realization evidence", P_ROI),
        ("governance gap classification (all-study mapping)", P_GOVERNANCE_GAP),
    ]
    rows: List[dict] = []
    for group, field_path in groups:
        for row in count_rows(
            observations_for_studies(studies, field_path),
            field_path,
            codebook,
            unit="study membership (unique report)",
            id_column="study_ids",
        ):
            rows.append(
                {
                    "measure_group": group,
                    "source_field": field_path,
                    **row,
                }
            )
    return rows


def baseline_availability_category(observation: FieldObservation) -> str:
    """Controlled-code-only grouping used in the claim-anatomy figure."""
    category = single_category(observation)
    if category in {
        "previous document-centric process",
        "manual analysis",
        "alternative toolchain",
        "previous mission",
    }:
        return "comparator recorded"
    if category == "none":
        return "explicitly none"
    if category == "not reported":
        return "not reported"
    if category == UNMAPPED:
        return UNMAPPED
    if category == UNASSIGNED_VALUE:
        return UNASSIGNED_VALUE
    raise ValidationError(f"Unexpected controlled baseline category {category!r}")


def evidence_type_by_baseline_availability(claims: Sequence[ClaimRecord], codebook: Mapping[str, Any]) -> Tuple[List[str], List[str], Dict[Tuple[str, str], int]]:
    evidence_types = [*codebook_allowed(codebook, P_CLAIM_EVIDENCE_TYPE), UNMAPPED, UNASSIGNED_VALUE]
    availability = ["comparator recorded", "explicitly none", "not reported", UNMAPPED, UNASSIGNED_VALUE]
    values: Dict[Tuple[str, str], int] = {(evidence, baseline): 0 for evidence in evidence_types for baseline in availability}
    for claim in claims:
        baseline = baseline_availability_category(claim.fields[P_CLAIM_BASELINE])
        for evidence in category_memberships(claim.fields[P_CLAIM_EVIDENCE_TYPE]):
            values[(evidence, baseline)] += 1
    return evidence_types, availability, values


def curated_lineage_rows(studies: Sequence[StudyRecord]) -> List[dict]:
    by_id = {study.corpus_id: study for study in studies}
    selected = [*CURATED_LINEAGE_IDS, *CURATED_EPS_IDS, CURATED_BOUNDARY_ID]
    if len(selected) != len(set(selected)):
        raise ValidationError("Selected evidence-map membership contains duplicate corpus IDs")
    missing = [corpus_id for corpus_id in selected if corpus_id not in by_id]
    if missing:
        raise ValidationError(f"Selected evidence map references missing reports: {missing}")
    label_ids = set(CURATED_DISPLAY_LABELS)
    selected_ids = set(selected)
    if label_ids != selected_ids or len(set(CURATED_DISPLAY_LABELS.values())) != len(selected):
        raise ValidationError(
            "Selected evidence-map labels must cover each selected report exactly once; "
            f"missing={sorted(selected_ids - label_ids)}, extra={sorted(label_ids - selected_ids)}"
        )
    rows: List[dict] = []
    for corpus_id in selected:
        study = by_id[corpus_id]
        if corpus_id in CURATED_LINEAGE_IDS:
            lane = CURATED_REFERENCE_LANE
            eps_role = study_field_text(study, P_EPS)
            note = ""
        elif corpus_id == CURATED_BOUNDARY_ID:
            lane = CURATED_EPS_LANE
            eps_role = study_field_text(study, P_EPS)
            note = "Coded power-budget/electrical-architecture; retained without reclassification."
        else:
            lane = CURATED_EPS_LANE
            eps_role = study_field_text(study, P_EPS)
            note = ""
        ivv = study_field_text(study, P_IVV)
        executable = "yes" if ivv in {"executable/model-based checks", "simulation-in-the-loop"} else "no"
        rows.append(
            {
                "paper_id": corpus_id,
                "short_id": corpus_id.replace("paper-", ""),
                "display_label": CURATED_DISPLAY_LABELS[corpus_id],
                "year": study.year,
                "lane": lane,
                "eps_role": eps_role,
                "coded_eps_relevance": study_field_text(study, P_EPS),
                "maturity": study_field_text(study, P_MATURITY),
                "ivv_integration_level": ivv,
                "executable_or_simulation_evidence": executable,
                "note": note,
            }
        )
    return sorted(rows, key=lambda row: (int(row["year"]), row["paper_id"]))


def field_coverage_rows(studies: Sequence[StudyRecord], codebook: Mapping[str, Any]) -> List[dict]:
    """Emit status, selected-value, and invalid-value QA coverage for all fields."""
    rows: List[dict] = []
    claims = all_claims(studies)
    for field_path, spec in codebook["controlled_fields"].items():
        sources: List[Tuple[str, str, Sequence[Tuple[str, FieldObservation]]]] = [
            (
                "structured_code_summary",
                "study",
                observations_for_studies(studies, field_path),
            )
        ]
        if field_path.startswith(CLAIM_PREFIX):
            sources.append(
                ("canonical_claim_record", "claim", observations_for_claims(claims, field_path)))
        for source_scope, unit, observations in sources:
            denominator = len(observations)
            observation_values = [observation for _, observation in observations]
            by_status: Dict[str, set[str]] = {status: set() for status in (*codebook["status_values"], UNASSIGNED_STATUS)}
            by_value: Dict[str, set[str]] = {value: set() for value in spec["allowed_values"]}
            invalid_refs: set[str] = set()
            unassigned_refs: set[str] = set()
            invalid_values: set[str] = set()
            for record_ref, observation in observations:
                by_status.setdefault(observation.status, set()).add(record_ref)
                for value in observation.values:
                    by_value[value].add(record_ref)
                if observation.invalid_values:
                    invalid_refs.add(record_ref)
                    invalid_values.update(observation.invalid_values)
                if not observation.values and not observation.invalid_values:
                    unassigned_refs.add(record_ref)
            for status in (*codebook["status_values"], UNASSIGNED_STATUS):
                refs = by_status.get(status, set())
                rows.append(
                    {
                        "field_path": field_path,
                        "source_scope": source_scope,
                        "unit": unit,
                        "selection_type": spec["type"],
                        "row_kind": "status",
                        "coverage_category": status,
                        "record_count": len(refs),
                        "denominator": denominator,
                        "percent_of_denominator": f"{(100 * len(refs) / denominator) if denominator else 0:.1f}",
                        "record_refs": "; ".join(sorted(refs)),
                        "raw_invalid_values": "",
                    }
                )
            for value in spec["allowed_values"]:
                refs = by_value[value]
                rows.append(
                    {
                        "field_path": field_path,
                        "source_scope": source_scope,
                        "unit": unit,
                        "selection_type": spec["type"],
                        "row_kind": "selected controlled value",
                        "coverage_category": value,
                        "record_count": len(refs),
                        "denominator": denominator,
                        "percent_of_denominator": f"{(100 * len(refs) / denominator) if denominator else 0:.1f}",
                        "record_refs": "; ".join(sorted(refs)),
                        "raw_invalid_values": "",
                    }
                )
            for category, refs, raw_invalid in (
                (UNMAPPED, invalid_refs, "; ".join(sorted(invalid_values))),
                (UNASSIGNED_VALUE, unassigned_refs, ""),
            ):
                rows.append(
                    {
                        "field_path": field_path,
                        "source_scope": source_scope,
                        "unit": unit,
                        "selection_type": spec["type"],
                        "row_kind": "QA",
                        "coverage_category": category,
                        "record_count": len(refs),
                        "denominator": denominator,
                        "percent_of_denominator": f"{(100 * len(refs) / denominator) if denominator else 0:.1f}",
                        "record_refs": "; ".join(sorted(refs)),
                        "raw_invalid_values": raw_invalid,
                    }
                )
    return rows


# ---------------------------------------------------------------------------
# CSV writers and invariants


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def assert_complete_categories(rows: Sequence[Mapping[str, Any]], field_path: str, codebook: Mapping[str, Any]) -> None:
    expected = [*codebook_allowed(codebook, field_path), UNMAPPED, UNASSIGNED_VALUE]
    actual = [row["category"] for row in rows]
    if actual != expected:
        raise ValidationError(f"{field_path}: output categories are not complete/codebook-ordered")


def assert_matrix_total(rows: Sequence[Mapping[str, Any]], expected: int, message: str) -> None:
    actual = sum(int(row["count"]) for row in rows)
    if actual != expected:
        raise ValidationError(f"{message}: expected {expected}, got {actual}")


def assert_report_membership_rows(rows: Sequence[Mapping[str, Any]], *, label: str, expected_unit: str) -> None:
    """Verify denominator, percentage, and auditable unique-report membership IDs."""
    for row in rows:
        count = int(row["count"])
        denominator = int(row["denominator"])
        if denominator != 40:
            raise ValidationError(f"{label}: expected report denominator 40, got {denominator}")
        if row["unit"] != expected_unit:
            raise ValidationError(f"{label}: unexpected unit {row['unit']!r}")
        expected_percent = f"{100 * count / denominator:.1f}"
        if row["percent_of_denominator"] != expected_percent:
            raise ValidationError(
                f"{label}: percentage for {row.get('category', row.get('vv_linkage_category'))!r} "
                f"is {row['percent_of_denominator']!r}, expected {expected_percent!r}"
            )
        ids = [value for value in clean_text(row["study_ids"]).split("; ") if value]
        if len(ids) != count or len(ids) != len(set(ids)):
            raise ValidationError(
                f"{label}: count/unique-study-ID mismatch for "
                f"{row.get('category', row.get('vv_linkage_category'))!r}"
            )


def assert_direct_vv_rows(
    rows: Sequence[Mapping[str, Any]], field_path: str, codebook: Mapping[str, Any]
) -> None:
    """Lock direct RQ3 counts and statuses to the reviewed controlled inputs."""
    assert_complete_categories(rows, field_path, codebook)
    actual_counts = {row["category"]: int(row["count"]) for row in rows}
    if actual_counts != VV_DIRECT_EXPECTED_COUNTS[field_path]:
        raise ValidationError(
            f"{field_path}: direct controlled counts changed; "
            f"expected={VV_DIRECT_EXPECTED_COUNTS[field_path]}, got={actual_counts}"
        )
    assert_report_membership_rows(
        rows,
        label=field_path,
        expected_unit="study membership (unique report)",
    )
    expected_statuses = VV_DIRECT_EXPECTED_STATUS_COUNTS[field_path]
    for status, expected_count in expected_statuses.items():
        column = status_column_name(status)
        actual_statuses = {int(row[column]) for row in rows}
        if actual_statuses != {expected_count}:
            raise ValidationError(
                f"{field_path}: status {status!r} changed; expected {expected_count}, "
                f"got {sorted(actual_statuses)}"
            )


def assert_derived_vv_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    """Keep the retained mixed-source display's declared mapping/counts stable."""
    actual_order = [row["vv_linkage_category"] for row in rows]
    if actual_order != VV_LINKAGE_ORDER:
        raise ValidationError("Derived V&V linkage categories are not in the declared order")
    actual_counts = {row["vv_linkage_category"]: int(row["count"]) for row in rows}
    if actual_counts != VV_DERIVED_EXPECTED_COUNTS:
        raise ValidationError(
            f"Derived V&V linkage counts changed; expected={VV_DERIVED_EXPECTED_COUNTS}, got={actual_counts}"
        )
    assert_report_membership_rows(
        rows,
        label="derived V&V linkage",
        expected_unit="derived study membership (unique report; mixed-source union)",
    )
    if {row["derivation_basis"] for row in rows} != {VV_DERIVATION_BASIS}:
        raise ValidationError("Derived V&V linkage rows lost their mixed-source derivation basis")


def run_invariants(
    studies: Sequence[StudyRecord],
    codebook: Mapping[str, Any],
    *,
    maturity_eps_rows: Sequence[Mapping[str, Any]],
    lifecycle_ivv_rows: Sequence[Mapping[str, Any]],
    specificity_confidence_rows: Sequence[Mapping[str, Any]],
    evidence_baseline_rows: Sequence[Mapping[str, Any]],
    model_maturity_rows: Sequence[Mapping[str, Any]],
    lifecycle_rows: Sequence[Mapping[str, Any]],
    specificity_rows: Sequence[Mapping[str, Any]],
    baseline_rows: Sequence[Mapping[str, Any]],
    evidence_type_rows: Sequence[Mapping[str, Any]],
    prephysical_rows: Sequence[Mapping[str, Any]],
    vv_artifact_rows: Sequence[Mapping[str, Any]],
    readiness_rows: Sequence[Mapping[str, Any]],
    vv_rows: Sequence[Mapping[str, Any]],
) -> None:
    claims = all_claims(studies)
    validate_vv_status_semantics(codebook)
    if len(studies) != 40:
        raise ValidationError(f"Expected 40 extracted reports, found {len(studies)}")
    if len(claims) != len({claim.claim_ref for claim in claims}):
        raise ValidationError("Stable claim references are not unique")
    if len(claims) != 270:
        raise ValidationError(f"Expected 270 claim records, found {len(claims)}")

    for rows, path in (
        (model_maturity_rows, P_MATURITY),
        (lifecycle_rows, P_LIFECYCLE),
        (specificity_rows, P_CLAIM_SPECIFICITY),
        (baseline_rows, P_CLAIM_BASELINE),
        (evidence_type_rows, P_CLAIM_EVIDENCE_TYPE),
    ):
        assert_complete_categories(rows, path, codebook)
    for rows, path in (
        (prephysical_rows, P_PREPHYSICAL),
        (vv_artifact_rows, P_VV_ARTIFACTS),
        (readiness_rows, P_TEST_READINESS),
    ):
        assert_direct_vv_rows(rows, path, codebook)
    assert_derived_vv_rows(vv_rows)

    # Single-select claim matrices contain exactly one cell per claim.
    assert_matrix_total(
        specificity_confidence_rows,
        len(claims),
        "Claim specificity × evidence confidence matrix",
    )
    assert_matrix_total(
        lifecycle_ivv_rows,
        sum(len(category_memberships(study.fields[P_LIFECYCLE])) for study in studies),
        "Lifecycle × IVV matrix",
    )
    assert_matrix_total(
        maturity_eps_rows,
        sum(len(category_memberships(study.fields[P_MATURITY])) for study in studies),
        "Model maturity × EPS relevance matrix",
    )
    assert_matrix_total(
        evidence_baseline_rows,
        sum(len(category_memberships(claim.fields[P_CLAIM_EVIDENCE_TYPE])) for claim in claims),
        "Evidence type × baseline comparator matrix",
    )

    # Regression safeguard for the five prose baseline strings in paper-0007.
    paper_0007 = [claim for claim in claims if claim.corpus_id == "paper-0007"]
    invalid_baselines = [
        claim for claim in paper_0007
        if UNMAPPED in category_memberships(claim.fields[P_CLAIM_BASELINE])
    ]
    if len(invalid_baselines) != 5:
        raise ValidationError(
            "Expected exactly five paper-0007 unmapped/invalid baseline comparator values; "
            f"found {len(invalid_baselines)}"
        )
    if field_value_count(baseline_rows, UNMAPPED) != 5:
        raise ValidationError("Invalid paper-0007 baseline values were not retained in the QA category")


def expected_output_paths() -> List[Path]:
    paths = [DATA_DIR / name for name in (*EXISTING_CSV_NAMES, *PLANNED_CSV_NAMES, *ADDITIONAL_CSV_NAMES)]
    paths.extend(DRAFTS_DIR / name for name in ("data_summary.md", "results_tables.tex"))
    paths.extend(FIG_DIR / f"{name}{suffix}" for name in FIGURE_NAMES for suffix in (".svg", ".pdf", ".png"))
    return paths


# ---------------------------------------------------------------------------
# SVG primitives and figure construction


def svg_text(
    x: float,
    y: float,
    text: Any,
    *,
    size: int = 14,
    anchor: str = "start",
    weight: str = "normal",
    color: str = "#111827",
    extra: str = "",
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
        f'font-weight="{weight}" fill="{color}" {extra}>{html.escape(clean_text(text))}</text>'
    )


def wrapped_svg_text(
    x: float,
    y: float,
    text: str,
    width_chars: int,
    *,
    size: int = 13,
    anchor: str = "start",
    line_height: int = 15,
    weight: str = "normal",
    color: str = "#111827",
) -> Tuple[str, int]:
    lines = textwrap.wrap(clean_text(text), width=width_chars, break_long_words=False) or [""]
    body = "\n".join(
        svg_text(
            x,
            y + index * line_height,
            line,
            size=size,
            anchor=anchor,
            weight=weight,
            color=color,
        )
        for index, line in enumerate(lines)
    )
    return body, len(lines)


def fixed_svg_lines(
    x: float,
    y: float,
    lines: Sequence[str],
    *,
    size: int = 12,
    anchor: str = "start",
    line_height: int = 14,
    weight: str = "normal",
    color: str = "#111827",
) -> str:
    """Render deliberate short label lines without rewrapping them."""
    return "\n".join(
        svg_text(
            x,
            y + index * line_height,
            line,
            size=size,
            anchor=anchor,
            weight=weight,
            color=color,
        )
        for index, line in enumerate(lines)
    )


def svg_document(width: int, height: int, title: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(clean_text(title))}">
<title>{html.escape(clean_text(title))}</title>
<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>
<g font-family="Arial, Helvetica, sans-serif">
{body}
</g>
</svg>
'''


def integer_ticks(maximum: int, desired: int = 5) -> List[int]:
    if maximum <= desired:
        return list(range(0, maximum + 1))
    ticks = {0, maximum}
    for index in range(1, desired):
        ticks.add(round(maximum * index / desired))
    return sorted(ticks)


def horizontal_bar_svg(
    title: str,
    subtitle: str,
    rows: Sequence[Tuple[str, int]],
    *,
    color: str = "#2563EB",
    width: int = 800,
    subtitle_width_chars: int | None = None,
) -> str:
    """Render a full-text-width bar chart with readable source text."""
    maximum = max((int(value) for _, value in rows), default=1)
    left, right, top, row_height = 330, 48, 106, 44
    if subtitle_width_chars is None:
        subtitle_body = svg_text(width / 2, 54, subtitle, size=13, anchor="middle", color="#4B5563")
    else:
        subtitle_body, subtitle_lines = wrapped_svg_text(
            width / 2, 54, subtitle, subtitle_width_chars,
            size=13, anchor="middle", line_height=16, color="#4B5563",
        )
        top = 90 + subtitle_lines * 16
    height = max(245, top + row_height * len(rows) + 62)
    chart_width = width - left - right
    body: List[str] = [
        svg_text(width / 2, 29, title, size=20, anchor="middle", weight="bold"),
        subtitle_body,
    ]
    for tick in integer_ticks(maximum):
        x = left + chart_width * tick / max(maximum, 1)
        body.append(f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{height - 38}" stroke="#E5E7EB" stroke-width="1"/>')
        body.append(svg_text(x, height - 18, str(tick), size=12, anchor="middle", color="#4B5563"))
    for index, (label, value) in enumerate(rows):
        y = top + index * row_height
        label_body, _ = wrapped_svg_text(16, y + 16, label, 38, size=13, line_height=15)
        body.append(label_body)
        bar_width = chart_width * int(value) / max(maximum, 1)
        if value:
            body.append(f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="25" rx="3" fill="{color}"/>')
        else:
            body.append(f'<rect x="{left}" y="{y + 12}" width="3" height="2" fill="#CBD5E1"/>')
        body.append(svg_text(left + bar_width + 7, y + 18, str(value), size=13, color="#111827"))
    return svg_document(width, height, title, "\n".join(body))


def stacked_bar_svg(
    title: str,
    subtitle: str,
    labels: Sequence[str],
    series: Sequence[str],
    values: Mapping[str, Sequence[int]],
    colors: Sequence[str],
) -> str:
    """Render light-fill stacked bars with dark, high-contrast value labels."""
    width, left, right, row_height = 800, 300, 42, 54
    maximum = max((sum(values[label]) for label in labels), default=1)
    subtitle_body, subtitle_lines = wrapped_svg_text(
        width / 2, 54, subtitle, 96, size=13, anchor="middle", line_height=16, color="#4B5563"
    )
    legend_y = 62 + subtitle_lines * 16
    legend_x = left
    legend_positions: List[Tuple[int, int, str, str]] = []
    for label, color in zip(series, colors):
        item_width = max(88, 24 + len(label) * 7)
        if legend_x + item_width > width - right:
            legend_x = left
            legend_y += 22
        legend_positions.append((legend_x, legend_y, label, color))
        legend_x += item_width
    top = legend_y + 40
    height = max(250, top + row_height * len(labels) + 62)
    chart_width = width - left - right
    body: List[str] = [
        svg_text(width / 2, 29, title, size=20, anchor="middle", weight="bold"),
        subtitle_body,
    ]
    for legend_x, legend_y, label, color in legend_positions:
        body.append(f'<rect x="{legend_x}" y="{legend_y}" width="16" height="16" rx="2" fill="{color}" stroke="#94A3B8" stroke-width="0.5"/>')
        body.append(svg_text(legend_x + 22, legend_y + 13, label, size=13, color="#374151"))
    for tick in integer_ticks(maximum):
        x = left + chart_width * tick / max(maximum, 1)
        body.append(f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{height - 38}" stroke="#E5E7EB" stroke-width="1"/>')
        body.append(svg_text(x, height - 18, str(tick), size=12, anchor="middle", color="#4B5563"))
    for row_index, label in enumerate(labels):
        y = top + row_index * row_height
        label_body, _ = wrapped_svg_text(16, y + 16, label, 34, size=13, line_height=15)
        body.append(label_body)
        x = left
        total = sum(values[label])
        for value, color in zip(values[label], colors):
            if value:
                segment = chart_width * value / max(maximum, 1)
                body.append(f'<rect x="{x:.1f}" y="{y}" width="{segment:.1f}" height="27" rx="2" fill="{color}"/>')
                if segment >= 25:
                    body.append(svg_text(x + segment / 2, y + 19, str(value), size=12, anchor="middle", color="#111827"))
                x += segment
        body.append(svg_text(left + chart_width + 7, y + 19, str(total), size=13, color="#111827"))
    return svg_document(width, height, title, "\n".join(body))


def heat_color(value: int, maximum: int) -> str:
    if value <= 0 or maximum <= 0:
        return "#F8FAFC"
    # Deterministic five-stop sequential blue scale.
    palette = ("#DBEAFE", "#BFDBFE", "#93C5FD", "#60A5FA", "#2563EB")
    index = min(len(palette) - 1, max(0, math.ceil(value / maximum * len(palette)) - 1))
    return palette[index]


def separated_coverage_bar_svg(
    title: str,
    status_line: str,
    rows: Sequence[Tuple[str, int]],
    *,
    neutral_label: str,
    neutral_count: int,
    color: str,
) -> str:
    """Render substantive categories and a visibly separate neutral QA bar."""
    width, left, right, row_height = 800, 350, 44, 45
    maximum = max([neutral_count, *(int(count) for _, count in rows), 1])
    status_body, status_lines = wrapped_svg_text(
        width / 2, 54, status_line, 100, size=13, anchor="middle", line_height=16, color="#4B5563"
    )
    unit_y = 55 + status_lines * 16
    top = unit_y + 30
    neutral_y = top + len(rows) * row_height + 15
    height = neutral_y + row_height + 54
    chart_width = width - left - right
    body: List[str] = [
        svg_text(width / 2, 29, title, size=20, anchor="middle", weight="bold"),
        status_body,
        svg_text(width / 2, unit_y, "Bars are unique report memberships; selected elements may co-occur.", size=13, anchor="middle", color="#4B5563"),
    ]
    for tick in integer_ticks(maximum):
        x = left + chart_width * tick / maximum
        body.append(f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{height - 38}" stroke="#E5E7EB" stroke-width="1"/>')
        body.append(svg_text(x, height - 18, str(tick), size=12, anchor="middle", color="#4B5563"))
    for index, (label, count) in enumerate(rows):
        y = top + index * row_height
        label_body, _ = wrapped_svg_text(16, y + 16, label, 39, size=13, line_height=15)
        body.append(label_body)
        bar_width = chart_width * int(count) / maximum
        if count:
            body.append(f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="25" rx="3" fill="{color}"/>')
        else:
            body.append(f'<rect x="{left}" y="{y + 12}" width="3" height="2" fill="#CBD5E1"/>')
        body.append(svg_text(left + bar_width + 7, y + 18, str(count), size=13, color="#111827"))
    body.append(f'<line x1="16" y1="{neutral_y - 8}" x2="{width - 20}" y2="{neutral_y - 8}" stroke="#94A3B8" stroke-width="1" stroke-dasharray="4 3"/>')
    neutral_body, _ = wrapped_svg_text(16, neutral_y + 16, neutral_label, 39, size=13, line_height=15, weight="bold", color="#374151")
    body.append(neutral_body)
    neutral_width = chart_width * neutral_count / maximum
    body.append(f'<rect x="{left}" y="{neutral_y}" width="{neutral_width:.1f}" height="25" rx="3" fill="#E5E7EB" stroke="#94A3B8" stroke-width="1"/>')
    body.append(svg_text(left + neutral_width + 7, neutral_y + 18, str(neutral_count), size=13, weight="bold", color="#111827"))
    return svg_document(width, height, title, "\n".join(body))


def co_reporting_heatmap_svg(
    title: str,
    subtitle: str,
    row_labels: Sequence[str],
    column_labels: Sequence[str],
    values: Mapping[Tuple[str, str], int],
    *,
    row_axis_label: str,
    column_axis_label: str,
    footer: str,
    columns_per_panel: int,
    column_display_labels: Mapping[str, str] | None = None,
    neutral_columns: Iterable[str] = (),
) -> str:
    """Render a wide controlled co-reporting matrix as readable vertical panels."""
    width, left, right, cell_height = 800, 285, 28, 50
    neutral = set(neutral_columns)
    display_labels = dict(column_display_labels or {})
    chunks = [
        list(column_labels[index:index + columns_per_panel])
        for index in range(0, len(column_labels), columns_per_panel)
    ]
    maximum = max(values.values(), default=0)
    subtitle_body, subtitle_lines = wrapped_svg_text(
        width / 2, 54, subtitle, 98, size=13, anchor="middle", line_height=16, color="#4B5563"
    )
    body: List[str] = [
        svg_text(width / 2, 29, title, size=20, anchor="middle", weight="bold"),
        subtitle_body,
    ]
    y = 66 + subtitle_lines * 16
    for panel_index, columns in enumerate(chunks, start=1):
        cell_width = (width - left - right) // len(columns)
        header_width = max(10, int(cell_width / 7.0))
        maximum_header_lines = max(
            len(textwrap.wrap(display_labels.get(label, label), width=header_width, break_long_words=False) or [""])
            for label in columns
        )
        body.append(svg_text(
            width / 2, y + 19,
            f"{column_axis_label} — panel {panel_index} of {len(chunks)}",
            size=15, anchor="middle", weight="bold", color="#374151",
        ))
        body.append(svg_text(16, y + 43, row_axis_label, size=13, weight="bold", color="#374151"))
        header_y = y + 43
        for column_index, column_label in enumerate(columns):
            x = left + column_index * cell_width + cell_width / 2
            label_body, _ = wrapped_svg_text(
                x, header_y, display_labels.get(column_label, column_label), header_width,
                size=13, anchor="middle", line_height=15, color="#374151",
            )
            body.append(label_body)
        top = header_y + maximum_header_lines * 15 + 12
        for row_index, row_label in enumerate(row_labels):
            row_y = top + row_index * cell_height
            label_body, _ = wrapped_svg_text(16, row_y + 18, row_label, 33, size=13, line_height=15, color="#374151")
            body.append(label_body)
            for column_index, column_label in enumerate(columns):
                x = left + column_index * cell_width
                value = int(values.get((row_label, column_label), 0))
                color = "#E5E7EB" if column_label in neutral and value else (
                    "#F8FAFC" if column_label in neutral else heat_color(value, maximum)
                )
                body.append(f'<rect x="{x}" y="{row_y}" width="{cell_width}" height="{cell_height}" fill="{color}" stroke="#CBD5E1" stroke-width="1"/>')
                text_color = "white" if color == "#2563EB" else "#111827"
                body.append(svg_text(x + cell_width / 2, row_y + 31, str(value), size=15, anchor="middle", weight="bold", color=text_color))
        y = top + len(row_labels) * cell_height + 34
    footer_body, footer_lines = wrapped_svg_text(
        16, y + 5, footer, 100, size=13, line_height=16, color="#4B5563"
    )
    body.append(footer_body)
    height = y + footer_lines * 16 + 22
    return svg_document(width, height, title, "\n".join(body))


def compact_maturity_eps_heatmap_svg(
    row_labels: Sequence[str],
    column_labels: Sequence[str],
    values: Mapping[Tuple[str, str], int],
) -> str:
    """Render the substantive 5 × 6 maturity/EPS cross-classification."""
    if len(row_labels) != 5 or len(column_labels) != 6:
        raise ValidationError("The maturity × EPS figure must contain one 5 × 6 substantive matrix")

    width = 800
    title = "Model maturity × EPS relevance / controlled co-reporting"
    subtitle = "n=40 reports; model maturity is multi-label and EPS relevance is a controlled category."
    header_labels: Dict[str, Tuple[str, ...]] = {
        "conceptual framework": ("Conceptual", "framework"),
        "reference model/template": ("Reference", "model /", "template"),
        "prototype demonstration": ("Prototype", "demonstration"),
        "executable model": ("Executable", "model"),
        "project-applied model": ("Project-", "applied model"),
        "validated/operational model": ("Validated /", "operational", "model"),
    }
    header_lines = {
        label: header_labels.get(label, tuple(textwrap.wrap(label, width=12, break_long_words=False) or [""]))
        for label in column_labels
    }
    maximum_header_lines = max(len(lines) for lines in header_lines.values())
    left, right, cell_height = 250, 20, 55
    cell_width = (width - left - right) / len(column_labels)
    maximum = max(
        (int(values.get((row, column), 0)) for row in row_labels for column in column_labels),
        default=0,
    )
    subtitle_body, subtitle_lines = wrapped_svg_text(
        width / 2, 54, subtitle, 108, size=12, anchor="middle", line_height=14, color="#4B5563"
    )
    axis_y = 80 + (subtitle_lines - 1) * 14
    header_y = axis_y + 26
    top = header_y + maximum_header_lines * 14 + 12
    body: List[str] = [
        svg_text(width / 2, 29, title, size=20, anchor="middle", weight="bold"),
        subtitle_body,
        svg_text(left + (width - left - right) / 2, axis_y, "Model maturity", size=13, anchor="middle", weight="bold", color="#374151"),
        svg_text(16, header_y, "EPS relevance", size=12, weight="bold", color="#374151"),
    ]
    for column_index, column in enumerate(column_labels):
        x = left + column_index * cell_width + cell_width / 2
        body.append(fixed_svg_lines(
            x, header_y, header_lines[column], size=12, anchor="middle", line_height=14, color="#374151"
        ))
    for row_index, row in enumerate(row_labels):
        row_y = top + row_index * cell_height
        row_body, _ = wrapped_svg_text(16, row_y + 20, row, 35, size=12, line_height=14, color="#374151")
        body.append(row_body)
        for column_index, column in enumerate(column_labels):
            x = left + column_index * cell_width
            value = int(values.get((row, column), 0))
            color = heat_color(value, maximum)
            body.append(f'<rect x="{x:.1f}" y="{row_y}" width="{cell_width:.1f}" height="{cell_height}" fill="{color}" stroke="#CBD5E1" stroke-width="1"/>')
            text_color = "white" if color == "#2563EB" else "#111827"
            body.append(svg_text(x + cell_width / 2, row_y + 34, str(value), size=13, anchor="middle", weight="bold", color=text_color))
    matrix_bottom = top + len(row_labels) * cell_height
    footer = (
        "Cells are unique-report co-reporting counts; × means cross-classification only / no progression or direct linkage. "
        "All QA, unassigned, and not-reported classes are zero and remain in the CSV."
    )
    footer_y = matrix_bottom + 27
    footer_body, footer_lines = wrapped_svg_text(16, footer_y, footer, 108, size=12, line_height=14, color="#4B5563")
    body.append(footer_body)
    height = footer_y + footer_lines * 14 + 18
    if height > 700:
        raise ValidationError(f"Maturity × EPS figure exceeds its 700-unit page-height limit: {height}")
    return svg_document(width, height, title, "\n".join(body))


def compact_lifecycle_ivv_heatmap_svg(
    row_labels: Sequence[str],
    panel_columns: Sequence[Sequence[str]],
    values: Mapping[Tuple[str, str], int],
    *,
    no_selected_ivv: int,
    omitted_columns: Sequence[str],
) -> str:
    """Render two aligned, four-column IVV heatmap panels with shared rows."""
    if len(row_labels) != 7 or len(panel_columns) != 2 or any(len(columns) != 4 for columns in panel_columns):
        raise ValidationError("The lifecycle × IVV figure must contain two four-column panels and seven substantive rows")
    if no_selected_ivv != 3:
        raise ValidationError(f"Expected three reports with no selected IVV level, found {no_selected_ivv}")

    width = 800
    title = "Lifecycle stage × IVV integration level / controlled co-reporting"
    subtitle = (
        "n=40 reports; lifecycle is multi-label. 'none/not reported' is a controlled IVV level; "
        f"{no_selected_ivv} reports have no selected IVV level."
    )
    display_lines: Dict[str, Tuple[str, ...]] = {
        "none/not reported": ("none/not", "reported"),
        "separate document only": ("separate", "document"),
        "trace-linked verification artifacts": ("trace-linked", "artifacts"),
        "model-contained verification artifacts": ("model-", "contained", "artifacts"),
        "executable/model-based checks": ("executable", "checks"),
        "simulation-in-the-loop": ("simulation-", "in-the-loop"),
        "software/hardware-in-the-loop": ("SIL/HIL",),
        UNASSIGNED_VALUE: ("No selected", "IVV level", f"({no_selected_ivv} reports)"),
    }
    max_header_lines = max(
        len(display_lines.get(column, tuple(textwrap.wrap(column, width=11, break_long_words=False) or [""])))
        for columns in panel_columns for column in columns
    )
    labels_right, gap, right, cell_height = 218, 16, 16, 48
    panel_width = (width - labels_right - gap - right) / 2
    maximum = max(
        (int(values.get((row, column), 0)) for row in row_labels for columns in panel_columns for column in columns),
        default=0,
    )
    subtitle_body, subtitle_lines = wrapped_svg_text(
        width / 2, 53, subtitle, 108, size=12, anchor="middle", line_height=14, color="#4B5563"
    )
    panel_title_y = 96 + (subtitle_lines - 2) * 14
    header_y = panel_title_y + 26
    top = header_y + max_header_lines * 14 + 11
    body: List[str] = [
        svg_text(width / 2, 29, title, size=20, anchor="middle", weight="bold"),
        subtitle_body,
        svg_text(16, header_y, "Lifecycle stage addressed", size=12, weight="bold", color="#374151"),
    ]
    for panel_index, columns in enumerate(panel_columns):
        origin_x = labels_right + panel_index * (panel_width + gap)
        cell_width = panel_width / len(columns)
        panel_name = chr(ord("A") + panel_index)
        body.append(svg_text(
            origin_x + panel_width / 2, panel_title_y,
            f"IVV integration level — panel {panel_name}",
            size=13, anchor="middle", weight="bold", color="#374151",
        ))
        for column_index, column in enumerate(columns):
            x = origin_x + column_index * cell_width + cell_width / 2
            lines = display_lines.get(column, tuple(textwrap.wrap(column, width=11, break_long_words=False) or [""]))
            body.append(fixed_svg_lines(
                x, header_y, lines, size=12, anchor="middle", line_height=14, color="#374151"
            ))
    for row_index, row in enumerate(row_labels):
        row_y = top + row_index * cell_height
        row_body, _ = wrapped_svg_text(16, row_y + 19, row, 31, size=12, line_height=13, color="#374151")
        body.append(row_body)
        for panel_index, columns in enumerate(panel_columns):
            origin_x = labels_right + panel_index * (panel_width + gap)
            cell_width = panel_width / len(columns)
            for column_index, column in enumerate(columns):
                x = origin_x + column_index * cell_width
                value = int(values.get((row, column), 0))
                color = "#E5E7EB" if column == UNASSIGNED_VALUE and value else (
                    "#F8FAFC" if column == UNASSIGNED_VALUE else heat_color(value, maximum)
                )
                body.append(f'<rect x="{x:.1f}" y="{row_y}" width="{cell_width:.1f}" height="{cell_height}" fill="{color}" stroke="#CBD5E1" stroke-width="1"/>')
                text_color = "white" if color == "#2563EB" else "#111827"
                body.append(svg_text(x + cell_width / 2, row_y + 30, str(value), size=13, anchor="middle", weight="bold", color=text_color))
    matrix_bottom = top + len(row_labels) * cell_height
    footer = (
        "Cells are unique-report co-reporting counts; × means cross-classification only / no progression or direct linkage. "
        "Omitted zero-only controlled/QA IVV columns—"
        + "; ".join(omitted_columns)
        + "—remain in the CSV. All lifecycle rows remain in the CSV."
    )
    footer_y = matrix_bottom + 27
    footer_body, footer_lines = wrapped_svg_text(16, footer_y, footer, 108, size=12, line_height=14, color="#4B5563")
    body.append(footer_body)
    height = footer_y + footer_lines * 14 + 18
    if height > 850:
        raise ValidationError(f"Lifecycle × IVV figure exceeds its 850-unit page-height limit: {height}")
    return svg_document(width, height, title, "\n".join(body))


def heatmap_svg(
    title: str,
    subtitle: str,
    row_labels: Sequence[str],
    column_labels: Sequence[str],
    values: Mapping[Tuple[str, str], int],
    *,
    row_axis_label: str,
    column_axis_label: str,
) -> str:
    cell_width, cell_height, left, right = 142, 54, 315, 45
    max_column_lines = max(
        len(textwrap.wrap(label, width=18, break_long_words=False) or [""])
        for label in column_labels
    )
    top = 105 + max_column_lines * 15
    width = max(1000, left + len(column_labels) * cell_width + right)
    height = top + len(row_labels) * cell_height + 62
    maximum = max(values.values(), default=0)
    body: List[str] = [
        svg_text(width / 2, 29, title, size=21, anchor="middle", weight="bold"),
        svg_text(width / 2, 53, subtitle, size=12, anchor="middle", color="#4B5563"),
        svg_text(left + len(column_labels) * cell_width / 2, 82, column_axis_label, size=12, anchor="middle", weight="bold", color="#374151"),
        svg_text(16, top - 8, row_axis_label, size=12, weight="bold", color="#374151"),
    ]
    for column_index, label in enumerate(column_labels):
        x = left + column_index * cell_width + cell_width / 2
        label_body, lines = wrapped_svg_text(x, 96, label, 18, size=11, anchor="middle", line_height=13, color="#374151")
        body.append(label_body)
    for row_index, row_label in enumerate(row_labels):
        y = top + row_index * cell_height
        label_body, _ = wrapped_svg_text(12, y + 19, row_label, 34, size=11, line_height=13, color="#374151")
        body.append(label_body)
        for column_index, column_label in enumerate(column_labels):
            x = left + column_index * cell_width
            value = int(values.get((row_label, column_label), 0))
            color = heat_color(value, maximum)
            body.append(f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" fill="{color}" stroke="#CBD5E1" stroke-width="1"/>')
            text_color = "white" if color == "#2563EB" else "#111827"
            body.append(svg_text(x + cell_width / 2, y + 32, str(value), size=15, anchor="middle", weight="bold", color=text_color))
    body.append(svg_text(left, height - 19, "Cell values are counts of unique records; zero cells are retained.", size=11, color="#4B5563"))
    return svg_document(width, height, title, "\n".join(body))


def heatmap_panel_body(
    *,
    origin_x: int,
    origin_y: int,
    panel_width: int,
    title: str,
    row_labels: Sequence[str],
    column_labels: Sequence[str],
    values: Mapping[Tuple[str, str], int],
) -> Tuple[List[str], int]:
    left, right, cell_height = 255, 25, 48
    cell_width = max(88, (panel_width - left - right) // max(len(column_labels), 1))
    max_lines = max(
        len(textwrap.wrap(label, width=15, break_long_words=False) or [""])
        for label in column_labels
    )
    top = origin_y + 60 + max_lines * 13
    maximum = max(values.values(), default=0)
    body: List[str] = [
        svg_text(origin_x + panel_width / 2, origin_y + 24, title, size=16, anchor="middle", weight="bold"),
    ]
    for column_index, label in enumerate(column_labels):
        x = origin_x + left + column_index * cell_width + cell_width / 2
        label_body, _ = wrapped_svg_text(x, origin_y + 49, label, 15, size=10, anchor="middle", line_height=12, color="#374151")
        body.append(label_body)
    for row_index, row_label in enumerate(row_labels):
        y = top + row_index * cell_height
        label_body, _ = wrapped_svg_text(origin_x + 8, y + 17, row_label, 31, size=10, line_height=12, color="#374151")
        body.append(label_body)
        for column_index, column_label in enumerate(column_labels):
            x = origin_x + left + column_index * cell_width
            value = int(values.get((row_label, column_label), 0))
            color = heat_color(value, maximum)
            body.append(f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" fill="{color}" stroke="#CBD5E1" stroke-width="1"/>')
            text_color = "white" if color == "#2563EB" else "#111827"
            body.append(svg_text(x + cell_width / 2, y + 29, str(value), size=13, anchor="middle", weight="bold", color=text_color))
    return body, top + len(row_labels) * cell_height


def claim_anatomy_svg(
    specificity_labels: Sequence[str],
    confidence_labels: Sequence[str],
    specificity_values: Mapping[Tuple[str, str], int],
    evidence_labels: Sequence[str],
    baseline_labels: Sequence[str],
    evidence_values: Mapping[Tuple[str, str], int],
    claim_count: int,
) -> str:
    """Stack compact claim matrices while retaining the invalid baseline column."""
    width = 800
    title = "Claim evidence anatomy"
    if UNMAPPED not in baseline_labels:
        raise ValidationError("Claim anatomy must retain the invalid/unmapped baseline column")
    body: List[str] = [svg_text(width / 2, 29, title, size=20, anchor="middle", weight="bold")]
    explanatory_lines = [
        f"n={claim_count} nested claims. Left cells are claim counts; right cells are evidence-type memberships (multi-label).",
        "Comparator recorded = previous document-centric process, manual analysis, alternative toolchain, or previous mission.",
        "All-zero QA rows are omitted from the figure but remain zero in the CSV; the invalid baseline column is retained.",
    ]
    y = 52
    for line in explanatory_lines:
        line_body, line_count = wrapped_svg_text(
            width / 2, y, line, 122, size=12, anchor="middle", line_height=14, color="#4B5563"
        )
        body.append(line_body)
        y += line_count * 14
    y += 7

    def visible_rows(
        rows: Sequence[str],
        columns: Sequence[str],
        matrix: Mapping[Tuple[str, str], int],
    ) -> List[str]:
        return [
            row for row in rows
            if row not in {UNMAPPED, UNASSIGNED_VALUE}
            or any(int(matrix.get((row, column), 0)) for column in columns)
        ]

    def panel(
        origin_y: int,
        panel_title: str,
        rows: Sequence[str],
        columns: Sequence[str],
        matrix: Mapping[Tuple[str, str], int],
        *,
        left: int,
        row_width: int,
    ) -> Tuple[List[str], int]:
        right, cell_height = 18, 40
        cell_width = (width - left - right) / len(columns)
        header_width = max(10, int(cell_width / 7.0))
        header_labels = {
            UNMAPPED: ("invalid /", "unmapped"),
            UNASSIGNED_VALUE: ("no selected", "value"),
            "comparator recorded": ("comparator", "recorded"),
            "explicitly none": ("explicitly", "none"),
            "not reported": ("not", "reported"),
        }
        header_lines = {
            column: header_labels.get(
                column, tuple(textwrap.wrap(column, width=header_width, break_long_words=False) or [""])
            )
            for column in columns
        }
        maximum_header_lines = max(len(lines) for lines in header_lines.values())
        top = origin_y + 43 + maximum_header_lines * 14 + 8
        maximum = max((int(matrix.get((row, column), 0)) for row in rows for column in columns), default=0)
        panel_body: List[str] = [
            svg_text(width / 2, origin_y + 20, panel_title, size=16, anchor="middle", weight="bold"),
        ]
        for column_index, column in enumerate(columns):
            x = left + column_index * cell_width + cell_width / 2
            panel_body.append(fixed_svg_lines(
                x, origin_y + 43, header_lines[column], size=12, anchor="middle", line_height=14, color="#374151"
            ))
        for row_index, row in enumerate(rows):
            row_y = top + row_index * cell_height
            row_body, _ = wrapped_svg_text(16, row_y + 15, row, row_width, size=12, line_height=13, color="#374151")
            panel_body.append(row_body)
            for column_index, column in enumerate(columns):
                x = left + column_index * cell_width
                value = int(matrix.get((row, column), 0))
                color = heat_color(value, maximum)
                panel_body.append(f'<rect x="{x:.1f}" y="{row_y}" width="{cell_width:.1f}" height="{cell_height}" fill="{color}" stroke="#CBD5E1" stroke-width="1"/>')
                text_color = "white" if color == "#2563EB" else "#111827"
                panel_body.append(svg_text(x + cell_width / 2, row_y + 25, str(value), size=13, anchor="middle", weight="bold", color=text_color))
        return panel_body, top + len(rows) * cell_height

    visible_specificity_rows = visible_rows(specificity_labels, confidence_labels, specificity_values)
    visible_evidence_rows = visible_rows(evidence_labels, baseline_labels, evidence_values)
    specificity_body, specificity_bottom = panel(
        y,
        "Claim specificity × evidence confidence",
        visible_specificity_rows,
        confidence_labels,
        specificity_values,
        left=250,
        row_width=35,
    )
    body.extend(specificity_body)
    evidence_body, evidence_bottom = panel(
        specificity_bottom + 18,
        "Evidence type × baseline-comparator availability",
        visible_evidence_rows,
        baseline_labels,
        evidence_values,
        left=300,
        row_width=40,
    )
    body.extend(evidence_body)
    footer = "Counts are controlled claim memberships; all-zero QA rows are omitted here but remain zero in the CSV."
    footer_y = evidence_bottom + 20
    footer_body, footer_lines = wrapped_svg_text(16, footer_y, footer, 120, size=12, line_height=14, color="#4B5563")
    body.append(footer_body)
    height = footer_y + footer_lines * 14 + 18
    if height > 950:
        raise ValidationError(f"Claim-evidence anatomy figure exceeds its 950-unit page-height limit: {height}")
    return svg_document(width, height, title, "\n".join(body))


def toolchain_panels_svg(
    mechanism_rows: Sequence[Mapping[str, Any]],
    limitation_rows: Sequence[Mapping[str, Any]],
    mechanism_statuses: Mapping[str, int],
    limitation_statuses: Mapping[str, int],
    report_count: int,
) -> str:
    """Render compact side-by-side toolchain panels with separate status context."""
    width = 800
    title = "Interoperability mechanisms and toolchain limitations"
    subtitle = "Only substantive controlled categories are bars; neutral gray rows are no selected controlled values."
    subtitle_body, subtitle_lines = wrapped_svg_text(
        width / 2, 53, subtitle, 114, size=12, anchor="middle", line_height=14, color="#4B5563"
    )
    body: List[str] = [
        svg_text(width / 2, 29, title, size=20, anchor="middle", weight="bold"),
        subtitle_body,
    ]

    def status_context(statuses: Mapping[str, int]) -> str:
        parts = [
            f"coded {statuses.get('coded', 0)}/{report_count}",
            f"not-reported status {statuses.get('not_reported', 0)}",
        ]
        if statuses.get("uncertain", 0):
            parts.append(f"uncertain {statuses['uncertain']}")
        return "Field status: " + "; ".join(parts) + "."

    def panel(
        origin_x: float,
        origin_y: int,
        panel_width: float,
        panel_title: str,
        rows: Sequence[Mapping[str, Any]],
        statuses: Mapping[str, int],
        neutral_label: str,
        color: str,
    ) -> Tuple[List[str], int]:
        label_width, right, row_height = 158, 20, 35
        chart_left = origin_x + label_width
        chart_right = origin_x + panel_width - right
        chart_width = chart_right - chart_left
        filtered = [
            (str(row["category"]), int(row["count"]))
            for row in rows
            if row["category"] not in {"not reported", UNMAPPED, UNASSIGNED_VALUE}
        ]
        neutral_count = next(
            int(row["count"]) for row in rows if row["category"] == UNASSIGNED_VALUE
        )
        maximum = max([neutral_count, *(count for _, count in filtered), 1])
        status_body, status_lines = wrapped_svg_text(
            origin_x + panel_width / 2, origin_y + 42, status_context(statuses), 50,
            size=12, anchor="middle", line_height=14, color="#4B5563",
        )
        status_bottom = origin_y + 42 + (status_lines - 1) * 14
        note_y = status_bottom + 18
        top = note_y + 22
        neutral_lines = textwrap.wrap(neutral_label, width=22, break_long_words=False) or [""]
        neutral_height = max(36, len(neutral_lines) * 13 + 8)
        neutral_y = top + len(filtered) * row_height + 14
        neutral_bar_y = neutral_y + (neutral_height - 24) / 2
        tick_y = neutral_y + neutral_height + 18
        panel_body: List[str] = [
            svg_text(origin_x + panel_width / 2, origin_y + 20, panel_title, size=16, anchor="middle", weight="bold"),
            status_body,
            svg_text(origin_x + panel_width / 2, note_y, "Bars are unique report memberships.", size=12, anchor="middle", color="#4B5563"),
        ]
        for tick in integer_ticks(maximum):
            x = chart_left + chart_width * tick / maximum
            panel_body.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{neutral_bar_y + 24:.1f}" stroke="#E5E7EB" stroke-width="1"/>')
            panel_body.append(svg_text(x, tick_y, str(tick), size=12, anchor="middle", color="#4B5563"))
        for index, (label, count) in enumerate(filtered):
            row_y = top + index * row_height
            label_body, _ = wrapped_svg_text(origin_x, row_y + 14, label, 23, size=12, line_height=13, color="#111827")
            panel_body.append(label_body)
            bar_width = chart_width * count / maximum
            bar_y = row_y + 5
            if count:
                panel_body.append(f'<rect x="{chart_left:.1f}" y="{bar_y}" width="{bar_width:.1f}" height="22" rx="3" fill="{color}"/>')
            else:
                panel_body.append(f'<rect x="{chart_left:.1f}" y="{row_y + 15}" width="3" height="2" fill="#CBD5E1"/>')
            panel_body.append(svg_text(chart_left + bar_width + 5, bar_y + 17, str(count), size=12, color="#111827"))
        panel_body.append(f'<line x1="{origin_x:.1f}" y1="{neutral_y - 7}" x2="{origin_x + panel_width:.1f}" y2="{neutral_y - 7}" stroke="#94A3B8" stroke-width="1" stroke-dasharray="4 3"/>')
        panel_body.append(fixed_svg_lines(
            origin_x, neutral_y + 14, neutral_lines, size=12, line_height=13, weight="bold", color="#374151"
        ))
        neutral_width = chart_width * neutral_count / maximum
        panel_body.append(f'<rect x="{chart_left:.1f}" y="{neutral_bar_y:.1f}" width="{neutral_width:.1f}" height="24" rx="3" fill="#E5E7EB" stroke="#94A3B8" stroke-width="1"/>')
        panel_body.append(svg_text(chart_left + neutral_width + 5, neutral_bar_y + 18, str(neutral_count), size=12, weight="bold", color="#111827"))
        return panel_body, tick_y + 14

    margin, gap = 16, 18
    panel_width = (width - margin * 2 - gap) / 2
    origin_y = 72 + (subtitle_lines - 1) * 14
    mechanisms_body, mechanisms_bottom = panel(
        margin,
        origin_y,
        panel_width,
        "Interoperability mechanisms",
        mechanism_rows,
        mechanism_statuses,
        "No selected controlled value (not a mechanism)",
        "#2563EB",
    )
    limitations_body, limitations_bottom = panel(
        margin + panel_width + gap,
        origin_y,
        panel_width,
        "Toolchain limitations",
        limitation_rows,
        limitation_statuses,
        "No selected controlled value (not a limitation)",
        "#B45309",
    )
    body.extend(mechanisms_body)
    body.extend(limitations_body)
    height = max(mechanisms_bottom, limitations_bottom) + 16
    if height > 800:
        raise ValidationError(f"Toolchain mechanisms/limitations figure exceeds its 800-unit page-height limit: {height}")
    return svg_document(width, height, title, "\n".join(body))


def prisma_svg(counts: Mapping[str, int]) -> str:
    width, height = 800, 500
    main_x, main_width, main_height = 60, 400, 68
    side_x, side_width, side_height = 540, 210, 52
    y_values = (42, 145, 248, 351)
    main_boxes = (
        ("Records identified", counts["raw_records"], "#DBEAFE"),
        ("Records screened", counts["unique_records_screened"], "#E0F2FE"),
        ("Reports sought for retrieval", counts["reports_sought"], "#DCFCE7"),
        ("Reports included in the synthesis", counts["extracted"], "#F3E8FF"),
    )
    side_boxes = (
        ("Duplicates removed", counts["duplicates_removed"], 58),
        ("Records excluded", counts["excluded_screening"], 161),
        ("Reports not retrieved", counts["not_retrieved"], 264),
    )
    title = "Study selection flow"
    body: List[str] = [svg_text(width / 2, 26, title, size=20, anchor="middle", weight="bold")]
    for index, (label, count, fill) in enumerate(main_boxes):
        y = y_values[index]
        body.append(f'<rect x="{main_x}" y="{y}" width="{main_width}" height="{main_height}" rx="10" fill="{fill}" stroke="#334155" stroke-width="1.5"/>')
        body.append(svg_text(main_x + 16, y + 29, label, size=16, weight="bold"))
        body.append(svg_text(main_x + 16, y + 53, f"n = {count}", size=15, color="#1F2937"))
        if index < len(main_boxes) - 1:
            x = main_x + main_width / 2
            target_y = y_values[index + 1]
            body.append(f'<line x1="{x}" y1="{y + main_height + 6}" x2="{x}" y2="{target_y - 10}" stroke="#334155" stroke-width="2"/>')
            body.append(f'<polygon points="{x - 7},{target_y - 10} {x + 7},{target_y - 10} {x},{target_y}" fill="#334155"/>')
    for index, (label, count, y) in enumerate(side_boxes):
        body.append(f'<rect x="{side_x}" y="{y}" width="{side_width}" height="{side_height}" rx="8" fill="#F8FAFC" stroke="#64748B" stroke-width="1.2"/>')
        body.append(svg_text(side_x + 13, y + 22, label, size=13, weight="bold"))
        body.append(svg_text(side_x + 13, y + 41, f"n = {count}", size=13, color="#374151"))
        source_y = y_values[index] + main_height / 2
        target_y = y + side_height / 2
        body.append(f'<line x1="{main_x + main_width + 8}" y1="{source_y}" x2="{side_x - 10}" y2="{target_y}" stroke="#64748B" stroke-width="1.5"/>')
        body.append(f'<polygon points="{side_x - 10},{target_y - 5} {side_x - 10},{target_y + 5} {side_x},{target_y}" fill="#64748B"/>')
    return svg_document(width, height, title, "\n".join(body))


def curated_timeline_svg(rows: Sequence[Mapping[str, Any]]) -> str:
    """Render the selected evidence map with legible title-derived labels."""
    expected_ids = set(CURATED_DISPLAY_LABELS)
    row_ids = [str(row["paper_id"]) for row in rows]
    if len(rows) != len(expected_ids) or set(row_ids) != expected_ids or len(row_ids) != len(set(row_ids)):
        raise ValidationError("Selected evidence-map rows do not retain the declared 19-report membership")
    if {str(row["display_label"]) for row in rows} != set(CURATED_DISPLAY_LABELS.values()):
        raise ValidationError("Selected evidence-map rows do not retain every title-derived display label")

    width = 1040
    colors = {
        "power-budget/electrical-architecture": "#2CA25F",
        "EPS-adjacent": "#60A5FA",
        "system-level only": "#9CA3AF",
        "EPS-specific": "#F59E0B",
        "not EPS-relevant": "#CBD5E1",
    }
    title = "Selected evidence map: reference-model lineage and EPS-focused reports"
    years = list(range(min(int(row["year"]) for row in rows), max(int(row["year"]) for row in rows) + 1))
    by_year_lane: Dict[Tuple[int, str], List[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_year_lane[(int(row["year"]), str(row["lane"]))].append(row)
    for entries in by_year_lane.values():
        entries.sort(key=lambda row: str(row["paper_id"]))

    year_left, reference_left, eps_left, right = 34, 122, 628, 1006
    header_top, header_height = 146, 35
    table_y = header_top + header_height
    row_heights: Dict[int, int] = {}
    for year in years:
        entries = max(
            len(by_year_lane[(year, CURATED_REFERENCE_LANE)]),
            len(by_year_lane[(year, CURATED_EPS_LANE)]),
            1,
        )
        row_heights[year] = max(30, 8 + entries * 22)
    height = table_y + sum(row_heights.values()) + 22
    if height > 850:
        raise ValidationError(f"Selected evidence map exceeds its 850-unit page-height limit: {height}")

    body: List[str] = [
        svg_text(width / 2, 29, title, size=20, anchor="middle", weight="bold"),
        svg_text(
            width / 2, 53,
            f"Selected evidence map (n={len(rows)}); not an all-corpus aggregate or a derivation chain.",
            size=13, anchor="middle", color="#4B5563",
        ),
        svg_text(
            width / 2, 74,
            "Colors = coded EPS relevance; heavy outlines = executable/model-based checks or simulation-in-the-loop.",
            size=13, anchor="middle", color="#4B5563",
        ),
    ]
    color_legend = [
        (38, 101, "#2CA25F", "Power-budget/electrical architecture"),
        (316, 101, "#60A5FA", "EPS-adjacent"),
        (500, 101, "#9CA3AF", "System-level only"),
        (690, 101, "#F59E0B", "EPS-specific"),
    ]
    for x, y, color, label in color_legend:
        body.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}" stroke="#64748B" stroke-width="1"/>')
        body.append(svg_text(x + 11, y + 4, label, size=12, color="#374151"))
    body.append('<circle cx="38" cy="125" r="7" fill="#F8FAFC" stroke="#111827" stroke-width="3"/>')
    body.append(svg_text(51, 129, "Heavy outline = executable/model-based checks or simulation-in-the-loop", size=12, color="#374151"))
    body.append('<polygon points="550,118 557,125 550,132 543,125" fill="#2CA25F" stroke="#64748B" stroke-width="1"/>')
    body.append(svg_text(562, 129, "Diamond = protocol-boundary report; coded EPS relevance retained", size=12, color="#374151"))

    body.append(f'<rect x="{year_left}" y="{header_top}" width="{right - year_left}" height="{header_height}" fill="#E2E8F0" stroke="#94A3B8" stroke-width="1"/>')
    body.append(svg_text((year_left + reference_left) / 2, header_top + 22, "Year", size=14, anchor="middle", weight="bold", color="#1F2937"))
    body.append(svg_text((reference_left + eps_left) / 2, header_top + 22, CURATED_REFERENCE_LANE, size=14, anchor="middle", weight="bold", color="#1F2937"))
    body.append(svg_text((eps_left + right) / 2, header_top + 22, "EPS-focused reports / protocol boundary", size=14, anchor="middle", weight="bold", color="#1F2937"))

    y = table_y
    for year_index, year in enumerate(years):
        row_height = row_heights[year]
        row_fill = "#F8FAFC" if year_index % 2 == 0 else "#FFFFFF"
        body.append(f'<rect x="{year_left}" y="{y}" width="{right - year_left}" height="{row_height}" fill="{row_fill}" stroke="#CBD5E1" stroke-width="0.8"/>')
        body.append(f'<line x1="{reference_left}" y1="{y}" x2="{reference_left}" y2="{y + row_height}" stroke="#CBD5E1" stroke-width="0.8"/>')
        body.append(f'<line x1="{eps_left}" y1="{y}" x2="{eps_left}" y2="{y + row_height}" stroke="#CBD5E1" stroke-width="0.8"/>')
        body.append(svg_text((year_left + reference_left) / 2, y + 21, str(year), size=14, anchor="middle", weight="bold", color="#374151"))
        for lane, x in ((CURATED_REFERENCE_LANE, reference_left + 16), (CURATED_EPS_LANE, eps_left + 16)):
            for entry_index, row in enumerate(by_year_lane[(year, lane)]):
                text_y = y + 19 + entry_index * 22
                marker_y = text_y - 5
                fill = colors.get(str(row["coded_eps_relevance"]), "#E5E7EB")
                outlined = row["executable_or_simulation_evidence"] == "yes"
                is_boundary = row["paper_id"] == CURATED_BOUNDARY_ID
                stroke = "#111827" if outlined else "#64748B"
                stroke_width = 3 if outlined else 1.2
                if is_boundary:
                    body.append(f'<polygon points="{x},{marker_y - 8} {x + 8},{marker_y} {x},{marker_y + 8} {x - 8},{marker_y}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>')
                else:
                    body.append(f'<circle cx="{x}" cy="{marker_y}" r="7" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>')
                body.append(svg_text(x + 14, text_y, row["display_label"], size=15, color="#111827"))
        y += row_height
    return svg_document(width, height, title, "\n".join(body))


def render_figure_triplets(svgs: Mapping[str, str]) -> None:
    """Convert all figures before replacing any target; fail without stale files."""
    expected = set(FIGURE_NAMES)
    if set(svgs) != expected:
        raise ValidationError(f"Figure set mismatch: expected={sorted(expected)}, got={sorted(svgs)}")
    converter = shutil.which("rsvg-convert")
    if not converter:
        for name in FIGURE_NAMES:
            for suffix in (".svg", ".pdf", ".png"):
                (FIG_DIR / f"{name}{suffix}").unlink(missing_ok=True)
        raise RuntimeError(
            "Cannot produce required PDF/PNG figure derivatives: rsvg-convert is not available. "
            "Stale target figure files were removed."
        )

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    # librsvg honors SOURCE_DATE_EPOCH for deterministic PDF object streams.
    # Pin locale/time-zone too so font and numeric formatting cannot depend on
    # the invoking shell environment.
    render_env = os.environ.copy()
    render_env.update({"SOURCE_DATE_EPOCH": "0", "TZ": "UTC", "LC_ALL": "C"})
    temporary = Path(tempfile.mkdtemp(prefix=".slr-render-", dir=FIG_DIR))
    try:
        for name in FIGURE_NAMES:
            svg_path = temporary / f"{name}.svg"
            svg_path.write_text(svgs[name], encoding="utf-8")
            for fmt in ("pdf", "png"):
                output = temporary / f"{name}.{fmt}"
                result = subprocess.run(
                    [converter, "-f", fmt, "-o", str(output), str(svg_path)],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    env=render_env,
                )
                if result.returncode != 0 or not output.exists() or output.stat().st_size == 0:
                    details = result.stderr.strip() or result.stdout.strip() or "no converter diagnostics"
                    raise RuntimeError(f"rsvg-convert failed for {name}.{fmt}: {details}")
        # Commit only after every SVG/PDF/PNG derivative exists and is nonempty.
        for name in FIGURE_NAMES:
            for suffix in (".svg", ".pdf", ".png"):
                source = temporary / f"{name}{suffix}"
                if not source.exists() or source.stat().st_size == 0:
                    raise RuntimeError(f"Missing rendered derivative: {source.name}")
                os.replace(source, FIG_DIR / f"{name}{suffix}")
    except Exception as exc:
        # A partial replacement is less misleading than a stale derivative.
        for name in FIGURE_NAMES:
            for suffix in (".svg", ".pdf", ".png"):
                (FIG_DIR / f"{name}{suffix}").unlink(missing_ok=True)
        raise RuntimeError(
            "Required figure conversion failed; stale SVG/PDF/PNG targets were removed. "
            f"Cause: {exc}"
        ) from exc
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


# ---------------------------------------------------------------------------
# Publication-facing LaTeX and Markdown


def tex_escape(value: Any) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in clean_text(value))


def latex_table(
    caption: str,
    label: str,
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    *,
    small: bool = False,
    environment: str = "table",
    column_spec: str | None = None,
) -> str:
    """Build a deterministic table, allowing readable full-width wrapped layouts."""
    columns = column_spec or ("l" + "r" * (len(headers) - 1))
    result = [f"\\begin{{{environment}}}[htbp]", r"\centering"]
    if small:
        result.append(r"\small")
    result.extend([
        f"\\caption{{{tex_escape(caption)}}}",
        f"\\label{{{label}}}",
        f"\\begin{{tabular}}{{{columns}}}",
        r"\toprule",
        " & ".join(tex_escape(header) for header in headers) + r" \\",
        r"\midrule",
    ])
    for row in rows:
        result.append(" & ".join(tex_escape(value) for value in row) + r" \\")
    result.extend([r"\bottomrule", r"\end{tabular}", f"\\end{{{environment}}}"])
    return "\n".join(result)


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(clean_text(value).replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def matrix_value(rows: Sequence[Mapping[str, Any]], first: str, second: str, first_value: str, second_value: str) -> int:
    for row in rows:
        if row[first] == first_value and row[second] == second_value:
            return int(row["count"])
    return 0


def write_results_tables(
    studies: Sequence[StudyRecord],
    codebook: Mapping[str, Any],
    *,
    eps_rows: Sequence[Mapping[str, Any]],
    approach_rows: Sequence[Mapping[str, Any]],
    maturity_rows: Sequence[Mapping[str, Any]],
    artifact_rows: Sequence[Mapping[str, Any]],
    eps_element_rows: Sequence[Mapping[str, Any]],
    interop_rows: Sequence[Mapping[str, Any]],
    limitation_rows: Sequence[Mapping[str, Any]],
    claim_rows: Sequence[Mapping[str, Any]],
    specificity_rows: Sequence[Mapping[str, Any]],
    baseline_rows: Sequence[Mapping[str, Any]],
    specificity_confidence_rows: Sequence[Mapping[str, Any]],
    reliability_rows: Sequence[Mapping[str, Any]],
    prephysical_rows: Sequence[Mapping[str, Any]],
    vv_artifact_rows: Sequence[Mapping[str, Any]],
    readiness_rows: Sequence[Mapping[str, Any]],
    vv_rows: Sequence[Mapping[str, Any]],
    ivv_rows: Sequence[Mapping[str, Any]],
    governance_rows: Sequence[Mapping[str, Any]],
    gap_rows: Sequence[Mapping[str, Any]],
) -> None:
    claims = all_claims(studies)
    tier_counts = Counter(study_field_text(study, P_TIER) for study in studies)
    confidence_counts = Counter(single_category(claim.fields[P_CLAIM_CONFIDENCE]) for claim in claims)
    extraction_confidence = Counter(study_field_text(study, P_EXTRACTION_CONFIDENCE) for study in studies)

    def status_caption(observations: Sequence[FieldObservation]) -> str:
        denominator = len(observations)
        counts = Counter(observation.status for observation in observations)
        labels = {
            "coded": "coded",
            "not_reported": "not reported",
            "not_applicable": "not applicable",
            "none": "none",
            "uncertain": "uncertain",
            UNASSIGNED_STATUS: "unassigned status",
        }
        nonzero = [
            f"{labels[status]} {counts.get(status, 0)}/{denominator}"
            for status in (*codebook["status_values"], UNASSIGNED_STATUS)
            if status != "coded" and counts.get(status, 0)
        ]
        text = f"field status: coded {counts.get('coded', 0)}/{denominator}"
        if nonzero:
            text += "; " + "; ".join(nonzero)
        return text + f"; all other statuses 0/{denominator}"

    def study_status(path: str) -> str:
        return status_caption([study.fields[path] for study in studies])

    def claim_status(path: str) -> str:
        return status_caption([claim.fields[path] for claim in claims])

    p_left = lambda width: rf">{{\raggedright\arraybackslash}}p{{{width}}}"
    p_center = lambda width: rf">{{\centering\arraybackslash}}p{{{width}}}"
    vv_observations = [
        study.fields[path]
        for study in studies
        for path in (P_VV_ARTIFACTS, P_PREPHYSICAL, P_TEST_READINESS)
    ]

    def direct_status_vector(path: str) -> str:
        counts = Counter(study.fields[path].status for study in studies)
        return "/".join(str(counts.get(status, 0)) for status in codebook["status_values"])

    direct_vv_groups = (
        ("Explicitly pre-physical verification mechanism", prephysical_rows),
        ("Verification/validation artifacts", vv_artifact_rows),
        ("Integration/test readiness", readiness_rows),
    )
    direct_vv_table_rows = [
        (source_label if index == 0 else "", row["category"], row["count"])
        for source_label, rows in direct_vv_groups
        for index, row in enumerate(rows)
    ]
    parts = [
        "% Auto-generated controlled-code evidence tables. Do not edit by hand.",
        "% Units: report counts use unique report memberships; claim counts use unique nested claims.",
        latex_table(
            "Corpus and claim-record summary. Claims are nested in reports and are not independent implementations.",
            "tab:slr-corpus-summary",
            ["Metric", "n"],
            [
                ("Reports", len(studies)),
                ("Core reports", tier_counts.get("core", 0)),
                ("Supporting reports", tier_counts.get("supporting", 0)),
                ("Nested claim records", len(claims)),
                ("Unsupported claims", confidence_counts.get("Unsupported", 0)),
                ("Weak claims", confidence_counts.get("Weak", 0)),
                ("Moderate claims", confidence_counts.get("Moderate", 0)),
                ("Strong claims", confidence_counts.get("Strong", 0)),
                ("High-confidence extractions", extraction_confidence.get("high", 0)),
                ("Medium-confidence extractions", extraction_confidence.get("medium", 0)),
                ("Invalid baseline comparator values", field_value_count(baseline_rows, UNMAPPED)),
            ],
            column_spec=p_left(r"0.70\linewidth") + "r",
        ),
        latex_table(
            f"Mutually exclusive controlled EPS-relevance categories by report (n={len(studies)}; {study_status(P_EPS)}).",
            "tab:eps-relevance-counts",
            ["EPS relevance", "n"],
            [(row["category"], row["count"]) for row in eps_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Report-level multi-label model-maturity memberships (n={len(studies)}; {study_status(P_MATURITY)}).",
            "tab:model-maturity-counts",
            ["Model maturity", "n"],
            [(row["category"], row["count"]) for row in maturity_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Mutually exclusive approach classification by report (n={len(studies)}; {study_status(P_APPROACH)}).",
            "tab:approach-classification-counts",
            ["Approach classification", "n"],
            [(row["category"], row["count"]) for row in approach_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Report-level multi-label model-artifact memberships (n={len(studies)}; {study_status(P_ARTIFACTS)}).",
            "tab:model-artifacts-counts",
            ["Model artifact", "n"],
            [(row["category"], row["count"]) for row in artifact_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Report-level multi-label EPS-element memberships (n={len(studies)}; {study_status(P_EPS_ELEMENTS)}); {field_value_count(eps_element_rows, UNASSIGNED_VALUE)} reports have no selected controlled value.",
            "tab:eps-elements-modeled-counts",
            ["EPS element modeled", "n"],
            [(row["category"], row["count"]) for row in eps_element_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Report-level multi-label interoperability-mechanism memberships (n={len(studies)}; {study_status(P_INTEROP)}); {field_value_count(interop_rows, UNASSIGNED_VALUE)} reports have no selected controlled value.",
            "tab:interoperability-mechanisms-counts",
            ["Mechanism", "n"],
            [(row["category"], row["count"]) for row in interop_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Report-level multi-label toolchain-limitation memberships (n={len(studies)}; {study_status(P_TOOL_LIMITATIONS)}); {field_value_count(limitation_rows, UNASSIGNED_VALUE)} reports have no selected controlled value.",
            "tab:toolchain-limitations-counts",
            ["Limitation", "n"],
            [(row["category"], row["count"]) for row in limitation_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Controlled outcome-domain evidence from n={len(claims)} nested claims. Rows are claim-domain memberships and domains can overlap; confidence columns partition each row. Outcome {claim_status(P_CLAIM_OUTCOME)}; confidence {claim_status(P_CLAIM_CONFIDENCE)}.",
            "tab:claim-evidence-by-outcome",
            ["Outcome domain", "Total", "Unsup.", "Weak", "Mod.", "Strong"],
            [
                (
                    row["outcome_domain"], row["total_claim_domain_memberships"], row["unsupported"],
                    row["weak"], row["moderate"], row["strong"],
                )
                for row in claim_rows
            ],
            environment="table*",
            column_spec=p_left(r"0.44\textwidth") + "rrrrr",
        ),
        latex_table(
            f"Claim specificity by evidence confidence (n={len(claims)} nested claims). Both fields are single-select, so cells are mutually exclusive; unmapped/invalid and unassigned groups are retained. Specificity {claim_status(P_CLAIM_SPECIFICITY)}; confidence {claim_status(P_CLAIM_CONFIDENCE)}.",
            "tab:claim-specificity-confidence",
            ["Claim specificity", *codebook_allowed(codebook, P_CLAIM_CONFIDENCE)],
            [
                [
                    specificity,
                    *[
                        matrix_value(
                            specificity_confidence_rows,
                            "claim_specificity",
                            "evidence_confidence",
                            specificity,
                            confidence,
                        )
                        for confidence in codebook_allowed(codebook, P_CLAIM_CONFIDENCE)
                    ],
                ]
                for specificity in [*codebook_allowed(codebook, P_CLAIM_SPECIFICITY), UNMAPPED, UNASSIGNED_VALUE]
            ],
            environment="table*",
            column_spec=p_left(r"0.48\textwidth") + "rrrr",
        ),
        latex_table(
            f"Mutually exclusive baseline/comparator coding by nested claim (n={len(claims)}; {claim_status(P_CLAIM_BASELINE)}). Five invalid baseline strings remain in the explicit unmapped/invalid class and were not recoded.",
            "tab:baseline-comparator-counts",
            ["Baseline/comparator", "n"],
            [(row["category"], row["count"]) for row in baseline_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Claim-level multi-label reliability-subtype memberships (n={len(claims)}; {claim_status(P_CLAIM_RELIABILITY)}).",
            "tab:reliability-subtype-counts",
            ["Reliability subtype", "n"],
            [(row["category"], row["count"]) for row in reliability_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Direct controlled-source V&V fields by report (n={len(studies)}; multi-label memberships). Status order coded/not reported/not applicable/none/uncertain: explicitly pre-physical mechanisms {direct_status_vector(P_PREPHYSICAL)}; V&V artifacts {direct_status_vector(P_VV_ARTIFACTS)}; integration/test readiness {direct_status_vector(P_TEST_READINESS)}. Zero categories and no-selected-value QA classes are retained.",
            "tab:vv-direct-field-counts",
            ["Direct source field", "Controlled category", "n"],
            direct_vv_table_rows,
            small=True,
            environment="table*",
            column_spec=p_left(r"0.31\textwidth") + p_left(r"0.53\textwidth") + "r",
        ),
        latex_table(
            f"Derived V&V linkage categories by report (n={len(studies)}); categories can overlap. This is a mixed-source union across direct verification/validation-artifact, explicitly pre-physical-mechanism, and integration/test-readiness fields; the generic/planned fallback additionally uses controlled RQ3 relevance when no coded artifact or pre-physical mechanism is selected. It does not mean every category is directly pre-physical. A readiness link is distinct from completed integration/test closure. Source V&V fields have {status_caption(vv_observations)}.",
            "tab:vv-linkage-counts",
            ["Derived V&V linkage category", "n"],
            [(row["vv_linkage_category"], row["count"]) for row in vv_rows],
            environment="table*",
            column_spec=p_left(r"0.80\textwidth") + "r",
        ),
        latex_table(
            f"IVV integration level by report (n={len(studies)}; {study_status(P_IVV)}). 'none/not reported' is a controlled level; {field_value_count(ivv_rows, UNASSIGNED_VALUE)} reports have no selected IVV level.",
            "tab:ivv-integration-level-counts",
            ["IVV integration level", "n"],
            [(row["category"], row["count"]) for row in ivv_rows],
            column_spec=p_left(r"0.74\linewidth") + "r",
        ),
        latex_table(
            f"Separate governance, ROI, and all-study governance-gap measures (n={len(studies)} reports). Governance and ROI rows are multi-label memberships; the gap-classification rows are mutually exclusive. Governance {study_status(P_GOVERNANCE)}; ROI {study_status(P_ROI)}; gap classification {study_status(P_GOVERNANCE_GAP)}.",
            "tab:governance-roi-counts",
            ["Measure", "Category", "n"],
            [
                (row["measure_group"], row["category"], row["count"])
                for row in governance_rows
            ],
            environment="table*",
            column_spec=p_left(r"0.30\textwidth") + p_left(r"0.50\textwidth") + "r",
        ),
    ]

    gap_statuses = codebook_allowed(codebook, GAP_FIELDS[0][0])
    gap_table_rows: List[List[Any]] = []
    for _, label in GAP_FIELDS:
        selected = [row for row in gap_rows if row["gap_label"] == label]
        by_status = {row["classification"]: row["count"] for row in selected}
        gap_table_rows.append([label, *[by_status.get(status, 0) for status in gap_statuses]])
    parts.append(
        latex_table(
            f"All-study gap mapping using pre-specified controlled classifications. Each gap row is mutually exclusive across n={len(studies)} reports; {study_status(GAP_FIELDS[0][0])} for every gap field.",
            "tab:gap-mapping-counts",
            ["Gap", *gap_statuses],
            gap_table_rows,
            environment="table*",
            column_spec=p_left(r"0.34\textwidth") + p_center(r"0.115\textwidth") * len(gap_statuses),
        )
    )
    parts.append(
        "% Supplementary CSVs retain complete codebook-ordered maturity × EPS, lifecycle × IVV, and EPS-elements × V&V co-reporting matrices. These are cross-classifications only / not progression, causal linkage, or element-level V&V relationships."
    )
    (DRAFTS_DIR / "results_tables.tex").write_text("\n\n".join(parts) + "\n", encoding="utf-8")


def read_protocol_rqs() -> List[str]:
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    match = re.search(r"## Research questions\n(?P<body>.*?)(?:\n## |\Z)", text, flags=re.S)
    if not match:
        return []
    rqs: List[str] = []
    for line in match.group("body").splitlines():
        item = re.match(r"\s*(\d+)\.\s*(.*)", line)
        if item:
            rqs.append(f"RQ{item.group(1)}: {clean_text(item.group(2))}")
    return rqs


def parse_prisma_counts() -> Dict[str, int]:
    if not SCOPING_TEX.exists():
        raise ValidationError(f"Missing scoping-review flow source: {SCOPING_TEX}")
    text = SCOPING_TEX.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(\d+)\s+raw merged search records,\s*(\d+)\s+duplicates removed,\s*(\d+)\s+unique records screened,\s*"
        r"(\d+)\s+excluded during screening,\s*(\d+)\s+reports sought for retrieval,\s*(\d+)\s+not retrieved/inaccessible,\s*and\s*(\d+)\s+extracted",
        flags=re.I,
    )
    match = pattern.search(text)
    if not match:
        raise ValidationError("Could not parse PRISMA flow counts from scoping-review.tex")
    raw, duplicates, screened, excluded, reports, not_retrieved, extracted = map(int, match.groups())
    return {
        "raw_records": raw,
        "duplicates_removed": duplicates,
        "unique_records_screened": screened,
        "excluded_screening": excluded,
        "reports_sought": reports,
        "not_retrieved": not_retrieved,
        "extracted": extracted,
    }


def write_data_summary(
    studies: Sequence[StudyRecord],
    codebook: Mapping[str, Any],
    *,
    eps_rows: Sequence[Mapping[str, Any]],
    maturity_rows: Sequence[Mapping[str, Any]],
    lifecycle_rows: Sequence[Mapping[str, Any]],
    artifact_rows: Sequence[Mapping[str, Any]],
    eps_element_rows: Sequence[Mapping[str, Any]],
    interop_rows: Sequence[Mapping[str, Any]],
    limitation_rows: Sequence[Mapping[str, Any]],
    specificity_rows: Sequence[Mapping[str, Any]],
    evidence_rows: Sequence[Mapping[str, Any]],
    baseline_rows: Sequence[Mapping[str, Any]],
    prephysical_rows: Sequence[Mapping[str, Any]],
    vv_artifact_rows: Sequence[Mapping[str, Any]],
    readiness_rows: Sequence[Mapping[str, Any]],
    vv_rows: Sequence[Mapping[str, Any]],
    ivv_rows: Sequence[Mapping[str, Any]],
    governance_rows: Sequence[Mapping[str, Any]],
    claim_rows: Sequence[Mapping[str, Any]],
    top_rows: Sequence[Mapping[str, Any]],
    coverage_rows: Sequence[Mapping[str, Any]],
    prisma_counts: Mapping[str, int],
) -> None:
    claims = all_claims(studies)
    tier_counts = Counter(study_field_text(study, P_TIER) for study in studies)
    confidence_counts = Counter(single_category(claim.fields[P_CLAIM_CONFIDENCE]) for claim in claims)
    extraction_counts = Counter(study_field_text(study, P_EXTRACTION_CONFIDENCE) for study in studies)
    eps_element_statuses = Counter(study.fields[P_EPS_ELEMENTS].status for study in studies)
    interop_statuses = Counter(study.fields[P_INTEROP].status for study in studies)
    limitation_statuses = Counter(study.fields[P_TOOL_LIMITATIONS].status for study in studies)
    rqs = read_protocol_rqs()

    baseline_invalid = field_value_count(baseline_rows, UNMAPPED)
    mechanism_qa = [
        row for row in coverage_rows
        if row["source_scope"] == "canonical_claim_record"
        and row["field_path"] == P_CLAIM_MECHANISM
        and row["coverage_category"] == UNMAPPED
    ]
    invalid_mechanism_count = int(mechanism_qa[0]["record_count"]) if mechanism_qa else 0

    def direct_status_coverage(path: str) -> str:
        counts = Counter(study.fields[path].status for study in studies)
        labels = (*codebook["status_values"], UNASSIGNED_STATUS)
        return "; ".join(
            f"{status.replace('_', ' ')}={counts.get(status, 0)}/{len(studies)}"
            for status in labels
        )

    coverage_specs: List[Tuple[str, str, List[FieldObservation]]] = [
        ("Lifecycle stage addressed", "report", [study.fields[P_LIFECYCLE] for study in studies]),
        ("Development context", "report", [study.fields[P_DEVELOPMENT_CONTEXT] for study in studies]),
        ("Model maturity", "report", [study.fields[P_MATURITY] for study in studies]),
        ("Model artifacts used", "report", [study.fields[P_ARTIFACTS] for study in studies]),
        ("EPS elements modeled", "report", [study.fields[P_EPS_ELEMENTS] for study in studies]),
        ("Interoperability mechanisms", "report", [study.fields[P_INTEROP] for study in studies]),
        ("Toolchain limitations", "report", [study.fields[P_TOOL_LIMITATIONS] for study in studies]),
        ("Verification/validation artifacts", "report", [study.fields[P_VV_ARTIFACTS] for study in studies]),
        ("Pre-physical verification mechanism", "report", [study.fields[P_PREPHYSICAL] for study in studies]),
        ("Integration/test readiness", "report", [study.fields[P_TEST_READINESS] for study in studies]),
        ("IVV integration level", "report", [study.fields[P_IVV] for study in studies]),
        ("Model governance strategy", "report", [study.fields[P_GOVERNANCE] for study in studies]),
        ("ROI/value-realization evidence", "report", [study.fields[P_ROI] for study in studies]),
        ("Claim specificity", "claim", [claim.fields[P_CLAIM_SPECIFICITY] for claim in claims]),
        ("Evidence type", "claim", [claim.fields[P_CLAIM_EVIDENCE_TYPE] for claim in claims]),
        ("Baseline comparator", "claim", [claim.fields[P_CLAIM_BASELINE] for claim in claims]),
    ]
    coverage_summary_rows: List[List[str]] = []
    for label, unit, observations in coverage_specs:
        statuses_for_field = Counter(observation.status for observation in observations)
        denominator = len(observations)
        coverage_summary_rows.append([
            label,
            f"{unit} N={denominator}",
            f"{statuses_for_field.get('coded', 0)}/{denominator}",
            f"{statuses_for_field.get('not_reported', 0)}/{denominator}",
            f"{statuses_for_field.get('not_applicable', 0)}/{denominator}",
            f"{statuses_for_field.get('none', 0)}/{denominator}",
            f"{statuses_for_field.get('uncertain', 0)}/{denominator}",
            f"{statuses_for_field.get(UNASSIGNED_STATUS, 0)}/{denominator}",
            f"{sum(not observation.values and not observation.invalid_values for observation in observations)}/{denominator}",
        ])

    lines: List[str] = [
        "# Systematic-review controlled evidence-artifact summary",
        "",
        "## Scope and units",
        "",
        f"The artifact set summarizes **{len(studies)} reports** and **{len(claims)} claim records**. Claims are nested within reports; neither reports nor claims are treated as independent implementations.",
        "Study multi-select outputs count unique report memberships. Claim multi-select outputs count unique claim memberships. Every count CSV gives its denominator and status coverage; codebook-ordered zero categories are retained. `study_characteristics.csv` retains the controlled development-context field and its field status.",
    ]
    if rqs:
        lines.extend(["", "Registered review questions: " + "; ".join(rqs) + "."])
    lines.extend([
        "",
        "## Generated outputs",
        "",
        "### CSV data",
        "",
        *[f"- `data/{name}`" for name in (*EXISTING_CSV_NAMES, *PLANNED_CSV_NAMES, *ADDITIONAL_CSV_NAMES)],
        "",
        "### Figures",
        "",
        "SVG outputs: " + ", ".join(f"`figures/{name}.svg`" for name in FIGURE_NAMES) + ".",
        "Each SVG has matching PDF and PNG derivatives. The maturity × EPS and lifecycle × IVV figures are controlled study-level cross-classifications only / not progression or direct linkage. The lifecycle × IVV display treats `none/not reported` as a controlled level and separately identifies the three reports with no selected IVV level. The claim-anatomy figure retains unmapped/invalid and unassigned classes and defines `comparator recorded`.",
        "",
        "### Manuscript snippets",
        "",
        "- `drafts/results_tables.tex`",
        "- `drafts/data_summary.md`",
        "",
        "## Corpus and evidence counts",
        "",
        markdown_table(
            ["Metric", "Count"],
            [
                ("Reports", len(studies)),
                ("Core reports", tier_counts.get("core", 0)),
                ("Supporting reports", tier_counts.get("supporting", 0)),
                ("Publication year range", f"{min(study.year for study in studies)}–{max(study.year for study in studies)}"),
                ("Nested claim records", len(claims)),
                ("Moderate/Strong claim records", len(top_rows)),
                ("High-confidence extractions", extraction_counts.get("high", 0)),
                ("Medium-confidence extractions", extraction_counts.get("medium", 0)),
                ("Unmapped/invalid baseline values", baseline_invalid),
                ("Unmapped/invalid MBSE mechanism values", invalid_mechanism_count),
            ],
        ),
        "",
        "Claim evidence confidence: " + ", ".join(
            f"{category}={confidence_counts.get(category, 0)}"
            for category in [*codebook_allowed(codebook, P_CLAIM_CONFIDENCE), UNMAPPED, UNASSIGNED_VALUE]
        ) + ".",
        "",
        "## Key controlled aggregates",
        "",
        "### EPS relevance and model maturity",
        "",
        markdown_table(["EPS relevance", "Report memberships (n=40)"], [(row["category"], row["count"]) for row in eps_rows]),
        "",
        markdown_table(["Model maturity", "Report memberships (n=40)"], [(row["category"], row["count"]) for row in maturity_rows]),
        "",
        markdown_table(["Lifecycle stage addressed", "Report memberships (n=40; multi-label)"], [(row["category"], row["count"]) for row in lifecycle_rows]),
        "",
        "### Model artifacts, EPS elements, toolchain, and claim evidence",
        "",
        markdown_table(["Model artifact used", "Report memberships (n=40; multi-label)"], [(row["category"], row["count"]) for row in artifact_rows]),
        "",
        markdown_table(["EPS element modeled", "Report memberships (n=40; multi-label)"], [(row["category"], row["count"]) for row in eps_element_rows]),
        "",
        f"The EPS-elements figure states coded coverage {eps_element_statuses.get('coded', 0)}/{len(studies)} and statuses not reported={eps_element_statuses.get('not_reported', 0)}, not applicable={eps_element_statuses.get('not_applicable', 0)}, none={eps_element_statuses.get('none', 0)}. Its separated neutral bar shows the {field_value_count(eps_element_rows, UNASSIGNED_VALUE)} reports with no selected controlled value; that bar is not an EPS element.",
        "",
        markdown_table(["Interoperability mechanism", "Report memberships (n=40; multi-label)"], [(row["category"], row["count"]) for row in interop_rows]),
        "",
        markdown_table(["Toolchain limitation", "Report memberships (n=40; multi-label)"], [(row["category"], row["count"]) for row in limitation_rows]),
        "",
        f"The toolchain figure gives field-status context: interoperability coded {interop_statuses.get('coded', 0)}/{len(studies)}, not-reported status {interop_statuses.get('not_reported', 0)}, uncertain {interop_statuses.get('uncertain', 0)}; limitations coded {limitation_statuses.get('coded', 0)}/{len(studies)}, not-reported status {limitation_statuses.get('not_reported', 0)}. It shows separated neutral no-selected-value bars ({field_value_count(interop_rows, UNASSIGNED_VALUE)} and {field_value_count(limitation_rows, UNASSIGNED_VALUE)}), not a misleading `not reported` category bar.",
        "",
        markdown_table(["Claim specificity", "Claim memberships (n=270)"], [(row["category"], row["count"]) for row in specificity_rows]),
        "",
        markdown_table(["Evidence type", "Claim memberships (n=270; multi-label)"], [(row["category"], row["count"]) for row in evidence_rows]),
        "",
        markdown_table(["Baseline/comparator", "Claim memberships (n=270)"], [(row["category"], row["count"]) for row in baseline_rows]),
        "",
        markdown_table(["Controlled outcome domain", "Claim-domain memberships (n=270 nested claims; domains can overlap)"], [(row["outcome_domain"], row["total_claim_domain_memberships"]) for row in claim_rows]),
        "",
        "### Direct V&V source fields and derived linkage",
        "",
        "RQ3 direct controlled fields are reported separately from the derived linkage map. Reports with at least one coded value are 26 for explicitly pre-physical verification mechanisms, 24 for verification/validation artifacts, and 10 for integration/test readiness. Their status coverage is: explicitly pre-physical verification mechanisms, " + direct_status_coverage(P_PREPHYSICAL) + "; verification/validation artifacts, " + direct_status_coverage(P_VV_ARTIFACTS) + "; integration/test readiness, " + direct_status_coverage(P_TEST_READINESS) + ".",
        "",
        markdown_table(["Pre-physical verification mechanism", "Report memberships (n=40; multi-label)"], [(row["category"], row["count"]) for row in prephysical_rows]),
        "",
        markdown_table(["Verification/validation artifact", "Report memberships (n=40; multi-label)"], [(row["category"], row["count"]) for row in vv_artifact_rows]),
        "",
        markdown_table(["Integration/test readiness", "Report memberships (n=40; multi-label)"], [(row["category"], row["count"]) for row in readiness_rows]),
        "",
        "Derived V&V linkage categories are a mixed-source union of coded values across verification/validation artifacts, explicitly pre-physical verification mechanisms, and integration/test readiness. The generic/planned fallback additionally uses controlled RQ3 relevance when no coded artifact or pre-physical mechanism is selected. The map is not a direct pre-physical-only measure: only the mechanism source field is explicitly pre-physical. A readiness link denotes readiness, not completed integration/test closure.",
        "",
        markdown_table(["Derived V&V linkage category", "Derived report memberships (n=40; categories can overlap)"], [(row["vv_linkage_category"], row["count"]) for row in vv_rows]),
        "",
        "### IVV and governance/ROI",
        "",
        markdown_table(["IVV integration level", "Report memberships (n=40)"], [(row["category"], row["count"]) for row in ivv_rows]),
        "",
        "`none/not reported` is a controlled IVV level (10 reports), distinct from the three reports with no selected IVV level.",
        "",
        markdown_table(
            ["Separate controlled measure", "Category", "Report memberships (n=40)"],
            [(row["measure_group"], row["category"], row["count"]) for row in governance_rows],
        ),
        "",
        "The governance/ROI table deliberately does not derive project-decision counts from claim prose or outcome categories. It separately reports the model-governance field, ROI/value-realization field, and existing all-study governance gap classification.",
        "",
        "## Field coverage and unassigned values",
        "",
        "Status entries are n/N records for the named field. `Unassigned value` means that the record contains no selected controlled label; it is distinct from an explicit `not reported`, `none`, `not applicable`, or `uncertain` status.",
        "",
        markdown_table(
            ["Field", "Unit", "coded", "not reported", "not applicable", "none", "uncertain", "unassigned status", "unassigned value"],
            coverage_summary_rows,
        ),
        "",
        "## PRISMA flow",
        "",
        f"The PRISMA figure is rendered from parsed flow counts, not copied from another figure: raw records={prisma_counts['raw_records']}; duplicates removed={prisma_counts['duplicates_removed']}; screened={prisma_counts['unique_records_screened']}; excluded={prisma_counts['excluded_screening']}; reports sought={prisma_counts['reports_sought']}; not retrieved={prisma_counts['not_retrieved']}; reports included={prisma_counts['extracted']}.",
        "",
        "## Assumptions",
        "",
        "- Outcome-domain synthesis uses the declared exact-code mapping only; a controlled `generality/reuse` code can contribute to both reuse and generality domains, while uncontrolled outcome text cannot create a domain membership.",
        "- In the claim-anatomy figure, `comparator recorded` groups only the four exact baseline codes `previous document-centric process`, `manual analysis`, `alternative toolchain`, and `previous mission`. `none`, `not reported`, unmapped/invalid, and unassigned remain separate.",
        "- Matrix cells are report or claim memberships, as stated in each CSV; multi-label fields can make matrix totals exceed the number of reports or claims. The maturity × EPS and lifecycle × IVV displays are cross-classifications only / not progression or direct linkage.",
        "",
        "## Controlled-code and QA safeguards",
        "",
        "- `extraction_codebook.json` is loaded at runtime. The generator validates codebook version 1.1, exact extraction-ID coverage, structured-summary field coverage, exact controlled labels, statuses, and applicable single-/multi-select cardinality.",
        "- Canonical claim fields normalize typed wrappers and the documented aliases `outcome_category|category`, `specificity_of_claim|specificity`, `mbse_mechanism|mechanism`, and `evidence_confidence_rating|evidence_confidence`. Stable claim references use `corpus_id:claim_id`, with an `id` alias or a 1-based index only when needed.",
        f"- The five non-codebook baseline strings in `paper-0007` are retained as `{UNMAPPED}` (n={baseline_invalid}); they are not mapped to `none` or `not reported`. The same explicit QA class captures the one invalid claim-level MBSE mechanism value.",
        "- `field_coverage_status.csv` includes status and selected-value coverage for every codebook field at the structured-summary level and, for canonical claim fields, at the claim-record level. It also records unmapped/invalid and unassigned classes.",
        "- Derived V&V linkage categories use only values whose source field has status `coded`; a non-coded selected value, including the allowed `not reported` literal, cannot create a derived V&V membership. The derived map mixes verification/validation-artifact, explicitly pre-physical-mechanism, and integration/test-readiness fields; it does not make every category directly pre-physical, and readiness is not completed integration/test closure.",
        "",
        "## Interpretation limits",
        "",
        "- All synthesis aggregates use controlled codes only. Claim text, quotations, open coding, and emergent observations are displayed only as audit context where applicable and never classify a count.",
        "- Multi-label co-reporting is not causal linkage. Lifecycle × IVV cells do not establish a developmental progression or direct linkage, and EPS-element × V&V-artifact cells do not establish element-level V&V relationships.",
        "- Report counts should not be interpreted as independent implementation counts; recurring reference-model lineages can represent related publications. The retained lineage graphic is a selected evidence map (n=19), not an all-corpus aggregate or a derivation chain; title-derived labels aid reading while corpus IDs remain in the CSV for audit, and outlines mean executable/model-based checks or simulation-in-the-loop.",
        "- Missing, none, not-reported, not-applicable, uncertain, and unassigned statuses are retained rather than filled from prose. The analysis performs no paper recoding.",
    ])
    (DRAFTS_DIR / "data_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main pipeline


def main() -> None:
    for directory in (DATA_DIR, FIG_DIR, DRAFTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    if not CODEBOOK_PATH.exists() or not EXTRACTION_INDEX.exists() or not PROTOCOL_PATH.exists():
        raise ValidationError("Missing required codebook, extraction index, or protocol input")

    codebook = read_json(CODEBOOK_PATH)
    extraction_index = read_json(EXTRACTION_INDEX)
    validate_codebook(codebook, extraction_index)
    validate_outcome_domain_map(codebook)
    studies = validate_and_load_studies(codebook, extraction_index)
    validate_index_quality_statistics(extraction_index, studies)
    claims = all_claims(studies)
    statuses = codebook["status_values"]

    # Existing count artifacts, upgraded to explicit units, denominators, status
    # coverage, zero categories, and claim-level units where applicable.
    study_rows = study_characteristic_rows(studies, codebook)
    eps_rows = count_rows(observations_for_studies(studies, P_EPS), P_EPS, codebook, unit="study membership (unique report)", id_column="study_ids")
    approach_rows = count_rows(observations_for_studies(studies, P_APPROACH), P_APPROACH, codebook, unit="study membership (unique report)", id_column="study_ids")
    generality_rows = count_rows(observations_for_studies(studies, P_GENERALITY), P_GENERALITY, codebook, unit="study membership (unique report)", id_column="study_ids")
    ivv_rows = count_rows(observations_for_studies(studies, P_IVV), P_IVV, codebook, unit="study membership (unique report)", id_column="study_ids")
    reliability_rows = count_rows(observations_for_claims(claims, P_CLAIM_RELIABILITY), P_CLAIM_RELIABILITY, codebook, unit="claim membership (unique nested claim)", id_column="claim_refs")
    # Direct RQ3 controlled fields remain distinct from the retained derived map.
    prephysical_rows = count_rows(observations_for_studies(studies, P_PREPHYSICAL), P_PREPHYSICAL, codebook, unit="study membership (unique report)", id_column="study_ids")
    vv_artifact_rows = count_rows(observations_for_studies(studies, P_VV_ARTIFACTS), P_VV_ARTIFACTS, codebook, unit="study membership (unique report)", id_column="study_ids")
    readiness_rows = count_rows(observations_for_studies(studies, P_TEST_READINESS), P_TEST_READINESS, codebook, unit="study membership (unique report)", id_column="study_ids")
    claim_rows, top_rows = claim_evidence_rows(studies, codebook)
    vv_rows = vv_linkage_rows(studies, codebook)
    gap_rows = gap_mapping_rows(studies, codebook)
    curated_rows = curated_lineage_rows(studies)

    # Other planned direct field counts.
    lifecycle_rows = count_rows(observations_for_studies(studies, P_LIFECYCLE), P_LIFECYCLE, codebook, unit="study membership (unique report)", id_column="study_ids")
    maturity_rows = count_rows(observations_for_studies(studies, P_MATURITY), P_MATURITY, codebook, unit="study membership (unique report)", id_column="study_ids")
    artifact_rows = count_rows(observations_for_studies(studies, P_ARTIFACTS), P_ARTIFACTS, codebook, unit="study membership (unique report)", id_column="study_ids")
    eps_element_rows = count_rows(observations_for_studies(studies, P_EPS_ELEMENTS), P_EPS_ELEMENTS, codebook, unit="study membership (unique report)", id_column="study_ids")
    interop_rows = count_rows(observations_for_studies(studies, P_INTEROP), P_INTEROP, codebook, unit="study membership (unique report)", id_column="study_ids")
    limitation_rows = count_rows(observations_for_studies(studies, P_TOOL_LIMITATIONS), P_TOOL_LIMITATIONS, codebook, unit="study membership (unique report)", id_column="study_ids")
    specificity_rows = count_rows(observations_for_claims(claims, P_CLAIM_SPECIFICITY), P_CLAIM_SPECIFICITY, codebook, unit="claim membership (unique nested claim)", id_column="claim_refs")
    evidence_rows = count_rows(observations_for_claims(claims, P_CLAIM_EVIDENCE_TYPE), P_CLAIM_EVIDENCE_TYPE, codebook, unit="claim membership (unique nested claim)", id_column="claim_refs")
    baseline_rows = count_rows(observations_for_claims(claims, P_CLAIM_BASELINE), P_CLAIM_BASELINE, codebook, unit="claim membership (unique nested claim)", id_column="claim_refs")
    governance_rows = governance_roi_rows(studies, codebook)

    # Complete codebook-ordered cross-tabs.  These count study/claim memberships,
    # never phrases in the extraction narrative.
    maturity_eps_rows = matrix_rows(
        [(study.corpus_id, study.fields[P_EPS], study.fields[P_MATURITY]) for study in studies],
        P_EPS, P_MATURITY, codebook,
        a_column="eps_relevance", b_column="model_maturity",
        unit="study co-reporting membership (unique report)", id_column="study_ids",
    )
    lifecycle_ivv_rows = matrix_rows(
        [(study.corpus_id, study.fields[P_LIFECYCLE], study.fields[P_IVV]) for study in studies],
        P_LIFECYCLE, P_IVV, codebook,
        a_column="lifecycle_stage", b_column="ivv_integration_level",
        unit="study co-reporting membership (unique report)", id_column="study_ids",
    )
    specificity_confidence_rows = matrix_rows(
        [(claim.claim_ref, claim.fields[P_CLAIM_SPECIFICITY], claim.fields[P_CLAIM_CONFIDENCE]) for claim in claims],
        P_CLAIM_SPECIFICITY, P_CLAIM_CONFIDENCE, codebook,
        a_column="claim_specificity", b_column="evidence_confidence",
        unit="claim co-reporting membership (unique nested claim)", id_column="claim_refs",
    )
    evidence_baseline_rows = matrix_rows(
        [(claim.claim_ref, claim.fields[P_CLAIM_EVIDENCE_TYPE], claim.fields[P_CLAIM_BASELINE]) for claim in claims],
        P_CLAIM_EVIDENCE_TYPE, P_CLAIM_BASELINE, codebook,
        a_column="evidence_type", b_column="baseline_comparator",
        unit="claim co-reporting membership (unique nested claim)", id_column="claim_refs",
    )
    eps_vv_rows = matrix_rows(
        [(study.corpus_id, study.fields[P_EPS_ELEMENTS], study.fields[P_VV_ARTIFACTS]) for study in studies],
        P_EPS_ELEMENTS, P_VV_ARTIFACTS, codebook,
        a_column="eps_element_modeled", b_column="verification_validation_artifact",
        unit="study co-reporting membership (unique report)", id_column="study_ids",
    )
    coverage_rows = field_coverage_rows(studies, codebook)

    run_invariants(
        studies,
        codebook,
        maturity_eps_rows=maturity_eps_rows,
        lifecycle_ivv_rows=lifecycle_ivv_rows,
        specificity_confidence_rows=specificity_confidence_rows,
        evidence_baseline_rows=evidence_baseline_rows,
        model_maturity_rows=maturity_rows,
        lifecycle_rows=lifecycle_rows,
        specificity_rows=specificity_rows,
        baseline_rows=baseline_rows,
        evidence_type_rows=evidence_rows,
        prephysical_rows=prephysical_rows,
        vv_artifact_rows=vv_artifact_rows,
        readiness_rows=readiness_rows,
        vv_rows=vv_rows,
    )

    # CSV outputs.
    write_csv(
        DATA_DIR / "study_characteristics.csv",
        study_rows,
        [
            "corpus_id", "tier", "year", "title", "authors", "venue", "venue_type", "doi_or_url",
            "quality_total_score", "quality_normalized_score", "RQ1_relevance", "RQ2_relevance", "RQ3_relevance",
            "eps_relevance", "eps_relevance_status", "approach_classification", "model_maturity", "model_maturity_status",
            "lifecycle_stage", "lifecycle_stage_status", "development_context", "development_context_status", "claim_count", "unsupported_claims", "weak_claims",
            "moderate_claims", "strong_claims", "unmapped_invalid_confidence_claims", "unassigned_confidence_claims",
            "extraction_confidence",
        ],
    )
    write_csv(DATA_DIR / "eps_relevance_counts.csv", eps_rows, count_headers("study_ids", statuses))
    write_csv(DATA_DIR / "approach_classification_counts.csv", approach_rows, count_headers("study_ids", statuses))
    write_csv(
        DATA_DIR / "claim_evidence_by_outcome.csv",
        claim_rows,
        [
            "outcome_domain", "total_claim_domain_memberships", "unsupported", "weak", "moderate", "strong",
            "unmapped_invalid", "unassigned", "unit", "denominator_claims", "study_count",
            "eps_specific_or_power_relevant_claims", "study_ids", "claim_refs",
        ],
    )
    write_csv(
        DATA_DIR / "vv_linkage_counts.csv", vv_rows,
        ["vv_linkage_category", "count", "unit", "denominator", "percent_of_denominator", "derivation_basis", "source_field_statuses", "study_ids"],
    )
    write_csv(
        DATA_DIR / "pre_physical_verification_mechanism_counts.csv", prephysical_rows,
        count_headers("study_ids", statuses),
    )
    write_csv(
        DATA_DIR / "verification_validation_artifacts_counts.csv", vv_artifact_rows,
        count_headers("study_ids", statuses),
    )
    write_csv(
        DATA_DIR / "integration_test_readiness_counts.csv", readiness_rows,
        count_headers("study_ids", statuses),
    )
    write_csv(
        DATA_DIR / "gap_mapping_counts.csv", gap_rows,
        ["gap_key", "gap_label", "classification", "count", "unit", "denominator", "percent_of_denominator", *status_columns(statuses), "unmapped_invalid_records", "unassigned_value_records", "study_ids"],
    )
    write_csv(DATA_DIR / "generality_reuse_mechanism_counts.csv", generality_rows, count_headers("study_ids", statuses))
    write_csv(DATA_DIR / "ivv_integration_level_counts.csv", ivv_rows, count_headers("study_ids", statuses))
    write_csv(DATA_DIR / "reliability_subtype_counts.csv", reliability_rows, count_headers("claim_refs", statuses))
    write_csv(
        DATA_DIR / "top_value_claims.csv", top_rows,
        [
            "rank", "claim_ref", "study_id", "claim_id", "claim_id_source", "claim_index", "year", "title", "claim",
            "outcome_domain", "original_outcome_category", "specificity", "evidence_type", "baseline_comparator",
            "evidence_confidence", "evidence_source", "direct_quote",
        ],
    )
    write_csv(
        DATA_DIR / "kaslow_eps_lineage_timeline.csv", curated_rows,
        ["paper_id", "short_id", "display_label", "year", "lane", "eps_role", "coded_eps_relevance", "maturity", "ivv_integration_level", "executable_or_simulation_evidence", "note"],
    )

    write_csv(DATA_DIR / "lifecycle_stage_counts.csv", lifecycle_rows, count_headers("study_ids", statuses))
    write_csv(DATA_DIR / "model_maturity_counts.csv", maturity_rows, count_headers("study_ids", statuses))
    write_csv(
        DATA_DIR / "model_maturity_by_eps_relevance.csv", maturity_eps_rows,
        matrix_headers("eps_relevance", "model_maturity", "study_ids", statuses),
    )
    write_csv(DATA_DIR / "model_artifacts_counts.csv", artifact_rows, count_headers("study_ids", statuses))
    write_csv(DATA_DIR / "eps_elements_modeled_counts.csv", eps_element_rows, count_headers("study_ids", statuses))
    write_csv(DATA_DIR / "interoperability_mechanisms_counts.csv", interop_rows, count_headers("study_ids", statuses))
    write_csv(DATA_DIR / "toolchain_limitations_counts.csv", limitation_rows, count_headers("study_ids", statuses))
    write_csv(DATA_DIR / "claim_specificity_counts.csv", specificity_rows, count_headers("claim_refs", statuses))
    write_csv(DATA_DIR / "evidence_type_counts.csv", evidence_rows, count_headers("claim_refs", statuses))
    write_csv(DATA_DIR / "baseline_comparator_counts.csv", baseline_rows, count_headers("claim_refs", statuses))
    write_csv(
        DATA_DIR / "lifecycle_by_ivv_integration_level.csv", lifecycle_ivv_rows,
        matrix_headers("lifecycle_stage", "ivv_integration_level", "study_ids", statuses),
    )
    write_csv(
        DATA_DIR / "governance_roi_counts.csv", governance_rows,
        ["measure_group", "source_field", *count_headers("study_ids", statuses)],
    )
    write_csv(
        DATA_DIR / "claim_specificity_by_evidence_confidence.csv", specificity_confidence_rows,
        matrix_headers("claim_specificity", "evidence_confidence", "claim_refs", statuses),
    )
    write_csv(
        DATA_DIR / "evidence_type_by_baseline_comparator.csv", evidence_baseline_rows,
        matrix_headers("evidence_type", "baseline_comparator", "claim_refs", statuses),
    )
    write_csv(
        DATA_DIR / "eps_elements_by_vv_artifact.csv", eps_vv_rows,
        matrix_headers("eps_element_modeled", "verification_validation_artifact", "study_ids", statuses),
    )
    write_csv(
        DATA_DIR / "field_coverage_status.csv", coverage_rows,
        [
            "field_path", "source_scope", "unit", "selection_type", "row_kind", "coverage_category",
            "record_count", "denominator", "percent_of_denominator", "record_refs", "raw_invalid_values",
        ],
    )

    # Figures are built from the same rows and rendered only after all data
    # invariants succeed.
    maturity_values = {
        (row["eps_relevance"], row["model_maturity"]): int(row["count"])
        for row in maturity_eps_rows
    }
    lifecycle_values = {
        (row["lifecycle_stage"], row["ivv_integration_level"]): int(row["count"])
        for row in lifecycle_ivv_rows
    }
    specificity_values = {
        (row["claim_specificity"], row["evidence_confidence"]): int(row["count"])
        for row in specificity_confidence_rows
    }
    evidence_labels, availability_labels, evidence_availability = evidence_type_by_baseline_availability(claims, codebook)
    interop_statuses = Counter(study.fields[P_INTEROP].status for study in studies)
    limitation_statuses = Counter(study.fields[P_TOOL_LIMITATIONS].status for study in studies)
    eps_element_statuses = Counter(study.fields[P_EPS_ELEMENTS].status for study in studies)
    maturity_figure_rows = list(codebook_allowed(codebook, P_EPS))
    maturity_figure_columns = [
        label for label in codebook_allowed(codebook, P_MATURITY)
        if label != "not reported"
    ]
    maturity_hidden_classes = {"not reported", UNMAPPED, UNASSIGNED_VALUE}
    if len(maturity_figure_rows) != 5 or len(maturity_figure_columns) != 6:
        raise ValidationError("Expected five substantive EPS categories and six substantive maturity categories")
    if any(
        count for (eps_relevance, model_maturity), count in maturity_values.items()
        if eps_relevance in maturity_hidden_classes or model_maturity in maturity_hidden_classes
    ):
        raise ValidationError("Maturity figure QA/unassigned/not-reported classes are expected to be zero")

    lifecycle_figure_rows = [
        label for label in codebook_allowed(codebook, P_LIFECYCLE)
        if label != "not reported"
    ]
    all_lifecycle_rows = [*codebook_allowed(codebook, P_LIFECYCLE), UNMAPPED, UNASSIGNED_VALUE]
    all_ivv_columns = [*codebook_allowed(codebook, P_IVV), UNMAPPED, UNASSIGNED_VALUE]
    lifecycle_figure_columns = [
        column for column in all_ivv_columns
        if any(lifecycle_values.get((row, column), 0) for row in all_lifecycle_rows)
    ]
    lifecycle_omitted_columns = [
        column for column in all_ivv_columns if column not in lifecycle_figure_columns
    ]
    expected_lifecycle_columns = (
        "none/not reported",
        "separate document only",
        "trace-linked verification artifacts",
        "model-contained verification artifacts",
        "executable/model-based checks",
        "simulation-in-the-loop",
        "software/hardware-in-the-loop",
        UNASSIGNED_VALUE,
    )
    if len(lifecycle_figure_rows) != 7 or tuple(lifecycle_figure_columns) != expected_lifecycle_columns:
        raise ValidationError("Lifecycle figure must retain seven substantive rows and eight nonzero IVV columns")
    if any(
        lifecycle_values.get((row, column), 0)
        for row in all_lifecycle_rows for column in lifecycle_omitted_columns
    ):
        raise ValidationError("Only zero IVV controlled/QA columns may be omitted from the lifecycle figure")
    no_selected_ivv = field_value_count(ivv_rows, UNASSIGNED_VALUE)
    prisma_counts = parse_prisma_counts()
    figure_svgs = {
        "prisma_flow": prisma_svg(prisma_counts),
        "eps_relevance_counts": horizontal_bar_svg(
            "Mutually exclusive EPS-relevance categories",
            "One controlled category per report (n=40); counts are unique reports.",
            [(row["category"], int(row["count"])) for row in eps_rows],
            color="#2563EB",
        ),
        "claim_evidence_by_outcome": stacked_bar_svg(
            "Claim evidence confidence by controlled outcome domain",
            "n=270 nested claims; unique claim-domain memberships, with outcome domains allowed to overlap.",
            [row["outcome_domain"] for row in claim_rows if int(row["total_claim_domain_memberships"]) > 0],
            ["Unsupported", "Weak", "Moderate", "Strong"],
            {
                row["outcome_domain"]: [int(row["unsupported"]), int(row["weak"]), int(row["moderate"]), int(row["strong"])]
                for row in claim_rows
            },
            ["#D1D5DB", "#FDE68A", "#BFDBFE", "#BBF7D0"],
        ),
        "vv_linkage_counts": horizontal_bar_svg(
            "Derived V&V linkage categories",
            "Mixed-source union of V&V artifacts, explicit pre-physical mechanisms, and readiness; the generic/planned fallback also uses controlled RQ3 relevance. Readiness is not closure; n=40 memberships can overlap.",
            [(row["vv_linkage_category"], int(row["count"])) for row in vv_rows],
            color="#DC2626",
            subtitle_width_chars=96,
        ),
        "gap_mapping_counts": stacked_bar_svg(
            "All-study controlled gap mapping",
            "n=40 reports per gap; pre-specified classifications are mutually exclusive.",
            [label for _, label in GAP_FIELDS],
            list(codebook_allowed(codebook, GAP_FIELDS[0][0])),
            {
                label: [
                    next(int(row["count"]) for row in gap_rows if row["gap_label"] == label and row["classification"] == status)
                    for status in codebook_allowed(codebook, GAP_FIELDS[0][0])
                ]
                for _, label in GAP_FIELDS
            },
            ["#BBF7D0", "#BAE6FD", "#FDE68A", "#FECACA"],
        ),
        "kaslow_eps_lineage_timeline": curated_timeline_svg(curated_rows),
        "model_maturity_by_eps_relevance": compact_maturity_eps_heatmap_svg(
            maturity_figure_rows,
            maturity_figure_columns,
            maturity_values,
        ),
        "eps_elements_modeled": separated_coverage_bar_svg(
            "EPS elements modeled: controlled selections",
            f"Field coverage/status: coded {eps_element_statuses.get('coded', 0)}/{len(studies)}; "
            f"not reported status {eps_element_statuses.get('not_reported', 0)}; "
            f"not applicable {eps_element_statuses.get('not_applicable', 0)}; none {eps_element_statuses.get('none', 0)}.",
            [
                (row["category"], int(row["count"]))
                for row in eps_element_rows
                if row["category"] not in {UNMAPPED, UNASSIGNED_VALUE}
            ],
            neutral_label="No selected controlled value (not an EPS element)",
            neutral_count=field_value_count(eps_element_rows, UNASSIGNED_VALUE),
            color="#0F766E",
        ),
        "toolchain_mechanisms_limitations": toolchain_panels_svg(
            interop_rows, limitation_rows, interop_statuses, limitation_statuses, len(studies)
        ),
        "claim_evidence_anatomy": claim_anatomy_svg(
            [*codebook_allowed(codebook, P_CLAIM_SPECIFICITY), UNMAPPED, UNASSIGNED_VALUE],
            [*codebook_allowed(codebook, P_CLAIM_CONFIDENCE), UNMAPPED, UNASSIGNED_VALUE],
            specificity_values,
            evidence_labels,
            availability_labels,
            evidence_availability,
            len(claims),
        ),
        "lifecycle_ivv_heatmap": compact_lifecycle_ivv_heatmap_svg(
            lifecycle_figure_rows,
            [lifecycle_figure_columns[:4], lifecycle_figure_columns[4:]],
            lifecycle_values,
            no_selected_ivv=no_selected_ivv,
            omitted_columns=lifecycle_omitted_columns,
        ),
    }
    render_figure_triplets(figure_svgs)

    write_results_tables(
        studies, codebook,
        eps_rows=eps_rows,
        approach_rows=approach_rows,
        maturity_rows=maturity_rows,
        artifact_rows=artifact_rows,
        eps_element_rows=eps_element_rows,
        interop_rows=interop_rows,
        limitation_rows=limitation_rows,
        claim_rows=claim_rows,
        specificity_rows=specificity_rows,
        baseline_rows=baseline_rows,
        specificity_confidence_rows=specificity_confidence_rows,
        reliability_rows=reliability_rows,
        prephysical_rows=prephysical_rows,
        vv_artifact_rows=vv_artifact_rows,
        readiness_rows=readiness_rows,
        vv_rows=vv_rows,
        ivv_rows=ivv_rows,
        governance_rows=governance_rows,
        gap_rows=gap_rows,
    )
    write_data_summary(
        studies, codebook,
        eps_rows=eps_rows,
        maturity_rows=maturity_rows,
        lifecycle_rows=lifecycle_rows,
        artifact_rows=artifact_rows,
        eps_element_rows=eps_element_rows,
        interop_rows=interop_rows,
        limitation_rows=limitation_rows,
        specificity_rows=specificity_rows,
        evidence_rows=evidence_rows,
        baseline_rows=baseline_rows,
        prephysical_rows=prephysical_rows,
        vv_artifact_rows=vv_artifact_rows,
        readiness_rows=readiness_rows,
        vv_rows=vv_rows,
        ivv_rows=ivv_rows,
        governance_rows=governance_rows,
        claim_rows=claim_rows,
        top_rows=top_rows,
        coverage_rows=coverage_rows,
        prisma_counts=prisma_counts,
    )

    missing_outputs = [path for path in expected_output_paths() if not path.exists() or path.stat().st_size == 0]
    if missing_outputs:
        raise RuntimeError(f"Pipeline completed with missing/empty outputs: {missing_outputs}")
    print(f"Validated {len(studies)} reports and {len(claims)} nested claim records against codebook {codebook['codebook_version']}")
    print(f"Wrote {len(EXISTING_CSV_NAMES) + len(PLANNED_CSV_NAMES) + len(ADDITIONAL_CSV_NAMES)} CSV artifacts, {len(FIGURE_NAMES)} SVG/PDF/PNG figure triplets, and two draft snippets")


if __name__ == "__main__":
    main()
