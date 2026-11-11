"""Reusable EPS requirements instantiated from immutable engineering definitions."""

from ...catalogs.definitions import PYTHON_TYPES
from ...core.requirements import Parameter, Requirement
from ...core.verification import VerificationMethod


class GenericRequirement(Requirement):
    """A populated requirement that retains its reusable engineering definition."""

    def __init__(
        self, template, id=None, *, substitute=lambda source: source, **kwargs
    ):
        self.template = template
        parameters = tuple(
            Parameter(
                parameter.name,
                PYTHON_TYPES[parameter.kind],
                parameter.unit or "",
                expression=None
                if parameter.expression is None
                else substitute(parameter.expression),
            )
            for parameter in template.parameters
            if parameter.exposed
        )
        methods = (
            ()
            if not template.condition
            else (
                VerificationMethod(
                    "condition", substitute(template.condition), key="condition"
                ),
            )
        )
        super().__init__(
            template.id if id is None else id,
            template.text,
            parameters=parameters,
            verifications=methods,
            definition=template.model,
            origin=template.origin,
            rationale=template.origin,
            **kwargs,
        )
        self._verification_style = "condition"
