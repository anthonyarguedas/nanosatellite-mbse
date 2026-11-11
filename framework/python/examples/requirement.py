"""Review example for the Requirement API, independent of the UI.

Run from the repository root:
    PYTHONPATH=framework/python/src python3 framework/python/examples/requirement.py

All quantities are illustrative. This example establishes no hardware claim.
"""

from typing import Mapping

from nanosat_mbse import Parameter, Requirement, VerificationMethod


def watt_hours_to_joules(values: Mapping[str, float]) -> float:
    return values["installed_energy_Wh"] * 3600


def positive_energy(values: Mapping[str, float]) -> bool:
    return values["required_energy_J"] > 0 and values["installed_energy_J"] > 0


def sufficient_energy(values: Mapping[str, float]) -> bool:
    return values["installed_energy_J"] >= values["required_energy_J"]


class BatteryEnergyRequirement(Requirement):
    """Reusable defaults and behavior, with independent populated instances."""

    def __init__(self, id: str, **metadata) -> None:
        super().__init__(
            id=id,
            text="The battery shall provide at least $$required_energy_J$$.",
            definition="Example::BatteryEnergy",
            parameters=(
                Parameter("required_energy_J", unit="J"),
                Parameter("installed_energy_Wh", unit="Wh"),
                Parameter(
                    "installed_energy_J", unit="J", expression=watt_hours_to_joules
                ),
            ),
            verifications=(
                VerificationMethod("positive energy", positive_energy),
                VerificationMethod("sufficient energy", sufficient_energy),
            ),
            **metadata,
        )


def build_requirement() -> BatteryEnergyRequirement:
    """Populate the reusable requirement as a future session would."""
    requirement = BatteryEnergyRequirement(
        "EPS008",
        rationale="Illustrate a declared energy need and explicit Wh to J conversion.",
        origin="Requirement API review example",
    )
    requirement.set_value("required_energy_J", 360_000)
    return requirement


def main() -> None:
    requirement = build_requirement()
    print("Missing input:", requirement.verify().state.value)

    requirement.set_value("installed_energy_Wh", 50)
    print("Insufficient energy:", requirement.verify().state.value)

    requirement.set_value("installed_energy_Wh", 100)
    assessment = requirement.verify()
    print("Sufficient energy:", assessment.state.value)
    print("Calculated energy:", requirement.value("installed_energy_J"), "J")
    print("Requirement:", requirement.render_text())
    print(
        "Stored calculation:",
        requirement.parameters["installed_energy_J"].expression.__name__,
    )
    print(
        "Stored calculated value:", requirement.parameters["installed_energy_J"].value
    )

    independent = BatteryEnergyRequirement("EPS009")
    print("Independent instance:", independent.verify().state.value)


if __name__ == "__main__":
    main()
