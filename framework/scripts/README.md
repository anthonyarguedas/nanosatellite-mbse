# Engineering calculations

`sizing.py` implements the preliminary EPS sizing and scalar array/battery configuration calculations in `final_report/design-proposal.tex`.
`illumination.py` calculates fixed body geometry and full-orbit illumination averages.
Both use the Python standard library.
Public functions have individually named, annotated inputs and return annotated NamedTuples.
`cell_power` accepts either its scalar MPP inputs or optional PV points. Existing scalar calls remain valid.
They can be called directly with numbers or through the model's Property-binding interface.
Importing the module executes no analysis.

Each Mission includes `import framework.scripts.sizing as sizing` and `import framework.scripts.illumination as illumination` in its expression namespace.
There is no result cache, subprocess isolation or timeout.
The previous GUI analysis implementations and their registry have not been restored.

## Orbit calculation

The geometry assumes Keplerian motion, a spherical Earth, a cylindrical shadow and a fixed Sun direction for one orbit.
Lengths use km and time uses s.
Beta and the perigee-to-Sun projection angle enter the Python interface in degrees.
The calculations convert them to radians.

`orbit_period` checks `0 <= e < 1`, positive Earth constants and perigee above Earth.
`circular_illumination` uses the circular beta-angle relation.
`eccentric_illumination` finds the night-side shadow boundaries and converts their true anomalies to mean anomalies.
It sums their positive time spans.
Both return eclipse and sunlight durations.
An orbit without eclipse returns zero eclipse duration.

For eccentric geometry, write `x = nu - lambda - pi` on the night side and `t = tan(x/2)`.
The night side is `-1 < t < 1`.
After multiplying the boundary equation by `(1+t²)²`, it becomes a quartic polynomial.
Real roots are isolated between derivative roots and refined by bounded bisection.
This avoids an angular sampling grid that could miss a short eclipse.
Negative polynomial intervals identify shadow arcs.
The implementation uses floating point arithmetic, including roundoff handling at circular tangency.
It provides no Earth precession, penumbra, evolving Sun direction or atmospheric model.

## Fixed geometry and orbit-averaged illumination

- `cubesat_dimensions`: nominal X, Y and Z allocation lengths in m for 1U, 1.5U, 2U, 3U, 6U and 12U.
- `face_normal`: outward unit normal for one of the six `Face` identifiers.
- `face_area`: gross area of that face from three positive body dimensions in m.
- `orbital_projection`: sunlight-mean projected illumination and equivalent projected sunlight duration, in s per orbit.

The nominal dimensions use 10 cm units. The 6U and 12U layouts are 2 by 1 by 3 and 2 by 2 by 3 units.
These boxes exclude rails, dispenser allowances, clearances and detailed cell layout.
Usable area is an explicit installation input.

