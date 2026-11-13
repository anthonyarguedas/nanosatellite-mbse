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
| `geometry.py` | Body face and prescribed pointing enums |
| `spacecraft.py` | CubeSatBus and named subsystem types |
| `eps.py` | EPS defaults, solar power paths, component properties and fixed COTS classes |
| `modes.py` | Distinct mode, state and allocation classes |
| `requirements.py` | Conditions, evaluation status and failure paths |
| `mission.py` | One configuration and its expression namespace |

## Objects and Properties

```python
from framework.models import Mission, CubeSatBus, Property, Requirement, VerificationCondition

mission = Mission()
bus = mission.add(CubeSatBus("BUS", units=1))
eps = bus.EPS
battery = eps.Battery
battery.mass = Property("0.2", "kg")

for component in eps.components:
    if component is not battery:
        component.mass = 0.05

requirement = eps.add(Requirement("mass_limit"))
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
Assigning an Enum member stores its underlying value as a Python literal, so `panel.mounting_face = Face.POS_Y` evaluates to `"+Y"`.
Assigning another bound Property stores a live reference to that Property, including before attachment.
Additional properties use `object.define("name", Property(...))`.
Inherited declarations are copied into independent instance bindings.
A custom Component specialisation declares its compatible `subsystem_type`.

Expressions reference values explicitly:

```python
battery.mass.expression = "0.1 + 0.1"
requirement.define("margin", Property("1.1"))
condition.measure.expression = "mission.BUS.EPS.mass.value * mission.BUS.EPS.mass_limit.margin.value"
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
    "calc.energy(power=mission.BUS.EPS.mass_limit.power, duration=mission.BUS.EPS.mass_limit.duration).joules",
    "J",
))
```

Custom functions have individually named and annotated inputs.
Inputs without defaults are required. Omitted inputs retain the Python function's declared defaults.
A nullable input annotation requires a default. Variadic arguments are rejected.
Each supplied argument is an actual Property object, without `.value`.
The wrapper resolves supplied values and calls the function.
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
Call `property.unbind(mode)` to remove an override and use its default expression again.

## Orbit and preliminary EPS sizing

Every Mission imports `framework.scripts.sizing` as `sizing` and `framework.scripts.illumination` as `illumination` alongside `math`.
The numerical code stays in [the sizing script](../scripts/sizing.py) and [the illumination script](../scripts/illumination.py).
Model Properties declare fixed inputs and expose scalar results for the assessed configuration.
Orbital phase, instantaneous orientation, panel incidence and Earth shadow stay internal to the scripts.
Attach Orbit to a Mission before evaluating calculations that use these session imports.

Orbit owns Earth radius (6378 km), gravitational parameter (398601 km3/s2), semimajor axis, mean motion, period, orbits per day and eclipse/sunlight durations.
The defaults for Earth constants follow the report.
Altitude, eccentricity and beta remain explicit inputs.
`semimajor_axis` defaults to Earth radius plus `altitude`, so altitude is the offset of the semimajor axis from Earth's surface.
Supply `semimajor_axis` directly when that is the known eccentric-orbit parameter.
Perigee must remain above the spherical Earth.

Beta and `sun_projection_angle` use degrees at the model interface.
The script converts them to radians.
For an eccentric orbit, `sun_projection_angle` is the angle from perigee to the Sun's projection in the direction of motion.
Circular orbits and beta angles of ±90 degrees need no projection angle.
`effective_sun_projection_angle` supplies the arbitrary angular reference zero in those cases and otherwise reads the explicit input.
The model supports the report's cylindrical-shadow entry/exit method, including eclipse intervals crossing the angular origin.
It returns zero eclipse duration when the orbit is fully sunlit.

Adding an EPS creates these ordinary Requirements as its own children.
Names are local to the EPS, such as `eps.solar_power`, so multiple EPS instances remain independent.

| Requirement | Its `required` Property |
| --- | --- |
| `sunlight_energy` | Mean sunlight load power times sunlight duration, in J |
| `eclipse_energy` | Mean eclipse load power times eclipse duration, in J |
| `solar_power` | `(E_s / X_s + E_e / X_e) / T_s`, in W |
| `solar_cell_count` | Ceiling of required power divided by EOL cell power |
| `battery_energy` | `E_e / DoD * (1 + M)`, in J at BOL |

```python
mission = Mission(lifetime=2, days_per_year=365.25)
mission.orbit.altitude = 600
mission.orbit.eccentricity = 0
mission.orbit.beta_angle = 0
bus = mission.add(CubeSatBus("BUS", units=1))
eps = bus.EPS
eps.SolarArray.power_path = "self.parent.RegulatorAndConverter"
eps.RegulatorAndConverter.transfer_method = "'MPPT'"  # Ideal MPP reference.
eps.sunlight_energy.average_power = 5
eps.eclipse_energy.average_power = 3
eps.SolarArray.sunlight_path_efficiency = 0.8
eps.SolarArray.eclipse_path_efficiency = 0.65
eps.SolarArray.cell_eol_voltage = 2.3
eps.SolarArray.cell_eol_current = 0.45
print(eps.solar_power.required.value)
print(eps.solar_cell_count.required.value)
```

The average powers represent complete illumination-period means, including duty cycles and EPS consumption at the declared load boundary.
Their products with duration equal the stated energy integrals by definition.
No component schedule, mode normalization or average power is invented.
An absent period contributes zero energy without requiring its average power.
An efficiency for a zero-energy term is unused. Its effective factor is the identity 1, while the SolarArray's actual input remains unchanged.

`SolarArray` owns sunlight/eclipse path efficiencies, EOL cell maximum power point voltage/current, `cell_eol_power`, installed `cell_count` and `eol_power`.
The panel power screen compares installed EOL power with its required power.
The cell screen requires an integer installed count at least as large as the ceiling.
The unrounded ratio is available as `eps.solar_cell_count.fractional_count`.
These remain preliminary uniform-cell power screens.
The configuration checks below assess the entered arrangement and supplied generation conditions.

`Battery` owns cycle-law coefficient/exponent, `fit_dod_min`, `fit_dod_max`, degradation margin and separate energy/capacity retention factors.
Mission lifetime and days per year remain unset until supplied explicitly.
The battery Requirement exposes `required_cycles` and `maximum_dod`.
It assumes one cycle per orbit and chooses the largest supported DoD meeting that lifetime.
Unsupported extrapolation beyond the characterized DoD interval is an error.
The BOL capacity screen uses `Battery.bol_energy`, explicitly converting `rated_energy` from Wh to J.
Cell assemblies derive `rated_energy`, `rated_capacity` and `nominal_voltage` from the entered counts and cell ratings.
Purchased pack ratings can be bound directly to those Properties.
Margin M is applied once in this screen.
`Battery.eol_energy` is retained energy in J. `eol_capacity` is retained charge in Ah.
Neither retained value applies M again.
This preliminary screen establishes no chronological battery or EOL service claim.

Delivered-energy data are separate inputs: `eps.available_sunlight_energy` and `eps.available_eclipse_energy`, in J at the same load boundary as demand.
They stay pending until supplied from an applicable study or explicit allocation.
The two phase energy criteria compare those inputs with their required energies.
A zero demand needs no delivered-energy evidence for that criterion.
All sizing Requirements participate in `mission.verify()` and retain the ordinary transitive failure paths.
Restoration and deliberate default deletions retain their existing behavior.
See [the complete synthetic session](../sessions/example_eps_sizing.py) and [calculation assumptions](../scripts/README.md).

## Array, battery and rail configuration

`SolarArray.series_count`, `SolarArray.parallel_count`, `Battery.series_count` and `Battery.parallel_count` start unset.
They accept literals or ordinary expressions supplied by the user.
For example, a user-defined **1S assembly of single-cell COTS products** can count its parallel cells with:

```python
battery.series_count = 1
battery.parallel_count = "len(self.cots)"
```

The user implements and validates this expression for the actual arrangement.
The framework does not infer topology, divide an installed count into strings, count products automatically or select another configuration.
Each `cell_count` defaults to `series_count * parallel_count`.
The configuration Requirements check positive native integer counts and consistency with the installed count.
Explicitly overriding `cell_count` preserves this consistency check.
`eps.solar_cell_count.minimum_parallel_count` and `eps.battery_energy.minimum_parallel_count` expose comparison bounds for the entered series count. They do not change it.

Array voltages scale with series count and currents with parallel count.
`eol_voltage` and `eol_current` remain MPP reference quantities and use the existing EOL cell maximum power point ratings unless `cell_iv_curve` selects PV points.
`open_circuit_voltage` and `short_circuit_current` use their separate cell ratings.
Battery charge capacity scales with parallel count, energy with total cell count and voltage with series count.
Battery voltage bounds and separate charge/discharge current limits have corresponding `cell_*` inputs.
These relations assume identical cells, matched conditions and balanced sharing.
Packaging, protection and interconnect limits can require stricter aggregate ratings.

The additional EPS Requirements are:

| Requirement | Check |
| --- | --- |
| `solar_configuration`, `battery_configuration` | Positive integer series/parallel counts and consistent installed count |
| `solar_area` | Active area at least required power divided by available power density |
| `solar_area_fit` | Panel area at most usable installation area |
| `solar_generation` | Available sunlight power at least the power budget requirement |
| `solar_voltage` | Array EOL operating voltage within explicitly assigned receiving limits |
| `battery_voltage` | Complete pack voltage interval within explicitly assigned receiving limits |
| `solar_open_circuit_voltage` | Array open-circuit voltage at most the assigned absolute input limit |
| `solar_short_circuit_current` | Array short-circuit current at most the assigned permissible source current |
| `bus_voltage` | Nominal source voltage matches the required load voltage within an explicit tolerance |
| `bus_current` | Selected path capacity at least the declared load current |
| `battery_charge_current`, `battery_discharge_current` | Separate battery current capacity at least the current declared at its terminals |

### Solar power path and operating point

`SolarPowerPath` owns `transfer_method`, `bus_voltage`, `voltage_drop` and `input_voltage_setpoint`.
`RegulatorAndConverter` and `PowerCircuit` inherit these inputs.
The inputs start unset. The model selects no wiring or transfer method.
`SolarArray.power_path` is an explicit expression returning the connected path object:

```python
from framework.models import TransferMethod

