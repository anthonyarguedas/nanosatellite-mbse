---
source: null
title: "citation-candidate-1095"
page_count: 7
converted_at: "2026-09-08T15:06:26Z"
---

<!-- PDF_PAGE: 1 -->





PAPER • OPEN ACCESS

<div align="center">

# Application and development of MBSE in aerospace

</div>

To cite this article: Wang Wenyue et al 2022 J. Phys.: Conf. Ser. 2235 012021

View the article online for updates and enhancements.

## You may also like

- Mission analysis and design of launch vehicle based on MBSE Longxi Zhang, Xiang Guo, Zhengfei Ren et al.

- Demand Analysis of Wind Turbine System Based on MBSE Ben Jing, Wang Hao and Xu Yang

- Artificial versus natural atoms: the uncanny capability of the many-body Schrödinger equation to produce emergent behavior Constantine Yannouleas

<!-- PDF_PAGE: 2 -->

<div align="center">

# Application and development of MBSE in aerospace

</div>

Wang Wenyue*, Hou Junjie, Mao Yinxuan, Jinjie, Lu Zhiang

China Aerospace Academy of Systems Science and Engineering, Beijing, China

Corresponding author's e-mail: 13821692051@163.com

Abstract. MBSE (Model-Based Systems Engineering), as the representation of digital technology, has achieved effective management of system complexity through model-centric means, and a state of coordination and matching with modern complex engineering systems. On the basis of introducing the background of MBSE and the overview of MBSE practice in the aerospace field, two typical application cases of MBSE in the domestic and foreign were analyzed. In order to provide reference for the application of MBSE in the aerospace field, suggestions and conclusions on the development of MBSE application in China were put forward: the integration of traditional development process and MBSE method, the consistency understanding of system model, and the integration ability of system model and domain model.

## 1. Introdution

With the rise of scientific and technological revolution and industrial transformation, the technical of complex systems developing and its development environment are undergoing significant changes, and the complexity and performance requirements of complex engineering systems are increasing day by day [1]. In recent years, driven by the new aerospace products, the development mode is faced with such challenges as highly complex system, short lifecycle, and "one success" of system design. However, the potential problems existing in the traditional development mode and management system with documents as the main information carrier and physical verification as the main verification mode are becoming increasingly prominent. In 2007, the International Council on Systems Engineering (INCOSE) in the "Systems Engineering Vision 2020" formally put forward the concept of MBSE [2]: "Model-based systems engineering (MBSE) is the formalized application of modeling to support system requirements, design, analysis, verification and validation activities beginning in the conceptual design phase and continuing throughout development and later life cycle phases."

Driven by the requirements of aerospace research and systems engineering theory [3], foreign defense and aerospace research institutions, such as NASA, ESA, Dassault, Lockheed Martin, Airbus, Boeing and etc., began to explore and apply MBSE to project pre-research as early as more than a decade ago. At present, MBSE standard and integrated digital technology are actively studied and carried out in the whole life cycle research and development process [4,5], gradually realize the document as the center to model, full life cycle extended application and multi-disciplinary integrated simulation and other advanced development mode. In China, China Academy of Space Technology and Shanghai Academy of Spaceflight Technology actively applied MBSE method to space exploration, manned spacecraft and other missions [6,7], which effectively improved design efficiency and personnel communication and cooperation. From the current MBSE application practice in the field of aerospace, along with the INCOSE, NASA, Boeing and other authoritative system engineering practitioners of MBSE development constantly advancing and deepening, MBSE will effectively





<!-- PDF_PAGE: 3 -->

integrate field model for the center with system model and materialized expression system formalization and standardization of space engineering process in whole life cycle of activity.

Meanwhile, with the integration of digital twin and digital thread, the development mode of MBSE will tend to be digital and intelligent. Wang [8] proposed the overall model and application framework of spacecraft system engineering based on digital twin, which can effectively realize the dynamic realtime interaction, integration and collaboration between the information world and the physical world in the whole life cycle of spacecraft development, and the simulation integration test process between different systems. In 2019, Madni [9] integrated digital twin system simulation and Internet of Things (IoT) to support MBSE, and suggested that digital twin technology be part of MBSE methodology and practice to improve product life cycle performance and real-time update of status data; In January 2021, a platform closed-loop validation test was conducted on MBSE based on digital twin [10] to explore system behavior under operational scenarios and conditions such as modeling, simulation, verification and validation to discover new patterns and trends in MBSE development.

## 2. Typical cases of MBSE application in aerospace field

MBSE application and development focuses on modeling for aerospace systems engineering process. Through the integration of traditional development process and MBSE method, formal description of system modeling language and integrated application of modeling tools, the development process and key elements can be modeled and linked organically. Thus, a multi-view system model is provided for system engineers' collaboration, and the system complexity can be effectively managed. The following are the description and analysis of applications of MBSE in the aerospace field:

## 2.1. Lifecycle extension of MBSE in JPL

As practitioner of MBSE, NASA Jet Propulsion Laboratory (JPL) uses MBSE at various stages of the lifecycle through more than 20 projects. It is also involved in requirement management, architecture design, task planning, reliability analysis, risk management, concurrent engineering and so on.

Taking Mars2020 as a typical case, the function of MBSE in the application practice is introduced. On February 19, 2021, Mars rover Perseverance successfully landed and embarked on its journey to Mars. As the most complex Mars rover to date, the success of its system design could not have been achieved without advancing MBSE technology. At the initial stage of Mars rover design, based on the experience of Curiosity rover, the research team summarized the challenges from the perspective of SE, including technical baseline by "boxology", trades/concurrent engineering, information siols, SE product alignment, personnel/artifact discontinuity, and SE product relevance [11]. Based on these, the Mars2020 research team chose to use MBSE to build an authoritative information source to address the challenges of systems engineering from the perspective of system model[12].

2. 1.1. Converting design document into SysML model. All of Curiosity's design data is stored in documentation, and there is a lack of standards for expressing knowledge. Mars2020, therefore, on the basis of the design data's documents, the model was carried out on the key elements to form a system design based on SysML model, and then to carry out the simulation verifying the correctness of the design data, project deliverables automatically generated, web-based model visualization, and to realize cross-team collaborative design and stakeholders regular inspection.

2. 1.2. Reuse of knowledge assets. Changes to the design team and scattered design data from the earlier Curiosity rover have made it difficult to reuse all information effectively. Therefore, at the beginning of the design, the system model was constructed to provide and maintain the authority of the information source, based on the standardization of language from the aspects of requirement, behavior, structure and parameters, and from the operation analysis model, test verification model, hardware and software model respective characteristic parameters to provide professional information, and the system model as the center for integration, to achieve the monitoring and management of model information, according to the need to generate and confirm the required information.

<!-- PDF_PAGE: 4 -->

2. 1.3. Model-based automatic generation of documents. Due to the complexity of Mars2020 system design, different design teams and fields often have inconsistent design information, that is, information silos. In the design of Perseverance rover, model integration is used to check the consistency, and cross-domain documents and reports are generated based on the integrated system model to ensure the consistency of document information.

2. 1.4. Automatic generation of review deliverables. In the traditional design mode, designers must stop the design work and concentrate on preparing all kinds of materials necessary for the key review node of the project, namely project deliverables. To effectively address this problem, Mars2020 automatically generates as many documents as possible for project delivery from the model during the MBSE-based rover design process to save designers the preparation time required for project review.

2. 1.5. Model based complex behavior analysis. It is a complex task to effectively coordinate the actions and roles of rover and ground controllers during the five hours of communication between Mars and Earth, and to analyze the information interaction and key decision points between different activities. Therefore, Mars2020 uses MBSE-related standard BPMN language to describe this activity in the design process, realizing the design analysis and integrity expression of complex activities.

2. 1.6. Customizing model information display. Selective presentation of design information is a necessary step in the process of design communication. However, when the model complexity reaches a certain level, the typesetting function provided by SysML modeling tool itself cannot meet the requirements of information filtering and personalized presentation. Mars2020 project is based on the complete SysML model, with the help of data filtering and automatic typesetting functions provided by third-party tools to achieve automatic diagram creation to complete personalized presentation.

From the overall situation of application of MBSE, Mars2020 system modeling based on SysML extended framework provides multiple viewpoints of view of system model, and formalization and defined the model elements and the relationship between elements, and by building authoritative sources, implementation model based document automatic generation techniques, the model-based knowledge reuse system, personalized display and other requirements are formed, and the system information integrity and inconsistency verification ability is enhanced.

## 2.2. Application practice of MBSE for manned spacecraft

Manned spacecraft has the characteristics of high technical difficulty, single piece and small batch production, and high reliability requirements. Driven by new manned spacecraft task, China Academy of Space Technology, chose MBSE method as its application practice recently, in order to solve the problem of low informatization and digitization degree in the development of manned spacecraft. From the perspective of the full lifecycle model of manned spacecraft, combined with the development requirements of MBSE throughout the full lifecycle, the Manned Space Department takes the model as the carrier of development data and integrates all aspects of product development through requirement model, function model, product model, engineering model, manufacturing model and implementation model. And form model-based technology state control of the whole lifecycle from the aspects of system design, product design and closed-loop verification of actual products [7].

