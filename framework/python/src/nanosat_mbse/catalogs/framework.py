"""The reusable framework catalog, independent of browser and worker modules."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterable

from ._data import ELEMENTS, REQUIREMENTS
from .definitions import ElementDefinition, RequirementDefinition


class FrameworkCatalog:
    def __init__(
        self,
        elements: Iterable[ElementDefinition] = ELEMENTS,
        requirements: Iterable[RequirementDefinition] = REQUIREMENTS,
    ):
        self.elements = tuple(elements)
        self.requirements = tuple(requirements)
        self.by_model = {element.model: element for element in self.elements}
        self.by_requirement = {
            requirement.model: requirement for requirement in self.requirements
        }
        if len(self.by_model) != len(self.elements) or len(self.by_requirement) != len(
            self.requirements
        ):
            raise ValueError("Catalog identifiers must be unique.")
        if len({requirement.id for requirement in self.requirements}) != len(
            self.requirements
        ):
            raise ValueError("Catalog requirement IDs must be unique.")
        by_name = {requirement.name: requirement for requirement in self.requirements}
        for element in self.elements:
            seen = set()
            parent = element
            for parameter in element.properties:
                parameter.validate()
            while parent.parent is not None:
                if parent.model in seen or parent.parent not in self.by_model:
                    raise ValueError(
                        "Catalog element parents must resolve without cycles."
                    )
                seen.add(parent.model)
                parent = self.by_model[parent.parent]
        for requirement in self.requirements:
            requirement.validate()
            seen, stack = set(), list(requirement.derives_from)
            while stack:
                name = stack.pop()
                if name not in by_name or name == requirement.name:
                    raise ValueError(f"{requirement.name}: invalid derivation source.")
                if name not in seen:
                    seen.add(name)
                    stack.extend(by_name[name].derives_from)
            for expression in [
                requirement.condition,
                *[
                    parameter.expression
                    for parameter in requirement.parameters
                    if parameter.expression
                ],
            ]:
                for target, name in re.findall(
                    r"@([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)", expression
                ):
                    if target not in by_name or name not in {
                        parameter.name for parameter in by_name[target].parameters
                    }:
                        raise ValueError(
                            f"{requirement.name}: unknown template reference {target}.{name}."
                        )

    def validate_expressions(self):
        """Type-check definitions against owned native parameters without execution."""
        from ..core.evaluation import EvaluationContext
        from ..core.requirements import Parameter, Requirement
        from ..core.session import Session
        from .definitions import PYTHON_TYPES

        session = Session(catalog=self)
        rows = []
        for template in self.requirements:
            row = Requirement(
                f"template_{template.name}",
                template.text,
                parameters=tuple(
                    Parameter(
                        parameter.name,
                        PYTHON_TYPES[parameter.kind],
                        parameter.unit or "",
                    )
                    for parameter in template.parameters
                ),
            )
            session.add(row, owner=session.external, initialize=False)
            rows.append((template, row))
        context = EvaluationContext(session)
        for template, row in rows:
            expressions = [
                (template.condition, "boolean"),
                (template.acceptance, "boolean"),
            ]
            expressions.extend(
                (
                    parameter.expression,
                    "boolean" if parameter.kind == "boolean" else "number",
                )
                for parameter in template.parameters
                if parameter.expression
            )
            for expression, expected in expressions:
                if not expression:
                    continue
                source = re.sub(
                    r"@([A-Za-z_][A-Za-z0-9_]*)\.", r"template_\1.", expression
                )
                tree, _ = context.engine.tree(source)
                if context.engine.infer(tree, row) not in (expected, "null"):
                    raise ValueError(
                        f"{template.name}: a catalog expression has an incompatible type."
                    )
        return self

    def children(self, definition):
        return tuple(
            element for element in self.elements if element.parent == definition
        )

    def requirements_for(self, definition):
        element = self.by_model.get(definition)
        context = (
            "mission"
            if element and element.role == "orbit"
            else "eps"
            if element and element.role == "eps"
            else None
        )
        return tuple(
            requirement
            for requirement in self.requirements
            if requirement.context == context
        )

    def projection(self):
        result = []
        for element in self.elements:
            item = element.projection()
            requirements = self.requirements_for(element.model)
            if requirements:
                item["requirements"] = [
                    requirement.projection() for requirement in requirements
                ]
            result.append(item)
        return result


@lru_cache(maxsize=1)
def default_catalog():
    return FrameworkCatalog().validate_expressions()


def catalog():
    """Detached browser metadata produced from the same native definitions."""
    return default_catalog().projection()
