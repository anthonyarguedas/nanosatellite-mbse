---
source: null
title: "citation-candidate-1786"
page_count: 44
converted_at: "2026-09-08T15:50:11Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# Preliminary mission profile of Hera's Milani CubeSat

</div>

Fabio Ferrari $ ^{*} $ , Vittorio Franzese, Mattia Pugliatti, Carmine Giordano, Francesco Topputo

Department of Aerospace Science and Technology, Politecnico di Milano, Via La Masa 34, 20156, Milan, Italy

## Abstract

CubeSats offer a flexible and low-cost option to increase the scientific and technological return of small-body exploration missions. ESA's Hera mission, the European component of the Asteroid Impact and Deflection Assessment (AIDA) international collaboration, plans on deploying two CubeSats in the proximity of binary system 65803 Didymos, after arrival in 2027. In this work, we discuss the feasibility and preliminary mission profile of Hera's Milani CubeSat. The CubeSat mission is designed to achieve both scientific and technological objectives. We identify the design challenges and discuss design criteria to find suitable solutions in terms of mission analysis, operational trajectories, and Guidance, Navigation, & Control (GNC) design. We present initial trajectories and GNC baseline, as a result of trade-off analyses. We assess the feasibility of the Milani CubeSat mission and provide a preliminary solution to cover the operational mission profile of Milani in the close-proximity of Didymos system.

Keywords: Hera, AIDA, CubeSat, Didymos, asteroid, Milani

<!-- PDF_PAGE: 2 -->

## 1. Introduction

Motivated by a great scientific interest and large accessibility to space missions, small celestial bodies represent the current frontier of space exploration. The close-proximity exploration of asteroids and comets entered a new era in 2000, as the NEAR-Shoemaker spacecraft entered into orbit around asteroid 433 Eros, achieving the first rendezvous with a small celestial body (Veverka et al., 2001). An important milestone was marked more recently, by ESA's Rosetta (Ulamec et al., 2014) and later by JAXA's Hayabusa 2 (Van wal et al., 2018; Tsuda et al., 2020) missions, which were able to release small probes and SmallSats on the surface and/or in the close-proximity of such objects. In this context, CubeSats offer a flexible and low-cost option to increase the scientific and technological return of small-body exploration missions. Although many concepts of interplanetary CubeSats have been studied and/or are planned for future missions (Walker et al., 2018; Franzese et al., 2019; Speretta et al., 2019; Topputo et al., 2020), very few of them have flown so far (Freeman, 2020; Lockett et al., 2020), and no CubeSat has ever flown in the proximity of a small-body yet. ESA's Hera mission (Michel et al., 2018), the European component of the Asteroid Impact and Deflection Assessment (AIDA) international collaboration (Cheng et al., 2015), plans on deploying two CubeSats in the proximity of binary system 65803 Didymos, after arrival in 2027. The idea is supported by several SmallSat/CubeSat studies that have been performed in the past few years with reference to Hera (formerly known as AIM), to study the feasibility of deploying a small lander (Ferrari and Lavagna, 2018, 2016; Lange et al., 2018; Celik et al., 2019) and possibly CubeSats (Kohout et al., 2018; Lasagni Manghi et al., 2018; Perez et al., 2018) in the close proximity of Didymos. These were anticipated by detailed studies of the dynamical environment near binary asteroid systems (Tardivel and Scheeres, 2013; Tardivel, 2016; Ferrari et al., 2016, 2014; Celik and Sánchez, 2017), some with direct application to the Didymos case study (Dell'Elce et al., 2017; Capannolo et al., 2019, 2016). Hera is currently in its phase-B design, on-track to be launched in 2024. Its payloads have been

<!-- PDF_PAGE: 3 -->

recently consolidated and, as mentioned, it will carry two 6U CubeSats, to be deployed after rendezvous with Didymos. These are called Juventas (Karatekin et al., 2019) and Milani. Milani has been officially confirmed on mid 2020 and is currently in its phase-A design. Its flight readiness does reflect Hera schedule, foreseen in late 2024.

In this work, we discuss the feasibility and preliminary mission profile of Hera's Milani CubeSat. The Milani mission is designed to achieve both scientific and technological objectives. The first include the global mapping of Didymos (primary) and Dimorphos (secondary) asteroids. This involves determining the composition difference between the bodies and the study of their surface properties. In the context of the AIDA international collaboration, Milani will help at determining the composition of the ejecta created after the impact of DART spacecraft (Cheng et al., 2018) in 2022 on the surface of Dimorphos, and their fallbacks on the surface of the asteroids. In terms of the technological objectives, the mission will be among the first to operate CubeSat technologies in deep space and the first to use Inter-Satellite Link (ISL) network with the mother spacecraft in such challenging context.

Milani is a 6U CubeSat with maneuvering capabilities both in terms of translational and attitude motion (full 6-DOF). After release it will perform autonomous operations to reach its operational trajectories towards the fulfilment of its mission goals. The main payload aboard Milani is the ASPECT hyperspectral camera (Kohout et al., 2018). The characteristics of the ASPECT camera are reported in Table 1. The payload has three channels, which are the Visible (VIS), the Near-Infrared (NIR), and the Short Wavelength Infrared (SWIR). The three channels have different characteristics, especially in terms of field-of-view and sensor size. These quantities affect the allowed orbital ranges to the targets for scientific observations. The visible channel has the largest field of view and a 1 Mpx sensor size. The NIR is narrower than the VIS channel, while the SWIR is a mono-pixel circular FOV channel. In addition to ASPECT, which is used for scientific imaging only, Milani hosts two additional cameras, which are used for optical navigation. These cameras have not been selected yet:

<!-- PDF_PAGE: 4 -->

<div align="center">

Table 1: Characteristics of the ASPECT hyperspectral camera.

</div>

<table border="1"><tr><td>Parameter</td><td>Unit</td><td>VIS</td><td>NIR</td><td>SWIR</td></tr><tr><td>Field-Of-View</td><td>deg</td><td>10x10</td><td>6.68x5.36</td><td>5</td></tr><tr><td>Sensor Size</td><td>pix</td><td>1024x1024</td><td>640x512</td><td>1</td></tr><tr><td>Pixel Size</td><td>μm</td><td>5.5x5.5</td><td>15x15</td><td>1000</td></tr><tr><td>Focal Length</td><td>mm</td><td>32.3</td><td>81.7</td><td>11.7</td></tr><tr><td>F-number</td><td>-</td><td>3.3</td><td>6.0</td><td>0.9</td></tr></table>

the properties and performance assumed for navigation cameras are reported in Section 4.4. As a secondday payload, Milani hosts the VISTA thermogravimeter (Dirri et al., 2018), which will collect information on the dust environment near the asteroids. It is operated in background during the operational phases of the Milani mission: it does not impose any further requirement and does not require a specific tayloring of the mission profile.

After release in the proximity of Didymos binary asteroid, Milani independently makes its own way to its operational trajectory, optimized to observe the asteroid system. In this work, we consider the CubeSat limitations given by miniaturized components, and address the challenges in deriving an optimal mission profile which meets the mission and scientific objectives. The GNC architecture and design that allow to achieve such a mission are also shown. It is worth stressing that the initial results presented in this paper have been obtained in response to the relevant ESA call. As such, the preliminary profile here shown will be revised as both mission and spacecraft design advance in later stages.

The paper is organized as follows. Section 2 reports the design constraints of the mission given by the environment and the payload. Section 3 shows the mission profile with a detailed explanation of the mission phases. Then, the GNC architecture and preliminary design are shown in Section 4. The operational analysis of the payload is reported in Section 5. Finally, conclusions and a summary of the results are given in Section 6.

<!-- PDF_PAGE: 5 -->

<div align="center">

Table 2: Didymos system characteristics and imaging constraints.

</div>

<table border="1"><tr><td>Asteroid</td><td>d</td><td>m$_{d}$</td><td>$p_{v}$</td><td>GSD</td><td>$\alpha$</td><td>$\theta$/FOV</td></tr><tr><td>Didymos</td><td>780m</td><td>10%</td><td>0.15</td><td>≤2m/pix</td><td>5-25deg</td><td>≤4</td></tr><tr><td>Dimorphos</td><td>170m</td><td>10%</td><td>0.15</td><td>≤2m/pix</td><td>5-25deg</td><td>≤1</td></tr></table>

## 2. Design constraints

