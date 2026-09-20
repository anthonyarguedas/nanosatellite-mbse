---
source: "SLR/SLR1/pdfs/handpicked-reports/handpicked-report-0001/handpicked-report-0001.pdf"
title: "handpicked-report-0001"
page_count: 10
converted_at: "2026-09-20T22:23:14Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# Towards Intelligent Systems for Battery Management: A Five-Tier Digital Twin Architecture

</div>

Tianwen Zhu, Hao Wang, Zhiwei Cao, Nanyang Technological University, Singapore, 639798

Simon See, NVIDIA AI Tech Centre, Singapore, 199589

Yonggang Wen, Nanyang Technological University, Singapore, 639798

Abstract—As digital twin technologies are increasingly incorporated into battery management systems to meet the growing need for transparent and lifecycle-aware operation, existing battery digital twins still suffer from fragmented operational processes and lack an architectural perspective to coordinate modeling, inference, and decision-making throughout the battery lifecycle. To this end, we develop a unified five-tier battery digital twin framework that integrates key functionalities into a coherent pipeline and facilitates a clearer architectural understanding of digital twins. The five-tier comprises geometric modeling, descriptive analytics, physics-informed prediction, prescriptive optimization, and autonomous control. In quantitative evaluation, the resulting architecture achieves high-fidelity multi-physics calibration with 0.92% voltage and 0.18% temperature prediction error, and provides state-of-health estimation with 1.09% MAPE and calibrated uncertainty. As the first battery digital twin system empowered by the NVIDIA ecosystem with physics-AI technologies, our proposed five-tier framework shifts battery management from reactive protection to an interpretable, predictive, and autonomous paradigm, paving the path to develop next-generation battery management and energy management systems.

Battery Management Systems (BMSs) serve a critical function in ensuring the safety and performance of electric vehicles and energy storage systems. With the increasing scale of battery pack integration and the growing complexity of operating conditions, BMSs should not only ensure basic safety protection but also progressively expand their capabilities to meet the pressing demand for higherlevel intelligent management. The indispensable role of BMSs is driven by the rapid expansion of energy storage applications, expected to reach around 442 GWh globally by 2030 [1]. This accelerating deployment is increasing not only capacity demands but also introducing system complexity. For instance, EV battery packs contain thousands of cells operating under fluctuating loads, while grid-scale systems integrate heterogeneous batteries with diverse degradation patterns [2]. These complexities demand BMSs capable of coordinating cell behavior and maintaining resilience under varying demand and supply conditions.

In practice, conventional BMSs remain limited in their sensing and prediction capabilities, primarily due to their reliance on a narrow range of sensor-accessible parameters. First, perception is limited because typical BMS architectures based on embedded PLCs and ECUs can process only a narrow set of measurable signals [3], providing limited visibility into latent states like State of Charge (SOC), or State of Health (SOH) [4]. This hardware limitation leads most existing BMSs to adopt rule-based designs with threshold-triggered protective actions for short-term safety. Second, predictive capability is limited because present BMSs mainly rely on simplified physics models that capture only short-term electrical responses while neglecting electrochemical degradation mechanisms. Consequently, they cannot simulate state trajectories under varying load and thermal conditions, making long-term health evolution prediction unattainable.

To overcome these limitations, researchers have introduced the concept of digital twins into BMSs, integrating multi-source data, multi-physics modeling, and advanced AI methods to establish a dynamic mapping between the physical and virtual domains. A digital twin is a synchronized digital replica of the physical system that combines the asset itself, a highfidelity virtual model, and bi-directional data flows to maintain alignment [5]. In the battery domain, digital twins typically leverage physics-based electrochemical

<!-- PDF_PAGE: 2 -->

models and multi-node thermal models to capture spatiotemporal distributions of temperature and lithium concentration. Because such high-fidelity simulations are computationally intensive, they are often executed on cloud or high-performance computing platforms, with the results synchronized back to the edge BMS for real-time decision support [6]. As a result, current solutions tend to cover one or a few functional layers in isolation separately.

Despite recent progress, the fundamental gap in current battery digital twin frameworks is the absence of a unified, multi-tier architecture that organizes fragmented capabilities and workflows into a coherent whole. Building on this overarching architectural void, three specific gaps emerge. First, lacking synergy between data-driven models and physics-based models makes it difficult to simultaneously achieve high predictive accuracy and physical interpretability. In practice, many battery digital twin implementations rely on black-box data-driven approaches that capture correlations but ignore physical laws, while physics-based electrochemical or thermal models offer mechanistic insight but remain computationally intensive and struggle to represent degradation behaviors under practical cycling conditions. Second, most existing battery digital twins lack self-evolving capability. They still depend heavily on offline analysis, which prevents timely updates of the virtual model. As a result, the digital twin cannot continuously adapt to real-time operating data, leading to gradual divergence from the physical battery under dynamic conditions. Third, current systems lack decision validation capabilities. Although many digital twins can generate accurate predictions of battery behavior, they seldom verify how these predictions translate into effective operational decisions. Thus, the digital twin cannot ensure that its recommendations, such as charging or scheduling strategies, consistently improve real-world performance.

