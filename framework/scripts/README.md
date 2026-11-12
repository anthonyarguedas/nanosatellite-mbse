# Engineering calculations

`sizing.py` implements the preliminary EPS sizing and scalar array/battery configuration calculations in `final_report/design-proposal.tex`.
`illumination.py` calculates fixed body geometry and full-orbit illumination averages.
Both use the Python standard library.
Public functions have required annotated inputs and return annotated NamedTuples.
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
- `cell_power`: EOL maximum power point voltage times current, in W.
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
