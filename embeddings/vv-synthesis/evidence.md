# Evidence map for nanosatellite EPS V&V

## Scope and method

This pilot used the 14,726 chunks from the 133-report corpus. Retrieval combined focused BM25 queries, supplementary dense candidate discovery, and exact term scans. Every item below was checked in the source Markdown. The embedding manifest hash is stale, so dense retrieval served only as a discovery aid. Counts remain provisional until every report receives formal dual screening.

A study entered the map when one passage linked these three elements:

1. a physical or virtual setup
2. an EPS-specific or power-relevant activity
3. an explicit verification, validation, assurance, or design objective

Companion and duplicate reports are grouped as one study family where evident. Examples include `review-1303` with `review-1443`, `review-0239` with `review-0240`, and `citation-1691` with `citation-1690`.

## What surfaced

### 1. Desktop model and simulation setups

The corpus describes several executable power analysis environments.

- A Python EPS sizing module was benchmarked against two existing CubeSat conceptual designs. The activity compared power, battery, and solar sizing outputs. The objective was tool validity. Power and solar results aligned closely, while battery cell count differed by 50% in one case (`review-1009`, pp. 83–91).
- CNES linked IDM-CIC, Simu-CIC, IDM-Power, and Opalis. The team ran a 48-hour worst illumination scenario and repeated technology trades. The objective was solar array and battery sizing with a stable energy balance and state of charge margin (`review-0289`, pp. 2–6).
- ESTNeT, based on OMNeT++, imported orbit-control behavior from Orekit. A seven-day NetSat simulation challenged a conventional power budget. The objective was to find transient outages and excessive simultaneous loads. The simulation found depletion on one satellite that the average budget missed (`review-1231`, pp. 5–7).
- A 3DEXPERIENCE, ENOVIA, CATIA, and Dymola workflow ran a design of experiments over many configurations. The objective was to verify that battery state of charge stayed above 60% and recovered after eclipse. The reported case stayed above 90% over 300 minutes (`review-0499`, pp. 5–9).
- A SysML, STK, MATLAB, Java, and ModelCenter RAX workflow linked simulation outputs to modeled requirements. The activity varied solar-panel area and propagated battery energy. Nominal and half-size arrays stayed above the 92,000 J minimum, while a quarter-size array violated it (`review-1563`, pp. 6–12).
- Cameo, MATLAB, STK, Excel, Teamcenter, and AWS formed a model-in-the-loop chain. The activity returned simulation outputs to requirement constraints. The objective was traceable compliance, including power and energy requirements. The source states that formal hardware and software testing remained outside scope (`review-0378`, pp. 273–276 and 296).
- A Cameo SysML power tool simulated battery energy through sunlight and eclipse. The objective was early power feasibility and risk reduction. The first run exposed missing duty-cycle logic and insufficient energy without an initial charge (`review-1409`, pp. 5–8).
- Capella, PVMT, and a Python simulation linked operating modes to power and energy margins. The objective was mission-timeline feasibility. Simulation feedback exposed a mode-transition timing issue that could deplete the battery in eclipse (`review-0377`, pp. 3–6).
- A parametric lifetime and operations simulator coupled orbit, attitude, stored energy, data, and temperature. The objective was early assessment of complete mission behavior and power management (`review-1629`, pp. 1–8).

### 2. Component bench setups

- A G2V Sunbrick large-area solar simulator characterized an eight-cell solar array section at AM0 irradiance and 85 °C. Measured I–V and P–V curves parameterized the digital twin (`review-0573`, p. 3).
- A 2S2P Samsung 18650 battery was discharged at 520 mA under a controlled 25 °C condition. A current step also identified series resistance. The objective was an empirical battery model for the digital twin (`review-0573`, p. 7).
- An AMSAT CubeSat Simulator and a solar energy simulator supported repeated solar-output test procedures. The objective was to measure solar-cell output against a current threshold. The study primarily measured execution time across prototype, qualification, and flight-model procedures (`review-0239`, pp. 62–64, 86–87, and 142–144).
- An OpenModelica EPS model was reportedly checked against a simple Python model and a laboratory test bench. Setup and result details were not reported (`review-0793`, p. 7).

### 3. Real-time digital twin, CHIL, and PHIL setups

A single report provides the richest direct EPS chain.

- A Typhoon HIL404 ran a digital twin of one solar array section, regulator, battery, PDU, and loads at a 500 ns step. The reported loopback latency was 1.65 µs. Physical and digital waveforms were compared across MPPT, end-of-charge, and an 18 W load step. The objective was digital-twin validity (`review-0573`, pp. 8–10).
- In control hardware in the loop, the physical controller replaced the simulated regulator controller. The solar array remained real-time simulation. A −50 °C to +100 °C cell-temperature sweep exercised MPPT tracking. The objective was controller performance over expected conditions (`review-0573`, pp. 9–11).
- In power hardware in the loop, the control ran in the real-time simulator and the power stage remained physical. A digital perturb-and-observe MPPT replaced the analog controller. The objective was safe evaluation of a control alternative. The operating point oscillated around the approximately 15 V maximum-power point (`review-0573`, pp. 10–12).

### 4. FlatSat, integrated article, EGSE, and end-to-end setups

