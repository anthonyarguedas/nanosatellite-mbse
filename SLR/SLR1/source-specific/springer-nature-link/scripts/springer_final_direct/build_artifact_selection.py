#!/usr/bin/env python3
"""Publish the accepted Springer final-search artifact selection."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import os
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCHEMA = "slr1-final-direct-artifact-selection/v1"
SOURCE_ID = "springer_nature_link"
RECONCILIATION_SCHEMA = "slr1-springer-nature-link-final-reconciliation/v1"
ASSESSMENT_SCHEMA = "slr1-springer-nature-link-final-assessment/v2"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve(strict=False).relative_to(REPOSITORY_ROOT))


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    descriptor, name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build(reconciliation_path: Path, assessment_path: Path) -> dict[str, Any]:
    reconciliation = load(reconciliation_path)
    assessment = load(assessment_path)
    if (
        reconciliation.get("schema_version") != RECONCILIATION_SCHEMA
        or reconciliation.get("success") is not True
        or assessment.get("schema_version") != ASSESSMENT_SCHEMA
        or assessment.get("status") != "passed"
        or assessment.get("final_reconciliation_sha256")
        != digest(reconciliation_path)
        or assessment.get("validation_errors") != []
    ):
        raise ValueError("The final Springer reconciliation or assessment is incomplete")
    rows = reconciliation.get("source_cells")
    if not isinstance(rows, list) or len(rows) != 67:
        raise ValueError("The final Springer source-cell selection changed")
    artifacts = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("The final Springer source-cell selection is malformed")
        path = REPOSITORY_ROOT / str(row.get("artifact", ""))
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing accepted Springer artifact {path}")
        relative_path = relative(path)
        if relative_path in seen:
            raise ValueError(f"Repeated accepted Springer artifact {relative_path}")
        seen.add(relative_path)
        if (
            row.get("artifact_sha256") != digest(path)
            or row.get("artifact_bytes") != path.stat().st_size
        ):
            raise ValueError(f"Changed accepted Springer artifact {relative_path}")
        value = load(path)
        metadata = value.get("output_metadata")
        if (
            value.get("schema_version") != "academic-search-result/v1"
            or not isinstance(metadata, Mapping)
            or metadata.get("merge_eligible") is not True
            or metadata.get("retrieval_complete") is not True
        ):
            raise ValueError(f"Invalid accepted Springer artifact {relative_path}")
        artifacts.append(
            {
                "source_id": SOURCE_ID,
                "partition_id": row["partition_id"],
                "cell_id": row["cell_id"],
                "source_run_id": row["source_run_id"],
                "path": relative_path,
                "sha256": digest(path),
                "byte_count": path.stat().st_size,
            }
        )
    return {
        "schema_version": SCHEMA,
        "status": "complete",
        "source": "Springer Nature Link",
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "purpose": (
            "Select only reconciled final source events and exclude superseded "
            "normal outputs from direct-review deduplication."
        ),
        "reconciliation": relative(reconciliation_path),
        "reconciliation_sha256": digest(reconciliation_path),
        "assessment": relative(assessment_path),
        "assessment_sha256": digest(assessment_path),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "created_at_utc": now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconciliation", type=Path, required=True)
    parser.add_argument("--assessment", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build(args.reconciliation, args.assessment)
    write_new(args.output, value)
    print(json.dumps({"saved": str(args.output), "artifacts": value["artifact_count"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
