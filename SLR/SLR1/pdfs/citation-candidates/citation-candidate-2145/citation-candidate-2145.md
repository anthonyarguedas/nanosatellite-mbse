---
source: null
title: "citation-candidate-2145"
candidate_id: "citation-candidate-2145"
publication_year: 2014
converted_at: "2026-09-15"
---

# Communication analysis of QB50 cubesat network

Authors: March, G

<!-- PDF_PAGE: 1 -->

UNIVERSITA’ DI PISA


             Tesi di Laurea in Ingegneria Aerospaziale
                          Indirizzo Spaziale



COMMUNICATION ANALYSIS OF QB50
     CUBESAT NETWORK

                             Candidato
                           Günther March




  Relatori                                     Correlatori
  Prof. Salvo Marcuccio                        Thorsten Scholz
                                               Patrick Rambaud




                    Anno Accademico 2013-2014

<!-- PDF_PAGE: 3 -->

iii




Acknowledgements
I would like to gratefully acknowledge the supervision of Dr. Patrick Rambaud, and my university
supervisor Ing. Salvo Marcuccio during this work. I thank Thorsten Scholz for the fundamental
technical help, general advices and his friendship. His guidance helped me for all my permanence. I
could not have imagined having a better advisor and mentor for my stage.
A special gratitude I give to QB50 Project Manager, Dr. Jan Thömel, whose contribution in
stimulating suggestions and encouragement, helped me to coordinate my project. His support and
companionship made me feel at ease and a fledged member of QB50 project.
I would like to acknowledge the help of Fiona Singarayar for her support, especially for the final
report, her friendship, and nice discussions. I would like to thank all QB50 Team members, Dr.
Cem Asma, Isil Sakraker, and Gilles Bailet, they were always present and available to help me.
I am grateful to all my friends from VKI, for being my second family during my internship, and I
would like to thank also my italian friends for the support during past months. Finally, yet
importantly, I am forever indebted to my family, especially my mother Concetta, Riccardo, and
Hilde, for their understanding endless patience and encouragement when it was most required.

<!-- PDF_PAGE: 4 -->

iv




The writer thanks the von Karman Institute for Fluid Dynamics that allowed the author to deal with
this investigation.




Finally, the author of this thesis would like to thank Analytical Graphics, Inc. for the educational
license of their System Tool Kit software used extensively in this project.

<!-- PDF_PAGE: 5 -->

v




Abstract
In recent years emerged the idea of sending extremely small satellites into space; this new approach
involved first educational satellites, then also commercial satellites. Especially the field of small
satellite formations and constellations attracted growing attention, based on recent advances in
small satellite engineering. The utilization of distributed space systems allows the realization of
innovative applications and will enable improved temporal and spatial resolution in observation
scenarios. On the other side, this new paradigm imposes a variety of research challenges. A benefit
of designing small satellites is that they can be launched as secondary payloads, hence at moderate
costs. This makes it possible to install networks of satellites, carried from a single launch vehicle
into space. The concept of networked satellites promises progress in diverse application fields. One
application field with high potential for improvements through swarms of small satellites is Earth
observation. Satellites in Low Earth Orbit (LEO) are able to monitor environmental changes
without large delays. One of the most limited resources of a satellite in a LEO is surely the
communication time. The contact window between a satellite and a ground station can be
determined from the orbit elements and the location of the ground station. The main inconvenience
is that a satellite is only visible for a few minutes each day, this limits the amount of transferable
data dramatically and the ground station is not utilized for a large fraction of each day.

In this thesis a communication architecture for QB50 mission is analyzed. This space mission will
provide the biggest CubeSat network in orbit and it is carried out by a consortium of numerous
institutes and industries led by the von Karman Institute for Fluid Dynamics. This project consists
in a network of 50 CubeSats in a ‘string-of-pearls’ configuration that will be launched together in
January 2016 by a single rocket, into a circular orbit at 350 km altitude. Due to the atmospheric
drag, the orbit will decay in approximately 3 months and progressively lower layers of the
atmosphere will be explored. Main goals are exploration of the lower thermosphere with multi-
point measurements, re-entry research and in-orbit science and technology demonstration.

In this analysis of the functions of the communication ground segment is analyzed, having a global
overview of different architectures, the main elements of a ground station, mission and control
centers and the link between them. This study is realized through the development of a tool
computing the number of stations required to recover a certain amount of data generated by a
constellation of satellites. This tool ensures the efficiency of the communication system taking into
account various design parameters like data rates, limited elevation angles from ground stations,
and the effects on the link quality such as orbit perturbations, space and atmospheric losses and
Doppler shifts. Particular attention is devoted to frequencies; two different types of systems
(UHF/VHF and S-band) are analyzed.

In order to optimize the positioning and number of stations, an iterative method is applied to
compute the fraction of time when a station is in view of a CubeSat in function of various

<!-- PDF_PAGE: 6 -->

vi



parameters such as the latitude of the station, its elevation and the altitude of the satellite. During
the main part of the project, author used AGI-STK software to compute the accesses between a
constellation of satellites and a constellation of ground stations, simulating system operability.
Starting with a gradual approach, the analysis begins by ideal study of the communication behavior
between one CubeSat and a single ground station at VKI. After the selection of the communication
system architecture, author introduced the constellation concept, introducing also related
considerations due to communication overlaps between close satellites. Constellation problem is
deeply investigated by Combination Analysis, Ground Segments Analysis, and last analysis on a
single station at high latitude. Through this gradual investigation was possible to increase the
analysis complexity, having a detailed analytical description on communication behavior, and
finding reliable results, which are extremely useful for mission accomplishment.

<!-- PDF_PAGE: 7 -->

vii

<!-- PDF_PAGE: 8 -->

viii




Table of Contents
Acknowledgements ...................................................................................................................................... iii
Abstract ..........................................................................................................................................................v
Table of Contents ....................................................................................................................................... viii
List of Symbols ............................................................................................................................................ xi
List of Figures ............................................................................................................................................ xiii
List of Tables.............................................................................................................................................. xvi
1      Introduction ........................................................................................................................................18
1.1.       Background ......................................................................................................................................18
1.2.       The small satellite concept ...............................................................................................................19
       1.2.1.          CubeSats............................................................................................................................................. 20
1.3.       Benefits of small satellite concept ....................................................................................................22
1.4.       Small satellite development worldwide ...........................................................................................22
1.5.       A new concept of ground station networks ......................................................................................24
1.6.       Classic and academic ground station networks ................................................................................26
       1.6.1.          Architecture of academic ground station networks ............................................................................ 26
       1.6.2.          Differences between classic and new ground station approach .......................................................... 26
       1.6.3.          Global Education Network for Satellite Operations ........................................................................... 27
1.7.       Distributed satellite systems .............................................................................................................30
       1.7.1.          Application scenarios for distributed satellite systems ....................................................................... 31
       1.7.2.          Challenges and technologies for distributed space missions .............................................................. 31
2      QB50 Mission ......................................................................................................................................33
2.1.       QB50 project description .................................................................................................................33
2.2.       The lower thermosphere research.....................................................................................................35
2.3.       The re-entry phase research..............................................................................................................38
       2.3.1.          QARMAN CubeSat ........................................................................................................................... 39
2.4.       Launch and deployment phases........................................................................................................41
2.5.       Mission orbital mechanics ................................................................................................................44
2.6.       Mission Control Centres...................................................................................................................46
2.7.       Requirements for CubeSats, technical specifications.......................................................................46

<!-- PDF_PAGE: 9 -->

ix



2.8.      QB50 Communication challenge .....................................................................................................47
3      Communication Challenge ................................................................................................................48
3.1.      Communication role .........................................................................................................................48
3.2.      Earth geometry viewed from space ..................................................................................................49
3.3.      Satellite apparent motion with respect to Earth................................................................................52
3.4.      LEO communication ........................................................................................................................55
3.5.      Communication of multiple satellites...............................................................................................56
3.6.      QB50 communication strategies and configurations........................................................................56
       3.6.1.        Proposed communication systems ...................................................................................................... 57
3.7.      Analysis methodology ......................................................................................................................59
4      One-to-one problem ...........................................................................................................................61
4.1.      STK software and scenarios .............................................................................................................61
4.2.      Fixed Ground Station scenario .........................................................................................................64
4.3.      Ground Station with rotator mechanism ..........................................................................................67
5      Link Budget Analysis .........................................................................................................................70
5.1.      Ground segment ...............................................................................................................................70
       5.1.1.        VKI Ground segment ......................................................................................................................... 71
5.2.      Space Segment .................................................................................................................................73
5.3.      Radio wave propagation ...................................................................................................................74
       5.3.1.        Atmospheric loss ................................................................................................................................ 74
       5.3.2.        Ionospheric effects ............................................................................................................................. 76
       5.3.3.        Rain attenuation ................................................................................................................................. 76
       5.3.4.        Other Propagation Impairments ......................................................................................................... 78
5.4.      Antenna theory .................................................................................................................................79
       5.4.1.        Polarization ........................................................................................................................................ 79
       5.4.2.        Antenna bandwidth ............................................................................................................................ 81
       5.4.3.        Radiation Pattern ................................................................................................................................ 82
       5.4.4.        Efficiency and Antenna Gain ............................................................................................................. 83
       5.4.5.        Yagi Antennas .................................................................................................................................... 84
5.5.      Link design .......................................................................................................................................86
5.6.      Link Budget procedure .....................................................................................................................89
5.7.      QB50 Link Budget analysis .............................................................................................................90
       5.7.1.        Main Communication Link Losses .................................................................................................... 92
       5.7.2.        Link Margins and Thresholds............................................................................................................. 95
       5.7.3.        UHF/VHF System Link Budget ......................................................................................................... 96
       5.7.4.        S-band System Link Budget ............................................................................................................... 97
       5.7.5.        Comparison with other CubeSat projects ........................................................................................... 98
       5.7.6.        Results and selected architecture ........................................................................................................ 99
6      Constellation Analysis ......................................................................................................................101

<!-- PDF_PAGE: 10 -->

x



6.1.       Constellation issues ........................................................................................................................101
6.2.       STK setting.....................................................................................................................................102
       6.2.1.         Analyzed CubeSat configurations .................................................................................................... 103
       6.2.2.         Ground segment configurations ....................................................................................................... 104
       6.2.3.         Analyzed Scenarios .......................................................................................................................... 107
6.3.       Communication Overlaps ...............................................................................................................113
       6.3.1.         Minimum angle between CS to avoid overlaps ................................................................................ 115
6.4.       Ground Segments analysis .............................................................................................................116
       6.4.1.         Asia N/S Ground segment ................................................................................................................ 116
       6.4.2.         Northern Hemisphere E/W Ground segment ................................................................................... 120
       6.4.3.         America N/S Ground segment ......................................................................................................... 124
       6.4.4.         Europe Ground segment ................................................................................................................... 128
       6.4.5.         Ground Segments analysis results .................................................................................................... 132
6.5.       Combinations Analysis ..................................................................................................................134
       6.5.1.         Results for one GS ........................................................................................................................... 135
       6.5.2.         Results for 2 GSs .............................................................................................................................. 137
       6.5.3.         Results for 10 GSs ............................................................................................................................ 138
       6.5.4.         Results for 25 GSs ............................................................................................................................ 140
       6.5.5.         Evaluation of the Minimum GSs number ......................................................................................... 141
6.6.       Influence of orbit inclination ..........................................................................................................144
6.7.       Influence of ground station latitude................................................................................................146
6.8.       Use of a single GS at high latitude .................................................................................................148
       6.8.1.         GS 29 results .................................................................................................................................... 149
       6.8.2.         GS 30 results .................................................................................................................................... 152
       6.8.3.         GS 31 results .................................................................................................................................... 154
       6.8.4.         General considerations for single GS utilization .............................................................................. 157
7      Conclusions and further works .......................................................................................................158
7.1.       Final considerations........................................................................................................................158
7.2.       Possible further works ....................................................................................................................160
List of references ........................................................................................................................................162
Annex A .....................................................................................................................................................164
Annex B .....................................................................................................................................................171

<!-- PDF_PAGE: 11 -->

xi




List of Symbols
        ballistic coefficient
W       vehicle weight (kg)
CD      drag coefficient
L       lift force
D       drag force
CL      lift coefficient
RE      Earth radius
λ0      angular radius measured at the center of the Earth of the region seen by the spacecraft
ρ       angular radius of the spherical Earth as seen from the spacecraft
Dmax    maximum distance from the horizon
λ       Earth central angle
η       nadir angle
El, ε   elevation angle
δs      subsatellite latitude
Ls      subsatellite longitude
        angular velocity of Earth’s rotation around its axis
        satellite's angular velocity
        ground track velocity
        angular rate of the satellite as seen from the ground station
        orbital velocity of the satellite
T       total time in view
Kp      geomagnetic index
        specific attenuation
Rp      rain rate
A       total attenuation
Ap      rain attenuation
L       effective path length
Ls      slant length
hr      rain height
rp      rain reduction factor
BW      antenna's bandwidth
FH      highest frequency in the band
FL      lowest frequency in the band
FC      center frequency in the band
        antenna efficiency
εT      antenna’s total efficiency
ML      antenna’s loss due to impedance mismatch
G       antenna gain
Eb      received energy-per-bit
N       noise
N0      noise density

<!-- PDF_PAGE: 12 -->

xii



P     transmitter power
Ll    transmitter-to-antenna line loss
GR    receive antenna gain
k     Boltzmann’s constant
TS    system noise temperature
R     data rate
Ta    transmission path loss
Wf    effective isotropic radiated power
C     received power
AR    effective receive antenna aperture area
LS    space loss
TR    noise temperature of the receiver
f     signal frequency (Hz)

<!-- PDF_PAGE: 13 -->

xiii




List of Figures
Figure 1.1: The CalPoly CP1 CubeSat [1] ....................................................................................... 20
Figure 1.2: Skeleton of a single, double and triple CubeSat [5] ...................................................... 21
Figure 1.3: Illustration of the CanX-1 (Canadian Advanced Nanospace eXperiment-1). The first
picosatellite of UTIAS/SFL (University of Toronto, Institute for Aerospace studies/Space Flight
Laboratory) within the CubeSat frame of reference [24] ................................................................. 23
Figure 1.4: Illustration of the XI-IV picosatellite, X-factor Investigator is a project of ISSL
(Intelligent Space Systems Laboratory) at the University of Tokyo (UT), a participant in the
CubeSat program [11] ...................................................................................................................... 23
Figure 1.5: Map of locations of Estrack ground stations [10] .......................................................... 24
Figure 1.6: Comparison between European core network of the ESTRACK ground segment (on the
left) and a possible ground station configuration for academic GENSO network (on the right) [2] 25
Figure 1.7: Simple schematic of the GENSO architecture [3] ......................................................... 28
Figure 2.1: Map with the number of partners worldwide for the QB50 project [4] ......................... 34
Figure 2.2: Vertical structure of the atmosphere [5] ........................................................................ 37
Figure 2.3: VKI’s QARMAN CubeSat [6] ...................................................................................... 40
Figure 2.4: QARMAN scenario time line [6] .................................................................................. 40
Figure 2.5: Cyclon-4 Launcher (on the right) with predecessor launchers [7]................................. 41
Figure 2.6: Accommodations and StackPack configuration examples [8]....................................... 42
Figure 2.7: Example of accommodation inside cyclone upper stage (isometric view) [8] .............. 42
Figure 2.8: Distribution of CubeSats for deployment with random BC order after 20 days [12] .... 43
Figure 2.9: Distribution for 1 month after deployment [12] ............................................................ 43
Figure 2.10: Altitude as a function of mission time for a QB50 CubeSat, obtained with STK ....... 45
Figure 2.11: Velocity as a function of mission time for a QB50 CubeSat, obtained with STK....... 45
Figure 3.1: Relationship between geometry as viewed from the spacecraft and from the center of
the Earth [13].................................................................................................................................... 49
Figure 3.2: Definition of angular relationships between satellite, target and Earth center [13] ....... 50
Figure 3.3: Example of QB50 CubeSat Ground Track (green line), i=98 deg, h=350 km, obtained
with STK. ......................................................................................................................................... 51
Figure 3.4: Geometry of satellite ground track relative to an observer on the Earth’s surface [13] 52
Figure 3.5: Overlapping contact windows for adjacent ground stations .......................................... 55
Figure 3.6: Radio Frequency Spectrum [17] .................................................................................... 58
Figure 4.1: CubeSat orbit characteristics for STK scenarios. .......................................................... 63
Figure 4.2: CubeSat force model for STK scenarios........................................................................ 63
Figure 4.3: Altitude as a function of mission time for a QB50 CubeSat, obtained with STK ......... 64
Figure 4.4:STK scenario with fixed VKI Ground Station (obtained with STK).............................. 65
Figure 4.5:Schematic representation of different beamwidths for different communication systems
(green UHF/VHF cone, red S-Band opening angle). ....................................................................... 65

<!-- PDF_PAGE: 14 -->

xiv



Figure 4.6: Antenna azimuth-elevation rotator and controller YAESU G-5500. [18] ..................... 67
Figure 5.1: Relationship between Space Segment, Ground Segment and Data users. ..................... 70
Figure 5.2: Allocations for Antenna System (white arrow), and Control Computer Room (black
arrow). .............................................................................................................................................. 72
Figure 5.3: Approximate view from 1.8 m height from top of arc (5th segment), North direction. 73
Figure 5.4: Approximate view from 1.8 m height from top of arc (5th segment), South direction. 73
Figure 5.5: Total zenith attenuation at ground level: pressure of 1 atm, temperature of 20°C, and
water vapor of 7.5 g/m3. [19] ........................................................................................................... 75
Figure 5.6: Path length through rain [20] ......................................................................................... 78
Figure 5.7: E-field variation of Linear and Circular polarization. [16] ............................................ 80
Figure 5.8: Definition of antenna beamwidth. [14] .......................................................................... 81
Figure 5.9: Sample of a rectangular plot presentation of a typical 10 elements Yagi antenna [9] ... 82
Figure 5.10: Sample of polar plot of a typical 10 elements Yagi antenna. [9] ................................. 82
Figure 5.11: Yagi antenna with 6 directors and one reflector. [15] ................................................. 84
Figure 5.12: Skeleton of a Yagi antenna [15] .................................................................................. 85
Figure 5.13: Cross Yagi antenna [15] .............................................................................................. 85
Figure 5.14: Trade-off between antenna gain and transmitter power [13] ....................................... 87
Figure 5.15: AMSAT/IARU spreadsheet concerning orbit characteristics [21] .............................. 91
Figure 5.16: AMSAT/IARU spreadsheet concerning frequencies selection (UHF/VHF system) [21]
.......................................................................................................................................................... 91
Figure 5.17: Angles for the Estimated Pointing Error and Angles between S/C antenna symmetry
axis and vector from S/C to ground station for uplink and downlink [21]....................................... 93
Figure 5.18: Representation of Perfect Alignment and Miss-Aligned configurations [22] ............. 93
Figure 5.19: Polarization Loss Calculator (on the left) and representation of Polarization angle θ
(on the right) [21] ............................................................................................................................. 94
Figure 5.20: Selected solution for the following Constellation Analysis [23][18] ........................ 100
Figure 6.1: STK 3D visualization of QB50 network after around one month of lifetime, obtained
with STK ........................................................................................................................................ 102
Figure 6.2: CubeSats configurations: a) Group 1, angular distance of 72 deg; b) Group 2, angular
distance of 7.2 deg.......................................................................................................................... 104
Figure 6.3: Ground Segment groups for Constellation Analysis (obtained with STK) ................. 107
Figure 6.4: Scenario 0 output for GS group 1 (Asia N/S) with CS group 1 ................................... 108
Figure 6.5: Scenario 1 output for GS group 1 (Asia N/S) with CS group 1 ................................... 109
Figure 6.6: Scenario 2 output for GS group 1 (Asia N/S) with CS group 1................................... 109
Figure 6.7: Scenario 3 output for GS group 1 (Asia N/S) with CS group 1 ................................... 110
Figure 6.8: Scenario 4 output for GS group 1 (Asia N/S) with CS group 1 ................................... 111
Figure 6.9: Scenario 5 output for GS group 1 (Asia N/S) with CS group 1 ................................... 111
Figure 6.10: Scenario 6 output for GS group 1 (Asia N/S) with CS group 1 ................................. 112
Figure 6.11: Scenario 7 output for GS group 1 (Asia N/S) with CS group 1 ................................. 113
Figure 6.12: Schematic representation of overlapping access constraints ..................................... 114
Figure 6.13: Results of 2 CS and 1 GS Overlap Analysis .............................................................. 114
Figure 6.14: Evaluation plot for minimum angular distance in true anomaly to avoid
communication overlaps ................................................................................................................ 115
Figure 6.15: Data per day for CS Group 1 and Asia N/S Ground segment (Single CS results) .... 117
Figure 6.16: Data per day for CS Group 1 and Asia N/S Ground segment (Overall result) .......... 118
Figure 6.17: Data per day for CS Group 2 and Asia N/S Ground segment (Single CS results) .... 119
Figure 6.18: Data per day for CS Group 2 and Asia N/S Ground segment (Overall result) .......... 120
Figure 6.19: Data per day for CS Group 1 and Northern Hemisphere E/W Ground segment (Single
CS results) ...................................................................................................................................... 121
Figure 6.20: Data per day for CS Group 1 and Northern Hemisphere E/W Ground segment (Overall
result).............................................................................................................................................. 122
Figure 6.21: Data per day for CS Group 2 and Northern Hemisphere E/W Ground segment (Single
CS results) ...................................................................................................................................... 123

<!-- PDF_PAGE: 15 -->

xv



Figure 6.22: Data per day for CS Group 2 and Northern Hemisphere E/W Ground segment (Overall
results) ............................................................................................................................................ 124
Figure 6.23: Data per day for CS Group 1 and America N/S Ground segment (Single CS results)
........................................................................................................................................................ 125
Figure 6.24: Data per day for CS Group 1 and America N/S Ground segment (Overall results) .. 126
Figure 6.25: Data per day for CS Group 2 and America N/S Ground segment (Single CS results)
........................................................................................................................................................ 127
Figure 6.26: Data per day for CS Group 2 and America N/S Ground segment (Overall results) .. 128
Figure 6.27: Data per day for CS Group 1 and Europe Ground segment (Single CS results) ....... 129
Figure 6.28: Data per day for CS Group 1 and Europe Ground segment (Overall results) ........... 130
Figure 6.29: Data per day for CS Group 2 and Europe Ground segment (Single CS results) ....... 131
Figure 6.30: Data per day for CS Group 2 and Europe Ground segment (Overall results) ........... 132
Figure 6.31: Combinations Analysis idea ...................................................................................... 134
Figure 6.32: CS Group 2 overall results for 1 GS cases................................................................. 136
Figure 6.33: CS1 result for 1 GS configuration (Case 1) ............................................................... 136
Figure 6.34: CS Group 2 overall results for 2 GSs cases ............................................................... 137
Figure 6.35: CS1 result for 2 GSs configuration (Case 5) ............................................................. 138
Figure 6.36: CS Group 2 overall results for 10 GSs cases ............................................................. 139
Figure 6.37: CS1 result for 10 GSs configuration (Case 37) ......................................................... 139
Case 99                                                                        Case 100 Figure 6.38: CS Group 2 overall results
for 25 GSs cases ............................................................................................................................. 140
Figure 6.39: CS1 result for 25 GSs configuration (Case 97) ......................................................... 141
Figure 6.40: Minimum data collected per day for different numbers of ground stations ............... 141
Figure 6.41: CS1 result for 3 GSs configuration ............................................................................ 142
Figure 6.42: Overall results for 3 GSs configuration ..................................................................... 143
Figure 6.43: Number of accesses per day during mission lifetime for different orbit inclinations 144
Figure 6.44: Access time per day during mission lifetime for different orbit inclinations ............ 145
Figure 6.45: Transmitted data per day during mission lifetime for different orbit inclinations ..... 145
Figure 6.46: GS coverage range angles for different GS latitudes ................................................. 146
Figure 6.47: Number of access per day during mission lifetime for different GS latitudes ........... 147
Figure 6.48: Transmitted data per day during mission lifetime for different GS latitudes ............ 147
Figure 6.49: 3D Visualization of new ground stations close to North Pole ................................... 148
Figure 6.50: Access contact time and data per day for GS 29 (CS group 1).................................. 149
Figure 6.51: Data per day for GS 29 (CS group 1) ........................................................................ 150
Figure 6.52: Access contact time and data per day for GS 29 (CS group 2).................................. 151
Figure 6.53: Data per day for GS 29 (CS group 2) ........................................................................ 151
Figure 6.54: Access contact time and data per day for GS 30 (CS group 1).................................. 152
Figure 6.55: Data per day for GS 30 (CS group 1) ........................................................................ 152
Figure 6.56: Access contact time and data per day for GS 30 (CS group 2).................................. 153
Figure 6.57: Data per day for GS 30 (CS group 2) ........................................................................ 154
Figure 6.58: Access contact time and data per day for GS 31 (CS group 1).................................. 155
Figure 6.59: Data per day for GS 31 (CS group 1) ........................................................................ 155
Figure 6.60: Access contact time and data per day for GS 31 (CS group 2).................................. 156
Figure 6.61: Data per day for GS 31 (CS group 2) ........................................................................ 156
Figure 7.1: IRIDIUM Constellation ............................................................................................... 160

<!-- PDF_PAGE: 16 -->

xvi




List of Tables
Table 1.1: Classification of Satellites ............................................................................................... 19
Table 1.2: Comparison of ground station network concepts ............................................................ 27
Table 2.1: Orbital parameters of QB50 ............................................................................................ 44
Table 3.1: Wavelengths and frequencies for different communication bands ................................. 58
Table 4.1: Access results for UHF/VHF system with beamwidth of 27.5 deg (obtained with STK)
.......................................................................................................................................................... 66
Table 4.2: Access results for S-band system with beamwidth of 3 deg (obtained with STK) ......... 66
Table 4.3:Ground station rotor mechanism specifications (YAESU G-5500). [18] ........................ 68
Table 5.1: Propagation concerns for satellite communications systems [19] .................................. 74
Table 5.2: Specific attenuation coefficients [20].............................................................................. 77
Table 5.3: Reduction factors [20] ..................................................................................................... 77
Table 5.4: Uplink budget for the UHF/VHF system ........................................................................ 96
Table 5.5: Downlink budget for the UHF/VHF system ................................................................... 97
Table 5.6: Uplink budget for the S-band system .............................................................................. 98
Table 5.7: Downlink budget for the S-band system ......................................................................... 98
Table 6.1: Mother-CubeSat parameters for Constellation Scenario ............................................... 103
Table 6.2: Ground Station list of CubeSat flying institutes ........................................................... 104
Table 6.3: Minimum and maximum data per day accumulated during first 100 days of mission
lifetime (CS Group 1)..................................................................................................................... 133
Table 6.4: Minimum and maximum data per day accumulated during first 100 days of mission
lifetime (CS Group 2)..................................................................................................................... 133
Table 6.5: Ground stations used for the Combination Analysis, with the corresponding number
used for computations .................................................................................................................... 135

<!-- PDF_PAGE: 18 -->

18                                                                                       Introduction




1 Introduction

1.1. Background
Over recent years a new approach has come forward in the field of satellite engineering. This
approach corresponds mainly to the use of small satellites and new miniaturized technologies. It
originated from educational institutions and then adopted in diverse application fields.
The trend towards building satellites that are smaller, faster, better and cheaper was a reaction to
falling industry budgets in the late Nineties. The miniaturization trend of sending extremely small
satellites into space is growing up and the number of small satellites in operation calls for increased
regulatory attention.
Currently the small satellite industry is widely driven by what many refer to as the microspace
philosophy. The microspace philosophy is predicated on embracing commercial-off-the shelf
(COTS) technologies. This approach yields fast, inexpensive missions that track modern
technology curves much more closely than conventional space programs.
Converging technological and economic forces drive us inevitably to the next decades of small
satellite development. The increasing pace of new capabilities and convergence of key technologies
over the next few years will provide the next generation of satellite revolution "push" on small
satellites.
The scientific community awoke to the capabilities and advantages that small satellites hold for
existing and new space applications. The pattern of constructing and launching small satellites
within a short time-scale continues unabated. Satellites are currently big, expensive to build and
launch, vulnerable, impossible in practice to upgrade on-orbit and difficult to replace; but,
technology of small satellites are scaling new heights by the day.
With the evolution of satellite technologies, many believe that small satellites will be able to
perform all functions that larger satellites are currently performing today. The 21st century has
begun with a significant interest in smaller satellites. As an evidence of that ESA recently
completed its launcher family with VEGA, a small launcher capable of sending small satellites in
GEO and in interplanetary orbit at low cost, renouncing to the possibility of sending larger and
heavier satellites, in favor of satellites more limited in size and weight.
Another advantage of designing lightweight satellites is that they can be launched as secondary
payloads, and hence at moderate costs. This makes it possible to install networks of small satellites,
carried from a single launch vehicle into space.
The concept of networked satellites promises progress in diverse application fields. Specifically
from a computer scientist point of view, the network aspect is very interesting, although it is known
that handling, communicating and controlling distributed systems is very challenging.
Especially communication analysis turns out to be a difficult issue. An efficient utilization of
ground station resources requires proper scheduling of satellite contact windows and not only. But
there are also positive aspects, like the advantage of highly distributed ground station networks
with an inherently high degree of redundancy. This enables the reception of a satellite from
multiple terrestrial stations, resulting in parallel received data streams.

<!-- PDF_PAGE: 19 -->

Introduction                                                                                      19



The central topic of this thesis consists in different strategies to improve small satellites operability
with ground station networks. In the following chapters we discuss different concepts that optimize
the use of ground station resources within the QB50 mission proposed. Their performances are
investigated in detail and results from simulations are presented.
At center of dissertation there are CubeSats, the new low cost satellites, on which the scientific
community is focusing the interest of space engineering research during last years.




1.2. The small satellite concept
The phrase small satellites was promoted in the last years as an important catchword and expresses
the ongoing miniaturization efforts in satellite engineering. Nevertheless, the term small satellite is
not strictly defined, depending on the context it is used for a wide range of space vehicles. In the
last years the common understanding of a small satellite evolved to a spacecraft with less than 500
kilograms. Especially in academia the terms pico, nano, micro and mini-satellites were established
to describe different types of small satellites. The mass of a pico-satellite is less than 1 kilogram,
nano-satellites are space vehicles between 1 and 10 kg, micro satellites have a maximum mass of
100 kg and mini satellites have a mass between 100 and 500 kg. This classification is used quite
consistently, however, other definitions exist.


                                    Table 1.1: Classification of Satellites

            Group Name                                    Wet Mass

      1.    Large Satellite                               > 1000 kg

      2.    Medium Sized Satellite                        500 – 1000 kg

      3.    Mini Satellite                                100 – 500 kg

      4.    Micro Satellite                               10 – 100 kg

      5.    Nano Satellite                                1 - 10 kg           Small Satellites

      6.    Pico Satellite                                0.1 – 1 kg

      7.    Femto Satellite                               < 100 kg



A large number of small satellites were launched successfully, first pico-satellites were operated in
orbit in 2000, nano-satellites were launched long before (e.g. OSCAR-1 in 1961), but in the last
years the number increased steadily due to advances in miniaturization.
One of the milestones in small satellite development is surely the creation of the CubeSat standard,
which initiated a huge number of small-satellite projects worldwide. The concept of a CubeSat, a
small satellite with cubic shape, was first introduced by Professor Jordi Puig-Suari from California
Polytechnic State University (CalPoly) and Robert Twiggs from Stanford University. The
corresponding CubeSat Design Specification was already published in 1999.
A first batch of 5 CubeSats was launched in 2003, in the last years more than 50 CubeSats were
brought into orbit, neglecting many more projects currently under development or waiting for
launch.

<!-- PDF_PAGE: 20 -->

20                                                                                        Introduction



One of the key issues for the success of the CubeSat specification is the standardized structure,
which is now a broadly adopted interface used in small satellites development. Consequently,
launch providers offer launch slots for CubeSats, several launch adapter devices for piggyback
launches exist, launch opportunities are granted from the space agencies to universities. CubeSats
have various positive qualities and offer many missions solutions. The study is highly focused on
them, they seem to be one of the possible futures of space research.




                                  Figure 1.1: The CalPoly CP1 CubeSat [1]




1.2.1. CubeSats
The CubeSat concept was originally developed by the California Polytechnic State University and
by the Stanford University, with Professors J. Puig-Suari and R. Twiggs, and afterward it widely
circulates among the academic world. The CubeSat philosophy is different from the larger
satellites. The launch of a commercial satellite requires millions of dollars and a lot of time to cover
the period between the design and the launch. Whereas a CubeSat, with a small budget, can be
designed, tested and launched in a few years, allowing students to participate to all the phases of
the mission.
Today the CubeSat project is an international collaboration of more than 100 universities, high
schools and private firms developing their own designed small-satellites. Furthermore, thanks to
the great success of CubeSat projects, some safe interfaces for CubeSats have been developed and
the launch providers are definitely favorable to use the free space to set into orbit this kind of
nanosatellites.
CubeSats offer all the standard functions of a normal satellite (attitude determination and control,
uplink and downlink telecommunications, power subsystem including a battery and body-mounted
solar panels, on-board data handling and storage by a CPU, and either a technology package or a
small sensor or camera). It takes about two years to develop a CubeSat (from the provision of
funding until the launch).
A CubeSat must respect the CubeSat design specifications. This will ensure that the satellite is
compatible with the launcher’s interface and it will not interfere with the other payloads.

The key requirements for a CubeSat are summarized below:

     •   Its dimensions must be 10x10x10 cm

<!-- PDF_PAGE: 21 -->

Introduction                                                                                  21



    •   It must not exceed 1 Kg mass
    •   Its centre of mass must be within 2 cm of its geometric centre
    •   The CubeSat must not present any danger to neighboring CubeSats, to the launch vehicle
        or to the primary payload: all parts must remain attached during launch, ejection and
        operation and no pyrotechnics are allowed
    •   Whenever possible, the use of NASA or ESA approved material is recommended: it allows
        a reduction of out-gassing and contamination
    •   Rails have to be anodized to prevent cold-welding and provide electrical isolation between
        the CubeSat and the deployment system. They also have to be smooth and their edges
        rounded
       The use of Aluminum 7075 or 6061 is suggested for the main structure. If others materials
        are used, the thermal expansion must be similar and approved
       This prevents the CubeSat to conk out because of an excessive thermal expansion
       No electronic device can be active during launch. Rechargeable batteries have to be
        discharged or the CubeSat must be fully deactivated
    •   At least one deployment switch is required
       All deployable components, such as antennas, booms and solar panels can be deployed 30
        minutes after ejection into orbit
    •   It has to undergo qualification and acceptance testing according to the specifications of the
        launcher: at least random vibration testing at a level higher than the published launch
        vehicle envelope and thermal vacuum testing. Each CubeSat has to survive qualification
        testing for the specific launcher. Acceptance testing will also be performed after the
        integration into the deployment system


