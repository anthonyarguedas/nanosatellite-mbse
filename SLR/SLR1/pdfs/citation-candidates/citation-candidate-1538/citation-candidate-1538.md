---
source: null
title: "citation-candidate-1538"
page_count: 10
converted_at: "2026-09-08T15:24:17Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# 6U CubeSat commercial applications

</div>

S. R. Tsitas

s.r.tsitas@alumni2008.cranfield.ac.uk

J. Kingston

j.kingston@cranfield.ac.uk

Cranfield Space Research Centre, Aerospace Engineering Department Cranfield University, UK

## ABSTRACT

Recent work by Tsitas and Kingston $ ^{(1)} $ has demonstrated that an 8kg 6U CubeSat can be designed to perform Earth observation missions equivalent to those of 50-150kg microsatellites. Their design is reviewed and its commercial potential is compared to the 156kg RapidEye spacecraft. Three other commercial applications of this design are described. These are: a standard spacecraft for space scientists and astronomers; the spacecraft component of an N nation 5 spectral band disaster monitoring constellation and a night imaging satellite. Nanosatellites should now be considered for commercial missions previously thought to require microsatellites.

## NOMENCLATURE

<table border="1"><tr><td>$c$</td><td>speed of light</td></tr><tr><td>D</td><td>imager aperture diameter</td></tr><tr><td>h</td><td>Planck&#x27;s constant</td></tr><tr><td>H</td><td>altitude</td></tr><tr><td>$\lambda$</td><td>wavelength of light</td></tr><tr><td>L</td><td>ground sample distance</td></tr><tr><td>$L_{rad}$</td><td>surface spectral radiance</td></tr><tr><td>$N_{electrons}$</td><td>number of electrons read out from a column of pixels</td></tr><tr><td>$N_{TDI}$</td><td>number of time delay and integration pixels</td></tr></table>

<div align="center">

Paper No. 3526. Manuscript received 15 January 2010, revised version received 9 June 2011, second revision 11 July 2011, accepted 13 July 2011.

</div>

<!-- PDF_PAGE: 2 -->

<table border="1"><tr><td>$\varphi$</td><td>complement of spacecraft elevation angle</td></tr><tr><td>$QE$</td><td>CCD quantum efficiency</td></tr><tr><td>$t_{acquisition}$</td><td>time required for signal acquisition after changing transmitter speeds</td></tr><tr><td>$T_{atm}$</td><td>fraction of light transmitted by the atmosphere</td></tr><tr><td>$T_{filter}$</td><td>fraction of light transmitted by the transmission filter</td></tr><tr><td>$T_{scope}$</td><td>fraction of light transmitted by the telescope</td></tr><tr><td>$v_{g}$</td><td>magnitude of the velocity of the spacecraft projected on the ground</td></tr></table>

## 1.0 INTRODUCTION

Tsitas and Kingston $ ^{(1)} $ have detailed the system design of an 8kg 6U CubeSat capable of performing Earth Observation missions equivalent to those of current 50-150kg microsatellites. This paper explores commercial applications for this newfound capability. This paper is also intended to stimulate discussion of further applications for the 6U CubeSat, and promote another step-change in miniaturization of spacecraft with real scientific and commercial capabilities.

## 2.0 REVIEW OF THE 6U CUBESAT DESIGN

The 6U CubeSat design of Tsitas and Kingston $ ^{(1)} $ has dimensions of approximately 30cm x 20cm x 10cm and a weight of 8kg including a margin of 1.22kg. The design includes a fibre optic gyroscope (FOG) to meet the requirements for pointing stability which follow from the use of time delay integration (TDI) by the imager. TDI is used to achieve the signal to noise ratio (SNR) of a larger aperture than the 89mm aperture specified for the design. A compact star tracker is specified for attitude determination when not imaging and to provide lost in space capability. Magnetometers are specified for initial attitude acquisition following deployment, and to measure magnetic field strength for calculating magnetorquer use. Magnetorquers embedded in body fixed solar panels are specified to desaturate three orthogonal reaction wheels which are used for attitude control.

A Sun synchronous orbit at an altitude of 600km is specified for the design which enables imaging with a 6.5m ground sample distance (GSD), an optical MTF (on axis) of >59% at half Nyquist and >35% at Nyquist and a 26km swath. 12 bit digitisation is specified and it is shown that a SNR of 120-200:one in five spectral bands; blue, green, red, red edge and near infrared can be achieved. The design specifies the use of DVB-S2 encoding for the data transmitted to the ground, which results in significant coding gain. Through the use of DVB-S2 encoding and three transmitter speeds, 1GB of data can be downlinked during a ground station pass to a 3.7m S band ground station.

