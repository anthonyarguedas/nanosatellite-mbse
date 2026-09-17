---
source: null
title: "citation-candidate-2892"
page_count: 35
converted_at: "2026-09-08T16:49:33Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# Aalto-1, multi-payload CubeSat: In-orbit results and lessons learned

</div>

M. Rizwan Mughal $ ^{1} \mathrm{a} $ , J. Praks $ ^{a} $ , R. Vainio $ ^{b} $ , P. Janhunen $ ^{c} $ , J. Envall $ ^{c} $ A. Nasilä $ ^{d} $ , P. Oleynik $ ^{b} $ , P. Niemelä $ ^{a} $ , A. Slavinskis $ ^{a, e} $ , J. Gieseler $ ^{b} $ N. Jovanovic $ ^{a} $ , B. Riwanto $ ^{a} $ , P. Toivanen $ ^{c} $ , H. Leppinen $ ^{a} $ , T. Tikka $ ^{a} $ A. Punkkinen $ ^{b} $ , R. Punkkinen $ ^{f} $ , H.-P. Hedman $ ^{f} $ , J.-O. Lill $ ^{g} $ , J.M.K. Slotte $ ^{h} $

$ ^{a} $Department of Electronics and Nanoengineering, Aalto University School of Electrical Engineering, 02150 Espoo, Finland

$ ^{b} $ Department of Physics and Astronomy, University of Turku, 20014 Turku, Finland $ ^{c} $ Finnish Meteorological Institute, Space and Earth Observation Centre, Helsinki, Finland $ ^{d} $ VTT Technical Research Centre of Finland Ltd, Espoo, Finland

$ ^{e} $ Tartu Observatory, University of Tartu, Observatoriumi 1, 61602 Tõravere, Estonia $ ^{f} $ Department of Future Technologies, University of Turku, 20014 Turku, Finland $ ^{g} $ Accelerator Laboratory, Turku PET Centre, Åbo Akademi University, 20500 Turku, Finland

$ ^{h} $ Physics, Faculty of Science and Technology, Åbo Akademi University, 20500 Turku, Finland

## Abstract

The in-orbit results and lessons learned of the first Finnish satellite Aalto-1 are briefly presented in this paper. Aalto-1, a three-unit CubeSat which was launched in June 2017, performed Aalto Spectral Imager (AaSI), Radiation Monitor (RADMON) and Electrostatic Plasma Brake (EPB) missions. The satellite partly fulfilled its mission objectives and allowed to either perform or attempt the experiments. Although attitude control was partially functional, AaSI and RADMON were able to acquire valuable measurements. EPB was successfully commissioned but the tether deployment was not successful.

In this paper, we present the intended mission, in-orbit experience in operating and troubleshooting the satellite, an overview of experiment results, as well as lessons learned that will be used in future missions.

Keywords: Aalto-1, CubeSat, In-orbit results, Lessons learned, Aalto

<!-- PDF_PAGE: 2 -->

## 1. Introduction

There has been a significant increase in the design, development, launch and operation of nano and micro satellites since last two decades. A large number countries initiated their space activities and a large number of Newspace companies emerged as an outcome. A number of innovative platform subsystems, payloads and missions have been proposed, designed and launched by universities and small industry thanks to significantly reduction of development and launch costs [1,2,3,4,5,6,7,8,9]. This has been made possible due to availability of Commercial Off The Shelf (COTS), technology miniaturization and affordable rides. The CubeSat standard, initially perceived for educational purposes only, was defined by Stanford and California Polytechnic State Universities in 1999 [10]. Since the launch of first CubeSat in 2003, this standard has revolutionized the space industry by playing an increasingly important role in technology demonstrations, remote sensing, Earth observation and education [11,12]. More recently, the CubeSats have started to increasingly exploit the scientific and commercial use cases [12,13]. Being small in size, they have transformed the traditional design approach of space systems by providing low-cost access to space [14,15,16,17]. A single ride of launch vehicle can carry hundreds of CubeSat-class satellites. Many universities are effectively using CubeSats as hands-on tools to teach the challenging engineering concepts about the design and development of complex interdisciplinary systems. The launch and operation phase provides a unique learning experience to university teams enabling them to learn essential skills in mission design and operations [18]. Now a day's university CubeSat missions aim at real science and technology demonstration while also ensuring the educational objectives. It is important for CubeSat community to share the knowledge, in orbit experiences, lessons learned and mission details which will consequently help other teams to gain valuable experience and not repeat the same mistakes.

The current small satellite literature lacks the whole life cycle: i.e. all aspects relating to mission planning, design, launch, operations and lessons learned. The teams either report very specific technical information of the design, or come up with mission descriptions and in-orbit results. One can barely find information in the current literature about complete life cycle

<!-- PDF_PAGE: 3 -->

covering a wide range of aspects. In order to provide the CubeSat community with the sufficient details on complete aspects in terms of technology development, technology demonstration and key experiences, we present the design, development and in-orbit experience of Aalto-1, the first satellite of Aalto University, Finland. We present our findings in two papers: the first one covering the technology development aspects [19] whereas the present paper covers the in-orbit results and lessons learned.

## 2. Mission overview

Aalto-1, shown in Fig. 1, is a 3U CubeSat designed and developed by Aalto university and partner organizations. The spacecraft was launched in June 2017 and hosted three payloads: AaSI, RADMON and EPB.

AaSI is the first hyperspectral imaging system compatible with nanosatellites, based on a piezo-actuated tunable Fabry-Pérot Interferometer (FPI) which allows for an unprecedented miniaturization [20]. The instrument fits in a half of CubeSat unit and, within a few seconds, can acquire spectral images in tens of freely programmable channels. The filter works in the spectral range of 500-900 nm where each channel is 10-20 nm wide. A $ 5 1 2 \times5 1 2 $ -pixel sensor with a $ 1 0^{\circ} $ field of view provides a ground resolution better than 200 m per pixel.

RADMON, fitting within 0.4 CubeSat units, is one of the smallest particle detectors, which has proven itself capable of taking scientific measurements [21, 22]. It measures electron energies in the >1.5 MeV range and protons in the >10 MeV range.

EPB is novel deorbiting technology which employs the coulomb drag between the ionospheric plasma and a long charged tether [23, 24]. The tether is deployed using a centrifugal force and it is estimated that a 100-m tether (such as on-board Aalto-1) could decrease an altitude by 100 km of a three- unit CubeSat within 600 days [25]. A similar experiment was carried on board ESTCube-1 [26, 27] where tether deployment was not successful [28]. While Aalto-1 EPB experiment was improved based on ESTCube-1 ground test results, yet the deployment of EPB was not successful. This is due to the fact that Aalto-1 flight hardware had to be delivered soon after the ESTCube-1 experiment was carried out and, therefore, the team did not have time and resources to redesign the EPB module, as it is being done for the FORESAIL-1 mission [25].

<!-- PDF_PAGE: 4 -->


![figure_001.png](figure_001.png)




![figure_002.png](figure_002.png)



<div align="center">

Figure 1: Overview of Aalto 1 subsystems and photograph of Flight Model (FM).The highlighted subsystems are: 1) Radiation Monitor (RADMON), 2) Electrostatic Plasma Brake (EPB) 3) Global Positioning System's (GPS's) antenna and stack interface board, 4) Attitude Determination and Control System (ADCS), 5) GPS and S-band radio, 6) Aalto Spectral Imager (AaSI), 7) Electrical Power System (EPS), 8) On-Board Computer (OBC), 9) Ultra High Frequency (UHF) radios, 10) solar panels, 11) electron guns for EPB, 12) S-band antenna, 13) debug connector

