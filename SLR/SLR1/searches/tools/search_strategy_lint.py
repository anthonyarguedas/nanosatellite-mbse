#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Static regression checks for the current source-plan translations."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


FAMILIES = ("S", "WS", "I", "C", "W", "SN", "PQ", "OATD", "ARC")
ALIASED_FAMILIES = {"PQDT": "PQ"}
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
MERGER_PATH = SCRIPT_DIR / "merge_search_results.py"
MERGER_TEST_PATH = SCRIPT_DIR / "test_merge_search_results.py"
REQUIRED_MERGER_SOURCE_KEYS = (
    "proquest_aerospace_index",
    "proquest_dissertations_theses_global",
    "oatd",
)
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
    require("**Protocol version:** `1.6` (frozen)" in protocol, "protocol is not frozen as version 1.6", failures)
    require("| `1.5` to `1.6` |" in protocol, "protocol lacks the version-1.6 amendment record", failures)
    require(
        "fourteen independently searched" in protocol and "through twelve interfaces" in protocol,
        "protocol lacks the version-1.6 source-count contract",
        failures,
    )
    require(
        "IAF Digital Library" in protocol and "Version 1.6" in protocol,
        "protocol does not retain IAF under version 1.6",
        failures,
    )
    require(
        "ProQuest Dissertations & Theses Global" in protocol
        and "Open Access Theses and Dissertations" in protocol,
        "protocol does not authorize both thesis/dissertation sources",
        failures,
    )
    require(
        "110 logical direct query events" in protocol,
        "protocol lacks the version-1.6 logical-query count",
        failures,
    )
    require("2026-08-10" in protocol and "common" in protocol, "protocol lacks the common cutoff", failures)

    queries = {
        f"{family}-{suffix}": extract(plan, f"{family}-{suffix}")
        for family in FAMILIES
        for suffix in SUFFIXES
    }
    for alias, source_family in ALIASED_FAMILIES.items():
        for suffix in SUFFIXES:
            alias_id = f"{alias}-{suffix}"
            source_id = f"{source_family}-{suffix}"
            require(
                f"| `{alias_id}` | `{source_id}` |" in plan,
                f"plan lacks normative alias {alias_id} -> {source_id}",
                failures,
            )
            queries[alias_id] = queries[source_id]

    thesis_manifest_entries_checked = 0
    thesis_manifest_path = (
        args.plan.parent / "searches" / "thesis-source-query-manifest-v1.6.json"
    )
    require(
        thesis_manifest_path.is_file(),
        "version-1.6 thesis-source query manifest is missing",
        failures,
    )
    if thesis_manifest_path.is_file():
        try:
            thesis_manifest = json.loads(
                thesis_manifest_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"thesis-source query manifest is invalid: {error}")
            thesis_manifest = {}
        require(
            thesis_manifest.get("protocol_version") == "1.6"
            and thesis_manifest.get("artifact_class")
            == "frozen_validation_contract_not_search_output",
            "thesis-source query manifest has the wrong protocol/artifact class",
            failures,
        )
        manifest_sources = thesis_manifest.get("sources", {})
        require(
            set(manifest_sources) == {
                "proquest_dissertations_theses_global", "oatd"
            },
            "thesis-source query manifest source keys are not exact",
            failures,
        )
        expected_manifest_families = {
            "proquest_dissertations_theses_global": ("PQDT", "PQ"),
            "oatd": ("OATD", "OATD"),
        }
        for source_key, (event_family, body_family) in expected_manifest_families.items():
            source = manifest_sources.get(source_key, {})
            entries = source.get("queries", []) if isinstance(source, dict) else []
            require(
                isinstance(entries, list) and len(entries) == len(SUFFIXES),
                f"{source_key} manifest must contain exactly eleven queries",
                failures,
            )
            indexed_entries = {
                entry.get("query_id"): entry
                for entry in entries
                if isinstance(entry, dict) and isinstance(entry.get("query_id"), str)
            }
            require(
                len(indexed_entries) == len(entries),
                f"{source_key} manifest query IDs are missing or duplicated",
                failures,
            )
            for suffix in SUFFIXES:
                event_id = f"{event_family}-{suffix}"
                body_id = f"{body_family}-{suffix}"
                entry = indexed_entries.get(event_id, {})
                expected_query = queries[event_id]
                require(
                    entry.get("source_body_id") == body_id,
                    f"{event_id} manifest body origin is not {body_id}",
                    failures,
                )
                require(
                    entry.get("query") == expected_query,
                    f"{event_id} manifest query differs from the governing plan",
                    failures,
                )
                require(
                    entry.get("query_sha256")
                    == hashlib.sha256(expected_query.encode("utf-8")).hexdigest(),
                    f"{event_id} manifest SHA-256 differs",
                    failures,
                )
                thesis_manifest_entries_checked += 1
        pqdt_controls = manifest_sources.get(
            "proquest_dissertations_theses_global", {}
        ).get("controls", {})
        require(
            manifest_sources.get("proquest_dissertations_theses_global", {}).get(
                "fixed_product_route"
            ) == "pqdtglobal"
            and pqdt_controls.get("sort") == "Relevance"
            and pqdt_controls.get("page_size") == 20
            and pqdt_controls.get("source_duplicate_exclusion") is False
            and pqdt_controls.get("full_text_limiter") is False
            and pqdt_controls.get("spelling_variants") is True
            and pqdt_controls.get("plural_and_adjective_variants") is True,
            "PQDT manifest controls differ from the frozen source contract",
            failures,
        )
        oatd_controls = manifest_sources.get("oatd", {}).get("controls", {})
        require(
            manifest_sources.get("oatd", {}).get("fixed_search_url")
            == "https://oatd.org/oatd/search"
            and oatd_controls.get("form") == "basic"
            and oatd_controls.get("sort") == "Relevance"
            and oatd_controls.get("page_size") == 30
            and oatd_controls.get("native_date_filter") is False
            and oatd_controls.get("native_language_filter") is False
            and oatd_controls.get("creative_commons_only") is False
            and oatd_controls.get("wildcards_permitted") is False,
            "OATD manifest controls differ from the frozen source contract",
            failures,
        )

    thesis_validation_files = (
        args.plan.parent / "searches" / "tools" / "oatd_basic_count_gate.py",
        args.plan.parent / "searches" / "tools" / "search_proquest_pqdt_global.py",
        args.plan.parent / "searches" / "tools" / "test_oatd_basic_count_gate.py",
        args.plan.parent / "searches" / "tools" / "test_search_proquest_pqdt_global.py",
        args.plan.parent / "searches" / "tools" / "test_thesis_source_count_gate_fixtures.py",
        args.plan.parent / "searches" / "fixtures" / "thesis-source-count-gate-v1.6.json",
    )
    for path in thesis_validation_files:
        require(path.is_file(), f"thesis-source validation artifact is missing: {path}", failures)
    if thesis_manifest_path.is_file():
        pinned_manifest_sha256 = hashlib.sha256(thesis_manifest_path.read_bytes()).hexdigest()
        for wrapper_name in ("oatd_basic_count_gate.py", "search_proquest_pqdt_global.py"):
            wrapper_path = args.plan.parent / "searches" / "tools" / wrapper_name
            wrapper_text = wrapper_path.read_text(encoding="utf-8") if wrapper_path.is_file() else ""
            require(
                pinned_manifest_sha256 in wrapper_text,
                f"{wrapper_name} does not pin the current thesis-source query manifest",
                failures,
            )
            require(
                "candidate_import_allowed" in wrapper_text
                and "merge_input" in wrapper_text
                and "pilot_not_candidate_search" in wrapper_text,
                f"{wrapper_name} lacks the non-candidate output boundary",
                failures,
            )
    fixture_path = args.plan.parent / "searches" / "fixtures" / "thesis-source-count-gate-v1.6.json"
    if fixture_path.is_file():
        try:
            fixture_contract = json.loads(fixture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"thesis-source count fixture is invalid: {error}")
        else:
            require(
                fixture_contract.get("contains_candidate_records") is False
                and fixture_contract.get("artifact_class")
                == "synthetic_interface_contract_fixture_not_search_output",
                "thesis-source count fixture lacks its synthetic non-candidate boundary",
                failures,
            )

    for query_id, query in queries.items():
        require('"nano satellites"' in query, f"{query_id} lacks spaced plural nano satellites", failures)
        require(balanced(query), f"{query_id} has unbalanced parentheses/quotes", failures)

    for query_id, query in queries.items():
        if query_id.startswith(("I-", "OATD-", "ARC-")):
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
        if family not in {"I", "OATD"}:
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

    for family in ("I", "OATD"):
        for token in IEEE_T2_FINITE_TERMS:
            require(
                token_present(queries[f"{family}-BT2"], token),
                f"{family}-BT2 lacks finite inflection {token}",
                failures,
            )

    finite_relation = "(requirement OR requirements OR function OR functions OR behavior OR behaviors OR behaviour OR behaviours OR architecture OR architectures OR interface OR interfaces OR traceability OR parametric OR parametrics OR verification OR validation)"
    for family in ("I", "OATD"):
        require(
            finite_relation in queries[f"{family}-B2"],
            f"{family}-B2 relation block differs from explicit frozen inflections",
            failures,
        )

    for required_plan_control in (
        "version `1.6`", "fourteen independently searched sources/collections through twelve interfaces",
        "110 logical direct query events", "99 physical source-native code blocks", "A1 ∪ A2 ∪ A3",
        "## 13. ProQuest Dissertations & Theses Global", "## 14. Open Access Theses and Dissertations",
        "## 16. IAF Digital Library authorized", "2026-08-10", "**940 cells**",
        "**180 N-B-core cells**", "**250 N-BG cells**", "**510 N-BC1 cells**",
        "**280 unpiloted C1 cells**", "pilots-to-run-v1.6.md",
        "PQDT-A1 = 1", "PQDT-B1 = 17", "PQDT-B2 = 9",
        "OATD-B1** below through the basic interface", "**23**-record aggregate",
        "Server Too Busy - Please slow down", "form=basic",
        "search_proquest_pqdt_global.py", "oatd_basic_count_gate.py",
        "final-run-source-crosswalk-v1.6.json", "failure-register-schema-v1.6.json",
    ):
        require(required_plan_control in plan, f"version-1.6 plan lacks {required_plan_control}", failures)

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

    require(dictionary.get("dictionary_version") == "1.6.0-thesis-sources-2026-08-10", "dictionary version is not 1.6", failures)
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
        require(templates.get("schema_version") == "1.6", "API template schema is not 1.6", failures)
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

    require(MERGER_PATH.is_file(), f"merger is unavailable: {MERGER_PATH}", failures)
    require(MERGER_TEST_PATH.is_file(), f"merger tests are unavailable: {MERGER_TEST_PATH}", failures)
    merger_text = MERGER_PATH.read_text(encoding="utf-8") if MERGER_PATH.is_file() else ""
    merger_test_text = (
        MERGER_TEST_PATH.read_text(encoding="utf-8") if MERGER_TEST_PATH.is_file() else ""
    )
    for source_key in REQUIRED_MERGER_SOURCE_KEYS:
        require(source_key in merger_text, f"merger lacks source key {source_key}", failures)
        require(source_key in merger_test_text, f"merger tests lack source key {source_key}", failures)

    report = {
        "status": "passed" if not failures else "failed",
        "protocol_version_checked": "1.6",
        "physical_query_blocks_checked": len(FAMILIES) * len(SUFFIXES),
        "aliased_query_blocks_checked": len(ALIASED_FAMILIES) * len(SUFFIXES),
        "queries_checked": len(queries),
        "thesis_source_manifest_entries_checked": thesis_manifest_entries_checked,
        "thesis_validation_files_checked": len(thesis_validation_files),
        "source_scripts_checked": len(PERMITTED_SOURCE_SCRIPTS | FORBIDDEN_SOURCE_SCRIPTS),
        "merger_source_keys_checked": len(REQUIRED_MERGER_SOURCE_KEYS),
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
