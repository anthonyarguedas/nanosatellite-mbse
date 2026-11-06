# Tether deployment notebook as a Python script

[`tether_deployment.py`](tether_deployment.py) uses `# %%` cells for code and `# %% [markdown]` cells for explanations. It works as a script and in VS Code's Python Interactive window.

## Run

From the repository root:

```sh
uv run cubics-proposal/tether-deployment/tether_deployment.py
```

`uv` installs NumPy, SciPy, and Matplotlib in an isolated environment. The script compares nylon and Dyneema at 2 m and 200 m. It prints a summary for each of the four cases and opens two separate 2x3 grids, one for each tether length. Each grid has its own time and distance scales. It writes no output files by default.

For notebook cells, select a Python environment containing those packages and `ipykernel`. A dedicated environment can be created with:

```sh
uv venv cubics-proposal/tether-deployment/.venv
uv pip install --python cubics-proposal/tether-deployment/.venv/bin/python numpy scipy matplotlib ipykernel
```

Open the script in VS Code with the Python and Jupyter extensions. Select that environment and use **Run Cell** or **Run All**. Edit `params = Parameters(...)` and the material assumptions cell, then rerun the comparison and display cells.

To save a plot from the interactive window:

```python
figures[2.0].savefig("tether-deployment-2m.png", dpi=180)
figures[200.0].savefig("tether-deployment-200m.png", dpi=180)
```

## Inputs to replace

The defaults are illustrative. They are not fitted to STARS-C or to a specific separation mechanism.

| Parameter | Meaning |
| --- | --- |
| `mass_1_kg`, `mass_2_kg` | Satellite masses |
| `altitude_m` | Initial circular orbit altitude |
| `initial_direction_rtn` | Deployment direction, normalized automatically |
| `initial_separation_m` | Initial distance between centres of mass |
| `initial_separation_speed_m_s` | Initial relative speed along that direction |
| `initial_pair_spin_rad_s` | Extra pair rotation about the orbit normal, relative to RTN |
| `spring_stiffness_N_m`, `spring_stroke_m` | Equivalent spring stiffness and initial compression |
| `initial_free_length_m`, `total_tether_length_m` | Unstretched tether length initially outside the reel and total available length |
| `tether_youngs_modulus_Pa` | Effective Young's modulus in pascals for a single simulation |
| `tether_diameter_m` | Equivalent circular tether diameter in metres, shared by the comparison cases |
| `tether_damping_N_s_m` | Effective axial damping, held fixed across materials |
| `payout_friction_N`, `payout_viscosity_N_s_m` | Constant payout resistance and its speed dependence |
| `collision_distance_m` | Approximate centre separation at contact, where integration stops |
| `duration_s`, `sample_interval_s`, `max_step_s` | Run duration, output interval, and solver step limit |

RTN means radial outward, along track, and orbit normal. `(1, 0, 0)` starts deployment radially outward. `(0, 1, 0)` starts it along track. Pair rotation is orbital motion of the two point masses about their centre. Individual CubeSat spin requires an attitude model.

Spring energy is `0.5 * k_s * stroke**2`. With zero initial relative velocity and the spring alone, the relative release speed is `sqrt(2 * spring_energy / reduced_mass)`. Both satellites recoil. The script integrates the spring push, so this velocity is a diagnostic, not an additional initial kick.

## Material and length comparison

Edit `MATERIAL_YOUNGS_MODULUS_PA` and `TETHER_LENGTHS_M` to choose the cases. The comparison overrides `tether_youngs_modulus_Pa` and `total_tether_length_m` for each run. All other inputs stay fixed, including diameter, initial free length, damping, payout resistance, and spring energy.

The example moduli are assumptions for sensitivity studies. They are not specifications for a particular grade or finished cord. Braiding, knots, terminations, temperature, and load level affect the effective modulus. Replace the examples with measurements or data for the selected tether.

For the default 0.4 mm diameter:

| Material label | Assumed effective modulus [GPa] | Stiffness at 2 m [N/m] | Stiffness at 200 m [N/m] |
| --- | ---: | ---: | ---: |
| Nylon | 2 | 126 | 1.26 |
| Dyneema | 100 | 6,280 | 62.8 |

The code calculates area `A = pi * diameter**2 / 4`, axial rigidity `EA`, and stiffness `k(t) = EA / L(t)`. Here `L(t)` is the unstretched length outside the reel. Stiffness changes during payout and remains fixed once the reel locks. Elastic stored energy is `0.5 * k(t) * extension**2`.

The 2 m and 200 m cases have separate figures. Each material has its own row (nylon and Dyneema). The three columns are:

