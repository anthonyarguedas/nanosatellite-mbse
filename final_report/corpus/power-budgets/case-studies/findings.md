# Executed EPS case studies

## Scope and actual execution

These are BIRDS-derived and OreSat-derived verification configurations. They are declared engineering cases using published component/mission data and supplied assumptions. They verify calculations at stated boundaries. They establish no reproduction of complete flight performance or original published architectures.

Each mission has 18 named scenario groups. The final ledger contains 877 comparisons: 812 resolved matches, 32 expected unknowns and 33 expected errors. There are no mismatches in the final executed ledger. All nonzero numerical comparisons meet the 1% criterion separately. The maximum relative error is 0.3307393%, from a rounded BIRDS published P label. The maximum among independently calculated references is 0.000864321%. Zero references and counts, arrangements, statuses and verdicts use exact comparisons.

The 70 false resolved Requirement verdicts are expected observations. They include infeasible alternatives, invalid count domains and conservative threshold boundaries. Their false verdicts agree with the independent expectations. These are successful comparisons, not evidence that the configurations are feasible.

**Coverage qualification:** the BIRDS measured 1.575 W peak is not reconstructed. Only the unambiguous 50 and 100 mA labels are used as published curve-product benchmarks. The complete characteristics used for numerical verification are explicit three-anchor approximations from component scalars. The OreSat original sweep is retained and rejected as a complete characteristic. Do not describe all prescribed mission-publication outputs as verified. All target MOPs are exercised in both engineering cases, with this MOP-18 publication-output limitation.

No source inconsistency was corrected to force a match. No framework code was modified. No screenshots, GUI actions, commits or further subagents were used.

### Commands and files

From the evidence bundle directory (Python3.12 and NumPy2.5.4):

```sh
export EPS_FRAMEWORK_ROOT=/path/to/nanosatellite-mbse
PYTHONDONTWRITEBYTECODE=1 python3 run_case_studies.py
PYTHONDONTWRITEBYTECODE=1 python3 audit_execution.py
PYTHONDONTWRITEBYTECODE=1 python3 render_evidence.py
```

The driver also accepts `--framework-root`. Explicit selection takes priority over the environment and ancestor/cwd discovery. `README.md` and `requirements.txt` give portable setup and dependency instructions. The bundled original sweep is read relative to the driver.

The final full driver was executed again through the audit script, producing `rerun/`. A subsequent bounded profiling audit used `audit_execution.py --reuse-replay`. The six final JSON/CSV replay files are byte identical to `executed/`. `audit.json` retains their hashes. A first attempt to profile the entire interpreter exceeded the 120 s command limit and was terminated. The replacement audit observes a separate bounded public-API probe after full replay. It patches no functions. No execution-time performance claim is made.

The first development execution exposed a driver-authored binding error (`EPS.spacecraft`). The driver now references `EPS.parent` for its load aggregation. Earlier development logs remain available. Those binding errors are excluded from final numerical results and are not attributed to the framework.

- `run_case_studies.py`: actual unchanged public framework execution.
- `independent_reference.py`: independent Decimal arithmetic and Cartesian orbit references, without framework imports.
- `case_inputs.py`: explicit values and source locators.
- `sources/`: exact local copies of the original OreSat sweep, 2016 3G30A datasheet and BIRDS battery verification report. The driver reads the bundled spreadsheet.
- `executed/inputs.json`: complete baseline and variation declarations, plus all 205 original OreSat sweep rows.
- `executed/results.json`, `executed/results.csv`: all raw comparison records, actual providers, rules, statuses and traces.
- `executed/engineering-verdicts.json`: engineering findings separated from correctness comparisons.
- `executed/model-bindings.json`: actual Property expressions/units and unknowns in saved construction snapshots. Result rows retain earlier mutation expressions and evaluated measures/limits.
- `executed/summary.json`: counts, convergence and framework hashes.
- `audit.json`: deterministic artifact hashes and runtime observations.
- `case-study-evidence.tex`: compact report-facing appendix organized by requirement, with essential inputs, maximum deviations and selected reference/framework comparisons. Expected failure records, repeated outputs and the full sweep are omitted. It contains no local audit filenames, raw hashes or implementation traces.
- `case-study-evidence-full.tex`: expanded working appendix retained separately for audit.
- `reviewed-799/`: preserved earlier independent-review snapshot, including its historical37-page compiled check. That PDF is not the revised report fragment. This bounded follow-up leaves final compilation and polish to the orchestrator.

A saved-child-session metadata field is emitted only if `session.jsonl` actually exists beside the running driver. Copies without that file omit the field.


### Live implementation evidence

| Actual provider | Records |
| --- | --- |
| public Property | 554 |
| public Requirement.verify | 281 |
| direct public numerical function | 42 |


The bounded probe observed 17958 calls inside the numerical modules and 2 VerificationCondition evaluations. The runtime sizing module was `/Users/antho/nanosatellite-mbse/framework/scripts/sizing.py`. These are observed probe calls, not counts of independent test scenarios. Property and Requirement results in the full ledger are obtained through `.assess()` and `.verify()`. Direct numerical function calls are individually identified with their function names and complete keyword inputs.


### Framework revision and hashes

Revision: `f224329e05e9fd4570720967bb434e934e4184ec`. Python: `3.12.10 (v3.12.10:0cc81280367, Apr  8 2025, 08:46:59) [Clang 13.0.0 (clang-1300.0.29.30)]`. NumPy: `2.5.4`.

| File | SHA-256 |
| --- | --- |
| framework/models/__init__.py | 8c4ea3901eddeeaa2cb8cd6bb4d2c3abe9e726278876c1d0ace2d636d2e5a787 |
| framework/models/elements.py | e7babcfeb72c1755c8bc8f7554fc0259f23de560c2a65f5d0f3cdf8e7709ce39 |
| framework/models/eps.py | 5f59c73886a550314477787673186119f1abba6ad4b72e003b23ba31f89566f9 |
| framework/models/functions.py | 07266e545f793481849decf991a7967cdc46596eecd569f37d7043b6f622565b |
| framework/models/geometry.py | 88ed7bf00569fd2a1bf585aa62c246652f4c9fcfce95190370ff1550e9807c0d |
| framework/models/mission.py | 45045970d3bc2e97b5bdd2d7837775a5bfdcd6961eee8d7ed537cc2167a3be57 |
| framework/models/modes.py | 40369eadcf057c143f9ef924edbbe18a4da0c5c99a51acf61245825bd7a3354b |
| framework/models/objects.py | 213c356917aa9e0e9a09ba5f7ade8b1e2e18275843e85e9dfc17f426785dddad |
| framework/models/properties.py | dc23ef03924deba9ac15f6d5acd272619077a8aecbe2867a9312207c304a4009 |
| framework/models/recommendations.py | a61f302b1020960135043a33046d6a02c33b6fb34d2e5edfbbe398bc4350eb56 |
| framework/models/requirements.py | b3fbb49a107bb4975e2343d8b3a12e6bb575302c90e2061ef49a96938bd55393 |
| framework/models/spacecraft.py | e706147ce34d5fd5e9e89276c0f77846aeae4d2bb10786b2c4e723f7a4b07581 |
| framework/models/stakeholders.py | c8b65424d0cd540baffe5ae8bc7006c984e8c042a711406c26f4e2a1840bcd38 |
| framework/scripts/__init__.py | a05c2a3947957a30ad45dcc2c4de335b5d609aa0b4438f241ece58312797dcce |
| framework/scripts/illumination.py | 29ffa4e0f116591f755cc1370fb70acc318a14b9566d8ed3537aab2d42885a7c |
| framework/scripts/sizing.py | 8fb602449c37437b8b9a77026cb21b8cca209f9dbaf67d64a00f6b75ee143ccc |


## Comparison accounting

| Category | Records |
| --- | --- |
| exact_or_structural_value_comparisons | 302 |
| expected_errors | 33 |
| expected_unknowns | 32 |
| false_resolved_engineering_verdicts | 70 |
| numerical_value_comparisons | 510 |


## Reviewed BOL additions

Both cases execute a separate BOL characteristic under unchanged baseline mission/load/geometry. Native slots named EOL carry the explicitly selected BOL anchors in these subcases. No battery service verdict is added.

| Mission | Quantity | Unit | Independent reference | Framework actual | Outcome |
| --- | --- | --- | --- | --- | --- |
| BIRDS-4 | BOL_case_minimum_panel_power | W | 1.233912621 | 1.233906067 | match |
| BIRDS-4 | BOL_case_fractional_count | cell | 1.018511579 | 1.01850617 | match |
| BIRDS-4 | BOL_case_required_count | cell | 2 | 2 | match |
| BIRDS-4 | BOL_case_minimum_solar_parallel | string | 1 | 1 | match |
| BIRDS-4 | BOL_case_cell_power | W | 1.2114861 | 1.2114861 | match |
| BIRDS-4 | BOL_case_array_mpp | W | 2.4229722 | 2.4229722 | match |
| BIRDS-4 | BOL_case_array_voltage | V | 4.818 | 4.818 | match |
| BIRDS-4 | BOL_case_array_current | A | 0.5029 | 0.5029 | match |
| BIRDS-4 | BOL_case_array_voc | V | 5.38 | 5.38 | match |
| BIRDS-4 | BOL_case_array_isc | A | 0.5196 | 0.5196 | match |
| BIRDS-4 | BOL_case_generation_efficiency | 1 | 0.2936504601 | 0.2936504601 | match |
| BIRDS-4 | BOL_case_active_area | m2 | 0.006036 | 0.006036 | match |
| BIRDS-4 | BOL_case_panel_area | m2 | 0.007545 | 0.007545 | match |
| BIRDS-4 | BOL_case_required_area | m2 | 0.003335722134 | 0.003335704417 | match |
| BIRDS-4 | BOL_case_effective_area | m2 | 0.003073867946 | 0.00307385162 | match |
| BIRDS-4 | BOL_case_density | W/m2 | 369.9086949 | 369.9086949 | match |
| BIRDS-4 | BOL_case_available_power | W | 2.232768882 | 2.232768882 | match |
| BIRDS-4 | BOL_case_source_energy | J | 7784.452929 | 7784.492819 | match |
| BIRDS-4 | BOL_case_solar_power_verdict | verdict | true | true | match |
| BIRDS-4 | BOL_case_solar_count_verdict | verdict | true | true | match |
| BIRDS-4 | BOL_case_area_fit_verdict | verdict | true | true | match |
| BIRDS-4 | BOL_case_active_area_verdict | verdict | true | true | match |
| BIRDS-4 | BOL_case_generation_verdict | verdict | true | true | match |
| OreSat | BOL_case_minimum_panel_power | W | 0.9635935073 | 0.9635974674 | match |
| OreSat | BOL_case_fractional_count | cell | 0.8209949027 | 0.8209982767 | match |
| OreSat | BOL_case_required_count | cell | 1 | 1 | match |
| OreSat | BOL_case_minimum_solar_parallel | string | 1 | 1 | match |
| OreSat | BOL_case_cell_power | W | 1.17369 | 1.17369 | match |
| OreSat | BOL_case_array_mpp | W | 2.34738 | 2.34738 | match |
| OreSat | BOL_case_array_voltage | V | 4.86 | 4.86 | match |
| OreSat | BOL_case_array_current | A | 0.483 | 0.483 | match |
| OreSat | BOL_case_array_voc | V | 5.5 | 5.5 | match |
| OreSat | BOL_case_array_isc | A | 0.502 | 0.502 | match |
| OreSat | BOL_case_generation_efficiency | 1 | 0.3179956108 | 0.3179956108 | match |
| OreSat | BOL_case_active_area | m2 | 0.0054 | 0.0054 | match |
| OreSat | BOL_case_panel_area | m2 | 0.00675 | 0.00675 | match |
| OreSat | BOL_case_required_area | m2 | 0.002405519519 | 0.002405529405 | match |
| OreSat | BOL_case_effective_area | m2 | 0.002216686237 | 0.002216695347 | match |
| OreSat | BOL_case_density | W/m2 | 400.57605 | 400.57605 | match |
| OreSat | BOL_case_available_power | W | 2.16311067 | 2.16311067 | match |
| OreSat | BOL_case_source_energy | J | 7791.994582 | 7791.9608 | match |
| OreSat | BOL_case_solar_power_verdict | verdict | true | true | match |
| OreSat | BOL_case_solar_count_verdict | verdict | true | true | match |
| OreSat | BOL_case_area_fit_verdict | verdict | true | true | match |
| OreSat | BOL_case_active_area_verdict | verdict | true | true | match |
| OreSat | BOL_case_generation_verdict | verdict | true | true | match |


| Driver/reference file | SHA-256 |
| --- | --- |
| case_inputs.py | cc4b1150f3fa3c2e543bf62eeedea2bf2aace4bc405a28cb8a7ae1cca006e674 |
| independent_reference.py | e5139dcf6ba75acf62eab2e36e5c881e2c71e4bbcfa7f212c901fdda6307722c |
| run_case_studies.py | fc1fabcce71f8d7dce17f1d92620ea507268a560e67d9d664c62bc85ace4dce2 |


## Setup and accounting boundaries

### Representative electrical configurations

The BIRDS case uses one two-cell 3G30A section mounted on +Z of a nominal 1U bus. It does not put ten cells on one face. The OreSat case uses one two-cell XTE-SF section on the +Z end face of a nominal 2U bus. Both are unobstructed sections with supplied usable area 0.008 m2. The baseline law keeps +Z toward the Sun. This is a declared variation from the missions' original rotation conditions. Array conclusions apply to the assessed section, not a full multi-face flight array.

The load boundary includes a representative complete spacecraft demand. Every load has explicit voltage, current, on/off states and sunlight/eclipse duty fractions. Component state powers use the native V*I relation. Component power bindings use explicit StateAllocation fractions for the selected spacecraft mode. Payload power uses the native immediate-component sum. Mean phase powers are explicitly authored sums over those allocations. No chronology or allocation normalization is inferred. EPS consumption is separately set to zero and the representative whole-spacecraft load includes it. The default EPS demand sum excludes storage and generation.

The full-orbit energy equations use supplied average powers over each complete phase. Available load-boundary energies are separately allocated at 3000 J in sunlight and 1800 J in eclipse. They are not derived from the demand or claimed to be delivered by a chronological charge/discharge simulation. Source generation and bus power remain distinct boundaries.

The BIRDS battery is a 3S2P minimum-capacity NiMH estimate: 1.2 V, 1.9 Ah and 2.28 Wh per cell. The OreSat baseline retains two independent 2S1P Li-ion packs, each 18.72 Wh and 2.6 Ah, with 37.44 Wh total stored energy. The latter agrees with the rounded 37.4 Wh publication. The two independently protected real branches share the card bus, where branch currents add by Kirchhoff's current law. The 5.2 Ah sum is bookkeeping at the common nominal voltage. Current limits are evaluated per primary pack without assuming how current shares between branches. Mission 3.6 V is used for nominal energy. The manufacturer's separate 3.65 V average-energy convention is not mixed in.

The BIRDS complete EPS mass case is a supplied 0.300 kg allocation case with 0.240 kg complete battery, including a declared 0.078 kg overhead above the published 0.162 kg cells. Its 0.000121 m3 volume is supplied. The separate six-cell nominal mass benchmark remains cell-only. The OreSat mass case uses the historical 2016 modules: 0.252 kg solar and 0.416 kg battery. Adding assumed 0.035 kg conversion and 0.025 kg distribution gives 0.728 kg. Its solar volume uses eight assumed 0.10 x 0.10 x 0.003 m module envelopes, including boards and components. Together with the other supplied volumes, the EPS estimate is 0.000450 m3 against a 0.000500 m3 allocation. This mass case is not the later Tenergy/XTE electrical configuration. No historic complete EPS mass or volume is inferred.

All mass/volume allocations, receiving limits, lifetime and DoD fits, battery retentions, converter efficiencies, protection assumptions and illustrative charging selections are explicit supplied values. They are not observations of mission qualification. The baseline battery occupied envelopes and their volume allocations support separate scalar installation checks. The BIRDS electrical setup uses 69.2 cm3 for six cell envelopes plus packaging. Its standalone EPS mass case uses a separate supplied 80 cm3 battery allowance. These are two explicit volume-estimate variations, with no claimed propagation between them. The OreSat standalone mass volumes belong to the different 2016 hardware.

### Age, illumination and losses

The BIRDS EOL curve uses the 3G30A 1e15 1 MeV electrons/cm2 scalars at 28 C and AM0 1367 W/m2. Its BOL quantities use the same datasheet's BOL row. The ratio of their MPP products is applied once in the scalar efficiency comparison. Curve efficiency is calculated directly from the selected EOL anchors and receives no additional lifetime multiplier.

The OreSat XTE-SF BOL inputs are 2.43 V, 0.483 A, 2.75 V Voc, 0.502 A Isc and 0.0027 m2 at 28 C AM0. EOL current retention 0.9 at unchanged voltage is an assumption. Reference irradiance 1367 W/m2 is supplied. The silicon case uses the article's IXOLAR scalar inputs with assumed 0.9 EOL current retention and a declared illustrative common 28 C assessment. Its reference irradiance is supplied as 1362 W/m2, while both mission cases retain actual irradiance 1367 W/m2. Constant-efficiency scaling handles that explicit difference.

Each complete characteristic has anchors (0,Isc), (Vmp,Imp), (Voc,0). These are declared complete three-anchor approximations, not full measured curves. The source MPP point is retained. Linear operating-point interpolation is explicitly accepted. Irradiance and projection scale current/power under a fixed normalized shape. No voltage correction or physical curve interpolation across temperature, degradation or battery states is claimed.

Source losses are 0.95 inherent retention and 0.97 electrical assembly efficiency. Sunlight/eclipse load-path efficiencies are 0.85/0.75. Packing is geometric and remains separate. Reference MPP powers, selected operating powers, mean source powers and mean bus powers use their respective boundaries. Battery degradation margin 0.2 enters preliminary required BOL energy once. Retained energy and Ah use separate 0.8 factors without repeating that margin.

### Alternatives and checks

The silicon section has 4S10P IXOLAR packages on a supplied deployed 0.08 by 0.125 m plate. An 8 by 5 physical package layout occupies 0.064 by 0.115 m. The electrical arrangement is independent of placement. Both mission cases fail its power and receiving-voltage checks. Its panel area still passes the scalar area fit. This is an infeasible declared alternative, not a failed numerical comparison.

BIRDS compares NiMH with a supplied 1S2P Tenergy Li-ion selection. OreSat compares Li-ion with two independent 4S1P A123 LiFePO4 packs. The LiFePO4 group has 29.04 Wh, with no claim of fitting a flown card. Its 0.000184 m3 assumed occupied volume exceeds the 0.000160 m3 allocation. Its 8.0-14.4 V interval exceeds the retained receiving window 5.0-9.0 V. Unchanged chargers fail product-specific chemistry/count/voltage/termination checks. Explicit new compatible charger selections pass their supplied checks. This establishes only static compatibility with the entered conditions.

The integer arrangement variation uses a four-cell deployed coplanar array on a separate0.10x0.17m plate with0.016m2 usable allowance. A2x2 grid includes2mm inter-package gaps,3mm clearance at each edge and0.1mm upper allowance on each package dimension. BIRDS uses sourced40.15x80.15mm assembly dimensions. OreSat uses an assumed39.7x69.1mm envelope based on the manufacturer's nominal rectangular cell outline. The actual CIC/contact envelope is unvalidated. The executed maximum extents are0.0885x0.1685m for BIRDS and0.0876x0.1464m for OreSat. Both numerical layouts fit the plate and usable allowance. No mechanical qualification is inferred. BIRDS battery becomes 2S1P, and each OreSat branch becomes 3S1P. Domain tests use zero, negative, fractional and Boolean counts, plus a mismatched installed total. Native configuration Requirements reject them. Numerical integer lower bounds do not claim that a series arrangement satisfying the count automatically meets voltage or installation constraints.

Load-rail tests use BIRDS TPS63020-Q1 at 3.3 V with a 1.8-5.5 V input interval, and LTC3119 at 5 V with a 2.5-18 V interval. Their complete-circuit current limit 1 A and efficiency 0.9 are assumptions. OreSat uses TPS62111/12 at 3.3/5 V with published 3.1-17 V input and 1.5 A output, plus assumed 0.9 efficiency. Battery-terminal current includes the declared converter loss. TPS62111 fails the BIRDS pack's 3.0 V minimum. TPS63020-Q1 fails the OreSat pack's 8.4 V maximum. The SPV1040 5.2 V output ceiling fails 2S charging. These are explicit interval/setting checks, not a converter topology inference or full switching envelope.

The ideal PV converter is a separate supplied verification path with tracking/operating window 2-12 V, absolute limit 15 V, permissible source current 1.2 A and efficiency 0.9. It is not asserted to be the flown LTC3119 fixed-input controller or a qualified LT1618 circuit. In the increased-series OreSat pair, its required buck conversion is a declared unflown generic converter variation.


## Compact main-report table

| MOP | BIRDS comparisons | OreSat comparisons | Result within executed scope |
| --- | --- | --- | --- |
| MOP-12 | 21 | 21 | All expected values/statuses agree. |
| MOP-14a | 36 | 34 | All expected values/statuses agree. |
| MOP-14b | 86 | 90 | All expected values/statuses agree. |
| MOP-15 | 100 | 104 | All expected values/statuses agree. |
| MOP-16 | 65 | 67 | All expected values/statuses agree. |
| MOP-17 | 14 | 15 | All expected values/statuses agree. |
| MOP-18 | 21 | 21 | All expected values/statuses agree. BIRDS published peak remains outside reconstructed outputs. |
| MOP-19 | 59 | 56 | All expected values/statuses agree. |
| MOP-20 | 34 | 33 | All expected values/statuses agree. |


## Per-mission MOP outcome counts

