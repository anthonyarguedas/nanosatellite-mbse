import { createEditor, escape, icon } from '/editor.js';
import { createRecommendations } from '/recommendations.js';

const $ = selector => document.querySelector(selector);
const EXTERNAL = '@external';
let view = null, workspace = null, active = EXTERNAL, mode = '', busy = false, sessions = [], addKind = '', copySession = false, inspection = 0;
const label = name => name.replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/^Cots/, 'COTS ');
const row = path => workspace?.objects.find(item => item.path === path);
const within = (path, owner) => path === owner || path.startsWith(`${owner}.`);
const requestedSession = () => new URLSearchParams(location.search).get('session') || 'current';
const requestedTab = () => { try { return decodeURIComponent(location.hash.slice(1)) || EXTERNAL; } catch { return EXTERNAL; } };
function status(message = '', error = false) {
  $('#status').textContent = message; $('.notice').classList.toggle('error', error); $('#retry').hidden = !error;
}
async function api(path, data) {
  const response = await fetch(path, data === undefined ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || `Request failed (${response.status}).`);
  return result;
}
const request = (path, data = {}) => api(path, { handle: view.handle, revision: view.revision, mode, ...data });
const editor = createEditor({ panel: $('#object-editor'), getWorkspace: () => ({ ...workspace, mode }), request,
  onSave: result => { adopt(result); status('Saved'); }, onClose: () => {} });
