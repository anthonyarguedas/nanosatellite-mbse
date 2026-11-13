# Published references for the framework MOPs

The numerical references below come from public mission documents and their published tables or spreadsheets.
They supplement the BIRDS-4 presentation and the September 2019 OreSat power budget.
Academic discovery through the local browser supplied five further full papers and the existing peer-reviewed EPS dataset article.
The checked publications strengthen FR-11, FR-12, FR-13, FR-14, FR-15, FR-18 and FR-20.
They provide partial coverage of FR-12 to FR-20.
Every case study MOP requires separate BIRDS-4 and OreSat evaluations.
The 1% tolerance applies to each numerical comparison in each mission.
Results are not averaged across outputs or missions.
Both missions must meet the acceptance criteria for a MOP to pass.
Missing published results receive no verification credit and do not waive either mission's evaluation.

## Coverage

This table records available evidence. It does not establish complete verification of either mission.

| FR | Published reference | Scope and limits |
| --- | --- | --- |
| FR-10 | Manufacturer datasheets linked from the COTS catalogue | The table inspection checks values, conditions, units and provenance. It does not verify parameter estimation or dynamic model accuracy. |
| FR-11 | Kim et al. (2021), Greenberg et al. (2021), OreSat battery research and battery card design notes | Documented criteria support comparison with LTC3119, Tenergy 30005-0 and MAX17205 choices. Supply criteria without the chosen part numbers. An alternative needs evidence that it satisfies every documented constraint and improves the stated quantitative selection measure. |
| FR-12 | BIRDS-4 battery verification report, Figure 1-1, page 21, and OreSat 2016 application, Section D.2, pages 21–22 | BIRDS-4 explicitly publishes 27 g × 6 = 162 g for its battery cells. OreSat solar modules total 252 g and battery modules total 416 g. These support mass sums at their stated subassembly boundaries. Complete EPS mass, occupied volume and margin references remain incomplete for both missions. Spacecraft masses are excluded. |
| FR-13 | Jara et al. (2022), Section 2, and the original budgets | The BIRDS dataset article reports a 400 km, 51.6° ISS orbit, a 92.6 min period and free rotation near 3°/s on each axis. OreSat's budget supplies its own orbit assumptions, modes and load schedules. Retain each source's assumptions. Numerical comparisons use 1% tolerance in both missions, and categorical inputs require exact agreement. |
| FR-14 | Shrestha et al. (2022), IAC power performance paper, Tables 2–4, and the OreSat 2019 power budget | The BIRDS-4 tables give 1604, 1202 and 801 mWh available at the load, six BCR-output simulation results and 1438 mWh nominal consumption. OreSat reports a 1011 mWh standby energy surplus. Each mission's budget and balance results must meet 1% separately. Full mission BOL/EOL sizing and installed array area still lack complete published output references for both missions. |
| FR-15 | OreSat battery research and Solar Cell Selection spreadsheet | Battery alternatives include lithium-ion, lithium iron phosphate and lithium titanate, with published capacity estimates of 74.88, 29 and 25 Wh. The solar spreadsheet publishes five power outputs from 2952.5 to 6055 mW with an explicit common numerical multiplier. Environmental conditions and complete compatibility findings remain incomplete. |
| FR-15 | Shrestha et al. (2026), Section III and Tables 3–5 | The proposed BIRDS-4 hybrid case has ten triple-junction and six small monocrystalline cells and a reported 3.023 Wh per orbit. Its immediate context explicitly specifies +X Sun tracking, beta 23.5° and 1362 W/m². The BIRDS-4 hybrid layout, wiring and loss mapping remain incomplete. Table 5 imports KITSUNE mass and inertia values. It is separate from the flown BIRDS-4 configuration and its original free-rotation budget. |
| FR-16 | BIRDS-4 safety paper, Section 2.2 and Table 5, OreSat battery research and bus paper | BIRDS-4 uses two-cell solar strings and a 3S2P, 3800 mAh battery. OreSat's card has two independent 2S packs and 37.4 Wh capacity. Its battery trade gives 74.88, 86.4 and 64.8 Wh against 80 Wh. Compare capacities within 1% for each mission and require exact counts, arrangements and findings. BIRDS-4 alternative arrangement cases remain missing. |
| FR-17 | OreSat battery research and solar hardware revision history | The study discusses 1S, 2S and 4S buses. The history records the SPV1040 rejection after the change from 1S to 2S. The historical README calls LT1618 a buck-boost converter, while its manufacturer datasheet and the later design notes identify the implemented boost topology. Retain that discrepancy. |
| FR-17 | BIRDS platform ICD, Section 6.3, pages 22–23, and BIRDS-4 battery verification report, Table 8-2, page 42 | The ICD specifies a 5 V boost line and 3.3 V buck-boost lines. The battery report gives five measured LTC3119 input voltage/current and output voltage points. Output current and efficiency are absent. These support selected operating-point checks, not a full converter alternative comparison. |
| FR-18 | Shrestha et al. (2021), Figures 13–14, pages 6–7 | The Maya-2 +Z panel I–V and P–V curves have printed numerical point labels. Figure 14 labels a peak of 1.575 W. Use the labelled values as references. Unlabelled graph coordinates do not establish 1% measurement precision. |
| FR-18 | OreSat solar sweep, worksheet `minicom.cap`, rows 2–206, columns F–H | There are 205 published current, voltage and calculated power triplets. F197 = 373.04 mA, G197 = 4.435 V and H197 = 1.6544324 W. The published formula is H = F × G / 1000. The sweep has repeated voltages and lacks short/open-circuit endpoints. It directly supports sampled power calculations. It does not satisfy the current complete-curve input contract without additional processing and endpoint assumptions. |
| FR-19 | Mission budgets, recovered Lay et al. full text, and related Rojas et al. experiment | No complete mission-specific paired DET/ideal-MPPT case was found for either mission in the checked sources. Rojas et al. supplies a related generic Kyutech DET comparison and an analytical ideal-MPP reference, using a different battery configuration. Its physical converter branch uses fixed near-MPP regulation. The missing evidence concerns mission applicability and matched operating-point/bus-power outputs, not actual tracker dynamics. |
| FR-20 | OreSat battery card design notes | A 30 W load gives 5.0, 4.17 and 3.57 A at 6.0, 7.2 and 8.4 V. The notes give separate firmware and hardware thresholds, release settings and fuse ratings. The current calculations are published outputs. Thresholds supply inputs to static comparisons. Firmware recovery logic is outside the implemented analysis scope. |
| FR-20 | Shrestha et al. (2021), Section 3.6, pages 7–8 | The BCR test uses input at or above 4.8 V and reports output near 4.2 V, below the stated 4.8 V overcharge boundary. This is a regulator-limiting experiment. Its measured voltage can supply an operating case, but it does not directly verify a declared detector's no-trip comparison. |
| FR-20 | BIRDS platform ICD, Section 6.3 | Published overcurrent thresholds are 4 A for Unreg1, 3 A for Unreg2 and 2 A for the regulated lines. |

