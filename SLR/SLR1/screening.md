# Screening Log

## Current screening snapshot

- Primary candidates screened from merged source: 81
- Kept in current `corpus.json`: 44
- Core in current `corpus.json`: 22
- Supporting in current `corpus.json`: 22
- Rejected from primary merged-candidate screening: 37
- IEEE Xplore parity screening addendum (2026-04-24): screened `7.csv`, `23.csv`, and `24.csv` from `searches/ieee-xplore-csv-drop/`; 36 raw rows → 26 unique titles. The addendum reaffirmed 10 already-kept papers, promoted 2 user-approved `core` papers into `merged_candidates.json` / `corpus.json`, and logged 14 rejected/not-added decisions.
- Kept papers with non-empty abstract text in `corpus.json`: 30 / 44
- User-approved overrides in this file: already applied
- Query provenance, recall audits, and merge/dedup details are maintained in `search-log.md`

## Screening rule actually applied

### Protocol criteria
- Applied the protocol as written: years 2013-2026, English-language conference/journal papers, nanosatellite/CubeSat context, MBSE-oriented studies only, and preference for system-level or EPS-level modeling with explicit verification/validation linkage for RQ3.
- For RQ1, preference was given to system-level or EPS-level MBSE models rather than other subsystem-level or non-MBSE modeling.
- For RQ2, outcomes had to be attributable to MBSE rather than to EPS technology choices alone.
- For RQ3, the strongest evidence required explicit verification / validation / IVV integration in or around the model.

### Reassessment method used in this revisit
- This Stage-1 revisit re-screened **all 40 papers that were previously kept** in `corpus.json` using improved abstract evidence recovered via exact-title enrichment queries in Semantic Scholar and Scopus, plus Google Scholar fallback only when the preferred sources still lacked usable abstract text.
- When a richer abstract was recovered, the paper was reassessed against the protocol using the abstract rather than relying mainly on title semantics.
- When no richer abstract could be recovered, the earlier title-led decision was retained unless the new metadata clearly contradicted it.
- Google Scholar fallback evidence was treated as **snippet-level support**, not as equivalent to a full publisher abstract.
- Records whose improved abstracts showed they were broader than nanosatellite/CubeSat scope, not clearly MBSE model studies, or not sufficiently aligned with the protocol were demoted or rejected.

## Reassessment changes and overrides applied in this update
| Paper | Year | Old tier | New tier | Basis | Notes |
|---|---:|---|---|---|---|
| Open-Source Data Formalization through Model-Based Systems Engineering for Concurrent Preliminary Design of CubeSats | 2024 | supporting | core | abstract-aware reassessment | Recovered abstract showed a generic CubeSat SysML model used as the central data source across preliminary-design phases, with explicit reuse and automated trade-off support. |
| CubeSat Model-Based System Engineering (MBSE) reference model - Development and distribution - Interim status | 2016 | supporting | core | user-approved subagent recommendation | Promoted after later review because it belongs directly to the main CubeSat reference-model lineage and reports continued SysML model development and application. |
| MODEL-BASED SYSTEMS ENGINEERING (MBSE)—WHAT GOOD IS IT? LESSONS LEARNED FROM SMALL SATELLITE PROJECTS | 2021 | supporting | rejected | abstract-aware reassessment | Recovered snippet read as a broad lessons-learned / overview paper rather than nanosatellite-specific primary modeling evidence under the protocol. |
| Enterprise modeling for CubeSats | 2014 | core | core | user override retained | Demotion to `supporting` was suggested after abstract-aware reassessment, but the user chose to keep it as `core` because of its role in the early generalized CubeSat modeling lineage. |
| Towards a Unified Modeling and Simulation Framework for Space Systems: Integrating Model-Based Systems Engineering with Open Source Multi-Domain Simulation Environments | 2025 | supporting | supporting | user override retained | Rejection was suggested after reassessment because the paper is broader than CubeSat-specific scope, but the user chose to keep it as contextual support. |
| CONCURRENT ENGINEERING PROCESS FOR ELECTRICAL ARCHITECTURE OF NANOSATELLITES PRELIMINARY PHASES | 2025 | supporting | supporting | user override retained | Rejection was suggested after reassessment because the contribution is workflow- and interoperability-heavy, but the user chose to keep it as EPS-adjacent support. |
| Developing a CubeSat System MBSE Reference Model – Interim Status #5 | 2019 | new candidate | core | citation-chasing continuation + full-text confirmation | Added as the missing 2019 bridge in the main CSRM lineage, with explicit CSRM application plus mission-specific validation/verification framing. |
| Preliminary Design of Satellite Systems through the Integration of Model-Based System Engineering and Agile Methodologies: Application to the 3ColStar Mission | 2024 | new candidate | supporting | citation-chasing continuation + exact-title recovery | Added as a nanosatellite / CubeSat Arcadia/Capella case study with strong requirements / architecture / interface consistency claims, but still broader and more process-oriented than the core lineage. |
| Model-based systems engineering to support the development of nanosatellites | 2014 | new candidate | core | citation-chasing continuation + full-text confirmation | Added as an early nanosatellite MBSE case study focused on requirements development, design validation, and model-linked onboard-software integration. |

