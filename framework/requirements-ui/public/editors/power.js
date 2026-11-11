import { powerFor, spacecraftComponents, metadata } from '/workbook.js';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const inputNumber = input => input.value.trim() === '' ? null : Number(input.value);
const key = () => crypto.randomUUID();
const blankMode = () => ({ key: key(), name: '', sunlight: null, eclipse: null });
const blankState = () => ({ key: key(), name: '', watts: null, basis: 'estimated', source: '', conditions: '' });
const addIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>';
const deleteIcon = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 5h12M8 3h4M6 5l1 12h6l1-12M9 8v6M11 8v6"/></svg>';

export function createPowerEditor({ section, panel, getWorkspace, getActive, onChange, onCommand, onError, beforeOpen }) {
  let draft = null, modeDraft = blankMode();
  const limits = () => metadata(getWorkspace()).limits;
  function render() {
    const workspace = getWorkspace(), active = getActive();
    const mission = active === 'mission';
    section.hidden = !mission && !(metadata(workspace).powerScopes ?? []).some(scope => scope.key === active && scope.kind === 'subsystem');
    if (section.hidden) { section.replaceChildren(); return; }
    const modes = workspace.power.modes;
    const modeRows = [...modes, ...(modes.length < limits().modes ? [modeDraft] : [])];
    const components = spacecraftComponents(workspace).filter(element => element.owner === active && powerFor(workspace, element).accounting === 'counted');
    section.innerHTML = `${mission ? `<section class="sheet power-modes"><div class="table-top"><h2>Spacecraft Modes</h2><button type="button" class="add-row" data-power-add-mode aria-label="Add spacecraft mode" title="Add row" ${modes.length >= limits().modes ? 'disabled' : ''}>${addIcon}</button></div>
      <div class="table-frame"><table class="power-table" aria-label="Spacecraft modes"><colgroup><col class="row-actions-col"><col><col class="power-share-col"><col class="power-share-col"></colgroup><thead><tr><th class="row-actions-heading" aria-label="Row actions"></th><th scope="col">Mode</th><th scope="col">Sunlight (%)</th><th scope="col">Eclipse (%)</th></tr></thead><tbody>${modeRows.map((mode, index) => `<tr data-mode-row="${mode.key}"><td class="row-actions"><button type="button" class="row-delete" data-power-remove-mode="${mode.key}" aria-label="Delete mode ${escape(mode.name || index + 1)}" ${mode === modeDraft ? 'disabled' : ''}>${deleteIcon}</button></td><td><input data-mode-key="${mode.key}" data-mode-field="name" value="${escape(mode.name)}" maxlength="80" aria-label="Mode name, row ${index + 1}"></td>${['sunlight', 'eclipse'].map(period => `<td><input type="number" min="0" max="100" step="any" data-mode-key="${mode.key}" data-mode-field="${period}" value="${mode[period] ?? ''}" aria-label="${period === 'sunlight' ? 'Sunlight' : 'Eclipse'} share, row ${index + 1}"></td>`).join('')}</tr>`).join('')}</tbody></table></div></section>` : ''}
      ${!mission && modes.length ? `<section class="sheet power-allocations"><div class="table-top"><h2>Component State Allocation</h2></div><div class="table-frame"><table class="power-table" aria-label="Component state allocation"><colgroup><col class="power-reference-col">${modes.map(() => '<col class="power-mode-col">').join('')}</colgroup><thead><tr><th scope="col">Component</th>${modes.map(mode => `<th scope="col">${escape(mode.name)}</th>`).join('')}</tr></thead><tbody>${components.map(element => {
        const load = powerFor(workspace, element);
        return `<tr data-power-row="${element.key}"><td><div class="row-sources"><a href="#row-${element.key}" data-row-link="${element.key}" title="${escape(element.name)}">${escape(element.id)}</a></div></td>${modes.map(mode => `<td><select data-power-assignment="${element.key}" data-mode="${mode.key}" aria-label="${escape(element.id)} state in ${escape(mode.name)}" ${load.states.length ? '' : 'disabled'}><option value=""> </option>${load.states.map(state => `<option value="${state.key}" ${load.assignments[mode.key] === state.key ? 'selected' : ''}>${escape(state.name)}</option>`).join('')}</select></td>`).join('')}</tr>`;
      }).join('')}</tbody></table></div></section>` : ''}`;
  }
  async function change(mutator) {
    try { const candidate = structuredClone(getWorkspace()); mutator(candidate); await onChange(candidate); }
    catch (error) { onError(error.message); render(); }
  }
  async function command(operation) {
    try { await onCommand(operation); render(); return true; }
    catch (error) { onError(error.message); render(); return false; }
  }
  section.addEventListener('change', async event => {
    const input = event.target;
    if (input.dataset.modeKey) {
      if (input.dataset.modeKey === modeDraft.key) {
        modeDraft[input.dataset.modeField] = input.dataset.modeField === 'name' ? input.value.trim() : inputNumber(input);
        if (!modeDraft.name) return;
        const added = structuredClone(modeDraft);
        if (await command({ name: 'add_mode', label: added.name, key: added.key, sunlight: added.sunlight, eclipse: added.eclipse })) modeDraft = blankMode();
        render();
      } else await command(input.dataset.modeField === 'name'
        ? { name: 'rename_mode', target: input.dataset.modeKey, label: input.value.trim() }
        : { name: 'configure_mode', target: input.dataset.modeKey, [input.dataset.modeField]: inputNumber(input) });
    } else if (input.dataset.powerAssignment) change(workspace => {
      let load = workspace.power.loads.find(load => load.element === input.dataset.powerAssignment);
      if (!load) { load = structuredClone(powerFor(workspace, workspace.elements.find(row => row.key === input.dataset.powerAssignment))); workspace.power.loads.push(load); }
      if (input.value) load.assignments[input.dataset.mode] = input.value;
      else delete load.assignments[input.dataset.mode];
    });
  });
  section.addEventListener('click', event => {
    if (event.target.closest('[data-power-add-mode]')) section.querySelector(`[data-mode-key="${modeDraft.key}"][data-mode-field="name"]`)?.focus();
    const remove = event.target.closest('[data-power-remove-mode]');
    if (remove && !remove.disabled) command({ name: 'remove_mode', target: remove.dataset.powerRemoveMode });
  });
  section.addEventListener('keydown', event => {
    const input = event.target;
    if (!input.dataset.modeKey || !['Tab', 'Enter', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
    const fields = ['name', 'sunlight', 'eclipse'], field = fields.indexOf(input.dataset.modeField), modeKey = input.dataset.modeKey;
    event.preventDefault(); input.blur();
    const rows = [...section.querySelectorAll('[data-mode-row]')], index = rows.findIndex(row => row.dataset.modeRow === modeKey);
    let rowIndex = index, column = field;
    if (event.key === 'Tab') { column += event.shiftKey ? -1 : 1; if (column > 2) { rowIndex++; column = 0; } if (column < 0) { rowIndex--; column = 2; } }
    else rowIndex += event.key === 'ArrowUp' || (event.key === 'Enter' && event.shiftKey) ? -1 : 1;
    rows[rowIndex]?.querySelector(`[data-mode-field="${fields[column]}"]`)?.focus();
  });
  function isDirty() { return Boolean(draft && JSON.stringify(draft.load) !== draft.initial); }
  function close() {
    const elementKey = draft?.elementKey;
    draft = null; panel.hidden = true; document.body.classList.remove('power-editor-open');
    if (elementKey) document.querySelector(`[data-open-power="${elementKey}"]`)?.focus({ preventScroll: true });
  }
  function closeWithConfirmation() {
    if (isDirty() && !window.confirm('Discard the unsaved component power edits?')) return false;
    close(); return true;
  }
  function open(elementKey) {
    if (!closeWithConfirmation() || !beforeOpen()) return;
    const element = getWorkspace().elements.find(row => row.key === elementKey);
    if (!element) return;
    const load = structuredClone(powerFor(getWorkspace(), element));
    draft = { elementKey, definition: element.definition, load, emptyState: blankState(), initial: JSON.stringify(load), original: structuredClone(load) };
    panel.hidden = false; document.body.classList.add('power-editor-open'); renderDraft(); panel.querySelector('input')?.focus();
  }
  function stateRow(state, index, placeholder = false) {
    return `<tr data-state-key="${state.key}"><td class="row-actions"><button type="button" class="row-delete" data-remove-state="${state.key}" aria-label="Delete state ${escape(state.name || index + 1)}" ${placeholder ? 'disabled' : ''}>${deleteIcon}</button></td><td><input data-state-field="name" value="${escape(state.name)}" maxlength="80" aria-label="State ${index + 1} name"></td><td><input type="number" min="0" step="any" data-state-field="watts" value="${state.watts ?? ''}" aria-label="State ${index + 1} power in W"></td><td><select data-state-field="basis" aria-label="State ${index + 1} value meaning">${['estimated', 'typical', 'maximum', 'measured'].map(value => `<option value="${value}" ${state.basis === value ? 'selected' : ''}>${value[0].toUpperCase() + value.slice(1)}</option>`).join('')}</select></td><td><input data-state-field="source" value="${escape(state.source)}" maxlength="2000" aria-label="State ${index + 1} source"></td><td><input data-state-field="conditions" value="${escape(state.conditions)}" maxlength="2000" aria-label="State ${index + 1} operating conditions"></td></tr>`;
  }
  function renderDraft() {
    const element = getWorkspace().elements.find(row => row.key === draft.elementKey), load = draft.load;
    const options = metadata(getWorkspace()).accountingOptions?.[element.key] ?? [];
    const software = options.includes('host');
    panel.innerHTML = `<form id="power-component-form"><header class="requirement-editor-heading"><h2>Edit ${escape(element.id)}</h2><button type="button" data-power-cancel aria-label="Close component power editor">×</button></header><div class="requirement-editor-content">
      <div class="power-editor-fields"><label>Quantity<input type="number" min="1" max="1000000" step="1" data-load-field="quantity" value="${load.quantity}" ${software ? 'disabled' : ''}></label><label>Accounting<select data-load-field="accounting">${options.map(value => [value, { host: 'On execution host', counted: 'Count once', excluded: 'Excluded' }[value]]).map(([value, label]) => `<option value="${value}" ${load.accounting === value ? 'selected' : ''}>${label}</option>`).join('')}</select></label></div>
      ${software ? `<label>Execution host<select data-load-field="host"><option value=""> </option>${spacecraftComponents(getWorkspace()).filter(row => (metadata(getWorkspace()).executionHosts ?? []).includes(row.key)).map(row => `<option value="${row.key}" ${load.host === row.key ? 'selected' : ''}>${escape(row.id)}</option>`).join('')}</select></label>` : `<section class="sheet power-state-sheet"><div class="table-top"><h2>Component States</h2><button type="button" class="add-row" data-add-state aria-label="Add component state" title="Add row" ${load.states.length >= limits().states ? 'disabled' : ''}>${addIcon}</button></div><div class="table-frame"><table class="power-table" aria-label="Component states"><colgroup><col class="row-actions-col"><col class="power-state-name-col"><col class="power-state-watts-col"><col class="power-state-basis-col"><col><col></colgroup><thead><tr><th class="row-actions-heading" aria-label="Row actions"></th><th scope="col">State</th><th scope="col">Power (W)</th><th scope="col">Meaning</th><th scope="col">Source</th><th scope="col">Conditions</th></tr></thead><tbody>${load.states.map((state, index) => stateRow(state, index)).join('')}${load.states.length < limits().states ? stateRow(draft.emptyState, load.states.length, true) : ''}</tbody></table></div></section>`}
      <label>Accounting rationale<textarea data-load-field="rationale" maxlength="2000" rows="3">${escape(load.rationale)}</textarea></label></div><footer class="requirement-editor-actions"><p id="power-editor-error" role="alert"></p><button type="button" data-power-cancel>Cancel</button><button type="submit" class="primary">Save component</button></footer></form>`;
  }
  panel.addEventListener('input', event => {
    if (!draft) return;
    const input = event.target;
    if (input.dataset.loadField) draft.load[input.dataset.loadField] = input.dataset.loadField === 'quantity' ? inputNumber(input) : input.value;
    if (input.dataset.stateField) {
      const row = input.closest('[data-state-key]');
      const state = draft.load.states.find(state => state.key === row.dataset.stateKey) ?? draft.emptyState;
      state[input.dataset.stateField] = input.dataset.stateField === 'watts' ? inputNumber(input) : input.value;
      if (state === draft.emptyState && (state.name || state.watts !== null || state.source || state.conditions)) {
        draft.load.states.push(state); draft.emptyState = blankState(); row.querySelector('.row-delete').disabled = false;
        if (draft.load.states.length < limits().states) row.closest('tbody').insertAdjacentHTML('beforeend', stateRow(draft.emptyState, draft.load.states.length, true));
        panel.querySelector('[data-add-state]').disabled = draft.load.states.length >= limits().states;
      }
    }
  });
  panel.addEventListener('click', event => {
    if (event.target.closest('[data-power-cancel]')) close();
    if (event.target.closest('[data-add-state]')) panel.querySelector(`[data-state-key="${draft.emptyState.key}"] [data-state-field="name"]`)?.focus();
    const remove = event.target.closest('[data-remove-state]');
    if (remove && !remove.disabled) { draft.load.states = draft.load.states.filter(state => state.key !== remove.dataset.removeState); renderDraft(); }
  });
  function snapshot(base = getWorkspace()) {
    if (!draft) return base;
    const workspace = structuredClone(base), element = workspace.elements.find(row => row.key === draft.elementKey);
    if (!element || element.definition !== draft.definition) throw new Error('This component changed. Reopen its power editor.');
    const current = powerFor(workspace, element);
    for (const field of ['states', 'quantity', 'accounting', 'host', 'rationale']) if (JSON.stringify(current[field]) !== JSON.stringify(draft.original[field])) throw new Error('This component’s power data changed. Reopen its editor.');
    const load = { ...structuredClone(draft.load), assignments: { ...current.assignments } };
    workspace.power.loads = [...workspace.power.loads.filter(load => load.element !== element.key), load];
    return workspace;
  }
  async function save() {
    if (!draft) return false;
    panel.inert = true;
    try {
      await onChange(snapshot()); close(); return true;
    }
    catch (error) { panel.querySelector('#power-editor-error').textContent = error.message; return false; }
    finally { panel.inert = false; }
  }
  panel.addEventListener('submit', event => { event.preventDefault(); save(); });
  panel.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') { event.preventDefault(); event.stopPropagation(); save(); return; }
    if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); close(); return; }
    if (!event.target.dataset.stateField || !['Tab', 'Enter', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
    if (event.target.tagName === 'SELECT' && event.key !== 'Tab') return;
    const fields = ['name', 'watts', 'basis', 'source', 'conditions'];
    const rows = [...panel.querySelectorAll('[data-state-key]')];
    let index = rows.indexOf(event.target.closest('tr')), column = fields.indexOf(event.target.dataset.stateField);
    if (event.key === 'Tab') {
      column += event.shiftKey ? -1 : 1;
      if (column > 4) { column = 0; index++; }
      if (column < 0) { column = 4; index--; }
    } else index += event.key === 'ArrowUp' || (event.key === 'Enter' && event.shiftKey) ? -1 : 1;
    const target = rows[index]?.querySelector(`[data-state-field="${fields[column]}"]`);
    if (target) { event.preventDefault(); target.focus(); }
  });
  return { render, open, close, closeWithConfirmation, snapshot, isDirty, isOpen: () => Boolean(draft), save, reset: () => { close(); modeDraft = blankMode(); } };
}
