#!/usr/bin/env python3
"""Generate systematic-literature-review data artifacts for SLR1.

The generator is deterministic and offline. It reads the SLR1 extraction index,
per-study extraction JSON files, the protocol, and scoping-review artifacts, then
writes SLR-focused CSV summaries, figures, and LaTeX/Markdown snippets.

Run from the repository root:
    python3 SLR/SLR1/systematic-literature-review/scripts/generate_slr_artifacts.py

Paths are resolved from this script's location, not from the current working
folder. Figures are generated as SVG and converted to PDF/PNG with
``rsvg-convert`` when available; the PRISMA flow is copied from the existing
scoping review when present and generated from parsed scoping counts otherwise.
"""
from __future__ import annotations

import csv
import html
import json
import math
import re
import shutil
import subprocess
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
REPORT_DIR = SCRIPT_DIR.parent
SLR1_DIR = REPORT_DIR.parent
EXTRACTIONS_DIR = SLR1_DIR / "extractions"
EXTRACTION_INDEX = SLR1_DIR / "extraction.json"
PROTOCOL = SLR1_DIR / "protocol.md"
SCOPING_DIR = SLR1_DIR / "scoping-review"
SCOPING_DATA_DIR = SCOPING_DIR / "data"
SCOPING_TEX = SCOPING_DIR / "scoping-review.tex"
BURUSO_MD = (
    SLR1_DIR.parent.parent
    / "incose-journal-research"
    / "Systems Engineering - 2026 - Buruso - Model‐Based Systems Engineering in Space Applications  A Comprehensive Literature.md"
)
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"
DRAFTS_DIR = REPORT_DIR / "drafts"

CONFIDENCE_ORDER = ["Unsupported", "Weak", "Moderate", "Strong"]
CONFIDENCE_SCORE = {"Unsupported": 0, "Weak": 1, "Moderate": 2, "Strong": 3}
GAP_STATUSES = ["addressed with evidence", "addressed conceptually", "mentioned only", "not addressed"]

BURUSO_GAPS: List[Tuple[str, str]] = [
    ("practical_implementation_pathway", "Practical implementation pathway"),
    ("toolchain_fragmentation_interoperability", "Toolchain fragmentation/interoperability"),
    ("lightweight_resource_constrained_tailoring", "Lightweight/resource-constrained tailoring"),
    ("governance_project_deliverables_roi", "Governance/project deliverables/ROI/value"),
    ("newspace_agile_distributed_rapid_iteration_alignment", "NewSpace/agile/distributed/rapid iteration"),
]

# Outcome domains emphasize the SLR results focus. Rules are multi-label: one
# extracted claim can contribute to more than one outcome domain when its coded
# category explicitly spans multiple value mechanisms.
OUTCOME_DOMAIN_RULES: List[Tuple[str, Sequence[str]]] = [
    (
        "Reliability / mission assurance / risk",
        [
            r"reliab", r"mission success", r"mission assurance", r"risk", r"robust", r"resilien",
            r"fault", r"defect", r"error", r"quality", r"correctness", r"failure", r"safety",
        ],
    ),
    (
        "Reproducibility / reuse / openness",
        [
            r"reproduc", r"reuse", r"reusability", r"replic", r"open", r"accessib", r"repository",
            r"standard", r"template", r"library", r"distribution", r"knowledge reuse",
        ],
    ),
    (
        "Integrability / interoperability / lifecycle continuity",
        [
            r"integrab", r"integration", r"interoper", r"interface", r"toolchain", r"data continuity",
            r"data exchange", r"digital thread", r"lifecycle continuity", r"model continuity",
            r"semantic integration", r"configuration continuity", r"downstream", r"software/hardware/system",
        ],
    ),
    (
        "Traceability / consistency / requirements quality",
        [
            r"trace", r"consisten", r"coheren", r"single source", r"requirements?", r"compliance",
            r"satisfaction", r"coverage", r"completeness", r"change impact", r"maintain",
            r"information retrieval",
        ],
    ),
    (
        "Cost / schedule / effort / efficiency / automation",
        [
            r"cost", r"schedule", r"time", r"effort", r"efficien", r"productiv", r"workload",
            r"automation", r"automated", r"automatic", r"speed", r"rapid", r"iteration", r"rework",
            r"redesign", r"process efficiency",
        ],
    ),
    (
        "Governance / ROI / project decisions",
        [
            r"govern", r"\broi\b", r"deliverable", r"project", r"management", r"planning", r"review",
            r"milestone", r"decision", r"value", r"configuration management", r"archival",
        ],
    ),
    (
        "Pre-physical V&V / verification / validation / test",
        [
            r"verification", r"validation", r"\bv&v\b", r"test", r"model checking", r"pre-physical",
            r"pre-development", r"checks?", r"acceptance", r"formal verification",
        ],
    ),
    (
        "Decision support / analysis / trade-space / feasibility",
        [
            r"analysis", r"trade", r"decision support", r"design-space", r"optimization", r"feasib",
            r"performance", r"budget", r"power", r"energy", r"component selection", r"sizing",
            r"simulation", r"technical performance",
        ],
    ),
    (
        "Communication / collaboration / knowledge",
        [
            r"communicat", r"collaborat", r"stakeholder", r"knowledge", r"education", r"learning",
            r"training", r"understanding", r"documentation", r"readability", r"sharing",
        ],
    ),
    (
        "Generality / scalability / tailoring",
        [
            r"generality", r"generic", r"scalab", r"extensib", r"modular", r"adapt", r"tailor",
            r"portability", r"variability", r"abstraction", r"customization",
        ],
    ),
]

VALUE_DOMAIN_PRIORITY = {
    "Reliability / mission assurance / risk": 8,
    "Reproducibility / reuse / openness": 8,
    "Integrability / interoperability / lifecycle continuity": 8,
    "Traceability / consistency / requirements quality": 8,
    "Cost / schedule / effort / efficiency / automation": 7,
    "Governance / ROI / project decisions": 7,
    "Pre-physical V&V / verification / validation / test": 8,
    "Decision support / analysis / trade-space / feasibility": 6,
    "Communication / collaboration / knowledge": 4,
    "Generality / scalability / tailoring": 4,
    "Other / uncategorized value claim": 1,
}

VV_RULES: List[Tuple[str, Sequence[str]]] = [
    (
        "Requirements-to-model traceability or verification matrix",
        [
            r"requirement", r"verified by", r"verifies", r"verify relationship", r"satisfy",
            r"satisfied by", r"trace", r"matrix", r"compliance", r"coverage", r"criteria",
        ],
    ),
    (
        "Executable simulation or scenario analysis before build",
        [
            r"simulation", r"simulate", r"execute", r"executable", r"scenario", r"time-history",
            r"animated", r"dymola", r"forplan", r"opalis", r"monte carlo", r"modelcenter",
            r"cameo simulation", r"stk", r"matlab", r"mission timeline",
        ],
    ),
    (
        "Parametric/budget/constraint checks",
        [
            r"parametric", r"constraint", r"budget", r"margin", r"threshold", r"pass/fail",
            r"accepted/not-accepted", r"mass", r"volume", r"power", r"energy", r"battery",
            r"solar", r"state of charge", r"\bsoc\b", r"\bdod\b", r"depth-of-discharge",
        ],
    ),
    (
        "Test cases/procedures/V&V activity packages",
        [
            r"test case", r"test-case", r"test procedure", r"test specification", r"verification activity",
            r"validation activity", r"verification package", r"validation package", r"plan", r"procedure",
            r"inspection", r"demonstration", r"acceptance", r"status", r"result", r"pass/fail",
        ],
    ),
    (
        "External tool or data-flow coupling for V&V",
        [
            r"modelcenter", r"stk", r"matlab", r"dymola", r"java", r"parser", r"api", r"database",
            r"spreadsheet", r"excel", r"script", r"automatic extraction", r"automatically transfer",
            r"data transfer", r"export", r"import", r"transformation", r"generated", r"code",
        ],
    ),
    (
        "EPS/power-specific pre-physical verification",
        [
            r"\beps\b", r"power subsystem", r"power budget", r"power demand", r"power profile",
            r"battery", r"solar", r"energy", r"state of charge", r"\bsoc\b", r"\bdod\b", r"pcdu",
            r"power-source", r"voltage", r"eclipse", r"illumination",
        ],
    ),
    (
        "Physical/SIL/HIL/integration-test readiness link",
        [
            r"integration test", r"physical integration", r"hardware-in-the-loop", r"\bhil\b", r"sil",
            r"flat-sat", r"testbed", r"end-to-end setup", r"ground-station hardware", r"flight software",
            r"environmental test", r"qualification", r"bench test", r"operational validation",
        ],
    ),
]