1. Force magnitudes, with solid tether tension, dashed gravity gradient magnitude, and dotted spring force.
2. The existing along track and radial separation trajectory, with crosses at each run's end. Set `SEPARATION_VIEW = "time"` for centre separation versus time instead.
3. Separation speed versus time, with negative values indicating rebound.

Each panel contains one material and one tether length. The force panels show blue solid tether tension, green dashed gravity gradient magnitude, and orange dotted spring force. Axis limits are shared within each column of a figure to compare materials directly. Figures for different lengths have independent scales. Time and separation axes are linear. The force magnitude axes use a symmetric logarithmic scale to show both weak and strong loads.

The time window for each figure extends to the latest run end for that length. A run ends at contact or at `duration_s`, whichever comes first. A 200 m tether may remain partly deployed if the spring energy is insufficient to overcome payout resistance.

The display cell stores the figures in `figures[2.0]` and `figures[200.0]`. `plot_comparisons_by_length(comparisons)` creates the separate grids. `plot_comparison(...)` accepts runs for a single length.

Energy and stiffness remain available through `diagnostics(run)`, even though their separate plots have been removed.

## Physics

- Each satellite experiences central Earth gravity at its own position.
- Equal and opposite spring and tether forces preserve internal momentum balance.
- The spring acts along the line of centres and permanently disengages at full extension.
- The tether pulls when stretched and becomes force free when slack.
- A reel with negligible inertia pays out when tension exceeds its resistance.
- Paid out length increases until the available tether is exhausted. The reel then locks.
- Residual kinetic energy can stretch the tether and cause rebound.
- Integration stops at the contact distance. There is no contact or impact model.

The script uses centre and relative coordinates in an inertial frame. This avoids integrating small relative displacements as the difference of two large orbit positions. Gravity gradient and the effect of pair rotation emerge from the equations. Centrifugal forces are not added separately.

Diagnostics include separation, paid out length, relative speed, spring force, tether tension, gravity gradient force magnitude, axial stiffness, elastic extension, and an energy balance. The total available tether length limits **unstretched length**. Separation can exceed it through elastic stretch.

The force comparison plots `F_gg = reduced_mass * ||g(r2) - g(r1)||`, the equivalent differential gravity force in the relative-motion equation. It uses a symmetric logarithmic scale to show small gravity gradient loads alongside spring and tether loads. This diagnostic measures inertial differential gravity. Rotating-frame centrifugal terms are excluded, and gravity is already included in the integration.

The energy residual is `mechanical_energy(t) - mechanical_energy(0) + dissipated_energy(t)`. Model losses include payout resistance, tether damping, unilateral force clipping, and energy released as the axial stiffness decreases during payout. That last term follows the simplified reel law and has rate `0.5 * k * extension**2 * L_dot / L`. Global orbital energy is large, so floating point subtraction imposes a small residual floor. Peak force is sampled. Check sensitivity to solver tolerances, `max_step_s`, and output spacing before using loads for design.

The solver also caps its step using a relative speed estimate to resolve rapid approaches to contact. The speed bound is exact with gravity disabled. Its gravity allowance is an estimate for short tether motion near the initial orbit.

## Limits and next steps

The model uses point masses and a massless tether with constant effective Young's modulus and length-dependent stiffness. It omits individual attitude, offset attachment torques, tether wrapping, coiling memory, distributed tether dynamics, reel inertia, rewind, and stop compliance. It also omits atmospheric drag, Earth oblateness, and solar pressure.

Measure spring energy, tether stiffness, damping, and payout resistance before calibrating the model. A measured resistance curve can replace the constant friction law. A detailed end stop model is needed for hardware peak load estimates. Body attitude and cable contact are needed to study the STARS-C winding scenarios.

## Sources

- [Liu et al. (2015), §4](../corpus/tethers-and-propulsion/0.1155_2015_740253.pdf): tension and slack modeling. DOI: 10.1155/2015/740253.
- [Yamagiwa et al. (2020), §6 and Appendix D](../corpus/tethers-and-propulsion/10.1016_j.actaastro.2019.12.035.pdf): resistance and rotation during STARS-C deployment. DOI: 10.1016/j.actaastro.2019.12.035.

The implemented payout law is a simplified constitutive model. This notebook is an initial engineering study, with no validation against flight data.

## Sanity checks

Doubling Young's modulus doubles stiffness. Doubling diameter quadruples stiffness. Increasing deployed length from 2 m to 200 m divides stiffness by 100. Each run's summary prints its stiffness at full payout, peak loads, deployment events, and energy residual.