panel = eps.SolarArray
panel.power_path = "self.parent.PowerCircuit"
path = eps.PowerCircuit
path.transfer_method = TransferMethod.DET
path.bus_voltage = eps.Battery.nominal_voltage  # One declared battery voltage case.
path.voltage_drop = 0.2  # V at the assessed current, including blocking and wiring.
panel.iv_interpolation = "'linear'"  # Explicit acceptance for supplied PV samples.
print(panel.operating_voltage.value)
print(panel.operating_current.value)
print(panel.operating_power.value)
```

| `TransferMethod` | Array operating voltage |
| --- | --- |
| `DET` | Explicit bus voltage plus the declared path drop |
| `MPPT` | `SolarArray.eol_voltage`, the ideal MPP reference |
| `FIXED_VOLTAGE` | Explicit `input_voltage_setpoint` on the path |

`selected_transfer_method` validates the path's selector before calculation.
Enum members and quoted string expressions are equivalent inputs.
The calculation reads only the inputs used by the selected branch.
MPPT leaves bus voltage, drop and fixed setpoint unused.
Fixed input-voltage regulation establishes no automatic search for MPP.
The ideal MPPT branch establishes no tracking accuracy, startup or conversion feasibility.
Use the selected controller's applicable settings and additional checks for those claims.
Fixed-setpoint equality assumes active input-voltage regulation. A source can rise above an inactive voltage floor.
For fractional-Voc control or curtailment, bind `operating_voltage` to an applicable controller calculation instead of assuming ideal MPP.

`operating_current` uses the MPP current when the selected voltage equals the reference MPP voltage.
Other voltages require a complete `cell_iv_curve` at the assessed conditions.
The script scales cell voltage by series count and current by parallel count.
Exact sampled voltages need no interpolation.
`iv_interpolation` defaults to `"none"`. Select `"linear"` explicitly to accept straight segments between samples.
Voltages outside the supplied characteristic are errors. No extrapolation or reverse-blocking behavior is inferred.
A missing path or method remains pending. Unsupported methods and inadequate curves produce errors.

`operating_power` is array-terminal voltage times current, before path losses.
`operating_efficiency` multiplies the reference `generation_efficiency` by `operating_power / eol_power`.
Area and generation screens use this selected operating efficiency consistently.
The existing constant-efficiency irradiance and projection scaling assumes a fixed normalized I-V shape and a fixed operating voltage for each assessed case.
It supplies no voltage correction with irradiance, temperature or battery state.
Changing conditions require applicable curves or an externally established mean power.
A supplied mean projection alone does not establish an actual DET history.
MPP cell count and installed MPP power remain preliminary reference screens.

For the simple DET path, delivered bus power is `bus_voltage * operating_current` before any additional consumption.
For an ideal MPPT reference with a characterized converter efficiency, output power is `efficiency * operating_power` before additional consumption.
Supply delivered energy separately at its declared load boundary.
See [the comparison session](../sessions/example_eps_transfer.py) for explicitly assumed losses and sourced PV points.

### Fixed geometry and illumination

`Face` has `POS_X`, `NEG_X`, `POS_Y`, `NEG_Y`, `POS_Z` and `NEG_Z` members.
Their values are the corresponding body face identifiers, such as `"+Y"`.
`CubeSatBus.length_x`, `length_y` and `length_z` use nominal 10 cm unit layouts in m:

| Units | X, Y, Z unit counts |
| --- | --- |
| 1, 1.5, 2, 3 | 1, 1, units |
| 6 | 2, 1, 3 |
| 12 | 2, 2, 3 |

These allocation boxes exclude rails and dispenser allowances.
They establish no mechanical compliance or panel layout claim.
Override the three dimensions for a specified bus or another form factor.
Unsupported nominal layouts raise an error when their dimensions are evaluated.

`SolarArray.mounting_face` determines its outward `normal_body` and nominal `body_face_area`.
The area uses the two body dimensions perpendicular to the selected face normal.
`usable_area` remains an explicit installation allocation after clearances.
For example, `panel.usable_area = "0.8 * self.body_face_area.value"` allocates 80% of the nominal body face.
A deployed section can override `normal_body` with a constant three-component body-frame expression and supply its deployed usable area.
The face remains its mounting reference. Its nominal body area is a comparison value.
The illumination script normalizes every nonzero panel normal.

`AttitudeDeterminationAndControl` owns `pointing`, `pointing_face` and `clocking_angle`.
All three inputs start unset.
`Pointing.SUN_POINTING` keeps the declared body face toward the Sun.
`Pointing.NADIR` keeps it toward Earth's center with fixed clocking in the local orbital frame.
At zero clocking, the next cyclic positive body axis (+Y for ±X, +Z for ±Y, +X for ±Z) aligns with the along-track direction.
Positive clocking follows the right-hand rule about the pointing direction.
Clocking has no effect on panel projection under ideal Sun pointing and can remain unset.
`effective_clocking_angle` supplies the unused value zero for that law and otherwise reads `clocking_angle`.

```python
from framework.models import Face, Pointing