This initial paper stimulated discussion, a result of which certain refinements have been made to the design which are now described.

The conclusion by Tsitas and Kingston $ ^{(1)} $ that the lifetime of the CubeSat in a 600km orbit could exceed 25 years is supported by results presented in a 2009 draft of the ISO Standard 27852 for determining orbit lifetime $ ^{(2)} $ . Using a drag coefficient of 2.2 the 8kg 6U CubeSat ballistic coefficient is $ 101\mathrm{cm}^{2}\mathrm{kg}^{-1} $ . Figure B-4 of the draft standard indicates that the orbit lifetime of a satellite with this ballistic coefficient in a polar orbit can be greater than 25 years at 600km initial altitude.

Tsitas and Kingston $ ^{(1)} $ propose transmitting with three different speeds from elevation angles of $ 1 0^{\circ}-3 0^{\circ} $ $ 3 0^{\circ}-6 0^{\circ} $ and $ 6 0^{\circ}-9 0^{\circ} $ respectively to take advantage of the decreasing space loss as the spacecraft moves closer to the ground station. Compared to transmitting with a single speed from

<!-- PDF_PAGE: 3 -->

<div align="center">

Table 1

</div>

<div align="center">

Relative amounts of data that can be downlinked using one, two and three different transmitter speeds during a ground station pass. Transmitter speeds are fixed from each elevation angle

</div>

<table border="1"><tr><td>Transmitter speeds</td><td>Relative amount of data downlinked</td></tr><tr><td>3 speed(10°,30°,60°),tacquisition=0</td><td>1</td></tr><tr><td>3 speed(10°,30°,60°),tacquisition=7.5s</td><td>0.96</td></tr><tr><td>3 speed(10°,30°,60°),tacquisition=15s</td><td>0.91</td></tr><tr><td>3 speed(10°,30°,60°),tacquisition=30s</td><td>0.83</td></tr><tr><td>2 speed(10°,45°),tacquisition=60s</td><td>0.73</td></tr><tr><td>Single speed(40°)</td><td>0.58</td></tr><tr><td>Single speed(10°)</td><td>0.34</td></tr></table>

<div align="center">

$ t_{acquisition} $ is the time required for signal acquisition after changing transmitter speeds.

</div>

an elevation angle of $ 1 0^{\circ} $ this increases the amount of data which can be downlinked by a factor of 2.9. However this assumes that signal acquisition after changing transmitter speeds is instantaneous. Table 1 lists the relative amount of data that can be downlinked using one, two and three different transmitter speeds with different values for the time required for signal acquisition $ \left(t_{\mathrm{acquisition}}\right) $ after changing transmitter speeds.

As $ t_{acquisition} $ approaches one minute more data can be downlinked using two transmitter speeds instead of three. If a single transmitter speed is used significantly more data ( 70% ) can be downlinked by delaying downlink until the spacecraft has reached an elevation angle of $ 40^{\circ} $ relative to the ground station. The reduced time available for downlink is more than compensated for by the higher transmitter speeds possible due to the lower space loss compared to an elevation angle of $ 10^{\circ}. $

Tsitas and Kingston $ ^{(1)} $ derive the average data downlink rate by dividing the total data downlinked by the time required for the ground station pass. However the ground station pass time of 9.58 minutes used by Tsitas and Kingston $ ^{(1)} $ is for an altitude of 700km $ (10^{\circ} $ elevation). For an altitude of 600km the ground station pass time is 8.50 minutes $ (10^{\circ} $ elevation). This increases the average data downlink rate from the 14Mbps reported by Tsitas and Kingston $ ^{(1)} $ to 15.7Mbps. The total amount of data downlinked during a ground station pass is unchanged at 1GB assuming no delay in signal reacquisition after changing transmitter speeds.

The disturbance torques acting on the 6U CubeSat are quantified in Table 5 of Tsitas and Kingston $ ^{(1)} $ . The residual dipole moment of a CubeSat may approach $ 0.05 \mathrm{~A m}^{2} $ , towards the upper end of the range considered by Tsitas and Kingston $ ^{(1)} $ . Coupling of the residual dipole moment with the Earth's magnetic field is therefore likely to be the most significant disturbance to the 6U CubeSat's attitude. We do not anticipate any significant effects from coupling of the reaction wheel motor magnetic moment with the Earth magnetic field at low wheel speeds, as one would aim to avoid the near zero wheel speed regime (defined as wheel rotation rates comparable to the orbit rate, i.e. $ \sim1/90 \mathrm{rpm} $ ), certainly during imaging operations.