These are the fundamental features of a single CubeSat (1U), but there are bigger formats, as the
double CubeSats (2U) with the dimensions of 20x10x10 cm, and the triple CubeSats (3U) with the
next dimensions 30x10x10cm. The structure of a double CubeSat is obtained by stacking two basic
units, and obviously the structure of a triple CubeSat, stacking three basic units. The skeleton of
these structures is shown in Figure 1.2.
QB50 mission will comprise about 40 atmospheric double CubeSats and about 10 double or triple
CubeSats for science and technology demonstration.




                        Figure 1.2: Skeleton of a single, double and triple CubeSat [5]

<!-- PDF_PAGE: 22 -->

22                                                                                      Introduction




1.3. Benefits of small satellite concept
The most prominent argument for reducing the mass of a space vehicle is the reduced launch costs.
The price to bring an object into space is directly correlated to the mass of that object, therefore
less mass means less costs. That is also the main reason why the CubeSat standard is so successful
in educational context, as the launch cost for a 1 kg satellite is affordable for a university.
Meanwhile many funding sources are available to get an educational satellite into orbit.
One more benefit, which is closely related to the reduced mass, and consequently also reduced
complexity, is the short development time. The small satellite concept enables realization in
extremely short time frames, obstacles are currently rather launch opportunities, which quite often
delay the operation of a satellite much longer than the actual development time.
Another important benefit is that a costumer can conduct an experiment on a dedicated satellite and
is therefore independent of other parties. This enables customizing the satellite individually for one
specific experiment or mission.
Very interesting for future satellite missions is the usage of distributed satellite systems for new
application fields. The innovative idea, which coincides also with QB50 concept, is the utilization
of several small satellites instead of a single large satellite to perform a task or mission. Possible
application fields are for instance multi-point measurements used to increase the spatial and
temporal resolution of a measured parameter (e.g. in space weather research), or efficiency
improvement with interferometry (e.g. in astronomy). Such distributed missions require the
possibility of launching a large amount of vehicles into the desired orbit, here the small satellite
concept shows its strength. Due to reduced size and mass it is possible to deploy many satellites
with a single launch vehicle in orbit. That has been already demonstrated several times with the
launch of CubeSat batches and currently QB50 mission integrating 50 CubeSats into a single
launch vehicle.
Of course, the reduced size and weight of these satellites induces also restrictions: the most obvious
drawback is the fact that the payload budget is very restricted. Therefore, huge devices or heavy
components cannot be accommodated. Thus, current small satellite missions are restricted to low
Earth orbits.
Another issue is the restricted lifetime, due to restricted power resources or missing redundancy
concepts. Admittedly, CubeSats have been already operated for more than 5 years, but the lifetime
of most small satellites lies only between few months and around 2 years.
In summary, the small satellite concept is still a very new field of interest and much research
focuses currently on miniaturization and enabling technology. Nevertheless, the scientific potential
leads to a steadily increasing number of planned small satellite missions, demonstrating the interest
in this emerging field. This new concept of small, lightweight, orbital vehicles complements the
traditional approach of satellite engineering and offers new strategies in niche applications.




1.4. Small satellite development worldwide
The introduction of the CubeSat specification in 1999 initiated a wave of small satellite projects
worldwide. A rapid growth of small satellite projects was observed in the last ten years.
Currently, the main contribution to the small satellite community comes from North-America,
Europe and Asia. The most active community is located in the US, which launched so far more
than half of all pico-satellites. Surely one of the best known research group from the North-
America comes from Canada with the Canadian Advanced Nanospace eXperiment (CanX)
program. It is operated by the University of Toronto Institute for Aerospace Studies, Space Flight
Laboratory (UTIAS/SFL). The program's objectives are to involve graduate students in the process

<!-- PDF_PAGE: 23 -->

Introduction                                                                                                         23



of spaceflight development, and to provide low-cost access to space for scientific research and the
testing of nanoscale devices.
In Europe a wide range of institutions (from Denmark, Netherlands, France, Italy, Switzerland etc.)
are involved in small satellite projects.
From Asia mainly Japan and China brought their own small satellites into orbit. Among the most
famous Asian projects there is certainly XI-IV, which is a picosatellite project of ISSL (Intelligent
Space Systems Laboratory) at the University of Tokyo (UT), a participant in the CubeSat program.
The objective of this program is to demonstrate and validate a picosatellite bus system and the
space use of commercial-of-the-shelf (COTS) parts, including also the successful on-orbit
operation of the picosatellite.
Some main manufacturers of microsatellites include SpaceDev and Surrey Satellite Technology
Ltd, while for nanosatellites there are GomSpace, ISIS, NovaNano and UTIAS-SFL.




    Figure 1.3: Illustration of the CanX-1 (Canadian Advanced Nanospace eXperiment-1). The first picosatellite of
 UTIAS/SFL (University of Toronto, Institute for Aerospace studies/Space Flight Laboratory) within the CubeSat frame
                                                   of reference [24]




 Figure 1.4: Illustration of the XI-IV picosatellite, X-factor Investigator is a project of ISSL (Intelligent Space Systems
                 Laboratory) at the University of Tokyo (UT), a participant in the CubeSat program [11]

<!-- PDF_PAGE: 24 -->

24                                                                                      Introduction




1.5. A new concept of ground station networks
A new thought concerning satellites naturally implies a new concept of ground station networks. Of
course the idea to combine ground stations in a network is not a recent invention. Since the first
space missions the ground segment consisted of several entities, and exchanging information
between these parts can be already considered as networking. The aggregation of different stations
was already performed in the beginning of the space era to achieve better coverage or to increase
redundancy. A good example for this "classic" approach is the ESA ESTRACK system, which was
initiated already in the early 70’s. Also NASA started quite early with the combination of different
stations to networks, e.g. the Deep Space Network (DSN) was established in 1958.

In Figure 1.5 there is a map showing locations of Estrack ground stations. Blue indicates core ESA-
owned stations operated by the Estrack Control Centre (ECC), at ESA/ESOC, Darmstadt,
Germany. Orange indicates Augmented Estrack stations, procured commercially and operated on
behalf of ESA by commercial entities. Green indicates Cooperative Estrack stations fully owned
and operated by outside agencies, but regularly providing services on an exchange basis.




                         Figure 1.5: Map of locations of Estrack ground stations [10]




Nevertheless, a new concept of ground station networks originated from the small satellite
community and developed in the last years. In this "new" concept the ground stations from the
individual small satellite projects are combined to extend the access time to space vehicles. At a
first glance the "classic" and the "new" ground station network approaches seem fairly similar,
nevertheless significant differences exist: the most obvious difference between the classical and the
new approach is the topology. The classic ground station network contains only a few, but
therefore highly specialized stations, to support a broad spectrum of space missions. On the other
side the newly emerged networks exhibit a high degree of distribution, composed of many low-cost
ground stations (comparable to the architecture of the Internet), supporting very similar types of

<!-- PDF_PAGE: 25 -->

Introduction                                                                                              25



space missions (i.e. small satellites in LEO). This fundamental difference in topology affects the
characteristics of the complete network, with all its requirements and objectives, but also
constraints and bottlenecks.
An important aspect related to the taxonomy of the term ground station has to be clarified: in
literature the space segment is typically divided into mission control and ground station network.
The mission control is aggregated in control center (Mission Control Center (MCC), Spacecraft
Operations Control Center (SOCC)) and it is responsible for mission planning and mission
operations, e.g. monitoring and commanding the spacecraft. On the other side the ground station
network, composed of different ground stations, deals with signal reception and transmission, orbit
tracking, etc. The mission control and the ground station network are not only logically divided,
they are also often geographically separated from each other. A typical ground station contains in
this context several receiving stations including different types of antennas as well as
corresponding hardware equipments. A ground station describes in a classic sense a sophisticated
system containing a larger number of facilities for satellite communication.
On the contrary, in the context of small satellite projects, a ground station is considered rather as a
single entity used to access one single satellite. This ground station, in contrast to the classical
definition, is a standalone system, comprising all components to communicate with the satellite, i.e.
antenna, transceiver, tracking hardware, data distribution system, etc. There is not any clear
distinction between mission control and ground stations. Furthermore, a ground station here
consists typically only of one antenna system and corresponding equipment for communication
with a single satellite in LEO.




 Figure 1.6: Comparison between European core network of the ESTRACK ground segment (on the left) and a possible
                     ground station configuration for academic GENSO network (on the right) [2]

<!-- PDF_PAGE: 26 -->

26                                                                                      Introduction




1.6. Classic and academic ground station networks

1.6.1. Architecture of academic ground station networks
The reason why academic ground stations are so similar in architecture, is that they are designed
for the communication links typically used in small satellites. Due to the limited mass and power
budget and the restricted pointing capabilities, the transceivers used for communication are
primarily UHF and VHF. The utilized frequency bands, 70cm and 2m, are part of the amateur radio
bands and they are under the supervision of the International Amateur Radio Union (IARU).
Higher frequency bands, e.g. S-Band, will be the next step in the evolution process of small
satellites, but they are still rarely used. Of course that affects the architecture of academic ground
stations: since hardware components for UHF and VHF are commercially available, many ground
stations are built up from low cost commercial of-the-shelf components.
The ground stations of an academic network are connected through the Internet and each ground
station in the network can be seen as an access node to a satellite, which is in contact range.
Typically only one communication link to a satellite can be established at the same time. However,
it is possible to track one satellite with several ground stations in parallel, in order to achieve a
more robust connection or to increase redundancy.
The primarily used protocol for data exchange between ground stations and a satellite is AX.25,
which is conform to HDLC ISO standard 3309. AX.25 originates from the X.25 protocol and it was
adapted for the special needs of the radio amateur community. It is used as data link layer protocol
in packet radio mode. AX.25 is accepted in the small satellite community as a standard
communication protocol.




1.6.2. Differences between classic and new ground station
approach
The distinction between "classic" and "academic" ground station networks is very important, due to
crucial differences in architecture and topology and therefore different capabilities and
characteristics.
Academic ground networks might support more missions in all, but those missions have typically
only a short lifetime and do not require a certain level of service. Conversely classic ground station
networks are used for less missions, but predefined services and support are guaranteed. Major
emphasis in academic networks is placed on the need for flexibility. For classic ground station
networks operation plans are created for long time spans to maintain a high utilization and to
satisfy the needs of the customers. In the field of academic ground station networks the situation is
totally different: most participants are from non-commercial institutions, involved personnel is not
available 24 hours a day, ground stations are sometimes unexpectedly not available. The result is a
highly dynamic topology in academic ground station networks, and the need for flexibility results
for instance in different scheduling objectives compared to classical ground station networks.
Another crucial point is that classic ground station networks are open to paying customers. In order
to run a huge ground station network a large part of the available budget comes from facility fees.
At the current stage in academic ground station networks there is no commercial interest,
participants are contributing with their own ground station and can use other stations of the
network free of charge. Costs occurring for a ground station, e.g. maintenance, are charged to the
owning institution. Of course that affects the objectives of the network, rather than increasing the
utilization of the network, which makes sense if the network has to be commercially successful.

<!-- PDF_PAGE: 27 -->

Introduction                                                                                    27



The aim of academic networks is to share the sparse resources of ground stations hardware,
respectively access time.
A perfect example of academic ground station network is surely the Global Education Network for
Satellite Operations (GENSO) that, once completed, will be an excellent resource for many space
mission communications.
At first it was believed that it could be completed and operating by the launch of QB50, but there
are not great chances to see the network operating by 2015.
For this reason, CubeSat teams working on the mission were encouraged to set up an academic
subset ground station network comprising any number of ground stations.


                          Table 1.2: Comparison of ground station network concepts

        Academic Ground Station Network                   Classic Ground Station Network

               Highly distributed network                      Clustered in operation center

          Supports mainly small satellite LEO                Supports wide range of satellite
                      missions                                         missions

                    Low-cost stations                         High end devices and stations

               Generic, replaceable stations                  Specialized, dedicated stations

                    Dynamic topology                        Strictly defined network topology

                  Distributed organized                     Centrally controlled and managed

                 No commercial interest                       Provided to paying customers

               Sharing resources to extend
                                                                Utilization increase desired
               communication time desired




1.6.3. Global Education Network for Satellite Operations
The Global Education Network for Satellite Operations (GENSO) was started in 2006 from the
International Space Education Board (ISEB), which consists of the educational departments of
CSA, JAXA, NASA and ESA. It would eventually comprise more than 100 ground stations in
different parts of the world, providing a vastly improved uplink and downlink capability for all
CubeSats. The University of Vigo in Spain hosts the European Operations Node and
coordinates access to the GENSO network. The software development was carried out by a set
of students and radio amateur teams distributed worldwide.
Objectives of the GENSO project are to allow remote access for operators to their satellites over
the network, to provide remote control of the participating ground stations, and to define and
implement a global standard for educational ground stations. The main goal of GENSO is to realize
a worldwide network of radio amateur and university ground stations to support the operations of
university satellites. In order to achieve this goal, GENSO has been designed as a distributed
system connected via the internet. GENSO offers the capability to plan and schedule utilization of

<!-- PDF_PAGE: 28 -->

28                                                                                     Introduction



ground station resources, to predict the trajectories of spacecrafts over the ground station, and to
automate tracking and hardware control during a pass.

GENSO aims to provide:

        Unparalleled near-global access to the mission operators of educational and radio
         amateur spacecraft
        Remote access for operators to real-time mission data, even in cases when their
         local ground station is experiencing technical difficulties
        Scheduling of remote uplink sessions via trusted ground stations
        Optional automatic remote control of all participating ground stations
        Downlink error-correction by comparing multiple data streams
        Definition of an optional standard solution for educational ground-segment
         hardware, designed to optimize return from GENSO at minimal cost
        Recommendations for future educational space hardware in order to enhance
         mission return by utilizing GENSO
        Close collaboration with the amateur radio community to support a common
         interface for applying for frequency allocation and coordination.

Access to the GENSO network is possible via one of the two main software applications. Ground
station operators run a Ground Station Server (GSS) and mission controllers run a Mission Control
Client (MCC). This secure access is controlled by the GENSO Authentication Server (AUS), which
ensures at all times that the entities participating in the network are allowed to do so.
During a pass, the ground station receives data from the satellite, which are stored locally by the
GSS. The GSS then notifies the AUS, which in turn notifies the MCC owning the satellite. The
MCC can then retrieve the data directly from the GSS (data are not stored in the AUS). Data may
therefore be inspected or replayed locally at either GSS or MCC.




                         Figure 1.7: Simple schematic of the GENSO architecture [3]

<!-- PDF_PAGE: 29 -->

Introduction                                                                                  29




GENSO offers many benefits for the operation of small satellites in Low Earth Orbit (LEO). The
key challenge for missions operating in LEO is that the spacecraft is above the horizon of a ground
station for only a few minutes each day.
For the rest of the time, missions rely on manually collected beacons from other ground station
operators or simply they have to wait for the spacecraft to pass overhead again.
GENSO extends the timeframe for communication with a LEO satellite from the normal value of
approximately 20 minutes a day, up to a theoretical maximum of 24 hours a day by tunnelling the
traffic over the internet. This applies not only to the downloading of telemetry, but also to the
transmission of telecommands.
GENSO has the potential to offer many additional services for participating missions and ground
stations through the application of novel scientific approaches. The open source nature of the
project will allow individuals to develop any number of enhancements to the system. While the
dramatically-increased communication timeframe is one of the major benefits of GENSO, many
other advantages can be envisaged, such as:

     Spacecraft orbit deviation measurements
     Access to a satellite within minutes in case of emergency, no matter where the satellite is
      located in its orbit
     A significantly lowered bit error rate in receive-mode by aggregating multiple pass reports to
      statistically detect bit errors
     Automated ground station de-calibration detection
     Pass quality prediction for avoidance of low quality passes with hardly any or no payload
      outcome and therefore optimization of resource utilization
     A manifold of statistics on link quality, spacecraft communication ability, spacecraft transmit
      power, ground station communication facilities, and much more
     Rapid orbit determination after launch, long before institutions such as NORAD are able to
      provide reliable orbit information
     Significantly extended mission lifetimes and returns on investment, due to increased
      frequency of downlinks, faster TLE determinations after launch and the possibility to contact
      the satellite independently of its position.

The GENSO community is a valuable resource, not only for increased access to spacecrafts, but
also for advice, technical support for ground and space hardware, object identification on busy
launches, assistance during critical mission operations, and many other possibilities. When GENSO
network will be completed, and operating communications between satellites and ground stations
will be significantly improved, then we will have a sophisticated, practical and flexible
communication system, able to perform and provide an useful contribution to space communication
and research.

<!-- PDF_PAGE: 30 -->

30                                                                                       Introduction




1.7. Distributed satellite systems
New opportunities due to reduced size and mass were pointed out and efforts in the ground
segment to establish networks were discussed. Altogether these developments are strong
indications towards a new
generation of distributed space missions in the future.
Beside the space segment also the ground segment is integral part of each space mission. In a
simple view, one could already see one satellite and one ground station as a distributed system. But
it is more suitable to consider a general case, having a multi satellite system connected to a ground
station network. Therefore, one can identify two different distributed systems, one in space and
another one on ground, both in close relationship with each other.
The topology of the ground segment plays an important role for telemetry and telecommand. Due
to the movement of the satellites on their orbits, the communication links between ground stations
and satellites change frequently. That adds new challenges to the operation of a satellite network,
so that careful planning and scheduling are necessary.

Beside saving the costs, a very interesting side effect of reducing the mass is the ability to launch
several satellites together with a single launch vehicle, which is an important ability for future
space infrastructures. This was already performed several times in the CubeSat community, where
several of these satellites were piggybacked on the primary payload to further lower the launch
costs. It is still a very common strategy to attach small satellites to larger ones, since a dedicated
launch vehicle would be too expensive. Meanwhile this launch strategy was extended to bring
multi satellites into space.
The result is that distributed satellite systems can be realized now with affordable costs. The
current evolution towards extremely small satellites will promote even more highly distributed
systems. The paradigm change from single large satellites to distributed space missions with a large
number of satellites is currently going on. Distributed systems in space will be used mainly to
realize distributed applications.
Main drivers for a distributed application in space are higher spatial or temporal resolution, or the
usage of concepts like interferometry. But not only new application scenarios are the driver for
establishing networks in space, the concept of distributed intelligence was successfully
demonstrated in the last years in various fields, for example Internet or sensor networks. The idea is
always to have a huge number of nodes, each with restricted capabilities and knowledge about the
environment, but the complete network behaves "intelligent" and can fulfill a more effective task
than one single complex system. Furthermore, a possible decentralized organization or control
makes the system robust and reliable. Graceful degradation is a capability strongly desired in the
case of failures.
Altogether this paradigm shift from large single satellites to distributed small satellites is apparent
in many fields, and it is a hot research topic discussed in many workshops and conferences .The
concept of distributed satellite systems will not replace the classical approach of launching single
satellites, it will be rather a possibility for specific mission scenarios.

<!-- PDF_PAGE: 31 -->

Introduction                                                                                   31



1.7.1. Application scenarios for distributed satellite systems
The most critical question is of course about benefits of distributed systems in space. As it was
already indicated, main drivers for multi satellite systems are distributed applications. There are
many good reasons why an application should be implemented in a distributed way, for example to
achieve higher robustness in case of failure, or to increase resolution.
One application field with high potential for improvement through swarms of small satellites is
Earth observation. Satellites in Low Earth Orbit (LEO) are able to monitor environmental changes
without large delays. The low height of the orbit enables high spatial resolution on Earth and
provides therefore huge potential for applications like disaster monitoring. Even with small
satellites environmental changes like natural disasters can be observed. But the orbits of these
satellites are such that they are orbiting with a high velocity around Earth, resulting in short
observation periods in desired areas and large gaps until the ground track repeats. The solution for
that problem is a higher temporal resolution, achievable through several satellites in the same orbit.
This can be easily achieved for example with the launch of several cubesats. The reduced launch
costs enable a high temporal resolution, resulting in a contact time roughly every 10 minutes. The
future development of small satellites for Earth observation is therefore very promising.
Another interesting application could be the creation of 3-dimensional images out of data collected
by a swarm of satellites. That could be achieved by means of the different viewing angles of
satellites in the same orbit, flying in a leader-follower constellation.
A very interesting application field for small satellite swarms is space weather research. The
scientific objective of QB50 mission is just the in situ measurement of spatial and temporal
variations of key parameters in the lower thermosphere. Current missions related to that topic face
two problems: in order to better approximate atmospheric models, a more detailed knowledge
about relevant parameters is necessary. A single satellite delivers only single measurements at a
given time, and to increase the accuracy of current atmospheric models, the spatial resolution of the
measurement has to be increased. The simplest way to realize that kind of multipoint measurements
is a multi satellite system. A second crucial problem is the severe environment of the lower
atmospheric layers, which reduces dramatically the lifetime of a satellite in low altitude Earth
orbits. Hence, the usage of low-cost satellites to obtain information about the composition of these
lower atmospheric layers is favorable. In QB50 mission measurements are performed from 50
double CubeSats, launched together and separated consecutively from the launch vehicle.
Furthermore, the re-entry process of the distributed satellite system is studied. One key aspect for
the proper operation of 50 satellites flying near to each other in nearly the same orbit is efficient
scheduling.




1.7.2. Challenges and technologies for distributed space missions
From a technological point of view there are still several challenges to be faced in order to realize
such distributed missions in orbit. Formations of conventional satellites would be too expensive for
implementation in space. The small satellite concept is more cost-efficient due to reduced launch
costs, but limited mass and power budgets restrict the utilization of state of the art components and
subsystems to provide necessary capabilities. Especially attitude and orbit control functions are
mandatory to enable precise formation flying. Miniaturized AOCS components designed for small
satellites are indeed in focus of different research teams, but they have been rarely demonstrated in
orbit. Also relative distance measurements are required to efficiently control formations, and
advanced sensors and actuators are required to achieve the desired accuracy.
Beside hardware devices, proper control algorithms are needed to maintain a formation. Here, the
individual satellites as well as the complete formation need to be controlled with respect to attitude

<!-- PDF_PAGE: 32 -->

32                                                                                      Introduction



and orbit, in order to keep constant the relative distances between the vehicles. A major issue for
formations as well as for swarms is communication in highly distributed networks. Especially inter
satellite communication rises several problems in a highly dynamic environment, for example
routing, data flow optimization and link interruption handling.
A distributed satellite system does not necessarily need self organization capabilities, for example
does the GPS constellation contain more than 30 satellites, nevertheless they are individually
controlled from ground. But with a growing number of vehicles, the effort for individual operation
increases dramatically. Even with only a small number of assets in the network it might be
necessary to include self organization techniques, if fast actions or decisions are desired, e.g. for
collision avoidance. A manually controlled satellite might not be able to detect a critical situation
early enough to avoid the collision. Therefore, autonomous reactions should be implemented to
guarantee safe modes, e.g. in close distance formations.
Having a highly distributed formation or constellation in space also induces requirements for the
ground segment. Missions with a large number of satellites impose a lot of work for operators.
Considering a future space mission, which contains more than 100 small-satellites, would increase
the workload enormously. Commanding 100 different satellites individually from ground, which in
case of a satellite cluster have almost the same contact times on a local ground station, is nearly
impossible. Additionally, interferences between them might even more perturb proper mission
operations. A possible solution could be a fully autonomous satellite network with no interaction of
any human operator.
The ability to launch a satellite formation or swarm on a single launch vehicle was enabled by the
decreasing mass and size of actual satellite platforms. On the other side, the small satellite concept
suffers from limited capabilities due to mass and power restrictions. Even if the research focus of
many teams lies on further miniaturization of satellite components, there is still a strong need for
enabling technologies: in nowadays pico and nano-satellite platforms two major bottlenecks
originate from the mass and power restrictions. Many researchers from the small satellite
community try to overcome these issues by the development of miniaturized components and
subsystems especially designed for small scale space vehicles. Meanwhile a variety of innovative
systems are available even for CubeSats, including miniaturized star trackers, micro reaction
wheels or tiny propulsion systems such as cold-gas thrusters or pulsed plasma thrusters.
Another critical bottleneck is the communication subsystem. The limited power budget in
combination with less accurate pointing accuracy led to the utilization of lower frequency bands
(mainly UHF or VHF) in current satellite platforms. Furthermore, a broad spectrum of COTS radio
amateur hardware is available and proved its performance in several missions. The main drawback
is the low transmission rate provided from those COTS components, many small satellites are
restricted to 9600 bps or even less. Migration to higher frequency bands are planned, but ongoing
activities are still in development phase. Most developers envisage S-band communication as a
possible technology for higher data rates, and single missions already accommodated such systems.

<!-- PDF_PAGE: 33 -->

QB50 Mission                                                                                   33




2 QB50 Mission

2.1. QB50 project description
QB50 space mission has the scientific objective to study in situ the temporal and spatial variations
of a number of key constituents and parameters in the lower thermosphere (90‐350 km) with a
network of about 40 double CubeSats, carrying identical sensors for in-situ measurements and
about 10 triple CubeSats. QB50 will also study the re‐entry process by measuring a number of key
parameters during reentry, and by comparing predicted and actual CubeSat trajectories.
Space agencies and companies are not pursuing a multi-spacecraft network for in-situ
measurements in the lower thermosphere because the cost of a network of 50 satellites built to
industrial standards would be extremely high and not justifiable in view of the limited orbital
lifetime. No atmospheric network mission for in-situ measurements has been carried out in the past
or is planned for the future. A network of satellites for in-situ measurements in the lower
thermosphere can only be realized by using very low-cost satellites, and CubeSats are the only
realistic option. This atmosphere portion is the least explored layer; in past explorations were done
with highly elliptical orbits only for few minutes. With QB50 project it is possible to extend the
measuring time to some months and have finally detailed results on the troposphere.
The hardware cost of a CubeSat is normally in the range 50-100 k€ but can go up to 500 k€ for
more sophisticated payloads. Up to now, about 50 CubeSats have been successfully launched, and
an estimated 100-150 CubeSats are being planned for launch in the next few years.
A single CubeSat is simply too small to also carry sensors for significant scientific research. Hence,
for the universities the main objective of developing, launching and operating a CubeSat is
educational. However, when combining a large number of CubeSats with identical sensors into a
network, fundamental scientific questions, otherwise inaccessible, can be addressed in addition to
the educational value of the space mission in an inexpensive way. Networks of CubeSats have been
under discussion in the CubeSat community for several years, but so far no university, institution or
space agency has taken the initiative to set up and coordinate such a powerful network. CubeSat
reliability is not a major concern because the network can still fully achieve its mission objectives
even if a few CubeSats fail.
The QB50 project is partially supported by the European Community Framework Programme 7,
and satellites come from more than twenty European countries, as well as from the US, Canada and
others countries. The figure below shows the large number of participants involved in the project.

<!-- PDF_PAGE: 34 -->

34                                                                                                QB50 Mission




                 Figure 2.1: Map with the number of partners worldwide for the QB50 project [4]




Since the beginning, interest to participate in QB50 has been expressed by over 90 universities all
over the world. This includes universities in 30 European countries and universities in Argentina,
Australia, Brazil, Canada, Chile, China, Ethiopia, India, Israel, Peru, Puerto Rico, Russia,
Singapore, South Korea, Taiwan, Turkey, Ukraine, USA and Vietnam. For many of these
countries, the CubeSats that will participate in QB50 will be their first satellites in orbit and a
matter of national prestige. QB50 involves well over 1000 people from all over the world: 50
CubeSat teams of 10-20 students and engineers, numerous atmospheric scientists, instrument,
orbital dynamics and ground station experts, legal experts, as well as industry and space agency
representatives.
Von Karman Institute (VKI) has been working at this project for about few years and it has a great
knowledge of the mission details. This institute has also high experience in space technology. In
past years it was involved in a lot of space programs of ESA. Especially investigations of classical
problems for the development of hypersonic vehicles continue to be a strong activity at VKI.
Moreover, a considerable effort has been devoted to experimental and numerical studies aimed at
the development of atmospheric-entry flight experiments. Based on these works, recently, VKI has
developed also three experimental payloads for the EXPERT program of ESA.
The QB50 Project is mainly carried out by a Consortium of 14 institutes/industries led by the von
Karman Institute for Fluid Dynamics, but the complete number of involved institutes is huge.
For the QB50 atmospheric research network, 40 double-unit CubeSats are foreseen, with one unit
(the functional unit) providing the usual satellite functions and the other unit (the science unit)
accommodating a set of sensors for lower thermosphere and reentry research. The functional unit
provides the usual satellite functions, like power, Central Power Unit (CPU), telecommunication,
Inertial Measurements Unit (IMU) and Global Positioning System (GPS). The universities and
other partners are free to design the functional unit, CubeSat teams are free to use any space left in
this unit of the double CubeSat for a technology package or a sensor of their own choice. The
selection of the standardized sensors for in-situ measurements will be managed by the Sensor
Selection Working Group (SSWG) of the mission.

<!-- PDF_PAGE: 35 -->

QB50 Mission                                                                                 35



In addition to the division about sensor selection, there are other operating groups. The Orbital
Dynamics Working Group (ODWG) is responsible for advising at the selection of the initial orbital
altitude and the deployment sequence to ensure an initial separation between CubeSats in the
network. Science Payload Working Group (SPWG) has the task to focus on the sensors
recommended by the SSWG in detail. This includes detailed accommodation studies of the sensors
in the science unit and recommendations regarding the interface specifications. Finally there is the
Ground Station Network and Frequency Allocation Working Group (GFWG), which has mainly
the task to advise the Project Team at VKI on the selection of the frequency band (probably
UHF/VHF), the most appropriate modulation schemes and the data rates for the downlinks and
command uplinks, and give assistance for all communications problems.

Regarding the QB50 mission, the 50 satellites will be launched together on a single launch vehicle.
Due to atmospheric drag, it is predicted the orbits will decay from 350 km to 90 km in around 3
months, this is the minimal duration required to performed suitable in-situ measurements. After
launch the CubeSats will be deployed sequentially. The separation speed will have a great
influence on the total network size.
QB50 has been selected as the first large-scale CubeSat network in orbit because a network of
CubeSats in the lower thermosphere has many advantages in comparison with networks in higher
orbits. The lifetime of a CubeSat in the envisaged low-Earth orbit will only be three months, i.e.
much less than the time stipulated by international requirements related to space debris. A low-
Earth orbit allows high data rates because of the short communication distances involved.
Moreover, in low-Earth orbits, the CubeSats will be below the Earth’s radiation belts. This last
feature is advantageous because CubeSats can use low-cost Commercial-Off-The-Shelf (COTS)
components which are not radiation hardened.
The orbit of the International Space Station (ISS) is currently maintained between 388 km (perigee)
and 401 km (apogee). If a network of many CubeSats is launched into an orbit that is above that of
the ISS there is a danger of collision with the ISS when the orbits of the CubeSats decay due to
atmospheric drag. If the initial orbit of the CubeSats is below ISS there is no relevant danger of
collision.
For a network of CubeSats in the lower thermosphere the short mission lifetime is not a deterrent.
Indeed, from the point of view of a university, the primary purpose of a CubeSat is educational, and
educational objectives can be achieved even if the orbital lifetime is short.




2.2. The lower thermosphere research
The main objective of QB50 mission is the study of the atmosphere and in particular the
thermosphere, which is heavily undersampled compared to others layers.
The Earth's atmosphere is a thin layer of gases that surrounds the Earth. It is composed of 78%
nitrogen, 21% oxygen, 0.9% argon, 0.03% carbon dioxide and trace amounts of other gases.
Probably the present atmosphere of the Earth is not the original atmosphere. Our current
atmosphere is what chemists would call an oxidizing atmosphere, while the original atmosphere
was what chemists would call a reducing atmosphere. In particular, it probably did not contain
oxygen. The original atmosphere may have been similar to the composition of the solar nebula and
close to the present composition of the Gas Giant planets. Earth is the only planet in the solar
system with an atmosphere that can sustain life. The blanket of gases not only contains the air that
we breathe but also protects us from the blasts of heat and radiation emanating from the Sun. It
warms the planet by day and cools it at night.
The atmosphere protects life on Earth by warming the surface through heat retention, reducing
temperature extremes between day and night, and filtering the electromagnetic radiations of the

<!-- PDF_PAGE: 36 -->

36                                                                                   QB50 Mission



Sun. Over the past century, greenhouse gases and other air pollutants released into the atmosphere
have been causing big changes like global warming, ozone holes and acid rain. The absorption of
the radiations causes local heating, which contributes to the atmospheric structure. Atmospheric
stratification describes the structure of the atmosphere, dividing it into distinct layers, each with
specific characteristics such as temperature or composition. The atmosphere has a mass of about
5×1018 kg, three quarters of which are within about 11 km from the surface.
The atmosphere becomes thinner with increasing altitude, with no definite boundary between the
atmosphere and outer space. In general, air pressure and density decrease in the atmosphere as
height increases. However, temperature has a more complicated profile with altitude, but it
provides a useful metric to distinguish between atmospheric layers.




Earth's atmosphere can be divided into five main layers. From the highest to the lowest, these
layers are:

        Exosphere

         The exosphere is the outermost layer of Earth's atmosphere. It is mainly composed of
         hydrogen and helium. The particles are so far apart that they can travel hundreds of
         kilometers without colliding with each other. Since the particles rarely collide, the
         atmosphere no longer behaves like a fluid. These free-moving particles follow ballistic
         trajectories and may migrate into and out of the magnetosphere or the solar wind. This is
         the area where many satellites orbit the Earth.


        Thermosphere

         The thermosphere starts just above the mesosphere and extends up to 600 km high.
         Literally, thermosphere means “heat sphere”. In this layer the temperature rises continually
         with height to well beyond 1500°C. The few molecules that are present in the
         thermosphere receive extraordinary amounts of energy from the Sun, causing the layer to
         warm to such high temperatures. Within this layer, ultraviolet radiation causes ionization.

        Mesosphere

         The mesosphere extends from the end of stratosphere to 80–85 km. It is the layer where
         most meteors burn up upon entering the atmosphere. Temperature decreases with height in
         the mesosphere. The temperature minimum that marks the top of the mesosphere is the
         coldest place on Earth and has an average temperature around −85 °C. Due to the cold
         temperature of the mesosphere, water vapor is frozen, forming ice clouds.


        Stratosphere

         The stratosphere extends from the troposphere to about 50-55 km. Temperature increases
         with height due to increased absorption of ultraviolet radiation by the ozone layer, which
         restricts turbulence and mixing. While the highest temperature may be −60 °C at the
         troposphere, the top of the stratosphere is much warmer, and may be near freezing.

<!-- PDF_PAGE: 37 -->

QB50 Mission                                                                                    37



       Troposphere

        The troposphere begins at the Earth’s surface and extends to between 9 km at the poles and
        17 km at the equator. This layer is mostly heated by transfer of energy from the surface, so
        that on average the lowest part of the troposphere is warmest and temperature decreases
        with altitude. The troposphere contains roughly 80% of the mass of the atmosphere, and it
        is where most weather phenomena like cloud formation take place.




                             Figure 2.2: Vertical structure of the atmosphere [5]




