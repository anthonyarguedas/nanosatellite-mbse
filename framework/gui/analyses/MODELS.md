# Bounded report numerical models

> Historical reference. The implementations and generation commands described here have been removed.
> Replacement analyses will live in `framework/scripts/`. See the [current framework guide](../../README.md).

These four optional, registered Python analyses use the existing script picker,
input bindings, per-mode execution, result references and verification conditions.
They do not modify the UI, engine, schema, default mission, product catalog or
requirement definitions. New picker instances have **all inputs unset**. No script
supplies mission, product, reliability or safety defaults. The examples below are
**synthetic test fixtures, not recommended designs or acceptance targets**.

The current implementations are the `Sizing`, `Geometry`, `Fit` and `RAM`
`VerificationScript` subclasses in `framework/python/src/nanosat_mbse/verifications/`.
They use the Python 3.8+ standard library and declare their exact typed ports in Python.
The UI and native sessions call the same classes through the isolated runner.
The JSON blocks below describe input objects, with declared inputs bound explicitly.
`requirements` and `mode` supply no hidden defaults.
The runner retains exactly declared scalar outputs, diagnostics and any generated fault-tree representation.
Invalid types, domains, unsupported dependence or work bounds produce execution errors.
Known engineering failures return signed residuals or false.
Undefined or unavailable results are null and remain pending in the UI.
Interfaces have at most 32 inputs and 32 outputs.
No framework-conformity claim follows from these calculations or passing their software checks.

Create an unset native study from `framework/requirements-ui`:

```sh
node tools/create-report-session.mjs sizing --mission /tmp/nanosat-studies/mission.py
```

`geometry`, `fit` and `ram` select the other studies. Creation executes no analyses.
The former numerical regression sources are archived under `test/legacy/` with `.txt` suffixes.
See the [native API](../../python/README.md) for direct class execution.

## Report mapping and boundaries

| Script | Bounded numerical evidence | Explicit remaining scope |
| --- | --- | --- |
| `eps_sizing` | FR-14/20, EPS-01/02/08 and cell-area part of EPS-20. Necessary voltage screens relevant to EPS-03/04 | One identical-cell section and one battery, supplied series counts, aggregate sunlight budget. No catalog/configuration inference, cycle-life fit, charger compatibility, transient currents, full converter envelope or mission survival closure. |
| `eps_geometry` | EPS-20 oriented containment/keep-out predicates. One envelope-volume measure relevant to FR-13/EPS-19 | One component and one other box per invocation/state. Aggregate accounting, detailed solids, real mounting, connector access, deformation, harness routing and deployment require separate evidence unless represented by authored envelopes. |
| `eps_fit` | Bounded FR-22 parameter estimation and residuals | Local PV affine and battery OCV/resistance fits. Converter/thermal first-order response with known asymptote. Not general single-diode, electrochemical, coupled electrothermal or arbitrary dynamic calibration. |
| `eps_ram` | Bounded FR-27 authored fault-tree representation, minimal combinations, conditional probabilities, importance and mission reliability | Engineer determines FR-26 applicability and event/effect semantics. No automated FMEA, severity assignment, dependency discovery, arbitrary correlation, repair, dynamic sequences or full EPS reliability model. |

The report source is `final_report/requirements.tex`, `eps-requirements.tex` and
`design-proposal.tex`. Relevant equations are minimum-panel-power, solar-cell-count,
pv-integer-configuration, battery-energy, battery-assembly-capacity, retained
capacity and MPPT voltage compatibility. These are partial analysis implementations,
not complete satisfaction of any broad FR or the whole of EPS-20.

## `eps_sizing`: 32 inputs, 32 outputs

### Exact inputs

All unmarked inputs are `float`. Counts/selectors are `integer`. Flags are `boolean`.

