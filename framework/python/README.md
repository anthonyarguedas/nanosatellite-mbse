# Python domain model

The library provides native sessions, element inheritance, requirements and database-backed COTS selections.
The Node HTTP bridge uses the native application service for storage, domain edits, calculations and execution.
The browser retains presentation and editor drafts and calls that service for domain operations.

## Run the review example

From the repository root:

```sh
PYTHONPATH=framework/python/src python3 framework/python/examples/requirement.py
```

The package has no runtime dependencies and supports Python 3.8 or later.
It can also be installed with `python3 -m pip install -e framework/python`.

## Requirement API

```python
from nanosat_mbse import Parameter, Requirement, VerificationMethod


def within_limit(values):
    return 0 <= values["mass_kg"] <= values["mass_limit_kg"]


requirement = Requirement(
    id="MAS001",
    text="The spacecraft mass shall not exceed $$mass_limit_kg$$.",
    parameters=(
        Parameter("mass_limit_kg", unit="kg"),
        Parameter("mass_kg", unit="kg"),
    ),
    rationale="Preliminary mass allocation.",
    verifications=(VerificationMethod("mass allocation", within_limit),),
)
requirement.set_value("mass_limit_kg", 1.0)
requirement.set_value("mass_kg", 0.706)
result = requirement.verify()
assert result.verified
```

- Each requirement owns its parameters and verification methods.
- `Parameter` declares its name, Python value type, unit and literal value or expression.
- Supported value types are `float`, `int`, `bool` and `str`.
- Parameters are immutable records updated through requirement methods.
- `set_value()`, `set_expression()` and `set_unit()` validate replacements before applying them.
- A literal value and an expression are mutually exclusive.
- New `$$name$$` markers declare unset float parameters in Python.
- Removing a marker retains the parameter and its configuration.
- Each requirement needs at least one declared parameter.
- Metadata includes stable key, visible ID, name, text, rationale, provenance and generic definition identifier.
- `owner`, `sources` and `affected` reference domain objects through their stable identity.
- `derive_from()` protects requirement source links from cycles.
- `assign_to()` records affected domain objects separately from source links.
- Assigning `sources`, `affected` or `verifications` replaces its table after validation.
- Subclasses supply reusable parameter definitions, calculations and conditions.

`examples/requirement.py` demonstrates a reusable `BatteryEnergyRequirement`.
The example contains both the reusable subclass and session-style population to keep this review self-contained.
Production domain subclasses live under `nanosat_mbse.domains`.

## Native session graph

```python
from nanosat_mbse import Battery, CotsBattery, CubeSat, GroundStation, Orbit, Payload, Session

session = Session()
for domain in (Orbit(), CubeSat(), Payload(), GroundStation()):
    session.add(domain)
eps = session.get("EPS")
backup = eps.add_component(Battery(name="Backup battery"))
selected = eps.add_component(CotsBattery(
    product="gomspace_nanopower_bpx_100wh_8s1p",
    database=session.database,
    usage=session.get("BAT"),
))
```

Run `examples/session_graph.py` with the same `PYTHONPATH` as the requirement example.
A new `Session()` starts with empty user-visible tables.
Adding the domain objects calls their ordinary initialization methods to create children, reusable requirements and budgets.
Adding another Battery creates its applicable component requirements in its EPS.
Each populated requirement owns independent parameter records.

The supplied **Generic EPS Example** is an ordinary saved session in `framework/missions/sessions/`.
Open it through the Session picker and use **Save as** to make an independent copy.
It has no special initialization or regeneration behavior.
Deleting it leaves new sessions blank.

