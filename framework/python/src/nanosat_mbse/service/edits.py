"""Apply transport edits to trusted native objects through their domain methods.

The incoming document supplies changes. It is never reconstructed as the
replacement authority. Custom classes and configuration remain in a trusted
native clone, including fields that have no browser representation.
"""

from __future__ import annotations

import re
from dataclasses import replace
from uuid import uuid4

from ..catalogs.cots import component_for_product
from ..catalogs.database import DatabaseBacked, FactReference
from ..core.configuration import ComponentState, Mode, ScriptPort, Variable
from ..core.drafts import DraftRequirement, DraftStatement
from ..core.elements import Element, Stakeholder
from ..core.requirements import Parameter, Requirement, Statement
from ..core.predicates import VerificationMethod, restored_expression
from ..core.verification import VerificationScript
from ..domains.budgets import BUDGET_CLASSES
from ..domains.eps.requirements import GenericRequirement
from ..domains.registry import element_class
from ..persistence.repository import dumps, loads, validate_session
from ..persistence.projection import _local_names
from .validation import TABLES, TYPES, normalize_projection, validate_projection
from .views import allowed_definitions


def clone_session(session):
    clone = loads(
        dumps(session),
        catalog=session.catalog,
        database=session.database,
        verification_registry=session.verification_registry,
        session_class=type(session),
    )
    if session.storage is not None:
        clone._storage_status = session.storage
    return clone


def rows_by_key(projection):
    return {row["key"]: (table, row) for table in TABLES for row in projection[table]}


def _source(parameter):
    from ..core.session import expression_source

    return expression_source(parameter, callables=True)


def _metadata(data, row_key, name):
    return (
        data.get("modelState", {}).get("parameters", {}).get(row_key, {}).get(name, {})
    )


def _validate_capabilities(data, base, registry):
    """Descriptors can only repeat a capability for the exact trusted slot."""
    state = data.get("modelState", {})
    for row_key, parameters in state.get("parameters", {}).items():
        if not isinstance(parameters, dict):
            raise ValueError("Parameter metadata must be keyed by parameter name.")
        for name, metadata in parameters.items():
            if not isinstance(metadata, dict) or set(metadata) - {
                "type",
                "unit",
                "literal",
                "callable",
            }:
                raise ValueError("Unsupported owned parameter metadata.")
            if "callable" in metadata:
                registry.resolve(
                    metadata["callable"], slot=("parameter", row_key, name)
                )
                original = _metadata(base, row_key, name).get("callable")
                if original != metadata["callable"]:
                    raise ValueError(
                        "Native bindings are read-only capabilities of this session."
                    )
    for row_key, methods in state.get("verificationBindings", {}).items():
        if not isinstance(methods, dict):
            raise ValueError("Native method bindings must be keyed by method key.")
        for method_key, descriptor in methods.items():
            registry.resolve(descriptor, slot=("condition", row_key, method_key))
            if (
                base.get("modelState", {})
                .get("verificationBindings", {})
                .get(row_key, {})
                .get(method_key)
                != descriptor
            ):
                raise ValueError(
                    "A native condition cannot be imported from browser metadata."
                )
    for eps, bindings in state.get("loadInputs", {}).items():
        for name, metadata in bindings.items():
            if "callable" in metadata:
                registry.resolve(metadata["callable"], slot=("loadInput", eps, name))
                if (
                    base.get("modelState", {})
                    .get("loadInputs", {})
                    .get(eps, {})
                    .get(name)
                    != metadata
                ):
                    raise ValueError(
                        "A native load input is a read-only session binding."
                    )


def _variables(data):
    return {row["name"]: row for row in data["variables"]}


def _new_parameter(name, source, data, row_key):
    variable = _variables(data).get(name, {"type": "float", "unit": ""})
    metadata = _metadata(data, row_key, name)
    if "callable" in metadata:
        raise ValueError("Browser additions cannot introduce native callable bindings.")
    kind = TYPES[metadata.get("type", variable["type"])]
    unit = metadata.get("unit", variable.get("unit", ""))
    return Parameter(
        name,
        kind,
        unit,
        expression=None if source is None else restored_expression(source),
    )


