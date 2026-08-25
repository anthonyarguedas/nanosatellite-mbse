#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Apply the P02 pre-source endpoint-blocked status to the D05 draft spec."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
PAIRED = {"BG1", "BG2", "BC1", "BT2"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--pilot-id", required=True)
    parser.add_argument("--protocol-commit", required=True)
    args = parser.parse_args()
    root = Path(args.source_root).resolve()
    path = root / "translation-spec.json"
    spec = json.loads(path.read_text(encoding="utf-8"))
    if spec.get("schema_version") != "slr1-wiley-translation-spec/v1":
        raise SystemExit("unexpected translation specification schema")
    if [item.get("partition_id") for item in spec.get("partitions", [])] != list(PARTITIONS):
        raise SystemExit("unexpected partition coverage")
    spec["status"] = "draft_p02_blocked_before_live_validation_stale_browser_endpoint"
    spec["protocol_commit"] = args.protocol_commit
    spec["source_native_draft"]["field_scope"]["basis"] = "untested_no_current_source_use_p02_stale_browser_endpoint"
    spec["source_native_draft"]["field_scope"]["acceptance_gate"] = (
        "Final use is prohibited until a healthy dedicated browser gate permits current visible "
        "Advanced Search field inventory, exact query echo/rewrite behavior, and one-field operand semantics. "
        "P02 made no Wiley request because its required endpoint check was stale."
    )
    spec["source_native_draft"]["parser_status"] = (
        "P02 regenerated the exact v4 expressions and verified the corrected adapter's source-free no-clobber suite, "
        "but made no Wiley request after the required dedicated endpoint check reported stale. AND/OR/NOT, precedence, "
        "phrase, punctuation, acronym, case, wildcard, expansion, proximity, length, fields, and echo/rewrite remain untested."
    )
    spec["controls"]["diagnostic_publication_date"]["validation_status"] = "untested_no_live_source_use_p02_stale_browser_endpoint"
    spec["controls"]["language"]["basis"] = "untested_no_live_source_use_p02_stale_browser_endpoint"
    spec["controls"]["prohibited_limits"]["basis"] = "offline_planned_no_live_source_use_p02"
    spec["controls"]["articles_and_chapters_vs_collections"] = (
        "Both routes remain untested in P02 because no Wiley request was permitted after the stale endpoint gate; "
        "collections must never be primary-evidence records."
    )
    spec["controls"]["sort_page_size_date_precision"] = (
        "untested in a current Wiley interface; P02 was blocked before H-001 by a stale dedicated browser endpoint."
    )
    spec["controlled_vocabulary"]["reason"] = (
        "No current Advanced Search/indexed-term/hierarchy or record surface was inspected: P02 stopped at the stale "
        "dedicated browser endpoint before a Wiley request."
    )
    spec["query_length_and_cell_policy"]["basis"] = "untested_no_live_source_use_p02_stale_browser_endpoint"
    spec["query_length_and_cell_policy"]["current_cells"] = (
        "One complete v4 cell per partition was regenerated in memory and reconciled byte-for-byte to the root files; "
        "no cell was source-submitted, split, wildcard-compressed, narrowed, or given a source total."
    )
    spec["lossless_union_rule"]["identity"] = (
        "Untested: P02 stopped before a Wiley request, so no stable identifier, ordered pass, or union behavior was observed."
    )
    for partition in spec["partitions"]:
        if len(partition.get("cells", [])) != 1:
            raise SystemExit(f"unexpected cell count for {partition.get('partition_id')}")
        cell = partition["cells"][0]
        if cell.get("source_reported_total") is not None:
            raise SystemExit(f"refusing to overwrite a source total for {partition['partition_id']}")
        cell["query_status"] = (
            "draft_regenerated_p02_pair_semantics_untested_no_source_submission_browser_preflight_blocked"
            if partition["partition_id"] in PAIRED
            else "draft_regenerated_p02_no_source_submission_browser_preflight_blocked"
        )
        cell["source_total_basis"] = "untested_no_live_submission_p02_stale_browser_endpoint"
    spec["p02_correction_status"] = {
        "pilot_id": args.pilot_id,
        "basis": "observed",
        "adapter_no_clobber_verification": "passed source-free against the pinned corrective commit; no new code issue was demonstrated.",
        "browser_gate": "blocked before H-001 because the required dedicated endpoint was not live.",
        "source_requests_made": 0,
        "semantic_change": False,
    }
    spec["evidence_links"] = [
        "pilots/S-D05-P01-20260824T124916-0400/query-construction-audit.json",
        f"pilots/{args.pilot_id}/query-regeneration-audit.json",
        f"pilots/{args.pilot_id}/adapter-verification.json",
        f"pilots/{args.pilot_id}/browser-preflight-failure.json",
    ]
    path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
