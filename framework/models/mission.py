"""One configuration, its imports, orbit, domain elements and requirements."""

from collections import Counter
from types import MappingProxyType

from .elements import DomainElement, Orbit
from .functions import ModuleImport
from .objects import ModelObject
from .requirements import Requirement, VerificationReport
from .properties import Property
from .stakeholders import Stakeholder, ThirdParty

_DEFAULT_ORBIT = object()


class Mission(ModelObject):
    is_mission = True
    child_aliases = {"orbit": Orbit}
    lifetime = Property(unit="year")
    days_per_year = Property(unit="day/year")

    def __init__(self, name="mission", *, orbit=_DEFAULT_ORBIT, imports=(), **bindings):
        super().__init__(name, **bindings)
        self._imports = {}
        self.add_import("import math as math")
        self.add_import("import framework.scripts.sizing as sizing")
        for source in imports:
            self.add_import(source)
        if orbit is _DEFAULT_ORBIT:
            orbit = Orbit("orbit")
        if orbit is not None:
            self.add(orbit)
        self._initialized = True

    @property
    def imports(self):
        return MappingProxyType(self._imports)

    def add_import(self, source):
        imported = ModuleImport(source)
        if imported.alias in (self.name, "self", "mode"):
            raise ValueError("The import alias conflicts with the expression namespace.")
        old = self._imports.get(imported.alias)
        if old is not None:
            if old.package != imported.package:
                raise ValueError(f"Import alias {imported.alias!r} is already used.")
            return old
        if any(child.name == imported.alias for child in self.children):
            raise ValueError("An import alias cannot replace a Mission child.")
        self._imports[imported.alias] = imported
        return imported

    @property
    def namespace(self):
        objects = tuple(self.walk())
        counts = Counter(item.name for item in objects)
        namespace = {name: imported.namespace for name, imported in self.imports.items()}
        namespace[self.name] = self
        for item in objects:
            if counts[item.name] == 1 and item.name not in ("self", "mode"):
                namespace.setdefault(item.name, item)
        return namespace

    @property
    def orbit(self):
        return next((child for child in self.children if isinstance(child, Orbit)), None)

    @property
    def elements(self):
        return tuple(child for child in self.children if isinstance(child, DomainElement))

    @property
    def stakeholders(self):
        return tuple(child for child in self.children if isinstance(child, Stakeholder))

    @property
    def third_parties(self):
        return tuple(child for child in self.children if isinstance(child, ThirdParty))

    def accepts(self, child):
        if child.name in (*self.imports, self.name, "self", "mode"):
            raise ValueError("The child name conflicts with the expression namespace.")
        if isinstance(child, Orbit):
            return self.orbit is None
        return isinstance(child, (DomainElement, Stakeholder, ThirdParty, Requirement))

    def get(self, path):
        parts = path.split(".")
        if parts[0] == self.name:
            current = self
        else:
            matches = [item for item in self.walk() if item.name == parts[0]]
            if len(matches) != 1:
                raise KeyError(f"{parts[0]!r} is missing or ambiguous. Use its full path.")
            current = matches[0]
        for name in parts[1:]:
            current = current.properties[name] if name in current.properties else current.child(name)
        return current

    def verify(self, *, mode=None):
        results = tuple(
            condition.evaluate(mode=mode)
            for requirement in self.walk() if isinstance(requirement, Requirement)
            for condition in requirement.conditions
        )
        return VerificationReport(self, results)

    @classmethod
    def restore(cls, name="mission", *, orbit=None, **configuration):
        return cls(name, orbit=orbit, **configuration)


Session = Mission