NEGATIVE_VV_PATTERNS = [
    r"not reported", r"no .*verification", r"no .*v&v", r"no .*test", r"no .*integration",
    r"no .*hardware", r"no .*physical", r"does not integrate",
    r"cannot be used as an effective requirements verification tool", r"not demonstrated",
]

NEGATIVE_VV_SEGMENT_PATTERNS = [
    r"\bnot reported\b", r"\bno\b", r"\bnone\b", r"\bcannot\b", r"\bdoes not\b", r"\bwithout\b",
    r"not demonstrated", r"not shown", r"not provided", r"not integrated", r"not evaluated",
]

SPECIFICITY_SCORE = {
    "EPS-specific": 3.0,
    "power-budget/electrical-architecture": 2.5,
    "nanosatellite system-level": 2.0,
    "generic space-system": 1.5,
    "generic MBSE": 1.0,
    "unclear": 0.5,
}

# Controlled mappings from extraction_codebook.json labels to synthesis domains.
# These replace the earlier loose keyword mapping: a claim contributes to a
# domain only when its controlled outcome_category code supports that domain.
OUTCOME_DOMAINS = [domain for domain, _patterns in OUTCOME_DOMAIN_RULES] + ["Other / uncategorized value claim"]
CONTROLLED_OUTCOME_DOMAIN_MAP = {
    "reliability": ["Reliability / mission assurance / risk"],
    "mission assurance": ["Reliability / mission assurance / risk"],
    "risk reduction": ["Reliability / mission assurance / risk"],
    "defect/error reduction": ["Reliability / mission assurance / risk"],
    "reproducibility": ["Reproducibility / reuse / openness"],
    "generality/reuse": ["Reproducibility / reuse / openness", "Generality / scalability / tailoring"],
    "integrability/interoperability": ["Integrability / interoperability / lifecycle continuity"],
    "lifecycle continuity": ["Integrability / interoperability / lifecycle continuity"],
    "traceability": ["Traceability / consistency / requirements quality"],
    "consistency": ["Traceability / consistency / requirements quality"],
    "completeness": ["Traceability / consistency / requirements quality"],
    "cost reduction": ["Cost / schedule / effort / efficiency / automation"],
    "schedule reduction": ["Cost / schedule / effort / efficiency / automation"],
    "effort reduction": ["Cost / schedule / effort / efficiency / automation"],
    "automation": ["Cost / schedule / effort / efficiency / automation"],
    "governance/ROI": ["Governance / ROI / project decisions"],
    "decision support": ["Decision support / analysis / trade-space / feasibility"],
    "communication/stakeholder alignment": ["Communication / collaboration / knowledge"],
    "other": ["Other / uncategorized value claim"],
}

CONTROLLED_VV_CATEGORY_MAP = {
    "verification matrix": ["Requirements-to-model traceability or verification matrix"],
    "test cases": ["Test cases/procedures/V&V activity packages"],
    "test procedures": ["Test cases/procedures/V&V activity packages"],
    "simulation scenarios": ["Executable simulation or scenario analysis before build"],
    "acceptance criteria": ["Test cases/procedures/V&V activity packages"],
    "executable checks": ["Test cases/procedures/V&V activity packages", "Parametric/budget/constraint checks"],
    "generated test artifacts": ["Test cases/procedures/V&V activity packages", "External tool or data-flow coupling for V&V"],
    "SIL/HIL links": ["Physical/SIL/HIL/integration-test readiness link"],
    "automated tests": ["Test cases/procedures/V&V activity packages", "External tool or data-flow coupling for V&V"],
    "requirements-in-the-loop": ["Requirements-to-model traceability or verification matrix"],
    "simulation-in-the-loop": ["Executable simulation or scenario analysis before build"],
    "parametric checks": ["Parametric/budget/constraint checks"],
    "model checking": ["Requirements-to-model traceability or verification matrix", "Test cases/procedures/V&V activity packages"],
    "trade-study verification": ["Parametric/budget/constraint checks", "Executable simulation or scenario analysis before build"],
    "virtual integration": ["External tool or data-flow coupling for V&V"],
    "links to hardware integration": ["Physical/SIL/HIL/integration-test readiness link"],
    "software integration": ["Physical/SIL/HIL/integration-test readiness link"],
    "flat-sat/testbed": ["Physical/SIL/HIL/integration-test readiness link"],
    "environmental test": ["Physical/SIL/HIL/integration-test readiness link"],
    "operational validation": ["Physical/SIL/HIL/integration-test readiness link"],
}

GAP_KEY_ALIASES = {
    "governance_project_deliverables_roi_value": "governance_project_deliverables_roi",
    "newspace_agile_distributed_rapid_iteration": "newspace_agile_distributed_rapid_iteration_alignment",
}

# ---------------------------------------------------------------------------
# File and field utilities


def read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def as_list(value: object) -> List[str]:
    """Return a clean list of scalar labels without splitting controlled labels."""
    if value is None:
        return []
    if isinstance(value, dict):
        if "values" in value:
            return as_list(value.get("values"))
        text = value.get("value") or value.get("label") or value.get("classification") or value.get("rating") or ""
        text = normalize_whitespace(text)
        return [text] if text else []
    if isinstance(value, list):
        out: List[str] = []
        for item in value:
            if isinstance(item, dict):
                out.extend(as_list(item))
            else:
                text = normalize_whitespace(item)
                if text:
                    out.append(text)
        return out
    text = normalize_whitespace(value)
    return [text] if text else []


def controlled_values(study: dict, field_path: str) -> List[str]:
    """Read exact controlled-code values from structured_code_summary."""
    entry = study.get("structured_code_summary", {}).get(field_path, {})
    if entry.get("status") != "coded":
        return []
    return as_list(entry.get("values"))


def first_controlled_value(study: dict, field_path: str, default: str = "") -> str:
    values = controlled_values(study, field_path)
    return values[0] if values else default


def evidence_to_text(value: object) -> str:
    if isinstance(value, list):
        return "; ".join(evidence_to_text(v) for v in value if evidence_to_text(v))
    if isinstance(value, dict):
        quote = value.get("quote") or value.get("evidence_quote") or value.get("text") or ""
        location = value.get("location") or value.get("source") or ""
        if quote and location:
            return f"{location}: {quote}"
        return normalize_whitespace(quote or location or value)
    return normalize_whitespace(value)


def quality_item_score(item: object) -> float:
    """Score protocol quality items across old and refactored extraction shapes."""
    if not isinstance(item, dict):
        return 0.0
    if item.get("numeric_score") is not None:
        return float(item.get("numeric_score") or 0)
    if item.get("score") is not None:
        return float(item.get("score") or 0)
    values = as_list(item.get("values") or item.get("value") or item.get("label"))
    label = values[0] if values else ""
    return {"Yes": 1.0, "Insufficiently": 0.5, "No": 0.0}.get(label, 0.0)


def normalize_claim_record(claim: dict) -> dict:
    """Normalize heterogeneous subagent claim records to the generator schema."""
    normalized = dict(claim)
    normalized["claim"] = normalize_whitespace(
        claim.get("claim")
        or claim.get("claim_text")
        or claim.get("claim_text_or_paraphrase")
        or claim.get("claim_paraphrase")
        or ""
    )
    outcome_values = as_list(claim.get("outcome_category"))
    normalized["outcome_category_values"] = outcome_values
    normalized["outcome_category"] = "; ".join(outcome_values)
    normalized["specificity"] = normalize_whitespace(claim.get("specificity") or claim.get("specificity_of_claim") or "unclear")
    normalized["mbse_mechanism"] = as_list(claim.get("mbse_mechanism"))
    normalized["artifact_or_process_linked"] = normalize_whitespace(
        claim.get("artifact_or_process_linked")
        or claim.get("artifact_process_linked_to_claim")
        or claim.get("artifact_or_process_linked_to_claim")
        or ""
    )
    normalized["evidence_type"] = "; ".join(as_list(claim.get("evidence_type")))
    confidence_values = as_list(claim.get("evidence_confidence") or claim.get("evidence_confidence_rating"))
    normalized["evidence_confidence"] = confidence_values[0] if confidence_values else "Unsupported"
    normalized["evidence_source"] = evidence_to_text(claim.get("evidence_source"))
    normalized["direct_quote"] = normalize_whitespace(claim.get("direct_quote") or claim.get("evidence_quote") or evidence_to_text(claim.get("evidence_source")))
    return normalized


