// HTTP and static-file transport. framework.models owns model behavior.
import { createServer as httpServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createPythonService } from './python-client.mjs';
import { renderSchematic } from './exporters/kicad.mjs';
import { renderFprimeArchive } from './exporters/fprime.mjs';

const publicFiles = new Map([
  ['/', ['public/index.html', 'text/html; charset=utf-8']],
  ['/app.js', ['public/app.js', 'text/javascript; charset=utf-8']],
  ['/editors/requirement.js', ['public/editors/requirement.js', 'text/javascript; charset=utf-8']],
  ['/editors/verification.js', ['public/editors/verification.js', 'text/javascript; charset=utf-8']],
  ['/editors/power.js', ['public/editors/power.js', 'text/javascript; charset=utf-8']],
  ['/editors/cots.js', ['public/editors/cots.js', 'text/javascript; charset=utf-8']],
  ['/workbook.js', ['public/workbook.js', 'text/javascript; charset=utf-8']],
  ['/native-client.js', ['public/native-client.js', 'text/javascript; charset=utf-8']],
  ['/cots-view.js', ['public/cots-view.js', 'text/javascript; charset=utf-8']],
  ['/state-view.js', ['public/state-view.js', 'text/javascript; charset=utf-8']],
  ['/reference-view.js', ['public/reference-view.js', 'text/javascript; charset=utf-8']],
  ['/requirement-preview.js', ['public/requirement-preview.js', 'text/javascript; charset=utf-8']],
  ['/style.css', ['public/style.css', 'text/css; charset=utf-8']],
  ['/verification-worker.js', ['public/verification-worker.js', 'text/javascript; charset=utf-8']],
]);

async function bodyJSON(request) {
  if (request.headers['content-type']?.split(';')[0].trim().toLowerCase() !== 'application/json') {
    throw Object.assign(new Error('Send application/json.'), { status: 415 });
  }
  const chunks = []; let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 8 * 1024 * 1024) throw Object.assign(new Error('The workspace is too large.'), { status: 413 });
    chunks.push(chunk);
  }
  try {
    const data = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Expected an object.');
    return data;
  } catch { throw Object.assign(new Error('Send one JSON request object.'), { status: 400 }); }
}

