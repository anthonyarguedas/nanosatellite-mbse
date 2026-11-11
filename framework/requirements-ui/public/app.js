import {
  allowedDefinitions, allRows as workbookRows, assignableElements, availableSources,
  componentRequirements, contextForRow, parameterExpression, parseTSV, tabsFor,
  verificationMethods, metadata, objectMetadata, hasFixedBudgetScope as fixedScope,
  snapshot as projectionSnapshot, rebase, parameterInfo,
} from '/workbook.js';
import * as native from '/native-client.js';
import { createRequirementEditor } from '/editors/requirement.js';
import { requirementHTML } from '/requirement-preview.js';
import { createPowerEditor } from '/editors/power.js';
import { createCotsEditor } from '/editors/cots.js';

const hasFixedBudgetScope = row => fixedScope(workspace, row);
const main = document.querySelector('main');
const status = document.querySelector('#status'), retry = document.querySelector('#retry');
const sourceEditor = document.querySelector('#source-editor');
const sessionSelect = document.querySelector('#session-select'), sessionEditor = document.querySelector('#session-editor');
const sessionNameInput = document.querySelector('#session-name');
let sessions = [], sessionId = 'current', sessionName = 'Current mission', sessionBusy = false, sessionMode = 'new', suggestedSessionName = '';
let saveTask = null;
const workspaceURL = (id = sessionId) => id === 'current' ? '/api/workspace' : `/api/workspace?session=${encodeURIComponent(id)}`;
const requestedSession = () => new URLSearchParams(location.search).get('session') || 'current';
let catalog = [], products = [], active = 'external', workspace = { version: 14, expressionLanguage: 'python',
  variables: [], elements: [], stakeholders: [], statements: [], components: [], scripts: [], power: { modes: [], loads: [], links: [] } };
let revision, lastSaved, saveTimer, modelName = 'session.py';
let loaded = false, saving = false, conflict = false, exporting = false;
let editor = null, popoverAnchor = null, worker = null, evaluationTimer, workerTimer, generation = 0;
const selected = {}, sorts = {};
let results = new Map(), componentResults = new Map(), scriptResults = null;
let nativeEdits = Promise.resolve();
function enqueue(operation) {
  const task = nativeEdits.catch(() => {}).then(operation);
  nativeEdits = task.catch(() => {});
  return task;
}
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);
const variableNames = () => workspace.variables.map(variable => variable.name);
function captureFocus() {
  const input = document.activeElement, row = input?.closest('tr[data-key]');
  const selector = row && input.dataset.field ? `tr[data-key="${row.dataset.key}"] [data-field="${input.dataset.field}"]`
    : input?.dataset.modeKey ? `[data-mode-key="${input.dataset.modeKey}"][data-mode-field="${input.dataset.modeField}"]`
      : input?.dataset.powerAssignment ? `[data-power-assignment="${input.dataset.powerAssignment}"][data-mode="${input.dataset.mode}"]` : null;
  return selector ? { selector, start: input.selectionStart, end: input.selectionEnd } : null;
}
function restoreFocus(focus) {
  const input = focus && document.querySelector(focus.selector);
  if (!input) return;
  input.focus({ preventScroll: true });
  if (typeof focus.start === 'number') input.setSelectionRange?.(focus.start, focus.end);
}
function adoptCanonical(view, before = workspace) {
  const focus = captureFocus(), canonical = view.workspace?._native ? view.workspace : native.attachView(view, workspace);
  workspace = rebase(workspace, before, canonical);
  workspace._native = canonical._native;
  if (view.catalog) catalog = view.catalog;
  if (view.products) products = view.products;
  if (!tabsFor(workspace).some(tab => tab.key === active)) active = 'external';
  renderWorkbook(); updateSources(); restoreFocus(focus);
}
function commitCandidate(candidate) {
  const captured = structuredClone(workspace), id = sessionId;
  return enqueue(async () => {
    const before = structuredClone(workspace), combined = rebase(workspace, captured, candidate);
    combined._native = candidate._native;
    const view = await native.normalize(combined);
    if (id !== sessionId) throw new Error('The selected session changed while applying the draft.');
    adoptCanonical(view, before);
    scheduleSave(); scheduleEvaluation();
    return workspace;
  });
}
const tabInfo = () => tabsFor(workspace, catalog).find(tab => tab.key === active);
const columns = table => table === 'components' ? ['id', 'product', 'requirements', 'verified']
  : table === 'stakeholders' ? ['id', 'name', active === 'external' ? 'type' : 'definition']
    : ['id', 'sources', 'text', 'verified', ...(active === 'external' ? [] : ['affected'])];
const dataRows = (table, state = workspace) => table === 'components' ? state.components
  : table === 'statements' ? state.statements : active === 'external' ? state.stakeholders : state.elements;
const viewRows = (table, state = workspace) => dataRows(table, state).filter(row => table === 'statements' ? row.context === active : active === 'external' || row.owner === active);
const selectionKey = table => `${active}:${table}`;
const body = table => document.querySelector(`[data-table="${table}"] tbody`);
const rowElement = key => document.querySelector(`tr[data-key="${key}"]`);
const rowByKey = key => workbookRows(workspace).find(row => row.key === key);
const requirementEditor = createRequirementEditor({
  panel: document.querySelector('#requirement-editor'), getWorkspace: () => workspace, getCatalog: () => catalog,
  validate: candidate => candidate,
  getScriptResults: () => scriptResults, getProducts: () => products,
  onInspectCots: (key, name, anchor) => cotsEditor.open(key, anchor, name),
  onBackCots: () => cotsEditor.open(cotsEditor.key()),
  getBackCotsLabel: () => workspace.components.find(component => component.key === cotsEditor.key())?.id ?? '',
  onScriptResults: evidence => { scriptResults = evidence; workspace._native.evidenceToken = evidence?.evidenceToken ?? null; scheduleEvaluation(); },
  onCommit: commitCandidate,
});
const cotsEditor = createCotsEditor({
  panel: document.querySelector('#cots-editor'), getWorkspace: () => workspace, getProducts: () => products,
  getReferenceWorkspace: () => { try { return requirementEditor.preview(); } catch { return workspace; } },
  validate: candidate => candidate,
  beforeOpen: () => { if (!powerEditor.closeWithConfirmation()) return false; requirementEditor.suspend(); return true; },
  onReturn: () => requirementEditor.resume(), returnLabel: () => requirementEditor.id(),
  onCatalogueRefresh: () => { scheduleEvaluation(); requirementEditor.refresh(); },
  canInsert: () => requirementEditor.canInsertCots(), onInsert: reference => requirementEditor.insertCotsReference(reference),
  onOpenRequirement: key => {
    const row = rowByKey(key);
    if (row) { navigate(row.context); requirementEditor.open(key, rowElement(key)?.querySelector('.requirement-edit')); }
    if (!requirementEditor.isVisible()) cotsEditor.resume();
  },
  onCommit: async (candidate, before, after) => {
    await commitCandidate(candidate);
    await requirementEditor.rebaseCots(before, workspace.components.find(component => component.key === after.key));
  },
});
const powerEditor = createPowerEditor({
  section: document.querySelector('#power-workspace'), panel: document.querySelector('#power-editor'),
  getWorkspace: () => workspace, getActive: () => active,
  onError: message => showStatus(message, true),
  onChange: commitCandidate,
  onCommand: operation => enqueue(async () => {
    const before = structuredClone(workspace), view = await native.command(workspace, operation);
    adoptCanonical(view, before); requirementEditor.refresh(); scheduleSave(); scheduleEvaluation();
  }),
  beforeOpen: () => {
    if (requirementEditor.isDirty() && !window.confirm('Discard the unsaved requirement edits and edit component power?')) return false;
    requirementEditor.close(); cotsEditor.suspend(); return true;
  },
});
const rowLabel = row => row.name ?? row.text ?? products.find(product => product.id === row.product)?.name ?? '';
const isEps = () => catalog.find(type => type.model === rowByKey(active)?.definition)?.role === 'eps';
const componentCheck = row => componentResults.get(row.key) ?? { state: 'pending', message: 'Recalculating in Python…' };
function updateExport() {
  document.querySelectorAll('.export-python').forEach(button => { button.disabled = exporting || !loaded || sessionBusy; });
  document.querySelectorAll('.export-kicad, .export-fprime').forEach(button => {
    button.disabled = exporting || sessionBusy || !viewRows('components').some(row => row.product);
  });
}

