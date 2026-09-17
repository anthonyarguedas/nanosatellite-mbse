---
source: null
title: "citation-candidate-1412"
candidate_id: "citation-candidate-1412"
publication_year: 2022
converted_at: "2026-09-15"
---

# Development of Operations Complement to the Space System Ontology (Luleå University of Technology, Space Technology, 2022)

Authors: K. Tiensuu

<!-- PDF_PAGE: 1 -->

Development of Operations Complement
     to the Space System Ontology




                           Kiira Tiensuu



        Space Engineering, master's level (120 credits)
                            2022

                      Luleå University of Technology
       Department of Computer Science, Electrical and Space Engineering

<!-- PDF_PAGE: 2 -->

Master’s Thesis

Development of Operations Complement to
       the Space System Ontology




Author:           Kiira Tiensuu

Date:             15th of September 2022

Examiner:         René Laufer (Luleå University of Technology)
1st Supervisor:   Alex Vorobiev (RHEA Group)
2nd Supervisor:   Sam Gerené (RHEA Group)

<!-- PDF_PAGE: 4 -->

i


Abstract
Space system development is a complex process that typically involves multiple stake-
holders. Traditionally, information is captured and exchanged in the form of documents.
Efficient exchange of information is crucial, but often challenging with the traditional
document-based approach and multitude of stakeholders. In addition to the challenges in
information exchange, currently these is also pressure on the cost and schedule require-
ments of space projects. European Space Agency (ESA) proposes digitalisation as one
of the solutions to these challenges, and more specifically, a transition from document
based-approach to model-based. ESA’s vision is to implement digitalisation in the form
of an infrastructure to support MBSE processes, named the System Factory. This System
Factory needs a centralised data hub that provides interoperability between different stake-
holders and tools used throughout space system development life cycle. The purpose of
the hub is also to allow the stakeholders to exchange information using common semantics,
described in the space system ontology (SSO).
Model-Based Engineering Hub (MBEH) is an ESA project, implemented by RHEA Group,
Thales Alenia Space, OHB and DEKonsult. The overall objectives of the project are to
scope the MBSE hub, provide a technical solution for it and demonstrate its functionality
with two use cases. The selected use cases are exchanges between operations (OPS) and
systems engineering (ENG) domains, and reliability, availability, maintainability and safety
(RAMS) and systems engineering domains. The objective of this thesis is to develop a
conceptual data model (CDM) of the operations use case to support the MBEH project.
The CDM was developed in two phases. The first task was to analyse and complement the
exchanges related to the chosen operations use case based on the European Cooperation for
Space Standardization (ECSS) standards. This written analysis was then used as a starting
point for modelling, which was the second task. The modelling was performed using the
Object Role Modeling (ORM) language and Natural ORM Architect (NORMA) tool. The
models are created based on information from OHB and the ECSS standards. The next
step in the MBEH project is to harmonise these models with the European Ground Systems
Common Core (EGS-CC) and existing ontologies, which were not available for this thesis
project.

<!-- PDF_PAGE: 5 -->

ii


Acknowledgements
This thesis was written during an internship at RHEA Group. During the six months, I
acquired a great amount of knowledge about model-based systems engineering and con-
current design. I would like to thank RHEA Group and the MBSE competence group for
the opportunity, and specifically Alex Vorobiev and Sam Gerené for the supervision. In
addition, I would like to express my gratitude to my colleague Paloma Maestro Redondo
for all the guidance, especially in the beginning of my internship, and Nieves Salor Moral
for the introduction to object-role modelling and all the valuable comments on the thesis.
It has been a privilege to work with the state-of-the art of model-based systems engineering
and concurrent design tools, and I hope that I get to use them in future projects.
From Luleå University of Technology, I would like to thank René Laufer for the examination
of this thesis. In addition, many thanks to Victoria Barabash and the administrative staff
of the SpaceMaster program for putting so much dedication into the program and helping
the students to thrive. Lastly, I would like to thank my family and friends, in Kiruna and
far away, for their continuous support.

<!-- PDF_PAGE: 6 -->

Contents                                                                                  iii


Contents
List of Figures                                                                           iv

List of Tables                                                                            iv

List of Abbreviations                                                                     v

1 Introduction                                                                            1
  1.1 Background . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    1
  1.2 Model-Based Engineering Hub . . . . . . . . . . . . . . . . . . . . . . . . .       2
  1.3 Objectives and Outline of the Thesis . . . . . . . . . . . . . . . . . . . . .      3

2 Theory                                                                                   5
  2.1 Model-Based Systems Engineering . . . . . . . . . . . . . . . . . . . . . . .        5
  2.2 Space System Ontology . . . . . . . . . . . . . . . . . . . . . . . . . . . . .      9
  2.3 Space System Operations and EGS-CC . . . . . . . . . . . . . . . . . . . .          10

3 Methodology                                                                             14
  3.1 Analysis of the Exchanges . . . . . . . . . . . . . . . . . . . . . . . . . . .     14
  3.2 Modelling . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   15

4 Definition of Exchanges                                                                 20
  4.1 Operations Use Cases . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    20
  4.2 Selected Use Case: Flight Operations Procedure (FOP) . . . . . . . . . . .          20
  4.3 Process of Developing FOP With MBSE Hub . . . . . . . . . . . . . . . .             32

5 ORM Models                                                                              35

6 Conclusions and Outlook                                                                 55

References                                                                                56

<!-- PDF_PAGE: 7 -->

List of Tables                                                                                 iv


List of Figures
   1.1  System Factory high level functions. . . . . . . . . . . . . . . . . . . . . . .        2
   1.2  System Factory high level functions with a centralised data hub. . . . . . .            3
   2.1  Traditional systems engineering compared to model-based systems engineer-
        ing. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    7
   2.2 The EGS-CC design in three main layers. . . . . . . . . . . . . . . . . . . .           11
   2.3 Space system represented in the EGS-CC Monitoring & Control Model. . .                  12
   3.1 Main components of the NORMA tool. . . . . . . . . . . . . . . . . . . . .              16
   4.1 Procedure bodies. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .       23
   4.2 Use case diagram representing the development process of flight operations
        procedure with MBSE hub. . . . . . . . . . . . . . . . . . . . . . . . . . .           34
   5.1 ORM model: Space System Model. . . . . . . . . . . . . . . . . . . . . . .              36
   5.2 ORM model: System Element. . . . . . . . . . . . . . . . . . . . . . . . . .            37
   5.3 ORM model: Activity. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .          38
   5.4 ORM model: Activity Argument. . . . . . . . . . . . . . . . . . . . . . . .             40
   5.5 ORM model: Event. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .           41
   5.6 ORM model: Reporting Data. . . . . . . . . . . . . . . . . . . . . . . . . .            43
   5.7 ORM model: Parameter. . . . . . . . . . . . . . . . . . . . . . . . . . . . .           44
   5.8 ORM model: Procedure. . . . . . . . . . . . . . . . . . . . . . . . . . . . .           46
   5.9 ORM model: Body. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .          48
   5.10 ORM model: Step. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .         50
   5.11 ORM model: Telecommand. . . . . . . . . . . . . . . . . . . . . . . . . . .            52
   5.12 ORM model: PUS service. . . . . . . . . . . . . . . . . . . . . . . . . . . .          53


List of Tables
   3.1   Graphical notation of the UML use case diagrams. . . . . . . . . . . . . . .          15
   3.2   Graphical notation of Object-Role Modelling. . . . . . . . . . . . . . . . .          17
   4.1   Exchanges involved in the flight operations procedure use case. . . . . . . .         24
   4.2   Actors involved in the development and exchange of flight operations pro-
         cedures. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    33

<!-- PDF_PAGE: 8 -->

List of Abbreviations                                               v


List of Abbreviations
 AIT        Assembly, Integration and Testing

 CDF        Concurrent Design Facility
 CDM        Conceptual Data Model
 ConOps     Concept of Operations
 CPDU       Command Pulse Distribution Unit

 ECSS       European Cooperation for Space Standardization
 EGS-CC     European Ground Systems Common Core
 EGSE       Electrical Ground Support Equipment
 ENG        Systems Engineering
 ESA        European Space Agency
 ESOC       European Space Operation Center

 FOP        Flight Operations Procedure

 INCOSE     International Council on Systems Engineering

 MB4SE      Model Based 4(for) System Engineering
 MBEH       Model-Based Engineering Hub
 MBSE       Model-Based Systems Engineering
 MCM        Monitoring & Control Model
 MCS        Mission Control System
 MRS        Mars Sample Return

 NASA       National Aeronautics and Space Administration
 NORMA      Natural ORM Architect

 OMG    Object Management Group
 OPEN   Operations Preparation Environment framework
 OPEN-M Preparation Environment for Flight Control Team
 OPS    Operations
 ORM    Object Role Modelling
 OSMoSE Overall Semantic Modelling for System Engineering

 PUS        Packet Utilization Standard

 RAMS       Reliability, Availability, Maintainability and Safety

 SoW        Statement of Work

<!-- PDF_PAGE: 9 -->

List of Abbreviations                  vi


 SSO   Space System Ontology
 SysML System Modeling Language

 TC       Telecommand
 TM       Telemetry

 UC       Uniqueness Constraint
 UML      Unified Modelling Language

 XML      Extensible Markup Language

<!-- PDF_PAGE: 10 -->

1 Introduction                                                                             1


