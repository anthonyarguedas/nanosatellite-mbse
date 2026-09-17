## RQ2-1

This thesis presents a CubeSat Reference Architecture designed to meet these needs and explores its unique features, diagrams, and custom libraries. The CubeSat Reference Architecture was validated by relevant course instructors and is being used by a cohort of students in the Spacecraft Design Sequence at AFIT. (p. 6)

This Reference Architecture will use No Magic's Cameo Systems Modeler as the primary modeling tool. Cameo Systems Modeler was chosen as the modeling tool due to its common usage at AFIT and as it is being used more commonly in program offices in the Air Force Life Cycle Management Center. Mathworks' MATLAB will be used for analysis as it is a commonly used program in academia and throughout the Department of Defense, and it easily integrates with Cameo. Finally, Apache's Velocity Templating Language (VTL) will be used to generate documentation from the model elements. These tools will be used to develop a Reference Architecture that will be tested by students and then demonstrated to AFIT faculty for feedback. (p. 21)

In the CubeSat domain, Kaslow and a group of Subject Matter Experts built a CubeSat Reference Model (CRM) as part of a partnership between the Object Management Group (OMG) and the International Council on Systems Engineers (INCOSE). The CRM was intended to help CubeSat developers by providing logical, reusable architecture elements at a high level [21]. Some sample diagrams are provided in their interim status updates [21, 22, 23, 24, 25, 26], but the Cameo model itself was not available to investigate. This CRM describes three levels of architectural foundation that are necessary to capture the whole domain: the enterprise level, the space and ground segments, and the space and ground subsystems. Figure 12 indicates the structure for the CubeSat domain as described by Kaslow et al. (p. 40)

[Figure 15.](../../../pdfs/citation-reports/citation-report-1691/figure_016.png) CRM Space Segment (p. 42)

The Component Library is a function inspired by the SUAS Reference Architecture [20]. The goal is to have a library of components to choose from for each subsystem for rapid prototyping that improves over time. As teams create new CubeSat designs, the individual components can be stored in the Component Library for future reuse by other teams. For example, if there are multiple commercially available solar arrays that previous teams have used in their designs, those solar arrays will be available to reuse with all of their value properties already filled in. (p. 89)

[Figure 47.](../../../pdfs/citation-reports/citation-report-1691/figure_042.png) Component Library (p. 91)

[Figure 49.](../../../pdfs/citation-reports/citation-report-1691/figure_044.png) Component Library - EPS (p. 92)

One of the primary goals for this CubeSat Reference Architecture was to establish the platform for future work. Some of that work has already begun, including an Integrated Mission Modeling Tool that uses the physical structure in the Reference Architecture to create detailed MATLAB Simulink and STK simulations for mission modeling. These tools will improve the fidelity of mission simulations and provide visual views of the orbits for ground contacts, while also simulating multiple payloads at once. (p. 104)

## RQ2-1.2

MBSE requires a modeling language, a modeling method, and a modeling tool [11]. In this thesis, those are respectively the Systems Modeling Language (SysML), the Object-Oriented Systems Engineering Method (OOSEM), and the Cameo Systems Modeler tool. (p. 31)

SysML is a standard modeling language, which added systems engineering functionality to the Unified Modeling Language (UML) that has been used extensively in Software Engineering for decades [11]. SysML provides a language, or the definitions and notations for nine different diagram types to describe a complex system, many of which will be used in this Reference Architecture. SysML is expressed graphically through those diagrams, listed in Figure 8, to show various system viewpoints. For example, a Block Definition Diagram (bdd) expresses system structure, and an Activity Diagram can show specific system activities. Within "blocks", further detail can be expressed on an Internal Block Diagram (ibd). Further explanations will accompany their respective diagrams in Chapter IV, but for now, it's important to know that SysML provides the language and is built into the modeling tool, described later in this chapter. (pp. 31-32)

[Figure 8.](../../../pdfs/citation-reports/citation-report-1691/figure_009.png) SysML Taxonomy (p. 32)

OOSEM uses SysML in a top-down, model-based approach that leverages object-oriented concepts with traditional systems engineering methods to architect more flexible and extensible systems that can evolve with technology and changing requirements [14]. OOSEM was developed in part by Lockheed Martin Corporation as a method to capture and analyze requirements of complex systems, integrate with object-oriented software and hardware, and support system-level reuse and design evolution [15]. (pp. 32-33)

This research used the Object Oriented Systems Engineering Method with SysML to create a CubeSat Reference Architecture. (p. 105)

## RQ2-1.4

This Reference Architecture should be useable even by users not so familiar with MBSE, and it should assist with the system-level review process including Critical Design Reviews, Test Readiness Reviews, etc. Even though AFIT students will be the first users of this Reference Architecture, it is generic enough to be used for any team wishing to develop a CubeSat program from the ground up. It has all the functionality needed to develop requirements, design the physical system, and perform basic simulations. It also features helpful resources like a component library to assist with the physical design and document generators to create tailored stakeholder documents from model elements. (p. 18)

A Reference Architecture offers a baseline template for students to build from, using lessons learned from past projects and creating the framework to streamline the design process. A large effort of this research was focused on creating a generic model with default component specifications throughout. This was intended to spark ideas in the brainstorming process for students and aid in system analysis. Another component of this research was creating basic analysis capabilities within the model, allowing students to tweak component specifications to see how those changes affect overall capabilities and requirements. Additionally, the model traces the analysis to template requirements that future teams will tailor for their unique projects. This allows for rapid simulations of key performance parameters or measures of effectiveness for the system. Additional work is being done using this Reference Architecture for more in-depth state analysis and integration with Systems Tool-Kit (STK) and MATLAB, so it's critical to form a robust baseline to build off of. (p. 19)

