"""Declared rules for method eligibility and the next engineering activity.

This consumes an engineer's structured objective and input inventory. It does
not parse prose, establish input credibility or approve an engineering decision.
The bit/code tables are maintained in analyses/REPORT-COVERAGE.md.
"""

import sys

from ..core.verification import (
    ScriptDefinition,
    ScriptPort,
    VerificationScript,
    cli_main,
)


def analyze(p):
    counts = (
        "goal_code",
        "activity_code",
        "component_count",
        "operating_case_count",
        "valid_sample_count",
        "failure_mode_count",
        "failure_dependency_count",
        "basic_event_count",
        "cut_term_count",
    )
    for name in counts:
        value = p[name]
        if type(value) is not int or value < 0 or value > 1000000:
            raise ValueError(name + " must be an integer from 0 through 1000000.")
    if p["goal_code"] not in range(1, 8) or p["activity_code"] not in range(5):
        raise ValueError("Choose goal_code 1..7 and activity_code 0..4.")
    for name in set(p) - set(counts):
        if type(p[name]) is not bool:
            raise ValueError(name + " must be Boolean.")
    missing = []

    def need(condition, bit, reason):
        if not condition:
            missing.append((bit, reason))

    goal = p["goal_code"]
    need(p["operating_case_count"] > 0, 1, "Define at least one applicable case.")
    need(
        p["has_reference_limits"], 2, "Supply independently assigned acceptance limits."
    )
    if goal in (1, 2, 3, 7):
        need(
            p["has_model_parameters"],
            4,
            "Supply compatible model and product parameters.",
        )
    if goal == 1:
        need(p["has_schedule"], 8, "Supply a chronological source/load schedule.")
        need(
            p["has_retained_capacities"],
            16,
            "Supply distinct retained energy and charge capacities.",
        )
    if goal == 4:
        need(
            3 <= p["valid_sample_count"] <= 5,
            32,
            "Select three through five valid samples, then check excitation in the fit.",
        )
    if goal == 5:
        need(
            p["component_count"] > 0 and p["failure_mode_count"] > 0,
            64,
            "Identify components and failure modes.",
        )
        need(
            p["has_failure_logic"],
            128,
            "Supply authored failure effects and top-event logic.",
        )
        need(
            p["has_failure_probabilities"],
            256,
            "Supply applicable event probabilities for quantitative RAM.",
        )
        need(
            1 <= p["basic_event_count"] <= 4 and 1 <= p["cut_term_count"] <= 4,
            512,
            "The registered fault-tree model supports 1..4 basic events and 1..4 cut terms.",
        )
    if goal == 6:
        need(
            p["has_geometry"],
            1024,
            "Supply installation, component and keep-out envelopes in one frame.",
        )
    identified = p["component_count"] > 0 and p["failure_mode_count"] > 0
    fmea = identified and p["has_failure_effects"]
    fault_tree = identified and p["has_failure_logic"]
    propagation = identified and p["failure_dependency_count"] > 0
    executable = not missing
    if not executable:
        next_activity = 0 if p["operating_case_count"] == 0 else 1
    elif not p["results_available"] or not p["results_current"]:
        next_activity = 2
    elif p["activity_code"] < 3:
        next_activity = 3
    elif p["validation_required"]:
        next_activity = 4 if p["has_independent_reference"] else 1
    else:
        next_activity = 5
    names = {
        1: "eps_energy_segment",
        2: "eps_power_path",
        3: "eps_thermal",
        4: "eps_fit",
        5: "eps_ram",
        6: "eps_geometry",
        7: "eps_sizing",
    }
    print("Proposed method: " + names[goal], file=sys.stderr)
    for bit, reason in missing:
        print("Missing prerequisite " + str(bit) + ": " + reason, file=sys.stderr)
    if p["validation_required"] and not p["has_independent_reference"]:
        print(
            "Validation also requires independent reference data and an approved comparison protocol.",
            file=sys.stderr,
        )
    return dict(
        method_code=goal,
        unmet_prerequisite_mask=sum(bit for bit, _ in missing),
        unmet_prerequisite_count=len(missing),
        executable=executable,
        recommended_activity_code=next_activity,
        repeat_analysis=executable
        and p["results_available"]
        and not p["results_current"],
        independent_validation_recommended=p["validation_required"],
        independent_validation_ready=executable
        and p["validation_required"]
        and p["has_independent_reference"]
        and p["results_available"]
        and p["results_current"],
        fmea_eligible=fmea,
        fmeca_eligible=fmea and p["has_failure_probabilities"],
        fault_tree_eligible=fault_tree,
        quantitative_fault_tree_eligible=fault_tree and p["has_failure_probabilities"],
        failure_propagation_eligible=propagation,
    )


class Guidance(VerificationScript):
    definition_spec = ScriptDefinition(
        id="eps_guidance",
        name="EPS method and activity eligibility",
        description="Proposes a registered model, RAM methods and the next activity from an engineer-supplied structured objective and input inventory. Returns explicit unmet-prerequisite bits and repeat-analysis advice. Does not parse requirement prose, infer data quality, generate full FMEA records or approve decisions. Codes and rules are documented in analyses/REPORT-COVERAGE.md.",
        inputs=(
            ScriptPort("goal_code", int, None),
            ScriptPort("activity_code", int, None),
            ScriptPort("component_count", int, None),
            ScriptPort("operating_case_count", int, None),
            ScriptPort("valid_sample_count", int, None),
            ScriptPort("failure_mode_count", int, None),
            ScriptPort("failure_dependency_count", int, None),
            ScriptPort("basic_event_count", int, None),
            ScriptPort("cut_term_count", int, None),
            ScriptPort("has_reference_limits", bool, None),
            ScriptPort("has_model_parameters", bool, None),
            ScriptPort("has_schedule", bool, None),
            ScriptPort("has_retained_capacities", bool, None),
            ScriptPort("has_geometry", bool, None),
            ScriptPort("has_failure_logic", bool, None),
            ScriptPort("has_failure_effects", bool, None),
            ScriptPort("has_failure_probabilities", bool, None),
            ScriptPort("has_independent_reference", bool, None),
            ScriptPort("results_available", bool, None),
            ScriptPort("results_current", bool, None),
            ScriptPort("validation_required", bool, None),
        ),
        outputs=(
            ScriptPort("method_code", int, None),
            ScriptPort("unmet_prerequisite_mask", int, None),
            ScriptPort("unmet_prerequisite_count", int, None),
            ScriptPort("executable", bool, None),
            ScriptPort("recommended_activity_code", int, None),
            ScriptPort("repeat_analysis", bool, None),
            ScriptPort("independent_validation_recommended", bool, None),
            ScriptPort("independent_validation_ready", bool, None),
            ScriptPort("fmea_eligible", bool, None),
            ScriptPort("fmeca_eligible", bool, None),
            ScriptPort("fault_tree_eligible", bool, None),
            ScriptPort("quantitative_fault_tree_eligible", bool, None),
            ScriptPort("failure_propagation_eligible", bool, None),
        ),
        timeout_ms=3000,
    )

    def calculate(self, inputs, *, requirements=None, mode=None):
        return analyze(inputs)


if __name__ == "__main__":
    sys.exit(cli_main(Guidance))
