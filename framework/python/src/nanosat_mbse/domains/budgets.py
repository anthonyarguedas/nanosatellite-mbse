"""Native spacecraft power, mass and volume rules and editable requirements."""

from __future__ import annotations

import ast
from dataclasses import dataclass, replace

from ..core.configuration import LoadConnection, LoadProfile
from ..core.elements import Subsystem
from ..core.expressions import finite_number
from ..core.requirements import Parameter, Requirement
from ..core.verification import DraftExpression, PendingValue, VerificationMethod


POWER_INPUTS = ("sunlight_power_W", "eclipse_power_W", "sunlight_duty", "eclipse_duty")
POWER_MODELS = ("PowerBudgetModel::PowerLimit", "PowerBudgetModel::ComponentPowerLimit")


@dataclass(frozen=True)
class Resource:
    name: str
    unit: str
    value: str
    limit: str
    allocated: str
    model: str
    prefixes: tuple


RESOURCES = (
    Resource(
        "mass",
        "kg",
        "mass_kg",
        "mass_allocation_kg",
        "allocated_mass_kg",
        "Mass",
        ("MAS", "MSS", "MSC"),
    ),
    Resource(
        "volume",
        "m^3",
        "volume_m3",
        "volume_allocation_m3",
        "allocated_volume_m3",
        "Volume",
        ("VOL", "VLS", "VLC"),
    ),
)


class PowerLimit(Requirement):
    model = POWER_MODELS[0]


class ComponentPowerLimit(PowerLimit):
    model = POWER_MODELS[1]


class MassLimit(Requirement):
    model = "ResourceBudgetModel::MassLimit"


class ComponentMassLimit(MassLimit):
    model = "ResourceBudgetModel::ComponentMassLimit"


class VolumeLimit(Requirement):
    model = "ResourceBudgetModel::VolumeLimit"


class ComponentVolumeLimit(VolumeLimit):
    model = "ResourceBudgetModel::ComponentVolumeLimit"


BUDGET_CLASSES = {
    cls.model: cls
    for cls in (
        PowerLimit,
        ComponentPowerLimit,
        MassLimit,
        ComponentMassLimit,
        VolumeLimit,
        ComponentVolumeLimit,
    )
}


@dataclass(frozen=True)
class BudgetScope:
    target: object
    owner: object
    parent: object
    kind: str
    affected: tuple = ()

    @property
    def key(self):
        return self.target.key


def _spacecraft(element):
    while element is not None:
        if element.role in ("bus", "payload"):
            return True
        element = element.owner
    return False


def spacecraft_components(session):
    return tuple(
        element for element in session.physical_components if _spacecraft(element)
    )


def power_scopes(session):
    roots = tuple(
        element
        for element in session.elements
        if element.owner is session.mission and element.role in ("bus", "payload")
    )
    subsystems = tuple(
        element
        for element in session.elements
        if isinstance(element, Subsystem) and _spacecraft(element)
    )
    return (
        BudgetScope(session.mission, session.mission, None, "system", roots),
        *(
            BudgetScope(element, element, session.mission, "subsystem")
            for element in subsystems
        ),
        *(
            BudgetScope(element, element.owner, element.owner, "component", (element,))
            for element in spacecraft_components(session)
        ),
    )


def load_for(session, element):
    return session.power.load_for(element) or LoadProfile(
        element, accounting=element.default_accounting
    )


def power_limit_for(session, scope):
    return next(
        (
            row
            for row in session.requirements
            if row.definition in POWER_MODELS and row.power_scope is scope
        ),
        None,
    )


def _power_children(session, row):
    return tuple(
        scope
        for scope in power_scopes(session)
        if scope.parent is row.power_scope
        and (
            scope.kind != "component"
            or load_for(session, scope.target).accounting == "counted"
            or power_limit_for(session, scope.target) is not None
        )
    )


