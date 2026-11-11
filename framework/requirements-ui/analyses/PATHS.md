# Declared EPS power-path, protection, battery and thermal cases

These four registered, independent Python-standard-library analyses use the existing
requirements/parameters/script protocol. They add no mission, product, safety,
interface-polarity or qualification defaults. **All examples below are synthetic
arithmetic fixtures, not recommended hardware settings or mission conditions.**
A pass is evidence only for the declared model, supplied bounds and case. It is
not a claim that a complete EPS or every applicable requirement passes.

Each script reads `{ "inputs": { ... }, "requirements": {}, "mode": null }` from
stdin and emits exactly its `.json` definition's output object. Diagnostics go
to stderr. Invalid types/domains or nonrepresentable arithmetic fail with a
nonzero exit and no stdout. All declared inputs must be present and finite with
the declared scalar type, including explicit Booleans. Unknown optional findings
are `null`, never an invented bound. Operational violations retain raw measures
and `false`. An aggregate finding is false if any included criterion is false.
Otherwise it is null if a decisive included criterion is unknown.

Names are unique within each interface (including between inputs and outputs),
at most 40 characters. Interface sizes are respectively 32/28, 32/28, 16/27 and
14/18 inputs/outputs. Numeric fields below are `float` unless explicitly marked
`integer`. Logic fields are `boolean`. Units follow names or the tables. There
are no strings, arrays or hidden dependencies. Reuse names across separate
script instances through existing qualified output references.

## Report trace and scope

| Report criterion | Evidence here | Important exclusions |
| --- | --- | --- |
| FR-16 converter/regulator response, losses, electrical limits | `eps_power_path`: steady and one simultaneous startup/pulse demand, input/output propagation and supported averaged conversion envelope | Switching dynamics, ripple and loop stability require separate evidence. Startup time is a supplied bound, not a prediction. |
| FR-16 battery voltage, charge SOC and electrothermal loss | `eps_battery_step`: analytical circuit state, extrema and resistor heat. Pass heat to `eps_thermal`. | No chemistry identification, energy-SOC equivalence, aging or temperature-dependent circuit parameters |
| FR-16 thermal behavior and protection-component stress | `eps_thermal` and `eps_protection`: declared node and rectangular-current I²t/peak stress | No spatial temperatures, arcing, inductive interruption or complete safe-operating-area curve |
| FR-19 nominal/fault/recovery, commands, shedding and processor-off cases | `eps_protection`: three-phase sampled model-in-the-loop (MIL) state machine with transitions | Flight software, hardware-in-the-loop and DET/MPPT/charge-termination behavior are outside this script. |
| EPS-03 | Power-path operating-input and startup bounds | Source open-circuit voltage, permissible source current and tracking compatibility stay in the existing PV/MPPT assessment. This script adds no redundant Voc inputs. |
| EPS-04 | Topology/duty/headroom envelope and converter input/output ratings for each declared source/rail case | Only the explicit simplified envelope below. Arbitrary sourced conversion maps require separate evidence. |
| EPS-05 | Battery charge-positive circuit step and charging-temperature finding | Chemistry, charger cell count, charge policy and termination compatibility are not assessed |
| EPS-06 | Constant-current terminal voltage including rail resistance/diode drop. Supplied startup-time comparison. | No isolation/return mapping or computed startup waveform |
| EPS-07 | One aggregated path's continuous and coincident pulse currents, upstream loss propagation, battery/converter/switch/connection limits | Separate rail instances must sum shared-source demands. Ratings must already account for temperature and pulse duration. |
| EPS-13 | Exact temperature interval for the declared state/reference node and separate charging interval | Heater electrical demand must also be supplied in chronological load/energy assessment. Junction temperature requires separate evidence. |
| EPS-14 | Supplied shunt dissipation can be evaluated thermally | No inferred curtailment/shunt capability, surplus-generation or termination control |
| EPS-15 | Nominal no-trip finding, fault interruption time, I²t and actual switched peak against supplied bounds | Threshold uncertainty and full SOA need explicitly enumerated conservative cases/separate evidence |
| EPS-16 | Inclusive UV/OV thresholds, hysteretic reset and trip/reset delays, declared output state | One protected output with externally prescribed source values. Essential/recharge paths are not independently modeled. |
| EPS-17 | Logical command/inhibit truth-table cases, processor availability, explicit fallback and autonomous authorities | Logical Booleans are already decoded assertions, not electrical levels/polarities. The actual connected truth table requires separate verification. |
| EPS-18 | Command/inhibit semantics in the declared MIL case only | No pin maps, return paths, bus protocols, rates, identifiers or electrical signal compatibility |

