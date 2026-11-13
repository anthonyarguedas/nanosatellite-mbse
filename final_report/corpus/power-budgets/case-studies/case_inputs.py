"""Explicit mission-derived verification inputs and source boundaries.

All values absent from the source locators below are supplied engineering
assumptions. These are representative sections, not flight reproductions.
"""
from copy import deepcopy

SOURCES = {
 'B-cell': {'key':'birds2021batteryverification', 'locator':'Battery Verification Report, Fig. 1-1 p.21, pinned d7eadd98f5327e1ddea82b640293d49bfdb09555', 'values':'27 g x 6 = 162 g, diameter 14.35 mm, height 50.4 mm, 3S2P, 1.2 V, 3800 mAh', 'url':'https://github.com/BIRDSOpenSource/BIRDS4-ProceduresAndReports/blob/d7eadd98f5327e1ddea82b640293d49bfdb09555/Battery%28Cells%29%20Screening%20Procedures%20and%20its%20verification%20Report_V1.0%20%282%29.pdf'},
 'B-orbit': {'key':'jara2022birdsepsdataset','locator':'Section 2','values':'400 km, ISS orbit. Reference geometry and prescribed Sun/nadir pointing are supplied variations.'},
 'B-Azur': {'key':'cots-mission_azur_space_3g30a_review_legacy_ds','locator':'3G30A datasheet DB0003401-01-01, 2016-08-19 p.2','values':'AM0 1367 W/m2, 28 C. BOL Vmp=2.409 V, Imp=.5029 A, Voc=2.690 V, Isc=.5196 A. 1e15 1 MeV electrons/cm2: Vmp=2.244 V, Imp=.4851 A, Voc=2.512 V, Isc=.5013 A. Active area=.003018 m2. Complete three-anchor curve is an approximation, not a measured full curve.','url':'https://d35rpq4gusjz9h.cloudfront.net/files/73192/download/634236/73192_19_2023090605471491796.pdf'},
 'B-budget': {'key':'shrestha2022birds4powerbudget','locator':'2022 presentation pp.5,8,13','values':'428 mW x 1.5 h=642 mWh, 144 mW x 1 h=144 mWh, 280 mW x .5 h=140 mWh. p.8 beta30 eclipse35 min: (2173-240)*.8=1546 mWh rounded. p.13 (2507-240)*.8-210=1604 mWh rounded. Free rotation uses supplied external energies only.'},
 'B-IV': {'key':'shrestha2021birdssafety','locator':'Figs.13-14 pp.6-7, Maya-2 +Z two-cell panel','values':'V=5.223 at zero current, 5.123 V at 50 mA, 5.022 V at 100 mA. Printed P labels .257, .502 W and peak1.575 W. High-current x coordinates are not numerically labelled. No reconstruction of the true 1.575 W MPP is claimed.'},
 'B-rail': {'key':'kyutech2021birdsicd','locator':'Sec.6.3','values':'3.3 and 5 V rails, OC2/3/4 A regulated/Unreg2/Unreg1. Converter current capacities and efficiencies used here are supplied assumptions.'},
 'O-mass': {'key':'oresat2016csli','locator':'D.2 pp.21-22','values':'8 solar modules x31.5 g=252 g, 4 battery modules x104 g=416 g. Historical mass boundary only. All volumes and other masses supplied.'},
 'O-pack': {'key':'greenberg2021oresat','locator':'p.6','values':'Two independently protected 2S packs per card, 2.6 Ah per branch at mission nominal3.6 V/cell,37.4 Wh/card rounded. The branches share the real card bus, where currents add by Kirchhoff\'s current law. These checks retain each branch\'s ratings and do not assume a current-sharing law.'},
 'O-solar': {'key':'oresat2025solardesign','locator':'Solar Cells: GaAs','values':'XTE-SF Vmp2.43 V, Imp.483 A, Voc2.75 V, Isc.502 A, area.0027 m2,28 C AM0;2-cell output2.34 W rounded. Reference G1367 is supplied, and EOL current retention.9 is assumed. Complete three anchors are an approximation.'},
 'Si': {'key':'shrestha2026solarreliability','locator':'Table3 p.25042 and Sec.IV.C','values':'IXOLAR SSM silicon Vmp4.46 V, Imp.006 A,Voc5.53 V,Isc.0063 A, active.0000917 m2, package.008x.023 m. Curve reference1362 W/m2 supplied from article context, EOL current retention.9 assumed. Two-dimensional4x10 package layout occupies.032x.23 m if long strip, or8x5 layout.064x.115 m. Installation here is an explicit deployed.010 m2 plate, not a flush1U fit.'},
 'Li-ion': {'key':'cots-mission_tenergy_30005_0_ds','locator':'Tenergy30005-0 datasheet pp.2-4, capacity/voltage/current ratings, and O-pack for the separate mission nominal3.6 V convention','values':'2.6 Ah,2.75-4.2 V, charge1.25 A at15-45 C, discharge5 A at5-45 C. Reference temperature25 C. This case uses mission nominal3.6x2.6=9.36 Wh. The datasheet average3.65 V would give9.49 Wh and is not substituted. Neither nominal product is a measured energy guarantee.','url':'https://files.batteryjunction.com/frontend/files/tenergy/datasheet/TENERGY-30005-18650-FLAT-Datasheet.pdf'},
 'LFP': {'key':'oresatbatteryresearch','locator':'Choice#2 A123 APR18650m1-B','values':'LiFePO4,3.3 V nominal,1.1 Ah,cell2.0-3.6 V. 4S1P x2 cards29 Wh rounded. Room-temperature charge.5 A/discharge3 A and all fit/retention values are assumptions.'},
 'O-budget': {'key':'oresat2019powerbudget','locator':'2019 budget standby and battery rows','values':'1634-623=1011 mWh. Four2S3.3 Ah packs at7.2 V=95.04 Wh and60% DoD=57.024 Wh. Historical only.'},
 'O-sweep': {'key':'oresatsolarsweep','locator':'minicom.cap F2:H206; F197:H197','values':'205 published samples, row1974.435 V,.37304 A,1.6544324 W; row2 4.77625 V,.06406 A,.305966575 W. Unsorted/duplicate voltage, no endpoints. Raw curve is rejected, without sorting or invented endpoint claims.','url':'https://docs.google.com/spreadsheets/d/1vNrHLC0C6YMA_wZTWuHt7_7BPwSQPb8aQuyxLQmDAQ8/edit'},
 'O-rail': {'key':'oresat2021opddesign','locator':'OreSat Power Domain Design Notes, stated update2021-08-22, TPS62111/TPS62112 section','values':'TPS62111/12 input3.1-17 V,out3.3/5 V,max1.5 A. Efficiency.9 is supplied. The separate SPV1040 historical rejection uses oresatsolarhistory.','url':'https://docs.google.com/document/d/1NOkO6gGEJUFRpOrkwClRlZlzWuTLteq6fP9LPf_Ez0M/edit'},
 'O-protect': {'key':'oresat2025batterydesign','locator':'ABLIC selection, load current, heater and MOARPWR sections','values':'S-8209AAA per-cell UV2.50 V,OV4.10 V nominal (tolerances absent, not worst-case qualification).30 W at6/7.2/8.4 V=5/4.17/3.57 A. Local heater currents.245/.294/.342 A,OC.375 A enabled heater setting. Card electronics current.020 A supplied.'},
 'A': {'key':None,'locator':'Supplied verification assumptions in the complete input tables','values':'All lifetime/DoD fits, retentions other than stated fluence data, margins, efficiencies, allocations, unknown mass/volume, delivered-energy allocations, receiving windows, charger selections and settings, duties and load currents are supplied assumptions.'}
}

