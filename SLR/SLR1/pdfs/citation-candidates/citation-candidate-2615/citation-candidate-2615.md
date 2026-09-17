---
source: null
title: "citation-candidate-2615"
page_count: 26
converted_at: "2026-09-08T16:30:51Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# FORESAIL-1 cubesat mission to measure radiation belt losses and demonstrate de-orbiting

</div>

M. Palmroth $ ^{1,2} $ , J. Praks $ ^{3} $ , R. Vainio $ ^{4} $ , P. Janhunen $ ^{2} $ , E. K. J. Kilpua $ ^{1} $ , N. Yu. Ganushkina $ ^{2,5} $ , A. Afanasiev $ ^{4} $ , M. Ala-Lahti $ ^{1} $ , A. Alho $ ^{3} $ , T. Asikainen $ ^{6} $ , E. Asvestari $ ^{1} $ , M. Battarbee $ ^{1} $ , A. Binios $ ^{3} $ , A. Bosser $ ^{3} $ , T. Brito $ ^{1} $ , J. Envall $ ^{2} $ U. Ganse $ ^{1} $ , H. George $ ^{1} $ , J. Gieseler $ ^{4} $ , S. Good $ ^{1} $ , M. Grandin $ ^{1} $ , S. Haslam $ ^{2} $ H.-P. Hedman $ ^{7} $ , H. Hietala $ ^{4} $ , N. Jovanovic $ ^{3} $ , S. Kakakhel $ ^{7} $ , M. Kalliokoski $ ^{1} $ V. V. Kettunen $ ^{3} $ , T. Koskela $ ^{1,4} $ , E. Lumme $ ^{1} $ , M. Meskanen $ ^{2} $ , D. Morosan $ ^{1} $ M. Rizwan Mughal $ ^{3} $ , P. Niemelä $ ^{3} $ , S. Nyman $ ^{3} $ , P. Oleynik $ ^{4} $ , A. Osman $ ^{1} $ E. Palmerio $ ^{1} $ , Y. Pfau-Kempf $ ^{1} $ , J. Peltonen $ ^{4} $ , J. Plosila $ ^{7} $ , J. Polkko $ ^{2} $ S. Poluianov $ ^{6,8} $ , J. Pomoell $ ^{1} $ , D. Price $ ^{1} $ , A. Punkkinen $ ^{4} $ , R. Punkkinen $ ^{7} $ B. Riwanto $ ^{3} $ , L. Salomaa $ ^{7} $ , A. Slavinskis $ ^{3,9} $ , T. Santti $ ^{7} $ , J. Tammi $ ^{7} $ H. Tenhunen $ ^{7} $ , P. Toivanen $ ^{2} $ , J. Tuominen $ ^{7} $ , L. Turc $ ^{1} $ , E. Valtonen $ ^{4} $ P. Virtanen $ ^{4} $ , T. Westerlund $ ^{7} $

$ ^{1} $University of Helsinki, Department of Physics, Helsinki, Finland $ ^{2} $Finnish Meteorological Institute, Space and Earth Observation Centre, Helsinki, Finland $ ^{3} $Aalto University, School of Electrical Engineering, Espoo, Finland $ ^{4} $University of Turku, Department of Physics and Astronomy, Turku, Finland $ ^{5} $University of Michigan, Department of Climate and Space Sciences and Engineering, Ann Arbor, USA $ ^{6} $University of Oulu, Space Climate Research Unit, Oulu, Finland $ ^{7} $University of Turku, Department of Future Technologies, Turku, Finland $ ^{8} $University of Oulu, Sodankylä Geophysical Observatory (Oulu Unit), Oulu, Finland $ ^{9} $University of Tartu, Tartu Observatory, Tõravere, Estonia

## Key Points:

- FORESAIL-1 mission measures energetic electron precipitation and solar energetic neutral atom flux

- We will demonstrate a cost-efficient de-orbiting and orbit manoeuvring technology without propellants

- The goal of the mission is to contribute significantly to the sustainable utilisation of space

<!-- PDF_PAGE: 2 -->

## Abstract

Today, the near-Earth space is facing a paradigm change as the number of new spacecraft is literally sky-rocketing. Increasing numbers of small satellites threaten the sustainable use of space, as without removal, space debris will eventually make certain critical orbits unusable. A central factor affecting small spacecraft health and leading to debris is the radiation environment, which is unpredictable due to an incomplete understanding of the near-Earth radiation environment itself and its variability driven by the solar wind and outer magnetosphere. This paper presents the FORESAIL-1 nanosatellite mission, having two scientific and one technological objectives. The first scientific objective is to measure the energy and flux of energetic particle loss to the atmosphere with a representative energy and pitch angle resolution over a wide range of magnetic local times. To pave the way to novel model - in situ data comparisons, we also show preliminary results on precipitating electron fluxes obtained with the new global hybrid-Vlasov simulation Vlasiator. The second scientific objective of the FORESAIL-1 mission is to measure energetic neutral atoms (ENAs) of solar origin. The solar ENA flux has the potential to contribute importantly to the knowledge of solar eruption energy budget estimations. The technological objective is to demonstrate a satellite de-orbiting technology, and for the first time, make an orbit manoeuvre with a propellantless nanosatellite. FORESAIL-1 will demonstrate the potential for nanosatellites to make important scientific contributions as well as promote the sustainable utilisation of space by using a cost-efficient de-orbiting technology.

## 1 Introduction

Unprecedented numbers of new spacecraft are now being launched into Earth orbit to satisfy the growing demand from the scientific, commercial, and military sectors. Most of these new spacecraft need to survive in the radiation belts (RBs; van Allen & Frank, 1959), which are regions of trapped energetic charged particles. The RBs are critical in terms of space weather, as the radiation ages the spacecraft and deteriorates hardware. All new satellites contribute to the already existing large number of orbital debris, if they are not actively removed at the end of the mission. This section introduces the state of the art in the three scientific and technological objectives of the FORESAIL-1 mission: measurements of energetic particle precipitation and solar energetic neutral atoms (ENAs), and de-orbiting technologies.

## 1.1 State of the Art: Electron precipitation observations

The RBs are produced by a complex balance of particle source and loss processes that vary both temporally and spatially (e.g., Tverskoy, 1969; Walt, 1996; Chen et al., 2007; Shprits et al., 2008; Thorne, 2010). Significant variations in electron fluxes occur over various time scales as a function of both energy and distance, driven by solar-magnetospheric interactions and internal magnetospheric processes (e.g., Li et al., 1997; Elkington et al., 2003; Reeves et al., 2003; Shprits et al., 2006; Baker & Kanekal, 2008). Effective losses from the outer radiation belts consist of 1) loss through the outer edge of the magnetosphere (magnetopause shadowing (e.g., West et al., 1972; Ukhorskiy et al., 2006; Saito et al., 2010; Matsumura et al., 2011; Turner et al., 2014)) 2) radial outward displacement of the electrons due to waves (Mann et al., 2016), and weakening of the Earth's magnetic field (the $ D_{st} $ effect (McIlwain (1966); Kim & Chan (1997); Millan & Thorne (2007))), and 3) wave-particle interactions resulting in scattering of particles into the loss cone (Kennel & Petschek, 1966; Thorne & Kennel, 1971; Thorne, 1974). There are no comprehensive estimates about which of these processes is most important during different conditions, while it is clear that particle losses play a central part in regulating the RBs.

<!-- PDF_PAGE: 3 -->

The wave-particle interactions leading to losses from the RBs vary on time scales ranging from 100 milliseconds to several minutes (Millan & Thorne, 2007). Balloon experiments have historically been the earliest method to determine this loss category by measuring the X-rays from bremsstrahlung radiation induced by the interaction of precipitating particles with the neutrals in the upper atmosphere (Barcus et al., 1973; Pytte et al., 1976). Latest such observations are provided by the BARREL mission (Millan & the BARREL Team, 2011; Woodger et al., 2015). All balloon missions are constrained to balloon-reachable altitudes and thus only allow indirect observation of the precipitating particles.

Energetic particle precipitation has also been observed from the ground, as precipitating electrons with energies over several tens of keV cause enhanced ionisation in the ionospheric D-region at an altitude of about 90 km. Relative ionospheric opacity meters (riometers) (Hargreaves, 1969) are ground-based passive radars measuring the so-called cosmic noise absorption (Shain, 1951), which corresponds to absorbed radio wave power in the ionosphere resulting from enhanced D-region electron density. Recently, interferometric riometry has been developed to produce all-sky maps (e.g. McKay-Bukowski et al., 2015). Ground-based observations of energetic electron precipitation can also be achieved using incoherent scatter radars, which can accurately measure D-region electron density down to about 70 km altitude (e.g. Miyoshi et al., 2015). However, the intrinsically indirect ground-based observations do not allow inferring precipitating particle fluxes and energies, even using newly developed approaches such as spectral riometry (Kero et al., 2014). Hence having direct measurements of precipitating fluxes from space-borne instruments is critical for radiation belt loss studies.

One of the first satellite missions to study energetic electron precipitation was the Solar, Anomalous, and Magnetospheric Particle Explorer (SAMPEX, 1992-2012) used in a number of studies (Li et al., 2001; Tu et al., 2010; Nakamura et al., 2000). DEMETER microsatellite observed electron fluxes at energies between 70 keV and 2.5 MeV with high energy resolution (256 channels) on a 700 km orbit (Sauvaud et al., 2006). These observations have been used to infer energetic electron precipitation (Graf et al., 2009), although DEMETER viewed primarily trapped particles. The main data set of direct measurements of precipitating energetic particles comes from the Medium Energy Proton and Electron Detector (MEPED) onboard NOAA/POES satellites (D. S. Evans & Greer, 2000). MEPED consists of two telescopes, the $ 0^{\circ} $ telescope designed to measure precipitating particle fluxes and the $ 90^{\circ} $ telescope for trapped particle fluxes, measuring electrons in three energy channels (>30 keV, >100 keV, and >300 keV) and protons in five energy channels (>30 keV, >80 keV, >250 keV, >800 keV, and >2.5 MeV). However, the NOAA/POES particle data suffer from two issues. First, the $ 0^{\circ} $ telescope only partially views the bounce loss cone and does not offer any angular resolution inside its viewcone leading to poor pitch angle resolution. This leads to an underestimation of the precipitating fluxes (Rodger et al., 2013). Second, the electron channels are affected by proton contamination; partly corrected by a new data set by Asikainen & Mursula (2013).

