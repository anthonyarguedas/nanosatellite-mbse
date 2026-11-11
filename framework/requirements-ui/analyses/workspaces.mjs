// Optional analysis configurations. They leave the generic catalog and UX intact.
import { randomUUID } from 'node:crypto';
import { blankWorkspace, MAX_VARIABLES, nextId, requirementMarkers, seedRequirements, validateWorkspace } from '../model.mjs';
import { scriptInstance, setVerificationMethods } from '../verification-methods.mjs';

function addScript(workspace, definitions, id) {
  const definition = definitions.find(definition => definition.id === id);
  if (!definition) throw new Error(`Register the ${id} script before creating this analysis.`);
  const script = scriptInstance(definition, { key: randomUUID(), id: nextId(workspace, 'Script') });
  workspace.scripts.push(script);
  return script;
}

function addRequirement(workspace, { text, parameters, context, affected = [], sources = [], condition = '', script, rationale }) {
  for (const [name, unit] of parameters) {
    const existing = workspace.variables.find(variable => variable.name === name);
    if (existing && (existing.type !== 'float' || (existing.unit ?? '') !== (unit ?? ''))) {
      throw new Error(`${name}: the analysis needs a Float parameter with units ${unit || '(none)'}. Rename the conflicting variable first.`);
    }
    if (!existing) {
      if (workspace.variables.length >= MAX_VARIABLES) throw new Error(`This analysis exceeds the ${MAX_VARIABLES} shared parameter limit. Remove unused variable columns.`);
      workspace.variables.push({ name, type: 'float', ...(unit ? { unit } : {}) });
      for (const row of workspace.statements) row.parameters[name] = null;
    }
  }
  const row = { key: randomUUID(), id: nextId(workspace, 'Requirement', script?.definition === 'scenario_illumination' ? 'SCN' : 'MPT'),
    context, kind: 'Requirement', text, condition: '', affected, sources,
    origin: 'framework/requirements-ui/analyses/README.md', rationale,
    parameters: Object.fromEntries(workspace.variables.map(variable => [variable.name, null])) };
  if (condition) setVerificationMethods(row, [{ key: 'analysis', condition, ...(script ? { script: script.key } : {}) }]);
  workspace.statements.push(row);
  return row;
}

