---
source: null
title: "review-candidate-0895"
page_count: 4
converted_at: "2026-09-06T00:06:59Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# Heterogeneous Federated CubeSat System: problems, constraints and capabilities

</div>

Carlos Leandro Gomes Batista $ ^{*} $ , Fatima Mattiello-Francisco $ ^{*} $ , Andras Pataricza $ ^{\dagger} $

$ ^{*} $ Brazilian National Institute for Space Research,

Space Systems Engineering,

Sao Jose dos Campos, Brazil

Email: {carlos.batista, fatima.mattiello}@inpe.br

$ ^{\dagger} $Budapest University of Technology and Economics

Department of Measurement and Information Systems

Email: pataricza.andras@vik.bme.hu

Budapest, Hungary

Abstract—Different arguments were being presented in the last decade about CubeSats and their applications. Some of them address wireless communication (5G and 6G technologies) trying to achieve better characteristics as coverage and connectivity.

Some arrived with terms as IoST (Internet of Space Things), Internet of Satellites (IoSat), DSS (Distributed Space Systems), and FSS (Federated Satellite Systems).

All of them aim to use Small/NanoSatellites as constellations/swarms is to provide specific services, share unused resources, and evolve the concept of satellites-as-a-service (SaS).

This paper aims to emophasize performance attributes of such cyber-physical systems, model their inherent operational constraints and at the very end, evaluate the quality of service in terms of figures of merit for the entering/leaving of new heterogeneous constituent systems, a.k.a satellites, to the constellation. This "whitepaper"-styled work focuses on presenting the definitions of this heterogeneous constellation problem, aims at its main capabilities and constraints, and proposes modeling approaches for this system representation and evaluation.

Index Terms—cubesats, constellation, cyber-physical systems, IoSat, IoST, DSS, FSS

## I. INTRODUCTION

As the space became more and more accessible, new ways of thinking about the space services have also become more feasible. Issues, like flight formation, constellations, and swarms of satellites were always desirable for the leading space agencies and enterprises. GNSS [1], Sentinel [2], and Iridium [3] are examples of well-established satellites constellation systems, using the coordination between specific purpose developed spacecrafts for global positioning, earth observation and IoT communication, respectively.

The rapid electronics advances, increase of processing capabilities, and low power consumption changed this discussion completely. Since the introduction of the CubeSat standard [4], many works aim the exploration and development of new capabilities for these small satellites [5]. Additionally, the decreased size of these platforms also reduced the launch costs [6], [7]. Now, it is possible to, literally, launch hundreds of less than 5kg satellites, each one with entirely different

payloads, characteristics, owners, and purposes [8]. All these points lead us towards a new era of re-thinking the idea of satellite constellation systems and their applications.

This work aims to evaluate the primary constraints, problems, and capabilities of such new ideas of using CubeSats in the context of decentralized ownership of heterogeneous satellites cooperating to achieve a common goal, what we can call a Federated CubeSat System.

## II. CONCEPTS

Distributed Satellite Systems, DSS, are defined as space systems that allocate functionality through multiple constituent systems to achieve a common goal [9]. These constituent systems are generally different spacecrafts with [10]：(a) same capabilities (constellations and swarms) or; (b) fragmented functionalities, each satellite performs a different activity to achieve the main goal or; (c) decentralized ownership, a federated satellite system (FSS), where different organizations contribute with new satellites and infrastructure.

More specific about the FSS, this kind of system-of-systems establishes the active sharing of unused resources of the multiple constituent systems offered for exploitation in different ways. Shared resources from hosted payloads can service time, processing power, and data rate. Different integration concepts include Internet of Satellites, IoSat, and Internet of Space Things, IoST. They focus on communication and connectivity, relying on the involvement of the spacecrafts on what is called Inter-Satellite Networks, ISN, and Inter-satellite Links, ISL [11].

Key enabling technologies [10], like: (i) dynamic resource allocation and balancing; (ii) power-efficient software-defined radios; (iii) satellite negotiator; (iv) software-defined satellite; (v) virtual space missions, should also be taken into consideration to make these kinds of systems possible.

Once the FSS has implemented the satellite services, its generated payload data can become commodities from the user's point of view, the satellite-as-a-service (SaS). Here, we use the concept of FSS not only for spacecrafts, but we intend

<!-- PDF_PAGE: 2 -->

to expand the idea to the whole space system (space, ground, and user segments).

## III. PROBLEMS, REQUIREMENTS & CONSTRAINTS

The major problem in dealing with FSS is its lack of homogeneity [10]. Managing heterogeneity requires some common rules. Starting with a Systems Engineering approach, we must define such a system's primary needs, goals, objectives, and constraints. The goal is to develop measures that will drive each constituent system's impact, with their particular capabilities.