def power_allocation_expression(session, row, *, skip_missing=False):
    children = sorted(_power_children(session, row), key=lambda scope: scope.key)
    requirements = [power_limit_for(session, scope.target) for scope in children]
    if not skip_missing and any(row is None for row in requirements):
        return "None"
    references = [f"{row.id}.power_limit_W" for row in requirements if row is not None]
    return f"sum([{', '.join(references)}])" if references else "0"


def resource_for(row):
    return next(
        (
            resource
            for resource in RESOURCES
            if row.definition
            in (
                f"ResourceBudgetModel::{resource.model}Limit",
                f"ResourceBudgetModel::Component{resource.model}Limit",
            )
        ),
        None,
    )


def resource_scopes(session):
    return tuple(
        scope
        for scope in power_scopes(session)
        if (
            bool(scope.affected)
            if scope.kind == "system"
            else getattr(scope.target, "default_accounting", "counted") != "host"
        )
    )


def resource_limit_for(session, scope, resource):
    return next(
        (
            row
            for row in session.requirements
            if resource_for(row) == resource and row.budget_scope is scope
        ),
        None,
    )


def resource_sum_expression(session, row, name, *, skip_missing=False):
    resource = resource_for(row)
    children = sorted(
        (
            scope
            for scope in resource_scopes(session)
            if scope.parent is row.budget_scope
        ),
        key=lambda scope: scope.key,
    )
    requirements = [
        resource_limit_for(session, scope.target, resource) for scope in children
    ]
    if not skip_missing and any(row is None for row in requirements):
        return "None"
    field = resource.limit if name == resource.allocated else resource.value
    references = [f"{row.id}.{field}" for row in requirements if row is not None]
    return f"sum([{', '.join(references)}])" if references else "0"


def _source(parameter):
    if parameter is None:
        return None
    if isinstance(parameter.expression, DraftExpression):
        return parameter.expression.source
    if parameter.expression is not None:
        return parameter.expression
    return None if parameter.value is None else repr(parameter.value)


def _rule(session, scope, model):
    from ..core.session import SeedRule

    return SeedRule(scope.owner.key, scope.key, model)


def remember_budget_defaults(session):
    """Remember legacy initialized scopes, including intentionally missing rows."""
    if session.power.modes:
        for scope in power_scopes(session):
            if (
                scope.kind != "component"
                or load_for(session, scope.target).accounting == "counted"
                or power_limit_for(session, scope.target)
            ):
                model = (
                    POWER_MODELS[1] if scope.kind == "component" else POWER_MODELS[0]
                )
                session.seed_history.add(_rule(session, scope, model))
    if session.resource_budgets:
        for scope in resource_scopes(session):
            for resource in RESOURCES:
                model = f"ResourceBudgetModel::{'Component' if scope.kind == 'component' else ''}{resource.model}Limit"
                session.seed_history.add(_rule(session, scope, model))


