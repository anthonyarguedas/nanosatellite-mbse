---
source: null
title: "review-candidate-1493"
page_count: 99
converted_at: "2026-09-06T01:26:25Z"
---

<!-- PDF_PAGE: 1 -->

Keio Associated Repository of Academic resources

<table border="1"><tr><td>Title</td><td>Design of Reusable Software for Attitude Determination System of Micro/Nano Satellites in Consideration of Modularity and Extensibility using SysML</td></tr><tr><td>Sub Title</td><td></td></tr><tr><td>Author</td><td>Nguyen, Son Duong(Nishimura, Hidekazu)西村,秀和</td></tr><tr><td>Publisher</td><td>慶應義塾大学大学院システムデザイン・マネジメント研究科</td></tr><tr><td>Publication year</td><td>2015</td></tr><tr><td>Jtitle</td><td></td></tr><tr><td>JaLC DOI</td><td></td></tr><tr><td>Abstract</td><td></td></tr><tr><td>Notes</td><td>修士学位論文.2015年度システムエンジニアリング学第179号</td></tr><tr><td>Genre</td><td>Thesis or Dissertation</td></tr><tr><td>URL</td><td>https://koara.lib.keio.ac.jp/xoonips/modules/xoonips/detail.php?koara_id=KO40002001-00002015-0007</td></tr></table>

慶應義塾大学学術情報リポジトリ(KOARA)に掲載されているコンテンツの著作権は、それぞれの著作者、学会または出版社/発行者に帰属し、その権利は著作権法によって保護されています。引用にあたっては、著作権法を遵守してご利用ください。

<!-- PDF_PAGE: 2 -->

Master's Dissertation

Design of Reusable Software for Attitude Determination System of Micro/Nano Satellites in Consideration of Modularity and Extensibility using SysML

Nguyen Son Duong (Student ID Number: 81334561)

Supervisor: Prof. Hidekazu Nishimura

September 2015

Graduate School of System Design and Management Keio University Major in System Design and Management

<!-- PDF_PAGE: 3 -->

<div align="center">

# SUMMARY OF MASTER'S DISSERTATION

</div>

<table border="1"><tr><td>Student Identification Number</td><td>81334561</td><td>Name</td><td>Nguyen Son DUONG</td></tr><tr><td colspan="4">Title
Design of Reusable Software for Attitude Determination System of Micro/Nano Satellites in Consideration of Modularity and Extensibility using SysML</td></tr><tr><td colspan="4">Abstract
Today, micro and nano satellites are being widely used for Earth observation, remote sensing, technology demonstration and scientific purposes with lower cost and shorter time development in compare with larger satellites. The micro/nano satellites projects are usually varied according to missions and hardware constraints. Among on-board software components, attitude determination software is one of the most difficult parts when coding because it requires complicated calculations, especially for the micro/nano satellites. The ratio of the attitude determination software can be estimated about 40% in total on-board software of satellites. Therefore, design of the reusable attitude determination software which can be reused for many types of the micro/nano satellite projects to save time and cost for satellite development is the objective of this research.
NASA has already realized software reusability viewpoint in NASA Reuse Readiness Levels (RRLs). NASA RRLs is a method to measure the potential of reuse of general software and has 9 topic areas including documentation, modularity, extensibility, etc. After analyzing the context of attitude determination software reuse between micro/nano satellites projects, the modularity and extensibility are critical and therefore selected in this research.
Model-based systems engineering (MBSE) is a powerful approach to model complex systems such as the satellites. Systems Modeling Language (SysML) is a standardized language to enable MBSE. Applying SysML to design the satellite and the on-board software has outstanding benefits and is now very promising. By using SysML, not only the software itself is designed but also the whole system can be modeled as well. This point is very important when reuse software because the attitude determination software has constraints and relationships with other systems of the satellite. Besides, by using SysML, not only the modularity and extensibility but also the documentation is well supported.
In brief, by using SysML and utilizing the viewpoint of modularity and extensibility from NASA RRLs, the highly modular and extensible attitude determination software has been designed in this research in order to maximize the potential of reuse for micro/nano satellites. For future works, the necessary of applying SysML for designing satellites should be more persuaded to the satellite developers.</td></tr><tr><td colspan="4">Key Words(5 words): SysML, micro/nano satellites, attitude determination software, design reusable software, NASA RRLs.</td></tr></table>

<!-- PDF_PAGE: 4 -->

## Acknowledgements

I would like to thank my supervisor, Prof. Nishimura Hidekazu, without his supports and guidance during my 2 years at Keio SDM, this thesis could not be finished. He has provided us many professional software tools to practice SysML such as Rhapsody and Cameo Enterprise Architecture. I will apply knowledge about model-based system engineering (MBSE) and SysML learning from him to design satellites when I come back to my country.

I would like to thank Prof. Seiko Shirasaka for his regular meetings to improve the quality of my research. I also would like to thank Prof. Makoto Ioki for his useful advices and comments to my thesis.

I also would like to thank Shusaku Yamaura-sensei, Takashi Hiramatsu-sensei and Ayumu Tokaji-sensei, who have continuously help me to do this research as well as to finish my study at Keio SDM.

Lastly, I would like to thank my organization, Vietnam National Satellite Center, and my family who gave me a great deal of encouragement.

<!-- PDF_PAGE: 5 -->

## Table of Contents

I. Introduction...1

I.1. Problem background...1

I.2. Definition of software reuse...3

I.3. The software reusability viewpoint from NASA RRLs...3

I.4. The benefits of applying MBSE and SysML to design software for complex systems...6

I.5. Research objective and approach...7

I.6. Structure of the Thesis...8

II. Overview of attitude determination system and constraints of design reusable attitude determination software...10

II.1. Overview of attitude determination and control system of satellite...10

II.2. The modes of attitude determination...12

II.3.The constraints of design reusable attitude determination software for micro/nano satellites...15

III. Design of reusable attitude determination software for micro/nano satellites using SysML...16

III.1. Software architecture...16

III.2. Design of software modules...24

III.3. Design of software components of sensors processing module...33

III.4. Design of software components of reference vectors estimation module...51

III.5. Design of software components of attitude estimation module...53

III.6. The modularity and extensibility in design...55

IV. Verification and Validation...58

IV.1. Verification...58

IV.2. Validation...60

V. Conclusion...62

V.1. Summary...62

V.2. Future works...62

References...63

List of Figures...65

List of Tables...67

Appendices...68

<!-- PDF_PAGE: 6 -->

## I. Introduction

## 1.1. Problem background

The weight of micro satellites is in the range of 10-100 kg and that of nano satellites is in the range of 2-10 kg [1]. The micro and nano satellites are now becoming a new trend. There are more and more companies and organizations who are interested in developing these types of satellites [1], [2]. In 2014, there were 158 micro/nano satellites launched globally, this showed an increase of nearly 72% compared to 2013 [3]. The characteristics of micro/nano satellites are low cost, short time development, varied on mission requirements and limited on calculation capability compare with larger satellites.

Software coding is always the difficult task in satellite development because it requires a lot of time for developing and testing, especially for the micro/nano satellite projects. For each project, developers need to design and implement software for satellite's on-board computer including attitude determination software. The attitude determination software is one of the most complicated parts of the on-board software because it involves complex calculations [4] [5].

In the Table 1.1.1, the estimating software components of a typical satellite are showed [6]. Form the Table 1.1.1, the software components related to the attitude determination and control are the main part of the satellite on-board software, and nearly 40% is the attitude determination software. Therefore, development of the attitude determination software is more expensive and time consuming than other software components.

<div align="center">

Table 1.1.1. Estimating source lines of code for typical satellite functions

</div>

<table border="1"><tr><td>Software Component</td><td>Source Lines of Code</td></tr><tr><td>Executive</td><td>1,000</td></tr><tr><td>Communication</td><td>5,500</td></tr><tr><td>Attitude/Orbit Sensors Processing</td><td>8,100</td></tr><tr><td>Attitude Determination and Control Kalman Filter</td><td>29,800-33,8006,000-10,000</td></tr><tr><td>Attitude Actuator Processing</td><td>3,900</td></tr><tr><td>Mathematic Utilities</td><td>5,700</td></tr><tr><td>Fault Detection</td><td>11,500</td></tr><tr><td>Other Functions</td><td>5,000</td></tr></table>

<!-- PDF_PAGE: 7 -->

Software reuse for the attitude determination system is expected as a solution to save time and cost of satellite development, especially for organizations like Vietnam National Satellite Center (VNSC), who need to develop not only one but several micro/nano satellites for different type of applications. Software reuse can help save time and cost for coding and testing as well as increase software reliability.

However, according to Ref. [7], research on on-board software reusability is still low and its realization is urgently desired. The main reasons are the difficulties of software reuse in terms of the difference in CPU type, interfaces and mission requirement of the micro/nano satellites.

The constraints which lead to the difficulties of software reuse between micro and nano satellite projects can be showed in an example in Table 1.1.2. As can be shown in the Table 1.1.2, each of the satellite projects has the different mission as well as the determination accuracy requirement, the calculation performance of the on-board computer and the model of used sensors. Therefore, in order to be reused, the attitude determination software need to be designed to deal with the variety of each satellite projects. For example, it is difficult to reuse the attitude determination software from the first satellite project (Micro Dragon) to the second satellite project (Nano satellite) because the second satellite does not have the Star Tracker as the first satellite and the performance of the on-board computer is lower.

<div align="center">

Table 1.1.2. Example of the different mission requirements and hardware constraints between micro/nano satellites projects

</div>

<table border="1"><tr><td>Satellite Projects</td><td>Mission</td><td>Determination Accuracy</td><td>On-board Computer Performance</td><td>Sensors Model</td></tr><tr><td>MicroDragon(50kg)</td><td>Ocean color observation</td><td>~0.05°</td><td>48 MIPS64 MB SDRAM</td><td>1 Star Tracker6 Sun SensorsHigh Accuracy Gyro</td></tr><tr><td>Nano Satellite(3kg)</td><td>Communication</td><td>~3°</td><td>16 MIPS8MB SDRAM</td><td>0 Star Tracker3 Sun SensorsLow Accuracy Gyro</td></tr><tr><td>Micro Satellite(100kg)</td><td>Astronomy</td><td>~0.003°</td><td>96 MIPS64 MB SDRAM</td><td>2 Star Trackers6 Sun SensorsHigh Accuracy Gyro</td></tr></table>

<!-- PDF_PAGE: 8 -->

## 1.2. Definition of software reuse

The purpose of software reuse is to improve software quality and productivity. Software reuse is the use of existing software or software knowledge to construct new software. Reusable assets can be either reusable software or software knowledge. Reusability is a property of a software asset that indicates its probability of reuse [8]. A software artifact is any item which is created during the software development life cycle. A software asset is an artifact which has a particular value. A software component is a clearly delineated piece of software that performs a useful function within a software system [9].

Reusable software artifacts are not limited to just code. These assets may include algorithms and models, architectures and design patterns, systems modules and scripts, technical documentation and test results, and use metrics as well as other artifacts produced during the software development life cycle [10]. Therefore, the software developers can reuse requirements documents, design structures and any other development artifact.

The potentially reusable aspects of software projects are shown in Table I.2.1 [11].

<div align="center">

Table 1.2.1. Reusable aspects of software projects

</div>

<table border="1"><tr><td>1. Architectures</td><td>6. Templates</td></tr><tr><td>2. Source code</td><td>7. Human Interfaces</td></tr><tr><td>3. Data</td><td>8. Plans</td></tr><tr><td>4. Designs</td><td>9. Requirements</td></tr><tr><td>5. Documentation</td><td>10. Test Cases</td></tr></table>

## 1.3. The software reusability viewpoint from NASA RRLs

In order to design highly reusable software, it is necessary to know how the reusability of software can be evaluated. This information will be utilized as a viewpoint when design reusable software.

The NASA Earth Science Data Systems - Software Reuse Working Group has been developed Reuse Readiness Levels (RRLs) since 2008 for use as a measure to evaluate the potential reusability of software. Initially developed for the Earth science domain, but it is applicable to general. The RRLs are being developed to offer capabilities for developers and reusers of software to measure the reusability of software [12].

<!-- PDF_PAGE: 9 -->

<div align="center">

Table 1.3.1. The summary of 9 levels of software reuse according to RRLs [12]:

</div>

<table border="1"><tr><td>Level</td><td>Summary</td></tr><tr><td>RRL1</td><td>Limited reusability; the software is not recommended for reuse.</td></tr><tr><td>RRL2</td><td>Initial reusability; software reuse is not practical</td></tr><tr><td>RRL3</td><td>Basic reusability; the software might be reusable by skilled users at substantial effort, cost, and risk.</td></tr><tr><td>RRL4</td><td>Reuse is possible; the software might be reused by most users with some effort, cost, and risk.</td></tr><tr><td>RRL5</td><td>Reuse is practical; the software could be reused by most users with reasonable cost and risk.</td></tr><tr><td>RRL6</td><td>Software is reusable; the software can be reused by most users although there may be some cost and risk.</td></tr><tr><td>RRL7</td><td>Software is highly reusable; the software can be reused by most users with minimum cost and risk.</td></tr><tr><td>RRL8</td><td>Demonstrated local reusability; the software has been reused by multiple users.</td></tr><tr><td>RRL9</td><td>Demonstrated extensive reusability; the software is being reused by many classes of users over a wide range of systems.</td></tr></table>

