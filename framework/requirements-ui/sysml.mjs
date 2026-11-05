import { createHash, randomUUID } from 'node:crypto';
import { mkdir, readFile, rename, stat, unlink, writeFile } from 'node:fs/promises';
import { basename, dirname } from 'node:path';
import { domainTypes, emptyWorkspace, migrateWorkspace, stakeholderTypes, tabsFor, validateWorkspace } from './model.mjs';
import { createEvaluator, expressionType, parseExpression, printExpression, validateReferences } from './verification.mjs';
import { isPowerRequirement, powerLimitFor, powerRequirementTemplates, spacecraftComponents } from './power.mjs';
import { powerBudgetName, renderPowerBudgets, renderPowerDraws, renderPowerLimit } from './power-sysml.mjs';

const begin = '// <requirements-ui>';
const end = '// </requirements-ui>';
const dataBegin = '/* requirements-ui:data\n';
const dataEnd = '\nrequirements-ui:end-data */';
const revisionOf = source => createHash('sha256').update(source).digest('hex');
const identifier = (table, key) => `${table === 'stakeholders' ? 'stakeholder' : table === 'elements' ? 'element' : table === 'components' ? 'component' : 'statement'}_${key.replace(/[-_]/g, char => char === '-' ? '_h' : '_u')}`;
const literal = value => JSON.stringify(value);

function managedRange(source) {
  const starts = [...source.matchAll(/^\/\/ <requirements-ui>\r?$/gm)];
  const ends = [...source.matchAll(/^\/\/ <\/requirements-ui>\r?$/gm)];
  if (!starts.length && !ends.length) return null;
  if (starts.length !== 1 || ends.length !== 1 || starts[0].index >= ends[0].index) throw new Error('The requirements-ui section is incomplete or duplicated.');
  return [starts[0].index, ends[0].index + end.length];
}

export function readWorkspace(source, catalog = domainTypes, products = null) {
  const range = managedRange(source);
  if (!range) return emptyWorkspace(catalog);
  const block = source.slice(...range).replaceAll('\r\n', '\n');
  const start = block.indexOf(dataBegin), finish = block.indexOf(dataEnd);
  if (start === -1 || finish === -1) throw new Error('The requirements-ui data is missing.');
  return validateWorkspace(migrateWorkspace(JSON.parse(block.slice(start + dataBegin.length, finish)), catalog), catalog, products);
}