def seed_power_limits(session, scopes=None):
    subjects = power_scopes(session)
    selected = tuple(
        scope
        for scope in subjects
        if (scopes is None or scope.target in scopes)
        and (
            scope.kind != "component"
            or load_for(session, scope.target).accounting == "counted"
        )
    )
    if not selected or not session.power.modes:
        return ()
    defaults = {
        row
        for row in session.requirements
        if row.definition == POWER_MODELS[0]
        and _source(row.parameters.get("allocated_power_W"))
        in (
            power_allocation_expression(session, row),
            power_allocation_expression(session, row, skip_missing=True),
        )
    }
    created = []
    for scope in selected:
        component = scope.kind == "component"
        cls = ComponentPowerLimit if component else PowerLimit
        rule = _rule(session, scope, cls.model)
        if power_limit_for(session, scope.target) is not None:
            session.seed_history.add(rule)
            continue
        if rule in session.seed_history:
            continue
        row = cls(
            session.next_id(
                "Requirement",
                "PWR" if scope.kind == "system" else "PWC" if component else "PWS",
            ),
            f"The {'spacecraft' if scope.kind == 'system' else 'installed component' if component else 'subsystem'} power draw shall not exceed $$power_limit_W$$.",
            key=session.available_key(f"power-{scope.key}"),
            owner=scope.owner,
            affected=scope.affected,
            definition=cls.model,
            parameters=(
                Parameter("power_limit_W", unit="W"),
                Parameter(
                    "draw_power_W", unit="W", expression="PowerAllocation.draw_power_W"
                ),
                *((Parameter("allocated_power_W", unit="W"),) if not component else ()),
            ),
            verifications=(
                VerificationMethod(
                    "condition",
                    "power_limit_W >= 0 and draw_power_W >= 0 and draw_power_W <= power_limit_W"
                    if component
                    else "power_limit_W >= 0 and allocated_power_W >= 0 and allocated_power_W <= power_limit_W and draw_power_W >= 0 and draw_power_W <= power_limit_W",
                    key="condition",
                ),
            ),
        )
        row.power_scope = scope.target
        session.add(row, owner=scope.owner, initialize=False)
        session.seed_history.add(rule)
        if not component:
            defaults.add(row)
        created.append(row)
    by_scope = {scope.target: scope for scope in subjects}
    for row in tuple(
        row for row in session.requirements if row.definition in POWER_MODELS
    ):
        scope = by_scope.get(row.power_scope)
        parent = (
            power_limit_for(session, scope.parent)
            if scope is not None and scope.parent is not None
            else None
        )
        if parent is not None:
            row.derive_from(parent)
        if row.power_scope is session.mission:
            row.affected = subjects[0].affected
        if row in defaults:
            row.set_expression(
                "allocated_power_W", power_allocation_expression(session, row)
            )
    expand_power_allocations(session)
    return tuple(created)


def seed_resource_budgets(session, scopes=None):
    subjects = resource_scopes(session)
    selected = tuple(
        scope for scope in subjects if scopes is None or scope.target in scopes
    )
    if not selected:
        return ()
    defaults = {}
    for row in session.requirements:
        resource = resource_for(row)
        if resource is not None and "::Component" not in row.definition:
            defaults[row] = tuple(
                name
                for name in (resource.value, resource.allocated)
                if _source(row.parameters.get(name))
                in (
                    resource_sum_expression(session, row, name),
                    resource_sum_expression(session, row, name, skip_missing=True),
                )
            )
    created = []
    for resource in RESOURCES:
        for scope in selected:
            component = scope.kind == "component"
            model = f"ResourceBudgetModel::{'Component' if component else ''}{resource.model}Limit"
            rule = _rule(session, scope, model)
            if resource_limit_for(session, scope.target, resource) is not None:
                session.seed_history.add(rule)
                continue
            if rule in session.seed_history:
                continue
            cls = BUDGET_CLASSES[model]
            subject = (
                "spacecraft"
                if scope.kind == "system"
                else "installed component"
                if component
                else "subsystem"
            )
            row = cls(
                session.next_id(
                    "Requirement",
                    resource.prefixes[
                        0 if scope.kind == "system" else 2 if component else 1
                    ],
                ),
                f"The {subject} {resource.name} shall not exceed $${resource.limit}$$.",
                key=session.available_key(f"{resource.name}-{scope.key}"),
                owner=scope.owner,
                affected=scope.affected,
                definition=model,
                rationale=f"Enter total installed {resource.name}, including quantity and auxiliaries, using disjoint hardware accounting boundaries."
                if component
                else "Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.",
                parameters=tuple(
                    Parameter(name, unit=resource.unit)
                    for name in (
                        resource.limit,
                        resource.value,
                        *((resource.allocated,) if not component else ()),
                    )
                ),
                verifications=(
                    VerificationMethod(
                        "condition",
                        f"{resource.limit} >= 0 and {resource.value} >= 0 and {resource.value} <= {resource.limit}"
                        + (
                            ""
                            if component
                            else f" and {resource.allocated} >= 0 and {resource.allocated} <= {resource.limit}"
                        ),
                        key="condition",
                    ),
                ),
            )
            row.budget_scope = scope.target
            session.add(row, owner=scope.owner, initialize=False)
            session.seed_history.add(rule)
            if not component:
                defaults[row] = (resource.value, resource.allocated)
            created.append(row)
    by_scope = {scope.target: scope for scope in subjects}
    for row in tuple(session.requirements):
        resource = resource_for(row)
        if resource is None:
            continue
        scope = by_scope.get(row.budget_scope)
        parent = (
            resource_limit_for(session, scope.parent, resource)
            if scope is not None and scope.parent is not None
            else None
        )
        if parent is not None:
            row.derive_from(parent)
        if row.budget_scope is session.mission:
            row.affected = by_scope[session.mission].affected
        for name in defaults.get(row, ()):
            row.set_expression(name, resource_sum_expression(session, row, name))
    session.resource_budgets = True
    session._resource_budgets_present = True
    return tuple(created)