The constraints affecting the design of the mission and the CubeSat platform are presented in this Section. The Didymos binary system is composed of two asteroids: the primary (Didymos, also called D1 in the following) and its satellite (Dimorphos, also called the secondary or D2 in the following). The primary body has an estimated diameter of 780 m and an assumed albedo of 0.15. The secondary has an estimated diameter of 170 m and an assumed albedo of 0.15. Current estimates consider a 10 % size error for both asteroids. The requirements applicable to the Milani CubeSat derive directly from both the mission objectives and the ASPECT payload. To achieve the mission objectives with ASPECT, the payload team has determined the following two main conditions: 1) To map both asteroids with a ground resolution lower than 2 m/pixel with images from both the VIS and the NIR channels; 2) To observe the asteroids with a phase angle (Sun-asteroid-CubeSat angle) between 5 and 25 degrees. In order to ease the operations of Milani, Dimorphos is required to be imaged within a single picture, always inside the FOV of ASPECT, while the primary can be imaged as a 4-images mosaic. These values are summarized in Table 2, where d is the equivalent diameter of the asteroids, $ m_{d} $ the associated margin, $ p_{v} $ the albedo, GSD the ground sampling distance, $ \alpha $ the phase angle, and $ \theta $ /FOV the ratio between the apparent dimension of the asteroid to the ASPECT field-of-view. Note that the limiting value for the FOV is given by the NIR channel, since it is narrower than the VIS channel. The SWIR channel is not considered here because it is a monopixel channel.

With the values in Table 2, it is easy to verify that Dimorphos fills the FOV

<!-- PDF_PAGE: 6 -->

of the VIS channel at 1069 m of distance and the FOV of the NIR channel at 1997 m of distance, while Didymos fills a $ 2 \times2 $ image mosaic using the VIS channel at a distance of 2433 m and the NIR channel at 4572 m. Thus, the value of 4572 m is considered as the lower bound on the range constraints to the binary system. The maximum allowable ranges to meet the 2 m/pix imaging GSD are 11700 m for the VIS channel and 10940 m for the NIR channel. Thus, the upper bound on the relative range between the binary system and Milani is 10940 m. The communication link between Milani and the mother spacecraft through the ISL is assumed to be omnidirectional and available up to 60 km of relative distance between the two spacecraft.

All in all, the operations in the nominal orbit shall be performed at ranges from Didymos within 4572-10940 m and phase angles within 5 and 25 degrees, as summarized in Table 3, within a 60 km range from Hera mothercraft.

<div align="center">

Table 3: Mission design constraints.

</div>

<table border="1"><tr><td>Asteroid</td><td>Min Range</td><td>Max Range</td><td>Min Phase Angle</td><td>Max Phase Angle</td></tr><tr><td>Didymos</td><td>4572m</td><td>10940m</td><td>5deg</td><td>25deg</td></tr></table>

## 3. Mission profile

This section presents the preliminary mission profile for Hera's Milani CubeSat, from its release in the proximity of Didymos system, up to its decommisioning. We discuss the design strategy to provide efficient release of Milani from Hera spacecraft and detail the operational trajectories during the CubeSat science phase. End-of-life options are proposed. The feasibility of the mission profile is eventually discussed. The overall design is compliant with constraints outlined in Section 2. The dynamics of the CubeSat near the Didymos system are studied using a high-fidelity model, which includes the heliocentric motion of Didymos system barycenter, the binary motion of the asteroids (provided by high-order

<!-- PDF_PAGE: 7 -->

integration in ESA's Hera Mission kernels $ ^{1} $ and relevant perturbations, such as the effects of the non-sphericity of asteroids (through a polyhedral model of Didymos and ellipsoidal model of Dimorphos) and Solar Radiation Pressure (SRP).

## 3.1. Release strategy

The Hera spacecraft plans on releasing Milani after arrival at Didymos system, in late spring 2027. In this work, we set the release date to May 1st, 2027. At this time the Didymos-Sun distance is 1.5 AU and increases up to 2.0 AU during the expected operational life of the CubeSat. The selection of Milani operational dates is important to characterize the dynamical environment in the proximity of Didymos, as it affects the magnitude of the SRP, which is relevant. On the other hand, the release date does not affect the operations of Milani in terms of orbital determination and illumination conditions. The relative geometry of Hera trajectories and release point is set in terms of Milani/Hera, Didymos and Sun position. At any epoch, the release will be performed when Hera is between the binary system and the Sun direction, in order to have Didymos visible on its day side. Milani's release conditions are carefully selected after an extensive analysis, involving the investigation of different release points on Hera's Early and Detailed Characterization Phases trajectories $ ^{2} $ , the analysis of geometrical constraints at release, the dynamics of the CubeSat after release relative to Hera mothercraft and Didymos system. In particular, the following criteria have been considered in terms of release geometry and release trajectory:

- Minimum angle between CubeSat release velocity direction and CubeSat Sun direction of 45 deg;

- Minimum safety factor C of the release trajectory of 0.4.

<!-- PDF_PAGE: 8 -->

The safety factor C measures the energy of the trajectory (C>0 for hyperbolas), and is defined as

$$
v _ {\mathrm {p e r i}} = (1 + C) v _ {\mathrm {p a r a b}}
$$

with $ v_{\mathrm{peri}} $ and $ v_{\mathrm{parab}} $ defined as the velocity at pericenter on the release trajectory and the parabolic velocity at the release point, respectively. These conditions derive from the mother spacecraft requirements in terms of safety and illumination conditions. In addition, the release trajectory was selected to guarantee consistent relative motion with respect to Hera spacecraft and Didymos system for up to 7 days after release, in terms of:

- Maximum CubeSat-Hera distance of 60 km, to ensure communication with the mothercraft;

- Maximum phase angle of Didymos system (Sun-Didymos-CubeSat angle) of 90 deg, to ensure dayside visibility of the asteroids;

Finally, we analysed the robustness to release uncertainties, related to both the deployer mechanism and Hera's GNC accuracy. These are quantified as:

- Release velocity in the range 0-5 cm/s ( $ \pm1 $ cm/s, $ 3\sigma $ value)

- Release direction accuracy of the deployer mechanism within 5 deg (3 $ \sigma $ value)

- Release orientation accuracy of Hera spacecraft within 0.5 deg ( $ 3\sigma $ value)

The analysis performed is aimed at finding suitable release directions. In this case, pointing and release direction errors are the most important sources of errors. Position and velocity errors of Hera play a minor role in detecting preferred directions and, at the current stage they can be neglected. These will be added at a later refinement of the design. Release points are chosen among Hera spacecraft trajectories, which are retrieved from ESA's Hera Mission kernels. We performed an extensive Monte Carlo analysis of the parameter space (40k runs among eight difference release points) and, as a result, a release from 30 km (distance from Didymos system barycenter) in the direction (Az=10 deg, el=60 deg), is selected as a design baseline solution. Directions are shown in

<!-- PDF_PAGE: 9 -->

