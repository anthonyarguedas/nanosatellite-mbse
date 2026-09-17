---
source: null
title: "review-candidate-1433"
page_count: 15
converted_at: "2026-09-06T01:07:56Z"
---

<!-- PDF_PAGE: 1 -->

IAC-17-A7.2.2

<div align="center">

# The Australian Space Eye: Studying the History of Galaxy Formation with a CubeSat

</div>

Anthony Horton $ ^{a,*} $ , Lee Spitler $ ^{a,b} $ , Naomi Mathers $ ^{c} $ , Michael Petkovic $ ^{d} $ , Douglas Griffin $ ^{e} $ , Simon Barraclough $ ^{e} $ Craig Benson $ ^{e} $ , Igor Dimitrijevic $ ^{e} $ , Andrew Lambert $ ^{e} $ , Anthony Previte $ ^{f} $ , John Bowen $ ^{f} $ , Solomon Westerman $ ^{f} $ Jordi Puig-Suari $ ^{f,g} $ , Sam Reisenfeld $ ^{h} $ , Jon Lawrence $ ^{a} $ , Ross Zhelem $ ^{a} $ , Matthew Colless $ ^{c} $ , Russell Boyce $ ^{d} $

$ ^{a} $Australian Astronomical Observatory,105 Delhi Road, North Ryde NSW 2113, Australia $ ^{b} $Department of Physics & Astronomy, Macquarie University, North Ryde NSW 2109, Australia $ ^{c} $Space Industry Association of Australia Limited, ACN 613 961 005, c/- Nova Systems, 27-31 London Road, Mile End SA 5031, Australia

$ ^{d} $ Research School of Astronomy & Astrophysics, Australian National University, Cotter Road, Weston Creek ACT 2611, Australia

$ ^{e} $ School of Engineering & IT, UNSW Canberra, Northcott Drive, Campbell ACT 2600, Australia $ ^{f} $ Tyvak Inc., 15265 Alton Parkway, Suite 200, Irvine, CA 92618, USA

$ ^{g} $Aerospace Engineering Department, California Polytechnic State University, 1 Grand Avenue, San Luis Obispo, CA 93407, USA

$ ^{h} $ Department of Engineering, Macquarie University, North Ryde NSW 2109, Australia $ ^{*} $ Corresponding author, anthony.horton@aao.gov.au

## Abstract

The Australian Space Eye is a proposed astronomical telescope based on a 6U CubeSat platform. The Space Eye will exploit the low level of systematic errors achievable with a small space based telescope to enable high accuracy measurements of the Cosmic Infrared Background (CIB) and low surface brightness emission around nearby galaxies. To date absolute measurements of the CIB have proven elusive; the variability of atmospheric emission and scattering at these wavelengths make ground based measurements difficult while attempts to use sounding rockets have struggled to accumulate sufficient exposure time. An dedicated orbital telescope is required for a robust measurement, and Space Eye has been designed to fill this role. The scientific payload of Space Eye is a 90 mm diameter, clear aperture, all refractive telescope for wide field imaging using a set of 6 broadband filters in the $ i^{\prime} $ (700-850 nm) and $ z^{\prime} $ (850- 1000 nm) bands. The telescope design is optimised to minimise all sources of stray light which, when combined with the advantages of the space environment, will enable the most accurate measurements of the CIB so far. This project is also a demonstrator for several technologies with general applicability to astronomical observations from nanosatellites, in particular arcsecond level instrument pointing stability and efficient image sensor temperature control. These crucial capabilities are commonplace in larger scientific satellites but have yet to be flight proven in a CubeSat platform. For the former we have developed a two stage ADCS concept combining high precision star trackers, reaction wheels, and sensor shift image stabilisation in the science instrument focal plane. Detailed system modelling, incorporating in flight performance data for many of the components, has verified that the design can achieve sub-arcsecond level pointing stability. We have also designed a thermal control system and concept of operations that enables passive cooling of the image sensor to below $ -40^{\circ} \mathrm{C} $ despite a thermally unfavourable low Earth orbit.

Keywords: Space telescope, nanosatellite, CubeSat, extragalactic background, low surface brightness

## 1. Introduction

In December 2014 the Advanced Instrumentation Technology Centre at the Australian National University hosted the AstroSats 2014 workshop. The workshop was held to explore concepts for astronomical nanosatellite missions, with the goal of identifying viable missions that could be funded within existing Australian grant schemes. Concepts were required to be justifiable by the expected scientific results alone, i.e. without reference to the development

of technology or accumulation of expertise, valuable as those outcomes would be. Additionally proposed spacecraft were to be no larger than a 6 U CubeSat. The Australian Space Eye was conceived in response to this call for proposals.

Meeting the combination of scientific value, cost and size constraints is very challenging, essentially it means identifying a compelling science programme that is within the capabilities of a very small instrument in low earth or-

<!-- PDF_PAGE: 2 -->

bit but which could not be done with (much larger) ground based instruments for comparable cost. The two most well known benefits of situating an astronomical telescope above the Earth's atmosphere are accessing wavelengths that are absorbed by the Earth's atmosphere and avoiding the degradation of spatial resolution caused by atmospheric turbulence. Neither of these are of great relevance to an astronomical CubeSat however, at least one conceived within the AstroSats constraints. The gamma ray, X-ray, far ultraviolet and infrared wavelength regions all require exotic optics and/or image sensors which are not compatible with the cost, volume, thermal and power limitations imposed on us. For this reason we limited our consideration to the near ultravoilet to very near infrared wavelength region （ $ \sim 2 0 0-1 0 0 0 $ nm) that is accessible with silicon based image sensors and conventional optics. Within this wavelength range there is no spatial resolution advantage to being above the Earth's atmosphere either, the fundamental diffraction limit of a CubeSat sized telescope aperture （ $ \lesssim 9 0 $ mm diameter) is greater than atmospheric seeing at the same wavelengths.

There are however two other effects of the atmosphere which are relevant to a CubeSat based optical telescope: atmospheric scattering and emission. Atmospheric scattering spreads the light from astronomical objects in a similar way to scattering from the instrument's optics however the impact is compounded by the fact that the distribution of aerosols in the atmosphere is spatially and temporally variable. The amount of scattered light surrounding a given source can vary by several percent of the source brightness even in good 'photometric' conditions, on timescales of minutes to months. The variability in the scattering makes it difficult to accurately characterise and subtract [1] thereby introducing problematic systematic errors. Similar issues arise from atmospheric emission, particularly at longer wavelengths (> 700 nm). Here the atmosphere glows increasingly brightly, primarily due to line emission from OH $ ^{*} $ molecules in the mesosphere, reducing the sensitivity of ground based telescopes. This emission is sensitive to dynamic processes in the upper atmosphere (e.g. gravity waves) and consequently it is also spatially and temporally variable on timescales of minutes and longer [2] which makes accurate subtraction difficult. As a result of these effects locating a telescope in space not only helpfully reduces both scattered light and sky background levels but crucially makes both far more stable. Above the atmosphere the only sources of scattered light are associated with the instrument itself and the dominant source of sky background is the Zodiacal Light [3] which, while it does exhibit large scale spatial and seasonal variations, is much less variable, more uniform and more predictable than atmospheric emission.

