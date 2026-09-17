---
source: null
title: "review-candidate-0646"
page_count: 7
converted_at: "2026-09-05T23:45:09Z"
---

<!-- PDF_PAGE: 1 -->

IAC-24-85114

<div align="center">

# User integrated analysis of collaborative MBSE tools for student CubeSat teams

</div>

Gargi Pantoji $ ^{a *} $ , Nicolas Oidtmann $ ^{b} $ , Gitte van Helden $ ^{c} $ , Dr. Iklim Akay $ ^{d} $

$ ^{a} $ Faculty of Aerospace Engineering, Delft University of Technology (TU Delft), The Netherlands, g.s.pantoji@student.tudelft.nl

$ ^{b} $ Faculty of Aerospace Engineering, Delft University of Technology (TU Delft), The Netherlands, n.c.oidtmann@student.tudelft.nl

$ ^{c} $ Faculty of Aerospace Engineering, Delft University of Technology (TU Delft), The Netherlands,

$ ^{d} $ Faculty of Aerospace Engineering, Delft University of Technology (TU Delft), The Netherlands,

* Corresponding author

## Abstract

As the popularity of CubeSat Missions continues to rise within student teams, the demand for an efficient and collaborative engineering mindset becomes increasingly important. Model-Based Systems Engineering (MBSE) constitutes a promising approach to realize innovative, technically complex systems, by offering a basis for faster, simpler and more resilient information exchange within the student teams, as well as with collaborating professors and external stakeholders. This paper investigates various MBSE approaches that cater to the unique nature and needs of student teams. Some of these constraints include a varying degree of Systems Engineering knowledge and proficiency within the teams, frequent changes in team composition, a manageable learning curve of the deployed tools and financial constraints. Possible MBSE approaches are explored, each representing a combination of one or multiple MBSE tools combined with a proposed methodology.

Previous research at TU Delft has been focused on supporting and enabling Multidimensional Design Optimization (MDO) and Knowledge-Based Engineering (KBE) applications or did not consider the specific needs of larger teams of university students with up to 50 members. In contrast to this, the methodology applied for this paper relies on a strong integration of the targeted users, i.e. members of student-led projects, from within the environment of TU Delft for the requirements definition, concept generation, concept evaluation and final validation of the most promising MBSE approaches. This is achieved through interviews, surveys and interactive brainstorming working sessions.

This research focuses on student teams at TU Delft, considering the university-specific infrastructure like the Collaborative Design Lab, availability of software tool licenses and other constraints. In the last section of the paper, these university-specific aspects are reflected upon, providing a further understanding of how the conclusions can be adapted into another university context. By publishing the results, we look forward to connecting and sharing insights with student CubeSat teams from other universities across the world.

## 1. Introduction

Joining a university student team can have great benefits for students, by preparing them better for challenges they will face in their future careers. It furthermore allows students to pursue their interests next to regular university studies as well as connect and collaborate with like-minded people. Working in a student team also helps the students to develop essential soft skills for leadership and teamwork and usually offers networking chances to build connections with other students, university and industry professionals. Besides these benefits for students, there are challenges most university student teams face during their life cycle. In the frame of this research project, the extent to which Model-Based Systems Engineering (MBSE) can be leveraged to answer these specific challenges is investigated. While the general trend of adopting MBSE in industry can be understood as a response to similar issues, also present in university student teams, the specific nature of university student teams, motivates a dedicated investigation of the potential of applying MBSE. This paper presents the problem definition, state of the art literature review, and methodology followed to investigate the above mentioned aspects in the frame of a research project conducted at the Delft University of Technology.

## 2. Challenges Commonly Faced by Student Teams

Student Turnover and Limited Knowledge Transfer Student teams frequently face high team member turnover rates as students graduate or leave the group, causing disruptions in team dynamics and task divisions. This often results in a loss of specialized knowledge, as there is limited time or effort for proper documentation and knowledge transfer between outgoing and incoming students. Consequently, new team members may struggle to catch up or replicate previous work, which slows down progress and leads to inefficiencies.

<!-- PDF_PAGE: 2 -->

