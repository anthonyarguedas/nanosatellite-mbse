import { createHash, randomUUID } from 'node:crypto';
import { link, lstat, mkdir, open, readFile, rename, unlink } from 'node:fs/promises';
import { basename, dirname, extname, resolve } from 'node:path';
import { domainTypes, emptyWorkspace, validateWorkspace } from './model.mjs';
import { expandPowerAllocations } from './power.mjs';

const queues = new Map();
const conflict = message => Object.assign(new Error(message), { status: 409 });

export function workspacePaths(path) {
  path = resolve(path);
  if (extname(path).toLowerCase() !== '.json') throw new Error('Choose a .json workspace file.');
  return { path };
}
export async function canonicalWorkspace(workspace, { catalog = domainTypes, products = null } = {}) {
  const validated = validateWorkspace(structuredClone(workspace), catalog, products);
  return { workspace: validateWorkspace(expandPowerAllocations(validated), catalog, products) };
}

export function createStore(modelPath, { catalog = domainTypes, products = null, initialWorkspace = null, createIfMissing = true } = {}) {
  const { path } = workspacePaths(modelPath), modelName = basename(path);
  const revision = source => createHash('sha256').update(path).update('\0').update(source).digest('hex');
  const missing = () => Object.assign(new Error('The session file is missing.'), { status: 404 });
  const state = async () => {
    try {
      const info = await lstat(path);
      if (!info.isFile() || info.isSymbolicLink()) throw new Error(`${modelName} must be a regular workspace file, not a symlink.`);
      if (info.size > 16 * 1024 * 1024) throw new Error(`${modelName} exceeds the workspace file size limit.`);
      const source = await readFile(path, 'utf8');
      return { kind: 'json', source, mode: info.mode, revision: revision(source) };
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
    if (!createIfMissing) throw missing();
    return { kind: 'new', revision: revision('missing'), mode: 0o600 };
  };
  const prepared = data => canonicalWorkspace(data, { catalog, products });
  const decode = async current => {
    if (current.kind === 'new') return prepared(initialWorkspace ?? emptyWorkspace(catalog));
    let data;
    try { data = JSON.parse(current.source.replace(/^\uFEFF/, '')); }
    catch (error) { throw new Error(`${modelName} contains invalid JSON (${error.message}). Repair it before reopening.`); }
    return prepared(data);
  };
  const withQueue = operation => {
    const previous = queues.get(path) ?? Promise.resolve();
    const task = previous.catch(() => {}).then(operation);
    queues.set(path, task);
    task.finally(() => { if (queues.get(path) === task) queues.delete(path); }).catch(() => {});
    return task;
  };
  const write = async (workspace, current) => {
    const serialized = JSON.stringify(workspace, null, 2) + '\n';
    await mkdir(dirname(path), { recursive: true });
    const temporary = `${path}.${randomUUID()}.tmp`, lockPath = `${path}.lock`;
    let lock;
    try {
      try { lock = await open(lockPath, 'wx', 0o600); }
      catch (error) { if (error.code === 'EEXIST') throw conflict(`${modelName} is locked by another save. Check for another server, or remove its .lock file after confirming that server has stopped.`); throw error; }
      await lock.writeFile(JSON.stringify({ pid: process.pid, createdAt: new Date().toISOString() }) + '\n');
      const permissions = current.kind === 'json' ? current.mode & 0o777 : 0o600;
      const handle = await open(temporary, 'wx', permissions);
      try { await handle.chmod(permissions); await handle.writeFile(serialized, 'utf8'); await handle.sync(); }
      finally { await handle.close(); }
      if ((await state()).revision !== current.revision) throw conflict(`${modelName} changed while saving. Reload before saving again.`);
      if (current.kind === 'json') await rename(temporary, path);
      else {
        try { await link(temporary, path); }
        catch (error) { if (error.code === 'EEXIST') throw conflict(`${modelName} was created elsewhere. Reload before saving.`); throw error; }
      }
      return { workspace, revision: revision(serialized), modelName, storage: 'json' };
    } finally {
      try { await unlink(temporary).catch(error => { if (error.code !== 'ENOENT') throw error; }); }
      finally {
        if (lock) {
          const owned = await lock.stat(); await lock.close();
          const actual = await lstat(lockPath).catch(error => { if (error.code !== 'ENOENT') throw error; return null; });
          if (actual?.ino === owned.ino && actual.dev === owned.dev) await unlink(lockPath);
        }
      }
    }
  };
  const present = async current => ({ workspace: (await decode(current)).workspace, revision: current.revision, modelName, storage: 'json' });
  const read = async () => {
    const current = await state();
    if (current.kind !== 'new') return present(current);
    return withQueue(async () => {
      const latest = await state();
      return latest.kind === 'new' ? write((await decode(latest)).workspace, latest) : present(latest);
    });
  };
  const save = (workspace, expectedRevision) => {
    const snapshot = structuredClone(workspace);
    return withQueue(async () => {
      const current = await state();
      if (expectedRevision !== current.revision) throw conflict(`${modelName} changed. Reload before saving to avoid overwriting changes.`);
      return write((await prepared(snapshot)).workspace, current);
    });
  };
  return { path, read, save };
}
