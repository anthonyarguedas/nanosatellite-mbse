import {
  addElementChildren, allowedDefinitions, allRows as workbookRows, assignableElements, availableSources,
  contextForRow, domainTypes, emptyWorkspace, nextId, numeric, parseTSV,
  stakeholderTypes, statementKinds, tabsFor, validVariableName, validateWorkspace,
} from '/model.mjs';

const main = document.querySelector('main');
const status = document.querySelector('#status'), retry = document.querySelector('#retry');
const sourceEditor = document.querySelector('#source-editor');
const verificationEditor = document.querySelector('#verification-editor');
const variableEditor = document.querySelector('#variable-editor');
let catalog = domainTypes, active = 'external', workspace = emptyWorkspace(catalog);
let revision, lastSaved, saveTimer, modelName = 'mission.sysml';
let loaded = false, saving = false, conflict = false;
let editor = null, popoverAnchor = null, worker = null, evaluationTimer, workerTimer, generation = 0;
const selected = {}, sorts = {};
let results = new Map();
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);
const variableNames = () => workspace.variables.map(variable => variable.name);
const tabInfo = () => tabsFor(workspace, catalog).find(tab => tab.key === active);
const columns = table => table === 'stakeholders' ? ['id', 'name', active === 'external' ? 'type' : 'definition']
  : ['id', 'sources', 'text', 'verified', ...(active === 'external' ? [] : ['affected']), ...variableNames()];