</div>

In this paper, section 3 briefly introduces mission timeline representing the launch and operations. Section 4 presents the in-orbit results and lessons learned of all the payloads. RADMON in-orbit results are introduced briefly based on previously published results [21, 22]. EPB in-orbit results and lessons learned are discussed in detail, especially the possible reasons of tether deployment failure. AaSI detailed in-orbit results are presented here for the first time. Furthermore, Section 5 introduces in-orbit experience of platform's subsystems. Section 6 discusses the results and concludes the paper.

<!-- PDF_PAGE: 5 -->

## 3. Mission timeline

The spacecraft was launched aboard PSLV-C38 launch vehicle at 05:59 Eastern European Time (EET) and the first beacon was recorded by a Software Defined Radio (SDR) located in South Africa at approximately 08:30 EET. The first contact with the Aalto University ground station was established during the first pass at 10:07 EET.

During the consequent passes, several responses were recorded, but were not decoded due to an unidentified problem in the ground station reception chain. Later on the problem was troubleshooted to be in mast pre-amplifier. While powering it off provided a directional link with the CubeSat, it came at a cost-a loss in the signal strength.

The mission wise timeline on the commissioning and operations of each experiment is presented in Fig. 2. During Launch & Early Operations Phase (LEOP), the first AaSI picture was downloaded and RADMON commissioning phase was started. As part of Aalto-1 operations, multiple AaSI campaigns have been completed. RADMON operations resulted in a useful data set during nominal conditions and also during a solar storm. EPB campaign resulted in partial success in commissioning phase but failure in tether deployment.


![figure_003.png](figure_003.png)



<div align="center">

Figure 2: Mission timeline

</div>

## 4. Mission payloads

This section describes the in orbit performance of RADMON, EPB and AaSI payloads. The thorough design approach, selection and implementation has been presented in accompanying paper [19].

<!-- PDF_PAGE: 6 -->

## 4.1. Radiation monitor mission

The RADMON is a small $ ( 4 \times9 \times1 0 \mathrm{c m}^{3},3 6 0 \mathrm{g} ) $ low-power (1 W) radiation monitor [29,19]. The monitor detects protons and electrons employing a regular $ \Delta\mathrm{E}-\mathrm{E} $ analysis to distinguish between particle species. The detectors of the instrument are a $ 2. 1 \times2. 1 \times0. 3 5 \mathrm{m m}^{3} $ silicon detector and a $ 1 0 \times1 0 \times1 0 \mathrm{m m}^{3} $ CsI(Tl) scintillation detector placed inside a brass envelope (see Figure 3). The envelope of the detector compartment is opaque for protons below 50 MeV and electrons below 8 MeV. The envelope has a 280 $ \mu\mathrm{m} $ aluminum entrance window that stops low energy photons and low energy charged particles. A particle must hit both detectors to be registered. Therefore, the thicknesses of the entrance window and the silicon detector set the lower energy threshold for protons to about 10 MeV and electrons to about 1.5 MeV. A detailed description of the instrument calibration is presented in [22].


![figure_004.png](figure_004.png)



<div align="center">

Figure 3: The RADMON radiation monitor cross section. The arrow on the picture shows a particle that is incident within the instrument aperture. The brass case is light-brown. The silicon detector is light blue, surrounded by a blue passive silicon area, which is fixed on a printed circuit board (PCB) shown as dark gray. The CsI(Tl) scintillator is shown in green. Under the scintillator there is a photodiode shown in dark blue. White structure on the bottom is an alumina case of the photodiode.

</div>

## 4.1.1. In-orbit results

RADMON in-orbit calibration campaign was carried out in September 2017. It was discovered that the gain of the scintillator did not match the value obtained from ground calibrations, but was about 30% lower. The reason could not be positively determined, but the deterioration of the optical contact between the CsI(Tl) crystal and the photodiode during launch vibrations could potentially be responsible for this decay of performance. A successful in-flight calibration was, however, achieved using data obtained in

<!-- PDF_PAGE: 7 -->

a dedicated calibration mode, which allows raw data from detectors to be down-linked. The in-flight calibration is discussed in detail in [22].

The first observational campaign of RADMON started on 10 October 2017 and lasted until 2 May 2018. Using these data, it has been demonstrated in [21] that the instrument is able to measure the integral intensities of electrons above 1.5 MeV and protons above 10 MeV in Low Earth Orbit (LEO), reflecting the dynamic environment of the radiation belts. Fig. 4 shows the temporal evolution of daily electron intensities from October to December 2017 with respect to McIlwain L parameter [30] (indicating the equatorial distance of drift shells) together with the Dst (disturbance storm time) index as a measure for geomagnetic storm intensity [31, 32]. The two observed moderate geomagnetic storms result in strong enhancements of the outer radiation belt, while periods following small storms are characterized by reduced electron intensities in the outer belt.

Figure 4 also illustrates the contamination of all electron measurements by higher energy protons: the constantly increased intensities in the L range below 2 correspond to the proton-dominated inner radiation belt. Further comparisons with electron spectra observed in a similar but slightly higher orbit (820 km) by the Energetic Particle Telescope (EPT) onboard the ESA minisatellite (volume <1 m $ ^{3} $ ) PROBA-V (PProject for OnBoard AutonomyVegetation) showed a good agreement for the >1.5 MeV electron channel of RADMON [21].

Next observation effort was made late in 2019 to check if the instrument functions well. We have ensured that the instrument is in a good shape, but the satellite lacks power for continuous operations of RADMON. A compromise was found to keep RADMON operating for every 12 hours with a 3-hour break to ensure recharge of the satellite battery. A new set of calibration data from the end of 2019 confirmed that the calibration of the detectors had not changed during the 2.5 years in space and that no visible signs of detector degradation could be identified.

## 4.1.2. Lessons learned

RADMON is a successful space experiment and, certainly, it can be improved. Minimization of the contamination of electron channels by highenergy protons would be the most valuable improvement for the instrument. The collimator geometry should also be streamlined to achieve an optimal instrument aperture.

The current design is such that particles enter the instrument within a

<!-- PDF_PAGE: 8 -->


![figure_005.png](figure_005.png)



<div align="center">

Figure 4: From top to bottom: Time series of Dst index and four histograms of integral intensities with respect to L parameter obtained by the different RADMON electron channels from 10 Oct 2017 to 21 Dec 2017. The z-axis gives color-coded arithmetic daily mean of intensity per bin - note that the color scale is different for all panels in order to enhance the details of all channels which have different sensitivities. Figure adapted from [21] by permission of Elsevier, $ \textcircled{c} $2019 COSPAR.

</div>

$ \approx 2 0^{\circ} $ half-width cone defined by an opening in the brass container. The opening is manufactured as a right-angle shaft sufficiently larger than the dimension of the silicon detector (see Fig. 3).

An incident particle may, therefore, hit a side of the silicon detector in a way that it deposits energy into its active area and its passive area in an arbitrary proportion. Further, it hits the scintillation detector. This effect leads to an underestimation of energy deposited in the $ \Delta\mathrm{E} $ detector. Subsequently, such a particle is misclassified. A silicon detector with two concentric active areas would contribute to better particle classification and reduce contamination of electron channels by protons. The detector should

