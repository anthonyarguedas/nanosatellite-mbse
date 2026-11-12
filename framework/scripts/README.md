# Engineering calculations

`sizing.py` implements the preliminary EPS sizing subsection of `final_report/design-proposal.tex`.
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

The cycle model uses an explicit characterized DoD interval inside `(0, 1]`.
The chosen DoD is the largest value within that interval that meets the required cycle count.
A smaller required cycle count can therefore select the interval's upper bound.
A required count beyond the interval's lower-bound capacity raises an error.
The preliminary estimate assumes one cycle per orbit.

Efficiencies, EOL cell ratings, mission lifetime, calendar convention, battery curve data and margins have no assumed numerical values.
They are supplied by a session.
Nonfinite inputs and invalid physical domains raise errors.

These equations provide preliminary scalar screens.
Installed cell count alone establishes no series/parallel arrangement or illumination-dependent generation capability.
BOL sizing margin is applied once.
Battery retained energy and charge use their separate factors without applying the margin again.
The battery energy screen compares its BOL rating with the report's preliminary BOL requirement.
It establishes no chronological reserve, charging acceptance or EOL service claim.

See [the example session](../sessions/example_eps_sizing.py) for synthetic inputs and [the model guide](../models/README.md) for ownership.