The scientific competitiveness of small telescope for certain types of observations is well proven. For example while large astronomical telescopes are able to detect extremely faint compact or point-like objects their sensitivity to diffuse emission is limited by systematic errors from a number of sources. A significant contribution to these systematic errors is contamination with light from brighter objects within/near the instrument's field of view, caused by a combination of diffraction, scattered light and internal reflections. The difficulties caused by these effects have been discussed by, for example, Sandin [4, 5] and by Duc et al [6], who noted that the simpler optics of small telescopes suffer less from internal reflections. In addition small telescopes can more readily be constructed with unobscured apertures to minimise diffraction, and simpler optics also make them less prone to internal scattering of light. The resulting competitiveness of optimised small telescopes in the context of 'low surface brightness' (LSB) imaging has been demonstrated by the Dragonfly Telephoto Array, an astronomical imaging system based on an array of telephoto camera lenses [7]. This instrument exhibits less diffraction/scattering/internal reflections than other telescopes for which comparable data are available [4, 7] and the system has produced impressive results, including the discovery of a new class of 'ultra-diffuse galaxies'[8]. Two of this paper's authors (AJH & LS) are currently assembling a ground based instrument based on the same principles, the Huntsman Telephoto Array.

We conclude that a CubeSat based astronomical telescope may be scientifically competitive, especially an optimised telescope performing measurements that are typically limited by systematic errors. We identify the 700- 1000 nm wavelength region as particularly promising as it is accessible to instrumentation compatible with the constraints of a CubeSat mission while ground based instruments would be hampered by bright atmospheric emission, in terms of both reduced sensitivity and increased systematic errors. We have based the Australian Space Eye proposal on two primary science goals which would be well served by a telescope operating in this regime, the measurement of the Cosmic Infrared Background and mapping of the interplanetary dust cloud. These are discussed in more detail in the next section.

## 2. Science Case

## 2.1 Cosmic Infrared Background

Just as observations of the Cosmic Microwave Background all astronomers to directly see and therefore study the aftermath of the Big bang, the Cosmic Infrared Background (CIB) contains the entire integrated history of nearly everything that has happened since. The CIB directly probes all aspects of galaxy formation and evolution: as such it is a fundamental observable that anchors theories of galaxy formation and evolution.

To measure the CIB one must account for all foreground sources of diffuse light between the telescope and

<!-- PDF_PAGE: 3 -->

the CIB. Avoiding the bright and highly variable infrared flow of our atmosphere necessitates a space based telescope, and it must also be designed to minise stray light from the Sun, Earth and Moon. Modelling and subtracting contributions from starlight scattered by interstellar dust within the Milky Way can be done using existing high resolution maps (e.g. Schlafly et al., 2017[9]). The main challenge is accounting for zodiacal light, which comes from sunlight interacting with dust particles within the Solar System. This has proved very challenging (see Cooray 2016[10]), and while there have been several attempts to directly measure the CIB (e.g. Bernstein 2007, Aharonian et al. 2006 and Tsumura et al. 2010 [11-13]) no facility has been able to successfully measure and subtract the zodiacal light simultaneously with observations of the CIB. Space Eye will be the first facility to simultaneously monitor the zodiacal light and isolate the underlying CIB signal. In this way Space Eye will pin down models of galaxy evolution and reveal the role of extremely faint, but potentially very numerous, rest frame ultraviolet source in (re-)ionising hydrogen gas throughout the Universe[14].

The approach that Space Eye will use for disentangling the Zodiacal and cosmic light exploits spectral features of the former. As zodiacal light is scattered sunlight its spectrum is similar to that of the Sun, subject to reddening due to the wavelength dependence of the scattering strength[3,15,16]. This includes the strong Calcium triplet absorption lines near 860 nm, which will be present in the Zodiacal light spectrum with the same equivalent width as in the solar spectrum but will be absent from the spectrum of the CIB due to the effects of cosmological redshifts. Consequently the observed equivalent width of absorption lines in the total background light (Zodiacal plus cosmic) provided a measure of the relative contributions of the two components. This was the goal of one of the instruments of the CIBER sounding rocket experiment[17], a narrowband imaging spectrometer based on a tilted objective filter[18], however the measurement proved extremely difficult to make with the limited total exposure time of a sounding rocket campaign. An orbital space telescope, able to accumulate a year or more of observing time, promises secure measurements of both the absolute total sky brightness and the relative contributions of the Zodiacal light and extragalactic background.

## 2.2 Interplanetary dust

By measuring the zodiacal light for the CIB science goal we will also map the dust cloud that exists within the plane of the Solar System. The origin of this dust remains highly uncertain, with contradictory studies finding the dust originating from either asteroids or comets (e.g. Liou et al. 1995[19], Nesvorny et al. 2010 [20], Kawara et al. 2017[21]). The origin of the dust causing the zodiacal light provides constraints about important past events


![figure_001.png](figure_001.png)



<div align="center">

Fig. 1: Artist's impression of the Australian Space Eye in orbit over the Tasman Sea.

</div>

(e.g. the late heavy bombardment) and gives context to new observations of exoplanet systems with younger, hot dust disks (e.g. Nesvorny et al. 2010[20]). Zodiacal light measurements have the potential to resolve this mystery (Yang & Ishiguro 2015[22]), however previous observations were limited in their wavelength, temporal and/or spatial coverage. Space Eye will overcome these limitations to produce a detailed map of the Solar System's dust cloud, and thereby make a significant contribution to our understanding of the past history of the Solar System.

## 2.3 Coordinated observations with flagship observatories

The unique ability of Space Eye to isolate and measure both the CIB and zodiacal light complements the capabilities of the flagship James Webb Space Telescope (JWST). By observing fields that are simultaneously being observed with JWST Space Eye can provide additional constraints on the sky background for the JWST observations, thereby improving zodiacal light subtraction, enabling new science, and extending the wavelength coverage of CIB measurements from the Space Eye bands out to 15 $ \mu \mathrm{m} $

## 3. Space Eye Concept

The Australian Space Eye is a nano-satellite based on the 6 U CubeSat form factor standard[23] housing an optical imaging telescope. The specifications of the system are driven by the aims discussed in Sec. 2, subject to the constraints discussed in Sec. 1. An artist's impression of Space Eye is shown in Fig. 1.

## 3.1 Optical Payload

## 3.1.1 Requirements

The scientific goals described in Sec. 2 call for a wide field imaging instrument with moderate spatial resolution, an exceptionally 'clean' and stable point spread function (PSF), and the highest low light sensitivity achievable within the other constraints of the platform. The imager must be capable of both broadband imaging in the $ i^{\prime} $ and $ z^{\prime} $ bands (approximately 700-850 nm and 850-1000 nm re-

<!-- PDF_PAGE: 4 -->

spectively) as well as measurement of the strength of the Calcium absorption lines in the sky background spectrum.

