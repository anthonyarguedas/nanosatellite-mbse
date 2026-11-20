"""Read-only COTS queries against a component's owned requirements."""

from copy import deepcopy
from dataclasses import dataclass
import math
from numbers import Real

from .elements import Component
from .eps import EPS
from .properties import EvaluationStatus
from .requirements import VerificationReport


@dataclass(frozen=True)
class CotsRecommendation:
    candidate: Component
    report: VerificationReport
    sort_value: object = None


def recommend_cots(component, candidates=None, *, sort_by=None, reverse=False, limit=None, mode=None,
                   condition_id="", element_id=None, value_kinds=None):
    """Query the built-in catalog in an isolated Mission.

    Explicit alternatives can override automatic catalog discovery.
    Candidates are detached, fixed Component instances. Only the generic
    component's direct requirements are checked. Every owned requirement must
    have conditions and pass. With no requirements, the query is unconstrained.
    Property expressions use the generic component as self. Existing COTS
    selections are omitted. No installation or assembly search is performed.
    Sorting requires a finite real Property value and preserves ties in input
    order. Return the original candidates alongside their trial reports.
    """
    if not isinstance(component, Component) or component.fixed_properties:
        raise TypeError("Choose a generic Component.")
    mission = component.mission
    if mission is None:
        raise ValueError("Attach the component to a Mission before querying COTS.")
    if mode is not None and getattr(mode, "mission", None) is not mission:
        raise ValueError("The evaluation mode must belong to this Mission.")
    if limit is not None and (type(limit) is not int or limit < 0):
        raise ValueError("The recommendation limit must be a nonnegative integer or None.")
    if candidates is None:
        from framework.cots import load_catalog

        candidates = load_catalog().candidates(component, condition_id=condition_id,
                                               element_id=element_id, value_kinds=value_kinds)
    elif condition_id or element_id is not None or value_kinds:
        raise ValueError("Catalog selectors apply to automatically discovered candidates.")
    candidates = tuple(dict.fromkeys(candidates))
    if any(not isinstance(item, Component) or not item.fixed_properties for item in candidates):
        raise TypeError("Supply fixed COTS Component instances.")
    if any(item.parent is not None for item in candidates):
        raise ValueError("Supply detached COTS candidates.")
    if sort_by is not None and (not isinstance(sort_by, str) or not any(
        sort_by in item.properties for item in (component, *candidates)
    )):
        raise ValueError(f"Unknown sort Property {sort_by!r}.")

    matches = []
    for candidate in candidates:
        if not component.accepts(candidate):
            continue
        role = getattr(candidate, "catalog_role", None)
        if isinstance(role, type) and any(isinstance(component, cls) for cls in EPS.default_components):
            if any(issubclass(role, cls) and not isinstance(component, cls) for cls in EPS.default_components):
                continue
        memo = {id(imported): imported for imported in mission.imports.values()}
        trial, product = deepcopy((mission, candidate), memo)
        owner, selected_mode = memo[id(component)], memo.get(id(mode))
        for installed in owner.cots:
            owner.remove(installed)
        for name in ("catalog_product", "catalog_role", "catalog_element", "catalog_condition", "catalog_bindings"):
            if hasattr(product, name):
                setattr(owner, name, getattr(product, name))
        for name, prop in product.properties.items():
            definition = prop.copy(None, name)
            if name in owner.properties:
                setattr(owner, name, definition)
            else:
                owner.define(name, definition)
        reports = tuple(requirement.verify(mode=selected_mode) for requirement in owner.requirements)
        if any(report.verified is not True for report in reports):
            continue
        sort_value = None
        if sort_by is not None:
            if sort_by not in product.properties:
                continue
            result = owner.properties[sort_by].assess(mode=selected_mode)
            sort_value = result.value
            if (result.status is not EvaluationStatus.VALUE or isinstance(sort_value, bool)
                    or not isinstance(sort_value, Real)
                    or not (isinstance(sort_value, int) or math.isfinite(sort_value))):
                continue
        report = VerificationReport(trial, tuple(result for entry in reports for result in entry.results))
        matches.append(CotsRecommendation(candidate, report, sort_value))
    if sort_by is not None:
        matches.sort(key=lambda match: match.sort_value, reverse=reverse)
    return tuple(matches[:limit])
