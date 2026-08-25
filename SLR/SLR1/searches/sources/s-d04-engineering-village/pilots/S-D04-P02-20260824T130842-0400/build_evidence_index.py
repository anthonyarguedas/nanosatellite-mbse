#!/usr/bin/env python3
"""Build the safe P02 evidence index without reading restricted source rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PILOT_ID = "S-D04-P02-20260824T130842-0400"
ROOT = Path("SLR/SLR1/searches/sources/s-d04-engineering-village/pilots") / PILOT_ID

SPECS = [
    ("manifest.json", "diagnostic manifest", "metadata_only", None),
    ("observations.md", "diagnostic observations and requirement ledger", "metadata_only", None),
    ("preexisting-git-status.txt", "pre-content Git and Part 2 context snapshot", "metadata_only", None),
    ("adapter-provenance-preflight.txt", "current adapter pin and hashes before live work", "metadata_only", None),
    ("launcher-read-only-check-prelive.txt", "first read-only health check before no-source-work stop", "metadata_only", None),
    ("prelive-safety.json", "initial conservative no-source-work safety receipt", "metadata_only", None),
    ("launcher-read-only-check-prelive-recheck.txt", "immediate successful read-only health check", "metadata_only", None),
    ("prelive-safety-recheck.json", "successful AC/caffeinate pre-live receipt", "metadata_only", None),
    ("g01_owned_page_probe.py", "one-shot safe G01 Playwright owned-page probe", "public", None),
    ("g01-safe-receipt.json", "safe G01 navigation/ownership/continuity receipt", "metadata_only", None),
    ("g02-safe-receipt.json", "conditional G02 non-invocation and null-accounting receipt", "metadata_only", None),
    ("postflight_anchor_inspector.py", "read-only redacted anchor-continuity inspector", "public", None),
    ("browser-postflight.json", "redacted browser anchor postflight receipt", "metadata_only", None),
    ("launcher-read-only-check-postflight.txt", "postflight dedicated browser health check", "metadata_only", None),
    ("postflight_system_audit.py", "safe power/caffeinate/sleep audit implementation", "public", None),
    ("system-postflight.json", "initial safe system-audit receipt with unresolved loginwindow query", "metadata_only", None),
    ("system-postflight-recheck.json", "corrected exact-window safe system-audit receipt", "metadata_only", None),
    ("adapter-provenance-postflight.txt", "adapter pin/hash/repository postflight receipt", "metadata_only", None),
    ("adapter-assessment.json", "current adapter code-issue assessment", "metadata_only", None),
    ("restricted-capture-ledger.json", "zero-source-capture rights ledger", "metadata_only", ".searches/s-d04-engineering-village-restricted/S-D04-P02-20260824T130842-0400/"),
    ("postflight-git-status.txt", "postflight worktree, final-events, and Part 2 context receipt", "metadata_only", None),
    ("build_evidence_index.py", "safe evidence-index builder", "public", None),
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise SystemExit("refusing to overwrite evidence index")
    evidence = []
    for index, (name, role, classification, secure_reference) in enumerate(SPECS, start=1):
        path = ROOT / name
        if not path.is_file():
            raise SystemExit(f"required safe evidence path is absent: {name}")
        evidence.append(
            {
                "evidence_id": f"EV-{index:03d}",
                "path": str(path),
                "role": role,
                "access_classification": classification,
                "sha256": digest(path),
                "secure_location_reference": secure_reference,
            }
        )
    data = {
        "schema_version": "slr1-source-pilot-evidence-index/v1",
        "pilot_id": PILOT_ID,
        "status": "blocked",
        "rights_boundary": {
            "restricted_root_reference": ".searches/s-d04-engineering-village-restricted/S-D04-P02-20260824T130842-0400/",
            "restricted_capture_count": 0,
            "policy": "No raw source page, record, export, identifier, cookie, private URL, session/search value, or raw target identifier is retained in this Git packet. G02 did not run.",
        },
        "source_accounting": {
            "paired_total": None,
            "compendex_total": None,
            "inspec_total": None,
            "records_retrieved": 0,
            "adapter_invocation_count": 0,
            "explanation": "G01 was blocked before the conditional adapter gate. Null is failure/blocked accounting, not a zero or partial prefix.",
        },
        "evidence": evidence,
        "unavailable_evidence": [
            {"requirement": "G01 source route/control/access projection", "status": "blocked", "reason": "The one safe projection did not complete; no source state was inferred."},
            {"requirement": "G02 current combined-adapter result", "status": "blocked", "reason": "G01 was not healthy, so the conditional invocation count is zero."},
            {"requirement": "paired row provenance and separate source totals", "status": "untested", "reason": "No source query or result page occurred."},
            {"requirement": "fields, syntax, dates, language, thesauri, export, stable identity, pagination, completeness, explicit zero", "status": "untested", "reason": "Explicitly outside the stopped P02 scope."},
            {"requirement": "S-C01 Compendex/Inspec candidate terminology stage", "status": "untested", "reason": "Explicitly excluded from P02."},
        ],
        "code_issue": "unresolved",
        "semantic_protocol_change": False,
    }
    with output.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, sort_keys=False)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