1     Introduction
1.1     Background
Space system development is a complex process that requires knowledge from multiple
domains of expertise. Traditionally, information is captured and exchanged in the form
of documents. When a project has many stakeholders and involves different domains of
expertise, efficient and effective exchange of information is challenging. Document-based
approach is problematic especially if all parties involved do not have the same semantic
understanding of the information exchanged. There is a need to facilitate the exchange of
information and collaboration throughout the space system life cycle [1]. In addition, there
is pressure on the cost and schedule requirements of space projects. In fact, in its 2019
Technology Strategy, European Space Agency (ESA) listed four main goals, including
30% improvement of spacecraft development time by 2023 and one order of magnitude
improvement of cost efficiency with every generation [2].
ESA proposes digitalisation as one of the solutions to these challenges. The Agency defines
digitalisation as ”the process of transforming the artefacts of space systems into a (struc-
tured) digital representation on which computers can elaborate” [3]. It could mean, for
example, a transition from document-based development process to model-based. In the
model-based methodology, information, such as design, requirements, and analysis from
different domains of expertise, is expressed in a set of data structured into one or multiple
correlated models, instead of documents [3].
ESA’s vision is to implement digitalisation in the form of a System Factory, which is ba-
sically an infrastructure to support Model-Based Systems Engineering (MBSE) processes.
There are three general needs that the System Factory is expected to answer. Firstly,
to streamline the space system development process, i.e., shorten the development time
and reduce costs of space projects. Secondly, to manage the increasing complexity of space
missions. Thirdly, to offer process guidance and automation to support the development of
European Cooperation for Space Standardization (ECSS) [4] compliant space systems [1].
The System Factory requirements document [1] identifies the following four main functions
as the cornerstones of the infrastructure:
    1. Data sources. Tools that engineers from different domains of expertise use to create
       and manage design and architectural information.
    2. Analysis. Tools that are used for analyses, such as trade-off, design validation, and
       creation of engineering budgets.
    3. Engineering workflows. System and subsystem level processes that are part of the
       development process, such as design, production, verification and operation.
    4. Data consumers. Entities and tools that produce documents, reports and dashboards
       used for visualisation and communication of the engineering data.

<!-- PDF_PAGE: 11 -->

1 Introduction                                                                            2




                   Figure 1.1: System Factory high level functions [1].

These high level functions are presented in Figure 1.1. There are many tools used in
model-based activities in different engineering disciplines but the exchange of information
is typically done by manual processes, which has the disadvantages of work duplication,
low automation and lack of data normalisation [1].
A centralised hub that provides interoperability between the different stakeholders and
tools is needed. The hub will be used by different levels and disciplines of space engineer-
ing, as well as throughout different phases of a project, and it shall allow stakeholders to
exchange information using a common semantics, described in the Space System Ontology
(SSO). In addition to providing interoperability, the hub needs to support auxiliary pro-
cesses, such as authentication, authorisation, configuration control and enforcing correct
workflows [5]. The System Factory infrastructure with the centralised hub is presented in
Figure 1.2.

1.2    Model-Based Engineering Hub
The Model-Based Engineering Hub (MBEH) is an ESA project, implemented by RHEA
Group, OHB and Thales Alenia Space. DEKonsult is providing consultation throughout
the execution of the activity. The project started in October 2021, and the overall ob-
jectives are to scope the MBSE hub, provide a technical solution for it and demonstrate
its functionality with two use cases. Correct exchanges shall be demonstrated between
Operations (OPS) and Systems Engineering (ENG) domains and Reliability, Availabil-
ity, Maintainability and Safety (RAMS) and ENG domains. In addition to the technical
solution for the hub, the purpose is to complement OPS and RAMS parts of the SSO [5].

<!-- PDF_PAGE: 12 -->

1 Introduction                                                                            3




      Figure 1.2: System Factory high level functions with a centralised data hub [1].


The MBEH project is divided in two phases. The first phase is ”Scoping”, and it has the
following objectives according to the project Statement of Work (SoW) [5]:
 1.1 Produce a technical specification for the MBSE hub.
 1.2 Elaborate on the relevant information exchanged between OPS-ENG and RAMS-
     ENG throughout a space system project.
After successful completion of the first phase, the project proceeds to the second phase,
which is ”Development and Demonstration”. The second phase has the following objec-
tives:
 2.1 Provide a technical solution for the MBSE hub.
 2.2 Extend the ontology received from ESA as input with information that is needed to
     support the demonstration of the OPS-ENG and RAMS-ENG information exchanges.
 2.3 Demonstrate the MBSE hub operation with the two use cases.

1.3     Objectives and Outline of the Thesis
The objective for this thesis is to support the project objectives 1.2 and 2.2 by developing
a Conceptual Data Model (CDM) of the Operations use case. The CDM developed during
this thesis work will be created based on the needs of OHB. In practise, the work will
entail:

<!-- PDF_PAGE: 13 -->

1 Introduction                                                                           4


   • Conducting a literature review on MBSE, SSO and space system operations focusing
     on the European space industry.
   • Analysing the technical note on the OPS exchanges provided by OHB and defining
     the relevant exchanges and the interconnections to other exchanges.
   • Creating use case diagram of the selected OPS use case to identify the expected
     functions of the MBSE hub.
   • Creating models of the OPS exchanges using the Object Role Modelling (ORM)
     language.
The thesis is structured as follows: The important terms and concepts are established
in Section 2, including MBSE, SSO and space system operations and European Ground
Systems Common Core (EGS-CC). The selected methods and tools are explained in Sec-
tion 3, including how the analysis is performed and how the use case diagram is created.
Descriptions of the ORM language and the Natural ORM Architect (NORMA) tool that
are used for the modelling are also presented. The results of the analysis are presented in
Section 4, focusing on the selected OPS use case. The resulting ORM models are presented
in Section 5. Finally, the conclusions and outlook are presented in Section 6.

<!-- PDF_PAGE: 14 -->

2 Theory                                                                                                  5


2         Theory
2.1        Model-Based Systems Engineering
In the traditional document-based approach, information is captured in documents. These
include, for example, system description documents, trade-off analyses, specifications,
interface control documents, verification plans, analysis reports, Concept of Operations
(ConOps) and different procedures [6]. The document-based approach has the following
drawbacks [6, 7]:
        • It is challenging to achieve effective communication in projects with multiple stake-
          holders, and problems may arise if the stakeholders have different semantic under-
          standing of the information exchanged.
        • There is no efficient way to express dependencies. Typically, a change in one com-
          ponent needs to be reflected manually in other affected components/systems in the
          documentation.
        • Creating and maintaining documents is time consuming and prone to error due to
          manual work.
        • With space systems of high complexity, the risk of information getting lost or not
          being updated, and the risk of overlooking critical information are high.
        • It is difficult to verify completeness and consistency of documents and catch issues
          or contradicting information.
International Council on Systems Engineering (INCOSE) defines MBSE as “the formalised
application of modelling to support system requirements, design, analysis, verification and
validation activities beginning in the conceptual design phase and continuing throughout
the development and later life cycle phases” [6]. Model is essentially a representation of
the system that integrates inputs from different domains of expertise, capturing the system
architecture and its behaviour. The purpose of the model is to function as the “single source
of truth” of the system that is being developed. In the beginning of the development
process, the model is typically an abstract representation of the system, but it evolves and
becomes more concrete during the system’s life cycle when details are incrementally added
to it [7].
Different languages and tools have been developed for modelling, such as the System Mod-
eling Language (SysML) by Object Management Group (OMG) [8]. SysML is supported
by various tools, such as Enterprise Architect by Sparx Systems [9] and Cameo Systems
Modeler developed by No Magic [10] 1 . In addition, there is an open source solution called
Capella 2 [11], which can be used, for example, to formalise complex architectural designs,
    1
     For at least one of these tools, an adapter will be developed that supports the transfer of information
from the tool into the MBSE hub.
   2
     Capella will also be supported by the MBSE hub.

<!-- PDF_PAGE: 15 -->

2 Theory                                                                                      6


evaluate and justify architectural choices, and to prepare for validation and verification [12].
Comparison of traditional systems engineering and model-based systems engineering ap-
proaches is presented in Figure 2.1. Due to the improved information exchange and ability
to analyse and manage the information, MBSE has the following benefits compared to
traditional document-based approach [6]:
   • Improved communication and data exchange between stakeholders.
   • Managing system complexity is easier since it is possible to view the model from
     multiple perspectives and analyse how changes impact the system design.
   • Better quality results due to unambiguous model of the system and the possibility
     to evaluate that model for correctness, completeness and consistency.
   • Possibility to reuse information since the information is exchanged in a more stan-
     dardised manner and in a digital format.
   • Lower risk and cost of the system development since potential issues are noticed more
     easily and earlier in the process.
   • Potentially reduced project time.
