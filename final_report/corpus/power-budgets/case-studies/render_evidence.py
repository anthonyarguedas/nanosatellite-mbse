"""Render executed evidence. This script performs no framework calculations."""
from pathlib import Path
import json
import re
from collections import Counter,defaultdict
H=Path(__file__).resolve().parent
R=json.loads((H/'executed/results.json').read_text())
S=json.loads((H/'executed/summary.json').read_text())
I=json.loads((H/'executed/inputs.json').read_text())
A=json.loads((H/'audit.json').read_text())

def fmt(x):
    if x is None:return 'unresolved'
    if isinstance(x,bool):return 'true' if x else 'false'
    if isinstance(x,float):return f'{x:.10g}'
    if isinstance(x,(list,tuple,dict)):return json.dumps(x,ensure_ascii=True,separators=(',',':'))
    return str(x)

def md(x):return fmt(x).replace('|','/').replace('\n',' ')
def tex(x):
    def rounded(v):
        if isinstance(v,float):return float(f'{v:.7g}')
        if isinstance(v,(list,tuple)):return [rounded(z) for z in v]
        if isinstance(v,dict):return {k:rounded(z) for k,z in v.items()}
        return v
    x=f'{x:.7g}' if isinstance(x,float) else fmt(rounded(x))
    for old,new in [('\\',r'\textbackslash{}'),('&',r'\&'),('%',r'\%'),('$',r'\$'),('#',r'\#'),('_',r'\_\allowbreak{}')]:x=x.replace(old,new)
    x=re.sub(r'\b[0-9a-f]{32,64}\b',lambda m:r'\allowbreak{}'.join(m.group()[i:i+8] for i in range(0,len(m.group()),8)),x)
    return x.replace(',',r',\allowbreak{}')

def flat(x,p=''):
    if isinstance(x,dict):
        for k,v in x.items():yield from flat(v,p+'.'+k if p else k)
    elif isinstance(x,list) and x and isinstance(x[0],dict):
        for n,v in enumerate(x):yield from flat(v,p+f'[{n}]')
    else:yield p,x

def table_md(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(md(x) for x in row)+' |' for row in rows])+'\n'

def row(m,s,q):return next(x for x in R if x['mission']==m and x['scenario']==s and x['quantity']==q)

base_output=[('02-states-modes-circular','period','Orbital period','s'),('02-states-modes-circular','sunlight','Sunlight duration','s'),
             ('02-states-modes-circular','eclipse','Eclipse duration','s'),('02-states-modes-circular','sunlight_mean','Mean sunlight load','W'),
             ('02-states-modes-circular','eclipse_mean','Mean eclipse load','W'),('02-states-modes-circular','sunlight_energy','Sunlight load energy','J'),
             ('02-states-modes-circular','eclipse_energy','Eclipse load energy','J'),('02-states-modes-circular','minimum_panel_power','Minimum panel power','W'),
             ('05-baseline-sizing','available_power','Mean available source power','W'),('05-baseline-sizing','fractional_count','Fractional solar count','cell'),
             ('05-baseline-sizing','required_count','Minimum integer solar count','cell'),('05-baseline-sizing','minimum_solar_parallel','Minimum solar parallel strings','string'),
             ('05-baseline-sizing','cycles','Cycle demand','cycle'),('05-baseline-sizing','dod','Selected DoD','1'),
             ('05-baseline-sizing','required_battery_energy','Required BOL battery energy','J'),('05-baseline-sizing','minimum_battery_parallel','Minimum battery parallel strings','string'),
             ('05-baseline-sizing','pack_wh','BOL energy per primary pack','Wh'),('05-baseline-sizing','pack_ah','BOL capacity per primary pack','Ah'),
             ('05-baseline-sizing','eol_j','Retained energy per primary pack','J'),('05-baseline-sizing','eol_ah','Retained capacity per primary pack','Ah'),
             ('05-baseline-sizing','active_area','Active area','m2'),('05-baseline-sizing','panel_area','Installed panel area','m2'),
             ('05-baseline-sizing','required_area','Required active area','m2'),('05-baseline-sizing','storage_occupied_volume','Assumed complete storage occupied volume','m3')]