A 20Wh battery is specified in the design of the 6U CubeSat by Tsitas and Kingston $ ^{(1)} $ . The depth of discharge is 24.6% which may be adequate but doubling the battery capacity to 40Wh will help ensure a five year mission lifetime can be achieved. If the heater threshold temperature is lowered the batteries will be deleteriously affected by lower temperatures during passage through the Earth's shadow. However, the depth of discharge will also be reduced. A trade-off can be performed to determine the optimum heater threshold temperature which maximises battery life.

<!-- PDF_PAGE: 4 -->

The mass of the solar arrays with embedded magnetorquers which are located on one $ \sim 3 0 \mathrm{c m} $ x 20cm face of the 6U CubeSat is given in Table 8 of Tsitas and Kingston $ ^{(1)} $ as 297g. The mass range of such arrays is estimated to be 50-70g per 10cm x 10cm area. Therefore the total mass may range from 300-500g, and an additional 200g should be allocated to the solar panel mass in Table 8. This reduces the margin to 1kg.

Equation (11) in Tsitas and Kingston $ ^{(1)} $ gives the expression for the signal to noise ratio of the imager. Due to a typographical error the first term in the denominator is given as the square of the number of electrons; it should be the square of the shot noise. Since the shot noise is proportional to the square root of the number of electrons, this term is equal to the number of electrons which is correctly shown in Equation (12). The results for the SNR calculations presented in Table 4 of Tsitas and Kingston $ ^{(1)} $ are unaffected since Equation (12) was used in their calculation.

Tsitas and Kingston $ ^{(1)} $ give the pointing stability requirement to be that the pointing remain within half a pixel width 99.7% of the time during TDI for a pixel. The half pixel width is given as 1.18 arcsec in Section 5.1 and 5.4 of Tsitas and Kingston $ ^{(1)} $ , but it should be 1.12 arcsec. However the conclusions of the paper are unaffected because the $ 3\sigma $ pointing error is 1.09 arcsec for the fibre optic gyroscope specified in the paper. Therefore the requirement that the pointing remain within 1.12 arcsec $ (3\sigma) $ during the TDI integration period may still be met with suitable control loop design provided microvibrations from the RWA are properly characterised as originally concluded.

## 3.0 COMMERCIAL POTENTIAL OF THE 6U CUBESAT COMPARED TO RAPIDEYE

The cost effectiveness of the 6U CubeSat design can be compared with that of the RapidEye spacecraft by comparing the cost of the launched spacecraft per bit of data downlinked during the mission lifetime. Assuming one ground station pass per orbit and 15 seconds for signal acquisition by the ground station when the transmitter speed is changed the 6U CubeSat design proposed by Tsitas and Kingston $ ^{(1)} $ could downlink 0.9GB of data per orbit. The RapidEye spacecraft can downlink data at a rate of 80Mbps $ ^{(3)} $ which corresponds to approximately 5.3GB of data downlinked during a ground station pass above an elevation angle of $ 10^{\circ} $ . The RapidEye spacecraft mission lifetime is seven years during which the spacecraft can downlink 6.9 times as much data as the 6U CubeSat over a six year mission lifetime.

The RapidEye spacecraft cost $7m each $ ^{(4)} $ (all prices USD unless otherwise noted) adjusted for inflation, and all five RapidEye spacecraft were launched together on a single Dnepr-1 rocket with an estimated launch cost of $ 10m $ ^{(5)} $ . Therefore the price of a single RapidEye spacecraft including launch costs is approximately $ 9m. The cost of the 6U CubeSat can be estimated from 2001 estimates $ ^{(6)} $ of spacecraft bus cost for modern US Department of Defense small satellites of $ 140,000/kg adjusted for inflation. Costs for launch to 185km LEO using the Falcon 1e rocket are $ 10.9m for a payload of $ 1010kg $ ^{(7)} $ ($ 10,792/kg ). Assuming the cost of launching a 6U CubeSat to 600km LEO is $ 190,000 $ ^{(2)} $ ( $ 23,750/kg ), the total cost of the 6U CubeSat is $ 1.3m including launch, which is 1/6.9 that of a RapidEye spacecraft. Therefore the cost per bit of data downlinked during the missions of a 6U CubeSat and a RapidEye spacecraft are the same assuming a six year mission lifetime, $ 140,000/kg bus cost and $ 190,000 launch cost for the 6U CubeSat.

A constellation of 35 6U CubeSats would have approximately the same launched cost as the fivespacecraft RapidEye constellation ($45m) and be able to downlink approximately the same amount of data during a six year mission lifetime. In fact the 6U CubeSat bus cost would be

<!-- PDF_PAGE: 5 -->

expected to decrease for the production of such a large number of spacecraft. With a similar cost per bit of data downlinked the 6U CubeSat constellation would be competitive with the Rapid-Eye constellation if the data downlinked by the two constellations were of equal value.