<!-- PDF_PAGE: 9 -->

trigger on the central dot and add the energy deposited in the encircling area to its output signal. One of the possible geometries could be a "sandwich" detector with a thinner layer carrying the central spot and a thicker layer beneath. In this case, it is even easier to get the correct $ \Delta\mathrm{E} $ signal since the energy loss in the thinner layer would not be needed for the pulse height analysis. Any signal above the threshold would gate the particle detection by the $ \Delta\mathrm{E}-\mathrm{E} $ detectors below. The thickness of the top detector can be about 100-150 $ \mu\mathrm{m} $ and should be optimized for scientific requirements. A thicker detector would show more edge effects than a thin one, but could have a better signal-to-noise ratio. The thickness of the entrance window should be adjusted as well during the optimization.

Another issue is that the current geometry allows a gradual increase in the angle of the acceptance cone. The collimator should be designed as a conical opening in the shielding container so that it becomes transparent at sharper energy threshold. It would improve the flatness of the particle response at moderate energies.

A simulation of the suggested layered design carried out within the Geant4 [33,34] framework is compared to a simulation of the current design in Fig. 5. The "sandwich" has a thin silicon detector right on top of the $ \Delta E $ silicon detector. Both detectors are square and of the same size. The instrument container has a tantalum front wall, which can be optimized further to a tantalum lining of the container opening. This reduction is possible since the upper thin silicon detector sets the accepted solid angle for a particle to be detected. High energy protons coming within the aperture are still detected as electrons. Nevertheless, limiting the solid angle of the instrument acceptance for such protons improves the quality of the observational data. In a proton-rich environment, such as South Atlantic geomagnetic anomaly, contamination of electron channels could be used as a secondary proxy on the proton population.

As a positive takeaway from the experiment, the successful RADMON re-calibration using in-flight data showed that a dedicated mode allowing the full pulse height data to be downloaded also from space can render a RADMON-like instrument to a self-calibrating device. Thus, an expensive full calibration campaign in high-energy beam facilities, reaching hundreds of MeVs in proton energies, can be avoided using this approach.

<!-- PDF_PAGE: 10 -->


![figure_006.png](figure_006.png)



<div align="center">

Figure 5: The contamination of electron channels (e3 and e5 are chosen as examples) by high energy protons in comparison to a proposed "sandwich" design.

</div>

## 4.2. Electrostatic Plasma Brake

The key components of the EPB payload are those of the tether reeling mechanism as shown in Fig 6. These include the tether reel, reel motor (not visible), tether chamber, tether tip mass, tip mass launch lock (Kaiku), and reel launch lock (Kieku). The reel motor (vacuum qualified piezo motor) is nested inside the reel. The control electronics underneath the tether reeling Printed Circuit Board (PCB), separate high voltage PCB, and electron emitters are similar to those of ESTCube-1 as described earlier in the literature [27]. Only changes introduced were related to the revised launch locks and additional diagnostics. The high voltage converter was changed to double the voltage from $ \pm 500 $ kV to $ \pm 1000 $ kV which caused some minor changes in the electron emitters.

