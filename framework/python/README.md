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

The supplied **Generic EPS Example** is an ordinary saved session in `framework/sessions/`.
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

## Typed component properties and assignment checks

`Battery` and `SolarArray` declare typed properties in canonical catalogue units.
Examples include `Battery.rated_energy` in Wh and `SolarArray.maximum_power` in W.
Several other EPS types declare their common electrical properties too.
`component.property_definitions()` returns the inherited contract.
Additional catalogue facts remain available as ordinary named references.

Generic components own literal property values:

```python
battery = Battery(property_values={"rated_energy": 10}, quantity=2)
assert battery.rated_energy == 10
battery.rated_energy = 12
```

COTS components resolve these same properties through selected fact pins:

```python
matches = [fact for fact in selected.product_record.facts
           if fact.name == "rated_energy" and fact.element == "self"
           and fact.value_kind == "nominal" and not fact.condition["id"]]
assert len(matches) == 1
selected.select_property("rated_energy", matches[0])
energy_Wh = selected.rated_energy
```

`select_property()` validates the source name, internal element, scalar type and unit.
It retains the fact identity and revision without copying the database value.
Missing selections and changed records remain pending.
COTS properties accept no literal overrides.
Use explicit fact selection to choose the applicable conditions and value meaning.
The COTS pane lists typed properties and suggests their canonical reference names.

### Assignment ownership

`component.requirement_links` is the authoritative verification assignment relation.
Both generic components and COTS selections support it.
`component.assign_to(requirement)` adds a link.
`requirement.assign_component(component)` edits that same relation.
`requirement.unassign_component(component)` removes the link.
`requirement.assigned_components(Battery)` reads the inverse, filtered with `isinstance`.
Pass `cots_only=True` to select database-backed instances only.
Duplicate links count once.

`requirement.affected` remains the separate engineering scope relationship.
It creates no verification assignment.
A selection's `usage` also creates no assignment.

### Reusable verification conditions

These conditions run in the existing requirement verification editor and native evaluator:

```python
all_assigned("Battery", "nominal_voltage", "==", target_voltage, cots_only=True)
sum_assigned("SolarArray", "maximum_power", ">=", minimum_power_W, cots_only=True)
count_assigned("Battery", cots_only=True) <= max_batteries
```

For `all_assigned` and `sum_assigned`, the last positional argument names a parameter owned by the requirement.
The property and target must have compatible scalar types and units.
Supported comparisons are `==`, `!=`, `<`, `<=`, `>` and `>=`.
Strings and Booleans support per-component equality and inequality only.
Numeric equality defaults to exact comparison.
Set `abs_tol` in the target unit or dimensionless `rel_tol` for an explicit tolerance.
Inequality comparisons use their exact boundaries.

Both property checks convert into the target unit before comparison.
Conversions include Wh/J, Ah/C, W/mW, V/mV, A/mA, s/h, kg/g, m/mm, m2/cm2 and K/degC.
Other units must match exactly.
Sums reject offset conversions such as K to degC.
Ordinary arithmetic expressions retain their existing explicit unit conversion policy.

`all_assigned` checks each assigned instance once and ignores quantity.
`sum_assigned` adds each property multiplied by `component.quantity`.
Quantity is a positive integer that defaults to one.
This quantity describes the units represented by the assignment selection.
It is independent of the physical load budget's quantity.
The COTS pane edits this quantity alongside fact selections.

Empty property selections remain pending.
Every matching property's evidence is resolved before reduction.
An unset property cannot disappear behind a failed comparison.
Unavailable product types remain pending because the filter cannot classify them.

`count_assigned` counts distinct assigned objects without reading property facts.
Its default includes generic and COTS instances.
`cots_only=True` restricts it to COTS instances.
`by_quantity=True` counts represented units instead of selection rows.
An empty assignment set counts as zero, so an upper bound can pass with no assignments.

For example, this requirement limits assigned COTS battery selections to four:

```python
requirement = Requirement(
    "CNT001",
    "No more than $$max_batteries$$ COTS batteries shall be assigned to this requirement.",
    parameters=(Parameter("max_batteries", int, "1", value=4),),
    verifications=(VerificationMethod(
        "Assigned COTS battery count",
        'count_assigned("Battery", cots_only=True) <= max_batteries',
    ),),
)
```

Attach the requirement and components to the same session before checking assignments.
Trusted native conditions can call `values.all_assigned(Battery, "rated_energy", ">=", "minimum_energy_J")`, `values.sum_assigned(...)` and `values.count_assigned(Battery, cots_only=True)`.
Equivalent functions are exported from `nanosat_mbse` and take `values` as their first argument.
Property values, assignments, quantities and source mappings participate in evidence freshness.
Native source and browser projections preserve the same configuration.