In fact the data downlinked by the 6U CubeSat constellation would be of much higher temporal resolution, since the constellation could contain seven planes of five spacecraft each, compared with a single plane of five spacecraft for the RapidEye constellation. Roughly speaking the revisit time would be 1/7 that of the RapidEye constellation, reducing this from one day to 3.5 hours. This greatly improves the chances of cloud free imaging and the high temporal resolution may be considered by the market to be of superior value. Given the identical ground sample distance (GSD), digitisation and spectral bands this suggests that the commercial potential of a 6U CubeSat constellation compares favourably with the RapidEye constellation.

## 4.0 STANDARD SPACECRAFT FOR SPACE SCIENCE AND ASTRONOMY

The requirements for commercial Earth observation result in a spacecraft with microsatellite class attitude control and data downlink rate and a payload bay large enough for a commercially useful imaging system $ ^{(1)} $ . These capabilities also enable a range of missions in astronomy and space science. One way to commercialise this capability is to create a standard spacecraft based on this design. Small size and mass production should result in a cost low enough that scientists could purchase spacecraft (including launch) with modest science grants to fly an instrument they design into space.

This could be a commercial initiative by a satellite manufacturer, or a space agency could contract a satellite manufacturer to carry out the detailed design and testing of the system design described by Tsitas and Kingston $ ^{(1)} $ . In this case a reference standard for a 6U CubeSat suitable for a range of missions in astronomy and space science would be created. Any satellite manufacturer could then sell spacecraft built to this standard to scientists.

The US National Science Foundation began annual solicitations for the 'CubeSat-based Science Missions for Space Weather and Atmospheric Research' programme in 2008 $ ^{ (8)} $ . Up to $ 900,000 in total programme funding is available from this program every year. This demonstrates that the concept of national science agencies funding CubeSat based science missions has precedent. However the science that can be done within the NSF program is limited by the functionality of 1U-3U CubeSats which define the current CubeSat standard. Investigators also have to create their own CubeSats. This limits the current NSF program to scientists with practical space systems engineering experience. Collaboration between scientists lacking this experience with space engineers as required by the NASA Discovery program is problematic considering the low funding levels of the NSF program. It is unreasonable to expect that the reliability of a spacecraft built in this way will equal that of a spacecraft designed, tested and built by a commercial satellite manufacturer.

A standard small spacecraft built by a satellite manufacturer allows space scientists and astronomers to concentrate on instrument design and still have a reliable and relatively low cost way to fly their experiments in space. Aside from CubeSats with the aforementioned drawbacks, space science and astronomy currently lack a low cost and timely way to carry out research in space, preventing the exploration of new ideas in a relatively inexpensive and informal fashion that is the backbone of science.

Traditionally, scientists define requirements and bespoke spacecraft (or customised standard

<!-- PDF_PAGE: 6 -->

spacecraft buses) are built to meet them. In contrast, the proposed standard 6U CubeSat for space science and astronomy has requirements that must be met by scientists wishing to fly their payloads. This is similar to the way standard launchers impose requirements on spacecraft (for example, maximum width and mass). In some cases the spacecraft will be over specified for the mission (for example better pointing stability than required), which usually implies excess cost. On the other hand the use of a standard design promises significant cost reduction through mass production. It also promises increased reliability through flight heritage with each launch of identical (save for payload) spacecraft. Optimised bespoke spacecraft, even those based on a standard bus, do not utilise these advantages to the fullest.

A spacecraft User's Guide (similar to launcher User's Guides) could be produced to define the requirements for payloads to be integrated into the spacecraft. Requirements could include mass, dimensions, electrical interfaces, pointing accuracy/stability, downlink rate and power. With the use of ultracapacitors high power can be delivered to the payload for short periods of time.

The Maxwell BCAP0310 is an ultracapacitor the size of a D cell battery with a mass of 60g and stored energy of $ 0. 3 1 \mathrm {W h}^{(9)} $ . This ultracapacitor can deliver 110.7W for 10s, or 712.5W for 1s, requiring 79s of charging from the solar array. For comparison a Clyde Space 30Wh battery designed for spacecraft use has a mass of 256g and a discharge voltage of 6.2V with a recommended maximum discharge current of $ 1. 8 7 5 \mathrm {A}^{(1 0)} $ $ (1 1. 6 2 5 \mathrm {W} $ power output). If a payload requires power of 600W for 10s this would require 52 batteries for a total mass of 13.3kg. The same power could be delivered by six ultracapacitors with a total mass of 0.36kg. This bank of ultracapacitors would require seven minutes to be charged by the solar array. The operational temperature range of these ultracapacitors is $ - 4 0^{\circ} $ to $ 6 5^{\circ} $ , compared with $ - 1 0^{\circ} $ to $ 5 0^{\circ} $ for the Clyde Space battery.