The optical system is expected to occupy approximately 50% of the spacecraft internal volume. The optical axis will be aligned with the long axis of the spacecraft body and positioned on the centreline to assist with centre of mass positioning. The bulk of the optical payload is therefore confined to an approximately $ 3 0 0 \times1 0 0 \times1 0 0 \mathrm{~ m m} $ 3 U volume, however 1-2 U of the remaining 3 U of internal volume will be available for payload electronics. The largest practical optical aperture within these constraints is $ \sim9 0 \mathrm{~ m m} $ in diameter.

Considerations of cosmic variance, sky background gradients and the angular extents of galaxy groups/clusters result in a desire for a field of view at least $ 1^{\circ} $ across, preferably close to $ 2^{\circ} $ .

We have selected a image scale of $ 3^{\prime \prime} \mathrm{pixel}^{-1} $ , this is close to Nyquist sampling of the diffraction limited PSF at the Space Eye aperture size and operating wavelengths $ (1. 2 2 \lambda / D=2. 0^{\prime \prime}-2. 8^{\prime \prime}) $ . Coarser spatial sampling could increase the signal to noise ratio for diffuse sources however we avoid significant undersampling of the PSF due to the impact on the accuracy of PSF fitting and subsequent point source subtraction. With the selected image sensor (section 3.1.2) Space Eye can still be sky background noise limited at this pixel scale.

To accomplish the required measurements of both broadband $ i^{\prime} $ and $ z^{\prime} $ surface brightness and Calcium absorption we will use a set of 6 slightly modified $ i^{\prime} $ and $ z^{\prime} $ band filters with band edges positioned around the strong absorption line at 854.2 nm. More details are discussed in Sec. 3.1.4.

For Space Eye the requirement for a clean and stable PSF translates to minimising all sources of stray light, including surface and bulk scattering, internal reflections, stray sunlight/Earthshine/moonlight and diffraction.

The highest possible sensitivity will be achieved when the optical aperture is as large as it can be within the space constraints of the CubeSat, the optical throughput and quantum efficiency (QE) of the image sensor are close to 100% , and the total instrumental noise is below the Poisson noise from the sky background light.

## 3.1.2 Image sensor

The choice of image sensor is key, not only is it the biggest variable in determining the overall sensitivity of the system but the specifications for many of the other subsystems (optics, data handling, downlink capacity, thermal control, power, etc.) depend on the specifications of the sensor.

Astronomical instruments operating at these wavelengths typically use charge-coupled device (CCD) image sensors however for Space Eye we have selected the CIS115 CMOS image sensor from e2v[24]. The CIS115


![figure_002.png](figure_002.png)



<div align="center">

Fig. 2: Predicted CIS115 quantum efficiency as a function of wavelength at both $ 2 0^{\circ} \mathrm{C} $ and $ - 4 0^{\circ} \mathrm{C} $ , data from Soman et al.[25]

</div>


![figure_003.png](figure_003.png)



<div align="center">

Fig. 3: CIS115 dark current as a function of temperature based on the model from Wang et al. [26]

</div>

<!-- PDF_PAGE: 5 -->

<div align="center">

Table 1: Summary of main optical payload requirements

</div>

<table border="1"><tr><td>Field of view</td><td>＞1°(goal～2°)</td></tr><tr><td>Pixel scale</td><td>3&#x27;&#x27;pixel-1</td></tr><tr><td>Wavelength range</td><td>700-1000nm</td></tr><tr><td>Aperture diameter</td><td>90mm</td></tr><tr><td>Optical system dimensions</td><td>300×100×100mmmax</td></tr><tr><td>Payload electronics volume</td><td>&lt;2U</td></tr></table>

<div align="center">

Table 2: Summary of CIS115 specifications taken from draft datasheet dated December 2015. All performance values are 'typical'.

</div>

<table border="1"><tr><td>Number of pixels</td><td>2000×1504</td></tr><tr><td>Pixel size</td><td>7.0μm square</td></tr><tr><td>Quantum efficiency at 650nm</td><td>90%</td></tr><tr><td>Dark current</td><td>20e- pixel-1s-1at21℃</td></tr><tr><td>Read noise</td><td>5e- at6.2Mpixel s-1per channel</td></tr><tr><td>Well depth</td><td>27ke- pixel-1(linear),33ke- pixel-1(saturation)</td></tr><tr><td>Non-linearity</td><td>±4%</td></tr><tr><td>Operating temperature</td><td>-55℃-+60℃</td></tr><tr><td>Power consumption</td><td>~40mW</td></tr></table>

<!-- PDF_PAGE: 6 -->

is a back-side illuminated image sensor with $ 2 0 0 0 \times1 5 0 4 $ pixels on a 7 $ \mu m $ pitch. The main specifications, taken from the draft e2v datasheet, are given in Tab. 2.

The CIS115 is a new image sensor developed with space based scientific imaging in mind, in particular the ESA JUICE mission. In general its performance is close to that of back side illuminated CCD image sensors operated in inverted mode, the main difference being a 2-3 $ \times $ higher read noise when compared to the very best CCDs. CMOS image sensors offer a number of advantages for a CubeSat space telescope however, including lower power consumption and greater resistance to radiation induced damage than CCDs. Of particular importance to Space Eye is the relatively small pixel size, 7 $ \mu $m versus the 12-15 $ \mu $m of available scientific CCDs. This factor of 2 reduction in pixel size enables a corresponding reduction in the focal length of the optics required for a given on-sky pixel scale which has a significant impact on the design of the optics as discussed in the next section. An additional advantage is the ability to operate regions of the sensor independently of others, opening up the possibility of using small regions for high frame rate autoguiding/star tracking while simultaneously taking a long exposure with the rest of the sensor （'on-chip guiding'）.

Predicted quantum efficiency data for the CIS115 are plotted in Fig. 2. These data are reproduced from Soman et al.[25] and we regard them as conservative estimates, Wang et al.[26] report slightly higher peak QE from both their own and e2v's measurements of a prototype device (CIS107). The decline in QE for wavelengths greater than 700 nm is due to the increasing transparency of silicon at these wavelengths and is common to all silicon based image sensors. In this wavelength range only deep depletion or high rho CCDs offer significantly higher QE, due to the greater effective thickness of their photosensitive layer. We consider these devices unsuitable for Space Eye however as those currently available have large pixels and, more importantly, require deep cooling （< -100 $ ^{\circ} \mathrm{C} $ ）to control dark current due to their non-inverted operation. Deep depletion/high rho CMOS image sensors show promise however at the time of writing no devices suitable for Space Eye were known to the authors.

