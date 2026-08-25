"""Offline tests for the bounded ProQuest P01 runner and UI probe."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = load("test_slr1_proquest_pilot_runner", "proquest_pilot_runner.py")
probe = load("test_slr1_proquest_field_probe", "proquest_field_thesaurus_probe.py")


class ProQuestRunnerOfflineTests(unittest.TestCase):
    def packet_root(self, directory: Path, source: str) -> Path:
        packet = directory / source
        queries = packet / "queries"
        queries.mkdir(parents=True)
        for partition in runner.PARTITIONS:
            (queries / f"{partition}.proquest-noft.txt").write_text(
                f'NOFT("{partition}")\n', encoding="utf-8"
            )
        return packet

    def test_operation_caps_and_source_specific_probe_sets_are_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            atai = self.packet_root(root, "atai")
            pqdt = self.packet_root(root, "pqdt")
            date = runner.dt.date(2026, 8, 25)
            atai_ops = runner.build_operations(
                "proquest-atai", packet_root=atai, pilot_date=date
            )
            pqdt_ops = runner.build_operations(
                "proquest-pqdt", packet_root=pqdt, pilot_date=date
            )
            self.assertEqual(len(atai_ops), 14)
            self.assertEqual(len(pqdt_ops), 16)
            self.assertEqual(atai_ops[0].kind, "probe")
            self.assertEqual(pqdt_ops[0].kind, "probe")
            self.assertEqual(
                [item.operation_id for item in atai_ops[1:4]],
                ["O02-FIELD-NOFT", "O03-FIELD-SU", "O04-FIELD-IF"],
            )
            self.assertEqual(
                [item.operation_id for item in pqdt_ops[1:6]],
                [
                    "O02-FIELD-TI",
                    "O03-FIELD-AB",
                    "O04-FIELD-SU",
                    "O05-FIELD-IF",
                    "O06-FIELD-NOFT",
                ],
            )
            self.assertTrue(all(item.count_only for item in atai_ops[1:13]))
            self.assertTrue(all(item.count_only for item in pqdt_ops[1:15]))
            self.assertTrue(pqdt_ops[-1].require_complete)
            self.assertEqual(pqdt_ops[-1].bounded_limit, 40)
            self.assertEqual(pqdt_ops[-1].bounded_max_pages, 2)
            self.assertEqual(
                pqdt_ops[-1].conditional_total_operation_id,
                "O07-PARTITION-A1",
            )

    def test_runner_commands_use_one_loopback_endpoint_and_pqdt_safe_modes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet = self.packet_root(root, "pqdt")
            date = runner.dt.date(2026, 8, 25)
            ops = runner.build_operations("proquest-pqdt", packet_root=packet, pilot_date=date)
            plan = runner.render_plan(
                "proquest-pqdt",
                operations=ops,
                packet_root=packet,
                adapter_path=root / "search_pqdt.py",
                probe_path=root / "probe.py",
                output_dir=root / "outputs",
                pilot_date=date,
                cdp_url=runner.DEFAULT_CDP_URL,
            )
            self.assertEqual(plan["predeclared_operation_cap"], 16)
            encoded = json.dumps(plan)
            self.assertIn("YR(2011-2026) AND LA(English)", encoded)
            self.assertIn("--count-only", encoded)
            self.assertIn("--require-complete", encoded)
            self.assertEqual(
                plan["operations"][-1]["conditional_total"],
                {"operation_id": "O07-PARTITION-A1", "minimum": 1, "maximum": 40},
            )
            self.assertNotIn("9223", encoded)
            self.assertNotIn("fresh-browser", encoded)

    def test_strict_operation_is_not_run_outside_predeclared_total_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dependency = root / "O07-PARTITION-A1.json"
            strict = root / "O16-STRICT-A1.json"
            ledger = root / "runner-ledger.json"
            plan = {
                "source_id": "proquest-pqdt",
                "predeclared_operation_cap": 2,
                "retry_policy": {},
                "operations": [
                    {
                        "operation_id": "O07-PARTITION-A1",
                        "output_path": str(dependency),
                        "conditional_total": None,
                        "command": [
                            sys.executable,
                            "-c",
                            (
                                "from pathlib import Path; "
                                f"Path({str(dependency)!r}).write_text('''{{\"total\": 41}}''')"
                            ),
                        ],
                    },
                    {
                        "operation_id": "O16-STRICT-A1",
                        "output_path": str(strict),
                        "conditional_total": {
                            "operation_id": "O07-PARTITION-A1",
                            "minimum": 1,
                            "maximum": 40,
                        },
                        "command": [
                            sys.executable,
                            "-c",
                            f"from pathlib import Path; Path({str(strict)!r}).touch()",
                        ],
                    },
                ],
            }
            self.assertEqual(runner.run_plan(plan, output_dir=root), 0)
            self.assertFalse(strict.exists())
            payload = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(payload["performed_operations"], 1)
            self.assertEqual(payload["operations"][-1]["status"], "not_run")
            self.assertEqual(payload["operations"][-1]["dependency_total"], 41)

    def test_failed_child_preserves_bounded_stderr_diagnostic_in_output_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = {
                "source_id": "proquest-pqdt",
                "predeclared_operation_cap": 1,
                "retry_policy": {"maximum_source_reissues": 0},
                "operations": [
                    {
                        "operation_id": "O01-FAILURE",
                        "output_path": str(root / "O01-FAILURE.json"),
                        "command": [
                            sys.executable,
                            "-c",
                            "import sys; sys.stderr.write('safe diagnostic\\n'); sys.exit(7)",
                        ],
                    }
                ],
            }
            self.assertEqual(runner.run_plan(plan, output_dir=root), 7)
            ledger = json.loads((root / "runner-ledger.json").read_text(encoding="utf-8"))
            operation = ledger["operations"][0]
            diagnostic = root / operation["stderr_diagnostic_path"]
            self.assertEqual(diagnostic.read_text(encoding="utf-8"), "safe diagnostic\n")
            self.assertEqual(diagnostic.stat().st_mode & 0o077, 0)
            self.assertEqual(
                operation["stderr_sha256"],
                hashlib.sha256(diagnostic.read_bytes()).hexdigest(),
            )

    def test_probe_endpoint_and_projection_fail_closed(self) -> None:
        self.assertEqual(
            probe._validate_cdp_url("http://127.0.0.1:9222"),
            "http://127.0.0.1:9222",
        )
        for value in ("http://127.0.0.1:9223", "https://127.0.0.1:9222", "http://example.invalid:9222"):
            with self.subTest(value=value), self.assertRaises(probe.ProbeInputError):
                probe._validate_cdp_url(value)

        valid = {
            "protocol": "https:",
            "host": "www.proquest.com",
            "path": "/ataindex/commandline",
            "titleHasProQuest": True,
            "accessMarker": False,
            "subjectControlCount": 0,
            "indexControlCount": 1,
            "thesaurusControlCount": 0,
            "titleFieldCount": 1,
            "abstractFieldCount": 1,
            "queryFieldCount": 1,
            "visibleResultOrRecordFieldCount": 1,
        }
        parsed = probe.parse_probe_state(valid, source="proquest-atai")
        self.assertEqual(parsed["visible_allowlisted_counts"]["indexControlCount"], 1)
        invalid = {**valid, "host": "elsewhere.invalid"}
        with self.assertRaises(probe.ProbeProtocolError):
            probe.parse_probe_state(invalid, source="proquest-atai")
        with self.assertRaises(probe.ProbeProtocolError):
            probe.parse_probe_state({**valid, "accessMarker": True}, source="proquest-atai")

    def test_probe_dry_run_never_requires_playwright(self) -> None:
        receipt = probe.dry_run_receipt(
            "proquest-pqdt",
            adapter_path=Path("trusted/search_pqdt.py"),
            cdp_url=probe.DEFAULT_CDP_URL,
        )
        self.assertEqual(receipt["status"], "dry_run")
        self.assertFalse(receipt["browser_action_performed"])
        self.assertIsNone(receipt["observations"])
        self.assertIn("subject/keyword", " ".join(receipt["planned_observations"]))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