- `Session.add()` registers an object and runs its initialization and addition hooks.
- `Session.initialize()` applies defaults once.
- `Session.get()` accepts an object, stable key or visible ID.
- `Session.rename()` rewrites qualified expression references while retaining object links.
- Renaming an attached object's `id` uses the same session method.
- `Session.remove()` protects child rows, relationship references and expression references.
- `Session.retype()` changes an empty catalog element while retaining its identity.
- `Session.substitute_product()` retains named COTS references while adopting the new product's generic inheritance.
- `Session.configure_parameter()` applies a typed owned binding through domain validation.
- `Session.configure_facts()` protects fact deletion and rewrites named-reference changes.
- Seed history records defaults independently from current rows, preserving deliberate deletions.
- `Session.from_projection()` restores actual objects in two passes with creation hooks disabled.
- `Session.to_projection()` creates a detached browser view from the graph.
- The input projection is never retained as session backing state.

The projection adapter includes optional `modelState` metadata for native lifecycle history, subject links and owned parameter types.
Legacy files without this metadata retain their original projection shape.
Incomplete saved text becomes an explicit `DraftRequirement` or `DraftStatement`.
Invalid saved expressions become `DraftExpression` objects retaining their source and diagnostic.
Normal constructors and edit methods continue validating new input.
No placeholder parameters are invented to make incomplete requirements valid.

Non-requirement needs, objectives, concerns and constraints use `Statement`.
`Requirement` specializes it with the original requirement parameter rule.

## COTS and database providers

`CotsBattery` inherits both `Battery` and `DatabaseBacked`.
Equivalent classes represent the registered product types.
The default `TabularDatabase` adapter reads the existing `framework/cots/` tables.
Supply `TabularDatabase(directory)` or set `NANOSAT_MBSE_COTS_DIR` for an installed package.
Another database can implement the `ProductDatabase` protocol.

Select an exact `Fact` from `component.product_record.facts` with `component.select_fact(name, fact)`.
Review its value meaning, units, conditions and source when choosing a record.
`component.fact_value(name)` reads the current database record through the pinned reference.
A changed or unavailable record remains pending.
Selections retain identities and revisions without copied authoritative values.
Product substitution retains selected reference names and leaves incompatible records pending.

Legacy generic component usages and COTS selection rows remain distinct native objects.
A COTS selection's `usage` points to its generic physical usage when it is unambiguous.
`Session.physical_components` excludes selections, avoiding duplicate physical accounting.
A newly added COTS component inherits component initialization and links its generated requirements.
`component.verify()` aggregates its linked requirements through the same native session context.
`Session.evaluate()` includes native component checkbox results in its `components` projection.

`Mode`, `ComponentState`, `LoadProfile` and `LoadConnection` hold typed configuration and actual object links.
`ScriptConfiguration` and `ScriptPort` preserve registered analysis interfaces and input bindings.
They contain no execution output.

## Common native evaluation

```python
session = Session()
session.add(Orbit())
session.get("ORB001").set_value("altitude_km", 500)
period = session.value("ORB001", "orbit_period_s")
assert period == session.get("ORB001").value("orbit_period_s")

assessment = session.get("ORB001").verify()
assert assessment.verified
assert session.verify()["ORB001"].verified
browser_results = session.evaluate()
```

Run `examples/evaluation.py` for a standalone calculation and component-mode example.

- `Session.value(object_or_id, parameter)` resolves an owned parameter.
- An attached `Requirement.value()` uses that same session context.
- If all configured modes produce the same value, `value()` returns a scalar.
- Differing successful mode values return a read-only mapping keyed by mode name.
- Unset dependencies raise `PendingValue` and invalid calculations raise errors.
- Supply `mode=mode_object`, a mode key or a mode name to select one mode.
- Explicit `mode=None` evaluates without a selected mode.
- Omit `mode` to assess every configured mode.
- `Session.verify()` returns a `VerificationReport` addressable by object, key or ID.
- `Session.verify(object_or_id)` and attached `Requirement.verify()` return a `VerificationResult`.
- Aggregate assessments retain per-mode results in `result.modes`.
- Every configured method must pass in every configured mode for `verified` to be true.
- A requirement with no methods remains unset.
- `Session.evaluate()` returns the browser-shaped `results`, `scripts`, `engine` and `cotsSignature` projection.
- Browser parameter cells include states, values, errors and mode-conditional branch metadata.