The dark current of the CIS107 prototype was measured by Wang et al. between $ + 2 7^{\circ} \mathrm{C} $ and $ - 2 3^{\circ} \mathrm{C} $ and they found the expected exponential temperature dependence, with a halving of dark current for every $ 6. 2^{\circ} \mathrm{C} $ drop. Their best fit model is shown in Fig. 3. The dark current of cooled production CIS115 image sensors may be somewhat lower, e2v's draft datasheet suggests a typical dark current that is $ \sim 50\% $ lower at $ 20^{\circ} \mathrm{C} $ that also falls more rapidly with cooling, halving with each $ 5. 5-6. 0^{\circ} \mathrm{C} $ temperature drop. Based on these data we confidently expect a dark current of $ \lesssim 0. 0 4 e^{-} $ pixel $ ^{-1} $ s $ ^{-1} $ at $ - 4 0^{\circ} \mathrm{C} $ . Wang et al. also note a helpful reduction in read noise on cooling,


![figure_004.png](figure_004.png)



<div align="center">

Fig. 4: Cross section optical layout diagram of the baseline design for the Australian Space Eye.

</div>


![figure_005.png](figure_005.png)



<div align="center">

Fig. 5: Ensquared energy as a function of half-width for the baseline optical design.

</div>

to approximately $ 4 e^{-} $

## 3.1.3 Telescope optics

The combination of the requirements from Tab.1 and the image sensor specifications from Tab.2 enable us to determine the remaining requirements for the telescope optics. The resulting specifications are summarised in Tab.3. The biggest consideration for the design of the Space Eye optics is minimising the wings of the PSF due to internal scattering, reflections and diffraction. For this reason we have decided to use an all refractive design. Abraham and van Dokkum[7] have argued that refractive designs have a fundamental advantage over reflecting or catadioptric telescopes in this respect, and comparisons of telescope PSF

<div align="center">

Table 3: Summary of telescope optics specifications

</div>

<table border="1"><tr><td>Field of view</td><td>1.67°×1.25°</td></tr><tr><td>Effective focal length</td><td>481mm</td></tr><tr><td>Aperture diameter</td><td>90mm</td></tr><tr><td>Focal ratio</td><td>f/5.34</td></tr><tr><td>Wavelength range</td><td>700-1000nm</td></tr><tr><td>Overall length</td><td>250mm</td></tr></table>

<!-- PDF_PAGE: 7 -->


![figure_006.png](figure_006.png)



<div align="center">

Fig. 6: Conceptual surface plots of simulated images showing how stray (scattered) light from each star is higher in conventional telescopes than in Space Eye. The accumulation of stray light from all the stars in a field limits access to the underlying Cosmic Infrared Background.

</div>

measurements by Sandin[4] appear to support this view. Note that the relatively small pixels of the CIS115 image sensor are essential to allow a refractive design to be used. With 3 $ ^{\prime\prime} $ pixel $ ^{-1} $ and 7 $ \mu $ m pixels the required effective focal length is about twice the length of the space available for the optics, necessitating a moderately telephoto design but not presenting any insuperable problems. With the larger pixels typical of back side illuminated CCDs the focal length would have to be approximately four times the length of the available space, in which case folded light path reflective or catadioptric designs would be the only practical options.

We have produced a baseline optical design for Space Eye which is illustrated in figure 4. The design consists of 6 elements in 4 groups with two $ \mathrm{C a F_{2}} $ elements (L2 and L3) and two aspheric surfaces (L3-S1 and L4-S1). Six elements were required to achieve the desired image quality within the overall length constraints however we are able to limit the number of vacuum-glass interfaces to 7 which will assist with minimising surface scattering and internal reflections/ghosting. The image quality is essentially diffraction limited across the full field of view, as confirmed by the ensquared energy plots in Fig. 5. The calculation was performed using the Huygens-Fresnel method with the Zemax OpticStudio software. The ensquared energies are polychromatic (700-1000 nm) and have been calculated for 5 field points at a range of positions from the centre to the corner of the field of view.

Bulk scattering will be minimised through the use of high purity, high homogeneity lens blanks. Super polishing and high performance anti-reflection coatings will be used to minimise surface scattering and internal reflections. We are pursuing the possibility of using nanostructured anti-reflection coatings (as employed in some high end DSLR lenses) for this purpose, these are capable


![figure_007.png](figure_007.png)



<div align="center">

Fig. 7: Example mosaic filter layout. Each filter covers an area of $ 3 3 3 \times3 7 6 $ pixel, $ 1 6. 7^{\prime}\times1 8. 8^{\prime} $ on sky.

</div>

of very low reflectivities for a wide range of wavelengths and angles of incidence. Internal knife-edge baffles will be used, along with an external deployable baffle designed to prevent illumination of the optics by sunlight, earthshine or moonlight during observations. A 700-1000 nm bandpass filter will be applied to the 1st lens surface. A full stray light analysis will be performed as part of a general review of the optical design when the project is confirmed however we are confident that we will be able to acheive the required clean and stable PSF.

The telescope will include a bistable optical shutter between the L5 and L6 elements to enable on orbit image sensor dark current measurements.

## 3.1.4 Mosaic filter

In order to provide the necessary data to allow both broadband $ i^{\prime} $ and $ z^{\prime} $ band imagery and seperate measurements of the Zodiacal light and extragalactic components of the sky background we propose the use of 6 broadband filters, 3 variants on the $ i^{\prime} $ filter and 3 variants on the $ z^{\prime} $ filter. Nominal transmission profiles for these filters are shown in Fig. 8, together with a model of the Zodiacal light photon spectral flux density. The filters differ in their red cutoff wavelength in the case of the $ i^{\prime} $ filters and their blue cutoff wavelength in the case of the $ z^{\prime} $ filters. The cutoffs are chosen to bracket the strongest of the Calcium triplet absorption lines (854.2 nm) as well as an adjacent region of continuum. The pairwise surface brightness differences between filters provide information on the relative strength of the Calcium absorption that can used together with sky background models to separate the Zodiacal light and extragalactic components. Meanwhile the sum of the 3 $ i^{\prime} $ or $ z^{\prime} $ band filters gives deep broadband data with effective filter response close to the standard $ i^{\prime} $ or $ z^{\prime} $ filter bands.

Multiband astronomical imaging is typically accomplished by taking full frame images through each individual filter sequentially, i.e. temporal multiplexing. This approach requires a set of full frame filters and some sort

<!-- PDF_PAGE: 8 -->


![figure_008.png](figure_008.png)



<div align="center">

Fig. 8: Nominal filter transmission profiles shown together with a model of the zodiacal light photon spectral flux density.

</div>


![figure_009.png](figure_009.png)



<div align="center">

Fig. 9: Predicted SNR relative to the SNR without instrumental noise for the i2 and z2 filters as a function sub-exposure time for a range of image sensor temperatures. The calculation uses the ecliptic pole zodical light surface brightness values.

</div>

of filter exchange mechanism, e.g. a filter wheel. For space based instruments, and especially those intended for nanosatellites, there are strong incentives to avoid introducing mechanisms if at all possible due to complexity, cost and potential for failure. Consequently we favour a spatial multiplexing based approach in which the field of view is divided up amongst the 6 different filters by a fixed mosaic filter at the focal plane, an example layout of which can be seen in Fig. 7. By taking sequences of 6 images with pointing offsets equal to the dimensions of the filter regions contiguous images can be built up for each filter.

