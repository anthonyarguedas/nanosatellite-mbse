---
source: null
title: "review-candidate-1380"
page_count: 20
converted_at: "2026-09-06T20:19:11Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# A Structured, Model-Based System Engineering Methodology for Operations System Design

</div>

Duane L. Bindschadler, Robert R. Smith, Charlene P. Valerio, and Kathryn A. Schimmels

## 1 Introduction

This paper describes a methodology for the development of mission operations systems (MOS) that leverages model-based system engineering (MBSE) techniques to make the system engineering process more rigorous and repeatable and, ultimately, to lower the cost and risk associated with MOS development. It does so by casting many of the conventional system engineering products such as requirements, interface designs and specifications, and operations processes in a structured, reusable form. This paper begins (Sect. 2) by contrasting this structured methodology with more conventional practice of system engineering in the formulation and design phases. Section 3 reviews key architectural concepts that enable the approach and that arise from considering the development of mission operations systems from a product-line perspective, rather than as singular, unique creations in the context of a single flight project. Sections 4 and 5 describe (respectively) the structure of a multi-mission operations system (MMOS) model and the methods used to adapt the MMOS for use in a particular project context. Section 6 describes adoption by a number of diverse flight projects to date, challenges they face, and advantages that they have or expect to accrue as they continue development or begin flight operations.

<!-- PDF_PAGE: 2 -->

## 2 Background

Conventional system engineering practices [1, 2] emphasize a "best practices" approach focused on producing documentation of items such as requirements, scenarios, concepts of operations (or CONOPS), and interface specifications. These practices are firmly grounded in a document-based approach, and although those documents are developed and managed in electronic form, the fundamental structure remains informal, is described in narrative form, and is subject to reader's interpretation. The conventional approach has fundamental limitations [3], including:

- Difficulty (e.g., labor intensive) in assessing completeness, consistency, and relationships between system engineering products such as requirements, analyses, and design and test information.

- Difficulty in tracing and understanding the impacts of changes that affect multiple elements.

- Synchronization and consistency between higher- and lower-level requirements and designs are difficult to maintain.

- Documents frequently lag understanding of system requirements and design understanding.

- System engineering requirements and design information are laborious to maintain and have restricted reusability.

These limitations can and often do result in inefficiencies or quality issues that only become apparent during integration and testing (or later), where they can negatively impact cost, performance, or quality.

Many of these limitations can be addressed by model-based system engineering (MBSE) approaches. MBSE is a formalized application of modeling to support system requirements, design, analysis, verification, and validation activities beginning in the conceptual design phase and continuing throughout development and later life cycles [2]. Intended to address many of the limitations of conventional SE practice, it centers around a coherent model for a system and use of formal language (e.g., SysML). Significant advantages to this approach include:

- Ability to define and create reports that assess completeness, consistency, and relationships between system elements.

- Explicit traceability between elements, capturing engineer's insights and better enabling assessment of impacts due to change.

- Documents can be treated as views into the model and more easily kept consistent and up to date [4.].

- Reuse of system engineering products is both feasible and cost-effective.

Reuse is a common practice, usually intended to lower costs associated with nonrecurring engineering (NRE)the one-time costs associated with research, design, and testing of a new product. Less common is the reuse of design products themselves. The use of MBSE techniques significantly increases the potential for reuse, as will be described in Sects. 5 and 6.

<!-- PDF_PAGE: 3 -->

## 3 Architecture

A set of reusable, mission-adaptable design products for a mission operations system have been developed at JPL as part of the advanced multi-mission operations system (AMMOS). The design products themselves are referred to as the multi-mission operations system (MMOS) and are based on the Mission Services Architecture Framework (MSAF). The MSAF is a principled architecture framework based on ISO-42010 and consisting of the fundamental components, connections, and constraints needed to assemble a system design, along with a number of architectural patterns that are fundamental to mission operations. The framework includes detailed model representations needed to represent a system rigorously and explicitly. For example, specification of an interface component in the model includes the functional elements it connects, as well as the details of the information transfers that take place such as the information products, frequency of transfers, and any other constraints. The MMOS model is a specialized adaptation of the MSAF that addresses the particular needs and characteristics of a mission operations system (MOS). The components of the MMOS model are described fully in Sect. 4.

