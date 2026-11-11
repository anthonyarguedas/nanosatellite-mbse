"""Shared repository for trusted Python sessions and optimistic atomic saves."""

from __future__ import annotations

import ast
import errno
import hashlib
import inspect
import json
import os
import stat
import sys
import threading
import types
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ..catalogs.database import DatabaseBacked
from ..core.configuration import ScriptConfiguration
from ..core.requirements import Parameter, Statement
from ..core.session import Session
from .source import SESSION_FORMAT, SessionSourceError, dumps

MAX_SESSION_BYTES = 16 * 1024 * 1024
_LOCKS = {}
_LOCKS_GUARD = threading.Lock()


class SessionFileError(ValueError):
    status = 400


class SessionConflict(SessionFileError):
    status = 409


class SessionNotFound(FileNotFoundError):
    status = 404


@dataclass(frozen=True)
class StorageStatus:
    path: Path
    revision: str
    canonical: bool = True
    storage: str = "python"

    @property
    def model_name(self):
        return self.path.name

    @property
    def writable(self):
        return self.canonical

    def projection(self):
        return {
            "path": str(self.path),
            "revision": self.revision,
            "modelName": self.model_name,
            "storage": self.storage,
            "writable": self.writable,
        }


@dataclass(frozen=True)
class _FileState:
    content: bytes
    mode: int
    exists: bool
    revision: str


def session_path(path):
    """Normalize parent aliases without following the final file's symlink."""
    value = Path(os.path.abspath(os.path.expanduser(os.fspath(path))))
    if value.suffix.lower() != ".py":
        raise SessionFileError(
            "Choose a .py session file. Convert legacy JSON explicitly before opening it."
        )
    return value.parent.resolve(strict=False) / value.name


def revision_for(path, content=None):
    """Bind content revisions to their canonical file path, including absence."""
    path = session_path(path)
    marker = b"missing\0" if content is None else b"source\0" + content
    return hashlib.sha256(os.fsencode(path) + b"\0" + marker).hexdigest()


def _read_regular(path, maximum, *, missing=False):
    try:
        info = path.lstat()
    except FileNotFoundError:
        if missing:
            return None, 0o600
        raise SessionNotFound(f"The session file is missing: {path}.") from None
    if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise SessionFileError(f"{path.name} must be a regular file, not a symlink.")
    if info.st_size > maximum:
        raise SessionFileError(
            f"{path.name} exceeds the {maximum}-byte file size limit."
        )
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise SessionFileError(f"{path.name} must not be a symlink.") from error
        raise
    with os.fdopen(descriptor, "rb") as handle:
        opened = os.fstat(handle.fileno())
        if not stat.S_ISREG(opened.st_mode):
            raise SessionFileError(f"{path.name} must be a regular file.")
        if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
            raise SessionConflict(f"{path.name} changed while opening. Retry the load.")
        content = handle.read(maximum + 1)
    if len(content) > maximum:
        raise SessionFileError(
            f"{path.name} exceeds the {maximum}-byte file size limit."
        )
    return content, stat.S_IMODE(opened.st_mode) & 0o777


def validate_session(session):
    """Validate graph identities and relationships without running calculations."""
    if not isinstance(session, Session):
        raise TypeError("build_session() must return a native Session instance.")
    if (
        not isinstance(session.key, str)
        or not session.key
        or not isinstance(session.name, str)
    ):
        raise SessionFileError(
            "A session needs a stable text key and a text display name."
        )
    objects = session.objects
    if (
        session.get("mission") is not session.mission
        or session.get("external") is not session.external
    ):
        raise SessionFileError(
            "The session must retain its native Mission and External roots."
        )
    if len({value.id for value in objects}) != len(objects):
        raise SessionFileError("Session object IDs must be unique.")
    for value in objects:
        text_fields = ("key", "id", "name", "definition")
        if isinstance(value, Statement):
            text_fields += ("text", "kind", "rationale", "origin")
        if any(not isinstance(getattr(value, field), str) for field in text_fields):
            raise SessionFileError("Domain identities and metadata must remain text.")
        if not value.key or not value.id:
            raise SessionFileError("Domain objects need nonempty keys and IDs.")
        if hasattr(value, "selection") and type(value.selection) is not bool:
            raise SessionFileError("Element selection flags must be Boolean.")
        if value.session is not session or session.get(value.key) is not value:
            raise SessionFileError(
                "Every object must belong to this native session registry."
            )
        references = [value.owner]
        if isinstance(value, Statement):
            references.extend(
                (
                    *value.sources,
                    *value.affected,
                    value.power_scope,
                    value.budget_scope,
                    value.subject,
                    *(method.source for method in value.verifications),
                )
            )
        if isinstance(value, DatabaseBacked):
            references.extend((*value.requirement_links, value.usage))
        for reference in references:
            if reference is not None:
                session.get(reference)
        if isinstance(value, (Statement, ScriptConfiguration)):
            for name, parameter in value.parameters.items():
                if not isinstance(parameter, Parameter) or parameter.name != name:
                    raise SessionFileError(
                        "Owned parameter names must match their records."
                    )
    session.validate_budgets()
    return session


