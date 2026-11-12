# Model API

These modules implement `prompt.md` for Python scripts and a REPL.
They have no GUI imports, workbook schema, product database, restricted interpreter or persistence protocol.
Expressions execute trusted Python with full builtins and user permissions.
Units are descriptive annotations.
Values and verification results are recomputed on every request.

## Files to review

| File | Responsibility |
| --- | --- |
| `properties.py` | Unit annotations, expressions, modes and observed dependencies |
| `objects.py` | Property ownership, containment and default creation |
| `functions.py` | Explicit imports and required Function inputs |
| `stakeholders.py` | Stakeholders, their classifications and ThirdParty |
| `elements.py` | Segments, subsystems, components and Orbit |
| `spacecraft.py` | CubeSatBus and named subsystem types |
| `eps.py` | EPS defaults, component properties and fixed COTS classes |
| `modes.py` | Distinct mode, state and allocation classes |
| `requirements.py` | Conditions, evaluation status and failure paths |
| `mission.py` | One configuration and its expression namespace |

## Objects and Properties

```python
from framework.models import Mission, CubeSatBus, Property, Requirement, VerificationCondition

mission = Mission()
bus = mission.add(CubeSatBus("BUS"))
eps = bus.EPS
battery = eps.Battery
battery.mass = Property("0.2", "kg")

for component in eps.components:
    if component is not battery:
        component.mass = 0.05

requirement = mission.add(Requirement("mass_limit"))
condition = requirement.add(VerificationCondition(
    "maximum", eps.mass, Property("0.3", "kg"), "measure <= target",
))
report = mission.verify()
assert report.verified is False
for failure in report.for_instance(battery).failures:
    print(failure.explain())
```

`Session` is an alias for `Mission`.
A `Property` is a binding object. Read `battery.mass.value` to evaluate it.
Set `battery.mass.expression` to change its formula.
Assigning a literal such as `battery.mass = 0.2` stores its Python literal expression.
Assigning another bound Property stores a live reference to that Property, including before attachment.
Additional properties use `object.define("name", Property(...))`.
Inherited declarations are copied into independent instance bindings.
A custom Component specialisation declares its compatible `subsystem_type`.

Expressions reference values explicitly:

```python
battery.mass.expression = "0.1 + 0.1"
requirement.define("margin", Property("1.1"))
condition.measure.expression = "mission.BUS.EPS.mass.value * mission.mass_limit.margin.value"
```

Names are Python identifiers and remain fixed.
Sibling names are unique and cannot shadow existing attributes.
Full paths such as `mission.BUS.EPS.Battery` work in expressions.
A globally unique name also works as a short alias.
`self` is the Property's owner. `mode` is the explicitly selected mode or state.
`mission.get("BUS.EPS.Battery.mass")` returns the binding without evaluating it.
Cycles and references outside the Mission produce errors.

`Property.assess()` returns `value`, `pending` or `error` status.
An unset expression is pending.
Direct `.value` reads raise exceptions when evaluation cannot complete.
There is no unit conversion or dimensional checking.

## Functions

Put longer calculations in a normal importable module:

```python
# calculations.py
from typing import NamedTuple

class Energy(NamedTuple):
    joules: float

def energy(power: float, duration: float) -> Energy:
    return Energy(power * duration)
```

Then bind every input explicitly:

```python
mission.add_import("import calculations as calc")
requirement.define("power", Property("2", "W"))
requirement.define("duration", Property("10", "s"))
requirement.define("energy", Property(
    "calc.energy(power=mission.mass_limit.power, duration=mission.mass_limit.duration).joules",
    "J",
))
```

Custom functions have required, individually named and annotated inputs.
Defaults, variadic arguments and optional annotations are rejected.
Each call supplies actual Property objects, without `.value`, as its arguments.
The wrapper resolves their values and calls the function.
A custom function returns its declared NamedTuple type with annotated fields.
Annotations describe the interface. Python remains responsible for field value types.
Ordinary `math` functions operate on values, such as `math.sqrt(self.mass.value)`.

