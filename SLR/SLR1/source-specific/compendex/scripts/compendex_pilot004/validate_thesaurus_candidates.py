#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Validate Pilot 004 candidates against the live Compendex Ei Thesaurus."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
from copy import deepcopy
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urljoin, urlsplit

import queries

ADAPTER_PATH = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/_engineering_village_search.py"
)
CANDIDATES = (
    {
        "term": "Nanosatellites",
        "proposed_block": "P",
        "expected": "exact",
        "assignment_required": True,
        "role": "Population descriptor matching the normative nanosatellites literal.",
    },
    {
        "term": "Small satellites",
        "proposed_block": "P",
        "expected": "exact",
        "assignment_required": True,
        "role": "Population descriptor matching the normative small satellites literal.",
    },
    {
        "term": "Systems engineering",
        "proposed_block": "M_H_context_only",
        "expected": "exact",
        "assignment_required": True,
        "role": "Generic context descriptor that cannot satisfy M_H alone.",
    },
    {
        "term": "Modeling languages",
        "proposed_block": "M_H_modeling_context",
        "expected": "exact",
        "assignment_required": True,
        "role": "Modeling descriptor combined with Systems engineering for M_H.",
    },
    {
        "term": "SysML",
        "proposed_block": "M_H_direct_candidate",
        "expected": "exact",
        "assignment_required": False,
        "role": "Specific M_H descriptor candidate tested for selected-record assignment.",
    },
    {
        "term": "Model-based systems engineering",
        "proposed_block": "M_H_direct_candidate",
        "expected": "absent",
        "assignment_required": False,
        "role": "Direct MBSE label tested for exact preferred-term availability.",
    },
    {
        "term": "CubeSat",
        "proposed_block": "P_direct_candidate",
        "expected": "absent",
        "assignment_required": False,
        "role": "Direct CubeSat label tested for exact preferred-term availability.",
    },
)

RELATION_SCRIPT = r"""
() => {
  const normalize = value => String(value || "").replace(/\s+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const relations = {full: [], broader: [], related: [], narrower: [], prior: [], top: []};
  for (const control of Array.from(document.querySelectorAll("input.add-term[id]"))) {
    if (!visible(control)) continue;
    const match = String(control.id || "").match(
      /^(full|broader|related|narrow|prior|top)-result-([0-9]+)$/
    );
    if (!match) continue;
    const relation = match[1] === "narrow" ? "narrower" : match[1];
    relations[relation].push({term: normalize(control.value), term_id: match[2]});
  }
  const scopeLinks = Array.from(document.querySelectorAll("a.scope-note[href]"))
    .filter(visible)
    .map(anchor => ({href: anchor.getAttribute("href"), title: normalize(anchor.title)}));
  const expansionControls = Array.from(document.querySelectorAll("input,button,a,label,select"))
    .filter(visible)
    .filter(element => /\b(?:explode|explosion|include\s+(?:narrower|descendants?)|focus|major\s+(?:topic|heading))\b/i
      .test(normalize(element.innerText || element.getAttribute("aria-label") || "")))
    .length;
  return {relations, scopeLinks, expansionControls};
}
"""

