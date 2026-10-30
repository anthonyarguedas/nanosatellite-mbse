import { createHash, randomUUID } from 'node:crypto';
import { mkdir, readFile, rename, stat, unlink, writeFile } from 'node:fs/promises';
import { basename, dirname } from 'node:path';
import { domainTypes, emptyWorkspace, migrateWorkspace, stakeholderTypes, tabsFor, validateWorkspace } from './model.mjs';
import { expressionType, parseExpression, printExpression, validateReferences } from './verification.mjs';

const begin = '// <requirements-ui>';
const end = '// </requirements-ui>';
const dataBegin = '/* requirements-ui:data\n';
const dataEnd = '\nrequirements-ui:end-data */';
const revisionOf = source => createHash('sha256').update(source).digest('hex');
const identifier = (table, key) => `${table === 'stakeholders' ? 'stakeholder' : table === 'elements' ? 'element' : 'statement'}_${key.replace(/[-_]/g, char => char === '-' ? '_h' : '_u')}`;
const literal = value => JSON.stringify(value);

function managedRange(source) {
  const starts = [...source.matchAll(/^\/\/ <requirements-ui>\r?$/gm)];
  const ends = [...source.matchAll(/^\/\/ <\/requirements-ui>\r?$/gm)];
  if (!starts.length && !ends.length) return null;
  if (starts.length !== 1 || ends.length !== 1 || starts[0].index >= ends[0].index) throw new Error('The requirements-ui section is incomplete or duplicated.');
  return [starts[0].index, ends[0].index + end.length];
}

export function readWorkspace(source, catalog = domainTypes) {
  const range = managedRange(source);
  if (!range) return emptyWorkspace(catalog);
  const block = source.slice(...range).replaceAll('\r\n', '\n');
  const start = block.indexOf(dataBegin), finish = block.indexOf(dataEnd);
  if (start === -1 || finish === -1) throw new Error('The requirements-ui data is missing.');
  return validateWorkspace(migrateWorkspace(JSON.parse(block.slice(start + dataBegin.length, finish)), catalog), catalog);
}

export function renderManaged(workspace, { packageName = 'MissionRequirements', catalog = domainTypes } = {}) {
  validateWorkspace(workspace, catalog);
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(packageName)) throw new Error('Invalid mission package name.');
  const metadata = JSON.stringify(workspace, null, 2).replaceAll('*/', '\\u002a/');
  const lines = [begin,
    '// Mission data managed by requirements-ui. Generic definitions are imported.',
    '// The JSON preserves UI data. The SysML elements below are generated from it.',
    dataBegin + metadata + dataEnd,
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
  const elementNames = new Map(workspace.elements.map(row => [row.key, identifier('elements', row.key)]));
  for (const row of workspace.elements) {
    const name = row.owner === 'mission' ? elementNames.get(row.key) : `${elementNames.get(row.owner)}::${elementNames.get(row.key)}`;
    names.set(row.key, name);
    namesById.set(row.id, name);
  }
  const partExpression = key => names.get(key).replaceAll('::', '.');
  const contexts = new Map(tabsFor(workspace, catalog).map(tab => [tab.key, tab.label]));
  for (const row of workspace.stakeholders) {
    const type = stakeholderTypes.find(type => type.name === row.type);
    lines.push(`    part ${names.get(row.key)} : ${type.model} {`,
      `        attribute externalId : String = ${literal(row.id)};`,
      `        attribute displayName : String = ${literal(row.name)};`, '    }');
  }
  const emitElement = (row, indent) => {
    lines.push(`${indent}part ${elementNames.get(row.key)} : ${row.definition} {`,
      `${indent}    attribute externalId : String = ${literal(row.id)};`,
      `${indent}    attribute displayName : String = ${literal(row.name)};`);
    for (const child of workspace.elements.filter(child => child.owner === row.key)) emitElement(child, indent + '    ');
    lines.push(`${indent}}`);
  };
  for (const row of workspace.elements.filter(row => row.owner === 'mission')) emitElement(row, '    ');
  for (const row of workspace.statements) {
    const keyword = row.kind === 'Requirement' ? 'requirement' : 'attribute';
    const conditional = Boolean(row.condition.trim());
    lines.push(`    ${keyword} ${names.get(row.key)} {`,
      `        attribute externalId : String = ${literal(row.id)};`,
      `        attribute tableName : String = ${literal(contexts.get(row.context))};`,
      `        attribute statementKind : String = ${literal(row.kind)};`,
      `        attribute statementText : String = ${literal(row.text)};`,
      `        attribute verificationExpression : String[0..1]${conditional ? ` = ${literal(row.condition)}` : ''};`);
    for (const variable of workspace.variables) {
      const value = row.parameters[variable.name];
      lines.push(`        attribute '${variable.name}' : ${variable.type === 'integer' ? 'Integer' : 'Real'}[0..1]${value === null ? '' : ` = ${value}`};`);
    }
    if (row.affected.length) lines.push(`        ref part affectedElements[0..*] = (${row.affected.map(partExpression).join(', ')});`);
    if (conditional) {
      try {
        const ast = validateReferences(parseExpression(row.condition), workspace);
        if (expressionType(ast) !== 'boolean') throw new Error('The condition must produce a Boolean.');
        const expression = printExpression(ast, (id, name) => `${namesById.get(id)}.'${name}'`);
        lines.push(`        ${row.kind === 'Requirement' ? 'require' : 'assert'} constraint verificationCondition { ${expression} }`);
      } catch {
        lines.push('        doc /* The UI reports an invalid or unresolved verification expression. */');
      }
    }
    lines.push('    }');
  }
  for (const row of workspace.statements) {
    for (const source of row.sources) lines.push(`    dependency from ${names.get(row.key)} to ${names.get(source)};`);
  }
  lines.push('}', end);
  return lines.join('\n');
}

export function updateSource(source, workspace, options) {
  const eol = source.includes('\r\n') ? '\r\n' : '\n';
  const block = renderManaged(workspace, options).replaceAll('\n', eol);
  const range = managedRange(source);
  if (!range) return `${source}${source.endsWith('\n') ? eol : eol + eol}${block}${eol}`;
  return source.slice(0, range[0]) + block + source.slice(range[1]);
}

export function createStore(modelPath, { catalog = domainTypes } = {}) {
  let queue = Promise.resolve();
  const modelName = basename(modelPath);
  const stem = basename(modelPath, '.sysml').replace(/[^A-Za-z0-9_]/g, '_');
  const packageName = `${/^[A-Za-z_]/.test(stem) ? stem[0].toUpperCase() + stem.slice(1) : `Mission_${stem}`}Requirements`;
  const sourceFile = async () => {
    try { return await readFile(modelPath, 'utf8'); }
    catch (error) {
      if (error.code !== 'ENOENT') throw error;
      await mkdir(dirname(modelPath), { recursive: true });
      await writeFile(modelPath, renderManaged(emptyWorkspace(catalog), { packageName, catalog }) + '\n', { flag: 'wx' }).catch(error => {
        if (error.code !== 'EEXIST') throw error;
      });
      return readFile(modelPath, 'utf8');
    }
  };
  const read = async () => {
    const source = await sourceFile();
    return { workspace: readWorkspace(source, catalog), revision: revisionOf(source), modelName };
  };
  const save = (workspace, revision) => {
    const operation = queue.then(async () => {
      validateWorkspace(workspace, catalog);
      const source = await sourceFile();
      if (revision !== revisionOf(source)) throw Object.assign(new Error(`${modelName} changed. Reload before saving to avoid overwriting changes.`), { status: 409 });
      const updated = updateSource(source, workspace, { packageName, catalog });
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
