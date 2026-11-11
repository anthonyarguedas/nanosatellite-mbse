# Registered Python analyses

Use Python 3.8 or later. The automatic calculation worker also uses this interpreter. Registered script source runs only when **Run Python** is clicked. Set `VERIFICATION_PYTHON` to select an interpreter, including one in a virtual environment. Set `VERIFICATION_SCRIPTS_DIR` to choose a trusted directory, relative to where the server starts:

```sh
VERIFICATION_PYTHON=/path/to/venv/bin/python3 \
VERIFICATION_SCRIPTS_DIR=/path/to/reviewed/scripts npm start
```

The default directory is this one. Each registered analysis uses the Python standard library:

- `normal_interval` calculates a two-sided normal distribution interval with a known standard deviation.
- `scenario_illumination` estimates circular orbit illumination, conical eclipse and direct irradiance on one panel section.
- `mppt_po` simulates an ideal perturb and observe tracker over one environmental step.
- `eps_energy_segment` propagates chronological energy and independent charge balances, reserves, service shortages and surplus.
- `eps_converter_step` evaluates a declared first-order converter command/startup response.
- `eps_guidance` proposes model/activity eligibility and reports missing prerequisites from an explicit input inventory.
- `eps_power_path` assesses declared conversion, path losses and steady/pulse supply limits.
- `eps_protection` executes declared protection and recovery scenarios.
- `eps_battery_step` evaluates a supplied battery equivalent-circuit step.
- `eps_thermal` evaluates one-node thermal response and state temperature limits.
- `eps_sizing` proposes bounded integer cell-assembly arrangements and resource measures.
- `eps_geometry` checks declared installation and keep-out envelopes.
- `eps_fit` estimates parameters of declared models from checked supplied samples.
- `eps_ram` executes a bounded authored fault tree with quantitative failure measures.

New instances added from the script picker start with unset inputs. The combined test bench supplies synthetic values for both engineering analyses. See [analyses/README.md](../analyses/README.md) for engineering assumptions, required inputs, proposed requirements, result bindings and the optional named-session creator. These scripts provide preliminary model evidence within their declared scope.

The [report coverage audit](../analyses/REPORT-COVERAGE.md) documents the generic study requirements populated in every EPS session and the optional analysis benches. The generic requirement list provides the activity guidance. These scripts are tools for obtaining its study values and evidence through the existing pane. They use the same protocol and explicit execution boundary below. All independent model choices, product inputs and acceptance limits start unset.

## Interface

A definition consists of `<id>.py` and `<id>.json` in the configured directory. IDs use lowercase letters, digits and underscores, starting with a letter. The JSON declares `id`, `name`, `description`, `inputs`, `outputs` and an optional `timeoutMs`:

```json
{
  "id": "square_root_margin",
  "name": "Square root margin",
  "description": "Example external analysis interface.",
  "inputs": [{ "name": "input_value", "type": "float" }],
  "outputs": [{ "name": "margin", "type": "float" }],
  "timeoutMs": 3000
}
```

Each input and output declares `name`, `type` and optional display `unit`. Types are `float`, `integer` and `boolean`. Names are unique across the inputs and outputs. They follow the requirement parameter identifier rules. Each definition supports up to 32 inputs and 1 to 32 outputs. Each workspace supports up to 64 script instances.

## JSON protocol

The script reads one JSON object from stdin:

```json
{
  "inputs": { "input_value": 4 },
  "requirements": { "REQ001": { "mass": 4, "unset_input": null } },
  "mode": { "key": "nominal", "name": "Nominal" }
}
```

`inputs` contains evaluated bindings with validated types. `requirements` is a snapshot of evaluated requirement parameters for that mode. Unresolved or invalid cells appear as `null` in that snapshot. Declare dependencies through input bindings to ensure their values are resolved before execution. Bindings can reference other script outputs. Dependency cycles give an error. `mode` is `null` when the workspace has no spacecraft modes. Scripts receive evaluated JSON data directly.

The script writes exactly one JSON object to stdout, with exactly its declared output names:

```python
import json
import math
import sys

request = json.load(sys.stdin)
value = request["inputs"]["input_value"]
json.dump({"margin": math.sqrt(value)}, sys.stdout, allow_nan=False)
```

Write diagnostics to stderr. Outputs must match their declared types. Numeric outputs must be finite. Integer outputs must be safe JavaScript integers. A `null` output stays pending. Invalid JSON, unexpected output names, invalid values, a nonzero exit or a timeout gives an execution error. Missing inputs prevent execution.

Each instance pins a SHA-256 revision of its interface and Python source. If either file changes, reopen **Python scripts** and use **Update definition** before rerunning. Matching input expressions are retained. New inputs start unset. Review changed outputs and their references. Include the registered script files when sharing a saved mission.

## Execution boundary

**Run only trusted local scripts. Python runs with your user permissions. This is not a sandbox.** Registered scripts can access files and the network through normal Python APIs.

Execution requires an explicit `POST /api/scripts/run`. Opening, editing, saving and exporting never execute registered script source. Automatic Python expressions run in the separate restricted calculation worker. The browser cannot submit Python source, shell commands, paths or interpreter arguments. Only registered files inside the configured directory can run. Symlink escapes are rejected.

The server copies the verified source into a temporary working directory. It starts Python with `-I -u`, without a shell or inherited Python path configuration. Installed packages from the selected interpreter remain available. Scripts should receive data through the JSON protocol and use installed packages for reusable code. Relative imports from neighboring script files are unsupported. The working directory is deleted after execution.

The default invocation timeout is 3 seconds. `timeoutMs` can range from 10 ms to 10 seconds. Each request has a 30-second execution budget. Combined stdout and stderr are limited to 1 MiB. The server permits two simultaneous run requests. Cancellation, timeout and excessive output terminate the process group on Unix. These limits reduce accidental resource use and provide no security boundary for hostile code.

Execution evidence stays in the current browser session and is associated with the exact calculation context and pinned revision. Reloading or switching sessions clears it. JSON downloads retain typed interfaces, input expressions and pinned revisions, without cached outputs or execution flags.