Lack of Experience University student teams are often composed of members with less real-world experience compared to industry, making it challenging to manage complex projects. Without hands-on experience, students may struggle with decision-making, project management, proper systems engineering processes, and prioritizing of technical challenges. This inexperience can lead to trialand-error approaches, mistakes, and delays in reaching effective and balanced solutions that actually achieve the initial goal of the project.

Financial Constraints Many university teams operate with minimal financial support compared to industry, limiting their ability to acquire the tools, software, or materials necessary for project success. Teams often have to rely on fundraising or limited university funding, which can lead to resource shortages. Financial restrictions can also limit opportunities for research, testing, and development.

Working Hours Constraints Balancing academic responsibilities, part-time jobs, and other extracurricular activities means students have limited time to contribute to team projects. These time constraints can hinder productivity and collaboration, as team members may struggle to coordinate schedules for meetings or complete tasks promptly. The part-time nature of student work also limits the depth of engagement with the project, affecting its overall quality.

## 3. Model-Based Systems Engineering (MBSE)

## 3.1 Introduction to MBSE

In contrast to conventional, document-centered development, in MBSE information is documented in a central digital model of the system. The creation of this central model is equivalent to system development and various artefacts, such as source code or documents, are derived from the design captured in the model [1]. Oliver Alt defines the terms abstraction, view and model in connection with MBSE.

The concept of abstraction is the targeted omission of irrelevant information. In this way, abstraction makes it possible to concentrate on the essential features of the system [1].

A view only contains the model information that is relevant for the viewer or their perspective on the model. A view uses abstraction to filter specific information from the model and make it available in a collected form [1].

of reality from which artefacts can be automatically derived. The information in an MBSE model can be understood and processed by a computer[1].

An MBSE model is an abstract and formal description

Tim Weilkiens also defines the MBSE model as a representation of the system and its environment. The model is based on a modelling language that covers the concepts of systems engineering and is therefore understandable for computers [2].

MBSE is a special type of systems engineering that formalizes the use of models in the development process to support the fulfilment of systems engineering tasks [3], [4]. Weilkiens extends this definition to include the important task of MBSE of documenting the data generated during the development process in a computer understandable way [2].

## 3.2 Advantages of MBSE

The advantages of correctly applied MBSE are improved communication between stakeholders, the reduction of risks in development, higher quality of the end product, higher productivity and easier knowledge transfer [4]. Modeling can help to overcome the three biggest challenges of systems engineering identified by Holt and Perry. These challenges are high complexity, insufficient understanding and missing or faulty communication [5]. According to Deligatti, the implementation of MBSE in the development process can be measured gradually. In addition to the completely model-based approach, in which no more documents appear, there are also many types of hybrid MBSE approaches in which important documents are derived from the model [6].

## 3.3 Definition of MBSE methodology

Deligatti defines three pillars on which MBSE is built for the development of systems. These pillars are the modelling language, the modelling method and the modelling tool. All three aspects must be coordinated with each other and with the specific MBSE project and the environment in which this project takes place [6].

The modelling language is a standardized notation for system elements and relations between them. The language is used to standardize communication within the MBSE project. Examples of modelling languages are Systems Modeling Language (SysML), Unified Modeling Language (UML) and Business Process Model and Notation (BPMN) [6].

The modelling method defines a specific way of modelling. The modelling tasks, their sequence and how the

<!-- PDF_PAGE: 3 -->

modelling tasks are to be solved using the modelling language and the modelling tool are defined in the method [7].

A modelling tool is a software tool that allows you to work with one or more modelling languages and supports the creation of MBSE models [7]. Some well-known modeling tools are Cameo Systems Modeler from Dassault Systèmes [8], Rhapsody from IBM [9], Enterprise Architect from Sparx Systems [10]. Capella, an opensource software tool developed by the Eclipse Foundation, is a unique example of a tool which is tailored to the MBSE modelling method Arcadia, while the other modelling tools can be adapted to any modelling method [11].