| Inputs | Meaning and domain |
| --- | --- |
| `sun_energy_Wh`, `eclipse_energy_Wh` | Nonnegative load-side sunlight/eclipse demand, Wh, including the declared duty-cycle/consumer boundary. |
| `sunlight_s` | Positive sunlight duration, s. No orbit is inferred. |
| `sun_path_eff`, `eclipse_path_eff` | Path energy efficiencies in (0,1], each demand counted once. Eclipse energy must already be at the declared boundary used in the report's battery screen. The calculation adds no invented battery efficiency. |
| `sizing_margin` | Nonnegative fractional preliminary **battery BOL** margin M (0.2 means 20%). |
| `depth_of_discharge` | Supplied allowable fraction in (0,1]. Source it from the applicable cycling/operating conditions. No cycle-life curve is inferred. |
| `pv_cell_power_W` | Positive BOL cell power, W, at the selected attainable DET/MPPT operating point and reference conditions, not automatically the nameplate MPP. |
| `pv_operating_factor`, `pv_retained_factor` | Fractions [0,1]. Operating factor is the declared sunlight-average illumination/temperature/orientation derating at that point. Retention is lifetime degradation only. Avoid counting the same derating twice. |
| `pv_series`, `pv_parallel` | Positive integer configured counts, product <=1,000,000. Series count is fixed for proposal generation. |
| `pv_fixed` | Boolean: proposal must retain the configured arrangement, even when inadequate. |
| `pv_cell_area_m2` | Positive active cell area, m². |
| `usable_face_area_m2`, `packing_fraction` | Nonnegative usable face area, m², and packing fraction in (0,1]. No mounting area is inferred. |
| `bat_cell_energy_Wh`, `bat_cell_charge_Ah` | Positive characterized BOL per-cell energy, Wh, and charge, Ah. Energy is **not** inferred from Ah or nominal voltage. |
| `bat_series`, `bat_parallel`, `bat_fixed` | Battery configured positive integer counts (product <=1,000,000), and immutable-arrangement flag. |
| `energy_retained_factor`, `charge_retained_factor` | Separate EOL fractions fE and fQ in [0,1]. Zero retention yields zero usable capacity and a failed positive demand, not an invalid physical-domain error. |
| `required_retained_charge_Ah` | Nonnegative separately supplied retained **capacity** requirement, Ah. Include any charge-based DoD/reserve derivation explicitly upstream. It is not inferred from energy. |
| `source_low_V`, `source_high_V` | Complete assembly attainable source operating-voltage extrema, V, after declared path drops where appropriate. These are **not per-cell** inputs and do not automatically change with proposed counts. |
| `receiver_low_V`, `receiver_high_V` | Supported receiving operating/tracking input interval, V, for the chosen DET/MPPT architecture. |
| `interval_known` | Boolean: if false, the six finite voltage placeholders are ignored and voltage findings are null. If true, each source/receiver/output interval must be positive and ordered (equality allowed). |
| `conversion_kind` | Integer 0=direct/DET, 1=buck, 2=boost, 3=buck-boost. The source operating point still must be supplied for the chosen conditioning architecture. |
| `output_low_V`, `output_high_V` | Positive required/accepted output interval, V. Direct: supplied source extrema must lie inside it. Buck/boost: conservative all-combination ratio screen below. |

A purchased finished panel/pack uses its sourced **aggregate ratings as one
immutable equivalent unit** (`series=parallel=1`, `fixed=true`), not inferred
internal cell ratings. For a locked built cell assembly with known cell ratings,
`fixed=true` can instead retain its supplied internal counts. The engineer must
review which product options and auxiliary circuits the supplier supports. The
script leaves that support assessment to the engineer. Fixed products are never enlarged or silently
reconfigured. The packing screen for an aggregate panel is only a declared area
screen: its actual installation envelope still needs geometry analysis.

### Equations and exact outputs

With Es/Ee in Wh and Ts in s:

- `required_generation_W = 3600*(Es/Xs + Ee/Xe)/Ts`.
- `pv_cell_eol_W = pv_cell_power_W*pv_operating_factor*pv_retained_factor`.
- `pv_min_cells = ceil(required_generation_W/pv_cell_eol_W)`. It is null when
  positive demand meets zero cell power. Zero demand gives 0, but a physical proposed
  assembly always has at least one parallel string.
- `pv_installed_cells = pv_series*pv_parallel`. `pv_generation_bol_W` and
  `pv_generation_eol_W` multiply installed counts by the corresponding cell power.
  `generation_margin_W` is configured EOL generation minus required generation.
- `pv_proposed_series` retains the supplied series count. For nonfixed assemblies,
  `pv_proposed_parallel=max(1,ceil(pv_min_cells/pv_series))`. It is null if no finite
  solution exists or the proposal exceeds 1,000,000 total cells. Fixed proposals retain
  both configured counts regardless of adequacy. Inputs/configuration are unchanged.