The revised launch locks and additional diagnostics included the following components. The reel lock was newly designed and diagnostics was added. Behind the spring loaded lock shaft is an optoport (black component next to the lock in the left panel of Fig. 6. When the lock was burned the state of the optoport was designed to change from open to close. To monitor the tip mass before and after the tip mass lauch lock was released, a pair of phototransistor (Kyylä) and IR LED (Soihtu) was mounted in the tether chamber opposite to the opening tube of the tip mass and tether (two holes in the top right corner of the tether chamber in the right panel of Fig. 6). The IR LED can be used to healthy check the phototransistor prior to the tip mass release. After the release, if the tether should be damaged, the phototransistor observed light freely entering to the tether chamber.

<!-- PDF_PAGE: 11 -->


![figure_007.png](figure_007.png)



<div align="center">

Figure 6: EPB Mechanical parts on the PCB (left) and key tether reeling components: reel, tip mass, tether chamber, and tip mass launch lock (right). The reel lock can be seen on the left panel left side of the tether chamber.

</div>

## 4.2.1. In-orbit results

The in-orbit tests of the plasma brake started with a commission phase, in which the On Board Computer (OBC) sent EPB a number of commands with the goal of verifying its operational state. This list included essentially all the commands which were safe to run without any risk of hazard. This restriction ruled out e.g. the commands that would initiate physical changes in the payload's status (launch lock burns, motor activation) or the ones not usable at this point of the mission (high voltage or electron gun activation). The commands that were run all worked as designed, returning some housekeeping data for analysis. Most importantly at this point, the data showed that all systems were at nominal state and that the launch locks had kept the tether reel and the tip mass intact.

The second step in in-orbit tests was to open the two launch locks that had locked the tether reel and the tip mass during the launch. Each lock was opened by applying a 150 mA current, which would melt the dyneema string keeping the spring loaded lock at closed state. The tether reel lock, named Kieku, had an integrated optical diagnostics system whose state could be read by the OBC at any time. During the burn sequence the system's state switched from "locked" to "deployed" after about 12 seconds of burning as shown in Fig. 7. Similar diagnostics were not available for the tip mass lock Kaiku. The duration of the burn current for Kaiku was chosen long enough to ensure a proper deployment.

The final verification of the operational readiness before attempting tether

<!-- PDF_PAGE: 12 -->


![figure_008.png](figure_008.png)



<div align="center">

Figure 7: Flight data showing the deployment of the tether reel lock Kieku.

</div>

deployment was performed with the help of the photosensor Kyylä. Kyylä is a simple phototransistor placed inside the tether reel chamber. It has the backside of the tip mass in the center of its field of view. If the tip mass had been ejected from its nest prematurely, the light (e.g. from Earth albedo) entering the chamber could easily be detected in Kyylä's signal. An example data plot from an early Kyylä scan is shown in Fig. 8. The extremely narrow width of the peaks indicate that even though light is able to enter the chamber, it is able to do so over a very narrow angle only, as the satellite is spinning. This may be explained as follows. The tip mass, roughly cylinderic, remains like a plug in the tether opening tube. The tip mass is not tightly in the tube but held to its place by the launch lock. Thus there is a tiny gap between the tip mass and the tube walls that provides the light with a passage of the narrow angle. If the tip mass was completely removed, the shape of the peaks would be considerably wider. Another piece of infor-

<!-- PDF_PAGE: 13 -->

mation obtained from these tests was the confirmation of the satellite's spin rate. An approximate seven second periodicity of the peaks coincided precisely to the angular velocity data of the Attitude Determination & Control Subsystem (ADCS). Simultaneously it provided proof that Kyylä was indeed measuring real phenomena of its surroundings and not some arbitrary electrical disturbances.


![figure_009.png](figure_009.png)



<div align="center">

Figure 8: Flight data from the phototransistor Kyyylä. The periodicity of the signal corresponds to the satellite's spin rate at the time.

</div>

After the successful initial tests and preparations it was time to attempt tether deployment. A controlled spin-up of the satellite could not be performed due to the shortcomings of the satellite's ADCS which are described in detail in section5. The satellite was nonetheless spinning through natural causes and its spin axis and angular velocity ( $ \approx $ 50 degrees per second) were, by chance, suitable for taking a shot at deployment.

The spin rate for EPB deployment was verified by magnetometer and gyroscope telemetry data. Figures 9 and 10 present the high resolution measure-

<!-- PDF_PAGE: 14 -->

ment data in time and frequency domains respectively and Fig. 11 presents the calibrated gyroscope data during the EPB deployment campaign.


![figure_010.png](figure_010.png)



<div align="center">

Figure 9: Magnetometer high resolution data during EPB deployment campaign

</div>

Despite having achieved the desired spin rate around tether deployment axis, the deployment attempts all failed, unfortunately. In each attempt the motor was commanded to make a turn that is relatively small but still easily detectable. We couldn't observe any changes in the tether reel rotary position. The vacuum qualified piezo motor has an in-built potentiometer based rotary encoder. Fig. 12 shows the values measured by this encoder throughout the tether deployment trials. The peak-to-peak variation of the values corresponds to a $ 1. 4^{\circ} $ turn, or 0.4 mm on the perimeter of the reel. The conclusion must be that no detectable motor movement has taken place. If the motor had worked nominally, the turn angle would have been tens of degrees.

## 4.2.2. Lessons learned

The most noticeable result of the EPB mission is obviously the failure of the tether deployment hardware. It is somewhat unclear why this happened, even though several clues exist. Figure 12 shows examples of the measured

<!-- PDF_PAGE: 15 -->


![figure_011.png](figure_011.png)



<div align="center">

Figure 10: Magnetometer high resolution flight data during EPB deployment campaign in frequency domain confirming the spin rate around the spin axis

</div>

motor voltage during two tether deployment attempts. In normal operation the motor voltage would remain in its nominal value of approximately 40 volts. As the plots show, the voltage is cut off and starts a rather rapid decay as soon as it has been switched on. The motor voltage is generated within the EPB control electronics with the help of a boost converter. In Fig. 12 the voltage appears to saturate at the level of the boost converter's input voltage. This would indicate that the faulty operation of the boost converter is the source of all grief.

Not all went haywire, though. Several newly developed systems, some including moving parts, worked exactly as planned. Especially the completely renewed design for the tether reel lock Kieku proved to be a reliable work horse in space. At this point it is important to introduce the reader to the launch history of the EPB payload. A very similar payload was first launched on-board ESTCube-1 [26,27]. Its fate was identical to that of Aalto-1 EPB. It is important to note that the timelines of the two satellite missions overlapped in a most unfortunate way. Once the in-orbit results of ESTCube-1 were ready and verified, the delivery date of the Aalto-1 flight model hard-

<!-- PDF_PAGE: 16 -->


![figure_012.png](figure_012.png)



<div align="center">

Figure 11: High resolution gyroscope calibrated flight data during EPB deployment campaign

</div>

ware was only four months away. Also, due to the lack of proper on-board diagnostics, the reasons for the failure were mostly unknown. Therefore the EPB team was lacking both the proper time and the accurate knowledge of the problem in order to make fundamental changes in the motor hardware and control electronics. Instead, a number of features were added to gather all the information possible, in order to at least see what is happening in case of repeated failure. All these diagnostics tools described above (Kyylä, Kieku's optical feedback, motor's position encoder) worked as planned. This allowed the EPB team to have an instant view of the situation in orbit and finally get valuable clues of what happened on-board ESTCube-1 as well. The last minute changes could not help the Aalto-1 EPB to complete its mission, but at the very least they helped in compiling a road-map towards more successful missions in the future. A small step for Coulomb drag industry, but a step forward nonetheless.

<!-- PDF_PAGE: 17 -->


![figure_013.png](figure_013.png)



<div align="center">

Figure 12: Measured values of the rotary encoder of the tether reel motor. These values were recorded over several tether deployment attempts. The peak-to-peak variation of the values corresponds to a turn of 1.4 degrees. The pre-launch value recorded in the last ground tests was 421.

</div>

## 4.3. Aalto-1 Spectral Imager AaSI

## 4.3.1. In-orbit results

After establishing communications, the VIS camera was first powered on the $ 3^{rd} $ of July, 2017. The first housekeeping data from the camera indicated nominal behaviour, and the instrument temperature was ca. $ -5^{\circ} \mathrm{C} $ . The first image, as shown in Fig. 14, was taken on the $ 5^{th} $ of July, while the satellite was still tumbling. During image acquisition, the satellite was located over Norway with the field of view pointed to the southern direction towards Denmark. Based on visual analysis, the image quality is good, and no visible de-focusing or new aberrations are present.

The spectral camera was first powered on the $ 2 5^{th} $ of July, and the instrument housekeeping data was nominal. The temperature was around $ - 5^{\circ} \mathrm{C} $

<!-- PDF_PAGE: 18 -->


![figure_014.png](figure_014.png)



<div align="center">

Figure 13: Two data sets of the motor voltage during the tether deployment attempts. Notice the saturation at the level of the input voltage ( $ \approx $ 11 volts) of the boost converter. In each set the last data point was recorded after the input voltage had been switched off.

</div>

and the piezo voltages for the FPI were between 26 V and 28 V, which indicated perfect health for the FPI unit. When compared to piezo voltages measured on ground prior to launch, there was approximately 10 V difference in one of the channels. This was expected as there is a temperature difference between the measurements （ $ + 2 2^{\circ} \mathrm{C} $ at the pre-launch check vs. $ - 5^{\circ} \mathrm{C} $ in orbit) and the water absorbed by the piezo actuators has evaporated at the time of taking in-orbit measurements.

First images were taken with the spectral camera on the $ 3^{rd} $ of August. From these images, the functionality of the camera optics was verified. The imaged scene was covered by clouds, and in the false color composite as shown in Fig. 15, one can see spectral variation in the clouds. During this time, the satellite was still tumbling quite rapidly, so the imaged area is moving significantly between the spectral frames.

<!-- PDF_PAGE: 19 -->


![figure_015.png](figure_015.png)



<div align="center">

Figure 14: The first image downlinked from Aalto-1. The image is taken with the VIS camera on $ 5^{th} $ of July, 2017 and it shows the coastline of Denmark together with Earth's horizon.

</div>

After the performance of optics was verified, the on-board spectral calibration method was tested. The calibration is based on measuring a bright target (e.g. cloud or desert) and scanning the spectral filter over the cutoff wavelength of the 900 nm short pass filter and taking an average of the pixel values. The sequential images are recorded with very small wavelength increment. When the spectral transmission peak passes over the short pass filter, the signal level will drop. When the signal is plotted as a function of FPI set point voltage, the drop in signal level is visible. The location where the slope is steepest corresponds to the cutoff wavelength of the shortpass filter. Successful calibration measurement was performed on the $ 5^{th} $ of September which is shown in Fig. 16. When compared to measurements done on ground, it can be seen that the spectral behaviour is similar, but due to the cold temperature $ (-1 6^{\circ} \mathrm{C}) $ and different illumination conditions the shape of the calibration spectrum is different.

The satellite was de-tumbled in June 2018 and the imaging campaign was continued immediately after de-tumbling. During this campaign, an image

<!-- PDF_PAGE: 20 -->


![figure_016.png](figure_016.png)



<div align="center">

Figure 15: False color composite of the first spectral image captured by AaSI. The approximate wavelengths in the image are R=710 nm, G=535 nm and B=510 nm. The tumbling of the satellite is clearly visible as the frames do not contain much overlap. The bottom part of the image shows as yellow, as the wavelengths 535 nm and 710 nm are extracted from the same raw image.

