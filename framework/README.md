# Nanosatellite framework

`framework.models` implements the small object model described in `prompt.md`.
Use it from Python scripts or a REPL.

```sh
python3 -m pip install -e framework
```

```python
from framework.models import Mission, CubeSatBus

mission = Mission()
bus = mission.add(CubeSatBus("BUS", units=1))
bus.EPS.Battery.mass = 0.2
print(bus.EPS.Battery.mass.value)
```

See [the model API](models/README.md) for properties, COTS, functions, modes and verification traces.
The [COTS input guide](cots/README.md) maps sourced ratings and explicit data gaps to the native EPS inputs.
The ordinary [example session](sessions/example_mission.py) demonstrates transitive verification.
The [EPS sizing session](sessions/example_eps_sizing.py) demonstrates circular/eccentric illumination, preliminary energy sizing and checks of the entered array, battery and load-rail configuration.
From the repository root, run them with `python3 -m framework.sessions.example_mission` or `python3 -m framework.sessions.example_eps_sizing`.
There is no CLI.

## Layout

```text
framework/
├── models/                  # Small public Python model API
├── gui/
│   ├── backend/             # GUI application and transport
│   │   └── legacy/          # Compatibility for the existing workbook and sessions
│   ├── public/              # Browser code
│   └── server/              # Node HTTP server
├── scripts/                 # Typed numerical calculations, including EPS sizing
├── cots/                    # Existing product tables used by the GUI
└── sessions/                # Ordinary session files
```

The public models have no GUI, database or workbook dependencies.
Mission, Orbit, Stakeholder, DomainElement, Subsystem and Component can own Requirements.
Bus and EPS defaults belong to the bus and EPS respectively.
Mission verification includes Requirements throughout the containment tree.
Units are annotations.
Python expressions and custom functions execute trusted code with user permissions.
Custom function inputs are explicitly bound to Properties.
Mission expressions import the shipped EPS sizing functions as `sizing` by default.
Calculations have no cache or execution protection.

The current GUI retains its older workbook schema through `gui/backend/legacy/`.
It has not been rewritten to edit the new Mission classes.
Its serializers, draft handling, restricted interpreter and old model adapters stay outside the public API.
Version 1 saved workbook imports are redirected in memory when opened by the GUI.
Original saved source files remain unchanged.
The compatibility package can be retired as the GUI migrates.

## GUI

Requires Node.js 22 or later and Python 3.8 or later.

```sh
npm start --prefix framework/gui
```

Open <http://127.0.0.1:3000>.
`MISSION_FILE`, `PORT` and `VERIFICATION_PYTHON` select the GUI workspace, port and interpreter.
The old GUI numerical analyses remain unavailable. New sizing functions are used by the public model API.
See [GUI](gui/README.md).

Validation uses live Python and HTTP workflows.
