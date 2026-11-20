#!/usr/bin/env python3
"""Run live MOP-11 queries against original-document decimal references.

Run from the repository root with Python 3.12. This uses the built-in catalogue,
never an explicit candidate list. Framework source and catalogue data are read
only. Outputs are audit records, not a claim of complete mission qualification.
"""

import argparse
from dataclasses import asdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent / "eps-case-studies"
sys.path[:0] = [str(ROOT), str(HERE)]

# Standalone entry point: resolve the repository and adjacent reference module first.
import independent_cots_reference as ref  # noqa: E402
from framework.cots import load_catalog  # noqa: E402
from framework.models import EPS, CubeSatBus, Mission, Property, Software, VerificationCondition  # noqa: E402


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def mission_snapshot(mission):
    return canonical([
        {"path": obj.path, "type": type(obj).__name__,
         "children": [child.path for child in obj.children],
         "properties": {name: [prop.expression, str(prop.unit)] for name, prop in obj.properties.items()},
         "statement": getattr(obj, "statement", None),
         "rationale": getattr(obj, "rationale", None),
         "condition": getattr(obj, "expression", None)}
        for obj in mission.walk()
    ])


def catalog_snapshot(catalog):
    # Generated Python class caches are excluded. Published engineering records
    # and source tables must remain identical, both in memory and on disk.
    return canonical({
        "products": [{"id": product.product_id, "type": product.model_class.__name__,
                      "part": product.part_number, "manufacturer": product.manufacturer,
                      "level": product.product_level, "url": product.product_url,
                      "datasheet": product.datasheet_url,
                      "facts": [asdict(fact) for fact in product.facts]}
                     for product in catalog.products.values()],
        "sources": {key: dict(value) for key, value in catalog.sources.items()},
        "conditions": {key: dict(value) for key, value in catalog.conditions.items()},
        "elements": {str(key): value for key, value in catalog.elements.items()},
        "condition_parameters": {key: [dict(row) for row in rows]
                                 for key, rows in catalog.condition_parameters.items()},
        "curves": {str(key): [dict(row) for row in rows] for key, rows in catalog.curves.items()},
    })


def make_case(key, scenario):
    part = ref.PARTS[key]
    values = ref.inputs(key, scenario)
    mission = Mission()
    bus = mission.add(CubeSatBus("BUS"))
    owner = getattr(bus.EPS, part["role"])
    units = {
        "load": "Wh", "period": "min", "eclipse": "min", "diode": "Wh", "conversion": "1",
        "generation": "Wh", "after_bcr_printed": "Wh", "battery_cells": "cell", "budget_voltage": "V",
        "solar_cells": "cell", "dod": "1", "delivery": "1", "projection": "1", "standby": "Wh",
        "live": "Wh", "passes": "1", "sunlight_fraction": "1", "generation_power": "W",
        "generation_printed": "Wh", "balance_printed": "Wh",
    }
    for name, value in values.items():
        mission.define("case_" + name, Property(value, units[name]))
    if part["role"] == "Battery":
        expression = ("self.case_load.value / (self.case_battery_cells.value * "
                      "self.case_budget_voltage.value * self.case_dod.value * self.case_delivery.value)")
    else:
        hours = ("(self.case_period.value - self.case_eclipse.value) / 60" if "eclipse" in values else
                 "self.case_period.value / 60 * self.case_sunlight_fraction.value")
        expression = ("(self.case_load.value / self.case_conversion.value + self.case_diode.value) / "
                      f"(self.case_solar_cells.value * self.case_projection.value * ({hours}))")
    mission.define("case_required", Property(expression, part["unit"]))
    owner.add_requirement(
        "purchased_scope", statement="The purchased item shall contain one physical cell.",
        rationale="Installation counts belong to the separately recorded mission arrangement.",
        conditions=(
            VerificationCondition("series", owner.series_count, Property(1, "cell"),
                                  "type(measure) is int and measure == target"),
            VerificationCondition("parallel", owner.parallel_count, Property(1, "string"),
                                  "type(measure) is int and measure == target"),
        ),
    )
    owner.add_requirement(
        "mission_budget", statement="The purchased cell shall provide at least {minimum.target}.",
        rationale="Published mission demand and the declared arrangement, losses and illumination.",
        conditions=(VerificationCondition("minimum", getattr(owner, part["property"]),
                                          mission.case_required, "measure >= target"),),
    )
    if part["role"] == "Battery":
        owner.add_requirement(
            "voltage_convention", statement="The cell shall meet the declared nominal voltage interval.",
            rationale="Preserve mission and manufacturer nominal/average voltage conventions separately.",
            conditions=(VerificationCondition("interval", owner.nominal_voltage,
                Property(repr(tuple(float(x) for x in part["voltage_interval"])), "V"),
                "target[0] <= measure <= target[1]"),),
        )
        if scenario == "missing":
            owner.add_requirement(
                "mission_retention", statement="The cell shall retain at least {minimum.target} at mission end.",
                rationale="No applicable mission retention model has been supplied.",
                conditions=(VerificationCondition("minimum", owner.eol_capacity,
                                                   mission.case_required, "measure >= target"),),
            )
    return mission, owner