The lower thermosphere (90‐350 km) is the least explored layer of the atmosphere. The first
explorations of this layer were done with highly elliptical orbits, but the spent time in this region
was only a few tens of minutes.
NASA has launched 92 Explorer satellites in past years, 10 of which made in‐situ measurements in
the lower thermosphere. Since the lifetime of a satellite in the lower thermosphere in a circular
orbit is relatively short due to atmospheric drag all past satellites were in highly elliptical orbits.
These orbits, however, have the disadvantage that the time spent during each orbit in the lower
thermosphere is only around 10 minutes out of an orbital period of around 2 hours. In the 1960s,
NASA also launched four spheres, each 3.65 m in diameter, to determine the air density at orbital
altitude by tracking the orbits of the spheres from the ground. They were all launched into similar
orbits with perigees around 600 km and apogees around 2500 km. The decay of their orbits due to
atmospheric drag was tracked until they burnt up in the atmosphere at around 100 km altitude.
Nowadays, sounding rocket flights provide the only in-situ measurements, but the time spent in this
region is rather short. Earth observation satellites, which are equipped with powerful remote-
sensing instruments, can fly in higher orbits (600‐800 km). Although this is an excellent tool for
exploring the lower layers, they only observe constituents in the troposphere, the stratosphere and
the mesosphere, due to the thermosphere is so rarefied and the return signal is weak. The same

<!-- PDF_PAGE: 38 -->

38                                                                                       QB50 Mission



happens for remote-sensing observations from the ground with lidars and radars. With this
explanation it is easy to understand why the atmospheric density models do not agree with each
other. Some of these models are based on theoretical assumptions concerning key parameters like
the exospheric temperature, whereas other models are based on in-situ data measurements. The
multi-point in-situ measurements of QB50 mission will be complementary to observations by the
instruments on Earth observation satellites, and observations from the ground with lidars and
radars. QB50 will allow the increase of knowledge of the lower thermosphere and the dynamic
phenomena that take place. All atmospheric models surely will benefit from the measurements
obtained by this mission.




2.3. The re-entry phase research
The atmosphere surrounding Earth protects and supports life on the planet, but it also makes space
flight more difficult. All of the energy expended to get to orbit dissipates on the way back to Earth,
usually in the form of extreme heating. In addition to the aerodynamic concerns of high-speed
flight, there are serious thermodynamic issues.
Atmospheric reentry is without a doubt the most challenging phase of spaceflight and QB50
mission offers the occasion to study also the reentry process. The CubeSats, orbiting into a LEO at
about 350 km, will go down due to the atmospheric drag and they will be able to transmit
information during the reentry phase before being disintegrated in the atmosphere.
There are two types of reentry which determine the design of vehicles for hypersonic reentry into
the earth’s atmosphere from space. The first one, and also the QB50 one, is the ballistic reentry.
The spacecraft just drops into the atmosphere and uses only drag for slowing down. The retarding
force is always opposed to the line of flight. The primary design parameter for ballistic entry is the
ballistic coefficient ,




where W is the vehicle weight,        is the drag coefficient, and A is the reference area used in the
definition of the drag coefficient. The ballistic coefficient is the single most important parameter
in controlling flight trajectory during entry. This coeﬃcient signiﬁcantly aﬀects the nature of the
reentry proﬁle, in terms of heating and trajectory. Deceleration and heating are less intense for a
low value (low weight and/or high drag and large frontal area) than for a high value (high
weight and/or low drag and small frontal area) since the entry occurs at a high altitude in the
atmosphere where the air is less dense. Primarily the ballistic coefficient of a body is a measure of
its ability to overcome air resistance in flight. Satellites in Low Earth Orbit (LEO) with high
ballistic coefficients experience smaller perturbations to their orbits due to atmospheric drag. The
ballistic coefficient of an atmospheric reentry vehicle has a significant effect on its behavior. A
vehicle with very high ballistic coefficient would lose velocity very slowly and would impact the
Earth's surface at higher speeds. In contrast a vehicle with low ballistic coefficient would reach
subsonic speeds before reaching the ground. In general, reentry vehicles that carry human beings
back to Earth from space have high drag and a correspondingly low ballistic coefficient. Other
vehicles that carry nuclear weapons launched by an Intercontinental Ballistic Missile (ICBM), by
contrast, have a high ballistic coefficient, which enables them to travel rapidly from space to a
target on land. That makes the weapon less affected by crosswinds or other weather phenomena,
and harder to track, intercept, or otherwise defend against.
The second reentry type is the lifting entry in which the primary force being generated is
perpendicular to the flight path, that is, a "lift" force. Although drag is present throughout the entry,

<!-- PDF_PAGE: 39 -->

QB50 Mission                                                                                     39



the resulting flight path can be adjusted continuously to change both vertical motion and flight
direction while the velocity is slowing. The primary design parameter for lifting entry is the Lift to
Drag Ratio, or L/D,

                                              =       =

Low values of L/D produce moderate g loads, moderate heating levels, and low maneuverability.
High values of L/D produce very low g loads, but entries are of very long duration and have
continuous heating.
A more unusual reentry option that merges features of both ballistic and gliding profiles is the skip
entry trajectory. In this case, the vehicle first grazes the outer fringes of the atmosphere and
generates drag that slows the craft down by a small amount. However, the vehicle also generates a
lift-to-drag ratio between 1 and 4 and uses this lift to pitch up and leave the atmosphere again. This
process is repeated several times as the craft skips along the upper reaches of the atmosphere much
like a stone skipping across the surface of a lake. This skipping gradually slows the vehicle until it
can safely re-enter the atmosphere and fly a more ballistic path to touchdown (e.g. IXV, Space
Shuttle).




2.3.1. QARMAN CubeSat
The von Karman Institute (VKI) has the intention to provide a triple QB50 CubeSat with the
purpose of performing an atmospheric reentry flight. This CubeSat is named QARMAN (Qubesat
for Aerothermodynamic Research and Measurement on AblatioN) and it will be used to carry out
measurements during the reentry phase. The VKI CubeSat will be equipped with a special thermal
protection system (TPS) to increase the satellite operative life. This is a triple unit CubeSat with a
new generation low density/high porosity carbon fiber perform ablative TPS with phenolic resin.
QARMAN will fly with QB50 network and will be placed in an Earth orbit at altitude of 350 km.
After almost 3 months lifetime, it will perform an atmospheric entry with velocity of 7.5 km/s
starting at 120 km of altitude. The major scientific return of the project is the contribution of real
ﬂight data on an Earth reentry trajectory by a very low cost mission compared to other similar
missions and validation of the prediction and testing tools. The in-flight experiments on board
consist of aerothermodynamic research on the ablative TPS as well as hypersonic flight dynamics.
Moreover, a passive aerodynamic drag control device is used for attitude stability and control. The
platform development and the in-flight experiment design will be mainly performed at VKI with
the help of the Plasmatron facility and other vacuum chambers. Furthermore, an inertial
measurements unit will be utilized to perform measurements on the flight trajectory of the CubeSat.
Finally, if adequate remaining power and data resources are available, it is envisaged to carry
additional sensors for skin friction and pressure sensors for base flow measurements. QARMAN
represents an ideal cost-efficient platform for reentry flight test and validation of thermal protection
system materials. The CubeSat comprises a standard double-unit platform with sensors for
atmospheric research and a functional unit for essential satellite operations. A third unit
accommodating an ablative heat shield is added to protect the vehicle against the extreme
aerothermal conditions of reentry. The preliminary design of the vehicle results in a payload
collecting data all along the reentry trajectory including the maximal heat flux conditions. The
differences between the proposed reentry CubeSat platform and the other QB50 CubeSats consist
in the necessity of a deorbiting system and an extra unit for the thermal protection system with
regard to the reentry constrains. The extra unit is mandatory for the thermal protection system and
permits to increase the survivability of the vehicle up to the expected end of life altitude of 50 km.

<!-- PDF_PAGE: 40 -->

40                                                                                  QB50 Mission



It has to be noted that no other CubeSats of the QB50 program is expected to survive below 90 km
with the two unit configuration. As opposed to conventional reentry vehicles, the standard form
factor is a challenge and the design approach avoids the typical reentry vehicle shapes optimized
for stability and aerothermodynamics constrains. Moreover, it is mandatory to concede the need of
the vehicle’s destruction before it reaches the ground for safety reason. As primary objective
QARMAN should reach the expected end of life altitude (50-70 km), where measurements
performed at the critical points of the trajectory can be achieved, which are the maximum heat flux
point, the maximum dynamic pressure point and the telecommunication blackout phase. The choice
and feasibility of the telecommunication system has also to be considered to be able to transmit the
measured data before the vehicle loses its functionality. Eventually it is mandatory to consider the
need of the vehicle’s destruction before it reaches the ground, thus avoiding any problem of
collision with ground assets.
The project strong point is the low cost of the reentry spacecraft that generally permits huge
opportunities for independent research institutions like VKI with QARMAN.




                                Figure 2.3: VKI’s QARMAN CubeSat [6]




                               Figure 2.4: QARMAN scenario time line [6]

<!-- PDF_PAGE: 41 -->

QB50 Mission                                                                                    41




2.4. Launch and deployment phases
The 50 double CubeSats participating in QB50 will be launched probably by Cyclone-4 launcher.
The Cyclone-4 Launch Vehicle is the newest and most powerful version of the Cyclone family of
launchers developed by Yuzhnoye State Design Office and produced by Production Association
Yuzhny Machine-Building Plant, both Ukrainian companies. Since they became operational in
1969, the Cyclones were widely used for delivery of various spacecraft into orbit, mainly for the
USSR and Russian space programs, as well as for some international programs.
A good strong point for QB50 mission is surely the possibility to put all CubeSats inside the
launcher as primary, secondary or also tertiary payload. That optimizes launcher capability and
permits to have a lower cost, that can decrease very much. A few weeks before launch, the
deployment system with the 50 CubeSats inside is mounted on top of the launcher. The deployment
system will be accommodated inside Cyclone 4-upper Stage, inside the payload unit. The payload
unit is an individual assembly unit designed for launch vehicle and spacecraft integration, and
ensuring the required environments at all the payload unit and launch vehicle operation phases. The
payload unit includes a payload fairing, spacecraft, spacecraft adapter (or dispenser, if it is a
multiple injection), and a payload unit adapter. The payload unit is part of the Cyclone 4- Upper
Stage (3rd Stage). During the payload unit integration, the spacecraft is encapsulated under the
payload fairing and payload unit adapter (with an isolating membrane).




                  Figure 2.5: Cyclon-4 Launcher (on the right) with predecessor launchers [7]


Typically, CubeSats are launched from Picosatellite Orbital Deployers (PODs). These systems are
stand-alone items that are integrated onto the launch vehicle one-by-one. This concept offers
flexibility and freedom for the launch service provider about where to place the PODs. Integration
of 50 double and triple CubeSats is very challenging, both technically and operationally. It is

<!-- PDF_PAGE: 42 -->

42                                                                                               QB50 Mission



assumed that the CubeSats are not all deployed at once, that they are deployed radially away from
the upper stage rather than in the direction of flight, and that the deployment speed is in the range
1–3 m/s. During next months, these assumptions will be further elaborated and specified by the
QB50 Orbital Dynamics Working Group (ODWG). The interface between the deployment system
and the upper stage of the rocket transfers the loads from the launch vehicle to the integrated
payload structure. The launcher interface provides the means to partly absorb these loads without
transfer of the peak loads to the satellites: for instance by absorbing such loads using shock
damping systems. The innovative concept of StackPack consists of a collection of dispenser
modules that is able to accommodate and deploy the whole set of QB50 CubeSats. Figures 2.6 and
2.7 show positions and possible configurations for one of the possible StackPack concepts [8].




                     Figure 2.6: Accommodations and StackPack configuration examples [8]




              Figure 2.7: Example of accommodation inside cyclone upper stage (isometric view) [8]

<!-- PDF_PAGE: 43 -->

QB50 Mission                                                                                              43



The StackPack provides the interface between QB50 CubeSats and the Launch Vehicle. It is a
custom integrated platform that is optimized in terms of mass, volume and connectivity.
Requirements and constrains related with CubeSats, Launch Vehicle, operations and environment
have been taken into account in the StackPack design. The QB50 project involves two different
CubeSat types, the 3U CubeSat types, the 3U CubeSats for technology demonstration and the 2U
CubeSats for atmospheric research. The StackPack has to accommodate both 2U and 3U CubeSats.
After deployment CubeSats, as it is shown in Figure 2.8, tend to align up in orbit ordered according
to the ballistic coefficient, with the lightest CubeSat in front. Therefore it is favorable to deploy the
CubeSats directly ordered according to this coefficient to reduce the risk of collision when one
satellite “overtakes” another. The CubeSats have reached a good distribution in the orbital plane
after one month, which is shown in Figure 2.9. The CubeSats cover all latitudes with the potential
to take measurements in the night and day-side of the Earth simultaneously.




            Figure 2.8: Distribution of CubeSats for deployment with random BC order after 20 days [12]




                             Figure 2.9: Distribution for 1 month after deployment [12]

<!-- PDF_PAGE: 44 -->

44                                                                                     QB50 Mission




2.5. Mission orbital mechanics
All 50 CubeSats will be launched together from a single launch vehicle into a circular orbit at 350
km altitude and with an inclination higher than 75°. Due to atmospheric drag, the orbits of the
CubeSats will decay and progressively lower and lower layers of the thermosphere will be explored
without the need for on-board propulsion, perhaps down to 90 km. If mass of the final system to be
launched is significantly reduced, this may result in a slight increase of the orbital altitude but not
above 388 km, the lowest perigee of the ISS, thereby extending the lifetime of the mission. The
initial total network size in orbit is determined by the deployment sequence and the separation
speed and direction. The initial distances between individual CubeSats in the network will be
between a few tens and a few hundred kilometers. Orbital modeling has shown that, due to air
density variations along the orbit and small differences in the CubeSat ballistic (or drag)
coefficients, the separation distance will change, eventually, after about a month, leading to a non-
uniform distribution of CubeSats all the way around the Earth. In this way, the CubeSats will be
able to explore temporal and spatial variations over a wide range of scale sizes, from a few tens of
kilometers in the beginning to about 1000 km after a month.

Since the orbit is circular, there are some elements that are common for all circular orbits. The
altitude of apogee and perigee is the same. Eccentricity, the element used to describe elongation in
an elliptical orbit, is 0. Otherwise argument of perigee, RAAN and true anomaly are still undefined.
Taking into account all these aspects, Table 2.1 summarizes the orbital parameters:


                                   Table 2.1: Orbital parameters of QB50

                         Type                                              LEO

                         Altitude of apogee/perigee                        350 km

                         Eccentricity                                      0°

                         Inclination                                       > 75°

                         Argument of perigee                               TBD

                         RAAN                                              TBD

                         True anomaly                                      TBD




The evolution of the altitude of a typical CubeSat is shown in Figure 2.10 for the duration of the
mission. The satellite will stay above the altitude of 250 km for most of the time, before it will lose
quickly the altitude during the end of the mission due to the increasing drag forces.

<!-- PDF_PAGE: 45 -->

QB50 Mission                                                                                                   45




                                                                                                        For Educational Use




            Figure 2.10: Altitude as a function of mission time for a QB50 CubeSat, obtained with STK




The velocity as a function of lifetime is shown in Figure 2.11. With decreasing altitude the velocity
will increase. However the higher velocity has only a small effect on the ground station contact
time compared with the direct influence of the altitude on the arc length.


                                                                                                        For Educational Use




            Figure 2.11: Velocity as a function of mission time for a QB50 CubeSat, obtained with STK

<!-- PDF_PAGE: 46 -->

46                                                                                  QB50 Mission




2.6. Mission Control Centres
The idea is to set up parallel mission display centres at VKI, Stanford in the US and NPU in China
with real-time functions for all 50 CubeSats. These centres will compare predicted trajectories with
the actual ones, using different trajectory simulation software tools, atmospheric models and
CubeSat drag coefficients. They will monitor the status and health of the 50 CubeSats and the
deployment system, and for instance they will display which ground station is in contact with
which CubeSat while displaying the link quality. A further function would be the prediction and
update of the approximate time and latitude/longitude of atmospheric reentry for the 50 CubeSats.
Another fundamental centre will be the Belgian User Support and Operation Centre (B-USOC).
This is a service centre of the Belgian Science Policy (BELSPO)/R&D division. The main role of
the centre is to promote space research programs and flight opportunities to the Belgian scientific
community at universities, federal and regional institutes as well as to industry. The B-USOC, like
each USOC, is part of the Ground Segment for the ISS and it is connected to the Manned
Spaceflight and Microgravity Ground Segment. For this project and due to its experience, it is
foreseen that the B-USOC will be the Data Processing and Archiving Centre (DPAC).

The QB50 DPAC will have the following tasks:

          Serving as the single point of contact between the QB50 Project and the CubeSat teams
           regarding science and housekeeping data;
          Verification and cataloging of the data submitted to DPAC by the CubeSat teams;
          Support of the CubeSat teams in producing the necessary documentation describing their
           data set;
          Transfer of the data files into an uniform, user-friendly format;
          Handling the requests for data by the user community and providing clarifications to the
           user community if requested;
          Archiving of all data and documentation.




2.7. Requirements for CubeSats, technical specifications
QB50 CubeSats have requirements and technical specifications that are provided in the
Interface Control Document (ICD). The ICD controls the interface to the QB50 deployment
system and provides the guidelines for CubeSat development.

Main guiding principles are:

         Compatibility with the CubeSat Standard
         Science sensors specifications
         Science sensor accommodation, electronics
          Lifetime requirements
          Attitude Determination and Control Subsystem (ADCS)
          Electrical Power Subsystem (EPS)
          Telemetry, Tracking and Command (TT&C) subsystem

<!-- PDF_PAGE: 47 -->

QB50 Mission                                                                                 47



        On-Board Data Handling (OBDH)
        Thermal control
        Environmental testing
        Model philosophy
        Interface to the deployment system
        Payload environmental requirements

In the course of the project, the ICD will be frequently updated as soon as new technical or
interface information becomes available, in particular concerning the deployment system and the
launch vehicle.




2.8. QB50 Communication challenge
The CubeSat baseline regarding the communication system is the use of a UHF/VHF system.
Current systems promise a data transmission rate of up to 9.6 kbps which is rather low compared to
the faster S-Band systems. However S-Band is not recommended by the Ground Station Network
and Frequency Allocation Working Group (GFWG) due to the limited power budget on the
CubeSat and the requirements on antenna pointing [Orbital Dynamics of QB50 CubeSats, T.
Scholz, 2012].
The currently expected amount of data produced by the Sensor-Unit is 2 Mb per day, and
additional 2 Mb housekeeping and science data from the CubeSat teams is assumed. Therefore the
communication system should be capable of transmitting 4Mb data down to Earth per day.
An analysis for the prediction of the amount of transmitted data for one pass of a CubeSat over a
ground station will be presented in the following chapters in order to calculate the number of
necessary contacts per day.
It will be discussed also the possibility of implementing ground stations with a rotator mechanism,
in order to improve the ground segment beamwidth ability and to lock onto the receiving signal
better and longer.
Due to obstacles around the ground station and the longer signal travel distance through the
atmosphere, the first contact is established when the satellite is at a suitable elevation over the
horizon. Minimum elevation angles should be quite large to guarantee a satisfactory access. The
elevation angle problem will be discussed deeply in next chapters. It turns out to be a relevant
problem due to numerous obstacles present around the academic ground stations, that usually are
located in universities or places prone to be affected by a lot of obstacles like buildings or other
obstructing objects.
The communication analysis represents an interesting challenge, full of numerous parameters and
factors to be optimized. In the following chapters the communication problem will be analyzed, in
order to understand and find the benefit solution to satisfy all mission requirements and guarantee
the optimal number and time of access.

<!-- PDF_PAGE: 48 -->

48                                                                   Communication Challenge




3 Communication Challenge

3.1. Communication role
Communication is a key component in our world. Almost everything that is done in the world
today involves some form of communication. All communication methods require some kind of
medium to relay the communication data. These media could be for instance telephone lines, fiber
optic connections, or wireless radio frequency (RF) transmissions. Each method comes with its
strengths and weaknesses. A wired link can be operated at high data rates, thus providing large
amounts of data quickly. However, these links must be physically connected with wires or optical
cables. Such a constraint limits the distance that links of this nature can cover. Alternatively, RF
transmissions can cover large distances at much lower costs due to the absence of physical
connections between stations. However, they typically suffer the disadvantage of lower data rates.
Usually if the transmission distance is small, the components for an RF link can remain small.
Larger distances quickly increase the size, complexity and power consumption of RF links. One
common method for obtaining quality communication links over large coverage areas has been
through the use of satellite RF transmissions by relaying the signal. The altitude of satellite
transmissions provides an ideal advantage in RF communications by limiting the propagation loss
that occurs from buildings, trees and mountains. These obstacles do not severely affect RF
transmissions coming from an overhead satellite however there are other drawbacks to be
considered. Advances in space technology have made the placement of such satellite systems
achievable for many organizations. Because of this advantage, a great deal of research and
development has gone into building high-speed communication links for satellite RF transmissions.
Satellites can cover larger areas, but large satellite RF communication links are neither small nor
cheap. The development of such systems takes several years, and their cost typically ranges in the
millions of dollars to build and deploy. However, following typical technology trends, satellite
systems are getting smaller with time.
In 2003, the first set of CubeSats were deployed into space. Typical communication links to
CubeSat systems are in the baud to kilo baud range (9.6 kbps for UHF systems). Such connection
speeds are extremely slow compared to modern computer networking speeds. With the growing
number of possible payloads, and interested parties, the data transfer rate of these satellites is a
growing concern. CubeSat costs are very low in comparison with larger satellites and this is a huge
point of strength of small satellite concept.
Until now the small size and low power of a CubeSat has made a high data rate transmitter
impractical. However, using a network of CubeSats like in QB50 mission, it is possible to reach
very interesting achievements, exploiting large number of satellites involved respect to the high
technology of each one. A good understanding of the orbit characteristics is one of the most
relevant matters in communication and especially the position knowledge is fundamental. The
geometric problem has to be handled carefully in order to optimize all possible factors.

<!-- PDF_PAGE: 49 -->

Communication Challenge                                                                                          49




3.2. Earth geometry viewed from space
In communication it is mandatory to have an excellent knowledge of Earth geometry viewed from
satellites. The most common problem in space mission is to determine the relative geometry of
objects on the Earth's surface as seen from the spacecraft. Another issue is to determine the
intercept point on the surface of the Earth corresponding to a given direction in spacecraft
coordinates. To begin, we determine ρ, the angular radius of the spherical Earth as seen from the
spacecraft, and λ0, the angular radius measured at the center of the Earth of the region seen by the
spacecraft (see Fig. 3.1). Assuming a spherical Earth, the line from the spacecraft to the Earth's
horizon is perpendicular to the Earth's radius, and therefore

                                                 ρ        λ

and

                                                     ρ   λ         °

where       is the radius of the Earth and H is the altitude of the satellite.




      Figure 3.1: Relationship between geometry as viewed from the spacecraft and from the center of the Earth [13]




Thus, the Earth forms a small circle with an angle on the spacecraft sky, and the spacecraft sees
the area within a small circle with an angle λ0 on the surface of the Earth. The distance, Dmax to the
horizon is given by:

<!-- PDF_PAGE: 50 -->

50                                                                                  Communication Challenge




            Figure 3.2: Definition of angular relationships between satellite, target and Earth center [13]




The spherical-Earth approximation is adequate for most mission geometry applications. However,
for precise work, we must apply a correction for oblateness. Computationally, by STK for example,
it is possible to treat oblateness and surface irregularities as simply the target's altitude above or
below a purely spherical Earth. That the Earth's real surface is both irregular and oblate is
immaterial to the computation, therefore the results are exact.
An interesting investigation consists in looking for the angular relationships between a target, P, on
the surface of the Earth, and a spacecraft with subsatellite point, SSP, also on the surface of the
Earth. Assuming that the subsatellite point’s latitude, LatSSP and longitude LongSSP, are known, and
given the coordinates of a direction of a target on the Earth, it is not difficult to find its coordinates
viewed by the spacecraft. Furthermore, given the coordinates of a direction relative to the
spacecraft, it is also simple to find the coordinates of the intercept on the surface of the Earth.
Generally the main geometric problem is to find the relationship between the nadir angle, η,
measured at the spacecraft from the subsatellite point to the target; the Earth central angle, λ,
measured at the center of the Earth from the subsatellite point to the target; and the spacecraft
elevation angle, ε, measured at the target between the spacecraft direction and the local horizontal.
The first step consists in finding the angular radius of the Earth, ρ. Next, if λ is known, it is possible
to evaluate η from

                                                               ρ       λ
                                                 η
                                                                   ρ       λ


If η is known, it is possible to find ε from

                                                                   η
                                                         ε
                                                                   ρ

Or, if ε is known, we find η from

                                                     η         ε       ρ

<!-- PDF_PAGE: 51 -->

Communication Challenge                                                                                   51



Finally, the remaining angle and side are obtained from

                                              η      λ     ε

                                                               λ        η .

So far we have considered spacecraft geometry only from the point of view of a spacecraft fixed
over one point on the Earth. However, the spacecraft is traveling at high velocity.
Figure 3.3 shows a QB50 CubeSat path of the subsatellite point over the Earth's surface, called the
satellite's ground track. Because of the Earth's rotation, the spacecraft moves over the Earth's
surface in a spiral pattern with a displacement at successive equator crossings directly proportional
to the orbit period. For a satellite in a circular orbit at inclination i, the subsatellite latitude, δs, and
longitude, Ls, relative to the ascending node are




where t is the time since the satellite crossed the equator northbound,       = 0.00417807 deg/s is the
angular velocity of Earth’s rotation around its axis, and is the satellite's angular velocity. For a
satellite in a circular orbit, , measured in deg/s is related to the period, P, measured in minutes by



where 0.071 deg/s is the maximum angular velocity of a spacecraft in a circular orbit.
Similarly, the ground track velocity, Vg, is




where                    is the equatorial radius of the Earth.




                                                  For Educational Use




      Figure 3.3: Example of QB50 CubeSat Ground Track (green line), i=98 deg, h=350 km, obtained with STK.

<!-- PDF_PAGE: 52 -->

52                                                                                 Communication Challenge




