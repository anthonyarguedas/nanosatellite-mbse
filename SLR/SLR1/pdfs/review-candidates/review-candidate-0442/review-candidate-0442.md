---
source: null
title: "review-candidate-0442"
page_count: 8
converted_at: "2026-09-08T14:58:31Z"
---

<!-- PDF_PAGE: 1 -->

IAC-25,B1,7,3,x100501

The Circle: Future Earth Observation System Architecture System of Systems Analysis from a Science Need Perspective

Vito Fortunato $ ^{a} $ , Leonardo Amoruso $ ^{a} $ , Vanessa Keuck $ ^{b} $ , Michael Zemp $ ^{c} $ , Maria J. Santos $ ^{c} $ , Jacqueline Bannwart $ ^{c} $ , Martin Reader $ ^{c} $ , Emmanuel Pajot $ ^{d} $ , Nicola Carraro $ ^{e} $ , Oscar Adrian Robalino Florett $ ^{e} $ , Matteo Nori $ ^{e} $ , Simonetta Di Pippo $ ^{e} $ , Thomas Dell $ ^{f} $ , Martina Felici $ ^{f} $

a Planetek Srl, via Massaua 12,

b ESA European Space Agency

c University of Zurich

d EARSC

$ ^{e} $ SEELab - SDA Bocconi

f D-Orbit

* Corresponding Author: fortunato@planetek.it

## Abstract

"The Circle" is an ESA-funded initiative aimed at designing a future-proof, science-driven Earth Observation (EO) reference architecture by analyzing and synthesizing system-of-systems (SoS) configurations. The project is driven by five high-priority Science Questions (SQs) identified in ESA's Earth Observation Science Strategy: the ocean carbon cycle response to anthropogenic $ \mathrm{CO}_{2} $ , cryosphere mass balance, ecosystem critical transitions, land biosphere-climate interactions, and anthropogenic impacts on the water cycle. Addressing these complex, interdependent challenges require a nested SoS approach that integrates heterogeneous assets (satellites, HAPS, in situ, and digital platforms) into coordinated, adaptive architectures—beyond what single-mission planning can achieve.

The methodology applies the Multi-Attribute Tradespace Exploration (M.A.T.E.) approach to trace connections from SQs to Knowledge Advancement Objectives (KAOs), observables, and system requirements. Four candidate architectural scenarios are assessed: Baseline Continuity, Innovation Push, Resilient Decentralised, and Value-Maximising. Each is benchmarked against three value dimensions: scientific observability (e.g., KAOs-per-mission coverage, latency), system design (e.g., modularity, upgradeability), and societal/economic contribution (e.g., policy alignment, ecosystem enablement).

Results show, for example, that Baseline Continuity ensures critical time series for climate services, Innovation Push reduces product latency to under 3 hours, Resilient Decentralised enhances geographic equity and fault tolerance, and Value-Maximising achieves the highest scientific and economic co-benefits by maximizing cross-SQ observability. No single scenario is universally optimal; instead, a hybrid approach that integrates modularity, resilience, and synergy emerges as the most promising pathway. These findings provide ESA with actionable guidance on aligning future EO architectures with scientific priorities and European policy agendas toward 2050+.

Keywords: Earth Observation, System-of-Systems, M.A.T.E., Scenario Analysis, KAOs, Reference Architecture

## Nomenclature

Architecture Configuration: A specific arrangement of EO assets, services, and technologies to address defined science and mission needs.

Knowledge Advancement Objective (KAO): A focused scientific goal within an ESA Science Question aimed at expanding understanding of Earth system processes.

System-of-Systems (SoS): An organized collection of EO systems (satellites, ground stations, data platforms, etc.) that function as a coordinated whole.

Tradespace: A multi-dimensional design space in which EO architectures are evaluated based on utility across several attributes.

Utility Score: A normalized metric (0-1) indicating how well a configuration meets specific evaluation criteria.

Acronyms/Abbreviations

ESA-European Space Agency

EO-Earth Observation

SoS - System-of-Systems

M.A.T.E. - Multi-Attribute Tradespace Exploration

KAO-Knowledge Advancement Objective

SQ-Science Question

ET - Evapotranspiration

SWE-Snow Water Equivalent

SIF - Solar-Induced Fluorescence

SMB-Surface Mass Balance

VAS-Value-Added Services

TR- Technology Readiness

GCOS - Global Climate Observing System

