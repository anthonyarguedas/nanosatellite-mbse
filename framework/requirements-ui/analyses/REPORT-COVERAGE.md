# Report coverage audit and optional assessments

## Scope and interpretation

This is the historical numerical coverage audit for the report assessment additions.
Its **Existing support** and **Added assessment scope** columns describe that implementation stage.
The current runtime uses native Python classes and sessions, with the same numerical scope and engineering limitations.
See the [application guide](../README.md) and [native API](../../python/README.md) for current architecture and commands.
This runtime refactor supplies no new framework-conformity claim or re-evaluation of the report MOPs.

`final_report/requirements.tex` defines 23 framework requirements (FRs). The 20 EPS product requirements are in `final_report/eps-requirements.tex`, included by `design-proposal.tex`. This audit covers both sets. Legacy workbook IDs such as EPS047, EPS052 and EPS078 are decompositions of report obligations. They are not additional report requirements.

Coverage means an implemented assessment within its declared scope. A place to enter a manual verdict provides no implementation credit. A synthetic test pass establishes numerical behavior for that fixture. It establishes no product compliance, physical model validity or achieved framework MOP.

The additions use generic requirements, numeric parameters, typed registered scripts and sourced COTS facts. The 49 new study requirements are part of the normal Python catalog and populate every applicable EPS session. Their independent quantities and limits start unset. Existing entered values, prose, IDs and evidence configurations remain intact. The visible tables and editor are unchanged. Internal numeric capacity is 256 names, and mode results omit redundant empty cells to support the larger generic workbook. Native Python sessions retain per-owner lifecycle history for deliberate deletion preservation, with version-14 JSON retained only as migration input and browser transport. Scripts still require explicit execution. Missing decisive evidence stays pending, invalid model inputs produce errors, and known operational violations produce failed findings.

## Framework requirements

The **Existing support** column describes the application before these additions. None of the composite FRs receives a blanket conformity claim from this audit.

