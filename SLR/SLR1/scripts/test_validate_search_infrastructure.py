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

import validate_search_infrastructure as infrastructure

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


def accepted_campaign() -> dict[str, Any]:
    """Turn the small template fixture into a structurally accepted campaign."""
    data = campaign()
    data["status"] = "accepted"
    data["acceptance"] = {
        "accepted_by": "human reviewer",
        "accepted_at": "2026-08-24T15:20:00+00:00",
        "rationale": "All required direct capability gates have current valid evidence.",
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
    return data


@contextmanager
def materialized_campaign(
    data: dict[str, Any] | None = None,
) -> Iterator[tuple[Path, Path, dict[str, Any], Path]]:
    """Create a complete source packet with hashed evidence and linked manifests."""
    temporary = tempfile.TemporaryDirectory()
    try:
        temporary_root = Path(temporary.name)
        searches_root = temporary_root / "searches"
        shutil.copytree(SEARCHES / "schemas", searches_root / "schemas")
        source_packet = searches_root / "sources" / "s-d01-fixture"
        source_packet.mkdir(parents=True)
        data = copy.deepcopy(data if data is not None else campaign())
        data["source_id"] = "fixture"

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

        for attempt in data["attempts"]:
            manifest = manifest_template()
            manifest.update(
                {
                    "pilot_id": attempt["attempt_id"],
                    "task_id": data["task_id"],
                    "source_id": data["source_id"],
                    "method_type": data["method_type"],
                    "campaign": {
                        "campaign_id": data["campaign_id"],
                        "attempt_id": attempt["attempt_id"],
                    },
                    "attempt_terminal": copy.deepcopy(attempt["terminal"]),
                }
            )
            manifest["status"] = {
                "completed": "complete",
                "blocked": "blocked",
                "failed": "failed",
                "cancelled": "cancelled",
            }[attempt["terminal"]["outcome"]]
            attempt["manifest_sha256"] = write_json(
                source_packet / attempt["manifest_path"], manifest
            )

        campaign_path = source_packet / "campaign.json"
        write_json(campaign_path, data)
        yield searches_root, campaign_path, data, source_packet
    finally:
        temporary.cleanup()


def save_campaign(path: Path, data: dict[str, Any]) -> None:
    write_json(path, data)


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

    def test_legacy_manifest_without_additive_links_is_hashed_and_validated(
        self,
    ) -> None:
        with materialized_campaign() as (
            searches_root,
            campaign_path,
            data,
            source_packet,
        ):
            for attempt in data["attempts"]:
                manifest_path = source_packet / attempt["manifest_path"]
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest.pop("campaign")
                manifest.pop("attempt_terminal")
                attempt["manifest_sha256"] = write_json(manifest_path, manifest)
            save_campaign(campaign_path, data)
            self.assertEqual(
                infrastructure.validate_campaign_artifacts(searches_root), 1
            )

    def test_accepted_campaign_requires_observed_not_inferred_catalog_gate(
        self,
    ) -> None:
        data = accepted_campaign()
        query = gate(data, "G-QUERY-TRANSPORT")
        query["original_observed_basis"] = "inferred"
        query["carry_forward"]["original_observed_basis"] = "inferred"
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
        data["decisions"][0]["affected_gate_ids"] = ["G-PAGINATION-CONTROL"]
        with self.assertRaisesRegex(AssertionError, "missing required catalog gate"):
            infrastructure.validate_campaign_artifact(data)

    def test_carry_forward_retains_original_basis_and_exact_hash(self) -> None:
        data = campaign()
        query = gate(data, "G-QUERY-TRANSPORT")
        query["carry_forward"]["original_observed_basis"] = "official_documentation"
        with self.assertRaisesRegex(AssertionError, "original observed basis"):
            infrastructure.validate_campaign_artifact(data)

        data = campaign()
        query = gate(data, "G-QUERY-TRANSPORT")
        query["carry_forward"]["evidence"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(AssertionError, "path/hash"):
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
        with self.assertRaisesRegex(AssertionError, "cannot authorize source work"):
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
        with self.assertRaisesRegex(AssertionError, "cannot hide methodological"):
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
        terminal["browser_backed"] = True
        with self.assertRaises(AssertionError):
            infrastructure.validate_campaign_artifact(data)

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
