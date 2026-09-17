---
source: null
title: "review-candidate-1317"
page_count: 4
converted_at: "2026-09-06T00:56:03Z"
---

<!-- PDF_PAGE: 1 -->

IAC-18-B4.6A.6.x42844

<div align="center">

# Enabling Technologies and Processes for Space Missions - the S2TEP Platform

</div>

Frank Dannemann $ ^{1)} $ , Caroline Lange $ ^{1)} $ , Michael Jetzschmann $ ^{1)} $

$ ^{1} $ German Aerospace Center (DLR), Institute of Space Sytems, Bremen, Germany, {frank.dannemann, caroline.lange, michael.jetzschmann} @dlr.de

Inventing and integrating new technologies into todays spaceborne platforms is inevitable for the technical demands, cost-effectivenes and tight schedules of future missions. The German Aerospace Center (DLR) as the national aeronautics and space research center of the Federal Republic of Germany plays a central role within this demanding task. DLR focuses on technology research, development and maturation, working closely together with universities at basic research level on the one hand, and with industry at application level on the other hand.

The Small Satellite Technology Experiment Platform S2TEP is DLR's workhorse for doing this kind of research and development: focusing on scientific and technological needs and societal relevance, the S2TEP platform with its modular and scalable design offers the possibility to demonstrate novel technologies and increase their Technology Readiness Level (TRL) from 6 to 9 by in-orbit test and verification. This is absolutely necessary for doing innovative and pioneering research and development, thereby providing flight-proven technologies to future scientific and commercial missions.

The initial research on subsystem level is concentrated on the classical core avionic technologies like the on-board computer, the on-board software, as well as power- and communication systems. But this list is open for further expansions in terms of its research scope, and national as well as European initiatives provide a fertile cooperation environment. By putting a huge emphasis on scalability from component to system level, the developed technologies have the potential to leave the small satellite scope and be integrated into larger satellites as well. The flexibility of S2TEP-based missions is further extended by using a model-based design process and software development, simulation and automatic verification at different levels as well as a decentralized operational concept with a high degree of autonomy.

Within this paper we will give an overview of the S2TEP platform and its first mission, which will start in early 2020. We will describe the novel development processes and the technologies forming the platforms baseline architecture. Finally, we will shed light on future missions, the needed platform configurations and resulting from this - on prospective research and development challenges.

## I. INTRODUCTION

Satellites have a great impact on our daily life, enabling for instance global communications and navigation services or weather forecasts. The space research conducted by DLR has made, and continues to make, important contributions within this sector, enabling the digitalization and mobility of the future.

In order to promote space flight research, as well as supporting new innovative technologies, DLR develops and flies its own satellite platforms in scientific missions on a regular basis. This will make significant contributions by

- promoting innovation in all aspects of a space mission (space-, ground- and launch-segment), and thus improving the end-to-end system expertise,

- providing DLR with an independent access to spacebased research and technology demonstration as well as providing autonomy by removing the dependency on third party providers,

- promoting interdisciplinary cooperation between DLR institutes and exploiting synergies, and

- inviting external institutions and industries for national and international collaborations.

## The Idea behind S2TEP

The subsystems of a satellite are often mission specific developments. This limits the ability for reuse in other missions, and makes adaptations to new requirements difficult. To streamline this process, DLR is developing its own satellite platform, designing main avionic components that are easily adaptable, and at the same time utilizes the latest research and technology. The platform offers a higher degree of flexibility, enabling short-term design adjustment as well as the ability to adapt essential cost drivers and shorten the development time [1,2].

<!-- PDF_PAGE: 2 -->

## II. S2TEP DEVELOPMENT PHILOSOPHY

The S2TEP avionics introduce a variety of innovative technologies, a modular and flexible architecture as well as novel design and verification processes like:

- Scalable on-board computer (in terms of essential parameters such as computing power, reliability, interfaces and communication capabilities)

- Model-based software development & auto coding

- Software defined radio

- Wireless communication network

- Scalable power system

- Decentralized operation concept with a high degree of autonomy

- Model-based systems engineering ("Space 4.0")

- Simulation & automatic verification

The DLR developed avionic components will be flown on S2TEP-based missions as either technology demonstrations or bus components, depending on their degrees of maturity. S2TEP based missions will offer an ideal test environment for technology demonstrations and research within the field of avionics, and thus contributing significantly to the gain of comprehensive and deep design understanding within this field.

The same principle applies to the innovative system development and mission operation processes which are developed within the frame of the S2TEP platform. After maturation they can also be applied to many other space missions.

## III. MODEL-BASED SYSTEMS ENGINEERING