function requestedTab() {
  let key;
  try { key = decodeURIComponent(location.hash.slice(1)); } catch { key = 'external'; }
  return tabsFor(workspace, catalog).some(tab => tab.key === key) ? key : 'external';
}
function renderTabs() {
  document.querySelector('#tabs').innerHTML = tabsFor(workspace, catalog).map(tab =>
    `<button role="tab" id="tab-${tab.key}" data-tab="${tab.key}" aria-controls="workspace" aria-selected="${tab.key === active}" tabindex="${tab.key === active ? 0 : -1}">${escape(tab.label)}</button>`).join('');
}
function renderWorkbook() {
  const info = tabInfo();
  main.dataset.context = active;
  main.setAttribute('aria-labelledby', `tab-${active}`);
  document.querySelector('#stakeholders-title').textContent = info.leftTitle;
  document.querySelector('#statements-title').textContent = info.requirementsTitle;
  document.querySelector('.stakeholders table').setAttribute('aria-label', info.leftTitle);
  document.querySelector('.statements table').setAttribute('aria-label', info.requirementsTitle);
  document.querySelector('.stakeholders .add-row').setAttribute('aria-label', active === 'external' ? 'Add stakeholder row' : 'Add element row');
  document.querySelector('.stakeholders .menu-toggle').setAttribute('aria-label', active === 'external' ? 'Stakeholder table actions' : 'Element table actions');
  document.querySelector('.stakeholders th:last-child button').dataset.sort = active === 'external' ? 'type' : 'definition';
  document.querySelector('.components').hidden = !isEps();
  renderTabs(); render('stakeholders'); render('statements');
  if (isEps()) render('components');
  powerEditor.render(); updateExport();
}
function navigate(key, history = true) {
  if (!tabsFor(workspace, catalog).some(tab => tab.key === key)) return;
  closeEditor(); closeMenus();
  const changed = active !== key;
  active = key;
  if (history && location.hash !== `#${key}`) window.history.pushState(null, '', `#${encodeURIComponent(key)}`);
  renderWorkbook();
  if (changed) document.querySelectorAll('.table-frame').forEach(frame => { frame.scrollLeft = 0; });
}
document.querySelector('#tabs').addEventListener('click', event => {
  const tab = event.target.closest('[data-tab]');
  if (tab) navigate(tab.dataset.tab);
});
document.querySelector('#tabs').addEventListener('keydown', event => {
  const tabs = tabsFor(workspace, catalog), index = tabs.findIndex(tab => tab.key === active);
  let next;
  if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
  if (event.key === 'ArrowLeft') next = tabs[(index + tabs.length - 1) % tabs.length];
  if (event.key === 'Home') next = tabs[0];
  if (event.key === 'End') next = tabs.at(-1);
  if (next) { event.preventDefault(); navigate(next.key); document.querySelector(`[data-tab="${next.key}"]`).focus(); }
});
window.addEventListener('popstate', () => {
  if (!loaded) return;
  if (requestedSession() !== sessionId) switchSession(requestedSession(), false);
  else if (!sessionBusy) navigate(requestedTab(), false);
});