3.3. Satellite apparent motion with respect to Earth
For satellites in perfectly circular orbits, the apparent motion of a satellite across the sky for an
observer on the Earth's surface is not a simple geometrical figure. If the observer is in the orbit
plane, then the apparent path of the satellite will be a great circle going directly overhead. If the
observer is somewhat outside of the orbit plane, then the instantaneous orbit will be a large circle in
three-dimensional space viewed from somewhat outside the plane of the circle and projected onto
the observer's celestial sphere.
Since the apparent satellite path is not a simple geometrical figure, due to the non-homogeneous
Earth radius, it is best computed using a simulation program like Satellite Tool Kit (STK).
We assume a satellite is in a circular low-Earth orbit passing near a target-or ground station and
that the orbit is low enough that we can ignore the Earth's rotation in the relatively brief period for
which the satellite passes overhead. We wish to determine the characteristics of the apparent
satellite motion as seen from the ground station. The small circle in Figure 3.4, centered on the
ground station, contains the subsatellite points at which the spacecraft elevation, ε, seen by the
ground station is greater than some minimum εmin. The nature of the communication or observation
will determine the value of εmin. The size of this circle of accessibility strongly depends on the
value of εmin. The dashed circle in the figure surrounding the ground station is at εmin = 0 deg (that
is, the satellite's true outer horizon), and the solid circle corresponds to a possible εmin assumed to
be 5 deg. Many of the computed parameters will be extremely sensitive to the minimum elevation
angle.




          Figure 3.4: Geometry of satellite ground track relative to an observer on the Earth’s surface [13]




Given a value of εmin it is possible to define the maximum Earth central angle, λmax, the maximum
nadir angle, ηmax, measured at the satellite from nadir to the ground station, and the maximum
range, Dmax, at which the satellite will still be in view. These parameters are given by:

<!-- PDF_PAGE: 53 -->

Communication Challenge                                                                           53




where is the angular radius of the Earth as seen from the satellite. We call the small circle of
radius       centered on the target the effective horizon, corresponding in our example to        = 5°,
to distinguish it from the true or geometrical horizon for which                = 0°. Whenever the
subsatellite point lies within the effective horizon around the target or ground station, then
communications or observations are possible. The duration, T, of this contact and the maximum
elevation angle,       , of the satellite depend on how close the ground station is to the satellite’s
ground track on any given orbit pass.
Because of this orbit rotation relative to the Earth, it is convenient to know also the instantaneous
ascending node, which is Lnode evaluated at the time of an observation or passage over a ground
station. For purposes of geometry it is also often appropriate to work in terms of the instantaneous
orbit pole, or the pole of the orbit plane at the time of the observation. The coordinates of this pole
are




The satellite passes directly over a target or ground station on the Earth's surface if and only if



There are two valid solutions to the above equation corresponding to the satellite passing over the
ground station, either on the northbound leg of the orbit or on the southbound leg. For a circular
orbit, in order to determine the time of the satellite pass over the ground station, after crossing the
equator, we can determine μ, the arc length along the instantaneous ground track from the
ascending node to the ground station, using

                                           μ

Again, the two valid solutions correspond to the northbound and southbound passes. Figure 3.5
defines the parameters of the satellite's pass overhead in terms of     , the minimum Earth central
angle between the satellite's ground track and the ground station. This is 90° minus the angular
distance measured at the center of the Earth from the ground station to the instantaneous orbit pole
at the time of contact. If we
know the latitude and longitude of the orbit pole and of the ground station, index gs, then the value
of       is



where Δlong is the longitude difference between gs and the orbit pole. At the point of closest
approach, we may compute the minimum nadir angle,       , maximum elevation angle,       , and
minimum range, Dmin, as

<!-- PDF_PAGE: 54 -->

54                                                                     Communication Challenge




At the point of closest approach, the satellite is moving perpendicular to the line of sight to the
ground station. Thus, the maximum angular rate of the satellite as seen from the ground station,
     , will be




where        is the orbital velocity of the satellite, and P is the orbit period.
Finally, it is convenient to compute the total azimuth range, ΔΦ, which the satellite covers as seen
by the ground station, the total time in view, T, and the azimuth Φcenter, at the center of the viewing
arc at which the elevation angle is a maximum:




where the arccos is evaluated in degrees. Φcenter is related to Φpole , the azimuth to the direction to
the projection of the orbit pole onto the ground by

                                      Φ               °   Φ

                    Φ

where Φ               if the orbit pole is east of the ground station and Φ       if the orbit
pole is west of the ground station. The maximum time in view, T max, occurs when the satellite
passes overhead and

                                                          .

Orbit selection is driven by observation objectives, but also by operational and satellite design
constraints. The maximum periods between contacts to ground control stations have an implication
in sizing the data storage system on-board, in order to to provide sufficient capacity to
accommodate all observation data until the next downlink occurs. Duration of these ground
contacts affects the required transmission capacity to transfer all acquired data. With respect to
mission operations, on-board autonomy requirements are driven by the periods between ground
contacts.

<!-- PDF_PAGE: 55 -->

Communication Challenge                                                                        55




3.4. LEO communication
QB50 satellite orbits will decay from an altitude of around 350 km until the re-entry phase in
proximity of the Earth. Network orbits are LEO, a kind of orbit that has a lot of advantages but also
some disadvantages. One of the most limited resources of a satellite in a low Earth orbit is surely
the communication time. The contact window between a satellite and ground station can be
determined from the orbit elements and the location of the ground station. A major drawback is that
the satellite is only visible for few minutes each day. This problem limits the amount of
transferable data dramatically, moreover the ground stations are not utilized for a large fraction of
the day. Another disadvantage is that contact windows have fixed start and end times due to orbit
geometry, and an academic ground station can serve only a single satellite at a time. Therefore,
overlapping contact windows of individual satellites (see figure 3.5) raises the question of which of
these satellites should be operated first and what is the best solution to avoid this kind of problem.
To handle conflicts with regard to overlapping contact windows, mission design and
communication system optimization come into play. These particular problems will be investigated
deeply in next chapters comparing some different analysis.




                     Figure 3.5: Overlapping contact windows for adjacent ground stations




Within this work, the problems of finding an optimal communication strategy and best number and
positions of ground stations in order to satisfy all the mission requirements were analyzed.
Main requirements for QB50 mission are the use of simple and highly qualified space technologies.
Especially, for this analysis the most relevant achievement required is the daily 4 Mb of data
downloaded to Earth for each CubeSat.
In the case of classic ground station networks, the main objective is the increase of the ground
stations utilization. In academic ground station networks, scheduling follows the objective to share
ground station resources and to extend communication time. The participants of these academic
ground station networks are usually faced with some problems. Very often the ground stations were
built up in the scope of small satellite projects, however, since these satellites are normally
launched to low Earth orbit (LEO), the available communication time is restricted to a few minutes
a day. By sharing the ground stations between two institutions, the contact time with the satellites
can be doubled on both sides. Sharing ground stations in academic networks has no financial
benefit; the educational and research aspects play the leading role. Major emphasis in academic
ground station networks is placed on flexibility.
In the following chapters several problems and systems will be introduced, and several studies
related to optimal assignment of contact windows to ground station networks will be conducted.

<!-- PDF_PAGE: 56 -->

56                                                                     Communication Challenge




3.5. Communication of multiple satellites
Distributed systems of small satellites offer interesting capabilities to complement a broad
spectrum of space missions, in particular the Earth and atmospheric observation missions. A group
of satellites is described as a constellation, when several satellites flying in similar orbits without
control of relative positions, are organized in time and space to coordinate ground coverage. They
are controlled separately from ground control stations, that could be organized in a ground network.
It is possible to use the word formation, if multiple satellites with closed-loop control on-board
provide a coordinated motion control on the basis of relative positions to preserve the topology. It
is the collective use of several spacecrafts that performs the function of a single, large, virtual
instrument. Other possibilities for multiple spacecraft configurations are Swarms or Cluster. These
configurations are used if a distributed system of similar spacecrafts is cooperating to achieve a
joint goal without fixed absolute or relative positions. Each member determines and controls
relative positions to the other satellites. For self-organization in groups essential ingredients are
communication and control strategies. The system capabilities can be significantly increased by an
appropriate combination of data from multiple cooperating technical components. Space
applications raise additional challenges such as significant delays in the telecommunication link
due to large distances, high dynamics in changing positions and high levels of noise effects. The
efficient control of a group of satellites from ground is a hard contest. Challenging technologies to
be implemented for distributed small satellite systems include:

        Determination of attitude and position: miniaturized sensors have to be introduced to
         determine the attitude of the satellite with sufficient accuracy for the interpretation of
         measurements, as well as for the relative distance determination between the spacecrafts.
        Autonomous control of position and attitude: the deviation between measured position and
         attitude towards target values has to be determined in order to generate related correction
         maneuvers. In orbit there are only sporadic contacts to ground control stations, thus real-
         time reaction capabilities have to be implemented.
        Operations of satellite swarms: the control of satellite formations requires the coordination
         of autonomous reaction capabilities on-board with ground control interactions,
         characterized by signal propagation delays and link interrupts. The operator would benefit
         from functions, enabling just to control a leader satellite, while at a given formation the
         trajectories of the others are generated autonomously.

The primary goal of the communication system is to provide a link to relay data findings and send
commands to and from the satellite. Generally CubeSat communication systems are composed
primarily of the telemetry and command systems, which send and receive data, respectively.
Analog and digital data collected by the sensors and payload of the satellite must be relayed to the
ground stations via the telemetry system.




3.6. QB50 communication strategies and configurations
For the communication strategy, selection of a geometry is not the only problem. The visible areas
do not only depend on the orbit parameters, but also on communication configurations and by
technology that is used. The choice of transceivers, antennas, type of cables and other little parts
turns out to be fundamental to perform a detailed analysis. To select a communications system for a
CubeSat, two main possibilities exist: buying COTS (Commercial Off The Shelf) or building
devices from individual components.

<!-- PDF_PAGE: 57 -->

Communication Challenge                                                                           57



Purchasing a COTS component simplifies the communication system design. Purchased devices
typically accept a wide range of standard data and perform all general functions required. Several
companies build space-rated instrumentations, but usually they are too expensive, heavy, and big
for CubeSats. But the increased number of CubeSats in space missions in recent years has spiked
an interest in this application field. The Stensat Group or other companies like AstroDev and ISIS
began selling a lot of instrumentations designed for CubeSats in the last years.
Another way is the use of modified COTS originally designed for earth use, but many COTS would
have serious problems operating in space due to the missing radiation and vacuum tolerance. Some
projects, mainly at universities, decide to build the entire package of individual components by
themselves. In the following chapter the communication analysis will be discussed and a solution
will be selected to analyze deeply the communication problem. For QB50 mission it is possible to
propose two different strategies, based on the frequency link, S-band and UHF/VHF strategies.
These configurations need different devices and are mainly characterized by different data rates. To
enter into the details of the analysis it is mandatory to study the ground and space segment with
high accuracy. For this study, sample COTS products have been selected which are typically used
on-board of CubeSats. This high level of accuracy is in part guaranteed by the STK software. Using
this tool it is possible to obtain detailed results on access characteristics, calculating a wide variety
of analysis outputs.

As has been stated QB50 has the objective to use CubeSats for multi-point, in-situ, long-duration
measurements of atmospheric properties in the lower thermosphere and in-orbit demonstration of
new technologies. This will be achieved by measuring a number of key parameters during the
whole mission, and comparing them to predicted data. Data collected by constellation have to be
downloaded to Earth following the communication mission requirements. These requirements
currently consist mainly in the daily expected amount of data produced by the Sensor-Unit, which
is predicted to be around 2 Mb, and additional 2 Mb related to housekeeping and science data from
the CubeSat teams. Therefore the communication system should be capable of transmitting 4Mb
data down to Earth per day. Usually the CubeSat communication baseline is the usage of a
UHF/VHF system, but data transmission rate are lower compared to other systems due to the low
frequency. S-Band is another interesting possibility, but has some disadvantages, due to the limited
power budget on CubeSats and the requirements on antenna pointing. Through the first part of the
communication analysis there is a dissertation about the optimal communication system to use.
Once the optimal solution is fixed, the details of the access between ground and space segments
during the mission will be discussed, by some investigations on the communication link quality and
access characteristics variations during the mission time. It should be stated, that the chosen
system/bandwidth combination only affects the overall data rate and therefore the results can easily
be translated to different communication systems. The objectives of this analysis will be the
finding of number and positions of ground stations required to recover the data generated by the
QB50 constellation and optimize the communication link by studying different possible
architectures.




3.6.1. Proposed communication systems
The possible strategies adoptable are distinguished mainly by different frequency bands used.
Developing an understanding of radio communications begins with the comprehension of basic
electromagnetic radiation. Radio waves belong to the electromagnetic radiation family, which
includes x- ray, ultraviolet, and visible light forms of energy we use every day. Much like the
gentle waves that form when a stone is tossed into a still lake, radio signals radiate outward, or
propagate, from a transmitting antenna. Radio waves are characterized in terms of amplitude,
frequency, and wavelength. Radio wave amplitude, or strength, can be visualized as its height the

<!-- PDF_PAGE: 58 -->

58                                                                           Communication Challenge



distance between its peak and its lowest point. Amplitude, which is measured in volts, is usually
expressed in terms of an average value called

root- mean- square, or RMS. The frequency of a radio wave is the number of repetitions or cycles it
completes in a given period of time. Frequency is measured in hertz (Hz), and one hertz equals one
cycle per second. Radio wavelength is the distance between crests of a wave, and the product of
wavelength and frequency is a constant that is equal to the speed of propagation. Thus, as the
frequency increases, wavelength decreases, and vice versa.




                                 Figure 3.6: Radio Frequency Spectrum [17]


                                                   [17]


                  Table 3.1: Wavelengths and frequencies for different communication bands




In the radio frequency spectrum, the usable frequency range for radio waves extends from about 20
kHz (just above sound waves) to above 30,000 MHz.
Very High Frequency (VHF) Band is used in CubeSat mission usually for the uplink data
transmission in combination with the Ultra High Frequency (UHF) instead used for the downlink.
The VHF frequency band is defined as the frequency range from 30 to 300 MHz. From the

<!-- PDF_PAGE: 59 -->

Communication Challenge                                                                       59



previous discussion about the relationship between frequency and wavelength, it should be noted
that VHF wavelengths vary from 10 meters at the low end to one meter at the high end. This means
that the size of antennas and tuning components used in VHF radio are much smaller and lighter
than those of High Frequency radios. Ultra High Frequency (UHF) Band, commonly used for the
CubeSat downlink data transmission, goes from 300 MHz to 2450 MHz, but UHF radios do not
utilize frequencies above 512 MHz. The wavelengths associated with 300 to 512 MHz range from
one meter to 0.58 meters. The very small antennas required for these wavelengths make them ideal
for use on high- speed aircraft and as has been said for small satellite applications.
VHF and UHF radio frequencies propagate principally along Line Of Sight (LOS) paths, and it is
also clear that the elevation of both the transmitting and receiving antennas is crucially important.
For example if the receiving antenna were mounted on a 8 meters tower, the total LOS distance
would be increased to 14.5 km. Of course if the radiomen were both located on the tops of
mountains, the LOS range might be as much as from 80 to hundred km. An accurate estimation of
the minimum and maximum elevation angles for a ground station can permit to perform reliable
analysis for communication link. Elevation angle is one of the most important parameters that
appear in communication analysis and has a strong influence for communication link results.
With very few exceptions, space-ground communications for CubeSats are actually made in
VHF/UHF bands where the hardware requirements, such as antenna pointing accuracy, are not as
critical as for higher frequencies.
In VHF/UHF bands, a reliable and cheap ground station can be integrated using commercial off-
the-shelf amateur radio hardware and software. Compared to typical existing amateur radio VHF/
UHF systems on nanosatellites, other systems like S-band offers data throughput improvements by
taking advantage of broader available bandwidth and higher frequency.
S-band is defined for radio waves with frequencies that range from 2 to 4 GHz, crossing the
conventional boundary between UHF and SHF at 3.0 GHz. The S band is used by weather radar,
surface ship radar, and some communications satellites, especially those used by NASA to
communicate with the Space Shuttle and the International Space Station.
The main difference between S-band and VHF/UHF systems is the transmission data rate, which
heavily influences the amount of data transferred to ground stations. The biggest disadvantage of
the VHF/UHF system is the low data rate, which is in on the order of few kbps, as opposed to the
higher data rates of the S-band that are up to 1 Mbps. Although this disadvantage is a major
drawback the VHF/UHF system, it has the highest spreading/distribution in CubeSat space
missions. This solution results to be with low power consumption and wide beamwidth are two
good reasons to adopt it instead of other solutions that could be more expensive from the power
consumption point of view. S-band has a very interesting data rate, but has also high power
consumption and a narrow beamwidth, which makes it necessary to add something to solve the
antenna pointing problem. In spite of these disadvantages S-band remains an intriguing solution
especially for the future trends of CubeSat space communications, and could be implemented also
in current missions. The objective of the following analysis is to determine the optimal strategy to
satisfy all QB50 mission requirements, as both strategies have their strengths and weaknesses.




3.7. Analysis methodology
QB50 network has a complex structure that varies during the mission. Communication is not easy
to evaluate in a first moment directly taking into account the constellation problem. There is the
need to understand in a first step the communication link characteristics, to evaluate the
multisatellites problem it is mandatory enter into the detail of the one-to-one problem, where one
CubeSat or satellite is communication with one ground station. Analyzing this first problem it is
possible comprehend the basis for the communication for this kind of mission, choosing the

<!-- PDF_PAGE: 60 -->

60                                                                   Communication Challenge



devices for the ground and space segment, analyzing also the quality of the signal due to these
devices. Once this problem will be fixed it will be possible extend it to the constellation issue.

The analysis is divided into three main steps:

     One-to-one analysis, taking into account one CubeSat with QB50 orbit characteristics and
      one fixed ground station from QB50 consortium ground station list;

     Link budget analysis, to evaluate the quality of the signal and communication link;

     Constellation problem, increased number of ground stations with multiple CubeSats
      analysis.

<!-- PDF_PAGE: 61 -->

One-to-one problem                                                                                61




4 One-to-one problem

4.1. STK software and scenarios
System Tool Kit (STK) is a modular physics-based software package developed by Analytical
Graphics, which allows the complex analysis of land, sea, air and space assets. At the core of
STK’s software is a geometry engine that is designed to model time and space with unmatched
accuracy, and that has been enhanced through more than 20 years of development and built to meet
the needs of its users. STK delivers flexibility in coordinate system definition by converting from
or to any coordinate system with equal accuracy. This flexibility allows users to define objects in
the most appropriate coordinate system while maintaining a relationship with other objects. STK
also determines dynamic spatial relationships among all of the assets, or objects, under
consideration including the quality of those relationships or accesses given a number of complex,
simultaneous constraining conditions. Additional flexibility on modeling the position, velocity and
orientation of moving objects is provided to the user by allowing analysis using simple algorithms
and fundamental equations to emulate ideal motion, or using high fidelity integrators and force
models to generate realistic trajectories. STK was first adopted by the aerospace community for
orbit analysis and access calculations. As the software was expanded, more modules were added
that included the ability to perform calculations for communications systems, radar, and
interplanetary missions beside orbit collision avoidance. In addition to the analysis provided, STK
includes real-time visualization, in both 2D and 3D, of all air, land, sea and space components. This
has allowed STK to become a standalone software package capable of modeling and analyzing
complete and complex systems. Each system in STK is modeled with a hierarchy of objects, with
the highest level object being a Scenario. A scenario will contain numerous parent objects and each
parent object may include numerous child objects.
In order to analyze the performance of a constellation of CubeSats, STK will be used to perform all
orbital trajectory calculations, including perturbing forces. STK will also compute all access data
between targets, satellites and ground stations, which will include access start and stop times,
duration of access, and positional data for each access, such as azimuth, elevation and range while
taking into account terrain and access constraints.
STK allows calculating the access between a constellation of satellites which are represented by
their transmitters, and a constellation of ground stations represented by their receivers. The
computation of accesses is based on the visibility of a satellite by a ground station. The position of
the satellite is projected on the earth surface giving its sub-satellite latitude and longitude. The
intersection of these points with the mask of the antenna determines the access feasibility. In the
case of this prediction, the calculation of accesses by the geometrical approach is not sufficient. It
is indispensable to add a constraint based on the communication link between the transmitters and
the receivers, which has been done using the communication module of STK. This module can
provide a detailed link budget report between two communication elements. STK evaluates the
links and allows to determine the quality of the communication to validate if an access exists. With

<!-- PDF_PAGE: 62 -->

62                                                                                One-to-one problem



the communication module it is not possible to calculate the accesses directly, it just provides
information about the link parameters, but it can be used indirectly to predict accesses.
Usually, the main information provided by the custom access report is:

     Access Start Time
     Access Stop Time
     Access Duration
     Gap duration
     Collected data

Once the parameters have been calculated, the report can be exported and saved in text or CSV
format, and it is possible to use other software, like MATLAB, to increase further the complexity
of analysis, because STK in the basic version allows simultaneous accesses, which are not physical
possible. In order to obtain the quantity of transmitted and collected data, the access duration and
the gap duration are multiplied by the data rate of the transmitter and the date rate of the
instruments, respectively.
Each analysis or design space within STK is called a scenario. Each scenario defines the default
analysis time period and base units which are passed to all parent and child objects included in the
scenario. Only one scenario may exist at any given time; however, data may be exported and
reused in subsequent analyses.
Objects are at the base of STK’s analysis engine. Once more than one object is added, STK can
analyze relationships between two or more objects. These relationships can include: line of sight,
position, velocity, communication duration or range to name a few. There are several different
types of objects that can be added, such as: satellites, targets, facilities, planets, stars, constellations
or chains. Each object automatically inherits the general properties of the scenario, such as analysis
time and base units. The properties of each object can be individually modified to fit the needs of
the system being modeled, allowing for different coordinate systems, units or analysis time periods
for each object. For each object within a scenario, various reports and graphics, both static and
dynamic, may be created. Relative parameters between an object and another one can also be
reported, and the effect of real-world restrictions or constraints enabled, so that more accurate
reporting is obtained.
Using access reports provided by STK, an algorithm will be developed to analyze the performance
of a CubeSat constellation. In order to understand deeply the behavior of the communication links
between QB50 CubeSats and the ground segment, first it is mandatory to analyze the one-to-one
problem, between one CubeSat and one GS. In the first analysis conducted, a CubeSat is selected
with QB50 orbit characteristics. This information is also obtained by past studies about
aerodynamics and orbital dynamics analysis. One of the most important things for an STK scenario
is surely the choice of the propagator, to obtain the more realistic trajectory as possible. A
propagator is a tool for solving the equations of motion of the satellite in orbit. There are two types
of orbit propagators available in STK: analytic and numerical. Analytic propagators use a closed-
form solution of the time-dependent motion of a satellite to produce ephemeris or to provide
directly the position and velocity of a satellite at a particular time. Numerical propagators integrate
the equations of motion for the satellite by using different solvers like Runge-Kutta. Although
Satellite Tool Kit has more than six propagators, selected ones, particularly High Precision Orbit
Propagator (HPOP) and J4 Perturbation are the most convenient propagators for most of the
computations. For the scenarios considered in the following the HPOP propagator will be used.
This propagator uses a numerical integration method to propagate the satellite state in the J2000
reference frame. The figures below resume the most important CubeSat STK input data.

<!-- PDF_PAGE: 63 -->

One-to-one problem                                                                                    63




                           Figure 4.1: CubeSat orbit characteristics for STK scenarios.




                              Figure 4.2: CubeSat force model for STK scenarios.

The CubeSat orbits are nearly circular, with an initial altitude of 350 km. Orbit inclination for this
first part of analysis is 79 deg and orbit epoch is assumed to start on 15th April of 2015.
To simulate the drag effect and obtain the orbit decay during the mission an efficient force model
has to be chosen. Figure 4.2 shows the most relevant simulation parameters and values for the force
model. In the scenario it is taken into account the drag effect but also the solar effects, like the solar
radiation      pressure     and    solar    flux    by   the     geomagnetic       index      (Kp-index).

<!-- PDF_PAGE: 64 -->

64                                                                                     One-to-one problem



The K-index quantifies disturbances in the horizontal component of Earth's magnetic field with an
integer in the range 0-9, with 1 being calm and 5 or more indicating a geomagnetic storm. It is
derived from the maximum fluctuations of horizontal components observed on a magnetometer
during a three-hour interval. The K-scale is quasi-logarithmic. The conversion table from
maximum fluctuation R (nT) to K-index, varies from observatory to observatory in such a way that
the historical rate of occurrence of certain levels of K are about the same at all observatories. In
practice this means that observatories at higher geomagnetic latitude require higher levels of
fluctuation for a given K-index. The official planetary Kp index is derived by calculating a
weighted average of K-indices from a network of geomagnetic observatories. Since these
observatories do not report their data in real-time, various operations centers around the globe
estimate the index by means of data available from their local network of observatories.
To have a reliable description of the drag effect it is mandatory to choose an appropriate drag
coefficient (Cd) for the CubeSat and a convenient atmospheric density model. The value for Cd is
assumed to be 2.3 by previous aerodynamic analysis, while the used atmospheric model is the
NRLMSISE 2000. This model is an empirical density model developed by US Naval Research
Laboratory based on satellite data. It uses the composition of N2, O, O2, He, Ar and H to determine
the neutral density. The valid altitude range is between 0 km to 1000 km. The input parameters for
the model are: year and day, time of day, geodetic altitude, geodetic latitude, longitude, magnetic
index and F10.7 solar radiation flux index. This model is also the recommended model for QB50
because of the available integration in the standard software and good agreement with the density
obtained by satellite measurements.
The one-to-one scenario also includes the presence of the third body gravity effect of the Sun and
Moon, neglecting other possible contributes. By using these parameters and assumptions the
mission time turns out to be almost 4 months, with a slow decay during the main part of the
mission and a rapid one only in the last mission days.



                                                                                  For Educational Use




             Figure 4.3: Altitude as a function of mission time for a QB50 CubeSat, obtained with STK




4.2. Fixed Ground Station scenario
The first step of one-to-one communication analysis includes the study of one CubeSat, with QB50
characteristics, and one ground station. For this first analysis, it is fixed one ground station, which
is the future facility placed at VKI (4.386 deg, 50.755 deg) in next months. For this kind of study

<!-- PDF_PAGE: 65 -->

One-to-one problem                                                                                             65



the position of the antenna and of other devices at VKI will result very important. Interesting
investigation and evaluation are done directly in first person to estimate some fundamental
parameters in order to increase the reliability of the analysis. Some additional VKI GS features will
be discussed in detail in next chapters.


                                               For Educational Use




                    Figure 4.4:STK scenario with fixed VKI Ground Station (obtained with STK)


In this scenario, the VKI ground station has two different receiver systems: VHF/UHF and S-band.
In order to investigate the behavior of both systems the access for each system is analyzed
separately and, defining the communication characteristics, results are eventually compared. The
receivers are mainly characterized by the system beamwidth. The UHF/VHF system guarantees a
larger angle with respect to S-band, the beamwidths chosen are respectively of 27.5° and 3°.




  Figure 4.5:Schematic representation of different beamwidths for different communication systems (green UHF/VHF
                                           cone, red S-Band opening angle).


A narrow beamwidth, as it is shown in Figure 4.5, can guarantee only a short contact with respect
to a larger beamwidth. Contacts will be very short if the ground station cannot follow the satellite
during its passage above the facility.
The beamwidth is included in the simulation by putting a constraint on the minimum elevation
angle for the ground facility; minimum elevation angle for the UHF/VHF strategy is around 76 deg,
while for the S-band is 88.5 deg. Looking at these values it is clear that the S-band has a narrow
beamwidth, and access results very difficult. In the first simulation the ground station is assumed to
be vertical, with the pointing direction oriented to zenith. Using STK software, it is possible to

<!-- PDF_PAGE: 66 -->

66                                                                                    One-to-one problem



evaluate the access for both systems. Results are not satisfactory due to the few and short accesses.
UHF/VHF system is characterized by 26 accesses during all mission time, for a total duration of
408 seconds with a mean duration of 15 seconds, while S-band has only 3 accesses for a total
duration of 4 seconds. Accumulated data are obtained also by STK using different data rates for the
communication strategies. During the whole mission UHF/VHF and S-band systems can collect
only an amount of data of around 4 Mb. Below there is a classic example of the output information
obtained by STK for the access; the following outputs are the results for the UHF/VHF and S-band
systems with a fixed ground station.

          Table 4.1: Access results for UHF/VHF system with beamwidth of 27.5 deg (obtained with STK)


 UHF/VHF system:

                      Access        Start Time (UTCG)             Stop Time (UTCG)            Duration (sec)
                     ------    ------------------------      ------------------------        --------------
                          1    17 Apr 2015 13:25:13.646      17 Apr 2015 13:25:31.871                18.226
                          2    18 Apr 2015 23:17:26.634      18 Apr 2015 23:17:49.446                22.812
                          3    25 Apr 2015 11:57:18.451      25 Apr 2015 11:57:35.448                16.997
                          4    28 Apr 2015 11:32:43.255      28 Apr 2015 11:33:02.232                18.977
                          5    29 Apr 2015 21:22:02.028      29 Apr 2015 21:22:14.324                12.296
                          6     2 May 2015 20:54:45.716       2 May 2015 20:55:07.521                21.805
                          7     5 May 2015 20:25:45.385       5 May 2015 20:26:06.375                20.991
                          8     8 May 2015 19:54:53.425       8 May 2015 19:55:14.390                20.965
                          9    11 May 2015 19:22:08.246      11 May 2015 19:22:28.916                20.669
                         10    16 May 2015 08:26:56.092      16 May 2015 08:27:17.299                21.207
                         11    24 May 2015 17:08:08.752      24 May 2015 17:08:27.520                18.768
                         12    26 May 2015 06:44:02.079      26 May 2015 06:44:22.763                20.684
                         13    31 May 2015 15:53:58.406      31 May 2015 15:54:05.116                 6.709
                         14     2 Jun 2015 05:27:10.741       2 Jun 2015 05:27:14.481                 3.740
                         15     4 Jun 2015 15:19:00.112       4 Jun 2015 15:19:17.480                17.368
                         16     6 Jun 2015 04:50:28.554       6 Jun 2015 04:50:48.626                20.072
                         17     8 Jun 2015 14:39:51.781       8 Jun 2015 14:39:56.917                 5.136
                         18    10 Jun 2015 04:09:26.590      10 Jun 2015 04:09:46.299                19.709
                         19    12 Jun 2015 13:55:51.774      12 Jun 2015 13:56:10.355                18.582
                         20    14 Jun 2015 03:23:44.865      14 Jun 2015 03:23:50.567                 5.702
                         21    21 Jun 2015 12:21:13.901      21 Jun 2015 12:21:33.483                19.582
                         22    26 Jun 2015 11:26:21.726      26 Jun 2015 11:26:34.217                12.491
                         23    29 Jun 2015 00:51:36.067      29 Jun 2015 00:51:54.448                18.381
                         24     2 Jul 2015 10:25:15.040       2 Jul 2015 10:25:31.727                16.687
                         25    10 Jul 2015 09:07:49.998      10 Jul 2015 09:07:51.958                 1.960
                         26    13 Jul 2015 22:12:41.671      13 Jul 2015 22:12:49.156                 7.485

 Global Statistics
 -----------------
 Min Duration            25    10 Jul 2015 09:07:49.998      10 Jul 2015 09:07:51.958                    1.960
 Max Duration             2    18 Apr 2015 23:17:26.634      18 Apr 2015 23:17:49.446                   22.812
 Mean Duration                                                                                          15.692
 Total Duration                                                                                        408.000




             Table 4.2: Access results for S-band system with beamwidth of 3 deg (obtained with STK)


 S-band system:

                      Access        Start Time (UTCG)             Stop Time (UTCG)            Duration (sec)
                     ------    ------------------------      ------------------------        --------------
                          1     2 May 2015 20:54:56.381       2 May 2015 20:54:56.874                 0.493
                          2     6 Jun 2015 04:50:37.821       6 Jun 2015 04:50:39.358                 1.537
                          3    21 Jun 2015 12:21:22.662      21 Jun 2015 12:21:24.729                 2.067

 Global Statistics
 -----------------
 Min Duration             1     2 May 2015 20:54:56.381       2 May 2015 20:54:56.874                   0.493
 Max Duration             3    21 Jun 2015 12:21:22.662      21 Jun 2015 12:21:24.729                   2.067
 Mean Duration                                                                                          1.365
 Total Duration                                                                                         4.096

<!-- PDF_PAGE: 67 -->

One-to-one problem                                                                                 67



Results for the fixed ground station are far from being satisfactory, the daily requirement of 4 Mb is
not reached and this amount of data is transferred only at the end of the mission. These outcomes
suggest adding a rotator mechanism to the communication architecture in order to increase access
time and also the number of access.




4.3. Ground Station with rotator mechanism
In this new scenario we assume to have two different transmitters on the CubeSat characterized by
their data rates, and a single receiver at VKI with a minimum elevation angle of 20 deg, due to the
obstacles present around VKI. The use of a rotator introduces new constraints in the simulation,
these are due to the possibility that the satellite can move faster than rotator angular speed, so that
the contact may be lost. The selection of the rotator is very important, because the maximum
elevation and azimuth rate are given by the specifications of this device.
QB50 requirements agree completely with the selection of the rotator YAESU G-5500. This
antenna azimuth-elevation rotator and controller is one of the cheapest but also most reliable and
qualified.




                Figure 4.6: Antenna azimuth-elevation rotator and controller YAESU G-5500. [18]


The YAESU G-5500 provides 450° azimuth and 180° elevation control of medium- and large-size
unidirectional satellite antenna arrays under remote control from the station operating position. The
rotator permits the ground antenna to track and follow the CubeSat during its transit. The access
time and number of access result to be increased a lot. The choice of this rotator is also due to its
use in other GENSO ground station projects [Aspects of a Low-Cost Ground Station development
for GENSO network, Vlad Dascal, Paul Dolea, Tudor Palade, Octavian Cristea]. In the following
table it is possible to understand the main specifications for this rotor mechanism.

<!-- PDF_PAGE: 68 -->

68                                                                                     One-to-one problem



                 Table 4.3:Ground station rotor mechanism specifications (YAESU G-5500). [18]




            YAESU G-5500 Specifications
            Voltage requirement                        110-120 or 200-240 VAC

            Motor voltage                              24 VAC

                                                       Elevation (180°): 67 sec.
            Rotation time (approx., @60Hz)
                                                       Azimuth (360°): 58 sec.

            Maximum continuous operation               5 minutes

                                                       Elevation: 14 kg-m (101 ft-lbs)
            Rotation torque
                                                       Azimuth: 6 kg-m (44 ft-lbs)

                                                       Elevation: 40 kg-m (289 ft-lbs)
            Braking torque
                                                       Azimuth: 40 kg-m (289 ft-lbs)

            Vertical load                              200 kg (440 lbs)

            Pointing accuracy                          ±4 percent

            Wind surface area                          1 m2

            Control cables                             2 x 6 conductors - #20 AWG or larger

            Mast diameter                              38-63 mm (1-1/2 to 2-1/2 inches)

            Boom diameter                              32-43mm (1-1/4 to 1-5/8 inches)

                                                       Rotators: 9 kg (20 lbs)
            Weight
                                                       Controller: 3 kg (6.6 lbs)




The most important parameters are surely the Rotation times: by means of these values it is
possible to evaluate the maximum elevation and azimuth rate, that are respectively 2.68 deg/sec
and 6.2 deg/sec.
The new scenario gives better results and the presence of the new constraints due to the rotator
turns out to be negligible. For UHF/VHF and S-band strategies the access time and number turn out
to be the same, but the amount of collected data are much different.
In this scenario, it is possible to have around two accesses with the VKI ground station per day
with a mean duration of 144 seconds. Downloaded data are many. For UHF/VHF, only one ground
station can collect around 3 Mb per day from one CubeSat, so that the objective can be easily
reached with some modifications or using also few other GSs. The number of ground stations is
very low with respect to the number of the first scenario without the rotator mechanism. S-band
strategy guarantees a high amount of data, exceeding the QB50 requirements. Indeed it is possible
to collect more than 300 Mb per day. Mission communication requirements of 4 Mb/day is
completely achieved and satisfied by only one GS for each CubeSat.

The implementation of the rotator turns out to be good for requirements and YAESU G-5500 turns
out to be faster than the CubeSat angular speed during mission time, comporting contacts without

<!-- PDF_PAGE: 69 -->

One-to-one problem                                                                                 69



losses of communication. For UHF/VHF strategy it is not possible to reach the daily minimum
requirement of 4 Mb for the downlink, but results are not so far and it is possible to increase to 4
Mb with by some little expedients. Conversely, by using S-band system such requirements are all
satisfied. It is possible to affirm that the introduction of a rotator makes mission requirements
achievable.
In appendix A the list of contacts is available, with the sum of data collected during the mission for
S-band and UHF/VHF systems.
To increase the complexity of the simulations it is necessary to implement an investigation about
the signal quality. Next chapter will deal with the mission link budget analysis, introducing
particular devices for the ground and space segments. This kind of analysis is very important for
the choice of communication system and strongly influences the system selection.

<!-- PDF_PAGE: 70 -->

70                                                                                Link Budget Analysis




5 Link Budget Analysis

5.1. Ground segment
A ground station is an earth-based point of communication with the space segment. Ground
stations are the source for our interaction with satellites; hence they play an important role in any
satellite related operation and it is very important to have a good communication link between the
ground station and the space segment. Usually a ground segment involves the following tasks.

     •   Tracking the position of the satellite orbit and determining the orbit
     •   Telemetry operations to acquire and record satellite data and status
     •   Commanding operations to interrogate and control the various functions of the satellite
     •   Controlling operations to determine orbital parameters, to schedule all satellite passes and
         to monitor and load the on-board computer
     •   Data processing operations to present all the engineering and scientific data in the formats
         required for the successful progress of the mission
     •   Voice and data links to other worldwide ground stations and processing centres.




                Figure 5.1: Relationship between Space Segment, Ground Segment and Data users.

<!-- PDF_PAGE: 71 -->

Link Budget Analysis                                                                        71



Figure 5.1 shows the relationship between space segment, ground segment and data users.
Normally a ground segment can be divided into four main components:

    •   Hardware
    •   Software
    •   People
    •   Operations

Basically the hardware section consists of antennas, rotors, transceivers, computers, power
supplies, peripherals and data recorders.
There are mainly three different kinds of software uses in the student ground station operations:
Pre-pass         software,     Real       time       software      and       Post-pass       software.
Normally in a commercial ground station there are four different kinds of software involved,
including the onboard software which is needed for the spacecraft. At present most of the student
satellites do not have the function to upgrade software onboard using the uplink from the ground
station. Therefore the onboard software is not an essential item in a student ground station.
Pre-pass software is required before the pass of the spacecraft in order to determine and predict the
orbit, for observation, planning and scheduling, and for the command list generation and
simulation. Typically TLEs generated by Joint Space Operation Center, which is in charge of
tracking space objects for defense purpose and located in the United States of America, can be used
for this orbit prediction.
Real time software is required during the time the spacecraft is visible from the ground station. This
include mainly the antenna rotation software for satellite tracking, computer control software and
command and data handling software.
Post-pass software is the software required for Housekeeping, quality control and health
assessment, data processing and orbit determination and for data analysis.
The most important part for the successful operation is however the personnel. In a commercial
ground station people are involved in many different areas of responsibilities such as site and
project management, operation shift staff, hardware maintenance, software developer, data and
engineering support, administration, specialist engineers and scientists. However in a student
ground station all the operations are carried out by few staff members and a couple of students.
Eventually, operations bring hardware, software and people together. The operations team is the
fundamental human unit that integrates the mission software and hardware into an effective routine
process where frequent training is important for a successful operation.
In the following analysis a great importance will be given to hardware components, especially
antennas, rotors and transceivers, which are fundamental in order to study the link budget with a
high accuracy.




5.1.1. VKI Ground segment
Von Karman Institute is the QB50 project leader, and in next month’s a ground station dedicate to
this space mission will be placed at the institute. During past months antenna and Control computer
positions were fixed. A good understanding of the device allocations is very important in order to
estimate some parameters that turn out to be fundamental for a reliable analysis. The allocation
issues are mainly two: a large visibility area to avoid signal jamming by obstacles, and a short cable
distance between antenna and control computer to reduce cable losses. The antenna system will be
placed on top of the arc of the VKI main building, on fifth segment (from left/west). This position
guarantees a little distractions of the neighbors and an excellent sky visibility. Former VKI safety
room will be available for the Control Computer. By measuring the later cable route it is possible to

<!-- PDF_PAGE: 72 -->

72                                                                                  Link Budget Analysis



estimate a cable distance of around 37 m including 4 m margin. This length is very useful to
understand especially line losses.
Taking some pictures from the VKI roof it is possible to estimate the minimum elevation angle by
simple geometric considerations. From a first estimate, minimum elevation angle turns out to be
less than 10 deg. Using a 10 deg margin, it is possible to assume in simulations and calculations a
minimum elevation angle of 20 deg.




                          a)                                                             b)




                                                       c)

       Figure 5.2: Allocations for Antenna System (white arrow), and Control Computer Room (black arrow).

<!-- PDF_PAGE: 73 -->

Link Budget Analysis                                                                                       73




          Figure 5.3: Approximate view from 1.8 m height from top of arc (5th segment), North direction.




          Figure 5.4: Approximate view from 1.8 m height from top of arc (5th segment), South direction.




5.2. Space Segment
The main functions of the Space Segment are to transmit radio-navigation signals, and to store the
navigation message sent by the Control Segment. The space segment is defined by the number of
satellites in the constellation, as well as the characteristics of the satellites in question. Any
communications satellite is composed of a communications payload (antenna system) and its
supporting spacecraft bus (solar array and batteries, attitude and orbit control system, structure and
thermal control system). The Space Segment includes the tracking, telemetry and command
(TT&C)          station     or       stations,     and       a       satellite      control     center.
In QB50 mission the Space Segment consists in a 50 CubeSats network, each one having
transceiver and antenna to achieve all communication requirements. QB50 CubeSats will have the
antennas on the back part of each satellite in the functional unit. The frontal part will be dedicated
to     the    science     unit,    with     standard    sensors      equal     for     all   CubeSats.
In this chapter the best configuration and architecture will be studied for this segment in function of
signal quality.

<!-- PDF_PAGE: 74 -->

74                                                                                 Link Budget Analysis




5.3. Radio wave propagation
A signal traveling between an earth station and a satellite must pass through the Earth’s
atmosphere, including the ionosphere, and this can introduce certain impairments, which are
summarized in the following table. Some of the most important of these impairments will be
described in detail in next paragraphs.


                  Table 5.1: Propagation concerns for satellite communications systems [19]




5.3.1. Atmospheric loss
Losses occur in the Earth’s atmosphere as a result of energy absorption by the atmospheric gases.
These losses are treated quite separately from those which result from adverse weather conditions,
which of course are also atmospheric losses. To distinguish between these, the weather-related
losses are referred to as atmospheric attenuation and the absorption losses simply as atmospheric
absorption.
The atmospheric absorption loss varies with frequency, as shown in Figure 5.5. Two absorption
peaks are observed, the first one at a frequency of 22.3 GHz, resulting from resonance absorption
in water vapor (H2O), and the second one at 60 GHz, resulting from resonance absorption in
oxygen (O2). However, at the well clear frequencies of these peaks, the absorption is quite low.

<!-- PDF_PAGE: 75 -->

Link Budget Analysis                                                                                           75




Figure 5.5: Total zenith attenuation at ground level: pressure of 1 atm, temperature of 20°C, and water vapor of 7.5 g/m3.
                                                            [19]




The graph in Figure 5.5 is for vertical incidence, that is, for an elevation angle of 90° at the earth-
station antenna. Denoting this value of absorption loss as [AA]90 decibels, then for elevation angles
down to 10°, an approximate formula for the absorption loss in decibels is

                                             [AA] = [AA]90 cosec(El)

