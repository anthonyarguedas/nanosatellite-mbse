# GUI

A local table editor for `framework.models.Mission`.
The GUI calls the public model API for containment, parameters, modes, states and verification.
Expressions execute trusted Python with the same permissions and imports as a script or REPL.
The GUI owns presentation, unsaved editor drafts and file storage.

## Run

Requires Node.js 22 or later and Python 3.8 or later.
From the repository root:

```sh
npm start --prefix framework/gui
```

Open <http://127.0.0.1:3000>.
The server listens only on the local machine.
There are no npm dependencies or browser build steps.

Settings:

- `PORT`: HTTP port (default 3000).
- `VERIFICATION_PYTHON`: Python interpreter (default `python3`).
- `MISSION_FILE`: Python session (default `framework/sessions/current.py`).

For an existing example:

```sh
MISSION_FILE=framework/sessions/example_eps_sizing.py npm start --prefix framework/gui
```

The selected file is editable. Use Save as before changing an example you want to retain.

## Tables

The left table lists the current owner's elements or external stakeholders.
Names open their child tables. The pencil opens the same parameter editor used for Requirements.
The heading pencil edits the current owner, including Mission and Orbit.
Requirement editors also expose statement templates, rationale and Verification Conditions.
Parameter creation is explicit and independent of statement text.

Modes, states and allocation records have a separate table.
Its Add form selects an owner and any required allocation target.
Their parameters use the same editor.
The evaluation selector chooses one explicit mode or state for values and verification.
Parameter override rows call `Property.bind()` and `Property.unbind()`.
COTS parameters remain fixed by their Python product class.

Values, rendered statements, pending inputs, errors and failure paths come from the models.
Previews apply the draft to a temporary copy and call the same methods as a saved configuration.
The GUI adds no allocation, normalization, power averaging or all-mode compliance policy.

## Python sessions

A session defines a `mission` instance or a `build_mission()` factory returning a Mission.
A single Mission stored under another global name is also accepted.
Python helpers and custom product classes remain ordinary Python definitions.
Imports resolve from the session's source directory and the Python environment.

Saving appends readable public model calls before any `if __name__ == "__main__"` block.
It preserves authored definitions and deliberately removed defaults.
Saved files have no GUI imports or loading protocol.
Import them directly or execute them with Python.
The Python download contains the saved configuration.
Unsaved editor drafts remain in the browser until Save.

New sessions contain a Mission with its native default Orbit.
Named sessions live under `framework/sessions/<id>/session.py`, beside `metadata.json`.
A custom workspace uses its adjacent `sessions/` directory.
Save as copies the Python configuration and retains its source context for relative resources and helper imports.
File revisions reject stale saves from another browser or Python process.
Reopen reloads external edits.

## Layout

- `public/`: tables, navigation and the shared object editor.
- `server/`: local HTTP routes and Python process transport.
- `backend/application.py`: session handles and atomic transactions.
- `backend/edits.py`: browser requests translated into public model calls.
- `backend/views.py`: native model values and reports formatted for display.
- `backend/repository.py`: trusted Python loading and revision-checked source storage.

The retired workbook model, restricted expression interpreter, script runners, exporters and migration code have been removed.