In his paper Survey of Model-Based Systems Engineering (MBSE) Methodologies, Estefan defines an MBSE methodology as a collection of processes, methods and tools to support systems engineering in a model-based environment. An MBSE methodology is a collection of processes, methods and tools [12].

In contrast to Delligatti, Estefan emphasizes that MBSE processes and methods can be structured hierarchically. A process is a sequence of modeling tasks that need to be fulfilled. The individual process steps are carried out with the help of methods, whereby a method at a lower hierarchy level can take on the role of a process, which in turn is executed by methods [12]. Tools facilitate the execution of methods and processes and are usually software applications. Furthermore, external factors such as social, cultural or organizational aspects must also be taken into account, as these can significantly influence the execution of methods [12].

For this paper, MBSE is used as a term according to the definitions of Friedenthal [4] and Weilkiens [2]. To practice MBSE, an MBSE methodology according to Estefan provides a set of processes, methods and tools. The three pillars of MBSE described by Delligatti, the modeling method, the modeling tool and the modeling language, must be coordinated with each other to form a coherent MSBE methodology [7].

## 3.4 State of the Art MBSE Methods

The following shows a selection of existing MBSE Methods found in literature and in industry practise.

- SysML based Methods

MagicGrid

- ESA SysML Solution

- Other Tool and Method Combinations

- Concurrent Engineering with CDP4-COMET

- Arcadia / Capella

- Data Driven Systems Engineering (DDSE) with Valispace

MagicGrid MagicGrid provides a SysML-based framework that helps guide engineers through the structured development of system models by organizing the modeling activities within a matrix style model template. The framework divides the system development into three distinct domains: the Problem domain, the Solution domain, and the Implementation domain. Each domain is represented as a row in the matrix, with the Problem domain further split into a black-box and white-box view, reflecting different levels of abstraction. The Solution domain is broken into multiple rows to represent varying levels of detail in the system's architecture. In contrast, the Implementation domain is less detailed and falls largely outside the scope of MBSE, except for the specification of implementation requirements.

The columns of the MagicGrid matrix correspond to the four fundamental types of diagrams of SysML, also referred to as the Four Pillars of SysML: Requirements, Structure, Behavior, and Parametric Diagrams. A combination of row (= domain) and column (=Pillar of SysML), represents a certain view onto the model. These views help engineers document and understand the system from different perspectives. [13]

ESA SysML Solution The ESA SysML Solution is a tailored approach to MBSE, developed specifically for the space missions and in compliance with standards provided by the European Cooperation for Space Standardization (ECSS) and systems engineering practices at the European Space Agency (ESA). Similarly to the MagicGrid framework, the ESA SysML Solution can also be organized in a grid-like overview, separating Mission Specification, System of Interest Specification (Problem Space) and Functional Design and Physical Design (Solution Space) in rows. The columns categorize the different views on the model per row into breakdown views, architecture views, states and modes views, and scenarios views. In parallel, requirements are organized in the MBSE model and links between the views are created and maintained. [14]

Concurrent Engineering with CDP4-COMET CDP4-COMET is an open-source software tool designed to support Model-Based Systems Engineering (MBSE) through the Concurrent Design method. It enables multidisciplinary teams to collaboratively develop integrated system models, allowing stakeholders to modify design pa-

<!-- PDF_PAGE: 4 -->

rameters and assess the system's performance against its requirements. By organizing the system into a modular structure, CDP4-COMET helps teams analyze key design challenges and trade-offs early in the process. The model serves as a single point of truth, ensuring all team members have access to up-to-date information they require for their domain of expertise. Systems Engineers can generate typical Systems Engineering deliverables, like technical budget reports directly from the model. The tool supports both co-located and geographically distributed teams, ensuring clear role assignments and access controls. [15]

Arcadia/Capella ARCADIA provides a method dedicated to systems and architecture engineering, supported by the Capella modeling tool. The framework defines a structured process that helps stakeholders understand the customer's real needs, define and share the product architecture, validate the design early, and manage Integration, Validation, Verification, and Qualification (IVVQ). ARCADIA is applied to complex systems, hardware, and software architectures, particularly those requiring reconciliation of constraints such as cost, performance, safety, and security. The methodology divides system development into five core engineering activities: Operational Analysis (OA), System need Analysis (SA), Logical Architecture Design (LA), Physical Architecture Design (PA), and Building Strategy Definition (BS). Each activity contributes to a detailed system model, with each engineering activity represented as a distinct perspective of the model, ensuring all aspects of the system are accounted for and aligned. [16]

