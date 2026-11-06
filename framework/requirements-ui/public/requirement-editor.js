import {
  declareRequirementVariables, mergeRequirementDraft, nextId, parameterExpression, parameterUnit,
  parseTSV, requirementParameterNames, tabsFor,
} from '/model.mjs';
import { parameterValueHTML } from '/requirement-preview.js';
import { connectPower, disconnectPower, managedPowerInput } from '/power.mjs';
import { mergedStateExpression, parameterStates, splitParameterStates, stateExpression } from '/parameter-states.mjs';
import { createVerificationEditor } from '/verification-editor.js';
import { verificationMethods } from '/verification-methods.mjs';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);

export function createRequirementEditor({ panel, getWorkspace, getCatalog, validate, onCommit,
  getScriptResults = () => null, onScriptResults = () => {} }) {
  const form = panel.querySelector('form');
  const text = panel.querySelector('#requirement-text');
  const kind = panel.querySelector('#requirement-kind');
  const rationale = panel.querySelector('#requirement-rationale');
  const frame = panel.querySelector('.requirement-parameter-frame');
  const table = frame.querySelector('table');
  const errorLabel = panel.querySelector('#requirement-error');
  const saveButton = panel.querySelector('#requirement-save');
  const powerSource = panel.querySelector('#requirement-power-source');
  const powerDomains = panel.querySelector('#requirement-power-domains');
  const powerRoots = panel.querySelector('#requirement-power-roots');
  let draft = null, worker = null, timer, workerTimer, generation = 0;

  const row = () => draft.workspace.statements.find(row => row.key === draft.key);
  const isDirty = () => Boolean(draft && JSON.stringify(draft.workspace) !== draft.initial);
  const setError = message => { errorLabel.textContent = message; };
  const names = () => requirementParameterNames(draft.workspace, row(), getCatalog());
  const verificationEditor = createVerificationEditor({ container: panel.querySelector('#requirement-verification'),
    getWorkspace: () => draft.workspace, getRow: row, snapshot, onChange: synchronize, onError: setError,
    getScriptResults, onScriptResults, getScriptInputs: () => draft?.scriptInputs ?? new Map() });
  const focusEditor = anchor => anchor?.classList.contains('verification-edit') ? verificationEditor.focus() : text.focus({ preventScroll: true });
  function fitExpressions() {
    if (!frame.clientWidth) return;
    for (const input of table.querySelectorAll('textarea[data-parameter]')) {
      input.style.height = 'auto';
      input.style.height = `${input.scrollHeight}px`;
    }
  }
  let parameterWidth = 0;
  const parameterResize = new ResizeObserver(([entry]) => {
    if (entry.contentRect.width === parameterWidth) return;
    parameterWidth = entry.contentRect.width;
    fitExpressions();
  });
  parameterResize.observe(frame);
  function stateView(name) {
    const source = row().parameters[name], modes = getWorkspace().power.modes;
    let view = draft.parameterViews.get(name);
    if (!view || view.source !== source) {
      view = { source, states: managedPowerInput(draft.workspace, row(), name) ? null : parameterStates(source, modes) };
      draft.parameterViews.set(name, view);
    }
    const metadata = draft.results.get(draft.key)?.parameters?.[name];
    if (!view.states && metadata?.expressionSource === source && document.activeElement?.dataset.parameter === undefined) {
      view.states = metadata.branches ?? null;
    }
    const signature = JSON.stringify(modes.map(({ key, name }) => ({ key, name })));
    if (view.states && view.modes && view.modes !== signature) {
      view.states.values = Object.fromEntries(modes.map(mode => [mode.key, view.states.values[mode.key] ?? null]));
      if (!modes.some(mode => mode.key === view.states.lastEdited)) view.states.lastEdited = modes[0]?.key;
      view.source = row().parameters[name] = modes.length ? stateExpression(view.states, modes) : null;
      if (!modes.length) view.states = null;
    }
    view.modes = signature;
    return view;
  }
  function parameterRows() {
    return names().flatMap(name => {
      const variable = draft.workspace.variables.find(variable => variable.name === name);
      if (!variable) return [];
      const { states } = stateView(name);
      return states ? getWorkspace().power.modes.map(mode => ({ variable, mode: mode.key, expression: states.values[mode.key] }))
        : [{ variable, mode: '', expression: row().parameters[name] }];
    });
  }
  function editExpression(name, mode, value) {
    const source = parameterExpression(value, { name }, row().id), view = stateView(name);
    if (mode && view.states) {
      view.states.values[mode] = source;
      view.states.lastEdited = mode;
      view.source = row().parameters[name] = stateExpression(view.states, getWorkspace().power.modes);
    } else {
      view.states = null;
      view.source = row().parameters[name] = source;
    }
  }
  function renderParameters(force = false) {
    const rows = parameterRows(), modes = getWorkspace().power.modes;
    const signature = JSON.stringify([rows.map(({ variable: { name, type }, mode }) => ({ name, type, mode,
      managed: managedPowerInput(draft.workspace, row(), name) })), modes]);
    if (!force && signature === draft.columns) return;
    draft.columns = signature;
    const focused = document.activeElement;
    const field = focused?.dataset.parameterState !== undefined ? 'data-parameter-state'
      : focused?.dataset.parameterUnit !== undefined ? 'data-parameter-unit' : 'data-parameter';
    const parameter = focused?.getAttribute(field), focusedMode = focused?.dataset.mode ?? '';
    const selection = parameter && typeof focused.selectionStart === 'number' ? [focused.selectionStart, focused.selectionEnd] : null;
    panel.querySelector('#requirement-parameters-empty').hidden = Boolean(rows.length);
    table.innerHTML = '<colgroup><col class="parameter-name-col"><col class="parameter-state-col"><col><col class="parameter-unit-col"><col class="parameter-value-col"></colgroup>'
      + '<thead><tr><th scope="col">Name</th><th scope="col">State</th><th scope="col">Expression</th><th scope="col">Units</th><th scope="col">Evaluated value</th></tr></thead><tbody>'
      + rows.map(({ variable, mode, expression }) => {
        const suffix = mode ? ` in ${modes.find(state => state.key === mode).name}` : '';
        const managed = managedPowerInput(draft.workspace, row(), variable.name);
        return `<tr data-parameter-row="${variable.name}" data-mode="${mode}"><th scope="row"><code>${escape(variable.name)}</code></th><td><select data-parameter-state="${variable.name}" data-mode="${mode}" aria-label="State for ${variable.name}${escape(suffix)}" ${!modes.length || managed ? 'disabled' : ''}><option value="">All states</option>${modes.map(state => `<option value="${state.key}" ${state.key === mode ? 'selected' : ''} ${mode && state.key !== mode ? 'disabled' : ''}>${escape(state.name)}</option>`).join('')}</select></td><td class="parameter parameter-expression"><textarea data-parameter="${variable.name}" data-mode="${mode}" aria-label="Expression for ${variable.name}${escape(suffix)}" rows="1" wrap="soft" maxlength="5000" autocomplete="off" spellcheck="false">${escape(expression)}</textarea></td><td class="parameter"><input data-parameter-unit="${variable.name}" data-mode="${mode}" aria-label="Units for ${variable.name}${escape(suffix)}" value="${escape(variable.unit)}" maxlength="100" placeholder="e.g. m**2" autocomplete="off" spellcheck="false"></td><td class="parameter-value"><span class="parameter-result" aria-label="Evaluated ${variable.name}${escape(suffix)}"></span></td></tr>`;
      }).join('') + '</tbody>';
    fitExpressions();
    const target = parameter ? table.querySelector(`[${field}="${parameter}"][data-mode="${focusedMode}"]`)
      ?? table.querySelector(`[${field}="${parameter}"]`) : null;
    if (target) {
      target.focus({ preventScroll: true });
      if (selection) target.setSelectionRange(...selection);
    } else if (parameter) text.focus({ preventScroll: true });
  }
  function updateResults() {
    if (!draft) return;
    const result = draft.results.get(draft.key);
    panel.querySelector('#requirement-editor-title').textContent = `Edit ${row().id}`;
    for (const input of table.querySelectorAll('[data-parameter]')) {
      const name = input.dataset.parameter, parameterRow = input.closest('tr'), output = parameterRow.querySelector('.parameter-result');
      const managed = managedPowerInput(draft.workspace, row(), name);
      input.readOnly = managed;
      const populated = Boolean(input.value.trim());
      const stateResult = input.dataset.mode ? result?.modes?.find(result => result.mode === input.dataset.mode) ?? result : result;
      const check = stateResult?.parameters?.[name] ?? { state: populated ? 'pending' : 'unset', message: populated ? 'Recalculating…' : 'No Python parameter expression.' };
      parameterRow.dataset.state = check.state;
      if (check.state === 'value') output.innerHTML = parameterValueHTML(check.value, draft.workspace.variables.find(variable => variable.name === name)?.unit);
      else output.textContent = { error: 'Error', pending: 'Pending', varying: 'By mode', unset: 'Unset' }[check.state] ?? 'Unset';
      output.title = check.message;
      input.setAttribute('aria-invalid', String(check.state === 'error'));
      const message = managed ? `Component modes. ${check.message}` : check.message;
      input.setAttribute('aria-description', message);
      input.title = [input.value, message].filter(Boolean).join('\n');
    }
    verificationEditor.update(result);
    const hasMethods = verificationMethods(row()).length > 0;
    const check = hasMethods ? result ?? { state: 'pending', message: 'Recalculating…' }
      : { state: 'unset', message: 'No verification condition.' };
    const label = panel.querySelector('#requirement-check');
    label.dataset.state = check.state;
    label.hidden = check.state === 'unset';
    const stateLabel = state => ({ pass: 'TRUE', fail: 'FALSE', pending: 'PENDING', error: 'ERROR', unset: 'UNSET' })[state];
    label.textContent = check.state === 'error' ? check.message : check.state === 'unset' ? '' : stateLabel(check.state);
    label.title = check.message;
    const modeResults = panel.querySelector('#requirement-mode-results');
    modeResults.hidden = !hasMethods || !result?.modes;
    modeResults.textContent = result?.modes?.map(result => `${getWorkspace().power.modes.find(mode => mode.key === result.mode)?.name}: ${stateLabel(result.state)}`).join(' · ') ?? '';
  }
  frame.addEventListener('change', event => {
    const name = event.target.dataset.parameterState;
    if (!draft || !name || managedPowerInput(draft.workspace, row(), name)) return;
    try {
      const view = stateView(name), selected = event.target.value;
      if (selected && !event.target.dataset.mode) {
        view.states = draft.results.get(draft.key)?.parameters?.[name]?.branches ?? splitParameterStates(row().parameters[name], getWorkspace().power.modes, selected);
        view.source = row().parameters[name] = stateExpression(view.states, getWorkspace().power.modes);
      } else if (!selected && view.states) {
        view.source = row().parameters[name] = mergedStateExpression(view.states, event.target.dataset.mode);
        view.states = null;
      } else return;
      renderParameters(true); synchronize();
      table.querySelector(`[data-parameter="${name}"][data-mode="${selected}"]`)?.focus({ preventScroll: true });
    } catch (error) { setError(error.message); }
  });
  function renderPowerSource() {
    const relevant = row().definition === 'FrameworkRequirements::LoadEnergy';
    panel.querySelector('#requirement-load-source').hidden = !relevant;
    if (!relevant) return;
    const link = draft.workspace.power.links.find(link => link.eps === row().context);
    powerSource.value = link ? 'components' : 'manual';
    powerDomains.hidden = !link;
    powerRoots.innerHTML = link ? draft.workspace.elements.filter(element => element.id && element.owner === 'mission'
      && ['SpaceSegment::CubeSat', 'SpaceSegment::CubeSat::PayloadSubsystem'].includes(element.definition))
      .map(element => `<label title="${escape(element.name)}"><input type="checkbox" data-power-root="${element.key}" ${link.roots.includes(element.key) ? 'checked' : ''}>${escape(element.id)}</label>`).join('') : '';
  }
  powerSource.addEventListener('change', () => {
    if (!draft) return;
    try {
      if (powerSource.value === 'components') connectPower(draft.workspace, row().context);
      else disconnectPower(draft.workspace, row().context);
      setError(''); renderPowerSource(); renderParameters(true); evaluate();
    } catch (error) { setError(error.message); renderPowerSource(); }
  });
  powerRoots.addEventListener('change', event => {
    if (!draft || !event.target.dataset.powerRoot) return;
    const link = draft.workspace.power.links.find(link => link.eps === row().context);
    const roots = link.roots.filter(key => key !== event.target.dataset.powerRoot);
    if (event.target.checked) roots.push(event.target.dataset.powerRoot);
    if (!roots.length) { setError('Select at least one load domain.'); renderPowerSource(); return; }
    link.roots = roots; setError(''); evaluate();
  });
  function evaluate() {
    const token = ++generation;
    clearTimeout(timer); clearTimeout(workerTimer);
    draft.results = new Map(); draft.scriptInputs = new Map(); updateResults();
    timer = setTimeout(() => {
      if (!draft || token !== generation) return;
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
          if (data.error) { fail(data.error); return; }
          draft.scriptInputs = new Map((data.scripts ?? []).map(script => [script.key, script]));
          draft.results = new Map(data.results.map(result => [result.key, result])); renderParameters(); updateResults();
        };
        worker.onerror = () => fail('Could not evaluate the expression.');
        workerTimer = setTimeout(() => fail('Python expression evaluation timed out.'), 7000);
        const state = mergeRequirementDraft(getWorkspace(), draft.original, draft.workspace, draft.key);
        worker.postMessage({ token, scriptResults: getScriptResults(), workspace: { variables: state.variables,
          statements: state.statements.filter(row => row.id), elements: state.elements, power: state.power, scripts: state.scripts, expressionLanguage: state.expressionLanguage } });
      } catch (error) { fail(error.message || 'Expression evaluation is unavailable in this browser.'); }
    }, 100);
  }
  function synchronize() {
    const statement = row();
    statement.text = text.value; statement.kind = kind.value;
    statement.rationale = rationale.value;
    try {
      // Drop only empty, unused names created during this edit. Existing data,
      // populated cells and equation inputs remain available after marker edits.
      const needed = new Set(names());
      const removed = draft.workspace.variables.filter(variable => !draft.originalNames.has(variable.name) && !needed.has(variable.name));
      draft.workspace.variables = draft.workspace.variables.filter(variable => !removed.includes(variable));
      for (const variable of removed) for (const row of draft.workspace.statements) delete row.parameters[variable.name];
      const markers = declareRequirementVariables(draft.workspace, statement);
      const errors = [...markers.errors];
      for (const [name, value] of Object.entries(statement.parameters)) {
        try { parameterExpression(value, { name }, statement.id); } catch (error) { errors.push(error.message); }
      }
      setError(errors.join(' ')); saveButton.disabled = Boolean(errors.length);
      renderParameters(); evaluate();
      return !errors.length;
    } catch (error) {
      setError(error.message); saveButton.disabled = true;
      return false;
    }
  }
  function close() {
    if (!draft) return;
    const { anchor, key } = draft;
    verificationEditor.close();
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
    if (draft?.key === key) { draft.anchor = anchor; focusEditor(anchor); return; }
    if (isDirty() && !window.confirm('Discard the current requirement edits and open another requirement?')) return;
    close();
    const original = structuredClone(getWorkspace()), workspace = structuredClone(original);
    const statement = workspace.statements.find(row => row.key === key);
    if (!statement) return;
    const prefix = tabsFor(workspace, getCatalog()).find(tab => tab.key === statement.context)?.prefix ?? 'REQ';
    statement.id ||= nextId(workspace, statement.kind, prefix);
    draft = { workspace, original, key, anchor, originalNames: new Set(workspace.variables.map(variable => variable.name)), columns: null,
      parameterViews: new Map(), results: new Map(), scriptInputs: new Map() };
    panel.querySelector('#requirement-editor-title').textContent = `Edit ${statement.id}`;
    panel.querySelector('#requirement-kind-label').hidden = statement.context !== 'external';
    text.value = statement.text; kind.value = statement.kind;
    rationale.value = statement.rationale ?? statement.origin ?? '';
    verificationEditor.open(); renderPowerSource(); synchronize();
    draft.initial = JSON.stringify(draft.workspace);
    panel.hidden = false; panel.querySelector('.requirement-editor-content').scrollTop = 0;
    document.body.classList.add('requirement-editor-open');
    anchor?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    focusEditor(anchor);
  }
  text.addEventListener('input', synchronize);
  kind.addEventListener('change', synchronize);
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
        setUnit(name, event.target.value);
        for (const input of table.querySelectorAll(`[data-parameter-unit="${name}"]`)) if (input !== event.target) input.value = event.target.value;
        updateResults();
      } else {
        fitExpressions();
        editExpression(name, event.target.dataset.mode, event.target.value);
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
      const rows = parseTSV(source), columns = parameterRows();
      const start = columns.findIndex(column => column.variable.name === name && column.mode === (event.target.dataset.mode ?? ''));
      if (rows.some(row => row.length !== 1) || start + rows.length > columns.length) throw new Error(`Paste one column of ${units ? 'units' : 'expressions'} within the displayed parameter rows.`);
      if (!units && rows.some((_, index) => managedPowerInput(draft.workspace, row(), columns[start + index].variable.name))) throw new Error('Select Manual expressions before changing these inputs.');
      if (units) {
        const values = rows.map(([value], index) => parameterUnit(value, columns[start + index].variable));
        values.forEach((value, index) => setUnit(columns[start + index].variable.name, value));
      } else {
        const parameters = { ...row().parameters }, views = structuredClone(draft.parameterViews);
        try {
          rows.forEach(([value], index) => {
            const { variable, mode } = columns[start + index]; editExpression(variable.name, mode, value);
          });
          for (const [name, value] of Object.entries(row().parameters)) parameterExpression(value, { name }, row().id);
        } catch (error) { row().parameters = parameters; draft.parameterViews = views; throw error; }
      }
      renderParameters(true); synchronize();
    } catch (error) { setError(error.message); }
  });
  // Soft wrapping keeps each stored expression on one logical line.
  frame.addEventListener('beforeinput', event => {
    if (event.target.dataset.parameter && ['insertLineBreak', 'insertParagraph'].includes(event.inputType)) event.preventDefault();
  });
  form.addEventListener('submit', event => { event.preventDefault(); save(); });
  panel.querySelectorAll('[data-requirement-cancel]').forEach(button => button.addEventListener('click', close));
  panel.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') { event.preventDefault(); event.stopPropagation(); save(); }
  });
  return { open, close, save, snapshot, refresh: () => { if (draft) { renderParameters(); verificationEditor.refresh(); evaluate(); } }, isOpen: () => Boolean(draft), isDirty };
}
