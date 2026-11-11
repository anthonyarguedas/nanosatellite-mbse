// Optional report assessments. All content uses the existing version 14 model.
// No current workspace, catalog, engine, UI or execution policy is changed.
import { randomUUID } from 'node:crypto';
import { addGenericRequirements, addResourceBudgets, blankWorkspace, MAX_VARIABLES, nextId, validateWorkspace } from '../model.mjs';
import { scriptInstance, setVerificationMethods } from '../verification-methods.mjs';
import { cotsBinding } from '../cots-bindings.mjs';

const document = 'framework/requirements-ui/analyses/REPORT-COVERAGE.md';
const field = (name, unit = '', type = 'float', expression = null) => ({ name, unit, type, expression });
const label = name => name.replace(/_(?:per_s|W_m2|kg|m3|m2|m|J|W|V|A|C|K|s|Hz|deg|ohm|A2s|Ah)$/, '')
  .replaceAll('_', ' ').replace(/\bsoc\b/g, 'state of charge');
const profiles = new Map();
function profile(id, name, configure, products = []) { profiles.set(id, { id, name, configure, products }); }

function builder(catalog, definitions, name, cotsFacts) {
  const workspace = blankWorkspace();
  workspace.variables = [];
  const bus = { key: 'report-bus', id: 'BUS', name: 'CubeSat Bus', owner: 'mission', definition: 'SpaceSegment::CubeSat' };
  const eps = { key: 'report-eps', id: 'EPS', name: 'Power', owner: bus.key, definition: `${bus.definition}::PowerSubsystem` };
  workspace.elements.push(bus, eps);
  const rationale = `${name}. This is a bounded report assessment, with inputs and acceptance limits supplied by the engineer. `
    + 'No product, mission, protection setting or safety margin is assumed. Use compatible sources and conditions. '
    + 'An input declaration checks the executed model domain. Separate product criteria assess its outputs. '
    + 'A passing case covers its declared model and interval. See analyses/REPORT-COVERAGE.md for remaining scope.';
  function variable(parameter) {
    const previous = workspace.variables.find(item => item.name === parameter.name);
    if (previous && (previous.type !== parameter.type || (previous.unit ?? '') !== parameter.unit)) {
      throw new Error(`Report assessment has conflicting parameter ${parameter.name}.`);
    }
    if (!previous) {
      if (workspace.variables.length >= MAX_VARIABLES) throw new Error(`Report assessment exceeds ${MAX_VARIABLES} shared parameters.`);
      workspace.variables.push({ name: parameter.name, type: parameter.type, ...(parameter.unit ? { unit: parameter.unit } : {}) });
      for (const row of workspace.statements) row.parameters[parameter.name] = null;
    }
  }
  function requirement({ text, fields = [], condition, script, component, prefix = 'ASM', sources = [], reports = [], extra = '' }) {
    for (const parameter of fields) variable(parameter);
    const row = { key: randomUUID(), id: nextId(workspace, 'Requirement', prefix), context: eps.key, kind: 'Requirement',
      text, condition: '', sources: [...sources], affected: [], origin: `${document}#${reports.join(',')}`,
      rationale: `${rationale}${extra ? ` ${extra}` : ''}`, parameters: Object.fromEntries(workspace.variables.map(item => [item.name, null])) };
    for (const parameter of fields) row.parameters[parameter.name] = parameter.expression;
    setVerificationMethods(row, [{ key: 'assessment', condition, ...(script ? { script: script.key } : {}), ...(component ? { component: component.key } : {}) }]);
    workspace.statements.push(row);
    if (component) component.requirements.push(row.key);
    return row;
  }
  function analysis(id, caseName, reports) {
    const definition = definitions.find(item => item.id === id);
    if (!definition) throw new Error(`Register ${id} before creating this report assessment.`);
    const script = scriptInstance(definition, { key: randomUUID(), id: nextId(workspace, 'Script') });
    script.name = caseName;
    workspace.scripts.push(script);
    const numeric = definition.inputs.filter(input => input.type !== 'boolean');
    const owners = new Map(), sources = [];
    for (let offset = 0; offset < numeric.length; offset += 4) {
      const group = numeric.slice(offset, offset + 4);
      const row = requirement({
        text: `The ${caseName.toLowerCase()} assessment shall use ${group.map(input => `${label(input.name)} $$${input.name}$$`).join(', ')}.`,
        fields: group.map(input => field(input.name, input.unit, input.type)), reports, script, prefix: 'INP',
        condition: group.map(input => `math.isfinite(${input.name})`).join(' and '),
        extra: 'Boolean model choices remain explicit unset inputs in the script table.' });
      sources.push(row.key);
      for (const input of group) { owners.set(input.name, row); script.parameters[input.name] = `${row.id}.${input.name}`; }
    }
    return {
      script, sources, ref: output => `${script.id}.${output}`, input: input => script.parameters[input],
      fields(...names) {
        return names.map(name => {
          const input = definition.inputs.find(input => input.name === name);
          if (!input || input.type === 'boolean') throw new Error(`${id}.${name}: choose a numeric model input.`);
          return field(name, input.unit, input.type, script.parameters[name]);
        });
      },
      set(input, expression) {
        const row = owners.get(input);
        if (row) row.parameters[input] = expression;
        else if (Object.hasOwn(script.parameters, input)) script.parameters[input] = expression;
        else throw new Error(`${id} has no input ${input}.`);
      },
      check(text, fields, condition, ids = reports) {
        return requirement({ text, fields, condition, reports: ids, script, sources, prefix: 'CHK' });
      },
    };
  }
  function component(product, selections) {
    const facts = cotsFacts[product];
    if (!facts) throw new Error(`Load the current COTS facts for ${product} before creating this assessment.`);
    const row = { key: randomUUID(), id: nextId(workspace, 'Component'), owner: eps.key, product, requirements: [], facts: [] };
    for (const [name, query] of selections) {
      const matches = facts.filter(fact => Object.entries(query).every(([key, value]) => fact[key] === value));
      if (matches.length !== 1) throw new Error(`${product}.${name}: expected one exact current COTS record, found ${matches.length}.`);
      row.facts.push(cotsBinding(matches[0], { key: randomUUID(), name }));
    }
    workspace.components.push(row);
    return row;
  }
  return { workspace, analysis, requirement, component, finish() {
    // The same generic study requirements appear in every EPS session.
    addGenericRequirements(workspace, catalog);
    addResourceBudgets(workspace); workspace.resourceBudgets = true;
    return validateWorkspace(workspace, catalog);
  } };
}

