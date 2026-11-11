# Requirements UI

A JavaScript workbook over the native `nanosat_mbse` Python library.
Python owns the model, lifecycle, validation, calculations, analyses and session storage.
The browser owns rendering, navigation and unsaved editor drafts.
The UI and a Python REPL use the same domain classes and calculation engine.

## Run

Install Node.js 22 or later and Python 3.8 or later.
From the repository root:

```sh
cd framework/requirements-ui
npm start
```

Open <http://127.0.0.1:3000>.
The server listens only on the local machine.
Set `PORT` to select another port and `VERIFICATION_PYTHON` to select an interpreter or virtual environment.
There are no npm dependencies or browser build steps.
The source launcher locates the Python package in `framework/python/src`.

The default workspace is `framework/sessions/current.py`.
If it has never existed and no legacy source is present, opening it creates a blank session.
Choose another file relative to the directory where the server starts:

```sh
MISSION_FILE=/path/to/mission.py PORT=3002 npm start
```

An existing version-14 `.json` workspace is a retained migration source.
Its first open creates an adjacent Python session and leaves the JSON unchanged.
Subsequent opens and saves use the Python file.
Once native metadata records a session, a missing Python file remains an error and is never regenerated from stale JSON.
Use copies when exploring the supplied [demo](demo/README.md).

## Code organization

- `public/`: browser projections, presentation helpers and editor drafts.
- `public/editors/`: requirement, verification, component power and COTS editors.
- `server/`: HTTP routes, supervised Python transport and output adapters.
- `server/exporters/`: KiCad and Fprime output formatting over Python-validated data.
- `../python/src/nanosat_mbse/`: generic classes, engineering domains, catalogs, verifications, persistence and application service.
- `../cots/`: live shared product facts and sources.
- `../sessions/`: the current workspace and individual named Python sessions.

The retired JavaScript model and request-local Python worker have been removed.
There is one active engineering implementation.
See the [Python API](../python/README.md), [session format](../python/docs/sessions.md) and [service protocol](../python/docs/http-service.md).

## Sessions and shared REPL access

**New session** always creates empty tables.
Open any existing session and choose **Save as…** to reuse its configuration under another name.
The supplied **Generic EPS Example** is an ordinary editable saved session in the picker.
It is copied through Save as and has no special creation or automatic regeneration behavior.
If no sessions exist, start blank and add the desired elements.
Each browser tab keeps its own native draft handle and selected session.
The URL retains the session ID and tab.
Valid table edits autosave to that session.
Requirement, component and COTS panes retain drafts until their Save action.
Save as includes valid open drafts in an independent copy.

The default storage layout is:

```text
framework/sessions/
├── current.py
├── current.metadata.json
└── <id>/
    ├── session.py
    └── metadata.json
```

The UI and native CLI share these default locations.
With a custom `MISSION_FILE`, named sessions use a neighboring `sessions/` directory.
If the selected workspace is already inside a directory named `sessions`, named sessions share that directory.
Legacy JSON and its old metadata remain intact during conversion.

Install the same library for a REPL:

```sh
python3 -m pip install -e framework/python  # from the repository root
python3
```

```python
from nanosat_mbse import Session

session = Session.open("/path/to/mission.py")
period = session.get("ORB001").value("orbit_period_s")
session.get("ORB001").set_value("altitude_km", 500)
session.save()
session = session.reload()
```

Reload the browser after a REPL save and reload the REPL session after a browser save.
Revision checks reject a stale save from either writer.
A conflict keeps the local draft available for reload or Save as.
This is shared model access with safe independent drafts, without automatic live collaboration.
See the [runnable REPL demonstration](../python/docs/repl.md).

**Python sessions and native calculation functions are trusted local code running with your user permissions.**
Opening a session constructs its model.
Analyses remain unexecuted until **Run Python** or an explicit native execution call.
Handwritten files without the canonical format marker open read-only for replacement and require Save as.
The browser cannot submit Python files, import paths, shell commands or interpreter arguments.

## Workbook and requirements

External, Mission, bus, subsystem, payload and ground tabs are described by the Python model.
Adding an EPS initializes its default components and reusable requirements.
Adding another Battery creates its applicable EPS requirements.
Defaults are idempotent, and deliberate deletions remain deleted after reopening.
Source relationships and affected-element assignments remain separate links to actual model objects.

Open a requirement with either pencil.
Edit its single statement, rationale, parameter rows and verification methods in the pane.
A `$$parameter_name$$` marker creates a provisional row while typing and a real Python `Parameter` on application.
Each requirement owns its typed parameters and units.
Expressions remain visible beside evaluated values.