- `active_area_m2 = installed_count*pv_cell_area_m2`.
  `installed_area_m2 = active_area_m2/packing_fraction`.
  `required_area_m2` is the area of the **minimum adequate** assembly rounded to
  the declared series count, divided by packing fraction. This applies even to a
  fixed product as a comparison requirement, not permission to resize it. The
  required area is null if generation is impossible. `packing_margin_m2=usable_face_area_m2*packing_fraction-active_area_m2`.
- `required_bol_energy_Wh = Ee/DoD*(1+M)`.
  `required_retained_energy_Wh = Ee/DoD`.
  `required_bol_charge_Ah = required_retained_charge_Ah/fQ` (null for positive
  requirement and zero fQ, 0 for zero requirement and zero fQ).
- `battery_energy_bol_Wh=Ns*Np*Ecell`, `battery_energy_eol_Wh=fE*E_BOL`.
  `battery_charge_bol_Ah=Np*Qcell`, `battery_charge_eol_Ah=fQ*Q_BOL`.
  Margin M is applied only once in the preliminary requirement, **never** again
  to retained energy or charge.
- `bol_energy_margin_Wh`, `retained_energy_margin_Wh`,
  `retained_charge_margin_Ah` are configured capacities minus their respective
  requirements. No DoD/SOC or reserve criterion is silently converted between Wh
  and Ah.
- `bat_installed_cells=Ns*Np`. `bat_proposed_series=Ns`. For nonfixed batteries,
  `bat_proposed_parallel` is the smallest positive integer meeting **all three**
  BOL energy, retained energy and retained charge screens at that Ns. Null if
  impossible or >1,000,000 total cells. Fixed counts remain unchanged.
- `input_voltage_margin_V=min(source_low-receiver_low, receiver_high-source_high)`.
  `conversion_margin_V`: direct = min(source_low-output_low,
  output_high-source_high). For buck, the margin is source_low-output_high. For
  boost, it is output_low-source_high. For buck-boost, it is null (conversion map
  absent).
  These are necessary interval screens, not an operating-point solver. Buck
  requires the lowest input >= highest required output. Boost requires highest
  input <= lowest output. Startup, dropout and finite ratio restrictions remain
  unknown even with nonnegative ideal margins.
- `voltage_screen_ok` is false for any known negative voltage margin, true when
  both represented screens pass, otherwise null. `interface_feasible` is false
  on a voltage violation, otherwise **always null**, because necessary current,
  absolute Voc and full conversion-envelope limits are absent.
- `sizing_ok` is true iff configured generation, packing, BOL energy, retained
  energy and retained charge margins are all nonnegative. It does not assert
  electrical compatibility, cycle life or history-based energy sufficiency.
- `proposal_within_bounds` reports whether both proposed parallel counts are
  representable within the declared count bound. A fixed inadequate proposal can
  be in bounds while `sizing_ok=false`. Required integer outputs beyond JavaScript's
  safe-integer range are an explicit representability error, not rounded counts.

Synthetic valid inputs (these supply no mission defaults):

```json
{
  "sun_energy_Wh": 4, "eclipse_energy_Wh": 2, "sunlight_s": 3600,
  "sun_path_eff": 0.8, "eclipse_path_eff": 0.5, "sizing_margin": 0.2,
  "depth_of_discharge": 0.4, "pv_cell_power_W": 2, "pv_retained_factor": 0.8,
  "pv_operating_factor": 0.75, "pv_series": 4, "pv_parallel": 2, "pv_fixed": false,
  "pv_cell_area_m2": 0.003, "usable_face_area_m2": 0.04, "packing_fraction": 0.8,
  "bat_cell_energy_Wh": 3, "bat_cell_charge_Ah": 0.8, "bat_series": 2,
  "bat_parallel": 2, "bat_fixed": false, "energy_retained_factor": 0.8,
  "charge_retained_factor": 0.8, "required_retained_charge_Ah": 1,
  "source_low_V": 12, "source_high_V": 16, "receiver_low_V": 10,
  "receiver_high_V": 20, "interval_known": true, "conversion_kind": 1,
  "output_low_V": 5, "output_high_V": 6
}
```

Reference results: required generation is 9 W and configured EOL generation is
9.6 W. The proposal is 8 PV cells in 4s2p. Active area is 0.024 m² and
installed/required area is 0.03 m². The preliminary battery BOL requirement is
6 Wh and the retained requirement is 5 Wh. Configured BOL/EOL capacities are
12/9.6 Wh and 1.6/1.28 Ah. The battery proposal is 2s2p. Full interface feasibility
is null.

