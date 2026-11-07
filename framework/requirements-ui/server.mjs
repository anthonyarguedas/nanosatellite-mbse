import { createServer as httpServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { basename, extname, resolve } from 'node:path';
import { createSessions } from './sessions.mjs';
import { loadCatalog } from './catalog.mjs';
import { loadProducts } from './cots.mjs';
import { renderSchematic } from './kicad.mjs';
import { renderFprimeArchive } from './fprime.mjs';
import { defaultScriptDirectory, loadScriptCatalog, runScripts } from './python.mjs';
import { validateWorkspace } from './model.mjs';
import { createEvaluationWorker } from './evaluation-worker.mjs';
import { canonicalWorkspace, workspacePaths } from './storage.mjs';

const publicFiles = new Map([
  ['/', ['public/index.html', 'text/html; charset=utf-8']],
  ['/app.js', ['public/app.js', 'text/javascript; charset=utf-8']],
  ['/requirement-editor.js', ['public/requirement-editor.js', 'text/javascript; charset=utf-8']],
  ['/power-editor.js', ['public/power-editor.js', 'text/javascript; charset=utf-8']],
  ['/power.mjs', ['power.mjs', 'text/javascript; charset=utf-8']],
  ['/resource-budgets.mjs', ['resource-budgets.mjs', 'text/javascript; charset=utf-8']],
  ['/parameter-states.mjs', ['parameter-states.mjs', 'text/javascript; charset=utf-8']],
  ['/verification-methods.mjs', ['verification-methods.mjs', 'text/javascript; charset=utf-8']],
  ['/expression-metadata.mjs', ['expression-metadata.mjs', 'text/javascript; charset=utf-8']],
  ['/verification-editor.js', ['public/verification-editor.js', 'text/javascript; charset=utf-8']],
  ['/requirement-preview.js', ['public/requirement-preview.js', 'text/javascript; charset=utf-8']],
  ['/style.css', ['public/style.css', 'text/css; charset=utf-8']],
  ['/model.mjs', ['model.mjs', 'text/javascript; charset=utf-8']],
  ['/verification-worker.js', ['public/verification-worker.js', 'text/javascript; charset=utf-8']],
]);

async function bodyJSON(request) {
  if (request.headers['content-type']?.split(';')[0].trim().toLowerCase() !== 'application/json') {
    throw Object.assign(new Error('Send application/json.'), { status: 415 });
  }
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 5_000_000) throw Object.assign(new Error('The workspace is too large.'), { status: 413 });
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { throw new Error('Invalid JSON.'); }
}