COMMON = dict(earth_radius=6378.,mu=398601.,eccentricity=0.,sun_angle=0.,
              pointing='sun_pointing',days_per_year=365.25,sun_path=.85,eclipse_path=.75,
              irradiance=1367.,inherent=.95,assembly=.97,
              available_sunlight=3000.,available_eclipse=1800.,
              tracker_min=2.0,tracker_max=12.,absolute_max=15.,source_current_limit=1.2,
              bus_tolerance=.05,battery_receiving_min=2.5,battery_receiving_max=5.0,
              battery_usable_volume_m3=.00012,
              required_charge=.4,required_discharge=.8,
              converter_efficiency=.9,converter_current=1.,converter_in_min=2.5,converter_in_max=18.,
              converter_product='LTC3119 selected5V and TPS63020-Q1 selected3.3V (complete circuits assumed)',
              source_note='A unless source map below identifies a published rating')

BIRDS = dict(COMMON,mission='BIRDS-4',altitude=400.,beta=30.,lifetime=1.,units=1,
 array=dict(product='3G30A',technology='triple-junction GaAs',series=2,parallel=1,
            vmp=2.244,imp=.4851,voc=2.512,isc=.5013,area=.003018,
            reference_irradiance=1367.,packing=.8,usable=.008,
            bol_vmp=2.409,bol_imp=.5029,bol_voc=2.690,bol_isc=.5196,retention_kind='supplied1e15fluence EOL anchors',
            curve=True,source='B-Azur'),
 battery=dict(product='BK-3MCC mission minimum-capacity convention',chemistry='NiMH',series=3,parallel=2,
              nominal=1.2,minimum=1.,maximum=1.45,cell_ah=1.9,cell_wh=2.28,
              charge_limit=.95,discharge_limit=2.,fit_a=2000.,fit_b=-1.,fit_min=.1,fit_max=.8,
              margin=.2,energy_retention=.8,capacity_retention=.8,independent_packs=1,
              cell_volume_m3=.0000082,packaging_volume_m3=.000020,temperature_C=25.,
              source='B-cell; maximum voltage/current limits, occupied envelopes and life inputs A'),
 loads=dict(states=[dict(name='main',voltage=3.3,current=.13,sun_duty=1.,eclipse_duty=1.),
                    dict(name='receiver',voltage=3.3,current=.044,sun_duty=1.,eclipse_duty=1.),
                    dict(name='beacon',voltage=5.,current=.056,sun_duty=.25,eclipse_duty=.1)],
            source='A. Near B-budget scalar levels, with independently supplied currents/duties. Whole spacecraft representative load boundary.'),
 charger=dict(product='supplied NiMH3S charger',chemistry='NiMH',series=3,
              set_voltage=4.2,allowed_min=3.9,allowed_max=4.35,current=.4,current_limit=1.9,
              termination='negative_delta_V',required_termination='negative_delta_V',source='A, engineering selection. Not the flown LTC3119 charge architecture.'),
 provenance=['B-cell','B-Azur','B-orbit','B-rail','A'])

