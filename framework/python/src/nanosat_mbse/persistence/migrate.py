"""Explicit legacy JSON conversion that always preserves the original files."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, replace
from pathlib import Path
from uuid import uuid4

from ..catalogs.database import TabularDatabase
from ..core.session import Session
from ..verifications.registry import default_registry
from .repository import (
    MAX_SESSION_BYTES,
    SessionConflict,
    SessionFileError,
    SessionRepository,
    StorageStatus,
    _read_regular,
    _sync_directory,
)


def _path(path):
    value = Path(os.path.abspath(os.path.expanduser(os.fspath(path))))
    return value.parent.resolve(strict=False) / value.name


@dataclass(frozen=True)
class SessionMetadata:
    """Picker metadata, independent of the authoritative Python object graph."""

    id: str
    name: str
    template: str
    created_at: str
    model_file: str = "session.py"
    legacy_source: str = ""
    storage: str = "python"

    def __post_init__(self):
        if not isinstance(self.id, str) or not re.fullmatch(
            r"[A-Za-z0-9_-]{1,80}", self.id
        ):
            raise SessionFileError("Session metadata needs a stable identifier.")
        if (
            not isinstance(self.name, str)
            or not 1 <= len(self.name.strip()) <= 80
            or re.search(r"[\x00-\x1f\x7f]", self.name)
        ):
            raise SessionFileError(
                "Session names contain 1 to 80 characters on one line."
            )
        # Historical provenance is readable without exposing a creation preset.
        if self.template not in ("blank", "generic-eps", "copy", "existing"):
            raise SessionFileError("Unsupported session template metadata.")
        if not isinstance(self.created_at, str) or not self.created_at:
            raise SessionFileError("Session metadata needs its creation timestamp.")
        if self.storage != "python":
            raise SessionFileError("Native session metadata uses Python storage.")
        for value in (self.model_file, self.legacy_source):
            if (
                not isinstance(value, str)
                or value
                and (
                    Path(value).name != value
                    or value in (".", "..")
                    or "/" in value
                    or "\\" in value
                )
            ):
                raise SessionFileError("Metadata model paths are local filenames.")
        if not self.model_file.endswith(".py"):
            raise SessionFileError("Session metadata must name a Python model file.")

    @classmethod
    def from_projection(cls, data):
        if not isinstance(data, dict) or data.get("storage") not in ("json", "python"):
            raise SessionFileError("Choose recognized JSON or Python session metadata.")
        allowed = {
            "id",
            "name",
            "template",
            "createdAt",
            "storage",
            "modelFile",
            "legacySource",
        }
        if set(data) - allowed:
            raise SessionFileError(
                "Unsupported session metadata fields must be preserved explicitly."
            )
        return cls(
            data["id"],
            data["name"],
            data["template"],
            data["createdAt"],
            data.get("modelFile", "session.py"),
            data.get("legacySource", ""),
        )

    @classmethod
    def read(cls, path):
        path = _path(path)
        content, _ = _read_regular(path, 32768)
        try:
            return cls.from_projection(json.loads(content.decode("utf-8-sig")))
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
            raise SessionFileError(
                f"Invalid session metadata in {path.name}: {error}"
            ) from error

    def projection(self):
        return {
            "id": self.id,
            "name": self.name,
            "template": self.template,
            "createdAt": self.created_at,
            "storage": "python",
            "modelFile": self.model_file,
            **({"legacySource": self.legacy_source} if self.legacy_source else {}),
        }

    def create(self, path):
        """Publish new metadata atomically without replacing any existing file."""
        path = _path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = (
            json.dumps(self.projection(), ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        if len(encoded) > 32768:
            raise SessionFileError(
                "Session metadata exceeds its 32 KiB file size limit."
            )
        temporary = path.with_name(f"{path.name}.{uuid4().hex}.tmp")
        try:
            descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as output:
                output.write(encoded)
                output.flush()
                os.fsync(output.fileno())
            try:
                os.link(temporary, path)
            except FileExistsError:
                raise SessionConflict(
                    f"Metadata {path.name} already exists. Preserve it and choose a new path."
                ) from None
            _sync_directory(path.parent)
        finally:
            temporary.unlink(missing_ok=True)
        return path


@dataclass(frozen=True)
class MigrationResult:
    source: Path
    session: Session
    storage: StorageStatus
    metadata: object = None


def legacy_destination(source):
    """Suggest an adjacent .py path without opening or converting anything."""
    source = _path(source)
    if source.suffix.lower() != ".json":
        raise SessionFileError("Choose a legacy .json workspace.")
    return source.with_suffix(".py")


def convert_json(
    source,
    destination=None,
    *,
    metadata=None,
    name=None,
    catalog=None,
    database=None,
    verification_registry=None,
    repository=None,
):
    """Create a new Python file from JSON, with no analysis execution or overwrite.

    Passing legacy metadata retains its session ID, name, template and creation
    time. Adapted metadata is returned for explicit create-only publication by
    the caller. The original JSON and its metadata remain unchanged.
    """
    source = _path(source)
    suggested = legacy_destination(source)
    destination = suggested if destination is None else destination
    content, _ = _read_regular(source, MAX_SESSION_BYTES)
    try:
        data = json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SessionFileError(
            f"{source.name} contains invalid JSON: {error}"
        ) from error
    if metadata is not None and not isinstance(metadata, SessionMetadata):
        metadata = SessionMetadata.read(metadata)
    providers = {
        "catalog": catalog,
        "database": database,
        "verification_registry": verification_registry,
    }
    providers = {key: value for key, value in providers.items() if value is not None}
    if repository is not None:
        for key, value in repository.providers.items():
            if value is not None:
                if key in providers and providers[key] is not value:
                    raise TypeError(
                        "Configure one consistent set of migration providers."
                    )
                providers[key] = value
    session = Session.from_projection(data, **providers)
    if metadata is not None:
        session.key, session.name = metadata.id, metadata.name
    if name is not None:
        if not isinstance(name, str):
            raise TypeError("Session names are text.")
        session.name = name
    from .repository import session_path

    destination = session_path(destination)
    converted_metadata = (
        None
        if metadata is None
        else replace(
            metadata,
            name=session.name,
            model_file=destination.name,
            legacy_source=source.name,
        )
    )
    repository = SessionRepository(**providers) if repository is None else repository
    status = repository.create(session, destination)
    return MigrationResult(source, session, status, converted_metadata)


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source", type=Path, help="Version 14 JSON workspace to preserve"
    )
    parser.add_argument(
        "--output", type=Path, help="New .py file, default: adjacent to the JSON"
    )
    parser.add_argument(
        "--metadata", type=Path, help="Legacy picker metadata to retain"
    )
    parser.add_argument("--name", help="Display name for the new native session")
    parser.add_argument("--cots-directory", type=Path)
    parser.add_argument(
        "--scripts-directory", type=Path, help="Explicitly trusted external scripts"
    )
    args = parser.parse_args(argv)
    try:
        result = convert_json(
            args.source,
            args.output,
            metadata=args.metadata,
            name=args.name,
            database=None
            if args.cots_directory is None
            else TabularDatabase(args.cots_directory),
            verification_registry=default_registry(directory=args.scripts_directory),
        )
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, f"Conversion failed: {error}\n")
    print(f"Created {result.storage.path}")
    print(f"Preserved {result.source}")
    if result.metadata is not None:
        print(
            "Retained session metadata:",
            json.dumps(result.metadata.projection(), ensure_ascii=False),
        )
    print("Analyses remain unexecuted. Open the .py file with Session.open().")
    return 0
