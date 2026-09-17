---
source: null
title: "review-candidate-1553"
page_count: 57
converted_at: "2026-09-06T19:15:47Z"
---

<!-- PDF_PAGE: 1 -->









<div align="center">

# Effect of Satellite Formation Architectures and Imaging Modes on Albedo Estimation of major Biomes

</div>

Sreeja Nag $ ^{1,2} $ , Charles Gatebe $ ^{3} $ , David Miller $ ^{1,4} $ , Olivier de Weck $ ^{1} $

$ ^{1} $Massachusetts Institute of Technology, Cambridge, MA $ ^{2} $NASA Ames Research Center, Moffet Field, CA $ ^{3} $NASA Goddard Space Flight Center, Greenbelt, MD $ ^{4} $NASA Headquarters, Washington DC

October 1,2014

<!-- PDF_PAGE: 2 -->





## Outline






![figure_001.png](figure_001.png)



The Angular Acquisition problem

- Example Application dependent on Angular Sampling

- Proposed Solution and Design Methodology

- Baseline Case Study using a few Formation Configurations

- Value of Imaging Modes

- Summary and Future Work

<!-- PDF_PAGE: 3 -->

## Introduction: Why Angular?





- Because reflectance values depend on the direction of solar illumination and direction of measured reflection

- Angular performance metric: Bi-directional reflectance distribution function (BRDF)

- Anisotropic (angle-dependent) and multispectral (near-solar spectrum) reflectance of clouds and ground surface

- Angular sampling is inadequate using monolithic spacecrafts presenting an angular challenge


![figure_002.png](figure_002.png)



<div align="center">

BRDF Ground Spot spectrum

</div>

Image Credits: Schaepman-Strub et. al, 2006

<!-- PDF_PAGE: 4 -->

## Angular Acquisition Problem





Measurements for BRDF Estimation using a single satellite with forward aft sensors-one angle at a time


![figure_003.png](figure_003.png)



<!-- PDF_PAGE: 5 -->

## Angular Acquisition Problem





Measurements for BRDF Estimation using a single satellite with forward aft sensors-one angle at a time


![figure_004.png](figure_004.png)



<!-- PDF_PAGE: 6 -->

## Angular Acquisition Problem





Measurements for BRDF Estimation using a single satellite with forward aft sensors-one angle at a time


![figure_005.png](figure_005.png)



<!-- PDF_PAGE: 7 -->





## Angular Acquisition Problem





BRDF Estimation by combining the consecutive measurements

Problem: 1. Restrictive plane with respect to the sun

2. Up to 10 minutes between measurements


![figure_006.png](figure_006.png)



<!-- PDF_PAGE: 8 -->

## Angular Acquisition Problem





Measurements for BRDF Estimation using a single satellite with large cross-track swath-one angle at a time


![figure_007.png](figure_007.png)



What needs to be measured for BRDF estimation

<!-- PDF_PAGE: 9 -->





## Angular Acquisition Problem





Measurements for BRDF Estimation using a single satellite with large cross-track swath-one angle at a time

What is measured with a single satellite over time and/or multiple overpasses


![figure_008.png](figure_008.png)



What needs to be measured for BRDF estimation

<!-- PDF_PAGE: 10 -->

## Angular Acquisition Problem





Measurements for BRDF Estimation using a single satellite with large cross-track swath-one angle at a time

What is measured with a single satellite over time and/or multiple overpasses


![figure_009.png](figure_009.png)



<!-- PDF_PAGE: 11 -->





## Angular Acquisition Problem





BRDF Estimation by combining measurements over consecutive overpasses

Problem: 1. Restrictive plane with respect to the sun

2. Up 2 weeks between measurements


![figure_010.png](figure_010.png)



<!-- PDF_PAGE: 12 -->





## Outline





- The Angular Acquisition problem


![figure_011.png](figure_011.png)



Example Application dependent on Angular Sampling

- Proposed Solution and Design Methodology

- Baseline Case Study using a few Formation Configurations

- Value of Imaging Modes

- Summary and Future Work

<!-- PDF_PAGE: 13 -->





## Albedo Estimation





Albedo is the hemispheric integration of BRDF over all view zenith and azimuth angles. Can be estimated from nadir measurements BUT big errors in the Arctic...


![figure_012.png](figure_012.png)



Image Credits: Arnold et al, 2002

Figure uses thousands of angular measurement data from the airborne Cloud Absorption Radiometer taken during the ARMCAS campaign in 1998.

