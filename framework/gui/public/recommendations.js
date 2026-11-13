import { escape } from '/editor.js';

export function createRecommendations({ dialog, request }) {
  const $ = selector => dialog.querySelector(selector);
  let component = null, generation = 0;
  const value = (number, unit) => escape(`${number}${unit ? ` ${unit}` : ''}`);
  function render(result, limit) {
    const count = result.results.length;
    $('#recommendations-summary').textContent = `${count} recommendation${count === 1 ? '' : 's'} · ${result.compatibleCount} compatible candidates · ${result.requirements} owned requirements`;
    $('#recommendations-scope').textContent = result.requirements
      ? 'Every owned requirement must pass. Pending checks and errors exclude a candidate.'
      : 'No requirements are assigned. Compatible candidates are returned without a compliance assessment.';
    if (!result.catalogSize) {
      $('#recommendations-results').innerHTML = '<p class="empty">This session has no COTS catalog. Define a <code>cots_catalog</code> iterable of detached COTS instances in its Python file.</p>';
    } else if (!count) {
      $('#recommendations-results').innerHTML = `<p class="empty">${limit === 0 ? 'The maximum is zero. Increase it to display recommendations.' : !result.compatibleCount ? 'The catalog has no compatible COTS for this component.' : 'No candidates meet every requirement with the selected sort property. Missing, nonnumeric and nonfinite sort values are excluded.'}</p>`;
    } else {
      $('#recommendations-results').innerHTML = result.results.map((match, index) => `<article class="recommendation-card">
        <header><span class="recommendation-rank">${index + 1}</span><div><h3>${escape(match.name)}</h3><small>${escape(match.className)}</small></div><span class="result" data-state="${match.checks.length ? 'pass' : 'pending'}">${match.checks.length ? 'Pass' : 'Unconstrained'}</span>${match.sortValue ? `<strong class="recommendation-value">${value(match.sortValue, match.sortUnit)}</strong>` : ''}</header>
        ${match.checks.length ? `<details><summary>${match.checks.length} checks passed</summary><div class="table-frame"><table aria-label="Passing checks for ${escape(match.name)}"><thead><tr><th>Requirement</th><th>Measure</th><th>Target</th><th>Predicate</th></tr></thead><tbody>${match.checks.map(check => `<tr><td class="cell-text">${escape(check.requirement)}<small>${escape(check.condition)}</small></td><td class="cell-text">${value(check.measure, check.measureUnit)}</td><td class="cell-text">${value(check.target, check.targetUnit)}</td><td class="cell-text"><code>${escape(check.predicate)}</code></td></tr>`).join('')}</tbody></table></div></details>` : ''}
      </article>`).join('');
    }
  }
  async function search(initial = false) {
    if (!component) return;
    const version = ++generation, sortBy = $('#recommendations-sort').value;
    const limit = $('#recommendations-limit').value === '' ? null : Number($('#recommendations-limit').value);
    $('#recommendations-error').textContent = '';
    $('#recommendations-summary').textContent = 'Checking COTS…';
    $('#recommendations-results').replaceChildren();
    $('#recommendations-query').disabled = true;
    try {
      const result = await request('/api/recommend-cots', { path: component.path, sortBy: sortBy || null,
        reverse: Boolean(sortBy) && $('#recommendations-order').value === 'descending', limit });
      if (version !== generation || !dialog.open) return;
      if (initial) $('#recommendations-sort').innerHTML = '<option value="">Catalog order (unsorted)</option>'
        + result.sortProperties.map(name => `<option value="${escape(name)}">${escape(name)}</option>`).join('');
      render(result, limit);
    } catch (failure) {
      if (version === generation) {
        $('#recommendations-error').textContent = failure.message;
        $('#recommendations-summary').textContent = 'Query could not complete.';
      }
    } finally {
      if (version === generation) $('#recommendations-query').disabled = false;
    }
  }
  $('#recommendations-sort').addEventListener('change', () => {
    $('#recommendations-order').disabled = !$('#recommendations-sort').value;
  });
  $('#recommendations-form').addEventListener('submit', event => { event.preventDefault(); search(); });
  dialog.addEventListener('close', () => { generation++; component = null; });
  return {
    open(item, mode) {
      component = item;
      $('#recommendations-context').textContent = `${item.path} · ${mode || 'Default evaluation'}`;
      $('#recommendations-sort').innerHTML = '<option value="">Catalog order (unsorted)</option>';
      $('#recommendations-order').value = 'ascending';
      $('#recommendations-order').disabled = true;
      $('#recommendations-limit').value = '5';
      $('#recommendations-scope').textContent = 'Checking the component’s owned requirements in a temporary Mission.';
      dialog.showModal();
      search(true);
    },
  };
}
