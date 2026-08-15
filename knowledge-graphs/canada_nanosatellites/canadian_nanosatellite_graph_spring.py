# %% Imports

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyvis.network import Network

from ontology import (
    Agency,
    Company,
    Commissions,
    Constellation,
    Contains,
    Develops,
    Edge,
    Funds,
    Launches,
    Mission,
    Node,
    Operates,
    Payload,
    Service,
    Spacecraft,
    University,
    Uses,
)


# %% Dataset metadata

DATASET_TITLE = "Canadian nanosatellite ecosystem 2011-01-01 - 2026-06-11"


# %% Nodes

NODES = [
# Agency nodes
    Agency(id='csa', label='Canadian Space Agency', title='Canadian Space Agency', source_url='https://www.asc-csa.gc.ca/eng/'),
    Agency(id='drdc', label='Defence Research and Development Canada', title='Defence Research and Development Canada', source_url='https://www.canada.ca/en/defence-research-development.html'),
    Agency(id='dubai_municipality', label='Dubai Municipality / MBRSC', title='Dubai Municipality / MBRSC', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/'),
    Agency(id='norway_space_agency', label='Norwegian Space Agency', title='Norwegian Space Agency', source_url='https://www.romsenter.no/eng/'),
    Agency(id='nserc', label='NSERC', title='NSERC', source_url='https://www.nserc-crsng.gc.ca/'),

# University nodes
    University(id='aurora_college', label='Aurora College / Aurora Research Institute', title='Aurora College / Aurora Research Institute', source_url='https://nwtresearch.com/research-projects/projects/sky-and-space/cubesat'),
    University(id='concordia', label='Concordia University', title='Concordia University\nSpace Concordia', source_url='https://spaceconcordia.ca/spacecraft'),
    University(id='dalhousie', label='Dalhousie University', title='Dalhousie University', source_url='https://www.dal.ca/news/2023/09/15/dalhousie-satellite-mantis-space.html'),
    University(id='ets_lassena', label='ÉTS · LASSENA', title='ÉTS · LASSENA\nspace, navigation and avionics laboratory', source_url='https://lassena.etsmtl.ca/'),
    University(id='mcmaster', label='McMaster University', title='McMaster University', source_url='https://mcmasterneudose.ca/'),
    University(id='memorial', label='Memorial University', title='Memorial University', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp'),
    University(id='nunavut_college', label='Nunavut Arctic College', title='Nunavut Arctic College', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp'),
    University(id='ualberta', label='University of Alberta', title='University of Alberta\nAlbertaSat', source_url='https://albertasat.ca/'),
    University(id='ucalgary', label='University of Calgary', title='University of Calgary\nCalgaryToSpace', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve'),
    University(id='umanitoba', label='University of Manitoba', title='University of Manitoba', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp'),
    University(id='unb', label='University of New Brunswick', title='University of New Brunswick', source_url='https://www.unb.ca/initiatives/cubesat/radio.html'),
    University(id='uoft', label='University of Toronto', title='University of Toronto\nUTIAS SFL / UTAT', source_url='https://www.utias-sfl.net/'),
    University(id='upei', label='University of Prince Edward Island', title='University of Prince Edward Island', source_url='https://projects.upei.ca/spudnik1/'),
    University(id='usask', label='University of Saskatchewan', title='University of Saskatchewan', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp'),
    University(id='usherbrooke', label='Université de Sherbrooke', title='Université de Sherbrooke', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp'),
    University(id='uvic', label='University of Victoria', title='University of Victoria', source_url='https://www.marmotsat.ca/'),
    University(id='western', label='Western University', title='Western University', source_url='https://space.uwo.ca/research/Missions%20and%20Instruments/Skylark.html'),
    University(id='york', label='York University', title='York University', source_url='http://www.yorku.ca/edtsat/'),
    University(id='yukon_u', label='Yukon University', title='Yukon University', source_url='https://www.yukonu.ca/research/projects/cubesat'),

# Company nodes
    Company(id='aac_clyde', label='AAC Clyde Space', title='AAC Clyde Space', source_url='https://investor.aac-clyde.space/en/shares/share-capital/'),
    Company(id='abb_canada', label='ABB Canada', title='ABB Canada', source_url='https://www.ghgsat.com/en/newsroom/worlds-first-commercial-co2-sensor-in-orbit/'),
    Company(id='com_dev', label='COM DEV', title='COM DEV', source_url='https://www.eoportal.org/satellite-missions/canx-7'),
    Company(id='exactearth', label='exactEarth', title='exactEarth', source_url='https://spire.com/press-release/spire-global-inc-completes-acquisition-of-exactearth-ltd/'),
    Company(id='galaxia', label='Galaxia Mission Systems', title='Galaxia Mission Systems', source_url='https://gx.space/'),
    Company(id='ghgsat', label='GHGSat', title='GHGSat', source_url='https://www.ghgsat.com/en/technology/constellation/'),
    Company(id='globalstar_inc', label='Globalstar, Inc.', title='Globalstar, Inc.', source_url='https://www.globalstar.com/en-us/about/who'),
    Company(id='hawkeye360', label='HawkEye 360', title='HawkEye 360', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/'),
    Company(id='helios_wire', label='Helios Wire', title='Helios Wire', source_url='https://www.prnewswire.com/news-releases/echostar-acquires-helios-wire-corporation-300945263.html'),
    Company(id='kepler', label='Kepler Communications', title='Kepler Communications', source_url='https://kepler.space/about/'),
    Company(id='loft_orbital', label='Loft Orbital', title='Loft Orbital', source_url='https://www.wyvern.space/blog/wyvern-expands-dragonette-constellation-capacity-with-lofts-space-infrastructure'),
    Company(id='mission_control', label='Mission Control Space Services', title='Mission Control Space Services', source_url='https://missioncontrolspace.com/'),
    Company(id='mpb', label='MPB Communications', title='MPB Communications', source_url='https://www.eoportal.org/satellite-missions/ghgsat-d'),
    Company(id='northstar', label='NorthStar Earth & Space', title='NorthStar Earth & Space', source_url='https://northstar-data.com/space-situational-awareness-satellites-northstar-1-launch/'),
    Company(id='sfl_missions', label='SFL Missions Inc.', title='SFL Missions Inc.', source_url='https://sflmissions.com/space-flight-laboratory-becomes-new-private-company/'),
    Company(id='spire', label='Spire Global', title='Spire Global', source_url='https://stockanalysis.com/stocks/spir/market-cap/'),
    Company(id='wyvern', label='Wyvern', title='Wyvern', source_url='https://www.wyvern.space/technology'),

# Mission nodes
    Mission(id='brite_mission', label='BRITE science mission', title='BRITE science mission\nCSA investment: 4.07M CAD', source_url='https://sflmissions.com/brite-toronto-brite-montreal/'),
    Mission(id='canx45_mission', label='CanX-4/5 formation-flying mission', title='CanX-4/5 formation-flying mission', source_url='https://www.eoportal.org/satellite-missions/canx-4-5'),
    Mission(id='canx7_mission', label='CanX-7 ADS-B + drag-sail mission', title='CanX-7 ADS-B + drag-sail mission', source_url='https://www.utias-sfl.net/canx-7/'),
    Mission(id='ccp', label='Canadian CubeSat Project', title='Canadian CubeSat Project\n15 grants · 14 launched', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/what-is-the-canadian-cubesat-project.asp'),
    Mission(id='cubics', label='CUBICS 2022', title='CUBICS 2022\n9 grants · CAD 3.15M', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubics/about.asp'),
    Mission(id='descent_mission', label='DESCENT tether-deorbit mission', title='DESCENT tether-deorbit mission', source_url='http://www.yorku.ca/edtsat/'),
    Mission(id='dmsat_mission', label='DMSat-1 atmospheric mission', title='DMSat-1 atmospheric mission', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/'),
    Mission(id='exalta1_mission', label='Ex-Alta 1 / QB50 mission', title='Ex-Alta 1 / QB50 mission', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/ex-alta-1.asp'),
    Mission(id='frontier_mission', label='FrontierSat mission', title='FrontierSat mission', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve'),
    Mission(id='hawkeye_pathfinder', label='HawkEye 360 Pathfinder mission', title='HawkEye 360 Pathfinder mission', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/'),
    Mission(id='helios_mission', label='Helios Wire IoT pathfinder mission', title='Helios Wire IoT pathfinder mission', source_url='https://www.nanosats.eu/sat/helios-sirion'),
    Mission(id='kepler_pathfinders', label='Kepler RF pathfinder mission', title='Kepler RF pathfinder mission', source_url='https://kepler.space/first-launch/'),
    Mission(id='mobius_mission', label='MÖBIUS-1 software-defined mission', title='MÖBIUS-1 software-defined mission', source_url='https://www.asc-csa.gc.ca/eng/blog/2025/06/25/multiple-csa-funded-technologies-take-flight-on-latest-rideshare-mission.asp'),
    Mission(id='norsat3_mission', label='NorSat-3 maritime mission', title='NorSat-3 maritime mission', source_url='https://www.utias-sfl.net/norsat-3/'),
    Mission(id='persistence_mission', label='Mission Persistence', title='Mission Persistence', source_url='https://missioncontrolspace.com/mission-persistence/'),

# Service nodes
    Service(id='drone_link_research', label='Remote drone-fleet monitoring / control', title='Remote drone-fleet monitoring / control', source_url='https://lassena.etsmtl.ca/specialized-infrastructure/'),
    Service(id='ghg_service', label='Facility-level GHG monitoring', title='Facility-level GHG monitoring', source_url='https://www.ghgsat.com/en/technology/constellation/'),
    Service(id='hyperspectral_service', label='Hyperspectral Earth imagery', title='Hyperspectral Earth imagery', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/'),
    Service(id='maritime_ais', label='Maritime AIS monitoring', title='Maritime AIS monitoring', source_url='https://www.eoportal.org/satellite-missions/ev-9'),
    Service(id='optical_relay', label='Optical data-relay pathfinder', title='Optical data-relay pathfinder', source_url='https://kepler.space/kepler-validates-sda-compatible-optical-technology-for-space-data-relay-constellation/'),
    Service(id='pnt_research', label='LEO/INS pseudorange-rate research', title='LEO/INS pseudorange-rate research', source_url='https://doi.org/10.1177/09544100221113123'),
    Service(id='satcom_iot', label='Store-and-forward / IoT connectivity', title='Store-and-forward / IoT connectivity', source_url='https://kepler.space/first-launch/'),
    Service(id='ssa_service', label='Space situational awareness', title='Space situational awareness', source_url='https://northstar-data.com/space-situational-awareness-satellites-northstar-1-launch/'),

# Constellation nodes
    Constellation(id='aissat_constellation', label='AISSat constellation', title='AISSat constellation\n2 successful launches in 2011–2026', source_url='https://www.eoportal.org/satellite-missions/aissat-nanosatellite-constellation'),
    Constellation(id='brite_constellation', label='BRITE Constellation', title='BRITE Constellation\n6 launched · 5 deployed', source_url='https://www.asc-csa.gc.ca/eng/satellites/brite/'),
    Constellation(id='dragonette_constellation', label='Dragonette constellation', title='Dragonette constellation\n5 launched by 2025-11', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/'),
    Constellation(id='exactview_constellation', label='exactView AIS constellation', title='exactView AIS constellation', source_url='https://www.eoportal.org/satellite-missions/ev-9'),
    Constellation(id='ghgsat_constellation', label='GHGSat constellation', title='GHGSat constellation\n18 launch identities through C17', source_url='https://www.ghgsat.com/en/technology/constellation/'),
    Constellation(id='globalstar_constellation', label='Globalstar LEO constellation', title='Globalstar LEO constellation\nWalker-24 configuration\nGraph status: outside the ≤20 kg census scope.', source_url='https://www.globalstar.com/en-us/about/who'),
    Constellation(id='hawkeye_constellation', label='HawkEye Pathfinder cluster', title='HawkEye Pathfinder cluster', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/'),
    Constellation(id='helios_constellation', label='Helios pathfinders', title='Helios pathfinders\n2 launch attempts', source_url='https://www.nanosats.eu/sat/helios-sirion'),
    Constellation(id='kepler_aether_pathfinders', label='Kepler optical pathfinders', title='Kepler optical pathfinders', source_url='https://kepler.space/kepler-validates-sda-compatible-optical-technology-for-space-data-relay-constellation/'),
    Constellation(id='kepler_rf_constellation', label='Kepler RF fleet', title='Kepler RF fleet', source_url='https://kepler.space/kepler-raises-92-million-usd-series-c-to-complete-internet-ready-optical-constellation-3/'),
    Constellation(id='northern_spirit', label='Northern SPIRIT', title='Northern SPIRIT', source_url='https://albertasat.ca/northern-spirit/'),
    Constellation(id='northstar_constellation', label='NorthStar SSA', title='NorthStar SSA\n4 launched by cutoff', source_url='https://northstar-data.com/space-situational-awareness-satellites-northstar-1-launch/'),

# Payload nodes
    Payload(id='adsb_drag_payload', label='ADS-B receiver + drag sail', title='ADS-B receiver + drag sail', source_url='https://www.utias-sfl.net/canx-7/'),
    Payload(id='ais_receiver', label='AIS receiver', title='AIS receiver', source_url='https://www.eoportal.org/satellite-missions/ev-9'),
    Payload(id='frontier_payload', label='Mini Plasma Imager + deployable boom', title='Mini Plasma Imager + deployable boom', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve'),
    Payload(id='ghg_hosted_sensors', label='ABB methane / CO₂ sensor payloads', title='ABB methane / CO₂ sensor payloads', source_url='https://www.ghgsat.com/en/newsroom/worlds-first-commercial-co2-sensor-in-orbit/'),
    Payload(id='ghg_spectrometer', label='GHG imaging spectrometer', title='GHG imaging spectrometer\nInstrument family.', source_url='https://amt.copernicus.org/articles/14/2127/2021/'),
    Payload(id='marmot_radio', label='Open modular radio / ionospheric sounding', title='Open modular radio / ionospheric sounding', source_url='https://www.marmotsat.ca/'),

# Spacecraft nodes
    Spacecraft(id='aether_1_2', label='ÆTHER-1/2 optical pathfinders', title='ÆTHER-1/2 optical pathfinders\nÆTHER-1 catalog decay: 2026-07-19; ÆTHER-2 remained catalogued in orbit. Ten ~300 kg 2026 optical satellites are excluded.\nLaunch/deployment: Falcon 9 Transporter-9 · 2023-11-11.', source_url='https://kepler.space/kepler-validates-sda-compatible-optical-technology-for-space-data-relay-constellation/', is_early_failure=False),
    Spacecraft(id='aissat2', label='AISSat-2', title='AISSat-2\n~6.5 kg\nExtended-life\nLaunch/deployment: Soyuz-2.1b/Fregat · 2014-07-08.', source_url='https://www.eoportal.org/satellite-missions/aissat-nanosatellite-constellation', is_early_failure=False),
    Spacecraft(id='aissat3', label='AISSat-3', title='AISSat-3\n7 kg · launch failure\nEarly/launch failure\nLaunch/deployment: Soyuz-2.1b failure · 2017-11-28 (launch attempt failed).', source_url='https://sflmissions.com/aissat-3/', is_early_failure=True),
    Spacecraft(id='aissat4', label='AISSat-4', title='AISSat-4\nSPARTAN 6U\nLaunch/deployment: Falcon 9 Transporter-16 · 2026-03-30.', source_url='https://sflmissions.com/aissat-4-maritime-monitoring/', is_early_failure=False),
    Spacecraft(id='aurorasat', label='AuroraSat', title='AuroraSat\n2U / 3U conflict\nRetired; scope qualification unresolved\nLaunch/deployment: CRS-27 / NRCSD-25 · launch 2023-03-15 UTC · deploy 2023-04-24–28.', source_url='https://albertasat.ca/northern-spirit/', is_early_failure=False),
    Spacecraft(id='brite_heweliusz', label='BRITE-PL-2 / Heweliusz', title='BRITE-PL-2 / Heweliusz\n~7 kg\nLaunch/deployment: Long March-4B · 2014-08-19.', source_url='https://www.eoportal.org/satellite-missions/brite-poland', is_early_failure=False),
    Spacecraft(id='brite_lem', label='BRITE-PL-1 / Lem', title='BRITE-PL-1 / Lem\n~7 kg\nLaunch/deployment: Dnepr-1 · 2013-11-21.', source_url='https://www.eoportal.org/satellite-missions/brite-poland', is_early_failure=False),
    Spacecraft(id='brite_montreal', label='BRITE-Montréal / CA-2', title='BRITE-Montréal / CA-2\n~7 kg · no separation\nLaunched 2014-06-19 but did not detach from the launch vehicle.\nEarly/launch failure', source_url='https://www.eoportal.org/satellite-missions/brite-canada', is_early_failure=True),
    Spacecraft(id='brite_toronto', label='BRITE-Toronto / CA-1', title='BRITE-Toronto / CA-1\n~7 kg\nLaunch/deployment: Dnepr-1 · 2014-06-19.', source_url='https://sflmissions.com/brite-toronto-brite-montreal/', is_early_failure=False),
    Spacecraft(id='canx4', label='CanX-4', title='CanX-4\nmass disputed: 7 or 15 kg\nScope qualification unresolved\nLaunch/deployment: PSLV-C23 · 2014-06-30.', source_url='https://www.eoportal.org/satellite-missions/canx-4-5', is_early_failure=False),
    Spacecraft(id='canx5', label='CanX-5', title='CanX-5\nmass disputed: 7 or 15 kg\nScope qualification unresolved\nLaunch/deployment: PSLV-C23 · 2014-06-30.', source_url='https://www.eoportal.org/satellite-missions/canx-4-5', is_early_failure=False),
    Spacecraft(id='canx7', label='CanX-7', title='CanX-7\n3–3.5 kg · 3U\nRecovered sources differ between 3 and 3.5 kg. Seven-month ADS-B campaign; drag sails deployed 2017-05; re-entered 2022-04-21.\nRetired\nLaunch/deployment: PSLV-C35 · 2016-09-26.', source_url='https://www.utias-sfl.net/canx-7/', is_early_failure=False),
    Spacecraft(id='case_sat', label='CASE', title='CASE\n3U\nCatalog decay 2023-02-23. Numbered Kepler aliases vary across company/catalog sources and are not normalized here.\nRetired\nLaunch/deployment: PSLV-C43 · 2018-11-29.', source_url='https://kepler.space/first-launch/', is_early_failure=False),
    Spacecraft(id='claire', label='GHGSat-D / Claire', title='GHGSat-D / Claire\n~15 kg\nRetired\nLaunch/deployment: PSLV-C34 · 2016-06-22 UTC.', source_url='https://www.eoportal.org/satellite-missions/ghgsat-d', is_early_failure=False),
    Spacecraft(id='descent_ab', label='DESCENT Mother/Daughter', title='DESCENT Mother/Daughter\n2 × 1U\nLaunch/deployment: ISS deployment · 2020-11-05.', source_url='http://www.yorku.ca/edtsat/', is_early_failure=False),
    Spacecraft(id='dmsat1', label='DMSat-1', title='DMSat-1\n15 kg\nLaunch/deployment: Soyuz rideshare · 2021-03-22.', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/', is_early_failure=False),
    Spacecraft(id='dragonette1', label='Dragonette-1', title='Dragonette-1\n6U\nLaunch/deployment: Falcon 9 Transporter-7 · 2023-04-15.', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', is_early_failure=False),
    Spacecraft(id='dragonette2', label='Dragonette-2', title='Dragonette-2\n6U\nLaunch/deployment: Falcon 9 Transporter-8 · 2023-06-12.', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', is_early_failure=False),
    Spacecraft(id='dragonette3', label='Dragonette-3', title='Dragonette-3\n6U\nLaunch/deployment: Falcon 9 Transporter-9 · 2023-11-11.', source_url='https://www.wyvern.space/blog/dragonette-003-wyvern-expands-its-global-reach', is_early_failure=False),
    Spacecraft(id='dragonette4', label='Dragonette-4', title='Dragonette-4\nOperational and counted in Dragonette size; not stated as a CubeSat. <=20 kg qualification is unresolved.\nScope qualification unresolved\nLaunch/deployment: Falcon 9 Transporter-13 · 2025-03-15.', source_url='https://www.wyvern.space/blog/dragonette-004-hyperspectral-intelligence-from-orbit', is_early_failure=False),
    Spacecraft(id='dragonette5', label='Dragonette-5', title='Dragonette-5\nLaunched 2025-11-28; not stated as CubeSat.\nLaunch/deployment: Falcon 9 Transporter-15 · 2025-11-28.', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', is_early_failure=False),
    Spacecraft(id='essence', label='ESSENCE', title='ESSENCE\nDeployed; generic ISS-object mapping prevents an individual decay-date assignment.\nLaunch/deployment: CRS-28 / NRCSD-26 · launch 2023-06-05 · deploy 2023-07-06.', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', is_early_failure=False),
    Spacecraft(id='ev9', label='exactView-9 / EV9', title='exactView-9 / EV9\n5.5–6 kg\nLaunch/deployment: PSLV-C30 · 2015-09-28.', source_url='https://www.eoportal.org/satellite-missions/ev-9', is_early_failure=False),
    Spacecraft(id='exalta1', label='Ex-Alta 1', title='Ex-Alta 1\n2.64 kg · 3U\nRetired\nLaunch/deployment: ISS deployment · 2017-05-26.', source_url='https://www.ualberta.ca/en/science/space/albertasat.html', is_early_failure=False),
    Spacecraft(id='exalta2', label='Ex-Alta 2', title='Ex-Alta 2\n3U\nCelesTrak decay 2023-10-28\nRetired\nLaunch/deployment: CRS-27 / NRCSD-25 · launch 2023-03-15 UTC · deploy 2023-04-24–28.', source_url='https://albertasat.ca/ex-alta-2/', is_early_failure=False),
    Spacecraft(id='exalta3', label='Ex-Alta 3', title='Ex-Alta 3\nplanned 3U allocation\nPlanned', source_url='https://albertasat.ca/', is_early_failure=False),
    Spacecraft(id='frontiersat', label='FrontierSat / CTS-SAT-1', title='FrontierSat / CTS-SAT-1\n3U\nIndependent student CubeSat; planned operations at least three years.\nLaunch/deployment: Falcon 9 CAS500-2 rideshare · 2026-05-03.', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve', is_early_failure=False),
    Spacecraft(id='ghgsat_c1', label='GHGSat C1 / Iris', title='GHGSat C1 / Iris\n15 kg\nLaunch/deployment: Vega VV16 / SSMS · 2020-09-03 UTC.', source_url='https://www.utias.utoronto.ca/sfl/', is_early_failure=False),
    Spacecraft(id='ghgsat_c12_13', label='GHGSat C12–C13', title='GHGSat C12–C13\n2 × 15 kg\nLaunch/deployment: Falcon 9 Transporter-14 · 2025-06-23.', source_url='https://www.ghgsat.com/en/newsroom/ghgsat-successfully-launches-two-new-satellites-unlocking-unprecedented-daily-global-methane-monitoring-abilities/', is_early_failure=False),
    Spacecraft(id='ghgsat_c14_15', label='GHGSat C14–C15 hosted craft', title='GHGSat C14–C15 hosted craft\n2 × 16U\nLaunch/deployment: Falcon 9 Transporter-15 · 2025-11-28.', source_url='https://www.ghgsat.com/en/newsroom/ghgsat-successfully-launches-two-new-satellites/', is_early_failure=False),
    Spacecraft(id='ghgsat_c16_17', label='GHGSat C16–C17 hosted pair', title='GHGSat C16–C17 hosted pair\nLaunch/deployment: Falcon 9 Transporter-17 · 2026-07-07 UTC.', source_url='https://www.ghgsat.com/resources/ghgsats-two-new-methane-monitoring-satellites-eleonore-c-16-and-nuray-c-17-will-soon-take-flight/', is_early_failure=False),
    Spacecraft(id='ghgsat_c2', label='GHGSat C2 / Hugo', title='GHGSat C2 / Hugo\n15 kg\nLaunch/deployment: Falcon 9 Transporter-1 · 2021-01-24.', source_url='https://www.ghgsat.com/resources/satellite-greenhouse-gas-monitoring/', is_early_failure=False),
    Spacecraft(id='ghgsat_c3_5', label='GHGSat C3–C5', title='GHGSat C3–C5\n3 × 15 kg\nLaunch/deployment: Falcon 9 Transporter-5 · 2022-05-25.', source_url='https://www.newswire.com/news/greenhouse-gas-monitoring-from-space-ghgsat-launches-three-new-21721749', is_early_failure=False),
    Spacecraft(id='ghgsat_c6_8', label='GHGSat C6–C8', title='GHGSat C6–C8\n3 × 15 kg\nLaunch/deployment: Falcon 9 Transporter-7 · 2023-04-15.', source_url='https://www.ghgsat.com/en/newsroom/new-satellites-to-accelerate-the-fight-against-climate-change-launched-into-orbit-with-spacex/', is_early_failure=False),
    Spacecraft(id='ghgsat_c9_11', label='GHGSat C9–C11 hosted craft', title='GHGSat C9–C11 hosted craft\n3 × 16U\nLaunch/deployment: Falcon 9 Transporter-9 · 2023-11-11.', source_url='https://www.ghgsat.com/en/newsroom/worlds-first-commercial-co2-sensor-in-orbit/', is_early_failure=False),
    Spacecraft(id='globalstar2_spacecraft', label='Globalstar second-generation spacecraft', title='Globalstar second-generation spacecraft\n≈700 kg launch mass\nOutside the ≤20 kg census scope', source_url='http://www.starsem.com/news/Globalstar-2-gen-feature-9.htm', is_early_failure=False),
    Spacecraft(id='hawkeye_pathfinder_sats', label='Hawk A/B/C', title='Hawk A/B/C\n3 × NEMO 15 kg platform class\nLaunch/deployment: Falcon 9 SSO-A · 2018-12-03.', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/', is_early_failure=False),
    Spacecraft(id='helios_biu', label='Helios Wire BIU', title='Helios Wire BIU\n6U · launch failure\nEarly/launch failure\nLaunch/deployment: Soyuz-2.1b failure · 2017-11-28 (launch attempt failed).', source_url='https://www.nanosats.eu/sat/helios-sirion', is_early_failure=True),
    Spacecraft(id='helios_pathfinder2', label='Helios Pathfinder II', title='Helios Pathfinder II\n6U\nReported healthy after deployment.\nLaunch/deployment: Falcon 9 SSO-A · 2018-12-03.', source_url='https://helioswire.com/news/', is_early_failure=False),
    Spacecraft(id='heron_mk2', label='HERON Mk. II', title='HERON Mk. II\n3U\nLaunch/deployment: Falcon 9 Transporter-9 · 2023-11-11.', source_url='https://www.utias.utoronto.ca/news/utat-division-launches-first-satellite-into-space/', is_early_failure=False),
    Spacecraft(id='icecube_arcticsat', label='IceCube / ArcticSat?', title='IceCube / ArcticSat?\nplanned 3U allocation\nPlanned; scope qualification unresolved', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', is_early_failure=False),
    Spacecraft(id='iris_ccp', label='IRIS / ManitobaSat-1', title='IRIS / ManitobaSat-1\nDeployed; generic ISS-object mapping prevents an individual decay-date assignment.\nLaunch/deployment: CRS-28 / NRCSD-26 · launch 2023-06-05 · deploy 2023-07-06.', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', is_early_failure=False),
    Spacecraft(id='kepler_16_19', label='Kepler-16–19', title="Kepler-16–19\n4 × 6U-XL; ~12 kg RF class\nActual launch 2022-01-13 on Transporter-3; the company page's displayed 2021 date conflicts with catalog/mission identity. Approximate 12 kg is an RF-class comparison, not an individual wet mass.\nLaunch/deployment: Falcon 9 Transporter-3 · 2022-01-13.", source_url='https://kepler.space/kepler-announces-successful-launch-of-4-new-gen1-satellites-including-test-bed-for-aether-service/', is_early_failure=False),
    Spacecraft(id='kepler_20_21', label='Kepler-20/21', title='Kepler-20/21\n2 × 6U; ~12 kg RF class\nLaunch/deployment: Falcon 9 Transporter-7 · 2023-04-15.', source_url='https://sflmissions.com/kepler-k20-k21/', is_early_failure=False),
    Spacecraft(id='kepler_4_5', label='Kepler-4/5', title='Kepler-4/5\n2 × 6U-XL\nLaunch/deployment: Soyuz rideshare · 2020-09-28.', source_url='https://www.globenewswire.com/news-release/2020/09/28/2099934/0/en/Kepler-Communications-Announces-Successful-Launch-of-New-GEN1-Satellites.html', is_early_failure=False),
    Spacecraft(id='kepler_6_7', label='Kepler-6/7', title='Kepler-6/7\n2 × 6U-XL\nA later Kepler filing compares the RF class at approximately 12 kg. End status not asserted.\nLaunch/deployment: Soyuz rideshare · 2021-03-22.', source_url='https://kepler.space/kepler-communications-announces-successful-launch-of-2-new-gen1-satellites-creating-the-largest-constellation-by-a-canadian-company/', is_early_failure=False),
    Spacecraft(id='kepler_8_15', label='Kepler-8–15', title='Kepler-8–15\n8 × 6U-XL\nLaunch/deployment: Falcon 9 Transporter-1 · 2021-01-24.', source_url='https://kepler.space/kepler-communications-announces-successful-launch-of-8-new-gen1-satellites/', is_early_failure=False),
    Spacecraft(id='killick1', label='Killick-1', title='Killick-1\n2U\nDeployed and later decayed; precise object/date not assigned; wet mass unknown.\nRetired\nLaunch/deployment: CRS-30 / NRCSD-27 · launch 2024-03-21 · deploy 2024-04-18.', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', is_early_failure=False),
    Spacecraft(id='killick2', label='Killick-2 / MUNStar-1?', title='Killick-2 / MUNStar-1?\nplanned 3U allocation\nPlanned; scope qualification unresolved', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', is_early_failure=False),
    Spacecraft(id='kipp', label='KIPP', title='KIPP\n3U\nNumbered Kepler aliases vary across company/catalog sources and are not normalized here.\nRetired\nLaunch/deployment: Long March 11 · 2018-01-19.', source_url='https://kepler.space/first-launch/', is_early_failure=False),
    Spacecraft(id='lemur_krish', label='LEMUR-2-KRISH host', title='LEMUR-2-KRISH host\nScope qualification unresolved\nLaunch/deployment: Falcon 9 Transporter-14 · 2025-06-23.', source_url='https://missioncontrolspace.com/mission-persistence/', is_early_failure=False),
    Spacecraft(id='loris', label='LORIS / DUCS', title='LORIS / DUCS\n2U\nRetired\nLaunch/deployment: CRS-26 / NRCSD-24 · launch 2022-11-26 · deploy 2022-12-29.', source_url='https://www.dal.ca/news/2023/09/15/dalhousie-satellite-mantis-space.html', is_early_failure=False),
    Spacecraft(id='mantis', label='MANTIS', title='MANTIS\nplanned 3U allocation\nPlanned', source_url='https://www.dal.ca/news/2023/09/15/dalhousie-satellite-mantis-space.html', is_early_failure=False),
    Spacecraft(id='marmotsat', label='MARMOTSat', title='MARMOTSat\n3U\nIn-orbit commissioning after 2026-07-07 launch.\nLaunch/deployment: Falcon 9 Transporter-17 · 2026-07-07 UTC.', source_url='https://www.marmotsat.ca/', is_early_failure=False),
    Spacecraft(id='mobius1', label='MÖBIUS-1', title='MÖBIUS-1\n3U\nLaunch/deployment: Falcon 9 Transporter-14 · 2025-06-23.', source_url='https://www.asc-csa.gc.ca/eng/blog/2025/06/25/multiple-csa-funded-technologies-take-flight-on-latest-rideshare-mission.asp', is_early_failure=False),
    Spacecraft(id='neudose', label='NEUDOSE', title='NEUDOSE\nCelesTrak decay 2023-11-27.\nRetired\nLaunch/deployment: CRS-27 / NRCSD-25 · launch 2023-03-15 UTC · deploy 2023-04-24–28.', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', is_early_failure=False),
    Spacecraft(id='norsat3', label='NorSat-3', title="NorSat-3\n15–16.5 kg\nPrimary/secondary sources disagree between 15 and 16.5 kg; both are within the graph's borderline range.\nLaunch/deployment: Vega VV18 · 2021-04-29.", source_url='https://www.utias-sfl.net/norsat-3/', is_early_failure=False),
    Spacecraft(id='northstar_cluster1', label='NorthStar-1 cluster', title='NorthStar-1 cluster\n4 × 16U\nLaunch/deployment: Rocket Lab Electron · 2024-01-31 UTC.', source_url='https://northstar-data.com/space-situational-awareness-satellites-northstar-1-launch/', is_early_failure=False),
    Spacecraft(id='orcasat', label='ORCASat', title='ORCASat\n2U\nCelesTrak decay 2023-07-07.\nRetired\nLaunch/deployment: CRS-26 / NRCSD-24 · launch 2022-11-26 · deploy 2022-12-29.', source_url='https://asd.gsfc.nasa.gov/orcas/news/orcasat.html', is_early_failure=False),
    Spacecraft(id='preset', label='PRESET', title='PRESET\nplanned 3U\nPlanned', source_url='https://physics.mcmaster.ca/preset-mcmasters-2nd-satellite-development-project-funded-by-canadian-space-agency/', is_early_failure=False),
    Spacecraft(id='qmsat', label='QMSat / UdeSat', title='QMSat / UdeSat\n2U\nDeployed and later decayed; precise object/date not assigned; wet mass unknown.\nRetired\nLaunch/deployment: CRS-30 / NRCSD-27 · launch 2024-03-21 · deploy 2024-04-18.', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', is_early_failure=False),
    Spacecraft(id='radsat_sk', label='RADSAT-SK / IDRSat', title='RADSAT-SK / IDRSat\n2U / 3U conflict\nRetrieved catalogues conflict on 2U versus 3U; wet mass unknown; individual ISS-object decay mapping unresolved.\nScope qualification unresolved\nLaunch/deployment: CRS-28 / NRCSD-26 · launch 2023-06-05 · deploy 2023-07-06.', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', is_early_failure=False),
    Spacecraft(id='radsat_sk2', label='RADSAT-SK2', title='RADSAT-SK2\nplanned 3U allocation\nPlanned', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', is_early_failure=False),
    Spacecraft(id='sc_freyr', label='SC-FREYR', title='SC-FREYR\nplanned 3U allocation\nPlanned', source_url='https://spaceconcordia.ca/spacecraft', is_early_failure=False),
    Spacecraft(id='sc_odin', label='SC-ODIN', title='SC-ODIN\n3U · ~4 kg\nApproximate 4 kg mass; generic ISS-object mapping prevents an individual decay date assignment.\nLaunch/deployment: CRS-28 / NRCSD-26 · launch 2023-06-05 · deploy 2023-07-06.', source_url='https://spaceconcordia.ca/spacecraft', is_early_failure=False),
    Spacecraft(id='skyaana', label="SKYA'ANAsat", title="SKYA'ANAsat\nPlanned; scope qualification unresolved", source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', is_early_failure=False),
    Spacecraft(id='spudnik1', label='SpudNik-1', title='SpudNik-1\nselected; no launch confirmed\nPlanned', source_url='https://projects.upei.ca/spudnik1/', is_early_failure=False),
    Spacecraft(id='tars', label='TARS', title='TARS\n6U\nNumbered Kepler aliases vary across company/catalog sources and are not normalized here.\nRetired\nLaunch/deployment: Vega VV16 / SSMS · 2020-09-03 UTC.', source_url='https://kepler.space/first-launch/', is_early_failure=False),
    Spacecraft(id='tugsat1', label='BRITE-Austria / TUGSAT-1', title='BRITE-Austria / TUGSAT-1\n~7 kg\nExceeded its planned two-year mission and delivered data for more than ten years.\nExtended-life\nLaunch/deployment: PSLV-C20 · 2013-02-25.', source_url='https://www.tugraz.at/en/institute/iks/space-missions/brite-austria-tugsat-1', is_early_failure=False),
    Spacecraft(id='ukpik1', label='Ukpik-1', title='Ukpik-1\n2U\nDeployed; generic ISS-object mapping prevents an individual decay-date assignment; wet mass unknown.\nLaunch/deployment: CRS-28 / NRCSD-26 · launch 2023-06-05 · deploy 2023-07-06.', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', is_early_failure=False),
    Spacecraft(id='unibrite', label='UniBRITE / CanX-3A', title='UniBRITE / CanX-3A\n~7 kg\nLaunch/deployment: PSLV-C20 · 2013-02-25.', source_url='https://www.eoportal.org/satellite-missions/brite-canada', is_early_failure=False),
    Spacecraft(id='violet', label='VIOLET / CubeSat NB', title='VIOLET / CubeSat NB\n2U\nDeployed and later decayed; precise object/date not assigned; wet mass unknown.\nRetired\nLaunch/deployment: CRS-30 / NRCSD-27 · launch 2024-03-21 · deploy 2024-04-18.', source_url='https://www.unb.ca/initiatives/cubesat/radio.html', is_early_failure=False),
    Spacecraft(id='western_skylark', label='Western Skylark', title='Western Skylark\nplanned 3U\nPlanned', source_url='https://space.uwo.ca/research/Missions%20and%20Instruments/Skylark.html', is_early_failure=False),
    Spacecraft(id='yukonsat', label='YukonSat', title='YukonSat\n2U\nDeployment reported 2023-04-28; CelesTrak decay 2023-11-11; actual mass unknown.\nRetired\nLaunch/deployment: CRS-27 / NRCSD-25 · launch 2023-03-15 UTC · deploy 2023-04-24–28.', source_url='https://albertasat.ca/northern-spirit/', is_early_failure=False),

]

NODES_BY_ID = {node.id: node for node in NODES}



# %% Relations

@dataclass(frozen=True)
class RelationRecord:
    """Operational wrapper around an ontology Edge and its endpoints.

    `detail` preserves the more specific wording from the source atlas for hover
    text without introducing a new ontology relation type.
    """

    source: str
    target: str
    edge: Edge
    detail: str = ""


RELATIONS = [
    RelationRecord(source='dubai_municipality', target='dmsat1', edge=Commissions(id='commissions_dubai_municipality_dmsat1', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/', status='unknown'), detail='commissions'),
    RelationRecord(source='ghgsat', target='ghgsat_constellation', edge=Commissions(id='commissions_ghgsat_ghgsat_constellation', source_url='https://www.ghgsat.com/en/technology/constellation/', status='unknown'), detail='commissions payload missions / provides data'),
    RelationRecord(source='norway_space_agency', target='aissat3', edge=Commissions(id='commissions_norway_space_agency_aissat3', source_url='https://sflmissions.com/aissat-3/', status='unknown'), detail='commissions'),
    RelationRecord(source='norway_space_agency', target='aissat4', edge=Commissions(id='commissions_norway_space_agency_aissat4', source_url='https://sflmissions.com/aissat-4-maritime-monitoring/', status='unknown'), detail='commissions'),
    RelationRecord(source='norway_space_agency', target='norsat3', edge=Commissions(id='commissions_norway_space_agency_norsat3', source_url='https://www.utias-sfl.net/norsat-3/', status='unknown'), detail='commissions'),
    RelationRecord(source='aissat2', target='ais_receiver', edge=Contains(id='contains_aissat2_ais_receiver', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='carries'),
    RelationRecord(source='aissat3', target='ais_receiver', edge=Contains(id='contains_aissat3_ais_receiver', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='carries'),
    RelationRecord(source='aissat4', target='ais_receiver', edge=Contains(id='contains_aissat4_ais_receiver', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='carries'),
    RelationRecord(source='aissat_constellation', target='aissat2', edge=Contains(id='contains_aissat_constellation_aissat2', source_url='https://www.eoportal.org/satellite-missions/aissat-nanosatellite-constellation', status='unknown'), detail='uses — constellation membership'),
    RelationRecord(source='aissat_constellation', target='aissat3', edge=Contains(id='contains_aissat_constellation_aissat3', source_url='https://sflmissions.com/aissat-3/', status='unknown'), detail='attempted follow-on — constellation membership'),
    RelationRecord(source='aissat_constellation', target='aissat4', edge=Contains(id='contains_aissat_constellation_aissat4', source_url='https://sflmissions.com/aissat-4-maritime-monitoring/', status='unknown'), detail='2026 follow-on — constellation membership'),
    RelationRecord(source='brite_constellation', target='brite_heweliusz', edge=Contains(id='contains_brite_constellation_brite_heweliusz', source_url='https://www.eoportal.org/satellite-missions/brite-poland', status='unknown'), detail='includes'),
    RelationRecord(source='brite_constellation', target='brite_lem', edge=Contains(id='contains_brite_constellation_brite_lem', source_url='https://www.eoportal.org/satellite-missions/brite-poland', status='unknown'), detail='includes'),
    RelationRecord(source='brite_constellation', target='brite_montreal', edge=Contains(id='contains_brite_constellation_brite_montreal', source_url='https://www.eoportal.org/satellite-missions/brite-canada', status='unknown'), detail='includes; deployment failed'),
    RelationRecord(source='brite_constellation', target='brite_toronto', edge=Contains(id='contains_brite_constellation_brite_toronto', source_url='https://sflmissions.com/brite-toronto-brite-montreal/', status='unknown'), detail='includes'),
    RelationRecord(source='brite_constellation', target='tugsat1', edge=Contains(id='contains_brite_constellation_tugsat1', source_url='https://www.tugraz.at/en/institute/iks/space-missions/brite-austria-tugsat-1', status='unknown'), detail='includes'),
    RelationRecord(source='brite_constellation', target='unibrite', edge=Contains(id='contains_brite_constellation_unibrite', source_url='https://www.eoportal.org/satellite-missions/brite-canada', status='unknown'), detail='includes'),
    RelationRecord(source='canx7', target='adsb_drag_payload', edge=Contains(id='contains_canx7_adsb_drag_payload', source_url='https://www.utias-sfl.net/canx-7/', status='unknown'), detail='carries'),
    RelationRecord(source='claire', target='ghg_spectrometer', edge=Contains(id='contains_claire_ghg_spectrometer', source_url='https://amt.copernicus.org/articles/14/2127/2021/', status='unknown'), detail='carries'),
    RelationRecord(source='dragonette_constellation', target='dragonette1', edge=Contains(id='contains_dragonette_constellation_dragonette1', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', status='unknown'), detail='includes'),
    RelationRecord(source='dragonette_constellation', target='dragonette2', edge=Contains(id='contains_dragonette_constellation_dragonette2', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', status='unknown'), detail='includes'),
    RelationRecord(source='dragonette_constellation', target='dragonette3', edge=Contains(id='contains_dragonette_constellation_dragonette3', source_url='https://www.wyvern.space/blog/dragonette-003-wyvern-expands-its-global-reach', status='unknown'), detail='includes'),
    RelationRecord(source='dragonette_constellation', target='dragonette4', edge=Contains(id='contains_dragonette_constellation_dragonette4', source_url='https://www.wyvern.space/blog/dragonette-004-hyperspectral-intelligence-from-orbit', status='unknown'), detail='includes · scope pending'),
    RelationRecord(source='dragonette_constellation', target='dragonette5', edge=Contains(id='contains_dragonette_constellation_dragonette5', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', status='unknown'), detail='includes · scope pending'),
    RelationRecord(source='ev9', target='ais_receiver', edge=Contains(id='contains_ev9_ais_receiver', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='carries'),
    RelationRecord(source='exactview_constellation', target='ev9', edge=Contains(id='contains_exactview_constellation_ev9', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='part of — reversed part-of to contains'),
    RelationRecord(source='frontiersat', target='frontier_payload', edge=Contains(id='contains_frontiersat_frontier_payload', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve', status='unknown'), detail='carries'),
    RelationRecord(source='ghgsat_c9_11', target='ghg_hosted_sensors', edge=Contains(id='contains_ghgsat_c9_11_ghg_hosted_sensors', source_url='https://www.ghgsat.com/en/newsroom/worlds-first-commercial-co2-sensor-in-orbit/', status='unknown'), detail='carries'),
    RelationRecord(source='ghgsat_constellation', target='claire', edge=Contains(id='contains_ghgsat_constellation_claire', source_url='https://www.eoportal.org/satellite-missions/ghgsat-d', status='unknown'), detail='includes'),
    RelationRecord(source='ghgsat_constellation', target='ghgsat_c1', edge=Contains(id='contains_ghgsat_constellation_ghgsat_c1', source_url='https://www.utias.utoronto.ca/sfl/', status='unknown'), detail='includes'),
    RelationRecord(source='ghgsat_constellation', target='ghgsat_c12_13', edge=Contains(id='contains_ghgsat_constellation_ghgsat_c12_13', source_url='https://www.ghgsat.com/en/newsroom/ghgsat-successfully-launches-two-new-satellites-unlocking-unprecedented-daily-global-methane-monitoring-abilities/', status='unknown'), detail='includes'),
    RelationRecord(source='ghgsat_constellation', target='ghgsat_c14_15', edge=Contains(id='contains_ghgsat_constellation_ghgsat_c14_15', source_url='https://www.ghgsat.com/en/newsroom/ghgsat-successfully-launches-two-new-satellites/', status='unknown'), detail='hosted payloads on'),
    RelationRecord(source='ghgsat_constellation', target='ghgsat_c16_17', edge=Contains(id='contains_ghgsat_constellation_ghgsat_c16_17', source_url='https://www.ghgsat.com/resources/ghgsats-two-new-methane-monitoring-satellites-eleonore-c-16-and-nuray-c-17-will-soon-take-flight/', status='unknown'), detail='hosted payloads on'),
    RelationRecord(source='ghgsat_constellation', target='ghgsat_c2', edge=Contains(id='contains_ghgsat_constellation_ghgsat_c2', source_url='https://www.ghgsat.com/resources/satellite-greenhouse-gas-monitoring/', status='unknown'), detail='includes'),
    RelationRecord(source='ghgsat_constellation', target='ghgsat_c3_5', edge=Contains(id='contains_ghgsat_constellation_ghgsat_c3_5', source_url='https://www.newswire.com/news/greenhouse-gas-monitoring-from-space-ghgsat-launches-three-new-21721749', status='unknown'), detail='includes'),
    RelationRecord(source='ghgsat_constellation', target='ghgsat_c6_8', edge=Contains(id='contains_ghgsat_constellation_ghgsat_c6_8', source_url='https://www.ghgsat.com/en/newsroom/new-satellites-to-accelerate-the-fight-against-climate-change-launched-into-orbit-with-spacex/', status='unknown'), detail='includes'),
    RelationRecord(source='ghgsat_constellation', target='ghgsat_c9_11', edge=Contains(id='contains_ghgsat_constellation_ghgsat_c9_11', source_url='https://www.ghgsat.com/en/newsroom/worlds-first-commercial-co2-sensor-in-orbit/', status='unknown'), detail='hosted payloads on'),
    RelationRecord(source='globalstar_constellation', target='globalstar2_spacecraft', edge=Contains(id='contains_globalstar_constellation_globalstar2_spacecraft', source_url='http://www.starsem.com/news/Globalstar-2-gen-feature-9.htm', status='unknown'), detail='includes second-generation craft'),
    RelationRecord(source='hawkeye_constellation', target='hawkeye_pathfinder_sats', edge=Contains(id='contains_hawkeye_constellation_hawkeye_pathfinder_sats', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/', status='unknown'), detail='includes'),
    RelationRecord(source='helios_constellation', target='helios_biu', edge=Contains(id='contains_helios_constellation_helios_biu', source_url='https://www.nanosats.eu/sat/helios-sirion', status='unknown'), detail='includes'),
    RelationRecord(source='helios_constellation', target='helios_pathfinder2', edge=Contains(id='contains_helios_constellation_helios_pathfinder2', source_url='https://helioswire.com/news/', status='unknown'), detail='includes'),
    RelationRecord(source='kepler_aether_pathfinders', target='aether_1_2', edge=Contains(id='contains_kepler_aether_pathfinders_aether_1_2', source_url='https://kepler.space/kepler-validates-sda-compatible-optical-technology-for-space-data-relay-constellation/', status='unknown'), detail='includes'),
    RelationRecord(source='kepler_rf_constellation', target='case_sat', edge=Contains(id='contains_kepler_rf_constellation_case_sat', source_url='https://kepler.space/first-launch/', status='unknown'), detail='includes'),
    RelationRecord(source='kepler_rf_constellation', target='kepler_16_19', edge=Contains(id='contains_kepler_rf_constellation_kepler_16_19', source_url='https://kepler.space/kepler-announces-successful-launch-of-4-new-gen1-satellites-including-test-bed-for-aether-service/', status='unknown'), detail='includes'),
    RelationRecord(source='kepler_rf_constellation', target='kepler_20_21', edge=Contains(id='contains_kepler_rf_constellation_kepler_20_21', source_url='https://sflmissions.com/kepler-k20-k21/', status='unknown'), detail='includes'),
    RelationRecord(source='kepler_rf_constellation', target='kepler_4_5', edge=Contains(id='contains_kepler_rf_constellation_kepler_4_5', source_url='https://www.globenewswire.com/news-release/2020/09/28/2099934/0/en/Kepler-Communications-Announces-Successful-Launch-of-New-GEN1-Satellites.html', status='unknown'), detail='includes'),
    RelationRecord(source='kepler_rf_constellation', target='kepler_6_7', edge=Contains(id='contains_kepler_rf_constellation_kepler_6_7', source_url='https://kepler.space/kepler-communications-announces-successful-launch-of-2-new-gen1-satellites-creating-the-largest-constellation-by-a-canadian-company/', status='unknown'), detail='includes'),
    RelationRecord(source='kepler_rf_constellation', target='kepler_8_15', edge=Contains(id='contains_kepler_rf_constellation_kepler_8_15', source_url='https://kepler.space/kepler-communications-announces-successful-launch-of-8-new-gen1-satellites/', status='unknown'), detail='includes'),
    RelationRecord(source='kepler_rf_constellation', target='kipp', edge=Contains(id='contains_kepler_rf_constellation_kipp', source_url='https://kepler.space/first-launch/', status='unknown'), detail='includes'),
    RelationRecord(source='kepler_rf_constellation', target='tars', edge=Contains(id='contains_kepler_rf_constellation_tars', source_url='https://kepler.space/first-launch/', status='unknown'), detail='includes'),
    RelationRecord(source='marmotsat', target='marmot_radio', edge=Contains(id='contains_marmotsat_marmot_radio', source_url='https://www.marmotsat.ca/', status='unknown'), detail='carries'),
    RelationRecord(source='norsat3', target='ais_receiver', edge=Contains(id='contains_norsat3_ais_receiver', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='carries'),
    RelationRecord(source='northern_spirit', target='aurorasat', edge=Contains(id='contains_northern_spirit_aurorasat', source_url='https://albertasat.ca/northern-spirit/', status='unknown'), detail='includes'),
    RelationRecord(source='northern_spirit', target='exalta2', edge=Contains(id='contains_northern_spirit_exalta2', source_url='https://albertasat.ca/ex-alta-2/', status='unknown'), detail='includes'),
    RelationRecord(source='northern_spirit', target='yukonsat', edge=Contains(id='contains_northern_spirit_yukonsat', source_url='https://albertasat.ca/northern-spirit/', status='unknown'), detail='includes'),
    RelationRecord(source='northstar_constellation', target='northstar_cluster1', edge=Contains(id='contains_northstar_constellation_northstar_cluster1', source_url='https://northstar-data.com/space-situational-awareness-satellites-northstar-1-launch/', status='unknown'), detail='includes'),
    RelationRecord(source='aac_clyde', target='case_sat', edge=Develops(id='develops_aac_clyde_case_sat', source_url='https://kepler.space/first-launch/', status='unknown'), detail='builds'),
    RelationRecord(source='aac_clyde', target='kipp', edge=Develops(id='develops_aac_clyde_kipp', source_url='https://kepler.space/first-launch/', status='unknown'), detail='builds'),
    RelationRecord(source='aac_clyde', target='tars', edge=Develops(id='develops_aac_clyde_tars', source_url='https://kepler.space/first-launch/', status='unknown'), detail='builds / integrates'),
    RelationRecord(source='abb_canada', target='ghg_hosted_sensors', edge=Develops(id='develops_abb_canada_ghg_hosted_sensors', source_url='https://www.ghgsat.com/en/newsroom/worlds-first-commercial-co2-sensor-in-orbit/', status='unknown'), detail='builds'),
    RelationRecord(source='aurora_college', target='aurorasat', edge=Develops(id='develops_aurora_college_aurorasat', source_url='https://albertasat.ca/northern-spirit/', status='unknown'), detail='lead team / payload'),
    RelationRecord(source='concordia', target='sc_freyr', edge=Develops(id='develops_concordia_sc_freyr', source_url='https://spaceconcordia.ca/spacecraft', status='unknown'), detail='leads · CAD 350,000'),
    RelationRecord(source='concordia', target='sc_odin', edge=Develops(id='develops_concordia_sc_odin', source_url='https://spaceconcordia.ca/spacecraft', status='unknown'), detail='lead team builds'),
    RelationRecord(source='dalhousie', target='loris', edge=Develops(id='develops_dalhousie_loris', source_url='https://www.dal.ca/news/2023/09/15/dalhousie-satellite-mantis-space.html', status='unknown'), detail='lead team builds'),
    RelationRecord(source='dalhousie', target='mantis', edge=Develops(id='develops_dalhousie_mantis', source_url='https://www.dal.ca/news/2023/09/15/dalhousie-satellite-mantis-space.html', status='unknown'), detail='leads · CAD 349,740'),
    RelationRecord(source='galaxia', target='mobius_mission', edge=Develops(id='develops_galaxia_mobius_mission', source_url='https://www.asc-csa.gc.ca/eng/blog/2025/06/25/multiple-csa-funded-technologies-take-flight-on-latest-rideshare-mission.asp', status='unknown'), detail='builds'),
    RelationRecord(source='kepler', target='kepler_16_19', edge=Develops(id='develops_kepler_kepler_16_19', source_url='https://kepler.space/kepler-announces-successful-launch-of-4-new-gen1-satellites-including-test-bed-for-aether-service/', status='unknown'), detail='builds'),
    RelationRecord(source='kepler', target='kepler_20_21', edge=Develops(id='develops_kepler_kepler_20_21', source_url='https://sflmissions.com/kepler-k20-k21/', status='unknown'), detail='builds'),
    RelationRecord(source='mcmaster', target='neudose', edge=Develops(id='develops_mcmaster_neudose', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='lead team builds'),
    RelationRecord(source='mcmaster', target='preset', edge=Develops(id='develops_mcmaster_preset', source_url='https://physics.mcmaster.ca/preset-mcmasters-2nd-satellite-development-project-funded-by-canadian-space-agency/', status='unknown'), detail='leads · CAD 350,000'),
    RelationRecord(source='memorial', target='killick1', edge=Develops(id='develops_memorial_killick1', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='lead team builds'),
    RelationRecord(source='memorial', target='killick2', edge=Develops(id='develops_memorial_killick2', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', status='unknown'), detail='leads · CAD 350,000'),
    RelationRecord(source='mpb', target='ghg_spectrometer', edge=Develops(id='develops_mpb_ghg_spectrometer', source_url='https://amt.copernicus.org/articles/14/2127/2021/', status='unknown'), detail='builds demonstrator payload'),
    RelationRecord(source='nunavut_college', target='ukpik1', edge=Develops(id='develops_nunavut_college_ukpik1', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='co-leads — lead/co-lead mapped to develops'),
    RelationRecord(source='sfl_missions', target='aissat4', edge=Develops(id='develops_sfl_missions_aissat4', source_url='https://sflmissions.com/aissat-4-maritime-monitoring/', status='unknown'), detail='builds'),
    RelationRecord(source='sfl_missions', target='ghgsat_c12_13', edge=Develops(id='develops_sfl_missions_ghgsat_c12_13', source_url='https://www.ghgsat.com/en/newsroom/ghgsat-successfully-launches-two-new-satellites-unlocking-unprecedented-daily-global-methane-monitoring-abilities/', status='unknown'), detail='builds'),
    RelationRecord(source='spire', target='ghgsat_c14_15', edge=Develops(id='develops_spire_ghgsat_c14_15', source_url='https://www.ghgsat.com/en/newsroom/ghgsat-successfully-launches-two-new-satellites/', status='unknown'), detail='builds'),
    RelationRecord(source='spire', target='ghgsat_c16_17', edge=Develops(id='develops_spire_ghgsat_c16_17', source_url='https://www.ghgsat.com/resources/ghgsats-two-new-methane-monitoring-satellites-eleonore-c-16-and-nuray-c-17-will-soon-take-flight/', status='unknown'), detail='builds'),
    RelationRecord(source='spire', target='ghgsat_c9_11', edge=Develops(id='develops_spire_ghgsat_c9_11', source_url='https://www.ghgsat.com/en/newsroom/worlds-first-commercial-co2-sensor-in-orbit/', status='unknown'), detail='builds'),
    RelationRecord(source='spire', target='lemur_krish', edge=Develops(id='develops_spire_lemur_krish', source_url='https://missioncontrolspace.com/mission-persistence/', status='unknown'), detail='builds host spacecraft'),
    RelationRecord(source='spire', target='northstar_cluster1', edge=Develops(id='develops_spire_northstar_cluster1', source_url='https://northstar-data.com/space-situational-awareness-satellites-northstar-1-launch/', status='unknown'), detail='builds'),
    RelationRecord(source='ualberta', target='aurorasat', edge=Develops(id='develops_ualberta_aurorasat', source_url='https://albertasat.ca/northern-spirit/', status='unknown'), detail='builds bus'),
    RelationRecord(source='ualberta', target='exalta1', edge=Develops(id='develops_ualberta_exalta1', source_url='https://www.ualberta.ca/en/science/space/albertasat.html', status='unknown'), detail='builds'),
    RelationRecord(source='ualberta', target='exalta2', edge=Develops(id='develops_ualberta_exalta2', source_url='https://albertasat.ca/ex-alta-2/', status='unknown'), detail='lead team builds'),
    RelationRecord(source='ualberta', target='exalta3', edge=Develops(id='develops_ualberta_exalta3', source_url='https://albertasat.ca/', status='unknown'), detail='leads · CAD 348,700'),
    RelationRecord(source='ualberta', target='yukonsat', edge=Develops(id='develops_ualberta_yukonsat', source_url='https://albertasat.ca/northern-spirit/', status='unknown'), detail='builds bus'),
    RelationRecord(source='ucalgary', target='frontier_mission', edge=Develops(id='develops_ucalgary_frontier_mission', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve', status='unknown'), detail='leads — lead/co-lead mapped to develops'),
    RelationRecord(source='ucalgary', target='frontiersat', edge=Develops(id='develops_ucalgary_frontiersat', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve', status='unknown'), detail='builds'),
    RelationRecord(source='umanitoba', target='icecube_arcticsat', edge=Develops(id='develops_umanitoba_icecube_arcticsat', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', status='unknown'), detail='leads · CAD 349,992'),
    RelationRecord(source='umanitoba', target='iris_ccp', edge=Develops(id='develops_umanitoba_iris_ccp', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='lead team builds'),
    RelationRecord(source='unb', target='violet', edge=Develops(id='develops_unb_violet', source_url='https://www.unb.ca/initiatives/cubesat/radio.html', status='unknown'), detail='lead team builds'),
    RelationRecord(source='uoft', target='aissat2', edge=Develops(id='develops_uoft_aissat2', source_url='https://www.eoportal.org/satellite-missions/aissat-nanosatellite-constellation', status='unknown'), detail='builds'),
    RelationRecord(source='uoft', target='aissat3', edge=Develops(id='develops_uoft_aissat3', source_url='https://sflmissions.com/aissat-3/', status='unknown'), detail='builds'),
    RelationRecord(source='uoft', target='brite_mission', edge=Develops(id='develops_uoft_brite_mission', source_url='https://www.asc-csa.gc.ca/eng/satellites/brite/', status='unknown'), detail='designs / leads engineering'),
    RelationRecord(source='uoft', target='canx45_mission', edge=Develops(id='develops_uoft_canx45_mission', source_url='https://www.eoportal.org/satellite-missions/canx-4-5', status='unknown'), detail='develops'),
    RelationRecord(source='uoft', target='canx7', edge=Develops(id='develops_uoft_canx7', source_url='https://www.utias-sfl.net/canx-7/', status='unknown'), detail='develops / builds'),
    RelationRecord(source='uoft', target='claire', edge=Develops(id='develops_uoft_claire', source_url='https://www.eoportal.org/satellite-missions/ghgsat-d', status='unknown'), detail='builds'),
    RelationRecord(source='uoft', target='dmsat1', edge=Develops(id='develops_uoft_dmsat1', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/', status='unknown'), detail='builds'),
    RelationRecord(source='uoft', target='ev9', edge=Develops(id='develops_uoft_ev9', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='builds'),
    RelationRecord(source='uoft', target='ghgsat_c1', edge=Develops(id='develops_uoft_ghgsat_c1', source_url='https://www.utias.utoronto.ca/sfl/', status='unknown'), detail='builds'),
    RelationRecord(source='uoft', target='ghgsat_c2', edge=Develops(id='develops_uoft_ghgsat_c2', source_url='https://www.ghgsat.com/resources/satellite-greenhouse-gas-monitoring/', status='unknown'), detail='builds'),
    RelationRecord(source='uoft', target='ghgsat_c3_5', edge=Develops(id='develops_uoft_ghgsat_c3_5', source_url='https://www.newswire.com/news/greenhouse-gas-monitoring-from-space-ghgsat-launches-three-new-21721749', status='unknown'), detail='UTIAS SFL program develops'),
    RelationRecord(source='uoft', target='ghgsat_c6_8', edge=Develops(id='develops_uoft_ghgsat_c6_8', source_url='https://www.ghgsat.com/en/newsroom/new-satellites-to-accelerate-the-fight-against-climate-change-launched-into-orbit-with-spacex/', status='unknown'), detail='UTIAS SFL program develops'),
    RelationRecord(source='uoft', target='hawkeye_pathfinder_sats', edge=Develops(id='develops_uoft_hawkeye_pathfinder_sats', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/', status='unknown'), detail='builds'),
    RelationRecord(source='uoft', target='heron_mk2', edge=Develops(id='develops_uoft_heron_mk2', source_url='https://www.utias.utoronto.ca/news/utat-division-launches-first-satellite-into-space/', status='unknown'), detail='builds'),
    RelationRecord(source='uoft', target='kepler_4_5', edge=Develops(id='develops_uoft_kepler_4_5', source_url='https://www.globenewswire.com/news-release/2020/09/28/2099934/0/en/Kepler-Communications-Announces-Successful-Launch-of-New-GEN1-Satellites.html', status='unknown'), detail='develops GEN1 platform'),
    RelationRecord(source='uoft', target='norsat3', edge=Develops(id='develops_uoft_norsat3', source_url='https://www.utias-sfl.net/norsat-3/', status='unknown'), detail='builds'),
    RelationRecord(source='upei', target='spudnik1', edge=Develops(id='develops_upei_spudnik1', source_url='https://projects.upei.ca/spudnik1/', status='unknown'), detail='lead team develops'),
    RelationRecord(source='usask', target='radsat_sk', edge=Develops(id='develops_usask_radsat_sk', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='lead team builds'),
    RelationRecord(source='usask', target='radsat_sk2', edge=Develops(id='develops_usask_radsat_sk2', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', status='unknown'), detail='leads · CAD 350,000'),
    RelationRecord(source='usherbrooke', target='qmsat', edge=Develops(id='develops_usherbrooke_qmsat', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='lead team builds'),
    RelationRecord(source='uvic', target='marmotsat', edge=Develops(id='develops_uvic_marmotsat', source_url='https://www.marmotsat.ca/', status='unknown'), detail='builds'),
    RelationRecord(source='uvic', target='orcasat', edge=Develops(id='develops_uvic_orcasat', source_url='https://asd.gsfc.nasa.gov/orcas/news/orcasat.html', status='unknown'), detail='lead team builds'),
    RelationRecord(source='uvic', target='skyaana', edge=Develops(id='develops_uvic_skyaana', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', status='unknown'), detail='leads · CAD 349,600'),
    RelationRecord(source='western', target='ukpik1', edge=Develops(id='develops_western_ukpik1', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='co-leads'),
    RelationRecord(source='western', target='western_skylark', edge=Develops(id='develops_western_western_skylark', source_url='https://space.uwo.ca/research/Missions%20and%20Instruments/Skylark.html', status='unknown'), detail='leads · CAD 350,000'),
    RelationRecord(source='york', target='descent_mission', edge=Develops(id='develops_york_descent_mission', source_url='http://www.yorku.ca/edtsat/', status='unknown'), detail='develops'),
    RelationRecord(source='york', target='essence', edge=Develops(id='develops_york_essence', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='lead team builds'),
    RelationRecord(source='yukon_u', target='yukonsat', edge=Develops(id='develops_yukon_u_yukonsat', source_url='https://albertasat.ca/northern-spirit/', status='unknown'), detail='lead team / payload'),
    RelationRecord(source='com_dev', target='canx7_mission', edge=Funds(id='funds_com_dev_canx7_mission', source_url='https://www.utias-sfl.net/canx-7/', status='unknown'), detail='funds / payload — explicit funds component'),
    RelationRecord(source='csa', target='brite_mission', edge=Funds(id='funds_csa_brite_mission', source_url='https://sflmissions.com/brite-toronto-brite-montreal/', status='unknown'), detail='funds Canadian participation'),
    RelationRecord(source='csa', target='canx45_mission', edge=Funds(id='funds_csa_canx45_mission', source_url='https://www.eoportal.org/satellite-missions/canx-4-5', status='unknown'), detail='funds'),
    RelationRecord(source='csa', target='ccp', edge=Develops(id='develops_csa_ccp', source_url='https://www.asc-csa.gc.ca/eng/funding-programs/funding-opportunities/ao/2017-canadian-cubesat-project.asp', status='unknown'), detail='leads'),
    RelationRecord(source='csa', target='ccp', edge=Funds(id='funds_csa_ccp', source_url='https://www.asc-csa.gc.ca/eng/funding-programs/funding-opportunities/ao/2017-canadian-cubesat-project.asp', status='unknown'), detail='funds'),
    RelationRecord(source='csa', target='cubics', edge=Funds(id='funds_csa_cubics', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubics/about.asp', status='unknown'), detail='funds 9 grants'),
    RelationRecord(source='csa', target='exalta1_mission', edge=Funds(id='funds_csa_exalta1_mission', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/ex-alta-1.asp', status='unknown'), detail='funds'),
    RelationRecord(source='csa', target='mobius_mission', edge=Funds(id='funds_csa_mobius_mission', source_url='https://www.asc-csa.gc.ca/eng/blog/2025/06/25/multiple-csa-funded-technologies-take-flight-on-latest-rideshare-mission.asp', status='unknown'), detail='contributes CAD 1.9M'),
    RelationRecord(source='drdc', target='canx45_mission', edge=Funds(id='funds_drdc_canx45_mission', source_url='https://www.eoportal.org/satellite-missions/canx-4-5', status='unknown'), detail='funds'),
    RelationRecord(source='drdc', target='canx7_mission', edge=Funds(id='funds_drdc_canx7_mission', source_url='https://www.utias-sfl.net/canx-7/', status='unknown'), detail='funds'),
    RelationRecord(source='nserc', target='canx45_mission', edge=Funds(id='funds_nserc_canx45_mission', source_url='https://www.eoportal.org/satellite-missions/canx-4-5', status='unknown'), detail='funds'),
    RelationRecord(source='nserc', target='canx7_mission', edge=Funds(id='funds_nserc_canx7_mission', source_url='https://www.utias-sfl.net/canx-7/', status='unknown'), detail='funds'),
    RelationRecord(source='aac_clyde', target='dragonette1', edge=Operates(id='operates_aac_clyde_dragonette1', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', status='unknown'), detail='owns / operates under SDaaS'),
    RelationRecord(source='aac_clyde', target='dragonette2', edge=Operates(id='operates_aac_clyde_dragonette2', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', status='unknown'), detail='owns / operates under SDaaS'),
    RelationRecord(source='aac_clyde', target='dragonette3', edge=Operates(id='operates_aac_clyde_dragonette3', source_url='https://www.wyvern.space/blog/dragonette-003-wyvern-expands-its-global-reach', status='unknown'), detail='owns / operates under SDaaS'),
    RelationRecord(source='dubai_municipality', target='dmsat1', edge=Operates(id='operates_dubai_municipality_dmsat1', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/', status='unknown'), detail='operates'),
    RelationRecord(source='ets_lassena', target='pnt_research', edge=Operates(id='operates_ets_lassena_pnt_research', source_url='https://doi.org/10.1177/09544100221113123', status='unknown'), detail='authors / conducts — service provider represented as service operator'),
    RelationRecord(source='exactearth', target='ev9', edge=Operates(id='operates_exactearth_ev9', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='owns / operates'),
    RelationRecord(source='exactearth', target='maritime_ais', edge=Operates(id='operates_exactearth_maritime_ais', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='provides — service provider represented as service operator'),
    RelationRecord(source='galaxia', target='mobius_mission', edge=Operates(id='operates_galaxia_mobius_mission', source_url='https://www.asc-csa.gc.ca/eng/blog/2025/06/25/multiple-csa-funded-technologies-take-flight-on-latest-rideshare-mission.asp', status='unknown'), detail='operates'),
    RelationRecord(source='ghgsat', target='ghg_service', edge=Operates(id='operates_ghgsat_ghg_service', source_url='https://www.ghgsat.com/en/technology/constellation/', status='unknown'), detail='provides — service provider represented as service operator'),
    RelationRecord(source='globalstar_inc', target='globalstar_constellation', edge=Operates(id='operates_globalstar_inc_globalstar_constellation', source_url='https://www.globalstar.com/en-us/about/who', status='unknown'), detail='owns / operates'),
    RelationRecord(source='hawkeye360', target='hawkeye_pathfinder_sats', edge=Operates(id='operates_hawkeye360_hawkeye_pathfinder_sats', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/', status='unknown'), detail='owns / operates'),
    RelationRecord(source='helios_wire', target='helios_constellation', edge=Operates(id='operates_helios_wire_helios_constellation', source_url='https://www.nanosats.eu/sat/helios-sirion', status='unknown'), detail='operates'),
    RelationRecord(source='kepler', target='kepler_16_19', edge=Operates(id='operates_kepler_kepler_16_19', source_url='https://kepler.space/kepler-announces-successful-launch-of-4-new-gen1-satellites-including-test-bed-for-aether-service/', status='unknown'), detail='operates'),
    RelationRecord(source='kepler', target='kepler_20_21', edge=Operates(id='operates_kepler_kepler_20_21', source_url='https://sflmissions.com/kepler-k20-k21/', status='unknown'), detail='operates'),
    RelationRecord(source='kepler', target='kepler_aether_pathfinders', edge=Operates(id='operates_kepler_kepler_aether_pathfinders', source_url='https://kepler.space/kepler-validates-sda-compatible-optical-technology-for-space-data-relay-constellation/', status='unknown'), detail='operates'),
    RelationRecord(source='kepler', target='kepler_pathfinders', edge=Operates(id='operates_kepler_kepler_pathfinders', source_url='https://kepler.space/first-launch/', status='unknown'), detail='operates'),
    RelationRecord(source='kepler', target='kepler_rf_constellation', edge=Operates(id='operates_kepler_kepler_rf_constellation', source_url='https://kepler.space/kepler-raises-92-million-usd-series-c-to-complete-internet-ready-optical-constellation-3/', status='unknown'), detail='operates'),
    RelationRecord(source='kepler', target='satcom_iot', edge=Operates(id='operates_kepler_satcom_iot', source_url='https://kepler.space/first-launch/', status='unknown'), detail='provides — service provider represented as service operator'),
    RelationRecord(source='loft_orbital', target='dragonette4', edge=Operates(id='operates_loft_orbital_dragonette4', source_url='https://www.wyvern.space/blog/dragonette-004-hyperspectral-intelligence-from-orbit', status='unknown'), detail='hosts / operates'),
    RelationRecord(source='loft_orbital', target='dragonette5', edge=Operates(id='operates_loft_orbital_dragonette5', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', status='unknown'), detail='hosts / operates'),
    RelationRecord(source='mission_control', target='persistence_mission', edge=Operates(id='operates_mission_control_persistence_mission', source_url='https://missioncontrolspace.com/mission-persistence/', status='unknown'), detail='owns / operates software mission'),
    RelationRecord(source='northstar', target='ssa_service', edge=Operates(id='operates_northstar_ssa_service', source_url='https://northstar-data.com/space-situational-awareness-satellites-northstar-1-launch/', status='unknown'), detail='provides — service provider represented as service operator'),
    RelationRecord(source='norway_space_agency', target='aissat2', edge=Operates(id='operates_norway_space_agency_aissat2', source_url='https://www.eoportal.org/satellite-missions/aissat-nanosatellite-constellation', status='unknown'), detail='owns / operates'),
    RelationRecord(source='norway_space_agency', target='aissat4', edge=Operates(id='operates_norway_space_agency_aissat4', source_url='https://sflmissions.com/aissat-4-maritime-monitoring/', status='unknown'), detail='operates'),
    RelationRecord(source='norway_space_agency', target='norsat3', edge=Operates(id='operates_norway_space_agency_norsat3', source_url='https://www.utias-sfl.net/norsat-3/', status='unknown'), detail='operates'),
    RelationRecord(source='spire', target='ghgsat_c14_15', edge=Operates(id='operates_spire_ghgsat_c14_15', source_url='https://www.ghgsat.com/en/newsroom/ghgsat-successfully-launches-two-new-satellites/', status='unknown'), detail='operates'),
    RelationRecord(source='spire', target='ghgsat_c16_17', edge=Operates(id='operates_spire_ghgsat_c16_17', source_url='https://www.ghgsat.com/resources/ghgsats-two-new-methane-monitoring-satellites-eleonore-c-16-and-nuray-c-17-will-soon-take-flight/', status='unknown'), detail='operates'),
    RelationRecord(source='spire', target='ghgsat_c9_11', edge=Operates(id='operates_spire_ghgsat_c9_11', source_url='https://www.ghgsat.com/en/newsroom/worlds-first-commercial-co2-sensor-in-orbit/', status='unknown'), detail='operates'),
    RelationRecord(source='spire', target='northstar_cluster1', edge=Operates(id='operates_spire_northstar_cluster1', source_url='https://northstar-data.com/space-situational-awareness-satellites-northstar-1-launch/', status='unknown'), detail='operates'),
    RelationRecord(source='ualberta', target='exalta1', edge=Operates(id='operates_ualberta_exalta1', source_url='https://www.ualberta.ca/en/science/space/albertasat.html', status='unknown'), detail='operates'),
    RelationRecord(source='ucalgary', target='frontiersat', edge=Operates(id='operates_ucalgary_frontiersat', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve', status='unknown'), detail='operates'),
    RelationRecord(source='uoft', target='heron_mk2', edge=Operates(id='operates_uoft_heron_mk2', source_url='https://www.utias.utoronto.ca/news/utat-division-launches-first-satellite-into-space/', status='unknown'), detail='operates'),
    RelationRecord(source='uvic', target='marmotsat', edge=Operates(id='operates_uvic_marmotsat', source_url='https://www.marmotsat.ca/', status='unknown'), detail='operates'),
    RelationRecord(source='wyvern', target='hyperspectral_service', edge=Operates(id='operates_wyvern_hyperspectral_service', source_url='https://guide.wyvern.space/data-product-guide/technical-specifications/dragonette-constellation/', status='unknown'), detail='provides — service provider represented as service operator'),
    RelationRecord(source='york', target='descent_mission', edge=Operates(id='operates_york_descent_mission', source_url='http://www.yorku.ca/edtsat/', status='unknown'), detail='operates'),
    RelationRecord(source='brite_mission', target='brite_constellation', edge=Uses(id='uses_brite_mission_brite_constellation', source_url='https://www.asc-csa.gc.ca/eng/satellites/brite/', status='unknown'), detail='uses'),
    RelationRecord(source='canx45_mission', target='canx4', edge=Uses(id='uses_canx45_mission_canx4', source_url='https://www.eoportal.org/satellite-missions/canx-4-5', status='unknown'), detail='uses'),
    RelationRecord(source='canx45_mission', target='canx5', edge=Uses(id='uses_canx45_mission_canx5', source_url='https://www.eoportal.org/satellite-missions/canx-4-5', status='unknown'), detail='uses'),
    RelationRecord(source='canx7_mission', target='canx7', edge=Uses(id='uses_canx7_mission_canx7', source_url='https://www.utias-sfl.net/canx-7/', status='unknown'), detail='uses'),
    RelationRecord(source='ccp', target='aurorasat', edge=Uses(id='uses_ccp_aurorasat', source_url='https://albertasat.ca/northern-spirit/', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='essence', edge=Uses(id='uses_ccp_essence', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='exalta2', edge=Uses(id='uses_ccp_exalta2', source_url='https://albertasat.ca/ex-alta-2/', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='iris_ccp', edge=Uses(id='uses_ccp_iris_ccp', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='killick1', edge=Uses(id='uses_ccp_killick1', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='loris', edge=Uses(id='uses_ccp_loris', source_url='https://www.dal.ca/news/2023/09/15/dalhousie-satellite-mantis-space.html', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='neudose', edge=Uses(id='uses_ccp_neudose', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='orcasat', edge=Uses(id='uses_ccp_orcasat', source_url='https://asd.gsfc.nasa.gov/orcas/news/orcasat.html', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='qmsat', edge=Uses(id='uses_ccp_qmsat', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='radsat_sk', edge=Uses(id='uses_ccp_radsat_sk', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='sc_odin', edge=Uses(id='uses_ccp_sc_odin', source_url='https://spaceconcordia.ca/spacecraft', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='spudnik1', edge=Uses(id='uses_ccp_spudnik1', source_url='https://projects.upei.ca/spudnik1/', status='unknown'), detail='selected; no flight'),
    RelationRecord(source='ccp', target='ukpik1', edge=Uses(id='uses_ccp_ukpik1', source_url='https://www.asc-csa.gc.ca/eng/satellites/cubesat/selected-teams-map.asp', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='violet', edge=Uses(id='uses_ccp_violet', source_url='https://www.unb.ca/initiatives/cubesat/radio.html', status='unknown'), detail='includes'),
    RelationRecord(source='ccp', target='yukonsat', edge=Uses(id='uses_ccp_yukonsat', source_url='https://albertasat.ca/northern-spirit/', status='unknown'), detail='includes'),
    RelationRecord(source='cubics', target='exalta3', edge=Uses(id='uses_cubics_exalta3', source_url='https://albertasat.ca/', status='unknown'), detail='supports announced project'),
    RelationRecord(source='cubics', target='icecube_arcticsat', edge=Uses(id='uses_cubics_icecube_arcticsat', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', status='unknown'), detail='supports announced project'),
    RelationRecord(source='cubics', target='killick2', edge=Uses(id='uses_cubics_killick2', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', status='unknown'), detail='supports announced project'),
    RelationRecord(source='cubics', target='mantis', edge=Uses(id='uses_cubics_mantis', source_url='https://www.dal.ca/news/2023/09/15/dalhousie-satellite-mantis-space.html', status='unknown'), detail='supports probable project identity'),
    RelationRecord(source='cubics', target='marmotsat', edge=Uses(id='uses_cubics_marmotsat', source_url='https://www.marmotsat.ca/', status='unknown'), detail='confirmed CUBICS launch; award-name link unresolved'),
    RelationRecord(source='cubics', target='preset', edge=Uses(id='uses_cubics_preset', source_url='https://physics.mcmaster.ca/preset-mcmasters-2nd-satellite-development-project-funded-by-canadian-space-agency/', status='unknown'), detail='supports announced project'),
    RelationRecord(source='cubics', target='radsat_sk2', edge=Uses(id='uses_cubics_radsat_sk2', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', status='unknown'), detail='supports announced project'),
    RelationRecord(source='cubics', target='sc_freyr', edge=Uses(id='uses_cubics_sc_freyr', source_url='https://spaceconcordia.ca/spacecraft', status='unknown'), detail='supports announced project'),
    RelationRecord(source='cubics', target='skyaana', edge=Uses(id='uses_cubics_skyaana', source_url='https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html', status='unknown'), detail='supports 2023 UVic award identity'),
    RelationRecord(source='cubics', target='western_skylark', edge=Uses(id='uses_cubics_western_skylark', source_url='https://space.uwo.ca/research/Missions%20and%20Instruments/Skylark.html', status='unknown'), detail='supports announced project'),
    RelationRecord(source='descent_mission', target='descent_ab', edge=Uses(id='uses_descent_mission_descent_ab', source_url='http://www.yorku.ca/edtsat/', status='unknown'), detail='uses'),
    RelationRecord(source='dmsat_mission', target='dmsat1', edge=Uses(id='uses_dmsat_mission_dmsat1', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/', status='unknown'), detail='uses'),
    RelationRecord(source='ets_lassena', target='drone_link_research', edge=Operates(id='operates_ets_lassena_drone_link_research', source_url='https://lassena.etsmtl.ca/specialized-infrastructure/', status='unknown'), detail='operates'),
    RelationRecord(source='drone_link_research', target='globalstar_constellation', edge=Uses(id='uses_drone_link_research_globalstar_constellation', source_url='https://www.globalstar.com/en-us/about/who', status='unknown'), detail='uses satellite links via'),
    RelationRecord(source='exalta1_mission', target='exalta1', edge=Uses(id='uses_exalta1_mission_exalta1', source_url='https://www.ualberta.ca/en/science/space/albertasat.html', status='unknown'), detail='uses'),
    RelationRecord(source='frontier_mission', target='frontiersat', edge=Uses(id='uses_frontier_mission_frontiersat', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve', status='unknown'), detail='uses'),
    RelationRecord(source='hawkeye_pathfinder', target='hawkeye_constellation', edge=Uses(id='uses_hawkeye_pathfinder_hawkeye_constellation', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/', status='unknown'), detail='uses'),
    RelationRecord(source='helios_mission', target='helios_constellation', edge=Uses(id='uses_helios_mission_helios_constellation', source_url='https://www.nanosats.eu/sat/helios-sirion', status='unknown'), detail='uses'),
    RelationRecord(source='kepler_pathfinders', target='case_sat', edge=Uses(id='uses_kepler_pathfinders_case_sat', source_url='https://kepler.space/first-launch/', status='unknown'), detail='uses'),
    RelationRecord(source='kepler_pathfinders', target='kipp', edge=Uses(id='uses_kepler_pathfinders_kipp', source_url='https://kepler.space/first-launch/', status='unknown'), detail='uses'),
    RelationRecord(source='kepler_pathfinders', target='tars', edge=Uses(id='uses_kepler_pathfinders_tars', source_url='https://kepler.space/first-launch/', status='unknown'), detail='uses'),
    RelationRecord(source='maritime_ais', target='aissat_constellation', edge=Uses(id='uses_maritime_ais_aissat_constellation', source_url='https://www.eoportal.org/satellite-missions/ev-9', status='unknown'), detail='provides — reversed service-provision to service uses constellation'),
    RelationRecord(source='mobius_mission', target='mobius1', edge=Uses(id='uses_mobius_mission_mobius1', source_url='https://www.asc-csa.gc.ca/eng/blog/2025/06/25/multiple-csa-funded-technologies-take-flight-on-latest-rideshare-mission.asp', status='unknown'), detail='uses'),
    RelationRecord(source='norsat3_mission', target='norsat3', edge=Uses(id='uses_norsat3_mission_norsat3', source_url='https://www.utias-sfl.net/norsat-3/', status='unknown'), detail='uses'),
    RelationRecord(source='optical_relay', target='kepler_aether_pathfinders', edge=Uses(id='uses_optical_relay_kepler_aether_pathfinders', source_url='https://kepler.space/kepler-validates-sda-compatible-optical-technology-for-space-data-relay-constellation/', status='unknown'), detail='demonstrates — reversed service-provision to service uses constellation'),
    RelationRecord(source='persistence_mission', target='lemur_krish', edge=Uses(id='uses_persistence_mission_lemur_krish', source_url='https://missioncontrolspace.com/mission-persistence/', status='unknown'), detail='hosted on · allocation unresolved'),
    RelationRecord(source='pnt_research', target='globalstar_constellation', edge=Uses(id='uses_pnt_research_globalstar_constellation', source_url='https://www.globalstar.com/en-us/about/who', status='unknown'), detail='uses predicted measurement from'),
    # Mission-level actor links. These complement actor-to-spacecraft/constellation
    # edges so the mission itself has the appropriate developer/operator/customer.
    RelationRecord(source='uoft', target='canx7_mission', edge=Develops(id='develops_uoft_canx7_mission', source_url='https://www.utias-sfl.net/canx-7/', status='unknown'), detail='develops'),
    RelationRecord(source='ualberta', target='exalta1_mission', edge=Develops(id='develops_ualberta_exalta1_mission', source_url='https://www.ualberta.ca/en/science/space/albertasat.html', status='unknown'), detail='develops'),
    RelationRecord(source='ualberta', target='exalta1_mission', edge=Operates(id='operates_ualberta_exalta1_mission', source_url='https://www.ualberta.ca/en/science/space/albertasat.html', status='unknown'), detail='operates'),
    RelationRecord(source='ucalgary', target='frontier_mission', edge=Operates(id='operates_ucalgary_frontier_mission', source_url='https://ucalgary.ca/news/ucalgary-we-have-liftoff-team-set-launch-citys-first-student-built-satellite-orbit-study-steve', status='unknown'), detail='operates'),
    RelationRecord(source='helios_wire', target='helios_mission', edge=Operates(id='operates_helios_wire_helios_mission', source_url='https://www.nanosats.eu/sat/helios-sirion', status='unknown'), detail='operates'),
    RelationRecord(source='hawkeye360', target='hawkeye_pathfinder', edge=Operates(id='operates_hawkeye360_hawkeye_pathfinder', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/', status='unknown'), detail='operates'),
    RelationRecord(source='uoft', target='hawkeye_pathfinder', edge=Develops(id='develops_uoft_hawkeye_pathfinder', source_url='https://www.utias-sfl.net/hawkeye-360-pathfinder/', status='unknown'), detail='develops'),
    RelationRecord(source='dubai_municipality', target='dmsat_mission', edge=Commissions(id='commissions_dubai_municipality_dmsat_mission', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/', status='unknown'), detail='commissions'),
    RelationRecord(source='dubai_municipality', target='dmsat_mission', edge=Operates(id='operates_dubai_municipality_dmsat_mission', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/', status='unknown'), detail='operates'),
    RelationRecord(source='uoft', target='dmsat_mission', edge=Develops(id='develops_uoft_dmsat_mission', source_url='https://news.satnews.com/2021/03/29/sfl-built-dmsat-1-successfully-dispatched-to-orbit-for-dubai/', status='unknown'), detail='develops'),
    RelationRecord(source='norway_space_agency', target='norsat3_mission', edge=Commissions(id='commissions_norway_space_agency_norsat3_mission', source_url='https://www.utias-sfl.net/norsat-3/', status='unknown'), detail='commissions'),
    RelationRecord(source='norway_space_agency', target='norsat3_mission', edge=Operates(id='operates_norway_space_agency_norsat3_mission', source_url='https://www.utias-sfl.net/norsat-3/', status='unknown'), detail='operates'),
    RelationRecord(source='uoft', target='norsat3_mission', edge=Develops(id='develops_uoft_norsat3_mission', source_url='https://www.utias-sfl.net/norsat-3/', status='unknown'), detail='develops'),

]

# %% Semantic validation

def _node_kind(node: Node) -> str:
    if isinstance(node, Agency):
        return "agency"
    if isinstance(node, University):
        return "university"
    if isinstance(node, Company):
        return "company"
    if isinstance(node, Mission):
        return "mission"
    if isinstance(node, Service):
        return "service"
    if isinstance(node, Constellation):
        return "constellation"
    if isinstance(node, Payload):
        return "payload"
    if isinstance(node, Spacecraft):
        return "spacecraft"
    raise TypeError(f"Unknown node type: {type(node).__name__}")


def validate_data() -> None:
    if len(NODES_BY_ID) != len(NODES):
        raise ValueError("Duplicate node IDs found.")

    edge_ids = [record.edge.id for record in RELATIONS]
    if len(edge_ids) != len(set(edge_ids)):
        raise ValueError("Duplicate edge IDs found.")

    connected = {node_id for record in RELATIONS for node_id in (record.source, record.target)}
    orphan_ids = sorted(set(NODES_BY_ID) - connected)
    if orphan_ids:
        raise ValueError(f"Orphan nodes found: {orphan_ids}")

    actor_kinds = {"agency", "university", "company"}

    for relation in RELATIONS:
        if relation.source not in NODES_BY_ID:
            raise KeyError(f"Unknown source node: {relation.source}")
        if relation.target not in NODES_BY_ID:
            raise KeyError(f"Unknown target node: {relation.target}")

        source_kind = _node_kind(NODES_BY_ID[relation.source])
        target_kind = _node_kind(NODES_BY_ID[relation.target])
        edge = relation.edge

        if isinstance(edge, Launches):
            ok = source_kind in actor_kinds and target_kind in {"spacecraft", "constellation"}
        elif isinstance(edge, Operates):
            ok = source_kind in actor_kinds and target_kind in {
                "spacecraft", "constellation", "mission", "service"
            }
        elif isinstance(edge, Uses):
            ok = source_kind in {"mission", "service"} and target_kind in {
                "spacecraft", "constellation"
            }
        elif isinstance(edge, Contains):
            ok = (
                (source_kind == "spacecraft" and target_kind == "payload")
                or (source_kind == "constellation" and target_kind == "spacecraft")
            )
        elif isinstance(edge, Develops):
            ok = source_kind in actor_kinds and target_kind in {
                "mission", "spacecraft", "constellation", "payload"
            }
        else:
            # The supplied ontology does not state endpoint constraints for
            # Funds or Commissions, so validation intentionally does not invent any.
            ok = True

        if not ok:
            raise ValueError(
                f"Invalid endpoints for {type(edge).__name__}: "
                f"{relation.source} ({source_kind}) -> "
                f"{relation.target} ({target_kind})"
            )


validate_data()


# %% PyVis helpers

def _node_hover(node: Node) -> str:
    return f"{node.title}\n\nSource: {node.source_url}"


def _edge_hover(record: RelationRecord) -> str:
    pieces = [record.edge.label]
    if record.detail:
        pieces.append(record.detail)
    pieces.append(f"Source: {record.edge.source_url}")
    return "\n".join(pieces)


def build_network(
    *,
    height: str = "900px",
    width: str = "100%",
    show_edge_labels: bool = True,
) -> Network:
    net = Network(
        height=height,
        width=width,
        directed=True,
        bgcolor="#000000",
        font_color="#ffffff",
        notebook=False,
        cdn_resources="in_line",
        filter_menu=True,
    )

    for node in NODES:
        net.add_node(
            node.id,
            label=node.label,
            title=_node_hover(node),
            color=node.color,
            shape=node.shape,
            source_url=node.source_url,
        )

    for record in RELATIONS:
        edge = record.edge
        net.add_edge(
            record.source,
            record.target,
            id=edge.id,
            label=edge.label if show_edge_labels else "",
            title=_edge_hover(record),
            color=edge.color,
            arrows="to",
            source_url=edge.source_url,
        )

    net.set_options(
        """
        {
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "multiselect": true
          },
          "nodes": {
            "borderWidth": 1,
            "font": {
              "size": 14,
              "face": "Arial",
              "color": "#ffffff"
            }
          },
          "edges": {
            "smooth": {
              "enabled": true,
              "type": "dynamic"
            },
            "font": {
              "size": 10,
              "align": "middle",
              "strokeWidth": 0,
              "color": "#ffffff"
            }
          },
          "physics": {
            "enabled": true,
            "solver": "repulsion",
            "stabilization": {
              "enabled": true,
              "iterations": 1800,
              "updateInterval": 50
            },
            "repulsion": {
              "nodeDistance": 180,
              "centralGravity": 0.08,
              "springLength": 160,
              "springConstant": 0.05,
              "damping": 0.12
            }
          }
        }
        """
    )
    return net


# %% Render

def render_html(
    output_path: str | Path = "canadian_nanosatellite_knowledge_graph.html",
    *,
    show_edge_labels: bool = True,
) -> Path:
    output_path = Path(output_path)
    net = build_network(show_edge_labels=show_edge_labels)
    net.write_html(str(output_path), open_browser=False, notebook=False)

    html = output_path.read_text(encoding="utf-8")
    tooltip_css = """
    <style>
      html, body { background: #000000 !important; color: #ffffff !important; }
      .vis-tooltip {
        background: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #666666 !important;
        white-space: pre-line !important;
      }
    </style>
    """
    html = html.replace("</head>", tooltip_css + "</head>")
    output_path.write_text(html, encoding="utf-8")
    return output_path.resolve()


if __name__ == "__main__":
    output = render_html()
    print(f"Wrote {output}")
    print(f"Nodes: {len(NODES)}")
    print(f"Relations: {len(RELATIONS)}")
