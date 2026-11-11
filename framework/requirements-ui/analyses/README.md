# Illumination and MPPT analyses

These analyses are native `Illumination` and `MPPT` subclasses of `VerificationScript` in `nanosat_mbse.verifications`. The UI's **Python scripts**, parameter and verification tables call those same classes as the REPL and require explicit execution. The generic study requirements described in [REPORT-COVERAGE.md](REPORT-COVERAGE.md) populate independently in every EPS session. Python 3.8 or later and its standard library are sufficient.

The native factory creates **Illumination + MPPT test bench** with synthetic inputs and acceptance limits. Open MPT008 in EPS and run SCR001 (MPPT). Its dependencies execute SCR002 (illumination) first. The scenario also has a scalar electrical generation check. Generic study requirements remain unverified until their own quantities and evidence are supplied. Existing sessions are unchanged. Older illumination pins require **Update definition** and the new input bindings before execution.

## Input and result audit

Generic requirements cover preliminary sizing, study obligations and the numeric illumination model. Independent mission values and acceptance limits remain unset.

| Analysis | Reusable current inputs | Missing inputs |
| --- | --- | --- |
| Illumination | `OrbitPeriod` supplies altitude and Earth constants. `ArrayAttitude`, `ArrayPanelModel` and `ArrayIllumination` supply the numeric rotation, panel and scenario inputs. | Applicable numeric values and acceptance limits. `sun_tracking` remains an explicit Boolean script input. |
| MPPT | `SolarCellPower.cell_eol_V` and `cell_eol_A` can inform reference MPP points for an explicitly declared assembly | Open circuit voltage, short circuit current, compatible reference conditions, array arrangement, temperature and irradiance scaling, environmental change, controller settings, tracking interval, conversion efficiency and acceptance limits |

The current `sunlight_efficiency` and `eclipse_efficiency` describe aggregate energy paths. They do not define a tracker algorithm or its efficiency. Cell MPP voltage and current alone determine no I-V characteristic. `installed_cells` supplies no series/parallel arrangement.

The internal limit is 256 shared display names. Script inputs and outputs have separate namespaces. The optional illumination configuration adds acceptance parameters and reuses generic numeric model inputs when there is one EPS. Existing authored bindings remain intact.

### Result destinations

| Result | Destination |
| --- | --- |
| Scenario eclipse duration | SCN001 compares `SCRnnn.longest_eclipse_s` with `eclipse_limit_s` |
| Panel direct irradiance | SCN002 compares `SCRnnn.mean_irradiance_W_m2` with `irradiance_min_W_m2` |
| Electrical generation | SCN003 compares `generated_energy_J` with `generation_min_J` and exposes `mean_generation_W` |
| Per-orbit source generation | For one EPS with one section, an unset EPS002 energy input is linked to `mean_generation_W * orbit_period_s`. Review the interval and source boundary. |
| Sunlight, penumbra, total eclipse, beta angles and incident radiant energy | Typed outputs in the existing script table, available in other expressions and methods |
| MPPT tracking interval | MPT005 checks minimum and maximum MPP voltage |
| Source voltage and current ratings | MPT006 checks maximum open circuit voltage, MPT007 checks maximum short circuit current |
| Tracking energy fraction | MPT008 checks `tracking_efficiency` |
| Reacquisition time | MPT009 checks `settled` and `settling_time_s` |
| Conditioned energy | MPT010 checks `delivered_energy_J` |
| Other MPPT diagnostics | Typed outputs in the existing script table |

IDs are assigned without collisions. The new MPPT workspace starts with MPT001 through MPT010. SCN and script IDs can differ in an existing session.

ORB002 and ORB003 retain their original preliminary circular orbit equations and verification methods. Their sunlight and eclipse quantities describe one orbit under the original geometry. The script reports totals over a user-selected interval with different geometry. These quantities are distinct. Adding a scenario preserves all original equations and acceptance conditions.

EPS002 already has an input for `sunlight_generation_J`. A compatible MPPT source energy result can be referenced there after aligning the interval, array sections and source boundary. Its average power comparison uses energy **before** downstream path conversion. MPPT `tracked_energy_J` is source energy. `delivered_energy_J` is after the declared conversion efficiency. An illumination result in J/m² is radiant energy. The separate `generated_energy_J` output applies the declared active area, electrical efficiency and retention. These constants must represent the declared operating conditions. The model infers no DET or MPPT operating point.

