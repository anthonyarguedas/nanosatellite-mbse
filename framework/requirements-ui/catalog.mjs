import { readFile } from 'node:fs/promises';
import { domainTypes } from './model.mjs';

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
  Instrument: 'INS', ProcessorAndMemory: 'PCM', PlanAndScheduleSubsystem: 'PLS',
  SpacecraftCommandSubsystem: 'SCC', GroundEquipmentControlSubsystem: 'GEC', SpaceGroundCommunicationSubsystem: 'SGC',
  MissionDataProcessingSubsystem: 'MDP', MissionDataDisseminationSubsystem: 'MDD', NetworkSubsystem: 'NET', TelemetryProcessingSubsystem: 'TLM',
};

export function catalogFromSource(source) {
  const definitions = indexDefinitions(source);
  for (const domain of domainTypes) {
    if (!definitions.some(definition => definition.model === domain.model)) throw new Error(`The generic mission model is missing ${domain.model}.`);
  }
  const catalog = domainTypes.map(domain => ({ ...domain }));
  for (const domain of domainTypes.filter(domain => domain.expandable)) {
    const parent = domain.role === 'ground' ? 'GroundSegment' : domain.model;
    const children = definitions.filter(definition => definition.parent === parent
      && (domain.role === 'payload' || (definition.name.endsWith('Subsystem') && definition.name !== 'PayloadSubsystem')));
    for (const definition of children) catalog.push({
      model: definition.model, parent: domain.model, name: labels(definition.name),
      category: domain.role === 'payload' ? 'Element' : 'Subsystem', expandable: false,
      id: abbreviations[definition.name] ?? definition.name.slice(0, 3).toUpperCase(),
    });
  }
  return catalog;
}

export async function loadCatalog(path = new URL('../mission.sysml', import.meta.url)) {
  return catalogFromSource(await readFile(path, 'utf8'));
}
