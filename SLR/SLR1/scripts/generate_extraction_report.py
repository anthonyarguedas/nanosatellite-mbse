#!/usr/bin/env python3
"""Generate a LaTeX findings report from the SLR1 extraction corpus.

The script intentionally uses deterministic fields and keyword rules only.  It
reads protocol.md, extraction.json, and the per-study extraction JSON files, then
regenerates figures, derived classification tables, and report/extraction_findings.tex.

Run from any directory:
    python3 SLR/SLR1/scripts/generate_extraction_report.py
"""
from __future__ import annotations

import csv
import json
import math
import re
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXTRACTIONS_DIR = ROOT / "extractions"
REPORT_DIR = ROOT / "report"
FIG_DIR = REPORT_DIR / "figures"
DATA_DIR = REPORT_DIR / "data"

# --- deterministic category rules -------------------------------------------------

OUTCOME_RULES: List[Tuple[str, Sequence[str]]] = [
    ("Traceability, consistency, or single source of truth", [
        r"traceab", r"consistent|consistency|coherent|cohesive", r"single source", r"source of truth",
        r"central design baseline", r"satisf", r"coverage", r"unambiguous"
    ]),
    ("Reuse, templates, standardization, or replicability", [
        r"reus", r"template", r"reference model", r"standardiz", r"uniformity", r"checklist", r"replicab", r"150%"
    ]),
    ("Integration, interoperability, or data exchange", [
        r"integrat", r"interoperab", r"data flow", r"information flow", r"exchange", r"repository", r"database",
        r"central data", r"cde", r"plm", r"interface", r"web of connections"
    ]),
    ("Efficiency, automation, or reduced time/cost/effort", [
        r"efficien", r"productiv", r"faster", r"rapid", r"shorten", r"reduc", r"cost", r"burden", r"effort",
        r"automation|automated|automatic", r"manual intervention", r"streamline"
    ]),
    ("Simulation, trade-space, budget, or early analysis support", [
        r"simulation|simulat", r"trade", r"budget", r"parametric", r"scenario", r"doe", r"monte carlo",
        r"sensitivity", r"sizing", r"feasibility", r"design-space", r"screening", r"performance"
    ]),
    ("Verification, validation, test, or compliance support", [
        r"verif", r"validat", r"test", r"requirements-in-loop", r"compliance", r"coverage"
    ]),
    ("Communication, collaboration, or stakeholder alignment", [
        r"communicat", r"collaborat", r"sharing|share", r"team", r"stakeholder", r"student", r"university", r"concurrent|parallel"
    ]),
    ("Reliability, mission success, quality, risk, or robustness", [
        r"reliab", r"mission success", r"risk", r"quality", r"robust", r"failure", r"confidence", r"correct-by-construction", r"compatible components"
    ]),
    ("Documentation, configuration, or change management", [
        r"document", r"report generation", r"configuration", r"change propagation", r"change management", r"changes propagate",
        r"synchron|sync", r"version", r"generated documents"
    ]),
    ("Openness, accessibility, or reproducibility", [
        r"open-source", r"public release", r"accessib", r"reproduc", r"replicab", r"license", r"community"
    ]),
]

# Phrases that indicate an extraction bullet is reporting absence rather than a
# claimed positive outcome.  We keep these as separate gap evidence.
NEGATIVE_OUTCOME_PATTERNS = [
    r"not reported", r"no direct", r"no explicit", r"not directly", r"not demonstrated",
    r"no .* outcome", r"no .* improvement", r"not .* measured", r"only indirectly", r"not .* found",
]

EXACT_TOOL_RULES: List[Tuple[str, Sequence[str]]] = [
    ("SysML", [r"\bsysml\b"]),
    ("Cameo / MagicDraw / CATIA Magic", [r"cameo", r"magicdraw", r"catia magic", r"no magic"]),
    ("MATLAB / Simulink", [r"matlab", r"simulink"]),
    ("STK / GMAT / DRAMA orbit tools", [r"\bstk\b", r"systems tool kit", r"gmat", r"drama"]),
    ("ModelCenter / MBSE Analyzer", [r"modelcenter", r"mbse analyzer", r"phoenix integration"]),
    ("ParaMagic / ParaSolver / acausal parametrics", [r"paramagic", r"parasolver", r"acausal"]),
    ("OpenMBEE / XMI / model distribution", [r"openmbee", r"\bxmi\b", r"zip"]),
    ("PLM / Teamcenter / Windchill / 3DExperience", [r"plm", r"teamcenter", r"windchill", r"3dexperience", r"enovia", r"step", r"cpm"]),
    ("Capella / Arcadia", [r"capella", r"arcadia"]),
    ("Papyrus / Eclipse", [r"papyrus", r"eclipse"]),
    ("Gaphor / UML stereotypes", [r"gaphor", r"uml stereotype"]),
    ("OPM / OPCloud / OPL", [r"object-process", r"\bopm\b", r"opcloud", r"\bopl\b"]),
    ("Dymola / Modelica", [r"dymola", r"modelica"]),
    ("Docs-as-code / M30ML / YAML", [r"docs-as-code", r"m30ml", r"yaml", r"github", r"liquid", r"jinja"]),
    ("System-as-Code / Python / JSON", [r"system-as-code", r"python", r"json", r"python4capella", r"custom api"]),
    ("Excel / spreadsheets", [r"excel", r"spreadsheet", r"calculation sheets"]),
    ("Formal methods / PVS", [r"formal methods", r"\bpvs\b", r"higher-order logic", r"category-theoretic"]),
    ("RML / RMM", [r"requirements modeling language", r"\brml\b", r"requirements mapping matrix", r"\brmm\b"]),
    ("OPAL / SAPPhIRE", [r"\bopal\b", r"sapphire", r"javafx"]),
    ("Nanospace / DSM / DMM / MB2DM", [r"nanospace", r"\bdsm\b", r"\bdmm\b", r"mb2dm"]),
    ("ForPlan / Julia / C2F", [r"forplan", r"julia", r"c2f", r"capellatoforplan", r"xtend"]),
    ("IDM-CIC / Simu-CIC / Opalis", [r"idm-cic", r"simu-cic", r"idm-power", r"opalis", r"flows manager"]),
    ("Valispace", [r"valispace"]),
]

VV_LINKAGE_RULES: List[Tuple[str, Sequence[str]]] = [
    ("Requirements linked through satisfy/verify/trace relations", [
        r"satisfy", r"verified by|verified-by", r"verify/verifies", r"trace", r"requirements? table", r"requirements? compliance", r"coverage"
    ]),
    ("Executable simulation linked to the model", [
        r"simulation|simulat", r"execut", r"time-step", r"forplan", r"dymola", r"modelcenter", r"cameo simulation", r"paramagic", r"stk", r"matlab"
    ]),
    ("Parametric, constraint, budget, or resource checks", [
        r"constraint", r"parametric", r"budget", r"margin", r"mass", r"power", r"energy", r"data capacity", r"state of charge", r"\bsoc\b", r"battery", r"solar", r"doe"
    ]),
    ("V&V packages, reviews, plans, or procedures", [
        r"validation and verification package", r"verification package", r"v&v", r"lifecycle reviews", r"verification activity", r"tester", r"plans?, procedures", r"review"
    ]),
    ("Test cases, automated tests, or RTM/RMM mapping", [
        r"test case", r"test-case", r"automated testing", r"requirements? traceability matrix", r"\brmm\b", r"defects", r"end-to-end test", r"test runs"
    ]),
    ("External analysis tool coupling or automatic feedback", [
        r"external", r"modelcenter", r"mbse analyzer", r"paramagic", r"dymola", r"catia", r"simulink", r"matlab", r"python client", r"outputs? are compared", r"updates?"
    ]),
    ("Power/EPS resource requirement or feasibility check", [
        r"energyLowerMargin", r"power subsystem", r"power view", r"battery", r"state of charge", r"\bsoc\b", r"solar", r"power demand", r"electric power", r"power profile", r"energy feasibility", r"stable power"
    ]),
]

