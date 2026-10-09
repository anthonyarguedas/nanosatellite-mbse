"""Native coverage and real drawn logical part, boundary and delegation checks.

Run: python3 -m unittest discover -s final_report/tools -p 'test_logical_figure_coverage.py'
Source checks supplement the unchanged licensed native checker. Mutation tests
reject names, containment, endpoint geometry, authority and contract regressions.
"""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

REPORT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('logical_figure', REPORT / 'fig/logical-architecture.py')
figure = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(figure)


class SourceCoverageTests(unittest.TestCase):
    def setUp(self):
        self.inv = figure.inventory()
        self.ledger = json.loads((REPORT / 'traceability/logical-architecture.json').read_text())
        self.logical = (REPORT / 'sysml/04-logical.sysml').read_text()
        self.context = (REPORT / 'sysml/06-system-context.sysml').read_text()
        self.specs = (REPORT / 'sysml/10-interface-views.sysml').read_text()

    def check(self):
        figure.validate_inventory(self.inv, self.ledger, self.logical, self.context, self.specs)

    def test_complete_authoritative_inventory(self):
        self.check()
        self.assertEqual(self.inv['counts'], dict(peer_exchange_groups=20, peer_field_mappings=203,
            black_box_interfaces=5, black_box_directed_flows=17, boundary_refinement_routes=18))
        self.assertEqual(sum(e['kind'] == 'control' for e in self.inv['peer_exchanges']), 5)
        self.assertEqual({c['id']: c['name'] for c in self.inv['components']}, figure.CANONICAL_NAMES)

    def test_missing_reverse_route_rejected(self):
        self.inv['peer_exchanges'].pop(1)
        with self.assertRaisesRegex(ValueError, 'Missing/extra peer'):
            self.check()

    def test_all_native_field_mappings_individually_required(self):
        for i, e in enumerate(self.inv['peer_exchanges']):
            for j in range(len(e['mappings'])):
                original = self.inv
                self.inv = copy.deepcopy(original)
                self.inv['peer_exchanges'][i]['mappings'].pop(j)
                with self.assertRaisesRegex(ValueError, 'Missing/duplicate field'):
                    self.check()
                self.inv = original

    def test_duplicate_mapping_rejected(self):
        self.inv['peer_exchanges'][0]['mappings'].append(copy.deepcopy(self.inv['peer_exchanges'][0]['mappings'][0]))
        with self.assertRaisesRegex(ValueError, 'Missing/duplicate field'):
            self.check()

    def test_wrong_peer_kind_rejected(self):
        self.inv['peer_exchanges'][-1]['kind'] = 'information'
        with self.assertRaisesRegex(ValueError, 'kind mismatch'):
            self.check()

    def test_wrong_peer_type_rejected(self):
        self.inv['peer_exchanges'][0]['mappings'][0]['target_type'] = 'WrongType'
        with self.assertRaisesRegex(ValueError, 'meaning/type mismatch'):
            self.check()

    def test_native_direction_change_rejected(self):
        self.logical = self.logical.replace('from L01.io.fr01Outputs.field01 to requirementsAllocations_001.source;',
            'from requirementsAllocations_001.source to L01.io.fr01Outputs.field01;')
        with self.assertRaisesRegex(ValueError, 'Producer direction'):
            self.check()

    def test_native_extra_mapping_rejected(self):
        self.logical += '\nperform action missing_999 : Map_missing_999;\n'
        with self.assertRaisesRegex(ValueError, 'Uninventoried native mapping'):
            self.check()

    def test_missing_interface_rejected(self):
        self.inv['interfaces'].pop()
        with self.assertRaisesRegex(ValueError, 'black-box interface'):
            self.check()

    def test_each_external_flow_and_type_required(self):
        for i, interface in enumerate(self.inv['interfaces']):
            for j, flow in enumerate(interface['flows']):
                for key, value in [('direction', 'out' if flow['direction'] == 'in' else 'in'), ('type', 'WrongType')]:
                    original = self.inv
                    self.inv = copy.deepcopy(original)
                    self.inv['interfaces'][i]['flows'][j][key] = value
                    with self.assertRaisesRegex(ValueError, 'feature coverage'):
                        self.check()
                    self.inv = original

    def test_missing_boundary_refinement_rejected(self):
        self.inv['boundary_routes'].pop()
        with self.assertRaisesRegex(ValueError, 'Boundary refinement coverage'):
            self.check()

    def test_actual_native_boundary_binding_required(self):
        self.logical = self.logical.replace('bind p02.sourceSubmission = L01.io.fr02Inputs.field04;',
            'bind p02.sourceSubmission = L04.io.fr02Inputs.field04;')
        with self.assertRaisesRegex(ValueError, 'Native boundary route endpoint'):
            self.check()

    def test_projection_is_not_direct_aggregate_delivery(self):
        self.logical = self.logical.replace('projectComponentProperties.configuration to L02.io.fr13Inputs.field01',
            'p02.sourceSubmission to L02.io.fr13Inputs.field01')
        with self.assertRaisesRegex(ValueError, 'Native boundary projection'):
            self.check()

    def test_combined_pdf_trailer_id_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a.pdf', Path(directory)/'b.pdf'
            a.write_bytes(b'PDF objects and xref\n/ID [(aaaaaaaaaaaaaaaa) (aaaaaaaaaaaaaaaa) ]\nstartxref\n0\n%%EOF')
            b.write_bytes(b'PDF objects and xref\n/ID [(bbbbbbbbbbbbbbbb) (bbbbbbbbbbbbbbbb) ]\nstartxref\n0\n%%EOF')
            figure.normalize_document_id(a)
            figure.normalize_document_id(b)
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_native_root_port_delegation_required(self):
        self.inv['interfaces'][2]['delegation'] = 'L06.p03'
        with self.assertRaisesRegex(ValueError, 'native logical port delegation'):
            self.check()


