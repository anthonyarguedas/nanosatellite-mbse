const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const icon = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="m12 3 5 5M3 17l4-1 10-10a2.1 2.1 0 0 0-3-3L4 13l-1 4Z"/></svg>';
export { escape, icon };

export function createEditor({ panel, getWorkspace, request, onSave, onClose }) {
  let draft = null, initial = '', generation = 0, timer, saving = false;
  const payloadProperty = prop => ({ name: prop.name, unit: prop.unit, expression: prop.expression,
    bindings: prop.bindings.map(binding => ({ mode: binding.mode, expression: binding.expression })) });
  const command = () => ({ action: 'update', path: draft.path, properties: draft.properties.map(payloadProperty),
    ...(draft.conditions ? { statement: draft.statement, rationale: draft.rationale,
      conditions: draft.conditions.map(condition => ({ name: condition.name, expression: condition.expression, properties: condition.properties.map(payloadProperty) })) } : {}),
    ...(draft.imports ? { imports: draft.imports } : {}) });
  const dirty = () => Boolean(draft && JSON.stringify(command()) !== initial);
  const error = message => { const node = panel.querySelector('[data-error]'); if (node) node.textContent = message; };
  const scope = index => index === undefined ? draft : draft.conditions[index];
  const marker = index => index === undefined ? '' : `data-condition="${index}"`;
  const field = (property, condition, name, value, { readonly = false, binding } = {}) => {
    const attrs = `data-property="${property}" ${marker(condition)} data-field="${name}" ${binding === undefined ? '' : `data-binding="${binding}"`}`;
    const common = `${attrs} aria-label="${escape(name)} for ${escape(scope(condition).properties[property].name || 'new parameter')}" ${readonly ? 'readonly' : ''} autocomplete="off" spellcheck="false"`;
    return name === 'expression' ? `<textarea ${common} rows="1">${escape(value)}</textarea>` : `<input ${common} value="${escape(value)}">`;
  };
  function parameterTable(owner, condition) {
    const fixed = draft.fixed, modes = getWorkspace().modes;
    return `<div class="table-frame parameter-frame"><table aria-label="${condition === undefined ? 'Parameters' : 'Condition parameters'}"><colgroup><col class="parameter-name-col"><col class="parameter-mode-col"><col class="unit-col"><col><col class="value-col"><col class="actions-col"></colgroup><thead><tr><th>Parameter</th><th>Mode</th><th>Unit</th><th>Expression</th><th>Value</th><th aria-label="Actions"></th></tr></thead><tbody>${owner.properties.map((prop, index) => {
      const attrs = `data-property="${index}" ${marker(condition)}`;
      const result = `<span class="parameter-result" data-value="${index}" data-value-binding="-1" ${marker(condition)}></span>`;
      const defaultRow = `<tr><td>${field(index, condition, 'name', prop.name, { readonly: !prop.new || fixed })}</td><td><span class="cell-text hint">Default</span></td><td>${field(index, condition, 'unit', prop.unit, { readonly: fixed })}</td><td class="expression">${field(index, condition, 'expression', prop.expression, { readonly: fixed })}</td><td>${result}</td><td>${prop.new ? `<button type="button" class="row-delete" data-remove-property ${attrs} aria-label="Remove new parameter">×</button>` : ''}${!fixed && modes.length ? `<button type="button" class="override-add" data-add-binding ${attrs} aria-label="Add mode override for ${escape(prop.name)}" ${prop.bindings.length >= modes.length ? 'disabled' : ''}>+</button>` : ''}</td></tr>`;
      return defaultRow + prop.bindings.map((binding, bindingIndex) => `<tr class="binding-row"><td><span class="cell-text hint">${escape(prop.name)}</span></td><td><select ${attrs} data-binding="${bindingIndex}" data-field="mode" aria-label="Override mode for ${escape(prop.name)}" ${fixed ? 'disabled' : ''}>${modes.map(mode => `<option value="${escape(mode.path)}" ${binding.mode === mode.path ? 'selected' : ''}>${escape(mode.path)}</option>`).join('')}</select></td><td><span class="cell-text hint">${escape(prop.unit)}</span></td><td class="expression">${field(index, condition, 'expression', binding.expression, { readonly: fixed, binding: bindingIndex })}</td><td><span class="parameter-result" data-value="${index}" data-value-binding="${bindingIndex}" ${marker(condition)}></span></td><td>${fixed ? '' : `<button type="button" class="row-delete" data-remove-binding ${attrs} data-binding="${bindingIndex}" aria-label="Remove mode override">×</button>`}</td></tr>`).join('');
    }).join('') || '<tr><td colspan="6" class="empty">No parameters</td></tr>'}</tbody></table></div>`;
  }
  function render() {
    panel.innerHTML = `<form id="object-form"><header class="editor-heading"><div><h2 id="editor-title">${escape(draft.name)}</h2><span class="hint">${escape(draft.className)} · ${escape(draft.path)}</span></div><button type="button" data-cancel aria-label="Close editor">×</button></header><div class="editor-content">
      ${draft.conditions ? `<label for="statement">Statement</label><textarea id="statement" data-root-field="statement" rows="4">${escape(draft.statement)}</textarea><p class="hint">{condition.target} inserts a value.</p><p data-statement-preview class="statement-preview"></p><label for="rationale">Rationale</label><textarea id="rationale" data-root-field="rationale" rows="3">${escape(draft.rationale)}</textarea>` : ''}
      <section class="editor-section"><div class="section-heading"><h3>Parameters</h3>${draft.fixed ? '<span class="hint">Fixed by the product class</span>' : '<button type="button" class="text-button" data-add-property>Add parameter</button>'}</div><p class="hint">Python expressions. Blank means pending.</p>${parameterTable(draft)}</section>
      ${draft.conditions ? `<section class="editor-section"><div class="section-heading"><h3>Verification conditions</h3><button type="button" class="text-button" data-add-condition>Add condition</button></div><div data-conditions>${draft.conditions.map((condition, index) => `<article class="condition-card"><header><input data-condition-name="${index}" aria-label="Condition name" value="${escape(condition.name)}" ${condition.new ? '' : 'readonly'}><span data-condition-result="${index}" class="result"></span><button type="button" class="row-delete" data-remove-condition="${index}" aria-label="Remove condition ${escape(condition.name)}">×</button></header>${parameterTable(condition, index)}<label for="predicate-${index}">Predicate</label><textarea id="predicate-${index}" data-predicate="${index}" class="code-input" rows="2" spellcheck="false">${escape(condition.expression)}</textarea><p data-condition-message="${index}" class="diagnostic"></p></article>`).join('') || '<p class="hint">No conditions</p>'}</div></section>` : ''}
      ${draft.imports ? `<section class="editor-section"><div class="section-heading"><h3>Imports</h3><button type="button" class="text-button" data-add-import>Add import</button></div>${draft.imports.map((source, index) => `<input class="code-input import-input" data-import="${index}" aria-label="Python import" value="${escape(source)}" ${index < draft.originalImports ? 'readonly' : ''} spellcheck="false">`).join('')}</section>` : ''}
      <div data-failures class="failure-paths"></div>
      </div><footer class="editor-actions"><p class="error-text" data-error role="status" aria-live="polite"></p><button type="button" data-cancel>Cancel</button><button type="submit" class="primary">Save</button></footer></form>`;
    updateValues(draft);
  }
  function valueText(result) {
    return result?.status === 'value' ? result.value : result?.status === 'error' ? 'Error' : 'Pending';
  }
  function updateValues(detail) {
    const update = (owner, condition) => owner.properties.forEach((prop, index) => {
      const nodes = panel.querySelectorAll(`[data-value="${index}"]${condition === undefined ? ':not([data-condition])' : `[data-condition="${condition}"]`}`);
      const selected = scope(condition).properties[index]?.bindings.findIndex(binding => binding.mode === getWorkspace().mode) ?? -1;
      nodes.forEach(node => {
        const active = Number(node.dataset.valueBinding) === selected;
        node.textContent = active ? valueText(prop.assessment) : '';
        node.dataset.state = active ? prop.assessment?.status || 'pending' : '';
        node.title = active ? prop.assessment?.message || '' : '';
      });
    });
    update(detail);
    detail.conditions?.forEach((condition, index) => {
      update(condition, index);
      const node = panel.querySelector(`[data-condition-result="${index}"]`), result = condition.result;
      if (node) {
        node.textContent = result?.status === 'error' ? 'Error' : result?.value === true ? 'Pass' : result?.value === false ? 'Fail' : 'Pending';
        node.dataset.state = result?.value === false ? 'fail' : result?.status || 'pending';
      }
      const message = panel.querySelector(`[data-condition-message="${index}"]`);
      if (message) message.textContent = result?.message || '';
    });
    const preview = panel.querySelector('[data-statement-preview]');
    if (preview) { preview.textContent = detail.rendered || ''; preview.title = detail.statementMessage || ''; }
    panel.querySelector('[data-failures]').textContent = detail.verification?.failures?.join('\n') || '';
  }
  function preview() {
    clearTimeout(timer);
    const version = ++generation;
    timer = setTimeout(async () => {
      try {
        const result = await request('/api/preview', { command: command() });
        if (version !== generation || !draft) return;
        updateValues(result.workspace.detail); error('');
      } catch (failure) { if (version === generation) error(failure.message); }
    }, 400);
  }
  function close(force = false) {
    if (saving || (!force && dirty() && !window.confirm('Discard unsaved changes?'))) return false;
    clearTimeout(timer); generation++; draft = null; panel.hidden = true;
    document.body.classList.remove('editor-open'); onClose(); return true;
  }
  function open(detail) {
    clearTimeout(timer); generation++;
    draft = structuredClone(detail);
    draft.originalImports = draft.imports?.length || 0;
    initial = JSON.stringify(command());
    render(); panel.hidden = false; document.body.classList.add('editor-open');
    panel.querySelector('textarea, input:not([readonly]), [data-cancel]')?.focus();
  }
  panel.addEventListener('input', event => {
    const input = event.target, data = input.dataset;
    if (data.rootField) draft[data.rootField] = input.value;
    else if (data.conditionName !== undefined) draft.conditions[data.conditionName].name = input.value;
    else if (data.predicate !== undefined) draft.conditions[data.predicate].expression = input.value;
    else if (data.import !== undefined) draft.imports[data.import] = input.value;
    else if (data.property !== undefined && data.field) {
      const prop = scope(data.condition).properties[data.property];
      const target = data.binding === undefined ? prop : prop.bindings[data.binding];
      target[data.field] = data.field === 'expression' && !input.value.trim() ? null : input.value;
    }
    preview();
  });
  panel.addEventListener('click', event => {
    const button = event.target.closest('button'); if (!button || saving) return;
    const data = button.dataset;
    if ('cancel' in data) { close(); return; }
    if ('addProperty' in data) draft.properties.push({ name: '', expression: null, unit: '', bindings: [], new: true });
    else if ('removeProperty' in data) scope(data.condition).properties.splice(Number(data.property), 1);
    else if ('addBinding' in data) {
      const prop = scope(data.condition).properties[data.property], modes = getWorkspace().modes;
      const mode = modes.find(item => item.path === getWorkspace().mode && !prop.bindings.some(binding => binding.mode === item.path))
        || modes.find(item => !prop.bindings.some(binding => binding.mode === item.path));
      if (mode) prop.bindings.push({ mode: mode.path, expression: null });
    } else if ('removeBinding' in data) scope(data.condition).properties[data.property].bindings.splice(Number(data.binding), 1);
    else if ('addCondition' in data) draft.conditions.push({ name: '', expression: 'measure <= target', new: true,
      properties: ['measure', 'target'].map(name => ({ name, expression: null, unit: '', bindings: [] })) });
    else if ('removeCondition' in data) draft.conditions.splice(Number(data.removeCondition), 1);
    else if ('addImport' in data) draft.imports.push('import package as alias');
    else return;
    render(); preview();
    if ('addProperty' in data) panel.querySelector('input[data-field="name"]:not([readonly]):last-of-type')?.focus();
    if ('addCondition' in data) panel.querySelector('[data-condition-name]:not([readonly])')?.focus();
  });
  panel.addEventListener('submit', async event => {
    event.preventDefault(); if (saving) return;
    clearTimeout(timer); generation++; saving = true;
    panel.querySelectorAll('button').forEach(button => { button.disabled = true; }); error('');
    try {
      const result = await request('/api/commands', { command: command() });
      saving = false; onSave(result); close(true);
    } catch (failure) {
      saving = false; panel.querySelectorAll('button').forEach(button => { button.disabled = false; }); error(failure.message);
    }
  });
  return { open, close, dirty, path: () => draft?.path, isOpen: () => !panel.hidden, refresh: preview };
}
