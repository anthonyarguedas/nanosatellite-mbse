# Shared UI and REPL demonstration

The browser and an agent can open the same native Python session through `nanosat_mbse`.
Both use the same object classes, formulas, analysis implementations and verification rules.
`Session.open()` and `reload()` prepare the same generic defaults as a UI open.
They keep independent editable graphs and protect saves with file revisions.
Reload after the other writer saves.
A stale save reports a conflict and leaves the local graph available for recovery.

## Prepare independent demo copies

From the repository root, choose a new output directory:

```sh
PYTHONPATH=framework/python/src python3 -i framework/python/examples/repl_demo.py \
  --prepare /tmp/nanosat-repl-demo
```

This creates `sizing.py` and `analysis.py` with create-only publication.
The original demo JSON and live COTS tables remain untouched.
`session` opens the analysis file and `sizing` opens the physical-budget example.
`eps`, `battery` and `mppt` are native object references.
No analysis has run yet.

The package can also be installed with `python3 -m pip install -e framework/python`.
After installation, the `PYTHONPATH` prefix is unnecessary.
Use an existing file instead of preparing copies:

```sh
python3 -i framework/python/examples/repl_demo.py /path/to/session.py
```

## Suggested REPL sequence

```python
from nanosat_mbse import Battery, DatabaseBacked, Session

type(eps), type(battery), type(mppt)
isinstance(battery, Battery), isinstance(battery, DatabaseBacked)
battery.fact_value("mass")
sizing.get("ORB001").value("orbit_period_s")

session.verify()["MPT008"].state.value
session.run(mppt)
mppt.value("tracking_efficiency")
mppt.value("delivered_energy_J")
session.verify()["MPT008"].verified

session.get("MPT004").set_value("voltage_step_V", 0.1)
session.verify()["MPT008"].state.value
session.run(mppt)
mppt.value("tracking_efficiency")

session.get("MPT004").set_value("voltage_step_V", 0.05)
session.run(mppt)
session.save()
session = session.reload()
mppt = session.get("SCR001")
session.verify()["MPT008"].state.value
```

The numbers above are synthetic study inputs, not cached calculation outputs.
The results are calculated during the demonstration.
Changing an input makes old evidence pending.
Reloading keeps configuration and requires fresh execution.
Rebind local object references after `reload()` because it returns a fresh graph.

For a complete noninteractive rehearsal using actual calculations, add `--run`:

```sh
PYTHONPATH=framework/python/src python3 framework/python/examples/repl_demo.py \
  --prepare /tmp/nanosat-repl-rehearsal --run
```

The walkthrough changes a perturbation input, executes again, restores the original binding, saves and reopens.
It prints real outputs and retains no hardcoded result values.

## Open the same file in the browser

In a second terminal:

```sh
cd framework/requirements-ui
MISSION_FILE=/tmp/nanosat-repl-demo/analysis.py PORT=3002 npm start
```

Open <http://127.0.0.1:3002> and select the EPS tab.
Open MPT008 and run SCR001.
Compare the displayed values with the REPL's full-precision values.
Reload the browser after a REPL save.
After a browser save, call `session = session.reload()` and rebind `mppt`.
Simultaneous stale saves fail safely instead of overwriting the other writer.

## Recording recipe

Use the synthetic copies and a clean terminal with a readable font.
Record the actual interactive sequence with the operating system's screen recorder or a local terminal recorder.
Keep the browser beside the REPL to show the shared file and matching calculation results.
Pause on the native class names, database inheritance, pending evidence, explicit run and save/reload boundary.
The `--run` rehearsal verifies the sequence before recording.
These studies establish preliminary model results and no hardware qualification claim.