<!-- PDF_PAGE: 14 -->

## Albedo Estimation





Albedo is the hemispheric integration of BRDF over all view zenith and azimuth angles. Can be estimated from multiple hemispheric measurements BUT big errors in the Savannas...


![figure_013.png](figure_013.png)



BRDF Data (Image Credits: Gatebe et. al, 2012) from the

Cloud Absorption Radiometer

vs.

spaceborne MODIS

<!-- PDF_PAGE: 15 -->





## Outline





- The Angular Acquisition problem

- Example Application dependent on Angular Sampling


![figure_014.png](figure_014.png)



Proposed Solution and Design Methodology

- Baseline Case Study using a few Formation Configurations

- Value of Imaging Modes

- Summary and Future Work

<!-- PDF_PAGE: 16 -->

## Proposed Solution to Angular Acq.





Major Limitation: Angular undersampling


![figure_015.png](figure_015.png)




![figure_016.png](figure_016.png)



<!-- PDF_PAGE: 17 -->

## Proposed Solution to Angular Acq.





Major Limitation: Angular undersampling Potential Solution: Clusters (NFOV) of nano satellites in formation flight.


![figure_017.png](figure_017.png)



Additional advantages:- Small satellite design and development, Standard bus like 6U, Secondary payload launches, Cubesat GS network Disadvantages:- Restrictive orbits, mass/volume constraints, limited propulsion and ADCS


![figure_018.png](figure_018.png)




![figure_019.png](figure_019.png)



<!-- PDF_PAGE: 18 -->





## Cluster Design Approach





## Build a Systems engineering (SE) model integrated with traditional BRDF Estimation models


![figure_020.png](figure_020.png)



*as a function of tech requirements, biomes of interest, science applications

<!-- PDF_PAGE: 19 -->





## Cluster Design Approach





## Build a Systems engineering (SE) model integrated with traditional BRDF Estimation models


![figure_021.png](figure_021.png)



*as a function of tech requirements, biomes of interest, science applications

<!-- PDF_PAGE: 20 -->

## Constellation vs. Formation Flight






![figure_022.png](figure_022.png)



Image Credits: www.cienciaviva.pt

VS.


![figure_023.png](figure_023.png)




![figure_024.png](figure_024.png)



© CNES · Janvier 2004 / Illustration Pierre CARRIL

<!-- PDF_PAGE: 21 -->





## Cluster Design Approach





## Build a Systems engineering (SE) model integrated with traditional BRDF Estimation models


![figure_025.png](figure_025.png)



*as a function of tech requirements, biomes of interest, science applications

<!-- PDF_PAGE: 22 -->





## Science Evaluation






![figure_026.png](figure_026.png)



<!-- PDF_PAGE: 23 -->





## Setting up the "Truth"





MODIS Land Cover Map:

Find the global biome distribution Because local & static BRDF data is available per biome


![figure_027.png](figure_027.png)



<!-- PDF_PAGE: 24 -->





## Setting up the "Truth"





MODIS Land Cover Map + CAR data


![figure_028.png](figure_028.png)



<!-- PDF_PAGE: 25 -->





## Outline





- The Angular Acquisition problem

- Example Application dependent on Angular Sampling

- Proposed Solution and Design Methodology


![figure_029.png](figure_029.png)



Baseline Case Study using a few Formation Configurations

- Value of Imaging Modes

- Summary and Future Work

<!-- PDF_PAGE: 26 -->





## Formation Flight-Orbit Config





Simplest case considered-4 satellites, no propulsion but +/- 50deg of sensor slew, ISS inclination of 51.6 deg, 650 km.

Biome considered - Savanna vegetation considered for the baseline. Will be expanded to snow and others.

<div align="center">

Differential Keplerian variables

</div>

<table border="1"><tr><td>Semi Major Axis</td><td>No</td></tr><tr><td>Inclination</td><td>No</td></tr><tr><td>Arg. Of Perigee</td><td>No</td></tr><tr><td>Eccentricity</td><td>No</td></tr><tr><td>RAAN</td><td>Yes</td></tr><tr><td>True Anomaly</td><td>Yes</td></tr></table>

Effect of configurations (few architectures) and modes will be shown. Mode #1 is the baseline mode.