VERIFICATION_KIND_RULES: List[Tuple[str, Sequence[str]]] = [
    ("Requirement traceability or compliance checking", [
        r"requirements?.*(trace|satisf|verif|compliance|coverage|checked)", r"verified by|verified-by", r"satisfy", r"requirements? table"
    ]),
    ("Simulation-based scenario/resource verification", [
        r"simulation|simulat", r"scenario", r"time-step", r"dymola", r"forplan", r"stk", r"modelcenter", r"cameo simulation", r"operational"
    ]),
    ("Parametric, budget, or margin verification", [
        r"parametric", r"constraint", r"budget", r"margin", r"mass", r"power", r"energy", r"data capacity", r"state of charge", r"\bsoc\b", r"battery", r"solar"
    ]),
    ("Test-case or automated-test verification", [
        r"test case", r"test-case", r"automated testing", r"end-to-end test", r"test runs", r"\brmm\b", r"defects"
    ]),
    ("Review, inspection, validation package, or procedure planning", [
        r"inspection", r"review", r"verification package", r"validation and verification approach", r"verification activity", r"plans?, procedures", r"method"
    ]),
    ("Model consistency or tool validation", [
        r"model validation", r"built-in model validation", r"manual inspection", r"magic model analyst", r"flow is thorough", r"consistency", r"interface conflict"
    ]),
]

LIMITATION_RULES: List[Tuple[str, Sequence[str]]] = [
    ("Prototype, incomplete maturity, or future work", [
        r"prototype", r"proof of concept", r"future work", r"in progress", r"still under development", r"still maturing", r"first version", r"not yet", r"to be defined", r"needs? updating", r"must be created", r"planned"
    ]),
    ("Limited scope, single case, or partial subsystem/mode coverage", [
        r"limited", r"only", r"subset", r"scope", r"not comprehensive", r"excludes", r"not discussed", r"nominal", r"non-nominal", r"single", r"focused", r"one viewpoint", r"case stud"
    ]),
    ("Tool dependency, interoperability, licensing, or learning curve", [
        r"license", r"tool", r"vendor", r"wrapper", r"interoperab", r"learning curve", r"familiar", r"misinterpreted", r"maintainability", r"api", r"proprietary", r"manual"
    ]),
    ("Generalizability or mission-specific tailoring constraints", [
        r"generaliz", r"tailor", r"mission-specific", r"customiz", r"envelope", r"other tools", r"other simulators", r"adapt"
    ]),
    ("No quantitative evaluation, weak validation, or no threats discussion", [
        r"no quantitative", r"not reported", r"no formal limitations", r"threats", r"no formal", r"no .*evaluation", r"not demonstrated", r"could not", r"no comparative"
    ]),
    ("Data, model-quality, source, or assumption limitation", [
        r"data", r"file", r"versions", r"no appropriate file", r"source", r"student", r"survey", r"assumptions", r"accuracy"
    ]),
    ("Organizational, adoption, or training constraint", [
        r"student", r"team", r"training", r"adoption", r"widespread", r"communication", r"self-learning", r"industry", r"university"
    ]),
]

GENERIC_NO_EPS_REASON_BY_ID = {
    "paper-0002": "behavior/use-case and functional decomposition of a generic CubeSat mission, not subsystem power design",
    "paper-0010": "formal/agile small-satellite design process and formal-methods V&V, not a subsystem model",
    "paper-0024": "MBSE--PLM information-flow analysis from conceptual to detailed design, not EPS architecture",
    "paper-0034": "requirements modeling language and automated-testing/traceability method, not a power subsystem model",
    "paper-0063": "nanosatellite system-modeling architecture with a communications-subsystem V&V demonstrator, not EPS",
    "paper-0068": "digital-engineering information-exchange/DSM--DMM mapping for mission architecture, not EPS",
    "paper-0071": "SysML risk-management model for a student nanosatellite, not EPS design or verification",
}

# --- utilities --------------------------------------------------------------------

def read_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_studies() -> List[dict]:
    studies = [read_json(p) for p in sorted(EXTRACTIONS_DIR.glob("paper-*.json"))]
    return sorted(studies, key=lambda d: (d.get("year", 9999), d.get("corpus_id", "")))


def has_any(text: str, patterns: Sequence[str]) -> bool:
    t = text.lower()
    return any(re.search(p, t, flags=re.I) for p in patterns)


def classify_text_items(items: Iterable[str], rules: Sequence[Tuple[str, Sequence[str]]], *, ignore_negative_outcomes: bool = False) -> Tuple[Set[str], Set[str]]:
    cats: Set[str] = set()
    absence: Set[str] = set()
    for item in items:
        text = item or ""
        neg = ignore_negative_outcomes and has_any(text, NEGATIVE_OUTCOME_PATTERNS)
        if neg:
            low = text.lower()
            if any(w in low for w in ["reliability", "reproducibility", "eps", "power"]):
                absence.add("No explicit reliability/reproducibility/EPS-specific outcome")
            else:
                absence.add("Outcome absence or non-demonstration noted")
            continue
        for cat, pats in rules:
            if has_any(text, pats):
                cats.add(cat)
    return cats, absence


def model_focus(study: dict) -> str:
    cats = set(study.get("modeling_scope_categories", []))
    has_system = "system-level" in cats
    has_eps = "EPS/power" in cats
    if has_system and has_eps:
        return "Whole nanosatellite with EPS/power as subsystem"
    if has_system and not has_eps:
        return "Whole nanosatellite/generic, no explicit EPS"
    if has_eps and not has_system:
        return "EPS-only or EPS-first model"
    return "Other / not classifiable"


def generic_no_eps_reason(study: dict) -> str:
    cid = study["corpus_id"]
    if cid in GENERIC_NO_EPS_REASON_BY_ID:
        return GENERIC_NO_EPS_REASON_BY_ID[cid]
    scope = study.get("modeling_scope", "")
    return textwrap.shorten(scope, 160, placeholder="...")


