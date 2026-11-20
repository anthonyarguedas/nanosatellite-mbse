"""MOP-11 references transcribed from original PDFs, without framework imports.

Mission demands come from the cited budgets. Part ratings come from the original
manufacturer sheets, not from framework/cots. All decimal inputs remain strings.
See source-evidence.json for original documents, page numbers and source crops.
"""

from decimal import Decimal, localcontext


SOURCES = {
    "birds_budget": {
        "path": ".web-content/mop-academic/birds-budget-published.pdf",
        "url": "https://birds-project.com/open-source/pdf/Power-Budget-Analysis-for-1U-satellit20220514.pdf",
        "citation": "shrestha2022birds4powerbudget",
        "pages": [4, 5, 8, 9],
        "sha256": "462af3caa918f36b5fdcc0c00d77be7ffa585de09d3d1de25d05476612496b6d",
    },
    "oresat_budget": {
        "path": ".web-content/oresat/oresat-power-budget-2019-09-30.pdf",
        "url": "https://raw.githubusercontent.com/oresat/oresat.github.io/0d879a503be4a6d48e849f3088524c2748503640/pub/OreSat_Power_Budget_190930.pdf",
        "citation": "oresat2019powerbudget",
        "pages": [1, 2],
        "sha256": "da72cfa2f0ea565cf40604759a1bd3fb9c82dee7b1f877294774c9922fef4645",
    },
    "oresat_account": {
        "path": ".web-content/mop-academic/oresat-2021.pdf",
        "url": "https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=5110&context=smallsat",
        "citation": "greenberg2021oresat",
        "pages": [5, 6],
        "sha256": "09c258644bceb14873a2362f8010c2fb8bf09eb43aecda7d12e5ef07a9f0802c",
    },
    "panasonic": {
        "path": ".web-content/case-study-verification/panasonic-bk3mcc.pdf",
        "url": "https://www.optimusdigital.ro/ro/index.php?controller=attachment&id_attachment=3561",
        "citation": "cots-mission_panasonic_bk_3mcc_legacy_ds",
        "pages": [1],
        "sha256": "d5a2e1c898c6cd4818de95e468e38fc9a38cea0f4cb28ab385d8a895adf1c73c",
    },
    "tenergy": {
        "path": ".web-content/case-study-verification/tenergy-30005.pdf",
        "url": "https://files.batteryjunction.com/frontend/files/tenergy/datasheet/TENERGY-30005-18650-FLAT-Datasheet.pdf",
        "citation": "cots-mission_tenergy_30005_0_ds",
        "pages": [1, 2, 3, 4],
        "sha256": "add65c3a66acc2f29fedf350236c4062423326cab03c8aad50f44ee5a575ae2e",
    },
    "azur": {
        "path": ".web-content/case-study-verification/azur-3g30a.pdf",
        "url": "https://d35rpq4gusjz9h.cloudfront.net/files/73192/download/634236/73192_19_2023090605471491796.pdf",
        "citation": "cots-mission_azur_space_3g30a_review_legacy_ds",
        "pages": [1, 2],
        "sha256": "0f07d638ab7bf4f50bfc3deaa087dabd3caa520fe5ac0c536b4df06430d29a02",
    },
    "spectrolab": {
        "path": ".web-content/case-study-verification/spectrolab-xtesf.pdf",
        "url": "https://www.spectrolab.com/photovoltaics/XTE-SF%20Data%20Sheet%20_07.27.22.pdf",
        "citation": "cots-solar_src_spectro_xtesf",
        "pages": [1, 2],
        "sha256": "41e049ab29d95c1376a4f328a2ea5eef29477760bc57006cb5de8ff854ad7ad3",
    },
    "birds_cells": {
        "path": ".web-content/case-study-verification/birds-battery-report.pdf",
        "url": "https://raw.githubusercontent.com/BIRDSOpenSource/BIRDS4-ProceduresAndReports/d7eadd98f5327e1ddea82b640293d49bfdb09555/Battery%28Cells%29%20Screening%20Procedures%20and%20its%20verification%20Report_V1.0%20%282%29.pdf",
        "citation": "birds2021batteryverification",
        "pages": [21],
        "sha256": "bcac3915416ce82745bda87a78aa26360a2303c61f141f0e2484072990e50c55",
    },
    "oresat_mass": {
        "path": ".web-content/case-study-verification/oresat-2016-csli.pdf",
        "url": "https://raw.githubusercontent.com/oresat/oresat.github.io/0d879a503be4a6d48e849f3088524c2748503640/pub/OreSat_CSLI_Application-2016.pdf",
        "citation": "oresat2016csli",
        "pages": [21, 22],
        "sha256": "22451401684fbe3d950506b7e3d19206e8098902714c56e8ef9fe25df794b4c0",
    },
    "birds_safety": {
        "path": ".web-content/mop-academic/birds-safety-2021.pdf",
        "url": "https://iafastro.directory/iac/paper/id/62691/summary/",
        "citation": "shrestha2021birdssafety",
        "pages": [6, 7],
        "sha256": "05c5dd683be393c0469e0857dd4bbd1021d22771bae307a65c58c76ed194fa85",
    },
}

