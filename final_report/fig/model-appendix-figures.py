"""Build source-based component diagrams, workflow panels and live GUI evidence.

Run with a Python environment containing Playwright:
  python model-appendix-figures.py --chromium /path/to/chrome-headless-shell
Only temporary mission copies are opened in the GUI. Framework sources and the
existing report figures are unchanged. Numerical examples are synthetic.
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import textwrap

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
OUT = FIG / "model-appendices"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(FIG))

from diagram_style import Figure, INK, render_figure, require, sha
from framework.models import Battery, Component, EPS, PowerCircuit, Protection, RegulatorAndConverter, SolarArray, ProcessorAndMemory, Software
from framework.models.elements import Subsystem
from framework.models.objects import ModelObject


def load_helpers():
    spec = importlib.util.spec_from_file_location("appendix_evidence", FIG / "design-proposal-figures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    return module


def excerpt(name):
    source = (OUT / "mission-example.py").read_text()
    result = source.split(f"# excerpt: {name}\n", 1)[1].split(f"# end: {name}", 1)[0]
    return textwrap.dedent(result).strip()


def declarations(cls):
    instance = cls("example")
    return {name: {"unit": str(prop.unit), "expression": prop.expression}
            for name, prop in instance.properties.items()}


def prop_lines(cls, exclude=()):
    return [name + (f" [{item['unit']}]" if item["unit"] else " [no unit]")
            + (" *" if item["expression"] is not None else "")
            for name, item in declarations(cls).items() if name not in exclude]


def card(figure, x, y, width, title, lines, *, font=13, leading=17):
    height = 38 + leading * len(lines)
    group = figure.el("g", data_card=title)
    figure.rect(x, y, width, height, group)
    figure.text(title, x + 10, y + 21, size=14, weight="bold", parent=group, width=width - 20)
    figure.el("path", group, d=f"M{x} {y+31} H{x+width}", stroke=INK, stroke_width=".6")
    figure.lines(lines, x + 10, y + 50, size=font, leading=leading, width=width - 20, parent=group)
    return height


def overview():
    figure = Figure("CSRM EPS groups and Python property definitions", 690, 350)
    figure.text("CSRM EPS groups and Python property definitions", 8, 22, size=16, weight="bold")
    figure.rect(8, 42, 674, 298)
    figure.text("Power Subsystem", 20, 65, size=14, weight="bold")
    rows = [
        ("Batteries", ["Battery", "Property detail: next figure"]),
        ("Regulators and Converters", ["RegulatorAndConverter", "Property detail: next figure"]),
        ("Solar Arrays", ["SolarArray", "Separate full property view"]),
        ("Power Circuits and Switches", ["PowerCircuit", "Protection specialization"]),
        ("Processor and Memory", ["ProcessorAndMemory", "Additional property view"]),
        ("Software", ["Software", "Cost only"]),
    ]
    for index, (title, lines) in enumerate(rows):
        card(figure, 20 + (index % 3) * 220, 84 + (index // 3) * 118,
             210, title, lines, font=12, leading=18)
    return figure


def component_properties():
    figure = Figure("Battery, conversion and power circuit properties", 690, 660)
    figure.text("Battery, conversion and power circuit properties", 8, 22, size=16, weight="bold")
    common = declarations(Component)
    card(figure, 8, 40, 674, "Component (inherited by hardware EPS classes)",
         ["    ".join(prop_lines(Component))], font=13)
    card(figure, 8, 124, 330, "Battery", prop_lines(Battery, common), font=13, leading=15)
    path = ("transfer_method", "selected_transfer_method", "bus_voltage", "voltage_drop", "input_voltage_setpoint")
    card(figure, 352, 124, 330, "SolarPowerPath (shared base)",
         [line for line in prop_lines(PowerCircuit, common)
          if line.split(" [", 1)[0] in path], font=13, leading=15)
    card(figure, 352, 260, 330, "RegulatorAndConverter", prop_lines(RegulatorAndConverter, (*common, *path)),
         font=13, leading=15)
    card(figure, 352, 442, 330, "PowerCircuit", prop_lines(PowerCircuit, (*common, *path)), font=13, leading=15)
    card(figure, 352, 528, 330, "Protection (extends PowerCircuit)",
         prop_lines(Protection, declarations(PowerCircuit)), font=13, leading=15)
    return figure


def solar_properties():
    figure = Figure("SolarArray property definitions", 690, 546)
    figure.text("SolarArray property definitions", 8, 22, size=16, weight="bold")
    card(figure, 8, 40, 674, "Component (inherited)", ["    ".join(prop_lines(Component))])
    lines = prop_lines(SolarArray, declarations(Component))
    split = (len(lines) + 1) // 2
    card(figure, 8, 124, 330, "SolarArray (1 of 2)", lines[:split], font=13, leading=16)
    card(figure, 352, 124, 330, "SolarArray (2 of 2)", lines[split:], font=13, leading=16)
    return figure


def processor_software_properties():
    figure = Figure("Processor, memory and software properties", 690, 350)
    figure.text("Processor, memory and software properties", 8, 22, size=16, weight="bold")
    card(figure, 8, 40, 674, "Component (hardware properties)",
         ["    ".join(prop_lines(Component))], font=13)
    card(figure, 8, 124, 410, "ProcessorAndMemory", prop_lines(ProcessorAndMemory, declarations(Component)),
         font=13, leading=19)
    card(figure, 438, 124, 244, "Software", prop_lines(Software), font=13, leading=19)
    require(set(declarations(Software)) == {"cost"}, "Software must omit hardware properties")
    return figure


def action(figure, x, y, width, title, lines, height=80):
    figure.rect(x, y, width, height)
    figure.text(title, x + width / 2, y + 23, size=14, weight="bold", anchor="middle", width=width-20)
    figure.lines(lines, x + width / 2, y + 45, size=13, leading=17, anchor="middle", width=width-20)


def flow():
    figure = Figure("Representative mission modeling and Git workflow", 690, 690)
    figure.text("Representative mission modeling and Git workflow", 8, 22, size=16, weight="bold")
    action(figure, 20, 48, 300, "Open a working branch", ["git switch -c mission-study"], 64)
    action(figure, 20, 144, 300, "Create the mission", ["Mission(): imports and default Orbit", "Supply orbit and lifetime inputs"], 82)
    action(figure, 20, 258, 300, "Add CubeSat and subsystems", ["mission.add(CubeSatBus(...))", "Run automatic additions (next figure)"], 82)
    action(figure, 20, 372, 300, "Tailor the mission", ["Edit properties, COTS, modes and interfaces", "Add or revise requirements and rationale"], 82)
    action(figure, 20, 486, 300, "Link analysis scripts", ["Mission.add_import() and Property expressions", "Bind each named input and output field"], 82)
    for start, end in ((112, 144), (226, 258), (340, 372), (454, 486)):
        figure.arrow(f"M170 {start} V{end}", style="dashed")
    figure.arrow("M170 568 V674 H680 V36 H515 V48", style="dashed")
    action(figure, 365, 48, 300, "Execute analyses and verification", ["Property.value executes linked calculations", "mission.verify(mode=nominal)"], 82)
    action(figure, 365, 162, 300, "Inspect results and rationale", ["Read values, failures, missing inputs and errors", "Check assumptions and assessment coverage"], 82)
    figure.arrow("M515 130 V162", style="dashed")
    figure.el("path", d="M515 278 L635 324 L515 370 L395 324 Z", fill="white", stroke=INK, stroke_width=".8")
    figure.lines(["Satisfied with", "the assessment?"], 515, 319, leading=17,
                 size=14, anchor="middle")
    figure.arrow("M515 244 V278", style="dashed")
    figure.arrow("M395 324 H341 V413 H320", style="dashed")
    figure.text("No", 350, 313, size=13)
    action(figure, 365, 420, 300, "Save and review mission Python", ["Save the configuration as mission.py", "git diff -- mission.py"], 82)
    figure.arrow("M515 370 V420", style="dashed")
    figure.text("Yes", 525, 397, size=13)
    action(figure, 365, 544, 300, "Commit the reviewed decision", ["git add mission.py", 'git commit -m "Rationale for the EPS choice"'], 82)
    figure.arrow("M515 502 V544", style="dashed")
    return figure


def initialization():
    figure = Figure("Automatic method calls when a CubeSat is added", 690, 690)
    figure.text("Automatic method calls when a CubeSat is added", 8, 22, size=16, weight="bold")
    action(figure, 20, 48, 650, "ModelObject.add(child)",
           ["Validate type, ownership, names and containment, then attach child", "Run validate_attachment() on the attached subtree"], 82)
    action(figure, 20, 164, 650, "child.initialize()",
           ["First addition calls create_defaults(), then create_requirements() for uninitialized owners"], 65)
    figure.arrow("M345 130 V164", style="dashed")
    figure.arrow("M345 229 V246 H175 V274", style="dashed")
    action(figure, 20, 274, 310, "SpaceSegment.create_defaults()",
           ["CubeSatBus adds its nine default subsystems", "Each self.add(subsystem) repeats add()", "EPS initialization is expanded on the right"], 100)
    action(figure, 360, 274, 310, "Subsystem.create_defaults() on EPS",
           [", ".join(cls.__name__ for cls in EPS.default_components[:3]),
            ", ".join(cls.__name__ for cls in EPS.default_components[3:]), "Each component runs initialize()"], 100)
    figure.arrow("M330 324 H360", style="dashed")
    action(figure, 360, 416, 310, "EPS.create_requirements()",
           ["_sizing_requirement() and _voltage_requirement()", "add_requirement() creates 18 EPS requirements", "Requirement.add() attaches each condition"], 100)
    figure.arrow("M515 374 V416", style="dashed")
    action(figure, 20, 416, 310, "Complete CubeSat initialization",
           ["Add the other default subsystems", "CubeSatBus.create_requirements()", "add_requirement(): mass_limit, volume_limit"], 100)
    figure.arrow("M360 466 H330", style="dashed")
    action(figure, 20, 558, 310, "Return the attached CubeSat",
           ["mission.add(...) returns bus", "Repeated calls keep edits", "and do not recreate deleted items"], 100)
    figure.arrow("M175 516 V558", style="dashed")
    card(figure, 360, 558, 310, "Other additions use the same lifecycle",
         ["ComponentMode: on and off states", "SpacecraftMode: OrbitAllocation", "Protection: no_trip requirement"], font=13, leading=17)
    return figure


def check_property_coverage(figures):
    labels = [node.text for figure in figures for node in figure.root.findall(".//{*}text")]
    common = declarations(Component)
    for cls in (Battery, SolarArray, RegulatorAndConverter, PowerCircuit, Protection, ProcessorAndMemory, Software):
        for name, data in declarations(cls).items():
            require(any(text.startswith(name + " [") for text in labels)
                    or name in common, f"Missing {cls.__name__}.{name}")
    return {cls.__name__: declarations(cls) for cls in
            (Component, Battery, SolarArray, RegulatorAndConverter, PowerCircuit, Protection, ProcessorAndMemory, Software)}


def screenshots(helpers, job, args):
    from playwright.sync_api import sync_playwright

    session = job / "mission.py"
    shutil.copyfile(OUT / "mission-example.py", session)
    study = helpers.load_study(session)
    assert study.active.on.power.value == 0.33
    assert study.active.off.power.value == 0
    assert study.converter.power.evaluate(mode=study.nominal) == 0.33
    assert study.converter.input_voltage.value == study.battery.nominal_voltage.value == 3.7
    assert study.protector.no_trip.verify().verified is True
    assert len(study.eps.requirements) == 18
    assert study.energy_j == 33
    study.exercise_requirement_changes()
    process, log, url = helpers.start_server(session, job, args.python)
    images = {}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**({"executable_path": args.chromium} if args.chromium else {}))
            page = helpers.open_page(browser, url, "mission.BUS.EPS.RegulatorAndConverter", width=760, height=1050)
            # The native responsive view gives a compact modes/states table.
            assert "Component Mode" in page.locator(".modes").inner_text()
            assert "0.33 W" in page.locator(".modes").inner_text()
            images["modes-states"] = helpers.capture(page, "modes-states", page.locator(".modes"))
            page.close()
            page = helpers.open_page(browser, url, "mission.BUS.EPS.protector", width=760, height=850)
            assert page.locator("#requirement-rows .result").inner_text() == "Pass"
            images["component-requirements"] = helpers.capture(page, "component-requirements", page.locator(".requirements"))
            page.close()
            page = helpers.open_page(browser, url, "mission.BUS.EPS.RegulatorAndConverter", width=1800, height=1000)
            helpers.edit(page, "mission.BUS.EPS.RegulatorAndConverter")
            helpers.scroll_to(page, '[aria-label="expression for input_voltage"]')
            prop = page.locator('[aria-label="expression for input_voltage"]')
            assert prop.input_value() == "mission.BUS.EPS.Battery.nominal_voltage"
            row = prop.locator("xpath=ancestor::tr")
            assert row.locator(".parameter-result").inner_text() == "3.7"
            images["interface-before"] = helpers.capture(page, "interface-before", row)
            page.get_by_role("button", name="Close editor", exact=True).click()
            # Change the source through the GUI and read the dependent component.
            page.goto(url + "/#mission.BUS.EPS.Battery")
            page.locator('#workspace:not([inert])').wait_for()
            helpers.edit(page, "mission.BUS.EPS.Battery")
            field = page.locator('[aria-label="expression for cell_nominal_voltage"]')
            field.fill("3.8")
            page.get_by_role("button", name="Save", exact=True).click()
            page.locator("#object-editor").wait_for(state="hidden")
            page.goto(url + "/#mission.BUS.EPS.RegulatorAndConverter")
            page.locator('#workspace:not([inert])').wait_for()
            helpers.edit(page, "mission.BUS.EPS.RegulatorAndConverter")
            helpers.scroll_to(page, '[aria-label="expression for input_voltage"]')
            prop = page.locator('[aria-label="expression for input_voltage"]')
            assert prop.input_value() == "mission.BUS.EPS.Battery.nominal_voltage"
            row = prop.locator("xpath=ancestor::tr")
            assert row.locator(".parameter-result").inner_text() == "3.8"
            images["interface-after"] = helpers.capture(page, "interface-after", row)
            browser.close()
    finally:
        process.terminate()
        process.wait(timeout=10)
        log.close()
    return images


def code_panels(h, job):
    outputs = {}
    body = h.panel("Python: modes, states and allocation", h.verb(excerpt("modes"), 8), 246)
    body += r"\hfill" + h.panel("GUI: the same mode and states", h.image("modes-states.png", 252), 252)
    outputs["modes-and-states"] = h.make_pdf("modes-and-states", body, job)

    method = textwrap.dedent(inspect.getsource(Protection.create_requirements))
    call = method[method.index("    self.add_requirement(\n"):].rstrip()
    # An exact source excerpt. The computation of checks is omitted explicitly.
    method_excerpt = "class Protection(PowerCircuit):\n    def create_requirements(self):\n        # Threshold checks defined above (omitted).\n" + textwrap.indent(textwrap.dedent(call), "        ")
    # The exact rationale literal is long. Keep the allocation call, bindings and
    # conditions, with an explicit omission instead of altering the source text.
    begin = method_excerpt.index('            rationale=')
    end = method_excerpt.index('            voltages=', begin)
    method_excerpt = method_excerpt[:begin] + '            # Rationale omitted.\n' + method_excerpt[end:]
    # Typeset a compact excerpt by wrapping at existing argument boundaries.
    method_excerpt = method_excerpt.replace('            voltages=Property(unit="V"), currents=Property(unit="A"), conditions=tuple(conditions),',
        '            voltages=Property(unit="V"),\n            currents=Property(unit="A"),\n            conditions=tuple(conditions),')
    body = h.panel("Python: addition creates an owned requirement", h.verb(excerpt("automatic"), 8), 246)
    body += r"\hfill" + h.panel("GUI: requirement owned by protector", h.image("component-requirements.png", 252), 252)
    body += r"\par\medskip" + h.panel("Source excerpt: automatic assignment hook", h.verb(method_excerpt, 8), 506)
    outputs["requirement-assignment"] = h.make_pdf("requirement-assignment", body, job)

    body = h.panel("Python: explicit component interfaces", h.verb(excerpt("interfaces"), 8), 506)
    body += r"\par\medskip" + h.panel("GUI: converter input before the battery edit", h.image("interface-before.png", 506), 506)
    body += r"\par\medskip" + h.panel("GUI: converter input after the battery edit", h.image("interface-after.png", 506), 506)
    outputs["property-interfaces"] = h.make_pdf("property-interfaces", body, job)

    body = h.panel("Create the mission and its default architecture", h.verb(excerpt("construction"), 8.5), 506)
    body += r"\par\medskip" + h.panel("Add, edit and verify a component requirement", h.verb(excerpt("requirements"), 8.5), 506)
    body += r"\par\medskip" + h.panel("Delete and reattach the same requirement", h.verb(excerpt("removal"), 8.5), 506)
    outputs["mission-and-requirements"] = h.make_pdf("mission-and-requirements", body, job)

    body = h.panel("Shared lifecycle: ModelObject.initialize()", h.verb(textwrap.dedent(inspect.getsource(ModelObject.initialize)).strip(), 8.5), 506)
    body += r"\par\medskip" + h.panel("Automatic component addition: Subsystem.create_defaults()", h.verb(textwrap.dedent(inspect.getsource(Subsystem.create_defaults)).strip(), 8.5), 506)
    defaults = "EPS.default_components = (\n" + "".join(f"    {cls.__name__},\n" for cls in EPS.default_components) + ")"
    body += r"\par\medskip" + h.panel("The EPS declares these component defaults", h.verb(defaults, 8.5), 506)
    outputs["initialization-code"] = h.make_pdf("initialization-code", body, job)

    body = h.panel("Link a script, bind inputs and execute the calculation", h.verb(excerpt("scripts"), 8.5), 506)
    body += r"\par\medskip" + h.panel("Selected outputs from the synthetic mission", h.verb("energy_j == 33.0\nvoltage.verify(mode=nominal).verified is True\nprotector.no_trip.verify().verified is True\nreport.verified is None", 8.5), 506)
    body += r"\par\medskip" + h.panel("After reviewing and saving the mission as mission.py", h.verb('git diff -- mission.py\ngit add mission.py\ngit commit -m "Use the 3.3 V rail for nominal operation"', 8.5, language="bash"), 506)
    outputs["scripts-and-commit"] = h.make_pdf("scripts-and-commit", body, job)
    for name in outputs:
        check_panel_widths(OUT / f"{name}.tex")
    return outputs


def check_panel_widths(path):
    """Check monospaced listing widths independently of TeX box warnings."""
    width, size = 0, None
    for line in path.read_text().splitlines():
        match = re.search(r"begin\{minipage\}\[t\]\{([\d.]+)pt\}", line)
        if match:
            width = float(match[1])
        match = re.search(r"begin\{lstlisting\}.*fontsize\{([\d.]+)\}", line)
        if match:
            size = float(match[1])
            continue
        if r"\end{lstlisting}" in line:
            size = None
        if size is not None:
            require(len(line) * size * 0.6 <= width,
                    f"Code exceeds its panel in {path.name}: {line}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromium")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--components-only", action="store_true", help="Refresh component property figures without changing workflow or GUI panels")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    h = load_helpers()
    views = [overview(), component_properties(), solar_properties(), processor_software_properties()]
    inventory = check_property_coverage(views)
    names = ["eps-property-structure", "eps-component-properties", "solar-array-properties", "processor-software-properties"]
    if args.components_only:
        path = OUT / "provenance.json"
        manifest = json.loads(path.read_text()) if path.exists() else {}
        manifest["properties"] = inventory
        manifest["component_sources"] = {str(path.relative_to(ROOT)): sha(path) for path in (
            Path(__file__), FIG / "diagram_style.py", ROOT / "framework/models/eps.py",
            ROOT / "framework/models/elements.py", ROOT / "framework/models/objects.py")}
        with tempfile.TemporaryDirectory(prefix="eps-component-properties-") as temporary:
            rendered = {name: render_figure(view, OUT / name, Path(temporary)) for name, view in zip(names, views)}
        manifest.setdefault("diagrams", {}).update(rendered)
        path.write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps({"component_figures": names, "property_lists": list(inventory)}, indent=2))
        return
    views += [flow(), initialization()]
    names += ["mission-workflow", "addition-lifecycle"]
    manifest = {"basis": "Six CSRM categories with actual Python property declarations; synthetic live GUI evidence",
                "properties": inventory, "sources": {str(path.relative_to(ROOT)): sha(path) for path in (
                    Path(__file__), OUT / "mission-example.py", FIG / "diagram_style.py", FIG / "design-proposal-figures.py",
                    FIG / "code-highlighting.tex",
                    ROOT / "framework/models/eps.py", ROOT / "framework/models/elements.py",
                    ROOT / "framework/models/objects.py", ROOT / "framework/models/modes.py",
                    ROOT / "framework/models/mission.py", ROOT / "framework/gui/public/app.js",
                    ROOT / "framework/gui/public/editor.js", ROOT / "framework/gui/public/style.css")}}
    with tempfile.TemporaryDirectory(prefix="model-appendices-") as temporary:
        job = Path(temporary)
        manifest["diagrams"] = {name: render_figure(view, OUT / name, job) for name, view in zip(names, views)}
        manifest["screenshots"] = screenshots(h, job, args)
        manifest["panels"] = code_panels(h, job)
    manifest["checks"] = {"eps_owned_requirements": 18, "protection_owned_requirements": 1,
                          "state_power_w": 0.33, "script_energy_j": 33,
                          "live_interface_before_v": 3.7, "live_interface_after_v": 3.8,
                          "mission_compliance_claim": False}
    (OUT / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest["checks"], indent=2))


if __name__ == "__main__":
    main()
