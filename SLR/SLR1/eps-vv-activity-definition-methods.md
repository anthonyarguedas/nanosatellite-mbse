# Verbatim source quotations

## Development of a Cubesat Conceptual Design Tool and Implementation of the EPS Design Module

> The architecture testing sees the development of a test matrix that looks at different ways a user could operate the Conceptual Design Tool. As seen in Table 15, this includes different Use Cases, orbits, Design Methods, and missing information. There is also an expected outcome for each of these tests. While the tool is supposed to run nominally in most cases, some missing information or lack of selections should
>
> return an error in the tool, either through a written command line statement or through a pop-up window. Each of these test cases are to be run to see if their outcome is as expected.

Source report: `review-report-1009`. Pages 79–80.

> The testing plan for the CubeSat Conceptual Design Tool's EPS Design Module sees the development of test cases for the system. These test cases are already existing CubeSat designs, that have already gone through a conceptual design process
>
> or further design development. The inputs are found from published work, and then used within the Conceptual Design Tool.

Source report: `review-report-1009`. Pages 82–83.

> Two test cases were formally chosen for this step, comprised of CubeSat conceptual design studies rather than finalized CubeSat EPS designs. This was a result of the differing level of development between the two scenarios. For fully implemented CubeSats, the EPS papers delve into much more detailed design and their concept of operations for a mission gets fully expanded, resulting in parameters that are significantly more complex and nuanced than the Conceptual Design Tool is able to handle. For example, one mission had 14 modes in there nominal reference orbit alone [56].

Source report: `review-report-1009`. Page 83.

> With many subsystems remaining to be developed, the Subsystem Design Module validation testing will only get more challenging as users have to include more comprehensive test cases that cover all available subsystems. Therefore, a set of universal test cases, that cover the inputs and outputs for every subsystem, would greatly assist future validation campaigns, especially if they could be automatically ran through a test script rather than physically entered into the tool. However, it is recognized that such automation may not be possible under the existing software architecture.

Source report: `review-report-1009`. Page 99.

## Open-source CubeSat MBSE Approach to Address Traceability: Power Subsystem

> 3) Requirements Development: Requirements play a major role in systems engineering [9], as they: form the basis of system validation and stakeholder acceptance, act as a reference for integration and verification activities, and serve as a means of communication between the technical staff, management finance department, and the stakeholder community.

Source report: `review-report-0764`. Page 3.

> In the case of the power subsystem model, a UCD was constructed (Fig.3), as well as an SD so as to specify functions of the UCD if necessary. It can be seen that the power subsystem's main use case is generalized in two more concrete cases which are: "generate electric power" and "control". This last use case itself specified with other functions: "store power", "distribute power" and "protection". These different use cases can then be observed in different situations using sequence diagrams. For example, the manage energy use case may mean charging or discharging the battery and these cases can be realized in different conditions. Fig. 4 shows the battery in sunlight time. In this paper only nominal behavior is shown as in [30] without loss of complexity, mission modes are not discussed in this paper. However, the methodology presented here can be extended to take mission modes into account by creating complementary behavioral diagrams for the concerned
>
> modes.

Source report: `review-report-0764`. Page 4.

## An Implementation of Integrated Approach in Product Life-Cycle Management Tool to Ensure Requirements-In-Loop During Complex Product Development: A Cubesat Case Study

> Application of MBSE in PLM tool can be performed using an approach called RFLP. This approach is called on the four modelling pillars of MBSE [5]. RFLP approach aligns itself well with the modified V-model. In this paper an innovation method especially for space sector is defined to keep requirements-in-loop during the product development cycle. It is done by verifying each requirement during each phase by assigning a numerical parameter to each requirement. The functional, logical and physical simulations are performed with Design of experimentation intend and checked whether the design conforms to the requirements. The product being design is optimized using design of experiments tools which allows to built a web of different configurations and test each of them out to provide decision support [6] during the product developmental cycle. It allows to timely manage changes and reduce the complexity of configuration management all along the way.

Source report: `review-report-0499`. Page 2.

> Following a simulation, the parameters obtained are compared to the required parameters to determine if they meet the necessary requirements. If the requirements are not satisfied, the next experiment with different configuration is conducted as the earlier configuration is deemed infeasible. The Design of Experiments (DOE) technique is employed to modify the battery parameters associated with the EPS and power requirement parameters. An experiment matrix consisting of hundreds of potential configurations is created to evaluate and identify the optimal battery parameters that fulfill the desired power requirement. This technique guarantees that all requirements are met and is an effective tool for tracing the requirements.

Source report: `review-report-0499`. Page 7.

## Battery-aware scheduling in low orbit: the GomX–3 case

> The scheduling workflow, depicted in Fig. 6, loops through a two-step procedure of schedule generation and schedule validation. The latter is needed to account for the inaccuracies of the simple linear battery model, which is used for schedule generation, relative to real battery kinetics. Therefore any generated schedule is validated along the stochastically enhanced KiBaM known to be sensitive to such effects. If the validation does not exhibit good enough guarantees in the eyes of the GomSpace engineers, the current schedule is discarded and excluded from the generation step, and a new schedule is computed. Otherwise it will be accepted, upon which we break the loop and ship the schedule to orbit.

Source report: `review-report-1303`. Page 10.

> As mentioned, UPPAAL CORA's expressiveness does not allow for direct modelling of the KiBaM as a PTA. Instead the schedule computed is based on the simple linear model, that is known to not capture important effects that can be observed from measurements of real batteries. In order to validate whether the computed schedule truly doesn't violate the constraints we imposed, we need to validate the schedule along the above mentioned stochastic KiBaM with capacity limits. In fact, such a schedule can be seen as a sequence of tasks $ \left( T_{j}, I_{j} \right) $ , which can immediately be used as input to the method to bound the cumulative risk of premature battery depletion of the computed schedule. The initial KiBaM SoC distribution is assumed to be a truncated 2D Gaussian around the initial battery state given to the PTA network and white noise is added to the loads of the tasks. If the validation step exhibits a low enough depletion risk, the computed schedule is accepted, otherwise the schedule is excluded and another schedule is computed. This happened only once. Across the schedules evaluated "low enough" was interpreted as "below 0.2" though much stricter guarantees were actually at hand in two of the three cases.

Source report: `review-report-1303`. Page 13.

## Implementation of a 6U CubeSat Electrical Power System Digital Twin

> To implement the DT in the real-time simulator, the circuit models described in the second section were used. Additionally, appropriate tests were selected to validate the DT. One such test is illustrated in Figure 9, which presents a comparison of the SAR operation across three possible scenarios: MPPT mode, VEOC mode, and the transition between the two modes.

Source report: `review-report-0573`. Page 9.

> In CHIL-based simulations, the control circuit is physically implemented while the rest of the system is simulated in the HIL device. A diagram of the CHIL simulation that was implemented is shown in Figure 10. This type of simulation allows the validation of the operation of the control circuit under specific conditions. To illustrate this, the temperature of the solar cells in a typical LEO mission largely varies; solar cells can reach
>
> -50 $ ^{\circ} \mathrm{C} $ during an eclipse and $ +100^{\circ} \mathrm{C} $ during sunlight. Therefore, the control circuit must be evaluated under all possible SAS temperature conditions. In this case, the performance of the control system was evaluated across a solar cell temperature range of $ -50^{\circ} \mathrm{C} $ to $ +100^{\circ} \mathrm{C} $ , simulating the SAS behavior in the DT.

Source report: `review-report-0573`. Page 9.

## Simulating cubesat structure deployment dynamics

> A set of 11 trials was run to evaluate the sensitivity of the model to various input factors. The five input factors that were evaluated are root spring stiffness, panel-panel spring stiffness, side panel substrate modulus, center panel substrate modulus, and solar array add-on mass. Parameters were adjusted by 20% from the nominal value. The study was conducted with the intention of being used to develop physical test to validate the performance of the simulations. A summary of the results can be seen in Table 1.

Source report: `review-report-1357`. Page 15.

## A conceptual MBSE framework for satellite AIT planning

> One of the main objectives of modeling is to deliver reasonable answers to predefined questions (ROQUES, 2017). Therefore, the questions are used herein as criteria for evaluation of the model views, acting as a control for completeness.

Source report: `citation-report-1572`. Page 79.

> The system capabilities form the basis to define system level validation tests. Even though it is beyond the scope of this work, the author of this work highlight that the operational and system layers' models views support the definition of validation tests, specifically by using functional chains and operational scenarios.

Source report: `citation-report-1572`. Page 84.

> The criteria used to evaluate model views are stated as questions. If the model views provide all satisfactory and complete answers, they are considered sufficient. AIT team members shall evaluate the generated outputs and decide whether to move on to next step or to start it over.

Source report: `citation-report-1572`. Page 88.

> In this modeling phase, critical functionalities from previous step 1.2 (output 3) were decomposed in lower level functions, and these functions were allocated to physical elements. Using the traceability features, the modeler can trackdown the indications of critical components. The use of physical architecture verification chains is also an interesting source of information to attain this objective.

Source report: `citation-report-1572`. Page 95.

> The number of model views will be the same as the number of integration stages. The AIT modeler will use the collected information to assist the AIT team in planning electrical integration tests and system functional electric tests, which verify if the system was build (and is functioning) according to specifications.

Source report: `citation-report-1572`. Page 96.

> Inputs of Step 2.1 are system test requirements from system design verification matrix. These requirements will indicate the environmental tests scenarios.

Source report: `citation-report-1572`. Page 106.

> The outputs analysis from both steps represents an activity performed by all AIT team members to evaluate the outcomes and decide whether to finish Framework - Part II, or to start it over.

Source report: `citation-report-1572`. Page 107.

## A Model-based Methodology for Strategic Reuse of Legacy Designs in Space Mission Architecting