## 1. `eps_power_path`

### Inputs (32)

| Name(s) | Meaning/domain |
| --- | --- |
| `source_voltage_V`, `rail_voltage_V` | Positive source/battery-terminal voltage and converter output rail before distribution drop. One supplied operating point. |
| `efficiency` | In `(0,1]`. Rail-power conversion efficiency **excluding** the separate idle term. |
| `idle_power_W` | Nonnegative source-side idle consumption. Enter zero only when no separately counted idle term is applicable. |
| `steady_current_A`, `pulse_current_A` | Nonnegative aggregated constant-current demands, A. Account for coincident consumers once. |
| `pulse_replaces_steady` (**boolean**) | True: pulse amplitude replaces steady demand. False: pulse amplitude supplements steady demand |
| `pulse_duration_s` | Positive duration of the declared pulse/startup demand. Zero amplitude is allowed. |
| `path_resistance_ohm` | Nonnegative total conducting switch/contact/harness supply-and-return resistance, counted once |
| `diode_drop_V` | Nonnegative constant conducting-path drop, not also included in resistance |
| `load_min_V`, `load_max_V` | Ordered nonnegative required terminal-voltage limits |
| `input_min_V`, `input_max_V` | Ordered nonnegative converter operating-input interval |
| `startup_min_V` | Nonnegative minimum startup voltage at this source boundary |
| `dropout_V` | Nonnegative **input-side headroom subtraction** in this declared averaged envelope, not a universal converter dropout law |
| `topology_code` (**integer**) | 0 buck, 1 boost, 2 buckboost magnitude, as defined below |
| `duty_min`, `duty_max` | `0 <= min <= max <= 1`. Supplied attainable duty interval. |
| `battery_cont_A`, `battery_pulse_A` | Nonnegative source/battery discharge-current bounds for steady/pulse conditions |
| `converter_in_cont_A`, `converter_in_pulse_A` | Nonnegative converter input-current bounds |
| `converter_out_cont_A`, `converter_out_pulse_A` | Nonnegative converter output-current bounds |
| `switch_cont_A`, `switch_pulse_A` | Nonnegative rail-side switch/channel current bounds |
| `pulse_rating_duration_s` | Positive common supported duration, conservatively the minimum across all participating pulse ratings |
| `startup_time_s`, `startup_limit_s` | Nonnegative **supplied** startup-time bound and allowed service-establishment time, s |
| `connection_cont_A`, `connection_pulse_A` | Nonnegative rail-side harness/connection current bounds |

### Equations and outputs (28)

For each case, `I_s = steady_current_A`. If replacing, `I_p = pulse_current_A`.
Otherwise `I_p = steady_current_A + pulse_current_A`. Both cases are assessed,
even when pulse amplitude is lower than steady demand. For current `I`:

```
V_load = V_rail - diode_drop_V - I R_path
P_rail = V_rail I
P_terminal = V_load I
P_path_loss = I² R_path + I diode_drop_V
P_input = P_rail / efficiency + idle_power_W
I_source = P_input / V_source
P_converter_loss = P_rail (1/efficiency - 1) + idle_power_W
P_input = P_terminal + P_path_loss + P_converter_loss
```

The source current is the same current entering this single converter, not
rail-side current. This avoids using load voltage for upstream power accounting.
The constant-current algebra is deliberately retained even when voltage becomes
negative: that is failed service, not a physically sustainable load operating
point. No rail clipping or current limiting conceals the failed demand.

Let `V_eff = V_source - dropout_V`. For `V_eff > 0`, required ideal averaged duty is:

* code 0: `D = V_rail / V_eff` (buck).
* code 1: `D = 1 - V_eff / V_rail` (boost).
* code 2: `D = V_rail / (V_eff + V_rail)` (buckboost **magnitude** gain `D/(1-D)`).

Code 2 is not an assertion about polarity or every four-switch implementation.
The usage must explicitly provide a compatible positive-rail implementation or
adapter and validate this gain law. None of the codes models controller dynamics.
For a buck, this headroom model also requires `V_source >= V_rail + dropout_V`
through the unclipped duty check. For boost/buckboost, minimum operating input
and the supplied effective-input/duty interval define the declared envelope.