This approach yields some key differences with conventional SE approaches, many of which stem from the fact that the model (not documents) is the authoritative source of design information:

1. Documents are just one view (or perspective) into the system. Requirement documents or design descriptions or interface control documents (ICD) each represent one view of the system. Views may be individual diagrams, text, or tables, or collections thereof. One benefit of a rigorously defined model is that a view can be generated to meet the need based on any specific stakeholder's perspective. Tables, diagrams, text, or combinations thereof can be produced to meet the needs of the developing engineers, peer reviewers, review boards, implementers, or operators. A specification for such a view is called a viewpoint and can be reused as needed within or between projects.

2. Documents are produced from the model and updated as the model itself changes—in real time, according to schedule, or on demand. With appropriate configuration control and management, access to authoritative, up-to-date information is significantly improved.

3. The model itself can (and should) evolve throughout a project's life cycle. This is a significant advantage for a MOS, where design products such as processes and interface descriptions become operational processes, procedures, and operational interface agreements (OIAs) during flight operations and may themselves evolve over the course of long-duration missions.

These and other difference arise both from the MBSE methodology and from the MSAF's foundation in architectural principles. Principles are described more fully elsewhere [5]; here we briefly summarize two key principles:

- Close the Loop: For spaceflight missions, the notion of control must be built into a MOS from the ground up. The MSAF calls for closed-loop control, in

<!-- PDF_PAGE: 4 -->

which any command or directive prompts feedback from the element under control and in which the controlling element is responsible for generating explicit predictions. Only when feedback and prediction are meaningfully compared is the control loop considered closed. Within the MMOS, this principle is expressed by grouping functions into plan, execute, and analyze capabilities. This pattern is used by all elements of the MMOS. It represents and enforces the principle of closed-loop control.

- Use Authoritative Sources of Information: These must be explicitly identified and used by the system, particularly where decisions are made. This principle is as important during a mission's design phase as it is during system I&T or flight operations. For design information, the MMOS model is intended to be the authoritative source.

## 4 Description of the MMOS Model

The MMOS model provides representations of the mission operations system (MOS), focused on the components needed to design a MOS and the relationships between these components. Each component describes different aspects of the system design. Taken together, these components and their relationships describe a generic, adaptable mission operations system. The primary components of the MMOS are use cases, requirements, system components (and composition), interfaces, information products, functions, and processes. Relationships between these components and reporting and analysis capabilities are also discussed.

## 4.1 Uses Cases

The term use case (borrowed from software engineering) refers to how the mission needs to use the MOS. Use cases are mission scenarios that describe activities the MOS needs to be able to plan, execute, and/or analyze. Consider a use case for initial acquisition of the spacecraft. This scenario (Fig. 1) begins with separation of the flight vehicle from the launch vehicle and ends once the spacecraft is power positive and in communication with the MOS (the ground is receiving spacecraft data and can send commands). This use case scenario describes the significant steps that the MOS needs to perform to transition from the starting point to the end point.

Scenarios are meant to be kept simple. They describe what needs to happen, with much less concern as to how it will be implemented. The flow should be a sequential set of activities that need to be performed. If there are different outcomes or different paths through the scenario (e.g., decision points), a different scenario is defined. Scenarios are used to identify requirements.

<!-- PDF_PAGE: 5 -->


![figure_001.png](figure_001.png)



<div align="center">

Fig.1 The use case scenario for performing initial acquisition after launch is described in a mission operations scenario

</div>

## 4.2 Requirements

A MOS is designed and built to meet a set of requirements. Requirements are sometimes thought of consisting only of a title and a statement that begins "The MOS shall... In fact, MOS requirements have a number of other essential attributes that need to be captured. In the MMOS, a stereotype for MOS requirement is applied such that a requirement block has fields for capturing information such as rationale, verification method, and other attributes (such as a "key" or "driving"). Allocation of requirements to system components and requirement traceability are addressed through relationships and are discussed later.