### Combined COTS types

Combined products use ordinary multiple inheritance.
A class inheriting both `CotsBattery` and `CotsSolarArray` participates in both generic filters.
Each instance appears once in each check.
Requirements need no list of combination types.
The Battery + SolarArray combination currently exists only as a regression fixture in `tests/test_component_properties.py`.

Production combinations are added only for encountered catalogue products.
`CotsIntegratedBatteryEPS` represents the existing ICEPS2 Type A and IMEPS2 battery assemblies.
It inherits `CotsIntegratedEPS` and `CotsBattery`.
Their internal `battery.battery_capacity` and `battery.battery_energy` facts map to the canonical battery properties through `PropertySource` declarations.
Absent ratings remain pending.
Pumpkin EPSM1 retains its standalone integrated EPS type because its battery connections do not establish an included battery.
MPPT inputs establish no solar array inheritance.

The `product_type(model, products=(...))` decorator registers an exact product combination.
Omit `products` to register a whole catalogue model family.
Registration sets the combined class's product identity contract and lets factory creation, product substitution and projection restoration recover its actual inheritance.
Use `property_sources` overrides when an encountered combination stores a property under another fact name or internal element.
Existing Python sessions retain their explicit class declarations.
Call `session.substitute_product(component, component.product)` to accept a newly registered exact combination for an existing family instance.
This retains identities, assignments, quantities and fact pins without rerunning initialization.

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

Use `configure_load(component, quantity=..., accounting=..., states=..., allocations=...)` for component demand.
Legacy `assignments` and `duties` remain supported without changing saved single-state sessions.
States are `ComponentState` objects, and assignments reference actual `Mode` and state objects.
`ComponentState` stores only its name, per-unit power and stable key.
The former value meaning, source and conditions annotations have been removed.
Old Python constructors and projections can still be read, with those annotations discarded.
A state's `watts` accepts a nonnegative number or a restricted Python expression in W per installed unit.
Expressions can reference qualified requirement parameters, selected COTS facts, script outputs and `mode`.
They use the common evaluation context, dependency guards, evidence gating and reference renaming.
Unset upstream inputs remain pending. Negative or nonnumeric results are errors.

`duties` maps modes, mode keys or mode names to independent component duty percentages from 0 to 100.
Omitted entries mean 100 percent, preserving existing sessions.
Each table supplied to `configure_load()` replaces that table.
The browser edits state names, powers, quantities and allocations directly in Component State Allocation.
Adding and deleting states needs no separate component panel.
For an existing component and a configured Downlink mode:

```python
from nanosat_mbse import ComponentState

state = ComponentState("Transmit", "RAD001.current_A * RAD001.voltage_V")
session.configure_load(
    component,
    quantity=1,
    states=(state,),
    assignments={"Downlink": state},
    duties={"Downlink": 10},
)
```

For multiple states within one mode, use actual state references and duty percentages:

```python
from nanosat_mbse import StateAllocation

receive = ComponentState("Receive", 0.18)
transmit = ComponentState("Transmit", 10.8)
session.configure_load(
    component,
    states=(receive, transmit),
    allocations={"Downlink": (StateAllocation(receive, 99), StateAllocation(transmit, 1))},
)
```

State duties within a component and mode total at most 100 percent.
Unallocated time contributes zero power. Use an explicit zero-power Off state for a complete off mode.
Average draw is quantity times the sum of each allocated state's power times its duty divided by 100.
Active draw is quantity times the largest allocated state power, including zero-duty states.
Across components, active draw remains a conservative sum of independent maxima.
An `allocations` table replaces the previous mixture table and removes legacy assignments for the same modes.
Replacing `assignments` without `allocations` returns the component to legacy allocation semantics.
Power limit checks retain active draw, so low duty cannot conceal an active overload.
Software demand belongs to its execution host.
Battery storage, generation and passive components start excluded from load demand.
Mass and volume accounting still includes physical hardware.

`PowerLoss` is an explicit dissipative contribution with the same states, quantity and allocations.
Add it under a spacecraft subsystem, including EPS or payload, using `session.add(PowerLoss(), owner=subsystem)`.
It is never automatically instantiated and has no mass or volume budget.
Count a loss only when it is absent from the other loads at the declared accounting boundary.
No converter-loss solver or automatic efficiency model is introduced.