Suggested scoped conditions using an instance ID `SCR001`:
`SCR001.generation_margin_W >= 0`, `SCR001.packing_margin_m2 >= 0`,
`SCR001.bol_energy_margin_Wh >= 0`, `SCR001.retained_energy_margin_Wh >= 0`,
`SCR001.retained_charge_margin_Ah >= 0`. A separate voltage-only requirement may
use `SCR001.voltage_screen_ok`. Do **not** turn null full-interface feasibility
into a pass or apply these conditions to unrepresented cycle-life/history limits.

## `eps_geometry`: 26 inputs, 26 outputs

### Exact inputs and convention

All inputs are floats except `touching_allowed` (boolean).

- `size_x_m`, `size_y_m`, `size_z_m`: positive full component box dimensions, m.
- `center_x_m`, `center_y_m`, `center_z_m`: component box centre in the installation
  frame, m. `roll_deg`, `pitch_deg`, `yaw_deg`: right-handed active local-to-frame
  rotation **Rz(yaw) Ry(pitch) Rx(roll)** about its centre, degrees.
- `install_min_x_m`, `install_min_y_m`, `install_min_z_m`, `install_max_x_m`,
  `install_max_y_m`, `install_max_z_m`: strictly ordered axis-aligned installation
  bounds in that same frame, m.
- `keep_size_x_m`, `keep_size_y_m`, `keep_size_z_m`, `keep_center_x_m`,
  `keep_center_y_m`, `keep_center_z_m`, `keep_roll_deg`, `keep_pitch_deg`,
  `keep_yaw_deg`: positive dimensions, centre and rotation of the other/keep-out
  box in the same convention.
- `tolerance_m`: supplied nonnegative contact tolerance, m. `touching_allowed`:
  whether keep-out boundary contact is allowed. Installation boundary contact is
  allowed in either case. No numerical/engineering tolerance is invented.

### Equations and exact outputs

World half-extents `e_i=sum_j abs(R_ij)*h_j` give transformed component AABB
`bound_min_x_m`, `bound_min_y_m`, `bound_min_z_m`, `bound_max_x_m`,
`bound_max_y_m`, `bound_max_z_m`. The other box has the corresponding
`keep_bound_min_x_m`, `keep_bound_min_y_m`, `keep_bound_min_z_m`,
`keep_bound_max_x_m`, `keep_bound_max_y_m`, `keep_bound_max_z_m`.

The six signed containment margins are `contain_low_x_m`, `contain_low_y_m`,
`contain_low_z_m`, `contain_high_x_m`, `contain_high_y_m`, `contain_high_z_m`.
Low margin = component minimum minus installation minimum. High margin =
installation maximum minus component maximum. `containment_margin_m` is their
minimum. `contained` means minimum >= -tolerance. `volume_m3` is the unrotated
occupied-envelope product size_x*size_y*size_z. Rotation preserves it.

For both boxes' three face axes plus nine pairwise edge cross products, normalized
nonzero axes u give `gap=abs(delta_center dot u)-rA(u)-rB(u)`.
`keepout_gap_m` is the **maximum signed projection gap**. Positive proves
separation, zero means contact, negative means overlap in exact arithmetic. This
is **not Euclidean closest distance, intersection volume or a connector clearance**.
`axes_tested` reports 6..15 evaluated nonzero axes (parallel cross axes are skipped).
Double precision near contact/parallel axes is bounded by the supplied contact
policy, not exact symbolic geometry.

`keepout_clear` means gap >= -tolerance if touching is allowed, otherwise gap >
tolerance. `overlap` is the inverse **policy outcome**, including forbidden contact,
not an independent positive-volume intersection assertion. `accommodation_ok`
means `contained and keepout_clear`. It assesses exactly the authored boxes, not
real mounting/connector access that was not included in those boxes. Run additional
instances/pairs and per-mode bindings for other components, clearance envelopes
and deployment states. Pair enumeration and orientations remain engineer-supplied.

Synthetic valid inputs:

```json
{
  "size_x_m": 2, "size_y_m": 1, "size_z_m": 1,
  "center_x_m": 0, "center_y_m": 0, "center_z_m": 0,
  "roll_deg": 0, "pitch_deg": 0, "yaw_deg": 0,
  "install_min_x_m": -3, "install_min_y_m": -3, "install_min_z_m": -3,
  "install_max_x_m": 3, "install_max_y_m": 3, "install_max_z_m": 3,
  "keep_size_x_m": 1, "keep_size_y_m": 1, "keep_size_z_m": 1,
  "keep_center_x_m": 4, "keep_center_y_m": 0, "keep_center_z_m": 0,
  "keep_roll_deg": 0, "keep_pitch_deg": 0, "keep_yaw_deg": 0,
  "touching_allowed": false, "tolerance_m": 1e-12
}
```

Reference: volume 2 m³, containment margin 2 m, signed keep-out gap 2.5 m,
`accommodation_ok=true`. A scoped condition can use `SCR001.accommodation_ok`,
or separate `SCR001.contained` and `SCR001.keepout_clear`. Retain all raw margins.
Do not use this alone as the complete EPS-20 mounting/access predicate.

## `eps_fit`: 17 inputs, 22 outputs

### Exact inputs

- `model_kind` integer: 0=local PV `I=a+b*V`, 1=battery discharge `V=E-R*I`,
  2=first-order `y=y_inf+A*exp(-t/tau)` with **known** asymptote.
- `sample_count` integer 3..5: declared prefix of sample slots.
- `valid_mask` integer: bits 1,2,4,8,16 select accepted samples within that prefix.
  Bits beyond count produce an error. At least three accepted samples are required.
  The engineer supplies the quality mask. The script applies no automatic outlier
  rejection.
- `x1`, `y1`, `x2`, `y2`, `x3`, `y3`, `x4`, `y4`, `x5`, `y5`: all finite floats,
  including ignored placeholders. Used x is nonnegative. PV: x V, y A>=0.
  Battery: x discharge A, y V>0. Exponential: x s, y consistently V or K.
- `asymptote`: finite supplied float y_inf in y units for kind 2. Affine fits
  require an ignored finite placeholder. No joint asymptote estimation is performed.
- `min_x_span`: positive float excitation threshold in x units. Used max(x)-min(x)
  must be at least this and nonzero.
- `rmse_limit`, `max_error_limit`: nonnegative float acceptance thresholds in
  **original y units**, not defaults or inferred uncertainties.

Thermal runs must use consistent physical absolute-temperature data. The engineer
must distinguish K from V and validate thermal boundary physics. The generic
y-unit interface leaves those checks to the engineer. Battery/PV fits use only the
stated local measurement law. SoC, temperature and irradiance dependence require
separate models.

### Equations and exact outputs

Least squares uses centred normalized x, equivalent to
`b=sum((x-xmean)*(y-ymean))/sum((x-xmean)^2)`, `a=ymean-b*xmean`.
For exponential data, all `y-asymptote` must be nonzero and of the same sign.
Fit `log(abs(y-asymptote))=a+b*t`, require b<0, then
`A=sign(y-asymptote)*exp(a)`, `tau=-1/b`. Invalid transformed domains and zero
or positive decay slope error (no identifiable finite positive decay constant).
This is log-domain least squares, **not** nonlinear original-domain least squares.

- `fit_intercept`, `fit_slope`: raw a,b. Affine units are y and y/x. For exponential
  fits, a is the logarithmic amplitude intercept and b is in inverse seconds. The
  log uses the numeric magnitude expressed in the declared consistent y unit.
- `pv_intercept_A`, `pv_slope_A_V`: a,b for kind 0, otherwise null. A local affine
  intercept is not a physical global short-circuit current unless its domain and
  measurements actually support that extrapolation.
- `battery_ocv_V`, `battery_resistance_ohm`: a,-b for kind 1, otherwise null.
  Extrapolated OCV is conditional on the local supplied model and data domain.
- `exp_amplitude`, `time_constant_s`: A in y units and tau in s for kind 2,
  otherwise null. A can be positive (decay) or negative (rise to asymptote).
- `residual_rmse=sqrt(mean((prediction-y)^2))`, `residual_max=max(abs(error))`
  in original y units. `transformed_rmse` is the same residual norm in the fitted
  domain (original y for affine, logarithm for exponential).
- `r_squared=1-SSE/SST` in original y, null if used y is constant. It can be
  negative for a poor exponential fit. The raw value has no hidden clipping or
  threshold.