> Description: An important consideration in a reuse scenario is the degree to which the RCE will impact the testing and qualification campaign of the MoI. There are two primary considerations in this regard. First, the rework actions carried out on the RCE may be substantial enough to invalidate the certification of the RCE from its native mission - this is a concern at the architecture level of the RCE itself. Indeed, in its Systems Engineering Handbook, NASA stresses the need to understand the impact of the new mission context and rework efforts on the Technology Readiness Level (TRL) of the element: "If the architecture and the environment have changed, then the TRL drops to 5-at least initially". Therefore, changes made to the RCE necessitate at least an element-level re-certification. The second consideration regarding testing is related to the integration of the RCE into the reuse slot in the MoI - this is a concern at an architecture level above the RCE. A necessary aspect of this type of testing assessment is change propagation of rework actions on the RCE through the
>
> interfaces and potentially into other MoI elements $ ^{2} $ . At this level, however, an integration, assembly, and testing (IA&T) campaign is nominally required of both reuse and from-scratch solutions. Thus, it is not a new systems engineering effort imparted by the reuse decision, but rather one that must be tailored to one or the other design decision. Here we may rely on an organization's established testing, qualification, and verification and validation (V&V) activities as reusable patterns for re-qualifying the RCE and its integration in to the MoI architecture. The major output of this step is a determination of the impact on existing certifications and testing requirements of the RCE and MoI of a given rework action.

Source report: `review-report-0972`. Pages 149–150.

> Exploring Rework Actions A rework campaign is generated from the gaps in requirements and interface satisfaction noted in Table 5.15. Recalling the full description of Step 2.3 of the generalized procedure, rework assessment requires also supporting discipline analyses to determine feasibility and detailed aspects of each rework action; further, the impact of design modifications to potentially invalidate the testing and qualification pedigree of the original design must be assessed. In applying Step 2.3, we find mixed results in satisfying these analytical tasks with the information contained in the AC10 and DAILI mission models.

Source report: `review-report-0972`. Page 224.

> Verification and Testing Activities A powerful capability enabled by forward-looking modeling practices is the reuse of other systems engineering products usually developed alongside design specifications. This is especially true of testing and verification activities that often contribute significantly to mission schedules and budgets. The AC10 model allocates verification activities to many of its requirements that can be explored for reuse on DAILI. We focus specifically on those activities that are related to requirements that lead to rework actions. To that end, the last column of Figure 5.16 shows the names of AC10 verification activities that may be re-implemented on DAILI - indeed these activities must be re-run in order to ensure that design changes have not invalidated results. However, with the AC10 version of the verification procedures detailed within the model element linked in the table, it may lead to reduced schedule contributions of the activity on DAILI.

Source report: `review-report-0972`. Page 226.

> It should also be noted, that the AC10 verification campaign does not provide an exhaustive source of activities for DAILI. Indeed, there are rework actions for which no suitable existing AC10 activity is found; further, even actions that do contain reusable verification activities are not necessarily complete. For instance, for the CDH "Develop Autonomous Operations Capabilities" action, the verification campaign would include, in addition to the three activities listed, Day-in-the-life (DITL) testing, unit testing, edge-case scenario testing, etc., which would need to be uniquely developed for the DAILI mission. Similarly, rework actions for which component-level verification activities from AC10 have been identified (e.g., for "Battery DoD Decision") will also need to proceed through integration testing at higher architectural levels as the spacecraft is assembled. Nevertheless, the AC10 verification campaign provides a starting point for its successor, providing a template for many aspects of future testing and integration.

Source report: `review-report-0972`. Page 226.

## A radiation-reliability assurance case using goal structuring notation for a CubeSat experiment

> The evaluation of electronic piece parts performance related to the space radiation environment is Radiation Hardness Assurance (RHA) [3], [4]. RHA is the methodology for ensuring that the radiation environment does not degrade or damage the electronics to the point that the system can no longer function during the lifetime of the mission. This process includes defining system requirements, defining the radiation environment, selecting and testing COTS, and designing for radiation-tolerance. The result is a system that is reliable for a particular space environment and focuses on ensuring that the system can carry out the mission with electronics that have non-destructive failure modes and that system has mitigation or circumvention of radiation-induced errors and non-destructive radiation event failures. When reviewing the RHA process, it is important to present the methodology in a format that makes the discussion and review of the decisions made during the RHA process easy to follow. NASA's Office of Safety
>
> and Mission Assurance (OSMA) created the NASA Reliability & Maintainability (R&M) hierarchy that allows for the reliability and maintainability activities and decisions for a system to be presented in a graphical format [5]. In addition to making evaluation of the reliability of a system easier, the R&M hierarchy also moves reliability evaluation of systems into the Modelbased System Engineering (MBSE) paradigm. MBSE is the application of models to support activities related to system requirements, design, analysis, verification, and validation through the entire life-cycle of a system [6].

Source report: `citation-report-1689`. Pages 5–6.

> This thesis utilizes Goal Structuring Notation (GSN), a graphical argument notation, and the R&M hierarchy to create a model for system validation activities related to the radiation reliability of a CubeSat experiment. The argument is supported by total ionizing dose (TID) screening of COTS, system-level single-event latch-up (SEL) detection, isolation, and recovery, and single-event functional interrupt (SEFI) recovery in the microcontroller. These mitigation strategies were chosen because of the radiation environment expected for the mission and the expected rate of single-event effects (SEEs) compared to the required uptime to complete the science mission objectives of the experiment. The result is a graphical assurance case specifically for the radiation reliability of a spacecraft system that uses COTS instead of rad-hard parts.

Source report: `citation-report-1689`. Page 6.

> GSN provides a structure to indicate how claims are supported by sub-claims. These claims in GSN are represented as goals. An example goal is "COTS electronics pass mission SEL requirement: No latch-up seen up to $ 5 \times1 0^{9} $ protons/cm $ ^{2} $ ." A sub-claim, or child goal, is "FRAM
>
> passes proton SEL mission requirement." The goals for each of the electronic parts to pass the SEL requirement together support the claim that several of the parts in the system pass the SEL requirement. The assertion of evidence to support the truth of a goal is represented by a solution. An example solution is "No latch-up seen on FRAM(FM24CI6B) up to $ 6. 2 \times1 0^{9} $ protons/cm $ ^{2} $." The stakeholders reviewing the assurance case would then decide if the test result is evidence enough to support the goal of "FRAM passes proton SEL mission requirement." When documenting the reasoning between goals and child-goals, strategy elements are used. An example strategy is "Isolate and contain faults" which provides the task that specifies why the parent goal "Physical and functional pathways for fault propagation or combination are limited" is completed by the child goal "Latch-up faults are isolated and contained close to the fault source." Goals, strategies, and solutions make up the base of the GSN structure and are connected with solid arrows and indicate inferential and evidential relationships. In summary, goals and strategies are alternately refined until the goal is specific enough to be supported by a solution element which links to the results of parts tests, system tests, simulations and analysis, literature review, etc.

Source report: `citation-report-1689`. Pages 15–16.

> During the development of the model, incomplete lines of reasoning can be indicated with an undeveloped element symbol. This indicates that the goal or strategy is not fully supported. For example, if a test has not been completed for a goal, then the evidence is undeveloped. Also during development, multiple ways of making an argument can be notated by using the M of N
>
> options connector. For example, in Figure 4, a part can be considered SEL immune by either performing radiation tests to the level required by the radiation environment or by applying knowledge regarding the process technology. Either of these solutions would support the goal of a part being SEL immune. When the GSN model is reviewed, the undeveloped element symbol and the M of N options connector should not be used in the model. They are tools for the reliability team to use during development and when creating a high-level template for other designers to use.

Source report: `citation-report-1689`. Pages 17–18.

## A reference architecture for rapid cubesat development

> As teams progress from the design, they will test physical hardware. Before teams begin testing physical hardware though, they need to document their test plans. The Hardware Tests package includes workspaces for each subsystem that establishes consistency and makes it easier to generate the necessary tables to describe test activities. Each requirement should be tied to a test (sometimes multiple requirements can be verified by one test), and this can be done in diagram form. For example, if the Electrical Power System (EPS) lead needs to plan EPS testing activities, they can open up the EPS Tests bdd and follow the template process. If they drag and drop all of the applicable subsystem requirements onto this diagram, as shown in Figure 45, they can easily create test activities and assign a "verify" relationship between them, which automatically populates the included tables. In this example, notice the "Weigh Components" test, and that test verifies the EPS Subsystem Mass requirement. This pattern should be continued until each requirement is verified by some activity. Finally, the test activity tables provide a place to textually describe what happens in each test to verify the requirement(s). These tables are all useful for the Test Plans and Test Reports, keeping the model as the primary document instead of different files and formats for each subsystem. The subsystem requirement tables in this section also include a method for tracking testing progress while also establishing a common set of definitions. Previously, tests that were "not verified" for whatever reason were all in one category, causing confusion amongst stakeholders. Now, tests can be labeled from a drop-down menu as "not verified" for the specific reason and they are labeled in a color to bring attention to problematic tests. Figure 46 shows an example of how this could be used. The Verification Status legend is located in the Component Library and can be modified if definitions or categories change.

Source report: `citation-report-1691`. Page 88.

## A Scalable System Architecture for CubeSat Test & Evaluation for Enhanced Mission Success

> The requirements for the reference CubeSat Test & Evaluation system are based directly on validating the requirements for the reference CubeSat system. That is, every test & evaluation requirement is directly traceable to the CubeSat system requirement.

Source report: `review-report-0239`. Page 45.

> Quantifying the risk falls in the domain of risk analysis, which is one of the fundamental pillars of systems engineering. Several systems engineering tools have been developed to study the risk analysis of a system failure, including a preliminary hazard assessment (PHA); failure mode, effects, and criticality analysis (FMECA); and fault tree analysis (FTA). The following paragraphs will review the tools in depth and then apply the tools to the CubeSat T&E program.

Source report: `review-report-0239`. Page 49.

> The simulation involved running one thousand launches of CubeSat missions for each unique test spread. Twenty separate sources of errors were identified and used to inject errors into the simulated CubeSat and twenty sets of tests screened for these errors. Forty-one different arrangements of spreading out the tests between the various CubeSat models were included in the simulation.

Source report: `review-report-0239`. Page 67.

> The major systems engineering risk being reduced by the CubeSat Test & Evaluation system is design flaws or errors. The amount of risk reduction is based on the cumulative number of tests being performed and which CubeSat version upon which the test is being performed. Greater testing provides greater opportunity that every possible design flaw or error in the CubeSat has been corrected prior to launch.

Source report: `review-report-0239`. Page 71.

> The last step in determining the optimized test program was to create the Pareto chart that graphs the mission failure rates on the y-axis and the time spent testing on the x-axis. The various points were graphed on the chart. A Pareto frontier was drawn on the chart to represent the non-dominated (most efficient) solutions. The Pareto chart is shown in Figure 28 below.