function energyProfile(b, survival = false) {
  const reports = ['FR-16', 'FR-19', 'EPS-10', 'EPS-11', 'EPS-12', 'EPS-13', 'EPS-14'];
  const cases = [b.analysis('eps_energy_segment', survival ? 'Survival interval' : 'Nominal eclipse', reports),
    b.analysis('eps_energy_segment', survival ? 'Recovery interval' : 'Nominal sunlight', reports)];
  const [first, last] = cases;
  last.set('energy_initial_J', first.ref('energy_end_J'));
  last.set('soc_initial', first.ref('soc_end'));
  for (const input of ['energy_capacity_J', 'charge_capacity_C']) last.set(input, first.input(input));
  for (const a of cases) {
    a.check('The EPS shall supply the declared load throughout at least $$required_service_s$$ of the assessed interval.',
      [field('required_service_s', 's')],
      `required_service_s > 0 and ${a.input('duration_s')} >= required_service_s and ${a.ref('unserved_energy_J')} == 0 and ${a.ref('service_duration_s')} >= ${a.input('duration_s')}`,
      ['FR-16', survival ? 'EPS-12' : 'EPS-10']);
    a.check('The battery shall retain at least $$energy_reserve_J$$ of energy throughout the assessed interval.',
      [field('energy_reserve_J', 'J', 'float', a.input('energy_reserve_J'))],
      `${a.ref('energy_reserve_ok')}`, ['EPS-10', 'EPS-12']);
    a.check('The battery charge state shall remain at least $$soc_min$$ throughout the assessed interval.',
      [field('soc_min', '', 'float', a.input('soc_min'))], `${a.ref('soc_reserve_ok')}`, ['EPS-10', 'EPS-12']);
    a.check('The battery shall respect its separate charging and discharging temperature intervals at $$temperature_C$$.',
      [field('temperature_C', 'degC', 'float', a.input('temperature_C'))],
      `${a.ref('charge_temperature_ok')} and ${a.ref('discharge_temperature_ok')}`, ['EPS-13']);
    a.check('The EPS shall accommodate solar surplus within its declared handling capacity $$surplus_capacity_W$$.',
      [field('surplus_capacity_W', 'W', 'float', a.input('surplus_capacity_W'))], `${a.ref('surplus_supported')}`, ['EPS-14']);
  }
  if (!survival) {
    last.check('The battery shall replenish its initial energy within numerical tolerance $$closure_tolerance_J$$ over the nominal repeating interval.',
      [field('closure_tolerance_J', 'J')],
      `closure_tolerance_J >= 0 and ${last.ref('energy_end_J')} >= ${first.input('energy_initial_J')} - closure_tolerance_J`, ['EPS-11']);
    last.check('The battery shall replenish its initial charge state $$soc_initial$$ over the nominal repeating interval.',
      [field('soc_initial', '', 'float', first.input('soc_initial'))], `${last.ref('soc_end')} >= soc_initial`, ['EPS-11']);
    for (const a of cases) a.check('The nominal battery cycle shall remain within depth of discharge $$dod_max$$.',
      [field('dod_max')], `0 < dod_max <= 1 and ${a.ref('soc_minimum')} >= 1 - dod_max`, ['EPS-09', 'EPS-10']);
  }
}
profile('energy', 'Nominal energy and charge closure', b => energyProfile(b));
profile('survival', 'Survival and recovery energy', b => energyProfile(b, true));