Particle precipitation is a key element in magnetosphere-ionosphere-thermosphere coupling, and therefore a crucial objective for research in numerical models, especially as there is an increasing demand for space weather forecasting capabilities. The first attempts to model precipitating particle fluxes relied on statistical patterns inferred from satellite observations. McDiarmid et al. (1975) produced a model for precipitating electron flux within 0.15-200 keV as a function of magnetic local time (MLT) and invariant latitude based on about 1100 passes of the ISIS 2 spacecraft. Using data measured by the Low Energy Electron experiment onboard the Atmosphere Explorer C and D satellites, Spiro et al. (1982) parametrised precipitating electron energy flux and average energy as a function of MLT, geomagnetic latitude, and geomagnetic activity

<!-- PDF_PAGE: 4 -->

measured by the Kp and AE indices. One of the reference models for auroral-energy electron precipitation is the Hardy et al. (1985) model, empirically derived by compiling several years of observations from the Defense Meteorological Satellite Program and Satellite (DMSP) Test Program spacecraft. The Hardy model is parametrised by the Kp index, and it is still used to provide precipitation input in the 50 eV-20 keV energy range to state-of-the-art ionospheric models (e.g., Marchaudon & Blelly, 2015). At higher energies (30 keV-1 MeV), the recent van de Kamp et al. (2016) model provides energy-flux spectra of precipitating electrons as a function of L parameter and geomagnetic activity rendered with the Ap index. This empirical model was obtained from a statistical analysis of 11 years of NOAA/POES energetic electron precipitation observations and is averaged across all MLTs in its present version.

Modelling particle precipitation using first-principle models is not easy, given that many processes operating at spatial and temporal scales spanning many orders of magnitude are at play in the inner magnetosphere (energisation, and loss-cone scattering processes, among others). The emergence of global kinetic magnetospheric codes may enable addressing this issue in the near future. Recently, a preliminary run was performed using the Vlasiator code (von Alfthan et al., 2014; Palmroth et al., 2018), in which electrons were added as a modelled species during a substorm-time, polar-plane global magnetospheric run throughout the magnetospheric simulation box. Figure 1 shows an example of these preliminary results of $ 0. 1-6 0 $ keV electron precipitation estimation obtained from the analysis of the nightside velocity distribution functions of electrons at a single time step of this simulation. The top panel shows the differential number flux of precipitating electrons as a function of L shell (blue shading), as well as the mean precipitating energy (black line) in the same units as typical spacecraft data. The bottom panel shows the integral energy flux as a function of L. The integral energy flux was obtained by multiplying the differential number flux by the corresponding energies, and integrating across energies. The mean precipitating energy was calculated by dividing the integral energy flux by the total number flux (i.e., the differential number flux integrated across energies). The Hardy et al. (1985) model predicts a maximum integral energy flux of the order of $ 1 0 8-1 0 9 $ keV $ cm^{-2} s^{-1} s r^{-1} $ in the midnight sector, reached at geomagnetic latitudes comprised between $ 6 2^{\circ} $ and $ 6 9^{\circ} $ (translating into L values between 4.5 and 7.8), depending on geomagnetic activity given by the Kp index. The preliminary results from Vlasiator in Fig. 1 are therefore in reasonable agreement with those values.

With the expanding human activity in space, it is increasingly important to measure precipitating particle fluxes in situ and predict the precipitation by modelling, in order to understand the Earth's radiation environment. While previous satellite missions have provided a plethora of observations of the physical processes within the precipitation environment, none of the missions were designed specifically with a clear focus on precipitation. A number of new cubesat missions recently launched or being built focus on precipitation. These include, for example, the CSSWE mission (Kohnert et al., 2011), the ELFIN mission (Shprits et al., 2018), the Firebird mission Crew et al. (2016), and the AMICal Sat mission (Barthelemy et al., 2018). FORESAIL-1 will be a complementary mission, improving the spatial and temporal resolution of precipitation that may be offered by these missions together.

## 1.2 State of the Art: Solar energetic neutral atom observations

The energy budgets of the solar corona and solar eruptions are major unsolved questions in solar physics. Coronal heating leads to an abundance of suprathermal particles in the corona. Suprathermal ions are important for estimating the energy budget of an eruption (e.g., Emslie et al., 2004), however, they do not produce measurable amounts of electromagnetic radiation, and thus their abundance is difficult to measure. Direct in-situ measurements of suprathermal ions will be provided by the

<!-- PDF_PAGE: 5 -->


![figure_001.png](figure_001.png)



<div align="center">

Figure 1. Preliminary results of Vlasiator modelling of electron precipitation. (top) Differential flux of precipitating electrons as a function of L shell, in the same units as usually measured by telescopes onboard spacecraft. The black line indicates the mean precipitating energy. (bottom) Total precipitating energy flux as a function of L shell.

</div>

<!-- PDF_PAGE: 6 -->

recently launched NASA Parker Solar Probe mission, but only within the outermost reaches of the solar corona. During solar eruptions these suprathermal ions can be driven to participate in charge exchange processes with neutral atoms, resulting in the formation of solar energetic neutral atoms (ENAs). So far, ENAs have been measured only during one single event (Mewaldt et al., 2009) with the IMPACT/LET instrument onboard the twin the Solar TErestrial RElations Observatory (STEREO) spacecraft close to the beginning of the mission. Even these results may be questionable, as they have been disputed by Simnett (2011), who suggested the ENA observations could be explained by an earlier precursor event, detected as an electron burst.

## 1.3 State of the Art: Space debris removal technologies

The number of spacecraft in low-Earth orbit (LEO) is rapidly increasing, as technological and regulatory changes of launchers have allowed smaller satellites. These so-called nanosatellites typically do not have propulsion systems requiring bulky or volatile propellants for orbit control or de-orbiting, making them a significant source of future orbital debris. Furthermore, if they cannot handle high-radiation environments, these nanosatellites will fail early, thus on one hand contributing to existing debris and on the other hand defeating potential plans for active deorbiting at the end of mission. The sustainable use of the near-Earth space has become of great interest (e.g., Bastida Virgili et al., 2016). To avoid low-Earth orbits becoming unusable in the future, also nanosatellites should be removed at end-of-life, otherwise the amount of space debris will increase exponentially due to collisions with bigger objects (Kessler & Cour-Palais, n.d.; Klinkrad, 1993; Bradley & Wein, 2009; Bonnal et al., 2013), creating a potential danger to all later space missions. International standards have been developed to impose requirements on space missions to mitigate space debris production (e.g., European Space Agency, 2014; for Standardization, 2011). Thus, it is crucial to develop robust instruments for both controlling the small satellite orbits as well as for removing them from orbit after the end of the mission.

Apart from technological solutions for reduction of space debris that are inherent to the satellite design, efforts for third-party orbit removal techniques are ongoing. Approaches include spacecraft that perform automatic rendez-vous, attachment and joint de-orbiting of larger space debris items. Using high-powered lasers (either ground- or satellite-based) to exert radiation pressure, or directly ablate the surface material of space debris (a so-called "Laser Broom") has been a research project in both civilian Bekey, 1997; Phipps et al., 2012) and military (Campbell, 2000) projects. Compact propulsion methods possibly allowing de-orbiting of nanosatellites include miniaturised pulsed plasma and Hall-effect thrusters, which have reached commercial technological readiness, but still require propellants and a sizeable energy budget (Tummala & Dutta, 2017). Photonic solar sails have been investigated for propellantless propulsion and used successfully for interplanetary missions (Tsuda et al., 2013), as well as multiple nanosatellite missions (Lappas et al., 2011) with mixed success. Meanwhile, electric sails, in which electrically charged structures interact with the ion environment, have been proposed (Janhunen, 2004), and suitable packages have been implemented for nanosatellites, but successful experimental verification is still outstanding.

## 2 Science goals

## 2.1 Mission statement

FORESAIL-1 is the first nanosatellite mission designed to measure the energy dependent pitch angle spectra of the precipitating radiation belt particles, and solar ENA flux. Further, FORESAIL-1 will demonstrate the effectiveness of the plasma brake as a means of manipulating the spacecraft orbit in operation and lowering the

<!-- PDF_PAGE: 7 -->

spacecraft altitude to speed up de-orbiting at the end of the mission, thus addressing the sustainability of LEO space operations.

## 2.2 Science objectives

The FORESAIL-1 mission answers the following science questions: What are the pitch-angle and energy signatures of precipitation events as a function of MLT? How is the precipitation pitch-angle and energy distribution dependent on geomagnetic activity and driving from the solar wind? Thus, the FORESAIL-1 mission aims to perform precise directional measurements of electron and proton precipitation, as well as the energy spectrum and particle fluxes over a wide energy range (tens of keV to approximately one MeV). The spacecraft orbit shall drift in magnetic local time to allow determining precipitation as a function of MLT. The time resolution needs to be good enough to describe the lower bound on precipitation budget due to wave-particle interactions between chorus waves and electrons. Combining several measurements of at least three energy channels into a full pitch-angle resolution throughout the LEO region, with a time resolution of at least 15 s, will enable research of loss processes from the RBs.

To understand the energy budget of solar eruptions, the second science goal of this mission is to measure solar ENAs. This requires novel observations in an energy range well exceeding the magnetospheric ENA range. For this purpose, we use the geomagnetic field as a filter of solar particles and measure the ENA flux, thus inferring the flux that originates from the solar direction. Solar ENAs can only be measured reliably at energies exceeding the ring-current ion energies.

## 2.3 Technological objectives