where El is the elevation angle. An effect known as atmospheric scintillation can also occur. This is
a fading phenomenon, the fading period being several tens of seconds. It is caused by differences in
the atmospheric refractive index, which in turn result in focusing and defocusing of the radio
waves, which follow different ray paths through the atmosphere. It may be necessary to make an
allowance for atmospheric scintillation, through the introduction of a fade margin in the link
power-budget calculations, however for missions like QB50 this contribute is usually not so
relevant.

<!-- PDF_PAGE: 76 -->

76                                                                           Link Budget Analysis



5.3.2. Ionospheric effects
Radio waves traveling between satellites and earth stations must pass through the ionosphere. The
ionosphere is the upper region of the Earth’s atmosphere, which has been ionized, mainly by solar
radiation. The free electrons in the ionosphere are not uniformly distributed but they make up
layers. Furthermore, clouds of electrons (known as traveling ionospheric disturbances) may travel
through the ionosphere and give rise to fluctuations in the signal that can only be determined on a
statistical basis. The effects include scintillation, absorption, variation in the direction of arrival,
propagation delay, dispersion, frequency change, and polarization rotation. All these effects
decrease as frequency increases, most in inverse proportion to the squared frequency, and only
polarization rotation and scintillation effects are of major concern for satellite communications.
Ionospheric scintillations are variations in the amplitude, phase, polarization, or angle of arrival of
radio waves. They are caused by irregularities in the ionosphere which change with time. The main
effect of scintillations is fading of the signal. The fades can be quite severe, and they may last up to
several minutes. In analogy with fading caused by atmospheric scintillations, it may be necessary to
include a fade margin in the link power-budget calculations to allow for ionospheric scintillation.



5.3.3. Rain attenuation
In engineering, attenuation is usually measured in units of decibels per unit length of medium
(dB/cm, dB/km, etc.). The decibel (dB) is a logarithmic unit that indicates the ratio of a physical
quantity (usually power or intensity) relative to a specified or implied reference level. A ratio in
decibels is ten times the logarithm to base 10 of the ratio of two power quantities. The decibel
confers a number of advantages, such as the ability to conveniently represent very large or small
numbers, and the ability to carry out multiplication of ratios by simple addition and subtraction.
The decibel symbol is often qualified with a suffix that indicates which reference quantity or
frequency weighting function has been used. For example, dBm indicates a reference level of one
milliwatt. When referring to measurements of power or intensity, a ratio can be expressed in
decibels by evaluating ten times the base-10 logarithm of the ratio of the measured quantity to the
reference level. Thus, the ratio of a power value P1 to another power value P0 is represented by LdB,
that ratio expressed in decibels, which is calculated using the formula:




Rain attenuation is a function of rain rate. By rain rate it is meant the rate at which rainwater would
accumulate in a rain gauge situated at the ground in the region of interest. In calculations relating to
radio wave attenuation, the rain rate is measured in millimeters per hour. Of interest it is the
percentage of time that specified values are exceeded. The time percentage is usually referred to a
year; for example, a rain rate of 0.001 percent means that the rain rate would be exceeded for 0.001
percent of a year, or about 5.3 min during any one year. In this case the rain rate would be denoted
by R0.001. In general, the percentage time is denoted by p and the rain rate by Rp.
The specific attenuation α is


where a and b depend on frequency and polarization. Values for a and b are available in tabular
form like the following one.

<!-- PDF_PAGE: 77 -->

Link Budget Analysis                                                                       77



                               Table 5.2: Specific attenuation coefficients [20]




The subscripts h and v refer to horizontal and vertical polarizations respectively. The corresponding
equations for circular polarization are




Once the specific attenuation is found, the total attenuation is determined as



where L is the effective path length of the signal through the rain. Because the rain density is
unlikely to be uniform over the actual path length, an effective path length must be used rather than
the actual (geometric) length. Figure 5.6 shows the geometry of the situation. The geometric, or
slant, path length is shown as LS. This depends on the antenna angle of elevation and the rain
height hR, which is the height at which freezing occurs.


                                      Table 5.3: Reduction factors [20]

<!-- PDF_PAGE: 78 -->

78                                                                            Link Budget Analysis




                                  Figure 5.6: Path length through rain [20]




For small angles of elevation (El < 10°), the determination of LS is complicated by Earth’s
curvature. However, for El ≥ 10° a flat earth approximation may be used, and from Figure 5.6 it is
seen that




The effective path length is given in terms of the slant length by



where rp is a reduction factor which is a function of the percentage time p and LG, the horizontal
projection of LS. From Fig. 5.6 the horizontal projection is given by



The reduction factors are given in Table 5.3. Putting all these factors together into one equation, the
rain attenuation in decibels is given by



In next paragraphs QB50 rain attenuation calculation will be proposed, evaluating the amount of
total attenuation for both strategies taken into account.




5.3.4. Other Propagation Impairments
Hail, ice, and snow have little effect on attenuation because of the low water content. Ice can cause
depolarization. The attenuation resulting from clouds can be calculated as that for rain, although the
attenuation is generally much lower. For instance, at a frequency of 10 GHz and a water content of
0.25 g/m3, the specific attenuation is about 0.05 dB/km and about 0.2 dB/km for a water content of
2.5 g/m3. But for lower frequencies the attenuation amount decreases much. Furthermore there are
also other communication losses due to devices, cable distances and efficiencies that will be

<!-- PDF_PAGE: 79 -->

Link Budget Analysis                                                                       79



illustrated in next paragraphs. A very interesting study was conducted on antenna technology in
order to optimize all characteristics and to find the best way to realize satisfactory communication
links.




5.4. Antenna theory
Antennas are the most important part of a ground station. They are the essential link between free
space and the transmitter or receiver and play a vital role in determining the characteristics of the
complete system. Design of antennas and its working environment will decide the effectiveness of
any given ground station. Antennas can be broadly classified according to function, as transmitting
antennas and receiving antennas. Although the requirements for each function, or mode of
operation, are markedly different, a single antenna may be, and frequently is, used for transmitting
and receiving signals simultaneously. Many of the properties of an antenna, such as its directional
characteristics, apply equally to both modes of operation, this being a result of the reciprocity
theorem. Certain forms of interference can present particular problems for satellite systems which
are not encountered in other radio systems, and minimizing these requires special attention to those
features of the antenna design which control interference. Antennas are a very important
component of communication systems. By definition, an antenna is a device used to transform an
RF signal, traveling on a conductor, into an electromagnetic wave in free space. Antennas
demonstrate a property known as reciprocity, which means that an antenna will maintain the same
characteristics regardless if it is transmitting or receiving. Most antennas are resonant devices,
which operate efficiently over a relatively narrow frequency band. An antenna must be tuned to the
same frequency band of the radio system to which it is connected, otherwise the reception and the
transmission will be impaired. When a signal is fed into an antenna, the antenna will emit radiation
distributed in space in a certain way. A graphical representation
of the relative distribution of the radiated power in space is called a radiation pattern.
Another way in which antennas for use in satellite communications can be classified is into earth
station antennas and satellite or spacecraft antennas. Although the general principles of antennas
may apply to
each type, the constraints set by the physical environment lead to quite different designs in each
case.
Before looking at antennas specifically for use in QB50 satellite systems, some general properties
and definitions for antennas will be given in this and the next few sections.




5.4.1. Polarization
The polarization of an antenna is the orientation of the electric field (E-plane) of the radio wave
with respect to the Earth's surface and it is determined by the physical structure of the antenna and
by its orientation. It has nothing in common with antenna directionality terms: horizontal, vertical,
and circular. Thus, a simple straight wire antenna will have one polarization when mounted
vertically, and a different polarization when mounted horizontally. Electromagnetic wave
polarization filters are structures which can be employed to act directly on the electromagnetic
wave to filter out wave energy of an undesired polarization and to let pass wave energy of a desired
polarization.

<!-- PDF_PAGE: 80 -->

80                                                                                      Link Budget Analysis



Reflections generally affect polarization. For radio waves the most important reflector is the
ionosphere, signals which are reflected from the ionosphere will have their polarization changed
unpredictably. Polarization properties of such signals will not be reliable.
For radio antennas, polarization corresponds to the orientation of the radiating element in an
antenna.
Polarization results to be the sum of the E-plane orientations over time projected onto an imaginary
plane perpendicular to the direction of motion of the radio wave. In the most general case,
polarization is elliptical, meaning that the polarization of the radio waves varies over time. Two
special cases are linear polarization (the ellipse collapses into a line) and circular polarization (in
which the two axes of the ellipse are equal). In linear polarization the antenna compels the electric
field of the emitted radio wave to a particular orientation. In circular polarization, the antenna
continuously varies the electric field of the radio wave through all possible values of its orientation
with regard to the Earth's surface. Circular polarizations are classified as right-hand polarized or
left-hand polarized.
In practice it is important that linearly polarized antennas be matched, lest the received signal
strength be greatly reduced. So horizontal should be used with horizontal and vertical with vertical.
Intermediate matching will lose some signal strength, but not as much as a complete mismatch.
Transmitters mounted on vehicles with large motional freedom commonly use circularly polarized
antennas so that there will never be a complete mismatch with signals from other sources.




                      Figure 5.7: E-field variation of Linear and Circular polarization. [16]




As it is shown in Figure 5.7, if the E-field vector exists in a vertical plane then the polarization is
liner and vertical. If the E-field vector exists in a horizontal plane then the polarization is liner and
horizontal. As it has been stated before a simple way to identify which polarization an antenna
communicates when it transmits is to note the direction of the radiator elements; for vertical
polarization the radiator elements are vertical and for horizontal polarization the radiator elements
are horizontal.
If the signal is composed of two plane waves of equal amplitude but differing in phase by 90°, then
the signal is circularly polarized. The tip of the electric field vector appears to be moving in a
circle. If the electric vector of the electromagnetic wave appears to be rotating clockwise (as it is
coming toward), the wave is said to be right circularly polarized. If it rotates counter clockwise,
then it is said to be left-circularly polarized.

<!-- PDF_PAGE: 81 -->

Link Budget Analysis                                                                       81



5.4.2. Antenna bandwidth
Bandwidth is another fundamental antenna parameter. Bandwidth describes the range of
frequencies over which the antenna can properly radiate or receive energy. Often, the desired
bandwidth is one of the determining parameters used to decide upon an antenna. For instance,
many antenna types have very narrow bandwidths and cannot be used for wideband operation.
Bandwidth of an antenna generally refers to the range of frequencies over which the antenna can be
used to obtain a specified level of performance. The bandwidth is often referenced to some
Standing Wave Ratio (SWR) value. But SWR bandwidth is not always related to gain bandwidth.
All antennas exhibit directive effects, it means some directions will have more radiation compared
to other directions. This property is called as the directivity of the antenna. A directional antenna
radiates and receives through a main lobe and several side lobes. The side lobes are usually
undesirable, since they attract spurious noise, and efforts are made through the antenna design to
suppress them. As it is shown in Figure 5.8, the antenna beam width is the 3 dB angle respect to its
boresight maximum power.
The antenna's bandwidth is the number of Hz for which the antenna will exhibit an SWR less than
2:1.
The bandwidth can also be described in terms of percentage of the center frequency of the band.




where FH is the highest frequency in the band, FL is the lowest frequency in the band, and FC is the
center frequency in the band.
In this way, bandwidth is constant relative to frequency. If bandwidth were expressed in absolute
units of frequency, it would be different depending upon the center frequency. Different types of
antennas have different bandwidth limitations.




                             Figure 5.8: Definition of antenna beamwidth. [14]

<!-- PDF_PAGE: 82 -->

82                                                                                      Link Budget Analysis



5.4.3. Radiation Pattern
The radiation or antenna pattern describes the relative strength of the radiated field in various
directions from the antenna, at a constant distance. The radiation pattern is a reception pattern as
well, since it also describes the receiving properties of the antenna. The radiation pattern is three-
dimensional, but usually the measured radiation patterns are two-dimensional slices of the three-
dimensional pattern, in the horizontal or vertical plane. These pattern measurements are presented
in either a rectangular or a polar format. The following figure shows a rectangular plot
presentation of a typical 10 elements Yagi antenna. The detail is good but it is difficult to visualize
the antenna behavior at different directions.




           Figure 5.9: Sample of a rectangular plot presentation of a typical 10 elements Yagi antenna [9]




A graphical representation of the intensity of the radiation of the antenna plotted against the angle
(from the perpendicular axis) is presented in a polar format. The graph is usually circular, the
intensity indicated by the distance from the centre. Polar coordinate systems are used almost
universally. In the polar coordinate graph, points are located by projection along a rotating axis
(radius) to an intersection with one of several concentric circles.




                    Figure 5.10: Sample of polar plot of a typical 10 elements Yagi antenna. [9]

<!-- PDF_PAGE: 83 -->

Link Budget Analysis                                                                        83



Figure 5.10 shows a polar plot of a 10 elements Yagi antenna. Polar coordinate systems may be
divided generally in two classes: linear and logarithmic. In the linear coordinate system, the
concentric circles are equally spaced, and are graduated. Such a grid may be used to prepare a
linear plot of the power contained in the signal. For ease of comparison, the equally spaced
concentric circles may be replaced with appropriately placed circles representing the decibel
response, referred to 0 dB at the outer edge of the plot. In this kind of plot the minor lobes are
suppressed. Lobes with peaks more than 15 dB or so low below the main lobe disappear because of
their small size. This grid enhances plots in which the antenna has a high directivity and small
minor lobes. The voltage of the signal, rather than the power, can also be plotted on a linear
coordinate system. In this case, too, the directivity is enhanced and the minor lobes suppressed, but
not in the same degree as in the linear power grid. In the logarithmic polar coordinate system the
concentric grid lines are spaced periodically according to the logarithm of the voltage in the signal.




5.4.4. Efficiency and Antenna Gain
The antenna efficiency relates the power delivered to the antenna and the power radiated or
dissipated within the antenna. A high efficiency antenna has most of the power present at the
antenna's input radiated away. A low efficiency antenna has most of the power absorbed as losses
within the antenna, or reflected away due to impedance mismatch. The losses associated with an
antenna are typically the conduction losses (due to finite conductivity of the antenna) and dielectric
losses (due to conduction within a dielectric which may be present within the antenna).

The antenna efficiency (or radiation efficiency) can be written as the ratio of the radiated power to
the input power of the antenna:




Efficiency is ultimately a ratio, giving a number between 0 and 1, and it is often quoted in terms of
a percentage. Antenna efficiency is also frequently quoted in decibels (dB); an efficiency of 0.1 or
10% is -10 dB, and an efficiency of 0.5 or 50% is -3 dB. The previous formula is sometimes
referred to as the antenna's radiation efficiency. This is different from another sometimes-used
term, called an antenna's total efficiency. The total efficiency of an antenna is the radiation
efficiency multiplied by the impedance mismatch loss of the antenna, when connected to a
transmission line or receiver (radio or transmitter). This can be summarized in the following
equation, where εT is the antenna’s total efficiency, ML is the antenna’s loss due to impedance
mismatch, and εR is the antenna’s radiation efficiency.



Since ML is a number between 0 and 1, the total antenna efficiency is always less than the antenna's
radiation efficiency. Said another way, the radiation efficiency is the same as the total antenna
efficiency if there were no loss due to impedance mismatch.
Efficiency is one of the most important antenna parameters. The losses are often due to the
electronics and materials that surround the antenna; these tend to absorb some of the radiated
power (converting the energy to heat), which lowers the efficiency of the antenna. Impedance
matching can greatly improve the efficiency of an antenna.

<!-- PDF_PAGE: 84 -->

84                                                                                     Link Budget Analysis



The term Antenna Gain describes how much power is transmitted in the direction of peak radiation
to that of an isotropic source. Antenna gain is more commonly quoted in a real antenna's
specification sheet because it takes into account the actual losses that occur.
An antenna with a gain of 3 dB means that the power received far from the antenna will be 3 dB
higher (twice as much) than what would be received from a lossless isotropic antenna with the
same input power.
Antenna Gain is sometimes considered as a function of angle, but when a single number is quoted
the gain is the 'peak gain' over all directions. Antenna Gain (G) can be related to directivity (D) by:



The gain of a real antenna can be as high as 40-50 dB for very large dish antennas (although this is
rare). Directivity can be as low as 1.76 dB for a real antenna (example: short dipole antenna), but
can never theoretically be less than 0 dB. However, the peak gain of an antenna can be arbitrarily
low because of losses or low efficiency. Electrically small antennas (small relative to the
wavelength of the frequency that the antenna operates at) can be very inefficient, with antenna
gains lower than -10 dB (even without accounting for impedance mismatch loss).
The gain of an antenna is a combination of directivity and efficiency when compared with a
reference antenna. Normally the reference antenna will be an isotropic one. Omnidirectional
antennas are the simplest ones that can be used in a ground station. That will simplify the building
of the ground station tremendously, since neither rotors nor rotor interfaces are needed. Most of
amateur satellites can be heard by using omnidirectional antennas. Also other types of antennas are
diffused for academic ground stations; one of these is surely the Yagi antenna, often used when
omnidirectional antennas cannot fully satisfy mission requirements.



5.4.5. Yagi Antennas
A basic Yagi consists of a certain number of straight elements, each measuring approximately half
wavelength. The driven or active element of a Yagi is the equivalent of a center-fed, half-wave
dipole antenna. Parallel to the driven element, and approximately 0.2 to 0.5 wavelength on the
either side of it, there are straight rods or wires called reflectors and directors, or passive elements
altogether. A reflector is placed behind the driven element and it is slightly longer than half
wavelength; a director is placed in front of the driven element and it is slightly shorter than half
wavelength. A typical Yagi has one reflector and one or more directors. The antenna propagates
electromagnetic field energy in the direction running from the driven element toward the directors,
and it is most sensitive to incoming electromagnetic field energy in this same direction. The more
directors a Yagi has, the greater the gain is. However, if more directors are added to a Yagi, the
antenna becomes longer. Below there is a picture of a Yagi antenna with 6 directors and one
reflector.




                        Figure 5.11: Yagi antenna with 6 directors and one reflector. [15]

<!-- PDF_PAGE: 85 -->

Link Budget Analysis                                                                      85




Since most of student satellites produce low strength (due to the low power) circular polarized
waves (due to the spinning of the satellites), then Yagi antennas are preferred to other types of
antenna like the omnidirectional one. The number of elements on a Yagi and array length are
directly proportional to the gain of the antenna. More elements mean more gain but smaller
beamwidth. The array length is of greater importance than the number of elements, within the limit
of a maximum element spacing of just over 0.4 λ.
The antenna should be mounted considering the polarization of the wave. If the orbiting antenna is
horizontally polarized and the ground station antenna is vertically polarized, nothing will be
received. If the orbiting antenna is circularly polarized and the ground station antenna is linearly
polarized, then maximum loss will be 3 dB. But if the orbiting and ground station antennas are
circularly polarized then maximum loss can be 10 dB due to the polarization mismatch.




                               Figure 5.12: Skeleton of a Yagi antenna [15]




The simplest way to enable polarization selection consists in mounting a horizontal Yagi and a
vertical Yagi on the same boom, then obtaining the cross Yagi antenna configuration (shown in
Figure 5.13). Separate feeds to each section of the Yagi, brought down to the operation position,
enable the user to switch to either horizontal or vertical polarization.




                                  Figure 5.13: Cross Yagi antenna [15]

<!-- PDF_PAGE: 86 -->

86                                                                          Link Budget Analysis




5.5. Link design
To understand link design, we need to define the relationship between data rate, antenna size,
propagation path length and transmitter power. This relationship is defined by a link equation or
link budget which relates all of the parameters needed to compute the signal-to-noise ratio of the
communication system. The basic equation used in sizing a digital data link is




where Eb/N0 is the ratio of received energy-per-bit to noise-density, P is the transmitter power, Ll is
the transmitter-to-antenna line loss, Gr is the receive antenna gain, k is Boltzmann’s constant, Ts is
the system noise temperature, and R is the data rate. The propagation path length between
transmitter and receiver determines Ls, whereas La is a function of factors such as rainfall density.
In most cases, an Eb/No ratio between 5 and 10 is adequate for receiving binary data with low
probability of error with some forward error correction [AMSAT datasheets]. Once we select the
orbit and determine the transmitter-to-receiver distance, the major link variables which affect
system cost are P, Gr, Gt , and R. Rain absorption also becomes a significant factor at radio
frequencies above 10 GHz. The required transmitter power is relatively independent of satellite
altitude when the antenna beamwidth is set to just illuminate the indicated coverage area. At low
altitudes the required transmitted power is reduced in the Earth coverage case because the area in
view of the satellite is smaller.
Let us consider a transmitter located at the center of a sphere of radius S, radiating power PL l
isotropically, and thus uniformly illuminating the surface of the sphere. The power flux density, Wf,
received on the sphere's surface is the radiated power divided by the area of the sphere, that is,
PLl/4πS2. The radiated power is the transmitter power, P, reduced by the line loss, Ll, between the
transmitter and the antenna.
If the transmitting antenna has a narrow beamwidth, the power flux density is increased by the
transmitting antenna gain, Gt defined as the ratio between the power radiated to the center of the
coverage area and the power radiated by an isotropic (omnidirectional) antenna. The received flux
density is reduced by the transmission path loss, La, which includes atmospheric and rain
absorption. The power flux density then becomes:




where Wf is typically expressed in W/m2. PLlGt, is called the effective isotropic radiated power, or
EIRP, in watts. In Figure 5.14, the same EIRP and received power flux density are produced in two
ways, one using a high-power transmitter, the other a low-power transmitter. The difference
between them is that the approach using a low-power, high-gain antenna illuminates only a limited
coverage area, which may or may not meet the mission requirements.

<!-- PDF_PAGE: 87 -->

Link Budget Analysis                                                                          87




                     Figure 5.14: Trade-off between antenna gain and transmitter power [13]




The received power, C, is Wf times the effective receive antenna aperture area, Ar. Here Ar is equal
to the physical aperture area, πD2/4, times the antenna efficiency, η. The efficiency, η, is a figure of
merit between 0 and 1, and it is a function of various imperfections in the antenna, including
deviations of the reflector surface from theoretical, feed losses, and aperture blockage.

Substituting for Wf and Ar , we obtain




where Dr is the diameter of the receive antenna.
The antenna gain may also be defined as the ratio of its effective aperture area, A r, to the effective
area of a hypothetical isotropic antenna, λ2/4π, where λ is the wavelength of the transmitted signal.
For the receive antenna


                                                         λ          λ

Substituting again, we obtain

                                           λ


where C is the received power and ( /4πS)2 denotes the space loss, Ls.

<!-- PDF_PAGE: 88 -->

88                                                                          Link Budget Analysis



In digital communications, the received energy per bit, Eb , is equal to the received power times the
bit duration, or



where C is in W, R is the data rate in bps, and Eb is in W·s or J.
The noise power at the receiver input has usually a uniform noise spectral density, No, in the
frequency band containing the signal. The total received noise power, N, is then NoB, where B is
the receiver noise bandwidth. B is determined by the data rate and the choice of modulation and
coding, as discussed later in this chapter. No and N are related to the system noise temperature, Ta,
by:



and



where No is in W/Hz, N is in W, k is Boltzmann's constant = 1.380 x 10-23 J/K, Ts is in K, and B is
in Hz. By combining these last equations it is possible to obtain the original link equation.
The system noise temperature, TS is the sum of a number of individual contributions from various
sources. We have divided the noise sources into two groups. Those originating ahead of the
antenna aperture (e.g., in the atmosphere) we be called the antenna noise temperature, Tant.

These noise sources are external to the ground station, except for the antenna itself, and include:

      •   Galactic noise

      •   Noise radiated by clouds and rain in the propagation path

      •   Solar noise (either in the antenna main beam or in sidelobes)

      •   Presence of the Earth (typically 290 K) in a sidelobe

      •   Man-made noise (either in the antenna main beam or in sidelobes)

      •   Contribution of nearby objects, buildings, etc.

      •   Temperature of blockage items in antenna subsystem such as booms or feeds.


The noise figure, F, of the receiver is defined as:




where Tr, is the noise temperature of the receiver itself, and T 0 is a reference temperature, usually
290 K.
The noise figure is often expressed in dB.

Adding the antenna noise and the receiver noise we obtain the system noise temperature, Ts. To

<!-- PDF_PAGE: 89 -->

Link Budget Analysis                                                                       89



find Ts we add the noise contribution from the transmission line and the bandpass filter which
connect the antenna to the receiver's low-noise amplifier. Thus:




where Lr is the line loss between the antenna and the receiver, expressed as a power ratio. The
second term is the noise contribution from the transmission line, and the third term is the
contribution from the receiver. The receiver noise temperature is the sum of these two terms. These
noise temperatures are referred to the antenna terminal by dividing by L r.
In the future, improvements in design of low-noise amplifiers will reduce the receiver noise figures,
especially at higher frequencies.




5.6. Link Budget procedure
The link budget provides the designer with values of transmitter power and antenna gains for the
various links in the system. It is therefore one of the key items in a space system design, revealing
many characteristics of the overall system performance.

A detailed procedure for a downlink design is as follows:

    1. Select carrier frequency, based on spectrum availability and FCC allocations.

    2. Select the satellite transmitter power, based on satellite size and power limits.

    3. Estimate RF losses between transmitter and satellite antennas.

    4. Determine the required beamwidth for the satellite antenna, depending on the satellite
       orbit, satellite stabilization, and ground coverage area.

    5. Estimate the maximum antenna pointing offset angle, based on coverage angle, satellite
       stabilization error, and stationkeeping accuracy.

    6. Calculate transmit antenna gain toward the ground station.

    7. Calculate space loss. This is determined by satellite orbit and ground-station location.

    8. Estimate propagation absorption loss due to the atmosphere dividing the zenith attenuation
       by the sine of the minimum elevation angle from the ground station to the satellite.

    9. Select the ground station antenna diameter and estimate pointing error. If autotracking is
       used, let the pointing error be 10% of the beamwidth. Calculate the antenna beamwidth.

    10. Calculate the receive antenna gain toward the satellite.

    11. Estimate the system noise temperature (in clear weather).

<!-- PDF_PAGE: 90 -->

90                                                                            Link Budget Analysis



     12. Calculate Eb/N0 for the required data rate.

     13. Look up Eb/N0 required to achieve desired BER for the selected modulation and coding
         technique.

     14. Add 1 to 2 dB to the theoretical value for implementation losses.

     15. Estimate the degradation due to rain.

     16. Calculate the link margin, the difference between the expected value of Eb/N0 calculated
         and the required Eb/N0 (including implementation loss).

The downlink calculation described above provides the signal-to-noise ratio at the ground station
based on the assumed parameters for the downlink. In order to establish the performance of a
communication link Earth-to-Earth, it is necessary to do the same calculation on the uplink from
the ground station to the satellite. The overall link performance can then be predicted on the basis
of the design of the satellite communication payload.
The order of the steps outlined above will depend on which parameters are specified. For instance,
one might start with link margin and solve for transmitter power. The uplink design is performed in
the same way, except the receive antenna beamwidth may depend on the Earth-coverage
requirement rather than on size or pointing limitations.




5.7. QB50 Link Budget analysis
Link budget analysis is one of the most relevant investigations; by this analysis it is possible to
understand signal quality and especially if communication architecture is feasible to achieve
mission requirements.
In the following paragraphs there is the downlink and uplink analysis for UHF/VHF and S-band
systems. STK played an important role for the understanding of some values. The link budget tool
was widely used, obtaining detailed outputs to increase analysis reliability. To evaluate some other
values it was also used the AMSAT/IARU Annotated Link Model System spreadsheet and some
results coming from similar CubeSat communication systems of other missions.

In a first step, it is mandatory to define orbit characteristics. This part is very important in order to
evaluate propagation losses. Afterwards, frequency is also fundamental in order to fix a lot of
communication link losses. Defining these two input data it is possible to obtain a lot of detailed
link budget information.
Below AMSAT/IARU spreadsheets are shown concerning orbit characteristics and frequencies
selection. We can observe the presence of the 20 deg constraint of minimum elevation angle
estimated in previous paragraphs. For this first section the most important outputs are surely the
calculations of slant range and path losses.

<!-- PDF_PAGE: 91 -->

Link Budget Analysis                                                                                  91




                  Figure 5.15: AMSAT/IARU spreadsheet concerning orbit characteristics [21]




In the frequencies selection spreadsheet there are many options; for UHF/VHF systems it is chosen
an uplink frequency of 145.8 MHZ and a downlink frequency of 437.45 MHz, while for the S-band
system there is an uplink frequency of 2 GHz and a downlink frequency of around 2.4 GHz.




         Figure 5.16: AMSAT/IARU spreadsheet concerning frequencies selection (UHF/VHF system) [21]

Communication systems are characterized by choice of transmitters and receivers for the ground
and space segments. These choices influence also directivities, by the antenna gains, and antenna
losses, due to pointing or polarization. In the following paragraphs the main characteristics are
summarized for devices used for both strategies, and link budget analysis results are also discussed.

<!-- PDF_PAGE: 92 -->

92                                                                         Link Budget Analysis



5.7.1. Main Communication Link Losses
The Free-Space Path Loss, or Path Attenuation, is the loss in signal strength of an electromagnetic
wave that would result from a line-of-sight path through free space, with no obstacles nearby that
cause reflection or diffraction. It does not include factors such as the gain of the antennas used at
the transmitter and receiver, nor any loss associated with hardware imperfections. This loss is a
major component in the analysis and design of the link budget of a telecommunication system.
Free-space path loss is proportional to the square of the distance between the transmitter and
receiver, and it is also proportional to the square of the frequency of the radio signal.
The equation for FSPL is




where d is the distance from the transmitter (in meters), f is the signal frequency (in Hz) and c is
the speed of light in vacuum, 2.99792458 × 108 meters per second.
Using STK it is possible to evaluate this loss for each passage at every time. According to
evaluation by STK and AMSAT/IARU spreadsheet, these losses are 136.6 dB for the VHF uplink,
144.1 dB for the UHF downlink, and around 157 dB for both S-band links.

Cables and radio frequency waveguides have losses related to distance. This path loss will be in
terms of dB per unit distance. For the ground station the Belden 9913 cable is selected, which is
widely diffused for academic ground stations, while for the space segment the RG-188/AU cable is
used. By estimating the cable length required to connect the antenna system with the control
computer it is possible to evaluate the right attenuation that depends also on signal frequency. The
results will be presented in the following paragraphs in the downlink and uplink budget tables.
Another loss is the antenna pointing loss. This is the amount of signal loss due to inaccurate
antennas pointing. To determine the expected amount of pointing loss, we have to consider such
things as antenna position encoder accuracy, resolution of position commands, and autotrack
accuracy. Pointing loss is often one of the most common causes of link failure. This is usually due
to inaccurate commanded position of the antenna, but it can also be caused by a faulty position
encoder. In Figure 5.17 it is possible to distinguish all the important angles that are involved in a
possible antennas misalignment. For the uplink antenna system, the ground station has an estimated
pointing error (θ1) of 5 deg with a relative loss of 0.3 dB for the VHF. For S-band, and its narrow
beamwidth, it is not possible to accept an error of 5 deg, hence the estimated pointing error
decreases to 1 deg, and the attenuation increases to 0.5 dB. Maintaining same pointing errors for
the downlink (θ4) results are not so different with respect to uplink. For the other angles (θ 2, θ3)
between S/C antenna symmetry axis and vector from S/C to ground station are assumed values of
60 deg are assumed for both strategies and links. For the space segment the pointing losses turn out
to be negligible. In order to receive the maximum EIRP, and to have minimum loss, both receiving
and transmitting antennas have to be perfectly aligned (Figure 5.18).

<!-- PDF_PAGE: 93 -->

Link Budget Analysis                                                                                     93




 Figure 5.17: Angles for the Estimated Pointing Error and Angles between S/C antenna symmetry axis and vector from
                                  S/C to ground station for uplink and downlink [21]




               Figure 5.18: Representation of Perfect Alignment and Miss-Aligned configurations [22]




The next loss is the polarization loss. The transmitting and receiving antennas are usually polarized
to permit frequency reuse. Satellite links usually employ circular polarization, although linear
polarization is occasionally used. In the case of circular polarization, the design engineer will use
the axial ratio of the transmit and receive antennas to determine the maximum and minimum
polarization loss. The maximum loss is usually small enough (typically 0.3 dB) so that it can be
ignored by the maintenance engineer. However, there are a couple of special cases that the
maintenance engineer will need to keep in mind. If the ground antenna is capable of being
configured for either LHCP or RHCP, a misconfiguration of the polarization will result in a
significant loss, of the order of 20 dB or more. Moreover, polarization is affected by atmospheric
conditions. If there is rain in the area, polarization loss may increase. More information on that is
provided in the discussion of rain fade.
In order to transfer maximum power between a transmit and a receive antenna, both antennas must
have the same spatial orientation, the same polarization sense and the same axial ratio. When the
antennas are not aligned or do not have the same polarization, there will be a reduction in power
transfer between the two

<!-- PDF_PAGE: 94 -->

94                                                                                            Link Budget Analysis



antennas. This reduction in power transfer will reduce the overall system efficiency and
performance.
When the transmit and receive antennas are both linearly polarized, physical antenna misalignment
will result in a polarization mismatch loss. The actual mismatch loss between a circularly polarized
antenna and a
linearly polarized antenna will vary depending on the axial ratio of the circularly polarized antenna.
If polarizations are coincident no attenuation occurs due to coupling mismatch between field and
antenna, while if they are not, then the communication can't even take place. Using AMSAT/IARU
spreadsheet it is possible to calculate the polarization loss. One of the main parameters turns out to
be the angle between transmit and receive major axes, known as Polarization angle (θ). This loss,
for the UHF/VHF and S-band links, turns out to be around 0.2 dB, assuming θ equal to 90 deg.




     Figure 5.19: Polarization Loss Calculator (on the left) and representation of Polarization angle θ (on the right) [21]




Atmospheric loss, as stated before, is the amount of signal that is absorbed by the atmosphere as the
signal travels from the satellite to the ground station. It varies with signal frequency and the signal
path length through the atmosphere, which is related to the elevation angle between the ground
station and the spacecraft. Theoretically, the amount of signal absorbed by rain could also be
considered as an atmospheric loss, however, since rain fade can be quite large and unpredictable, it
is given its own variable in the link budget. By means of STK and AMSAT/IARU spreadsheet, it is
possible to predict the corresponding amount, and it turns out to be the same both for the downlink
and the uplink, and equal to 1.1 dB, assuming for both strategies a minimum elevation angle of 20
deg.

The ionospheric losses, discussed in previous paragraphs, turn out to be different for uplinks and
downlinks, they are strongly influenced by frequency, and their values are around 0.8 dB for
downlinks and 0.4 dB for uplinks.

One of the last losses is rain attenuation, that was analyzed in detail. The UHF/VHF system is
characterized by a low frequency to have a significant rain attenuation. Only the S-band could be
affected by this kind of loss. Using the equation of paragraph 5.2.3, with S-band system
specifications, it is possible to estimate the rain attenuation. It is considered the worst case, with a
Rp value of 50 mm/h.

The first step is the determination of the specific attenuation , which is usually calculated by

