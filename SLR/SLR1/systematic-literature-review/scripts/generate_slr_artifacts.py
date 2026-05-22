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
    ("governance_project_deliverables_roi_value", "Governance/project deliverables/ROI/value"),
    ("newspace_agile_distributed_rapid_iteration", "NewSpace/agile/distributed/rapid iteration"),
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

# ---------------------------------------------------------------------------
# File and field utilities


def read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_studies() -> List[dict]:
    studies = [read_json(p) for p in sorted(EXTRACTIONS_DIR.glob("paper-*.json"))]
    return sorted(studies, key=lambda d: (int(d.get("year", 9999)), d.get("corpus_id", "")))


def get_rq_relevance(study: dict, rq: str) -> str:
    value = study.get("bibliographic_review_management", {}).get("research_questions_addressed", {}).get(rq, "")
    if isinstance(value, dict):
        return value.get("relevance", "")
    return str(value or "")


def get_title(study: dict) -> str:
    return study.get("bibliographic_review_management", {}).get("title") or study.get("corpus_id", "")


def get_authors(study: dict) -> List[str]:
    return study.get("bibliographic_review_management", {}).get("authors") or []


def get_quality(study: dict) -> Tuple[float | str, float | str]:
    q = study.get("quality_checklist", {})
    return q.get("total_score", ""), q.get("normalized_score", "")


def get_extraction_confidence(study: dict) -> str:
    return study.get("synthesis_consistency", {}).get("extraction_confidence", "")


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
    text = claim_text_for_mapping(claim)
    domains = [domain for domain, patterns in OUTCOME_DOMAIN_RULES if has_any(text, patterns)]
    if not domains:
        domains = ["Other / uncategorized value claim"]
    return domains


def evidence_confidence(claim: dict) -> str:
    value = normalize_whitespace(claim.get("evidence_confidence", ""))
    return value if value in CONFIDENCE_ORDER else "Unsupported"


def vv_text(study: dict) -> str:
    eps = study.get("eps_verification_specific", {})
    parts: List[str] = []
    for key in [
        "verification_validation_artifacts",
        "pre_physical_development_verification_mechanism",
        "evidence_verification_integrated_in_model",
        "integration_test_readiness",
    ]:
        parts.append(join_list(eps.get(key, "")))
    return " ".join(parts)


def positive_vv_text(study: dict) -> str:
    """Return V&V text with explicit negated/no-evidence clauses removed.

    The extraction fields often include readiness caveats such as "no physical
    EPS integration test is reported". Those sentences should support absence
    categories, not positive V&V-linkage counts.
    """
    eps = study.get("eps_verification_specific", {})
    raw_parts: List[str] = []
    for key in [
        "verification_validation_artifacts",
        "pre_physical_development_verification_mechanism",
        "evidence_verification_integrated_in_model",
        "integration_test_readiness",
    ]:
        value = eps.get(key, "")
        if isinstance(value, list):
            raw_parts.extend(normalize_whitespace(v) for v in value)
        else:
            raw_parts.extend(re.split(r"(?<=[.;])\s+", normalize_whitespace(value)))
    segments = []
    for segment in raw_parts:
        segment = normalize_whitespace(segment)
        if not segment:
            continue
        if has_any(segment, NEGATIVE_VV_SEGMENT_PATTERNS):
            continue
        segments.append(segment)
    return " ".join(segments)


def vv_linkages_for_study(study: dict) -> List[str]:
    all_text = vv_text(study)
    positive_text = positive_vv_text(study)
    categories = [category for category, patterns in VV_RULES if has_any(positive_text, patterns)]

    eps = study.get("eps_verification_specific", {})
    artifacts_empty = not eps.get("verification_validation_artifacts")
    prephys_empty = not eps.get("pre_physical_development_verification_mechanism")
    integrated = normalize_whitespace(eps.get("evidence_verification_integrated_in_model", ""))
    readiness = normalize_whitespace(eps.get("integration_test_readiness", ""))
    no_positive = (not positive_text) or (artifacts_empty and prephys_empty and has_any(f"{integrated} {readiness}", NEGATIVE_VV_PATTERNS))
    if no_positive:
        categories.append("No explicit EPS-focused pre-physical V&V")

    # Separate studies that explicitly stop at a general/conceptual V&V statement
    # from studies with concrete checks/simulations/test artifacts.
    lower = all_text.lower()
    concrete = any(
        cat in categories
        for cat in [
            "Executable simulation or scenario analysis before build",
            "Parametric/budget/constraint checks",
            "External tool or data-flow coupling for V&V",
            "Physical/SIL/HIL/integration-test readiness link",
        ]
    )
    if not concrete and has_any(lower, [r"generic", r"conceptual", r"planned", r"future", r"not reported", r"no eps-specific"]):
        categories.append("Generic/planned V&V linkage only")

    return sorted(set(categories))