export function createMPPTWorkspace(catalog, definitions) {
  const workspace = blankWorkspace();
  workspace.variables = [];
  const bus = { key: 'mppt-bus', id: 'BUS', name: 'CubeSat Bus', owner: 'mission', definition: 'SpaceSegment::CubeSat' };
  const eps = { key: 'mppt-eps', id: 'EPS', name: 'Power', owner: bus.key, definition: `${bus.definition}::PowerSubsystem` };
  const solar = { key: 'mppt-array', id: 'SOL', name: 'Modeled array section', owner: eps.key, definition: `${eps.definition}::SolarArrays` };
  const converter = { key: 'mppt-converter', id: 'REG', name: 'Modeled MPPT receiver', owner: eps.key, definition: `${eps.definition}::RegulatorsAndConverters` };
  workspace.elements.push(bus, eps, solar, converter);
  const script = addScript(workspace, definitions, 'mppt_po');
  const ref = name => `${script.id}.${name}`;
  const rationale = 'Proposed preliminary simulation criterion. Inputs and acceptance limits require engineer approval and sources. No mission, product or compliance values are assumed. The script uses one uniform section, an empirical I-V curve and an ideal P&O controller. See analyses/README.md.';
  function requirement(text, names, condition, backed = false, sources = []) {
    const row = addRequirement(workspace, { text, parameters: names.map(name => [name, script.inputs.find(input => input.name === name)?.unit
      ?? ({ input_absolute_max_V: 'V', source_current_limit_A: 'A', settling_limit_s: 's', delivered_energy_min_J: 'J' })[name]]),
    context: eps.key, affected: [solar.key, converter.key], sources, condition, ...(backed ? { script } : {}), rationale });
    for (const name of names) if (Object.hasOwn(script.parameters, name)) script.parameters[name] = `${row.id}.${name}`;
    return row;
  }
  const points = requirement(
    'The array model shall use reference points $$voc_ref_V$$, $$isc_ref_A$$, $$vmp_ref_V$$ and $$imp_ref_A$$ at irradiance $$reference_irradiance_W_m2$$ and temperature $$reference_temperature_C$$.',
    ['voc_ref_V', 'isc_ref_A', 'vmp_ref_V', 'imp_ref_A', 'reference_irradiance_W_m2', 'reference_temperature_C'],
    '0 < vmp_ref_V < voc_ref_V and 0 < imp_ref_A < isc_ref_A and reference_irradiance_W_m2 > 0 and reference_temperature_C > -273.15');
  const scaling = requirement(
    'The array model shall apply voltage temperature coefficient $$voltage_temp_coeff_V_C$$, relative current temperature coefficient $$current_temp_coeff_per_C$$ and logarithmic irradiance coefficient $$voltage_log_coefficient_V$$.',
    ['voltage_temp_coeff_V_C', 'current_temp_coeff_per_C', 'voltage_log_coefficient_V'],
    'math.isfinite(voltage_temp_coeff_V_C) and math.isfinite(current_temp_coeff_per_C) and voltage_log_coefficient_V >= 0');
  const environment = requirement(
    'The tracker shall be assessed for $$duration_s$$ with a change at $$change_time_s$$ from irradiance $$irradiance_start_W_m2$$ and temperature $$temperature_start_C$$ to irradiance $$irradiance_end_W_m2$$ and temperature $$temperature_end_C$$.',
    ['duration_s', 'change_time_s', 'irradiance_start_W_m2', 'temperature_start_C', 'irradiance_end_W_m2', 'temperature_end_C'],
    'duration_s > 0 and 0 <= change_time_s <= duration_s and irradiance_start_W_m2 >= 0 and irradiance_end_W_m2 >= 0 and temperature_start_C > -273.15 and temperature_end_C > -273.15');
  const controller = requirement(
    'The tracker shall perturb voltage by $$voltage_step_V$$ every $$sample_period_s$$ from initial voltage $$initial_voltage_V$$.',
    ['voltage_step_V', 'sample_period_s', 'initial_voltage_V'],
    'voltage_step_V > 0 and sample_period_s > 0 and initial_voltage_V > 0');
  const sources = [points.key, scaling.key, environment.key, controller.key];
  requirement(
    'The source maximum power voltage shall remain within the tracking interval from $$tracking_min_V$$ to $$tracking_max_V$$ during illuminated phases.',
    ['tracking_min_V', 'tracking_max_V'],
    `0 < tracking_min_V < tracking_max_V and ${ref('min_mpp_voltage_V')} >= tracking_min_V and ${ref('max_mpp_voltage_V')} <= tracking_max_V`, true, sources);
  requirement(
    'The source open circuit voltage shall remain at most $$input_absolute_max_V$$.',
    ['input_absolute_max_V'], `input_absolute_max_V > 0 and ${ref('max_open_circuit_voltage_V')} <= input_absolute_max_V`, true, sources);
  requirement(
    'The source short circuit current shall remain at most $$source_current_limit_A$$.',
    ['source_current_limit_A'], `source_current_limit_A > 0 and ${ref('max_short_circuit_current_A')} <= source_current_limit_A`, true, sources);
  requirement(
    'The tracker shall capture at least fraction $$tracking_efficiency_min$$ of the energy attainable within its tracking interval.',
    ['tracking_efficiency_min'], `0 < tracking_efficiency_min <= 1 and ${ref('tracking_efficiency')} >= tracking_efficiency_min`, true, sources);
  requirement(
    'The tracker shall settle within $$settling_limit_s$$ to relative power error at most $$settling_relative_band$$ for at least $$settling_hold_s$$ through the end of each illuminated phase.',
    ['settling_limit_s', 'settling_relative_band', 'settling_hold_s'],
    `settling_limit_s >= 0 and 0 < settling_relative_band < 1 and settling_hold_s > 0 and ${ref('settled')} and ${ref('settling_time_s')} <= settling_limit_s`, true, sources);
  requirement(
    'The conditioning model shall deliver at least $$delivered_energy_min_J$$ over the assessed interval at conversion efficiency $$conversion_efficiency$$.',
    ['delivered_energy_min_J', 'conversion_efficiency'],
    `delivered_energy_min_J >= 0 and 0 < conversion_efficiency <= 1 and ${ref('delivered_energy_J')} >= delivered_energy_min_J`, true, sources);
  return validateWorkspace(workspace, catalog);
}