| Outputs | Meaning |
| --- | --- |
| `steady_input_W`, `pulse_input_W` | Source demand `P_input` |
| `steady_source_A`, `pulse_source_A` | Source/battery and converter-input current |
| `steady_rail_W`, `pulse_rail_W` | Converter-output power before distribution loss |
| `steady_load_V`, `pulse_load_V` | Raw terminal voltages |
| `steady_terminal_W`, `pulse_terminal_W` | Raw delivered terminal power |
| `steady_converter_loss_W`, `pulse_converter_loss_W` | Converter and separate idle dissipation |
| `steady_path_loss_W`, `pulse_path_loss_W` | Distribution dissipation |
| `duty_required` | Unclipped ideal duty. Null if `V_eff <= 0`, when envelope is known to fail. |
| `dropout_margin_V` | `V_eff - V_rail` for buck. `V_eff` for boost/buckboost. This is not an arbitrary converter-map residual. |
| `input_ok`, `startup_ok`, `envelope_ok`, `startup_time_ok` (**boolean**) | Operating input interval holds. Source meets startup minimum. Effective input is positive and duty lies in supplied bounds. Supplied startup bound meets allowed time. |
| `steady_voltage_ok`, `pulse_voltage_ok` (**boolean**) | Terminal voltage within the supplied load interval |
| `battery_current_ok`, `converter_current_ok`, `switch_current_ok`, `connection_current_ok` (**boolean**) | Both continuous and pulse demand fit the respective bounds (converter checks both sides) |
| `pulse_duration_ok` (**boolean**) | Pulse fits common supported duration |
| `path_ok` (**boolean**) | Conjunction of all the above findings, for this path and case only |

All interval/rating comparisons include equality. An unsupported positive source
point returns raw results/false, not a domain error. Zero/negative source voltage,
invalid efficiency, negative current/resistance, reversed bounds and unsupported
topology codes are domain errors. With zero current, the constant diode term
still defines the declared voltage-bound model. This is not a diode I-V solution.
For other source voltages, temperatures or pulse coincidences, create additional
cases. Sum shared upstream demands separately. Do not sum a board total and its
already included internal loads. This calculation has constant work.

### Synthetic input object

```json
{
  "source_voltage_V": 8, "rail_voltage_V": 5, "efficiency": 0.8, "idle_power_W": 0.1,
  "steady_current_A": 1, "pulse_current_A": 2, "pulse_replaces_steady": false, "pulse_duration_s": 0.5,
  "path_resistance_ohm": 0.1, "diode_drop_V": 0.2, "load_min_V": 4.4, "load_max_V": 5.1,
  "input_min_V": 6, "input_max_V": 10, "startup_min_V": 7, "dropout_V": 0.2, "topology_code": 0,
  "duty_min": 0.05, "duty_max": 0.95, "battery_cont_A": 1, "battery_pulse_A": 3,
  "converter_in_cont_A": 1, "converter_in_pulse_A": 3, "converter_out_cont_A": 1.2,
  "converter_out_pulse_A": 4, "switch_cont_A": 1.2, "switch_pulse_A": 4,
  "pulse_rating_duration_s": 1, "startup_time_s": 0.1, "startup_limit_s": 0.2,
  "connection_cont_A": 1.2, "connection_pulse_A": 4
}
```

Expected primary values: 6.35/18.85 W steady/pulse source demand, 4.7/4.5 V
terminal voltage, 0.79375/2.35625 A source current and `path_ok = true`.

## 2. `eps_protection`

### Inputs (32)

