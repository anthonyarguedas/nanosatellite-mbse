#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4"]
# ///
"""Validate the S-D05 P01 packet without touching shared review files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


PARTITIONS = ["A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def query_tree_digest(directory: Path) -> str:
    accumulator = hashlib.sha256()
    for path in sorted(directory.glob("*.txt")):
        accumulator.update(path.name.encode("utf-8"))
        accumulator.update(b"\0")
        accumulator.update(digest(path).encode("ascii"))
        accumulator.update(b"\n")
    return accumulator.hexdigest()


def local_path(base: Path, value: str) -> Path | None:
    if value.startswith("/"):
        return Path(value)
    if "://" in value:
        return None
    return (base / value).resolve()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--pilot-dir", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    root = Path(args.source_root).resolve()
    pilot = Path(args.pilot_dir).resolve()
    output = Path(args.output).resolve()
    schema_path = Path(args.schema).resolve()
    if args.verify_existing:
        require(output.is_file() and not output.is_symlink(), "existing validation receipt is required for verify mode")
    else:
        require(not output.exists() and not output.is_symlink(), "refusing to overwrite validation receipt")

    json_paths = sorted(root.rglob("*.json"))
    parsed: dict[Path, object] = {}
    for path in json_paths:
        parsed[path] = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    manifest_path = pilot / "manifest.json"
    manifest = parsed[manifest_path]
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest),
        key=lambda error: list(error.absolute_path),
    )
    require(not errors, "manifest schema errors: " + "; ".join(error.message for error in errors))
    require(manifest["status"] == "blocked", "manifest status must remain blocked")
    require(manifest["diagnostic_only"] is True, "diagnostic-only invariant failed")
    require(manifest["screening_performed"] is False, "screening invariant failed")
    require(manifest["candidate_import_permitted"] is False, "import invariant failed")
    require(manifest["interface"]["candidate_adapter"]["code_issue"] is True, "code issue not recorded")
    require(all(item["records_retrieved"] == 0 for item in manifest["executions"]), "record-free invariant failed")
    require(all(item["source_reported_total"] is None for item in manifest["executions"]), "null-total invariant failed")

    guideline = (root / "guideline.md").read_text(encoding="utf-8")
    require("status: draft" in guideline and "accepted_pilot_ids: []" in guideline, "guideline draft/acceptance invariant failed")
    spec = parsed[root / "translation-spec.json"]
    require(spec["status"] == "draft_blocked_code_issue_no_live_validation", "translation status changed")
    observed_partition_ids = [item["partition_id"] for item in spec["partitions"]]
    require(observed_partition_ids == PARTITIONS, "translation partition order/coverage differs")

    query_checks: list[dict[str, object]] = []
    for partition in spec["partitions"]:
        require(len(partition["cells"]) == 1, f"{partition['partition_id']} has unexpected cell count")
        cell = partition["cells"][0]
        require(cell["source_reported_total"] is None, f"{partition['partition_id']} has a source total")
        path = (root / cell["exact_query_file"]).resolve()
        data = path.read_bytes()
        require(data.endswith(b"\n") and not data.endswith(b"\n\n"), f"{path.name} terminal LF failure")
        require(len(data) == cell["utf8_bytes_including_terminal_lf"], f"{path.name} byte length differs")
        require(digest(path) == cell["sha256"], f"{path.name} digest differs")
        require(b"*" not in data, f"{path.name} contains a wildcard")
        query_checks.append({"file": path.name, "sha256": digest(path), "bytes": len(data)})

    audit = parsed[pilot / "query-construction-audit.json"]
    require(audit["result"] == "passed_offline_literal_and_structure_audit_only", "query audit did not pass")
    require([item["partition_id"] for item in audit["partitions"]] == PARTITIONS, "query audit partition coverage differs")
    require(all(item["terminal_lf_only"] and not item["wildcard_present"] for item in audit["partitions"]), "query audit LF/wildcard failure")
    require(all(not item["missing_terms"] and not item["missing_or_nonunique_pair_clauses"] for item in audit["partitions"]), "query literal/pair audit failure")

    ledger = parsed[pilot / "restricted-capture-ledger.json"]
    require(ledger["file_count"] == 0 and ledger["files"] == [], "restricted capture ledger is not empty")
    evidence = parsed[pilot / "evidence-index.json"]
    evidence_checks: list[dict[str, object]] = []
    for item in evidence["evidence"]:
        path = local_path(pilot, item["path"])
        if path is None:
            continue
        require(path.exists(), f"evidence path missing: {item['path']}")
        expected = item.get("sha256")
        if path.is_dir():
            actual = query_tree_digest(path)
        else:
            actual = digest(path)
        require(expected == actual, f"evidence digest mismatch: {item['evidence_id']}")
        evidence_checks.append({"id": item["evidence_id"], "sha256": actual})

    markdown_link_errors: list[str] = []
    for markdown in root.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            candidate = (markdown.parent / target).resolve()
            if not candidate.exists():
                markdown_link_errors.append(f"{markdown.relative_to(root)} -> {target}")
    require(not markdown_link_errors, "broken local markdown links: " + "; ".join(markdown_link_errors))

    text_checks: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
            continue
        data = path.read_bytes()
        require(data.endswith(b"\n"), f"missing terminal LF: {path.relative_to(root)}")
        for number, line in enumerate(data.splitlines(), start=1):
            if line.rstrip(b" \t") != line:
                text_checks.append(f"{path.relative_to(root)}:{number}")
    require(not text_checks, "trailing whitespace: " + "; ".join(text_checks))

    diff = subprocess.run(
        ["git", "diff", "--check", "--", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )
    require(diff.returncode == 0 and not diff.stdout and not diff.stderr, "git diff --check failed for packet")
    restricted_root = Path(".searches/s-d05-wiley-restricted/S-D05-P01-20260824T124916-0400")
    require(not restricted_root.exists(), "unexpected restricted capture directory exists despite zero-capture ledger")

    receipt = {
        "schema_version": "slr1-s-d05-packet-validation-receipt/v1",
        "pilot_id": manifest["pilot_id"],
        "result": "passed",
        "manifest_schema": str(schema_path),
        "manifest_format_validation": "passed using Draft202012Validator plus FormatChecker",
        "json_files_parsed": len(json_paths),
        "query_files": query_checks,
        "query_tree_sha256": query_tree_digest(root / "queries"),
        "evidence_hashes_checked": evidence_checks,
        "local_markdown_links": "passed",
        "terminal_lf_and_trailing_whitespace": "passed",
        "git_diff_check_packet": "passed",
        "write_boundary": {
          "packet_root": str(root),
          "restricted_capture_root_created": False,
          "reason": "No source request or raw/source record capture occurred after the offline code gate."
        },
        "invariants": {
          "diagnostic_only": True,
          "screening_performed": False,
          "candidate_import_permitted": False,
          "all_execution_records_retrieved": 0,
          "all_execution_source_totals_null": True,
          "code_issue_true": True
        }
    }
    if args.verify_existing:
        return 0
    output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