Aiming for re-usability also on Systems Engineering (SE) level is one overarching goal of the development process of the S2TEP platform. Introducing Model-based Systems Engineering (MBSE) on design, building, integration, testing and also mission operation level are the first steps in this direction. MBSE is especially characterized by the fact, that an explicit model is used as a representation of the system. Using this model as the base, typical SE tasks like change- and interface management, system design and -analysis as well as verification and validation will be performed. Using the system model as single source of information avoids inconsistencies and double work and speeds up the overall development process [3,4].

## IV. S2TEP TECHNOLOGIES

The technologies developed for the micro-satellite platform S2TEP are also used for DLR's mini-satellite platform COMPSAT. Their high degree of scalability creates a synergy between both platforms, enabling technology exchange and allows for a high degree of re-usability. Technologies which are flown on COMPSAT as secondary payloads can later be flown on S2TEP as critical bus components, and vice versa, making both platforms test beds for new developments.

To maintain a high level of flexibility, on both component and system level, the research and development work is focused mainly on scalability in terms of performance, adaptability and reliability. The S2TEP philosophy is further explained below, using two of the developed technologies as examples: the modular software platform and the scalable on-board computer.

## Scalable On-Board Computer

The Compact On-Board Computer (COBC) is easily adaptable and can be customized to fulfill a large range of control and data processing requirements. The generic design of the computer facilitates the usage of electric components of different qualification levels, adds the ability to change processor performance, memory size and type, as well as the number and type of interfaces [6, 7]. The on-board computer will be flown on the first COMPSAT satellite Eu:CROPIS [5] as a technology experiment, and after in-orbit verification, on S2TEP as part of the bus, and on the second COMPSAT mission as the payload computer.

## Modular software platform

The Open Modular Software Platform for Spacecraft (OUTPOST) was originally developed for the on-board computer COBC, but is now also being used for the S2TEP and COMPSAT platforms [8], as well as in sounding rockets and launchers. The usage of abstraction layers, towards hardware and operating system, creates a strong foundation for modular and portable implementations of flight software. The key elements of OUTPOST have been released under an open-source license, available to private and industrial users, for possible joint further developments.

## Scalable Power System (SPS)

Currently implemented as modules for the SpaceVPX backplane standard, the S2TEP power subsystem is scalable in terms of the solar array power conversion capability, the available secondary voltages, the maximum power delivered to subsystems as well as the number

<!-- PDF_PAGE: 3 -->

of switches for individual subsystem connected via the backplane or the harness. Based on COTS components, it is most flexible in terms of reliability and redundancy by implementing modularity on circuit and component level. Finally, the usage of automated design techniques which are connected to the systems power requirements allows for short design cycles when adapting the SPS to the new small satellite missions.

## Generic Software Defined Radio

Software-Defined Radios (SDRs) are widespread used in current satellite communication technologies. Developed for terrestrial applications, the needed hardware technologies for a highly integrated SDR for reliable multiband operation in space are currently not available. Within the frame of the S2TEP platform first steps towards preparing the SDR system for low earth orbit applications are being taken. SDR technologies are independent from current frequency band limitations (e.g. for TM/TC) and allows the operation of multiple radio frequency related applications (e.g. AIS, ADS-B). Currently available in a Eurocard form-factor with VPX-Backplane connection, its motherboard-/daughterboard design facilitates the simple and cost-efficient re-use and modification of the SDR system [911].

## Wireless Communication Network

S2TEP will be one of the first satellite platforms heavily relying on a wireless communication network, which is reliable, provides a deterministic behavior and low latencies. On the physical layer, the network will be interference-free and immune against multipath fading while having low power spectral density. The most prominent use cases for the network will be its usage for AIT (mainly thermal vacuum campaigns), as a wireless EGSE and/or debug interface, for intra-satellite communication as well as for late-access during the final checkout procedures at the launch site [14,15].

## V. S2TEP PLATFORM CONFIGURATION

As the S2TEP platform is aiming for a larger satellite class, current structural approaches from the cubesat sector would produce too much system overhead regarding the overall platform configuration. Therefore a new methodology for the definition of scalability was developed: different technology experiments and payloads were selected to be used on the S2TEP platform, resulting in a reference mission which serves as baseline. Though the system design shall be scalable to broaden the range of possible payloads, the goal was not to serve all payloads with the same design, but to create a modular and

scalable system that can be adapted with little effort in a certain range to different missions.

Therefore, investigations were undertaken to define minimum and maximum platform variants - leading to a system configuration with three large sub-assemblies: the bus compartment, the solar panels/hood and the payload compartment. The bus compartment consists of the launch adapter ring interface plate and sub-compartments for avionics, COTS-units and propulsion. For payloads three different zones are foreseen: a variable payload compartment, a zone inside the avionic compartment and the last zone directly on the solar panels [13].

## VI. S2TEP HOSTED CONTROL CENTER

