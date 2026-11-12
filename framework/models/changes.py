"""Shared native edit operations used by interactive clients and the UI service."""

from __future__ import annotations

import io
import tokenize
from dataclasses import replace

from .elements import Component, Element
from .requirements import Parameter, Statement
from .predicates import DraftExpression, restored_expression
from .database import DatabaseBacked, FactReference


def retype_element(session, identity, definition):
    """Retain object identity while changing an empty catalog element's type."""
    from .registry import element_class
    from .budgets import after_element_added

    value = session.get(identity)
    if not isinstance(value, Element) or value.selection:
        raise TypeError("Choose a generic domain element to change its type.")
    target = session.catalog.by_model.get(definition)
    if target is None:
        raise ValueError("Choose a definition from the generic catalog.")
    if value.definition == definition:
        return value
    if (
        value.children
        or value.property_values
        or isinstance(value, Component) and any(
            parameter.value is not None or parameter.expression is not None
            and not (parameter.name == "average_power_W" and parameter.expression == "draw_power_W")
            for parameter in value.parameters.values()
        )
        or value.requirement_links
        or value.quantity != 1
        or any(row.owner is value for row in session.statements)
        or session.power.load_for(value) is not None
    ):
        raise ValueError(
            "Remove child rows and component configuration before changing this type."
        )
    if target.parent is None:
        valid_owner = value.owner is session.mission
    else:
        valid_owner = (
            value.owner is not None and value.owner.definition == target.parent
        )
    if not valid_owner:
        raise ValueError("The selected type belongs to a different parent table.")
    old_class, old_definition = type(value), value.definition
    before = set(session._objects)
    history = set(session.seed_history)
    initialized = set(session._initialized)
    variables = list(session.variables)
    remembered = dict(session.requirement_seeds)
    flags = (
        session.resource_budgets,
        session._resource_budgets_present,
        session._requirement_seeds_present,
        session._model_state_present,
    )
    statements = {
        row: (dict(row.parameters), row.sources, row.affected)
        for row in session.statements
    }
    component_state = {component: dict(component.parameters) for component in session.components}
    budget = getattr(value, "_budget_parameters", None)
    value.__class__, value.definition = element_class(definition), definition
    try:
        if isinstance(value, Component) and budget is None:
            value._initialize_budget(())
        elif not isinstance(value, Component) and budget is not None:
            del value._budget_parameters
        session._initialized.discard(value.key)
        session.initialize(value)
        value.on_added(session)
        after_element_added(session, value)
        session.validate_budgets()
    except Exception:
        for object_key in set(session._objects) - before:
            session._objects.pop(object_key)._session = None
        session.seed_history, session._initialized = history, initialized
        session.variables, session.requirement_seeds = variables, remembered
        (
            session.resource_budgets,
            session._resource_budgets_present,
            session._requirement_seeds_present,
            session._model_state_present,
        ) = flags
        for row, (parameters, sources, affected) in statements.items():
            row._parameters, row._sources, row._affected = parameters, sources, affected
        value.__class__, value.definition = old_class, old_definition
        for component, parameters in component_state.items():
            component._budget_parameters = parameters
        if budget is None:
            value.__dict__.pop("_budget_parameters", None)
        raise
    session._model_state_present = True
    return value


def substitute_product(session, identity, product):
    """Use the generic inheritance of the new product while retaining fact names."""
    from .cots import PRODUCT_CLASSES, PRODUCT_TYPES, component_for_product

    value = session.get(identity)
    if not isinstance(value, DatabaseBacked):
        raise TypeError("Choose a database-backed component.")
    upgrade_combination = (
        type(value) in PRODUCT_TYPES.values()
        and PRODUCT_CLASSES.get(product) not in (None, type(value))
    )
    if value.product == product and not upgrade_combination:
        return value
    replacement = component_for_product(product, database=session.database)
    cls = type(replacement)
    old_class, old_definition, old_product, old_usage = (
        type(value),
        value.definition,
        value.product,
        value.usage,
    )
    budget = getattr(value, "_budget_parameters", None)
    value.__class__ = cls
    try:
        if isinstance(value, Component) and budget is None:
            value._initialize_budget(())
        elif not isinstance(value, Component) and budget is not None:
            if any(parameter.value is not None or parameter.expression is not None
                   and not (parameter.name == "average_power_W" and parameter.expression == "draw_power_W")
                   for parameter in budget.values()):
                raise ValueError("Clear installed budget inputs before substituting a product without component accounting.")
            del value._budget_parameters
        value.definition = replacement.definition
        value.product = product
        if (
            value.usage is not None
            and value.usage.definition.rsplit("::", 1)[-1]
            != value.definition.rsplit("::", 1)[-1]
        ):
            value.usage = None
        if value.usage is None:
            matches = [
                element
                for element in session.elements
                if element.owner is value.owner
                and element.definition.rsplit("::", 1)[-1]
                == value.definition.rsplit("::", 1)[-1]
            ]
            if len(matches) == 1:
                value.usage = matches[0]
    except Exception:
        value.__class__, value.definition, value._product, value._usage = (
            old_class,
            old_definition,
            old_product,
            old_usage,
        )
        if budget is None:
            value.__dict__.pop("_budget_parameters", None)
        else:
            value._budget_parameters = budget
        raise
    session._model_state_present = True
    return value


