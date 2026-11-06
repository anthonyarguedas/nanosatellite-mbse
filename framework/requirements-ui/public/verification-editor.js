import { nextId, parameterExpression, rewriteRowReferences } from '/model.mjs';
import { expressionReferences } from '/expression-metadata.mjs';
import { runKey, scriptContext, scriptInstance, setVerificationMethods, verificationMethods } from '/verification-methods.mjs';
import { parameterValueHTML } from '/requirement-preview.js';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const blank = () => ({ key: crypto.randomUUID(), condition: '' });
const label = state => ({ pass: 'TRUE', fail: 'FALSE', pending: 'PENDING', error: 'ERROR', unset: '' })[state] ?? '';

export function createVerificationEditor({ container, getWorkspace, getRow, snapshot, onChange, onError,
  getScriptResults, onScriptResults, getScriptInputs }) {
  const table = container.querySelector('[data-method-table]');
  const library = container.querySelector('[data-script-library]');
  const scriptList = container.querySelector('[data-script-list]');
  const addDefinition = container.querySelector('[data-script-add-definition]');
  const message = container.querySelector('[data-script-message]');
  let methods = [], definitions = [], columns = '', active = false, runController = null, running = '', lifecycle = 0;
  let currentResult = null, currentPreview = '', catalogLoaded = false;
  const ids = new Map(), expanded = new Set();
  const workspace = () => getWorkspace();
  const store = () => setVerificationMethods(getRow(), methods);
  function renderMethods(force = false) {
    if (!active) return;
    const populated = methods.filter(method => method.condition.trim() || method.script);
    const empty = methods.find(method => !method.condition.trim() && !method.script) ?? blank();
    methods = [...populated, ...(populated.length < 32 ? [empty] : [])];
    const scripts = workspace().scripts;
    const signature = JSON.stringify([methods.map(({ key, script }) => ({ key, script })), scripts.map(({ key, id, name }) => ({ key, id, name }))]);
    if (!force && columns === signature) return;
    columns = signature;
    const focused = document.activeElement, key = focused?.closest('[data-method-key]')?.dataset.methodKey;
    const field = focused?.dataset.methodField;
    const selection = typeof focused?.selectionStart === 'number' ? [focused.selectionStart, focused.selectionEnd] : null;
    table.innerHTML = '<colgroup><col class="row-actions-col"><col class="verification-source-col"><col><col class="verification-result-col"></colgroup><thead><tr><th aria-label="Row actions"></th><th scope="col">Values from</th><th scope="col">Python condition</th><th scope="col">Result</th></tr></thead><tbody>'
      + methods.map((method, index) => `<tr data-method-key="${method.key}"><td class="row-actions"><button type="button" class="row-delete" data-remove-method="${method.key}" aria-label="Delete verification method ${index + 1}" ${method.condition.trim() || method.script ? '' : 'disabled'}>×</button></td><td><select data-method-field="script" aria-label="Values for verification method ${index + 1}"><option value="">Requirement values</option>${scripts.map(script => `<option value="${script.key}" ${method.script === script.key ? 'selected' : ''}>${escape(script.id)} · ${escape(script.name)}</option>`).join('')}</select>${method.script ? `<button type="button" class="verification-run" data-run-script="${method.script}" aria-label="Run ${escape(scripts.find(script => script.key === method.script)?.id)}">Run Python</button>` : ''}</td><td><input ${index === 0 ? 'id="requirement-condition"' : ''} data-method-field="condition" aria-label="${index === 0 ? 'Verification condition' : `Verification condition ${index + 1}`}" maxlength="5000" spellcheck="false" autocomplete="off" value="${escape(method.condition)}" placeholder="${method.script ? `${escape(scripts.find(script => script.key === method.script)?.id)}.output <= limit` : 'energy_J >= REQ001.energy_J'}"><span class="verification-message" hidden></span></td><td><span class="verification-method-result" role="status"></span></td></tr>`).join('') + '</tbody>';
    const target = key && field ? table.querySelector(`[data-method-key="${key}"] [data-method-field="${field}"]`) : null;
    if (target) { target.focus({ preventScroll: true }); if (selection) target.setSelectionRange(...selection); }
    container.querySelector('[data-add-method]').disabled = populated.length >= 32;
  }
  function renderScripts() {
    if (!active) return;
    scriptList.innerHTML = workspace().scripts.map(script => {
      const current = definitions.find(definition => definition.id === script.definition);
      return `<details class="python-script" data-script-key="${script.key}" ${expanded.has(script.key) ? 'open' : ''}><summary><code>${escape(script.id)}</code> ${escape(script.name)}</summary><div class="script-fields"><label>ID<input data-script-field="id" value="${escape(script.id)}" maxlength="6" autocomplete="off"></label><label>Name<input data-script-field="name" value="${escape(script.name)}" maxlength="80" autocomplete="off"></label></div><p><code>${escape(script.definition)}.py</code> · ${escape(script.revision.slice(0, 12))}</p>${current && current.revision !== script.revision ? '<button type="button" data-update-script>Update definition</button><p>The registered script changed. Review its new interface before running.</p>' : catalogLoaded && !current ? '<p>This definition is not registered on this server.</p>' : ''}<div class="verification-frame"><table aria-label="${escape(script.id)} inputs"><thead><tr><th scope="col">Input</th><th scope="col">Expression</th><th scope="col">Value</th></tr></thead><tbody>${script.inputs.map(input => `<tr><th scope="row"><code>${escape(input.name)}</code>${input.unit ? ` (${escape(input.unit)})` : ''}</th><td class="parameter"><textarea data-script-input="${input.name}" aria-label="${escape(script.id)} ${input.name} expression" rows="1" maxlength="5000" spellcheck="false">${escape(script.parameters[input.name])}</textarea></td><td><span data-script-input-result="${input.name}" class="parameter-result"></span></td></tr>`).join('')}</tbody></table></div><div class="verification-frame"><table aria-label="${escape(script.id)} outputs"><thead><tr><th scope="col">Output reference</th><th scope="col">Type</th><th scope="col">Value</th></tr></thead><tbody>${script.outputs.map(output => `<tr><th scope="row"><code>${escape(script.id)}.${escape(output.name)}</code></th><td>${escape(output.type)}</td><td><span data-script-output="${output.name}" class="parameter-result"></span></td></tr>`).join('')}</tbody></table></div><p data-script-status role="status"></p><div class="script-actions"><button type="button" data-run-script="${script.key}" aria-label="Run ${escape(script.id)}">Run Python</button><button type="button" data-delete-script>Delete script</button></div></details>`;
    }).join('');
    update(currentResult, currentPreview);
  }
  async function loadDefinitions() {
    const token = lifecycle;
    try {
      const response = await fetch('/api/scripts'), data = await response.json();
      if (!response.ok) throw new Error(data.error);
      if (!active || token !== lifecycle) return;
      definitions = data.scripts; catalogLoaded = true;
      addDefinition.innerHTML = '<option value="">Choose a registered script…</option>' + definitions.map(definition => `<option value="${definition.id}">${escape(definition.name)}</option>`).join('');
      message.textContent = definitions.length ? '' : 'No registered Python scripts. Add a .py file and its .json interface to the server script directory.';
      renderScripts();
    } catch (error) { if (active && token === lifecycle) message.textContent = error.message; }
  }
  library.addEventListener('toggle', event => {
    if (event.target === library && library.open && active) { update(currentResult, currentPreview); loadDefinitions(); }
  });
  scriptList.addEventListener('toggle', event => {
    if (!event.target.dataset.scriptKey) return;
    if (event.target.open) expanded.add(event.target.dataset.scriptKey);
    else expanded.delete(event.target.dataset.scriptKey);
    if (active && library.open) update(currentResult, currentPreview);
  }, true);
  function changed() { store(); renderMethods(); onChange(); }
  table.addEventListener('input', event => {
    if (!active || event.target.dataset.methodField !== 'condition') return;
    methods.find(method => method.key === event.target.closest('[data-method-key]').dataset.methodKey).condition = event.target.value;
    changed();
  });
  table.addEventListener('change', event => {
    if (!active || event.target.dataset.methodField !== 'script') return;
    const method = methods.find(method => method.key === event.target.closest('[data-method-key]').dataset.methodKey);
    if (event.target.value) method.script = event.target.value;
    else delete method.script;
    changed();
  });
  container.addEventListener('click', event => {
    const remove = event.target.closest('[data-remove-method]');
    if (remove && active) { methods = methods.filter(method => method.key !== remove.dataset.removeMethod); store(); renderMethods(true); onChange(); }
    if (event.target.closest('[data-add-method]')) {
      renderMethods(); table.querySelector('tbody tr:last-child [data-method-field="condition"]')?.focus();
    }
  });
  container.querySelector('[data-script-add]').addEventListener('click', () => {
    const definition = definitions.find(definition => definition.id === addDefinition.value);
    if (!active || !definition) { message.textContent = 'Choose a registered script first.'; return; }
    if (workspace().scripts.length >= 64) { message.textContent = 'A workspace supports up to 64 script instances.'; return; }
    const script = scriptInstance(definition, { key: crypto.randomUUID(), id: nextId(workspace(), 'Script') });
    workspace().scripts.push(script); ids.set(script.key, script.id); expanded.add(script.key);
    renderScripts(); renderMethods(true); onChange();
  });
  addDefinition.addEventListener('change', () => {
    message.textContent = definitions.find(definition => definition.id === addDefinition.value)?.description ?? '';
  });
  scriptList.addEventListener('input', event => {
    if (!active) return;
    const script = workspace().scripts.find(script => script.key === event.target.closest('[data-script-key]')?.dataset.scriptKey);
    if (!script) return;
    try {
      if (event.target.dataset.scriptInput) {
        script.parameters[event.target.dataset.scriptInput] = event.target.value.trim() ? event.target.value : null;
        parameterExpression(script.parameters[event.target.dataset.scriptInput], { name: event.target.dataset.scriptInput }, script.id);
      } else if (event.target.dataset.scriptField) {
        const field = event.target.dataset.scriptField;
        script[field] = field === 'id' ? event.target.value.toUpperCase() : event.target.value;
        if (field === 'id') event.target.value = script.id;
      } else return;
      onChange();
    } catch (error) { onChange(); onError(error.message); }
  });
  scriptList.addEventListener('beforeinput', event => {
    if (event.target.dataset.scriptInput && ['insertLineBreak', 'insertParagraph'].includes(event.inputType)) event.preventDefault();
  });
  scriptList.addEventListener('change', event => {
    if (!active || event.target.dataset.scriptField !== 'id') return;
    const script = workspace().scripts.find(script => script.key === event.target.closest('[data-script-key]').dataset.scriptKey);
    const previous = ids.get(script.key);
    if (/^[A-Z]{3}\d{3}$/.test(script.id) && ![...workspace().scripts, ...workspace().statements].some(row => row.key !== script.key && row.id === script.id)) {
      rewriteRowReferences(workspace(), new Map([[previous, script.id]])); ids.set(script.key, script.id);
      methods = [...structuredClone(verificationMethods(getRow())), blank()];
    }
    renderMethods(true); renderScripts(); onChange();
  });
  scriptList.addEventListener('click', event => {
    const script = workspace().scripts.find(script => script.key === event.target.closest('[data-script-key]')?.dataset.scriptKey);
    if (!script || !active) return;
    try {
      if (event.target.closest('[data-delete-script]')) {
        const others = workspace().statements.flatMap(row => [row.condition, ...(row.verifications ?? []).map(method => method.condition), ...Object.values(row.parameters)])
          .concat(workspace().scripts.filter(row => row.key !== script.key).flatMap(row => Object.values(row.parameters)));
        const referenced = others.some(source => {
          if (!source?.trim()) return false;
          return expressionReferences(source).some(reference => reference.id === script.id);
        });
        if (referenced || workspace().statements.some(row => row.sources.includes(script.key) || verificationMethods(row).some(method => method.script === script.key))) throw new Error('Remove expression and verification references before deleting this script.');
        workspace().scripts = workspace().scripts.filter(row => row.key !== script.key);
        renderScripts(); renderMethods(true); onChange();
      } else if (event.target.closest('[data-update-script]')) {
        const definition = definitions.find(definition => definition.id === script.definition), replacement = scriptInstance(definition, script);
        replacement.name = script.name;
        for (const input of replacement.inputs) replacement.parameters[input.name] = script.parameters[input.name] ?? null;
        Object.assign(script, replacement); renderScripts(); onChange();
      }
    } catch (error) { onError(error.message); }
  });
  container.addEventListener('click', async event => {
    const button = event.target.closest('[data-run-script]');
    if (!button || !active || running) return;
    const key = button.dataset.runScript, token = lifecycle;
    try {
      const state = snapshot();
      running = key; runController = new AbortController(); update(null);
      message.textContent = 'Running Python for every configured mode…';
      const response = await fetch('/api/scripts/run', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace: state, script: key }), signal: runController.signal });
      const evidence = await response.json();
      if (!response.ok) throw new Error(evidence.error);
      if (!active || token !== lifecycle) return;
      if (evidence.signature !== scriptContext(snapshot())) throw new Error('Calculation inputs changed during execution. Run Python again.');
      const previous = getScriptResults();
      onScriptResults({ signature: evidence.signature, runs: { ...(previous?.signature === evidence.signature ? previous.runs : {}), ...evidence.runs } });
      message.textContent = 'Execution completed. Results remain valid until calculation inputs change.';
      onChange();
    } catch (error) { if (active && token === lifecycle && error.name !== 'AbortError') { message.textContent = error.message; onError(error.message); } }
    finally { if (token === lifecycle) { running = ''; runController = null; update(null); } }
  });
  function update(result, previewMode = currentPreview) {
    if (!active) return;
    currentResult = result; currentPreview = previewMode;
    for (const tr of table.querySelectorAll('[data-method-key]')) {
      const method = methods.find(method => method.key === tr.dataset.methodKey);
      const index = methods.filter(method => method.condition.trim() || method.script).findIndex(item => item.key === method.key);
      const check = result?.methods?.[index] ?? (method.condition.trim() || method.script ? { state: 'pending', message: 'Recalculating…' } : { state: 'unset', message: '' });
      const output = tr.querySelector('.verification-method-result'), error = tr.querySelector('.verification-message');
      tr.dataset.state = check.state; output.textContent = label(check.state); output.title = check.message;
      error.hidden = check.state !== 'error'; error.textContent = check.state === 'error' ? check.message : '';
      tr.querySelector('[data-method-field="condition"]').setAttribute('aria-invalid', String(check.state === 'error'));
    }
    for (const button of container.querySelectorAll('[data-run-script]')) { button.disabled = Boolean(running); button.textContent = button.dataset.runScript === running ? 'Running…' : 'Run Python'; }
    if (!library.open) return;
    const modes = workspace().power.modes.length ? workspace().power.modes : [{ key: null, name: '' }];
    const selected = previewMode && modes.some(mode => mode.key === previewMode) ? modes.filter(mode => mode.key === previewMode) : modes;
    const evidence = getScriptResults(), fresh = evidence?.signature === scriptContext(workspace());
    const inputResults = getScriptInputs();
    for (const element of scriptList.querySelectorAll('[data-script-key][open]')) {
      const script = workspace().scripts.find(script => script.key === element.dataset.scriptKey);
      const runs = selected.map(mode => fresh ? evidence.runs[runKey(script.key, mode.key)] : null);
      const display = (output, cells, unit) => {
        const same = cells.every(cell => cell.state === 'value' && cell.value === cells[0].value);
        output.innerHTML = same ? typeof cells[0].value === 'boolean' ? String(cells[0].value) : parameterValueHTML(cells[0].value, unit) : '';
        if (!same) output.textContent = cells.every(cell => cell.state === 'value') ? 'By mode' : cells.some(cell => cell.state === 'error') ? 'Error' : 'Pending';
        output.title = cells.map((cell, index) => `${selected[index].name}: ${cell.message ?? cell.value ?? 'Pending'}`).join('\n');
      };
      const aggregate = inputResults.get(script.key);
      for (const input of script.inputs) display(element.querySelector(`[data-script-input-result="${input.name}"]`), selected.map(mode =>
        (aggregate?.modes?.find(result => result.mode === mode.key) ?? aggregate)?.parameters?.[input.name] ?? { state: 'pending', message: 'Recalculating…' }), input.unit);
      for (const output of script.outputs) display(element.querySelector(`[data-script-output="${output.name}"]`), runs.map(run => run?.state === 'value'
        ? { state: run.values[output.name] === null ? 'pending' : 'value', value: run.values[output.name] } : { state: run?.state ?? 'pending', message: run?.message }), output.unit);
      element.querySelector('[data-script-status]').textContent = runs.map((run, index) => `${selected[index].name ? `${selected[index].name}: ` : ''}${run ? `${run.message}${run.executedAt ? ` (${run.executedAt})` : ''}${run.log ? `\n${run.log}` : ''}` : 'Run Python for the current inputs.'}`).join('\n');
    }
  }
  function close() { active = false; lifecycle++; runController?.abort(); runController = null; running = ''; }
  function open() {
    close(); active = true; columns = ''; currentResult = null; currentPreview = ''; expanded.clear(); ids.clear();
    for (const script of workspace().scripts) ids.set(script.key, script.id);
    methods = [...structuredClone(verificationMethods(getRow())), blank()];
    library.open = false; message.textContent = ''; renderMethods(true); renderScripts();
  }
  return { open, close, update, refresh: () => { renderMethods(); }, focus: () => table.querySelector('[data-method-field="condition"]')?.focus() };
}