In addition to the science objectives outlined above, FORESAIL-1 has a technological objective to ensure the sustainable use of space and to set a precedent for maintaining clean orbits. The objective is to test the plasma brake technology and achieve at least a 100 km lowering of the spacecraft altitude at mid-to-high altitude LEO. The consequences of this lowering of the orbit are 1) the orbital drift of the mission allowing monitoring the science objectives as a function of MLT, and 2) demonstrating that the technology can be used to de-orbit spacecraft. We will observe efficiency and performance of the plasma brake during the experiment to determine general information about the orbit lowering process. The success of the plasma brake experiment (and thus the completion of the mission's sustainability goals) is dependent on the reliable operation of the avionics, making reliability a primary design driver for FORESAIL-1. Radiation effects are identified as a major potential source of failures, hence radiation hardening techniques are used in the design.

## 3 Requirements

The study of precipitating electrons from the RBs is intrinsically coupled to the characteristic energy ranges of the electron seed populations there. Scientific and operational requirements are as follows:

1. NOAA/POES, for which the energy resolution is $ ( E_{2}-E_{1} ) / E_{1}=3 $ (where $ E_{1} $ and $ E_{2} $ are the upper and lower limits for consecutive integral channels), provides the lower reference bar in terms of energy resolution (Evans & Greer, 2006). The nominal energy resolution for FORESAIL-1 is 0.4 between the upper and lower limits of a channel.

2. The particle detector must have a sufficient discriminating ability between electrons and protons, such that the electron channel does not suffer from proton

<!-- PDF_PAGE: 8 -->

contamination. For lower energy channels there is no contamination, while in the higher energy channels we allow a small background, however, this should be so small that the electrons are discernible.

3. The orbit must drift to cover several MLTs.

4. For electron precipitation and solar ENA measurements, the orbital altitude should lie between 400 km and 800 km.

5. The electron pitch angle resolution should include at least three bins measured every 15 s.

6. The mission profile must allow for the use of the plasma brake for orbital and altitude control.

7. The mission profile must provide the ability for daily updates of measurements of orbital parameters to assess the effect of the plasma brake, once activated.

In order to achieve the above scientific requirements, the spacecraft spin axis must be oriented with $ 3^{\circ} $ accuracy, with spin of $ 4. 0 0 \pm0. 0 4 $ rpm. Attitude determination system must supply the magnetic field vector with $ 1^{\circ} $ accuracy and the satellite position must be known with 5-km accuracy. There must be a $ \sim1 $ kbs $ ^{-1} $ data downlink.

## 4 Description of the Mission

## 4.1 General Concept

FORESAIL-1 is a nanosatellite mission in LEO designed to answer the science objectives outlined in Section 2. The payload consists of a PArticle TElescope (PATE) and a Plasma Brake (PB). PATE will measure energetic electrons in the energy range 80-800 keV as well as $ \mathrm{H^{+}} $ ions (protons) and neutral atoms in the energy range 0.3-10 MeV. PB consists of a tether that will be used to lower the spacecraft altitude. The spacecraft is constrained under the CubeSat 3U standard to fit the two payloads.

## 4.2 Mission Timeline and Orbit

The manufacturing of the FORESAIL-1 payload and spacecraft started in 2018 and the manufacturing and integration will continue throughout 2019 until launch. The spacecraft is scheduled to be launched in 2020 into a Sun-synchronous orbit at or lower than 700 km altitude. Available launch opportunities are sought in 2019. Following the successful launch of the mission, the 1-month commissioning phase is scheduled to start immediately. After the commissioning phase, the mission's primary science phase is scheduled for 4 months at the initial Sun-synchronous orbit. After the primary phase, the plasma brake will be applied to lower the spacecraft by more than 100 km such that 1) the plasma braking force is fully demonstrated and 2) from the lowered orbit the spacecraft will naturally de-orbit after 25 years. The lowering of the orbit will inject the spacecraft into a drifting polar orbit, allowing precipitation measurements in different MLTs. Following the successful orbital manoeuvring of the spacecraft, the science phase continues with detecting particle precipitation in the drifting orbit for at least 1-2 years. After this will be the ENA measurement phase. There is a possibility of an extended science phase that will be scheduled depending on the health of the spacecraft.

## 4.3 Spacecraft Conjunctions

FORESAIL-1 can be used in conjunction with various other spacecraft in order to determine the origin of precipitating particles observed. Spacecraft that can provide context to the FORESAIL-1 observations include the Solar and Heliospheric Observatory (SOHO), STEREO, the Advanced Composition Explorer (ACE), Wind, DSCOVR, the Geostationary Operational Environmental Satellites (GOES), and the

<!-- PDF_PAGE: 9 -->

Parker Solar Probe. These missions directly monitor solar wind conditions, coronal mass ejections and solar energetic particles.

The conditions encountered by FORESAIL-1 will depend strongly on the state of the other regions in the magnetosphere. Simultaneous observations from satellites such as Cluster, the Magnetospheric Multi-Scale mission, the Time History of Events and Macroscale Interactions during Substorms spacecraft (THEMIS), and the Geomagnetic Tail Lab (GEOTAIL) will be invaluable for understanding the global context in which the FORESAIL-1 measurements are made. In particular, when located in the relevant region, these spacecraft can monitor substorms occurring in the magnetotail and the associated fast earthward plasma flows which are also the sources of the energetic particle precipitations to be measured by FORESAIL-1, in addition to the RB source. They can also provide information about the wave activity in the magnetosphere, which will be key to interpreting the FORESAIL-1 observations. In the regions closer to Earth, data from the recently-launched Arase mission in the radiation belts will be of particular importance. Direct complementary observations to FORESAIL-1 will be provided by the POES satellites, which will provide precipitating particle data at similar energy ranges, however these data are often problematic and require corrections.

## 4.4 Coordinated Ground-Based Observations

Coordinated observation will also be possible with ground-based instrumentation. Whenever suitable conjunctions with riometer chains such as the Finnish chain operated by Sodankylä Geophysical Observatory or the Canadian chain (NORSTAR) take place, it will be possible to compare energetic particle precipitation patterns to those inferred from cosmic noise absorption measurements. The special case of the Kilpisjärvi Atmospheric Imaging Receiver Array (KAIRA) is of particular interest, as this instrument, which may be used as a multibeam, multifrequency riometer could allow to finely study energetic precipitation along the FORESAIL-1 overpass. Indeed, KAIRA can provide 1 s time resolution observations of cosmic noise absorption with beams of $ 1 0^{\circ} 3 0^{\circ} $ width, depending on the considered frequency, which is accurate enough to study, e.g., individual patches of pulsating aurora with KAIRA (Grandin et al., 2017), suggesting that it may be possible to study mesoscale (<100 km) structures in energetic precipitation using FORESAIL-1 and KAIRA conjunctions.

During conjunctions, it can also prove valuable to combine FORESAIL-1 data with observations of other space weather manifestations. For instance, auroral precipitation can be inferred from observations by all-sky imagers such as the MIRACLE network in Fennoscandia, and the geomagnetic context of FORESAIL-1 measurements can be given more accurately during conjunctions with ground-based magnetometer networks as well as by making use of polar cap convection maps derived from Super Dual Auroral Radar Network observations (SUPERDARN). Finally, FORESAIL-1 precipitation data could prove useful in studies focusing on electron density enhancements in the ionosphere using, e.g., ionosondes or incoherent scatter radars such as the European Incoherent Scatter radars (EISCAT). The latter ones also enable the study of effects such as ionospheric Joule heating or ion outflow, as they measure ion and electron temperatures and ion line-of-sight velocity, and when in a specific configuration they also allow estimating electric fields (Nygren et al., 2011).

## 5 Payloads

The FORESAIL-1 mission will carry two science payloads, the Particle Telescope (PATE) and the Plasma Brake (PB).

<!-- PDF_PAGE: 10 -->


![figure_002.png](figure_002.png)



<div align="center">

Figure 2. a) Mechanical design concept of PATE. b) Schematic of the anti-coincidence (AC) and main detector (D) stack of each telescope.

</div>

## 5.1 Particle Telescope (PATE)

PATE measures energetic electrons, $ \mathrm{H^{+}} $ ions (protons) and neutral H atoms. The targeted energy range of hydrogen measurement is $ 0.3-10 \mathrm{MeV} $ , which covers the energies above the typical ring-current proton energies. This is to avoid the neutral hydrogen background originating from the interaction of the ring current with the geocorona. The primary energy range for electrons is $ 80-800 \mathrm{keV} $ . In addition, the instrument is sensitive to electrons at higher and lower energies in channels, where reliable particle identification cannot be performed, but especially the high-energy integral channel is still valuable since the contamination from heavier species comes only from relativistic protons, which have low fluxes compared to relativistic electrons in typical conditions.

PATE consists of two particle telescopes with identical stacks of detectors (see Fig. 2). The longer Telescope 1 is directed along the long axis of the spacecraft, that is, perpendicular to the rotation axis, and thus, it scans the directions in a plane perpendicular to the rotation axis of the spacecraft. The shorter Telescope 2 is directed along the rotation axis, so it can maintain a stable orientation. When the rotation axis is pointed towards the Sun, the telescope is able to measure the neutral hydrogen flux from the Sun. Note that the instrument itself does not determine the hydrogen charge state but relies on the geomagnetic field as a rigidity filter and on the measurement of angular distribution to disentangle the neutral flux from the solar direction. The motivation for the use of longer collimator in Telescope 1 is to improve the pitch angle angular resolution to better than 10 degrees for the scanning telescope.