ORESAT = dict(COMMON,mission='OreSat',altitude=550.,beta=0.,lifetime=2.,units=2,
 array=dict(product='XTE-SF',technology='triple-junction GaAs',series=2,parallel=1,
            vmp=2.43,imp=.4347,voc=2.75,isc=.4518,area=.0027,
            reference_irradiance=1367.,packing=.8,usable=.008,
            bol_vmp=2.43,bol_imp=.483,bol_voc=2.75,bol_isc=.502,retention_kind='A .9 EOL current at constant voltage',curve=True,source='O-solar'),
 battery=dict(product='Tenergy30005-0, one2S string',chemistry='Li-ion',series=2,parallel=1,
              nominal=3.6,minimum=2.75,maximum=4.2,cell_ah=2.6,cell_wh=9.36,
              charge_limit=1.25,discharge_limit=5.,fit_a=2000.,fit_b=-1.,fit_min=.1,fit_max=.8,
              margin=.2,energy_retention=.8,capacity_retention=.8,independent_packs=2,
              cell_volume_m3=.000018,packaging_volume_m3=.000020,temperature_C=25.,
              source='O-pack;Li-ion; occupied envelopes, fit and retentions A'),
 loads=dict(states=[dict(name='main',voltage=3.3,current=.06,sun_duty=1.,eclipse_duty=1.),
                    dict(name='receiver',voltage=3.3,current=.04,sun_duty=1.,eclipse_duty=1.),
                    dict(name='payload',voltage=5.,current=.2,sun_duty=.2,eclipse_duty=.1)],
            source='A. Complete representative whole-spacecraft demand, not the2019 full mission schedule.'),
 charger=dict(product='supplied2S Li-ion charger',chemistry='Li-ion',series=2,
              set_voltage=8.4,allowed_min=8.3,allowed_max=8.4,current=.4,current_limit=1.25,
              termination='CC_CV',required_termination='CC_CV',source='A,25 C current setting. Not a claim of LT1618 full charger behavior.'),
 battery_receiving_min=5.0,battery_receiving_max=9.0,battery_usable_volume_m3=.00016,
 converter_product='TPS62111/12',converter_in_min=3.1,converter_in_max=17.,converter_current=1.5,
 provenance=['O-pack','O-solar','Li-ion','O-rail','A'])

