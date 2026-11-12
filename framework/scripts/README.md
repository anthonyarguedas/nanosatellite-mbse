# Engineering calculations

`sizing.py` implements the preliminary EPS sizing and scalar array/battery configuration calculations in `final_report/design-proposal.tex`.
It uses the Python standard library.
Public functions have required annotated inputs and return annotated NamedTuples.
They can be called directly with numbers or through the model's Property-binding interface.
Importing the module executes no analysis.

Each Mission includes `import framework.scripts.sizing as sizing` in its expression namespace.
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
- `array_power_density`: irradiance times corrected cell efficiency, inherent retention, assembly efficiency and projected incidence angle, in W/m2. Angle inputs use degrees.
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
Array power density describes uniform fixed conditions. The model's generation screen needs a conservative sunlight bound or constant sunlight conditions.
A supplied external history can instead provide mean available power.
Zero irradiance, zero efficiency or incidence of at least 90 degrees produces zero power density.
Positive demand at zero density fails the generation screen and has no finite required area.
The required-area calculation therefore requires positive power density.
The tumbling approximation applies only to its stated geometry and uniform packing.
All loss factors, efficiencies and geometric assumptions remain explicit inputs.
BOL sizing margin is applied once.
Battery retained energy and charge use their separate factors without applying the margin again.
The battery energy screen compares its BOL rating with the report's preliminary BOL requirement.
It establishes no chronological reserve, charging acceptance or EOL service claim.

See [the example session](../sessions/example_eps_sizing.py) for synthetic inputs and [the model guide](../models/README.md) for ownership.
