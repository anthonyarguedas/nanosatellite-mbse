import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { mkdtemp, readFile, readdir, realpath, rm, stat, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, relative, resolve, sep } from 'node:path';
import { validScriptParameterName } from './model.mjs';
import { createEvaluationWorker, evaluationRequest } from './evaluation-worker.mjs';
import { runKey, scriptContext } from './verification-methods.mjs';

export const defaultScriptDirectory = new URL('./scripts/', import.meta.url);
const slug = value => typeof value === 'string' && /^[a-z][a-z0-9_]{0,79}$/.test(value);
const fail = message => { throw new Error(`Python scripts: ${message}`); };

async function registeredScript(directory, id) {
  if (!slug(id)) fail('choose a registered script ID.');
  let root;
  try { root = await realpath(directory); } catch { fail('the configured script directory is unavailable.'); }
  const read = async (extension, maximum) => {
    let file;
    try { file = await realpath(join(root, `${id}.${extension}`)); } catch { fail(`${id}.${extension} is not available in the registered script directory.`); }
    const path = relative(root, file);
    if (path.startsWith(`..${sep}`) || path === '..' || resolve(root, path) !== file) fail('script files must remain inside the configured script directory.');
    const info = await stat(file);
    if (!info.isFile() || info.size > maximum) fail(`the ${extension} file exceeds its size limit.`);
    return readFile(file, 'utf8');
  };
  const metadata = await read('json', 32768), source = await read('py', 262144);
  let data;
  try { data = JSON.parse(metadata); } catch { fail(`${id}.json must contain JSON.`); }
  if (data.id !== id || typeof data.name !== 'string' || !data.name.trim() || data.name.length > 80
      || typeof data.description !== 'string' || data.description.length > 2000) fail(`${id}: provide an ID, name and description.`);
  if (!Array.isArray(data.inputs) || data.inputs.length > 32 || !Array.isArray(data.outputs) || !data.outputs.length || data.outputs.length > 32) fail(`${id}: declare up to 32 inputs and 1 to 32 outputs.`);
  const names = new Set();
  for (const parameter of [...data.inputs, ...data.outputs]) {
    if (!parameter || !validScriptParameterName(parameter.name) || names.has(parameter.name)
        || !['float', 'integer', 'boolean'].includes(parameter.type)
        || (parameter.unit !== undefined && (typeof parameter.unit !== 'string' || parameter.unit.length > 100 || /[\r\n]/.test(parameter.unit)))
        || Object.keys(parameter).some(key => !['name', 'type', 'unit'].includes(key))) fail(`${id}: declare unique, typed parameter names and optional units.`);
    names.add(parameter.name);
  }
  const timeoutMs = data.timeoutMs ?? 3000;
  if (!Number.isInteger(timeoutMs) || timeoutMs < 10 || timeoutMs > 10000) fail(`${id}: timeoutMs must be between 10 and 10,000.`);
  const revision = createHash('sha256').update(metadata).update('\0').update(source).digest('hex');
  return { definition: { id, name: data.name, description: data.description, inputs: data.inputs, outputs: data.outputs, timeoutMs, revision }, source };
}

export async function loadScriptCatalog(directory = defaultScriptDirectory) {
  let entries;
  try { entries = await readdir(directory, { withFileTypes: true }); }
  catch (error) { if (error.code === 'ENOENT') return []; throw error; }
  const definitions = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    if (entry.isFile() && entry.name.endsWith('.json')) definitions.push((await registeredScript(directory, entry.name.slice(0, -5))).definition);
  }
  return definitions;
}

async function executePython(source, payload, { python, timeoutMs, signal }) {
  if (signal?.aborted) throw new Error('Python execution was cancelled.');
  const directory = await mkdtemp(join(tmpdir(), 'requirements-python-'));
  try {
    const file = join(directory, 'analysis.py');
    await writeFile(file, source, { mode: 0o600 });
    return await new Promise((resolve, reject) => {
      const child = spawn(python, ['-I', '-u', file], { cwd: directory,
        env: { PATH: process.env.PATH, HOME: directory, LANG: 'en_US.UTF-8', ...(process.env.SystemRoot ? { SystemRoot: process.env.SystemRoot } : {}) },
        detached: process.platform !== 'win32', stdio: ['pipe', 'pipe', 'pipe'] });
      let stdout = '', stderr = '', size = 0, failure;
      const kill = message => {
        failure ??= message;
        try { if (process.platform === 'win32') child.kill('SIGKILL'); else process.kill(-child.pid, 'SIGKILL'); } catch { /* Already exited. */ }
      };
      const timer = setTimeout(() => kill(`Python execution timed out after ${timeoutMs} ms.`), timeoutMs);
      const abort = () => kill('Python execution was cancelled.');
      signal?.addEventListener('abort', abort, { once: true });
      const cleanup = () => { clearTimeout(timer); signal?.removeEventListener('abort', abort); };
      child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
      for (const [stream, output] of [[child.stdout, true], [child.stderr, false]]) stream.on('data', chunk => {
        size += Buffer.byteLength(chunk);
        if (size > 1048576) { kill('Python output exceeded 1 MiB.'); return; }
        if (output) stdout += chunk;
        else stderr += chunk;
      });
      child.on('error', error => { cleanup(); reject(new Error(`Could not start Python (${error.message}). Set VERIFICATION_PYTHON to a Python 3 executable.`)); });
      child.on('close', (code, exitSignal) => {
        cleanup();
        // Clean up descendants even if the script exited before them.
        if (process.platform !== 'win32') { try { process.kill(-child.pid, 'SIGKILL'); } catch { /* No descendants. */ } }
        if (failure || code !== 0) return reject(new Error(failure || `Python exited ${exitSignal ?? code}: ${stderr.trim().slice(-2000) || 'No error details.'}`));
        try {
          const values = JSON.parse(stdout);
          if (!values || typeof values !== 'object' || Array.isArray(values)) throw new Error('expected a JSON object');
          resolve({ values, log: stderr.trim().slice(-2000) });
        } catch (error) { reject(new Error(`Python must write one JSON object to stdout (${error.message}). Write diagnostics to stderr.`)); }
      });
      child.stdin.on('error', () => {});
      child.stdin.end(JSON.stringify(payload));
      if (signal?.aborted) abort();
    });
  } finally { await rm(directory, { recursive: true, force: true }); }
}