| Mission | MOP | Resolved matches | Expected unknown | Expected error | Mismatch | Total |
| --- | --- | --- | --- | --- | --- | --- |
| BIRDS-4 | MOP-12 | 15 | 6 | 0 | 0 | 21 |
| BIRDS-4 | MOP-14a | 34 | 1 | 1 | 0 | 36 |
| BIRDS-4 | MOP-14b | 81 | 2 | 3 | 0 | 86 |
| BIRDS-4 | MOP-15 | 99 | 1 | 0 | 0 | 100 |
| BIRDS-4 | MOP-16 | 64 | 1 | 0 | 0 | 65 |
| BIRDS-4 | MOP-17 | 13 | 1 | 0 | 0 | 14 |
| BIRDS-4 | MOP-18 | 16 | 0 | 5 | 0 | 21 |
| BIRDS-4 | MOP-19 | 55 | 1 | 3 | 0 | 59 |
| BIRDS-4 | MOP-20 | 27 | 3 | 4 | 0 | 34 |
| OreSat | MOP-12 | 15 | 6 | 0 | 0 | 21 |
| OreSat | MOP-14a | 32 | 1 | 1 | 0 | 34 |
| OreSat | MOP-14b | 85 | 2 | 3 | 0 | 90 |
| OreSat | MOP-15 | 103 | 1 | 0 | 0 | 104 |
| OreSat | MOP-16 | 66 | 1 | 0 | 0 | 67 |
| OreSat | MOP-17 | 14 | 1 | 0 | 0 | 15 |
| OreSat | MOP-18 | 16 | 0 | 5 | 0 | 21 |
| OreSat | MOP-19 | 51 | 1 | 4 | 0 | 56 |
| OreSat | MOP-20 | 26 | 3 | 4 | 0 | 33 |


## Baseline numerical results

| Quantity | Unit | BIRDS actual | OreSat actual |
| --- | --- | --- | --- |
| Orbital period | s | 5553.452008 | 5738.81857 |
| Sunlight duration | s | 3486.474969 | 3602.201638 |
| Eclipse duration | s | 2066.97704 | 2136.616931 |
| Mean sunlight load | W | 0.6442 | 0.53 |
| Mean eclipse load | W | 0.6022 | 0.43 |
| Sunlight load energy | J | 2245.987175 | 1909.166868 |
| Eclipse load energy | J | 1244.733573 | 918.7452804 |
| Minimum panel power | W | 1.233906067 | 0.9635974674 |
| Mean available source power | W | 2.006224189 | 1.946799603 |
| Fractional solar count | cell | 1.133516829 | 0.9122203075 |
| Minimum integer solar count | cell | 2 | 1 |
| Minimum solar parallel strings | string | 1 | 1 |
| Cycle demand | cycle | 5682.519621 | 10997.94308 |
| Selected DoD | 1 | 0.3519565498 | 0.1818521868 |
| Required BOL battery energy | J | 4243.933772 | 6062.584982 |
| Minimum battery parallel strings | string | 1 | 1 |
| BOL energy per primary pack | Wh | 13.68 | 18.72 |
| BOL capacity per primary pack | Ah | 3.8 | 2.6 |
| Retained energy per primary pack | J | 39398.4 | 53913.6 |
| Retained capacity per primary pack | Ah | 3.04 | 2.08 |
| Active area | m2 | 0.006036 | 0.0054 |
| Installed panel area | m2 | 0.007545 | 0.00675 |
| Required active area | m2 | 0.003712375248 | 0.002672810451 |
| Assumed complete storage occupied volume | m3 | 6.92e-05 | 0.000112 |


## Results and discussion

Both representative Sun-pointing baseline sections pass the preliminary source-power, integer-count, active-area, panel-area, battery-energy and supplied electrical screens. BIRDS requires 1.233906 W and supplies 2.006224 W mean source power. OreSat requires 0.9635975 W and supplies 1.946800 W. Their minimum cell counts are two and one, respectively. OreSat still installs its explicit 2S pair. These values are not the missions' complete published power budgets.

The independent eccentric/nadir calculation changes the generation verdict in both missions. BIRDS mean projection is 0.456793 and available source power is 0.916429 W, below 1.254177 W required. OreSat mean projection is 0.435473 and source power is 0.847778 W, below 0.954445 W required. This confirms that passing installed-MPP/count checks alone does not establish illumination-dependent generation feasibility. The explicit eclipse-free variation has zero eclipse energy without requiring an eclipse mean power or eclipse path efficiency.

The BIRDS baseline DET operating point is 3.8 V at a 3.6 V battery plus 0.2 V drop. Its mean bus power is 1.617509 W, compared with 1.805602 W for ideal MPPT under the same curve, section, battery, illumination and source losses. Fixed regulation is assessed separately at 4.0 V. These are static illustrative calculations with accepted interpolation and supplied loss assumptions, not tracker performance measurements.

The OreSat baseline 2S array has 5.5 V Voc while DET requires 7.4 V at the 7.2 V battery plus 0.2 V drop. Operating-current evaluation correctly raises an out-of-range error. A controller receiving-window check alone can still pass for 7.4 V. It does not repair the absent source operating point. The baseline ideal-MPPT mean bus power is 1.752120 W.

The unflown OreSat 4S pair uses the same cell characteristic, battery, load and illumination for DET, ideal MPPT and fixed input regulation. DET gives 2.911227 W mean bus power, while ideal MPPT gives 3.504239 W. The increased-series BIRDS pair gives 1.640261 W DET and 3.611204 W ideal MPPT. All normal-incidence bus values include source factors 0.95*0.97 and either a 0.2 V DET drop or 0.9 conversion efficiency. No tracker startup or transient claim follows.

Protection uses separate sensed nodes. The supplied BIRDS voltage detector observes 3.9, 4.0 and 4.2 V at battery terminals, with assumed UV/OV limits 3.5/4.8 V. The regulated 5 V rail OC case uses assumed 0.2, 0.6 and 1.5 A with the published 2 A setting. Additional 3 and 4 A cases retain their own declared rail interpretation. OreSat ABLIC compares individual cells at supplied 3.0, 3.6 and 4.0 V against nominal 2.50/4.10 V thresholds. Its heater OPD separately compares 0.265, 0.314 and 0.362 A against 0.375 A, including assumed 20 mA electronics consumption. The spacecraft 30 W current calculation is at a different battery-bus node and is not assigned to that local heater breaker. Its conservative independent P/V corners are screened by a separately declared illustrative 6 A OC device. The BIRDS regulated-rail P/V corners use its 2 A OC setting.

Every declared UV, OV and OC setting is now exercised at0.99,1.00 and1.01 of its threshold. The added nine checks cover BIRDS Unreg2 at3A and Unreg1 at4A, and the assumed OreSat spacecraft battery-bus detector at6A. Each retains its distinct rail/sensing interpretation. Equality fails the implemented strict check. Empty/nonfinite samples produce errors. Missing samples/thresholds remain pending. Negative current magnitude fails its condition. No delay, hysteresis, startup, thermal PTC behavior, recovery or interruption performance is claimed. Nominal ABLIC thresholds are not a worst-case tolerance qualification.

A separate OreSat balanced charger endpoint cross-check gives8.4V/2=4.20V per cell, above the nominal4.10V OV threshold. The native no-trip Requirement returns false as independently expected. The charger remains8.4V and the original3.0/3.6/4.0V normal-sample case remains unchanged. Isolated charger criteria and normal samples pass separately, while this endpoint conflict prevents an integrated compatibility claim. It is a negative engineering result, not an implementation defect.

The maximum saved OreSat sweep product is correctly 1.6544324 W at row 197, using 4.435 V and 0.37304 A. The original 205-row sweep has 134 distinct voltages and no true short/open endpoints. It is rejected by the complete-curve contract. The largest sample is not asserted to be the true physical MPP. The distinct column B power is retained in inputs and is not substituted for the calculated column H output.

Native functions and Properties supply orbital geometry, sizing, characteristic extraction, operating-point selection, rating sums and the built-in Requirements. Mass/volume allocations, mean-load aggregation, converter input intervals, charger conditions, storage volume and bus-power loss accounting use explicitly authored ordinary Properties/Requirements. The public model has no dedicated native full charger model, buck/boost envelope solver, multi-face shared-tracker synthesis or chronological EPS simulation. These are scope limits, not hidden successful tests.

### Excluded inconsistent or inapplicable source rows

- BIRDS 2021 Table 1 prints (2184-360)*0.8=1411 mWh. Literal arithmetic gives 1459.2 mWh. It is excluded as a closed 1% reference, without changing either printed value.
- The older BIRDS HNT row prints 500 mW*0.25 h=150 mWh, while direct multiplication gives 125 mWh. It is excluded.
- The 2022 presentation's four-/three-panel diode losses differ from the IAC paper. They remain separate source revisions.
- The BIRDS safety paper's solar model identifier/area units conflict with other documents. The selected 3G30A datasheet and its 30.18 cm2 active area are explicit instead.
- BIRDS 2026 hybrid energy 3.023 Wh is not used to infer projected area, power density or an input that would reproduce that energy. The missing face map, wiring and loss boundary remain unresolved.
- BIRDS-5 masses do not fill BIRDS-4 mass gaps. OreSat 2016 mass, 2019 power/storage and 2021 independent-card data retain their separate boundaries.
- The printed BIRDS 1.575 W measured peak is not used to back-calculate an otherwise unavailable MPP current. An exact reconstructed peak comparison remains unverified.

## Independent method and convergence

Decimal arithmetic at 40-digit precision supplies scalar multiplication, sums, energy accounting, interpolation and ceiling bounds. The reference code imports only decimal, math, functools and NumPy. It imports no framework model, sizing or illumination code. Inputs come from declarations, not actual outputs.

The orbital reference uses uniformly spaced mean-anomaly/time midpoints. Newton iteration solves Kepler's equation. It calculates Cartesian position in the orbital plane, tests the night-side cylindrical shadow by the Sun dot product and perpendicular distance, and averages positive panel projection only over sunlit samples. For the selected nadir variation, +Z is radial outward and -Z points to Earth. This avoids copying the framework's general face/clocking transform, quartic shadow roots or analytic projection integral.

The fine grid has 262144 points and the convergence grid 131072. Kepler residuals are below 1e-12 rad. A two-boundary eclipse midpoint-grid error bound is 2*T/N, below 0.044 s. The largest coarse/fine eclipse relative change is 0.002050%, and the largest projection relative change is 0.0006173%. All checked minimum solar counts, solar parallel-string bounds and battery parallel-string bounds remain unchanged on the two reference grids, including both new BOL solar runs. The tested independent comparisons are far inside1%. These checks establish numerical agreement for the selected simple eclipse arcs, not universal error guarantees for every possible grazing geometry.


| Mission | Scenario | Fine eclipse s | Fine mean projection | Coarse/fine eclipse difference % | Coarse/fine projection difference % | Grid duration bound s |
| --- | --- | --- | --- | --- | --- | --- |
| BIRDS-4 | 02-states-modes-circular | 2066.994905 | 1 | 0.002049810393 | 0 | 0.04236947638 |
| BIRDS-4 | 03-eccentric-nadir | 2121.376128 | 0.4567932074 | 0.0009986318743 | 0.0006172684335 | 0.04236947638 |
| BIRDS-4 | 04-eclipse-free | 0 | 1 | 0 | 0 | 0.04236947638 |
| OreSat | 02-states-modes-circular | 2136.601314 | 1 | 0.00204922232 | 0 | 0.04378371101 |
| OreSat | 03-eccentric-nadir | 2100.151374 | 0.4354719315 | 0.001042394171 | 0.0006016498278 | 0.04378371101 |
| OreSat | 04-eclipse-free | 0 | 1 | 0 | 0 | 0.04378371101 |


## Appendix-ready complete baseline input tables

Units follow the field names and these conventions: altitude/radius in km, mu in km3/s2, angles in degrees, lifetime in years, powers in W, voltage in V, current in A, energy cell_wh in Wh, charge in Ah, area in m2, volume in m3 and all duty/retention/efficiency/packing/DoD factors as fractions. Fit law is N=a*DoD^b, with a in cycles. All uncredited quantities are A (supplied assumptions).


### BIRDS-4 baseline

| Input | Value |
| --- | --- |
| absolute_max | 15 |
| altitude | 400 |
| array.area | 0.003018 |
| array.bol_imp | 0.5029 |
| array.bol_isc | 0.5196 |
| array.bol_vmp | 2.409 |
| array.bol_voc | 2.69 |
| array.curve | true |
| array.imp | 0.4851 |
| array.isc | 0.5013 |
| array.packing | 0.8 |
| array.parallel | 1 |
| array.product | 3G30A |
| array.reference_irradiance | 1367 |
| array.retention_kind | supplied1e15fluence EOL anchors |
| array.series | 2 |
| array.source | B-Azur |
| array.technology | triple-junction GaAs |
| array.usable | 0.008 |
| array.vmp | 2.244 |
| array.voc | 2.512 |
| assembly | 0.97 |
| available_eclipse | 1800 |
| available_sunlight | 3000 |
| battery.capacity_retention | 0.8 |
| battery.cell_ah | 1.9 |
| battery.cell_volume_m3 | 8.2e-06 |
| battery.cell_wh | 2.28 |
| battery.charge_limit | 0.95 |
| battery.chemistry | NiMH |
| battery.discharge_limit | 2 |
| battery.energy_retention | 0.8 |
| battery.fit_a | 2000 |
| battery.fit_b | -1 |
| battery.fit_max | 0.8 |
| battery.fit_min | 0.1 |
| battery.independent_packs | 1 |
| battery.margin | 0.2 |
| battery.maximum | 1.45 |
| battery.minimum | 1 |
| battery.nominal | 1.2 |
| battery.packaging_volume_m3 | 2e-05 |
| battery.parallel | 2 |
| battery.product | BK-3MCC mission minimum-capacity convention |
| battery.series | 3 |
| battery.source | B-cell; maximum voltage/current limits, occupied envelopes and life inputs A |
| battery.temperature_C | 25 |
| battery_receiving_max | 5 |
| battery_receiving_min | 2.5 |
| battery_usable_volume_m3 | 0.00012 |
| beta | 30 |
| bus_tolerance | 0.05 |
| charger.allowed_max | 4.35 |
| charger.allowed_min | 3.9 |
| charger.chemistry | NiMH |
| charger.current | 0.4 |
| charger.current_limit | 1.9 |
| charger.product | supplied NiMH3S charger |
| charger.required_termination | negative_delta_V |
| charger.series | 3 |
| charger.set_voltage | 4.2 |
| charger.source | A, engineering selection. Not the flown LTC3119 charge architecture. |
| charger.termination | negative_delta_V |
| converter_current | 1 |
| converter_efficiency | 0.9 |
| converter_in_max | 18 |
| converter_in_min | 2.5 |
| converter_product | LTC3119 selected5V and TPS63020-Q1 selected3.3V (complete circuits assumed) |
| days_per_year | 365.25 |
| earth_radius | 6378 |
| eccentricity | 0 |
| eclipse_path | 0.75 |
| inherent | 0.95 |
| irradiance | 1367 |
| lifetime | 1 |
| loads.source | A. Near B-budget scalar levels, with independently supplied currents/duties. Whole spacecraft representative load boundary. |
| loads.states[0].current | 0.13 |
| loads.states[0].eclipse_duty | 1 |
| loads.states[0].name | main |
| loads.states[0].sun_duty | 1 |
| loads.states[0].voltage | 3.3 |
| loads.states[1].current | 0.044 |
| loads.states[1].eclipse_duty | 1 |
| loads.states[1].name | receiver |
| loads.states[1].sun_duty | 1 |
| loads.states[1].voltage | 3.3 |
| loads.states[2].current | 0.056 |
| loads.states[2].eclipse_duty | 0.1 |
| loads.states[2].name | beacon |
| loads.states[2].sun_duty | 0.25 |
| loads.states[2].voltage | 5 |
| mission | BIRDS-4 |
| mu | 398601 |
| pointing | sun_pointing |
| provenance | ["B-cell","B-Azur","B-orbit","B-rail","A"] |
| required_charge | 0.4 |
| required_discharge | 0.8 |
| source_current_limit | 1.2 |
| source_note | A unless source map below identifies a published rating |
| sun_angle | 0 |
| sun_path | 0.85 |
| tracker_max | 12 |
| tracker_min | 2 |
| units | 1 |


### OreSat baseline

| Input | Value |
| --- | --- |
| absolute_max | 15 |
| altitude | 550 |
| array.area | 0.0027 |
| array.bol_imp | 0.483 |
| array.bol_isc | 0.502 |
| array.bol_vmp | 2.43 |
| array.bol_voc | 2.75 |
| array.curve | true |
| array.imp | 0.4347 |
| array.isc | 0.4518 |
| array.packing | 0.8 |
| array.parallel | 1 |
| array.product | XTE-SF |
| array.reference_irradiance | 1367 |
| array.retention_kind | A .9 EOL current at constant voltage |
| array.series | 2 |
| array.source | O-solar |
| array.technology | triple-junction GaAs |
| array.usable | 0.008 |
| array.vmp | 2.43 |
| array.voc | 2.75 |
| assembly | 0.97 |
| available_eclipse | 1800 |
| available_sunlight | 3000 |
| battery.capacity_retention | 0.8 |
| battery.cell_ah | 2.6 |
| battery.cell_volume_m3 | 1.8e-05 |
| battery.cell_wh | 9.36 |
| battery.charge_limit | 1.25 |
| battery.chemistry | Li-ion |
| battery.discharge_limit | 5 |
| battery.energy_retention | 0.8 |
| battery.fit_a | 2000 |
| battery.fit_b | -1 |
| battery.fit_max | 0.8 |
| battery.fit_min | 0.1 |
| battery.independent_packs | 2 |
| battery.margin | 0.2 |
| battery.maximum | 4.2 |
| battery.minimum | 2.75 |
| battery.nominal | 3.6 |
| battery.packaging_volume_m3 | 2e-05 |
| battery.parallel | 1 |
| battery.product | Tenergy30005-0, one2S string |
| battery.series | 2 |
| battery.source | O-pack;Li-ion; occupied envelopes, fit and retentions A |
| battery.temperature_C | 25 |
| battery_receiving_max | 9 |
| battery_receiving_min | 5 |
| battery_usable_volume_m3 | 0.00016 |
| beta | 0 |
| bus_tolerance | 0.05 |
| charger.allowed_max | 8.4 |
| charger.allowed_min | 8.3 |
| charger.chemistry | Li-ion |
| charger.current | 0.4 |
| charger.current_limit | 1.25 |
| charger.product | supplied2S Li-ion charger |
| charger.required_termination | CC_CV |
| charger.series | 2 |
| charger.set_voltage | 8.4 |
| charger.source | A,25 C current setting. Not a claim of LT1618 full charger behavior. |
| charger.termination | CC_CV |
| converter_current | 1.5 |
| converter_efficiency | 0.9 |
| converter_in_max | 17 |
| converter_in_min | 3.1 |
| converter_product | TPS62111/12 |
| days_per_year | 365.25 |
| earth_radius | 6378 |
| eccentricity | 0 |
| eclipse_path | 0.75 |
| inherent | 0.95 |
| irradiance | 1367 |
| lifetime | 2 |
| loads.source | A. Complete representative whole-spacecraft demand, not the2019 full mission schedule. |
| loads.states[0].current | 0.06 |
| loads.states[0].eclipse_duty | 1 |
| loads.states[0].name | main |
| loads.states[0].sun_duty | 1 |
| loads.states[0].voltage | 3.3 |
| loads.states[1].current | 0.04 |
| loads.states[1].eclipse_duty | 1 |
| loads.states[1].name | receiver |
| loads.states[1].sun_duty | 1 |
| loads.states[1].voltage | 3.3 |
| loads.states[2].current | 0.2 |
| loads.states[2].eclipse_duty | 0.1 |
| loads.states[2].name | payload |
| loads.states[2].sun_duty | 0.2 |
| loads.states[2].voltage | 5 |
| mission | OreSat |
| mu | 398601 |
| pointing | sun_pointing |
| provenance | ["O-pack","O-solar","Li-ion","O-rail","A"] |
| required_charge | 0.4 |
| required_discharge | 0.8 |
| source_current_limit | 1.2 |
| source_note | A unless source map below identifies a published rating |
| sun_angle | 0 |
| sun_path | 0.85 |
| tracker_max | 12 |
| tracker_min | 2 |
| units | 2 |


## Complete variation inputs

Each table inherits every baseline field not listed. Mutations listed as test arrays are separate assessments, not simultaneously installed values. Ordinary bindings and the evaluated limits are retained in the raw records.


### BIRDS-4:01-mass-boundaries

| Changed or additional input | Value |
| --- | --- |
| BIRDS_pack_overhead_assumed_kg | 0.078 |
| assumed_solar_module_envelope_m | unresolved |
| mass_allocation_initial_kg | 0.35 |
| mass_allocation_variations | ["exact total",0.1] |
| masses_kg | [0.24,0.018,0.025,0.017] |
| mission | BIRDS-4 |
| solar_module_count | unresolved |
| source | B-cell; all complete EPS masses/volumes A |
| unknown | ["SolarArray.mass","SolarArray.volume"] |
| volume_allocation_m3 | 0.00015 |
| volumes_m3 | [8e-05,6e-06,2e-05,1.5e-05] |


### BIRDS-4:02-states-modes-circular

No numerical change from the complete baseline.


### BIRDS-4:03-eccentric-nadir

| Changed or additional input | Value |
| --- | --- |
| beta | 25 |
| eccentricity | 0.02 |
| pointing | nadir |
| sun_angle | 47 |


### BIRDS-4:04-eclipse-free

| Changed or additional input | Value |
| --- | --- |
| beta | 90 |


### BIRDS-4:05-baseline-sizing

No numerical change from the complete baseline.


### BIRDS-4:05-baseline-sizing:BOL

| Changed or additional input | Value |
| --- | --- |
| array.imp | 0.5029 |
| array.isc | 0.5196 |
| array.retention_kind | BOL anchors, no solar lifetime reduction |
| array.vmp | 2.409 |
| array.voc | 2.69 |
| solar_age | BOL |


### BIRDS-4:06-silicon-technology

| Changed or additional input | Value |
| --- | --- |
| array.area | 9.17e-05 |
| array.bol_imp | 0.006 |
| array.bol_isc | 0.0063 |
| array.bol_vmp | 4.46 |
| array.bol_voc | 5.53 |
| array.imp | 0.0054 |
| array.isc | 0.00567 |
| array.packing | 0.4983695652 |
| array.parallel | 10 |
| array.product | IXOLAR SSM |
| array.reference_irradiance | 1362 |
| array.retention_kind | A .9 EOL current at constant voltage |
| array.series | 4 |
| array.source | Si; A40 packages on deployed .08x.125m plate. Layout8x5 uses.064x.115m. Electrical4S10P is supplied independently of physical placement. Scalar area check establishes no mechanical qualification. |
| array.technology | monocrystalline silicon |
| array.temperature_C | 28 |
| array.usable | 0.01 |
| array.vmp | 4.46 |
| array.voc | 5.53 |