Didymos equatorial plane, where Azimuth is the in-plane angle (Az=0 deg towards the projection of Sun's position on Didymos equatorial plane), and elevation is the out-of-plane angle. Figure 1 shows the results of the analysis in terms of release direction, for the 30 km distant release point. Each release condition is propagated forward for 7 days. The compliance to the aforementioned constraints is checked at any time on the release trajectory. Feasible release directions are identified by green markers, while red markers indicate conditions where the constraints are not satisfied. Unfeasible release direction in Figure 1 are characterized by a mix of green and red markers. This is due to effect of the release velocity: these directions are typically unfeasible for high release velocities (close to 5 cm/s), but might be feasible for lower velocities. In fact, the higher the release velocity, the higher the probability of falling beyond a 90 deg phase angle or 60 km distance from Hera after a 7-day ballistic arc. The blue marker highlight the selected release direction.

The release solution is shown in Figure 2. The trajectory of Milani and Hera spacecraft are shown for seven days after release. This solution is compliant with design constraints, robust to uncertainties, and guarantees a safe 7-day ballistic arc after release.

## 3.2. Operational trajectories

After release from Hera and commissioning, Milani will maneuver to perform scientific operations. This section presents the selected operational orbit and maneuvering strategy to accomplish Milani's mission objectives. As summarized in Table 3, scientific operations are carried at a distance within the range 4.572-10.940 km from Didymos system and when the phase angle (Sun-asteroid-CubeSat angle) of Didymos and Dimorphos is in the range 5-25 deg. Also, we enforce the CubeSat to have a non-zero elevation above Didymos equatorial plane, to ensure visibility of the asteroids poles. In terms of $ \Delta v $ cost, we considered a budget of 10 m/s. In addition to constraints reported above, additional design drivers were considered, namely:

- Safety, in terms of orbital energy, quantified by the safety factor C. We

<!-- PDF_PAGE: 10 -->


![figure_001.png](figure_001.png)



<div align="center">

Figure 1: Release options in the Didymos equatorial plane. Green and red markers indicate compliant and non-compliant solutions, respectively. The upper-left picture is the composite of the other three pictures, plus the addition of geometrical constraints at release (forbidden $ \pm 4 5 $ deg cone around CubeSat-Sun direction).

</div>

Azimuth is the in-plane angle (Az=0 deg towards the projection of Sun's position on Didymos equatorial plane), elevation is the out-of-plane angle. Yellow and black markers indicate the direction of the Sun and Didymos, respectively, as seen from the release point. The blue marker represents the selected release direction.

give the highest priority to trajectories that are inherently safe, i.e. with C>0 (hyperbolic arcs). Closed trajectories (C<0), according to their range, have a moderate to high risk of entering chaotic three-body dynamics, potentially resulting in impacts with either of the bodies.

- Simplicity, in terms of reduced operational burden required to perform active operations on the CubeSat and optimization of the time allocated on Hera to relay Milani operations. To accomplish this, we leverage natural dynamics and perturbations of the asteroid environment to reduce the frequency of manoeuvres. In particular, we consider this criterium more important than $ \Delta v $ cost, which is less critical in our mission.

<!-- PDF_PAGE: 11 -->


![figure_002.png](figure_002.png)



<div align="center">

Figure 2: Nominal release trajectory in the Didymos equatorial frame. Milani's and Hera's orbital motion is shown for seven days after release. Geometrical constraints (release exclusion angle around Sun's direction), and Didymos system are shown.

</div>

- Robustness to uncertainties due to the system and dynamical environment. This is tightly connected to safety and simplicity criteria. Inherently safe trajectories are typically more robust to uncertainties. On the other hand, long ballistic time of flights between consecutive manoeuvres require robust trajectories, able to deal with uncertainties without jeopardizing the safety of the Hera mission or altering the mission profile strategy.

- Cost, in terms of $ \Delta v $ . Our analyses show that cost is not critical to our mission. For this reason, safe, simple, and robust trajectories are preferred, at a cost of a slightly higher $ \Delta v $ .

We performed an extensive trade-off analysis between several orbital strategies and trajectory solutions, including hyperbolic arcs, closed orbits and three-body

<!-- PDF_PAGE: 12 -->

proximity solutions. The results of the trade-off are summarized in Table 4. In particular, we show the suitability of each strategy in terms of available time for science operations (time in the science admissible region), navigation constraints (check on phase angles and asteroid illumination), safety/risk of entering chaotic dynamics, simplicity of operations/maneuvering strategy, dynamical robustness to uncertainties and $ \Delta v $ cost. The study clearly identifies the hyperbolic-arc strategy as the most promising solution to host Milani scientific operations. This has several advantages in terms of safety, simplicity and robustness, and provides the best option in terms of asteroid visibility. In particular, we implemented a patched-arc manoeuvring strategy that leverage the SRP acceleration to target pre-selected waypoints. To reduce the burden for active operations, we consider a 4-3-4-3 maneuvering pattern, where maneuvers are performed after a 4- or 3-day ballistic arc. This is similar to the strategy implemented by the Hera spacecraft. Selecting such pattern has the advantage to ease operations at maneuvering points, which will be fit within a fixed weekly schedule and aligned to Hera operations.

After a thorough design process, where several hyperbolic-arc waypoint configurations have been investigated, the waypoints of the hyperbolic loop are selected as shown in Figure 3. Left plots in Figure 3 show the ranges and admissible science regions (between dashed lines). Milani has science windows of 1-2 days for each arc. Projections of the trajectory on the Didymos equatorial plane are shown on the right. To maximize the time spent by the spacecraft within the science admissible region, the orbital plane between consecutive hyperbolic arcs is tilted by a few degrees at each maneuvering point. This is clearly visible in the y-z projection plot (lower-right). This allows Milani to fly within admissible ranges in terms of aspect angle and distance, when transiting near the pericenter of each hyperbola. Numbered labels indicate the maneuver sequence, under the 4-3-4-3 day scheme, from maneuver 0 (insertion into science loop trajectory) up to maneuver 5. The waypoint design strategy is modular and can be further extended. As detailed in Section 5, six hyperbolic arcs (21 days in total) are enough to accomplish the scientific objectives of the mission. If needed,

<!-- PDF_PAGE: 13 -->

<div align="center">

Table 4: Science orbit trade-off matrix.

</div>

<table border="1"><tr><td>Strategy</td><td>Time for science</td><td>Navigation</td><td>Safety/risk</td><td>Simplicity</td><td>Robustness</td><td>Cost: monthly</td></tr><tr><td>Loop(C&gt;0)</td><td>1-2 days per loop</td><td>Always on asteroids&#x27; dayside</td><td>Inherently safe</td><td>Compliant to 4-3-4-3 pattern</td><td>3-4 days</td><td>1.5m/s</td></tr><tr><td>Loop(C&lt;0)</td><td>2-3 days per loop</td><td>Always on dayside</td><td>Moderate risk</td><td>Compliant to 4-3-4-3 pattern</td><td>2-3 days</td><td>1.2m/s</td></tr><tr><td>Closed orbit(7km)</td><td>&lt;1 day per orbit</td><td>Dayside for half orbit</td><td>Moderate risk</td><td>Compliant to 4-3-4-3 pattern</td><td>2-3 days</td><td>20cm/s</td></tr><tr><td>Closed orbit(2-7km)</td><td>&lt;few hours per orbit</td><td>Dayside for half orbit</td><td>High risk</td><td>Maneuver frequency1-2 days</td><td>&lt;1 day</td><td>&lt;20cm/s</td></tr><tr><td>3-Body Solution(&lt;2km)</td><td>Never in science region</td><td>Little dayside time; exceeding FOV</td><td>High risk</td><td>Maneuver frequency&lt;1 day</td><td>Not robust. Chaotic dynamics</td><td>&lt;20cm/s</td></tr></table>

the science loop trajectory can be further extended at the cost of 1.5 m/s per month.

## 3.2.1. End-of-Life options

Eventually, we discuss two End-of-Life (EoL) options in terms of their concept and feasibility in the broad context of the Hera mission, with the goal to identify benefits and criticalities. No baseline solution was selected within the context of this work.

Option 1: Injection into a graveyard heliocentric orbit. This option is safe and cheap, and it does not require any additional trajectory design after the scientific phase (except for a long-term integration of the outgoing heliocentric orbit). As

<!-- PDF_PAGE: 14 -->


![figure_003.png](figure_003.png)




![figure_004.png](figure_004.png)




![figure_005.png](figure_005.png)



<div align="center">

Figure 3: Nominal science trajectory. Phase angle and distance time profile with respect to Didymos (D1) and Dimorphos (D2) are shown in upper and lower left plots. Science admissible region is highlighted (ranges between dashed lines). Projections on Didymos Equatorial frame x-y and y-z plane are shown in upper and lower right plots, respectively. These show science admissible regions in terms of distance from the binary system (green sphere is minimum distance, red sphere is maximum) and phase angles (green cone is minimum value, red cone is maximum value). The Sun direction is also shown (orange arrow inside the green cone), as well as the projection of Hera spacecraft's trajectory (green lines in the upper right plot).

</div>

discussed, the nominal science loop is built as a sequence of hyperbolic arcs Missing one manoeuvre would safely bring Milani into an escape trajectory from the Didymos system. In addition, the SRP accelerates the CubeSat further away from Didymos, increasing its orbital energy. In this case, a safe graveyard heliocentric orbit can be achieved by missing the last manoeuvre of the scientific phase. After this, the spacecraft takes approximately 10 days to fly beyond a 60 km distance from Hera spacecraft. This option is the safest possible and may be preferred to avoid criticalities in terms of operational burden and costs. However, it does not provide any opportunistic science information in addition to those gathered during the science phase: it is a low risk-low gain solution.

<!-- PDF_PAGE: 15 -->

Option 2: Landing attempt on Dimorphos. The second option is to attempt a landing on D2. After the nominal scientific and technological objectives of the mission are accomplished, it might be worth to exploit Milani to provide additional data on the Didymos system. To achieve this goal, a higher risk can be accepted. In this context, we plan to get closer to the Didymos system, dropping the design driver of flying inherently safe hyperbolic trajectories. As mentioned, orbiting the inner region of Didymos system poses several challenges in terms of navigation and robustness to manoeuvres. This is a high risk-high gain option. The knowledge analysis performed in Section 4.2 shows that, in principle, the current GNC baseline would be compatible with a soft-landing design for the CubeSat. However, a more detailed analysis will be required to rigorously assess the feasibility of such option.

## 3.3. Momentum budget

As mentioned, the SRP plays a fundamental role in assessing the dynamics of the CubeSat in the close-proximity of Didymos. Also, it contributes in a relevant manner to the active maneuvering costs to be provided to control the attitude of the CubeSat. The momentum budget is estimated here by assessing the impact of the SRP perturbation to the attitude dynamics of Milani. We use a cannonball model with an equivalent area of 0.5160 m $ ^{2} $ , a reflection coefficient $ ( C_{r} ) $ of 1.1926, and a constant arm of 5 cm. These data are consistent for a 6U CubeSat with large solar arrays.

As mentioned earlier, the baseline scenario considers that Milani is released in May 2027, when the distance from the Sun is 1.5 AU, reaching 1.9 AU and 2.2 AU after 3 and 6 months of operations, respectively. For comparison, we consider here the backup launch option as well, which considers a CubeSat release on January 2031, when the distance from the Sun is 1.1 AU, reaching 1.5 AU and 1.9 AU after 3 and 6 months of operations, respectively. The latter option is considered since it is a worst case scenario: the CubeSat is closer to the Sun and the effect of SRP is higher. The total momentum buildup due to SRP in the worst case scenario (backup launch and 6 months of operations)

<!-- PDF_PAGE: 16 -->

<div align="center">

Total momentum build up at @EOL

</div>


![figure_006.png](figure_006.png)



<div align="center">

Figure 4: SRP total momentum build up by the SRP on Milani after 6 months. The nominal value is shown with a red marker for $ C_{R}=1.19 $ and SRP arm=5 cm.

</div>

is illustrated in Figure 4 as function of the key parameters of the cannonball model. With the nominal values a total momentum build up of 0.99 mNms during the whole mission is estimated.

Assuming that the disturbance torque is building up on a single reaction wheel, two options are considered in terms of momentum capacity: 25 mNms and 55 mNms. In the first case a total of 40 dumping manoeuvres would be required for 6 months of operations (approximately 1 manoeuvre every 4.5 days) while in the latter one the number drop to 18 for 6 months of operations (approximately 1 manoeuvre every 10 days). The total $ \Delta V $ budget to be allocated for momentum dumping is therefore estimated to be around 1 m/s in the worst case scenario. The evolution of the $ \Delta v $ budget for desaturation as function of the mission launch and duration is illustrated in Figure 5.

<!-- PDF_PAGE: 17 -->


![figure_007.png](figure_007.png)



<div align="center">

Figure 5: Desaturation budget as function of mission duration for the nominal launch (blue curve) and backup launch (red curve).

</div>

## 4. GNC strategy

The key driver for Milani's GNC subsystem design is to maximize the opportunities to observe the binary asteroid system. Also, it is paramount to complement the Orbit Determination (OD) with optical navigation, to always track the target asteroid, and to increase the efficiency of the operations by exploiting the pointing of the scientific observations for optical navigation. All in all, it is beneficial for the mission to never lose the line-of-sight to the target asteroid while performing scientific but also housekeeping tasks.

The GNC system architecture is shown in Figure 6. Milani is equipped with an on-board computer (OBC) where two modules are present, namely the ADCS processing module and the GNC processing module. These modules are responsible for collecting and processing sensor inputs to elaborate commands for the actuators. The ground segment is responsible for computing the nominal guidance, navigation, and control of the satellite. This information is sent to the Hera spacecraft that is acting as a relay satellite and then sent back to Milani via the inter-satellite link (ISL). Apart from the ASPECT payload, we assume that Milani is equipped with a $ 2 1 \times1 6 $ deg NavCam and a $ 4 0 \times4 0 $ deg Wide Angle Camera (WAC). These are required for high-resolution imaging of the asteroids and optical navigation, as described in Section 4.4. The navigation measurements for Milani come from the navigation camera and ISL. The nav-

<!-- PDF_PAGE: 18 -->


![figure_008.png](figure_008.png)



<div align="center">

Figure 6: System architecture.

</div>

igation camera is used to acquire images of the two asteroids, while the ISL is exploited for range and range-rate measurements with respect to Hera. Milani is equipped with a Six Degree-of-Freedom Reaction Control System (6 DOF RCS) for trajectory and attitude control. The attitude measurements for Milani are given by an Inertial Measurement Unit (IMU), two sun sensors, and the star trackers. The attitude is also controlled by the reaction wheels.

## 4.1. Guidance

The Differential Guidance (DG) strategy (Dei Tos et al. (2019); Park and Scheeres (2006)) adopted for Milani's guidance is detailed in this section. In the DG formulation, the whole trajectory is subdivided in different legs. At the extremal points of a single leg, two maneuvers are applied to cancel both the position and velocity deviations on the final leg point. However, the final impulse is usually not applied in practice, since at the time of arrival at the final point a new maneuver is calculated in a receding horizon approach. The maneuver can be computed by minimizing the deviations from the nominal state

<!-- PDF_PAGE: 19 -->

at the final point in a least square residual sense. Thus, the maneuver that has to be applied at the time $ t_{j} $ in order to cancel out the deviations at time $ t_{j+1} $ is computed as Dei Tos et al. (2019)

$$
\Delta \mathbf {v} _ {j} = - \left(\Phi_ {r v} ^ {T} \Phi_ {r v} + \Phi_ {v v} ^ {T} \Phi_ {v v}\right) ^ {- 1} \left(\Phi_ {r v} ^ {T} \Phi_ {r r} + \Phi_ {v v} ^ {T} + \Phi_ {v r}\right) \delta \mathbf {r} _ {j} - \delta \mathbf {v} _ {j}
$$

where $ \delta\mathbf{r}_{j} $ and $ \delta\mathbf{v}_{j} $ are the (estimated) position and velocity deviation at time $ t_{j}, $ $ \Phi_{rr}, $ $ \Phi_{rv}, $ $ \Phi_{vr} $ and $ \Phi_{vv} $ are the 3-by-3 blocks of the State Transition Matrix (STM) $ \Phi\left(t_{j}, t_{j+1}\right) $ from time $ t_{j} $ to time $ t_{j+1} $ associated to the nominal trajectory.

## 4.2. Knowledge Analysis

Errors in the dynamical propagation of the trajectories, e.g. inaccuracies in state determination or thrust misalignment, can lead to large deviations with respect to the nominal trajectory. Hence, a knowledge analysis is required to compute, through a covariance analysis, the achievable state knowledge. Simulations of the radiometric data for range and range-rate coming from the ISL are performed, generating the pseudo-measurements as

$$
\rho = \sqrt {\boldsymbol {\rho} ^ {T} \boldsymbol {\rho}} + \varepsilon_ {\rho}, \quad \dot {\rho} = \frac {\boldsymbol {\rho} ^ {T} \boldsymbol {\eta}}{\rho} + \varepsilon_ {\eta}
$$

where $ \rho $ is the range, $ \dot{\rho} $ is the range rate, $ \rho=\mathbf{r}-\mathbf{r}_{H} $ is the relative distance between Milani and Hera, while $ \eta=\mathbf{v}-\mathbf{v}_{H} $ is the relative velocity with $ \varepsilon $ representing the error. $ \mathbf{r} $ and $ \mathbf{v} $ are position and velocity of Milani Cubesat, while $ \mathbf{r}_{H} $ and $ \mathbf{v}_{H} $ represent position and velocity of the Hera spacecraft. Pseudomesurements are used to feed an Extended Kalman Filter (EKF, Schutz et al., 2004) in order to simulate a realistic Orbit Determination procedure. In our case, the Hera spacecraft is always in view and no assessment of visibility windows is needed.

## 4.3. Guidance & Navigation closed-loop approach

The overall navigation cost, necessary to keep the spacecraft on the nominal path, is estimated in a closed-loop fashion, taking into account: 1) the knowledge analysis (as in Section 4.2) to estimate the deviation of the real trajectory from

<!-- PDF_PAGE: 20 -->

the nominal trajectory at the target points; 2) the differential guidance (as in Section 4.1) to assess the stochastic cost, starting from the estimated deviations. The total navigation cost is estimated by means of a Monte Carlo simulation. Following this approach, an initial Gaussian distribution with mean $ \bar{x}_{0} $ and covariance $ P_{0} $ is identified and a set of samples $ x_{0}^{i} $ is generated. Both the state and the covariance matrix are propagated with the associated dynamics up the first measurement epoch, where the estimated trajectory is updated. Proceeding in this way, the state estimates are sequentially updated as new measurements are processed, leading to the position and velocity knowledge profiles. This is repeated up to the final epoch of the Orbit Determination phase, where the deviation from the nominal path is estimated. The deviation is then pushed forward using the STM up to the maneuver time and used to feed the guidance law. The correction impulse is computed and applied. The whole process is repeated up to the final time for each initial state in the sample set. The estimation of the total cost for each sample is obtained as the sum of all maneuvers' cost, i.e., $ \Delta v_{i}=\sum_{j=1}^{N}\left\|\Delta\mathbf{v}_{j}^{i}\right\|. $

## 4.3.1. Science phase

During the science phase, it is of paramount importance to acquire precisely and track the nominal trajectory in order to achieve the mission objectives. An assessment considering a higher fidelity model, with the OD process in the loop, is performed. Some assumptions are made for this analysis and they are listed below:

- The guidance law is the standard differential guidance algorithm;

- Correction maneuvers are given together with deterministic maneuvers;

- No uncertainty in stochastic maneuvers is considered;

- Due to technological constraints, correction maneuvers are not applied if their value is lower than 5 mm/s;

<!-- PDF_PAGE: 21 -->

- An initial a-priori uncertainty of 10 m on position, 1 mm/s on velocity (3 $ \sigma $ ) is used;

- To compensate for differences between physical model and real world, a thrust misalignment of 1% in magnitude and 1 deg in pointing angle $ (3\sigma) $ is considered;

- The ISL is simulated taking into account an accuracy of 1 m in range and 0.1 mm/s in range-rate. The error is modelled as Gaussian noise;

- In order to allow Flight Dynamics estimations and reduce the operational costs, an interval of 1.5 days between the maneuver and the beginning of the OD phase is considered, while a cut-off time of 1 day is inserted before the maneuver;

- The ISL performs a range measurement every 20 minutes and a range-rate every 2 minutes;

- Propagation is done linearly by means of the STM, while the estimation is done exploiting the EKF;

- 1000 samples Monte Carlo run.

Following these assumptions, a timeline for the science orbit can be derived. In Figure 7, red dots indicate when the range measurements are computed, while blue dots shows range-rate measurements. Orange bars mark the maneuvers time.

The outcome of the knowledge analysis is reported in Figure 8 and Figure 9. They illustrate the results of the covariance analysis and, in particular, the achievable knowledge accuracy of the spacecraft during the science phase. In the plots, the DidymosECLIPJ2000 (centered in Didymos system barycenter, axes directed as ECLIPJ2000) reference frame is considered. At the manoeuvre points, a jump in the velocity covariance and a change of slope in the position covariance can be clearly noted. This effect is due to the uncertainty in the nominal maneuver. The high relative accuracy associated to the ISL leads a

<!-- PDF_PAGE: 22 -->


![figure_009.png](figure_009.png)



<div align="center">

Figure 7: Science orbit timeline (measurements dots are too close to be distinguished).

</div>

quite precise knowledge at the final point. Indeed, $ 1\sigma $ position total accuracy is 100 m, while the velocity accuracy is better than 1 mm/s. Furthermore, the corrections are very effective in strongly reducing the dispersion. This leads to errors of some meters in position and few tens of microns per second in velocity after the correction step. The overall error associated to the OD is compatible with respect to the one assumed in the previous analyses when a mechanization of the error was considered. The 95% confidence level for total correction maneuver cost in the science phase is 0.069 m/s (Figure 10), while the position error one is 2.76 km, again mainly due to uncertainty in the final maneuver (Figure 11).

## 4.3.2. Release trajectory

As for the release trajectory, the approach described in Section 4.3 is exploited. The first day after release is fully allocated to commissioning. After that, a first OD lasting 1 day for orbit acquisition is made. This is useful to reduce the huge dispersion given by the release. No correction maneuver is performed during the first 7 days. Then, a second Orbit Determination is performed from day 5 and day 6, where the deviation from the nominal path is estimated and then used as input for the differential guidance algorithm. In the second transfer phase leg, from the Injection Maneuver to the Science Orbit Acquisition Manuever (SOAM), the scheme similar to the science phase one is used: two correction maneuvers are given, the first after 4 days from the Injection Maneuver (IM)

<!-- PDF_PAGE: 23 -->


![figure_010.png](figure_010.png)



<div align="center">

Figure 8: Achievable position knowledge in the science phase.

</div>

and the second after 7 days from the IM together with the SOAM. Differently from the science loop, the first correction maneuver is not associated with any deterministic maneuver, but it is needed in order to cope with the deviations caused by the Injection Maneuver and to target with an increased precision the Science Orbit Acquisition Maneuver point. In the second transfer phase leg a cut-off time of 1.5 days is considered between the OD and the maneuvers, plus a period of 1 day is taken into account between the maneuver and the beginning of the OD. For the initial state uncertainty, the worst-case scenario is taken as reference (see Section 3.3.1 for detailed discussion). Thus, a deployer release velocity of 5 cm/s with an uncertainty of 1 cm/s $ (3\sigma) $ is used. The half cone pointing error is 5 deg; on top of it the Hera pointing accuracy of 0.5 deg $ (3\sigma) $ is considered.

For clarity's sake, the assumptions made for this analysis are summarized and listed below:

- The guidance law is the standard differential guidance algorithm;

- Correction maneuvers are given with the IM, the SOAM and at day 4 of the second leg;

<!-- PDF_PAGE: 24 -->


![figure_011.png](figure_011.png)



<div align="center">

Figure 9: Achievable velocity knowledge in the science phase.

</div>

- No uncertainty in stochastic maneuvers is considered;

- Correction maneuvers are not applied if their value is lower than 5 mm/s;

- An initial uncertainty of 5 m on position is considered. The relative velocity with respect to Hera has a mean of 5 cm/s and a standard deviation of 1 cm/s $ (3\sigma) $ . A pointing error of 5 deg $ (3\sigma $ , half cone) with a 0.5 deg pointing accuracy is used;

- A thrust misalignment of 1% in magnitude and 1 deg in angle (3 $ \sigma $ ) is considered;

- The ISL is simulated taking into account an accuracy of 1 m in range and 0.1 mm/s in range-rate. The error is modeled as Gaussian noise;

- During the first leg, Orbit Acquisition is performed from day 1 to day 2, while Orbit Determination from day 5 to day 6;

- In the second leg, a interval of 1.5 days between the maneuver and the beginning of the OD phase is considered, while a cut-off time of 1 day is

<!-- PDF_PAGE: 25 -->


![figure_012.png](figure_012.png)



<div align="center">

(a)

</div>


![figure_013.png](figure_013.png)



<div align="center">

(b)

</div>

<div align="center">

Figure 10: (a) Navigation cost probability distribution function for science phase. On the y-axis the number of occurrences are shown. (b) Navigation cost cumulative distribution function for science phase.

</div>

inserted before the maneuver;

- The ISL performs a range measurement every 20 minutes and a range-rate every 2 minutes;

- Propagation is done linearly by means of the STM, while the estimation is done exploiting the EKF;

- 1000 samples Monte Carlo run.

Following these assumptions, a timeline for the transfer orbit can be derived. In Figure 12, red dots indicates when the range measurements are computed, while blue dots shows when range-rate is performed.

The knowledge analysis is reported in Figure 13 and Figure 14. They illustrate the results of the covariance analysis and the achievable knowledge accuracy of the spacecraft during the transfer phase. In the plots, the DidymosECLIPJ2000 reference frame is considered. The large dispersion at the beginning is only partially recovered through the Orbit Determination and an error of some tens of meters is found for the position at the SOAM. On the other hand, the velocity knowledge improves better during the transfer, leading to error less than 0.1 mm/s at the end of transfer phase. These figures show how the orbit acqui-

<!-- PDF_PAGE: 26 -->


![figure_014.png](figure_014.png)



<div align="center">

(a)

</div>


![figure_015.png](figure_015.png)



<div align="center">

(b)

</div>

<div align="center">

Figure 11: (a) Final error probability distribution function for science phase. On the y-axis the number of occurrences are shown. (b) Final error cumulative distribution function for science phase.

</div>


![figure_016.png](figure_016.png)



<div align="center">

Figure 12: Transfer trajectory timeline (measurements dots are too close to be distinguished).

</div>

sition phase is beneficial to enhance the knowledge analysis in the first transfer leg, quenching the dispersion and helping in determine the correct orbit the spacecraft is on just after the release. The covariance analysis shows also that the navigation costs (Figure 15) can be represented as a Gaussian distribution of mean 0.01354 m/s and a standard deviation of 0.0039 m/s. The 95%-ile for correction maneuver cost in the transfer phase is 2.1 cm/s.

## 4.4. Optical Navigaton

The baseline navigation strategy exploits information of range and range-rate with respect to the mother spacecraft. In addition, the mission will perform an optical navigation experiment by processing the images of the asteroids. This is

<!-- PDF_PAGE: 27 -->


![figure_017.png](figure_017.png)



<div align="center">

Figure 13: Achievable position knowledge in the transfer phase

</div>

intended to validate the performances of optical navigation on-board, but will not impact the baseline navigation strategy.

## 4.4.1. State-of-art methods and trade-off

Different state-of-art strategies can be adopted for optical navigation. They range from the landmark-based methods to centroiding and disk fitting methods. The landmark navigation estimates the position of Milani based on the natural landmarks on the asteroid surface de Santayana and Lauer (2015). It is accurate, however is also heavy from a computational standpoint. The centroiding method with disk fitting exploits the acquisition of the center of brightness of the figure to estimate the relative line-of-sight and the external horizon to estimate the apparent asteroid size, which is related to the relative range Gil Fernandez and Ortega-Hernando (2018). This method can yield a good accuracy, the image processing required is simple, and an accurate asteroid model is not required. The horizon-based navigation is similar to landmark navigation, but it compares the asteroid shape and dimension as seen in the images with an asteroid model Owen (2011). The correlation between the two yield an

<!-- PDF_PAGE: 28 -->


![figure_018.png](figure_018.png)



<div align="center">

Figure 14: Achievable velocity knowledge in the transfer phase

</div>

information about the relative position and pose of Milani at a very high computational cost, and an accurate asteroid shape model is required. We performed a trade-off analysis to select the most suitable method and the centroiding with disk fitting resulted as the most promising one for optical navigation owing to its accuracy, robustness, simplicity, and independency from the asteroid model knowledge. Thus, a navigation strategy exploiting the centroiding technique with disk fitting is baselined for navigation. During the occultation periods of the secondary by the primary body or shadow, the navigation strategy will still be robust, as Milani could either use ISL range and range-rate measurements or use Didymos visual images (provided that the navigation NavCam field-of-view will be able to image Didymos fully within the frame) or relying on on-board propagation to avoid losing the tracking of the system. However, since the shape of the asteroids and their features are not known, the centroiding method with a disk fitting has been chosen as the baseline for optical navigation. In order to assure accuracy, observability of the whole system, coverage, and efficiency of operations, the navigation strategy uses a different navigation camera which has

<!-- PDF_PAGE: 29 -->


![figure_019.png](figure_019.png)



<div align="center">

(a)

</div>


![figure_020.png](figure_020.png)



<div align="center">

(b)

</div>

<div align="center">

Figure 15: (a) Navigation cost probability distribution function for transfer phase. On the y-axis the number of occurrences are shown. (b) Navigation cost cumulative distribution function for transfer phase.

</div>

a larger field-of-view and higher resolution than ASPECT. In this way, while performing scientific operations, it is still possible to acquire navigation information. Moreover, a separated wide-angle camera (WAC) is foreseen to grant the full system visibility at any time. Thus, the adopted strategy for optical navigation exploits the same target of the scientific investigation with a navigation camera but keeps the observability of the two asteroids with a small ultra-wide angle camera. In this way, the pointing is shared among science and navigation, the navigation observables are accurate because the navigation camera is dedicated to the asteroid, and the full binary system view is assured owing to the ultra-wide angle camera. This strategy is also beneficial during the safe mode and targets acquisition mode. The parameters of the navigation cameras are reported in Table 5. Due to the early stage of the design process, the GNC baseline has not been established yet in terms of hardware components. The values in Table 5 are assumed based on typical performance of similar sensors, and do not refer to any existing camera. A representative image of the Didymos system with the three different cameras (ASPECT, NavCam, and WAC) is shown in Figure 16.

<!-- PDF_PAGE: 30 -->

<div align="center">

Table 5: Navigation camera characteristics.

</div>

<table border="1"><tr><td>Camera</td><td>FOV</td><td>Sensor</td></tr><tr><td>NavCam</td><td>21x16deg</td><td>2048x1536pix</td></tr><tr><td>WAC</td><td>40x40deg</td><td>2048x2048pix</td></tr></table>


![figure_021.png](figure_021.png)



<div align="center">

Figure 16: The external frame represents the FOV of the WAC, the medium frame represents the FOV of the NavCam, while the small asteroid is included in the small ASPECT field-of view. The distance at which this image is simulated is about 8.5 km from Didymos.

</div>

## 4.4.2. Optical Navigation Model and Methods

The image processing steps and the optical navigation method are described in this paragraph. The image, generated according to the CubeSat trajectory, pointing, and navcam specifications, is retrieved by Celestial Objects Rendering Tool (CORTO), which is a tool developed at Politecnico di Milano (Figure 17, step 1). The image is pre-processed to compute a mean background noise which is subtracted from the image, and the image is thresholded to highlight the bright objects in the frame (Figure 17, step 2). In this way, it is straightforward to identify the two groups of connected pixels belonging to D1 and D2, which can be bounded by a green box (Figure 17, step 3).

The center of brightness of each object can be easily computed by determining the centroid of the illuminated pixels inside the green boxes (Figure 18, step 4). The principal axes of each object can be determined, one of this axis will be

<!-- PDF_PAGE: 31 -->


![figure_022.png](figure_022.png)



<div align="center">

Figure 17: Steps 1-3; Image acquisition, pre-processing, and objects detection.

</div>


![figure_023.png](figure_023.png)



<div align="center">

Figure 18: Steps 4-6; Center of brightness (blue dot), center of mass (red dot), light direction and lit edge estimations.

</div>

aligned with the light direction while the other in the direction orthogonal to it. In this way, the axis of the light direction can be estimated from the images but it can be also complemented by the sun sensor information (Figure 18, step 5). The center of mass can be then estimated as a displacement of the center of brightness along the negative light direction. The displacement between the center of brightness and the center of mass is inversely proportional to the object phase angle (Figure 18, step 5). The image is then scanned along the light direction to identify the pixels belonging to the lit edge of each body (Figure 18, step 6).

Owing to the estimations of both the center of mass and the lit edge of each object in the images, a mean radius in pixels can be estimated from the center of mass to the pixels constituting the lit edge. In this way a disk is fitted to the object (Figure 19, step 7 for D1 and step 8 for D2). The center of mass, the center of brightness, and the dimensions of the two objects are the outputs that can be extracted from the image processing algorithm.

<!-- PDF_PAGE: 32 -->


![figure_024.png](figure_024.png)



<div align="center">

Figure 19: Steps 7-9; D1 disk fitting and D2 disks fitting.

</div>

## 4.4.3. Image Processing Accuracy

The optical navigation method accuracy is evaluated by processing 150 images randomly chosen from the nominal orbit. The procedure extracts navigation information from the figures in a static way, thus no dynamic filtering is used in this preliminary phase. The image processing steps extract the information on the centroid of D1 and the apparent disk size. This information are given in pixels and are compared to the actual ones to assess the errors involved with the image processing. Figure 20 shows the mentioned errors, where the x and y directions are the horizontal and vertical pixel coordinates and COM refers to the center of mass. The error in the centroiding has a 3 $ \sigma $ std lower than 10 pixels, while the error in the disk radius estimation has a 3 $ \sigma $ std lower than 20 pixels.

The NavCam has a 21 $ \times $16 deg FOV and a 2048 $ \times $1536 pixels detector. Thus, since every pixel spans 0.0103 deg, the worst case centroiding error is 0.103 deg. This is equivalent to a lateral error of 12.5 m at a distance of 7 km, and a lateral error of 17.9 m at a distance of 10 km. The worst case pixel radius error is 20 pixels (equivalent to a 0.2051 deg error). This is equivalent to a range error of 423.8 m at true distance of 7 km, and to a range error of 841.9 m at a true distance of 10 km. Thus, the worst case range error coming from the image processing is lower than the 10% of the true range. The error might be still reduced by developing an on-board optical navigation filter.

<!-- PDF_PAGE: 33 -->


![figure_025.png](figure_025.png)




![figure_026.png](figure_026.png)




![figure_027.png](figure_027.png)



<div align="center">

Figure 20: Center of mass error in horizontal and vertical pixel directions x and y and radius error as output of the image processing.

</div>

## 4.5. Control

Milani's nominal control architecture is expected to be based on traditional methods. However, because of the unique operations of Milani, in concert with other spacecraft (Hera and Juventas) and the risk of collision with either of the asteroids, particular care is involved in the design of the Corrective Action Maneuver (CAM) strategy. The CAM is a semi-autonomous contingency maneuver which is executable during nominal operations, in this section the strategy involved in the evaluation, quantification and execution of the maneu-

<!-- PDF_PAGE: 34 -->


![figure_028.png](figure_028.png)



<div align="center">

Figure 21: High-level architecture of the CAM strategy.

</div>

ver is explained.

During operations Milani will be sharing the most valuable space around Didymos system with Juventas and Hera. To ensure safe operations, the CubeSat shall be capable to avoid collisions with the surrounding bodies. The safety of Milani starts at mission analysis level with the design of trajectories that nominally do not encroach with the spacecraft and asteroids. However, a high-level strategy for the CAM is designed for unsafe deviations from nominal operations. Its schematics is shown in Figure 21. It is desirable to avoid both collisions with the spacecraft and with the asteroids. However, it is also important to distinguish between these two different events. The happening of the first one would produce the loss of multiple systems, while the latter would involve Milani. The collision risk can be assessed directly with the ISL range and range-rate capabilities for the spacecraft (Hera and Juventas, both active systems) while a combination of visual images from the NavCam and ISL data can be used with the asteroids (Didymos and Dimorphos, both passive systems).

The triggering mechanism of the CAM mode is based on the concept of risk ranges, that are simply the estimated ranges from the spacecraft and the asteroids. Whenever these quantities go below a certain threshold, a correction maneuver is considered necessary. Figure 22 shows the risk ranges associated to Hera, Juventas and the Didymos system. Their evolution in time is describing

<!-- PDF_PAGE: 35 -->


![figure_029.png](figure_029.png)




![figure_030.png](figure_030.png)



<div align="center">

Figure 22: Example of risk tubes during the science phase of Milani mission. The trajectories of Hera (black rectangle), Juventas (inner magenta circle) and Milani (blue) are represented in the Didymos Equatorial reference frame. The risk tubes for Hera and Juventas are represented with radius respectively of 1 km and 500 m. A contingency spherical region of risk is assumed for Didymos with a radius of 1.5 km.

</div>

risk tubes.

Once a corrective maneuver is requested, its orientation and magnitude are computed. The strategy to do that on-board is based on an hybrid between a generic and a specific look-up tables. The generic one contains only the magnitude of the maneuvers as a function of the range of Milani from the colliding object. The delta-V vector of the maneuver is directed towards the local radial direction of Milani's osculating orbit, opposite to the asteroid system. These maneuvers are pre-computed on ground based on the dynamic environment of the asteroid in such a way to ensure Milani will get further away but will not escape the system before a certain amount of days to be specified. The specific one contains pre-computed maneuvers both in magnitude and direction that are evaluated with a certain timespan on the nominal trajectory. The specific one are more accurate and can be relevant for small deviations from the nominal trajectory, the generic one are less accurate but are designed to cover the entire space around the colliding objects.

<!-- PDF_PAGE: 36 -->

## 5. Payload operations

In this section a detailed analysis of payload operations during the scientific phase of the mission is illustrated. In particular, we only focus on ASPECT operations, which is the only payload that impose observational requirements to the mission profile. The driving requirements are in terms of phase angle and resolution. Together with resulting distances, these are summarized in Table 2 and Table 3.

A science orbit cycle of 21 days is considered in the analysis to assess the capability to fulfill the payload objective to produce global maps of the asteroids. The time intervals within this cycle in which the constraints on the phase angle, distance and resolution are simultaneously satisfied are considered for potential observations.

Further pruning is performed by assessing the illumination condition and viewing geometry of each individual face of the asteroid shape models. Shadowing effect of Didymos on Dimorphos are also taken into account. Considering all these factors, it is estimated that a total cumulative time of 4.7 and 4.6 days are available to perform scientific observations of, respectively, Didymos and Dimorphos. There are however regions in both bodies near the south poles that will be permanently in shadow during the mission. These cannot be observed by ASPECT using visual imaging and are not caused by the choice of Milani trajectories, and therefore are not accounted in the evaluation of the global coverage.

Figure 23 and Figure 24 illustrate the faces that can be imaged during the potential observation periods. In bot cases global coverage can be achieved with the trajectory chosen. It is also estimated that a minimum number of 4 images timed at the proper epochs will be needed for each body to achieve global coverage. The areas covered by them is illustrated in Figure 25 and Figure 26.

This analysis is valid assuming ideal pointing and that the target body is entirely within the FOV of ASPECT. If the latter case is not true, especially in the case

<!-- PDF_PAGE: 37 -->


![figure_031.png](figure_031.png)



<div align="center">

Figure 23: ASPECT potential global coverage on Didymos. The map represents which faces of the shape model can be imaged by the payload given that the observation requirements are satisfied. The color of each face represents the minimum angle between the ASPECT line of sight and the face local normal during the science orbit cycle.

</div>


![figure_032.png](figure_032.png)



<div align="center">

Figure 24: ASPECT potential global coverage on Dimorphos. The map represents which faces of the shape model can be imaged by the payload given that the observation requirements are satisfied. The color of each face represents the minimum angle between the ASPECT line of sight and the face local normal during the science orbit cycle.

</div>

<!-- PDF_PAGE: 38 -->


![figure_033.png](figure_033.png)



<div align="center">

Figure 25: Simulation of an image acquisition sequence to achieve global coverage on Didymos. The colors represent the areas of the shape model covered by each image in a sequential order. Global coverage on the visible faces can be achieved with 4 images.

</div>


![figure_034.png](figure_034.png)



<div align="center">

Figure 26: Simulation of an image acquisition sequence to achieve global coverage on Dimorphos. The colors represent the areas of the shape model covered by each image in a sequential order. Global coverage on the visible faces can be achieved with 4 images.

</div>

<!-- PDF_PAGE: 39 -->


![figure_035.png](figure_035.png)



<div align="center">

Figure 27: Schematic of the angle used as metric to color the faces of the shape models in Figure 23 and Figure 24. The angle is the one between the line of sight vector from the face center to ASPECT (cyan) and the local normal of each face (black).

</div>

of Didymos, a mosaic strategy is proposed. As far as the scientific orbit is concerned, there seems to be plenty of opportunities in terms of observation time to acquire a higher number of images. The bottle-neck in this case might be given by the overall data budget, which is expected in the range of few Gbits.

## 6. Conclusion

The paper presents the preliminary mission profile of Hera's Milani CubeSat, during its operational lifetime after release in the proximity of Didymos binary asteroid system. We provide a detailed analysis of the feasibility of such mission, given the constraints arising from Hera mission scenario. We discuss the challenges and driving design criteria in terms of mission analysis, trajectory design and GNC design. Finally, we provide a preliminary design solution, consistent with mission objectives and demonstrate its feasibility and suitability in meeting science and technological obejctives of the Milani CubeSat mission. Although the preliminary mission profile suggests feasibility against the imposed requirements and constraints, the initial results presented in this paper will be subject to changes as the Milani mission project evolves.

<!-- PDF_PAGE: 40 -->

## Acknowledgement

This work has been performed in response to ESA call AO/1-10258/20/NL/GLC: Hera Mission "Second CubeSat" Phase A/B C/D & E1. Fabio Ferrari acknowledge funding from the European Union's Horizon 2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No. 800060. Mattia Pugliatti and Francesco Topputo acknowledge funding from the European Union's Horizon 2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement no. 813644. The authors would like to acknowledge the support received by the whole Milani Team.

## References

Capannolo, A., Ferrari, F., and Lavagna, M. (2019). Families of bounded orbits near binary asteroid 65803 didymos. Journal of Guidance, Control, and Dynamics, 42(1):189-198. DOI: 10.2514/1.G003437.

Capannolo, A., Lavagna, M., Ferrari, F., and Lunghi, P. (2016). Nanosatellite formation flying to enhance science in binary asteroid environment. In Proceedings of 65th International Astronautical Congress.

Çelik, O. and Sánchez, J. P. (2017). Opportunities for ballistic soft landing in binary asteroids. Journal of Guidance, Control, and Dynamics, 40(6):13901402. DOI: 10.2514/1.G002181.

Çelik, O., Sánchez, J. P., Karatekin, Ö., and Ritter, B. (2019). A comparative reliability analysis of ballistic deployments on binary asteroids. Acta Astronautica, 156:308-316. DOI: 10.1016/j.actaastro.2018.03.020.

Cheng, A., Atchison, J., Kantsiper, B., et al. (2015). Asteroid impact and deflection assessment mission. Acta Astronautica, 115(Supplement C):262- 269. DOI: 10.1016/j.actaastro.2015.05.021.

<!-- PDF_PAGE: 41 -->

Cheng, A. F., Rivkin, A. S., Michel, P., et al. (2018). AIDA DART asteroid deflection test: Planetary defense and science objectives. Planetary and Space Science, 157:104-115. DOI: 10.1016/j.pss.2018.02.015.

de Santayana, R. and Lauer, M. (2015). Optical measurements for rosetta navigation near the comet. In Proceedings of the 25th International Symposium on Space Flight Dynamics (ISSFD), Munich.

Dei Tos, D. A., Rasotto, M., Renk, F., and Topputo, F. (2019). Lisa pathfinder mission extension: A feasibility analysis. Advances in Space Research, 63(12):3863-3883. DOI: 10.1016/j.asr.2019.02.035.

Dell'Elce, L., Baresi, N., Naidu, S., Benner, L., and Scheeres, D. (2017). Numerical investigation of the dynamical environment of 65803 didymos. Advances in Space Research, 59(5):1304-1320. DOI: 10.1016/j.asr.2016.12.018.

Dirri, F., Palomba, E., Longobardo, A., et al. (2018). VISTA instrument: A PCM-based sensor for organics and volatiles characterization by using thermogravimetric technique. In 2018 5th IEEE International Workshop on Metrology for AeroSpace (MetroAeroSpace). IEEE. DOI: 10.1109/metroaerospace.2018.8453532.

Ferrari, F. and Lavagna, M. (2016). Consolidated phase a design of asteroid impact mission: Mascot-2 landing on binary asteroid didymos. Advances in the Astronautical Sciences, 158:3759-3769.

Ferrari, F. and Lavagna, M. (2018). Ballistic landing design on binary asteroids: The aim case study. Advances in Space Research, 62(8):2245-2260. DOI: 10.1016/j.asr.2017.11.033.

Ferrari, F., Lavagna, M., and Howell, K. C. (2014). Trajectory design about binary asteroids through coupled three-body problems. Advances in the Astronautical Sciences, 152:2093-2110.

<!-- PDF_PAGE: 42 -->

Ferrari, F., Lavagna, M., and Howell, K. C. (2016). Dynamical model of binary asteroid systems through patched three-body problems. Celestial Mechanics and Dynamical Astronomy, 125(4):413-433. DOI: 10.1007/s10569-016-9688-x.

Franzese, V., Di Lizia, P., and Topputo, F. (2019). Autonomous optical navigation for the lunar meteoroid impacts observer. Journal of Guidance, Control, and Dynamics, 42(7):1579-1586. DOI: 10.2514/1.G003999.

Freeman, A. (2020). Exploring our solar system with CubeSats and SmallSats: the dawn of a new era. CEAS Space Journal. DOI: 10.1007/s12567-02000298-5.

Gil-Fernandez, J. and Ortega-Hernando, G. (2018). Autonomous vision-based navigation for proximity operations around binary asteroids. CEAS Space Journal, 10(2):287-294. DOI: 10.1007/s12567-018-0197-5.

Karatekin, O., Goldberg, H., Prioroc, C.-L., Villa, V., and Juventas Team (2019). Juventas: Exploration of a binary asteroid system with a cubesat. In Proceedings of the International Astronautical Congress, IAC, volume 2019 October.

Kohout, T., Näsilä, A., Tikka, T., et al. (2018). Feasibility of asteroid exploration using cubesats—aspect case study. Advances in Space Research, 62(8):2239-2244. DOI: 10.1016/j.asr.2017.07.036.

Lange, C., Biele, J., Ulamec, S., et al. (2018). MASCOT2 - a small body lander to investigate the interior of 65803 didymos moon in the frame of the AIDA/AIM mission. Acta Astronautica, 149:25-34. DOI: 10.1016/j.actaastro.2018.05.013.

Lasagni Manghi, R., Modenini, D., Zannoni, M., and Tortora, P. (2018). Preliminary orbital analysis for a cubesat mission to the didymos binary asteroid system. Advances in Space Research, 62(8):2290-2305. DOI: 10.1016/j.asr.2017.12.014.

<!-- PDF_PAGE: 43 -->

Lockett, T. R., Castillo-Rogez, J., Johnson, L., et al. (2020). Near-earth asteroid scout flight mission. IEEE Aerospace and Electronic Systems Magazine, 35(3):20-29. DOI: 10.1109/maes.2019.2958729.

Michel, P., Kueppers, M., Sierks, H., et al. (2018). European component of the AIDA mission to a binary asteroid: Characterization and interpretation of the impact of the DART mission. Advances in Space Research, 62(8):2261-2272. DOI: 10.1016/j.asr.2017.12.020.

Owen, W. M. J. (2011). Methods of optical navigation. In AAS Spaceflight Mechanics Conference, New Orleans, Louisiana.

Park, R. S. and Scheeres, D. J. (2006). Nonlinear mapping of gaussian statistics: theory and applications to spacecraft trajectory design. Journal of guidance, Control, and Dynamics, 29(6):1367-1375. DOI: 10.2514/1.20177.

Perez, F., Modenini, D., Vázquez, A., et al. (2018). DustCube, a nanosatellite mission to binary asteroid 65803 didymos as part of the ESA AIM mission. Advances in Space Research, 62(12):3335-3356. DOI: 10.1016/j.asr.2018.06.019.

Schutz, B., Tapley, B., and Born, G. H. (2004). Statistical orbit determination. Elsevier.

Speretta, S., Cervone, A., Sundaramoorthy, P., et al. (2019). LUMIO: An Autonomous CubeSat for Lunar Exploration, pages 103-134. Springer International Publishing. DOI: 10.1007/978-3-030-11536-4_6.

Tardivel, S. (2016). Optimization of the ballistic deployment to the secondary of a binary asteroid. Journal of Guidance, Control, and Dynamics, 39(12):27902798. DOI: 10.2514/1.g000593.

Tardivel, S. and Scheeres, D. J. (2013). Ballistic deployment of science packages on binary asteroids. Journal of Guidance, Control, and Dynamics, 36(3):700709. DOI: 10.2514/1.59106.

<!-- PDF_PAGE: 44 -->

Topputo, F., Wang, Y., Giordano, C., et al. (2020). Envelop of reachable asteroids by m-argo cubesat. Advances in Space Research (under review).

Tsuda, Y., Saiki, T., Terui, F., et al. (2020). Hayabusa2 mission status: Landing, roving and cratering on asteroid ryugu. Acta Astronautica, 171:42-54. DOI: 10.1016/j.actaastro.2020.02.035.

Ulamec, S., Biele, J., Bousquet, P.-W., et al. (2014). Landing on small bodies: From the rosetta lander to mascot and beyond. Acta Astronautica, 93:460466. DOI: 10.1016/j.actaastro.2013.02.007.

Van wal, S., Tsuda, Y., Yoshikawa, K., et al. (2018). Prearrival deployment analysis of rovers on hayabusa2 asteroid explorer. Journal of Spacecraft and Rockets, 55(4):797-817. DOI: 10.2514/1.a34157.

Veverka, J., Farquhar, B., Robinson, M., et al. (2001). The landing of the near-shoemaker spacecraft on asteroid 433 eros. Nature, 413:390-393. DOI: 10.1038/35096507.

Walker, R., Binns, D., Bramanti, C., et al. (2018). Deep-space cubesats: thinking inside the box. Astronomy & Geophysics, 59(5). DOI: 10.1093/astrogeo/aty237.