def _replace_alias(source, replacement):
    if not isinstance(source, str):
        return source
    try:
        tree = ast.parse(source.strip(), mode="eval")
    except (SyntaxError, ValueError):
        return source
    # Token matching keeps comments, literals and invalid drafts intact.
    if not any(
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "PowerAllocation"
        and node.attr == "allocated_power_W"
        for node in ast.walk(tree)
    ):
        return source
    import io
    import tokenize

    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    significant = [
        token
        for token in tokens
        if token.type
        not in (
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.COMMENT,
        )
    ]
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    changes = []
    for first, dot, field in zip(significant, significant[1:], significant[2:]):
        if (
            first.type == tokenize.NAME
            and first.string == "PowerAllocation"
            and dot.string == "."
            and field.string == "allocated_power_W"
        ):
            start = offsets[first.start[0] - 1] + first.start[1]
            end = offsets[field.end[0] - 1] + field.end[1]
            standalone = source.strip() == source[start:end]
            value = (
                "None if True else 0"
                if replacement == "None" and not standalone
                else replacement
            )
            changes.append((start, end, value if standalone else f"({value})"))
    for start, end, value in reversed(changes):
        source = source[:start] + value + source[end:]
    return source


def expand_power_allocations(session):
    for row in session.requirements:
        if row.definition not in POWER_MODELS:
            continue
        replacement = power_allocation_expression(session, row)
        for name, parameter in tuple(row.parameters.items()):
            if isinstance(parameter.expression, str):
                updated = _replace_alias(parameter.expression, replacement)
                if updated != parameter.expression:
                    row.set_expression(name, updated)
        row.verifications = tuple(
            replace(method, condition=_replace_alias(method.condition, replacement))
            for method in row.verifications
        )


def reconcile_defaults(session, *, generic=True, budgets=True):
    """Explicitly introduce catalog additions and legacy budgets once per scope.

    Import alone is hook-free. Remembered defaults protect later deletions.
    """
    if generic:
        for owner in session.elements:
            remembered = session.requirement_seeds.get(owner, ())
            templates = tuple(
                template
                for template in session.catalog.requirements_for(owner.definition)
                if template.auto_populate and template.model not in remembered
            )
            if templates:
                session._seed_templates(owner, templates)
    if budgets:
        seed_resource_budgets(session)
        seed_power_limits(session)
        expand_power_allocations(session)
    return session


def after_element_added(session, element):
    if getattr(element, "selection", False) or not _spacecraft(element):
        return
    descendants = {element}
    changed = True
    while changed:
        before = len(descendants)
        descendants.update(
            value for value in session.elements if value.owner in descendants
        )
        changed = len(descendants) != before
    # Parent requirements update their unchanged default sums, while only new
    # scopes receive allocations. Existing deletions remain remembered.
    scopes = (*descendants, session.mission)
    seed_resource_budgets(session, scopes)
    seed_power_limits(session, scopes)


