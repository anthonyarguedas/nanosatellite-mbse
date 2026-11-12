import { metadata } from '/workbook.js';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const inputNumber = input => input.value.trim() === '' ? null : Number(input.value);
const blankMode = () => ({ key: crypto.randomUUID(), name: '', sunlight: null, eclipse: null });
const addIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>';
const deleteIcon = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 5h12M8 3h4M6 5l1 12h6l1-12M9 8v6M11 8v6"/></svg>';

export function createPowerTable({ section, getWorkspace, getActive, onCommand, onError }) {
  let modeDraft = blankMode();
  const limits = () => metadata(getWorkspace()).limits;

  function render() {
    section.hidden = getActive() !== 'mission';
    if (section.hidden) { section.replaceChildren(); return; }
    const modes = getWorkspace().power.modes;
    const modeRows = [...modes, ...(modes.length < limits().modes ? [modeDraft] : [])];
    section.innerHTML = `<section class="sheet power-modes"><div class="table-top"><h2>Spacecraft Modes</h2><button type="button" class="add-row" data-power-add-mode aria-label="Add spacecraft mode" title="Add row" ${modes.length >= limits().modes ? 'disabled' : ''}>${addIcon}</button></div>
      <div class="table-frame"><table class="power-table" aria-label="Spacecraft modes"><colgroup><col class="row-actions-col"><col><col class="power-share-col"><col class="power-share-col"></colgroup><thead><tr><th class="row-actions-heading" aria-label="Row actions"></th><th scope="col">Mode</th><th scope="col">Sunlight (%)</th><th scope="col">Eclipse (%)</th></tr></thead><tbody>${modeRows.map((mode, index) => `<tr data-mode-row="${mode.key}"><td class="row-actions"><button type="button" class="row-delete" data-power-remove-mode="${mode.key}" aria-label="Delete mode ${escape(mode.name || index + 1)}" ${mode === modeDraft ? 'disabled' : ''}>${deleteIcon}</button></td><td><input data-mode-key="${mode.key}" data-mode-field="name" value="${escape(mode.name)}" maxlength="80" aria-label="Mode name, row ${index + 1}"></td>${['sunlight', 'eclipse'].map(period => `<td><input type="number" min="0" max="100" step="any" data-mode-key="${mode.key}" data-mode-field="${period}" value="${mode[period] ?? ''}" aria-label="${period === 'sunlight' ? 'Sunlight' : 'Eclipse'} share, row ${index + 1}"></td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`;
  }

  async function command(operation) {
    try { await onCommand(operation); render(); return true; }
    catch (error) { onError(error.message); render(); return false; }
  }
  section.addEventListener('change', async event => {
    const input = event.target;
    if (!input.dataset.modeKey) return;
    if (input.dataset.modeKey === modeDraft.key) {
      modeDraft[input.dataset.modeField] = input.dataset.modeField === 'name' ? input.value.trim() : inputNumber(input);
      if (!modeDraft.name) return;
      const added = structuredClone(modeDraft);
      if (await command({ name: 'add_mode', label: added.name, key: added.key, sunlight: added.sunlight, eclipse: added.eclipse })) modeDraft = blankMode();
      render();
    } else await command(input.dataset.modeField === 'name'
      ? { name: 'rename_mode', target: input.dataset.modeKey, label: input.value.trim() }
      : { name: 'configure_mode', target: input.dataset.modeKey, [input.dataset.modeField]: inputNumber(input) });
  });
  section.addEventListener('click', event => {
    if (event.target.closest('[data-power-add-mode]')) section.querySelector(`[data-mode-key="${modeDraft.key}"][data-mode-field="name"]`)?.focus();
    const removeMode = event.target.closest('[data-power-remove-mode]');
    if (removeMode && !removeMode.disabled) return command({ name: 'remove_mode', target: removeMode.dataset.powerRemoveMode });
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
  return { render, reset: () => { modeDraft = blankMode(); } };
}