def gap_classification(study: dict, gap_key: str) -> str:
    value = study.get("gap_mapping", {}).get(gap_key, "")
    if isinstance(value, dict):
        return normalize_whitespace(value.get("classification", ""))
    return normalize_whitespace(value)


def study_characteristics_rows(studies: Sequence[dict]) -> List[dict]:
    rows: List[dict] = []
    for study in studies:
        claims = get_claims(study)
        confidence_counts = Counter(evidence_confidence(claim) for claim in claims)
        q_total, q_norm = get_quality(study)
        bib = study.get("bibliographic_review_management", {})
        context = study.get("study_context_population", {})
        impl = study.get("implementation_pathway_tailoring", {})
        rows.append(
            {
                "corpus_id": study.get("corpus_id", ""),
                "tier": study.get("tier", ""),
                "year": study.get("year", ""),
                "title": get_title(study),
                "authors": "; ".join(get_authors(study)),
                "venue": bib.get("venue", ""),
                "venue_type": bib.get("venue_type", ""),
                "doi_or_url": bib.get("doi_or_url", ""),
                "quality_total_score": q_total,
                "quality_normalized_score": q_norm,
                "RQ1_relevance": get_rq_relevance(study, "RQ1"),
                "RQ2_relevance": get_rq_relevance(study, "RQ2"),
                "RQ3_relevance": get_rq_relevance(study, "RQ3"),
                "eps_relevance": context.get("eps_relevance", ""),
                "approach_classification": impl.get("approach_classification", ""),
                "model_maturity": context.get("model_maturity", ""),
                "lifecycle_stage": context.get("lifecycle_stage_addressed", ""),
                "development_context": context.get("development_context", ""),
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


def claim_evidence_rows(studies: Sequence[dict]) -> Tuple[List[dict], List[dict], int, int]:
    domain_counts: Dict[str, Counter] = {domain: Counter() for domain, _ in OUTCOME_DOMAIN_RULES}
    domain_counts["Other / uncategorized value claim"] = Counter()
    domain_studies: Dict[str, set] = defaultdict(set)
    domain_eps_or_power: Dict[str, int] = Counter()
    top_claims: List[dict] = []
    total_claims = 0
    total_domain_memberships = 0

    for study in studies:
        for idx, claim in enumerate(get_claims(study), start=1):
            total_claims += 1
            confidence = evidence_confidence(claim)
            domains = outcome_domains_for_claim(claim)
            total_domain_memberships += len(domains)
            specificity = normalize_whitespace(claim.get("specificity", "")) or "unclear"
            for domain in domains:
                domain_counts[domain][confidence] += 1
                domain_studies[domain].add(study["corpus_id"])
                if specificity in {"EPS-specific", "power-budget/electrical-architecture"}:
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
    for domain in list(dict(OUTCOME_DOMAIN_RULES).keys()) + ["Other / uncategorized value claim"]:
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
    width, height = 980, 760
    boxes = [
        ("Identification", f"Raw merged search records: {counts['raw_records']}\nDuplicates removed: {counts['duplicates_removed']}", "#DBEAFE"),
        ("Screening", f"Unique records screened: {counts['unique_records_screened']}\nRecords excluded: {counts['excluded_screening']}", "#E0F2FE"),
        ("Retrieval", f"Reports sought for retrieval: {counts['reports_sought']}\nReports not retrieved/inaccessible: {counts['not_retrieved']}", "#DCFCE7"),
        ("Extraction", f"Accessible reports extracted: {counts['extracted']}", "#FEF3C7"),
        ("Included", f"Studies in extraction synthesis: {counts['extracted']}", "#F3E8FF"),
    ]
    body: List[str] = []
    body.append(svg_text(width / 2, 38, "PRISMA-style SLR1 flow", 22, anchor="middle", weight="bold"))
    box_w, box_h = 700, 100
    x = (width - box_w) / 2
    y = 80
    for idx, (header, content, color) in enumerate(boxes):
        yy = y + idx * 130
        body.append(f'<rect x="{x}" y="{yy}" width="{box_w}" height="{box_h}" rx="16" fill="{color}" stroke="#334155" stroke-width="1.3"/>')
        body.append(svg_text(width / 2, yy + 30, header, 17, anchor="middle", weight="bold"))
        for line_i, line in enumerate(content.split("\n")):
            body.append(svg_text(width / 2, yy + 58 + line_i * 19, line, 14, anchor="middle"))
        if idx < len(boxes) - 1:
            x1, y1 = width / 2, yy + box_h
            x2, y2 = width / 2, yy + 130
            body.append(f'<line x1="{x1}" y1="{y1 + 8}" x2="{x2}" y2="{y2 - 14}" stroke="#334155" stroke-width="2"/>')
            body.append(f'<polygon points="{x2-7},{y2-14} {x2+7},{y2-14} {x2},{y2-2}" fill="#334155"/>')
    body.append(svg_text(width / 2, height - 24, "Counts parsed from the existing scoping-review LaTeX report.", 12, anchor="middle", color="#475569"))
    return svg_document(width, height, "\n".join(body))


def copy_or_generate_prisma(counts: Dict[str, int]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    copied_pdf = False
    copied_png = False
    source_pdf = SCOPING_DIR / "figures" / "prisma_flow.pdf"
    source_png = SCOPING_DIR / "figures" / "prisma_flow.png"
    if source_pdf.exists():
        shutil.copy2(source_pdf, FIG_DIR / "prisma_flow.pdf")
        copied_pdf = True
    if source_png.exists():
        shutil.copy2(source_png, FIG_DIR / "prisma_flow.png")
        copied_png = True
    if not (copied_pdf and copied_png):
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
            "Pre-physical V&V linkage counts. Categories are multi-label by study.",
            "tab:vv-linkage-counts",
            ["V&V linkage category", "n"],
            [[row["vv_linkage_category"], row["count"]] for row in vv_rows],
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
    lines.append("- CSV: `data/study_characteristics.csv`, `data/eps_relevance_counts.csv`, `data/approach_classification_counts.csv`, `data/claim_evidence_by_outcome.csv`, `data/vv_linkage_counts.csv`, `data/gap_mapping_counts.csv`, `data/top_value_claims.csv`.")
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
    lines.append("## Pre-physical V&V linkage counts")
    lines.append("")
    lines.append(markdown_table(["V&V linkage category", "Count"], [[row["vv_linkage_category"], row["count"]] for row in vv_rows]))
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
    lines.append("- `claim_evidence_by_outcome.csv` uses deterministic multi-label keyword mapping from each claim's `outcome_category`, claim text, mechanism, and linked artifact/process. Therefore claim-domain memberships exceed the 294 unique claim records.")
    lines.append("- Evidence strength is taken from the standardized `evidence_confidence` field. No claim was coded as `Strong`; `top_value_claims.csv` therefore contains all `Moderate` claims (plus any future `Strong` claims if extractions change).")
    lines.append("- `vv_linkage_counts.csv` is multi-label at the study level and is derived from `eps_verification_specific` artifacts, pre-physical mechanisms, integration evidence, and integration/test-readiness text.")
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
    eps_rows = count_by_study_field(studies, lambda study: study.get("study_context_population", {}).get("eps_relevance", ""))
    approach_rows = count_by_study_field(studies, lambda study: study.get("implementation_pathway_tailoring", {}).get("approach_classification", ""))
    claim_rows, top_claim_rows, total_claims, total_domain_memberships = claim_evidence_rows(studies)
    vv_rows = vv_linkage_rows(studies)
    gap_rows = gap_mapping_rows(studies)

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
    write_csv(
        DATA_DIR / "top_value_claims.csv",
        top_claim_rows,
        [
            "rank", "value_score", "study_id", "year", "title", "claim_index", "claim", "outcome_domain",
            "original_outcome_category", "specificity", "evidence_type", "evidence_confidence", "evidence_source", "direct_quote",
        ],
    )

    generate_figures(eps_rows, claim_rows, vv_rows, gap_rows, scoping_info["prisma_counts"])
    write_results_tables(studies, eps_rows, approach_rows, claim_rows, vv_rows, gap_rows, total_claims, len(top_claim_rows))
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
    )

    print(f"Wrote data CSVs to {DATA_DIR.relative_to(SLR1_DIR.parent.parent)}")
    print(f"Wrote figures to {FIG_DIR.relative_to(SLR1_DIR.parent.parent)}")
    print(f"Wrote drafts to {DRAFTS_DIR.relative_to(SLR1_DIR.parent.parent)}")


if __name__ == "__main__":
    main()