The restricted engine reads actual objects and their owned `Parameter` records.
It never reconstructs the old worker `Workspace` model or executes `eval` or `exec`.
Names such as `ORB001.altitude_km` resolve through the native registry.
COTS references read a single current database snapshot per evaluation request.
Native calculation functions receive a lazy parameter mapping and can inspect `values.mode`.
Native and expression-backed dependencies share cycle detection and the request cache.
Nested attached-object calls reuse the active context.
Unrelated unset parameters leave configured checks unaffected.

Expressions retain the existing bounded math, statistics, conditionals and comprehension syntax.
Limits include 5,000 source characters, 2,048 AST nodes, 64 syntax/dependency levels, 1,024 collection items and a shared operation budget across modes.
Integer results remain safe for browser transport.
Native callables are trusted Python code and are outside the restricted source interpreter.

A standalone requirement still supports native functions or an explicitly supplied `ExpressionEvaluator(source, requirement, values)`.
Attaching it to a session provides the built-in restricted engine automatically.
Calculated values and results remain transient.
`render_text()` substitutes supplied results or literal inputs with unit labels without running calculations.
Units remain labels, with conversions explicit in calculations.

## Native budgets and lifecycle

`Session.add_mode(Mode(...))` or `add_mode(name, sunlight=..., eclipse=...)` creates a mode and its power requirements.
Use `configure_mode()`, `rename_mode()` and `remove_mode()` to retain expression and state links.
Removing a mode with expression references is protected.

Use `configure_load(component, quantity=..., accounting=..., states=..., assignments=...)` for component demand.
States are `ComponentState` objects, and assignments reference actual `Mode` and state objects.
Software demand belongs to its execution host.
Battery storage, generation and passive components start excluded from load demand.
Mass and volume accounting still includes physical hardware.

`connect_power(eps, roots=...)` binds its LoadEnergy requirement to weighted component-mode demand.
Zero-share modes need no draw for that illumination period.
The connected inputs are protected until `disconnect_power(eps)` restores their previous `Parameter` bindings.

New spacecraft elements and components receive independent resource requirements through native lifecycle methods.
Power requirements are generated when modes exist.
Unchanged default allocation sums extend with new children.
Custom expressions and deliberately cleared cells retain their configuration.
Budget scopes and parent/source/affected relationships reference domain objects.
`validate_budgets()` checks modes, states, scope ownership and managed connections.

Import remains hook-free and preserves the original projection.
`Session.reconcile_defaults(generic=True, budgets=True)` explicitly introduces new catalog studies and legacy budget initialization.
Seed history preserves deliberate requirement deletions through reconciliation and restoration.
Native edits enable `modelState` metadata so parameter ownership, literal bindings and deletion history survive transport.

## Interoperable verification scripts

`VerificationScript` inherits the native analysis configuration and element interfaces.
Concrete subclasses declare a `ScriptDefinition` in Python and implement `calculate(inputs, requirements=..., mode=...)`.
Their ports are typed `ScriptPort` records.
The library contains importable implementations for all 14 existing analyses, including `MPPT`, `Illumination`, `NormalInterval`, `EnergySegment`, `ConverterStep`, `Guidance`, `PowerPath`, `Protection`, `BatteryStep`, `Thermal`, `Sizing`, `Geometry`, `Fit` and `RAM`.
The numerical functions and classes live together under `nanosat_mbse.verifications`.
Importing them never reads stdin or executes an analysis.

```python
from nanosat_mbse import NormalInterval, Session

session = Session()
analysis = session.add(NormalInterval("SCR001"))
analysis.set_value("mean", 4)
analysis.set_value("standard_deviation", 1)
analysis.set_value("confidence", 0.95)
evidence = session.run(analysis)
upper = analysis.value("upper")
assert upper == session.value("SCR001", "upper")
```

Run `examples/verification.py` for native configuration, explicit execution, source-backed requirement checks and evidence invalidation.
Its optional `--workspace framework/requirements-ui/demo/analysis-workspace.json` argument runs the illumination and MPPT bench through the native API without changing the input file.

