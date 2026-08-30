"""Offline integrity tests for the OATD Pilot 003 route-cell plan."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RUNNER = Path(__file__).with_name("run_pilot.py")


def load_runner():
    spec = importlib.util.spec_from_file_location("oatd_pilot003_test_runner", RUNNER)
    if spec is None or spec.loader is None:  # pragma: no cover - test setup
        raise RuntimeError("could not load Pilot 003 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class OATDPilot003PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner()
        cls.modules = cls.runner.load_modules()
        cls.plan = cls.runner.build_plan(cls.modules)

    def test_uses_the_canonical_main_agent_tools_browser_stack(self):
        root = Path.home() / "agent-tools"
        self.assertEqual(root, self.runner.CANONICAL_AGENT_TOOLS_ROOT)
        self.assertEqual(
            root / "internet/skills/browser/scripts/search_oatd.py",
            self.runner.OATD_ADAPTER_PATH,
        )
        self.assertEqual(
            root / "internet/skills/browser/scripts/run_search_events.py",
            self.runner.EVENT_RUNNER_PATH,
        )
        self.assertEqual(
            root / "internet/skills/browser/scripts/run_with_browser.py",
            self.runner.BROWSER_RUNNER_PATH,
        )

    def test_health_readback_requires_the_exact_rendered_english_clause(self):
        plain = "title:(microRNA) AND pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]"
        english = "title:(microRNA) AND language:(en OR eng OR english) AND pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]"
        payload = {
            "query": "title:(microRNA)",
            "executed_query": english,
            "total": 1096,
            "output_metadata": {
                "executed_query": english,
                "status": "count_only",
                "observed_exact_query_echo": True,
                "earliest_year_filter": 2011,
                "latest_year_filter": 2026,
                "page_size": 30,
                "language_filter": {
                    "display_label": "English",
                    "source_value": "(en OR eng OR english)",
                },
            },
        }
        self.assertTrue(
            self.runner.expected_health_readback(payload, require_english=True)
        )
        payload["executed_query"] = plain
        self.assertFalse(
            self.runner.expected_health_readback(payload, require_english=True)
        )

    def test_strict_failure_reason_retains_the_explicit_source_error(self):
        reason = self.runner.strict_failure_reason(
            {
                "output_metadata": {
                    "error_type": "OATDMetadataRequestError",
                    "error": "OATD could not return from Record Details to search results.",
                }
            },
            "missing_exact_total_or_rows",
            "adapter failed",
        )
        self.assertEqual(
            "OATDMetadataRequestError: OATD could not return from Record Details to search results.",
            reason,
        )

    def test_all_nine_partitions_have_exact_route_safe_cells(self):
        expected = {
            "A1": 16,
            "A2": 20,
            "A3": 8,
            "B1": 3,
            "B2": 8,
            "BG1": 17,
            "BG2": 17,
            "BC1": 148,
            "BT2": 1792,
        }
        self.assertEqual(list(expected), self.plan["partition_order"])
        self.assertEqual(expected, {key: value["planned_cell_count"] for key, value in self.plan["partitions"].items()})
        self.assertEqual(sum(expected.values()), self.plan["total_planned_cells"])
        for partition in self.plan["partitions"].values():
            self.assertTrue(partition["coverage"]["factor_alternatives_preserved_in_source_order"])
            self.assertTrue(partition["coverage"]["each_atomic_conjunction_covered_once_by_disjoint_factor_groups"])
            self.assertEqual(
                partition["coverage"]["expected_atomic_conjunction_count"],
                partition["coverage"]["covered_atomic_conjunction_count"],
            )
            for cell in partition["cells"]:
                self.assertLessEqual(
                    cell["encoded_route_characters"], self.runner.CELL_TARGET
                )
                self.assertTrue(cell["adapter_planner_rechecked_as_identity"])
                self.assertNotIn("*", cell["query"])
                self.assertNotIn("?", cell["query"])

    def test_all_named_field_pair_unions_are_preserved(self):
        expected = {
            "BG1": (16, 192),
            "BG2": (16, 192),
            "BC1": (36, 432),
            "BT2": (224, 2688),
        }
        for partition_id, counts in expected.items():
            coverage = self.plan["partitions"][partition_id]["coverage"]
            self.assertEqual(counts[0], coverage["complete_pair_unions_checked"])
            self.assertEqual(counts[1], coverage["named_field_two_order_clauses_checked"])

    def test_plan_only_artifacts_keep_unreconciled_totals_null(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--output-dir", directory],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            root = Path(directory)
            plan = json.loads((root / "lossless-cell-plan.json").read_text())
            assessment = json.loads((root / "execution-assessment.json").read_text())
            self.assertEqual(self.runner.PLAN_SCHEMA, plan["schema_version"])
            self.assertEqual("not_checked_plan_only", assessment["browser_preflight"]["status"])
            self.assertTrue(assessment["overall"]["no_final_search"])
            for partition in assessment["partitions"].values():
                self.assertIsNone(partition["total"])
                self.assertFalse(partition["union"]["lossless"])
                self.assertEqual("unreconciled", partition["union"]["status"])


if __name__ == "__main__":
    unittest.main()