mdparts=['''# Executed EPS case studies

## Scope and actual execution

These are BIRDS-derived and OreSat-derived verification configurations. They are declared engineering cases using published component/mission data and supplied assumptions. They verify calculations at stated boundaries. They establish no reproduction of complete flight performance or original published architectures.

Each mission has 18 named scenario groups. The final ledger contains 795 comparisons: 730 resolved matches, 32 expected unknowns and 33 expected errors. There are no mismatches in the final executed ledger. All nonzero numerical comparisons meet the 1% criterion separately. The maximum relative error is 0.3307393%, from a rounded BIRDS published P label. The maximum among independently calculated references is 0.000864321%. Zero references and counts, arrangements, statuses and verdicts use exact comparisons.

The FALSE_COUNT false resolved Requirement verdicts are expected observations. They include infeasible alternatives, invalid count domains and conservative threshold boundaries. Their false verdicts agree with the independent expectations. These are successful comparisons, not evidence that the configurations are feasible.

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
''']

providers=Counter(x['actual_provider']['kind'] for x in R)
mdparts.append('### Live implementation evidence\n\n'+table_md(['Actual provider','Records'],providers.items()))
mdparts.append(f"The bounded probe observed {A['numerical_function_call_count']} calls inside the numerical modules and {A['observed_framework_calls']['framework/models/requirements.py:evaluate']} VerificationCondition evaluations. The runtime sizing module was `{A['actual_sizing_module_path']}`. These are observed probe calls, not counts of independent test scenarios. Property and Requirement results in the full ledger are obtained through `.assess()` and `.verify()`. Direct numerical function calls are individually identified with their function names and complete keyword inputs.\n")
mdparts.append('### Framework revision and hashes\n\nRevision: `'+str(S['metadata']['framework_revision'])+'`. Python: `'+S['metadata']['python'].splitlines()[0]+'`. NumPy: `'+S['metadata']['reference_numpy']+'`.\n\n'+table_md(['File','SHA-256'],S['metadata']['framework_sha256'].items()))
mdparts.append(table_md(['Driver/reference file','SHA-256'],S['metadata']['driver_sha256'].items()))

mdparts.append('''## Setup and accounting boundaries

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
''')
mdparts.append('## Compact main-report table\n\n'+table_md(['MOP','BIRDS comparisons','OreSat comparisons','Result within executed scope'],[(m,next(x['total'] for x in S['per_mission_mop'] if x['mission']=='BIRDS-4' and x['mop']==m),next(x['total'] for x in S['per_mission_mop'] if x['mission']=='OreSat' and x['mop']==m),'All expected values/statuses agree. BIRDS published peak remains outside reconstructed outputs.' if m=='MOP-18' else 'All expected values/statuses agree.') for m in ['MOP-'+x for x in ['12','14a','14b','15','16','17','18','19','20']]]))
mdparts.append('## Per-mission MOP outcome counts\n\n'+table_md(['Mission','MOP','Resolved matches','Expected unknown','Expected error','Mismatch','Total'],[(x['mission'],x['mop'],x.get('match',0),x.get('expected unknown',0),x.get('expected error',0),x.get('mismatch',0),x['total']) for x in S['per_mission_mop']]))
mdparts.append('## Baseline numerical results\n\n'+table_md(['Quantity','Unit','BIRDS actual','OreSat actual'],[(label,unit,row('BIRDS-4',sc,q)['actual'],row('OreSat',sc,q)['actual']) for sc,q,label,unit in base_output]))

mdparts.append('''## Results and discussion

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
''')
mdparts.append(table_md(['Mission','Scenario','Fine eclipse s','Fine mean projection','Coarse/fine eclipse difference %','Coarse/fine projection difference %','Grid duration bound s'],[(x['mission'],x['scenario'],x['fine']['eclipse'],x['fine']['projection'],100*x['eclipse_relative_change'],100*x['projection_relative_change'],x['fine']['duration_grid_bound_s']) for x in S['convergence']]))

mdparts.append('## Appendix-ready complete baseline input tables\n\nUnits follow the field names and these conventions: altitude/radius in km, mu in km3/s2, angles in degrees, lifetime in years, powers in W, voltage in V, current in A, energy cell_wh in Wh, charge in Ah, area in m2, volume in m3 and all duty/retention/efficiency/packing/DoD factors as fractions. Fit law is N=a*DoD^b, with a in cycles. All uncredited quantities are A (supplied assumptions).\n')
for mission,base in I['baselines'].items():
    mdparts.append('### '+mission+' baseline\n\n'+table_md(['Input','Value'],flat(base)))

# Delta tables are complete when combined with the full baseline above.
delta_records=[]
for key,cfg in I['executed_configurations'].items():
    if key=='published_oresat_sweep':continue
    mission=cfg.get('mission',key.split(':')[0]);base=I['baselines'].get(mission,{})
    if 'array' in cfg:
        bf=dict(flat(base));changes=[(k,v) for k,v in flat(cfg) if k not in bf or bf[k]!=v]
    else:changes=list(flat(cfg))
    delta_records.append((key,changes))
