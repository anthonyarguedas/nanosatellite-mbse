import {
  addElementChildren, allowedDefinitions, allRows as workbookRows, assignableElements, availableSources,
  componentCheck, componentRequirements, contextForRow, domainTypes, emptyWorkspace,
  nextId, parameterExpression, parseTSV, WORKSPACE_VERSION, rewriteRowReferences, stakeholderTypes, tabsFor, validateWorkspace,
} from '/model.mjs';
import { createRequirementEditor } from '/requirement-editor.js';
import { requirementHTML } from '/requirement-preview.js';

const main = document.querySelector('main');
const status = document.querySelector('#status'), retry = document.querySelector('#retry');
const sourceEditor = document.querySelector('#source-editor');
let catalog = domainTypes, products = [], active = 'external', workspace = emptyWorkspace(catalog);
let revision, lastSaved, saveTimer, modelName = 'mission.sysml';
let loaded = false, saving = false, conflict = false, exporting = false;
let editor = null, popoverAnchor = null, worker = null, evaluationTimer, workerTimer, generation = 0;
const selected = {}, sorts = {}, statementIds = new Map();
let results = new Map();
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);
const variableNames = () => workspace.variables.map(variable => variable.name);
function syncStatementIds(state = workspace, known = statementIds) {
  const renames = new Map();
  for (const row of state.statements) {
    if (!/^[A-Z]{3}\d{3}$/.test(row.id) || state.statements.some(other => other.key !== row.key && other.id === row.id)) continue;
    const previous = known.get(row.key);
    if (previous && previous !== row.id) renames.set(previous, row.id);
    known.set(row.key, row.id);
  }
  rewriteRowReferences(state, renames);
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
  validate: candidate => validateWorkspace(snapshot(candidate), catalog, products),
  onCommit: candidate => {
    workspace = candidate; statementIds.clear(); syncStatementIds();
    renderWorkbook(); updateSources(); scheduleSave(); scheduleEvaluation();
  },
});
const rowLabel = row => row.name ?? row.text ?? products.find(product => product.id === row.product)?.name ?? '';
const isEps = () => catalog.find(type => type.model === rowByKey(active)?.definition)?.role === 'eps';
const componentChecks = () => new Map(workspace.statements.map(row => [row.key,
  row.condition.trim() ? results.get(row.key) ?? { state: 'pending' } : { state: 'unset' }]));