- `Session.run(script)` accepts an object, ID or key and executes the selected script and needed dependencies.
- `Session.run()` executes all configured scripts.
- `VerificationScript.run()` delegates to its attached session.
- Omitting `mode` executes every configured mode, with one invocation when no modes exist.
- Dependencies can pass through other scripts or requirement parameters.
- Missing inputs remain pending and cyclic dependencies produce errors.
- Inputs and outputs use the declared types, with finite numeric values and safe integers.
- Null outputs remain unresolved when used by a requirement.
- Execution alone establishes no compliance claim.
- New runs return immutable `ExecutionEvidence` and `ExecutionResult` records.
- Evidence retains typed outputs, resolved inputs, timestamps, durations, logs and diagnostics.
- The session retains its latest evidence in memory for normal `evaluate()`, `verify()` and attached-object calls.
- `clear_evidence()` discards this transient cache.
- `to_projection()` excludes all execution evidence and output values.

### Explicit execution and limits

The default `IsolatedRunner` imports the same registered analysis class in a separate Python process.
It uses the current interpreter unless a trusted caller configures another executable.
The private bootstrap supports both installed packages and the source checkout under Python's `-I` isolation flag.
The browser supplies only registered identities and bindings to the native service.
It must never supply Python class paths, source files, interpreter arguments or shell commands.

Each invocation uses its definition's timeout of 10 through 10,000 ms.
A `Session.run()` call has a default total budget of 30 seconds.
Combined stdout and stderr are limited to 1 MiB per invocation.
`CancellationToken` or a compatible event can cancel active subprocesses.
On Unix, cleanup terminates the process group, including descendants.
Missing inputs prevent invocation.
Malformed JSON, unexpected outputs, invalid types, nonzero exits and exceeded limits produce error evidence.

`InlineRunner` is an explicit option for trusted interactive classes and debugging.
It executes the same `calculate()` method and captures bounded logs.
A running native function cannot be safely interrupted in process.
Inline time and cancellation checks therefore apply before and after the call.
Source edits require reloading a class before inline execution.
Direct `calculate()` calls also have no execution limits.
The HTTP service should always use the default isolated runner.

All analysis and session code is trusted local Python running with user permissions.
This execution boundary is not a sandbox.

### Definitions, revisions and legacy imports

`default_registry().describe()` returns browser-compatible metadata derived from Python definitions.
`ScriptRegistry` also accepts explicitly configured trusted directories through `RegisteredScript`, a `VerificationScript` subclass for the existing JSON stdin/stdout protocol.
`VERIFICATION_SCRIPTS_DIR` extends the default registry and explicitly overrides matching builtin IDs.
Directory containment and file size checks apply before source can be copied for execution.
The library never imports that external source when opening a session or listing definitions.
Installed packages used by external scripts remain available, and neighboring relative imports are unsupported.

Each builtin revision covers its source module, inherited calculation source, declared interface and execution protocol revision.
Declare additional importable `revision_dependencies` on a custom analysis class when its algorithm uses helpers in other modules.
Registered external scripts retain the original hash of their exact source and JSON metadata.
`current_revision` always identifies the current implementation.
`update_definition()` explicitly accepts that revision and its interface while retaining matching input bindings.

The transport importer restores actual analysis subclasses and preserves original script pins and interface data.
The migration's `_legacy.py` contains reviewed aliases for exact pre-refactor source/metadata hashes.
Each alias authorizes only its fixed migrated native source revision and exact interface.
These aliases are never learned from files or saved sessions at runtime.
Arbitrary old pins, modified source and changed interfaces stay pending until reviewed.
This permits faithful imports of the existing demos without silently accepting new source.
The Python serializer emits the concrete importable subclass, its original pin and declared bindings directly.
The duplicate UI script implementations have been retired. Native modules are the sole built-in calculation source.

### Evidence freshness and service boundary