## Remaining evidence gaps by mission

Updated after the additional search on 13 November 2026.
These are findings within the checked sources, not claims that further evidence does not exist.
The identifiers follow the current MOP table, which separates budgets in MOP-14a from sizing in MOP-14b.
No MOP was revised during this research.

| MOP | BIRDS-4 | OreSat |
| --- | --- | --- |
| MOP-12 | A published 162 g cell sum is available. Complete EPS mass, occupied volume and allocation margins remain incomplete | Published hardware subassembly masses and thermal model mass sums are available at different boundaries. Complete EPS volume and allocation margins remain incomplete |
| MOP-14a | Published state-power products and budgets are available. Complete orbit/attitude generation inputs are missing for some cases, and some printed budget arithmetic is inconsistent | Published state powers, interval/session energies and budgets are available. Complete orbital variation cases and applicable geometric generation inputs remain incomplete |
| MOP-14b | Baseline capacities and installed counts are available. Mission cycle-life/DoD sizing, BOL/EOL sizing and required array area outputs remain missing | Baseline capacities and shelf-life calculations are available. Shelf life does not establish mission cycle-life/DoD sizing, BOL/EOL sizing or required array area |
| MOP-15 | A proposed solar hybrid result is available with incomplete layout and loss mapping. A common-condition battery chemistry trade was not found | Published solar and battery trade calculations are available. Environmental conditions and full charger/installation compatibility remain incomplete |
| MOP-16 | Baseline arrangements and panel-loss cases are available. Another battery arrangement and a complete alternative array wiring/feasibility case were not found | Published battery alternatives and a proposed silicon arrangement are available. The latter lacks a fully specified numerical power and installation case |
| MOP-17 | Five measured converter operating points supplement rail specifications. Complete alternative-converter and terminal-current outputs remain incomplete | New OPD supply compatibility calculations supplement converter ratings. They do not establish a complete numerical converter-alternative benchmark |
| MOP-18 | Labelled panel points and a 1.575 W peak remain available. Full condition/efficiency and electrical-limit references remain incomplete | Published V×I products are available. The sweep lacks the endpoint and ordering properties required by the current complete-curve operation |
| MOP-19 | No complete mission-specific matched DET/ideal-MPPT operating-point and bus-power case was found | The full AIAA paper documents an MPPT converter and future characterization. No matched DET counterpart was found |
| MOP-20 | Battery-terminal observations and rail thresholds are available. A detector-specific normal-case UV/OV/OC result set was not found | Nominal calculated trip settings, normal heater/load calculations and protection policies are available. Complete normal-case extrema, conservative detector tolerances and matching no-trip findings remain incomplete |

Each gap concerns the named mission.
Evidence from another mission or a generic testbed remains separately identified.

## Academic publications checked in full