| Name(s) | Meaning/domain |
| --- | --- |
| `nominal_voltage_V`, `fault_voltage_V`, `recovery_voltage_V` | Nonnegative prescribed monitored source voltages, V, constant within each phase |
| `legitimate_current_A`, `fault_current_A`, `recovery_current_A` | Nonnegative **prospective** path current in each phase, A, including while disconnected |
| `nominal_duration_s`, `fault_duration_s`, `recovery_duration_s` | Nonnegative phase lengths, s. Fault duration is positive. Each positive phase is at least one whole step. |
| `step_s` | Positive timestep, s. Each phase must be an integer number of steps. |
| `uv_trip_V`, `uv_reset_V`, `ov_trip_V`, `ov_reset_V` | Nonnegative thresholds: `uv_trip <= uv_reset <= ov_reset <= ov_trip` and `uv_trip < ov_trip` |
| `oc_trip_A`, `oc_reset_A` | Nonnegative OC thresholds, with `oc_reset <= oc_trip` |
| `trip_delay_s`, `reset_delay_s` | Nonnegative consecutive-condition delays, s |
| `nominal_command_on`, `fault_command_on`, `recovery_command_on` (**boolean**) | Logical requested output enable in each phase. Phase changes implement explicit command/load shedding. |
| `nominal_inhibited`, `fault_inhibited`, `recovery_inhibited` (**boolean**) | Logical inhibit asserted in each phase, independent of electrical active-high/low polarity |
| `processor_available` (**boolean**) | Processor available throughout this scenario. Enumerate another case for unavailable processor. |
| `autonomous_protection` (**boolean**) | UV/OV/OC trips and resets remain active without processor |
| `autonomous_inhibit` (**boolean**) | Inhibit remains effective without processor |
| `processor_off_output_on` (**boolean**) | Explicit enable fallback if processor unavailable. In that case, command is ignored. |
| `auto_reset` (**boolean**) | True permits hysteretic automatic reset. False latches until the scenario ends (no hidden manual reset). |
| `i2t_limit_A2s`, `peak_limit_A`, `interruption_limit_s` | Nonnegative fault-phase stress and interruption bounds. All safety values remain supplied inputs. |

### State/timer conventions

1. The scenario begins **unlatched**. Initial output is computed from the supplied
   command/fallback and inhibit, not an assumed default polarity. The output is
   on exactly when enabled, not effectively inhibited and not latched.
2. Protection is active if the processor is available **or** autonomous protection
   is supplied. Inhibit is effective if asserted and the processor is available
   **or** autonomous inhibit is supplied. A latch dominates every command.
3. Trip condition is inclusive: `V <= uv_trip OR V >= ov_trip OR I >= oc_trip`.
   Reset requires **no trip condition** and `V >= uv_reset AND V <= ov_reset AND
   I <= oc_reset`. Thus trip wins if trip/reset thresholds coincide.
4. Input steps occur at phase boundaries. Each interval is left-closed/right-open.
   Zero delay changes the latch at the left boundary before any interval stress.
   A positive delay expires at the first right grid boundary at/after that
   continuous condition duration: `max(1, ceil(delay/step))` steps. A ratio within
   `1e-8` of an integer is treated as that integer to suppress binary roundoff.
   **Every strictly positive delay still requires at least one interval**.
   Phase alignment uses absolute ratio tolerance `1e-8`, never rounds a positive
   substep phase to zero. Timers carry across phase boundaries only if the
   condition continues, clear on a nonqualifying sample, and clear when protection
   is unavailable. Trip and reset are separate timers. No retry is invented.
5. A positive-delay trip/reset takes effect at the right boundary. New phase
   controls apply at that same boundary, without an artificial intermediate output
   glitch. The final endpoint state is reported, including a trip/reset exactly
   at the end. It contributes no additional time or energy. Output-transition
   count excludes initial state assignment. Latch trip/reset counts are separate.
6. Off-state actual switched current is zero, but **prescribed prospective current
   continues to qualify trip/reset**. This permits nonresetting persistent faults
   and explicitly excludes current-sensor-only retry behavior that would treat a
   disconnected short as cleared. Validate this assumption against the actual
   autonomous detector, or use a richer model. Voltage input is also external:
   no bus/battery feedback is inferred.
7. I²t is the exact rectangular-current integral over energized fault-phase
   intervals only, not quadrature of an unknown waveform. Peak is the largest
   switched fault-phase current (zero for instantaneous isolation). Inrush,
   residual current, detection uncertainty and interrupting energy are excluded.
8. Work is bounded at **100000 total intervals**. Larger or misaligned scenarios
   are errors, not partial simulations. Delays beyond the run cannot expire.

### Outputs (28)