export function renderManaged(workspace, { packageName = 'MissionRequirements', catalog = domainTypes, products = null, includeData = true, strict = false } = {}) {
  validateWorkspace(workspace, catalog, products);
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(packageName)) throw new Error('Invalid mission package name.');
  const metadata = JSON.stringify(workspace, null, 2).replaceAll('*/', '\\u002a/');
  const lines = [
    ...(includeData ? [begin,
      '// Mission data managed by requirements-ui. Generic definitions are imported.',
      '// The JSON preserves UI data. The SysML elements below are generated from it.',
      dataBegin + metadata + dataEnd] : ['// Mission-specific export. Load with the generic framework/*.sysml libraries.']),
    `package ${packageName} {`,
    '    private import External::*;',
    '    private import Orbit;',
    '    private import SpaceSegment::*;',
    '    private import GroundSegment::*;',
    '    private import ScalarValues::*;',
  ];
  const names = new Map(), namesById = new Map();
  for (const [table, rows] of [['stakeholders', workspace.stakeholders], ['statements', workspace.statements]]) {
    for (const row of rows) {
      names.set(row.key, identifier(table, row.key));
      namesById.set(row.id, identifier(table, row.key));
    }
  }
  const elements = new Map(workspace.elements.map(row => [row.key, row]));
  const elementNames = new Map(workspace.elements.map(row => [row.key, identifier('elements', row.key)]));
  const elementPath = row => {
    if (names.has(row.key)) return names.get(row.key);
    const name = row.owner === 'mission' ? elementNames.get(row.key) : `${elementPath(elements.get(row.owner))}::${elementNames.get(row.key)}`;
    names.set(row.key, name);
    namesById.set(row.id, name);
    return name;
  };
  workspace.elements.forEach(elementPath);
  const templates = new Map([...catalog.flatMap(type => type.requirements ?? []), ...powerRequirementTemplates].map(template => [template.model, template]));
  const evaluators = (workspace.power.modes.length ? workspace.power.modes : [{ key: null }]).map(mode => createEvaluator(workspace, { mode: mode.key }));
  const checkResolved = evaluate => {
    try { evaluate(); }
    catch (error) { if (!error.pending) throw error; }
  };
  const productsById = new Map((products ?? []).map(product => [product.id, product]));
  for (const row of workspace.components) names.set(row.key, `${names.get(row.owner)}::${identifier('components', row.key)}`);
  const partExpression = key => names.get(key).replaceAll('::', '.');
  const contexts = new Map(tabsFor(workspace, catalog).map(tab => [tab.key, tab.label]));
  for (const row of workspace.stakeholders) {
    const type = stakeholderTypes.find(type => type.name === row.type);
    lines.push(`    part ${names.get(row.key)} : ${type.model} {`,
      `        attribute externalId : String = ${literal(row.id)};`,
      `        attribute displayName : String = ${literal(row.name)};`, '    }');
  }
  const powerElements = new Set(spacecraftComponents(workspace).map(row => row.key));
  const emitElement = (row, indent) => {
    lines.push(`${indent}part ${elementNames.get(row.key)} : ${row.definition} {`,
      `${indent}    attribute externalId : String = ${literal(row.id)};`,
      `${indent}    attribute displayName : String = ${literal(row.name)};`);
    if (row.definition === 'Orbit') {
      const period = workspace.statements.find(statement => statement.definition === 'FrameworkRequirements::OrbitPeriod' && statement.affected.includes(row.key));
      if (period) for (const name of ['altitude_km', 'earthRadius_km', 'gravitationalParameter_km3_s2']) {
        lines.push(`${indent}    attribute :>> ${name} = ${names.get(period.key)}.'${name}';`);
      }
    }
    const consumption = powerLimitFor(workspace, row.key);
    if (consumption) lines.push(`${indent}    attribute :>> power_consumption_W = ${names.get(consumption.key)}.'draw_power_W';`);
    if (powerElements.has(row.key)) lines.push(...renderPowerDraws(workspace, row, partExpression, indent + '    '));
    for (const child of workspace.elements.filter(child => child.owner === row.key)) emitElement(child, indent + '    ');
    for (const component of workspace.components.filter(component => component.owner === row.key)) {
      lines.push(`${indent}    part ${identifier('components', component.key)} : ${productsById.get(component.product)?.model ?? 'EPSModel::HardwareComponent'} {`,
        `${indent}        attribute externalId : String = ${literal(component.id)};`,
        `${indent}        attribute :>> catalog_product_id = ${literal(component.product)};`,
        `${indent}        attribute :>> physical_resource_id = ${literal(component.key)};`, `${indent}    }`);
    }
    lines.push(`${indent}}`);
  };
  for (const row of workspace.elements.filter(row => row.owner === 'mission')) emitElement(row, '    ');
  lines.push(...renderPowerBudgets(workspace, partExpression));
  for (const row of workspace.statements) {
    const allocation = isPowerRequirement(row) ? renderPowerLimit(workspace, row, partExpression, key => names.get(key), `${packageName}::`) : null;
    const reference = (id, name) => {
      if (id === 'PowerAllocation') {
        if (!allocation) throw new Error('PowerAllocation belongs to a power limit requirement.');
        return allocation[name];
      }
      if (id !== 'LoadBudget') return `${namesById.get(id)}.'${name}'`;
      if (!workspace.power.links.some(link => link.eps === row.context)) throw new Error('Connect this EPS to a load budget before using LoadBudget inputs.');
      return `${powerBudgetName(row.context)}.'${name}'`;
    };
    const keyword = row.kind === 'Requirement' ? 'requirement' : 'attribute';
    const conditional = Boolean(row.condition.trim());
    lines.push(`    ${keyword} ${names.get(row.key)}${row.definition ? ` : ${row.definition}` : ''} {`,
      `        attribute externalId : String = ${literal(row.id)};`,
      `        attribute tableName : String = ${literal(contexts.get(row.context))};`,
      `        attribute statementKind : String = ${literal(row.kind)};`,
      `        attribute statementText : String = ${literal(row.text)};`,
      `        attribute verificationExpression : String[0..1]${conditional ? ` = ${literal(row.condition)}` : ''};`);
    if (allocation) lines.push(...allocation.lines);
    if (row.origin) lines.push(`        attribute sourceReference : String = ${literal(row.origin)};`);
    if (row.rationale) lines.push(`        attribute rationale : String = ${literal(row.rationale)};`);
    for (const variable of workspace.variables) {
      const source = row.parameters[variable.name];
      const populated = source !== null && Boolean(source.trim());
      const inherited = Object.hasOwn(templates.get(row.definition)?.attributes ?? {}, variable.name);
      if (row.definition && !inherited && !populated) continue;
      let binding = '';
      if (populated) {
        try {
          const ast = validateReferences(parseExpression(source), workspace);
          if (!['number', 'null'].includes(expressionType(ast))) throw new Error('A parameter expression must produce a number.');
          for (const evaluator of evaluators) checkResolved(() => evaluator.parameter(row, variable.name));
          const expression = printExpression(ast, reference, `${packageName}::spacecraft_mode.display_name`);
          if (variable.type === 'integer' && ast.kind !== 'literal') {
            // Integer cells accept equations involving Real values. The native
            // binding retains an integrality predicate, so conversion cannot
            // silently round a fractional result when inputs become available.
            binding = ` = RealFunctions::ToInteger(${expression})`;
            lines.push(`        assert constraint { ${expression} == RealFunctions::ToInteger(${expression}) }`);
          } else binding = ` = ${expression}`;
        } catch (error) {
          if (strict) throw new Error(`${row.id}.${variable.name}: ${error.message}`);
          lines.push(`        doc /* Invalid parameter expression for ${variable.name}. See the stored UI data. */`);
        }
      }
      if (inherited) {
        if (binding) lines.push(`        attribute :>> '${variable.name}'${binding};`);
      } else lines.push(`        attribute '${variable.name}' : ${variable.type === 'integer' ? 'Integer' : 'Real'}[0..1]${binding};`);
    }
    if (row.affected.length) lines.push(`        ref part affectedElements[0..*] = (${row.affected.map(partExpression).join(', ')});`);
    if (conditional) {
      try {
        const ast = validateReferences(parseExpression(row.condition), workspace);
        if (expressionType(ast) !== 'boolean') throw new Error('The condition must produce a Boolean.');
        if (strict) for (const evaluator of evaluators) checkResolved(() => evaluator.expression(ast, row));
        const expression = printExpression(ast, reference, `${packageName}::spacecraft_mode.display_name`);
        lines.push(`        ${row.kind === 'Requirement' ? 'require' : 'assert'} constraint verificationCondition { ${expression} }`);
      } catch (error) {
        if (strict) throw new Error(`${row.id}: ${error.message}`);
        lines.push('        doc /* The UI reports an invalid or unresolved verification expression. */');
      }
    }
    lines.push('    }');
  }
  for (const row of workspace.statements) {
    for (const source of row.sources) lines.push(`    dependency from ${names.get(row.key)} to ${names.get(source)};`);
  }
  for (const link of workspace.power.links) {
    const row = workspace.statements.find(row => row.context === link.eps && row.definition === 'FrameworkRequirements::LoadEnergy');
    lines.push(`    dependency from ${names.get(row.key)} to ${powerBudgetName(link.eps)};`);
  }
  for (const row of workspace.components) {
    for (const requirement of row.requirements) lines.push(`    dependency from ${names.get(row.key)} to ${names.get(requirement)};`);
  }
  lines.push('}', ...(includeData ? [end] : []));
  return lines.join('\n');
}