## 4.3 System Components and Composition

To be understandable, a system and its components must have defined boundaries and scope. The ability to allocate responsibility for performing functions (e.g., via requirements) relies on clearly defined scope. Engineers responsible for both internal and external systems need to share a common understanding of system boundaries and interfaces. System composition is represented in views that describe the system in a particular context. In the MMOS, model components possess clearly defined boundaries and explicit relationships to other components. Views are created to show only necessary parts of that information so that they can more clearly and completely describe specific aspects of the system.

To provide a view of system composition, the MMOS includes three standard diagrams. The first (not shown) is a hierarchical depiction of a flight project. This view is used to identify elements of the project (including its MOS) and ownership or authority relationships between those elements.

The second composition diagram is the MMOS in context with external systems (Fig. 2). Systems are grouped by domains, which provide context. The MMOS is shown as a peer system to other systems within the ground domain, and ground domain is shown as a peer domain with other domains. Such a diagram clarifies whether a particular system is part of the MOS or is a distinct entity requiring an external interface.

<!-- PDF_PAGE: 6 -->


![figure_002.png](figure_002.png)



<div align="center">

Fig. 2 The system composition shows the MMOS as a system within the ground domain, having peer systems within the ground domain such as the tracking network. The flight system domain is shown as a peer to the ground domain

</div>

For example, a tracking network (e.g., DSN, ESTRACK) is a distinct entity that predates any given flight project and its MOS and interacts with multiple missions. Thus, the tracking network is not part of the MMOS. The tracking station scheduling and Mars relay systems are external systems that coordinate and integrate activities of multiple missions. They are not part of one mission operations system in a compositional sense (although they may be part of a project's organization). The tracking station scheduling system coordinates mission tracking needs with those of other missions (and station downtime) to form an integrated schedule. The Mars relay system coordinates the timing, data rates, and protocols for communications between landed spacecraft and Mars orbiters (i.e., between different project's MOSs) and manages the overall flow of data that flows through that relay network. (Note that a relay capability can easily be generalized to other locations in the solar system; Mars relay is the only such existing example.)

The third diagram shows the internal composition of the MMOS (Fig. 3). Functionality within the MMOS is allocated to individual services. These standard (unadapted) services are the mission operations engineering service (MOES), mission control service (MCS), navigation service (NAV), spacecraft operations service (SCOS), and science and instrument operations service (SIOS). It is important to note that these services are functional elements, not organizational ones. A particular MOS may or may not choose to establish its operations teams to match these services (see Sect. 4.7 for further discussion).

## 4.4 Interfaces

The MMOS must exchange information products with other systems and between internal elements. There are a number of items that need to be represented in the

<!-- PDF_PAGE: 7 -->


![figure_003.png](figure_003.png)



<div align="center">

Fig. 3 The composition diagram (an internal block diagram) describes the services internal to the MMOS

</div>


![figure_004.png](figure_004.png)



<div align="center">

Fig.4 Above is the radio science agreement between the MMOS and the tracking network. It exists on the MOS to DSN port. The controller port further clarifies the type of interaction as control information exchanged with a system under control

</div>

system design at each interface. The design needs to show the entity responsible for providing a specific product and the recipients. The interface needs to have a title and a description. The information product needs to be identified and described. The frequency of delivery and any constraints need to be specified (e.g., information provided on change, information made available upon request, whether or not a receipt acknowledgement is required). An interface agreement is used to capture all these attributes and to expose system functionality for use (Fig. 4). The agreement contains the list of information products being exchanged, describes the exchange of information, and specifies other related constraints. In addition to the interface agreement, characteristics of the interface itself are captured as ports within the MMOS model (Fig. 4).

<!-- PDF_PAGE: 8 -->


![figure_005.png](figure_005.png)



<div align="center">

