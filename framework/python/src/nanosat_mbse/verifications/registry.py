"""Explicit analysis registration shared by the native API and UI service."""

from __future__ import annotations

import os
from pathlib import Path

from ..core.verification import UnresolvedVerification, VerificationScript
from .registered import RegisteredScript, read_registered


def builtin_classes():
    from .battery_step import BatteryStep
    from .converter_step import ConverterStep
    from .energy_segment import EnergySegment
    from .fit import Fit
    from .geometry import Geometry
    from .guidance import Guidance
    from .illumination import Illumination
    from .mppt import MPPT
    from .normal_interval import NormalInterval
    from .power_path import PowerPath
    from .protection import Protection
    from .ram import RAM
    from .sizing import Sizing
    from .thermal import Thermal

    return (
        BatteryStep,
        ConverterStep,
        EnergySegment,
        Fit,
        Geometry,
        Guidance,
        Illumination,
        MPPT,
        NormalInterval,
        PowerPath,
        Protection,
        RAM,
        Sizing,
        Thermal,
    )


class ScriptRegistry:
    """Trusted class/provider registry, with no source paths supplied by UI data."""

    def __init__(self, classes=(), *, directory=None, override=False):
        self._classes = {}
        self._directories = []
        for cls in classes:
            self.register(cls)
        if directory is not None:
            self.register_directory(directory, override=override)

    def register(self, cls):
        if not isinstance(cls, type) or not issubclass(cls, VerificationScript):
            raise TypeError("Registered classes must inherit VerificationScript.")
        identity = cls.definition_spec.id
        if identity in self._classes:
            raise ValueError(f"Duplicate registered analysis {identity!r}.")
        self._classes[identity] = cls
        return cls

    def register_directory(self, directory, *, override=False):
        root = Path(directory).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("The trusted script directory is unavailable.")
        # Check metadata and containment now, without importing source.
        for identity in self._external_ids(root):
            read_registered(root, identity)
            if not override and (
                identity in self._classes
                or self._external_directory(identity) is not None
            ):
                raise ValueError(f"Duplicate registered analysis {identity!r}.")
        self._directories.append(root)
        return self

    @staticmethod
    def _external_ids(directory):
        return tuple(path.stem for path in sorted(directory.glob("*.json")))

    def _external_directory(self, identity):
        return next(
            (
                root
                for root in reversed(self._directories)
                if (root / f"{identity}.json").exists()
            ),
            None,
        )

    def directory_for(self, definition):
        """Return only an application-configured trusted source directory."""
        return self._external_directory(definition)

    def create(self, definition, id="", **kwargs):
        directory = self.directory_for(definition)
        if directory is not None:
            return RegisteredScript(
                id, directory=directory, definition=definition, **kwargs
            )
        cls = self._classes.get(definition)
        if cls is None:
            return UnresolvedVerification(id, definition=definition, **kwargs)
        return cls(id, definition=definition, **kwargs)

    def describe(self):
        identities = set(self._classes)
        for directory in self._directories:
            identities.update(self._external_ids(directory))
        return [self.create(identity).describe() for identity in sorted(identities)]


def default_registry(*, directory=None):
    configured = (
        directory
        if directory is not None
        else os.environ.get("VERIFICATION_SCRIPTS_DIR")
    )
    return ScriptRegistry(builtin_classes(), directory=configured, override=True)