function updateExport() {
  document.querySelector('.export-sysml').disabled = exporting || !loaded;
  document.querySelectorAll('.export-kicad, .export-fprime').forEach(button => {
    button.disabled = exporting || !viewRows('components').some(row => row.product);
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
  updateExport();
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
window.addEventListener('popstate', () => { if (loaded) navigate(requestedTab(), false); });

function draft(table) {
  const common = { key: crypto.randomUUID(), id: '' };
  if (table === 'components') return { ...common, owner: active, product: '', requirements: [] };
  if (table === 'stakeholders') return active === 'external'
    ? { ...common, name: '', type: '' } : { ...common, name: '', definition: '', owner: active };
  return { ...common, context: active, sources: [], affected: [], kind: 'Requirement', text: '', condition: '',
    parameters: Object.fromEntries(variableNames().map(name => [name, null])) };
}
function used(row, table) {
  return table === 'components' ? Boolean(row.id || row.product || row.requirements.length)
    : table === 'stakeholders' ? Boolean(row.id || row.name || row.type || row.definition)
    : Boolean(row.id || row.sources.length || row.affected.length || row.text || row.condition || row.kind !== 'Requirement'
      || Object.values(row.parameters).some(value => value !== null && value !== ''));
}
function snapshot(state = workspace) {
  return {
    version: WORKSPACE_VERSION, variables: structuredClone(state.variables),
    stakeholders: state.stakeholders.filter(row => used(row, 'stakeholders')).map(row => ({ key: row.key, id: row.id.trim(), name: row.name, type: row.type })),
    elements: state.elements.filter(row => used(row, 'stakeholders')).map(row => ({ key: row.key, id: row.id.trim(), name: row.name, owner: row.owner, definition: row.definition })),
    components: state.components.filter(row => used(row, 'components')).map(row => ({
      key: row.key, id: row.id.trim(), owner: row.owner, product: row.product, requirements: [...row.requirements],
    })),
    statements: state.statements.filter(row => used(row, 'statements')).map(row => ({
      key: row.key, id: row.id.trim(), context: row.context, sources: [...row.sources], affected: [...row.affected], kind: row.kind, text: row.text,
      condition: row.condition,
      ...(row.definition ? { definition: row.definition } : {}),
      ...(row.origin ? { origin: row.origin } : {}),
      parameters: Object.fromEntries(state.variables.map(variable => [variable.name, parameterExpression(row.parameters[variable.name], variable, row.id)])),
    })),
  };
}
function sourceHTML(row, index, field = 'sources', col = 1) {
  const links = row[field].map(key => {
    const source = rowByKey(key);
    return source ? `<a href="#row-${key}" data-row-link="${key}" title="${escape(rowLabel(source))}">${escape(source.id)}</a>` : '';
  }).join('');
  const label = field === 'requirements' ? 'affected requirements' : field === 'affected' ? 'affected elements' : 'sources';
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
function rowHTML(row, table, index) {
  const attrs = (field, col) => `data-field="${field}" data-col="${col}" aria-label="${table === 'components' ? 'COTS component' : table === 'stakeholders' ? active === 'external' ? 'Stakeholder' : 'Element' : 'Statement'} ${field}, row ${index + 1}"`;
  let cells = `<td class="row-actions"><button type="button" class="row-delete" data-delete-row="${row.key}" aria-label="Delete row ${escape(row.id || index + 1)}" title="Delete this row" ${used(row, table) ? '' : 'disabled'}><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 5h12M8 3h4M6 5l1 12h6l1-12M9 8v6M11 8v6"/></svg></button></td>`;
  cells += `<td class="id-cell"><input ${attrs('id', 0)} value="${escape(row.id)}" maxlength="${table === 'stakeholders' ? 3 : 6}" title="${table === 'stakeholders' ? 'Three uppercase letters' : 'Three uppercase letters and three digits'}" autocomplete="off" spellcheck="false"></td>`;
  if (table === 'components') {
    cells += `<td><select ${attrs('product', 1)} title="${escape(rowLabel(row))}"><option value=""> </option>${products.map(product => `<option value="${escape(product.id)}" ${row.product === product.id ? 'selected' : ''}>${escape(product.name)}</option>`).join('')}</select></td>`;
    cells += `<td>${sourceHTML(row, index, 'requirements', 2)}</td>`;
    cells += `<td class="checkbox-cell component-summary" tabindex="0" ${attrs('verified', 3)}><input class="verification-result" type="checkbox" disabled tabindex="-1" aria-readonly="true" aria-label="All affected requirements verified, row ${index + 1}"></td>`;
  } else if (table === 'stakeholders') {
    cells += `<td><input ${attrs('name', 1)} value="${escape(row.name)}" title="${escape(row.name)}" autocomplete="off"></td>`;
    if (active === 'external') cells += `<td><select ${attrs('type', 2)}><option value=""> </option>${stakeholderTypes.map(type => `<option ${row.type === type.name ? 'selected' : ''}>${type.name}</option>`).join('')}</select></td>`;
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
  summary.querySelector('.statement-preview').innerHTML = requirementHTML(row.text, results.get(row.key)?.values, workspace.variables);
  summary.title = [row.text, row.origin].filter(Boolean).join('\n') || 'Use the edit button to write a requirement.';
  const errors = Object.values(results.get(row.key)?.parameters ?? {}).filter(result => result.state === 'error');
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
    const result = row.condition.trim() ? results.get(row.key) ?? { state: 'pending', message: 'Recalculating…' }
      : { state: 'unset', message: 'No SysML condition. Enter a Boolean expression to verify this row.' };
    const checkbox = cell.querySelector('.verification-result'), edit = cell.querySelector('.verification-edit');
    checkbox.checked = result.state === 'pass'; checkbox.indeterminate = ['error', 'pending'].includes(result.state);
    checkbox.title = result.message;
    edit.title = `${result.message} Open the requirement editor.`;
    edit.setAttribute('aria-description', result.message);
    cell.dataset.state = result.state;
  }
  const checks = componentChecks();
  for (const row of viewRows('components')) {
    const cell = rowElement(row.key)?.querySelector('.component-summary');
    if (!cell) continue;
    const result = componentCheck(row, checks), checkbox = cell.querySelector('input');
    checkbox.checked = result.state === 'pass'; checkbox.indeterminate = ['error', 'pending'].includes(result.state);
    cell.dataset.state = result.state; cell.title = result.message; cell.setAttribute('aria-description', result.message);
  }
}
function scheduleEvaluation() {
  const token = ++generation;
  clearTimeout(evaluationTimer); clearTimeout(workerTimer); results = new Map(); updateChecks();
  evaluationTimer = setTimeout(() => {
    const statements = workspace.statements.filter(row => used(row, 'statements'));
    if (!statements.length) return;
    const fail = message => {
      results = new Map(statements.map(row => [row.key, { state: row.condition.trim() ? 'error' : 'unset', message,
        parameters: Object.fromEntries(workspace.variables.map(variable => [variable.name, { state: row.parameters[variable.name]?.trim() ? 'error' : 'unset', value: null, message }])) }]));
      updateChecks(); worker?.terminate(); worker = null;
    };
    try {
      if (!worker) {
        worker = new Worker('/verification-worker.js', { type: 'module' });
        worker.onmessage = event => {
          if (event.data.token !== generation) return;
          clearTimeout(workerTimer); results = new Map(event.data.results.map(result => [result.key, result])); updateChecks();
        };
      }
      worker.onerror = () => fail('Could not evaluate the expression.');
      workerTimer = setTimeout(() => fail('Expression evaluation timed out.'), 1500);
      worker.postMessage({ token, workspace: { variables: workspace.variables, statements } });
    } catch { fail('Expression evaluation is unavailable in this browser.'); }
  }, 100);
}
function showStatus(message = '', error = false, action = null) {
  status.textContent = message; status.parentElement.classList.toggle('error', error);
  retry.hidden = !action; retry.textContent = conflict ? 'Reload' : 'Retry'; retry.onclick = action;
}
function dirty() { if (!loaded) return false; try { return JSON.stringify(snapshot()) !== lastSaved; } catch { return true; } }
function scheduleSave() { clearTimeout(saveTimer); if (!conflict) { showStatus('Unsaved changes'); saveTimer = setTimeout(save, 450); } }
async function save() {
  clearTimeout(saveTimer);
  if (!loaded || saving || conflict) return;
  let data, serialized;
  try { data = validateWorkspace(snapshot(), catalog, products); serialized = JSON.stringify(data); }
  catch (error) { showStatus(error.message, true); return; }
  if (serialized === lastSaved) { showStatus(); return; }
  saving = true; showStatus(`Saving to ${modelName}…`);
  let succeeded = false;
  try {
    const response = await fetch('/api/workspace', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace: data, revision }) });
    const result = await response.json();
    if (!response.ok) { conflict = response.status === 409; throw new Error(result.error); }
    revision = result.revision; lastSaved = serialized; succeeded = true; showStatus();
  } catch (error) { showStatus(error.message || 'Could not save. Your edits are still in this tab.', true, conflict ? () => location.reload() : save); }
  finally { saving = false; if (succeeded && dirty()) scheduleSave(); }
}
async function load() {
  try {
    const response = await fetch('/api/workspace'), data = await response.json();
    if (!response.ok) throw new Error(data.error);
    catalog = data.catalog ?? domainTypes; products = data.products ?? [];
    workspace = validateWorkspace(data.workspace, catalog, products);
    statementIds.clear(); syncStatementIds();
    revision = data.revision; modelName = data.modelName ?? modelName; lastSaved = JSON.stringify(snapshot());
    active = requestedTab(); renderWorkbook(); loaded = true; main.inert = false; updateExport(); showStatus(); scheduleEvaluation();
  } catch (error) { showStatus(error.message || 'Could not open the mission model.', true, load); }
}
async function exportArtifact(kind) {
  const button = document.querySelector(`.export-${kind}`);
  try {
    const data = validateWorkspace(snapshot(), catalog, products), context = active;
    exporting = true; updateExport(); button.setAttribute('aria-busy', 'true');
    const response = await fetch(`/api/${kind}`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workspace: data, context }) });
    if (!response.ok) throw new Error((await response.json()).error);
    const blob = await response.blob(), url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = response.headers.get('Content-Disposition')?.match(/filename="([^"]+)"/)?.[1] ?? (kind === 'sysml' ? 'mission-export.sysml' : kind === 'kicad' ? 'eps.kicad_sch' : 'eps-fprime.zip');
    document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) { showStatus(error.message || 'Could not export the components.', true); }
  finally { exporting = false; updateExport(); button.removeAttribute('aria-busy'); }
}
function context(target) {
  const tr = target.closest('tr[data-key]'), table = tr?.closest('[data-table]').dataset.table;
  return tr ? { tr, table, row: rowByKey(tr.dataset.key) } : null;
}
function activate(row, table, field, state = workspace) {
  if (table === 'components') {
    if (field !== 'id' && !row.id) row.id = nextId(state, 'Component');
  } else if (table === 'stakeholders' && active !== 'external') {
    const wasEmpty = !row.definition;
    row.definition ||= allowedDefinitions(state, active, catalog)[0]?.model ?? '';
    const type = catalog.find(type => type.model === row.definition);
    if (!row.name && field === 'definition') row.name = type?.name ?? '';
    if (field !== 'id' && !row.id) row.id = nextId(state, 'Element', type?.id ?? row.name);
    if (wasEmpty || field === 'definition') addElementChildren(state, row, catalog);
  } else {
    const prefix = tabsFor(state, catalog).find(tab => tab.key === row.context)?.prefix ?? 'REQ';
    if (field !== 'id' && !row.id) row.id = nextId(state, table === 'stakeholders' ? 'Stakeholder' : row.kind,
      table === 'stakeholders' ? row.name : row.kind === 'Requirement' ? prefix : '');
    if (table === 'stakeholders' && !row.type && row.id) row.type = 'Mission Stakeholder';
  }
}
function changed(row, table, field) {
  activate(row, table, field);
  syncStatementIds();
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
      renderTabs();
    }
  } else if (table === 'statements') updatePreview(row);
  else tr.querySelector('[data-field="product"]').title = rowLabel(row);
  addTrailingRows(table); updateExport(); scheduleSave(); scheduleEvaluation();
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
      if (field === 'definition' && row.definition !== event.target.value && (workspace.elements.some(child => child.owner === row.key && used(child, 'stakeholders'))
          || workspace.statements.some(statement => statement.context === row.key && used(statement, 'statements'))
          || workspace.components.some(component => component.owner === row.key && used(component, 'components')))) {
        event.target.value = row.definition; throw new Error('This element has child rows. Remove those rows before changing its type.');
      }
      row[field] = field === 'id' ? event.target.value.toUpperCase() : event.target.value;
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
  if (table === 'statements' && ((field === 'verified' && event.key === 'F2') || (field === 'text' && ['F2', 'Enter', ' '].includes(event.key)))) {
    event.preventDefault(); closeEditor(); closeMenus();
    requirementEditor.open(row.key, tr.querySelector(field === 'verified' ? '.verification-edit' : '.statement-cell .requirement-edit')); return;
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
  if (restore && popoverAnchor?.isConnected) popoverAnchor.querySelector('input,button,textarea')?.focus();
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
  const state = { stakeholders: workspace.stakeholders.filter(item => /^[A-Z]{3}$/.test(item.id)),
    elements: workspace.elements.filter(item => /^[A-Z]{3}$/.test(item.id)),
    statements: workspace.statements.filter(item => /^[A-Z]{3}\d{3}$/.test(item.id)),
    components: workspace.components.filter(item => /^[A-Z]{3}\d{3}$/.test(item.id)) };
  const labels = new Map(tabsFor(workspace, catalog).map(tab => [tab.key, tab.label]));
  const candidates = editor.field === 'requirements' ? componentRequirements(state, row)
    : editor.field === 'affected' ? assignableElements(state, row) : availableSources(state, row.key);
  const choices = candidates.filter(item => `${item.id} ${rowLabel(item)} ${labels.get(contextForRow(item))}`.toLowerCase().includes(query));
  document.querySelector('#source-choices').innerHTML = choices.length ? choices.map(item => `<label class="source-choice"><input type="checkbox" data-source-key="${item.key}" ${row[editor.field].includes(item.key) ? 'checked' : ''}><span><strong>${escape(item.id)}</strong><span>${escape(labels.get(contextForRow(item)))} · ${escape(rowLabel(item)) || '(empty row)'}</span></span></label>`).join('') : '<p>No matching rows.</p>';
}
function openSources(row, anchor, field = 'sources') {
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
  if (table === 'statements') requirementEditor.open(added.key, rowElement(added.key).querySelector('.requirement-edit'));
  else focusCell(table, insertion, 1);
}
function deleteRow(table, key) {
  if (!viewRows(table).some(row => row.key === key)) return;
  if (workspace.statements.some(row => row.sources.includes(key) || row.affected.includes(key)) || workspace.components.some(row => row.requirements.includes(key))) { showStatus('This row is linked. Remove its source and assignment links before deleting it.', true); return; }
  if (workspace.elements.some(row => row.owner === key && used(row, 'stakeholders')) || workspace.statements.some(row => row.context === key && used(row, 'statements')) || workspace.components.some(row => row.owner === key && used(row, 'components'))) { showStatus('This element has child rows. Delete those rows before deleting the element.', true); return; }
  const rows = viewRows(table), collection = dataRows(table), index = rows.findIndex(row => row.key === key);
  if (index < 0) return;
  collection.splice(collection.indexOf(rows[index]), 1); selected[selectionKey(table)] = null;
  renderTabs(); render(table); updateSources(); focusCell(table, Math.min(index, viewRows(table).length - 1), 0); scheduleSave(); scheduleEvaluation();
}
main.addEventListener('click', event => {
  const exportButton = event.target.closest('.export-sysml, .export-kicad, .export-fprime');
  if (exportButton) { closeMenus(); closeEditor(); exportArtifact(exportButton.matches('.export-sysml') ? 'sysml' : exportButton.matches('.export-kicad') ? 'kicad' : 'fprime'); return; }
  const ctx = context(event.target), link = event.target.closest('[data-row-link]');
  const requirement = event.target.closest('.requirement-edit');
  if (requirement) { event.preventDefault(); closeMenus(); closeEditor(); requirementEditor.open(ctx.row.key, requirement); return; }
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
        : field === 'verified' ? (table === 'components' ? componentCheck(row, componentChecks()) : results.get(row.key))?.state === 'pass'
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
    if (!transient) requirementEditor.close();
  }
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 's') {
    event.preventDefault(); if (requirementEditor.isOpen()) requirementEditor.save(); else save();
  }
});
main.addEventListener('paste', event => {
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
          if (target.definition && target.definition !== matches[0].model && (candidate.elements.some(child => child.owner === target.key && used(child, 'stakeholders')) || candidate.components.some(component => component.owner === target.key && used(component, 'components')) || candidate.statements.some(statement => statement.context === target.key && used(statement, 'statements')))) throw new Error('Remove child rows before changing their parent type.');
          target.definition = matches[0].model;
        } else if (variable) target.parameters[field] = parameterExpression(value, variable, target.id);
        else target[field] = field === 'id' ? value.trim().toUpperCase() : value;
      }
      activate(target, table, columns(table).includes('definition') ? 'definition' : 'paste', candidate);
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
    syncStatementIds(candidate, new Map(statementIds));
    validateWorkspace(snapshot(candidate), catalog, products); workspace = candidate;
    statementIds.clear(); workspace.statements.forEach(row => statementIds.set(row.key, row.id));
    renderWorkbook(); focusCell(table, start, column); scheduleSave(); scheduleEvaluation();
  } catch (error) { showStatus(error.message, true); }
});
window.addEventListener('beforeunload', event => { if (dirty() || requirementEditor.isDirty()) { event.preventDefault(); event.returnValue = ''; } });
document.addEventListener('visibilitychange', () => { if (document.hidden && dirty()) save(); });
load();
