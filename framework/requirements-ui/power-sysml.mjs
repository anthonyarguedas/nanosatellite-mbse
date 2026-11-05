import { allocationChildren, allocationComponents, inRoots, powerFor, powerLimitFor, powerScopes, spacecraftComponents } from './power.mjs';

export const powerBudgetName = eps => `power_budget_${eps.replace(/[-_]/g, char => char === '-' ? '_h' : '_u')}`;
const modeName = key => `spacecraft_mode_${key.replace(/[-_]/g, char => char === '-' ? '_h' : '_u')}`;
const drawName = key => `mode_draw_${key.replace(/[-_]/g, char => char === '-' ? '_h' : '_u')}`;

export function renderPowerDraws(workspace, row, path, indent) {
  const load = powerFor(workspace, row), lines = [];
  if (row.definition.endsWith('::Software')) {
    if (load.host) lines.push(`${indent}ref part executionHost : EPSModel::ProcessorMemory = ${path(load.host)};`);
    return lines;
  }
  lines.push(`${indent}attribute power_accounting : String = ${JSON.stringify(load.accounting)};`);
  if (load.rationale) lines.push(`${indent}attribute power_accounting_rationale : String = ${JSON.stringify(load.rationale)};`);
  for (const state of load.states) {
    const subset = /::(?:StaticMount|ThermalSink|PropellantStorage)$/.test(row.definition) ? '' : ' :> load_profiles';
    lines.push(`${indent}attribute ${drawName(state.key)} : PowerBudgetModel::ModeDraw${subset} {`,
      `${indent}    :>> profile_id = ${JSON.stringify(`${row.key}:${state.key}`)};`,
      `${indent}    :>> mode_id = ${JSON.stringify(state.key)};`,
      `${indent}    :>> display_name = ${JSON.stringify(state.name)};`,
      `${indent}    :>> basis = PowerBudgetModel::ValueBasis::${state.basis};`,
      `${indent}    :>> source_note = ${JSON.stringify(state.source)};`,
      `${indent}    :>> conditions = ${JSON.stringify(state.conditions)};`,
      ...(state.watts === null ? [] : [`${indent}    :>> watts = ${state.watts};`]), `${indent}}`);
  }
  return lines;
}

export function renderPowerLimit(workspace, row, partPath, requirementPath, modeNamespace = '') {
  const activeMode = `${modeNamespace}spacecraft_mode`;
  const lines = [`        attribute :>> mode = ${activeMode};`];
  const scope = powerScopes(workspace).find(scope => scope.key === row.powerScope);
  const targets = row.powerScope === 'mission' ? scope.affected : [row.powerScope];
  if (targets.length) lines.push(`        ref part :>> power_scope = (${targets.map(partPath).join(', ')});`);
  const missing = label => {
    const name = `${label}_${lines.length}`;
    lines.push(`        attribute ${name} : ScalarValues::Real[0..1];`);
    return name;
  };
  const components = allocationComponents(workspace, row.powerScope);
  const children = allocationChildren(workspace, row.powerScope);
  let draw;
  if (children.length) {
    draw = `(${children.map(child => {
      const limit = powerLimitFor(workspace, child.key);
      return limit ? `${requirementPath(limit.key)}.'draw_power_W'` : missing('unmodeled_draw');
    }).join(' + ')})`;
  } else {
    const cases = workspace.power.modes.map(mode => {
      const terms = components.filter(element => powerFor(workspace, element).accounting === 'counted').map(element => {
        const load = powerFor(workspace, element);
        const state = load.states.find(state => state.key === load.assignments[mode.key]);
        return state ? `(${load.quantity} * ${partPath(element.key)}.${drawName(state.key)}.watts)` : missing('unmodeled_draw');
      });
      return { mode, value: `(${terms.join(' + ') || '0'})` };
    });
    draw = cases.reduceRight((rest, { mode, value }) => `(if ${activeMode} == ${modeNamespace}${modeName(mode.key)} ? ${value} else ${rest})`, 'null');
  }
  const allocated = children.map(child => {
    const limit = powerLimitFor(workspace, child.key);
    return limit ? `${requirementPath(limit.key)}.'power_limit_W'` : missing('unallocated_power');
  });
  return { lines, draw_power_W: components.length ? draw : missing('unmodeled_draw'),
    allocated_power_W: `(${allocated.join(' + ') || '0'})` };
}

export function renderPowerBudgets(workspace, path) {
  const lines = [], power = workspace.power;
  if (power.modes.length || workspace.statements.some(row => row.powerScope)) lines.push('    attribute spacecraft_mode : PowerBudgetModel::SpacecraftMode[0..1];');
  for (const mode of power.modes) {
    lines.push(`    attribute ${modeName(mode.key)} : PowerBudgetModel::SpacecraftMode {`,
      `        :>> mode_id = ${JSON.stringify(mode.key)};`, `        :>> display_name = ${JSON.stringify(mode.name)};`,
      ...['sunlight', 'eclipse'].filter(period => mode[period] !== null).map(period => `        :>> ${period}_fraction = ${mode[period]} / 100;`), '    }');
  }
  for (const link of power.links) {
    const components = spacecraftComponents(workspace).filter(row => inRoots(workspace, row, link.roots));
    lines.push(`    part ${powerBudgetName(link.eps)} : PowerBudgetModel::IlluminationBudget {`);
    if (power.modes.length) lines.push(`        attribute :>> modes = (${power.modes.map(mode => modeName(mode.key)).join(', ')});`);
    const terms = { sunlight: [], eclipse: [] };
    let number = 0;
    for (const element of components) {
      const load = powerFor(workspace, element);
      if (load.accounting !== 'counted') continue;
      for (const mode of power.modes) {
        const name = `contribution_${++number}`;
        const state = load.states.find(state => state.key === load.assignments[mode.key]);
        lines.push(`        part ${name} : PowerBudgetModel::ModeContribution {`,
          `            ref part :>> physical_load = ${path(element.key)};`,
          `            attribute :>> mode = ${modeName(mode.key)};`, `            attribute :>> quantity = ${load.quantity};`,
          ...(state ? [`            attribute :>> profile = ${path(element.key)}.${drawName(state.key)};`] : []), '        }');
        for (const period of ['sunlight', 'eclipse']) if (mode[period] !== 0) terms[period].push(`${name}.${period}_power_W`);
      }
    }
    if (power.modes.length && components.length) for (const period of ['sunlight', 'eclipse']) {
      const normalized = `RealFunctions::abs((${power.modes.map(mode => `${modeName(mode.key)}.${period}_fraction`).join(' + ')}) - 1) <= 1e-8`;
      lines.push(`        attribute :>> ${period}_power_W = if ${normalized} ? ${terms[period].join(' + ') || '0'} else null;`,
        `        assert constraint ${period}Fractions { ${normalized} }`);
    }
    lines.push('    }');
    for (const root of link.roots) lines.push(`    dependency from ${powerBudgetName(link.eps)} to ${path(root).replaceAll('.', '::')};`);
  }
  return lines;
}
