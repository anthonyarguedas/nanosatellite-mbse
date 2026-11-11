import { cotsBinding, cotsBindingState, cotsUses, mergeCotsDraft } from '/cots-view.js';
import * as native from '/native-client.js';
import { metadata } from '/workbook.js';
import { parameterValueHTML } from '/requirement-preview.js';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const safeURL = value => { try { const url = new URL(value); return ['http:', 'https:'].includes(url.protocol) ? escape(url.href) : ''; } catch { return ''; } };
const valueHTML = fact => typeof fact.value === 'number' ? parameterValueHTML(fact.value, fact.unit) : `<code>${escape(String(fact.value))}</code>`;
const recordLabel = fact => `${fact.element} · ${fact.name} · ${fact.valueKind} · ${fact.condition.id || 'no stated condition'} · ${fact.source.locator}`;

export function createCotsEditor({ panel, getWorkspace, getReferenceWorkspace, getProducts, validate, onCommit,
  beforeOpen, onReturn, onOpenRequirement, onInsert, canInsert, returnLabel, onCatalogueRefresh = () => {} }) {
  let draft = null, token = 0, controller = null;
  const isOpen = () => Boolean(draft);
  const isVisible = () => Boolean(draft && !panel.hidden);
  const isDirty = () => Boolean(draft && JSON.stringify(draft.component.facts ?? []) !== JSON.stringify(draft.original.facts ?? []));
  const error = message => { const label = panel.querySelector('[data-cots-error]'); if (label) label.textContent = message; };
  function usesHTML(name = null) {
    const uses = cotsUses(getReferenceWorkspace(), draft.original, name);
    return uses.map(use => use.kind === 'requirement'
      ? `<button type="button" class="reference-link" data-cots-requirement="${use.key}" title="${escape(use.fields.join(', '))}">${escape(use.id)}</button>`
      : `<span title="${escape(use.fields.join(', '))}">${escape(use.id)}</span>`).join(' ') || '<span class="muted">None</span>';
  }
  function conditionHTML(fact) {
    const condition = fact.condition;
    if (!condition.id) return '<span class="muted">No stated condition</span>';
    const values = Object.entries(condition.values).map(([name, value]) => `${name}: ${value}`);
    values.push(...condition.parameters.map(item => `${item.parameter_name}: ${item.value} ${item.unit} (${item.value_kind}, ${item.source_id}, revision ${item.source_revision}, ${item.source_locator})`));
    return `<details><summary>${escape(condition.id)}</summary>${values.map(value => `<div>${escape(value)}</div>`).join('')}</details>`;
  }
  function sourceHTML(fact) {
    const source = fact.source, url = safeURL(source.url);
    return `${url ? `<a href="${url}" target="_blank" rel="noopener noreferrer">${escape(source.id)}</a>` : escape(source.id)}<div>${escape(source.locator)}</div><div class="muted">${escape(source.revision)}</div>`;
  }
  function renderReferences() {
    if (!draft) return;
    const facts = draft.facts ?? [];
    panel.querySelector('[data-cots-reference-list]').innerHTML = (draft.component.facts ?? []).map(binding => {
      const state = cotsBindingState(binding, facts);
      const before = draft.original.facts?.find(fact => fact.key === binding.key);
      return `<tr data-cots-binding="${binding.key}" data-state="${state.state}"><td><input data-cots-name aria-label="Reference name ${escape(binding.name)}" maxlength="40" autocomplete="off" spellcheck="false" value="${escape(binding.name)}"><code class="cots-qualified">${escape(draft.component.id)}.${escape(binding.name)}</code></td><td><select data-cots-record aria-label="Catalogue record for ${escape(binding.name)}">${!state.fact ? `<option value="${binding.fact}">Unavailable record</option>` : ''}${facts.map(fact => `<option value="${fact.id}" ${fact.id === binding.fact ? 'selected' : ''}>${escape(recordLabel(fact))}</option>`).join('')}</select><div class="cots-reference-status">${escape(state.message)}</div>${state.fact && state.state !== 'value' ? '<button type="button" class="cell-button" data-cots-update>Update fact</button>' : ''}</td><td class="cell-text" title="${escape(state.fact?.value)}">${state.state === 'value' ? valueHTML(state.fact) : 'Pending'}</td><td class="cell-text">${usesHTML(before?.name ?? binding.name)}</td><td><button type="button" class="cell-button" data-cots-copy>Copy reference</button>${canInsert() ? '<button type="button" class="cell-button" data-cots-insert>Insert reference</button>' : ''}<button type="button" class="cell-button" data-cots-remove>Remove</button></td></tr>`;
    }).join('');
    panel.querySelector('[data-cots-no-references]').hidden = Boolean(draft.component.facts?.length);
    panel.querySelector('[data-cots-used-by]').innerHTML = usesHTML();
  }
  function renderFacts() {
    if (!draft) return;
    const query = panel.querySelector('[data-cots-search]').value.toLowerCase();
    const facts = (draft.facts ?? []).filter(fact => `${recordLabel(fact)} ${fact.value} ${fact.unit} ${fact.type} ${JSON.stringify(fact.condition)} ${fact.source.id}`.toLowerCase().includes(query));
    panel.querySelector('[data-cots-fact-count]').textContent = draft.facts ? `${facts.length} of ${draft.facts.length} facts` : 'Loading catalogue…';
    panel.querySelector('[data-cots-fact-list]').innerHTML = facts.map(fact => {
      const selected = draft.component.facts?.some(binding => binding.fact === fact.id);
      return `<tr data-cots-fact="${fact.id}"><th scope="row"><code>${escape(fact.name)}</code><span class="muted">${escape(fact.element)} · ${escape(fact.type)}</span></th><td class="cell-text" title="${escape(fact.value)}">${valueHTML(fact)}</td><td class="cell-text">${escape(fact.valueKind)}</td><td class="cell-text">${conditionHTML(fact)}</td><td class="cell-text">${sourceHTML(fact)}</td><td><button type="button" class="cell-button" data-cots-use ${selected || (draft.component.facts?.length ?? 0) >= metadata(getWorkspace()).limits.facts ? 'disabled' : ''}>${selected ? 'Referenced' : 'Use fact'}</button></td></tr>`;
    }).join('');
  }
  function render() {
    const component = draft.component, product = getProducts().find(product => product.id === component.product);
    const url = safeURL(product?.datasheetUrl), back = returnLabel();
    panel.innerHTML = `<form><header class="requirement-editor-heading"><h2>COTS ${escape(component.id)}</h2><button type="button" data-cots-cancel aria-label="Close COTS pane">×</button></header><div class="requirement-editor-content">
      ${back ? `<button type="button" class="reference-link cots-back" data-cots-back>Back to ${escape(back)}</button>` : ''}
      <h3>${escape(product?.name ?? component.product)}</h3><p>${escape(component.product)}${url ? ` · <a href="${url}" target="_blank" rel="noopener noreferrer">Datasheet</a>` : ''}</p>
      <p>Catalogue facts are read-only. Select the element, value meaning and conditions that apply to your assessment. References use catalogue units. Convert explicitly in expressions.</p>
      <section class="sheet editor-sheet"><div class="table-top"><h3>Named fact references</h3></div><div class="table-frame cots-reference-frame"><table aria-label="COTS fact references"><colgroup><col class="cots-name-col"><col class="cots-record-col"><col class="cots-value-col"><col class="cots-uses-col"><col class="cots-actions-col"></colgroup><thead><tr><th>Reference</th><th>Catalogue record</th><th>Value</th><th>Used by</th><th>Actions</th></tr></thead><tbody data-cots-reference-list></tbody></table></div><p data-cots-no-references>Choose Use fact below to create a named reference.</p></section>
      <p>Used by: <span data-cots-used-by></span></p>
      <section class="sheet editor-sheet"><div class="table-top"><h3>Catalogue facts</h3></div><div class="cots-search"><input type="search" data-cots-search aria-label="Search COTS facts" placeholder="Find a property, condition, source or element"><button type="button" class="cell-button" data-cots-refresh>Refresh catalogue</button></div><p data-cots-fact-count></p><div class="table-frame cots-fact-frame"><table aria-label="COTS catalogue facts"><colgroup><col class="cots-property-col"><col class="cots-value-col"><col class="cots-meaning-col"><col class="cots-condition-col"><col class="cots-source-col"><col class="cots-uses-col"></colgroup><thead><tr><th>Property and element</th><th>Value and units</th><th>Meaning</th><th>Conditions</th><th>Source</th><th>Reference</th></tr></thead><tbody data-cots-fact-list></tbody></table></div></section>
      </div><footer class="requirement-editor-actions"><p data-cots-error class="error-text" role="alert"></p><button type="button" data-cots-cancel>Cancel</button><button type="submit" class="primary" data-cots-save>Save COTS</button></footer></form>`;
    renderReferences(); renderFacts();
  }
  async function loadFacts() {
    const generation = ++token;
    controller?.abort(); controller = new AbortController();
    try {
      const response = await fetch(`/api/cots?product=${encodeURIComponent(draft.component.product)}`, { signal: controller.signal });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error);
      if (!draft || generation !== token) return;
      draft.facts = data.facts; error(''); renderReferences(); renderFacts(); onCatalogueRefresh();
      if (draft.focusName) panel.querySelector(`[data-cots-binding="${draft.component.facts?.find(fact => fact.name === draft.focusName)?.key}"]`)?.scrollIntoView({ block: 'nearest' });
    } catch (failure) { if (draft && generation === token && failure.name !== 'AbortError') error(failure.message); }
  }
  function resume() {
    if (!draft) return;
    panel.hidden = false; document.body.classList.add('cots-editor-open');
    render(); loadFacts();
  }
  function suspend() { panel.hidden = true; document.body.classList.remove('cots-editor-open'); }
  function close(notify = true) {
    const anchor = draft?.anchor;
    draft = null; token++; controller?.abort(); suspend();
    if (notify) onReturn();
    if (panel.hidden && !returnLabel()) anchor?.isConnected && anchor.focus({ preventScroll: true });
  }
  function open(key, anchor, name) {
    if (draft?.component.key !== key && isDirty() && !window.confirm('Discard the unsaved COTS reference edits and open another component?')) return false;
    const component = getWorkspace().components.find(component => component.key === key);
    if (!component || !component.product || !beforeOpen()) return false;
    if (draft?.component.key !== key) draft = { component: structuredClone(component), original: structuredClone(component), facts: null, anchor };
    draft.focusName = name; resume(); return true;
  }
  function snapshot(base = getWorkspace()) {
    if (!draft) return base;
    return mergeCotsDraft(base, draft.original, draft.component);
  }
  async function save() {
    if (!draft) return false;
    panel.inert = true;
    try {
      // Validate against suspended local requirement edits without committing them.
      await native.normalize(snapshot(getReferenceWorkspace()));
      await onCommit(validate(snapshot()), draft.original, draft.component);
      close(); return true;
    } catch (failure) { error(failure.message); return false; }
    finally { panel.inert = false; }
  }
  panel.addEventListener('input', event => {
    if (!draft) return;
    if (event.target.matches('[data-cots-search]')) renderFacts();
    if (event.target.matches('[data-cots-name]')) {
      const binding = draft.component.facts.find(binding => binding.key === event.target.closest('[data-cots-binding]').dataset.cotsBinding);
      binding.name = event.target.value;
      event.target.nextElementSibling.textContent = `${draft.component.id}.${binding.name}`;
    }
  });
  panel.addEventListener('change', event => {
    if (!draft || !event.target.matches('[data-cots-record]')) return;
    const binding = draft.component.facts.find(binding => binding.key === event.target.closest('[data-cots-binding]').dataset.cotsBinding);
    const fact = draft.facts.find(fact => fact.id === event.target.value);
    Object.assign(binding, cotsBinding(fact, binding)); error(''); renderReferences(); renderFacts();
  });
  panel.addEventListener('click', async event => {
    if (!draft) return;
    const button = event.target.closest('button');
    if (!button) return;
    try {
      if (button.matches('[data-cots-cancel]')) { close(); return; }
      if (button.matches('[data-cots-back]')) { suspend(); onReturn(); return; }
      if (button.matches('[data-cots-refresh]')) { await loadFacts(); return; }
      if (button.matches('[data-cots-requirement]')) { suspend(); onOpenRequirement(button.dataset.cotsRequirement); return; }
      if (button.matches('[data-cots-use]')) {
        const fact = draft.facts.find(fact => fact.id === button.closest('[data-cots-fact]').dataset.cotsFact);
        const current = draft;
        const view = await native.command(snapshot(), { name: 'select_fact', target: draft.component.key, fact: fact.id, key: crypto.randomUUID() });
        if (draft !== current) return;
        draft.nativeState = view.workspace;
        draft.component = structuredClone(view.workspace.components.find(component => component.key === draft.component.key));
        renderReferences(); renderFacts(); return;
      }
      const binding = draft.component.facts?.find(binding => binding.key === button.closest('[data-cots-binding]')?.dataset.cotsBinding);
      if (!binding) return;
      if (button.matches('[data-cots-update]')) Object.assign(binding, cotsBinding(draft.facts.find(fact => fact.id === binding.fact), binding));
      if (button.matches('[data-cots-remove]')) {
        draft.component.facts = draft.component.facts.filter(fact => fact !== binding);
      }
      if (button.matches('[data-cots-copy]')) { await navigator.clipboard.writeText(`${draft.component.id}.${binding.name}`); error('Reference copied.'); return; }
      if (button.matches('[data-cots-insert]')) { const reference = `${draft.component.id}.${binding.name}`; if (await save()) onInsert(reference); return; }
      error(''); renderReferences(); renderFacts();
    } catch (failure) { error(failure.message); }
  });
  panel.addEventListener('submit', event => { event.preventDefault(); save(); });
  panel.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); close(); }
    if ((event.metaKey || event.ctrlKey) && ['Enter', 's'].includes(event.key)) { event.preventDefault(); event.stopPropagation(); save(); }
  });
  return { open, close, suspend, resume, snapshot, isOpen, isVisible, isDirty, save, key: () => draft?.component.key,
    refresh: () => {
      if (!isVisible()) return;
      const current = getWorkspace().components.find(component => component.key === draft.component.key);
      if (!current || current.id !== draft.original.id || current.product !== draft.original.product) {
        token++; controller?.abort();
        if (!current || isDirty()) { error('This COTS selection changed. Reopen its pane before saving the reference edits.'); return; }
        draft.component = structuredClone(current); draft.original = structuredClone(current); draft.facts = null;
        render(); loadFacts();
      } else if (!panel.querySelector('[data-cots-name]:focus')) renderReferences();
    } };
}