Both telescopes have a mechanical collimator defining the aperture, consisting of an aluminum tube housing 18 (12) $ ( 5 0 0 \, \mu\mathrm{m} $ Al+ $ 5 0 0 \, \mu\mathrm{m} $ Ta) collimator rings in Telescope 1 (Telescope 2), followed by a stack of silicon detectors, D1, D2, and D3, measuring the energy losses of the particles in adjacent layers. The measured signals allow the determination of particle energy and the identification of particle species (electron / H). The thicknesses of the D detectors are $ 2 0 \, \mu\mathrm{m} $ $ 3 5 0 \, \mu\mathrm{m} $ and $ 3 5 0 \, \mu\mathrm{m} $ respectively. The D1 detectors have a bias voltage of 5 V, while the other ones are biased at 70 V. D1 and D2 detectors are segmented so that the central elements have diameters of 5.2 mm while the total active-area diameters of both are 16.4 mm. D3 has a single active area of 16.4 mm diameter. Both detector stacks are covered at the bottom of the collimator by two thin (nominally $ 0. 5 \, \mu\mathrm{m} $ each, 1 mm apart) Ni foils preventing low-energy $ (< 2 5 0 \mathrm{k e V}) $ ions and soft $ (< 5 0 0 \mathrm{e V}) $ photons from entering the detector stack. Each aperture is limited from above by an annular anti-coincidence

<!-- PDF_PAGE: 11 -->

detector AC1 (300 $ \mu $m thickness) with a circular hole of 14.0 mm diameter in the middle and and an outer active-area diameter of 33.8 mm. Another single-element circular anti-coincidence detector AC2 (350 $ \mu $m thickness, 33.8 mm active-area diameter) at the bottom of the stack flags particles penetrating the whole D detector stack. Note that while the AC2 is operated in anti-coincidence with the D detectors for the nominal energy range of the instrument (particles stopping in the D stack), PATE still analyses the D detector pulse heights for particles triggering AC2 but not AC1 to provide integral flux channels above the nominal energy ranges. The distances from upper surface to upper surface in the detector stack AC1-D1-D2-D3-AC2 are 2.5 mm, 2.0 mm, 2.5 mm, and 2.5 mm. The lower Ni foil is 3.2 mm above the upper surface of AC1.

Signal processing is based on continuous sampling and digitization of the analog signals and on digital filtering and pulse height analysis. The signal processing board contains 16 Analog to Digital Converters (ADCs) and a Microsemi ProAsic3L Field Programmable Gate Array (FPGA) handling the signal processing for both telescopes. The signal sampling rate in each ADC channel is 10 MHz, and the digital streams are processed by the FPGA, which is running at 40 MHz. The logic analyzes the incoming digital data streams, detects pulses, and identifies the particle for each valid coincidence event, counting and rejecting from further analysis any events not matching validity criteria. Valid particle events are then counted in separate counters based on their detection time, species and measured energy, forming the bulk of the science data of the instrument. The electron (hydrogen) spectrum consists of seven (ten) energy channels, log-spaced in measured energy.

## 5.1.1 Instrument Performance

The performance of the PATE electron measurement has been simulated using GEANT4 (Agostinelli et al., 2003). The simulation is performed for an isotropic electron distribution launched from a (15-cm radius) spherical surface surrounding PATE. The simulated pulse heights of all D-detector signals are analysed to separate electrons and hydrogen (ions/ENAs) and to measure particle energies, as in the FPGA-based on-board analysis. Particles producing a hit (i.e., an energy deposit > 50 keV) only in D2 are identified as electrons and particles producing a hit only in D1 are identified as hydrogen. Hit levels can be set freely in the logic, but values lower than 50 keV in D1a, D1c, AC1 and AC2 (see Fig. 2) should not be used as the simulated RMS noise levels in those pads are around 9-14 keV. While electrons are able to produce hits in D1 as well, there is only a minor level of electron contamination in the nominal hydrogen energy channels, which require the energy deposit in D1 to exceed 110 keV. If more than two adjacent D layers detect a pulse, the Delta E-E method is used for clean species separation. The geometric factor of the seven electron channels as a function of electron energy for (the shorter) Telescope 2 is shown in Fig. 3 (Oleynik & Vainio, 2019). The high-energy tails of the response functions are due to the inevitable scattering of electrons off the detectors and other structures inside the telescope, which prevents the full energy of the electron to be absorbed in active detector elements. The internal energy resolution of the instrument is much better for hydrogen than for electrons and the response functions are close to boxcar type within the nominal energy range.

The geometric factors of both telescopes are mostly determined by the uppermost collimator ring (with an inner diameter of 21.5 mm) and the hole of the AC1 detector (diameter of 14 mm), which are at a vertical separation of 12.0 cm (7.0 cm) in Telescope 1 (Telescope 2). The nominal value of the geometric factor is $ 0.037 \mathrm{c m}^{2} \mathrm{s r} $ $ (0.11 \mathrm{c m}^{2} \mathrm{s r}) $ for Telescope 1 (Telescope 2), but especially electrons have somewhat lower values (see Fig. 3) due to scattering off the Ni foils and the D1 detector, causing trajectories to miss the D2 detector. The nominal angular widths of the acceptance

<!-- PDF_PAGE: 12 -->


![figure_003.png](figure_003.png)



<div align="center">

Figure 3. The geometric factor of PATE as a function of energy for the seven electron energy channels within the nominal energy range (80-800 keV), simulated using GEANT4 (Agostinelli et al., 2003). The range above 800 keV is additionally covered by a penetrating particle flux channel.

</div>

cones (half width at half the on-axis value) for the two telescopes are $ 4. 6^{\circ} $ and $ 7. 9^{\circ} $ respectively. The instrument can also be operated in a mode where only the central segments of the D1 and D2 are included in the coincidence logic while the rim areas are logically included in the anti-coincidence. This allows to decrease the geometric factors of the telescopes by a factor of about 7. Any detector element can also be switched off from the logic entirely.

## 5.1.2 Mass, power and telemetry budgets

The mass of PATE is 1.2kg, consisting of the instrument box and mechanical support structures (435 g), detector and pre-amplified board housings (290 g), the collimators (180 g), cables (115 g), and the rest (180 g), including the back-end electronics stack. The power budget for PATE is 2.5 W, half of which is consumed by the FPGA, with an additional margin of 20%, mainly required to account for the final FPGA power consumption.

The telemetry budget of PATE is summarized in Table 1. Spectral resolution of the data products for both electrons and hydrogen is on average $ \Delta E / E\approx 40\% $ within the nominal energy ranges, which means that the spectral counter data consists of eight (ten) differential and one (two) integral channels for electrons (hydrogen). The rotation period, nominally 15 s, of the satellite equals the time resolution of the instrument. This main time frame is further broken in 36 angular sectors for the rotating telescope to provide the angular distribution measurement. Both telescopes deliver, in addition to the spectral counter data, also pulse height data samples, which allow an accurate in-flight calibration and health monitoring of the detection system.

<!-- PDF_PAGE: 13 -->

<table border="1"><tr><td>Data source</td><td>Data rate[bit/s]</td><td>Data amount per day[kiB]</td></tr><tr><td>Rotating telescope</td><td>993</td><td>10500</td></tr><tr><td>Solar pointing telescope</td><td>60</td><td>633</td></tr><tr><td>Housekeeping</td><td>13</td><td>135</td></tr><tr><td>Total</td><td>1066</td><td>11268</td></tr></table>

<div align="center">

Table 1. Summary of the PATE telemetry budget during science operations.

</div>


![figure_004.png](figure_004.png)



<div align="center">

Figure 4. Operating principle of the PB: an electric current system and a net thrust exerted on the negative tether by the plasma ram flow.

</div>

## 5.2 Plasma Brake (PB)

## 5.2.1 Operating Principle

The Plasma Brake instrument is designed to measure the Coulomb drag, i.e., the braking force caused by the ionospheric plasma ram flow to an electrically charged tether (Figure 4). When interacting with the surrounding plasma, the negative tether gathers positive ions, which tends to neutralize the tether. To maintain the charge, the tether is connected by a high-voltage power system to a conducting surface (deployable booms for FORESAIL-1) that acts as an electron sink to close the current system through the plasma (Janhunen, 2011). The braking force can be measured in two modes. One is to monitor the system spin rate while charging the tether synchronously with the tether rotation (PB Measurement). The other is to maintain a constant charging and monitor the spacecraft velocity and orbital elements (PB Mode).

We employ $ - 1 \mathrm{kV} $ voltage, which is the maximum without risking electron field emission from micrometeoroid-struck parts of the tether wires. At this voltage, the expected nominal plasma brake thrust per tether length is 58 nN/m when the tether is perpendicular to the ram flow. This value is obtained by using Equation 1 of Janhunen (2014) and assuming plasma density of $ 3 \cdot 1 0^{1 0} \mathrm{m}^{-3} $ , mean ion mass of 10 proton masses, ram flow speed of 7.8 km/s and tether's effective electric radius of 1 mm. The tether's collected ion current is small, nominally 30 $ \mu\mathrm{A} $ for a 300 m long tether.

## 5.2.2 Design

The tether is deployed from a chamber (blue) by the centrifugal force affecting the tether tip mass (gray button inside the red collar) (Figure 5). The mechanical interface through the satellite side panel is provided by an anti-static collar (red) to avoid triple junctions of plasma, insulator, and high voltage tether. The tip mass is locked during the launch by two launch locks located on opposite sides of the tether chamber opening. The tether reel (dark gray) and the stepper motor that turns it (orange) are nested inside the tether chamber. The tether high-voltage contact is

<!-- PDF_PAGE: 14 -->


![figure_005.png](figure_005.png)



<div align="center">

Figure 5. PB payload structure.

</div>

through the conducting reel and the slider (copper brown) attached straight to the high-voltage converter (orange) board behind the tether chamber.

The PB tether is made of thin metallic wires that are periodically bonded to each to withstand the micrometeoroid and space debris collisions (e.g., Seppänen et al., 2011). The single wire thickness is a few tens of micrometers to minimise the ion current to the tether and thus the mass of the power system and size of the electron gathering surface.

