# Verification implementations and external registration

Built-in analyses live in `framework/python/src/nanosat_mbse/verifications/`.
Each implementation inherits `VerificationScript`, declares typed Python ports and provides its calculation in the same module.
The UI and REPL execute these same classes.
The former duplicate `.py` and `.json` files have been retired from this directory.
Reviewed legacy revision aliases remain in `nanosat_mbse.verifications._legacy` so unchanged saved configurations retain their migration identity.

Examples include `MPPT`, `Illumination`, `NormalInterval`, `PowerPath`, `EnergySegment`, `BatteryStep`, `Thermal`, `Sizing`, `Geometry`, `Fit` and `RAM`.
Their public registry IDs, such as `mppt_po` and `scenario_illumination`, remain stable.
See the [native verification API](../../python/README.md#interoperable-verification-scripts) and [analysis scope](../analyses/README.md).

## Native use

```python
from nanosat_mbse import NormalInterval, Session

session = Session()
analysis = session.add(NormalInterval("SCR001"))
analysis.set_value("mean", 4)
analysis.set_value("standard_deviation", 1)
analysis.set_value("confidence", 0.95)
evidence = analysis.run()
upper = analysis.value("upper")
```

Construction and imports execute no analysis.
`run()` resolves typed inputs and dependencies, runs the same importable calculation through the isolated runner and returns transient evidence.
Session files contain instances and bindings, with explicit verification calls separated from construction.

## Trusted external scripts

A configured external directory can register `<id>.py` and `<id>.json` pairs:

```sh
VERIFICATION_SCRIPTS_DIR=/path/to/reviewed/scripts \
VERIFICATION_PYTHON=/path/to/venv/bin/python3 npm start
```

`RegisteredScript` adapts them through the same `VerificationScript` interface.
The application-configured directory is trusted.
The browser can choose registered identities and bindings and cannot supply source files or paths.
External definitions can override built-in IDs only through that trusted configuration.

```json
{
  "id": "square_root_margin",
  "name": "Square root margin",
  "description": "Example external analysis interface.",
  "inputs": [{"name": "input_value", "type": "float"}],
  "outputs": [{"name": "margin", "type": "float"}],
  "timeoutMs": 3000
}
```

The script reads one JSON object from stdin with `inputs`, a requirement-value snapshot in `requirements`, and the selected `mode` or `null`.
Declare dependencies through input bindings.
Write exactly the declared output names to stdout and diagnostics to stderr:

```python
import json
import math
import sys

request = json.load(sys.stdin)
json.dump({"margin": math.sqrt(request["inputs"]["input_value"])}, sys.stdout, allow_nan=False)
```

Inputs and outputs support `float`, `integer` and `boolean`, with optional unit labels.
Each definition permits up to 32 input and 32 output ports.
Numeric values must be finite and integers safe for browser transport.
A `null` output remains unresolved.
The interface and reviewed source revision are pinned on each instance.
Use **Update definition** after reviewing a changed interface or implementation.

## Execution boundary

**Run only trusted code. Python executes with your user permissions and is not sandboxed.**
The default isolated runner uses the selected interpreter, per-script timeouts, a total run budget, cancellation and bounded output.
Each script timeout ranges from 10 ms through 10 seconds.
A run defaults to a 30-second total budget and 1 MiB combined output per invocation.
Unix cleanup terminates the child process group.
External source is copied to a temporary directory, so neighboring relative imports are unavailable.
Installed packages in the selected interpreter remain available.

Opening, editing, saving and exporting a session never execute registered analysis source.
Execution evidence stays separate from configuration and requires current inputs, modes, implementation and selected COTS pins.
A successful process supplies evidence only, with requirement predicates establishing the declared pass/fail result.