def install_properties(owner, candidate):
    """Separate isolated public Requirement evaluation, including rejected parts.

    Recommendation results contain only successful trials. This diagnostic copy
    exposes the actual false/pending conditions of a documented excluded part.
    Expected values and decisions still come exclusively from the PDF references.
    """
    for name, prop in candidate.properties.items():
        definition = prop.copy(None, name)
        if name in owner.properties:
            setattr(owner, name, definition)
        else:
            owner.define(name, definition)


def condition_records(owner):
    return [{"requirement": requirement.name, "condition": item.condition.name,
             "status": item.status.value, "verified": item.value,
             "measure": item.measure, "target": item.target, "message": item.message}
            for requirement in owner.requirements for item in requirement.verify().results]


def compare(checks, label, expected, actual):
    error = None
    if expected is None or isinstance(expected, (bool, str)):
        passed = expected == actual and type(expected) is type(actual)
    else:
        expected = Decimal(str(expected))
        try:
            actual_decimal = Decimal(str(actual))
            error = abs(actual_decimal - expected) / abs(expected) if expected else Decimal(0)
            passed = actual_decimal.is_finite() and (actual_decimal == 0 if expected == 0 else error <= Decimal("0.01"))
        except (ArithmeticError, ValueError, TypeError):
            passed = False
    checks.append({"check": label, "expected": str(expected) if isinstance(expected, Decimal) else expected,
                   "actual": actual, "relative_error": str(error) if error is not None else None,
                   "passed": passed})


def source_records():
    result = {}
    for key, source in ref.SOURCES.items():
        path = ROOT / source["path"]
        if not path.is_file():
            raise FileNotFoundError(f"Original source PDF missing: {path} ({source['url']})")
        actual = digest(path)
        if source.get("sha256") and source["sha256"] != actual:
            raise ValueError(f"Original source PDF changed: {key}")
        result[key] = dict(source, sha256=actual)
    return result