Let us use as an example the Brazilian Environmental Data Collection System, BEDCS, [12] and its exploitation as GOLDS - Global Open coLlecting Data System [13]. The BEDCS and GODLS serve identical overall needs, goals, and objectives, get the data from the Data Collection Platforms (DCP) spread around a specific territory, and send it to the Ground Stations. However, they differ in constraints due to the capabilities of their constituent systems (Figure 1).

For the BEDCS, we have the SCD and CBERS family satellites. These satellites differ in form, design, mission, and primary objective. The CBERS main goal is Earth Observation, and the Data Collection is secondary. Nevertheless, they share the Ground Stations and the hosted payload, which requires simultaneous access/contact with DCP and Ground Station.

The GOLDS, on the other hand, intends to use a new generation of CubeSats from CONASAT and CATARINA constellations beside the SCD and CBERS satellites. Each constellation has its particular objectives, but they will share a common goal for the GOLDS through a new hosted payload, the Environmental Data Collector (EDC), that enables the GOLDS to be global and overcome the simultaneous visibility constraint from BEDCS. Turning the data collection global, we start to deal with new constraints, such as data storage capacity and download rates.


![figure_001.png](figure_001.png)



<div align="center">

Fig. 1. Baseline and possible composition view of the BEDCS/GOLDS SoS and its constituent systems.

</div>

This simple example causes minimal impact on the individual spacecrafts. And it offers services based upon availability of the resources without modifications in the space-to-ground links. We have different satellites cooperating built up by using different technologies, from different organizations [14]. New terrestrial DCPs can enter the network, increasing the demand and the regions of interest, i.e., global. Ways to measure the quality of the service, as FSS, must be considered, even more with the effects of new arriving constituent systems.

## A. Setting up the requirements

We can derive some requirements for the constellation from the definition of the goals and objectives of the FSS.

Functional and extra-functional requirements should be derived, but how to do it once we do not control the constituent systems? One approach for that is the approach driven with the unifying concept of operation, ConOps, and its requirements [15]. The federation as a single System of Systems, SoS, has unique characteristics and requirements that the sum of its parts should meet. At the same time, every single participating satellite still keeps its original primary designated mission [16].

Back to the BEDCS/GOLDS example, we can use the ConOps characteristics [15] to define some requirements for the idealized FSS:

- Data Availability

- The data will be processed onboard for the EDC payload satellites, and on ground for SCD and CBERS satellites.

- The data must be available as soon as the Mission Center validates the acquired data.

- All the data is centralized at the Mission Center located in Brazil.

## Communication Architecture

- Each satellite must define its particular downlink data rates in compliance with its ground stations.

- The access link between any satellite and the ground stations must be enough to download all the data from one complete orbital period.

- The access link between any satellite and one DCP must be enough to upload all the DCP data available.

- The revisit time (time between two consecutive overpasses on the same target) for one DCP must not be more than 1 hour.

## Tasks, Scheduling and Control

- The use and control of the hosted payload, EDC, must respect the BEDCS/GOLDS decisions and the satellite resources availability.

- All the federated ground stations must be capable of controlling the hosted payload, EDC.

## Timeline

- The BEDCS/GOLDS must have the flexibility to receive new satellites with the hosted payload, EDC, to its federation.

- The BEDCS/GOLDS must have the flexibility to retire satellites from its federation to maintain the federation quality of service.

## Fault Management

- In case of a fault on an FSS constituent system, the Mission Center must be able to perform a reconfiguration on the FSS resources.

- The time for reconfiguration must not exceed one operation planning period (operational activity when all the operational procedures are planned for a

<!-- PDF_PAGE: 3 -->

specific period of time, i.e., overpasses, flight plans, calibration, etc.).

As a System of Systems, an FSS evolves. Its behavior can be defined in terms of its systems independence and interoperability or, to be more specific, retrofitting, which is the capability for systems to interoperate on-demand to meet mission objectives as soon as a new satellite arrives/leaves the federation [17].

## B. Constraints

Even knowing the overall objectives of an FSS, some items can remain fuzzy, again, due to the heterogeneity of the constituent systems. How to dynamically integrate unknown resources? Will the system correctly provide the services? Looking at the limitations of our system is, sometimes, more productive. The constraints of the FSS can best formulate the boundaries of its solution space.

The requirements presented earlier can be refined into more detailed requirements and resource constraints. Data availability requirements create constraints on each constituent satellite on data storage and processing. Communication Architecture characteristics derive constraints on bandwidth and data rates to download DCP data. Power consumption and federation engagement time on available resources constrain satellite control and tasks scheduling. The deployment/retirement of new satellites requires a capability of reconfiguration and retrofitting on the FSS. Fault management requirements also influence the FSS configuration.