Fig. 5 The above set of interfaces describes the products to be exchanged within the radio science agreement. Within the MMOS, responsibility for these product interfaces is delegated to the science and instrument operations service (SIOS)

</div>

More-detailed diagrams (Fig. 5) identify all information products flowing across and interface (and contained within an agreement). In addition, interfaces are further characterized by which services consume or produce information products. Delegation from the MMOS to an internal service—in this case the Science and Instrument Operations Service—is also depicted.

The agreement to exchange information of a particular type between two systems includes information about the timing of interactions. This is particularly important for mission operations, where information products are produced by human operators, and the timing of interactions (e.g., daily at 5 pm or within 1 h of receipt of telemetry) can drive performance requirements, complexity, staffing levels, and cost. The MMOS enables capture of this kind of information using sequence diagrams (Fig. 6). Specification of interactions such as these is important for operator-involved processes, but is essential for automating all but the simplest interactions between systems. It can also be of significant value when changes occur on one side of an interface, enabling impact assessment and compensating changes if needed.

## 4.5 Information Products

The MMOS defines a standard set of information types including plans, predicts, commands, measurements, and analysis products. These support the fundamental plan-execute-analyze pattern. Plans and commands are produced by plan for execution by the system under control (most commonly a flight system or a tracking station). Predicts are also a product of plan, for use by the analyze capability. Measurements are provided by the system under control (for analyze), and analysis products are needed (by plan) to create the next set of plans and commands. Each

<!-- PDF_PAGE: 9 -->


![figure_006.png](figure_006.png)



<div align="center">

Fig. 6 A SysML scenario diagram is used to show the steps involved in the agreement interaction

</div>

product provides information that the system needs in order to plan, execute, and/or analyze its activities.

Information products are described so as to be independent of implementation in software. This allows for decoupling the MOS design from the details of a specific software tool or format. Thus, the MMOS is not tied to any particular set of planning, telemetry, or command tools; those choices are left to a specific implementing project.

## 4.6 Functions

The MOS is composed of services (Sect. 4.3). Each service includes a fundamental set of capabilities: planning, execution, analysis, reporting, and data management (Fig. 7). These five capabilities are used to group specific functions performed by a service as described below:

- Planning consists of the functions needed to generate executable plans for a flight system or tracking station. Examples include integration and conflict resolution of multiple plan inputs, validation of plans against flight rules and resource constraints, and creation of predicts against which telemetered information can be compared.

<!-- PDF_PAGE: 10 -->


![figure_007.png](figure_007.png)



<div align="center">

Fig.7 Diagram shows the association of the planning, execution, analysis, reporting, and data management capabilities to a service block

</div>


![figure_008.png](figure_008.png)



<div align="center">

Fig. 8 Examples of functions within a capability

</div>

- Execution functions are those that a service is directed to perform by an external system or in response to its plans.

- Analysis functions evaluate the results of execution and compare them to predicts or other expectations.

- Reporting functions create documents or other materials in response to requests. These are used internally by services to monitor performance or by an external element to indicate status of a service. They also include production of standard documents needed for reviews.

- Data management functions deal with storage, retrieval, and dissemination of a service's information.

Figure 8 shows an example of the individual functions of one service (MOES) for its execution capability.

Functions are elaborated into processes. The MMOS uses Business Process Modeling Notation (BPMN) for its expressivity and ease of understanding (Fig. 9). Processes link to the information products they accept as inputs and output and capture the tasks needed, including conditionals for decision points or contingencies. Key attributes of processes include:

- Individual tasks can be elaborated as subprocesses (designated by “+”).

- Processes may call one another. A particular subprocesses can be used by multiple calling processes.

<!-- PDF_PAGE: 11 -->


![figure_009.png](figure_009.png)



<div align="center">

Fig. 9 A system level process delegated to MOES calls functions from two other services. Data association flows link information products, control flows link individual tasks. In this example, each task has an elaborating subprocess ("+"). An error boundary event (the "lightning bolt" symbol) ties the task to a contingency process describing steps to take if the task fails

</div>

- Information products internal to the process can be explicitly represented.