<table border="1"><tr><td></td><td>Sat #1</td><td>Sat #2</td><td>Sat #3</td><td>Sat #4</td></tr><tr><td>Config #1</td><td>0::0</td><td>0::-5</td><td>-5::-1</td><td>-5::-6</td></tr><tr><td>Config #2</td><td>0::0</td><td>0::-5</td><td>-5::-1</td><td>5::-4</td></tr><tr><td>Config #3</td><td>0::0</td><td>0::-5</td><td>-5::-6</td><td>5::-4</td></tr><tr><td>Config #4</td><td>0::0</td><td>0::-5</td><td>-5::-3</td><td>5::-4</td></tr><tr><td>Config #5</td><td>0::0</td><td>0::-5</td><td>-5::-3</td><td>3::-3</td></tr><tr><td>Config #6</td><td>0::0</td><td>0::-3</td><td>-3::0</td><td>-3::-3</td></tr></table>

<!-- PDF_PAGE: 27 -->

## Formation Flight - Imaging Modes





## MODE #1 - Same reference satellite

One satellite in the cluster is the designated leader and always points nadir. Other sats point to the ground spot directly nadir to the leader satellite.


![figure_030.png](figure_030.png)



## MODE #2-Change the reference satellite over the orbit

Like Mode #1 but the leader satellite changes over the course of the orbit so as to optimize the angular coverage of the BRDF plane.


![figure_031.png](figure_031.png)




![figure_032.png](figure_032.png)



## MODE #3-Tracking/Staring at a Spot

All satellites such that they point to the same ground target/s as they approach over the horizon and recede into the horizon.

RADIUS: View Zenith Angle in degrees


![figure_033.png](figure_033.png)



## MODE #4 - Multiple Payloads

Each follows a different mode among the above or fractionate functionality.

<!-- PDF_PAGE: 28 -->

## Formation Flight - Imaging Modes





## MODE #1 - Same reference satellite

One satellite in the cluster is the designated leader and always points nadir. Other sats point to the ground spot directly nadir to the leader satellite.

RADIUS: View Zenith Angle in degrees


![figure_034.png](figure_034.png)



## MODE #2-Change the reference satellite over the orbit

Like Mode #1 but the leader satellite changes over the course of the orbit so as to optimize the angular coverage of the BRDF plane.


![figure_035.png](figure_035.png)




![figure_036.png](figure_036.png)



## MODE #3-Tracking/Staring at a Spot

All satellites such that they point to the same ground target/s as they approach over the horizon and recede into the horizon.

RADIUS: View Zenith Angle in degrees


![figure_037.png](figure_037.png)



## MODE #4 - Multiple Payloads

Each follows a different mode among the above or fractionate functionality.

<!-- PDF_PAGE: 29 -->

## Albedo Errors by Configuration





Compared 6 diff. TA+RAAN orbits wrt CAR data (682 nm) from South Africa assuming same biome over a 20 minute pass over African Peninsula.


![figure_038.png](figure_038.png)




![figure_039.png](figure_039.png)



<!-- PDF_PAGE: 30 -->

## Albedo Errors by Configuration






![figure_040.png](figure_040.png)



Compared 6 diff. TA+RAAN orbits wrt CAR data (682 nm) from South Africa assuming same biome over a 20 minute pass over African Peninsula.


![figure_041.png](figure_041.png)



<div align="center">

True BRDF from CAR

</div>


![figure_042.png](figure_042.png)



<!-- PDF_PAGE: 31 -->

## Albedo Errors by Configuration






![figure_043.png](figure_043.png)



Compared 6 diff. TA+RAAN orbits wrt CAR data (682 nm) from South Africa assuming same biome over a 20 minute pass over African Peninsula.


![figure_044.png](figure_044.png)




![figure_045.png](figure_045.png)



<!-- PDF_PAGE: 32 -->

## Albedo Errors by Configuration






![figure_046.png](figure_046.png)




![figure_047.png](figure_047.png)




![figure_048.png](figure_048.png)




![figure_049.png](figure_049.png)



mpared 6 diff. TA+RAAN orbits wrt R data (682 nm) from South Africauming same biome over a 20 minute pass over African Peninsula.


![figure_050.png](figure_050.png)



<div align="center">

True BRDF from CAR

</div>


![figure_051.png](figure_051.png)



<!-- PDF_PAGE: 33 -->

## Albedo Errors by Configuration






![figure_052.png](figure_052.png)




![figure_053.png](figure_053.png)