def power_allocation(context, row, name):
    session = context.session
    if row.definition not in POWER_MODELS or name not in (
        "allocated_power_W",
        "draw_power_W",
    ):
        raise ValueError("PowerAllocation belongs to a power limit requirement.")
    children = _power_children(session, row)
    if name == "allocated_power_W" or children:
        total = 0
        for child in children:
            requirement = power_limit_for(session, child.target)
            if requirement is None:
                raise PendingValue(f"Define a power limit for {child.target.id}.")
            value = context.parameter(
                requirement,
                "power_limit_W" if name == "allocated_power_W" else "draw_power_W",
            )
            if value < 0:
                raise ValueError(f"{requirement.id} power must be nonnegative.")
            total += value
        return finite_number(total)
    components = tuple(
        element
        for element in spacecraft_components(session)
        if row.power_scope is session.mission or in_roots(element, (row.power_scope,))
    )
    if not components:
        raise PendingValue("Define the components for this power limit.")
    total = 0
    for element in components:
        load = load_for(session, element)
        if load.accounting != "counted":
            continue
        total += component_draw(load, context.mode)
    return finite_number(total)


def in_roots(element, roots):
    while element is not None:
        if element in roots:
            return True
        element = element.owner
    return False


def component_draw(load, mode):
    if mode is None:
        raise PendingValue("Select a spacecraft mode to calculate power draw.")
    state = load.assignments.get(mode)
    if state is None or state.watts is None:
        raise PendingValue(f"Select a state and power draw for {load.element.id}.")
    return finite_number(load.quantity) * finite_number(state.watts)


def load_budget(context, row, name):
    session = context.session
    link = next((link for link in session.power.links if link.eps is row.owner), None)
    if link is None:
        raise ValueError(
            "Connect this EPS to a load budget before using LoadBudget inputs."
        )
    if name not in ("sunlight_power_W", "eclipse_power_W"):
        raise ValueError("Unknown LoadBudget input.")
    period = "sunlight" if name == "sunlight_power_W" else "eclipse"
    weights = [getattr(mode, period) for mode in session.power.modes]
    if (
        not weights
        or any(weight is None for weight in weights)
        or abs(sum(weights) - 100) > 1e-6
    ):
        raise PendingValue(f"{period.capitalize()} mode fractions must total 100%.")
    components = tuple(
        element
        for element in spacecraft_components(session)
        if in_roots(element, link.roots)
    )
    if not components:
        raise PendingValue("The selected scope has no spacecraft components.")
    total = 0
    for mode in session.power.modes:
        weight = getattr(mode, period)
        if weight == 0:
            continue
        for element in components:
            load = load_for(session, element)
            if load.accounting == "counted":
                total += component_draw(load, mode) * weight / 100
    return finite_number(total)


def default_power_roots(session, eps):
    return tuple(
        element
        for element in session.elements
        if element is eps.owner
        or (element.owner is session.mission and element.role == "payload")
    )


def connect_power(session, eps, roots=None):
    eps = session.get(eps)
    roots = (
        default_power_roots(session, eps)
        if roots is None
        else tuple(session.get(root) for root in roots)
    )
    if any(link.eps is eps for link in session.power.links):
        return next(link for link in session.power.links if link.eps is eps)
    if (
        eps.role != "eps"
        or not roots
        or any(
            root.owner is not session.mission or root.role not in ("bus", "payload")
            for root in roots
        )
    ):
        raise ValueError("Connect an EPS to existing bus or payload roots.")
    row = next(
        (
            row
            for row in eps.requirements
            if row.definition == "FrameworkRequirements::LoadEnergy"
        ),
        None,
    )
    if row is None:
        raise ValueError(
            "This EPS needs the generic LoadEnergy requirement before connecting a budget."
        )
    previous = {name: row.parameters[name] for name in POWER_INPUTS}
    link = LoadConnection(eps, roots, previous)
    session.power.links.append(link)
    row.set_expression("sunlight_power_W", "LoadBudget.sunlight_power_W")
    row.set_expression("eclipse_power_W", "LoadBudget.eclipse_power_W")
    row.set_expression("sunlight_duty", "1")
    row.set_expression("eclipse_duty", "1")
    return link