To bridge these gaps, we propose a highly intelligent five-tier battery digital twin architecture empowered by the NVIDIA ecosystem, systematically organizing the full spectrum of digital twin capabilities. This battery digital twin integrates real-time data assimilation at the descriptive tier, multi-physics simulation for accurate forecasting at the predictive tier, optimization algorithms for prescriptive control, and autonomous closed-loop operation at the highest tier, forming a continuous pipeline from monitoring to intelligent actuation. Electrochemical and thermal dynamics are captured in physics-based simulators and synchronized within NVIDIA Omniverse, with NVIDIA SimReady assets streamlining standardized model construction, while NVIDIA PhysicsNeMo provides the physics-informed

learning engine that accelerates simulation and forecasting. Unlike conventional designs that separate monitoring, forecasting, and control into isolated modules, our digital twin establishes an evolving digital intelligence across the entire battery lifecycle, enabling continuous synchronization and self-evolution between the physical and virtual systems, thereby delivering enhanced safety and reliability for next-generation EVs and energy storage applications.

The contributions of our approach are as follows.

- To the best of our knowledge, this is the first article that systematically proposes and introduces a unified five-tier digital twin system for intelligent battery management. Each tier is clearly defined to address the gaps in existing BMS approaches.

- The system uniquely employs calibrated multiphysics modeling with PIML to achieve interpretable tracking of internal battery states and latent variables, which directly enhances the physical interpretability of battery management and supports proactive decision-making.

- We present the first battery digital twin system implemented within the NVIDIA ecosystem, leveraging Omniverse, SimReady assets, and PhysicsNeMo for end-to-end geometric modeling, multi-physics simulation, and physics-informed learning. Our implementation delivers high simulation fidelity, achieving low voltage and temperature prediction error, and produces robust SOH estimates with quantified uncertainty.

## Preliminaries

In this section, we first review the common BMS architectures. We then introduce multi-physics modeling approaches for electrochemical, thermal, and degradation processes. Finally, we summarize key simulation platforms and validation methods that bridge virtual models with real-world operation.

## Overview of BMS

BMSs are designed to monitor and protect batteries. In practice, a BMS integrates subsystems for signal acquisition, central control, circuit protection, and communication with upper-level energy management systems [7]. Despite these capabilities, conventional implementations remain limited in intelligence, as they rely heavily on rule-based logic where protective actions such as disconnection, cooling, or cell balancing are triggered only after predefined safety thresholds are exceeded [8]. While such designs mitigate immediate risks, they remain inherently reactive and

<!-- PDF_PAGE: 3 -->

inefficient, motivating the need for more advanced and predictive BMS solutions.

## Battery Multi-physics Modeling Techniques

Battery physics modeling sets up the foundation for estimating and predicting battery dynamic behavior based on electrochemical, chemical and mechanical principles. At the electrochemical level, broadly used models include the Single Particle Model (SPM) and the Doyle-Fuller-Newman (DFN) model [9]. The SPM simplifies battery dynamics by considering single representative particles, offering computational efficiency, while the DFN model provides detailed insights by simulating complex lithium-ion transport and electrochemical reactions across battery electrodes.

Thermal modeling is a key component that characterizes heat generation, transfer, and dissipation during battery operation, typically formulated from energy conservation laws. Lumped thermal models [10] are widely adopted due to their simplicity and computational efficiency in estimating temperature dynamics, thereby supporting effective thermal management strategies essential for safety and reliability. Battery degradation modeling, on the other hand, focuses on long-term aging driven by mechanisms such as solid electrolyte interphase growth, lithium plating, and particle cracking. Advanced modeling methods, such as those introduced by Wang et al. [11], explicitly couple these processes to capture the complex interactions that govern performance decay and material loss. These integrated multi-physics modeling plays an important role in accurately predicting battery lifetime and performance, emphasizing the importance and challenge of incorporating comprehensive multi-physics models within digital twin architectures. It is worth mentioning that both the thermal models and degradation models can be coupled within the multi-physics model by introducing new source functions.

## Simulation Platforms and Validation Methods