2. 2.1. Requirement management and system design (Requirement model). Taking a certain manned spacecraft as an example, the overall requirement model and the relationship between requirement elements is established to realize requirement coverage, requirement traceability, requirement verification and other analysis work. Meanwhile, based on MagicDraw, M-Design, and SysML as the modeling language, through the use case diagram, activity diagram, state machine diagram to refine the manned spacecraft requirements system, and based on the requirement model to achieve more than 5000 requirements items and key functional indicators at all levels of 100% traceability.

<!-- PDF_PAGE: 5 -->

2. 2.2. Multidisciplinary system simulation (Function model). Function models were established by using Modelica, and the model library was accumulated. Co-simulation was carried out by using FMI (Functional Mock-up Interface) interface to clarify model principles, model parameters, and model input and output interfaces. Through the comprehensive integration of functional simulation models of various disciplines, the correctness of the overall scheme design of the model is verified.

2. 2.3. Full 3D collaborative design (Product model). With the requirement model and function model as normative guidance and constraints, and the simulation of structural, thermal and control parameters as reliability basis, all single machine models were integrated into the system model architecture and multi-professional collaborative design was carried out, and the integrated manufacturing model was downward connected to achieve full 3D collaborative design.

2. 2.4. Professional simulation (Engineering model). Engineering simulations have been carried out to meet the simulation requirements of various special schemes of manned spacecraft, and the correctness of each special design scheme has been verified.

2. 2.5. Digital manufacturing final assembly (Manufacturing model). Data source unification is realized through digital model information integration using manufacturing model.

2. 2.6. Product electronic packet management (Implementation model). Through the construction of product electronic data package management system, the unified collection and acceptance process management of single product electronic data package is realized based on model matching system.

According to the case of MBSE for manned spacecraft in China, it is necessary to put forward a specific model based procedure specification for manned spacecraft development based on MBSE fusion. On the one hand, manned spacecraft must be from the perspective of actual engineering tasks, the requirements of the SoS, system, subsystem, or even component must be established. The development methods covered by different missions may differ, so MBSE practice should be implemented based on the development requirements. On the other hand, different designers may have deviations in their understanding of the manned spacecraft system model, so necessary design specifications should be established on the basis of unified data sources for consistent understanding.

## 3. Suggestions on the development of MBSE application in domestic aerospace field

Based on the above two typical cases at home and abroad, suggestions for the development of MBSE application practice in the domestic aerospace field are proposed:

## 3.1. Accelerate the integration of traditional development process and MBSE method

At present, there is no consensus on the application of MBSE in aerospace field [13]. The main reason is that different research institutions have different approaches to spacecraft model development. Therefore, it is difficult to integrate development tasks with MBSE processes and work effectively.

MBSE practitioners often adopt SysML based modeling to integrate static descriptive models from requirements, behavior, structure and parameters, and realize information sharing of dynamic analysis models such as Modelica, STK, Simulink based on FMI data interface. The key problem that complex system is difficult to effectively communicate and coordinate between "information domain" and "physical domain" design is solved by associating the hierarchical models with the view of "SoS system-subsystem-component" and increasing the interaction of system elements. Song [14] of China Academy of Space Technology established a multidisciplinary integration model of manned spacecraft for system-level scheme simulation based on Modelica, and realized the forward drive and reverse feedback mechanism of model interaction, as well as the collaborative design of system architecture model and models in various professional fields.

<!-- PDF_PAGE: 6 -->

## 3.2. Improve designers' understanding of the consistency of MBSE's system models

Based on the specific spacecraft, engineers often have a clear division of tasks and perform their duties respectively. On the basis of the integration of the traditional development process and MBSE, system model needs to effectively avoid the existence of differences in the understanding of designers.

MBSE generally based on SysML, modeling methodology such as MagicGrid/Arcadia, modeling tools such as MagicDraw/EA, etc., to describe the system from the perspective of requirements, behavior, structure, and parameters aspect. On requirement model, function model, architecture model, such model building effectively including requirement, function information about the entities and relationships, through the entity of decomposition to the level of the system model is established to manage the system complexity, and by way of modeling feedback iteration and fine system model [15]. On this basis, the established system model can accurately and uniformly describe the system from multiple perspectives, standardize the model development, and support the consistent understanding of complex system, and realize the closed-loop verification process of system design in the early stage.

## 3.3. Enhance the integration capability of MBSE's system model and domain model

The construction of system models requires a certain degree of data integration and standardization ability, by integrating analysis model, validation model, hardware/software model characteristic information, to create an authoritative information source for MBSE practitioners to share.

For the integrated design of system model and domain model, NASA JPL proposed Open Source Model-based Engineering Environment (OpenMBEE) in 2015. The OpenMBEE integrates Model Development Kit (MDK), Model Management System (MMS) and View Editor (VE) to realize unified storage of model data, version management, process management, Web-based document generation, model viewing, and RESTful WebService provide interfaces for tool integration. MMS is the only data source for the entire OpenMBEE environment to ensure data consistency and traceability and store data from MDK integration. MDK is used for integration of modeling tools with various analysis/design/simulation tools and synchronization with MMS through dynamic acquisition of model data to verify the performance of built system components. VE is used to provide web side model synchronization, view, document generation and other functions [16].