However, the transition from the traditional document-based approach to MBSE requires
an investment in tools, security, infrastructure and the training of personnel, since the way
of thinking, tools and needed skills differ from the document-based approach [14]. Due to
the greater upfront investment, MBSE is not the most optimal approach for all projects.
Industry sectors with high environment complexity, system complexity and long lifespan
of the system benefit most of the adaptation of the approach economically. These kinds of
industry sectors are, for example, aerospace, defence, energy and transportation [13].
Younse et al. [15] performed a quantitative analysis on the benefits of using MBSE com-
pared to traditional systems engineering approaches. In the study, a robotic space system
was architected by both an MBSE approach and non-MBSE approach. The architected
system was the orbiting sample Capture and Orient Module (COM) for Capture, Con-
tainment, and Return System (CCRS) payload of the Mars Sample Return (MSR), and
the study was performed at the Jet Propulsion Laboratory of California Institute of Tech-
nology under contract from National Aeronautics and Space Administration (NASA). It
was found out that in the non-MBSE approach, there were 4858 information transfers that
were all done manually. In the MBSE approach, 630 of them (13%) were done automati-
cally. It was also predicted that the level of automation could be increased up to 81% by,
for example, further utilising MBSE in trade-off studies and reviews. The importance of
further developing MBSE tools and increasing the level of automation was highlighted. It
was also pointed out that further research on the topic is needed, including for example, a
study testing the methodology with two separate research teams to make sure the decision
making in both approaches remain decoupled [15].

<!-- PDF_PAGE: 16 -->

2 Theory                                                                              7




Figure 2.1: Traditional systems engineering compared to model-based systems engineering.
The figure is adapted from [13].

<!-- PDF_PAGE: 17 -->

2 Theory                                                                                   8


MBSE is constantly evolving and currently being adopted for more and more use cases,
which can also be seen in the European space industry. There are examples from different
phases of the space system life cycle where MBSE methods have been adopted [16]. In phase
03 , ESA uses MBSE tools for concurrent engineering activities in the Concurrent Design
Facility (CDF) [18]. The tools used at theCDF are based on the Technical Memorandum
ECSS-E-TM-E-10-25A [19], which is a standard for model-based data exchange developed
by ESA. The Technical Memorandum has been created to facilitate and promote definition
and exchange of data between agencies and European space industry, and it covers phases
0 and A. The model-based and ECSS-E-TM-E-10-25A compliant tool that is currently
being used at the ESA CDF is COMET, which is an open source concurrent engineering
tool developed by RHEA Group [20].
In the mission definition and early design phases (phases A and B1), MBSE has been
utilised, for example, in the ESA e.Derobit mission design [21]. The phase 0 study was
performed at ESA CDF [22], after which ESA awarded three industrial contracts for phase
A of the mission. The contractors, Airbus Defence and Space, OHB and Thales Alenia
Space, were requested to use MBSE, but the selection of methodology and tools was left to
the contractors. Key lessons learned from this project were that there is a need to harmonise
the data exchange processes and interfaces, as well as data models. In addition, conducting
reviews with models required considerable learning from the external experts [16]. Airbus
and OHB continued to develop the mission further in phase B1 using MBSE [21].
MBSE has also been utilised in the development of ConOps for the Mars Sample Return
(MRS) mission, which is a joint effort of ESA and NASA [23, 24]. The proposed MRS
mission concept is very complex and spans over multiple phases using different vehicles,
such as the NASA Perseverance rover, sample retrieval lander, fetching rover, Mars as-
cent vehicle, and Earth return vehicle. NASA, ESA and several industry contractors are
involved in the study, and thus, this project is an example of a cross-Agency and multi-
Center use of MBSE. MBSE is used in this project to determine the campaign architecture
by developing and controlling the overall ConOps. More specifically, MBSE will be used
to provide a “single source of truth” for important systems engineering data, automate
the generation of reports and engineering documents and analysis of integrated systems
engineering data, such as requirement and risk assessments [23]. The ConOps is modelled
with SysML, and to be able to fully capture the ConOps, a language extension mechanism
is used. This mechanism is native to SysML and Unified Modelling Language (UML),
which is the language that SysML is built upon, and is described in [24].
The use of MBSE in operations ground segment engineering has been studied by ESA in
the context of the Euclid mission, which is a medium class ESA science mission currently
under development [25]. Fischer et al. [26] identified the main issues with the document-
based approach in ground segment engineering. As space segment projects, also ground
segment projects are increasing in complexity, and thus, facing similar issues with the
document-based approach. Firstly, most of the documents are living documents, making
  3
      Phases according to [17].

<!-- PDF_PAGE: 18 -->

2 Theory                                                                                    9


change management tedious, time-consuming and prone to error. This is followed by
redundancies and inconsistencies that develop over time. In addition, most documents are
written to be human-readable, while machine readability would be a desired feature in the
ground segment. Many operations ground segment engineering activities are defined in the
ECSS standards. However, in many cases it is not conceptualised how the processes are
or should be implemented. This leads to different organisations using different tools which
are not able to directly exchange data [26].

2.2    Space System Ontology
It has been recognised that a number of activities towards MBSE has been carried out
in the European space industry and ESA. However, to fully employ MBSE in the space
projects, the exchange of data needs to be possible in three dimensions, including discipline,
project phase and stakeholders. One of the current obstacles in the deployment of MBSE
is the lack of interoperability [27].
The Model Based 4(for) System Engineering (MB4SE) is an ESA initiative with the goal
to streamline systems engineering process for space programmes [3]. The purpose of the
MB4SE is to federate the space systems engineering community and to work together
towards the deployment of MBSE in the space projects taking place in Europe. This is done
by providing a platform for technical discussions and recommendations from stakeholders,
steered by the MB4SE advisory group [3]. The work of the MB4SE group was started with
five European agencies, including ESA, French Space Agency (CNES), German Space
Agency (DLR), Italian Space Agency (ASI), and the UK Space Agency (UKSA), and
three European large space integrators Airbus Defence and Space, Thales Alenia Space
and OHB [27].
In addition to the need for the digital infrastructure for systems engineering (system fac-
tory with centralised data hub), the working group has identified the need for a global
conceptual data model, an ontology. The purpose of the ontology is to ensure the needed
interoperability. To address this, the Overall Semantic Modelling for System Engineering
(OSMoSE) initiative was started under the governance of the MB4SE group. The goal
for the OSMoSE initiative is to promote addressing interoperability at semantic level, i.e.,
focusing on the customers’ needs, and then merging all those needs in a global conceptual
data model called the Space System Ontology (SSO) [3].
Madni and Sievers [7] define ontology as follows: ”An ontology is a formal explicit con-
ceptualisation of a problem domain shared by stakeholders, which presents a controlled
vocabulary that comprises a set of agreed upon terms (semantic domain) and rules for
using and interpreting them within the domain. Terms and relationships in the controlled
vocabulary are explicitly enumerated, unambiguous, non-redundant, and managed by a
controlling authority.”. The SSO is a conceptual model that captures the semantics of
space systems engineering. The scope of SSO is limited to what is exchanged, it does
not cover how the exchange is performed or how the data is stored. It is meant to cover

<!-- PDF_PAGE: 19 -->

2 Theory                                                                                     10


space, ground operations and launchers during all phases of the space system life cycle,
and initially the focus is on the engineering data [3].
The SSO consists of various universes of discourse, which ESA is currently developing with
partners by using ORM [28, 29]. In the MBEH project, the purpose is to extend the
SSO with the OPS and RAMS universes of discourse. To make use of the advantages of
ontologies, they should be:
   • Complete, to make sure all areas of development are covered.
   • Unambiguous, to avoid misinterpretations.
   • Intuitive, to cover concepts that are familiar to users’ domain.
   • Generic, to allow the usage of the ontology in various contexts.
   • Extendable, to allow addition of new concepts.
These features should be considered when extending the SSO with the OPS and RAMS
universes of discourse. Specifically, extensibility is considered an important feature for
space projects, and also in the OPS and RAMS domains, to keep up with the advancements
and updates in the field.

2.3    Space System Operations and EGS-CC
According to the ECSS [30], mission operations are ”activities related to the operations
planning, execution and evaluation of the combined space segment and ground segment
during phases E and F of a space project”. Operations engineering covers multiple pro-
cesses, such as requirements analysis and concept development, mission operations data
production, mission operations data validation, operations teams build-up and training, op-
erational validation, operational configuration management, operations execution (launch
and early orbit phase, commissioning and routine phase operations) and space segment
disposal operations [30].
In Europe, there are many different systems that companies and agencies use for space
system operations and Assembly, Integration and Testing (AIT). There are often multiple
systems that are used at different levels and phases of the project and in some cases, same
systems are used for both operations and AIT. These existing systems have little synergies
across project phases, which complicates information exchange. In addition, many systems
used in Europe are using old software technologies and hardware platforms that are either
reaching their end of life or have reached it and are difficult and expensive to modernise [31].
In 2009-2010, ESA started the EGS-CC, which is a ”European initiative to develop a
common infrastructure to support space systems monitoring and control in pre- and post-
launch phases for all mission types” [31, 32]. The initiative is a collaboration between ESA,
European national space agencies and industry. The objectives of the EGS-CC initiative

<!-- PDF_PAGE: 20 -->

2 Theory                                                                                  11




                Figure 2.2: The EGS-CC design in three main layers [32].


are to provide seamless transition from spacecraft AIT to mission operations, enable over-
all cost and risk reductions by implementing projects with the use of a stable common
infrastructure, as well as enable modernisation of the legacy Electrical Ground Support
Equipment (EGSE) and Mission Control System (MCS) systems. To achieve these goals,
the system is expected to have the following features: support for all mission types and
phases, open, component based and service oriented architecture, generic and extensible
functionality, interoperability through standardised interfaces, long term maintainability,
high performance and scalability, among others [33].
The EGS-CC has a layered implementation, as illustrated in Figure 2.2. It is not a moni-
toring and control system, but rather a platform on which those systems can be built and
integrated into. It provides core monitoring and control features and application support
functionality in its kernel. The reference implementations layer contain application specific
functionalities, and works as adaptor between EGS-CC software and specific application
and mission. The reference test facilities provide external functionality that is needed to
test the EGS-CC based systems in isolation [32].
The functional core of the EGS-CC kernel is provided by Monitoring & Control Model
(MCM), which is a software component allowing the modelling of a space system from a
monitoring and control perspective. It is based on the ECSS standard E-ST-70-31C Ground
Systems and Operations – Monitoring and Control Data Definition [34], which defines how
the information is organised in a structured way to reflect the functional decomposition
of a space system. An example of how the space system is represented in the MCM is
presented in Figure 2.3. The space system knowledge is organised in a hierarchical structure
of the system elements, which can be for example, systems, subsystems or equipment. The
monitoring and control knowledge is expressed as activities, events and reporting data [32].