The nominal FORESAIL-1 tether length is 300 meters requiring $ \sim 2 0 $ Nms of the total angular momentum to deploy it. The initial angular speed of $ 1 8 0 \degree/s $ is sufficient to provide a centrifugal force of 0.4 cN which would safely pull out a tip mass weighing 2.5 g without breaking the tether. The angular momentum is provided by several consecutive satellite spin-up and reel-out maneuvers to compensate for the decreasing spin rate associated with the increasing moment of inertia. Since magnetorquers are used for attitude control, the angular acceleration is low to avoid the tether winding around the satellite. It also indicates that a considerable amount of time is needed to provide the angular momentum. However, after measuring the Coulomb drag force with a few tens of meters of the tether, the force can be used to spin up the satellite by modulating the tether voltage in synchronization with the rotation (charging downstream to increase the spin rate). After deploying the tether and taking PB measurements, the PB mode will start by continuously charging the tether which in turn will lower the orbit and start the satellite drift in MLT. When reaching $ \sim 6 0 0 $ -km altitude and gaining a sufficient drift in MLT, the satellite will be prepared for PATE observations the tether will be discarded to allow the spin axis being pointed towards the Sun. It can be done by attempting to reel in the tether which might break because it would be partially broken by micrometeoroids. A broken tether would deorbit in a few months thanks to its large area/mass ratio. If the tether does not break, the attitude control system and/or PB itself will have to provide an angular momentum to compensate for an increasing spin rate.

## 5.2.3 Mass, Power and Telemetry Budgets

The mass of the PB is 0.6 kg including a margin of 25% . The structure (frame, tether chamber, and motor mounting shaft) contributes 67% to the mass budget. The size of the system is $ 6 7 \times8 4 \times9 6 $ mm. For the two measurement modes of the PB, the power budget for PB is 600 mW. For the tether reeling, the motor and the controller consumes 7 W continuously. In case the reel-out power cannot be provided continuously by the spacecraft, the operation can be done in stages. The telemetry budget of the PB is summarised in Table 2. To reduce the overall telemetry budget,

<!-- PDF_PAGE: 15 -->

<table border="1"><tr><td>Mode</td><td>Data rate[bit/s]</td><td>Data amount per day[kiB]</td></tr><tr><td>Reel-Out/In</td><td>128</td><td>1350</td></tr><tr><td>PB Mode</td><td>19</td><td>200</td></tr><tr><td>PB Measurement</td><td>256</td><td>2700</td></tr><tr><td>Standby</td><td>64</td><td>675</td></tr></table>

<div align="center">

Table 2. Summary of the PB telemetry budget for the operation modes.

</div>

<table border="1"><tr><td>Subsystem</td><td>Planned mass(g)</td><td>Mass with contingency(g)</td><td>Fraction(%)</td></tr><tr><td>OBC</td><td>80</td><td>96</td><td>2</td></tr><tr><td>EPS</td><td>926</td><td>1093</td><td>23</td></tr><tr><td>Magnetorquers</td><td>240</td><td>288</td><td>6</td></tr><tr><td>UHF Transceiver</td><td>80</td><td>96</td><td>2</td></tr><tr><td>Antennas</td><td>50</td><td>60</td><td>1</td></tr><tr><td>Structure</td><td>1033</td><td>1240</td><td>26</td></tr><tr><td>PATE</td><td>1000</td><td>1200</td><td>26</td></tr><tr><td>PB</td><td>600</td><td>660</td><td>14</td></tr><tr><td>Total</td><td>4009</td><td>4733</td><td>100</td></tr></table>

<div align="center">

Table 3. FORESAIL-1 mass budget.

</div>

the long-duration routine PB mode uses a lower telemetry rate. Frequent housekeeping data are not required because in the PB mode, altitude change over weeks to months will show the success of experiment.

## 6 Spacecraft platform

The platform has been designed to accommodate the payloads and to provide data, power and mechanical interfaces. The overall mission tree for the FORESAIL-1 is presented in Figure 6. Since one of the key technological drivers for the mission is reliability, the avionics stack has several designs to this end. The avionics stack is enclosed in a vault providing substantially better shielding than what is typically seen on CubeSats (around 4 mm equivalent aluminium, instead of the more typical 2 mm), thus enhancing system tolerance to total dose. Single-event effects will be mitigated using dual cold redundancy, hardware overcurrent protection, minimization of the software footprint, and systematic data integrity checks. Finally, the FORESAIL-1 components will be submitted to radiation test campaigns; the radiation response data will be made available publicly in order to benefit from the broader field of (small) satellite technology and help other designers addressing this issue.

The avionics stack consists of the Electrical Power System (EPS) for power collection, storage and distribution, Communication System for telemetry, On-Board Computer (OBC) for telemetry handling and mission and payload management and data storage, and Attitude Determination and Control System (ADCS) for maintaining the attitude modes during different operation phases. The mechanical structure satisfies dimensional limitations of the CubeSat standard and ensures modular configuration of the spacecraft's subsystems. The configuration of the platform is shown in Figure 7. The total mass budget is shown in Table 3.

<!-- PDF_PAGE: 16 -->


![figure_006.png](figure_006.png)



<div align="center">

Figure 6. FORESAIL-1 mission product tree.

</div>


![figure_007.png](figure_007.png)



<div align="center">

Figure 7. Spacecraft structure including the subsystems without shielding.

</div>

<!-- PDF_PAGE: 17 -->

<table border="1"><tr><td>Parameter</td><td>X,Y axes</td><td>Z axis</td></tr><tr><td>Number of wire turns</td><td>184</td><td>952</td></tr><tr><td>Nominal current,mA</td><td>26.2</td><td>19.3</td></tr><tr><td>Dipole moment,Am2</td><td>0.2</td><td>0.2</td></tr><tr><td>Power,mW</td><td>51.7</td><td>56.5</td></tr></table>

<div align="center">

Table 4. Quantitative parameters for the air core magneotorquers.

</div>

## 6.1 Platform subsystems

Each payload has different requirements for attitude. PATE needs to be oriented towards the Sun, while the detector with longer collimator scans the environment in the directions perpendicular to the Earth-Sun vector. The PB needs the spinning control for deploying and maintaining the tension of the tether. While the PB does not need specific pointing direction, its tether deployment introduces a mass distribution change that will require a proper control of the spacecraft angular momentum.

The attitude determination and control system (ADCS) is divided into Attitude Determination System (ADS) and Attitude Control System (ACS). The ADS is equipped with gyroscope (L3GD20H), magnetometer (LIS3MDL), and in-house built sun sensors (Noman et al., 2017). The angular velocity of the spacecraft is a crucial parameter for the payload attitude modes, thus gyroscope is necessary. Sun sensors are required for a precise sun pointing control, and magnetometers are needed for properly using with attitude control. The outputs will provide a full attitude information through using an unscented Kalman filter algorithm on all sensors.

The ACS changes the orientation of the spacecraft by using magnetorquers. There is a closed loop feedback, which ensures the maintenance of desired attitude by repeating the torque command until the desired orientation is achieved. The mission requirements for PATE and PB impose specific constraints on the attitude control. The spacecraft uses the following attitude control modes:

- Detumble mode: To stabilize the spacecraft after deployment

- Spin control mode: In order to deploy the PB tether, this mode spins up the spacecraft preferably with the spin axis being aligned with the earth pole. After deorbiting, spin down might be required during tether reel in if the tether does not break.

- Sun pointing mode: This mode continuously points Telescope 2 (at -Y axis) towards the sun while spinning in order for Telescope 1 (at Z-axis) to scan the sky.

Magnetorquers are sufficient to provide all necessary control modes for the manipulation of the attitude and angular velocity. They are designed in-house, in form of air coils, so that they can be integrated to the solar panels (for the X and Y axes), and on a small factor magnetorquer driver board for the Z axis. All axes have two magnetorquers connected in parallel. The designed magnetorquers are driven through a custom-built coil driver to optimize either consumed power or the generated magnetic moment. The quantitative parameters of air core magnetorquers are given in Table 4.

The EPS of the satellite consist of solar panels, power conditioning and power distribution (Ali et al., 2014), (Mughal et al., 2014). The solar panels are mounted on

<!-- PDF_PAGE: 18 -->

every long side of the satellite. The solar panels at other sides than where PATE is located consist of 7 solar cells connected in series, whereas the panel at the PATE side consists of 6 cells in order to provide space for the telescope. The power conditioning consists of switching buck converters to convert the incoming solar power to the battery voltage level. A perturb and observe based algorithm extracts the maximum power from the solar cells. Each subsystem houses a linear regulator to effectively convert the voltage down to a stable 3.3 V with a low ripple factor. The theoretical efficiency of the EPS is above 85 %. All losses have been accounted for in the calculation of power budget. The maximum input power is 7 W, whereas the average power consumption in the nominal mode 3.7 W.

The on-board computer (OBC) is the satellite's main computer responsible for computational and data storage needs, running the ADCS algorithms, and storing the telemetry and housekeeping data logs. A safety-critical ARM Cortex-R4 based processor is selected as the central OBC of the spacecraft. The processor features 256 k data rapid-access memory and 3 MB of program flash. There are external flash memory devices also interfaced with the processor. To facilitate possible faults due to radiation, the OBC houses two cold redundant symmetric processors. Only one of the processors is active and powered. The arbiter switches the control to the redundant processor in case of failure. The OBC is responsible for operational work during the PB and PATE operations and collects all relevant telemetry data for downlink.

The UHF transceiver onboard the FORESAIL-1 consist of CC1125 transceiver with maximum output power of 15 dBm (30 mW); an external power amplifier RF5110G (gain: 31.5 dB, maximum output power 34.5 dBm) to amplify the power to desired 1.5-watt power in the transmit chain. In the receive chain, it consist of a Low Noise Amplifier and a bandpass filter.

## 7 Ground Segment and Operations

The primary ground station used for satellite operation is located in Aalto University Campus in Espoo, Finland. The ground station operates mainly as a radio amateur satellite station and has capabilities for operation on radio amateur UHF, VHF and S-bands. Due to its northern location the ground station has an average link time to polar orbit up to 90 minutes per day for all passes above the horizon. Ground station radio systems are built based on the Software Defined Radio (SDR) architecture which facilitates easy satellite-specific customization. The ground station infrastructure and equipment are designed and operated by students and serve also for educational purposes for the Aalto University. The Aalto University ground station also operates as the mission control centre.