### BIRDS-4:07-battery-chemistry:incompatible

| Changed or additional input | Value |
| --- | --- |
| battery.cell_ah | 2.6 |
| battery.cell_volume_m3 | 1.8e-05 |
| battery.cell_wh | 9.36 |
| battery.charge_limit | 1.25 |
| battery.chemistry | Li-ion |
| battery.discharge_limit | 5 |
| battery.maximum | 4.2 |
| battery.minimum | 2.75 |
| battery.nominal | 3.6 |
| battery.product | Tenergy30005-0 |
| battery.series | 1 |
| battery.source | Li-ion; A occupied envelopes, fit and retentions |
| charger.allowed_max | 4.2 |
| charger.allowed_min | 4.1 |
| charger.required_termination | CC_CV |


### BIRDS-4:07-battery-chemistry:selected-new-charger

| Changed or additional input | Value |
| --- | --- |
| battery.cell_ah | 2.6 |
| battery.cell_volume_m3 | 1.8e-05 |
| battery.cell_wh | 9.36 |
| battery.charge_limit | 1.25 |
| battery.chemistry | Li-ion |
| battery.discharge_limit | 5 |
| battery.maximum | 4.2 |
| battery.minimum | 2.75 |
| battery.nominal | 3.6 |
| battery.product | Tenergy30005-0 |
| battery.series | 1 |
| battery.source | Li-ion; A occupied envelopes, fit and retentions |
| charger.allowed_max | 4.2 |
| charger.allowed_min | 4.1 |
| charger.chemistry | Li-ion |
| charger.current_limit | 2.5 |
| charger.required_termination | CC_CV |
| charger.series | 1 |
| charger.termination | CC_CV |


### BIRDS-4:08-integer-configurations

| Changed or additional input | Value |
| --- | --- |
| additional_mutations.Battery.parallel_count | [0,-1,2.5,true] |
| additional_mutations.SolarArray.cell_count | 99 |
| additional_mutations.SolarArray.series_count | [0,-1,2.5,true] |
| array.series | 4 |
| array.usable | 0.016 |
| battery.parallel | 1 |
| battery.series | 2 |
| deployment.columns | 2 |
| deployment.edge_clearance_m | 0.003 |
| deployment.gap_m | 0.002 |
| deployment.package_dimension_tolerance_m | 0.0001 |
| deployment.package_length_m | 0.08015 |
| deployment.package_width_m | 0.04015 |
| deployment.plate_length_m | 0.17 |
| deployment.plate_width_m | 0.1 |
| deployment.rows | 2 |
| deployment.source | B-Azur nominal assembly dimensions40.15x80.15mm with source +/-0.1mm tolerance. Plate,2x2 arrangement,gaps and edge clearances are A. |
| deployment.usable_area_m2 | 0.016 |


### BIRDS-4:09-converter-rails

| Changed or additional input | Value |
| --- | --- |
| alternative_converter_interval_V | [3.1,17.0] |
| alternative_converter_product | TPS62111 (3S NiMH lower bound3.0V fails3.1V) |
| alternative_current_A | 1.1 |
| alternative_output_V | 5.06 |
| rail_cases[0].A | 0.5 |
| rail_cases[0].V | 3.3 |
| rail_cases[1].A | 0.4 |
| rail_cases[1].V | 5 |
| selected_3p3V_product | TPS63020-Q1 input1.8-5.5V |
| selected_5V_product | LTC3119 input2.5-18V |
| unknown | converter.efficiency |
| voltage_tolerance | 0.05 |


### BIRDS-4:10-characteristics

| Changed or additional input | Value |
| --- | --- |
| invalid_curves | [["partial",[[2.244,0.4851],[2.512,0.0]]],["duplicate_voltage",[[0.0,0.5],[1.0,0.4],[1.0,0.3],[2.0,0.0]]],["negative_current",[[0.0,0.5],[1.0,-0.1],[2.0,0.0]]],["nonfinite",[[0.0,0.5],[1.0,"nan"],[2.0,0.0]]]] |
| purchased_panel_variation | 2cell module curve voltage x2, active area x2, external1S1P |
| source_curve_limit | Three-anchor approximation, not complete measured curve. |


### BIRDS-4:11-baseline-DET:DET

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| bus_nominal_V | 3.6 |
| common_bus_demand_W | 0.5 |
| fixed_setpoint_V | unresolved |
| method | DET |


### BIRDS-4:12-baseline-ideal-MPPT:MPPT

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| bus_nominal_V | 3.6 |
| common_bus_demand_W | 0.5 |
| fixed_setpoint_V | unresolved |
| method | MPPT |


### BIRDS-4:13-baseline-fixed-voltage:FIXED_VOLTAGE

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| bus_nominal_V | 3.6 |
| common_bus_demand_W | 0.5 |
| fixed_setpoint_V | 4 |
| method | FIXED_VOLTAGE |


### BIRDS-4:14-unflown-4S-pair:DET

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| array.series | 4 |
| array.usable | 0.016 |
| bus_nominal_V | 3.6 |
| common_bus_demand_W | 0.5 |
| deployment.columns | 2 |
| deployment.edge_clearance_m | 0.003 |
| deployment.gap_m | 0.002 |
| deployment.package_dimension_tolerance_m | 0.0001 |
| deployment.package_length_m | 0.08015 |
| deployment.package_width_m | 0.04015 |
| deployment.plate_length_m | 0.17 |
| deployment.plate_width_m | 0.1 |
| deployment.rows | 2 |
| deployment.source | B-Azur nominal assembly dimensions40.15x80.15mm with source +/-0.1mm tolerance. Plate,2x2 arrangement,gaps and edge clearances are A. |
| deployment.usable_area_m2 | 0.016 |
| fixed_setpoint_V | 8 |
| method | DET |


### BIRDS-4:14-unflown-4S-pair:FIXED_VOLTAGE

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| array.series | 4 |
| array.usable | 0.016 |
| bus_nominal_V | 3.6 |
| common_bus_demand_W | 0.5 |
| deployment.columns | 2 |
| deployment.edge_clearance_m | 0.003 |
| deployment.gap_m | 0.002 |
| deployment.package_dimension_tolerance_m | 0.0001 |
| deployment.package_length_m | 0.08015 |
| deployment.package_width_m | 0.04015 |
| deployment.plate_length_m | 0.17 |
| deployment.plate_width_m | 0.1 |
| deployment.rows | 2 |
| deployment.source | B-Azur nominal assembly dimensions40.15x80.15mm with source +/-0.1mm tolerance. Plate,2x2 arrangement,gaps and edge clearances are A. |
| deployment.usable_area_m2 | 0.016 |
| fixed_setpoint_V | 8 |
| method | FIXED_VOLTAGE |


### BIRDS-4:14-unflown-4S-pair:MPPT

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| array.series | 4 |
| array.usable | 0.016 |
| bus_nominal_V | 3.6 |
| common_bus_demand_W | 0.5 |
| deployment.columns | 2 |
| deployment.edge_clearance_m | 0.003 |
| deployment.gap_m | 0.002 |
| deployment.package_dimension_tolerance_m | 0.0001 |
| deployment.package_length_m | 0.08015 |
| deployment.package_width_m | 0.04015 |
| deployment.plate_length_m | 0.17 |
| deployment.plate_width_m | 0.1 |
| deployment.rows | 2 |
| deployment.source | B-Azur nominal assembly dimensions40.15x80.15mm with source +/-0.1mm tolerance. Plate,2x2 arrangement,gaps and edge clearances are A. |
| deployment.usable_area_m2 | 0.016 |
| fixed_setpoint_V | 8 |
| method | MPPT |


### BIRDS-4:15-operating-point-contract

| Changed or additional input | Value |
| --- | --- |
| interpolation_cases | ["none","linear"] |
| sampling_voltages_V | [4.488,3.5904000000000007,5.034] |
| selectors | ["WRONG",null] |


### BIRDS-4:16-normal-extrema

| Changed or additional input | Value |
| --- | --- |
| OC_A | 2 |
| OV_V | 4.8 |
| UV_V | 3.5 |
| charger_endpoint_cross_check | unresolved |
| independent_corner_OC_A | 2 |
| independent_corner_OC_source | BIRDS2A regulatedrail setting. OreSat6A supplied separate spacecraft-bus OC device, no PTC behavior claim. |
| independent_corner_powers_W | [1.0,3.0,7.5] |
| independent_corner_voltage_V | [4.75,5.25] |
| mission | BIRDS-4 |
| sensed_rail_current_A | [0.2,0.6,1.5] |
| sensed_voltages_V | [3.9,4.0,4.2] |
| source | A battery-node UV3.5OV4.8; battery samples from Tsuru observations. OC2A at distinct5Vregulatedrail, rail currents/powers A. Additional3/4A railthresholds sourceB-rail. |


### BIRDS-4:17-threshold-boundaries

| Changed or additional input | Value |
| --- | --- |
| OC_A | 2 |
| OV_V | 4.8 |
| UV_V | 3.5 |
| additional_OC_scope | BIRDS Unreg2 and Unreg1 are distinct unregulated rail detectors. OreSat6A is a supplied spacecraft battery-bus detector, separate from local heater OC and ABLIC cell sensing. |
| additional_OC_settings[0].rail | Unreg2 |
| additional_OC_settings[0].threshold_A | 3 |
| additional_OC_settings[1].rail | Unreg1 |
| additional_OC_settings[1].threshold_A | 4 |
| factors | [0.99,1.0,1.01] |
| invalid_current | [[-0.01],[],null] |
| invalid_voltages | [null,[],["nan"]] |
| mission | BIRDS-4 |
| unknown_OC_threshold | true |


### BIRDS-4:18-unknown-invalid-feasibility

| Changed or additional input | Value |
| --- | --- |
| inadequate_sunlight_delivery_J | 1 |
| invalid_cycles | 30000 |
| invalid_orbit.R | 6378 |
| invalid_orbit.a | 6500 |
| invalid_orbit.e | 0.2 |
| invalid_packing | 0 |
| invalid_retention | 1.1 |
| unknown | ["SolarArray.series_count","SolarArray.usable_area","Battery.cycle_coefficient","Battery.energy_retention","orbit.altitude"] |


### OreSat:01-mass-boundaries

| Changed or additional input | Value |
| --- | --- |
| BIRDS_pack_overhead_assumed_kg | unresolved |
| assumed_solar_module_envelope_m | [0.1,0.1,0.003] |
| mass_allocation_initial_kg | 0.8 |
| mass_allocation_variations | ["exact total",0.1] |
| masses_kg | [0.416,0.252,0.035,0.025] |
| mission | OreSat |
| solar_module_count | 8 |
| source | O-mass historical2016; all volumes and converter/distribution masses A |
| unknown | ["SolarArray.mass","SolarArray.volume"] |
| volume_allocation_m3 | 0.0005 |
| volumes_m3 | [0.00016,0.00024,3e-05,2e-05] |


### OreSat:02-states-modes-circular

No numerical change from the complete baseline.


### OreSat:03-eccentric-nadir

| Changed or additional input | Value |
| --- | --- |
| beta | 25 |
| eccentricity | 0.04 |
| pointing | nadir |
| sun_angle | 47 |


### OreSat:04-eclipse-free

| Changed or additional input | Value |
| --- | --- |
| beta | 90 |


### OreSat:05-baseline-sizing

No numerical change from the complete baseline.


### OreSat:05-baseline-sizing:BOL

| Changed or additional input | Value |
| --- | --- |
| array.imp | 0.483 |
| array.isc | 0.502 |
| array.retention_kind | BOL anchors, no solar lifetime reduction |
| solar_age | BOL |


### OreSat:06-silicon-technology

| Changed or additional input | Value |
| --- | --- |
| array.area | 9.17e-05 |
| array.bol_imp | 0.006 |
| array.bol_isc | 0.0063 |
| array.bol_vmp | 4.46 |
| array.bol_voc | 5.53 |
| array.imp | 0.0054 |
| array.isc | 0.00567 |
| array.packing | 0.4983695652 |
| array.parallel | 10 |
| array.product | IXOLAR SSM |
| array.reference_irradiance | 1362 |
| array.series | 4 |
| array.source | Si; A40 packages on deployed .08x.125m plate. Layout8x5 uses.064x.115m. Electrical4S10P is supplied independently of physical placement. Scalar area check establishes no mechanical qualification. |
| array.technology | monocrystalline silicon |
| array.temperature_C | 28 |
| array.usable | 0.01 |
| array.vmp | 4.46 |
| array.voc | 5.53 |


### OreSat:07-battery-chemistry:incompatible

| Changed or additional input | Value |
| --- | --- |
| battery.cell_ah | 1.1 |
| battery.cell_wh | 3.63 |
| battery.charge_limit | 0.5 |
| battery.chemistry | LiFePO4 |
| battery.discharge_limit | 3 |
| battery.maximum | 3.6 |
| battery.minimum | 2 |
| battery.nominal | 3.3 |
| battery.product | A123 APR18650m1-B |
| battery.series | 4 |
| battery.source | LFP; A occupied envelopes, limits, fit and retentions. Two independent4S1P packs in one verification storage group. No claim that these fit a flown card. Published29Wh refers to two cards. |
| charger.allowed_max | 14.4 |
| charger.allowed_min | 14.2 |


### OreSat:07-battery-chemistry:selected-new-charger

| Changed or additional input | Value |
| --- | --- |
| battery.cell_ah | 1.1 |
| battery.cell_wh | 3.63 |
| battery.charge_limit | 0.5 |
| battery.chemistry | LiFePO4 |
| battery.discharge_limit | 3 |
| battery.maximum | 3.6 |
| battery.minimum | 2 |
| battery.nominal | 3.3 |
| battery.product | A123 APR18650m1-B |
| battery.series | 4 |
| battery.source | LFP; A occupied envelopes, limits, fit and retentions. Two independent4S1P packs in one verification storage group. No claim that these fit a flown card. Published29Wh refers to two cards. |
| charger.allowed_max | 14.4 |
| charger.allowed_min | 14.2 |
| charger.chemistry | LiFePO4 |
| charger.current_limit | 0.5 |
| charger.series | 4 |
| charger.set_voltage | 14.4 |


### OreSat:08-integer-configurations

| Changed or additional input | Value |
| --- | --- |
| additional_mutations.Battery.parallel_count | [0,-1,2.5,true] |
| additional_mutations.SolarArray.cell_count | 99 |
| additional_mutations.SolarArray.series_count | [0,-1,2.5,true] |
| array.series | 4 |
| array.usable | 0.016 |
| battery.series | 3 |
| deployment.columns | 2 |
| deployment.edge_clearance_m | 0.003 |
| deployment.gap_m | 0.002 |
| deployment.package_dimension_tolerance_m | 0.0001 |
| deployment.package_length_m | 0.0691 |
| deployment.package_width_m | 0.0397 |
| deployment.plate_length_m | 0.17 |
| deployment.plate_width_m | 0.1 |
| deployment.rows | 2 |
| deployment.source | A rectangular package envelope39.7x69.1mm, based on Spectrolab XTE-SF27cm2 nominal cell outline in the2022-07-27 datasheet p.2. CIC outer envelope is unvalidated. Envelope tolerance,plate,2x2 layout,gaps and clearances are A. |
| deployment.usable_area_m2 | 0.016 |


### OreSat:09-converter-rails

| Changed or additional input | Value |
| --- | --- |
| alternative_converter_interval_V | [1.8,5.5] |
| alternative_converter_product | TPS63020-Q1 (2S Li-ion upper bound8.4V exceeds5.5V) |
| alternative_current_A | 1.6 |
| alternative_output_V | 5.06 |
| rail_cases[0].A | 0.5 |
| rail_cases[0].V | 3.3 |
| rail_cases[1].A | 0.4 |
| rail_cases[1].V | 5 |
| selected_3p3V_product | TPS62111 input3.1-17V |
| selected_5V_product | TPS62112 input3.1-17V |
| unknown | converter.efficiency |
| voltage_tolerance | 0.05 |


### OreSat:10-characteristics

| Changed or additional input | Value |
| --- | --- |
| invalid_curves | [["partial",[[2.43,0.4347],[2.75,0.0]]],["duplicate_voltage",[[0.0,0.5],[1.0,0.4],[1.0,0.3],[2.0,0.0]]],["negative_current",[[0.0,0.5],[1.0,-0.1],[2.0,0.0]]],["nonfinite",[[0.0,0.5],[1.0,"nan"],[2.0,0.0]]]] |
| purchased_panel_variation | 2cell module curve voltage x2, active area x2, external1S1P |
| source_curve_limit | Three-anchor approximation, not complete measured curve. |


### OreSat:11-baseline-DET:DET

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| bus_nominal_V | 7.2 |
| common_bus_demand_W | 0.5 |
| fixed_setpoint_V | unresolved |
| method | DET |


### OreSat:12-baseline-ideal-MPPT:MPPT

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| bus_nominal_V | 7.2 |
| common_bus_demand_W | 0.5 |
| fixed_setpoint_V | unresolved |
| method | MPPT |


### OreSat:13-baseline-fixed-voltage:FIXED_VOLTAGE

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| bus_nominal_V | 7.2 |
| common_bus_demand_W | 0.5 |
| fixed_setpoint_V | 4 |
| method | FIXED_VOLTAGE |


### OreSat:14-unflown-4S-pair:DET

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| array.series | 4 |
| array.usable | 0.016 |
| bus_nominal_V | 7.2 |
| common_bus_demand_W | 0.5 |
| deployment.columns | 2 |
| deployment.edge_clearance_m | 0.003 |
| deployment.gap_m | 0.002 |
| deployment.package_dimension_tolerance_m | 0.0001 |
| deployment.package_length_m | 0.0691 |
| deployment.package_width_m | 0.0397 |
| deployment.plate_length_m | 0.17 |
| deployment.plate_width_m | 0.1 |
| deployment.rows | 2 |
| deployment.source | A rectangular package envelope39.7x69.1mm, based on Spectrolab XTE-SF27cm2 nominal cell outline in the2022-07-27 datasheet p.2. CIC outer envelope is unvalidated. Envelope tolerance,plate,2x2 layout,gaps and clearances are A. |
| deployment.usable_area_m2 | 0.016 |
| fixed_setpoint_V | 8 |
| method | DET |


### OreSat:14-unflown-4S-pair:FIXED_VOLTAGE

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| array.series | 4 |
| array.usable | 0.016 |
| bus_nominal_V | 7.2 |
| common_bus_demand_W | 0.5 |
| deployment.columns | 2 |
| deployment.edge_clearance_m | 0.003 |
| deployment.gap_m | 0.002 |
| deployment.package_dimension_tolerance_m | 0.0001 |
| deployment.package_length_m | 0.0691 |
| deployment.package_width_m | 0.0397 |
| deployment.plate_length_m | 0.17 |
| deployment.plate_width_m | 0.1 |
| deployment.rows | 2 |
| deployment.source | A rectangular package envelope39.7x69.1mm, based on Spectrolab XTE-SF27cm2 nominal cell outline in the2022-07-27 datasheet p.2. CIC outer envelope is unvalidated. Envelope tolerance,plate,2x2 layout,gaps and clearances are A. |
| deployment.usable_area_m2 | 0.016 |
| fixed_setpoint_V | 8 |
| method | FIXED_VOLTAGE |


### OreSat:14-unflown-4S-pair:MPPT

| Changed or additional input | Value |
| --- | --- |
| DET_drop_V | 0.2 |
| array.series | 4 |
| array.usable | 0.016 |
| bus_nominal_V | 7.2 |
| common_bus_demand_W | 0.5 |
| deployment.columns | 2 |
| deployment.edge_clearance_m | 0.003 |
| deployment.gap_m | 0.002 |
| deployment.package_dimension_tolerance_m | 0.0001 |
| deployment.package_length_m | 0.0691 |
| deployment.package_width_m | 0.0397 |
| deployment.plate_length_m | 0.17 |
| deployment.plate_width_m | 0.1 |
| deployment.rows | 2 |
| deployment.source | A rectangular package envelope39.7x69.1mm, based on Spectrolab XTE-SF27cm2 nominal cell outline in the2022-07-27 datasheet p.2. CIC outer envelope is unvalidated. Envelope tolerance,plate,2x2 layout,gaps and clearances are A. |
| deployment.usable_area_m2 | 0.016 |
| fixed_setpoint_V | 8 |
| method | MPPT |


### OreSat:15-operating-point-contract

| Changed or additional input | Value |
| --- | --- |
| interpolation_cases | ["none","linear"] |
| sampling_voltages_V | [4.86,3.8880000000000003,5.51] |
| selectors | ["WRONG",null] |


### OreSat:16-normal-extrema

| Changed or additional input | Value |
| --- | --- |
| OC_A | 0.375 |
| OV_V | 4.1 |
| UV_V | 2.5 |
| charger_endpoint_cross_check.balanced_series_cells | 2 |
| charger_endpoint_cross_check.nominal_cell_OV_V | 4.1 |
| charger_endpoint_cross_check.original_normal_cell_samples_V | [3.0,3.6,4.0] |
| charger_endpoint_cross_check.pack_voltage_V | 8.4 |
| independent_corner_OC_A | 6 |
| independent_corner_OC_source | BIRDS2A regulatedrail setting. OreSat6A supplied separate spacecraft-bus OC device, no PTC behavior claim. |
| independent_corner_powers_W | [6.0,30.0] |
| independent_corner_voltage_V | [6.0,8.4] |
| mission | OreSat |
| sensed_rail_current_A | [0.265,0.314,0.362] |
| sensed_voltages_V | [3.0,3.6,4.0] |
| source | O-protect nominalABLIC cellthresholds and suppliedindividualcellnormal3-4V. OC localheaterbranch .245/.294/.342+.020A electronicsassumption, enabledMOARPWR. Powercorners at separate spacecraftbatterybus6-8.4V. |


### OreSat:17-threshold-boundaries

| Changed or additional input | Value |
| --- | --- |
| OC_A | 0.375 |
| OV_V | 4.1 |
| UV_V | 2.5 |
| additional_OC_scope | BIRDS Unreg2 and Unreg1 are distinct unregulated rail detectors. OreSat6A is a supplied spacecraft battery-bus detector, separate from local heater OC and ABLIC cell sensing. |
| additional_OC_settings[0].rail | spacecraft_battery_bus |
| additional_OC_settings[0].threshold_A | 6 |
| factors | [0.99,1.0,1.01] |
| invalid_current | [[-0.01],[],null] |
| invalid_voltages | [null,[],["nan"]] |
| mission | OreSat |
| unknown_OC_threshold | true |


