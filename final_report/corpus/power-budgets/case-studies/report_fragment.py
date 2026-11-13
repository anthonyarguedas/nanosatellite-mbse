"""Compact report evidence organized by requirement. No framework imports."""
import re


class Tex(str):
    """Explicit report markup, separate from escaped evidence values."""


def render(directory, results, summary, inputs):
    # A compact report must never hide an unexpected failure through selection.
    if any(row['outcome'] == 'mismatch' for row in results):
        raise ValueError('Unexpected mismatches require explicit reporting before rendering the summary.')

    def value(item):
        if isinstance(item, bool):
            return 'true' if item else 'false'
        if isinstance(item, float):
            return f'{item:.7g}'
        if isinstance(item, (list, tuple)):
            return '[' + ', '.join(value(x) for x in item) + ']'
        return str(item)

    def esc(item):
        if isinstance(item, Tex):
            return str(item)
        text = value(item)
        for old, new in [('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'),
                         ('$', r'\$'), ('#', r'\#'), ('_', r'\_\allowbreak{}')]:
            text = text.replace(old, new)
        return text.replace(',', r',\allowbreak{}').replace('/', r'/\allowbreak{}')

    def table(headers, rows, widths):
        columns = '@{}' + ' '.join(
            r'>{\raggedright\arraybackslash}p{' + f'{width * .91:.5f}' + r'\linewidth}'
            for width in widths) + '@{}'
        heading = ' & '.join(esc(x) for x in headers) + r' \\ \midrule'
        return '\n'.join([
            r'\begingroup\footnotesize\setlength{\tabcolsep}{3pt}\setlength{\parskip}{0pt}',
            r'\begin{longtable}{' + columns + '}', r'\toprule', heading, r'\endfirsthead',
            r'\toprule', heading, r'\endhead', r'\bottomrule\endfoot',
            *[' & '.join(esc(x) for x in row) + r' \\' for row in rows],
            r'\end{longtable}\endgroup'])

    missions = ('BIRDS-4', 'OreSat')
    requirements = [
        ('12', ('12',), 'Mass, volume and allocation margins'),
        ('14', ('14a', '14b'), 'Energy budgets and BOL/EOL sizing'),
        ('15', ('15',), 'Solar technology and battery chemistry'),
        ('16', ('16',), 'Series and parallel arrangements'),
        ('17', ('17',), 'Bus rails and converter compatibility'),
        ('18', ('18',), 'PV power products and sampled MPP'),
        ('19', ('19',), 'Matched DET and ideal MPPT paths'),
        ('20', ('20',), 'Normal extrema and trip comparisons'),
    ]

    def pick(mission, scenario, quantity):
        found = [row for row in results if row['mission'] == mission
                 and row['scenario'] == scenario and row['quantity'] == quantity]
        if len(found) != 1:
            raise ValueError((mission, scenario, quantity, len(found)))
        row = found[0]
        if row['actual_status'] != 'value' or row['actual'] is False:
            raise ValueError('Detailed tables select resolved quantities, not expected failure records: ' + row['id'])
        return row

    def scale(item, factor):
        if isinstance(item, (list, tuple)):
            return [scale(x, factor) for x in item]
        return item if factor == 1 else item * factor

    def display(mission, scenario, quantity, label, factor=1):
        row = pick(mission, scenario, quantity)
        basis = 'P' if row['reference_basis'] == 'published' else 'I'
        return [mission.replace('BIRDS-4', 'BIRDS'), Tex(label + ' (' + basis + ')'),
                scale(row['expected'], factor), scale(row['actual'], factor)]

    def pair(scenario, quantity, label, factor=1):
        return [display(mission, scenario, quantity, label, factor) for mission in missions]

    def comparisons(rows):
        return table(['Case', 'Quantity and reference basis', 'Reference', 'Framework'],
                     rows, [.12, .40, .24, .24])

    def deviation(rows):
        greatest = max((row['relative_error'] or 0) * 100 for row in rows)
        if greatest == 0:
            return '0'
        if greatest < 1e-10:
            return Tex(r'$<10^{-10}$')
        return f'{greatest:.3g}'

    baseline = inputs['baselines']
    b, o = (baseline[mission] for mission in missions)
    parameters = [
        ('Altitude (km)', b['altitude'], o['altitude']),
        (Tex(r'Beta angle ($^\circ$)'), b['beta'], o['beta']),
        ('Lifetime (year)', b['lifetime'], o['lifetime']),
        ('Solar arrangement', '2S1P 3G30A', '2S1P XTE-SF'),
        ('BOL cell MPP (V, A)', [b['array']['bol_vmp'], b['array']['bol_imp']],
         [o['array']['bol_vmp'], o['array']['bol_imp']]),
        ('EOL cell MPP (V, A)', [b['array']['vmp'], b['array']['imp']],
         [o['array']['vmp'], o['array']['imp']]),
        ('EOL cell Voc, Isc (V, A)', [b['array']['voc'], b['array']['isc']],
         [o['array']['voc'], o['array']['isc']]),
        (Tex(r'Cell active area (m$^2$)'), b['array']['area'], o['array']['area']),
        ('Battery arrangement', '3S2P NiMH', 'Two independent 2S1P Li-ion packs'),
        ('Cell nominal voltage (V)', b['battery']['nominal'], o['battery']['nominal']),
        ('Cell capacity (Ah)', b['battery']['cell_ah'], o['battery']['cell_ah']),
        ('Cell nominal energy (Wh)', b['battery']['cell_wh'], o['battery']['cell_wh']),
    ]
    loads = []
    for mission in missions:
        labels = {'main': 'OBC/EPS/FAB', 'receiver': 'UHF receiver', 'beacon': 'CW transmitter'} if mission == 'BIRDS-4' else {}
        for state in baseline[mission]['loads']['states']:
            loads.append([mission.replace('BIRDS-4', 'BIRDS'), labels.get(state['name'], state['name']),
                          [state['voltage'], state['current']],
                          [state['sun_duty'], state['eclipse_duty']]])

    t = [r'\chapter{EPS Case Study Evidence}\label{appendix:eps-case-studies}',
         r'''The results are organized by FR-12 and FR-14 to FR-20.
The overview gives the greatest numerical deviation for each requirement and mission across all executed numerical comparisons.
The detailed tables select representative quantities and identifiable published benchmarks.
Repeated outputs, deliberately failing configurations and missing/invalid-input records are omitted.
No unexpected mismatch was observed.

\section{Verification basis}
\label{appendix:eps-case-basis}
Each nonzero numerical output uses a 1\% relative comparison limit.
Zero values, integer counts, records and discrete outcomes require exact agreement.
I identifies an independent calculation from the stated inputs.
P identifies a published reference value.
Displayed values use seven significant figures. Deviations use unrounded values.

The electrical baselines are circular and Sun pointing.
Both use $R_E=6378$ km, $\mu=398601$ km$^3$/s$^2$ and 365.25 days per year.
Solar irradiance is 1367 W/m$^2$.
Sunlight and eclipse load-path efficiencies are 0.85 and 0.75.
The additional age-independent source derating is 0.95 and electrical assembly efficiency is 0.97.
Packing fraction is 0.8 and usable section area is 0.008 m$^2$.
These efficiencies, allocations and mission durations are assumptions.

Cell ratings come from the 3G30A datasheet, BIRDS battery documentation and OreSat component records \citep{cots-mission_azur_space_3g30a_review_legacy_ds,birds2021batteryverification,greenberg2021oresat,oresat2025solardesign,cots-mission_tenergy_30005_0_ds}.
BIRDS EOL ratings use the datasheet's $10^{15}$ 1 MeV electrons/cm$^2$ condition.
OreSat EOL current retention of 0.9 is assumed at unchanged voltage.
Nominal cell energies use the selected nominal voltage times charge capacity.
''',
         table(['Electrical input', 'BIRDS', 'OreSat'], parameters, [.42, .29, .29]),
         r'''The BIRDS power levels approximate the measured OBC/EPS/FAB, UHF receiver and CW transmitter entries \citep[p.~9]{shrestha2022birds4powerbudget}.
The voltage/current representation and the separate sunlight/eclipse duty fractions are assumed.
OreSat's 2019 power budget provides component loads and operating-mode energy budgets \citep{oresat2019powerbudget}.
The simplified OreSat profile below uses assumed voltage/current pairs and phase-specific duty fractions.
''',
         table(['Case', 'State', 'Voltage (V), current (A)', 'Sunlight, eclipse duty'],
               loads, [.12, .18, .35, .35]),
         r'''Independent scalar references use decimal sums, products, ratios and linear interpolation.
Products and ratios use 40 significant digits.
The orbital reference solves Kepler's equation on 262144 uniform time samples and tests cylindrical Earth shadow in Cartesian coordinates.
A 131072-sample calculation checks convergence.
Published comparisons retain each source's component grouping and conditions.
Ambiguous entries and inconsistent published budget arithmetic are excluded.

\section{Results by requirement}
\label{appendix:eps-case-requirements}
All numerical maxima below meet the 1\% criterion.
Integer counts, source/unit records and discrete outcomes also agree with their references.
A matching comparison establishes correct calculation for the entered case, including cases with unfavorable design verdicts.
''']
    overview = []
    for number, mops, label in requirements:
        groups = [[row for row in results if row['mission'] == mission
                   and row['mop'] in {'MOP-' + mop for mop in mops}
                   and row['actual_status'] == 'value'
                   and row['comparison_rule'].startswith('1%')]
                  for mission in missions]
        assert all(groups)
        overview.append(['FR-' + number, label, *(deviation(group) for group in groups)])
    t.append(table(['Requirement', 'Calculation checked', 'BIRDS max. (%)', 'OreSat max. (%)'],
                   overview, [.14, .46, .20, .20]))

    t.append(r'''\subsection{FR-12: mass, volume and allocation margins}
Published checks use six BIRDS cells at 27 g each and the historical OreSat battery and solar modules \citep{birds2021batteryverification,oresat2016csli}.
The complete mass estimates add assumed EPS contributions.
The values below list battery, solar array, conversion and distribution contributions, in that order.
The OreSat mass case uses 2016 hardware, separate from its later electrical baseline.
''')
    mass_inputs = []
    for mission in missions:
        c = inputs['executed_configurations'][mission + ':01-mass-boundaries']
        mass_inputs.append([mission.replace('BIRDS-4', 'BIRDS'), scale(c['masses_kg'], 1000),
                            scale(c['volumes_m3'], 1e6),
                            [c['mass_allocation_initial_kg'] * 1000, c['volume_allocation_m3'] * 1e6]])
    t.append(table(['Case', 'Component masses (g)', Tex(r'Occupied volumes (cm$^3$)'),
                    Tex(r'Mass (g), volume (cm$^3$) allocations')],
                   mass_inputs, [.12, .30, .28, .30]))
    t.append(r'''BIRDS battery mass includes 78 g of assumed packaging and EPS overhead above the 162 g cell sum.
OreSat solar volume uses eight assumed $100\times100\times3$ mm complete module envelopes.
References sum the contributions and subtract them from their allocations.
''')
    rows = [display('BIRDS-4', '01-mass-boundaries', 'published_cell_only_mass', 'Published cells (g)', 1000),
            display('OreSat', '01-mass-boundaries', 'published_battery_module_mass', 'Published battery modules (g)', 1000)]
    rows += pair('01-mass-boundaries', 'mass', 'EPS mass (g)', 1000)
    rows += pair('01-mass-boundaries', 'volume', r'EPS volume (cm$^3$)', 1e6)
    rows += pair('01-mass-boundaries', 'mass_margin', 'Mass margin (g)', 1000)
    t.append(comparisons(rows))

    t.append(r'''\subsection{FR-14: energy budgets and BOL/EOL sizing}
MOP-14a covers power and orbital energy accounting. MOP-14b covers sizing and generation.
References use $P=VI$, duty-weighted phase power, $E=\overline P T$ and
$P_{req}=(E_s/0.85+E_e/0.75)/T_s$.
The assumed battery law is $N=2000\,DoD^{-1}$ over $0.1\le DoD\le0.8$.
One cycle per orbit is assumed, so cycle demand is mission duration divided by orbital period.
This demand determines DoD, and required BOL energy is $E_e(1+0.2)/DoD$.
Retained battery energy and Ah use separate assumed 0.8 factors.
Source generation uses the selected age-specific curve once.
Cell efficiency is $V_{mp}I_{mp}/(G_{ref}A_{cell})$.
Required active area divides source-power demand by irradiance, efficiency, the two source factors and mean sunlight projection.
Additional orbital checks include eccentric nadir cases and an eclipse-free case.
The eccentricities are 0.02 for BIRDS and 0.04 for OreSat, with $\beta=25^\circ$ and Sun projection angle $47^\circ$.
The eclipse-free case uses $\beta=90^\circ$.
''')
    rows = pair('02-states-modes-circular', 'minimum_panel_power', 'Required source power (W)')
    for q, label in [('BOL_case_available_power', 'BOL mean source power (W)'),
                     ('available_power', 'EOL mean source power (W)'),
                     ('required_count', 'Power-based minimum cell count'),
                     ('required_battery_energy', 'Required battery energy (J)'),
                     ('required_area', r'Required active area (m$^2$)')]:
        rows += pair('05-baseline-sizing', q, label)
    rows += [display('BIRDS-4', '02-states-modes-circular', 'external_free_rotation_BCR', 'Published regulator energy (mWh)'),
             display('OreSat', '05-baseline-sizing', 'published_BOL_module_power', 'Published BOL module power (W)')]
    t.append(comparisons(rows))
    t.append(r'''The BIRDS published regulator row evaluates $(2173-240)\times0.8$ mWh using supplied generation and stated losses \citep[p.~8]{shrestha2022birds4powerbudget}.
The OreSat published BOL module comparison uses its stated cell ratings \citep{oresat2025solardesign}.
Doubling the reference grid changes eclipse duration by at most 0.00205\% and leaves integer sizing bounds unchanged.
''')

    t.append(r'''\subsection{FR-15: solar technology and battery chemistry}
The silicon alternative is a 4S10P IXOLAR section with 4.46 V and 5.4 mA per cell at the selected EOL MPP \citep{shrestha2026solarreliability}.
Its EOL current retention of 0.9 is assumed.
The BIRDS battery alternative is 1S2P Tenergy Li-ion, using 3.6 V and 2.6 Ah per cell.
The OreSat alternative is 4S1P LiFePO4 per independent pack, using 3.3 V and 1.1 Ah per cell \citep{cots-mission_tenergy_30005_0_ds,oresatbatteryresearch}.
References recompute $P_{array}=n_sn_pV_{mp}I_{mp}$ and $E_{pack}=n_sn_pV_{nom}C_{cell}$.
Charger comparisons retain the selected chemistry, cell count, endpoint and termination method.
''')
    rows = pair('06-silicon-technology', 'array_mpp', 'Silicon array MPP power (W)')
    rows += pair('07-battery-chemistry', 'pack_wh', 'Alternative pack energy (Wh)')
    t.append(comparisons(rows))

    t.append(r'''\subsection{FR-16: series and parallel arrangements}
The array variation uses 4S1P in both cases.
BIRDS storage changes to 2S1P, while each OreSat branch changes to 3S1P.
References scale series voltage and energy, and parallel charge capacity and current ratings.
The four-cell array uses a 2 by 2 grid on an assumed $100\times170$ mm plate.
Package envelopes are $40.15\times80.15$ mm for BIRDS and $39.7\times69.1$ mm for OreSat \citep{cots-mission_azur_space_3g30a_review_legacy_ds,cots-solar_src_spectro_xtesf}.
The grid adds 2 mm gaps, 3 mm edge clearances and 0.1 mm per-dimension allowances.
The OreSat package envelope is assumed from the nominal cell outline.
''')
    rows = pair('08-integer-configurations', 'array_voltage', 'Four-cell MPP voltage (V)')
    rows += pair('08-integer-configurations', 'pack_wh', 'Changed primary-pack energy (Wh)')
    rows += pair('08-integer-configurations', 'pack_ah', 'Changed primary-pack capacity (Ah)')
    rows += pair('08-integer-configurations', 'deployed_footprint', r'Deployed footprint (cm$^2$)', 1e4)
    rows.append(display('OreSat', '08-integer-configurations', 'published_card_energy', 'Published baseline card energy (Wh)'))
    t.append(comparisons(rows))
    t.append(r'''The last row concerns the baseline card's two independent 2S1P packs \citep[p.~6]{greenberg2021oresat}.
Stored energies add. Current limits remain per branch without an assumed sharing law.
''')

    t.append(r'''\subsection{FR-17: bus rails and converter compatibility}
The selected rails are 3.3 V at 0.5 A and 5 V at 0.4 A.
Terminal battery current is $I_{bat}=P_{rail}/(0.9V_{bat})$ at nominal pack voltage.
BIRDS uses TPS63020-Q1 for 3.3 V and LTC3119 for 5 V, with assumed complete-circuit efficiency 0.9 and 1 A output limit.
Their entered input intervals are 1.8--5.5 V and 2.5--18 V.
OreSat uses TPS62111/12 with a 3.1--17 V input interval, 1.5 A output limit and assumed efficiency 0.9 \citep{oresat2021opddesign}.
Voltage tolerance is an assumed 0.05 V.
Input containment, output tolerance and current-limit comparisons matched their references.
''')
    rows = pair('09-converter-rails', 'terminal_battery_current_3.3', 'Battery current, 3.3 V rail (A)')
    rows += pair('09-converter-rails', 'terminal_battery_current_5.0', 'Battery current, 5 V rail (A)')
    t.append(comparisons(rows))

    t.append(r'''\subsection{FR-18: PV characteristics and sampled MPP}
The verification curves have short-circuit, MPP and open-circuit anchors from the baseline input table.
The reference calculates each $VI$ product and selects the largest sampled value.
Published checks use the BIRDS 5.123 V, 50 mA point \citep[Figs.~13--14]{shrestha2021birdssafety} and OreSat's 4.435 V, 0.37304 A row \citep{oresatsolarsweep}.
''')
    rows = pair('10-characteristics', 'mpp_power', 'Sampled cell MPP power (W)')
    rows += [display('BIRDS-4', '10-characteristics', 'Maya_label_50mA', 'Published 50 mA power label (W)'),
             display('OreSat', '10-characteristics', 'published_sweep_max_VI', 'Published row 197 product (W)')]
    t.append(comparisons(rows))
    t.append(r'''The BIRDS 1.575 W measured peak remains unreconstructed.
The OreSat sweep lacks short/open-circuit endpoints and contains repeated voltages, so it supports power-product checks rather than a complete measured-curve benchmark.
''')

    t.append(r'''\subsection{FR-19: matched DET and ideal MPPT paths}
The BIRDS pair uses the baseline 2S1P section and 3.6 V battery bus.
The OreSat pair uses an explicitly unflown 4S1P section and the same 7.2 V battery bus.
Four series cells provide a DET operating point at that bus voltage.
Within each pair, both paths share the curve, illumination, source losses and 0.5 W bus demand.
DET imposes $V_{op}=V_{bat}+0.2$ V and obtains array current by linear interpolation.
Its bus power is mean source power times $V_{bat}/V_{op}$.
Ideal MPPT selects the sampled MPP and applies assumed conversion efficiency 0.9.
The separate OreSat published net-power calculation subtracts 0.387 W of listed losses from its stated 2.10 W module power \citep{oresat2025solardesign}.
''')
    rows = []
    for mission in missions:
        for method, scenario in [('DET', '11-baseline-DET'), ('MPPT', '12-baseline-ideal-MPPT')]:
            if mission == 'OreSat':
                scenario = '14-unflown-4S-pair'
            rows.append(display(mission, scenario, method + '_mean_bus_power', method + ' mean bus power (W)'))
    rows.append(display('OreSat', '12-baseline-ideal-MPPT', 'published_separate_net_power', 'Separate published net power (W)'))
    t.append(comparisons(rows))

    t.append(r'''\subsection{FR-20: normal extrema and protection comparisons}
The BIRDS voltage samples are 3.9, 4.0 and 4.2 V at pack terminals, with assumed UV/OV thresholds of 3.5/4.8 V.
OreSat uses 3.0, 3.6 and 4.0 V cell samples against nominal 2.50/4.10 V thresholds \citep{oresat2025batterydesign}.
Separate current bounds use $I_{min}=P_{min}/V_{max}$ and $I_{max}=P_{max}/V_{min}$.
BIRDS uses 1--7.5 W at a 4.75--5.25 V regulated rail with a 2 A threshold \citep[Sec.~6.3]{kyutech2021birdsicd}.
OreSat uses 6--30 W at the 6--8.4 V spacecraft battery bus with an assumed 6 A threshold.
These are separate from the OreSat heater branch's 0.375 A detector.
''')
    rows = pair('16-normal-extrema', 'Vmin', 'Normal voltage extrema (V)')
    rows += pair('16-normal-extrema', 'bound_current_extrema', 'Power/voltage current bounds (A)')
    rows.append(display('OreSat', '16-normal-extrema', 'published_30W_current_7.2', 'Published 30 W / 7.2 V current (A)'))
    t.append(comparisons(rows))
    t.append(r'''Normal-case no-trip decisions and the strict comparisons at each declared threshold matched their references.
The separate assumed OreSat charger endpoint remains 4.20 V per cell against the nominal 4.10 V trip threshold.
''')

    text = '\n\n'.join(t).rstrip() + '\n'
    assert not re.search(r'/Users/|/tmp/|\.json\b|\.csv\b|\.py\b|SHA-?256|includegraphics', text, re.I)
    (directory / 'case-study-evidence.tex').write_text(text)
