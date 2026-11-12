"""Authoritative application service shared by the HTTP bridge and native tools."""

from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import time
from collections import OrderedDict
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ..catalogs.cots import component_for_product, product_facts, products
from ..catalogs.database import FactReference, TabularDatabase
from ..catalogs.framework import default_catalog
from ..core.configuration import Mode
from ..core.elements import Element, Stakeholder
from ..core.predicates import VerificationMethod, restored_expression
from ..core.requirements import Parameter, Requirement, Statement
from ..core.verification import VerificationScript
from ..core.session import Session
from ..domains.registry import element_class
from ..persistence.callables import CallableRegistry
from ..persistence.locations import default_workspace, named_sessions_directory
from ..persistence.migrate import SessionMetadata, convert_json
from ..persistence.repository import (
    SessionConflict,
    SessionFileError,
    SessionNotFound,
    SessionRepository,
)
from ..persistence.source import dumps
from ..verifications.registry import default_registry
from .edits import apply_projection, clone_session, validate_graph
from .validation import TYPES, mapping, text, validate_projection
from .views import describe, tabs


class ServiceError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


@dataclass
class Handle:
    graph: Session
    session_id: str
    callables: CallableRegistry
    lineage: str
    accessed: float


@dataclass(frozen=True)
class EvidenceHandle:
    evidence: object
    lineage: str
    created: float