SI = dict(product='IXOLAR SSM',technology='monocrystalline silicon',series=4,parallel=10,
          vmp=4.46,imp=.0054,voc=5.53,isc=.00567,area=.0000917,reference_irradiance=1362.,
          packing=.0000917/(.008*.023),usable=.010,bol_vmp=4.46,bol_imp=.006,bol_voc=5.53,bol_isc=.0063,
          retention_kind='A .9 EOL current at constant voltage',temperature_C=28.,curve=True,
          source='Si; A40 packages on deployed .08x.125m plate. Layout8x5 uses.064x.115m. Electrical4S10P is supplied independently of physical placement. Scalar area check establishes no mechanical qualification.')
LI = dict(product='Tenergy30005-0',chemistry='Li-ion',series=1,parallel=2,
          nominal=3.6,minimum=2.75,maximum=4.2,cell_ah=2.6,cell_wh=9.36,
          charge_limit=1.25,discharge_limit=5.,fit_a=2000.,fit_b=-1.,fit_min=.1,fit_max=.8,
          margin=.2,energy_retention=.8,capacity_retention=.8,independent_packs=1,
          cell_volume_m3=.000018,packaging_volume_m3=.000020,temperature_C=25.,source='Li-ion; A occupied envelopes, fit and retentions')
LFP = dict(product='A123 APR18650m1-B',chemistry='LiFePO4',series=4,parallel=1,
           nominal=3.3,minimum=2.,maximum=3.6,cell_ah=1.1,cell_wh=3.63,
           charge_limit=.5,discharge_limit=3.,fit_a=2000.,fit_b=-1.,fit_min=.1,fit_max=.8,
           margin=.2,energy_retention=.8,capacity_retention=.8,independent_packs=2,
           cell_volume_m3=.000018,packaging_volume_m3=.000020,temperature_C=25.,
           source='LFP; A occupied envelopes, limits, fit and retentions. Two independent4S1P packs in one verification storage group. No claim that these fit a flown card. Published29Wh refers to two cards.')

# The four-cell deployment is separate from the nominal +Z body face.
# All gaps, edge clearances and package-envelope tolerances are supplied.
FOUR_CELL_DEPLOYMENT = {
 'BIRDS-4': dict(plate_width_m=.10,plate_length_m=.17,usable_area_m2=.016,
                columns=2,rows=2,package_width_m=.04015,package_length_m=.08015,
                package_dimension_tolerance_m=.0001,gap_m=.002,edge_clearance_m=.003,
                source='B-Azur nominal assembly dimensions40.15x80.15mm with source +/-0.1mm tolerance. Plate,2x2 arrangement,gaps and edge clearances are A.'),
 'OreSat': dict(plate_width_m=.10,plate_length_m=.17,usable_area_m2=.016,
               columns=2,rows=2,package_width_m=.0397,package_length_m=.0691,
               package_dimension_tolerance_m=.0001,gap_m=.002,edge_clearance_m=.003,
               source='A rectangular package envelope39.7x69.1mm, based on Spectrolab XTE-SF27cm2 nominal cell outline in the2022-07-27 datasheet p.2. CIC outer envelope is unvalidated. Envelope tolerance,plate,2x2 layout,gaps and clearances are A.')
}
SOURCES['O-package'] = dict(key='cots-solar_src_spectro_xtesf',
    locator='Spectrolab XTE-SF datasheet,2022-07-27 p.2,27cm2 rectangular cell outline',
    values='Cell outline3.97x6.91cm. The verification package envelope uses these nominal dimensions with a supplied0.1mm upper allowance. Actual CIC/contact envelope remains unvalidated.',
    url='https://www.spectrolab.com/photovoltaics/XTE-SF%20Data%20Sheet%20_07.27.22.pdf')
SOURCES['SPV'] = dict(key='oresatsolarhistory',locator='Rev2 historical design notes after1S-to2S change',
    values='Published rejection:SPV1040 cannot supply the2S charging voltage. The5.2V numeric ceiling is a declared static compatibility input in this case. No general boost envelope is inferred.',
    url='https://github.com/oresat/oresat-solar-hardware/blob/47d610c1964c31f049a8f9844f7881931b5d0f06/README.md')

BASELINES={'BIRDS-4':BIRDS,'OreSat':ORESAT}

def clone(name):
    return deepcopy(BASELINES[name])