def exact_tools(study: dict) -> Set[str]:
    """Return named tools/methods that the extraction indicates were used.

    The free-text tool field sometimes says that a language/tool was mentioned
    only as background or an alternative.  This function therefore combines the
    structured tool categories with conservative keyword rules and skips common
    negated/background mentions.
    """
    text = study.get("mbse_language_method_tool", "") or ""
    low = text.lower()
    high_level = set(study.get("mbse_language_method_tool_categories", []))
    tools: Set[str] = set()

    # Structured categories are the most reliable signal for actual use.
    if "SysML" in high_level:
        tools.add("SysML")
    if "Cameo/MagicDraw" in high_level or has_any(text, [r"cameo", r"magicdraw", r"catia magic", r"no magic"]):
        tools.add("Cameo / MagicDraw / CATIA Magic")
    if "MATLAB/Simulink" in high_level or has_any(text, [r"matlab", r"simulink"]):
        tools.add("MATLAB / Simulink")
    if "PLM" in high_level or has_any(text, [r"plm", r"teamcenter", r"windchill", r"3dexperience", r"enovia", r"step", r"cpm"]):
        tools.add("PLM / Teamcenter / Windchill / 3DExperience")
    if "Capella/Arcadia" in high_level or (has_any(text, [r"capella", r"arcadia"]) and "mentioned as alternatives, not used" not in low):
        tools.add("Capella / Arcadia")
    if "OpenMBEE" in high_level or has_any(text, [r"openmbee", r"\bxmi\b"]):
        tools.add("OpenMBEE / XMI / model distribution")
    if "OOSEM" in high_level:
        tools.add("OOSEM")
    if "CPS" in high_level:
        tools.add("CPS abstraction")
    if "Docs-as-code" in high_level or has_any(text, [r"docs-as-code", r"m30ml", r"yaml", r"github", r"liquid", r"jinja"]):
        tools.add("Docs-as-code / M30ML / YAML")
    if "System-as-Code" in high_level or has_any(text, [r"system-as-code", r"python4capella", r"custom api"]):
        tools.add("System-as-Code / Python / JSON")

    # More specific named tools/methods from the tool field.  Skip background-only mentions.
    background_only = [
        "mentioned only as background", "mentioned only as related", "mentioned only for comparison",
        "mentioned as alternatives, not used", "mentioned as examples", "present work uses matlab instead",
        "discussed as an objective/future", "future work proposes",
    ]
    for name, pats in EXACT_TOOL_RULES:
        if name in {"SysML", "Cameo / MagicDraw / CATIA Magic", "MATLAB / Simulink", "PLM / Teamcenter / Windchill / 3DExperience", "Capella / Arcadia", "OpenMBEE / XMI / model distribution", "Docs-as-code / M30ML / YAML", "System-as-Code / Python / JSON"}:
            continue
        if has_any(text, pats):
            # Conservative skips for known background-only clauses in the standardized extractions.
            if name in {"OPM / OPCloud / OPL"} and "mentioned as alternatives, not used" in low:
                continue
            if name in {"ParaMagic / ParaSolver / acausal parametrics"} and any(p in low for p in ["mentioned as examples", "present work uses matlab instead"]):
                continue
            if name in {"STK / GMAT / DRAMA orbit tools"} and "discussed as an objective/future" in low:
                continue
            if name == "Valispace" and "planned valispace" in low:
                continue
            if name == "OPAL / SAPPhIRE" and "opalis" in low and not re.search(r"\bopal\b|sapphire|javafx", low):
                continue
            if any(p in low for p in background_only) and name in {"STK / GMAT / DRAMA orbit tools"}:
                continue
            tools.add(name)
    return tools


def classify_vv_linkage(study: dict) -> Set[str]:
    text = study.get("verification_validation_linkage", "") or ""
    cats: Set[str] = set()
    rq3 = study.get("rqs_addressed", {}).get("RQ3", "")
    low = text.lower()
    no_linkage = (
        rq3 == "no" or low.startswith("no ") or "not reported/none" in low or "does not link" in low
        or "no paper-specific" in low or "no spacecraft or eps verification" in low
    )
    general_only = (
        "general linkage only" in low or "general system-level linkage only" in low or "general model/tool" in low
        or "only informal" in low or ("defined as supporting" in low and "actual" in low)
    )
    if no_linkage:
        cats.add("No explicit model-linked V&V")
    if general_only:
        cats.add("General MBSE V&V statement only")
    for cat, pats in VV_LINKAGE_RULES:
        # Avoid classifying negated EPS phrases as positive EPS verification.
        if cat.startswith("Power/EPS") and has_any(text, [r"no explicit eps-specific", r"not eps", r"no eps-specific"]):
            continue
        if has_any(text, pats):
            cats.add(cat)
    return cats


def classify_verification_kind(study: dict) -> Set[str]:
    # Use the explicit V&V linkage field only.  Key findings often mention
    # power/budget/simulation as modeling scope, which would inflate counts for
    # verification actually performed or proposed.
    text = study.get("verification_validation_linkage", "") or ""
    cats: Set[str] = set()
    low = study.get("verification_validation_linkage", "").lower()
    if study.get("rqs_addressed", {}).get("RQ3") == "no" or "general linkage only" in low or low.startswith("no ") or "not reported/none" in low:
        cats.add("No concrete verification performed or only generic V&V claim")
    for cat, pats in VERIFICATION_KIND_RULES:
        if has_any(text, pats):
            cats.add(cat)
    return cats


def classify_contributions(study: dict) -> Set[str]:
    scope_cats = set(study.get("modeling_scope_categories", []))
    text = " ".join([
        study.get("title", ""), study.get("modeling_scope", ""), study.get("mbse_language_method_tool", ""),
        " ".join(study.get("key_findings", [])), " ".join(study.get("claimed_outcomes", []))
    ]).lower()
    cats: Set[str] = set()
    if "system-level" in scope_cats:
        cats.add("System-/mission-level nanosatellite model")
    if "EPS/power" in scope_cats or "budget" in scope_cats:
        cats.add("EPS, power, resource-budget, or electrical-architecture representation")
    if "reference model/template" in scope_cats or re.search(r"reference model|template|generic|standardized|library|baseline|starting point", text):
        cats.add("Reference model, template, or reusable architecture")
    if "requirements" in scope_cats or "verification" in scope_cats or re.search(r"requirement|verification|validation|test|traceability|satisfy|verify", text):
        cats.add("Requirements, traceability, V&V, or testing linkage")
    if "simulation" in scope_cats or re.search(r"simulation|executable|trade|analysis|scenario|parametric|monte carlo|sizing|forplan|modelcenter|operational", text):
        cats.add("Simulation, trade study, executable analysis, or sizing")
    if re.search(r"tool|integrat|parser|plm|repository|database|exchange|docs-as-code|system-as-code|gaphor|papyrus|opcloud|capella|cameo|magicdraw|matlab|interoper", text):
        cats.add("Toolchain, data integration, or interoperability")
    if "tool/process" in scope_cats or re.search(r"method|framework|approach|process|workflow|methodology|agile|concurrent", text):
        cats.add("Method, framework, process, or workflow")
    if re.search(r"case|application|demonstrat|rax|eirsat|sealion|borealis|3colstar|rvsat|nss-1|nanosatc|psat|delffi|mission", text):
        cats.add("Mission or case-study application")
    if "risk" in scope_cats or re.search(r"risk|technical measure|\bmoe\b|\bmop\b|\btpm\b", text):
        cats.add("Risk or technical-measurement model")
    return cats


def classify_limitations(study: dict) -> Set[str]:
    limits = study.get("limitations_gaps", []) or []
    joined = " ".join(limits).strip()
    cats: Set[str] = set()
    if not joined or joined.lower() in {"not discussed", "not discussed."} or any(l.strip().lower() == "not discussed" for l in limits):
        cats.add("No limitations discussed")
    for cat, pats in LIMITATION_RULES:
        if has_any(joined, pats):
            cats.add(cat)
    return cats


