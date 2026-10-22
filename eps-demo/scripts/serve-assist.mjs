#!/usr/bin/env node
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const script = fileURLToPath(new URL('../src/mission-assist/serve_semantic.py', import.meta.url));
const researchPython = fileURLToPath(new URL('../../embeddings/.venv/bin/python', import.meta.url));
const researchCache = fileURLToPath(new URL('../../embeddings/.cache/huggingface', import.meta.url));
const python = process.env.EPS_PYTHON || (existsSync(researchPython) ? researchPython : 'python3');
const args = [script];
if (!process.env.HF_HOME && existsSync(researchCache)) args.push('--hf-home', researchCache);
args.push('--allow-origin', 'http://127.0.0.1:5173', '--allow-origin', 'http://localhost:5173', '--allow-origin', 'http://127.0.0.1:4173', '--allow-origin', 'http://localhost:4173', ...process.argv.slice(2));
const child = spawn(python, args, { stdio: 'inherit', env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1', HF_HUB_OFFLINE: '1', TRANSFORMERS_OFFLINE: '1' } });
child.on('error', error => { console.error(`Local semantic service could not start: ${error.message}. Use the offline lexical mode or configure EPS_PYTHON.`); process.exitCode = 1; });
child.on('exit', (code, signal) => { process.exitCode = signal ? 0 : (code ?? 1); });
for (const signal of ['SIGINT', 'SIGTERM', 'SIGHUP']) process.on(signal, () => child.kill(signal));