class RenderedCoverageTests(unittest.TestCase):
    def setUp(self):
        self.inv = figure.inventory()
        published = json.loads((REPORT / 'fig/logical-architecture.inventory.json').read_text())
        self.paths = [REPORT.parent / p['svg'] for p in published['panels']]

    def mutated(self, predicate, mutation):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        paths, matched = [], False
        for index, path in enumerate(self.paths):
            tree = ET.parse(path)
            for node in list(tree.getroot().iter()):
                if predicate(node):
                    mutation(node)
                    matched = True
            destination = Path(directory.name) / f'{index}.svg'
            tree.write(destination)
            paths.append(destination)
        self.assertTrue(matched, 'Mutation selector matched nothing')
        return paths

    def reject(self, predicate, mutation, message):
        with self.assertRaisesRegex(ValueError, message):
            figure.display_check(self.inv, self.mutated(predicate, mutation))

    def test_all_native_entries_have_real_drawn_connections(self):
        checks = figure.display_check(self.inv, self.paths)
        self.assertTrue(all(checks.values()))
        self.assertTrue(all(m['display']['arrow'] == e['display']['arrow'] for e in self.inv['peer_exchanges'] for m in e['mappings']))
        self.assertTrue(all(r['display']['component_name'] == r['display']['component']+' '+figure.CANONICAL_NAMES[r['display']['component']] for r in self.inv['boundary_routes']))

    def test_every_occurrence_requires_the_full_canonical_name(self):
        for path in self.paths:
            for group in ET.parse(path).getroot().findall('.//{*}g[@data-component]'):
                cid, occurrence = group.attrib['data-component'], group.attrib['data-occurrence']
                self.reject(lambda n: n.attrib.get('data-component') == cid and n.attrib.get('data-occurrence') == occurrence,
                    lambda n: setattr(n.find('./{*}text'), 'text', cid), 'Incomplete canonical component name')

    def test_no_abbreviated_name_or_collapsed_owner_summary(self):
        self.reject(lambda n: n.attrib.get('data-component') == 'L05' and n.attrib.get('data-occurrence') == 'boundary',
            lambda n: setattr(n.find('./{*}text'), 'text', 'Framework boundary L01,L02,L05,L06'), 'canonical component name')

    def test_framework_enclosure_required_on_each_view(self):
        self.reject(lambda n: n.attrib.get('data-system') == 'Framework',
            lambda n: n.attrib.pop('data-system'), 'Framework containment')

    def test_component_numeric_containment_required(self):
        self.reject(lambda n: n.attrib.get('data-component') == 'L01' and n.attrib.get('data-occurrence') == 'boundary',
            lambda n: n.find('./{*}rect').set('x', '0'), 'outside Framework containment')

    def test_external_actor_must_remain_outside(self):
        self.reject(lambda n: n.attrib.get('data-actor') == 'engineers',
            lambda n: n.find('./{*}rect').set('x', '200'), 'overlaps Framework')

    def test_erased_bundle_meaning_rejected(self):
        self.reject(lambda n: n.tag.endswith('text') and n.text == 'Requirements &',
            lambda n: setattr(n, 'text', 'Generic records'), 'meaningful peer label')

    def test_erased_external_meaning_rejected(self):
        self.reject(lambda n: n.attrib.get('id') == 'X03.2',
            lambda n: setattr(n.find('./{*}text'), 'text', 'Analysis data'), 'meaningful external label')

    def test_missing_native_bundle_arrow_rejected(self):
        self.reject(lambda n: n.attrib.get('id') == 'E04', lambda n: n.clear(), 'displayed peer bundle')

    def test_reversed_actual_peer_arrow_rejected(self):
        self.reject(lambda n: n.attrib.get('id') == 'arrow-E01',
            lambda n: n.set('d', 'M278 83 H148'), 'Reversed/disconnected rendered peer')

    def test_reversed_actual_configuration_arrow_rejected(self):
        self.reject(lambda n: n.attrib.get('id') == 'arrow-E16',
            lambda n: n.set('d', 'M140 304 V376'), 'Reversed/disconnected rendered peer')

    def test_each_control_bundle_retains_dashed_style(self):
        for e in self.inv['peer_exchanges']:
            if e['kind'] == 'control':
                self.reject(lambda n: n.attrib.get('id') == 'arrow-'+e['id'],
                    lambda n: n.attrib.pop('stroke-dasharray'), 'solid-information/dashed-control')

    def test_all_external_directions_and_information_styles(self):
        for interface in self.inv['interfaces']:
            for flow in interface['flows']:
                self.reject(lambda n: n.attrib.get('id') == 'arrow-'+flow['id'],
                    lambda n: n.set('d', figure.external_geometry(flow['id'], 'out' if flow['direction'] == 'in' else 'in')),
                    'Reversed/disconnected rendered interface')
                self.reject(lambda n: n.attrib.get('id') == 'arrow-'+flow['id'],
                    lambda n: n.set('stroke-dasharray', '4 2.5'), 'solid-information/dashed-control')

    def test_detached_tool_flow_cannot_end_at_pseudo_boundary(self):
        self.reject(lambda n: n.attrib.get('id') == 'arrow-X03.5',
            lambda n: n.set('d', 'M120 289 H280'), 'rendered interface arrow')

    def test_real_boundary_port_required(self):
        self.reject(lambda n: n.attrib.get('data-port') == 'p03' and n.attrib.get('data-owner') == 'Framework' and n.attrib.get('data-feature') == 'spacecraftInputs',
            lambda n: n.set('x', '200'), 'real boundary port')

    def test_part_port_cannot_be_an_inventory_assertion(self):
        self.reject(lambda n: n.attrib.get('data-port') == 'p04' and n.attrib.get('data-owner') == 'L03' and n.attrib.get('data-feature') == 'codingRequest',
            lambda n: n.set('x', '300'), 'real delegated part port')

    def test_every_refinement_needs_a_real_connected_arrow(self):
        for names, d, labels, x, y in figure.REFINEMENT_VIEWS:
            route = next(r for r in self.inv['boundary_routes'] if r['name'] == names[0])
            self.reject(lambda n: n.attrib.get('id') == 'arrow-ref-'+route['id'],
                lambda n: n.set('d', n.attrib['d'].rsplit('H', 1)[0]+'H250'), 'actual LC refinement arrow|actual boundary port')

    def test_native_component_ownership_cannot_change(self):
        self.reject(lambda n: n.attrib.get('id') == 'ref-B17',
            lambda n: n.set('data-component-endpoint', 'L06'), 'concrete boundary ownership')

    def test_refinement_detached_from_port_rejected(self):
        self.reject(lambda n: n.attrib.get('id') == 'arrow-ref-B08',
            lambda n: n.set('d', 'M130 150 H143 V160 H273'), 'detached from its actual boundary port')

    def test_whole_aggregate_replication_rejected(self):
        self.reject(lambda n: n.attrib.get('id') == 'ref-B02',
            lambda n: n.set('data-routes', 'B02,B03,B07,B08'), 'whole aggregate')

    def test_erased_branch_meaning_rejected(self):
        self.reject(lambda n: n.attrib.get('id') == 'ref-B17',
            lambda n: setattr(n.find('./{*}text'), 'text', 'All source data'), 'refinement meaning')

    def test_authority_boundary_cannot_disappear(self):
        for note in (figure.AUTHORITY_NOTES[0], figure.AUTHORITY_NOTES[1], figure.AUTHORITY_NOTES[3]):
            self.reject(lambda n: n.tag.endswith('text') and n.text == note,
                lambda n: setattr(n, 'text', 'Automatic engineering approval'), 'engineering authority boundary')

    def test_external_participant_cannot_disappear(self):
        self.reject(lambda n: n.tag.endswith('text') and n.text == 'NVIDIA Omniverse',
            lambda n: setattr(n, 'text', 'Generic tools'), 'external participant/responsibility')

    def test_audience_facing_style(self):
        for path in self.paths:
            visible = ' '.join(n.text or '' for n in ET.parse(path).getroot().findall('.//{*}text'))
            self.assertNotIn('\u2014', visible)
            self.assertNotIn(';', visible)
            self.assertNotRegex(visible, r'FR-\d\d|\b\d\d\.[io]\d\d|\bfield\d+\b')
        logical = (REPORT / 'logical.tex').read_text()
        self.assertIn('Solid arrows carry information. Dashed arrows carry control.', logical)
        self.assertNotIn(';', logical)

    def test_generated_and_report_panel_counts_match(self):
        inventory = json.loads((REPORT / 'fig/logical-architecture.inventory.json').read_text())
        logical = (REPORT / 'logical.tex').read_text()
        self.assertEqual(len(inventory['panels']), 3)
        self.assertIn('{1,...,3}', logical)
        for suffix in ('svg', 'pdf', 'png'):
            self.assertEqual({p.name for p in (REPORT/'fig').glob(f'logical-architecture-panel-*.{suffix}')},
                {f'logical-architecture-panel-{i:02}.{suffix}' for i in (2, 3)})
        self.assertEqual(sum('fig:framework-logical' in line and '\\label' in line for line in logical.splitlines()), 1)

    def test_publication_provenance_and_models_match(self):
        record = json.loads((REPORT / 'fig/logical-architecture.provenance.json').read_text())
        self.assertFalse(record['native_syside_render'])
        for kind, digest in record['artifact_sha256'].items():
            self.assertEqual(figure.sha(REPORT / f'fig/logical-architecture.{kind}'), digest)
        for name, digest in record['coordinated_panel_sha256'].items():
            self.assertEqual(figure.sha(REPORT / 'fig' / name), digest)
        for path, digest in record['source_model_sha256'].items():
            self.assertEqual(figure.sha(REPORT.parent / path), digest)
        self.assertEqual(record['generator_sha256'], figure.sha(REPORT/'fig/logical-architecture.py'))
        ledger_figure = json.loads((REPORT / 'traceability/logical-architecture.json').read_text())['figure']
        self.assertEqual(ledger_figure['source_sha256'], record['artifact_sha256']['svg'])
        self.assertEqual(ledger_figure['pdf_sha256'], record['artifact_sha256']['pdf'])


if __name__ == '__main__':
    unittest.main()