def validate_parameter_binding(session, row, parameter):
    if (
        row.definition != "FrameworkRequirements::LoadEnergy"
        or parameter.name not in POWER_INPUTS
    ):
        return
    if not any(link.eps is row.owner for link in session.power.links):
        return
    expected = dict(
        zip(
            POWER_INPUTS,
            ("LoadBudget.sunlight_power_W", "LoadBudget.eclipse_power_W", "1", "1"),
        )
    )
    if _source(parameter) != expected[parameter.name]:
        raise ValueError(
            "Disconnect the EPS budget before changing its managed LoadEnergy inputs."
        )


def protect_budget_removal(session, value):
    if getattr(
        value, "definition", None
    ) == "FrameworkRequirements::LoadEnergy" and any(
        link.eps is value.owner for link in session.power.links
    ):
        raise ValueError(
            "Disconnect the EPS budget before deleting its LoadEnergy requirement."
        )


def disconnect_power(session, eps):
    eps = session.get(eps)
    link = next((link for link in session.power.links if link.eps is eps), None)
    if link is None:
        return
    row = next(
        (
            row
            for row in eps.requirements
            if row.definition == "FrameworkRequirements::LoadEnergy"
        ),
        None,
    )
    if row is not None:
        row._parameters.update(link.previous)
    session.power.links.remove(link)


def configure_load(session, element, **changes):
    element = session.get(element)
    if element not in spacecraft_components(session):
        raise ValueError("Choose a physical spacecraft component.")
    if "host" in changes and changes["host"] is not None:
        changes["host"] = session.get(changes["host"])
    if "states" in changes:
        changes["states"] = tuple(changes["states"])
    previous = load_for(session, element)
    load = replace(previous, **changes)
    if "states" in changes and "assignments" not in changes:
        states = {state.key: state for state in load.states}
        load.assignments = {
            mode: states[state.key]
            for mode, state in previous.assignments.items()
            if state.key in states
        }
    if "assignments" in changes:
        states = {state.key: state for state in load.states}
        states.update({state.name: state for state in load.states})
        assignments = {}
        for mode, state in changes["assignments"].items():
            selected_mode = session.resolve_mode(mode)
            if isinstance(state, str) and state not in states:
                if "states" in changes and any(
                    old.key == state for old in previous.states
                ):
                    continue
                raise ValueError("Select an existing component state for each mode.")
            selected_state = states[state] if isinstance(state, str) else state
            assignments[selected_mode] = selected_state
        load.assignments = assignments
    validate_load(session, load)
    existing = session.power.load_for(element)
    if existing is None:
        session.power.loads.append(load)
    else:
        session.power.loads[session.power.loads.index(existing)] = load
    seed_power_limits(session)
    return load


def _unique(values, label):
    if len(set(values)) != len(values):
        raise ValueError(f"{label} must be unique.")


def validate_load(session, load):
    if load.element not in spacecraft_components(session) or load.accounting not in (
        "counted",
        "host",
        "excluded",
    ):
        raise ValueError(
            "Choose a physical spacecraft component and accounting boundary."
        )
    if load.element.default_accounting == "host" and load.accounting == "counted":
        raise ValueError("Software demand belongs to its execution host.")
    if type(load.quantity) is not int or not 1 <= load.quantity <= 1_000_000:
        raise ValueError("Quantity must be an integer from 1 to 1,000,000.")
    if load.host is not None and (
        load.host is load.element
        or load.host not in spacecraft_components(session)
        or not load.host.definition.endswith("::ProcessorAndMemory")
    ):
        raise ValueError("Choose an existing processor and memory execution host.")
    if len(load.states) > 32:
        raise ValueError("Use up to 32 component states.")
    _unique([state.key for state in load.states], "Component state keys")
    _unique(
        [state.name.strip().lower() for state in load.states], "Component state names"
    )
    for state in load.states:
        if not state.name.strip() or state.basis not in (
            "estimated",
            "typical",
            "maximum",
            "measured",
        ):
            raise ValueError("Name each component state and its value meaning.")
        if state.watts is not None and finite_number(state.watts) < 0:
            raise ValueError("Component power draw must be nonnegative.")
    for mode, state in load.assignments.items():
        if mode not in session.power.modes or state not in load.states:
            raise ValueError(
                "Mode mappings must reference existing modes and component states."
            )