| Name(s) | Meaning |
| --- | --- |
| `transition_count`, `trip_count`, `reset_count`, `nominal_trip_count` (**integer**) | Output transitions, latch trip/reset events, and trips assigned to nominal phase |
| `first_trip_time_s`, `first_reset_time_s` | Absolute scenario event times. Null if absent. |
| `fault_interruption_s` | Time after fault-phase start until first off state, including a trip exactly at fault-phase end. Zero if already off. Null if not interrupted. |
| `recovery_time_s` | Time after recovery-phase start to first on state **after observed fault-phase interruption**. Zero if on at start. Null if absent/not observed. |
| `nominal_unserved_s`, `recovery_unserved_s` | Time commanded/fallback enabled and not logically inhibited, but output off, in the respective phase |
| `fault_i2t_A2s`, `fault_peak_A` | Actual energized fault-phase I²t and peak stress |
| `inhibited_on_s` | Energized time with a logical inhibit asserted, regardless of its configured autonomy |
| `final_output_on`, `final_latched` (**boolean**) | Final endpoint output and latch states |
| `fault_seen` (**boolean**) | Fault-phase prescribed values meet a trip condition, independently of detector authority |
| `fault_interrupted`, `fault_reenergized` (**boolean**) | At least one off state observed during fault. A later on interval after that off state. |
| `nuisance_free` (**boolean**) | No nominal-phase trip and no nominal unserved time. A trip exactly at nominal end is still a no-trip failure. |
| `inhibited_outputs_off` (**boolean**) | No energized inhibited interval or final inhibited-on endpoint |
| `stress_ok` (**boolean**) | Both supplied I²t and peak limits hold |
| `interruption_ok` (**boolean**, nullable) | Fault meets supplied interruption bound. False if never interrupted. Null if fault-phase values contain no trip condition. |
| `recovery_observed` (**boolean**) | Defined recovery time was observed. This is not an assumed mandatory reset policy. |
| `protection_active` (**boolean**) | Available processor or autonomous protection. Bind this explicitly when autonomous authority is required. |
| `protection_ok` (**boolean**, nullable) | For a fault-containing phase: interruption and stress pass and no fault reenergization. Otherwise null |
| `sample_count` (**integer**) | Number of intervals actually executed |
| `fault_output_on_s`, `total_on_s` | Energized fault-phase and complete-scenario duration |

`protection_ok` does **not** include nuisance, inhibit or recovery findings and
cannot establish autonomous protection merely because a command already isolated
the fault. Bind those separate outputs to the applicable requirements. A
permanently latched reset policy intentionally yields no recovery. A requirement
that needs automatic recovery must require `recovery_observed` and compare the
returned time with its own supplied allowance. No recovery deadline is assumed.
Zero-length nominal/recovery phases provide no evidence for those omitted cases.
One nominal current step tests one legitimate workload, not all possible pulses.

### Synthetic input object

```json
{
  "nominal_voltage_V": 4, "fault_voltage_V": 2.5, "recovery_voltage_V": 4,
  "legitimate_current_A": 1, "fault_current_A": 4, "recovery_current_A": 1,
  "nominal_duration_s": 1, "fault_duration_s": 1, "recovery_duration_s": 1, "step_s": 0.1,
  "uv_trip_V": 3, "uv_reset_V": 3.5, "ov_trip_V": 5.5, "ov_reset_V": 5,
  "oc_trip_A": 2, "oc_reset_A": 1.5, "trip_delay_s": 0.2, "reset_delay_s": 0.3,
  "nominal_command_on": true, "fault_command_on": true, "recovery_command_on": true,
  "nominal_inhibited": false, "fault_inhibited": false, "recovery_inhibited": false,
  "processor_available": true, "autonomous_protection": true, "autonomous_inhibit": true,
  "processor_off_output_on": true, "auto_reset": true,
  "i2t_limit_A2s": 4, "peak_limit_A": 5, "interruption_limit_s": 0.25
}
```

Expected: trip at 1.2 s, reset at 2.3 s, interruption 0.2 s, recovery 0.3 s,
3.2 A²s, peak 4 A, 30 intervals, two output transitions, no nominal nuisance,
and `protection_ok = true` for this rectangular-current model.

## 3. `eps_battery_step`

### Inputs (16)