def _new_statement(session, row, data):
    names = {name for name, source in row["parameters"].items() if source is not None}
    names.update(re.findall(r"\$\$\s*([A-Za-z_][A-Za-z0-9_]*)\s*\$\$", row["text"]))
    names.update(data.get("modelState", {}).get("parameters", {}).get(row["key"], {}))
    for source in [
        row.get("condition", ""),
        *row["parameters"].values(),
        *(method["condition"] for method in row.get("verifications", [])),
    ]:
        names.update(_local_names(source, set(_variables(data))))
    parameters = tuple(
        _new_parameter(name, row["parameters"].get(name), data, row["key"])
        for name in sorted(names)
    )
    options = {
        "key": row["key"],
        "parameters": parameters,
        "kind": row["kind"],
        "rationale": row.get("rationale", ""),
        "origin": row.get("origin", ""),
        "definition": row.get("definition", ""),
        "name": row.get("name", ""),
    }
    template = session.catalog.by_requirement.get(row.get("definition"))
    if template is not None and row["kind"] == "Requirement":
        # Explicit authored copies use the same concrete requirement class. The
        # owner lifecycle creates generic defaults through its normal methods.
        try:
            return GenericRequirement.restore(
                row["id"], row["text"], template=template, **options
            )
        except (ValueError, TypeError):
            value = DraftRequirement(row["id"], row["text"], **options)
            value.template = template
            return value
    cls = (
        BUDGET_CLASSES.get(row.get("definition"), Requirement)
        if row["kind"] == "Requirement"
        else Statement
    )
    try:
        return cls(row["id"], row["text"], **options)
    except (ValueError, TypeError):
        return (DraftRequirement if row["kind"] == "Requirement" else DraftStatement)(
            row["id"], row["text"], **options
        )


def _new_object(session, table, row, data):
    if row["id"]:
        identifier = row["id"]
    elif table == "elements":
        identifier = session.next_id(
            "Element", session.catalog.by_model[row["definition"]].id
        )
    elif table == "stakeholders":
        identifier = session.next_id("Stakeholder", row.get("name", ""))
    elif table == "statements":
        owner = session.get(row["context"])
        definition = session.catalog.by_model.get(owner.definition)
        prefix = (
            "MIS"
            if owner is session.mission
            else definition.prefix
            if definition is not None
            else "REQ"
        )
        identifier = session.next_id(
            row["kind"], prefix if row["kind"] == "Requirement" else ""
        )
    else:
        identifier = session.next_id("Script" if table == "scripts" else "Component")
    row["id"] = identifier
    if table == "stakeholders":
        return Stakeholder(
            identifier, name=row["name"], key=row["key"], stakeholder_type=row["type"]
        )
    if table == "elements":
        return element_class(row["definition"])(
            identifier, name=row["name"], key=row["key"], definition=row["definition"]
        )
    if table == "components":
        return component_for_product(
            row["product"], database=session.database, id=identifier, key=row["key"]
        )
    if table == "scripts":
        value = session.verification_registry.create(
            row["definition"],
            identifier,
            name=row["name"],
            key=row["key"],
            revision=row["revision"],
            inputs=tuple(
                ScriptPort(port["name"], TYPES[port["type"]], port.get("unit"))
                for port in row["inputs"]
            ),
            outputs=tuple(
                ScriptPort(port["name"], TYPES[port["type"]], port.get("unit"))
                for port in row["outputs"]
            ),
        )
        value.assert_current()
        return value
    return _new_statement(session, row, data)


