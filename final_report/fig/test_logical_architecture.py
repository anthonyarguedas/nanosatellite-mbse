"""Checks for the single-view logical architecture.

PYTHONPATH=final_report/fig python3 -m unittest test_logical_architecture
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET

from diagram_style import (SerifMetrics, foreground_arrowheads, run, sha,
                           validate_arrowheads, validate_port_labels)

FIG = Path(__file__).resolve().parent
REPORT = FIG.parent


def load_generator():
    spec = importlib.util.spec_from_file_location('logical_architecture', FIG / 'logical-architecture.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LogicalArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logical = load_generator()
        cls.metrics = SerifMetrics()
        cls.inventory = json.loads((FIG / 'logical-architecture.inventory.json').read_text())
        cls.job = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.job.cleanup)
        cls.svg = Path(cls.job.name) / 'logical-architecture.svg'
        cls.logical.create_figure(cls.inventory, cls.metrics).save(cls.svg)
        cls.root = ET.parse(cls.svg).getroot()

    def check_root(self, root):
        changed = Path(self.job.name) / 'changed.svg'
        ET.ElementTree(root).write(changed)
        return self.logical.display_check(self.inventory, changed, self.metrics)

    def test_four_components_match_report_allocations(self):
        expected = {
            'L01': ('MBSE Workspace', [1, 2, 3, 4, 5, 6, 7, 8, 11, 13]),
            'L02': ('COTS Database', [10]),
            'L03': ('Simulation and Analysis', [12, *range(14, 21)]),
            'L04': ('Configuration Management', [9]),
        }
        self.assertEqual({c['id']: (c['name'], [int(fr[-2:]) for fr in c['requirements']])
                          for c in self.inventory['components']}, expected)
        self.logical.inventory_check(self.inventory)
        self.assertEqual(len(self.inventory['requirements']), 20)

    def test_all_components_are_inside_and_only_users_are_outside(self):
        frame = self.root.find('./{*}g[@data-system="Framework"]')
        self.assertEqual({g.attrib['data-component'] for g in frame.findall('./{*}g[@data-component]')},
                         {'L01', 'L02', 'L03', 'L04'})
        self.assertFalse(frame.findall('.//{*}g[@data-actor]'))
        self.assertEqual([g.attrib['data-actor'] for g in self.root.findall('./{*}g[@data-actor]')],
                         ['users'])
        self.assertNotIn('Simulation tools', ' '.join(self.root.itertext()))

    def test_cots_identifiers_and_values_reach_different_consumers(self):
        exchanges = {e['name']: e for e in self.inventory['peer_exchanges']}
        self.assertEqual((exchanges['cotsParameterLinkRequests']['source'],
                          exchanges['cotsParameterLinkRequests']['target']), ('L01', 'L02'))
        self.assertEqual((exchanges['cotsParameterIdentifiers']['source'],
                          exchanges['cotsParameterIdentifiers']['target']), ('L02', 'L01'))
        self.assertEqual((exchanges['linkedCotsParameterRequests']['source'],
                          exchanges['linkedCotsParameterRequests']['target']), ('L03', 'L02'))
        self.assertEqual((exchanges['cotsParameterValues']['source'],
                          exchanges['cotsParameterValues']['target']), ('L02', 'L03'))

    def test_workspace_sends_models_and_receives_result_identifiers(self):
        exchanges = {e['name']: e for e in self.inventory['peer_exchanges']}
        inputs, results = exchanges['computationInputs'], exchanges['numericalResultIdentifiers']
        self.assertEqual((inputs['source'], inputs['target']), ('L01', 'L03'))
        self.assertIn('MBSE models', ' '.join(inputs['labels']))
        self.assertEqual((results['source'], results['target']), ('L03', 'L01'))
        self.assertEqual(' '.join(results['labels']), 'Numerical result identifiers')

    def test_user_interfaces_reach_workspace_and_configuration_management(self):
        self.assertEqual({i['id']: i['component'] for i in self.inventory['interfaces']},
                         {'IF-01': 'L01', 'IF-02': 'L04'})
        self.assertEqual(len(self.root.findall('.//{*}rect[@data-port]')), 2)
        validate_port_labels(self.root)
        for interface in self.inventory['interfaces']:
            self.assertEqual([f['direction'] for f in interface['flows']], ['in', 'out'])

    def test_every_directed_exchange_has_one_terminal_head(self):
        validate_arrowheads(self.root)
        self.assertEqual(len(self.root.find('./{*}g[@data-layer="arrowheads"]')), 12)
        self.assertTrue(all(self.logical.display_check(self.inventory, self.svg, self.metrics).values()))

    def test_internal_simulation_cannot_be_moved_outside(self):
        root = copy.deepcopy(self.root)
        frame = root.find('./{*}g[@data-system="Framework"]')
        simulation = frame.find('./{*}g[@data-component="L03"]')
        frame.remove(simulation)
        root.insert(2, simulation)
        with self.assertRaisesRegex(ValueError, 'logical component'):
            self.check_root(root)

    def test_reversed_route_is_rejected(self):
        root = copy.deepcopy(self.root)
        root.find('.//{*}g[@id="E04"]/{*}path').set('d', 'M410 185 H445 V420 H600')
        foreground_arrowheads(root)
        with self.assertRaisesRegex(ValueError, 'Reversed or disconnected'):
            self.check_root(root)

    def test_missing_exchange_and_wrong_allocation_are_rejected(self):
        inventory = copy.deepcopy(self.inventory)
        inventory['peer_exchanges'].pop()
        with self.assertRaisesRegex(ValueError, 'Changed internal exchange'):
            self.logical.inventory_check(inventory)
        inventory = copy.deepcopy(self.inventory)
        inventory['components'][1]['requirements'] = ['FR-05']
        with self.assertRaisesRegex(ValueError, 'allocations differ'):
            self.logical.inventory_check(inventory)

    def test_labels_cannot_overlap_routes_or_shrink(self):
        for defect in ('overlap', 'small'):
            with self.subTest(defect=defect):
                root = copy.deepcopy(self.root)
                label = root.find('./{*}g[@id="X01.1"]/{*}text')
                label.set('y' if defect == 'overlap' else 'font-size',
                          '110' if defect == 'overlap' else '9')
                with self.assertRaises(ValueError):
                    self.check_root(root)

    def test_missing_or_detached_shared_port_is_rejected(self):
        for defect in ('missing', 'detached'):
            with self.subTest(defect=defect):
                root = copy.deepcopy(self.root)
                frame = root.find('./{*}g[@data-system="Framework"]')
                port = frame.find('./{*}rect[@data-port="p02"]')
                if defect == 'missing':
                    frame.remove(port)
                else:
                    port.set('x', '0')
                with self.assertRaises(ValueError):
                    self.check_root(root)

    def test_pdf_is_one_searchable_page(self):
        pdf = FIG / 'logical-architecture.pdf'
        self.assertRegex(run(['pdfinfo', str(pdf)]), r'(?m)^Pages:\s+1\s*$')
        text = ' '.join(run(['pdftotext', str(pdf), '-']).split())
        for cid, name in self.logical.CANONICAL_NAMES.items():
            self.assertIn(cid+' '+name, text)
        self.assertIn('Users', text)
        self.assertNotIn('Simulation tools', text)
        self.assertNotIn('Logical architecture', text)

    def test_published_metadata_matches_sources_and_pdf(self):
        provenance = json.loads((FIG / 'logical-architecture.provenance.json').read_text())
        self.assertEqual(provenance['dimensions'], dict(pdf_pt=[760, 620], pdf_pages=1))
        self.assertEqual(provenance['generator_sha256'], sha(FIG / 'logical-architecture.py'))
        self.assertEqual(provenance['style_sha256'], sha(FIG / 'diagram_style.py'))
        self.assertEqual(provenance['artifact_sha256'], dict(pdf=sha(FIG / 'logical-architecture.pdf')))
        for name, digest in provenance['report_source_sha256'].items():
            self.assertEqual(digest, sha(REPORT.parent / name))

    def test_latex_uses_one_view_and_four_complete_table_rows(self):
        text = (REPORT / 'logical.tex').read_text()
        self.assertIn('four logical components', text)
        figure = text.split('\\begin{figure}[p]', 1)[1].split('\\end{figure}', 1)[0]
        self.assertEqual(figure.count('\\includegraphics'), 1)
        self.assertIn('\\includegraphics[width=\\linewidth]{fig/logical-architecture.pdf}', figure)
        self.assertNotRegex(text, r'two coordinated views|upper view|lower view|including simulation tools')
        rows = re.findall(r'^L\d\d [^\n]+', text, re.M)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row.endswith('\\\\') for row in rows))


if __name__ == '__main__':
    unittest.main()