<!-- PDF_PAGE: 95 -->

Link Budget Analysis                                                                          95



where a and b are coefficients which depend on frequency and polarization. In this case, due to
circular polarization, the values for a and b are different coefficients with respect to vertical and
horizontal ones.




By these coefficients, turns out to be equal to 0.02 dB/km. Once the specific attenuation is found,
the total attenuation is determined as



where L is the effective path length of the signal through the rain.
Assuming a rain height of 4 km and a minimum elevation angle of 20 deg, L turns out to be equal
to 11.7 km. Adding margins, it is possible to state that the total attenuation for the S-band system is
around 0.5 dB. This result expresses the low influence of rain attenuation for S-band signal quality.
Like the UHF/VHF system, where such an attenuation is totally negligible, the S-band system
frequency appears to be too low to constitute a significant problem in the system link budget.




5.7.2. Link Margins and Thresholds
The Link Margin, measured in dB, is the difference between the receiver's sensitivity (i.e., the
received power at which the receiver will stop working) and the actual received power. A 20 dB
link margin means that the system could tolerate an additional 20 dB of attenuation between the
transmitter and the receiver, and it would still just barely work.
It is typical to design a system with at least a few dB of link margin, to allow for attenuation that is
not modeled elsewhere. A system with a negative link margin would insufficient to transfer data,
usually this means a better receiver is needed, with improved sensitivity. To increase a link margin
it is often required to increase the system complexity, using more expensive devices and power
consumption.
CubeSats require low technology systems, with low power consumption. Usually, for low cost
systems, the minimum link margin is assumed to be around 10 dB; this value could decrease for
professional systems and deep space missions. Taking into account a required minimum link
margin of 10 dB, it will be possible to understand the strategy feasibility.

The system link margin is mainly based on the threshold Eb/N0, which is the value of Eb/N0
theoretically required for the modulation method selected plus any additional losses caused by
imperfections in the demodulator design.
Generally, in electronics and telecommunications, modulation is the process of varying one or
more properties of a periodic waveform, called the carrier signal, with a modulating signal which
typically contains information to be transmitted. In digital modulation, an analog carrier signal is
modulated by a discrete signal. Digital modulation methods can be considered as digital-to-analog
conversions, and the corresponding demodulation or detection as an analog-to-digital conversion.
Signals in a communication link can be: voice (telephony, radio broadcast, audio portion of TV
broadcast); data; video. The base band signal is subject to base band processing to convert the
signal to a form suitable for transmission (e.g., band limiting of speech signals to 3000 Hz in

<!-- PDF_PAGE: 96 -->

96                                                                             Link Budget Analysis



telephony, coding of digital signals). The processed base band signal then modulates a high
frequency carrier, suitable for propagation over the transmission link. The demodulator on the
receiver end recovers the base band signal from the received modulated signal.
In the case of digital transmission, the quality of the recovered speech signal depends on the
number of bits transmitted per second and the Bit Error Rate (BER). The maximum allowed BER
for a good quality speech signal is considered to be 10−4, i.e. approximately 1 bit error in 10 kB,
though a BER of 10−5 or better is common.
Going back to the Eb/N0 threshold due to selected modulation, it is possible to state that, for the
VHF system, the AFSK/FM modulation type is chosen, with BER of 10−5, and Eb/N0 threshold of
23.2 dB. For UHF, which is used for the downlink in the first strategy, the QPSK modulation type
is used, with BER of 10−5, and Eb/N0 threshold of 9.6 dB. The second strategy, the S-band system,
has the same modulation type of the UHF system for both links.
In the following paragraphs the link budget tables are presented with final results. The results are
divided in three sub-tables relative to Ground Segment, Spacecraft and Path.




5.7.3. UHF/VHF System Link Budget
After initial One-to-one simulations an analysis on the link budget was conducted in order to
investigate the communication link quality. In this paragraph the UHF/VHF system is examined by
studying the uplink and downlink budget. In the following tables we present the evaluation of the
path losses, the choices for the space and ground segments, and especially the link budget results,
like the link margin and other interesting outputs.
As it has been discussed before, for UHF/VHF the rain attenuation is negligible, and the free-space
path loss, or simply path loss, represents the main loss. For the ground station, there is a
transmitted power of 10 W, that is more than 10 times the spacecraft transmitted power. A Yagi-
Ugi Antenna was used with a gain of 16.3 dBi, with EIRP of 22.3 dBW. For the uplink the data rate
is quite low, it is around 1200 kbps, while for the downlink it is close to 9600 kbps.
Below there is a complete link budget analysis, with two tables for the link details. The system link
margin are highly satisfactory because it is higher than the required minimum link margin of 10
dB, so that it guarantees the full feasibility of this kind of communication strategy.


                             Table 5.4: Uplink budget for the UHF/VHF system

<!-- PDF_PAGE: 97 -->

Link Budget Analysis                                                                         97




                            Table 5.5: Downlink budget for the UHF/VHF system




5.7.4. S-band System Link Budget
After the examination of the UHF/VHF system, S-band strategy is now analyzed. In the following
tables we present device characteristics for selected space and ground segments, the evaluation of
path losses, and as before the link budget results, like the link margin and other interesting outputs.
As it has been evaluated before, for S-band the rain attenuation is present, though not so relevant,
and the path loss always represents the main loss. For the ground station, there is a transmitted
power of 35 Watts, higher with respect to an UHF/VHF Yagi-Ugi antenna. The spacecraft
transmitted power is of 1 Watt as for the UHF/VHF system. An antenna was used with a gain of
30.6 dBi, with EIRP of 42.1 dBW. The data rate is high, and it is around 1 Mbps for both links.
Below there are two tables for the main link specifications. For the downlink, the system link
margin is not satisfactory because it is lower than the required minimum link margin of 10 dB, so
that it doesn’t guarantee the full feasibility. This result undermines the use of this system. The

<!-- PDF_PAGE: 98 -->

98                                                                               Link Budget Analysis



selected ground station requires more power in comparison with the first strategy. For the space
segment, it is not possible to change dramatically the utilized devices because of CubeSat
requirements. Devices utilized for both strategies are typical for these applications, and power
consumption constraints on board should create some problems for the communication.


                               Table 5.6: Uplink budget for the S-band system




                              Table 5.7: Downlink budget for the S-band system




5.7.5. Comparison with other CubeSat projects
Evaluated link budget is highly reliable, the obtained values turn out to be equal, or closer, to other
similar projects. This similarity is a strong point for this kind of analysis, because it validates
achieved results. Surely one of the similar projects is the CySat Project, this is a team of
undergraduate and graduate students from Iowa State University committed to the design and
development of a pico-satellite in accordance with the CubeSat standard. It is designed to use

<!-- PDF_PAGE: 99 -->

Link Budget Analysis                                                                        99



UHF/VHF bands with similar frequencies to first strategy analyzed. Satellite antenna gain turns out
to be equal to proposed QB50 UHF/VHF system, and also the Ground antenna gain is almost the
same (12 dB instead of 14.1 dB). System powers are the same of QB50 proposed solution for both
segments, the satellite transmitter power turns out to be 1 W, and Ground transmitter power is 10
W. But CySat CubeSat is not the only one, link budgets of other projects turn out to be close to
proposed analysis. The Indian INASAT-1 CubeSat is another example of project which has similar
used devices and link budget values, and a huge quantity of AMSAT datasheets can also validate
results evaluated by this analysis. Link budget values appears to be the same, or very close, with
respect to a high number of other projects. This equivalence, and the use of selected
communication devices, highly utilized in past CubeSat missions, guarantee an high reliability of
obtained analysis outputs.




5.7.6. Results and selected architecture
Resuming the results of the link budget analysis, especially analyzing in detail the link margins of
suggested solutions, it is possible to select the communication architecture for the next
constellation analysis.
The UHF/VHF system guarantees a full achievement of mission requirements, link margins are
above the low cost system threshold of 10 dB, and it is also one of the most qualified technologies
for CubeSat mission. S-band could be an interesting option, but requires an increase of complexity
for both segments (space and ground segments). At present this increase in complexity could be in
conflict with CubeSat requirements, with S-band it is not possible to achieve the required minimum
link margin of 10 dB for the downlink. In order to increase this margin we should use other
devices, especially for the space segment, however, at present, this is not so compatible with the
CubeSat concept. But is also true, that a lower bit rate results in a higher margin. Therefore a
possible solution for S-Band could be the reduction of the bit rate from 1 to 0.5 mbps, finding in
this way a compromise, between S-Band link margin and high data rate. Eventually, to continue the
analysis, and to extend it to the constellation problem, it is necessary to choose an architecture for
next studies. After this first part of analysis it is possible to select the UHF/VHF system with a
rotator mechanism as the baseline solution. A Yagi Antenna will be used for the ground stations,
and a UHF/VHF transceiver with an omnidirectional antenna for the CubeSat. For the space
segment two GOMSPACE company devices will be selected: the NanoCom U482C UHF/VHF for
the transceiver and the NanoCom ANT430 for the omnidirectional antenna.

<!-- PDF_PAGE: 100 -->

100                                                                        Link Budget Analysis




      Figure 5.20: Selected solution for the following Constellation Analysis [23][18]

<!-- PDF_PAGE: 101 -->

Constellation Analysis                                                                        101




6 Constellation Analysis



6.1. Constellation issues
Some very interesting CubeSat constellation concepts have been proposed over the years in
different scientific papers, and always there are some issues that working groups have to fix. The
main reason for delaying CubeSat projects usually seems to be the amount of novelty introduced by
these projects, with problems that are generally different from other missions.
One of the most relevant problems is that each CubeSat can communicate with one ground station
per time, and each ground station can follow only one CubeSat during its transit. The presence of a
large number of satellites, close to each others, could be a huge problem for presence of
communication overlaps, especially if it is not possible to track more than one CubeSat per time.
Another significant problem is the variation of the constellation geometry with time during mission
lifetime. After deployment CubeSats are very close to each others, but just after one month, there is
a distributed formation of them. The preferred deployment scenario is based on the assumption that
the upper stage engine can be operated in continuous low-thrust mode. Each CubeSat will have a
different velocity through the increase in velocity of the upper stage in the time between each
deployment. These differences in the velocity assist the spreading along the orbit since the first
deployed CubeSat, last one in the string of pearls, has the lowest velocity whereas the last deployed
satellite, leader of the string, has the highest. The difference in velocity also leads to a slight
spreading in altitude which reduces even further the collision risk between the CubeSats. Another
possibility for deployment could be that CubeSats will be deployed one after another in the local
horizontal plane in the four perpendicular directions. The risk of collisions is reduced through the
additional velocity component in the along-track direction. It is possible to adjust the additional
velocity applied to each CubeSat during deployment by altering the spring load inside the dispenser
system. Since each CubeSat will have a different weight and the spring loading will not be totally
homogeneous, a non-uniform distribution of the deployment velocity around the mean value is
expected. However the small changes have only small effects on the spreading of the CubeSats.
CubeSats tend to align up in orbit ordered by the ballistic coefficient with the lightest CubeSat at
the front. Therefore it is favorable to directly deploy the CubeSats ordered according to the value of
this coefficient to reduce the risk of collision when one satellite “overtakes” another.
In around one month CubeSats can be considered equally distributed around Earth. The CubeSats
cover all latitudes with the potential to measure in the night and day-side of the Earth
simultaneously.
The configuration difference with time is one of the issues, which has to be fixed with simulations,
in order to obtain good outputs and reliable analysis results.

<!-- PDF_PAGE: 102 -->

102                                                                                       Constellation Analysis




                                                                         For Educational Use



      Figure 6.1: STK 3D visualization of QB50 network after around one month of lifetime, obtained with STK




6.2. STK setting
The first step is the introduction of the network of CubeSats in the STK scenario. Selecting a HPOP
propagator, it is not possible to use the Walker constellation tool. The Walker Tool makes it easy to
generate a Walker constellation using the Two Body, J2, J4, or SGP4 orbit propagators. The
original satellite that you defined is referred to as the seed satellite, while the satellites generated
using the Walker tool are referred to as the children. If the seed satellite has sub-objects such as
sensors, the sub-objects are also created for each of the child satellites. Unfortunately this useful
tool cannot be used for these STK scenarios, and satellites are obtained creating a first mother-
CubeSat, and cloning it. Properties of other CubeSats differ only in true anomaly angle. Each
satellite has an angular distance of 7.2 deg from the previous one in the operating configuration
with uniformly distributed CubeSats around Earth. The altitude of the constellation for the initial
phase is 350 km, and orbit inclination is 98 deg. The first CubeSat is assumed to be in an almost
circular orbit (due to drag effect) at true anomaly of 155 deg. As it has been previously discussed in
the one-to-one problem, orbits decay slowly during the first part of lifetime. All orbit dynamic
properties don’t change with respect to results obtained in previous analysis.
The following table summarizes the main characteristics used in the simulations for the network
mother-CubeSat. Children CubeSats differ only in true anomaly angle. Within the Constellation
analysis, there are several possible configurations for space and ground segments. In next
paragraphs these configurations will be explained and analyzed.

<!-- PDF_PAGE: 103 -->

Constellation Analysis                                                                        103



                         Table 6.1: Mother-CubeSat parameters for Constellation Scenario




                             Parameter                         Value

                             Altitude                          350 km

                             Eccentricity                      ~0

                             Inclination                       98 deg

                             Argument of perigee               0 deg

                             RAAN                              40 deg

                             True anomaly                      155 deg

                             Propagator                        HPOP

                             Drag Coefficient                  2.3

                             Area/Mass ratio                   0.005 m2/kg

                             Satellite Mass                    2 kg




6.2.1. Analyzed CubeSat configurations
In this chapter we present a great number of analyses performed on different configurations for
space and ground segments. Analyzing a wide variety of cases and possibilities, it is possible to
describe in depth the behavior of a QB50 CubeSat network. The space segment is represented by
the 50 CubeSats around the Earth in a quasi-circular orbit. As it has been discussed before there are
several configurations depending on the lifetime phase. After deployment phase, CubeSats are
close to each others, and angular distance in true anomaly is short. During mission time, angular
distances between near CubeSats increase, and there is a complete coverage of all latitudes by the
satellite network.
For the simulations we assume two configurations. The first one, denoted by Group 1, would
describe the large distance configuration for CubeSats. There are five CubeSats with an angular
difference in true anomaly angles of 72 deg. These satellites are called respectively: CS1, CS11,
CS21, CS31, and CS41.
The second one is constituted by five CubeSats closer to each other, with an angular difference in
true anomaly of 7.2 deg. This is a very interesting shape, especially for the study of communication
overlaps. This second configuration is called Group 2. These other satellites are called respectively:
CS1, CS2, CS3, CS4, and CS5.
In next paragraphs a couple of the presented simulations take into account these two possible
configurations, and the results are very interesting. These two possible kinds of space segments
have to be combined with a ground segment. Also for ground segment there are more options,
varying selected ground and space segments, it is possible to conduct very intriguing simulations,
and to obtain useful results.

<!-- PDF_PAGE: 104 -->

104                                                                                          Constellation Analysis




                                            a)                               b)


  Figure 6.2: CubeSats configurations: a) Group 1, angular distance of 72 deg; b) Group 2, angular distance of 7.2 deg




6.2.2. Ground segment configurations
For ground stations there are several configurations. Two analyses will be mainly considered in
depth in next paragraphs. The first one deals with a communication study of some established
ground segments, characterized by different geographic areas. The second one conducts a
communication analysis with a combination of ground stations that vary in number and positions.
The number of ground stations will vary between 1 and 25 ground stations, and positions will be
selected by a ground station list of all CubeSat flying universities and institutes (Table 6.2), that
could supply a ground station in next months for the mission.


                               Table 6.2: Ground Station list of CubeSat flying institutes

Ground Station                                                                           Latitude        Longitude

Universidad de Buenos Aires                                                              -34.599214      -58.373133

The University of Adelaide                                                               -34.920141      138.606967

University of New South Wales                                                            -33.916752      151.230013

University of Sydney                                                                     -33.890492      151.191376

Graz University of Technology                                                            47.069493       15.450958

University of Applied Science Technikum Wien                                             48.239309       16.378627

Lessius College                                                                          51.208174       4.418163

Royal Meteorological Institute of Belgium (RMIB)                                         50.814612       4.36821

Royal Observatory of Belgium                                                             50.798707       4.358779

University of Liège                                                                      50.639772       5.575705

<!-- PDF_PAGE: 105 -->

Constellation Analysis                                                              105



von Karman Institute                                              50.755029    4.385684

Instituto Federal Fluminense                                      -21.763645   -41.33626

York University - Toronto                                         43.772798    -79.504416

Beihang University                                                39.980113    116.342719

Harbin Institute of Technology                                    39.912633    116.270685

Nanjing University of Science and Technology                      32.028671    118.85798

Northwestern Polytechnical University                             32.013898    118.84562

Zhejiang University                                               30.26118     120.125191

National University of Defense Technology                         30.260735    120.125234

Czech Technical University in Prague                              50.101602    14.390734

VZLU                                                              50.10924     14.484587

Aalborg University                                                57.014922    9.987041

NARSS, University of Tartu                                        58.380985    26.719455

Addis Ababa Institute of Technology (AAiT)                        9.040139     38.764472

Aalto University                                                  60.226516    24.897366

École Polytechnique                                               48.714143    2.211081

Institut Supérieur de l’Aéronautique et de l’Espace ISAE          43.56671     1.475401

Institut Supérieur Des Sciences Et Technique (INSSET)             49.848831    3.285398

Laboratoire Interuniversitaire des Systèmes Atmosphériques LISA   48.861101    2.347784

MinesParisTech                                                    48.845768    2.339741

Fraunhofer Institute for Physical Measurement Techniques          48.010367    7.834954

TU Dresden                                                        51.028683    13.731658

University of Applied Sciences Bremen                             53.071133    8.803124

Democritus University of Thrace / Space Research Lab              41.060715    24.979706

University of Patras                                              38.289499    21.78571

Anna University                                                   11.167413    76.948882

Dublin Institute of Technology                                    53.338689    -6.266205

The Space laboratory of the Herzliya Science Center               32.140734    34.894867

Department of Physics – University of Trieste                     45.651008    13.779058

University of Rome “LA SAPIENZA”                                  41.902628    12.51179

<!-- PDF_PAGE: 106 -->

106                                                                            Constellation Analysis



Korea Advanced Institute of Science and Technology                         36.37071     127.360325

Seoul National University                                                  37.461233    126.949368

Kaunas University of Technology                                            54.89902     23.914132

Space Science and Technology Institute                                     8.626169     77.037821

Delft University of Technology                                             51.997565    4.374526

PERUVIAN CONSORTIUM                                                        -16.341226   -71.325073

Space Research Center of Polish Academy of Sciences                        52.223173    21.001339

University of Porto                                                        41.147379    -8.614669

Institute of Space Science and the Romanian Space Agency Research Center   41.38093     -8.743172

Samara State Aerospace University                                          53.229057    50.204544

University of Novi Sad                                                     45.238152    19.83284

University of Zilina                                                       49.202892    18.754753

Universidad Politécnica de Madrid                                          40.44889     -3.719046

University of Khartoum                                                     15.495867    32.559857

National Cheng Kung University                                             22.996946    120.21681

Istanbul Technical University / Air Force Academy                          41.104611    29.021369

Middle East Technical University                                           39.891958    32.782381

National Technical University of Ukraine                                   50.449635    30.530777

National Aerospace Educational Center of Youth named after А.М. Makarov    48.463816    35.043526

Cranfield University                                                       52.073466    -0.627301

MSSL University College London                                             51.175038    -0.420342

University of Leicester                                                    52.615921    -1.128809

University of Surrey                                                       51.24279     -0.589596

Stanford University                                                        37.42348     -122.165666

FPT Technology Research Institute - FPT University                         10.617418    106.937255

<!-- PDF_PAGE: 107 -->

Constellation Analysis                                                                            107



For the first analysis there are four groups of ground segments. Some ground stations of the Table
6.2 were selected to arrange four groups characterized by different geographic locations. These
groups are:

- Group 1, Asia north/south distribution ;
- Group 2, Northern hemisphere west/east alignment;
- Group 3, America north/south distribution;
- Group 4, Europe cluster




                                                     For Educational Use




               Figure 6.3: Ground Segment groups for Constellation Analysis (obtained with STK)




6.2.3. Analyzed Scenarios
In this paragraph the word Scenario stands for a study with particular conditions. Some of the
results are obtained by STK software, but computations are implemented also in MATLAB scripts,
in order to increase the realism level and to achieve sophisticated outputs. Input data for MATLAB
scripts are almost always derived from STK tools, especially by access tool.

The first analyzed scenario is called Scenario 0, this isn’t a multiple satellites or ground stations
scenario. This scenario analyzes the communication behavior for a single CS-GS simulation. This
is obviously an ideal case, that doesn’t take into account the presence of other CubeSats, and
especially of communication overlaps. Results are highly satisfactory: the following Figure 6.4
shows an example of the kind of outputs that can be obtained at the end of the analysis. Below
there is the example of GS group 1 (Asia N/S) with CS group 1. Here, the highest dashed line (red
line) identifies the minimum data per day obtained in first 100 lifetime days. If it is above the other
two dashed lines (lower for 4 Mb/day, higher for 10 Mb/day), the communication links reach the
mission requirements. If the red dashed line is below the others, mission requirements are not
satisfied, and number of ground stations or other expedients have to be used. More than 150 hours

<!-- PDF_PAGE: 108 -->

108                                                                                    Constellation Analysis



of contact time have been accumulated, and the minimum data per day line is more than 25 Mb
over 10 Mb threshold. There aren’t high oscillations in the data per day function, and the
differences between different CubeSats are not significant. For this scenario, and also for the next
ones, the minimum contact time is 20 seconds. If the access is below this threshold, contact is not
taken into account for calculations.




                    Figure 6.4: Scenario 0 output for GS group 1 (Asia N/S) with CS group 1




Scenario 1 introduces a sequential contact to all possible CubeSats from group 1, assuming partial
contacts in the case of overlaps. Ground stations track satellites assuming an ideal antenna rotator,
which has an instantaneous rotation between last pointing end and the following one in the opposite
side, for the incoming new CubeSat.
As it is shown in the following double plot Figure 6.5, accumulated contact time is shorter with
respect to scenario 0, contact time decreases, and fluctuations are huge. Low peaks are very
dangerous because they lower the minimum data per day dashed line, under the thresholds of 10
Mb/day in this case. The example case shown is GS group 1 (Asia N/S) with CS group 1 again.

<!-- PDF_PAGE: 109 -->

Constellation Analysis                                                                        109




                    Figure 6.5: Scenario 1 output for GS group 1 (Asia N/S) with CS group 1


Scenario 2 is the following one, with a fixed antenna rotation time of 1 minute. Generally it is very
similar to the previous one for the general characteristics, but it is less ideal. This is easily
understandable from the plots shown below: minimum data per day line turns out to fall below the
minimum 4 Mb/day line for this case, while in Scenario 1 it was in the midle between the 4 Mb/day
and 10 Mb/day lines.




                    Figure 6.6: Scenario 2 output for GS group 1 (Asia N/S) with CS group 1

<!-- PDF_PAGE: 110 -->

110                                                                                    Constellation Analysis




Scenario 3 is very interesting because there is an optimization of the previous scenario by giving
priority to low accumulated contact time CubeSats. Accesses with a low contact time are neglected
in favour of longer contacts in the case of overlaps. Fluctuations are huge and larger with respect to
other scenarios, and the red dashed line for minimum data per day is the lowest one. The same case
study does not yield good results for this scenario, requirements are far to be reached. Minimum
data per day is below 4 Mb threshold. Accumulated contact time is almost the same for all
CubeSats, there aren’t high differences concluding that the optimization for this parameters is
functional. Contact times decrease and performances are worst in comparison with all previous
scenarios. Therefore it is more suitable to optimizate for daily contact time or transmitted data to
ensure every CubeSat will have the maximum ground station access per day.




                    Figure 6.7: Scenario 3 output for GS group 1 (Asia N/S) with CS group 1



In the Scenario 4 we assumed again an ideal instantaneous rotation time, however, with respect to
other scenarios, in this analysis only the full passes are considered. Passes shorter than a given
threshold and partial contacts are not taken into account. For the example GS group 1 (Asia N/S)
with CS group 1, accumulated contact time decreases a lot due to the skipped accesses compared to
the Scenario 1, and minimum data per day line is above 10 Mb/day dashed line. Requirements turn
out to be satisfied, but the behavior is ideal. By considering a real antenna rotation time, it is
possible to obtain reliable results.

<!-- PDF_PAGE: 111 -->

Constellation Analysis                                                                       111




                   Figure 6.8: Scenario 4 output for GS group 1 (Asia N/S) with CS group 1


In Scenario 5 we consider a fixed antenna rotation time of 1 minute. Results are more reliable in
comparison with Scenario 4, and not so negative. For the case study, it is possible to show that
minimum data per day line is again above other thresolds of 4 and 10 Mb/day. Oscillations are
present but they are not so large like in Scenario 1, Scenario 2 or Scenario 3, and mission
requirements can be reached easily.




                   Figure 6.9: Scenario 5 output for GS group 1 (Asia N/S) with CS group 1

<!-- PDF_PAGE: 112 -->

112                                                                                    Constellation Analysis



The penultimate analyzed scenario is Scenario 6. This new scenario is optimized for summed or
accumulated data rate, and takes into account only full passes. For the same Asia case, minimum
data per day is below 4 Mb threshold, and there are high fluctuations in data per day. CubeSats
have almost the same behavior concerning the accumulated contact time function. There are too
much low peaks that don’t permit this configurations combination to reach mission requirements.
To avoid the presence of these peaks, Scenario 7 makes the scene.
Scenario 6 is optimized for the accumulated contact time information, but this scenario turns out to
be not so reliable to perform analysis due to a bad choice of optimization parameter. Low peaks of
data per day function are very deep, and minimum data per day line is almost always below the
minimum requirement lines of 4 Mb/day and 10 Mb/day. To avoid this kind of problem, in a new
scenario outputs are optimized for the data per day function, and this last scenario gives more
reliable results for subsequent analysis.




                   Figure 6.10: Scenario 6 output for GS group 1 (Asia N/S) with CS group 1




Scenario 7, or Scenario 6mod, as stated before, is obtained by an optimization for daily data rate.
As the previous one, this scenario does not have an ideal antenna rotation time, and in this analysis
only full passes are considered. By the adoption of this scenario it is possible to avoid access with
low peaks of collected data. As shown in the following figure, results are much better with respect
to Scenario 6. For the case of GS group 1 (Asia N/S) with CS group 1, mission requirements are
fully satisfied, and the red dashed line for minimum data per day during first 100 days is well
above mission requirements thresholds. There aren’t high fluctuations in data per day function, and
peaks         are       far       from        communication            requirement         thresholds.
For next analysis, Scenario 7 is the selected one and it is used to explain the communication
behavior.

<!-- PDF_PAGE: 113 -->

Constellation Analysis                                                                        113




                   Figure 6.11: Scenario 7 output for GS group 1 (Asia N/S) with CS group 1




6.3. Communication Overlaps
Overlapping contact windows of individual satellites raise the question of which of these satellites
should be operated first and which is the best solution to avoid this kind of problems. To handle
conflicts with regard to overlapping contact windows, mission design and communication system
optimization come into play.
These particular problems will be investigated deeply in these paragraphs.
For this analysis it isn’t possible to have more than one access per time for a ground station or a
CubeSat, so that one ground station can communicate only with one CubeSat per time, and vice
versa. To understand the analysis of contribution of communication overlaps, this problem was
studied in depth. In a first step it is analyzed the behavior of CubeSat communication for special
combinations. These combinations are characterized by different True Anomaly angles between
close CubeSats. In this first study four configurations of CubeSats are analyzed, with different
angular distances of: 2.5 deg, 5 deg, 7.5 deg and 10 deg. This analysis has multiple satellites but
only one ground station, assumed to be the VKI ground station.

<!-- PDF_PAGE: 114 -->

114                                                                                     Constellation Analysis




                    Figure 6.12: Schematic representation of overlapping access constraints




Conducted STK simulations show the results for two CubeSats with a difference in true anomaly of
2.5 deg, 5 deg, 7.5 deg and 10 deg. In the following pictures results are shown for each value of
true anomaly difference. From the plots it is possible to see that for higher angular distances, there
are shorter overlaps, and that close CubeSat configurations require more ground stations to avoid
overlap problem. As it is shown in the following plots, communication overlap is a significant
problem for communication, especially when satellites are close to each others.
The first plot on the left is for 2.5 deg of angular difference in true anomaly: CubeSat 2 starts the
access and CubeSat 1 is covered by the previous one for almost all its access time. The amount of
data collected by CubeSat 1 is not satisfactory, while CubeSat 2 downloads all data during its
contact window. The situation is better for the 5 deg angular distance, shown in the top right of
Figure 6.13. Communication overlap is shorter and CubeSat 1 can communicate longer with
ground station, but the time dedicated to CubeSat 2 isn’t so much long, and a loss of data could
occur. Increasing angle differences, overlaps decrease. To avoid overlaps, it is mandatory to
increase the angular distances between close CubeSats in the space network. Sometimes this is not
possible, so that it isn’t possible to avoid the presence of overlaps. To avoid problems, mission
design plays an important role, and the significant role of the communication overlaps has to taken
into account, evaluating contact time losses for each CubeSat during the mission lifetime.




                           Figure 6.13: Results of 2 CS and 1 GS Overlap Analysis

<!-- PDF_PAGE: 115 -->

Constellation Analysis                                                                                     115



6.3.1. Minimum angle between CS to avoid overlaps
Iterating STK results, it is possible to find the overlaps end condition corresponding to an average
access time, and the angle between CubeSats. The oblique blue line corresponds to the iteration
output of STK access data, circular marks correspond to 2.5 deg, 5 deg, 7.5 deg and 10 deg,
respectively.
As it is shown in the following plot, assuming an average access time of around 214 seconds
(dashed line), at the intersection point of average access time line and iteration line (blue oblique
line), it is possible to find the ideal overlaps end condition (point I). This condition is characterized
by a difference in true anomaly between CubeSats of 14 deg. This is the ideal end condition
because it is not taken into account the time required to direct again the antenna to the starting
position, to track the next satellite.
Adding the rotation time of 1 minute, it is possible to find another intersection (point R). This new
point coincides with an angular distance of around 18 deg. After this point, increasing angular
distance, contacts will be free from overlaps. This is a very interesting information, because now it
is possible to state that a ground station is able to collect data by a maximum of 20 satellites
without communication overlaps.
This model for communication overlaps will be used in next simulations and analyses, in order to
increase the study reliability and complexity.




     Figure 6.14: Evaluation plot for minimum angular distance in true anomaly to avoid communication overlaps

<!-- PDF_PAGE: 116 -->

116                                                                            Constellation Analysis




6.4. Ground Segments analysis
In this paragraph we present is a detailed study about the communication for the four ground
segments selected before. Just to recall these groups, they are:

                Group 1: Asia N/S;
                Group 2: Northern Hemisphere E/W;
                Group 3: America N/S;
                Group 4: Europe.

In this analysis, previous CubeSat configurations are used in order to understand the access skills
for each combination of configurations. CubeSats are parted in the same two groups as before:

                CS Group 1: CubeSats with angular difference in true anomaly of 72 deg;
                CS Group 2: CubeSats with angular difference in true anomaly of 7.2 deg.

For each ground segment there will be a study for both CubeSat groups. Analyzing the results we
are able to understand if the proposed ground station will satisfy communication mission
requirements. If the minimum amount of data collected in the first 100 days will be more than the
communication thresholds of 4 and 10 Mb/day, the ground station will be able to satisfy QB50
mission requirements. If the minimum value of 10 Mb/day is not achieved, it is mandatory to
improve the selected ground segment, adding more ground stations or increasing latitude of some
ground stations. Next paragraphs show the communication behavior for each ground segment, and
it is possible to find a “Single CubeSat” and an “overall” description of results with very interesting
plots. For this analysis, we assume an orbit inclination of 98 deg, a minimum contact time of 20
seconds, and a data rate of 9.6 kbps.




6.4.1. Asia N/S Ground segment
In this paragraph, Asia N/S Ground segment is analyzed in detail. Next plots give us an idea about
the average data per day collected during mission lifetime. First part of plots shows the results
evaluated for each single CubeSat of CS Group, while the second kind of plot represents the overall
behavior of CubeSats. The second representation could help better to understand the requirements
achievement. If minimum collected data turn out to be below communication thresholds, then the
ground segment must be improved. The following plots are related to CS Group 1. In Figure 6.15
each color corresponds to a different ground station, and one bar is one day of mission lifetime.
Figure 6.15 shows also that there are huge peaks and valleys, which have to be analyzed deeply to
avoid all kind of problems.

<!-- PDF_PAGE: 117 -->

Constellation Analysis                                                                                117




                           CS 1                                             CS 11




                             CS 21                                        CS 31




                                                    CS 41


           Figure 6.15: Data per day for CS Group 1 and Asia N/S Ground segment (Single CS results)

<!-- PDF_PAGE: 118 -->

118                                                                                    Constellation Analysis




             Figure 6.16: Data per day for CS Group 1 and Asia N/S Ground segment (Overall result)




Minimum data per day, as we can see in Figure 6.16, is above the threshold value of 10 Mb/d.
Analyzing also results for the single CubeSats, results turn out to be fully satisfactory, without
presence of empty spaces under the dashed lines.
After CS Group 1, it is good to understand also the CS Group 2 behavior. Generally the
communication access is lower due to the closer angular distance, and the inevitable presence of
communication overlaps. Usually if the requirements are satisfied for this configuration, they are
also satisfied for the CS Group 1.
In the first part the single CubeSats results are presented. In these plots, if there are presences of
empty spaces under the communication threshold dashed lines, it is not possible to achieve mission
requirements, and ground segment has to increase the ground station number or latitudes. CS
Group 2 results are shown below for the Asia N/S layout of ground stations.

<!-- PDF_PAGE: 119 -->

Constellation Analysis                                                                                119




                          CS 1                                                CS 2




                          CS 3                                                CS 4




                                                    CS 5


           Figure 6.17: Data per day for CS Group 2 and Asia N/S Ground segment (Single CS results)

<!-- PDF_PAGE: 120 -->

120                                                                                     Constellation Analysis




              Figure 6.18: Data per day for CS Group 2 and Asia N/S Ground segment (Overall result)




For this new CS group, results are not satisfactory. The minimum data per day line is under the 10
Mb/d line. In first days there is a low peak, which is responsible of the non-satisfying results of the
mission requirements. If this peak is avoided, increasing for instance the number of ground
stations, then this ground station group can be used.



6.4.2. Northern Hemisphere E/W Ground segment
The Northern Hemisphere ground segment includes some ground stations above the equator. Next
plots show the average data per day collected during QB50 mission. The first part of plots is
evaluated for each single CubeSat, while the second figure, as before, represents the overall
behavior of CubeSats. If there is presence of empty spaces under the dashed threshold lines, the
ground segment has to be improved. In the previous ground segment (Asia N/S), in the second CS
group, there were some of these empty spaces. If we want to achieve mission requirements, it is
mandatory to avoid this kind of problem, and for this new ground segment results seem good from
this point of view. The following plots are related to CS Group 1.