## 3.1.5 Performance modelling

In order to determine appropriate operational parameters and predict the approximate sensitivity of Space Eye we have developed performance models for the optical payload. These are not full end-to-end simulations but are instead parametric models, suitable for efficiently exploring parameter space ahead of the more detailed analysis to follow.

As noted in Sec. 3.1.1 obtaining the maximum sensitivity for a fixed telescope aperture size requires both maximising the end-to-end efficiency (optical throughput and image sensor QE) and ensuring the instrumental noise sources do not add significantly to the fundamental Poisson noise of the light received from the sky, which at these wavelengths is predominantly Zodiacal light. For the purpose of these calculations we use a model for the zodiacal light based on that used by the Hubble Space Telescope Exposure Time Calculator[15]. The starting point is a solar spectrum from Colina, Bohlin and Castelli[27], to which we apply a normalisation, reddening and spatial depen-

<!-- PDF_PAGE: 9 -->


![figure_010.png](figure_010.png)



<div align="center">

Fig. 10: Predicted surface brightness spectral flux density corresponding to a signal to noise ratio of 1 per pixel as a function of total exposure time per filter. The calculcation is for the ecliptic pole Zodiacal light surface brightness, an image sensor temperature of $ - 4 0^{\circ} \mathrm{C} $ and sub-exposures of 600 s.

</div>

dency following the prescription of Leinert et al.[3] with the revised parameters from Aldering[16]. Using the aperture size, estimated optical throughput, filter transmission profiles, pixel scale and image sensor quantum efficiency we can predict the observed zodiacal light signal (in photoelectrons per second per pixel) and then, with the estimated image sensor dark current and read noise values, we can predict the signal to noise ratio (SNR). By comparing the predicted SNR with the value it would have in the absence of dark current and read noise we can quantify the degree to which instrumental noise is effecting sensitivity. The key results are summarised in Fig. 9, which shows the SNR relative to the SNR without instrumental noise for the i2 and z2 filters for a range of image sensor temperatures and sub-exposure time.

The calculation uses the zodiacal light model surface brightness values for the ecliptic poles, which are close to the minimum possible value and therefore place the most stringent demands on instrumental noise. Due primarily to the falling image sensor QE the $ z^{\prime} $ band is more sensitive to instrumental noise and drives the selection of operating parameters. Based on these results we have selected a nominal exposure time for individual science exposures of 600s and an image sensor operating temperature of $ -40^{\circ} \mathrm{C}. $

Using these parameters we then calculate the predicted sensitivity limit for Space Eye, specifically the source surface brightness spectral flux density that would correspond to a signal to noise of 1 per pixel, for each filter. This is plotted as a function of total exposure time in Fig. 10, with a horizontal scale that runs from 600 s

i' band relative sensitivity, NEP, March


![figure_011.png](figure_011.png)



i'band relative sensitivity, SEP, March


![figure_012.png](figure_012.png)




![figure_013.png](figure_013.png)




![figure_014.png](figure_014.png)




![figure_015.png](figure_015.png)




![figure_016.png](figure_016.png)



<div align="center">

i' band relative sensitivity, NEP, December

</div>


![figure_017.png](figure_017.png)



<div align="center">

i'band relative sensitivity, SEP, December

</div>


![figure_018.png](figure_018.png)



<div align="center">

Fig. 11: Predicted $ i^{\prime} $ band sensitivity relative to the ecliptic pole, zero extinction case. The maps show $ 4 5^{\circ}\times 4 5^{\circ} $ gnomonic projections centred on the north and south ecliptic poles in March, June, September and December, with a colourmap running from halved sensitivity (black) to full sensitivity (white). Equatorial coordinate grids are also shown, with 1 hour spacing in RA and $ 1 0^{\circ} $ in dec, as well as the outlines of the designated target regions.

</div>

<!-- PDF_PAGE: 10 -->

(i.e. a single exposure) to $ 2 \times1 0^{6} \mathrm{~ s} $ . The latter value corresponds to the approximate total exposure time per filter per celestial hemisphere for a 2 year duration mission, assuming the duty cycle discussed in Sec. 4.3. Of more relevance to the broadband imaging science goals, we have also calculated the predicted sensitivity limit from summing the 3 $ i^{\prime} $ and $ z^{\prime} $ filters. At the end of the 2 year mission we predict ultimate $ 1 \sigma $ per pixel sensitivity limits of $ 1.1 \times1 0^{-2 0} \mathrm{~ W m}^{-2} \mathrm{~ a r c s e c o n d}^{-2} \mu\mathrm{m}^{-1} $ and $ 1.9 \times1 0^{-2 0} \mathrm{~ W m}^{-2} \mathrm{~ a r c s e c o n d}^{-2} \mu\mathrm{m}^{-1} $ for $ i^{\prime} $ and $ z^{\prime} $ bands respectively, equivalent to 30.5 and 29.6 in AB magnitude surface brightness units.

The zodiacal light model includes spatial (and seasonal) variations, allowing us to calculate how the predicted sensitivity varies with position on the sky. For extragalactic sources, such as other galaxies and the CIB we must also take into account extinction by Galactic dust. For this we use the all sky dust reddening (E(B-V)) maps from the Planck Legacy Archive[28] and convert to extinctions at our filter wavlengths using the prescription of Fitzpatrick[29], with R=3.1. Fig 11 shows the resulting $ i^{\prime} $ band relative sensitivity maps for regions near the ecliptic poles at the times of the equinoxes and solstices. Due to the seasonal variation in Zodiacal light regions close to the north ecliptic pole are preferred from February to July, and close to the south ecliptic pole from August to January. The tightest constraints come the Galactic dust, in order to minimise its effects targets should be chosen from within regions between 15.5 and 16.5 hours Right Ascension and $ 5 5^{\circ} $ and $ 6 0^{\circ} $ declination in the north, and between 4 and 5 hours Right Ascension and $ - 5 0^{\circ} $ and $ - 6 0^{\circ} $ degrees declination in the south.

## 3.2 Spacecraft Bus

The Space Eye spacecraft bus will be based on the Tyvak Endeavour platform. This highly integrated, high performance platform incorporates almost all the systems required for a functional 3-12 U Cubesat, including Command and Data Handling (C & DH), Electrical Power System (EPS) and thermal management, Attitude Determination, Control and Navigation System (ADCNS), and structural and mechanical parts. In a typical configuration the avionics package, including battery modules, occupies approximately 1 U of volume. As noted in Sec. 3.1.1 the Space Eye telescope will occupy a 3 U volume leaving a final ~ 2 U of volume for other mission specific hardware, e.g. the image sensor control electronics, image sensor thermal control system (Sec. 3.2.2), image stabilisation system/ADCS 2nd stage (Sec. 3.2.1) and communication equipment.

