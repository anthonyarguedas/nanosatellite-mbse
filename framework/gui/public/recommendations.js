import { escape } from '/editor.js';

export function createRecommendations({ dialog, request }) {
  const $ = selector => dialog.querySelector(selector);
  const csrmNames = { Battery: 'Batteries', SolarArray: 'Solar Arrays', RegulatorAndConverter: 'Regulators and Converters',
    PowerCircuit: 'Power Circuits and Switches', ProcessorAndMemory: 'Processor and Memory', Software: 'Software' };
  const value = (number, unit) => escape(`${number}${unit ? ` ${unit}` : ''}`);
  const meaning = kind => kind.replaceAll('_', ' ').replace(/^./, char => char.toUpperCase());
  const option = (key, text) => `<option value="${escape(key)}">${escape(text)}</option>`;
  const link = (url, text) => url ? `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(text)}</a>` : escape(text);
  const source = (id, url, locator) => `${link(url, id)}${locator ? `<small>${escape(locator)}</small>` : ''}`;
  let component = null, generation = 0, propertyKinds = {};
  const overrides = new Map();

  function changed() {
    $('#recommendations-summary').textContent = 'Find matches to apply these query settings.';
    $('#recommendations-results').replaceChildren();
    $('#recommendations-case').replaceChildren();
    $('#recommendations-error').textContent = '';
  }
  function renderOverrides() {
    const selected = $('#recommendations-property').value;
    const available = Object.keys(propertyKinds).filter(name => !overrides.has(name));
    $('#recommendations-property').innerHTML = available.map(name => option(name, name)).join('');
    if (available.includes(selected)) $('#recommendations-property').value = selected;
    $('#recommendations-property').disabled = !available.length;
    $('#recommendations-add-kind').disabled = !available.length;
    $('#recommendations-value-kinds').innerHTML = [...overrides].map(([name, kind], index) => {
      const kinds = [...new Set([...(propertyKinds[name] || []), ...(kind ? [kind] : [])])];
      return `<div class="recommendation-kind-row"><label for="recommendation-kind-${index}"><code>${escape(name)}</code></label>
        <select id="recommendation-kind-${index}" data-kind-property="${escape(name)}" aria-label="Value meaning for ${escape(name)}">${option('', 'Catalog default')}${kinds.map(item => option(item, meaning(item))).join('')}</select>
        <button type="button" data-remove-kind="${escape(name)}" aria-label="Remove value meaning for ${escape(name)}">×</button></div>`;
    }).join('');
    for (const select of dialog.querySelectorAll('[data-kind-property]')) select.value = overrides.get(select.dataset.kindProperty);
  }
  function options(result) {
    const sort = $('#recommendations-sort'), channel = $('#recommendations-channel');
    const sortBy = sort.value, elementId = channel.value;
    sort.innerHTML = option('', 'Catalog order (unsorted)') + result.sortProperties.map(name => option(name, name)).join('');
    if (sortBy && !result.sortProperties.includes(sortBy)) sort.insertAdjacentHTML('beforeend', option(sortBy, sortBy));
    sort.value = sortBy;
    channel.innerHTML = option('', 'All compatible channels') + result.channels.map(name => option(name, name === 'self' ? 'Purchased product (self)' : name)).join('');
    channel.value = elementId;
    channel.disabled = !result.channels.length;
    $('#recommendations-conditions').innerHTML = result.conditions.map(item => `<option value="${escape(item.id)}" label="${escape(item.label || item.id)}"></option>`).join('');
    $('#recommendations-condition').disabled = !result.conditions.length && !$('#recommendations-condition').value;
    propertyKinds = result.valueKinds;
    renderOverrides();
  }
  function renderCase(condition) {
    $('#recommendations-case').innerHTML = condition ? `<details class="recommendation-case"><summary>Selected condition details</summary><p class="hint"><code>${escape(condition.id)}</code></p>
      <dl>${condition.fields.map(field => `<div><dt>${escape(field.name.replaceAll('_', ' '))}</dt><dd>${escape(field.value)}</dd></div>`).join('')}</dl>
      ${condition.parameters.length ? `<div class="table-frame"><table aria-label="Selected condition parameters"><thead><tr><th>Parameter</th><th>Value</th><th>Meaning</th><th>Source</th></tr></thead><tbody>${condition.parameters.map(item => `<tr><td class="cell-text">${escape(item.parameter_name)}</td><td class="cell-text">${value(item.value, item.unit)}</td><td class="cell-text">${escape(meaning(item.value_kind))}</td><td class="cell-text">${source(item.source_id, item.sourceUrl, item.source_locator)}</td></tr>`).join('')}</tbody></table></div>` : ''}
      </details>` : '';
  }
  function facts(match) {
    const count = match.bindings.reduce((total, binding) => total + binding.facts.length, 0);
    if (!count) return '';
    return `<details><summary>${count} selected facts and sources</summary><div class="table-frame"><table aria-label="Selected facts for ${escape(match.partNumber)}"><thead><tr><th>Property</th><th>Value</th><th>Meaning and condition</th><th>Source</th></tr></thead><tbody>${match.bindings.map(binding => binding.facts.map(fact => `<tr>
      <td class="cell-text"><code>${escape(binding.property)}</code><small>${escape(fact.parameter)} · ${escape(fact.elementId)}</small></td>
      <td class="cell-text">${value(fact.value, fact.unit)}</td>
      <td class="cell-text">${escape(meaning(fact.valueKind))}<small>${escape(fact.conditionId || 'No condition ID')}</small></td>
      <td class="cell-text">${source(fact.sourceId, fact.sourceUrl, fact.sourceLocator)}${fact.note ? `<p class="hint">${escape(fact.note)}</p>` : ''}</td>
      </tr>`).join('')).join('')}</tbody></table></div></details>`;
  }
  function checks(match) {
    if (!match.checks.length) return '';
    return `<details><summary>${match.checks.length} checks passed</summary><div class="table-frame"><table aria-label="Passing checks for ${escape(match.partNumber)}"><thead><tr><th>Requirement</th><th>Measure</th><th>Target</th><th>Predicate</th></tr></thead><tbody>${match.checks.map(check => `<tr><td class="cell-text">${escape(check.requirement)}<small>${escape(check.condition)}</small></td><td class="cell-text">${value(check.measure, check.measureUnit)}</td><td class="cell-text">${value(check.target, check.targetUnit)}</td><td class="cell-text"><code>${escape(check.predicate)}</code></td></tr>`).join('')}</tbody></table></div></details>`;
  }
  function render(result, limit) {
    const count = result.results.length;
    $('#recommendations-summary').textContent = `Showing ${count} recommendation${count === 1 ? '' : 's'} · ${result.compatibleProducts} compatible products · ${result.compatibleCount} channel candidates · ${result.catalogSize} catalog products`;
    $('#recommendations-scope').textContent = result.requirements
      ? `Every condition in the ${result.requirements} directly owned requirement${result.requirements === 1 ? '' : 's'} must pass. EPS and bus requirements are outside this query.`
      : 'No requirements are assigned. Results are unconstrained. EPS and bus requirements are outside this query.';
    renderCase(result.selectedCondition);
    if (!count) {
      const message = !result.catalogSize ? 'The built-in catalog is empty.'
        : limit === 0 ? 'The maximum is zero. Increase it to display recommendations.'
        : !result.compatibleCount ? 'The built-in catalog has no compatible products for this component or channel.'
        : result.requirements ? 'No candidates pass every owned check and sorting filter. Unresolved checks, errors and unavailable sort values exclude candidates.'
        : 'No candidates have an available finite value for the selected sort property. Change the property or fact selection.';
      $('#recommendations-results').innerHTML = `<p class="empty">${message}</p>`;
      return;
    }
    $('#recommendations-results').innerHTML = result.results.map((match, index) => `<article class="recommendation-card">
      <header><span class="recommendation-rank">${index + 1}</span><div class="recommendation-identity"><h3>${escape(match.partNumber)}</h3><small>${escape(match.manufacturer)} · ${escape(match.className)}</small></div>
        <span class="result" data-state="${match.checks.length ? 'pass' : 'pending'}">${match.checks.length ? 'Pass owned checks' : 'Unconstrained'}</span>
        ${match.sortValue !== '' ? `<strong class="recommendation-value">${value(match.sortValue, match.sortUnit)}</strong>` : ''}</header>
      <p class="hint">CSRM: ${escape(match.csrmTypes.map(name => csrmNames[name] || name).join(', '))}</p>
      <dl class="recommendation-context"><div><dt>Queried role</dt><dd>${escape(csrmNames[match.role] || match.role)}</dd></div><div><dt>Channel</dt><dd><code>${escape(match.elementId)}</code></dd></div><div><dt>Requested case</dt><dd><code>${escape(match.conditionId || 'Default selection')}</code></dd></div></dl>
      <p class="recommendation-links">${link(match.datasheetUrl, 'Datasheet')}${match.productUrl && match.productUrl !== match.datasheetUrl ? ` · ${link(match.productUrl, 'Product page')}` : ''}<small>${escape(match.productId)}</small></p>
      ${checks(match)}${facts(match)}
      ${match.unsetProperties.length ? `<details><summary>${match.unsetProperties.length} unset properties</summary><p class="hint">These include product data gaps and mission or installation inputs.</p><p class="recommendation-unset">${match.unsetProperties.map(name => `<code>${escape(name)}</code>`).join(', ')}</p></details>` : ''}
      </article>`).join('');
  }
  async function search() {
    if (!component) return;
    const version = ++generation, sortBy = $('#recommendations-sort').value;
    const limit = $('#recommendations-limit').value === '' ? null : Number($('#recommendations-limit').value);
    $('#recommendations-error').textContent = '';
    $('#recommendations-summary').textContent = 'Checking the built-in COTS catalog…';
    $('#recommendations-results').replaceChildren();
    $('#recommendations-case').replaceChildren();
    $('#recommendations-controls').disabled = true;
    try {
      const result = await request('/api/recommend-cots', { path: component.path, sortBy: sortBy || null,
        reverse: Boolean(sortBy) && $('#recommendations-order').value === 'descending', limit,
        elementId: $('#recommendations-channel').value || null, conditionId: $('#recommendations-condition').value.trim(),
        valueKinds: Object.fromEntries([...overrides].filter(([, kind]) => kind)) });
      if (version !== generation || !dialog.open) return;
      options(result);
      render(result, limit);
    } catch (failure) {
      if (version === generation && dialog.open) {
        $('#recommendations-error').textContent = failure.message;
        $('#recommendations-summary').textContent = 'Query could not complete.';
      }
    } finally {
      if (version === generation) $('#recommendations-controls').disabled = false;
    }
  }
  $('#recommendations-sort').addEventListener('change', () => {
    $('#recommendations-order').disabled = !$('#recommendations-sort').value;
  });
  $('#recommendations-add-kind').addEventListener('click', () => {
    const name = $('#recommendations-property').value;
    if (name) { overrides.set(name, ''); renderOverrides(); changed(); }
  });
  $('#recommendations-value-kinds').addEventListener('change', event => {
    if (event.target.matches('[data-kind-property]')) overrides.set(event.target.dataset.kindProperty, event.target.value);
  });
  $('#recommendations-value-kinds').addEventListener('click', event => {
    const button = event.target.closest('[data-remove-kind]');
    if (button) { overrides.delete(button.dataset.removeKind); renderOverrides(); changed(); $('#recommendations-property').focus(); }
  });
  $('#recommendations-form').addEventListener('input', event => { if (event.target.id !== 'recommendations-property') changed(); });
  $('#recommendations-form').addEventListener('change', event => { if (event.target.id !== 'recommendations-property') changed(); });
  $('#recommendations-form').addEventListener('submit', event => {
    event.preventDefault();
    if (!$('#recommendations-controls').disabled) search();
  });
  dialog.addEventListener('close', () => { generation++; component = null; });
  return {
    open(item, mode) {
      component = item; overrides.clear(); propertyKinds = {};
      $('#recommendations-context').textContent = `${item.path} · ${mode || 'Default evaluation'}`;
      $('#recommendations-sort').innerHTML = option('', 'Catalog order (unsorted)');
      $('#recommendations-channel').innerHTML = option('', 'All compatible channels');
      $('#recommendations-condition').value = '';
      $('#recommendations-conditions').replaceChildren();
      $('#recommendations-order').value = 'ascending';
      $('#recommendations-order').disabled = true;
      $('#recommendations-limit').value = '5';
      $('#recommendations-scope').textContent = 'Checking owned requirements in a temporary Mission.';
      $('.recommendation-kind-settings').open = false;
      renderOverrides();
      dialog.showModal();
      search();
    },
  };
}
