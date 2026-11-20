"""Build the title-only workflow and paired Battery source/property figures.

Run with the same Python environment as model-appendix-figures.py:
  python3 design-proposal-summaries.py
The workflow reuses the appendix diagram's activities and routes. Battery
excerpts retain the source declarations and their exact expression values.
"""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import textwrap

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
DESIGN = FIG / "design-proposal"
APPENDIX = FIG / "model-appendices"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(FIG))

from diagram_style import render_figure, require, sha, Figure
from framework.models import Battery, Component

SPEC = importlib.util.spec_from_file_location("appendix_figures", FIG / "model-appendix-figures.py")
APP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(APP)

SELECTED = ("series_count", "parallel_count", "cell_count", "cell_rated_energy", "rated_energy")
WORKFLOW_SCALE = 0.65


def workflow_summary():
    figure = APP.flow()
    figure.height = 550
    figure.root.set("height", "550pt")
    figure.root.set("viewBox", "0 0 760 550")
    title = "Mission modeling and tailoring workflow"
    figure.root.set("aria-label", title)
    figure.root.find("./{*}title").text = title
    figure.root.find("./{*}text").text = title

    # Preserve activities and routing, with shorter boxes and one title per step.
    for step in figure.root.findall('.//{*}g[@data-step]'):
        labels = step.findall("./{*}text")
        for label in labels[1:]:
            step.remove(label)
        rect = step.find("./{*}rect")
        if rect is not None:
            center = float(rect.attrib["y"]) + float(rect.attrib["height"]) / 2
        else:
            center = 582
            labels[0].text = "Satisfied with the assessment?"
        labels[0].set("y", str(center + 4.9 / WORKFLOW_SCALE))

    for rect in figure.root.findall(".//{*}rect"):
        for attribute in ("y", "height"):
            rect.set(attribute, f"{float(rect.attrib[attribute]) * WORKFLOW_SCALE:g}")
    for label in figure.root.findall(".//{*}text"):
        label.set("y", f"{float(label.attrib['y']) * WORKFLOW_SCALE:g}")
        if "transform" in label.attrib:
            label.set("transform", f"rotate(-90 {label.attrib['x']} {label.attrib['y']})")
    paths = figure.root.findall('.//{*}path[@data-terminal-head]')
    paths += [figure.root.find('.//{*}g[@data-actor="Engineer"]/{*}g/{*}path')]
    for path in paths:
        value = re.sub(r"([ML])([\d.]+) ([\d.]+)",
                       lambda m: f"{m[1]}{m[2]} {float(m[3]) * WORKFLOW_SCALE:g}", path.attrib["d"])
        value = re.sub(r"V([\d.]+)", lambda m: f"V{float(m[1]) * WORKFLOW_SCALE:g}", value)
        path.set("d", value)
    return figure


def property_source(helpers, cls, names, columns=64):
    """Wrap Property calls and string literals while preserving their Python AST."""
    source = helpers.fields(cls, set(names))
    tree = ast.parse(source)
    lines = [source.splitlines()[0]]
    for node in tree.body[0].body:
        declaration = "    " + ast.get_source_segment(source, node)
        if len(declaration) <= columns:
            lines.append(declaration)
            continue
        require(isinstance(node.value, ast.Call), "Expected a Property declaration")
        arguments = [ast.get_source_segment(source, arg) for arg in node.value.args]
        require(not node.value.keywords, "Long keyword declarations need explicit wrapping")
        lines.append(f"    {node.targets[0].id} = Property(")
        combined = "        " + ", ".join(arguments) + ")"
        if len(combined) <= columns:
            lines.append(combined)
            continue
        for index, (argument, value) in enumerate(zip(arguments, node.value.args)):
            ending = ")" if index == len(arguments) - 1 else ","
            if len(argument) + 8 + len(ending) <= columns:
                lines.append("        " + argument + ending)
                continue
            require(isinstance(value, ast.Constant) and isinstance(value.value, str),
                    "Only expression strings can be split across literals")
            chunks = textwrap.wrap(value.value, width=columns - 11, break_long_words=False,
                                   break_on_hyphens=False, replace_whitespace=False, drop_whitespace=False)
            require("".join(chunks) == value.value, "Wrapped expression changed")
            lines.extend("        " + json.dumps(chunk) + (ending if i == len(chunks) - 1 else "")
                         for i, chunk in enumerate(chunks))
    wrapped = "\n".join(lines)
    require(ast.dump(ast.parse(wrapped)) == ast.dump(tree), "Property source changed during wrapping")
    require(all(len(line) <= columns for line in lines), "Property source exceeds its panel")
    return wrapped


