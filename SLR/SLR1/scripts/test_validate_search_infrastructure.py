"""Focused regression tests for checkpointed pilot campaigns."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_search_infrastructure as infrastructure  # noqa: E402

ROOT = SCRIPT_DIR.parent
TEMPLATE_PATH = ROOT / "searches" / "templates" / "pilot-campaign.template.json"


def campaign() -> dict:
    return copy.deepcopy(json.loads(TEMPLATE_PATH.read_text(encoding="utf-8")))


def gate(data: dict, gate_id: str) -> dict:
    return next(item for item in data["capability_gates"] if item["gate_id"] == gate_id)


def pending_methodological_campaign() -> dict:
    data = campaign()
    data["status"] = "methodological_decision_pending"
    data["decisions"].append(
        {
            "decision_id": "D-METHOD-P03",
            "attempt_id": None,
            "decision_class": "human_methodological",
            "review_effect": True,
            "affects_underlying_literature_review": True,
            "human_authorization_required": True,
            "authorization_status": "pending",
            "authorized_by": "none",
            "affected_gate_ids": ["G-PAGINATION-CONTROL"],
            "rationale": "Changing pagination accounting would change the reviewed method.",
        }
    )
    return data


class PilotCampaignValidationTests(unittest.TestCase):
    def test_late_failure_preserves_independent_earlier_gates(self) -> None:
        data = campaign()
        infrastructure.validate_campaign_artifact(data)

        self.assertEqual(gate(data, "G-QUERY-TRANSPORT")["status"], "passed")
        self.assertEqual(gate(data, "G-FIELD-BOUNDARY")["status"], "passed")
        self.assertEqual(gate(data, "G-PAGINATION-CONTROL")["status"], "failed")
        self.assertEqual(gate(data, "G-PAGE-IDENTITY")["status"], "invalidated")

    def test_missing_dependency_is_rejected(self) -> None:
        data = campaign()
        gate(data, "G-QUERY-TRANSPORT")["depends_on"] = ["G-NOT-DECLARED"]
        with self.assertRaisesRegex(AssertionError, "missing gate"):
            infrastructure.validate_campaign_artifact(data)

    def test_dependency_cycle_is_rejected(self) -> None:
        data = campaign()
        gate(data, "G-QUERY-TRANSPORT")["depends_on"] = ["G-PAGE-IDENTITY"]
        with self.assertRaisesRegex(AssertionError, "dependency cycle"):
            infrastructure.validate_campaign_artifact(data)

    def test_only_declared_dependent_is_invalidated(self) -> None:
        data = campaign()
        identity = gate(data, "G-PAGE-IDENTITY")
        identity["status"] = "passed"
        identity["evidence"][0]["validity"] = "valid"
        identity["invalidation"] = None
        data["attempts"][0]["evidence"][2]["validity"] = "valid"
        with self.assertRaisesRegex(AssertionError, "stale passed dependent"):
            infrastructure.validate_campaign_artifact(data)

    def test_carry_forward_requires_exact_hash_and_prior_attempt(self) -> None:
        data = campaign()
        query = gate(data, "G-QUERY-TRANSPORT")
        query["carry_forward"]["evidence"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(AssertionError, "path/hash"):
            infrastructure.validate_campaign_artifact(data)

        data = campaign()
        query = gate(data, "G-QUERY-TRANSPORT")
        query["carry_forward"]["from_attempt_id"] = "S-D01-P99-20260824T140000+0000"
        with self.assertRaisesRegex(AssertionError, "unknown prior attempt"):
            infrastructure.validate_campaign_artifact(data)

    def test_controller_technical_decision_never_requires_human(self) -> None:
        data = campaign()
        data["decisions"][0]["human_authorization_required"] = True
        with self.assertRaisesRegex(
            AssertionError, "technical work cannot require human"
        ):
            infrastructure.validate_campaign_artifact(data)

    def test_methodological_decision_requires_human(self) -> None:
        data = pending_methodological_campaign()
        infrastructure.validate_campaign_artifact(data)

        data["decisions"][-1]["human_authorization_required"] = False
        with self.assertRaisesRegex(AssertionError, "must require human authorization"):
            infrastructure.validate_campaign_artifact(data)

    def test_operator_cancellation_is_not_provider_failure(self) -> None:
        data = campaign()
        data["status"] = "cancelled"
        data["cancellation"] = {
            "kind": "operator_cancellation",
            "cancelled_by": "operator",
            "cancelled_at": "2026-08-24T15:11:00+00:00",
            "reason": "Operator stopped the campaign before another attempt.",
            "provider_failure": False,
        }
        infrastructure.validate_campaign_artifact(data)

        data["cancellation"]["provider_failure"] = True
        with self.assertRaisesRegex(AssertionError, "not provider failure"):
            infrastructure.validate_campaign_artifact(data)

    def test_old_pilot_manifests_remain_compatible(self) -> None:
        infrastructure.validate_legacy_pilot_manifests()

    def test_null_zero_and_no_import_invariants(self) -> None:
        data = campaign()
        data["attempts"][1]["source_operations"]["operations"][0][
            "source_reported_total"
        ] = 0
        with self.assertRaisesRegex(AssertionError, "null total"):
            infrastructure.validate_campaign_artifact(data)

        data = campaign()
        data["attempts"][0]["source_operations"]["operations"][0][
            "records_imported"
        ] = 1
        with self.assertRaisesRegex(AssertionError, "must be zero"):
            infrastructure.validate_campaign_artifact(data)

        data = campaign()
        operation = data["attempts"][0]["source_operations"]["operations"][0]
        operation["outcome"] = "explicit_zero"
        with self.assertRaisesRegex(AssertionError, "explicit zero"):
            infrastructure.validate_campaign_artifact(data)


if __name__ == "__main__":
    unittest.main()
