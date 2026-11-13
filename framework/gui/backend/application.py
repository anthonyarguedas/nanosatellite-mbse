"""Session handles and file transactions around framework.models."""

from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import re
import secrets
import sys
from uuid import uuid4

from . import repository
from .edits import apply
from .views import describe, recommendations


class ServiceError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


@dataclass
class Handle:
    mission: object
    path: Path
    source: str
    assignment: str
    module: object
    session: str
    catalog: tuple

    @property
    def revision(self):
        return repository.revision(self.source)


class Application:
    def __init__(self, model_path=None, *, session_directory=None):
        self.path = Path(model_path or Path(__file__).resolve().parents[2] / "sessions" / "current.py").expanduser().absolute()
        if self.path.suffix != ".py":
            raise ValueError("Choose a Python session file (.py).")
        self.directory = Path(session_directory).expanduser().absolute() if session_directory else (
            self.path.parent if self.path.parent.name == "sessions" else self.path.parent / "sessions"
        )
        self.handles = OrderedDict()

    def location(self, session):
        if session == "current":
            return self.path
        if not isinstance(session, str) or not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", session):
            raise ServiceError("Invalid session ID.")
        return self.directory / session / "session.py"

    def metadata(self, session):
        path = self.location(session)
        if session == "current":
            return {"id": session, "name": f"Current ({path.name})"}
        value = json.loads(path.with_name("metadata.json").read_text(encoding="utf-8"))
        return {"id": session, "name": value["name"]}

    def list_sessions(self):
        result = [self.metadata("current")]
        if self.directory.exists():
            for folder in self.directory.iterdir():
                if folder.is_dir() and (folder / "session.py").is_file():
                    try:
                        result.append(self.metadata(folder.name))
                    except (ValueError, KeyError, FileNotFoundError):
                        continue
        return [result[0], *sorted(result[1:], key=lambda row: row["name"].lower())]

    def open(self, session):
        path = self.location(session)
        if not path.exists() and session == "current":
            repository.save(path, "from framework.models import Mission\n\nmission = Mission()\n")
        mission, source, assignment, module = repository.load(path)
        catalog = tuple(getattr(module, "cots_catalog", ()))
        handle = Handle(mission, path, source, assignment, module, session, catalog)
        token = secrets.token_urlsafe(24)
        self.handles[token] = handle
        while len(self.handles) > 32:
            _, expired = self.handles.popitem(last=False)
            sys.modules.pop(expired.module.__name__, None)
        return token, handle

    def handle(self, data):
        token = data.get("handle")
        if token not in self.handles:
            raise ServiceError("Reopen the session to reconnect.", 410)
        handle = self.handles[token]
        if data.get("revision", handle.revision) != handle.revision:
            raise repository.Conflict("This browser view is stale. Reopen the session.")
        self.handles.move_to_end(token)
        return token, handle

    def view(self, token, handle, data=None, *, mission=None, selected=None):
        data = data or {}
        mission = mission or handle.mission
        mode = mission.get(data["mode"]) if data.get("mode") else None
        with repository.source_directory(Path(handle.module.__file__).parent):
            workspace = describe(mission, mode=mode, selected=selected)
        return {"handle": token, "revision": handle.revision, "session": self.metadata(handle.session),
                "filename": handle.path.name, "workspace": workspace}

    def dispatch(self, data):
        operation = data.get("operation")
        if operation == "sessions":
            return self.list_sessions()
        if operation == "open":
            token, handle = self.open(data.get("session", "current"))
            return {**self.view(token, handle), "sessions": self.list_sessions()}
        if operation == "create":
            name = data.get("name", "").strip()
            if not name or len(name) > 80:
                raise ServiceError("Enter a session name of 1 to 80 characters.")
            session = str(uuid4())
            path = self.location(session)
            source = "from framework.models import Mission\n\nmission = Mission()\n"
            if data.get("copy"):
                _, original = self.handle(data)
                source = repository.anchored_copy(original.source, Path(original.module.__file__), original.module.__package__)
                source = repository.append_calls(source, original.assignment, []) if original.assignment else source
            repository.save(path, source)
            path.with_name("metadata.json").write_text(json.dumps({"name": name}, indent=2) + "\n", encoding="utf-8")
            token, handle = self.open(session)
            return {**self.view(token, handle), "sessions": self.list_sessions()}
        token, handle = self.handle(data)
        if operation in ("inspect", "evaluate", "describe"):
            return self.view(token, handle, data, selected=data.get("path"))
        if operation == "recommend_cots":
            component = handle.mission.get(data["path"])
            mode = handle.mission.get(data["mode"]) if data.get("mode") else None
            with repository.source_directory(Path(handle.module.__file__).parent):
                return recommendations(component, handle.catalog, sort_by=data.get("sortBy"),
                                       reverse=data.get("reverse", False), limit=data.get("limit"), mode=mode)
        if operation in ("command", "preview"):
            with repository.source_directory(Path(handle.module.__file__).parent):
                mission = deepcopy(handle.mission, {id(item): item for item in handle.mission.imports.values()})
                calls, selected = apply(mission, data["command"])
            # A removed evaluation selection returns the browser to Default.
            view_data = dict(data)
            removed = data["command"].get("path", "")
            if data["command"]["action"] == "remove" and data.get("mode") and (
                data["mode"] == removed or data["mode"].startswith(removed + ".")
            ):
                view_data["mode"] = ""
            # Compute the response before publishing the transaction.
            result = self.view(token, handle, view_data, mission=mission, selected=selected)
            if operation == "preview":
                return result
            if calls:
                source = repository.append_calls(handle.source, handle.assignment, calls)
                repository.save(handle.path, source, handle.revision)
                handle.mission, handle.source, handle.assignment = mission, source, ""
            elif repository.revision(handle.path.read_text(encoding="utf-8")) != handle.revision:
                raise repository.Conflict("The session changed on disk. Reopen it before saving.")
            result["revision"] = handle.revision
            result["selected"] = selected
            return result
        if operation == "export_python":
            source = repository.append_calls(handle.source, handle.assignment, []) if handle.assignment else handle.source
            source = repository.anchored_copy(source, Path(handle.module.__file__), handle.module.__package__)
            return {"filename": handle.path.name, "source": source}
        raise ServiceError("Unknown operation.")