- Flow of control (tasks) and flow of information are both explicitly represented.

At the system (MOS) level, a process involves the coordination of functions provided by multiple services. In Fig. 9, MOES has overall responsibility for coordinating MCS and SCOS tasks during a tracking pass. In this simple example, MOES distributes information needed by MCS and SCOS. MCS and SCOS then execute pass-related activities and provide reports to MOES. Details of MCS

<!-- PDF_PAGE: 12 -->

and SCOS activities are delegated to those services to elaborate and design, just as (during operations) they are responsible for their execution. Boundary events (Fig. 8) tie a task to a contingency response process—for example, response to outof-limit telemetry indicators.

## 4.7 Roles

Roles are an important feature of the MMOS. Roles perform tasks-individual steps within a process-and may either be an individual or a piece of software (for an automated task). Roles are specified in the MMOS and explicitly linked to the tasks that make up operational processes and thence to the services that make up the MMOS.

Neither services nor roles require that a MOS adopt a specific organization structure. Flight projects employ a wide variety of organizational structures, depending on the size of the overall flight team and the difficulty and complexity of their work. The use of roles enables decoupling of functional elements (services) from organizational elements (teams) and provides each specific MOS the ability to organize roles into teams as it sees fit. Roles are linked to a service—in a functional sense. But roles may also be grouped into teams in response to project or MOS needs.

For example, a command operator and telemetry analyst are two separate roles, each responsible for a unique set process steps. Depending on the mission implementation, each role could be performed by a separate team or could be the responsibility of a single team. On a CubeSat or SmallSat mission, multiple roles or even entire services might be performed by one part-time individual.

## 4.8 Relationships

Typically, when assessing completeness of the design, there is a list of interfaces, a separate list of functions a team performs, and a different list of system and subsystem requirements. Implicitly, an engineer has connected the dots between these various aspects of the system. Reviewers look at the independent pieces of information and ask questions to understand how one impacts the other and to look for holes.

Within the MMOS, such relationships are explicitly specified. Not only are the relationships between items specified, but also the type of relationship is defined. Reports can be generated based on relationships (e.g., which requirements is a specific process related to—useful for V&V planning). To enable this kind of analysis of the design, the MMOS contains a set of key relationships between the various components described above. Many of these relationships are illustrated in Fig. 10 (see Sect. 5). These explicit relationships are useful for all types of

<!-- PDF_PAGE: 13 -->


![figure_010.png](figure_010.png)



<div align="center">

Fig. 10 This overview flowchart of the MMOS model is the directed top-down approach that the adaptation guide walks through

</div>

reviews, ranging from a report used by individual engineers to assess progress, to review products given to peer reviews or review boards, to preliminary V&V reports showing the relationship of requirements to the part of the design that fulfills them.

## 4.9 Reporting and Analysis

If left buried in the database of a model, the information is of little value. To be able to view or analyze the information, reports are built. Engineers use software such as DocGen [4] to build the needed documents as they model the system design.

As the model is being adapted or developed, reports are needed to understand the quality and completeness of the system design. Reports can be quickly built for relationships, descriptions, or whatever information the system engineer needs to understand at the time. Reports can provide analysis of the model. Items such as

<!-- PDF_PAGE: 14 -->

unallocated requirements or information products with no consumer can be easily identified. Since all the items are connected using a systematic approach, the model can be traced from the mission scenarios down to the details of the information products being exchanged.

At key decision points, a project generates gate products to show maturity of the design. These gate products represent a common set of views of the system. Using the MMOS, document models are populated with design information within the model and then render the information in a readable document format. Document models available in the MMOS include mission operations concepts, system requirements, operational interface agreements, and functional design descriptions, among others.

As an example, interface documentation for an MOS needs to address a number of concerns. Interface designs need to identify specific attributes including the name of the product being exchanged, the frequency of delivery, the size of the information product, the provider, the consumer(s), how information is requested and delivered, and any other constraints on the interface. Each of these attributes is present in the model for every interface. Using an existing document model, all these attributes may be extracted, formatted, and placed in a document form. The result is a reviewable document that is consistent across all interfaces and contains up-to-date design information. If reused across multiple flight projects, this method simplifies reviews by providing a common format and structure for the information being reviewed.

