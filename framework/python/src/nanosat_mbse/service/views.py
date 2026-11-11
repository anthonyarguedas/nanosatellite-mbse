"""Workbook descriptions projected from the native graph and engineering types."""

from __future__ import annotations

from ..catalogs.database import DatabaseBacked
from ..core.configuration import ScriptConfiguration
from ..core.elements import Element
from ..core.requirements import Statement
from ..domains.budgets import (
    BUDGET_CLASSES,
    POWER_MODELS,
    RESOURCES,
    POWER_INPUTS,
    load_for,
    power_scopes,
    power_limit_for,
    resource_for,
    resource_scopes,
    resource_limit_for,
    spacecraft_components,
)
from .validation import KINDS, STAKEHOLDERS


def tabs(session):
    result = [
        {
            "key": "external",
            "label": "External",
            "leftTitle": "Stakeholders and Third Parties",
            "requirementsTitle": "Stakeholder Requirements",
            "prefix": "REQ",
        },
        {
            "key": "mission",
            "label": "Mission",
            "leftTitle": "Mission Domain Elements",
            "requirementsTitle": "Mission Requirements",
            "affectedLabel": "Affected domain elements",
            "prefix": "MIS",
        },
    ]
    elements = [row for row in session.elements if row.expandable]

    def label(row):
        definition = session.catalog.by_model.get(row.definition)
        return (
            row.name
            if definition is None or row.name != definition.name
            else definition.tab_label or definition.name
        )

    for row in elements:
        name = label(row)
        definition = session.catalog.by_model.get(row.definition)
        component = row.role in ("eps", "subsystem")
        result.append(
            {
                "key": row.key,
                "label": f"{name} ({row.id})"
                if any(other is not row and label(other) == name for other in elements)
                else name,
                "leftTitle": f"{name} {'Components' if component else 'Elements' if row.role == 'payload' else 'Subsystems'}",
                "requirementsTitle": f"{name} {'Parametric Requirements' if row.role == 'eps' else 'Requirements'}",
                "affectedLabel": "Affected components"
                if component
                else "Affected elements"
                if row.role == "payload"
                else "Affected subsystems",
                "prefix": definition.prefix if definition is not None else "REQ",
            }
        )
    return result


def allowed_definitions(session, owner):
    owner = session.get(owner)
    return [
        definition.projection()
        for definition in session.catalog.elements
        if (
            definition.parent is None
            if owner is session.mission
            else owner.expandable and definition.parent == owner.definition
        )
    ]


def _source_candidates(session, statement):
    excluded = {statement.key}
    changed = True
    while changed:
        changed = False
        for row in session.statements:
            if row.key not in excluded and any(
                source.key in excluded for source in row.sources
            ):
                excluded.add(row.key)
                changed = True
    return [
        row.key
        for row in session.objects
        if row not in (session.mission, session.external)
        and row.key not in excluded
        and not isinstance(row, ScriptConfiguration)
    ]


def _required_sources(session, row):
    scope = row.power_scope or row.budget_scope
    if scope is None:
        return []
    resource = resource_for(row)
    scopes = (
        power_scopes(session)
        if row.power_scope is not None
        else resource_scopes(session)
    )
    subject = next((item for item in scopes if item.target is scope), None)
    if subject is None or subject.parent is None:
        return []
    parent = (
        power_limit_for(session, subject.parent)
        if row.power_scope is not None
        else resource_limit_for(session, subject.parent, resource)
    )
    return [] if parent is None else [parent.key]