```python
REQ002.mass_kg * 1.2
18 if mode == "Downlink" else 3
sum(i ** 2 for i in range(10))
```

Automatic source expressions use the bounded restricted Python interpreter.
Imports, arbitrary calls, assignments, object introspection and unbounded collections are unavailable there.
Numbers must remain finite, and integer values must be safe for browser transport.
Missing inputs stay pending and malformed drafts retain diagnostics.
Units are labels, so conversions are explicit in expressions.

Native imported callable bindings from a REPL or reusable subclass display read-only labels in the UI.
Their scoped identities are preserved through edits and saves.
Their calculated results use the same evaluation context as editable expressions.

Save and Cancel apply to the pane's drafts.
Cmd+Enter or Ctrl+Enter saves the active requirement or component editor.
Source and assignment pickers, stable IDs, trailing empty rows, plus buttons, delete gutters, sorting and tab navigation remain available.
Python handles naming, reference rewriting, ownership constraints and protected deletion.

## Power, mass and volume

Define spacecraft modes and sunlight/eclipse fractions in Mission.
Define component quantities, accounting, states and power values in each component pane.
Allocate states to spacecraft modes in the subsystem table.
Power limit requirements link spacecraft, subsystem and component allocations.

Connect the EPS **LoadEnergy** requirement to component modes and selected load domains.
Its weighted sunlight and eclipse averages feed the existing energy equations.
Disconnecting restores the previous manual bindings.
Software uses its execution host, and passive hardware, battery storage and solar generation start excluded from load demand.

Mass and volume requirements account for physical hardware independently from power accounting.
Parent sums reference child values and allocations.
Unchanged default sums extend with newly added children.
Custom expressions and cleared cells remain editable.
These are preliminary budgets, with energy closure, chronological peaks, mechanical fit and hardware qualification assessed separately.

## COTS facts

COTS classes inherit both their generic engineering component and `DatabaseBacked`.
For example, `CotsBattery` inherits `Battery` and the shared database loader.
Database rows populate the instances without changing their engineering inheritance.

The default provider reads the live `framework/cots/` tables.
Set `NANOSAT_MBSE_COTS_DIR` for another complete database directory.
New rows are read through content-aware caches, and no fixed catalog size is assumed.
Use **Refresh catalogue** to inspect current records.

Choose exact facts by internal element, value meaning, conditions, unit and source revision.
Named references such as `CMP001.mass` pin identity and revision without copying authoritative values into the session.
Changed or substituted facts remain pending until reviewed.
Renaming a reference updates dependent bindings in Python.
Typical values establish no guaranteed hardware limit, and operating limits remain distinct from absolute maxima.

## Verification and analyses

Every configured method must pass in every configured mode for the requirement checkbox to pass.
A requirement with no method stays unset.
Selecting a COTS component or script as a value source also requires its current evidence.
Successful script execution alone establishes no compliance claim.

The built-in analyses are importable `VerificationScript` subclasses in `nanosat_mbse.verifications`.
Their typed interfaces and calculations are defined in Python.
Use the script picker, bind inputs to literals or requirement references, add conditions and click **Run Python**.
Dependencies run first, and per-mode outputs, logs and diagnostics remain inspectable.

Execution evidence is transient and held outside session configuration.
Input, mode, implementation and selected-fact changes invalidate stale evidence.
Unrelated new COTS rows leave existing pinned evidence current.
Reloading or switching sessions requires fresh execution.
The primary download is **Export Python session** and retains executable bindings without cached success flags or outputs.

Trusted external analyses can still use registered `.py`/`.json` pairs through `VERIFICATION_SCRIPTS_DIR`.
See [analysis registration](scripts/README.md), [model scope](analyses/README.md) and [report coverage](analyses/REPORT-COVERAGE.md).

## Optional study sessions

The compatibility commands delegate to native Python factories and the shared repository.
They create independent named sessions without running analyses:

```sh
node tools/create-analysis-session.mjs demo --name "My test bench"
node tools/create-analysis-session.mjs mppt --name "My MPPT study"
node tools/create-analysis-session.mjs scenario --from current --name "My illumination study"
node tools/create-report-session.mjs --list
node tools/create-report-session.mjs energy --name "My energy assessment"
```

Use `--mission /path/to/mission.py` to choose the neighboring session directory.
A retained JSON source is also accepted.
The installed equivalents are `nanosat-mbse analysis ...` and `nanosat-mbse report ...`.

## Focused checks

```sh
npm test
```

This runs the retained requirement presentation checks.
The obsolete architecture tests are clearly archived under `test/legacy/` with `.txt` suffixes.
They are outside active Node test discovery.
Native examples and browser workflows exercise the current model and service.
The active test command makes no claim of full old-suite parity.