</div>

mosaic was created from VIS images, and finally on August 6, 2018 the first cloud-free images of land targets were acquired. The imaging sequence started at the equator above Congo, and continued for about six minutes while the satellite was travelling south toward South Africa. The images of six different wavelengths were acquired, and, from the resulting spectrum, the red-edge of vegetation is clearly visible, as shown in Fig. 17.

An image compression program was uploaded to the satellite during the spring of 2018. This was first tested around the midsummer of 2018, and several series of images were taken. In order to downlink the image mosaics, image compression was required. After compression, the images were successfully downlinked. The stiched mosaic is shown in Fig. 18. The slow tumbling of the satellite is clearly visible in the sequential images.

<!-- PDF_PAGE: 21 -->


![figure_017.png](figure_017.png)




![figure_018.png](figure_018.png)



<div align="center">

Figure 16: Calibration measurement comparison. In the top figure, the signal level is plotted as function of FPI set point voltage. Signal derivative is plotted in the bottom figure. The position with the steepest slope corresponds to the filter cutoff wavelength. The filter cutoff position is visible in both cases, but the measurement performed in orbit is distorted. This is mainly due to the cold temperature, which is outside the instrument's operation temperature.

</div>

## 4.3.2. Lessons learned

This was the first mission ever to demonstrate a hyperspectral camera on a nanosatellite. It was also the first space-borne demonstration of a tunable FPI-based nanosatellite-compatible hyperspectral camera.

The main lesson learned was that this technology works in space environment and it can be used for nanosatellite-based hyperspectral imagers. All of the primary mission objectives were completed, so the AaSI mission can be considered successful.

Not all functionalities of the imager could be verified though. The tumbling platform prevented imaging of planned targets, and the limited downlink allowed only the use of minimal spectral mode with six wavelengths. However, the tumbling platform showcased the benefits of frame-based spectral imaging, as the images in different wavelengths can be overlapped in post processing. This is a great benefit in nanosatellite missions, as the imager can still be used in the case of attitude control malfunction.

<!-- PDF_PAGE: 22 -->


![figure_019.png](figure_019.png)




![figure_020.png](figure_020.png)



<div align="center">

Figure 17: The first cloud-free spectral image of a land target (top). The image is centered on Tshuapa River near Mbandaka. The false color image is constructed from R=752 nm, G=671 nm, B=565 nm. The bottom figure shows the spectrum of the central area of the image measured at 6 wavelenghts.

</div>


![figure_021.png](figure_021.png)



<div align="center">

Figure 18: Mosaic of sequential VIS images

</div>

<!-- PDF_PAGE: 23 -->

## 5. Platform in-orbit performance

The in-orbit performance of spacecraft platform which consisted of commercial and in house developed subsystems, is briefly presented. While the key platform subsystems were successfully commissioned, the spacecraft accomplished its mission with partial success. The design approach of platform subsystems which consisted of an Electrical Power Subsystem (EPS) [35], an ADCS [36], a Global Positioning System (GPS)-based navigation system [37], a Ultra High Frequency (UHF) [38] and S-band [39] radios for Telemetry, Telecommand & Communication (TT&C), and a Linux-based Onboard Data handling (OBDH) [40] is briefly presented in [19].

## 5.1. In orbit performance of EPS

In order to monitor and keep track of the health of the spacecraft, a number of housekeeping sensors were used. The performance of EPS is presented in terms of telemetry values of voltage, current and temperature sensors. The flight data of these sensors confirms that the EPS is functional and provides power to satellite subsystems since its launch. However, there are some issues. The telemetry data reveals partially degraded performance of one of the solar panels as evident by green plot in Fig. 20. This behaviour is likely due to the un-controlled spin orientation of the satellite. The telemetry data of solar panel temperatures, EPS board temperature and battery temperatures from launch date till Aug 2020 is plotted in Fig. 19. The highest temperature variation takes place on the satellite surface as evident from central graphs representing panel X and Y, where solar panel temperatures change in $ \pm 2 0^{\circ} \mathrm{C} $ range. This range remains quite stable throughout the mission representing that the temperature is at equilibrium. The temperature inside the satellite depends on operation of payloads and platform subsystems. The telemetry data of board and battery temperatures, as evident from Fig. 19, represents that the passive thermal control maintains sufficiently stable temperature fluctuations.

## 5.2. In-orbit performance of ADCS

The commissioning phase of the ADCS functions were met with complications, as some of the sensor readings were erroneous. Two of the sun sensors (on the +X and -X directions of the satellite) were malfunctioned and not usable for attitude estimation. In Fig. 21, the gyroscope readings from regular housekeeping data until October 2017 have a low angular rate

<!-- PDF_PAGE: 24 -->


![figure_022.png](figure_022.png)



<div align="center">

Figure 19: Aalto 1 surface and inner temperatures (in $ \circ $C ) from launch till Aug 2020

</div>

resolution. This was because of improper processing of sensor raw data and a problem with the communication channel in the ADCS module. This was fixed with a small firmware update. Over the course of the mission, sometimes the ADCS module is reset and defaulted to idle mode. Such event will turn off the ADCS sensors which needs to be manually turned on. This shows up as frozen sensor data, visible in Fig. 21 around October-November, 2017 and February-May 2018.

The first attempt to detumble the satellite was attempted on October 2017. The attempt failed because of constant rebooting of the ADCS module when the B-dot control was turned on. The problem was caused by the magnetorquer driver channel which was later fixed with a major firmware and magnetorquer driver update on June 2018 consequently solving the reboot issue. The detumbling operation was tested again with positive results. The spin rate of the satellite was reduced close to 0 deg/sec as confirmed by the telemetry data of Fig. 21. The detumbling control was kept on until September 2018, after which the satellite started to spin up.

The main cause of the uncontrolled spin up of the satellite remains unknown when the B-dot is disabled. Some possible causes are environmental disturbance torque, residual dipole moment generated by unknown magnetic materials or current loop from the solar panels power routing.

Although detumbling with the B-dot controller was successful, many other mission modes, including controlled spin up for tether deployment,

<!-- PDF_PAGE: 25 -->


![figure_023.png](figure_023.png)



<div align="center">

Figure 20: Solar panel current intensities from launch till Aug 2019. The vertical axis represents the generated current (in mA) read by each BCR

</div>

were not successful. The ADCS commissioning modes, including the spin up manoeuvre, has been tried with the magnetorquers only [6, 5]. The reaction wheels showed inconsistencies in their power reading during the early commissioning phase and thus have not been thoroughly tested yet.

An important lesson learned was to procure the commercial modules at the early stages of development and test all the functional modes during the qualification phase. Moreover, designing an in house subsystem gives more flexibility in interfacing and testing.

## 5.3. In-orbit performance of OBDH, TT&C and GPS subsystems

The OBC-1 branch that was enabled at satellite deployment had reset itself after around a month after launch. The cause was initially perceived as single event upset due to radiation in South Atlantic Anomaly, but the problem was later found to be actually caused by a software bug in the command line. The reboots due to software bugs, radiation and EPS reset etc. plotted in relation to proton fluxes, are given in Fig. 22 [40]. During first five months after launch, a total of 38 boot events occurred. A boot event may have one or more boots, with the group having a likely common cause. A further detailed analysis on the boot events can be read in [40]. The satellite

<!-- PDF_PAGE: 26 -->