EPS011, EPS052 and EPS053 accept battery energy and charge evidence. These scripts propagate neither battery energy nor charge. They leave these requirements untouched and establish no battery closure, reserve or survival evidence.

## Proposed requirements

These are proposed analysis criteria. The combined test bench supplies illustrative values and limits for exercising them. The reusable blank configurations leave these inputs unset.

### Illumination

The configuration adds three Mission criteria:

- **SCN001:** Maximum longest total eclipse duration.
- **SCN002:** Minimum interval mean direct irradiance.
- **SCN003:** Minimum generated electrical energy, with scalar energy and mean power parameters.

The generic EPS requirements own numeric model inputs:

| Requirement | Parameters |
| --- | --- |
| `ArrayAttitude` (normally SIZ018) | `rotation_rate_deg_s`, axis components `rotation_axis_radial`, `rotation_axis_along`, `rotation_axis_cross`, and `initial_roll_deg`, `initial_pitch_deg`, `initial_yaw_deg` |
| `ArrayPanelModel` (normally SIZ019) | `panel_area_m2`, `panel_efficiency`, `panel_retained_factor` and the three `panel_normal_*` components |
| `ArrayIllumination` (normally SIZ020) | `inclination_deg`, `raan_deg`, `argument_latitude_deg`, `epoch_jd`, `duration_s`, `step_s`, `earth_j2`, `solar_constant_W_m2` |

The scenario factory binds these numeric inputs when there is one EPS. Multiple-EPS or mission-only studies retain manual script bindings. Differently oriented sections use separate analysis instances with their own parameters. Their compatible energy outputs can be summed explicitly. No case sweep or supplied history is required.

`sun_tracking` is a Boolean script input. The shared requirement parameter table supports numeric parameters. State this modeling choice in rationale and supply it through the typed script table.

### MPPT

The MPPT configuration implements these requirements and binds all 23 numerical script inputs to their parameter cells:

| ID | Obligation | Parameters |
| --- | --- | --- |
| MPT001 | Use declared reference I-V points and conditions. | `voc_ref_V`, `isc_ref_A`, `vmp_ref_V`, `imp_ref_A`, `reference_irradiance_W_m2`, `reference_temperature_C` |
| MPT002 | Apply declared environmental scaling. | `voltage_temp_coeff_V_C`, `current_temp_coeff_per_C`, `voltage_log_coefficient_V` |
| MPT003 | Assess a declared environmental change. | `duration_s`, `change_time_s`, initial/final irradiance and temperature |
| MPT004 | Apply declared tracker perturbations. | `sample_period_s`, `voltage_step_V`, `initial_voltage_V` |
| MPT005 | Keep source MPP voltage in the tracking interval. | `tracking_min_V`, `tracking_max_V` |
| MPT006 | Keep source open circuit voltage within its limit. | `input_absolute_max_V` |
| MPT007 | Keep source short circuit current within its permissible limit. | `source_current_limit_A` |
| MPT008 | Meet the required attainable energy capture fraction. | `tracking_efficiency_min` |
| MPT009 | Settle within the allowed time and error band. | `settling_limit_s`, `settling_relative_band`, `settling_hold_s` |
| MPT010 | Deliver the required conditioned energy. | `delivered_energy_min_J`, `conversion_efficiency` |

MPT001 through MPT004 check input domains. MPT005 through MPT010 select the MPPT script as their verification value source. All script outputs remain inspectable through these requirements. Requirement and script namespaces stay independent.

For an assembly of identical matched cells, reference section voltage is series count times cell voltage. Section current is parallel count times cell current. Use compatible Voc, Isc, Vmp and Imp conditions and declare the arrangement in rationale. Purchased section data can be entered directly. These scripts infer no arrangement from installed cell count.

## Create another named session

Run from `framework/requirements-ui/` to create another populated combined test bench:

```sh
node tools/create-analysis-session.mjs demo --name "My test bench"
```

The `demo` command creates both analyses, their input and acceptance requirements, and synthetic test values. It reads no existing mission data.

