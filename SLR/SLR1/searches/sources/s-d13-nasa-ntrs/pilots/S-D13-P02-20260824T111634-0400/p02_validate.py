#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.0"]
# ///
"""P02 local postflight and manifest validation without source-network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

REQUIRED_PARTITIONS = ["A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"]
FORBIDDEN_PATTERNS = [
    r"/var/folders",
    r"/Users/antho",
    r"agent-tools-ntrs-codefix",
    r"Set-Cookie:\\s*[^\\s]",
    r"Cookie:\\s*[^\\s]",
    r"Authorization:\\s*(?:Bearer|Basic)\\s+[^\\s]",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(131072), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_hash_snapshot(path: Path) -> list[tuple[str, str]]:
    output: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split(maxsplit=1)
        output.append((digest, relative.strip()))
    return output


def markdown_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--pilot-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--adapter-worktree", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    pilot = Path(args.pilot_dir).resolve()
    manifest_path = Path(args.manifest).resolve()
    schema_path = Path(args.schema).resolve()
    output_path = Path(args.output).resolve()

    pre_status = (pilot / "pre-existing-git-status.txt").read_text(encoding="utf-8").splitlines()
    current_status = subprocess.run(
        ["git", "status", "--porcelain=v1"], cwd=repo, check=True, text=True, capture_output=True
    ).stdout.splitlines()
    pre_set, current_set = set(pre_status), set(current_status)
    status_added = sorted(current_set - pre_set)
    status_removed = sorted(pre_set - current_set)
    status_unchanged = sorted(current_set & pre_set)

    root_mismatches = []
    for expected, relative in parse_hash_snapshot(pilot / "pre-existing-root-packet-sha256.txt"):
        actual = sha256_file(repo / relative)
        if actual != expected:
            root_mismatches.append({"path": relative, "expected": expected, "actual": actual})
    p01_mismatches = []
    for expected, relative in parse_hash_snapshot(pilot / "pre-existing-p01-sha256.txt"):
        actual = sha256_file(repo / relative)
        if actual != expected:
            p01_mismatches.append({"path": relative, "expected": expected, "actual": actual})

    json_errors: list[dict[str, str]] = []
    parsed_json: dict[str, Any] = {}
    all_files = sorted(path for path in pilot.rglob("*") if path.is_file())
    for path in all_files:
        relative = path.relative_to(pilot).as_posix()
        if path.suffix != ".json" or path == output_path:
            continue
        try:
            parsed_json[relative] = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            json_errors.append({"path": relative, "error_type": type(error).__name__})

    private_matches: list[dict[str, str]] = []
    for path in all_files:
        # Search persisted evidence/receipts only. The validator's own source
        # contains detection patterns, which are not retained source data.
        if path == output_path or path.suffix.lower() not in {".json", ".md", ".txt"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, content, flags=re.I):
                private_matches.append({"path": path.relative_to(pilot).as_posix(), "pattern": pattern})

    bad_links: list[dict[str, str]] = []
    checked_links = 0
    for path in all_files:
        if path.suffix.lower() != ".md":
            continue
        for target in markdown_links(path):
            target = target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            target_file = target.split("#", 1)[0]
            if not target_file:
                continue
            checked_links += 1
            if not (path.parent / target_file).resolve().exists():
                bad_links.append({"from": path.relative_to(pilot).as_posix(), "target": target})

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    manifest_errors = [
        {"path": "/".join(str(item) for item in error.absolute_path), "message": error.message}
        for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.absolute_path))
    ]

    audit = parsed_json.get("offline-partition-audit.json", {})
    rows = audit.get("nine_partition_receipts", []) if isinstance(audit, dict) else []
    audit_ids = [row.get("partition_id") for row in rows if isinstance(row, dict)]
    audit_cells_ok = all(
        isinstance(row, dict)
        and row.get("offline_literal_and_boolean_audit_passed") is True
        and row.get("p02_live_transport_status") == "blocked_before_request_by_unreconciled_mandatory_early-gate_timeout"
        and row.get("p02_source_reported_total") is None
        for row in rows
    )
    query_path = pilot / "queries/Q01-minimal-nanosatellite.txt"
    query_raw = query_path.read_bytes()
    try:
        query_raw.decode("utf-8")
        query_utf8 = True
    except UnicodeDecodeError:
        query_utf8 = False

    gate = parsed_json.get("early-gate-decision.json", {})
    adapter_status = subprocess.run(
        ["git", "status", "--porcelain=v1"], cwd=Path(args.adapter_worktree), check=True, text=True, capture_output=True
    ).stdout
    source_request_count = 2 if (pilot / "health-receipt.json").exists() and (pilot / "minimal-search-envelope-receipt.json").exists() else None
    code_issue_value = gate.get("code_issue", {}).get("value") if isinstance(gate, dict) else None

    result = {
        "schema_version": "slr1-ntrs-p02-postflight-validation/v1",
        "scope": "Local validation only; no NTRS request was made by this validator.",
        "manifest_schema": {
            "path": "SLR/SLR1/searches/schemas/pilot-manifest.schema.json",
            "valid": not manifest_errors,
            "errors": manifest_errors,
        },
        "json_parse": {"valid": not json_errors, "files_parsed": sorted(parsed_json), "errors": json_errors},
        "link_validation": {"valid": not bad_links, "checked_relative_links": checked_links, "errors": bad_links},
        "query_encoding": {
            "p02_executed_query_utf8_valid": query_utf8,
            "p02_executed_query_has_no_line_ending": b"\n" not in query_raw and b"\r" not in query_raw,
            "p02_executed_query_sha256": hashlib.sha256(query_raw).hexdigest(),
        },
        "nine_partition_coverage": {
            "required_ids": REQUIRED_PARTITIONS,
            "observed_ids": audit_ids,
            "exact_coverage": audit_ids == REQUIRED_PARTITIONS,
            "offline_literal_boolean_hash_audit_passed": audit_cells_ok,
        },
        "integrity": {
            "root_packet_hashes_match_preflight": not root_mismatches,
            "root_packet_mismatches": root_mismatches,
            "p01_hashes_match_preflight": not p01_mismatches,
            "p01_mismatches": p01_mismatches,
            "private_path_cookie_or_session_value_matches": private_matches,
            "adapter_worktree_clean": adapter_status == "",
        },
        "concurrency": {
            "preflight_status_line_count": len(pre_status),
            "postflight_status_line_count": len(current_status),
            "status_lines_added_after_preflight": status_added,
            "status_lines_removed_after_preflight": status_removed,
            "status_lines_unchanged_from_preflight": status_unchanged,
            "interpretation": "Git status treats the already-untracked NTRS source packet as one pre-existing directory entry; root/P01 hash comparisons separately protect immutable pre-existing packet files. Added/removed status lines outside the NTRS packet are concurrent/unrelated to this P02 write boundary unless independently attributed by their owner.",
        },
        "early_gate": {
            "source_request_count": source_request_count,
            "code_issue_value": code_issue_value,
            "code_issue_value_allowed": code_issue_value in {"true", "false", "unresolved"},
            "draft_source_packet_present": (pilot / "draft-source-packet").exists(),
        },
    }
    result["all_validation_checks_passed"] = bool(
        result["manifest_schema"]["valid"]
        and result["json_parse"]["valid"]
        and result["link_validation"]["valid"]
        and result["query_encoding"]["p02_executed_query_utf8_valid"]
        and result["query_encoding"]["p02_executed_query_has_no_line_ending"]
        and result["nine_partition_coverage"]["exact_coverage"]
        and result["nine_partition_coverage"]["offline_literal_boolean_hash_audit_passed"]
        and result["integrity"]["root_packet_hashes_match_preflight"]
        and result["integrity"]["p01_hashes_match_preflight"]
        and not result["integrity"]["private_path_cookie_or_session_value_matches"]
        and result["integrity"]["adapter_worktree_clean"]
        and result["early_gate"]["source_request_count"] == 2
        and result["early_gate"]["code_issue_value_allowed"]
        and result["early_gate"]["draft_source_packet_present"] is False
    )
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_validation_checks_passed": result["all_validation_checks_passed"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