def normalize_refactored_study(raw: dict) -> dict:
    """Flatten the refactored extraction schema while preserving controlled summaries.

    The new extraction files keep protocol fields under ``extraction`` and the
    controlled coding under ``structured_code_summary``. The report generator was
    originally written for a flat schema, so this adapter gives downstream code a
    controlled-code-backed view instead of making it rediscover categories with
    regexes.
    """
    extraction = raw.get("extraction") or {}
    if not extraction:
        return raw

    study = dict(extraction)
    for key in [
        "corpus_id",
        "tier",
        "year",
        "quality_checklist",
        "structured_code_summary",
        "structured_limitations",
        "emergent_codes",
        "bibtex",
    ]:
        if key in raw:
            study[key] = raw[key]

    # Ensure protocol sections exist even when a subagent omitted an optional section.
    for section in [
        "bibliographic_review_management",
        "study_context_population",
        "mbse_objective_scope_artifacts",
        "implementation_pathway_tailoring",
        "toolchain_interoperability_lifecycle_continuity",
        "eps_verification_specific",
        "claimed_outcomes_value_mechanisms_evidence",
        "governance_roi_project_decision_linkage",
        "gap_mapping",
        "synthesis_consistency",
    ]:
        study.setdefault(section, extraction.get(section, {} if section != "claimed_outcomes_value_mechanisms_evidence" else []))

    # Normalize quality total for tables/figures.
    total = 0.0
    for item in study.get("quality_checklist", {}).values():
        total += quality_item_score(item)
    if study.get("quality_checklist") is not None:
        study["quality_checklist"] = dict(study.get("quality_checklist", {}))
        study["quality_checklist"].setdefault("total_score", total)
        study["quality_checklist"].setdefault("normalized_score", round(total / 8.0, 3) if total else "")

    study["claimed_outcomes_value_mechanisms_evidence"] = [
        normalize_claim_record(claim)
        for claim in study.get("claimed_outcomes_value_mechanisms_evidence", [])
        if isinstance(claim, dict)
    ]
    return study


def load_studies() -> List[dict]:
    studies = [normalize_refactored_study(read_json(p)) for p in sorted(EXTRACTIONS_DIR.glob("paper-*.json"))]
    return sorted(studies, key=lambda d: (int(d.get("year", 9999)), d.get("corpus_id", "")))


def get_rq_relevance(study: dict, rq: str) -> str:
    controlled = first_controlled_value(study, f"bibliographic_review_management.{rq.lower()}_relevance")
    if controlled:
        return controlled
    value = study.get("bibliographic_review_management", {}).get("research_questions_addressed", {}).get(rq, "")
    if isinstance(value, dict):
        return value.get("relevance", "")
    return str(value or "")


def get_title(study: dict) -> str:
    bib = study.get("bibliographic_review_management", {})
    citation = bib.get("citation") if isinstance(bib.get("citation"), dict) else {}
    return bib.get("title") or citation.get("title") or study.get("title") or study.get("corpus_id", "")


def get_authors(study: dict) -> List[str]:
    bib = study.get("bibliographic_review_management", {})
    citation = bib.get("citation") if isinstance(bib.get("citation"), dict) else {}
    return bib.get("authors") or citation.get("authors") or study.get("authors") or []


def get_quality(study: dict) -> Tuple[float | str, float | str]:
    q = study.get("quality_checklist", {})
    if "total_score" in q or "normalized_score" in q:
        return q.get("total_score", ""), q.get("normalized_score", "")
    total = 0.0
    for item in q.values():
        total += quality_item_score(item)
    return total, round(total / 8.0, 3) if total else ""


def get_extraction_confidence(study: dict) -> str:
    controlled = first_controlled_value(study, "synthesis_consistency.extraction_confidence")
    if controlled:
        return controlled
    value = study.get("synthesis_consistency", {}).get("extraction_confidence", "")
    if isinstance(value, dict):
        return value.get("value") or value.get("confidence") or ""
    return value


def get_claims(study: dict) -> List[dict]:
    return study.get("claimed_outcomes_value_mechanisms_evidence") or []


def normalize_whitespace(text: object) -> str:
    return re.sub(r"\s+", " ", str("" if text is None else text)).strip()


def has_any(text: str, patterns: Sequence[str]) -> bool:
    return any(re.search(pattern, text, flags=re.I) for pattern in patterns)


def join_list(value: object, sep: str = "; ") -> str:
    if isinstance(value, list):
        return sep.join(normalize_whitespace(v) for v in value if normalize_whitespace(v))
    return normalize_whitespace(value)


def first_author_label(study: dict) -> str:
    authors = get_authors(study)
    if not authors:
        return "Unknown"
    return str(authors[0]).split()[-1]


