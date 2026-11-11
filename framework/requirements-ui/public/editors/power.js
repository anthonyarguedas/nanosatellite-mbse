import { powerFor, spacecraftComponents, metadata } from '/workbook.js';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const inputNumber = input => input.value.trim() === '' ? null : Number(input.value);
const key = () => crypto.randomUUID();
const blankMode = () => ({ key: key(), name: '', sunlight: null, eclipse: null });
const blankState = () => ({ key: key(), name: '', watts: null });
const addIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>';
const deleteIcon = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 5h12M8 3h4M6 5l1 12h6l1-12M9 8v6M11 8v6"/></svg>';

export function createPowerTable({ section, getWorkspace, getActive, onChange, onCommand, onError }) {
  let modeDraft = blankMode(), showOthers = false, epoch = 0, edits = Promise.resolve();
  const stateDrafts = new Map();
  const limits = () => metadata(getWorkspace()).limits;
  // Presentation adapter for saved single-state sessions. Python validates
  // allocations and calculates all power and energy values.
  const entriesFor = (load, mode) => load.allocations?.[mode] ?? (load.assignments?.[mode]
    ? [{ state: load.assignments[mode], duty: load.duties?.[mode] ?? 100 }] : []);

  function allocationRows(element, modes, workspace) {
    const load = powerFor(workspace, element), pending = stateDrafts.get(element.key);
    const states = load.states.map(state => ({ state, draft: false }));
    if (pending && !load.states.some(state => state.key === pending.key)) states.push({ state: pending, draft: true });
    if (!states.length) states.push({ state: null, draft: false });
    const options = metadata(workspace).accountingOptions?.[element.key] ?? ['counted', 'excluded'];
    const software = options.includes('host');
    const loss = metadata(workspace).objects?.[element.key]?.className === 'PowerLoss';
    const hosts = spacecraftComponents(workspace).filter(row => (metadata(workspace).executionHosts ?? []).includes(row.key));
    return states.map(({ state, draft }, index) => `<tr data-power-row="${element.key}" class="${index === 0 ? 'power-component-start' : ''} ${loss ? 'power-loss-row' : ''}">
      ${index === 0 ? `<td rowspan="${states.length}" class="power-component-label"><strong>${escape(element.id)}</strong><span>${escape(element.name)}</span>${loss ? '<small>Explicit loss</small>' : ''}
        <label class="power-quantity">Quantity<input type="number" min="1" max="1000000" step="1" data-power-load="${element.key}" data-load-field="quantity" value="${load.quantity}" aria-label="${escape(element.id)} quantity" ${software ? 'disabled' : ''}></label>
        ${!software ? `<button type="button" class="power-add-state" data-power-add-state="${element.key}" aria-label="Add state for ${escape(element.id)}" ${load.states.length >= limits().states ? 'disabled' : ''}>${addIcon}<span>Add state</span></button>` : ''}</td>
        <td rowspan="${states.length}" class="power-accounting"><select data-power-load="${element.key}" data-load-field="accounting" aria-label="${escape(element.id)} accounting">${options.map(value => `<option value="${value}" ${load.accounting === value ? 'selected' : ''}>${{ host: 'On execution host', counted: 'Count once', excluded: 'Excluded' }[value]}</option>`).join('')}</select>
        ${software ? `<label>Execution host<select data-power-load="${element.key}" data-load-field="host" aria-label="${escape(element.id)} execution host"><option value=""> </option>${hosts.map(host => `<option value="${host.key}" ${load.host === host.key ? 'selected' : ''}>${escape(host.id)}</option>`).join('')}</select></label>` : ''}</td>` : ''}
      <td class="power-state-label">${state ? `<div class="power-state-name"><button type="button" class="row-delete" data-power-remove-state="${element.key}" data-state="${state.key}" aria-label="Delete ${escape(state.name || 'new state')} for ${escape(element.id)}">${deleteIcon}</button><input data-power-name="${element.key}" data-state="${state.key}" value="${escape(state.name)}" maxlength="80" placeholder="State name" aria-label="${draft ? 'New state name for' : 'State name for'} ${escape(element.id)}${draft ? '' : ` ${escape(state.name)}`}"></div>` : '<span class="power-no-states">No states</span>'}</td>
      <td>${state ? `<input type="text" data-power-watts="${element.key}" data-state="${state.key}" value="${escape(state.watts ?? '')}" maxlength="5000" autocomplete="off" spellcheck="false" placeholder="W or expression" title="${escape(state.watts ?? '')}" aria-label="${escape(element.id)} ${escape(state.name || 'new state')} power in W">` : ''}</td>
      ${modes.map(mode => {
        const entry = state && entriesFor(load, mode.key).find(item => item.state === state.key);
        return `<td>${state ? `<label class="power-duty"><input type="number" min="0" max="100" step="any" data-power-duty="${element.key}" data-mode="${mode.key}" data-state="${state.key}" value="${escape(entry ? entry.duty : '')}" placeholder="Unset" aria-label="${escape(element.id)} ${escape(state.name || 'new state')} duty percentage in ${escape(mode.name)}" ${draft || load.accounting !== 'counted' ? 'disabled' : ''}><span>%</span></label>` : ''}</td>`;
      }).join('')}</tr>`).join('');
  }

  function render() {
    const workspace = getWorkspace(), active = getActive(), mission = active === 'mission';
    section.hidden = !mission && !(metadata(workspace).powerScopes ?? []).some(scope => scope.key === active && scope.kind === 'subsystem');
    if (section.hidden) { section.replaceChildren(); return; }
    const modes = workspace.power.modes;
    const modeRows = [...modes, ...(modes.length < limits().modes ? [modeDraft] : [])];
    const allComponents = spacecraftComponents(workspace).filter(element => element.owner === active);
    const components = allComponents.filter(element => showOthers || powerFor(workspace, element).accounting === 'counted');
    const others = allComponents.some(element => powerFor(workspace, element).accounting !== 'counted');
    section.innerHTML = `${mission ? `<section class="sheet power-modes"><div class="table-top"><h2>Spacecraft Modes</h2><button type="button" class="add-row" data-power-add-mode aria-label="Add spacecraft mode" title="Add row" ${modes.length >= limits().modes ? 'disabled' : ''}>${addIcon}</button></div>
      <div class="table-frame"><table class="power-table" aria-label="Spacecraft modes"><colgroup><col class="row-actions-col"><col><col class="power-share-col"><col class="power-share-col"></colgroup><thead><tr><th class="row-actions-heading" aria-label="Row actions"></th><th scope="col">Mode</th><th scope="col">Sunlight (%)</th><th scope="col">Eclipse (%)</th></tr></thead><tbody>${modeRows.map((mode, index) => `<tr data-mode-row="${mode.key}"><td class="row-actions"><button type="button" class="row-delete" data-power-remove-mode="${mode.key}" aria-label="Delete mode ${escape(mode.name || index + 1)}" ${mode === modeDraft ? 'disabled' : ''}>${deleteIcon}</button></td><td><input data-mode-key="${mode.key}" data-mode-field="name" value="${escape(mode.name)}" maxlength="80" aria-label="Mode name, row ${index + 1}"></td>${['sunlight', 'eclipse'].map(period => `<td><input type="number" min="0" max="100" step="any" data-mode-key="${mode.key}" data-mode-field="${period}" value="${mode[period] ?? ''}" aria-label="${period === 'sunlight' ? 'Sunlight' : 'Eclipse'} share, row ${index + 1}"></td>`).join('')}</tr>`).join('')}</tbody></table></div></section>` : ''}
      ${!mission ? `<section class="sheet power-allocations"><div class="table-top"><h2>Component State Allocation</h2>${others ? `<label class="power-show-others"><input type="checkbox" data-power-show-others ${showOthers ? 'checked' : ''}>Show other components</label>` : ''}${metadata(workspace).powerLossDefinitions?.[active] ? `<button type="button" class="power-add-loss" data-power-add-loss>${addIcon}<span>Add loss</span></button>` : ''}</div>
      <p class="power-allocation-help">Edit states, powers and duties here. Duties for one component total at most 100%. Unallocated time contributes zero power. Add an Off state for a complete zero-power mode.</p>
      <div class="table-frame"><table class="power-table" aria-label="Component state allocation"><colgroup><col class="power-reference-col"><col class="power-accounting-col"><col class="power-state-name-col"><col class="power-state-watts-col">${modes.map(() => '<col class="power-mode-col">').join('')}</colgroup><thead><tr><th scope="col">Component</th><th scope="col">Accounting</th><th scope="col">State</th><th scope="col">Power per unit (W)</th>${modes.map(mode => `<th scope="col">${escape(mode.name)}<small>Duty (%)</small></th>`).join('')}</tr></thead><tbody>${components.map(element => allocationRows(element, modes, workspace)).join('')}</tbody></table></div>
      ${!modes.length ? '<p class="power-allocation-help">Add spacecraft modes in Mission to allocate state duties.</p>' : ''}</section>` : ''}`;
  }

  function change(mutator) {
    const version = epoch;
    const task = edits.then(async () => {
      if (version !== epoch) return false;
      try { const candidate = structuredClone(getWorkspace()); mutator(candidate); await onChange(candidate); return true; }
      catch (error) { onError(error.message); render(); return false; }
    });
    edits = task;
    return task;
  }
  async function command(operation) {
    try { await onCommand(operation); render(); return true; }
    catch (error) { onError(error.message); render(); return false; }
  }
  function editableLoad(workspace, elementKey) {
    let load = workspace.power.loads.find(load => load.element === elementKey);
    if (!load) {
      load = structuredClone(powerFor(workspace, workspace.elements.find(row => row.key === elementKey)));
      workspace.power.loads.push(load);
    }
    return load;
  }
  function updateStateDraft(input) {
    const elementKey = input.dataset.powerName ?? input.dataset.powerWatts;
    const draft = stateDrafts.get(elementKey);
    if (!draft || draft.key !== input.dataset.state) return null;
    draft[input.dataset.powerName ? 'name' : 'watts'] = input.dataset.powerName ? input.value : input.value.trim() || null;
    return draft;
  }
  section.addEventListener('input', event => updateStateDraft(event.target));
  section.addEventListener('change', async event => {
    const input = event.target;
    if (input.matches?.('[data-power-show-others]')) { showOthers = input.checked; render(); return; }
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
      return;
    }
    const elementKey = input.dataset.powerName ?? input.dataset.powerWatts ?? input.dataset.powerDuty ?? input.dataset.powerLoad;
    if (!elementKey) return;
    const draft = updateStateDraft(input);
    if (draft) {
      if (!draft.name.trim()) return;
      const added = { ...draft, name: draft.name.trim() };
      if (await change(workspace => {
        const load = editableLoad(workspace, elementKey);
        const current = load.states.find(state => state.key === added.key);
        if (current) Object.assign(current, added);
        else load.states.push(added);
      })) stateDrafts.delete(elementKey);
      return;
    }
    if (input.dataset.loadField === 'accounting' && input.value !== 'counted') showOthers = true;
    await change(workspace => {
      const load = editableLoad(workspace, elementKey);
      if (input.dataset.powerName) load.states.find(state => state.key === input.dataset.state).name = input.value.trim();
      else if (input.dataset.powerWatts) load.states.find(state => state.key === input.dataset.state).watts = input.value.trim() || null;
      else if (input.dataset.powerLoad) load[input.dataset.loadField] = input.dataset.loadField === 'quantity' ? inputNumber(input) : input.value;
      else {
        const mode = input.dataset.mode, value = inputNumber(input);
        const entries = entriesFor(load, mode).filter(item => item.state !== input.dataset.state);
        if (value !== null) entries.push({ state: input.dataset.state, duty: value });
        load.allocations ??= {};
        load.allocations[mode] = entries;
        delete load.assignments[mode];
        if (load.duties) delete load.duties[mode];
      }
    });
  });

  function addState(elementKey) {
    const load = powerFor(getWorkspace(), getWorkspace().elements.find(row => row.key === elementKey));
    if (!load || load.states.length >= limits().states) return;
    if (!stateDrafts.has(elementKey)) stateDrafts.set(elementKey, blankState());
    render();
    section.querySelector(`[data-power-name="${elementKey}"][data-state="${stateDrafts.get(elementKey).key}"]`)?.focus();
  }
  section.addEventListener('click', async event => {
    if (event.target.closest('[data-power-add-loss]')) {
      const definition = metadata(getWorkspace()).powerLossDefinitions?.[getActive()];
      if (definition) {
        const elementKey = key();
        if (await command({ name: 'add_element', definition, owner: getActive(), key: elementKey })) addState(elementKey);
      }
      return;
    }
    const add = event.target.closest('[data-power-add-state]');
    if (add && !add.disabled) { addState(add.dataset.powerAddState); return; }
    const removeState = event.target.closest('[data-power-remove-state]');
    if (removeState) {
      const elementKey = removeState.dataset.powerRemoveState, stateKey = removeState.dataset.state;
      if (stateDrafts.get(elementKey)?.key === stateKey) { stateDrafts.delete(elementKey); render(); }
      else await change(workspace => {
        const load = editableLoad(workspace, elementKey);
        load.states = load.states.filter(state => state.key !== stateKey);
      });
      return;
    }
    if (event.target.closest('[data-power-add-mode]')) section.querySelector(`[data-mode-key="${modeDraft.key}"][data-mode-field="name"]`)?.focus();
    const removeMode = event.target.closest('[data-power-remove-mode]');
    if (removeMode && !removeMode.disabled) command({ name: 'remove_mode', target: removeMode.dataset.powerRemoveMode });
  });
  section.addEventListener('keydown', event => {
    const input = event.target;
    if (!input.dataset.modeKey) {
      if (event.key === 'Enter' && (input.dataset.powerName || input.dataset.powerWatts || input.dataset.powerDuty || input.dataset.powerLoad)) { event.preventDefault(); input.blur(); }
      return;
    }
    if (!['Tab', 'Enter', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
    const fields = ['name', 'sunlight', 'eclipse'], field = fields.indexOf(input.dataset.modeField), modeKey = input.dataset.modeKey;
    event.preventDefault(); input.blur();
    const rows = [...section.querySelectorAll('[data-mode-row]')], index = rows.findIndex(row => row.dataset.modeRow === modeKey);
    let rowIndex = index, column = field;
    if (event.key === 'Tab') { column += event.shiftKey ? -1 : 1; if (column > 2) { rowIndex++; column = 0; } if (column < 0) { rowIndex--; column = 2; } }
    else rowIndex += event.key === 'ArrowUp' || (event.key === 'Enter' && event.shiftKey) ? -1 : 1;
    rows[rowIndex]?.querySelector(`[data-mode-field="${fields[column]}"]`)?.focus();
  });
  return { render, reset: () => { epoch++; modeDraft = blankMode(); showOthers = false; stateDrafts.clear(); } };
}