| Name(s) | Meaning/domain |
| --- | --- |
| `capacity_C` | Positive applicable retained charge capacity, coulombs, **not joules** |
| `initial_soc` | Supplied initial charge SOC, not energy fraction. Any finite value is evaluated without clipping, with `[0,1]` excursions reported as violations. |
| `current_A` | Constant port current **positive INTO battery** (charging). Negative current discharges. |
| `ocv_at_zero_V`, `ocv_slope_V` | Positive linear OCV intercept and nonnegative volts-per-unit-SOC slope. The model is supplied. The script infers no chemistry. |
| `r0_ohm`, `r1_ohm`, `c1_F` | Nonnegative ohmic resistance, positive polarization resistance and capacitance |
| `initial_polarization_V` | Signed initial branch voltage under the charge-positive convention |
| `duration_s` | Nonnegative interval duration, s. Zero-duration instantaneous current-step observation is supported. |
| `voltage_limits_known` (**boolean**) | Whether supplied voltage bounds support a finding |
| `voltage_min_V`, `voltage_max_V` | Ordered nonnegative terminal-voltage bounds, V |
| `soc_limits_known` (**boolean**) | Whether supplied additional scenario SOC bounds support a finding |
| `soc_min`, `soc_max` | Ordered scenario charge-SOC bounds within `[0,1]` |

Unknown limits still require typed numeric placeholders (for example both zero).
The corresponding false `*_known` flag disables all comparisons and margins.
Placeholders are not interpreted as engineering bounds. Bound ordering/domain
must nevertheless remain valid. The physical definition `0 <= SOC <= 1` is
always assessed separately. If no scenario bounds are known, that physical
finding is not promoted into a complete scenario-SOC assessment.

### Equations, extrema, energy and outputs (27)

With `I = current_A`, `Q = capacity_C`, `tau = R1 C1`, `a = I R1`,
`b = u0 - a`, and supplied OCV `O(z) = O_zero + s z`:

```
z(t) = z0 + I t / Q
u(t) = a + b exp(-t/tau)
V(t) = O(z(t)) + I R0 + u(t)
q_change = I duration
P_loss(t) = I² R0 + u(t)²/R1
E_terminal = integral I V(t) dt      [positive into battery]
E_ohmic = I² R0 duration
E_polarization_loss = [a² T + 2ab tau(1-exp(-T/tau))
                      + b² tau/2 (1-exp(-2T/tau))] / R1
Delta_E_polarization = C1 (u(T)²-u0²)/2
E_terminal = integral I O(z(t)) dt + E_ohmic + E_polarization_loss
             + Delta_E_polarization
```

Coulomb counting is ideal (unit coulombic efficiency). This is a declared circuit
model, not a separate energy-storage/cycle-life/degradation model. A normalized
energy state is never substituted for SOC. Heat is **resistor loss**, not all
terminal energy and not all polarization energy exchange. Reversible/entropic
heat, reaction heat and thermal feedback are excluded.

SOC is linear. Its extrema are endpoints. Voltage has at most one interior
stationary point: `t* = -tau log((s I/Q) tau / b)` when the logarithm's argument
is positive and `0 < t* < T`. Both endpoints and this point are evaluated. Thus
voltage limits are not merely sampled. Branch voltage is monotone. Resistor-loss
extrema use its endpoints and any zero crossing. Analytical integrals use
`expm1` and small-argument series/complete-square evaluation to avoid cancellation.

Accepted/delivered energies integrate the positive/negative parts of instantaneous
`I V(t)`, even when a failed case crosses zero terminal voltage. At most two
voltage-zero roots are bracketed by the analytic monotone subintervals and solved
with exactly 80 bisections each. All segment energies then use analytical
integrals. No user-supplied sampling workload or unbounded iteration exists.

| Name(s) | Meaning |
| --- | --- |
| `end_voltage_V`, `min_voltage_V`, `max_voltage_V` | Exact circuit endpoint and analytical interval extrema |
| `end_soc`, `min_soc`, `max_soc` | Raw charge SOC, never clipped |
| `end_polarization_V` | State to chain to a subsequent interval |
| `charge_change_C` | Signed integrated port charge |
| `terminal_energy_J` | Signed net energy accepted at the terminal |
| `accepted_energy_J`, `delivered_energy_J` | Nonnegative positive/negative terminal-energy parts. Net equals accepted minus delivered. |
| `ohmic_loss_J`, `polarization_loss_J`, `total_loss_J` | Nonnegative resistor heat, integrated exactly |
| `min_loss_W`, `max_loss_W`, `avg_loss_W` | Tight interval dissipated-power bounds and average. Average is null at zero duration. |
| `voltage_low_margin_V`, `voltage_high_margin_V` | Minimum voltage minus lower bound, upper bound minus maximum voltage. Null if voltage limits unknown. |
| `soc_low_margin`, `soc_high_margin` | Corresponding charge-SOC margins. Null if scenario SOC limits unknown. |
| `voltage_ok`, `soc_ok` (**boolean**, nullable) | Supplied voltage/scenario charge-SOC intervals hold, null if respective limits unknown |
| `physical_soc_ok` (**boolean**) | Entire charge-SOC interval lies in `[0,1]` |
| `step_ok` (**boolean**, nullable) | Three findings combined, false dominates unknown |
| `polarization_energy_change_J` | Change of branch stored energy, not resistor heat |
| `ocv_end_V` | Supplied linear OCV model evaluated at raw endpoint SOC |