![figure_024.png](figure_024.png)



<div align="center">

Figure 21: Gyroscope data from July 2017 to November 2019.

</div>

suffered from instability in EPS, resulting in several resets in EPS and the arbiter. A Coronal Mass Ejection (CME) occurred in early September 2017, providing an excellent opportunity for RADMON testing [41]. The satellite was quickly retasked to collect as much data as possible with RADMON. A precious RADMON set of data collection was also interrupted during a CME due to OBC reboots. A few unexplained boot events of the OBC, which were resolved without involvement of the arbiter, occurred during the CME event. It is suspected that these may be related to either radiation or EPS reset.

Immediately after the launch, multiple objects launched on the same rocket as Aalto-1 had similar Two Line Element (TLE), and it was unclear which TLE set belonged to Aalto-1. The GPS subsystem was one of the first instruments successfully operated after contacting the satellite, and navigation solutions provided by the receiver allowed determining the correct TLE set. The determined identity was also communicated to the TLE data provider [42].

It has been observed that the TLE accuracy has been sufficient for most routine operations, and the use of GPS has been less frequent than expected.

<!-- PDF_PAGE: 27 -->


![figure_025.png](figure_025.png)



<div align="center">

Figure 22: OBC reboot events during July-Nov 2017 [40]

</div>

A sub-optimal GPS antenna placement (resulting from a compromise with solar panel placement) and satellite tumbling have caused delays in obtaining the first fix after powering the receiver.

The commissioning of the UHF transceiver was successful since the first contact with the CubeSat was established during first pass over the ground station. The commissioning phase was met with many challenges which have been briefly detailed in [19]. From the telemetry logs, a radio interference in the Northern direction, close to the horizon, was noted at around 437.22 MHz. Similar kind of interference around the 437.0-437.4 MHz was measured by the UWE-3 CubeSat mission though the source of interference has not been confirmed [43]. The S-band transmitter has not been successfully commissioned despite multiple attempts in July 2017 and July 2018.

<!-- PDF_PAGE: 28 -->

## 6. Discussion and conclusions

Although the mission was a partial success in terms of executing the experiments, the important lessons learned during this mission have been applied in the design of next variants of payloads and platforms. The RADMON instrument was successful in commissioning and measurement phases. Its heritage has been used to design a more complex Particle Telescope (PATE) payload for the upcoming FORESAIL-1 mission [44]. The EPB tether could not be deployed due to a failure in tether deployment hardware. The lessons learned have been taken into consideration in development of the plasma brake for upcoming FORESAIL-1 and ESTCube-2 missions [45]. The AaSI was the first nanosatellite-compatible hyper-spectral imager to be flown in space. Aalto-1 project successfully demonstrated the expertise of VTT in both visible and hyper-spectral miniature imager designs. The technology has many potential future applications to serve CubeSat and/or scientific industry/community. Since Aalto-1, VTT's hyper-spectral imagers have been developed for Reaktor Hello World, PICASSO, Hera and Comet Interceptor missions. The platform has provided successful in-orbit demonstration, although some subsystems lacked the desired performance. An important lesson learned was to perform a rigorous test campaign while integrating the commercial and in-house built subsystems.

## Acknowledgements

The RADMON team thanks P.-O. Eriksson and S. Johansson at the Accelerator Laboratory, Abo Akademi University, for operating the cyclotron. Computations necessary for the presented modeling were conducted on the Pleione cluster at the University of Turku.

Aalto University and its Multidisciplinary Institute of Digitalisation and Energy are thanked for Aalto-1 project funding, as are Aalto University, Nokia, SSF, the University of Turku and RUAG Space for supporting the launch of Aalto-1.

## References

[1] A. Ali, H. Ali, J. Tong, M. R. Mughal, S. U. Rehman, Modular Design and Thermal Modeling Techniques for the Power Distribution Module (PDM) of a Micro Satellite, IEEE Access 8 (2020) 160723-160737.

<!-- PDF_PAGE: 29 -->

[2] M. Mughal, Student research highlight smart panel bodies for modular small satellites, IEEE Aerospace and Electronic Systems Magazine 29 (2014) 38-41.

[3] A. Ali, S. A. Khan, M. Usman Khan, H. Ali, M. Rizwan Mughal, J. Praks, Design of modular power management and attitude control subsystems for a microsatellite, International Journal of Aerospace Engineering (2018).

[4] A. Ali, M. R. Mughal, H. J. Ali, M. Leonardo, Innovative electric power supply system for nano-satellites, in: 64rd International Astronautical Congress, Beijing, China, pp. 1-7.

[5] Z. Mukhtar, A. Ali, M. R. Mughal, L. M. Reyneri, Design and comparison of different shapes embedded magnetorquers for cubesat standard nanosatellites, in: 2016 International Conference on Computing, Electronic and Electrical Engineering (ICE Cube), pp. 175-180.

[6] M. R. Mughal, H. Ali, A. Ali, J. Praks, L. M. Reyneri, Optimized design and thermal analysis of printed magnetorquer for attitude control of reconfigurable nanosatellites, IEEE Transactions on Aerospace and Electronic Systems (2019) 1-1.

[7] M. R. Mughal, A. Ali, J. Praks, L. M. Reyneri, Intra-spacecraft optical communication solutions using discrete transceiver, International Journal of Satellite Communications and Networking 37 (2019) 588-600.

[8] A. Ali, M. R. Mughal, H. Ali, L. Reyneri, Innovative power management, attitude determination and control tile for cubesat standard nanosatellites, Acta Astronautica 96 (2014) 116-127.

[9] M. R. Mughal, A. Ali, L. M. Reyneri, Plug-and-play design approach to smart harness for modular small satellites, Acta Astronautica 94 (2014) 754-764.

[10] J. Bouwmeester, J. Guo, Survey of worldwide pico- and nanosatellite missions, distributions and subsystem technology, Acta Astronautica (2010).

[11] J. Crusan, C. Galica, NASA's CubeSat Launch Initiative: Enabling broad access to space, Acta Astronautica (2019).

<!-- PDF_PAGE: 30 -->

[12] A. Poghosyan, A. Golkar, CubeSat evolution: Analyzing CubeSat capabilities for conducting science missions, 2017.

[13] M. E. Seyedabadi, M. Falanga, M. Azam, N. Baresi, R. Fleron, V. Jantarachote, v. A. Juarez Ortiz, J. J. Julca Yaya, M. Langer, S. Manuthasna, N. Martinod, M. R. Mughal, M. Noman, J. Park, A. Pimnoo, J. Praks, L. Reyneri, A. Sanna, T. Sisman, J. Some, T. Ulambayar, Y. Xiaozhou, D. Xiaolong, L. Baldis, Science Missions Using CubeSats, Chinese Journal of Space Science 40 (2020) 443.

[14] N. Frischauf, R. Horn, T. Kauerhoff, M. Wittig, I. Baumann, E. Pellander, O. Koudelka, NewSpace: New Business Models at the Interface of Space and Digital Economy: Chances in an Interconnected World, New Space (2018).

[15] G. Peters, Utilizing commercial best practices for success in NewSpace, Microwave Journal (2015).

[16] S. Tkatchova, Emerging Space Markets, 2018.

[17] D. Salt, NewSpace-delivering onthedream, Acta Astronautica (2013).

[18] T. H. Zurbuchen, B. Lal, Achieving science with cubesats: Thinking inside the box, in: Proceedings of the International Astronautical Congress, IAC, pp. 9-9.