Low-cost satellite mission based-on the S2TEP platform also demand for an easy and affordable access to a Mission Control System (MCS). Working closely together with the S2TEP space-segment team and taking their requirements into account, the German Space Operations Center (GSOC) developed the Hosted Control Center (HCC). HCCs core is a multi-client capable MCS, that provides external access for satellite owners, payload operators and other users. Multiple instances of the MCS can be used in parallel to operate different satellites simultaneously. Providing this kind of external access allows for a much stronger interaction between the space- and the ground-segment teams, as the HCC can already be used during the early development and integration phases of the spacecraft. Offering a completely new way of operating satellites, the decentralized operation and the absence of dedicated control rooms and dedicated operation teams reduces the ground-segment costs significantly [12].

## VII. CONCLUSIONS

The S2TEP platform offers an ideal testbed for technology development and maturation as well as serving as a satellite bus for many distributed payloads. The usage of new development processes and the flexibility of a hosted control center solution completes the picture and clearly shows, that S2TEP is a research enabler for current and future satellite systems.

## REFERENCES

[1] Dannemann, F.; Jetzschmann, M.: Technology-Driven Design of a Scalable Small Satellite Platform Proceedings of 4S Symposium 2016, Malta, 2016

[2] Jetzschmann, M.; Dannemann, F.; Lange, C.; Gartner, T.: Scalability and Modularity as Dimensions

<!-- PDF_PAGE: 4 -->

of Flexibility of a Microsatellite Platform 68th International Astronautical Congress (IAC), Australien, 2017

[3] Fischer, P. M.; Lüdtke, D.; Lange, C.; Roshani, F.C.; Dannemann, F.; Gerndt, A.: Implementing modelbased system engineering for the whole lifecycle of a spacecraft CEAS Space Journal, 9 (3), pages 351- 365, Springer, ISSN 1868-2502, 2017

[4] Lange, C.; Grundmann, J. T.; Kretzenbacher, M.; Fischer, P. M.: Systematic reuse and platforming: Application examples for enhancing reuse with model-based systems engineering methods in space systems development Concurrent Engineering Research and Applications, SAGE Publications Ltd STM., DOI: 10.1177/1063293X17736358, ISSN 1063-293X, 2017

[5] Hauslage, J.; Lebert, M.; Müller, H.: Eu:CROPIS - Euglena and Combined Regenerative Organic-food Production in Space Life in Space for Life on Earth (Joint Life Sciences Meeting of ISGP, ESA and CSA), 2014

[6] Treudler, C. J.;Schröder, J.C.; Greif, F.; Borchers, K.; Aydos, Gökce; Fey, G.: Scalability of a base level design for an on-board-computer for scientific missions Data Systems In Aerospace (DASIA), Polen, 2014

[7] Gärtner, T.; Treudler, C. J.; Dannemann, F.; Jetzschmann, M.: Scalable Avionics for the DLR Micro- and Minisatellite Platforms S2TEP and COMPSAT Data Systems In Aerospace (DASIA), Schweden, 2017

[8] Dannemann, F.; Greif, F.: Software Platform of the DLR Compact Satellite Series Proceedings of 4S Symposium 2014, Spanien, 2014

[9] Budroweit, J.; Kölpin, A.: Design challenges of a highly integrated SDR platform for multiband spacecraft applications in radiation environments IEEE Radio & Wireless Week 2018, Anaheim, USA, 2018

[10] Budroweit, J.: Design of a highly integrated and reliable SDR platform for multiple RF applications on spacecrafts IEEE Global Communications Conference GLOBECOM, Singapur, 2017

[11] Budroweit, J.: Software-defined radio with flexible RF front end for satellite maritime radio applications, CEAS Space Journal, 8 (3), Seiten 201-213, Springer, DOI: 10.1007/s12567-016-0121-9, ISSN 1868-2502, 2016

[12] Roshani, F.-C.; Sellmaier, F.; Schmidhuber M.; Morfill, G.; Klein, B.; Gnat, M.: Hosted Control Center for Small Satellites Proceedings of 4S Symposium 2016, Malta, 2016

[13] Reershemius, S.; Spröwitz, T.; Jetzschmann, M.; Dannemann, F.: S2TEP - A new scalable Satellite Platform European Conference on Spacecraft Structures, Materials and Environmental Testing (ECSSMET) 2018, ESA/ESTEC, Netherlands, 2018

[14] Drobczyk, M.; Martens, H.: Deployment of a Wireless Sensor Network in Assembly, Integration and Test Activities Proceedings ofIEEE International Conference on Wireless for Space and Extreme Environments (WiSEE), Aachen, Germany, ISBN 978- 150902609-8, 2016

[15] Drobczyk, M.; Martens, H.: A study on low-latency wireless sensing in timecritical satellite applications Proceedings of IEEE Sensors IEEE Sensors 2016, Orlando, USA, DOI: 10.1109/ICSENS.2016.7808889, ISBN 978-1-4799-8287-5, 2016