High-fidelity simulation platforms are a trustworthy way to validate battery digital twins, ensuring accurate representation of electrochemical, thermal, and mechanical behaviors under diverse conditions. Besides well-known tools like PyBaMM and COMSOL, other notable platforms include ANSYS Fluent for computational fluid dynamics and thermal analysis, and MATLAB/Simulink for dynamic system modeling and control strategy simulations. These platforms support analyzing and simulating battery operation, facilitating comprehensive virtual testing without the necessity for costly physical prototype validations.

Hardware-in-the-Loop (HIL) and Software-in-the-Loop (SIL) are two main complementary simulation paradigms that establish a bridge between virtual models and real-world systems [12]. In SIL, controller algorithms and software modules are embedded within a virtual simulation environment, allowing rapid prototyping, algorithm debugging, and iterative design without the need for physical hardware. Moreover, HIL extends this principle by incorporating real physical components into the simulation loop, thereby exposing algorithms to realistic operating conditions and hardware constraints. By combining these two approaches, digital twins benefit from a continuous validation pipeline that spans from early-stage software verification to hardware-level performance testing, laying the foundation for reliable predictive maintenance and operational optimization of batteries.

## System Design of the Digital Twin

In this section, we present the intelligent five-tier digital twin system for battery management. First, we introduce the overall system architecture. Then, we articulate several potential applications of this digital twin in predictive and prescriptive battery analysis.

## Architecture Overview

The architecture of our intelligent five-tier digital twin system is shown in Figure 1. Each layer is constructed upon the foundation of the previous one within a unified intelligent system. From bottom to top, Tier 1 (Geometric) builds 3D representations of battery cells, modules, and packs, implemented in NVIDIA Omniverse as the spatial backbone, supported by NVIDIA SimReady assets that provide standardized, simulationready battery components; Tier 2 (Descriptive) binds real-time sensor streams to this geometry to create a live, data-rich twin that visualizes temperature distributions, voltage/current profiles, and operating conditions; Tier 3 (Predictive) leverages PIML to forecast capacity-degradation trajectories, estimate SOH and RUL, and quantify thermal-runaway risk under diverse scenarios; Tier 4 (Prescriptive) translates these forecasts into optimal operating strategies, such as fast-charging protocols, cell-balancing schedules, and cooling-system set-points, while enforcing safety and operational constraints; and Tier 5 (Autonomous) enables the system to achieve closed-loop, AI-driven control, where decisions are executed independently and models adapt through continual learning. NVIDIA Omniverse underpins Tier 1 and Tier 2 as the shared spatial and data plane, augmented by NVIDIA SimReady

<!-- PDF_PAGE: 4 -->


![figure_001.png](handpicked-report-0001_images/figure_001.png)



<div align="center">

FIGURE 1. Overview of the proposed five-tier digital twin intelligence system, integrating geometric modeling, descriptive analytics, predictive forecasting, prescriptive optimization, and autonomous control for intelligent battery management.

</div>

standardized battery assets, while PhysicsNeMo powers Tier 3 to Tier 5 for learning, prescription, and autonomy.

This intelligent system is enabled by three core modules spanning across tiers, with the overall organization illustrated in Figure 3: (i) a virtual 3D environment powered by NVIDIA Omniverse and NVIDIA SimReady for geometric modeling and visualization, (ii) a multi-physics simulation engine for high-fidelity battery state estimation and prediction, and (iii) an AI engine leveraging NVIDIA PhysicsNeMo with PIML to tighten synchronization between the physical battery and its digital replica.

Virtual 3D Environment Module The virtual 3D environment underpins Tier 1 (Geometric) and Tier 2 (Descriptive) with NVIDIA Omniverse serving as the foundational platform for constructing high-fidelity virtual replicas of battery systems. As illustrated in Figure 3, this module forms the core of the Visualization Layer, where USD files enable standardized geometric

modeling spanning from cell components to complete battery system assemblies with many packs. Within this system, this module is designed based on a USD-based 3D scene environment, which is completely programmable using a Python script to add or remove 3D objects and determine their spatial location. In our settings, the scene graph captures the full battery hierarchy from cell to module to pack to represent a 20 kWh-level lithium-ion battery energy storage system. To accelerate and standardize the construction of such virtual battery assemblies, we leverage NVIDIA SimReady assets, which provide preconfigured, simulation-ready models of cells, modules, and packs that integrate natively with the USD-based Omniverse environment.

