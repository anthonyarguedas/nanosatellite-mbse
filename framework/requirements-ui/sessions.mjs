import { randomUUID } from 'node:crypto';
import { lstat, mkdir, readFile, readdir, rename, rm, writeFile } from 'node:fs/promises';
import { basename, dirname, join, resolve } from 'node:path';
import { blankWorkspace, emptyWorkspace, validateWorkspace } from './model.mjs';
import { createStore } from './sysml.mjs';

const validId = id => typeof id === 'string' && /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(id);
const fail = (status, message) => { throw Object.assign(new Error(message), { status }); };
function sessionName(value) {
  if (typeof value !== 'string' || !value.trim() || value.trim().length > 80 || /[\x00-\x1f\x7f]/.test(value)) fail(400, 'Session names must contain 1 to 80 characters on one line.');
  return value.trim();
}

export function createSessions(modelPath, { catalog, products, directory = join(dirname(modelPath), 'sessions') } = {}) {
  directory = resolve(directory);
  const current = { id: 'current', name: `Current mission (${basename(modelPath)})`, template: 'existing' };
  const currentStore = createStore(modelPath, { catalog, products });
  const stores = new Map();
  let creations = Promise.resolve();
  const folder = id => join(directory, id);
  const file = id => join(folder(id), `${id}.sysml`);
  async function metadata(id) {
    if (!validId(id)) fail(400, 'Invalid session ID.');
    try {
      if (!(await lstat(folder(id))).isDirectory() || !(await lstat(file(id))).isFile()) fail(404, 'The session file is missing.');
      const data = JSON.parse(await readFile(join(folder(id), 'session.json'), 'utf8'));
      if (data.id !== id || !['blank', 'generic-eps', 'copy'].includes(data.template) || typeof data.createdAt !== 'string') fail(400, 'Invalid session metadata.');
      sessionName(data.name);
      return { id, name: data.name, template: data.template, createdAt: data.createdAt };
    } catch (error) {
      if (error.code === 'ENOENT') fail(404, 'Session not found.');
      throw error;
    }
  }
  async function list() {
    let entries;
    try { entries = await readdir(directory, { withFileTypes: true }); }
    catch (error) { if (error.code === 'ENOENT') return [current]; throw error; }
    const sessions = [];
    for (const entry of entries) {
      if (!entry.isDirectory() || !validId(entry.name)) continue;
      try { sessions.push(await metadata(entry.name)); }
      catch (error) {
        // An interrupted creation has no metadata and stays out of the picker.
        if (error.status !== 404) throw error;
      }
    }
    return [current, ...sessions.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }))];
  }
  async function get(id = 'current') {
    if (id === 'current') return { session: current, store: currentStore };
    const session = await metadata(id);
    if (!stores.has(id)) stores.set(id, createStore(file(id), { catalog, products }));
    return { session, store: stores.get(id) };
  }
  function create({ name, template, workspace }) {
    const operation = creations.then(async () => {
      name = sessionName(name);
      if (!['blank', 'generic-eps', 'copy'].includes(template)) fail(400, 'Choose Blank, Generic EPS or a copy of the current session.');
      if (template !== 'copy' && workspace !== undefined) fail(400, 'Only Save as accepts an existing workspace.');
      const initialWorkspace = validateWorkspace(template === 'blank' ? blankWorkspace()
        : template === 'generic-eps' ? emptyWorkspace(catalog) : structuredClone(workspace), catalog, products);
      if ((await list()).some(session => session.name.toLowerCase() === name.toLowerCase())) fail(409, 'A session with this name already exists. Choose another name.');
      await mkdir(directory, { recursive: true });
      const id = randomUUID(), session = { id, name, template, createdAt: new Date().toISOString() };
      await mkdir(folder(id));
      try {
        const store = createStore(file(id), { catalog, products, initialWorkspace });
        const data = await store.read();
        const temporary = join(folder(id), 'session.json.tmp');
        await writeFile(temporary, JSON.stringify(session, null, 2) + '\n', { flag: 'wx' });
        await rename(temporary, join(folder(id), 'session.json'));
        stores.set(id, store);
        return { ...data, session };
      } catch (error) {
        await rm(folder(id), { recursive: true, force: true });
        throw error;
      }
    });
    creations = operation.catch(() => {});
    return operation;
  }
  return { list, get, create };
}