### OreSat:18-unknown-invalid-feasibility

| Changed or additional input | Value |
| --- | --- |
| inadequate_sunlight_delivery_J | 1 |
| invalid_cycles | 30000 |
| invalid_orbit.R | 6378 |
| invalid_orbit.a | 6500 |
| invalid_orbit.e | 0.2 |
| invalid_packing | 0 |
| invalid_retention | 1.1 |
| unknown | ["SolarArray.series_count","SolarArray.usable_area","Battery.cycle_coefficient","Battery.energy_retention","orbit.altitude"] |


## Source and assumption register


### A

| Field | Value |
| --- | --- |
| key | unresolved |
| locator | Supplied verification assumptions in the complete input tables |
| values | All lifetime/DoD fits, retentions other than stated fluence data, margins, efficiencies, allocations, unknown mass/volume, delivered-energy allocations, receiving windows, charger selections and settings, duties and load currents are supplied assumptions. |


### B-Azur

| Field | Value |
| --- | --- |
| key | cots-mission_azur_space_3g30a_review_legacy_ds |
| locator | 3G30A datasheet DB0003401-01-01, 2016-08-19 p.2 |
| url | https://d35rpq4gusjz9h.cloudfront.net/files/73192/download/634236/73192_19_2023090605471491796.pdf |
| values | AM0 1367 W/m2, 28 C. BOL Vmp=2.409 V, Imp=.5029 A, Voc=2.690 V, Isc=.5196 A. 1e15 1 MeV electrons/cm2: Vmp=2.244 V, Imp=.4851 A, Voc=2.512 V, Isc=.5013 A. Active area=.003018 m2. Complete three-anchor curve is an approximation, not a measured full curve. |


### B-IV

| Field | Value |
| --- | --- |
| key | shrestha2021birdssafety |
| locator | Figs.13-14 pp.6-7, Maya-2 +Z two-cell panel |
| values | V=5.223 at zero current, 5.123 V at 50 mA, 5.022 V at 100 mA. Printed P labels .257, .502 W and peak1.575 W. High-current x coordinates are not numerically labelled. No reconstruction of the true 1.575 W MPP is claimed. |


### B-budget

| Field | Value |
| --- | --- |
| key | shrestha2022birds4powerbudget |
| locator | 2022 presentation pp.5,8,13 |
| values | 428 mW x 1.5 h=642 mWh, 144 mW x 1 h=144 mWh, 280 mW x .5 h=140 mWh. p.8 beta30 eclipse35 min: (2173-240)*.8=1546 mWh rounded. p.13 (2507-240)*.8-210=1604 mWh rounded. Free rotation uses supplied external energies only. |


### B-cell

| Field | Value |
| --- | --- |
| key | birds2021batteryverification |
| locator | Battery Verification Report, Fig. 1-1 p.21, pinned d7eadd98f5327e1ddea82b640293d49bfdb09555 |
| url | https://github.com/BIRDSOpenSource/BIRDS4-ProceduresAndReports/blob/d7eadd98f5327e1ddea82b640293d49bfdb09555/Battery%28Cells%29%20Screening%20Procedures%20and%20its%20verification%20Report_V1.0%20%282%29.pdf |
| values | 27 g x 6 = 162 g, diameter 14.35 mm, height 50.4 mm, 3S2P, 1.2 V, 3800 mAh |


### B-orbit

| Field | Value |
| --- | --- |
| key | jara2022birdsepsdataset |
| locator | Section 2 |
| values | 400 km, ISS orbit. Reference geometry and prescribed Sun/nadir pointing are supplied variations. |


### B-rail

| Field | Value |
| --- | --- |
| key | kyutech2021birdsicd |
| locator | Sec.6.3 |
| values | 3.3 and 5 V rails, OC2/3/4 A regulated/Unreg2/Unreg1. Converter current capacities and efficiencies used here are supplied assumptions. |


### LFP

| Field | Value |
| --- | --- |
| key | oresatbatteryresearch |
| locator | Choice#2 A123 APR18650m1-B |
| values | LiFePO4,3.3 V nominal,1.1 Ah,cell2.0-3.6 V. 4S1P x2 cards29 Wh rounded. Room-temperature charge.5 A/discharge3 A and all fit/retention values are assumptions. |


### Li-ion

| Field | Value |
| --- | --- |
| key | cots-mission_tenergy_30005_0_ds |
| locator | Tenergy30005-0 datasheet pp.2-4, capacity/voltage/current ratings, and O-pack for the separate mission nominal3.6 V convention |
| url | https://files.batteryjunction.com/frontend/files/tenergy/datasheet/TENERGY-30005-18650-FLAT-Datasheet.pdf |
| values | 2.6 Ah,2.75-4.2 V, charge1.25 A at15-45 C, discharge5 A at5-45 C. Reference temperature25 C. This case uses mission nominal3.6x2.6=9.36 Wh. The datasheet average3.65 V would give9.49 Wh and is not substituted. Neither nominal product is a measured energy guarantee. |


### O-budget

| Field | Value |
| --- | --- |
| key | oresat2019powerbudget |
| locator | 2019 budget standby and battery rows |
| values | 1634-623=1011 mWh. Four2S3.3 Ah packs at7.2 V=95.04 Wh and60% DoD=57.024 Wh. Historical only. |


### O-mass

| Field | Value |
| --- | --- |
| key | oresat2016csli |
| locator | D.2 pp.21-22 |
| values | 8 solar modules x31.5 g=252 g, 4 battery modules x104 g=416 g. Historical mass boundary only. All volumes and other masses supplied. |


### O-pack

| Field | Value |
| --- | --- |
| key | greenberg2021oresat |
| locator | p.6 |
| values | Two independently protected 2S packs per card, 2.6 Ah per branch at mission nominal3.6 V/cell,37.4 Wh/card rounded. The branches share the real card bus, where currents add by Kirchhoff's current law. These checks retain each branch's ratings and do not assume a current-sharing law. |


### O-package

| Field | Value |
| --- | --- |
| key | cots-solar_src_spectro_xtesf |
| locator | Spectrolab XTE-SF datasheet,2022-07-27 p.2,27cm2 rectangular cell outline |
| url | https://www.spectrolab.com/photovoltaics/XTE-SF%20Data%20Sheet%20_07.27.22.pdf |
| values | Cell outline3.97x6.91cm. The verification package envelope uses these nominal dimensions with a supplied0.1mm upper allowance. Actual CIC/contact envelope remains unvalidated. |


### O-protect

| Field | Value |
| --- | --- |
| key | oresat2025batterydesign |
| locator | ABLIC selection, load current, heater and MOARPWR sections |
| values | S-8209AAA per-cell UV2.50 V,OV4.10 V nominal (tolerances absent, not worst-case qualification).30 W at6/7.2/8.4 V=5/4.17/3.57 A. Local heater currents.245/.294/.342 A,OC.375 A enabled heater setting. Card electronics current.020 A supplied. |


### O-rail

| Field | Value |
| --- | --- |
| key | oresat2021opddesign |
| locator | OreSat Power Domain Design Notes, stated update2021-08-22, TPS62111/TPS62112 section |
| url | https://docs.google.com/document/d/1NOkO6gGEJUFRpOrkwClRlZlzWuTLteq6fP9LPf_Ez0M/edit |
| values | TPS62111/12 input3.1-17 V,out3.3/5 V,max1.5 A. Efficiency.9 is supplied. The separate SPV1040 historical rejection uses oresatsolarhistory. |


### O-solar

| Field | Value |
| --- | --- |
| key | oresat2025solardesign |
| locator | Solar Cells: GaAs |
| values | XTE-SF Vmp2.43 V, Imp.483 A, Voc2.75 V, Isc.502 A, area.0027 m2,28 C AM0;2-cell output2.34 W rounded. Reference G1367 is supplied, and EOL current retention.9 is assumed. Complete three anchors are an approximation. |


### O-sweep

| Field | Value |
| --- | --- |
| key | oresatsolarsweep |
| locator | minicom.cap F2:H206; F197:H197 |
| url | https://docs.google.com/spreadsheets/d/1vNrHLC0C6YMA_wZTWuHt7_7BPwSQPb8aQuyxLQmDAQ8/edit |
| values | 205 published samples, row1974.435 V,.37304 A,1.6544324 W; row2 4.77625 V,.06406 A,.305966575 W. Unsorted/duplicate voltage, no endpoints. Raw curve is rejected, without sorting or invented endpoint claims. |


### SPV

| Field | Value |
| --- | --- |
| key | oresatsolarhistory |
| locator | Rev2 historical design notes after1S-to2S change |
| url | https://github.com/oresat/oresat-solar-hardware/blob/47d610c1964c31f049a8f9844f7881931b5d0f06/README.md |
| values | Published rejection:SPV1040 cannot supply the2S charging voltage. The5.2V numeric ceiling is a declared static compatibility input in this case. No general boost envelope is inferred. |


### Si

| Field | Value |
| --- | --- |
| key | shrestha2026solarreliability |
| locator | Table3 p.25042 and Sec.IV.C |
| values | IXOLAR SSM silicon Vmp4.46 V, Imp.006 A,Voc5.53 V,Isc.0063 A, active.0000917 m2, package.008x.023 m. Curve reference1362 W/m2 supplied from article context, EOL current retention.9 assumed. Two-dimensional4x10 package layout occupies.032x.23 m if long strip, or8x5 layout.064x.115 m. Installation here is an explicit deployed.010 m2 plate, not a flush1U fit. |


### Bibliography integration

Existing keys include shrestha2021birdssafety, shrestha2022birds4powerbudget, shrestha2026solarreliability, jara2022birdsepsdataset, oresat2016csli, greenberg2021oresat, oresat2019powerbudget, oresatbatteryresearch, oresat2025batterydesign, oresat2025solardesign, oresatsolarsweep, kyutech2021birdsicd and cots-mission_azur_space_3g30a_review_legacy_ds. Li-ion limits use `cots-mission_tenergy_30005_0_ds` with the actual Tenergy datasheet URL. OPD converter material uses `oresat2021opddesign` with the actual OPD notes URL. The XTE-SF outline uses `cots-solar_src_spectro_xtesf`, while its package envelope remains explicitly assumed. The mission3.6V energy convention remains separate from Tenergy's3.65V average. One new entry is supplied in `new-source.bib` for the original battery verification report. The filename's revision and combined report dates should remain visible. The article's safety key is not reused as if it identified that report.

## Fully expanded comparison ledger

The following ledger is an appendix-ready record of every executed comparison. Each scenario has the full input declaration or baseline delta above. Expected unknown status is compared exactly. Invalid-domain errors require both error status and ValueError type. An unrelated binding error does not count as a successful rejection. Numerical relative errors are fractions in raw JSON and percentages here. False engineering verdicts are printed as false, separately from the match result. Every Property/function provider and Requirement dependency trace remains in JSON/CSV.


### BIRDS-4: 01-mass-boundaries

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-12 | published_cell_only_mass | kg | 0.162 | 0.162 | 0 | match |
| MOP-12 | cylindrical_cell_volume | m3 | 4.890750076e-05 | 4.890750076e-05 | 0 | match |
| MOP-12 | cell_source |  | B-cell Fig.1-1 p.21, cell-only | B-cell Fig.1-1 p.21, cell-only |  | match |
| MOP-12 | mass | kg | 0.3 | 0.3 | 0 | match |
| MOP-12 | volume | m3 | 0.000121 | 0.000121 | 1.120043567e-14 | match |
| MOP-12 | mass_margin | kg | 0.05 | 0.05 | 2.775557562e-14 | match |
| MOP-12 | volume_margin | m3 | 2.9e-05 | 2.9e-05 | 9.346570452e-14 | match |
| MOP-12 | mass_allocation | verdict | true | true |  | match |
| MOP-12 | volume_allocation | verdict | true | true |  | match |
| MOP-12 | aggregate_replacement_no_double_count | kg | 0.3 | 0.3 | 0 | match |
| MOP-12 | zero_margin_passes | verdict | true | true |  | match |
| MOP-12 | negative_margin_fails | verdict | false | false |  | match |
| MOP-12 | unknown_mass_total | kg | unresolved | unresolved |  | expected unknown |
| MOP-12 | unknown_mass_margin | kg | unresolved | unresolved |  | expected unknown |
| MOP-12 | volume_unaffected_by_unknown_mass | m3 | 0.000121 | 0.000121 | 1.120043567e-14 | match |
| MOP-12 | unknown_mass_allocation | verdict | unresolved | unresolved |  | expected unknown |
| MOP-12 | unknown_volume_total | m3 | unresolved | unresolved |  | expected unknown |
| MOP-12 | unknown_volume_margin | m3 | unresolved | unresolved |  | expected unknown |
| MOP-12 | unknown_volume_allocation | verdict | unresolved | unresolved |  | expected unknown |
| MOP-12 | mass_unit_record |  | kg | kg |  | match |
| MOP-12 | volume_unit_record |  | m3 | m3 |  | match |


### BIRDS-4: 02-states-modes-circular

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-14a | period | s | 5553.452008 | 5553.452008 | 1.637710563e-14 | match |
| MOP-14a | sunlight | s | 3486.457103 | 3486.474969 | 0.000512424693 | match |
| MOP-14a | eclipse | s | 2066.994905 | 2066.97704 | 0.0008643208099 | match |
| MOP-14b | projection | 1 | 1 | 1 | 0 | match |
| MOP-14b | projected_duration | s | 3486.457103 | 3486.474969 | 0.000512424693 | match |
| MOP-14a | main_state_power | W | 0.429 | 0.429 | 0 | match |
| MOP-14a | receiver_state_power | W | 0.1452 | 0.1452 | 0 | match |
| MOP-14a | beacon_state_power | W | 0.28 | 0.28 | 0 | match |
| MOP-14a | sunlight_mode_aggregation | W | 0.6442 | 0.6442 | 0 | match |
| MOP-14a | sunlight_EPS_consumption_boundary | W | 0 | 0 |  | match |
| MOP-14a | sunlight_mean | W | 0.6442 | 0.6442 | 0 | match |
| MOP-14a | sunlight_energy | J | 2245.975666 | 2245.987175 | 0.000512424693 | match |
| MOP-14a | sunlight_delivery | verdict | true | true |  | match |
| MOP-14a | eclipse_mode_aggregation | W | 0.6022 | 0.6022 | 0 | match |
| MOP-14a | eclipse_EPS_consumption_boundary | W | 0 | 0 |  | match |
| MOP-14a | eclipse_mean | W | 0.6022 | 0.6022 | 0 | match |
| MOP-14a | eclipse_energy | J | 1244.744332 | 1244.733573 | 0.0008643208099 | match |
| MOP-14a | eclipse_delivery | verdict | true | true |  | match |
| MOP-14a | minimum_panel_power | W | 1.233912621 | 1.233906067 | 0.0005311309418 | match |
| MOP-14a | main_energy | Wh | 0.642 | 0.642 | 0 | match |
| MOP-14a | receiver_energy | Wh | 0.144 | 0.144 | 0 | match |
| MOP-14a | CW_energy | Wh | 0.14 | 0.14 | 0 | match |
| MOP-14a | external_free_rotation_BCR | mWh | 1546 | 1546.4 | 0.02587322122 | match |
| MOP-14a | external_free_rotation_load | mWh | 1604 | 1603.6 | 0.02493765586 | match |


### BIRDS-4: 03-eccentric-nadir

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-14a | period | s | 5553.452008 | 5553.452008 | 1.637710563e-14 | match |
| MOP-14a | sunlight | s | 3432.07588 | 3432.077747 | 5.44013071e-05 | match |
| MOP-14a | eclipse | s | 2121.376128 | 2121.374261 | 8.801334735e-05 | match |
| MOP-14b | projection | 1 | 0.4567932074 | 0.4567929589 | 5.440148737e-05 | match |
| MOP-14b | projected_duration | s | 1567.748949 | 1567.748949 | 2.098612208e-10 | match |
| MOP-14a | minimum_panel_power | W | 1.254177792 | 1.254177085 | 5.635541105e-05 | match |
| MOP-14b | nontrivial_projection_generation | W | 0.9164295821 | 0.9164290836 | 5.440148738e-05 | match |
| MOP-14b | nadir_generation_verdict | verdict | false | false |  | match |


### BIRDS-4: 04-eclipse-free

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-14a | period | s | 5553.452008 | 5553.452008 | 1.637710563e-14 | match |
| MOP-14a | sunlight | s | 5553.452008 | 5553.452008 | 1.637710563e-14 | match |
| MOP-14a | eclipse | s | 0 | 0 |  | match |
| MOP-14b | projection | 1 | 1 | 1 | 0 | match |
| MOP-14b | projected_duration | s | 5553.452008 | 5553.452008 | 1.637710563e-14 | match |
| MOP-14a | zero_eclipse_demand | verdict | true | true |  | match |
| MOP-14a | zero_eclipse_energy | J | 0 | 0 |  | match |
| MOP-14a | unused_eclipse_efficiency_identity | 1 | 1 | 1 | 0 | match |
| MOP-14a | minimum_panel_power | W | 0.7578823529 | 0.7578823529 | 0 | match |


### BIRDS-4: 05-baseline-sizing

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-14b | cell_power | W | 1.0885644 | 1.0885644 | 0 | match |
| MOP-14b | array_mpp | W | 2.1771288 | 2.1771288 | 0 | match |
| MOP-14b | array_voltage | V | 4.488 | 4.488 | 0 | match |
| MOP-14b | array_current | A | 0.4851 | 0.4851 | 0 | match |
| MOP-14b | array_voc | V | 5.024 | 5.024 | 0 | match |
| MOP-14b | array_isc | A | 0.5013 | 0.5013 | 0 | match |
| MOP-14b | active_area | m2 | 0.006036 | 0.006036 | 0 | match |
| MOP-14b | panel_area | m2 | 0.007545 | 0.007545 | 0 | match |
| MOP-14b | required_area | m2 | 0.003712394966 | 0.003712375248 | 0.0005311309418 | match |
| MOP-14b | effective_area | m2 | 0.003420971961 | 0.003420953791 | 0.0005311309418 | match |
| MOP-14b | tumbling_area | m2 | 0.01330521898 | 0.01330514831 | 0.0005311309418 | match |
| MOP-14b | generation_efficiency | 1 | 0.2638556372 | 0.2638556372 | 2.103845566e-14 | match |
| MOP-14b | density | W/m2 | 332.3764396 | 332.3764396 | 1.71021204e-14 | match |
| MOP-14b | available_power | W | 2.006224189 | 2.006224189 | 2.21355725e-14 | match |
| MOP-14b | source_energy | J | 6994.614575 | 6994.650417 | 0.000512424693 | match |
| MOP-14b | fractional_count | cell | 1.13352285 | 1.133516829 | 0.0005311309418 | match |
| MOP-14b | required_count | cell | 2 | 2 |  | match |
| MOP-14b | minimum_solar_parallel | string | 1 | 1 |  | match |
| MOP-14b | cycles | cycle | 5682.519621 | 5682.519621 | 0 | match |
| MOP-14b | dod | 1 | 0.3519565498 | 0.3519565498 | 0 | match |
| MOP-14b | required_battery_energy | J | 4243.970453 | 4243.933772 | 0.0008643208099 | match |
| MOP-14b | minimum_battery_parallel | string | 1 | 1 |  | match |
| MOP-14b | pack_wh | Wh | 13.68 | 13.68 | 0 | match |
| MOP-14b | pack_ah | Ah | 3.8 | 3.8 | 0 | match |
| MOP-14b | pack_j | J | 49248 | 49248 | 0 | match |
| MOP-14b | eol_j | J | 39398.4 | 39398.4 | 0 | match |
| MOP-14b | eol_ah | Ah | 3.04 | 3.04 | 0 | match |
| MOP-14b | battery_voltage | V | 3.6 | 3.6 | 1.233581138e-14 | match |
| MOP-14b | battery_min | V | 3 | 3 | 0 | match |
| MOP-14b | battery_max | V | 4.35 | 4.35 | 0 | match |
| MOP-14b | charge_limit | A | 1.9 | 1.9 | 0 | match |
| MOP-14b | discharge_limit | A | 4 | 4 | 0 | match |
| MOP-14b | solar_power_verdict | verdict | true | true |  | match |
| MOP-14b | solar_count_verdict | verdict | true | true |  | match |
| MOP-14b | battery_energy_verdict | verdict | true | true |  | match |
| MOP-14b | solar_configuration_verdict | verdict | true | true |  | match |
| MOP-14b | battery_configuration_verdict | verdict | true | true |  | match |
| MOP-14b | area_fit_verdict | verdict | true | true |  | match |
| MOP-14b | active_area_verdict | verdict | true | true |  | match |
| MOP-14b | generation_verdict | verdict | true | true |  | match |
| MOP-14b | tracking_voltage_verdict | verdict | true | true |  | match |
| MOP-14b | absolute_voltage_verdict | verdict | true | true |  | match |
| MOP-14b | source_current_verdict | verdict | true | true |  | match |
| MOP-14b | battery_receiving_verdict | verdict | true | true |  | match |
| MOP-14b | charge_current_verdict | verdict | true | true |  | match |
| MOP-14b | discharge_current_verdict | verdict | true | true |  | match |
| MOP-14b | storage_occupied_volume | m3 | 6.92e-05 | 6.92e-05 | 0 | match |
| MOP-14b | battery_installation_verdict | verdict | true | true |  | match |
| MOP-14b | BOL_cell_power | W | 1.2114861 | 1.2114861 | 0 | match |
| MOP-14b | EOL_efficiency_once | 1 | 0.2638556372 | 0.2638556372 | 2.103845566e-14 | match |
| MOP-15 | baseline_charger | verdict | true | true |  | match |
| MOP-14b | BOL_case_minimum_panel_power | W | 1.233912621 | 1.233906067 | 0.0005311309418 | match |
| MOP-14b | BOL_case_fractional_count | cell | 1.018511579 | 1.01850617 | 0.0005311309418 | match |
| MOP-14b | BOL_case_required_count | cell | 2 | 2 |  | match |
| MOP-14b | BOL_case_minimum_solar_parallel | string | 1 | 1 |  | match |
| MOP-14b | BOL_case_cell_power | W | 1.2114861 | 1.2114861 | 0 | match |
| MOP-14b | BOL_case_array_mpp | W | 2.4229722 | 2.4229722 | 0 | match |
| MOP-14b | BOL_case_array_voltage | V | 4.818 | 4.818 | 0 | match |
| MOP-14b | BOL_case_array_current | A | 0.5029 | 0.5029 | 0 | match |
| MOP-14b | BOL_case_array_voc | V | 5.38 | 5.38 | 0 | match |
| MOP-14b | BOL_case_array_isc | A | 0.5196 | 0.5196 | 0 | match |
| MOP-14b | BOL_case_generation_efficiency | 1 | 0.2936504601 | 0.2936504601 | 0 | match |
| MOP-14b | BOL_case_active_area | m2 | 0.006036 | 0.006036 | 0 | match |
| MOP-14b | BOL_case_panel_area | m2 | 0.007545 | 0.007545 | 0 | match |
| MOP-14b | BOL_case_required_area | m2 | 0.003335722134 | 0.003335704417 | 0.0005311309418 | match |
| MOP-14b | BOL_case_effective_area | m2 | 0.003073867946 | 0.00307385162 | 0.0005311309418 | match |
| MOP-14b | BOL_case_density | W/m2 | 369.9086949 | 369.9086949 | 0 | match |
| MOP-14b | BOL_case_available_power | W | 2.232768882 | 2.232768882 | 0 | match |
| MOP-14b | BOL_case_source_energy | J | 7784.452929 | 7784.492819 | 0.000512424693 | match |
| MOP-14b | BOL_case_solar_power_verdict | verdict | true | true |  | match |
| MOP-14b | BOL_case_solar_count_verdict | verdict | true | true |  | match |
| MOP-14b | BOL_case_area_fit_verdict | verdict | true | true |  | match |
| MOP-14b | BOL_case_active_area_verdict | verdict | true | true |  | match |
| MOP-14b | BOL_case_generation_verdict | verdict | true | true |  | match |