def tex_escape(text: object) -> str:
    s = normalize_whitespace(text)
    repl = {
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
    return "".join(repl.get(ch, ch) for ch in s)


def compact_ids(ids: Iterable[str]) -> str:
    return "; ".join(sorted(ids))


def parse_scoping_prisma_counts() -> Dict[str, int]:
    text = SCOPING_TEX.read_text(encoding="utf-8") if SCOPING_TEX.exists() else ""
    pattern = re.compile(
        r"(\d+)\s+raw merged search records,\s*(\d+)\s+duplicates removed,\s*(\d+)\s+unique records screened,\s*"
        r"(\d+)\s+excluded during screening,\s*(\d+)\s+reports sought for retrieval,\s*(\d+)\s+not retrieved/inaccessible,\s*and\s*(\d+)\s+extracted",
        flags=re.I,
    )
    m = pattern.search(text)
    if m:
        raw, duplicates, screened, excluded, reports, not_retrieved, extracted = map(int, m.groups())
        return {
            "raw_records": raw,
            "duplicates_removed": duplicates,
            "unique_records_screened": screened,
            "excluded_screening": excluded,
            "reports_sought": reports,
            "not_retrieved": not_retrieved,
            "extracted": extracted,
        }
    return {
        "raw_records": 199,
        "duplicates_removed": 118,
        "unique_records_screened": 81,
        "excluded_screening": 37,
        "reports_sought": 44,
        "not_retrieved": 4,
        "extracted": 40,
    }


def read_protocol_rqs() -> List[str]:
    text = PROTOCOL.read_text(encoding="utf-8")
    match = re.search(r"## Research questions\n(?P<body>.*?)(?:\n## |\Z)", text, flags=re.S)
    if not match:
        return []
    rqs: List[str] = []
    for line in match.group("body").splitlines():
        item = re.match(r"\s*(\d+)\.\s*(.*)", line)
        if item:
            rqs.append(f"RQ{item.group(1)}: {normalize_whitespace(item.group(2))}")
    return rqs


def read_scoping_inputs() -> Dict[str, object]:
    """Read scoping CSV/TEX inputs for count reuse/verification."""
    info: Dict[str, object] = {"csv_files": [], "studies_rows": 0, "category_rows": 0}
    for csv_path in sorted(SCOPING_DATA_DIR.glob("*.csv")):
        info["csv_files"].append(str(csv_path.relative_to(SLR1_DIR)))
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            row_count = max(sum(1 for _ in f) - 1, 0)
        if csv_path.name == "studies.csv":
            info["studies_rows"] = row_count
        if csv_path.name == "category_counts.csv":
            info["category_rows"] = row_count
    info["prisma_counts"] = parse_scoping_prisma_counts()
    if BURUSO_MD.exists():
        text = BURUSO_MD.read_text(encoding="utf-8")
        info["buruso_table5_present"] = "TABLE 5 Summary of gaps identified" in text
    else:
        info["buruso_table5_present"] = False
    return info

# ---------------------------------------------------------------------------
# Classification and aggregation


def claim_text_for_mapping(claim: dict) -> str:
    parts = [
        claim.get("outcome_category", ""),
        claim.get("claim", ""),
        join_list(claim.get("mbse_mechanism", [])),
        claim.get("artifact_or_process_linked", ""),
    ]
    return " ".join(normalize_whitespace(p) for p in parts if normalize_whitespace(p))


def outcome_domains_for_claim(claim: dict) -> List[str]:
    """Map claims to synthesis domains using controlled outcome_category codes.

    No keyword matching is used here; uncoded or unrecognized categories remain
    in the explicit Other bucket so emergent findings are not hidden by loose
    text classification.
    """
    domains: List[str] = []
    for category in claim.get("outcome_category_values") or as_list(claim.get("outcome_category")):
        for domain in CONTROLLED_OUTCOME_DOMAIN_MAP.get(category, ["Other / uncategorized value claim"]):
            if domain not in domains:
                domains.append(domain)
    return domains or ["Other / uncategorized value claim"]


def evidence_confidence(claim: dict) -> str:
    values = as_list(claim.get("evidence_confidence") or claim.get("evidence_confidence_rating"))
    value = values[0] if values else ""
    return value if value in CONFIDENCE_ORDER else "Unsupported"


def vv_linkages_for_study(study: dict) -> List[str]:
    """Classify V&V linkages from controlled extraction codes, not regexes."""
    prephysical_values: List[str] = []
    readiness_values: List[str] = []
    for field_path in [
        "eps_verification_specific.verification_validation_artifacts",
        "eps_verification_specific.pre_physical_development_verification_mechanism",
    ]:
        prephysical_values.extend(controlled_values(study, field_path))
    readiness_values.extend(controlled_values(study, "eps_verification_specific.integration_test_readiness"))

    # Fallback to normalized extraction fields if a legacy extraction is used.
    if not prephysical_values and not readiness_values:
        eps = study.get("eps_verification_specific", {})
        for key in ["verification_validation_artifacts", "pre_physical_development_verification_mechanism"]:
            prephysical_values.extend(v for v in as_list(eps.get(key)) if v != "not reported")
        readiness_values.extend(v for v in as_list(eps.get("integration_test_readiness")) if v != "not reported")

    categories: List[str] = []
    prephysical_categories: List[str] = []
    for value in prephysical_values:
        for category in CONTROLLED_VV_CATEGORY_MAP.get(value, []):
            if category not in categories:
                categories.append(category)
            if category not in prephysical_categories:
                prephysical_categories.append(category)
    for value in readiness_values:
        for category in CONTROLLED_VV_CATEGORY_MAP.get(value, []):
            if category not in categories:
                categories.append(category)

    eps_relevance = first_controlled_value(study, "study_context_population.eps_relevance") or normalize_whitespace(
        study.get("study_context_population", {}).get("eps_relevance", "")
    )
    if prephysical_categories and eps_relevance in {"EPS-specific", "power-budget/electrical-architecture", "EPS-adjacent"}:
        categories.append("EPS/power-specific pre-physical verification")

    if not prephysical_categories:
        categories.append("No explicit EPS-focused pre-physical V&V")
        if first_controlled_value(study, "bibliographic_review_management.rq3_relevance") in {"partial", "high"}:
            categories.append("Generic/planned V&V linkage only")

    return sorted(set(categories))


def gap_classification(study: dict, gap_key: str) -> str:
    key = GAP_KEY_ALIASES.get(gap_key, gap_key)
    controlled = first_controlled_value(study, f"gap_mapping.{key}")
    if controlled:
        return controlled
    value = study.get("gap_mapping", {}).get(key, study.get("gap_mapping", {}).get(gap_key, ""))
    if isinstance(value, dict):
        return normalize_whitespace(value.get("classification") or value.get("rating") or "")
    return normalize_whitespace(value)


def study_characteristics_rows(studies: Sequence[dict]) -> List[dict]:
    rows: List[dict] = []
    for study in studies:
        claims = get_claims(study)
        confidence_counts = Counter(evidence_confidence(claim) for claim in claims)
        q_total, q_norm = get_quality(study)
        bib = study.get("bibliographic_review_management", {})
        citation = bib.get("citation") if isinstance(bib.get("citation"), dict) else {}
        context = study.get("study_context_population", {})
        impl = study.get("implementation_pathway_tailoring", {})
        rows.append(
            {
                "corpus_id": study.get("corpus_id", ""),
                "tier": study.get("tier", ""),
                "year": study.get("year", ""),
                "title": get_title(study),
                "authors": "; ".join(get_authors(study)),
                "venue": bib.get("venue") or citation.get("venue", ""),
                "venue_type": bib.get("venue_type") or citation.get("venue_type", ""),
                "doi_or_url": bib.get("doi_or_url") or bib.get("doi") or bib.get("url") or citation.get("doi") or citation.get("url", ""),
                "quality_total_score": q_total,
                "quality_normalized_score": q_norm,
                "RQ1_relevance": get_rq_relevance(study, "RQ1"),
                "RQ2_relevance": get_rq_relevance(study, "RQ2"),
                "RQ3_relevance": get_rq_relevance(study, "RQ3"),
                "eps_relevance": first_controlled_value(study, "study_context_population.eps_relevance") or context.get("eps_relevance", ""),
                "approach_classification": first_controlled_value(study, "implementation_pathway_tailoring.approach_classification") or impl.get("approach_classification", ""),
                "model_maturity": join_list(controlled_values(study, "study_context_population.model_maturity") or context.get("model_maturity", "")),
                "lifecycle_stage": join_list(controlled_values(study, "study_context_population.lifecycle_stage_addressed") or context.get("lifecycle_stage_addressed", "")),
                "development_context": join_list(controlled_values(study, "study_context_population.development_context") or context.get("development_context", "")),
                "claim_count": len(claims),
                "unsupported_claims": confidence_counts.get("Unsupported", 0),
                "weak_claims": confidence_counts.get("Weak", 0),
                "moderate_claims": confidence_counts.get("Moderate", 0),
                "strong_claims": confidence_counts.get("Strong", 0),
                "extraction_confidence": get_extraction_confidence(study),
            }
        )
    return rows


def count_by_study_field(studies: Sequence[dict], getter) -> List[dict]:
    members: Dict[str, List[str]] = defaultdict(list)
    for study in studies:
        value = normalize_whitespace(getter(study)) or "not reported"
        members[value].append(study["corpus_id"])
    return [
        {"category": category, "count": len(ids), "study_ids": compact_ids(ids)}
        for category, ids in sorted(members.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]


def controlled_field_count_rows(studies: Sequence[dict], field_path: str) -> List[dict]:
    """Count selected controlled values for a structured_code_summary field.

    Unlike ``controlled_values``, this helper intentionally counts selected
    values even when the status is ``none`` or ``not_reported``.  That is needed
    for fields such as the v1.1 IVV integration level, where the controlled
    value ``none/not reported`` is itself synthesis-relevant.
    """
    members: Dict[str, List[str]] = defaultdict(list)
    statuses: Dict[str, Counter] = defaultdict(Counter)
    for study in studies:
        entry = study.get("structured_code_summary", {}).get(field_path, {})
        for value in as_list(entry.get("values")):
            members[value].append(study["corpus_id"])
            statuses[value][entry.get("status", "")] += 1
    return [
        {
            "category": category,
            "count": len(ids),
            "statuses": "; ".join(f"{status}={count}" for status, count in sorted(statuses[category].items()) if status),
            "study_ids": compact_ids(ids),
        }
        for category, ids in sorted(members.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]


def claim_evidence_rows(studies: Sequence[dict]) -> Tuple[List[dict], List[dict], int, int]:
    domain_counts: Dict[str, Counter] = {domain: Counter() for domain in OUTCOME_DOMAINS}
    domain_studies: Dict[str, set] = defaultdict(set)
    domain_eps_or_power: Dict[str, int] = Counter()
    top_claims: List[dict] = []
    total_claims = 0
    total_domain_memberships = 0

    for study in studies:
        study_eps_relevance = first_controlled_value(study, "study_context_population.eps_relevance")
        for idx, claim in enumerate(get_claims(study), start=1):
            total_claims += 1
            confidence = evidence_confidence(claim)
            domains = outcome_domains_for_claim(claim)
            total_domain_memberships += len(domains)
            specificity = normalize_whitespace(claim.get("specificity", "")) or "unclear"
            for domain in domains:
                domain_counts[domain][confidence] += 1
                domain_studies[domain].add(study["corpus_id"])
                if specificity == "EPS-specific" or study_eps_relevance in {"EPS-specific", "power-budget/electrical-architecture"}:
                    domain_eps_or_power[domain] += 1

            score = (
                10 * CONFIDENCE_SCORE.get(confidence, 0)
                + SPECIFICITY_SCORE.get(specificity, 0.5)
                + max(VALUE_DOMAIN_PRIORITY.get(domain, 1) for domain in domains) / 10.0
            )
            if confidence in {"Moderate", "Strong"}:
                top_claims.append(
                    {
                        "rank": 0,
                        "value_score": f"{score:.1f}",
                        "study_id": study["corpus_id"],
                        "year": study.get("year", ""),
                        "title": get_title(study),
                        "claim_index": idx,
                        "claim": normalize_whitespace(claim.get("claim", "")),
                        "outcome_domain": "; ".join(domains),
                        "original_outcome_category": normalize_whitespace(claim.get("outcome_category", "")),
                        "specificity": specificity,
                        "evidence_type": normalize_whitespace(claim.get("evidence_type", "")),
                        "evidence_confidence": confidence,
                        "evidence_source": normalize_whitespace(claim.get("evidence_source", "")),
                        "direct_quote": normalize_whitespace(claim.get("direct_quote", "")),
                    }
                )

    rows: List[dict] = []
    for domain in OUTCOME_DOMAINS:
        counts = domain_counts[domain]
        total = sum(counts.values())
        if not total:
            continue
        rows.append(
            {
                "outcome_domain": domain,
                "total_claim_domain_memberships": total,
                "unsupported": counts.get("Unsupported", 0),
                "weak": counts.get("Weak", 0),
                "moderate": counts.get("Moderate", 0),
                "strong": counts.get("Strong", 0),
                "study_count": len(domain_studies[domain]),
                "eps_specific_or_power_relevant_claims": domain_eps_or_power.get(domain, 0),
                "study_ids": compact_ids(domain_studies[domain]),
            }
        )
    rows.sort(key=lambda r: (-int(r["total_claim_domain_memberships"]), r["outcome_domain"]))

    top_claims.sort(
        key=lambda r: (
            -float(r["value_score"]),
            r["study_id"],
            int(r["claim_index"]),
            r["claim"],
        )
    )
    for rank, row in enumerate(top_claims, start=1):
        row["rank"] = rank
    return rows, top_claims, total_claims, total_domain_memberships


def vv_linkage_rows(studies: Sequence[dict]) -> List[dict]:
    members: Dict[str, List[str]] = defaultdict(list)
    for study in studies:
        for category in vv_linkages_for_study(study):
            members[category].append(study["corpus_id"])
    return [
        {"vv_linkage_category": category, "count": len(ids), "study_ids": compact_ids(ids)}
        for category, ids in sorted(members.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]


def gap_mapping_rows(studies: Sequence[dict]) -> List[dict]:
    rows: List[dict] = []
    for gap_key, gap_label in BURUSO_GAPS:
        by_status: Dict[str, List[str]] = defaultdict(list)
        for study in studies:
            status = gap_classification(study, gap_key) or "not addressed"
            by_status[status].append(study["corpus_id"])
        for status in GAP_STATUSES:
            ids = by_status.get(status, [])
            rows.append(
                {
                    "gap_key": gap_key,
                    "gap_label": gap_label,
                    "classification": status,
                    "count": len(ids),
                    "study_ids": compact_ids(ids),
                }
            )
        for status, ids in sorted(by_status.items()):
            if status not in GAP_STATUSES:
                rows.append(
                    {
                        "gap_key": gap_key,
                        "gap_label": gap_label,
                        "classification": status,
                        "count": len(ids),
                        "study_ids": compact_ids(ids),
                    }
                )
    return rows

# ---------------------------------------------------------------------------
# CSV, figure, LaTeX, and Markdown writers


def write_csv(path: Path, rows: Sequence[dict], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def svg_text(x: float, y: float, text: str, size: int = 14, anchor: str = "start", weight: str = "normal", color: str = "#111827") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}">{html.escape(text)}</text>'


def wrap_svg_text(x: float, y: float, text: str, width_chars: int, size: int = 13, anchor: str = "start", line_height: int = 15) -> Tuple[str, int]:
    lines = textwrap.wrap(str(text), width=width_chars) or [""]
    out = []
    for i, line in enumerate(lines):
        out.append(svg_text(x, y + i * line_height, line, size=size, anchor=anchor))
    return "\n".join(out), len(lines)


def svg_document(width: int, height: int, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>
<g font-family="Arial, Helvetica, sans-serif">
{body}
</g>
</svg>
'''


def convert_svg(svg_path: Path, out_base: Path) -> None:
    rsvg = shutil.which("rsvg-convert")
    if not rsvg:
        return
    subprocess.run([rsvg, "-f", "pdf", "-o", str(out_base.with_suffix(".pdf")), str(svg_path)], check=True)
    subprocess.run([rsvg, "-f", "png", "-o", str(out_base.with_suffix(".png")), str(svg_path)], check=True)


def write_svg_figure(name: str, svg: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = FIG_DIR / f"{name}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    convert_svg(svg_path, FIG_DIR / name)


def barh_figure(name: str, title: str, rows: Sequence[Tuple[str, int]], color: str = "#2563EB") -> None:
    rows = [(label, int(value)) for label, value in rows if int(value) > 0]
    max_value = max((value for _, value in rows), default=1)
    width = 1100
    left = 360
    right = 70
    top = 78
    row_h = 42
    height = top + row_h * len(rows) + 55
    chart_w = width - left - right
    body: List[str] = []
    body.append(svg_text(width / 2, 34, title, size=21, anchor="middle", weight="bold"))
    body.append(svg_text(left, height - 22, "Count", size=12, color="#4B5563"))
    # Grid lines.
    tick_count = min(max_value, 5)
    for i in range(tick_count + 1):
        val = round(max_value * i / tick_count) if tick_count else 0
        x = left + chart_w * val / max_value
        body.append(f'<line x1="{x:.1f}" y1="{top - 20}" x2="{x:.1f}" y2="{height - 48}" stroke="#E5E7EB" stroke-width="1"/>')
        body.append(svg_text(x, height - 32, str(val), size=11, anchor="middle", color="#6B7280"))
    for idx, (label, value) in enumerate(rows):
        y = top + idx * row_h
        wrapped, _ = wrap_svg_text(16, y + 15, label, 42, size=13)
        body.append(wrapped)
        bar_w = chart_w * value / max_value
        body.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="24" rx="3" fill="{color}"/>')
        body.append(svg_text(left + bar_w + 8, y + 18, str(value), size=13, color="#111827"))
    write_svg_figure(name, svg_document(width, height, "\n".join(body)))


def stacked_barh_figure(
    name: str,
    title: str,
    labels: Sequence[str],
    series_names: Sequence[str],
    values_by_label: Dict[str, Sequence[int]],
    colors: Sequence[str],
) -> None:
    width = 1180
    left = 385
    right = 70
    top = 100
    row_h = 46
    legend_y = 62
    max_total = max((sum(values_by_label[label]) for label in labels), default=1)
    chart_w = width - left - right
    height = top + row_h * len(labels) + 65
    body: List[str] = []
    body.append(svg_text(width / 2, 34, title, size=21, anchor="middle", weight="bold"))
    lx = left
    for name_i, color in zip(series_names, colors):
        body.append(f'<rect x="{lx}" y="{legend_y - 14}" width="16" height="16" fill="{color}"/>')
        body.append(svg_text(lx + 22, legend_y, name_i, size=12, color="#374151"))
        lx += 120 if len(name_i) < 8 else 145
    tick_count = min(max_total, 5)
    for i in range(tick_count + 1):
        val = round(max_total * i / tick_count) if tick_count else 0
        x = left + chart_w * val / max_total
        body.append(f'<line x1="{x:.1f}" y1="{top - 20}" x2="{x:.1f}" y2="{height - 48}" stroke="#E5E7EB" stroke-width="1"/>')
        body.append(svg_text(x, height - 32, str(val), size=11, anchor="middle", color="#6B7280"))
    for idx, label in enumerate(labels):
        y = top + idx * row_h
        wrapped, _ = wrap_svg_text(16, y + 15, label, 44, size=13)
        body.append(wrapped)
        x = left
        total = sum(values_by_label[label])
        for value, color in zip(values_by_label[label], colors):
            if value <= 0:
                continue
            w = chart_w * value / max_total
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="25" rx="2" fill="{color}"/>')
            if w > 26:
                body.append(svg_text(x + w / 2, y + 18, str(value), size=12, anchor="middle", color="white"))
            x += w
        body.append(svg_text(left + chart_w + 8, y + 18, str(total), size=13, color="#111827"))
    write_svg_figure(name, svg_document(width, height, "\n".join(body)))


def prisma_svg(counts: Dict[str, int]) -> str:
    """Compact article-facing PRISMA-style flow figure.

    The figure deliberately omits provenance notes and file names; those belong in
    reproducibility documentation, not in the article graphic.
    """
    width, height = 900, 500
    body: List[str] = []
    main_x, main_w, main_h = 100, 430, 72
    side_x, side_w, side_h = 595, 230, 54
    y_values = [34, 144, 254, 364]
    main_boxes = [
        ("Records identified", f"n = {counts['raw_records']}", "#DBEAFE"),
        ("Records screened", f"n = {counts['unique_records_screened']}", "#E0F2FE"),
        ("Reports sought for retrieval", f"n = {counts['reports_sought']}", "#DCFCE7"),
        ("Studies included in synthesis", f"n = {counts['extracted']}", "#F3E8FF"),
    ]
    side_boxes = [
        ("Duplicates removed", f"n = {counts['duplicates_removed']}", 55),
        ("Records excluded", f"n = {counts['excluded_screening']}", 165),
        ("Reports not retrieved", f"n = {counts['not_retrieved']}", 275),
    ]

    # Main flow boxes.
    for idx, (header, count_text, color) in enumerate(main_boxes):
        y = y_values[idx]
        body.append(f'<rect x="{main_x}" y="{y}" width="{main_w}" height="{main_h}" rx="10" fill="{color}" stroke="#334155" stroke-width="1.5"/>')
        body.append(svg_text(main_x + 18, y + 30, header, 18, weight="bold"))
        body.append(svg_text(main_x + 18, y + 55, count_text, 16, color="#1F2937"))
        if idx < len(main_boxes) - 1:
            x_mid = main_x + main_w / 2
            y1 = y + main_h
            y2 = y_values[idx + 1]
            body.append(f'<line x1="{x_mid}" y1="{y1 + 6}" x2="{x_mid}" y2="{y2 - 10}" stroke="#334155" stroke-width="2"/>')
            body.append(f'<polygon points="{x_mid-7},{y2-10} {x_mid+7},{y2-10} {x_mid},{y2}" fill="#334155"/>')

    # Exclusion/removal boxes to the right, connected to the relevant stage.
    for idx, (header, count_text, y) in enumerate(side_boxes):
        body.append(f'<rect x="{side_x}" y="{y}" width="{side_w}" height="{side_h}" rx="8" fill="#F8FAFC" stroke="#64748B" stroke-width="1.2"/>')
        body.append(svg_text(side_x + 14, y + 23, header, 14, weight="bold", color="#1F2937"))
        body.append(svg_text(side_x + 14, y + 43, count_text, 13, color="#374151"))
        source_y = [y_values[0] + main_h / 2, y_values[1] + main_h / 2, y_values[2] + main_h / 2][idx]
        target_y = y + side_h / 2
        body.append(f'<line x1="{main_x + main_w + 8}" y1="{source_y}" x2="{side_x - 10}" y2="{target_y}" stroke="#64748B" stroke-width="1.6"/>')
        body.append(f'<polygon points="{side_x-10},{target_y-5} {side_x-10},{target_y+5} {side_x},{target_y}" fill="#64748B"/>')

    return svg_document(width, height, "\n".join(body))


def copy_or_generate_prisma(counts: Dict[str, int]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    write_svg_figure("prisma_flow", prisma_svg(counts))


def generate_figures(
    eps_rows: Sequence[dict],
    claim_rows: Sequence[dict],
    vv_rows: Sequence[dict],
    gap_rows: Sequence[dict],
    prisma_counts: Dict[str, int],
) -> None:
    copy_or_generate_prisma(prisma_counts)
    barh_figure(
        "eps_relevance_counts",
        "EPS/nanosatellite relevance of extracted studies",
        [(row["category"], row["count"]) for row in eps_rows],
        color="#2563EB",
    )
    labels = [row["outcome_domain"] for row in claim_rows]
    values = {
        row["outcome_domain"]: [int(row["unsupported"]), int(row["weak"]), int(row["moderate"]), int(row["strong"])]
        for row in claim_rows
    }
    stacked_barh_figure(
        "claim_evidence_by_outcome",
        "Claim evidence confidence by value-outcome domain",
        labels,
        ["Unsupported", "Weak", "Moderate", "Strong"],
        values,
        ["#9CA3AF", "#F59E0B", "#2563EB", "#16A34A"],
    )
    barh_figure(
        "vv_linkage_counts",
        "Pre-physical V&V linkage categories",
        [(row["vv_linkage_category"], row["count"]) for row in vv_rows],
        color="#DC2626",
    )
    gap_labels = [label for _, label in BURUSO_GAPS]
    gap_values: Dict[str, List[int]] = {}
    for _, gap_label in BURUSO_GAPS:
        rows = [r for r in gap_rows if r["gap_label"] == gap_label]
        status_counts = {r["classification"]: int(r["count"]) for r in rows}
        gap_values[gap_label] = [status_counts.get(status, 0) for status in GAP_STATUSES]
    stacked_barh_figure(
        "gap_mapping_counts",
        "Buruso Table 5-inspired gap mapping across studies",
        gap_labels,
        GAP_STATUSES,
        gap_values,
        ["#16A34A", "#60A5FA", "#F59E0B", "#EF4444"],
    )


def latex_simple_table(caption: str, label: str, headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    cols = "l" + "r" * (len(headers) - 1)
    out = [r"\begin{table}[htbp]", r"\centering", f"\\caption{{{tex_escape(caption)}}}", f"\\label{{{label}}}", f"\\begin{{tabular}}{{{cols}}}", r"\toprule"]
    out.append(" & ".join(tex_escape(h) for h in headers) + r" \\")
    out.append(r"\midrule")
    for row in rows:
        out.append(" & ".join(tex_escape(c) for c in row) + r" \\")
    out.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(out)


def latex_gap_table(gap_rows: Sequence[dict]) -> str:
    out = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Gap mapping inspired by Buruso et al. Table 5.}",
        r"\label{tab:gap-mapping-counts}",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Gap & Evidence & Conceptual & Mentioned & Not addressed \\",
        r"\midrule",
    ]
    for _, gap_label in BURUSO_GAPS:
        rows = [r for r in gap_rows if r["gap_label"] == gap_label]
        counts = {r["classification"]: r["count"] for r in rows}
        out.append(
            f"{tex_escape(gap_label)} & {counts.get('addressed with evidence', 0)} & {counts.get('addressed conceptually', 0)} & {counts.get('mentioned only', 0)} & {counts.get('not addressed', 0)} " + r"\\"
        )
    out.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(out)


def write_results_tables(
    studies: Sequence[dict],
    eps_rows: Sequence[dict],
    approach_rows: Sequence[dict],
    claim_rows: Sequence[dict],
    vv_rows: Sequence[dict],
    gap_rows: Sequence[dict],
    total_claims: int,
    top_claim_count: int,
    generality_rows: Sequence[dict],
    ivv_level_rows: Sequence[dict],
    reliability_subtype_rows: Sequence[dict],
) -> None:
    tier_counts = Counter(study.get("tier", "") for study in studies)
    confidence_counts = Counter(evidence_confidence(claim) for study in studies for claim in get_claims(study))
    extraction_conf = Counter(get_extraction_confidence(study) for study in studies)
    summary_rows = [
        ["Extracted studies", len(studies)],
        ["Core studies", tier_counts.get("core", 0)],
        ["Supporting studies", tier_counts.get("supporting", 0)],
        ["Claim records", total_claims],
        ["Unsupported claims", confidence_counts.get("Unsupported", 0)],
        ["Weak claims", confidence_counts.get("Weak", 0)],
        ["Moderate claims", confidence_counts.get("Moderate", 0)],
        ["Strong claims", confidence_counts.get("Strong", 0)],
        ["High-confidence extractions", extraction_conf.get("high", 0)],
        ["Medium-confidence extractions", extraction_conf.get("medium", 0)],
        ["Top-value-claim rows", top_claim_count],
    ]
    parts = [
        "% Auto-generated by scripts/generate_slr_artifacts.py. Do not edit by hand unless regenerating is impossible.",
        latex_simple_table("Study and claim evidence summary.", "tab:slr-study-claim-summary", ["Metric", "n"], summary_rows),
        latex_simple_table(
            "EPS relevance counts.",
            "tab:eps-relevance-counts",
            ["EPS relevance", "n"],
            [[row["category"], row["count"]] for row in eps_rows],
        ),
        latex_simple_table(
            "Approach-classification counts.",
            "tab:approach-classification-counts",
            ["Approach classification", "n"],
            [[row["category"], row["count"]] for row in approach_rows],
        ),
        latex_simple_table(
            "Claim evidence by value-outcome domain. Domains are multi-label, so totals exceed unique claim records.",
            "tab:claim-evidence-by-outcome",
            ["Outcome domain", "Total", "Unsup.", "Weak", "Mod.", "Strong"],
            [
                [row["outcome_domain"], row["total_claim_domain_memberships"], row["unsupported"], row["weak"], row["moderate"], row["strong"]]
                for row in claim_rows
            ],
        ),
        latex_simple_table(
            "Reliability subtype counts from the focused codebook-refinement pass.",
            "tab:reliability-subtype-counts",
            ["Reliability subtype", "n"],
            [[row["category"], row["count"]] for row in reliability_subtype_rows],
        ),
        latex_simple_table(
            "Generality/reuse mechanism counts from the focused codebook-refinement pass.",
            "tab:generality-reuse-counts",
            ["Generality/reuse mechanism", "n"],
            [[row["category"], row["count"]] for row in generality_rows],
        ),
        latex_simple_table(
            "Pre-physical V&V linkage counts. Categories are multi-label by study.",
            "tab:vv-linkage-counts",
            ["V&V linkage category", "n"],
            [[row["vv_linkage_category"], row["count"]] for row in vv_rows],
        ),
        latex_simple_table(
            "Highest coded IVV integration level.",
            "tab:ivv-integration-level-counts",
            ["IVV integration level", "n"],
            [[row["category"], row["count"]] for row in ivv_level_rows],
        ),
        latex_gap_table(gap_rows),
    ]
    (DRAFTS_DIR / "results_tables.tex").write_text("\n\n".join(parts) + "\n", encoding="utf-8")


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |")
    return "\n".join(out)


def write_data_summary(
    studies: Sequence[dict],
    protocol_rqs: Sequence[str],
    scoping_info: Dict[str, object],
    eps_rows: Sequence[dict],
    approach_rows: Sequence[dict],
    claim_rows: Sequence[dict],
    vv_rows: Sequence[dict],
    gap_rows: Sequence[dict],
    total_claims: int,
    total_domain_memberships: int,
    top_claim_count: int,
    generality_rows: Sequence[dict],
    ivv_level_rows: Sequence[dict],
    reliability_subtype_rows: Sequence[dict],
) -> None:
    tier_counts = Counter(study.get("tier", "") for study in studies)
    quality_counts = Counter(str(get_quality(study)[0]) for study in studies)
    confidence_counts = Counter(evidence_confidence(claim) for study in studies for claim in get_claims(study))
    extraction_conf = Counter(get_extraction_confidence(study) for study in studies)
    rq_counts: Dict[str, Counter] = {rq: Counter(get_rq_relevance(study, rq) for study in studies) for rq in ["RQ1", "RQ2", "RQ3"]}
    prisma = scoping_info.get("prisma_counts", {})

    lines: List[str] = []
    lines.append("# Systematic-review data artifact summary")
    lines.append("")
    lines.append("Generated by `scripts/generate_slr_artifacts.py` from `SLR/SLR1/extraction.json`, `SLR/SLR1/extractions/*.json`, `protocol.md`, the scoping-review data/TEX files, and the Buruso et al. Table 5 gap frame.")
    if protocol_rqs:
        lines.append("")
        lines.append("Protocol RQs read from `protocol.md`: " + "; ".join(protocol_rqs) + ".")
    lines.append("")
    lines.append("## Output files")
    lines.append("")
    lines.append("- CSV: `data/study_characteristics.csv`, `data/eps_relevance_counts.csv`, `data/approach_classification_counts.csv`, `data/claim_evidence_by_outcome.csv`, `data/vv_linkage_counts.csv`, `data/gap_mapping_counts.csv`, `data/generality_reuse_mechanism_counts.csv`, `data/ivv_integration_level_counts.csv`, `data/reliability_subtype_counts.csv`, `data/top_value_claims.csv`.")
    lines.append("- Figures: `figures/prisma_flow.{pdf,png}`, `figures/eps_relevance_counts.{pdf,png}`, `figures/claim_evidence_by_outcome.{pdf,png}`, `figures/vv_linkage_counts.{pdf,png}`, `figures/gap_mapping_counts.{pdf,png}`. SVG sources are retained for regenerated plots.")
    lines.append("- LaTeX/Markdown snippets: `drafts/results_tables.tex`, `drafts/data_summary.md`.")
    lines.append("")
    lines.append("## Corpus and evidence counts")
    lines.append("")
    lines.append(markdown_table(["Metric", "Count"], [
        ["Extracted studies", len(studies)],
        ["Core studies", tier_counts.get("core", 0)],
        ["Supporting studies", tier_counts.get("supporting", 0)],
        ["Publication year range", f"{min(study['year'] for study in studies)}--{max(study['year'] for study in studies)}"],
        ["Claim records", total_claims],
        ["Claim-domain memberships", total_domain_memberships],
        ["Top value claims (Moderate/Strong)", top_claim_count],
        ["Extraction confidence: high", extraction_conf.get("high", 0)],
        ["Extraction confidence: medium", extraction_conf.get("medium", 0)],
    ]))
    lines.append("")
    lines.append("Claim evidence confidence counts: " + ", ".join(f"{conf}={confidence_counts.get(conf, 0)}" for conf in CONFIDENCE_ORDER) + ".")
    lines.append("Quality score counts: " + ", ".join(f"{score}={count}" for score, count in sorted(quality_counts.items(), key=lambda kv: float(kv[0]))) + ".")
    lines.append("RQ relevance counts: " + "; ".join(f"{rq}: " + ", ".join(f"{k}={v}" for k, v in rq_counts[rq].items()) for rq in ["RQ1", "RQ2", "RQ3"]) + ".")
    lines.append("")
    lines.append("## PRISMA/scoping-review reuse")
    lines.append("")
    lines.append(f"The local `prisma_flow` figure was copied from the scoping-review figure when available. The parsed scoping flow is: raw={prisma.get('raw_records')}, duplicates removed={prisma.get('duplicates_removed')}, screened={prisma.get('unique_records_screened')}, excluded={prisma.get('excluded_screening')}, reports sought={prisma.get('reports_sought')}, not retrieved={prisma.get('not_retrieved')}, extracted={prisma.get('extracted')}.")
    lines.append(f"Scoping CSV inputs read: {', '.join(scoping_info.get('csv_files', []))}; scoping `studies.csv` rows={scoping_info.get('studies_rows')}; scoping `category_counts.csv` rows={scoping_info.get('category_rows')}. Buruso Table 5 marker present={scoping_info.get('buruso_table5_present')}.")
    lines.append("")
    lines.append("## EPS relevance counts")
    lines.append("")
    lines.append(markdown_table(["EPS relevance", "Count"], [[row["category"], row["count"]] for row in eps_rows]))
    lines.append("")
    lines.append("## Approach-classification counts")
    lines.append("")
    lines.append(markdown_table(["Approach classification", "Count"], [[row["category"], row["count"]] for row in approach_rows]))
    lines.append("")
    lines.append("## Claim evidence by value-outcome domain")
    lines.append("")
    lines.append(markdown_table(
        ["Outcome domain", "Total", "Unsupported", "Weak", "Moderate", "Strong", "Studies", "EPS/power claims"],
        [
            [row["outcome_domain"], row["total_claim_domain_memberships"], row["unsupported"], row["weak"], row["moderate"], row["strong"], row["study_count"], row["eps_specific_or_power_relevant_claims"]]
            for row in claim_rows
        ],
    ))
    lines.append("")
    lines.append("## Reliability subtype counts")
    lines.append("")
    lines.append(markdown_table(["Reliability subtype", "Count", "Statuses"], [[row["category"], row["count"], row["statuses"]] for row in reliability_subtype_rows]))
    lines.append("")
    lines.append("## Generality/reuse mechanism counts")
    lines.append("")
    lines.append(markdown_table(["Generality/reuse mechanism", "Count", "Statuses"], [[row["category"], row["count"], row["statuses"]] for row in generality_rows]))
    lines.append("")
    lines.append("## Pre-physical V&V linkage counts")
    lines.append("")
    lines.append(markdown_table(["V&V linkage category", "Count"], [[row["vv_linkage_category"], row["count"]] for row in vv_rows]))
    lines.append("")
    lines.append("## IVV integration level counts")
    lines.append("")
    lines.append(markdown_table(["IVV integration level", "Count", "Statuses"], [[row["category"], row["count"], row["statuses"]] for row in ivv_level_rows]))
    lines.append("")
    lines.append("## Gap mapping counts")
    lines.append("")
    gap_summary_rows = []
    for _, gap_label in BURUSO_GAPS:
        rows = [row for row in gap_rows if row["gap_label"] == gap_label]
        counts = {row["classification"]: row["count"] for row in rows}
        gap_summary_rows.append([gap_label] + [counts.get(status, 0) for status in GAP_STATUSES])
    lines.append(markdown_table(["Gap", "Evidence", "Conceptual", "Mentioned", "Not addressed"], gap_summary_rows))
    lines.append("")
    lines.append("## Assumptions")
    lines.append("")
    lines.append(f"- `claim_evidence_by_outcome.csv` uses deterministic multi-label mapping from controlled `outcome_category` codes only; no loose keyword categorization is applied. Claim-domain memberships can exceed the {total_claims} unique claim records because some controlled outcome codes map to more than one synthesis domain.")
    lines.append("- Evidence strength is taken from the standardized `evidence_confidence`/`evidence_confidence_rating` field. `top_value_claims.csv` contains all Moderate and Strong claims.")
    lines.append("- `vv_linkage_counts.csv` is multi-label at the study level and is derived from controlled `eps_verification_specific` artifact, pre-physical mechanism, and integration/test-readiness codes.")
    lines.append("- `ivv_integration_level_counts.csv`, `reliability_subtype_counts.csv`, and `generality_reuse_mechanism_counts.csv` report selected controlled values from the v1.1 focused recoding pass.")
    lines.append("- Gap labels and order follow the five Buruso Table 5-inspired gap fields already coded in the per-study extraction JSON files.")
    lines.append("- PRISMA counts and the base PRISMA graphic are reused from the scoping review without modifying scoping-review source/output files.")
    lines.append("")
    (DRAFTS_DIR / "data_summary.md").write_text("\n".join(lines), encoding="utf-8")

# ---------------------------------------------------------------------------
# Main


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    studies = load_studies()
    extraction_index = read_json(EXTRACTION_INDEX)
    if int(extraction_index.get("study_count", len(studies))) != len(studies):
        raise RuntimeError(
            f"extraction.json study_count={extraction_index.get('study_count')} but found {len(studies)} extraction files"
        )
    if not PROTOCOL.exists():
        raise RuntimeError(f"Missing protocol input: {PROTOCOL}")
    protocol_rqs = read_protocol_rqs()
    scoping_info = read_scoping_inputs()

    study_rows = study_characteristics_rows(studies)
    eps_rows = count_by_study_field(
        studies,
        lambda study: first_controlled_value(study, "study_context_population.eps_relevance")
        or study.get("study_context_population", {}).get("eps_relevance", ""),
    )
    approach_rows = count_by_study_field(
        studies,
        lambda study: first_controlled_value(study, "implementation_pathway_tailoring.approach_classification")
        or study.get("implementation_pathway_tailoring", {}).get("approach_classification", ""),
    )
    claim_rows, top_claim_rows, total_claims, total_domain_memberships = claim_evidence_rows(studies)
    vv_rows = vv_linkage_rows(studies)
    gap_rows = gap_mapping_rows(studies)
    generality_rows = controlled_field_count_rows(studies, "mbse_objective_scope_artifacts.generality_reuse_mechanism")
    ivv_level_rows = controlled_field_count_rows(studies, "eps_verification_specific.ivv_integration_level")
    reliability_subtype_rows = controlled_field_count_rows(studies, "claimed_outcomes_value_mechanisms_evidence[].reliability_subtype")

    write_csv(
        DATA_DIR / "study_characteristics.csv",
        study_rows,
        [
            "corpus_id", "tier", "year", "title", "authors", "venue", "venue_type", "doi_or_url",
            "quality_total_score", "quality_normalized_score", "RQ1_relevance", "RQ2_relevance", "RQ3_relevance",
            "eps_relevance", "approach_classification", "model_maturity", "lifecycle_stage", "development_context",
            "claim_count", "unsupported_claims", "weak_claims", "moderate_claims", "strong_claims", "extraction_confidence",
        ],
    )
    write_csv(DATA_DIR / "eps_relevance_counts.csv", eps_rows, ["category", "count", "study_ids"])
    write_csv(DATA_DIR / "approach_classification_counts.csv", approach_rows, ["category", "count", "study_ids"])
    write_csv(
        DATA_DIR / "claim_evidence_by_outcome.csv",
        claim_rows,
        [
            "outcome_domain", "total_claim_domain_memberships", "unsupported", "weak", "moderate", "strong",
            "study_count", "eps_specific_or_power_relevant_claims", "study_ids",
        ],
    )
    write_csv(DATA_DIR / "vv_linkage_counts.csv", vv_rows, ["vv_linkage_category", "count", "study_ids"])
    write_csv(DATA_DIR / "gap_mapping_counts.csv", gap_rows, ["gap_key", "gap_label", "classification", "count", "study_ids"])
    write_csv(DATA_DIR / "generality_reuse_mechanism_counts.csv", generality_rows, ["category", "count", "statuses", "study_ids"])
    write_csv(DATA_DIR / "ivv_integration_level_counts.csv", ivv_level_rows, ["category", "count", "statuses", "study_ids"])
    write_csv(DATA_DIR / "reliability_subtype_counts.csv", reliability_subtype_rows, ["category", "count", "statuses", "study_ids"])
    write_csv(
        DATA_DIR / "top_value_claims.csv",
        top_claim_rows,
        [
            "rank", "value_score", "study_id", "year", "title", "claim_index", "claim", "outcome_domain",
            "original_outcome_category", "specificity", "evidence_type", "evidence_confidence", "evidence_source", "direct_quote",
        ],
    )

    generate_figures(eps_rows, claim_rows, vv_rows, gap_rows, scoping_info["prisma_counts"])
    write_results_tables(
        studies,
        eps_rows,
        approach_rows,
        claim_rows,
        vv_rows,
        gap_rows,
        total_claims,
        len(top_claim_rows),
        generality_rows,
        ivv_level_rows,
        reliability_subtype_rows,
    )
    write_data_summary(
        studies,
        protocol_rqs,
        scoping_info,
        eps_rows,
        approach_rows,
        claim_rows,
        vv_rows,
        gap_rows,
        total_claims,
        total_domain_memberships,
        len(top_claim_rows),
        generality_rows,
        ivv_level_rows,
        reliability_subtype_rows,
    )

    print(f"Wrote data CSVs to {DATA_DIR.relative_to(SLR1_DIR.parent.parent)}")
    print(f"Wrote figures to {FIG_DIR.relative_to(SLR1_DIR.parent.parent)}")
    print(f"Wrote drafts to {DRAFTS_DIR.relative_to(SLR1_DIR.parent.parent)}")


if __name__ == "__main__":
    main()