const recommendations = createRecommendations({ dialog: $('#recommendations-dialog'), request });
function busyState(value) {
  busy = value; $('#workspace').inert = busy || !workspace;
  document.querySelectorAll('.session-toolbar button, .session-toolbar select').forEach(node => { node.disabled = busy || !workspace; });
  $('#tabs').inert = busy;
}
function adopt(result) {
  view = result; workspace = result.workspace; mode = workspace.mode;
  if (result.sessions) sessions = result.sessions;
  if (!workspace.contexts.some(context => context.path === active)) active = workspace.mission;
  $('#storage').textContent = 'Python · saved';
  render();
}
function badge(result, statementMessage = '') {
  const state = result?.verified === false ? 'fail' : result?.status === 'error' ? 'error' : result?.verified === true ? 'pass' : 'pending';
  const text = { pass: 'Pass', fail: 'Fail', error: 'Error', pending: 'Pending' }[state];
  return `<span class="result" data-state="${state}" title="${escape(result?.failures?.join('\n') || statementMessage)}">${text}</span>`;
}
const pencil = item => `<button class="edit-button" data-edit="${escape(item.path)}" aria-label="Edit ${escape(item.name)}">${icon}</button>`;
const remove = item => `<td class="row-actions"><button class="row-delete" data-remove="${escape(item.path)}" aria-label="Delete ${escape(item.name)}">×</button></td>`;
const nameCell = item => `<td class="name-cell">${item.context ? `<button class="object-link" data-context="${escape(item.path)}">${escape(item.name)}</button>` : `<span class="cell-text">${escape(item.name)}</span>`}${pencil(item)}</td>`;
const empty = (count, text) => `<tr><td colspan="${count}" class="empty">${text}</td></tr>`;
function render() {
  $('#session-select').innerHTML = sessions.map(session => `<option value="${escape(session.id)}" ${session.id === view.session.id ? 'selected' : ''}>${escape(session.name)}</option>`).join('');
  const context = row(active), external = active === EXTERNAL;
  const elements = workspace.objects.filter(item => external ? item.kind === 'external' && item.parent === workspace.mission : item.kind === 'element' && item.parent === active);
  const requirements = workspace.objects.filter(item => item.kind === 'requirement' && (external ? row(item.parent)?.kind === 'external' : item.parent === active));
  const inherited = context?.scopeModes || [];
  const modes = workspace.objects.filter(item => item.kind === 'mode' && (within(item.path, active) || inherited.some(path => within(item.path, path))));
  $('#elements-title').textContent = external ? 'Stakeholders and third parties' : context?.className === 'Mission' ? 'Mission elements' : context?.className === 'Orbit' ? 'Orbit' : `${context?.name || 'Model'} elements`;
  $('#requirements-title').textContent = external ? 'Stakeholder requirements' : 'Requirements';
  $('.elements table').setAttribute('aria-label', external ? 'Stakeholders and third parties' : 'Elements');
  $('#context-edit').hidden = external;
  $('#recommend-cots').hidden = !context?.recommendable;
  $('#context-edit').innerHTML = icon;
  $('#context-edit').dataset.edit = active;
  $('#context-edit').setAttribute('aria-label', `Edit ${context?.name || 'mission'}`);
  $('#element-rows').innerHTML = elements.map(item => `<tr>${remove(item)}${nameCell(item)}<td class="cell-text type-cell">${escape(label(item.className))}</td><td class="check-cell">${badge(item.verification)}</td></tr>`).join('') || empty(4, external ? 'No stakeholders' : 'No elements');
  $('#requirement-rows').innerHTML = requirements.map(item => `<tr>${remove(item)}<td class="cell-text requirement-name">${escape(item.name)}${external ? `<small>${escape(row(item.parent)?.name)}</small>` : ''}</td><td class="statement-cell"><span class="cell-text statement">${escape(item.rendered || item.name)}</span>${pencil(item)}</td><td class="check-cell">${badge(item.verification, item.statementMessage)}</td></tr>`).join('') || empty(4, 'No requirements');
  $('.modes').hidden = external;
  $('#mode-rows').innerHTML = modes.map(item => {
    const values = Object.entries(item.values || {}).map(([name, result]) => {
      const unit = item.properties.find(prop => prop.name === name)?.unit || '';
      return `<span class="mode-value" title="${escape(result.message)}">${escape(name)} <strong>${escape(result.status === 'value' ? `${result.value}${unit ? ` ${unit}` : ''}` : result.status === 'error' ? 'Error' : 'Pending')}</strong></span>`;
    }).join('');
    return `<tr>${remove(item)}<td class="name-cell"><span class="cell-text">${escape(item.name)}<small>${escape(item.parent)}${item.target ? `<br>→ ${escape(item.target)}` : ''}</small></span>${pencil(item)}</td><td class="cell-text type-cell">${escape(label(item.className))}</td><td class="cell-text">${values}</td></tr>`;
  }).join('') || empty(4, 'No modes or states');
  document.querySelectorAll('[data-add]').forEach(button => { button.disabled = !owners(button.dataset.add).length; });
  $('#evaluation-mode').innerHTML = '<option value="">Default</option>' + workspace.modes.map(item => `<option value="${escape(item.path)}" ${item.path === mode ? 'selected' : ''}>${escape(item.path)}</option>`).join('');
  $('#mission-result').innerHTML = badge(workspace.verification);
  const crumbs = external ? [{ path: EXTERNAL, name: 'External' }] : active.split('.').map((name, index, parts) => ({ name, path: parts.slice(0, index + 1).join('.') }));
  $('#breadcrumbs').innerHTML = crumbs.map(item => `<button data-context="${escape(item.path)}" ${item.path === active ? 'aria-current="page"' : ''}>${escape(item.name)}</button>`).join('<span>/</span>');
  const tabs = workspace.contexts.filter(item => item.path === EXTERNAL || item.path === workspace.mission || (row(item.path)?.kind === 'element' && (row(item.path)?.parent === workspace.mission || row(row(item.path)?.parent)?.parent === workspace.mission)));
  if (!tabs.some(item => item.path === active)) tabs.push(workspace.contexts.find(item => item.path === active));
  $('#tabs').innerHTML = tabs.filter(Boolean).map(item => `<button role="tab" data-context="${escape(item.path)}" aria-selected="${item.path === active}" tabindex="${item.path === active ? 0 : -1}">${escape(item.name)}</button>`).join('');
  document.title = `${external ? 'External' : context?.name || 'Mission'} · Mission`;
}
function navigate(path, history = true) {
  if (busy || !workspace.contexts.some(context => context.path === path)) return;
  if (!editor.close()) return;
  inspection++; active = path;
  if (history) window.history.pushState(null, '', `${location.pathname}${location.search}#${encodeURIComponent(path)}`);
  render();
}
async function inspect(path) {
  if (busy || !editor.close()) return;
  const version = ++inspection;
  try {
    const result = await request('/api/inspect', { path });
    if (version === inspection) editor.open(result.workspace.detail);
  } catch (failure) { status(failure.message, true); }
}
async function openSession(id = requestedSession(), updateURL = false) {
  if (busy || !editor.close()) { if (view) $('#session-select').value = view.session.id; return; }
  busyState(true); inspection++; status('Opening mission…');
  try {
    const result = await api(`/api/workspace?session=${encodeURIComponent(id)}`);
    active = requestedTab(); mode = ''; adopt(result);
    if (updateURL) {
      const url = new URL(location); url.searchParams.set('session', id); url.hash = encodeURIComponent(active);
      history.pushState(null, '', url);
    }
    status();
  } catch (failure) { status(failure.message, true); if (view) $('#session-select').value = view.session.id; }
  finally { busyState(false); }
}
function types(owner, kind) {
  return (owner?.types || []).filter(type => kind === 'requirements' ? type.kind === 'requirement'
    : kind === 'modes' ? type.kind === 'mode' : type.kind === (active === EXTERNAL ? 'external' : 'element'));
}
function owners(kind) {
  if (!workspace) return [];
  if (kind === 'elements') { const owner = row(active === EXTERNAL ? workspace.mission : active); return types(owner, kind).length ? [owner] : []; }
  return workspace.objects.filter(item => types(item, kind).length && (active === EXTERNAL ? item.kind === 'external' : kind === 'requirements' ? item.path === active : within(item.path, active)));
}
function updateAddTypes() {
  const owner = row($('#add-owner').value);
  $('#add-type').innerHTML = types(owner, addKind).map(type => `<option value="${escape(type.key)}">${escape(label(type.name))}</option>`).join('');
  updateAddTarget();
}
function updateAddTarget() {
  const type = types(row($('#add-owner').value), addKind).find(item => item.key === $('#add-type').value);
  $('#add-target-field').hidden = !type?.targets.length;
  $('#add-target').innerHTML = (type?.targets || []).map(path => `<option value="${escape(path)}">${escape(path)}</option>`).join('');
}
function openAdd(kind) {
  if (busy || !editor.close()) return;
  addKind = kind; const choices = owners(kind); if (!choices.length) return;
  $('#add-title').textContent = kind === 'requirements' ? 'Add requirement' : kind === 'modes' ? 'Add mode, state or allocation' : active === EXTERNAL ? 'Add stakeholder or third party' : 'Add element';
  $('#add-owner').innerHTML = choices.map(item => `<option value="${escape(item.path)}">${escape(item.path)}</option>`).join('');
  $('#add-name').value = ''; $('#add-error').textContent = ''; updateAddTypes();
  $('#add-dialog').showModal(); $('#add-name').focus();
}
document.addEventListener('click', async event => {
  const context = event.target.closest('[data-context]'); if (context) { navigate(context.dataset.context); return; }
  const edit = event.target.closest('[data-edit]'); if (edit) { inspect(edit.dataset.edit); return; }
  const add = event.target.closest('[data-add]'); if (add) { openAdd(add.dataset.add); return; }
  const remove = event.target.closest('[data-remove]');
  if (remove && !busy) {
    const item = row(remove.dataset.remove);
    if (!editor.close() || !window.confirm(`Delete ${item.path} and its children?`)) return;
    busyState(true);
    try { adopt(await request('/api/commands', { command: { action: 'remove', path: item.path } })); status('Saved'); }
    catch (failure) { status(failure.message, true); }
    finally { busyState(false); }
  }
  if (event.target.closest('[data-close]')) event.target.closest('dialog')?.close();
});
$('#recommend-cots').addEventListener('click', () => {
  if (!busy && editor.close()) { inspection++; recommendations.open(row(active), mode); }
});
$('#add-owner').addEventListener('change', updateAddTypes);
$('#add-type').addEventListener('change', updateAddTarget);
$('#add-form').addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return;
  busyState(true); $('#add-form button[type="submit"]').disabled = true;
  try {
    const result = await request('/api/commands', { command: { action: 'create', owner: $('#add-owner').value,
      type: $('#add-type').value, name: $('#add-name').value.trim(), ...($('#add-target-field').hidden ? {} : { target: $('#add-target').value }) } });
    adopt(result); $('#add-dialog').close(); editor.open(result.workspace.detail); status('Saved');
  } catch (failure) { $('#add-error').textContent = failure.message; }
  finally { busyState(false); $('#add-form button[type="submit"]').disabled = false; }
});
$('#evaluation-mode').addEventListener('change', async event => {
  const previous = mode; mode = event.target.value; busyState(true);
  try { adopt(await request('/api/evaluate')); if (editor.isOpen()) editor.refresh(); status(); }
  catch (failure) { mode = previous; render(); status(failure.message, true); }
  finally { busyState(false); }
});
$('#tabs').addEventListener('keydown', event => {
  const tabs = [...$('#tabs').querySelectorAll('button')], index = tabs.findIndex(tab => tab.getAttribute('aria-selected') === 'true');
  const next = event.key === 'ArrowRight' ? tabs[(index + 1) % tabs.length] : event.key === 'ArrowLeft' ? tabs[(index - 1 + tabs.length) % tabs.length] : event.key === 'Home' ? tabs[0] : event.key === 'End' ? tabs.at(-1) : null;
  if (next) { event.preventDefault(); navigate(next.dataset.context); [...$('#tabs').querySelectorAll('button')].find(tab => tab.dataset.context === next.dataset.context)?.focus(); }
});
$('#session-select').addEventListener('change', event => openSession(event.target.value, true));
$('#refresh').addEventListener('click', () => openSession(view.session.id));
$('#retry').addEventListener('click', () => openSession(view?.session.id || requestedSession()));
for (const [selector, copy] of [['#session-new', false], ['#session-copy', true]]) {
  $(selector).addEventListener('click', () => {
    if (!editor.close()) return;
    copySession = copy; $('#session-title').textContent = copy ? 'Save as' : 'New session';
    $('#session-name').value = ''; $('#session-error').textContent = ''; $('#session-dialog').showModal(); $('#session-name').focus();
  });
}
$('#session-form').addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return;
  busyState(true); $('#session-form button[type="submit"]').disabled = true;
  try {
    const result = await request('/api/sessions', { name: $('#session-name').value, copy: copySession });
    active = result.workspace.mission; adopt(result); $('#session-dialog').close();
    const url = new URL(location); url.searchParams.set('session', result.session.id); url.hash = encodeURIComponent(active); history.pushState(null, '', url);
    status('Saved');
  } catch (failure) { $('#session-error').textContent = failure.message; }
  finally { busyState(false); $('#session-form button[type="submit"]').disabled = false; }
});
$('#export-python').addEventListener('click', async () => {
  if (editor.dirty() && !window.confirm('Download the saved session without unsaved changes?')) return;
  try {
    const response = await fetch('/api/python', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ handle: view.handle, revision: view.revision }) });
    if (!response.ok) throw new Error((await response.json()).error);
    const url = URL.createObjectURL(await response.blob()), link = document.createElement('a');
    link.href = url; link.download = view.filename; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (failure) { status(failure.message, true); }
});
window.addEventListener('popstate', () => {
  if (!workspace || busy) return;
  if (requestedSession() !== view.session.id) openSession(requestedSession());
  else navigate(requestedTab(), false);
});
window.addEventListener('beforeunload', event => { if (editor.dirty()) { event.preventDefault(); event.returnValue = ''; } });
document.addEventListener('keydown', event => { if (event.key === 'Escape' && !document.querySelector('dialog[open]')) editor.close(); });
openSession();
