"""Named objects, owned properties and explicit containment lifecycle."""

import keyword
from types import MappingProxyType

from .properties import Property


def identifier(name):
    if not isinstance(name, str) or not name.isidentifier() or keyword.iskeyword(name):
        raise ValueError("Object and property names must be Python identifiers.")
    return name


class ModelObject:
    fixed_properties = False
    is_mission = False
    child_aliases = {}

    def __init__(self, name, **bindings):
        self._name = identifier(name)
        self._parent = None
        self._children = []
        self._initialized = False
        self._requirements_initialized = False
        definitions = {}
        for cls in reversed(type(self).__mro__):
            definitions.update({key: value for key, value in vars(cls).items() if isinstance(value, Property)})
        self._properties = {
            key: value.copy(self, key, frozen=self.fixed_properties)
            for key, value in definitions.items()
        }
        if self.fixed_properties and bindings:
            raise TypeError("Define COTS property values on the product class.")
        for key, value in bindings.items():
            if key in self._properties:
                self._set_property(key, value)
            elif isinstance(value, Property):
                self.define(key, value)
            else:
                raise TypeError(f"Unknown property {key!r}. Declare it with Property.")

    def __getattr__(self, name):
        properties = self.__dict__.get("_properties", {})
        if name in properties:
            return properties[name]
        for child in self.__dict__.get("_children", ()):
            if child.name == name:
                return child
        raise AttributeError(f"{type(self).__name__} has no attribute {name!r}.")

    def __setattr__(self, name, value):
        if name in self.__dict__.get("_properties", {}):
            self._set_property(name, value)
        else:
            object.__setattr__(self, name, value)

    def _set_property(self, name, value):
        current = self._properties[name]
        current._editable()
        if value is current:
            return
        if isinstance(value, Property):
            source = Property.link(value) if value.owner is not None else value
            current.expression = source.expression
            current.unit = source.unit
            current._modes = dict(source._modes)
            current._source = source._source
        else:
            current.expression = value

    def define(self, name, prop):
        identifier(name)
        if self.fixed_properties:
            raise AttributeError("COTS properties are fixed by the product class.")
        if name in self.__dict__ or hasattr(type(self), name) or name in self._properties or any(child.name == name for child in self.children):
            raise ValueError(f"{name!r} is already defined.")
        if not isinstance(prop, Property):
            raise TypeError("Declare an additional property with Property.")
        source = Property.link(prop) if prop.owner is not None else prop
        self._properties[name] = source.copy(self, name)
        return self._properties[name]

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def path(self):
        return f"{self.parent.path}.{self.name}" if self.parent is not None else self.name

    @property
    def mission(self):
        if self.is_mission:
            return self
        return self.parent.mission if self.parent is not None else None

    @property
    def properties(self):
        return MappingProxyType(self._properties)

    @property
    def children(self):
        return tuple(self._children)

    @property
    def requirements(self):
        from .requirements import Requirement

        return tuple(child for child in self.children if isinstance(child, Requirement))

    def add_requirement(self, name, **definition):
        """Create an owned default once, preserving authored replacements."""
        from .requirements import Requirement

        identifier(name)
        existing = next((child for child in self.children if child.name == name), None)
        if existing is not None:
            if not isinstance(existing, Requirement):
                raise ValueError(f"Generated requirement name {name!r} conflicts with another object.")
            return existing
        definition.setdefault("context", self)
        return self.add(Requirement(name, **definition))

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def child(self, name):
        for child in self.children:
            if child.name == name:
                return child
        raise KeyError(f"{self.path} has no child {name!r}.")

    def accepts(self, child):
        return False

    def validate_attachment(self):
        """Subclasses validate links after joining a parent."""

    def add(self, child, *, initialize=True):
        if isinstance(child, ModelObject) and child.parent is self:
            return child
        if not isinstance(child, ModelObject) or not self.accepts(child):
            raise TypeError(f"{type(self).__name__} cannot contain {type(child).__name__}.")
        if child.parent is not None:
            raise ValueError("An object has one parent. Reference its properties from other objects.")
        if self in child.walk():
            raise ValueError("Containment cannot contain a cycle.")
        if any(existing.name == child.name for existing in self.children):
            raise ValueError(f"Duplicate child name {child.name!r} in {self.path}.")
        alias_type = self.child_aliases.get(child.name)
        if child.name in self.__dict__ or hasattr(type(self), child.name) or child.name in self.properties:
            if alias_type is None or not isinstance(child, alias_type):
                raise ValueError(f"Child name {child.name!r} conflicts with an existing attribute.")
        roots = (self.mission or self, child)
        requirements_before = {req for root in roots for item in root.walk() for req in item.requirements}
        states_before = {item: item._requirements_initialized for item in child.walk()}
        child._parent = self
        self._children.append(child)
        try:
            for item in child.walk():
                item.validate_attachment()
                for prop in item.properties.values():
                    if item.mission is not None and any(mode.mission is not item.mission for mode in prop.modes):
                        raise ValueError("Property bindings must use modes from this Mission.")
            if initialize:
                child.initialize()
            else:
                child._initialized = True
                for item in child.walk():
                    item._requirements_initialized = True
        except Exception:
            self._children.remove(child)
            child._parent = None
            for root in roots:
                for item in root.walk():
                    for requirement in item.requirements:
                        if requirement not in requirements_before:
                            item.remove(requirement)
            for item in child.walk():
                item._requirements_initialized = states_before.get(item, False)
            raise
        return child

    def remove(self, child):
        child = self.child(child) if isinstance(child, str) else child
        self._children.remove(child)
        child._parent = None
        return child

    def initialize(self):
        if not self._initialized:
            self.create_defaults()
            self._initialized = True
        if self.mission is not None:
            for item in self.walk():
                if not item._requirements_initialized:
                    item.create_requirements()
                    item._requirements_initialized = True
        return self

    def create_defaults(self):
        """Create declared physical defaults on an explicit first add."""

    def create_requirements(self):
        """Add owned default requirements after joining a Mission."""

    @classmethod
    def restore(cls, name, **bindings):
        value = cls(name, **bindings)
        value._initialized = True
        value._requirements_initialized = True
        return value

    @property
    def verification(self):
        from .requirements import InstanceVerification

        return self.mission.verify().for_instance(self) if self.mission else InstanceVerification(self, ())

    @property
    def verified(self):
        return self.verification.verified

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"
