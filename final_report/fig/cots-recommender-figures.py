"""Refresh only the report's COTS recommendation and inheritance figures.

Run with Playwright, Chromium and XeLaTeX. The GUI opens a temporary session.
The catalogue and mission sources are unchanged. Other report panels retain
their original captures and provenance.
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

from playwright.sync_api import sync_playwright

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
OUT = FIG / "design-proposal"
sys.path.insert(0, str(ROOT))

from framework.cots import get_product, load_catalog
from framework.cots.types import IntegratedEPS, BatteryIntegratedEPS
from framework.models import Battery, EPS
from framework.models.recommendations import recommend_cots


def helpers():
    spec = importlib.util.spec_from_file_location("cots_report_helpers", FIG / "design-proposal-figures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_hashes(h):
    paths = [Path(__file__).resolve(), FIG / "design-proposal-figures.py", FIG / "code-highlighting.tex"]
    paths += [ROOT / path for path in (
        "framework/cots/__init__.py", "framework/cots/types.py", "framework/cots/catalog.py",
        "framework/models/eps.py", "framework/models/elements.py", "framework/models/objects.py",
        "framework/models/properties.py", "framework/models/recommendations.py", "framework/models/requirements.py",
        "framework/gui/backend/application.py", "framework/gui/backend/views.py",
        "framework/gui/public/index.html", "framework/gui/public/recommendations.js", "framework/gui/public/style.css",
        "framework/sessions/example_cots_recommendations.py",
    )]
    paths += sorted((ROOT / "framework/cots").glob("*.tsv"))
    return {str(path.relative_to(ROOT)): h.sha(path) for path in paths}


def capture_cots(h, browser, job, args):
    session = job / "cots-study.py"
    session.write_text("from framework.sessions.example_cots_recommendations import mission\n")
    source_before = session.read_bytes()
    study = h.load_study(session)
    battery = study.mission.BUS.EPS.Battery
    matches = battery.recommend_cots(sort_by="rated_energy", reverse=True)
    numbers = [match.candidate.catalog_product.part_number for match in matches]
    assert numbers == ["INR-21700-M65A", "INR-21700-P50B", "INR-21700-P45B", "INR-21700-P42A", "INR-18650-M35A"]
    process, log, url = h.start_server(session, job, args.python)
    page = None
    try:
        page = h.open_page(browser, url, "mission.BUS.EPS.Battery", width=1100, height=2400)
        page.get_by_role("button", name="Recommend COTS", exact=True).click()
        page.locator("#recommendations-controls:not([disabled])").wait_for()
        assert "147 catalog products" in page.locator("#recommendations-summary").inner_text()
        page.locator("#recommendations-sort").select_option("rated_energy")
        page.locator("#recommendations-order").select_option("descending")
        page.locator("#recommendations-limit").fill("3")
        with page.expect_response(lambda response: response.url.endswith("/api/recommend-cots")) as response:
            page.get_by_role("button", name="Find matches", exact=True).click()
        result = response.value.json()
        page.locator("#recommendations-controls:not([disabled])").wait_for()
        assert result["catalogSize"] == 147
        assert result["compatibleProducts"] == 15
        assert [item["partNumber"] for item in result["results"]] == numbers[:3]
        assert page.locator(".recommendation-card h3").all_inner_texts() == numbers[:3]
        images = {"cots-matches": h.capture(page, "cots-matches", page.locator("#recommendations-results"))}
        for index in range(3):
            name = f"cots-match-{index + 1}"
            images[name] = h.capture(page, name, page.locator(".recommendation-card > header").nth(index))
        page.locator(".recommendation-card summary").first.click()
        images["cots-checks"] = h.capture(page, "cots-checks", page.locator(".recommendation-card .table-frame").first)
        images["cots-recommendations"] = h.capture(page, "cots-recommendations", page.locator("#recommendations-dialog"))
        assert session.read_bytes() == source_before
        assert not battery.cots
        checks = {"catalog_products": 147, "compatible_battery_products": 15,
                  "recommended_products": numbers, "displayed_products": numbers[:3],
                  "candidate_list_required": False, "temporary_session_unchanged": True}
        return images, checks
    finally:
        if page is not None:
            page.close()
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        log.close()


def query_panel(h, job):
    lines = inspect.getsource(recommend_cots).splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip().startswith("reports = tuple"))
    policy = textwrap.dedent("\n".join(lines[start:start + 3]))
    policy = policy.replace(
        "reports = tuple(requirement.verify(mode=selected_mode) for requirement in owner.requirements)",
        "reports = tuple(\n    requirement.verify(mode=selected_mode)\n    for requirement in owner.requirements)")
    policy = policy.replace("if any(report.verified is not True for report in reports):",
                            "if any(report.verified is not True\n       for report in reports):")
    call = 'matches = battery.recommend_cots(\n    sort_by="rated_energy",\n    reverse=True, limit=3)'
    body = h.panel("(a) Automatic catalogue query", h.verb(call, 8), 240)
    body += "\\hfill\n" + h.panel("(b) Every owned requirement must pass", h.verb(policy, 8), 260)
    body += "\\par\\medskip\\textbf{(c) Highest three rated energies (cropped GUI headers)}\\par\\smallskip\n"
    body += "\\par\\smallskip\n".join(h.image(f"cots-match-{index + 1}.png", 510) for index in range(3))
    body += "\\par\\medskip\\textbf{(d) Expanded verification for M65A}\\par\\smallskip\n"
    body += h.image("cots-checks.png", 510)
    return h.make_pdf("cots-query", body, job)


def inheritance_panel(h, job):
    declarations = h.fields(IntegratedEPS, {"catalog_parameters"}) + "\n\n" + h.fields(BatteryIntegratedEPS, {"maximum_voltage"})
    declarations = declarations.replace(
        "class IntegratedEPS(RegulatorAndConverter, PowerCircuit):",
        "class IntegratedEPS(\n    RegulatorAndConverter, PowerCircuit\n):")
    declarations = declarations.replace("    catalog_parameters = LoadSwitch.catalog_parameters",
                                        "    catalog_parameters = (\n        LoadSwitch.catalog_parameters)")
    declarations = declarations.replace("class BatteryIntegratedEPS(Battery, IntegratedEPS):",
                                        "class BatteryIntegratedEPS(\n    Battery, IntegratedEPS\n):")
    product = load_catalog().products["isispace_imeps2_base_4s1p"]
    selected = (
        ("battery", "rated_energy", "nominal", ""),
        ("battery", "maximum_voltage", "maximum", ""),
        ("battery", "maximum_voltage", "absolute_maximum", ""),
        ("vd1_5v", "output_voltage", "nominal", "boards_factory_default"),
        ("vd1_5v_ch1", "maximum_output_current", "maximum", ""),
    )
    rows = []
    for element, name, kind, condition in selected:
        facts = [fact for fact in product.facts if fact.model_property == name and fact.element_id == element
                 and fact.value_kind == kind and fact.condition_id == condition]
        assert len(facts) == 1
        fact = facts[0]
        rows.append(r"\texttt{" + h.escape(element) + r"} & \texttt{" + h.escape(name) + "} & "
                    + f"{fact.value:g}~{h.escape(fact.unit)}" + r"\newline " + h.escape(kind.replace("_", " ")) + r" \\")
    table = (r"{\fontsize{8}{10}\selectfont\setlength{\tabcolsep}{3pt}"
             r"\begin{tabular}{@{}p{54pt}p{109pt}p{75pt}@{}}"
             r"\textbf{Element} & \textbf{Property} & \textbf{Rating} \\ \hline" + "\n"
             + "\n".join(rows) + "\n" + r"\end{tabular}}")
    call = ('from framework.cots import get_product\nfrom framework.models import Battery\n\n'
            'pack = get_product(\n    "isispace_imeps2_base_4s1p",\n'
            '    model_class=Battery, element_id="battery",\n'
            '    value_kinds={"rated_energy": "nominal"})\n'
            'print(pack.rated_energy.value, pack.maximum_voltage.value)\n# 45.0 16.0')
    pack = get_product(product.product_id, model_class=Battery, element_id="battery", value_kinds={"rated_energy": "nominal"})
    assert pack.fixed_properties and (pack.rated_energy.value, pack.maximum_voltage.value) == (45, 16)
    body = h.panel("(a) Selected inherited definitions", h.verb(declarations, 7.7), 245)
    body += "\\hfill\n" + h.panel("(b) Catalogue values for IMEPS2", table, 255)
    body += "\\par\\medskip\n" + h.panel("(c) Concrete product and explicit fact selection", h.verb(call, 8), 506)
    return h.make_pdf("cots-inheritance", body, job)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromium")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    h = helpers()
    path = OUT / "provenance.json"
    manifest = json.loads(path.read_text()) if path.exists() else {"screenshots": {}, "panels": {}, "checks": {}}
    manifest["cots_sources"] = source_hashes(h)
    with tempfile.TemporaryDirectory(prefix="report-cots-") as temporary:
        job = Path(temporary)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**({"executable_path": args.chromium} if args.chromium else {}))
            try:
                images, checks = capture_cots(h, browser, job, args)
            finally:
                browser.close()
        manifest["screenshots"].update(images)
        manifest["checks"].update(checks)
        manifest["panels"]["cots-query"] = query_panel(h, job)
        manifest["panels"]["cots-inheritance"] = inheritance_panel(h, job)
    catalog = load_catalog()
    manifest["catalog"] = {"total": len(catalog), "counts_csrm": {
        cls.__name__: sum(issubclass(product.model_class, cls) for product in catalog.products.values())
        for cls in EPS.default_components}, "products_sha256": h.sha(ROOT / "framework/cots/products.tsv")}
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