attitude = bus.AttitudeDeterminationAndControl
attitude.pointing = Pointing.NADIR
attitude.pointing_face = Face.NEG_Z
attitude.clocking_angle = 0
panel = bus.EPS.SolarArray
panel.mounting_face = Face.POS_Z
panel.usable_area = "0.8 * self.body_face_area.value"
print(panel.sunlight_projection.value)
```

The script calculates `sunlight_projection` as the sunlight-time mean of `max(0, normal dot Sun direction)` over one full orbit.
It accounts for Earth shadow using the same geometry as the orbit duration calculations.
An initial epoch or phase is unnecessary for these prescribed full-orbit averages.
No changing state, eclipse flag or incidence angle is exposed as a model Property.
The model assumes exact prescribed pointing, a fixed Sun per orbit and an unobstructed section.
Slew, pointing error, deployment motion, self shading, penumbra and attitude dynamics need a separate assessment.
The default array represents one uniformly oriented section. Other orientations need separate sections and explicit aggregation.
Electrical topology remains independent of mounting geometry.

### Area and generation assumptions

`active_area` defaults to cell count times `cell_active_area`.
`panel_area` is active area divided by `packing_fraction`, which must be in `(0, 1]`.
`usable_area` is supplied separately. Area alone establishes no two-dimensional layout or clearance claim.
Purchased panels can bind their specified active and panel areas directly.

`eol_efficiency` applies `bol_efficiency * lifetime_retention * temperature_factor`.
Bind supplied EOL efficiency directly when those effects are already included.
`eol_power_density` applies constant irradiance, selected operating efficiency, inherent retention, assembly efficiency and the calculated `sunlight_projection`.
It is a sunlight-mean power density. The area and generation criteria use this same mean.
No numerical loss factors, packing fraction or pointing inputs are assumed.
`available_power` defaults to active area times that mean density.
`projected_sunlight_duration` is the mean projection times sunlight duration.
`source_energy` is mean available power times sunlight duration, in J per orbit at the declared source boundary.
It is separate from delivered energy at the load boundary.
An external calculation can instead supply a mean density, projection or power under its stated conditions.
Overriding available power alone leaves the area calculation unchanged, so the engineer must keep those assessments consistent.
Shading, mismatched sections and shared trackers require their applicable model. The framework does not synthesize their combined I--V characteristic. DET uses the selected voltage and supplied curve under the operating-point assumptions above.

`eps.solar_area.effective_area` exposes the normal-incidence power/area relation.
`eps.solar_area.tumbling_panel_area` exposes Nogrady's six-face, half-illuminated, 50 degree approximation with uniform packing.
This is an alternative comparison value. It is not automatically imposed on other geometries.
A zero-power source fails the generation check for positive demand. Its required area has no finite value, so the area calculation reports an error.
Physical losses must enter the chosen source boundary once.
These checks establish no chronological energy balance, charging acceptance or EOL service claim.

### Optional photovoltaic data

`SolarArray.cell_iv_curve` defaults to the empty tuple `()` and preserves the scalar sizing path.
Set it to ordered `(voltage_V, current_A)` points for one cell at one selected condition.
The characteristic must include short circuit, a positive MPP point and open circuit.
The calculation uses the largest sampled `V * I`. The MPP calculation performs no interpolation or extrapolation.
The separate operating-point calculation supports explicitly accepted linear interpolation.
A partial digitized trace without both endpoints is rejected.

```python
panel.cell_iv_curve = "((0, 0.501), (2.23, 0.484), (2.519, 0))"
panel.pv_reference_irradiance = 1367
```

These points reproduce the catalog's AZUR 3G30 reference case at 28 C after 1e15 1 MeV electrons/cm2.
The curve supplies the reference MPP power, operating voltage/current, open-circuit voltage and short-circuit current.
Scalar cell electrical ratings remain unchanged and become active again when the curve is cleared.
`generation_efficiency` uses sampled MPP power divided by `cell_active_area * pv_reference_irradiance` for this path.
The existing area and generation checks use that efficiency with actual `irradiance`, installation losses and illumination projection.
Without a curve, `generation_efficiency` references the existing `eol_efficiency`.

Select an explicit product, curve, condition and units from the catalog before binding the points.
Keep cell data separate from a complete purchased panel's data and avoid applying its internal counts again.
Use applicable EOL points for an EOL assessment.
Reference voltage/current characteristics remain at the selected curve conditions.
Generation retains the existing constant-efficiency irradiance approximation.
No temperature correction, automatic tracker restriction, mismatch or shading model is introduced.
See [the sourced operating-limits session](../sessions/example_eps_operating_limits.py) for both scalar and PV paths.

### Required bus voltage and current

A state's `voltage` can be the **nominal required voltage for its declared rail**.
It is not a minimum bus voltage, and a larger source voltage does not automatically pass.
Different load voltages require separate paths or conversion. Taking the maximum over all states would lose that distinction.
Only currents on the same rail at the same operating point can be added directly.
The user supplies allocations, source bindings and conversions between rail and battery current.

For an existing `state` and a selected converter on that load path:

```python
eps.bus_voltage.available = eps.RegulatorAndConverter.output_voltage
eps.bus_voltage.required = state.voltage
eps.bus_current.available = eps.RegulatorAndConverter.maximum_output_current
eps.bus_current.required = state.current
```

The voltage tolerance defaults to zero, an exact nominal match.
Set `eps.bus_voltage.tolerance` explicitly when an accepted voltage tolerance is known.
A nominal match establishes no transient or full operating-envelope compliance.
Use ordinary `.bind(mode, expression)` overrides and `mission.verify(mode=mode)` for a selected spacecraft mode or component state.
No automatic all-mode verification, allocation or averaging is introduced.
For an unpowered switched path, bind its actual voltage and required voltage to zero in that state. Other rails remain separate.

The source receiving intervals use `eps.solar_voltage.minimum_allowed`/`maximum_allowed` and `eps.battery_voltage.minimum_allowed`/`maximum_allowed`.
Their values start unset because the model has no inferred wiring.
For MPPT, assign the applicable tracking interval and assess startup separately.
Assign the absolute voltage and permissible source-current limits through the two solar rating Requirements' `required` Properties.
`RegulatorAndConverter` provides separate operating input, absolute input voltage, input current and output ratings for these explicit links.
Battery charge/discharge Requirements also have explicit `required` current inputs. They do not assume battery current equals load-rail current.

## Protection and normal operating extrema

`Protection` is an EPS `PowerCircuit` specialisation. `CotsProtection` fixes its product Properties on a class.
Adding either type to a Mission creates its owned `no_trip` Requirement through `create_requirements()`.
It can be placed directly under the EPS or as a COTS selection under its compatible PowerCircuit.
It is an explicit selection, separate from the EPS defaults.

The default checks use these selected COTS parameter bounds:

| Parameter | Normal-operation condition |
| --- | --- |
| `undervoltage_threshold` | Minimum sensed voltage strictly above the highest applicable UV trip threshold |
| `overvoltage_threshold` | Maximum sensed voltage strictly below the lowest applicable OV trip threshold |
| `current_limit` | Nonnegative current magnitudes strictly below the lowest applicable OC trip threshold |

```python
from framework.models import CotsProtection, Property