The separate blank configurations remain available:

```sh
node tools/create-analysis-session.mjs mppt --name "My MPPT study"
node tools/create-analysis-session.mjs scenario --name "My illumination study"
```

The `scenario` command copies the current mission, binds its unique `OrbitPeriod` requirement, connects generic numeric EPS model inputs when unambiguous and adds three scenario checks. It preserves the original mission. It works with blank sessions too, with all script inputs initially unset.

Use `--from <session-id>` to copy another named session. Use `--orbit <requirement-key>` when several orbit definitions exist. An ambiguous orbit gives an error. The tool never chooses one silently.

Use `--mission /path/to/mission.py` for another workspace and its neighboring session directory. A retained version-14 JSON source is also accepted and stays unchanged during conversion. `MISSION_FILE`, `VERIFICATION_SCRIPTS_DIR` and `VERIFICATION_PYTHON` are honored. The compatibility launcher calls native bench factories and the shared Python session repository, then prints the session path and URL query. It executes no analyses and rejects duplicate names. Installed equivalents use `nanosat-mbse analysis ...`.

A scenario copy needs space for any newly introduced parameter names. A full workspace gives an actionable error and leaves the source unchanged. You can still select **Orbit illumination scenario** directly in any requirement's existing Python script picker and supply script inputs and a verification condition without adding shared columns.

## Run in the existing UI

1. Reload the page and select **Illumination + MPPT test bench**.
2. Open MPT008 in EPS.
3. Click **Run Python** for SCR001 (MPPT). The illumination dependency runs first.
4. Inspect both scripts' outputs and the verification results. All inputs are already populated.
5. Change requirement parameters, script inputs or acceptance limits to try another case, save and rerun.

Mission contains ORB001 through ORB003 and SCN001 through SCN003. EPS contains MPT001 through MPT010. MPT003's two irradiance expressions reference illumination outputs. All MPPT script inputs continue to reference requirement parameters.

In a blank configuration, populate the inputs and limits before running.

Each script runs for every configured spacecraft mode. A mode expression can supply different attitudes, temperatures, irradiances or limits. Modes are independent analysis cases. They establish no chronological attitude or load schedule.

Missing inputs block execution. An invalid physical model gives an execution error. Undefined outputs remain `null`, so comparisons stay pending. Unsatisfied limits return false. Results are transient and tied to the exact inputs and source revision. Reloading requires another explicit run. If registered files change, use **Update definition** before rerunning.

## Illumination model

The native `Illumination` class evaluates a declared circular-orbit interval and one panel section with midpoint time integration.

- Radius is `earth_radius_km + altitude_km` and mean motion is `sqrt(mu_km3_s2 / radius**3)`.
- Inclination is in [0,180] degrees. RAAN and argument of latitude are angular coordinates at the start epoch. Coordinates use an approximate mean equator and equinox of date. UTC Julian dates are adequate for this preliminary model. It ignores UTC/TT differences and frame precession during the interval.
- The Sun model uses mean longitude `280.460 + 0.9856474*d` degrees, mean anomaly `357.528 + 0.9856003*d` degrees and the first two longitude harmonics about J2000 (`d = JD - 2451545`). Distance varies with the orbital anomaly. This is a low precision solar position approximation, suitable here for 1900 through 2100.
- The AU is 149,597,870.7 km (IAU 2012). The nominal solar radius is 695,700 km (IAU 2015). These model constants are explicit in the source. Mission inputs have no defaults.
- Optional secular node drift is `-1.5 * J2 * n * (R/r)**2 * cos(inclination)`. This includes only the J2 node term. It retains Keplerian argument-of-latitude rate and circular radius.
- Apparent Earth and Sun disks determine total eclipse and penumbra. Partial disk overlap uses the small-angle planar disk formula. Direct flux scales as inverse square Earth-Sun distance, visible solar fraction and positive panel incidence cosine.
- The panel normal is normalized in the body frame, whose initial reference axes coincide with local radial outward, along-orbit and orbit-normal axes. Initial active orientation is `Rz(yaw) Ry(pitch) Rx(roll)`. A Rodrigues rotation then applies `rotation_rate_deg_s * time` about the normalized `rotation_axis_*` vector, fixed in the local orbital frame.
- Zero angles and zero rate recover the former fixed local-orbital geometry. Positive rate follows the right-hand rule. This is a prescribed motion relative to the local frame and supplies no torque or attitude dynamics model.
- A Sun-tracking panel has unit incidence cosine and ignores the prescribed attitude. Its normal and spin axis can be zero when unused. Generic input-domain checks still use nonzero declared vectors.
- Electrical power is direct panel irradiance times `panel_area_m2 * panel_efficiency * panel_retained_factor`. Area is the complete active cell area of this section. Efficiency is in (0,1] and retention in [0,1]. Zero area or retention gives zero electrical generation.