profile('guidance', 'EPS method and activity prerequisites', b => {
  const a = b.analysis('eps_guidance', 'Method eligibility', ['FR-03', 'FR-26', 'FR-39']);
  a.check('The assessment shall establish its model prerequisites for $$operating_case_count$$ declared cases before execution.',
    [field('operating_case_count', '', 'integer', a.input('operating_case_count'))],
    `operating_case_count > 0 and ${a.ref('executable')} and ${a.ref('unmet_prerequisite_count')} == 0`, ['FR-03', 'FR-39']);
});

profile('converter', 'Converter command and startup response', b => {
  const a = b.analysis('eps_converter_step', 'Converter voltage step', ['FR-16', 'FR-19', 'EPS-04', 'EPS-06']);
  a.check('The converter shall reach its required supply interval within startup time $$startup_limit_s$$.',
    [field('startup_limit_s', 's')], `startup_limit_s >= 0 and ${a.ref('startup_reached')} and ${a.ref('startup_time_s')} <= startup_limit_s`, ['EPS-04', 'EPS-06']);
  a.check('The converter shall settle to its declared voltage error band within $$settling_limit_s$$.',
    [field('settling_limit_s', 's')], `settling_limit_s >= 0 and ${a.ref('settled')} and ${a.ref('settling_time_s')} <= settling_limit_s`, ['FR-16', 'FR-19']);
  a.check('The converter shall provide required voltage throughout at least $$required_service_s$$ after startup.',
    [field('required_service_s', 's')], `required_service_s > 0 and ${a.ref('service_duration_s')} >= required_service_s`, ['EPS-06']);
});

profile('charger', 'Charger operating bounds', b => {
  b.requirement({ text: 'The charger shall support battery series count $$battery_series_count$$ within its interval from $$series_min$$ to $$series_max$$.',
    fields: [field('battery_series_count', 'cells', 'integer'), field('series_min', 'cells', 'integer'), field('series_max', 'cells', 'integer')],
    condition: '0 < series_min <= battery_series_count <= series_max', reports: ['EPS-01', 'EPS-05'] });
  b.requirement({ text: 'The selected charge voltage $$charge_voltage_V$$ shall remain in the common battery and charger voltage interval.',
    fields: ['charge_voltage_V', 'battery_charge_min_V', 'battery_charge_max_V', 'charger_min_V', 'charger_max_V'].map(n => field(n, 'V')),
    condition: '0 < battery_charge_min_V <= charge_voltage_V <= battery_charge_max_V and 0 < charger_min_V <= charge_voltage_V <= charger_max_V', reports: ['EPS-05'] });
  b.requirement({ text: 'The selected charge current $$charge_current_A$$ shall remain within the battery limit $$battery_charge_limit_A$$ and charger limit $$charger_limit_A$$.',
    fields: ['charge_current_A', 'battery_charge_limit_A', 'charger_limit_A'].map(n => field(n, 'A')),
    condition: '0 <= charge_current_A <= battery_charge_limit_A and 0 <= charge_current_A <= charger_limit_A', reports: ['EPS-05', 'EPS-07'] });
  b.requirement({ text: 'The charge termination current $$termination_current_A$$ shall remain within the battery interval from $$termination_min_A$$ to $$termination_max_A$$.',
    fields: ['termination_current_A', 'termination_min_A', 'termination_max_A'].map(n => field(n, 'A')),
    condition: '0 <= termination_min_A <= termination_current_A <= termination_max_A', reports: ['EPS-05'] });
  b.requirement({ text: 'The charging temperature $$charge_temperature_C$$ shall remain between $$charge_min_C$$ and $$charge_max_C$$.',
    fields: ['charge_temperature_C', 'charge_min_C', 'charge_max_C'].map(n => field(n, 'degC')),
    condition: '-273.15 < charge_min_C <= charge_temperature_C <= charge_max_C', reports: ['EPS-05', 'EPS-13'] });
});