| FR | Existing support | Added assessment scope | Remaining scope |
| --- | --- | --- | --- |
| FR-01 | IDs, statements, sources, rationale, quantities, units, methods and assignments are retained. | Input declarations and result criteria retain their report origins. | Product levels, typed parent relationships, resolution statuses and unresolved/inapplicable reasons are incomplete. |
| FR-02 | Parameter markers, expression syntax, references and types have deterministic edit checks. | No prose checker is added. | Requirement statement syntax rules with affected text and their reference defect population remain undefined. |
| FR-03 | Engineers select methods and registered models. | Generic requirement rationales identify studies and available bounded methods. Optional `eps_guidance` proposes methods and independent validation from a declared inventory on request. | Reading arbitrary requirement prose, automatic edit guidance and expert recommendation precision/recall remain unimplemented. |
| FR-04 | Source links, assignments and COTS uses are navigable. | Assessment criteria link to their input declarations. | A complete scenario/requirement/allocation relation model and general forward/reverse queries remain incomplete. |
| FR-17 | Power, mass and volume allocation rows have parent links and independently assigned limits. | Assembly sizing proposes numerical generation and storage configurations. | General mission-to-EPS/component requirement allocation proposals with residuals remain incomplete. |
| FR-39 | No activity planner. | Unfilled generic requirements provide activity guidance by exposing the studies and quantities still needed. Optional `eps_guidance` also proposes activities from an explicit inventory. | The current activity and input inventory remain engineer supplied. There is no managed activity history or automatic workflow transition. |
| FR-25 | Orbit inputs, spacecraft modes, component states and load shares are retained. Illumination scripts retain epoch and attitude inputs. | Explicit segment chains retain chronology, duration, temperatures and source/load conditions. | A complete mission expectation, constraint and ConOps record with scenario identity and environmental histories remains incomplete. |
| FR-15 | Generic EPS components, selected products, parameters, allocations and software hosts are configurable. | Declared assembly, path, controller, battery and thermal cases use the same model. | Complete connection topology, function coverage and general design representation remain incomplete. |
| FR-13 | Mass and volume budgets, component sums, independent allocations, COTS references and pending unknowns exist. | Existing budget requirements remain available in every assessment session. | Authorized design revisions and revision-linked estimate history remain incomplete. Summed volume establishes no mechanical fit. |
| FR-14 | Engineers can enter alternative concepts, but common engineering feasibility models are limited. | Sizing, electrical path, charger, geometry and energy cases provide common raw measures and feasibility checks. Spacecraft modes can represent independent alternatives. | Complete concept enumeration, automatic catalog selection, unknown-aware multi-criterion comparison and all product-specific topology envelopes remain incomplete. |
| FR-20 | Circular orbit, duty-weighted load budgets, preliminary solar/battery sizing and cycle-life fits exist. | Integer assembly arrangements, area/capacity measures and chronological retained energy/charge checks extend preliminary sizing. | Results require applicable BOL/EOL cell data, temperature and degradation factors. A universal mission sizing or optimal configuration claim is unsupported. |
| FR-16 | Orbit illumination and empirical I-V/P-V MPPT analyses exist. | Chronological energy and charge, path losses, converter response, battery equivalent circuit, thermal RC and protection stress models cover the missing numerical families within declared bounds. | Complete coupled spacecraft electrothermal models, arbitrary orbit/attitude histories, switching fidelity and physical validation remain separate work. |
| FR-22 | No registered parameter estimator. | Quality-checked supplied samples support declared affine and first-order model fits with residuals and identifiability checks. | General single-diode, electrochemical, spatial thermal and dynamic multi-parameter identification remain outside the supplied models. Independent prediction assessment remains separate. |
| FR-26 | No RAM eligibility assessment. | `eps_guidance` identifies FMEA, FMECA, fault-tree and failure-propagation eligibility from explicit prerequisites. | It screens an engineer's inventory. It does not infer failure semantics or establish expert eligibility accuracy. |
| FR-27 | No executable RAM model. | A declared bounded fault tree produces minimal failure combinations, conditional failure measures and reliability results. | Complete FMEA/FMECA records, arbitrary dependency graphs, recovery/repair models and general failure propagation remain incomplete. |
| FR-19 | MPPT transition simulation exists. | Explicit energy schedules, converter command/startup response and UV/OV/OC protection scenarios support bounded MIL checks. | General scenario orchestration, actual flight software feedback and exhaustive mission/control coverage remain incomplete. |
| FR-34 | F Prime COTS wrappers and a component manifest are exported. | No new integration-profile claim is made. | Specification-derived service ports, checked mappings and version-compatibility assessment remain incomplete. |
| FR-05 | Expression dependencies update calculations and invalidate script evidence. Referential edits protect linked rows. | New assessments reuse that dependency behavior. | A proposed-change impact report covering requirements and design remains incomplete. |
| FR-07 | Independent named JSON sessions exist. | New assessments are independent named sessions. | Sessions are editable copies. Exact authorized phase baselines, revision history and controlling decisions remain unimplemented. |
| FR-09 | Script inputs, methods, pinned source revisions, outputs, logs and failure statuses are associated during a browser session. | Every new result uses this existing execution boundary. | Results and failed runs are transient. Persistent scenario/result records and retained failed runs remain unimplemented. |
| FR-11 | Pending, erroneous, stale and failed method/script evidence prevents passing checks. | New criteria use current script-backed methods. | Formal rejected/unresolved evidence dispositions and durable requirement evidence-gap reports remain incomplete. |
| FR-10 | Workspace JSON, pinned local script interfaces, source files and documented commands support replay. | Standard-library implementations, equations, synthetic fixtures and tests provide a controlled replay basis. | Exact execution environment capture, archived raw runs and a complete independently replayed analysis package remain incomplete. |
| FR-37 | Mission/subsystem tables, assignments, COTS uses and export views exist. | All new criteria and outputs appear in those existing views. | Arbitrary filtered interface/design/analysis review views and measured human interpretation performance remain incomplete. |

The residual record, history, authorization, view and integration functions require application or data-model work. They cannot be completed by adding numerical requirements or Boolean catalog properties alone.

## EPS product requirements

All rows apply to declared conditions and selected functions. A requirement without evidence remains unassessed. An absent optional function requires an explicit applicability decision. No script automatically turns an optional requirement into a passing result.