def _configure_parameters(session, value, row, original, data, base):
    supplied, previous = row["parameters"], original.get("parameters", {})
    variables, old_variables = _variables(data), _variables(base)
    for name in supplied:
        current = value.parameters.get(name)
        source = supplied[name]
        meta, old_meta = (
            _metadata(data, value.key, name),
            _metadata(base, value.key, name),
        )
        if current is None and source is None and not meta:
            continue
        if current is None:
            current = _new_parameter(name, None, data, value.key)
        if callable(current.expression):
            if source != previous.get(name) or meta.get(
                "callable", old_meta.get("callable")
            ) != old_meta.get("callable"):
                raise ValueError(
                    "Native callable bindings are read-only. Use the explicit replace_binding command to enter expression source."
                )
            continue
        kind, unit = current.value_type, current.unit
        variable, old_variable = variables.get(name), old_variables.get(name)
        if variable is not None and (original == {} or variable != old_variable):
            kind, unit = TYPES[variable["type"]], variable.get("unit", "")
        for field in ("type", "unit"):
            if field in meta and meta[field] != old_meta.get(field):
                if field == "type":
                    kind = TYPES[meta[field]]
                else:
                    unit = meta[field]
        changed = (
            source != previous.get(name)
            or name not in value.parameters
            or kind is not current.value_type
            or unit != current.unit
        )
        if not changed:
            continue
        parameter = replace(current, value_type=kind, unit=unit)
        if source != previous.get(name) or original == {}:
            parameter = replace(
                parameter,
                value=None,
                expression=None if source is None else restored_expression(source),
            )
        session.configure_parameter(value, parameter)


def _configure_methods(session, value, row, original, data, base):
    configured = row.get("verifications")
    if configured is None:
        condition = row.get("condition", "")
        native = (
            base.get("modelState", {})
            .get("verificationBindings", {})
            .get(value.key, {})
        )
        configured = (
            [{"key": "condition", "condition": condition}]
            if condition.strip() or "condition" in native
            else []
        )
    previous = {method.key: method for method in value.verifications}
    # Older editors cannot display native conditions. Omission from a snapshot
    # must not silently erase them. Explicit set_verifications is the editable
    # native command boundary for deliberate replacement or removal.
    configured = list(configured)
    configured_keys = {item["key"] for item in configured}
    for method in previous.values():
        if callable(method.condition) and method.key not in configured_keys:
            item = {"key": method.key, "condition": ""}
            if method.source is not None:
                item[
                    "component"
                    if isinstance(method.source, DatabaseBacked)
                    else "script"
                ] = method.source.key
            configured.append(item)
    original_methods = original.get("verifications")
    if original_methods is None:
        original_methods = [
            {"key": "condition", "condition": original.get("condition", "")}
        ]
    original_by_key = {method["key"]: method for method in original_methods}
    methods = []
    names = data.get("modelState", {}).get("verificationNames", {}).get(value.key, {})
    for item in configured:
        old = previous.get(item["key"])
        old_row = original_by_key.get(item["key"], {})
        source_key = item.get("script", item.get("component"))
        source = None if source_key is None else session.get(source_key)
        if source is not None and not isinstance(
            source, (VerificationScript, DatabaseBacked)
        ):
            raise ValueError(
                "Verification values come from a requirement, registered script or COTS selection."
            )
        if old is not None and callable(old.condition):
            if item["condition"] != old_row.get("condition", ""):
                raise ValueError(
                    "A native condition is read-only. Use replace_binding explicitly."
                )
            condition = old.condition
        elif old is not None and item["condition"] == old_row.get("condition"):
            condition = old.condition
        else:
            condition = restored_expression(item["condition"])
        methods.append(
            VerificationMethod(
                names.get(item["key"], old.name if old else item["key"]),
                condition,
                key=item["key"],
                source=source,
            )
        )
    value.verifications = methods
    value._verification_style = "methods" if "verifications" in row else "condition"


def _mode_changes(session, data, base):
    previous = {row["key"]: row for row in base["power"]["modes"]}
    following = {row["key"]: row for row in data["power"]["modes"]}
    existing = {mode.key: mode for mode in session.power.modes}
    for mode_key, row in following.items():
        if mode_key not in existing:
            session.add_mode(
                Mode(row["name"], row["sunlight"], row["eclipse"], mode_key)
            )
    renamed = [
        (existing[key], row["name"])
        for key, row in following.items()
        if key in existing and row["name"] != previous.get(key, {}).get("name")
    ]
    for mode, _ in renamed:
        session.rename_mode(mode, f"_rename_{uuid4().hex}")
    for mode, name in renamed:
        session.rename_mode(mode, name)
    for mode_key, row in following.items():
        mode = session.resolve_mode(mode_key)
        session.configure_mode(mode, sunlight=row["sunlight"], eclipse=row["eclipse"])
    return [mode for mode in tuple(session.power.modes) if mode.key not in following]


