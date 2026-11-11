"""Adapter for explicitly configured, trusted local JSON-protocol scripts.

Source is read for revision checks and copied only during explicit execution.
It is never imported while a session or the script picker is being opened.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from ..core.verification import PendingValue, ScriptDefinition, VerificationScript


@dataclass(frozen=True)
class RegisteredSource:
    directory: Path
    definition: ScriptDefinition
    source: str
    revision: str


def read_registered(directory, identity):
    if not isinstance(identity, str) or not re.fullmatch(
        r"[a-z][a-z0-9_]{0,79}", identity
    ):
        raise ValueError("Choose a registered script ID.")
    root = Path(directory).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("The trusted script directory is unavailable.")

    def read(extension, maximum):
        path = (root / f"{identity}.{extension}").resolve(strict=True)
        try:
            path.relative_to(root)
        except ValueError:
            raise ValueError(
                "Registered scripts must stay inside the trusted directory."
            ) from None
        if not path.is_file() or path.stat().st_size > maximum:
            raise ValueError(f"The registered {extension} file exceeds its size limit.")
        data = path.read_bytes()
        if len(data) > maximum:
            raise ValueError(f"The registered {extension} file exceeds its size limit.")
        return data

    metadata = read("json", 32768)
    source = read("py", 262144)
    definition = ScriptDefinition.from_metadata(json.loads(metadata.decode("utf-8")))
    if definition.id != identity:
        raise ValueError("The registered metadata ID must match its filename.")
    return RegisteredSource(
        root,
        definition,
        source.decode("utf-8"),
        hashlib.sha256(metadata + b"\0" + source).hexdigest(),
    )


class RegisteredScript(VerificationScript):
    """A VerificationScript whose trusted implementation uses stdin/stdout JSON."""

    def __init__(self, id="", *, directory, definition, **kwargs):
        self._registration = read_registered(directory, definition)
        super().__init__(id, definition=definition, **kwargs)

    @classmethod
    def restore(
        cls, id="", *, directory, registration_spec, registry=None, **configuration
    ):
        """Retain a trusted external binding even while its files are unavailable.

        An explicitly configured registry can relocate the source directory.
        Reading or executing external source remains the normal explicit runner's
        responsibility. Saved interface pins are never silently updated here.
        """
        if not isinstance(registration_spec, ScriptDefinition):
            raise TypeError("Restore a registered ScriptDefinition.")
        configured = (
            None if registry is None else registry.directory_for(registration_spec.id)
        )
        value = cls.__new__(cls)
        value._registration = RegisteredSource(
            Path(directory if configured is None else configured)
            .expanduser()
            .resolve(),
            registration_spec,
            "",
            configuration.get("revision", ""),
        )
        from ..core.configuration import ScriptConfiguration

        ScriptConfiguration.__init__(value, id, **configuration)
        return value

    @property
    def spec(self):
        return self._registration.definition

    @property
    def current_revision(self):
        try:
            return read_registered(self._registration.directory, self.spec.id).revision
        except (OSError, ValueError, KeyError, TypeError):
            return "unavailable"

    @property
    def revision_is_current(self):
        return self.revision == self.current_revision

    def registered_source(self):
        registered = read_registered(self._registration.directory, self.spec.id)
        if (
            registered.revision != self.revision
            or tuple(self.inputs) != registered.definition.inputs
            or tuple(self.outputs) != registered.definition.outputs
        ):
            raise PendingValue(
                f"{self.id}: the registered source or interface changed. Review and update its definition before running.",
                script_key=self.key,
            )
        return registered

    def assert_current(self):
        try:
            self.registered_source()
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise PendingValue(
                f"{self.id}: registered definition is unavailable or changed ({error}).",
                script_key=self.key,
            ) from error

    def describe(self):
        registered = read_registered(self._registration.directory, self.spec.id)
        return {**registered.definition.projection(), "revision": registered.revision}

    def update_definition(self):
        self._registration = read_registered(self._registration.directory, self.spec.id)
        return super().update_definition()

    def calculate(self, inputs, *, requirements=None, mode=None):
        raise ValueError("Registered JSON-protocol scripts require isolated execution.")