| Report ID | Existing coverage | Added coverage through the existing UX | Evidence or scope still required |
| --- | --- | --- | --- |
| EPS-01 | Product selection and COTS supported configuration facts. | Assembly count/configuration checks and charger series bounds. | Fixed purchased arrangements, exact supported options and required external circuits/adapters must come from the selected product. |
| EPS-02 | SIZ001–004, EPS002 and MPPT source energy provide a preliminary screen. | Integer arrangements and area/derating measures. | Use an attainable DET/MPPT operating point with compatible EOL conditions. Radiant J/m² is not electrical generation. |
| EPS-03 | MPPT tests check tracking voltage, Voc and Isc. | Converter/path source and startup bounds supplement those checks. | Product-specific shared-tracker, DET, temperature and absolute-maximum conditions remain distinct. |
| EPS-04 | No general converter operating envelope assessment. | Declared topology/source/duty/path bounds and first-order startup/response. | Characterize the real converter envelope and any limitations beyond these models. |
| EPS-05 | Relevant charger/battery catalog facts can be selected. | Series count, charge voltage/current, termination and charging temperature requirements. | Check chemistry, charge algorithm and product-specific termination/reset policy using sourced feature facts. |
| EPS-06 | Average load budgets establish no terminal supply voltage. | Rail drop, pulse demand and startup service time criteria. | Cover every required load, return path, isolation relationship and service interval. |
| EPS-07 | Per-mode component demand/allocation exists. | Upstream conversion losses and steady/pulse/current rating checks. | Repeat for each shared path at applicable temperature/duration. Count losses, heaters and software hosts once. |
| EPS-08 | SIZ007–008, SIZ016 and EPS008 cover preliminary BOL/retained energy. | Assembly charge capacity and separate energy/coulomb balances. | Supply compatible retained capacities and cell/pack ratings. Apply preliminary margin once. |
| EPS-09 | Cycle-life domain and required/supported cycles exist, with EPS009/EPS047 evidence inputs. | Nominal segment SOC minima check actual scenario DoD. | Applicable cycle data and separate exceptional survival limits remain required. |
| EPS-10 | Preliminary load/energy fields exist, with no chronological battery propagation. | Chained energy/charge intervals report unmet service, reserves and limits. | Define the complete chronology and use applicable voltage, efficiencies and retained capacities. |
| EPS-11 | EPS011/EPS052/EPS053 accept externally supplied closure evidence. | Repeating-interval ending energy and charge are computed and checked separately. | Chain the complete repeating interval. Numerical energy tolerance permits no persistent depletion. |
| EPS-12 | No survival/recovery propagation. | Independent survival and recovery intervals retain state continuity, duration and reserve checks. | The engineer defines essential loads, shedding, allowed transitions and exceptional reserves. Electrical recovery also requires EPS-04–07. |
| EPS-13 | Temperature facts can be selected, with no thermal response model. | Exact one-node RC bounds, distinct charge/discharge temperature checks and heater inputs. | Match the modeled cell/case/junction reference. Include heater electrical demand in load/current/energy cases. |
| EPS-14 | MPPT conversion alone provides no battery-full surplus assessment. | Charge acceptance stops at either full energy or charge. Surplus power/energy and handling limits remain visible. Shunt dissipation and curtailed harvest remain separate. | Model supported circuit behavior and feed shunt heat into an applicable thermal case. |
| EPS-15 | Protection facts can be referenced, with no fault-stress execution. | Legitimate demand, threshold/delay and interruption stress scenarios. | Apply threshold tolerances and actual time-current/SOA ratings, including fault source behavior. |
| EPS-16 | Catalog UV/OV capabilities can be selected. | Declared threshold, hysteresis, reset and recovery scenarios. | Match the product policy and assess essential outputs/recharge paths separately where they differ. |
| EPS-17 | Inhibit/default/autonomous protection catalog facts can be selected. | Command/inhibit and processor-unavailable scenarios use explicit policy inputs. | Cover the applicable IF-C truth table, permitted domains and actual circuit truth behavior. |
| EPS-18 | COTS pins and protocol/control features exist. | Signal operating/logic levels, exchange rate and response bounds have executable numeric requirements. | Pin/return mapping, directions, meanings, protocol/version, address uniqueness and polarity/default/fault semantics still require explicit connected-endpoint evidence. |
| EPS-19 | Mass/volume budgets and EPS019/EPS078 already exist. | Profiles retain the ordinary budget rows. | Include auxiliaries and establish disjoint accounting boundaries. |
| EPS-20 | Volume totals alone provide no fit test. | Transformed rectangular envelope containment/keep-out checks and cell-area packing. | Declare mounting/connector/deployment keep-outs, installation states and envelope fidelity. Curved/flexible geometry needs another model. |

Existing workbook rows keep their values and verification methods. The new generic rows have no mission values, selected products or passing evidence. They expose study quantities and retain engineering acceptance predicates in Python. As with the existing report requirements, engineers choose applicable evidence methods in the ordinary requirement pane. The optional profiles provide isolated study configurations.

## Generic requirements are the activity guidance

