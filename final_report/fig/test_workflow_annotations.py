"""Check requirement annotations and logical component boundaries in the workflows.

Run from the repository root:
  python3 -m unittest discover -s final_report/fig -p 'test_workflow_annotations.py' -v
"""
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
OUT = FIG / "model-appendices"
sys.path.insert(0, str(FIG))
sys.path.insert(0, str(ROOT))

from diagram_style import sha, validate_arrowheads, validate_style


def requirement_ids(text):
    return {f"FR-{number:02d}"
            for start, end in re.findall(r"FR-(\d{2})(?: to FR-(\d{2}))?", text)
            for number in range(int(start), int(end or start) + 1)}


class WorkflowAnnotationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("workflow_figures", FIG / "model-appendix-figures.py")
        cls.generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.generator)
        cls.views = {"mission-workflow": cls.generator.flow(),
                     "addition-lifecycle": cls.generator.initialization()}
        cls.manifest = json.loads((OUT / "provenance.json").read_text())
        cls.requirements = set(re.findall(r"^(FR-\d{2}) &", (FIG.parent / "requirements.tex").read_text(), re.M))
        cls.allocations = {}
        cls.names = {}
        for component, name, numbers in re.findall(
                r"^(L\d{2}) ([^&]+?) & ([^&]+) &", (FIG.parent / "logical.tex").read_text(), re.M):
            cls.names[component] = name
            cls.allocations[component] = {
                f"FR-{number:02d}" for start, end in re.findall(r"(\d{2})(?:--(\d{2}))?", numbers)
                for number in range(int(start), int(end or start) + 1)}

    def test_component_names_and_scope_match_report(self):
        self.assertEqual(self.generator.COMPONENT_NAMES, self.names)
        for name, expected in (("mission-workflow", set(self.names)), ("addition-lifecycle", {"L01"})):
            components = self.views[name].root.findall('.//{*}g[@data-component]')
            self.assertEqual({node.attrib["data-component"] for node in components}, expected)
        engineer = self.views["mission-workflow"].root.find('.//{*}g[@data-actor="Engineer"]')
        self.assertIsNotNone(engineer)
        self.assertNotIn("data-component", engineer.attrib)

    def test_every_step_has_visible_valid_requirements(self):
        for name, figure in self.views.items():
            steps = figure.root.findall('.//{*}g[@data-step]')
            self.assertEqual(len(steps), 11 if name == "mission-workflow" else 8)
            for step in steps:
                with self.subTest(diagram=name, step=step.attrib["data-step"]):
                    identifiers = requirement_ids(step.attrib["data-requirements"])
                    label = step.find('./{*}text[@data-annotation="requirements"]')
                    self.assertTrue(identifiers)
                    self.assertLessEqual(identifiers, self.requirements)
                    self.assertIsNotNone(label)
                    self.assertEqual(requirement_ids(label.text), identifiers)
                    prepared = requirement_ids(step.attrib["data-prepares"])
                    self.assertLessEqual(prepared, self.allocations["L03"])
                    if prepared:
                        label = step.find('./{*}text[@data-annotation="prepares"]')
                        self.assertIsNotNone(label)
                        self.assertTrue(label.text.startswith("Prepares "))
                        self.assertEqual(requirement_ids(label.text), prepared)

    def test_steps_are_enclosed_by_the_responsible_component(self):
        for name, figure in self.views.items():
            enclosed = set()
            for component in figure.root.findall('.//{*}g[@data-component]'):
                boundary = component.find('./{*}rect[@data-component-boundary]')
                bx, by, bw, bh = (float(boundary.attrib[key]) for key in ("x", "y", "width", "height"))
                for step in component.findall('./{*}g[@data-step]'):
                    enclosed.add(step.attrib["data-step"])
                    requirements = requirement_ids(step.attrib["data-requirements"])
                    self.assertTrue(requirements & self.allocations[component.attrib["data-component"]])
                    rect = step.find('./{*}rect')
                    x, y, w, h = (float(rect.attrib[key]) for key in ("x", "y", "width", "height"))
                    self.assertTrue(bx < x < x + w < bx + bw)
                    self.assertTrue(by < y < y + h < by + bh)
            all_steps = {step.attrib["data-step"] for step in figure.root.findall('.//{*}g[@data-step]')}
            external = {"Review assessment coverage and assumptions"} if name == "mission-workflow" else set()
            self.assertEqual(all_steps - enclosed, external)

    def test_labels_fit_action_rectangles_and_review_diamond(self):
        for figure in self.views.values():
            for step in figure.root.findall('.//{*}g[@data-step]'):
                rect = step.find('./{*}rect')
                for label in step.findall('./{*}text'):
                    size = float(label.attrib["font-size"])
                    width = figure.metrics.measure(label.text, size, label.attrib["font-weight"])
                    cx, baseline = float(label.attrib["x"]), float(label.attrib["y"])
                    left, right = cx - width / 2, cx + width / 2
                    top, bottom = baseline - size * .9, baseline + size * .25
                    if rect is not None:
                        x, y, w, h = (float(rect.attrib[key]) for key in ("x", "y", "width", "height"))
                        self.assertTrue(x < left < right < x + w, label.text)
                        self.assertTrue(y < top < bottom < y + h, label.text)
                    else:
                        for x in (left, right):
                            for y in (top, bottom):
                                self.assertLess(abs(x - 574) / 146 + abs(y - 582) / 40, 1, label.text)

    def test_requirements_can_cover_multiple_steps(self):
        for figure in self.views.values():
            steps = figure.root.findall('.//{*}g[@data-step]')
            self.assertGreaterEqual(sum("FR-01" in requirement_ids(step.attrib["data-requirements"])
                                        for step in steps), 3)
            self.assertGreaterEqual(sum("FR-02" in requirement_ids(step.attrib["data-requirements"])
                                        for step in steps), 3)

    def test_sources_artifacts_and_style_are_reproducible(self):
        for path, expected in self.manifest["workflow_sources"].items():
            self.assertEqual(sha(ROOT / path), expected, path)
        with tempfile.TemporaryDirectory() as temporary:
            for name, figure in self.views.items():
                svg = Path(temporary) / (name + ".svg")
                figure.save(svg)
                self.assertEqual(svg.read_bytes(), (OUT / svg.name).read_bytes())
                validate_style(figure.root)
                validate_arrowheads(figure.root)
                for extension, expected in self.manifest["diagrams"][name]["artifact_sha256"].items():
                    self.assertEqual(sha(OUT / (name + "." + extension)), expected)
                for arrow in figure.root.findall('.//{*}path[@data-terminal-head="true"]'):
                    expected = {"COTS request": None, "COTS parameters": "1 3"}.get(
                        arrow.attrib.get("data-exchange"), "4 2.5")
                    self.assertEqual(arrow.attrib.get("stroke-dasharray"), expected)


if __name__ == "__main__":
    unittest.main()