<!-- PDF_PAGE: 21 -->

2 Theory                                                                                   12




Figure 2.3: Space system represented in the EGS-CC Monitoring & Control Model. The
figure is adapted from [32].


Activity, event and reporting data are defined as follows in the ECSS [34, 35]:
   • Activity is a space system monitoring and control function implemented within the
     EGSE or mission control system MCS. An activity can be implemented as a telecom-
     mand either to the space segment or to the ground segment, a procedure, an operating
     system command or any other command type that is specific to a given implemen-
     tation of the space system.
   • Event is an occurrence of a condition or group of conditions of operational signifi-
     cance. Events are widely used within the space system to trigger the execution of
     functions (e.g. acquisition of signal can initiate telemetry processing tasks at the
     ground station).
   • Reporting data is information that a system element provides, irrespective of how
     this information is used. Reporting data can comprise measurements which reflect
     the state of the associated system element or an output product whose purpose is
     to be used by another system element (e.g., manoeuvre parameters provided by the
     flight dynamics system).
ESA also has an initiative called Operations Preparation Environment framework (OPEN),
which purpose is to provide an environment and software foundation for monitoring and
control preparation tools that are aligned with EGS-CC [36]. The objectives of OPEN are
to ”streamline the mission tailoring activities and enable a reduction of the required efforts
by preparation teams, provide a consistent environment where all applications related to
preparation can be hosted and avoid proliferation of heterogeneous implementations, and
to extend the support of advanced features (e.g. configuration management) to all artefacts

<!-- PDF_PAGE: 22 -->

2 Theory                                                                             13


related to mission operations, EGSE and AIT activities” [36]. In addition to the general
objectives, OPEN also has European Space Operation Center (ESOC) specific objectives
to harmonise the tools for mission and ground station operations teams, as well as to
support transition to the EGS-CC based ground data system infrastructure.

<!-- PDF_PAGE: 23 -->

3 Methodology                                                                             14


3     Methodology
3.1     Analysis of the Exchanges
During the first phase of the MBEH project, OHB and Thales Alenia Space provide infor-
mation on different use cases related to the exchanges between OPS-ENG and RAMS-ENG
domains, and then select one as the demonstration case which will be further analysed [5].
The first task in this thesis project is to analyse the technical note provided by OHB. More
specifically, the task is to:
    1. Read through the technical note provided by OHB.
    2. Explain the selected use case and describe how it is defined in the ECSS standards.
    3. List all of the exchanges that OHB considers relevant for the selected use case.
    4. Complement the list with other relevant exchanges that are needed to create a model
       of the use case.
    5. For each exchange in the list, extract the following information from the ECSS stan-
       dards:
         • How is it defined?
         • What kind of information is related to it?
         • What connections does it have to other exchanges?
         • Reference to the ECSS standard(s), where the information for this exchange is
           presented.
In this first task of the thesis project, the purpose is to perform the analysis in a written
format. The results of this task will then serve as a starting point for the ORM modelling.
The second task is to create a use case diagram of the selected OPS use case. The use case
is described in a text format in the technical note provided by OHB, and the task here is to
transform that textual information into a UML [37, 38] use case diagram. UML has been
developed by the OMG [39] to be a standardised way to describe software oriented designs,
and a use case diagram captures what the system is supposed to do, i.e., the requirements
of the system [40]. The graphical notation of the UML use case diagrams is presented in
Table 3.1.

<!-- PDF_PAGE: 24 -->

3 Methodology                                                                           15


           Table 3.1: Graphical notation of the UML use case diagrams [40].

 Graphical          Description
 notation
                    Actor is an entity that performs a role in the given system. Actor
                    may represent a role by person, organisation or external system.
                    Actor must be involved with at least use case, but it can be involved
                    with multiple use cases. Multiple actors can also be involved with a
                    single use case.


                    Use case specifies a behaviour that yields an observable result of
                    value for the actors or other stakeholders. It is basically a function
                    or an action within the system.




                    System is used to define the scope of the use case.




                    Extend relationship between two use cases is used when there is
   <<extend>>
                    some additional behaviour that should be added to the behaviour
                    defined in the base use case. The extending use case is dependent
                    on the base use case and is usually optional.
                    Include relationship between two use cases indicates that the be-
   <<include>>
                    haviour of the included use case is inserted into the behaviour of the
                    base use case. The base use case is incomplete without the included
                    use case and the included use case is mandatory.


3.2   Modelling
In the second phase of the MBEH project, the purpose is to extend the ontology received
from ESA as input with information that is needed for the demonstration of the OPS-ENG
and RAMS-ENG information exchanges [5]. ESA has chosen the ORM language for the
SSO modelling. To prepare for this phase of the MBEH project, the task in this thesis
project is to model the selected OPS use case with ORM based on the analysis made on
the technical note provided by OHB.
ORM is a ”method for modelling and querying an information system at the conceptual

<!-- PDF_PAGE: 25 -->

3 Methodology                                                                             16




                 Figure 3.1: Main components of the NORMA tool [41].


level, and mapping between conceptual and logical (e.g., relational) levels” [28, 29]. It is
possible to map from ORM to, for example, entity relationship models, UML class models
or relational database models. ORM is a fact-oriented modelling approach, meaning that
the underlying facts of interest are modelled in an attribute-free way. In ORM, natural
sentences are used to identify objects and their roles in relationships.
Currently in use is the second generation of ORM, ORM 2, which is used with NORMA
modelling tool. NORMA is a plug-in to Microsoft Visual Studio [41]. The main components
of the NORMA tool are presented in Figure 3.1. There is a public domain version of
NORMA that is freely downloadable in the ORM Foundation website [42], but for the work
performed withing this thesis project, a professional version of the software (NORMA Pro)
is used.
The building blocks of ORM are objects (entity and value), fact types and constraints.
Entity types represent the concepts of the universe of discourse that is being modelled. The
state of an entity can change over time. Value types are lexical constants that are literal
and cannot change their state. Fact types represent the relationships between objects, i.e.,
entity and value types. Fact types can be elementary, binary, ternary and so on, depending
on the complexity. Constrains are restrictions that apply to the objects, the arities in fact
types, the multiplicity of instances or the relationships between fact types. Different types
of constraints are, for example, uniqueness, mandatory, ring or value constraints [43].
The graphical notation of ORM 2 is presented in the ”ORM 2 Graphical Notation” book
by Terry Halpin [43], which can be downloaded from the ORM website [44]. The ba-
sic constructs of ORM 2 that are used in this modelling task have been summarised in
Table 3.2.

<!-- PDF_PAGE: 26 -->

3 Methodology                                                                          17


Table 3.2: Graphical notation of Object-Role Modelling according to the ORM 2 Graphical
Notation book by Terry Halpin [43].

  Graphical notation ex-      Construct           Description
  ample
                              Entity type         Named soft rectangle.



                              Entity type with    Abbreviation for injective reference
                              popular reference   relationship to value type (e.g.,
                              mode                Country has CountryCode).


                              Value type          Named and dashed soft rectangle.



                              Predicate (unary,   Ordered set of one or more role
                              binary, ternary,    boxes with at least one predicate
                              etc.)               reading in mixfix notation. If shown,
                                                  object placeholders are denoted by
                                                  ”...”. If placeholders are not shown,
                                                  unaries are in prefix and binaries are
                                                  in infix notation.
                              Unary fact type     The smokes role may be played by
                                                  instances of the Person object type.



                              Binary fact type    By default, predicate readings (bi-
                                                  nary or longer) are read from left to
                                                  right ot form top to bottom. If the
                                                  reading direction is different, an ar-
                                                  row tip is used to indicate it. Role
                                                  names may be displayed in square
                                                  brackets beside their role.       For-
                                                  ward and inverse readings for bina-
                                                  ries may be shown together, sepa-
                                                  rated by ”/”.

<!-- PDF_PAGE: 27 -->

3 Methodology                                                            18



                Ternary fact type   Role names may be added in square
                                    brackets and arrow tips are used to
                                    indicate reverse reading order. In
                                    addition, reading orders other than
                                    forward and reverse are shown using
                                    named placeholders.
                Uniqueness          In unaries, having UC is equivalent
                Constraint (UC)     to not having it. On binaries, UCs
                                    can be used to indicate: 1:n (one-
                                    to-many), n:1 (many-to-one), m:n
                                    (many-to-many) or 1:1 (one-to-one)
                                    constraints.
                Simple              The constraint is displayed as a large
                mandatory role      dot at either end of the role connec-
                constraint          tor. The example constraint means
                                    that each person was born in some
                                    country.
                Subtyping           All subtypes are proper subtypes.
                                    An arrow runs from subtype to the
                                    supertype. A solid arrow indicates
                                    a path to the subtype’s preferred
                                    identifier (e.g., student employees
                                    are primarily identified by their em-
                                    ployee number). A dashed arrow in-
                                    dicates the supertype has a different
                                    preferred identifier.


                Inclusive-or con-   Displayed as a circled dot connected
                straint (disjunc-   to the constrained roles or the junc-
                tive mandatory      tion of adjacent roles hosted by the
                role)               same fact type. Example: each visi-
                                    tor must have a passport or a driver
                                    license or both).
                Exclusion    con-   Example: no person is both mar-
                straint             ried and widowed, and no person re-
                                    viewed and authored the same book.
                                    Exclusion may apply between two
                                    or more compatible role sequences,
                                    possible involving joints.

