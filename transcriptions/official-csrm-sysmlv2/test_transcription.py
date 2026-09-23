"""Offline completeness and repeatability checks for the pinned CSRM transcription."""

import hashlib
import json
from pathlib import Path
import unittest

from transcribe import Transcriber, XMI, kind

HERE = Path(__file__).resolve().parent


class TranscriptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HERE / "source" / "CSRM.xmi"
        cls.generator = Transcriber(cls.source)
        cls.model, cls.mapping, cls.coverage = cls.generator.generate()

    def test_pinned_source_and_generated_files(self):
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(),
                         "52c48e735f1c497e1bcba5d152747b461c257c1cbe32391919dc196a3e32f99f")
        self.assertEqual(self.model, (HERE / "CSRM.sysml").read_text(encoding="utf-8"))
        self.assertEqual(self.mapping, json.loads((HERE / "source-map.json").read_text(encoding="utf-8")))
        self.assertEqual(self.coverage, json.loads((HERE / "coverage.json").read_text(encoding="utf-8")))

    def test_every_typed_uml_id_is_accounted_for(self):
        source_ids = {element.get(XMI + "id") for element in self.generator.model.iter() if kind(element)}
        self.assertEqual(source_ids, set(self.mapping))
        self.assertEqual(len(source_ids), 1986)
        self.assertTrue(all(source_id in self.model for source_id in source_ids))
        self.assertEqual(self.coverage["unaccounted_ids"], [])

    def test_dependencies_and_associations_are_resolved(self):
        expected = {"uml:Association": 134, "uml:Abstraction": 101, "uml:Dependency": 14,
                    "uml:Activity": 47, "uml:ControlFlow": 22, "uml:ObjectFlow": 44,
                    "uml:Class": 335, "uml:Package": 255}
        for kind_name, count in expected.items():
            self.assertEqual(self.coverage["source_kind_counts"][kind_name], count)
        for entry in self.mapping.values():
            if entry["source_kind"] in {"uml:Association", "uml:Abstraction", "uml:Dependency"}:
                self.assertIn(entry["target"].split("::")[-1], self.model)
        self.assertIn("@OfficialCSRMProfile::", self.model)

    def test_profile_inventory(self):
        data = json.loads((HERE / "profile-map.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["stereotypes"]), 53)
        self.assertEqual(data["sha256"], hashlib.sha256(
            (HERE / "source" / "CSRM-Profile-23-11-16.xmi").read_bytes()).hexdigest())
        self.assertIn("metadata def 'MissionRequirement'", (HERE / "CSRMProfile.sysml").read_text())


if __name__ == "__main__":
    unittest.main()