mdparts.append('## Complete variation inputs\n\nEach table inherits every baseline field not listed. Mutations listed as test arrays are separate assessments, not simultaneously installed values. Ordinary bindings and the evaluated limits are retained in the raw records.\n')
for key,changes in delta_records:
    mdparts.append('### '+key+'\n\n'+(table_md(['Changed or additional input','Value'],changes) if changes else 'No numerical change from the complete baseline.\n'))

mdparts.append('## Source and assumption register\n')
for key,src in I['sources'].items():
    mdparts.append('### '+key+'\n\n'+table_md(['Field','Value'],src.items()))
mdparts.append('''### Bibliography integration

Existing keys include shrestha2021birdssafety, shrestha2022birds4powerbudget, shrestha2026solarreliability, jara2022birdsepsdataset, oresat2016csli, greenberg2021oresat, oresat2019powerbudget, oresatbatteryresearch, oresat2025batterydesign, oresat2025solardesign, oresatsolarsweep, kyutech2021birdsicd and cots-mission_azur_space_3g30a_review_legacy_ds. Li-ion limits use `cots-mission_tenergy_30005_0_ds` with the actual Tenergy datasheet URL. OPD converter material uses `oresat2021opddesign` with the actual OPD notes URL. The XTE-SF outline uses `cots-solar_src_spectro_xtesf`, while its package envelope remains explicitly assumed. The mission3.6V energy convention remains separate from Tenergy's3.65V average. One new entry is supplied in `new-source.bib` for the original battery verification report. The filename's revision and combined report dates should remain visible. The article's safety key is not reused as if it identified that report.

## Fully expanded comparison ledger

The following ledger is an appendix-ready record of every executed comparison. Each scenario has the full input declaration or baseline delta above. Expected unknown status is compared exactly. Invalid-domain errors require both error status and ValueError type. An unrelated binding error does not count as a successful rejection. Numerical relative errors are fractions in raw JSON and percentages here. False engineering verdicts are printed as false, separately from the match result. Every Property/function provider and Requirement dependency trace remains in JSON/CSV.
''')
by=defaultdict(list)
for r in R:by[(r['mission'],r['scenario'])].append(r)
for (mission,scenario),rows in by.items():
    mdparts.append('### '+mission+': '+scenario+'\n\n'+table_md(['MOP','Quantity','Unit','Reference','Actual','Relative error %','Outcome'],[(r['mop'],r['quantity'],r['units'],r['expected'],r['actual'],100*r['relative_error'] if r['relative_error'] is not None else '',r['outcome']) for r in rows]))
mdparts.append('## Original OreSat sweep input record\n\nThis is the unchanged published column H product record. It is not a valid complete ordered curve. Column B retains its separate raw meaning.\n\n'+table_md(['Sheet row','Voltage V','Current A','Saved H power W','Raw B value'],[(x['row'],x['voltage'],x['current_A'],x['saved_power'],x['raw_B']) for x in I['executed_configurations']['published_oresat_sweep']['rows']]))
mdparts.insert(4,'## Comparison accounting\n\n'+table_md(['Category','Records'],S['comparison_accounting'].items()))
mdparts.insert(5,'## Reviewed BOL additions\n\nBoth cases execute a separate BOL characteristic under unchanged baseline mission/load/geometry. Native slots named EOL carry the explicitly selected BOL anchors in these subcases. No battery service verdict is added.\n\n'+table_md(['Mission','Quantity','Unit','Independent reference','Framework actual','Outcome'],[(r['mission'],r['quantity'],r['units'],r['expected'],r['actual'],r['outcome']) for r in R if r['quantity'].startswith('BOL_case_')]))
mdparts.append('## Reference integer-bound stability\n\n'+table_md(['Mission','Case','Age','Coarse-grid bounds','Fine-grid bounds','Stable'],[(x['mission'],x['scenario'],x['age'],x['coarse_counts'],x['fine_counts'],x['stable']) for x in S['reference_count_stability']]))
(H/'findings.md').write_text(('\n\n'.join(mdparts).rstrip()+'\n').replace('795 comparisons',f'{len(R)} comparisons').replace('730 resolved matches',f"{S['total_outcomes']['match']} resolved matches").replace('FALSE_COUNT',str(S['comparison_accounting']['false_resolved_engineering_verdicts'])))