## 5 Methodology for Mission Adaptation

A structured methodology is a necessary adjunct to the rigor of a model-based representation of and MOS. For MMOS, this is provided in the form of an adaptation guide that follows a stepwise, top-down approach consistent with best practices [1, 2]. Figure 10 depicts the methodology, stepping through the MMOS components described in Sect. 4 (e.g., requirements) in general order of precedence. The guide itself begins with a start ("splash") page for Adaptation Guidance, which introduces the model and its design principles. Navigating through Adaptation Guidance in sequential order (Fig. 10) leads the user through the following processes:

1. Establish the Scope of the MOS—What are the goals that my MOS is intended to support? (Use cases, use case scenarios, requirements)

2. Establish the Composition of the MOSHow do I partition my MOS's design to accomplish my goals? (Systems, services, capabilities, functions)

3. Establish the Exchange of Information of the MOS—Who does my MOS interact with and what functionalities does my MOS expose? (Interfaces and agreements)

4. Establish the Behavior of the MOSHow does my MOS design accomplish my goals? (Processes and roles)

<!-- PDF_PAGE: 15 -->


![figure_011.png](figure_011.png)



<div align="center">

Fig.11 A sample page of Adaptation Guidance for requirements. Users may adapt requirements from this view or (for more expert users) work directly in the model

</div>

Each section of the Adaptation Guidance steps through a particular type of model content (e.g., requirements). Model content is introduced followed by three options for adaptation—how to add new content, how to modify existing content, and how to remove content. In this manner, existing specifications (e.g., an interface agreement from Sect. 4.4) can be used as is, modified, or deleted if unneeded. Adaptation Guidance was designed with simplicity and a less-experienced MBSE practitioner in mind. Each section shows the model components presented in Sect. 4 in an easy and understandable format. Notations for best modeling practices appear in green, and SysML tips and information are gray (Fig. 11). And although the guide is presented in a linear fashion, there are no barriers to working "backward." In general, iteration is necessary between parts of any system engineering process. Should the need for a new function be recognized during development, the MMOS model easily accommodates the need to backfill necessary interfaces, specify requirements, or even identify new use case scenarios.

The application of MBSE methods means that the Adaptation Guidance is more useful than conventional user guide-type documents. Adaptation itself is one of the viewpoints provided with the MMOS, and the adaptation guide is a view for any project-specific instance of the MMOS. The guide structure (itself a model) is distinct from the MMOS model content (or its project-specific adaptation) and therefore reusable. But the content appearing in the guide is sourced directly from the MMOS model itself, and any changes done within Adaptation Guidance are applied to the model. This is in contrast to conventional paper documents, which cannot reflect the changing state of the system model as adaptation proceeds. This method also provides rapid, concrete feedback to novice users (in the form of changes to the adapted MMOS) in the same place as tutorial and reference information.

<!-- PDF_PAGE: 16 -->

One challenge with implementing model-based system engineering in a project is that users will range from novices to experts in understanding the modeling languages, MBSE methods, and the software tools and plugins. Regardless of whether the user is a novice or an expert, they can start with the adaptation guide. A novice user may follow the stepwise, tutorial steps of the guide, while more advanced users use it as a "table of contents" to navigate through contents deep within the model. Moreover, the use of the adaptation guide as an entry point for adapting the model or working directly on the model is not mutually exclusive both options remain because the adaptation guide is always consistent with the content of the model.

## 6 Adoption and Advantages

Missions of all sizes and types can leverage model-based system engineering. From CubeSats to flagship missions that span multiple NASA centers, the conceptual architecture and design of an MOS must address many of the same concerns. All missions need to identify their operational scenarios, allocate requirements, describe their compositional structure, assign functions, identify responsibility for data products, and document processes. Smaller missions may require a less complex design; they must still address many of the same concerns as larger missions. Missions of all sizes have utilized the MSAF and MMOS to aid in their MOS architecture development and early design.

