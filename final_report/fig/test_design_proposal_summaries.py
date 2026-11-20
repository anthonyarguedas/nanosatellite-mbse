"""Check the workflow summary and both Battery source/property comparisons.

Run from the repository root:
  python3 -m unittest discover -s final_report/fig -p 'test_design_proposal_summaries.py' -v
"""
import ast
import importlib.util
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(FIG))

from diagram_style import orthogonal_points, sha, validate_arrowheads, validate_style
from framework.models import Battery, Component


class DesignProposalSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("proposal_summaries", FIG / "design-proposal-summaries.py")
        cls.generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.generator)
        cls.manifest = json.loads((FIG / "design-proposal/summaries.provenance.json").read_text())

    def test_workflow_keeps_the_appendix_steps_and_routes(self):
        detailed = self.generator.APP.flow().root
        summary = ET.parse(FIG / "design-proposal/mission-workflow-summary.svg").getroot()
        steps = summary.findall('.//{*}g[@data-step]')
        self.assertEqual([step.attrib["data-step"] for step in steps],
                         [step.attrib["data-step"] for step in detailed.findall('.//{*}g[@data-step]')])
        self.assertEqual(len(steps), 11)
        for step in steps:
            labels = step.findall("./{*}text")
            self.assertEqual(len(labels), 1)
            expected = ("Satisfied with the assessment?" if step.find("./{*}rect") is None
                        else step.attrib["data-step"])
            self.assertEqual(labels[0].text, expected)
        old_routes = detailed.findall('.//{*}path[@data-terminal-head]')
        new_routes = summary.findall('.//{*}path[@data-terminal-head]')
        self.assertEqual(len(new_routes), len(old_routes))
        for old, new in zip(old_routes, new_routes):
            self.assertEqual(old.attrib.get("stroke-dasharray"), new.attrib.get("stroke-dasharray"))
            old_points, new_points = orthogonal_points(old.attrib["d"]), orthogonal_points(new.attrib["d"])
            self.assertEqual(len(old_points), len(new_points))
            for (x, y), (sx, sy) in zip(old_points, new_points):
                self.assertEqual(x, sx)
                self.assertAlmostEqual(y * self.generator.WORKFLOW_SCALE, sy)
        self.assertFalse(any("FR-" in (node.text or "") for node in summary.findall('.//{*}text')))

    def shown_properties(self, name):
        root = ET.parse(FIG / (name + "-diagram.svg")).getroot()
        labels = [node.text or "" for node in root.findall('.//{*}text')]
        return {match[1]: (match[2], bool(match[3])) for label in labels
                if (match := re.fullmatch(r"(\w+) \[([^]]+)\]( \*)?", label))}

    def test_five_selected_properties_match_the_complete_view(self):
        selected = self.shown_properties("design-proposal/battery-property-excerpt")
        complete = self.shown_properties("model-appendices/battery-property-definitions")
        self.assertEqual(set(selected), set(self.generator.SELECTED))
        self.assertEqual(len(selected), 5)
        self.assertEqual(selected, {name: complete[name] for name in selected})
        expected = {name: (str(prop.unit), prop.expression is not None)
                    for name, prop in Battery("example").properties.items()}
        self.assertEqual(complete, expected)
        self.assertEqual(len(complete), 32)

    def test_python_panels_retain_the_actual_declarations(self):
        def declarations(source):
            return {cls.name: {node.targets[0].id: ast.dump(node.value)
                               for node in cls.body if isinstance(node, ast.Assign)
                               and isinstance(node.value, ast.Call)
                               and isinstance(node.value.func, ast.Name)
                               and node.value.func.id == "Property"}
                    for cls in ast.parse(source).body if isinstance(cls, ast.ClassDef)}

        expected = declarations(inspect.getsource(Component) + "\n" + inspect.getsource(Battery))
        for name, complete in (("design-proposal/battery-property-excerpt", False),
                               ("model-appendices/battery-property-definitions", True)):
            source = (FIG / (name + ".tex")).read_text()
            code = re.search(r"\\begin\{lstlisting\}[^\n]*\n(.*?)\\end\{lstlisting\}", source, re.S)[1]
            shown = declarations(code)
            self.assertEqual(shown, expected if complete else {
                "Battery": {name: expected["Battery"][name] for name in self.generator.SELECTED}})
            self.generator.APP.check_panel_widths(FIG / (name + ".tex"))
            self.assertLess(source.index("Python property declarations"), source.index("Graphical representation"))
            self.assertIn(r"\input{../code-highlighting}", source)

    def test_diagram_style_and_artifact_provenance(self):
        for path, expected in self.manifest["sources"].items():
            self.assertEqual(sha(ROOT / path), expected, path)
        for name, output in self.manifest["diagrams"].items():
            root = ET.parse(FIG / (name + ".svg")).getroot()
            validate_style(root)
            validate_arrowheads(root)
            for extension, expected in output["artifact_sha256"].items():
                self.assertEqual(sha(FIG / (name + "." + extension)), expected)
        for name, output in self.manifest["panels"].items():
            self.assertEqual(sha(FIG / (name + ".tex")), output["source_sha256"])
            self.assertEqual(sha(FIG / (name + ".pdf")), output["pdf_sha256"])
            self.assertEqual(sha(FIG / "code-highlighting.tex"), output["code_highlighting_sha256"])

    def test_combined_pdf_text_is_searchable_and_within_the_page(self):
        for name in self.manifest["panels"]:
            xml = subprocess.check_output(["pdftotext", "-bbox", str(FIG / (name + ".pdf")), "-"], text=True)
            pages = ET.fromstring(xml).findall('.//{*}page')
            self.assertEqual(len(pages), 1)
            page = pages[0]
            width, height = float(page.attrib["width"]), float(page.attrib["height"])
            words = page.findall('.//{*}word')
            self.assertTrue(words)
            for word in words:
                self.assertTrue(0 <= float(word.attrib["xMin"]) <= float(word.attrib["xMax"]) <= width)
                self.assertTrue(0 <= float(word.attrib["yMin"]) <= float(word.attrib["yMax"]) <= height)
            self.assertIn("Battery", {word.text for word in words})

    def test_report_links_the_summaries_and_has_no_remaining_comments(self):
        design = (FIG.parent / "design-proposal.tex").read_text()
        workflow = (FIG.parent / "framework-workflow-appendix.tex").read_text()
        components = (FIG.parent / "eps-component-models-appendix.tex").read_text()
        for label in ("mission-workflow-summary", "battery-property-excerpt"):
            self.assertIn(r"\label{fig:" + label + "}", design)
            self.assertIn(r"\ref{fig:" + label + "}", design)
        self.assertIn(r"\ref{fig:mission-modeling-workflow}", design)
        self.assertIn(r"\ref{fig:battery-property-definitions}", design)
        self.assertIn(r"\label{fig:battery-property-definitions}", components)
        self.assertIn("Mission modeling and tailoring workflow from branch creation", workflow)
        self.assertNotIn(r"\ref{}", design)
        self.assertNotRegex(design, r"(?<!\\)%")
        for source in (design, components):
            for name in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", source):
                self.assertTrue((FIG.parent / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