## IEEE Xplore parity screening addendum (2026-04-24)

### Scope and rule
- Source files screened: `searches/ieee-xplore-csv-drop/7.csv`, `searches/ieee-xplore-csv-drop/23.csv`, and `searches/ieee-xplore-csv-drop/24.csv`.
- Deduplicated screening set: 36 raw IEEE CSV rows → 26 unique titles.
- Applied the protocol criteria as written: 2013-2026, English conference/journal records, nanosatellite/CubeSat or close small-satellite context, MBSE-oriented system/EPS modeling, MBSE-attributed outcomes for RQ2, and explicit IVV / verification / validation modeling for RQ3.
- User-approved override in this addendum: `Application of model-based systems engineering in small satellite conceptual design-A SysML approach` and `Automating Object-Oriented Functional Modeling for Standardized Design in the New Space Domain` were upgraded from my proposed rejection/borderline exclusion to `core`.
- This addendum records screening decisions from the new IEEE exports. The two user-approved core additions have now been promoted into `merged_candidates.json` and `corpus.json`; rejected/not-added addendum records remain logged only.

### Core decisions from the IEEE addendum
| Decision | Year | Title | Source CSV(s) | Status | Why core |
|---|---:|---|---|---|---|
| core | 2014 | Integrated model-based systems engineering (MBSE) applied to the Simulation of a CubeSat mission | `7.csv` | Reaffirmed existing core | Direct CubeSat mission-level MBSE model integrating SysML, analytical models, simulation, and requirements/design/analysis/verification support. |
| core | 2017 | Developing a CubeSat Model-Based System Engineering (MBSE) reference model — Interim status #3 | `7.csv` | Reaffirmed existing core | Direct CubeSat MBSE reference-model lineage with system-level SysML modeling and requirements/design/analysis/V&V framing. |
| core | 2018 | Application of model-based systems engineering in small satellite conceptual design-A SysML approach | `7.csv` | Added to current corpus as core | User upgraded to core. IEEE abstract frames SysML-based small-satellite conceptual design as addressing completeness/consistency, traceability, and change-impact assessment; retained as close nanosatellite-class/general system-level MBSE evidence for RQ1/RQ2. |
| core | 2021 | Mission Engineering and the CubeSat System Reference Model | `7.csv` | Reaffirmed existing core | Direct CubeSat System Reference Model / mission-engineering extension and central reusable CubeSat MBSE evidence. |
| core | 2021 | Towards Simulation of CubeSat Operational Scenarios under a Cyber-Physical Systems View | `23.csv` | Reaffirmed existing core | SysML/CPS workflow for CubeSat operational-scenario simulation, including power-consumption / data-generation analysis and early requirements verification. |
| core | 2023 | Development of a Nanosatellite System Modeling Architecture for EIRSAT-1 | `23.csv`; `24.csv` | Reaffirmed existing core | Direct nanosatellite system-modeling architecture case with MBSE, CubeSat/system-engineering, and verification/validation relevance. |
| core | 2023 | Open-source CubeSat MBSE Approach to Address Traceability: Power Subsystem | `7.csv` | Reaffirmed existing core | Strongest direct EPS paper: CubeSat power-subsystem SysML model, traceability, and requirement-fulfillment checking. |
| core | 2025 | Automating Object-Oriented Functional Modeling for Standardized Design in the New Space Domain | `7.csv`; `23.csv` | Added to current corpus as core | User upgraded to core. The abstract presents an automated object-oriented functional MBSE/System-as-Code approach for standardized satellite-platform digitalization, reuse, traceability, and functional alignment across New Space missions; retained as core generality/reuse evidence for RQ1/RQ2. |