Source report: `review-report-0239`. Page 89.

## Application of model-based systems engineering in small satellite conceptual design-A SysML approach

> The requirement diagram defines requirements, traceability, and the test cases that verify each requirement. Figure 4 shows the requirements contained in the requirements package to specify the NSS-1 system. For demonstration purposes, some requirements are suppressed to save space.

Source report: `review-report-1301`. Page 4.

> The relationships among the requirements and other model elements are important aspects of requirement diagrams. These include relationships for defining a requirements hierarchy, deriving requirements, satisfying requirements, verifying requirements, and refining requirements. Being able to ask a modeling tool to generate requirement traceability and verification matrices, and to perform an automated impact analysis when the requirements change, is an important time-saving feature for systems engineering. SysML requirement diagrams in this context are quite helpful to assess NSS-1 requirement specifications and their verification and validation (V&V).

Source report: `review-report-1301`. Page 4.

> A test case or other named element can be used in a similar fashion to represent any standard verification method, such as re-
>
> view, inspection, test, or analysis. NSS-1 is composed of seven subsystems. Each subsystem has a mass, and there is a total mass budget for the satellite of 50 kg. The ACS (Attitude control subsystem), CDHS (Command and data handling subsystem), payload, TCS (Thermal control subsystem), and RFCS (Radio frequency communication subsystem) subsystems draw electrical power from the EPS (Electrical power subsystem), which can supply a maximum of 80 W. Given the masses of all subsystems and the power requirements of five subsystems, we calculated the total mass and power demand for the satellite and compare it against the requirement.

Source report: `review-report-1301`. Pages 8–9.

## Contributions to eco-friendly satellite lean design for a sustainable space environment

> In this thermal analysis, only the most extreme hot and cold cases have been studied to include all possible scenarios in between.

Source report: `review-report-0532`. Page 191.

> Extreme hot and cold heating environments have been defined to encompass all possible scenarios in between. Table 8.4 provides a summary of the design hot and cold environments, with extreme and less pessimistic values taken from Thermal design & verification, ESA-TEC-MTT
>
> ECSS-E-ST-10-04C Rev. 1 Space Engineering (Space Environment) [17], and Spacecraft Thermal Control Handbook: Fundamental Technologies [18] respectively.

Source report: `review-report-0532`. Pages 193–194.

> As it can be seen in Table 8.1, the most restrictive consumption, leading to higher temperatures, is the Nominal Mode, while the most restrictive for low temperatures is the Released mode. When carrying out the simulations, two different models will be considered: the stowed model when the NADS is not deployed, and the deployed model when the NADS is already deployed. This is because in both configurations, the satellite will have different restrictive modes, and the degrees of rotation in each mode will also have to be taken into account. For example, the Nominal Mode is only applicable to the deployed model, since this
>
> type of operation is carried out with the NADS deployed. Similarly, the Released mode only applies to the stowed model. Additionally, based on the rotations stipulated in the ADCS simulations (which evaluate the rotations of each configuration in orbit), 30 different simulations are obtained, which will have to be performed for both configurations, rotations ( $ ^{\circ} / \mathrm{s} $ ) in all axes, or only for the Z-axis, and restrictive modes.

Source report: `review-report-0532`. Pages 195–196.

> Once the results were validated by the expert support team from ESA, the $ ^{3} $Cat-4 environmental test campaign in the thermal-vacuum chamber at the CubeSat Support Facilities (CSF) at ESEC-GALAXIA facilities (Belgium) was prepared. The entire procedure for this test is documented in the " $ ^{3} $Cat-4 Test Specifications and Test Procedures Full Assembly Verification Environmental Test Campaign - Thermal and Vacuum Testing" [23], prepared by $ ^{3} $Cat-4 team with the support of ESA ESTEC Thermal Control Section (TEC-MTT) for use with CubeSat Systems, which combines a tailored version of the ECSS standards with lessons learned from past CubeSat projects.

Source report: `review-report-0532`. Page 203.

> All the test descriptions include the requirements that have to be verified in order to determine if the test results are satisfactory. It also outlined the test specifications and requirements that define the conditions under which the test should be conducted and a detailed schedule of the test organization [23].

Source report: `review-report-0532`. Page 203.

> Furthermore, the temperature rate of change is determined based on the thermal analyses, considering the worst-case scenario with the highest thermal gradients. The temperature rate of change is set at 0.25 K/min, which complies with the facility's specifications. The maximum temperature rate of change expected in orbit is 1 K/min.

Source report: `review-report-0532`. Page 206.

## Developing a CubeSat System MBSE Reference Model - Interim Status #5

> - Confirmation of the above five over-arching elements as necessary and sufficient: stakeholders, technical measures, use cases, requirements, and architecture. If not, modify accordingly.

Source report: `citation-report-2362`. Page 4.

> The engineering methodology should address the extent that the technical measures, use cases, and requirements adequately define the design space. There is a trade-off between not enough detail and unnecessary detail. This has been referred to as requirements truncation or termination. That is, how do you know when enough is enough relative to requirements development and specification. The MSM supports defining requirements development all the way down to the subsystem component level or truncating requirement development based on defining use cases and verification strategies.

Source report: `citation-report-2362`. Page 5.

> The verify relationship is a relationship between a requirement and a test case or other model element that is used to verify the requirement is satisfied. The relationship is shown with a dashed line pointing from the test case to the requirement or other model element.

Source report: `citation-report-2362`. Page 5.

> Sections 2.2.3 Model Evaluation and 2.2.4 Establishing Model Evaluation Criteria provide a set of model validation questions. A set of model validation requirements have been derived and mapped to the questions. The validation questions and requirements have been populated into CSRM packages and tables. Satisfaction of the validation requirements will be recorded in the tables.

Source report: `citation-report-2362`. Page 6.

## Developing a Model-Based System Engineering Methodology for CubeSat Missions

> After capturing what is to be accomplished with the Mission Objectives, the desired performance of these accomplishments should be captured as Success Criteria (SC). These success criteria should be split into Minimum Success Criteria (MSC), which represents the minimum that must be achieved to consider the mission a success, and Full Success Criteria (FSC), which represents the entire performance that is desired to be met.

Source report: `review-report-0299`. Page 50.

> - Verification Method: Defines how the requirement will be verified to ensure it is being met. This should include the following options: Test, Analysis, Inspection, and Demo.

Source report: `review-report-0299`. Page 56.

> - Verification Status: Defines whether the requirement has been verified using the previously defined method or not. This should include at least two options: Not Complete and Complete.

Source report: `review-report-0299`. Page 56.

> - Priority: Defines the criticality of the requirement. Typically includes mandatory, desired, or luxury/low.

Source report: `review-report-0299`. Page 56.

> - Define How to Meet the Top-Level Mission Requirements: System functions and functional exchanges should be used to illustrate how the Top-Level Mission Requirements can be met. A functional process can also be used, which demonstrates a chain of functions to show how they work together to fulfill a top-level requirement directly. There will likely be several different views captured here, including one of the overall CONOP, from launch to mission termination, and one of each experiment or demonstration that needs to be completed. Again, this involves considering what the system as a whole needs to do, rather than delving into the subsystem functionalities. This information should be captured in SABs and Scenario Diagrams. The latter can be used to show the sequencing and timing needs. For example, if an experiment requires data collection for a specific duration, or if certain functions need to be executed iteratively. The information defined in this step can be used to populate the Science Traceability Matrix and the Supporting Analysis View Products.

Source report: `review-report-0299`. Page 57.

> All Phase B steps are iterative and must be repeated until the functional design satisfies the requirements and mission objectives. Phase C will then focus on the physical architecture and optimizing the baseline design captured in this phase.

Source report: `review-report-0299`. Page 65.

> The system architecture diagrams should also be used to capture the required experiments needed to fulfill the Mission Objectives and Success Criteria. An example of this is shown in Figure 4.11 for Experiment 1 of the N2 mission, which focuses on collecting science data over the polar regions to fulfill Mission Objective 1 and the corresponding Full Success Criteria. Additionally, derived system-level requirements from these functions were captured on the same diagram. Lastly, a functional scenario diagram was used to capture the same experiment and understand the sequence of steps, as well as the timing needs. It can be seen that the data collection duration over the poles will be 15 minutes. Additionally, loops were used to illustrate that this process is repeated throughout the mission. The inner loop, titled LOOP [until neutron_count $ \geq 10,000 $ ], notes that this series of functions needs to be repeated until 10,000 neutron counts are collected based on the Success Criteria for Mission Objective 1. The outer loop, titled LOOP [repeat every 6 months], indicates that 10,000 counts need to be collected after 6 months to understand how the solar cycle impacts neutron flux, as described by the Success Criteria for Mission Objective 1. A requirement for the lifetime of the system was derived from this loop, showing that requirements can be added to different types of diagrams.

Source report: `review-report-0299`. Page 84.

## Effective Model-Based Systems Engineering framework for academic nanosatellite project management and design

> - The 'Verified By' column shows the specific test cases that determine how the system meets the requirement. For example, the "Bus System Activation" activity diagram (Fig. 23), which is part of the LEOP flow (Fig. 22), is used to verify operational requirement 100.1.6.

Source report: `review-report-0546`. Page 13.

## Enhancing CubeSat Design through ARCADIA and Capella: A Concrete Application

> AIV/AIT plan definition is at a different level of modeling with respect to the system design. However, it is inherently connected with system functioning and architecture.

Source report: `citation-report-1573`. Page 19.

> Each activity is further described by a set of procedures which can be assigned to team members, monitoring the progress status.

Source report: `citation-report-1573`. Page 20.

## Enterprise modeling for CubeSats

> The integrated model enabled the execution of trade studies to evaluate mission performance and verify that mission requirements would be satisfied. Requirements were defined for data collection, storage, download and for battery capacity and margin. Data collection and management and power collection and management subsystems were modeled in order to demonstrate the interdependencies of these requirements. Energy state trade studies varied the solar panel area and battery capacity. Data collection trade studies varied the orbital altitude and ground station network.

Source report: `review-report-1554`. Page 11.

## Integrated model-based systems engineering (MBSE) applied to the Simulation of a CubeSat mission

> Requirement diagrams depict requirements and their relationship with other requirements, design elements, and test cases to support requirements traceability, satisfaction, and verification.