def _load_changes(session, data, base):
    previous = {row["element"]: row for row in base["power"]["loads"]}
    following = {row["element"]: row for row in data["power"]["loads"]}
    for element, row in following.items():
        if row == previous.get(element):
            continue
        old_states = {
            state["key"]: state for state in previous.get(element, {}).get("states", [])
        }
        current = session.power.load_for(session.get(element))
        native_states = (
            {} if current is None else {state.key: state for state in current.states}
        )
        states = tuple(
            native_states[state["key"]]
            if state == old_states.get(state["key"]) and state["key"] in native_states
            else ComponentState(
                state["name"],
                state["watts"],
                state["basis"],
                state["source"],
                state["conditions"],
                state["key"],
            )
            for state in row["states"]
        )
        session.configure_load(
            element,
            quantity=row["quantity"],
            accounting=row["accounting"],
            host=None if not row.get("host") else row["host"],
            rationale=row["rationale"],
            states=states,
            assignments=row["assignments"],
            duties=row.get("duties", previous.get(element, {}).get("duties", {})),
        )
    session.power.loads = [
        load
        for load in session.power.loads
        if load.element.key not in previous or load.element.key in following
    ]
    previous_links = {row["eps"]: row for row in base["power"]["links"]}
    links = {row["eps"]: row for row in data["power"]["links"]}
    for eps in previous_links:
        if eps not in links:
            session.disconnect_power(eps)
    for eps, row in links.items():
        if eps not in previous_links:
            session.connect_power(eps, row["roots"])
        elif row["roots"] != previous_links[eps]["roots"]:
            session.disconnect_power(eps)
            session.connect_power(eps, row["roots"])


def validate_graph(session):
    """Validate table relationships in addition to common native invariants."""
    validate_session(session)
    contexts = {
        session.mission,
        session.external,
        *(row for row in session.elements if row.expandable),
    }
    for element in session.elements:
        definitions = {
            item["model"] for item in allowed_definitions(session, element.owner)
        }
        if element.definition not in definitions:
            raise ValueError(f"{element.id}: choose a type allowed by its parent.")
    for row in session.statements:
        if row.owner not in contexts:
            raise ValueError(f"{row.id}: choose an existing workbook context.")
        if any(
            not isinstance(element, Element)
            or element.selection
            or element.owner is not row.owner
            for element in row.affected
        ):
            raise ValueError(f"{row.id}: affected elements must belong to this table.")
        template = session.catalog.by_requirement.get(row.definition)
        if template is not None:
            expected = session.mission if template.context == "mission" else row.owner
            if (
                row.owner is not expected
                or template.context != "mission"
                and row.owner.role != "eps"
            ):
                raise ValueError(
                    f"{row.id}: this generic requirement belongs to another table."
                )
            for spec in template.parameters:
                parameter = row.parameters.get(spec.name)
                if (
                    parameter is not None
                    and spec.kind == "integer"
                    and parameter.value_type is not int
                ):
                    raise ValueError(
                        f"{row.id}.{spec.name} must retain its declared Integer type."
                    )
        if row.definition and template is None and row.definition not in BUDGET_CLASSES:
            # Trusted custom native subclasses can supply their own definitions.
            if type(row) in (Requirement, Statement, DraftRequirement, DraftStatement):
                raise ValueError(
                    f"{row.id}: choose a registered generic requirement definition."
                )
    for component in session.cots_components:
        if (
            component.owner is None
            or component.owner.role != "eps"
            or component.owner.selection
        ):
            raise ValueError("COTS selections belong to an EPS table.")
        if any(
            requirement.owner is not component.owner
            for requirement in component.requirement_links
        ):
            raise ValueError("Link COTS requirements from the same EPS table.")
    return session