### Supporting decisions from the IEEE addendum
| Decision | Year | Title | Source CSV(s) | Status | Why supporting |
|---|---:|---|---|---|---|
| supporting | 2013 | Model based systems engineering (MBSE) applied to Radio Aurora Explorer (RAX) CubeSat mission operational scenarios | `7.csv`; `24.csv` | Reaffirmed existing supporting | Direct CubeSat MBSE operational-scenario modeling with energy/data/resource constraints; useful but narrower than the core general-model lineage. |
| supporting | 2018 | A model-based systems engineering approach for technical measurement with application to a CubeSat | `7.csv` | Reaffirmed existing supporting | Relevant MBSE technical-measurement / traceability contribution applied to CubeSat, but not EPS-specific and narrower than core papers. |
| supporting | 2019 | Requirements Modeling Language and Automated Testing for CubeSats | `24.csv` | Reaffirmed existing supporting | Direct CubeSat requirements validation/testing support for RQ3, but not EPS-specific and not central enough for core. |
| supporting | 2022 | MBSE Challenges in the Concurrent Preliminary Design of CubeSats: Nanospace Study | `7.csv` | Reaffirmed existing supporting | Relevant CubeSat MBSE/concurrent-engineering integration context; useful for barriers/challenges, but contextual rather than review-defining. |

### Rejected / not-added decisions from the IEEE addendum
| Decision | Year | Title | Source CSV(s) | Why rejected / not added |
|---|---:|---|---|---|
| rejected | 2015 | Optimization of multi-satellite systems using integrated Model Based System Engineering (MBSE) techniques | `7.csv`; `24.csv` | Generic small-satellite / constellation optimization; not clearly nanosatellite/CubeSat-class and not EPS-specific. |
| rejected | 2016 | A concept for an Agile Mission Development Facility for CubeSat and suborbital missions | `7.csv`; `24.csv` | Facility/platform concept using SysML, not a direct nanosatellite mission or EPS MBSE model. |
| rejected | 2018 | Adopting MBSE in Construction Equipment Industry: An Experience Report | `7.csv`; `23.csv` | Non-space domain. |
| rejected | 2018 | An MBSE conceptual design phase model for inter-satellite communication | `24.csv` | MBSE ConOps for inter-satellite communication / VLC subsystem; not system-level nanosatellite/EPS modeling. |
| rejected | 2018 | Model-Based Semi-Physical Simulation Platform Architecting for Satellite Communication System | `7.csv` | Generic satellite communication simulation platform; not nanosatellite/CubeSat and not EPS. |
| rejected | 2018 | Radiation Assurance of CubeSat Payloads Using Bayesian Networks and Fault Models | `7.csv`; `24.csv` | CubeSat payload radiation/fault modeling; subsystem/payload reliability, not system-level or EPS MBSE outcomes. |
| rejected | 2019 | Enhanced Feasibility Assessment of Payload Adapters for NASA's Space Launch System | `24.csv` | SLS payload-adapter feasibility / launch-vehicle context; not nanosatellite/CubeSat MBSE. |
| rejected | 2020 | Applying Model-Based Systems Engineering to the Development of a Test and Evaluation Tool for Unmanned Autonomous Systems | `7.csv`; `24.csv` | UAS, not space/nanosatellite. |
| rejected | 2020 | Intersatellite Communication: An MBSE Operational Concept for a Multiorbit Disaggregated System | `7.csv` | Space-related MBSE OpsCon, but communication-system focused and not clearly nanosatellite/EPS/system-level CubeSat modeling. |
| rejected | 2022 | Reliability Analysis and Failure Mitigation Strategies for the PROVE Pathfinder CubeSat Payload | `7.csv`; `24.csv` | CubeSat payload reliability study; MBSE appears as one reliability-model component, but outcomes are payload/failure-analysis focused rather than EPS/system MBSE. |
| rejected | 2024 | A Semantic Approach to Spacecraft Verification Planning Using Bayesian Networks | `7.csv`; `24.csv` | Strong generic spacecraft verification/digital-engineering paper, but not nanosatellite/CubeSat and not EPS. |
| rejected | 2024 | A Tailored Systems Engineering Process for Developing Student-Built CubeSat Class Satellites | `24.csv` | CubeSat-class and MBSE-related, but primarily educational/process tailoring and cohort-performance evaluation rather than target system/EPS MBSE model evidence. |
| rejected | 2024 | Cardinal Effect in Bistatic SAR Imagery: Analysis and Physical Interpretation | `23.csv` | False positive from “Capella”; SAR imagery/physics paper, not MBSE. |
| rejected | 2025 | Calibration Platform for MEMS Gyroscopes used in Nanosatellite Attitude Determination and Control Systems | `24.csv` | Nanosatellite ADCS sensor calibration hardware/metrology; not MBSE and not EPS. |