Restart the server and reload any existing EPS session. The reusable orbit and EPS catalog has 76 requirements: the original 27 plus 49 study requirements. All 20 report EPS criteria have generic primary rows. EPR001–027 separate additional obligations. CAL001–004 cover model fits, MIL001 covers regulator settling, and RAM001–002 cover reliability measures.

For example, EPS013 exposes `temp_limit_min_K`, `temp_limit_max_K`, `assessed_temp_min_K` and `assessed_temp_max_K`, all unset. Its assigned components, source and rationale identify the thermal study to perform. The engineer supplies independently assigned operating limits and assessed temperature bounds, then binds applicable study evidence through the existing verification table. A registered model can support that work. No separate session or planner is needed to make the obligation visible.

Each EPS owns independent parameter cells. Existing sessions receive only newly introduced generic templates. Reads leave source files untouched. Save and export retain optional `requirementSeeds` metadata, keyed by EPS and template definition. Later deliberate deletions remain deleted. Future template additions can still populate. Blank sessions remain empty until an EPS is added.

## Optional study configurations

These commands create independent analysis benches. They are supplementary to the automatically populated generic requirements.

From `framework/requirements-ui/`:

```sh
node tools/create-report-session.mjs --list
node tools/create-report-session.mjs energy --name "My nominal energy assessment"
node tools/create-report-session.mjs survival --name "My survival assessment"
node tools/create-report-session.mjs charger --name "My charger bounds"
node tools/create-report-session.mjs interfaces --name "My service port bounds"
node tools/create-report-session.mjs converter --name "My converter step"
node tools/create-report-session.mjs guidance --name "My method eligibility"
```

Available profiles:

| Profile | Scope |
| --- | --- |
| `energy` | Chained nominal eclipse/sunlight energy, independent charge and repeating-interval closure |
| `survival` | Chained essential-load survival and recovery intervals |
| `path` | Converter envelope, path voltage drop, simultaneous steady/pulse ratings and losses |
| `converter` | Declared first-order voltage command/startup response |
| `protection` | Nominal, fault and recovery MIL with explicit trip/reset and inhibit policy |
| `battery` | Analytical equivalent-circuit voltage, charge state and resistor loss |
| `thermal` | Exact component and charging temperature bounds for one thermal interval |
| `electrothermal` | Battery circuit plus conservative hot/cold thermal bounds driven by its resistor heat |
| `sizing` | Integer array/battery proposals, BOL/EOL capacities, packing and necessary voltage screens |
| `geometry` | Oriented installation containment and keep-out contact policy |
| `fit` | Quality-checked PV, battery or first-order model parameter estimation |
| `ram` | Authored four-event fault tree, minimal cuts, reliability and conditional failure probability |
| `charger` | Series count, charge voltage/current, termination and temperature bounds |
| `interfaces` | Electrical logic/operating levels, exchange rate and response bounds |
| `guidance` | Structured method and activity eligibility with missing prerequisites |
| `cots-protection` | TPS63802 capability, tolerance endpoints, startup and recommended temperature bounds from pinned manufacturer facts |

Exact model interfaces, equations, test fixtures and limitations are in [MODELS.md](MODELS.md) and [PATHS.md](PATHS.md). The `electrothermal` profile links `max_loss_W` into its hot bound and `min_loss_W` into its cold bound. It uses the same interval and shared thermal parameters. Charging activity derives from the battery's charge-positive current. Both thermal cases need their limit-availability flags supplied explicitly. This bounds a declared linear thermal model and supplies no temperature-dependent circuit feedback. Heater electrical demand remains a separate load-accounting input.

The power-path topology codes are 0 (buck), 1 (boost) and 2 (buckboost magnitude). Sizing uses its separate codes 0 (direct/DET), 1 (buck), 2 (boost) and 3 (buck-boost). Keep each script's documented codebook. Sizing voltage screens are necessary conditions. Its full-interface feasibility result remains pending unless a represented violation proves false.

Use `--mission /path/to/mission.py` to select the neighboring saved-session directory. A retained legacy JSON source is also accepted. `MISSION_FILE`, `VERIFICATION_SCRIPTS_DIR` and `VERIFICATION_PYTHON` are honored. The thin Node launcher uses native Python bench factories and the shared session repository. It creates a named Python copy without reading inputs from, overwriting or running analyses on the current mission. Duplicate names fail without replacing a session.