def rq_status_counts(studies: Sequence[dict]) -> Dict[str, Counter]:
    out = {rq: Counter() for rq in ["RQ1", "RQ2", "RQ3"]}
    for d in studies:
        for rq in out:
            out[rq][d.get("rqs_addressed", {}).get(rq, "unknown")] += 1
    return out


def counter_from_multilabel(studies: Sequence[dict], key: str) -> Counter:
    c = Counter()
    for d in studies:
        for x in d.get(key, []):
            c[x] += 1
    return c


def count_member_map(classified: Dict[str, Set[str]], all_categories: Iterable[str] | None = None) -> Tuple[Counter, Dict[str, List[str]]]:
    c = Counter()
    members: Dict[str, List[str]] = defaultdict(list)
    for cid, cats in classified.items():
        for cat in cats:
            c[cat] += 1
            members[cat].append(cid)
    if all_categories:
        for cat in all_categories:
            c.setdefault(cat, 0)
            members.setdefault(cat, [])
    return c, {k: sorted(v) for k, v in members.items()}


def tex_escape(s: object) -> str:
    if s is None:
        return ""
    s = str(s)
    repl = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
        "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in s)


def short_title(study: dict, n: int = 82) -> str:
    return textwrap.shorten(study.get("title", ""), width=n, placeholder="...")


def cite_label(study: dict) -> str:
    authors = study.get("authors", [])
    if not authors:
        lead = "Unknown"
    else:
        first = authors[0]
        lead = first.split()[-1] if isinstance(first, str) else str(first)
    return f"{study['corpus_id']} ({lead} et al., {study.get('year', '')})"


def parse_protocol() -> Tuple[List[str], List[str]]:
    text = (ROOT / "protocol.md").read_text(encoding="utf-8")
    rq_block = re.search(r"## Research questions\n(?P<body>.*?)(?:\n## |\Z)", text, flags=re.S)
    rqs: List[str] = []
    if rq_block:
        for line in rq_block.group("body").splitlines():
            m = re.match(r"\s*\d+\.\s*(.*)", line)
            if m:
                rqs.append(m.group(1).strip())
    field_block = re.search(r"## Extraction fields\n(?P<body>.*?)(?:\n## |\Z)", text, flags=re.S)
    fields: List[str] = []
    if field_block:
        for line in field_block.group("body").splitlines():
            m = re.match(r"\s*-\s*(.*)", line)
            if m:
                fields.append(m.group(1).strip())
    return rqs, fields


def regex_int(text: str, patterns: Sequence[str], default: int = 0) -> int:
    for pat in patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            return int(m.group(1))
    return default


def prisma_counts(extraction_index: dict) -> Dict[str, int]:
    search_log = (ROOT / "search-log.md").read_text(encoding="utf-8") if (ROOT / "search-log.md").exists() else ""
    screening = (ROOT / "screening.md").read_text(encoding="utf-8") if (ROOT / "screening.md").exists() else ""
    pdf_status = (ROOT / "pdf-status.md").read_text(encoding="utf-8") if (ROOT / "pdf-status.md").exists() else ""
    raw = regex_int(search_log, [r"Raw results counted into the updated merged set:\s*(\d+)", r"Raw results counted.*?:\s*(\d+)"])
    unique = regex_int(search_log, [r"Unique results:\s*(\d+)", r"Final merged candidate pool:\s*(\d+)"])
    dup = regex_int(search_log, [r"Duplicates removed:\s*(\d+)"])
    screened = regex_int(screening, [r"Primary candidates screened from merged source:\s*(\d+)"]) or unique
    kept = regex_int(screening, [r"Kept in current `corpus\.json`:\s*(\d+)", r"Kept in current .*?:\s*(\d+)"])
    rejected = regex_int(screening, [r"Rejected from primary merged-candidate screening:\s*(\d+)"])
    total_corpus = regex_int(pdf_status, [r"Total corpus entries:\s*(\d+)"]) or kept
    extracted = int(extraction_index.get("study_count", 0))
    missing = max(total_corpus - extracted, 0)
    if not rejected and screened and kept:
        rejected = screened - kept
    if not dup and raw and unique:
        dup = raw - unique
    return {
        "raw_records": raw,
        "duplicates_removed": dup,
        "unique_records": unique or screened,
        "screened": screened,
        "excluded": rejected,
        "reports_sought": total_corpus or kept,
        "reports_not_retrieved": missing,
        "reports_extracted": extracted,
        "included": extracted,
    }

# --- plotting ---------------------------------------------------------------------

plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi": 160,
})

COLORS = {
    "core": "#3B82F6",
    "supporting": "#93C5FD",
    "yes": "#22C55E",
    "partial": "#F59E0B",
    "no": "#EF4444",
    "unknown": "#9CA3AF",
    "bar": "#2563EB",
    "bar2": "#0F766E",
    "bar3": "#7C3AED",
    "gap": "#B45309",
}


def savefig(fig, name: str):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / f"{name}.png", bbox_inches="tight")
    plt.close(fig)


def barh_counter(counter: Counter, name: str, title: str, xlabel: str = "Studies", *, color: str = COLORS["bar"], max_items: int | None = None, min_count: int = 1):
    items = [(k, v) for k, v in counter.most_common() if v >= min_count]
    if max_items:
        items = items[:max_items]
    if not items:
        return
    labels, vals = zip(*items)
    h = max(3.0, 0.34 * len(items) + 1.2)
    fig, ax = plt.subplots(figsize=(8.0, h))
    y = np.arange(len(items))[::-1]
    vals_rev = list(vals)[::-1]
    labels_rev = [textwrap.fill(l, 44) for l in labels[::-1]]
    ax.barh(y, vals_rev, color=color)
    ax.set_yticks(y, labels_rev)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25)
    for yi, v in zip(y, vals_rev):
        ax.text(v + 0.2, yi, str(v), va="center", fontsize=9)
    ax.set_xlim(0, max(vals_rev) + 4)
    savefig(fig, name)


def plot_prisma(counts: Dict[str, int]):
    fig, ax = plt.subplots(figsize=(9, 8))
    ax.set_axis_off()
    boxes = [
        (0.5, 0.92, "Identification", f"Records identified\nRaw search/merge records: {counts['raw_records']}\nDuplicates removed: {counts['duplicates_removed']}", "#DBEAFE"),
        (0.5, 0.73, "Screening", f"Unique records screened: {counts['screened']}\nRecords excluded: {counts['excluded']}", "#E0F2FE"),
        (0.5, 0.54, "Retrieval", f"Reports sought for retrieval: {counts['reports_sought']}\nReports not retrieved / inaccessible: {counts['reports_not_retrieved']}", "#DCFCE7"),
        (0.5, 0.35, "Extraction", f"Accessible reports extracted: {counts['reports_extracted']}", "#FEF3C7"),
        (0.5, 0.18, "Included in findings", f"Studies in extraction synthesis: {counts['included']}", "#F3E8FF"),
    ]
    for x, y, header, body, color in boxes:
        w, h = 0.72, 0.12
        patch = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
                               linewidth=1.2, edgecolor="#334155", facecolor=color)
        ax.add_patch(patch)
        ax.text(x, y + 0.032, header, ha="center", va="center", weight="bold", fontsize=12)
        ax.text(x, y - 0.020, body, ha="center", va="center", fontsize=10)
    for i in range(len(boxes) - 1):
        _, y1, *_ = boxes[i]
        _, y2, *_ = boxes[i + 1]
        ax.add_patch(FancyArrowPatch((0.5, y1 - 0.075), (0.5, y2 + 0.075), arrowstyle="-|>", mutation_scale=14,
                                     linewidth=1.0, color="#334155"))
    ax.text(0.5, 0.04, "Counts regenerated from search-log.md, screening.md, pdf-status.md, and extraction.json.",
            ha="center", va="center", fontsize=9, color="#475569")
    savefig(fig, "prisma_flow")


