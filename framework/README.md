# Nanosatellite framework

The Python library is available as `framework.models`.
The local browser application lives in `framework/gui/`.
The current model behavior is retained while the object model is redesigned.

## Layout

```text
framework/
├── models/              # Model classes, definitions, product adapters and evaluation
│   ├── eps/             # EPS classes
│   └── persistence/     # Python session loading, saving and JSON conversion
├── gui/
│   ├── backend/         # Python application service and browser edit validation
│   ├── public/          # Browser code
│   └── server/          # Node HTTP server and Python transport
├── scripts/             # Reserved for the future analysis implementations
├── cots/                # Shared product facts and source records
└── sessions/            # Current and named Python sessions
```

The former `core`, `domains` and `catalogs` modules share the `models` package.
There is no CLI or study factory package.
Example sessions will provide study configurations.
The deleted numerical analyses are unavailable.
Saved script interfaces and bindings remain loadable as unresolved definitions.
The default script registry is empty.

## Use the Python library

Run Python from the repository root, or install the package:

```sh
python3 -m pip install -e framework
```

```python
from framework.models import Orbit, Session

session = Session()
session.add(Orbit())
session.get("ORB001").set_value("altitude_km", 500)
period_s = session.value("ORB001", "orbit_period_s")
session.save("/tmp/mission.py")
reopened = Session.open("/tmp/mission.py")
```

Session files contain trusted Python construction code.
Loading a session leaves its analysis scripts unexecuted.
Saving preserves expressions and object relationships.
Calculated results remain disposable.
The library imports no GUI modules.

`TabularDatabase` reads the source checkout's `framework/cots/` tables or the installed package data.
Supply `TabularDatabase(directory)` or set `NANOSAT_MBSE_COTS_DIR` for another database.

Convert a retained JSON workspace through the library:

```python
from framework.models import convert_json

result = convert_json("workspace.json", "/tmp/converted-session.py")
```

The original JSON remains unchanged.

## Run the GUI

Requires Node.js 22 or later and Python 3.8 or later.
No npm dependencies or browser build steps are needed.

```sh
npm start --prefix framework/gui
```

Open <http://127.0.0.1:3000>.
The GUI uses `framework/sessions/current.py` by default.
Set `MISSION_FILE` to use another workspace, `PORT` to select another port and `VERIFICATION_PYTHON` to select an interpreter.
See [GUI](gui/README.md) and [backend](gui/backend/README.md).

Validation uses live library and GUI workflows.