<!-- PDF_PAGE: 121 -->

Constellation Analysis                                                                                  121




                             CS 1                                          CS 11




                             CS 21                                         CS 31




                                                    CS 41




    Figure 6.19: Data per day for CS Group 1 and Northern Hemisphere E/W Ground segment (Single CS results)

<!-- PDF_PAGE: 122 -->

122                                                                                    Constellation Analysis




      Figure 6.20: Data per day for CS Group 1 and Northern Hemisphere E/W Ground segment (Overall result)




Results of CS Group 1 turn out to be satisfactory. Minimum data per day is above 4 Mb/d and 10
Mb/d lines, and there is not presence of empty spaces in single CubeSat plots.
Analyzing also the CS Group 2, it is possible to have a general overview of this ground segment.
The results for the CS Group 2 are shown below for the Northern Hemisphere ground segment.
As it is shown in next figures, mission requirements are satisfied also for this other CS group.
There aren’t empty spaces in the first part of plots (single CubeSats results), and the overall result
turns out to be good in order to use this ground segment also with a closer configuration of
satellites, like for CS group 2.

<!-- PDF_PAGE: 123 -->

Constellation Analysis                                                                                  123




                            CS 1                                             CS 2




                            CS 3                                              CS 4




                                                     CS 5




    Figure 6.21: Data per day for CS Group 2 and Northern Hemisphere E/W Ground segment (Single CS results)

<!-- PDF_PAGE: 124 -->

124                                                                                    Constellation Analysis




      Figure 6.22: Data per day for CS Group 2 and Northern Hemisphere E/W Ground segment (Overall results)




6.4.3. America N/S Ground segment
The third ground segment proposed is the America N/S layout. There are four ground stations, two
in North America, and two in South America. We still assume 98° for CubeSats orbit inclination,
and a data rate of 9.6 kbps for the UHF communication strategy.
As it is shown in next plots, like for the Northern Hemisphere ground segment, communication
requirements are completely satisfied for both CS groups.
The single CubeSats results are shown below for CS group 1, followed by the overall results for the
same CS group.

<!-- PDF_PAGE: 125 -->

Constellation Analysis                                                                                  125




                             CS 1                                          CS 11




                            CS 21                                           CS 31




                                                    CS 41




          Figure 6.23: Data per day for CS Group 1 and America N/S Ground segment (Single CS results)

<!-- PDF_PAGE: 126 -->

126                                                                                    Constellation Analysis




           Figure 6.24: Data per day for CS Group 1 and America N/S Ground segment (Overall results)




As it is has been stated before, results are good. Mission requirements are fully satisfied; there
aren’t low peaks, which lower minimum data per day line. Like for Northern Hemisphere segment
everything is fine, and the ground segment turns out to be compatible with QB50 communication
constraints. As it is shown also by next plots, for CS group 2 results are also good for mission
threshold. Also the worst CubeSat configuration appears to be fully operative under mission
communication rules.

<!-- PDF_PAGE: 127 -->

Constellation Analysis                                                                                  127




                            CS 1                                              CS 2




                           CS 3                                               CS 4




                                                     CS 5


          Figure 6.25: Data per day for CS Group 2 and America N/S Ground segment (Single CS results)

<!-- PDF_PAGE: 128 -->

128                                                                                    Constellation Analysis




           Figure 6.26: Data per day for CS Group 2 and America N/S Ground segment (Overall results)




6.4.4. Europe Ground segment
The last ground segment selected for this kind of analysis is the European group of ground stations.
From this study we are able to state that this group will satisfy mission requirements for both CS
groups. Below we present single CubeSats results, without free spaces under the threshold dashed
lines. As it is shown also in the overall results plot (Figure 6.28), minimum data per day line turns
out to be higher than other two. The minimum data per day accumulated in first 100 days appears
to be higher than 15 Mb/day, hence including 5 Mb/day more than the selected threshold of 10
Mb/day. Plots are shown below for the CS Group 1 combined with Europe segment ground
stations. In Figure 6.27 it is very interesting note that for some CubeSats GS 20 cannot receive data
for almost three weeks at the end of the mission lifetime. As Figure 6.27 shows, this is not a huge
problem, because exploiting other GSs it is always possible to achieve mission requirements.

<!-- PDF_PAGE: 129 -->

Constellation Analysis                                                                               129




                           CS 1                                             CS 11




                           CS 21                                            CS 31




                                                    CS 41




            Figure 6.27: Data per day for CS Group 1 and Europe Ground segment (Single CS results)

<!-- PDF_PAGE: 130 -->

130                                                                                   Constellation Analysis




             Figure 6.28: Data per day for CS Group 1 and Europe Ground segment (Overall results)




The worst configuration for CubeSats is the second one. Here, for this segment, mission
requirements are achieved also for this second group. Like for the two previous segments (Northern
Hemisphere and America), requirements are achieved, and ground segments are able to satisfy all
mission requirements imposed by QB50 space mission.

<!-- PDF_PAGE: 131 -->

Constellation Analysis                                                                               131




                           CS 1                                              CS 2




                            CS 3                                            CS 4




                                                    CS 5


            Figure 6.29: Data per day for CS Group 2 and Europe Ground segment (Single CS results)

<!-- PDF_PAGE: 132 -->

132                                                                                    Constellation Analysis




              Figure 6.30: Data per day for CS Group 2 and Europe Ground segment (Overall results)




6.4.5. Ground Segments analysis results
This analysis is very interesting; by this study we are able to understand the average behavior of
communication between QB50 satellite network and some possible ground segments, selected on
the basis of particular geographic positions. These geographic regions are described by the ground
segment groups previously introduced. Analyzing results, we found that the worst scenarios for
communication turn out to be CS Group 2 combined with the possible ground segments. The
shorter angular distance could determine in the simulations a strong presence of communication
overlaps or other possible problems due to interferences, that don’t allow a good communication
link. Indeed, for all possible ground segments, in the case of the CS group 1 communication
mission requirements turn out to be fully satisfied. Plots show that QB50 communication
thresholds are completely under the minimum data per day line. For the second CS group, related
to the shorter angular distance, results are closer to the thresholds, and for the Asia N/S layout of
ground stations, it is not possible to achieve mission requirements. It is mandatory to improve
something if we want to use this ground station for QB50 mission. A possible idea could be the
increase of ground stations number, or the change of latitude positions for ground stations,
choosing higher altitude, with higher coverage. The tables below, one for each CS Group,
summarize all minimum and maximum data per day calculated for the selected ground segments.

<!-- PDF_PAGE: 133 -->

Constellation Analysis                                                                                   133



Results are highly satisfactory, because in almost every case, mission requirements are achieved.
Only the Asia ground segment has to be improved, and we are not so far to reach the 10 Mb/day
threshold. Also European GS cluster doesn’t give good results looking the high number of ground
stations involved (minimum data per day of around 15 Mb/day). This is due to the high overlaps
presence in clustered Ground Stations. So it could be preferred use ground stations quite distant
with respect to clustered GSs.

These results give us a good output in order to choose one of the proposed ground segments for the
QB50 mission. This kind of output ensures a full achievement of mission requirements, and these
ground stations turn out to be able to satisfy communication requirements.


  Table 6.3: Minimum and maximum data per day accumulated during first 100 days of mission lifetime (CS Group 1)

                                           Minimum Data per day                  Maximum Data per day
         Ground Segment
                                                 [Mb/d]                                [Mb/d]

             Asia N/S                                 ~ 16                                  > 40

  Northern Hemisphere W/E                             > 20                                  ~ 90

           America N/S                                ~ 18                                  ~ 60

              Europe                                  ~ 15                                  ~ 30




  Table 6.4: Minimum and maximum data per day accumulated during first 100 days of mission lifetime (CS Group 2)

                                           Minimum Data per day                  Maximum Data per day
         Ground Segment
                                                 [Mb/d]                                [Mb/d]

             Asia N/S                                  ~9                                   > 40

  Northern Hemisphere W/E                             ~ 18                                  ~ 90

           America N/S                                ~ 13                                  ~ 60

              Europe                                  ~ 13                                  ~ 30

<!-- PDF_PAGE: 134 -->

134                                                                           Constellation Analysis




6.5. Combinations Analysis


One of the most important analyses is the Combinations Analysis. The word combinations is used
because communication of previous CS groups, here, is analyzed for different combinations of
ground stations. These combinations are four for an increasing total number of ground stations.
These four simulations for each GS number are arbitrarily selected to avoid bad GS combinations,
which could be randomly picked. Starting from one ground station, so, analyzing four different
ground stations, the number of stations for the ground segment is increased to two. For each
number of total ground stations are studied four different cases are studied, in order to have an idea
of average communication behavior for the selected GS number. Below we present a schematic
representation that explains the simulation scheduling for this kind of analysis. In appendix B it is
possible to find the complete list of cases analyzed in this study. The simulation includes 100 cases
for a total number of ground stations between 1 and 25. Obviously, increasing the ground stations
number, the amount of collected data increases. The main objective of this analysis is the finding of
the minimum GS number required to satisfy all mission requirements. Starting from one GS, the
communication behavior is analyzed for each number of ground stations until the number of 25
GSs utilized is reached. In order to analyze the worst case in next paragraphs results for CS Group
2 are presented, but the same analysis was conducted also for CS Group 1, and a comparison will
be shown in few paragraphs.




                                 Figure 6.31: Combinations Analysis idea




A number of 28 possible ground stations are selected from the current list of QB50 teams. Creating
combinations of these 28 ground stations, it is possible to understand the average behavior of a
good number of ground segments. In the table below there are all possible stations used for the
analysis, with the corresponding numbers used for computations.

<!-- PDF_PAGE: 135 -->

Constellation Analysis                                                                                             135



    Table 6.5: Ground stations used for the Combination Analysis, with the corresponding number used for computations

Universidad de Buenos Aires                                1    Anna University                                            15

The University of Adelaide                                 2    University of Rome “LA SAPIENZA”                           16

University of Sydney                                       3    Korea Advanced Institute of Science and Technology         17

University of Applied Science Technikum Wien               4    Delft University of Technology                             18

University of Liège                                        5    PERUVIAN CONSORTIUM                                        19

von Karman Institute                                       6    University of Porto                                        20

York University – Toronto                                  7    Samara State Aerospace University                          21

Beihang University                                         8    Universidad Politécnica de Madrid                          22

Nanjing University of Science and Technology               9    National Cheng Kung University                             23

Zhejiang University                                        10   Istanbul Technical University / Air Force Academy          24

Czech Technical University in Prague                       11   National Technical University of Ukraine                   25

Aalborg University                                         12   MSSL University College London                             26

Aalto University                                           13   University of Surrey                                       27

Institut Supérieur de l’Aéronautique et de l’Espace ISAE   14   Stanford University                                        28




  6.5.1. Results for one GS
  This paragraph shows results obtained for an unique ground station. The selected ground stations
  for this analysis are: 1, 6, 13, and 20. Case 1 is composed of GS 1, case 2 is made up of GS 6, case
  3 of GS 13, and finally case 4 of GS 20 as also shown before in Figure 6.31. For each GS case it is
  possible to have an average behavior for the communication for the CS Group 2.

  In Figure 6.32 below the overall results are presented for all four studied cases. As it is shown in
  the following plots, mission requirements are not achieved. Taking into account all four cases,
  there is an average minimum collected data per day in first 100 days of mission lifetime that is
  around 2 Mb/day. This value is too far from the 10 Mb/day threshold, and the use of one ground
  station turns out to be not feasible to achieve QB50 requirements. There is also the extracted
  behavior of the first CS, the presence of empty spaces under threshold lines is another proof of the
  non-fulfillment of the one GS study. As suggested in previous ground segments analysis, in order
  to improve system performances, there are mainly two ways: to use higher latitude for the ground
  stations, and/or to increase the number of involved ground stations. In next paragraph are shown
  for a number of stations increased to two different ground stations.

<!-- PDF_PAGE: 136 -->

136                                                             Constellation Analysis




        Case 1                                       Case 2




        Case 3                                       Case 4


      Figure 6.32: CS Group 2 overall results for 1 GS cases




      Figure 6.33: CS1 result for 1 GS configuration (Case 1)

<!-- PDF_PAGE: 137 -->

Constellation Analysis                                                                            137



6.5.2. Results for 2 GSs
In this paragraph we present results obtained by using two ground stations. The selected ground
stations for this analysis are: 1, 3, 7, 13, 17, 21, and 28. The cases analyzed are still four, and in
particular they are:

    -   Case 5: 1, 13
    -   Case 6: 28, 3
    -   Case 7: 7, 21
    -   Case 8: 13, 17

The overall results for all four analyzed cases are presented below. For each GS case it is possible
to have an average behavior for the communication for the CS Group 2.
As it is shown in the following plots, mission requirements are not achieved also for this number of
ground stations. Taking into account all four cases, there is an average minimum collected data per
day in first 100 days of mission lifetime that is around 7 Mb/day. The minimum value is increased
with respect to one GS analysis, but it is still under the 10 Mb/day threshold, and the use of two
ground stations turn out to be not feasible in order to achieve communication requirements. After
the overall results for all the studied cases, there is also the extracted behavior of the first CubeSat
of CS group 2. The presence of empty spaces under threshold lines confirms that 2 GSs
configuration doesn’t work well for QB50 constraints. In order to improve further system
performances, the analysis studies other configurations with a larger number of ground stations.




                               Case 5                                       Case 6




                               Case 7                                        Case 8

                            Figure 6.34: CS Group 2 overall results for 2 GSs cases

<!-- PDF_PAGE: 138 -->

138                                                                                    Constellation Analysis




                            Figure 6.35: CS1 result for 2 GSs configuration (Case 5)




6.5.3. Results for 10 GSs

In this new paragraph we present results obtained by using ten ground stations. The selected ground
stations for this analysis are: 1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26 and
28.

The ground station cases analyzed are again four, and in this particular case they are:

        - Case 37: 1, 3, 4, 11, 12, 16, 20, 24, 25, 26

        - Case 38: 1, 2, 4, 7, 8, 17, 18, 19, 22, 28

        - Case 39: 1, 7, 8, 12, 16, 19, 20, 21, 22, 28

        - Case 40: 1, 2, 4, 6, 7, 10, 16, 20, 21, 22

As it is shown in next figures, mission requirements are fully achieved. Taking into account all four
cases, there is an average minimum collected data per day that is around 34.6 Mb/day. The
minimum value is much increased with respect to 2 GSs analysis, and the use of ten ground stations
turn out to be completely feasible to achieve QB50 communication requirements.

Moreover, as we can see from the extracted plot of the first CubeSat, the absence of empty spaces
under threshold lines confirms that 10 GSs is a good option for QB50 project.

<!-- PDF_PAGE: 139 -->

Constellation Analysis                                                                139




                             Case 37                                    Case 38




                            Case 39                                      Case 40


                          Figure 6.36: CS Group 2 overall results for 10 GSs cases




                         Figure 6.37: CS1 result for 10 GSs configuration (Case 37)

<!-- PDF_PAGE: 140 -->

140                                                                                    Constellation Analysis



6.5.4. Results for 25 GSs
Increasing further the number of ground stations, until the end of the analyzed cases is reached, it is
possible to obtain the results for the 25 GSs cases. Analyzed ground station cases are still four, and
in detail they are:

- Case 97: 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28

- Case 98: 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28

- Case 99: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25

- Case 100: 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28

As it is shown in following plots, mission requirements are completely achieved, and it is possible
to affirm that there is an overload of accumulated data per day with respect to QB50
communication requirements. There is an average minimum collected data per day that is above 59
Mb/day. This value is too high with respect to the 10 Mb/day threshold; using a ground segment
with this number of GSs we could have a high waste of resources. There is a very good amount of
collected data, but we cannot go too beyond the thresholds, because the costs for maintenance or
other mission aspects could increase exponentially with a too large number of GSs.




                               Case 97                                     Case 98




                              Case 99                                       Case 100


                            Figure 6.38: CS Group 2 overall results for 25 GSs cases

<!-- PDF_PAGE: 141 -->

Constellation Analysis                                                                               141




                           Figure 6.39: CS1 result for 25 GSs configuration (Case 97)



6.5.5. Evaluation of the Minimum GSs number
In order to improve system performances, but also to take into account a reasonable cost of the
mission, it is mandatory to find the minimum number of ground stations which permits to achieve
QB50 requirements. Solutions with 10 and 25 GSs are fully above mission thresholds, hence, in
order to find the optimal number it is requested to decrease again the number of GSs, taking in
consideration the solution which overtakes communication thresholds, without waste of too many
resources. Interpolating minimum collected data per day from simulations with all possible cases, it
is possible to reproduce a plot with the number of ground stations in the x-axis, and the minimum
data accumulated per day in the y-axis. As it has been previously demonstrated, CS Group 2 is the
worst case from the collected data point of view. Analyzing CS group 2 behavior, and putting the
threshold of 10 Mb/day as the design parameter, it is possible to find the minimum number of
ground stations required to achieve at least 10 Mb/day amount of data. This minimum number turns
out to be three for the CS group 2.




              Figure 6.40: Minimum data collected per day for different numbers of ground stations

<!-- PDF_PAGE: 142 -->

142                                                                                    Constellation Analysis



Studying in detail the results of the analysis for three ground stations, it is possible to verify below
that for the single CS 1 results, for all four studied cases, there is a complete absence of free spaces
under the thresholds dashed lines, moreover daily collected data in low peak regions are not too far
from requirement lines, avoiding additional useless costs. The analyzed cases for 3 GSs study are:

        - Case 9: 3, 7, 13

        - Case 10: 2, 12, 17

        - Case 11: 1, 9, 25

        - Case 12: 2, 7, 24

Below we present the single CS 1 results and the overall results for all four analyzed cases.




                              Case 9                                         Case 10




                              Case 11                                        Case 12


                                  Figure 6.41: CS1 result for 3 GSs configuration

<!-- PDF_PAGE: 143 -->

Constellation Analysis                                                                       143




                             Case 9                                       Case 10




                             Case 11                                       Case 12


                             Figure 6.42: Overall results for 3 GSs configuration



This stations number guarantees a full achievement of the QB50 mission requirements, and avoids
a waste of resources. In order to minimize costs of the mission it is suggested to exploit a
configuration for the ground segment including three or four ground stations. This value could
change in function of the change of the orbital inclination (assumed to be 98°), and high changes of
ground station altitudes. In next paragraphs we show the main effects of variations of these last two
parameters on the daily access numbers and transmitted data per day.

<!-- PDF_PAGE: 144 -->

144                                                                                         Constellation Analysis




6.6. Influence of orbit inclination
The inclination is one of the six orbital parameters describing the shape and orientation of a
celestial orbit. It is the angular distance of the orbital plane from the plane of reference, Earth's
equator in this case, normally measured in degrees. Choosing a different inclination it is possible to
change dramatically all mission parameters, and among these also the communication
performances. Accesses are strongly influenced by this orbital parameter, number and time of
accesses are functions of this angle. If the launcher is changed it is often mandatory to change also
orbit inclination for the mission in the case of secondary passengers which is typically the case of
CubeSats. The use of Cyclone-4 changed the orbit inclination of previous Shtil' launcher from 79°
to 98°. Hence it is very interesting to have a general overview of the performances obtainable by
changing the launcher and/or orbit inclination. By means of this analysis it is possible to understand
directly the influence of a change in orbit inclination comprised between 60° and 100°. These are
the results of the one-to-one problem results for different satellites at different inclinations. We
assume to have only one GS at VKI (50.75 lat., 4.38 long.), and a data rate of 9.6 kbps.




           Figure 6.43: Number of accesses per day during mission lifetime for different orbit inclinations



The number of accesses, and also all other performances decrease with mission lifetime; this is
mainly due to the orbit altitude decrease and to increasing problems for communication. Indeed for
lower altitudes satellite passages are faster and shorter.

As it is possible to see in Figure 6.43, lower inclinations ensure a higher number of accesses. This
analysis shows that a maximum increase of number accesses, above 75%, takes place for low
inclinations. Hence, a lower inclination allows a larger number of contacts, and a consequent
improvement in communication performances as other plots below can show. Figure 6.44 shows
the access times for different inclinations, and a maximum increase of access times above 70% for
low inclinations. In Figure 6.45 there is the same maximum increase of transmitted data above 70%
for low inclinations.

<!-- PDF_PAGE: 145 -->

Constellation Analysis                                                                                      145



As it has been stated before lower inclinations allow an improvement in communication
performances, however, inclination selection sometimes depends also on other factors, like choice
of the launcher vehicle or other mission constraints.




             Figure 6.44: Access time per day during mission lifetime for different orbit inclinations




           Figure 6.45: Transmitted data per day during mission lifetime for different orbit inclinations

<!-- PDF_PAGE: 146 -->

146                                                                                                       Constellation Analysis




6.7. Influence of ground station latitude


Another relevant communication analysis factor is the ground station latitude. GSs at high latitudes
offer a larger coverage area for communication. In a first step it is very interesting to analyze a set
of nine ground stations placed at the same longitude for nine different latitudes between 0° and 80°.
Choosing the orbit inclination of 98°, results turn out to be intriguing. In the plot below it is shown
the variation of the angular range for the longitude and latitude coverage for different GS latitudes.
Increasing GS latitudes performances are better, and guarantee longer access. By this first analysis
it is possible to state that higher GS latitudes lead to greater longitude range angles, while latitude
range angles are nearly constant.




                              90

                              80

                              70
                                               Longitude




       Coverage Anlge [deg]
                              60               Range

                              50               Latitude
                                               Range
                              40

                              30

                              20

                              10

                              0
                                   0     10         20        30        40         50        60           70      80
                                                                GS Latitude [deg]



                                       Figure 6.46: GS coverage range angles for different GS latitudes



Assuming an orbit inclination of 98°, with the previous nine ground stations at the same longitude,
it is possible to study the communication behavior for different GS latitudes. As it has been shown
in the previous plot, higher latitudes offer better performances. In Figure 6.46 the number of
accesses per day during mission lifetime for different GS latitudes is analyzed. Higher latitudes
ensure higher access numbers and larger coverage areas. Access numbers can be 8 times larger for
higher latitudes with respect to lower ones. A good behavior for higher latitudes is confirmed also
by transferred data per day plot, which is shown in Figure 6.48. Higher latitudes ensure also longer
accesses, and access times can be also 7 times longer for higher latitudes, especially during the first
part of mission lifetime. The same good results are obtained for the transmitted data per day.
Therefore higher GS latitudes ensure therefore more daily transmitted data, which could reach an
amount even 7 times larger for higher latitudes. By means of this analysis it is possible to have

<!-- PDF_PAGE: 147 -->

Constellation Analysis                                                                                   147



direct results for communication behavior for different positions of ground stations. If it is possible
to choose GS locations, the outcome of this study suggests the choice of GSs at high latitudes.
Higher GS latitudes could reduce also the number of used ground stations and related mission
costs.




              Figure 6.47: Number of access per day during mission lifetime for different GS latitudes




              Figure 6.48: Transmitted data per day during mission lifetime for different GS latitudes

<!-- PDF_PAGE: 148 -->

148                                                                                      Constellation Analysis




6.8. Use of a single GS at high latitude
In the previous analysis selected GS latitudes are not so high. Probably, by optimizing the ground
station latitude, it would be possible to decrease the ground stations number. If the orbit inclination
is 98°, in order to maximize time and number of accesses, it would be interesting to study the case
of a single ground station with a high latitude. In the previous analysis, selected GS latitudes are
below an average latitude of 40° - 50°. Assuming an orbit inclination of 98°, we assume that the
ideal latitude could be something around 82°. For this reason in the present paragraph there is a
deep study of three different GS latitudes close to this ideal case.

In the following we present an analysis about three different GSs, characterized by three different
latitudes:

         GS 29: 0° long., 90° lat. (North Pole)
         GS 30: 0° long., 85° lat.
         GS 31: 0° long., 80° lat.

These GSs are completely imaginary, since there not exist ground stations in these positions.




                                                                                                  For Educational Use




                     Figure 6.49: 3D Visualization of new ground stations close to North Pole




For this new analysis there are the same assumptions of previous analyses. The orbital
characteristics and mission requirements are the same. In order to have a deep investigation there
are two different studies about two different CS groups (CS Group 1 and CS Group 2). As it is
stated before CS Group 1 is characterized by a larger angular distance between close CubeSats,

<!-- PDF_PAGE: 149 -->

Constellation Analysis                                                                        149



while for CS Group 2 the situation is worst, CubeSats are closer, and there are more overlaps
problems.



6.8.1. GS 29 results
This ground station is at the north pole, at a chosen longitude of 0°. For this kind of analysis all
stations are at the same longitude of 0°. For these ground stations, Scenario 7 (or Scenario 6 mod)
is used, in order to understand the access contact time and the behavior of the data per day in
function of mission lifetime. Results turn out to be highly satisfactory, there is only one ground
station but mission requirements are fully satisfied for both CS groups.

For CS Group 1, CubeSats exhibit the same behavior, there are strong oscillations, but the average
amount of data per day is well above the 10 Mb/d threshold, and also the minimum data per day
collected in the first 100 days is around 18 Mb/d. Access contact time is almost the same for all
CubeSats, without high differences between first and final CubeSats of the group.




                   Figure 6.50: Access contact time and data per day for GS 29 (CS group 1)

<!-- PDF_PAGE: 150 -->

150                                                                              Constellation Analysis




                              Figure 6.51: Data per day for GS 29 (CS group 1)




For CS Group 2 there are some differences between different CubeSats. First CubeSats of the
group exhibit a good behavior, but last CubeSats seem to suffer overlaps presence, and access time
for them is lower with respect to the first CubeSats of the group. Therefore, despite this kind of
problems mission requirements turn out to be satisfied and fully reached. The minimum data per
day is lower with respect to CS Group 1, but it is not avoidable because CS Group 2 is in the worst
condition for the strong overlaps presence. As it is shown in Figure 6.52, the minimum data per day
is around 15 Mb/d, and the behavior of CubeSats is deeply dependent on the CubeSat position
inside the analyzed constellation. Access time and daily data collected for first satellites can be
more than two times higher with respect to last CSs of the considered group. If the CubeSat is one
of the first of the group, then it collects a lot of data, but following ones collect less data due to
overlaps and consequent reduced contact time. The amount of daily collected data has less
oscillations with respect to the case of CS Group 1: the amount of collected data doesn’t vary
periodically as it happens with CS Group 1, but the values of daily collected data often stay almost
constant for a lot of time during mission lifetime. Therefore, though the conditions are worst than
for the first CS group, also this second group satisfies all mission requirements.

<!-- PDF_PAGE: 151 -->

Constellation Analysis                                                                       151




                  Figure 6.52: Access contact time and data per day for GS 29 (CS group 2)




                             Figure 6.53: Data per day for GS 29 (CS group 2)

<!-- PDF_PAGE: 152 -->

152                                                                                    Constellation Analysis



6.8.2. GS 30 results
This second ground station is at a chosen longitude of 0°, and at the latitude of 85°. Analyzing the
results of Scenario 7 it is possible to understand the communication behavior in function of mission
lifetime. Results turn out to be satisfactory. CS Group 1 exhibits the same behavior with strong
oscillations analogous to GS 29, but the average amount of data per day stays above the 10 Mb/d
threshold also for this case. The minimum data per day collected in the first 100 days is around 18
Mb/d, and access contact time is almost the same for all CubeSats, without large differences
between first and final CubeSats of the group.




                   Figure 6.54: Access contact time and data per day for GS 30 (CS group 1)




                              Figure 6.55: Data per day for GS 30 (CS group 1)

<!-- PDF_PAGE: 153 -->

Constellation Analysis                                                                        153



Also for this GS, for CS Group 2, there are some differences between different CubeSats. First
CubeSats of the group exhibit a better communication behavior, and access time for them is higher
with respect to last CubeSats of the group. Therefore, mission requirements turn out to be satisfied,
and minimum data per day is higher than 10 Mb/d threshold. As it is shwn in Figure 6.56, the
minimum data per day is around 15 Mb/d, and the behavior of CubeSats strongly depends on
CubeSat position in the considered constellation. Access time and daily data collected for first
satellites can be more than twice higher with respect to last CSs of the considered group. The
amount of daily collected data has less oscillations with respect to the case of CS Group 1, and the
amount of collected data doesn’t vary periodically as it happens with CS Group 1. Therefore,
though the conditions are worst than for CS group 1, this second group satisfies all mission
requirements, so that the use of this GS can be fully feasible.




                   Figure 6.56: Access contact time and data per day for GS 30 (CS group 2)

<!-- PDF_PAGE: 154 -->

154                                                                              Constellation Analysis




                              Figure 6.57: Data per day for GS 30 (CS group 2)




6.8.3. GS 31 results
The last analyzed ground station is at 80° of latitude. Results turn out to be highly satisfactory. For
CS Group 1, CubeSats exhibit the same behavior, there are quasi-periodic oscillations, but the
average amount of data per day is well above the communication threshold of 10 Mb/d, and also
the minimum data per day collected in the first 100 days is around 15 Mb/d. Access contact time is
almost the same for all CubeSats, without remarkable differences between CubeSats of the group.
For this ground station, but also for the others previously analyzed, the maximum peak of daily
data collected by a single ground station is very high. From the results obtained by this study it
follows that the maximum data collected per day is around 80 Mb/d, a value 8 times larger with
respect to QB50 communication requirement of 10 Mb/d. This result, in combination with the
result that minimum daily collected data is always larger than 10 Mb/d, confirms that the use of one
ground station at high latitudes improves communication performances. As it is shown in the
following plots, both CS groups yield good results for QB50 mission requirements. CS Group 2
turns out to have a minimum data per day during first 100 days that is around 13 Mb/d, this value is
lower than for the first CS group, but it is always above the communication threshold, guarantying
system feasibility.

<!-- PDF_PAGE: 155 -->

Constellation Analysis                                                                       155




                  Figure 6.58: Access contact time and data per day for GS 31 (CS group 1)




                             Figure 6.59: Data per day for GS 31 (CS group 1)

<!-- PDF_PAGE: 156 -->

156                                                                       Constellation Analysis




      Figure 6.60: Access contact time and data per day for GS 31 (CS group 2)




                 Figure 6.61: Data per day for GS 31 (CS group 2)

<!-- PDF_PAGE: 157 -->

Constellation Analysis                                                                       157



6.8.4. General considerations for single GS utilization
The ground stations list considered in the initial part of the chapter has ground stations with low
altitudes, and the latitudes are in average of 40° - 50°. Using an orbit inclination of 98° it is
preferable use a different latitude for ground stations, and the optimal latitude to increase
communication performances could be around 82°. From previous paragraphs it turns out that even
only one GS could satisfy mission requirements. Ground stations 29, 30, 31 guarantee the overtake
of the 10 Mb/d for the daily data accumulated during mission lifetime, and there are high peaks of
accumulated data, which reach values around 80 Mb/d. The single GS utilization could be an
effective alternative with respect to the use of a ground segment with academic stations. For a
single GS utilization maintenance requires high costs to guarantee a high reliability. With a ground
stations network the reliability required for each ground station is surely lower with respect to the
use of a single GS. Moreover, if one GS doesn’t work for a short or a long period it could be
substituted by another one of the ground segment, without huge losses of data during the failure
period until the ground station reparation. High maintenance costs and also the difficulties for the
accessibility, considering high latitudes, can create some problems, but, from another point of view,
the utilization of a single GS can remove all problems related to the network concept.

<!-- PDF_PAGE: 158 -->

158                                                                   Conclusions and further works




7 Conclusions and further works

7.1. Final considerations
In this final chapter, there is a brief review of the performed researches, in order to reorganize all
analyses results obtained in previous chapters. The objectives of the conducted communication
analysis were the research of the optimal number and position for the ground stations to satisfy all
mission requirements, and the communication link optimization by study of different strategies.
Analysis requirements were mainly the use of a simple and high space qualified technology and a
particular amount of daily data downloaded (4 Mb/day extended later to 10 Mb/day including
margins) for each CubeSat. The first analyzed issue was the choice of communication system. The
choice was focused on two different systems: S-Band and UHF/VHF. During this study the crucial
demand of a rotator mechanism was found in order to track satellites for longer time during their
passages. This additional component allows an increase in access times and, consequentially, in
transmitted data amount. Analyzing the behavior of the suggested systems for the one-to-one
problem (one CS with one GS), from the transmitted data point of view, S-Band appeared to be
dramatically over mission requirement thresholds, and UHF/VHF was not so far off to achieve the
QB50 requirements. Apparently both solutions could be fine to achieve mission constraints. In
order to choose the system, another analysis on the signal quality was performed. By the link
budget analysis emerged that UHF/VHF signal quality is fully satisfactory for typical used devices
on board of a CubeSat, while for S-Band strategy the quality is not so good due the higher data
rate. Link margins of proposed strategies are different, and S-Band requires a complexity increase
on board for CubeSats due to higher pointing requirements. These results suggest selecting the
UHF/VHF strategy for QB50 communication system, avoiding the S-Band utilization.
As it is stated in first chapters UHF/VHF system has a lot of advantages, like the low power
consumption or the wide beamwidth, but has a weakness point, which is the low data rate. In order
to avoid this problem the number of ground stations turns out to be larger with respect to other
solutions with higher data rates. Results of one-to-one analysis were exploited to extend the study
to the constellation concept. Just before introducing the constellation problem, it was studied the
presence of communication overlaps in QB50 mission. This turned out to be a relevant problem,
especially when the satellites are in the initial close configuration shortly after deployment. The
main issue in STK software environment was the impossibility to add the single access constraint.
Only one GS can communicate with a CS and vice versa, but for the software when there was the
spatial possibility to create a link, it allows simultaneously accesses without opportunity to avoid
wrong contacts (i.e. multiple satellites contacts by one GS). In order to prevent this problem, access
times were evaluated by STK, but afterwards a MATLAB program analyzed all possible true
contacts including constraints like antenna rotation time and minimum contact time, and by

<!-- PDF_PAGE: 159 -->

Conclusions and further works                                                                 159