export function createServer({ modelPath = process.env.MISSION_FILE
  ? resolve(process.env.MISSION_FILE) : undefined,
  sessionDirectory, cotsDirectory,
  python = process.env.VERIFICATION_PYTHON || 'python3', installed = false } = {}) {
  const service = createPythonService({ modelPath, sessionDirectory, cotsDirectory, python, installed });
  const runs = new Set();
  const server = httpServer(async (request, response) => {
    response.setHeader('Cache-Control', 'no-store');
    response.setHeader('X-Content-Type-Options', 'nosniff');
    response.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; worker-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'");
    const json = (status, data) => {
      if (response.destroyed) return;
      response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
      response.end(JSON.stringify(data));
    };
    const call = async (operation, data = {}, control = {}) => {
      const controller = new AbortController(), cancel = () => controller.abort();
      response.once('close', cancel);
      try { return await service.request({ ...data, operation }, { ...control, signal: controller.signal }); }
      finally { response.removeListener('close', cancel); }
    };
    const methods = allowed => {
      if (allowed.includes(request.method)) return true;
      response.setHeader('Allow', allowed.join(', ')); json(405, { error: 'Method not allowed.' }); return false;
    };
    try {
      const url = new URL(request.url, 'http://localhost');
      const host = new URL(`http://${request.headers.host}`).hostname;
      if (!['localhost', '127.0.0.1', '[::1]'].includes(host)
          || (request.headers.origin && request.headers.origin !== `http://${request.headers.host}`)) return json(403, { error: 'Only requests from this local app are allowed.' });
      const session = url.searchParams.get('session') ?? 'current';
      if (url.pathname === '/api/workspace') {
        if (!methods(['GET', 'PUT'])) return;
        return json(200, request.method === 'GET' ? await call('open', { session }) : await call('save', { ...await bodyJSON(request), session }));
      }
      if (url.pathname === '/api/sessions') {
        if (!methods(['GET', 'POST'])) return;
        return json(request.method === 'POST' ? 201 : 200, await call(request.method === 'POST' ? 'create' : 'sessions', request.method === 'POST' ? await bodyJSON(request) : {}));
      }
      if (url.pathname === '/api/evaluate') {
        if (!methods(['POST'])) return;
        return json(200, await call('evaluate', await bodyJSON(request)));
      }
      if (url.pathname === '/api/draft' || url.pathname === '/api/commands') {
        if (!methods(['POST'])) return;
        return json(200, await call(url.pathname === '/api/draft' ? 'draft' : 'command', await bodyJSON(request)));
      }
      if (url.pathname === '/api/describe') {
        if (!methods(['GET', 'POST'])) return;
        const handle = url.searchParams.get('handle') || undefined;
        const data = request.method === 'POST' ? await bodyJSON(request) : { handle,
          ...(url.searchParams.has('session') || !handle ? { session } : {}) };
        return json(200, await call('describe', data));
      }
      if (url.pathname === '/api/scripts') {
        if (!methods(['GET'])) return;
        return json(200, await call('scripts'));
      }
      if (url.pathname === '/api/catalog') {
        if (!methods(['GET'])) return;
        return json(200, await call('catalog'));
      }
      if (url.pathname === '/api/products') {
        if (!methods(['GET'])) return;
        return json(200, { products: await call('products') });
      }
      if (url.pathname === '/api/cots') {
        if (!methods(['GET'])) return;
        return json(200, await call('cots_facts', { product: url.searchParams.get('product') }));
      }
      if (url.pathname === '/api/scripts/run') {
        if (!methods(['POST'])) return;
        if (runs.size >= 2) return json(429, { error: 'Two Python runs are already active. Wait for one to finish.' });
        const data = await bodyJSON(request), marker = {};
        if (runs.size >= 2) return json(429, { error: 'Two Python runs are already active. Wait for one to finish.' });
        runs.add(marker);
        try { return json(200, await call('run', data, { timeout: 35000 })); }
        finally { runs.delete(marker); }
      }
      if (url.pathname === '/api/python' || url.pathname === '/api/json') {
        if (!methods(['POST'])) return;
        const native = url.pathname === '/api/python';
        const requestData = await bodyJSON(request);
        const data = await call(native ? 'export_python' : 'export_json', { ...requestData,
          ...(url.searchParams.has('session') || !requestData.handle ? { session } : {}) });
        response.writeHead(200, { 'Content-Type': native ? 'text/x-python; charset=utf-8' : 'application/json; charset=utf-8',
          'Content-Disposition': `attachment; filename="${data.filename}"` });
        return response.end(native ? data.source : JSON.stringify(data.workspace, null, 2) + '\n');
      }
      if (['/api/kicad', '/api/fprime'].includes(url.pathname)) {
        if (!methods(['POST'])) return;
        const requestData = await bodyJSON(request);
        const data = await call('artifacts', { ...requestData,
          ...(url.searchParams.has('session') || !requestData.handle ? { session } : {}) });
        const context = requestData.context;
        const projectName = `eps-${(data.workspace.elements.find(row => row.key === context)?.id ?? 'components').toLowerCase().replace(/[^a-z0-9_-]/g, '_')}`;
        const fprime = url.pathname === '/api/fprime';
        const artifact = fprime ? renderFprimeArchive(data.workspace, context, { products: data.products, validated: true })
          : renderSchematic(data.workspace, context, { products: data.products, projectName,
            componentChecks: data.componentChecks, tabs: data.tabs, validated: true });
        response.writeHead(200, { 'Content-Type': fprime ? 'application/zip' : 'application/octet-stream',
          'Content-Disposition': `attachment; filename="${projectName}${fprime ? '-fprime.zip' : '.kicad_sch'}"` });
        return response.end(artifact);
      }
      const file = publicFiles.get(url.pathname);
      if (!file) return json(404, { error: 'Not found.' });
      if (!methods(['GET', 'HEAD'])) return;
      const content = await readFile(new URL(`../${file[0]}`, import.meta.url));
      response.writeHead(200, { 'Content-Type': file[1] });
      response.end(request.method === 'HEAD' ? undefined : content);
    } catch (error) {
      const status = error.status ?? (error.code ? 500 : 400);
      if (status === 500) console.error(error);
      json(status, { error: status === 500 ? 'Could not read or save the native mission. Check the terminal.' : error.message });
    }
  });
  server.on('close', () => service.close());
  return server;
}

export function startServer() {
  const port = Number(process.env.PORT ?? 3000);
  if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('PORT must be a valid port number.');
  const server = createServer();
  server.on('error', error => {
    console.error(error.code === 'EADDRINUSE' ? `Port ${port} is busy. Try PORT=3001 npm start.` : error.message);
    process.exitCode = 1;
  });
  server.listen(port, '127.0.0.1', () => {
    console.log(`Requirements UI: http://127.0.0.1:${server.address().port}`);
    console.log('Model behavior and session storage use framework.models. Legacy JSON sources are retained.');
  });
  return server;
}