On top of this geometric structure of an energy storage system, the module adds a semantic schema that assigns meaning to each element. While the scene graph defines how cells, modules, and packs of the batteries are arranged in space, the semantic schema describes what each object represents and how it should be interpreted. For instance, a node can be marked as a temperature sensor, linked to the quantity it measures, and associated with a unit such as degrees Celsius. In this way, the schema ensures that the 3D scene is not just a geometric model but also a machine-readable map of physical roles and properties. To ensure that these semantic descriptions are usable across different scenarios in the digital twin, the module also fixes global coordinate frames, standardizes unit systems, records sensor locations, and assigns unique identifiers. These definitions make it possible to map live telemetry onto the 3D geometry without ambiguity and to exchange data consistently among different simulation and control tools.

In addition, the 3D environment module defines live data mappings that connect telemetry streams and simulation outputs to the corresponding geometric entities. These mappings specify how data is transmitted and processed, including communication topics, update rates, and data types, while providing standardized input-output interfaces to connect with other tiers. The module also exposes read/write APIs for Tier 3 predictive services to present measured, estimated, and predicted results such as SOH and RUL in the 3D scene, while for Tier 4 controllers to visualize recommended setpoints. Figure 2 illustrates this integration within the Omniverse digital twin interface. This figure presents a 3D battery pack model augmented with live sensor dashboards and overlays of predicted SOH, RUL, and temperature variations results. Through this design, the shared 3D scene serves as the central hub where all information about the operational condition,

<!-- PDF_PAGE: 5 -->


![figure_002.png](handpicked-report-0001_images/figure_002.png)



<div align="center">

FIGURE 2. Battery digital twin visualization in NVIDIA Omniverse, showing pack-level monitoring with predictive analytics. The system integrates real-time health indicators with SOH, RUL, and temperature prediction modules to support proactive safety and maintenance decisions.

</div>

real-time system information, and optimized control commands are integrated, ensuring consistency and coordination inside the battery digital twin.

Multi-physics Simulation Engine The multi-physics simulation engine underpins Tier 3 (Predictive) by enabling high-fidelity forecasting of battery dynamics through coupled electrochemical, thermal, and mechanical modeling. As shown in Figure 3, this module constitutes the core of the Model Layer and Simulation Engine, which serve as the analytical backbone of the overall system. Simulation outputs are streamed to Omniverse for live visualization and are used as supervised and physics constrained signals for model training and inference in PhysicsNeMo.

The simulation engine integrates these physics domains into a unified, co-evolving environment, ensuring that the digital twin reproduces battery behavior in a physically consistent manner. For example, electrochemical reactions and ohmic resistance heat are identified as different heat generation sources that result in thermal dynamic variations. The rising temperature inside the cell then impacts the reaction kinetics and transport processes as described by the

Arrhenius equation [13], reshaping voltage responses and accentuating spatial non-uniformities across cells. By resolving these cause-and-effect loops, the multi-physics simulation engine can capture critical battery behaviors such as hot-spot formation, heat spread, and performance shifts under varying loads.

This multi-physics simulation engine not only aligns with experimentally observed behaviours of actual battery systems but also produces high-quality synthetic datasets for the battery digital twin. It also conducts calibrated simulation campaigns in which operating profiles, ambient conditions, thermal management strategies, and aging states are systematically synchronised, generating multi-domain information in time series such as voltage, current, temperature fields, concentration distributions, and derived health indicators. Due to these outputs being computed in a coupled physics model, they are physically interpretable and can be used to deduce other critical latent states that are hard to observe using sensors. This enriches the battery health-related information, making it particularly valuable for supervised learning and benchmarking. Furthermore, the data reliability of this simulation engine is ensured through real-time calibration against experimental measurements to make the simulation responses match well with the observed responses. Additionally, physical consistency checks based on universal physical principles, such as energy conservation laws, are utilised to further reduce the mismatch between the digital twin battery and the physical battery.

The augmentation datasets generated from the multi-physics simulation engine support the formation and enhance the performance of digital twin by (i) providing training supplementary datasets for downstream PIML tasks, (ii) forming operational scenario libraries that reveal trade-offs among various factors, such as charging rate, round-trip efficiency, and thermal effect and (iii) verification of control policies under rare or hazardous conditions before safe transfer to HIL testbeds. By combining these techniques, the simulation engine elevates the twin from a passive mirror of sensor streams into an active experimental platform for intelligent battery management, monitoring and prognostics.

AI Engine Module The AI engine supports Tier 4 (Prescriptive) and Tier 5 (Autonomous) by providing intelligent optimization and adaptive control capabilities for the battery digital twin. As illustrated in Figure 3, it represents the intelligence core of the overall system within the Machine Learning Platform, where advanced AI methods complement physics-based modeling. In our digital twin system design, NVIDIA PhysicsNeMo

<!-- PDF_PAGE: 6 -->

