#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Harvest PQDT Subject and Index term assignments from selected records."""

from __future__ import annotations

import argparse
import asyncio
from collections import Counter
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

import queries

SCHEMA = "pqdt-global-pilot005-assigned-term-harvest/v1"
DEFAULT_PREFLIGHT = queries.PILOT_ROOT / "searches" / "preflight.json"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "assigned-terms.json"
DEFAULT_FAILURE = (
    queries.PILOT_ROOT
    / "searches"
    / "failures"
    / "assigned-terms.NON_MERGEABLE_FAILURE.json"
)

ASSIGNMENT_STATE_SCRIPT = r"""
() => {
  const normalize = value => String(value || "").replace(/[\s\u200e\u200f]+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const bodyText = document.body && document.body.innerText ? document.body.innerText : "";
  const lower = bodyText.toLowerCase();
  const titleNodes = Array.from(document.querySelectorAll("#documentTitle, h1.documentTitle"))
    .filter(visible);
  const productLinks = Array.from(document.querySelectorAll(
    "a[aria-label='ProQuest Dissertations & Theses Global Product Home page']"
  )).filter(visible);
  const pathMatch = window.location.pathname.match(/^\/pqdtglobal\/docview\/(\d+)(?:\/|$)/i);
  const indexingSections = Array.from(document.querySelectorAll(
    "div[id^='indexingSectionDiv_MSTAR_']"
  )).filter(visible);
  const section = indexingSections.length === 1 ? indexingSections[0] : null;
  const links = section
    ? Array.from(section.querySelectorAll("a.lateralSearch[href]"))
        .filter(visible)
        .map(element => {
          let route = "";
          try {
            const parsed = new URL(element.href, window.location.origin);
            const match = parsed.pathname.match(
              /^\/pqdtglobal\/indexinglinkhandler\/sng\/([^/]+)\//i
            );
            if (parsed.origin === "https://www.proquest.com" && match) route = match[1].toLowerCase();
          } catch (_) {}
          return {label: normalize(element.textContent), route};
        })
        .filter(item => item.label && item.route)
    : [];
  const rows = section
    ? Array.from(section.querySelectorAll(":scope > .display_record_indexing_row"))
        .filter(visible)
        .map(row => ({
          label: normalize(row.querySelector(":scope > .display_record_indexing_fieldname")?.textContent),
          values: Array.from(row.querySelectorAll(":scope > .display_record_indexing_data a.lateralSearch"))
            .filter(visible).map(element => normalize(element.textContent)).filter(Boolean)
        }))
        .filter(item => item.label)
    : [];
  return {
    protocol: window.location.protocol,
    host: window.location.hostname,
    pathClass: /^\/pqdtglobal\/docview\/\d+\/abstract\/[^/]+\/\d+$/i.test(window.location.pathname)
      ? "pqdt_abstract_details" : "other",
    paperId: pathMatch ? pathMatch[1] : "",
    titleHasSource: document.title.includes("ProQuest Dissertations & Theses Global"),
    productLinkCount: productLinks.length,
    titleCount: titleNodes.length,
    title: titleNodes.length === 1 ? normalize(titleNodes[0].textContent) : "",
    indexingSectionCount: indexingSections.length,
    rows,
    links,
    databaseValues: rows.filter(item => item.label === "Database").flatMap(item => item.values),
    blocked: ["captcha", "verify you are human", "access denied", "unusual traffic"]
      .some(marker => lower.includes(marker)),
    requiresAccess: /authentication error|institutional access required|session has expired/i.test(bodyText) ||
      /\/(?:login|signin)(?:\/|$)/i.test(window.location.pathname)
  };
}
"""


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def safe_error(error: BaseException) -> str:
    message = clean(error)
    if "intercepts pointer events" in message:
        return "The source sticky tools menu intercepted the Abstract/Details action."
    if "target identities" in message or "adapter-owned Chrome page target" in message:
        return "The shared browser target inventory changed during owned-page setup."
    if re.search(r"(?i)accountid|_csrf|/abstract/[A-Za-z0-9]+/", message):
        return "Source interaction failed. URL and session details were omitted."
    return message


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pqdt_pilot005_assignment_adapter", queries.ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load PQDT adapter at {queries.ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_preflight(path: Path) -> dict[str, Any]:
    preflight = queries.load_object(path)
    if preflight.get("schema_version") != "pqdt-global-pilot005-preflight/v1":
        raise RuntimeError("Unexpected PQDT Pilot 005 preflight schema")
    if preflight.get("status") != "predeclared":
        raise RuntimeError("PQDT Pilot 005 preflight is not active")
    pinned = preflight.get("pinned_inputs")
    adapter = pinned.get("adapter") if isinstance(pinned, Mapping) else None
    if not isinstance(adapter, Mapping) or adapter.get("sha256") != queries.file_sha256(
        queries.ADAPTER_PATH
    ):
        raise RuntimeError("The PQDT adapter changed after predeclaration")
    records = preflight.get("record_selection", {}).get("records")
    if not isinstance(records, list) or len(records) != len(queries.SELECTED_KNOWN_RECORDS):
        raise RuntimeError("PQDT Pilot 005 selected-record plan changed")
    expected_ids = [item["paper_id"] for item in queries.SELECTED_KNOWN_RECORDS]
    if [item.get("paper_id") for item in records if isinstance(item, Mapping)] != expected_ids:
        raise RuntimeError("PQDT Pilot 005 selected-record order changed")
    return preflight