export async function runScripts(workspace, key, { directory = defaultScriptDirectory,
  python = process.env.VERIFICATION_PYTHON || 'python3', evaluator = null, signal, totalTimeoutMs = 30000 } = {}) {
  if (!workspace.scripts.some(script => script.key === key)) fail('choose an existing script instance.');
  const evidence = { signature: scriptContext(workspace), runs: {} }, running = new Set(), registered = new Map();
  const modes = workspace.power.modes.length ? workspace.power.modes : [{ key: null, name: null }];
  const deadline = Date.now() + totalTimeoutMs;
  const worker = evaluator ?? createEvaluationWorker({ python });
  const ensure = async (script, mode) => {
    const identity = runKey(script.key, mode.key);
    if (running.has(identity)) throw new Error(`Cyclic Python dependency at ${script.id}.`);
    if (evidence.runs[identity]) return;
    running.add(identity);
    const result = { script: script.key, mode: mode.key, revision: script.revision, state: 'pending', values: {}, message: '' };
    try {
      if (signal?.aborted) throw new Error('Python execution was cancelled.');
      if (Date.now() >= deadline) throw new Error('The Python run exceeded its total time limit.');
      if (!registered.has(script.definition)) registered.set(script.definition, await registeredScript(directory, script.definition));
      const { definition, source } = registered.get(script.definition);
      if (definition.revision !== script.revision || JSON.stringify(definition.inputs) !== JSON.stringify(script.inputs)
          || JSON.stringify(definition.outputs) !== JSON.stringify(script.outputs)) throw new Error(`${script.id}: the registered script changed. Update its definition before running.`);
      let inputs, requirements;
      for (let attempt = 0; attempt <= workspace.scripts.length; attempt++) {
        try {
          ({ inputs, requirements } = await worker.request(evaluationRequest(workspace, {
            operation: 'script_inputs', script: script.key, mode: mode.key, scriptResults: evidence, expectedCotsSignature: evidence.cotsSignature ?? null,
          }), { signal, timeout: Math.max(1, deadline - Date.now()) }));
          break;
        } catch (error) {
          const dependency = error.scriptKey && workspace.scripts.find(script => script.key === error.scriptKey);
          if (!dependency || evidence.runs[runKey(dependency.key, mode.key)]) throw error;
          await ensure(dependency, mode);
        }
      }
      const output = await executePython(source, { inputs, requirements, mode: mode.key === null ? null : { key: mode.key, name: mode.name } },
        { python, signal, timeoutMs: Math.max(1, Math.min(definition.timeoutMs, deadline - Date.now())) });
      if (Object.keys(output.values).length !== script.outputs.length || Object.keys(output.values).some(name => !script.outputs.some(output => output.name === name))) throw new Error(`${script.id}: return exactly the declared output names.`);
      for (const parameter of script.outputs) {
        const value = output.values[parameter.name];
        if (value === null) continue;
        if (parameter.type === 'boolean' ? typeof value !== 'boolean' : typeof value !== 'number' || !Number.isFinite(value)
            || (parameter.type === 'integer' && !Number.isSafeInteger(value))) throw new Error(`${script.id}.${parameter.name}: return a finite ${parameter.type} value or null.`);
      }
      Object.assign(result, output, { state: 'value', executedAt: new Date().toISOString(), message: 'Python execution completed for the current inputs.' });
    } catch (error) {
      result.state = error.pending ? 'pending' : 'error';
      result.message = String(error.message).slice(0, 2500);
    } finally { running.delete(identity); evidence.runs[identity] = result; }
  };
  try {
    if (workspace.components?.some(component => component.facts?.length)) {
      evidence.cotsSignature = (await worker.request({ operation: 'cots_context', workspace }, { signal })).signature;
    }
    for (const mode of modes) await ensure(workspace.scripts.find(script => script.key === key), mode);
    return evidence;
  } finally { if (!evaluator) worker.close(); }
}