serves as the foundation of the AI engine, enabling the battery digital twin to deliver real-time intelligent estimation, prediction and management while preserving physical consistency and interpretability. PhysicsNeMo follows a PIML paradigm that incorporates governing principles such as charge conservation, electrochemical kinetics, and thermodynamic constraints are embedded directly into neural architectures and training objectives, ensuring both estimations and predictions remain physically plausible and trustworthy rather than purely data-driven. PhysicsNeMo implements neural PDE solvers to accelerate electrochemical and thermal dynamics by several orders of magnitude compared to classical finite-element methods. Meanwhile, transformer-based or other sequence-learning models capture long-term dependencies that characterize degradation trajectories. Together, these methods provide robust forecasts of voltage response, temperature evolution, SOH, RUL, and associated uncertainty at battery cell, module, and pack levels.

Building on its predictive accuracy, the AI engine also supports prescriptive analytics by turning predictions into concrete operating strategies. For example, reinforcement learning with experience replay utilizes past driving or charging information to gradually improve the charging strategy, and thermal management is scheduled as batteries age. Transfer learning accelerates the roll-out of new systems by reusing models trained on similar fleets, reducing the necessity of model retraining. In addition, AI-driven multiobjective optimization methods are applied to generate clear trade-off curves that show, for example, how increasing the charging rate may reduce efficiency or raise cell temperature. This information gives operators and upper-level controllers practical choices, facilitating them to select strategies that well-fit their performance and safety requirements under varying conditions.

From a system-level perspective, the AI engine drives autonomous operation by turning forecasts and optimizations into direct control actions. It utilized continual learning to adapt operational policies as usage conditions vary, and employs fault-tolerant mechanisms that keep the system functional when components fail. Before new decisions are enacted, the engine runs fast predictive simulations to conduct risk detections such as thermal runaway or internal shortcircuit. To validate these learned policies work effectively on real battery systems, the AI engine is coupled with HIL platforms (e.g., OPAL-RT), which execute virtual commands against real controllers and components. In this way, optimized policies are validated under realistic constraints before deployment, ensuring that the digital twin can operate as a self-governing

battery manager across its lifecycle.

## Practical Applications of The Proposed Intelligent System

The capabilities of our intelligent digital twin system enable transformative applications across battery management, through two primary domains that collectively address intelligent battery operations.

Predictive Battery Health Management The most immediate value of the proposed battery digital twin lies in its ability to transform health prediction into a continuous and adaptive process. Instead of relying on sparse snapshots, SOH and RUL are evaluated in real time, adapting to variations in usage and environment. This approach improves predictive accuracy and produces risk-aware outputs expressed as probability distributions rather than deterministic forecasts, enabling operators to plan maintenance proactively with quantified confidence [14]. Such predictive intelligence ensures that maintenance actions are both timely and cost-effective, reducing unexpected downtime and improving overall system reliability.

Beyond prediction, the digital twin enables early detection of degradation far in advance of conventional monitoring tools. By identifying subtle indicators of failure, such as cell imbalance or incipient thermal runaway, it allows operators to isolate or rebalance systems before issues escalate. This capability supports practical applications across fleets and grid storage by preventing propagation of failures and guiding warranty or replacement decisions based on emerging degradation patterns. By distinguishing short-term performance drift from irreversible damage, the system ensures that minor fluctuations are managed efficiently while critical risks are addressed without delay, strengthening both safety and operational resilience.

Battery Repurposing and Value Maximization Beyond health prediction, the digital twin enables actionable strategies to maximize battery value across its entire lifecycle. During operation, forecasts are translated into adaptive charging protocols that shorten charging duration while keeping temperature rise and energy loss within safe limits, and intelligent thermal management that dynamically adjusts airflow and coolant flow according to predicted heat loads. These strategies not only improve energy efficiency but also mitigate thermal stress that accelerates degradation. At the system level, the twin orchestrates load distribution across modules with different health states. Instead of uniform current sharing, it redistributes demand away from

<!-- PDF_PAGE: 7 -->


![figure_003.png](handpicked-report-0001_images/figure_003.png)



<div align="center">

FIGURE 3. Technical architecture of the five-tier intelligent digital twin system for battery management. The comprehensive technical architecture includes multi-physics modeling tools, advanced simulation platforms, and physics-informed AI methodologies such as PhysicsNeMo. The layered structure enables systematic data integration, accurate predictive simulations, and effective prescriptive strategies, thus supporting proactive battery health management throughout its lifecycle.

</div>