## Core papers
| corpus_id | Decision | Year | Title | Evidence basis | Why core |
|---|---|---:|---|---|---|
| paper-0008 | core | 2014 | Enterprise modeling for CubeSats | snippet + user override | User-retained core anchor for the early generalized CubeSat modeling lineage despite limited abstract evidence. |
| paper-0001 | core | 2014 | Integrated model-based systems engineering (MBSE) applied to the Simulation of a CubeSat mission | abstract | Direct mission-level MBSE modeling and simulation paper for CubeSat design under resource and subsystem-coupling constraints. |
| paper-0079 | core | 2014 | Model-based systems engineering to support the development of nanosatellites | full text + citation chase | Early nanosatellite MBSE case study linking requirements development, design validation, executable SysML / Simulink coupling, and onboard-software development. |
| paper-0004 | core | 2015 | Developing a CubeSat Model-Based System Engineering (MBSE) Reference Model - Interim status | title+metadata | Foundational start of the CubeSat MBSE reference-model lineage and still review-defining for generalized CubeSat MBSE. |
| paper-0016 | core | 2016 | Developing a CubeSat Model-Based System Engineering (MBSE) reference model - Interim status #2 | title+metadata | Core continuation of the main CubeSat reference-model lineage and central for modeling evolution across the series. |
| paper-0031 | core | 2016 | CubeSat Model-Based System Engineering (MBSE) reference model - Development and distribution - Interim status | abstract + user-approved promotion | Core reference-model lineage paper reporting continued SysML model development, application to RAX, and model-enabled trade/simulation work. |
| paper-0002 | core | 2017 | A model-based systems engineering (MBSE) approach for defining the behaviors of CubeSats | title+metadata | Directly addresses defining CubeSat behaviors with MBSE, making it central to RQ1 even without richer abstract recovery. |
| paper-0005 | core | 2017 | Developing a CubeSat Model-Based System Engineering (MBSE) reference model - Interim status #3 | title+metadata | Core reference-model lineage paper that remains central to generalized CubeSat MBSE. |
| paper-0015 | core | 2017 | Validation and verification of MBSE compliant CubeSat reference model | abstract | Explicit validation/verification of a CubeSat MBSE reference model, making it key RQ3 evidence. |
| paper-0013 | core | 2018 | Developing a cubesat model-based system engineering (MBSE) reference model – Interim status #4 | title+metadata | Latest interim paper in the main reference-model lineage and still core for the maturation of reusable CubeSat modeling. |
| paper-0080 | core | 2018 | Application of model-based systems engineering in small satellite conceptual design-A SysML approach | IEEE abstract + user-approved promotion | User-approved core addition from the IEEE parity addendum; SysML-based small-satellite conceptual design evidence for completeness/consistency, traceability, and change-impact assessment. |
| paper-0077 | core | 2019 | Developing a CubeSat System MBSE Reference Model – Interim Status #5 | full text + exact-title chase | Closes the missing 2019 gap in the CSRM lineage and adds explicit mission-specific model validation / verification framing before the 2020–2021 CSRM papers. |
| paper-0011 | core | 2020 | Development and Application of the CubeSat System Reference Model | abstract | Confirms a mature reusable logical architecture for CubeSat systems and explicit MBSE-quality/reusability benefits. |
| paper-0039 | core | 2020 | Applying a Model-Based Approach to Develop a Standardized Template for CubeSat-class Satellites | abstract | Provides an explicitly reusable CubeSat template/model intended to reduce design time and propagate changes through the system model. |
| paper-0014 | core | 2021 | Mission Engineering and the CubeSat System Reference Model | abstract | Extends the CubeSat System Reference Model toward complete mission engineering and remains central to generalized mission modeling. |
| paper-0033 | core | 2021 | Towards Simulation of CubeSat Operational Scenarios under a Cyber-Physical Systems View | abstract | Confirms an explicit SysML-based workflow for simulating operational scenarios, including power-consumption-oriented analysis and early operations verification. |
| paper-0026 | core | 2023 | Open-source CubeSat MBSE Approach to Address Traceability: Power Subsystem | abstract | Strongest EPS-focused paper in the corpus, with direct power-subsystem SysML modeling plus traceability and requirement-fulfillment visibility. |
| paper-0063 | core | 2023 | Development of a Nanosatellite System Modeling Architecture for EIRSAT-1 | abstract | Explicit nanosatellite system-modeling architecture case that is central to recent RQ1-style practice. |
| paper-0023 | core | 2024 | Effective Model-Based Systems Engineering framework for academic nanosatellite project management and design | title+metadata | Central contemporary nanosatellite MBSE framework paper with no contradicting abstract evidence. |
| paper-0029 | core | 2024 | Open-Source Data Formalization through Model-Based Systems Engineering for Concurrent Preliminary Design of CubeSats | abstract | Promoted to core because the recovered abstract shows a generic CubeSat SysML model serving as a central data source across preliminary-design phases. |
| paper-0051 | core | 2025 | A Scalable Systems Architecture for CubeSat Test and Evaluation to Improve Mission Success | snippet | Snippet-level evidence still shows a direct CubeSat test-and-evaluation architecture contribution that is central to RQ3. |
| paper-0081 | core | 2025 | Automating Object-Oriented Functional Modeling for Standardized Design in the New Space Domain | IEEE abstract + user-approved promotion | User-approved core addition from the IEEE parity addendum; automated object-oriented functional MBSE/System-as-Code approach for standardized satellite-platform digitalization, reuse, traceability, and functional alignment. |

