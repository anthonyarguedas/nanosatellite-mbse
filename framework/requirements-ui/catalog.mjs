import { readFile } from 'node:fs/promises';
import { domainTypes, requirementMarkers, validVariableName } from './model.mjs';

// Index package and part definition scopes. This is a structural index for the
// generic model, not a replacement for SysML parsing or validation.
export function indexDefinitions(source) {
  const tokens = source.match(/\/\*[\s\S]*?\*\/|\/\/[^\r\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[A-Za-z_][A-Za-z0-9_]*|[{};]/g)?.filter(token => !/^(?:\/\/|\/\*|"|')/.test(token)) ?? [];
  const scopes = [], definitions = [];
  const path = () => scopes.filter(Boolean).join('::');
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    const isPackage = token === 'package';
    const isPart = token === 'part' && tokens[i + 1] === 'def';
    if (isPackage || isPart) {
      const name = tokens[i + (isPart ? 2 : 1)];
      if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name ?? '')) continue;
      const parent = path();
      if (isPart) definitions.push({ name, model: parent ? `${parent}::${name}` : name, parent });
      i += isPart ? 3 : 2;
      while (i < tokens.length && !['{', ';'].includes(tokens[i])) i++;
      if (tokens[i] === '{') scopes.push(name);
    } else if (token === '{') scopes.push(null);
    else if (token === '}') scopes.pop();
  }
  return definitions;
}

const labels = name => name.replace(/Subsystem$/, '').replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/([A-Z])([A-Z][a-z])/g, '$1 $2').replace(/\bAnd\b/g, 'and').replace(/\bOf\b/g, 'of');
const abbreviations = {
  CommandAndDataHandlingSubsystem: 'CDH', CommunicationSubsystem: 'COM',
  AttitudeDeterminationAndControlSubsystem: 'ADC', GuidanceNavigationAndControlSubsystem: 'GNC',
  StructuresAndMechanismsSubsystem: 'STR', ThermalSubsystem: 'THE', PropulsionSubsystem: 'PRO', PowerSubsystem: 'EPS',
  Instrument: 'INS', ProcessorAndMemory: 'PCM', Batteries: 'BAT', SolarArrays: 'SOL',
  RegulatorsAndConverters: 'REG', PowerCircuitsAndSwitches: 'PCS', Software: 'SFW', PlanAndScheduleSubsystem: 'PLS',
  SpacecraftCommandSubsystem: 'SCC', GroundEquipmentControlSubsystem: 'GEC', SpaceGroundCommunicationSubsystem: 'SGC',
  MissionDataProcessingSubsystem: 'MDP', MissionDataDisseminationSubsystem: 'MDD', NetworkSubsystem: 'NET', TelemetryProcessingSubsystem: 'TLM',
};

// Annotations belong to native generic requirement definitions. They carry the
// table projection only. The SysML constraints remain the normative model.
export function requirementsFromSource(source) {
  const requirements = [];
  const pattern = /requirement def ([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*doc\s*\/\*\s*@requirements-ui\s+([\s\S]*?)\*\//g;
  for (const match of source.matchAll(pattern)) {
    const template = JSON.parse(match[2]);
    if (!['mission', 'eps'].includes(template.context) || !/^[A-Z]{3}\d{3}$/.test(template.id)
        || !template.parameters || Object.hasOwn(template, 'formulas')
        || Object.values(template.parameters).some(value => value !== null && typeof value !== 'string')
        || typeof template.text !== 'string' || typeof template.condition !== 'string'
        || requirements.some(row => row.id === template.id)) throw new Error(`Invalid generic requirement ${match[1]}.`);
    if (!Object.keys(template.parameters).length) throw new Error(`${match[1]}: declare at least one numeric parameter.`);
    const markers = requirementMarkers(template.text);
    if (!markers.names.length || markers.errors.length || markers.names.some(name => !Object.hasOwn(template.parameters, name))) {
      throw new Error(`${match[1]}: each $$variable$$ must name a declared table parameter.`);
    }
    const body = source.slice(match.index + match[0].length).split(/\brequirement def\b/, 1)[0];
    const attributes = Object.fromEntries([...body.matchAll(/\battribute\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(Real|Integer|Boolean)\[0\.\.1\]/g)].map(item => [item[1], item[2]]));
    if (Object.keys(template.parameters).some(name => !validVariableName(name) || !attributes[name])) throw new Error(`${match[1]}: a table parameter has no valid native SysML attribute.`);
    if (Object.keys(template.parameters).some(name => attributes[name] !== (template.integers?.includes(name) ? 'Integer' : 'Real'))) {
      throw new Error(`${match[1]}: table parameter types must match native SysML attributes.`);
    }
    requirements.push({ ...template, attributes, name: match[1], model: `FrameworkRequirements::${match[1]}` });
  }
  if (!requirements.length) throw new Error('The generic model has no requirements-ui definitions.');
  const names = new Set(requirements.map(template => template.name));
  for (const template of requirements) {
    if (!Array.isArray(template.derivesFrom ?? []) || template.derivesFrom?.some(name => !names.has(name) || name === template.name)) {
      throw new Error(`${template.name}: derivation sources must name other generic requirements.`);
    }
  }
  return requirements;
}

export function catalogFromSource(source, requirements = []) {
  const definitions = indexDefinitions(source);
  for (const domain of domainTypes) {
    if (!definitions.some(definition => definition.model === domain.model)) throw new Error(`The generic mission model is missing ${domain.model}.`);
  }
  const catalog = domainTypes.map(domain => ({ ...domain }));
  for (const domain of catalog) {
    if (!domain.expandable) continue;
    const components = domain.role === 'eps';
    const parent = domain.role === 'ground' ? 'GroundSegment' : domain.model;
    const children = definitions.filter(definition => definition.parent === parent
      && (components || domain.role === 'payload' || (definition.name.endsWith('Subsystem') && definition.name !== 'PayloadSubsystem')));
    for (const definition of children) catalog.push({
      model: definition.model, parent: domain.model, name: labels(definition.name),
      category: components ? 'Component' : domain.role === 'payload' ? 'Element' : 'Subsystem', expandable: false,
      id: abbreviations[definition.name] ?? definition.name.slice(0, 3).toUpperCase(),
      ...(definition.model === 'SpaceSegment::CubeSat::PowerSubsystem'
        ? { expandable: true, role: 'eps', prefix: 'EPS', tabLabel: 'EPS' } : {}),
    });
  }
  for (const type of catalog) {
    const templates = requirements.filter(row => row.context === (type.role === 'orbit' ? 'mission' : type.role === 'eps' ? 'eps' : null));
    if (templates.length) type.requirements = templates;
  }
  return catalog;
}

export async function loadCatalog(path = new URL('../mission.sysml', import.meta.url)) {
  const [source, requirements] = await Promise.all([readFile(path, 'utf8'), readFile(new URL('../requirements.sysml', import.meta.url), 'utf8')]);
  return catalogFromSource(source, requirementsFromSource(requirements));
}