Using NASA RRLs to measure software reusability has many advantages. RRLs can be used by different types of stakeholders in different situations. Software can be evaluated either by using the RRLs in a simple manner by the summary RRLs or more extensively by each of the nine topic areas to get a precise assessment. The project managers have a single number by the summary RRLs that is quick and easy to understand. Software developers have a simple way to quickly estimate the readiness of software assets to be reused. Although an estimation of reuse readiness will not reduce the tasks of testing candidate reusable assets, it will enable software developers to more easily determine how ready the software is for their purposes. The software developers also can have more detailed information by the RRL topic area levels [12]. Software providers need to evaluate whether their software can be used by others, whether the software is ready for reuse, and which parts need to be enhanced for use by others. Software reusers need to check whether to consider reusing a software asset, compare software assets available for reuse, assess strengths and weaknesses of such software, and recognize where additional development is necessary for reuse [13].

<!-- PDF_PAGE: 10 -->

In NASA RRLs, there are 9 topic areas to measure software reuse including: Portability, Extensibility, Documentation, Support, Packaging, Intellectual Property Issues, Standards Compliance, Verification and Testing, and Modularity.

Examples of the difference between limited reusable software and highly reusable software when comparing software by each topic area in NASA RRLs are shown in Table 1.3.2 and Table 1.3.3.

<div align="center">

Table I.3.2. Comparison by Documentation, Extensibility and Modularity

</div>

<table border="1"><tr><td></td><td>Documentation</td><td>Extensibility</td><td>Modularity</td></tr><tr><td>Limited reusable software</td><td>Source code is available without documentation.</td><td>Parameters cannot be changed.</td><td>Not designed with modularity</td></tr><tr><td>Highly reusable software</td><td>Documentation on design, customization, testing, use, and reuse is available.</td><td>Use configuration files.The extensibility capability for the software is well defined.</td><td>Organize software components into libraries</td></tr></table>

<div align="center">

Table 1.3.3. Comparison by Portability, Standards Compliance and Verification and Testing

</div>

<table border="1"><tr><td></td><td>Portability</td><td>Standards Compliance</td><td>Verification and Testing</td></tr><tr><td>Limited reusable software</td><td>The software is not portable.</td><td>No standards compliance.</td><td>No testing performed</td></tr><tr><td>Highly reusable software</td><td>The software can be ported to all systems.</td><td>The software and software development process comply with internationally recognized standards.</td><td>Software application tested and validated in a relevant context</td></tr></table>

In this research, after analyzing these topic areas in NASA RRLs, the modularity and extensibility are focused in this research because they are very important for attitude determination software.

Modularity is a software design technique that increases the extent to which software is composed from separate components, called modules. Conceptually, modules represent a separation of and encapsulation of concern, purpose, and function [12]. To achieve modularity

<!-- PDF_PAGE: 11 -->

of level 7 in NASA RRLs, in software, modules should be created for all specified functions and organized into libraries with consistent features within interfaces.

Extensibility is an important dimension to be able to incorporate an asset and add to or modify its functionality [12]. To achieve extensibility of level 6 in NASA RRLs, software should be designed to allow extensibility across a moderate to broad range of application contexts, provides many points of extensibility.

## 1.4. The benefits of applying MBSE and SysML to design software for complex systems

Traditionally, large projects have employed a document-based system engineering approach. However, the document-based approach has some critical limitations. The completeness, consistency, and relationships between requirements, design, engineering analysis, and test information are hard to assess because this information is spread across several documents. To understand a particular aspect of the system and to perform the necessary traceability and change impact assessments are also difficult and leads to poor synchronization between system-level requirements and lower-level hardware and software design. As a result, to reuse the system requirements and design information for the design of the new systems is limited [14].

Compare with document-based system engineering, model-based systems engineering (MBSE) is proved as a more effective approach to manage complexity, improve design quality and communication between developers. MBSE applies systems modeling as part of the system engineering process to support analysis, specification, design, and verification of the developed system [14].

Systems Modeling Language (SysML) is a standardized language to enable MBSE. SysML is an extension of the Unified Modeling Language (UML) version 2, which has become the standard software modeling language. SysML supports the specification, design, analysis, and verification of systems which may include not only software but also data, hardware, etc.

SysML is a graphical modeling language for representing requirements, behaviors, structure, and properties of the system and its components [14]. SysML has capability to model complex systems from a broad range of domain such as satellites. By using SysML, the design of attitude determination software is consistent with the other sub-systems of satellite. Therefore, SysML is more suitable to design software components of satellite than UML.

The type of diagrams of SysML is showed in Figure I.4.1 [14]. The requirement diagram and parametric diagram are the new diagrams compare to UML. One benefit of SysML is allowing traceability between requirements and design model.

<!-- PDF_PAGE: 12 -->


![figure_001.png](figure_001.png)



<div align="center">

Figure I.4.1. SysML diagram taxonomy

</div>

## 1.5. Research objective and approach

The objective of this research is to design highly modular and extensible attitude determination software which can be reused for a variety of micro/nano satellite projects to save time and cost of satellite development.

The context of software reuse here is mainly for the software design and source code reuse. The software will be designed and implemented in C code files, so that the other programmers can utilize reusable parts in their projects. They only need to modify the changing parts for each micro/nano satellite projects. By doing so, they can save time and cost in developing attitude determination software for their satellites.

The approach of this research is to design the reusable attitude determination software by using SysML with the focus on modularity and extensibility from the viewpoint of NASA RRLs.

The modularity in my research is the degree of decomposition of the attitude determination software. There are three steps of decomposition in my research.

In the first step, based on functional analysis, the attitude determination software is decomposed into software modules such as sensor processing, reference vectors estimation, attitude estimation. The sensor processing module is to process the data outputs of sensors. The reference vectors estimation module is to calculate the reference vectors in Earth-Centered Inertial (ECI) frame. The attitude estimation module contains the algorithms for attitude estimation which will be which can be selected based on different accuracy requirements and hardware constraints of each micro/nano satellites projects.

In the second step, each software module is decomposed into components. For example, the sensor processing module is decomposed into the components correspond to each types of sensors.

<!-- PDF_PAGE: 13 -->

In the third step of decomposition, each component is decomposed into basic functions and the standard interfaces are defined between basic functions. For example, the software component “Gyro Processing” is decomposed into two basic functions including “Get Angular Rates in Gyro Frame” and “Calculate Angular Rates in Satellite Body Frame”.

The modularity is also to support the extensibility. In my research, the extensibility is the ability to change the sensors model and performance of onboard computer of satellite projects. For example, there are 6 Sun sensors, 1 Star tracker in Micro Dragon satellite project; however, there is no Star tracker in Nano satellite project, and the performance of onboard computer of Nano satellite is lower.

To achieve the extensibility in my research, there are two steps. Firstly, mission and sensor dependent parameters are separated by data store which can be easily modified when reuse. Secondly, for each satellite project, the attitude estimation algorithms are selected based on the time constraint of calculation.

1.6. Structure of the Thesis

In this research, chapter 1 discusses about the problem background, the objective and approach of the research. The research problem is how to design the reusable attitude determination software to apply for variety of micro/nano satellite projects to save time and cost of satellite development. The approach of this research is to design by using SysML and selecting viewpoint of modularity and extensibility from NASA RRLs base on analyzing the difference between micro and nano satellites projects in term of mission and hardware.

Chapter 2 overviews about the attitude determination and control system of satellite including the attitude determination system and the constraints of design reusable attitude determination software for micro/nano satellites. The attitude determination system is one of the system of the attitude determination and control system. Therefore, the design of the reusable attitude determination software for attitude determination system need to consider the attitude determination and control system of satellites in general as well as the design constraints of the reusable attitude determination software.

Chapter 3 shows the detail design of reusable attitude determination software for micro/nano satellites by using SysML including the design of each software modules and components. The modularity and extensibility also are explained in this chapter.

Chapter 4 shows the verification and validation of this research. The verification is done by both SysML models and calculation the ratio of software reuse. The validation is done by analyzing the situation of reuse attitude determination software between Micro

<!-- PDF_PAGE: 14 -->

Dragon and Nano satellite projects. An interview to check whether the purpose of saving time and cost by using this design is also established.

Chapter 5 is the conclusion to summarize the results of this research and discussions about the future works including the necessary of applying SysML for designing satellites.

<!-- PDF_PAGE: 15 -->

II. Overview of attitude determination system and constraints of design reusable attitude determination software

## 11.1. Overview of attitude determination and control system of satellite

The main satellite subsystems are attitude determination and control system (ADCS), communication, thermal control, power, and command & data handling.

ADCS is one of the most important subsystems of satellite because it helps satellite achieve its mission such as pointing camera to take picture, solar panel direct to the Sun for battery charging.

The ADCS has three subsystems: attitude determination system (ADS), attitude control system (ACS) and attitude guidance. The function of ADS is to determine the current attitude and position of the satellite. The current attitude will be the input of the ACS. The ACS will compare the current attitude and the desired attitude to calculate the required torque for actuators.


![figure_002.png](figure_002.png)



<div align="center">

Figure II.1.1. The block diagram of ADCS

</div>

In terms of the hardware, the ADCS consists of sensors, onboard computer and actuators. For the ADS, the hardware only consists of sensors and onboard computer. The usual sensors used for ADS including Sun sensors, magnetometer, gyro, star tracker and GPS receiver.

<!-- PDF_PAGE: 16 -->


![figure_003.png](figure_003.png)



<div align="center">

Figure II.1.2. The hardware diagram of ADCS

</div>

ADCS software was usually developed for each individual satellite project. The ADCS software including ADS software will be embedded software which runs on the onboard computer.


![figure_004.png](figure_004.png)



<div align="center">

Figure II.1.3. The development of ADCS software between satellite projects

</div>

<!-- PDF_PAGE: 17 -->

## 11.2. The modes of attitude determination

Each satellite has the own modes for attitude determination and control system. The name of each mode can be different from satellites. However, the purpose of each mode should be the similar. For each mode, the attitude determination should be defined in order to consider about the reuse of attitude determination software between satellites.

The modes of attitude determination and control of satellite and the explanation of the output of attitude determination for each mode are following:


![figure_005.png](figure_005.png)



<div align="center">

Figure II.2.1. The modes of attitude determination and control of satellite

</div>

## 1. Recovery mode

This mode begins right after the satellite is separated from rocket. At this moment, almost all satellite's components are turn off except the communication system to save energy for survival of satellite. This is also the first time satellite communicates with ground station by sending the telemetries and receiving the commands.

At this mode, there is no attitude determination because all the satellite's sensors and actuators are turn off.

## 2. Detumbling mode

<!-- PDF_PAGE: 18 -->

This is the second mode of satellite operation following the recovery mode. At this mode, the satellite is rotating very fast. Therefore, the purpose of this mode is to make the satellite rotate slowly.

At this mode, only the magnetometer is turn on. This sensor measure the B-Field vectors on satellite body frame.

## 3. Safe mode (Sun pointing mode)

This is the first time the satellite gets energy from the Sun. There are two kinds of Sun pointing mode including:

+ Spin Sun pointing: the satellite does not need to turn on the reaction wheels, only need to turn on the magnetometer and the Sun sensors.

+ 3axis Sun pointing: the satellite need to turn on the reaction wheels, the control algorithm is PD. Therefore, the attitude should be the quaternion output from the attitude determination function.

In order to save battery of the satellite, in this research, the Sun pointing mode should be Spin Sun pointing, therefore only the magnetometer and Sun sensors are turn on.


![figure_006.png](figure_006.png)



<div align="center">

Figure II.2.2. Attitude determination at Sun Pointing mode

</div>

## 4. Standby mode (Idle mode)

The purpose of this mode is to save energy. The satellite faces to the Sun or to the Earth depend on the design.

<!-- PDF_PAGE: 19 -->


![figure_007.png](figure_007.png)



<div align="center">

Figure II.2.3. Attitude determination at Standby mode

</div>

## 5. Mission mode

At this mode, depend on the mission of each satellite projects, satellite controls its camera to take images of the Earth by nadir pointing or target pointing; or moving its antenna for communication with other satellites. At this mode, almost all sensors are turn on and the attitude determination is similar to the Standby mode. However, the star tracker is used in case of high accuracy pointing.

The considering of the attitude determination for each mode is the application of the modular design in this research. The attitude determination algorithms should be designed for each mode of satellite depend on the constraint of satellite's power consumption, the accuracy requirements and the availability of the sensors. In brief, the outputs of attitude determination function for each mode are defined in the table II.1.

<div align="center">

Table II.2.1. The output of attitude determination function of each mode

</div>

<table border="1"><tr><td rowspan="2">Modes</td><td colspan="5"> Sensors</td><td rowspan="2">Output of Attitude Determination</td></tr><tr><td>Sun Sensor</td><td>Magnetometer</td><td>Gyro</td><td>Star Sensor</td><td>GPS Receiver</td></tr><tr><td>Recovery</td><td>OFF</td><td>OFF</td><td>OFF</td><td>OFF</td><td>OFF</td><td>No Attitude Determination</td></tr><tr><td>Detumbling</td><td>OFF</td><td>ON</td><td>OFF</td><td>OFF</td><td>OFF</td><td>B-Field Vector in Satellite&#x27;s BODY Frame from Magnetometer</td></tr><tr><td>Sun Pointing(Safe Mode)</td><td>ON</td><td>ON</td><td>OFF</td><td>OFF</td><td>OFF</td><td>Sun Vector in Satellite&#x27;s BODY Frame</td></tr><tr><td>Standby</td><td>ON</td><td>ON</td><td>ON</td><td>OFF</td><td>ON</td><td>Quaternion</td></tr><tr><td>Mission</td><td>ON</td><td>ON</td><td>ON</td><td>ON/OFF</td><td>ON</td><td>Quaternion</td></tr></table>