Extensibility demands the introduction of quality measures into the set of requirements. The respective required minimal and offered values for new constituent satellites decide their integration. , e.g., at least 90% of all DCP coverage, minimum of 10% engagement time for non-dedicated satellites, 2 GB DCP data storage capacity, 2W peak power consumption, one day revisit time, minimum 10 minutes ground station access time per day, at least one dedicated ground station and communication channel [13].

For example, Figure 2 shows the constraint of the BEDCS/GOLDS satellites coverage of DCP.


![figure_002.png](figure_002.png)



<div align="center">

Fig. 2. Coverage Constraint Problem for BEDCS.

</div>

Note that, on BEDCS satellites, the access only exists if the satellite can 'view' the DCP and the Ground Station simultaneously, it is a COVERAGE constraint problem.

From now on, we will handle these constraints with the help of the mathematical paradigm called the Constraint

Satisfaction Problem (CSP). CSP is an approach that facilitates estimating a single solution, all solutions or the best solution for problems with limitations or conditions, defined into a domain set.

We can define each DCP as a region of interest (ROI) for the satellite and has its field of view (FOV).

$$
R O I = \left[ R O I _ {1}, R O I _ {2}, \dots , R O I _ {n} \right]
$$

The same for the ground station(s):

$$
G r S t = \left[ G r S t _ {1}, G r S t _ {2}, \dots , G r S t _ {n} \right]
$$

The Satellite has its FOV but it changes over time (orbit):

$$
S a t = [ f o v (t) ]
$$

If we deal with different satellites:

$$
S a t = \left[ f o v _ {1} (t), f o v _ {2} (t), \dots , f o v _ {n} (t) \right]
$$


![figure_003.png](figure_003.png)



<div align="center">

Fig. 3. BEDCS Coverage Constraint Problem Model

</div>

Once the constraints are satisfied we have a successful access as can be viewed at the Figure 3.

As the satellite FOV changes over time, we will have an solution for each instant of time.

Given a time interval $ t=[0,\dots,k] $ , the sum of these solutions for a specific ROI will give us the COVERAGE characteristic of the satellite for that ROI.

Moreover, if we have a constellation of n satellites, we can derive the constellation COVERAGE for a specific ROI as the sum of each satellite set of solutions.

As we go to the GOLDS concept and the hosted EDC payload, the same problem of COVERAGE transforms itself into a CSP on data storage. The covered DCP networks upload to the satellite an amount of data associated with each ROI:

$$
D a t a = \left[ D a t a _ {1}, D a t a _ {2}, \dots , D a t a _ {n} \right]
$$

Nevertheless, the satellite has two parameters, FOV and available storage at that specific time, storage(t).

$$
S a t = \left[ \left(f o v (t), s t o r a g e (t)\right) \right]
$$

Again, if we deal with different satellites:

$$
S a t = \left[ \left(f o v _ {1} (t), s t o r a g e _ {1} (t)\right), \dots , \left(f o v _ {n} (t), s t o r a g e _ {n} (t)\right) \right]
$$

<!-- PDF_PAGE: 4 -->


![figure_004.png](figure_004.png)



<div align="center">

Fig. 4. Data Access as Coverage Constraint Problem Model

</div>

Once the constraints are satisfied, we have successful access as can be viewed in Figure 4.

As the satellite FOV changes over time, we will have a solution for each instant of time.

Given a time interval $ t=[0,\dots,k] $ , the sum of these solutions for a specific ROI will give us the COVERAGE characteristic of the satellite for that ROI.

Moreover, if we have a constellation of n satellites, we can derive the constellation COVERAGE for a specific ROI as the sum of each satellite set of solutions.

So, evaluating the actual configuration characteristics (i.e. coverage, available satellites, ground stations, storage data, power, revisit time) and the desired configuration to achieve the expected quality of service is a must. This reconfiguring capability configures an FSS emerging behavior by translating into a Constraint Optimization Problem instead of a satisfaction-only problem optimizing service provision with available resources.

At the end, the sum of sets of solution for a specific ROI of the BEDCS and EDC satellites give us the COVERAGE of the GOLDS for that specific ROI.

## IV. CONCLUSION

Developing a Distributed Satellite System is a challenge task. Validating this idea using CubeSats can be gamechanging for the next years. Distributed CubeSat Systems have not yet been demonstrated in large scale, with exception of Planet and Spire over more than 40 proposed constellations and Federated CubeSats concepts have not yet flight.

