#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.0"]
# ///
"""Local P03 integrity validator; it makes no NTRS or browser-source request."""
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
FORBIDDEN_PERSISTED_PATTERNS = [
    r"/var/folders",
    r"/Users/antho",
    r"\.browser-profiles/",
    r"\.browser-apps/",
    r"https?://127\.0\.0\.1:",
    r"https?://localhost:",
    r"https://ntrs\.nasa\.gov/api(?:/|\b)",
    r"/api/citations/search",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(131072), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_rows(path: Path) -> list[tuple[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split(maxsplit=1)
        rows.append((digest, relative.strip()))
    return rows


def markdown_links(path: Path) -> list[str]:
    return re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--pilot-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--adapter-worktree", required=True)
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    pilot = Path(args.pilot_dir).resolve()
    output = Path(args.output).resolve()

    json_errors: list[dict[str, str]] = []
    utf8_errors: list[str] = []
    parsed: dict[str, Any] = {}
    all_files = sorted(path for path in pilot.rglob("*") if path.is_file())
    for path in all_files:
        relative = path.relative_to(pilot).as_posix()
        if path == output:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            utf8_errors.append(relative)
            continue
        if path.suffix == ".json":
            try:
                parsed[relative] = json.loads(text)
            except json.JSONDecodeError as exc:
                json_errors.append({"path": relative, "error_type": type(exc).__name__})

    schema = json.loads((repo / "SLR/SLR1/searches/schemas/pilot-manifest.schema.json").read_text(encoding="utf-8"))
    manifest = parsed.get("manifest.json", {})
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    manifest_errors = [
        {"path": "/".join(str(part) for part in item.absolute_path), "message": item.message}
        for item in sorted(validator.iter_errors(manifest), key=lambda item: list(item.absolute_path))
    ]

    root_mismatches = []
    p01_mismatches = []
    p02_mismatches = []
    for label, output_rows in (("root", root_mismatches), ("p01", p01_mismatches), ("p02", p02_mismatches)):
        snapshot = pilot / f"pre-existing-{label}-packet-sha256.txt" if label == "root" else pilot / f"pre-existing-{label}-sha256.txt"
        for expected, relative in snapshot_rows(snapshot):
            actual = sha256(repo / relative)
            if actual != expected:
                output_rows.append({"path": relative, "expected": expected, "actual": actual})

    evidence = parsed.get("evidence-index.json", {}).get("evidence", [])
    evidence_errors = []
    prefix = "SLR/SLR1/searches/sources/s-d13-nasa-ntrs/pilots/" + pilot.name + "/"
    for entry in evidence if isinstance(evidence, list) else []:
        if not isinstance(entry, dict):
            evidence_errors.append({"path": None, "error": "non_object_entry"})
            continue
        stored = entry.get("path")
        expected = entry.get("sha256")
        if not isinstance(stored, str) or not stored.startswith(prefix) or not isinstance(expected, str):
            evidence_errors.append({"path": stored, "error": "invalid_entry"})
            continue
        relative = stored[len(prefix):]
        target = pilot / relative
        if not target.is_file() or sha256(target) != expected:
            evidence_errors.append({"path": stored, "error": "missing_or_hash_mismatch"})

    link_errors = []
    link_count = 0
    for path in all_files:
        if path.suffix.lower() != ".md":
            continue
        for target in markdown_links(path):
            target = target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            file_target = target.split("#", 1)[0]
            if not file_target:
                continue
            link_count += 1
            if not (path.parent / file_target).resolve().exists():
                link_errors.append({"from": path.relative_to(pilot).as_posix(), "target": target})

    privacy_matches = []
    for path in all_files:
        if path == output or path.name == "validate_p03.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in FORBIDDEN_PERSISTED_PATTERNS:
            if re.search(pattern, text, flags=re.I):
                privacy_matches.append({"path": path.relative_to(pilot).as_posix(), "pattern": pattern})

    partition = parsed.get("partition-accounting.json", {})
    rows = partition.get("partitions", []) if isinstance(partition, dict) else []
    ids = [row.get("partition_id") for row in rows if isinstance(row, dict)]
    partition_ok = (
        ids == REQUIRED_PARTITIONS
        and all(row.get("source_reported_total") is None and row.get("records_retrieved") == 0 and row.get("transport_status") == "blocked_not_sent_after_G01_navigation_failure" for row in rows if isinstance(row, dict))
        and len(rows) == len(REQUIRED_PARTITIONS)
    )
    ledger = parsed.get("query-and-request-ledger.json", {})
    ledger_counts = ledger.get("counts", {}) if isinstance(ledger, dict) else {}
    request_ok = isinstance(ledger_counts, dict) and ledger_counts.get("adapter_invocations") == 1 and ledger_counts.get("post_gate_live_query_operations") == 0 and ledger_counts.get("direct_ntrs_api_calls") == 0 and ledger_counts.get("candidate_imports") == 0
    gate = parsed.get("initial-rendered-gate.json", {})
    gate_ok = isinstance(gate, dict) and gate.get("gate_outcome") == "failed_or_unreconciled" and gate.get("safe_artifact", {}).get("top_level_total") is None
    code = parsed.get("code-issue-assessment.json", {})
    code_value = code.get("code_issue") if isinstance(code, dict) else None
    browser = parsed.get("browser-postflight.json", {})
    sleep = parsed.get("sleep-wake-postflight.json", {})
    browser_ok = isinstance(browser, dict) and browser.get("runtime_and_disk_version_match") is True and browser.get("anchor_intact") is True and browser.get("non_anchor_pages_remaining") == 0 and browser.get("power", {}).get("on_ac_power") is True and browser.get("power", {}).get("battery_percent") == 100 and browser.get("controller_caffeinate", {}).get("passed") is True
    sleep_ok = isinstance(sleep, dict) and sleep.get("sleep_or_wake_observed_during_pilot_window") is False and sleep.get("fresh_browser_prior_sleep_status", {}).get("had_survived_prior_sleep") is False
    adapter_status = subprocess.run(["git", "-C", args.adapter_worktree, "status", "--porcelain=v1"], text=True, capture_output=True, check=False).stdout
    # Do not persist the worktree path; only the clean boolean.
    current_status = subprocess.run(["git", "status", "--porcelain=v1"], cwd=repo, text=True, capture_output=True, check=True).stdout.splitlines()
    allocation_status = (pilot / "git-status-at-allocation.txt").read_text(encoding="utf-8").splitlines()
    status_added = sorted(set(current_status) - set(allocation_status))
    status_removed = sorted(set(allocation_status) - set(current_status))

    result = {
        "schema_version": "slr1-ntrs-p03-validation-receipt/v1",
        "scope": "Local JSON/schema/hash/link/privacy/boundary validation only; no NTRS or browser-source request was made.",
        "manifest_schema": {"valid": not manifest_errors, "errors": manifest_errors},
        "json_and_utf8": {"json_valid": not json_errors, "json_errors": json_errors, "utf8_valid": not utf8_errors, "utf8_errors": utf8_errors},
        "evidence_hashes": {"valid": not evidence_errors, "errors": evidence_errors, "entry_count": len(evidence) if isinstance(evidence, list) else None},
        "markdown_links": {"valid": not link_errors, "checked_relative_links": link_count, "errors": link_errors},
        "privacy": {"valid": not privacy_matches, "matches": privacy_matches},
        "immutability": {"root_packet_hashes_match": not root_mismatches, "root_mismatches": root_mismatches, "p01_hashes_match": not p01_mismatches, "p01_mismatches": p01_mismatches, "p02_hashes_match": not p02_mismatches, "p02_mismatches": p02_mismatches},
        "pilot_rules": {"exact_partition_accounting": partition_ok, "query_and_no_api_accounting": request_ok, "gate_null_stop": gate_ok, "code_issue_value": code_value, "code_issue_value_allowed": code_value in {"true", "false", "unresolved"}, "draft_source_packet_present": (pilot / "draft-source-packet").exists(), "screening_performed": manifest.get("screening_performed"), "candidate_import_permitted": manifest.get("candidate_import_permitted")},
        "browser_postflight": {"valid": browser_ok, "sleep_wake_valid": sleep_ok},
        "adapter_worktree_clean": adapter_status == "",
        "concurrency": {"allocation_status_line_count": len(allocation_status), "postflight_status_line_count": len(current_status), "status_lines_added_after_allocation": status_added, "status_lines_removed_after_allocation": status_removed, "interpretation": "Concurrent status changes outside the assigned P03 directory are not attributed to this pilot. Immutable root/P01/P02 hash snapshots establish the P03 write boundary."},
    }
    result["all_structural_validation_checks_passed"] = bool(
        result["manifest_schema"]["valid"] and result["json_and_utf8"]["json_valid"] and result["json_and_utf8"]["utf8_valid"] and result["evidence_hashes"]["valid"] and result["markdown_links"]["valid"] and result["privacy"]["valid"] and result["immutability"]["root_packet_hashes_match"] and result["immutability"]["p01_hashes_match"] and result["immutability"]["p02_hashes_match"] and result["pilot_rules"]["exact_partition_accounting"] and result["pilot_rules"]["query_and_no_api_accounting"] and result["pilot_rules"]["gate_null_stop"] and result["pilot_rules"]["code_issue_value_allowed"] and result["pilot_rules"]["draft_source_packet_present"] is False and result["pilot_rules"]["screening_performed"] is False and result["pilot_rules"]["candidate_import_permitted"] is False and result["browser_postflight"]["valid"] and result["browser_postflight"]["sleep_wake_valid"] and result["adapter_worktree_clean"]
    )
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_structural_validation_checks_passed": result["all_structural_validation_checks_passed"]}))
    return 0 if result["all_structural_validation_checks_passed"] else 65


if __name__ == "__main__":
    raise SystemExit(main())
