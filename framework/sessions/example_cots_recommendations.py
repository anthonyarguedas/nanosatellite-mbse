"""Read-only battery recommendations from explicitly selected catalog facts.

Run: python3 -m framework.sessions.example_cots_recommendations
GUI: MISSION_FILE=framework/sessions/example_cots_recommendations.py npm start --prefix framework/gui

Each candidate is one purchased cell. Energy uses the published minimum.
Mass uses the published maximum. Nominal voltage is a reference rating.
The P26A has typical energy only, so its minimum energy remains pending.
These three product screens establish no lifetime, thermal or flight claim.
"""

import csv
from pathlib import Path

from framework.models import CotsBattery, CubeSatBus, Mission, Property, VerificationCondition

CATALOG = Path(__file__).resolve().parents[1] / "cots"
with (CATALOG / "model-inputs.tsv").open(newline="") as stream:
    _inputs = list(csv.DictReader(stream, delimiter="\t"))
with (CATALOG / "parameters.tsv").open(newline="") as stream:
    _parameters = list(csv.DictReader(stream, delimiter="\t"))


def fact(product, parameter, kind):
    rows, field = (_parameters, "parameter_name") if parameter == "mass" else (_inputs, "model_property")
    matches = [row for row in rows if row["product_id"] == product and row["element_id"] == "self"
               and row[field] == parameter and row["value_kind"] == kind
               and row["condition_id"] == "" and row["value"]]
    if len(matches) != 1:
        raise ValueError(f"Choose one {kind} fact for {product}.{parameter}.")
    row = matches[0]
    return Property(float(row["value"]), row["unit"])


class MolicelM30A(CotsBattery):
    mass = fact("molicel_inr_18650_m30a", "mass", "maximum")
    rated_energy = fact("molicel_inr_18650_m30a", "rated_energy", "minimum")
    nominal_voltage = fact("molicel_inr_18650_m30a", "nominal_voltage", "nominal")


class MolicelM35A(CotsBattery):
    mass = fact("molicel_inr_18650_m35a", "mass", "maximum")
    rated_energy = fact("molicel_inr_18650_m35a", "rated_energy", "minimum")
    nominal_voltage = fact("molicel_inr_18650_m35a", "nominal_voltage", "nominal")


class MolicelP42A(CotsBattery):
    mass = fact("molicel_inr_21700_p42a", "mass", "maximum")
    rated_energy = fact("molicel_inr_21700_p42a", "rated_energy", "minimum")
    nominal_voltage = fact("molicel_inr_21700_p42a", "nominal_voltage", "nominal")


class MolicelP45B(CotsBattery):
    mass = fact("molicel_inr_21700_p45b", "mass", "maximum")
    rated_energy = fact("molicel_inr_21700_p45b", "rated_energy", "minimum")
    nominal_voltage = fact("molicel_inr_21700_p45b", "nominal_voltage", "nominal")


class MolicelP26A(CotsBattery):
    mass = fact("molicel_inr_18650_p26a", "mass", "maximum")
    rated_energy = Property(unit="Wh")  # No published minimum energy.
    nominal_voltage = fact("molicel_inr_18650_p26a", "nominal_voltage", "nominal")


# Detached alternatives are ordinary Python objects, separate from installation.
cots_catalog = (MolicelM30A("M30A"), MolicelM35A("M35A"), MolicelP42A("P42A"),
                MolicelP45B("P45B"), MolicelP26A("P26A"))
mission = Mission()
bus = mission.add(CubeSatBus("BUS", units=1))
battery = bus.EPS.Battery
for name, prop, target, predicate, statement in (
    ("energy", battery.rated_energy, Property(11, "Wh"), "measure >= target",
     "The purchased cell shall provide at least {check.target} of rated energy."),
    ("mass", battery.mass, Property(0.075, "kg"), "measure <= target",
     "The purchased cell shall have a mass of at most {check.target}."),
    ("voltage", battery.nominal_voltage, Property(3.6, "V"), "measure == target",
     "The purchased cell shall have a nominal voltage of {check.target}."),
):
    battery.add_requirement(
        f"{name}_screen", statement=statement,
        rationale="Explicit preliminary allocation for a purchased cell. Ratings retain their source meanings.",
        conditions=(VerificationCondition("check", prop, target, predicate),),
    )


if __name__ == "__main__":
    for match in battery.recommend_cots(cots_catalog, sort_by="rated_energy", reverse=True, limit=3):
        print(f"{match.candidate.name}: {match.sort_value:g} Wh, {len(match.report.results)} passing checks")
    print("The live battery remains unassigned:", not battery.cots)