1. **Kim, S., Yamauchi, T., Masui, H. and Cho, M. (2021). BIRDS BUS: A Standard CubeSat BUS for an Annual Educational Satellite Project.** *Journal of Small Satellites*, 10(2), 1015–1034. Page 1025 explicitly explains the LTC3119 selection for maximum power point control and the move from three BCRs to one to remove blocking-diode losses. This replaces the textbook as the main BIRDS COTS selection reference. [Public full text](https://jossonline.com/wp-content/uploads/2021/07/Kim-first-pg.pdf). Citation key: `kim2021birdsbus`.
2. **Greenberg, A. et al. (2021). OreSat: A Student Team-Based Approach to an Inexpensive, Open, and Modular (1–3U) CubeSat Bus.** 35th Annual Small Satellite Conference, SSC21-WKI-09. Page 5 gives frame masses of 342, 710 and 1083 g for 1U, 2U and 3U and a complete OreSat0 mass of 1.288 kg. These are structural and spacecraft masses, not EPS masses. Page 6 gives two independent 2S packs per card, 5200 mAh and approximately 37.4 Wh per card. The paper uses the Tenergy UL listing label MH48285. The exact 30005-0 identity comes from the existing BOM and design notes. [Proceedings record and paper download](https://digitalcommons.usu.edu/smallsat/2021/all2021/236/). Citation key: `greenberg2021oresat`.
3. **Shrestha, H. R. et al. (2021). Verification of the 1U Standard CubeSat Electrical Power System (EPS) for the International Space Station (ISS) Safety Requirements.** 72nd International Astronautical Congress, IAC-21-C3.3.1, 9 pages. Figures 13–14 contain the measured Maya-2 +Z I–V/P–V curves and numerical labels. Section 3.6 and Figure 18 give the BCR overvoltage test. Tables 5–6 give the battery arrangement and measured bus voltages. [Official record](https://iafastro.directory/iac/paper/id/62691/summary/). [Public author copy](https://www.researchgate.net/publication/371957109_VERIFICATION_OF_THE_1U_STANDARD_CUBESAT_ELECTRICAL_POWER_SYSTEM_EPS_FOR_THE_INTERNATIONAL_SPACE_STATION_ISS_SAFETY_REQUIREMENTS). Citation key: `shrestha2021birdssafety`.
4. **Shrestha, H. R. et al. (2022). Results of BIRDS-4 Satellite On-Orbit Power Performance for Enhancing 1U Satellite Power System Reliability.** 73rd International Astronautical Congress, IAC-22-C3.3.12, 8 pages. Tables 2–4 on page 6 give the worst-case, simulation and nominal load budgets. [Official record](https://iafastro.directory/iac/paper/id/67756/summary/). [Public author copy](https://www.researchgate.net/publication/402618792_RESULTS_OF_BIRDS-4_SATELLITE_ON-ORBIT_POWER_PERFORMANCE_FOR_ENHANCING_1U_SATELLITE_POWER_SYSTEM_RELIABILITY). Citation key: `shrestha2022birds4powerperformance`.
5. **Shrestha, H. R. et al. (2026). Improving the Reliability of a CubeSat Power System by Combining Small-Sized Monocrystalline Cells With Triple-Junction Solar Cells.** *IEEE Access*, 14, 25038–25054. Section III reports the simulated BIRDS-4 hybrid case with ten triple-junction and six small monocrystalline cells, producing 3.023 Wh per orbit. Table 5 and the surrounding text describe the simulation inputs. The physical ground and flight validations concern MicroOrbiter-1 and CURTIS, not BIRDS-4. [DOI and full text](https://doi.org/10.1109/ACCESS.2026.3664750). Citation key: `shrestha2026solarreliability`.
6. **Jara, A. et al. (2022). On-orbit electrical power system dataset of 1U CubeSat constellation.** *Data in Brief*, 45, 108697. Section 2 reports orbit, attitude, component arrangements and acquisition conditions. [DOI and article](https://doi.org/10.1016/j.dib.2022.108697). Citation key: `jara2022birdsepsdataset`.

### Additional academic full texts checked on 13 November 2026

**Lay, D. A., Semerjian, G., Simpson, M., Das, M. and Greenberg, A. (2021). An Open Source and Modular CubeSat Solar Array with an Integrated Variable Step Incremental Conductance Maximum Power Point Tracker.** AIAA SciTech 2021 Forum, AIAA 2021-0804. [DOI](https://doi.org/10.2514/6.2021-0804). The seven-page full text was obtained through existing authorized institutional browser access using the publisher's visible [PDF link](https://arc.aiaa.org/doi/pdf/10.2514/6.2021-0804?download=true). A freely available author or institutional mirror was not found in the checked routes. Sections V–VI describe voltage versus current control within an MPPT converter. Section VII explicitly places extensive characterization and efficiency measurements in future work. The paper supplies no paired DET/MPPT numerical case. Its historical 66 Wh storage estimate uses four 2S, 2.3 Ah packs and remains separate from later 2.6 Ah configurations.

**Rojas, J. J., Yamauchi, T. and Cho, M. (2020). A Lean Satellite Electrical Power System with Direct Energy Transfer and Bus Voltage Regulation Based on a Bi-Directional Buck Converter.** *Aerospace*, 7(7), 94. [Open full text](https://doi.org/10.3390/aerospace7070094). The 19-page paper gives a matched generic 1U laboratory experiment, with common illumination, load profile and initial battery voltage. It uses two parallel NCR18650B Li-ion cells, rather than BIRDS-4's NiMH pack. Its physical converter branch regulates near MPP at 4.8 V. Equations 12–14 supply an analytical ideal-MPP reference, which is relevant to the implemented ideal-MPPT analysis. Actual tracker dynamics are unnecessary for that comparison. Complete BIRDS-4/OreSat matched static outputs and the applicable time-varying inputs remain missing. Table 7 reports ±2.03% power and ±2.87% efficiency uncertainty, so a 1% numerical criterion would not establish 1% physical accuracy.

**Cordova-Alarcon, J. R. et al. (2022). Attitude determination and control system for the 6U CubeSat KITSUNE.** 33rd ISTS, paper 2022-f-40. [Public author record](https://www.researchgate.net/publication/363263924_Attitude_determination_and_control_system_for_the_6U_CubeSat_KITSUNE). Table 2 on PDF page 5 gives KITSUNE mass 7.268 kg and the same six inertia values reproduced by the 2026 hybrid article's Table 5. This resolves their origin. It supplies no replacement BIRDS-4 parameter mapping.

## Additional source links and locators

1. **BIRDS Program Digital Textbook**, revision G, 6 July 2021. Sangkyun Kim, George Maeda and Mengu Cho. Pages 14–15 explain the LTC3119 selection, maximum power point control and power capability. [Published PDF](https://github.com/BIRDSOpenSource/BIRDS-GeneralDocumentation/blob/76cf923be9dc7e923e7397b5426c5b1e3d3f41c6/BIRDS%20Program%20Digital%20Textbook_RevG_ENGLISH_2021JUL06.pdf). Citation key: `kim2021birdstextbook`.
2. **BIRDS Platform Interface Control Document**, revision F, 3 March 2021. Section 6.3 gives regulated lines and overcurrent thresholds. Section 6.4 gives a platform battery specification that differs from some BIRDS-4 budget values. [Published PDF](https://github.com/BIRDSOpenSource/BIRDS-GeneralDocumentation/blob/76cf923be9dc7e923e7397b5426c5b1e3d3f41c6/BIRDS_Platform_ICD_ENGLISH_RevF_0303.pdf). Citation key: `kyutech2021birdsicd`.
3. **OreSat: Oregon's First Nanosatellite**, NASA CSLI application, 22 November 2016. Section D.2, pages 21–22, contains the mass budget. Section D.3 describes the corresponding early hardware. [Published PDF](https://github.com/oresat/oresat.github.io/blob/0d879a503be4a6d48e849f3088524c2748503640/pub/OreSat_CSLI_Application-2016.pdf). Citation key: `oresat2016csli`.
4. **Battery Pack and Cell Requirements and Research**, undated OreSat design study. Sections “Background and Some Design Decisions”, “Requirements” and “Choice #1” through “Choice #4” give the trades. It is linked from the battery card design notes. [Public document](https://docs.google.com/document/d/1tGRrhCfbk0fJJVCt0csk0iamH-1ZTGMi4msohmOQFPg/edit). Citation key: `oresatbatteryresearch`.
5. **OreSat Battery Card Design Notes**, stated update 4 March 2025. Relevant sections are “Choosing ABLIC cell protection ICs part numbers”, “Circuit Breaker / Resettable Fuses / PTC fuses / eFuse”, “Enabling Charging and Discharging” and “Fuel Gauge: MAX17205”. [Public document](https://docs.google.com/document/d/1yaPGtJSM5RQG5k7sVpsDxBkVu4CHtm4LMNnisgOaNRg/edit). Citation key: `oresat2025batterydesign`.
6. **OreSat Solar Module Design Notes**, stated update 2 February 2025, with later dated additions. Relevant sections are “Solar Cells: GaAs”, “Solar Cells: Si”, “LT1618 Design Notes”, “Power and Efficiency Apriori Analysis” and “Testing: Ground”. [Public document](https://docs.google.com/document/d/1mogZjYhJievwLsnVkg4Q0sEF9xPMA5q7KPciky3YWKE/edit). Citation key: `oresat2025solardesign`.
7. **OreSat Solar Modules**, historical hardware documentation at the v5.3 revision already used by the catalogue. The “Rev 2 Design” section explains the SPV1040 voltage incompatibility. [Published revision](https://github.com/oresat/oresat-solar-hardware/blob/47d610c1964c31f049a8f9844f7881931b5d0f06/README.md). Citation key: `oresatsolarhistory`.
8. **OreSat solar module ground test spreadsheet**, linked as “data” in “Testing: Ground” of the solar design notes. Use worksheet `minicom.cap`, rows 2–206, columns F–H. [Public spreadsheet](https://docs.google.com/spreadsheets/d/1vNrHLC0C6YMA_wZTWuHt7_7BPwSQPb8aQuyxLQmDAQ8/edit). Citation key: `oresatsolarsweep`.
9. **OreSat Power Budget**, 30 September 2019. [Published PDF](https://github.com/oresat/oresat.github.io/blob/0d879a503be4a6d48e849f3088524c2748503640/pub/OreSat_Power_Budget_190930.pdf). Existing citation key: `oresat2019powerbudget`.
10. **BIRDS-4 1U CubeSat Missions and On-Orbit Results**, Hari Ram Shrestha and colleagues, 11th Nano-Satellite Symposium, 2022. Section 5, page 3, reports 1604 mWh with five panels, 1202 mWh with four panels and 1438 mWh nominal consumption. It explicitly identifies the four-panel energy deficit. [Published paper](https://nanosat11th.itu.edu.tr/assets/papers/BIRDS-4.pdf). Citation key: `shrestha2022birds4results`.

## Interpretation safeguards

- The original BIRDS power presentation is publicly available at [the project website](https://birds-project.com/open-source/pdf/Power-Budget-Analysis-for-1U-satellit20220514.pdf), located through reference 53 of the IEEE Access article. It matches the retained BIRDS-4 budget PDF byte for byte.
- The former `www.oresat.org/pub/` PDF URLs return HTTP 404. The links above use the public website repository at a fixed revision. The archived 2019 budget matches the retained PDF byte for byte.
- Keep the 2016 OreSat mass case separate from its 2019 power budget and later Tenergy/Spectrolab flight hardware.
- The BIRDS-4 IAC power paper gives 1202 mWh for its four-panel case and 801 mWh for its three-panel case. Its Table 2 uses 240 mWh blocking-diode loss for every panel count. Presentation page 13 uses 192 and 144 mWh losses for four and three panels, producing 1240 and 878 mWh. These are different published loss assumptions. Retain separate cases, rather than treating the different outputs alone as an arithmetic error.
- The 2026 hybrid article explicitly places the 3.023 Wh BIRDS-4 result in a +X Sun-tracking paragraph. Earlier free-rotation wording remains unmapped to separate runs. Table 5's mass and inertia originate in KITSUNE, while the BIRDS-specific hybrid layout, wiring, loss boundary and lifetime conditions remain incomplete. Do not label the result as flight validation or combine it with the original free-rotation budget. The article's 743 mWh receive-only figure belongs to BIRDS-3. It does not replace the BIRDS-4 nominal 1438 mWh reference.
- The 2021 safety paper names the solar cell 3G30C-advanced and prints a 30.18 m² cell area in Table 4. Other BIRDS sources identify 3G30A and 30.18 cm². Preserve and flag these source discrepancies. Do not silently replace one model or unit with another.
- The 2016 mass table has inconsistent line sums and reports an approximate spacecraft margin. Preserve the printed values and flag discrepancies. Do not introduce corrected reference totals.
- A geometric allocation and a reported fit decision do not supply a numerical occupied volume reference.
- The solar sweep's raw power column B differs from its calculated power column H. Preserve both meanings. The MOP uses the explicit published calculation in H, without asserting that the raw power calibration is validated.
- Published solar power estimates and measured ground sweep values have different environmental conditions. Reproducing a published calculation does not demonstrate 1% physical prediction accuracy.
- Battery firmware thresholds and ABLIC hardware thresholds are separate protection layers. The selected S-8209AAA hardware has published overcharge detection/release values of 4.10/4.00 V and overdischarge detection/release values of 2.50/2.70 V. The firmware policy disables discharge below 3.0 V or 20% SOC and uses separate recovery criteria.
- A regulated constant-voltage converter remains distinct from a direct energy transfer connection.
- FR-01 to FR-11 and FR-13 were outside the additional evidence search. Their committed MOPs were left unchanged.

## Additional mission evidence search, 13 November 2026

Three internet-enabled researchers covered BIRDS-4, OreSat, and the solar-path/hybrid-study bottlenecks.
The search included mission-owned repositories, developer theses, newsletters, institutional proceedings, public engineering documents, spreadsheets, saved model outputs and the cited papers' references.
The findings below distinguish new sources from new passages in already known sources.
They document evidence availability and leave the MOP definitions unchanged.

### BIRDS-4 battery verification report: new primary source

**Title:** *Battery (Cells) Screening Procedures and its Verification Report*, document header `24_Battery Verification Report`.
**Team:** Kyushu Institute of Technology, with Hari Ram Shrestha and colleagues.
The combined report includes BIRDS-4 September 2020 test results and later screening instructions.
**Source:** [Mission repository PDF at revision d7eadd98f5327e1ddea82b640293d49bfdb09555](https://github.com/BIRDSOpenSource/BIRDS4-ProceduresAndReports/blob/d7eadd98f5327e1ddea82b640293d49bfdb09555/Battery%28Cells%29%20Screening%20Procedures%20and%20its%20verification%20Report_V1.0%20%282%29.pdf).

- **Page 21, Figure 1-1:** explicitly publishes **27 g × 6 = 162 g**, **1.2 V × 3 = 3.6 V**, a **3S2P** arrangement and **3800–4000 mAh** capacity. The mass calculation is a direct FR-12 cell-sum reference. It excludes the battery box, heater, insulation, wiring, connectors and other EPS hardware. The figure is an image and was checked visually.
- **Pages 32–33, Table 7-1:** identifies the six flight cells allocated to each satellite, with individually measured masses and capacities. These measurements differ from the separate nominal 27 g estimate and must remain separate cases.
- **Page 41:** publishes assembled-pack capacities on 9 September 2020 of **3783.4 mAh GuaraniSat-1**, **3779.5 mAh Tsuru** and **3785 mAh Maya-2**. Two-day capacity losses are **11.2, 12.2 and 10 mAh**, with reported daily losses **0.15%, 0.16% and 0.13%**. These are measured room-temperature baseline/self-discharge results, not mission EOL sizing outputs.
- **Page 42, Table 8-2:** gives the following LTC3119 test points. The report states an allowed input range of **2.5–18 V** and a battery overcharge boundary of **4.8 V**.

| Input V | Input A | Output V | Test condition |
| ---: | ---: | ---: | --- |
| 4.654 | 0.604 | 4.229 | Constant voltage |
| 5.000 | 0.460 | 4.219 | Constant voltage |
| 6.000 | 0.383 | 4.219 | Constant voltage |
| 7.000 | 0.330 | 4.219 | Constant voltage |
| 8.000 | 0.289 | 4.219 | Constant voltage |

These measured voltages support sourced operating-point conditions and voltage-limit checks.
The framework does not predict the regulator's physical voltage response.
Output current and efficiency are absent from this table.
The test addresses regulator limiting, rather than a declared detector's no-trip behavior.

### BIRDS-4 historical budgets and observations: new sources

**Jara Cespedes et al. (2021), *An Overview of the BIRDS-4 Satellite Project and the First Satellite of Paraguay*, SSC21-WKIII-03.** [Proceedings record and paper](https://digitalcommons.usu.edu/smallsat/2021/all2021/245/).
Table 1 on page 4 prints **2184 mWh source energy**, **360 mWh diode loss**, **80% BCR efficiency** and **1411 mWh after BCR**.
The printed calculation is inconsistent: independently evaluating its formula gives 1459.2 mWh, which is an audit result, not a replacement published reference.
Table 3 on page 8 gives **1411/1178/821 mWh** simulation results for five/four/three panels.
These historical cases remain separate from the 2022 budgets.
Page 7 reports Tsuru battery-terminal voltage around **4.2 V**, nominal discharge around **250–280 mA**, and around **400 mA** during CW transmission.
Those battery currents cannot be compared directly with individual rail OCP thresholds.

**Earlier mission calculation slides:** [Power consumption/generation, BIRDS-4](https://github.com/BIRDSOpenSource/BIRDS-FAQ-References/blob/d04739936ae3ea29f9f721a696d2420ad05f6679/151_Power_consumption_generation_BIRDS4.pdf).
Page 9 supplies explicit products including **428 mW × 1.5 h = 642 mWh**, **144 mW × 1 h = 144 mWh** and **280 mW × 0.5 h = 140 mWh**.
Page 3 repeats the inconsistent older BCR budget.
The 2022 presentation's separate slide 8 labels its left group **beta 30°, eclipse 35 min**, and its right group **beta 73°, eclipse 0 min**.
Slide 13 is the distinct beta 0° case.

**Newsletter evidence:** Hari Ram Shrestha, *BIRDS-4: Solar panel functionality based on sun simulator tests*, [BIRDS Newsletter 48, pages 77–79](https://birds1.birds-project.com/files/BIRDS_Newsletter_Issue_No_48.pdf).
The source gives a **50 mA** sweep increment and panel plots for all three satellites.
It lacks labelled numerical point coordinates, a calibrated irradiance value and a controlled temperature adequate for a new 1% curve reference.

**Generation safeguard:** [BIRDS bus Questions List, question 40](https://birds-project.com/open-source/pdf/BIRDS_bus_Questions_List.pdf) supplies masses including a **267 g battery box**, **36 g FAB** and **33 g OBC/EPS**, but explicitly labels them **BIRDS-5**.
They are related evidence and cannot fill the BIRDS-4 mass gap.
A mission-hosted developer thesis by Yuji Sasaki supplies solar installation procedures and BIRDS-4 thermal testing, while its tabulated 3G30A component properties are introduced as BIRDS-3 data.
Neither source supplies a BIRDS-4 EPS occupied-volume or required-area calculation.

### OreSat solar selection spreadsheet: new published calculation trade

**Title/team:** *Solar Cell Selection*, OreSat/PSAS, undated.
**Source:** [Mission-linked spreadsheet](https://docs.google.com/spreadsheets/d/15n9CXiEv7sbkS53eMZBUrHc1U8VdNBw8xGGn412ABSw/edit), linked from the solar design notes' GaAs research discussion.
**Locator:** `Sheet1`, rows 2–6, columns H, I and K.
The I-column values are saved published results of **(K/8) × 2.5 × H**.

| Product | H: device Pmp, mW | K: count per OreSat | I: maximum power supplied to OPD, mW |
| --- | ---: | ---: | ---: |
| Alta, comparison only | 1181 | 8 | 2952.5 |
| Azur HNR 0003401-01-01 | 1211 | 16 | 6055 |
| Azur HNR 0003805-01-01 | 1211 | 16 | 6055 |
| Azur HNR 0006051-01-01 | 1064 | 16 | 5320 |
| Spectrolab 047480-002 | 1170 | 15 | 5484.375 |

The numerical multiplier is explicit.
Its physical derivation, irradiance, temperature, lifetime condition and power-path loss boundary are unspecified.
The Spectrolab count is printed as **15** and must remain unchanged.
These are published scalar trade calculations, not complete installation or common-environment feasibility results.

### OreSat OPD supply and protection calculations: new sources

**OPD Design Notes:** [Public team document](https://docs.google.com/document/d/1NOkO6gGEJUFRpOrkwClRlZlzWuTLteq6fP9LPf_Ez0M/edit), stated update 22 August 2021.
The section “Powering the OPD (VPD)” publishes a **3.3 V supply**, **100 Ω series resistor**, **2.0 mA worst-case load**, **0.2 V drop** and **3.1 V available**, followed by an explicit acceptable-supply finding against the ICs' **2.7 V minimum**.
This is related static supply-compatibility evidence.
It is not a converter-alternative or UV-detector experiment.

**OPD Circuit Breaker Designs:** [Public team spreadsheet](https://docs.google.com/spreadsheets/d/1PE7U5m56bN0CZ0h20G8QKrn_dD4fJunBUuOQCO6Czg8/edit).
`Sheet1`, design columns C/F/I/L/O, supplies a **40.96 V/V gain**, **1.21 V reference**, shunts **0.1/0.02/0.01/0.015/0.03 Ω**, and the relevant divider ratios.
Row 18 publishes trip settings of **0.2954101563/1.477050781/2.954101563/1.969401042/5.908203125 A**.
The final design uses an IOUT divider of **1/6**, while the others use **1**.
Rows 20–21 flag that design **`> REF VOLTAGE`** and **159.6811655% of PFET Imax**.
These are genuine setting/rating calculations.
FR-20 accepts declared thresholds rather than calculating resistor-defined settings, so they provide threshold inputs rather than a complete no-trip benchmark.
Normal load extrema and conservative threshold tolerances remain incomplete.

The known battery design notes additionally publish heater current/power states at **6.0/7.2/8.4 V** of **245/294/342 mA** and **1.47/2.12/2.88 W**.
Its local OPD setting changes from **300 to 375 mA** for heating.
The spacecraft-wide 30 W load must not be assigned to that local heater/electronics protection node.

### OreSat mass and configuration records: new limited evidence

**Thermal-model outputs:** [OreSat0.5 saved mass table](https://github.com/oresat/oresat-thermal/blob/8673eeb58f3923243ceec57ad32d70e34d966202/OreSat0.5/case0_mass_submodel.txt) and the same revision's `case0_mass_node.csv` give input addends and saved model sums.
The printed substrate masses include **BATTERY 0.03125 kg** and **SOLAR_PANEL 0.02390 kg**.
They are incomplete thermal submodels, not complete physical battery or EPS masses.
No occupied-volume or allocation-margin output accompanies them.

**Proposed silicon alternative:** an [OreSat developer review comment, 18–19 May 2025](https://github.com/oresat/oresat-solar-hardware/issues/53#issuecomment-2889288292) proposes two four-junction packages in series instead of eight-junction packages.
It predicts approximately **4.5 V**, half as many LTC4411 devices and **10–20 mW** more power.
It lacks the complete product, illumination and numerical calculation details needed for a 1% benchmark.

**Historical 2016 budget:** D.3.2 and D.15 of the already cited CSLI application publish four one-cell **3300 mAh** modules, **13.2 Ah / 47.52 Wh at 3.6 V**, **28.512 Wh at 60% DoD**, **616 mWh standby consumption** and **1018 mWh surplus**.
These are useful additional calculation references.
They remain separate from the 2019 four-2S-pack, **95.04 Wh**, **623 mWh standby**, **1011 mWh surplus** case.

### OreSat sampled solar power: new exact locators in known evidence

`minicom.cap!F197:H197` publishes **373.04 mA**, **4.435 V** and **1.6544324 W**.
`F2:H2` publishes **64.06 mA**, **4.77625 V** and **0.305966575 W**.
These directly support V×I calculations.
The 205 samples span **3.575–4.77625 V** and **64.06–389.94 mA**, with **134 distinct voltages**, repeated values and no short/open-circuit endpoints.
Selecting row 197 as the largest saved H value is an evaluator operation on published results, not a source-labelled claim of the true physical MPP.
The narrative's approximate **1.63 W** ground peak, **1.73 W AM0 prediction**, and **1.71 W net estimate** are distinct statements and conditions.

### BIRDS hybrid simulation: clarified applicability

The final [IEEE article](https://doi.org/10.1109/ACCESS.2026.3664750), pages 25042–25043, explicitly supplies **beta 23.5°**, **1362 W/m²** and **+X Sun tracking** near the **3.023 Wh/orbit** BIRDS result.
Earlier free-rotation wording remains unmapped to runs.
Table 3 supplies cell MPP values and active areas.
Table 5 supplies a roughly **7 kg** body and inertia values traced to the KITSUNE paper above, with **6.78 V**, **64% bus efficiency** and **91.4% converter efficiency** lacking a BIRDS-specific mapping.
The article separately gives a **3.80–4.20 V** BIRDS battery range.
Its BIRDS hybrid face layout, six-SSM wiring, circuit-boundary loss accounting, temperature and lifetime condition remain incomplete.
The associated public EPS dataset contains Tsuru telemetry, including battery-present/absent ground tests, rather than hybrid simulation inputs or a DET/MPPT pair.

The framework can represent the stated Sun-pointing condition.
Matching that condition alone does not establish reproduction of an SGP4/attitude simulation with the proposed Keplerian/scalar model.
Importing the published orbit energy as an input would verify neither generation calculation.
No simulation data export that closes these mappings was found in the checked publisher, author, dataset and repository routes.

### Search limits and excluded evidence

- Public BIRDS procedures, CAD, solar, FAB, OBC, FAQ references and EPS dataset repositories were inspected. CAD geometry was not recomputed into purported published volume results.
- OreSat design, testing, battery testing, solar/battery hardware, thermal, simulation and test-infrastructure repositories were inspected. Public spreadsheets and selected issue comments were followed from mission-owned documents.
- Searches included Kyutech and PSU/PDXScholar developer theses. Some Kyutech records timed out, one relevant PDXScholar PDF returned 403, and an older OreSat solar-information document returned 410. Their uninspected content receives no verification credit.
- The full Lay paper was read through authorized institutional access. Related public MPPT abstracts, slides and test plans added no matched DET counterpart. Future test plans are distinguished from completed measurements.
- A published OreSat soft-start report contains inrush simulations and prototype tests. They concern transient startup behavior and remain outside the current static FR-20 scope.
- The related Rojas experiment supplies useful DET and ideal-MPP reference methods. Its different battery and whole-orbit metrics prevent it from being treated as either mission's complete static benchmark.
- No complete EPS occupied-volume/margin, full mission BOL/EOL sizing, or complete mission-specific DET/ideal-MPPT pair was found in the checked sources for both missions. That search established the limits of published comparisons.

## Subsequent case-study execution

The accepted verification approach supplements mission evidence with explicit engineering assumptions and independent references.
The executed BIRDS-derived and OreSat-derived configurations are described in the Results chapter and the EPS Case Study Evidence appendix.
They are representative verification configurations, not full flight reproductions.

The retained driver, input declarations, original OreSat sweep and execution records are in `case-studies/`.
A subagent executed the retained bundle and its deterministic replay.
An independent reviewer separately recomputed selected results and exercised the public model.
The final 36 scenario groups contain 877 comparisons: 510 numerical values, 302 exact or structural values, 32 expected unknowns and 33 expected errors.
There are no unexpected mismatches.
The largest numerical deviation is 0.3307393%, from a rounded published BIRDS power label.

The mass cases retain the published 162 g BIRDS cell-only sum and the historical OreSat module sums.
Missing occupied volumes and allocations are supplied assumptions.
The OreSat solar occupied-volume case uses eight assumed 100 × 100 × 3 mm module envelopes, including boards and components.
Full solar sizing is assessed separately with BOL and EOL anchors.
The alternative array layouts, battery chemistry choices, generic transfer paths and detector assumptions are explicit.
The BIRDS 1.575 W measured peak remains unreconstructed.
MOP-18 therefore uses available published products and independent complete-curve references rather than requiring that inaccessible peak reconstruction.

Negative engineering findings are retained, including the original OreSat DET voltage incompatibility, illumination-dependent generation shortages and a supplied charger endpoint above the nominal cell OV threshold.
Agreement with these expected negative results verifies the calculations within their stated scope.
It establishes no flight performance, chronological energy delivery, tracker dynamics, detector tolerance qualification or complete mechanical fit.