mpared 6 diff. TA+RAAN orbits wrt R data (682 nm) from South Africauming same biome over a 20 minute pass over African Peninsula.


![figure_054.png](figure_054.png)




![figure_055.png](figure_055.png)




![figure_056.png](figure_056.png)



<div align="center">

MODE #1:

</div>


![figure_057.png](figure_057.png)



<!-- PDF_PAGE: 34 -->

## Albedo Errors by Configuration






![figure_058.png](figure_058.png)



mpared 6 diff. TA+RAAN orbits wrt R data (682 nm) from South Africauming same biome over a 20 minute pass over African Peninsula.


![figure_059.png](figure_059.png)




![figure_060.png](figure_060.png)



<div align="center">

MODE #1:

</div>


![figure_061.png](figure_061.png)



<!-- PDF_PAGE: 35 -->





## Outline





- The Angular Acquisition problem

- Example Application dependent on Angular Sampling

- Proposed Solution and Design Methodology

- Baseline Case Study using a few Formation Configurations


![figure_062.png](figure_062.png)



Value of Imaging Modes

- Summary and Future Work

<!-- PDF_PAGE: 36 -->

## Why use Imaging Modes?





## MODE #1 - Same reference satellite

Needs differential elements that are impossible to maintain with smallsat technologies to cover both hemispheres at all times (e.g. diff. inclination, diff. eccentricity)


![figure_063.png](figure_063.png)



## MODE #2-Change the reference satellite over the orbit

An appropriately selected ref. satellite allows both angular hemispheres to be covered using maintainable diff. elements. Satellites drift apart over a year even in true anomaly.. This

mode helps upto ~6 months.

RADIUS: View Zenith Angle in degrees


![figure_064.png](figure_064.png)




![figure_065.png](figure_065.png)



MODE #3-Tracking/Staring at a Spot More angular coverage and lesser local errors at the cost of spatial coverage. Polar + high latitude coverage only possible with this mode. Allows mission continuity beyond 6 months in spite of drifting satellites.


![figure_066.png](figure_066.png)



<!-- PDF_PAGE: 37 -->

## Why use Imaging Modes?





## MODE #1 - Same reference satellite

Needs differential elements that are impossible to maintain with smallsat technologies to cover both hemispheres at all times (e.g. diff. inclination, diff. eccentricity)

RADIUS: View Zenith Angle in degrees


![figure_067.png](figure_067.png)



## MODE #2-Change the reference satellite over the orbit

An appropriately selected ref. satellite allows both angular hemispheres to be covered using maintainable diff. elements. Satellites drift apart over a year even in true anomaly.. This mode helps upto ~6 months.

RADIUS: View Zenith Angle in degrees


![figure_068.png](figure_068.png)




![figure_069.png](figure_069.png)



MODE #3-Tracking/Staring at a Spot More angular coverage and lesser local errors at the cost of spatial coverage. Polar + high latitude coverage only possible with this mode. Allows mission continuity beyond 6 months in spite of drifting satellites.

RADIUS: View Zenith Angle in degrees


![figure_070.png](figure_070.png)



<!-- PDF_PAGE: 38 -->

## Albedo Errors by Reference Sat





