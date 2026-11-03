import {
  declareRequirementVariables, interpolateRequirement, nextId, parameterExpression,
  parseTSV, requirementParameterNames, tabsFor,
} from '/model.mjs';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);

export function createRequirementEditor({ dialog, getWorkspace, getCatalog, validate, onCommit }) {
  const form = dialog.querySelector('form');
  const text = dialog.querySelector('#requirement-text');
  const kind = dialog.querySelector('#requirement-kind');
  const condition = dialog.querySelector('#requirement-condition');
  const frame = dialog.querySelector('.requirement-parameter-frame');
  const table = frame.querySelector('table');
  const errorLabel = dialog.querySelector('#requirement-error');
  const saveButton = dialog.querySelector('#requirement-save');
  let draft = null, worker = null, timer, workerTimer, generation = 0;

  const row = () => draft.workspace.statements.find(row => row.key === draft.key);
  const setError = message => { errorLabel.textContent = message; };
  const names = () => requirementParameterNames(draft.workspace, row(), getCatalog());
  function renderParameters(force = false) {
    const columns = names().map(name => draft.workspace.variables.find(variable => variable.name === name)).filter(Boolean);
    const signature = JSON.stringify(columns);
    if (!force && signature === draft.columns) return;
    draft.columns = signature;
    const focused = document.activeElement;
    const parameter = focused?.dataset.parameter;
    const selection = parameter ? [focused.selectionStart, focused.selectionEnd] : null;
    table.hidden = !columns.length;
    dialog.querySelector('#requirement-parameters-empty').hidden = Boolean(columns.length);
    table.innerHTML = '<colgroup><col class="parameter-name-col"><col><col class="parameter-value-col"></colgroup>'
      + '<thead><tr><th scope="col">Name</th><th scope="col">Expression</th><th scope="col">Evaluated value</th></tr></thead><tbody>'
      + columns.map(variable => `<tr data-parameter-row="${variable.name}"><th scope="row"><code>${escape(variable.name)}</code></th><td class="parameter"><input data-parameter="${variable.name}" aria-label="Expression for ${variable.name}" value="${escape(row().parameters[variable.name])}" maxlength="5000" autocomplete="off" spellcheck="false"></td><td class="parameter-value"><span class="parameter-result" aria-label="Evaluated ${variable.name}"></span></td></tr>`).join('') + '</tbody>';
    const target = parameter ? table.querySelector(`[data-parameter="${parameter}"]`) : null;
    if (target) {
      target.focus({ preventScroll: true });
      if (selection) target.setSelectionRange(...selection);
    } else if (parameter) text.focus({ preventScroll: true });
  }
  function updateResults() {
    if (!draft) return;
    const result = draft.results.get(draft.key);
    for (const input of table.querySelectorAll('[data-parameter]')) {
      const name = input.dataset.parameter, parameterRow = input.closest('tr'), output = parameterRow.querySelector('.parameter-result');
      const populated = Boolean(row().parameters[name]?.trim());
      const check = result?.parameters?.[name] ?? { state: populated ? 'pending' : 'unset', message: populated ? 'Recalculating…' : 'No SysML parameter expression.' };
      parameterRow.dataset.state = check.state;
      output.textContent = check.state === 'value' ? String(check.value) : check.state === 'error' ? 'Error' : check.state === 'pending' ? 'Pending' : 'Unset';
      output.title = check.message;
      input.setAttribute('aria-invalid', String(check.state === 'error'));
      input.setAttribute('aria-description', check.message);
      input.title = check.message;
    }
    dialog.querySelector('#requirement-preview').textContent = interpolateRequirement(row().text, result?.values);
    const check = condition.value.trim() ? result ?? { state: 'pending', message: 'Recalculating…' }
      : { state: 'unset', message: 'No verification condition.' };
    const label = dialog.querySelector('#requirement-check');
    label.textContent = `${{ pass: 'True', fail: 'False', pending: 'Pending', error: 'Error', unset: 'Not verified' }[check.state]}: ${check.message}`;
    label.classList.toggle('error-text', check.state === 'error');
  }
  function evaluate() {
    const token = ++generation;
    clearTimeout(timer); clearTimeout(workerTimer);
    draft.results = new Map(); updateResults();
    timer = setTimeout(() => {
      if (!draft || token !== generation) return;
      const statements = draft.workspace.statements.filter(row => row.id);
      const fail = message => {
        if (!draft || token !== generation) return;
        draft.results.set(draft.key, { state: 'error', message,
          parameters: Object.fromEntries(draft.workspace.variables.map(variable => [variable.name, {
            state: row().parameters[variable.name]?.trim() ? 'error' : 'unset', message,
          }])) });
        updateResults(); worker?.terminate(); worker = null;
      };
      try {
        worker ??= new Worker('/verification-worker.js', { type: 'module' });
        worker.onmessage = ({ data }) => {
          if (!draft || data.token !== generation) return;
          clearTimeout(workerTimer);
          draft.results = new Map(data.results.map(result => [result.key, result])); updateResults();
        };
        worker.onerror = () => fail('Could not evaluate the expression.');
        workerTimer = setTimeout(() => fail('Expression evaluation timed out.'), 1500);
        worker.postMessage({ token, workspace: { variables: draft.workspace.variables, statements } });
      } catch { fail('Expression evaluation is unavailable in this browser.'); }
    }, 100);
  }
  function synchronize() {
    const statement = row();
    statement.text = text.value; statement.kind = kind.value; statement.condition = condition.value;
    try {
      // Drop only empty, unused names created during this edit. Existing data,
      // populated cells and equation inputs remain available after marker edits.
      const needed = new Set(names());
      const removed = draft.workspace.variables.filter(variable => !draft.originalNames.has(variable.name) && !needed.has(variable.name));
      draft.workspace.variables = draft.workspace.variables.filter(variable => !removed.includes(variable));
      for (const variable of removed) for (const row of draft.workspace.statements) delete row.parameters[variable.name];
      const markers = declareRequirementVariables(draft.workspace, statement);
      setError(markers.errors.join(' ')); saveButton.disabled = Boolean(markers.errors.length);
      renderParameters(); evaluate();
      return !markers.errors.length;
    } catch (error) {
      setError(error.message); saveButton.disabled = true;
      return false;
    }
  }
  function close() {
    if (!draft) return;
    const { anchor, key } = draft;
    draft = null; generation++;
    clearTimeout(timer); clearTimeout(workerTimer); worker?.terminate(); worker = null;
    dialog.close();
    const selector = anchor?.classList.contains('verification-edit') ? 'data-verification-edit' : 'data-requirement-edit';
    const target = anchor?.isConnected ? anchor : document.querySelector(`[${selector}="${key}"]`);
    target?.focus({ preventScroll: true });
  }
  function save() {
    if (!draft || !synchronize()) return;
    try {
      const candidate = validate(draft.workspace);
      onCommit(candidate);
      close();
    } catch (error) { setError(error.message); }
  }
  function open(key, anchor) {
    close();
    const workspace = structuredClone(getWorkspace());
    const statement = workspace.statements.find(row => row.key === key);
    if (!statement) return;
    const prefix = tabsFor(workspace, getCatalog()).find(tab => tab.key === statement.context)?.prefix ?? 'REQ';
    statement.id ||= nextId(workspace, statement.kind, prefix);
    draft = { workspace, key, anchor, originalNames: new Set(workspace.variables.map(variable => variable.name)), columns: null, results: new Map() };
    dialog.querySelector('#requirement-editor-title').textContent = `Edit ${statement.id}`;
    dialog.querySelector('#requirement-kind-label').hidden = statement.context !== 'external';
    text.value = statement.text; kind.value = statement.kind; condition.value = statement.condition;
    dialog.querySelector('#requirement-origin').textContent = statement.origin ?? '';
    synchronize();
    draft.initial = JSON.stringify(draft.workspace);
    dialog.showModal(); (anchor?.classList.contains('verification-edit') ? condition : text).focus();
  }
  text.addEventListener('input', synchronize);
  kind.addEventListener('change', synchronize);
  condition.addEventListener('input', synchronize);
  frame.addEventListener('input', event => {
    if (!draft || !event.target.dataset.parameter) return;
    try {
      const name = event.target.dataset.parameter;
      row().parameters[name] = parameterExpression(event.target.value, { name }, row().id);
      synchronize();
    } catch (error) { setError(error.message); }
  });
  frame.addEventListener('paste', event => {
    const name = event.target.dataset.parameter, source = event.clipboardData.getData('text/plain');
    if (!name || !/[\t\r\n]/.test(source)) return;
    event.preventDefault();
    try {
      const rows = parseTSV(source), columns = names(), start = columns.indexOf(name);
      if (rows.some(row => row.length !== 1) || start + rows.length > columns.length) throw new Error('Paste one column of expressions within the displayed parameter rows.');
      const parameters = { ...row().parameters };
      rows.forEach(([value], index) => {
        const name = columns[start + index]; parameters[name] = parameterExpression(value, { name }, row().id);
      });
      row().parameters = parameters;
      renderParameters(true); synchronize();
    } catch (error) { setError(error.message); }
  });
  form.addEventListener('submit', event => { event.preventDefault(); save(); });
  dialog.querySelectorAll('[data-requirement-cancel]').forEach(button => button.addEventListener('click', close));
  dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
  dialog.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') { event.preventDefault(); event.stopPropagation(); save(); }
  });
  return { open, close, save, isOpen: () => Boolean(draft), isDirty: () => Boolean(draft && JSON.stringify(draft.workspace) !== draft.initial) };
}
