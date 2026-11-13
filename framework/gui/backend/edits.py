"""Translate editor requests into the same public calls used in Python."""

from framework import models


def reference(path):
    return f"mission.get({path!r})"


def classes(mission):
    result = {
        name: (cls, f"_gui_models.{name}")
        for name in models.__all__
        if isinstance(cls := getattr(models, name), type)
        and issubclass(cls, models.ModelObject)
        and cls not in (models.Mission, models.ModelObject, models.VerificationCondition)
    }
    for item in mission.walk():
        cls = type(item)
        if cls not in [entry[0] for entry in result.values()] and cls is not models.Mission:
            result[f"custom:{item.path}"] = (cls, f"type({reference(item.path)})")
    return result


def allocation_targets(owner, cls):
    if cls is models.ModeAllocation:
        return owner.parent.spacecraft_modes if isinstance(owner, models.ComponentMode) and owner.parent else ()
    if cls is models.StateAllocation:
        return owner.states if isinstance(owner, models.ComponentMode) else ()
    return ()


def construct(cls, name, owner, target=None):
    if cls in (models.ModeAllocation, models.StateAllocation):
        targets = allocation_targets(owner, cls)
        if target is None:
            if not targets:
                raise ValueError("Create an allocation target first.")
            target = targets[0]
        return cls(name, target)
    return cls(name)


def allowed_types(mission, owner):
    result = []
    for key, (cls, _) in classes(mission).items():
        try:
            if owner.accepts(construct(cls, "_new", owner)):
                kind = "requirement" if issubclass(cls, models.Requirement) else "mode" if issubclass(cls, (models.SpacecraftMode, models.ComponentMode, models.ComponentState, models.TimeAllocation)) else "external" if issubclass(cls, (models.Stakeholder, models.ThirdParty)) else "element"
                result.append({"key": key, "name": cls.__name__, "kind": kind, "targets": [item.path for item in allocation_targets(owner, cls)]})
        except (TypeError, ValueError, AttributeError):
            continue
    return result


def properties(mission, owner, definitions, calls):
    names = [item["name"] for item in definitions]
    if len(set(names)) != len(names):
        raise ValueError("Parameter names must be unique.")
    for definition in definitions:
        name = definition["name"]
        source, unit = definition.get("expression"), definition.get("unit", "")
        location = f"{reference(owner.path)}.{name}"
        if name not in owner.properties:
            prop = owner.define(name, models.Property(source, unit))
            calls.append(f"{reference(owner.path)}.define({name!r}, _gui_models.Property({source!r}, {unit!r}))")
        else:
            prop = owner.properties[name]
            if prop.expression != source:
                prop.expression = source
                calls.append(f"{location}.expression = {source!r}")
            if str(prop.unit) != unit:
                prop.unit = unit
                calls.append(f"{location}.unit = {unit!r}")
        bindings = definition.get("bindings")
        if bindings is None:
            continue
        overrides = {mission.get(item["mode"]): item.get("expression") for item in bindings}
        if len(overrides) != len(bindings):
            raise ValueError("Choose each override mode once per parameter.")
        for mode in tuple(prop.modes):
            if mode not in overrides:
                prop.unbind(mode)
                calls.append(f"{location}.unbind({reference(mode.path)})")
        for mode, expression in overrides.items():
            if mode not in prop.modes or prop.modes[mode] != expression:
                prop.bind(mode, expression)
                calls.append(f"{location}.bind({reference(mode.path)}, {expression!r})")


def apply(mission, command):
    """Apply one transaction and return its executable Python calls."""
    calls, selected = [], command.get("path")
    action = command["action"]
    if action == "create":
        owner = mission.get(command["owner"])
        cls, source = classes(mission)[command["type"]]
        target = mission.get(command["target"]) if command.get("target") else None
        child = owner.add(construct(cls, command["name"], owner, target))
        arguments = repr(child.name)
        if cls in (models.ModeAllocation, models.StateAllocation):
            actual = child.spacecraft_mode if cls is models.ModeAllocation else child.state
            arguments += f", {reference(actual.path)}"
        calls.append(f"{reference(owner.path)}.add({source}({arguments}))")
        selected = child.path
    elif action == "remove":
        item = mission.get(command["path"])
        parent = item.parent
        if parent is None:
            raise ValueError("The Mission cannot be removed.")
        calls.append(f"{reference(parent.path)}.remove({item.name!r})")
        parent.remove(item)
        selected = None
    elif action == "update":
        owner = mission.get(command["path"])
        properties(mission, owner, command.get("properties", []), calls)
        if isinstance(owner, models.Requirement):
            for field in ("statement", "rationale"):
                if field in command and getattr(owner, field) != command[field]:
                    if not isinstance(command[field], str):
                        raise TypeError(f"{field.title()} must be text.")
                    setattr(owner, field, command[field])
                    calls.append(f"{reference(owner.path)}.{field} = {command[field]!r}")
            if "conditions" in command:
                definitions = command["conditions"]
                names = [item["name"] for item in definitions]
                if len(set(names)) != len(names):
                    raise ValueError("Condition names must be unique.")
                for condition in owner.conditions:
                    if condition.name not in names:
                        owner.remove(condition)
                        calls.append(f"{reference(owner.path)}.remove({condition.name!r})")
                for definition in definitions:
                    name = definition["name"]
                    if name not in [child.name for child in owner.conditions]:
                        condition = owner.add(models.VerificationCondition(name, models.Property(), models.Property(), definition["expression"]))
                        calls.append(f"{reference(owner.path)}.add(_gui_models.VerificationCondition({name!r}, _gui_models.Property(), _gui_models.Property(), {definition['expression']!r}))")
                    else:
                        condition = owner.child(name)
                        if condition.expression != definition["expression"]:
                            condition.expression = definition["expression"]
                            calls.append(f"{reference(condition.path)}.expression = {condition.expression!r}")
                    properties(mission, condition, definition.get("properties", []), calls)
        if "imports" in command:
            if owner is not mission:
                raise ValueError("Imports belong to the Mission.")
            for source in command["imports"]:
                before = tuple(mission.imports)
                mission.add_import(source)
                if tuple(mission.imports) != before:
                    calls.append(f"mission.add_import({source!r})")
    else:
        raise ValueError("Unknown model operation.")
    return calls, selected