## 6.1 Asteroid Redirect Robotic Mission (ARRM) Use of MMOS

The ARRM mission is a technology demonstration and human spaceflight precursor mission. Its intent is to retrieve a boulder from the surface of a near-Earth asteroid and return it to a lunar orbit for later examination by astronauts. The ARRM Project organization involves multiple NASA centers, including Glenn Research Center, Goddard Space Flight Center, Johnson Space Center, and JPL. All these development organizations need a common understanding of the project elements and systems, their designs, allocation of responsibilities, and clearly defined common terminology. Using MBSE across the project has significantly helped to facilitate communication across distributed teams. The architecture enables a layered approach, where the design can be adapted at a level of detail appropriate to project needs at each stage in its life cycle.

ARRM was provided the architecture framework for modeling an MOS (the MSAF) and a set of integrated MOS design information (functions, interfaces, agreements, and processes) and associated MOS (Level 3) requirements. This has helped to quickly define an initial requirements set and to ensure completeness.

<!-- PDF_PAGE: 17 -->

ARRM is also using MMOS patterns for representing information, enabling clarity about information products and their flow through the flight and ground systems.

The collection of system views applicable to and used by ARRM includes the standard MOS key decision point (KDP) documents. ARRM has adapted the document models to suit mission-specific needs and is enhancing and improving some of the analysis viewpoints.

## 6.2 Europa Project Use of MMOS

The Europa Mission will conduct detailed reconnaissance and look for evidence of subsurface environments that could harbor life. It includes a partnership between JPL and the Applied Physics Lab (APL) managed by John Hopkins University. System modeling has become integral to the project's system engineering approach. The MSAF and MMOS were utilized in 2014 during the mission concept study and review preparations. In 2015, they were used for early requirements and conceptual architecture development. In late 2015, the MMOS was deployed to the Europa modeling environment, and adaptation for the specific Europa MOS architecture is currently in progress.

Accomplishments and benefits seen to date include:

1. A draft set of MOS functional requirements for Europa Mission Concept Review based on the MMOS was generated in 2 days—and ingested into the Europa System Model framework. Conventional efforts to develop a set of draft requirements in a bottoms-up sense take months. This provided the mission with a clean starting set which could be incorporated into the top-down requirement development process.

2. The small MOS design team is currently assessing the sets of operational functions in the MMOS model for each of the service areas and identifying the needs for mission-specific adaptation to them. This represents a better starting point than either starting from scratch or trying to extract such a list from a previous project's design materials.

3. The MOS team is using the agreements and interfaces of the MMOS and adapting them to define and capture ground system interfaces. These include the MOS interfaces to the tracking network, science data archive, launch services, and project science systems.

4. The project is capturing the ground system and MOS concepts in architecture documents which are part of the system model. The operations concept document, the MOS functional requirement document, and the functional description document will be generated from the system model and include the modeled MOS content and diagrams.

In addition, the Europa MOS design team plans to refine and update MMOS use case scenarios and add new scenarios as they are identified. Some MMOS terminology is expected to change as well (e.g., Planning, Coordination, and

<!-- PDF_PAGE: 18 -->

Execution (PCE) will replace the MOES service name, and Science System will replace Project Science). Preliminary examination suggests this will not require significant rework.

## 6.3 Asteria

The Asteria mission is an astrophysics technology demonstration of arc second line-of-sight pointing, using a 6U CubeSat platform. Like many such missions, the development team is very small; the MOS design team consists of a single, parttime engineer. Using the MMOS and following the methodology, an MOS design was completed and delivered. The operations concept, requirements, functional and interface designs and specifications, and operations processes were developed on a small budget without sacrificing necessary completeness or quality. This usage demonstrated scalability of the MMOS models—despite being designed with discovery—to flagship-class missions in mind, its use on a CubeSat mission was straightforward; for example, unnecessary model items (e.g., specific requirements or functions) were easy to delete. The MOS engineer noted that he was able to focus on the technical aspects of the system design, rather than researching how to design the system and spending time documenting it from scratch.