We propose a possible protocol/process to validate the impacts on a heterogeneous federate CubeSat system of a new satellite or group of satellites deployed in orbit to work in this federation. What is the problems inherent to this kind of system? What to expect from the evolution of this SoS? How much can be modeled once we do not have control over the constituent systems?

Using the BEDCS/GOLDS constellation as an example, we could translate some of the main characteristics of such constellation concepts. We could also start to theorize over this complete satellite system (space, ground, and user segment) as an idea of cooperation and sharing of resources.

Another thing is how to simulate the system. As a dynamic system, the federated CubeSat system and its constituent satellites time dependent, and the fulfillment of their constraints

will also change over time. Some tools can be used for that, orbit simulators are well-known but some work is necessary, e.g. NASA General Mission Analysis Tool. Mainly we focus about the representation of the resources available at the system.

We still have significant work to do, not only on the modeling/model side but also on correctly picking the main attributes of this kind of constellation to better formulate the questions we have been asked during this whole paper.

## REFERENCES

[1] B. Hofmann-Wellenhof, H. Lichtenegger, and E. Wasle, GNSS-global navigation satellite systems: GPS, GLONASS, Galileo, and more. Springer Science & Business Media, 2007.

[2] E. Attema, P. Snoeij, G. Levrini, M. Davidson, B. Rommen, N. Floury, B. Duesmann, B. Rosich, A. Pietropaolo, V. Mastroddi et al., "Sentinel-1 mission capabilities," ESA Special Publication, vol. 677, p. 45, 2010.

[3] K. Maine, C. Devieux, and P. Swan, "Overview of iridium satellite network," in Proceedings of WESCON'95. IEEE, 1995, p. 483.

[4] J. Puig-Suari, C. Turner, and R. Twiggs, "CubeSat: the development and launch support infrastructure for eighteen different satellite customers on one launch," 15TH Annual/USU Conference on Small Satellites, pp. 1-5, 2001. [Online]. Available: http://digitalcommons.usu.edu/smallsat/ 2001/All2001/59/

[5] National Academies of Sciences, Engineering, and Medicine, Achieving Science with CubeSats: Thinking Inside the Box. Washington, DC: The National Academies Press, 2016, no. September. [Online]. Available: http://www.nap.edu/catalog/23503

[6] E. Kulu, "Small Launchers-2021 Industry Survey and Market Analysis," 2021 IAC Proceedings, vol. 13, no. October, pp. 25-29, 2021. [Online]. Available: www.newspace.im

[7] W. Fox, "Launch costs to low earth orbit, 1980-2100: Future timeline, data & trends, future predictions," accessed: 2021-01-05. [Online]. Available: https://www.futuretimeline.net/data-trends/6.htm

[8] "India launches record 104 satellites at one go," Feb 2017, accessed: 2021-01-05. [Online]. Available: https://www.reuters.com/article/us-space-launch-satellites-india-idUSKBN15U0EI

[9] D. Selva and D. Krejci, "A survey and assessment of the capabilities of Cubesats for Earth observation," Acta Astronautica, vol. 74, pp. 50-68, 2012.

[10] C. Cappelletti, S. Battistini, and B. K. Malphrus, Cubesat Handbook. Academic Press, 2021.

[11] A. Golkar, "Federated Satellite Systems (FSS): A Vision Towards an Innovation in Space Systems Design," 9th IAA Symposium on Small Satellites for Earth Observation, 2013.

[12] W. Yamaguti, E. A. Ribeiro, J. C. Becceneri, and S. N. Itami, "Collection and treatment of the environmental data with the brazilian satellite scd1," Revista Brasileira de Ciencias Mecanicas (ISSN 0100-7386, vol. 16, pp. 205-211, 1994.

[13] F. J. Vidal et al., "Global open collecting data system (golds): Proposta de requisitos para o desenvolvimento da especificação do sistema," Revista de Tecnologia da Informação e Comunicação, vol. 10, no. 1, pp. 1-5, 2021.

[14] A. Golkar and I. Lluch I Cruz, "The Federated Satellite Systems paradigm: Concept and business case evaluation," Acta Astronautica, vol. 111, pp. 230-248, 2015. [Online]. Available: http://dx.doi.org/10. 1016/j.actaastro.2015.02.009

[15] W. J. Larson and J. R. Wertz, Space mission analysis and design. Space Technology Library, 1999, vol. 29, no. 09.

[16] R. Akhtyamov, R. Vingerhoeds, and A. Golkar, "Identifying retrofitting opportunities for federated satellite systems," Journal of Spacecraft and Rockets, vol. 56, no. 3, pp. 620-629, 2019.

[17] A. M. Madni and M. Sievers, "System of Systems Integration: Key Considerations and Challenges," Systems Engineering, vol. 17, no. 3, pp. 330-347, 2014.