Data-Driven Systems Engineering (DDSE) with Valispace Data-Driven Systems Engineering moves away from document-centric approaches by focusing on working with data points within a single source of truth application, such as Valispace. In this approach, all data is stored, accessed, and managed in a central database, eliminating the need for duplication and increasing data consistency. Engineers can reference data points in real-time from anywhere, ensuring consistent, up-to-date information across the entire development process. DDSE enables decisions and trade-offs to be made with the latest project data, which is automatically propagated throughout the system when altered. Reports in DDSE link directly to live data, always reflecting the current state of development and easily shareable with stakeholders in real-time. [17]

## 3.5 Challenges with adopting MBSE

In [18], Chami, et al. describe a number of challenges related to adoption of MBSE within an organization. The following section picks up a selection of some of these challenges and puts them into the context of university student teams.

One of the crucial challenges to master for a successful MBSE adoption, is the need to create awareness of the benefits of MBSE among the (future) practitioners and to anticipate a natural resistance to fundamentally change from a document-centric way of working to a model-based approach. While change resistance in student teams is usually lower then in most industries, creating awareness of MBSE and its benefits in contrast to document-based Systems Engineering can become more challenging, since the overall level of experience with applying Systems Engineering in complex projects is naturally lower then in industry. Without a clear demonstration of the benefits this can create a perception that the promises of adopting MBSE are rather abstract.

Upfront investments are required when starting to adopt MBSE. This includes obvious points like acquiring software licenses, but also the investment in manpower to build up experience with the tool and the specific MBSE methodology. For student teams, this challenge can be exaggerated if a commercial software is chosen, since financial constraints are usually stricter. Most universities have not yet implemented a comprehensive educational programme to teach MBSE, which will mean that at least for now a student team looking to adopt MBSE will need to resort to other means to teach its members the theory and practical aspects of working model-based. This step is crucial, since the first exposure of a student to MBSE will have an influence on their opinion about the topic.

Another important aspect, that should be considered specifically for student teams is related to the tendency of student teams to have a higher turnover rate of members. While the structured and consistent organization through the application of MBSE is a promising approach to manage technical data, knowledge about the MBSE process and its application within the project needs to be managed with a long term vision in mind. Without a clear strategy to onboard new team members for the model-based approach, the risk is that MBSE will be applied less rigorously and without following the modelling methodology correctly, which will in the end create the opposite of the intended benefits of using MBSE in the first place. To circumvent this, it is critical to use an easy to understand and clearly explained MBSE Methodology, which is adapted to the specific challenges the student team is facing.

<!-- PDF_PAGE: 5 -->

In order to fully embrace the MBSE approach, the created model needs to be the authoritative source of truth for all participants. If this is not the case and instead updating, refining and consulting the model consistently becomes an afterthought of the design process, the concept of authoritative source of truth is broken and the drawbacks of a document-centric approach persist. This situation is sometimes referred to as "shadow engineering" with the MBSE approach, which basically means that the work is done twice, if both documents and the model needs to keep up with the technical development. This being said the shadow engineering can be a sensible approach for a smaller, one-time project to show the benefits of MBSE.

## 4. Motivation

In the context of university student teams, as highlighted in the earlier sections, the challenges faced by these organisations are fairly unique. Although MBSE presents a promising option to tackle these challenges, the need for a tailored approach is apparent. This study addresses these gaps by proposing a process to engage student teams directly in n the development of an MBSE methodology tailored towards student teams. It is important to understand how collaborative engineering design is currently integrated into student teams before implementing any new approaches.

Our focus is not just on the deployment of MBSE tools but on determining which elements of MBSE can effectively solve specific issues faced by student teams. Therefore, stakeholders' perspectives, specifically the students and their advisors in the case of student teams, must be considered. By identifying these areas, we aim to build a more collaborative, and accessible approach to engineering education through student teams.