- `used_samples`, `used_mask`, `residual_dof=used_samples-2`: integers.
- `domain_x_min`, `domain_x_max`, `domain_y_min`, `domain_y_max`: actual used
  sample extrema, in the model's x/y units, not extrapolated validity claims.
- `fit_quality_ok`: both supplied original-domain error limits hold.
  `physical_model_ok` requires PV a>=0,b<=0, battery E>0,R>=0 or a valid
  exponential decay transform, according to the selected model. Raw negative resistance/wrong PV trend is returned with false,
  not silently constrained to a physical value. `model_valid` is their conjunction:
  only these local domain/quality screens, **not empirical physical validation**.

Synthetic valid battery inputs:

```json
{
  "model_kind": 1, "sample_count": 5, "valid_mask": 31, "asymptote": 0,
  "rmse_limit": 1e-10, "max_error_limit": 1e-10, "min_x_span": 0.1,
  "x1": 0, "y1": 4.2, "x2": 1, "y2": 4.1, "x3": 2, "y3": 4,
  "x4": 3, "y4": 3.9, "x5": 4, "y5": 3.8
}
```

Reference: E=4.2 V, R=0.1 ohm, RMSE approximately zero, sample domain 0..4 A.
For a valid synthetic PV fit use the same x, kind 0, y=[1,0.9,0.8,0.7,0.6] A:
a=1 A,b=-0.1 A/V. For an exponential example use kind 2, asymptote 10 and
`y_i=10+4*exp(-(i-1)/2)` at the same x seconds: A=4,tau=2 s.

Suggested scoped conditions: `SCR001.fit_quality_ok and SCR001.physical_model_ok`
(or `SCR001.model_valid`) plus any engineer-declared parameter limits as separate
requirements. Preserve residuals and sample-domain outputs. These are not proof
of full-model calibration or accuracy outside the supplied data domain.

## `eps_ram`: 15 inputs, 30 outputs

### Exact inputs

- `value_kind` integer: 0=exposure-specific failure probabilities, 1=nonrepairable
  constant failure rates per hour. `exposure_h`: finite nonnegative float hours.
  Supplied probabilities must already apply to this exposure. This cannot be
  established from numbers alone.
- `event1_value`, `event2_value`, `event3_value`, `event4_value`: finite floats,
  probabilities in [0,1] for kind 0, nonnegative rates/h for kind 1. No fabricated
  rates, probability defaults, severity or safety target.
- `independence_confirmed`, `common_cause_resolved`: boolean declarations, both
  must be true. False is an explicitly unsupported dependence case, not implicit
  independence. A shared/common-cause effect can be a separately authored basic
  event only if residual events remain mutually independent. Otherwise use a
  different model. This script cannot establish independence from supplied data.
- `term_count` integer 1..4: an empty tree cannot pass. `term1`, `term2`, `term3`,
  `term4`: integer AND masks 1..15 for active prefix, **zero for inactive slots**.
  Bit 1=event1,2=event2,4=event3,8=event4. TOP is OR of active AND terms.
- `conditional_failed_mask`, `conditional_healthy_mask`: disjoint integers 0..15.
  Condition on all failed-mask events having failed and all healthy-mask events
  not having failed. Both 0 means unconditional probability.

**Required engineering rationale:** identify the top failure/service effect,
component revision and exact failure meaning for each bit. Identify any unused
bit. Link each probability/rate to its source and exposure/conditions. State
independence and common-cause treatment, tree applicability and declared criterion.
For the synthetic fixture below one possible mapping is A=source branch lost,
B=storage branch lost, C=converter branch lost, D=unrelated monitored failure.
TOP=(A AND B) OR (A AND C) is entirely an authored synthetic effect, not an
inferred EPS architecture. Stderr logs the indexed generated expression, authored
terms, minimal cuts and effective probabilities for that engineer-authored mapping.
The typed public protocol contains parameter snapshots, **not prose semantics**.
Names and engineering rationale remain engineer-supplied.

### Equations and exact outputs

Rates use `p_i=-expm1(-lambda_i*exposure_h)`. Duplicate terms and every strict
superset of another term are removed. Exact enumeration of all 16 independent
states uses `P(state)=product(p_i if failed else 1-p_i)`. Cuts are **not disjoint**.
Their probabilities must not be added to estimate TOP.