### BIRDS-4: 06-silicon-technology

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-15 | cell_power | W | 0.024084 | 0.024084 | 0 | match |
| MOP-15 | array_mpp | W | 0.96336 | 0.96336 | 0 | match |
| MOP-15 | array_voltage | V | 17.84 | 17.84 | 0 | match |
| MOP-15 | array_current | A | 0.054 | 0.054 | 1.284980353e-14 | match |
| MOP-15 | array_voc | V | 22.12 | 22.12 | 0 | match |
| MOP-15 | array_isc | A | 0.0567 | 0.0567 | 0 | match |
| MOP-15 | active_area | m2 | 0.003668 | 0.003668 | 1.182336066e-14 | match |
| MOP-15 | panel_area | m2 | 0.00736 | 0.00736 | 1.178480622e-14 | match |
| MOP-15 | required_area | m2 | 0.005079703658 | 0.005079676678 | 0.0005311309418 | match |
| MOP-15 | effective_area | m2 | 0.004680946921 | 0.004680922059 | 0.0005311309419 | match |
| MOP-15 | tumbling_area | m2 | 0.02922433939 | 0.02922418417 | 0.0005311309419 | match |
| MOP-15 | generation_efficiency | 1 | 0.192833363 | 0.192833363 | 0 | match |
| MOP-15 | density | W/m2 | 242.9103554 | 242.9103554 | 1.170049312e-14 | match |
| MOP-15 | available_power | W | 0.8909951836 | 0.8909951836 | 1.24604829e-14 | match |
| MOP-15 | source_energy | J | 3106.416487 | 3106.432405 | 0.000512424693 | match |
| MOP-15 | fractional_count | cell | 51.2337079 | 51.23343578 | 0.0005311309418 | match |
| MOP-15 | required_count | cell | 52 | 52 |  | match |
| MOP-15 | minimum_solar_parallel | string | 13 | 13 |  | match |
| MOP-15 | cycles | cycle | 5682.519621 | 5682.519621 | 0 | match |
| MOP-15 | dod | 1 | 0.3519565498 | 0.3519565498 | 0 | match |
| MOP-15 | required_battery_energy | J | 4243.970453 | 4243.933772 | 0.0008643208099 | match |
| MOP-15 | minimum_battery_parallel | string | 1 | 1 |  | match |
| MOP-15 | pack_wh | Wh | 13.68 | 13.68 | 0 | match |
| MOP-15 | pack_ah | Ah | 3.8 | 3.8 | 0 | match |
| MOP-15 | pack_j | J | 49248 | 49248 | 0 | match |
| MOP-15 | eol_j | J | 39398.4 | 39398.4 | 0 | match |
| MOP-15 | eol_ah | Ah | 3.04 | 3.04 | 0 | match |
| MOP-15 | battery_voltage | V | 3.6 | 3.6 | 1.233581138e-14 | match |
| MOP-15 | battery_min | V | 3 | 3 | 0 | match |
| MOP-15 | battery_max | V | 4.35 | 4.35 | 0 | match |
| MOP-15 | charge_limit | A | 1.9 | 1.9 | 0 | match |
| MOP-15 | discharge_limit | A | 4 | 4 | 0 | match |
| MOP-15 | solar_power_verdict | verdict | false | false |  | match |
| MOP-15 | solar_count_verdict | verdict | false | false |  | match |
| MOP-15 | battery_energy_verdict | verdict | true | true |  | match |
| MOP-15 | solar_configuration_verdict | verdict | true | true |  | match |
| MOP-15 | battery_configuration_verdict | verdict | true | true |  | match |
| MOP-15 | area_fit_verdict | verdict | true | true |  | match |
| MOP-15 | active_area_verdict | verdict | false | false |  | match |
| MOP-15 | generation_verdict | verdict | false | false |  | match |
| MOP-15 | tracking_voltage_verdict | verdict | false | false |  | match |
| MOP-15 | absolute_voltage_verdict | verdict | false | false |  | match |
| MOP-15 | source_current_verdict | verdict | true | true |  | match |
| MOP-15 | battery_receiving_verdict | verdict | true | true |  | match |
| MOP-15 | charge_current_verdict | verdict | true | true |  | match |
| MOP-15 | discharge_current_verdict | verdict | true | true |  | match |
| MOP-15 | storage_occupied_volume | m3 | 6.92e-05 | 6.92e-05 | 0 | match |
| MOP-15 | battery_installation_verdict | verdict | true | true |  | match |


### BIRDS-4: 07-battery-chemistry

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-15 | cell_power | W | 1.0885644 | 1.0885644 | 0 | match |
| MOP-15 | array_mpp | W | 2.1771288 | 2.1771288 | 0 | match |
| MOP-15 | array_voltage | V | 4.488 | 4.488 | 0 | match |
| MOP-15 | array_current | A | 0.4851 | 0.4851 | 0 | match |
| MOP-15 | array_voc | V | 5.024 | 5.024 | 0 | match |
| MOP-15 | array_isc | A | 0.5013 | 0.5013 | 0 | match |
| MOP-15 | active_area | m2 | 0.006036 | 0.006036 | 0 | match |
| MOP-15 | panel_area | m2 | 0.007545 | 0.007545 | 0 | match |
| MOP-15 | required_area | m2 | 0.003712394966 | 0.003712375248 | 0.0005311309418 | match |
| MOP-15 | effective_area | m2 | 0.003420971961 | 0.003420953791 | 0.0005311309418 | match |
| MOP-15 | tumbling_area | m2 | 0.01330521898 | 0.01330514831 | 0.0005311309418 | match |
| MOP-15 | generation_efficiency | 1 | 0.2638556372 | 0.2638556372 | 2.103845566e-14 | match |
| MOP-15 | density | W/m2 | 332.3764396 | 332.3764396 | 1.71021204e-14 | match |
| MOP-15 | available_power | W | 2.006224189 | 2.006224189 | 2.21355725e-14 | match |
| MOP-15 | source_energy | J | 6994.614575 | 6994.650417 | 0.000512424693 | match |
| MOP-15 | fractional_count | cell | 1.13352285 | 1.133516829 | 0.0005311309418 | match |
| MOP-15 | required_count | cell | 2 | 2 |  | match |
| MOP-15 | minimum_solar_parallel | string | 1 | 1 |  | match |
| MOP-15 | cycles | cycle | 5682.519621 | 5682.519621 | 0 | match |
| MOP-15 | dod | 1 | 0.3519565498 | 0.3519565498 | 0 | match |
| MOP-15 | required_battery_energy | J | 4243.970453 | 4243.933772 | 0.0008643208099 | match |
| MOP-15 | minimum_battery_parallel | string | 1 | 1 |  | match |
| MOP-15 | pack_wh | Wh | 18.72 | 18.72 | 0 | match |
| MOP-15 | pack_ah | Ah | 5.2 | 5.2 | 0 | match |
| MOP-15 | pack_j | J | 67392 | 67392 | 0 | match |
| MOP-15 | eol_j | J | 53913.6 | 53913.6 | 1.349558852e-14 | match |
| MOP-15 | eol_ah | Ah | 4.16 | 4.16 | 0 | match |
| MOP-15 | battery_voltage | V | 3.6 | 3.6 | 0 | match |
| MOP-15 | battery_min | V | 2.75 | 2.75 | 0 | match |
| MOP-15 | battery_max | V | 4.2 | 4.2 | 0 | match |
| MOP-15 | charge_limit | A | 2.5 | 2.5 | 0 | match |
| MOP-15 | discharge_limit | A | 10 | 10 | 0 | match |
| MOP-15 | solar_power_verdict | verdict | true | true |  | match |
| MOP-15 | solar_count_verdict | verdict | true | true |  | match |
| MOP-15 | battery_energy_verdict | verdict | true | true |  | match |
| MOP-15 | solar_configuration_verdict | verdict | true | true |  | match |
| MOP-15 | battery_configuration_verdict | verdict | true | true |  | match |
| MOP-15 | area_fit_verdict | verdict | true | true |  | match |
| MOP-15 | active_area_verdict | verdict | true | true |  | match |
| MOP-15 | generation_verdict | verdict | true | true |  | match |
| MOP-15 | tracking_voltage_verdict | verdict | true | true |  | match |
| MOP-15 | absolute_voltage_verdict | verdict | true | true |  | match |
| MOP-15 | source_current_verdict | verdict | true | true |  | match |
| MOP-15 | battery_receiving_verdict | verdict | true | true |  | match |
| MOP-15 | charge_current_verdict | verdict | true | true |  | match |
| MOP-15 | discharge_current_verdict | verdict | true | true |  | match |
| MOP-15 | storage_occupied_volume | m3 | 5.6e-05 | 5.6e-05 | 1.210047068e-14 | match |
| MOP-15 | battery_installation_verdict | verdict | true | true |  | match |
| MOP-15 | unchanged_charger_incompatible | verdict | false | false |  | match |
| MOP-15 | explicit_new_charger_compatible | verdict | true | true |  | match |


### BIRDS-4: 08-integer-configurations

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-16 | cell_power | W | 1.0885644 | 1.0885644 | 0 | match |
| MOP-16 | array_mpp | W | 4.3542576 | 4.3542576 | 0 | match |
| MOP-16 | array_voltage | V | 8.976 | 8.976 | 0 | match |
| MOP-16 | array_current | A | 0.4851 | 0.4851 | 0 | match |
| MOP-16 | array_voc | V | 10.048 | 10.048 | 0 | match |
| MOP-16 | array_isc | A | 0.5013 | 0.5013 | 0 | match |
| MOP-16 | active_area | m2 | 0.012072 | 0.012072 | 0 | match |
| MOP-16 | panel_area | m2 | 0.01509 | 0.01509 | 0 | match |
| MOP-16 | required_area | m2 | 0.003712394966 | 0.003712375248 | 0.0005311309418 | match |
| MOP-16 | effective_area | m2 | 0.003420971961 | 0.003420953791 | 0.0005311309418 | match |
| MOP-16 | tumbling_area | m2 | 0.01330521898 | 0.01330514831 | 0.0005311309418 | match |
| MOP-16 | generation_efficiency | 1 | 0.2638556372 | 0.2638556372 | 2.103845566e-14 | match |
| MOP-16 | density | W/m2 | 332.3764396 | 332.3764396 | 1.71021204e-14 | match |
| MOP-16 | available_power | W | 4.012448378 | 4.012448378 | 2.21355725e-14 | match |
| MOP-16 | source_energy | J | 13989.22915 | 13989.30083 | 0.000512424693 | match |
| MOP-16 | fractional_count | cell | 1.13352285 | 1.133516829 | 0.0005311309418 | match |
| MOP-16 | required_count | cell | 2 | 2 |  | match |
| MOP-16 | minimum_solar_parallel | string | 1 | 1 |  | match |
| MOP-16 | cycles | cycle | 5682.519621 | 5682.519621 | 0 | match |
| MOP-16 | dod | 1 | 0.3519565498 | 0.3519565498 | 0 | match |
| MOP-16 | required_battery_energy | J | 4243.970453 | 4243.933772 | 0.0008643208099 | match |
| MOP-16 | minimum_battery_parallel | string | 1 | 1 |  | match |
| MOP-16 | pack_wh | Wh | 4.56 | 4.56 | 0 | match |
| MOP-16 | pack_ah | Ah | 1.9 | 1.9 | 0 | match |
| MOP-16 | pack_j | J | 16416 | 16416 | 0 | match |
| MOP-16 | eol_j | J | 13132.8 | 13132.8 | 1.385073559e-14 | match |
| MOP-16 | eol_ah | Ah | 1.52 | 1.52 | 0 | match |
| MOP-16 | battery_voltage | V | 2.4 | 2.4 | 0 | match |
| MOP-16 | battery_min | V | 2 | 2 | 0 | match |
| MOP-16 | battery_max | V | 2.9 | 2.9 | 0 | match |
| MOP-16 | charge_limit | A | 0.95 | 0.95 | 0 | match |
| MOP-16 | discharge_limit | A | 2 | 2 | 0 | match |
| MOP-16 | solar_power_verdict | verdict | true | true |  | match |
| MOP-16 | solar_count_verdict | verdict | true | true |  | match |
| MOP-16 | battery_energy_verdict | verdict | true | true |  | match |
| MOP-16 | solar_configuration_verdict | verdict | true | true |  | match |
| MOP-16 | battery_configuration_verdict | verdict | true | true |  | match |
| MOP-16 | area_fit_verdict | verdict | true | true |  | match |
| MOP-16 | active_area_verdict | verdict | true | true |  | match |
| MOP-16 | generation_verdict | verdict | true | true |  | match |
| MOP-16 | tracking_voltage_verdict | verdict | true | true |  | match |
| MOP-16 | absolute_voltage_verdict | verdict | true | true |  | match |
| MOP-16 | source_current_verdict | verdict | true | true |  | match |
| MOP-16 | battery_receiving_verdict | verdict | false | false |  | match |
| MOP-16 | charge_current_verdict | verdict | true | true |  | match |
| MOP-16 | discharge_current_verdict | verdict | true | true |  | match |
| MOP-16 | storage_occupied_volume | m3 | 3.64e-05 | 3.64e-05 | 1.861610873e-14 | match |
| MOP-16 | battery_installation_verdict | verdict | true | true |  | match |
| MOP-16 | deployed_width | m | 0.0885 | 0.0885 | 1.568111617e-14 | match |
| MOP-16 | deployed_length | m | 0.1685 | 0.1685 | 0 | match |
| MOP-16 | deployed_footprint | m2 | 0.01491225 | 0.01491225 | 1.163287549e-14 | match |
| MOP-16 | deployed_plate_area | m2 | 0.017 | 0.017 | 0 | match |
| MOP-16 | deployed_layout_verdict | verdict | true | true |  | match |
| MOP-16 | published_pack_capacity | Ah | 3.8 | 3.8 | 0 | match |
| MOP-16 | published_pack_energy | Wh | 13.68 | 13.68 | 0 | match |
| MOP-16 | invalid_solar_series_0 | verdict | false | false |  | match |
| MOP-16 | invalid_battery_parallel_0 | verdict | false | false |  | match |
| MOP-16 | invalid_solar_series_-1 | verdict | false | false |  | match |
| MOP-16 | invalid_battery_parallel_-1 | verdict | false | false |  | match |
| MOP-16 | invalid_solar_series_2.5 | verdict | false | false |  | match |
| MOP-16 | invalid_battery_parallel_2.5 | verdict | false | false |  | match |
| MOP-16 | invalid_solar_series_True | verdict | false | false |  | match |
| MOP-16 | invalid_battery_parallel_True | verdict | false | false |  | match |
| MOP-16 | inconsistent_total_count | verdict | false | false |  | match |


### BIRDS-4: 09-converter-rails

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-17 | rail_power_3.3 | W | 1.65 | 1.65 | 0 | match |
| MOP-17 | terminal_battery_current_3.3 | A | 0.5092592593 | 0.5092592593 | 0 | match |
| MOP-17 | input_interval_3.3 | verdict | true | true |  | match |
| MOP-17 | output_voltage_3.3 | verdict | true | true |  | match |
| MOP-17 | output_current_3.3 | verdict | true | true |  | match |
| MOP-17 | rail_power_5.0 | W | 2 | 2 | 0 | match |
| MOP-17 | terminal_battery_current_5.0 | A | 0.6172839506 | 0.6172839506 | 0 | match |
| MOP-17 | input_interval_5.0 | verdict | true | true |  | match |
| MOP-17 | output_voltage_5.0 | verdict | true | true |  | match |
| MOP-17 | output_current_5.0 | verdict | true | true |  | match |
| MOP-17 | voltage_outside_tolerance | verdict | false | false |  | match |
| MOP-17 | over_output_current | verdict | false | false |  | match |
| MOP-17 | incompatible_converter_input | verdict | false | false |  | match |
| MOP-17 | uncharacterized_efficiency_current_unknown | A | unresolved | unresolved |  | expected unknown |


### BIRDS-4: 10-characteristics

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-18 | sample_VI_0 | W | 0 | 0 |  | match |
| MOP-18 | sample_VI_1 | W | 1.0885644 | 1.0885644 | 0 | match |
| MOP-18 | sample_VI_2 | W | 0 | 0 |  | match |
| MOP-18 | mpp_power | W | 1.0885644 | 1.0885644 | 0 | match |
| MOP-18 | mpp_voltage | V | 2.244 | 2.244 | 0 | match |
| MOP-18 | mpp_current | A | 0.4851 | 0.4851 | 0 | match |
| MOP-18 | voc | V | 2.512 | 2.512 | 0 | match |
| MOP-18 | isc | A | 0.5013 | 0.5013 | 0 | match |
| MOP-18 | curve_efficiency | 1 | 0.2638556372 | 0.2638556372 | 2.103845566e-14 | match |
| MOP-18 | tracking_limit | verdict | true | true |  | match |
| MOP-18 | absolute_limit | verdict | true | true |  | match |
| MOP-18 | source_limit | verdict | true | true |  | match |
| MOP-18 | purchased_panel_no_internal_count_repeat | W | 2.1771288 | 2.1771288 | 0 | match |
| MOP-18 | empty_curve_scalar_fallback | W | 1.0885644 | 1.0885644 | 0 | match |
| MOP-18 | reject_partial |  | unresolved | unresolved |  | expected error |
| MOP-18 | reject_duplicate_voltage |  | unresolved | unresolved |  | expected error |
| MOP-18 | reject_negative_current |  | unresolved | unresolved |  | expected error |
| MOP-18 | reject_nonfinite |  | unresolved | unresolved |  | expected error |
| MOP-18 | reject_partial_Maya_labelled_subset |  | unresolved | unresolved |  | expected error |
| MOP-18 | Maya_label_50mA | W | 0.257 | 0.25615 | 0.3307392996 | match |
| MOP-18 | Maya_label_100mA | W | 0.502 | 0.5022 | 0.03984063745 | match |


### BIRDS-4: 11-baseline-DET

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | DET_operating_voltage | V | 3.8 | 3.8 | 1.168655815e-14 | match |
| MOP-19 | DET_operating_current | A | 0.4875834225 | 0.4875834225 | 1.138495459e-14 | match |
| MOP-19 | DET_operating_power | W | 1.852817005 | 1.852817005 | 1.198416273e-14 | match |
| MOP-19 | DET_operating_efficiency | 1 | 0.2245508909 | 0.2245508909 | 1.236048341e-14 | match |
| MOP-19 | DET_mean_source_power | W | 1.70737087 | 1.70737087 | 1.300505993e-14 | match |
| MOP-19 | DET_mean_bus_power | W | 1.617509246 | 1.617509246 | 1.372756326e-14 | match |
| MOP-19 | DET_bus_delivery | verdict | true | true |  | match |
| MOP-19 | DET_electrical_window | verdict | true | true |  | match |


### BIRDS-4: 12-baseline-ideal-MPPT

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | MPPT_operating_voltage | V | 4.488 | 4.488 | 0 | match |
| MOP-19 | MPPT_operating_current | A | 0.4851 | 0.4851 | 0 | match |
| MOP-19 | MPPT_operating_power | W | 2.1771288 | 2.1771288 | 0 | match |
| MOP-19 | MPPT_operating_efficiency | 1 | 0.2638556372 | 0.2638556372 | 2.103845566e-14 | match |
| MOP-19 | MPPT_mean_source_power | W | 2.006224189 | 2.006224189 | 0 | match |
| MOP-19 | MPPT_mean_bus_power | W | 1.80560177 | 1.80560177 | 1.229754028e-14 | match |
| MOP-19 | MPPT_bus_delivery | verdict | true | true |  | match |
| MOP-19 | MPPT_electrical_window | verdict | true | true |  | match |


### BIRDS-4: 13-baseline-fixed-voltage

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | FIXED_VOLTAGE_operating_voltage | V | 4 | 4 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_current | A | 0.4868614973 | 0.4868614973 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_power | W | 1.947445989 | 1.947445989 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_efficiency | 1 | 0.2360193859 | 0.2360193859 | 1.175987113e-14 | match |
| MOP-19 | FIXED_VOLTAGE_mean_source_power | W | 1.794571479 | 1.794571479 | 1.237312682e-14 | match |
| MOP-19 | FIXED_VOLTAGE_mean_bus_power | W | 1.615114331 | 1.615114331 | 1.374791868e-14 | match |
| MOP-19 | FIXED_VOLTAGE_bus_delivery | verdict | true | true |  | match |
| MOP-19 | FIXED_VOLTAGE_electrical_window | verdict | true | true |  | match |