def validate_budgets(session):
    if len(session.power.modes) > 24 or len(session.power.loads) > 1000:
        raise ValueError("Use up to 24 spacecraft modes and 1,000 load profiles.")
    _unique([mode.key for mode in session.power.modes], "Mode keys")
    _unique([mode.name.strip().lower() for mode in session.power.modes], "Mode names")
    for mode in session.power.modes:
        if not mode.name.strip():
            raise ValueError("Name each spacecraft mode.")
        for period in ("sunlight", "eclipse"):
            value = getattr(mode, period)
            if value is not None and not 0 <= finite_number(value) <= 100:
                raise ValueError("Mode fractions must be between 0 and 100 percent.")
    _unique(
        [load.element.key for load in session.power.loads], "Component load records"
    )
    for load in session.power.loads:
        validate_load(session, load)
    scopes = {scope.target: scope for scope in power_scopes(session)}
    hardware_scopes = {scope.target: scope for scope in resource_scopes(session)}
    if session._resource_budgets_present and session.resource_budgets is not True:
        raise ValueError("Invalid resource budget initialization marker.")
    identities = set()
    for row in session.statements:
        resource = resource_for(row)
        if row.definition not in POWER_MODELS and resource is None:
            if row.power_scope is not None or row.budget_scope is not None:
                raise ValueError("Scope references belong to budget requirements.")
            continue
        target = row.power_scope if resource is None else row.budget_scope
        if not isinstance(row, Requirement):
            raise ValueError("Budget definitions belong to Requirement instances.")
        scope = (scopes if resource is None else hardware_scopes).get(target)
        identity = ("power" if resource is None else resource.name, target)
        if scope is None or scope.owner is not row.owner or identity in identities:
            raise ValueError("Define each budget once in its matching scope.")
        identities.add(identity)
        if len(row.affected) != len(scope.affected) or set(row.affected) != set(
            scope.affected
        ):
            raise ValueError("Budget requirement assignments follow their scope.")
        component = "::Component" in row.definition
        if component != (scope.kind == "component"):
            raise ValueError("Use the budget requirement type for its scope.")
        parent = (
            power_limit_for(session, scope.parent)
            if resource is None
            else resource_limit_for(session, scope.parent, resource)
        )
        if parent is not None and parent not in row.sources:
            raise ValueError("Retain the parent budget requirement as a source.")
    _unique([link.eps.key for link in session.power.links], "EPS budget connections")
    for link in session.power.links:
        if (
            link.eps.session is not session
            or link.eps.role != "eps"
            or not link.roots
            or any(
                root.session is not session
                or root.owner is not session.mission
                or root.role not in ("bus", "payload")
                for root in link.roots
            )
        ):
            raise ValueError("Connect existing EPS, bus and payload objects.")
        _unique([root.key for root in link.roots], "Load domain roots")
        row = next(
            (
                row
                for row in link.eps.requirements
                if row.definition == "FrameworkRequirements::LoadEnergy"
            ),
            None,
        )
        expected = (
            "LoadBudget.sunlight_power_W",
            "LoadBudget.eclipse_power_W",
            "1",
            "1",
        )
        if row is None or any(
            _source(row.parameters.get(name)) != value
            for name, value in zip(POWER_INPUTS, expected)
        ):
            raise ValueError(
                "Disconnect the EPS budget before changing its managed LoadEnergy inputs."
            )
        if set(link.previous) != set(POWER_INPUTS) or any(
            not isinstance(parameter, Parameter) for parameter in link.previous.values()
        ):
            raise ValueError("Retain each previous LoadEnergy input binding.")
    return session