`sunlight_s` includes penumbra whenever any direct solar disk is visible. `eclipse_s` counts totality only. Their sum is the declared interval. `penumbra_s` is a subset of sunlight. `longest_eclipse_s` is the longest contiguous sampled totality within that interval. Eclipse runs are clipped at the start and end boundaries. Use intervals spanning full eclipses, typically several orbits, when imposing a maximum eclipse requirement.

`mean_irradiance_W_m2` includes darkness and panel orientation across the entire interval. `min_irradiance_W_m2` can be zero even in sunlight when a fixed panel faces away from the Sun. `incident_energy_J_m2` is the integral of direct panel irradiance. Beta is the signed Sun angle above the orbit plane.

`generated_energy_J` and `generated_energy_Wh` integrate electrical generation over the entire interval. `mean_generation_W` includes darkness. `mean_sunlight_generation_W` divides energy by sunlight duration and returns zero for an all-dark interval. `min_generation_W` and `max_generation_W` are sampled extrema. All outputs are scalars. The script accepts and retains no time series.

There are at most 200,000 samples. The time step must be no greater than one orbit divided by 180 and cover at most two degrees of prescribed rotation when Sun tracking is disabled. The final step is shortened to match the interval. Eclipse edges and irradiance extrema have finite temporal resolution. Repeat with a smaller step and retain margin around thresholds. A sampled pass establishes only the specified model and interval.

The model excludes eccentricity, drag, full orbit propagation, terrain, atmospheric refraction, albedo, Earth infrared flux, spacecraft obstruction, thermal balance and attitude dynamics. Panel temperatures must come from another declared model or source. It supplies no claim that all mission epochs or scenarios have been assessed.

## MPPT model

`mppt_po.py` models an ideal sampled perturb and observe controller for one uniformly illuminated section and one environmental step.

Reference inputs must satisfy `0 < Vmp < Voc` and `0 < Imp < Isc`. They can describe EOL points when all points and coefficients have compatible EOL conditions. With `q = irradiance / reference_irradiance` and temperature change `dT`:

```text
Isc = Isc_ref * q * (1 + current_temp_coeff_per_C * dT)
Imp = Imp_ref * q * (1 + current_temp_coeff_per_C * dT)
voltage_shift = voltage_temp_coeff_V_C * dT + voltage_log_coefficient_V * log(q)
Voc = Voc_ref + voltage_shift
Vmp = Vmp_ref + voltage_shift
```

Zero irradiance gives zero source power and zero source voltage. For positive irradiance the adjusted reference points must remain valid. These scaling rules require an accepted validity domain. They are no substitute for characterized source curves.

The empirical I-V interpolation is:

```text
I(V) = Isc - (Isc - Imp) * (V/Vmp)**(Imp/(Isc-Imp))          for 0 <= V <= Vmp
I(V) = Imp * ((Voc-V)/(Voc-Vmp))**((Voc-Vmp)/Vmp)           for Vmp < V < Voc
I(V) = 0                                                 for V >= Voc
```

It passes through the three current points, has a continuous first derivative at Vmp and reaches maximum power at `(Vmp, Imp)`. It is an explicit empirical model with no diode-parameter identification.

The tracker starts with a positive voltage perturbation. It reverses direction after a measured power decrease or at a tracking bound. It retains controller state across the environmental change. Environmental changes can temporarily mislead P&O. The voltage actuator is instantaneous, without noise or converter dynamics. A passive source cannot be driven above its open circuit voltage. If Voc is below the tracking minimum, the receiver draws no current.