Source report: `review-report-1563`. Page 3.

> Detailed modeling was minimized by excluding several other non-critical subsystems, such as attitude determination and control. The energy and data dynamics of these other subsystems, which were less important to capture in our models, are grouped into the Bus subsystem.

Source report: `review-report-1563`. Page 4.

> The integrated RAX CubeSat model was used to analyze performance of different hardware and mission configurations. The trade studies were motivated by common design questions for realistic CubeSat missions. In the current practice of satellite design, tools such as STK and MATLAB are used to analyze mission performance. However, there is no readily available capability that enables verifying the impact of design decisions on mission requirements throughout the entire mission. The integrated model demonstrates how to accomplish this by performing mission simulations using MBSE models.

Source report: `review-report-1563`. Page 10.

> To evaluate impact of solar panel area, three different sizes were selected: nominal of 18.2 $ cm^{2} $ per side, a half, and a quarter of the nominal size. The integrated CubeSat model was executed for each of the three configurations and time history of energy state was collected. Figure 16 compares time histories from the simulations. For all three designs, maximum battery capacity was fixed at 115,000 J. One system requirement was that "the energy level in the battery shall not drop below 92,000 J". The max and min bounds are shown as flat lines in Figure 16. Energy level of the nominal design stayed within the bounds during the mission. When the solar panel area was reduced by half, energy level still stayed within the bounds, although it was well below the max capacity. When the solar panel area was reduced further, to a quarter of the nominal, the energy level went below the required minimum at the end of the simulation. The flat area of the energy level in the middle indicates that the rate of energy collection of the solar panel was equal to the rate of energy consumption by the satellite when it was idling. The results clearly show that the quarter size solar panel is too small for the mission.

Source report: `review-report-1563`. Page 12.

## Model based systems engineering (MBSE) applied to Radio Aurora Explorer (RAX) CubeSat mission operational scenarios

> - Analysis Scenario 1: Given the data download rate $ ( r_{dl} ) $ and the available power $ ( p_{dl} ) $ , compute the maximum feasible SNR for the communication link.

Source report: `review-report-1621`. Page 9.

> - Analysis Scenario 2: Given the data download rate $ ( r_{dl} ) $ and the desired SNR, compute the minimum feasible power required $ ( p_{dl} ) $

Source report: `review-report-1621`. Page 9.

> - Analysis Scenario 3: Given the available power $ ( p_{dl} ) $ and the desired SNR, compute the maximum feasible data download rate (r_dl) that can be achieved.

Source report: `review-report-1621`. Page 9.

> To capture realistic power scenarios, we have developed a simulation that consists of simulations and analysis components from STK, SysML, and MATLAB. PHX ModelCenter acts as the glue that ties them together. We model dynamic orbits, opportunities to collect energy and download data, realistic schedules. We use the model to investigate the time history of the satellite states, including the on-board energy and data, and the amount of downloaded data.

Source report: `review-report-1621`. Page 9.

## Model-Based Systems Engineering approach in Capella for Concept of Operations and Operating Modes: Methodology Comparison across Space Systems Domains

> ConOps elements are modeled concurrently with this structural development. Mission phases - such as launch, commissioning, or nominal operations - define the operational timeline. Within each phase, the system may adopt different internal configurations or behaviors - captured as Operating Modes. These OMs, defined through Capella's state machine diagrams, represent both the system's status (e.g., Safe Mode, Science Mode) and the conditions under which transitions occur (e.g., power thresholds, visibility events, fault recovery). At the subsystem level, Modes represent variations in functional behavior (e.g., Payload Active, TTC Idle) based on the current mission phase and system objectives.

Source report: `review-report-0377`. Page 3.

> This bidirectional structure supports both design derivation and behavioral execution. The required operations "drive the design of" the architecture by defining available capabilities and constraints; conversely, the architectural elements "execute" the operations, activating specific functions and behaviors in time. For instance, an OM such as "Science Acquisition" will dictate the active configuration of subsystems, turning on payload components, activating data storage, and powering down nonessential services. These behavioral requirements must be anticipated and satisfied by the architectural layout defined at the LA and PA levels.

Source report: `review-report-0377`. Page 4.

## Model-Based Systems Engineering for Aerospace Applications: Strategic Requirements Prioritization in Complex Adaptive Systems and Digital Integration

> A key dimension of MBSE tool selection lies in the ability to support disciplined requirements prioritization and verification alignment. In complex aerospace systems, requirements are not uniformly critical; some have a greater impact on safety, mission objectives, or regulatory compliance. As such, MBSE environments must not only capture and manage
>
> requirements but also enable analysts to systematically rank, trace, and validate them throughout the lifecycle.

Source report: `review-report-0378`. Pages 112–113.

> Following that approach, the SidSat case study used the framework to evaluate a validated set of 113 actionable requirements derived from the complete requirement matrix within the SysML model. These requirements were drawn from multiple areas, including communication, performance, battery evaluation, environmental resilience, mechanical structures, power systems, and mass properties. Broad category labels, such as "Functional" or "Environmental," were excluded to focus exclusively on specific and testable requirement statements. Each requirement was evaluated using the four criteria defined in Chapter 3:

Source report: `review-report-0378`. Page 255.

> The decision matrix was constructed using a tabular structure in which each row corresponded to one of the 30 high-priority requirements identified through filtration. Columns represented weighted evaluation criteria grouped into two major dimensions (Saaty, 1990; Herrmann & Daneva, 2008):

Source report: `review-report-0378`. Page 259.

> - Requirement Criticality Factors: Derived from Method 1, including business value, urgency, implementation effort, and risk impact.

Source report: `review-report-0378`. Page 259.

> - Modeling Feasibility Factors: Derived from Method 2, including SysML compatibility, simulation support, tool-specific traceability, and parameter binding capability.

Source report: `review-report-0378`. Page 259.

> The matrix also highlighted several requirements with high mission impact but lower modeling feasibility, such as those that require external hardware validation or lack tool-native constraint interfaces. These were flagged for further development of offline test cases and hardware-in-the-loop validation.

Source report: `review-report-0378`. Page 260.

> The integrated simulation and validation framework, linking Cameo Systems Modeler with MATLAB and STK, enabled a structured digital engineering process that transformed system requirements into executable test cases (NASA, 2020). Simulation results were automatically compared to model-defined constraints, producing verifiable outcomes that ensured system compliance and readiness. The Beartooth nuclear testbed project demonstrated how combining MBSE and digital twin models enhances traceability and real-time simulation in safety-critical environments (Houck et al., 2022). The following five validation scenarios demonstrate this model-in-the-loop approach, each mapped to specific system-level requirements.

Source report: `review-report-0378`. Page 274.

## Model-Based Verification Strategies Using SysML and Bayesian Networks

> Verification activities, which usually take the form of a combination of analyses, inspections, and tests, consume a significant, if not the biggest, part of the development costs of large-scale engineered systems [1]. Verification occurs at various levels of a system's decomposition and at different times during its life cycle [1]. Under a common master plan, low-level verification activities are executed as risk mitigation activities, such as early identification of problems, or because they are not possible at higher levels of integration [1]. Therefore, a verification strategy is planned, "aiming at maximizing confidence on verification coverage, which facilitates convincing a customer that contractual obligations have been met;
>
> minimizing risk of undetected problems, which is important for a manufacturer's reputation and to ensure customer satisfaction once the system is operational; and minimizing invested effort, which is related to manufacturer's profit" [2]. Essentially, verification activities are the vehicle by which contractors can assess evidence of contractual fulfillment in acquisition programs.

Source report: `review-report-0591`. Pages 1–2.

> Specifically, consider two system parameters such as the power consumption of the system (denoted by $ \theta_{1} $ ), the maximum temperature of the system (denoted by $ \theta_{2} $ ), a power consumption test (denoted by $ \nu_{1} $ ), and a temperature measurement (denoted by $ \nu_{2} $ ). Clearly, the power consumption test provides information about the power consumption of the system (hence the link between $ \theta_{1} $ and $ \nu_{1} $ ). Similarly, the temperature measurement provides information about the system's temperature (hence the link between $ \theta_{2} $ and $ \nu_{2} $ ). In addition, we know from physics that the temperature of a system depends on its power consumption, so we can infer to some extent one from the other (hence the link between $ \theta_{1} $ and $ \theta_{2} $ ). Conditional probability tables or functions are then used to characterize such graph networks. In this way, given a prior confidence on the state of any of the system parameters (for example, $ \theta_{1} $ or $ \theta_{2} $ ), the confidence is updated using the Bayesian rule [27] as per the evidence gathered when executing related verification activities (for example, $ \nu_{1} $ or $ \nu_{2} $ ). In essence, if the verification activity is successful, the confidence of the system exhibiting a certain attribute (or meeting a requirement) increases. If the results of the verification activity are not satisfactory, then such confidence decreases.

Source report: `review-report-0591`. Page 4.

> In this task, we extend the profile developed in task 1 to enable the connection of systems models with verification models. The key idea of this task is that the definition of verification elements, such as test configurations, can be established by directly pointing to the systems model instead of creating them manually. This is a threefold undertaking. First, as stated earlier, avoiding manual repetition of information in different models can reduce errors due to information inconsistencies. Second, the systems model restricts the possible configurations in which the system may be used, thus enabling earlier assessment of feasibility and adequacy of test configurations and other verification artifacts. Third, by leveraging existing systems models, we can seamlessly predict and define analyses and test pass/fail criteria by interrogating the systems model directly.

Source report: `review-report-0591`. Page 6.

> Once the status of the verification strategy has been updated in the Bayesian model and the confidence values have been calculated, these values are to be automatically stored in the SysML model as value properties. These values may be used to inform future decisions regarding the verification strategy (i.e., whether further verification activities are required). In this way, the verification strategy itself can be simulated.

Source report: `review-report-0591`. Page 11.

## Modeling Radiation Risk Assessment and Mitigation for Spacecraft Electronics

