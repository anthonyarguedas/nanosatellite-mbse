#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Static regression checks for the current source-plan translations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


FAMILIES = ("S", "WS", "I", "C", "W", "SN", "PQ", "ARC")
SUFFIXES = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2", "V1", "O1")
MODEL_VARIANTS = (
    '"system modeling"', '"systems modeling"', '"system modelling"', '"systems modelling"'
)
BROAD_MODEL_TERMS = (
    '"system model"', '"systems model"', '"system modeling"', '"systems modeling"',
    '"system modelling"', '"systems modelling"', '"reference model"',
    '"digital engineering"', '"object-oriented systems model"',
)
HIGH_E_TERMS = (
    '"electrical power system"', '"electric power system"',
    '"electrical power subsystem"', '"electric power subsystem"',
    '"power subsystem"', '"electrical architecture"', '"power architecture"',
    "PCDU", "PMAD", "EPS",
)
V1_FINITE_TERMS = (
    "verification", "validation", "traceability", "traceable",
    '"model verification"', '"model validation"', '"system verification"',
    '"system validation"', '"model checking"', '"virtual integration"',
    '"requirements-in-the-loop"', "MIL", '"model-in-the-loop"', "SIL",
    '"software-in-the-loop"', "PIL", '"processor-in-the-loop"', "HIL",
    '"hardware-in-the-loop"', '"test case"', '"test procedure"',
)
O1_FINITE_TERMS = (
    "reliability", "reliable", '"mission assurance"', "reproducibility",
    "reproducible", "reuse", "reusable", "integrability", "integrable",
    "interoperability", "interoperable", "traceability", "traceable",
    "benefit", "benefits", "impact", "outcome", '"no effect"', "adverse",
    "burden", "effort", "workload", "overhead", "cost", "schedule",
    "training", '"learning curve"', "licensing", "license", "licence", "adoption",
)
NTRS_C1_BASE_ATOMS = (
    '"reference model"', '"system reference model"', '"model library"', '"model libraries"',
    '"system model library"', '"system model libraries"', '"model pattern"',
    '"modeling pattern"', '"modelling pattern"', '"system model pattern"',
    '"systems model pattern"', '"model profile"', '"system model profile"',
    '"systems model profile"', '"SysML profile"',
)
IEEE_T2_FINITE_TERMS = (
    "reuse", "reuses", "reused", "reusable", "reusing",
    "tailor", "tailors", "tailored", "tailoring",
    "customize", "customizes", "customized", "customizing", "customization",
    "customise", "customises", "customised", "customising", "customisation",
    "configure", "configures", "configured", "configuring", "configuration",
    "parameterize", "parameterizes", "parameterized", "parameterizing", "parameterization",
    "parameterise", "parameterises", "parameterised", "parameterising", "parameterisation",
    "instantiate", "instantiates", "instantiated", "instantiating", "instantiation",
    "variability", '"variation point"',
    "specialize", "specializes", "specialized", "specializing", "specialization",
    "specialise", "specialises", "specialised", "specialising", "specialisation",
    "adapt", "adapts", "adapted", "adapting", "adaptation",
)
SCRIPT_DIR = Path("/Users/antho/agent-tools/academic-research/skills/academic-search/scripts")
PERMITTED_SOURCE_SCRIPTS = {
    "search_aiaa_arc.py", "search_compendex.py", "search_esa_indico.py",
    "search_iaf_digital_library.py", "search_ieee_xplore.py", "search_ntrs.py",
    "search_proquest_aerospace.py", "search_scopus.py", "search_springer_link.py",
    "search_wiley_online_library.py",
}
FORBIDDEN_SOURCE_SCRIPTS = {
    "search_arxiv.py", "search_google_scholar.py", "search_semantic_scholar.py",
}


def extract(markdown: str, query_id: str) -> str:
    match = re.search(
        rf"^### {re.escape(query_id)}(?:\s+[^\n]*)?\n\n```text\n(.*?)\n```",
        markdown,
        re.M | re.S,
    )
    if not match:
        raise ValueError(f"missing query block {query_id}")
    return match.group(1).strip()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def token_present(query: str, token: str) -> bool:
    if token.startswith('"'):
        return token in query
    return bool(re.search(rf"(?<![A-Za-z0-9_*]){re.escape(token)}(?![A-Za-z0-9_*])", query))