`EvaluationContext` accepts current evidence and an optional `source_ready(source, context)` callback.
COTS-backed methods require every selected fact to resolve to its pinned current record.
Script-backed methods require successful evidence for the same pin, implementation revision, calculation signature and selected mode, including constant conditions.
Changing calculation inputs, modes, bindings, implementations or selected fact revisions invalidates evidence.
Prose and predicate edits leave unchanged calculation evidence reusable.
Unrelated COTS database additions leave selected facts unchanged.
The runner checks configuration and source identities before and after execution.

`ExecutionEvidence.result_for(script, mode)` returns a run record.
Supply a mode object or key when the session has configured modes, or use `script.value()` to aggregate output values.
`ExecutionEvidence.projection()` supplies `signature`, `cotsSignature` and `runs` keyed by `<script-key>:<mode-key>`.
Each run includes its pinned `revision`, actual `implementationRevision`, state, values and diagnostics.
`Session.calculation_signature()` and `evaluation_context().cots_signature` expose current identities.
`Session.script_inputs()` uses the same native evaluator to resolve dependencies and an evaluated requirement snapshot.
The HTTP service retains returned evidence behind an opaque token and passes that evidence to this common API.
Browser-supplied output values are rejected as authoritative evidence.

## Native Python session files

```python
session.save("mission/session.py")
reopened = Session.open("mission/session.py")
assert reopened.execution_evidence is None
reopened.run("SCR001")
reopened.save()
```

Files contain imports, explicit populated class instances, relationships and an execution entry point.
Loading reconstructs the graph with creation hooks disabled and leaves analyses unexecuted.
The shared `SessionRepository` enforces path-bound revisions, locks, atomic writes and create-only publication.
A stale browser or REPL writer receives `SessionConflict` while its local edits remain available.
`session.storage` exposes the last successful path and revision.
`session.reload()` returns a fresh graph, so use `session = session.reload()` to refresh REPL references.

Convert legacy JSON explicitly to a new file:

```sh
PYTHONPATH=framework/python/src python3 -m nanosat_mbse.persistence \
  framework/requirements-ui/demo/analysis-workspace.json \
  --output /tmp/analysis/session.py
```

Original JSON and metadata remain unchanged.
Native functions are stored through importable identities, with clear errors for lambdas, closures and REPL-local functions.
A trusted service can retain native callable bindings in browser projections through a process-local `CallableRegistry` and read-only opaque tokens.
The browser supplies no import paths.

Run `examples/persistence.py` for save/reopen, explicit execution and conflicting-writer examples.
Its optional `--workspace` argument converts a copy into temporary Python storage.
See [Native Python sessions](docs/sessions.md) for the source format, migration, metadata, custom-class and UI integration contracts.
See [Native application service](docs/http-service.md) for HTTP contracts, native draft handles, workbook metadata and opaque execution evidence.
The active browser uses those operations and preserves canonical native responses through local drafts.

## Optional study factories and CLI

`nanosat_mbse.benches` provides `create_mppt_session()`, `add_scenario_analysis()`, `create_analysis_demo()`, `create_report_session()` and `report_profiles()`.
These functions construct actual classes, owned parameters and object relationships without executing analyses.
Blank studies leave independent quantities and limits unset.
The combined demo supplies synthetic inputs and acceptance limits.
Report factories select current COTS facts through the configured database provider.

```sh
nanosat-mbse analysis demo --mission /path/to/mission.py --name "My bench"
nanosat-mbse report --list
nanosat-mbse report energy --mission /path/to/mission.py --name "My energy assessment"
```

From a source checkout, use `python3 -I framework/python/cli.py` before the same arguments.
The old Node tool commands are thin launchers for this CLI.
Named-session creation shares the application's repository, locks and unique-name rules.
`--from` and `--orbit` select an existing session and orbit for independent scenario copies.
Original source files remain intact, and creating a study runs no analysis.

See the [shared REPL demonstration](docs/repl.md) for opening the same native file as the UI, changing inputs, running MPPT, and saving/reloading safely.