def plot_year_tier(studies: Sequence[dict]):
    years = sorted({d["year"] for d in studies})
    tiers = ["core", "supporting"]
    vals = {tier: [sum(1 for d in studies if d["year"] == y and d.get("tier") == tier) for y in years] for tier in tiers}
    fig, ax = plt.subplots(figsize=(8.8, 3.8))
    bottom = np.zeros(len(years))
    for tier in tiers:
        ax.bar(years, vals[tier], bottom=bottom, label=tier.title(), color=COLORS[tier])
        bottom += np.array(vals[tier])
    ax.set_xticks(years)
    ax.set_ylabel("Extracted studies")
    ax.set_title("Extracted studies by year and tier")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    savefig(fig, "year_tier_counts")


def plot_rq_relevance(studies: Sequence[dict]):
    counts = rq_status_counts(studies)
    rqs = ["RQ1", "RQ2", "RQ3"]
    statuses = ["yes", "partial", "no"]
    x = np.arange(len(rqs))
    width = 0.22
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    for i, st in enumerate(statuses):
        vals = [counts[rq].get(st, 0) for rq in rqs]
        ax.bar(x + (i - 1) * width, vals, width, label=st.title(), color=COLORS[st])
        for xi, v in zip(x + (i - 1) * width, vals):
            if v:
                ax.text(xi, v + 0.5, str(v), ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x, rqs)
    ax.set_ylabel("Studies")
    ax.set_title("Extraction-coded relevance to protocol research questions")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_ylim(0, max(max(counts[rq].values()) for rq in rqs) + 5)
    savefig(fig, "rq_relevance_counts")


def plot_focus_counts(focus_by_id: Dict[str, str]):
    c = Counter(focus_by_id.values())
    barh_counter(c, "model_focus_counts", "Modeling focus derived from modeling_scope_categories", color=COLORS["bar2"])


def plot_study_focus_rq_matrix(studies: Sequence[dict], focus_by_id: Dict[str, str]):
    studies_sorted = sorted(studies, key=lambda d: (focus_by_id[d["corpus_id"]], d["year"], d["corpus_id"]))
    focus_labels = [
        "Whole+EPS", "Generic no EPS", "EPS-only", "RQ1", "RQ2", "RQ3"
    ]
    n = len(studies_sorted)
    matrix = np.zeros((n, len(focus_labels)))
    # Encodings: focus binary 1, RQ no=1, partial=2, yes=3, unknown=0
    for i, d in enumerate(studies_sorted):
        focus = focus_by_id[d["corpus_id"]]
        if focus.startswith("Whole nanosatellite with"):
            matrix[i, 0] = 1
        elif focus.startswith("Whole nanosatellite/generic"):
            matrix[i, 1] = 1
        elif focus.startswith("EPS-only"):
            matrix[i, 2] = 1
        for j, rq in enumerate(["RQ1", "RQ2", "RQ3"], start=3):
            st = d.get("rqs_addressed", {}).get(rq, "unknown")
            matrix[i, j] = {"no": 1, "partial": 2, "yes": 3}.get(st, 0)
    fig, ax = plt.subplots(figsize=(8.2, 11.5))
    # custom RGB image per cell
    rgb = np.ones((n, len(focus_labels), 3))
    status_colors = {
        0: np.array([0.95, 0.95, 0.95]),
        1: np.array([0.94, 0.27, 0.27]),  # no for RQ; focus binary overwritten below
        2: np.array([0.96, 0.62, 0.04]),
        3: np.array([0.13, 0.77, 0.37]),
    }
    for i in range(n):
        for j in range(len(focus_labels)):
            if j < 3:
                rgb[i, j] = np.array([0.20, 0.45, 0.85]) if matrix[i, j] else np.array([0.93, 0.93, 0.93])
            else:
                rgb[i, j] = status_colors[matrix[i, j]]
    ax.imshow(rgb, aspect="auto")
    ax.set_xticks(np.arange(len(focus_labels)), focus_labels, rotation=30, ha="right")
    ylabels = [f"{d['corpus_id']} ({d['year']})" for d in studies_sorted]
    ax.set_yticks(np.arange(n), ylabels, fontsize=7)
    ax.set_title("Study-level modeling focus and RQ relevance matrix")
    ax.set_xticks(np.arange(-.5, len(focus_labels), 1), minor=True)
    ax.set_yticks(np.arange(-.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.7)
    ax.tick_params(which="minor", bottom=False, left=False)
    # Legend as text to keep deterministic/compact
    ax.text(0.5, -0.075, "Focus columns: blue = membership. RQ columns: green = yes, amber = partial, red = no.",
            transform=ax.transAxes, ha="center", va="top", fontsize=9)
    savefig(fig, "study_focus_rq_matrix")


def plot_scope_tools(studies: Sequence[dict], exact_tool_by_id: Dict[str, Set[str]]):
    scope_counts = counter_from_multilabel(studies, "modeling_scope_categories")
    barh_counter(scope_counts, "modeling_scope_categories", "Modeling-scope categories recorded in extractions", color=COLORS["bar"])
    tool_cat_counts = counter_from_multilabel(studies, "mbse_language_method_tool_categories")
    # "Other" is retained in data but is visually uninformative; leave it in the CSV and out of the main chart.
    tool_cat_counts_for_plot = Counter({k: v for k, v in tool_cat_counts.items() if k != "Other"})
    barh_counter(tool_cat_counts_for_plot, "tool_category_counts", "High-level MBSE language/method/tool categories", color=COLORS["bar3"])
    exact_counts = Counter()
    for tools in exact_tool_by_id.values():
        for t in tools:
            exact_counts[t] += 1
    barh_counter(exact_counts, "exact_tool_counts", "Named tools/languages/methods detected deterministically", color="#0891B2", max_items=24)


def plot_quality(studies: Sequence[dict]):
    c = Counter(str(d.get("quality", {}).get("total_score", "unknown")) for d in studies)
    # Sort numeric-ish labels
    items = sorted(c.items(), key=lambda kv: float(kv[0]) if re.match(r"^\d+(\.\d+)?$", kv[0]) else 999)
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    labels, vals = zip(*items)
    ax.bar(labels, vals, color="#64748B")
    ax.set_xlabel("Quality score")
    ax.set_ylabel("Studies")
    ax.set_title("Quality checklist total scores")
    ax.grid(axis="y", alpha=0.25)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.3, str(v), ha="center")
    savefig(fig, "quality_score_counts")