export function renderExport(workspace, options = {}) {
  return renderManaged(workspace, { ...options, includeData: false, strict: true }) + '\n';
}

export function updateSource(source, workspace, options) {
  const eol = source.includes('\r\n') ? '\r\n' : '\n';
  const block = renderManaged(workspace, options).replaceAll('\n', eol);
  const range = managedRange(source);
  if (!range) return `${source}${source.endsWith('\n') ? eol : eol + eol}${block}${eol}`;
  return source.slice(0, range[0]) + block + source.slice(range[1]);
}

export function createStore(modelPath, { catalog = domainTypes, products = null, initialWorkspace = null } = {}) {
  let queue = Promise.resolve();
  const modelName = basename(modelPath);
  const stem = basename(modelPath, '.sysml').replace(/[^A-Za-z0-9_]/g, '_');
  const packageName = `${/^[A-Za-z_]/.test(stem) ? stem[0].toUpperCase() + stem.slice(1) : `Mission_${stem}`}Requirements`;
  const sourceFile = async () => {
    try { return await readFile(modelPath, 'utf8'); }
    catch (error) {
      if (error.code !== 'ENOENT') throw error;
      await mkdir(dirname(modelPath), { recursive: true });
      await writeFile(modelPath, renderManaged(initialWorkspace ?? emptyWorkspace(catalog), { packageName, catalog, products }) + '\n', { flag: 'wx' }).catch(error => {
        if (error.code !== 'EEXIST') throw error;
      });
      return readFile(modelPath, 'utf8');
    }
  };
  const read = async () => {
    const source = await sourceFile();
    return { workspace: readWorkspace(source, catalog, products), revision: revisionOf(source), modelName };
  };
  const save = (workspace, revision) => {
    const operation = queue.then(async () => {
      validateWorkspace(workspace, catalog, products);
      const source = await sourceFile();
      if (revision !== revisionOf(source)) throw Object.assign(new Error(`${modelName} changed. Reload before saving to avoid overwriting changes.`), { status: 409 });
      const updated = updateSource(source, workspace, { packageName, catalog, products });
      const temporary = `${modelPath}.${randomUUID()}.tmp`;
      try {
        const { mode } = await stat(modelPath);
        await writeFile(temporary, updated, { encoding: 'utf8', mode });
        if (revisionOf(await readFile(modelPath, 'utf8')) !== revision) throw Object.assign(new Error(`${modelName} changed while saving. Reload before saving again.`), { status: 409 });
        await rename(temporary, modelPath);
      } finally { await unlink(temporary).catch(() => {}); }
      return { workspace, revision: revisionOf(updated), modelName };
    });
    queue = operation.catch(() => {});
    return operation;
  };
  return { read, save };
}