CEOS - Committee on Earth Observation Satellites

<!-- PDF_PAGE: 2 -->

OSCAR - Observing Systems Capability Analysis and Review Tool

## 1. Introduction

The growing complexity and urgency of environmental challenges that need monitoring and addressing demand transformative innovations in Earth Observation (EO) system design. Climate change and extreme events, biodiversity loss, anthropogenic alterations to biogeochemical cycles, and pollution have escalated the requirements placed on EO infrastructures. Beyond traditional observation needs, the EO community is now being asked to deliver high-frequency, multiscale, interoperable, and user-oriented data systems capable of informing not only scientific understanding but also operational services, socio-political decisions, and economic resilience.

In this context, the European Space Agency (ESA) has developed the 2024 EO Science Strategy [1], which identifies 23 over-archingScience Questions (SQs) to guide the future of EO science systems. For the SoS scenario development and benchmarking the focus is put on the following SQs:

1. Ocean carbon cycle responses to anthropogenic CO2.

2. Mass balance of the cryosphere (glaciers, ice sheets, ice shelves).

3. Identification and monitoring of ecosystem critical transitions.

4. Human and climate change impacts land biosphere processes.

5. Anthropogenic influences on the water cycle and their predictability.

These questions represent complex, interdependent phenomena with implications across spatial, temporal, and thematic domains. They necessitate an architectural paradigm shift from mission-based planning to systemof-systems (SoS) orchestration.

"The Circle" project was launched in this strategic framework. Its primary aim is to derive a new, future-proof EO reference architecture that is science-driven, stakeholder-informed, and operationally feasible. It implements a structured methodology to link these guiding science questions to concrete architectural and system design decisions. Rather than designing single missions, The Circle envisions an evolving ecosystem comprising constellations of public and commercial satellites, High Altitude Pseudo-Satellites (HAPS), in situ infrastructure, and advanced digital platforms.

The Circle's structure is divided into key phases. The initial technical assessments are reported in:

- ESA EO Reference Architecture definition: Analyzes the current state as a baseline, including ESA and global assets, and highlights architectural gaps.

- EO Ecosystem identification: Examines EO supply and demand dynamics, actor roles, policy and economic drivers, and system boundaries.

- SoS Evaluation Framework: Establishes a methodology based on Multi-Attribute Tradespace Exploration (M.A.T.E.).

- Scenario Analysis (v1): Develops and benchmarks scenario-based architectures according to science, system, and societal value.

These phases inform a non-prescriptive reference model that enables adaptive planning toward 2030, 2040, and beyond 2050. Moreover, The Circle contributes to ESA's Agenda 2025 and aligns with global initiatives like the UN Ocean Decade, the Group on Earth Observations (GEO), and the Global Climate Observing System (GCOS). It sets the foundation for a new generation of architecture co-design and participatory foresight methods in EO.

## 2. Material and methods

To create a science-aligned EO reference architecture, The Circle project applies a structured methodology that directly links high-level scientific questions to concrete system design choices. Rather than remaining at a conceptual level, this methodology specifies how SQs are decomposed into Knowledge Advancement Objectives (KAOs), observables, and measurable system requirements, and then evaluates alternative architectures against multi-dimensional criteria.

The process is multi-step and traceable, and each step is detailed in the subsections below. In summary, it includes:

1. Decomposition of science needs - translating ESA's SQs into KAOs and associated observables (Section 2.1-2.2).

2. Evaluation framework - defining the dimensions (scientific, system, economic/societal) and metrics used for benchmarking (Section 2.3).

3. Data sources and inputs - identifying datasets, inventories, and stakeholder contributions that inform the analysis (Section 2.4).

4. Stakeholder engagement - incorporating the perspectives of scientific, commercial, and policy actors to weight attributes and validate trade-offs (Section 2.5).

<!-- PDF_PAGE: 3 -->

This explicit breakdown ensures that what follows goes beyond introductory statements and demonstrates how the methodology is implemented in practice.

## 2.1 From Science Questions to System Requirements

The methodology begins with the five selected overarching Science Questions (SQs) defined in ESA's Earth Observation Science Strategy (2024) [1]. Each SQ is further associated with a set of Knowledge Advancement Objectives (KAOs), which articulate the specific scientific goals required to address the broader question. For instance, the cryosphere SQ includes KAOs targeting glacier surface mass balance and ice velocity, while the ocean carbon cycle SQ includes KAOs related to air-sea $ \mathrm{C O_{2}} $ fluxes.

