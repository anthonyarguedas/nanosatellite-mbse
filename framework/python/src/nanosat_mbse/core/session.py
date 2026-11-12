"""Authoritative native object registry, relationships and creation lifecycle."""

from __future__ import annotations

import io
import re
import tokenize
from dataclasses import dataclass, replace

from ..catalogs.database import DatabaseBacked, TabularDatabase
from ..catalogs.framework import default_catalog
from .configuration import Mode, PowerModel, ScriptConfiguration, Variable
from .elements import Component, Element, Stakeholder
from .identity import ALL_MODES
from .requirements import Requirement, Statement
from .verification import DraftExpression, restored_expression


@dataclass(frozen=True)
class SeedRule:
    owner: str
    subject: str
    rule: str


def expression_source(parameter, *, callables=None):
    if parameter.expression is not None:
        if isinstance(parameter.expression, DraftExpression):
            return parameter.expression.source
        if not isinstance(parameter.expression, str):
            if callables is None:
                raise TypeError(
                    "Supply a trusted CallableRegistry to project native bindings."
                )
            return None
        return parameter.expression
    return None if parameter.value is None else repr(parameter.value)


def _rewrite(source, old, new):
    """Rewrite qualified IDs while preserving strings, spelling and invalid drafts."""
    if not isinstance(source, str):
        return source
    tokens = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            tokens.append(token)
    except (tokenize.TokenError, IndentationError):
        pass
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    replacements = []
    meaningful = [
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
    for index, token in enumerate(meaningful[:-1]):
        if (
            token.type == tokenize.NAME
            and token.string == old
            and meaningful[index + 1].string == "."
        ):
            replacements.append(
                (
                    offsets[token.start[0] - 1] + token.start[1],
                    offsets[token.end[0] - 1] + token.end[1],
                )
            )
    for start, end in reversed(replacements):
        source = source[:start] + new + source[end:]
    return source


class Session:
    """An editable graph of actual elements, requirements and script bindings.

    The registry owns identities. The browser projection is produced on demand
    and is never retained as the backing model. Restoration suppresses hooks.
    """

    def __init__(
        self,
        *,
        catalog=None,
        database=None,
        name="",
        key=None,
        verification_registry=None,
    ):
        from uuid import uuid4
        from ..domains.mission import External, Mission
        from ..verifications.registry import default_registry

        self.key = str(uuid4()) if key is None else key
        self.name = name
        self.catalog = default_catalog() if catalog is None else catalog
        self.database = TabularDatabase() if database is None else database
        self.verification_registry = (
            default_registry()
            if verification_registry is None
            else verification_registry
        )
        self._execution_evidence = None
        self._objects = {}
        self.seed_history = set()
        self._initialized = set()
        self._initializing = set()
        self.requirement_seeds = {}
        self._requirement_seeds_present = False
        self._model_state_present = True
        self.resource_budgets = False
        self._resource_budgets_present = False
        self.variables = [Variable(name) for name in ("x", "y", "z", "a")]
        self.power = PowerModel()
        self.mission = Mission("MISSION", key="mission")
        self.external = External("EXTERNAL", key="external")
        self._register(self.mission)
        self._register(self.external)

    @classmethod
    def from_projection(cls, data, **kwargs):
        from ..persistence.projection import from_projection

        return from_projection(data, session_class=cls, **kwargs)

    def to_projection(self, *, callables=None):
        from ..persistence.projection import to_projection

        return to_projection(self, callables=callables)

    @classmethod
    def open(cls, path, *, repository=None, **providers):
        """Open trusted Python session source without running its analyses."""
        from ..persistence.repository import SessionRepository

        if repository is not None and providers:
            raise TypeError("Configure providers on the supplied session repository.")
        repository = (
            SessionRepository(**providers) if repository is None else repository
        )
        session = repository.load(path, session_class=cls)
        session.reconcile_defaults()
        return session

    @property
    def storage(self):
        """Path and revision of the last successful load or save, or None."""
        return getattr(self, "_storage_status", None)

    def save(self, path=None, *, expected_revision=None, repository=None, create=False):
        """Save configuration with optimistic revision checks and atomic writes."""
        from ..persistence.repository import SessionRepository

        repository = SessionRepository() if repository is None else repository
        return repository.save(
            self, path, expected_revision=expected_revision, create=create
        )

    def reload(self, *, repository=None):
        """Return a fresh graph from storage, leaving this graph and references intact."""
        if self.storage is None:
            raise ValueError("Save the session before reloading it.")
        from ..persistence.repository import SessionRepository

        repository = (
            SessionRepository(
                catalog=self.catalog,
                database=self.database,
                verification_registry=self.verification_registry,
            )
            if repository is None
            else repository
        )
        return type(self).open(self.storage.path, repository=repository)

    @property
    def objects(self):
        return tuple(self._objects.values())

    @property
    def all_elements(self):
        return tuple(
            value
            for value in self.objects
            if isinstance(value, Element) and not isinstance(value, ScriptConfiguration)
        )

    @property
    def elements(self):
        return tuple(
            value
            for value in self.all_elements
            if value not in (self.mission, self.external)
            and not isinstance(value, Stakeholder)
            and not value.selection
        )

    @property
    def stakeholders(self):
        return tuple(value for value in self.objects if isinstance(value, Stakeholder))

    @property
    def components(self):
        return tuple(
            value for value in self.all_elements if isinstance(value, Component)
        )

    @property
    def physical_components(self):
        return tuple(value for value in self.components if not value.selection)

    @property
    def cots_components(self):
        return tuple(
            value for value in self.all_elements if isinstance(value, DatabaseBacked)
        )

    @property
    def statements(self):
        return tuple(value for value in self.objects if isinstance(value, Statement))

    @property
    def requirements(self):
        return tuple(value for value in self.objects if isinstance(value, Requirement))

    @property
    def scripts(self):
        return tuple(
            value for value in self.objects if isinstance(value, ScriptConfiguration)
        )

    def get(self, identity):
        if not isinstance(identity, str):
            object_key = getattr(identity, "key", None)
            if object_key is not None and self._objects.get(object_key) is identity:
                return identity
            raise KeyError("The object is not registered in this session.")
        if identity in self._objects:
            return self._objects[identity]
        matches = [value for value in self.objects if value.id == identity]
        if len(matches) == 1:
            return matches[0]
        raise KeyError(f"Unknown session object {identity!r}.")

    def next_id(self, kind="Requirement", hint=""):
        ids = {value.id for value in self.objects}
        if kind in ("Element", "Stakeholder"):
            preferred = (
                re.sub(r"[^a-z]", "", hint, flags=re.I)[:3].upper().ljust(3, "X")
                if hint
                else "STK"
            )
            if preferred not in ids:
                return preferred
            for number in range(26**3):
                candidate = "".join(
                    chr(65 + index)
                    for index in (number // 676, number // 26 % 26, number % 26)
                )
                if candidate not in ids:
                    return candidate
            raise ValueError("All three-letter element IDs are in use.")
        prefix = (
            hint
            if re.fullmatch(r"[A-Z]{3}", hint)
            else {
                "Requirement": "REQ",
                "Need": "NED",
                "Objective": "OBJ",
                "Concern": "CON",
                "Constraint": "CST",
                "Component": "CMP",
                "Script": "SCR",
            }.get(kind, "REQ")
        )
        for number in range(1, 1000):
            candidate = f"{prefix}{number:03}"
            if candidate not in ids:
                return candidate
        raise ValueError(f"All {prefix} IDs are in use.")

    def available_key(self, hint):
        base = hint[:70]
        key, suffix = base, 1
        while key in self._objects:
            key = f"{base}_{suffix}"
            suffix += 1
        return key

    def _register(self, value):
        if not isinstance(value, (Element, Statement)):
            raise TypeError(
                "A session object must be an Element or Statement instance."
            )
        if value.session not in (None, self):
            raise ValueError("An object belongs to one session.")
        if value.key in self._objects:
            if self._objects[value.key] is value:
                return value
            raise ValueError(f"Duplicate object key {value.key!r}.")
        if not value.id:
            kind = (
                "Component"
                if isinstance(value, DatabaseBacked)
                else "Script"
                if isinstance(value, ScriptConfiguration)
                else "Element"
                if isinstance(value, Element)
                else value.kind
            )
            hint = (
                ""
                if isinstance(value, DatabaseBacked)
                else getattr(value, "id_prefix", "")
            )
            value._id = self.next_id(kind, hint)
        if any(other.id == value.id for other in self.objects):
            raise ValueError(f"The ID {value.id!r} is already in use.")
        value._session = self
        self._objects[value.key] = value
        if isinstance(value, Statement):
            for parameter in value.parameters.values():
                self.register_parameter(parameter)
        return value

    def restore(
        self,
        value,
        *,
        owner=None,
        projection_fields=(),
        verification_style=None,
        facts_present=None,
    ):
        """Register an explicitly reconstructed object with creation hooks disabled.

        Use add() for new engineering objects. This method deliberately avoids
        default owner inference, catalog seeding and budget initialization.
        """
        if owner is not None:
            value.owner = self.get(owner)
        if verification_style not in (None, "auto", "condition", "methods"):
            raise ValueError("Choose a supported verification transport style.")
        projection_fields = tuple(projection_fields)
        if any(not isinstance(field, str) for field in projection_fields):
            raise TypeError("Projection field names must be text.")
        if verification_style is not None and not isinstance(value, Statement):
            raise TypeError("Only statements have verification table styles.")
        if facts_present is not None and (
            not isinstance(value, DatabaseBacked) or type(facts_present) is not bool
        ):
            raise TypeError(
                "Only database-backed components have fact presence metadata."
            )
        self._register(value)
        value._projection_fields = frozenset(projection_fields)
        if verification_style is not None:
            value._verification_style = verification_style
        if facts_present is not None:
            value._facts_present = facts_present
        return value

    def restore_roots(
        self, *, mission, external, mission_fields=(), external_fields=()
    ):
        """Restore both concrete roots before registering non-root objects."""
        if (
            set(self._objects) != {self.mission.key, self.external.key}
            or self.seed_history
            or self._initialized
        ):
            raise ValueError(
                "Restore roots before adding objects or initialization history."
            )
        for role, value, original in (
            ("mission", mission, self.mission),
            ("external", external, self.external),
        ):
            if (
                not isinstance(value, type(original))
                or value.key != role
                or value.owner is not None
                or value.session not in (None, self)
            ):
                raise TypeError(
                    "A restored root retains its domain type, stable key and empty owner."
                )
        if mission.id == external.id:
            raise ValueError("Session root IDs must be unique.")
        originals = self.mission, self.external
        self._objects.clear()
        for value in originals:
            value._session = None
        try:
            self.restore(mission, projection_fields=mission_fields)
            self.restore(external, projection_fields=external_fields)
        except Exception:
            for value in tuple(self._objects.values()):
                value._session = None
            self._objects.clear()
            for value in originals:
                self._register(value)
            raise
        self.mission, self.external = mission, external
        return self

    def restore_state(
        self,
        *,
        variables=None,
        seed_history=(),
        initialized=(),
        requirement_seeds=(),
        resource_budgets=False,
        model_state_present=True,
        resource_budgets_present=False,
        requirement_seeds_present=False,
    ):
        """Restore typed initialization history after reconstructing relationships."""
        if any(
            type(flag) is not bool
            for flag in (
                resource_budgets,
                model_state_present,
                resource_budgets_present,
                requirement_seeds_present,
            )
        ):
            raise TypeError("Session initialization flags must be Boolean.")
        seeds = set(seed_history)
        if any(not isinstance(rule, SeedRule) for rule in seeds):
            raise TypeError("Initialization history contains SeedRule instances.")
        initialized = set(initialized)
        if any(not isinstance(key, str) for key in initialized):
            raise TypeError("Initialized object identities must be text.")
        remembered = {}
        for owner, definitions in requirement_seeds:
            self.get(owner)
            definitions = tuple(definitions)
            if any(not isinstance(definition, str) for definition in definitions):
                raise TypeError("Remembered requirement definitions must be text.")
            remembered[owner] = definitions
        if variables is not None:
            variables = list(variables)
            if any(not isinstance(variable, Variable) for variable in variables):
                raise TypeError("Display variables contain Variable records.")
            if len({variable.name for variable in variables}) != len(variables):
                raise ValueError("Display variable names must be unique.")
            self.variables = variables
        self.seed_history, self._initialized = seeds, initialized
        self._initializing = set()
        self.requirement_seeds = remembered
        self.resource_budgets = resource_budgets
        self._model_state_present = model_state_present
        self._resource_budgets_present = resource_budgets_present
        self._requirement_seeds_present = requirement_seeds_present
        self.clear_evidence()
        return self

    def _default_owner(self, value):
        if isinstance(value, ScriptConfiguration):
            return None
        if isinstance(value, (Statement, Stakeholder)):
            return self.external
        definition = self.catalog.by_model.get(value.definition)
        if definition is None or definition.parent is None:
            return self.mission
        matches = [
            element
            for element in self.elements
            if element.definition == definition.parent
        ]
        if len(matches) != 1:
            raise ValueError(
                f"Choose an owner of type {definition.parent} for {value.id or type(value).__name__}."
            )
        return matches[0]

    def add(self, value, *, owner=None, initialize=True):
        if value.key in self._objects and self._objects[value.key] is value:
            return value
        selected_owner = owner if owner is not None else value.owner
        if selected_owner is None:
            selected_owner = self._default_owner(value)
        if selected_owner is not None:
            self.get(selected_owner)
        value.owner = selected_owner
        if (
            isinstance(value, Component)
            and not value.selection
            and selected_owner is not None
        ):
            candidates = self.catalog.children(selected_owner.definition)
            matching = [
                definition
                for definition in candidates
                if definition.model.rsplit("::", 1)[-1]
                == value.definition.rsplit("::", 1)[-1]
            ]
            if matching:
                value.definition = matching[0].model
        if (
            isinstance(value, Element)
            and not isinstance(value, (Stakeholder, ScriptConfiguration))
            and not value.selection
        ):
            definition = self.catalog.by_model.get(value.definition)
            if definition is not None:
                expected = self.mission if definition.parent is None else selected_owner
                if (
                    selected_owner is not expected
                    or definition.parent is not None
                    and (
                        selected_owner is None
                        or selected_owner.definition != definition.parent
                    )
                ):
                    raise ValueError(
                        f"{value.definition} must belong to {definition.parent or 'Mission'}."
                    )
        if isinstance(value, Statement):
            for reference in (
                *value.sources,
                *value.affected,
                *(
                    method.source
                    for method in value.verifications
                    if method.source is not None
                ),
            ):
                self.get(reference)
        if (
            isinstance(value, DatabaseBacked)
            and value.usage is None
            and selected_owner is not None
        ):
            candidates = [
                element
                for element in self.elements
                if element.owner is selected_owner
                and element.definition.rsplit("::", 1)[-1]
                == value.definition.rsplit("::", 1)[-1]
            ]
            if len(candidates) == 1:
                value.usage = candidates[0]
        if isinstance(value, Element):
            for requirement in value.requirement_links:
                self.get(requirement)
        if isinstance(value, DatabaseBacked) and value.usage is not None:
            self.get(value.usage)
            if value.usage.selection:
                raise ValueError(
                    "A COTS usage must refer to a physical domain element."
                )
        before = set(self._objects)
        history, initialized = set(self.seed_history), set(self._initialized)
        variables = list(self.variables)
        remembered = dict(self.requirement_seeds)
        seeds_present = self._requirement_seeds_present
        model_state_present = self._model_state_present
        budget_flags = self.resource_budgets, self._resource_budgets_present
        statement_state = {
            row: (dict(row.parameters), row.sources, row.affected)
            for row in self.statements
        }
        self._register(value)
        try:
            if initialize:
                self._model_state_present = True
                self.initialize(value)
                if isinstance(value, Element):
                    value.on_added(self)
                    from ..domains.budgets import after_element_added

                    after_element_added(self, value)
        except Exception:
            for key in set(self._objects) - before:
                self._objects.pop(key)._session = None
            self.seed_history, self._initialized = history, initialized
            self.variables = variables
            self.requirement_seeds = remembered
            self._requirement_seeds_present = seeds_present
            self._model_state_present = model_state_present
            self.resource_budgets, self._resource_budgets_present = budget_flags
            for row, (parameters, sources, affected) in statement_state.items():
                row._parameters, row._sources, row._affected = (
                    parameters,
                    sources,
                    affected,
                )
            raise
        return value

    def initialize(self, value):
        self.get(value)
        if value.key in self._initialized or value.key in self._initializing:
            return value
        if isinstance(value, Element):
            self._initializing.add(value.key)
            try:
                value.initialize(self)
            finally:
                self._initializing.remove(value.key)
        self._initialized.add(value.key)
        return value

    def element_from_definition(self, definition, *, id="", key=None):
        from ..domains.registry import element_class

        cls = element_class(definition.model)
        return cls(id, key=key, name=definition.name, definition=definition.model)

    def initialize_children(self, parent):
        created = []
        for definition in self.catalog.children(parent.definition):
            if not definition.auto_create:
                continue
            rule = SeedRule(parent.key, parent.key, f"child:{definition.model}")
            if rule in self.seed_history:
                continue
            self.seed_history.add(rule)
            existing = [
                child
                for child in parent.children
                if not child.selection and child.definition == definition.model
            ]
            if existing:
                continue
            child = self.element_from_definition(
                definition,
                key=self.available_key(
                    f"{parent.key}-{definition.model.rsplit('::', 1)[-1]}"
                ),
            )
            self.add(child, owner=parent, initialize=False)
            created.append(child)
        for child in created:
            self.initialize(child)
        return tuple(created)

    def register_parameter(self, parameter):
        existing = next(
            (
                variable
                for variable in self.variables
                if variable.name == parameter.name
            ),
            None,
        )
        if existing is None:
            self.variables.append(
                Variable(parameter.name, parameter.value_type, parameter.unit or None)
            )
        elif existing.unit is None and parameter.unit:
            self.variables[self.variables.index(existing)] = replace(
                existing, unit=parameter.unit
            )

    def _component_templates(self, component):
        if component.owner is None or component.owner.role != "eps":
            return ()
        terminals = {
            component.definition.rsplit("::", 1)[-1],
            *(base.__dict__["model"].rsplit("::", 1)[-1]
              for base in type(component).__mro__ if base.__dict__.get("model")),
        }
        return tuple(
            template
            for template in self.catalog.requirements_for(component.owner.definition)
            if len(template.affected) == 1 and template.affected[0] in terminals
        )

    def remember_component_defaults(self, component):
        for template in self._component_templates(component):
            self.seed_history.add(
                SeedRule(component.owner.key, component.key, template.model)
            )

    def seed_component_requirements(self, component):
        return self._seed_templates(
            component.owner, self._component_templates(component), subject=component
        )

    def seed_requirements(self, owner):
        return self._seed_templates(
            owner, self.catalog.requirements_for(owner.definition)
        )

    def _seed_templates(self, owner, templates, *, subject=None):
        from ..domains.eps.requirements import GenericRequirement

        created = []
        for template in templates:
            context = self.mission if template.context == "mission" else owner
            seed_subject = subject or owner
            rule = SeedRule(context.key, seed_subject.key, template.model)
            if rule in self.seed_history:
                continue
            self.seed_history.add(rule)
            affected = (
                ((subject.usage,) if subject.usage is not None else ())
                if isinstance(subject, DatabaseBacked) and subject.selection
                else (subject,)
                if subject is not None
                else (owner,)
                if template.context == "mission"
                else tuple(
                    child
                    for child in owner.children
                    if not child.selection
                    and child.definition.rsplit("::", 1)[-1] in template.affected
                )
            )
            existing = next(
                (
                    row
                    for row in self.requirements
                    if row.owner is context
                    and row.definition == template.model
                    and row.subject is subject
                    and (template.context != "mission" or owner in row.affected)
                ),
                None,
            )
            if existing is not None:
                continue
            id = (
                template.id
                if not any(value.id == template.id for value in self.objects)
                else self.next_id("Requirement", template.id[:3])
            )
            row = GenericRequirement(
                template,
                id,
                substitute=lambda source: re.sub(
                    r"@([A-Za-z_][A-Za-z0-9_]*)\.", "UNBOUND.", source
                ),
                owner=context,
                affected=affected,
                key=self.available_key(f"generic-{seed_subject.id}-{template.name}"),
            )
            row.subject = subject
            self.add(row, owner=context, initialize=False)
            created.append(row)
        for row in created:

            def substitute(expression):
                def reference(match):
                    name = match.group(1)
                    candidates = [
                        other
                        for other in self.requirements
                        if other.definition == f"FrameworkRequirements::{name}"
                    ]
                    local = [
                        other
                        for other in candidates
                        if other.owner is row.owner
                        and (
                            row.owner is not self.mission
                            or any(
                                element in row.affected for element in other.affected
                            )
                        )
                    ]
                    specific = (
                        [other for other in local if other.subject is subject]
                        if subject is not None
                        else local
                    )
                    baseline = [other for other in local if other.subject is None]
                    mission = [
                        other for other in candidates if other.owner is self.mission
                    ]
                    target = (
                        specific[0]
                        if len(specific) == 1
                        else baseline[0]
                        if len(baseline) == 1
                        else mission[0]
                        if len(mission) == 1
                        else None
                    )
                    if target is None:
                        return "UNBOUND."
                    if target is not row:
                        row.derive_from(target)
                    return f"{target.id}."

                return re.sub(r"@([A-Za-z_][A-Za-z0-9_]*)\.", reference, expression)

            for name in row.template.derives_from:
                substitute(f"@{name}.")
            for parameter in row.template.parameters:
                if parameter.exposed and parameter.expression is not None:
                    expression = substitute(parameter.expression)
                    row.set_expression(
                        parameter.name, None if "UNBOUND." in expression else expression
                    )
            if row.template.condition:
                row.verifications = (
                    replace(
                        row.verifications[0],
                        condition=substitute(row.template.condition),
                    ),
                )
        managed = tuple(
            template.model for template in templates if template.auto_populate
        )
        if managed and subject is None:
            previous = self.requirement_seeds.get(owner, ())
            self.requirement_seeds[owner] = tuple(dict.fromkeys((*previous, *managed)))
            self._requirement_seeds_present = True
        return tuple(created)

    def _expressions(self):
        for value in (*self.statements, *self.scripts):
            for name, parameter in value.parameters.items():
                source = (
                    parameter.expression.source
                    if isinstance(parameter.expression, DraftExpression)
                    else parameter.expression
                )
                if isinstance(source, str):
                    yield value, "parameter", name, source
            if isinstance(value, Statement):
                for index, method in enumerate(value.verifications):
                    source = (
                        method.condition.source
                        if isinstance(method.condition, DraftExpression)
                        else method.condition
                    )
                    if isinstance(source, str):
                        yield value, "condition", index, source

        for load in self.power.loads:
            for state in load.states:
                if isinstance(state.watts, str):
                    yield load.element, "power_state", state.key, state.watts

    def _set_expression(self, row, kind, name, expression):
        """Rewrite every supported binding through the same lifecycle seam."""
        if kind == "parameter":
            self.configure_parameter(
                row, replace(row.parameters[name], expression=expression)
            )
        elif kind == "power_state":
            load = self.power.load_for(row)
            state = next(state for state in load.states if state.key == name)
            state.watts = (
                expression.source
                if isinstance(expression, DraftExpression)
                else expression
            )
        else:
            methods = list(row.verifications)
            methods[name] = replace(methods[name], condition=expression)
            row.verifications = methods

    def rename(self, identity, new_id):
        value = self.get(identity)
        if not isinstance(new_id, str) or not new_id.strip():
            raise ValueError("An object ID must be nonempty text.")
        if any(other is not value and other.id == new_id for other in self.objects):
            raise ValueError(f"The ID {new_id!r} is already in use.")
        old_id = value.id
        if old_id == new_id:
            return value
        updates = []
        for row, kind, name, source in self._expressions():
            rewritten = _rewrite(source, old_id, new_id)
            if rewritten != source:
                updates.append((row, kind, name, restored_expression(rewritten)))
        value._id = new_id
        self._model_state_present = True
        for row, kind, name, expression in updates:
            self._set_expression(row, kind, name, expression)
        for link in self.power.links:
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
                            _rewrite(source, old_id, new_id)
                        ),
                    )
        return value

    def remove(self, identity):
        value = self.get(identity)
        if value in (self.mission, self.external):
            raise ValueError("Session roots cannot be removed.")
        from ..domains.budgets import protect_budget_removal

        protect_budget_removal(self, value)
        for other in self.objects:
            if other is value:
                continue
            references = [
                getattr(other, "owner", None),
                getattr(other, "power_scope", None),
                getattr(other, "budget_scope", None),
                getattr(other, "subject", None),
                getattr(other, "usage", None),
            ]
            if isinstance(other, Statement):
                references.extend(
                    (
                        *other.sources,
                        *other.affected,
                        *(method.source for method in other.verifications),
                    )
                )
            if isinstance(other, Element):
                references.extend(other.requirement_links)
            if any(reference is value for reference in references):
                raise ValueError(
                    f"{value.id} is referenced by {other.id}. Remove that relationship first."
                )
        for row, _, _, source in self._expressions():
            if (
                row is not value
                and _rewrite(source, value.id, "__referenced__") != source
            ):
                raise ValueError(f"{value.id} is used by an expression in {row.id}.")
        if any(load.host is value for load in self.power.loads):
            raise ValueError("Remove the execution host reference before deleting it.")
        if any(link.eps is value or value in link.roots for link in self.power.links):
            raise ValueError(
                "Remove the load budget connection before deleting its scope."
            )
        self.power.loads = [
            load for load in self.power.loads if load.element is not value
        ]
        del self._objects[value.key]
        self.requirement_seeds.pop(value, None)
        value._session = None
        self._model_state_present = True
        return value

    def retype(self, identity, definition):
        from .changes import retype_element

        return retype_element(self, identity, definition)

    def substitute_product(self, identity, product):
        from .changes import substitute_product

        return substitute_product(self, identity, product)

    def configure_parameter(self, identity, parameter):
        from .changes import configure_parameter

        return configure_parameter(self, identity, parameter)

    def configure_facts(self, identity, references):
        from .changes import configure_facts

        return configure_facts(self, identity, references)

    def resolve_mode(self, mode):
        if isinstance(mode, Mode) and mode in self.power.modes:
            return mode
        if isinstance(mode, str):
            matches = [
                value for value in self.power.modes if mode in (value.key, value.name)
            ]
            if len(matches) == 1:
                return matches[0]
        raise ValueError("Choose an existing spacecraft mode.")

    def add_mode(self, mode, *, sunlight=None, eclipse=None):
        from ..domains.budgets import seed_power_limits, validate_budgets

        if isinstance(mode, str):
            mode = Mode(mode, sunlight, eclipse)
        if not isinstance(mode, Mode):
            raise TypeError("Add a Mode instance or a mode name.")
        if mode in self.power.modes:
            return mode
        self.power.modes.append(mode)
        try:
            validate_budgets(self)
        except Exception:
            self.power.modes.remove(mode)
            raise
        seed_power_limits(self)
        self._model_state_present = True
        return mode

    def configure_mode(self, mode, **changes):
        selected = self.resolve_mode(mode)
        if set(changes) - {"name", "sunlight", "eclipse"}:
            raise ValueError("Update a mode's name or sunlight/eclipse shares.")
        candidate = replace(selected, **changes)
        if candidate.name != selected.name:
            self.rename_mode(selected, candidate.name)
        selected.sunlight, selected.eclipse = candidate.sunlight, candidate.eclipse
        self._model_state_present = True
        return selected

    def rename_mode(self, mode, name):
        from .modes import rewrite_mode

        selected = self.resolve_mode(mode)
        if not isinstance(name, str) or not name.strip() or len(name) > 80:
            raise ValueError("Name the mode using 1 to 80 characters.")
        if any(
            other is not selected and other.name.strip().lower() == name.strip().lower()
            for other in self.power.modes
        ):
            raise ValueError("Spacecraft mode names must be unique.")
        previous = selected.name
        for row, kind, field, source in self._expressions():
            rewritten = rewrite_mode(source, previous, name)
            if rewritten == source:
                continue
            self._set_expression(row, kind, field, restored_expression(rewritten))
        for link in self.power.links:
            for field, parameter in tuple(link.previous.items()):
                source = (
                    parameter.expression.source
                    if isinstance(parameter.expression, DraftExpression)
                    else parameter.expression
                )
                if isinstance(source, str):
                    link.previous[field] = replace(
                        parameter,
                        expression=restored_expression(
                            rewrite_mode(source, previous, name)
                        ),
                    )
        selected.name = name
        self._model_state_present = True
        return selected

    def remove_mode(self, mode):
        from .modes import mode_referenced

        selected = self.resolve_mode(mode)
        sources = [source for _, _, _, source in self._expressions()]
        sources.extend(
            parameter.expression.source
            if isinstance(parameter.expression, DraftExpression)
            else parameter.expression
            for link in self.power.links
            for parameter in link.previous.values()
        )
        if any(mode_referenced(source, selected.name) for source in sources):
            raise ValueError(
                "Remove expression references to this mode before deleting it."
            )
        self.power.modes.remove(selected)
        self._model_state_present = True
        for load in self.power.loads:
            load.assignments.pop(selected, None)
            load.duties.pop(selected, None)
            load.allocations.pop(selected, None)
        return selected

    def configure_parameter_states(self, target, parameter, **changes):
        from .modes import configure_parameter_states

        return configure_parameter_states(self, target, parameter, **changes)

    def configure_load(self, element, **changes):
        from ..domains.budgets import configure_load

        return configure_load(self, element, **changes)

    def connect_power(self, eps, roots=None):
        from ..domains.budgets import connect_power

        return connect_power(self, eps, roots)

    def disconnect_power(self, eps):
        from ..domains.budgets import disconnect_power

        return disconnect_power(self, eps)

    def seed_power_limits(self, scopes=None):
        from ..domains.budgets import seed_power_limits

        return seed_power_limits(
            self, None if scopes is None else tuple(self.get(scope) for scope in scopes)
        )

    def seed_resource_budgets(self, scopes=None):
        from ..domains.budgets import seed_resource_budgets

        return seed_resource_budgets(
            self, None if scopes is None else tuple(self.get(scope) for scope in scopes)
        )

    def reconcile_defaults(self, *, generic=True, budgets=True):
        from ..domains.budgets import reconcile_defaults

        self._model_state_present = True
        return reconcile_defaults(self, generic=generic, budgets=budgets)

    def validate_budgets(self):
        from ..domains.budgets import validate_budgets

        return validate_budgets(self)

    def validate_parameter_binding(self, row, parameter):
        from ..domains.budgets import validate_parameter_binding

        validate_parameter_binding(self, row, parameter)

    def evaluation_context(self, mode=None, **kwargs):
        from .evaluation import EvaluationContext

        return EvaluationContext(self, mode, **kwargs)

    def calculation_signature(self):
        from .evaluation import calculation_signature

        return calculation_signature(self)

    def value(
        self, identity, parameter, *, mode=ALL_MODES, evidence=None, source_ready=None
    ):
        from .evaluation import value

        return value(
            self,
            self.get(identity),
            parameter,
            mode=mode,
            evidence=evidence,
            source_ready=source_ready,
        )

    def evaluate(self, *, mode=ALL_MODES, evidence=None, source_ready=None):
        from .evaluation import evaluate

        return evaluate(self, mode=mode, evidence=evidence, source_ready=source_ready)

    def verify(
        self, identity=None, *, mode=ALL_MODES, evidence=None, source_ready=None
    ):
        from .evaluation import verify

        return verify(
            self, identity, mode=mode, evidence=evidence, source_ready=source_ready
        )

    def script_inputs(self, script, *, mode=None, evidence=None):
        from .evaluation import script_inputs

        return script_inputs(self, script, mode=mode, evidence=evidence)

    def run(self, script=None, **kwargs):
        """Explicitly execute analyses and retain transient current evidence."""
        from .execution import run

        return run(self, script, **kwargs)

    @property
    def execution_evidence(self):
        """The latest immutable run evidence, excluded from session configuration."""
        return self._execution_evidence

    def clear_evidence(self):
        self._execution_evidence = None
