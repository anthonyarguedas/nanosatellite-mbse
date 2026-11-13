"""Browser presentation of public model objects and native evaluation reports."""

from framework import models
from .edits import allowed_types

MODES = (models.SpacecraftMode, models.ComponentMode, models.ComponentState)
MODE_ROWS = (*MODES, models.TimeAllocation)
CONTEXTS = (models.Mission, models.DomainElement, models.Orbit, models.Subsystem, models.Component, models.Stakeholder)


def display(value):
    return format(value, ".10g") if type(value) is float else repr(value)[:4000]


def assessment(prop, mode):
    result = prop.assess(mode=mode)
    return {"status": result.status.value, "value": display(result.value) if result.status is models.EvaluationStatus.VALUE else "", "message": result.message}


def verification(value):
    return {"verified": value.verified, "status": value.status.value, "failures": [failure.explain() for failure in value.failures]}


def coverage(item, report):
    if isinstance(item, models.Requirement):
        return models.InstanceVerification(item, tuple(result for result in report.results if result.requirement is item))
    return report.for_instance(item)


def parameters(owner, report, mode, *, evaluate=False):
    return [
        {"name": name, "expression": prop.expression, "unit": str(prop.unit),
         "bindings": [{"mode": key.path, "expression": value} for key, value in prop.modes.items()],
         **({"assessment": assessment(prop, mode), "verification": verification(report.for_instance(prop))} if evaluate else {})}
        for name, prop in owner.properties.items()
    ]


def detail(item, report, mode):
    result = {"path": item.path, "name": item.name, "className": type(item).__name__,
              "fixed": item.fixed_properties, "properties": parameters(item, report, mode, evaluate=True),
              "verification": verification(coverage(item, report))}
    if isinstance(item, models.Requirement):
        try:
            rendered, message = item.render_statement(mode=mode), ""
        except Exception as error:
            rendered, message = item.statement, str(error)
        condition_results = {entry.condition: entry for entry in report.results}
        result.update(statement=item.statement, rationale=item.rationale, rendered=rendered, statementMessage=message,
                      conditions=[{
                          "name": condition.name, "expression": condition.expression,
                          "properties": parameters(condition, report, mode, evaluate=True),
                          "result": {"status": condition_results[condition].status.value,
                                     "value": condition_results[condition].value,
                                     "message": condition_results[condition].message,
                                     "measure": display(condition_results[condition].measure),
                                     "target": display(condition_results[condition].target)},
                      } for condition in item.conditions])
    if isinstance(item, models.Mission):
        result["imports"] = [imported.source for imported in item.imports.values()]
    return result


def describe(mission, *, mode=None, selected=None):
    report = mission.verify(mode=mode)
    objects, contexts = [], [{"path": "@external", "name": "External"}]
    for item in mission.walk():
        if isinstance(item, models.VerificationCondition):
            continue
        kind = "requirement" if isinstance(item, models.Requirement) else "mode" if isinstance(item, MODE_ROWS) else "external" if isinstance(item, (models.Stakeholder, models.ThirdParty)) else "element"
        row = {"path": item.path, "name": item.name, "parent": item.parent.path if item.parent else None,
               "className": type(item).__name__, "kind": kind, "fixed": item.fixed_properties,
               "properties": parameters(item, report, mode), "verification": verification(coverage(item, report)),
               "context": isinstance(item, CONTEXTS)}
        if isinstance(item, CONTEXTS):
            contexts.append({"path": item.path, "name": item.name})
            row["types"] = allowed_types(mission, item)
            row["scopeModes"] = [value.path for value in getattr(item, "modes", ())]
        if isinstance(item, (models.SpacecraftMode, models.ComponentMode)):
            row["types"] = allowed_types(mission, item)
        if isinstance(item, models.Requirement):
            try:
                row["rendered"], row["statementMessage"] = item.render_statement(mode=mode), ""
            except Exception as error:
                row["rendered"], row["statementMessage"] = item.statement, str(error)
            row["statement"] = item.statement
        if isinstance(item, MODE_ROWS):
            row["values"] = {name: assessment(prop, mode) for name, prop in item.properties.items()}
            row["target"] = item.spacecraft_mode.path if isinstance(item, models.ModeAllocation) else item.state.path if isinstance(item, models.StateAllocation) else None
        objects.append(row)
    return {"mission": mission.path, "objects": objects, "contexts": contexts,
            "modes": [{"path": item.path, "name": item.name, "className": type(item).__name__} for item in mission.walk() if isinstance(item, MODES)],
            "imports": [item.source for item in mission.imports.values()],
            "mode": mode.path if mode is not None else "", "verification": verification(report),
            "detail": detail(mission.get(selected), report, mode) if selected else None}
