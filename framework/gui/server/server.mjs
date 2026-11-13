// Local HTTP transport. Engineering operations execute in framework.models.
import { createServer as httpServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createPythonService } from './python-client.mjs';

const files = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
  ['/editor.js', ['editor.js', 'text/javascript; charset=utf-8']],
  ['/style.css', ['style.css', 'text/css; charset=utf-8']],
]);

async function bodyJSON(request) {
  if (request.headers['content-type']?.split(';')[0].trim().toLowerCase() !== 'application/json') {
    throw Object.assign(new Error('Send application/json.'), { status: 415 });
  }
  const chunks = []; let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 8 * 1024 * 1024) throw Object.assign(new Error('Request exceeds 8 MiB.'), { status: 413 });
    chunks.push(chunk);
  }
  const data = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Send one JSON object.');
  return data;
}

export function createServer({ modelPath = process.env.MISSION_FILE ? resolve(process.env.MISSION_FILE) : undefined,
  sessionDirectory, python = process.env.VERIFICATION_PYTHON || 'python3', installed = false } = {}) {
  const service = createPythonService({ modelPath, sessionDirectory, python, installed });
  const server = httpServer(async (request, response) => {
    response.setHeader('Cache-Control', 'no-store');
    response.setHeader('X-Content-Type-Options', 'nosniff');
    response.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'");
    const json = (status, data) => {
      if (response.destroyed) return;
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
      let operation;
      if (url.pathname === '/api/workspace' && request.method === 'GET') operation = 'open';
      if (url.pathname === '/api/sessions') operation = request.method === 'GET' ? 'sessions' : request.method === 'POST' ? 'create' : null;
      const routes = { '/api/commands': 'command', '/api/preview': 'preview', '/api/inspect': 'inspect',
        '/api/evaluate': 'evaluate', '/api/python': 'export_python' };
      if (routes[url.pathname] && request.method === 'POST') operation = routes[url.pathname];
      if (operation) {
        const data = request.method === 'GET' ? { session: url.searchParams.get('session') || 'current' } : await bodyJSON(request);
        const result = await service.request({ ...data, operation });
        if (operation === 'export_python') {
          response.writeHead(200, { 'Content-Type': 'text/x-python; charset=utf-8',
            'Content-Disposition': `attachment; filename="${result.filename.replace(/[^a-zA-Z0-9_.-]/g, '_')}"` });
          return response.end(result.source);
        }
        return json(operation === 'create' ? 201 : 200, result);
      }
      if (url.pathname.startsWith('/api/')) return json(405, { error: 'Unknown route or method.' });
      const file = files.get(url.pathname);
      if (!file) return json(404, { error: 'Not found.' });
      if (!['GET', 'HEAD'].includes(request.method)) return json(405, { error: 'Method not allowed.' });
      const content = await readFile(new URL(`../public/${file[0]}`, import.meta.url));
      response.writeHead(200, { 'Content-Type': file[1] });
      response.end(request.method === 'HEAD' ? undefined : content);
    } catch (error) {
      const status = error.status ?? 400;
      if (status === 500) console.error(error);
      json(status, { error: error.message });
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
  server.listen(port, '127.0.0.1', () => console.log(`Mission UI: http://127.0.0.1:${server.address().port}`));
  return server;
}