<!-- PDF_PAGE: 20 -->

11. 3.The constraints of design reusable attitude determination software for micro/nano satellites

## II.3.1.The constraints of onboard computers

The constraints of onboard computers including calculation performance, size of memory storage and development environment.

<div align="center">

Table II.3.1. The constraints of onboard computers

</div>

<table border="1"><tr><td>Onboard computers</td><td>Constraints</td></tr><tr><td>Calculation Performance</td><td>Processing speed should be feasible for reuse attitude determination algorithms</td></tr><tr><td>Size of memory storage</td><td>Memory for working area of reusable functions and models should be enough</td></tr><tr><td>Development Environment</td><td>The difference in programming language</td></tr></table>

## 11.3.2.The constraints of sensors

The constraints of sensors are showed in the Table II.3.2.

<div align="center">

Table II.3.2. The constraints of sensors

</div>

<table border="1"><tr><td>Sensors</td><td>Power Consumption</td><td>Update Rate</td><td>Availability</td><td>Accuracy</td><td>Formats of outputs</td></tr><tr><td>Sun Sensor</td><td>Low</td><td>Always</td><td>Only in sunshine time</td><td>Low(~1deg)</td><td>Depend on driver</td></tr><tr><td>Magnetometer</td><td>Low</td><td>Always</td><td>Continuous</td><td>Low(2-5deg)</td><td>Depend on driver</td></tr><tr><td>Gyro</td><td>Mid/High</td><td>~20Hz</td><td>Continuous</td><td>Accumulative Error</td><td>Depend on driver</td></tr><tr><td>Star Tracker</td><td>High</td><td>~1Hz</td><td>Depend on image of stars</td><td>High</td><td>Depend on driver</td></tr><tr><td>GPS Receiver</td><td>Low</td><td>~1Hz</td><td>Continuous</td><td>Mid/Low</td><td>Depend on driver</td></tr></table>

## 11.3.3.The constraints of satellite mission

Satellite missions will effect to design constraints including the determination accuracy requirements, the sensor models for attitude determination and the mounting locations of sensors.

<!-- PDF_PAGE: 21 -->

III. Design of reusable attitude determination software for micro/nano satellites using SysML

## III.1. Software architecture

In this design the Satellite Domain is developed to show the relationship between satellite and the external environment.


![figure_008.png](figure_008.png)



<div align="center">

Figure III.1.1. The block definition diagram of "Satellite Domain"

</div>

The activity of control orientation of satellite for pointing to the target is showed in Figure III.1.2.


![figure_009.png](figure_009.png)



<div align="center">

Figure III.1.2. The activity diagram of "Control Satellite"

</div>

<!-- PDF_PAGE: 22 -->

As described in the Chapter 2, the structure of Attitude Determination and Control System is showed in Figure III.1.3.


![figure_010.png](figure_010.png)



<div align="center">

Figure III.1.3. The structure of Attitude Determination and Control System

</div>

The main function of Attitude Determination System is to estimate the current attitude of the satellite from measuring the state of satellite body rotation and processing the positional and directional information provided from external objects.

After estimated, the current attitude of satellite and the desired attitude will become the inputs for the Attitude Control System to calculate the control torque.

The activity diagram "Attitude Determination and Control" is showed in Figure III.1.4.


![figure_011.png](figure_011.png)



<div align="center">

Figure III.1.4. The activity diagram of "Attitude Determination and Control"

</div>

<!-- PDF_PAGE: 23 -->

The Attitude Determination System consists of the Attitude Determination Software and the Attitude Determination Hardware. The Attitude Determination Hardware consist of the Onboard Computer and Sensors including Gyro, Star Tracker, GPS Receiver, Magnetometer and Sun Sensor as mentioned in Chapter 2.

The block definition diagram of "Attitude Determination System"


![figure_012.png](figure_012.png)



<div align="center">

Figure III.1.5. The block definition diagram of "Attitude Determination System"

</div>

The functions of attitude determination software are analyzed from the use case diagram. The main use case of Attitude Determination Software is "Determine Attitude of Satellite" in which the actor "Attitude Determination Software" interacts with the other actors including "External Objects", "Satellite Dynamics" and "Models in Reference Frame" to determine the current attitude of the satellite.


![figure_013.png](figure_013.png)



<div align="center">

Figure III.1.6. The main use case of Attitude Determination Software

</div>

<!-- PDF_PAGE: 24 -->

The External Objects including the GPS, the Earth's Magnetic Field, the Sun and the Stars provide the positional and directional information to the satellite.

The sequence diagram of the use case "Determine Attitude of Satellite"


![figure_014.png](figure_014.png)



<div align="center">

Figure III.1.7. The sequence diagram of the use case "Determine Attitude of Satellite" The sequence diagram of "Get Positional and Directional Information of Satellite"

</div>


![figure_015.png](figure_015.png)



<div align="center">

Figure III.1.8. The sequence diagram of "Get Positional and Directional Information of Satellite"

</div>

<!-- PDF_PAGE: 25 -->

The sequence diagram of "Estimate Reference Vectors from Models"


![figure_016.png](figure_016.png)



<div align="center">

Figure III.1.9. The sequence diagram of "Estimate Reference Vectors from Models"

</div>

The sequence diagram of "Measure Satellite Body Rotating"


![figure_017.png](figure_017.png)



<div align="center">

Figure III.1.10. The sequence diagram of "Measure Satellite Body Rotating"

</div>

After analyzing the functions of the attitude determination software, the software modules are developed.

<!-- PDF_PAGE: 26 -->

The block definition diagram of "Attitude Determination Software"


![figure_018.png](figure_018.png)



<div align="center">

Figure III.1.11. The block definition diagram of "Attitude Determination Software"

</div>

The internal block diagram of "Attitude Determination Software"


![figure_019.png](figure_019.png)



<div align="center">

Figure III.1.12. The internal block diagram of "Attitude Determination Software"

</div>

<!-- PDF_PAGE: 27 -->


![figure_020.png](figure_020.png)



<div align="center">

Figure III.1.13. The activity diagram of "Estimate Current Attitude"

</div>

<!-- PDF_PAGE: 28 -->

## The requirement diagram of "Attitude Determination Software"


![figure_021.png](figure_021.png)



<div align="center">

Figure III.1.14. The requirement diagram of "Attitude Determination Software"

</div>

<!-- PDF_PAGE: 29 -->

## III.2. Design of software modules

In this section, the design of "Sensors Processing Module", "Reference Vectors Estimation Module" and "Attitude Estimation Module" are showed.

For each software module, the diagrams including the block definition diagram, the activity diagram and the internal block diagram are described.

The "Sensors Processing Module" consists of the software components to process the data outputs of each type of sensors including "Gyro Processing", "Star Tracker Processing", "GPS Receiver Processing", "Magnetometer Processing" and "Sun Sensor Processing".

The "Reference Vectors Estimation Module" contains the software components including "Time Conversion", "Reference Sun Vector in ECI Estimation" and "Reference Magnetic Vector in ECI Estimation".

The "Attitude Estimation Module" has three software components including "Attitude Estimation by TRIAD", "Attitude Estimation by TRIAD and Gyro" and "Attitude Estimation by Star Tracker and Gyro".

For each software component, the consistency between sequence, activity and internal block diagrams are checked by analyzing the diagrams.

<!-- PDF_PAGE: 30 -->

The block definition diagram of "Sensors Processing Module"


![figure_022.png](figure_022.png)



<div align="center">

Figure III.2.1. The block definition diagram of "Sensors Processing Module"

</div>

<!-- PDF_PAGE: 31 -->

The activity diagram of "Sensors Processing Module"


![figure_023.png](figure_023.png)



<div align="center">

Figure III.2.2. The activity diagram of "Sensors Processing Module"

</div>

<!-- PDF_PAGE: 32 -->

## The internal block diagram of "Sensors Processing Module"


![figure_024.png](figure_024.png)



<div align="center">

Figure III.2.3. The internal block diagram of "Sensors Processing Module"

</div>

The block definition diagram of "Reference Vectors Estimation Module"


![figure_025.png](figure_025.png)



<div align="center">

Figure III.2.4. The block definition diagram of "Reference Vectors Estimation Module"

</div>

<!-- PDF_PAGE: 33 -->

The activity diagram of "Reference Vectors Estimation Module"


![figure_026.png](figure_026.png)



<div align="center">

Figure III.2.5. The activity diagram of "Reference Vectors Estimation Module"

</div>

<!-- PDF_PAGE: 34 -->

The internal block diagram of "Reference Vectors Estimation Module"


![figure_027.png](figure_027.png)



<div align="center">

Figure III.2.6. The internal block diagram of "Reference Vectors Estimation Module"

</div>

The implementation in C code for the software component "Time Conversion" and "Reference Sun Vector in ECI Estimation" are showed in the Appendix.

The block definition diagram of "Attitude Estimation Module"


![figure_028.png](figure_028.png)



<div align="center">

Figure III.2.7. The block definition diagram of "Attitude Estimation Module"

</div>

<!-- PDF_PAGE: 35 -->

The activity diagram of "Attitude Estimation Module"


![figure_029.png](figure_029.png)



<div align="center">

Figure III.2.8. The activity diagram of "Attitude Estimation Module"

</div>

<!-- PDF_PAGE: 36 -->

<div align="center">

The internal block diagram of "Attitude Estimation Module"

</div>


![figure_030.png](figure_030.png)



<div align="center">

Figure III.2.9. The internal block diagram of "Attitude Estimation Module"

</div>

The implementation in C code for the software component "Attitude Estimation by TRIAD" is showed in the Appendix.

<!-- PDF_PAGE: 37 -->

The sequence diagram of "Estimate Current Attitude of Satellite"


![figure_031.png](figure_031.png)



<div align="center">

Figure III.2.10. The sequence diagram of "Estimate Current Attitude of Satellite"

</div>

<!-- PDF_PAGE: 38 -->

## III.3. Design of software components of sensors processing module III.3.1. GPS Receiver Processing

The sequence diagrams of "GPS Receiver Processing" software component


![figure_032.png](figure_032.png)



<div align="center">

Figure III.3.1.1. The sequence diagram "Get Current Latitude, Longitude and Time of Satellite"

</div>


![figure_033.png](figure_033.png)



<div align="center">

Figure III.3.1.2. The sequence diagram "GPS Receiver Measure"

</div>

<!-- PDF_PAGE: 39 -->

The activity diagram of "GPS Receiver Processing"


![figure_034.png](figure_034.png)



<div align="center">

Figure III.3.1.3. The activity diagram of "GPS Receiver Processing"

</div>

<!-- PDF_PAGE: 40 -->

## III.3.2. Gyro Processing

The sequence diagrams of "Gyro Processing"


![figure_035.png](figure_035.png)



<div align="center">

Figure III.3.2.1. The sequence diagram "Calculate Angular Rates in Satellite Body Frame"

</div>


![figure_036.png](figure_036.png)



<div align="center">

Figure III.3.2.2. The sequence diagram "Get Angular Rates in Gyro Frame"

</div>

<!-- PDF_PAGE: 41 -->


![figure_037.png](figure_037.png)



<div align="center">

Figure III.3.2.3. The sequence diagram "Gyro Measure"

</div>

<!-- PDF_PAGE: 42 -->

The activity diagram of "Gyro Processing"


![figure_038.png](figure_038.png)



<div align="center">

Figure III.3.2.4. The activity diagram of "Gyro Processing"

</div>

<!-- PDF_PAGE: 43 -->

The internal block diagram of "Gyro Processing"


![figure_039.png](figure_039.png)



<div align="center">

Figure III.3.2.5. The internal block diagram "Gyro Processing"

</div>

<!-- PDF_PAGE: 44 -->

## III.3.3. Magnetometer Processing

The sequence diagrams of "Magnetometer Processing"


![figure_040.png](figure_040.png)



<div align="center">

Figure III.3.3.1. The sequence diagram "Calculate Magnetic Vector in Satellite Body Frame"

</div>


![figure_041.png](figure_041.png)



<div align="center">

Figure III.3.3.2. The sequence diagram "Get Magnetic Vector in Sensor Frame"

</div>

<!-- PDF_PAGE: 45 -->


![figure_042.png](figure_042.png)



<div align="center">

Figure III.3.3.3. The sequence diagram "Magnetometer Measure"

</div>

<!-- PDF_PAGE: 46 -->

The activity diagram of "Magnetometer Processing"


![figure_043.png](figure_043.png)



<div align="center">

Figure III.3.3.4. The activity diagram of "Magnetometer Processing"

</div>

<!-- PDF_PAGE: 47 -->

The internal block diagram of "Magnetometer Processing"


![figure_044.png](figure_044.png)



<div align="center">

Figure III.3.3.5. The internal block diagram of "Magnetometer Processing"

</div>

<!-- PDF_PAGE: 48 -->

## III.3.4. Star Tracker Processing

The sequence diagrams of "Star Tracker Processing"


![figure_045.png](figure_045.png)



<div align="center">

Figure III.3.4.1. The sequence diagram "Calculate Quaternion Vector in Satellite Body Frame"

</div>


![figure_046.png](figure_046.png)



<div align="center">

Figure III.3.4.2. The sequence diagram "Get Quaternion Vector in Sensor Frame"