### BIRDS-4: 14-unflown-4S-pair

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | shared_4S_deployed_width | m | 0.0885 | 0.0885 | 1.568111617e-14 | match |
| MOP-19 | shared_4S_deployed_length | m | 0.1685 | 0.1685 | 0 | match |
| MOP-19 | shared_4S_deployed_footprint | m2 | 0.01491225 | 0.01491225 | 1.163287549e-14 | match |
| MOP-19 | shared_4S_deployed_plate_area | m2 | 0.017 | 0.017 | 0 | match |
| MOP-19 | shared_4S_deployed_layout_verdict | verdict | true | true |  | match |
| MOP-19 | DET_operating_voltage | V | 3.8 | 3.8 | 1.168655815e-14 | match |
| MOP-19 | DET_operating_current | A | 0.4944417112 | 0.4944417112 | 0 | match |
| MOP-19 | DET_operating_power | W | 1.878878503 | 1.878878503 | 1.181793312e-14 | match |
| MOP-19 | DET_operating_efficiency | 1 | 0.1138546981 | 0.1138546981 | 1.218903395e-14 | match |
| MOP-19 | DET_mean_source_power | W | 1.73138654 | 1.73138654 | 2.564933939e-14 | match |
| MOP-19 | DET_mean_bus_power | W | 1.640260933 | 1.640260933 | 2.707430269e-14 | match |
| MOP-19 | DET_bus_delivery | verdict | true | true |  | match |
| MOP-19 | DET_electrical_window | verdict | true | true |  | match |
| MOP-19 | MPPT_operating_voltage | V | 8.976 | 8.976 | 0 | match |
| MOP-19 | MPPT_operating_current | A | 0.4851 | 0.4851 | 0 | match |
| MOP-19 | MPPT_operating_power | W | 4.3542576 | 4.3542576 | 0 | match |
| MOP-19 | MPPT_operating_efficiency | 1 | 0.2638556372 | 0.2638556372 | 2.103845566e-14 | match |
| MOP-19 | MPPT_mean_source_power | W | 4.012448378 | 4.012448378 | 0 | match |
| MOP-19 | MPPT_mean_bus_power | W | 3.611203541 | 3.611203541 | 1.229754028e-14 | match |
| MOP-19 | MPPT_bus_delivery | verdict | true | true |  | match |
| MOP-19 | MPPT_electrical_window | verdict | true | true |  | match |
| MOP-19 | FIXED_VOLTAGE_operating_voltage | V | 8 | 8 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_current | A | 0.4868614973 | 0.4868614973 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_power | W | 3.894891979 | 3.894891979 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_efficiency | 1 | 0.2360193859 | 0.2360193859 | 1.175987113e-14 | match |
| MOP-19 | FIXED_VOLTAGE_mean_source_power | W | 3.589142958 | 3.589142958 | 1.237312682e-14 | match |
| MOP-19 | FIXED_VOLTAGE_mean_bus_power | W | 3.230228662 | 3.230228662 | 1.374791868e-14 | match |
| MOP-19 | FIXED_VOLTAGE_bus_delivery | verdict | true | true |  | match |
| MOP-19 | FIXED_VOLTAGE_electrical_window | verdict | true | true |  | match |


### BIRDS-4: 15-operating-point-contract

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | exact | A | 0.4851 | 0.4851 | 0 | match |
| MOP-19 | interpolation | A | 0.48834 | 0.48834 | 0 | match |
| MOP-19 | interpolation_not_accepted | A | unresolved | unresolved |  | expected error |
| MOP-19 | out_of_range | A | unresolved | unresolved |  | expected error |
| MOP-19 | invalid_selector | V | unresolved | unresolved |  | expected error |
| MOP-19 | unknown_selector | V | unresolved | unresolved |  | expected unknown |


### BIRDS-4: 16-normal-extrema

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-20 | Vmin | V | [3.9,4.2] | [3.9,4.2] |  | match |
| MOP-20 | Iminmax | A | [0.2,1.5] | [0.2,1.5] |  | match |
| MOP-20 | voltage_normal_no_trip | verdict | true | true |  | match |
| MOP-20 | rail_normal_no_trip | verdict | true | true |  | match |
| MOP-20 | bound_current_extrema | A | [0.19047619047619047,1.5789473684210527] | [0.19047619047619047,1.5789473684210527] |  | match |
| MOP-20 | conservative_corner_no_trip | verdict | true | true |  | match |
| MOP-20 | independent_PV_corner_minimum | A | 0.1904761905 | 0.1904761905 | 0 | match |
| MOP-20 | independent_PV_corner_maximum | A | 1.578947368 | 1.578947368 | 0 | match |
| MOP-20 | source_rail_threshold_2.0 | verdict | true | true |  | match |
| MOP-20 | source_rail_threshold_3.0 | verdict | true | true |  | match |
| MOP-20 | source_rail_threshold_4.0 | verdict | true | true |  | match |


### BIRDS-4: 17-threshold-boundaries

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-20 | UV_0.99 | verdict | false | false |  | match |
| MOP-20 | UV_1.0 | verdict | false | false |  | match |
| MOP-20 | UV_1.01 | verdict | true | true |  | match |
| MOP-20 | OV_0.99 | verdict | true | true |  | match |
| MOP-20 | OV_1.0 | verdict | false | false |  | match |
| MOP-20 | OV_1.01 | verdict | false | false |  | match |
| MOP-20 | OC_0.99 | verdict | true | true |  | match |
| MOP-20 | OC_1.0 | verdict | false | false |  | match |
| MOP-20 | OC_1.01 | verdict | false | false |  | match |
| MOP-20 | Unreg2_OC_0.99 | verdict | true | true |  | match |
| MOP-20 | Unreg2_OC_1.0 | verdict | false | false |  | match |
| MOP-20 | Unreg2_OC_1.01 | verdict | false | false |  | match |
| MOP-20 | Unreg1_OC_0.99 | verdict | true | true |  | match |
| MOP-20 | Unreg1_OC_1.0 | verdict | false | false |  | match |
| MOP-20 | Unreg1_OC_1.01 | verdict | false | false |  | match |
| MOP-20 | unknown_voltage_samples | verdict | unresolved | unresolved |  | expected unknown |
| MOP-20 | empty_voltage_samples | verdict | unresolved | unresolved |  | expected error |
| MOP-20 | nonfinite_voltage_samples | verdict | unresolved | unresolved |  | expected error |
| MOP-20 | negative_current_magnitude_fails | verdict | false | false |  | match |
| MOP-20 | empty_current_samples | verdict | unresolved | unresolved |  | expected error |
| MOP-20 | unknown_current_samples | verdict | unresolved | unresolved |  | expected unknown |
| MOP-20 | unknown_threshold | verdict | unresolved | unresolved |  | expected unknown |


### BIRDS-4: 18-unknown-invalid-feasibility

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-16 | unknown_series_count | cell | unresolved | unresolved |  | expected unknown |
| MOP-15 | unknown_installation_allocation | verdict | unresolved | unresolved |  | expected unknown |
| MOP-14b | unknown_life_fit | J | unresolved | unresolved |  | expected unknown |
| MOP-14b | unknown_energy_retention | J | unresolved | unresolved |  | expected unknown |
| MOP-14a | deliberately_inadequate_delivery | verdict | false | false |  | match |
| MOP-14a | unknown_orbit | s | unresolved | unresolved |  | expected unknown |
| MOP-14a | invalid_perigee |  | unresolved | unresolved |  | expected error |
| MOP-14b | unsupported_cycle_fit |  | unresolved | unresolved |  | expected error |
| MOP-14b | invalid_retention |  | unresolved | unresolved |  | expected error |
| MOP-14b | invalid_packing |  | unresolved | unresolved |  | expected error |
| MOP-20 | invalid_current_voltage_interval |  | unresolved | unresolved |  | expected error |


### OreSat: 01-mass-boundaries

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-12 | published_battery_module_mass | kg | 0.416 | 0.416 | 0 | match |
| MOP-12 | published_solar_module_mass | kg | 0.252 | 0.252 | 0 | match |
| MOP-12 | assumed_solar_module_volume | m3 | 0.00024 | 0.00024 | 2.258754526e-14 | match |
| MOP-12 | mass | kg | 0.728 | 0.728 | 0 | match |
| MOP-12 | volume | m3 | 0.00045 | 0.00045 | 2.409338161e-14 | match |
| MOP-12 | mass_margin | kg | 0.072 | 0.072 | 9.637352644e-14 | match |
| MOP-12 | volume_margin | m3 | 5e-05 | 5e-05 | 1.76182853e-13 | match |
| MOP-12 | mass_allocation | verdict | true | true |  | match |
| MOP-12 | volume_allocation | verdict | true | true |  | match |
| MOP-12 | aggregate_replacement_no_double_count | kg | 0.728 | 0.728 | 0 | match |
| MOP-12 | zero_margin_passes | verdict | true | true |  | match |
| MOP-12 | negative_margin_fails | verdict | false | false |  | match |
| MOP-12 | unknown_mass_total | kg | unresolved | unresolved |  | expected unknown |
| MOP-12 | unknown_mass_margin | kg | unresolved | unresolved |  | expected unknown |
| MOP-12 | volume_unaffected_by_unknown_mass | m3 | 0.00045 | 0.00045 | 2.409338161e-14 | match |
| MOP-12 | unknown_mass_allocation | verdict | unresolved | unresolved |  | expected unknown |
| MOP-12 | unknown_volume_total | m3 | unresolved | unresolved |  | expected unknown |
| MOP-12 | unknown_volume_margin | m3 | unresolved | unresolved |  | expected unknown |
| MOP-12 | unknown_volume_allocation | verdict | unresolved | unresolved |  | expected unknown |
| MOP-12 | mass_unit_record |  | kg | kg |  | match |
| MOP-12 | volume_unit_record |  | m3 | m3 |  | match |


### OreSat: 02-states-modes-circular

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-14a | period | s | 5738.81857 | 5738.81857 | 1.584811736e-14 | match |
| MOP-14a | sunlight | s | 3602.217256 | 3602.201638 | 0.0004335530857 | match |
| MOP-14a | eclipse | s | 2136.601314 | 2136.616931 | 0.0007309517207 | match |
| MOP-14b | projection | 1 | 1 | 1 | 0 | match |
| MOP-14b | projected_duration | s | 3602.217256 | 3602.201638 | 0.0004335530857 | match |
| MOP-14a | main_state_power | W | 0.198 | 0.198 | 1.401796748e-14 | match |
| MOP-14a | receiver_state_power | W | 0.132 | 0.132 | 0 | match |
| MOP-14a | payload_state_power | W | 1 | 1 | 0 | match |
| MOP-14a | sunlight_mode_aggregation | W | 0.53 | 0.53 | 0 | match |
| MOP-14a | sunlight_EPS_consumption_boundary | W | 0 | 0 |  | match |
| MOP-14a | sunlight_mean | W | 0.53 | 0.53 | 0 | match |
| MOP-14a | sunlight_energy | J | 1909.175146 | 1909.166868 | 0.0004335530857 | match |
| MOP-14a | sunlight_delivery | verdict | true | true |  | match |
| MOP-14a | eclipse_mode_aggregation | W | 0.43 | 0.43 | 0 | match |
| MOP-14a | eclipse_EPS_consumption_boundary | W | 0 | 0 |  | match |
| MOP-14a | eclipse_mean | W | 0.43 | 0.43 | 0 | match |
| MOP-14a | eclipse_energy | J | 918.7385648 | 918.7452804 | 0.0007309517207 | match |
| MOP-14a | eclipse_delivery | verdict | true | true |  | match |
| MOP-14a | minimum_panel_power | W | 0.9635935073 | 0.9635974674 | 0.0004109699657 | match |
| MOP-14a | standby_surplus | mWh | 1011 | 1011 | 0 | match |
| MOP-14a | flight_computer_10min | Wh | 0.18 | 0.18 | 1.541976423e-14 | match |
| MOP-14a | heater_6V | W | 1.47 | 1.47 | 0 | match |


### OreSat: 03-eccentric-nadir

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-14a | period | s | 5738.81857 | 5738.81857 | 1.584811736e-14 | match |
| MOP-14a | sunlight | s | 3638.667195 | 3638.662372 | 0.0001325717736 | match |
| MOP-14a | eclipse | s | 2100.151374 | 2100.156198 | 0.0002296903784 | match |
| MOP-14b | projection | 1 | 0.4354719315 | 0.4354725088 | 0.0001325741848 | match |
| MOP-14b | projected_duration | s | 1584.537432 | 1584.537432 | 2.235398495e-09 | match |
| MOP-14a | minimum_panel_power | W | 0.9544436513 | 0.9544448501 | 0.0001255997285 | match |
| MOP-14b | nontrivial_projection_generation | W | 0.8477765834 | 0.8477777073 | 0.0001325741848 | match |
| MOP-14b | nadir_generation_verdict | verdict | false | false |  | match |


### OreSat: 04-eclipse-free

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-14a | period | s | 5738.81857 | 5738.81857 | 1.584811736e-14 | match |
| MOP-14a | sunlight | s | 5738.81857 | 5738.81857 | 1.584811736e-14 | match |
| MOP-14a | eclipse | s | 0 | 0 |  | match |
| MOP-14b | projection | 1 | 1 | 1 | 0 | match |
| MOP-14b | projected_duration | s | 5738.81857 | 5738.81857 | 1.584811736e-14 | match |
| MOP-14a | zero_eclipse_demand | verdict | true | true |  | match |
| MOP-14a | zero_eclipse_energy | J | 0 | 0 |  | match |
| MOP-14a | unused_eclipse_efficiency_identity | 1 | 1 | 1 | 0 | match |
| MOP-14a | minimum_panel_power | W | 0.6235294118 | 0.6235294118 | 0 | match |


### OreSat: 05-baseline-sizing

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-14b | cell_power | W | 1.056321 | 1.056321 | 0 | match |
| MOP-14b | array_mpp | W | 2.112642 | 2.112642 | 0 | match |
| MOP-14b | array_voltage | V | 4.86 | 4.86 | 0 | match |
| MOP-14b | array_current | A | 0.4347 | 0.4347 | 0 | match |
| MOP-14b | array_voc | V | 5.5 | 5.5 | 0 | match |
| MOP-14b | array_isc | A | 0.4518 | 0.4518 | 0 | match |
| MOP-14b | active_area | m2 | 0.0054 | 0.0054 | 0 | match |
| MOP-14b | panel_area | m2 | 0.00675 | 0.00675 | 0 | match |
| MOP-14b | required_area | m2 | 0.002672799466 | 0.002672810451 | 0.0004109699657 | match |
| MOP-14b | effective_area | m2 | 0.002462984708 | 0.00246299483 | 0.0004109699657 | match |
| MOP-14b | tumbling_area | m2 | 0.009579309989 | 0.009579349357 | 0.0004109699657 | match |
| MOP-14b | generation_efficiency | 1 | 0.2861960497 | 0.2861960497 | 0 | match |
| MOP-14b | density | W/m2 | 360.518445 | 360.518445 | 1.576713193e-14 | match |
| MOP-14b | available_power | W | 1.946799603 | 1.946799603 | 1.140562206e-14 | match |
| MOP-14b | source_energy | J | 7012.795124 | 7012.76472 | 0.0004335530857 | match |
| MOP-14b | fractional_count | cell | 0.9122165585 | 0.9122203075 | 0.0004109699657 | match |
| MOP-14b | required_count | cell | 1 | 1 |  | match |
| MOP-14b | minimum_solar_parallel | string | 1 | 1 |  | match |
| MOP-14b | cycles | cycle | 10997.94308 | 10997.94308 | 1.653936004e-14 | match |
| MOP-14b | dod | 1 | 0.1818521868 | 0.1818521868 | 1.526271204e-14 | match |
| MOP-14b | required_battery_energy | J | 6062.540667 | 6062.584982 | 0.0007309517207 | match |
| MOP-14b | minimum_battery_parallel | string | 1 | 1 |  | match |
| MOP-14b | pack_wh | Wh | 18.72 | 18.72 | 0 | match |
| MOP-14b | pack_ah | Ah | 2.6 | 2.6 | 0 | match |
| MOP-14b | pack_j | J | 67392 | 67392 | 0 | match |
| MOP-14b | eol_j | J | 53913.6 | 53913.6 | 1.349558852e-14 | match |
| MOP-14b | eol_ah | Ah | 2.08 | 2.08 | 0 | match |
| MOP-14b | battery_voltage | V | 7.2 | 7.2 | 0 | match |
| MOP-14b | battery_min | V | 5.5 | 5.5 | 0 | match |
| MOP-14b | battery_max | V | 8.4 | 8.4 | 0 | match |
| MOP-14b | charge_limit | A | 1.25 | 1.25 | 0 | match |
| MOP-14b | discharge_limit | A | 5 | 5 | 0 | match |
| MOP-14b | solar_power_verdict | verdict | true | true |  | match |
| MOP-14b | solar_count_verdict | verdict | true | true |  | match |
| MOP-14b | battery_energy_verdict | verdict | true | true |  | match |
| MOP-14b | solar_configuration_verdict | verdict | true | true |  | match |
| MOP-14b | battery_configuration_verdict | verdict | true | true |  | match |
| MOP-14b | area_fit_verdict | verdict | true | true |  | match |
| MOP-14b | active_area_verdict | verdict | true | true |  | match |
| MOP-14b | generation_verdict | verdict | true | true |  | match |
| MOP-14b | tracking_voltage_verdict | verdict | true | true |  | match |
| MOP-14b | absolute_voltage_verdict | verdict | true | true |  | match |
| MOP-14b | source_current_verdict | verdict | true | true |  | match |
| MOP-14b | battery_receiving_verdict | verdict | true | true |  | match |
| MOP-14b | charge_current_verdict | verdict | true | true |  | match |
| MOP-14b | discharge_current_verdict | verdict | true | true |  | match |
| MOP-14b | storage_occupied_volume | m3 | 0.000112 | 0.000112 | 1.210047068e-14 | match |
| MOP-14b | battery_installation_verdict | verdict | true | true |  | match |
| MOP-14b | independent_packs_energy | Wh | 37.44 | 37.44 | 0 | match |
| MOP-14b | independent_packs_Ah_bookkeeping | Ah | 5.2 | 5.2 | 0 | match |
| MOP-14b | BOL_cell_power | W | 1.17369 | 1.17369 | 1.891850531e-14 | match |
| MOP-14b | EOL_efficiency_once | 1 | 0.2861960497 | 0.2861960497 | 0 | match |
| MOP-14b | published_BOL_module_power | W | 2.34 | 2.34738 | 0.3153846154 | match |
| MOP-14b | published_hot_module_power | W | 2.1 | 2.10105 | 0.05 | match |
| MOP-15 | baseline_charger | verdict | true | true |  | match |
| MOP-14b | BOL_case_minimum_panel_power | W | 0.9635935073 | 0.9635974674 | 0.0004109699657 | match |
| MOP-14b | BOL_case_fractional_count | cell | 0.8209949027 | 0.8209982767 | 0.0004109699657 | match |
| MOP-14b | BOL_case_required_count | cell | 1 | 1 |  | match |
| MOP-14b | BOL_case_minimum_solar_parallel | string | 1 | 1 |  | match |
| MOP-14b | BOL_case_cell_power | W | 1.17369 | 1.17369 | 1.891850531e-14 | match |
| MOP-14b | BOL_case_array_mpp | W | 2.34738 | 2.34738 | 1.891850531e-14 | match |
| MOP-14b | BOL_case_array_voltage | V | 4.86 | 4.86 | 0 | match |
| MOP-14b | BOL_case_array_current | A | 0.483 | 0.483 | 0 | match |
| MOP-14b | BOL_case_array_voc | V | 5.5 | 5.5 | 0 | match |
| MOP-14b | BOL_case_array_isc | A | 0.502 | 0.502 | 0 | match |
| MOP-14b | BOL_case_generation_efficiency | 1 | 0.3179956108 | 0.3179956108 | 1.745657781e-14 | match |
| MOP-14b | BOL_case_active_area | m2 | 0.0054 | 0.0054 | 0 | match |
| MOP-14b | BOL_case_panel_area | m2 | 0.00675 | 0.00675 | 0 | match |
| MOP-14b | BOL_case_required_area | m2 | 0.002405519519 | 0.002405529405 | 0.0004109699657 | match |
| MOP-14b | BOL_case_effective_area | m2 | 0.002216686237 | 0.002216695347 | 0.0004109699657 | match |
| MOP-14b | BOL_case_density | W/m2 | 400.57605 | 400.57605 | 0 | match |
| MOP-14b | BOL_case_available_power | W | 2.16311067 | 2.16311067 | 0 | match |
| MOP-14b | BOL_case_source_energy | J | 7791.994582 | 7791.9608 | 0.0004335530857 | match |
| MOP-14b | BOL_case_solar_power_verdict | verdict | true | true |  | match |
| MOP-14b | BOL_case_solar_count_verdict | verdict | true | true |  | match |
| MOP-14b | BOL_case_area_fit_verdict | verdict | true | true |  | match |
| MOP-14b | BOL_case_active_area_verdict | verdict | true | true |  | match |
| MOP-14b | BOL_case_generation_verdict | verdict | true | true |  | match |


