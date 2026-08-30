#!/usr/bin/env python3
"""Record the required Pilot 003 >100-set investigation without filtering rows."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA = "slr1-scopus-pilot003-large-set-investigation/v1"


def records(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("output_metadata", {}).get("retrieval_complete") is not True:
        raise ValueError(f"Incomplete input: {path}")
    return value["results"]


def control_summary(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    controls = value["output_metadata"].get("controls", {})
    return {
        "scope": controls.get("result_scope", {}).get("effective"),
        "sort": controls.get("sort", {}).get("effective"),
        "language_facets": controls.get("result_facets", {}).get("effective"),
        "document_type_control": "not applied; DOCTYPE was prohibited",
        "subject_area_control": "not applied",
        "access_control": "not applied",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True, type=Path)
    parser.add_argument("--union", required=True, type=Path)
    parser.add_argument("--output-path", required=True, type=Path)
    args = parser.parse_args()
    if args.output_path.exists() or args.output_path.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output_path}")
    root = args.pilot_root
    union = json.loads(args.union.read_text(encoding="utf-8"))
    b1_path = root / "searches/main/strict-ids-B200/B1.json"
    b2_path = root / "searches/main/strict-ids-B200/B2.json"
    b1, b2 = records(b1_path), records(b2_path)
    b1_ids, b2_ids = {row["paperId"] for row in b1}, {row["paperId"] for row in b2}
    types = Counter(
        (row.get("documentType") or "not_exposed")
        for row in [*b1, *b2]
    )
    main_records = union["main"]["records"]
    output = {
        "schema_version": SCHEMA,
        "pilot_id": "003",
        "scope": "Every deduplicated candidate set above 100; no records were removed during this investigation.",
        "sets": [
            {
                "name": "B1",
                "stable_id_count": len(b1_ids),
                "trigger": ">100",
                "controls": control_summary(b1_path),
                "actions": [
                    "Retained the validated visible English facet and Documents/Date (oldest) readback.",
                    "Retained all 164 stable publication IDs; no DOCTYPE, subject, access, or peer-review filter was applied.",
                    "Exact local pair check is not applicable: B1 has no declared paired concept block.",
                    "No INDEXTERMS supplement was applied: Scopus exposes no searchable thesaurus, hierarchy, or expansion switch and no term-to-record mapping was validated for this partition.",
                ],
            },
            {
                "name": "B2",
                "stable_id_count": len(b2_ids),
                "trigger": ">100",
                "controls": control_summary(b2_path),
                "actions": [
                    "Retained the validated visible English facet and Documents/Date (oldest) readback.",
                    "Retained all 180 stable publication IDs; no DOCTYPE, subject, access, or peer-review filter was applied.",
                    "Exact local pair check is not applicable: B2 has no declared paired concept block.",
                    "Observed type labels are audit-only and incomplete; they cannot support a lossless eligible-type filter.",
                ],
                "observed_document_types": dict(sorted(types.items())),
            },
            {
                "name": "B1_union_B2",
                "stable_id_count": len(b1_ids | b2_ids),
                "intersection": len(b1_ids & b2_ids),
                "trigger": ">100",
                "actions": [
                    "Kept the exact source publication-ID union; source-wide title/abstract/key search may match hidden indexed metadata, so a local metadata check cannot safely discard a source hit.",
                    "No unvalidated field restriction, wildcard, descriptor, thesaurus expansion, or document-type condition was introduced.",
                ],
            },
            {
                "name": "main_union",
                "stable_id_count": len(main_records),
                "trigger": ">100",
                "actions": [
                    "Retained all source IDs after cross-partition deduplication; this is a pilot candidate set, not a screened inclusion set.",
                    "2026 records remain date-unresolved against the diagnostic 2026-08-29 cutoff; no cutoff-year record was silently removed.",
                    "The repaired batch native-abstract expansion was attempted and its safe failures are retained. Stable-ID completeness was recovered without representing empty abstracts as source absence.",
                ],
            },
            {
                "name": "PSR2_full_count",
                "source_total": 237,
                "trigger": ">100",
                "status": "incomplete_lossless_recovery",
                "actions": [
                    "Split only declared OR factors into prospectively recorded lossless cells; no language, type, subject, access, or descriptor limiter was added.",
                    "Some source cells still ended with null-total safe failures. No partial PSR2 cell ledger is presented as a complete union.",
                ],
            },
        ],
        "conclusion": "No validated no-loss precision field existed beyond the required main-route English facet. Source-controlled INDEXTERMS cannot be expanded through a searchable thesaurus, and observed type labels cannot justify DOCTYPE. All candidate rows remain retained for later screening when their source event is complete.",
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