</div>

<!-- PDF_PAGE: 49 -->


![figure_047.png](figure_047.png)



<div align="center">

Figure III.3.4.3. The sequence diagram "Star Tracker Measure"

</div>

<!-- PDF_PAGE: 50 -->

The activity of "Star Tracker Processing"


![figure_048.png](figure_048.png)



<div align="center">

Figure III.3.4.4. The activity of "Star Tracker Processing"

</div>

<!-- PDF_PAGE: 51 -->

The internal block diagram of "Star Tracker Processing"


![figure_049.png](figure_049.png)



<div align="center">

Figure III.3.4.5. The internal block diagram of "Star Tracker Processing"

</div>

<!-- PDF_PAGE: 52 -->

## III.3.5. Sun Sensor Processing

The sequence diagrams of "Sun Sensor Processing"


![figure_050.png](figure_050.png)



<div align="center">

Figure III.3.5.1. The sequence diagram "Calculate Sun Vector in Satellite Body Frame"

</div>


![figure_051.png](figure_051.png)



<div align="center">

Figure III.3.5.2. The sequence diagram "Get Sun Vector in Sensor Frame"

</div>

<!-- PDF_PAGE: 53 -->


![figure_052.png](figure_052.png)



<div align="center">

Figure III.3.5.3. The sequence diagram "Sun Sensor Measure"

</div>

<!-- PDF_PAGE: 54 -->

The activity diagram of "Sun Sensor Processing"


![figure_053.png](figure_053.png)



<div align="center">

Figure III.3.5.4. The activity diagram of "Sun Sensor Processing"

</div>

<!-- PDF_PAGE: 55 -->

The internal block diagram of "Sun Sensor Processing"


![figure_054.png](figure_054.png)



<div align="center">

Figure III.3.5.5. The internal block diagram of "Sun Sensor Processing"

</div>

<!-- PDF_PAGE: 56 -->

## II.4. Design of software components of reference vectors estimation module II.4.1. Reference Magnetic Vector in ECI Estimation

The sequence diagram of "Calculate Magnetic Vector in ECI from Earth Magnetic Model"


![figure_055.png](figure_055.png)



<div align="center">

Figure III.4.1.1. The sequence diagram of "Calculate Magnetic Vector in ECI from Earth Magnetic Model"

</div>

## III.4.2. Reference Sun Vector in ECI Estimation

The sequence diagram of "Calculate Sun Vector in ECI from Sun Model"


![figure_056.png](figure_056.png)



<div align="center">

Figure III.4.2.1. The sequence diagram of "Calculate Sun Vector in ECI from Sun Model"

</div>

<!-- PDF_PAGE: 57 -->

## III.4.3. Time Conversion

The sequence diagram of "Convert Current Time to Standard Time"


![figure_057.png](figure_057.png)



<div align="center">

Figure III.4.3.1. The sequence diagram of "Convert Current Time to Standard Time"

</div>

<!-- PDF_PAGE: 58 -->

<div align="center">

II.5. Design of software components of attitude estimation module The sequence diagram of "Attitude Estimation by TRIAD"

</div>


![figure_058.png](figure_058.png)



<div align="center">

Figure III.5.1. The sequence diagram of "Attitude Estimation by TRIAD"

</div>

<!-- PDF_PAGE: 59 -->

## The sequence diagram of "Kalman Filter by TRIAD and Gyro"


![figure_059.png](figure_059.png)



<div align="center">

Figure III.5.2. The sequence diagram of "Kalman Filter by TRIAD and Gyro"

</div>

The sequence diagram of "Kalman Filter by Star Tracker and Gyro"


![figure_060.png](figure_060.png)



<div align="center">

Figure III.5.3. The sequence diagram of "Kalman Filter by Star Tracker and Gyro"

</div>

<!-- PDF_PAGE: 60 -->

## III.6. The modularity and extensibility in design

The modularity is the decomposition of the attitude determination software. The extensibility is the ability to change the sensors and performance of on-board computer of micro/nano satellites projects. For example, there are 6 Sun sensors, 1 Star tracker in Micro Dragon satellite project; however, there is no Star tracker in Nano satellite project, and the performance of onboard computer of Nano satellite is lower. The modularity and extensibility has a close relationship with each other. The modularity is also to support extensibility. There are 3 levels of modularity and extensibility.

At level 1, based on functional analysis, the attitude determination software is decomposed into software modules including sensors processing module, reference vectors estimation module, attitude estimation module and attitude representation conversion module. The sensor processing module is to process the data outputs of sensors. The reference vectors estimation module is to calculate the reference vectors in Earth-Centered Inertial (ECI) frame. The attitude estimation module contains the algorithms for attitude estimation which will be which can be selected based on different accuracy requirements and hardware constraints of each micro/nano satellites projects. The attitude representation conversion module is to convert between the representations of attitude.

Mission dependent parameters such as mounting location of sensors and update rate of sensors are separated in isolated database which can be easily modified when reuse. This decomposition shows the extensibility in design. If the satellite projects are different on the sensor mounting location (on the surface of the satellites) or the updated rates of sensors, only this database need to be modified, the other software modules do not need to be modified.


![figure_061.png](figure_061.png)



<div align="center">

Figure III.6.1. The decomposition of attitude determination software into software modules

</div>

<!-- PDF_PAGE: 61 -->

At level 2, each software module is decomposed into software components. For example, Figure III.6.2 shows the decomposition of attitude estimation module into software components based on types of sensors. By this decomposition, the attitude estimation components are selected based on sensors when reuse. This decomposition shows the extensibility because the satellites projects are different on used sensors. The nano satellites do not have Star tracker, therefore, without this decomposition, the attitude estimation module cannot be reuse for nano satellites. By this decomposition, the nano satellites can select two software components including attitude estimation by TRIAD and attitude estimation by TRIAD and Gyro when reuse.


![figure_062.png](figure_062.png)



<div align="center">

Figure III.6.2. The decomposition of attitude estimation module into software components

</div>

Another example is the decomposition of reference vectors estimation module into software components in Figure III.6.3.


![figure_063.png](figure_063.png)



<div align="center">

Figure III.6.3. The decomposition of reference vectors estimation module

</div>

By this way of decomposition, the reference magnetic vector estimation component, which requires a lot of calculation, can be replaced when reuse based on performance of on-

<!-- PDF_PAGE: 62 -->

board computer. For example, with nano satellites, the on-board computers are limited on power of processing, therefore, the simpler version of the reference magnetic vector estimation will be chosen.

Finally, at level 3, each software component is decomposed into basic software components. The basic software components are not decomposed any more in design. Figure III.6.4. is the decomposition of sun sensor processing component into basic software components.


![figure_064.png](figure_064.png)



<div align="center">

Figure III.6.4. The decomposition of sun sensor processing component

</div>

By this way of decomposition, input and output interfaces of basic software components are analyzed when reuse and this shows the extensibility of design. For example, the Sun sensor outputs can be different if the Sun sensor is changed, therefore, the "Sun Vector in Sensor Frame Acquisition" need to be modified when reuse.

<!-- PDF_PAGE: 63 -->

## IV. Verification and Validation

## IV.1. Verification

In this research, to verify the reusability of attitude determination software, the software reuse ratio is defined to measure the percentages of basic software components which can be reused between satellite projects.

Steps to calculate the software reuse ratio for the new satellite project:

1. Calculate number of existing basic software components

2. List all basic software components need to be add for the new satellite (number of added components)

3. List all basic software components need to be change for the new satellite (number of changed components)

4. Calculate the software reuse ratio by the equation below

$$
\begin{array}{l} \mathrm {The s o f t w a r e r e u s e r a t i o} = 1 - \frac {\mathrm {n u m b e r o f a d d e d c o m p o n e n t s} + \mathrm {n u m b e r o f c h a n g e d c o m p o n e n t s}}{\mathrm {n u m b e r o f a d d e d c o m p o n e n t s} + \mathrm {n u m b e r o f e x i s t i n g c o m p o n e n t s}} \\ = \frac {\mathrm {n u m b e r o f u n c h a n g e d c o m p o n e n t s}}{\mathrm {n u m b e r o f a l l c o m p o n e n t s}} \\ \end{array}
$$

Example 1:

$$
\text {The total number of existing components} = 1 0
$$

$$
\text {The number of new components} = 3
$$

$$
\text {The number of change components} = 2
$$

$$
\text {The software reuse ratio} = 1 - (3 + 2) / (1 0 + 3) = 1 - 5 / 1 3 = 8 / 1 3
$$

Example 2:

$$
\text {The total number of existing components} = 1 0
$$

$$
\text {The number of new components} = 3
$$

$$
\text {The number of change components} = 6
$$

$$
\text {The software reuse ratio} = 1 - (3 + 6) / (1 0 + 3) = 1 - 9 / 1 3 = 4 / 1 3
$$

From the draft estimation, at least 60% of basic software components designed in this research can be reused for the new satellite projects without the need of modification.

In this thesis, there are 16 basic software components have been designed in total. All these basic software components can be used for MicroDragon satellite. There are 10/16 basic software components can be used for Nano Satellite (about 60%).

<!-- PDF_PAGE: 64 -->

<div align="center">

Table IV.1.1 All designed software components

</div>

<table border="1"><tr><td colspan="2">Sensors Processing Module</td></tr><tr><td colspan="2">Sun Sensor Processing</td></tr><tr><td>1</td><td>Sun Vector in Sensor Frame Acquisition</td></tr><tr><td>2</td><td>Sun Vector in Satellite Body Frame Calculation</td></tr><tr><td colspan="2">Magnetometer Processing</td></tr><tr><td>3</td><td>Magnetic Vector in Sensor Frame Acquisition</td></tr><tr><td>4</td><td>Magnetic Vector in Satellite Body Frame Calculation</td></tr><tr><td colspan="2">GPS Receiver Processing</td></tr><tr><td>5</td><td>Get Current Latitude, Longitude and Time of Satellite</td></tr><tr><td colspan="2">Gyro Processing</td></tr><tr><td>6</td><td>Angular Rates in Gyro Frame Acquisition</td></tr><tr><td>7</td><td>Angular Rates in Satellite Body Frame Calculation</td></tr><tr><td colspan="2">Star Tracker Processing</td></tr><tr><td>8</td><td>Quaternion Vector in Sensor Frame Acquisition</td></tr><tr><td>9</td><td>Quaternion Vector in Satellite Body Frame Calculation</td></tr><tr><td colspan="2">Reference Vectors Estimation Module</td></tr><tr><td>10</td><td>Time Conversion</td></tr><tr><td>11</td><td>Reference Sun Vector in ECI Estimation</td></tr><tr><td>12</td><td>Reference Magnetic Vector in ECI Estimation</td></tr><tr><td colspan="2">Attitude Estimation Module</td></tr><tr><td>13</td><td>Attitude Estimation by TRIAD</td></tr><tr><td>14</td><td>Attitude Estimation by TRIAD and Gyro</td></tr><tr><td>15</td><td>Attitude Estimation by Star Tracker and Gyro</td></tr><tr><td colspan="2">Attitude Representation Conversion Module</td></tr><tr><td>16</td><td>DCM to Quaternion Conversion</td></tr></table>

The reusability of the designed attitude determination software is also verified by analyzing SysML diagrams by checking the input and output interfaces of software components. There are only input and output interfaces between software components. Therefore, these software components are reusable when the input and output interfaces are the same.

<!-- PDF_PAGE: 65 -->

## IV.2. Validation

In this research, the design of reusable attitude determination software needs to validate whether it can save time and cost of satellite development. By analyzing the situation of reuse attitude determination software from MicroDragon project (the current satellite project of Vietnamese students) to next satellite project which is the nano satellite (based on the assumption from Table 1.1.2) the goal of saving time and cost of satellite development is proved because the reusable software components will not need time to develop and test again.


![figure_065.png](figure_065.png)



<div align="center">

Figure IV.2.1. Attitude determination at Standby mode in Sunshine time for MicroDragon

</div>


![figure_066.png](figure_066.png)



<div align="center">

Figure IV.2.2. Attitude determination at Standby mode in Eclipse time for MicroDragon

</div>

<!-- PDF_PAGE: 66 -->


![figure_067.png](figure_067.png)



<div align="center">

Figure IV.2.3. Attitude determination at Mission mode for MicroDragon

</div>


![figure_068.png](figure_068.png)



<div align="center">

Figure IV.2.4. Attitude determination at Standby mode and Mission mode for Nano Satellite

</div>

<!-- PDF_PAGE: 67 -->

## V. Conclusion

## V.1. Summary

There are three key points in this research. Firstly, the reusable attitude determination software is designed by using SysML which has outstanding benefits compare with other methods. Secondly, based on analyzing the difference between micro and nano satellites projects in term of mission and hardware, the viewpoints of modularity and extensibility from NASA RRLs are selected and implemented in my design. Finally, in this research, the designed software is highly modular and extensible.

The results of this research include the design activities and the design of reusable attitude determination software using SysML. In this research, the software modules are designed based on functional analysis and also to support extensibility. The extensibility is the ability to adapt to the change of sensors model and performance of onboard computer. When comparing with levels in NASA RRLs, the modularity achieves level 7, the extensibility achieves level 6.

In this thesis, the libraries of reusable functions in C code for attitude determination including vector, quaternion and matrix calculations; conversion functions of attitude representations and the implementation of TRIAD algorithm are also developed and listed in the Appendix.

By interviewing experts and analyzing the situation of reuse attitude determination software for MicroDragon and Nano satellite project, the designed software can significantly save time and cost of micro/nano satellites development.