SCOPE_SCRIPT = r"""
() => {
  const normalize = value => String(value || "").replace(/\s+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const paragraphs = Array.from(document.querySelectorAll("#contents p"))
    .filter(visible)
    .map(element => normalize(element.innerText || element.textContent))
    .filter(Boolean);
  const bodyText = normalize(document.body?.innerText || "");
  return {
    host: location.hostname,
    path: location.pathname,
    paragraphs,
    blocked: ["suspicious activity", "access currently limited", "access denied", "captcha", "verify you are human", "unusual traffic"]
      .some(marker => bodyText.toLowerCase().includes(marker)),
    requiresLogin: /trouble signing in|check to see if you have access/i.test(bodyText),
  };
}
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "compendex_pilot004_vocabulary_adapter", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load the Engineering Village adapter at {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_assignments(artifact: Any) -> None:
    if not isinstance(artifact, dict) or artifact.get("status") != "complete_two_pass_assignment_readback":
        raise RuntimeError("The Compendex assignment harvest is incomplete")
    if artifact.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        raise RuntimeError("The assignment harvest uses a different protocol commit")
    assignments = artifact.get("candidate_assignments")
    if not isinstance(assignments, dict):
        raise RuntimeError("The assignment harvest lacks candidate assignment evidence")
    for candidate in CANDIDATES:
        if not candidate["assignment_required"]:
            continue
        entry = assignments.get(candidate["term"])
        if not isinstance(entry, dict) or entry.get("assigned_record_count", 0) < 1:
            raise RuntimeError(f"Required candidate {candidate['term']!r} lacks selected-record assignment evidence")
    context = artifact.get("context_qualified_M_H_assignment", {})
    if context.get("assigned_record_count", 0) < 1:
        raise RuntimeError("The context-qualified M_H construction lacks joint assignment evidence")


def parse_scope(payload: Any, expected_term: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise RuntimeError("Engineering Village returned malformed scope-note evidence")
    if payload.get("blocked") is True or payload.get("requiresLogin") is True:
        raise RuntimeError("Engineering Village blocked scope-note inspection")
    if clean(payload.get("host")).casefold() != "www.engineeringvillage.com":
        raise RuntimeError("Scope-note inspection left Engineering Village")
    if payload.get("path") != "/thes/scopenote.url":
        raise RuntimeError("Engineering Village returned an unexpected scope-note route")
    paragraphs = [clean(value) for value in payload.get("paragraphs", []) if clean(value)]
    if not paragraphs or paragraphs[0].casefold() != expected_term.casefold():
        raise RuntimeError(f"Scope-note title did not match {expected_term!r}")
    introduced: str | None = None
    classification_codes: list[str] = []
    prose: list[str] = []
    for paragraph in paragraphs[1:]:
        introduced_match = re.fullmatch(r"Introduced:\s*(\d{4}-\d{2}-\d{2})", paragraph)
        if introduced_match:
            introduced = introduced_match.group(1)
            continue
        prefix = "Related classification codes:"
        if paragraph.startswith(prefix):
            classification_codes = [
                clean(value) for value in paragraph[len(prefix) :].split(";") if clean(value)
            ]
            continue
        prose.append(paragraph)
    return {
        "state": "observed",
        "term": paragraphs[0],
        "introduced": introduced,
        "related_classification_codes": classification_codes,
        "prose_scope_note": " ".join(prose) or None,
        "prose_scope_note_state": "observed" if prose else "not_exposed",
    }


async def inspect_exact_term(
    adapter: Any,
    page: Any,
    candidate: dict[str, Any],
    timeout_seconds: float,
) -> dict[str, Any]:
    plan = adapter.build_controlled_vocabulary_plan(
        databases=("compendex",), controlled_terms=[candidate["term"]]
    )
    try:
        validated, receipt = await adapter.validate_live_vocabulary_plan(
            page, plan, timeout_seconds
        )
    except adapter.CompendexProtocolError as error:
        if error.code != adapter.ProtocolFailureCode.VOCABULARY_TERM_NOT_FOUND.value:
            raise
        if candidate["expected"] != "absent":
            raise RuntimeError(f"Expected exact candidate {candidate['term']!r} was absent") from error
        return {
            **candidate,
            "status": "not_an_exact_preferred_ei_thesaurus_term",
            "source_failure_code": error.code,
            "term_id": None,
            "exact_clause": None,
            "hierarchy": None,
            "scope_note": None,
        }
    if candidate["expected"] != "exact":
        raise RuntimeError(f"Candidate {candidate['term']!r} unexpectedly became an exact preferred term")
    observation = receipt["observations"][0]
    canonical = clean(observation["term"])
    term_id = clean(observation["term_id"])
    if len(validated.controlled_terms) != 1 or not term_id.isdigit():
        raise RuntimeError(f"Candidate {candidate['term']!r} lacked one validated numeric identity")

    initial = page.locator(f"#thes-result-{term_id}")
    if await initial.count() != 1:
        raise RuntimeError(f"Candidate {candidate['term']!r} lacked one exact result control")
    full_link = initial.locator("xpath=..").locator("a.fullRecLink")
    if await full_link.count() != 1 or not await full_link.is_visible():
        raise RuntimeError(f"Candidate {candidate['term']!r} lacked one visible full-record link")
    await full_link.click()
    await page.locator(f"#full-result-{term_id}").wait_for(
        state="visible", timeout=max(1, int(timeout_seconds * 1000))
    )
    relation_payload = await page.evaluate(RELATION_SCRIPT)
    if not isinstance(relation_payload, dict) or relation_payload.get("expansionControls") != 0:
        raise RuntimeError("Engineering Village exposed an unexpected vocabulary expansion control")
    relations = relation_payload.get("relations")
    if not isinstance(relations, dict):
        raise RuntimeError("Engineering Village returned malformed thesaurus relations")
    full = relations.get("full")
    if full != [{"term": canonical, "term_id": term_id}]:
        raise RuntimeError(f"Candidate {candidate['term']!r} full-record identity changed")
    hierarchy = {
        relation: relations.get(relation, [])
        for relation in ("broader", "related", "narrower", "prior", "top")
    }
    for relation, entries in hierarchy.items():
        if not isinstance(entries, list):
            raise RuntimeError(f"Candidate {candidate['term']!r} had malformed {relation} relations")
        identities = [(clean(entry.get("term")), clean(entry.get("term_id"))) for entry in entries]
        if any(not term or not identity.isdigit() for term, identity in identities):
            raise RuntimeError(f"Candidate {candidate['term']!r} had invalid {relation} identities")
        if len(identities) != len(set(identities)):
            raise RuntimeError(f"Candidate {candidate['term']!r} had duplicate {relation} identities")

    scope_links = relation_payload.get("scopeLinks")
    if not isinstance(scope_links, list) or len(scope_links) > 1:
        raise RuntimeError(f"Candidate {candidate['term']!r} had ambiguous scope-note links")
    if scope_links:
        href = clean(scope_links[0].get("href"))
        parsed = urlsplit(urljoin(adapter.PORTAL_ORIGIN, href))
        params = parse_qs(parsed.query)
        if (
            parsed.scheme != "https"
            or parsed.hostname != "www.engineeringvillage.com"
            or parsed.path != "/thes/scopenote.url"
            or params.get("database") != ["1"]
            or [value.casefold() for value in params.get("term", [])] != [canonical.casefold()]
        ):
            raise RuntimeError(f"Candidate {candidate['term']!r} had an invalid scope-note route")
        await page.goto(
            parsed.geturl(),
            wait_until="domcontentloaded",
            timeout=max(1, int(timeout_seconds * 1000)),
        )
        scope_note = parse_scope(await page.evaluate(SCOPE_SCRIPT), canonical)
    else:
        scope_note = {
            "state": "not_exposed",
            "term": canonical,
            "introduced": None,
            "related_classification_codes": [],
            "prose_scope_note": None,
            "prose_scope_note_state": "not_exposed",
        }
    return {
        **candidate,
        "status": "verified_exact_preferred_ei_thesaurus_term",
        "canonical_term": canonical,
        "term_id": term_id,
        "vocabulary": "Ei Thesaurus",
        "field": "CV",
        "exact_clause": f"{{{canonical}}} WN CV",
        "preferred_result": True,
        "hierarchy": hierarchy,
        "hierarchy_expansion": "not_requested_and_not_implicit",
        "focus": "not_exposed",
        "major_topic": "not_requested",
        "scope_note": scope_note,
    }


async def run(
    assignment_path: Path,
    output_path: Path,
    failure_path: Path,
    timeout_seconds: float,
) -> None:
    assignments = json.loads(assignment_path.read_text(encoding="utf-8"))
    validate_assignments(assignments)
    adapter = load_adapter()
    from playwright.async_api import async_playwright

    started_at = now()
    pass_results: list[list[dict[str, Any]]] = []
    try:
        async with async_playwright() as playwright:
            connection = None
            try:
                connection = await adapter.open_chrome_connection(
                    playwright,
                    cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
                    headless=False,
                    timeout_seconds=timeout_seconds,
                    chrome_executable=None,
                    require_single_cdp_context=True,
                )
                for _pass_number in (1, 2):
                    page = None
                    try:
                        page = await adapter.new_owned_chrome_page(
                            connection.context,
                            timeout_seconds=timeout_seconds,
                            authorization=None,
                            validate_authorization=adapter._validate_engineering_village_authorized_target,
                        )
                        current: list[dict[str, Any]] = []
                        for candidate in CANDIDATES:
                            current.append(
                                await inspect_exact_term(
                                    adapter, page, candidate, timeout_seconds
                                )
                            )
                        pass_results.append(current)
                    finally:
                        await adapter.close_owned_chrome_page_only(page)
            finally:
                await adapter.close_chrome_connection(connection)
    except Exception as error:
        failure = {
            "schema_version": "compendex-controlled-vocabulary-validation-failure/v1",
            "source": "Compendex",
            "pilot": "004",
            "status": "error",
            "do_not_merge": True,
            "protocol_commit": queries.PROTOCOL_COMMIT,
            "started_at_utc": started_at,
            "failed_at_utc": now(),
            "stage": "ei_thesaurus_candidate_validation",
            "error_type": type(error).__name__,
            "error": clean(error),
            "candidate_terms": [candidate["term"] for candidate in CANDIDATES],
        }
        failure_path.parent.mkdir(parents=True, exist_ok=True)
        failure_path.write_text(json.dumps(failure, indent=2, ensure_ascii=False) + "\n")
        raise

    passes_equal = len(pass_results) == 2 and pass_results[0] == pass_results[1]
    if not passes_equal:
        raise RuntimeError("Ei Thesaurus candidate identity or hierarchy changed across passes")
    assignment_evidence = assignments["candidate_assignments"]
    active = deepcopy(pass_results[1])
    for candidate in active:
        assigned = assignment_evidence.get(candidate["term"], {})
        candidate["selected_record_assignment_count"] = assigned.get(
            "assigned_record_count", 0
        )
        candidate["selected_record_assignment_accessions"] = assigned.get(
            "assigned_accessions", []
        )
    artifact = {
        "schema_version": "compendex-ei-thesaurus-candidate-validation/v1",
        "source": "Compendex",
        "source_id": "compendex",
        "platform": "Engineering Village",
        "pilot": "004",
        "status": "complete_two_pass_readback",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "started_at_utc": started_at,
        "completed_at_utc": now(),
        "adapter": {
            "id": adapter.ADAPTER_ID,
            "version": adapter.ADAPTER_VERSION,
        },
        "vocabulary": {
            "name": "Ei Thesaurus",
            "database": "Compendex",
            "version": None,
            "version_state": "not_exposed",
            "release_cadence_state": "not_exposed",
            "field": "CV",
            "exact_syntax": "{term} WN CV",
            "explosion": "not_requested_and_no_control_exposed",
            "focus": "not_exposed",
            "major_topic": "not_requested",
        },
        "method": {
            "passes": 2,
            "lookup": "Engineering Village Thesaurus Search / Exact term",
            "hierarchy": "source-rendered broader, related, narrower, prior, and top relations",
            "scope_notes": "source-rendered /thes/scopenote.url",
            "private_paths_persisted": False,
            "session_values_persisted": False,
        },
        "candidates": active,
        "context_qualified_M_H": {
            "construction": queries.M_H_CONTROLLED,
            "rule": (
                "Systems engineering is generic and is accepted only when AND-combined "
                "with the Modeling languages descriptor."
            ),
            "joint_selected_record_assignment_count": assignments[
                "context_qualified_M_H_assignment"
            ]["assigned_record_count"],
            "joint_selected_record_assignment_accessions": assignments[
                "context_qualified_M_H_assignment"
            ]["assigned_accessions"],
        },
        "pass_reconciliation": {
            "passes": 2,
            "ordered_candidate_results_equal": passes_equal,
            "pass_1_terms": [candidate["term"] for candidate in pass_results[0]],
            "pass_2_terms": [candidate["term"] for candidate in pass_results[1]],
        },
        "interpretation_boundary": [
            "Hierarchy relations are navigation evidence and were not exploded.",
            "A term introduced date is not an Ei Thesaurus release identifier.",
            "Exact vocabulary identity and selected-record assignment do not prove marginal recall.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--failure-output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()
    asyncio.run(run(args.assignments, args.output, args.failure_output, args.timeout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
