"""Generate the design proposal's live GUI evidence and source comparisons.

Requires Python with Playwright, a Chromium installation, Node.js and XeLaTeX.
Run from any directory, for example:
    python design-proposal-figures.py --chromium /path/to/chrome-headless-shell
Optional --python selects the GUI's Python interpreter (default: python3).
Only temporary session copies are edited. The framework sources stay unchanged.
Screenshots retain the native GUI styling. Authored panels use Times New Roman,
Courier New for Python, white backgrounds and thin rectangular black borders.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
OUT = FIG / "design-proposal"
sys.path.insert(0, str(ROOT))

from framework.models import Battery, Property, Requirement, VerificationCondition
from framework.models.recommendations import recommend_cots
from framework.scripts import sizing


def run(args, **kwargs):
    result = subprocess.run(args, check=True, text=True, capture_output=True, **kwargs)
    return result.stdout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_study(path):
    spec = importlib.util.spec_from_file_location("figure_study", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fields(cls, names):
    """Read real class declarations, wrapping literals without changing them."""
    tree = ast.parse(inspect.getsource(cls))
    lines = [f"class {cls.__name__}({', '.join(c.id for c in tree.body[0].bases)}):"]
    for node in tree.body[0].body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names for target in node.targets
        ):
            source = ast.get_source_segment(inspect.getsource(cls), node)
            lines.extend("    " + line for line in source.splitlines())
    return "\n".join(lines)


def snippet(source):
    """Remove indentation from a displayed, explicitly wrapped code excerpt."""
    return textwrap.dedent(source).strip()


def escape(text):
    return "".join({"\\": r"\textbackslash{}", "_": r"\_", "&": r"\&",
                    "%": r"\%", "#": r"\#", "{": r"\{", "}": r"\}"}.get(c, c) for c in text)


def verb(code, size=8):
    return (f"\\begin{{Verbatim}}[fontsize=\\fontsize{{{size}}}{{{size * 1.28}}}\\selectfont]\n"
            + code + "\n\\end{Verbatim}\n")


def panel(title, body, width):
    return (f"\\begin{{minipage}}[t]{{{width}pt}}\n\\vspace{{0pt}}"
            f"\\textbf{{{escape(title)}}}\\par\\smallskip\n" + body + "\\end{minipage}")


def image(name, width):
    return f"\\includegraphics[width={width}pt]{{{name}}}"


def make_pdf(name, body, job):
    source = r"""\documentclass[border=5pt]{standalone}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\setmonofont{Courier New}