const dataRows = (table, state = workspace) => table === 'statements' ? state.statements : active === 'external' ? state.stakeholders : state.elements;
const viewRows = (table, state = workspace) => dataRows(table, state).filter(row => table === 'statements' ? row.context === active : active === 'external' || row.owner === active);
const selectionKey = table => `${active}:${table}`;
const body = table => document.querySelector(`[data-table="${table}"] tbody`);
const rowElement = key => document.querySelector(`tr[data-key="${key}"]`);
const rowByKey = key => workbookRows(workspace).find(row => row.key === key);

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
  renderTabs(); render('stakeholders'); render('statements');
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
  if (table === 'stakeholders') return active === 'external'
    ? { ...common, name: '', type: '' } : { ...common, name: '', definition: '', owner: active };
  return { ...common, context: active, sources: [], affected: [], kind: 'Requirement', text: '', condition: '',
    parameters: Object.fromEntries(variableNames().map(name => [name, null])) };
}
function used(row, table) {
  return table === 'stakeholders' ? Boolean(row.id || row.name || row.type || row.definition)
    : Boolean(row.id || row.sources.length || row.affected.length || row.text || row.condition || row.kind !== 'Requirement'
      || Object.values(row.parameters).some(value => value !== null && value !== ''));
}
function snapshot(state = workspace) {
  return {
    version: 4, variables: structuredClone(state.variables),
    stakeholders: state.stakeholders.filter(row => used(row, 'stakeholders')).map(row => ({ key: row.key, id: row.id.trim(), name: row.name, type: row.type })),
    elements: state.elements.filter(row => used(row, 'stakeholders')).map(row => ({ key: row.key, id: row.id.trim(), name: row.name, owner: row.owner, definition: row.definition })),
    statements: state.statements.filter(row => used(row, 'statements')).map(row => ({
      key: row.key, id: row.id.trim(), context: row.context, sources: [...row.sources], affected: [...row.affected], kind: row.kind, text: row.text,
      condition: row.condition,
      parameters: Object.fromEntries(state.variables.map(variable => [variable.name, numeric(row.parameters[variable.name], variable, row.id)])),
    })),
  };
}
function sourceHTML(row, index, field = 'sources', col = 1) {
  const links = row[field].map(key => {
    const source = rowByKey(key);
    return source ? `<a href="#row-${key}" data-row-link="${key}" title="${escape(source.name ?? source.text)}">${escape(source.id)}</a>` : '';
  }).join('');
  return `<div class="row-sources ${links ? 'has-sources' : ''}" data-links="${field}">${links}<button data-field="${field}" data-col="${col}" class="source-edit" aria-label="Edit ${field === 'affected' ? 'affected elements' : 'sources'}, row ${index + 1}" title="${field === 'affected' ? 'Assign to elements on the left' : 'Link one or more source rows'}"><span class="chevron"></span></button></div>`;
}
function renderHeader() {
  const table = document.querySelector('.statements table');
  const widths = workspace.variables.map(variable => Math.max(70, Math.min(200, 60 + variable.name.length * 7)));
  table.style.setProperty('--variables-width', `${widths.reduce((sum, width) => sum + width, 0)}px`);
  table.style.setProperty('--assignment-width', active === 'external' ? '0px' : '190px');
  table.querySelector('colgroup').innerHTML = '<col class="row-actions-col"><col class="statement-id"><col class="statement-source"><col class="statement-text"><col class="statement-verified">'
    + (active === 'external' ? '' : '<col class="statement-affected">')
    + workspace.variables.map(() => '<col class="parameter-col">').join('') + '<col class="add-variable-col">';
  table.querySelectorAll('.parameter-col').forEach((column, index) => { column.style.width = `${widths[index]}px`; });
  const header = (field, label) => `<th scope="col"><button data-sort="${field}" title="Sort by ${label}">${label}</button></th>`;
  table.querySelector('thead').innerHTML = '<tr><th scope="col" class="row-actions-heading" aria-label="Row actions"></th>'
    + header('id', 'ID')
    + header('sources', 'Source')
    + header('text', active === 'external' ? 'Requirement, Need, Objective, Concern, Constraint' : 'Requirement')
    + header('verified', 'Verified')
    + (active === 'external' ? '' : header('affected', tabInfo().affectedLabel))
    + workspace.variables.map(variable => `<th scope="col"><div class="variable-heading"><button data-sort="${variable.name}" title="Sort by ${variable.name}">${escape(variable.name)}</button><button class="variable-menu" data-variable="${variable.name}" aria-label="Edit variable ${variable.name}" title="Edit variable type">${variable.type === 'integer' ? 'Int' : 'Float'}</button></div></th>`).join('')
    + '<th scope="col"><button class="add-variable" aria-label="Add variable column" title="Add variable column">+</button></th></tr>';
}
function rowHTML(row, table, index) {
  const attrs = (field, col) => `data-field="${field}" data-col="${col}" aria-label="${table === 'stakeholders' ? active === 'external' ? 'Stakeholder' : 'Element' : 'Statement'} ${field}, row ${index + 1}"`;
  let cells = `<td class="row-actions"><button type="button" class="row-delete" data-delete-row="${row.key}" aria-label="Delete row ${escape(row.id || index + 1)}" title="Delete this row" ${used(row, table) ? '' : 'disabled'}><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 5h12M8 3h4M6 5l1 12h6l1-12M9 8v6M11 8v6"/></svg></button></td>`;
  cells += `<td class="id-cell"><input ${attrs('id', 0)} value="${escape(row.id)}" maxlength="${table === 'stakeholders' ? 3 : 6}" title="${table === 'stakeholders' ? 'Three uppercase letters' : 'Three uppercase letters and three digits'}" autocomplete="off" spellcheck="false"></td>`;
  if (table === 'stakeholders') {
    cells += `<td><input ${attrs('name', 1)} value="${escape(row.name)}" title="${escape(row.name)}" autocomplete="off"></td>`;
    if (active === 'external') cells += `<td><select ${attrs('type', 2)}><option value=""> </option>${stakeholderTypes.map(type => `<option ${row.type === type.name ? 'selected' : ''}>${type.name}</option>`).join('')}</select></td>`;
    else {
      const options = allowedDefinitions(workspace, active, catalog), type = catalog.find(type => type.model === row.definition);
      cells += `<td><select ${attrs('definition', 2)} data-category="${escape(type?.category)}" title="${escape(row.definition)}"><option value=""> </option>${options.map(option => `<option value="${option.model}" ${row.definition === option.model ? 'selected' : ''}>${escape(active === 'mission' && option.category !== option.name ? `${option.category} · ${option.name}` : option.name)}</option>`).join('')}</select></td>`;
    }
  } else {
    cells += `<td>${sourceHTML(row, index)}</td>`;
    cells += `<td class="statement-cell"><textarea ${attrs('text', 2)} rows="1">${escape(row.text)}</textarea>${active === 'external' ? `<select class="kind-select" data-field="kind" aria-label="Statement type, row ${index + 1}" title="${escape(row.kind)}">${statementKinds.map(kind => `<option ${row.kind === kind ? 'selected' : ''}>${kind}</option>`).join('')}</select>` : ''}</td>`;
    cells += `<td class="checkbox-cell"><input class="verification-result" type="checkbox" disabled tabindex="-1" aria-readonly="true" aria-label="Verification result, row ${index + 1}"><button type="button" class="verification-edit" data-field="verified" data-col="3" aria-label="Edit verification, row ${index + 1}" aria-haspopup="dialog" title="Edit SysML condition (F2)"></button></td>`;
    if (active !== 'external') cells += `<td>${sourceHTML(row, index, 'affected', 4)}</td>`;
    cells += workspace.variables.map((variable, i) => `<td class="parameter"><input ${attrs(variable.name, i + (active === 'external' ? 4 : 5))} value="${escape(row.parameters[variable.name])}" inputmode="${variable.type === 'integer' ? 'numeric' : 'decimal'}" autocomplete="off" spellcheck="false" title="${variable.name}: ${variable.type}"></td>`).join('');
    cells += '<td class="column-tail"></td>';
  }
  return `<tr id="row-${row.key}" data-key="${row.key}">${cells}</tr>`;
}
function pad(table) {
  while (viewRows(table).length < 8 || used(viewRows(table).at(-1), table)) dataRows(table).push(draft(table));
}
function render(table) {
  pad(table);
  if (table === 'statements') renderHeader();
  body(table).innerHTML = viewRows(table).map((row, index) => rowHTML(row, table, index)).join('');
  if (table === 'statements') { viewRows(table).forEach(updatePreview); updateChecks(); }
}
function addTrailingRows(table) {
  const count = viewRows(table).length; pad(table);
  const rows = viewRows(table);
  for (let i = count; i < rows.length; i++) body(table).insertAdjacentHTML('beforeend', rowHTML(rows[i], table, i));
}
function updateSources() {
  for (const row of viewRows('statements')) {
    for (const container of rowElement(row.key)?.querySelectorAll('.row-sources') ?? []) {
      const field = container.dataset.links, button = container.querySelector('.source-edit');
      for (const link of container.querySelectorAll('[data-row-link]')) if (!row[field].includes(link.dataset.rowLink)) link.remove();
      for (const key of row[field]) {
        const source = rowByKey(key);
        if (!source) continue;
        let link = container.querySelector(`[data-row-link="${key}"]`);
        if (!link) { link = document.createElement('a'); link.dataset.rowLink = key; link.href = `#row-${key}`; container.insertBefore(link, button); }
        link.textContent = source.id; link.title = source.name ?? source.text;
      }
      container.classList.toggle('has-sources', row[field].length > 0);
    }
  }
}
function updatePreview(row) {
  const textarea = rowElement(row.key)?.querySelector('textarea');
  if (textarea) textarea.title = row.text.replace(/\{([A-Za-z_][A-Za-z0-9_]*)\}/g, (token, name) => row.parameters[name] ?? token) || 'Use variable names in braces, such as {x} or {mass}.';
}
function updateChecks() {
  for (const row of viewRows('statements')) {
    const cell = rowElement(row.key)?.querySelector('.checkbox-cell');
    if (!cell) continue;
    const result = row.condition.trim() ? results.get(row.key) ?? { state: 'pending', message: 'Recalculating…' }
      : { state: 'unset', message: 'No SysML condition. Enter a Boolean expression to verify this row.' };
    const checkbox = cell.querySelector('.verification-result'), edit = cell.querySelector('.verification-edit');
    checkbox.checked = result.state === 'pass'; checkbox.indeterminate = ['error', 'pending'].includes(result.state);
    edit.title = `${result.message} Click to edit the SysML condition.`;
    edit.setAttribute('aria-description', result.message);
    cell.dataset.state = result.state;
  }
  if (editor?.type === 'verification') {
    const row = rowByKey(editor.key);
    const result = row.condition.trim() ? results.get(editor.key) ?? { state: 'pending', message: 'Recalculating…' }
      : { state: 'unset', message: 'Enter a SysML condition to verify this row.' };
    const label = document.querySelector('#verification-result');
    label.textContent = `${{ pass: 'True', fail: 'False', pending: 'Pending', error: 'Error', unset: 'Not verified' }[result.state]}: ${result.message}`;
    label.classList.toggle('error-text', result.state === 'error');
  }
}
function scheduleEvaluation() {
  const token = ++generation;
  clearTimeout(evaluationTimer); clearTimeout(workerTimer); results = new Map(); updateChecks();
  evaluationTimer = setTimeout(() => {
    const statements = workspace.statements.filter(row => used(row, 'statements'));
    if (!statements.some(row => row.condition.trim())) return;
    const fail = message => {
      results = new Map(statements.filter(row => row.condition.trim()).map(row => [row.key, { state: 'error', message }]));
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
  try { data = validateWorkspace(snapshot(), catalog); serialized = JSON.stringify(data); }
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
    catalog = data.catalog ?? domainTypes; workspace = validateWorkspace(data.workspace, catalog);
    revision = data.revision; modelName = data.modelName ?? modelName; lastSaved = JSON.stringify(snapshot());
    active = requestedTab(); renderWorkbook(); loaded = true; main.inert = false; showStatus(); scheduleEvaluation();
  } catch (error) { showStatus(error.message || 'Could not open the mission model.', true, load); }
}
function context(target) {
  const tr = target.closest('tr[data-key]'), table = tr?.closest('[data-table]').dataset.table;
  return tr ? { tr, table, row: rowByKey(tr.dataset.key) } : null;
}
function activate(row, table, field, state = workspace) {
  if (table === 'stakeholders' && active !== 'external') {
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
  } else updatePreview(row);
  addTrailingRows(table); scheduleSave(); scheduleEvaluation();
}
main.addEventListener('focusin', event => { const ctx = context(event.target); if (ctx) selected[selectionKey(ctx.table)] = ctx.row.key; });
main.addEventListener('input', event => {
  const field = event.target.dataset.field, ctx = context(event.target);
  if (!field || !ctx || ['sources', 'affected'].includes(field)) return;
  const { row, table } = ctx;
  try {
    const variable = workspace.variables.find(variable => variable.name === field);
    if (variable) {
      row.parameters[field] = event.target.value;
      try { numeric(event.target.value, variable, row.id); event.target.removeAttribute('aria-invalid'); } catch { event.target.setAttribute('aria-invalid', 'true'); }
    } else if (field === 'verified') { updateChecks(); return; }
    else {
      if (field === 'definition' && row.definition !== event.target.value && (workspace.elements.some(child => child.owner === row.key && used(child, 'stakeholders'))
          || workspace.statements.some(statement => statement.context === row.key && used(statement, 'statements')))) {
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
  if (event.key === 'F2' && event.target.dataset.field === 'verified') { event.preventDefault(); openVerification(row, tr.querySelector('.checkbox-cell')); return; }
  if (active === 'external' && event.altKey && event.key === 'ArrowDown' && event.target.dataset.field === 'text') {
    event.preventDefault(); const select = tr.querySelector('.kind-select'); select.focus(); select.showPicker?.(); return;
  }
  if (event.target.matches('.kind-select') && event.key === 'Tab' && event.shiftKey) { event.preventDefault(); focusCell(table, index, 2); return; }
  if (event.target.dataset.col === undefined && !event.target.matches('.kind-select')) return;
  const col = Number(event.target.dataset.col ?? 2);
  if (event.target.tagName === 'SELECT' && event.key !== 'Tab') return;
  if (event.key === 'Tab') {
    if (event.shiftKey && col === 0) {
      const remove = tr.querySelector('.row-delete:not(:disabled)');
      if (remove) { event.preventDefault(); remove.focus(); return; }
    }
    if (active === 'external' && table === 'statements' && ((col === 2 && !event.shiftKey && !event.target.matches('select')) || (col === 3 && event.shiftKey))) return;
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
    statements: workspace.statements.filter(item => /^[A-Z]{3}\d{3}$/.test(item.id)) };
  const labels = new Map(tabsFor(workspace, catalog).map(tab => [tab.key, tab.label]));
  const candidates = editor.field === 'affected' ? assignableElements(state, row) : availableSources(state, row.key);
  const choices = candidates.filter(item => `${item.id} ${item.name ?? item.text} ${labels.get(contextForRow(item))}`.toLowerCase().includes(query));
  document.querySelector('#source-choices').innerHTML = choices.length ? choices.map(item => `<label class="source-choice"><input type="checkbox" data-source-key="${item.key}" ${row[editor.field].includes(item.key) ? 'checked' : ''}><span><strong>${escape(item.id)}</strong><span>${escape(labels.get(contextForRow(item)))} · ${escape(item.name ?? item.text) || '(empty row)'}</span></span></label>`).join('') : '<p>No matching rows.</p>';
}
function openSources(row, anchor, field = 'sources') {
  document.querySelector('#source-search').value = '';
  const label = field === 'affected' ? 'Assign to elements on the left' : 'Link source rows';
  sourceEditor.querySelector('strong').textContent = label; sourceEditor.setAttribute('aria-label', label);
  openEditor(sourceEditor, anchor, { type: 'sources', key: row.key, field }); renderSourceChoices(); document.querySelector('#source-search').focus();
}
document.querySelector('#source-search').addEventListener('input', renderSourceChoices);
sourceEditor.addEventListener('change', event => {
  const key = event.target.dataset.sourceKey;
  if (!key) return;
  const row = rowByKey(editor.key), field = editor.field;
  row[field] = event.target.checked ? [...row[field], key] : row[field].filter(source => source !== key);
  changed(row, 'statements', field); updateSources();
});
function openVerification(row, anchor) {
  document.querySelector('#verification-condition').value = row.condition;
  openEditor(verificationEditor, anchor, { type: 'verification', key: row.key }); updateChecks(); document.querySelector('#verification-condition').focus();
}
document.querySelector('#verification-condition').addEventListener('input', event => { const row = rowByKey(editor.key); row.condition = event.target.value; changed(row, 'statements', 'condition'); });
document.querySelector('#verification-condition').addEventListener('keydown', event => { if (event.key === 'Enter') { event.preventDefault(); closeEditor(true); save(); } });
function openVariable(name, anchor) {
  const variable = workspace.variables.find(variable => variable.name === name), input = document.querySelector('#variable-name');
  input.value = variable?.name ?? ''; input.readOnly = Boolean(variable);
  document.querySelector('#variable-type').value = variable?.type ?? 'float';
  document.querySelector('#variable-title').textContent = variable ? `Variable ${name}` : 'Add variable';
  document.querySelector('#variable-submit').textContent = variable ? 'Save type' : 'Add column';
  document.querySelector('#variable-error').textContent = '';
  openEditor(variableEditor, anchor, { type: 'variable', name: variable?.name }); (variable ? document.querySelector('#variable-type') : input).focus();
}
variableEditor.addEventListener('submit', event => {
  event.preventDefault();
  try {
    const name = document.querySelector('#variable-name').value.trim(), type = document.querySelector('#variable-type').value;
    if (!validVariableName(name)) throw new Error('Use a variable name such as mass or cell_count.');
    const candidate = structuredClone(workspace);
    if (editor.name) candidate.variables.find(variable => variable.name === editor.name).type = type;
    else { if (candidate.variables.some(variable => variable.name === name)) throw new Error('This variable already exists.'); candidate.variables.push({ name, type }); candidate.statements.forEach(row => { row.parameters[name] = null; }); }
    validateWorkspace(snapshot(candidate), catalog); workspace = candidate; closeEditor(); render('statements'); scheduleSave(); scheduleEvaluation();
  } catch (error) { document.querySelector('#variable-error').textContent = error.message; }
});
function insertRow(table) {
  const rows = viewRows(table), collection = dataRows(table), index = rows.findIndex(row => row.key === selected[selectionKey(table)]);
  let insertion = index < 0 ? rows.findIndex(row => !used(row, table)) : index + 1;
  if (insertion < 0) insertion = rows.length;
  collection.splice(rows[insertion] ? collection.indexOf(rows[insertion]) : collection.length, 0, draft(table));
  render(table); focusCell(table, insertion, table === 'stakeholders' ? 1 : 2);
}
function deleteRow(table, key) {
  if (!viewRows(table).some(row => row.key === key)) return;
  if (workspace.statements.some(row => row.sources.includes(key) || row.affected.includes(key))) { showStatus('This row is linked. Remove its source and assignment links before deleting it.', true); return; }
  if (workspace.elements.some(row => row.owner === key && used(row, 'stakeholders')) || workspace.statements.some(row => row.context === key && used(row, 'statements'))) { showStatus('This element has child rows. Delete those rows before deleting the element.', true); return; }
  const rows = viewRows(table), collection = dataRows(table), index = rows.findIndex(row => row.key === key);
  if (index < 0) return;
  collection.splice(collection.indexOf(rows[index]), 1); selected[selectionKey(table)] = null;
  renderTabs(); render(table); updateSources(); focusCell(table, Math.min(index, viewRows(table).length - 1), 0); scheduleSave(); scheduleEvaluation();
}
main.addEventListener('click', event => {
  const ctx = context(event.target), link = event.target.closest('[data-row-link]');
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
  if (event.target.closest('.verification-edit')) { event.preventDefault(); openVerification(ctx.row, event.target.closest('td')); return; }
  const variable = event.target.closest('[data-variable]');
  if (variable || event.target.closest('.add-variable')) { openVariable(variable?.dataset.variable, event.target.closest('th')); return; }
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
    const value = row => variableNames().includes(field) ? row.parameters[field]
      : ['sources', 'affected'].includes(field) ? row[field].map(key => rowByKey(key)?.id ?? '').join(',')
        : field === 'verified' ? results.get(row.key)?.state === 'pass' : row[field];
    const current = viewRows(table), collection = dataRows(table);
    const sorted = current.filter(row => used(row, table)).sort((a, b) => direction * (variableNames().includes(field)
      ? Number(value(a) ?? 0) - Number(value(b) ?? 0) : String(value(a) ?? '').localeCompare(String(value(b) ?? ''), undefined, { numeric: true })));
    const retained = collection.filter(row => !current.includes(row)); collection.splice(0, collection.length, ...retained, ...sorted);
    render(table); document.querySelectorAll(`[data-table="${table}"] th`).forEach(th => th.removeAttribute('aria-sort'));
    const heading = document.querySelector(`[data-table="${table}"] [data-sort="${field}"]`);
    heading?.closest('th').setAttribute('aria-sort', direction === 1 ? 'ascending' : 'descending');
    if (heading) heading.title = `Sorted ${direction === 1 ? 'ascending' : 'descending'}. Click to reverse.`;
    scheduleSave();
  }
});
main.addEventListener('dblclick', event => { const cell = event.target.closest('.checkbox-cell'); if (cell) openVerification(context(cell).row, cell); });
document.addEventListener('click', event => {
  if (event.target.closest('[data-close]')) closeEditor(true);
  else if (!event.target.closest('.popover') && !popoverAnchor?.contains(event.target)) closeEditor();
  if (!event.target.closest('.table-top')) closeMenus();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') { closeMenus(); closeEditor(true); }
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 's') { event.preventDefault(); save(); }
});
main.addEventListener('paste', event => {
  const ctx = context(event.target), text = event.clipboardData.getData('text/plain');
  if (!ctx || event.target.dataset.col === undefined || (!['sources', 'affected', 'verified'].includes(event.target.dataset.field) && !text.includes('\t') && (!/[\r\n]/.test(text) || event.target.tagName === 'TEXTAREA'))) return;
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
        if (['sources', 'affected'].includes(field)) links.push([target, field, value.trim()]);
        else if (field === 'definition') {
          const matches = allowedDefinitions(candidate, active, catalog).filter(type => [type.model, type.name, type.category].includes(value.trim()));
          if (matches.length !== 1) throw new Error('The element type must match one definition in the generic mission model.');
          if (target.definition && target.definition !== matches[0].model && candidate.elements.some(child => child.owner === target.key && used(child, 'stakeholders'))) throw new Error('Remove child rows before changing their parent type.');
          target.definition = matches[0].model;
        } else if (variable) target.parameters[field] = numeric(value, variable, target.id);
        else if (field === 'verified') target.condition = value; else target[field] = field === 'id' ? value.trim().toUpperCase() : value;
      }
      activate(target, table, columns(table).includes('definition') ? 'definition' : 'paste', candidate);
    }
    for (const [target, field, label] of links) {
      target[field] = [];
      for (const item of label.split(/[,;]+/).map(value => value.trim()).filter(Boolean)) {
        const rows = field === 'affected' ? assignableElements(candidate, target) : workbookRows(candidate);
        let matches = rows.filter(row => row.id === item);
        if (!matches.length) matches = rows.filter(row => row.name === item);
        if (matches.length !== 1) throw new Error(`Source or assignment “${item}” must match one row ID or a unique element name.`);
        if (!target[field].includes(matches[0].key)) target[field].push(matches[0].key);
      }
    }
    validateWorkspace(snapshot(candidate), catalog); workspace = candidate; renderWorkbook(); focusCell(table, start, column); scheduleSave(); scheduleEvaluation();
  } catch (error) { showStatus(error.message, true); }
});
window.addEventListener('beforeunload', event => { if (dirty()) { event.preventDefault(); event.returnValue = ''; } });
document.addEventListener('visibilitychange', () => { if (document.hidden && dirty()) save(); });
load();
