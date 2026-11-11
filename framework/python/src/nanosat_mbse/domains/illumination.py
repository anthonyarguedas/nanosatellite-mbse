"""Reconcile reviewed illumination defaults without replacing authored bindings."""

from dataclasses import replace

from ..catalogs._illumination import LEGACY_DEFAULTS
from ..catalogs.definitions import PYTHON_TYPES
from ..core.requirements import Parameter


def reconcile_illumination_defaults(session):
    """Upgrade existing generic rows only. Import and deleted rows stay intact."""
    for row in session.requirements:
        legacy = LEGACY_DEFAULTS.get(row.definition)
        template = session.catalog.by_requirement.get(row.definition)
        if legacy is None or template is None:
            continue
        specs = {parameter.name: parameter for parameter in template.parameters}
        beta = specs.get("beta_deg")
        if beta is not None and "beta_deg" not in row.parameters:
            row.add_parameter(
                Parameter(
                    "beta_deg",
                    PYTHON_TYPES[beta.kind],
                    beta.unit or "",
                    expression=beta.expression,
                )
            )
        for name, old_expression in legacy["parameters"].items():
            parameter = row.parameters.get(name)
            if (
                parameter is not None
                and parameter.expression == old_expression
                and name in specs
            ):
                row.set_expression(name, specs[name].expression)
        methods = tuple(
            replace(method, condition=template.condition)
            if method.key == "condition"
            and method.source is None
            and method.condition in legacy["conditions"]
            else method
            for method in row.verifications
        )
        if methods != row.verifications:
            row.verifications = methods
        if row.text == legacy.get("text"):
            row.text = template.text
        if hasattr(row, "template"):
            row.template = template
    return session
