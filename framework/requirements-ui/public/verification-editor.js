import { nextId, parameterExpression, rewriteRowReferences } from '/model.mjs';
import { expressionReferences } from '/expression-metadata.mjs';
import { runKey, scriptContext, scriptInstance, setVerificationMethods, verificationMethods } from '/verification-methods.mjs';
import { parameterValueHTML } from '/requirement-preview.js';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const blank = () => ({ key: crypto.randomUUID(), condition: '' });
const hasMethod = method => Boolean(method.condition.trim() || method.script || method.component);
const label = state => ({ pass: 'TRUE', fail: 'FALSE', pending: 'PENDING', error: 'ERROR', unset: '' })[state] ?? '';
const trash = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 5h12M8 3h4M6 5l1 12h6l1-12M9 8v6M11 8v6"/></svg>';

export function createVerificationEditor({ container, getWorkspace, getRow, snapshot, onChange, onError,
  getScriptResults, onScriptResults, getScriptInputs, getProducts = () => [] }) {
  const table = container.querySelector('[data-method-table]');
  const library = container.querySelector('[data-script-library]');
  const scriptList = container.querySelector('[data-script-list]');
  const parameterList = container.querySelector('[data-script-parameter-list]');
  const message = container.querySelector('[data-script-message]');
  let methods = [], definitions = [], columns = '', active = false, runController = null, running = '', lifecycle = 0;
  let currentResult = null, catalogLoaded = false;
  const ids = new Map();
  const workspace = () => getWorkspace();
  const store = () => setVerificationMethods(getRow(), methods);
  const showMessage = text => { message.textContent = text; message.hidden = !text; };
  const eventScript = target => {
    const element = target.closest('[data-script-key], [data-script-parameters]');
    return workspace().scripts.find(script => script.key === (element?.dataset.scriptKey ?? element?.dataset.scriptParameters));
  };
  function renderMethods(force = false) {
    if (!active) return;
    const populated = methods.filter(hasMethod);
    const empty = methods.find(method => !hasMethod(method)) ?? blank();
    methods = [...populated, ...(populated.length < 32 ? [empty] : [])];
    const scripts = workspace().scripts;
    const components = workspace().components.filter(component => component.id && component.product);
    const signature = JSON.stringify([methods.map(({ key, script, component }) => ({ key, script, component })), scripts.map(({ key, id, name }) => ({ key, id, name })), components.map(({ key, id, product }) => ({ key, id, product }))]);
    if (!force && columns === signature) return;
    columns = signature;
    const focused = document.activeElement, key = focused?.closest('[data-method-key]')?.dataset.methodKey;
    const field = focused?.dataset.methodField;
    const selection = typeof focused?.selectionStart === 'number' ? [focused.selectionStart, focused.selectionEnd] : null;
    table.innerHTML = '<colgroup><col class="row-actions-col"><col class="verification-source-col"><col><col class="verification-result-col"></colgroup><thead><tr><th class="row-actions-heading" aria-label="Row actions"></th><th scope="col">Values from</th><th scope="col">Python condition</th><th scope="col">Result</th></tr></thead><tbody>'
      + methods.map((method, index) => {
        const component = components.find(component => component.key === method.component);
        const options = scripts.map(script => `<option value="${script.key}" ${method.script === script.key ? 'selected' : ''}>${escape(script.id)} · ${escape(script.name)}</option>`).join('')
          + components.map(part => `<option value="cots:${part.key}" ${method.component === part.key ? 'selected' : ''}>${escape(part.id)} · ${escape(getProducts().find(product => product.id === part.product)?.name ?? part.product)}</option>`).join('');
        return `<tr data-method-key="${method.key}"><td class="row-actions"><button type="button" class="row-delete" data-remove-method="${method.key}" aria-label="Delete verification method ${index + 1}" title="Delete row" ${hasMethod(method) ? '' : 'disabled'}>${trash}</button></td><td><select data-method-field="script" aria-label="Values for verification method ${index + 1}"><option value="">Requirement values</option>${options}</select>${method.script ? `<button type="button" class="verification-run cell-button" data-run-script="${method.script}" aria-label="Run ${escape(scripts.find(script => script.key === method.script)?.id)}">Run Python</button>` : ''}${component ? `<button type="button" class="reference-link" data-inspect-cots="${component.key}">Inspect ${escape(component.id)}</button>` : ''}</td><td><input ${index === 0 ? 'id="requirement-condition"' : ''} data-method-field="condition" aria-label="${index === 0 ? 'Verification condition' : `Verification condition ${index + 1}`}" maxlength="5000" spellcheck="false" autocomplete="off" value="${escape(method.condition)}" placeholder="${component ? `${escape(component.id)}.fact >= limit` : method.script ? `${escape(scripts.find(script => script.key === method.script)?.id)}.output <= limit` : 'energy_J >= REQ001.energy_J'}"><div data-cots-links class="cots-expression-links"></div><span class="verification-message" hidden></span></td><td><span class="verification-method-result" role="status"></span></td></tr>`;
      }).join('') + '</tbody>';
    const target = key && field ? table.querySelector(`[data-method-key="${key}"] [data-method-field="${field}"]`) : null;
    if (target) { target.focus({ preventScroll: true }); if (selection) target.setSelectionRange(...selection); }
    container.querySelector('[data-add-method]').disabled = populated.length >= 32;
  }
  function scriptParameters(script) {
    const parameters = [...script.inputs.map(input => ({ ...input, direction: 'Input' })),
      ...script.outputs.map(output => ({ ...output, direction: 'Output' }))];
    return `<section class="sheet editor-sheet script-parameters" data-script-parameters="${script.key}" aria-label="${escape(script.id)} parameters"><div class="table-top"><h4>${escape(script.id)} parameters</h4></div><div class="table-frame"><table aria-label="${escape(script.id)} parameters"><colgroup><col class="parameter-name-col"><col class="script-direction-col"><col class="script-type-col"><col><col class="parameter-unit-col"><col class="parameter-value-col"></colgroup><thead><tr><th scope="col">Parameter</th><th scope="col">Direction</th><th scope="col">Type</th><th scope="col">Expression</th><th scope="col">Units</th><th scope="col">Evaluated value</th></tr></thead><tbody>${parameters.map(parameter => {
      const input = parameter.direction === 'Input';
      return `<tr><th scope="row"><code>${input ? '' : `${escape(script.id)}.`}${escape(parameter.name)}</code></th><td class="cell-text">${parameter.direction}</td><td class="cell-text">${escape(parameter.type)}</td><td class="parameter">${input ? `<textarea data-script-input="${parameter.name}" aria-label="${escape(script.id)} ${parameter.name} expression" rows="1" maxlength="5000" spellcheck="false">${escape(script.parameters[parameter.name])}</textarea><div data-cots-script-links="${parameter.name}" class="cots-expression-links"></div>` : ''}</td><td class="cell-text"><code>${escape(parameter.unit)}</code></td><td><span ${input ? 'data-script-input-result' : 'data-script-output'}="${parameter.name}" class="parameter-result"></span></td></tr>`;
    }).join('')}</tbody></table></div></section>`;
  }
  function renderScripts() {
    if (!active) return;
    const focused = document.activeElement, script = focused?.closest('[data-script-key], [data-script-parameters]');
    const key = script?.dataset.scriptKey ?? script?.dataset.scriptParameters;
    const field = focused?.dataset.scriptField !== undefined ? 'data-script-field' : 'data-script-input';
    const name = focused?.getAttribute(field);
    const selection = typeof focused?.selectionStart === 'number' ? [focused.selectionStart, focused.selectionEnd] : null;
    scriptList.innerHTML = '<colgroup><col class="row-actions-col"><col class="script-id-col"><col><col><col class="script-execution-col"></colgroup><thead><tr><th class="row-actions-heading" aria-label="Row actions"></th><th scope="col">ID</th><th scope="col">Name</th><th scope="col">Definition</th><th scope="col">Execution</th></tr></thead><tbody>'
      + workspace().scripts.map(script => {
        const current = definitions.find(definition => definition.id === script.definition);
        return `<tr data-script-key="${script.key}"><td class="row-actions"><button type="button" class="row-delete" data-delete-script aria-label="Delete ${escape(script.id)}" title="Delete row">${trash}</button></td><td class="id-cell"><input data-script-field="id" aria-label="Script ID ${escape(script.id)}" value="${escape(script.id)}" maxlength="6" autocomplete="off" spellcheck="false"></td><td><input data-script-field="name" aria-label="Script name ${escape(script.id)}" value="${escape(script.name)}" maxlength="80" autocomplete="off"></td><td class="cell-text"><span title="${escape(script.definition)}.py · ${escape(script.revision)}">${escape(current?.name ?? script.definition)}</span>${current && current.revision !== script.revision ? '<button type="button" class="cell-button" data-update-script>Update definition</button>' : catalogLoaded && !current ? '<span class="error-text">Unavailable</span>' : ''}</td><td><button type="button" class="cell-button" data-run-script="${script.key}" aria-label="Run ${escape(script.id)}" title="Run trusted Python locally with your user permissions">Run Python</button><span data-script-status class="script-status" role="status"></span></td></tr>`;
      }).join('')
      + (workspace().scripts.length < 64 ? `<tr data-script-placeholder><td class="row-actions"><button type="button" class="row-delete" aria-label="Delete empty script row" disabled>${trash}</button></td><td></td><td></td><td><select data-script-add-definition aria-label="Python script definition" ${!definitions.length ? 'disabled' : ''}><option value="">${catalogLoaded ? definitions.length ? 'Choose a script…' : 'No scripts available' : 'Loading…'}</option>${definitions.map(definition => `<option value="${definition.id}">${escape(definition.name)}</option>`).join('')}</select></td><td></td></tr>` : '') + '</tbody>';
    parameterList.innerHTML = workspace().scripts.map(scriptParameters).join('');
    library.querySelector('[data-script-add]').disabled = !definitions.length || workspace().scripts.length >= 64;
    const target = key && name ? library.querySelector(`[data-script-key="${key}"] [${field}="${name}"], [data-script-parameters="${key}"] [${field}="${name}"]`) : null;
    if (target) { target.focus({ preventScroll: true }); if (selection) target.setSelectionRange(...selection); }
    update(currentResult);
  }
  async function loadDefinitions() {
    const token = lifecycle;
    try {
      const response = await fetch('/api/scripts'), data = await response.json();
      if (!response.ok) throw new Error(data.error);
      if (!active || token !== lifecycle) return;
      definitions = data.scripts; catalogLoaded = true;
      renderScripts();
    } catch (error) { if (active && token === lifecycle) showMessage(error.message); }
  }
  function changed() { store(); renderMethods(); onChange(); }
  table.addEventListener('input', event => {
    if (!active || event.target.dataset.methodField !== 'condition') return;
    methods.find(method => method.key === event.target.closest('[data-method-key]').dataset.methodKey).condition = event.target.value;
    changed();
  });
  table.addEventListener('change', event => {
    if (!active || event.target.dataset.methodField !== 'script') return;
    const method = methods.find(method => method.key === event.target.closest('[data-method-key]').dataset.methodKey);
    delete method.script; delete method.component;
    if (event.target.value.startsWith('cots:')) method.component = event.target.value.slice(5);
    else if (event.target.value) method.script = event.target.value;
    changed();
  });
  container.addEventListener('click', event => {
    const remove = event.target.closest('[data-remove-method]');
    if (remove && active) { methods = methods.filter(method => method.key !== remove.dataset.removeMethod); store(); renderMethods(true); onChange(); }
    if (active && event.target.closest('[data-add-method]')) {
      renderMethods(); table.querySelector('tbody tr:last-child [data-method-field="condition"]')?.focus();
    }
    if (active && event.target.closest('[data-script-add]')) library.querySelector('[data-script-add-definition]')?.focus();
  });
  library.addEventListener('input', event => {
    if (!active) return;
    const script = eventScript(event.target);
    if (!script) return;
    try {
      if (event.target.dataset.scriptInput) {
        script.parameters[event.target.dataset.scriptInput] = event.target.value.trim() ? event.target.value : null;
        parameterExpression(script.parameters[event.target.dataset.scriptInput], { name: event.target.dataset.scriptInput }, script.id);
      } else if (event.target.dataset.scriptField) {
        const field = event.target.dataset.scriptField;
        script[field] = field === 'id' ? event.target.value.toUpperCase() : event.target.value;
        if (field === 'id') event.target.value = script.id;
        renderMethods();
      } else return;
      onChange();
    } catch (error) { onChange(); onError(error.message); }
  });
  library.addEventListener('beforeinput', event => {
    if (event.target.dataset.scriptInput && ['insertLineBreak', 'insertParagraph'].includes(event.inputType)) event.preventDefault();
  });
  library.addEventListener('change', event => {
    if (!active) return;
    if (event.target.matches('[data-script-add-definition]')) {
      const definition = definitions.find(definition => definition.id === event.target.value);
      if (!definition || workspace().scripts.length >= 64) return;
      const script = scriptInstance(definition, { key: crypto.randomUUID(), id: nextId(workspace(), 'Script') });
      workspace().scripts.push(script); ids.set(script.key, script.id);
      showMessage(''); renderScripts(); renderMethods(true); onChange();
      parameterList.querySelector(`[data-script-parameters="${script.key}"] [data-script-input]`)?.focus();
      return;
    }
    if (event.target.dataset.scriptField !== 'id') return;
    const script = eventScript(event.target), previous = ids.get(script.key);
    if (/^[A-Z]{3}\d{3}$/.test(script.id) && ![...workspace().scripts, ...workspace().statements].some(row => row.key !== script.key && row.id === script.id)) {
      rewriteRowReferences(workspace(), new Map([[previous, script.id]])); ids.set(script.key, script.id);
      methods = [...structuredClone(verificationMethods(getRow())), blank()];
    }
    renderMethods(true); renderScripts(); onChange();
  });
  library.addEventListener('click', event => {
    if (!active) return;
    const script = eventScript(event.target);
    if (!script) return;
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
      running = key; runController = new AbortController(); showMessage(''); update(null);
      const response = await fetch('/api/scripts/run', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace: state, script: key }), signal: runController.signal });
      const evidence = await response.json();
      if (!response.ok) throw new Error(evidence.error);
      if (!active || token !== lifecycle) return;
      if (evidence.signature !== scriptContext(snapshot())) throw new Error('Calculation inputs changed during execution. Run Python again.');
      const previous = getScriptResults();
      onScriptResults({ signature: evidence.signature, runs: { ...(previous?.signature === evidence.signature ? previous.runs : {}), ...evidence.runs } });
      onChange();
      if (Object.values(evidence.runs).some(run => run.state === 'error')) loadDefinitions();
    } catch (error) {
      if (active && token === lifecycle && error.name !== 'AbortError') { showMessage(error.message); onError(error.message); }
    } finally { if (token === lifecycle) { running = ''; runController = null; update(null); } }
  });
  function cotsLinks(source) {
    return [...new Map(expressionReferences(source).map(reference => [`${reference.id}.${reference.name}`, reference])).values()].flatMap(reference => {
      const component = workspace().components.find(component => component.id === reference.id);
      return component ? [`<button type="button" class="reference-link" data-inspect-cots="${component.key}" data-cots-name="${escape(reference.name)}">${escape(component.id)}.${escape(reference.name)}</button>`] : [];
    }).join('');
  }
  function update(result) {
    if (!active) return;
    currentResult = result;
    for (const tr of table.querySelectorAll('[data-method-key]')) {
      const method = methods.find(method => method.key === tr.dataset.methodKey);
      const index = methods.filter(hasMethod).findIndex(item => item.key === method.key);
      tr.querySelector('[data-cots-links]').innerHTML = cotsLinks(method.condition);
      const check = result?.methods?.[index] ?? (hasMethod(method) ? { state: 'pending', message: 'Recalculating…' } : { state: 'unset', message: '' });
      const output = tr.querySelector('.verification-method-result'), error = tr.querySelector('.verification-message');
      tr.dataset.state = check.state; output.textContent = label(check.state); output.title = check.message;
      error.hidden = check.state !== 'error'; error.textContent = check.state === 'error' ? check.message : '';
      tr.querySelector('[data-method-field="condition"]').setAttribute('aria-invalid', String(check.state === 'error'));
    }
    for (const button of container.querySelectorAll('[data-run-script]')) { button.disabled = Boolean(running); button.textContent = button.dataset.runScript === running ? 'Running…' : 'Run Python'; }
    const modes = workspace().power.modes.length ? workspace().power.modes : [{ key: null, name: '' }];
    const evidence = getScriptResults(), fresh = evidence?.signature === scriptContext(workspace());
    const inputResults = getScriptInputs();
    const display = (output, cells, unit) => {
      const same = cells.every(cell => cell.state === 'value' && cell.value === cells[0].value);
      output.innerHTML = same ? typeof cells[0].value === 'boolean' ? String(cells[0].value) : parameterValueHTML(cells[0].value, unit) : '';
      if (!same) output.textContent = cells.every(cell => cell.state === 'value') ? 'By mode' : cells.some(cell => cell.state === 'error') ? 'Error' : 'Pending';
      output.title = cells.map((cell, index) => `${modes[index].name ? `${modes[index].name}: ` : ''}${cell.message ?? cell.value ?? 'Pending'}`).join('\n');
      const input = output.closest('tr').querySelector('[data-script-input]');
      if (input) { input.setAttribute('aria-invalid', String(cells.some(cell => cell.state === 'error'))); input.title = output.title; }
    };
    for (const script of workspace().scripts) {
      const element = parameterList.querySelector(`[data-script-parameters="${script.key}"]`);
      const runs = modes.map(mode => fresh ? evidence.runs[runKey(script.key, mode.key)] : null);
      const aggregate = inputResults.get(script.key);
      for (const input of script.inputs) {
        display(element.querySelector(`[data-script-input-result="${input.name}"]`), modes.map(mode =>
          (aggregate?.modes?.find(result => result.mode === mode.key) ?? aggregate)?.parameters?.[input.name] ?? { state: 'pending', message: 'Recalculating…' }), input.unit);
        element.querySelector(`[data-cots-script-links="${input.name}"]`).innerHTML = cotsLinks(script.parameters[input.name]);
      }
      for (const output of script.outputs) display(element.querySelector(`[data-script-output="${output.name}"]`), runs.map(run => run?.state === 'value'
        ? { state: run.values[output.name] === null ? 'pending' : 'value', value: run.values[output.name] } : { state: run?.state ?? 'pending', message: run?.message }), output.unit);
      const status = scriptList.querySelector(`[data-script-key="${script.key}"] [data-script-status]`);
      status.dataset.state = script.key === running ? 'running' : runs.some(run => run?.state === 'error') ? 'error' : runs.every(run => run?.state === 'value') ? 'value' : 'pending';
      status.textContent = { running: 'Running…', error: 'Error', value: 'Completed', pending: 'Pending' }[status.dataset.state];
      status.title = runs.map((run, index) => `${modes[index].name ? `${modes[index].name}: ` : ''}${run ? `${run.message}${run.executedAt ? ` (${run.executedAt})` : ''}${run.log ? `\n${run.log}` : ''}` : 'Pending'}`).join('\n');
    }
  }
  function close() { active = false; lifecycle++; runController?.abort(); runController = null; running = ''; }
  function open() {
    close(); active = true; columns = ''; currentResult = null; catalogLoaded = false; definitions = []; ids.clear();
    for (const script of workspace().scripts) ids.set(script.key, script.id);
    methods = [...structuredClone(verificationMethods(getRow())), blank()];
    showMessage(''); renderMethods(true); renderScripts(); loadDefinitions();
  }
  return { open, close, update, refresh: () => { renderMethods(); }, focus: () => table.querySelector('[data-method-field="condition"]')?.focus() };
}
