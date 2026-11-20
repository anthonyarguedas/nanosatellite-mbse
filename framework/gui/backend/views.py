"""Browser presentation of public model objects and native evaluation reports."""

from numbers import Real
from urllib.parse import urlsplit

from framework import models
from framework.cots import load_catalog
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


def catalog_url(value):
    parsed = urlsplit(value)
    return value if parsed.scheme in ("http", "https") and parsed.netloc else ""


def catalog_fact(fact, catalog):
    return {
        "parameter": fact.parameter or fact.model_property, "value": display(fact.value), "unit": fact.unit,
        "valueKind": fact.value_kind, "conditionId": fact.condition_id, "elementId": fact.element_id,
        "sourceId": fact.source_id, "sourceUrl": catalog_url(catalog.sources[fact.source_id]["url"]),
        "sourceLocator": fact.source_locator, "note": fact.note,
    }


def catalog_condition(condition_id, catalog):
    if not condition_id:
        return None
    return {
        "id": condition_id,
        "fields": [{"name": key, "value": value} for key, value in catalog.conditions[condition_id].items()
                   if key != "condition_id" and value],
        "parameters": [{**row, "sourceUrl": catalog_url(catalog.sources[row["source_id"]]["url"])}
                       for row in catalog.condition_parameters.get(condition_id, ())],
    }


def catalog_options(component, candidates, catalog):
    kinds, conditions, numeric, categorical = {}, set(), set(), set()
    properties = dict(component.properties)
    for candidate in candidates:
        properties.update(candidate.properties)
        element = catalog.elements.get((candidate.product_id, candidate.catalog_element), {})
        elements = {"self", candidate.catalog_element, element.get("parent_element_id")}
        roles = {cls.__name__ for cls in candidate.catalog_role.__mro__}
        aliases = getattr(candidate.catalog_product.model_class, "catalog_parameters", {})
        for fact in candidate.catalog_product.facts:
            if fact.value is None or fact.element_id not in elements or fact.model_class and fact.model_class not in roles:
                continue
            if fact.condition_id:
                conditions.add(fact.condition_id)
            name = fact.model_property or fact.parameter
            names = {name} | {key for key, parameter in aliases.items() if not fact.model_class and parameter == name}
            for name in names & candidate.properties.keys():
                kinds.setdefault(name, set()).add(fact.value_kind)
                (numeric if isinstance(fact.value, Real) and not isinstance(fact.value, bool) else categorical).add(name)
    return {
        "sortProperties": sorted(name for name, prop in properties.items() if "__" not in name
                                 and name not in ("voltage_extrema", "current_extrema")
                                 and name not in categorical - numeric
                                 and (name in numeric or str(prop.unit) not in ("", "1"))),
        "valueKinds": {name: sorted(values) for name, values in sorted(kinds.items())},
        "conditions": [{"id": key, "label": ", ".join(f"{name}: {value}" for name, value in catalog.conditions[key].items()
                                                     if name != "condition_id" and value)} for key in sorted(conditions)],
    }


def recommendations(component, *, sort_by=None, reverse=False, limit=None, mode=None,
                    condition_id="", element_id=None, value_kinds=None):
    matches = models.recommend_cots(component, sort_by=sort_by, reverse=reverse, limit=limit, mode=mode,
                                   condition_id=condition_id, element_id=element_id, value_kinds=value_kinds)
    catalog = load_catalog()
    available = tuple(catalog.candidates(component))
    compatible = tuple(item for item in available if element_id is None or item.catalog_element == element_id)
    results = []
    for match in matches:
        candidate, product = match.candidate, match.candidate.catalog_product
        results.append({
            "name": candidate.name, "className": product.model_class.__name__,
            "productId": product.product_id, "manufacturer": product.manufacturer, "partNumber": product.part_number,
            "productUrl": catalog_url(product.product_url), "datasheetUrl": catalog_url(product.datasheet_url),
            "role": candidate.catalog_role.__name__, "elementId": candidate.catalog_element,
            "csrmTypes": [cls.__name__ for cls in models.EPS.default_components if isinstance(candidate, cls)],
            "conditionId": candidate.catalog_condition,
            "sortValue": display(match.sort_value) if sort_by is not None else "",
            "sortUnit": str(candidate.properties[sort_by].unit) if sort_by is not None else "",
            "bindings": [{"property": binding.property_name, "facts": [catalog_fact(fact, catalog) for fact in binding.facts]}
                         for binding in candidate.catalog_bindings if "__" not in binding.property_name and binding.facts],
            "unsetProperties": sorted(name for name, prop in candidate.properties.items() if "__" not in name and prop.expression is None),
            "checks": [{"requirement": entry.requirement.name, "condition": entry.condition.name,
                        "measure": display(entry.measure), "measureUnit": str(entry.condition.measure.unit),
                        "target": display(entry.target), "targetUnit": str(entry.condition.target.unit),
                        "predicate": entry.condition.expression} for entry in match.report.results],
        })
    return {
        "catalogSize": len(catalog), "compatibleCount": len(compatible),
        "compatibleProducts": len({item.product_id for item in compatible}), "requirements": len(component.requirements),
        "channels": sorted({item.catalog_element for item in available}),
        "selectedCondition": catalog_condition(condition_id, catalog),
        **catalog_options(component, compatible, catalog), "results": results,
    }


def describe(mission, *, mode=None, selected=None):
    report = mission.verify(mode=mode)
    objects, contexts = [], [{"path": "@external", "name": "External"}]
    for item in mission.walk():
        if isinstance(item, models.VerificationCondition):
            continue
        kind = "requirement" if isinstance(item, models.Requirement) else "mode" if isinstance(item, MODE_ROWS) else "external" if isinstance(item, (models.Stakeholder, models.ThirdParty)) else "element"
        row = {"path": item.path, "name": item.name, "parent": item.parent.path if item.parent else None,
               "className": type(item).__name__, "kind": kind, "fixed": item.fixed_properties,
               "recommendable": isinstance(item, models.Component) and not item.fixed_properties,
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