class SelectedEfuse(CotsProtection):
    # TPS259531 catalog bounds, current-limit resistor 1780 ohm.
    undervoltage_threshold = Property(2.53, "V")
    overvoltage_threshold = Property(5.5, "V")
    current_limit = Property(1.09, "A")

protector = eps.PowerCircuit.add(SelectedEfuse("efuse"))
protector.no_trip.voltages = "(4.75, 5.0, 5.25)"
protector.no_trip.currents = "(0.4, 1.0)"
print(protector.voltage_extrema.value)  # Extrema(minimum=4.75, maximum=5.25)
print(protector.current_extrema.value)  # Extrema(minimum=0.4, maximum=1.0)
assert protector.no_trip.verify().verified is True
```

The sampled inputs stay editable on the Requirement, including for a fixed COTS product.
Expressions may reference load states and other Properties. Verification retains their dependency paths.
Voltage samples must describe the detector's sensed node. Cell-level detectors need individual cell voltage bounds.
Current samples are magnitudes in the assessed protected direction, using a threshold for that direction.
Sense-voltage thresholds need an explicit circuit conversion to amperes before binding `current_limit`.
Select the applicable resistor, temperature and configuration bounds when choosing catalog facts.

A product class can declare `trip_parameters = ("current_limit",)` for an OC-only assessment.
The default tuple declares all three detectors. Unset thresholds for declared detectors remain pending.
Missing samples remain pending. Empty or nonfinite samples produce an error.
Equality with a trip threshold fails this conservative screen.
`load_current_extrema` in `sizing.py` can derive current bounds from explicit power cases and a positive voltage interval.
Those powers must include losses at the same source boundary. Period-average powers establish no peak bound.
An unpowered case should only be included if protection is expected to remain inactive in that case.

This is a normal-operation screen for an enabled, recovered device.
Delays, hysteresis, startup, temperature protection, fault interruption and recovery require separate evidence.
Only the declared detectors and supplied operating cases are assessed.
See [the sourced example](../sessions/example_eps_operating_limits.py) for live pass and overload cases.

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

## CubeSat size and bus limits

A CubeSatBus owns a numeric `units` Property annotated with `U`.
It starts unset. Select a size explicitly, such as `CubeSatBus("BUS", units=3)`.
Positive fractional sizes such as 1.5U are also supported.

The first add creates two ordinary Requirements owned by the bus, accessible as `bus.mass_limit` and `bus.volume_limit`:

| Requirement | Measure | Target | Default per-U limit |
| --- | --- | --- | --- |
| `mass_limit` | Entire bus mass | Units times maximum mass per U | 2 kg/U |
| `volume_limit` | Entire accounted bus volume | Units times maximum volume per U | 0.001 m3/U |

```python
bus.units = 3
assert bus.mass_limit.maximum.target.value == 6
assert bus.volume_limit.maximum.target.value == 0.003
bus.mass_limit.maximum_per_u = 1.5  # An explicitly chosen stricter allocation.
```

Each Requirement owns `units`, linked to the bus, and an editable `maximum_per_u` Property.
Changing the bus size or either per-U limit updates its Target through the stored expression.
Known values pass when the size is positive and finite and the Measure lies between zero and the Target.
Unset inputs remain pending.
`bus.requirements` lists the bus's direct Requirement children.
`mission.verify()` checks Requirements throughout the containment tree.
Repeated initialization and restoration preserve deliberate deletions and custom edits.

The mass baseline follows [CubeSat Design Specification Rev 14.1, Table 1](../../final_report/corpus/standards/cds-14.1/cds-14.1.md).
It is a typical planning maximum and must be checked against the selected launch provider and dispenser.
The volume baseline is the nominal 10 cm cube definition of one U.
These are scalar budgets over the contributions included in the bus aggregates.
Packing, bounding dimensions and dispenser fit require separate assessments.

## Requirement ownership

Mission, Orbit, DomainElement, Subsystem, Component and Stakeholder accept Requirements as children.
Each object's `requirements` is a read-only tuple of its direct Requirement children.
Bus and EPS initialization create their own defaults through `self.add_requirement(name, ...)`.
Names are local to the owner, with full paths such as `mission.BUS.EPS.solar_power`.
Sibling name collisions raise an error.

Each generated Requirement has a read-only `context` reference to its owner for calculation inputs.
Authored Requirements may use another context from the same Mission or omit it.
Verification coverage follows Measure dependencies independently of ownership and context.
Authored Requirements can be added with `eps.add(Requirement(...))` or `mission.add(Requirement(...))`.
`mission.requirements` lists only Mission's direct Requirements.
`mission.verify()` checks Requirements at every level of the containment tree.

Physical defaults and authored Requirements can be constructed before attachment.
Default requirement creation waits until their owners belong to a Mission.
Repeated initialization preserves edits and deletions.
A failed add rolls back newly generated Requirements.
Restoration suppresses default requirement creation.
Removing an owner keeps its Requirements attached to it and excludes them from Mission verification until reattachment.

## Requirement prose

Every Requirement has plain text `rationale` and a `statement` template.
Statements use Python's brace-format syntax and can reference owned conditions by name:

```python
requirement.rationale = "Preliminary mass allocation."
requirement.statement = "The mass {maximum.measure:.2f} shall be at most {maximum.target:.2f}."
print(requirement.render_statement())
```

A Property placeholder evaluates its value and appends its Unit annotation.
Use `{maximum.target.value:.2f}` for the number alone and `{maximum.target.unit}` for the unit alone.
`self` refers to the Requirement, including its additional Properties.
`mode` is the selected mode passed to `render_statement(mode=nominal)`.
Double braces, such as `{{literal}}`, produce literal braces.
The former `text` field remains an alias for `statement`.

Statement content is arbitrary and has no checked relationship to verification conditions.
Rendering evaluates only the referenced Properties and never runs a condition's predicate.
A literal statement renders even if verification is pending or failed.
Requested unset values and template errors raise on rendering and leave verification definitions unchanged.
Rationale is ordinary text with no interpolation.

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

Detailed allocation policies and chronological energy simulation remain deferred.