The projection follows [Freimann et al., Sec. II.i](../../final_report/corpus/review-reports/review-report-1231/review-report-1231.md#L64): `max(0, normal dot Sun direction)`.
Earth shadow and a panel facing away from the Sun are separate geometric effects, as in [Qureshi, Sec. 2.2](../../final_report/corpus/review-candidates/review-candidate-1017/review-candidate-1017.md#L704).
The script shares the shadow-boundary calculation with `sizing.py`.
It excludes eclipse arcs and weights the remaining projected illumination by elapsed orbital time.
Mean angles and orbit-mean projection factors are not substituted for the sunlight-time mean.

`Pointing.SUN_POINTING` keeps the selected body face toward the Sun.
Each fixed panel normal then has constant projection onto that face normal.
`Pointing.NADIR` keeps the selected face toward Earth's center at a declared clocking angle in the local orbital frame.
See [the model guide](../models/README.md#fixed-geometry-and-illumination) for the clocking convention.

For nadir pointing, write the projection as `A*cos(nu) + B*sin(nu) + C`.
Using eccentric anomaly E and `dt = (1 - e*cos(E))/n * dE` gives the projected-time integrand:

```text
max(0, (A - e*C)*cos(E) + sqrt(1-e²)*B*sin(E) + C - e*A) / n
```

The script splits sunlit arcs at the zeros of this expression and integrates each positive interval analytically.
It uses no time grid or integration step.
The changing positions, shadow intervals and panel projections stay internal.
Properties expose only fixed inputs and scalar summaries.
A complete-orbit average under these prescribed laws needs no initial epoch or phase.

The assessment assumes an unobstructed section, a fixed Sun per orbit and exact prescribed pointing.
It includes no attitude dynamics, slew, pointing error, deployment motion, self shading, penumbra or annual ephemeris.
Other pointing laws and supplied histories require a separate calculation.
Normal vectors are normalized after validation. Zero vectors, unknown faces and unsupported pointing choices raise errors.

## Sizing calculation

- `load_energy`: period-average power times duration, in J.
- `minimum_panel_power`: `(E_s / X_s + E_e / X_e) / T_s`, in W.
- `cell_power`: EOL maximum power point voltage times current, or sampled MPP power from optional `pv_points`, in W.
- `cell_count`: fractional power ratio and its integer ceiling.
- `mission_cycles`: lifetime times days per year times `86400 / T_o`.
- `depth_of_discharge`: invert `N = a * DoD**b` for positive `a` and negative `b`.
- `battery_energy`: `E_e / DoD * (1 + M)`, in J.
- `retained_value`: apply a declared retention factor between zero and one.
- `parallel_strings`: fractional and ceiling parallel-string bounds for an entered positive integer series count. Total demand and per-cell rating use the same unit, such as W or J.
- `panel_area`: active area divided by packing fraction, in m2.
- `solar_efficiency`: BOL efficiency times lifetime retention and a temperature factor.
- `array_power_density`: constant irradiance times corrected cell efficiency, inherent retention, assembly efficiency and sunlight-mean projection in `[0, 1]`, in W/m2.
- `minimum_array_area`: required power divided by positive available power density, in m2.
- `tumbling_array_area`: Nogrady's six-face, half-illuminated, 50 degree approximation divided by packing fraction.

The cycle model uses an explicit characterized DoD interval inside `(0, 1]`.
The chosen DoD is the largest value within that interval that meets the required cycle count.
A smaller required cycle count can therefore select the interval's upper bound.
A required count beyond the interval's lower-bound capacity raises an error.
The preliminary estimate assumes one cycle per orbit.

Efficiencies, EOL cell ratings, mission lifetime, calendar convention, battery curve data and margins have no assumed numerical values.
They are supplied by a session.
Nonfinite inputs and invalid physical domains raise errors.

These equations provide scalar comparison bounds for the current configuration.
Series/parallel counts are explicit user inputs. No product counting, topology inference, configuration search or mode sweep is performed.
Array power density assumes constant irradiance, temperature and losses while orientation varies according to the prescribed pointing law.
The selected operating-power fraction adjusts the reference MPP efficiency before the area and generation checks.
This preserves the existing constant-efficiency approximation with a fixed normalized I-V shape and fixed operating voltage for each case.
It supplies no irradiance-dependent voltage shift or chronological battery/array coupling.
Area and generation checks use the same sunlight-mean density.
A supplied external history can instead provide an applicable mean density or available power.
Source energy is mean available power times sunlight duration, without another eclipse duty factor or path loss.
It establishes no delivered energy at the load boundary.
Zero irradiance, zero efficiency or zero sunlight projection produces zero power density.
Positive demand at zero density fails the generation screen and has no finite required area.
The required-area calculation therefore requires positive power density.
The tumbling approximation applies only to its stated geometry and uniform packing.
All loss factors, efficiencies and geometric assumptions remain explicit inputs.
BOL sizing margin is applied once.
Battery retained energy and charge use their separate factors without applying the margin again.
The battery energy screen compares its BOL rating with the report's preliminary BOL requirement.
It establishes no chronological reserve, charging acceptance or EOL service claim.

See [the example session](../sessions/example_eps_sizing.py) for synthetic inputs and [the model guide](../models/README.md) for ownership.

## Electrical extrema and protection screening

- `extrema(values)`: minimum and maximum of a nonempty finite sequence on one electrical path.
- `load_current_extrema(powers, minimum_voltage, maximum_voltage)`: independent power/voltage corners, returning `P_min / V_max` and `P_max / V_min` in A.

The voltage interval is strictly positive. Powers are nonnegative and include losses at the assessed source boundary.
The calculation combines independent extremes conservatively. It assumes no pairing or chronology between cases.
Measured or otherwise established current cases can use `extrema` directly.
Period-average budgets establish no peak-current bound.

`Protection` and `CotsProtection` use these extrema in automatically created `no_trip` Requirements.
Samples and COTS thresholds share the detector's actual sensing boundary and selected operating conditions.
The UV comparison uses the highest applicable trip threshold. OV and OC use the lowest.
Equality fails. These checks establish normal operation for an enabled, recovered device.
They establish no fault response, interruption stress or recovery behavior.

## Optional photovoltaic characteristics

`cell_power(eol_voltage=..., eol_current=...)` preserves its scalar interface.
Alternatively, pass only `pv_points=((V0, I0), (V1, I1), ...)`.
Supplying both input forms is an error.
Each point uses V and A for one cell or one explicitly represented purchased panel.

`pv_characteristics(pv_points)` returns MPP voltage/current, maximum sampled power, open-circuit voltage and short-circuit current.
Samples must be finite, nonnegative and strictly increasing in voltage.
They must span `(0, Isc)` to `(Voc, 0)` and include a positive power point.
The largest sampled `V * I` is the reported MPP. Sparse data must include the manufacturer's MPP point.
The MPP calculation infers no continuous curve, interpolation, diode fit or extrapolation.

`pv_efficiency(pv_points, active_area, reference_irradiance)` returns sampled MPP power divided by incident reference power.
Area is in m2 and irradiance in W/m2. The resulting efficiency must lie in `(0, 1]`.
`SolarArray.cell_iv_curve` opts into this calculation for the existing generation and area checks.
With an empty curve, those checks retain the scalar efficiency path.
The script reads no catalog files. The caller selects a coherent product, characteristic, condition and units.
Generation retains the existing linear irradiance scaling at constant efficiency.
Reference voltage/current characteristics keep their selected temperature, irradiance and degradation conditions.
There is no automatic temperature, degradation or shading correction.

## Solar transfer methods and operating points

- `transfer_selection`: validate `DET`, `MPPT` or `FIXED_VOLTAGE`.
- `solar_operating_voltage`: add the declared DET drop to bus voltage, or use the MPPT reference or fixed input setpoint.
- `pv_operating_point`: return array voltage, current and power at an imposed voltage under one selected cell characteristic.

`SolarPowerPath` holds the selector and path inputs.
`SolarArray.power_path` explicitly identifies that path.
The model reads only the selected branch's inputs and retains `eol_voltage`, `eol_current` and `eol_power` as MPP references.
MPPT is an ideal MPP reference. The actual controller's startup, tracking behavior and conversion envelope need separate evidence.
Fixed input-voltage control uses an explicit setpoint and establishes no automatic MPP search.
DET uses a supplied voltage drop at the assessed current. Current-dependent wiring losses need their applicable circuit solution.

`pv_operating_point` requires the complete characteristic accepted by `pv_characteristics` and positive integer series/parallel counts.
The default `interpolation="none"` accepts exact sampled voltages.
The caller can explicitly accept `interpolation="linear"` between adjacent samples.
Three catalog anchors support only a declared straight-segment approximation between them.
The calculation supplies no physical diode fit or guaranteed off-MPP accuracy.
Voltages outside the characteristic are errors. Reverse blocking, disconnected sources and unavailable arrays require explicit cases.
A partial graph is still rejected rather than extended to an invented endpoint.

Operating power is at the array terminals.
DET bus power is bus voltage times array current for the stated simple path.
MPPT or fixed-setpoint output power needs applicable conversion losses.
Neither an ideal MPP voltage nor a computed source power establishes delivered energy, charge acceptance or successful tracking.
Run `python3 -m framework.sessions.example_eps_transfer` for a sourced curve with explicit interpolation and assumed path losses.

Run `python3 -m framework.sessions.example_eps_operating_limits` for sourced PV and no-trip examples.
The example loads the existing catalog and exercises both scalar and optional PV inputs.

## BIRDS-4 comparison tables

`birds4_tables.py` formats the [BIRDS-4 example session](../sessions/example_birds4_power_budget.py) as standalone HTML and CSV tables.
Run `python3 -m framework.scripts.birds4_tables` from the repository root.
Use `--output DIRECTORY` to choose another destination.
The default output is `framework/sessions/birds4/`.
The generator preserves the reference table layouts and shows reference, model and difference values.
All engineering formulas remain in model Property expressions and the existing numerical scripts.
The [reconstruction notes](../sessions/birds4/README.md) distinguish measured inputs, supplied MATLAB results, independent calculations and source discrepancies.