def run(output):
    catalog = load_catalog()
    record_snapshot = catalog_snapshot(catalog)
    framework_paths = sorted(path for folder in ("models", "scripts", "cots")
                             for path in (ROOT / "framework" / folder).glob("*")
                             if path.suffix in (".py", ".tsv"))
    hashes = {str(path.relative_to(ROOT)): digest(path) for path in framework_paths}
    sources = source_records()
    queries, all_checks = [], []
    for key, part in ref.PARTS.items():
        scenarios = ["baseline", "strict", "missing"]
        if part["role"] == "SolarArray":
            scenarios.append("radiation")
        for scenario in scenarios:
            mission, owner = make_case(key, scenario)
            expected = ref.reference(key, scenario)
            condition = part["radiation_condition"] if scenario == "radiation" else part["condition"]
            value_kinds = {"maximum_power": "minimum"} if scenario == "missing" and part["role"] == "SolarArray" else {}
            selectors = {"condition_id": condition, "value_kinds": value_kinds}
            before = mission_snapshot(mission)
            matches = owner.recommend_cots(**selectors)
            unchanged = before == mission_snapshot(mission)
            records_unchanged = record_snapshot == catalog_snapshot(catalog)
            files_unchanged = all(digest(ROOT / path) == sha for path, sha in hashes.items())
            checks = []
            compare(checks, "mission unchanged", True, unchanged)
            compare(checks, "catalogue records unchanged", True, records_unchanged)
            compare(checks, "framework and catalogue files unchanged", True, files_unchanged)
            included = any(match.candidate.product_id == part["product_id"] and
                           match.candidate.catalog_element == "self" for match in matches)
            compare(checks, "documented part inclusion", expected["verified"] is True, included)
            compare(checks, "derived purchased-cell requirement", Decimal(expected["target"]), mission.case_required.value)
            if included:
                selected = next(match for match in matches if match.candidate.product_id == part["product_id"])
                compare(checks, "automatic trial verdict", True, selected.report.verified)
                compare(checks, "automatic trial status", "value", selected.report.status.value)
                automatic_owner = selected.report.mission.get(owner.path)
                compare(checks, "automatic trial purchased-cell measure", Decimal(expected["rating"]),
                        getattr(automatic_owner, part["property"]).value)
                compare(checks, "automatic trial selected condition", condition, automatic_owner.catalog_condition)
                budget_result = next(item for item in selected.report.results
                                     if item.requirement.name == "mission_budget")
                compare(checks, "automatic trial requirement target", Decimal(expected["target"]), budget_result.target)
            candidate = catalog.product(part["product_id"], model_class=part["role"], **selectors)
            probe, isolated_owner = make_case(key, scenario)
            install_properties(isolated_owner, candidate)
            records = condition_records(isolated_owner)
            verdicts = [requirement.verify().verified for requirement in isolated_owner.requirements]
            verified = False if False in verdicts else True if all(value is True for value in verdicts) else None
            status = ("error" if any(item["status"] == "error" for item in records) else
                      "pending" if any(item["status"] == "pending" for item in records) else "value")
            compare(checks, "isolated owned-requirement verdict", expected["verified"], verified)
            compare(checks, "isolated owned-requirement status", expected["status"], status)
            assessment = getattr(candidate, part["property"]).assess()
            if scenario != "missing" or part["role"] == "Battery":
                compare(checks, "source-qualified purchased-cell rating", Decimal(expected["rating"]), assessment.value)
            else:
                compare(checks, "missing minimum power status", "pending", assessment.status.value)
            if part["role"] == "Battery":
                compare(checks, "source-qualified voltage convention", Decimal(part["voltage"]), candidate.nominal_voltage.value)
            bindings = [{"property": binding.property_name, "element": binding.element_id,
                         "class": binding.model_class, "facts": [asdict(fact) for fact in binding.facts]}
                        for binding in candidate.catalog_bindings if binding.property_name in
                        (part["property"], "nominal_voltage", "series_count", "parallel_count", "eol_capacity")]
            queries.append({"case": key, "mission": part["mission"], "scenario": scenario,
                            "role": part["role"], "documented_part": part["product_id"],
                            "inputs": ref.inputs(key, scenario), "reference": expected,
                            "selectors": selectors, "target": mission.case_required.value,
                            "rating": assessment.value, "rating_status": assessment.status.value,
                            "included": included, "verified": verified, "status": status,
                            "matches": [{"product": match.candidate.product_id,
                                         "element": match.candidate.catalog_element} for match in matches],
                            "diagnostic_conditions": records, "bindings": bindings, "checks": checks})
            all_checks.extend(dict(item, mission=part["mission"], case=key, scenario=scenario) for item in checks)

    # Public Properties also evaluate the matching printed budget arithmetic.
    budget = Mission()
    for name, expression in {
        "birds_after_bcr": "(2.173 - 0.240) * 0.80",
        "oresat_generation": "2.600 * 0.59 * 0.71 * 1.5",
        "oresat_balance": "1.634 - 0.623",
    }.items():
        budget.define(name, Property(expression, "Wh"))
    printed = {"birds_after_bcr": ref.BIRDS["after_bcr_printed"],
               "oresat_generation": ref.ORESAT["generation_printed"],
               "oresat_balance": ref.ORESAT["balance_printed"]}
    benchmarks = []
    for name, expected in ref.published_references().items():
        actual = getattr(budget, name).value
        compare(benchmarks, name + ": independent arithmetic", Decimal(expected), actual)
        compare(benchmarks, name + ": printed reference", Decimal(printed[name]), actual)
    all_checks.extend(benchmarks)
    failures = [check for check in all_checks if not check["passed"]]
    maxima = {}
    for mission, prefix in (("BIRDS-4", "birds_"), ("OreSat", "oresat_")):
        subset = [check for check in all_checks if check.get("mission") == mission or check["check"].startswith(prefix)]
        maxima[mission] = str(max(Decimal(check["relative_error"]) for check in subset if check["relative_error"] is not None))
    catalogue_inspection = {
        "mop": "MOP-10", "scope": "generic CSRM EPS hardware types",
        "minimum_per_type": 5, "distinct_products": len(catalog),
        "types": {cls.__name__: {
            "count": len({(product.manufacturer, product.part_number) for product in catalog.products.values()
                          if issubclass(product.model_class, cls)}),
            "products": [{"product_id": product.product_id, "part_number": product.part_number,
                          "datasheet_url": product.datasheet_url} for product in catalog.products.values()
                         if issubclass(product.model_class, cls)],
        } for cls in EPS.default_components if not issubclass(cls, Software)},
        "all_products_have_datasheet_links": all(product.datasheet_url for product in catalog.products.values()),
    }
    catalogue_inspection["verified"] = (catalogue_inspection["all_products_have_datasheet_links"] and
        all(group["count"] >= 5 for group in catalogue_inspection["types"].values()))
    summary = {
        "mop": "MOP-11", "queries": len(queries), "checks": len(all_checks), "failed_checks": len(failures),
        "catalogue_products": len(catalog), "compatible_products": {
            role: len({candidate.product_id for candidate in catalog.candidates(make_case(key, "baseline")[1])})
            for role, key in (("Battery", "birds_battery"), ("SolarArray", "birds_solar"))},
        "maximum_relative_error": maxima,
        "baseline_inclusions": {row["case"]: row["included"] for row in queries if row["scenario"] == "baseline"},
        "strict_verdicts": {row["case"]: row["verified"] for row in queries if row["scenario"] == "strict"},
        "missing_statuses": {row["case"]: row["status"] for row in queries if row["scenario"] == "missing"},
        "radiation_verdicts": {row["case"]: row["verified"] for row in queries if row["scenario"] == "radiation"},
        "framework_revision": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "framework_sha256": hashes, "python": sys.version,
        "driver_sha256": {path.name: digest(path) for path in (Path(__file__), HERE / "independent_cots_reference.py")},
        "sources": sources,
        "scope": ["Purchased cell or single-cell SCA screening only; no installation or full mission qualification.",
                  "Four 2019 OreSat 2S packs are evaluated with later Tenergy cells; solar replacement uses two two-cell modules.",
                  "No branch current sharing, thermal history, age retention or guaranteed minimum solar performance is inferred.",
                  "Independent references use original PDF facts, not catalogue tables or framework numerical functions."]}
    output.mkdir(parents=True, exist_ok=True)
    for filename, value in (("mop11-results.json", queries), ("mop11-summary.json", summary),
                            ("mop11-budget-checks.json", benchmarks),
                            ("mop11-inputs.json", {"parts": ref.PARTS, "birds": ref.BIRDS, "oresat": ref.ORESAT}),
                            ("mop10-catalogue-inspection.json", catalogue_inspection)):
        (output / filename).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({key: summary[key] for key in ("queries", "checks", "failed_checks", "baseline_inclusions",
                      "strict_verdicts", "missing_statuses", "radiation_verdicts", "maximum_relative_error")}, indent=2))
    for failure in failures:
        print("MISMATCH", canonical(failure))
    return not failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE)
    raise SystemExit(0 if run(parser.parse_args().output) else 1)