# Original page 9 nominal-mode ON cells: 642+144+140+282+120+110 mWh.
BIRDS = {
    "load": "1.438", "period": "90", "eclipse": "35", "diode": "0.240",
    "conversion": "0.80", "generation": "2.173", "after_bcr_printed": "1.546",
    "battery_cells": "6", "budget_voltage": "1.2", "solar_cells": "10",
    # Authored conservative storage allocation: full orbit demand, 20% DoD,
    # 90% delivery. Uniform orientation projection 1/4 is a separate assumption.
    "dod": "0.20", "delivery": "0.90", "projection": "0.25",
}
ORESAT = {
    "standby": "0.623", "live": "2.318", "passes": "24.6", "period": "90",
    "sunlight_fraction": "0.59", "projection": "0.71", "generation_power": "2.600",
    "generation_printed": "1.634", "balance_printed": "1.011",
    "battery_cells": "8", "budget_voltage": "3.6", "dod": "0.60",
    # Four independent 2S packs follow the 2019 budget. Two illuminated modules
    # are replaced by two 2021-type two-cell modules (four purchased solar cells).
    # Unity delivery/conversion adds no unreported loss to the budget boundary.
    "delivery": "1", "conversion": "1", "diode": "0", "solar_cells": "4",
}

PARTS = {
    "birds_battery": {
        "mission": "BIRDS-4", "role": "Battery", "product_id": "panasonic_bk_3mcc",
        "condition": "mission_panasonic_bk_3mcc_capacity_25c_0p4a",
        "rating": "1.9", "voltage": "1.2", "voltage_interval": ["1.2", "1.2"],
        "unit": "Ah", "property": "rated_capacity", "source": "panasonic",
        "source_locator": "p.1, minimum capacity; 25 C, 0.4 A discharge to 1 V after 0.2 A x 16 h charge",
        "rating_meaning": "minimum charge capacity, not a measured Wh guarantee",
    },
    "oresat_battery": {
        "mission": "OreSat", "role": "Battery", "product_id": "tenergy_30005_0",
        "condition": "mission_tenergy_30005_0_capacity_0p2c_25c",
        "rating": "2.5", "voltage": "3.65", "voltage_interval": ["3.5", "3.7"],
        "unit": "Ah", "property": "rated_capacity", "source": "tenergy",
        "source_locator": "p.2, minimum capacity and average working voltage; 25 C, 0.2C discharge to 2.75 V",
        "rating_meaning": "minimum 2.5 Ah, distinct from nominal 2.6 Ah; 3.65 V sheet convention, 3.6 V budget convention",
    },
    "birds_solar": {
        "mission": "BIRDS-4", "role": "SolarArray", "product_id": "azur_space_3g30a",
        "condition": "mission_azur_space_3g30a_review_bol_am0_g1367_t301p15",
        "vmp": "2.409", "imp": "0.5029", "unit": "W", "property": "maximum_power",
        "source": "azur", "source_locator": "p.2, Electrical Data (SCA), BOL; AM0 WRC 1367 W/m2, 28 C",
        "radiation_condition": "mission_azur_space_3g30a_review_eol_1e15cm2_am0_g1367_t301p15",
        "radiation_vmp": "2.244", "radiation_imp": "0.4851",
        "rating_meaning": "derived Vmp x Imp from typical terminal ratings, one single-cell SCA",
    },
    "oresat_solar": {
        "mission": "OreSat", "role": "SolarArray", "product_id": "spectrolab_xte_sf_27cm2",
        "condition": "solar_bol_am0_t301p15_g1353",
        "vmp": "2.435", "jmp_mA_cm2": "17.9", "area_cm2": "27", "unit": "W",
        "property": "maximum_power", "source": "spectrolab",
        "source_locator": "p.1, BOL column and 27 cm2 footnote; AM0 1353 W/m2, 28 C",
        "radiation_condition": "solar_eol_am0_e1mev_f1e15cm2_aiaa_s111_2005_t301p15_g1353",
        "radiation_v_fraction": "0.86", "radiation_i_fraction": "0.98",
        "rating_meaning": "derived Vmp x Jmp x area from typical ratings, one physical cell",
    },
}