To operationalize these KAOs, The Circle project links them to a set of measurable geophysical observables. These include, for example, Surface Mass Balance (SMB), Snow Water Equivalent (SWE), SolarInduced Fluorescence (SIF), and Evapotranspiration (ET). These observables were selected because they are:

- directly traceable to ESA's KAOs,

- widely recognized in the scientific community as essential indicators of Earth system processes,

- measurable by current or emerging EO technologies, and

- relevant to multiple SQs, ensuring synergies across domains.

Each observable is characterized by quantitative requirements, such as:

- Spatial resolution (e.g., tens of meters for land processes, kilometers for ocean fluxes),

- Temporal revisit frequency (from sub-daily for dynamic phenomena to seasonal for slow processes),

- Radiometric and geometric accuracy, and

- Latency (from acquisition to delivery, ranging from hours to weeks depending on application).

The relationships between SQs, KAOs, and observables are formalized in a KAO-observables matrix (Section 2.2). This matrix ensures full traceability from ESA's strategic science agenda down to the systemlevel requirements used in the architecture assessment

## 2.2 KAOs and Observables Mapping

A matrix structure links each SQ to its relevant KAOs and associated observables. For example:

- Question 1 (Ocean carbon cycle response to anthropogenic $ \mathrm{C O_{2}} $ ） $ \rightarrow $ KAO1.2 (Air-sea $ \mathrm{C O_{2}} $ fluxes and exchange processes) $ \rightarrow $ Observables: Sea Surface Temperature (SST), ocean partial pressure of $ \mathrm{C O_{2}} $ （ $ \mathrm{p C O_{2}} $ ）, and surface wind fields. These variables were selected because they are

the primary controls on air-sea fluxes directly linking climate forcing to ocean carbon uptake and variability.

- Question 2 (Cryosphere mass balance of glaciers, ice sheets, and shelves) $ \rightarrow $ KAO 2.1 (Glacier and ice sheet surface mass balance and dynamics) $ \rightarrow $ Observables: glacier area, glacier elevation change, glacier mass change, ice sheet elevation change, ice sheet velocity, ice sheet mass change, grounding line location, and ice thickness. These observables capture both surface mass balance drivers (accumulation/ablation) and dynamic processes (flow and grounding line migration), ensuring a complete picture of cryosphere contributions to sea-level rise.

- Question 3 (Ecosystem critical transitions) $ \rightarrow $ KAO 3.1 (Ecosystem function dynamics in extent, composition, and productivity) $ \rightarrow $ Observables: Solar-Induced Fluorescence (SIF), Evapotranspiration (ET), and etc, These indicators were chosen because they quantify ecosystem function (photosynthetic efficiency, water use, vegetation productivity) rather than biodiversity per se, providing sensitive early-warning signals of ecosystem instability.

- Question 4 (Land biosphere response to human activity and climate change) $ \rightarrow $ KAO 4.2 (Biosphere-atmosphere carbon and energy exchange) $ \rightarrow $ Observables: Gross Primary Productivity (GPP from SIF), land surface temperature (LST), soil moisture, and evapotranspiration (ET). These observables capture the fluxes and feedbacks linking land processes with the atmosphere, thereby enabling assessment of how land use and climate variability alter carbon sequestration and hydrological cycles.

- Question 5 (Anthropogenic influences on the water cycle and its predictability) $ \rightarrow $ KAO 5.1 (Hydrological fluxes and water storage changes) $ \rightarrow $ Observables: precipitation, soil moisture, river discharge, terrestrial water storage (from gravimetry), and evapotranspiration (ET). These variables were selected because they represent the key fluxes and storages of the water cycle, directly connecting human-driven changes (e.g., irrigation, groundwater depletion) with climate variability and predictability.

This KAOs-observables matrix ensures the traceability and justification of system capabilities because it makes the underlying choices and assumptions explicit.

<!-- PDF_PAGE: 4 -->

By systematically linking each SQ to its associated KAOs and then to specific observables, the matrix:

- Documents rationale $ \rightarrow $ shows why a given observable (e.g., SWE, SIF) is included because it directly supports a defined KAO.

- Avoids arbitrariness $ \rightarrow $ prevents ad hoc selection of observables by requiring each to be traceable to ESA's science strategy.

- Reveals assumptions $ \rightarrow $ highlights where observables were prioritized due to feasibility, maturity of measurement techniques, or multiSQ relevance.

- Supports consistency $ \rightarrow $ ensures that architectural configurations are evaluated against the same science-derived requirements, not shifting criteria.

In this way, the matrix provides a transparent "audit trail" from ESA's science strategy down to the technical requirements assessed in the architecture evaluation.

## 2.3 Evaluation Dimensions

The Circle evaluates candidate architecture using the Multi-Attribute Tradespace Exploration (M.A.T.E.) framework [7]. M.A.T.E. is a decision-support approach based on Multi-Attribute Utility Theory that has been widely applied in space system design (Ross et al., 2004). It provides a structured way to assess complex design options across multiple, often competing, criteria.

In this study, M.A.T.E. is implemented through three main value dimensions, which reflect both ESA's strategic priorities and established practice in system-of-systems analysis:

1. Scientific Observability - measures how well the architecture meets the spatial, temporal, accuracy and thematic requirements of the KAOs.

2. System Design Characteristics - captures engineering performance, adaptability, and lifecycle considerations.

3. Economic and Societal Value - accounts for cost efficiency, ecosystem enablement, sustainability, and policy alignment.

These dimensions were selected because they cover the full value chain from science needs (knowledge generation), through system engineering feasibility, to societal impact. Together, they ensure that architecture is not only technically viable, but also scientifically relevant and policy/economically justified

## 2.4 Data Sources and Inputs

The analysis draws from a wide variety of data sources:

- ESA EO Science Strategy documents and implementation roadmaps. [1]

- CEOS database of satellite missions and sensors. [3]

- OSCAR/WMO inventory of observing systems. [4]

- Commercial operator reports (e.g., Planet, ICEYE, GHGSat).

- Ground segment and data infrastructure statistics.

## 2.5 Stakeholder Engagement

To enhance legitimacy, The Circle engages with academic institutions (e.g., Universität Zürich), commercial entities (D-Orbit), policy organizations (EARSC), and domain experts. Inputs from these groups helped define the attribute weights and assess trade-offs during scenario benchmarking.

## 3. Theory and calculation

## 3.1 Architecture Evaluation Framework

At the heart of The Circle's analysis lies the Multi-Attribute Tradespace Exploration (M.A.T.E.) [7] methodology. M.A.T.E. is a structured decision support framework grounded in Multi-Attribute Utility Theory (MAUT) and system engineering principles. It provides a mechanism to evaluate multiple architectural options across diverse and often competing criteria.

The M.A.T.E. process involves:

1. Defining Evaluation Attributes: Each attribute represents a criterion of value or performance (e.g., revisit time, latency, modularity).

2. Utility Function Construction: Attributes are normalized and mapped to a utility scale (typically 0-1), reflecting stakeholder preferences.

3. Weight Assignment: Each attribute is weighted to indicate its relative importance in the overall evaluation. In The Circle, weights were derived through a combination of expert consultation and stakeholder workshops (Section 2.5). Experts from the scientific, engineering, and policy domains were asked to prioritize attributes according to their relevance to the ESA Science Questions and downstream applications, while stakeholder sessions helped to calibrate these priorities against user needs and policy drivers.

4. Scoring of Architectures: Each candidate configuration is assessed using a weighted utility model, where attributes are not treated as equally important. Weights were derived from expert and stakeholder input (Section 2.5), giving greater influence on critical factors such as latency for emergency response or continuity for climate monitoring. Attributes are grouped under the three M.A.T.E. value dimensions (scientific, system design, economic/societal),

<!-- PDF_PAGE: 5 -->

with composite scores calculated per dimension and then integrated. This layered approach captures cascading effects and highlights tradeoffs both within and across dimensions.

5. Tradespace Analysis: Results are visualized and analyzed using Pareto frontier techniques, multi-objective optimization, and sensitivity assessments.

## 3.2 Scenario Development

The Circle developed four contrasting architecture scenarios to explore alternative strategic postures and evolutions of technology. The scenarios were generated through a structured process that combined:

- Review of ESA strategic roadmaps and mission portfolios, to anchor the scenarios in ongoing programmatic trajectories.

- Expert elicitation within the project team, drawing on scientific, engineering, policy, and economic perspectives (see affiliations of co-authors).

- Stakeholder consultations with ESA, industry partners, and academic experts (Section 2.5), to validate assumptions and ensure relevance; and

- Iterative tradespace analysis, in which preliminary configurations were tested against observability, system, and societal criteria, and then refined into representative scenario "families."

This process ensured that the four scenarios are not arbitrary storylines, but structured explorations of plausible architectural pathways shaped by both science-driven needs and stakeholder priorities. Each scenario contains multiple candidate configurations that embody different design choices within its strategic posture:

- Baseline Continuity: Extends current ESA programs (e.g., Copernicus, Earth Explorers) with minimal innovation. Focus is on continuity, data heritage, and operational reliability. Platform design relies on proven, mature buses and data systems.

- Innovation Push: Emphasizes technological innovation and system agility. Features include AI-based onboard processing, modular sensor architecture, hosted payloads, and crossmission data fusion. Latency is reduced through edge computing and optical intersatellite links.

- Resilient Decentralised: Prioritizes redundancy, fault tolerance, and local autonomy. Includes heterogeneous assets (CubeSats, microsatellites, HAPS), autonomous scheduling, and regional downlink capacity. Designed to withstand extreme weather conditions and geopolitical disruptions.

- Value-Maximising: Seeks to optimize utility per asset, focusing on missions that serve multiple KAOs simultaneously. Rely on

configurable payloads, dynamic tasking, and integration with commercial data providers.

## 3.3 Calculation Model

The utility for each configuration is computed using a weighted sum model, considering either a weight of the attribute (e.g., revisit frequency, latency, modularity) and a normalized utility score of architecture on attribute Each scenario configuration is represented as a point in a multi-dimensional tradespace. Frontier architectures are identified as those that are non-dominated, i.e., no other configuration is better in all evaluated dimensions.

Additionally, The Circle introduces a scoring matrix approach to analyze cross-SQ coverage, providing a scientific synergy metric. For example, a configuration covering 5 KAOs across 3 SQs with fewer assets is scored higher than a similar configuration with narrower coverage.

However, it is important to note that different configurations may emerge as equally interesting even if they do not dominate across all parameters. For instance, one configuration may achieve broad cross-SQ coverage but with higher latency, while another offers rapid response for fewer KAOs. In such cases, both solutions can be considered valuable, depending on stakeholder priorities (e.g., climate monitoring vs. emergency response). This reflects the Pareto frontier principle inherent in M.A.T.E., where multiple nondominated configurations coexist and provide decisionmakers with a spectrum of valid options rather than a single "winner."

## 4. Results

## 4.1 Scientific Observability Performance

Each scenario offers different capabilities in addressing the observables linked to ESA's five SQs:

- Baseline Continuity excels in maintaining long-term series for variables like Land Surface Temperature (LST), SWE, and vegetation indices. This supports trend analysis and continuity-dependent services such as Copernicus Climate Change Services. In the scoring matrix, Baseline achieved the highest continuity score (0.95/1.0) but lower responsiveness (0.45) compared with Innovation Push.

- Innovation Push significantly improves detection and reporting of dynamic phenomena (e.g., forest fires, algal blooms, glacier calving) due to AI-enabled processing and higher temporal resolution.

- Resilient Decentralised demonstrates high geographic equity in coverage, particularly in the cryosphere and tropics, thanks to multiplatform redundancy and independent data relay.

<!-- PDF_PAGE: 6 -->

- Value-Maximising shows superior performance in enabling co-observability. For instance, a hyperspectral imaging spectroscopy mission with a short revisit time and large swath simultaneously informs KAO 1.1 (Ocean productivity), KAO 2.2 (Ice shelf integrity), and KAO 4.3 (Biosphere-atmosphere feedback).

To increase transparency, the qualitative descriptors ("excels," "improves," etc.) are supported by a quantitative observability matrix. Each scenario was scored against the KAOs-observables requirements (Section 2.2) using normalized utility values (0-1). Table 1 summarizes the relative performance.

<table border="1"><tr><td>Scenario</td><td>Continuity</td><td>Responsiveness(latency)</td><td>Cross-SQ Coverage</td><td>Overall Scientific Observability</td></tr><tr><td>Baseline Continuity</td><td>0.95</td><td>0.45</td><td>0.60</td><td>0.67</td></tr><tr><td>Innovation Push</td><td>0.70</td><td>0.90</td><td>0.75</td><td>0.78</td></tr><tr><td>Resilient Decentralal.</td><td>0.80</td><td>0.65</td><td>0.85</td><td>0.77</td></tr><tr><td>Value-Maximising</td><td>0.75</td><td>0.75</td><td>0.95</td><td>0.82</td></tr></table>

<div align="center">

Table 1. Sample relative performance finding

</div>

This matrix makes traceability explicit, showing how qualitative statements in the text are underpinned by quantitative scoring. The values presented here are illustrative and subject to refinement, as the scoring process is still being consolidated through iterative expert review and stakeholder feedback. They are intended to convey initial findings and demonstrate the methodological link between KAOs-observables requirements and scenario performance, rather than serve as final or prescriptive results.

## 4.2 System Design and Engineering Metrics

- Latency: Innovation Push delivers latency under 3 hours for priority products. This is enabled through direct-to-cloud relays, onboard compression, and edge processing. Baseline and Resilient scenarios average 6-24 hours.

- Modularity: Value-Maximising and Innovation Push achieved modularity scores

>0.9 due to use of standard payload interfaces and software-defined sensors.

- Upgradeability: Baseline systems, reliant on traditional procurement, show limited upgradability. In contrast, Resilient systems enable fast insertion of new technologies.

## 4.3 Economic and Policy Insights

- Cost Efficiency: Baseline has the highest cost predictability, while Innovation Push incurs higher upfront R&D investments. However, downstream value (e.g., in climate services and disaster response) is highest for Value-Maximising.

- Ecosystem Enablement: The number of valueadded services (VAS) unlocked by each scenario was used as a proxy. ValueMaximising enables the broadest ecosystem from precision agriculture to Arctic navigation.

- Policy Alignment: Resilient Decentralised aligns best with resilience-oriented policies such as the EU Green Deal and Sendai Framework for Disaster Risk Reduction.

## 5. Discussion

The findings of The Circle illustrate the trade-offs and interdependencies inherent in designing a future science-driven EO reference architecture. These results go beyond binary comparisons and point to the need for hybrid architectural approaches that combine strengths across multiple value dimensions. In practice, this means that certain architectural options are not mutually exclusive but co-occurring and complementary for example, innovation-driven lowlatency services can be paired with resilient, redundancy-rich infrastructures to ensure reliability under stress.

A critical implication is the need to avoid architectural lock-in. Because new Science Questions will emerge and existing ones will evolve with novel dimensions, the reference architecture must remain modular and replaceable, rather than fixed. This includes the ability to:

- Insert new capabilities as technologies mature,

- Retire or swap outdated components without destabilizing the system, and

- Scale capacity up or down depending on immediate needs or future demands.

This adaptability strengthens resilience to disruptions (e.g., climate extremes, geopolitical shocks) while preserving continuity of core measurements. By structuring the architecture around open interfaces and modular payload/platform designs, The Circle framework ensures that hybridization does not lead to rigidity but instead provides a dynamic system-of-

<!-- PDF_PAGE: 7 -->

systems able to evolve alongside scientific, policy, and societal needs.

## 5.1 Strategic Trade-offs

- Innovation vs. Resilience: Innovation Push introduces capabilities such as AI-driven onboard analytics and agile re-tasking, reducing latency and increasing responsiveness. However, its reliance on cutting-edge, lower TRL components poses reliability challenges. Conversely, Resilient Decentralised favors platform redundancy and fault tolerance but lags in agility.

- Cost vs. Synergy: Value-Maximising achieves the highest KAOs-per-mission ratio, optimizing return on investment for individual missions. This comes at the expense of increased system complexity and potential bottlenecks.

- Latency vs. Continuity: While Innovation Push significantly reduces latency, this may disrupt long-term data continuity due to new sensor modalities. Baseline Continuity, while less responsive, ensures critical time series are preserved, a need echoed by climate modellers and service providers.

## 5.2 Architectural Convergence and Divergence

Analysis reveals that certain architectural choices consistently yield high performance across multiple scenarios:

- Modular Payload Buses with standard interfaces (for modularity): Enable future upgradeability and flexible mission design.

- Software-defined Instruments: Increase cross-KAO observability by switching operational modes based on user needs.

- Cloud-native Ground Segment Integration: Ensures scalability, automated data fusion, and reduced distribution latency.

## Divergences arise in areas such as:

- Downlink Strategies: Direct-to-cloud optical relays (Innovation Push) vs. in-region ground stations (Resilient).

- Data Governance Models: Centralized repositories vs. edge-enabled federated data lakes.

- User Access Models: Open access APIs (Baseline) vs. tiered user segmentation (Value-Maximising).

## 5.3 Stakeholder Implications

The Circle scenarios cater to different actor priorities:

- Scientific Community: Seeks continuity, cross-sensor calibration, and access to raw observables.

- Policy Makers: Emphasize coverage, latency, and reliability for decision support.

- Private Sector: Prioritizes downstream service enablement and cost transparency.

- Civil Society and NGOs: Value inclusivity, regional equity, and public access.

Therefore, no scenario fully satisfies all stakeholder groups. The design challenge lies in co-creating hybrid systems that incorporate scenario-specific strengths while mitigating weaknesses.

## 5.4 Toward a Dynamic Reference Architecture

Rather than prescribing a fixed system blueprint, The Circle advocates for an adaptive, modular reference framework. This framework should:

- Define core capability tiers (Essential, Strategic, Optional)

- Support progressive innovations via open interfaces

- Facilitate co-funding and cross-sector engagement

A dynamic architecture allows ESA and partners to iterate design choices based on technological maturation, evolving user needs, and emerging crises (e.g., pandemics, conflicts, abrupt climate events).

## 6. Conclusions

The Circle project establishes a robust, transparent, and stakeholder-inclusive framework for designing future EO architectures. Its system-of-systems approach aligns scientific priorities with technological feasibility and societal value.

## 6.1 Key Findings:

- A direct and traceable link between ESA's Science Questions, KAOs, observables, and architectural design ensures scientific relevance.

- The M.A.T.E. methodology effectively evaluates candidate architecture across multiple dimensions, revealing trade-offs and synergies.

- Each scenario offers valuable contributions, but no single approach is universally optimal.

## 6.2 Strategic Recommendations:

- Adopt a Hybrid Strategy: Combine modularity (Innovation Push), resilience (Resilient), and synergy (Value-Maximising).

- Promote Open and Standardized Interfaces: Ensure payloads, platforms, and ground systems are interoperable across public and commercial actors.

- Embrace Digital Twins: Integrate EO architectures with modeling frameworks for real-time feedback and optimization.

<!-- PDF_PAGE: 8 -->

- Establish Participatory Governance: Involve science,policy,industry,and civil society actors in ongoing co-design.

## 6.3 Future Work:

Subsequent phases will:

- Incorporate feedback from stakeholder workshops.

- Extend the scenario portfolio with alternative geopolitical and economic assumptions.

- Perform sensitivity and uncertainty analysis on architectural attributes.

- Define pathways for implementation, including regulatory, industrial, and financing models.

Ultimately, The Circle supports ESA's mission to lead the global EO community in advancing science, informing policy, and delivering societal benefit through a future-ready, integrated system architecture.

## Acknowledgements

The authors gratefully acknowledge the support of the European Space Agency (ESA) for the funding (

ESA Contract No. 4000145640/24/NL/SC) and strategic guidance provided throughout The Circle project. Special thanks go to all the contributors from Planetek Italia, University of Zürich, D-Orbit, EARSC, and SDA Bocconi who provided their expertise across scientific, technical, policy, and economic domains. We also thank the domain experts and stakeholders who engaged in review sessions, ensuring the robustness and

applicability of our reference architecture framework. Their insights and participation were instrumental in aligning this work with the broader goals of the EO community.

## References

[1] ESA Earth Observation Science Strategy, 2024. Available at:

https://esamultimedia.esa.int/docs/EarthObservation/ES A_Earth_Observation_Science_Strategy_issued_Sept_2 024.pdf

[2] European Space Agency, "EO Gateway Missions," Accessed 2025. https://earth.esa.int/eogateway/missions.

[3] CEOS, "Database of Earth Observation Satellites and Sensors," Accessed 2025. https://database.eohandbook.com/

[4] OSCAR (Observing Systems Capability Analysis and Review Tool), World Meteorological Organization (WMO). https://space.oscar.wmo.int

[5] Group on Earth Observations (GEO). https://earthobservations.org

[6] GCOS Implementation Plan 2022, World Meteorological Organization. https://gcos.wmo.int/en/gcos-implementation-plan

[7] Ross, A.M., Hastings, D.E., Warmkessel, J.M., and Diller, N.P., "Multi-Attribute Tradespace Exploration as a Front-End for Effective Space System Design," Journal of Spacecraft and Rockets, Vol. 41, No. 1, pp. 20-28, Jan/Feb 2004. doi: 10.2514/1.9204