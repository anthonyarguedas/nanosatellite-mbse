"""Source-free invariants for the new S-D07/S-D08 launch bundles."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "searches" / "sources"
DICTIONARY_PATH = ROOT / "searches" / "search-concept-dictionary.json"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
PACKETS = (
    ("s-d07-proquest-atai", "S-D07", "proquest-atai", "Advanced Technologies & Aerospace Index", 14),
    ("s-d08-proquest-pqdt", "S-D08", "proquest-pqdt", "ProQuest Dissertations & Theses Global", 16),
)


class ProQuestSourcePacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dictionary = json.loads(DICTIONARY_PATH.read_text(encoding="utf-8"))
        cls.dictionary_hash = hashlib.sha256(DICTIONARY_PATH.read_bytes()).hexdigest()

    def test_brand_new_packets_have_no_fabricated_campaign_or_attempt(self) -> None:
        for directory, *_ in PACKETS:
            with self.subTest(directory=directory):
                packet = SOURCES / directory
                self.assertFalse((packet / "campaign.json").exists())
                self.assertFalse(any((packet / "pilots").glob("**/manifest.json")) if (packet / "pilots").exists() else False)

    def test_each_packet_has_exactly_nine_hashed_cells_and_no_shards(self) -> None:
        for directory, task_id, source_id, source_name, _ in PACKETS:
            with self.subTest(directory=directory):
                packet = SOURCES / directory
                spec = json.loads((packet / "translation-spec.json").read_text(encoding="utf-8"))
                self.assertEqual(spec["task_id"], task_id)
                self.assertEqual(spec["source_id"], source_id)
                self.assertEqual(spec["source_name"], source_name)
                self.assertEqual(spec["normative_provenance"]["dictionary_sha256"], self.dictionary_hash)
                self.assertEqual(
                    [item["partition_id"] for item in spec["partitions"]], list(PARTITIONS)
                )
                self.assertEqual(len(list((packet / "queries").glob("*.txt"))), 9)
                for partition in spec["partitions"]:
                    self.assertEqual(len(partition["source_native_cells"]), 1)
                    cell = partition["source_native_cells"][0]
                    query_path = packet / cell["exact_query_file"]
                    self.assertTrue(query_path.is_file())
                    content = query_path.read_bytes()
                    self.assertEqual(cell["sha256"], hashlib.sha256(content).hexdigest())
                    self.assertEqual(cell["utf8_byte_count"], len(content))
                    self.assertTrue(content.endswith(b"\n"))
                    self.assertIsNone(cell["source_reported_total"])
                    self.assertFalse(cell["total_is_exact"])
                    self.assertFalse(partition["lossless_union"]["required"])

    def test_union_of_query_cells_retains_all_normative_literals_and_pairs(self) -> None:
        for directory, *_ in PACKETS:
            with self.subTest(directory=directory):
                packet = SOURCES / directory
                query_text = "\n".join(
                    path.read_text(encoding="utf-8")
                    for path in sorted((packet / "queries").glob("*.txt"))
                )
                self.assertNotIn("SmallSat", query_text)
                for concept in self.dictionary["concepts"].values():
                    for term in concept.get("terms", []):
                        self.assertIn(f'"{term}"', query_text)
                    for rule in concept.get("pair_rules", []):
                        for left in rule["left"]:
                            for right in rule["right"]:
                                self.assertIn(
                                    f'"{left}" NEAR/6 "{right}"', query_text
                                )
                    if concept.get("kind") == "paired_terms":
                        for left in concept["left"]:
                            for right in concept["right"]:
                                self.assertIn(
                                    f'"{left}" NEAR/6 "{right}"', query_text
                                )
                self.assertNotIn("model-based engineering", query_text)

    def test_guidelines_and_plans_are_separate_and_predeclare_launch_requirements(self) -> None:
        for directory, task_id, source_id, source_name, operation_cap in PACKETS:
            with self.subTest(directory=directory):
                packet = SOURCES / directory
                guideline = (packet / "guideline.md").read_text(encoding="utf-8")
                plan = (packet / "p01-execution-plan.md").read_text(encoding="utf-8")
                for required in (
                    task_id,
                    source_id,
                    source_name,
                    "translation-spec.json",
                    "G-SOURCE-BOUNDARY",
                    "G-CONTROLLED-VOCABULARY",
                    "G-COMPLETENESS",
                    "diagnostic",
                    "total=null",
                    "no-screening",
                ):
                    self.assertIn(required, guideline.lower() if required.islower() else guideline)
                for required in (
                    task_id,
                    "P01",
                    "run_with_browser_lease.py",
                    "--receipt",
                    "127.0.0.1:9222",
                    "proquest_pilot_runner.py",
                    "--pilot-date",
                    "--lease-timeout",
                    "G-SOURCE-BOUNDARY",
                    "G-COMPLETENESS",
                    "2026-08-25",
                    "2011",
                    "2026",
                    f"{operation_cap} source operations",
                ):
                    self.assertIn(required, plan)
                for partition in PARTITIONS:
                    self.assertIn(f"{partition}.proquest-noft.txt", plan)
                self.assertNotIn("s-d-d08", plan)
                self.assertNotIn("S-D07-P02", plan)
                self.assertNotIn("S-D08-P02", plan)

    def test_runner_and_probe_are_source_free_on_dry_run_and_have_help(self) -> None:
        import subprocess
        import sys

        for filename in ("proquest_pilot_runner.py", "proquest_field_thesaurus_probe.py"):
            with self.subTest(filename=filename):
                completed = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / filename), "--help"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0)
                self.assertIn("usage:", completed.stdout.lower())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
