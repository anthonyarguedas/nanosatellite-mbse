import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { CatalogView, DEFAULT_CATALOG_FILTERS, ProductInspector, specValue } from './CatalogView';
import type { WorkspaceController } from './ui';
import { catalog } from '../data/catalog';
import { createExampleWorkspace } from '../state/model';
import { nodeStatuses } from '../workflow';

const noop = () => {};
function controller(): WorkspaceController {
  const workspace = createExampleWorkspace();
  return { workspace, statuses: nodeStatuses(workspace), selectProduct: noop } as unknown as WorkspaceController;
}
describe('comparison coverage presentation', () => {
  it('separates role coverage, richer gaps and assessment in the inspector', () => {
    const html = renderToStaticMarkup(<ProductInspector product={catalog.products[0]} catalog={catalog} api={controller()} onClose={noop} onCandidates={noop} onApplied={noop} />);
    expect(html).toContain('comparison data:');
    expect(html).toContain('Missing required comparison data');
    expect(html).toContain('Richer characterization gaps');
    expect(html).toContain('does not establish installed compatibility');
    expect(html).toContain('Candidate screen');
    expect(html).not.toContain('Not published');
  });
  it('filters role-specific profile coverage without implying a feasible option', () => {
    const html = renderToStaticMarkup(<CatalogView catalog={catalog} api={controller()} onInspect={noop} onCandidates={noop} filters={{ ...DEFAULT_CATALOG_FILTERS, role: 'software', coverage: 'covered' }} />);
    expect(html).toContain('Quetzal');
    expect(html).not.toContain('No products in this view');
    expect(html).toContain('3 profile-covered');
    expect(html).toContain('Target deficit: 0');
  });
  it('renders intervals and min/typ/max tuples with distinct meaning', () => {
    const base = catalog.products[0].specs.massKg;
    expect(specValue({ ...base, value: [1, 2], valueForm: 'interval' })).toBe('[1 – 2] kg');
    expect(specValue({ ...base, value: [1, 2, 3], valueForm: 'min-typ-max' })).toBe('min 1, typ 2, max 3 kg');
  });
});