Known SOC/voltage excursions are returned as failed extrapolated algebra, not
silently corrected physical trajectories. Do not propagate such a trajectory as
successful battery service. Negative resistance/capacity, invalid bound order,
negative OCV slope and nonfinite/unrepresentable numerical domains are errors.
To chain histories, bind `end_soc` to next `initial_soc` and
`end_polarization_V` to next `initial_polarization_V`. Each interval's new current
causes the corresponding instantaneous R0 voltage step. Same-model split steps
preserve state and additive energy/heat. Parameters must be characterized for
the declared SOC, temperature and lifetime case. Their physical validity outside
that characterized domain requires separate evidence.

### Synthetic input object

```json
{
  "capacity_C": 3600, "initial_soc": 0.8, "current_A": -1,
  "ocv_at_zero_V": 3, "ocv_slope_V": 1, "r0_ohm": 0.05, "r1_ohm": 0.1,
  "c1_F": 100, "initial_polarization_V": 0, "duration_s": 60,
  "voltage_limits_known": true, "voltage_min_V": 2.5, "voltage_max_V": 4.5,
  "soc_limits_known": true, "soc_min": 0.2, "soc_max": 1
}
```

Expected primary values: endpoint SOC `0.8 - 60/3600`, polarization
`-0.1 (1-exp(-6))` V, endpoint/minimum voltage approximately 3.6335812 V,
3 J ohmic loss and `step_ok = true`.

## 4. `eps_thermal`

### Inputs (14)

| Name(s) | Meaning/domain |
| --- | --- |
| `initial_temp_K`, `ambient_temp_K` | Nonnegative initial declared-node and constant boundary temperatures, K |
| `dissipation_W`, `heater_W` | Separately supplied nonnegative constant dissipated and heater heat, W |
| `heat_capacity_J_K` | Positive lumped heat capacity |
| `conductance_W_K` | Nonnegative linear thermal conductance to the boundary. Zero explicitly selects an adiabatic interval. |
| `duration_s` | Nonnegative interval duration, s |
| `temp_limits_known` (**boolean**) | State-specific component temperature bounds are known |
| `temp_min_K`, `temp_max_K` | Ordered nonnegative temperature bounds at the **same declared node/reference**, K |
| `charge_active` (**boolean**) | Charging is occurring throughout this interval, requiring the additional charging-temperature check |
| `charge_limits_known` (**boolean**) | Additional charging-temperature bounds are known |
| `charge_min_K`, `charge_max_K` | Ordered nonnegative charging-temperature bounds, K |

Use component-state bounds for the actual operating state (including separate
battery discharge restrictions). When `charge_active = false`, the charging
criterion is explicitly not applicable (`charge_ok = true`, charge margins null).
When charging is active but its bounds are unknown, its finding is null. Unknown
limits require valid typed placeholders as for the battery script, not inferred
bounds. Use Kelvin consistently. Convert Celsius before entry.

### Equations and outputs (18)

```
C dT/dt = P_dissipation + P_heater - G (T - T_ambient)
P = P_dissipation + P_heater
G > 0: tau = C/G, T_eq = T_ambient + P/G
       T(t) = T_eq + (T_initial-T_eq) exp(-t/tau)
G = 0: T(t) = T_initial + P t/C
E_generated = P duration
Delta_E_node = C (T_end-T_initial)
E_to_ambient = integral G (T(t)-T_ambient) dt
E_generated - Delta_E_node - E_to_ambient = 0  [roundoff residual retained]
```

The solution is monotone or constant, so endpoint extrema are exact. The interval
mean is integrated analytically with small-argument series where necessary.
`E_to_ambient` is signed: a warm boundary can supply heat to the node. There are
no discretization settings or size-dependent loops.

