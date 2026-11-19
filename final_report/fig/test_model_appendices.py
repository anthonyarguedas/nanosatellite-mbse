"""Source fidelity and executable checks for the two model appendices.

Run from the repository root:
  python3 -m unittest discover -s final_report/fig -p 'test_model_appendices.py' -v
GUI captures can be rebuilt with model-appendix-figures.py and Playwright.
"""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
OUT = FIG / "model-appendices"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(FIG))

from diagram_style import sha, validate_arrowheads, validate_style
from framework.models import Battery, Component, PowerCircuit, Protection, RegulatorAndConverter, SolarArray
from framework.models.eps import SolarPowerPath


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModelAppendixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = load("model_appendix_figures", FIG / "model-appendix-figures.py")
        cls.manifest = json.loads((OUT / "provenance.json").read_text())

    def study(self):
        return load("appendix_mission_test", OUT / "mission-example.py")

    def card_properties(self, name, card):
        root = ET.parse(OUT / (name + ".svg")).getroot()
        group = root.find(f'.//{{*}}g[@data-card="{card}"]')
        self.assertIsNotNone(group)
        labels = " ".join(text.text or "" for text in group.findall("./{*}text"))
        return set(re.findall(r"(\w+) \[", labels))

    def test_six_csrm_categories_and_implementation_boundary(self):
        root = ET.parse(OUT / "eps-property-structure.svg").getroot()
        titles = {node.attrib["data-card"] for node in root.findall('.//{*}g[@data-card]')}
        self.assertEqual(titles, {"Batteries", "Regulators and Converters", "Solar Arrays",
                                  "Power Circuits and Switches", "Processor and Memory", "Software"})
        labels = [node.text for node in root.findall('.//{*}text')]
        self.assertEqual(labels.count("No dedicated Python class"), 2)

    def test_complete_property_lists_with_inheritance(self):
        common = self.card_properties("eps-component-properties", "Component (inherited by all numerical EPS classes)")
        self.assertEqual(common, set(Component("component").properties))
        path = self.card_properties("eps-component-properties", "SolarPowerPath (shared base)")
        self.assertEqual(common | path, set(SolarPowerPath("path").properties))
        for cls in (Battery, RegulatorAndConverter, PowerCircuit, Protection):
            title = cls.__name__ if cls is not Protection else "Protection (extends PowerCircuit)"
            shown = self.card_properties("eps-component-properties", title) | common
            if cls is not Battery:
                shown |= path
            if cls is Protection:
                shown |= self.card_properties("eps-component-properties", "PowerCircuit")
            self.assertEqual(shown, set(cls("component").properties), cls.__name__)
        solar = (self.card_properties("solar-array-properties", "Component (inherited)")
                 | self.card_properties("solar-array-properties", "SolarArray (1 of 2)")
                 | self.card_properties("solar-array-properties", "SolarArray (2 of 2)"))
        self.assertEqual(solar, set(SolarArray("array").properties))

    def test_unit_annotations_and_default_markers_match_source(self):
        for cls in (Component, Battery, SolarArray, RegulatorAndConverter, PowerCircuit, Protection):
            self.assertEqual(self.manifest["properties"][cls.__name__], self.generator.declarations(cls))
        root = ET.parse(OUT / "solar-array-properties.svg").getroot()
        labels = {node.text for node in root.findall('.//{*}text')}
        self.assertIn("cell_iv_curve [no unit] *", labels)
        self.assertIn("power_path [no unit]", labels)
        self.assertIn("source_energy [J] *", labels)

    def test_executable_defaults_and_automatic_requirement_ownership(self):
        s = self.study()
        self.assertEqual(tuple(type(item) for item in s.eps.components[:4]),
                         (Battery, SolarArray, RegulatorAndConverter, PowerCircuit))
        self.assertEqual(len(s.bus.subsystems), 9)
        self.assertEqual(len(s.bus.requirements), 2)
        self.assertEqual(len(s.eps.requirements), 18)
        self.assertIs(s.protector.no_trip.parent, s.protector)
        self.assertIs(s.protector.no_trip.context, s.protector)
        before = tuple(s.protector.requirements)
        s.protector.initialize()
        self.assertEqual(s.protector.requirements, before)
        s.protector.remove("no_trip")
        s.protector.initialize()
        self.assertFalse(s.protector.requirements)

    def test_modes_states_and_explicit_allocations(self):
        s = self.study()
        self.assertEqual([state.name for state in s.active.states], ["on", "off"])
        self.assertEqual(s.active.on.power.value, 0.33)
        self.assertEqual(s.active.off.power.value, 0)
        self.assertEqual(s.active.nominal_share.fraction.value, 1)
        self.assertIs(s.active.nominal_share.spacecraft_mode, s.nominal)
        self.assertIs(s.active.on_share.state, s.active.on)
        self.assertEqual(s.converter.power.evaluate(mode=s.nominal), 0.33)

    def test_interface_is_a_live_reference(self):
        s = self.study()
        original = s.converter.input_voltage.expression
        self.assertEqual(original, "mission.BUS.EPS.Battery.nominal_voltage")
        self.assertEqual(s.converter.input_voltage.value, 3.7)
        s.battery.cell_nominal_voltage = 3.8
        self.assertEqual(s.converter.input_voltage.expression, original)
        self.assertEqual(s.converter.input_voltage.value, 3.8)

    def test_linked_analysis_reexecutes_on_dependency_changes(self):
        s = self.study()
        self.assertEqual(s.energy_j, 33)
        s.active.on.current = 0.2
        self.assertEqual(s.voltage.energy.value, 66)
        self.assertIsNone(s.report.verified)
        self.assertTrue(s.voltage.verify(mode=s.nominal).verified)
        self.assertTrue(s.protector.no_trip.verify().verified)

    def test_authored_requirement_update_verification_and_removal(self):
        s = self.study()
        self.assertIn("3.3 V", s.voltage.render_statement(mode=s.nominal))
        self.assertEqual(s.voltage.rationale, "Nominal mode uses the 3.3 V load rail.")
        s.converter.output_voltage = 3.0
        self.assertFalse(s.voltage.verify(mode=s.nominal).verified)
        s.converter.output_voltage = s.active.on.voltage
        self.assertTrue(s.voltage.verify(mode=s.nominal).verified)
        count = len(s.mission.verify().results)
        s.converter.remove(s.voltage)
        self.assertIsNone(s.voltage.parent)
        self.assertEqual(len(s.mission.verify().results), count - 1)
        s.converter.add(s.voltage)
        self.assertEqual(len(s.mission.verify().results), count)
        s.exercise_requirement_changes()

    def test_diagram_style_and_control_flow(self):
        for name in self.manifest["diagrams"]:
            root = ET.parse(OUT / (name + ".svg")).getroot()
            validate_style(root)
            validate_arrowheads(root)
            if name in ("mission-workflow", "addition-lifecycle"):
                arrows = root.findall('.//{*}path[@data-terminal-head="true"]')
                self.assertTrue(arrows)
                self.assertTrue(all(arrow.attrib["stroke-dasharray"] == "4 2.5" for arrow in arrows))
        labels = " ".join(node.text or "" for node in ET.parse(OUT / "mission-workflow.svg").getroot().findall('.//{*}text'))
        for text in ("git switch", "Mission.add_import()", "Property.value", "mission.verify", "git diff", "git add", "git commit", "No", "Yes"):
            self.assertIn(text, labels)

    def test_code_stays_inside_each_panel(self):
        for name in self.manifest["panels"]:
            self.generator.check_panel_widths(OUT / (name + ".tex"))

    def test_provenance_and_capture_integrity(self):
        for path, expected in self.manifest["sources"].items():
            self.assertEqual(sha(ROOT / path), expected, path)
        for name, output in self.manifest["diagrams"].items():
            for extension, expected in output["artifact_sha256"].items():
                self.assertEqual(sha(OUT / (name + "." + extension)), expected)
        for name, output in self.manifest["screenshots"].items():
            self.assertEqual(sha(OUT / (name + ".png")), output["sha256"])
        for name, output in self.manifest["panels"].items():
            self.assertEqual(sha(OUT / (name + ".pdf")), output["pdf_sha256"])
            self.assertEqual(sha(OUT / (name + ".tex")), output["source_sha256"])
            self.assertEqual(sha(FIG / "code-highlighting.tex"), output["code_highlighting_sha256"])

    def test_all_code_panels_use_shared_syntax_highlighting(self):
        for directory in (FIG / "design-proposal", OUT):
            for path in directory.glob("*.tex"):
                source = path.read_text()
                self.assertNotIn(r"\begin{Verbatim}", source, path.name)
                if r"\begin{lstlisting}" not in source:
                    continue
                self.assertIn(r"\input{../code-highlighting}", source)
                listings = re.findall(r"\\begin\{lstlisting\}\[([^\n]+)\]", source)
                self.assertTrue(listings)
                self.assertTrue(all("style=report-" in options for options in listings))
                xml = subprocess.check_output([
                    "pdftohtml", "-xml", "-hidden", "-stdout", str(path.with_suffix(".pdf")),
                ], text=True, stderr=subprocess.DEVNULL)
                colors = {node.attrib["color"].lower()
                          for node in ET.fromstring(xml).findall(".//fontspec")}
                # PDF color conversion can round a channel down by one.
                target = (0x24, 0x3B, 0x53)
                self.assertTrue(any(
                    all(abs(int(color[index:index + 2], 16) - channel) <= 1
                        for index, channel in zip((1, 3, 5), target))
                    for color in colors
                ), path.name)
        shell = (OUT / "scripts-and-commit.tex").read_text()
        self.assertIn("style=report-bash", shell)
        diff = (FIG / "design-proposal/configuration-diff.tex").read_text()
        self.assertIn("style=report-diff", diff)
        framework = (FIG / "framework-code/script-figures.tex").read_text()
        self.assertIn("style=report-python", framework)
        self.assertNotIn("keywordstyle={}", framework)

    def test_appendices_follow_first_mention_with_full_code_last(self):
        main = (FIG.parent / "main.tex").read_text()
        appendix_section = main.split(r"\appendix", 1)[1].split(r"\backmatter", 1)[0]
        actual = re.findall(r"\\input\{([^}]+)\}", appendix_section)
        labels = {}
        for name in actual:
            source = (FIG.parent / (name + ".tex")).read_text()
            label = re.search(r"\\label\{(appendix:[^}]+)\}", source)[1]
            labels[label] = name

        def expand(source):
            return re.sub(r"\\(?:input|include)\{([^}]+)\}",
                          lambda match: expand((FIG.parent / (match[1] + ".tex")).read_text()),
                          re.sub(r"(?<!\\)%[^\n]*", "", source))

        body = expand(main.split(r"\mainmatter", 1)[1].split(r"\appendix", 1)[0])
        expected = []
        for label in re.findall(r"\\ref\{(appendix:[^}]+)\}", body):
            if label != "appendix:framework-code" and labels[label] not in expected:
                expected.append(labels[label])
        expected.append(labels["appendix:framework-code"])
        self.assertEqual(actual, expected)

    def test_report_integration_and_automatic_letters(self):
        main = (FIG.parent / "main.tex").read_text()
        self.assertIn(r"\input{eps-component-models-appendix}", main)
        self.assertIn(r"\input{framework-workflow-appendix}", main)
        self.assertLess(main.index(r"\input{eps-component-models-appendix}"), main.index(r"\input{framework-code-appendix}"))
        design = (FIG.parent / "design-proposal.tex").read_text()
        self.assertIn(r"\ref{fig:csrm-mission-structure}--\ref{fig:csrm-eps-components}", design)
        for name in ("eps-component-models", "framework-workflow"):
            self.assertIn(r"\ref{appendix:" + name + "}", design)
            appendix = (FIG.parent / (name + "-appendix.tex")).read_text()
            self.assertIn(r"\label{appendix:" + name + "}", appendix)
            self.assertNotIn(r"\setcounter{chapter}", appendix)
            for figure in re.findall(r"\{(fig/model-appendices/[^}]+\.pdf)\}", appendix):
                self.assertTrue((FIG.parent / figure).is_file())


if __name__ == "__main__":
    unittest.main()