def decimal(value):
    return Decimal(str(value))


def inputs(key, scenario):
    """Return the declared mission allocation, retaining its hardware boundary."""
    part = PARTS[key]
    if part["mission"] == "BIRDS-4":
        values = dict(BIRDS)
        values["load"] = str(decimal(BIRDS["load"]) * (2 if scenario == "strict" else 1))
    else:
        values = dict(ORESAT)
        if scenario == "strict" and part["role"] == "Battery":
            # Reproduce the published 24.6-pass storage reserve, not a new
            # claim that the 2021 Tenergy cells were the 2019 3300 mAh packs.
            values["load"] = str(decimal(ORESAT["live"]) * decimal(ORESAT["passes"]))
        else:
            values["load"] = str(decimal(ORESAT["standby"]) + decimal(ORESAT["live"]) *
                                 (2 if scenario == "strict" else 1))
    return values


def reference(key, scenario):
    """Separate decimal capacity/power calculations and explicit truth values."""
    with localcontext() as context:
        context.prec = 50
        part = PARTS[key]
        values = {k: decimal(v) for k, v in inputs(key, scenario).items()}
        if part["role"] == "Battery":
            target = values["load"] / (values["battery_cells"] * values["budget_voltage"] *
                                       values["dod"] * values["delivery"])
            rating = decimal(part["rating"])
        else:
            hours = ((values["period"] - values["eclipse"]) / 60 if "eclipse" in values
                     else values["period"] / 60 * values["sunlight_fraction"])
            target = (values["load"] / values["conversion"] + values["diode"]) / (
                values["solar_cells"] * values["projection"] * hours)
            current = (decimal(part["imp"]) if "imp" in part else
                       decimal(part["jmp_mA_cm2"]) * decimal(part["area_cm2"]) / 1000)
            voltage = decimal(part["vmp"])
            if scenario == "radiation":
                voltage = (decimal(part["radiation_vmp"]) if "radiation_vmp" in part else
                           voltage * decimal(part["radiation_v_fraction"]))
                current = (decimal(part["radiation_imp"]) if "radiation_imp" in part else
                           current * decimal(part["radiation_i_fraction"]))
            rating = voltage * current
        return {"target": str(target), "rating": str(rating),
                "verified": None if scenario == "missing" else rating >= target,
                "status": "pending" if scenario == "missing" else "value"}


def published_references():
    """Printed budget values are external benchmarks, separate from exact maths."""
    with localcontext() as context:
        context.prec = 50
        birds = {k: decimal(v) for k, v in BIRDS.items()}
        oresat = {k: decimal(v) for k, v in ORESAT.items()}
        generated = oresat["generation_power"] * oresat["sunlight_fraction"] * oresat["projection"] * oresat["period"] / 60
        return {
            "birds_after_bcr": str((birds["generation"] - birds["diode"]) * birds["conversion"]),
            "oresat_generation": str(generated),
            "oresat_balance": str(oresat["generation_printed"] - oresat["standby"]),
        }
