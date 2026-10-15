#!/usr/bin/env python3
"""Render the proposed functional requirement activity and information flows.

python3 final_report/fig/fr-activity-flows.py --jobdir /absolute/external/check-dir

All panels are included in fr-activity-flows.pdf. Each panel also has an SVG,
PDF and PNG. The report appendix, rather than this script, specifies meaning.
No framework execution or engineering validation is claimed by these checks.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from diagram_style import (Figure, INK, LIGHT, LINE_PATTERNS, SerifMetrics,
                           orthogonal_points, render_figure, require, run, sha)

FIG = Path(__file__).resolve().parent
ROOT = FIG.parent.parent
BASE = FIG / 'fr-activity-flows'
REQUIREMENTS = FIG.parent / 'requirements.tex'
APPENDIX = FIG.parent / 'fr-activity-flows.tex'
W, H = 1000, 1235
NODE_FONT, FLOW_FONT, ID_FONT = 24, 22, 22
# Identified activities use two short verb/object lines plus a trace header.
# External participants alone use gray. There is no architecture boundary here.
COLUMNS = {'L': (70, 410), 'R': (670, 300)}


def n(key, row, label, fr='', side='L', owner='Framework', kind='activity'):
    return dict(id=key, row=row, labels=label.split('|'), fr=fr.split(),
                side=side, owner=owner, kind=kind)


def e(source, target, label, kind='information', **kw):
    return dict(source=source, target=target, labels=label.split('|'), kind=kind, **kw)


def p(identifier, title, nodes, edges):
    return dict(id=identifier, title=title, nodes=nodes, edges=edges)


PANELS = [
    p('01-admission', '01  Controlled transfer admission', [
        n('1', 0, 'Submit engineering|information', owner='Engineer / source', kind='external'),
        n('2', 1, 'Check transferred|meanings', 'FR-08'),
        n('3', 2, 'Register compatible|information', 'FR-08'),
        n('4', 3, 'Retain controlled|records', 'FR-08', kind='record'),
        n('5', 1, 'Retain rejected|raw submission', 'FR-08', side='R'),
        n('6', 2, 'Return rejection|findings', 'FR-08', side='R'),
    ], [
        e('1', '2', 'Raw submission, identity and provenance;|declared interface specification'),
        e('2', '3', '[compatible] Revisions, structure, quantities,|units, polarity and time / mode meanings'),
        e('3', '4', 'Admitted records with identifiers,|revisions, producer and provenance'),
        e('2', '5', '[incompatible]|raw + findings', 'findings'),
        e('5', '6', 'Unchanged controlled content;|rejected values and incompatibilities', 'findings', pos=[795, 453]),
    ]),
    p('02-mission-allocations', '02  Mission context and proposed allocations', [
        n('1', 0, 'Supply mission|and spacecraft inputs', owner='Engineer', kind='external'),
        n('2', 1, 'Retain mission|and ConOps', 'FR-25'),
        n('3', 2, 'Derive proposed|EPS allocations', 'FR-17'),
        n('4', 2, 'Disposition|allocations', side='R', owner='Engineer', kind='external'),
        n('5', 3, 'Retain allocation|basis and disposition', 'FR-17'),
        n('6', 4, 'Link requirements|and analysis inputs', 'FR-25 FR-17'),
    ], [
        e('1', '2', 'Expectations, constraints, nominal / degraded|scenarios, spacecraft requirements and sources'),
        e('2', '3', 'Identified mission / scenarios and configuration;|sourced quantities and declared derivation method'),
        e('3', '4', 'Proposed|allocations'),
        e('4', '5', 'Engineer disposition of proposed allocations;|parent links, units, assumptions and uncertainty'),
        e('5', '6', 'Revision-linked mission conditions,|EPS / component proposals and dispositions'),
    ]),
    p('03-requirements', '03  Requirement records, checks and trace queries', [
        n('1', 0, 'Retain requirement|draft and metadata', 'FR-01'),
        n('2', 1, 'Check requirement|draft', 'FR-02'),
        n('3', 2, 'Retrieve traces|and coverage', 'FR-04'),
        n('4', 3, 'Explain corrections|and questions', 'FR-02'),
        n('5', 3, 'Disposition|suggestion', side='R', owner='Engineer', kind='external'),
        n('6', 4, 'Retain authorized|disposition', 'FR-29'),
        n('7', 5, 'Retain requirement|resolution status', 'FR-01'),
    ], [
        e('1', '2', 'Each draft edit / request, current rules,|source / parent revisions and coverage references'),
        e('2', '3', 'Quality errors, probable duplicates, gaps / conflicts;|trace query and declared reference set'),
        e('3', '4', 'Forward / reverse links, missing / ambiguous|endpoints and reference-set coverage'),
        e('4', '5', 'Explained|suggestion'),
        e('5', '6', 'Authorized accept / modify / reject / defer decision;|rationale and exact suggestion / context revisions', 'authorization'),
        e('6', '7', 'Disposition, revised draft where applicable,|field resolution reasons and verification context'),
    ]),
    p('04-guidance', '04  Method recommendations and next activities', [
        n('1', 0, 'Identify current|engineering context', 'FR-03 FR-39'),
        n('2', 1, 'Assess method|and model eligibility', 'FR-03'),
        n('3', 2, 'Recommend methods|and alternatives', 'FR-03'),
        n('4', 3, 'Propose next|engineering activities', 'FR-39'),
        n('5', 3, 'Disposition|suggestion', side='R', owner='Engineer', kind='external'),
        n('6', 4, 'Retain authorized|disposition', 'FR-29'),
    ], [
        e('1', '2', 'Edit / request, phase, question, requirements,|available inputs, validity, resources and scope'),
        e('2', '3', 'Applicable choices, conditions, cited sources,|rationale, alternatives and rejection records'),
        e('3', '4', 'Current method guidance, maturity, dependencies,|open findings and designated review criteria'),
        e('4', '5', 'Proposals +|prerequisites'),
        e('5', '6', 'Authorized accept / modify / reject / defer decision;|rationale and exact suggestion / context revisions', 'authorization'),
    ]),
    p('05-assistance-response', '05  Assistance acknowledgement and response', [
        n('1', 0, 'Receive assistance|trigger', 'FR-48'),
        n('2', 1, 'Acknowledge current|context trigger', 'FR-41 FR-48'),
        n('3', 2, 'Assess guidance|and service status', 'FR-47'),
        n('4', 3, 'Return current|response', 'FR-47 FR-48'),
        n('5', 4, 'Record exchange|completion', 'FR-48'),
        n('6', 1, 'Receive|acknowledgement', side='R', owner='Engineer', kind='external'),
        n('7', 3, 'Receive guidance|or explicit status', side='R', owner='Engineer', kind='external'),
    ], [
        e('1', '2', 'Trigger time, exact context revision and|engineer-approved acknowledgement limit'),
        e('2', '3', 'Acknowledgement time, exact context and|engineer-approved interactive response limit'),
        e('2', '6', 'Within agreed|ack limit'),
        e('3', '4', 'Finding / recommendation when available;|otherwise explicit pending / unavailable status'),
        e('4', '7', 'Within agreed|response limit'),
        e('4', '5', 'First-response time and context;|completion event and completion time'),
    ]),
    p('06-assistance-currency', '06  Assistance currency and reassessment', [
        n('1', 0, 'Identify changed|assistance context', 'FR-30 FR-46'),
        n('2', 1, 'Mark affected|assistance stale', 'FR-30'),
        n('3', 2, 'Initiate context|reassessment', 'FR-46'),
        n('4', 4, 'Check suggestion|before application', 'FR-45'),
        n('5', 5, 'Return current|guidance for decision', 'FR-45'),
        n('6', 4, 'Block stale|suggestion application', 'FR-45', side='R'),
        n('7', 3, 'Request suggestion|application', side='R', owner='Engineer', kind='external'),
    ], [
        e('1', '2', 'Changed requirement, mission, design, source,|criterion or scope revisions; affected assistance'),
        e('2', '3', 'Stale status and new context revision;|affected assistance to reassess'),
        e('3', '4', 'New-context reassessment / suggestion status;|no assumption of completed fresh guidance'),
        e('7', '4', 'Application request; exact|suggestion / context revisions', path='M670 745 H585 V890 H400 V910', pos=[610, 824], anchor='start', width=370),
        e('4', '5', '[current] Checked suggestion and context;|engineer disposition remains required'),
        e('4', '6', '[stale]|block finding', 'findings'),
    ]),
    p('07-design-resources', '07  EPS configuration and physical estimates', [
        n('1', 0, 'Configure EPS|design representation', 'FR-15'),
        n('2', 1, 'Identify sourced|aggregate / component data', 'FR-13'),
        n('3', 2, 'Calculate mass, volume|and stack height', 'FR-13'),
        n('4', 3, 'Assess allocation|margins', 'FR-13'),
        n('5', 4, 'Retain estimates|and unknown values', 'FR-13'),
        n('6', 3, 'Consider design|findings', side='R', owner='Engineer', kind='external'),
    ], [
        e('1', '2', 'Parameters, component variants, extensions,|interfaces and requirement allocations'),
        e('2', '3', 'Mass, dimensions, quantities, units and sources;|aggregation assumptions and uncertainty'),
        e('3', '4', 'Revision-linked mass, occupied volume and|stack-height estimates; applicable allocations'),
        e('4', '5', 'Margins, uncertainty, assumptions, sources|and explicit unknown quantities'),
        e('4', '6', 'Allocation|findings', 'findings'),
    ]),
    p('08-power-sizing', '08  Power and energy budgets and discrete sizing', [
        n('1', 0, 'Calculate mode|power and losses', 'FR-20'),
        n('2', 1, 'Calculate sunlight|and eclipse energy', 'FR-20'),
        n('3', 2, 'Size array|and battery', 'FR-20'),
        n('4', 3, 'Resolve discrete|cell arrangements', 'FR-20'),
        n('5', 4, 'Assess allocations|and operating limits', 'FR-20'),
        n('6', 5, 'Retain sizing|and margin findings', 'FR-20'),
    ], [
        e('1', '2', 'Nominal / peak mode power, conversion / distribution|losses, efficiencies, duty cycles and schedules'),
        e('2', '3', 'Sunlight / eclipse budgets, illumination, temperature,|degradation, cycle life, discharge limits and margins'),
        e('3', '4', 'Beginning / end of life array area and|battery capacity, required voltages and cell data'),
        e('4', '5', 'Integer cell counts, array / battery|series and parallel arrangements'),
        e('5', '6', 'Allocation margins and operating-limit findings;|sizing basis and configured EPS revision'),
    ]),
    p('09-trades', '09  Common-basis EPS trades and sensitivity', [
        n('1', 0, 'Define common|trade basis', 'FR-14'),
        n('2', 1, 'Check concept|feasibility', 'FR-14'),
        n('3', 2, 'Assess parameter|sensitivity', 'FR-14'),
        n('4', 3, 'Rank feasible|alternatives', 'FR-14'),
        n('5', 4, 'Retain comparison|and preference basis', 'FR-14'),
        n('6', 1, 'Retain infeasible|alternative findings', 'FR-14', side='R'),
        n('7', 3, 'Consider trade|recommendation', side='R', owner='Engineer', kind='external'),
    ], [
        e('1', '2', 'EPS concepts, common mission / requirement basis,|sweep parameters and engineer-approved criteria'),
        e('2', '3', '[feasible] Raw measures, margins and uncertainty;|applicable cell, pack, bus and regulator choices'),
        e('2', '6', '[infeasible]|risks / limits', 'findings'),
        e('3', '4', 'Sensitivity measures, margins, uncertainty, risks|and engineer-approved preference criteria'),
        e('4', '7', 'Preference|ranking'),
        e('4', '5', 'Ranked feasible alternatives with raw results,|uncertainty, risks and preference rationale'),
    ]),
    p('10-coupling', '10  Model exchange and identified Omniverse coupling', [
        n('1', 0, 'Exchange identified|discipline models', 'FR-18'),
        n('2', 1, 'Map incoming|scenario conditions', 'FR-43'),
        n('3', 2, 'Admit histories|before numerical use', 'FR-31 FR-32'),
        n('4', 3, 'Execute framework|EPS analysis', 'FR-16'),
        n('5', 4, 'Map outgoing|EPS responses', 'FR-44'),
        n('6', 1, 'Simulate spacecraft|and subsystems', side='R', owner='NVIDIA Omniverse', kind='external'),
        n('7', 4, 'Receive same-scenario|EPS responses', side='R', owner='NVIDIA Omniverse', kind='external'),
        n('8', 5, 'Retain exchange|status and limits', 'FR-18 FR-43 FR-44'),
    ], [
        e('1', '2', 'EPS / external model revisions; declared electrical,|thermal, applicable EMC and geometry profiles'),
        e('6', '2', 'Conditions +|constraints'),
        e('2', '3', 'Scenario conditions, constraints and feasibility;|mission / scenario, configuration and profile revisions'),
        e('3', '4', 'Checked histories, directed channel mappings,|units, model / tool revisions and supported effects'),
        e('4', '5', 'Computed EPS states, dissipation, margins|and feasibility findings; same scenario / configuration'),
        e('5', '7', 'Mapped EPS|responses'),
        e('5', '8', 'Incoming / outgoing mapping and execution status;|unsupported effects and lossy transfers'),
    ]),
    p('11-history-quality', '11  History timing, quality and numerical admission', [
        n('1', 0, 'Preserve supplied|and simulated histories', 'FR-32'),
        n('2', 1, 'Check time bases|and synchronization', 'FR-31'),
        n('3', 2, 'Check channel|and sample validity', 'FR-32'),
        n('4', 3, 'Apply processing|masks', 'FR-32'),
        n('5', 4, 'Supply checked|numerical inputs', 'FR-31 FR-32'),
        n('6', 1, 'Report timing|gaps and limits', 'FR-31', side='R'),
        n('7', 2, 'Retain invalid|or missing samples', 'FR-32', side='R'),
    ], [
        e('1', '2', 'Raw exchanged / simulated / reference histories;|sample / receipt times and scenario time references'),
        e('2', '3', 'Timing, sampling, synchronization and known|calculation / interface delays; declared timing rules'),
        e('2', '6', 'Missing timing|or limit breach', 'findings'),
        e('3', '4', 'Identity, units, timing, completeness and validity;|raw values, invalid samples and missing intervals'),
        e('3', '7', 'Invalid / missing|status + masks', 'findings'),
        e('4', '5', 'Admitted samples and processing masks;|missing / inactive readings remain distinct from zero'),
    ]),
    p('12-eps-electrical', '12  EPS electrical and mission energy analysis', [
        n('1', 0, 'Retain declared|run configuration', 'FR-23'),
        n('2', 1, 'Calculate photovoltaic|characteristics', 'FR-16'),
        n('3', 2, 'Execute converter|and regulator models', 'FR-16'),
        n('4', 3, 'Execute battery|and energy models', 'FR-16'),
        n('5', 4, 'Assess electrical|and energy limits', 'FR-16'),
        n('6', 5, 'Retain runtime|and numerical findings', 'FR-23'),
    ], [
        e('1', '2', 'Checked loads, schedules, modes, orbit / attitude,|illumination, eclipse, thermal inputs and model revisions'),
        e('2', '3', 'Photovoltaic I-V / P-V characteristics,|operating points and selected model parameters'),
        e('3', '4', 'Converter / regulator responses and conversion /|distribution losses under time-dependent loads'),
        e('4', '5', 'Battery voltage / state of charge, mission energy|histories, shortages and survival autonomy'),
        e('5', '6', 'Electrical / battery limit margins and status;|numerical / resource limits and measured runtime'),
    ]),
    p('13-eps-health-stress', '13  EPS electrothermal, health and stress analysis', [
        n('1', 0, 'Retain declared|run configuration', 'FR-23'),
        n('2', 1, 'Execute electrothermal|models', 'FR-16'),
        n('3', 2, 'Predict battery|state of health', 'FR-16'),
        n('4', 3, 'Assess conducted|emissions', 'FR-16'),
        n('5', 4, 'Assess protection|component stress', 'FR-16'),
        n('6', 5, 'Retain histories|and limit findings', 'FR-16 FR-23'),
    ], [
        e('1', '2', 'Checked scenario conditions, EPS models, parameters,|electrical responses and thermal / rating limits'),
        e('2', '3', 'Voltage / temperature histories and dissipation;|battery use profile, health model and uncertainty basis'),
        e('3', '4', 'SOH predictions / uncertainty indicators and|scenario-linked electrical / thermal analysis basis'),
        e('4', '5', 'Conducted-emission histories / spectra and margins;|circuit responses, component ratings and limits'),
        e('5', '6', 'Thermal, emission and component-stress margins;|supported effects, execution / numerical / resource limits'),
    ]),
    p('14-calibration-credibility', '14  Calibration proposals and independent credibility', [
        n('1', 0, 'Estimate model|parameters', 'FR-22'),
        n('2', 1, 'Retain calibration|proposal', 'FR-22'),
        n('3', 1, 'Authorize parameter|change decision', side='R', owner='Engineer', kind='external'),
        n('4', 2, 'Resolve controlled|model revision', 'FR-22'),
        n('5', 3, 'Assess conclusion|credibility', 'FR-21'),
        n('6', 4, 'Retain credibility|findings and gaps', 'FR-21'),
        n('7', 3, 'Retain independent|assessment gaps', 'FR-21', side='R'),
        n('8', 2, 'Supply conclusion|and assessment basis', side='R', owner='Engineer / source', kind='external'),
    ], [
        e('1', '2', 'Quality-checked solar / battery / dynamic EPS-load|data, fitting criteria, residuals and parameter estimates'),
        e('2', '3', 'Prior / revised|values + basis'),
        e('3', '4', 'Authorized change disposition and calibration proposal;|residuals, uncertainty and affected analyses', 'authorization'),
        e('4', '5', '[if applicable] Calibration|evidence and controlled|parameter revision', pos=[250, 614], anchor='end', width=230),
        e('8', '5', 'Current model / conclusion, intended use;|independent assessment evidence or gaps;|fidelity, mechanisms and declared error rules', path='M820 580 V670 H400 V700', pos=[795, 614], anchor='end', width=480),
        e('5', '6', 'Calibration evidence where applicable, separate independent|evidence / gaps, numerical / validity / prediction-error checks;|uncertainty interpretation and credibility findings'),
        e('5', '7', 'Missing evidence|or domain limits', 'findings'),
    ]),
    p('15-ram', '15  RAM applicability, execution and recovery assessment', [
        n('1', 0, 'Identify applicable|RAM analyses', 'FR-26'),
        n('2', 1, 'Generate RAM|representations', 'FR-27'),
        n('3', 2, 'Check failure|and recovery data', 'FR-27'),
        n('4', 3, 'Execute applicable|RAM analyses', 'FR-27'),
        n('5', 4, 'Assess service|and restoration', 'FR-27'),
        n('6', 5, 'Retain RAM findings|and uncertainty', 'FR-27'),
        n('7', 2, 'Leave affected results|unavailable', 'FR-27', side='R'),
    ], [
        e('1', '2', 'Applicable methods, chosen measures, coverage / exclusions,|failure dependencies and probability / recovery assumptions'),
        e('2', '3', 'Identified functions / components, failure dependencies,|declared representation rules and sourced parameters'),
        e('3', '4', '[sufficient data] Declared qualitative / quantitative|scope, probability / rate and recovery assumptions'),
        e('3', '7', '[missing data]|affected results', 'findings'),
        e('4', '5', 'Failure effects / criticality, minimal combinations,|conditional probabilities, mission reliability and redundancy'),
        e('5', '6', 'Time-dependent service availability; detection, isolation,|reconfiguration / restoration outcomes against criteria'),
    ]),
    p('16-interfaces-control', '16  Interface definitions and modeled control behavior', [
        n('1', 0, 'Retain modeled|EPS interfaces', 'FR-33'),
        n('2', 1, 'Retain command|and ground definitions', 'FR-33'),
        n('3', 2, 'Specify command|and mode behavior', 'FR-35'),
        n('4', 3, 'Check protection|and recovery behavior', 'FR-35'),
        n('5', 4, 'Retain checked|behavior specification', 'FR-35'),
        n('6', 3, 'Resolve behavior|discrepancies', side='R', owner='Engineer', kind='external'),
    ], [
        e('1', '2', 'Revision-linked endpoints, ownership, directions,|identifiers, types, units, ranges and polarity'),
        e('2', '3', 'Commands, telemetry, events and parameters;|encodings and time / mode meanings'),
        e('3', '4', 'Preconditions, order, effects, rejection / failure behavior|and mode transitions; control / interface requirements'),
        e('4', '5', 'Modeled protection / recovery responsibilities,|criterion checks and unresolved discrepancies'),
        e('4', '6', 'Behavior|findings', 'findings'),
    ]),
    p('17-fprime-build', '17  F Prime mappings and authorized host builds', [
        n('1', 0, 'Map EPS interfaces|to F Prime profile', 'FR-34'),
        n('2', 1, 'Check mapping|and version limits', 'FR-34'),
        n('3', 2, 'Check current|design release authority', 'FR-36'),
        n('4', 3, 'Coordinate declared|coding and host build', 'FR-36'),
        n('5', 3, 'Code / reuse behavior|and build on host', side='R', owner='F Prime toolchain', kind='external'),
        n('6', 4, 'Retain source / build|products and failures', 'FR-36'),
        n('7', 2, 'Block unreleased|or stale coding', 'FR-36', side='R'),
    ], [
        e('1', '2', 'EPS component / port / topology and ground definitions;|required profile, tool and representation versions'),
        e('2', '3', 'Checked mappings, compatibility findings, unsupported|behavior and lossy translations; detailed design release'),
        e('3', '4', '[current and authorized] Exact design / interface release,|declared coding scope and checked F Prime mappings', 'authorization'),
        e('3', '7', '[no current|authorization]', 'findings'),
        e('4', '5', 'Coding / build|request'),
        e('5', '6', 'Source / build revisions, versions, dependencies,|host configuration, raw logs and failures'),
    ]),
    p('18-mil', '18  MIL execution and fault diagnosis assessment', [
        n('1', 0, 'Fix MIL scenarios|and assessment criteria', 'FR-19'),
        n('2', 1, 'Execute nominal|and transition scenarios', 'FR-19'),
        n('3', 2, 'Execute fault|and recovery scenarios', 'FR-19'),
        n('4', 3, 'Assess detection|and fault diagnosis', 'FR-19'),
        n('5', 4, 'Compare expected|and actual responses', 'FR-19'),
        n('6', 5, 'Retain MIL evidence|and failures', 'FR-19'),
    ], [
        e('1', '2', 'Identified plant / controller models, fixed stimuli,|expected responses, declared criteria and checked histories'),
        e('2', '3', 'Nominal / step responses, DET / MPPT / end-of-charge|transitions and command / mode changes'),
        e('3', '4', 'Overcurrent / undervoltage / overvoltage, interruption,|hysteresis, load shedding and recovery responses'),
        e('4', '5', 'Simulated / supplied histories, fault hypotheses,|diagnostic alternatives and assessment evidence'),
        e('5', '6', 'Stimuli, expected / actual responses, criterion findings,|alternative hypotheses, execution limits and failures'),
    ]),
    p('19-sil', '19  Framework plant, external host and SIL assessment', [
        n('1', 0, 'Fix released SIL|and MIL comparison basis', 'FR-24'),
        n('2', 1, 'Execute framework|EPS plant', 'FR-24'),
        n('3', 1, 'Supply spacecraft|simulation conditions', side='R', owner='NVIDIA Omniverse', kind='external'),
        n('4', 2, 'Coordinate released|host software execution', 'FR-24'),
        n('5', 2, 'Execute released|host software', side='R', owner='F Prime host', kind='external'),
        n('6', 3, 'Assess SIL|requirement / ConOps results', 'FR-24'),
        n('7', 4, 'Compare corresponding|MIL and SIL outputs', 'FR-24'),
        n('8', 5, 'Retain outcomes,|differences and limits', 'FR-24'),
    ], [
        e('1', '2', 'Current released design / host build, fixed scenarios,|comparison rules, matching MIL and run / coupling settings'),
        e('3', '2', 'Same-scenario|conditions'),
        e('2', '4', 'Simulated EPS plant states; same mission / scenario,|configuration and coupling-profile revisions'),
        e('4', '5', 'Host request|+ stimuli'),
        e('5', '2', 'Host actuation and command effects;|control outputs to simulated EPS plant', path='M970 535 H985 V250 H400 V280', pos=[960, 453], anchor='end', width=520),
        e('2', '6', 'Resulting plant histories and states for assessment', path='M70 325 H35 V745 H70', pos=[60, 690], width=600),
        e('5', '6', 'Raw host responses, execution status, logs and failures;|declared requirement / ConOps criteria', path='M820 580 V675 H585 V745 H480', pos=[795, 614], anchor='end', width=720),
        e('6', '7', 'Framework-assessed SIL responses, corresponding|MIL outputs and rules fixed before comparison'),
        e('7', '8', 'Criterion outcomes, MIL / SIL differences,|partial / failed execution status and applicability limits'),
    ]),
    p('20-plans-gaps', '20  Verification / validation plans and evidence gaps', [
        n('1', 0, 'Retain phase-product|assessment plans', 'FR-28'),
        n('2', 1, 'Link observations|and execution status', 'FR-28'),
        n('3', 2, 'Assess evidence|gaps and criticality', 'FR-11'),
        n('4', 3, 'Report gaps|and dispositions', 'FR-11'),
        n('5', 4, 'Qualify affected|conformity conclusions', 'FR-11'),
        n('6', 3, 'Prevent unqualified|current claims', 'FR-11', side='R'),
    ], [
        e('1', '2', 'Distinct requirement and expectation / ConOps references;|subject configuration, method, conditions, inputs and criteria'),
        e('2', '3', 'Expected response, observations, applicability limits|and planned / executed status; linked evidence'),
        e('3', '4', 'Missing, rejected, stale, failed, out-of-domain|or unresolved evidence; affected conclusions and owners'),
        e('4', '6', '[critical gap]|claim blocked', 'findings'),
        e('4', '5', 'Requirement / expectation links, criticality, owner|and disposition; retained limits on current conclusions'),
    ]),
    p('21-results-replay', '21  Result provenance, reconstruction and replay', [
        n('1', 0, 'Associate result|with exact run basis', 'FR-09'),
        n('2', 1, 'Retain raw outputs,|logs and run status', 'FR-09'),
        n('3', 2, 'Provide replay inputs|and instructions', 'FR-10'),
        n('4', 3, 'Reconstruct designated|analysis / MIL / SIL run', 'FR-10'),
        n('5', 4, 'Compare replay|raw outputs', 'FR-10'),
        n('6', 5, 'Retain comparison|and dependency findings', 'FR-10'),
        n('7', 3, 'Retain missing|dependencies', 'FR-10', side='R'),
    ], [
        e('1', '2', 'Requirement / expectation, method, scenario, exact input /|design / model / software revisions, parameters and producer'),
        e('2', '3', 'Execution environment, raw outputs, logs and status|including failed / cancelled / partial runs; replay request'),
        e('3', '4', 'Controlled inputs, dependencies and instructions;|result-specific rules / tolerances fixed before replay'),
        e('4', '7', '[missing]|dependencies', 'findings'),
        e('4', '5', '[reconstructed] Returned raw replay outputs|and preserved original raw outputs'),
        e('5', '6', 'Result-specific comparison, differences / failures|and missing-dependency findings'),
    ]),
    p('22-change-baselines', '22  Reciprocal impacts and authorized baselines', [
        n('1', 0, 'Retrieve exact|predecessor baseline', 'FR-07'),
        n('2', 1, 'Identify reciprocal|change impacts', 'FR-05'),
        n('3', 1, 'Decide engineering|change request', side='R', owner='Engineer', kind='external'),
        n('4', 2, 'Check change|decision authority', 'FR-06'),
        n('5', 3, 'Issue distinct|successor baseline', 'FR-06'),
        n('6', 4, 'Retain retrievable|baseline history', 'FR-07'),
        n('7', 2, 'Preserve current|baseline unchanged', 'FR-06', side='R'),
    ], [
        e('1', '2', 'Exact mission / requirement / design / model / software /|interface / evidence revisions; proposed engineering change'),
        e('2', '3', 'Reciprocal|impact findings'),
        e('3', '4', 'Authorized change decision, rationale, findings|and dispositions; unresolved dependencies / reassessments', 'authorization'),
        e('4', '7', '[unauthorized /|not accepted]', 'findings'),
        e('4', '5', '[authorized change] Predecessor, request, decision|and regenerated / stale / unresolved product / evidence status', 'authorization'),
        e('5', '6', 'Distinct successor and preserved predecessor;|exact revisions, history and controlling decisions'),
    ]),
    p('23-reviews', '23  Engineering views and authorized technical reviews', [
        n('1', 0, 'Generate filtered|engineering views', 'FR-37'),
        n('2', 1, 'Assemble phase-baseline|review package', 'FR-38'),
        n('3', 1, 'Review identified|baseline', side='R', owner='Reviewers', kind='external'),
        n('4', 2, 'Prepare findings|for authority decision', 'FR-38'),
        n('5', 2, 'Decide scoped|technical review', side='R', owner='Review authority', kind='external'),
        n('6', 3, 'Check authority,|baseline and criteria', 'FR-42'),
        n('7', 4, 'Record review|disposition', 'FR-42'),
        n('8', 5, 'Retain conditional|closure obligations', 'FR-42'),
        n('9', 3, 'Retain decision|rejection findings', 'FR-42', side='R'),
        n('10', 4, 'Retain accepted|review scope', 'FR-42', side='R'),
        n('11', 5, 'Retain blocked|progression status', 'FR-42', side='R'),
    ], [
        e('1', '2', 'Controlled EPS baseline, filtered mission / allocation /|design / interface / analysis views with units, legends and links'),
        e('2', '3', 'Prepared|review package'),
        e('3', '4', 'Reviewer findings against exact phase baseline|and designated entrance / scoped success criteria', 'findings'),
        e('4', '5', 'Baseline +|findings'),
        e('5', '6', 'Designated-authority decision, exact baseline /|criteria revisions, decision role and rationale', 'authorization'),
        e('6', '9', '[wrong role /|revision]', 'findings'),
        e('6', '7', '[authorized, matching basis] Decision and rationale;|prepared status remains distinct from review acceptance', 'authorization'),
        e('7', '10', '[accepted]|scope + basis'),
        e('7', '8', '[conditional]|Conditions, owners,|actions and dates', pos=[250, 1034], anchor='end', width=220),
        e('7', '11', '[progression-blocked] Rationale, conditions,|closure actions, owners and dates', path='M400 1000 V1090 H820 V1120', pos=[440, 1034], width=520),
    ]),
]


class Panel:
    def __init__(self, spec, metrics=None):
        self.spec = spec
        self.figure = Figure(spec['title'], W, 185+210*max(node['row'] for node in spec['nodes']), metrics)
        self.figure.el('desc').text = ('Proposed decomposition of existing functional requirements. '
            'Gray identifies external participants. Framework activities exchange the labeled '
            'information. Human decisions retain their specified authority.')
        self.figure.text(spec['title'], 20, 30, size=27, weight='bold')
        self.nodes, self.flows = {}, []
        for node in spec['nodes']:
            self.add_node(node)
        for index, flow in enumerate(spec['edges'], 1):
            self.add_edge(dict(id=str(index), **flow))

    def add_node(self, spec):
        key = spec['id']
        x, width = COLUMNS[spec['side']]
        y, height = 70+210*spec['row'], 90
        require(key not in self.nodes, 'Duplicate activity identifier')
        node = dict(spec, box=(x, y, width, height))
        self.nodes[key] = node
        group = self.figure.el('g', data_node=key, data_kind=spec['kind'],
            data_owner=spec['owner'], data_frs=' '.join(spec['fr']),
            data_activity_id=self.spec['id'][:2]+'.'+key)
        self.figure.rect(x, y, width, height, group,
                         fill=LIGHT if spec['kind'] == 'external' else 'white')
        header = spec['owner'] if spec['kind'] == 'external' else (
            self.spec['id'][:2]+'.'+key+'  '+', '.join(spec['fr']))
        self.figure.text(header, x+width/2, y+23, size=ID_FONT, weight='normal',
                         anchor='middle', width=width-16, parent=group, data_trace_header='true')
        baseline = y+53 if len(spec['labels']) == 2 else y+61
        self.figure.lines(spec['labels'], x+width/2, baseline, leading=27,
                          size=NODE_FONT, weight='bold', anchor='middle',
                          width=width-18, parent=group, data_activity_label='true')

    def add_edge(self, spec):
        source, target = (self.nodes[spec[key]] for key in ('source', 'target'))
        sx, sy, sw, sh = source['box']
        tx, ty, tw, th = target['box']
        sc, tc = sx+sw/2, tx+tw/2
        width, anchor = 650, 'start'
        if 'path' in spec:
            path, pos = spec['path'], spec['pos']
        elif source['side'] == target['side']:
            require(sy+sh < ty, 'Default same-column exchange must run downwards')
            path = f'M{sc:g} {sy+sh:g} V{ty:g}'
            pos = (sc+25, sy+sh+34)
            if source['side'] == 'R':
                pos, anchor, width = (sc-25, sy+sh+34), 'end', 480
        elif sy == ty:
            left_to_right = sx < tx
            start, finish = (sx+sw, tx) if left_to_right else (sx, tx+tw)
            path = f'M{start:g} {sy+70:g} H{finish:g}'
            pos, width = (500, sy+22), 155
        else:
            require(sy+sh < ty, 'Default cross-column exchange must run downwards')
            end = tx if sx < tx else tx+tw
            path = f'M{sc:g} {sy+sh:g} V{ty+45:g} H{end:g}'
            pos = (sc+25, sy+sh+34)
            if source['side'] == 'R':
                path = f'M{sc:g} {sy+sh:g} V{ty-30:g} H{tc:g} V{ty:g}'
                pos, anchor, width = (sc-25, sy+sh+34), 'end', 720
        path, pos = spec.get('path', path), spec.get('pos', pos)
        anchor, width = spec.get('anchor', anchor), spec.get('width', width)
        styles = {'information': 'solid', 'findings': 'dotted', 'authorization': 'dashed'}
        group = self.figure.el('g', data_flow=spec['id'], data_source=spec['source'],
            data_target=spec['target'], data_kind=spec['kind'],
            data_exchange_label=' / '.join(spec['labels']))
        self.figure.arrow(path, group, style=styles[spec['kind']], id='flow-'+spec['id'])
        self.figure.lines(spec['labels'], *pos, size=FLOW_FONT, leading=25,
            anchor=anchor, width=width, parent=group, data_exchange_text=spec['id'])
        self.flows.append(dict(spec, path=path, pos=list(pos), anchor=anchor, width=width))


def actual_requirements():
    text = REQUIREMENTS.read_text().split('\\subsection{Measures of performance}')[0]
    pairs = re.findall(r'^(FR-\d\d) & (.*?) & ', text, re.M)
    require(len(pairs) == len(dict(pairs)), 'Duplicate functional requirement')
    require(pairs, 'No functional requirements found in the authoritative table')
    return dict(pairs)


def text_bounds(figure, text):
    size = float(text.attrib['font-size'])
    width = figure.metrics.measure(text.text or '', size, text.attrib.get('font-weight', 'normal'))
    x, y = float(text.attrib['x']), float(text.attrib['y'])
    anchor = text.attrib.get('text-anchor', 'start')
    left = x-width/2 if anchor == 'middle' else x-width if anchor == 'end' else x
    return left, y-.82*size, width, size*1.06


def overlap(a, b):
    return (max(a[0], b[0]) < min(a[0]+a[2], b[0]+b[2]) and
            max(a[1], b[1]) < min(a[1]+a[3], b[1]+b[3]))


def crosses(a, b, box):
    left, top, width, height = box
    x1, y1 = a
    x2, y2 = b
    return ((x1 == x2 and left < x1 < left+width and
             max(min(y1, y2), top) < min(max(y1, y2), top+height)) or
            (y1 == y2 and top < y1 < top+height and
             max(min(x1, x2), left) < min(max(x1, x2), left+width)))


def on_boundary(point, box):
    x, y = point
    left, top, width, height = box
    return (left <= x <= left+width and top <= y <= top+height and
            (x in (left, left+width) or y in (top, top+height)))


def check_panel(panel):
    root = panel.figure.root
    groups = root.findall('.//{*}g[@data-flow]')
    require(len(groups) == len(panel.flows), 'Missing or duplicate exchange')
    node_groups = root.findall('.//{*}g[@data-node]')
    require(len(node_groups) == len(panel.nodes), 'Missing or duplicate activity')
    labels, routes = [], []
    for group, flow in zip(groups, panel.flows):
        require(group.attrib['data-source'] == flow['source'] and
                group.attrib['data-target'] == flow['target'], 'Changed exchange dependency')
        visible = [text.text for text in group.findall('./{*}text')]
        require(visible == flow['labels'] and visible and all(visible), 'Missing or changed exchange label')
        require(group.attrib['data-kind'] == flow['kind'], 'Changed exchange kind')
        path = group.find('./{*}path')
        require(path.attrib['d'] == flow['path'], 'Changed exchange route')
        points = orthogonal_points(path.attrib['d'])
        require(on_boundary(points[0], panel.nodes[flow['source']]['box']) and
                on_boundary(points[-1], panel.nodes[flow['target']]['box']),
                'Exchange endpoint is not on its sender / receiver')
        require(path.attrib.get('stroke-dasharray') == LINE_PATTERNS[
            {'information': 'solid', 'findings': 'dotted', 'authorization': 'dashed'}[flow['kind']]],
            'Changed information / feedback / authorization line meaning')
        for key, node in panel.nodes.items():
            if key not in (flow['source'], flow['target']):
                require(not any(crosses(a, b, node['box']) for a, b in zip(points, points[1:])),
                        'Exchange crosses unrelated activity: '+panel.spec['id']+'/'+flow['id']+'/'+key)
        routes.append(points)
        for text in group.findall('./{*}text'):
            labels.append((text_bounds(panel.figure, text), text.text))
    for i, (box, label) in enumerate(labels):
        for points in routes:
            require(not any(crosses(a, b, box) for a, b in zip(points, points[1:])),
                    'Route crosses exchange text: '+panel.spec['id']+'/'+str(label))
        for node in panel.nodes.values():
            require(not overlap(box, node['box']), 'Exchange text overlaps node: '+str(label))
        require(not any(overlap(box, prior[0]) for prior in labels[:i]),
                'Exchange labels overlap: '+panel.spec['id']+'/'+str(label))
    visible_frs = set()
    for group in node_groups:
        node = panel.nodes[group.attrib['data-node']]
        texts = group.findall('./{*}text')
        activity_texts = group.findall('./{*}text[@data-activity-label]')
        require([text.text for text in activity_texts] == node['labels'] and
                1 <= len(activity_texts) <= 2, 'Dense or changed activity label')
        require(group.attrib['data-owner'] == node['owner'] and
                group.attrib['data-frs'] == ' '.join(node['fr']), 'Changed activity ownership / FR mapping')
        header = group.find('./{*}text[@data-trace-header]').text
        if node['kind'] != 'external':
            expected = panel.spec['id'][:2]+'.'+node['id']+'  '+', '.join(node['fr'])
            require(header == expected, 'Missing visible activity / FR identifier')
            visible_frs.update(node['fr'])
        rect = group.find('./{*}rect')
        require(rect.attrib['fill'] == (LIGHT if node['kind'] == 'external' else 'white'),
                'Gray is reserved for external participants')
        for text in texts:
            box = text_bounds(panel.figure, text)
            x, y, w, h = node['box']
            require(x <= box[0] and box[0]+box[2] <= x+w and
                    y <= box[1] and box[1]+box[3] <= y+h, 'Node text outside activity')
    # Every node is connected to at least one exchange, and every framework step
    # has incoming information. Context is deliberately supplied at panel roots.
    receivers = {flow['target'] for flow in panel.flows}
    connected = receivers | {flow['source'] for flow in panel.flows}
    require(connected == set(panel.nodes), 'Isolated activity')
    require(all(node['row'] == 0 or key in receivers for key, node in panel.nodes.items()
                if node['kind'] != 'external'), 'Activity has no incoming information')
    require(min(float(t.attrib['font-size']) for t in root.findall('.//{*}text')) >= 22,
            'Unreadably small label')
    return dict(visible_frs=sorted(visible_frs), labeled_exchanges=len(groups),
                short_activity_labels=True, visible_activity_identifiers=True,
                endpoints_on_receivers=True, no_routes_through_unrelated_nodes=True,
                labels_clear_of_routes_nodes_and_each_other=True,
                external_ownership_and_gray_checked=True, minimum_source_font_pt=22)


def coverage(panels):
    mapping = {}
    for panel in panels:
        check_panel(panel)
        for key, node in panel.nodes.items():
            if node['kind'] == 'external':
                continue
            for fr in node['fr']:
                mapping.setdefault(fr, []).append(dict(panel=panel.spec['id'],
                    activity=panel.spec['id'][:2]+'.'+key, label=' '.join(node['labels'])))
    require(set(mapping) == set(actual_requirements()),
            'FR coverage differs from the authoritative requirement table: '+
            str(set(mapping) ^ set(actual_requirements())))
    return dict(sorted(mapping.items()))


def check_report(panels, mapping):
    text = APPENDIX.read_text()
    require('\\chapter{Functional requirement activity and information flows}' in text and
            '\\label{appendix:fr-activity-flows}' in text, 'Missing appendix title / label')
    for panel in panels:
        require('\\FRFlowGraphic{'+panel.spec['id']+'}' in text,
                'Panel is missing from the report')
    index = text.split('% BEGIN COVERAGE INDEX')[1].split('% END COVERAGE INDEX')[0]
    listed = set(re.findall(r'FR-\d\d', index))
    require(listed == set(mapping), 'Report coverage index differs from actual requirements')
    rows = {row.split(' & ')[0]: set(re.findall(r'FR-\d\d', row))
            for row in index.splitlines() if re.match(r'^\d\d & ', row)}
    require(set(rows) == {panel.spec['id'][:2] for panel in panels}, 'Report panel index is incomplete')
    for panel in panels:
        visible = {fr for node in panel.nodes.values() for fr in node['fr']}
        require(rows[panel.spec['id'][:2]] == visible, 'Report index has changed per-panel FR mapping')
    require('\\include{fr-activity-flows}' in (FIG.parent / 'main.tex').read_text(),
            'Appendix is not registered')
    return dict(actual_requirements=len(mapping), panels=len(panels),
                exact_visible_fr_coverage=True, report_coverage_index_checked=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', required=True, type=Path)
    args = parser.parse_args()
    job = args.jobdir.resolve()
    require(not job.is_relative_to(ROOT), 'Use an external scratch directory')
    job.mkdir(parents=True, exist_ok=True)
    metrics = SerifMetrics()
    panels = [Panel(spec, metrics) for spec in PANELS]
    mapping = coverage(panels)
    checks = check_report(panels, mapping)
    published = []
    for panel in panels:
        base = FIG / ('fr-activity-flow-'+panel.spec['id'])
        artifact = render_figure(panel.figure, base, job)
        artifact['checks'].update(check_panel(panel))
        published.append(dict(id=panel.spec['id'], title=panel.spec['title'], file=base.name,
                              nodes=list(panel.nodes.values()), flows=panel.flows, **artifact))
    run(['pdfunite', *[str(FIG / (panel['file']+'.pdf')) for panel in published], str(BASE.with_suffix('.pdf'))])
    sources = [REQUIREMENTS, APPENDIX, FIG.parent / 'fr-inputs-outputs.tex',
               FIG.parent / 'logical.tex', FIG.parent / 'as-is-domain.tex', FIG.parent / 'main.tex']
    provenance = dict(kind='Proposed decomposition of existing functional requirements',
        source_sha256={str(path.relative_to(ROOT)): sha(path) for path in sources},
        generator_sha256=sha(Path(__file__)), style_sha256=sha(FIG / 'diagram_style.py'),
        artifact_sha256={'pdf': sha(BASE.with_suffix('.pdf'))}, requirements=actual_requirements(),
        coverage=mapping, panels=published, checks=checks,
        reproduction=['python3 final_report/fig/fr-activity-flows.py --jobdir /absolute/external/check-dir'])
    BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
