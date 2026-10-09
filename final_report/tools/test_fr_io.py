"""Exact-ID joins and rejection checks for the separate appendix FR IO table."""
from pathlib import Path
import runpy

import audit_report as audit
from test_audit_report import Fixture

REPORT = Path(__file__).resolve().parents[1]
LOGICAL = runpy.run_path(str(REPORT/'sysml/check_logical_responsibilities.py'))
SCENARIO = runpy.run_path(str(REPORT/'sysml/check_scenarios.py'))


class FRIOTableTests(Fixture):
    def setUp(self):
        super().setUp()
        self.io_path = self.root/audit.FR_IO_SOURCE
        self.io_text = self.io_path.read_text()
        self.main_path = self.root/'requirements.tex'
        self.main_text = self.main_path.read_text()
        self.ledger = audit.load(self.root/'traceability/framework-baseline.json')
        self.logical = audit.load(self.root/'traceability/logical-architecture.json')

    def validators(self):
        return (
            lambda: audit.current_trace(self.root),
            lambda: LOGICAL['validate_source_contract'](
                self.logical, self.main_path.read_text(),
                (self.root/'logical.tex').read_text(), self.io_path.read_text()),
            lambda: SCENARIO['validate_report_contract'](
                self.main_path.read_text(), self.io_path.read_text(), self.ledger),
        )

    def reject_all(self):
        for number, validate in enumerate(self.validators()):
            with self.subTest(checker=number):
                with self.assertRaises((AssertionError, ValueError)):
                    validate()

    def test_same_exact_join_for_report_logical_and_scenario(self):
        report = audit.current_trace(self.root)[1]
        logical = self.validators()[1]()
        scenario = self.validators()[2]()
        self.assertEqual(set(report), audit.ACTIVE_FR)
        for rid, row in report.items():
            self.assertEqual(logical[rid]['statement'], row['text'])
            self.assertEqual(logical[rid]['parents'], row['parents'])
            for direction in ('inputs', 'outputs'):
                self.assertEqual(logical[rid][direction + '_verbatim'], row[direction])
                self.assertEqual(scenario[rid][direction], row[direction])

    def test_every_io_cell_is_content_protected(self):
        for rid, row in self.fr.items():
            for direction in ('inputs', 'outputs'):
                with self.subTest(FR=rid, direction=direction):
                    old = row[direction]
                    self.assertEqual(self.io_text.count(old), 1)
                    self.io_path.write_text(self.io_text.replace(old, old + ' Changed.'))
                    self.reject_all()
        self.io_path.write_text(self.io_text)

    def test_every_direction_swap_is_rejected(self):
        for rid, row in self.fr.items():
            with self.subTest(FR=rid):
                old = f"{rid} & {row['inputs']} & {row['outputs']}"
                new = f"{rid} & {row['outputs']} & {row['inputs']}"
                self.assertEqual(self.io_text.count(old), 1)
                self.io_path.write_text(self.io_text.replace(old, new))
                self.reject_all()
        self.io_path.write_text(self.io_text)

    def test_missing_duplicate_extra_and_malformed_ids(self):
        row = next(line for line in self.io_text.splitlines() if line.startswith('FR-01 &'))
        for replacement in ('', row + '\n' + row, row + '\n' + row.replace('FR-01', 'FR-99'),
                            row + '\n' + row.replace('FR-01', 'FR-100'),
                            row + '\n' + row.replace('FR-01', 'UNKNOWN-ID'),
                            row.replace('FR-01', 'fr-01')):
            with self.subTest(replacement=replacement[:35]):
                self.io_path.write_text(self.io_text.replace(row, replacement))
                self.reject_all()

    def test_io_assigned_to_wrong_id(self):
        first, second = self.fr['FR-01'], self.fr['FR-02']
        old1 = f"FR-01 & {first['inputs']} & {first['outputs']}"
        old2 = f"FR-02 & {second['inputs']} & {second['outputs']}"
        text = self.io_text.replace(old1, f"FR-01 & {second['inputs']} & {second['outputs']}")
        text = text.replace(old2, f"FR-02 & {first['inputs']} & {first['outputs']}")
        self.io_path.write_text(text)
        self.reject_all()

    def test_remaining_main_table_or_prose_duplication(self):
        for addition in (r'\par \textit{Inputs:} copied.', self.fr['FR-18']['outputs']):
            with self.subTest(addition=addition[:30]):
                self.main_path.write_text(self.main_text + '\n' + addition + '\n')
                self.reject_all()

    def test_duplication_elsewhere_in_body(self):
        path = self.root/'logical.tex'
        path.write_text(path.read_text() + '\n' + self.fr['FR-01']['inputs'])
        with self.assertRaisesRegex(AssertionError, 'Remaining body FR IO duplication'):
            audit.current_trace(self.root)

    def test_exact_repeated_columns_and_valid_references(self):
        header = r'\textbf{ID} & \textbf{Inputs} & \textbf{Outputs}'
        for changed in (header.replace('Inputs', 'Incoming'),
                        r'\textbf{ID} & \textbf{Outputs} & \textbf{Inputs}',
                        header + r' & \textbf{Extra}'):
            with self.subTest(header=changed):
                self.io_path.write_text(self.io_text.replace(header, changed, 1))
                self.reject_all()
        self.io_path.write_text(self.io_text)
        for label in ('tab:framework-io', 'appendix:framework-io'):
            with self.subTest(label=label):
                self.main_path.write_text(self.main_text.replace(r'\ref{' + label + '}', 'removed'))
                self.reject_all()

    def test_fragment_included_exactly_once(self):
        path = self.root/'apendice.tex'
        original = path.read_text()
        for changed in (original.replace(r'\input{fr-inputs-outputs}', ''),
                        original + '\n' + r'\input{fr-inputs-outputs}'):
            path.write_text(changed)
            with self.assertRaisesRegex(AssertionError, 'included exactly once'):
                audit.current_trace(self.root)

    def test_group_and_order_retained(self):
        self.io_path.write_text(self.io_text.replace('Mission concepts and preliminary design', 'Changed group'))
        self.reject_all()
        lines = self.io_text.splitlines()
        first = next(i for i, line in enumerate(lines) if line.startswith('FR-01 &'))
        lines[first], lines[first + 1] = lines[first + 1], lines[first]
        self.io_path.write_text('\n'.join(lines) + '\n')
        self.reject_all()
