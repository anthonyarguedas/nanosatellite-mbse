#!/usr/bin/env python3
"""Exercise shared synthetic PQDT/OATD interface-state fixtures."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
EXTERNAL_SCRIPTS = Path("/Users/antho/agent-tools/academic-research/skills/academic-search/scripts")
FIXTURES = TOOLS.parent / "fixtures" / "thesis-source-count-gate-v1.6.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"Could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


oatd = load_module(
    "fixture_oatd_basic_count_gate",
    EXTERNAL_SCRIPTS / "oatd_basic_count_gate.py",
)
pqdt = load_module(
    "fixture_search_proquest_pqdt_global",
    EXTERNAL_SCRIPTS / "search_proquest_pqdt_global.py",
)


class SharedFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
        if cls.fixtures.get("contains_candidate_records") is not False:
            raise AssertionError("shared count-gate fixtures must contain no candidate records")

    def assert_outcome(self, function, fixture: dict[str, object]) -> None:
        expected = fixture["expected"]
        if expected == "success":
            function(fixture["state"])
        elif expected == "access_error":
            with self.assertRaises((oatd.AccessGateError, pqdt.AccessGateError)):
                function(fixture["state"])
        elif expected == "protocol_error":
            with self.assertRaises((oatd.ProtocolGateError, pqdt.ProtocolGateError)):
                function(fixture["state"])
        else:  # pragma: no cover
            self.fail(f"unknown fixture outcome {expected!r}")

    def test_oatd_count_states(self) -> None:
        for fixture in self.fixtures["oatd_count_states"]:
            with self.subTest(fixture=fixture["fixture_id"]):
                self.assert_outcome(oatd.parse_count_state, fixture)

    def test_pqdt_database_states(self) -> None:
        for fixture in self.fixtures["pqdt_database_states"]:
            with self.subTest(fixture=fixture["fixture_id"]):
                self.assert_outcome(pqdt.parse_database_state, fixture)

    def test_pqdt_form_states(self) -> None:
        for fixture in self.fixtures["pqdt_form_states"]:
            with self.subTest(fixture=fixture["fixture_id"]):
                self.assert_outcome(pqdt.parse_form_state, fixture)

    def test_pqdt_count_states(self) -> None:
        for fixture in self.fixtures["pqdt_count_states"]:
            with self.subTest(fixture=fixture["fixture_id"]):
                self.assert_outcome(pqdt.parse_count_state, fixture)


if __name__ == "__main__":
    unittest.main()