def balanced(query: str) -> bool:
    level = 0
    quoted = False
    for character in query:
        if character == '"':
            quoted = not quoted
        elif not quoted and character == "(":
            level += 1
        elif not quoted and character == ")":
            level -= 1
        if level < 0:
            return False
    return level == 0 and not quoted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--dictionary", required=True, type=Path)
    args = parser.parse_args()

    plan = args.plan.read_text(encoding="utf-8")
    dictionary = json.loads(args.dictionary.read_text(encoding="utf-8"))
    protocol_path = args.plan.with_name("protocol.md")
    protocol = protocol_path.read_text(encoding="utf-8") if protocol_path.is_file() else ""
    failures: list[str] = []

    require(bool(protocol), "protocol.md is missing beside the query plan", failures)
    require("**Protocol version:** `1.5` (frozen)" in protocol, "protocol is not frozen as version 1.5", failures)
    require("| `1.4` to `1.5` |" in protocol, "protocol lacks the version-1.5 amendment record", failures)
    require(
        "twelve databases/collections searched through eleven interfaces" in protocol,
        "protocol lacks the version-1.5 source-count contract",
        failures,
    )
    require(
        "IAF Digital Library" in protocol and "Version 1.5" in protocol,
        "protocol does not authorize IAF under version 1.5",
        failures,
    )
    require("2026-08-10" in protocol and "common" in protocol, "protocol lacks the common cutoff", failures)

    queries = {
        f"{family}-{suffix}": extract(plan, f"{family}-{suffix}")
        for family in FAMILIES
        for suffix in SUFFIXES
    }

    for query_id, query in queries.items():
        require('"nano satellites"' in query, f"{query_id} lacks spaced plural nano satellites", failures)
        require(balanced(query), f"{query_id} has unbalanced parentheses/quotes", failures)

    for query_id, query in queries.items():
        if query_id.startswith(("I-", "ARC-")):
            require(token_present(query, "nanosat"), f"{query_id} lacks standalone nanosat", failures)

    for family in FAMILIES:
        for suffix in ("A2", "B2"):
            query_id = f"{family}-{suffix}"
            query = queries[query_id]
            for phrase in MODEL_VARIANTS:
                require(phrase in query, f"{query_id} lacks {phrase}", failures)
            require('"object-oriented systems model"' in query, f"{query_id} lacks object-oriented systems model", failures)
        for phrase in ('"power mode"', '"power modes"'):
            require(phrase in queries[f"{family}-A2"], f"{family}-A2 lacks {phrase}", failures)

        a3 = queries[f"{family}-A3"]
        for token in HIGH_E_TERMS:
            require(token_present(a3, token), f"{family}-A3 lacks high-E term {token}", failures)
        for token in BROAD_MODEL_TERMS:
            require(token in a3, f"{family}-A3 lacks broad-model term {token}", failures)
        for relation in ("requirement", "function", "traceab", "verification", "validation"):
            require(relation not in a3.casefold(), f"{family}-A3 incorrectly includes relation gate {relation}", failures)

        for suffix, required in {
            "BG1": ('"generic model"', '"model template"'),
            "BG2": ('"reference architecture"', '"variation point"'),
            "BC1": ('"model library"', '"domain-specific modeling language"'),
            "BT2": ('"system model"', "reuses"),
        }.items():
            query_id = f"{family}-{suffix}"
            query = queries[query_id]
            for token in required:
                require(token_present(query, token), f"{query_id} lacks {token}", failures)
        if family != "I":
            require("tailor*" in queries[f"{family}-BT2"], f"{family}-BT2 lacks tailoring wildcard", failures)
        for suffix in ("BG1", "BG2", "BC1"):
            query_id = f"{family}-{suffix}"
            query = queries[query_id]
            require("verification" not in query.casefold(), f"{query_id} is not relation-free", failures)
            require("validation" not in query.casefold(), f"{query_id} is not relation-free", failures)

        for token in V1_FINITE_TERMS:
            require(token_present(queries[f"{family}-V1"], token), f"{family}-V1 lacks finite term {token}", failures)
        for token in O1_FINITE_TERMS:
            require(token_present(queries[f"{family}-O1"], token), f"{family}-O1 lacks finite term {token}", failures)
        for wildcard in ("traceab*", "reliab*", "reproduc*", "integrab*", "interoperab*", "benefit*", "licen*"):
            require(wildcard not in queries[f"{family}-V1"], f"{family}-V1 retains wildcard {wildcard}", failures)
            require(wildcard not in queries[f"{family}-O1"], f"{family}-O1 retains wildcard {wildcard}", failures)

    for token in IEEE_T2_FINITE_TERMS:
        require(token_present(queries["I-BT2"], token), f"I-BT2 lacks finite inflection {token}", failures)

    ieee_relation = "(requirement OR requirements OR function OR functions OR behavior OR behaviors OR behaviour OR behaviours OR architecture OR architectures OR interface OR interfaces OR traceability OR parametric OR parametrics OR verification OR validation)"
    require(ieee_relation in queries["I-B2"], "I-B2 relation block differs from explicit frozen inflections", failures)

    for required_plan_control in (
        "version `1.5`", "twelve-database/collection, eleven-interface", "A1 ∪ A2 ∪ A3",
        "## 14. IAF Digital Library authorized", "2026-08-10", "**940 cells**",
        "**180 N-B-core cells**", "**250 N-BG cells**", "**510 N-BC1 cells**",
        "**280 unpiloted C1 cells**", "pilots-to-run-v1.5.md",
    ):
        require(required_plan_control in plan, f"version-1.5 plan lacks {required_plan_control}", failures)

    for required_arc_control in (
        "field1=AllField", "access=on", "BeforeMonth=8", "pageSize=20",
        "Tools → Download citation", "/action/downloadCitation", "include=abs", "--require-complete",
    ):
        require(required_arc_control in plan, f"ARC execution contract lacks {required_arc_control}", failures)

    for query_id, query in queries.items():
        if query_id.startswith("S-"):
            require("DOCTYPE(" not in query, f"{query_id} retains Scopus DOCTYPE filter", failures)
    require("Select **no Document Type restriction**" in plan, "WoS no-type control is not explicit", failures)
    require("Do not add a `ContentType` refinement" in plan, "IEEE no-type control is not explicit", failures)

    p_n_match = re.search(r"^- `P_N = \{(.*?)\}`;", plan, re.M)
    require(p_n_match is not None, "NTRS P_N set is missing", failures)
    if p_n_match:
        for term in (
            "CubeSat", "CubeSats", '"cube sat"', "nanosat", "nanosatellite", "nanosatellites",
            '"nano-satellite"', '"nano-satellites"', '"nano satellite"', '"nano satellites"',
        ):
            require(term in p_n_match.group(1), f"NTRS P_N lacks {term}", failures)

    for atom in NTRS_C1_BASE_ATOMS:
        require(atom in plan, f"NTRS C_N lacks base atom {atom}", failures)
    languages = (
        '"domain-specific modeling language"', '"domain specific modeling language"',
        '"domain-specific modelling language"', '"domain specific modelling language"',
    )
    anchors = (
        "MBSE", '"model-based systems engineering"', '"model based systems engineering"',
        '"model-based system engineering"', '"model based system engineering"', "SysML",
        '"systems modeling language"', '"system model"', '"systems model"',
    )
    for language in languages:
        for anchor in anchors:
            require(f"'{language} {anchor}'" in plan, f"NTRS C_N lacks {language} + {anchor}", failures)
    require("**660 cells**" not in plan or "superseded 660-cell" in plan, "plan treats 660 cells as current", failures)

    require(dictionary.get("dictionary_version") == "1.5.0-source-completeness-2026-08-10", "dictionary version is not 1.5", failures)
    forms = {
        form.casefold()
        for concept in ("P", "E", "M", "G", "R", "T", "V1", "O1")
        for term in dictionary["concepts"][concept]["terms"]
        for form in term["forms"]
    }
    for form in (
        "nanosat", "nano satellites", "power mode", "power modes", "battery", "batteries",
        "systems modeling", "system modelling", "object-oriented systems model",
        "electric power subsystem", "reuses", "tailors", "customizes", "configures",
        "parameterizes", "instantiates", "specializes", "adapts", "traceable",
        "reliable", "reproducible", "integrable", "interoperable", "benefits", "no effect", "adverse",
    ):
        require(form in forms, f"dictionary lacks {form!r}", failures)
    require(dictionary["candidate_logic"].get("cross_route_cooccurrence") is False, "cross-route matching must remain false", failures)
    clusters = [
        artifact.get("cluster")
        for artifact in dictionary.get("genericity_recall", {}).get("artifacts", [])
    ]
    require(clusters.count("G1") == 11, "dictionary G1 artifact count is not 11", failures)
    require(clusters.count("G2") == 7, "dictionary G2 artifact count is not 7", failures)
    require(clusters.count("C1") == 6, "dictionary C1 artifact count is not 6", failures)

    templates_path = args.plan.parent / "searches" / "api-pagination-request-templates.json"
    require(templates_path.is_file(), "API request template file is missing", failures)
    if templates_path.is_file():
        templates = json.loads(templates_path.read_text(encoding="utf-8"))
        final_execution = templates.get("prospective_final_execution", {})
        for family, source_key in (("S", "scopus"), ("I", "ieee_xplore")):
            observed_ids = set(final_execution.get(source_key, {}).get("final_query_ids", []))
            expected_ids = {f"{family}-{suffix}" for suffix in SUFFIXES}
            require(
                observed_ids == expected_ids,
                f"{source_key} template query IDs differ: observed={sorted(observed_ids)}, expected={sorted(expected_ids)}",
                failures,
            )

    if SCRIPT_DIR.is_dir():
        discovered = {path.name for path in SCRIPT_DIR.glob("search_*.py")}
        expected = PERMITTED_SOURCE_SCRIPTS | FORBIDDEN_SOURCE_SCRIPTS
        require(discovered == expected, f"unaccounted source scripts: discovered={sorted(discovered)}, expected={sorted(expected)}", failures)
        for script in PERMITTED_SOURCE_SCRIPTS:
            require(f"`{script}`" in plan and "included" in plan, f"permitted adapter {script} is not mapped in plan", failures)
        for script in FORBIDDEN_SOURCE_SCRIPTS:
            require(f"`{script}`" in plan and "forbidden" in plan, f"forbidden adapter {script} is not declared", failures)
    else:
        require(False, f"source script directory is unavailable: {SCRIPT_DIR}", failures)

    report = {
        "status": "passed" if not failures else "failed",
        "protocol_version_checked": "1.5",
        "queries_checked": len(queries),
        "source_scripts_checked": len(PERMITTED_SOURCE_SCRIPTS | FORBIDDEN_SOURCE_SCRIPTS),
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
