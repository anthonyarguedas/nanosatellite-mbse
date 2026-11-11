"""Native construction helpers shared by the optional study configurations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from ..catalogs.cots import component_for_product
from ..core.requirements import Parameter, Requirement
from ..core.predicates import VerificationMethod
from ..core.session import Session
from ..domains.eps.subsystem import EPS
from ..domains.mission import CubeSat
from ..persistence.repository import validate_session

_TYPES = {"float": float, "integer": int, "boolean": bool, "string": str}
DOCUMENT = "framework/requirements-ui/analyses/REPORT-COVERAGE.md"


@dataclass(frozen=True)
class Field:
    name: str
    unit: str = ""
    type: str = "float"
    expression: Optional[str] = None

    def parameter(self):
        return Parameter(
            self.name, _TYPES[self.type], self.unit or "", expression=self.expression
        )


def label(name):
    return re.sub(
        r"\bsoc\b",
        "state of charge",
        re.sub(
            r"_(?:per_s|W_m2|kg|m3|m2|m|J|W|V|A|C|K|s|Hz|deg|ohm|A2s|Ah)$", "", name
        ).replace("_", " "),
    )


def add_requirement(
    session,
    *,
    text,
    fields=(),
    owner=None,
    affected=(),
    sources=(),
    condition="",
    script=None,
    component=None,
    prefix="ASM",
    origin="",
    rationale="",
):
    requirement = Requirement(
        session.next_id("Requirement", prefix),
        text,
        parameters=tuple(field.parameter() for field in fields),
        owner=session.external if owner is None else owner,
        affected=tuple(affected),
        sources=tuple(sources),
        origin=origin,
        rationale=rationale,
        verifications=(
            VerificationMethod(
                "assessment",
                condition,
                source=script if script is not None else component,
            ),
        )
        if condition
        else (),
    )
    session.add(requirement, initialize=False)
    if component is not None:
        component.requirement_links = (*component.requirement_links, requirement)
    if len(session.variables) > 256:
        raise ValueError("This study exceeds the browser's 256 shared display names.")
    return requirement


class AnalysisCase:
    def __init__(self, builder, definition, name, reports):
        self.builder = builder
        self.reports = tuple(reports)
        self.script = builder.session.add(
            builder.session.verification_registry.create(definition, name=name),
            initialize=False,
        )
        self.owners = {}
        self.sources = []
        numeric = [port for port in self.script.inputs if port.value_type is not bool]
        for offset in range(0, len(numeric), 4):
            group = numeric[offset : offset + 4]
            row = builder.requirement(
                text=(
                    f"The {name.lower()} assessment shall use "
                    + ", ".join(f"{label(port.name)} $${port.name}$$" for port in group)
                    + "."
                ),
                fields=tuple(
                    Field(
                        port.name,
                        port.unit or "",
                        "integer" if port.value_type is int else "float",
                    )
                    for port in group
                ),
                reports=reports,
                script=self.script,
                prefix="INP",
                condition=" and ".join(f"math.isfinite({port.name})" for port in group),
                extra="Boolean model choices remain explicit unset inputs in the script table.",
            )
            self.sources.append(row)
            for port in group:
                self.owners[port.name] = row
                self.script.set_expression(port.name, f"{row.id}.{port.name}")

    def ref(self, output):
        return f"{self.script.id}.{output}"

    def input(self, name):
        parameter = self.script.parameters[name]
        return parameter.expression

    def fields(self, *names):
        ports = {port.name: port for port in self.script.inputs}
        fields = []
        for name in names:
            port = ports.get(name)
            if port is None or port.value_type is bool:
                raise ValueError(
                    f"{self.script.definition}.{name}: choose a numeric input."
                )
            fields.append(
                Field(
                    name,
                    port.unit or "",
                    "integer" if port.value_type is int else "float",
                    self.input(name),
                )
            )
        return tuple(fields)

    def set(self, name, expression):
        if name in self.owners:
            self.owners[name].set_expression(name, expression)
        else:
            self.script.set_expression(name, expression)

    def check(self, text, fields, condition, reports=None):
        return self.builder.requirement(
            text=text,
            fields=fields,
            condition=condition,
            reports=self.reports if reports is None else reports,
            script=self.script,
            sources=self.sources,
            prefix="CHK",
        )


class ReportBuilder:
    def __init__(self, name, **providers):
        self.session = Session(name=name, **providers)
        self.session.variables = []
        self.bus = self.session.add(CubeSat("BUS", key="report-bus"), initialize=False)
        self.eps = self.session.add(
            EPS("EPS", key="report-eps"), owner=self.bus, initialize=False
        )
        self.rationale = (
            f"{name}. This is a bounded report assessment, with inputs and acceptance limits supplied by the engineer. "
            "No product, mission, protection setting or safety margin is assumed. Use compatible sources and conditions. "
            "An input declaration checks the executed model domain. Separate product criteria assess its outputs. "
            "A passing case covers its declared model and interval. See analyses/REPORT-COVERAGE.md for remaining scope."
        )

    def requirement(
        self,
        *,
        text,
        fields=(),
        condition,
        script=None,
        component=None,
        prefix="ASM",
        sources=(),
        reports=(),
        extra="",
    ):
        return add_requirement(
            self.session,
            text=text,
            fields=fields,
            condition=condition,
            script=script,
            component=component,
            prefix=prefix,
            sources=sources,
            owner=self.eps,
            origin=f"{DOCUMENT}#{','.join(reports)}",
            rationale=self.rationale + (f" {extra}" if extra else ""),
        )

    def analysis(self, definition, name, reports):
        return AnalysisCase(self, definition, name, reports)

    def component(self, product, selections):
        component = component_for_product(product, database=self.session.database)
        self.session.add(component, owner=self.eps, initialize=False)
        for name, query in selections:
            matches = [
                fact
                for fact in component.product_record.facts
                if all(
                    fact.projection().get(key) == value for key, value in query.items()
                )
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"{product}.{name}: expected one exact current COTS record, found {len(matches)}."
                )
            component.select_fact(name, matches[0])
        return component

    def finish(self):
        self.session.reconcile_defaults()
        validate_session(self.session)
        return self.session