> Many of the COTS components used to meet performance requirements have a large state space to consider for radiation testing consisting of different modes, frequencies, and power levels. The complexity makes qualifying the components for all of the possible operating modes, frequencies, or power levels unreasonable [4]. The components then are qualified only for their use in a specific system. As a result, risk assessments make many assumptions about component use when analyzing the risk from the radiation environment for a system. These analyses are increasingly including system-level mitigation and using radiation test results that are from similar components or even not using radiation tests at all. Leveraging MBSE would make these analyses more transparent and enable the engineers to keep up-to-date with design changes. While NewSpace, which includes CubeSats and large near-earth constellations of satellites [1], seem to be driving constraint-driven design and the resulting changes to the radiation hardness assurance process, missions of all classifications can take advantage of and even require these changes [5].

Source report: `review-report-1254`. Page 14.

> Single-Event Effects Criticality Analysis (SEECA) is the analysis of SEEs on system performance [82]. The process is an implementation of functional analysis, usually a systems engineering task, for radiation-induced faults. The goal is to determine the effects of SEEs on the functions of the component, sub-system, or system, in order to define the problem and to
>
> implement mitigation that minimizes the impact on the system. The first step is recreated from [82] in Figure 19. The goal is to determine the criticality of the functions and what components, sub-systems, or systems implement that function. If the function is error-functional, meaning it
>
> can tolerate many faults, then components are chosen that have a predicted error rate that is less than the availability requirement for that function. If the function is error-vulnerable or error critical, meaning it can tolerate only a few faults or no faults, respectively, then components and mitigation are chosen to drive the error-rate to zero.

Source report: `review-report-1254`. Pages 54–56.

> For the linear regulators on the REM experiment board, the quiescent current and the regulated output voltage were the main parameters of concern. The line regulation and load regulation were not of concern since the input voltage and output load were not expected to change much during the mission. The experiment running on the REM board was not also expected to be sensitive to noise or ripple. These parameters were checked using a visual inspection of the output voltage on an oscilloscope during testing. Since the application circuit did not use logic levels or power bus voltage close to the datasheet limits, the shutdown threshold and minimum input voltage were not precisely measured. Instead, they were checked with a pass-fail test. Lastly, the current limit was not checked because the system was also using a load switch with a lower current limit
>
> than the one on the linear regulator. Figure 23 shows the modified fault model. The TID-induced faults originate from the "TID" fault block. The main faults of concern are a change in the output voltage and leakage current. The change in the output voltage is modeled as the anomaly "Out_of_spec_Voltage" and propagates out of the component through the "Vout" port. The anomaly "Leakage_Current," the increase in power supply current, propagates out of the component through the "Vin" port.

Source report: `review-report-1254`. Pages 59–60.

> When mitigation strategies can be represented in fault propagation models, the automated fault tree generation provides a means to analyze the effectiveness of the mitigation in terms of the functionality of the board. The effect of applying the mitigation strategy will be reflected in the lower probabilities associated with the corresponding fault that is mitigated. In the case that the mitigation strategy does not cover every fault path, this would also be brought out in the FTA.

Source report: `review-report-1254`. Page 69.

> GSN provides a structure to indicate how claims are supported by sub-claims. These claims in GSN are represented as goals. An example goal is "Part is not susceptible to SEB." A sub-claim, or child goal, is "Probability of failure from SEB is less than 1%." The goal for the reliability of the electronic components to not experience an SEB-induced failure supports the claim that the part is not susceptible to SEB. The assertion of evidence to support the truth of a goal is represented by a solution. An example solution is "The probability of failure from SEB is 2%." The stakeholders reviewing the assurance case would then decide if the probability of failure of 2% is evidence enough to support the goal of "Part is not susceptible to SEB." When documenting the reasoning between goals and child-goals, strategy elements are used. An example strategy is "Determine part susceptibility to SEB," which provides the task that specifies why the parent goal "Part is not susceptible to SEB" is completed by the child goal "Probability of failure from SEB is less than 1%." Goals, strategies, and solutions make up the base of the GSN structure and are
>
> connected with solid arrows and indicate inferential and evidential relationships. In summary, goals and strategies are alternately refined until the goal is specific enough to be supported by a solution element that links to the results of components tests, system tests, simulations and analysis, or literature review.

Source report: `review-report-1254`. Pages 79–80.

> At the beginning of Phase B, generic goals are generated for the GSN argument from part assurance templates and provide a framework for planning RHA activities. For example, the requirement RAD1 in Figure 42 implies that there is a goal that the components in the system survive SEB. In order to meet that goal, the components in the system that are susceptible to SEB need to be identified. Then their probability of failure needs to be calculated. In order to make these calculations, the mission environment needs to be estimated, radiation tests need to be found or performed, and then the susceptibility of the component can be evaluated by calculating a probability of failure. These activities will happen throughout Phase B.

Source report: `review-report-1254`. Page 88.

## Preliminary Design of Satellite Systems through the Integration of Model-Based System Engineering and Agile Methodologies: Application to the 3ColStar Mission

> - Bidirectional Traceability: Bidirectional traceability was established to ensure that each requirement could be traced forward to its corresponding design elements and backward to its source. This was achieved by creating traceability links between the requirements and their associated system functions, logical components, and verification test cases. For instance, the requirement for data transmission every 30 min was linked to the design specifications of the IoT payload, ensuring that all aspects of the requirement were addressed. This was validated with the link budget model developed by the communications team.

Source report: `review-report-0610`. Page 26.

> - Connectivity Diagrams and Matrices: Capella provided diagrams and matrices to visualize the relationship between requirements and their corresponding design elements. These representations were used to verify that all components, functions and actors were fully addressed and to monitor how changes in the architecture impacted the design. For example, traceability matrices from the system's physical level showed, from multi-physics analysis, the alignment of the solar weather payload's accuracy requirement with its corresponding design elements and test cases.

Source report: `review-report-0610`. Page 26.

> - Validation and Verification: From the system architecture based on the Capella model, the validation and verification were established by using additional tools, such as Ansys STK, NASA GMAT, Matlab and Simulink, throughout the project. From the component to system level, each part was linked to test cases and validation criteria, enabling systematic verification of compliance with mission objectives. For example, test cases related to the solar radiation measurement accuracy were linked to the specific design elements responsible for this function, ensuring that the requirements were validated through testing.

Source report: `review-report-0610`. Page 26.

> - Traceability Diagrams: Diagrams like Requirement Coverage Diagrams visually represented requirement coverage by system elements, highlighting any gaps or overlaps.

Source report: `review-report-0610`. Page 28.

## Present the System Design Process and Review of Specifications of a Very Low-Cost 6U CubeSat Platform to Improve Accessibility to Space Based on Pluto Experience

> The requirements are the do's and don'ts that, if met, can ensure that the purpose of the mission is satisfied. The European space agency has recommended a way to publish the requirements on the ECSS-E-ST-10C document. This document recommends first writing requirements based on the space environment, the purpose of the mission, and the lessons learned from previous CubeSats. Next, the sentences should review, then the importance of having those requirements is examined in the structure of RTM and finally published [13]. In other words, the requirements allocated to the system elements and their interfaces are traceable to the customer's requirements baseline [14]. Researchers have associated the waterfall methodology with "requirement freezing" early in the development life cycle, making the project inflexible and unable to respond to changing requirements or use cases. Also, high costs and efforts seem to be a major downside to the waterfall design process [15]. The goal here is to speed up the design process, so the minimum requirements for a platform are mentioned here to facilitate the selection among off-the-shelf components. Developing the correct requirements will lead us to choose the COTS in the right way. We need to achieve a specification tree base on the subsystem requirements. The requirements that are presented here are based on the experience of the Pluto team, CubeSats standards, review of documents from other satellites, and the statistical study to obtain the interfaces and the technical budget required to support the maximum range of payloads (the most crucial factor in designing a platform is
>
> to be able to service the broadest possible range of payloads with different purposes and different interfaces).

Source report: `review-report-0773`. Page 4.

> RTM:Requirements are verified by one or a combination of these methods: design review, testing, inspection, or analysis methods [16]. One example of a row of the Pluto platform's RTM is shown in Table 2. RTM table includes columns of numbering, determining the root and reason for existing of a requirement (design, product assurance, communication, environments, functional, mission verification), description of the requirement, subsystems to which the requirement is referred, requirement status (TBD, TBC, CONFIRM, TBR), requirement verification method (review, test, inspection, analysis), requirement approval phase (Design, En_Model, Q_Test, A_Test, Orbit Operation, pre. launch), date of the last review, requirement confirmation officer. System requirements are referred to subsystems and
>
> are used to formulate subsystem requirements. Subsystem requirements drive the design to the product tree.

Source report: `review-report-0773`. Page 5.

> Justifying and tracking the requirements helps us to justify the design. A row from Pluto's RVTM table is shown in Table 3. As can be seen for each requirement, the functional structure, validation phase, test description, the necessary physical structure in the related subsystem, the physical interface structure, and the description of the verification method are shown. Moreover, to be as clear as possible, the mode that requirement is necessary to fulfilling it is mentioned.

Source report: `review-report-0773`. Page 5.

> The States of Operation include system status (mode) in each phase of satellite life. By defining modes, the state of each subsystem and their components in every step of the satellite life cycle is obtainable. The functional structure tree helps
>
> to understand what phases and modes we need to accomplish the mission goal. The functional structure developed for the Pluto platform is shown in Fig. 2. As seen in the functional structure, the satellite has four operating phases and ten operating modes. Each mode also has several use cases that are called or not called depending on the conditions of entering the mode. These conditions will be described in the CONOPS and sequence diagram. These phases, modes, and use cases are defined to cover all the operational requirements of a platform in the simplest way. It is noticeable that the mission mode is defined according to the type of payload and is not described here.

Source report: `review-report-0773`. Pages 5–6.

## Radiation Assurance of CubeSat Payloads Using Bayesian Networks and Fault Models

> NASA is creating a Model-Based Mission Assurance (MBMA) paradigm to incorporate reliability into the Model-Base System Engineering (MBSE) paradigm. This work uses the Model-Based Assurance Case + (MBAC+) process and the System Engineering and Assurance Models (SEAM) tool set to support the modeling activities of requirements, design, and reliability engineering [4]. In Figure 1, the integrated approach is presented. Goals derived from mission objectives and environment and how they are met in the system design are captured in System Modeling Language (SysML) functional decomposition and block diagram models. The graphical argument that the goals lead to a reliable system is done using the Goal Structuring Notation (GSN) standard. While the SysML and GSN models are linked in the SEAM tool set, the underlying fault propagation model is used to construct the Bayesian network model. The Bayesian network model is then used to study the sensitivity of the design to radiation which supports the evidence for the goals that argue for the radiation reliability of the system. These three modeling standards and the process of creating and linking them form the MBAC+ process.