Ultracapacitors lose only a few percent of their charge after 72 hours, suggesting they might also be used to provide spacecraft energy during eclipses and obviating the need for batteries. However, their low energy density makes this inefficient. For example, the total energy that must be provided to the 6U CubeSat during eclipse is $ 4.91\mathrm{Wh}^{(1)} $ . This would require 16 ultracapacitors for a total mass of 0.96kg, The same energy could be provided by the 30Wh Clyde Space battery with a depth of discharge of 84% and a mass of 0.256kg. Therefore the most efficient arrangement is a combination of batteries and ultracapacitors when high power for a short period of time is required. This approach was used in a design study of a SAR microsatellite based on the CNES MYRIADE bus $ ^{(11)} $ . If high power is required by the payload some part of the payload volume can be used for ultracapacitors. As ultracapacitors have low equivalent series resistance (ESR) the main limitation to the power delivered to the payload will be heat dissipation in the payload during discharge.

It is possible to do useful astronomy in space with small telescopes. Being above the atmosphere ensures any change in the intensity of starlight is due to changes in the stellar output and not scintillation in the atmosphere. Even a 52mm telescope has been used productively in orbit for stellar photometry, although this was by accident and not design. This was a star tracker for the WIRE spacecraft (Wide-Field Infrared Explorer). The main instrument was an infrared telescope, which failed within four days of launch due to loss of the coolant for the infrared detector. The star tracker still worked however and was used to carry out photometry to detect oscillations on $ \alpha $ Ursae Majoris $ ^{12} $

A payload telescope on the standard 6U CubeSat could also be used as a star tracker similar to the MOST microsatellite. MOST uses a 150mm telescope for both stellar photometry and as a star tracker $ ^{ (13)} $ . Magnetometers and sun sensors are used for coarse pointing. A MEMS gyroscope is used for rate information which is combined with a dynamic model of the spacecraft and the star tracker

<!-- PDF_PAGE: 7 -->

attitude information in an Extended Kalman Filter to obtain a high bandwidth attitude estimate $ ^{14)} $ . This allows MOST to carry out stellar photometry observations. NESS uses the MOST telescope but replaces the MEMS gyroscope with a fiber optic gyroscope (FOG) which has lower angular random walk noise for improved attitude estimation $ ^{14)} $ . This helps NESS achieve better pointing accuracy to detect and track Earth approaching asteroids and monitor Earth orbiting satellites. Since an 89mm aperture payload telescope and a FOG are used in the 6U CubeSat design of Tsitas and Kingston $ ^{1)} $ this suggests photometry and asteroid detection could be suitable astronomy missions for the standard 6U CubeSat.

## 5.0 N NATION 5 SPECTRAL BAND DISASTER MONITORING CONSTELLATION

The Disaster Monitoring Constellation (DMC) is a constellation of originally five microsatellites with three spectral bands and mass ranging from 90kg to 130kg built by SSTL $ ^{15} $ . Nigeria, Algeria, Turkey, China and the United Kingdom each bought a satellite and each bought or installed an S-Band ground station. The satellite costs were in the region of $ 7 \mathrm{m} $ per satellite. With five satellites, any point on the Earth can be revisited on a daily basis. The ability to use the DMC in this way is guaranteed when the United Nations declares a disaster area, in which case the charter of the DMC provides for free use of the constellation. At other times, while nations retain 'absolute control over their own assets to meet specific national or commercial needs' there is no chartered requirement for the sharing of assets, although the owners are 'strongly encourage[d] ... to share resources to reap the benefits of operating the spacecraft as a constellation $ ^{16} $ .

Extending this concept it is proposed that the 6U CubeSat design of Tsitas and Kingston $ ^{(1)} $ be used as the spacecraft component of an N nation 5 spectral band disaster monitoring constellation similar to the original five-nation SSTL DMC, but with N>>5 and a GSD of 6.5m. With a much lower spacecraft cost many developing countries could afford to join the N nation disaster monitoring constellation. The 6U CubeSat design images the same five spectral bands used by RapidEye with the same GSD to support agricultural monitoring. This allows the N nation Disaster Monitoring Constellation to be used by member countries for agricultural monitoring to RapidEye standard, extending this capability to many developing countries.

Furthermore, the utility of a satellite constellation increases as the number of satellites in the constellation increases. This is because the revisit time decreases as N increases. A very short time between revisits - potentially continuous coverage for medium resolution (GSD = 6.5 m) multispectral imagery is a capability that has not existed before. Aside from improved disaster monitoring, improved agricultural monitoring (a short time between revisits increases the probability that a cloud free image of a target area can be obtained at a desired time, which may be critical for agricultural planning) and fire detection, it is expected that new applications will emerge to take advantage of this unique capability. In contrast to the charter of the SSTL DMC, provision for guaranteed sharing at all times is proposed for the charter of the N nation 5 spectral band disaster monitoring constellation.