Open the new session in the existing Session picker. INP rows declare numeric model inputs with shared units. Open each requirement pane to supply their parameter expressions. Boolean inputs remain in the script input table and start unset. CHK rows contain product or assessment acceptance criteria. Supply their independent limits and sources. Run the relevant script explicitly. Inspect its typed outputs, logs and verification results in the existing pane.

Use source links and affected-component assignments to connect the study to approved mission requirements and products. Most profiles are scoped studies with no automatically selected COTS product. Add a product through the existing COTS table and pin applicable facts. The `cots-protection` profile selects TPS63802 and pins nine exact capability, action, threshold and operating-limit facts. Its output OVP maximum is 5.9 V. A separately assigned 5.5 V trip ceiling therefore fails. Its OVP threshold does not extend the recommended operating range or establish battery protection. Replace input literals with fact references where appropriate. Unit conversions stay explicit. Capability facts describe supported functions. The assessed circuit and selected settings determine whether the function is effective.

The full orbit and EPS model uses 161 shared numeric names before power/resource allocation additions. The internal capacity is 256, leaving room for additional studies in the same session. Script inputs and outputs keep independent namespaces. Any registered model can be selected directly in an existing requirement pane. Define its inputs there and attach an evidence method to the generic requirement. No new UI controls or activity workflow are introduced.

## Chronological energy and charge

`eps_energy_segment` executes one constant-condition interval exactly. Source and load powers use separate declared boundaries. With source efficiency `eta_s`, load efficiency `eta_l` and segment duration `T`:

```text
P_source_bus = source_power_W * eta_s
P_demand_bus = load_power_W / eta_l
P_delta = P_source_bus - P_demand_bus
```

Positive surplus can charge at `min(P_delta, I_charge_limit * V_battery)` when enabled and thermally allowed. Stored energy increases by `eta_E_charge * P_charge * t`. Remaining charge increases by `eta_Q_charge * P_charge / V_battery * t`. Acceptance ends when either retained capacity is full. Negative surplus discharges up to the specified battery-port current limit. Stored energy decreases by `P_discharge / eta_E_discharge * t`. Remaining charge decreases by `P_discharge / V_battery / eta_Q_discharge * t`. Discharge ends when either physical state reaches zero. Reserve violations remain visible before physical depletion. Missing demand after depletion/current limiting is reported as unserved load energy.

Battery voltage is supplied and constant within a segment. Energy and charge remain distinct. Their capacities, voltage and efficiencies require a compatible characterization. The model establishes no OCV/voltage history by itself. Use smaller declared segments or the separate equivalent-circuit model for varying conditions. It reports unsupported discharge temperatures. Charging outside its permitted interval is blocked and a requested-but-disallowed charge is reported. Explicitly disabling charge produces no charging-temperature violation.

Solar surplus is reported even when charge acceptance is current, temperature, energy or charge limited. `shunt_surplus = True` adds that surplus to dissipation. Otherwise it reports foregone harvest as `curtailed_energy_J`. The peak handling bound is checked in both cases. At the declared boundaries:

```text
initial_energy + source_energy
    = ending_energy + served_load_energy + loss_energy + curtailed_energy
```

This identity is an accounting check, with no physical validation claim. The model omits transient conversion dynamics, battery voltage dependence, thermal feedback and fault switching.

The `energy` profile chains **Nominal eclipse → Nominal sunlight**. The `survival` profile chains **Survival interval → Recovery interval**. Ending energy and charge feed the next interval's initial state through ordinary script dependencies. Retained capacities also reference the first interval. Every other input remains independently editable. Run the second script to execute the dependency chain. Add more instances and explicit links for a richer schedule. Each spacecraft mode runs its own independent chain. Mode shares supply no chronological ordering.

Each interval checks complete declared load service and a minimum required duration, energy reserve, charge reserve, temperature rules and surplus handling. Nominal cases also check DoD and separate energy/charge closure. Survival reserves and allowed duration remain independently defined. Startup and protective switching are separate electrical/control assessments.

A reproducible synthetic fixture uses 100 s intervals, a 1 V battery with 1000 J and 1000 C retained capacities, initial energy 500 J, initial SOC 0.5, all efficiencies one and 2 W demand. Eclipse has zero source power. Sunlight has 4 W source power. Both current limits are 10 A, energy reserve is 200 J, minimum SOC is 0.2, and the permitted temperature intervals include 20 °C. Eclipse ends at 300 J and SOC 0.3. Sunlight ends at 500 J and SOC 0.5. These values are invented test data, with no product basis.

## Converter command response

