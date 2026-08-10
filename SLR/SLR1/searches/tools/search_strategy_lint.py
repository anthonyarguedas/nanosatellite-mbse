#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Static regression checks for the frozen version-1.3 source translations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


FAMILIES = ("S", "WS", "I", "C", "W")
SUFFIXES = ("A1", "A2", "B1", "B2", "BG1", "BG2", "BC1", "BT2", "V1", "O1")
MODEL_VARIANTS = (
    '"system modeling"', '"systems modeling"', '"system modelling"', '"systems modelling"'
)


def extract(markdown: str, query_id: str) -> str:
    match = re.search(rf"^### {re.escape(query_id)}(?:\s+[^\n]*)?\n\n```text\n(.*?)\n```", markdown, re.M | re.S)
    if not match:
        raise ValueError(f"missing query block {query_id}")
    return match.group(1).strip()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--dictionary", required=True, type=Path)
    args = parser.parse_args()
    plan = args.plan.read_text(encoding="utf-8")
    dictionary = json.loads(args.dictionary.read_text(encoding="utf-8"))
    failures: list[str] = []
    queries = {f"{family}-{suffix}": extract(plan, f"{family}-{suffix}") for family in FAMILIES for suffix in SUFFIXES}

    for query_id, query in queries.items():
        require('"nano satellites"' in query, f"{query_id} lacks spaced plural nano satellites", failures)
    for query_id, query in queries.items():
        if query_id.startswith("I-"):
            require(bool(re.search(r"(?<![A-Za-z0-9_])nanosat(?![A-Za-z0-9_*])", query)), f"{query_id} lacks standalone nanosat", failures)
    for family in FAMILIES:
        for suffix in ("A2", "B2"):
            query_id = f"{family}-{suffix}"; query = queries[query_id]
            for phrase in MODEL_VARIANTS:
                require(phrase in query, f"{query_id} lacks {phrase}", failures)
            require('"object-oriented systems model"' in query, f"{query_id} lacks object-oriented systems model", failures)
    for family in FAMILIES:
        query = queries[f"{family}-A2"]
        for phrase in ('"power mode"', '"power modes"'):
            require(phrase in query, f"{family}-A2 lacks {phrase}", failures)
    for family in ("I", "W"):
        require('"electric power subsystem"' in queries[f"{family}-A1"], f"{family}-A1 lacks electric power subsystem", failures)
        for token in ('"power generation"', "battery", "batteries"):
            require(token in queries[f"{family}-A2"], f"{family}-A2 lacks {token}", failures)
    ieee_relation = "(requirement OR requirements OR function OR functions OR behavior OR behaviors OR behaviour OR behaviours OR architecture OR architectures OR interface OR interfaces OR traceability OR parametric OR parametrics OR verification OR validation)"
    require(ieee_relation in queries["I-B2"], "I-B2 relation block differs from explicit frozen inflections", failures)
    wiley_relation = "(requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)"
    require(wiley_relation in queries["W-B2"], "W-B2 relation wildcard block differs from frozen form", failures)
    for query_id, query in queries.items():
        if query_id.startswith("S-"):
            require("DOCTYPE(" not in query, f"{query_id} retains Scopus DOCTYPE filter", failures)
    require("Select **no Document Type restriction**" in plan, "WoS no-type control is not explicit", failures)
    require("Do not add a `ContentType` refinement" in plan, "IEEE no-type control is not explicit", failures)
    for family in FAMILIES:
        for suffix, required in {
            "BG1": ('"generic model"', '"model template"'),
            "BG2": ('"reference architecture"', '"variation point"'),
            "BC1": ('"model library"', '"domain-specific modeling language"'),
            "BT2": ('"system model"', "tailor"),
        }.items():
            query_id = f"{family}-{suffix}"
            query = queries[query_id]
            for token in required:
                require(token in query, f"{query_id} lacks {token}", failures)
        for suffix in ("BG1", "BG2", "BC1"):
            query_id = f"{family}-{suffix}"
            query = queries[query_id]
            require("verification" not in query.casefold(), f"{query_id} is not relation-free", failures)
            require("validation" not in query.casefold(), f"{query_id} is not relation-free", failures)

    for query_id, query in queries.items():
        balance = 0
        quoted = False
        for character in query:
            if character == '"':
                quoted = not quoted
            elif not quoted and character == "(":
                balance += 1
            elif not quoted and character == ")":
                balance -= 1
            if balance < 0:
                break
        require(balance == 0 and not quoted, f"{query_id} has unbalanced parentheses/quotes", failures)

    require("**660 cells**" in plan, "NTRS mandatory-cell arithmetic is not 660", failures)
    for expected in ("**180 N-B-core cells**", "**250 N-BG cells**", "**230 N-BC1 cells**"):
        require(expected in plan, f"NTRS partition assertion missing: {expected}", failures)
    p_n_match = re.search(r"^- `P_N = \{(.*?)\}`;", plan, re.M)
    require(p_n_match is not None, "NTRS P_N set is missing", failures)
    if p_n_match:
        for term in ("CubeSat", "CubeSats", '"cube sat"', "nanosat", "nanosatellite", "nanosatellites", '"nano-satellite"', '"nano-satellites"', '"nano satellite"', '"nano satellites"'):
            require(term in p_n_match.group(1), f"NTRS P_N lacks {term}", failures)
    require("136 mandatory NTRS" not in plan, "obsolete 136-cell stopping rule remains", failures)

    forms = {
        form.casefold()
        for concept in ("P", "E", "M", "G", "R", "T")
        for term in dictionary["concepts"][concept]["terms"]
        for form in term["forms"]
    }
    required_dictionary_forms = {
        "nanosat", "nano satellites", "power mode", "power modes", "battery", "batteries",
        "systems modeling", "system modelling", "object-oriented systems model", "electric power subsystem"
    }
    for form in required_dictionary_forms:
        require(form in forms, f"dictionary lacks {form!r}", failures)
    require(dictionary["candidate_logic"].get("cross_route_cooccurrence") is False, "ESA cross-route matching must remain false", failures)
    clusters = [artifact.get("cluster") for artifact in dictionary.get("genericity_recall", {}).get("artifacts", [])]
    require(clusters.count("G1") == 11, "dictionary G1 artifact count is not 11", failures)
    require(clusters.count("G2") == 7, "dictionary G2 artifact count is not 7", failures)
    require(clusters.count("C1") == 6, "dictionary C1 artifact count is not 6", failures)

    report = {"status": "passed" if not failures else "failed", "queries_checked": len(queries), "failures": failures}
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