profile('interfaces', 'Service port electrical and timing bounds', b => {
  b.requirement({ text: 'The service port shall support required exchange rate $$required_rate_Hz$$ within capacity $$supported_rate_Hz$$.',
    fields: [field('required_rate_Hz', 'Hz'), field('supported_rate_Hz', 'Hz')],
    condition: '0 <= required_rate_Hz <= supported_rate_Hz', reports: ['EPS-18'] });
  b.requirement({ text: 'The service port response $$response_time_s$$ shall remain within bound $$response_limit_s$$.',
    fields: [field('response_time_s', 's'), field('response_limit_s', 's')],
    condition: '0 <= response_time_s <= response_limit_s', reports: ['EPS-18'] });
  b.requirement({ text: 'The transmitted logic levels $$output_low_max_V$$ and $$output_high_min_V$$ shall satisfy the receiver thresholds $$input_low_max_V$$ and $$input_high_min_V$$.',
    fields: ['output_low_max_V', 'output_high_min_V', 'input_low_max_V', 'input_high_min_V'].map(n => field(n, 'V')),
    condition: 'output_low_max_V < output_high_min_V and input_low_max_V < input_high_min_V and output_low_max_V <= input_low_max_V and output_high_min_V >= input_high_min_V', reports: ['EPS-18'] });
  b.requirement({ text: 'The service signal interval from $$signal_min_V$$ to $$signal_max_V$$ shall remain within the receiver operating interval from $$operating_min_V$$ to $$operating_max_V$$.',
    fields: ['signal_min_V', 'signal_max_V', 'operating_min_V', 'operating_max_V'].map(n => field(n, 'V')),
    condition: 'operating_min_V <= signal_min_V <= signal_max_V <= operating_max_V', reports: ['EPS-18'] });
});

profile('path', 'Converter rail and simultaneous pulse demand', b => {
  const a = b.analysis('eps_power_path', 'Power path', ['FR-14', 'FR-16', 'EPS-03', 'EPS-04', 'EPS-06', 'EPS-07']);
  a.check('The converter shall support rail voltage $$rail_voltage_V$$ at source voltage $$source_voltage_V$$ within its declared operating and startup envelope.',
    a.fields('rail_voltage_V', 'source_voltage_V'), `${a.ref('input_ok')} and ${a.ref('startup_ok')} and ${a.ref('envelope_ok')}`, ['EPS-03', 'EPS-04']);
  a.check('The load terminal voltage shall remain between $$load_min_V$$ and $$load_max_V$$ during steady and pulse demand.',
    a.fields('load_min_V', 'load_max_V'), `${a.ref('steady_voltage_ok')} and ${a.ref('pulse_voltage_ok')}`, ['EPS-06']);
  a.check('The path shall supply declared steady current $$steady_current_A$$ and pulse current $$pulse_current_A$$ within its battery, converter, switch and connection ratings.',
    a.fields('steady_current_A', 'pulse_current_A'), `${a.ref('battery_current_ok')} and ${a.ref('converter_current_ok')} and ${a.ref('switch_current_ok')} and ${a.ref('connection_current_ok')} and ${a.ref('pulse_duration_ok')}`, ['EPS-07']);
  a.check('The supplied converter startup bound shall remain within $$startup_limit_s$$.',
    a.fields('startup_limit_s'), `${a.ref('startup_time_ok')}`, ['EPS-04', 'EPS-06']);
  a.check('The converter and distribution path shall dissipate at most $$dissipation_limit_W$$ under steady and pulse demand.',
    [field('dissipation_limit_W', 'W')], `dissipation_limit_W >= 0 and max(${a.ref('steady_converter_loss_W')} + ${a.ref('steady_path_loss_W')}, ${a.ref('pulse_converter_loss_W')} + ${a.ref('pulse_path_loss_W')}) <= dissipation_limit_W`, ['FR-16', 'EPS-13']);
});

