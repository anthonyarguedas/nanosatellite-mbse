// Tests use the same Python engine as the application and plain JSON snapshots.
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { domainTypes, validateWorkspace } from '../model.mjs';
import { scriptContext } from '../verification-methods.mjs';

export const serializeWorkspace = workspace => JSON.stringify(workspace, null, 2) + '\n';
export const readWorkspace = (source, catalog = domainTypes, products = null) => validateWorkspace(JSON.parse(source), catalog, products);
export const roundTrip = workspace => JSON.parse(JSON.stringify(workspace));

function execute(workspace, options = {}) {
  const request = { id: 1, operation: 'evaluate', workspace,
    runs: options.scriptResults?.signature === scriptContext(workspace) ? options.scriptResults.runs : {},
    ...(Object.hasOwn(options, 'mode') ? { mode: options.mode } : {}) };
  const worker = fileURLToPath(new URL('../worker/main.py', import.meta.url));
  const result = spawnSync(process.env.VERIFICATION_PYTHON || 'python3', ['-I', '-B', '-u', worker], {
    input: JSON.stringify(request) + '\n', encoding: 'utf8', maxBuffer: 16 * 1024 * 1024, timeout: 15000,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(result.stderr || 'Python calculation failed.');
  const response = JSON.parse(result.stdout);
  if (response.error) throw Object.assign(new Error(response.error.message), { pending: response.error.pending });
  return response.result;
}
export const evaluateChecks = (workspace, options) => execute(workspace, options).results;
export function createEvaluator(workspace, options = {}) {
  const checkParameter = (row, name) => {
    const data = execute(workspace, { mode: options.mode ?? null, ...options });
    return [...data.results, ...data.scripts].find(result => result.key === row.key)?.parameters[name];
  };
  return { checkParameter, parameter(row, name) {
    const result = checkParameter(row, name);
    if (result?.state === 'value') return result.value;
    throw Object.assign(new Error(result?.message || 'Parameter is unset.'), { pending: result?.state === 'pending' || result?.state === 'unset' });
  } };
}
export function evaluateExpression(source, workspace, row) {
  const copy = structuredClone(workspace), probe = '_test_probe';
  copy.variables.push({ name: probe, type: 'float' });
  for (const target of copy.statements) target.parameters[probe] = target.key === row.key ? source : null;
  return createEvaluator(copy).parameter(copy.statements.find(target => target.key === row.key), probe);
}
export function validateCalculations(workspace, { catalog = domainTypes, products = null } = {}) {
  validateWorkspace(workspace, catalog, products);
  const results = evaluateChecks(workspace);
  for (const result of results) {
    const row = workspace.statements.find(row => row.key === result.key);
    for (const [name, cell] of Object.entries(result.parameters)) if (cell.state === 'error') throw new Error(`${row.id}.${name}: ${cell.message}`);
    for (const method of result.methods) if (method.state === 'error') throw new Error(`${row.id}: ${method.message}`);
  }
  return serializeWorkspace(workspace);
}