<!-- PDF_PAGE: 28 -->

3 Methodology                                                          19



                Exclusive-or con-   An exclusive-or constraint is sim-
                straint (xor con-   ply the conjunction of an inclusive-
                straint)            or constraint and an exclusion con-
                                    straint. Example: each academic is
                                    male or female but not both, and is
                                    tenured or contracted till some date
                                    but not both.

<!-- PDF_PAGE: 29 -->

4 Definition of Exchanges                                                               20


4       Definition of Exchanges
4.1     Operations Use Cases
During the first phase of the MBEH project, OHB identified 10 different use cases that in-
clude exchange of information between the operations engineering and systems engineering
domains:
    1. Spacecraft attitude and orbit control system models exchanged with flight dynamics
       system developers.
    2. Exchange of monitoring & control data: from the spacecraft reference database
       through to EGSE, on-board software and development environment and the MCS.
    3. Exchange of on-board control procedures.
    4. Exchange of Flight Operations Procedure (FOP).
    5. Exchange of system and subsystem functional models, parameters and electronic data
       sheets to drive operational simulator development.
    6. Exchange of relevant spacecraft system and subsystem models as input to a mission
       operational rules and constraints document and rules and constraints language of the
       mission planning system states, planning constraints etc.
    7. Exchange of integration and test data, anomaly reports and non conformance reports
       across domains and at different project phases to share status and results.
    8. Exchange of space-ground interface control data - synchronise and ensure consistency
       of the interface control data definition and link budget calculation between ground
       and space.
    9. Linking of instruments data return models (e.g., mass memory), the link budget and
       ground stations planning to analyse data return and enable associated trade-offs.
 10. Exchange and traceability of operational and system requirements, including justifi-
     cations.
The task in this phase of the MBEH project was to explain all the use cases and then select
one as the demonstration case. The use case number 4, exchange of FOP, was selected as
the core demonstration case by OHB [45].

4.2     Selected Use Case: Flight Operations Procedure (FOP)
4.2.1    Description
Purpose and objective of the operations procedure according to the ECSS-E-ST-70C -
Ground Systems and Operations [30] is: ”An operations procedure is an elementary com-
ponent of the mission operations plan that defines the actions to achieve a specific opera-

<!-- PDF_PAGE: 30 -->

4 Definition of Exchanges                                                               21


tional objective. The complete set of operational procedures covers all planned operations
for the space and ground segments. An operations procedure is a “building block” used
in the construction of the actual operations to be performed in a given mission phase. An
operations procedure may be called up by a mission timeline, an automatically executing
schedule, another procedure or it can be initiated manually.”
According to the ECSS-E-ST-70C [30], an operations procedure consists of the following
parts:
  1. Preliminary elements
        • Title of the procedure.
        • Version control, including version number and date.
        • Names of the authors.
  2. Introduction (this part is for informative purposes and does not belong to the exe-
     cutable part of the procedure)
        • Objectives of the procedure.
        • Context in which the procedure can be executed, goal of the procedure and all
          possible results.
        • Explanatory figures or diagrams.
  3. Required operational authority
        • Required special operational authorisation for manual execution of the proce-
          dure. For example: ”This procedure may be executed by the spacecraft con-
          troller only with the written authority of the spacecraft operations manager.”
  4. Expected duration
        • How long it takes to execute the procedure.
  5. Pre-conditions
        • List of all conditions that need to be satisfied before the execution of the pro-
          cedure can be started.
        • Possible conditions under which start of the procedure is prohibited.
        • Pre-conditions shall refer to one or more of the following:
            – Mission phase;
            – Ground segment configuration;
            – Space segment configuration;
            – Orbit position or environmental conditions;

<!-- PDF_PAGE: 31 -->

4 Definition of Exchanges                                                                22


           – Status of other procedures.
  6. Procedure body
       • The executable elements that achieve the goal of the procedure.
       • Procedure steps, which can either be executed in sequence or in parallel.
           – The structure of a step shall be similar to that of the procedure itself, mean-
             ing that it can have pre-conditions, executable body and post conditions.
           – For each step, the sequence of activities to be performed shall be described.
             These activities can be, for example, uplink telecommand, initiate command
             sequence or check specific telemetry values.
       • Possible contingency element that manages contingency situations detected dur-
         ing the execution of the procedure.
           – The procedure shall contain information regarding what to do in case of a
             contingency. This is necessary for the steps for which the system cannot be
             left as is, such as a situation when a critical on-board protection has been
             disabled.
           – If contingency actions are specified, the procedure shall contain information
             regarding how to restore the system configuration, achieve the goal of the
             procedure in a different manner or abort the procedure if it is not possible
             to recover from the contingency.
  7. Post conditions
       • Defines how to verify the goal(s) of the procedure are achieved after the execu-
         tion of the procedure body.
       • Following the verification, the status of the procedure shall be one of the fol-
         lowing:
           1. procedure terminated, success confirmed, or
           2. procedure terminated, procedure failed (including reasons).
The procedure bodies of AIT and ground segment operations procedures are defined in
ECSS-E-ST-70-32C - Test and operations procedure language [35]. The procedure bodies
include declaration body, preconditions body, main body, watchdog body and confirma-
tions body. The different bodies are presented in Figure 4.1.

<!-- PDF_PAGE: 32 -->

4 Definition of Exchanges                                                                 23




                 Figure 4.1: Procedure bodies. The figure is adapted from [35].


4.2.2      Exchanges
In the technical note [45], OHB listed 16 exchanges that are relevant for the selected flight
operations procedure4 use case. This list of exchanges was complemented with space system
model, system element, activity, event, reporting data, compound parameter, telecom-
mand, activity call and the different procedure bodies. The results of the analysis are
presented in Table 4.1.




  4
      Flight operations procedure is a type of ground procedure.

<!-- PDF_PAGE: 33 -->

4 Definition of Exchanges                                                                  24


      Table 4.1: Exchanges involved in the flight operations procedure use case.

 Exchange Description                 Information type         Connections to           Ref.
                                                               other exchanges
 Space       Reflects the struc-      The space system         Space system model       [34]
 System      ture of the space sys-   model consists of en-    contains system ele-
 Model       tem, and is hierar-      tity types (e.g., sys-   ment(s). It can con-
             chically broken down     tem element) and         tain more than one
             into system elements     value types.             system element.
             mirroring the func-
             tional breakdown of
             the space system.
 System      Representation of a      Name, description,       System element pro-      [34]
 Element     functional element       type, nature and list    vides information in
             of the space system      of references.           the form of report-
             within the space                                  ing data (e.g., mea-
             system model.                                     surements which re-
                                                               flect the state of the
                                                               associated system el-
                                                               ement). Monitoring
                                                               and control knowl-
                                                               edge of a system el-
                                                               ement is expressed
                                                               in the form of ac-
                                                               tivities and events.
                                                               System element may
                                                               contain other system
                                                               elements. Each sys-
                                                               tem element belongs
                                                               to exactly one sys-
                                                               tem element. Sys-
                                                               tem element may not
                                                               cycle back to itself.

<!-- PDF_PAGE: 34 -->

4 Definition of Exchanges                                                                 25



 Activity    Space system mon-      Name, description,        Activity       is  ei-   [34]
             itoring and control    type       (procedure,    ther procedure or
             function.              telecommand          or   telecommand, and it
                                    operating       system    belongs to exactly
                                    command), list of         one system element.
                                    references, critical-     Activity is called by
                                    ity, list of domain(s)    activity call.
                                    of applicability, list
                                    of redundant activ-
                                    ities, list of reverse
                                    activities and list of
                                    arguments.
 Event       Occurrence of a        Name of system ele-       Event belongs to         [34]
             condition or set       ment, name, descrip-      exactly one system
             of conditions that     tion, type, list of do-   element. Event can
             can arise during       main(s) of applica-       have a reporting
             the course of a test   bility, list of refer-    data      components
             session or mission     ences, severity, or-      or domain specific
             phase. Events are      dered list of report-     activities.
             used within the        ing data components
             space system to        and list of domain
             trigger the execu-     specific activities.
             tion of functions
             (e.g. acquisition of
             signal can initiate
             telemetry processing
             tasks at the ground
             station).      Users
             can define mission-
             specific     events,
             associated with a
             system element, for
             example, for use
             within procedures.

<!-- PDF_PAGE: 35 -->