An initial power budget analysis has indicated that Space Eye will require body mounted solar panels on the largest face of the spacecraft body plus 1 U wide deployable panels along both long edges, as shown schematically


![figure_019.png](figure_019.png)



<div align="center">

Fig. 12: Main components of the standard Tyvak Endeavour attitude determination and control system (ADCS). Space Eye's ADCS will be based on an updated Endeavour system.

</div>

in figure 1. Based on a preliminary analysis we believe that standard UHF telemetry/command and S-band downlink systems will be sufficient given the expected data rates (see section 4)[30].

## 3.2.1 Attitude determination & control

The main technical challenge for astronomical imaging from CubeSats is instrument pointing stability. Long exposures are required to prevent image sensor noise overwhelming the faint signals from the sky (see Sec. 3.1.5) and the instrument must be kept stable to within less than 1 pixel for the duration of the exposures to avoid blurring. For Space Eye the required exposure times are 600 s and 1 pixel corresponds to 3" , these requirements are well beyond the capabilities of any current commercially available CubeSat ADCS system. Improvements are required in both the attitude determination and attitude control aspects.

The standard Tyvak Endeavour main attitude determination system is based on a set of two orthogonal Tyvak developed star trackers and a three-axis MEMS gyro. These sensors are paired with a set of three Tyvak reaction wheels as primary attitude control actuators. The system also incorporates three magnetic torque coils for wheel desaturation and a set of sun sensors and magnetometers to provide coarse attitude determination. Attitude determination and control computations are performed on a dedicated processor on the Endeavor main board. Pointing stability of the Endeavour platform is primarily driven by rate noise from the gyroscope in the attitude control loop. Disturbances from the reaction wheels also contribute jitter to a lesser extent; however, reaction wheel induced jitter can be mitigated with placement and isolation. Modest software and firmware updates to the current Endeavour platform achieve 30" (3 sigma) stability in simulation.

<!-- PDF_PAGE: 11 -->

Tyvak has investigated several paths to achieve arcsecond level pointing stability with the Endeavour platform. The highest technology readiness level path for arcsecond level pointing of an imaging payload is a two-stage control system with piezoelectric actuators driving lateral translation of the focal plane assembly (FPA) in a high bandwidth second stage. The two-stage approach is well suited to CubeSats since it is orbit agnostic and CubeSat rideshares generally cannot select their orbit.

The piezoelectric second stage consists of the FPA (image sensor, interface board, mosaic filter and field flatener lens), piezoelectric actuators driving lateral translation of the FPA, a dedicated processor for calculating guide star centroids and performing control calculations, and the electrical and power system for the piezoelectric actuators.

Space Eye will use fine star tracking (autoguiding) in the main telescope focal plane to provide the precision pointing information required. Dedicated sensors adjacent to the main image sensor could be used however the CIS115 image sensor and its control electronics are capable of continuously reading out sub-regions of the image sensor for fine star tracking while the remainder of the sensor is simultaneously doing a long science exposure. A fraction of the science image is lost in this way however avoiding a dedicated set of fine star tracking sensors and associated control electronics reduces complexity considerably.

Preliminary design for the dual-stage controller indicates the control bandwidth of the piezoelectric second stage needs to be greater than 3.5 Hz with centroiding noise of less than 1". Control inputs (centroids from guide stars) need to be computed at roughly 20 Hz and with delay of no more than roughly 1 ms.

Specific piezoelectric actuators have not been analyzed however the required actuator throw is within COTS hardware capability. Significant work remains to refine guide star sensor selection, actuator selection, packaging, and the algorithms to drive the second stage control system.

## 3.2.2 Thermal control

Cooling the image sensor below the temperature where the dark current is a negligible contributor to the system radiometric noise budget (see Sec. 3.1.5) is both critical to the scientific performance of the mission as well as a very difficult engineering challenge within the resource constraints of a 6 U CubeSat spacecraft. In order to address the feasibility of achieving this requirement, a number of configurations of the spacecraft, attitude control strategies and Concept of Operations need to be assessed.

In order to cool the detector over an extended period of time a radiator needs to be integrated onto an external face of the spacecraft to reject heat to deep space. Through the orbit the radiator will in general be in radiative exchange with deep space, the Earth, the solar heat load from the direct view of the radiator to the Sun as well as the solar energy reflected from the Earth to the radiator (i.e. the Albedo heat load). The overall efficacy of a particular radiator design will then depend on the area, thermal conductivity and thermo-optical properties of the radiator as well as the relative geometry of the radiator surface to the Earth, Sun and any other appendages of the spacecraft. Ultimately, these geometric factors depend on the accommodation of the subsystems within the spacecraft, the attitude of the spacecraft, the season and the orbital parameters of the spacecraft and the location of the spacecraft in its orbit.

The most favorable orbit, from the point of view of thermal control of the detector radiator, is dawn-dusk Sun synchronous. In this orbit the detector radiator can be placed on the opposite side of the spacecraft to the main solar array. has a very good view factor towards deep space and is protected from direct solar illumination. There are several drawbacks of baselining this orbit which makes it unattractive from the mission level perspective. Firstly, only a relatively small minority of CubeSat launches are dawn-dusk and therefore adopting it involves a risk of incurring a significant programmatic delay to wait for a suitable launch opportunity. Secondly, due to the fact that the sequencing of the deployments of the primary and secondary payloads is planned to optimize the orbital parameters of the primary payload, there is generally an injection error of the CubeSat with respect to a fully sun synchronous orbit. Finally, without a propulsion system, as the orbit decays it will drift further and further away from the ideal orbit and compromise the thermal performance. In the light of these considerations it was decided to abandon the dawn-dusk sun-synchronous orbit approach and consider Sun-synchronous orbits with a Local time of the Ascending Node (LTAN) closer to local noon.

A Thermal Mathematical Model (TMM) of the spacecraft and orbit was built using ESATAN TMS. For the purpose of the analysis we assumed a 600km Sun-synchronous circular orbit with a 96.7 minute period and LTAN of 14:00. The initial analysis showed that a 100 mm $ \times $ 100 mm radiator on the anti-Sun facing surface of the spacecraft would not provide sufficient cooling to the image sensor due to the thermal IR load from the Earth (and to a lesser extent the solar albedo load). In order to improve the efficiency of the radiator a deployable Thermal IR baffle was modelled (see Fig. 13). The inside faces of this baffle are to be coated with a low-emissivity coating (for example, vacuum deposited aluminum) to improve the effective view factor of the radiator to deep space while blocking views to Earth. In order to avoid interference with the spacecraft Attitude Determination and Control System (ADCS) the stiffness and first eigenmode of the deployed baffle needs to be outside of the control bandwidth of the fine pointing system.

The TMM indicated that although the thermal IR baffle improves the performance of the radiator, there are peri-

<!-- PDF_PAGE: 12 -->


![figure_020.png](figure_020.png)



<div align="center">

Fig. 13: Configuration of the spacecraft showing the deployed thermal IR radiator baffle (left), and spacecraft attitude and solar illumination during (northern) summer solstice in a 14:00 LTAN orbit without Earth IR avoidance manoeuvres outside of the observation windows (right).