## 5. Methodology

One of the first steps of implementing MBSE into an existing framework would be to understand that MBSE should not considered a plug-and-play method. As mentioned in the previous sections, awareness of MBSE must be created among the team members to create an understanding of what changes one can expect in the organisation. In recent times, focus groups have gained popularity as a means of qualitative research. Focus groups tap into group dynamics to gain insights on topics that may be missed during one-on-one interviews. They have also proven to be more economical, spontaneous and a safe forum to carry out qualitative research [19]. Hence, this approach was found to be the most suitable one to capture the interests and opinions of all the stakeholders of student

teams.

The authors propose a workshop-based approach that involves holding multiple focus group interviews to capture the current systems engineering workflow in student teams. This interactive setting allows for a collaborative discussion, encouraging diverse perspectives from both the team members and advisors. The goal is to capture a holistic understanding of the practical challenges and the gaps in systems engineering knowledge within student teams, which will form the foundation for refining MBSE approaches tailored to these teams. The key features and recommendations for the focus group interviews are:

## 5.1 Composition

A well-structured focus group composition is essential to capture the varied interests and requirements of the stakeholders. Participant diversity should be maintained in terms of experience, competencies and roles in the team. A good focus group size would vary between 5-8 members. This strikes a balance between representing different perspectives while conforming to a feasible timeframe and calendars of everyone involved. The team could also choose to have more than one group to accommodate variable opinions or large group size. Authors encourage teams to also invite new members to provide varying perspectives.

## 5.2 Structure

Participants will engage in a single focus group session lasting approximately 60 to 90 minutes. During the session, participants will be encouraged to share their experiences and provide details on how systems engineering methodologies are applied within their teams.

An example of an ideal focus group structure would be as follows:

- 0-10 mins, Introduction and Objective setting: The session will begin with a brief introduction to the research objectives, followed by an overview of the discussion topics. It is important to encourage the Participants to share their experiences openly and freely.

- 10-25 mins, Team Composition Diagram: A visual representation of the student team's structure will be discussed in focus groups, focusing on how roles and responsibilities are distributed across the team. This can be done on a whiteboard or a bulletin board with post-its. This activity serves to establish a baseline

<!-- PDF_PAGE: 6 -->

for the next activity and to understand specific team dynamics and their collaborative working approach.

- 25-40 mins, Data Management Mindmap: A mindmap of the current data management practices are discussed. Key deliverables from the team(eg: requirements document, test plans) are captured here. Participants can be encouraged to sketch out how the data is currently being managed in the team. Participants can also discuss the ownership of data and current data transfer methods. This will serve as a good exercise to identify current discrepancies and identify areas of improvement.

- 40-60 mins, Used Tools Mindmap: During this segment, participants will identify the tools that are used at every segment and list them in the mindmap. Any existing tools that are already considered inconvenient can serve as a possible opportunity to be replaced by MBSE tools.

While this structure is aimed at capturing most of the

- 60-90 mins, Challenges and Opportunities: If not already highlighted and identified in the previous activities, this segment will serve as a means to discuss the existing challenges that students or advisors face during day-to-day operations.

The presented structure is meant to be a rough guideline for guiding the conversation during the focus group interviews. However, moderators should aim to have a more dynamic approach to capture specific concerns or issues during the interview.

## 5.3 Data Management and Processing

After the workshop, the data collected will be processed and analyzed in various stages:

- Transcription: The audio recordings from the focus groups will be transcribed to capture the full depth of participant discussions. To ensure confidentiality, all transcriptions will be anonymized, and no identifiable information will be linked to the discussion. Transcription will be done automatically with Whisper or MicrosoftTeams, with manual transcription with oTranscribe as a backup solution.

- Analysis: A qualitative analysis for the transcription using software like ATLAS.ti would serve as a basis to categorize recurring issues related to systems engineering tools, practices, and difficulties faced by student teams.