// Return an independent copy, suitable for Save as. No existing equation or
// acceptance condition is replaced. Detailed inputs live in the script table.
export function addScenarioAnalysis(original, catalog, definitions, { orbitKey } = {}) {
  const workspace = structuredClone(original);
  const orbits = workspace.statements.filter(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  const orbit = orbitKey ? orbits.find(row => row.key === orbitKey) : orbits.length === 1 ? orbits[0] : null;
  if (orbitKey && !orbit) throw new Error('Choose an existing OrbitPeriod requirement key.');
  if (!orbitKey && orbits.length > 1) throw new Error('Several orbit definitions exist. Select one with --orbit.');
  const script = addScript(workspace, definitions, 'scenario_illumination');
  if (orbit) Object.assign(script.parameters, { altitude_km: `${orbit.id}.altitude_km`, earth_radius_km: `${orbit.id}.earthRadius_km`,
    mu_km3_s2: `${orbit.id}.gravitationalParameter_km3_s2` });
  const rationale = 'Proposed interval-specific illumination criterion. Set and source the scenario inputs in the Python script input table. Supply an approved acceptance limit here. Eclipse lengths use midpoint samples and are clipped at interval boundaries. Repeat at a smaller step and cover the required epochs and orbital phases. This criterion establishes no thermal, energy closure or complete mission compliance.';
  const common = { context: 'mission', affected: orbit?.affected ?? [], sources: orbit ? [orbit.key] : [], script, rationale };
  addRequirement(workspace, { ...common,
    text: 'The longest total eclipse within the assessed interval shall be at most $$eclipse_limit_s$$.',
    parameters: [['eclipse_limit_s', 's']], condition: `eclipse_limit_s >= 0 and ${script.id}.longest_eclipse_s <= eclipse_limit_s` });
  addRequirement(workspace, { ...common,
    text: 'The assessed panel section shall receive interval mean direct irradiance of at least $$irradiance_min_W_m2$$.',
    parameters: [['irradiance_min_W_m2', 'W/m**2']], condition: `irradiance_min_W_m2 >= 0 and ${script.id}.mean_irradiance_W_m2 >= irradiance_min_W_m2` });
  return validateWorkspace(workspace, catalog);
}

// A populated, reproducible test bench. Reusable blank configurations above
// retain their unset inputs. No COTS or real mission data is implied here.
export function createAnalysisTestWorkspace(catalog, definitions) {
  let workspace = createMPPTWorkspace(catalog, definitions);
  const orbitElement = { key: 'test-orbit', id: 'ORB', name: 'Test orbit', owner: 'mission', definition: 'Orbit' };
  workspace.elements.push(orbitElement);
  seedRequirements(workspace, catalog, [orbitElement]);
  workspace = addScenarioAnalysis(workspace, catalog, definitions);
  const orbit = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  orbit.parameters.altitude_km = '500';
  const illumination = workspace.scripts.find(script => script.definition === 'scenario_illumination');
  Object.assign(illumination.parameters, {
    inclination_deg: '0', raan_deg: '0', argument_latitude_deg: '0', epoch_jd: '2460754.5',
    duration_s: `2 * ${orbit.id}.orbit_period_s`, step_s: '2', earth_j2: '0.00108263', solar_constant_W_m2: '1361',
    panel_normal_radial: '1', panel_normal_along: '0', panel_normal_cross: '0', sun_tracking: 'True',
  });
  const mppt = workspace.scripts.find(script => script.definition === 'mppt_po');
  const inputs = {
    voc_ref_V: '8', isc_ref_A: '1.1', vmp_ref_V: '6.4', imp_ref_A: '1',
    reference_irradiance_W_m2: '1361', reference_temperature_C: '28',
    voltage_temp_coeff_V_C: '-0.02', current_temp_coeff_per_C: '0.0005', voltage_log_coefficient_V: '0.25',
    irradiance_start_W_m2: `${illumination.id}.max_irradiance_W_m2`, irradiance_end_W_m2: `${illumination.id}.mean_irradiance_W_m2`,
    temperature_start_C: '28', temperature_end_C: '50', change_time_s: '60', duration_s: '120',
    sample_period_s: '0.1', voltage_step_V: '0.05', initial_voltage_V: '3', tracking_min_V: '2', tracking_max_V: '8',
    conversion_efficiency: '0.9', settling_relative_band: '0.02', settling_hold_s: '5',
  };
  for (const [name, expression] of Object.entries(inputs)) {
    const [id, parameter] = mppt.parameters[name].split('.');
    workspace.statements.find(row => row.id === id).parameters[parameter] = expression;
  }
  for (const [name, expression] of Object.entries({ input_absolute_max_V: '9', source_current_limit_A: '1.2',
    tracking_efficiency_min: '0.95', settling_limit_s: '15', delivered_energy_min_J: '400',
    eclipse_limit_s: '2400', irradiance_min_W_m2: '800' })) {
    workspace.statements.find(row => requirementMarkers(row.text).names.includes(name)).parameters[name] = expression;
  }
  for (const row of workspace.statements) row.rationale = 'Synthetic test bench. Values and acceptance limits are illustrative test data. '
    + 'See analyses/README.md for the model and test setup.' + (row.origin ? ` Equation or criterion basis: ${row.origin}.` : '');
  const environment = workspace.statements.find(row => row.id === 'MPT003');
  environment.sources.push(workspace.statements.find(row => row.id === 'SCN002').key);
  environment.rationale += ' Initial irradiance uses the illumination maximum and final irradiance uses its interval mean. '
    + 'These are two constant test levels. They do not replay the orbital time history.';
  return validateWorkspace(workspace, catalog);
}