def parse_assignment_state(payload: Any, expected: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise RuntimeError("PQDT returned malformed assignment evidence")
    paper_id = clean(payload.get("paperId"))
    if payload.get("blocked") is True or payload.get("requiresAccess") is True:
        raise RuntimeError(f"PQDT assignment page was blocked for {paper_id or 'an unknown record'}")
    if not all(
        (
            payload.get("protocol") == "https:",
            clean(payload.get("host")).casefold() == "www.proquest.com",
            payload.get("pathClass") == "pqdt_abstract_details",
            paper_id == expected["paper_id"],
            payload.get("titleHasSource") is True,
            payload.get("productLinkCount") == 1,
            payload.get("titleCount") == 1,
            clean(payload.get("title")).casefold() == expected["title"].casefold(),
            payload.get("indexingSectionCount") == 1,
        )
    ):
        raise RuntimeError(f"PQDT assignment scope or identity failed for {expected['paper_id']}")

    raw_links = payload.get("links")
    if not isinstance(raw_links, list) or not raw_links:
        raise RuntimeError(f"PQDT exposed no indexing assignments for {paper_id}")
    by_route: dict[str, list[str]] = {}
    for raw in raw_links:
        if not isinstance(raw, Mapping):
            raise RuntimeError(f"PQDT exposed a malformed indexing assignment for {paper_id}")
        route = clean(raw.get("route")).casefold()
        label = clean(raw.get("label"))
        if not route or not label or len(label) > 512:
            raise RuntimeError(f"PQDT exposed an invalid indexing assignment for {paper_id}")
        by_route.setdefault(route, []).append(label)
    for route, labels in by_route.items():
        if len(labels) != len(set(labels)):
            raise RuntimeError(f"PQDT exposed duplicate {route} assignments for {paper_id}")

    ps_count = len(by_route.get("mainsubject", []))
    return {
        "paper_id": paper_id,
        "title": clean(payload.get("title")),
        "canonical_url": f"https://www.proquest.com/pqdtglobal/docview/{paper_id}",
        "source_scope_proof": "exact_pqdt_title_product_link_and_abstract_details_route",
        "pq_subject_field": "PSUB.EXACT",
        "pq_subject_terms": by_route.get("mainsubject", []),
        "pq_subject_term_count": ps_count,
        "index_term_field": "IF.EXACT",
        "index_terms": by_route.get("if", []),
        "index_term_count": len(by_route.get("if", [])),
        "broader_subject_terms": by_route.get("subject", []),
        "other_indexing_routes": {
            route: labels
            for route, labels in sorted(by_route.items())
            if route not in {"mainsubject", "if", "subject"}
        },
    }


async def open_abstract_details(
    adapter: Any, page: Any, expected: Mapping[str, Any], timeout_seconds: float
) -> None:
    paper_id = expected["paper_id"]
    await adapter.navigate(
        page,
        f"https://www.proquest.com/pqdtglobal/docview/{paper_id}",
        timeout_seconds,
    )
    await adapter.wait_ready(
        page, adapter.PQDT_DETAIL_STATE_SCRIPT, None, timeout_seconds
    )
    path = clean(getattr(page, "url", ""))
    if f"/pqdtglobal/docview/{paper_id}/abstract/" not in path:
        abstract = page.locator("#addFlashPageParameterformat_abstract:visible")
        if await abstract.count() != 1:
            raise RuntimeError(f"PQDT record {paper_id} lacked one Abstract/Details action")
        try:
            await abstract.click(timeout=adapter.milliseconds(min(timeout_seconds, 5.0)))
        except Exception:
            await abstract.dispatch_event("click")
        await page.wait_for_load_state(
            "domcontentloaded", timeout=adapter.milliseconds(timeout_seconds)
        )
    detail_payload = await adapter.wait_ready(
        page, adapter.PQDT_DETAIL_STATE_SCRIPT, None, timeout_seconds
    )
    detail = adapter.parse_detail_state(detail_payload)
    if detail.paper_id != paper_id or detail.title.casefold() != expected["title"].casefold():
        raise RuntimeError(f"PQDT Abstract/Details identity changed for {paper_id}")


async def harvest(
    preflight_path: Path,
    output_path: Path,
    failure_path: Path,
    timeout_seconds: float,
) -> None:
    if output_path.exists():
        raise RuntimeError(f"Refusing to overwrite {output_path}")
    if failure_path.exists():
        raise RuntimeError(f"Refusing to overwrite {failure_path}")
    preflight = validate_preflight(preflight_path)
    expected_records = preflight["record_selection"]["records"]
    adapter = load_adapter()
    from playwright.async_api import async_playwright

    started_at = adapter.utc_now()
    scope = None
    passes: list[list[dict[str, Any]]] = []
    try:
        async with async_playwright() as playwright, adapter._LeaseCleanup() as cleanup:
            lease = await adapter.open_owned_chrome_page(
                playwright,
                cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
                headless=False,
                timeout_seconds=timeout_seconds,
                chrome_executable=None,
            )
            cleanup.lease = lease
            scope = adapter._PQDTScopeCleanup(
                lease.page, timeout_seconds=timeout_seconds
            )
            await scope.__aenter__()
            cleanup.scope = scope
            for _pass_number in (1, 2):
                current: list[dict[str, Any]] = []
                for expected in expected_records:
                    await open_abstract_details(
                        adapter, lease.page, expected, timeout_seconds
                    )
                    payload = await lease.page.evaluate(ASSIGNMENT_STATE_SCRIPT)
                    current.append(parse_assignment_state(payload, expected))
                passes.append(current)
    except Exception as error:
        evidence = getattr(error, "scope_evidence", None)
        failure = {
            "schema_version": "pqdt-global-pilot005-assigned-term-failure/v1",
            "source": "ProQuest Dissertations & Theses Global",
            "pilot": "005",
            "status": "error",
            "diagnostic_only": True,
            "do_not_merge": True,
            "started_at_utc": started_at,
            "failed_at_utc": adapter.utc_now(),
            "stage": "record_assignment_harvest",
            "error_type": type(error).__name__,
            "error": safe_error(error),
            "selected_document_ids": [item["paper_id"] for item in expected_records],
            "scope_restoration": (
                adapter._scope_evidence_dict(evidence)
                if isinstance(evidence, adapter.PQDTScopeEvidence)
                else None
            ),
        }
        failure_path.parent.mkdir(parents=True, exist_ok=True)
        failure_path.write_text(
            json.dumps(failure, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        raise

    if len(passes) != 2 or passes[0] != passes[1]:
        raise RuntimeError("PQDT assignments changed across two complete passes")
    if scope is None or scope.restoration_verified is not True:
        raise RuntimeError("PQDT assignment harvest did not verify scope restoration")

    records = passes[1]
    ps_frequency = Counter(
        term for record in records for term in record["pq_subject_terms"]
    )
    if_frequency = Counter(term for record in records for term in record["index_terms"])
    artifact = {
        "schema_version": SCHEMA,
        "source": "ProQuest Dissertations & Theses Global",
        "source_id": "proquest_dissertations_theses_global",
        "platform": "ProQuest",
        "pilot": "005",
        "status": "complete_two_pass_assignment_readback",
        "diagnostic_only": True,
        "do_not_merge": True,
        "started_at_utc": started_at,
        "completed_at_utc": adapter.utc_now(),
        "preflight": str(preflight_path.relative_to(queries.PILOT_ROOT)),
        "preflight_sha256": queries.file_sha256(preflight_path),
        "method": {
            "passes": 2,
            "record_route": "source-created Abstract/Details view",
            "assignment_identity": (
                "Lateral-search field routes classify mainsubject as PSUB and if as IF. "
                "No account value, opaque detail token, or complete source URL is retained."
            ),
            "fields": {
                "mainsubject": "PQ Subject, PSUB.EXACT",
                "if": "Index term (keyword), IF.EXACT",
                "subject": "broader All subjects & indexing context only",
            },
            "scope": adapter._scope_evidence_dict(scope.evidence),
        },
        "interpretation_boundary": {
            "assignment_evidence": (
                "Each retained PSUB or IF label is visibly assigned to a selected record "
                "through its field-specific lateral-search route."
            ),
            "descriptor_state": (
                "Assignment alone does not establish an exact selectable browse label or a "
                "valid mapping to a protocol block."
            ),
            "eligibility_state": (
                "The selected records are known items for this vocabulary test. This is not "
                "final review screening."
            ),
        },
        "selected_record_count": len(records),
        "records": records,
        "pq_subject_unique_term_count": len(ps_frequency),
        "pq_subject_term_frequency": [
            {"term": term, "assigned_record_count": count}
            for term, count in sorted(
                ps_frequency.items(), key=lambda item: (-item[1], item[0].casefold())
            )
        ],
        "index_term_unique_term_count": len(if_frequency),
        "index_term_frequency": [
            {"term": term, "assigned_record_count": count}
            for term, count in sorted(
                if_frequency.items(), key=lambda item: (-item[1], item[0].casefold())
            )
        ],
        "pass_reconciliation": {
            "pass_1_document_ids": [item["paper_id"] for item in passes[0]],
            "pass_2_document_ids": [item["paper_id"] for item in passes[1]],
            "ordered_records_equal": passes[0] == passes[1],
            "ordered_assignments_equal": passes[0] == passes[1],
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--failure-output", type=Path, default=DEFAULT_FAILURE)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()
    asyncio.run(
        harvest(
            args.preflight.expanduser().resolve(),
            args.output.expanduser().resolve(),
            args.failure_output.expanduser().resolve(),
            args.timeout,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
