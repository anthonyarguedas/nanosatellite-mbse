"""Exact bounded monotone fault-tree RAM: four basic events, 1..4 OR-of-AND terms.

Events have bit masks 1,2,4,8. Each authored nonzero term mask denotes AND of
its events; TOP is the OR of authored terms. Duplicate/superset terms are removed
to form sorted minimal cuts. All 16 joint states are enumerated, NOT a sum of
cut probabilities (cuts can overlap). P(state)=product(p_i if failed else 1-p_i).
Cut occurrence probability=product(p_i for events in cut), without exclusion of
other failures. P(TOP|evidence)=P(TOP AND evidence)/P(evidence), null if evidence
has zero probability. Per-event conditional results are null on zero-probability
conditioning. Birnbaum importance B_i=P(TOP|do(X_i=1))-P(TOP|do(X_i=0)) is
computed by exact pivotal-state enumeration, including p_i=0 or 1 boundaries.
Criticality importance=p_i*B_i/P(TOP), null when P(TOP)=0; this is NOT severity.

value_kind=0 uses supplied exposure-specific probabilities; =1 uses supplied
nonrepairable CONSTANT rates per hour: p_i=-expm1(-lambda_i*exposure_h).
Mutual independence and resolved common-cause treatment MUST be explicitly
confirmed. A common-cause event can be one of the four supplied independent
basic events only if residual event definitions preserve independence. Arbitrary
correlations, repairs, sequence dependence, dynamic trees, automatic dependency
inference and full FMEA are unsupported. Rates, severities and safety criteria
are never invented. Engineer MUST identify event/component meanings, sources,
exposure, dependencies and top-effect semantics in the requirement rationale.
Stderr logs the generated indexed representation for that authored mapping.
"""
import json
import math
import sys

INPUTS = """value_kind exposure_h independence_confirmed common_cause_resolved
term_count term1 term2 term3 term4 event1_value event2_value event3_value
event4_value conditional_failed_mask conditional_healthy_mask""".split()
INTEGER_INPUTS = {"value_kind", "term_count", "term1", "term2", "term3", "term4", "conditional_failed_mask", "conditional_healthy_mask"}
BOOLEAN_INPUTS = {"independence_confirmed", "common_cause_resolved"}


def calculate(p):
    if not isinstance(p, dict) or set(p) != set(INPUTS):
        raise ValueError("Supply exactly the declared inputs.")
    for name, value in p.items():
        if name in BOOLEAN_INPUTS:
            if type(value) is not bool:
                raise ValueError(f"{name} must be boolean.")
        elif name in INTEGER_INPUTS:
            if type(value) is not int or abs(value) > 9007199254740991:
                raise ValueError(f"{name} must be a safe integer.")
        elif type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")
    if not p["independence_confirmed"] or not p["common_cause_resolved"]:
        raise ValueError("Unsupported dependence: confirm mutual independence and explicit common-cause treatment.")
    if p["value_kind"] not in (0, 1) or p["exposure_h"] < 0:
        raise ValueError("Use value_kind 0=probability or 1=constant rate/h and nonnegative exposure_h.")
    count = p["term_count"]
    if not 1 <= count <= 4:
        raise ValueError("term_count work bound is 1 through 4; an empty tree is not allowed.")
    terms = [p["term" + str(i)] for i in range(1, 5)]
    if any(not 1 <= t <= 15 for t in terms[:count]) or any(t != 0 for t in terms[count:]):
        raise ValueError("Active term masks must be 1..15; unused term masks must be zero.")
    failed, healthy = p["conditional_failed_mask"], p["conditional_healthy_mask"]
    if not (0 <= failed <= 15 and 0 <= healthy <= 15) or failed & healthy:
        raise ValueError("Conditional masks must be 0..15 and disjoint.")
    values = [p["event" + str(i) + "_value"] for i in range(1, 5)]
    if any(v < 0 or (p["value_kind"] == 0 and v > 1) for v in values):
        raise ValueError("Supply probabilities in [0,1] or nonnegative failure rates/h.")
    probabilities = values if p["value_kind"] == 0 else [-math.expm1(-v * p["exposure_h"]) for v in values]
    unique = sorted(set(terms[:count]))
    cuts = [t for t in unique if not any(s != t and s & t == s for s in unique)]

    def top(state):
        return any(state & cut == cut for cut in cuts)

    def weight(state, omit=None):
        result = 1.0
        for i, probability in enumerate(probabilities):
            if i != omit:
                result *= probability if state & (1 << i) else 1 - probability
        return result

    states = [(state, weight(state), top(state)) for state in range(16)]
    q = math.fsum(w for state, w, is_top in states if is_top)
    reliability = math.fsum(w for state, w, is_top in states if not is_top)
    evidence = [(w, is_top) for state, w, is_top in states if state & failed == failed and state & healthy == 0]
    evidence_p = math.fsum(w for w, is_top in evidence)
    conditional = math.fsum(w for w, is_top in evidence if is_top) / evidence_p if evidence_p > 0 else None
    result = {"top_failure_probability": q, "mission_reliability": reliability,
              "conditional_failure_probability": conditional, "evidence_probability": evidence_p,
              "minimal_cut_count": len(cuts), "states_enumerated": 16}
    for j in range(4):
        cut = cuts[j] if j < len(cuts) else None
        cut_p = None
        if cut is not None:
            cut_p = math.prod(probabilities[i] for i in range(4) if cut & (1 << i))
        result["cut" + str(j + 1) + "_mask"] = cut
        result["cut" + str(j + 1) + "_probability"] = cut_p
        bit = 1 << j
        other_states = [s for s in range(16) if not s & bit]
        forced_failed = math.fsum(weight(s, j) for s in other_states if top(s | bit))
        forced_healthy = math.fsum(weight(s, j) for s in other_states if top(s))
        birnbaum = math.fsum(weight(s, j) for s in other_states if top(s | bit) and not top(s))
        result["top_given_event" + str(j + 1)] = forced_failed if probabilities[j] > 0 else None
        result["top_given_no_event" + str(j + 1)] = forced_healthy if probabilities[j] < 1 else None
        result["birnbaum" + str(j + 1)] = birnbaum
        result["criticality" + str(j + 1)] = probabilities[j] * birnbaum / q if q > 0 else None
    expression = " OR ".join("(" + " AND ".join("event" + str(i + 1) for i in range(4) if t & (1 << i)) + ")" for t in cuts)
    print(f"TOP = {expression}; authored_terms={terms[:count]}; minimal_cuts={cuts}; p={probabilities}; exposure_h={p['exposure_h']}; independent=True; common_cause_resolved=True; semantics/sources: engineer requirement rationale", file=sys.stderr)
    return result


def main():
    try:
        request = json.load(sys.stdin)
        encoded = json.dumps(calculate(request["inputs"]), allow_nan=False)
    except (ValueError, KeyError, TypeError, OverflowError, ZeroDivisionError) as exc:
        print(f"eps_ram: {exc}", file=sys.stderr)
        return 1
    print(encoded)
    return 0


if __name__ == "__main__":
    sys.exit(main())