profile('protection', 'Protection fault and recovery MIL', b => {
  const a = b.analysis('eps_protection', 'Protection scenario', ['FR-16', 'FR-19', 'EPS-15', 'EPS-16', 'EPS-17']);
  a.check('The EPS shall interrupt the declared fault within $$interruption_limit_s$$ without reenergizing the persisting fault.',
    a.fields('interruption_limit_s'), `${a.ref('fault_seen')} and ${a.ref('protection_active')} and ${a.ref('protection_ok')}`, ['EPS-15', 'EPS-16']);
  a.check('The protected path shall remain within fault stress limits $$i2t_limit_A2s$$ and $$peak_limit_A$$.',
    a.fields('i2t_limit_A2s', 'peak_limit_A'), `${a.ref('stress_ok')}`, ['EPS-15']);
  a.check('The EPS shall supply legitimate nominal current $$legitimate_current_A$$ throughout $$nominal_duration_s$$ without nuisance trips.',
    a.fields('legitimate_current_A', 'nominal_duration_s'), `${a.input('nominal_duration_s')} > 0 and ${a.ref('nuisance_free')}`, ['EPS-15']);
  a.check('The EPS shall keep any asserted inhibit effective throughout the fault interval $$fault_duration_s$$.',
    a.fields('fault_duration_s'), `${a.ref('inhibited_outputs_off')}`, ['EPS-17']);
  a.check('The protected output shall recover within $$recovery_limit_s$$ after the declared fault clears.',
    [field('recovery_limit_s', 's')], `recovery_limit_s >= 0 and ${a.input('recovery_duration_s')} > 0 and ${a.ref('recovery_observed')} and ${a.ref('recovery_time_s')} <= recovery_limit_s`, ['EPS-16']);
});

function batteryAssessment(b) {
  const a = b.analysis('eps_battery_step', 'Battery circuit step', ['FR-16', 'EPS-06', 'EPS-08', 'EPS-10']);
  a.check('The battery terminal voltage shall remain between $$voltage_min_V$$ and $$voltage_max_V$$ throughout the circuit step.',
    a.fields('voltage_min_V', 'voltage_max_V'), `${a.ref('voltage_ok')}`, ['EPS-06']);
  a.check('The battery charge state shall remain between $$soc_min$$ and $$soc_max$$ throughout the circuit step.',
    a.fields('soc_min', 'soc_max'), `${a.ref('physical_soc_ok')} and ${a.ref('soc_ok')}`, ['EPS-10']);
  a.check('The battery resistors shall dissipate at most $$battery_loss_limit_W$$ throughout the circuit step.',
    [field('battery_loss_limit_W', 'W')], `battery_loss_limit_W >= 0 and ${a.ref('max_loss_W')} <= battery_loss_limit_W`, ['FR-16', 'EPS-13']);
  return a;
}
profile('battery', 'Battery voltage and charge state response', batteryAssessment);
profile('thermal', 'Component and charging temperature response', b => {
  const a = b.analysis('eps_thermal', 'Thermal interval', ['FR-16', 'EPS-13', 'EPS-14']);
  a.check('The component node shall remain between $$temp_min_K$$ and $$temp_max_K$$ throughout the thermal interval.',
    a.fields('temp_min_K', 'temp_max_K'), `${a.ref('temp_ok')}`, ['EPS-13']);
  a.check('Any active charging shall respect its temperature interval from $$charge_min_K$$ to $$charge_max_K$$.',
    a.fields('charge_min_K', 'charge_max_K'), `${a.ref('charge_ok')}`, ['EPS-05', 'EPS-13']);
});
profile('electrothermal', 'Battery electrical and thermal bounds', b => {
  const battery = batteryAssessment(b);
  const upper = b.analysis('eps_thermal', 'Battery hot bound', ['FR-16', 'EPS-13']);
  const lower = b.analysis('eps_thermal', 'Battery cold bound', ['FR-16', 'EPS-13']);
  upper.set('dissipation_W', battery.ref('max_loss_W'));
  lower.set('dissipation_W', battery.ref('min_loss_W'));
  upper.set('duration_s', battery.input('duration_s'));
  lower.set('duration_s', battery.input('duration_s'));
  for (const name of ['initial_temp_K', 'ambient_temp_K', 'heater_W', 'heat_capacity_J_K', 'conductance_W_K', 'temp_min_K', 'temp_max_K', 'charge_min_K', 'charge_max_K']) {
    lower.set(name, upper.input(name));
  }
  for (const a of [upper, lower]) {
    // Charging is derived from the circuit's declared charge-positive current.
    a.set('charge_active', `${battery.input('current_A')} > 0`);
    a.check('The battery thermal bound shall remain within node limits from $$temp_min_K$$ to $$temp_max_K$$.',
      a.fields('temp_min_K', 'temp_max_K'), `${a.ref('temp_ok')}`, ['EPS-13']);
    a.check('Any charging shall remain within the declared node interval from $$charge_min_K$$ to $$charge_max_K$$.',
      a.fields('charge_min_K', 'charge_max_K'), `${a.ref('charge_ok')}`, ['EPS-05', 'EPS-13']);
  }
});