[19] J. Praks, M. R. Mughal, et. al., Aalto-1, multi-payload cubesat: design, integration and launch, Acta Astronautica (2020 (submitted for publication)).

[20] J. Praks, P. Niemelä, A. Näsilä, A. Kestilä, N. Jovanovic, B. A. Riwanto, T. Tikka, H. Leppinen, R. Vainio, P. Janhunen, Miniature Spectral Imager in-Orbit Demonstration Results from Aalto-1 Nanosatellite Mission, IGARSS 2018 - 2018 IEEE International Geoscience and Remote Sensing Symposium (2018) 1986-1989.

[21] J. Gieseler, P. Oleynik, H. Hietala, R. Vainio, H.-P. Hedman, J. Peltonen, A. Punkkinen, R. Punkkinen, T. Santti, E. Haeggström, J. Praks, P. Niemelä, B. Riwanto, N. Jovanovic, M. R. Mughal, Radiation Monitor RADMON aboard Aalto-1 CubeSat: First results, Advances in Space Research 66(1) (2020) 52-65.

<!-- PDF_PAGE: 31 -->

[22] P. Oleynik, R. Vainio, A. Punkkinen, O. Dudnik, J. Gieseler, H. Hedman, H. Hietala, E. Haeggström, P. Niemelä, J. Peltonen, J. Praks, R. Punkkinen, T. Säntti, E. Valtonen, Calibration of RADMON Radiation Monitor Onboard Aalto-1 CubeSat, Advances in Space Research 66(1) (2020) 42-51.

[23] P. Janhunen, Simulation study of the plasma-brake effect, Ann. Geophys. 32 (2014) 1207-1216.

[24] O. Khurshid, T. Tikka, J. Praks, M. Hallikainen, Accommodating the plasma brake experiment on-board the Aalto-1 satellite, Proc. Estonian Acad. Sci. 63(2S) (2014) 258-266.

[25] I. Iakubivskyi, P. Janhunen, J. Praks, V. Allik, K. Bussov, B. Clayhills, J. Dalbins, T. Eenmäe, H. Ehrpais, J. Envall, S. Haslam, E. Ilbis, N. Jovanovic, E. Kilpua, J. Kivastik, J. Laks, P. Laufer, M. Merisalu, M. Meskanen, R. Märk, A. Nath, P. Niemelä, M. Noorma, M. R. Mughal, S. Nyman, M. Pajusalu, M. Palmroth, A. S. Paul, T. Peltola, M. Plans, J. Polkko, Q. S. Islam, A. Reinart, B. Riwanto, J. Sate, I. Sünter, M. Tajmar, E. Tanskanen, H. Teras, P. Toivanen, R. Vainio, M. Väänänen, A. Slavinskis, Coulomb drag propulsion experiments of ESTCube-2 and FORESAIL-1, Acta Astronautica (2019).

[26] S. Lätt, A. Slavinskis, E. Ilbis, U. Kvell, K. Voormansik, E. Kulu, M. Pajusalu, H. Kuuste, I. Sünter, T. Eenmäe, K. Laizans, K. Zalite, R. Vendt, J. Piepenbrock, I. Ansko, A. Leitu, A. Vahter, A. Agu, E. Eilonen, E. Soolo, H. Ehrpais, H. Lillmaa, I. Mahhonin, J. Mõttus, J. Viru, J. Kalde, J. Šubitidze, J. Mucenieks, J. Šate, J. Kütt, J. Poľevskis, J. Laks, K. Kivistik, K.-L. Kusmin, K.-G. Kruus, K. Tarbe, K. Tuude, K. Kalniqa, L. Joost, M. Lõoke, M. Järve, M. Vellak, M. Neerot, M. Valgur, M. Pelakauskas, M. Averin, M. Mikkor, M. Veske, O. Scheler, P. Liias, P. Laes, R. Rantsus, R. Soosaar, R. Reinumägi, R. Valner, S. Kurvits, S.-E. Mändmaa, T. Ilves, T. Peet, T. Ani, T. Tilk, T. H. C. Tamm, T. Scheffler, T. Vahter, T. Uiboupin, V. Evard, A. Sisask, L. Kimmel, O. Krömer, R. Rosta, P. Janhunen, J. Envall, P. Toivanen, T. Rauhala, H. Seppänen, J. Ukkonen, E. Haeggström, R. Kurppa, T. Kalvas, O. Tarvainen, J. Kauppinen, A. Nuottajärvi, H. Koivisto, S. Kiprich, A. Obraztsov, V. Allik, A. Reinart, M. Noorma, ESTCube-1

<!-- PDF_PAGE: 32 -->

nanosatellite for electric solar wind sail in-orbit technology demonstration, Proc. Estonian Acad. Sci. 63(2S) (2014) 200-209.

[27] J. Envall, P. Janhunen, P. Toivanen, M. Pajusalu, E. Ilbis, J. Kalde, M. Averin, H. Kuuste, K. Laizans, V. Allik, T. Rauhala, H. Seppänen, S. Kiprich, J. Ukkonen, E. Haeggström, T. Kalvas, O. Tarvainen, J. Kauppinen, A. Nuottajärvi, H. Koivisto, E-sail test payload of ESTCube-1 nanosatellite, Proc. Estonian Acad. Sci. 63(2S) (2014) 210221.

[28] A. Slavinskis, M. Pajusalu, H. Kuuste, E. Ilbis, T. Eenmäe, I. Sünter, K. Laizans, H. Ehrpais, P. Liias, E. Kulu, et al., ESTCube-1 in-orbit experience and lessons learned, IEEE Aerospace and Electronic Systems Magazine 30 (2015) 12-22.

[29] J. Peltonen, H. Hedman, A. Ilmanen, M. Lindroos, M. Määttänen, J. Pesonen, R. Punkkinen, A. Punkkinen, R. Vainio, E. Valtonen, T. Santti, J. Pentikäinen, E. Haeggström, Electronics for the radmon instrument on the aalto-1 student satellite, in: 10th European Workshop on Microelectronics Education (EWME), pp. 161-166.

[30] C. E. McIlwain, Coordinates for Mapping the Distribution of Magnetically Trapped Particles, Journal of Geophysical Research 66 (1961) 3681-3691.

[31] W. D. Gonzalez, J. A. Joselyn, Y. Kamide, H. W. Kroehl, G. Rostoker, B. T. Tsurutani, V. M. Vasyliunas, What is a geomagnetic storm?, Journal of Geophysical Research: Space Physics 99 (1994) 5771-5792.

[32] T. Pulkkinen, Space Weather: Terrestrial Perspective, Living Reviews in Solar Physics 4 (2007) 1.

[33] S. Agostinelli, J. Allison, K. Amako, J. Apostolakis, H. Araujo, P. Arce, M. Asai, D. Axen, S. Banerjee, G. Barrand, F. Behner, L. Bellagamba, J. Boudreau, L. Broglia, A. Brunengo, H. Burkhardt, S. Chauvie, J. Chuma, R. Chytracek, G. Cooperman, G. Cosmo, P. Degtyarenko, A. Dell'Acqua, G. Depaola, D. Dietrich, R. Enami, A. Feliciello, C. Ferguson, H. Fesefeldt, G. Folger, F. Foppiano, A. Forti, S. Garelli, S. Giani, R. Giannitrapani, D. Gibin, J. G. Cadenas, I. González, G. G. Abril, G. Greeniaus, W. Greiner, V. Grichine, A. Grossheim, S. Guatelli,