4 Definition of Exchanges                                                                   26



 Reporting   Data used for assess-    Name of system ele-       Parameter and com-       [34]
 Data        ing the functioning      ment, name, descrip-      pound parameter are
             of the space system.     tion, type (parame-       subtypes of report-
                                      ter or compound pa-       ing data. Reporting
                                      rameter), list of do-     data is either param-
                                      main(s) of applica-       eter or compound
                                      bility, list of domain    parameter but not
                                      specific validity con-    both.       Reporting
                                      ditions, list of ref-     data belongs to ex-
                                      erences and list of       actly one system el-
                                      redundant reporting       ement.
                                      data.
 Procedure   Means for interact-      Initiation mode, ear-     Procedure is a type      [34,
             ing with the space       liest validity date,      of activity.             35]
             system in order to       latest validity date,
             achieve a given ob-      activity      execution
             jective or sequence of   state.       Procedure
             objectives.    Proce-    consists of an op-
             dure can be either       tional      declaration
             ground procedure or      body, optional pre-
             on-board procedure.      conditions        body,
                                      mandatory         main
                                      body,          optional
                                      watchdog body and
                                      optional confirma-
                                      tion body.
 Ground      Subtype of proce-        Ground procedure          Subtype of proce-        [34]
 procedure   dure.                    script and execution      dure.
                                      mode.
 Ground      The textual repre-       Script.                   Ground procedure         [34]
 procedure   sentation of the pro-                              script is provided
 script      cedure.                                            for activities of type
                                                                ground procedure.
 Body        Declaration   body,      Scripts.                  Body is a part of        [35]
             preconditions body,                                procedure or step.
             main body, watch-
             dog    body     and
             confirmation body.

<!-- PDF_PAGE: 36 -->

4 Definition of Exchanges                                                                27



 Declaration Part of a proce-         Script with event        Optional part of a     [35]
 body        dure (or step) that      name and descrip-        procedure or step.
             declares the local       tion.                    Subtype of body.
             events that can be
             raised within the
             procedure (or step).
 Pre-        Part of a procedure      Script with expres-      Optional part of a     [35]
 conditions (or step) dedicated       sion and wait state-     procedure or step
 body        to ensuring that the     ment.                    (mandatory       for
             procedure (or step)                               watchdog      step).
             only executes if or                               Subtype of body.
             when pre-defined ini-
             tial conditions are
             satisfied.
 Main        Part of a procedure      Script consisting of     Mandatory      part    [35]
 body        (or step) dedicated      sequence of state-       of a procedure or
             to achieving the ob-     ments of the follow-     step.   Subtype of
             jectives of the proce-   ing type: set of pro-    body.       Consists
             dure (or step).          cedure context state-    of a sequence of
                                      ment, initiate in par-   statements.
                                      allel, initiate and
                                      confirm step, initiate
                                      and confirm activity,
                                      initiate activity, in-
                                      form user statement,
                                      log statement.
 Watchdog     Part of a procedure     Script     consisting    Optional part of a     [35]
 body         (or step) which         of watchdog steps,       procedure or step
              manages       contin-   which are subtypes       (not part of watch-
              gency      situations   of step.                 dog step). Subtype
              that can arise during                            of body. Consists of
              the execution of the                             watchdog steps.
              procedure (or step).
 Confir-      Part of a procedure     Script with expres-      Optional part of a     [35]
 mation       (or step) whose pur-    sion and wait state-     procedure or step.
 body         pose is to assess       ment.                    Subtype of body.
              whether or not the
              objective of the pro-
              cedure (or step) has
              been achieved.

<!-- PDF_PAGE: 37 -->

4 Definition of Exchanges                                                                    28



 Step        Component of a pro-       The structure of a        An activity can be       [35]
             cedure that achieves      step is similar to that   comprised of steps
             a well-defined sub-       of a procedure itself,    and each step can
             goal.                     i.e., it can have pre-    itself be further de-
                                       conditions, an ex-        composed into lower-
                                       ecutable body and         level steps. Steps are
                                       post conditions. In       the building blocks
                                       addition, it has a        of which the proce-
                                       name.                     dure body is com-
                                                                 posed of. Watchdog
                                                                 and main body steps
                                                                 are subtypes of step.
 Statement   Element     of    the     Text or scripts.          Statement is part of     [35]
             procedure language                                  a sequence of state-
             which,       together                               ments.
             with other elements,
             implements the goal
             of a procedure (or
             step).     Statement
             can, for example,
             initiate the execu-
             tion of main body
             step or activity.
 Sequence    Collection of state-      Predefined list of        The body of pro-         [35]
 of state-   ments in a defined        possible statements.      cedure or step con-
 ments       order.                                              sists of a sequence of
                                                                 statements.
 Step/       Tells the state of step   Enum (set of named        The result of ex-        [35]
 Activity    or activity.              constants), for ex-       ecution of part of
 execution                             ample:     executed,      a procedure at the
 state                                 aborted, confirmed,       level of the overall
                                       not       confirmed,      procedure or specific
                                       completed.                steps/statements.

<!-- PDF_PAGE: 38 -->

4 Definition of Exchanges                                                               29



 Tele-       No ECSS definition      Service type, sub-      Telecommand is a        [34,
 command     found for telecom-      service type, default   subtype of activity.    46]
             mand in the stan-       application process,    Telecommand has a
             dards or ECSS glos-     priority,    possibly   service type and sub-
             sary. A ”telecom-       MAP etc.                service type.
             mand packet” is the
             data unit that is
             used to carry a ser-
             vice request from an
             application process
             on the ground to
             an application pro-
             cess on-board.
 Packet      A telemetry packet      Telecommand             Packet    transports
 (TM/TC)     is the data unit that   packet and teleme-      message type.
             is used to carry a      try   packet     are
             service report from     subtypes of packet.
             an application pro-
             cess on board to an
             application process
             on the ground. A
             telecommand packet
             is the data unit that
             is used to carry a
             service request from
             an application pro-
             cess on the ground to
             an application pro-
             cess on-board.

<!-- PDF_PAGE: 39 -->

4 Definition of Exchanges                                                               30



 (PUS)       Functional element     Unique service type      Each service type       [46]
 Service     of the space system    name, unique ser-        defines at least one
 type        that provides a num-   vice type identifier     subservice      type
             ber of closely re-     (unsigned      integer   (each      subservice
             lated functions that   greater than or equal    type is defined by
             can be remotely op-    to 1 and less than or    exactly one service
             erated. Each service   equal to 255), and       type and has a
             is composed of one     reference to involved    unique     subservice
             or more subservices,   (PUS)subservice.         type name).      Ser-
             where each subser-                              vice type contains
             vice involves a sub-                            message type.
             service provider and
             one or more subser-
             vice users.
 (PUS)       Request or report.     Unique       message     Service type con-       [46]
 Message                            type name, unique        tains message type.
 type                               message type iden-       Request and report
                                    tifier,   which     is   types are subtypes
                                    composed of service      of a message type.
                                    type identifier that
                                    contains the message
                                    type and a unique
                                    message      subtype
                                    identifier (unsigned
                                    integer greater than
                                    or equal to 1 and
                                    less than or equal to
                                    255) that identifies
                                    the message type in
                                    that service type,
                                    and request/report
                                    type.

<!-- PDF_PAGE: 40 -->

4 Definition of Exchanges                                                                 31



 (PUS)       Message consisting       Instruction type.       Request type is a        [46]
 Request     of one or more in-                               subtype of message
 type        structions generated                             type.
             by a subservice user
             for execution by a
             subservice provider.
             (Instruction = ele-
             mentary constituent
             of a request that
             is    generated     by
             a subservice user
             for execution by a
             subservice provider.)
 Activity    Activities can have      Name, description,      Activity has some        [34]
 argument    arguments which can      arity,   type (any      activity       argu-
             either be simple or      simple data type,       ment(s).     Activity
             compound in nature       record or activity      call is a subtype of
             e.g., a commanded        call), default value,   activity argument.
             filter wheel position    fixed value.
             of type enumerated
             is a simple argu-
             ment, a command
             to power up an in-
             strument can com-
             prise an array of
             CPDU command ar-
             guments, each argu-
             ment comprising the
             output line number
             and the pulse dura-
             tion.
 Activity    The call to the activ-   List of system ele-     Calls activity. Sub-     [34]
 call        ity that is initiated.   ment names to which     type of activity argu-
                                      the activity call re-   ment.
                                      lates or whose prop-
                                      erty can be used.

<!-- PDF_PAGE: 41 -->

4 Definition of Exchanges                                                                   32



 Parameter     Lowest level of ele-    Data type (simple         Reporting data con-     [34]
               mentary information     type).                    sists of a parameter
               that has a meaning                                or a compound pa-
               for monitoring the                                rameter. Engineer-
               space system.                                     ing value and unit
                                                                 are part of a param-
                                                                 eter.
 Compound Record       comprised       Compound parame-          Reporting data is ei-   [34]
 parameter of any sequence             ter type (record, ar-     ther parameter or
             of reporting data,        ray, deducted struc-      compound parame-
             arrays of reporting       ture).                    ter.
             data and sub-records
             that are interpreted
             together.
 Engineering Value, property of                                  Property of parame-     [35]
 value       parameter.                                          ter.
 Engineering Property of parame-       Quantity,       name,     Property of parame-     [35]
 Unit        ter.                      symbol and def-           ter.
                                       inition.        (E.g.,.
                                       quantity:      length,
                                       name: metre, sym-
                                       bol: m, definition:
                                       SI base unit.)