Calls have no value cache, timeout, isolation or sandbox.
Dependencies read through Property inputs are traced.
Other dependencies and side effects inside functions remain the accepted gap from the prompt.

## Modes and allocations

`SpacecraftMode`, `ComponentMode`, `ComponentState`, `OrbitAllocation`, `ModeAllocation` and `StateAllocation` are separate classes.
Allocations hold an explicit `fraction` Property.
An unspecified fraction remains pending.
No normalization, automatic power averaging or chronology is imposed.

```python
from framework.models import SpacecraftMode, ComponentMode, ModeAllocation

nominal = bus.add(SpacecraftMode("nominal"))
nominal.allocation.fraction = 1
active = battery.add(ComponentMode("active"))
active.add(ModeAllocation("nominal_share", nominal, 1))
active.on.voltage = 3.7
active.on.current = 0.1
battery.power.bind(nominal, "self.active.on.power.value")
assert battery.power.evaluate(mode=nominal) == active.on.power.value
```

Component modes initially contain `on` and `off` Component States.
Each state owns Voltage, Current and the explicit `voltage * current` Power expression.
Both states start with unset electrical inputs.
A Subsystem reads its parent's current Spacecraft Modes.
Use `mission.verify(mode=nominal)` to assess one selected mode.
No automatic all-mode compliance policy is assumed.

## COTS and aggregation

Product classes fix their property bindings:

```python
from framework.models import CotsBattery

class SelectedPack(CotsBattery):
    mass = Property("0.2", "kg")
    rated_energy = Property("12", "Wh")

pack = battery.add(SelectedPack("pack"))
mission.add_import("import framework.models as models")
battery.mass.expression = "sum(c.mass.value for c in self.cots if isinstance(c, models.Battery))"
```

COTS instance property expressions, units and mode bindings are immutable.
Missing product properties remain pending.
A combined product can inherit several EPS component types and COTS.
Python's normal method resolution order resolves inherited declarations.
Define conflicting product properties explicitly on the combined class.

Containment gives each physical instance one parent.
Adding the same object again leaves it counted once.
Attach an integrated product once and reference its properties from other objects.
COTS selections nested under a component contribute through that component's chosen expressions.
They are never separately added to the parent's default sum.
Separate installed units use separate instances.
Alternatives belong in separate Missions.

Segment sums read immediate Subsystem totals.
Subsystem sums read immediate Component contributions.
Each class can replace its aggregate expressions to choose its accounting boundary.
The EPS demand sum excludes Battery and SolarArray instances by default.
Override `EPS.power_consumers` for a different boundary or an integrated device.
No quantity, efficiency or loss is silently inferred.

## Verification and restoration

A condition evaluates `measure` and `target`, then its Boolean expression.
Its Boolean result is separate from its evaluation status.
False conditions propagate to every instance and Property observed through Measure dependencies.
Target-only dependencies receive no propagated result.
Reports retain the Requirement, condition, actual values and dependency path for each failure.
Use `report.for_instance(object_or_property)` or its full path to inspect coverage.
`.verified` is `True` for all passing covering conditions, `False` for any failed condition, and `None` for incomplete or absent coverage.
`.status` keeps pending inputs and errors visible.
Observed dependencies follow the branches actually evaluated.

Defaults run on an object's first explicit add.
Removing a default and calling `initialize()` preserves that deletion.
Restore a saved configuration with `Class.restore(...)` and explicit remaining children, or `parent.add(child, initialize=False)`.
`Mission.restore()` starts without an automatically created Orbit.
No file loading, source generation or browser metadata is part of this API.
Ordinary Python session files construct the saved instances directly.

Eccentricity is an Orbit Property.
Illumination calculations and detailed allocation policies remain deferred.