Source report: `review-report-1350`. Page 2.

> The nodes and edges in the Bayesian network structure are identified by traversing all the fault paths in the system model. The nodes include faults, functional effects, mitigation functions, and observable anomalous conditions captured in the system fault model. Edges are added between the nodes if a fault path or functional dependency is identified. The structure is refined by grouping the radiation-induced failure modes as environment nodes. Also, wherever possible, anomalies, degradation, and mitigation responses are abstracted into component nodes whose states correspond to the health of the component or functionality of the component. The graph is further simplified based on expert knowledge. Figure 5 shows the refined Bayesian net for the load switch SRAM system for the best and worst case environments.

Source report: `review-report-1350`. Page 3.

> The conditional probability tables for each node in the Bayesian network model take into account the impact of radiation as well as the impact of "degraded" performance of related components in the system. The Bayesian network sensitivity analysis helps reveal the relative strength of parameters in the conditional probability table to influence the target nodes like the system operation or performance of a specific component. This could be useful in performing more directed testing and design changes to improve the overall system performance.

Source report: `review-report-1350`. Page 4.

> The integrated approach presented in this paper creates a system level radiation-induced fault model from the fault model of individual parts, taking into account functionality degradation and mitigation measures. The fault model helps create the structure of both the GSN assurance case model and
>
> the Bayesian network model by identifying the possible fault paths and related effects on functionality. The results from the Bayesian network analysis are useful in understanding the sensitivity of system performance to radiation effects in specific parts, thereby providing additional information to prioritize parts testing, adjust radiation margins, and update the design to add radiation-effects mitigation.

Source report: `review-report-1350`. Pages 4–5.

## Reliability Analysis and Failure Mitigation Strategies for the PROVE Pathfinder CubeSat Payload

> There have been several different techniques of both fault analysis and robustness applied to CubeSat design, many of which are described for general space missions [6], [7]. While analyzing possible failure modes, there are two main approaches. Fault Tree Analysis (FTA) is a top-down approach, that starts with a total system failure and works down, exploring each possible cause until the component level is reached. This is useful for analyzing the combined effects of faults, but poor at illuminating all their possible causes. Failure Mode Effects and Criticality Analysis (FMECA) is a bottom-up approach, that starts with each component and explores how the effects of a failure propagate through a system. This technique is very effective at describing most of the causes of faults in a system but struggles to explore how their effects may combine.

Source report: `review-report-0933`. Page 3.

> The main input to this process was a comprehensive Product Breakdown Structure (PBS), defining each of the components of the system, to as high a level of detail as possible. Once every system component was defined, the methodology followed the 7 steps below.

Source report: `review-report-0933`. Page 3.

> 1. Define Failure Modes and Causes-Firstly every conceivable way in which a component might fail during the mission, along with the cause, was identified. The difference between failure mode and cause of failure is commonly poorly identified, however in this instance "failure mode" is defined specifically as the resulting state that the component enters after failing and the "cause of failure" is defined as is.

Source report: `review-report-0933`. Page 4.

> While this process did not provide an accurate figure of the likelihood of a failure occurring or its true criticality, it allowed a comparison between the failure modes to illustrate which were more critical than others. Hence the highest priority failure modes were highlighted and any component with a failure mode scoring above fifty was carried forward to the second stage. This is where quantitative figures of MTTF and other available data were used to produce more rigorously estimated figures of criticality. A range of sources
>
> were used to obtain these values, and where possible multiple sources were considered for each component.

Source report: `review-report-0933`. Page 4.

> The complete fault tree developed for PROVE Pathfinder was found to be very extensive, and many of the components were lacking in MTTF's. Therefore, to better focus development work, a second fault tree was produced, reduced to just the high criticality failure modes, as it was hoped that the lower criticality failure modes would have an insignificant effect on the reliability of the system. However this did mean that the estimates discussed in the next section were optimistic, as they did not include all the potential failure modes of the system.

Source report: `review-report-0933`. Page 7.

## small sats lifecycle management through mbse aided decision making tailored tool

> Verification and testing activities are defined since the Phase A of a space mission and continue to be refined during the entire product development. The classical approach exploits traceability links between textual requirements and tests procedures. Relying just on them to derive test campaigns results in a lack of a detailed vision of the needs, also reducing the possibility to identify problems. This is due to the inability of textual requirements to cover all system aspects. As presented in the previous sections, an articulated model has been created with the aim of defining any functional and physical aspect of the system. Such model elements provide precise basis for a test campaign definition; however, to explicitly define test activities, new ad-hoc ones are introduced. The power of the here proposed approach resides in the guidance provided by the same model elements used as source of knowledge in the definition of the AIV/AIT plan. It is reminded that the approach must be intended as a prototype proposal, since it sometimes results in contrast with some of the ARCADIA concepts. The reader is invited to focus on the gained benefits as it is recalled that ARCADIA does not propose a way for managing test activities within the architectural model.

Source report: `review-report-1073`. Page 9.

> Going back to Fig.18, the second link is analysed. Right clicking on the blue stamp Functional Chain EPS testing activities, it is possible to open the Physical Functional Chain Diagram in Fig.20. Two new elements can be noted: the dark green blocks with the Functional Chain icon on the top left and the yellow blocks with the {c} icon. They are respectively Functional Chains expressed in a compact form, here exploited to create a bridge between the test activities and functional model elements, and Constraint blocks. The proposed approach is simple: some Functional Chains are already defined within the model in the previous functional analysis; since all test activities necessarily refer to the system
>
> functional or interface analysis, whenever it is decided to conduct a certain test systems engineers can exploit the chains reported in dark green blocks which contain such functional aspects of the system. Any Functional Chain can be added to this diagram to cover any system aspect, assuming it was properly modeled before. This is also very useful since during test activities problems typically arise and some changes have to be applied to the system; in this case, engineers can go back to the architectural model, refine the analysis, and finally exploit the new Functional Chains for a further check. This is what the green blocks show, a compact form of Functional Chains used as reference; an expanded view of one of them is reported in Fig. 21. The Constraint element is used to explicitly "allocate" such Functional Chains to activities; this is not a formal allocation, but more a graphical one used for this preliminary version of the approach.

Source report: `review-report-1073`. Pages 9–10.

> The advantage of dealing with AIV/AIT activities within the same environment in which the system was modeled resides in the possibility to exploit all the knowledge and information embedded in the model. So, for example, in the context of system integration, Physical Links can be consulted to check the correctness of the integration plan serving also as base for its definition. The presented approach is demonstrative and experimental and requires a formalization in terms of syntax and semantics, which can be defined in a dedicated "AIV/AIT add-on" to be implemented in Capella.

Source report: `review-report-1073`. Page 10.

## Systems engineering and assurance modeling (SEAM): a web-based solution for integrated mission assurance

> Abstract. We present an overview of the Systems Engineering and Assurance Modeling (SEAM) platform, a web-browser-based tool which is designed to help engineers evaluate the radiation vulnerabilities and develop an assurance approach for electronic parts in space systems. The SEAM framework consists of three interconnected modeling tools, a SysML compatible system description tool, a Goal Structuring Notation (GSN) visual argument tool, and Bayesian Net and Fault Tree extraction and export tools. The SysML and GSN sections also have a coverage check application that ensures that every radiation fault identified on the SysML side is also addressed in the assurance case in GSN. The SEAM platform works on space systems of any degree of radiation hardness but is especially helpful for assessing radiation performance in systems with commercial-off-the-shelf (COTS) electronic components.

Source report: `citation-report-1752`. Page 1.

> A simplified GSN assurance case for the generalized embedded system example is shown in Fig. 7. In this figure, The GSN nodes within red boxes come directly from the NASA R&M Hierarchy and were used as starting points for development of the more specific assurance case being made here. In this incomplete GSN assurance case, the argument for Goal 2.2 has been completed while the other subgoals are still in development. Goal 2.2 applies to the Sensor Subsystem, and requires that the subsystem be tolerant to faults, failures, and other anomalous internal and external events. The strategy for meeting this goal, from the NASA R&M Hierarchy, is to prevent faults and failures or to provide mitigation for the faults and failures. Two subgoals were identified to meet this strategy, both related to the known radiation effects possible in the sensor. The solutions (or evidence to support) Goal 2.2.1 and 2.2.2, total ionizing dose (TID) degradation and single event effects (SEE) errors, respectively, are found through radiation testing of the sensor. TID is found to not be a concern for the mission requirements in this project and SEEs are to be mitigated by the Microcontroller subsystem, which could involve another goal/strategy argument chain.

Source report: `citation-report-1752`. Page 7.

> - Function Coverage: This list presents a summary of the functional decomposition model. For each function, it lists the implementing component(s) in the system model. Functions that do not have a corresponding implementation component in the system are appropriately flagged. This informs the user that either the functionality is not implemented in the system or the relationships have not been captured in the functional decomposition model. Fig. 12 shows the function coverage table generated as part of coverage check for the function decomposition model (Fig. 5) and the system (Fig. 2)

Source report: `citation-report-1752`. Page 13.

> - GSN Coverage: This table presents the coverage of the assurance argument in the GSN model relative to the components in the system. The table lists the GSN goals and solutions for the assurance argument related to each component instance in the system. It further identifies the specific GSN goals related to each of the underlying component faults, each functional degradation effect that the fault propagates to and each mitigation strategy associated with the fault propagation.

Source report: `citation-report-1752`. Page 14.

## A CubeSat-payload radiation-reliability assurance case using goal structuring notation

> Radiation Hardness Assurance (RHA) is the methodology for evaluating and assuring the radiation tolerance of electronic components to the space radiation environment [1], [2]. RHA activities assure that the designed system and its components will function over the lifetime of the mission. These activities include defining system requirements, defining the radiation environment, selecting and testing COTS, and designing for radiation-tolerance against mission goals. The activities focus on ensuring that the system can
>
> carry out the mission, its electronics have non-destructive failure modes, and system mitigation or circumvention strategies handle radiation-induced errors and non-destructive radiation event failures. The result is system reliability for a mission in a particular space radiation environment.

Source report: `citation-report-0687`. Page 1.