The 6U CubeSat system design described by Tsitas and Kingston $ ^{(1)} $ does not include propulsion, raising the question of how the spacecraft may be separated within an orbital plane if a number are launched in a batch. One solution is that dedicated nanosat launchers may become available, optimised for launching six 1U CubeSats, or a single 6U CubeSat. These launchers may be based on modified sounding rockets or new air launched rockets that take advantage of the emerging commercial suborbital space plane infrastructure. This would remove the need and risk of batch launching.

<!-- PDF_PAGE: 8 -->

## 6.0 NIGHT IMAGING SATELLITE

Images of the Earth at night reveal the extent of human settlements by their artificial lighting. With sufficient spatial and spectral resolution, these allow population density and economic activity to be monitored $ ^{ (17)} $ . This data may be sold to government and non-governmental agencies. So far there have been no satellites dedicated to the task of night imaging, and the highest spatial resolution images are those taken by astronaut D. R. Pettit from the International Space Station $ ^{ (17)} $ .

Elvidge et al $ ^{ (17)} $ describe the requirements for a night imaging satellite they call NightSat. These include: the ability to detect a surface spectral radiance of $ 2\cdot 5\mathrm{x}10^{-8}\mathrm{Wcm}^{-2}\mathrm{sr}^{-1}\mu\mathrm{m}^{-1} $ with a SNR of 10 in the photopic band (0.51 to $ 0.61\mu\mathrm{m} $); a nadir GSD in the 50-100m range and swath of 100km; on board calibration; one or more thermal bands for detecting cloud free areas and contamination by fires; collection of data from a polar low Earth orbit with an overpass time of 8:30 pm to 10:00pm and a repeat cycle of 20 days and geolocation accuracy comparable to Landsat.

Tsitas and Kingston $ ^{(1)} $ model the number of electrons $ N_{electrons} $ read out from a column of $ N_{TDI} $ pixels of a time delay and integration (TDI) CCD at the focal plane of an imaging system compact enough to be carried by a 6U CubeSat. These electrons are created by light collected from a square area of side length L on the Earth's surface (the GSD) in the wavelength interval $ \Delta \lambda $ about a wavelength $ \sim\lambda $ . For an imager of clear aperture D with a TDI CCD of quantum efficiency $ Q_{E} $ and $ N_{TDI} $ TDI stages $ N_{electrons} $ is given by Equation (1):

$$
N _ {e l e c t r o n s} = N _ {T D I} \left(\frac {\pi}{4 \mathrm {h c}}\right) T _ {a t m} T _ {s c o p e} T _ {f i l t e r} Q _ {E} D ^ {2} L _ {r a d} \left(\frac {L ^ {3} \operatorname {C o s} \phi}{H ^ {2} \nu_ {g}}\right) \lambda \Delta \lambda
$$

$ \varphi $ is the angle between the normal to the Earth's surface and the direction to the spacecraft which is at an altitude H. $ T_{scope} $ is the transmission factor of the telescope, $ T_{atm} $ is the transmission factor of the atmosphere and $ T_{filter} $ is the transmission factor of the transmission filter which will be used to separate the light incident upon the focal plane into different wavelengths. $ L_{rad} $ is the surface spectral radiance and $ v_{g} $ is the magnitude of the velocity of the spacecraft projected on the ground. h and c are Planck's constant and the speed of light respectively.

Equation (1) is used to model a night imaging camera that could be carried by a 6U CubeSat. An aperture diameter of 89mm is assumed with a focal length of 101mm, resulting in a compact imager with f/1.1. The short focal length should not require compound optics so a telescope transmission factor of 0.90 is assumed (the fraction of light passed by the camera to its focal plane). The atmosphere transmission factor is assumed to be 0.7, and the filter transmission factor is taken as 0.6. A transmission filter is assumed to be used to provide multispectral imaging ability. For a GSD of 52m, the pixel size from 600km altitude is 8.75 $ \mu $m.