profile('sizing', 'Integer assembly sizing and packing', b => {
  const a = b.analysis('eps_sizing', 'Assembly sizing', ['FR-14', 'FR-17', 'FR-20', 'EPS-01', 'EPS-02', 'EPS-08', 'EPS-20']);
  a.check('The configured array with $$pv_series$$ series cells and $$pv_parallel$$ parallel strings shall meet its preliminary EOL generation bound.',
    a.fields('pv_series', 'pv_parallel'), `${a.ref('generation_margin_W')} >= 0`, ['EPS-02']);
  a.check('The array active area shall fit usable face area $$usable_face_area_m2$$ at packing fraction $$packing_fraction$$.',
    a.fields('usable_face_area_m2', 'packing_fraction'), `${a.ref('packing_margin_m2')} >= 0`, ['EPS-20']);
  a.check('The configured battery with $$bat_series$$ series cells and $$bat_parallel$$ parallel strings shall meet its preliminary BOL energy bound.',
    a.fields('bat_series', 'bat_parallel'), `${a.ref('bol_energy_margin_Wh')} >= 0`, ['EPS-08']);
  a.check('The configured battery shall meet its retained energy bound at retention factor $$energy_retained_factor$$.',
    a.fields('energy_retained_factor'), `${a.ref('retained_energy_margin_Wh')} >= 0`, ['EPS-08']);
  a.check('The configured battery shall retain charge capacity of at least $$required_retained_charge_Ah$$.',
    a.fields('required_retained_charge_Ah'), `${a.ref('retained_charge_margin_Ah')} >= 0`, ['EPS-08']);
  a.check('The selected source operating interval from $$source_low_V$$ to $$source_high_V$$ shall satisfy the declared receiver and ideal conversion voltage screens.',
    a.fields('source_low_V', 'source_high_V'), `${a.ref('voltage_screen_ok')}`, ['EPS-03', 'EPS-04']);
});
profile('geometry', 'Installation envelope accommodation', b => {
  const a = b.analysis('eps_geometry', 'Installation envelope', ['EPS-20']);
  a.check('The declared component envelope shall fit its installation box within contact tolerance $$tolerance_m$$.',
    a.fields('tolerance_m'), `${a.ref('contained')}`, ['EPS-20']);
  a.check('The declared component envelope shall clear its keep-out under contact tolerance $$tolerance_m$$ and the selected touching policy.',
    a.fields('tolerance_m'), `${a.ref('keepout_clear')}`, ['EPS-20']);
});
profile('fit', 'Supplied-data parameter estimation', b => {
  const a = b.analysis('eps_fit', 'Parameter fit', ['FR-22']);
  a.check('The parameter fit shall reproduce accepted supplied samples within RMS error $$rmse_limit$$ and maximum error $$max_error_limit$$.',
    a.fields('rmse_limit', 'max_error_limit'), `${a.ref('fit_quality_ok')}`, ['FR-22']);
  a.check('The estimated parameters for declared model $$model_kind$$ shall satisfy that model\'s physical parameter bounds.',
    a.fields('model_kind'), `${a.ref('physical_model_ok')}`, ['FR-22']);
});
profile('ram', 'Authored fault tree and reliability', b => {
  const a = b.analysis('eps_ram', 'Fault tree', ['FR-27']);
  a.check('The declared top failure probability shall remain at most $$failure_probability_limit$$ over the supplied exposure.',
    [field('failure_probability_limit')], `0 <= failure_probability_limit <= 1 and ${a.ref('top_failure_probability')} <= failure_probability_limit`, ['FR-27']);
  a.check('The declared mission service shall retain reliability of at least $$reliability_min$$ over the supplied exposure.',
    [field('reliability_min')], `0 <= reliability_min <= 1 and ${a.ref('mission_reliability')} >= reliability_min`, ['FR-27']);
  a.check('The conditional top failure probability shall remain at most $$conditional_probability_limit$$ for the declared failure evidence.',
    [field('conditional_probability_limit')], `0 <= conditional_probability_limit <= 1 and ${a.ref('conditional_failure_probability')} <= conditional_probability_limit`, ['FR-27']);
});