# Clean LaTeX fragment, uses standard longtable/booktabs/array and hyperref.
T=[r'''\chapter{EPS Case Study Evidence}
\label{appendix:eps-case-studies}
These are declared BIRDS-derived and OreSat-derived verification configurations.
They use published component data and supplied assumptions.
The 36 scenario groups contain 795 executed comparisons: 730 resolved matches,
32 expected unknowns and 33 expected errors.
Every executed comparison meets its rule. False engineering verdicts remain false.
The largest nonzero numerical deviation is 0.3307393\%.
The BIRDS measured 1.575~W peak remains outside the reconstructed outputs.
Complete curves in the verification cases are declared three-anchor approximations.
These results establish no complete flight reproduction, chronological energy
simulation, tracker dynamics or hardware qualification.

\section{Method and boundaries}
BIRDS uses one 2S1P 3G30A section on a 1U bus and a 3S2P NiMH pack.
OreSat uses one 2S1P XTE-SF section on a 2U bus and two independent 2S1P
Li-ion packs. Their stored energies are added for bookkeeping.
Independent branch currents are not silently combined.
Sun pointing on $+Z$ is a supplied variation from the original mission rotation.
Nadir variations hold $-Z$ toward Earth with zero clocking.
The array is one unobstructed section.
The alternative 4S section and silicon plate are supplied deployed configurations.

The standalone mass cases retain their own boundaries.
BIRDS first checks the published six-cell 162~g sum, then an assumed complete EPS.
OreSat uses historical 2016 solar and battery module masses with assumed
conversion/distribution contributions and volumes.
They are separate from the later electrical case.

Sources are given in the register below.
Every quantity without an applicable source is a supplied assumption (A).
This includes lifetime and DoD fits, complete curve shape between anchors,
retention assumptions, efficiencies, receiving limits, allocations, charger
conditions and unavailable occupied volumes.
The BIRDS cell fluence row supplies its EOL scalar data.
Those effects are applied once.
The OreSat and silicon EOL current retention of 0.9 is supplied.
Each battery sizing margin is 0.2 and its separate retained energy/capacity
factors are 0.8.
Scalar volume and area screens establish no mechanical qualification.

The independent orbital method solves Kepler's equation at uniform time
midpoints and tests Cartesian cylindrical shadow and positive projection.
It uses 262144 samples, checked against 131072 samples.
The largest duration-grid bound is below 0.044~s.
The largest coarse/fine eclipse change is 0.002050\%.
The largest projection change is 0.0006173\%.
The reference module imports no framework code.

Native Properties and Requirements provide the implemented model results.
Mass margins, mean-load aggregation, charger criteria, converter interval
criteria, storage volume and bus-loss accounting use explicitly authored
ordinary Properties and Requirements.
Direct public numerical function calls are labelled in the retained ledger.
The six JSON/CSV replay artifacts are byte identical.
The framework revision and all model/script hashes are retained in the evidence.

\section{Baseline numerical results}
''']

def lt(headers,rows,widths=None):
    n=len(headers)
    if widths is None: widths=[1/n]*n
    cols='@{}'+' '.join(r'>{\raggedright\arraybackslash}p{'+str(w*.92)+r'\linewidth}' for w in widths)+'@{}'
    # Widths exclude small inter-column padding explicitly through tabcolsep2pt.
    return '\n'.join([r'\begingroup\scriptsize\setlength{\tabcolsep}{2pt}\setlength{\parskip}{0pt}',r'\begin{longtable}{'+cols+'}',r'\toprule', ' & '.join(tex(h) for h in headers)+r' \\ \midrule',r'\endfirsthead',r'\toprule',' & '.join(tex(h) for h in headers)+r' \\ \midrule',r'\endhead',r'\bottomrule\endfoot']+[' & '.join(tex(x) for x in row)+r' \\' for row in rows]+[r'\end{longtable}\endgroup'])

T.append(lt(['Quantity','Unit','BIRDS actual','OreSat actual'],[(label,unit,row('BIRDS-4',sc,q)['actual'],row('OreSat',sc,q)['actual']) for sc,q,label,unit in base_output],[.43,.10,.235,.235]))
T.append(r'\section{Complete baseline inputs}')
T.append(r'Units are km, degrees, years, V, A, Wh, Ah, m$^2$ and m$^3$ as indicated by field names. Efficiencies, retentions, packing, duties and DoD are fractions. The cycle law is $N=a\,\mathrm{DoD}^{b}$. The supplied phase allocations are not inferred chronology.')
for mission,base in I['baselines'].items():
    T.append(r'\subsection{'+tex(mission)+'}')
    T.append(lt(['Input','Value'],flat(base),[.33,.67]))
