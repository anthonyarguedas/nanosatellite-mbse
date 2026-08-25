"""Offline tests for the bounded arXiv P01 runner."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arxiv_p01_runner as runner


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "searches" / "sources" / "s-d11-arxiv"
ADAPTER = Path("/trusted/local/search_arxiv.py")


class ArxivP01RunnerTests(unittest.TestCase):
    def test_translation_spec_covers_exactly_nine_hashed_query_cells(self):
        spec = json.loads((PACKET / "translation-spec.json").read_text(encoding="utf-8"))
        partitions = spec["partition_to_cell_unions"]
        self.assertEqual(
            [item["partition_id"] for item in partitions], list(runner.PARTITIONS)
        )
        for item in partitions:
            self.assertTrue(item["lossless_union"])
            self.assertEqual(len(item["cells"]), 1)
            cell = item["cells"][0]
            raw = (PACKET / cell["path"]).read_bytes()
            self.assertTrue(raw.endswith(b"\n"))
            self.assertNotIn(b"\r", raw)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), cell["sha256"])

    def test_adapter_command_uses_normal_shared_context_without_requiring_target(self):
        arguments = dict(
            adapter=ADAPTER,
            query="(CubeSat) AND (SysML)",
            output=Path("out.json"),
            pilot_year=2026,
            limit=1,
            max_pages=1,
            count_only=True,
            skip_full_abstracts=True,
            timeout=30,
            page_delay=0.2,
            uv="uv",
        )
        command = runner.adapter_command(target_id=None, **arguments)
        self.assertIn("http://127.0.0.1:9222", command)
        self.assertNotIn("--target-id", command)
        self.assertIn("--count-only", command)
        self.assertNotIn("--fresh-browser", command)
        self.assertNotIn("--headless", command)
        self.assertNotIn("--csv-output-path", command)

        authorized = runner.adapter_command(target_id="trusted-target", **arguments)
        target_index = authorized.index("--target-id")
        self.assertEqual(authorized[target_index + 1], "trusted-target")

    def test_runner_executes_nine_counts_then_bounded_diagnostics(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "runner-receipt.json"
            calls: list[list[str]] = []

            def fake_invoke(command, **kwargs):
                calls.append(command)
                output = Path(command[command.index("--output-path") + 1])
                output.parent.mkdir(parents=True, exist_ok=True)
                name = output.name
                if ".count." in name:
                    total = 101 if name.startswith("B1.") else 0
                    payload = {
                        "total": total,
                        "results": [],
                        "output_metadata": {"count_only": True, "status": "count_only"},
                    }
                elif ".metadata-abstract." in name:
                    payload = {
                        "total": 101,
                        "results": [{"paperId": "2401.12345", "abstract": "native"}],
                        "output_metadata": {"count_only": False, "status": "partial"},
                    }
                else:
                    payload = {
                        "total": 101,
                        "results": [{"paperId": "2401.12345"}],
                        "output_metadata": {"count_only": False, "status": "partial"},
                    }
                output.write_text(json.dumps(payload), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0)

            result = runner.run_attempt(
                packet=PACKET,
                output_root=root / "outputs",
                runner_receipt=receipt,
                attempt_id="S-D11-P01-20260825T000000+0000",
                target_id="trusted-target",
                pilot_year=2026,
                adapter=Path(__file__),
                invoke=fake_invoke,
            )
            self.assertEqual(result, 0)
            data = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(data["source_operations_performed"], 11)
            self.assertEqual(data["terminal"], "completed")
            self.assertEqual(len(data["operations"]), 11)
            self.assertEqual(len(calls), 11)
            self.assertTrue(all("http://127.0.0.1:9222" in call for call in calls))
            self.assertEqual(
                [operation["kind"] for operation in data["operations"][:9]],
                ["count"] * 9,
            )
            self.assertEqual(data["operations"][9]["kind"], "metadata-abstract")
            self.assertEqual(data["operations"][10]["kind"], "pagination")

    def test_failed_count_stops_without_a_partial_prefix(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "runner-receipt.json"
            calls = 0

            def fail_invoke(command, **kwargs):
                nonlocal calls
                calls += 1
                return subprocess.CompletedProcess(command, 1)

            result = runner.run_attempt(
                packet=PACKET,
                output_root=root / "outputs",
                runner_receipt=receipt,
                attempt_id="S-D11-P01-20260825T000001+0000",
                target_id="trusted-target",
                pilot_year=2026,
                adapter=Path(__file__),
                invoke=fail_invoke,
            )
            data = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(result, 1)
            self.assertEqual(calls, 1)
            self.assertEqual(data["terminal"], "failed")
            self.assertEqual(data["operations"][0]["outcome"], "failed")
            self.assertIsNone(data["operations"][0]["source_reported_total"])


if __name__ == "__main__":
    unittest.main()