def _canonical_source(source):
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, UnicodeDecodeError):
        return False
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "SESSION_FORMAT"
                for target in node.targets
            )
            and isinstance(node.value, ast.Constant)
            and type(node.value.value) is int
            and node.value.value == SESSION_FORMAT
        ):
            return True
    return False


def _construct(source, *, filename, session_class=Session, **providers):
    """Execute trusted configuration source with __main__ analysis entry disabled."""
    if not isinstance(source, str):
        raise TypeError("Session source must be text.")
    if len(source.encode("utf-8")) > MAX_SESSION_BYTES:
        raise SessionFileError("The session source exceeds its file size limit.")
    module_name = f"_nanosat_session_{uuid4().hex}"
    module = types.ModuleType(module_name)
    module.__file__ = str(filename)
    module.__package__ = None
    sys.modules[module_name] = module
    try:
        code = compile(source, str(filename), "exec")
        exec(code, module.__dict__)
        marker = module.__dict__.get("SESSION_FORMAT")
        if marker is not None and (type(marker) is not int or marker != SESSION_FORMAT):
            raise SessionFileError(f"Unsupported Python session format {marker!r}.")
        builder = module.__dict__.get("build_session")
        if not callable(builder):
            raise SessionFileError("The session file must define build_session().")
        supplied = {
            name: value for name, value in providers.items() if value is not None
        }
        try:
            inspect.signature(builder).bind(**supplied)
        except TypeError as error:
            raise SessionFileError(
                "build_session() must accept the configured catalog, database and verification_registry providers."
            ) from error
        session = builder(**supplied)
        if not isinstance(session, session_class):
            raise SessionFileError(
                f"build_session() must return {session_class.__name__}."
            )
        validate_session(session)
        if session.execution_evidence is not None:
            raise SessionFileError(
                "build_session() must construct configuration without executing analyses."
            )
        return session, marker == SESSION_FORMAT and _canonical_source(source)
    except SessionFileError:
        raise
    except Exception as error:
        raise SessionFileError(
            f"Could not load {Path(filename).name}: {type(error).__name__}: {error}"
        ) from error
    finally:
        if sys.modules.get(module_name) is module:
            del sys.modules[module_name]


def loads(source, *, filename="<session>", session_class=Session, **providers):
    """Build trusted source in memory with no storage attachment or analysis run."""
    return _construct(
        source, filename=filename, session_class=session_class, **providers
    )[0]


def _thread_lock(path):
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(str(path), threading.RLock())


def _sync_directory(path):
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        if (
            error.errno not in (errno.EINVAL, errno.ENOTSUP, errno.EBADF)
            and os.name != "nt"
        ):
            raise