A generic physical decomposition of a standard CubeSat has been included to help teams stay organized and to provide a starting point to work from. Figure 33 shows a top level view, with subsystems being rolled up into subsystem blocks. Each of those subsystem blocks contains more detailed diagrams within for individual components. Organizing it in this fashion prevents massive, unreadable diagrams from being presented to stakeholders and instead, the specific details for different components are only shown in the appropriate level diagram. The primary benefit of this provided physical decomposition is the value properties included in each block. The pre-built value properties allows for analysis tools to be included in the Reference Architecture, because the inputs are already defined. The included value properties also follow a "camel case" naming convention that reduces errors when they are used with constraint blocks. Teams can add additional value properties and use them for analysis, but the provided set is a well-rounded start. (pp. 72-73)

Figure 34 shows an example of one of those subsystem views, and Figure 35 shows how teams can tailor that generic diagram into something that meets their unique mission needs. In this example, the ADCS subsystem had unnecessary components that were removed, and values were added to each remaining block to describe the chosen components. Additional components were also added to address the needs of this particular system. (p. 75)

[Figure 34.](../../../pdfs/citation-reports/citation-report-1691/figure_031.png) ADCS Template (p. 75)

[Figure 35.](../../../pdfs/citation-reports/citation-report-1691/figure_032.png) ADCS tailored (p. 75)

This research used the Object Oriented Systems Engineering Method with SysML to create a CubeSat Reference Architecture. While originally intended to be used by students at AFIT in their Spacecraft Design Sequence, the model can be tailored to be used by other teams that have similar goals. (p. 105)

## RQ2-2

Kaslow et al. described all of the CubeSat subsystems and provided Block Definition Diagrams for the major views of a CubeSat, including each mission segment, as shown in Figure 14 for the Ground Segment and Figure 15 for the Space Segment. (pp. 41-42)

[Figure 15.](../../../pdfs/citation-reports/citation-report-1691/figure_016.png) CRM Space Segment (p. 42)

The CubeSat Reference Architecture is a large model, so the organizational structure is critically important. Many users of this model will be new to MBSE or at least new to Cameo Systems Modeler, and with so many diagrams and packages, it can be easy to get lost or have trouble finding a diagram that you need. Furthermore, modelers may prefer different navigational styles. Some prefer visual diagrams, while others prefer navigating a nested folder structure, while others still may prefer to directly navigate to a desired diagram with one click from an index. To address these preferences, multiple ways to navigate the model have been provided. Each navigation style is based off the four pillars of SysML - Requirements, Structure, Behavior, and Parametrics [31]. This model uses the term analysis instead of parametrics to cover more content, but does contain the parametric diagrams to assess system performance. The extra package, called Document Generators, contains templates that pull information from each of other packages, so it is kept separate. (p. 57)

The standard way is to navigate using the "Containment Tree," or Cameo's File Tree, as shown in Figure 19. Notice the numbered packages for the most important packages to guide users to the appropriate section. Note that some packages, such as those inside the Generic CubeSat Model, include hyperlink icons, informing the user that those packages are also links to more detailed diagrams. A user can navigate this tree and find the appropriate diagrams in an intuitive manner. For example, if they wish to work on the CubeSat's physical decomposition, they will navigate to the Structure package and find the CubeSat package within. If they need to generate some activity diagrams for mission phases, those diagrams will be located within the Behavior section, and so on. (pp. 57-58)

[Figure 19.](../../../pdfs/citation-reports/citation-report-1691/figure_020.png) Containment Tree (p. 58)

Some users may prefer to navigate using diagrams instead. This has been built in to the Reference Architecture by creating top level "organization diagrams" for the most used sections. Figure 20 shows the first page users see when they open up the model, and each icon within that diagram is hyperlinked to another, similar diagram at the lower level. These organization diagrams will be detailed in upcoming sections. (pp. 58-59)

[Figure 20.](../../../pdfs/citation-reports/citation-report-1691/figure_021.png) Model Organization (p. 59)

Finally, some users may wish to directly navigate to a diagram by name. The "Index" diagram shown in Figure 21 shows all of the built-in diagrams and tables that users will be expected to complete during the design sequence, organized by category. If additional diagrams are created, this index will need to be updated accordingly. This Index provides a very fast and easy way to open up one diagram in particular if the user forgot where a diagram was located, for example. (pp. 59-60)