4.3    Process of Developing FOP With MBSE Hub
The process of developing the flight operations procedure while using the MBSE hub
to exchange information is detailed in a text format in the technical note provided by
OHB [45]. The purpose of this task was to transform that textual description into a UML
use case diagram. The result is presented in Figure 4.2. Main actors involved in the
exchanges are systems engineer, OPS engineer (supplier) and OPS customer (MCS). The
actors are presented in Table 4.2 according to the technical note.
The use case diagram in Figure 4.2 describes the following process of developing the flight
operations procedure. The process starts by the systems engineer creating a space system
model in COMET, and extending the model with parameters, requirements and relation-
ships in COMET, Capella, Enterprise Architect or Cameo Systems Modeler. During this
phase, it shall be possible to import the model to the MBSE hub, where it is translated
into the SSO representation, as well as to export the model to the same or different systems
engineering tool. In addition, the space system model can be extended with activities and
events associated to the different system elements, as well as transitions, conditions and
exchanges, such as telecommands, between space and ground segments. This is done by

<!-- PDF_PAGE: 42 -->

4 Definition of Exchanges                                                               33


the systems engineer in Capella, Enterprise Architect or Cameo, and the result works as
the skeleton for the flight operations procedure.
When the extended space system model has been imported to the hub and translated into
the SSO representation, the OPS engineer can export it from the hub and import it into the
Preparation Environment for Flight Control Team (OPEN-M) tool to populate the EGS-
CC CDM with the monitoring and control elements and related parameters, activities and
functions. The resulting EGS-CC CDM information type is a procedure skeleton populated
with steps and activities converted to activity list. The OPS engineer exports this to the
MBSE hub, where it can be translated into the SSO representation. It shall be possible to
also exchange the EGS-CC CDM in its native format, enabling the direct exchange with
for example, mission control centre. Additional exchange type would be to exchange the
flight operations procedure as XML schema. It shall be possible to publish updates of the
space system model and the EGS-CC CDM in the MBSE hub.

Table 4.2: Actors involved in the development and exchange of flight operations procedures
as defined in the technical note by OHB [45].

  Actor                    Entity         Definition
  Systems engineer         Industry       Responsible of the overall design of the space-
                                          craft, definition of the system requirements,
                                          design assessments and trade-offs, technical
                                          interfaces, technical budget and margin phi-
                                          losophy, mission phase and spacecraft mode
                                          definition, spacecraft control, ConOps and
                                          mission architecture definition.
  Operations customer      Agency         Responsible of the procurement of the space
                                          and ground segment operations. Receives the
                                          operations deliverables and executes the flight
                                          operations.
  Operations supplier      Agency /       Responsible of the preparation and execu-
  (OPS engineer)           Industry       tion of the space and ground segment oper-
                                          ations. Prepares and validates flight opera-
                                          tions and provides operation relevant deliver-
                                          ables to customer.

<!-- PDF_PAGE: 43 -->

4 Definition of Exchanges                                                          34




Figure 4.2: Use case diagram representing the development process of flight operations
procedure with MBSE hub.

<!-- PDF_PAGE: 44 -->

5 ORM Models                                                                                35


5     ORM Models
The scope of this task is to model the exchanges that are related to the selected OPS use
case, as presented in Table 4.1. An old ORM model of the ECSS-E-ST-70-31C [34] is used
as a reference for the modelling. The reference model covers the entire standard, meaning
also a lot of information that is out of the scope of this task. In addition, not everything
that is modelled in this task is covered in the standard.
The model created in this task is structured differently from the reference model to better
reflect the OPS use case. The reference model is structured according to the sections and
subsections of the ECSS-E-ST-70-31C standard. The model created in this task focuses
on showing the hierarchical structure and relationships of space system model, system ele-
ments, and the monitoring and control knowledge (activities, events and reporting data), as
well as the connections of all the relevant procedure and telecommand related information
defined in Table 4.1.
Some parts of the model are similar as in the reference model, such as parts of the definitions
of activity, event and reporting data, which are well defined in the ECSS-E-ST-70-31C.
However, the structure and scope of the model differs, and some parts have been updated.
Parameter, procedure, body, step, telecommand and the PUS service/message/request
parts are not entirely covered in the ECSS-E-ST-70-31C, and therefore, those parts are
modelled without any reference model.
The models are presented in Figures 5.1-5.12. Each picture is followed by the verbalisation
of the model. The relationships of space system model, system element, activity, event,
reporting data and their main subtypes are presented in Figure 5.1. In the following
models, the system element, activity, event and reporting data and information associated
with them are presented in more detail, starting with system element in Figure 5.2. Activity
is presented in Figure 5.3. Activity is called by activity call, which is a subtype of activity
argument, as presented in Figure 5.4. Event and information related to it are presented
in Figure 5.5. Reporting data, and its subtypes parameter and compound parameter are
presented in Figures 5.6 and 5.7, respectively. Two subtypes of activity are modelled:
procedure and telecommand. Procedure and its subtype ground procedure are presented
in Figure 5.8. Procedure is composed of bodies and steps, which can be seen in Figures
5.9 and 5.10, respectively. Telecommand is presented in Figure 5.11 and the PUS service,
message and request types that are related to it are presented in Figure 5.12.

<!-- PDF_PAGE: 45 -->

5 ORM Models                                                36




               Figure 5.1: ORM model: Space System Model.

<!-- PDF_PAGE: 46 -->

5 ORM Models                                            37




               Figure 5.2: ORM model: System Element.

<!-- PDF_PAGE: 47 -->

5 ORM Models                                      38




               Figure 5.3: ORM model: Activity.

<!-- PDF_PAGE: 48 -->

5 ORM Models   39

<!-- PDF_PAGE: 49 -->

5 ORM Models                                               40




               Figure 5.4: ORM model: Activity Argument.

<!-- PDF_PAGE: 50 -->

5 ORM Models                                   41




               Figure 5.5: ORM model: Event.

<!-- PDF_PAGE: 51 -->

5 ORM Models   42

<!-- PDF_PAGE: 52 -->

5 ORM Models                                            43




               Figure 5.6: ORM model: Reporting Data.

<!-- PDF_PAGE: 53 -->

5 ORM Models                                       44




               Figure 5.7: ORM model: Parameter.

<!-- PDF_PAGE: 54 -->

5 ORM Models   45

<!-- PDF_PAGE: 55 -->

5 ORM Models                                       46




               Figure 5.8: ORM model: Procedure.

<!-- PDF_PAGE: 56 -->

5 ORM Models   47

<!-- PDF_PAGE: 57 -->

5 ORM Models                                  48




               Figure 5.9: ORM model: Body.

<!-- PDF_PAGE: 58 -->

5 ORM Models   49

<!-- PDF_PAGE: 59 -->

5 ORM Models                                   50




               Figure 5.10: ORM model: Step.

<!-- PDF_PAGE: 60 -->

5 ORM Models   51

<!-- PDF_PAGE: 61 -->

5 ORM Models                                          52




               Figure 5.11: ORM model: Telecommand.

<!-- PDF_PAGE: 62 -->

5 ORM Models                                          53




               Figure 5.12: ORM model: PUS service.

<!-- PDF_PAGE: 63 -->

5 ORM Models   54

<!-- PDF_PAGE: 64 -->

6 Conclusions and Outlook                                                                  55


6    Conclusions and Outlook
The thesis work was performed during the first phase of European Space Agency’s Model
Based Engineering Hub (MBEH) -project. The first phase of the MBEH project, called
”Scoping”, had the main objectives of producing a technical specification for the MBSE
hub and elaborating on the relevant information exchanged between OPS-ENG and RAMS-
ENG domains. After successful completion of the first phase, the project proceeds to the
second phase called ”Development and Demonstration”. In this phase, a technical solution
for the MBSE hub would be provided, the ontologies received from ESA would be extended
with information needed to support the demonstration of the information exchanges, and
the MBSE hub operation would be demonstrated.
The objectives of the thesis were to support the first phase of the MBEH project and to
prepare for its second phase by developing a CDM of the operations use case. The CDM
was developed in two parts. The first task was to analyse and complement the exchanges
related to the chosen operations use case based on the ECSS standards. OHB listed 16
exchanges that are relevant for the selected flight operations procedure use case. This list
of exchanges was complemented with 13 additional exchanges that were deemed important
for the next task. For each exchange, description, information types, connections to other
exchanges and relevant ECSS standards were listed. This written analysis was then used
as a starting point for modelling, which was the second task.
The modelling was performed using the ORM language and NORMA tool. The ORM
model is structured to reflect the hierarchical structure and relationships of space system
model, system elements, and the monitoring and control knowledge (activities, events and
reporting data), as well as the connections of all the relevant procedure and telecommand
related information defined in the previous task. As an additional task, the OHB’s textual
description of how the flight operations procedure is developed using the MBSE hub was
transformed into a UML use case diagram. The purpose of this task was to identify the
needs for the MBSE hub.
The result of the thesis is a conceptual data model of the operations use case, reflecting the
industry needs identified by OHB. The work was based on the operations technical note
written by OHB [45] and ECSS standards. In the next phase of the MBEH project, the
model needs to be complemented and harmonised with EGS-CC and the existing ontology
models, which were not available for this thesis work. After complementing the OPS and
RAMS universes of discourse of the SSO, and building the technical solution for the MBSE
hub, it will be demonstrated with the two use cases.

<!-- PDF_PAGE: 65 -->

References                                                                              56


