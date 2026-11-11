"""Generic recovery-orbit expressions, acceptance and lifecycle behavior."""

import tempfile
import unittest
from pathlib import Path

from nanosat_mbse import CubeSat, Orbit, PendingValue, Session
from nanosat_mbse.benches import create_report_session
from nanosat_mbse.persistence import dumps, loads


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.session = s = Session()
        s.add(Orbit())
        s.add(CubeSat())
        self.row = self.generic("BatteryRecoveryOrbits")
        self.generic("OrbitPeriod").set_value("altitude_km", 416.86)
        self.generic("CycleLife").set_value("dod_max", .6)
        capacity = self.generic("BatteryCapacityScreen")
        capacity.set_value("pack_bol_J", 95.04 * 3600)
        capacity.set_value("retained_energy_factor", 1)
        self.generic("EPS02").set_value("sunlight_generation_J", 1.634 * 3600)
        load = self.generic("LoadEnergy")
        for name, value in {
            "sunlight_s": 3240, "eclipse_s": 2160,
            "sunlight_power_W": .623 / 1.5, "eclipse_power_W": .623 / 1.5,
            "sunlight_duty": 1, "eclipse_duty": 1,
        }.items():
            load.set_value(name, value)

    def generic(self, name):
        return next(row for row in self.session.requirements
                    if row.definition == f"FrameworkRequirements::{name}" and row.subject is None)

    def test_reference_limit_starts_blank_while_recovery_is_calculated(self):
        self.assertIsNone(self.row.parameters["max_recovery_orbits"].value)
        self.assertIsNone(self.row.parameters["max_recovery_orbits"].expression)
        self.assertAlmostEqual(self.row.value("recovery_orbits"), 56.403560830860535)
        self.assertEqual(self.row.verify().state.value, "pending")
        self.row.set_value("max_recovery_orbits", 57)
        self.assertTrue(self.row.verify().verified)
        self.row.set_value("max_recovery_orbits", 56)
        self.assertEqual(self.row.verify().state.value, "fail")

    def test_upstream_capacity_retention_and_dod_edits_propagate(self):
        before = self.row.value("recovery_orbits")
        self.generic("CycleLife").set_value("dod_max", .3)
        self.assertAlmostEqual(self.row.value("recovery_orbits"), before / 2)
        self.generic("BatteryCapacityScreen").set_value("retained_energy_factor", .8)
        self.assertAlmostEqual(self.row.value("recovery_orbits"), before * .4)

    def test_nonpositive_surplus_is_unrecoverable_and_fails_without_division(self):
        for generation in (.623, .5):
            with self.subTest(generation=generation):
                self.row.set_value("generated_energy_J", generation * 3600)
                with self.assertRaises(PendingValue):
                    self.row.value("recovery_orbits")
                self.assertEqual(self.row.verify().state.value, "fail")

    def test_zero_dod_needs_zero_orbits_even_without_a_surplus(self):
        self.row.set_value("recovery_dod", 0)
        self.row.set_value("generated_energy_J", 0)
        self.row.set_value("max_recovery_orbits", 0)
        self.assertEqual(self.row.value("recovery_orbits"), 0)
        self.assertTrue(self.row.verify().verified)

    def test_invalid_dod_and_limit_fail_the_requirement(self):
        self.row.set_value("max_recovery_orbits", 100)
        for dod in (-.1, 1.1):
            self.row.set_value("recovery_dod", dod)
            self.assertEqual(self.row.verify().state.value, "fail")
        self.row.set_value("recovery_dod", .6)
        self.row.set_value("max_recovery_orbits", -1)
        self.assertEqual(self.row.verify().state.value, "fail")

    def test_round_trip_retains_expression_and_deliberate_deletion(self):
        restored = loads(dumps(self.session))
        self.assertAlmostEqual(restored.value(self.row.id, "recovery_orbits"), self.row.value("recovery_orbits"))
        self.session.remove(self.row)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.py"
            self.session.save(path)
            restored = Session.open(path)
            self.assertFalse(any(row.definition == "FrameworkRequirements::BatteryRecoveryOrbits"
                                 for row in restored.requirements))

    def test_reconciliation_adds_new_generic_defaults_once(self):
        s = Session()
        bus = s.add(CubeSat(), initialize=False)
        from nanosat_mbse import EPS
        s.add(EPS(), owner=bus, initialize=False)
        s.reconcile_defaults()
        count = len(s.requirements)
        s.reconcile_defaults()
        self.assertEqual(len(s.requirements), count)
        self.assertEqual(sum(row.definition == "FrameworkRequirements::BatteryRecoveryOrbits"
                             for row in s.requirements), 1)

    def test_energy_study_has_script_bound_recovery_inputs(self):
        s = create_report_session("energy")
        row = next(row for row in s.requirements if row.definition == "FrameworkRequirements::BatteryRecoveryOrbits")
        self.assertEqual(row.parameters["pack_eol_J"].expression, "INP002.energy_capacity_J")
        self.assertIn("SCR002.source_energy_J", row.parameters["generated_energy_J"].expression)
        self.assertIsNone(row.parameters["max_recovery_orbits"].value)


if __name__ == "__main__":
    unittest.main()