overstressed or degraded packs, thereby protecting weaker components while extracting maximum capacity from healthier ones. This capability is particularly valuable in grid-scale storage plants integrating batteries of mixed chemistries and vintages, where conventional rule-based control often leads to underutilization of robust modules and premature aging of already stressed ones [15]. Finally, by preserving complete degradation histories, the digital twin provides accurate assessments of residual capacity at end-of-life. This enables reliable decisions for second-life deployment in stationary storage or recycling, ensuring safe, efficient, and sustainable reuse while maximizing residual value.

## System Implementation and Evaluation

In this section, we implement the proposed five-tier intelligent digital twin system based on NVIDIA ecosystem, focusing on model calibration and health prediction for practical battery management.

## Problem Settings

XJTU battery dataset [16] is used to demonstrate practical battery management. The dataset comprises experiments on 55 lithium-ion batteries $ \mathrm{(L i N i_{0. 5} C o_{0. 2} M n_{0. 3} O_{2}} $ each with a nominal capacity of 2000 mAh and a nominal voltage of 3.6 V. The experiments cover six charge and discharge regimes that emulate realistic operating conditions, including constant C rates, variable-rate profiles, randomized usage, and a satellite-use pattern.

The problem setting is to implement two key functions of the proposed system. The first task is to calibrate a coupled electrochemical-thermal model that can accurately simulate voltage and temperature dynamics under diverse cycling conditions. The second task is to develop predictive models for battery SOH estimation with quantified uncertainty, enabling risk-informed decision support for lifecycle management.

## Realization of the Five-Tier System

We instantiate these tasks by mapping them to Tier 1-5 of the proposed system. Figure 2 illustrates how

<!-- PDF_PAGE: 8 -->

Tiers 1 and 2 are realized in the Omniverse-based 3D environment, where geometric models are bound with telemetry and simulation data to visualize battery states and predictions. We additionally leverage NVIDIA SimReady assets to accelerate the construction of standardized, simulation-ready battery components for Tiers 1 and 2, ensuring consistent geometric and physical representations within the Omniverse environment. Building on this foundation, Tier 3 is enabled through multi-physics modeling and calibration, while Tiers 4 and 5 leverage AI engines to provide predictive and prescriptive intelligence with uncertainty quantification.

Tier 3: Multi-physics Modeling and Calibration We integrate the SPM and DFN electrochemical models with a lumped thermal model using PyBaMM as the modeling platform [17]. The SPM offers computationally efficient simulations suitable for rapid, real-time predictions, while the DFN model provides detailed representation of lithium-ion transport processes and reaction kinetics. A lumped thermal model is coupled with the DFN to accurately capture thermal dynamics under diverse operating conditions.

To ensure fidelity with respect to experimental battery performance, we apply Bayesian optimization for parameter calibration. This procedure adjusts over 15 model parameters (e.g., diffusivities, reaction rates, conductivities, electrode geometries, thermal conductivities) by minimizing discrepancies between simulated and measured voltage and temperature. Through iterative refinement, the calibrated models achieve strong consistency with experimental observations, forming the predictive backbone of the digital twin.

Tier 4: Physics-informed Neural Network Leveraging NVIDIA PhysicsNeMo, we construct PINNs trained on data generated from the calibrated multi-physics simulations. The loss function integrates both data-driven accuracy terms and physics-based constraints, penalizing violations of electrochemical principles and thermal equilibrium. By enforcing these constraints via automatic differentiation at strategically selected points, the PINN captures complex battery dynamics while maintaining physical consistency. This enables Tier 4 prescriptive functions by providing physically trustworthy predictions for SOH and RUL.

Tier 5: Uncertainty Aware Decision-Making To support automatically decision-making in Tier 5, we incorporate Deep Autoencoding Gaussian Mixture Model (DAGMM) for uncertainty quantification. DAGMM combines an autoencoder with a Gaussian Mixture Model


![figure_004.png](handpicked-report-0001_images/figure_004.png)



<div align="center">

(a) Voltage prediction under 1C, 2C, and 3C discharge rates.

</div>


![figure_005.png](handpicked-report-0001_images/figure_005.png)



<div align="center">

(b) Temperature prediction under 1C, 2C, and 3C discharge rates.

</div>

<div align="center">

FIGURE 4. Multi-physics calibration results against the XJTU battery dataset after Bayesian optimization.

</div>

(GMM) to evaluate the likelihood of latent representations of operational data. The resulting energy-based score provides a principled uncertainty metric, identifying anomalies and quantifying confidence in predictions. By capturing uncertainty alongside predictions, this implementation equips the digital twin with the ability to support risk-informed management decisions.

## Evaluation Results

Rigorous evaluations are given to demonstrate the superior predictive accuracy and reliability of the proposed digital twin system through multi-physics model calibration and uncertainty quantifications.

For the multi-physics calibration, our model demonstrated good estimation accuracy compared with the XJTU battery dataset as shown in Figure 4. Across ten repeated trials, the calibrated model achieved an average voltage prediction MAPE of 0.92 $ \pm $0.15% (1C), 1.06 $ \pm $0.17% (2C), and 1.57 $ \pm $0.21% (3C). For temperature prediction, the MAPE reached 0.07 $ \pm $0.01% (1C), 0.18 $ \pm $0.01% (2C), and 0.39 $ \pm $0.05% (3C). These results validate the effectiveness of the multi-physics model in accurately reproducing voltage and temperature behaviors of batteries.

Building upon the calibrated simulations, we can further assess the predictive performance of our PINNbased SOH prediction model, including its capability to quantify prediction uncertainty. As shown in Figure 5, our model demonstrated robust predictive accuracy in SOH, across ten runs achieving MAPE at 1.09 $ \pm 0.04\% $ Most importantly, the integrated uncertainty quantification via the DAGMM provided reliable indications of prediction confidence. As shown in Figure 6, the energy-based uncertainty scores exhibited a strong positive correlation with the actual prediction errors, effectively highlighting scenarios where predictions were less reliable due to data distribution shifts.

<!-- PDF_PAGE: 9 -->


![figure_006.png](handpicked-report-0001_images/figure_006.png)



<div align="center">

FIGURE 5. Prediction results across six charging protocol datasets. Each panel plots battery SOH versus cycle index for a distinct dataset (2C, 3C, R2.5, R3, RW, Satellite). The red curve shows the true SOH labels and the blue curve shows predictions from our model. Panels share comparable axis limits to enable fair visual comparison across datasets. The results indicate that predictions closely follow the true trajectories under both constant rate and randomized profiles.

</div>


![figure_007.png](handpicked-report-0001_images/figure_007.png)



<div align="center">

FIGURE 6. Impact of noise injection on prediction error and the proxy metric for uncertainty.

</div>

## Future Directions

In this section, we discuss several future directions that can be explored to further enhance the intelligent battery management using this digital twin architecture.

Foundation Models for Battery Intelligence: Large Language Models (LLMs) are foundation models trained on massive text corpora using transformer architectures, enabling diverse tasks such as reasoning, summarization, and question answering without task-specific supervision. Beyond language, they serve as general-purpose engines for knowledge representation and code generation across scientific domains. Building on these capabilities, LLMs adapted on battery-related literature present promising opportunities for digital twins through automated knowledge extraction and model generation [18]. Future implementations envision specialized battery foundation models that automatically design PINN architectures for specific chemistries, synthesize insights from vast research to identify degradation mechanisms, recommend experimental protocols, and support conversational interfaces for intuitive querying of battery states and explanations of complex degradation phenomena.

Blockchain-based Battery Passport Systems: The implementation of blockchain in battery lifecycle management offers transformative potential for future battery passport systems, enabling complete traceability and transparency. Distributed ledger technologies will record manufacturing data, operational history, maintenance, and performance metrics as immutable entries, ensuring reliable information sharing across manufacturers, operators, and recyclers [19]. Smart contracts could automate management decisions such as maintenance scheduling and end-of-life processing, reducing fraud in condition reporting. Blockchainbased passports will further support circular economy initiatives by providing verified health data for secondlife applications, allowing batteries retired from vehicles to be reused in stationary storage with confidence.

Differentiable Simulation for Optimal Control: The development of fully differentiable battery simulation frameworks enables gradient-based optimization of battery operational strategies directly through physics-based models, eliminating the need for computationally expensive reinforcement learning approaches. Future implementations could leverage automatic differentiation through simulation platforms to enable direct optimization of charging protocols, thermal management strategies, and load balancing decisions with respect to battery health and performance objectives. This approach provides enhanced transparency compared to black-box optimization methods while enabling principled handling of operational constraints through physics-based penalty terms in the optimization objective.

<!-- PDF_PAGE: 10 -->

## Conclusion

To promote the transition of BMS towards intelligent systems for achieving full-lifecycle efficient management across diverse energy storage applications, we presented an intelligent battery management concept based on a five-tier digital twin system for autonomous operations. We first highlighted current BMS challenges and the need for advanced digital twin approaches. Then, we introduced the system design, progressing from geometric modeling to autonomous operation, supported by PIML and uncertainty quantification. Its applications span predictive health management, operational optimization, and lifecycle control. Finally, a system implementation validated our design, showing sub-1% voltage/temperature errors and robust SOH predictions with MAPE below 3%, demonstrating the system's potential for interpretable modeling and reliable decision-making.

## REFERENCES

1. BloombergNEF, "Global energy storage market records biggest jump yet," https://about.bnef.com/insights/clean-energy/global- energy-storage-market-records-biggest-jump-yet/, 2023, accessed: 2025-08-28.

2. X. Cheng, R. Zhang, and L. Yang, "Consumer-centered energy system for electric vehicles and the smart grid," IEEE intelligent systems, vol. 31, no. 3, pp. 97-101, 2016.

3. B. Muneer, V. Palazzi, F. Alimenti, P. Mezzanotte, and L. Roselli, "A way towards energy autonomous wireless sensing for EV battery management system," IEEE Journal of Microwaves, 2025.

4. X. Cui, M. A. Khan, S. Singh, R. Sharma, and S. Onori, "Towards a BMS 2 design framework: Adaptive data-driven state-of-health estimation for secondlife batteries with BIBO stability guarantees," IEEE Transactions on Transportation Electrification, 2025.

5. M. I. Ali, P. Patel, J. G. Breslin, R. Harik, and A. Sheth, "Cognitive digital twins for smart manufacturing," IEEE Intelligent Systems, vol. 36, no. 2, pp. 96-100, 2021.

6. J. Xie, R. Yang, S.-Y. R. Hui, and H. D. Nguyen, "Dual digital twin: Cloud-edge collaboration with Lyapunov-based incremental learning in EV batteries," Applied Energy, vol. 355, p. 122237, 2024.

7. H. A. Gabbar, A. M. Othman, and M. R. Abdussami, "Review of battery management systems (BMS) development and industrial standards," Technologies, vol. 9, no. 2, p. 28, 2021.

8. R. Fioravanti, K. Kumar, S. Nakata, B. Chalamala,

and Y. Preger, "Predictive-maintenance practices: For operational safety of battery energy storage systems," IEEE Power and Energy Magazine, vol. 18, no. 6, pp. 86-97, 2020.

9. M. Doyle, T. F. Fuller, and J. Newman, "Modeling of galvanostatic charge and discharge of the lithium/polymer/insertion cell," Journal of the Electrochemical Society, vol. 140, no. 6, p. 1526, 1993.

10. M. Alkhedher, A. B. Al Tahhan, J. Yousaf, M. Ghazal, R. Shahbazian-Yassar, and M. Ramadan, "Electrochemical and thermal modeling of lithium-ion batteries: A review of coupled approaches for improved thermal performance and safety lithium-ion batteries," Journal of Energy Storage, vol. 86, p. 111172, 2024.

11. A. Wang, S. Kadam, H. Li, S. Shi, and Y. Qi, "Review on modeling of the anode solid electrolyte interphase (SEI) for lithium-ion batteries," NPJ Computational Materials, vol. 4, no. 1, p. 15, 2018.

12. T. M. Bui, M. F. Niri, D. Worwood, T. Q. Dinh, and J. Marco, "An advanced hardware-in-the-loop battery simulation platform for the experimental testing of battery management system," in 2019 23rd International Conference on Mechatronics Technology (ICMT). IEEE, 2019, pp. 1-6.

13. K. J. Laidler, "The development of the arrhenius equation," Journal of chemical Education, vol. 61, no. 6, p. 494, 1984.

14. J. Gama, R. P. Ribeiro, and B. Veloso, "Data-driven predictive maintenance," IEEE Intelligent Systems, vol. 37, no. 4, pp. 27-29, 2022.

15. L. Koltermann, M. C. Cortes, J. Figgener, S. Zurmuhlen, and D. U. Sauer, "Improved rule-based power distribution algorithm for hybrid battery storage systems and real-world validation," Journal of Energy Storage, vol. 86, p. 111360, 2024.

16. F. Wang, Z. Zhai, Z. Zhao, Y. Di, and X. Chen, "Physics-informed neural network for lithium-ion battery degradation stable modeling and prognosis," Nature Communications, vol. 15, no. 1, p. 4332, 2024.

17. V. Sulzer, S. G. Marquis, R. Timms, M. Robinson, and S. J. Chapman, "Python battery mathematical modelling (PyBaMM)," Journal of Open Research Software, vol. 9, no. 1, 2021.

18. W. Zuo, H. Zheng, T. He, V. Vishwanath, M. K. Chan, R. L. Stevens, K. Amine, and G.-L. Xu, "Large language models for batteries," Joule, vol. 9, no. 8, 2025.

19. P. Dasgupta, D. Marriott, L. Li, and P. Narayanan, "Intelligent and autonomous systems in government," IEEE Intelligent Systems, vol. 40, no. 4, pp. 5-7, 2025.