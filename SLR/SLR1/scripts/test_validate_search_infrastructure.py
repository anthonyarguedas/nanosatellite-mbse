#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.18,<5",
# ]
# ///
"""Focused regression tests for fail-closed checkpointed pilot campaigns."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_search_infrastructure as infrastructure  # noqa: E402

ROOT = SCRIPT_DIR.parent
SEARCHES = ROOT / "searches"
TEMPLATE_PATH = SEARCHES / "templates" / "pilot-campaign.template.json"
MANIFEST_TEMPLATE_PATH = SEARCHES / "templates" / "pilot-manifest.template.json"
VALIDATOR_PATH = SCRIPT_DIR / "validate_search_infrastructure.py"


def campaign() -> dict[str, Any]:
    return copy.deepcopy(json.loads(TEMPLATE_PATH.read_text(encoding="utf-8")))


def manifest_template() -> dict[str, Any]:
    return copy.deepcopy(json.loads(MANIFEST_TEMPLATE_PATH.read_text(encoding="utf-8")))


def gate(data: dict[str, Any], gate_id: str) -> dict[str, Any]:
    return next(item for item in data["capability_gates"] if item["gate_id"] == gate_id)


def sha256(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> str:
    contents = json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(contents)
    return sha256(contents)


def set_terminal_cancelled(data: dict[str, Any]) -> None:
    attempt = data["attempts"][-1]
    terminal = attempt["terminal"]
    terminal.update(
        {
            "outcome": "cancelled",
            "category": "operator_cancellation",
            "provider_failure": False,
            "cancelled_by": "operator",
            "reason": "Operator stopped this attempt before another source operation.",
        }
    )
    data["status"] = "cancelled"
    data["acceptance"] = None
    data["cancellation"] = {
        "attempt_id": attempt["attempt_id"],
        "kind": "operator_cancellation",
        "cancelled_by": "operator",
        "cancelled_at": "2026-08-24T15:11:00+00:00",
        "reason": "Operator stopped the campaign.",
        "provider_failure": False,
    }


def browser_terminal_receipt(
    attempt: dict[str, Any], receipt_name: str
) -> dict[str, Any]:
    common = {
        "attempt_id": attempt["attempt_id"],
        "controller": {
            "controller_id": "controller-fixture",
            "owns_attempt": True,
            "ownership_verified": True,
        },
        "verified_at": "2026-08-24T15:11:00+00:00",
        "sanitized_for_campaign": True,
    }
    if receipt_name == "cleanup_receipt":
        return {
            "schema_version": "slr1-browser-cleanup-receipt/v1",
            "receipt_kind": "browser_cleanup",
            **common,
            "cleanup": {
                "owned_pages_closed": True,
                "controller_anchor_preserved": True,
                "cleanup_verified": True,
            },
        }
    return {
        "schema_version": "slr1-shared-lease-release-receipt/v1",
        "receipt_kind": "shared_lease_release",
        **common,
        "lease": {
            "lease_id": "fixture-shared-browser-lease",
            "released_by_controller": True,
            "release_verified": True,
        },
    }


def accepted_campaign() -> dict[str, Any]:
    """Turn the small template fixture into a structurally accepted campaign."""
    data = campaign()
    data["status"] = "accepted"
    data["acceptance"] = {
        "accepted_by": "human reviewer",
        "accepted_at": "2026-08-24T15:20:00+00:00",
        "rationale": "All required source-plan gates have current valid evidence.",
    }
    p2 = data["attempts"][1]
    p2["source_operations"]["operations"][0].update(
        {
            "outcome": "success",
            "source_reported_total": 1,
            "records_retrieved": 0,
        }
    )
    p2["terminal"].update(
        {
            "outcome": "completed",
            "category": "completed",
            "provider_failure": False,
            "reason": "Corrective diagnostic completed.",
        }
    )
    pagination = gate(data, "G-PAGINATION-CONTROL")
    pagination.update(
        {
            "status": "passed",
            "reusable": True,
            "invalidation": None,
            "notes": "Observed pagination control passed after the bounded repair.",
        }
    )
    identity = gate(data, "G-PAGE-IDENTITY")
    identity.update(
        {
            "status": "passed",
            "reusable": True,
            "invalidation": None,
            "notes": "Observed identity check remains valid.",
        }
    )
    identity["evidence"][0]["validity"] = "valid"
    data["attempts"][0]["evidence"][2]["validity"] = "valid"

    required_gates = infrastructure.TASK_SOURCE_REQUIRED_GATE_PLANS[
        (data["task_id"], data["source_id"])
    ]
    existing_gate_ids = {item["gate_id"] for item in data["capability_gates"]}
    for gate_id in required_gates:
        if gate_id in existing_gate_ids:
            continue
        suffix = gate_id.removeprefix("G-")
        evidence_path = f"pilots/{p2['attempt_id']}/accepted-{suffix.lower()}.json"
        p2["evidence"].append(
            {
                "evidence_id": f"E-P02-{suffix}",
                "gate_id": gate_id,
                "path": evidence_path,
                "sha256": "e" * 64,
                "validity": "valid",
                "basis": "observed",
            }
        )
        data["capability_gates"].append(
            {
                "gate_id": gate_id,
                "checkpoint_id": f"CP-{suffix}-P02",
                "attempt_id": p2["attempt_id"],
                "requirement": f"Accepted fixture verifies {suffix.lower()}.",
                "depends_on": [],
                "status": "passed",
                "observed_basis": "observed",
                "original_observed_basis": "observed",
                "evidence": [
                    {
                        "path": evidence_path,
                        "sha256": "e" * 64,
                        "validity": "valid",
                    }
                ],
                "reusable": True,
                "carried_forward": False,
                "carry_forward": None,
                "source_operation_count": 0,
                "semantic_impact": {
                    "classification": "none",
                    "review_effect": False,
                    "rationale": "The fixture evidence does not change review semantics.",
                },
                "invalidation": None,
                "notes": "",
            }
        )
    return data


@contextmanager
def materialized_campaign(
    data: dict[str, Any] | None = None,
    *,
    legacy_manifests: bool = False,
) -> Iterator[tuple[Path, Path, dict[str, Any], Path]]:
    """Create a complete source packet with hashed evidence and linked manifests."""
    temporary = tempfile.TemporaryDirectory()
    try:
        temporary_root = Path(temporary.name)
        searches_root = temporary_root / "searches"
        shutil.copytree(SEARCHES / "schemas", searches_root / "schemas")
        shutil.copyfile(ROOT / "protocol.md", searches_root.parent / "protocol.md")
        shutil.copyfile(
            SEARCHES / "search-concept-dictionary.json",
            searches_root / "search-concept-dictionary.json",
        )
        source_packet = searches_root / "sources" / "s-d01-fixture"
        source_packet.mkdir(parents=True)
        data = copy.deepcopy(data if data is not None else campaign())
        data["protocol_fingerprint"] = sha256(
            (searches_root.parent / "protocol.md").read_bytes()
        )
        data["dictionary_fingerprint"] = sha256(
            (searches_root / "search-concept-dictionary.json").read_bytes()
        )

        evidence_hashes: dict[str, str] = {}
        for attempt_index, attempt in enumerate(data["attempts"]):
            for evidence_index, evidence in enumerate(attempt["evidence"]):
                path = source_packet / evidence["path"]
                contents = f"evidence-{attempt_index}-{evidence_index}\n".encode()
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(contents)
                digest = sha256(contents)
                evidence["sha256"] = digest
                evidence_hashes[evidence["path"]] = digest
        for item in data["capability_gates"]:
            for evidence in item["evidence"]:
                evidence["sha256"] = evidence_hashes[evidence["path"]]
            if item["carry_forward"] is not None:
                for evidence in item["carry_forward"]["evidence"]:
                    evidence["sha256"] = evidence_hashes[evidence["path"]]
        for snapshot in data["gate_status_snapshots"]:
            for evidence in snapshot["evidence"]:
                evidence["sha256"] = evidence_hashes[evidence["path"]]

        for attempt in data["attempts"]:
            terminal = attempt["terminal"]
            if terminal["browser_backed"]:
                for receipt_name in ("cleanup_receipt", "lease_receipt"):
                    receipt = terminal[receipt_name]
                    if receipt is None:
                        continue
                    receipt_path = source_packet / receipt["path"]
                    receipt_contents = json_bytes(
                        browser_terminal_receipt(attempt, receipt_name)
                    )
                    receipt_path.parent.mkdir(parents=True, exist_ok=True)
                    receipt_path.write_bytes(receipt_contents)
                    receipt["sha256"] = sha256(receipt_contents)

            manifest = manifest_template()
            manifest.update(
                {
                    "pilot_id": attempt["attempt_id"],
                    "task_id": data["task_id"],
                    "source_id": data["source_id"],
                    "method_type": data["method_type"],
                    "started_at": attempt["allocation"]["allocated_at"],
                }
            )
            if not legacy_manifests:
                manifest.update(
                    {
                        "campaign": {
                            "campaign_id": data["campaign_id"],
                            "attempt_id": attempt["attempt_id"],
                        },
                        # pilot-manifest.schema.json predates the campaign-only
                        # terminal verification state; links retain its old shape.
                        "attempt_terminal": {
                            key: value
                            for key, value in attempt["terminal"].items()
                            if key != "terminal_verification"
                        },
                    }
                )
            else:
                manifest.pop("campaign", None)
                manifest.pop("attempt_terminal", None)
            manifest["status"] = {
                "completed": "complete",
                "blocked": "blocked",
                "failed": "failed",
                "cancelled": "cancelled",
            }[attempt["terminal"]["outcome"]]
            attempt["manifest_sha256"] = write_json(
                source_packet / attempt["manifest_path"], manifest
            )

        attempts_by_id = {
            attempt["attempt_id"]: attempt for attempt in data["attempts"]
        }
        for snapshot in data["gate_status_snapshots"]:
            source_attempt = attempts_by_id[snapshot["attempt_id"]]
            snapshot["manifest_path"] = source_attempt["manifest_path"]
            snapshot["manifest_sha256"] = source_attempt["manifest_sha256"]

        campaign_path = source_packet / "campaign.json"
        write_json(campaign_path, data)
        yield searches_root, campaign_path, data, source_packet
    finally:
        temporary.cleanup()


def save_campaign(path: Path, data: dict[str, Any]) -> None:
    write_json(path, data)


def rewrite_linked_manifest_terminal(
    source_packet: Path, attempt: dict[str, Any]
) -> None:
    manifest_path = source_packet / attempt["manifest_path"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["attempt_terminal"] = {
        key: value
        for key, value in attempt["terminal"].items()
        if key != "terminal_verification"
    }
    attempt["manifest_sha256"] = write_json(manifest_path, manifest)


def source_campaign(source_directory: str) -> dict[str, Any]:
    return json.loads(
        (SEARCHES / "sources" / source_directory / "campaign.json").read_text(
            encoding="utf-8"
        )
    )


@contextmanager
def copied_source_campaign(
    source_directory: str,
) -> Iterator[tuple[Path, Path, Path]]:
    """Isolate a real campaign packet without mutating immutable evidence."""
    temporary = tempfile.TemporaryDirectory()
    try:
        temporary_root = Path(temporary.name)
        searches_root = temporary_root / "searches"
        shutil.copytree(SEARCHES / "schemas", searches_root / "schemas")
        shutil.copyfile(ROOT / "protocol.md", searches_root.parent / "protocol.md")
        shutil.copyfile(
            SEARCHES / "search-concept-dictionary.json",
            searches_root / "search-concept-dictionary.json",
        )
        source_packet = searches_root / "sources" / source_directory
        shutil.copytree(SEARCHES / "sources" / source_directory, source_packet)
        yield searches_root, source_packet / "campaign.json", source_packet
    finally:
        temporary.cleanup()


class PilotCampaignValidationTests(unittest.TestCase):
    def test_plain_python_without_jsonschema_fails_closed(self) -> None:
        result = subprocess.run(
            [sys.executable, "-S", str(VALIDATOR_PATH)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("jsonschema is required", result.stderr)
        self.assertIn("uv run", result.stderr)

    def test_template_and_real_campaign_scan(self) -> None:
        infrastructure.validate_campaign_artifact(campaign())
        with materialized_campaign() as (searches_root, _, _, _):
            self.assertEqual(
                infrastructure.validate_campaign_artifacts(searches_root), 1
            )

    def test_evidence_path_traversal_is_rejected(self) -> None:
        with materialized_campaign() as (searches_root, campaign_path, data, _):
            data["attempts"][0]["evidence"][0]["path"] = "../outside.json"
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(AssertionError, "path traversal"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_evidence_symlink_escape_is_rejected(self) -> None:
        with materialized_campaign() as (searches_root, _, data, source_packet):
            evidence_path = source_packet / data["attempts"][0]["evidence"][0]["path"]
            outside = source_packet.parent / "outside.json"
            outside.write_text("outside\n", encoding="utf-8")
            evidence_path.unlink()
            evidence_path.symlink_to(outside)
            with self.assertRaisesRegex(AssertionError, "escapes or is missing"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_evidence_hash_mismatch_is_rejected(self) -> None:
        with materialized_campaign() as (searches_root, _, data, source_packet):
            evidence_path = source_packet / data["attempts"][0]["evidence"][0]["path"]
            evidence_path.write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "SHA-256 does not match"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_real_campaign_fingerprint_mismatch_is_rejected(self) -> None:
        with materialized_campaign() as (searches_root, campaign_path, data, _):
            data["protocol_fingerprint"] = "f" * 64
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(AssertionError, "protocol_fingerprint"):
                infrastructure.validate_campaign_artifacts(searches_root)

        with materialized_campaign() as (searches_root, campaign_path, data, _):
            data["dictionary_fingerprint"] = "f" * 64
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(AssertionError, "dictionary_fingerprint"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_technical_decision_uses_immutable_manifest_start(self) -> None:
        with materialized_campaign() as (searches_root, campaign_path, data, _):
            attempt = data["attempts"][1]
            data["decisions"][0]["decided_at"] = "2026-08-24T15:10:00+00:00"
            # This mutable allocation time cannot turn a post-start decision into
            # prospective authorization. The linked manifest still starts at 15:10.
            attempt["allocation"]["allocated_at"] = "2026-08-24T15:11:00+00:00"
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(
                AssertionError, "must precede immutable .*manifest.started_at"
            ):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_campaign_text_rejects_local_execution_details_at_every_status(
        self,
    ) -> None:
        cases = (
            (
                "gate requirement",
                "/Users/reviewer/private.json",
                "absolute path",
                lambda data, value: gate(data, "G-FIELD-BOUNDARY").__setitem__(
                    "requirement", value
                ),
            ),
            (
                "gate notes",
                "--profile-directory=Default",
                "browser profile",
                lambda data, value: gate(data, "G-FIELD-BOUNDARY").__setitem__(
                    "notes", value
                ),
            ),
            (
                "controller rationale",
                "google-chrome --headless",
                "browser command",
                lambda data, value: data["controller_authorization"].__setitem__(
                    "rationale", value
                ),
            ),
            (
                "decision rationale",
                "open -a Google Chrome",
                "browser command",
                lambda data, value: data["decisions"][0].__setitem__(
                    "rationale", value
                ),
            ),
            (
                "terminal reason",
                "/private/var/folders/terminal.txt",
                "absolute path",
                lambda data, value: data["attempts"][1]["terminal"].__setitem__(
                    "reason", value
                ),
            ),
        )
        for name, value, message, mutate in cases:
            with self.subTest(name=name):
                data = campaign()
                mutate(data, value)
                with self.assertRaisesRegex(AssertionError, message):
                    infrastructure.validate_campaign_artifact(data)

    def test_campaign_file_rejects_unsafe_raw_campaign_text(self) -> None:
        with materialized_campaign() as (searches_root, campaign_path, _, _):
            contents = campaign_path.read_text(encoding="utf-8")
            safe_rationale = (
                '"rationale": "Controller may allocate bounded behavior-preserving '
                'repairs without changing the review method."'
            )
            self.assertIn(safe_rationale, contents)
            campaign_path.write_text(
                contents.replace(
                    safe_rationale,
                    '"rationale": "/Users/reviewer/private.json",\n    '
                    + safe_rationale,
                    1,
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(AssertionError, "unsafe local absolute path"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_acceptance_candidate_rejects_unsafe_local_evidence(self) -> None:
        cases = (
            (
                "accepted",
                b'{"path": "/Users/reviewer/private.json"}\n',
                "absolute path",
            ),
            (
                "accepted",
                b'{"profile": "--profile-directory=Default"}\n',
                "browser profile",
            ),
            (
                "ready_for_acceptance_review",
                b'{"command": "google-chrome --headless"}\n',
                "browser command",
            ),
        )
        for status, contents, message in cases:
            with self.subTest(status=status):
                data = accepted_campaign()
                data["status"] = status
                if status != "accepted":
                    data["acceptance"] = None
                with materialized_campaign(data) as (
                    searches_root,
                    campaign_path,
                    data,
                    source_packet,
                ):
                    attempt = data["attempts"][1]
                    evidence = next(
                        item
                        for item in attempt["evidence"]
                        if item["gate_id"] == "G-PAGINATION-CONTROL"
                    )
                    digest = sha256(contents)
                    (source_packet / evidence["path"]).write_bytes(contents)
                    evidence["sha256"] = digest
                    gate(data, "G-PAGINATION-CONTROL")["evidence"][0]["sha256"] = digest
                    save_campaign(campaign_path, data)
                    with self.assertRaisesRegex(AssertionError, message):
                        infrastructure.validate_campaign_artifacts(searches_root)

    def test_campaign_and_attempt_task_prefixes_must_match_task(self) -> None:
        data = campaign()
        data["campaign_id"] = "S-D02-C01-20260824T150000+0000"
        with self.assertRaisesRegex(AssertionError, "wrong task prefix"):
            infrastructure.validate_campaign_artifact(data)

        data = campaign()
        data["attempts"][0]["attempt_id"] = "S-D02-P01-20260824T150000+0000"
        with self.assertRaisesRegex(AssertionError, "wrong task prefix"):
            infrastructure.validate_campaign_artifact(data)

    def test_linked_manifest_must_match_campaign(self) -> None:
        with materialized_campaign() as (
            searches_root,
            campaign_path,
            data,
            source_packet,
        ):
            attempt = data["attempts"][0]
            manifest_path = source_packet / attempt["manifest_path"]
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["campaign"]["campaign_id"] = "S-D01-C99-20260824T150000+0000"
            attempt["manifest_sha256"] = write_json(manifest_path, manifest)
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(AssertionError, "campaign_id does not match"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_unlinked_new_manifest_cannot_claim_legacy_shape(self) -> None:
        with materialized_campaign(legacy_manifests=True) as (searches_root, _, _, _):
            with self.assertRaisesRegex(AssertionError, "new attempt must include"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_accepted_campaign_requires_observed_not_inferred_catalog_gate(
        self,
    ) -> None:
        data = accepted_campaign()
        query = gate(data, "G-QUERY-TRANSPORT")
        query["observed_basis"] = "inferred"
        query["original_observed_basis"] = "inferred"
        data["attempts"][0]["evidence"][0]["basis"] = "inferred"
        with self.assertRaisesRegex(AssertionError, "inferred or untested"):
            infrastructure.validate_campaign_artifact(data)

    def test_accepted_campaign_requires_each_catalog_gate(self) -> None:
        data = accepted_campaign()
        data["capability_gates"] = [
            item
            for item in data["capability_gates"]
            if item["gate_id"] != "G-PAGE-IDENTITY"
        ]
        data["attempts"][0]["evidence"] = [
            item
            for item in data["attempts"][0]["evidence"]
            if item["gate_id"] != "G-PAGE-IDENTITY"
        ]
        data["attempts"][0]["source_operations"]["operations"][0]["gate_ids"].remove(
            "G-PAGE-IDENTITY"
        )
        data["decisions"][0]["affected_gate_ids"] = ["G-PAGINATION-CONTROL"]
        with self.assertRaisesRegex(AssertionError, "missing required catalog gate"):
            infrastructure.validate_campaign_artifact(data)

    def test_generic_direct_catalog_is_not_an_acceptance_plan(self) -> None:
        data = accepted_campaign()
        data["capability_catalog"] = [
            "G-QUERY-TRANSPORT",
            "G-FIELD-BOUNDARY",
            "G-PAGINATION-CONTROL",
            "G-PAGE-IDENTITY",
        ]
        with self.assertRaisesRegex(
            AssertionError, "frozen task/source required-gate plan"
        ):
            infrastructure.validate_campaign_artifact(data)

    def test_source_plan_covers_required_acceptance_domains(self) -> None:
        required_domains = {
            "G-CONTENT-CONTROL",
            "G-DATE-CONTROL",
            "G-LANGUAGE-CONTROL",
            "G-CONTROLLED-VOCABULARY",
            "G-RETRIEVAL",
            "G-PAGE-IDENTITY",
            "G-COMPLETENESS",
            "G-FAILURE-BEHAVIOR",
        }
        plan = infrastructure.TASK_SOURCE_REQUIRED_GATE_PLANS[("S-D01", "scopus")]
        self.assertTrue(required_domains <= set(plan))

        data = accepted_campaign()
        data["capability_gates"] = [
            item
            for item in data["capability_gates"]
            if item["gate_id"] != "G-DATE-CONTROL"
        ]
        data["attempts"][1]["evidence"] = [
            item
            for item in data["attempts"][1]["evidence"]
            if item["gate_id"] != "G-DATE-CONTROL"
        ]
        with self.assertRaisesRegex(AssertionError, "missing required catalog gate"):
            infrastructure.validate_campaign_artifact(data)

    def test_carry_forward_requires_immutable_passed_snapshot(self) -> None:
        data = source_campaign("s-d03-ieee-xplore")
        field_parser = gate(data, "G-FIELD-PARSER")
        field_parser["carry_forward"]["original_observed_basis"] = (
            "official_documentation"
        )
        with self.assertRaisesRegex(AssertionError, "original observed basis"):
            infrastructure.validate_campaign_artifact(data)

        data = source_campaign("s-d03-ieee-xplore")
        field_parser = gate(data, "G-FIELD-PARSER")
        field_parser["carry_forward"]["evidence"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(AssertionError, "path/hash"):
            infrastructure.validate_campaign_artifact(data)

        data = source_campaign("s-d03-ieee-xplore")
        data["gate_status_snapshots"] = []
        with self.assertRaisesRegex(
            AssertionError, "immutable passed\\+reusable gate-status snapshot"
        ):
            infrastructure.validate_campaign_artifact(data)

    def test_d03_failed_year_evidence_cannot_be_carried_to_p05_as_passed(self) -> None:
        data = source_campaign("s-d03-ieee-xplore")
        data["controller_authorization"]["maximum_additional_attempts"] = 5
        data["controller_authorization"]["maximum_technical_corrective_attempts"] = 5
        p4 = next(attempt for attempt in data["attempts"] if attempt["sequence"] == 4)
        p5 = copy.deepcopy(p4)
        p5_id = "S-D03-P07-20260825T161500-0400"
        next_sequence = max(attempt["sequence"] for attempt in data["attempts"]) + 1
        p5.update(
            {
                "attempt_id": p5_id,
                "sequence": next_sequence,
                "manifest_path": f"pilots/{p5_id}/manifest.json",
                "manifest_sha256": "f" * 64,
                "evidence": [],
                "source_operations": {
                    "predeclared_maximum": 0,
                    "performed": 0,
                    "operations": [],
                },
            }
        )
        p5["allocation"].update(
            {
                "authorization_decision_id": "D-TECH-NEXT-P05",
                "allocated_at": "2026-08-24T16:13:25-04:00",
            }
        )
        p5["terminal"].update(
            {
                "browser_backed": False,
                "terminal_verification": "not_applicable",
                "cleanup_receipt": None,
                "lease_receipt": None,
            }
        )
        data["attempts"].append(p5)

        year_control = gate(data, "G-YEAR-CONTROL")
        failed_evidence = [
            {"path": item["path"], "sha256": item["sha256"]}
            for item in p4["evidence"]
            if item["gate_id"] == "G-YEAR-CONTROL"
        ]
        year_control.update(
            {
                "checkpoint_id": "CP-YEAR-CONTROL-P05",
                "evidence": [
                    {"path": item["path"], "sha256": item["sha256"], "validity": "valid"}
                    for item in failed_evidence
                ],
                "attempt_id": p5_id,
                "status": "passed",
                "observed_basis": "carried_forward",
                "reusable": True,
                "carried_forward": True,
                "carry_forward": {
                    "from_attempt_id": p4["attempt_id"],
                    "from_gate_id": "G-YEAR-CONTROL",
                    "evidence": failed_evidence,
                    "original_observed_basis": "observed",
                    "affected_by_code_or_semantic_change": False,
                    "rationale": "This false carry is intentionally rejected.",
                },
                "source_operation_count": 0,
                "semantic_impact": {
                    "classification": "none",
                    "review_effect": False,
                    "rationale": "A carry has no new technical effect.",
                },
                "invalidation": None,
            }
        )
        data["gate_status_snapshots"].append(
            {
                "snapshot_id": "GS-P04-YEAR-CONTROL",
                "attempt_id": p4["attempt_id"],
                "manifest_path": p4["manifest_path"],
                "manifest_sha256": p4["manifest_sha256"],
                "gate_id": "G-YEAR-CONTROL",
                "status": "passed",
                "reusable": True,
                "original_observed_basis": "observed",
                "evidence": failed_evidence,
                "immutable": True,
            }
        )
        with self.assertRaisesRegex(
            AssertionError, "trusted immutable gate-status migration inventory"
        ):
            infrastructure.validate_campaign_artifact(data)

    def test_second_initial_attempt_is_rejected(self) -> None:
        data = campaign()
        data["attempts"][1]["allocation"]["attempt_kind"] = "initial"
        data["attempts"][1]["allocation"]["authorization_decision_id"] = None
        data["attempts"][1]["allocation"]["prospectively_authorized"] = False
        with self.assertRaisesRegex(AssertionError, "exactly one initial"):
            infrastructure.validate_campaign_artifact(data)

    def test_finite_campaign_budget_cannot_be_bypassed(self) -> None:
        data = campaign()
        third = copy.deepcopy(data["attempts"][1])
        third.update(
            {
                "attempt_id": "S-D01-P03-20260824T152000+0000",
                "sequence": 3,
                "manifest_path": "pilots/S-D01-P03-20260824T152000+0000/manifest.json",
                "manifest_sha256": "e" * 64,
                "evidence": [],
            }
        )
        third["allocation"].update(
            {
                "authorization_decision_id": "D-TECH-P03",
                "allocated_at": "2026-08-24T15:20:00+00:00",
            }
        )
        third["source_operations"] = {
            "predeclared_maximum": 0,
            "performed": 0,
            "operations": [],
        }
        data["attempts"].append(third)
        data["decisions"].append(
            {
                "decision_id": "D-TECH-P03",
                "attempt_id": third["attempt_id"],
                "decision_class": "controller_technical",
                "review_effect": False,
                "affects_underlying_literature_review": False,
                "human_authorization_required": False,
                "authorization_status": "prospectively_authorized",
                "authorized_by": "controller",
                "decided_at": "2026-08-24T15:19:00+00:00",
                "maximum_source_operations": 0,
                "affected_gate_ids": ["G-PAGINATION-CONTROL"],
                "rationale": "Second bounded technical repair.",
            }
        )
        authorization = data["controller_authorization"]
        authorization["maximum_additional_attempts"] = 1
        authorization["maximum_technical_corrective_attempts"] = 1
        authorization["maximum_methodological_revision_attempts"] = 1
        with self.assertRaisesRegex(AssertionError, "finite .*budget"):
            infrastructure.validate_campaign_artifact(data)

    def test_source_free_setup_incident_does_not_consume_enacted_attempt_budget(
        self,
    ) -> None:
        data = campaign()
        incident = copy.deepcopy(data["attempts"][1])
        incident_id = "S-D01-P03-20260824T152000+0000"
        incident.update(
            {
                "attempt_id": incident_id,
                "sequence": 3,
                "manifest_path": f"pilots/{incident_id}/manifest.json",
                "manifest_sha256": "e" * 64,
                "evidence": [],
                "source_operations": {
                    "predeclared_maximum": 1,
                    "performed": 0,
                    "operations": [],
                },
            }
        )
        incident["allocation"].update(
            {
                "authorization_decision_id": "D-TECH-P03",
                "allocated_at": "2026-08-24T15:20:00+00:00",
                "source_phase_started": False,
            }
        )
        incident["terminal"].update(
            {
                "outcome": "blocked",
                "category": "technical",
                "ended_at": "2026-08-24T15:21:00+00:00",
                "provider_failure": False,
                "browser_backed": False,
                "terminal_verification": "not_applicable",
                "cleanup_receipt": None,
                "lease_receipt": None,
                "cancelled_by": None,
                "reason": "A deterministic source-free setup check failed before enactment.",
            }
        )
        data["attempts"].append(incident)
        data["decisions"].append(
            {
                "decision_id": "D-TECH-P03",
                "attempt_id": incident_id,
                "decision_class": "controller_technical",
                "review_effect": False,
                "affects_underlying_literature_review": False,
                "human_authorization_required": False,
                "authorization_status": "prospectively_authorized",
                "authorized_by": "controller",
                "decided_at": "2026-08-24T15:19:00+00:00",
                "maximum_source_operations": 1,
                "affected_gate_ids": ["G-PAGINATION-CONTROL"],
                "rationale": "The source-free setup incident did not enact a source phase.",
            }
        )
        authorization = data["controller_authorization"]
        authorization["maximum_additional_attempts"] = 1
        authorization["maximum_technical_corrective_attempts"] = 1
        authorization["maximum_methodological_revision_attempts"] = 1

        infrastructure.validate_campaign_artifact(data)

        del incident["allocation"]["source_phase_started"]
        with self.assertRaisesRegex(AssertionError, "finite enacted .*budget"):
            infrastructure.validate_campaign_artifact(data)

    def test_non_enacted_setup_incident_cannot_hide_a_source_operation(self) -> None:
        data = campaign()
        incident = copy.deepcopy(data["attempts"][1])
        incident_id = "S-D01-P03-20260824T152000+0000"
        incident.update(
            {
                "attempt_id": incident_id,
                "sequence": 3,
                "manifest_path": f"pilots/{incident_id}/manifest.json",
                "manifest_sha256": "e" * 64,
                "evidence": [],
            }
        )
        incident["allocation"].update(
            {
                "authorization_decision_id": "D-TECH-P03",
                "allocated_at": "2026-08-24T15:20:00+00:00",
                "source_phase_started": False,
            }
        )
        incident["terminal"].update(
            {
                "outcome": "blocked",
                "category": "technical",
                "ended_at": "2026-08-24T15:21:00+00:00",
                "provider_failure": False,
                "browser_backed": False,
                "terminal_verification": "not_applicable",
                "cleanup_receipt": None,
                "lease_receipt": None,
                "cancelled_by": None,
                "reason": "An invalid non-enacted incident contains source work.",
            }
        )
        data["attempts"].append(incident)
        data["decisions"].append(
            {
                "decision_id": "D-TECH-P03",
                "attempt_id": incident_id,
                "decision_class": "controller_technical",
                "review_effect": False,
                "affects_underlying_literature_review": False,
                "human_authorization_required": False,
                "authorization_status": "prospectively_authorized",
                "authorized_by": "controller",
                "decided_at": "2026-08-24T15:19:00+00:00",
                "maximum_source_operations": 1,
                "affected_gate_ids": ["G-PAGINATION-CONTROL"],
                "rationale": "Intentionally invalid test fixture.",
            }
        )
        with self.assertRaisesRegex(
            AssertionError, "cannot perform source operations before its source phase starts"
        ):
            infrastructure.validate_campaign_artifact(data)

    def test_prospective_technical_decision_binds_a_later_attempt(self) -> None:
        data = campaign()
        decision = data["decisions"][0]
        decision["attempt_id"] = None
        decision["maximum_source_operations"] = 4
        data["controller_authorization"]["maximum_source_operations_per_attempt"] = 100
        data["attempts"][1]["source_operations"]["predeclared_maximum"] = 4
        infrastructure.validate_campaign_artifact(data)

        data["attempts"][1]["source_operations"]["predeclared_maximum"] = 5
        with self.assertRaisesRegex(
            AssertionError, "decision .*source-operation bound"
        ):
            infrastructure.validate_campaign_artifact(data)

        data["attempts"][1]["source_operations"]["predeclared_maximum"] = 4
        decision["affected_gate_ids"] = ["G-QUERY-TRANSPORT"]
        with self.assertRaisesRegex(AssertionError, "omits a bound"):
            infrastructure.validate_campaign_artifact(data)

    def test_allocated_technical_decision_scopes_operation_bearing_gate(self) -> None:
        data = campaign()
        data["decisions"][0]["affected_gate_ids"] = ["G-PAGE-IDENTITY"]
        with self.assertRaisesRegex(
            AssertionError,
            "omits a bound operation-bearing capability gate",
        ):
            infrastructure.validate_campaign_artifact(data)

    def test_p05_cannot_hide_pending_near6_work_under_a_none_gate(self) -> None:
        data = source_campaign("s-d03-ieee-xplore")
        data["controller_authorization"]["maximum_additional_attempts"] = 5
        data["controller_authorization"]["maximum_technical_corrective_attempts"] = 5
        p5_id = "S-D03-P07-20260825T161500-0400"
        p4 = next(attempt for attempt in data["attempts"] if attempt["sequence"] == 4)
        p5 = copy.deepcopy(p4)
        next_sequence = max(attempt["sequence"] for attempt in data["attempts"]) + 1
        p5.update(
            {
                "attempt_id": p5_id,
                "sequence": next_sequence,
                "manifest_path": f"pilots/{p5_id}/manifest.json",
                "manifest_sha256": "f" * 64,
                "evidence": [],
                "source_operations": {
                    "predeclared_maximum": 1,
                    "performed": 1,
                    "operations": [
                        {
                            "operation_id": "P05-NEAR6-BYPASS",
                            "operation_key": "P05-NEAR6-BYPASS",
                            "gate_ids": ["G-NEAR6-PENDING-BYPASS"],
                            "outcome": "failed",
                            "source_reported_total": None,
                            "records_retrieved": 0,
                            "records_imported": 0,
                            "retry": None,
                        }
                    ],
                },
            }
        )
        p5["allocation"].update(
            {
                "authorization_decision_id": "D-TECH-NEXT-P05",
                "allocated_at": "2026-08-24T16:15:00-04:00",
            }
        )
        p5["terminal"].update(
            {
                "outcome": "failed",
                "category": "technical",
                "ended_at": "2026-08-24T16:16:00-04:00",
                "provider_failure": False,
                "browser_backed": False,
                "terminal_verification": "not_applicable",
                "cleanup_receipt": None,
                "lease_receipt": None,
                "cancelled_by": None,
                "reason": "The disallowed methodological operation stopped.",
            }
        )
        data["attempts"].append(p5)
        data["capability_gates"].append(
            {
                "gate_id": "G-NEAR6-PENDING-BYPASS",
                "checkpoint_id": "CP-NEAR6-PENDING-BYPASS-P05",
                "attempt_id": p5_id,
                "requirement": "A pending NEAR/6 methodological action cannot run.",
                "depends_on": [],
                "status": "blocked",
                "observed_basis": "untested",
                "original_observed_basis": "untested",
                "evidence": [],
                "reusable": False,
                "carried_forward": False,
                "carry_forward": None,
                "source_operation_count": 1,
                "semantic_impact": {
                    "classification": "none",
                    "review_effect": False,
                    "rationale": "The bypass falsely labels pending method work as neutral.",
                },
                "invalidation": None,
                "notes": "This is an intentionally rejected P05 bypass.",
            }
        )
        next_decision = next(
            decision
            for decision in data["decisions"]
            if decision["decision_id"] == "D-TECH-NEXT-P05"
        )
        next_decision["affected_gate_ids"].append("G-NEAR6-PENDING-BYPASS")

        with self.assertRaisesRegex(AssertionError, "non-technical capability gate"):
            infrastructure.validate_campaign_artifact(data)

    def test_methodological_decision_only_gate_does_not_block_technical_retry(
        self,
    ) -> None:
        data = campaign()
        data["status"] = "methodological_decision_pending"
        data["capability_gates"].append(
            {
                "gate_id": "G-NEAR6-METHOD",
                "checkpoint_id": "CP-NEAR6-METHOD",
                "attempt_id": data["attempts"][0]["attempt_id"],
                "requirement": "Human decision is required before changing the method.",
                "depends_on": [],
                "status": "untested",
                "observed_basis": "untested",
                "original_observed_basis": "untested",
                "evidence": [],
                "reusable": False,
                "carried_forward": False,
                "carry_forward": None,
                "source_operation_count": 0,
                "semantic_impact": {
                    "classification": "human_methodological",
                    "review_effect": True,
                    "rationale": "NEAR/6 method remains undecided.",
                },
                "invalidation": None,
                "notes": "Decision-only gate recorded against the initial technical observation.",
            }
        )
        data["decisions"].append(
            {
                "decision_id": "D-METHOD-NEAR6",
                "attempt_id": None,
                "decision_class": "human_methodological",
                "review_effect": True,
                "affects_underlying_literature_review": True,
                "human_authorization_required": True,
                "authorization_status": "pending",
                "authorized_by": "none",
                "affected_gate_ids": ["G-NEAR6-METHOD"],
                "rationale": "Human authorization is pending for the NEAR/6 methodological choice.",
            }
        )
        infrastructure.validate_campaign_artifact(data)

        data["capability_gates"][-1]["source_operation_count"] = 1
        data["attempts"][0]["source_operations"]["operations"][0]["gate_ids"].append(
            "G-NEAR6-METHOD"
        )
        with self.assertRaisesRegex(AssertionError, "cannot authorize source work"):
            infrastructure.validate_campaign_artifact(data)

    def test_human_can_accept_decision_only_gate_after_technical_observation(
        self,
    ) -> None:
        data = campaign()
        field_gate = gate(data, "G-FIELD-BOUNDARY")
        field_gate["semantic_impact"].update(
            {
                "classification": "human_methodological",
                "review_effect": True,
                "rationale": "The observed implementation is broader and needs owner acceptance.",
            }
        )
        evidence_attempt_id = field_gate["attempt_id"]
        data["decisions"].append(
            {
                "decision_id": "D-METHOD-BROADER-FALLBACK",
                "attempt_id": evidence_attempt_id,
                "decision_class": "human_methodological",
                "review_effect": True,
                "affects_underlying_literature_review": True,
                "human_authorization_required": True,
                "authorization_status": "authorized",
                "authorized_by": "human",
                "affected_gate_ids": ["G-FIELD-BOUNDARY"],
                "rationale": "The review owner accepts the observed broader fallback.",
                "decided_at": "2026-08-24T15:06:00+00:00",
            }
        )
        infrastructure.validate_campaign_artifact(data)

        data["decisions"][-1]["decided_at"] = "2026-08-24T14:59:00+00:00"
        with self.assertRaisesRegex(AssertionError, "predates its evidence attempt"):
            infrastructure.validate_campaign_artifact(data)

    def test_methodological_gate_cannot_hide_in_technical_attempt(self) -> None:
        data = campaign()
        pagination = gate(data, "G-PAGINATION-CONTROL")
        pagination["semantic_impact"].update(
            {
                "classification": "human_methodological",
                "review_effect": True,
                "rationale": "This would change the reviewed method.",
            }
        )
        with self.assertRaisesRegex(AssertionError, "non-technical capability gate"):
            infrastructure.validate_campaign_artifact(data)

    def test_cancelled_attempt_terminal_is_linked_and_not_provider_failure(
        self,
    ) -> None:
        data = campaign()
        set_terminal_cancelled(data)
        infrastructure.validate_campaign_artifact(data)

        data["attempts"][-1]["terminal"]["provider_failure"] = True
        with self.assertRaises(AssertionError):
            infrastructure.validate_campaign_artifact(data)

    def test_browser_backed_terminal_requires_cleanup_and_lease_receipts(self) -> None:
        data = campaign()
        terminal = data["attempts"][0]["terminal"]
        terminal.update({"browser_backed": True, "terminal_verification": "verified"})
        with self.assertRaises(AssertionError):
            infrastructure.validate_campaign_artifact(data)

    def test_current_browser_terminal_receipts_are_hash_verified(self) -> None:
        data = campaign()
        terminal = data["attempts"][0]["terminal"]
        terminal.update(
            {
                "browser_backed": True,
                "terminal_verification": "verified",
                "cleanup_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/cleanup-receipt.json",
                    "sha256": "a" * 64,
                },
                "lease_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/lease-receipt.json",
                    "sha256": "b" * 64,
                },
            }
        )
        with materialized_campaign(data) as (searches_root, _, _, _):
            self.assertEqual(
                infrastructure.validate_campaign_artifacts(searches_root), 1
            )

    def test_current_browser_terminal_rejects_missing_receipt(self) -> None:
        data = campaign()
        terminal = data["attempts"][0]["terminal"]
        terminal.update(
            {
                "browser_backed": True,
                "terminal_verification": "verified",
                "cleanup_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/cleanup-receipt.json",
                    "sha256": "a" * 64,
                },
            }
        )
        with self.assertRaises(AssertionError):
            infrastructure.validate_campaign_artifact(data)

    def test_trusted_pre_migration_legacy_inventory_is_accepted(self) -> None:
        with copied_source_campaign("s-d03-ieee-xplore") as (searches_root, _, _):
            self.assertEqual(
                infrastructure.validate_campaign_artifacts(searches_root), 1
            )

    def test_blocked_legacy_evidence_is_not_rewritten_for_privacy(self) -> None:
        # D05's immutable blocked evidence retains a historical local marker.
        # Only campaign-owned text and acceptance candidates are sanitized.
        with copied_source_campaign("s-d05-wiley-online-library") as (
            searches_root,
            _,
            _,
        ):
            self.assertEqual(
                infrastructure.validate_campaign_artifacts(searches_root), 1
            )

    def test_pre_migration_manifest_coverage_cannot_be_rewritten(self) -> None:
        with copied_source_campaign("s-d13-nasa-ntrs") as (
            searches_root,
            campaign_path,
            _,
        ):
            data = json.loads(campaign_path.read_text(encoding="utf-8"))
            data["attempts"][0]["manifest_sha256"] = "f" * 64
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(
                AssertionError, "omits a trusted pre-migration manifest identity"
            ):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_fresh_unlinked_p05_cannot_claim_legacy_terminal(self) -> None:
        with copied_source_campaign("s-d03-ieee-xplore") as (
            searches_root,
            campaign_path,
            source_packet,
        ):
            data = json.loads(campaign_path.read_text(encoding="utf-8"))
            p5_id = "S-D03-P07-20260825T161500-0400"
            p4 = next(attempt for attempt in data["attempts"] if attempt["sequence"] == 4)
            p5 = copy.deepcopy(p4)
            next_sequence = max(attempt["sequence"] for attempt in data["attempts"]) + 1
            p5.update(
                {
                    "attempt_id": p5_id,
                    "sequence": next_sequence,
                    "manifest_path": f"pilots/{p5_id}/manifest.json",
                    "evidence": [],
                    "source_operations": {
                        "predeclared_maximum": 0,
                        "performed": 0,
                        "operations": [],
                    },
                }
            )
            p5["allocation"].update(
                {
                    "authorization_decision_id": "D-TECH-NEXT-P05",
                    "allocated_at": "2026-08-24T16:13:25-04:00",
                }
            )
            manifest = manifest_template()
            manifest.update(
                {
                    "pilot_id": p5_id,
                    "task_id": data["task_id"],
                    "source_id": data["source_id"],
                    "method_type": data["method_type"],
                    "status": "failed",
                }
            )
            manifest.pop("campaign")
            manifest.pop("attempt_terminal")
            p5["manifest_sha256"] = write_json(
                source_packet / p5["manifest_path"], manifest
            )
            data["attempts"].append(p5)
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(AssertionError, "trusted pre-migration"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_missing_or_symlinked_legacy_manifest_is_rejected(self) -> None:
        with self.subTest("missing"):
            with copied_source_campaign("s-d03-ieee-xplore") as (
                searches_root,
                campaign_path,
                source_packet,
            ):
                data = json.loads(campaign_path.read_text(encoding="utf-8"))
                legacy_attempt = next(
                    attempt
                    for attempt in data["attempts"]
                    if attempt["terminal"]["terminal_verification"] == "legacy_unverifiable"
                )
                manifest_path = source_packet / legacy_attempt["manifest_path"]
                manifest_path.unlink()
                with self.assertRaisesRegex(AssertionError, "escapes or is missing"):
                    infrastructure.validate_campaign_artifacts(searches_root)

        with self.subTest("external symlink"):
            with copied_source_campaign("s-d03-ieee-xplore") as (
                searches_root,
                campaign_path,
                source_packet,
            ):
                data = json.loads(campaign_path.read_text(encoding="utf-8"))
                legacy_attempt = next(
                    attempt
                    for attempt in data["attempts"]
                    if attempt["terminal"]["terminal_verification"] == "legacy_unverifiable"
                )
                manifest_path = source_packet / legacy_attempt["manifest_path"]
                external = searches_root.parent / "external-manifest.json"
                shutil.copyfile(manifest_path, external)
                manifest_path.unlink()
                manifest_path.symlink_to(external)
                with self.assertRaisesRegex(AssertionError, "must not be symlinked"):
                    infrastructure.validate_campaign_artifacts(searches_root)

    def test_acceptance_rejects_legacy_unverifiable_browser_terminal(self) -> None:
        data = accepted_campaign()
        terminal = data["attempts"][0]["terminal"]
        terminal.update(
            {
                "outcome": "blocked",
                "category": "technical",
                "browser_backed": True,
                "terminal_verification": "legacy_unverifiable",
                "reason": "Historical browser attempt lacks a public shared-lease receipt.",
            }
        )
        with self.assertRaisesRegex(AssertionError, "legacy_unverifiable"):
            infrastructure.validate_campaign_artifact(data)

    def test_terminal_receipts_reject_aliasing_and_unrelated_evidence(self) -> None:
        data = campaign()
        terminal = data["attempts"][0]["terminal"]
        terminal.update(
            {
                "browser_backed": True,
                "terminal_verification": "verified",
                "cleanup_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/cleanup-receipt.json",
                    "sha256": "a" * 64,
                },
                "lease_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/lease-receipt.json",
                    "sha256": "b" * 64,
                },
            }
        )
        terminal["lease_receipt"] = copy.deepcopy(terminal["cleanup_receipt"])
        with self.assertRaisesRegex(AssertionError, "must be distinct"):
            infrastructure.validate_campaign_artifact(data)

        data = campaign()
        terminal = data["attempts"][0]["terminal"]
        terminal.update(
            {
                "browser_backed": True,
                "terminal_verification": "verified",
                "cleanup_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/cleanup-receipt.json",
                    "sha256": "a" * 64,
                },
                "lease_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/lease-receipt.json",
                    "sha256": "b" * 64,
                },
            }
        )
        with materialized_campaign(data) as (
            searches_root,
            campaign_path,
            data,
            source_packet,
        ):
            attempt = data["attempts"][0]
            terminal = attempt["terminal"]
            evidence = attempt["evidence"][0]
            terminal["cleanup_receipt"] = {
                "path": evidence["path"],
                "sha256": evidence["sha256"],
            }
            rewrite_linked_manifest_terminal(source_packet, attempt)
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(AssertionError, "structured JSON"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_terminal_receipts_bind_attempt_and_controller_ownership(self) -> None:
        data = campaign()
        terminal = data["attempts"][0]["terminal"]
        terminal.update(
            {
                "browser_backed": True,
                "terminal_verification": "verified",
                "cleanup_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/cleanup-receipt.json",
                    "sha256": "a" * 64,
                },
                "lease_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/lease-receipt.json",
                    "sha256": "b" * 64,
                },
            }
        )
        with materialized_campaign(data) as (
            searches_root,
            campaign_path,
            data,
            source_packet,
        ):
            attempt = data["attempts"][0]
            receipt_path = (
                source_packet / attempt["terminal"]["cleanup_receipt"]["path"]
            )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["attempt_id"] = data["attempts"][1]["attempt_id"]
            attempt["terminal"]["cleanup_receipt"]["sha256"] = write_json(
                receipt_path, receipt
            )
            rewrite_linked_manifest_terminal(source_packet, attempt)
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(AssertionError, "not bound to its attempt ID"):
                infrastructure.validate_campaign_artifacts(searches_root)

        data = campaign()
        data["attempts"][0]["terminal"].update(
            {
                "browser_backed": True,
                "terminal_verification": "verified",
                "cleanup_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/cleanup-receipt.json",
                    "sha256": "a" * 64,
                },
                "lease_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/lease-receipt.json",
                    "sha256": "b" * 64,
                },
            }
        )
        with materialized_campaign(data) as (
            searches_root,
            campaign_path,
            data,
            source_packet,
        ):
            attempt = data["attempts"][0]
            receipt_path = source_packet / attempt["terminal"]["lease_receipt"]["path"]
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["controller"]["controller_id"] = "another-controller"
            attempt["terminal"]["lease_receipt"]["sha256"] = write_json(
                receipt_path, receipt
            )
            rewrite_linked_manifest_terminal(source_packet, attempt)
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(
                AssertionError, "different controller ownership"
            ):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_pre_or_postflight_file_cannot_bypass_structured_lease_receipt(
        self,
    ) -> None:
        data = campaign()
        terminal = data["attempts"][0]["terminal"]
        terminal.update(
            {
                "browser_backed": True,
                "terminal_verification": "verified",
                "cleanup_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/cleanup-receipt.json",
                    "sha256": "a" * 64,
                },
                "lease_receipt": {
                    "path": "pilots/S-D01-P01-20260824T150000+0000/postflight.json",
                    "sha256": "b" * 64,
                },
            }
        )
        with materialized_campaign(data) as (
            searches_root,
            campaign_path,
            data,
            source_packet,
        ):
            attempt = data["attempts"][0]
            lease_path = source_packet / attempt["terminal"]["lease_receipt"]["path"]
            attempt["terminal"]["lease_receipt"]["sha256"] = write_json(
                lease_path, {"phase": "postflight", "release_verified": True}
            )
            rewrite_linked_manifest_terminal(source_packet, attempt)
            save_campaign(campaign_path, data)
            with self.assertRaisesRegex(AssertionError, "does not validate"):
                infrastructure.validate_campaign_artifacts(searches_root)

    def test_busy_reissue_policy_is_auditable_and_accounted(self) -> None:
        data = campaign()
        operations = data["attempts"][1]["source_operations"]
        first = operations["operations"][0]
        first.update(
            {
                "outcome": "busy",
                "source_reported_total": None,
                "records_retrieved": 0,
            }
        )
        operations["predeclared_maximum"] = 2
        operations["performed"] = 2
        operations["operations"].append(
            {
                "operation_id": "OP-P02-PAGINATION-REISSUE",
                "operation_key": "PAGINATION",
                "gate_ids": ["G-PAGINATION-CONTROL"],
                "outcome": "failed",
                "source_reported_total": None,
                "records_retrieved": 0,
                "records_imported": 0,
                "retry": {
                    "reissue_of": "OP-P02-PAGINATION",
                    "policy_id": "RP-BUSY-01",
                    "reason": "same_tab_busy",
                    "same_tab": True,
                    "preauthorized": True,
                    "completed": True,
                    "passive_wait_delay_seconds": 5,
                    "receipt": {
                        "path": "pilots/S-D01-P02-20260824T151000+0000/busy-reissue.json",
                        "sha256": "e" * 64,
                    },
                },
            }
        )
        data["controller_authorization"]["maximum_source_operations_per_attempt"] = 2
        data["decisions"][0]["maximum_source_operations"] = 2
        gate(data, "G-PAGINATION-CONTROL")["source_operation_count"] = 2
        data["retry_policy"] = {
            "policy_id": "RP-BUSY-01",
            "maximum_retries": 1,
            "passive_wait_delays_seconds": [5],
            "attempted": 1,
            "completed": 1,
            "preauthorized_same_tab_busy_reissue": True,
        }
        infrastructure.validate_campaign_artifact(data)

        retry = data["attempts"][1]["source_operations"]["operations"][1]["retry"]
        retry["completed"] = False
        data["retry_policy"]["completed"] = 0
        infrastructure.validate_campaign_artifact(data)

        data["retry_policy"]["completed"] = 1
        with self.assertRaisesRegex(AssertionError, "completed does not match"):
            infrastructure.validate_campaign_artifact(data)

    def test_incomplete_reissue_must_be_failed(self) -> None:
        data = campaign()
        operations = data["attempts"][1]["source_operations"]
        first = operations["operations"][0]
        first.update(
            {
                "outcome": "busy",
                "source_reported_total": None,
                "records_retrieved": 0,
            }
        )
        operations["predeclared_maximum"] = 2
        operations["performed"] = 2
        operations["operations"].append(
            {
                "operation_id": "OP-P02-PAGINATION-REISSUE",
                "operation_key": "PAGINATION",
                "gate_ids": ["G-PAGINATION-CONTROL"],
                "outcome": "success",
                "source_reported_total": 1,
                "records_retrieved": 0,
                "records_imported": 0,
                "retry": {
                    "reissue_of": "OP-P02-PAGINATION",
                    "policy_id": "RP-BUSY-01",
                    "reason": "same_tab_busy",
                    "same_tab": True,
                    "preauthorized": True,
                    "completed": False,
                    "passive_wait_delay_seconds": 5,
                    "receipt": {
                        "path": "pilots/S-D01-P02-20260824T151000+0000/busy-reissue.json",
                        "sha256": "e" * 64,
                    },
                },
            }
        )
        data["controller_authorization"]["maximum_source_operations_per_attempt"] = 2
        data["decisions"][0]["maximum_source_operations"] = 2
        data["retry_policy"] = {
            "policy_id": "RP-BUSY-01",
            "maximum_retries": 1,
            "passive_wait_delays_seconds": [5],
            "attempted": 1,
            "completed": 0,
            "preauthorized_same_tab_busy_reissue": True,
        }
        with self.assertRaisesRegex(AssertionError, "failed"):
            infrastructure.validate_campaign_artifact(data)

    def test_failed_operation_cannot_be_reissued(self) -> None:
        data = campaign()
        operations = data["attempts"][1]["source_operations"]
        first = operations["operations"][0]
        first["outcome"] = "failed"
        operations["predeclared_maximum"] = 2
        operations["performed"] = 2
        operations["operations"].append(
            {
                "operation_id": "OP-P02-PAGINATION-REISSUE",
                "operation_key": "PAGINATION",
                "gate_ids": ["G-PAGINATION-CONTROL"],
                "outcome": "failed",
                "source_reported_total": None,
                "records_retrieved": 0,
                "records_imported": 0,
                "retry": {
                    "reissue_of": "OP-P02-PAGINATION",
                    "policy_id": "RP-BUSY-01",
                    "reason": "same_tab_busy",
                    "same_tab": True,
                    "preauthorized": True,
                    "completed": True,
                    "passive_wait_delay_seconds": 5,
                    "receipt": {
                        "path": "pilots/S-D01-P02-20260824T151000+0000/busy-reissue.json",
                        "sha256": "e" * 64,
                    },
                },
            }
        )
        data["controller_authorization"]["maximum_source_operations_per_attempt"] = 2
        data["decisions"][0]["maximum_source_operations"] = 2
        data["retry_policy"] = {
            "policy_id": "RP-BUSY-01",
            "maximum_retries": 1,
            "passive_wait_delays_seconds": [5],
            "attempted": 1,
            "completed": 1,
            "preauthorized_same_tab_busy_reissue": True,
        }
        with self.assertRaisesRegex(AssertionError, "cannot reissue a failed"):
            infrastructure.validate_campaign_artifact(data)

    def test_transitive_failure_does_not_leave_stale_passed_evidence(self) -> None:
        data = campaign()
        identity = gate(data, "G-PAGE-IDENTITY")
        identity["status"] = "passed"
        identity["reusable"] = True
        identity["evidence"][0]["validity"] = "valid"
        identity["invalidation"] = None
        data["attempts"][0]["evidence"][2]["validity"] = "valid"
        with self.assertRaisesRegex(AssertionError, "stale passed dependent"):
            infrastructure.validate_campaign_artifact(data)

    def test_thirty_one_legacy_manifests_remain_compatible_without_campaign_fields(
        self,
    ) -> None:
        existing = next((SEARCHES / "sources").rglob("manifest.json"))
        with tempfile.TemporaryDirectory() as temporary:
            searches_root = Path(temporary) / "searches"
            shutil.copytree(SEARCHES / "schemas", searches_root / "schemas")
            for index in range(31):
                path = (
                    searches_root
                    / "sources"
                    / "s-d01-legacy"
                    / "pilots"
                    / f"legacy-{index:02d}"
                    / "manifest.json"
                )
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(existing, path)
            self.assertEqual(
                infrastructure.validate_legacy_pilot_manifests(searches_root), 31
            )

    def test_final_events_are_forbidden_only_in_pre_final_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            searches_root = Path(temporary) / "searches"
            final_events = searches_root / "final-events"
            final_events.mkdir(parents=True)
            (final_events / "README.md").write_text("placeholder\n", encoding="utf-8")
            (final_events / "R002.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "premature"):
                infrastructure.validate_final_events("pre-final", searches_root)
            infrastructure.validate_final_events("final", searches_root)
            infrastructure.validate_final_events("R002", searches_root)


if __name__ == "__main__":
    unittest.main()