## Supporting papers
| corpus_id | Decision | Year | Title | Evidence basis | Why supporting |
|---|---|---:|---|---|---|
| paper-0003 | supporting | 2013 | Model based systems engineering (MBSE) applied to Radio Aurora Explorer (RAX) CubeSat mission operational scenarios | abstract | Relevant operational-scenario modeling under tight power/data/resource constraints, but narrower and earlier than the core general-model lineage. |
| paper-0010 | supporting | 2014 | Small satellite systems design methodology: A formal and agile design process | abstract | Supports pico-/nano-class MBSE plus formal-methods design process and traceability themes, but is broader than the core CubeSat-specific lineage. |
| paper-0012 | supporting | 2014 | Rapid model-based inter-disciplinary design of a CubeSat mission | title+metadata | Relevant contextual early mission-design evidence, but not strong enough to define the review on its own. |
| paper-0022 | supporting | 2015 | CubeSat Model-Based System Engineering (MBSE) reference model - Application in the concept lifecycle phase | abstract | Useful application of MBSE in the concept lifecycle phase, but still an application-focused extension rather than a review-defining core paper. |
| paper-0007 | supporting | 2018 | A model-based systems engineering approach for technical measurement with application to a CubeSat | abstract | Useful outcomes/measurement contribution, but narrower than the central general-model papers. |
| paper-0034 | supporting | 2019 | Requirements Modeling Language and Automated Testing for CubeSats | abstract | Direct CubeSat requirements validation/testing support for RQ3, but still supporting rather than core EPS-specific evidence. |
| paper-0070 | supporting | 2019 | Implementation of model based systems engineering (MBSE) tools to model cubesats systems | title+metadata | Directly relevant CubeSat MBSE-tooling paper, but richer abstract evidence was not recovered. |
| paper-0024 | supporting | 2020 | Analysis of MBSE/PLM Integration: From Conceptual Design to Detailed Design | title+metadata | Useful lifecycle-linkage and integrability context, but not central enough for core status. |
| paper-0068 | supporting | 2020 | Digital engineering information exchange model for space missions architecture: A case study of a cubesat mission | title+metadata | Relevant digital-engineering / information-exchange evidence in a CubeSat mission setting, though abstract recovery remained unsuccessful. |
| paper-0069 | supporting | 2020 | Nanosatc-br3 concept design using model-based systems engineering (Mbse) | title+metadata | Title-level evidence still indicates a relevant nanosatellite MBSE concept-design case, but usable abstract evidence was not recovered. |
| paper-0046 | supporting | 2022 | Investigating the Effectiveness of a Causal MBSE Software Tool in Modelling CubeSat Conceptual Design Data | title+metadata | Relevant tool-effectiveness/context paper for CubeSat conceptual design data modeling, but abstract recovery remained unsuccessful. |
| paper-0027 | supporting | 2022 | MBSE Challenges in the Concurrent Preliminary Design of CubeSats: Nanospace Study | abstract | Relevant concurrent-engineering / MBSE-integration challenges paper, but contextual rather than core. |
| paper-0071 | supporting | 2022 | A Model-Based Approach to Risk Management for RVSAT-1: a Student Nano-satellite Project - Using SysML | abstract | Clear SysML-based nanosatellite risk-modeling contribution, but not central enough to define the review on its own. |
| paper-0037 | supporting | 2023 | Model Based Systems Engineering with a Docs-as-Code Approach for the SeaLion CubeSat Project | abstract | CubeSat MBSE workflow/process-support contribution whose focus is documentation/process implementation rather than central system/EPS modeling. |
| paper-0059 | supporting | 2024 | An Implementation of Integrated Approach in Product Life-Cycle Management Tool to Ensure Requirements-In-Loop During Complex Product Development: A Cubesat Case Study | title+metadata | Useful requirements-in-loop / lifecycle integration context, but not strong enough for core status. |
| paper-0078 | supporting | 2024 | Preliminary Design of Satellite Systems through the Integration of Model-Based System Engineering and Agile Methodologies: Application to the 3ColStar Mission | abstract + full text | Strong Arcadia/Capella CubeSat case study with explicit traceability, interface consistency, and agile preliminary-design claims, but more process-centric and less review-defining than the core lineage. |
| paper-0061 | supporting | 2024 | Concurrent Model-Based Approach for CubeSat Mission Design | snippet | Snippet-level evidence supports a relevant collaborative/model-based CubeSat mission-design context, but the evidence remains thin and conference-contextual. |
| paper-0040 | supporting | 2025 | A model based system engineering approach for CubeSat structure and configuration management with highly constrained system design | abstract | Confirms a CubeSat MBSE tool/process contribution around structure/configuration management, but it is narrower than the main review-defining papers. |
| paper-0041 | supporting | 2025 | Applying Model-Based Systems Engineering on CubeSat Budget Calculating | abstract | Confirms automated mass/volume/power/energy budget calculation for CubeSat nanosatellites, but the contribution remains narrow and application-specific. |
| paper-0043 | supporting | 2025 | Towards a Unified Modeling and Simulation Framework for Space Systems: Integrating Model-Based Systems Engineering with Open Source Multi-Domain Simulation Environments | user-retained contextual | Broader-than-CubeSat contextual support for MBSE-simulation integration that the user chose to retain. |
| paper-0053 | supporting | 2025 | CONCURRENT ENGINEERING PROCESS FOR ELECTRICAL ARCHITECTURE OF NANOSATELLITES PRELIMINARY PHASES | abstract + user-retained contextual | EPS-adjacent preliminary-phase context around electrical architecture, power budgets, and concurrent engineering, retained by user choice despite weaker protocol fit. |
| paper-0054 | supporting | 2025 | Integrating Model-Based Systems Engineering into CubeSat Development: A Case Study of the BOREALIS Mission | abstract | Substantive CubeSat MBSE case study with trade-space and reusability discussion, but still a mission-specific supporting case rather than a core general model. |