## V.2. Future works

From the interviews to validate this research, there are mix feelings from the interviewees about the utilizing SysML to design software for satellite's systems. Almost experts agree that design by using SysML has many advantages which are critical for design software reuse of onboard software of satellites. However, there are concerns about the popularity of SysML among the satellite developers. Although, SysML is being increasingly used to model complex systems, the necessary as well as the benefits of applying SysML for designing satellites should be more persuaded to the satellite developers.

Besides, the software tool used to design in this research is Cameo Enterprise Architecture 18.1 which is very powerful tool and its capabilities should be more effectively exploited to design.

<!-- PDF_PAGE: 68 -->

## References

[1] D. D. Elizabeth Buchen, "2014 Nano / Microsatellite Market Assessment," SpaceWorks Enterprises, Inc., 2014.

[2] "Small Sat 2014 Conference," [Online]. Available: http://digitalcommons.usu.edu/smallsat/2014/.

[3] E. Buchen, "2015 Small Satellite Market Observations," 2015. [Online]. Available: http://www.spaceworksforecast.com/docs/SpaceWorks_Small_Satellite_Market_Observations _2015.pdf. [Accessed 07 2015].

[4] L. F. L. M. a. M. D. S. E. J., "Kalman Filtering for Spacecraft Attitude Estimation," Journal of Guidance, Control, and Dynamics, vol. 5, no. 5, pp. 417-429, 1982.

[5] C. F. L. M. a. Y. C. J. L., "Survey of Nonlinear Attitude Estimation Methods," AIAA Journal of. Guidance, Control and Dynamics , vol. 30, no. 1, pp. 12-28, 2007.

[6] D. F. E. J. J. P. James R. Wertz, Space Mission Engineering: The New SMAD, Microcosm Press, 2011.

[7] S. Nakasuka, "Micro/Nano-satellites On-board Software Framework Design and Its Implementation in Hodoyoshi Satellites," 2013.

[8] W. a. K. K. Frakes, "Software Reuse Research: Status and Future," IEEE Transactions on Software Engineering, vol. 31, no. 7, pp. 529-536, 2005.

[9] "Software Reuse FAQ," [Online]. Available: https://earthdata.nasa.gov/esdswg/software-reuse-srwg/software-reuse-faq.

[10] "Tools to Support the Reuse of Software Assets for the NASA Earth Science Decadal Survey Missions," [Online]. Available: http://gsfcir.gsfc.nasa.gov/download/authors/18943/Journal%20Articles_18943.

[11] W. a. C. T. Frakes, "Software Reuse: Metrics and Models," ACM Computing Surveys, vol. 28, no. 2, pp. 415-435, 1996.

[12] "Reuse Readiness Levels (RRLs), Version 1.0," [Online]. Available: https://earthdata.nasa.gov/sites/default/files/esdswg/reuse/Resources/rrls/RRLs_v1.0.pdf.

[13] Marshall, J.J.; Downs, R.R., "Reuse Readiness Levels as a Measure of Software Reusability," in Geoscience and Remote Sensing Symposium, IGARSS, IEEE International Conference, 2008.

[14] A. M. R. S. Sanford Friedenthal, A practical guide to SysML: the systems modeling language, Second edition ed., Elsevier Inc, 2012.

<!-- PDF_PAGE: 69 -->

[15] J. S.Poulin, Measuring Software Reuse: Principles, Practices, and Economic Models, Addison Wesley Longman, Inc., 1997.

[16] "NASA Studying the Reuse of Spacecraft Software," [Online]. Available: http://www.space.com/2304-nasa-studying-reuse-spacecraft-software.html.

<!-- PDF_PAGE: 70 -->

Figure I.4.1. SysML diagram taxonomy

Figure II.1.1. The block diagram of ADCS

Figure II.1.2. The hardware diagram of ADCS

Figure II.1.3. The development of ADCS software between satellite projects

Figure II.2.1. The modes of attitude determination and control of satellite

Figure II.2.2. Attitude determination at Sun Pointing mode

Figure II.2.3. Attitude determination at Standby mode

Figure III.1.1. The block definition diagram of “Satellite Domain”

Figure III.1.2. The activity diagram of “Control Satellite”

Figure III.1.3. The structure of Attitude Determination and Control System

Figure III.1.4. The activity diagram of “Attitude Determination and Control”

Figure III.1.5. The block definition diagram of “Attitude Determination System”

Figure III.1.6. The main use case of Attitude Determination Software

Figure III.1.7. The sequence diagram of the use case “Determine Attitude of Satellite”

Figure III.1.8. The sequence diagram of “Get Positional and Directional Information of Satellite”

Figure III.1.9. The sequence diagram of “Estimate Reference Vectors from Models”

Figure III.1.10. The sequence diagram of “Measure Satellite Body Rotating”

Figure III.1.11. The block definition diagram of “Attitude Determination Software”

Figure III.1.12. The internal block diagram of “Attitude Determination Software”

Figure III.1.13. The activity diagram of “Estimate Current Attitude”

Figure III.1.14. The requirement diagram of “Attitude Determination Software”

Figure III.2.1. The block definition diagram of “Sensors Processing Module”

Figure III.2.2. The activity diagram of “Sensors Processing Module”

Figure III.2.3. The internal block diagram of “Sensors Processing Module”

Figure III.2.4. The block definition diagram of “Reference Vectors Estimation Module”

Figure III.2.5. The activity diagram of “Reference Vectors Estimation Module”

Figure III.2.6. The internal block diagram of “Reference Vectors Estimation Module”

Figure III.2.7. The block definition diagram of “Attitude Estimation Module”

Figure III.2.8. The activity diagram of “Attitude Estimation Module”

Figure III.2.9. The internal block diagram of “Attitude Estimation Module”

Figure III.2.10. The sequence diagram of “Estimate Current Attitude of Satellite”

Figure III.3.1.1. The sequence diagram “Get Current Latitude, Longitude and Time of Satellite”

Figure III.3.1.2. The sequence diagram “GPS Receiver Measure”

Figure III.3.1.3. The activity diagram of “GPS Receiver Processing”

Figure III.3.2.1. The sequence diagram “Calculate Angular Rates in Satellite Body Frame”

<!-- PDF_PAGE: 71 -->

Figure III.3.2.2. The sequence diagram “Get Angular Rates in Gyro Frame”

Figure III.3.2.3. The sequence diagram “Gyro Measure”

Figure III.3.2.4. The activity diagram of “Gyro Processing”

Figure III.3.2.5. The internal block diagram “Gyro Processing”

Figure III.3.3.1. The sequence diagram “Calculate Magnetic Vector in Satellite Body Frame”

Figure III.3.3.2. The sequence diagram “Get Magnetic Vector in Sensor Frame”

Figure III.3.3.3. The sequence diagram “Magnetometer Measure”

Figure III.3.3.4. The activity diagram of “Magnetometer Processing”

Figure III.3.3.5. The internal block diagram of “Magnetometer Processing”

Figure III.3.4.1. The sequence diagram “Calculate Quaternion Vector in Satellite Body Frame”

Figure III.3.4.2. The sequence diagram “Get Quaternion Vector in Sensor Frame”

Figure III.3.4.3. The sequence diagram “Star Tracker Measure”

Figure III.3.4.4. The activity of “Star Tracker Processing”

Figure III.3.4.5. The internal block diagram of “Star Tracker Processing”

Figure III.3.5.1. The sequence diagram “Calculate Sun Vector in Satellite Body Frame”

Figure III.3.5.2. The sequence diagram “Get Sun Vector in Sensor Frame”

Figure III.3.5.3. The sequence diagram “Sun Sensor Measure”

Figure III.3.5.4. The activity diagram of “Sun Sensor Processing”

Figure III.3.5.5. The internal block diagram of “Sun Sensor Processing”

Figure III.4.1.1. The sequence diagram of “Calculate Magnetic Vector in ECI from Earth Magnetic Model”

Figure III.4.2.1. The sequence diagram of “Calculate Sun Vector in ECI from Sun Model”

Figure III.4.3.1. The sequence diagram of “Convert Current Time to Standard Time”

Figure III.5.1. The sequence diagram of “Attitude Estimation by TRIAD”

Figure III.5.2. The sequence diagram of “Kalman Filter by TRIAD and Gyro”

Figure III.5.3. The sequence diagram of “Kalman Filter by Star Tracker and Gyro”

Figure III.6.1. The decomposition of attitude determination software into software modules

Figure III.6.2. The decomposition of attitude estimation module into software components

Figure III.6.3. The decomposition of reference vectors estimation module

Figure III.6.4. The decomposition of sun sensor processing component

Figure IV.2.1. Attitude determination at Standby mode in Sunshine time for MicroDragon

Figure IV.2.2. Attitude determination at Standby mode in Eclipse time for MicroDragon

Figure IV.2.3. Attitude determination at Mission mode for MicroDragon

Figure IV.2.4. Attitude determination at Standby mode and Mission mode for Nano Satellite

<!-- PDF_PAGE: 72 -->

## List of Tables

Table I.1.1. Estimating source lines of code for typical satellite functions

Table I.1.2. Example of the different mission requirements and hardware constraints between micro/nano satellites projects

Table I.2.1. Reusable aspects of software projects

Table I.3.1. The summary of 9 levels of software reuse according to RRLs

Table I.3.2. Comparison by Documentation, Extensibility and Modularity

Table I.3.3. Comparison by Portability, Standards Compliance and Verification and Testing

Table II.2.1. The output of attitude determination function of each mode

Table II.3.1. The constraints of onboard computers

Table II.3.2. The constraints of sensors

Table IV.1.1 All designed software components

<!-- PDF_PAGE: 73 -->

Appendices

Appendix1. Listing C source code of reusable functions for att

//Reusable utilities

//1. Mathematical utilities

1. Vector.h

//This file contains basic functions related to vector calculations

//The default dimension of vector is 3

//Verified 05/09/2015

//calc norm of vector

float NormOfVector(float *v)

{

    float norm = sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);

    return norm;

}

//Normalize vector

void NormalizeVector(float *v)

{

    float norm = NormOfVector(v);

    if(norm>0){

        v[0] = v[0]/norm;

        v[1] = v[1]/norm;

        v[2] = v[2]/norm;

    }

}

//calc dot product of 2 vectors a and b.

float DotProductOf2Vector(float *a, float *b)

{

    return (a[0]*b[0] + a[1]*b[1] + a[2]*b[2]);

}

//The Cross Product c = a × b of two vectors a and b

<!-- PDF_PAGE: 74 -->

//Reference: https://www.mathsisfun.com/algebra/vectors-cross-product.html

//a × b = |a| |b| sin(a,b)

void VectorCrossProduct(float *a, float *b, float *c)

{

    c[0] = a[1]*b[2] - a[2]*b[1];

    c[1] = a[2]*b[0] - a[0]*b[2];

    c[2] = a[0]*b[1] - a[1]*b[0];

}

//check if 2 vectors are parallel; 1: parallel 0: not parallel

int CheckParallelVector(float *a, float *b)

{

    float *c;

    VectorCrossProduct(a,b,c);

    //if 2 vectors parallel

    if(NormOfVector(c)==0) return 1;

    //if not parallel

    return 0;

}

//calc angular between 2 vectors a and b

//angle output in radian

float AngleOf2Vector(float *a, float *b)

{

    float c;

    c=DotProductOf2Vector(a,b)/(NormOfVector(a)*NormOfVector(b));

    return acos(c);

}

<!-- PDF_PAGE: 75 -->

2. Quaternion.h

//Version 1.2:

//Date 05/08/2015

//These are the basic functions related to quaternion calculations

//All these functions are reusable

//The users need only call these functions with their parameters

//Reference from:

//http://jp.mathworks.com/help/aeroblks/math-operations.html

//q[0] is scalar

//Normalize quaternion

void NormalizeQuaternion(float *q){

    float norm; //norm of quaternion

    norm = sqrt(q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3]);

    //Normalize quaternion

    if(norm>0)

    {

        q[0] = q[0]/norm;

        q[1] = q[1]/norm;

        q[2] = q[2]/norm;

        q[3] = q[3]/norm;

    }

}

//Properize quaternion

void ProperizeQuaternion(float *q){

    //q0 should always be positive

    if(q[0]<0.0){        //if q0<0 make q0 be positive

        q[0]*=-1.0;

        q[1]*=-1.0;

        q[2]*=-1.0;

        q[3]*=-1.0;

    }

}

<!-- PDF_PAGE: 76 -->

}

}

//Conjugate quaternion

void ConjugateQuaternion(float *q, float *q_conjugated)

{

    q_conjugated[0] = q[0];

    q_conjugated[1] = -q[1];

    q_conjugated[2] = -q[2];

    q_conjugated[3] = -q[3];

}

//Inverse quaternion

void InverseQuaternion(float *q, float *q_inversed){

    //ConjugateQuaternion

    ConjugateQuaternion(q,q_inversed);

    //Normalize quaternion

    NormalizeQuaternion(q_inversed);

}

//Calculate product of two input quaternion

void QuaternionMultiplication(float *q, float *r, float *t)

{

    //output quaternion t = qxr

    t[0] = r[0]*q[0]-r[1]*q[1]-r[2]*q[2]-r[3]*q[3];

    t[1] = r[0]*q[1]+r[1]*q[0]-r[2]*q[3]+r[3]*q[2];

    t[2] = r[0]*q[2]+r[1]*q[3]+r[2]*q[0]-r[3]*q[1];

    t[3] = r[0]*q[3]-r[1]*q[2]+r[2]*q[1]+r[3]*q[0];

}