References
 [1] European Space Agency, “Requirements for a Model Based System Engineering Fac-
     tory,” Technical Dossier, ESA-TECS-TN-011986, Issue 0, Rev. 3, 2019.
 [2] European Space Agency, “ESA’s Technology Strategy: Maximising Competitiveness
     and Achieving Ambitious Goals,” Ver. 1.1, 2019.
 [3] European Space Agency, “Digitalisation at ESA,” https://mb4se.esa.int/, Accessed
     on April 4, 2022.
 [4] European Cooperation for Space Standardization, “ECSS homepage,” https://ecss.
     nl/, Accessed on April 6, 2022.
 [5] European Space Agency, “Model-Based Engineering Hub,” Statement of Work, ESA-
     TRP-TECSYE-SOW-014909, Issue 2, Rev. 1, 2021.
 [6] D. D. Walden, G. J. Roedler, K. J. Forsberg, R. D. Hamelin and T. M. Shortell,
     Systems Engineering Handbook: A Guide for System Life Cycle Processes and Activ-
     ities, 4th ed. San Diego, CA, USA: International Council on Systems Engineering
     (INCOSE), 2015.
 [7] A. M. Madni and M. Sievers, “Model-based systems engineering: Motivation, current
     status, and research opportunities,” Systems Engineering, vol. 21, no. 3, pp. 172–190,
     2018.
 [8] Object Management Group (OMG), “OMG SysML,” https://www.omgsysml.org, Ac-
     cessed on April 26, 2022.
 [9] Sparx Systems, “Enterprise Architect,” https://sparxsystems.com/, Accessed on May
     23, 2022.
[10] Dassault Systemes/No Magic, “Cameo Systems Modeler,” https://www.3ds.com/
     products-services/catia/products/no-magic/cameo-systems-modeler/, Accessed on
     May 23, 2022.
[11] Eclipse Foundation, “Capella,” https://www.eclipse.org/capella/, Accessed on May
     23, 2022.
[12] P. Roques, “MBSE with the ARCADIA Method and the Capella Tool,” in 8th Euro-
     pean Congress on Embedded Real Time Software and Systems (ERTS 2016), Toulouse,
     France, 2016.
[13] A. M. Madni and S. Purohit, “Economic analysis of model-based systems engineering,”
     Systems, vol. 7, no. 1, p. 12, 2019.
[14] A. L. Ramos, J. V. Ferreira, and J. Barceló, “Model-based systems engineering: An
     emerging approach for modern systems,” IEEE Transactions on Systems, Man, and
     Cybernetics, Part C (Applications and Reviews), vol. 42, no. 1, pp. 101–111, 2011.

<!-- PDF_PAGE: 66 -->

References                                                                              57


[15] P. J. Younse, J. E. Cameron, and T. H. Bradley, “Comparative analysis of model-based
     and traditional systems engineering approaches for architecting a robotic space system
     through automatic information transfer,” IEEE Access, vol. 9, pp. 107 476–107 492,
     2021.
[16] J. Lorenzo Alvarez, H.-P. de Koning, D. Fischer, M. Wallum, H. Metselaar, and
     M. Kretzenbacher, “Towards a definition of best practices for Model Based Systems
     Engineering in European Space Agency Projects,” in 2018 AIAA Space and Astro-
     nautics Forum and Exposition, Orlando, FL, USA, 2018, p. 5327.
[17] Project Planning and Implementation, ECSS-M-ST-10C Rev. 1, ECSS Secretariat,
     2009.
[18] M. Bandecchi, B. Melton, B. Gardini, and F. Ongaro, “The ESA/ESTEC concurrent
     design facility,” Proceedings of EUSEC, vol. 9, p. 2000, 2000.
[19] Engineering Design Model Data Exchange (CDF), ECSS-E-TM-E-10-25A, ECSS Sec-
     retariat, 2010.
[20] RHEA Group, “COMET,” https://products.rheagroup.com/comet, Accessed on June
     2, 2022.
[21] R. Biesbroek, L. Innocenti, A. Wolahan, and S. M. Serrano, “e. Deorbit-ESA’s active
     debris removal mission,” in Proceedings of the 7th European Conference on Space
     Debris, Darmstadt, Germany, 2017, Published by the ESA Space Debris Office.
[22] R. Biesbroek, T. Soares, J. Hüsing, and L. Innocenti, “The e. Deorbit CDF study:
     A design study for the safe removal of a large space debris,” in Proceedings of the
     6th European Conference on Space Debris, Darmstadt, Germany, 2013, Published by
     ESA.
[23] B. K. Muirhead, A. K. Nicholas, J. Umland, O. Sutherland, and S. Vijendran, “Mars
     sample return campaign concept status,” Acta Astronautica, vol. 176, pp. 131–138,
     2020.
[24] S. J. Herzig, D. Velez, B. Nairouz, B. Weatherspoon, R. Tikidjian, T. M. Randolph,
     and B. Muirhead, “A model-based approach to developing the concept of operations
     for potential mars sample return,” in 2018 AIAA SPACE and Astronautics Forum
     and Exposition, Orlando, FL, USA, 2018, p. 5389.
[25] G. D. Racca, R. Laureijs, L. Stagnaro, J.-C. Salvignol, J. L. Alvarez, G. S. Criado,
     L. G. Venancio, A. Short, P. Strada, T. Bönke et al., “The Euclid mission design,”
     in Space telescopes and instrumentation 2016: optical, infrared, and millimeter wave,
     vol. 9904. SPIE, 2016, pp. 235–257.
[26] D. Fischer, F. Keck, M. Spada, M. Wallum, and T. Stoitsev, “Leveraging MBSE
     for ESA Ground Segment Engineering: Starting with the Euclid Mission,” in 2018
     SpaceOps Conference, Marseille, France, 2018, p. 2572.

<!-- PDF_PAGE: 67 -->

References                                                                            58


[27] J.-P. Terraillon, H.-P. de Koning and S. Valera, “Overall System Modelling for Sys-
     tem Engineering (OSMoSE) - Space System Ontology 1st Brainstorming Workshop
     Report,” European Space Agency, ESA-TECSW-RP-014789, rev. 0.2, 2019.
[28] T. Halpin, “Object-role modeling (ORM/NIAM),” in Handbook on architectures of
     information systems, ser. International Handbooks on Information Systems, P. Bernus,
     K. Mertins and G. Schmidt, Ed. Berlin, Heidelberg: Springer, 1998, pp. 81–103.
[29] Halpin, Terry, Object-role modeling fundamentals: a practical guide to data modeling
     with ORM. New Jersey, USA: Technics Publications, 2015.
[30] Ground Systems and Operations, ECSS-E-ST-70C, ECSS Secretariat, 2008.
[31] A. Walsh, M. Pecchioli, J. M. Carranza, W. Bothmer, P.-Y. Schmerber, J. Rueting
     et al., “The European Ground Systems-Common Core (EGS-CC) Initiative,” in 2012
     SpaceOps Conference, Stockholm, Sweden, 2012, p. 1282732.
[32] European Space Agency, “European Ground Systems – Common Core (EGS-CC),”
     http://www.egscc.esa.int/, Accessed on May 24, 2022.
[33] M. Pecchioli, A. Walsh, J. M. Carranza, R. Blommestijn, M.-C. Charmeau, M. P.
     Geyer et al., “Objectives and Concepts of the European Ground Systems Com-
     mon Core (EGS-CC),” in Simulation and EGSE for Space Programmes (SESP2012),
     ESA/ESTEC, Noordwijk, The Netherlands, 2012.
[34] Ground Systems and Operations - Monitoring and Control Data Definition, ECSS-E-
     ST-70-31C, ECSS Secretariat, 2008.
[35] Test and Operations Procedure Language, ECSS-E-ST-70-32C, ECSS Secretariat,
     2008.
[36] F. Trifin and A. Walsh, “Monitoring and Control Operations Preparation Framework
     for EGS-CC Based Environments,” in 2018 SpaceOps Conference, Marseille, France,
     2018, p. 2711.
[37] R. Pooley and P. King, “The unified modelling language and performance engineer-
     ing,” IEE Proceedings-Software, vol. 146, no. 1, pp. 2–10, 1999.
[38] Object Management Group (OMG), “UML Home Page,” https://www.uml.org/, Ac-
     cessed on May 18, 2022.
[39] Object Management Group (OMG), “OMG Home Page,” https://www.omg.org/, Ac-
     cessed on May 18, 2022.
[40] OMG Unified Modelling Language Specification, ver. 2.5.1, Object Management
     Group, 2017, https://www.omg.org/spec/UML, Accessed on May 18, 2022.
[41] M. Curland and T. Halpin, “The NORMA Software Tool for ORM 2,” in Information
     Systems Evolution, P. Soffer and E. Proper, Eds. Berlin, Heidelberg: Springer, 2011,
     pp. 190–204.

<!-- PDF_PAGE: 68 -->

References                                                                           59


[42] K. Evans, “The ORM Foundation,” https://www.ormfoundation.org/, Accessed on
     May 31, 2022.
[43] T. Halpin, “ORM 2 Graphical Notation Summary,”               http://orm.net/pdf/
     ORM2GraphicalNotation.pdf, Accessed on May 31, 2022.
[44] T. Halpin, “Object Role Modeling,” http://orm.net/, Accessed on May 31, 2022.
[45] S. Janke, M. Guilherme, R. Lampka and A. Wortmann, OHB Systems AG, “Definition
     of OPS-ENG exchanges,” Technical Note, MBEH-RHEA-TN1, Issue 1, Rev. 2, 2022.
[46] Telemetry and Telecommand Packet Utilization, ECSS-E-ST-70-41C, ECSS Secre-
     tariat, 2016.

## Figures

![figure_001.png](figure_001.png)