The Fairchild Imaging CCD5061 is a 6,144 pixel TDI CCD with $ 8\cdot 7 5 \mu \mathrm{m} $ pixels and 4,8,16,32, 64,96 or 128 selectable TDI stages $ ^{(18)} $ . With a GSD of 52m and swath width of 100km, 1,923 pixels will be illuminated by the ground image. It is assumed that a backthinned version of the CCD5061 can be obtained with quantum efficiencies similar to the Hamamatsu S10202-08 TDI CCD (the same assumption is made by Tsitas and Kingston $ ^{(1)} $ ). The quantum efficiency of the S10202-08 in the photopic band is shown in Table 1 and used in the calculation of the SNR. The Hamamatsu S10202-08 back-thinned TDI-CCD has 4,160 pixels of $ 1 2 \mu \mathrm{m} $ width and 128 stage TDI $ ^{(19)} $ .

For the CCD5061 the typical readout noise is 40 electrons and the dark signal is typically 374.4 electrons for 64 TDI stages $ ^{(18)} $ . The SNR is therefore given by Equation (2):

$$
S N R = \frac {N _ {e l e c t r o n s}}{\sqrt {N _ {e l e c t r o n s} + 1 9 7 4 . 4}}
$$

<!-- PDF_PAGE: 9 -->

<div align="center">

Table 2

</div>

<div align="center">

SNR for 6U CubeSat night imaging camera of 89mm aperture, GSD = 52m and $ N_{TDI}=64 $

</div>

<table border="1"><tr><td>Band</td><td>λnm</td><td>Δλnm</td><td>QE</td><td>LrefWm-2sr-1μm-1</td><td>SNR@Lref[Requirement]</td><td>SNR</td></tr><tr><td>Photopic</td><td>560</td><td>100</td><td>0.87</td><td>2.5E-4</td><td>10</td><td>10.4</td></tr></table>

Using Equation (1) with $ N_{TDI}=64 $ $ T_{scope}=0.9 $ $ T_{atm}=0.7 $ $ T_{filter}=0.6 $ $ D=89\mathrm{mm} $ $ L=52\mathrm{m} $ $ \varphi=0 $ $ H=600\mathrm{km} $ , and $ \nu_{g}=6,907\mathrm{ms}^{-1} $ the SNR is calculated for a surface spectral radiance of $ 2.5\times10^{-8} $ $ \mathrm{Wc m}^{-2}\mathrm{s r}^{-1}\mu\mathrm{m}^{-1} $ in the photopic band with a central wavelength of $ 0.56\mu\mathrm{m} $ and a band width of $ 0.1\mu\mathrm{m} $ . Table 2 summarises the calculation and shows the SNR requirement is met.

The swath width requirement of 100km requires the camera to have a field of view of $ 9\cdot 5^{\circ} $ which is possible given the 101mm focal length. Tsitas and Kingston $ ^{(1)} $ specify the use of a polar Sun synchronous orbit for the 6U CubeSat to passively maintain the local time of ascending node, which could be set to the 8:30 to 10:00 pm local time suggested by Elvidge et al $ ^{(17)} $ . As specified by Tsitas and Kingston $ ^{(1)} $ onboard GPS allows geolocation of the images.

Using TDI creates the pointing stability requirement that an image on a pixel stays within the TDI column as the spacecraft moves down track. Three sigma pointing stability of half a pixel width during the TDI integration time is used as the requirement for TDI imaging on the 6U CubeSat by Tsitas and Kingston $ ^{(1)} $ . A GSD of 52m subtends an angle of 17.9 arcsec from 600km altitude. Tsitas and Kingston $ ^{(1)} $ specify a LN-200S fibre optic gyroscope $ ^{(20)} $ to propagate the attitude during the TDI integration time, following an approach suggested by Grocott and Carroll $ ^{(14)} $ The 1 sigma pointing error after propagating the output from the gyro for t seconds is given by Equation (3) for the LN-200S, where ARW is the angular random walk noise.

$$
1 \sigma \mathrm {p o i n t i n g e r r o r} = A R W \sqrt {t} < \frac {4 . 2 \mathrm {a r c s e c}}{\sqrt {s}} \sqrt {t}
$$

The dwell time for a pixel is 7.5ms and the TDI integration time for 64 pixels is 0.48s. The 3 sigma pointing error after propagating the output from the gyro is therefore 8.7 arcsec which is less than the angle subtended by half a pixel (8.95 arcsec), satisfying the pointing stability requirement.

While further work is required to investigate the orbit repeat cycle and to define the required radiances in other spectral bands it appears the requirements for Nightsat could be met by a 6U CubeSat, for significantly less than the < $ 30m ( < $ 100m for a Venture class mission) cost estimated for Nightsat $ ^{(21)}$.

## 7.0 CONCLUSIONS

The 6U CubeSat design described by Tsitas and Kingston $ ^{(1)} $ can carry out some of the commercial missions currently thought to require microsatellites, such as a night imaging satellite and disaster monitoring constellation with RapidEye-like agricultural monitoring abilities.

- This provides an economy of means that should improve the chances of funding for many mission concepts.