`duration_s` and `change_time_s` must be integer multiples of `sample_period_s`. The change lies within the interval. A change at an endpoint selects a single active phase. There are 1 through 200,000 samples. Voltage perturbation must fit within the tracking span. Conversion efficiency is a fixed factor in (0,1].

Energy outputs distinguish four boundaries:

- `available_energy_J` integrates the unconstrained source MPP.
- `attainable_energy_J` integrates the best source power inside the declared tracking interval.
- `tracked_energy_J` integrates actual controller source power.
- `delivered_energy_J` applies the declared conversion efficiency once to tracked source energy.

`tracking_efficiency` divides tracked by attainable energy. `capture_efficiency` divides tracked by unconstrained available energy. A restricted tracking window can give high tracking efficiency while losing available source energy. MPT005 checks the window independently. Neither fraction includes downstream conversion losses.

Settling uses power error relative to the unconstrained MPP. Each illuminated phase must end with a continuous in-band run lasting at least `settling_hold_s`. `settling_time_s` is the largest elapsed time to the start of that final run across active illuminated phases. A failed settling assessment returns `settled = False` and a null settling time. All-dark intervals return null MPP voltages and energy fractions, with `settled = False`. Undefined efficiency provides no passing evidence.

The voltage rating check uses Voc. The permissible source current check uses Isc. Actual operating current is also reported. The model reports violations without clipping generation to hide an exceeded rating.

The model excludes partial shading, bypass diodes, multiple peaks, converter power/current regulation, startup thresholds, losses varying with operating point, sensor noise, delay, battery charging and processor execution. It is a preliminary controller comparison. Hardware and software qualification require their own evidence.

### Synthetic test bench

The generated test bench uses a 500 km equatorial orbit starting at Julian date 2460754.5. Illumination covers two orbits with a 2 s step, a Sun-tracking panel, J2 0.00108263 and reference solar irradiance 1361 W/m².

The separate constant-efficiency generation example uses active area 0.006036 m², efficiency 0.293 and retention 1, with an 8000 J minimum interval energy. These are demonstration inputs. They are independent of the empirical MPPT section parameters.

The invented MPPT section has Voc 8 V, Isc 1.1 A, Vmp 6.4 V and Imp 1 A at 1361 W/m² and 28 °C. The MPPT run lasts 120 s with a change after 60 s. Initial irradiance references `SCR002.max_irradiance_W_m2`. Final irradiance references `SCR002.mean_irradiance_W_m2`. Temperature changes from 28 °C to 50 °C. Sampling is 0.1 s and perturbation is 0.05 V, inside a 2–8 V window, starting at 3 V.

Voltage temperature coefficient is -0.02 V/°C, relative current temperature coefficient is 0.0005/°C and logarithmic irradiance coefficient is 0.25 V. Conversion efficiency is 0.9.

The test limits are 2400 s maximum eclipse, 800 W/m² minimum mean irradiance, 9 V maximum source Voc, 1.2 A maximum source Isc, 0.95 minimum tracking efficiency and 400 J minimum delivered energy. Settling has a 15 s limit, 0.02 relative power band and 5 s hold duration.

Expected results are approximately 2140 s longest eclipse, 853.1 W/m² mean irradiance, 98.46% tracking efficiency, 540.2 J delivered energy and 6 s settling time. The archived earlier numerical checks also exercised a separate half-irradiance change and failure cases.

The illumination maximum and mean supply two constant MPPT test levels through requirement parameters. They do not replay the orbital time history. Both scripts run through the existing dependency mechanism. Execution results remain transient.

## Native and REPL examples

```sh
# From the repository root, with a new destination directory:
PYTHONPATH=framework/python/src python3 framework/python/examples/repl_demo.py \
  --prepare /tmp/nanosat-analysis-rehearsal --run
```

This computes the example through the same native classes as the UI, demonstrates stale evidence after an input change, restores the binding and saves/reopens a Python session.
See the [REPL recording recipe](../../python/docs/repl.md).
The old `analyses.test.mjs` source is preserved under `test/legacy/analyses.test.mjs.txt` as historical numerical coverage. Active `npm test` covers requirement presentation and power allocation editing. The Python tests exercise rotation, electrical generation, state mixtures, recovery and native service round trips.