- `top_failure_probability=P(TOP)`. `mission_reliability=P(not TOP)` (calculated
  from non-top states to retain small reliability values near certain failure).
- `evidence_probability=P(evidence)`.
  `conditional_failure_probability=P(TOP and evidence)/P(evidence)`, null for
  zero-probability evidence.
- `minimal_cut_count` is an integer. `cut1_mask`, `cut2_mask`, `cut3_mask`,
  `cut4_mask` are sorted ascending integer minimal masks, padded null.
  `cut1_probability`, `cut2_probability`, `cut3_probability`, `cut4_probability`
  are their occurrence probabilities `product(p_i for i in cut)`, padded null. Other events are unrestricted.
- `top_given_event1`, `top_given_event2`, `top_given_event3`, `top_given_event4`:
  P(TOP|event failed), null if that event's p=0.
- `top_given_no_event1`, `top_given_no_event2`, `top_given_no_event3`,
  `top_given_no_event4`: P(TOP|event healthy), null if that event's p=1.
- `birnbaum1`, `birnbaum2`, `birnbaum3`, `birnbaum4`:
  B_i=P(TOP|do(X_i=1))-P(TOP|do(X_i=0)), evaluated by pivotal-state sums over
  the other three events. This structural derivative is well-defined even at
  p_i=0 or 1, unlike zero-probability conditional observations.
- `criticality1`, `criticality2`, `criticality3`, `criticality4`: probability
  criticality importance `p_i*B_i/P(TOP)`, null if TOP probability=0. These are
  dimensionless importance measures, **not qualitative severity or full FMECA**.
- `states_enumerated` integer, always 16. Work is constant and bounded: at most
  four terms, four events. More events/terms require another representation.

Synthetic valid inputs:

```json
{
  "value_kind": 0, "exposure_h": 100, "independence_confirmed": true,
  "common_cause_resolved": true, "term_count": 4,
  "term1": 3, "term2": 5, "term3": 7, "term4": 3,
  "event1_value": 0.1, "event2_value": 0.2,
  "event3_value": 0.3, "event4_value": 0.4,
  "conditional_failed_mask": 2, "conditional_healthy_mask": 0
}
```

Reference: minimal cuts [3,5], Q=0.1*(0.2+0.3-0.2*0.3)=0.044, reliability
0.956, cut occurrence probabilities 0.02/0.03 (sum is not Q), conditional TOP
probability given B failed=0.1. Birnbaum importance is [0.44,0.07,0.08,0] and
criticality of A=1.

Suggested criteria use **engineer-supplied** requirement thresholds, e.g.
`SCR001.top_failure_probability <= RAM001.failure_probability_limit` or
`SCR001.mission_reliability >= RAM001.reliability_min`. These names illustrate
normal existing requirement references. Thresholds remain engineer-supplied. Conditional
criteria remain pending on zero-probability evidence, not automatically passing.

## Verification coverage and numerical limits

The archived `test/legacy/report-models.test.mjs.txt` records earlier numerical coverage.
That earlier implementation loaded definitions through `loadScriptCatalog` and checked
names/counts/types and exactly declared finite outputs, creates unset picker
instances, and executes Python via the public JSON protocol and `runScripts`.
It includes independent analytic power/Wh/Ah/area calculations, fixed/inadequate
assemblies, unknown ratings, zero source, bounded proposals, transformed box
bounds/volume/contact, AABB false positives and a 3D edge-cross-edge SAT separator,
affine and positive/negative-amplitude exponential fits, masks/poor residuals/
unphysical trends/degenerate excitation, overlapping fault cuts, conditional
probabilities, rates, common-cause-as-authored-event, importance and probability
boundaries. Invalid masks, physical domains, unsupported dependence and work
limits error rather than pass. Public-runner tests preserve the workspace and
exercise separate mode bindings, with a real per-mode sizing violation.

Calculations use double-precision scalar arithmetic, no uncertainty propagation,
optimization over series counts, general geometric search or automatic engineering
assumption generation. Nonfinite results and counts outside safe-integer range
error rather than emitting NaN/Infinity or unsafe integers. Ordinary floating-point
rounding, cancellation and extreme-value underflow/saturation still limit precision.
These scripts provide no arbitrary-precision guarantee. Supplied provenance,
lifecycle applicability, empirical model validation and all unrepresented decisive
limits remain separate evidence.