`eps_converter_step` uses `V(t) = V_target + (V_initial - V_target) * exp(-t/tau)`. Inputs declare the duration, target and initial voltage, positive time constant, positive input voltage, nonnegative constant load current, conversion efficiency, required service band and absolute settling error band.

The script evaluates exact monotone voltage bounds and integrates constant-current load energy. Fixed efficiency gives input energy and losses. It reports finite settling/startup time when reached within the interval, otherwise `null`. `service_duration_s` covers the final continuous interval inside the supply band. Startup success requires service to remain valid through the end of the assessed interval. Startup may legitimately begin below the supply band, so full-interval voltage compliance is reported separately.

This is a declared transfer model. Target voltage includes any supplied steady droop. It models no overshoot, current limiting, reactive stored energy, switching ripple, control stability or topology feasibility. Use `eps_power_path` for topology, source startup and rating constraints. Fit `tau` only from compatible characterized response data. Chain instances for additional steps.

## Method and activity eligibility

The populated generic requirement list is the primary activity guidance. `eps_guidance` is an optional additional tool that uses an explicit structured objective and inventory. It proposes a method on **Run Python** and reports unmet prerequisites. It does not inspect prose, automatically count workspace records, authorize work or verify the engineer's inventory claims. Its rules are proposed engineering rules for this bounded model library. Independent expert assessment remains required for FR-03/26/39 performance claims.

Goal and method codes:

| Code | Goal | Proposed registered method |
| --- | --- | --- |
| 1 | Chronological energy | `eps_energy_segment` |
| 2 | Electrical path | `eps_power_path` |
| 3 | Thermal response | `eps_thermal` |
| 4 | Model parameter fitting | `eps_fit` |
| 5 | Quantitative bounded fault tree | `eps_ram` |
| 6 | Envelope accommodation | `eps_geometry` |
| 7 | Assembly sizing | `eps_sizing` |

Input activity codes are 0 (define case), 1 (collect inputs), 2 (execute analysis), 3 (assess criteria) and 4 (independent validation). Proposed next activities use those codes and 5 (technical review). Missing model prerequisites lead to case definition or input collection. Complete prerequisites with missing/stale results lead to execution. Current results lead to assessment, independent validation when requested, then review. Stale existing results explicitly recommend repeated analysis.

Unmet-prerequisite bits are 1 (no case), 2 (no limits), 4 (no model parameters), 8 (no chronology), 16 (no retained capacities), 32 (accepted sample count outside 3..5), 64 (unidentified components/failure modes), 128 (no authored failure logic), 256 (no quantitative probabilities), 512 (outside the registered tree size) and 1024 (no geometry). Each missing bit has a reason in the script log. Model-specific execution performs its own stronger domain and identifiability checks.

FMEA eligibility requires identified components, failure modes and supplied effects. FMECA also requires probabilities. Fault-tree eligibility requires identified modes and authored logic. Quantitative fault-tree eligibility also requires probabilities. Failure-propagation eligibility requires identified modes and supplied dependencies. These flags propose analysis families. The supplied numerical executor implements the bounded fault-tree subset, with full FMEA/FMECA and general propagation left open.

## COTS evidence boundary

The existing COTS model already supports numeric, Boolean and String facts with internal elements, conditions, source revisions and exact record identities. Protection presence can be verified directly, for example `CMP001.autonomous_overvoltage_protection`. A false feature is a known failure when the capability is required. An unreported feature remains absent and unresolved. Add a numeric requirement parameter such as a trip delay or protected-path current to state an actual engineering criterion, then combine the relevant capability and numeric limit in its existing verification method.

Controller capability requires its external circuitry, supported configuration and processor-unavailable policy to be assessed. Typical trip values establish no guaranteed worst-case limit. A Boolean capability alone establishes no threshold, interruption-time, fault-energy, SOA or system-level protection result. See `framework/cots/ENRICHMENT.md` for the sourced database additions and unresolved properties.

## Verification history

The pre-refactor sources under `test/legacy/` preserve checks using synthetic data, analytic reference calculations, known violations, invalid inputs, missing evidence, dependency chains, mode isolation and JSON round trips.
Their `.txt` suffix excludes them from current Node test discovery because their earlier implementation dependencies were retired.
Active `npm test` runs the retained requirement presentation checks and makes no claim of old-suite parity.
Current native examples, Python study factories and browser workflows are documented in the [application guide](../README.md) and [REPL demonstration](../../python/docs/repl.md).
