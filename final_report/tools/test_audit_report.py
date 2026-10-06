"""Regression checks for native diagram provenance in the report audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from audit_report import audit_native_figures, solution_sources


class NativeFigureAuditTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.diagram = 'fig/view.pdf'
        figure = self.root / self.diagram
        figure.parent.mkdir()
        figure.write_bytes(b'%PDF-1.4\n')
        figure.with_suffix('.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        figure.with_suffix('.png').write_bytes(b'\x89PNG\r\n\x1a\n')
        self.svg_hash = hashlib.sha256(figure.with_suffix('.svg').read_bytes()).hexdigest()
        self.manifest = {
            'visualizer': {'name': 'Syside Modeler', 'native': True},
            'target': {'qualified_name': 'Example::view'},
            'artifacts': [
                {'format': 'svg', 'path': '/original/worktree/fig/view.svg',
                 'provenance': {'producer': 'Syside Modeler', 'native': True, 'sha256': self.svg_hash}},
                {'format': 'png', 'path': '/original/worktree/fig/view.png'},
                {'format': 'pdf', 'path': '/original/worktree/fig/view.pdf',
                 'provenance': {'source_svg': {'path': '/original/worktree/fig/view.svg',
                                               'producer': 'Syside Modeler', 'sha256': self.svg_hash}}},
            ],
        }
        self.save_manifest()

    def save_manifest(self):
        (self.root / self.diagram).with_suffix('.manifest.json').write_text(json.dumps(self.manifest))

    def test_valid_native_figure_is_portable_between_worktrees(self):
        result = audit_native_figures(self.root, [self.diagram])
        self.assertEqual(result[0]['view'], 'Example::view')
        self.assertEqual(result[0]['native_svg_sha256'], self.svg_hash)
        self.assertTrue(result[0]['exact_pdf_source_hash_matches'])

    def test_modified_svg_is_rejected(self):
        (self.root / self.diagram).with_suffix('.svg').write_text('<svg/>')
        with self.assertRaisesRegex(AssertionError, 'Native SVG hash mismatch'):
            audit_native_figures(self.root, [self.diagram])

    def test_pdf_must_reference_exact_native_svg(self):
        self.manifest['artifacts'][2]['provenance']['source_svg']['sha256'] = 'stale'
        self.save_manifest()
        with self.assertRaisesRegex(AssertionError, 'PDF source hash mismatch'):
            audit_native_figures(self.root, [self.diagram])

    def test_non_native_producer_is_rejected(self):
        self.manifest['visualizer']['native'] = False
        self.save_manifest()
        with self.assertRaisesRegex(AssertionError, 'Non-native figure'):
            audit_native_figures(self.root, [self.diagram])

    def test_missing_artifact_is_rejected(self):
        (self.root / self.diagram).with_suffix('.png').unlink()
        with self.assertRaisesRegex(AssertionError, 'Missing png artifact'):
            audit_native_figures(self.root, [self.diagram])

    def test_missing_manifest_is_rejected(self):
        (self.root / self.diagram).with_suffix('.manifest.json').unlink()
        with self.assertRaisesRegex(AssertionError, 'Missing native figure manifest'):
            audit_native_figures(self.root, [self.diagram])

    def test_duplicate_figure_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'Duplicate solution figure paths'):
            audit_native_figures(self.root, [self.diagram, self.diagram])


class SolutionSourceTests(unittest.TestCase):
    def test_follows_flattened_inputs_once_and_ignores_comments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'solucion.tex').write_text('\\input{needs}\n% \\input{missing}\n\\input{requirements}\n')
            (root / 'needs.tex').write_text('Mission requirements.')
            (root / 'requirements.tex').write_text('\\input{needs.tex}\nSystem requirements.')
            self.assertEqual([path.name for path in solution_sources(root)],
                             ['solucion.tex', 'needs.tex', 'requirements.tex'])

    def test_missing_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'solucion.tex').write_text('\\input{missing}')
            with self.assertRaisesRegex(AssertionError, 'Missing solution source'):
                solution_sources(root)


if __name__ == '__main__':
    unittest.main()