<!-- PDF_PAGE: 10 -->

- Earth observation constellations with much higher temporal resolution than existing systems can now be contemplated.

- Many developing countries could afford entry into such a constellation, gaining access to agricultural monitoring data with GSD, spectral coverage and revisit times to RapidEye standard.

- The design could also be the basis for a standard satellite for space science and astronomy, which will give scientists a low cost and timely way to carry out research in space, allowing the exploration of new ideas in a relatively inexpensive and informal fashion.

## REFERENCES

1. TSITAS, S. and KINGSTON, J. 6U CubeSat design for Earth observation with 6.5m GSD, 5 Spectral Bands and 14 Mbps downlink, Aeronaut J, November 2010, 114, (1161), pp 689-697.

2. ISO/TC 20/SC 14/WG 3, Space systems — Determining orbit lifetime, ISO/DIS/27852, 2009 <http://aiaa.kavi.com/apps/group_public/download.php/1973/20090605_ISO_27852_(G)_Orbit_Lifetime.pdf>

3. The RapidEye Mission, 2007, <http://wgiss.ceos.org/meetings/wgiss24/Host%20Workshop/RapidEye WGISS_Oct2007.pdf>

4. RapidEye: A commodities view From 60,000 feet, 2007, <http://www.rapideye.de/upload/In%20the%20News/ HedgeworldJuly07.pdf>

5. Dnepr — Specifications, Space and Tech, <http://www.spaceandtech.com/spacedata/elvs/dnepr_specs.shtml>

6. Small-satellite costs, 2001, Crosslink, <http://www.aero.org/publications/crosslink/winter2001/04.html>

7. SpaceX, 2011, <http://www.spacex.com/falcon1.php>

8. National Science Foundation, CubeSat-based Science Missions for Space Weather and Atmospheric Research, 2008 <http://www.nsf.gov/pubs/2008/nsf08549/nsf08549.htm>

9. Maxwell Technologies, Datasheet BC Power Series Radial D Cell 310F, Ultracapacitor <http://www.maxwell.com/products/ultracapacitors/docs/DATASHEET D CELLS 1017105.PDF>

10. Clyde Space, User Manual: Standalone 30Wh Battery, 2010, Document No: C3-USM-5016-CS-BAT- 30Wh<http://www.clyde-space.com/documents/1902>

11. AGUTTES, J.P. High resolution (metric) SAR microsatellite, based on the CNES MYRIADE bus, Geoscience and Remote Sensing Symposium (IGARSS 01), IEEE 2001 Int, 2001, 1, pp224-226.

12. BUSAZI, D., CATANZARITE, J., LAHER, R., CONROW, T., SHUPE, D., GAUTIER, T.N., KREIDL, T. and EVERETT, D. The detection of multimodal oscillations on $ \alpha $ Ursae Majoris,Astrophysical J, April 2000, 1, (532), L133-L136.

13. ZEE, R. and STIBRANY, P., Canada's first microsatellite — an enabling low-cost technology for future space science and technology missions, Canadian Aeronautics and Space J, 48, (1), pp 1-11.

14. GROCOTT, S.C.O. and CARROLL, K.A. Arc-second attitude control for the NESS asteroid/satellite tracking microsat, <http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.133.7848&rep=rep1&type=pdf>

15. Surrey Satellite Technology Ltd, Surrey Missions: DMC Disaster Monitoring Constellation, <http://centaur.sstl.co.uk/datasheets/Mission_DMC.pdf>

16. CURIEL, A., BOLAND, L., COOKSLEY, J., BEKHTI, M., STEPHENS, P., SUN, W. and SWEETING, M. First results from the disaster monitoring constellation (DMC), Acta Astronautica, 2005, 56, pp 261-271.

17. ELVIDGE, C.D., CINZANO, P., PETTIT, D.R., ARVESEN, J., SUTTON, P., SMALL, C., NEWMAN, R., LONGCORE, T., RICH, C., SAFRAN, J., WEEKS, J. and EBENER, S. The Nightsat mission concept, Int J Remote Sensing, 2007, 28, pp 2645-2670.

18. Fairchild Imaging, 2009, <http://www.fairchildimaging.com/documents/CCD5061DataSheetRevB_004.pdf>

19. Hamamatsu, TDI-CCD image sensors, 2009. <http://sales.hamamatsu.com/assets/pdf/parts_S/ s1020002_etc_kmpd1098e04.pdf>

20. LN-200S Inertial Measurement Unit <ftp://ftp.uni-duisburg.de/Hardware/Litton/Prodsheet_LN200S.pdf>

21. Nightsat Mission Overview, 2008, < http://files.harc.edu/Documents/Announcements/2008/NightSat.pdf>