- Comparison with state of the art: The identified themes will be compared with findings from previous studies on MBSE and student engineering teams. They will also be compared with the existing tools available on the market. This comparison will highlight where student experiences align with or deviate from broader trends in MBSE implementation and educational contexts.

- Report and Requirements generation: The next step would be to report the interpretations from the analysis in the form of requirements in a true systems engineering fashion. These requirements would serve as a basis to modify an MBSE framework for student teams.

## 5.4 Ethical considerations

When working with human participants for a study, it is important to consider how data and identities are managed. For this purpose, an extensive risk management plan and a clear data management plan stating the ownership of the recorded data must be established. Participation in the study would be voluntary and participants would be informed about their rights under European General Data Protection Regulation (GDPR). Wherever possible, data should be anonymised or pseudonymised to protect identities and allow for more open discussions.

## 6. Conclusion

The approach presented in this paper aims to establish a requirements baseline for the development of an MBSE approach that caters to the specific needs of university student teams. Focus Groups have been chosen as the preferred qualitative analysis method to understand the systems engineering approach and information management within student teams. The related challenges expressed by the students will then be used to derive possible ways forward to implement MBSE in student teams.

## References

[1] O. Alt, "Modellbasierte Systemwicklung mit SysML," 2012.

[2] T. Weilkiens, Definition MBSE Model - Model Based Systems Engineering 4 You, 2022. [Online]. Available: https://mbse4u.com/2022/01/18/ definition-mbse-model/.

[3] INCOSE, "INCOSE Systems Engineering Vision 2020," 2007.

<!-- PDF_PAGE: 7 -->

[4] S. Fridenthal, A Practical Guide to SysML: The Systems Modeling Language. 2014, ISBN: 978-0128002025.

[5] J. Holt and S. Perry, SysML for systems engineering. Institution of Engineering and Technology, 2008, p. 335, ISBN: 9780863418259.

[6] L. Delligatti, "SysML Distilled," Tech. Rep., 2013.

[7] L. Delligatti, "Model-Based Systems Engineering (MBSE) with SysML - An Approach for Reducing Cost and Improving Quality," Tech. Rep., 2012.

[8] Dassault Systèmes, No Magic Cameo Systems Modeler | CATIA. [Online]. Available: https://www. 3ds.com/products/catia/no-magic/cameo systems-modeler.

[9] IBM, IBM Engineering Systems Design Rhapsody. [Online]. Available: https://www.ibm.com/ products/systems-design-rhapsody.

[10] Sparx Systems, UML modeling tools for Business, Software, Systems and Architecture. [Online]. Available: https://sparxsystems.com/.

[11] Capella, Capella | Open Source MBSE Tool. [Online]. Available: https://mbse-capella.org/.

[12] J. A. Estefan, "Survey of Model-Based Systems Engineering (MBSE) Methodologies," Tech. Rep., 2008.

[13] A. Aleksandravičiene and A. Morkevičius, "MagicGrid $ \mathbb{R} $ BOOK OF KNOWLEDGE A Practical Guide to Systems Modeling using MagicGrid from Dassault Systèmes 2nd edition," 2021.

[14] J. Whitehouse, A. Gonzalez Fernandez, A. Toan, B. Long, and E. Maleki, "ESA SysML Solution," 2022.

[15] Starion-Group, "CDP4-COMET $ ^{\mathrm{TM}} $ User manual," 2024.

[16] J.-L. Voirin, "ARCADIA USER GUIDE Arcadia Principles and Contents Overview," 2023.

[17] L. Lindblad, M. Witzmann, and S. Vanden Bussche, "DATA-DRIVEN SYSTEMS ENGINEERING: TURNING MBSE INTO INDUSTRIAL REALITY," 2021.

[18] M. Chami, A. Aleksandraviciene, A. Morkevicius and J.-M. Bruel, "Towards Solving MBSE Adoption Challenges: The D3 MBSE Adoption Toolbox," INCOSE International Symposium, vol. 28, no. 1, pp. 1463-1477, Jul. 2018, ISSN: 2334-5837. DOI: 10.1002/j.2334-5837.2018.00561.x.