class Application:
    """One trusted repository configuration with independent browser draft handles.

    Paths and providers are supplied by the local launcher, never by requests.
    Opening Python files is trusted execution. Browser source is always limited
    to restricted parameter/predicate expressions.
    """

    def __init__(
        self,
        model_path=None,
        *,
        session_directory=None,
        cots_directory=None,
        script_directory=None,
    ):
        self.model_path = (
            default_workspace()
            if model_path is None
            else Path(model_path).expanduser().absolute()
        )
        if self.model_path.suffix.lower() not in (".json", ".py"):
            raise SessionFileError(
                "Choose a .py session or a retained legacy .json source."
            )
        self.current_path = self.model_path.with_suffix(".py")
        self.current_metadata = self.current_path.with_suffix(".metadata.json")
        self.legacy_path = (
            self.model_path
            if self.model_path.suffix.lower() == ".json"
            else self.model_path.with_suffix(".json")
        )
        self.directory = (
            Path(session_directory).expanduser().absolute()
            if session_directory
            else named_sessions_directory(self.model_path)
        )
        self.catalog = default_catalog()
        self.database = TabularDatabase(cots_directory)
        self.registry = default_registry(directory=script_directory)
        self.repository = SessionRepository(
            catalog=self.catalog,
            database=self.database,
            verification_registry=self.registry,
        )
        self.handles = OrderedDict()
        self.evidence = OrderedDict()
        self.max_handles = 128
        self.max_evidence = 128
        self.ttl = 4 * 3600

    def _providers(self):
        return {
            "catalog": self.catalog,
            "database": self.database,
            "verification_registry": self.registry,
        }

    @staticmethod
    def _session_id(value):
        if value == "current":
            return value
        if not isinstance(value, str) or not re.fullmatch(
            r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", value
        ):
            raise ServiceError("Invalid session ID.")
        return value

    def _metadata(self, session_id):
        self._session_id(session_id)
        if session_id == "current":
            return {
                "id": "current",
                "name": f"Current session ({self.current_path.name})",
                "template": "existing",
                "storage": "python",
            }
        folder = self.directory / session_id
        if folder.is_symlink() or not folder.is_dir():
            raise SessionNotFound("The session folder is missing.")
        native = folder / "metadata.json"
        metadata = SessionMetadata.read(
            native
            if native.exists() or native.is_symlink()
            else folder / "session.json"
        )
        if metadata.id != session_id:
            raise SessionFileError("The metadata ID differs from its session folder.")
        result = metadata.projection()
        if native.exists():
            if (
                not (folder / metadata.model_file).exists()
                and not (folder / metadata.model_file).is_symlink()
            ):
                raise SessionNotFound("The native session file is missing.")
        elif (
            not (folder / metadata.model_file).exists()
            and not (folder / f"{session_id}.json").exists()
        ):
            raise SessionNotFound("The session data file is missing.")
        return result

    def list_sessions(self):
        result = [self._metadata("current")]
        if self.directory.exists():
            if self.directory.is_symlink() or not self.directory.is_dir():
                raise SessionFileError(
                    "The session directory must be a normal directory."
                )
            for folder in self.directory.iterdir():
                if folder.is_symlink() or not folder.is_dir():
                    continue
                if not re.fullmatch(
                    r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", folder.name
                ):
                    continue
                try:
                    result.append(self._metadata(folder.name))
                except (SessionNotFound, FileNotFoundError):
                    continue
        return [
            result[0],
            *sorted(result[1:], key=lambda metadata: metadata["name"].lower()),
        ]

    def _publish_current_metadata(self):
        metadata = SessionMetadata(
            "current",
            self._metadata("current")["name"][:80],
            "existing",
            datetime.now(timezone.utc).isoformat(),
            self.current_path.name,
            self.legacy_path.name if self.legacy_path.exists() else "",
        )
        try:
            metadata.create(self.current_metadata)
        except SessionConflict:
            recorded = SessionMetadata.read(self.current_metadata)
            if (
                recorded.id != "current"
                or recorded.model_file != self.current_path.name
            ):
                raise SessionConflict(
                    "The current-session metadata belongs to another model."
                )

    def _load_current(self):
        if self.current_path.exists() or self.current_path.is_symlink():
            graph = self.repository.load(self.current_path)
            self._publish_current_metadata()
            return graph
        if self.current_metadata.exists() or self.current_metadata.is_symlink():
            SessionMetadata.read(self.current_metadata)
            raise SessionNotFound(
                "The authoritative Python session is missing. Restore it or choose a new workspace."
            )
        if self.legacy_path.exists() or self.legacy_path.is_symlink():
            try:
                graph = convert_json(
                    self.legacy_path, self.current_path, repository=self.repository
                ).session
            except SessionConflict:
                graph = self.repository.load(self.current_path)
            self._publish_current_metadata()
            return graph
        # A selected, never-created workspace starts with empty tables.
        graph = Session(**self._providers())
        try:
            self.repository.create(graph, self.current_path)
        except SessionConflict:
            graph = self.repository.load(self.current_path)
        self._publish_current_metadata()
        return graph

    def _load_named(self, session_id):
        metadata = self._metadata(session_id)
        folder = self.directory / session_id
        native_metadata = folder / "metadata.json"
        target = folder / metadata.get("modelFile", "session.py")
        if native_metadata.exists() or native_metadata.is_symlink():
            return self.repository.load(target)
        if target.exists() or target.is_symlink():
            graph = self.repository.load(target)
        else:
            legacy = folder / f"{session_id}.json"
            try:
                graph = convert_json(
                    legacy,
                    target,
                    metadata=folder / "session.json",
                    repository=self.repository,
                ).session
            except SessionConflict:
                graph = self.repository.load(target)
        converted = SessionMetadata(
            metadata["id"],
            metadata["name"],
            metadata["template"],
            metadata["createdAt"],
            target.name,
            f"{session_id}.json",
        )
        try:
            converted.create(native_metadata)
        except SessionConflict:
            current = SessionMetadata.read(native_metadata)
            if current.id != session_id:
                raise SessionConflict(
                    "Another session metadata record was published concurrently."
                )
        return graph

    def _prune(self):
        now = time.monotonic()
        for store, limit in (
            (self.handles, self.max_handles),
            (self.evidence, self.max_evidence),
        ):
            for token, entry in tuple(store.items()):
                timestamp = (
                    entry.accessed if isinstance(entry, Handle) else entry.created
                )
                if now - timestamp > self.ttl:
                    del store[token]
            while len(store) > limit:
                store.popitem(last=False)

    def _store(self, graph, session_id, *, parent=None):
        token = secrets.token_urlsafe(32)
        self.handles[token] = Handle(
            graph,
            session_id,
            CallableRegistry() if parent is None else parent.callables,
            secrets.token_urlsafe(24) if parent is None else parent.lineage,
            time.monotonic(),
        )
        self._prune()
        return token

    def _view(self, token, *, include_library=True):
        handle = self.handles[token]
        handle.accessed = time.monotonic()
        graph = handle.graph
        status = graph.storage
        result = {
            "workspace": graph.to_projection(callables=handle.callables),
            "handle": token,
            "session": self._metadata(handle.session_id),
            "revision": None if status is None else status.revision,
            "modelName": self.current_path.name
            if status is None
            else status.model_name,
            "storage": "python",
            "writable": status is None or status.writable,
            "metadata": describe(graph, callables=handle.callables),
            "calculationSignature": graph.calculation_signature(),
            "protocolVersion": 1,
        }
        if include_library:
            result["catalog"] = self.catalog.projection()
            result["products"] = products(self.database, include_pins=False)
        return result

    def load_session(self, session_id="current"):
        """Load a trusted native graph for a local UI or CLI application."""
        self._session_id(session_id)
        graph = (
            self._load_current()
            if session_id == "current"
            else self._load_named(session_id)
        )
        graph.reconcile_defaults()
        return graph

    def open(self, session_id="current"):
        return self._view(self._store(self.load_session(session_id), session_id))

    def _resolve(self, request, *, session_id=None):
        self._prune()
        token = request.get("handle", request.get("draftToken"))
        if token is not None:
            if not isinstance(token, str) or token not in self.handles:
                raise ServiceError(
                    "The session handle expired. Reopen the session and rerun analyses.",
                    410,
                )
            handle = self.handles[token]
            if session_id is not None and handle.session_id != session_id:
                raise ServiceError("The handle belongs to another session.")
            handle.accessed = time.monotonic()
            self.handles.move_to_end(token)
            return token, handle
        raise ServiceError(
            "A native draft handle is required. Reopen the session.", 410
        )

    def _draft(self, request, *, session_id=None):
        token, handle = self._resolve(request, session_id=session_id)
        edits = request.get("stateEdits", [])
        if not isinstance(edits, list) or len(edits) > 256:
            raise ServiceError("Supply at most 256 parameter state edits.")
        if request.get("workspace") is None and not edits:
            return token, handle
        for edit in edits:
            mapping(
                edit,
                "Parameter state edit",
                {"target", "parameter", "values", "lastEdited", "merge"},
            )
        if request.get("workspace") is not None:
            graph = apply_projection(
                handle.graph,
                request["workspace"],
                callables=handle.callables,
                state_edits=edits,
            )
        else:
            graph = clone_session(handle.graph)
            for edit in edits:
                graph.configure_parameter_states(
                    edit["target"],
                    edit["parameter"],
                    values=edit.get("values"),
                    last_edited=edit.get("lastEdited"),
                    merge=edit.get("merge", False),
                )
        validate_graph(graph)
        if edits:
            validate_projection(graph.to_projection(callables=handle.callables))
        token = self._store(graph, handle.session_id, parent=handle)
        return token, self.handles[token]

    def draft(self, request):
        token, _ = self._draft(request, session_id=request.get("session"))
        return self._view(token, include_library=False)

    def save(self, request, *, session_id="current"):
        token, handle = self._draft(request, session_id=session_id)
        revision = request.get("revision")
        if not isinstance(revision, str):
            raise ServiceError(
                "Supply the opened session's revision before saving.", 409
            )
        status = handle.graph.storage
        if status is None:
            raise ServiceError("This draft has no storage destination. Use Save as.")
        self.repository.save(handle.graph, status.path, expected_revision=revision)
        return self._view(token)

    def create(self, request):
        template = request.get("template")
        if template not in ("blank", "copy"):
            raise ServiceError("Create a blank session or use Save as for a copy.")
        if template != "copy" and request.get("workspace") is not None:
            raise ServiceError("Only Save as accepts an existing workspace.")
        if template == "copy":
            _, handle = self._draft(request)
            graph = clone_session(handle.graph)
        else:
            graph = Session(**self._providers())
        return self._create_graph(graph, name=request.get("name"), template=template)

    def create_session(self, graph, *, name, template="copy"):
        """Save an independent named copy supplied by trusted native Python code."""
        if not isinstance(graph, Session):
            raise TypeError("Create a named session from a native Session instance.")
        return self._create_graph(clone_session(graph), name=name, template=template)

    def _create_graph(self, graph, *, name, template):
        name = text(name, "Session name", 80, required=True, line=True).strip()
        if re.search(r"[\x00-\x1f\x7f]", name):
            raise ServiceError("Session names contain one printable line.")
        if template not in ("blank", "copy"):
            raise ServiceError("Create a blank session or use Save as for a copy.")
        graph.name = name
        graph.key = str(uuid4())
        graph.clear_evidence()
        self.directory.mkdir(parents=True, exist_ok=True)
        lock_path = self.directory / ".create.lock"
        try:
            descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise SessionConflict(
                "Another session creation is active. Retry after it finishes."
            ) from None
        owned_lock = os.fstat(descriptor)
        folder = None
        try:
            with os.fdopen(descriptor, "w") as lock:
                lock.write(
                    json.dumps(
                        {
                            "pid": os.getpid(),
                            "createdAt": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                )
                lock.flush()
                os.fsync(lock.fileno())
                if any(
                    metadata["name"].lower() == name.lower()
                    for metadata in self.list_sessions()
                ):
                    raise SessionConflict("A session with this name already exists.")
                session_id = graph.key
                candidate = self.directory / session_id
                candidate.mkdir()
                folder = candidate
                self.repository.create(graph, folder / "session.py")
                SessionMetadata(
                    session_id, name, template, datetime.now(timezone.utc).isoformat()
                ).create(folder / "metadata.json")
        except Exception:
            if folder is not None:
                shutil.rmtree(folder)
            raise
        finally:
            try:
                actual = lock_path.lstat()
            except FileNotFoundError:
                actual = None
            if actual is not None and (actual.st_dev, actual.st_ino) == (
                owned_lock.st_dev,
                owned_lock.st_ino,
            ):
                lock_path.unlink()
        result = self._view(self._store(graph, session_id))
        result["sessions"] = self.list_sessions()
        return result

    def _selected_evidence(self, request, handle):
        token = request.get("evidenceToken")
        supplied = request.get("scriptResults")
        if token is None and isinstance(supplied, dict):
            token = supplied.get("evidenceToken")
        if token is None:
            if isinstance(supplied, dict) and supplied.get("runs"):
                raise ServiceError(
                    "Browser-supplied execution values are not evidence. Run Python to obtain a server evidence token."
                )
            return None
        record = self.evidence.get(token) if isinstance(token, str) else None
        if record is None or record.lineage != handle.lineage:
            raise ServiceError(
                "The execution evidence is unknown or belongs to another session. Run Python again.",
                410,
            )
        self.evidence.move_to_end(token)
        return record.evidence

    @staticmethod
    def _evidence_current(graph, evidence):
        if evidence is None:
            return False
        context = graph.evaluation_context()
        if (
            evidence.signature != context.signature
            or evidence.cots_signature != context.cots_signature
        ):
            return False
        return all(
            script.revision_is_current
            and all(
                result.implementation_revision == script.current_revision
                for result in evidence.runs.values()
                if result.script == script.key
            )
            for script in graph.scripts
        )

    def evaluate(self, request):
        token, handle = self._draft(request, session_id=request.get("session"))
        evidence = self._selected_evidence(request, handle)
        handle.graph.clear_evidence()
        kwargs = {"evidence": evidence}
        if "mode" in request:
            kwargs["mode"] = request["mode"]
        result = handle.graph.evaluate(**kwargs)
        result.update(
            {
                "handle": token,
                "calculationSignature": handle.graph.calculation_signature(),
                "evidenceCurrent": self._evidence_current(handle.graph, evidence),
                "view": self._view(token, include_library=False),
            }
        )
        return result

    def run(self, request, cancel=None):
        token, handle = self._draft(request, session_id=request.get("session"))
        evidence = self._selected_evidence(request, handle)
        script = request.get("script")
        if script is not None and not isinstance(script, (str, list)):
            raise ServiceError("Choose a registered script instance.")
        if isinstance(script, list) and (
            len(script) > 64 or any(not isinstance(value, str) for value in script)
        ):
            raise ServiceError("Choose at most 64 registered script instances.")
        kwargs = {"evidence": evidence, "cancel": cancel, "total_timeout_ms": 30000}
        if "mode" in request:
            kwargs["mode"] = request["mode"]
        result = handle.graph.run(script, **kwargs)
        if cancel is not None and cancel.is_set():
            raise ServiceError("Python execution was cancelled.", 499)
        evidence_token = secrets.token_urlsafe(32)
        self.evidence[evidence_token] = EvidenceHandle(
            result, handle.lineage, time.monotonic()
        )
        self._prune()
        return {
            **result.projection(),
            "evidenceToken": evidence_token,
            "handle": token,
            "calculationSignature": result.signature,
            "evidenceCurrent": self._evidence_current(handle.graph, result),
        }

    def export(self, request, *, native=True):
        token, handle = self._draft(request, session_id=request.get("session"))
        name = handle.graph.name or self._metadata(handle.session_id)["name"]
        stem = re.sub(r"[^A-Za-z0-9_]", "_", name)
        if native:
            return {
                "source": dumps(handle.graph),
                "filename": f"{stem}-session.py",
                "handle": token,
            }
        return {
            "workspace": handle.graph.to_projection(callables=handle.callables),
            "filename": f"{stem}-projection.json",
            "handle": token,
        }

    def artifacts(self, request):
        token, handle = self._draft(request, session_id=request.get("session"))
        evidence = self._selected_evidence(request, handle)
        owner = handle.graph.get(request.get("context"))
        if owner.role != "eps" or owner.selection:
            raise ServiceError("Choose an EPS tab to export.")
        selected = [
            component
            for component in handle.graph.cots_components
            if component.owner is owner
        ]
        if not selected:
            raise ServiceError("Add at least one COTS selection before exporting.")
        if any(component.product_record is None for component in selected):
            raise ServiceError(
                "Review missing product selections before exporting architecture artifacts."
            )
        checked = handle.graph.evaluate(evidence=evidence)
        return {
            "workspace": handle.graph.to_projection(callables=handle.callables),
            "catalog": self.catalog.projection(),
            "products": products(self.database),
            "checks": checked["results"],
            "componentChecks": {
                result["key"]: result for result in checked["components"]
            },
            "tabs": tabs(handle.graph),
            "handle": token,
        }

    def command(self, request):
        _, base = self._resolve(request, session_id=request.get("session"))
        graph = clone_session(base.graph)
        command = mapping(request.get("command"), "Domain command")
        name = command.get("name")
        target = command.get("target")
        if name == "add_element":
            definition = command.get("definition")
            if definition not in self.catalog.by_model:
                raise ServiceError("Choose a catalog element definition.")
            value = element_class(definition)(
                command.get("id", ""),
                name=command.get("label"),
                key=command.get("key"),
                definition=definition,
            )
            graph.add(value, owner=graph.get(command["owner"]))
        elif name == "add_stakeholder":
            value = Stakeholder(
                command.get("id", ""),
                name=command.get("label", ""),
                key=command.get("key"),
                stakeholder_type=command.get("type", "Mission Stakeholder"),
            )
            graph.add(value, owner=graph.external)
        elif name == "add_cots":
            value = component_for_product(
                command["product"],
                database=self.database,
                id=command.get("id", ""),
                key=command.get("key"),
                quantity=command.get("quantity", 1),
            )
            graph.add(value, owner=graph.get(command["owner"]))
        elif name == "add_script":
            definition = command["definition"]
            if not isinstance(definition, str) or not re.fullmatch(
                r"[a-z][a-z0-9_]{0,79}", definition
            ):
                raise ServiceError("Choose a registered analysis definition.")
            value = self.registry.create(
                definition, command.get("id", ""), key=command.get("key")
            )
            value.assert_current()
            graph.add(value)
        elif name == "add_requirement":
            parameters = tuple(
                Parameter(
                    item["name"],
                    TYPES[item.get("type", "float")],
                    item.get("unit", ""),
                    value=item.get("value"),
                    expression=None
                    if item.get("expression") is None
                    else restored_expression(item["expression"]),
                )
                for item in command.get("parameters", ())
            )
            owner = graph.get(command.get("owner", "external"))
            definition = graph.catalog.by_model.get(owner.definition)
            prefix = (
                "MIS"
                if owner is graph.mission
                else definition.prefix
                if definition is not None
                else "REQ"
            )
            value = Requirement(
                command.get("id") or graph.next_id("Requirement", prefix),
                command["text"],
                key=command.get("key"),
                parameters=parameters,
                rationale=command.get("rationale", ""),
            )
            graph.add(value, owner=owner)
        elif name == "remove":
            graph.remove(target)
        elif name == "rename":
            graph.rename(target, command["id"])
        elif name == "retype":
            graph.retype(target, command["definition"])
        elif name == "substitute_product":
            graph.substitute_product(target, command["product"])
        elif name in ("set_value", "set_expression", "set_unit", "replace_binding"):
            value = graph.get(target)
            if not hasattr(value, "parameters"):
                raise ServiceError("Choose a requirement or analysis parameter.")
            parameter = command["parameter"]
            if name == "set_unit":
                text(command["unit"], "Units", 100, line=True)
                graph.configure_parameter(
                    value, replace(value.parameters[parameter], unit=command["unit"])
                )
            elif name == "set_value":
                graph.configure_parameter(
                    value,
                    replace(
                        value.parameters[parameter],
                        value=command.get("value"),
                        expression=None,
                    ),
                )
            else:
                source = command.get("expression")
                if source is not None:
                    text(source, "Parameter expression", 5000, line=True)
                graph.configure_parameter(
                    value,
                    replace(
                        value.parameters[parameter],
                        value=None,
                        expression=None
                        if source is None
                        else restored_expression(source),
                    ),
                )
        elif name == "set_property":
            value = graph.get(target)
            if not isinstance(value, Element):
                raise ServiceError("Choose a component property owner.")
            value.set_property(command["property"], command.get("value"))
        elif name == "configure_component":
            value = graph.get(target)
            if not isinstance(value, Element):
                raise ServiceError("Choose an existing component.")
            if "quantity" in command:
                value.quantity = command["quantity"]
            if "requirements" in command:
                value.requirement_links = tuple(graph.get(key) for key in command["requirements"])
        elif name == "set_text":
            value = graph.get(target)
            if not isinstance(value, Statement):
                raise ServiceError(
                    "Choose a requirement or statement to edit its text."
                )
            value.text = text(command["text"], "Requirement text", 50000)
        elif name == "set_relationships":
            value = graph.get(target)
            if not isinstance(value, Statement):
                raise ServiceError(
                    "Choose a requirement or statement for source and allocation links."
                )
            if "sources" in command:
                value.sources = tuple(graph.get(item) for item in command["sources"])
            if "affected" in command:
                value.affected = tuple(graph.get(item) for item in command["affected"])
        elif name == "set_verifications":
            value = graph.get(target)
            if not isinstance(value, Statement):
                raise ServiceError(
                    "Choose a requirement or statement for verification conditions."
                )
            value.verifications = tuple(
                VerificationMethod(
                    item.get("label", item["key"]),
                    restored_expression(item["condition"]),
                    key=item["key"],
                    source=None
                    if not item.get("source")
                    else graph.get(item["source"]),
                )
                for item in command["methods"]
            )
        elif name == "select_fact":
            value = graph.get(target)
            if not hasattr(value, "product_record") or value.product_record is None:
                raise ServiceError(
                    "Choose a current database product before selecting facts."
                )
            record = next(
                (
                    fact
                    for fact in value.product_record.facts
                    if fact.id == command["fact"]
                ),
                None,
            )
            if record is None:
                raise ServiceError("Select a current database fact.")
            selection = FactReference.select(
                command.get("reference") or value.suggested_reference_name(record),
                record,
                key=command.get("key"),
            )
            graph.configure_facts(
                value,
                tuple(item for item in value.facts if item.name != selection.name)
                + (selection,),
            )
        elif name == "set_facts":
            graph.configure_facts(
                target, tuple(FactReference(**item) for item in command["facts"])
            )
        elif name == "add_mode":
            graph.add_mode(
                Mode(
                    command["label"],
                    command.get("sunlight"),
                    command.get("eclipse"),
                    command.get("key") or str(uuid4()),
                )
            )
        elif name == "rename_mode":
            graph.rename_mode(target, command["label"])
        elif name == "remove_mode":
            graph.remove_mode(target)
        elif name == "configure_mode":
            graph.configure_mode(
                target,
                **{
                    field: command[field]
                    for field in ("sunlight", "eclipse")
                    if field in command
                },
            )
        elif name == "connect_power":
            graph.connect_power(target, command.get("roots"))
        elif name == "disconnect_power":
            graph.disconnect_power(target)
        elif name == "configure_load":
            changes = dict(mapping(command.get("changes", {}), "Load changes", {
                "quantity", "accounting", "host", "rationale", "states",
                "assignments", "duties", "allocations",
            }))
            if "states" in changes:
                from ..core.configuration import ComponentState

                changes["states"] = tuple(
                    ComponentState(**state) for state in changes["states"]
                )
            graph.configure_load(target, **changes)
        elif name == "update_definition":
            value = graph.get(target)
            if not isinstance(value, VerificationScript):
                raise ServiceError("Choose a registered analysis instance.")
            value.update_definition()
        else:
            raise ServiceError("Unknown native domain command.")
        validate_graph(graph)
        validate_projection(graph.to_projection(callables=base.callables))
        token = self._store(graph, base.session_id, parent=base)
        return self._view(token, include_library=False)

    def dispatch(self, request, *, cancel=None):
        operation = request.get("operation")
        if operation == "ping":
            return {"pid": os.getpid(), "engine": "nanosat_mbse", "protocolVersion": 1}
        if operation == "sessions":
            return {"sessions": self.list_sessions()}
        if operation == "open":
            return self.open(request.get("session", "current"))
        if operation == "create":
            return self.create(request)
        if operation == "save":
            return self.save(request, session_id=request.get("session", "current"))
        if operation == "draft":
            return self.draft(request)
        if operation == "command":
            return self.command(request)
        if operation == "describe":
            if not request.get("handle"):
                return self.open(request.get("session", "current"))
            token, _ = self._resolve(request, session_id=request.get("session"))
            return self._view(token, include_library=False)
        if operation == "evaluate":
            return self.evaluate(request)
        if operation == "run":
            return self.run(request, cancel=cancel)
        if operation == "scripts":
            return {"scripts": self.registry.describe()}
        if operation == "catalog":
            return self.catalog.projection()
        if operation == "products":
            return products(
                self.database, include_pins=request.get("includePins", False)
            )
        if operation == "cots_facts":
            return product_facts(request.get("product"), self.database)
        if operation == "export_python":
            return self.export(request)
        if operation == "export_json":
            return self.export(request, native=False)
        if operation == "artifacts":
            return self.artifacts(request)
        raise ServiceError("Unknown Python application operation.")