<!-- PDF_PAGE: 33 -->

P. Gumplinger, R. Hamatsu, K. Hashimoto, H. Hasui, A. Heikkinen, A. Howard, V. Ivanchenko, A. Johnson, F. Jones, J. Kallenbach, N. Kanaya, M. Kawabata, Y. Kawabata, M. Kawaguti, S. Kelner, P. Kent, A. Kimura, T. Kodama, R. Kokoulin, M. Kossov, H. Kurashige, E. Lamanna, T. Lampen, V. Lara, V. Lefebure, F. Lei, M. Liendl, W. Lockman, F. Longo, S. Magni, M. Maire, E. Medernach, K. Minamimoto, P. M. de Freitas, Y. Morita, K. Murakami, M. Nagamatu, R. Nartallo, P. Nieminen, T. Nishimura, K. Ohtsubo, M. Okamura, S. O'Neale, Y. Oohata, K. Paech, J. Perl, A. Pfeiffer, M. Pia, F. Ranjard, A. Rybin, S. Sadilov, E. D. Salvo, G. Santin, T. Sasaki, N. Savvas, Y. Sawada, S. Scherer, S. Sei, V. Sirotenko, D. Smith, N. Starkov, H. Stoecker, J. Sulkimo, M. Takahata, S. Tanaka, E. Tcherniaev, E. S. Tehrani, M. Tropeano, P. Truscott, H. Uno, L. Urban, P. Urban, M. Verderi, A. Walkden, W. Wander, H. Weber, J. Wellisch, T. Wenaus, D. Williams, D. Wright, T. Yamada, H. Yoshida, D. Zschiesche, Geant4-a simulation toolkit, Nuclear Instruments and Methods in Physics Research Section A: Accelerators, Spectrometers, Detectors and Associated Equipment 506 (2003) 250-303.

[34] J. Allison, K. Amako, J. Apostolakis, H. Araujo, P. Arce Dubois, M. Asai, G. Barrand, R. Capra, S. Chauvie, R. Chytracek, G. A. P. Cirrone, G. Cooperman, G. Cosmo, G. Cuttone, G. G. Daquino, M. Donszelmann, M. Dressel, G. Folger, F. Foppiano, J. Generowicz, V. Grichine, S. Guatelli, P. Gumplinger, A. Heikkinen, I. Hrivnacova, A. Howard, S. Incerti, V. Ivanchenko, T. Johnson, F. Jones, T. Koi, R. Kokoulin, M. Kossov, H. Kurashige, V. Lara, S. Larsson, F. Lei, O. Link, F. Longo, M. Maire, A. Mantero, B. Mascialino, I. McLaren, P. Mendez Lorenzo, K. Minamimoto, K. Murakami, P. Nieminen, L. Pandola, S. Parlati, L. Peralta, J. Perl, A. Pfeiffer, M. G. Pia, A. Ribon, P. Rodrigues, G. Russo, S. Sadilov, G. Santin, T. Sasaki, D. Smith, N. Starkov, S. Tanaka, E. Tcherniaev, B. Tome, A. Trindade, P. Truscott, L. Urban, M. Verderi, A. Walkden, J. P. Wellisch, D. C. Williams, D. Wright, H. Yoshida, Geant4 developments and applications, IEEE Transactions on Nuclear Science 53 (2006) 270-278.

[35] J. Hemmo, Electrical Power Systems for Finnish Nanosatellites, Master's thesis, Aalto University, Espoo, Finland, 2013.

[36] T. Tikka, O. Khurshid, N. Jovanovic, H. Leppinen, A. Kestilä, J. Praks,

<!-- PDF_PAGE: 34 -->

Aalto-1 Nanosatellite Attitude Determination and Control System Endto-End Testing, in: 6th European CubeSat Symposium, p. 78.

[37] H. Leppinen, Integration of a GPS subsystem into the Aalto-1 nanosatellite, Master's thesis, Aalto University, Espoo, Finland, 2013.

[38] M. Lankinen, Design and Testing of Antenna Deployment System for Aalto-1 Satellite, Master's thesis, Aalto University, Espoo, Finland, 2015.

[39] J. Jussila, S. Ben Cheikh, J. Holopainen, M. Lankinen, A. Kestilä, J. Praks, M. Hallikainen, Design of high data rate, low power and efficient S-band transmitter for Aalto-1 nanosatellite mission, in: Proceedings of the 2nd IAA Conference on University Satellites Missions and CubeSat Workshop, pp. 811-829.

[40] H. Leppinen, P. Niemelä, N. Silva, H. Sanmark, H. Forén, A. Yanes, R. Modrzewski, A. Kestilä, J. Praks, Developing a Linux-based nanosatellite on-board computer: flight results from the Aalto-1 mission, IEEE Aerospace and Electronic Systems Magazine 34 (2019).

[41] R. Vainio, A. Punkkinen, J. Peltonen, H.-P. Hedman, E. Haeggström, P. Niemelä, J. Praks, R. Punkkinen, T. Säntti, E. Valtonen, Measurements of Energetic Electrons and Protons aboard a CubeSat on Low Earth Orbit: Aalto-1 / RADMON, in: T. Hynninen, T. Kuusela (Eds.), Physics Days 2018 21.3- 23.3.2018 Turku, Finland: FP2018 Proceedings, p. 62.

[42] H. Leppinen, Enabling technologies and practices for low-cost nanosatellite missions, Doctoral dissertation, Aalto University, Espoo, Finland, 2018.

[43] S. Busch, P. Bangert, S. Dombrovski, K. Schilling, UWE-3, In-Orbit Performance and Lessons Learned of a Modular and Flexible Satellite Bus for Future Pico-Satellite Formations, Acta Astronautica (2015).

[44] P. Oleynik, R. Vainio, H.-P. Hedman, A. Punkkinen, R. Punkkinen, L. Salomaa, T. Santti, J. Tuominen, P. Virtanen, A. Bosser, P. Janhunen, E. Kilpua, M. Palmroth, J. Praks, A. Slavinskis, S. R. Kakakhel, J. Peltonen, J. Plosila, J. Tammi, H. Tenhunen, T. Westerlund, Particle

<!-- PDF_PAGE: 35 -->

Telescope aboard FORESAIL-1: simulated performance, Advances in Space Research 66(1) (2020) 29-41.

[45] I. Iakubivskyi, P. Janhunen, J. Praks, V. Allik, K. Bussov, B. Clayhills, J. Dalbins, T. Eenmäe, H. Ehrpais, J. Envall, S. Haslam, E. Ilbis, N. Jovanovic, E. Kilpua, J. Kivastik, J. Laks, P. Laufer, M. Merisalu, M. Meskanen, R. Märk, A. Nath, P. Niemelä, M. Noorma, M. R. Mughal, S. Nyman, M. Pajusalu, M. Palmroth, A. S. Paul, T. Peltola, M. Plans, J. Polkko, Q. S. Islam, A. Reinart, B. Riwanto, J. Sate, I. Sünter, M. Tajmar, E. Tanskanen, H. Teras, P. Toivanen, R. Vainio, M. Väänänen, A. Slavinskis, Coulomb drag propulsion experiments of ESTCube-2 and FORESAIL-1, Acta Astronautica (2020).