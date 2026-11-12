// Bounded transport to the GUI's Python application service.
// No workbook rules, expression evaluation or analysis execution live here.
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const sourceBootstrap = fileURLToPath(new URL('../backend/service.py', import.meta.url));
const defaultCots = fileURLToPath(new URL('../../cots/', import.meta.url));
const failure = (message, status = 503) => Object.assign(new Error(message), { status });
const pathValue = value => value instanceof URL ? fileURLToPath(value) : value;

export function createPythonService({ python = process.env.VERIFICATION_PYTHON || 'python3',
  modelPath = process.env.MISSION_FILE, sessionDirectory, cotsDirectory = process.env.NANOSAT_MBSE_COTS_DIR || defaultCots,
  installed = false, path,
  timeoutMs = 7000, maxQueue = 16, maxResponseBytes = 16 * 1024 * 1024 } = {}) {
  let child = null, active = null, sequence = 0, closed = false, buffer = '', stderr = '';
  const queue = [];
  const release = job => {
    clearTimeout(job.timer); job.signal?.removeEventListener('abort', job.abort);
  };
  const disconnect = () => {
    const previous = child;
    child = null; buffer = ''; stderr = '';
    if (!previous) return;
    // Cooperative cancellation and EOF let the native runner clean isolated
    // process groups before bounded termination fallbacks replace the worker.
    try { previous.stdin.end(JSON.stringify({ cancel: 'all' }) + '\n'); } catch { /* Already closed. */ }
    const terminate = setTimeout(() => { try { previous.kill('SIGTERM'); } catch { /* Already exited. */ } }, 500);
    const timer = setTimeout(() => { try { previous.kill('SIGKILL'); } catch { /* Already exited. */ } }, 1500);
    terminate.unref(); timer.unref();
    previous.once('close', () => { clearTimeout(terminate); clearTimeout(timer); });
    previous.stdout.destroy(); previous.stderr.destroy();
  };
  const fail = error => {
    const job = active; active = null; disconnect();
    if (job) { release(job); job.reject(error); }
    if (!closed) queueMicrotask(pump);
  };
  const start = () => {
    const args = ['-I', '-B', '-u', ...(installed ? ['-m', 'framework.gui.backend'] : [pathValue(path || sourceBootstrap)])];
    if (modelPath) args.push('--model', pathValue(modelPath));
    if (sessionDirectory) args.push('--sessions', pathValue(sessionDirectory));
    if (cotsDirectory) args.push('--cots-directory', pathValue(cotsDirectory));
    const processChild = spawn(python, args, { stdio: ['pipe', 'pipe', 'pipe'], env: {
      PATH: process.env.PATH, LANG: 'en_US.UTF-8',
      ...(process.env.SystemRoot ? { SystemRoot: process.env.SystemRoot } : {}),
    } });
    child = processChild;
    processChild.stdout.setEncoding('utf8'); processChild.stderr.setEncoding('utf8');
    processChild.stderr.on('data', text => { if (child === processChild) stderr = (stderr + text).slice(-8000); });
    processChild.stdout.on('data', text => {
      if (child !== processChild) return;
      buffer += text;
      if (Buffer.byteLength(buffer) > maxResponseBytes) return fail(failure('Python service response exceeded its size limit.'));
      let newline;
      while ((newline = buffer.indexOf('\n')) !== -1) {
        const line = buffer.slice(0, newline); buffer = buffer.slice(newline + 1);
        let response;
        try { response = JSON.parse(line); } catch { return fail(failure('Python service returned invalid JSON.')); }
        if (!active || response.id !== active.id || (!response.error && !Object.hasOwn(response, 'result'))) return fail(failure('Python service returned an invalid response.'));
        const job = active; active = null; release(job);
        if (job.aborted) job.reject(failure('Python request was cancelled.', 499));
        else if (response.error) job.reject(Object.assign(new Error(response.error.message), {
          status: response.error.status ?? 400, pending: response.error.pending, scriptKey: response.error.scriptKey,
        }));
        else job.resolve(response.result);
        queueMicrotask(pump);
      }
    });
    processChild.on('error', error => {
      if (child === processChild) fail(failure(`Could not start the Python backend (${error.message}). Set VERIFICATION_PYTHON to a Python 3.8 or later executable.`));
    });
    processChild.on('close', () => {
      if (child === processChild) fail(failure(`Python service exited unexpectedly. Reopen the session.${stderr ? ` ${stderr.trim()}` : ''}`));
    });
    processChild.stdin.on('error', error => { if (child === processChild) fail(failure(`Could not send a Python service request: ${error.message}`)); });
  };
  function pump() {
    if (closed || active || !queue.length) return;
    const job = queue.shift(); active = job; clearTimeout(job.timer);
    try { if (!child) start(); }
    catch (error) { fail(failure(error.message)); return; }
    job.timer = setTimeout(() => fail(failure(`Python service request timed out after ${job.timeoutMs} ms. Reopen the session.`)), job.timeoutMs);
    child.stdin.write(job.packet);
  }
  function request(data, { signal, timeout = data.operation === 'run' ? 35000 : timeoutMs } = {}) {
    if (closed) return Promise.reject(failure('Python service is closed.'));
    if (signal?.aborted) return Promise.reject(failure('Python request was cancelled.', 499));
    if (queue.length >= maxQueue) return Promise.reject(failure('Python service queue is full. Try again shortly.', 429));
    const id = ++sequence;
    let packet;
    try {
      packet = JSON.stringify({ ...data, id }) + '\n';
      if (Buffer.byteLength(packet) > 8 * 1024 * 1024) throw failure('Python service request exceeds 8 MiB.', 413);
    } catch (error) { return Promise.reject(error); }
    return new Promise((resolve, reject) => {
      const job = { id, packet, resolve, reject, signal, timeoutMs: timeout, aborted: false };
      job.abort = () => {
        if (active === job) {
          job.aborted = true;
          clearTimeout(job.timer);
          child?.stdin.write(JSON.stringify({ cancel: job.id }) + '\n');
          job.timer = setTimeout(() => fail(failure('Python request was cancelled.', 499)), 2000);
        } else {
          const index = queue.indexOf(job);
          if (index >= 0) { queue.splice(index, 1); release(job); reject(failure('Python request was cancelled.', 499)); }
        }
      };
      signal?.addEventListener('abort', job.abort, { once: true });
      job.timer = setTimeout(() => {
        const index = queue.indexOf(job);
        if (index >= 0) { queue.splice(index, 1); release(job); reject(failure('Timed out waiting for the Python service.')); }
      }, timeout);
      queue.push(job); pump();
    });
  }
  function close() {
    closed = true;
    if (active) { release(active); active.reject(failure('Python service closed.')); active = null; }
    for (const job of queue.splice(0)) { release(job); job.reject(failure('Python service closed.')); }
    disconnect();
  }
  return { request, close };
}
