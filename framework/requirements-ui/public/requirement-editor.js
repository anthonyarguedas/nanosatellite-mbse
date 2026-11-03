import {
  declareRequirementVariables, mergeRequirementDraft, nextId, parameterExpression, parameterUnit,
  parseTSV, requirementParameterNames, tabsFor,
} from '/model.mjs';
import { parameterValueHTML } from '/requirement-preview.js';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);

export function createRequirementEditor({ panel, getWorkspace, getCatalog, validate, onCommit }) {
  const form = panel.querySelector('form');
  const text = panel.querySelector('#requirement-text');
  const kind = panel.querySelector('#requirement-kind');
  const condition = panel.querySelector('#requirement-condition');
  const rationale = panel.querySelector('#requirement-rationale');
  const frame = panel.querySelector('.requirement-parameter-frame');
  const table = frame.querySelector('table');
  const errorLabel = panel.querySelector('#requirement-error');
  const saveButton = panel.querySelector('#requirement-save');
  let draft = null, worker = null, timer, workerTimer, generation = 0;

  const row = () => draft.workspace.statements.find(row => row.key === draft.key);
  const isDirty = () => Boolean(draft && JSON.stringify(draft.workspace) !== draft.initial);
  const setError = message => { errorLabel.textContent = message; };
  const names = () => requirementParameterNames(draft.workspace, row(), getCatalog());
  function renderParameters(force = false) {
    const columns = names().map(name => draft.workspace.variables.find(variable => variable.name === name)).filter(Boolean);
    const signature = JSON.stringify(columns.map(({ name, type }) => ({ name, type })));
    if (!force && signature === draft.columns) return;
    draft.columns = signature;
    const focused = document.activeElement;
    const field = focused?.dataset.parameterUnit === undefined ? 'data-parameter' : 'data-parameter-unit';
    const parameter = focused?.getAttribute(field);
    const selection = parameter ? [focused.selectionStart, focused.selectionEnd] : null;
    table.hidden = !columns.length;
    panel.querySelector('#requirement-parameters-empty').hidden = Boolean(columns.length);
    table.innerHTML = '<colgroup><col class="parameter-name-col"><col><col class="parameter-unit-col"><col class="parameter-value-col"></colgroup>'
      + '<thead><tr><th scope="col">Name</th><th scope="col">Expression</th><th scope="col">Units</th><th scope="col">Evaluated value</th></tr></thead><tbody>'
      + columns.map(variable => `<tr data-parameter-row="${variable.name}"><th scope="row"><code>${escape(variable.name)}</code></th><td class="parameter"><input data-parameter="${variable.name}" aria-label="Expression for ${variable.name}" value="${escape(row().parameters[variable.name])}" maxlength="5000" autocomplete="off" spellcheck="false"></td><td class="parameter"><input data-parameter-unit="${variable.name}" aria-label="Units for ${variable.name}" value="${escape(variable.unit)}" maxlength="100" placeholder="e.g. m^2" autocomplete="off" spellcheck="false"></td><td class="parameter-value"><span class="parameter-result" aria-label="Evaluated ${variable.name}"></span></td></tr>`).join('') + '</tbody>';
    const target = parameter ? table.querySelector(`[${field}="${parameter}"]`) : null;
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
      if (check.state === 'value') output.innerHTML = parameterValueHTML(check.value, draft.workspace.variables.find(variable => variable.name === name)?.unit);
      else output.textContent = check.state === 'error' ? 'Error' : check.state === 'pending' ? 'Pending' : 'Unset';
      output.title = check.message;
      input.setAttribute('aria-invalid', String(check.state === 'error'));
      input.setAttribute('aria-description', check.message);
      input.title = check.message;
    }
    const check = condition.value.trim() ? result ?? { state: 'pending', message: 'Recalculating…' }
      : { state: 'unset', message: 'No verification condition.' };
    const label = panel.querySelector('#requirement-check');
    label.dataset.state = check.state;
    label.hidden = check.state === 'unset';
    label.textContent = check.state === 'error' ? check.message : { pass: 'TRUE', fail: 'FALSE', pending: 'PENDING', unset: '' }[check.state];
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
    statement.rationale = rationale.value;
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
    panel.hidden = true;
    document.body.classList.remove('requirement-editor-open');
    const selector = anchor?.classList.contains('verification-edit') ? 'data-verification-edit' : 'data-requirement-edit';
    const target = anchor?.isConnected ? anchor : document.querySelector(`[${selector}="${key}"]`);
    target?.focus({ preventScroll: true });
  }
  function snapshot() {
    if (!draft) return validate(getWorkspace());
    if (!synchronize()) throw new Error('Correct the requirement editor errors before saving a session.');
    return validate(mergeRequirementDraft(getWorkspace(), draft.original, draft.workspace, draft.key));
  }
  function save() {
    if (!draft) return false;
    try {
      onCommit(snapshot());
      close();
      return true;
    } catch (error) { setError(error.message); return false; }
  }
  function open(key, anchor) {
    if (draft?.key === key) { draft.anchor = anchor; (anchor?.classList.contains('verification-edit') ? condition : text).focus(); return; }
    if (isDirty() && !window.confirm('Discard the current requirement edits and open another requirement?')) return;
    close();
    const original = structuredClone(getWorkspace()), workspace = structuredClone(original);
    const statement = workspace.statements.find(row => row.key === key);
    if (!statement) return;
    const prefix = tabsFor(workspace, getCatalog()).find(tab => tab.key === statement.context)?.prefix ?? 'REQ';
    statement.id ||= nextId(workspace, statement.kind, prefix);
    draft = { workspace, original, key, anchor, originalNames: new Set(workspace.variables.map(variable => variable.name)), columns: null, results: new Map() };
    panel.querySelector('#requirement-editor-title').textContent = `Edit ${statement.id}`;
    panel.querySelector('#requirement-kind-label').hidden = statement.context !== 'external';
    text.value = statement.text; kind.value = statement.kind; condition.value = statement.condition;
    rationale.value = statement.rationale ?? statement.origin ?? '';
    synchronize();
    draft.initial = JSON.stringify(draft.workspace);
    panel.hidden = false; panel.querySelector('.requirement-editor-content').scrollTop = 0;
    document.body.classList.add('requirement-editor-open');
    anchor?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    (anchor?.classList.contains('verification-edit') ? condition : text).focus({ preventScroll: true });
  }
  text.addEventListener('input', synchronize);
  kind.addEventListener('change', synchronize);
  condition.addEventListener('input', synchronize);
  rationale.addEventListener('input', () => { if (draft) row().rationale = rationale.value; });
  function setUnit(name, value) {
    const variable = draft.workspace.variables.find(variable => variable.name === name);
    const unit = parameterUnit(value, variable);
    if (unit) variable.unit = unit;
    else delete variable.unit;
  }
  frame.addEventListener('input', event => {
    const name = event.target.dataset.parameter ?? event.target.dataset.parameterUnit;
    if (!draft || !name) return;
    try {
      if (event.target.dataset.parameterUnit !== undefined) {
        setUnit(name, event.target.value); updateResults();
      } else {
        row().parameters[name] = parameterExpression(event.target.value, { name }, row().id);
        synchronize();
      }
    } catch (error) { setError(error.message); }
  });
  frame.addEventListener('paste', event => {
    const units = event.target.dataset.parameterUnit !== undefined;
    const name = event.target.dataset.parameter ?? event.target.dataset.parameterUnit, source = event.clipboardData.getData('text/plain');
    if (!draft || !name || !/[\t\r\n]/.test(source)) return;
    event.preventDefault();
    try {
      const rows = parseTSV(source), columns = names(), start = columns.indexOf(name);
      if (rows.some(row => row.length !== 1) || start + rows.length > columns.length) throw new Error(`Paste one column of ${units ? 'units' : 'expressions'} within the displayed parameter rows.`);
      if (units) {
        const values = rows.map(([value], index) => parameterUnit(value, { name: columns[start + index] }));
        values.forEach((value, index) => setUnit(columns[start + index], value));
      } else {
        const parameters = { ...row().parameters };
        rows.forEach(([value], index) => {
          const name = columns[start + index]; parameters[name] = parameterExpression(value, { name }, row().id);
        });
        row().parameters = parameters;
      }
      renderParameters(true); synchronize();
    } catch (error) { setError(error.message); }
  });
  form.addEventListener('submit', event => { event.preventDefault(); save(); });
  panel.querySelectorAll('[data-requirement-cancel]').forEach(button => button.addEventListener('click', close));
  panel.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') { event.preventDefault(); event.stopPropagation(); save(); }
  });
  return { open, close, save, snapshot, isOpen: () => Boolean(draft), isDirty };
}
