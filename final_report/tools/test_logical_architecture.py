"""Focused six-component source/ledger/safety tests, independent of task7 audit.

These unit tests exercise report parsing and checker rejection logic. Native
semantic validation is executed by check_logical_responsibilities.py, not mocked
or replaced by source regexes here.
"""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

REPORT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("logical_checker", REPORT / "sysml/check_logical_responsibilities.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class LogicalSourceTests(unittest.TestCase):
    def setUp(self):
        self.ledger = json.loads((REPORT / "traceability/logical-architecture.json").read_text())
        self.requirements = (REPORT / "requirements.tex").read_text()
        self.logical = (REPORT / "logical.tex").read_text()
        self.io = (REPORT / 'fr-inputs-outputs.tex').read_text()

    def check(self):
        return checker.validate_source_contract(self.ledger, self.requirements, self.logical, self.io)

    def test_current_contract(self):
        source = self.check()
        self.assertEqual(len(source), 40)
        self.assertEqual(sum(len(r["parents"]) for r in source.values()), 169)

    def test_renderer_call_joins_appendix_without_api_change(self):
        source = checker.validate_source_contract(self.ledger, self.requirements, self.logical)
        self.assertEqual(len(source), 40)
        self.assertEqual(source['FR-18']['inputs_verbatim'], self.check()['FR-18']['inputs_verbatim'])

    def test_name_id_first_frs_second_interfaces_third(self):
        table = checker.parse_logical_table(self.logical)
        self.assertEqual(table["L01"]["name"], "Requirements and guidance")
        self.assertEqual(table["L01"]["FR"], ["FR-01", "FR-02", "FR-03", "FR-04", "FR-17", "FR-29", "FR-39", "FR-41"])
        self.assertIn("$\\rightarrow$", table["L01"]["interfaces"])

    def test_missing_allocation(self):
        self.ledger["allocations"].pop()
        with self.assertRaisesRegex(ValueError, "Missing or retired allocation"):
            self.check()

    def test_duplicate_allocation(self):
        self.ledger["allocations"].append(copy.deepcopy(self.ledger["allocations"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate allocation"):
            self.check()

    def test_retired_allocations(self):
        for fr in ("FR-12", "FR-40"):
            with self.subTest(fr=fr):
                row = copy.deepcopy(self.ledger["allocations"][0])
                row["FR"] = fr
                self.ledger["allocations"].append(row)
                with self.assertRaisesRegex(ValueError, "Missing or retired allocation"):
                    self.check()
                self.ledger["allocations"].pop()

    def test_wrong_primary_owner(self):
        self.ledger["allocations"][0]["primary"] = "L02"
        with self.assertRaisesRegex(ValueError, "Wrong primary allocation"):
            self.check()

    def test_missing_table_allocation(self):
        self.logical = self.logical.replace("01--04, 17, 29, 39, 41", "01--03, 17, 29, 39, 41")
        with self.assertRaisesRegex(ValueError, "Missing/duplicate/retired table allocation"):
            self.check()

    def test_duplicate_table_allocation(self):
        self.logical = self.logical.replace("13--15, 20, 25, 33, 35", "01, 13--15, 20, 25, 33, 35")
        with self.assertRaisesRegex(ValueError, "Missing/duplicate/retired table allocation"):
            self.check()

    def test_retired_table_allocation(self):
        self.logical = self.logical.replace("13--15, 20, 25, 33, 35", "12--15, 20, 25, 33, 35")
        with self.assertRaisesRegex(ValueError, "Missing/duplicate/retired table allocation"):
            self.check()

    def test_duplicate_number_within_row(self):
        with self.assertRaisesRegex(ValueError, "Duplicate number"):
            checker.expand_numbers("01--04, 04")

    def test_missing_input_union(self):
        self.ledger["components"][0]["io_union"]["inputs"].pop()
        with self.assertRaisesRegex(ValueError, "IO union mismatch"):
            self.check()

    def test_extra_output_union(self):
        self.ledger["components"][0]["io_union"]["outputs"].append({"field": "invented output", "provenance": ["FR-01"]})
        with self.assertRaisesRegex(ValueError, "IO union mismatch"):
            self.check()

    def test_union_wrong_provenance(self):
        self.ledger["components"][0]["io_union"]["inputs"][0]["provenance"] = ["FR-13"]
        with self.assertRaisesRegex(ValueError, "IO union provenance mismatch"):
            self.check()

    def test_union_duplicate_provenance(self):
        row = self.ledger["components"][0]["io_union"]["inputs"][0]
        row["provenance"] += row["provenance"]
        with self.assertRaisesRegex(ValueError, "IO union provenance mismatch"):
            self.check()

    def test_exchange_wrong_direction(self):
        self.ledger["exchanges"][0]["bindings"][0]["source_direction"] = "in"
        with self.assertRaisesRegex(ValueError, "Exchange direction mismatch"):
            self.check()

    def test_exchange_wrong_owner_provenance(self):
        self.ledger["exchanges"][0]["bindings"][0]["source_FR"] = "FR-13"
        with self.assertRaisesRegex(ValueError, "Exchange FR provenance/owner mismatch"):
            self.check()

    def test_exchange_unknown_field(self):
        self.ledger["exchanges"][0]["bindings"][0]["source_fields"] = ["nonexistent"]
        with self.assertRaisesRegex(ValueError, "Exchange IO field provenance mismatch"):
            self.check()

    def test_exchange_missing_mapping(self):
        self.ledger["exchanges"][0]["bindings"][0]["mapping"] = ""
        with self.assertRaisesRegex(ValueError, "explicit mapping"):
            self.check()

    def test_changed_requirement_meaning(self):
        self.ledger["allocations"][0]["statement"] = "Different obligation."
        with self.assertRaisesRegex(ValueError, "Stale final FR contract"):
            self.check()

    def test_changed_parent(self):
        self.ledger["allocations"][0]["parents"] = ["MR-06"]
        with self.assertRaisesRegex(ValueError, "Stale final FR contract"):
            self.check()

    def test_changed_check(self):
        self.ledger["allocations"][0]["verification"]["need"] = "Different verification need."
        with self.assertRaisesRegex(ValueError, "Changed final source contract"):
            self.check()

    def test_false_verification_outcome(self):
        self.ledger["allocations"][0]["verification"]["status"] = "executed, passed"
        with self.assertRaises(ValueError):
            self.check()

    def test_final_mop_names(self):
        self.ledger["allocations"][0]["native_mop"] = "FrameworkRequirements::MOP_01"
        with self.assertRaises(ValueError):
            self.check()

    def test_full_names_are_exact(self):
        self.logical = self.logical.replace("L05 Evidence and technical review", "L05 Review")
        with self.assertRaisesRegex(ValueError, "Logical name disagreement"):
            self.check()

    def test_native_pending_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "synchronization incomplete"):
            checker.check_native_architecture(None, {"native_status": "pending", "native_contract": None})

    def test_core_boundary_excludes_physical(self):
        self.assertEqual(len(checker.CORE_FILES), 9)
        self.assertFalse(any("candidate" in f or "physical" in f or "07-report" in f for f in checker.CORE_FILES))


class SafetyRejectionTests(unittest.TestCase):
    def test_exact_selector_required(self):
        for text, selector in (("abc", "missing"), ("abc abc", "abc"), ("abc", "")):
            with self.subTest(text=text, selector=selector):
                with self.assertRaisesRegex(ValueError, "selector must match exactly once"):
                    checker.mutate_exact(text, selector, "unsafe")

    def test_mutation_must_change_source(self):
        with self.assertRaisesRegex(ValueError, "must change source"):
            checker.mutate_exact("guard", "guard", "guard")

    def test_matching_selector_mutates(self):
        self.assertEqual(checker.mutate_exact("if authorized then apply", "authorized", "true"), "if true then apply")

    def test_lost_authority_or_currency_guard(self):
        expected = "dispose.authorized and checkApplication.sameContext"
        for unsafe in ("true", "dispose.authorized", "checkApplication.sameContext"):
            with self.subTest(unsafe=unsafe):
                with self.assertRaisesRegex(ValueError, "Lost required safety guard"):
                    checker.validate_guard(unsafe, expected, "apply", "apply")

    def test_lost_release_blocker_or_exact_revision(self):
        expected = "checkRelease.authorizedDetailedDesign and checkRelease.currentDesign and checkRelease.blockersClear and interfaces.profileCompatible"
        for fragment in expected.split(" and "):
            with self.subTest(fragment=fragment):
                unsafe = " and ".join(x for x in expected.split(" and ") if x != fragment)
                with self.assertRaisesRegex(ValueError, "Lost required safety guard"):
                    checker.validate_guard(unsafe, expected, "coordinate", "coordinate")

    def test_lost_review_consistency_or_closure(self):
        expected = "checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete)"
        with self.assertRaisesRegex(ValueError, "Lost required safety guard"):
            checker.validate_guard("checkDecision.authorized and checkDecision.current", expected, "record", "record")

    def test_lost_calibration_independence(self):
        with self.assertRaisesRegex(ValueError, "Lost required safety guard"):
            checker.validate_guard("checkData.dataUsable", "checkData.dataUsable and checkData.independentSeparation", "propose", "propose")

    def test_lost_replay_dependency_or_fixed_rules(self):
        expected = "prepare.dependenciesComplete and prepare.rulesFixed"
        for unsafe in ("prepare.dependenciesComplete", "prepare.rulesFixed"):
            with self.subTest(unsafe=unsafe):
                with self.assertRaisesRegex(ValueError, "Lost required safety guard"):
                    checker.validate_guard(unsafe, expected, "execute", "execute")

    def test_tool_failure_never_counts_as_rejection(self):
        for code, message in ((1, "FAIL: Native tooling unavailable: license"),
                              (3, "FAIL: native dependency missing"),
                              (1, "Traceback: checker bug"), (0, "")):
            with self.subTest(code=code, message=message):
                with self.assertRaisesRegex(ValueError, "not rejected"):
                    checker.require_native_mutation_rejection(code, message)

    def test_semantic_counterexample_counts_as_rejection(self):
        checker.require_native_mutation_rejection(1, "FAIL: Native safety guard counterexample")

    def test_independent_guard_basis_and_complete_native_mapping_count(self):
        ledger = json.loads((REPORT / "traceability/logical-architecture.json").read_text())
        expected = [{"native": f"LogicalRealization::{name}::{gate}", "expression": expr,
                     "target": f"LogicalRealization::{name}::{target}"}
                    for name, rows in checker.GUARDS.items() for gate, (expr, target) in rows.items()]
        self.assertEqual(ledger["safety_contract"]["guards"], expected)
        self.assertEqual(sum(len(e["mappings"]) for e in ledger["exchanges"]), 203)
        self.assertEqual(len(ledger["external_exchanges"]), 5)
        self.assertEqual(len(ledger["safety_contract"]["tasks"]), 142)

    def test_guard_wrong_target(self):
        with self.assertRaisesRegex(ValueError, "wrong action"):
            checker.validate_guard("authorized", "authorized", "build", "hold")

    def test_release_gate_dominance(self):
        safe_edges = [("start", "checkRelease"), ("coordinate", "codeBuildSil")]
        self.assertNotIn("codeBuildSil", checker.reachable_without_gate(safe_edges, {"start"}))
        unsafe_edges = safe_edges + [("checkRelease", "codeBuildSil")]
        self.assertIn("codeBuildSil", checker.reachable_without_gate(unsafe_edges, {"start"}))


if __name__ == "__main__":
    unittest.main()