def _editor_defaults(session, data, base):
    """Choose initial domain types for newly populated visual placeholders."""
    known = rows_by_key(base)
    rows = {row["key"]: row for row in data["elements"]}
    for row in data["stakeholders"]:
        if row["key"] not in known and not row.get("type"):
            row["type"] = "Mission Stakeholder"
    for row in data["elements"]:
        if row["key"] in known:
            continue
        if not row.get("definition"):
            owner = row.get("owner")
            if owner in session._objects:
                options = allowed_definitions(session, owner)
            else:
                parent = rows.get(owner, {}).get("definition")
                options = [
                    item.projection()
                    for item in session.catalog.elements
                    if item.parent == parent
                ]
            if not options:
                raise ValueError("Choose a parent that accepts domain elements.")
            row["definition"] = options[0]["model"]
        definition = session.catalog.by_model.get(row["definition"])
        if definition is not None and not row.get("name"):
            row["name"] = definition.name


def apply_projection(
    session, incoming, *, callables, allow_new_ids=True, state_edits=()
):
    """Apply a snapshot's delta to a detached native clone, returning that graph."""
    base = session.to_projection(callables=callables)
    data = normalize_projection(incoming, base)
    _editor_defaults(session, data, base)
    validate_projection(data, allow_new_ids=allow_new_ids)
    _validate_capabilities(data, base, callables)
    target = clone_session(session)
    original = rows_by_key(base)
    following = rows_by_key(data)
    for object_key in original.keys() & following.keys():
        if original[object_key][0] != following[object_key][0]:
            raise ValueError("An existing row cannot move to a different object table.")
    # IDs change through Session.rename so expression links follow them. A
    # temporary namespace permits simultaneous renames and deleted-ID reuse.
    changed_ids = []
    for object_key, (_, old_row) in original.items():
        if object_key not in following:
            target.rename(object_key, f"_removed_{uuid4().hex}")
        elif following[object_key][1]["id"] != old_row["id"]:
            identifier = following[object_key][1]["id"]
            if not identifier:
                raise ValueError("An existing object must retain a nonempty ID.")
            changed_ids.append((object_key, identifier))
            target.rename(object_key, f"_rename_{uuid4().hex}")
    for object_key, identifier in changed_ids:
        target.rename(object_key, identifier)
    # Register owners before their children. Normal add hooks create all generic
    # defaults. Old clients may also submit those generated rows, which are
    # matched by stable key and edited rather than created a second time.
    pending = [
        (table, row)
        for object_key, (table, row) in following.items()
        if object_key not in original
        and table in ("elements", "stakeholders", "components", "scripts")
    ]
    while pending:
        deferred, progress = [], False
        for table, row in pending:
            if row["key"] in target._objects:
                progress = True
                continue
            owner_key = row.get(
                "owner", "external" if table == "stakeholders" else None
            )
            if owner_key is not None and owner_key not in target._objects:
                deferred.append((table, row))
                continue
            value = _new_object(target, table, row, data)
            target.add(
                value, owner=None if owner_key is None else target.get(owner_key)
            )
            progress = True
        if not progress:
            raise ValueError(
                "New elements need existing parents without containment cycles."
            )
        pending = deferred
    removed_modes = _mode_changes(target, data, base)
    for object_key, (table, row) in following.items():
        if table == "statements" and object_key not in target._objects:
            value = _new_object(target, table, row, data)
            target.add(value, owner=target.get(row["context"]))
    _load_changes(target, data, base)
    # Edit metadata and relationships first so explicit unlink-and-delete works
    # atomically. Unchanged cells keep native rewrites and custom class state.
    type_changes, fact_changes = [], []
    for object_key, (table, row) in following.items():
        value = target.get(object_key)
        old = original.get(object_key, (None, {}))[1]
        if table in ("elements", "stakeholders", "scripts") and row.get(
            "name"
        ) != old.get("name"):
            value.name = row.get("name", "")
        if table == "stakeholders":
            value.stakeholder_type = row["type"]
        if table == "elements":
            if row["definition"] != value.definition:
                type_changes.append((value, row["definition"]))
            if row["owner"] != old.get("owner"):
                value.owner = target.get(row["owner"])
        if table == "components":
            if row["product"] != value.product:
                target.substitute_product(value, row["product"])
            value.owner = target.get(row["owner"])
            if old or row["requirements"]:
                value.requirement_links = tuple(
                    target.get(key) for key in row["requirements"]
                )
            if row.get("facts", []) != old.get("facts", []):
                fact_changes.append(
                    (
                        value,
                        tuple(
                            FactReference(**reference)
                            for reference in row.get("facts", [])
                        ),
                    )
                )
            value._facts_present = "facts" in row
        if table == "scripts":
            if row["definition"] != value.definition:
                raise ValueError(
                    "Create a new instance to change an analysis definition."
                )
            changed_interface = any(
                row[field] != old.get(field)
                for field in ("revision", "inputs", "outputs")
            )
            if old and changed_interface:
                described = value.describe()
                if any(
                    row[field] != described[field]
                    for field in ("revision", "inputs", "outputs")
                ):
                    raise ValueError(
                        "An analysis update must use its current registered definition."
                    )
                value.update_definition()
            _configure_parameters(target, value, row, old, data, base)
        if table == "statements":
            if row.get("definition", "") != value.definition:
                raise ValueError(
                    "An existing requirement retains its generic definition."
                )
            if row["kind"] != value.kind:
                if value.definition:
                    raise ValueError(
                        "A generic engineering requirement retains kind Requirement."
                    )
                value.kind = row["kind"]
                if row["kind"] != "Requirement" and type(value) in (
                    Requirement,
                    DraftRequirement,
                ):
                    value.__class__ = (
                        Statement if type(value) is Requirement else DraftStatement
                    )
                elif row["kind"] == "Requirement" and type(value) in (
                    Statement,
                    DraftStatement,
                ):
                    value.__class__ = (
                        Requirement if type(value) is Statement else DraftRequirement
                    )
            if row["context"] != old.get("context"):
                value.owner = target.get(row["context"])
            if row["text"] != old.get("text"):
                value.text = row["text"]
            for field in ("rationale", "origin", "name"):
                if row.get(field, "") != old.get(field, ""):
                    setattr(value, field, row.get(field, ""))
            _configure_parameters(target, value, row, old, data, base)
            if row["sources"] != old.get("sources"):
                value.sources = tuple(target.get(key) for key in row["sources"])
            if row["affected"] != old.get("affected"):
                value.affected = tuple(target.get(key) for key in row["affected"])
            for field, attribute in (
                ("powerScope", "power_scope"),
                ("budgetScope", "budget_scope"),
            ):
                if row.get(field) != old.get(field):
                    setattr(
                        value,
                        attribute,
                        None if row.get(field) is None else target.get(row[field]),
                    )
            if (
                row.get("condition", "") != old.get("condition", "")
                or row.get("verifications") != old.get("verifications")
                or not old
            ):
                _configure_methods(target, value, row, old, data, base)
        value._projection_fields = frozenset(row)
    # Domain remove() supplies protection, including expressions, scopes,
    # children and COTS references. Retry only for dependency order among rows
    # explicitly removed in this same atomic edit.
    pending = [target.get(key) for key in original if key not in following]
    while pending:
        deferred, errors = [], []
        for value in pending:
            try:
                target.remove(value)
            except ValueError as error:
                deferred.append(value)
                errors.append(error)
        if len(deferred) == len(pending):
            raise errors[0]
        pending = deferred
    # State-row bindings are part of the same authored edit. Apply them before
    # fact renames so native reference rewriting also covers their new source.
    for edit in state_edits:
        target.configure_parameter_states(
            edit["target"],
            edit["parameter"],
            values=edit.get("values"),
            last_edited=edit.get("lastEdited"),
            merge=edit.get("merge", False),
        )
    for value, references in fact_changes:
        target.configure_facts(value, references)
    for mode in removed_modes:
        target.remove_mode(mode)
    for value, definition in type_changes:
        target.retype(value, definition)
    variables = []
    for variable in data["variables"]:
        variables.append(
            Variable(variable["name"], TYPES[variable["type"]], variable.get("unit"))
        )
    target.variables = variables
    # Native generated parameters remain visible even when an older client has
    # not yet installed the returned canonical projection.
    for value in target.statements:
        for parameter in value.parameters.values():
            target.register_parameter(parameter)
    target._model_state_present = True
    return validate_graph(target)