export function createServer({ modelPath = process.env.MISSION_FILE
  ? resolve(process.env.MISSION_FILE) : fileURLToPath(new URL('../missions/mission.json', import.meta.url)), sessionDirectory,
  scriptDirectory = process.env.VERIFICATION_SCRIPTS_DIR ? resolve(process.env.VERIFICATION_SCRIPTS_DIR) : defaultScriptDirectory,
  python = process.env.VERIFICATION_PYTHON || 'python3' } = {}) {
  workspacePaths(modelPath);
  const evaluator = createEvaluationWorker({ python });
  const catalogReady = loadCatalog({ evaluator });
  const productsReady = loadProducts();
  const sessionsReady = Promise.all([catalogReady, productsReady]).then(([catalog, products]) => createSessions(modelPath, { catalog, products, directory: sessionDirectory }));
  sessionsReady.catch(() => {});
  const runningScripts = new Set();
  const server = httpServer(async (request, response) => {
    response.setHeader('Cache-Control', 'no-store');
    response.setHeader('X-Content-Type-Options', 'nosniff');
    response.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; worker-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'");
    const json = (status, data) => {
      response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
      response.end(JSON.stringify(data));
    };
    try {
      const url = new URL(request.url, 'http://localhost');
      const host = new URL(`http://${request.headers.host}`).hostname;
      if (!['localhost', '127.0.0.1', '[::1]'].includes(host)
          || (request.headers.origin && request.headers.origin !== `http://${request.headers.host}`)) {
        return json(403, { error: 'Only requests from this local app are allowed.' });
      }
      if (url.pathname === '/api/evaluate') {
        if (request.method !== 'POST') { response.setHeader('Allow', 'POST'); return json(405, { error: 'Method not allowed.' }); }
        const { workspace, scriptResults, mode } = await bodyJSON(request);
        const controller = new AbortController(), cancel = () => controller.abort();
        response.once('close', cancel);
        try { return json(200, await evaluator.evaluate(workspace, { scriptResults, ...(mode !== undefined ? { mode } : {}) }, { signal: controller.signal })); }
        finally { response.removeListener('close', cancel); }
      }
      if (url.pathname === '/api/scripts') {
        if (request.method !== 'GET') { response.setHeader('Allow', 'GET'); return json(405, { error: 'Method not allowed.' }); }
        return json(200, { scripts: await loadScriptCatalog(scriptDirectory) });
      }
      if (url.pathname === '/api/scripts/run') {
        if (request.method !== 'POST') { response.setHeader('Allow', 'POST'); return json(405, { error: 'Method not allowed.' }); }
        if (runningScripts.size >= 2) return json(429, { error: 'Two Python runs are already active. Wait for one to finish.' });
        const { workspace, script } = await bodyJSON(request);
        validateWorkspace(workspace, await catalogReady, await productsReady);
        if (runningScripts.size >= 2) return json(429, { error: 'Two Python runs are already active. Wait for one to finish.' });
        const controller = new AbortController(), cancel = () => controller.abort();
        runningScripts.add(controller); response.once('close', cancel);
        try { return json(200, await runScripts(workspace, script, { directory: scriptDirectory, python, evaluator, signal: controller.signal })); }
        finally { runningScripts.delete(controller); response.removeListener('close', cancel); }
      }
      if (url.pathname === '/api/sessions') {
        const sessions = await sessionsReady;
        if (request.method === 'GET') return json(200, { sessions: await sessions.list() });
        if (request.method === 'POST') {
          const data = await sessions.create(await bodyJSON(request));
          const catalog = await catalogReady, products = (await productsReady).map(({ pins, ...product }) => product);
          return json(201, { ...data, sessions: await sessions.list(), catalog, products });
        }
        response.setHeader('Allow', 'GET, POST');
        return json(405, { error: 'Method not allowed.' });
      }
      if (url.pathname === '/api/workspace') {
        const { store, session } = await (await sessionsReady).get(url.searchParams.get('session') ?? 'current');
        const catalog = await catalogReady;
        const products = (await productsReady).map(({ pins, ...product }) => product);
        if (request.method === 'GET') return json(200, { ...await store.read(), session, catalog, products });
        if (request.method === 'PUT') {
          const { workspace, revision } = await bodyJSON(request);
          return json(200, { ...await store.save(workspace, revision), session, catalog, products });
        }
        response.setHeader('Allow', 'GET, PUT');
        return json(405, { error: 'Method not allowed.' });
      }
      if (url.pathname === '/api/json') {
        if (request.method !== 'POST') { response.setHeader('Allow', 'POST'); return json(405, { error: 'Method not allowed.' }); }
        const { workspace } = await bodyJSON(request);
        const canonical = await canonicalWorkspace(workspace, { catalog: await catalogReady, products: await productsReady });
        const id = url.searchParams.get('session') ?? 'current';
        const name = id === 'current' ? basename(modelPath, extname(modelPath)) : (await (await sessionsReady).get(id)).session.name;
        const stem = name.replace(/[^A-Za-z0-9_]/g, '_');
        response.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8',
          'Content-Disposition': `attachment; filename="${stem}-export.json"` });
        return response.end(JSON.stringify(canonical.workspace, null, 2) + '\n');
      }
      if (['/api/kicad', '/api/fprime'].includes(url.pathname)) {
        if (request.method !== 'POST') {
          response.setHeader('Allow', 'POST');
          return json(405, { error: 'Method not allowed.' });
        }
        const { workspace, context } = await bodyJSON(request);
        const catalog = await catalogReady, products = await productsReady;
        const projectName = `eps-${workspace?.elements?.find(row => row.key === context)?.id?.toLowerCase() ?? 'components'}`;
        const fprime = url.pathname === '/api/fprime';
        const artifact = fprime ? renderFprimeArchive(workspace, context, { catalog, products })
          : renderSchematic(workspace, context, { catalog, products, projectName,
            checks: (await evaluator.evaluate(workspace)).results });
        response.writeHead(200, { 'Content-Type': fprime ? 'application/zip' : 'application/octet-stream',
          'Content-Disposition': `attachment; filename="${projectName}${fprime ? '-fprime.zip' : '.kicad_sch'}"` });
        return response.end(artifact);
      }
      const file = publicFiles.get(url.pathname);
      if (!file) return json(404, { error: 'Not found.' });
      if (!['GET', 'HEAD'].includes(request.method)) {
        response.setHeader('Allow', 'GET, HEAD');
        return json(405, { error: 'Method not allowed.' });
      }
      const content = await readFile(new URL(file[0], import.meta.url));
      response.writeHead(200, { 'Content-Type': file[1] });
      response.end(request.method === 'HEAD' ? undefined : content);
    } catch (error) {
      const status = error.status ?? (error.code ? 500 : 400);
      if (status === 500) console.error(error);
      json(status, { error: status === 500 ? 'Could not read or save the mission model. Check the terminal.' : error.message });
    }
  });
  server.on('close', () => evaluator.close());
  return server;
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  const port = Number(process.env.PORT ?? 3000);
  if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('PORT must be a valid port number.');
  const server = createServer();
  server.on('error', error => {
    console.error(error.code === 'EADDRINUSE' ? `Port ${port} is busy. Try PORT=3001 npm start.` : error.message);
    process.exitCode = 1;
  });
  server.listen(port, '127.0.0.1', () => {
    console.log(`Requirements UI: http://127.0.0.1:${server.address().port}`);
    console.log(`Edits are saved as JSON (${process.env.MISSION_FILE ? workspacePaths(resolve(process.env.MISSION_FILE)).path : 'framework/missions/mission.json'}).`);
  });
}