</div>


![figure_021.png](figure_021.png)



<div align="center">

Fig. 14: Predicted image sensor and thermal radiator temperature variations during several orbits with a thermal IR baffle, both with and without Earth IR avoidance manoeuvres outside of the observation window. When Earth IR avoidance manoeuvres are used the image sensor temperature remains below the nominal $ - 4 0^{\circ} \mathrm{C} $ operating temperature throughout the observation windows.

</div>

ods of the orbit where the radiator is exposed to the Earth and does not provide enough cooling to the image sensor. Fortunately, these periods occur outside the observation windows and therefore the spacecraft is able to slew the radiator away from the Earth without significantly compromising the power generating capacity of the solar arrays. This can be seen in Fig. 14, where the image sensor temperatures are plotted during several orbits with and without the Earth IR avoidance manoeuvres. The design and analysis carried out on the image sensor cooling system shows the fundamental feasibility for this aspect of the mission.

## 4. Concept of operations

The concept of operations for Space Eye is very much a work in progress at the time of writing, however some aspects have been worked out. The science aims of the project require the telescope to obtain repeated long exposure images of a small number of target fields for as long as possible.

## 4.1 Target fields

The exact positions of the target fields will be chosen based on a number of factors, including the positions of suitable guide stars, avoidance of very bright stars and the locations of galaxies and galaxy groups. It is possible to constrain the general location of the target fields based on sensitivity and systematic error considerations, however. Sensitivity models for the baseline design which include the effects of Zodiacal light and Galactic dust show that the preferred regions of sky are those close to the North ecliptic pole from February to July and close to the South ecliptic pole from August to January, and that the tightest

<!-- PDF_PAGE: 13 -->