function draft(table) {
  const common = { key: crypto.randomUUID(), id: '' };
  if (table === 'components') return { ...common, owner: active, product: '', requirements: [] };
  if (table === 'stakeholders') return active === 'external'
    ? { ...common, name: '', type: '' } : { ...common, name: '', definition: '', owner: active };
  return { ...common, context: active, sources: [], affected: [], kind: 'Requirement', text: '', condition: '', rationale: '',
    parameters: Object.fromEntries(variableNames().map(name => [name, null])) };
}
function used(row, table) {
  return table === 'components' ? Boolean(row.id || row.product || row.requirements.length)
    : table === 'stakeholders' ? Boolean(row.id || row.name || row.type || row.definition)
    : Boolean(row.id || row.sources.length || row.affected.length || row.text || row.condition || row.verifications?.length || row.rationale || row.kind !== 'Requirement'
      || Object.values(row.parameters).some(value => value !== null && value !== ''));
}
function snapshot(state = workspace) { return projectionSnapshot(state); }
function sourceHTML(row, index, field = 'sources', col = 1) {
  const links = row[field].map(key => {
    const source = rowByKey(key);
    return source ? `<a href="#row-${key}" data-row-link="${key}" title="${escape(rowLabel(source))}">${escape(source.id)}</a>` : '';
  }).join('');
  const label = field === 'requirements' ? 'affected requirements' : field === 'affected' ? 'affected elements' : 'sources';
  if (field === 'affected' && hasFixedBudgetScope(row)) return `<div class="row-sources ${links ? 'has-sources' : ''}" data-links="affected" data-field="affected" data-col="${col}" tabindex="0" aria-label="Affected elements, row ${index + 1}">${links}</div>`;
  return `<div class="row-sources ${links ? 'has-sources' : ''}" data-links="${field}">${links}<button data-field="${field}" data-col="${col}" class="source-edit" aria-label="Edit ${label}, row ${index + 1}" title="${field === 'requirements' ? 'Link EPS requirements' : field === 'affected' ? 'Assign to elements on the left' : 'Link one or more source rows'}"><span class="chevron"></span></button></div>`;
}
function renderHeader() {
  const table = document.querySelector('.statements table');
  table.style.setProperty('--assignment-width', active === 'external' ? '0px' : '190px');
  table.querySelector('colgroup').innerHTML = '<col class="row-actions-col"><col class="statement-id"><col class="statement-source"><col class="statement-text"><col class="statement-verified">'
    + (active === 'external' ? '' : '<col class="statement-affected">');
  const header = (field, label) => `<th scope="col"><button data-sort="${field}" title="Sort by ${label}">${label}</button></th>`;
  table.querySelector('thead').innerHTML = '<tr><th scope="col" class="row-actions-heading" aria-label="Row actions"></th>'
    + header('id', 'ID') + header('sources', 'Source')
    + header('text', active === 'external' ? 'Requirement, Need, Objective, Concern, Constraint' : 'Requirement')
    + header('verified', 'Verified')
    + (active === 'external' ? '' : header('affected', tabInfo().affectedLabel)) + '</tr>';
}
function elementAction(row) {
  if (active === 'external') return '';
  if (objectMetadata(workspace, row.key).expandable) return `<button type="button" class="element-open" data-open-element="${row.key}" aria-label="Open ${escape(row.name)}" title="Open component and requirement tables">↗</button>`;
  return (metadata(workspace).powerComponents ?? []).includes(row.key) ? `<button type="button" class="element-open" data-open-power="${row.key}" aria-label="Edit power for ${escape(row.name)}" title="Edit component power"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="m12 3 5 5M3 17l4-1 10-10a2.1 2.1 0 0 0-3-3L4 13l-1 4Z"/></svg></button>` : '';
}
function rowHTML(row, table, index) {
  const attrs = (field, col) => `data-field="${field}" data-col="${col}" aria-label="${table === 'components' ? 'COTS component' : table === 'stakeholders' ? active === 'external' ? 'Stakeholder' : 'Element' : 'Statement'} ${field}, row ${index + 1}"`;
  let cells = `<td class="row-actions"><button type="button" class="row-delete" data-delete-row="${row.key}" aria-label="Delete row ${escape(row.id || index + 1)}" title="Delete this row" ${used(row, table) ? '' : 'disabled'}><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 5h12M8 3h4M6 5l1 12h6l1-12M9 8v6M11 8v6"/></svg></button></td>`;
  cells += `<td class="id-cell"><input ${attrs('id', 0)} value="${escape(row.id)}" maxlength="200" title="Display ID, assigned and validated by Python" autocomplete="off" spellcheck="false"></td>`;
  if (table === 'components') {
    cells += `<td class="cots-product-cell"><select ${attrs('product', 1)} title="${escape(rowLabel(row))}"><option value=""> </option>${products.map(product => `<option value="${escape(product.id)}" ${row.product === product.id ? 'selected' : ''}>${escape(product.name)}</option>`).join('')}</select><button type="button" class="requirement-edit" data-cots-edit="${row.key}" aria-label="Edit COTS ${escape(row.id || 'new row')}" aria-controls="cots-editor" title="Inspect COTS facts and named references" ${row.product ? '' : 'disabled'}><svg viewBox="0 0 20 20" aria-hidden="true"><path d="m12 3 5 5M3 17l4-1 10-10a2.1 2.1 0 0 0-3-3L4 13l-1 4Z"/></svg></button></td>`;
    cells += `<td>${sourceHTML(row, index, 'requirements', 2)}</td>`;
    cells += `<td class="checkbox-cell component-summary" tabindex="0" ${attrs('verified', 3)}><input class="verification-result" type="checkbox" disabled tabindex="-1" aria-readonly="true" aria-label="All affected requirements verified, row ${index + 1}"></td>`;
  } else if (table === 'stakeholders') {
    const action = elementAction(row);
    cells += `<td class="${action ? 'element-name-cell' : ''}"><input ${attrs('name', 1)} value="${escape(row.name)}" title="${escape(row.name)}" autocomplete="off">${action}</td>`;
    if (active === 'external') cells += `<td><select ${attrs('type', 2)}><option value=""> </option>${(metadata(workspace).stakeholderTypes ?? []).map(type => `<option ${row.type === type ? 'selected' : ''}>${escape(type)}</option>`).join('')}</select></td>`;
    else {
      const options = allowedDefinitions(workspace, active, catalog), type = catalog.find(type => type.model === row.definition);
      cells += `<td><select ${attrs('definition', 2)} data-category="${escape(type?.category)}" title="${escape(row.definition)}"><option value=""> </option>${options.map(option => `<option value="${option.model}" ${row.definition === option.model ? 'selected' : ''}>${escape(active === 'mission' && option.category !== option.name ? `${option.category} · ${option.name}` : option.name)}</option>`).join('')}</select></td>`;
    }
  } else {
    cells += `<td>${sourceHTML(row, index)}</td>`;
    cells += `<td class="statement-cell"><div class="statement-summary" ${attrs('text', 2)} tabindex="0" contenteditable="false">${active === 'external' && row.kind !== 'Requirement' ? `<span class="statement-kind">${escape(row.kind)}</span>` : ''}<span class="statement-preview">${escape(row.text)}</span></div><button type="button" class="requirement-edit" data-requirement-edit="${row.key}" aria-label="Edit requirement ${escape(row.id || 'new row')}" aria-controls="requirement-editor" title="Edit requirement"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="m12 3 5 5M3 17l4-1 10-10a2.1 2.1 0 0 0-3-3L4 13l-1 4Z"/></svg></button></td>`;
    cells += `<td class="checkbox-cell"><input class="verification-result" type="checkbox" disabled tabindex="-1" aria-readonly="true" aria-label="Verification result, row ${index + 1}"><button type="button" class="requirement-edit verification-edit" data-verification-edit="${row.key}" data-field="verified" data-col="3" aria-label="Edit verification for ${escape(row.id || 'new row')}" aria-controls="requirement-editor" title="Edit requirement verification"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="m12 3 5 5M3 17l4-1 10-10a2.1 2.1 0 0 0-3-3L4 13l-1 4Z"/></svg></button></td>`;
    if (active !== 'external') cells += `<td>${sourceHTML(row, index, 'affected', 4)}</td>`;
  }
  return `<tr id="row-${row.key}" data-key="${row.key}">${cells}</tr>`;
}
function pad(table) {
  while (!viewRows(table).length || used(viewRows(table).at(-1), table)) dataRows(table).push(draft(table));
}
function render(table) {
  pad(table);
  if (table === 'statements') renderHeader();
  body(table).innerHTML = viewRows(table).map((row, index) => rowHTML(row, table, index)).join('');
  if (table === 'statements') viewRows(table).forEach(updatePreview);
  if (table !== 'stakeholders') updateChecks();
  if (table === 'components') updateExport();
}
function addTrailingRows(table) {
  const count = viewRows(table).length; pad(table);
  const rows = viewRows(table);
  for (let i = count; i < rows.length; i++) body(table).insertAdjacentHTML('beforeend', rowHTML(rows[i], table, i));
}
function updateSources() {
  for (const row of [...viewRows('statements'), ...viewRows('components')]) {
    for (const container of rowElement(row.key)?.querySelectorAll('.row-sources') ?? []) {
      const field = container.dataset.links, button = container.querySelector('.source-edit');
      for (const link of container.querySelectorAll('[data-row-link]')) if (!row[field].includes(link.dataset.rowLink)) link.remove();
      for (const key of row[field]) {
        const source = rowByKey(key);
        if (!source) continue;
        let link = container.querySelector(`[data-row-link="${key}"]`);
        if (!link) { link = document.createElement('a'); link.dataset.rowLink = key; link.href = `#row-${key}`; container.insertBefore(link, button); }
        link.textContent = source.id; link.title = rowLabel(source);
      }
      container.classList.toggle('has-sources', row[field].length > 0);
    }
  }
}
function updatePreview(row) {
  const tr = rowElement(row.key), summary = tr?.querySelector('.statement-summary');
  if (!summary) return;
  summary.querySelector('.statement-preview').innerHTML = requirementHTML(row.text, results.get(row.key)?.values, Object.keys(row.parameters).map(name => parameterInfo(workspace, row, name)));
  const issues = objectMetadata(workspace, row.key).draftIssues ?? [];
  summary.title = [row.text || 'Use the edit button to write a requirement.', ...issues].join('\n');
  const errors = [...Object.values(results.get(row.key)?.parameters ?? {}).filter(result => result.state === 'error'), ...issues.map(message => ({ message }))];
  for (const button of tr.querySelectorAll('.requirement-edit')) {
    button.setAttribute('aria-label', `Edit ${button.classList.contains('verification-edit') ? 'verification for' : 'requirement'} ${row.id || 'new row'}`);
    button.dataset.state = errors.length ? 'error' : '';
    button.title = errors.length ? `Edit requirement. ${errors[0].message}` : 'Edit requirement text, parameters and verification condition';
  }
}
function updateChecks() {
  for (const row of viewRows('statements')) {
    const tr = rowElement(row.key), cell = tr?.querySelector('.checkbox-cell');
    if (!cell) continue;
    updatePreview(row);
    const result = verificationMethods(row, workspace).length ? results.get(row.key) ?? { state: 'pending', message: 'Recalculating…' }
      : { state: 'unset', message: 'No verification condition. Enter a Python Boolean expression to verify this row.' };
    const checkbox = cell.querySelector('.verification-result'), edit = cell.querySelector('.verification-edit');
    checkbox.checked = result.state === 'pass'; checkbox.indeterminate = ['error', 'pending'].includes(result.state);
    checkbox.title = result.message;
    edit.title = `${result.message} Open the requirement editor.`;
    edit.setAttribute('aria-description', result.message);
    cell.dataset.state = result.state;
  }
  for (const row of viewRows('components')) {
    const cell = rowElement(row.key)?.querySelector('.component-summary');
    if (!cell) continue;
    const result = componentCheck(row), checkbox = cell.querySelector('input');
    checkbox.checked = result.state === 'pass'; checkbox.indeterminate = ['error', 'pending'].includes(result.state);
    cell.dataset.state = result.state; cell.title = result.message; cell.setAttribute('aria-description', result.message);
  }
}
function scheduleEvaluation() {
  const token = ++generation;
  clearTimeout(evaluationTimer); clearTimeout(workerTimer); results = new Map(); componentResults = new Map(); updateChecks();
  evaluationTimer = setTimeout(() => {
    const statements = workspace.statements.filter(row => used(row, 'statements'));
    const evaluationBase = structuredClone(workspace);
    const fail = message => {
      results = new Map(statements.map(row => [row.key, { state: verificationMethods(row, workspace).length ? 'error' : 'unset', message,
        parameters: Object.fromEntries(Object.entries(row.parameters).map(([name, source]) => [name, { state: source ? 'error' : 'unset', value: null, message }])) }]));
      updateChecks(); worker?.terminate(); worker = null;
    };
    try {
      if (!worker) worker = new Worker('/verification-worker.js', { type: 'module' });
      worker.onmessage = event => {
          if (event.data.token !== generation) return;
          clearTimeout(workerTimer);
          if (event.data.error) { fail(event.data.error); return; }
          if (event.data.view) adoptCanonical(event.data.view, evaluationBase);
          native.applyEvaluation(workspace, event.data);
          results = new Map(event.data.results.map(result => [result.key, result]));
          componentResults = new Map((event.data.components ?? []).map(result => [result.key, result])); updateChecks();
      };
      worker.onerror = () => fail('Could not evaluate the expression.');
      workerTimer = setTimeout(() => fail('Python expression evaluation timed out.'), 7000);
      worker.postMessage({ token, ...native.payload(workspace, scriptResults) });
    } catch { fail('Expression evaluation is unavailable in this browser.'); }
  }, 100);
}
function showStatus(message = '', error = false, action = null) {
  status.textContent = message; status.parentElement.classList.toggle('error', error);
  retry.hidden = !action; retry.textContent = conflict ? 'Reload' : 'Retry'; retry.onclick = action;
}
function dirty() { if (!loaded) return false; try { return JSON.stringify(snapshot()) !== lastSaved; } catch { return true; } }
function scheduleSave() { clearTimeout(saveTimer); if (!conflict && !sessionBusy) { showStatus('Unsaved changes'); saveTimer = setTimeout(save, 450); } }
function save() {
  clearTimeout(saveTimer);
  if (saveTask) return saveTask.then(success => success && dirty() ? save() : success);
  saveTask = enqueue(persist).finally(() => { saveTask = null; });
  return saveTask;
}
async function persist() {
  clearTimeout(saveTimer);
  if (!loaded || saving || conflict) return false;
  let data, serialized;
  const before = structuredClone(workspace);
  try { data = snapshot(); serialized = JSON.stringify(data); }
  catch (error) { showStatus(error.message, true); return false; }
  if (serialized === lastSaved) { showStatus(); return true; }
  const id = sessionId;
  saving = true; showStatus(`Saving ${sessionName}…`);
  let succeeded = false;
  try {
    const response = await fetch(workspaceURL(id), { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...native.payload(before, scriptResults), workspace: data, revision }) });
    const result = await response.json();
    if (!response.ok) { conflict = response.status === 409; throw new Error(result.error); }
    native.attachView(result, workspace);
    revision = result.revision; lastSaved = JSON.stringify(snapshot(result.workspace)); succeeded = true;
    adoptCanonical(result, before); workspace._native.revision = revision;
    document.querySelector('#session-storage').title = `Autosaved separately to ${modelName}.`;
    showStatus(); scheduleEvaluation();
  } catch (error) { showStatus(error.message || 'Could not save. Your edits are still in this tab.', true, conflict ? () => location.reload() : save); }
  finally { saving = false; if (succeeded && dirty()) scheduleSave(); }
  return succeeded;
}
function renderSessions() {
  sessionSelect.innerHTML = sessions.map(session => `<option value="${escape(session.id)}" ${session.id === sessionId ? 'selected' : ''}>${escape(session.name)}</option>`).join('');
}
function setSessionBusy(busy) {
  sessionBusy = busy;
  main.inert = !loaded || busy;
  document.querySelector('#tabs').inert = busy;
  document.querySelector('#requirement-editor').inert = busy;
  document.querySelector('#power-editor').inert = busy;
  document.querySelector('#cots-editor').inert = busy;
  sessionEditor.inert = busy;
  sessionSelect.disabled = busy || !loaded;
  document.querySelectorAll('#session-new, #session-copy').forEach(button => { button.disabled = busy || !loaded; });
  updateExport();
}
function sessionLocation(history = 'replace') {
  const url = new URL(location.href);
  if (sessionId === 'current') url.searchParams.delete('session');
  else url.searchParams.set('session', sessionId);
  url.hash = encodeURIComponent(active);
  window.history[history === 'push' ? 'pushState' : 'replaceState'](null, '', url);
}
function installWorkspace(data, id, tab, history = 'replace') {
  const nextCatalog = data.catalog ?? [], nextProducts = data.products ?? [];
  const candidate = native.attachView(data);
  cotsEditor.close(false); requirementEditor.close(); powerEditor.reset(); closeEditor(); closeMenus();
  clearTimeout(saveTimer); clearTimeout(evaluationTimer); clearTimeout(workerTimer);
  generation++; worker?.terminate(); worker = null; results = new Map(); componentResults = new Map(); scriptResults = null;
  for (const state of [selected, sorts]) for (const key of Object.keys(state)) delete state[key];
  catalog = nextCatalog; products = nextProducts; workspace = candidate;
  sessionId = id; sessionName = data.session?.name ?? data.modelName ?? 'Current mission';
  sessions = data.sessions ?? sessions;
  revision = data.revision; modelName = data.modelName ?? modelName;
  const storage = document.querySelector('#session-storage');
  storage.title = `Autosaved separately to ${modelName}.`;
  lastSaved = JSON.stringify(snapshot()); conflict = false; loaded = true;
  active = tab === 'eps' ? workspace.elements.find(row => catalog.find(type => type.model === row.definition)?.role === 'eps')?.key ?? 'mission'
    : tab ?? requestedTab();
  if (!tabsFor(workspace, catalog).some(item => item.key === active)) active = 'external';
  sessionLocation(history); renderSessions(); renderWorkbook();
  document.title = `${sessionName} · Requirements`;
  showStatus(); scheduleEvaluation();
}
async function load() {
  setSessionBusy(true);
  try {
    const id = requestedSession();
    const [response, listResponse] = await Promise.all([fetch(workspaceURL(id)), fetch('/api/sessions')]);
    const data = await response.json(), list = await listResponse.json();
    if (!response.ok) throw new Error(data.error);
    if (!listResponse.ok) throw new Error('Could not load sessions. Restart the server and reload this page.');
    installWorkspace({ ...data, sessions: list.sessions }, id);
  } catch (error) { showStatus(error.message || 'Could not open the mission model.', true, load); }
  finally { setSessionBusy(false); }
}
async function switchSession(id, history = true) {
  if (sessionBusy || !loaded || id === sessionId) { renderSessions(); if (loaded) sessionLocation(); return; }
  if ((requirementEditor.isDirty() || powerEditor.isDirty() || cotsEditor.isDirty()) && !window.confirm('Discard the unsaved editor changes and switch sessions?')) {
    renderSessions(); sessionLocation(); return;
  }
  setSessionBusy(true); clearTimeout(saveTimer);
  try {
    if (!await save()) return;
    const response = await fetch(workspaceURL(id)), data = await response.json();
    if (!response.ok) throw new Error(data.error);
    installWorkspace(data, id, undefined, history ? 'push' : 'replace');
  } catch (error) { showStatus(error.message || 'Could not open the session.', true); }
  finally { setSessionBusy(false); renderSessions(); if (requestedSession() !== sessionId) sessionLocation(); }
}
function suggestSessionName(base) {
  base = base.slice(0, 70);
  let name = base, suffix = 2;
  while (sessions.some(session => session.name.toLowerCase() === name.toLowerCase())) name = `${base} (${suffix++})`;
  return name;
}
function describeSession() {
  document.querySelector('#session-description').textContent = sessionMode === 'copy'
    ? 'Save an independent copy, including valid open editor drafts. The original session stays available.'
    : 'Empty tables with no preloaded elements or requirements. To reuse an existing session, open it and choose Save as.';
  const name = suggestSessionName(sessionMode === 'copy' ? `${sessionName} copy` : 'Blank session');
  if (!sessionNameInput.value.trim() || sessionNameInput.value === suggestedSessionName) sessionNameInput.value = name;
  suggestedSessionName = name;
}
function openSessionEditor(mode, anchor) {
  if (!loaded || sessionBusy) return;
  sessionMode = mode; sessionNameInput.value = ''; suggestedSessionName = '';
  document.querySelector('#session-editor-title').textContent = mode === 'copy' ? 'Save session as' : 'New session';
  document.querySelector('#session-create').textContent = mode === 'copy' ? 'Save copy' : 'Create session';
  document.querySelector('#session-error').textContent = '';
  describeSession(); openEditor(sessionEditor, anchor, { type: 'session' });
  sessionNameInput.focus(); sessionNameInput.select();
}
async function createSession(event) {
  event.preventDefault();
  if (!loaded || sessionBusy) return;
  const copy = sessionMode === 'copy', tab = active;
  if (!copy && (requirementEditor.isDirty() || powerEditor.isDirty() || cotsEditor.isDirty()) && !window.confirm('Discard the unsaved editor changes and create a new session?')) return;
  setSessionBusy(true); clearTimeout(saveTimer);
  try {
    if (copy) { if (saveTask) await saveTask; }
    else if (!await save()) return;
    const copied = copy ? powerEditor.snapshot(cotsEditor.snapshot(requirementEditor.snapshot())) : null;
    const data = { name: sessionNameInput.value, template: copy ? 'copy' : 'blank',
      ...(copy ? native.payload(copied, scriptResults) : {}) };
    const response = await fetch('/api/sessions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error);
    installWorkspace(result, result.session.id, copy ? tab : 'external', 'push');
  } catch (error) {
    document.querySelector('#session-error').textContent = error.message;
    showStatus(error.message || 'Could not create the session.', true);
  } finally { setSessionBusy(false); if (dirty() && !conflict) scheduleSave(); }
}
sessionSelect.addEventListener('change', () => switchSession(sessionSelect.value));
document.querySelector('#session-new').addEventListener('click', event => openSessionEditor('new', event.currentTarget));
document.querySelector('#session-copy').addEventListener('click', event => openSessionEditor('copy', event.currentTarget));
document.querySelector('#session-form').addEventListener('submit', createSession);
async function exportArtifact(kind) {
  const button = document.querySelector(`.export-${kind}`);
  try {
    const data = powerEditor.snapshot(cotsEditor.snapshot(requirementEditor.snapshot())), context = active;
    exporting = true; updateExport(); button.setAttribute('aria-busy', 'true');
    const response = await fetch(`/api/${kind}?session=${encodeURIComponent(sessionId)}`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...native.payload(data, scriptResults), context }) });
    if (!response.ok) throw new Error((await response.json()).error);
    const blob = await response.blob(), url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = response.headers.get('Content-Disposition')?.match(/filename="([^"]+)"/)?.[1] ?? (kind === 'python' ? 'session.py' : kind === 'kicad' ? 'eps.kicad_sch' : 'eps-fprime.zip');
    document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) { showStatus(error.message || 'Could not export the components.', true); }
  finally { exporting = false; updateExport(); button.removeAttribute('aria-busy'); }
}
function context(target) {
  const tr = target.closest('tr[data-key]'), table = tr?.closest('[data-table]').dataset.table;
  return tr ? { tr, table, row: rowByKey(tr.dataset.key) } : null;
}
function changed(row, table, field) {
  const tr = rowElement(row.key), remove = tr.querySelector('.row-delete');
  remove.disabled = !used(row, table);
  remove.setAttribute('aria-label', `Delete row ${row.id || 'draft'}`);
  if (field !== 'id') tr.querySelector('[data-field="id"]').value = row.id;
  if (table === 'stakeholders') {
    tr.querySelector('[data-field="name"]').title = row.name;
    if (active === 'external') tr.querySelector('[data-field="type"]').value = row.type;
    else {
      const select = tr.querySelector('[data-field="definition"]');
      select.value = row.definition; select.title = row.definition; select.dataset.category = catalog.find(type => type.model === row.definition)?.category ?? '';
      if (field !== 'name') tr.querySelector('[data-field="name"]').value = row.name;
      const cell = tr.querySelector('[data-field="name"]').closest('td'), action = elementAction(row);
      cell.querySelector('.element-open')?.remove(); cell.classList.toggle('element-name-cell', Boolean(action));
      cell.insertAdjacentHTML('beforeend', action);
      renderTabs(); render('statements');
    }
  } else if (table === 'statements') updatePreview(row);
  else {
    tr.querySelector('[data-field="product"]').title = rowLabel(row);
    const button = tr.querySelector('[data-cots-edit]'); button.disabled = !row.product; button.setAttribute('aria-label', `Edit COTS ${row.id || 'new row'}`);
  }
  addTrailingRows(table); powerEditor.render(); cotsEditor.refresh(); requirementEditor.refresh(); updateExport(); scheduleSave(); scheduleEvaluation();
}
main.addEventListener('focusin', event => { const ctx = context(event.target); if (ctx) selected[selectionKey(ctx.table)] = ctx.row.key; });
main.addEventListener('input', event => {
  const field = event.target.dataset.field, ctx = context(event.target);
  if (!field || !ctx || ['sources', 'affected', 'requirements'].includes(field)) return;
  const { row, table } = ctx;
  if (table === 'statements' && field === 'text') return;
  try {
    const variable = workspace.variables.find(variable => variable.name === field);
    if (variable) {
      row.parameters[field] = parameterExpression(event.target.value, variable, row.id);
    } else if (field === 'verified') { updateChecks(); return; }
    else {
      row[field] = event.target.value;
      if (field === 'id') event.target.value = row.id;
      if (field === 'kind') event.target.title = row.kind;
    }
    changed(row, table, field);
  } catch (error) { showStatus(error.message, true); }
});
main.addEventListener('change', updateSources);
function focusCell(table, index, column) {
  if (index < 0) return;
  while (index >= viewRows(table).length) dataRows(table).push(draft(table));
  if (body(table).rows.length !== viewRows(table).length) render(table);
  body(table).rows[index]?.querySelector(`[data-col="${column}"]`)?.focus();
}
main.addEventListener('keydown', event => {
  const ctx = context(event.target);
  if (!ctx) return;
  const { table, row, tr } = ctx, index = viewRows(table).indexOf(row);
  const field = event.target.dataset.field;
  if (table === 'components' && field === 'product' && event.key === 'F2') {
    event.preventDefault(); closeEditor(); closeMenus(); cotsEditor.open(row.key, tr.querySelector('[data-cots-edit]')); return;
  }
  if (table === 'statements' && ((field === 'verified' && event.key === 'F2') || (field === 'text' && ['F2', 'Enter', ' '].includes(event.key)))) {
    event.preventDefault(); closeEditor(); closeMenus();
    if (!powerEditor.closeWithConfirmation()) return;
    cotsEditor.suspend(); requirementEditor.open(row.key, tr.querySelector(field === 'verified' ? '.verification-edit' : '.statement-cell .requirement-edit')); return;
  }
  if (event.target.dataset.col === undefined) return;
  const col = Number(event.target.dataset.col ?? 2);
  if (event.target.tagName === 'SELECT' && event.key !== 'Tab') return;
  if (event.key === 'Tab') {
    if (event.shiftKey && col === 0) {
      const remove = tr.querySelector('.row-delete:not(:disabled)');
      if (remove) { event.preventDefault(); remove.focus(); return; }
    }
    if (table === 'statements' && ((col === 2 && !event.shiftKey) || (col === 3 && event.shiftKey))) return;
    let column = col + (event.shiftKey ? -1 : 1), target = index;
    if (column >= columns(table).length) { column = 0; target++; }
    if (column < 0) { column = columns(table).length - 1; target--; }
    if (target < 0) return;
    event.preventDefault(); focusCell(table, target, column);
  } else if (event.key === 'Enter' && !event.altKey && event.target.tagName !== 'BUTTON') { event.preventDefault(); focusCell(table, index + (event.shiftKey ? -1 : 1), col); }
  else if (['ArrowUp', 'ArrowDown'].includes(event.key) && event.target.tagName !== 'TEXTAREA') { event.preventDefault(); focusCell(table, index + (event.key === 'ArrowUp' ? -1 : 1), col); }
});
function closeMenus() {
  document.querySelectorAll('.table-menu').forEach(menu => { menu.hidden = true; });
  document.querySelectorAll('.menu-toggle').forEach(button => button.setAttribute('aria-expanded', 'false'));
}
function closeEditor(restore = false) {
  document.querySelectorAll('.popover').forEach(popover => { popover.hidden = true; });
  if (restore && popoverAnchor?.isConnected) (popoverAnchor.matches('input,button,textarea,select') ? popoverAnchor : popoverAnchor.querySelector('input,button,textarea,select'))?.focus();
  editor = null; popoverAnchor = null;
}
function openEditor(element, anchor, data) {
  closeEditor(); closeMenus(); editor = data; popoverAnchor = anchor; element.hidden = false;
  const rect = anchor.getBoundingClientRect();
  element.style.left = `${Math.max(12, Math.min(rect.left, innerWidth - element.offsetWidth - 12))}px`;
  element.style.top = `${Math.max(12, rect.bottom + element.offsetHeight + 12 > innerHeight ? rect.top - element.offsetHeight - 6 : rect.bottom + 6)}px`;
}
function renderSourceChoices() {
  const row = rowByKey(editor?.key);
  if (!row) return;
  const query = document.querySelector('#source-search').value.toLowerCase();
  const state = workspace;
  const labels = new Map(tabsFor(workspace, catalog).map(tab => [tab.key, tab.label]));
  const candidates = editor.field === 'requirements' ? componentRequirements(state, row)
    : editor.field === 'affected' ? assignableElements(state, row) : availableSources(state, row.key);
  const requiredSources = editor.field === 'sources' ? objectMetadata(workspace, row.key).requiredSources ?? [] : [];
  const choices = candidates.filter(item => `${item.id} ${rowLabel(item)} ${labels.get(contextForRow(item))}`.toLowerCase().includes(query));
  document.querySelector('#source-choices').innerHTML = choices.length ? choices.map(item => `<label class="source-choice"><input type="checkbox" data-source-key="${item.key}" ${row[editor.field].includes(item.key) ? 'checked' : ''} ${requiredSources.includes(item.key) ? 'disabled' : ''}><span><strong>${escape(item.id)}</strong><span>${escape(labels.get(contextForRow(item)))} · ${escape(rowLabel(item)) || '(empty row)'}</span></span></label>`).join('') : '<p>No matching rows.</p>';
}
function openSources(row, anchor, field = 'sources') {
  if (field === 'affected' && hasFixedBudgetScope(row)) return;
  document.querySelector('#source-search').value = '';
  const label = field === 'requirements' ? 'Link affected EPS requirements' : field === 'affected' ? 'Assign to elements on the left' : 'Link source rows';
  sourceEditor.querySelector('strong').textContent = label; sourceEditor.setAttribute('aria-label', label);
  openEditor(sourceEditor, anchor, { type: 'sources', key: row.key, field, table: field === 'requirements' ? 'components' : 'statements' }); renderSourceChoices(); document.querySelector('#source-search').focus();
}
document.querySelector('#source-search').addEventListener('input', renderSourceChoices);
sourceEditor.addEventListener('change', event => {
  const key = event.target.dataset.sourceKey;
  if (!key) return;
  const row = rowByKey(editor.key), field = editor.field;
  row[field] = event.target.checked ? [...row[field], key] : row[field].filter(source => source !== key);
  changed(row, editor.table, field); updateSources();
});
function insertRow(table) {
  const rows = viewRows(table), collection = dataRows(table), index = rows.findIndex(row => row.key === selected[selectionKey(table)]);
  let insertion = index < 0 ? rows.findIndex(row => !used(row, table)) : index + 1;
  if (index >= 0 && !used(rows[index], table)) insertion = index;
  if (insertion < 0) insertion = rows.length;
  const added = rows[insertion] && !used(rows[insertion], table) ? rows[insertion] : draft(table);
  if (!collection.includes(added)) collection.splice(rows[insertion] ? collection.indexOf(rows[insertion]) : collection.length, 0, added);
  render(table);
  if (table === 'statements') { cotsEditor.suspend(); requirementEditor.open(added.key, rowElement(added.key).querySelector('.requirement-edit')); }
  else focusCell(table, insertion, 1);
}
async function deleteRow(table, key) {
  const row = viewRows(table).find(row => row.key === key);
  if (!row) return;
  if (requirementEditor.isDirty() || cotsEditor.isDirty() || powerEditor.isDirty()) { showStatus('Save or cancel the open editor draft before deleting rows.', true); return; }
  const before = structuredClone(workspace);
  try {
    if (!used(row, table)) dataRows(table).splice(dataRows(table).indexOf(row), 1);
    else {
      const view = await native.command(workspace, { name: 'remove', target: key });
      adoptCanonical(view, before);
    }
    selected[selectionKey(table)] = null;
    renderWorkbook(); requirementEditor.refresh(); updateSources(); scheduleSave(); scheduleEvaluation();
  } catch (error) { showStatus(error.message, true); }
}
main.addEventListener('click', event => {
  const exportButton = event.target.closest('.export-kicad, .export-fprime, .export-python');
  if (exportButton) { closeMenus(); closeEditor(); exportArtifact(exportButton.matches('.export-python') ? 'python' : exportButton.matches('.export-kicad') ? 'kicad' : 'fprime'); return; }
  const openElement = event.target.closest('[data-open-element]');
  if (openElement) { navigate(openElement.dataset.openElement); return; }
  const openPower = event.target.closest('[data-open-power]');
  if (openPower) { powerEditor.open(openPower.dataset.openPower); return; }
  const cots = event.target.closest('[data-cots-edit]');
  if (cots) { event.preventDefault(); closeMenus(); closeEditor(); cotsEditor.open(cots.dataset.cotsEdit, cots); return; }
  const ctx = context(event.target), link = event.target.closest('[data-row-link]');
  const requirement = event.target.closest('.requirement-edit');
  if (requirement) { event.preventDefault(); if (!powerEditor.closeWithConfirmation()) return; closeMenus(); closeEditor(); cotsEditor.suspend(); requirementEditor.open(ctx.row.key, requirement); return; }
  const remove = event.target.closest('[data-delete-row]');
  if (remove) {
    event.preventDefault();
    if (!remove.disabled && ctx) { closeMenus(); closeEditor(); deleteRow(ctx.table, remove.dataset.deleteRow); }
    return;
  }
  if (link) {
    event.preventDefault(); const key = link.dataset.rowLink, linked = rowByKey(key);
    if (linked) navigate(contextForRow(linked));
    const target = rowElement(key); target?.scrollIntoView({ block: 'center', inline: 'nearest' }); target?.querySelector('input')?.focus(); return;
  }
  const sourceCell = event.target.closest('.row-sources');
  if (sourceCell) { openSources(ctx.row, event.target.closest('td'), sourceCell.dataset.links); return; }
  const section = event.target.closest('section[data-table]');
  if (!section) return;
  const table = section.dataset.table, toggle = event.target.closest('.menu-toggle');
  if (toggle) { const open = toggle.getAttribute('aria-expanded') !== 'true'; closeMenus(); closeEditor(); toggle.setAttribute('aria-expanded', String(open)); section.querySelector('.table-menu').hidden = !open; return; }
  const action = event.target.closest('[data-action]')?.dataset.action;
  if (action === 'add' || event.target.closest('.add-row')) { closeMenus(); closeEditor(); insertRow(table); }
  const sort = event.target.closest('[data-sort]');
  if (sort) {
    const key = selectionKey(table), field = sort.dataset.sort, direction = sorts[key]?.field === field ? -sorts[key].direction : 1;
    sorts[key] = { field, direction };
    const value = row => variableNames().includes(field) ? results.get(row.key)?.values?.[field]
      : ['sources', 'affected', 'requirements'].includes(field) ? row[field].map(key => rowByKey(key)?.id ?? '').join(',')
        : field === 'verified' ? (table === 'components' ? componentCheck(row) : results.get(row.key))?.state === 'pass'
          : field === 'product' ? rowLabel(row) : row[field];
    const current = viewRows(table), collection = dataRows(table);
    const sorted = current.filter(row => used(row, table)).sort((a, b) => {
      const left = value(a), right = value(b);
      if (variableNames().includes(field)) {
        if (left == null || right == null) return left == right ? 0 : left == null ? 1 : -1;
        return direction * (left - right);
      }
      return direction * String(left ?? '').localeCompare(String(right ?? ''), undefined, { numeric: true });
    });
    const retained = collection.filter(row => !current.includes(row)); collection.splice(0, collection.length, ...retained, ...sorted);
    render(table); document.querySelectorAll(`[data-table="${table}"] th`).forEach(th => th.removeAttribute('aria-sort'));
    const heading = document.querySelector(`[data-table="${table}"] [data-sort="${field}"]`);
    heading?.closest('th').setAttribute('aria-sort', direction === 1 ? 'ascending' : 'descending');
    if (heading) heading.title = `Sorted ${direction === 1 ? 'ascending' : 'descending'}. Click to reverse.`;
    scheduleSave();
  }
});
document.addEventListener('click', event => {
  if (event.target.closest('[data-close]')) closeEditor(true);
  else if (!event.target.closest('.popover') && !popoverAnchor?.contains(event.target)) closeEditor();
  if (!event.target.closest('.table-top')) closeMenus();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    const transient = editor || document.querySelector('.table-menu:not([hidden])');
    closeMenus(); closeEditor(true);
    if (!transient) { if (cotsEditor.isVisible()) cotsEditor.close(); else { requirementEditor.close(); powerEditor.close(); } }
  }
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 's') {
    event.preventDefault();
    if (editor?.type === 'session') document.querySelector('#session-form').requestSubmit();
    else if (cotsEditor.isVisible()) cotsEditor.save();
    else if (powerEditor.isOpen()) powerEditor.save();
    else if (requirementEditor.isOpen()) requirementEditor.save();
    else save();
  }
});
main.addEventListener('paste', async event => {
  const ctx = context(event.target), text = event.clipboardData.getData('text/plain');
  if (!ctx || event.target.dataset.col === undefined || (!['sources', 'affected', 'requirements', 'verified', 'text'].includes(event.target.dataset.field) && !text.includes('\t') && (!/[\r\n]/.test(text) || event.target.tagName === 'TEXTAREA'))) return;
  event.preventDefault();
  const { table, row } = ctx, start = viewRows(table).indexOf(row), column = Number(event.target.dataset.col ?? 0);
  const candidate = structuredClone(workspace), links = [], targets = viewRows(table, candidate);
  try {
    for (const [offset, cells] of parseTSV(text).entries()) {
      while (targets.length <= start + offset) { const row = draft(table); dataRows(table, candidate).push(row); targets.push(row); }
      const target = targets[start + offset];
      for (const [cellIndex, value] of cells.entries()) {
        const field = columns(table)[column + cellIndex], variable = workspace.variables.find(variable => variable.name === field);
        if (!field) throw new Error('The pasted cells extend past the last column.');
        if (table === 'statements' && ['text', 'verified'].includes(field)) throw new Error('Edit requirement text and verification only in the requirement pane.');
        if (['sources', 'affected', 'requirements'].includes(field)) links.push([target, field, value.trim()]);
        else if (field === 'product') {
          const matches = products.filter(product => [product.id, product.name, product.partNumber].includes(value.trim()));
          if (matches.length !== 1) throw new Error('Choose one component from the COTS catalog.');
          target.product = matches[0].id;
        } else if (field === 'verified' && table === 'components') throw new Error('Component verification is calculated from affected requirements.');
        else if (field === 'definition') {
          const matches = allowedDefinitions(candidate, active, catalog).filter(type => [type.model, type.name, type.category].includes(value.trim()));
          if (matches.length !== 1) throw new Error('The element type must match one definition in the generic mission model.');
          target.definition = matches[0].model;
        } else if (variable) target.parameters[field] = parameterExpression(value, variable, target.id);
        else target[field] = field === 'id' ? value.trim() : value;
      }
    }
    for (const [target, field, label] of links) {
      target[field] = [];
      for (const item of label.split(/[,;]+/).map(value => value.trim()).filter(Boolean)) {
        const rows = field === 'requirements' ? componentRequirements(candidate, target)
          : field === 'affected' ? assignableElements(candidate, target) : workbookRows(candidate);
        let matches = rows.filter(row => row.id === item);
        if (!matches.length) matches = rows.filter(row => row.name === item);
        if (matches.length !== 1) throw new Error(`Source or assignment “${item}” must match one row ID or a unique element name.`);
        if (!target[field].includes(matches[0].key)) target[field].push(matches[0].key);
      }
    }
    await commitCandidate(candidate);
    focusCell(table, start, column);
  } catch (error) { showStatus(error.message, true); }
});
window.addEventListener('beforeunload', event => { if (dirty() || requirementEditor.isDirty() || powerEditor.isDirty() || cotsEditor.isDirty()) { event.preventDefault(); event.returnValue = ''; } });
document.addEventListener('visibilitychange', () => { if (document.hidden && dirty()) save(); });
load();