\usepackage{amsmath,graphicx,fancyvrb}
\setlength{\fboxsep}{7pt}
\setlength{\fboxrule}{0.5pt}
\begin{document}
\begin{minipage}{510pt}
\fontsize{10}{12}\selectfont
""" + body + "\n\\end{minipage}\n\\end{document}\n"
    tex = job / f"{name}.tex"
    tex.write_text(source)
    result = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                             f"-output-directory={job}", str(tex)], cwd=OUT,
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout[-8000:])
    if "Overfull" in result.stdout:
        raise RuntimeError(f"Clipped panel in {name}:\n{result.stdout}")
    shutil.copyfile(job / f"{name}.pdf", OUT / f"{name}.pdf")
    # Keep the exact typesetting source with the figure for independent rebuilds.
    shutil.copyfile(tex, OUT / f"{name}.tex")
    return {"pdf_sha256": sha(OUT / f"{name}.pdf"), "source_sha256": sha(tex)}


def start_server(session, job, python):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, MISSION_FILE=str(session), PORT=str(port),
               VERIFICATION_PYTHON=python, PYTHONPATH=str(ROOT))
    log = (job / f"server-{port}.log").open("w")
    process = subprocess.Popen(["node", "framework/gui/server.mjs"], cwd=ROOT, env=env,
                               stdout=log, stderr=subprocess.STDOUT)
    url = f"http://127.0.0.1:{port}"
    for _ in range(200):
        if process.poll() is not None:
            raise RuntimeError(f"GUI failed to start. See {log.name}")
        try:
            with urlopen(url, timeout=1):
                return process, log, url
        except OSError:
            time.sleep(0.05)
    process.terminate()
    raise RuntimeError("GUI did not start")


def capture(page, name, locator=None, clip=None):
    page.mouse.move(0, 0)
    path = OUT / f"{name}.png"
    if locator is not None:
        locator.screenshot(path=path, animations="disabled")
    else:
        page.screenshot(path=path, clip=clip, animations="disabled")
    return {"sha256": sha(path), "pixel_scale": 2}


def open_page(browser, url, context, width=1600, height=1120):
    page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
    page.goto(f"{url}/#{context}")
    page.locator("#workspace:not([inert])").wait_for()
    page.locator("#status").filter(has_text="Opening").wait_for(state="hidden")
    return page


def edit(page, path):
    page.locator(f'[data-edit="{path}"]').click()
    page.locator("#object-editor:not([hidden])").wait_for()


def scroll_to(page, selector):
    page.evaluate("""selector => {
        const content = document.querySelector('.editor-content');
        const target = document.querySelector(selector);
        content.scrollTop += target.getBoundingClientRect().top - content.getBoundingClientRect().top - 8;
    }""", selector)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromium", help="Chromium executable, if outside Playwright's default cache")
    parser.add_argument("--python", default="python3", help="Python interpreter for the GUI backend")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    manifest = {"description": "Live, unmodified GUI captures and source excerpts for the design proposal",
                "screenshots": {}, "panels": {}, "checks": {}}
    demo_source = (FIG / "design-proposal-demo.py").read_text()
    manifest["demo_sha256"] = sha(FIG / "design-proposal-demo.py")
    manifest["framework_sources"] = {str(path.relative_to(ROOT)): sha(path) for path in (
        ROOT / "framework/models/eps.py", ROOT / "framework/models/properties.py",
        ROOT / "framework/models/requirements.py", ROOT / "framework/models/recommendations.py",
        ROOT / "framework/scripts/sizing.py", ROOT / "framework/gui/public/editor.js",
        ROOT / "framework/gui/public/style.css")}

    with tempfile.TemporaryDirectory(prefix="design-proposal-") as temporary:
        job = Path(temporary)
        baseline = job / "battery-study.py"
        baseline.write_text(demo_source)
        study = load_study(baseline)
        assert study.battery.rated_energy.value == 20.35
        assert study.battery.bol_energy.value == 73260
        assert study.requirement.required.value == 14400
        assert study.requirement.verify().verified is True
        manifest["checks"].update(initial_energy_j=73260, required_energy_j=14400, initial_verified=True)

        processes = []
        try:
            process, log, url = start_server(baseline, job, args.python)
            processes.append((process, log))
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(**({"executable_path": args.chromium} if args.chromium else {}))
                manifest["browser"] = browser.version
                page = open_page(browser, url, "mission.BUS.EPS.Battery", width=1000)
                assert page.locator("#requirement-rows .result").inner_text() == "Pass"
                manifest["screenshots"]["requirement-before"] = capture(
                    page, "requirement-before", page.locator(".requirements"))
                page.set_viewport_size({"width": 1600, "height": 1120})

                edit(page, "mission.BUS.EPS.Battery")
                scroll_to(page, '[aria-label="expression for rated_energy"]')
                assert page.locator('[aria-label="expression for rated_energy"]').input_value() == "20.35"
                assert page.locator('[aria-label="expression for bol_energy"]').input_value() == "self.rated_energy.value * 3600"
                for field in ("rated_energy", "bol_energy"):
                    row = page.locator(f'[aria-label="expression for {field}"]').locator("xpath=ancestor::tr")
                    name = "battery-" + field.replace("_", "-")
                    manifest["screenshots"][name] = capture(page, name, row)
                page.get_by_role("button", name="Close editor", exact=True).click()

                edit(page, "mission.BUS.EPS.Battery.energy_reserve")
                assert "73260 J" in page.locator("[data-statement-preview]").inner_text()
                manifest["screenshots"]["rendered-statement"] = capture(
                    page, "rendered-statement", page.locator("[data-statement-preview]"))
                manifest["screenshots"]["verification-condition"] = capture(
                    page, "verification-condition", page.locator(".condition-card"))
                scroll_to(page, ".editor-section")
                assert page.locator('[aria-label="expression for required"]').input_value().endswith(").joules")
                assert page.locator('[data-condition-result="0"]').inner_text() == "Pass"
                manifest["screenshots"]["analysis-mappings"] = capture(
                    page, "analysis-mappings", page.locator("#object-editor"))
                page.get_by_role("button", name="Close editor", exact=True).click()

                # Change one input through the real GUI, wait for native preview,
                # save it, and inspect the updated requirement and session source.
                edit(page, "mission.BUS.EPS.Battery")
                page.locator('[aria-label="expression for rated_energy"]').fill("3.0")
                page.wait_for_function("""() => {
                    const field = document.querySelector('[aria-label="expression for bol_energy"]');
                    return field.closest('tr').querySelector('.parameter-result').textContent === '10800';
                }""")
                manifest["checks"]["gui_preview_energy_j"] = 10800
                page.get_by_role("button", name="Save", exact=True).click()
                page.locator("#object-editor").wait_for(state="hidden")
                assert page.locator("#requirement-rows .result").inner_text() == "Fail"
                assert "10800 J" in page.locator("#requirement-rows").inner_text()
                assert "14400 J" in page.locator("#requirement-rows").inner_text()
                page.set_viewport_size({"width": 1000, "height": 1120})
                manifest["screenshots"]["requirement-after"] = capture(
                    page, "requirement-after", page.locator(".requirements"))
                saved = load_study(baseline)
                assert saved.requirement.verify().verified is False
                assert saved.battery.bol_energy.value == 10800
                manifest["checks"].update(saved_energy_j=10800, saved_verified=False)
                page.close()

                # A separate view of the same temporary mission shows automatically
                # created EPS requirements with both resolved and unset targets.
                automatic = open_page(browser, url, "mission.BUS.EPS", width=1600, height=1120)
                rows = automatic.locator("#requirement-rows tr")
                assert rows.count() == len(study.eps.requirements)
                assert "{minimum.target}" in rows.nth(4).inner_text()
                assert "Pending" in rows.nth(4).inner_text()
                assert "{minimum.target}" not in rows.nth(0).inner_text()
                bounds = automatic.locator(".requirements").bounding_box()
                bottom = rows.nth(4).bounding_box()
                bounds["height"] = bottom["y"] + bottom["height"] - bounds["y"]
                manifest["screenshots"]["automatic-requirements"] = capture(
                    automatic, "automatic-requirements", clip=bounds)
                manifest["checks"]["automatic_eps_requirements"] = rows.count()
                automatic.close()

                # The sourced COTS study stays separate from the synthetic pack.
                cots_file = job / "cots-study.py"
                cots_file.write_text("from framework.sessions.example_cots_recommendations import mission, cots_catalog\n")
                process, log, cots_url = start_server(cots_file, job, args.python)
                processes.append((process, log))
                cots = open_page(browser, cots_url, "mission.BUS.EPS.Battery", width=700, height=1120)
                cots.get_by_role("button", name="Recommend COTS", exact=True).click()
                cots.locator("#recommendations-dialog[open]").wait_for()
                cots.locator("#recommendations-sort").select_option("rated_energy")
                cots.locator("#recommendations-order").select_option("descending")
                cots.locator("#recommendations-limit").fill("3")
                cots.get_by_role("button", name="Find matches", exact=True).click()
                cots.wait_for_function("""() => document.querySelector('.recommendation-card h3')?.textContent === 'P45B'""")
                assert cots.locator(".recommendation-card h3").all_inner_texts() == ["P45B", "P42A", "M35A"]
                manifest["screenshots"]["cots-matches"] = capture(
                    cots, "cots-matches", cots.locator("#recommendations-results"))
                # The results retain native measures, targets and predicates.
                cots.locator(".recommendation-card summary").first.click()
                manifest["screenshots"]["cots-checks"] = capture(
                    cots, "cots-checks", cots.locator(".recommendation-card .table-frame").first)
                manifest["screenshots"]["cots-recommendations"] = capture(
                    cots, "cots-recommendations", cots.locator("#recommendations-dialog"))
                manifest["checks"]["recommended_products"] = ["P45B", "P42A", "M35A"]
                cots.close()
                browser.close()
        finally:
            for process, log in reversed(processes):
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                log.close()

        # Source panels. Every framework excerpt is taken from inspected source.
        battery_fields = fields(Battery, {"rated_energy", "bol_energy"})
        # Wrap the actual rated_energy string across adjacent Python literals.
        battery_fields = battery_fields.replace(
            '    rated_energy = Property("self.cell_count.value * self.cell_rated_energy.value", "Wh")',
            '    rated_energy = Property(\n        "self.cell_count.value * "\n        "self.cell_rated_energy.value", "Wh")')
        battery_fields = battery_fields.replace(
            '    bol_energy = Property("self.rated_energy.value * 3600", "J")',
            '    bol_energy = Property(\n        "self.rated_energy.value * 3600", "J")')
        repl = snippet('''
            >>> from framework.models import (
            ...     Mission, CubeSatBus)
            >>> mission = Mission()
            >>> bus = mission.add(CubeSatBus("BUS"))
            >>> battery = bus.EPS.Battery
            >>> battery.rated_energy = 20.35
            >>> battery.rated_energy.value
            20.35
            >>> battery.bol_energy.value
            73260.0
        ''')
        body = panel("(a) Battery class (selected lines)", verb(battery_fields, 8), 250)
        body += "\\hfill\n" + panel("(b) Interactive Python", verb(repl, 8), 250)
        manifest["panels"]["eps-python-model"] = make_pdf("eps-python-model", body, job)

        body = "\\textbf{(a) Rated energy entered in Wh}\\par\\smallskip\n"
        body += image("battery-rated-energy.png", 510)
        body += "\\par\\medskip\\textbf{(b) Beginning-of-life energy calculated in J}\\par\\smallskip\n"
        body += image("battery-bol-energy.png", 510)
        manifest["panels"]["eps-gui"] = make_pdf("eps-gui", body, job)

        energy_source = inspect.getsource(sizing.battery_energy)
        energy_lines = [line.strip() for line in energy_source.splitlines()
                        if line.strip().startswith(("energy =", "_finite(energy)", "return Energy"))]
        assert len(energy_lines) == 3
        assert energy_lines[0] == "energy = eclipse_energy / depth_of_discharge * (1 + degradation_margin)"
        # Parentheses make the displayed line break executable Python.
        calculation = "energy = (eclipse_energy / depth_of_discharge\n          * (1 + degradation_margin))\n" + "\n".join(energy_lines[1:])
        algebra = r"""\[
E_{\mathrm{Battery}}=\frac{E_e}{\mathrm{DoD}}(1+M)
\]
\begin{tabular}{@{}ll@{}}
\texttt{eclipse\_energy} & $E_e$ (J)\\
\texttt{depth\_of\_discharge} & $\mathrm{DoD}$\\
\texttt{degradation\_margin} & $M$
\end{tabular}
\[
\frac{6000~\mathrm{J}}{0.5}(1+0.2)=14400~\mathrm{J}
\]
"""
        body = panel("(a) Battery sizing calculation", verb(calculation, 8), 270)
        body += "\\hfill\n" + panel("(b) Algebraic expression", algebra, 230)
        manifest["panels"]["analysis-equation"] = make_pdf("analysis-equation", body, job)

        # Read the public constructor and value accessor verbatim.
        property_init = inspect.getsource(Property.__init__)
        property_init = "\n".join(line for line in property_init.splitlines()
                                  if line.strip().startswith(("def ", "self.expression", "self.unit")))
        accessor = textwrap.dedent(inspect.getsource(Property.value.fget)).strip()
        declarations = "class Property:\n" + property_init + "\n\n" + textwrap.indent(accessor, "    ")
        expression = snippet('''
            required = Property(
                "sizing.battery_energy("
                "eclipse_energy=self.eclipse_energy, "
                "depth_of_discharge=self.depth_of_discharge, "
                "degradation_margin=self.degradation_margin"
                ").joules", "J")
        ''')
        # This is exactly the expression used by the live requirement.
        expression_tree = ast.parse(expression)
        shown_expression = ast.literal_eval(expression_tree.body[0].value.args[0])
        assert shown_expression == study.requirement.required.expression
        body = panel("(a) Property class (selected lines)", verb(declarations, 8), 245)
        body += "\\hfill\n" + panel("(b) Calculated requirement property", verb(expression, 7.6), 255)
        body += "\\par\\medskip\\textbf{(c) GUI statement after evaluation}\\par\\smallskip\n"
        body += image("rendered-statement.png", 510)
        manifest["panels"]["property-expressions"] = make_pdf("property-expressions", body, job)

        condition_fields = fields(VerificationCondition, {"measure", "target"})
        verify = textwrap.dedent(inspect.getsource(Requirement.verify)).strip()
        # Equivalent wrapping of the actual one-line verification return.
        verify = verify.replace(
            "    return VerificationReport(self.mission, tuple(condition.evaluate(mode=mode) for condition in self.conditions))",
            "    return VerificationReport(self.mission, tuple(\n        condition.evaluate(mode=mode)\n        for condition in self.conditions))")
        links = condition_fields + "\n\n" + snippet('''
            condition = VerificationCondition(
                "minimum", battery.bol_energy,
                Property("self.parent.required", "J"),
                "measure >= target")
        ''')
        body = panel("(a) Stored verification links", verb(links, 7.5), 225)
        body += "\\hfill\n" + panel("(b) GUI verification condition", image("verification-condition.png", 275), 275)
        body += "\\par\\medskip\\textbf{(c) Requirement evaluation method}\\par\n" + verb(verify, 8)
        manifest["panels"]["requirement-links"] = make_pdf("requirement-links", body, job)

        body = panel("(a) Before: 20.35 Wh, Pass", image("requirement-before.png", 250), 250)
        body += "\\hfill\n" + panel("(b) After: 3.0 Wh, Fail", image("requirement-after.png", 250), 250)
        manifest["panels"]["parameter-impact"] = make_pdf("parameter-impact", body, job)

        query_source = inspect.getsource(recommend_cots)
        query_lines = query_source.splitlines()
        policy_start = next(i for i, line in enumerate(query_lines) if line.strip().startswith("reports = tuple"))
        policy_end = policy_start + 3
        policy = textwrap.dedent("\n".join(query_lines[policy_start:policy_end]))
        assert "report.verified is not True" in policy
        policy = policy.replace(
            "reports = tuple(requirement.verify(mode=selected_mode) for requirement in owner.requirements)",
            "reports = tuple(\n    requirement.verify(mode=selected_mode)\n    for requirement in owner.requirements)")
        policy = policy.replace(
            "if any(report.verified is not True for report in reports):",
            "if any(report.verified is not True\n       for report in reports):")
        call = snippet('''
            matches = battery.recommend_cots(
                cots_catalog,
                sort_by="rated_energy",
                reverse=True, limit=3)
        ''')
        body = panel("(a) Candidate acceptance", verb(policy, 7.5)
                     + "\\medskip\\textbf{Python query}\\par\n" + verb(call, 7.5), 210)
        body += "\\hfill\n" + panel("(b) GUI recommendations", image("cots-matches.png", 290), 290)
        body += "\\par\\medskip\\textbf{(c) Expanded verification for P45B}\\par\\smallskip\n"
        body += image("cots-checks.png", 510)
        manifest["panels"]["cots-query"] = make_pdf("cots-query", body, job)

        # Produce a real Git diff in an isolated repository. No user branch,
        # index, identity or working file is touched.
        git_job = job / "git-study"
        git_job.mkdir()
        git_file = git_job / "battery-study.py"
        git_file.write_text(demo_source)
        run(["git", "init", "-q", str(git_job)])
        run(["git", "add", git_file.name], cwd=git_job)
        run(["git", "-c", "user.name=Report figures", "-c", "user.email=figures@example.invalid",
             "-c", "commit.gpgsign=false", "commit", "-qm", "Retain the 20.35 Wh study"], cwd=git_job)
        git_file.write_text(demo_source.replace("battery.rated_energy = 20.35", "battery.rated_energy = 3.0"))
        diff = run(["git", "diff", "--no-ext-diff", "--unified=1", "--", git_file.name], cwd=git_job).strip()
        assert "-battery.rated_energy = 20.35" in diff and "+battery.rated_energy = 3.0" in diff
        changed = load_study(git_file)
        assert changed.requirement.verify().verified is False
        body = "\\textbf{(a) Git comparison with the retained baseline}\\par\n" + verb("$ git diff -- battery-study.py\n" + diff, 8.5)
        body += "\\par\\medskip\n"
        body += panel("(b) Baseline evaluation", verb(
            ">>> battery.bol_energy.value\n73260.0\n>>> requirement.verify().verified\nTrue", 8.5), 250)
        body += "\\hfill\n" + panel("(c) Edited evaluation", verb(
            ">>> battery.bol_energy.value\n10800.0\n>>> requirement.verify().verified\nFalse", 8.5), 250)
        manifest["panels"]["configuration-diff"] = make_pdf("configuration-diff", body, job)
        manifest["checks"]["git_diff_changes_one_property"] = True

    with (ROOT / "framework/cots/products.tsv").open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    counts = {}
    for row in rows:
        counts[row["model_type"]] = counts.get(row["model_type"], 0) + 1
    assert len({row["product_id"] for row in rows}) == len(rows)
    manifest["catalog"] = {"total": len(rows), "counts": counts,
                           "products_sha256": sha(ROOT / "framework/cots/products.tsv")}
    (OUT / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Generated {len(manifest['panels'])} PDF panels and {len(manifest['screenshots'])} live GUI captures in {OUT}")
    print(json.dumps(manifest["checks"], indent=2))


if __name__ == "__main__":
    main()