For the best configuration (#3), analyzed errors using different sats as reference.

By changing the ref sat once in 20 mins, we can outdo monoliths.


![figure_071.png](figure_071.png)




![figure_072.png](figure_072.png)




![figure_073.png](figure_073.png)



MODE #1:


![figure_074.png](figure_074.png)




![figure_075.png](figure_075.png)



MODE #2:


![figure_076.png](figure_076.png)




![figure_077.png](figure_077.png)



<!-- PDF_PAGE: 39 -->

## Albedo Errors by Reference Sat





For the best configuration (#3), analyzed errors using different sats as reference.

By changing the ref sat once in 20 mins, we can outdo monoliths.


![figure_078.png](figure_078.png)



MODE #1:


![figure_079.png](figure_079.png)




![figure_080.png](figure_080.png)




![figure_081.png](figure_081.png)



MODE #2:


![figure_082.png](figure_082.png)




![figure_083.png](figure_083.png)




![figure_084.png](figure_084.png)



<!-- PDF_PAGE: 40 -->





## Albedo Errors by Reference Sat





For the best configuration (#3), analyzed errors using different sats as reference.

By changing the ref sat once in 20 mins, we can outdo monoliths

Minimum Estimation Error:


![figure_085.png](figure_085.png)




![figure_086.png](figure_086.png)




![figure_087.png](figure_087.png)



MODE #1:


![figure_088.png](figure_088.png)




![figure_089.png](figure_089.png)




![figure_090.png](figure_090.png)



<!-- PDF_PAGE: 41 -->

## Why use Imaging Modes?





## MODE #1 - Same reference satellite

Needs differential elements that are impossible to maintain with smallsat technologies to cover both hemispheres at all times (e.g. diff. inclination, diff. eccentricity)

RADIUS: View Zenith Angle in degrees


![figure_091.png](figure_091.png)



## MODE #2-Change the reference satellite over the orbit

An appropriately selected ref. satellite allows both angular hemispheres to be covered using maintainable diff. elements. Satellites drift apart over a year even in true anomaly.. This

mode helps upto ~6 months.

RADIUS: View Zenith Angle in degrees


![figure_092.png](figure_092.png)




![figure_093.png](figure_093.png)



MODE #3-Tracking/Staring at a Spot More angular coverage and lesser local errors at the cost of spatial coverage. Polar + high latitude coverage only possible with this mode. Allows mission continuity beyond 6 months in spite of drifting satellites.


![figure_094.png](figure_094.png)



<!-- PDF_PAGE: 42 -->

## MIT More Angular Coverage, Lower Errors





Compared 6 diff. TA+RAAN orbits wrt CAR data (682 nm) from South Africa assuming same biome over a 20 minute pass over African Peninsula.


![figure_095.png](figure_095.png)



<div align="center">

MODE #3:

</div>


![figure_096.png](figure_096.png)



<!-- PDF_PAGE: 43 -->

## MIT More Angular Coverage, Lower Errors





## RECAP-

Config #1 : Mode #1 Worst but Improved by Mode#2

Config #2 : Mode #1 Worse, NOT improved by Mode #2

Config #3 : Best for Mode#1 and Mode#2


![figure_097.png](figure_097.png)



<!-- PDF_PAGE: 44 -->

## MIT More Angular Coverage, Lower Errors






![figure_098.png](figure_098.png)



Compared 6 diff. TA+RAAN orbits wrt CAR data (682 nm) from South Africa assuming same biome over a 20 minute pass over African Peninsula.


![figure_099.png](figure_099.png)




![figure_100.png](figure_100.png)



<!-- PDF_PAGE: 45 -->

## More Angular Coverage, Lower Errors






![figure_101.png](figure_101.png)




![figure_102.png](figure_102.png)



Compared 6 diff. TA+RAAN orbits wrt CAR data (682 nm) from South Africa assuming same biome over a 20 minute pass over African Peninsula.


![figure_103.png](figure_103.png)




![figure_104.png](figure_104.png)




![figure_105.png](figure_105.png)



<!-- PDF_PAGE: 46 -->

## MIT More Angular Coverage, Lower Errors






![figure_106.png](figure_106.png)




![figure_107.png](figure_107.png)



Compared 6 diff. TA+RAAN orbits wrt CAR data (682 nm) from South Africa assuming same biome over a 20 minute pass over African Peninsula.


![figure_108.png](figure_108.png)




![figure_109.png](figure_109.png)




![figure_110.png](figure_110.png)



<!-- PDF_PAGE: 47 -->

## MIT More Angular Coverage, Lower Errors






![figure_111.png](figure_111.png)




![figure_112.png](figure_112.png)



Compared 6 diff. TA+RAAN orbits wrt CAR data (682 nm) from South Africa assuming same biome over a 20 minute pass over African Peninsula.


![figure_113.png](figure_113.png)




![figure_114.png](figure_114.png)




![figure_115.png](figure_115.png)



<!-- PDF_PAGE: 48 -->

## Why use Imaging Modes?





## MODE #1 - Same reference satellite

Needs differential elements that are impossible to maintain with smallsat technologies to cover both hemispheres at all times (e.g. diff. inclination, diff. eccentricity)

RADIUS: View Zenith Angle in degrees


![figure_116.png](figure_116.png)



## MODE #2-Change the reference satellite over the orbit

An appropriately selected ref. satellite allows both angular hemispheres to be covered using maintainable diff. elements. Satellites drift apart over a year even in true anomaly.. This

mode helps upto ~6 months.

RADIUS: View Zenith Angle in degrees


![figure_117.png](figure_117.png)




![figure_118.png](figure_118.png)



MODE #3-Tracking/Staring at a Spot More angular coverage and lesser local errors at the cost of spatial coverage. Polar + high latitude coverage only possible with this mode. Allows mission continuity beyond 6 months in spite of drifting satellites.

RADIUS: View Zenith Angle in degrees


![figure_119.png](figure_119.png)



<!-- PDF_PAGE: 49 -->





## Polar Albedo Estimation






![figure_120.png](figure_120.png)



Compared 3 of the previous TA+RAAN orbits wrt CAR data (1031 nm) from Alaska assuming same biome over a 12 minute pass over the Arctic Circle.


![figure_121.png](figure_121.png)



<div align="center">

True BRDF from CAR

</div>


![figure_122.png](figure_122.png)



<!-- PDF_PAGE: 50 -->





## Polar Albedo Estimation






![figure_123.png](figure_123.png)




![figure_124.png](figure_124.png)




![figure_125.png](figure_125.png)



Compared 3 of the previous TA+RAAN orbits wrt CAR data (1031 nm) from Alaska assuming same biome over a 12 minute pass over the Arctic Circle.


![figure_126.png](figure_126.png)



<div align="center">

True BRDF from CAR

</div>


![figure_127.png](figure_127.png)



<!-- PDF_PAGE: 51 -->





## Polar Albedo Estimation






![figure_128.png](figure_128.png)




![figure_129.png](figure_129.png)




![figure_130.png](figure_130.png)



Compared 3 of the previous TA+RAAN orbits wrt CAR data (1031 nm) from Alaska assuming same biome over a 12 minute pass over the Arctic Circle.


![figure_131.png](figure_131.png)



<div align="center">

True BRDF from CAR

</div>


![figure_132.png](figure_132.png)



<!-- PDF_PAGE: 52 -->





## Polar Albedo Estimation






![figure_133.png](figure_133.png)




![figure_134.png](figure_134.png)




![figure_135.png](figure_135.png)



Compared 3 of the previous TA+RAAN orbits wrt CAR data (1031 nm) from Alaska assuming same biome over a 12 minute pass over the Arctic Circle.


![figure_136.png](figure_136.png)



<div align="center">

True BRDF from CAR

</div>


![figure_137.png](figure_137.png)



<!-- PDF_PAGE: 53 -->





## Polar Albedo Estimation






![figure_138.png](figure_138.png)



Instead, by spreading out the RAAN and TA, we may get lower errors. However, BRDF near the equator would need a clustellation (more spatio temporal coverage)

MODE #3:


![figure_139.png](figure_139.png)



<div align="center">

True BRDF from CAR

</div>

<!-- PDF_PAGE: 54 -->

## Polar Albedo Estimation






![figure_140.png](figure_140.png)




![figure_141.png](figure_141.png)




![figure_142.png](figure_142.png)



Instead, by spreading out the RAAN and TA, we may get lower errors. However, BRDF near the equator would need a clustellation (more spatio temporal coverage)


![figure_143.png](figure_143.png)



<div align="center">

MODE #3:

</div>


![figure_144.png](figure_144.png)




![figure_145.png](figure_145.png)



<div align="center">

True BRDF from CAR

</div>

<!-- PDF_PAGE: 55 -->





## Outline





- Distributed Space Missions for the Angular Acquisition problem

- Example Application dependent on Angular Sampling

- Proposed Solution and Design Methodology

- Baseline Case Study using a few Formation Configurations

- Value of Imaging Modes


![figure_146.png](figure_146.png)



Summary and Future Work

<!-- PDF_PAGE: 56 -->

## Conclusions and Future Work





- The angular acquisition problem for more accurate albedo estimation can be solved using small satellite formation flight

- Coupled science (BRDF estimation) and engineering (differential Keplerian) models proposed to validate the performance of a baseline formation design

- Simple formations with 4 satellites and no propulsion (only RAAN, TA variation) can achieve better performance than monoliths over few months, especially when different imaging modes are used

- Imaging modes are indispensible for albedo retrievals at the poles and for when the TA spread becomes too large because of unpredictable J2 effects

- Future work - Assess effect on major variables like chief orbit altitude/inclination+satellites and minor variables like their differential variation in RAAN, TA, eccentricity

- The same cluster designs are applicable for 3D mapping and biomass estimation from space

<!-- PDF_PAGE: 57 -->





Thank you!

Questions?

For more info, please email: sreejanag@alum.mit.edu or sreeja.nag@nasa.gov