# --- outputs ----------------------------------------------------------------------

def write_csvs(studies: Sequence[dict], derived: Dict[str, dict], counts: Dict[str, Counter], members: Dict[str, Dict[str, List[str]]]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "studies.csv", "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "corpus_id", "tier", "year", "title", "focus", "RQ1", "RQ2", "RQ3", "quality_total_score",
            "modeling_scope_categories", "tool_categories", "exact_tools", "outcome_categories", "outcome_gap_categories",
            "vv_linkage_categories", "verification_kind_categories", "contribution_categories", "limitation_categories",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for d in studies:
            cid = d["corpus_id"]
            der = derived[cid]
            w.writerow({
                "corpus_id": cid,
                "tier": d.get("tier", ""),
                "year": d.get("year", ""),
                "title": d.get("title", ""),
                "focus": der["focus"],
                "RQ1": d.get("rqs_addressed", {}).get("RQ1", ""),
                "RQ2": d.get("rqs_addressed", {}).get("RQ2", ""),
                "RQ3": d.get("rqs_addressed", {}).get("RQ3", ""),
                "quality_total_score": d.get("quality", {}).get("total_score", ""),
                "modeling_scope_categories": "; ".join(d.get("modeling_scope_categories", [])),
                "tool_categories": "; ".join(d.get("mbse_language_method_tool_categories", [])),
                "exact_tools": "; ".join(sorted(der["exact_tools"])),
                "outcome_categories": "; ".join(sorted(der["outcome_categories"])),
                "outcome_gap_categories": "; ".join(sorted(der["outcome_gap_categories"])),
                "vv_linkage_categories": "; ".join(sorted(der["vv_linkage_categories"])),
                "verification_kind_categories": "; ".join(sorted(der["verification_kind_categories"])),
                "contribution_categories": "; ".join(sorted(der["contribution_categories"])),
                "limitation_categories": "; ".join(sorted(der["limitation_categories"])),
            })
    # Category counts and members
    with open(DATA_DIR / "category_counts.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["family", "category", "count", "members"])
        for family, counter in counts.items():
            for cat, val in counter.most_common():
                w.writerow([family, cat, val, "; ".join(members.get(family, {}).get(cat, []))])
    with open(DATA_DIR / "study_classifications.json", "w", encoding="utf-8") as f:
        serializable = {cid: {k: sorted(v) if isinstance(v, set) else v for k, v in der.items()} for cid, der in derived.items()}
        json.dump(serializable, f, indent=2, ensure_ascii=False)


def latex_table_category_members(family_title: str, counter: Counter, members: Dict[str, List[str]], max_rows: int | None = None) -> str:
    rows = []
    items = counter.most_common()
    if max_rows:
        items = items[:max_rows]
    rows.append(r"\begin{longtable}{p{0.48\linewidth}r p{0.34\linewidth}}")
    rows.append(r"\toprule")
    rows.append(r"Category & n & Study IDs \\")
    rows.append(r"\midrule")
    rows.append(r"\endfirsthead")
    rows.append(r"\toprule Category & n & Study IDs \\ \midrule \endhead")
    for cat, val in items:
        ids = ", ".join(members.get(cat, []))
        rows.append(f"{tex_escape(cat)} & {val} & {tex_escape(ids)} " + r"\\")
    rows.append(r"\bottomrule")
    rows.append(r"\end{longtable}")
    return "\n".join(rows)


def latex_study_focus_table(studies: Sequence[dict], derived: Dict[str, dict]) -> str:
    groups = defaultdict(list)
    for d in studies:
        groups[derived[d["corpus_id"]]["focus"]].append(d)
    order = [
        "Whole nanosatellite with EPS/power as subsystem",
        "Whole nanosatellite/generic, no explicit EPS",
        "EPS-only or EPS-first model",
        "Other / not classifiable",
    ]
    rows = []
    rows.append(r"\begin{longtable}{p{0.27\linewidth}p{0.10\linewidth}p{0.55\linewidth}}")
    rows.append(r"\toprule Focus & Count & Studies \\")
    rows.append(r"\midrule\endfirsthead")
    rows.append(r"\toprule Focus & Count & Studies \\ \midrule\endhead")
    for focus in order:
        ds = sorted(groups.get(focus, []), key=lambda d: (d.get("year", 0), d["corpus_id"]))
        if not ds:
            continue
        labels = "; ".join(f"{d['corpus_id']} ({d.get('year', '')})" for d in ds)
        rows.append(f"{tex_escape(focus)} & {len(ds)} & {tex_escape(labels)} " + r"\\")
    rows.append(r"\bottomrule\end{longtable}")
    return "\n".join(rows)


def latex_generic_no_eps_table(studies: Sequence[dict], derived: Dict[str, dict]) -> str:
    rows = []
    rows.append(r"\begin{longtable}{p{0.14\linewidth}p{0.30\linewidth}p{0.46\linewidth}}")
    rows.append(r"\caption{Why generic system-level studies were not counted as explicit EPS modeling.}\label{tab:generic-no-eps}\\")
    rows.append(r"\toprule Study & Short title & Why it is generic/no-EPS \\")
    rows.append(r"\midrule\endfirsthead")
    rows.append(r"\toprule Study & Short title & Why it is generic/no-EPS \\ \midrule\endhead")
    for d in studies:
        if derived[d["corpus_id"]]["focus"] == "Whole nanosatellite/generic, no explicit EPS":
            rows.append(f"{tex_escape(d['corpus_id'])} & {tex_escape(short_title(d, 65))} & {tex_escape(generic_no_eps_reason(d))} " + r"\\")
    rows.append(r"\bottomrule\end{longtable}")
    return "\n".join(rows)


def latex_study_contribution_limit_table(studies: Sequence[dict], derived: Dict[str, dict]) -> str:
    rows = []
    rows.append(r"\begin{landscape}")
    rows.append(r"\scriptsize")
    rows.append(r"\begin{longtable}{p{0.08\linewidth}p{0.20\linewidth}p{0.31\linewidth}p{0.31\linewidth}}")
    rows.append(r"\toprule Study & Short title & Contribution categories & Limitation categories \\")
    rows.append(r"\midrule\endfirsthead")
    rows.append(r"\toprule Study & Short title & Contribution categories & Limitation categories \\ \midrule\endhead")
    for d in studies:
        cid = d["corpus_id"]
        contrib = "; ".join(sorted(derived[cid]["contribution_categories"]))
        limits = "; ".join(sorted(derived[cid]["limitation_categories"]))
        rows.append(f"{tex_escape(cid)} & {tex_escape(short_title(d, 58))} & {tex_escape(contrib)} & {tex_escape(limits)} " + r"\\")
    rows.append(r"\bottomrule\end{longtable}")
    rows.append(r"\end{landscape}")
    return "\n".join(rows)


def latex_report(studies: Sequence[dict], extraction_index: dict, prisma: Dict[str, int], derived: Dict[str, dict], counters: Dict[str, Counter], members: Dict[str, Dict[str, List[str]]]) -> str:
    rqs, extraction_fields = parse_protocol()
    n = len(studies)
    tier_counts = Counter(d.get("tier", "") for d in studies)
    focus_counts = Counter(derived[d["corpus_id"]]["focus"] for d in studies)
    rq_counts = rq_status_counts(studies)
    years = [d["year"] for d in studies]
    direct_eps_ids = [d["corpus_id"] for d in studies if derived[d["corpus_id"]]["focus"] == "EPS-only or EPS-first model"]
    generic_no_eps_ids = [d["corpus_id"] for d in studies if derived[d["corpus_id"]]["focus"] == "Whole nanosatellite/generic, no explicit EPS"]

    rqs_tex = "\n".join(f"\
\\item RQ{i+1}. {tex_escape(rq)}" for i, rq in enumerate(rqs))
    fields_tex = ", ".join(tex_escape(f) for f in extraction_fields)

    top_outcomes = ", ".join(f"{tex_escape(cat)} ({cnt})" for cat, cnt in counters["outcomes"].most_common(5))
    top_vv = ", ".join(f"{tex_escape(cat)} ({cnt})" for cat, cnt in counters["vv_linkage"].most_common(5))
    top_contrib = ", ".join(f"{tex_escape(cat)} ({cnt})" for cat, cnt in counters["contributions"].most_common(5))
    top_limits = ", ".join(f"{tex_escape(cat)} ({cnt})" for cat, cnt in counters["limitations"].most_common(5))

    return rf"""
\documentclass[11pt]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{hyperref}}
\usepackage{{pdflscape}}
\usepackage{{enumitem}}
\usepackage{{caption}}
\graphicspath{{{{figures/}}}}
\hypersetup{{colorlinks=true,linkcolor=blue,urlcolor=blue}}
\setlength{{\LTpre}}{{0.35em}}
\setlength{{\LTpost}}{{0.5em}}
\title{{SLR 1: Questions 1--3}}
\author{{}}
\date{{}}

\begin{{document}}
\maketitle

\section{{Protocol basis and scope of this report}}
The protocol research questions are:
\begin{{enumerate}}[leftmargin=*]
{rqs_tex}
\end{{enumerate}}

The protocol extraction fields used as the organizing frame are: {fields_tex}.  The corpus summarized here contains {n} accessible extracted studies ({tier_counts.get('core',0)} core and {tier_counts.get('supporting',0)} supporting), from {min(years)}--{max(years)}.  The four inaccessible kept corpus records listed in \texttt{{pdf-status.md}} are not included in the extraction synthesis.

\section{{Search, screening, retrieval, and extraction flow}}
Figure~\ref{{fig:prisma}} gives the PRISMA-style flow reconstructed from the maintained search, screening, retrieval, and extraction artifacts.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.88\linewidth]{{prisma_flow.pdf}}
\caption{{PRISMA-style flow for SLR1 extraction synthesis.}}
\label{{fig:prisma}}
\end{{figure}}

The regenerated flow is: {prisma['raw_records']} raw merged search records, {prisma['duplicates_removed']} duplicates removed, {prisma['screened']} unique records screened, {prisma['excluded']} excluded during screening, {prisma['reports_sought']} reports sought for retrieval, {prisma['reports_not_retrieved']} not retrieved/inaccessible, and {prisma['reports_extracted']} extracted.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.95\linewidth]{{year_tier_counts.pdf}}
\caption{{Extracted studies by publication year and screening tier.}}
\end{{figure}}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.72\linewidth]{{quality_score_counts.pdf}}
\caption{{Quality checklist total scores recorded during extraction.}}
\end{{figure}}

\section{{RQ relevance and modeling focus}}
Figure~\ref{{fig:rq-counts}} summarizes the extraction-coded relevance to each protocol RQ.  The key pattern is that RQ2 is coded as partial for all extracted studies, reflecting that claimed outcomes are usually MBSE/process claims rather than direct measured EPS reliability, reproducibility, or integrability outcomes.  RQ3 has the smallest ``yes'' subset.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.78\linewidth]{{rq_relevance_counts.pdf}}
\caption{{Extraction-coded relevance to each protocol research question.}}
\label{{fig:rq-counts}}
\end{{figure}}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.82\linewidth]{{model_focus_counts.pdf}}
\caption{{Modeling focus derived deterministically from \texttt{{modeling\_scope\_categories}}.}}
\label{{fig:focus-counts}}
\end{{figure}}

The focus categories answer the user's requested distinctions directly from extraction categories:
\begin{{itemize}}[leftmargin=*]
\item Whole nanosatellite with EPS/power as a subsystem: {focus_counts.get('Whole nanosatellite with EPS/power as subsystem',0)} studies.
\item Whole nanosatellite/generic with no explicit EPS: {focus_counts.get('Whole nanosatellite/generic, no explicit EPS',0)} studies ({tex_escape(', '.join(generic_no_eps_ids))}).
\item EPS-only or EPS-first model: {focus_counts.get('EPS-only or EPS-first model',0)} study ({tex_escape(', '.join(direct_eps_ids) if direct_eps_ids else 'none')}).
\end{{itemize}}

\begin{{figure}}[p]
\centering
\includegraphics[width=0.82\linewidth]{{study_focus_rq_matrix.pdf}}
\caption{{Study-level matrix showing modeling focus membership and RQ relevance.}}
\label{{fig:study-matrix}}
\end{{figure}}

\subsection{{Which studies fall in each modeling-focus group}}
{latex_study_focus_table(studies, derived)}

\subsection{{Generic whole-nanosatellite studies that do not model EPS explicitly}}
Table~\ref{{tab:generic-no-eps}} lists the generic/no-EPS studies and the extraction-based reason each is not counted as EPS modeling.
{latex_generic_no_eps_table(studies, derived)}

\section{{Categories arising in extraction fields}}
\subsection{{Modeling-scope categories}}
\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.90\linewidth]{{modeling_scope_categories.pdf}}
\caption{{Multi-label modeling-scope categories recorded in the standardized extractions.}}
\end{{figure}}

{latex_table_category_members('Modeling scope', counter_from_multilabel(studies, 'modeling_scope_categories'), members['scope'])}

\subsection{{MBSE languages, methods, and tools}}
The high-level extraction categories show SysML dominance but also a long tail of methods and toolchains.  ``Other'' is present in all extraction files and is omitted from the main high-level tool figure; it remains in \texttt{{report/data/category\_counts.csv}}.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.78\linewidth]{{tool_category_counts.pdf}}
\caption{{High-level MBSE language/method/tool categories, excluding the uninformative ``Other'' category.}}
\end{{figure}}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{{exact_tool_counts.pdf}}
\caption{{Named tools/languages/methods detected from \texttt{{mbse\_language\_method\_tool}} using deterministic keyword rules.}}
\end{{figure}}

{latex_table_category_members('Exact tools', counters['exact_tools'], members['exact_tools'])}

\subsection{{Claimed outcomes}}
Outcome categories are extracted from the \texttt{{claimed\_outcomes}} lists using deterministic keyword rules and with negated/absence statements separated.  The most frequent positive outcome categories are: {top_outcomes}.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{{outcome_categories.pdf}}
\caption{{Positive claimed-outcome categories detected in the extraction field.}}
\end{{figure}}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.72\linewidth]{{outcome_gap_categories.pdf}}
\caption{{Outcome absence/gap categories explicitly noted in extraction bullets.}}
\end{{figure}}

{latex_table_category_members('Claimed outcomes', counters['outcomes'], members['outcomes'])}

\subsection{{How verification/validation was linked to models}}
The most common verification-linkage categories are: {top_vv}.  These are multi-label categories; for example, a study can have requirements traceability, parametric checks, and external tool coupling at the same time.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{{vv_linkage_categories.pdf}}
\caption{{How verification/validation was linked to the model in the extractions.}}
\end{{figure}}

{latex_table_category_members('V&V linkage', counters['vv_linkage'], members['vv_linkage'])}

\subsection{{Kinds of verification performed or proposed}}
\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{{verification_kind_categories.pdf}}
\caption{{Kinds of verification performed or proposed, derived from V\&V linkage and key-finding fields.}}
\end{{figure}}

{latex_table_category_members('Verification kinds', counters['verification_kinds'], members['verification_kinds'])}

\section{{Contributions and limitations}}
The contribution taxonomy shows what each paper primarily added to the corpus.  The most frequent contribution categories are: {top_contrib}.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{{contribution_categories.pdf}}
\caption{{Contribution categories derived from key findings, modeling scope, and tool/method fields.}}
\end{{figure}}

{latex_table_category_members('Contributions', counters['contributions'], members['contributions'])}

Limitations are also multi-label.  The most frequent limitation categories are: {top_limits}.  Several studies do not provide formal limitations/threats-to-validity discussions; those are explicitly separated rather than silently ignored.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{{limitation_categories.pdf}}
\caption{{Limitation/gap categories derived from the standardized limitation fields.}}
\end{{figure}}

{latex_table_category_members('Limitations', counters['limitations'], members['limitations'])}

\clearpage
\section{{Study-level contribution and limitation map}}
The following landscape table supports paper-by-paper inspection of what each extraction contributed and what limitations/gaps were recorded.

{latex_study_contribution_limit_table(studies, derived)}

\section{{Generated artifacts and reproducibility}}
This report is regenerated by running:
\begin{{verbatim}}
python3 SLR/SLR1/scripts/generate_extraction_report.py
\end{{verbatim}}
The script writes the figures under \texttt{{SLR/SLR1/report/figures/}}, tabular derived data under \texttt{{SLR/SLR1/report/data/}}, and this LaTeX file at \texttt{{SLR/SLR1/report/extraction\_findings.tex}}.  The deterministic category rules are persisted in the script.

\end{{document}}
""".lstrip()


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    studies = load_studies()
    extraction_index = read_json(ROOT / "extraction.json")
    prisma = prisma_counts(extraction_index)

    derived: Dict[str, dict] = {}
    for d in studies:
        cid = d["corpus_id"]
        outcome_cats, outcome_gaps = classify_text_items(d.get("claimed_outcomes", []), OUTCOME_RULES, ignore_negative_outcomes=True)
        derived[cid] = {
            "focus": model_focus(d),
            "exact_tools": exact_tools(d),
            "outcome_categories": outcome_cats,
            "outcome_gap_categories": outcome_gaps,
            "vv_linkage_categories": classify_vv_linkage(d),
            "verification_kind_categories": classify_verification_kind(d),
            "contribution_categories": classify_contributions(d),
            "limitation_categories": classify_limitations(d),
        }

    # Member/counter maps for multi-label derived categories.
    counters: Dict[str, Counter] = {}
    members: Dict[str, Dict[str, List[str]]] = {}
    derived_keys = {
        "exact_tools": "exact_tools",
        "outcomes": "outcome_categories",
        "outcome_gaps": "outcome_gap_categories",
        "vv_linkage": "vv_linkage_categories",
        "verification_kinds": "verification_kind_categories",
        "contributions": "contribution_categories",
        "limitations": "limitation_categories",
    }
    for family, key in derived_keys.items():
        classified = {cid: der[key] for cid, der in derived.items()}
        counters[family], members[family] = count_member_map(classified)

    # Source category member maps.
    scope_classified = {d["corpus_id"]: set(d.get("modeling_scope_categories", [])) for d in studies}
    counters["scope"], members["scope"] = count_member_map(scope_classified)
    tool_classified = {d["corpus_id"]: set(d.get("mbse_language_method_tool_categories", [])) for d in studies}
    counters["tool_categories"], members["tool_categories"] = count_member_map(tool_classified)

    # Figures.
    plot_prisma(prisma)
    plot_year_tier(studies)
    plot_quality(studies)
    plot_rq_relevance(studies)
    focus_by_id = {cid: der["focus"] for cid, der in derived.items()}
    plot_focus_counts(focus_by_id)
    plot_study_focus_rq_matrix(studies, focus_by_id)
    plot_scope_tools(studies, {cid: der["exact_tools"] for cid, der in derived.items()})
    barh_counter(counters["outcomes"], "outcome_categories", "Claimed outcomes: deterministic categories", color="#16A34A")
    barh_counter(counters["outcome_gaps"], "outcome_gap_categories", "Outcome absence/gap statements noted", color=COLORS["gap"])
    barh_counter(counters["vv_linkage"], "vv_linkage_categories", "Verification/validation linkage categories", color="#DC2626")
    barh_counter(counters["verification_kinds"], "verification_kind_categories", "Kinds of verification performed or proposed", color="#EA580C")
    barh_counter(counters["contributions"], "contribution_categories", "Contribution categories", color="#7C3AED")
    barh_counter(counters["limitations"], "limitation_categories", "Limitation/gap categories", color="#475569")

    # Data files and LaTeX.
    write_csvs(studies, derived, counters, members)
    tex = latex_report(studies, extraction_index, prisma, derived, counters, members)
    (REPORT_DIR / "extraction_findings.tex").write_text(tex, encoding="utf-8")

    readme = f"""# SLR1 extraction findings report\n\nGenerated artifacts for the extraction findings report.\n\nRegenerate everything from the maintained protocol/extraction data with:\n\n```bash\npython3 ../scripts/generate_extraction_report.py\n```\n\nFrom this directory, compile the PDF with:\n\n```bash\npdflatex extraction_findings.tex\npdflatex extraction_findings.tex\n```\n\nThe generator uses deterministic numeric, categorical, and keyword-based rules.\n\nKey outputs:\n- `extraction_findings.tex` -- LaTeX report\n- `figures/` -- regenerated charts as PDF and PNG\n- `data/studies.csv` -- study-level derived classifications\n- `data/category_counts.csv` -- category counts and members\n- `data/study_classifications.json` -- JSON audit trail for derived categories\n"""
    (REPORT_DIR / "README.md").write_text(readme, encoding="utf-8")
    makefile = """report:\n\tpython3 ../scripts/generate_extraction_report.py\n\tpdflatex extraction_findings.tex\n\tpdflatex extraction_findings.tex\n\npdf: report\n\nclean:\n\trm -f *.aux *.log *.out *.toc *.lof *.lot extraction_findings.pdf\n\n.PHONY: report pdf clean\n"""
    (REPORT_DIR / "Makefile").write_text(makefile, encoding="utf-8")
    print(f"Wrote {REPORT_DIR / 'extraction_findings.tex'}")
    print(f"Wrote figures to {FIG_DIR}")
    print(f"Wrote data to {DATA_DIR}")


if __name__ == "__main__":
    main()