T.append(r'\section{Variation inputs}')
T.append('Each variation inherits all baseline inputs not listed. Arrays of invalid values denote separate assessments. The output ledger retains every resulting status or verdict. No input is inferred from a calculated output.')
for key,changes in delta_records:
    T.append(r'\subsection{'+tex(key)+'}')
    T.append(lt(['Changed input','Value'],changes,[.33,.67]) if changes else 'The numerical inputs are the complete baseline.')
T.append(r'\section{Sources and assumptions}')
for key,src in I['sources'].items():
    T.append(r'\paragraph{'+tex(key)+'} '+tex(src['locator'])+'. '+tex(src['values']))
    if src.get('key'):T.append(r'\citep{'+src['key']+'}.')
T.append(r'''\section{Interpretation and exclusions}
The silicon configuration fails generation and receiving-voltage screens in both
missions. The LiFePO4 storage group fails the retained OreSat voltage and assumed
installation allocations. A newly selected charger passes its supplied static
conditions. This leaves the other failed engineering criteria unchanged.

OreSat baseline DET requires 7.4~V while its 2S array has 5.5~V open-circuit voltage.
Its operating current correctly reports an out-of-range error.
The supplied unflown 4S variation provides a feasible paired comparison.
All DET, ideal MPPT and fixed-voltage results in each pair use the same curve,
battery, illumination and load. The source factors are $0.95\times0.97$.
DET uses a 0.2~V drop. Converter paths use efficiency 0.9.
No tracker dynamics or full converter envelope is inferred.

Protection compares battery voltage and regulated-rail current at distinct BIRDS
nodes. OreSat ABLIC samples are individual-cell voltages, while heater OC samples
belong to the local enabled heater/electronics branch.
The separate 30~W power corners belong to spacecraft battery-bus terminals.
Nominal detector thresholds establish no worst-case tolerance qualification.
Each threshold is tested below, at and above equality.
Equality fails the strict conservative predicate.
No PTC thermal rating is used as an instantaneous OC detector.

Excluded inconsistent references include the 2021 BIRDS printed
$(2184-360)\times0.8=1411$~mWh (literal result 1459.2~mWh),
the 500~mW for 0.25~h row printed as 150~mWh (literal result 125~mWh),
and the incompletely mapped 3.023~Wh hybrid simulation.
Different historical budget revisions retain their own loss assumptions.
The BIRDS measured 1.575~W peak is not used to infer an unavailable MPP current.
Only unambiguous labelled scalar products are benchmarked.
The OreSat raw sweep is not sorted, deduplicated or supplied with invented
observed endpoints to force acceptance.

\section{Complete executed comparison ledger}
Expected unknowns compare exact status. Invalid-domain errors require error
status and ValueError type, so unrelated binding failures do not count as passes.
Nonzero numerical references use a 1\% relative tolerance.
Zero references, counts and verdicts compare exactly.
Numerical table values are rounded to seven significant figures and error
percentages to three. The retained machine-readable ledger preserves full values.
A false engineering verdict followed by match is an expected infeasible case.
''')
for (mission,scenario),rows in by.items():
    T.append(r'\subsection{'+tex(mission+': '+scenario)+'}')
    T.append(lt(['MOP and quantity','Unit','Expected','Actual','Error %','Comparison'],[(r['mop']+' '+r['quantity'],r['units'],r['expected'],r['actual'],f"{100*r['relative_error']:.3g}" if r['relative_error'] is not None else '',r['outcome']) for r in rows],[.39,.06,.15,.15,.10,.15]))
T.append(r'\section{Original OreSat sweep inputs}')
T.append('Worksheet minicom.cap, rows 2--206. Currents are converted from mA to A. H is the saved VI product. B retains the separate raw power column. Duplicate voltages and missing endpoints are preserved. The largest sampled H occurs at row 197.')
T.append(lt(['Row','V','A','Saved H (W)','Raw B'],[(x['row'],x['voltage'],x['current_A'],x['saved_power'],x['raw_B']) for x in I['executed_configurations']['published_oresat_sweep']['rows']],[.08,.22,.22,.28,.20]))
(H/'case-study-evidence-full.tex').write_text(('\n\n'.join(T)+'\n').replace('795 executed comparisons',f'{len(R)} executed comparisons').replace('730 resolved matches',f"{S['total_outcomes']['match']} resolved matches"))
from report_fragment import render
render(H,R,S,I)
print('Rendered findings.md and report-facing/working appendix fragments from',len(R),'actual comparisons')