> The argument for the radiation reliability of the CubeSat experiment is supported by TID screening of COTS components, system-level SEL detection, isolation, and recovery, and SEFI recovery in the microcontroller. These mitigation strategies were chosen because of the radiation environment expected for the mission and the expected rate of single-event effects (SEEs) compared to the required uptime to complete the science mission objectives of the experiment. The result of this paper is a graphical assurance case specifically for the radiation reliability of a spacecraft system that uses COTS instead of rad-hard parts.

Source report: `citation-report-0687`. Page 2.

> The stakeholders reviewing the assurance case would then decide if that test result is evidence enough to support the goal of "FRAM passes proton SEL mission requirement." When documenting the reasoning between goals and child-goals, strategy elements are used. An example strategy is "Isolate and contain faults" which provides the reasoning step between the parent goal "Physical and functional pathways for fault propagation or combination are limited" and the child goal "Latch-up faults are isolated and contained close to the fault source." Goals, strategies, and solutions make up the base of the GSN structure and are connected with solid arrows and indicate inferential and evidential relationships. In summary, goals and strategies are alternately refined until the goal is specific enough to be supported by a solution element which links to the results of parts tests, system tests, simulations and analysis, literature review, etc.

Source report: `citation-report-0687`. Page 3.

> The last way is through a justification element. Justifications explain why a goal or strategy is acceptable. For example, the justification "Heavy-ion SEL tests were not performed because the heavy-ion environment does not significantly contribute to the radiation environment" is an explanation for the goal "System and its elements are designed to withstand nominal and extreme load and stresses related to radiation for the life of the mission." A reviewer might ask why heavy-ion SEL testing was not completed as it is a part of standard RHA activities and this explicitly states the reasoning for that decision. Assumptions, justifications, and context are connected to goal, strategies, and solutions with dotted arrows to indicate contextual relationships. In summary, assumptions, justifications, and context about the argument are linked to appropriate strategies or goals to further clarify the assurance case. In Figure 2, all of the elements of GSN are presented.

Source report: `citation-report-0687`. Page 4.

## A Scalable Systems Architecture for CubeSat Test and Evaluation to Improve Mission Success

> The first step in creating a scalable systems architecture was to capture and define the system requirements. The initial step was to review the requirements from a discipline-centric viewpoint. Each test was categorized as one of five top level domains, categorized by the engineering discipline that performed the test. The chart of requirements is shown in Figure 3 below.

Source report: `review-report-0240`. Page 3.

> Each of the three block definition diagrams was built as a test-centric viewpoint within the operational viewpoint of the overall system. Each of the three block definition diagrams reflects a different workload on the actors of the system as well as results in a different probability of potential mission success. The system can be scaled up by shifting more testing to the full flight model testing, if test resources (people, lab space, and financial) are adequate or scaled down by shifting more testing to the prototype testing if test resources are more limited. Some teams, whose CubeSats may never be intended to launch due to tight budgets, may shift 100% of the testing to the prototype version. While this would be a poor choice for a CubeSat intended for launch, this may be a viable choice for a team whose CubeSat will remain in the lab until retirement.

Source report: `review-report-0240`. Page 9.

## ADVANCING DIGITAL TWIN IMPLEMENTATION FOR CUBESATS: INTEGRATING THEORETICAL INSIGHTS WITH REAL-WORLD APPLICATIONS

> The scenario of the CubeSat Digital Twin implementation of the EventSat has been oriented on the possible known parameters for operation and the early stage of development. Therefore, some assumptions and considerations have been taken. This assumption mainly considered the amounts of events logged, the computation algorithms operated on the NVIDIA Jetson Orin Nano, and the orbit characteristics. For the orbital considerations, a simplified sun-synchronous orbit has been taken as a baseline for the simulation: 90 minutes of orbit time, 60 minutes in the sunlight, and 30 minutes of eclipse. This has been validated with a separate computation in orbit mechanics software. The communication window has been selected in a way that it communicates while operating in the sun to reduce the risk of a fallback in the safe mode. It has been decided to initiate the simulation for one orbit to observe the correct functionality of the simulation before the hardware connection is checked automatically and then operate the simulation for 170 orbits, as a trade-off between time to wait until the simulation finishes and giving the behavior of the component enough time to see a trend in operation.

Source report: `review-report-0494`. Page 10.

## Development of A Standard Model Based System Architecture for Cubesat Missions

> Applying the block definition diagrams, failure modes of a satellite are created by displaying the failure constraints causing a mission failure. As shown in Figure 28, each failure mode is then correlated to a respective activity block, linked to one of the activity diagrams discussed earlier. These failure modes violate the connected activity thus causing either partial or total mission failure state for the CubeSat. The failure state is then connected to Figure 25 CubeSTEP Operational States Powered On block's failure detection block.

Source report: `review-report-1010`. Page 45.

> The creation of the constraints above allows for the user to generate parametric diagrams for each of the failures to conduct the analyses necessary for determining the system reliability. Using additional features of SysML Parametric diagrams enables the automatic generation of Failure Mode and Effects Analysis (FMEA) tables as needed. The failure rate values determined through FMEA are then used in the failure analyses used to determine the most at-risk components and where to focus efforts on risk reduction.

Source report: `review-report-1010`. Page 46.

> Each fault tree must then be run through a cut set minimization, where a cut set is a set of occurrences that would cause a system failure. The minimum cut set removes the redundant cuts from the fault tree reducing the necessary work for reliability analysis while keeping its integrity. As such Figure 33 and Table 3 below show the determination of the minimum cut set for a given fault tree diagram.

Source report: `review-report-1010`. Page 48.

## Digital Engineering for Cubesats with Semantic Web Technologies

> The Test Engineer also defines a series of verification activities to be performed. These are modeled as activities in GENESYS. GENESYS is a MBSE tool designed to support the entire lifecycle of complex systems using the Systems Definition Language (SDL) [39]. The Test Engineer defines the overall verification strategy in GENESYS. The verification strategy as modeled in GENESYS is presented in Fig. 3. Currently, no built-in integration capability exists between Violet and GENESYS (although this is under development), and so we have developed a Python script that will parse the GENESYS activity model and produce an equivalent SysML v2 model. Note that 'VA1.1_Mass_analysis' and 'VA1.2_Deorbit_analysis' are used to verify 'MR1 - Orbital Decay'. The other verification activities would be used to verify the system requirements. These have been modeled in Jama but are not displayed in this paper.

Source report: `review-report-0301`. Page 5.

> The value in integrating information from Jama, GENESYS, and multiple SysON models can be further demonstrated when considering the traceability from verification activities through architecture models to the requirements. This information is displayed on the 'Requirements' tab of the dashboard, which is shown in Fig. 7. In this case, we have only focused on modeling the information required to verify 'MR1-Deorbit'. This mission requirement is verified by the verification activity 'VA1.2_Deorbit_analysis'. This analysis uses the mass of the cubesat in its calculations. This value is produced by 'VA1.1_Mass_analysis'. The 'Requirements' tab displays a table of all mission requirements alongside the corresponding verification activities and any available results. Such traceability is essential for ensuring compliance with mission objectives and for identifying potential gaps in the verification process.

Source report: `review-report-0301`. Page 8.

## Early validation of system requirements and design through correctness-by-construction

> If requirements (and derived properties) are simultaneously satisfied by the design model, then early assurance of consistency and correctness is provided (we do not cope though with inconsistencies between requirements at the specification level, which are treated e.g. in [47] and other works). The design model is incrementally built using correct-by-construction model transformations, which integrate reusable BIP architectures [5]. The integrated architectures provably discharge the specified properties through coordinating the model components. This is an automated step aiming to preserve the previously established properties. Only the properties that cannot be enforced by design need to be verified by model checking.

Source report: `review-report-1315`. Page 8.

> Step 6 Model checking: Properties that could not be enforced using existing architecture styles are verified on the final design model. If these properties are satisfied, then so is the whole set of requirements; otherwise, the design model should be refined or certain unsatisfied requirements have to be revised.

Source report: `review-report-1315`. Page 9.

> The key advantage of our architecture-based approach is that the burden of verification is shifted from the final design to architectures, which are considerably smaller in size and can be reused. In particular, we managed to enforce 47 out of 57 derived properties using our simple architecture styles. The remaining 10 derived properties were verified by inspection and 4 fairness assumptions were left for verification using the nuXmv model checker.

Source report: `review-report-1315`. Page 23.

## Modelling a CubeSatbased space mission and its operation

> The fundamental for any V&V processes is the system requirements specification. Most CubeSat-based projects have given less importance to the mission requirements definition and analysis phase because the use of the CubeSat standard is considered the architectural solution to the satellite platform. Although CubeSat provides COTS (Commercial Off TheShelf) subsystems with standardized interfaces and communication protocols, they are not enough to define the mission goals. The mission requirements and constraints are the major elements to drive the use of the COTS in right way, as result of Phase 0 analysis, i.e. mission conception analysis and feasibility.

Source report: `citation-report-3312`. Page 1.

> Focusing on the concept of operation aspects of a Cubesatbased mission, we present an experience on the use of a modelling tool developed at INPE, by space system engineering student. The tool aids the mission design analysis allowing anticipate requirements verification by means of operational scenarios validation. The purpose is to increase confidence in the mission requirements, reducing the cost of design rework in terms of time and resources consuming.

Source report: `citation-report-3312`. Page 2.

> The ATOM SysVAP has demonstrated, so far, its capability to, not only, model the operational phase of a space system, but also help the conception, development, and V&V (validation of specific FSM paths). With the use of Lua as scripting language, the ATOM exploits its usage being capable of generating telemetry files, payload data, mathematical models, evaluating behaviour in real time (debug) and, modeling faults (using fault/error/failure behaviours and scenarios). This capability enables the FSM to be more reduced and the models simpler.

Source report: `citation-report-3312`. Page 4.

## Reusable and Reliable Flight- Control Software for a Fail-Safe and Cost-Efficient Cubesat Mission: Design and Implementation

> Fault detection, isolation and recovery (FDIR) analysis main goals are to detect anomalies, isolate the problem, and recover spacecraft systems and capabilities. FDIR analysis is a highly iterative process (Figure 4). First, the mission success criteria, autonomy levels and constraints are defined. Then, the system functional indentures are identified, and FDIR boundaries are defined in respect of the project; this is to prevent unnecessary analysis expansion and a waste of effort and time. Subsequently, the FDIR concepts and strategy are described. After that, a list of system and subsystem failure modes is developed using systematic reliability analysis tools [5]. Finally, the mission FDIR procedures are defined, and candidate contingency scenarios are proposed to perform verification and validation tests. The latter falls outside the scope of this paper, and it shall be the subject of further works.