Typically, each satellite pass provides 10-20 min of link time between satellite and ground station. The data rate requirements for FORESAIL-1 in science mode require the downlink data rate to be approximately 8 kbps. Since the data rate requirements are not stringent in order to accomplish both the missions, the ground station at Aalto University easily handles the data rate requirements.

## 8 Data Products

FORESAIL-1 data products are outlined in Table 5. The Aalto University ground station is responsible for downlinking the L0/L1 data containing general spacecraft housekeeping data, PATE raw data, PB housekeeping and mission log information. These low level data products are shared forward using file-based web interface. For PATE data processing, Level 1 raw data files combined to ADCS metadata and orbital information are used to produce calibrated and geolocated measurements of the particle fluxes.

<!-- PDF_PAGE: 19 -->

<table border="1"><tr><td>Provider</td><td>Data product</td><td>Details</td></tr><tr><td>Mission Spacecraft</td><td>List of data availability Orbital data, Attitude</td><td>Includes position and altitude required to estimate the PB performance</td></tr><tr><td>PB</td><td>Electric current in the tether L0 telemetry stream L1 raw data L2 calibrated data L3 derived products</td><td>Plasma density L2 and plasma density including position</td></tr><tr><td>PATE</td><td>Flux L0 telemetry stream L1 raw data L2 calibrated data(fluxes) L3 derived products</td><td>L2 including location Precipitation maps(varying time resolutions) Angular distribution data(spin resolution) Event catalogues(mission duration)</td></tr></table>

<div align="center">

Table 5. FORESAIL-1 data products. PATE fluxes are given as function of energy, time and pointing azimuth.

</div>

These data products will be used to demonstrate that the PB de-orbits the satellite at a measurable amount, as a function of time. The PATE data will be used to infer the precipitation energy spectrum in time and place, addressing the science objectives. The science data are open for everyone, with the nominal rules-of-the-road typical in the field of space physics.

## 9 Summary and Discussion

The increasing number of small satellites launched into Earth's orbit raises timely concerns about the sustainable use of space. Small, rapidly built and launched satellites have a large future potential for scientific and commercial use. However, the satellites will become debris sooner rather than later, if they have poor radiation tolerance and if they are not de-orbited at the end of mission. The Finnish centre Of excellence in REsearch of SustAInabLe space (FORESAIL) funded by the Academy of Finland tackles this issue by focusing both on science of the near-Earth radiation environment and on novel technological solutions related to building more resilient instruments and debris removal.

The first nanosatellite designed and built by the Centre of Excellence, FORESAIL-1, is a 3U cubesat operating at polar LEO orbit at and below 700 km which will produce energy-dependent pitch angle spectra of electrons and protons that precipitate from the RBs into the ionosphere. Further, it will measure energetic neutral atoms (ENAs) from the Sun and test the PB technology to lower the spacecraft altitude and manage its orbit in space.

Today, nanosatellites can address significant scientific questions. This requires focused measurements and innovative technological approaches, as well as coordination with the other spacecraft and facilities operating simultaneously. The FORESAIL-1 PATE instrument will make unprecedented and precise measurements of precipitating electrons and protons with high temporal resolution. It will be able to discriminate between electrons and protons, over a wide energy range (80-800 keV for electrons

<!-- PDF_PAGE: 20 -->

and 0.3-10 MeV for protons and neutral atoms). The large coverage of the polar cap at different orbital planes is achieved by operating the PB at the beginning of the mission, which sets the spacecraft orbital plane to drift in magnetic local time. This is the first time such a manoeuvre is attempted with a nanosatellite, and if successful, it will open new avenues for controlling the orbits of propellantless spacecraft, expanding their operational and observational ranges.

FORESAIL-1 is targeted to make important advances in radiation belt physics. With simultaneous observations in the solar wind, magnetosphere and from the ground, FORESAIL-1 will allow quantifying the role of solar wind and outer magnetospheric driving, and the role of different plasma waves in the inner magnetosphere in the precipitation process. The primary science phase allows connecting precipitation signatures and mechanisms to geomagnetic activity levels and solar wind conditions. Together with the novel Vlasiator model, a global hybrid-Vlasov simulation (Palmroth et al., 2018), it will be possible to tie precipitation measurements to global processes in the outer magnetosphere for the first time, as Vlasiator begins its full six-dimensional operation before the launch of FORESAIL-1. The six dimensions refer to three dimensions in the ordinary space and three in the velocity space to describe the full particle distribution function, which is used to infer the energy spectrum and pitch angle in time. At the time of writing, Vlasiator allows already 2D electron precipitation calculations (see Fig. 1), which are in reasonable agreement with previous estimates (Hardy et al., 1985). Once the model is fully 6D, in situ observations of electron precipitation can be directly compared to kinetic processes anywhere in the magnetosphere, without limitations as to whether a spacecraft traverses particular regions. This unprecedented plan will likely open new avenues in space physics.

Successful observations of ENAs from the Sun will allow estimating for the first time comprehensively estimating the suprathermal coronal ion population indirectly. This is the key knowledge for improved understanding of the charged particle acceleration processes at the CME-driven shock waves close to the Sun and of the CME energy budget. The solar ENA flux has been measured only once in a very fortuitous event (Mewaldt et al., 2009). Observing the ENA flux from the Sun on a regular basis as a function of time and solar activity is unprecedented.

The demonstration of the altitude manoeuvre of FORESAIL-1 will bring potential for future applications for the PB as a standard tool for removing satellites from their orbits. This is in particular a compelling solution considering the possibly upcoming regulations for including debris mitigation techniques in newly launched spacecraft.

FORESAIL-1 is at the forefront of scientific nanosatellites. The advances we have made will be particularly important in demonstrating the usefulness of nanosatellites in making relevant physics and discovery measurements (ENA), whose spatio-temporal resolution could be brought to a new level using fleets of nanosatellites. Technological solutions of FORESAIL-1 have particularly far reaching impact for future debris removal solutions and orbit control. All these aspects are expected to pave the way for the sustainable use of space.

The Finnish Centre of Excellence in Research of Sustainable Space, building and launching three FORESAIL missions is funded through the Academy of Finland with grant numbers 312351, 312390, 312358, 312357, and 312356.

## Acknowledgments

We acknowledge The European Research Council for Starting grant 200141- QuESpace, with which Vlasiator was developed, and Consolidator grant 682068-PRESTISSIMO awarded to further develop Vlasiator and use it for scientific investigations. We

<!-- PDF_PAGE: 21 -->