## 6.4 Lunar Resource Prospector Mission

The Lunar Resource Prospector Mission is a technology demonstration for harvesting volatiles near the South Pole of the Moon. The MOS design team (at Ames Research Center) is adapting the MMOS for their mission. To date, use case scenarios, requirements, and system composition and services have been adapted. The use of the MMOS which provides a framework with a pre-populated reference design has allowed the design team to spend more time developing their system and less time on developing a mission unique architecture.

## 6.5 Incorporating Mission Adaptation Back into the MMOS

As each mission adapts the MSAF and MMOS, they identify items that were not part of the baseline products. When missions request to use the products, we request that they provide feedback as to what they added, changed, or found not to be of value. This allows the architecture and reference system design to evolve to meet the everchanging needs of the next generation of missions.

<!-- PDF_PAGE: 19 -->

## 6.6 Challenges

As with any innovation, there are challenges to be overcome. The adoption of model-based approaches requires a degree of formality of both thought and approach. Conventional diagrams and narrative description allow for differing interpretations far more than do SysML or other modeling languages. This imprecision allows for more latitude (e.g., two interacting elements may have very different representations of the same interface) but ultimately results in problems in implementation, testing, or even operations. Projects and teams need to be sufficiently trained and to be given time and opportunity to work through the learning curve. This is the investment needed to yield the advantages noted by missions (above) and in Sect. 4.8.

MBSE is fundamentally reliant on software that is responsive to system engineering needs. The software tooling continues to evolve and be updated. One challenge is managing an MBSE environment that is a diverse collection of tools, including both COTS and in-house developed software.

In terms of the MMOS framework itself, both the technical issues in evolving the MMOS and support for doing so present challenges. For both Europa and ARRM, the MMOS represents one part of a larger project system model. Consistency, interfaces, and integration have only just begun to be addressed. Changes both to project instantiations of the model and to the MMOS themselves require a degree of configuration control and management that may be challenging, particularly in the formulation phase of flight projects.

## 7 Conclusions

The development of the MMOS model and its associated methodology has facilitated the use of MBSE techniques by flight projects. Early adoption of these methods shows significant promise for having MOS formulation and design phase efforts that are more repeatable from mission to mission and that produce higher-quality requirements and design products in a cost-effective manner. The extent of adoption by projects of varying size (cost) and mission type and the ability of the MMOS to capture feedback and improve in response suggest that return on the overall investment in such capabilities is only just beginning. In its focus on building generalized, scalable model and method for the development of mission operations systems, the MMOS is highly consistent with NASA's efforts to find and create agency-wide efficiencies such as the Mission Operations Capability Leadership effort.

Acknowledgments The authors acknowledge the contributions of the many members of the Ops Revitalization Team that made this work possible. This research was carried out at the Jet Propulsion Laboratory, California Institute of Technology, under a contract with the National Aeronautics and Space Administration.

<!-- PDF_PAGE: 20 -->

## References

1. SE Handbook Working Group: INCOSE Systems Engineering Handbook v3.2.2. International Council on Systems Engineering, INCOSE-TP-2003-002-03.2.2, San Diego, CA, Oct 2011

2. NASA Systems Engineering Handbook, NASA Headquarters, NASA/SP-2007-6105 Rev1, Washington, DC, Dec 2007

3. Friedenthal, S., Moore, A., Steiner, R.: A Practical Guide to SysML: The Systems Modeling Language. Elsevier, New York (2008). Chaps. 1, 2

4. Jackson, M., Delp, C., Bindschadler, D., Sarrel, M., Wollaeger, R., Lam, D.: Dynamic gate product and artifact generation from system models, (2011) IEEE Aerospace Conference Proceedings, AERO 2011, May 13, 2011

5. Bindschadler, D.L., Delp, C.L., McCullar, M.: Principles to products: toward realizing MOS 2.0. AIAA Space Operations 2012 Conference Proceedings, June 2012