Based on OpenMBEE, JPL put forward the concept of OpenCAE (Open Computer Adided Engineering) in 2017 [17], which expanded OpenMBEE from system engineering to electrical, mechanical and software engineering and formed the best practice. The whole OpenCAE environment takes the intermediate data management as the core, realizes the data interaction with each different client modeling tool through webservice and finally realizes the unique data source management and cross-department data collaboration.

## 4. Summary and conclusion

From the perspective of JPL MBSE lifecycle application and manned spacecraft MBSE application, the current application of MBSE is still in the stage of standardization and modeling of documented information. In recent, the integration of digital technology has made it possible to extend MBSE to the full lifecycle, and digital twin is expected to become the core capability of MBSE, driving MBSE across the entire system lifecycle through digital thread. Specifically, within MBSE rules, the digital twin constructed by integrating information from the system model can be a single authoritative source of truth about the full lifecycle of the system. Meanwhile, the combination of digital connectivity provided by the digital thread and trusted data and knowledge provided by the digital twin accelerates the transformation of systems engineering processes used in MBSE, and enables real-time operation of physical entities through simulation verification control processes.

In the future, MBSE will be applied in aerospace field in the process of combining with digital twin, digital thread and other digital technologies. The system model will continue to interact with the physical world with the continuous integration of data, to build a digital twin throughout the product manufacturing, system test integration and operation. Meanwhile, the complexity, accuracy and real-

<!-- PDF_PAGE: 7 -->

time performance of the MBSE model are gradually improved with the evolution of the product lifecycle, leading MBSE to become more intelligent.

## References

[1] Martin T, Paul T. G. How to deal with the complexity of future cyber-physical systems?[J]. Designs, 2018, 2(4):40.

[2] Estefan J A. Survey of model-based systems engineering (MBSE) methodologies[J]. INCOSE MBSE Focus Group, 2007, 25(8):1-12.

[3] Gregory J, Berthoud L, Tryfonas T, et al. The long and winding road: MBSE adoption for functional avionics of spacecraft[J]. Journal of Systems and Software, 2020, 160:110453.

[4] Employing Model-Based Systems Engineering (MBSE) on a NASA Aeronautic Research Project: A Case Study[C]//2018 Aviation Technology, Integration, and Operations Conference. 2018: 3361.

[5] Best Practices for Model Based Systems Engineering in ESA Projects[C]//2018 AIAA SPACE and Astronautics Forum and Exposition. 2018: 5327.

[6] Yu G B. Application and trend of Model-Based Systems Engineering methods for deep space exploration mission[J]. Journal of Deep Space Exploration, 2021, 8(4):407-415.

[7] Zhang B N, Qi F R, Xing T, et al. Model based development method of manned spacecraft: Research and practice[J]. Acta Aeronautica ET Astronautica Sinica, 2020, 41(07):78-86.

[8] Wang J J, Xiang Y Q, He Z W. Models and implementation of digital twin based spacecraft system engineering[J]. Computer Integrated Manufacturing Systems, 2019, 25(6):1348-1360.

[9] Madni A M, Madni C C, Lucero S D. Leveraging digital twin technology in model-based systems engineering[J]. Systems, 2019, 7(1):7.

[10] Madni A M, Erwin D, Purohit S K, et al. Digital-Twin Enabled Experimentation Testbed for MBSE[C]//AIAA Scitech 2021 Forum. 2021:0201.

[11] Fosse E, Devereaux A, Harmon C, et al. Inheriting Curiosity: Leveraging MBSE to Build Mars2020[C]// AIAA SPACE 2015 Conference and Exposition. 2015.

[12] Elyse Fosse. From SysML to Mars: Mars2020's MBSE infusion. NAFEMS Model-Based Engineering 2019.

[13] Huldt T, Stenius I. State-of-practice survey of model-based systems engineering[J]. Systems Engineering, 2019, 22(2):134-145.

[14] Song Y, Xing T, Gong C Y. Multi-disciplinary integrated modeling and simulation of manned spacecraft based on modelica[J]. Manned Spaceflight, 2019, 25(03):397-402.

[15] Friedenthal S, Moore A, Steiner R. A practical guide to SysML: The systems modeling language[M]. Morgan Kaufmann, 2015.

[16] Kruse B, Blackburn M. Collaborating with OpenMBEE as an authoritative source of truth environment[J]. Procedia Computer Science, 2019, 153: 277-284.

[17] Eric W Brower. OpenCAE case study: Europa Lander concept[C]//2019Annual INCOSE International Workshop, Torrance, CA, USA. 2019.