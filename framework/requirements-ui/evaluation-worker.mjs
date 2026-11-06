import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { scriptContext } from './verification-methods.mjs';

const workerFile = fileURLToPath(new URL('./worker/main.py', import.meta.url));
const failure = (message, status = 503) => Object.assign(new Error(message), { status });

export function evaluationRequest(workspace, { scriptResults, mode, ...options } = {}) {
  const runs = scriptResults?.signature === scriptContext(workspace) ? scriptResults.runs : {};
  return { operation: 'evaluate', workspace, runs,
    ...(mode !== undefined ? { mode } : {}), ...options };
}

// One supervised interpreter per server. Requests are serialized, bounded and
// independent. A timeout, cancellation or protocol error replaces the process.
export function createEvaluationWorker({ python = process.env.VERIFICATION_PYTHON || 'python3',
  path = workerFile, timeoutMs = 4000, maxQueue = 16, maxResponseBytes = 16 * 1024 * 1024 } = {}) {
  let child = null, active = null, sequence = 0, closed = false, buffer = '', stderr = '';
  const queue = [];
  const release = job => {
    clearTimeout(job.timer); job.signal?.removeEventListener('abort', job.abort);
  };
  const disconnect = () => {
    const previous = child;
    child = null; buffer = ''; stderr = '';
    if (previous) { previous.stdin.destroy(); previous.stdout.destroy(); previous.stderr.destroy(); previous.kill('SIGKILL'); }
  };
  const fail = error => {
    const job = active; active = null;
    disconnect();
    if (job) { release(job); job.reject(error); }
    if (!closed) queueMicrotask(pump);
  };
  const start = () => {
    const process = spawn(python, ['-I', '-B', '-u', path], { stdio: ['pipe', 'pipe', 'pipe'], env: {
      PATH: globalThis.process.env.PATH, LANG: 'en_US.UTF-8',
      ...(globalThis.process.env.SystemRoot ? { SystemRoot: globalThis.process.env.SystemRoot } : {}),
    } });
    child = process;
    process.stdout.setEncoding('utf8'); process.stderr.setEncoding('utf8');
    process.stderr.on('data', text => { if (child === process) stderr = (stderr + text).slice(-8000); });
    process.stdout.on('data', text => {
      if (child !== process) return;
      buffer += text;
      if (Buffer.byteLength(buffer) > maxResponseBytes) return fail(failure('Python evaluation response exceeded its size limit.'));
      let newline;
      while ((newline = buffer.indexOf('\n')) !== -1) {
        const line = buffer.slice(0, newline); buffer = buffer.slice(newline + 1);
        let response;
        try { response = JSON.parse(line); } catch { return fail(failure('Python evaluation worker returned invalid JSON.')); }
        if (!active || response.id !== active.id || (!response.error && !Object.hasOwn(response, 'result'))) return fail(failure('Python evaluation worker returned an invalid response.'));
        const job = active; active = null; release(job);
        if (response.error) job.reject(Object.assign(new Error(response.error.message), { pending: response.error.pending, scriptKey: response.error.scriptKey, status: 400 }));
        else job.resolve(response.result);
        // Pump after the current chunk is checked, so stray output cannot be
        // mistaken for a queued request's response.
        queueMicrotask(pump);
      }
    });
    process.on('error', error => {
      if (child === process) fail(failure(`Could not start Python evaluation (${error.message}). Set VERIFICATION_PYTHON to a Python 3.8 or later executable.`));
    });
    process.on('close', () => {
      if (child === process) fail(failure(`Python evaluation worker exited unexpectedly.${stderr ? ` ${stderr.trim()}` : ''}`));
    });
    process.stdin.on('error', error => { if (child === process) fail(failure(`Could not send a Python evaluation request: ${error.message}`)); });
  };
  function pump() {
    if (closed || active || !queue.length) return;
    const job = queue.shift(); active = job; clearTimeout(job.timer);
    try { if (!child) start(); }
    catch (error) { fail(failure(error.message)); return; }
    job.timer = setTimeout(() => fail(failure(`Python expression evaluation timed out after ${job.timeoutMs} ms.`)), job.timeoutMs);
    child.stdin.write(job.packet);
  }
  function request(data, { signal, timeout = timeoutMs } = {}) {
    if (closed) return Promise.reject(failure('Python evaluation worker is closed.'));
    if (signal?.aborted) return Promise.reject(failure('Python evaluation was cancelled.', 499));
    if (queue.length >= maxQueue) return Promise.reject(failure('Python evaluation queue is full. Try again shortly.', 429));
    let packet;
    const id = ++sequence;
    try {
      packet = JSON.stringify({ ...data, id }) + '\n';
      if (Buffer.byteLength(packet) > 8 * 1024 * 1024) throw failure('Python evaluation request exceeds 8 MiB.', 413);
    } catch (error) { return Promise.reject(error); }
    return new Promise((resolve, reject) => {
      const job = { id, packet, resolve, reject, signal, timeoutMs: timeout };
      job.abort = () => {
        if (active === job) fail(failure('Python evaluation was cancelled.', 499));
        else {
          const index = queue.indexOf(job);
          if (index >= 0) { queue.splice(index, 1); release(job); reject(failure('Python evaluation was cancelled.', 499)); }
        }
      };
      signal?.addEventListener('abort', job.abort, { once: true });
      job.timer = setTimeout(() => {
        const index = queue.indexOf(job);
        if (index >= 0) { queue.splice(index, 1); release(job); reject(failure('Timed out waiting for the Python evaluation worker.')); }
      }, timeout);
      queue.push(job); pump();
    });
  }
  function close() {
    closed = true;
    if (active) { release(active); active.reject(failure('Python evaluation worker closed.')); active = null; }
    for (const job of queue.splice(0)) { release(job); job.reject(failure('Python evaluation worker closed.')); }
    disconnect();
  }
  return { request, close, evaluate: (workspace, options = {}, control = {}) => request(evaluationRequest(workspace, options), control) };
}