def battery_properties(*, complete=False):
    names = set(APP.declarations(Battery)) - set(APP.declarations(Component)) if complete else set(SELECTED)
    lines = [line for line in APP.prop_lines(Battery) if line.split(" [", 1)[0] in names]
    inherited = APP.prop_lines(Component) if complete else []
    offset = 38 + 16 * len(inherited) + 14 if inherited else 0
    figure = Figure("Battery property declarations", 186, offset + 38 + 16 * len(lines))
    if inherited:
        APP.card(figure, 0, 0, 186, "Component (inherited)", inherited, font=10.7, leading=16)
    APP.card(figure, 0, offset, 186, "Battery", lines, font=10.7, leading=16)
    return figure


def build_battery(helpers, job, *, complete=False):
    directory = APPENDIX if complete else DESIGN
    name = "battery-property-definitions" if complete else "battery-property-excerpt"
    diagram = directory / (name + "-diagram")
    rendered = render_figure(battery_properties(complete=complete), diagram, job)
    if complete:
        code = property_source(helpers, Component, APP.declarations(Component)) + "\n\n"
        code += property_source(helpers, Battery, set(APP.declarations(Battery)) - set(APP.declarations(Component)))
    else:
        code = property_source(helpers, Battery, SELECTED)
    helpers.OUT = directory
    listing = helpers.verb(code, 8).replace("{8}{10.24}", "{8}{9.4}")
    body = helpers.panel("Python property declarations", listing, 310)
    body += r"\hfill" + helpers.panel("Graphical representation", helpers.image(diagram.name + ".pdf", 186), 186)
    panel = helpers.make_pdf(name, body, job)
    APP.check_panel_widths(directory / (name + ".tex"))
    return diagram.relative_to(FIG).as_posix(), rendered, (directory / name).relative_to(FIG).as_posix(), panel


def main():
    helpers = APP.load_helpers()
    manifest = {"selected_properties": list(SELECTED), "diagrams": {}, "panels": {}}
    with tempfile.TemporaryDirectory(prefix="design-proposal-summaries-") as temporary:
        job = Path(temporary)
        manifest["diagrams"]["design-proposal/mission-workflow-summary"] = render_figure(
            workflow_summary(), DESIGN / "mission-workflow-summary", job)
        for complete in (False, True):
            diagram, rendered, name, panel = build_battery(helpers, job, complete=complete)
            manifest["diagrams"][diagram] = rendered
            manifest["panels"][name] = panel
    manifest["sources"] = {str(path.relative_to(ROOT)): sha(path) for path in (
        Path(__file__), FIG / "model-appendix-figures.py", FIG / "design-proposal-figures.py",
        FIG / "diagram_style.py", FIG / "code-highlighting.tex", ROOT / "framework/models/eps.py",
        ROOT / "framework/models/elements.py", ROOT / "framework/models/objects.py")}
    (DESIGN / "summaries.provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")

    # The appendix workflow's caption is a declared source of its provenance.
    path = APPENDIX / "provenance.json"
    provenance = json.loads(path.read_text())
    provenance["workflow_sources"] = APP.workflow_sources()
    path.write_text(json.dumps(provenance, indent=2) + "\n")
    print("Built the workflow summary and both Battery source/property figures.")


if __name__ == "__main__":
    main()
