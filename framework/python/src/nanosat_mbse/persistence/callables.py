"""Trusted import identities and opaque transport tokens for native bindings.

Only trusted session loading or application composition registers callables.
Resolving browser data consults this registry and never imports a module named
by that data. Session source generation uses import identities separately.
"""

from __future__ import annotations

import importlib
import inspect
import secrets
from dataclasses import dataclass


class UnserializableCallable(ValueError):
    """A callable cannot be reconstructed through a stable Python import."""


def import_identity(value):
    """Return an identity only when a normal import retrieves this exact object."""
    module = getattr(value, "__module__", None)
    name = getattr(value, "__qualname__", None)
    if (
        not isinstance(module, str)
        or module == "__main__"
        or not isinstance(name, str)
        or any(not part.isidentifier() for part in name.split("."))
        or "<" in name
        or inspect.ismethod(value)
        and not isinstance(value.__self__, type)
    ):
        raise UnserializableCallable(
            "Session classes and native bindings need importable module identities. "
            "Move interactive functions, lambdas, closures and bound instance methods "
            "into a reusable module before saving."
        )
    try:
        imported = importlib.import_module(module)
        for part in name.split("."):
            imported = getattr(imported, part)
    except (ImportError, AttributeError) as error:
        raise UnserializableCallable(
            f"Cannot import {module}:{name} for session persistence."
        ) from error
    identical = imported is value
    if inspect.ismethod(value) and inspect.ismethod(imported):
        identical = (
            imported.__func__ is value.__func__ and imported.__self__ is value.__self__
        )
    if not identical:
        raise UnserializableCallable(
            f"{module}:{name} no longer identifies the configured object. "
            "Reload the implementation before saving."
        )
    return module, name


@dataclass(frozen=True)
class CallableBinding:
    token: str
    label: str

    def projection(self):
        return {"token": self.token, "label": self.label, "readOnly": True}


class CallableRegistry:
    """Session-scoped capability registry for read-only native UI bindings.

    Tokens are opaque and process local. They are never persisted as Python
    imports or accepted as module paths. Keep this object on the trusted service
    side while a browser edits the projection it produced.
    """

    def __init__(self):
        self._bindings = {}
        self._tokens = {}

    @staticmethod
    def _slot(slot):
        if slot is not None and (
            not isinstance(slot, tuple)
            or any(not isinstance(item, str) for item in slot)
        ):
            raise TypeError("A callable slot is a tuple of stable text identities.")
        return slot

    def register(self, function, *, slot=None):
        if not callable(function):
            raise TypeError("Register a trusted callable object.")
        slot = self._slot(slot)
        identity = (id(function), slot)
        existing = self._tokens.get(identity)
        if existing is not None and self._bindings[existing][0] is function:
            return self._bindings[existing][1].projection()
        label = f"{getattr(function, '__module__', '')}:{getattr(function, '__qualname__', type(function).__name__)}"
        token = secrets.token_urlsafe(24)
        binding = CallableBinding(token, label)
        self._bindings[token] = (function, binding, slot)
        self._tokens[identity] = token
        return binding.projection()

    def resolve(self, selection, *, slot=None):
        if (
            not isinstance(selection, dict)
            or set(selection) != {"token", "label", "readOnly"}
            or selection.get("readOnly") is not True
            or not isinstance(selection.get("token"), str)
        ):
            raise ValueError("Native bindings require a registered read-only token.")
        slot = self._slot(slot)
        registered = self._bindings.get(selection["token"])
        if (
            registered is None
            or registered[1].label != selection.get("label")
            or registered[2] != slot
        ):
            raise ValueError(
                "The native binding is unknown, expired or assigned to another slot. Reopen the session."
            )
        return registered[0]

    def clear(self):
        """Revoke the capabilities when the trusted session handle is closed."""
        self._bindings.clear()
        self._tokens.clear()