- An AESP-14 Stage 1 model joins EPS, TT&C, a power supply that bypasses the batteries, JTAG, EGSE, a PC, a portable ground station, and mechanical support. The modeled activity powers EPS and TT&C, routes data through EGSE, and traces the verification path. The objective is coverage of interfaces, functions, physical elements, and requirements (`citation-1572`, pp. 153–159).
- DESCENT defines three levels. Components are first laid out as a FlatSat with direct computer commands. The assembled spacecraft then uses a hardwired radio path. The final end-to-end setup uses spacecraft and ground antennas. Planned EPS activities include solar-panel illumination, EPS resets, load shedding, and voltage, current, and temperature monitoring. The objective is test-as-you-fly coverage and detection of performance shifts through AIT. The complete functional campaign was still pending, while the telemetry tool had been used (`citation-1662`, pp. 109–120).
- A heritage reuse study maps EPS changes to CEM analysis, EPS acceptance testing, battery cycling, design inspection, FlatSat testing, fit checks, CAD review, and harness checks. The objective is to re-establish validity after solar, battery, packaging, and interface changes. These are reusable or proposed activities for the successor mission (`review-0972`, pp. 224–227).
- A SysML reference-architecture template links EPS tests to requirements and tracks status. The visible objective set includes power, energy storage, fault protection, maximum load, charging efficiency, battery protection, solar-panel voltage, load current, temperature, and state of charge. Only the mass example is shown as verified (`citation-1691`, pp. 88–89).

### 5. Environmental setups

- The 3Cat-4 flight article was suspended by Dyneema wires in a PA12 isolating basket inside an ESEC-GALAXIA thermal-vacuum chamber. Twelve thermocouples included one on the batteries and one on the EPS board. Hot, cold, operational, non-operational, reduced-functional, and charging activities were run. The objectives were battery safety, heater performance, function retention, thermal stability, and readiness for the space environment. A cold-battery error caused an EPS configuration update. The campaign satisfied its overall requirements (`review-0532`, pp. 203–217).
- The same study correlated Thermal Desktop predictions with test measurements. The objective was model refinement for conductance, material, and radiative properties. Reported Pearson correlations were 0.7750 for hot balance and 0.78904 for cold balance (`review-0532`, pp. 217–219).
- The AESP-14 TVAC model includes the chamber, measurement and acquisition systems, thermocouples, EGSE, and a battery-bypass power supply. Its objective is simultaneous environmental exposure and electrical functional testing with explicit interface requirements (`citation-1572`, pp. 161–167).
- The Missurance platform connects simulation, HIL, automated test equipment, a thermal chamber, and the device under test over an instrumentation bus. Its electrical equipment includes power supplies, a DMM, a power meter, and an oscilloscope. The activity progresses from on/off, voltage, current, command, and telemetry checks to functional tests under a programmed thermal cycle. The published demonstration focused on communications hardware, so EPS use remains a platform capability rather than a reported EPS result (`review-1265`, pp. 7–15).

### 6. Telemetry, fault injection, and flight setups

- A SONATE qualification-model power system, UHF/VHF ground link, telemetry client, Java diagnosis engine, Excel model, and Python component equations formed a telemetry-in-the-loop setup. Housekeeping data were modified to inject subtle faults. The objective was early detection and isolation before hard telemetry limits were crossed. A boost-converter case isolated the correct component when measured current was 0.34 A and expected current was 0.18 A (`review-1251`, pp. 20–31).
- A GOMX-3 in-orbit loop joined POWERSIM windows, UPPAAL CORA schedule generation, stochastic KiBaM validation, UHF uplink, and measured current and voltage. Three schedules were executed in orbit. The objectives were low depletion risk, safe operation, fewer planning errors, and more payload activity. Telemetry exposed model and power-draw mismatches and informed later model-predictive updates (`review-1303`, pp. 13–22).

### 7. Analytical reliability setups

- A SysML EPS architecture integrates FMEA, event scenarios, qualitative and quantitative criticality analysis, and fault trees. Thirteen failure modes cover regulation, switching, protection, measurement, solar conversion, reverse current, bypass, and storage. The objective is to rank reliability concerns and compare design configurations. The source reports differing qualitative and quantitative rankings and a simplified EPS reliability estimate of 0.8802 (`review-1158`, pp. 42–63).

## Recurring V&V objectives

The evidence supports eight recurring objective families.

1. Establish model credibility through measured-to-simulated comparison.
2. Verify requirement compliance and preserve traceability.
3. Size solar generation and battery storage for worst-case energy balance.
4. Characterize electrical performance, including I–V, P–V, efficiency, rails, loads, and MPPT behavior.
5. Verify interfaces, commands, telemetry, and integrated functional chains.
6. Demonstrate protection, fault detection, recovery, reset, and load-shedding behavior.
7. Demonstrate environmental function and battery thermal safety.
8. Validate operational schedules against depletion risk while maximizing mission activity.

## Evidence strength

Four study families provide the strongest setup–activity–objective–result chains.

- `review-0573` covers component characterization, real-time digital-twin comparison, CHIL, and PHIL.
- `review-0532` covers flight-article TVAC, EPS errors, configuration changes, and thermal-model correlation.
- `review-1251` covers qualification-model telemetry, injected EPS faults, and diagnosis outcomes.
- `review-1303` covers in-orbit execution and comparison against battery telemetry.

The remaining evidence includes executed digital studies, proxy test articles, reported claims, and planned or modeled campaigns. Slide text states the limits of proxy, planned, and cross-domain evidence.

## Presentation choice

Graphics fit this evidence because the sources contain setup diagrams, photographs, waveforms, timelines, telemetry views, and requirement-linked results. The deck therefore uses:

1. setup and V&V question summaries
2. paired simulation results that expose margins and design failures
3. source graphics for physical setups, measured responses, and model-to-test comparison
4. source tables redrawn for the software benchmark

Each slide has a single descriptive title. The slides have no author, date, footer, or slide numbers.