[Figure 21.](../../../pdfs/citation-reports/citation-report-1691/citation-report-1691.pdf#page=60) Index (p. 60)

Users will start their design process in the Requirements package. The Requirements Organization diagram is shown in Figure 24, which links to each applicable diagram and provides basic instructions to help users navigate. While the Requirements process is not a linear process to be accomplished at one time, it is structured in the order in which users will likely need the included diagrams. (pp. 63-64)

[Figure 24.](../../../pdfs/citation-reports/citation-report-1691/figure_024.png) Requirements Organization (p. 64)

The Requirements section begins with users creating blocks for their source material. This Source Documentation diagram will continue to grow over the course of the design sequence, but some common CubeSat references are included and attached. By attaching source material to blocks, as shown in Figure 25, requirements can be properly traced to the exact source document version. Furthermore, it makes it much easier for users to quickly see the source documentation, instead of needing to search the internet based off the source name. (p. 65)

[Figure 25.](../../../pdfs/citation-reports/citation-report-1691/figure_025.png) Source Documentation (p. 65)

The Reference Architecture assumes that design teams were provided with an MCD. Given that, users should parse the contents of the MCD into blocks that can be used within the model. Instructions are provided in the diagrams for how to accomplish this, but the goal is to have a set of Design Constraints and Required Capabilities, an Operational Context statement, a Mission Need statement, and a matrix that traces these new blocks to the MCD. If any changes occur after the original MCD was parsed, users can generate a new MCD based off these tables using the Document Generator tool. Note also that the tables provided include an ID naming convention that will be continued when users add additional entries into the respective tables. Additionally, each table is populated with blocks that contain the correct modeling "stereotype" so that tables can properly and automatically populate. Figure 26 shows an example of a Design Constraints table for one class project, and that pattern repeats for the Required Capabilities table. The tables as provided only include sample names, as these will need to be replaced as soon as an MCD is provided. (pp. 65-66)

[Figure 26.](../../../pdfs/citation-reports/citation-report-1691/figure_026.png) Design Constraints (p. 66)

The next major step is to perform a Stakeholder Analysis as a team. Figure 27 shows the structure of the Stakeholder Analysis package, with a package for Stakeholder Concerns and another for Stakeholder Needs. Design teams will first brainstorm a list of Stakeholders and document whatever concerns they may have in the form of "comments" in Cameo. Some generic Stakeholders are provided as well as generic "concerns" that users should edit and add to for their unique program. The issue with these Stakeholder Concern "comments" is that requirements cannot be traced directly to them. To address this limitation, Stakeholder Needs are then created as blocks that represent those previously created concerns. Several concerns may address the same topic, so one Stakeholder Need block can be created that maps to each relevant concern. Figure 28 shows a portion of the matrix that will automatically change after the previous steps. By mapping the new Need blocks to the Concern comments and to their applicable stakeholder, the user can see where each Stakeholder Need comes from. Once the team has a complete list of Stakeholder Needs with traceability back to their concerns, the Stakeholder Analysis Report can be generated. The Document Generator process will be detailed later in this chapter. (pp. 66-67)

[Figure 27.](../../../pdfs/citation-reports/citation-report-1691/figure_027.png) Stakeholder Analysis (p. 67)

[Figure 28.](../../../pdfs/citation-reports/citation-report-1691/citation-report-1691.pdf#page=68) Stakeholder Matrix (p. 68)

The remaining sections within the Requirements package will be completed later in the design sequence. It is structured using a tiered Requirements convention, where teams start by generating a list of Mission Requirements, then a list of System or Space Vehicle Requirements, and finally a list of Subsystem Requirements for each subsystem. Each tier is organized in a similar fashion, but with different stereotypes and some different data fields. Additionally, template requirements for each tier have been provided, as well as some example entries in other data fields to show as examples, as shown in Figure 29. Each tier of requirements also comes with a traceability matrix for users to trace or derive that tier from. Note that the Subsystem Requirements table, shown in Figure 30, is further broken out into subsystem categories, with template requirements for each to get teams started on the brainstorming process. (pp. 68-69)

[Figure 29.](../../../pdfs/citation-reports/citation-report-1691/citation-report-1691.pdf#page=69) Mission Requirements (p. 69)

[Figure 30.](../../../pdfs/citation-reports/citation-report-1691/citation-report-1691.pdf#page=70) Subsystem Requirements (p. 70)

After coming up with a list of requirements, teams need to decide on a physical structure that can satisfy those requirements. Instead of starting from a blank slate, this CubeSat Reference Architecture provides teams with a generic physical decomposition for a CubeSat and its various subsystems, as well as related systems, such as the Launch Vehicle and the Ground segment. Figure 31 shows a high level view of the areas that the Reference Architecture includes. Each package is hyperlinked to more detailed diagrams to fill out, and the most relevant value properties have been included for each. (pp. 70-71)

[Figure 31.](../../../pdfs/citation-reports/citation-report-1691/figure_028.png) Mission Context bdd (p. 71)

Figure 32 shows the same Mission Context, but in the form of an internal block diagram so that various data or signal flows can be shown, highlighting interactions between the CubeSat system of interest and relevant systems in the overall mission context. This diagram also highlights key operations and relevant value properties that add value to this view. (p. 72)

[Figure 32.](../../../pdfs/citation-reports/citation-report-1691/figure_029.png) Mission Context ibd (p. 72)

A generic physical decomposition of a standard CubeSat has been included to help teams stay organized and to provide a starting point to work from. Figure 33 shows a top level view, with subsystems being rolled up into subsystem blocks. Each of those subsystem blocks contains more detailed diagrams within for individual components. Organizing it in this fashion prevents massive, unreadable diagrams from being presented to stakeholders and instead, the specific details for different components are only shown in the appropriate level diagram. The primary benefit of this provided physical decomposition is the value properties included in each block. The pre-built value properties allows for analysis tools to be included in the Reference Architecture, because the inputs are already defined. The included value properties also follow a "camel case" naming convention that reduces errors when they are used with constraint blocks. Teams can add additional value properties and use them for analysis, but the provided set is a well-rounded start. (pp. 72-73)

[Figure 33.](../../../pdfs/citation-reports/citation-report-1691/figure_030.png) Physical Decomposition (p. 74)

While this CubeSat Reference Architecture is not intended to be fully simulated, a State Machine diagram is necessary to highlight the states that the CubeSat may be in. The diagram in Figure 36 serves as an example so teams know what a CubeSat state machine might look like, but teams should make their own to describe their unique mission CONOPS. By filling in this diagram, additional tables will also be pre-generated, pulling state transitions, guards, etc. from this diagram. These state transition tables and state descriptions are useful for stakeholder documentation when the CubeSat states are discussed. (p. 76)

[Figure 36.](../../../pdfs/citation-reports/citation-report-1691/figure_033.png) State Machine (p. 76)

The Mission Phases package (Figure 38) contains a block definition diagram which has a place for each individual mission phase's activity diagram, subsystem status table, and text description. During each mission phase, the CubeSat's various subsystems will be in unique configurations, and this package includes an easy way to capture those. To capture these different configurations, tables have been created for teams to determine the various states for each subsystem for each phase. In addition to the subsystem configuration tables, teams should write textual descriptions of the applicable mission phase in the "Mission Phases" table (Figure 39) and create activity diagrams to show what happens in each phase. All of these will be used in the CONOPS document. (p. 78)

[Figure 38.](../../../pdfs/citation-reports/citation-report-1691/figure_035.png) Mission Phases (p. 79)

[Figure 39.](../../../pdfs/citation-reports/citation-report-1691/citation-report-1691.pdf#page=80) Mission Phase Descriptions (p. 80)

The Fault Management package, shown in Figure 40, includes similar tables that will describe the various fault states in narrative form and in tables that shows each subsystem status. (p. 80)

[Figure 40.](../../../pdfs/citation-reports/citation-report-1691/figure_036.png) Fault Management (p. 81)

The Analysis portion is how teams show that their requirements are verified and how they track any external analysis done to generate requirements. Figure 41 shows the top level organizational structure. As is the case throughout this Reference Architecture, many of the included packages are hyperlinked to more detailed diagrams. (pp. 81-82)

[Figure 41.](../../../pdfs/citation-reports/citation-report-1691/figure_037.png) Analysis Organization (p. 83)

Figure 48 shows how it could be used in a simple example with different CubeSat bus sizes. In the Structures package, multiple chassis sizes, with their dimensions all filled out, can be quickly copied and pasted into a new model. If some value differs from the default values provided, the team would just need to make those modifications. Figure 49 shows how Enumeration lists are also stored in the component library to be used throughout the model. These enumeration lists are all consolidated in their respective subsystem packages instead of scattered across the physical model. In this example, instead of typing in a string of text to denote the battery chemistry, the user can just select from a drop-down list of the available types in the enumeration list. These are created for many subsystems, and as new choices become available, these can be updated. (p. 90)

[Figure 47.](../../../pdfs/citation-reports/citation-report-1691/figure_042.png) Component Library (p. 91)

[Figure 49.](../../../pdfs/citation-reports/citation-report-1691/figure_044.png) Component Library - EPS (p. 92)

For that reason, all Value Types are stored in one central place within the Component Library. This has also been done with Object Flows in the Reference Architecture. Object Flows represent the flow of objects, whether they are matter, energy, or data, primarily used in the Mission Context diagram shown earlier in Figure 32. (p. 93)

## RQ2-2.1

SysML provides a language, or the definitions and notations for nine different diagram types to describe a complex system, many of which will be used in this Reference Architecture. SysML is expressed graphically through those diagrams, listed in Figure 8, to show various system viewpoints. For example, a Block Definition Diagram (bdd) expresses system structure, and an Activity Diagram can show specific system activities. Within "blocks", further detail can be expressed on an Internal Block Diagram (ibd). (pp. 31-32)

Some users may prefer to navigate using diagrams instead. This has been built in to the Reference Architecture by creating top level "organization diagrams" for the most used sections. Figure 20 shows the first page users see when they open up the model, and each icon within that diagram is hyperlinked to another, similar diagram at the lower level. These organization diagrams will be detailed in upcoming sections. (pp. 58-59)

Finally, some users may wish to directly navigate to a diagram by name. The "Index" diagram shown in Figure 21 shows all of the built-in diagrams and tables that users will be expected to complete during the design sequence, organized by category. If additional diagrams are created, this index will need to be updated accordingly. This Index provides a very fast and easy way to open up one diagram in particular if the user forgot where a diagram was located, for example. (pp. 59-60)

Users will start their design process in the Requirements package. The Requirements Organization diagram is shown in Figure 24, which links to each applicable diagram and provides basic instructions to help users navigate. (pp. 63-64)

The Requirements section begins with users creating blocks for their source material. This Source Documentation diagram will continue to grow over the course of the design sequence, but some common CubeSat references are included and attached. (p. 65)

Figure 26 shows an example of a Design Constraints table for one class project, and that pattern repeats for the Required Capabilities table. (p. 66)

The next major step is to perform a Stakeholder Analysis as a team. Figure 27 shows the structure of the Stakeholder Analysis package, with a package for Stakeholder Concerns and another for Stakeholder Needs. (p. 66)

Figure 28 shows a portion of the matrix that will automatically change after the previous steps. (p. 67)

Each tier of requirements also comes with a traceability matrix for users to trace or derive that tier from. Note that the Subsystem Requirements table, shown in Figure 30, is further broken out into subsystem categories, with template requirements for each to get teams started on the brainstorming process. (p. 69)

Figure 32 shows the same Mission Context, but in the form of an internal block diagram so that various data or signal flows can be shown, highlighting interactions between the CubeSat system of interest and relevant systems in the overall mission context. This diagram also highlights key operations and relevant value properties that add value to this view. (p. 72)

While this CubeSat Reference Architecture is not intended to be fully simulated, a State Machine diagram is necessary to highlight the states that the CubeSat may be in. The diagram in Figure 36 serves as an example so teams know what a CubeSat state machine might look like, but teams should make their own to describe their unique mission CONOPS. (p. 76)

The Mission Phases package (Figure 38) contains a block definition diagram which has a place for each individual mission phase's activity diagram, subsystem status table, and text description. (p. 78)

The Fault Management package, shown in Figure 40, includes similar tables that will describe the various fault states in narrative form and in tables that shows each subsystem status. (p. 80)

The Verification Analysis package contains several templates or patterns that highlight some capabilities of Cameo for requirement verification. For example, the Thermal Analysis parametric diagram in Figure 42 shows how to use a MATLAB script to perform analysis based off the values entered in the thermal subsystem, as well as any other values that affect these calculations, such as the CubeSat's mass and some orbital parameters. (p. 83)

[Figure 31.](../../../pdfs/citation-reports/citation-report-1691/figure_028.png) Mission Context bdd (p. 71)

[Figure 32.](../../../pdfs/citation-reports/citation-report-1691/figure_029.png) Mission Context ibd (p. 72)

[Figure 33.](../../../pdfs/citation-reports/citation-report-1691/figure_030.png) Physical Decomposition (p. 74)

[Figure 36.](../../../pdfs/citation-reports/citation-report-1691/figure_033.png) State Machine (p. 76)

[Figure 38.](../../../pdfs/citation-reports/citation-report-1691/figure_035.png) Mission Phases (p. 79)

[Figure 40.](../../../pdfs/citation-reports/citation-report-1691/figure_036.png) Fault Management (p. 81)

[Figure 41.](../../../pdfs/citation-reports/citation-report-1691/figure_037.png) Analysis Organization (p. 83)

[Figure 49.](../../../pdfs/citation-reports/citation-report-1691/figure_044.png) Component Library - EPS (p. 92)

## RQ2-3

3. Define Logical Architecture: A "logical" architecture is created that captures key functions in logical blocks, allowing for specific components to be chosen later in place of the logical depiction. (p. 33)

4. Synthesize Candidate Allocated Architectures: From the logical architecture, create potential physical instantiations using value properties and selected components. Each component at this stage is then traced to system requirements in table or matrix form. (p. 33)

5. Optimize and Evaluate Alternatives: Trade studies or other analysis is conducted at this step among the candidate architectures. Parametric diagrams within the model or integrating other tools can simulate system performance with the chosen components so alternative solutions can be compared. (p. 34)

As discussed in Chapter II, a similar effort has already been taking place with Small Unmanned Aerial Systems at AFIT. Those efforts created a Reference Architecture for a similar design course sequence, so the first step was to explore that Reference Architecture and get some ideas and any lessons learned from that effort. Of primary note was their component library, which allows the SUAS designer to choose from commonly available components to rapidly prototype a new system. Their organization was also well done, with top-level pages to show internal structures and a package breakdown to separate Requirements, Structure, Behavior, and Analysis. Several of these organization practices will be expanded upon in this CubeSat Reference Architecture. (p. 53)

While not explicitly stated as such, students going through this course sequence learned the OOSEM approach to modeling systems, so that approach should be used for this Reference Architecture as well. To bridge the gap between Wertz' Firefly model [5] and the OOSEM methodology, Friedenthal's text [27] was used as a reference, as he also uses OOSEM in his approach. Looking at these models provided a good foundation upon which to start building a Reference Architecture. Wertz had detailed subsystem breakdowns and relevant calculations, Friedenthal explained the OOSEM process and how it relates to CubeSat designs, and the SUAS model [20] helped guide the organizational structure and capabilities of a Reference Architecture. (pp. 53-54)

Once completed, this Reference Architecture would be used from the very beginning of the design course sequence all the way through its conclusion. They will be given the Reference Architecture file with their mission-specific MCD and some guidance, and then they design the system from the ground up using that template. (p. 54)

Figure 34 shows an example of one of those subsystem views, and Figure 35 shows how teams can tailor that generic diagram into something that meets their unique mission needs. In this example, the ADCS subsystem had unnecessary components that were removed, and values were added to each remaining block to describe the chosen components. Additional components were also added to address the needs of this particular system. (p. 75)

[Figure 34.](../../../pdfs/citation-reports/citation-report-1691/figure_031.png) ADCS Template (p. 75)

[Figure 35.](../../../pdfs/citation-reports/citation-report-1691/figure_032.png) ADCS tailored (p. 75)

The included parametric diagrams serve as patterns to replicate and modify, reducing the learning curve for teams who haven't learned these capabilities yet. (p. 84)

The Component Library is a function inspired by the SUAS Reference Architecture [20]. The goal is to have a library of components to choose from for each subsystem for rapid prototyping that improves over time. As teams create new CubeSat designs, the individual components can be stored in the Component Library for future reuse by other teams. (p. 89)

A team could swap out multiple solar arrays from the Component Library in their EPS subsystem diagram and perform analysis to quickly assess how each one performs for their system. (p. 90)

The Reference Architecture is meant to be improved and adapted over time. As new teams use the model, they will be creating new physical blocks for components they chose, and they will be creating new constraint blocks for analysis. These can be saved in the component library for future reuse, so over time, the component library can grow and contain more "plug and play" blocks. Eventually, the component library should have a variety of components for each subsystem to choose from, and there should be analysis blocks to tailor depending on the mission's requirements. (p. 104)

This research delivered a variety of helpful tools for teams to use that makes their modeling efforts easier. Auto-populating tables and matrices, a library of parts and value properties to choose from, analysis patterns to tailor, and document generators will save time and hopefully improve the quality of CubeSat models going forward. (p. 105)

## RQ2-3.1

MBSE requires a modeling language, a modeling method, and a modeling tool [11]. In this thesis, those are respectively the Systems Modeling Language (SysML), the Object-Oriented Systems Engineering Method (OOSEM), and the Cameo Systems Modeler tool. (p. 31)

OOSEM uses SysML in a top-down, model-based approach that leverages object-oriented concepts with traditional systems engineering methods to architect more flexible and extensible systems that can evolve with technology and changing requirements [14]. OOSEM was developed in part by Lockheed Martin Corporation as a method to capture and analyze requirements of complex systems, integrate with object-oriented software and hardware, and support system-level reuse and design evolution [15]. (pp. 32-33)

While not explicitly stated as such, students going through this course sequence learned the OOSEM approach to modeling systems, so that approach should be used for this Reference Architecture as well. (p. 53)

This research used the Object Oriented Systems Engineering Method with SysML to create a CubeSat Reference Architecture. (p. 105)

## RQ3-1

When preparing to develop the CubeSat Reference Architecture, a Digital Engineering (DE) Validation Tool from SAIC was made available [28]. This free tool was developed by SAIC and is provided free to the public as a set of validation rules and customizations for Cameo. SAIC states "Our free system model validation tool guides modeling consistency to reduce errors, aid analyses, and improve quality." This appeared to be a useful addition to this CubeSat Reference Architecture, so it was closely examined. (p. 44)

To assist users who are less familiar with Cameo or MBSE, a full CubeSat Modeling How-To Guide has been included within the model. Users can double-click the document icon in Figure 22 and open up a thorough guidebook that walks through each section and each diagram that users can fill out, in addition to guidance regarding the new Document Generator feature. The Guidance package also contains a set of modeling rules and a draft "active validation" profile to help identify common errors or missing data in the model. Figure 23 shows the structure of the included modeling rules, intended to keep the model standardized and to prevent common errors. Each of these rules is included in the Rules table with text descriptions. These are not mandatory to follow and these are only draft requirements created by the author. A wider conversation is required to establish modeling standards at AFIT, so these are just ideas to explore at a later date. (p. 61)

[Figure 22.](../../../pdfs/citation-reports/citation-report-1691/figure_022.png) Guidance (p. 61)

[Figure 23.](../../../pdfs/citation-reports/citation-report-1691/figure_023.png) Modeling Rules (p. 62)

The Analysis portion is how teams show that their requirements are verified and how they track any external analysis done to generate requirements. Figure 41 shows the top level organizational structure. As is the case throughout this Reference Architecture, many of the included packages are hyperlinked to more detailed diagrams. (pp. 81-82)

The Trade Studies package is a place to store any applicable trade studies in block form. This allows for requirements to be traced to any relevant analysis done in other tools. For example, if a team performed a Launch Vehicle Trade Study that ultimately impacted a requirement, that requirement could be traced to the Launch Vehicle Trade Study block, which includes the most current trade study as an attachment. This makes it very easy to know exactly where the numbers or decisions came from and stores that in the model for easy reference and modification from the team. (p. 82)

[Figure 41.](../../../pdfs/citation-reports/citation-report-1691/figure_037.png) Analysis Organization (p. 83)

The Verification Analysis package contains several templates or patterns that highlight some capabilities of Cameo for requirement verification. For example, the Thermal Analysis parametric diagram in Figure 42 shows how to use a MATLAB script to perform analysis based off the values entered in the thermal subsystem, as well as any other values that affect these calculations, such as the CubeSat's mass and some orbital parameters. The code in Figure 42 is not necessary to read in this thesis, and is usually hidden from view when scripts become lengthy, but is shown here just to highlight where the code is stored. (pp. 83-84)

[Figure 42.](../../../pdfs/citation-reports/citation-report-1691/figure_038.png) Thermal Analysis (p. 85)

Figure 43. Thermal Analysis Instance (p. 86)

[Figure 44.](../../../pdfs/citation-reports/citation-report-1691/figure_039.png) Thermal Analysis Run (p. 87)

Before teams begin testing physical hardware though, they need to document their test plans. The Hardware Tests package includes workspaces for each subsystem that establishes consistency and makes it easier to generate the necessary tables to describe test activities. (p. 88)

Each requirement should be tied to a test (sometimes multiple requirements can be verified by one test), and this can be done in diagram form. For example, if the Electrical Power System (EPS) lead needs to plan EPS testing activities, they can open up the EPS Tests bdd and follow the template process. (p. 88)

Finally, the test activity tables provide a place to textually describe what happens in each test to verify the requirement(s). These tables are all useful for the Test Plans and Test Reports, keeping the model as the primary document instead of different files and formats for each subsystem. The subsystem requirement tables in this section also include a method for tracking testing progress while also establishing a common set of definitions. (p. 88)

[Figure 45.](../../../pdfs/citation-reports/citation-report-1691/figure_040.png) EPS Tests (p. 89)

[Figure 46.](../../../pdfs/citation-reports/citation-report-1691/figure_041.png) EPS Test Verification (p. 89)

There are also some gaps in the Reference Architecture that can be tackled by other researchers in the future. For example, this current iteration focuses on verifying subsystem level requirements with hardware tests, but most mission level or system requirements are not properly accounted for. This was due to the specific requirements of the Spacecraft Design Sequence at AFIT, but additional functionality can be built in to verify requirements at the mission or system level for teams who have a need for that information. (p. 105)

## RQ3-1.2

MBSE requires a modeling language, a modeling method, and a modeling tool [11]. In this thesis, those are respectively the Systems Modeling Language (SysML), the Object-Oriented Systems Engineering Method (OOSEM), and the Cameo Systems Modeler tool. (p. 31)

SysML is a standard modeling language, which added systems engineering functionality to the Unified Modeling Language (UML) that has been used extensively in Software Engineering for decades [11]. SysML provides a language, or the definitions and notations for nine different diagram types to describe a complex system, many of which will be used in this Reference Architecture. (p. 31)

The Verification Analysis package contains several templates or patterns that highlight some capabilities of Cameo for requirement verification. For example, the Thermal Analysis parametric diagram in Figure 42 shows how to use a MATLAB script to perform analysis based off the values entered in the thermal subsystem, as well as any other values that affect these calculations, such as the CubeSat's mass and some orbital parameters. (p. 83)

This research used the Object Oriented Systems Engineering Method with SysML to create a CubeSat Reference Architecture. (p. 105)

## RQ3-2

The Guidance package also contains a set of modeling rules and a draft "active validation" profile to help identify common errors or missing data in the model. Figure 23 shows the structure of the included modeling rules, intended to keep the model standardized and to prevent common errors. Each of these rules is included in the Rules table with text descriptions. (p. 61)

[Figure 23.](../../../pdfs/citation-reports/citation-report-1691/figure_023.png) Modeling Rules (p. 62)

The remaining sections within the Requirements package will be completed later in the design sequence. It is structured using a tiered Requirements convention, where teams start by generating a list of Mission Requirements, then a list of System or Space Vehicle Requirements, and finally a list of Subsystem Requirements for each subsystem. Each tier is organized in a similar fashion, but with different stereotypes and some different data fields. Additionally, template requirements for each tier have been provided, as well as some example entries in other data fields to show as examples, as shown in Figure 29. Each tier of requirements also comes with a traceability matrix for users to trace or derive that tier from. Note that the Subsystem Requirements table, shown in Figure 30, is further broken out into subsystem categories, with template requirements for each to get teams started on the brainstorming process. (pp. 68-69)

[Figure 30.](../../../pdfs/citation-reports/citation-report-1691/citation-report-1691.pdf#page=70) Subsystem Requirements (p. 70)

The Analysis portion is how teams show that their requirements are verified and how they track any external analysis done to generate requirements. Figure 41 shows the top level organizational structure. As is the case throughout this Reference Architecture, many of the included packages are hyperlinked to more detailed diagrams. (pp. 81-82)

[Figure 41.](../../../pdfs/citation-reports/citation-report-1691/figure_037.png) Analysis Organization (p. 83)

The Verification Analysis package contains several templates or patterns that highlight some capabilities of Cameo for requirement verification. For example, the Thermal Analysis parametric diagram in Figure 42 shows how to use a MATLAB script to perform analysis based off the values entered in the thermal subsystem, as well as any other values that affect these calculations, such as the CubeSat's mass and some orbital parameters. The code in Figure 42 is not necessary to read in this thesis, and is usually hidden from view when scripts become lengthy, but is shown here just to highlight where the code is stored. (pp. 83-84)

This section is intended to encourage teams to perform analysis within the model instead of in other tools. By performing analysis within the model, easy verification of candidate systems can be accomplished using Instance Tables or the default values assigned to component value properties. The CubeSat Reference Architecture purposefully does not include default values for the components' value properties, but an instance table, such as the one in Figure 43, can be simulated using the MATLAB code to compare how different candidate systems perform. This instance was simulated, and the results are shown in Figure 44. By changing one or several value properties in the relevant blocks or in the instance table, these graphs automatically update to show how the performance changes. This is extremely useful for many requirements that are affected by multiple subsystems or multiple components. A constraint block can be created that uses those value properties as inputs, and the performance outputs can be quickly assessed in multiple system configurations. (p. 84)

[Figure 42.](../../../pdfs/citation-reports/citation-report-1691/figure_038.png) Thermal Analysis (p. 85)

[Figure 43.](../../../pdfs/citation-reports/citation-report-1691/citation-report-1691.pdf#page=86) Thermal Analysis Instance (p. 86)

[Figure 44.](../../../pdfs/citation-reports/citation-report-1691/figure_039.png) Thermal Analysis Run (p. 87)

Each requirement should be tied to a test (sometimes multiple requirements can be verified by one test), and this can be done in diagram form. For example, if the Electrical Power System (EPS) lead needs to plan EPS testing activities, they can open up the EPS Tests bdd and follow the template process. If they drag and drop all of the applicable subsystem requirements onto this diagram, as shown in Figure 45, they can easily create test activities and assign a "verify" relationship between them, which automatically populates the included tables. In this example, notice the "Weigh Components" test, and that test verifies the EPS Subsystem Mass requirement. This pattern should be continued until each requirement is verified by some activity. (p. 88)

Finally, the test activity tables provide a place to textually describe what happens in each test to verify the requirement(s). These tables are all useful for the Test Plans and Test Reports, keeping the model as the primary document instead of different files and formats for each subsystem. The subsystem requirement tables in this section also include a method for tracking testing progress while also establishing a common set of definitions. Previously, tests that were "not verified" for whatever reason were all in one category, causing confusion amongst stakeholders. Now, tests can be labeled from a drop-down menu as "not verified" for the specific reason and they are labeled in a color to bring attention to problematic tests. Figure 46 shows an example of how this could be used. The Verification Status legend is located in the Component Library and can be modified if definitions or categories change. (p. 88)

[Figure 45.](../../../pdfs/citation-reports/citation-report-1691/figure_040.png) EPS Tests (p. 89)

[Figure 46.](../../../pdfs/citation-reports/citation-report-1691/figure_041.png) EPS Test Verification (p. 89)

## RQ3-2.2

MBSE requires a modeling language, a modeling method, and a modeling tool [11]. In this thesis, those are respectively the Systems Modeling Language (SysML), the Object-Oriented Systems Engineering Method (OOSEM), and the Cameo Systems Modeler tool. (p. 31)

SysML is a standard modeling language, which added systems engineering functionality to the Unified Modeling Language (UML) that has been used extensively in Software Engineering for decades [11]. SysML provides a language, or the definitions and notations for nine different diagram types to describe a complex system, many of which will be used in this Reference Architecture. SysML is expressed graphically through those diagrams, listed in Figure 8, to show various system viewpoints. For example, a Block Definition Diagram (bdd) expresses system structure, and an Activity Diagram can show specific system activities. Within "blocks", further detail can be expressed on an Internal Block Diagram (ibd). (pp. 31-32)

The Verification Analysis package contains several templates or patterns that highlight some capabilities of Cameo for requirement verification. For example, the Thermal Analysis parametric diagram in Figure 42 shows how to use a MATLAB script to perform analysis based off the values entered in the thermal subsystem, as well as any other values that affect these calculations, such as the CubeSat's mass and some orbital parameters. (p. 83)

[Figure 8.](../../../pdfs/citation-reports/citation-report-1691/figure_009.png) SysML Taxonomy (p. 32)

[Figure 42.](../../../pdfs/citation-reports/citation-report-1691/figure_038.png) Thermal Analysis (p. 85)

## RQ3-3

5. Optimize and Evaluate Alternatives: Trade studies or other analysis is conducted at this step among the candidate architectures. Parametric diagrams within the model or integrating other tools can simulate system performance with the chosen components so alternative solutions can be compared. (p. 34)

6. Validate and Verify System: Once a candidate architecture has been chosen from the alternatives, the system needs to be validated and verified to ensure the requirements are being met and that stakeholder needs are satisfied. This step uses inspection, demonstration, analysis, and test activities to validate and verify the system. (p. 34)

At AFIT, the first course starts with teams given a Mission Capabilities Document (MCD) for a fictional or real mission, which outlines the "Mission Need Statement," "Operational Context," and a set of required capabilities and design constraints. From this set of inputs, students develop stakeholder concerns and needs, perform trade studies, write a Concept of Operations (CONOPS), and finally develop a set of mission requirements. These artifacts are carried into the next course, where system level requirements are defined and a physical structure is designed. Finally, in the third course, students take those system-level requirements and further define subsystem-level requirements and develop test plans to verify those requirements. These courses are intended to flow together, and this Reference Architecture will help by providing the model framework to carry between and support all three courses. Throughout the course sequence, there are also milestone reviews and stakeholder documentation requirements to fulfill. (pp. 49-50)

In addition to the modeling rules provided, a pared down version of SAIC's DE Validation Profile [28] is provided as well. As discussed in section 2.6, the Validation Profile does not meet the needs or practices of this model's intended audience, but there were several helpful active validation rules that were borrowed. A future effort may explore this concept further, but for now, roughly a third of the supplied rules were helpful for this context. Some very helpful rules include those that highlight when a requirement does not have proper traceability or is missing requirement text, rules that highlight missing elements in diagrams (such as starting and final nodes in activity diagrams), and a rule that checks to make sure each Value Property has an associated Value Type and Unit. If a modeler runs the validation profile during the design process, they may see helpful errors pointing out missing elements, so it does add some value to the Reference Architecture. (pp. 62-63)

This section is intended to encourage teams to perform analysis within the model instead of in other tools. By performing analysis within the model, easy verification of candidate systems can be accomplished using Instance Tables or the default values assigned to component value properties. The CubeSat Reference Architecture purposefully does not include default values for the components' value properties, but an instance table, such as the one in Figure 43, can be simulated using the MATLAB code to compare how different candidate systems perform. This instance was simulated, and the results are shown in Figure 44. By changing one or several value properties in the relevant blocks or in the instance table, these graphs automatically update to show how the performance changes. This is extremely useful for many requirements that are affected by multiple subsystems or multiple components. A constraint block can be created that uses those value properties as inputs, and the performance outputs can be quickly assessed in multiple system configurations. The included parametric diagrams serve as patterns to replicate and modify, reducing the learning curve for teams who haven't learned these capabilities yet. (p. 84)

Before teams begin testing physical hardware though, they need to document their test plans. The Hardware Tests package includes workspaces for each subsystem that establishes consistency and makes it easier to generate the necessary tables to describe test activities. Each requirement should be tied to a test (sometimes multiple requirements can be verified by one test), and this can be done in diagram form. For example, if the Electrical Power System (EPS) lead needs to plan EPS testing activities, they can open up the EPS Tests bdd and follow the template process. If they drag and drop all of the applicable subsystem requirements onto this diagram, as shown in Figure 45, they can easily create test activities and assign a "verify" relationship between them, which automatically populates the included tables. In this example, notice the "Weigh Components" test, and that test verifies the EPS Subsystem Mass requirement. This pattern should be continued until each requirement is verified by some activity. (p. 88)

Finally, the test activity tables provide a place to textually describe what happens in each test to verify the requirement(s). These tables are all useful for the Test Plans and Test Reports, keeping the model as the primary document instead of different files and formats for each subsystem. The subsystem requirement tables in this section also include a method for tracking testing progress while also establishing a common set of definitions. Previously, tests that were "not verified" for whatever reason were all in one category, causing confusion amongst stakeholders. Now, tests can be labeled from a drop-down menu as "not verified" for the specific reason and they are labeled in a color to bring attention to problematic tests. Figure 46 shows an example of how this could be used. The Verification Status legend is located in the Component Library and can be modified if definitions or categories change. (p. 88)

A team could swap out multiple solar arrays from the Component Library in their EPS subsystem diagram and perform analysis to quickly assess how each one performs for their system. (p. 90)

There are also some gaps in the Reference Architecture that can be tackled by other researchers in the future. For example, this current iteration focuses on verifying subsystem level requirements with hardware tests, but most mission level or system requirements are not properly accounted for. This was due to the specific requirements of the Spacecraft Design Sequence at AFIT, but additional functionality can be built in to verify requirements at the mission or system level for teams who have a need for that information. (p. 105)

## RQ3-3.1

MBSE requires a modeling language, a modeling method, and a modeling tool [11]. In this thesis, those are respectively the Systems Modeling Language (SysML), the Object-Oriented Systems Engineering Method (OOSEM), and the Cameo Systems Modeler tool. (p. 31)

OOSEM uses SysML in a top-down, model-based approach that leverages object-oriented concepts with traditional systems engineering methods to architect more flexible and extensible systems that can evolve with technology and changing requirements [14]. OOSEM was developed in part by Lockheed Martin Corporation as a method to capture and analyze requirements of complex systems, integrate with object-oriented software and hardware, and support system-level reuse and design evolution [15]. (pp. 32-33)

The Verification Analysis package contains several templates or patterns that highlight some capabilities of Cameo for requirement verification. For example, the Thermal Analysis parametric diagram in Figure 42 shows how to use a MATLAB script to perform analysis based off the values entered in the thermal subsystem, as well as any other values that affect these calculations, such as the CubeSat's mass and some orbital parameters. (p. 83)

This research used the Object Oriented Systems Engineering Method with SysML to create a CubeSat Reference Architecture. (p. 105)
