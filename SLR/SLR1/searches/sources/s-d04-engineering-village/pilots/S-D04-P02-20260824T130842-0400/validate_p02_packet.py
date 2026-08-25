#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4"]
# ///
"""Validate S-D04 P02 safe artifacts without emitting restricted content."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

PILOT_ID = "S-D04-P02-20260824T130842-0400"
PUBLIC_ROOT = Path("SLR/SLR1/searches/sources/s-d04-engineering-village/pilots") / PILOT_ID
RESTRICTED_ROOT = Path(".searches/s-d04-engineering-village-restricted") / PILOT_ID
SCHEMA_PATH = Path("SLR/SLR1/searches/schemas/pilot-manifest.schema.json")
PART2_PATH = Path("SLR/SLR1/protocol-discovery-and-appraisal.md")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def check_ignore(path: Path) -> bool:
    return subprocess.run(["git", "check-ignore", "-q", str(path)], check=False).returncode == 0


def status_for(path: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all", "--", path],
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout


def add_check(checks: dict[str, Any], errors: list[str], name: str, passed: bool, **details: Any) -> None:
    checks[name] = {**details, "passed": passed}
    if not passed:
        errors.append(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--anchor-id-file", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise SystemExit("refusing to overwrite validation receipt")

    checks: dict[str, Any] = {}
    errors: list[str] = []
    try:
        manifest = load_json(PUBLIC_ROOT / "manifest.json")
        schema = load_json(SCHEMA_PATH)
        schema_errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest))
        add_check(
            checks,
            errors,
            "manifest_draft202012_schema_with_format",
            not schema_errors,
            error_count=len(schema_errors),
        )

        json_paths = sorted(PUBLIC_ROOT.glob("*.json")) + sorted(RESTRICTED_ROOT.glob("*.json"))
        parse_ok = True
        for path in json_paths:
            try:
                load_json(path)
            except Exception:
                parse_ok = False
        add_check(checks, errors, "json_parse", parse_ok, files_checked=len(json_paths))

        evidence_index = load_json(PUBLIC_ROOT / "evidence-index.json")
        evidence = evidence_index.get("evidence", [])
        evidence_ok = isinstance(evidence, list)
        allowed_public = PUBLIC_ROOT.resolve()
        for item in evidence if isinstance(evidence, list) else []:
            path_value = item.get("path") if isinstance(item, dict) else None
            expected = item.get("sha256") if isinstance(item, dict) else None
            path = Path(path_value) if isinstance(path_value, str) else None
            if path is None or not path.is_file() or allowed_public not in path.resolve().parents:
                evidence_ok = False
                continue
            if not isinstance(expected, str) or sha256(path) != expected:
                evidence_ok = False
        add_check(checks, errors, "evidence_paths_and_checksums", evidence_ok, entries_checked=len(evidence) if isinstance(evidence, list) else 0)

        artifacts = manifest.get("artifacts", [])
        artifacts_ok = isinstance(artifacts, list)
        artifact_hashes_checked = 0
        for artifact in artifacts if isinstance(artifacts, list) else []:
            path_value = artifact.get("path") if isinstance(artifact, dict) else None
            path = Path(path_value) if isinstance(path_value, str) else None
            if path is None or not path.is_file() or allowed_public not in path.resolve().parents:
                artifacts_ok = False
                continue
            expected = artifact.get("sha256")
            if expected is not None:
                artifact_hashes_checked += 1
                if sha256(path) != expected:
                    artifacts_ok = False
        add_check(checks, errors, "manifest_artifact_paths", artifacts_ok, count=len(artifacts) if isinstance(artifacts, list) else 0, sha256_values_checked=artifact_hashes_checked)

        g01 = load_json(PUBLIC_ROOT / "g01-safe-receipt.json")
        g02 = load_json(PUBLIC_ROOT / "g02-safe-receipt.json")
        ledger = load_json(PUBLIC_ROOT / "restricted-capture-ledger.json")
        interface_totals = manifest.get("interface", {}).get("source_totals", {})
        accounting_ok = (
            interface_totals == {"paired": None, "compendex": None, "inspec": None}
            and g02.get("total") is None
            and g02.get("records_retrieved") == 0
            and g02.get("partial_prefix_retained") is False
            and ledger.get("source_capture_file_count") == 0
        )
        add_check(checks, errors, "null_zero_accounting", accounting_ok, paired=None, compendex=None, inspec=None, records_retrieved=0)

        no_query_ok = (
            g01.get("navigation_attempt_count") == 1
            and manifest.get("executions", [])[0].get("controls", {}).get("query_submitted") is False
            and g02.get("invocation_count") == 0
            and g02.get("source_query_submitted") is False
        )
        add_check(checks, errors, "fixed_gate_stop_no_G02_query", no_query_ok, g02_adapter_invocation_count=g02.get("invocation_count"))

        browser = load_json(PUBLIC_ROOT / "browser-postflight.json")
        anchor_ok = (
            g01.get("final_continuity", {}).get("anchor_unchanged") is True
            and browser.get("anchor_continuity_verified") is True
            and browser.get("page_target_count") == 1
        )
        add_check(checks, errors, "anchor_continuity", anchor_ok)

        system_postflight = load_json(PUBLIC_ROOT / "system-postflight-recheck.json")
        sleep = system_postflight.get("sleep_wake_events_during_live_source_window", {})
        sleep_ok = (
            sleep.get("pmset_log_checked") is True
            and sleep.get("loginwindow_log_checked") is True
            and sleep.get("pmset_sleep_wake_event_count") == 0
            and sleep.get("loginwindow_sleep_wake_event_count") == 0
        )
        add_check(checks, errors, "power_caffeinate_and_exact_sleep_window", sleep_ok, pmset_sleep_wake_count=sleep.get("pmset_sleep_wake_event_count"), loginwindow_sleep_wake_count=sleep.get("loginwindow_sleep_wake_event_count"))

        restricted_inventory_path = RESTRICTED_ROOT / "restricted-inventory.json"
        restricted_inventory = load_json(restricted_inventory_path)
        declared_inventory = ledger.get("restricted_inventory", {})
        inventory_checksum_matches = (
            isinstance(declared_inventory, dict)
            and declared_inventory.get("sha256") == sha256(restricted_inventory_path)
            and declared_inventory.get("bytes") == restricted_inventory_path.stat().st_size
        )
        rights_ok = (
            check_ignore(restricted_inventory_path)
            and restricted_inventory.get("source_artifact_count") == 0
            and ledger.get("source_capture_file_count") == 0
            and inventory_checksum_matches
        )
        add_check(
            checks,
            errors,
            "restricted_rights_boundary",
            rights_ok,
            restricted_source_artifact_count=restricted_inventory.get("source_artifact_count"),
            restricted_inventory_checksum_matches=inventory_checksum_matches,
        )

        private_anchor = Path(args.anchor_id_file).read_text(encoding="utf-8").strip().encode("ascii")
        raw_anchor_leak = False
        sensitive_key_value_leak = False
        websocket_leak = False
        # Flag identifier/credential-like key values, while not mistaking the
        # local CDP-session variable in the safe inspection scripts for a
        # serialized browser session. A bare session key is only sensitive in
        # URL-query form here.
        key_value = re.compile(
            rb"(?i)(?:\b(?:searchid|sessionid|access[_-]?token|authorization|cookie|token)\s*=|[?&]session(?:id)?\s*=)"
        )
        # Do not make the validator's own literal detection patterns look
        # like captured browser/session data. Every evidence artifact and
        # operational script is scanned; this validator and its receipts are
        # excluded from the content scan and are covered by code review.
        excluded_from_content_scan = {
            Path(__file__).name,
            "validation-receipt.json",
            "validation-receipt-recheck.json",
            "validation-receipt.stdout.txt",
            "validation-receipt.stderr.txt",
            "validation-receipt-recheck.stdout.txt",
            "validation-receipt-recheck.stderr.txt",
        }
        for path in sorted(PUBLIC_ROOT.glob("*")):
            if not path.is_file() or path.name in excluded_from_content_scan:
                continue
            raw = path.read_bytes()
            raw_anchor_leak = raw_anchor_leak or bool(private_anchor and private_anchor in raw)
            sensitive_key_value_leak = sensitive_key_value_leak or bool(key_value.search(raw))
            websocket_leak = websocket_leak or b"ws://127.0.0.1:9237/devtools/" in raw
        leakage_ok = not raw_anchor_leak and not sensitive_key_value_leak and not websocket_leak
        add_check(checks, errors, "no_raw_target_or_session_leakage", leakage_ok, raw_anchor_id=raw_anchor_leak, sensitive_key_value=sensitive_key_value_leak, websocket_url=websocket_leak)

        final_events_clean = status_for("SLR/SLR1/searches/final-events").strip() == ""
        add_check(checks, errors, "final_events_untouched", final_events_clean)

        write_boundary = load_json(PUBLIC_ROOT / "write-boundary-receipt.json")
        write_boundary_ok = (
            write_boundary.get("tracked_diff_paths_match_preexisting_snapshot") is True
            and write_boundary.get("restricted_root_ignored") is True
            and write_boundary.get("final_events_status") == "clean"
        )
        add_check(checks, errors, "no_edits_outside_declared_P02_roots", write_boundary_ok)

        snapshot = (PUBLIC_ROOT / "preexisting-git-status.txt").read_text(encoding="utf-8")
        expected_part2 = next((line.split("=", 1)[1] for line in snapshot.splitlines() if line.startswith("protocol_discovery_and_appraisal_sha256=")), None)
        current_part2 = sha256(PART2_PATH)
        add_check(checks, errors, "part2_context_unchanged_since_snapshot", current_part2 == expected_part2, current_sha256=current_part2)

        boundary_ok = all(path.resolve().is_relative_to(allowed_public) for path in PUBLIC_ROOT.glob("*")) and check_ignore(RESTRICTED_ROOT / "restricted-inventory.json")
        add_check(checks, errors, "declared_write_roots", boundary_ok, public_root=str(PUBLIC_ROOT), restricted_root=str(RESTRICTED_ROOT))
    except Exception:
        errors.append("validator_internal_failure")
        checks["validator_internal_failure"] = {"passed": False}

    data = {
        "schema_version": "slr1-pilot-validation-receipt/v1",
        "pilot_id": PILOT_ID,
        "checked_at": now(),
        "checks": checks,
        "errors": errors,
        "passed": not errors,
        "caveat": "Integrity validation cannot turn the blocked G01 safe-inspection outcome into accepted source evidence or authorize G02/a final run.",
    }
    with output.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