utilizing it reliable results turned out by this analysis. Implementation of another software, with
respect to STK, proved to be fundamental to obtain very interesting and reliable outputs. After
implementing the new overlaps algorithm, it is possible to extend the first results of one-to-one
analysis to the constellation concept. Dynamics of CubeSats is very difficult to explain by a
simulation and strongly depend on the initial orbit parameters, especially for the network behavior;
in order to describe as better as possible the network communication during mission lifetime, two
different CS configurations were introduced. CubeSat Group 1 is the configuration with a larger
angular distance between the CubeSats spreading over whole orbit, while CubeSat Group 2 is the
solution to describe closer CubeSats case, especially valid during first lifetime phase to simulate
contact                                                                                      overlaps.
Ground Segment analysis is the first analysis conducted for the constellation problem. Dividing by
four different geographic zones (Asia, Northern Hemisphere, America, and Europe) the global
ground segment, communication behavior of each particular ground segment was analyzed into the
detail for both CS groups. Results turn out to be highly satisfactory, save for the Asian ground
segment, which has to be improved to satisfy QB50 mission requirements. The lower performance
of the Asian ground segment was due to an alignment of the ground stations with the satellite path
resulting in similar contact losses and acquisitions. Therefore such a distribution should be avoided
for QB50. In order to achieve the objective of the optimal configuration of ground stations
research, it is mandatory to change the analysis type. Combination Analysis is the best way to
understand the true communication behavior for the optimal number of ground stations, and to find
also the best configuration. A high number of scenarios has been defined for constellation analyses,
with different parameters included like the rotation time or partial contacts. Selecting the optimal
scenario (rotation time, full passes with min. contact time, optimized for daily access time), results
were obtained with a high reliability level. By the combination analysis, starting from one GS until
arrive to 25 GSs, and analyzing scenario outputs for each possible configuration, the minimum
number of ground stations to satisfy all mission requirements (10 Mbpd) turns out to be three. Also
the ground stations influence on the communication was deeply analyzed, in particular the effect of
different position through the change of GS latitudes was studied. Results show clearly that higher
latitudes ensure better communication performances, and they are greatly preferred with respect to
lower ones. This study is fundamental to have a direct information about achievable performances
for a particular ground station, and it could be used also for a first selection of the stations
constituting QB50 ground segment. Afterwards GS latitude, the orbit inclinations have a great
influence on the accumulated data by ground stations. Changing of launcher vehicles often
corresponds to a change of orbital inclination for the mission. By this performed analysis it is
possible to have a general overview on possible amount of data transmitted in function of different
orbit inclinations, associable to different launchers. Increasing stations number with respect to the
minimum number, requirements will be surely satisfied, but it would occur a waste of resources,
and            a           consequent           increase          in           mission          costs.
Using an orbit inclination of 98° it could be preferable to use a different latitude for ground
stations, which could be around 80°. From previous analyses it turns out that also only one GS
could satisfy mission requirements. With the use of a high latitude GS there are high peaks of
accumulated data, which reach values around 80 Mb/d, and average daily collected data are well
over the imposed communication requirement of 10 Mb/d. The use of a single GS could be an
effective alternative with respect to the use of an academic stations network. For a single GS
utilization there are also relevant downsides as the maintenance, which requires high costs to
guarantee a high reliability. With a ground stations network the reliability of each ground station is
lower with respect to the use of a single GS. High maintenance costs and also the difficulties for
the accessibility, looking at high latitudes, can create some problems, but, from another point of
view, the utilization of a single GS can remove all problems related to network concept.
The suggested solution uses the academic ground stations network, and involves the minimum
number of ground station required to satisfy mission constraints, considering also some margins
and a not so high resource waste. Despite QB50 orbital dynamics for CubeSats is very complex,
this work includes interesting, and reliable results, and especially the flexibility of performed

<!-- PDF_PAGE: 160 -->

160                                                                     Conclusions and further works



analyses can guarantee a wide use of the utilized scenarios also in case of mission modifications,
and further changes.


7.2. Possible further works
Even though the analysis performed here is highly detailed, there are some points that could be
improved and studied deeply to increase simulations complexity. One of these points is surely the
interference problem; close satellites can have link loss problems for signal frequency interferences
due to Doppler shift. A possible solution suggested could be the use of different communication
channels, with frequencies quite different from each other however this is not every time possible.
Number of channels, and also the channels management by ground and space segment could be
investigate deeply in further works. Another point that deserves to be investigated is the
communication during re-entry phase. For “re-entry phase”, which is considered the last phase of
the mission, it is very important have informations during this mission phase, but the main
constrain is its short duration, and the black-out due to the plasma sheet forming in front of the
vehicle after the bow-shock. A re-entry lifetime is in the order of some minutes, and often it is not
easy guarantee a ground station able to receive data for this period due to black-out or re-entry over
oceans. One possible idea could be to send back data to the space, to another formation of satellites,
like IRIDIUM constellation, and finally send data from the constellation to Earth’s ground.
IRIDIUM could be a very interesting idea, this constellation is a large group of satellites providing
voice and data coverage over Earth's entire surface. The constellation consists of more than 70
satellites in orbit at a height of approximately 780 km, and inclination of 86.4°. This or other ideas
can be studied in depth, and possible changes in ground and space segments can be developed. One
last improvement that could be included in the simulations is the eclipses presence, with all the
related considerations for power consumptions of the communication system, and the possibility to
supply energy to communication subsystem during all mission phases. For more detailed
simulation, also the sensor unit operation scheme can be utilized to improve further results.




                                    Figure 7.1: IRIDIUM Constellation

<!-- PDF_PAGE: 161 -->

Conclusions and further works   161

<!-- PDF_PAGE: 162 -->

162                                                                              List of references




List of references


[1] J. Puig-Suari, “CubeSat Design Specification (CDS)”, California Polytechnic State University,
2nd CubeSat Program Conference, San Luis Obispo CA, 2009.

[2] M. Schmidt, “Ground Station Networks for Efficient Operation of Distributed Small Satellite
Systems”, “Distributed Space Missions for Earth System Monitoring”, International Academy of
Astronautics, Springer Verlag, 2012.

[3] V. Dascal, P. Dolea, T. Palade, O. Cristea, “Aspects Of A Low-Cost Ground Station
Development For Genso Network”; Volume 52, Number 4, Acta Technica Napocensis, Electronics
and Telecommunications, 2011.

[4] www.qb50.eu, access June 1st, 2013.

[5] Marc Vila Fernández, “Mission analysis of QB50, a nanosatellites intended to study the lower
thermosphere”, Final Project, Academic year 2010-2011, University of Liège, 2011.

[6] G. Bailet, “Feasibility Analysis and Conceptual design of an atmospheric re-entry CubeSat
demonstrator”, Research Master Project, von Karman Institute, 2011.

[7] “User’s Guide Cyclone-4 launch Vehicle (Issue 1, October 2010)”, Alcantara Cyclone Space.

[8] Aristeidis Iliopoulos, “Case study of different configurations of the deployment system for the
QB50 project”, Short Training Program Project, von Karman Institute, June 2013.

[9] “Antenna Basics”, http://wireless.ictp.trieste.it/handbook/C4.pdf

[10] http://www.esa.int/ESA, access April 1st, 2013.

[11] https://directory.eoportal.org, access June 1st, 2013.

[12] C. Kilic, “Development of deployment strategies for QB50”, Short Training Program Project,
von Karman Institute, 2011.

[13] W. Larson et al., “Space Mission Analysis and Design”, Third Edition, Microcosm, 1999.

[14] Berlin P., “Satellite Platform Design”, Fourth Edition. Lulea and Umea: Department of Space
Science of the University of Lulea and Umea, 2005.

<!-- PDF_PAGE: 163 -->

List of references                                                                        163



[15] M. Dennison, C. Lorek, “Radio Communication Handbook”, Radio Society of Grate Britain,
2005.

[16] http://hyperphysics.phy-astr.gsu.edu/hbase/phyopt/polclas.html, 25-5-2007.

[17] http://electronicdesign.com, access June 1st, 2013.

[18] “G-5500 Antenna Azimuth-Elevation Rotators & Controller Instruction Manual”, 1998.

[19] Vanhoenacker D., Vasseur H., Amaya C., and Vander Vorst A., "Atmospheric model for cloud
produced scintillation and evaluation of its impact on communication signals" E.S.A. Purchase
Order nr. 113272, Microwave Laboratory, U.C. Louvain-la-Neuve, July 1993.

[20] Louis J. Ippolito, “Propagation Effects Handbook for Satellite Systems Design”, Fift edition.
Stanford Telecom ACS. Prepared for JPL Jet Propulsion Laboratory, Pasadena, CA, February
1999.

[21] www.amsat.org, AMSAT/IARU Datasheets, access April 1st, 2013.

[22] complextoreal.com, access May 1st, 2013.

[23] gomspace.com, access April 1st, 2013.

[24] S. Eagleson, K. Sarda, S. Mauthe, T. Tuli, R. E. Zee, “Adaptable, Multi-Mission Design of
CanX Nanosatellites”. Proceedings of the 20th Annual AIAA/USU Conference on Small Satellites,
Logan, UT, Aug. 14-17, 2006, paper: SSC06-VII-3.

<!-- PDF_PAGE: 164 -->

164                                                       Annex A




Annex A

Access with rotator simulation
(CubeSat_1-S-band)

       Time (UTCG)         Accumulated_data_S-Band (Mb)
------------------------   ----------------------------
15 Apr 2015 11:00:00.000                       0.000000
16 Apr 2015 11:00:00.000                     316.249087
17 Apr 2015 11:00:00.000                     715.800276
18 Apr 2015 11:00:00.000                    1076.768236
19 Apr 2015 11:00:00.000                    1462.122844
20 Apr 2015 11:00:00.000                    1811.579981
21 Apr 2015 11:00:00.000                    2155.478335
22 Apr 2015 11:00:00.000                    2560.502325
23 Apr 2015 11:00:00.000                    2859.658766
24 Apr 2015 11:00:00.000                    3145.336638
25 Apr 2015 11:00:00.000                    3545.684398
26 Apr 2015 11:00:00.000                    3890.938299
27 Apr 2015 11:00:00.000                    4229.721675
28 Apr 2015 11:00:00.000                    4610.186510
29 Apr 2015 11:00:00.000                    4963.905017
30 Apr 2015 11:00:00.000                    5333.260049
 1 May 2015 11:00:00.000                    5868.390649
 2 May 2015 11:00:00.000                    6150.075280
 3 May 2015 11:00:00.000                    6403.612488
 4 May 2015 11:00:00.000                    6920.311158
 5 May 2015 11:00:00.000                    7261.598365
 6 May 2015 11:00:00.000                    7508.013158
 7 May 2015 11:00:00.000                    7920.384508
 8 May 2015 11:00:00.000                    8240.020955
 9 May 2015 11:00:00.000                    8461.087177
10 May 2015 11:00:00.000                    8870.795104
11 May 2015 11:00:00.000                    9180.221440
12 May 2015 11:00:00.000                    9395.262781
13 May 2015 11:00:00.000                    9800.730573
14 May 2015 11:00:00.000                   10114.492247
15 May 2015 11:00:00.000                   10348.383757
16 May 2015 11:00:00.000                   10747.409846
17 May 2015 11:00:00.000                   11077.541236
18 May 2015 11:00:00.000                   11331.904636
19 May 2015 11:00:00.000                   11719.737379
20 May 2015 11:00:00.000                   12072.185942
21 May 2015 11:00:00.000                   12337.256992
22 May 2015 11:00:00.000                   12703.932648

<!-- PDF_PAGE: 165 -->

Annex A                                   165



23 May 2015 11:00:00.000   13069.146484
24 May 2015 11:00:00.000   13322.181156
25 May 2015 11:00:00.000   13646.808886
26 May 2015 11:00:00.000   14035.354350
27 May 2015 11:00:00.000   14215.601400
28 May 2015 11:00:00.000   14421.959214
29 May 2015 11:00:00.000   14809.742496
30 May 2015 11:00:00.000   15115.665725
31 May 2015 11:00:00.000   15365.572330
 1 Jun 2015 11:00:00.000   15715.924858
 2 Jun 2015 11:00:00.000   16081.697184
 3 Jun 2015 11:00:00.000   16313.429471
 4 Jun 2015 11:00:00.000   16578.446565
 5 Jun 2015 11:00:00.000   16960.998263
 6 Jun 2015 11:00:00.000   17246.316626
 7 Jun 2015 11:00:00.000   17493.093831
 8 Jun 2015 11:00:00.000   17832.839084
 9 Jun 2015 11:00:00.000   18201.054835
10 Jun 2015 11:00:00.000   18372.496937
11 Jun 2015 11:00:00.000   18548.516482
12 Jun 2015 11:00:00.000   18916.082333
13 Jun 2015 11:00:00.000   19250.025282
14 Jun 2015 11:00:00.000   19490.926304
15 Jun 2015 11:00:00.000   19709.518289
16 Jun 2015 11:00:00.000   20080.840692
17 Jun 2015 11:00:00.000   20401.693889
18 Jun 2015 11:00:00.000   20651.682111
19 Jun 2015 11:00:00.000   20887.346525
20 Jun 2015 11:00:00.000   21256.032952
21 Jun 2015 11:00:00.000   21577.715468
22 Jun 2015 11:00:00.000   21822.685814
23 Jun 2015 11:00:00.000   22006.258598
24 Jun 2015 11:00:00.000   22365.920544
25 Jun 2015 11:00:00.000   22719.913387
26 Jun 2015 11:00:00.000   22886.198490
27 Jun 2015 11:00:00.000   23081.666177
28 Jun 2015 11:00:00.000   23401.521306
29 Jun 2015 11:00:00.000   23762.881651
30 Jun 2015 11:00:00.000   24141.745649
 1 Jul 2015 11:00:00.000   24458.014081
 2 Jul 2015 11:00:00.000   24650.947094
 3 Jul 2015 11:00:00.000   24964.119050
 4 Jul 2015 11:00:00.000   25153.246804
 5 Jul 2015 11:00:00.000   25470.635104
 6 Jul 2015 11:00:00.000   25772.533075
 7 Jul 2015 11:00:00.000   25963.147486
 8 Jul 2015 11:00:00.000   26274.686831
 9 Jul 2015 11:00:00.000   26461.549905
10 Jul 2015 11:00:00.000   26759.864972
11 Jul 2015 11:00:00.000   27072.614048
12 Jul 2015 11:00:00.000   27256.567149
13 Jul 2015 11:00:00.000   27551.734503
14 Jul 2015 11:00:00.000   27846.062808
15 Jul 2015 11:00:00.000   28026.992677
16 Jul 2015 11:00:00.000   28328.214934
17 Jul 2015 11:00:00.000   28627.641232
18 Jul 2015 11:00:00.000   28804.981624
19 Jul 2015 11:00:00.000   29083.299115
20 Jul 2015 11:00:00.000   29384.534772

<!-- PDF_PAGE: 166 -->

166                                       Annex A



21 Jul 2015 11:00:00.000   29597.210522
22 Jul 2015 11:00:00.000   29808.914953
23 Jul 2015 11:00:00.000   30102.444069
24 Jul 2015 11:00:00.000   30385.615741
25 Jul 2015 11:00:00.000   30564.744748
26 Jul 2015 11:00:00.000   30781.081359
27 Jul 2015 11:00:00.000   31069.867689
28 Jul 2015 11:00:00.000   31357.820093
29 Jul 2015 11:00:00.000   31586.685663
30 Jul 2015 11:00:00.000   31755.394127
31 Jul 2015 11:00:00.000   31957.197763
 1 Aug 2015 11:00:00.000   32218.291770
 2 Aug 2015 11:00:00.000   32484.705534
 3 Aug 2015 11:00:00.000   32729.720859
 4 Aug 2015 11:00:00.000   32891.075719
 5 Aug 2015 11:00:00.000   33056.024457
 6 Aug 2015 11:00:00.000   33213.427238
 7 Aug 2015 11:00:00.000   33376.227707
 8 Aug 2015 11:00:00.000   33582.548686
 9 Aug 2015 11:00:00.000   33810.290161
10 Aug 2015 11:00:00.000   34044.569312
11 Aug 2015 11:00:00.000   34277.280544
12 Aug 2015 11:00:00.000   34500.413975
13 Aug 2015 11:00:00.000   34699.015906
14 Aug 2015 11:00:00.000   34847.282204
15 Aug 2015 11:00:00.000   34984.516045
16 Aug 2015 11:00:00.000   35119.401647
17 Aug 2015 11:00:00.000   35228.000559
18 Aug 2015 11:00:00.000   35307.607889
19 Aug 2015 11:00:00.000   35429.216629
20 Aug 2015 11:00:00.000   35585.456453
21 Aug 2015 11:00:00.000   35585.456453
22 Aug 2015 11:00:00.000   35585.456453
23 Aug 2015 11:00:00.000   35585.456453
24 Aug 2015 11:00:00.000   35585.456453
25 Aug 2015 11:00:00.000   35585.456453
26 Aug 2015 11:00:00.000   35585.456453
27 Aug 2015 11:00:00.000   35585.456453
28 Aug 2015 11:00:00.000   35585.456453
29 Aug 2015 11:00:00.000   35585.456453
30 Aug 2015 11:00:00.000   35585.456453
31 Aug 2015 11:00:00.000   35585.456453
 1 Sep 2015 11:00:00.000   35585.456453
 2 Sep 2015 11:00:00.000   35585.456453
 3 Sep 2015 11:00:00.000   35585.456453
 4 Sep 2015 11:00:00.000   35585.456453
 5 Sep 2015 11:00:00.000   35585.456453
 6 Sep 2015 11:00:00.000   35585.456453
 7 Sep 2015 11:00:00.000   35585.456453
 8 Sep 2015 11:00:00.000   35585.456453
 9 Sep 2015 11:00:00.000   35585.456453
10 Sep 2015 11:00:00.000   35585.456453
11 Sep 2015 11:00:00.000   35585.456453
12 Sep 2015 11:00:00.000   35585.456453
13 Sep 2015 11:00:00.000   35585.456453
14 Sep 2015 11:00:00.000   35585.456453
15 Sep 2015 11:00:00.000   35585.456453

<!-- PDF_PAGE: 167 -->

Annex A                                                    167




Access with rotator simulation
(CubeSat_1-UHF/VHF)

       Time (UTCG)         Accumulated_data_UHF_VHF (Mb)
------------------------   -----------------------------
15 Apr 2015 11:00:00.000                        0.000000
16 Apr 2015 11:00:00.000                        3.035991
17 Apr 2015 11:00:00.000                        6.871683
18 Apr 2015 11:00:00.000                       10.336975
19 Apr 2015 11:00:00.000                       14.036379
20 Apr 2015 11:00:00.000                       17.391168
21 Apr 2015 11:00:00.000                       20.692592
22 Apr 2015 11:00:00.000                       24.580822
23 Apr 2015 11:00:00.000                       27.452724
24 Apr 2015 11:00:00.000                       30.195232
25 Apr 2015 11:00:00.000                       34.038570
26 Apr 2015 11:00:00.000                       37.353008
27 Apr 2015 11:00:00.000                       40.605328
28 Apr 2015 11:00:00.000                       44.257790
29 Apr 2015 11:00:00.000                       47.653488
30 Apr 2015 11:00:00.000                       51.199296
 1 May 2015 11:00:00.000                       56.336550
 2 May 2015 11:00:00.000                       59.040723
 3 May 2015 11:00:00.000                       61.474680
 4 May 2015 11:00:00.000                       66.434987
 5 May 2015 11:00:00.000                       69.711344
 6 May 2015 11:00:00.000                       72.076926
 7 May 2015 11:00:00.000                       76.035691
 8 May 2015 11:00:00.000                       79.104201
 9 May 2015 11:00:00.000                       81.226437
10 May 2015 11:00:00.000                       85.159633
11 May 2015 11:00:00.000                       88.130126
12 May 2015 11:00:00.000                       90.194523
13 May 2015 11:00:00.000                       94.087014
14 May 2015 11:00:00.000                       97.099126
15 May 2015 11:00:00.000                       99.344484
16 May 2015 11:00:00.000                      103.175135
17 May 2015 11:00:00.000                      106.344396
18 May 2015 11:00:00.000                      108.786285
19 May 2015 11:00:00.000                      112.509479
20 May 2015 11:00:00.000                      115.892985
21 May 2015 11:00:00.000                      118.437667
22 May 2015 11:00:00.000                      121.957753
23 May 2015 11:00:00.000                      125.463806
24 May 2015 11:00:00.000                      127.892939
25 May 2015 11:00:00.000                      131.009365
26 May 2015 11:00:00.000                      134.739402
27 May 2015 11:00:00.000                      136.469773
28 May 2015 11:00:00.000                      138.450808

<!-- PDF_PAGE: 168 -->

168                                     Annex A



29 May 2015 11:00:00.000   142.173528
30 May 2015 11:00:00.000   145.110391
31 May 2015 11:00:00.000   147.509494
 1 Jun 2015 11:00:00.000   150.872879
 2 Jun 2015 11:00:00.000   154.384293
 3 Jun 2015 11:00:00.000   156.608923
 4 Jun 2015 11:00:00.000   159.153087
 5 Jun 2015 11:00:00.000   162.825583
 6 Jun 2015 11:00:00.000   165.564640
 7 Jun 2015 11:00:00.000   167.933701
 8 Jun 2015 11:00:00.000   171.195255
 9 Jun 2015 11:00:00.000   174.730126
10 Jun 2015 11:00:00.000   176.375971
11 Jun 2015 11:00:00.000   178.065758
12 Jun 2015 11:00:00.000   181.594390
13 Jun 2015 11:00:00.000   184.800243
14 Jun 2015 11:00:00.000   187.112893
15 Jun 2015 11:00:00.000   189.211376
16 Jun 2015 11:00:00.000   192.776071
17 Jun 2015 11:00:00.000   195.856261
18 Jun 2015 11:00:00.000   198.256148
19 Jun 2015 11:00:00.000   200.518527
20 Jun 2015 11:00:00.000   204.057916
21 Jun 2015 11:00:00.000   207.146068
22 Jun 2015 11:00:00.000   209.497784
23 Jun 2015 11:00:00.000   211.260083
24 Jun 2015 11:00:00.000   214.712837
25 Jun 2015 11:00:00.000   218.111169
26 Jun 2015 11:00:00.000   219.707506
27 Jun 2015 11:00:00.000   221.583995
28 Jun 2015 11:00:00.000   224.654605
29 Jun 2015 11:00:00.000   228.123664
30 Jun 2015 11:00:00.000   231.760758
 1 Jul 2015 11:00:00.000   234.796935
 2 Jul 2015 11:00:00.000   236.649092
 3 Jul 2015 11:00:00.000   239.655543
 4 Jul 2015 11:00:00.000   241.471169
 5 Jul 2015 11:00:00.000   244.518097
 6 Jul 2015 11:00:00.000   247.416318
 7 Jul 2015 11:00:00.000   249.246216
 8 Jul 2015 11:00:00.000   252.236994
 9 Jul 2015 11:00:00.000   254.030879
10 Jul 2015 11:00:00.000   256.894704
11 Jul 2015 11:00:00.000   259.897095
12 Jul 2015 11:00:00.000   261.663045
13 Jul 2015 11:00:00.000   264.496651
14 Jul 2015 11:00:00.000   267.322203
15 Jul 2015 11:00:00.000   269.059130
16 Jul 2015 11:00:00.000   271.950863
17 Jul 2015 11:00:00.000   274.825356
18 Jul 2015 11:00:00.000   276.527824
19 Jul 2015 11:00:00.000   279.199671
20 Jul 2015 11:00:00.000   282.091534
21 Jul 2015 11:00:00.000   284.133221
22 Jul 2015 11:00:00.000   286.165584
23 Jul 2015 11:00:00.000   288.983463
24 Jul 2015 11:00:00.000   291.701911
25 Jul 2015 11:00:00.000   293.421550
26 Jul 2015 11:00:00.000   295.498381

<!-- PDF_PAGE: 169 -->

Annex A                                 169



27 Jul 2015 11:00:00.000   298.270730
28 Jul 2015 11:00:00.000   301.035073
29 Jul 2015 11:00:00.000   303.232182
30 Jul 2015 11:00:00.000   304.851784
31 Jul 2015 11:00:00.000   306.789099
 1 Aug 2015 11:00:00.000   309.295601
 2 Aug 2015 11:00:00.000   311.853173
 3 Aug 2015 11:00:00.000   314.205320
 4 Aug 2015 11:00:00.000   315.754327
 5 Aug 2015 11:00:00.000   317.337835
 6 Aug 2015 11:00:00.000   318.848901
 7 Aug 2015 11:00:00.000   320.411786
 8 Aug 2015 11:00:00.000   322.392467
 9 Aug 2015 11:00:00.000   324.578786
10 Aug 2015 11:00:00.000   326.827865
11 Aug 2015 11:00:00.000   329.061893
12 Aug 2015 11:00:00.000   331.203974
13 Aug 2015 11:00:00.000   333.110553
14 Aug 2015 11:00:00.000   334.533909
15 Aug 2015 11:00:00.000   335.851354
16 Aug 2015 11:00:00.000   337.146256
17 Aug 2015 11:00:00.000   338.188805
18 Aug 2015 11:00:00.000   338.953036
19 Aug 2015 11:00:00.000   340.120480
20 Aug 2015 11:00:00.000   341.620382
21 Aug 2015 11:00:00.000   341.620382
22 Aug 2015 11:00:00.000   341.620382
23 Aug 2015 11:00:00.000   341.620382
24 Aug 2015 11:00:00.000   341.620382
25 Aug 2015 11:00:00.000   341.620382
26 Aug 2015 11:00:00.000   341.620382
27 Aug 2015 11:00:00.000   341.620382
28 Aug 2015 11:00:00.000   341.620382
29 Aug 2015 11:00:00.000   341.620382
30 Aug 2015 11:00:00.000   341.620382
31 Aug 2015 11:00:00.000   341.620382
 1 Sep 2015 11:00:00.000   341.620382
 2 Sep 2015 11:00:00.000   341.620382
 3 Sep 2015 11:00:00.000   341.620382
 4 Sep 2015 11:00:00.000   341.620382
 5 Sep 2015 11:00:00.000   341.620382
 6 Sep 2015 11:00:00.000   341.620382
 7 Sep 2015 11:00:00.000   341.620382
 8 Sep 2015 11:00:00.000   341.620382
 9 Sep 2015 11:00:00.000   341.620382
10 Sep 2015 11:00:00.000   341.620382
11 Sep 2015 11:00:00.000   341.620382
12 Sep 2015 11:00:00.000   341.620382
13 Sep 2015 11:00:00.000   341.620382
14 Sep 2015 11:00:00.000   341.620382
15 Sep 2015 11:00:00.000   341.620382

<!-- PDF_PAGE: 170 -->

170   Annex AB

<!-- PDF_PAGE: 171 -->

Annex A                                                                                                               171




Annex B


Combinations Analysis Cases

Case 1     1    0    0    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 2     6    0    0    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 3    13    0    0    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 4    20    0    0    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 5     1   13    0    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 6    28    3    0    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 7     7   21    0    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 8    13   17    0    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 9     7   13    3    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 10   12   17    2    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 11   25    9    1    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 12   24    7    2    0    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 13    6   13   23   21    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 14   25   20    9    1    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 15   28    1   13    3    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 16    7    3   18   24    0    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 17    1    7    8    2   13    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 18   19   28   21    2   17    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 19    1    7   12    9   20    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 20   13   20   17    2    3    0    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 21    1    6   21    3    8   14    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 22   15   19   23   13    7   25    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 23    4    7   18   22   25   21    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 24   26    3   28   12   24   16    0    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 25   11   14   16    7    3   15    8    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 26   26   16    6   17   28   23    4    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 27   13   11   21   23    3    7    1    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 28    1   13   17    8    2    3   28    0    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 29   28    3    6    8    4   12   13   18    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 30    6   25   21   17    2    1    7   28    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 31   28    4    5   14   22   20   23    3    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 32   11    6   22   20   26    7    1   28    0    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 33    7    1   13    2   17    8   15   12    6    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 34   19   28    2    3   12   20   22   21   17    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 35    1   20   13    9   23    5    6   11   21    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 36    7   22    6   16    2    8   24   15    1    0    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 37   12   16   25   24    1    3    4   26   11   20    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 38    4   18   22   28    1   19    7    2   17    8    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 39   21   12   22   20   16    8    1   19    7   28    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 40    4   21   20    2    1    7   22   16    6   10    0    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 41   28    3    6    8    4   12   13   18   19   14    1    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 42    6   25   21   17    2    1    7   28   19   24    3    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 43   28    4    5   14   22   20   23    3   19   24    1    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 44   11    6   22   20   26    7    1   28   25    2   24    0   0   0   0   0   0   0   0   0   0   0   0   0   0
Case 45   20   13   21    8    2    1   28   11   14   24   12   23   0   0   0   0   0   0   0   0   0   0   0   0   0

<!-- PDF_PAGE: 172 -->

172                                                                                                                  Annex AB




Case 46    22    8    2   17    3   19    7    6   16   25   23    1    0    0    0    0    0    0    0    0    0    0    0    0    0
Case 47    26    1    2    4    5    8   12   15   17   19   20   28    0    0    0    0    0    0    0    0    0    0    0    0    0
Case 48     3    6    7    9   10   11   13   14   16   18   22   27    0    0    0    0    0    0    0    0    0    0    0    0    0
Case 49     1    3    6    7   11   13   14   16   19   20   23   24   28    0    0    0    0    0    0    0    0    0    0    0    0
Case 50     2    4    8    9   10   12   15   17   20   22   25   26   27    0    0    0    0    0    0    0    0    0    0    0    0
Case 51     4    6    9   10   12   14   16   18   19   20   22   25   26    0    0    0    0    0    0    0    0    0    0    0    0
Case 52     7    8   10   11   14   18   22   23   24   25   26   27   28    0    0    0    0    0    0    0    0    0    0    0    0
Case 53     1    3    6    7   11   13   14   16   19   20   23   24   28    2    0    0    0    0    0    0    0    0    0    0    0
Case 54     2    4    8    9   10   12   15   17   20   22   25   26   27    3    0    0    0    0    0    0    0    0    0    0    0
Case 55     4    6    9   10   12   14   16   18   19   20   22   25   26    5    0    0    0    0    0    0    0    0    0    0    0
Case 56     7    8   10   11   14   18   22   23   24   25   26   27   28    1    0    0    0    0    0    0    0    0    0    0    0
Case 57     1    3    6    7   11   13   14   16   19   20   23   24   28    2    5    0    0    0    0    0    0    0    0    0    0
Case 58     2    4    8    9   10   12   15   17   20   22   25   26   27    3    7    0    0    0    0    0    0    0    0    0    0
Case 59     4    6    9   10   12   14   16   18   19   20   22   25   26    5    8    0    0    0    0    0    0    0    0    0    0
Case 60     7    8   10   11   14   18   22   23   24   25   26   27   28    1    9    0    0    0    0    0    0    0    0    0    0
Case 61     1    3    6    7   11   13   14   16   19   20   23   24   28    2    5    8    0    0    0    0    0    0    0    0    0
Case 62     2    4    8    9   10   12   15   17   20   22   25   26   27    3    7   11    0    0    0    0    0    0    0    0    0
Case 63     4    6    9   10   12   14   16   18   19   20   22   25   26    5    8   11    0    0    0    0    0    0    0    0    0
Case 64     7    8   10   11   14   18   22   23   24   25   26   27   28    1    9   12    0    0    0    0    0    0    0    0    0
Case 65     1    3    6    7   11   13   14   16   19   20   23   24   28    2    5    8    9    0    0    0    0    0    0    0    0
Case 66     2    4    8    9   10   12   15   17   20   22   25   26   27    3    7   11   13    0    0    0    0    0    0    0    0
Case 67     4    6    9   10   12   14   16   18   19   20   22   25   26    5    8   11   13    0    0    0    0    0    0    0    0
Case 68     7    8   10   11   14   18   22   23   24   25   26   27   28    1    9   12   13    0    0    0    0    0    0    0    0
Case 69     1    3    6    7   11   13   14   16   19   20   23   24   28    2    5    8    9   12    0    0    0    0    0    0    0
Case 70     2    4    8    9   10   12   15   17   20   22   25   26   27    3    7   11   13   14    0    0    0    0    0    0    0
Case 71     4    6    9   10   12   14   16   18   19   20   22   25   26    5    8   11   13   15    0    0    0    0    0    0    0
Case 72     7    8   10   11   14   18   22   23   24   25   26   27   28    1    9   12   13   16    0    0    0    0    0    0    0
Case 73     1    3    6    7   11   13   14   16   19   20   23   24   28    2    5    8    9   12   15    0    0    0    0    0    0
Case 74     2    4    8    9   10   12   15   17   20   22   25   26   27    3    7   11   13   14   16    0    0    0    0    0    0
Case 75     4    6    9   10   12   14   16   18   19   20   22   25   26    5    8   11   13   15   17    0    0    0    0    0    0
Case 76     7    8   10   11   14   18   22   23   24   25   26   27   28    1    9   12   13   16   19    0    0    0    0    0    0
Case 77     1    3    6    7   11   13   14   16   19   20   23   24   28    2    5    8    9   12   15   17    0    0    0    0    0
Case 78     2    4    8    9   10   12   15   17   20   22   25   26   27    3    7   11   13   14   16   19    0    0    0    0    0
Case 79     4    6    9   10   12   14   16   18   19   20   22   25   26    5    8   11   13   15   17   27    0    0    0    0    0
Case 80     7    8   10   11   14   18   22   23   24   25   26   27   28    1    9   12   13   16   19   21    0    0    0    0    0
Case 81     1    3    6    7   11   13   14   16   19   20   23   24   28    2    5    8    9   12   15   17   18    0    0    0    0
Case 82     2    4    8    9   10   12   15   17   20   22   25   26   27    3    7   11   13   14   16   19   21    0    0    0    0
Case 83     4    6    9   10   12   14   16   18   19   20   22   25   26    5    8   11   13   15   17   27   28    0    0    0    0
Case 84     7    8   10   11   14   18   22   23   24   25   26   27   28    1    9   12   13   16   19   21    1    0    0    0    0
Case 85     1    2   28    4    5    6    7    8   27   10   11   12   13   14   15   26   17   18   19   20   24   22    0    0    0
Case 86     1   28    3    4    5    6    7    8   23   10   11   12   13   24   15   16   17   18   19   20   21   22    0    0    0
Case 87     1    2    3    4    5    6    7   23    9   10   25   12   13   14   15   26   17   27   19   20   28   27    0    0    0
Case 88     2    3    4    5    6   24    8    9   10   11   26   13   14   15   16   27   18   19   28   21   22   23    0    0    0
Case 89    23    2    3    4   24    6    7    8    9   25   11   12   13   14   28   16   17   18   19   20   21   22   27    0    0
Case 90     1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18   19   20   21   22   23    0    0
Case 91     1    2   25    4    5    6    7   26    9   10   11   12   13   14   15   16   17   18   19   20   21   22   24    0    0
Case 92     1    2    3   28    5    6    7    8    9   10   11   12   27   14   15   16   17   18   19   20   21   22   23    0    0
Case 93     1    2    3    4   25    6    7    8    9   27   11   12   13   14   15   28   17   18   19   20   21   22   23   24    0
Case 94     1    2    3    4    5    6    7    8   26   10   11   12   13   27   15   16   17   18   19   28   21   22   23   24    0
Case 95     1    2    3    4    5    6   25    8    9   10   11   27   13   14   15   16   17   18   19   20   28   22   23   24    0
Case 96     1    2    3    4    5    6    7    8    9   10   27   12   13   14   15   16   17   18   19   20   21   22   23   24    0
Case 97    27   28    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18   19   20   21   22   23   24   25
Case 98    26    2    3    4   28    6    7    8    9   10   11   12   13   14   15   16   17   18   19   20   21   22   23   24   25
Case 99     1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18   19   20   21   22   23   24   25
Case 100    1    2    3    4    5    6   27    8    9   10   11   12   13   14   28   16   17   18   19   20   21   22   23   24   25

## Figures

![figure_001.png](figure_001.png)
