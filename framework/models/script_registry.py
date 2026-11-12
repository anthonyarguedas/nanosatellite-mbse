"""Explicit registration of trusted analysis classes, with no built-in analyses."""

from .verification import ScriptDefinition, UnresolvedVerification, VerificationScript


class ScriptRegistry:
    """Expose explicitly supplied classes to sessions and the GUI."""

    def __init__(self, classes=()):
        self._classes = {}
        for cls in classes:
            self.register(cls)

    def register(self, cls):
        if not isinstance(cls, type) or not issubclass(cls, VerificationScript):
            raise TypeError("Registered classes must inherit VerificationScript.")
        if not isinstance(cls.definition_spec, ScriptDefinition):
            raise TypeError("Registered classes must declare a ScriptDefinition.")
        identity = cls.definition_spec.id
        if identity in self._classes:
            raise ValueError(f"Duplicate registered analysis {identity!r}.")
        self._classes[identity] = cls
        return cls

    def create(self, definition, id="", **kwargs):
        cls = self._classes.get(definition)
        if cls is None:
            if not kwargs.get("outputs"):
                raise ValueError(f"Analysis definition {definition!r} is unavailable.")
            # Retain saved interfaces and bindings while their implementation is absent.
            return UnresolvedVerification(id, definition=definition, **kwargs)
        return cls(id, definition=definition, **kwargs)

    def describe(self):
        return [self.create(identity).describe() for identity in sorted(self._classes)]


def default_registry():
    """Start empty while the script implementations are being redesigned."""
    return ScriptRegistry()
