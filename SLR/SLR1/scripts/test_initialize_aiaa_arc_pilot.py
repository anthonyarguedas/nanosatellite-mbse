"""Offline regression tests for the AIAA ARC P01 allocation materializer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent.parent
HELPER = SCRIPT_DIR / "initialize_aiaa_arc_pilot.py"
ADAPTER = ROOT.parent / "agent-tools/academic-research/skills/academic-search/scripts/search_aiaa_arc.py"
PLAN = ROOT / "SLR/SLR1/searches/sources/s-d10-aiaa-arc/p01-execution-plan.md"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import initialize_aiaa_arc_pilot as initializer  # noqa: E402


class AiaaArcPilotMaterializationTests(unittest.TestCase):
    def temporary_root(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        searches = root / "SLR/SLR1/searches"
        (searches / "templates").mkdir(parents=True)
        (searches / "sources/s-d10-aiaa-arc").mkdir(parents=True)
        shutil.copyfile(
            ROOT / "SLR/SLR1/searches/templates/pilot-campaign.template.json",
            searches / "templates/pilot-campaign.template.json",
        )
        shutil.copyfile(
            ROOT / "SLR/SLR1/searches/templates/pilot-manifest.template.json",
            searches / "templates/pilot-manifest.template.json",
        )
        (root / "SLR/SLR1/protocol.md").write_text(
            "offline protocol\n", encoding="utf-8"
        )
        (searches / "search-concept-dictionary.json").write_text(
            "offline dictionary\n", encoding="utf-8"
        )
        return temporary

    def test_materializes_empty_runtime_scaffold_from_shared_templates(self) -> None:
        temporary = self.temporary_root()
        try:
            root = Path(temporary.name)
            campaign_path, manifest_path = initializer.materialize(
                root,
                now="20260825T002312+0000",
                protocol_commit="b" * 40,
            )
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            attempt = campaign["attempts"][0]

            self.assertEqual("S-D10-C01-20260825T002312+0000", campaign["campaign_id"])
            self.assertEqual("S-D10-P01-20260825T002312+0000", attempt["attempt_id"])
            self.assertEqual("aiaa-arc", campaign["source_id"])
            self.assertEqual("in_progress", campaign["status"])
            self.assertEqual(12, len(campaign["capability_catalog"]))
            self.assertEqual(initializer.GATE_IDS, tuple(campaign["capability_catalog"]))
            self.assertEqual(1, len(campaign["attempts"]))
            self.assertEqual(2, attempt["source_operations"]["predeclared_maximum"])
            self.assertEqual([], attempt["source_operations"]["operations"])
            self.assertEqual(0, attempt["source_operations"]["performed"])
            self.assertEqual([], attempt["evidence"])
            self.assertTrue(all(gate["status"] == "untested" for gate in campaign["capability_gates"]))
            self.assertTrue(all(gate["evidence"] == [] for gate in campaign["capability_gates"]))
            self.assertEqual([], campaign["decisions"])
            self.assertEqual([], manifest["executions"])
            self.assertEqual([], manifest["checks"])
            self.assertEqual([], manifest["artifacts"])
            self.assertNotIn("attempt_terminal", manifest)
            self.assertEqual(campaign["campaign_id"], manifest["campaign"]["campaign_id"])
            self.assertEqual(attempt["attempt_id"], manifest["pilot_id"])
            self.assertEqual(
                hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                attempt["manifest_sha256"],
            )
            serialized = json.dumps([campaign, manifest], ensure_ascii=False)
            self.assertNotIn("S-D01", serialized)
            self.assertNotIn("scopus", serialized)
            self.assertNotIn("provider/model", serialized)
            self.assertNotIn("example.invalid", serialized)
        finally:
            temporary.cleanup()

    def test_materialization_is_no_clobber_and_timestamp_is_utc(self) -> None:
        temporary = self.temporary_root()
        try:
            root = Path(temporary.name)
            initializer.materialize(root, now="20260825T002312+0000", protocol_commit="c" * 40)
            with self.assertRaises(FileExistsError):
                initializer.materialize(
                    root, now="20260825T002312+0000", protocol_commit="c" * 40
                )
            with self.assertRaises(initializer.MaterializationError):
                initializer.materialize(
                    root / "unused", now="20260825T002312-0400", protocol_commit="c" * 40
                )
        finally:
            temporary.cleanup()

    def test_cli_help_is_offline(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(HELPER), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        self.assertIn("--now", completed.stdout)
        self.assertIn("no source work", completed.stdout)

    def test_sibling_adapter_derives_sidecar_before_json_suffix(self) -> None:
        spec = importlib.util.spec_from_file_location("aiaa_arc_sidecar_contract", ADAPTER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        output = Path("/restricted/op-01-count-b1.json")
        self.assertEqual(
            Path("/restricted/op-01-count-b1.NON_MERGEABLE_FAILURE.json"),
            module.non_mergeable_diagnostic_path(output),
        )

    def test_plan_has_fail_closed_sidecar_and_child_handoff_contract(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        self.assertIn('OP1_DIAGNOSTIC="${OP1%.json}.NON_MERGEABLE_FAILURE.json"', text)
        self.assertIn('OP2_DIAGNOSTIC="${OP2%.json}.NON_MERGEABLE_FAILURE.json"', text)
        self.assertIn('ROOT="$ROOT" PACKET="$PACKET" RESTRICTED="$RESTRICTED"', text)
        self.assertIn("OP2_STATUS", text)
        self.assertIn("execution_completion_status ==", text)
        self.assertIn('else "partial" end', text)
        self.assertIn('then "count_only"', text)
        self.assertIn('(($root.results | length) == 0)', text)
        self.assertNotIn("$OP1.NON_MERGEABLE_FAILURE.json", text)
        self.assertNotIn("$OP2.NON_MERGEABLE_FAILURE.json", text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