gratefully also acknowledge the Academy of Finland (grant numbers 138599,267144, 309937, and 309939). We acknowledge the CSC-IT Center for Science Grand Challenge grant for 2018, with which the Vlasiator simulation run was carried out. Vlasiator (http://www.physics.helsinki.fi/vlasiator/，（Palmroth,2019)）is distributed under the GPL-2 open source license at https://github.com/fmihpc/vlasiator/（Palmroth & the Vlasiator team,2019). Vlasiator uses a data structure developed in-house (Sandroos,2019), which is compatible with the VisIt visualization software (Childs et al.,2012) using a plugin available at the VLSV repository. The Analysator software (https://github.com/fmihpc/analysator/，（Hannuksela & the Vlasiator team,2019) was used to produce the presented figures. The run described here takes several terabytes of disk space and is kept in storage maintained within the CSC IT Center for Science. Data presented in this paper can be accessed by following the data policy on the Vlasiator web site.

## References

Agostinelli, S., Allison, J., Amako, K., Apostolakis, J., Araujo, H., Arce, P.,... G EANT4 Collaboration (2003, July). GEANT4-a simulation toolkit. Nuclear Instruments and Methods in Physics Research A, 506, 250-303. doi: 10.1016/S0168-9002(03)01368-8

Ali, A., Mughal, M., Ali, H., & Reyneri, L. (2014). Innovative power management, attitude determination and control tile for cubesat standard nanosatellites. Acta Astronautica, 96, 116 - 127. Retrieved from http://www.sciencedirect.com/ science/article/pii/S0094576513004165 doi: https://doi.org/10.1016/j.actaastro.2013.11.013

Asikainen, T., & Mursula, K. (2013, October). Correcting the NOAA/MEPED energetic electron fluxes for detector efficiency and proton contamination. J. Geophys. Res. Space Physics, 118, 6500-6510. doi: 10.1002/jgra.50584

Baker, D. N., & Kanekal, S. G. (2008, February). Solar cycle changes, geomagnetic variations, and energetic particle properties in the inner magnetosphere. Journal of Atmospheric and Solar-Terrestrial Physics, 70, 195-206. doi: 10.1016/j.jastp.2007.08.031

Barcus, J. R., Brown, R. R., Karas, R. H., Bronstad, K., Trefall, H., Kodama, M., & Rosenberg, T. J. (1973, March). Balloon observations of auroral-zone X-rays in conjugate regions. Journal of Atmospheric and Terrestrial Physics, 35, 497-511. doi: 10.1016/0021-9169(73)90039-1

Barthelemy, M., Vladimir, K., Anne, V., Frédéric, R., Sebastien, P., & Laurence, C. (2018, April). AMICAL and ATISE: two cubesats optical payload for space weather monitoring. In Egu general assembly conference abstracts (Vol. 20, p. 10580).

Bastida Virgili, B., Dolado, J. C., Lewis, H. G., Radtke, J., Krag, H., Revelin, B.,... Metz, M. (2016, September). Risk to space sustainability from large constellations of satellites. Acta Astronautica, 126, 154-162. doi: 10.1016/j.actaastro.2016.03.034

Bekey, I. (1997). Project Orion: Orbital Debris Removal Using Ground-Based Sensors and Lasers. In B. Kaldeich-Schuermann (Ed.), Second european conference on space debris (Vol. 393, p. 699).

Bonnal, C., Ruault, J.-M., & Desjean, M.-C. (2013, April). Active debris removal: Recent progress and current trends. Acta Astronautica, 85, 51-60. doi: 10.1016/j.actaastro.2012.11.009

Bradley, A. M., & Wein, L. M. (2009). Space debris: Assessing risk and responsibility. Advances in Space Research, 43(9), 1372 - 1390. doi: 10.1016/j.asr.2009.02.006

Campbell, J. W. (2000, December). Using lasers in space: Laser orbital debris re-

<!-- PDF_PAGE: 22 -->

moval and asteroid deflection (Occasional Paper No.20). Maxwell Air Force Base, Alabama: Air University.

Chen, Y., Reeves, G. D., & Friedel, R. H. W. (2007, September). The energization of relativistic electrons in the outer Van Allen radiation belt. Nature Physics, 3, 614-617. doi: 10.1038/nphys655

Childs, H., Brugger, E., Whitlock, B., Meredith, J., Ahern, S., Pugmire, D., .. Navr'atil, P. (2012, Oct). VisIt: An End-User Tool For Visualizing and Analyzing Very Large Data. In High Performance Visualization-Enabling Extreme-Scale Scientific Insight (p. 357-372). Chapman & Hall / CRC.

Crew, A. B., Spence, H. E., Blake, J. B., Klumpar, D. M., Larsen, B. A., O'Brien, T. P., ... Widholm, M. (2016). First multipoint in situ observations of electron microbursts: Initial results from the nsf firebird ii mission. Journal of Geophysical Research: Space Physics, 121(6), 5272-5283. doi: 10.1002/2016JA022485

Elkington, S. R., Hudson, M. K., & Chan, A. A. (2003, March). Resonant acceleration and diffusion of outer zone electrons in an asymmetric geomagnetic field. Journal of Geophysical Research (Space Physics), 108, 1116. doi: 10.1029/2001JA009202

Emslie, A. G., Kucharek, H., Dennis, B. R., Gopalswamy, N., Holman, G. D., Share, G. H., ... Zurbuchen, T. H. (2004, October). Energy partition in two solar flare/CME events. Journal of Geophysical Research (Space Physics), 109, A10104. doi: 10.1029/2004JA010571

European Space Agency. (2014). Space debris mitigation policy for agency projects reference ESA/ADMIN/IPOL(2014)2 and annexes [Computer software manual].

Evans, & Greer. (2006). Sem-2 documentation for noaa-15 and later satellites, version 2v2.0, rev 2006. https://ngdc.noaa.gov/stp/satellite/poes/ documentation.html. (Accessed: 2018-11-23)

Evans, D. S., & Greer, M. S. (2000). Polar orbiting environmental satellite space environment monitor-2: Instrument description and archive data documentation. US Department of Commerce, National Oceanic and Atmospheric Administration, Oceanic and Atmospheric Research Laboratories, Space Environment Center.

for Standardization, I. O. (2011). Space systems - space debris mitigation requirements [Computer software manual].

Graf, K. L., Inan, U. S., Piddyachiy, D., Kulkarni, P., Parrot, M., & Sauvaud, J. A. (2009, July). DEMETER observations of transmitter-induced precipitation of inner radiation belt electrons. Journal of Geophysical Research (Space Physics), 114, A07205. doi: 10.1029/2008JA013949

Grandin, M., Kero, A., Partamies, N., McKay, D., Whiter, D., Kozlovsky, A., & Miyoshi, Y. (2017, Jun). Observation of pulsating aurora signatures in cosmic noise absorption data. Geophysical Research Letters, 44, 5292-5300. doi: 10.1002/2017GL073901

Hannuksela, O., & the Vlasiator team. (2019). Analysator: python analysis toolkit. Github repository. Retrieved from https://github.com/fmihpc/analysator/ (last access: 09.05.2019)

Hardy, D. A., Gussenhoven, M. S., & Holeman, E. (1985). A statistical model of auroral electron precipitation. Journal of Geophysical Research, 90, 4229-4248. doi: 10.1029/JA090iA05p04229

Hargreaves, J. K. (1969). Auroral absorption of HF radio waves in the ionosphere: A review of results from the first decade of riometry. IEEE Proceedings, 57, 13481373. doi: 10.1109/PROC.1969.7275

Janhunen, P. (2004). Electric sail for spacecraft propulsion. Journal of Propulsion and Power, 20(4), 763-764. doi: 10.2514/1.8580

Janhunen, P. (2011, March). Electrostatic plasma brake for deorbiting a satellite. J. Prop. Power, 26, 370-372. doi: 10.2514/1.47537

Janhunen, P. (2014). Simulation study of the plasma-brake effect. Ann. Geophys.,

<!-- PDF_PAGE: 23 -->

32, 1207-1216. doi: 10.5194/angeo-32-1207-2014

Kennel, C. F., & Petschek, H. E. (1966, January). Limit on Stably Trapped Particle Fluxes. Journal of Geophysical Research, 71, 1. doi: 10.1029/JZ071i001p00001

Kero, A., Vierinen, J., McKay-Bukowski, D., Enell, C.-F., Sinor, M., Roininen, L., & Ogawa, Y. (2014, August). Ionospheric electron density profiles inverted from a spectral riometer measurement. Geophysical Research Letters, 41, 5370-5375. doi: 10.1002/2014GL060986

Kessler, D. J., & Cour-Palais, B. G. (n.d.). Collision frequency of artificial satellites: The creation of a debris belt. Journal of Geophysical Research: Space Physics, 83(A6), 2637-2646. doi: 10.1029/JA083iA06p02637

Kim, H.-J., & Chan, A. A. (1997, September). Fully adiabatic changes in storm time relativistic electron fluxes. Journal of Geophysical Research: Space Physics, 102, 22107-22116. doi: 10.1029/97JA01814

Klinkrad, H. (1993, August). Collision risk analysis for low Earth orbits. Advances in Space Research, 13, 177-186. doi: 10.1016/0273-1177(93)90588-3

Kohnert, R., Palo, S., & Li, X. (2011). Small space weather research mission designed fully by students. Space Weather, 9(4). Retrieved from https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2011SW000668 doi: 10.1029/2011SW000668

Lappas, V., Adeli, N., Visagie, L., Fernandez, J., Theodorou, T., Steyn, W., & Perren, M. (2011, December). CubeSail: A low cost CubeSat based solar sail demonstration mission. Advances in Space Research, 48, 1890-1901. doi: 10.1016/j.asr.2011.05.033

Li, X., Baker, D. N., Kanekal, S. G., Looper, M., & Temerin, M. (2001). Long term measurements of radiation belts by SAMPEX and their variations. Geophysical Research Letters, 28, 3827-3830. doi: 10.1029/2001GL013586

Li, X., Baker, D. N., Temerin, M., Larson, D., Lin, R. P., Reeves, G. D., ...

Mewaldt, R. A. (1997). Are energetic electrons in the solar wind the source of the outer radiation belt? Geophysical Research Letters, 24, 923-926. doi: 10.1029/97GL00543

Mann, I. R., Ozeke, L. G., Murphy, K. R., Claudepierre, S. G., Turner, D. L., Baker, D. N., ... Honary, F. (2016, October). Explaining the dynamics of the ultrarelativistic third Van Allen radiation belt. Nature Physics, 12, 978-983. doi: 10.1038/nphys3799

Marchaudon, A., & Blelly, P.-L. (2015). A new interhemispheric 16-moment model of the plasmasphere-ionosphere system: IPIM. J. Geophys. Res. Space Physics, 120, 5728-5745. doi: 10.1002/2015JA021193

Matsumura, C., Miyoshi, Y., Seki, K., Saito, S., Angelopoulos, V., & Koller, J. (2011, June). Outer radiation belt boundary location relative to the magnetopause: Implications for magnetopause shadowing. Journal of Geophysical Research (Space Physics), 116, A06212. doi: 10.1029/2011JA016575

McDiarmid, I. B., Burrows, J. R., & Budzinski, E. E. (1975). Average characteristics of magnetospheric electrons (150 eV to 200 keV) at 1400 km. Journal of Geophysical Research, 80, 73. doi: 10.1029/JA080i001p00073

McIlwain, C. E. (1966, August). Ring current effects on trapped particles. Journal of Geophysical Research: Space Physics, 71, 3623-3628. doi: 10.1029/JZ071i015p03623

McKay-Bukowski, D., Vierinen, J., Virtanen, I. I., Fallows, R., Postila, M., Ulich, T., ... Turunen, E. (2015, March). KAIRA: The Kilpisjärvi Atmospheric Imaging Receiver Array—System Overview and First Results. IEEE Transactions on Geoscience and Remote Sensing, 53, 1440-1451. doi: 10.1109/TGRS.2014.2342252

Mewaldt, R. A., Leske, R. A., Stone, E. C., Barghouty, A. F., Labrador, A. W., Cohen, C. M. S., ... Wiedenbeck, M. E. (2009, March). STEREO Observations of Energetic Neutral Hydrogen Atoms During the 2006 December 5 Solar Flare. The

<!-- PDF_PAGE: 24 -->

Astrophysical Journal, 693, L11-L15. doi: 10.1088/0004-637X/693/1/L11

Millan, R. M., & the BARREL Team. (2011, July). Understanding relativistic electron losses with BARREL. Journal of Atmospheric and Solar-Terrestrial Physics, 73, 1425-1434. doi: 10.1016/j.jastp.2011.01.006

Millan, R. M., & Thorne, R. M. (2007, March). Review of radiation belt relativistic electron losses. Journal of Atmospheric and Solar-Terrestrial Physics, 69, 362- 377. doi: 10.1016/j.jastp.2006.06.019

Miyoshi, Y., Oyama, S., Saito, S., Kurita, S., Fujiwara, H., Kataoka, R.,... Tsuchiya, F. (2015, April). Energetic electron precipitation associated with pulsating aurora: EISCAT and Van Allen Probe observations. Journal of Geophysical Research (Space Physics), 120, 2754-2766. doi: 10.1002/2014JA020690

Mughal, M. R., Ali, A., & Reyneri, L. M. (2014). Plug-and-play design approach to smart harness for modular small satellites. Acta Astronautica, 94(2), 754- 764. Retrieved from http://www.sciencedirect.com/science/article/pii/ S009457651300369X doi: https://doi.org/10.1016/j.actaastro.2013.09.015

Nakamura, R., Isowa, M., Kamide, Y., Baker, D. N., Blake, J. B., & Looper, M. (2000, July). SAMPEX observations of precipitation bursts in the outer radiation belt. Journal of Geophysical Research: Space Physics, 105, 15875-15886. doi: 10.1029/2000JA900018

Noman, M., Zulqamain, S. M., Mughal, M. R., Ali, A., & Reyneri, L. M. (2017, June). Component selection for magnetic attitude subsystem of pnss-1 small satellite. In 2017 8th international conference on recent advances in space technologies (rast) (p. 361-367). doi: 10.1109/RAST.2017.8002959

Nygren, T., Aikio, A. T., Kuula, R., & Voiculescu, M. (2011, May). Electric fields and neutral winds from monostatic incoherent scatter measurements by means of stochastic inversion. Journal of Geophysical Research (Space Physics), 116, A05305. doi: 10.1029/2010JA016347

Oleynik, P., & Vainio, R. (2019). Raw simulation data of response of the PATE particle telescope to electrons. [Data set]. Zenodo. doi: http://doi.org/10.5281/zenodo.2682547

Palmroth, M. (2019). Vlasiator. Web site. Retrieved from http://www.physics .helsinki.fi/vlasiator/ (last access: 09.05.2019)

Palmroth, M., Ganse, U., Pfau-Kempf, Y., Battarbee, M., Turc, L., Brito, T., ... von Alfthan, S. (2018). Vlasov methods in space physics and astrophysics. Living Reviews in Computational Astrophysics, 4, 1. doi: 10.1007/s41115-018-0003-2

Palmroth, M., & the Vlasiator team. (2019). Vlasiator: hybrid-vlasov simulation code. Github repository. Retrieved from https://github.com/fmihpc/ vlasiator/ (Version 3.0, last access: 09.05.2019)

Phipps, C. R., Baker, K. L., Libby, S. B., Liedahl, D. A., Olivier, S. S., Pleasance, L. D., ... Valley, M. T. (2012). Removing orbital debris with lasers. Advances in Space Research, 49(9), 1283 - 1300. doi: 10.1016/j.asr.2012.02.003

Pytte, T., Trefall, H., Kremser, G., Jalonen, L., & Riedler, W. (1976, July). On the morphology of energetic /not less than 30 keV/ electron precipitation during the growth phase of magnetospheric substorms. Journal of Atmospheric and Terrestrial Physics, 38, 739-755. doi: 10.1016/0021-9169(76)90112-4

Reeves, G. D., McAdams, K. L., Friedel, R. H. W., & O'Brien, T. P. (2003, May). Acceleration and loss of relativistic electrons during geomagnetic storms. Geophysical Research Letters, 30, 1529. doi: 10.1029/2002GL016513

Rodger, C. J., Kavanagh, A. J., Clilverd, M. A., & Marple, S. R. (2013, December). Comparison between POES energetic electron precipitation observations and riometer absorptions: Implications for determining true precipitation fluxes. J. Geophys. Res. Space Physics, 118, 7810-7821. doi: 10.1002/2013JA019439

Saito, S., Miyoshi, Y., & Seki, K. (2010, August). A split in the outer radiation belt by magnetopause shadowing: Test particle simulations. Journal of Geophysical Re-

<!-- PDF_PAGE: 25 -->

search (Space Physics), 115, A08210. doi: 10.1029/2009JA014738

Sandroos, A. (2019). Vlsv: file format and tools. Github repository. Retrieved from https://github.com/fmihpc/vlsv/ (last access: 09.05.2019)

Sauvaud, J. A., Moreau, T., Maggiolo, R., Treilhou, J. P., Jacquey, C., Cros, A., ... Gangloff, M. (2006, April). High-energy electron detection onboard DEMETER: The IDP spectrometer, description and first results on the inner belt. Planetary and Space Science, 54, 502-511. doi: 10.1016/j.pss.2005.10.019

Seppänen, H., Kiprich, S., Kurppa, R., Janhunen, P., & Haegström, E. (2011, November). Wire-to-wire bonding of $ \mu $m-diameter aluminum wires for the Electric Solar Wind Sail. Microelectronic Engineering, 88, 3267-3269. doi: 10.1016/j.mee.2011.07.002

Shain, C. A. (1951, September). Galactic Radiation at 18.3 Mc/s. Australian Journal of Scientific Research A Physical Sciences, 4, 258. doi: 10.1071/PH510258

Shprits, Y. Y., Angelopoulos, V., Russell, C. T., Strangeway, R. J., Runov, A.,

Shprits, Y. Y., Angelopoulos, V., Russell, C. T., Strangeway, R. J., Runov, A., Turner, D., ... Clemmons, J. H. (2018, February). Scientific Objectives of Electron Losses and Fields INvestigation Onboard Lomonosov Satellite. Space Science Reviews, 214, 25. doi: 10.1007/s11214-017-0455-4

Shprits, Y. Y., Subbotin, D. A., Meredith, N. P., & Elkington, S. R. (2008, November). Review of modeling of losses and sources of relativistic electrons in the outer radiation belt II: Local acceleration and loss. Journal of Atmospheric and Solar-Terrestrial Physics, 70, 1694-1713. doi: 10.1016/j.jastp.2008.06.014

Shprits, Y. Y., Thorne, R. M., Horne, R. B., Glauert, S. A., Cartwright, M., Russell, C. T., ... Kanekal, S. G. (2006, March). Acceleration mechanism responsible for the formation of the new radiation belt during the 2003 Halloween solar storm. Geophysical Research Letters, 33, L05104. doi: 10.1029/2005GL024256

Simnett, G. M. (2011, July). Energetic neutral atoms from the Sun: an alternative interpretation of a unique event. Astronomy & Astrophysics, 531, A46. doi: 10.1051/0004-6361/201116429

Spiro, R. W., Reiff, P. H., & Maher, J., L. J. (1982). Precipitating electron energy flux and auroral zone conductances-an empirical model. Journal of Geophysical Research, 87, 8215-8227. doi: 10.1029/JA087iA10p08215

Thorne, R. M. (1974, April). A possible cause of dayside relativistic electron precipitation events. Journal of Atmospheric and Terrestrial Physics, 36, 635. doi: 10.1016/0021-9169(74)90087-7

Thorne, R. M. (2010, November). Radiation belt dynamics: The importance of wave-particle interactions. Geophysical Research Letters, 37, L22107. doi: 10.1029/2010GL044990

Thorne, R. M., & Kennel, C. F. (1971, January). Relativistic electron precipitation during magnetic storm main phase. Journal of Geophysical Research, 76, 4446. doi: 10.1029/JA076i019p04446

Tsuda, Y., Mori, O., Funase, R., Sawada, H., Yamamoto, T., Saiki, T., ...

Kawaguchi, J. (2013, February). Achievement of IKAROS - Japanese deep space solar sail demonstration mission. Acta Astronautica, 82, 183-188. doi: 10.1016/j.actaastro.2012.03.032

Tu, W., Selesnick, R., Li, X., & Looper, M. (2010). Quantification of the precipitation loss of radiation belt electrons observed by sampex. Journal of Geophysical Research: Space Physics, 115(A7). doi: 10.1029/2009JA014949

Tummala, A. R., & Dutta, A. (2017). An overview of cube-satellite propulsion technologies and trends. Aerospace, 4(4). doi: 10.3390/aerospace4040058

Turner, D. L., Angelopoulos, V., Li, W., Bortnik, J., Ni, B., Ma, Q., ... Rodriguez, J. V. (2014, March). Competing source and loss mechanisms due to wave-particle interactions in Earth's outer radiation belt during the 30 September to 3 October 2012 geomagnetic storm. Journal of Geophysical Research (Space Physics), 119, 1960-1979. doi: 10.1002/2014JA019770

<!-- PDF_PAGE: 26 -->

Tverskoy, B. A. (1969). Main mechanisms in the formation of the Earth's radiation belts. Reviews of Geophysics and Space Physics, 7, 219-231. doi: 10.1029/RG007i001p00219

Ukhorskiy, A. Y., Anderson, B. J., Brandt, P. C., & Tsyganenko, N. A. (2006, November). Storm time evolution of the outer radiation belt: Transport and losses. Journal of Geophysical Research (Space Physics), 111(10), A11S03. doi: 10.1029/2006JA011690

van Allen, J. A., & Frank, L. A. (1959, February). Radiation Around the Earth to a Radial Distance of 107,400 km. Nature, 183, 430-434. doi: 10.1038/183430a0

van de Kamp, M., Seppälä, A., Clilverd, M. A., Rodger, C. J., Verronen, P. T., & Whittaker, I. C. (2016). A model providing long-term data sets of energetic electron precipitation during geomagnetic storms. J. Geophys. Res. Atmospheres, 121, 12,520-12,540. doi: 10.1002/2015JD024212

von Alfthan, S., Pokhotelov, D., Kempf, Y., Hoilijoki, S., Honkonen, I., Sandroos, A., & Palmroth, M. (2014). Vlasiator: First global hybrid-Vlasov simulations of Earth's foreshock and magnetosheath. Journal of Atmospheric and Solar-Terrestrial Physics, 120, 24-35. doi: 10.1016/j.jastp.2014.08.012

Walt, M. (1996). Source and Loss Processes for Radiation Belt Particles. Washington DC American Geophysical Union Geophysical Monograph Series, 97, 1. doi: 10.1029/GM097p0001

West, H. I., Buck, R. M., & Walton, J. R. (1972, November). Shadowing of Electron Azimuthal-Drift Motions near the Noon Magnetopause. Nature Physical Science, 240, 6-7. doi: 10.1038/physci240006a0

Woodger, L. A., Halford, A. J., Millan, R. M., McCarthy, M. P., Smith, D. M., Bowers, G. S., ... Liang, X. (2015, June). A summary of the BARREL campaigns: Technique for studying electron precipitation. Journal of Geophysical Research (Space Physics), 120, 4922-4935. doi: 10.1002/2014JA020874