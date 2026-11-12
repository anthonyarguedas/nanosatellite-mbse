# GUI

A local JavaScript workbook with a GUI-private compatibility model.
The browser handles rendering, navigation and unsaved editor drafts.
The Python backend handles workbook edits, validation and session storage.
The new `framework.models` API is independent and is not yet edited by this GUI.

## Run

Requires Node.js 22 or later and Python 3.8 or later.
From the repository root:

```sh
npm start --prefix framework/gui
```

Open <http://127.0.0.1:3000>.
The server listens only on the local machine.
There are no npm dependencies or browser build steps.
The source bootstrap at `backend/service.py` loads the GUI backend.

Environment settings:

- `PORT`: HTTP port (default 3000).
- `VERIFICATION_PYTHON`: Python interpreter (default `python3`).
- `MISSION_FILE`: current Python session path.
- `NANOSAT_MBSE_COTS_DIR`: alternate product database directory.

## Organization

- `public/`: browser presentation and editor drafts.
- `public/editors/`: requirement, verification, COTS and mode editors.
- `server/`: HTTP routes and supervised Python transport.
- `server/exporters/`: KiCad and Fprime formatting over validated data.
- `backend/`: Python application service and browser edit validation.
- `backend/legacy/`: existing workbook classes, expressions and session persistence.
- `../models/`: independent public model API for new Python scripts.
- `../cots/`: shared product facts and sources.
- `../sessions/`: current and named sessions.

## Sessions

The default workspace is `framework/sessions/current.py`.
Named sessions live in `framework/sessions/<id>/session.py`, beside their `metadata.json`.
A custom workspace uses a neighboring `sessions/` directory.
A workspace already inside `sessions/` shares that directory.

New sessions start with empty tables.
Use Save as to copy an existing session, including an example session.
Example sessions have no automatic creation or regeneration behavior.
Revision checks reject stale saves from another browser or Python process.

The GUI can migrate a retained version-14 JSON workspace to an adjacent Python file.
It preserves the original JSON.
Existing native metadata prevents a missing Python session from being silently regenerated.

Existing workbook sessions can be inspected through the compatibility package:

```python
from framework.gui.backend.legacy import Session

session = Session.open("framework/sessions/current.py")
session.save()
```

New Python configurations use `framework.models.Mission`.
See the [model API](../models/README.md).
Canonical version 1 workbook imports are redirected in memory when loaded.
New GUI saves use the compatibility package's import paths.

Python session files and native functions are trusted local code.
Opening a session constructs configuration without running analysis scripts.
Browser expressions use the existing bounded Python expression interpreter.
The browser supplies no import paths, source files or shell commands.

## Analysis status

The previous study factories, CLI and numerical analyses have been removed.
The default script picker is empty until replacement implementations are supplied.
Saved script rows retain their interfaces and bindings as unresolved definitions.
Historical material in `analyses/` and `demo/` describes the removed analyses.
See the [framework guide](../README.md) for the current library layout.