Source report: `citation-report-3814`. Page 8.

> In the literature [16,19], there are different types of FMEA analyses, namely functional (top-down), piece-part (bottom-up) and process. The piece-part approach (bottom-up) approach is hardware oriented. It is used when a system concept has been decided, and hardware items can be uniquely identified from the schematics and design data. This approach yields comprehensive results because all components at the lowest level of the system are considered, thus all potential failures are identified. Although it is time-consuming, the piece-part approach is a better fit when every component of a system must be reviewed. However, it will become inefficient when analyzing complex systems requiring progressive analysis or when analyzing incomplete systems during early design phases. It is also inadequate to provide risk-related information for a focused problem within the predefined boundaries of an existing system. Unlike the piece-part approach, the functional FMEA approach is function oriented. Thus, it lends itself extremely well to this type of problem. Functional FMEA is also a better fit to directly address only the most important contributors to major potential problems with significant effects on the system rather than every failure of each component. Intrinsically, functional FMEA results may not be comprehensive; not all failure events in a system may be covered, only major ones. It is also unable to identify the complex failure scenarios involving a combination of multiple failure modes within a subsystem. This is the reason why in practice functional FMEA is commonly used along with FTA or RBDs. A brief description of RBD analysis is provided in the next section.

Source report: `citation-report-3814`. Page 9.

> In summary, we selected functional FMECA in conjunction with RBD analysis for Masat-1 mission risk assessment and management mainly because the scope of our study is limited to the subsystem level, given the aforementioned design constraints in Section 4.1. We aim to use functional FMECA in an iterative and timely manner to increase its effectiveness. A quantitative analysis was not possible because of the absence of quantitative data about specific failure rates and the probability of occurrence for COTS. As Stesina et al. reported in [21], "anomaly analysis is complicated by the absence of a statistic database for Commercial Off-the-Shelf (COTS) items limiting the reliability analysis to a qualitative exercise without effective quantitative estimations". Instead, a qualitative approach of functional FMECA was used as per ECSS-Q-ST-30-02-C standard suggestion. Therefore, the scores of each failure mode were assigned based on the statistical studies and results of similar FMECA studies reported in previous
>
> Cubesat missions, such as Lumio [8], Swampsat [22] and e-st@r missions. Using functional FMECA, we could identify all major failure modes of each subsystem in Masat-1 and assess the resulting consequences. As a result, adequate FDIR design provisions and testing plans were defined. In our case, this step was essential to devise a reliable solution for Masat-1 flight-control software, and hence assure the Masat-1 mission reliability. According to the ECSS-Q-ST-30-02-C standard, the sequence of functional FMECA activities is summarized as follows [7,23]:

Source report: `citation-report-3814`. Pages 9–10.

> Step2 Fill out the FMECA worksheet which contains the following elements: all potential failure modes for each functional block of the system, all potential causes of the failure mode (optional), the worst potential consequences locally and on other subsystems, failure detection methods (optional), and methods to prevent or recover from each failure mode. It also assesses the failure criticality number (CN) given the worst potential severity level of the failure (SN) and its probability of occurrence (PN). The severity and probability categories were customized according to Masat-1 requirements and constraints. They are listed in Table 2a,b, respectively. The CN is calculated as the product of the ranking assigned to each factor: $ \mathbf{C N}=\mathbf{S N} \times\mathbf{P N}. $ It is worth mentioning that combinations of failures are not considered, and each single item failure is assumed to be the only failure in the system [5];
>
> Step 3 Define the overall mission critical items list (CIL): an item is critical if its failure mode severity is classified as catastrophic, or if a failure mode CN is greater or equal to 6 in conformance with the criticality matrix (Table 3);
>
> Step 4 Define corrective/preventive solutions (such as design provisions or operator actions) necessary to eliminate the failure or to mitigate/control the risk.

Source report: `citation-report-3814`. Page 10.

> 6. Throughout software validation and verification (V&V) testing: this is based on white box and integration testing. White box unitary testing will be applied to each command, since they are called independently as APIs or services provided to the ground segment. Integration tests are mini-applications running operation scenarios, such as switching the spacecraft through various states by generating events, running a command with different parameters, simulating failures scenarios, etc. This is to verify that the flight software is running in a deterministic manner and finishing tasks within specified deadlines. If an abnormal output or behavior in the software is identified, it will be fixed, and tests are repeated again. When integrated in its end environment, the overall reliability of the flight-control software is assessed using functional validation testing all within SIL and HIL simulations on a virtual model of each subsystem. Hardware-software interaction analysis (HSIA) will be used to analyze flight software reactions to hardware failures. It is worth mentioning that we also intend to use this V&V testing campaign to identify all failure modes that were unaccounted for during FMECA analysis. In such cases, the FMECA will be updated, the effects of new failure modes induced by these modifications will be evaluated, and adequate preventive/corrective functions will be implemented.

Source report: `citation-report-3814`. Page 26.

## Toward requirements engineering of cyber-physical systems: Modeling CubeSat

> To meet the first objective, sixteen quality attribute scenarios were generated to specify key quality attributes
>
> associated with the design of a CubeSat. The CubeSat's main design considerations are availability, security, performance and usability. Availability requires that the system to be up and running. The integrate-ability requirement refers to the degree by which system elements can be easily combined and/or interfaced with other elements such as the data link, etc. Security refers to the degree at which system assets are protected. Performance refers to speed by which the system reacts to the end-user, performs its operations, or the extent to which it utilizes the resources in efficient way.

Source report: `review-report-1476`. Pages 4–5.

> The first step in this process is to capture system requirements for the CubeSat using quality attributed scenarios [17] and UML use case scenarios. To this end, two templates were used to specify both functional and nonfunctional requirements. Extended version of use-case scenarios that incorporated references to non-functional or functional requirements were used to establish proper treatability among requirements. Quality attribute scenarios and templates developed by Bass, et al. at Carnegie Mellon University [17] were used to document the nonfunctional requirements of the CubeSat.

Source report: `review-report-1476`. Page 5.

> Future work will rank and prioritize scenarios generated during this work to perform the trade-off analysis procedure outlined in ATAM to select the optimal architecture that best meet the CubeSat's NFRs. The set of scenarios will be prioritized based on their difficulty (cost) to achieve and their relative importance to other system-wide requirements. For instance, if it is decided that the performance (e.g., transaction throughput scenario) is given priority over security (e.g., data integrity scenario), then the set of scenarios would be reprioritized. Using prioritized scenarios, the software architecture of the CubeSat will be selected. The selected architectureal style (or domain specific architecture) will be specified using the Architecture Analysis and Design Language (AADL) in order to describe and analyze the non-functionalities of the CubeSat. To this end, we plan to divert the output generated by the AADL parser to an appropriate analysis tool supported by OSATE to evaluate the results.

Source report: `review-report-1476`. Page 10.

## A reliability engineering approach for managing risks in CubeSats

> For each considered item—and its interfaces—it is necessary to identify the potential failure modes that can affect system performance, also considering their effects on systems. This step relies on the capability of the analysts to explore potential combinations of failure modes. Naturally, this capability does not reside in a single individual, thus implying the need to involve both fresh-eyes and experienced researchers in order to gather meaningful insights from collective collaborative knowledge and experiences. This step needs both teamwork and timely information exchange in order to ensure that the knowledge about the system is embedded in the reliability analyses. In case of systems made up of many different parts, it is necessary to develop a consistent coding system that uniquely identifies parts and related failures, in order to increase the comprehensibility of the analyses.

Source report: `citation-report-1436`. Page 4.

> This step allows for a structured systematic analysis of failure modes, based on three semi-quantitative indexes. In this sense, the proposed approach starts from ESA (European Space Agency) guideline (ECSS-Q-ST-30-02C), which takes into account severity, ranging from 1 (negligible damage) to 4 (catastrophic damage), and occurrence, ranging from 1 (probable, probability greater than 1E-1) to 4 (extremely remote, probability minor than 1E-5). These two terms are multiplied to obtain the Criticality Number (CN), which is used to filter the failures modes: the critical failure modes are the ones that are catastrophic (severity score equals to 4), and the ones whose CN is greater or equal to 6. On the contrary, the US standards for FMECA (SAE ARP5580) at a component level calculates an RPN (Risk Priority Number) defined as the product of severity (in a 1-10 range), occurrence (in a 1-10 range) and likelihood of mitigation—if the design can be revised, or detectability—if the design cannot be revised (both in a 1-10 range). Note that similar concepts are present in ESA guidelines for FMECA at process level. Therefore, the approach used in this study, extends ESA guidelines for functional FMECA, following the influence of the US satellite standard for FMECA—also documented in a recent FMECA space-based application [19]—in order to produce a three-dimensional risk index. This latter will include three indicators, each one rated in a 1-5 scale. The odd number of slots allows assigning intermediate values to variables, in order to support the analysts in avoiding overestimation or underestimation of factors, as emerged from initial categorizations performed in a real case scenario. The indexes are occurrence, severity, and detectability.

Source report: `citation-report-1436`. Page 5.

> Following the assessment conducted in Step 3, it is now possible to calculate an aggregated index, which takes into account occurrence, severity and detectability. This index, i.e., RPN (Risk Priority Number) aims at prioritizing the need for updated design requirements necessary to reduce risks and increase system's reliability. Depending on the values, the failure modes can be thus interpreted as negligible (low RPN), to be investigated (moderate RPN), or to be necessary managed (high RPN). The RPN is calculated as the product of the indexes and the relative thresholds are defined in Table 8.

Source report: `citation-report-1436`. Page 9.

> The risk classification conducted at Step 4 defines the risk acceptance levels for the missions and has to be intended as a guideline to identify requirements and initiate discussions for design revisions. Alternatively, it is necessary to provide document analysis for those failures that cannot be corrected at the current stage of the satellite development. Note that the FMECA has to be continuously revised, following the choices made during the design phase, using it as a dynamic decision support tool.

Source report: `citation-report-1436`. Page 9.
