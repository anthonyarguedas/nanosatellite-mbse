"""Trusted Python session persistence and browser projection adapters."""

from .callables import CallableBinding, CallableRegistry, UnserializableCallable
from .migrate import MigrationResult, SessionMetadata, convert_json, legacy_destination
from .repository import (
    SessionConflict,
    SessionFileError,
    SessionNotFound,
    SessionRepository,
    StorageStatus,
    loads,
    session_path,
)
from .source import SESSION_FORMAT, SessionSourceError, dumps

__all__ = [
    "CallableBinding",
    "CallableRegistry",
    "MigrationResult",
    "SESSION_FORMAT",
    "SessionConflict",
    "SessionFileError",
    "SessionMetadata",
    "SessionNotFound",
    "SessionRepository",
    "SessionSourceError",
    "StorageStatus",
    "UnserializableCallable",
    "convert_json",
    "dumps",
    "legacy_destination",
    "loads",
    "session_path",
]
