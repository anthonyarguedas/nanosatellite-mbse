import { createServer as httpServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { createStore } from './sysml.mjs';
import { loadCatalog } from './catalog.mjs';

const publicFiles = new Map([
  ['/', ['public/index.html', 'text/html; charset=utf-8']],
  ['/app.js', ['public/app.js', 'text/javascript; charset=utf-8']],
  ['/style.css', ['public/style.css', 'text/css; charset=utf-8']],
  ['/model.mjs', ['model.mjs', 'text/javascript; charset=utf-8']],
  ['/verification.mjs', ['verification.mjs', 'text/javascript; charset=utf-8']],
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
  ? resolve(process.env.MISSION_FILE) : fileURLToPath(new URL('../missions/mission.sysml', import.meta.url)) } = {}) {
  const genericModels = ['external', 'mission', 'eps', 'catalog', 'cad'].map(name =>
    fileURLToPath(new URL(`../${name}.sysml`, import.meta.url)));
  if (genericModels.includes(resolve(modelPath))) throw new Error('Choose a mission instance file. Generic framework models are read only.');
  const catalogReady = loadCatalog();
  const storeReady = catalogReady.then(catalog => createStore(modelPath, { catalog }));
  storeReady.catch(() => {});
  return httpServer(async (request, response) => {
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
      if (url.pathname === '/api/workspace') {
        const store = await storeReady;
        const catalog = await catalogReady;
        if (request.method === 'GET') return json(200, { ...await store.read(), catalog });
        if (request.method === 'PUT') {
          const { workspace, revision } = await bodyJSON(request);
          return json(200, { ...await store.save(workspace, revision), catalog });
        }
        response.setHeader('Allow', 'GET, PUT');
        return json(405, { error: 'Method not allowed.' });
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
    console.log(`Edits are saved to ${process.env.MISSION_FILE ?? 'framework/missions/mission.sysml'}.`);
  });
}