def configure_parameter(session, identity, parameter):
    """Replace an owned binding after validating its domain constraints."""
    value = session.get(identity)
    if not isinstance(parameter, Parameter) or not hasattr(value, "parameters"):
        raise TypeError("Configure a typed Parameter on a component, requirement or analysis.")
    if isinstance(value, Component):
        value._configure_budget(parameter)
    elif isinstance(value, Statement):
        link = value.linked_parameter(parameter.name)
        if link is not None and parameter.expression != f"{link[0].id}.{link[1]}":
            return configure_parameter(session, link[0], value.component_input(parameter))
        session.validate_parameter_binding(value, parameter)
        if parameter.name not in value.parameters:
            value.add_parameter(parameter)
        else:
            value._parameters[parameter.name] = parameter
    else:
        if parameter.name not in {port.name for port in value.inputs}:
            raise ValueError("Bind a declared analysis input.")
        value.parameters[parameter.name] = parameter
    session.register_parameter(parameter)
    session._model_state_present = True
    return parameter


def _field_source(source, identifier, old, new):
    if not isinstance(source, str):
        return source
    tokens = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type not in (
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.COMMENT,
            ):
                tokens.append(token)
    except (tokenize.TokenError, IndentationError):
        pass
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    spans = [
        (
            offsets[field.start[0] - 1] + field.start[1],
            offsets[field.end[0] - 1] + field.end[1],
        )
        for row, dot, field in zip(tokens, tokens[1:], tokens[2:])
        if row.type == tokenize.NAME
        and row.string == identifier
        and dot.string == "."
        and field.type == tokenize.NAME
        and field.string == old
    ]
    for start, end in reversed(spans):
        source = source[:start] + new + source[end:]
    return source


def configure_facts(session, identity, references):
    """Retain named selections, rewrite renames, and protect referenced deletions."""
    value = session.get(identity)
    if not isinstance(value, DatabaseBacked):
        raise TypeError("Choose a database-backed component.")
    references = tuple(references)
    if any(not isinstance(reference, FactReference) for reference in references):
        raise TypeError("Select FactReference instances.")
    if len({reference.key for reference in references}) != len(references) or len(
        {reference.name for reference in references}
    ) != len(references):
        raise ValueError("Fact keys and names must be unique.")
    previous = {reference.key: reference for reference in value.facts}
    record = value.product_record
    records = {} if record is None else {fact.id: fact for fact in record.facts}
    for reference in references:
        fact = records.get(reference.fact)
        if fact is not None and reference != previous.get(reference.key):
            message = value.property_reference_error(reference, fact)
            if message:
                raise ValueError(message)
    following = {reference.key: reference for reference in references}
    removed = [
        reference.name for reference in value.facts if reference.key not in following
    ]
    for _, _, _, source in session._expressions():
        if any(
            _field_source(source, value.id, name, "__used__") != source
            for name in removed
        ):
            raise ValueError(
                "Remove expression references before deleting a selected COTS fact."
            )
    renames = [
        (reference.name, following[key].name)
        for key, reference in previous.items()
        if key in following and reference.name != following[key].name
    ]
    # Simultaneous renames use temporary field names so swaps stay unambiguous.
    for index, (old, _) in enumerate(renames):
        _rename_field(session, value.id, old, f"_fact_rename_{index}")
    for index, (_, new) in enumerate(renames):
        _rename_field(session, value.id, f"_fact_rename_{index}", new)
    value.facts = references
    value._facts_present = True
    session._model_state_present = True
    return value


def _rename_field(session, identifier, old, new):
    for row, kind, name, source in tuple(session._expressions()):
        rewritten = _field_source(source, identifier, old, new)
        if rewritten == source:
            continue
        session._set_expression(row, kind, name, restored_expression(rewritten))
    for link in session.power.links:
        for name, parameter in tuple(link.previous.items()):
            source = (
                parameter.expression.source
                if isinstance(parameter.expression, DraftExpression)
                else parameter.expression
            )
            if isinstance(source, str):
                link.previous[name] = replace(
                    parameter,
                    expression=restored_expression(
                        _field_source(source, identifier, old, new)
                    ),
                )