<!-- PDF_PAGE: 77 -->

3. Matrix.ii

```c

#define MAX 3          //number of matrix row, column

void TransposeMatrix(float A[MAX][MAX], float B[MAX][MAX])

{

    int i,j;

    float C[MAX][MAX];

    for(i=0;i<MAX;i++)

        for(j=0;j<MAX;j++) C[i][j]=A[j][i];

    for(i=0;i<MAX;i++)

        for(j=0;j<MAX;j++) B[i][j]=C[i][j];

}

void MultiMatrix(float A[][MAX], float B[][MAX], float C[][MAX])

{

    int i, j, k;

    for(i = 0; i < MAX; i++)

    {

        for(j = 0; j < MAX; j++)

        {

            C[i][j] = 0.0;

            for(k = 0; k < MAX; k++){

                C[i][j] += A[i][k] * B[k][j];

            }

        }

    }

}

void AddMatrix(float A[MAX][MAX], float B[MAX][MAX], float C[MAX][MAX]){

    int i, j;

    for(i = 0; i < MAX; i++)

        for(j = 0; j < MAX; j++) C[i][j] = A[i][j] + B[i][j];

}

```

<!-- PDF_PAGE: 78 -->

4. TimeConversion.h // Converse universal time to standard time (Julian date)

//Given year, month, day, hour, minute, second, compute the Julian date, JD

float ConverseTime2JulianDate(int year, int month, int day, int hour, int minute, int second)

{

    //reference

    //http://en.wikipedia.org/wiki/Julian_day

    float a, y, m, jdn, jd;

    a=int((14-month)/12);

    y= year + 4800 - a;

    m= month + 12*a -3;

    //starting from a Gregorian calendar date

    jdn = day + int((153*m+2)/5) + 365*y + int(y/4) - int(y/100) + int(y/400) - 32045;

    jd = jdn + (hour-12)/24 + minute/1440 + second/86400;

    return jd;

}

<!-- PDF_PAGE: 79 -->

5. SunVectorCalculation.h

// Calculate reference sun vector in ECI from sun model when input given time (julian date)

//Compute reference sun vector in ECI

//reference from

http://www.acsu.buffalo.edu/~johnc/space_book/sampex_control_chapt7/solar.m

//Verified by compare with matlab results

void ComputeSunUnitVectorInECIFromJD(float jd, float *sun_i)