Each power limit requirement exposes `draw_power_W`, `average_power_W`, `assessment_duration_s` and `energy_Wh`.
Set the spacecraft requirement's `assessment_duration_s` through the existing parameter editor or Python API.
Subsystems and components inherit their parent's duration unless explicitly overridden.
Use the editor's State selector or `configure_parameter_states()` for different assessment durations by spacecraft mode.
Independent cases need no orbital mode shares and their durations need no normalization.
Energy is average power times assessment duration divided by 3600.
Unset durations leave energy pending while power checks remain usable. Configured durations must be positive when energy is evaluated.
These energies assess independent constant-average operating cases and imply no chronological battery closure.
Reconciliation adds missing assessment parameters to older budget requirements while preserving existing bindings and deliberately deleted requirements.

`connect_power(eps, roots=...)` binds its LoadEnergy requirement to weighted component-mode demand.
Component duty is applied within each mode before the separate sunlight/eclipse mode shares.
Expressions and upstream parameters are evaluated in the mode whose share is being counted.
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

### Recovery from depth of discharge

The generic `BatteryRecoveryOrbits` requirement (normally SIZ017) calculates:

```text
net_orbit_energy_J = generated_energy_J - load_energy_J
recovery_orbits = pack_eol_J * recovery_dod / net_orbit_energy_J
```

`max_recovery_orbits` starts unset. Supply the approved maximum to assess the requirement.
Capacity, generation, load energy and DoD initially reference the existing generic EPS parameters.
Both energies must cover one repeating orbit at the same accounting boundary.
This is a fractional orbit estimate with constant positive net energy and unrestricted charge acceptance.
It excludes charge taper and storage-path losses. Use `EnergySegment` separately for chronological service and charge limits.
A positive DoD with nonpositive surplus fails the requirement and leaves its recovery count pending.
Zero DoD requires zero recovery orbits.

### Circular orbit illumination

The existing `IlluminationPeriods` requirement owns `beta_deg`, in degrees, with a default of zero.
Beta is the signed angle between the Sun direction and the orbital plane. Its valid range is -90 to 90 degrees.
Edit it in the existing parameter table, bind it to another requirement parameter, or use Python:

```python
session.get("ORB002").set_value("beta_deg", 73)
```

The preliminary calculation assumes a circular orbit, constant beta, parallel solar rays and a cylindrical Earth shadow.
It reduces to the former geometry at beta zero and gives equal eclipse durations for positive and negative beta of equal magnitude.
At or above the critical absolute beta angle, eclipse duration is zero and sunlight lasts the full orbit.
This model excludes penumbra, eccentricity and variation of beta over time. Use the separate `Illumination` analysis for its epoch dependent geometry.

`LoadEnergy` returns zero energy for an absent sunlight or eclipse period without requiring that period's power or duty inputs.
A connected budget also skips the absent period's mode shares and state assignments.
A positive period still requires valid loads and mode shares, and the total assessed interval must be positive.
Power averages remain usable before orbit durations are supplied.

Opening a saved session or calling `reconcile_defaults()` adds a missing beta input and upgrades exact former library expressions and checks.
Authored expressions, conditions, cleared inputs and deliberately deleted requirements retain their configuration.
Direct source and projection imports remain unchanged until explicit reconciliation.

The separate `Illumination` script also supports prescribed constant rotation about an axis fixed in the local orbital frame.
The generic `ArrayAttitude`, `ArrayPanelModel` and `ArrayIllumination` requirements own its numeric inputs.
Initial orientation is active `Rz(yaw) Ry(pitch) Rx(roll)`, followed by the prescribed rotation.
Electrical generation uses incident irradiance times declared active cell area, electrical efficiency and retention.
The script returns only scalar energy, mean power and sampled extrema. It stores no history and infers no operating point.
The scenario factory binds these requirements when there is one EPS and adds a generation criterion.
Existing script pins require explicit definition review before running the changed interface.

Regression checks for illumination geometry, rotation, recovery, state mixtures, losses, persistence and UI transport:

```sh
PYTHONPATH=framework/python/src python3 -m unittest discover -s framework/python/tests -v
npm test --prefix framework/requirements-ui
```

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
The UI and CLI default to `framework/sessions/current.py` in a source checkout and store named sessions directly under `framework/sessions/`.
Outside a checkout, the default is `sessions/current.py` under the working directory.
`MISSION_FILE` or `--mission` selects a different workspace.
`--from` and `--orbit` select an existing session and orbit for independent scenario copies.
Original source files remain intact, and creating a study runs no analysis.

See the [shared REPL demonstration](docs/repl.md) for opening the same native file as the UI, changing inputs, running MPPT, and saving/reloading safely.