| Name(s) | Meaning |
| --- | --- |
| `end_temp_K`, `min_temp_K`, `max_temp_K`, `mean_temp_K` | Exact endpoint, interval extrema and analytical mean (initial temperature at zero duration) |
| `thermal_time_constant_s` | `C/G`, null for the explicitly adiabatic `G=0` case |
| `dissipation_energy_J`, `heater_energy_J`, `total_generated_J` | Dissipation, heater and total heat input |
| `stored_heat_change_J` | `C (T_end-T_initial)` |
| `ambient_heat_out_J` | Signed heat transferred from node to boundary |
| `energy_residual_J` | Raw generated-minus-stored-minus-out energy closure residual |
| `temp_low_margin_K`, `temp_high_margin_K` | Minimum minus lower bound, upper bound minus maximum. Null if unknown. |
| `charge_low_margin_K`, `charge_high_margin_K` | Same margins for charging, null when unknown/not applicable |
| `temp_ok`, `charge_ok` (**boolean**, nullable) | Whole interval within the respective bounds |
| `thermal_ok` (**boolean**, nullable) | Combination of state-temperature and applicable charging findings, false dominates unknown |

Bind converter/path dissipation from `eps_power_path` as the appropriate constant
heat input or use a supplied conservative maximum. Battery `avg_loss_W` is valid
as a constant-heat assumption for a declared average-heating model. It is **not**
a pointwise bound and does not reproduce the exact thermal response to varying
polarization heat. For a conservative upper-temperature bound use `max_loss_W`.
Use `min_loss_W` for a lower-temperature bound and assess the bounds together.
One average-driven run alone cannot establish all transient temperature limits.
The scripts are not a self-consistent temperature-dependent electrothermal solve.
A case, cell or junction claim requires that exact reference node and valid
C/G parameters to be declared. Spatial/junction behavior requires separate evidence.

Heater heat is separate from dissipation to prevent double counting. Count the
heater's **electrical power** separately and once in upstream/current and
chronological energy assessments, using its supplied electrical-to-heat relation.
Do not infer heater electrical consumption from a heat term without that relation.
Chain `end_temp_K` into the next interval's `initial_temp_K` for scheduled changes.

### Synthetic input object

```json
{
  "initial_temp_K": 280, "ambient_temp_K": 260, "dissipation_W": 2, "heater_W": 3,
  "heat_capacity_J_K": 100, "conductance_W_K": 0.5, "duration_s": 200,
  "temp_limits_known": true, "temp_min_K": 270, "temp_max_K": 300,
  "charge_active": true, "charge_limits_known": true, "charge_min_K": 273, "charge_max_K": 290
}
```

Expected: endpoint/minimum `270 + 10 exp(-1)` K (about 273.6787944 K), maximum
280 K, 400 J dissipation plus 600 J heater heat, `thermal_ok = true`.

## Recommended verification conditions

Run the independent protocol/arithmetic regression tests:

```sh
cd framework/requirements-ui
node --test test/report-paths.test.mjs
npm test
```

The new test file loads the registered catalog and spawns each script with `-I`
from an unrelated working directory, checks exact stdout keys/types, scalar limits,
strict input types, diagnostics and independently calculated model values. It
also exercises all three topologies, additive/replacing pulses, rating violations,
negative unserviceable rail voltage, UV/OV/OC equality, trip/reset delays including
substep positive delays, hysteresis, nuisance trips, command shedding, inhibited
states, processor-off protection/inhibit failures, nonresetting faults, endpoint
events, zero-duration battery/thermal steps, interior battery extrema, terminal
power sign changes, exact loss integrals, split-step consistency, thermal energy
balance, unknown criteria, invalid models, finite arithmetic rejection and the
100000-step MIL boundary.

For engineering use, separately enumerate source-voltage extrema and startup,
all legitimate simultaneous demand combinations and pulse durations, applicable
temperatures/lifetime ratings, threshold tolerance corners, no-trip workloads,
UV/OV/OC fault types, insufficient recovery hysteresis/duration, latched/automatic
policies, command and inhibit combinations and unavailable-processor cases.
Refine the MIL step until timing quantization is acceptable **against a supplied
engineering criterion**. Timestep/tolerance criteria remain engineer-supplied. Enumerate
required truth-table combinations explicitly, not merely one passing example.
Validate supplied battery/thermal parameters and node reference against independent
characterization, including separate charge/discharge temperature restrictions.
These scripts supply model calculations, not hardware qualification or complete
safe-operating-area evidence.
