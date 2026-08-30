#!/usr/bin/env python3
"""Screen retained 2026 pilot IDs against the diagnostic exact-date boundary.

This is a post-retrieval date-screening control, not a fourteenth candidate
partition.  It preserves the main/PSR source events unchanged and asks only
whether already-retrieved 2026 accessions match an inclusive before-cutoff or
an after-cutoff DOP range.  DOP's Early-Access/final-date basis remains a
source-documented limitation and is reported rather than silently resolved.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from queries import DIAGNOSTIC_CUTOFF, SLR1_DIR, events


AGENT_TOOLS = Path.home() / "agent-tools"
BROWSER_RUNNER = AGENT_TOOLS / "internet" / "skills" / "browser" / "scripts" / "run_with_browser.py"
WOS_ADAPTER = AGENT_TOOLS / "internet" / "skills" / "browser" / "scripts" / "search_web_of_science.py"
PILOT_ROOT = SLR1_DIR / "source-specific" / "web-of-science-core-collection" / "pilots" / "003"
SEARCH_ROOT = PILOT_ROOT / "searches"
ANALYSIS_ROOT = SEARCH_ROOT / "analysis"
LIMIT = 100_000
MAX_PAGES = 2_000
TIMEOUT_SECONDS = 120


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def retained_2026_ids() -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for item in events():
        artifact = SEARCH_ROOT / item.namespace / f"{item.partition_id}.json"
        payload = load(artifact)
        if payload.get("total") is None:
            raise RuntimeError(f"Cannot date-screen a failed event: {artifact}")
        for row in payload.get("results", []):
            identifier = row.get("paperId")
            if row.get("year") == 2026 and isinstance(identifier, str) and identifier not in seen:
                ordered.append(identifier)
                seen.add(identifier)
    return ordered


def accession_union(ids: list[str]) -> str:
    if not ids:
        return "UT=(WOS:000000000000000)"
    return "(" + " OR ".join(f"UT=({identifier})" for identifier in ids) + ")"


def command(query: str, path: Path) -> list[str]:
    return [
        "caffeinate", "-dims", "uv", "run", str(BROWSER_RUNNER), "--",
        "uv", "run", str(WOS_ADAPTER),
        "--raw-query", query,
        "--require-complete",
        "--limit", str(LIMIT),
        "--max-pages", str(MAX_PAGES),
        "--timeout", str(TIMEOUT_SECONDS),
        "--output-path", str(path),
    ]


def main() -> int:
    ANALYSIS_ROOT.mkdir(parents=True, exist_ok=True)
    ids = retained_2026_ids()
    before_query = f"{accession_union(ids)} AND DOP=(1900-01-01/{DIAGNOSTIC_CUTOFF})"
    after_query = f"{accession_union(ids)} AND DOP=(2026-08-30/2100-12-31)"
    plan_path = ANALYSIS_ROOT / "cutoff-control-plan.json"
    before_path = ANALYSIS_ROOT / f"cutoff-on-or-before-{DIAGNOSTIC_CUTOFF}.json"
    after_path = ANALYSIS_ROOT / f"cutoff-after-{DIAGNOSTIC_CUTOFF}.json"
    for path in (plan_path, before_path, after_path):
        if path.exists() or path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json").exists():
            raise SystemExit(f"Refusing to overwrite cutoff control artifact: {path}")
    with plan_path.open("x", encoding="utf-8") as stream:
        json.dump(
            {
                "schema_version": "slr1-wos-pilot-003-cutoff-control-plan/v1",
                "pilot": "003",
                "do_not_merge": True,
                "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
                "ordered_retained_2026_wos_ids": ids,
                "source_scope": "all current Web of Science Core Collection editions",
                "controls": [
                    {"artifact": before_path.name, "query": before_query, "meaning": "inclusive native DOP on-or-before diagnostic cutoff"},
                    {"artifact": after_path.name, "query": after_query, "meaning": "native DOP after diagnostic cutoff"},
                ],
                "limitation": "DOP is a documented source publication-date field, but Clarivate does not document its Early Access/final basis universally; this control does not silently resolve records lacking a decisive DOP match.",
            },
            stream,
            ensure_ascii=False,
            indent=2,
        )
        stream.write("\n")
    summaries = []
    for label, query, path in (("on_or_before", before_query, before_path), ("after", after_query, after_path)):
        result = subprocess.run(command(query, path), check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy())
        if result.returncode != 0:
            diagnostic = "\n".join(value for value in (result.stdout, result.stderr) if value)
            if diagnostic:
                print(diagnostic[-4000:])
        payload = load(path) if path.exists() else {}
        summaries.append({"control": label, "returncode": result.returncode, "artifact": str(path), "total": payload.get("total"), "status": payload.get("output_metadata", {}).get("status")})
    print(json.dumps({"retained_2026_ids": len(ids), "controls": summaries}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