## Rejected papers
| Decision | Year | Title | Reason category | Why rejected |
|---|---:|---|---|---|
| rejected | 2013 | Parametric CubeSat flight simulation architecture | weak/unclear MBSE evidence | Flight-simulation architecture paper is not clearly MBSE from title-level evidence. |
| rejected | 2014 | 13th International Conference on Space Operations, SpaceOps 2014 | proceedings | Conference proceedings record, not an individual paper. |
| rejected | 2014 | Effect of satellite formation architectures and imaging modes on albedo estimation of major biomes | not MBSE | Albedo-estimation science paper, not MBSE. |
| rejected | 2014 | System resilience framework and modeling for a cubesat system | weak/unclear MBSE evidence | Resilience-modeling paper is not clearly MBSE and not strong enough for retrieval. |
| rejected | 2016 | A concept for an Agile Mission Development Facility for CubeSat and suborbital missions | not target modeling study | Mission development facility concept is not a direct MBSE system/EPS modeling study. |
| rejected | 2016 | Effect of satellite formations and imaging modes on global albedo estimation | not MBSE | Earth-observation/science-performance study, not an MBSE nanosatellite system or EPS model paper. |
| rejected | 2016 | SPARC-1: A joint US/Sweden multi-mission modular nanosatellite platform | weak/unclear MBSE evidence | Recovered in the saturation pass, but the title/metadata indicate a modular platform paper without clear MBSE/system-model evidence. |
| rejected | 2018 | A university-based facility for evaluation and assessment of space projects | not target modeling study | Facility/infrastructure paper, not a target modeling study. |
| rejected | 2018 | Radiation Assurance of CubeSat Payloads Using Bayesian Networks and Fault Models | outside scope subsystem | Payload radiation/fault-model reliability paper does not attribute outcomes to MBSE system modeling. |
| rejected | 2019 | Model based systems engineering education with hands-on activities using CubeSat kit | education/tutorial | Education paper, not a target research study. |
| rejected | 2020 | A scheduling optimization using greedy knapsack algorithm for randev cubesat communication and observation missions analyzed with mbse activity diagram | weak/unclear MBSE evidence | Scheduling optimization with an activity diagram is algorithm/application focused, not a target MBSE model study. |
| rejected | 2020 | Model-based approach for requirements management connection with verification procedures applied to space systems | generic space systems | Framed at generic space-systems level rather than nanosatellite/CubeSat scope. |
| rejected | 2021 | Architecting an MBSE Black-Box System Model for the Physical Layer of a Visible Light Intersatellite Communication System | outside scope subsystem | Visible-light intersatellite communication physical-layer model is a non-EPS subsystem paper. |
| rejected | 2021 | From complex to complicated: development of a Model Based Systems Engineering and cyber security approach for a quantum key distribution nanosatellite. | outside scope subsystem | Cyber-security nanosatellite case is too specialized and not aligned with the EPS/verification focus. |
| rejected | 2021 | MODEL-BASED SYSTEMS ENGINEERING (MBSE)—WHAT GOOD IS IT? LESSONS LEARNED FROM SMALL SATELLITE PROJECTS | weak/unclear MBSE evidence | Rejected after abstract-aware reassessment because it reads as a broad overview / lessons-learned paper rather than primary nanosatellite modeling evidence. |
| rejected | 2021 | The Ground Segment: A proposal Framework based on concepts of Dynamic Management of the Space Link Extension Protocol Services. | outside scope subsystem | Ground-segment framework is outside the targeted nanosatellite mission/EPS MBSE scope. |
| rejected | 2022 | Architecture Framework Standardization for Satellite Software Generation Using MBSE and F Prime | outside scope subsystem | Software-generation architecture paper is subsystem/software focused, not system-level or EPS MBSE. |
| rejected | 2022 | Cost-Optimal System Performance Maps for Laser-Accelerated Sailcraft | not nanosatellite/CubeSat | Sailcraft performance paper is outside nanosatellite MBSE scope. |
| rejected | 2022 | Development of a Concurrent Engineering Tutorial as part of the ESA_Lab@ initiative | education/tutorial | Tutorial/teaching paper, not a target research study. |
| rejected | 2022 | Metric for Structural Complexity Assessment of Space Systems Modeled Using the System Modeling Language | generic space systems | Generic structural-complexity metric paper is not clearly nanosatellite/EPS-focused. |
| rejected | 2022 | Reliability Analysis and Failure Mitigation Strategies for the PROVE Pathfinder CubeSat Payload | outside scope subsystem | Payload reliability paper attributes outcomes to payload/failure analysis rather than MBSE. |
| rejected | 2023 | 6S CubeSat: a Student-made IOD Mission for Characterization of Perovskite Solar Cells and Structural Battery | not target modeling study | Mission technology paper on perovskite solar cells/structural battery, not MBSE. |
| rejected | 2023 | An Open-Source Method for Model-Based Development of Embedded Systems: Experience Report from a CubeSat Student Project | outside scope subsystem | Embedded-systems development experience report is not system-level/EPS MBSE. |
| rejected | 2023 | From design to delivery in three months: the fast development of a 3U CubeSat | weak/unclear MBSE evidence | Fast-development case paper is not clearly an MBSE modeling study. |
| rejected | 2023 | xSPANCION: Modular satellite platform design for scalable and adaptive production | weak/unclear MBSE evidence | Modular platform design paper lacks a clear MBSE system-model contribution for this review. |
| rejected | 2024 | 20th IFIP WG 5.1 International Conference on Product Lifecycle Management, PLM 2023 | proceedings | Conference proceedings record, not an individual paper. |
| rejected | 2024 | 57th IAA Symposium on Safety, Quality and Knowledge Management in Space Activities - Held at the 75th International Astronautical Congress, IAC 2024 | proceedings | Conference proceedings record, not an individual paper. |
| rejected | 2024 | A Tailored Systems Engineering Process for Developing Student-Built CubeSat Class Satellites | weak/unclear MBSE evidence | Systems-engineering process paper is not clearly an MBSE model paper. |
| rejected | 2024 | BOREALIS: A Multidisciplinary CubeSat Mission to Investigate Biofilm Radioprotection and Particle Interaction in Space | weak/unclear MBSE evidence | Mission-description paper without a clear MBSE contribution in title-level screening. |
| rejected | 2024 | FloripaSat-2: An Open-Source Platform for CubeSats | weak/unclear MBSE evidence | Platform/open-hardware paper without clear MBSE/system-model evidence. |
| rejected | 2024 | Micro-Satellite Systems Design, Integration, and Flight | generic space systems | Broad microsatellite design/integration paper without clear MBSE review fit. |
| rejected | 2025 | Assessment of large language models for use in generative design of model based spacecraft system architectures | not target modeling study | LLM/generative-design focus is outside the review scope. |
| rejected | 2025 | Ensuring Mission Success: A PA-QA approach in the AIV-T of the ELECTRA CubeSat | weak/unclear MBSE evidence | PA/QA-AIV-T operations paper without clear MBSE system-model evidence. |
| rejected | 2025 | Hierarchical Planning Applied to the Preliminary Design of CubeSats: Nanospace Study | weak/unclear MBSE evidence | Preliminary-design planning paper is not clearly an MBSE model paper from title-level evidence. |
| rejected | 2025 | LI Optical Lensing (LOL): Using the Earth as an Atmospheric Lens | not target modeling study | Optical-lensing mission concept is unrelated to the review scope. |
| rejected | 2025 | Riker & Laforge: Enabling Scalable and Efficient Satellite Manufacturing Through Integrated Information Management | not target modeling study | Information-management/manufacturing paper rather than an in-scope nanosatellite MBSE model study. |
| rejected | 2026 | 46th Academic Space Conference, 2022 | proceedings | Conference proceedings record, not an individual paper. |

## Screening confidence and corpus quality reflection
- **Highest confidence:** the main CubeSat MBSE reference-model / template / behavior / mission-architecture lineage is now well supported and coherently represented in the `core` tier.
- **High confidence:** `Open-source CubeSat MBSE Approach to Address Traceability: Power Subsystem` remains the strongest EPS-specific paper in the corpus.
- **Moderate confidence:** RQ3 is represented, but mainly through general CubeSat reference-model validation, test/evaluation architecture, requirements/testing support, and operational-scenario simulation rather than through a broad EPS-specific V&V literature.
- **Moderate-low confidence:** the **EPS-specific** subset remains sparse even after abstract enrichment; direct literature combining nanosatellite EPS modeling with explicit verification / IVV / test integration is still thin.
- **Residual uncertainty:** some retained papers remain title-led because preferred databases stayed abstract-empty and Google Scholar fallback was partly blocked. That uncertainty is now narrower than in the earlier Stage-1 version, but it has not disappeared completely.
- **Overall judgment:** the updated Stage-1 corpus is materially better justified for retrieval and synthesis than the earlier title-led version, while still preserving a small amount of user-approved contextual breadth in the supporting tier.