### OreSat: 06-silicon-technology

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-15 | cell_power | W | 0.024084 | 0.024084 | 0 | match |
| MOP-15 | array_mpp | W | 0.96336 | 0.96336 | 0 | match |
| MOP-15 | array_voltage | V | 17.84 | 17.84 | 0 | match |
| MOP-15 | array_current | A | 0.054 | 0.054 | 1.284980353e-14 | match |
| MOP-15 | array_voc | V | 22.12 | 22.12 | 0 | match |
| MOP-15 | array_isc | A | 0.0567 | 0.0567 | 0 | match |
| MOP-15 | active_area | m2 | 0.003668 | 0.003668 | 1.182336066e-14 | match |
| MOP-15 | panel_area | m2 | 0.00736 | 0.00736 | 1.178480622e-14 | match |
| MOP-15 | required_area | m2 | 0.003966868789 | 0.003966885091 | 0.0004109699657 | match |
| MOP-15 | effective_area | m2 | 0.003655469589 | 0.003655484612 | 0.0004109699657 | match |
| MOP-15 | tumbling_area | m2 | 0.0228220242 | 0.02282211799 | 0.0004109699657 | match |
| MOP-15 | generation_efficiency | 1 | 0.192833363 | 0.192833363 | 0 | match |
| MOP-15 | density | W/m2 | 242.9103554 | 242.9103554 | 1.170049312e-14 | match |
| MOP-15 | available_power | W | 0.8909951836 | 0.8909951836 | 1.24604829e-14 | match |
| MOP-15 | source_energy | J | 3209.558225 | 3209.54431 | 0.0004335530857 | match |
| MOP-15 | fractional_count | cell | 40.00969554 | 40.00985996 | 0.0004109699657 | match |
| MOP-15 | required_count | cell | 41 | 41 |  | match |
| MOP-15 | minimum_solar_parallel | string | 11 | 11 |  | match |
| MOP-15 | cycles | cycle | 10997.94308 | 10997.94308 | 1.653936004e-14 | match |
| MOP-15 | dod | 1 | 0.1818521868 | 0.1818521868 | 1.526271204e-14 | match |
| MOP-15 | required_battery_energy | J | 6062.540667 | 6062.584982 | 0.0007309517207 | match |
| MOP-15 | minimum_battery_parallel | string | 1 | 1 |  | match |
| MOP-15 | pack_wh | Wh | 18.72 | 18.72 | 0 | match |
| MOP-15 | pack_ah | Ah | 2.6 | 2.6 | 0 | match |
| MOP-15 | pack_j | J | 67392 | 67392 | 0 | match |
| MOP-15 | eol_j | J | 53913.6 | 53913.6 | 1.349558852e-14 | match |
| MOP-15 | eol_ah | Ah | 2.08 | 2.08 | 0 | match |
| MOP-15 | battery_voltage | V | 7.2 | 7.2 | 0 | match |
| MOP-15 | battery_min | V | 5.5 | 5.5 | 0 | match |
| MOP-15 | battery_max | V | 8.4 | 8.4 | 0 | match |
| MOP-15 | charge_limit | A | 1.25 | 1.25 | 0 | match |
| MOP-15 | discharge_limit | A | 5 | 5 | 0 | match |
| MOP-15 | solar_power_verdict | verdict | false | false |  | match |
| MOP-15 | solar_count_verdict | verdict | false | false |  | match |
| MOP-15 | battery_energy_verdict | verdict | true | true |  | match |
| MOP-15 | solar_configuration_verdict | verdict | true | true |  | match |
| MOP-15 | battery_configuration_verdict | verdict | true | true |  | match |
| MOP-15 | area_fit_verdict | verdict | true | true |  | match |
| MOP-15 | active_area_verdict | verdict | false | false |  | match |
| MOP-15 | generation_verdict | verdict | false | false |  | match |
| MOP-15 | tracking_voltage_verdict | verdict | false | false |  | match |
| MOP-15 | absolute_voltage_verdict | verdict | false | false |  | match |
| MOP-15 | source_current_verdict | verdict | true | true |  | match |
| MOP-15 | battery_receiving_verdict | verdict | true | true |  | match |
| MOP-15 | charge_current_verdict | verdict | true | true |  | match |
| MOP-15 | discharge_current_verdict | verdict | true | true |  | match |
| MOP-15 | storage_occupied_volume | m3 | 0.000112 | 0.000112 | 1.210047068e-14 | match |
| MOP-15 | battery_installation_verdict | verdict | true | true |  | match |
| MOP-15 | independent_packs_energy | Wh | 37.44 | 37.44 | 0 | match |
| MOP-15 | independent_packs_Ah_bookkeeping | Ah | 5.2 | 5.2 | 0 | match |


### OreSat: 07-battery-chemistry

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-15 | cell_power | W | 1.056321 | 1.056321 | 0 | match |
| MOP-15 | array_mpp | W | 2.112642 | 2.112642 | 0 | match |
| MOP-15 | array_voltage | V | 4.86 | 4.86 | 0 | match |
| MOP-15 | array_current | A | 0.4347 | 0.4347 | 0 | match |
| MOP-15 | array_voc | V | 5.5 | 5.5 | 0 | match |
| MOP-15 | array_isc | A | 0.4518 | 0.4518 | 0 | match |
| MOP-15 | active_area | m2 | 0.0054 | 0.0054 | 0 | match |
| MOP-15 | panel_area | m2 | 0.00675 | 0.00675 | 0 | match |
| MOP-15 | required_area | m2 | 0.002672799466 | 0.002672810451 | 0.0004109699657 | match |
| MOP-15 | effective_area | m2 | 0.002462984708 | 0.00246299483 | 0.0004109699657 | match |
| MOP-15 | tumbling_area | m2 | 0.009579309989 | 0.009579349357 | 0.0004109699657 | match |
| MOP-15 | generation_efficiency | 1 | 0.2861960497 | 0.2861960497 | 0 | match |
| MOP-15 | density | W/m2 | 360.518445 | 360.518445 | 1.576713193e-14 | match |
| MOP-15 | available_power | W | 1.946799603 | 1.946799603 | 1.140562206e-14 | match |
| MOP-15 | source_energy | J | 7012.795124 | 7012.76472 | 0.0004335530857 | match |
| MOP-15 | fractional_count | cell | 0.9122165585 | 0.9122203075 | 0.0004109699657 | match |
| MOP-15 | required_count | cell | 1 | 1 |  | match |
| MOP-15 | minimum_solar_parallel | string | 1 | 1 |  | match |
| MOP-15 | cycles | cycle | 10997.94308 | 10997.94308 | 1.653936004e-14 | match |
| MOP-15 | dod | 1 | 0.1818521868 | 0.1818521868 | 1.526271204e-14 | match |
| MOP-15 | required_battery_energy | J | 6062.540667 | 6062.584982 | 0.0007309517207 | match |
| MOP-15 | minimum_battery_parallel | string | 1 | 1 |  | match |
| MOP-15 | pack_wh | Wh | 14.52 | 14.52 | 0 | match |
| MOP-15 | pack_ah | Ah | 1.1 | 1.1 | 0 | match |
| MOP-15 | pack_j | J | 52272 | 52272 | 0 | match |
| MOP-15 | eol_j | J | 41817.6 | 41817.6 | 1.739927115e-14 | match |
| MOP-15 | eol_ah | Ah | 0.88 | 0.88 | 1.261617073e-14 | match |
| MOP-15 | battery_voltage | V | 13.2 | 13.2 | 0 | match |
| MOP-15 | battery_min | V | 8 | 8 | 0 | match |
| MOP-15 | battery_max | V | 14.4 | 14.4 | 0 | match |
| MOP-15 | charge_limit | A | 0.5 | 0.5 | 0 | match |
| MOP-15 | discharge_limit | A | 3 | 3 | 0 | match |
| MOP-15 | solar_power_verdict | verdict | true | true |  | match |
| MOP-15 | solar_count_verdict | verdict | true | true |  | match |
| MOP-15 | battery_energy_verdict | verdict | true | true |  | match |
| MOP-15 | solar_configuration_verdict | verdict | true | true |  | match |
| MOP-15 | battery_configuration_verdict | verdict | true | true |  | match |
| MOP-15 | area_fit_verdict | verdict | true | true |  | match |
| MOP-15 | active_area_verdict | verdict | true | true |  | match |
| MOP-15 | generation_verdict | verdict | true | true |  | match |
| MOP-15 | tracking_voltage_verdict | verdict | true | true |  | match |
| MOP-15 | absolute_voltage_verdict | verdict | true | true |  | match |
| MOP-15 | source_current_verdict | verdict | true | true |  | match |
| MOP-15 | battery_receiving_verdict | verdict | false | false |  | match |
| MOP-15 | charge_current_verdict | verdict | true | true |  | match |
| MOP-15 | discharge_current_verdict | verdict | true | true |  | match |
| MOP-15 | storage_occupied_volume | m3 | 0.000184 | 0.000184 | 0 | match |
| MOP-15 | battery_installation_verdict | verdict | false | false |  | match |
| MOP-15 | independent_packs_energy | Wh | 29.04 | 29.04 | 0 | match |
| MOP-15 | independent_packs_Ah_bookkeeping | Ah | 2.2 | 2.2 | 0 | match |
| MOP-15 | unchanged_charger_incompatible | verdict | false | false |  | match |
| MOP-15 | explicit_new_charger_compatible | verdict | true | true |  | match |


### OreSat: 08-integer-configurations

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-16 | cell_power | W | 1.056321 | 1.056321 | 0 | match |
| MOP-16 | array_mpp | W | 4.225284 | 4.225284 | 0 | match |
| MOP-16 | array_voltage | V | 9.72 | 9.72 | 0 | match |
| MOP-16 | array_current | A | 0.4347 | 0.4347 | 0 | match |
| MOP-16 | array_voc | V | 11 | 11 | 0 | match |
| MOP-16 | array_isc | A | 0.4518 | 0.4518 | 0 | match |
| MOP-16 | active_area | m2 | 0.0108 | 0.0108 | 0 | match |
| MOP-16 | panel_area | m2 | 0.0135 | 0.0135 | 0 | match |
| MOP-16 | required_area | m2 | 0.002672799466 | 0.002672810451 | 0.0004109699657 | match |
| MOP-16 | effective_area | m2 | 0.002462984708 | 0.00246299483 | 0.0004109699657 | match |
| MOP-16 | tumbling_area | m2 | 0.009579309989 | 0.009579349357 | 0.0004109699657 | match |
| MOP-16 | generation_efficiency | 1 | 0.2861960497 | 0.2861960497 | 0 | match |
| MOP-16 | density | W/m2 | 360.518445 | 360.518445 | 1.576713193e-14 | match |
| MOP-16 | available_power | W | 3.893599206 | 3.893599206 | 1.140562206e-14 | match |
| MOP-16 | source_energy | J | 14025.59025 | 14025.52944 | 0.0004335530857 | match |
| MOP-16 | fractional_count | cell | 0.9122165585 | 0.9122203075 | 0.0004109699657 | match |
| MOP-16 | required_count | cell | 1 | 1 |  | match |
| MOP-16 | minimum_solar_parallel | string | 1 | 1 |  | match |
| MOP-16 | cycles | cycle | 10997.94308 | 10997.94308 | 1.653936004e-14 | match |
| MOP-16 | dod | 1 | 0.1818521868 | 0.1818521868 | 1.526271204e-14 | match |
| MOP-16 | required_battery_energy | J | 6062.540667 | 6062.584982 | 0.0007309517207 | match |
| MOP-16 | minimum_battery_parallel | string | 1 | 1 |  | match |
| MOP-16 | pack_wh | Wh | 28.08 | 28.08 | 0 | match |
| MOP-16 | pack_ah | Ah | 2.6 | 2.6 | 0 | match |
| MOP-16 | pack_j | J | 101088 | 101088 | 0 | match |
| MOP-16 | eol_j | J | 80870.4 | 80870.4 | 1.799411803e-14 | match |
| MOP-16 | eol_ah | Ah | 2.08 | 2.08 | 0 | match |
| MOP-16 | battery_voltage | V | 10.8 | 10.8 | 0 | match |
| MOP-16 | battery_min | V | 8.25 | 8.25 | 0 | match |
| MOP-16 | battery_max | V | 12.6 | 12.6 | 1.409807015e-14 | match |
| MOP-16 | charge_limit | A | 1.25 | 1.25 | 0 | match |
| MOP-16 | discharge_limit | A | 5 | 5 | 0 | match |
| MOP-16 | solar_power_verdict | verdict | true | true |  | match |
| MOP-16 | solar_count_verdict | verdict | true | true |  | match |
| MOP-16 | battery_energy_verdict | verdict | true | true |  | match |
| MOP-16 | solar_configuration_verdict | verdict | true | true |  | match |
| MOP-16 | battery_configuration_verdict | verdict | true | true |  | match |
| MOP-16 | area_fit_verdict | verdict | true | true |  | match |
| MOP-16 | active_area_verdict | verdict | true | true |  | match |
| MOP-16 | generation_verdict | verdict | true | true |  | match |
| MOP-16 | tracking_voltage_verdict | verdict | true | true |  | match |
| MOP-16 | absolute_voltage_verdict | verdict | true | true |  | match |
| MOP-16 | source_current_verdict | verdict | true | true |  | match |
| MOP-16 | battery_receiving_verdict | verdict | false | false |  | match |
| MOP-16 | charge_current_verdict | verdict | true | true |  | match |
| MOP-16 | discharge_current_verdict | verdict | true | true |  | match |
| MOP-16 | storage_occupied_volume | m3 | 0.000148 | 0.000148 | 0 | match |
| MOP-16 | battery_installation_verdict | verdict | true | true |  | match |
| MOP-16 | independent_packs_energy | Wh | 56.16 | 56.16 | 0 | match |
| MOP-16 | independent_packs_Ah_bookkeeping | Ah | 5.2 | 5.2 | 0 | match |
| MOP-16 | deployed_width | m | 0.0876 | 0.0876 | 1.584222352e-14 | match |
| MOP-16 | deployed_length | m | 0.1464 | 0.1464 | 0 | match |
| MOP-16 | deployed_footprint | m2 | 0.01282464 | 0.01282464 | 1.352648867e-14 | match |
| MOP-16 | deployed_plate_area | m2 | 0.017 | 0.017 | 0 | match |
| MOP-16 | deployed_layout_verdict | verdict | true | true |  | match |
| MOP-16 | published_card_energy | Wh | 37.4 | 37.44 | 0.1069518717 | match |
| MOP-16 | historical_2019_energy | Wh | 95.04 | 95.04 | 1.495249865e-14 | match |
| MOP-16 | invalid_solar_series_0 | verdict | false | false |  | match |
| MOP-16 | invalid_battery_parallel_0 | verdict | false | false |  | match |
| MOP-16 | invalid_solar_series_-1 | verdict | false | false |  | match |
| MOP-16 | invalid_battery_parallel_-1 | verdict | false | false |  | match |
| MOP-16 | invalid_solar_series_2.5 | verdict | false | false |  | match |
| MOP-16 | invalid_battery_parallel_2.5 | verdict | false | false |  | match |
| MOP-16 | invalid_solar_series_True | verdict | false | false |  | match |
| MOP-16 | invalid_battery_parallel_True | verdict | false | false |  | match |
| MOP-16 | inconsistent_total_count | verdict | false | false |  | match |


### OreSat: 09-converter-rails

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-17 | rail_power_3.3 | W | 1.65 | 1.65 | 0 | match |
| MOP-17 | terminal_battery_current_3.3 | A | 0.2546296296 | 0.2546296296 | 2.180074303e-14 | match |
| MOP-17 | input_interval_3.3 | verdict | true | true |  | match |
| MOP-17 | output_voltage_3.3 | verdict | true | true |  | match |
| MOP-17 | output_current_3.3 | verdict | true | true |  | match |
| MOP-17 | rail_power_5.0 | W | 2 | 2 | 0 | match |
| MOP-17 | terminal_battery_current_5.0 | A | 0.3086419753 | 0.3086419753 | 0 | match |
| MOP-17 | input_interval_5.0 | verdict | true | true |  | match |
| MOP-17 | output_voltage_5.0 | verdict | true | true |  | match |
| MOP-17 | output_current_5.0 | verdict | true | true |  | match |
| MOP-17 | voltage_outside_tolerance | verdict | false | false |  | match |
| MOP-17 | over_output_current | verdict | false | false |  | match |
| MOP-17 | incompatible_converter_input | verdict | false | false |  | match |
| MOP-17 | uncharacterized_efficiency_current_unknown | A | unresolved | unresolved |  | expected unknown |
| MOP-17 | historical_SPV1040_rejection | verdict | false | false |  | match |


### OreSat: 10-characteristics

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-18 | sample_VI_0 | W | 0 | 0 |  | match |
| MOP-18 | sample_VI_1 | W | 1.056321 | 1.056321 | 0 | match |
| MOP-18 | sample_VI_2 | W | 0 | 0 |  | match |
| MOP-18 | mpp_power | W | 1.056321 | 1.056321 | 0 | match |
| MOP-18 | mpp_voltage | V | 2.43 | 2.43 | 0 | match |
| MOP-18 | mpp_current | A | 0.4347 | 0.4347 | 0 | match |
| MOP-18 | voc | V | 2.75 | 2.75 | 0 | match |
| MOP-18 | isc | A | 0.4518 | 0.4518 | 0 | match |
| MOP-18 | curve_efficiency | 1 | 0.2861960497 | 0.2861960497 | 0 | match |
| MOP-18 | tracking_limit | verdict | true | true |  | match |
| MOP-18 | absolute_limit | verdict | true | true |  | match |
| MOP-18 | source_limit | verdict | true | true |  | match |
| MOP-18 | purchased_panel_no_internal_count_repeat | W | 2.112642 | 2.112642 | 0 | match |
| MOP-18 | empty_curve_scalar_fallback | W | 1.056321 | 1.056321 | 0 | match |
| MOP-18 | reject_partial |  | unresolved | unresolved |  | expected error |
| MOP-18 | reject_duplicate_voltage |  | unresolved | unresolved |  | expected error |
| MOP-18 | reject_negative_current |  | unresolved | unresolved |  | expected error |
| MOP-18 | reject_nonfinite |  | unresolved | unresolved |  | expected error |
| MOP-18 | published_sweep_max_VI | W | 1.6544324 | 1.6544324 | 0 | match |
| MOP-18 | published_row2_VI | W | 0.305966575 | 0.305966575 | 0 | match |
| MOP-18 | reject_unaltered_published_partial_sweep |  | unresolved | unresolved |  | expected error |


### OreSat: 11-baseline-DET

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | DET_operating_voltage | V | 7.4 | 7.4 | 0 | match |
| MOP-19 | DET_infeasible_current | A | unresolved | unresolved |  | expected error |
| MOP-19 | DET_voltage_still_in_controller_window | verdict | true | true |  | match |


### OreSat: 12-baseline-ideal-MPPT

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | MPPT_operating_voltage | V | 4.86 | 4.86 | 0 | match |
| MOP-19 | MPPT_operating_current | A | 0.4347 | 0.4347 | 0 | match |
| MOP-19 | MPPT_operating_power | W | 2.112642 | 2.112642 | 0 | match |
| MOP-19 | MPPT_operating_efficiency | 1 | 0.2861960497 | 0.2861960497 | 0 | match |
| MOP-19 | MPPT_mean_source_power | W | 1.946799603 | 1.946799603 | 0 | match |
| MOP-19 | MPPT_mean_bus_power | W | 1.752119643 | 1.752119643 | 0 | match |
| MOP-19 | MPPT_bus_delivery | verdict | true | true |  | match |
| MOP-19 | MPPT_electrical_window | verdict | true | true |  | match |
| MOP-19 | published_separate_loss_sum | W | 0.387 | 0.387 | 0 | match |
| MOP-19 | published_separate_net_power | W | 1.71 | 1.713 | 0.1754385965 | match |


### OreSat: 13-baseline-fixed-voltage

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | FIXED_VOLTAGE_operating_voltage | V | 4 | 4 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_current | A | 0.4377259259 | 0.4377259259 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_power | W | 1.750903704 | 1.750903704 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_efficiency | 1 | 0.2371919726 | 0.2371919726 | 1.17017348e-14 | match |
| MOP-19 | FIXED_VOLTAGE_mean_source_power | W | 1.613457763 | 1.613457763 | 1.376203394e-14 | match |
| MOP-19 | FIXED_VOLTAGE_mean_bus_power | W | 1.452111987 | 1.452111987 | 1.529114882e-14 | match |
| MOP-19 | FIXED_VOLTAGE_bus_delivery | verdict | true | true |  | match |
| MOP-19 | FIXED_VOLTAGE_electrical_window | verdict | true | true |  | match |


### OreSat: 14-unflown-4S-pair

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | shared_4S_deployed_width | m | 0.0876 | 0.0876 | 1.584222352e-14 | match |
| MOP-19 | shared_4S_deployed_length | m | 0.1464 | 0.1464 | 0 | match |
| MOP-19 | shared_4S_deployed_footprint | m2 | 0.01282464 | 0.01282464 | 1.352648867e-14 | match |
| MOP-19 | shared_4S_deployed_plate_area | m2 | 0.017 | 0.017 | 0 | match |
| MOP-19 | shared_4S_deployed_layout_verdict | verdict | true | true |  | match |
| MOP-19 | DET_operating_voltage | V | 7.4 | 7.4 | 0 | match |
| MOP-19 | DET_operating_current | A | 0.4387814815 | 0.4387814815 | 1.265120648e-14 | match |
| MOP-19 | DET_operating_power | W | 3.246982963 | 3.246982963 | 1.367697998e-14 | match |
| MOP-19 | DET_operating_efficiency | 1 | 0.2199316537 | 0.2199316537 | 1.262009135e-14 | match |
| MOP-19 | DET_mean_source_power | W | 2.9920948 | 2.9920948 | 0 | match |
| MOP-19 | DET_mean_bus_power | W | 2.911227373 | 2.911227373 | 0 | match |
| MOP-19 | DET_bus_delivery | verdict | true | true |  | match |
| MOP-19 | DET_electrical_window | verdict | true | true |  | match |
| MOP-19 | MPPT_operating_voltage | V | 9.72 | 9.72 | 0 | match |
| MOP-19 | MPPT_operating_current | A | 0.4347 | 0.4347 | 0 | match |
| MOP-19 | MPPT_operating_power | W | 4.225284 | 4.225284 | 0 | match |
| MOP-19 | MPPT_operating_efficiency | 1 | 0.2861960497 | 0.2861960497 | 0 | match |
| MOP-19 | MPPT_mean_source_power | W | 3.893599206 | 3.893599206 | 0 | match |
| MOP-19 | MPPT_mean_bus_power | W | 3.504239285 | 3.504239285 | 0 | match |
| MOP-19 | MPPT_bus_delivery | verdict | true | true |  | match |
| MOP-19 | MPPT_electrical_window | verdict | true | true |  | match |
| MOP-19 | FIXED_VOLTAGE_operating_voltage | V | 8 | 8 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_current | A | 0.4377259259 | 0.4377259259 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_power | W | 3.501807407 | 3.501807407 | 0 | match |
| MOP-19 | FIXED_VOLTAGE_operating_efficiency | 1 | 0.2371919726 | 0.2371919726 | 1.17017348e-14 | match |
| MOP-19 | FIXED_VOLTAGE_mean_source_power | W | 3.226915526 | 3.226915526 | 1.376203394e-14 | match |
| MOP-19 | FIXED_VOLTAGE_mean_bus_power | W | 2.904223973 | 2.904223973 | 1.529114882e-14 | match |
| MOP-19 | FIXED_VOLTAGE_bus_delivery | verdict | true | true |  | match |
| MOP-19 | FIXED_VOLTAGE_electrical_window | verdict | true | true |  | match |