def describe(session, *, callables=None):
    """Return presentation metadata. Native methods remain the validation boundary."""
    projection = session.to_projection(callables=callables)
    contexts = tabs(session)
    elements = list(session.elements)
    descriptions = {}
    for row in session.objects:
        if row in (session.mission, session.external):
            continue
        metadata = {
            "className": type(row).__name__,
            "role": getattr(row, "role", "statement"),
        }
        if isinstance(row, Statement):
            metadata.update(
                {
                    "parameterNames": list(row.parameters),
                    "parameters": projection.get("modelState", {})
                    .get("parameters", {})
                    .get(row.key, {}),
                    "sources": _source_candidates(session, row),
                    "affected": [
                        element.key
                        for element in elements
                        if element.owner is row.owner
                    ],
                    "powerRequirement": row.definition in POWER_MODELS,
                    "resourceRequirement": row.definition in BUDGET_CLASSES
                    and row.definition not in POWER_MODELS,
                    "draftIssues": list(getattr(row, "draft_issues", ())),
                    "requiredSources": _required_sources(session, row),
                    "loadInput": row.definition == "FrameworkRequirements::LoadEnergy",
                    "managedParameters": list(POWER_INPUTS)
                    if row.definition == "FrameworkRequirements::LoadEnergy"
                    and any(link.eps is row.owner for link in session.power.links)
                    else [],
                }
            )
        if isinstance(row, DatabaseBacked):
            metadata.update(
                {
                    "requirements": [
                        requirement.key
                        for requirement in session.requirements
                        if requirement.owner is row.owner
                    ],
                    "usage": None if row.usage is None else row.usage.key,
                    "genericClass": type(row).__mro__[1].__name__,
                }
            )
        if isinstance(row, Element):
            metadata["expandable"] = row.expandable and not row.selection
        descriptions[row.key] = metadata
    power = {}
    for component in spacecraft_components(session):
        load = load_for(session, component)
        power[component.key] = {
            "element": component.key,
            "quantity": load.quantity,
            "accounting": load.accounting,
            "host": "" if load.host is None else load.host.key,
            "rationale": load.rationale,
            "states": [
                {
                    "key": state.key,
                    "name": state.name,
                    "watts": state.watts,
                }
                for state in load.states
            ],
            "assignments": {
                mode.key: state.key for mode, state in load.assignments.items()
            },
            "duties": {mode.key: duty for mode, duty in load.duties.items()},
            "allocations": {
                mode.key: [{"state": item.state.key, "duty": item.duty} for item in entries]
                for mode, entries in load.allocations.items()
            },
        }
    return {
        "tabs": contexts,
        "allowedDefinitions": {
            context["key"]: allowed_definitions(session, context["key"])
            for context in contexts
            if context["key"] != "external"
        },
        "stakeholderTypes": list(STAKEHOLDERS),
        "statementKinds": list(KINDS),
        "objects": descriptions,
        "powerDefaults": power,
        "powerComponents": list(power),
        "powerLossDefinitions": {
            context["key"]: next(
                (item["model"] for item in allowed_definitions(session, context["key"])
                 if item["category"] == "Power Loss"), None
            )
            for context in contexts if context["key"] != "external"
        },
        "powerScopes": [
            {"key": scope.key, "kind": scope.kind} for scope in power_scopes(session)
        ],
        "accountingOptions": {
            component.key: (
                ["host", "excluded"]
                if component.default_accounting == "host"
                else ["counted", "excluded"]
            )
            for component in spacecraft_components(session)
        },
        "executionHosts": [
            component.key
            for component in spacecraft_components(session)
            if component.definition.endswith("::ProcessorAndMemory")
        ],
        "loadRoots": [
            row.key
            for row in session.elements
            if row.owner is session.mission and row.role in ("bus", "payload")
        ],
        "powerInputs": [
            "sunlight_power_W",
            "eclipse_power_W",
            "sunlight_duty",
            "eclipse_duty",
        ],
        "resources": [
            {
                "name": resource.name,
                "unit": resource.unit,
                "value": resource.value,
                "limit": resource.limit,
                "allocated": resource.allocated,
            }
            for resource in RESOURCES
        ],
        "budgetDefinitions": list(BUDGET_CLASSES),
        "limits": {
            "variables": 256,
            "rows": 10000,
            "scripts": 64,
            "methods": 32,
            "facts": 64,
            "modes": 24,
            "states": 32,
        },
    }