profile('cots-protection', 'TPS63802 sourced protection bounds', b => {
  const component = b.component('ti_tps63802dlar', [
    ['ovp_available', { name: 'autonomous_overvoltage_protection', element: 'self' }],
    ['output_ovp_max_V', { name: 'overvoltage_threshold', element: 'output_supply', valueKind: 'maximum' }],
    ['output_ovp_action', { name: 'overvoltage_action', element: 'output_supply' }],
    ['uvlo_available', { name: 'autonomous_undervoltage_protection', element: 'self' }],
    ['uvlo_falling_min_V', { name: 'undervoltage_threshold', element: 'self', valueKind: 'minimum' }],
    ['uvlo_rising_max_V', { name: 'undervoltage_release', element: 'self', valueKind: 'maximum' }],
    ['startup_min_V', { name: 'startup_input_voltage_min', element: 'self' }],
    ['operating_min_K', { name: 'operating_temperature_min', element: 'self' }],
    ['operating_max_K', { name: 'operating_temperature_max', element: 'self' }],
  ]);
  const ref = name => `${component.id}.${name}`;
  const extra = 'This selects TPS63802 controller evidence, not a complete circuit or battery protector. '
    + 'OVP and UVLO thresholds retain tolerance endpoints and their separate operating conditions. '
    + 'The engineer must supply actual circuitry, operating cases, external-component ratings and independent limits.';
  const add = (text, fields, condition, reports) => b.requirement({ text, fields, condition, reports, component, extra });
  add('The converter output OVP threshold shall remain at most $$ovp_trip_ceiling_V$$.',
    [field('ovp_trip_ceiling_V', 'V')],
    `ovp_trip_ceiling_V > 0 and ${ref('ovp_available')} and ${ref('output_ovp_action')} == "output_OVP_stops_switching" and ${ref('output_ovp_max_V')} <= ovp_trip_ceiling_V`, ['EPS-15']);
  add('The converter UVLO falling threshold shall remain at least $$uvlo_trip_floor_V$$ under its declared once-started condition.',
    [field('uvlo_trip_floor_V', 'V')],
    `uvlo_trip_floor_V > 0 and ${ref('uvlo_available')} and ${ref('uvlo_falling_min_V')} >= uvlo_trip_floor_V`, ['EPS-04']);
  add('The startup source voltage $$startup_source_V$$ shall support the converter UVLO release and minimum startup input voltage.',
    [field('startup_source_V', 'V')],
    `startup_source_V >= ${ref('uvlo_rising_max_V')} and startup_source_V >= ${ref('startup_min_V')}`, ['EPS-04']);
  add('The converter junction temperature $$junction_temperature_K$$ shall remain within its recommended operating interval.',
    [field('junction_temperature_K', 'K')],
    `${ref('operating_min_K')} <= junction_temperature_K <= ${ref('operating_max_K')}`, ['EPS-13']);
}, ['ti_tps63802dlar']);

export function reportProfiles() { return [...profiles.values()].map(({ id, name, products }) => ({ id, name, products: [...products] })); }
export function createReportWorkspace(catalog, definitions, id, { cotsFacts = {} } = {}) {
  const selected = profiles.get(id);
  if (!selected) throw new Error(`Choose a report assessment: ${reportProfiles().map(item => item.id).join(', ')}.`);
  const b = builder(catalog, definitions, selected.name, cotsFacts);
  selected.configure(b);
  return b.finish();
}
