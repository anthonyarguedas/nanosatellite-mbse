// Native capabilities are retained beside browser drafts, never inside storage.
import { snapshot } from '/workbook.js';

export async function request(path, data, options = {}) {
  const response = await fetch(path, { ...options, method: options.method ?? 'POST',
    headers: { 'Content-Type': 'application/json', ...options.headers }, body: data === undefined ? undefined : JSON.stringify(data) });
  const result = await response.json();
  if (!response.ok) throw Object.assign(new Error(result.error || 'The native operation failed.'), { status: response.status });
  return result;
}
export function attachView(view, previous) {
  const state = view.workspace;
  state._native = { handle: view.handle, metadata: view.metadata, calculationSignature: view.calculationSignature,
    revision: view.revision, writable: view.writable, session: view.session?.id,
    evidenceToken: previous?._native?.evidenceToken ?? null,
    evidenceCurrent: previous?._native?.calculationSignature === view.calculationSignature && previous?._native?.evidenceCurrent === true,
    stateEdits: [] };
  return state;
}
export function payload(state, evidence = null) {
  if (!state?._native?.handle) throw new Error('Reopen the session to obtain a native draft handle.');
  return { handle: state._native.handle, workspace: snapshot(state), stateEdits: state._native.stateEdits ?? [],
    evidenceToken: evidence?.evidenceToken ?? state._native.evidenceToken ?? undefined };
}
export async function normalize(state) {
  const view = await request('/api/draft', payload(state));
  attachView(view, state);
  return view;
}
export async function command(state, operation) {
  const draft = await normalize(state);
  const view = await request('/api/commands', { handle: draft.handle, command: operation });
  attachView(view, state);
  return view;
}
export function applyEvaluation(state, result) {
  Object.assign(state._native, { calculationSignature: result.calculationSignature,
    evidenceCurrent: result.evidenceCurrent === true });
}
export function applyEvidence(state, evidence) {
  Object.assign(state._native, { handle: evidence.handle, evidenceToken: evidence.evidenceToken,
    calculationSignature: evidence.calculationSignature, evidenceCurrent: evidence.evidenceCurrent === true });
}
export async function run(state, script, evidence, signal) {
  const view = await normalize(state);
  const result = await request('/api/scripts/run', { handle: view.handle, script,
    evidenceToken: evidence?.evidenceToken ?? state._native.evidenceToken ?? undefined }, { signal });
  applyEvidence(view.workspace, result);
  return { view, evidence: result };
}