class SessionRepository:
    """The file/revision boundary shared by the UI service and native REPL.

    Python session files and all imported code are trusted local code. This
    repository performs filesystem integrity checks, not code sandboxing.
    """

    def __init__(self, *, catalog=None, database=None, verification_registry=None):
        self.providers = {
            "catalog": catalog,
            "database": database,
            "verification_registry": verification_registry,
        }

    @staticmethod
    def _state(path, *, missing=False):
        content, mode = _read_regular(path, MAX_SESSION_BYTES, missing=missing)
        return _FileState(
            b"" if content is None else content,
            mode,
            content is not None,
            revision_for(path, content),
        )

    def load(self, path, *, session_class=Session):
        path = session_path(path)
        state = self._state(path)
        try:
            source = state.content.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise SessionFileError(
                f"{path.name} must contain UTF-8 Python source."
            ) from error
        session, canonical = _construct(
            source, filename=path, session_class=session_class, **self.providers
        )
        session._storage_status = StorageStatus(path, state.revision, canonical)
        return session

    def create(self, session, path):
        return self.save(session, path, create=True)

    def save(self, session, path=None, *, expected_revision=None, create=False):
        validate_session(session)
        previous = session.storage
        if path is None:
            if previous is None:
                raise SessionFileError("Choose a path for the new Python session.")
            path = previous.path
        path = session_path(path)
        if previous is not None and previous.path == path and not previous.writable:
            raise SessionFileError(
                "This hand-authored file has no canonical SESSION_FORMAT marker. "
                "Save to a new .py path to preserve its original code."
            )
        if expected_revision is None and previous is not None and previous.path == path:
            expected_revision = previous.revision
        source = dumps(session)
        restored, _ = _construct(
            source,
            filename=path,
            session_class=type(session),
            catalog=session.catalog,
            database=session.database,
            verification_registry=session.verification_registry,
        )
        if dumps(restored) != source:
            raise SessionSourceError(
                "The configured classes or providers do not restore canonical state faithfully. "
                "Review their restore hooks before saving."
            )
        encoded = source.encode("utf-8")
        if len(encoded) > MAX_SESSION_BYTES:
            raise SessionFileError("The generated session exceeds its file size limit.")
        with _thread_lock(path):
            path.parent.mkdir(parents=True, exist_ok=True)
            lock_path = path.with_name(path.name + ".lock")
            try:
                descriptor = os.open(
                    lock_path,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                )
            except FileExistsError:
                raise SessionConflict(
                    f"{path.name} is locked by another save. Confirm that process has stopped "
                    "before removing its .lock file."
                ) from None
            owned = os.fstat(descriptor)
            temporary = path.with_name(f"{path.name}.{uuid4().hex}.tmp")
            try:
                with os.fdopen(descriptor, "wb") as lock:
                    lock.write(
                        json.dumps(
                            {
                                "pid": os.getpid(),
                                "createdAt": datetime.now(timezone.utc).isoformat(),
                            }
                        ).encode("utf-8")
                        + b"\n"
                    )
                    lock.flush()
                    os.fsync(lock.fileno())
                    current = self._state(path, missing=True)
                    if create and current.exists:
                        raise SessionConflict(
                            f"{path.name} already exists. Choose a new path."
                        )
                    if expected_revision is None:
                        if current.exists:
                            raise SessionConflict(
                                f"Open {path.name} before replacing it, or save to a new path."
                            )
                    elif expected_revision != current.revision:
                        raise SessionConflict(
                            f"{path.name} changed. Reload or save an independent copy."
                        )
                    if current.exists and not _canonical_source(current.content):
                        raise SessionFileError(
                            "The existing file has no canonical SESSION_FORMAT marker. "
                            "Preserve its code and save to a new .py path."
                        )
                    permissions = current.mode if current.exists else 0o600
                    temporary_fd = os.open(
                        temporary,
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                        permissions,
                    )
                    with os.fdopen(temporary_fd, "wb") as output:
                        os.fchmod(output.fileno(), permissions)
                        output.write(encoded)
                        output.flush()
                        os.fsync(output.fileno())
                    if self._state(path, missing=True).revision != current.revision:
                        raise SessionConflict(
                            f"{path.name} changed while saving. Retry after reloading."
                        )
                    if current.exists:
                        os.replace(temporary, path)
                    else:
                        try:
                            os.link(temporary, path)
                        except FileExistsError:
                            raise SessionConflict(
                                f"{path.name} was created by another writer. Reopen it."
                            ) from None
                    _sync_directory(path.parent)
            finally:
                try:
                    temporary.unlink(missing_ok=True)
                finally:
                    try:
                        actual = lock_path.lstat()
                    except FileNotFoundError:
                        actual = None
                    if actual is not None and (actual.st_dev, actual.st_ino) == (
                        owned.st_dev,
                        owned.st_ino,
                    ):
                        lock_path.unlink()
            status = StorageStatus(path, revision_for(path, encoded))
            session._storage_status = status
            return status
