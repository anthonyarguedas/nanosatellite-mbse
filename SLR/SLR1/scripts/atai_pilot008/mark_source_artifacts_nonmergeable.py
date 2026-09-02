#!/usr/bin/env python3
"""Mark every ATAI Pilot 008 source artifact as pilot-only and nonmergeable."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REASON = "ATAI Pilot 008 bounded-wildcard schedule comparison. This is not a final search."


def mark(path: Path) -> bool:
    value: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != "academic-search-result/v1":
        return False
    value["do_not_merge"] = True
    metadata = value.setdefault("output_metadata", {})
    metadata["merge_eligible"] = False
    metadata["normalized_merge_eligible"] = False
    metadata["pilot_only"] = True
    metadata["non_mergeable_reason"] = REASON
    prisma = metadata.get("prisma_search_run")
    if isinstance(prisma, dict):
        prisma["report_ready"] = False
        reasons = prisma.setdefault("report_readiness_reasons", [])
        if "pilot_non_mergeable" not in reasons:
            reasons.append("pilot_non_mergeable")
    value["pilot_cell"] = {
        "pilot_id": "008",
        "event_kind": "pilot",
        "pilot_only": True,
        "non_mergeable_reason": REASON,
    }
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted((args.pilot_root / "searches").rglob("*.json"))
    marked = [str(path.relative_to(args.pilot_root)) for path in paths if mark(path)]
    receipt = {
        "schema_version": "atai-pilot-008-nonmergeable-marking/v1",
        "pilot": "008",
        "status": "complete",
        "do_not_merge": True,
        "marked_artifact_count": len(marked),
        "marked_artifacts": marked,
        "reason": REASON,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