{

    // Get Julian Date and Centuries

    float d2r = 3.14159265/180; //pi=3.14159265 deg to radian

    float jd_cent=(jd-2451545)/36525;

    // Mean Longtitude and Other Parameters

    float lam=280.460+36000.771*jd_cent;

    float m_sun=357.5277233+35999.050*jd_cent; //mean longitude of Sun

    float lam_ecl=lam+1.914666471*sin(m_sun*d2r)+0.019994643*sin(2*m_sun*d2r);

    float eps=23.439291-0.0130042*jd_cent; //ecliptic longitude of Sun

    //reference sun vector in eci s_eci

    sun_i[0]=cos(lam_ecl*d2r); //cos lamda ecliptic

    sun_i[1]=cos(eps*d2r)*sin(lam_ecl*d2r);

    sun_i[2]=sin(eps*d2r)*sin(lam_ecl*d2r);

<!-- PDF_PAGE: 80 -->

6. File Triad.h

// The Triad algorithm computes DCMbi from s_eci,s_b,m_eci,m_b

//Verified 05/10/2015

//Reference from: http://www.dept.aoe.vt.edu/~cdhall/courses/aoe4140/

void TRIAD(float *v1i, float *v2i, float *v1b, float *v2b, float DCMbi[3][3])

{

    /////v1i, v2i: Sun vector and magnetic field vector in ECI

    //v1b, v2b: Sun vector and magnetic field vector in Body

    float t2i[3], t3i[3], t2b[3], t3b[3];

    float Rbt[3][3], Rti[3][3];

    VectorCrossProduct(v1i,v2i,t2i);

    NormalizeVector(t2i);

    VectorCrossProduct(v1i,t2i,t3i);

    NormalizeVector(t3i);

    VectorCrossProduct(v1b,v2b,t2b);

    NormalizeVector(t2b);

    VectorCrossProduct(v1b,t2b,t3b);

    NormalizeVector(t3b);

    //Construct Rbt

    Rbt[0][0]=v1b[0];    Rbt[0][1]=t2b[0];    Rbt[0][2]=t3b[0];

    Rbt[1][0]=v1b[1];    Rbt[1][1]=t2b[1];    Rbt[1][2]=t3b[1];

    Rbt[2][0]=v1b[2];    Rbt[2][1]=t2b[2];    Rbt[2][2]=t3b[2];

    //Construct Rti

    Rti[0][0]=v1i[0];    Rti[0][1]=t2i[0];    Rti[0][2]=t3i[0];

    Rti[1][0]=v1i[1];    Rti[1][1]=t2i[1];    Rti[1][2]=t3i[1];

    Rti[2][0]=v1i[2];    Rti[2][1]=t2i[2];    Rti[2][2]=t3i[2];

    TransposeMatrix(Rti,Rti);

    MultiMatrix(Rbt,Rti,DCMbi);

}

<!-- PDF_PAGE: 81 -->

7. ConverseAttitudeRepresentation.h

//These are functions which convert between attitude representation

//All these functions are reusable

//Reference from:

//http://jp.mathworks.com/help/aeroblks/axes-transformations.html

//Convert Quaternion to DCM (Direction Cosine Matrix)

//Reference from Prof. Nakasuka Lecturers at Keio University 2013

//DCM=Cb2i transformation from body to inertia

void ConvertQuaternion2DCMbi(float *q, float DCM[][3]){

//calculate elements of DCM matrix

$ \mathrm{DCM}[0][0]=q[0]^{*}q[0]+q[1]^{*}q[1]-q[2]^{*}q[2]-q[3]^{*}q[3] $

$ \mathrm{DCM}[0][1]=2.0^{*}(\mathrm{q}[1]^{*}\mathrm{q}[2]-\mathrm{q}[0]^{*}\mathrm{q}[3]); $

$ \mathrm{DCM}[0][2]=2.0^{*}(\mathrm{q}[1]^{*}\mathrm{q}[3]+\mathrm{q}[0]^{*}\mathrm{q}[2]); $

$ \mathrm{DCM}[1][0]=2.0^{*}(\mathrm{q}[1]^{*}\mathrm{q}[2]+\mathrm{q}[0]^{*}\mathrm{q}[3]); $

$ \mathrm{DCM}[1][1]=q[0]^{*}q[0]-q[1]^{*}q[1]+q[2]^{*}q[2]-q[3]^{*}q[3]; $

$ \mathrm{DCM}[1][2]=2.0^{*}(\mathrm{q}[2]^{*}\mathrm{q}[3]-\mathrm{q}[0]^{*}\mathrm{q}[1]); $

$ \mathrm{DCM}[2][0]=2.0^{*}(\mathrm{q}[1]^{*}\mathrm{q}[3]-\mathrm{q}[0]^{*}\mathrm{q}[2]); $

$ \mathrm{DCM}[2][1]=2.0^{*}(\mathrm{q}[2]^{*}\mathrm{q}[3]+\mathrm{q}[0]^{*}\mathrm{q}[1]); $

$ \mathrm{DCM}[2][2]=q[0]^{*}q[0]-q[1]^{*}q[1]-q[2]^{*}q[2]+\mathrm{q}[3]^{*}q[3]; $

<!-- PDF_PAGE: 82 -->

8. File TestADS.cpp

```cpp

//Verification the correctness of functions

#include <stdio.h>

#include <conio.h>

#include <stdlib.h> /* srand, rand */

#include <time.h> /* time */

#include <math.h>

//Reusable utilities

//1. Mathematical utilities

#include "Vector.h"

#include "Quaternion.h"

#include "Matrix.h"

//2. Converse universal time to standard time (Julian date)

#include "TimeConversion.h"

//3. Calculate reference sun vector in ECI from sun model when input given time (julian date)

#include "SunVectorCalculation.h"

//4. The Triad algorithm computes DCMbi from s_eci,s_b,m_eci,m_b

#include "Triad.h"

//5. Converse attitude representation

#include "ConverseAttitudeRepresentation.h"

//#define NMAX 4 //for test quaternion

void TestQuaternion()

{

    float q1[4];

    float q2[4];

    float q3[4];

    q1[0] =0.9962;

    q1[1] = 0;

    q1[2] = 0;

    q1[3] = 0.0872;

    q2[0] =0.9962;

    q2[1] = 0;

    q2[2] = 0;

    q2[3] = 0.0872;

    //Test Multiplication

    QuaternionMultiplication(q1,q2,q3);

    //Show results, OK

    printf("%5.3f %5.3f %5.3f %5.3f", q3[0], q3[1], q3[2], q3[3]);

    //0.9848 0 0 0.1736

}

```

<!-- PDF_PAGE: 83 -->

```cpp

void TestTimeConversion()

{

    float jd;

    float sun_eci[3];

    //Test case to check the time conversion function

    int year=2015;

    int month=5;

    int day=8;

    int hour=13;

    int minute=24;

    int second=20;

    jd=ConverseTime2JulianDate(year, month, day, hour, minute, second);

    //Result from online conversion

    //http://aa.usno.navy.mil/data/docs/JulianDate.php

    //The Julian date for CE 2015 May 8 13:24:20.0 UT is

    //JD 2457151.058565

    ComputeSunUnitVectorInECIFromJD(jd, sun_eci);

    printf("%f %f %f", sun_eci[0], sun_eci[1], sun_eci[2]);

}

void TestVector()

{

    float norm, a[3], b[3], v[3];

    a[0]=4; a[1]=0; a[2]=7;

    b[0]=-2; b[1]=1; b[2]=3;

    //VectorCrossProduct(a,b,v);

    //NormalizeVector(v);

    //int i=CheckParallelVector(a,b);

    //printf("%d",i);

    float c;

    c=AngleOf2Vector(a,b);

    printf("%.2f",c);

    //printf("%.2f %.2f %.2f",v[0], v[1], v[2]);

}

```

<!-- PDF_PAGE: 84 -->

//Ref: http://www.dept.aoe.vt.edu/~cdhall/courses/aoe4140/

void TestTriad()

{

    /////v1i, v2i: Sun vector and Magnetic field vector in ECI

    //v1b, v2b: Sun vector and Magnetic field vector in Body

    float v1i[3], v2i[3], v1b[3], v2b[3];

    float DCMbi[3][3]; //determined attitude

    //test case from http://www.dept.aoe.vt.edu/~cdhall/courses/aoe4140

    v1i[0]=-0.1517; v1i[1]=-0.9669; v1i[2]=0.2050;

    v2i[0]=-0.8393; v2i[1]= 0.4494; v2i[2]=-0.3044;

    v1b[0]=0.8273; v1b[1]=0.5541; v1b[2]=-0.0920;

    v2b[0]=-0.8285; v2b[1]=0.5522; v2b[2]=-0.0955;

    TRIAD(v1i,v2i,v1b,v2b,DCMbi);

    printf("Test Triad Algorithm:\n");

    int i,j;

    for(i=0;i<3;i++)

    {

        for(j=0;j<3;j++) printf("%.4f ",DCMbi[i][j]);

        printf("\n");

    }

    //result is OK

}

int main(){

    TestQuaternion();

    TestTimeConversion();

    TestVector();

    TestTriad();

    return 0;

}

<!-- PDF_PAGE: 85 -->

## Appendix 2. Transformation from Sensor Frame to Satellite Body Frame

Define DCM $ _{SensorFrame}^{Body} $ is the Direction Cosine Matrix which transform the Sensor Frame to the Satellite Body Frame.

DCM $ ^{Body} $ SensorFrame is calculated from 3 Euler angles $ \Psi, \theta, \Phi $ and using Z-Y-X rotation sequence from Sensor Frame to the Satellite Body Frame.

$ \Psi $ is the rotation angle about the Z-axis of Sensor Frame.

$ \theta $ is the rotation angle about the Y-axis of Sensor Frame.

$ \Phi $ is the rotation angle about the X-axis of Sensor Frame.

3 Euler angles $ \Psi, \theta, \Phi $ is measured when the sensor is integrated to the satellite.

For any mounting location of sensors including Sun sensor, Gyro, Magnetometer, the transformation from Sensor Frame to Satellite Body Frame is calculated from the equation (2.1).

$$
\mathrm {D C M} _ {\mathrm {S e n s o r F r a m e}} ^ {\mathrm {B o d y}} = \left[ \begin{array}{c c c} \cos \theta . \cos \psi & - \cos \phi . \sin \psi + \sin \phi . \sin \theta . \cos \psi & \sin \phi . \sin \psi + \cos \phi . \sin \theta . \cos \psi \\ \cos \theta . \sin \psi & \cos \phi . \cos \psi + \sin \phi . \sin \theta . \sin \psi & - \sin \phi . \cos \psi + \cos \phi . \sin \theta . \sin \psi \\ - \sin \theta & \sin \phi . \cos \theta & \cos \phi . \cos \theta \end{array} \right]
$$

However, for Star tracker, because the output of Star tracker is the quaternion, therefore, to convert quaternion output in Sensor Frame to the quaternion in Satellite Body Frame, the DCM $ ^{Body}_{\mathrm{SensorFrame}} $ should be transformed to the quaternion $ q ^{Body}_{\mathrm{SensorFrame}} $ .

$$
\text {D e f i n e} \quad \mathrm {D C M} _ {\text {S e n s o r F r a m e}} ^ {\text {B o d y}} = \left[ \begin{array}{l l l} \mathrm {D C M} _ {1 1} & \mathrm {D C M} _ {1 2} & \mathrm {D C M} _ {1 3} \\ \mathrm {D C M} _ {2 1} & \mathrm {D C M} _ {2 2} & \mathrm {D C M} _ {2 3} \\ \mathrm {D C M} _ {3 1} & \mathrm {D C M} _ {3 2} & \mathrm {D C M} _ {3 3} \end{array} \right]
$$

The conversion from DCM $ ^{Body} $ $ SensorFrame $ to the $ q ^{Body} $ $ SensorFrame $ is as below.

Define $ q_{\mathrm{SensorFrame}}^{\mathrm{Body}}=\left[ \begin{array}{cccc} q_{1} & q_{2} & q_{3} & q_{4} \end{array} \right]^{\mathrm{T}} $ , $ q_{4} $ is the scalar.

Firstly, $ q_{1}, $ $ q_{2}, $ $ q_{3} $ and $ q_{4} $ are calculated:

$$
q _ {1} = \sqrt {\frac {1}{4} \left(1 + \mathrm {D C M} _ {1 1} - \mathrm {D C M} _ {2 2} - \mathrm {D C M} _ {3 3}\right)}
$$

$$
q _ {2} = \sqrt {\frac {1}{4} \left(1 - D C M _ {1 1} + D C M _ {2 2} - D C M _ {3 3}\right)}
$$

$$
q _ {3} = \sqrt {\frac {1}{4} \left(1 - D C M _ {1 1} - D C M _ {2 2} + D C M _ {3 3}\right)}
$$

$$
q _ {4} = \sqrt {\frac {1}{4} \left(1 + D C M _ {1 1} + D C M _ {2 2} + D C M _ {3 3}\right)}
$$

<!-- PDF_PAGE: 86 -->

Secondly, $ q_{1} $ $ q_{2}, q_{3} $ and $ q_{4} $ are re-calculated by the Table 2.1. For example, if the $ q_{4} $ is the maximum compare to other elements, the $ q_{1} $ $ q_{2} $ and $ q_{3} $ are re-calculated as the first row of the Table 2.1.

<div align="center">

Table 2.1. Calculating $ q_{\mathrm{SensorFrame}}^{\mathrm{Body}} $ elements

</div>

<table border="1"><tr><td>Maximum</td><td>$q_{4}$</td><td>$q_{1}$</td><td>$q_{2}$</td><td>$q_{3}$</td></tr><tr><td>$q_{4}$</td><td>$q_{4}$</td><td>$\frac{DCM_{32}-DCM_{23}}{4q_{4}}$</td><td>$\frac{DCM_{13}-DCM_{31}}{4q_{4}}$</td><td>$\frac{DCM_{21}-DCM_{12}}{4q_{4}}$</td></tr><tr><td>$q_{1}$</td><td>$\frac{DCM_{32}-DCM_{23}}{4q_{1}}$</td><td>$q_{1}$</td><td>$\frac{DCM_{21}+DCM_{12}}{4q_{1}}$</td><td>$\frac{DCM_{13}+DCM_{31}}{4q_{1}}$</td></tr><tr><td>$q_{2}$</td><td>$\frac{DCM_{13}-DCM_{31}}{4q_{2}}$</td><td>$\frac{DCM_{21}+DCM_{12}}{4q_{2}}$</td><td>$q_{2}$</td><td>$\frac{DCM_{32}+DCM_{23}}{4q_{2}}$</td></tr><tr><td>$q_{3}$</td><td>$\frac{DCM_{21}-DCM_{12}}{4q_{3}}$</td><td>$\frac{DCM_{13}+DCM_{31}}{4q_{3}}$</td><td>$\frac{DCM_{32}+DCM_{23}}{4q_{3}}$</td><td>$q_{3}$</td></tr></table>

In brief, the diagram of transformation function from Sensor Frame to Satellite Body Frame is showed in Figure 2.1.


![figure_069.png](figure_069.png)



<div align="center">

Figure 2.1. Diagram of transform function from Sensor Frame to Satellite Body Frame

</div>

For Star tracker, the calculating of the quaternion in the Satellite Body Frame is as below

$$
\mathrm {q} _ {\mathrm {B o d y}} = \mathrm {q} _ {\mathrm {S e n s o r F r a m e}} ^ {\mathrm {B o d y}} \mathrm {q} _ {\mathrm {S e n s o r F r a m e}}
$$

$ q_{\mathrm{Body}} $ is the quaternion in the Satellite Body Frame.

q $ _{SensorFrame} $ is the quaternion output in the Star tracker Frame.

For Sun sensor, the calculating of the sun vector in the Satellite Body Frame is below

$$
S _ {\mathrm {B o d y}} = \mathrm {D C M} _ {\mathrm {S e n s o r F r a m e}} ^ {\mathrm {B o d y}} S _ {\mathrm {S e n s o r F r a m e}}
$$

$ S_{Body} $ is the sun vector in the Satellite Body Frame

$ S_{SensorFrame} $ is the sun vector measured in the Sun sensor Frame

<!-- PDF_PAGE: 87 -->

For Gyro, the Gyro Frame should be aligned with the Satellite Body Frame when integrating, the angular rate vector in Satellite Body Frame is calculated as below

$$
\left[ \begin{array}{l} w _ {x} ^ {\mathrm {B o d y}} \\ w _ {y} ^ {\mathrm {B o d y}} \\ w _ {z} ^ {\mathrm {B o d y}} \end{array} \right] = \left[ \begin{array}{l} w _ {x} ^ {\mathrm {S e n s o r F r a m e}} \\ w _ {y} ^ {\mathrm {S e n s o r F r a m e}} \\ w _ {z} ^ {\mathrm {S e n s o r F r a m e}} \end{array} \right] + \left[ \begin{array}{l} d _ {x} \\ d _ {y} \\ d _ {z} \end{array} \right]
$$

$$
w ^ {\mathrm {B o d y}} = \left[ \begin{array}{c c c} w _ {\mathrm {x}} ^ {\mathrm {B o d y}} & w _ {\mathrm {y}} ^ {\mathrm {B o d y}} & w _ {\mathrm {x}} ^ {\mathrm {B o d y}} \end{array} \right] ^ {\mathrm {T}} \mathrm {i s t h e a n g u l a r r a t e v e c t o r i n S a t e l l i t e B o d y F r a m e}.
$$

$$
w ^ {\mathrm {Sensor Frame}} = \left[ \begin{array}{l l l} w _ {x} ^ {\mathrm {Sensor Frame}} & w _ {y} ^ {\mathrm {Sensor Frame}} & w _ {z} ^ {\mathrm {Sensor Frame}} \end{array} \right] ^ {\mathrm {T}} \mathrm {i s t h e a n g u l a r r a t e v e c t o r m e a s u r e d}
$$

in Gyro Frame.

The offset vector $ \mathrm{d}=[\mathrm{d}_{x} \quad \mathrm{d}_{y} \quad \mathrm{d}_{z}]^{T} $ is measured during the integration of Gyro to the Satellite.

For GPS Receiver processing, because the GPS Receiver outputs are the location of the sensor, therefore, there is no need to transform the outputs of GPS Receiver to the Satellite Body Frame. The location of Satellite can be considered as the location of the GPS Receiver.

<!-- PDF_PAGE: 88 -->

Appendix 3. Simulation of using Kalman Filter

1. Introduction about Kalman Filter

The original Kalman Filter is only applicable for linear systems. However, it is extended to deal with nonlinear systems by Extended Kalman Filter (EKF). The EKF is not always optimal and can diverge if initial errors are too large or if the system model is inaccurate.

Defining the discrete nonlinear system as:

$$
x _ {k} = f \left(x _ {k - 1}, u _ {k - 1}\right) + w _ {k - 1}
$$

$$
z _ {k} = h \left(x _ {k}\right) + v _ {k}
$$

where:

x is state vector

f (. ) describes the system dynamics

u is control input

w is process noise

h is the measurement model

v is the measurement noise

the subscript k denotes discrete time.

Both measurement and process noise are assumed to be zero mean Gaussian. Using the system described above, the equations for EKF:

At Predict phase:

$$
\hat {x} _ {k} ^ {-} = f \left(\hat {x} _ {k - 1}, u _ {k - 1}\right)
$$

$$
P _ {k} ^ {-} = F _ {k} P _ {k} F _ {k} ^ {T} + Q
$$

At Update phase:

$$
K _ {k} = P _ {k} ^ {-} H _ {k} ^ {\top} \left(H _ {k} P _ {k} ^ {-} H _ {k} ^ {\top} + R\right) ^ {- 1}
$$

$$
\hat {x} _ {k} = \hat {x} _ {k} ^ {-} + K _ {k} \left(z _ {k} - H _ {k} \hat {x} _ {k} ^ {-}\right)
$$

$$
P _ {k} = \left(I - K _ {k} H _ {k}\right) P _ {k} ^ {-}
$$

where:

x denotes estimated state vector

P is covariance matrix

K is calculated Kalman gain

<!-- PDF_PAGE: 89 -->

$$
F _ {k} = \frac {\partial f}{\partial x} \Bigg | _ {\hat {x} _ {k - 1}, u}
$$

is the derivate of the nonlinear system with respect to the states

$$
H _ {k} = \left. \frac {\partial h}{\partial x} \right| _ {\hat {X} _ {k - 1}}
$$

is the derivate of the measurement equations with respect to the states.

R is the measurement covariance matrix.

Q is the process covariance matrix.

Due to the complexity of the EKF, it is limited when implementation on a on-board computer of nano satellites.

2. Simulation of using Kalman Filter for satellite with one axis

Physical model:

The system model of a satellite with one axis is described in Figure 3.1. The sensors consist of a gyro and a star tracker.


![figure_070.png](figure_070.png)



<div align="center">

Figure 3.1 System model of satellite with one axis

</div>

One axis rotational angle $ \theta $ of satellite is measured.

The true value of $ \varTheta $ is: $ \varTheta_{t} $

$$
\ddot {\Theta} _ {t} = w \tag {3.2.1}
$$

w is white noise with $ 1 \sigma=0. 0 1 \mathrm{~ r a d / s e c}^{2} $

The true value of angular velocity of satellite:

$$
w _ {t} = \dot {\Theta} _ {t}
$$

<!-- PDF_PAGE: 90 -->

This angular velocity is measured by gyro at every 10 msec:

$$
w _ {\mathrm {m}} = w _ {\mathrm {t}} + w _ {1} + r \tag {3.2.3}
$$

w1 is white noise with $ 1 \sigma=0. 1 $ rad/sec

r is random walk with:

$$
\dot {r} = w _ {2}
$$

$ w_{2} $ is white noise with $ 1\sigma=0.1 $ rad/sec $ ^{2} $

At every 1s, the star sensor (star tracker) is used to measure $ \theta $:

$$
\Theta_ {\mathrm {m}} = \Theta_ {\mathrm {t}} + \mathrm {v}
$$

with v is white noise 1 $ \sigma=0. 0 1 $ rad

Derive the system dynamic equation and measurement equation

To estimate $ \theta $ and r, the estimated of these values are included in state vector x: Define the notation:

$$
\mathbf {x} = \left[ \begin{array}{l} \mathrm {x} _ {1} \\ \mathrm {x} _ {2} \\ \mathrm {x} _ {3} \end{array} \right], \dot {\mathbf {x}} = \left[ \begin{array}{l} \dot {\mathrm {x}} _ {1} \\ \dot {\mathrm {x}} _ {2} \\ \dot {\mathrm {x}} _ {3} \end{array} \right]
$$

$$
\mathrm {x} _ {1} = \theta_ {\mathrm {s}}
$$

$$
\mathrm {x} _ {2} = \dot {\Theta} _ {\mathrm {s}}
$$

$$
\mathrm {x} _ {3} = \mathrm {r} _ {s}
$$

The system estimation model:

$$
\left[ \begin{array}{l} \dot {\mathrm {x}} _ {1} \\ \dot {\mathrm {x}} _ {2} \\ \dot {\mathrm {x}} _ {3} \end{array} \right] = \left[ \begin{array}{c c c} 0 & 1 & - 1 \\ 0 & 0 & 0 \\ 0 & 0 & 0 \end{array} \right] \left[ \begin{array}{l} \mathrm {x} _ {1} \\ \mathrm {x} _ {2} \\ \mathrm {x} _ {3} \end{array} \right] + \left[ \begin{array}{c c c} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{array} \right] \left[ \begin{array}{l} 0 \\ \mathrm {w} \\ \mathrm {w} _ {2} \end{array} \right]
$$

Define the notation:

$$
A = \left[ \begin{array}{c c c} 0 & 1 & - 1 \\ 0 & 0 & 0 \\ 0 & 0 & 0 \end{array} \right], \quad B = \left[ \begin{array}{c c c} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{array} \right], w = \left[ \begin{array}{c} 0 \\ w \\ w _ {2} \end{array} \right]
$$

the system dynamic equation:

$$
\frac {\mathrm {d} \mathbf {x}}{\mathrm {d} t} = \dot {\mathbf {x}} = A ^ {*} x + B ^ {*} w
$$

Figure 3.2 shows the state vector including theta $ \theta $ and angular velocity w without using Kalman Filter. The state of system is not converged.

Figure 3.3 shows the states including theta $ \varTheta $ angular velocity w and covariance matrix P when using Kalman Filter. The state of system is converged after 6s.

The C source code of the simulation is showed as below.

<!-- PDF_PAGE: 91 -->


![figure_071.png](figure_071.png)




![figure_072.png](figure_072.png)




![figure_073.png](figure_073.png)



<div align="center">

Figure 3.2 States without using Kalman Filter

</div>


![figure_074.png](figure_074.png)




![figure_075.png](figure_075.png)




![figure_076.png](figure_076.png)




![figure_077.png](figure_077.png)



<div align="center">

Figure 3.2 States using Kalman Filter

</div>

<!-- PDF_PAGE: 92 -->

P11

2

1.5

1

0.5

0

-0.5

0 2 4 6 8 10 12

P22

1.2

1

0.8

0.6

0.4

0.2

0

0 2 4 6 8 10 12

P33

1.2

1

0.8

0.6

0.4

0.2

0

-0.2

0 2 4 6 8 10 12

P= $\left[ \begin{array}{c} \mathrm{P11} \\ \mathrm{P22} \\ \mathrm{P33} \end{array} \right]$

<div align="center">

Figure 3.3 State of covariance matrix using Kalman Filter

</div>

C source code of simulation Kalman Filter for Gyro and Star tracker

```c

#include <stdio.h>

#include <conio.h>

#include <math.h>

#include <stdlib.h>        /* srand, rand */

#include <time.h>        /* time */

#include "Matrix.h"

#include "Noise.h"

#define PI 3.14159265359    //PI

#define NMAX 1000    // number of iterations 10000

#define MAX 3    //number of matrix row, column

//physical simulation

double dt=0.01;    //dt=10 msec

//----1. Satellite Axis----------------------------------------------------//

double I_sat;

double T_res[NMAX];

double w_t[NMAX], theta_t[NMAX];

//----2. Sensor------------------------------------------------------------//

//2.1. Gyro

double r[NMAX]; //random walk

double w_m[NMAX];

```

<!-- PDF_PAGE: 93 -->

```cpp

//Gyro Noise

double w1=0.1; //w_noise

double w2=0.1; //noise random walk_dot

//2.2. Star data

double theta_m[NMAX];

//star noise

double v =0.01;

//-----3. Kalman------------------------------------------------//

//matrixs

double A[MAX][MAX], B[MAX][MAX], Q[MAX][MAX];

//state equation dx/dt=Ax+Bw  Q=E[x]

double P_dot[MAX][MAX]; double PK[NMAX][MAX][MAX]; //covarian matrix

double KK[NMAX][MAX]; //Kalman Gain

double R; //=v*v//Measurement Noise

//system estimation

double theta_s[NMAX];        //estimation of theta angle

double theta_s_dot[NMAX];    //estimation of theta_dot

double r_s[NMAX];            //estimation of r

//-----4. Controller------------------------------------------------//

double K_p = -2; double K_d = -0.5;

double T_target[NMAX];

//-----5. Reaction Wheel------------------------------------------------//

double I_rw =0.1;

double K_rw = 100;

double V_dot[NMAX],    V[NMAX];

//-----Init values------------------------------------------------//

//init Sat Axis

void init_Sat(){

    I_sat = 2.0;

    T_res[0] = 0;

    w_t[0]= 10*2*PI/60;

    theta_t[0] =50*PI/180;

}

//init sensor data

void init_Sensors(){

    //init Gyro data

    r[0]=0.03;

    w_m[0]= w_t[0] + genNoise(w1) + r[0];

    //init Star data

    theta_m[0] = 0; //before update time from Star

}

```

<!-- PDF_PAGE: 94 -->

```cpp

void init_RW(){

    //initial RW

    V_dot[0]=0;

    V[0]=0;

}

//---storeFiles----------------------------------------//

void storeFile_NoKalman()

{

    FILE * fp;

    int i;

    //store theta_t

    fp = fopen ("1.theta_t.txt", "w+");

    for(i=0;i<NMAX-1; i++)

    fprintf(fp,"%4.2f\n",theta_t[i]);

    fclose(fp);

    //store theta_m

    fp = fopen ("2.theta_m.txt", "w+");

    for(i=0;i<NMAX-1; i++)

    fprintf(fp,"%4.2f\n",theta_m[i]);

    fclose(fp);

    //store w_t

    fp = fopen ("3.w_t.txt", "w+");

    for(i=0;i<NMAX-1; i++)        fprintf(fp,"%4.2f\n",w_t[i]);

    fclose(fp);

    //store w_m

    fp = fopen ("4.w_m.txt", "w+");

    for(i=0;i<NMAX-1; i++)        fprintf(fp,"%4.2f\n",w_m[i]);

    fclose(fp);

    //store random walk

    fp = fopen ("5.r.txt", "w+");

    for(i=0;i<NMAX-1; i++)        fprintf(fp,"%4.3f\n",r[i]);

    fclose(fp);

}

//----Kalman Calculation----------------------------------------//

//init for system estimation model

void init_kalman_matrix()

{

    //init A

    A[0][0]=0.0;             A[0][1]=1.0;

    A[0][2]=-1.0;

    A[1][0]=K_p/I_sat;       A[1][1]=K_d/I_sat;             A[1][2]=0.0;

    A[2][0]=0.0;             A[2][1]=0.0;

    A[2][2]=0.0;

```

<!-- PDF_PAGE: 95 -->

```cpp

//init B

B[0][0]=1.0;        B[0][1]=0.0;        B[0][2]=0.0;

B[1][0]=0.0;        B[1][1]=1.0;        B[1][2]=0.0;

B[2][0]=0.0;        B[2][1]=0.0;        B[2][2]=1.0;

//init Q

Q[0][0]=0.0;        Q[0][1]=0.0;        Q[0][2]=0.0;

Q[1][0]=0.0;        Q[1][1]=w1*w1;        Q[1][2]=0.0;

Q[2][0]=0.0;        Q[2][1]=0.0;        Q[2][2]=w2*w2;

//init covarian matrix PK

PK[0][0][0]=1.0; PK[0][0][1]=0.0;        PK[0][0][2]=0.0;

PK[0][1][0]=0.0; PK[0][1][1]=1.0;        PK[0][1][2]=0.0;

PK[0][2][0]=0.0; PK[0][2][1]=0.0;        PK[0][2][2]=1.0;

}

void init_kalman_estimation()

{

    //init estimation

    r_s[0]=0;

    theta_s[0]=0;

    theta_s_dot[0]=0;

}

void storeFile_withKalman()

{

    FILE * fp;

    int i;

    //store theta_s

    fp = fopen ("5.theta_s.txt", "w+");

    for(i=0;i<NMAX-1; i++)

    fprintf(fp,"%4.2f\n",theta_s[i]);

    fclose(fp);

    //store w_s

    fp = fopen ("6.w_s.txt", "w+");

    for(i=0;i<NMAX-1; i++)

    fprintf(fp,"%4.2f\n",theta_s_dot[i]);

    fclose(fp);

    //store random walk estimate

    fp = fopen ("7.r_s.txt", "w+");

    for(i=0;i<NMAX-1; i++)        fprintf(fp,"%4.3f\n",r_s[i]);

    fclose(fp);

    //PK

    fp = fopen ("8.p11.txt", "w+");

```

<!-- PDF_PAGE: 96 -->

```cpp

for(i=0;i<NMAX-1; i++)

fprintf(fp,"%4.3f\n",PK[i][0][0]);

fclose(fp);

fp = fopen ("9.p22.txt", "w+");

for(i=0;i<NMAX-1; i++)

fprintf(fp,"%4.3f\n",PK[i][1][1]);

fclose(fp);

fp = fopen ("10.p33.txt", "w+");

for(i=0;i<NMAX-1; i++)

fprintf(fp,"%4.3f\n",PK[i][2][2]);

fclose(fp);

}

void init_Kalman(){

    init_kalman_matrix();

    init_kalman_estimation();

}

//calc P_dot (k)

void calc_P_dot(int k)

{

    double AT[MAX][MAX];

    double BT[MAX][MAX];

    double B1[MAX][MAX], B2[MAX][MAX]; //temp matrix

    double C1[MAX][MAX], C2[MAX][MAX], C3[MAX][MAX]; //temp matrix

    matrix_multi_matrix(A,PK[k],C1); //A*P

    calc_trans_matrix(A, AT);

    matrix_multi_matrix(PK[k],AT, C2);     //P*AT

    matrix_add_matrix(C1,C2,C3);      //A*P + P*AT

    matrix_multi_matrix(B,Q,B1);      //B*Q

    calc_trans_matrix(B, BT);

    matrix_multi_matrix(B1,BT,B2);     //B*Q

    matrix_add_matrix(C3,B2,P_dot); //A*P + P*AT + B*Q*BT

}

//calc Covarian Matrix PK(k)

void calc_PK(int k){

    int i,j;

    for(i=0;i<MAX;i++)

    {

        for(j=0;j<MAX;j++)

```

<!-- PDF_PAGE: 97 -->

```cpp

        PK[k][i][j] = PK[k-1][i][j] + dt*P_dot

    }

}

//calc Kalman Gain

void calc_KK(int k)

{

    double temp;

    R =v*v;

    temp=1/(PK[k][0][0] +R);

    KK[k][0] = temp*PK[k][0][0];

    KK[k][1] = temp*PK[k][1][0];

    KK[k][2] = temp*PK[k][2][0];

}

//update Covarian Matrix

void update_PK(int k)

{

    int i,j;

    double P_temp[MAX][MAX]      ;

    //copy PK[k] -->P_temp

    for(i=0;i<MAX;i++)

    {

        for(j=0;j<MAX;j++)

            P_temp[i][j] = PK[k][i][j];

    }

    PK[k][0][0] = (1.0-KK[k][0])*P_temp[0][0];

    PK[k][0][1] = (1.0-KK[k][0])*P_temp[0][1];

    PK[k][0][2] = (1.0-KK[k][0])*P_temp[0][2];

    PK[k][1][0] = P_temp[1][0] - KK[k][1]*P_temp[0][0];

    PK[k][1][1] = P_temp[1][1] - KK[k][1]*P_temp[0][1];

    PK[k][1][2] = P_temp[1][2] - KK[k][1]*P_temp[0][2];

    PK[k][2][0] = P_temp[2][0] - KK[k][2]*P_temp[0][0];

    PK[k][2][1] = P_temp[2][1] - KK[k][2]*P_temp[0][1];

    PK[k][2][2] = P_temp[2][2] - KK[k][2]*P_temp[0][2];

}

void estimate_state(int k){

    //estimate r_s = constant

    r_s[k]=r_s[k-1];

    //estimate theta_dot

    theta_s_dot[k]= w_m[k]-r_s[k];

```

<!-- PDF_PAGE: 98 -->

```cpp

//Estimation for theta_s

theta_s[k] = theta_s[k-1] + dt*theta_s_dot[k];

//caculate p_dot

calc_P_dot(k-1);

//calc covarian matrix PK

calc_PK(k);

}

//propagation and update

void update_phase(int k)

{

    calc_KK(k);        //calc Kalman Gain

    update_PK(k);      //update Covarian Matrix

//update state vector

//update theta_s_dot

theta_s_dot[k] = theta_s_dot[k] + (theta_m[k]-theta_s[k])*KK[k][1];

//update r_s

r_s[k] = r_s[k] + (theta_m[k]-theta_s[k])*KK[k][2];

//update theta_s_dot

theta_s[k] = theta_s[k] + (theta_m[k]-theta_s[k])*KK[k][0];

}

//---End of Kalman Calculation---------------------------------//

//----Calculation System Cycle---------------------------------//

void calc_requiredTorque(int k){

    //T_target[k] = K_p*theta_m[k-1] + K_d*w_m[k-1]; //No KF

    T_target[k] = K_p*theta_s[k-1] + K_d*theta_s_dot[k-1];

    //KF use theta_s w_s

}

void calc_appliedTorque(int k){

    V_dot[k] = (K_rw/I_rw)*T_target[k];

    V[k] = V[k-1] + dt*V_dot[k];

    T_res[k] = (I_rw/K_rw)*V_dot[k];

}

void get_data_from_Sensor(int k){

    //true value, can not know

    w_t[k] = w_t[k-1] + dt*T_res[k]/I_sat;

    //true value

    theta_t[k] = theta_t[k-1] + dt*w_t[k-1];

    //simulate data , get real data from sensor if not simulation

```

<!-- PDF_PAGE: 99 -->

```c

r[k] = r[k-1] + dt*genNoise(w2);

//from gyro

w_m[k] = w_t[k] + genNoise(w1) + r[k];

//measurement of star, use for kf

if(k%100 ==0 )

{

    theta_m[k] = theta_t[k] + genNoise(v);

}

else theta_m[k]=theta_m[k-1];

}

void system_cycle()

{

    int k; //steps of iteration

    for(k=1; k<NMAX; k++)

    {

        calc_requiredTorque(k); //from w and theta from KF

        calc_appliedTorque(k);

        get_data_from_Sensor(k);

        //estimate from kalman

        estimate_state(k);

        if(k%100==0) update_phase(k);

    }

}

void init_system(){

    //init random

    srand (1);

    init_Sat();

    init_Sensors();

    init_RW();

    init_Kalman();

}

int main()

{

    init_system();

    system_cycle();

    storeFile_NoKalman();

    storeFile_withKalman();

    return 0;

}

```