constraints come from Galactic dust (see Sec. 3.1.5. We can use relative sensitivity maps (Fig. 11) to narrow down the optimum target field positions to between 15.5 and 16.5 hours Right Ascension and $ 5 5^{\circ} $ and $ 6 0^{\circ} $ declination in the north and between 4 and 5 hours Right Ascension and $ - 5 0^{\circ} $ and $ - 6 0^{\circ} $ declination in the south. Within each of these regions we expect to select 1 or 2 target fields, and each region will be observed for approximately 6 months before switching to the other region.

For the zodiacal light mapping, a larger number of fields will be targetted in order to map out the distribution of dust within the Solar System. These fields will be revisited to quantify seasonal variations.

## 4.2 Operational requirements

In order to observe both northern and southern target fields under favourable Zodiacal light conditions we require an operational lifetime of at least 1 year, with a goal of 2 years or more. Based on this lifetime requirement and the results our initial power, thermal and communications budget analyses we have selected a nominal circular Sunsynchronous orbit at 600 km altitude, 96.7 min period and LTAN of 14:00.

## 4.3 Observing constraints

Useful scientific data can only be acquired when certain constraints are met. These include image sensor temperature $ (-40^{\circ}\mathrm{C}) $ and minimum angular separations of the target field from the Earth's disc, the Sun and the Moon $ (25^{\circ},60^{\circ} $ and $ 60^{\circ} $ respectively). Preliminary analyses indicate that for the nominal orbit and approximate target field positions approximately 3-4 600 s science exposures will be possible during each 96.7 min orbit.

## 4.4 Observing sequence

The nominal sequence of operations for science observations is as follows:

1. Slew spacecraft to target field, arcminute level pointing accuracy is sufficient. Roll angle is chosen to orientate the main solar array towards the Sun

2. Take a short exposure with the main image sensor to locate positions of pre-selected guide stars (2-3) on the image sensor, define regions-of-interest (RoIs) around them.

3. Begin continuous imaging of the guide star RoIs and start closed loop image stabilisation using guide star centroids (ADCS 2nd stage).

4. Take a long exposure using the remainder of the main image sensor. Usually this would be a 600s exposure but some shorter exposures will be taken to obtain unsaturated images of the brightest stars.

5. Repeat 4 until orbital motion causes observing constraints to be no longer satisfied, likely after 3-4 exposures

6. Perform Earth IR avoidance manoeuvres until observering constraints met again.

7. Repeat from 1 with pointing offset to the next dither position

Over the course of 6 orbits Space Eye will obtain images at each of 6 dither positions in order to construct contiguous images for each of the 6 filters in the focal plane mosaic. Over the course of a 6 month period spent observing either the northern or southern targets the spacecraft will observe at roll angles spanning a range of $ 1 8 0^{\circ} $ as the spacecraft tracks the Sun with its main solar array. This ensures that each position on the sky is observed at a range of field positions, which helps in suppressing residual calibration errors and internal reflections.

## 4.5 Calibration sequences

Space Eye will be extensively characterised before launch however these data will be supplemented with on orbit calibrations, including dark current measurements and flat fielding using a combination of Earth streak images, stellar photometry, median sky frames and image sensor flat fielding using an internal screen on the reverse side of the shutter. The on-orbit measurements will account for changes caused by radiation damage, etc. In addition science observations will be interspersed with exposures of bright stars （'PSF standards'）to regularly characterise the faint, outer parts of the PSF wings in a strategy similar to that reported by Tujillo and Fliri[31].

## 4.6 Data handling

Each main image sensor image will be captured at 2000 x 1504 pixel resolution and 16 bits/pixel depth, i.e. each comprises 6.016 MB of raw data. Image data will be stored as losslessly compressed Flexible Image Transport System (FITS) files, which typically have compression factors of around 2 for astronomical data. On board data processing will be limited to insertion of relevant spacecraft and instrument status information into FITS file headers, all raw images will be downlinked for processing and analysis on the ground. Based on the assumption of 3-4 science images per 96.7 min orbit the average (compressed) data rate would be $ \sim $ 135-180 MB per day. Downlinking this volume of data from a CubeSat using standard S-band communications and 1-2 ground stations would be a challenge, but is achievable[30].

## 5. Status and plans

At the time of writing funding to complete the design, construction, testing, launch, and commissioning of the

<!-- PDF_PAGE: 14 -->

Australian Space Eye is being sought via the Australian Research Council's Linkage Infrastructure, Equipment & Facilities (LIEF) national competitive grant scheme.

The LIEF grant scheme allows consortia lead by an Australian higher education institution to seek part funding (typically 50%) for a research infrastructure project from the government, with the remainder to come from the institutions of the consortium. The Space Eye LIEF consortium is lead by PI Lee Spitler of Macquarie University and includes astronomers, instrument scientists and engineers from 6 Australian universities (Macquarie University, Australian National University, University of New South Wales, University of Western Australia, University of Queensland, Swinburne University of Technology), the Australian Astronomical Observatory, and both Tyvak and California Polytechnic State University, San Luis Obispo from the USA.

The outcome of our grant application is expected in September 2017 and, if successful, will be followed by a 3 year construction phase with launch and commissioning planned for H2 2020.

## Acknowledgements

This research made use of Astropy, a community-developed core Python package for astronomy[32], and the affiliated package ccdproc[33]. Some of the results in this paper have been derived using the HEALPix $ ^{*} $ [34] package. This work also used the NumPy[35], Scipy[36], Matplotlib[37] and IPython[38] Python packages.

## References

[1] J. T. McGraw, et al., Ground-based observatory operations optimized and enhanced by direct atmospheric measurements, Proc. SPIE 7739 (2010) 773929.

[2] G. Moreels, et al., Near-infrared sky background fluctuations at mid- and low latitudes, Exp. Astron. 22, 1-2 (2008) 87-107.

[3] C. Leinert, et al., The 1997 reference of diffuse night sky brightness, Astron. Astrophys. Suppl. Ser. 127, 1 (1998) 1-99.

[4] C. Sandin, The influence of diffuse scattered light. I. The PSF and its role in observations of the edgeon galaxy NGC 5907, Astron. Astrophys. 567 (2014) A97.

[5] C. Sandin, The influence of diffuse scattered light. II. Observations of galaxy haloes and thick discs and hosts of blue compact galaxies, Astron. Astrophys. 577 (2015) A106.

[6] P.-A. Duc, et al., The ATLAS 3D project - XXIX. The new look of early-type galaxies and surrounding

fields disclosed by extremely deep optical images, MNRAS 446,1 (2015) 120-143.

[7] R. G. Abraham, P. G. van Dokkum, Ultra-Low Surface Brightness Imaging with the Dragonfly Telephoto Array, Publ. Astron. Soc. Pacific 126, 935 (2014) 55-69.

[8] P. G. van Dokkum, et al., Forty-Seven Milky Way Sized, Extremely Diffuse Galaxies in the Coma Cluster, Astrophys. J. 798, 2 (2015) L45.

[9] E. F. Schlafly, et al., Mapping the Extinction Curve in 3D: Structure on Kiloparsec Scales, Astrophys. J. 838, 1 (2017) 36.

[10] A. Cooray, Extragalactic Background Light: Measurements and Applications, R. Soc. Open Sci. 3, 3 (2016) 150555.

[11] R. A. Bernstein, The Optical Extragalactic Background Light: Revisions and Further Comments, Astrophys. J. 666, 2 (2007) 663-673.

[12] F. Aharonian, et al., A low level of extragalactic background light as revealed by gamma-rays from blazars., Nature 440, 7087 (2006) 1018-1021.

[13] K. Tsumura, et al., Observations of the near-infrared spectrum of the zodiacal light with CIBER, Astrophys. J. 719, 1 (2010) 394-402.

[14] A. Lanz, et al., Studying extragalactic background fluctuations with the Cosmic Infrared Background ExpeRiment 2 (CIBER-2), Proc. SPIE 9143 (2014) 91433N.

[15] M. Giavalisco, K. Sahu, R. Bohlin, New estimates of the sky background for the HST exposure time calculator, Tech. rep., STSci (2002).

[16] G. Aldering, SNAP Sky Background at the North Ecliptic Pole, Tech. Rep. LBNL-51157, LBNL (2001).

[17] M. Zemcov, et al., The Cosmic Infrared Background Experiment (CIBER): a Sounding Rocket Payload To Study the Near Infrared Extragalactic Background Light, Astrophys. J. Suppl. Ser. 207, 2 (2013) 31.

[18] P. M. Korngut, et al., The cosmic infrared background experiment (CIBER): The narrow-band spectrometer, Astrophys. J. Suppl. Ser. 207, 2 (2013) 34.

[19] J. Liou, S. Dermott, Y. Xu, The contribution of cometary dust to the zodiacal cloud, Planet. Space Sci. 43, 6 (1995) 717-722.

<!-- PDF_PAGE: 15 -->

[20] D. Nesvorny, et al., Cometary origin of the zodiacal cloud and carbonaceous micrometeorites. Implications for hot debris disks., Astrophys. J. 713, 2 (2010) 816-836.

[21] K. Kawara, et al., Ultraviolet to optical diffuse sky emission as seen by the Hubble Space Telescope Faint Object Spectrograph, Publ. Astron. Soc. Japan 69, 2 (2017) 211.

[22] H. Yang, M. Ishiguro, Origin of interplanetary dust through optical properties of zodiacal light, Astrophys. J. 813, 2 (2015) 87.

[23] R. Hevner, et al., An Advanced Standard for CubeSats, SC11-II-3, 25th Annu. AIAA/USU Conf. Small Satell., 2011.

[24] P. R. Jorden, et al., e2v new CCD and CMOS technology developments for astronomical sensors, Proc. SPIE 9154 (2014) 91540M.

[25] M. Soman, et al., Design and characterisation of the new CIS115 sensor for JANUS, the high resolution camera on JUICE, Proc. SPIE 9154 (2014) 915407.

[26] S.-Y. Wang, et al., Characteristic of e2v CMOS sensors for astronomical applications, Proc. SPIE 9154 (2014) 91542I.

[27] L. Colina, R. C. Bohlin, F. Castelli, The 0.12-2.5 micron Absolute Flux Distribution of the Sun for Comparison With Solar Analog Stars, Astron. J. 112 (1996) 307.

[28] A. Abergel, et al., Planck 2013 results. XI. All-sky model of thermal dust emission, Astron. Astrophys. 571 (2014) A11.

[29] E. L. Fitzpatrick, Correcting for the Effects of Interstellar Extinction, Publ. Astron. Soc. Pacific 111, 755 (1999) 63-75.

[30] S. Reisenfeld, L. Spitler, A. Horton, The Australian Space Eye: Ultra-faint astronomy imaging from Space, 33rd AIAA Int. Commun. Satell. Syst. Conf. Exhib., American Institute of Aeronautics and Astronautics, 2015.

[31] I. Trujillo, J. Fliri, Beyond 31 mag/arcsec $ ^{2} $ : The frontier of low surface brightness imaging with the largest optical telescopes, Astrophys. J. 823, 2 (2016) 123.

[32] T. P. Robitaille, et al., Astropy: A community Python package for astronomy, Astron. Astrophys. 558 (2013) A33.

[33] M. W. Craig, et al., ccdproc: CCD data reduction software (2015).

[34] K. M. Gorski, et al., HEALPix - a Framework for High Resolution Discretization, and Fast Analysis of Data Distributed on the Sphere, Astrophys. J. 622, 2 (2004) 759-771.

[35] S. Van Der Walt, S. C. Colbert, G. Varoquaux, The NumPy array: A structure for efficient numerical computation, Comput. Sci. Eng. 13, 2 (2011) 22-30.

[36] E. Jones, et al., SciPy: Open source scientific tools for Python (2001).

[37] J. D. Hunter, Matplotlib: A 2D graphics environment, Comput. Sci. Eng. 9, 3 (2007) 99-104.

[38] F. Pérez, B. E. Granger, IPython: A system for interactive scientific computing, Comput. Sci. Eng. 9, 3 (2007) 21-29.