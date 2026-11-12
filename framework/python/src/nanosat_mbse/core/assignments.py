"""Reusable verification over authoritative component requirement assignments."""

from __future__ import annotations

import math
import operator

from .properties import conversion, resolve_property_type
from .requirements import Requirement
from .predicates import PendingValue


COMPARISONS = {
    "==": operator.eq, "!=": operator.ne,
    "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
}


def assignment_spec(
    requirement, component_type, property_name, comparison, target, *, aggregate=False
):
    """Validate the owned target and generic contract without resolving any values."""
    if not isinstance(requirement, Requirement):
        raise TypeError("Assignment checks belong to a Requirement.")
    cls = resolve_property_type(component_type)
    specification = cls.property_definitions().get(property_name)
    if specification is None:
        raise ValueError(f"{cls.__name__} has no typed property {property_name!r}.")
    if comparison not in COMPARISONS:
        raise ValueError("Use ==, !=, <, <=, > or >= for an assignment comparison.")
    parameter = requirement.parameters.get(target)
    if parameter is None:
        raise ValueError(f"The target {target!r} must be owned by {requirement.id}.")
    numeric = specification.value_type in (float, int)
    if numeric != (parameter.value_type in (float, int)) or (
        not numeric and specification.value_type is not parameter.value_type
    ):
        raise TypeError("The component property and requirement target need compatible types.")
    if not numeric and (aggregate or comparison not in ("==", "!=")):
        raise TypeError("Strings and Booleans support only per-component equality checks.")
    scale, offset = conversion(specification.unit, parameter.unit, aggregate=aggregate)
    return cls, specification, scale, offset


def _components(values, cls, cots_only):
    for component in values.row.assigned_components(cots_only=True):
        if not getattr(component, "type_is_resolved", True):
            raise PendingValue(f"Review the unavailable product type for assigned component {component.id}.")
    return values.row.assigned_components(cls, cots_only=cots_only)


def _check(
    values, component_type, property_name, comparison, target, *, aggregate,
    rel_tol=0, abs_tol=0, cots_only=False,
):
    context = getattr(values, "context", None)
    if context is None:
        raise PendingValue("Attach the requirement to a Session before checking assignments.")
    requirement = values.row
    cls, specification, scale, offset = assignment_spec(
        requirement, component_type, property_name, comparison, target, aggregate=aggregate
    )
    for tolerance in (rel_tol, abs_tol):
        if type(tolerance) not in (int, float) or not math.isfinite(tolerance) or tolerance < 0:
            raise ValueError("Comparison tolerances must be finite nonnegative numbers.")
    if (rel_tol or abs_tol) and (
        comparison not in ("==", "!=") or specification.value_type not in (float, int)
    ):
        raise ValueError("Numeric equality checks support rel_tol and abs_tol.")
    if type(cots_only) is not bool:
        raise TypeError("cots_only must be Boolean.")
    context.engine.budget[0] -= len(context.session.all_elements)
    if context.engine.budget[0] < 0:
        raise ValueError("The calculation exceeded its operation budget.")
    components = _components(values, cls, cots_only)
    if not components:
        raise PendingValue(f"Assign at least one {cls.__name__} to {requirement.id}.")
    expected = values[target]
    actual = []
    # Resolve every selected property before reducing. Missing evidence cannot
    # disappear behind a failed comparison or an empty/zero quantity sum.
    for component in components:
        context.engine.budget[0] -= 1
        if context.engine.budget[0] < 0:
            raise ValueError("The calculation exceeded its operation budget.")
        value = context.component_property(component, property_name)
        if specification.value_type in (float, int):
            value = value * scale + offset
            if not math.isfinite(value):
                raise ValueError("Converted component properties must be finite.")
        actual.append(value * component.quantity if aggregate else value)
    if aggregate:
        total = sum(actual) if all(type(value) is int for value in actual) else math.fsum(actual)
        if not math.isfinite(total):
            raise ValueError("The quantity weighted sum must be finite.")
        actual = [total]

    def compare(value):
        if comparison in ("==", "!=") and specification.value_type in (float, int) and (rel_tol or abs_tol):
            close = math.isclose(value, expected, rel_tol=rel_tol, abs_tol=abs_tol)
            return close if comparison == "==" else not close
        return COMPARISONS[comparison](value, expected)

    return all(compare(value) for value in actual)


def count_assigned(values, component_type, *, cots_only=False, by_quantity=False):
    """Count distinct assigned objects, or their represented quantities."""
    context = getattr(values, "context", None)
    if context is None:
        raise PendingValue("Attach the requirement to a Session before counting assignments.")
    if not isinstance(values.row, Requirement):
        raise TypeError("Assignment counts belong to a Requirement.")
    if type(cots_only) is not bool or type(by_quantity) is not bool:
        raise TypeError("cots_only and by_quantity must be Boolean.")
    cls = resolve_property_type(component_type)
    context.engine.budget[0] -= len(context.session.all_elements)
    if context.engine.budget[0] < 0:
        raise ValueError("The calculation exceeded its operation budget.")
    components = _components(values, cls, cots_only)
    count = sum(component.quantity for component in components) if by_quantity else len(components)
    if count > 9007199254740991:
        raise ValueError("An assignment count must be a safe integer.")
    return count


def all_assigned(values, component_type, property_name, comparison, target, **options):
    """Check every assigned instance, including subclasses of the generic type."""
    return _check(
        values, component_type, property_name, comparison, target,
        aggregate=False, **options,
    )


def sum_assigned(values, component_type, property_name, comparison, target, **options):
    """Compare the quantity weighted property sum in the requirement target's unit."""
    return _check(
        values, component_type, property_name, comparison, target,
        aggregate=True, **options,
    )