### OreSat: 15-operating-point-contract

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-19 | exact | A | 0.4347 | 0.4347 | 0 | match |
| MOP-19 | interpolation | A | 0.43812 | 0.43812 | 1.26703075e-14 | match |
| MOP-19 | interpolation_not_accepted | A | unresolved | unresolved |  | expected error |
| MOP-19 | out_of_range | A | unresolved | unresolved |  | expected error |
| MOP-19 | invalid_selector | V | unresolved | unresolved |  | expected error |
| MOP-19 | unknown_selector | V | unresolved | unresolved |  | expected unknown |


### OreSat: 16-normal-extrema

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-20 | Vmin | V | [3.0,4.0] | [3.0,4.0] |  | match |
| MOP-20 | Iminmax | A | [0.265,0.362] | [0.265,0.362] |  | match |
| MOP-20 | voltage_normal_no_trip | verdict | true | true |  | match |
| MOP-20 | rail_normal_no_trip | verdict | true | true |  | match |
| MOP-20 | bound_current_extrema | A | [0.7142857142857143,5.0] | [0.7142857142857143,5.0] |  | match |
| MOP-20 | conservative_corner_no_trip | verdict | true | true |  | match |
| MOP-20 | independent_PV_corner_minimum | A | 0.7142857143 | 0.7142857143 | 0 | match |
| MOP-20 | independent_PV_corner_maximum | A | 5 | 5 | 0 | match |
| MOP-20 | charger_endpoint_per_cell | V | 4.2 | 4.2 | 0 | match |
| MOP-20 | charger_endpoint_no_trip | verdict | false | false |  | match |
| MOP-20 | published_30W_current_6.0 | A | 5 | 5 | 0 | match |
| MOP-20 | published_30W_current_7.2 | A | 4.17 | 4.166666667 | 0.07993605116 | match |
| MOP-20 | published_30W_current_8.4 | A | 3.57 | 3.571428571 | 0.0400160064 | match |


### OreSat: 17-threshold-boundaries

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-20 | UV_0.99 | verdict | false | false |  | match |
| MOP-20 | UV_1.0 | verdict | false | false |  | match |
| MOP-20 | UV_1.01 | verdict | true | true |  | match |
| MOP-20 | OV_0.99 | verdict | true | true |  | match |
| MOP-20 | OV_1.0 | verdict | false | false |  | match |
| MOP-20 | OV_1.01 | verdict | false | false |  | match |
| MOP-20 | OC_0.99 | verdict | true | true |  | match |
| MOP-20 | OC_1.0 | verdict | false | false |  | match |
| MOP-20 | OC_1.01 | verdict | false | false |  | match |
| MOP-20 | spacecraft_battery_bus_OC_0.99 | verdict | true | true |  | match |
| MOP-20 | spacecraft_battery_bus_OC_1.0 | verdict | false | false |  | match |
| MOP-20 | spacecraft_battery_bus_OC_1.01 | verdict | false | false |  | match |
| MOP-20 | unknown_voltage_samples | verdict | unresolved | unresolved |  | expected unknown |
| MOP-20 | empty_voltage_samples | verdict | unresolved | unresolved |  | expected error |
| MOP-20 | nonfinite_voltage_samples | verdict | unresolved | unresolved |  | expected error |
| MOP-20 | negative_current_magnitude_fails | verdict | false | false |  | match |
| MOP-20 | empty_current_samples | verdict | unresolved | unresolved |  | expected error |
| MOP-20 | unknown_current_samples | verdict | unresolved | unresolved |  | expected unknown |
| MOP-20 | unknown_threshold | verdict | unresolved | unresolved |  | expected unknown |


### OreSat: 18-unknown-invalid-feasibility

| MOP | Quantity | Unit | Reference | Actual | Relative error % | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| MOP-16 | unknown_series_count | cell | unresolved | unresolved |  | expected unknown |
| MOP-15 | unknown_installation_allocation | verdict | unresolved | unresolved |  | expected unknown |
| MOP-14b | unknown_life_fit | J | unresolved | unresolved |  | expected unknown |
| MOP-14b | unknown_energy_retention | J | unresolved | unresolved |  | expected unknown |
| MOP-14a | deliberately_inadequate_delivery | verdict | false | false |  | match |
| MOP-14a | unknown_orbit | s | unresolved | unresolved |  | expected unknown |
| MOP-14a | invalid_perigee |  | unresolved | unresolved |  | expected error |
| MOP-14b | unsupported_cycle_fit |  | unresolved | unresolved |  | expected error |
| MOP-14b | invalid_retention |  | unresolved | unresolved |  | expected error |
| MOP-14b | invalid_packing |  | unresolved | unresolved |  | expected error |
| MOP-20 | invalid_current_voltage_interval |  | unresolved | unresolved |  | expected error |


## Original OreSat sweep input record

This is the unchanged published column H product record. It is not a valid complete ordered curve. Column B retains its separate raw meaning.

| Sheet row | Voltage V | Current A | Saved H power W | Raw B value |
| --- | --- | --- | --- | --- |
| 2 | 4.77625 | 0.06406 | 0.305966575 | 63 |
| 3 | 4.775 | 0.06552 | 0.312858 | 64 |
| 4 | 4.77125 | 0.06669 | 0.3181946625 | 65 |
| 5 | 4.77125 | 0.06523 | 0.3112286375 | 63 |
| 6 | 4.7725 | 0.06796 | 0.3243391 | 66 |
| 7 | 4.77 | 0.06718 | 0.3204486 | 66 |
| 8 | 4.7675 | 0.06826 | 0.32542955 | 66 |
| 9 | 4.7675 | 0.06933 | 0.330530775 | 68 |
| 10 | 4.76625 | 0.07128 | 0.3397383 | 69 |
| 11 | 4.7675 | 0.07119 | 0.339398325 | 69 |
| 12 | 4.765 | 0.07304 | 0.3480356 | 71 |
| 13 | 4.76625 | 0.07402 | 0.352797825 | 72 |
| 14 | 4.765 | 0.07548 | 0.3596622 | 73 |
| 15 | 4.76625 | 0.07617 | 0.3630452625 | 74 |
| 16 | 4.76125 | 0.07822 | 0.372424975 | 76 |
| 17 | 4.76125 | 0.08037 | 0.3826616625 | 78 |
| 18 | 4.765 | 0.08144 | 0.3880616 | 79 |
| 19 | 4.76 | 0.08291 | 0.3946516 | 81 |
| 20 | 4.76375 | 0.08457 | 0.4028703375 | 82 |
| 21 | 4.76 | 0.08632 | 0.4108832 | 84 |
| 22 | 4.76125 | 0.08886 | 0.423084675 | 86 |
| 23 | 4.7575 | 0.09013 | 0.428793475 | 88 |
| 24 | 4.76125 | 0.09082 | 0.432416725 | 88 |
| 25 | 4.75875 | 0.09257 | 0.4405174875 | 90 |
| 26 | 4.75625 | 0.09619 | 0.4575036875 | 94 |
| 27 | 4.75375 | 0.09707 | 0.4614465125 | 94 |
| 28 | 4.7525 | 0.09755 | 0.463606375 | 95 |
| 29 | 4.7525 | 0.10087 | 0.479384675 | 98 |
| 30 | 4.75375 | 0.10244 | 0.48697415 | 99 |
| 31 | 4.75375 | 0.10312 | 0.4902067 | 100 |
| 32 | 4.74875 | 0.10507 | 0.4989511625 | 102 |
| 33 | 4.74875 | 0.10585 | 0.5026551875 | 103 |
| 34 | 4.7475 | 0.10771 | 0.511353225 | 104 |
| 35 | 4.74375 | 0.10937 | 0.5188239375 | 106 |
| 36 | 4.75 | 0.11171 | 0.5306225 | 108 |
| 37 | 4.745 | 0.11328 | 0.5375136 | 110 |
| 38 | 4.74875 | 0.11367 | 0.5397904125 | 110 |
| 39 | 4.7525 | 0.11748 | 0.5583237 | 114 |
| 40 | 4.7425 | 0.11826 | 0.56084805 | 115 |
| 41 | 4.745 | 0.11914 | 0.5653193 | 116 |
| 42 | 4.745 | 0.12236 | 0.5805982 | 119 |
| 43 | 4.74125 | 0.12304 | 0.5833634 | 119 |
| 44 | 4.745 | 0.1249 | 0.5926505 | 121 |
| 45 | 4.74125 | 0.12695 | 0.6019016875 | 121 |
| 46 | 4.74125 | 0.12822 | 0.607923075 | 124 |
| 47 | 4.7375 | 0.12939 | 0.612985125 | 125 |
| 48 | 4.73875 | 0.13164 | 0.62380905 | 128 |
| 49 | 4.7375 | 0.1331 | 0.63056125 | 129 |
| 50 | 4.73875 | 0.13457 | 0.6376935875 | 130 |
| 51 | 4.73875 | 0.13505 | 0.6399681875 | 131 |
| 52 | 4.7375 | 0.13847 | 0.656001625 | 134 |
| 53 | 4.7375 | 0.13955 | 0.661118125 | 135 |
| 54 | 4.7325 | 0.14042 | 0.66453765 | 136 |
| 55 | 4.73125 | 0.14208 | 0.672216 | 137 |
| 56 | 4.73375 | 0.14394 | 0.681375975 | 139 |
| 57 | 4.7375 | 0.14541 | 0.688879875 | 141 |
| 58 | 4.72875 | 0.14687 | 0.6945115125 | 142 |
| 59 | 4.72625 | 0.14882 | 0.703360525 | 144 |
| 60 | 4.72875 | 0.15068 | 0.71252805 | 146 |
| 61 | 4.73 | 0.15214 | 0.7196222 | 147 |
| 62 | 4.725 | 0.15419 | 0.72854775 | 149 |
| 63 | 4.725 | 0.15576 | 0.735966 | 150 |
| 64 | 4.7275 | 0.15625 | 0.738671875 | 151 |
| 65 | 4.7275 | 0.15927 | 0.752948925 | 154 |
| 66 | 4.7225 | 0.16093 | 0.759991925 | 156 |
| 67 | 4.72125 | 0.1621 | 0.765314625 | 156 |
| 68 | 4.72125 | 0.16386 | 0.773624025 | 157 |
| 69 | 4.72125 | 0.16582 | 0.782877675 | 160 |
| 70 | 4.7175 | 0.16699 | 0.787775325 | 161 |
| 71 | 4.71625 | 0.16796 | 0.79214135 | 162 |
| 72 | 4.72375 | 0.16953 | 0.8008173375 | 164 |
| 73 | 4.71625 | 0.17148 | 0.80874255 | 165 |
| 74 | 4.7175 | 0.17324 | 0.8172597 | 167 |
| 75 | 4.71375 | 0.17529 | 0.8262732375 | 169 |
| 76 | 4.71625 | 0.17617 | 0.8308617625 | 170 |
| 77 | 4.71375 | 0.17714 | 0.834993675 | 171 |
| 78 | 4.71 | 0.18046 | 0.8499666 | 174 |
| 79 | 4.71 | 0.18203 | 0.8573613 | 175 |
| 80 | 4.70875 | 0.18271 | 0.8603357125 | 176 |
| 81 | 4.71375 | 0.18398 | 0.867235725 | 177 |
| 82 | 4.7075 | 0.18613 | 0.876206975 | 179 |
| 83 | 4.71125 | 0.18798 | 0.885620775 | 181 |
| 84 | 4.705 | 0.18886 | 0.8885863 | 182 |
| 85 | 4.70875 | 0.19101 | 0.8994183375 | 184 |
| 86 | 4.70375 | 0.19277 | 0.9067418875 | 185 |
| 87 | 4.70375 | 0.19433 | 0.9140797375 | 187 |
| 88 | 4.70125 | 0.19687 | 0.9255350875 | 189 |
| 89 | 4.705 | 0.19755 | 0.92947275 | 190 |
| 90 | 4.69875 | 0.19824 | 0.9314802 | 190 |
| 91 | 4.69875 | 0.20166 | 0.947549925 | 192 |
| 92 | 4.69625 | 0.20292 | 0.95296305 | 195 |
| 93 | 4.69625 | 0.204 | 0.958035 | 196 |
| 94 | 4.70125 | 0.20458 | 0.961781725 | 197 |
| 95 | 4.69375 | 0.20751 | 0.9740000625 | 199 |
| 96 | 4.69375 | 0.20927 | 0.9822610625 | 201 |
| 97 | 4.695 | 0.21044 | 0.9880158 | 202 |
| 98 | 4.6925 | 0.2123 | 0.99621775 | 204 |
| 99 | 4.69125 | 0.21396 | 1.00373985 | 205 |
| 100 | 4.69 | 0.21572 | 1.0117268 | 207 |
| 101 | 4.6875 | 0.21787 | 1.021265625 | 209 |
| 102 | 4.6925 | 0.21875 | 1.026484375 | 210 |
| 103 | 4.685 | 0.21982 | 1.0298567 | 211 |
| 104 | 4.68625 | 0.22314 | 1.045689825 | 212 |
| 105 | 4.68375 | 0.22392 | 1.0487853 | 215 |
| 106 | 4.685 | 0.22558 | 1.0568423 | 216 |
| 107 | 4.6825 | 0.22646 | 1.06039895 | 217 |
| 108 | 4.68125 | 0.22988 | 1.07612575 | 220 |
| 109 | 4.68125 | 0.23076 | 1.08024525 | 221 |
| 110 | 4.67625 | 0.23173 | 1.083627413 | 222 |
| 111 | 4.6725 | 0.23349 | 1.090982025 | 223 |
| 112 | 4.6725 | 0.23535 | 1.099672875 | 225 |
| 113 | 4.67375 | 0.2371 | 1.108146125 | 227 |
| 114 | 4.6775 | 0.23886 | 1.11726765 | 229 |
| 115 | 4.68 | 0.24013 | 1.1238084 | 230 |
| 116 | 4.67125 | 0.24111 | 1.126285088 | 230 |
| 117 | 4.6675 | 0.24208 | 1.1299084 | 231 |
| 118 | 4.6675 | 0.2457 | 1.14680475 | 235 |
| 119 | 4.67125 | 0.24638 | 1.150902575 | 236 |
| 120 | 4.6675 | 0.24755 | 1.155439625 | 236 |
| 121 | 4.665 | 0.25087 | 1.17030855 | 239 |
| 122 | 4.6675 | 0.25224 | 1.1773302 | 241 |
| 123 | 4.6625 | 0.25253 | 1.177421125 | 241 |
| 124 | 4.665 | 0.25449 | 1.18719585 | 243 |
| 125 | 4.65875 | 0.25742 | 1.199255425 | 245 |
| 126 | 4.6625 | 0.25791 | 1.202505375 | 246 |
| 127 | 4.65625 | 0.26035 | 1.212254688 | 247 |
| 128 | 4.6625 | 0.26132 | 1.2184045 | 249 |
| 129 | 4.66 | 0.2625 | 1.22325 | 250 |
| 130 | 4.65625 | 0.26279 | 1.223615938 | 250 |
| 131 | 4.655 | 0.2666 | 1.241023 | 254 |
| 132 | 4.65375 | 0.26748 | 1.24478505 | 255 |
| 133 | 4.65125 | 0.26816 | 1.2472792 | 255 |
| 134 | 4.645 | 0.2708 | 1.257866 | 257 |
| 135 | 4.6475 | 0.27324 | 1.2698829 | 260 |
| 136 | 4.6425 | 0.27343 | 1.269398775 | 260 |
| 137 | 4.64125 | 0.27568 | 1.2794998 | 262 |
| 138 | 4.64375 | 0.27675 | 1.285157813 | 263 |
| 139 | 4.65 | 0.27822 | 1.293723 | 265 |
| 140 | 4.64 | 0.27958 | 1.2972512 | 265 |
| 141 | 4.64125 | 0.28222 | 1.309853575 | 268 |
| 142 | 4.635 | 0.2832 | 1.312632 | 269 |
| 143 | 4.6375 | 0.28427 | 1.318302125 | 270 |
| 144 | 4.63 | 0.28818 | 1.3342734 | 273 |
| 145 | 4.63 | 0.28857 | 1.3360791 | 273 |
| 146 | 4.63125 | 0.29013 | 1.343664563 | 275 |
| 147 | 4.62875 | 0.29296 | 1.3560386 | 277 |
| 148 | 4.63 | 0.29345 | 1.3586735 | 278 |
| 149 | 4.62 | 0.29453 | 1.3607286 | 279 |
| 150 | 4.6275 | 0.29667 | 1.372840425 | 280 |
| 151 | 4.6225 | 0.29785 | 1.376811625 | 282 |
| 152 | 4.62625 | 0.29931 | 1.384682888 | 283 |
| 153 | 4.61875 | 0.30087 | 1.389643313 | 284 |
| 154 | 4.61875 | 0.30312 | 1.4000355 | 286 |
| 155 | 4.61375 | 0.30449 | 1.404840738 | 287 |
| 156 | 4.61375 | 0.30517 | 1.407978088 | 288 |
| 157 | 4.60625 | 0.30839 | 1.420521438 | 291 |
| 158 | 4.6075 | 0.31054 | 1.43081305 | 293 |
| 159 | 4.61 | 0.31064 | 1.4320504 | 293 |
| 160 | 4.6 | 0.31396 | 1.444216 | 296 |
| 161 | 4.60625 | 0.31484 | 1.45023175 | 297 |
| 162 | 4.59625 | 0.31621 | 1.453380213 | 297 |
| 163 | 4.605 | 0.31669 | 1.45835745 | 298 |
| 164 | 4.5925 | 0.31875 | 1.463859375 | 299 |
| 165 | 4.59625 | 0.32031 | 1.472224838 | 301 |
| 166 | 4.59125 | 0.32158 | 1.476454175 | 302 |
| 167 | 4.59125 | 0.32363 | 1.485866238 | 304 |
| 168 | 4.58625 | 0.32509 | 1.490944013 | 305 |
| 169 | 4.58375 | 0.32617 | 1.495081738 | 306 |
| 170 | 4.5775 | 0.32958 | 1.50865245 | 309 |
| 171 | 4.5775 | 0.33037 | 1.512268675 | 309 |
| 172 | 4.58125 | 0.33154 | 1.518867625 | 311 |
| 173 | 4.5775 | 0.3333 | 1.52568075 | 311 |
| 174 | 4.57125 | 0.33525 | 1.532511563 | 314 |
| 175 | 4.56125 | 0.33671 | 1.535818488 | 314 |
| 176 | 4.57125 | 0.33779 | 1.544122538 | 316 |
| 177 | 4.55875 | 0.33994 | 1.549701475 | 317 |
| 178 | 4.56625 | 0.34121 | 1.558050163 | 319 |
| 179 | 4.55 | 0.34287 | 1.5600585 | 319 |
| 180 | 4.5575 | 0.3455 | 1.57461625 | 322 |
| 181 | 4.54 | 0.34628 | 1.5721112 | 322 |
| 182 | 4.5425 | 0.34746 | 1.57833705 | 323 |
| 183 | 4.53125 | 0.35019 | 1.586798438 | 325 |
| 184 | 4.54 | 0.35166 | 1.5965364 | 327 |
| 185 | 4.53875 | 0.35253 | 1.600045538 | 327 |
| 186 | 4.5225 | 0.35332 | 1.5978897 | 327 |
| 187 | 4.5225 | 0.35654 | 1.61245215 | 330 |
| 188 | 4.50875 | 0.3583 | 1.615485125 | 331 |
| 189 | 4.52125 | 0.358 | 1.6186075 | 331 |
| 190 | 4.4975 | 0.36113 | 1.624182175 | 332 |
| 191 | 4.51125 | 0.3622 | 1.63397475 | 334 |
| 192 | 4.4875 | 0.36386 | 1.63282175 | 334 |
| 193 | 4.49375 | 0.3665 | 1.646959375 | 337 |
| 194 | 4.465 | 0.36699 | 1.63861035 | 335 |
| 195 | 4.46875 | 0.36816 | 1.645215 | 337 |
| 196 | 4.42125 | 0.37236 | 1.64629665 | 338 |
| 197 | 4.435 | 0.37304 | 1.6544324 | 338 |
| 198 | 4.425 | 0.37333 | 1.65198525 | 338 |
| 199 | 4.37125 | 0.37451 | 1.637076838 | 335 |
| 200 | 4.355 | 0.37773 | 1.64501415 | 337 |
| 201 | 4.2575 | 0.37929 | 1.614827175 | 330 |
| 202 | 4.3 | 0.37988 | 1.633484 | 334 |
| 203 | 4.1025 | 0.38242 | 1.56887805 | 321 |
| 204 | 4.1225 | 0.38457 | 1.585389825 | 324 |
| 205 | 4.01375 | 0.38583 | 1.548625163 | 317 |
| 206 | 3.575 | 0.38994 | 1.3940355 | 285 |


## Reference integer-bound stability

| Mission | Case | Age | Coarse-grid bounds | Fine-grid bounds | Stable |
| --- | --- | --- | --- | --- | --- |
| BIRDS-4 | 05-baseline-sizing | EOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":2} | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":2} | true |
| BIRDS-4 | 05-baseline-sizing:BOL | BOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":2} | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":2} | true |
| BIRDS-4 | 06-silicon-technology | EOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":13,"required_count":52} | {"minimum_battery_parallel":1,"minimum_solar_parallel":13,"required_count":52} | true |
| BIRDS-4 | 07-battery-chemistry | EOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":2} | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":2} | true |
| BIRDS-4 | 08-integer-configurations | EOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":2} | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":2} | true |
| OreSat | 05-baseline-sizing | EOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":1} | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":1} | true |
| OreSat | 05-baseline-sizing:BOL | BOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":1} | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":1} | true |
| OreSat | 06-silicon-technology | EOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":11,"required_count":41} | {"minimum_battery_parallel":1,"minimum_solar_parallel":11,"required_count":41} | true |
| OreSat | 07-battery-chemistry | EOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":1} | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":1} | true |
| OreSat | 08-integer-configurations | EOL | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":1} | {"minimum_battery_parallel":1,"minimum_solar_parallel":1,"required_count":1} | true |
