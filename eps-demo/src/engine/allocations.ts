import type { AllocationReceipt, Catalog, Role, Workspace } from '../types';

export const EPS_ROLES: Role[] = ['solar', 'battery', 'conditioning', 'distribution', 'processor', 'software'];
type AllocationSubject = Pick<Workspace, 'selections' | 'allocations'>;
/** Exact, deterministic record identity. This is a comparison snapshot, not a signature or approval. */
export function productSnapshot(product: Catalog['products'][number]): string {
  const canonical = (value: unknown): unknown => Array.isArray(value) ? value.map(canonical)
    : value && typeof value === 'object' ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => [key, canonical(item)])) : value;
  return JSON.stringify(canonical(product));
}
const sameRoles = (a: Role[], b: Role[]) => a.length === b.length && new Set(a).size === a.length && a.every(role => b.includes(role));

/** Frozen concept quantity only. Legacy/malformed allocations return null; never infer a quantity from suggestions. */
export function getAllocationQuantity(subject: AllocationSubject, productId: string): number | null {
  const receipts = subject.allocations?.filter(item => item.productId === productId) ?? [];
  if (receipts.length !== 1) return null;
  const receipt = receipts[0];
  const roles = EPS_ROLES.filter(role => subject.selections[role] === productId);
  return roles.length && sameRoles(receipt.roles, roles) && Number.isSafeInteger(receipt.quantity)
    && receipt.quantity > 0 && receipt.quantity <= 256 ? receipt.quantity : null;
}

/** Receipt identity and bounded whole-product checks. Missing legacy receipts are allowed, not manufactured. */
export function allocationIssues(subject: AllocationSubject, catalog: Catalog): string[] {
  const issues: string[] = [];
  const seen = new Set<string>();
  for (const receipt of subject.allocations ?? []) {
    const product = catalog.products.find(item => item.id === receipt.productId);
    const roles = EPS_ROLES.filter(role => subject.selections[role] === receipt.productId);
    if (product?.catalogUse === 'reference-only') issues.push(`${receipt.productId}: published reference-only assembly is not an allocatable product.`);
    if (seen.has(receipt.productId)) issues.push(`Duplicate allocation receipt for ${receipt.productId}.`);
    seen.add(receipt.productId);
    const snapshotMatches = product && receipt.productSnapshot === productSnapshot(product);
    if (!product || receipt.productRevision !== product.revision
      || (receipt.catalogRevision !== catalog.revision && !snapshotMatches)
      || (receipt.productSnapshot !== undefined && !snapshotMatches)) {
      issues.push(`${receipt.productId}: allocation product/catalog revision is absent or mismatched. Review and explicitly reallocate. Unchanged records require an exact saved product snapshot across catalog updates.`);
    }
    if (!roles.length || !sameRoles(receipt.roles, roles) || receipt.roles.some(role => !product?.roles.includes(role))) {
      issues.push(`${receipt.productId}: allocation roles do not match selected product/role identity.`);
    }
    const maximum = product?.level === 'cell' ? 256 : product?.level === 'panel' ? 8 : 1;
    if (!Number.isSafeInteger(receipt.quantity) || receipt.quantity < 1 || receipt.quantity > maximum) {
      issues.push(`${receipt.productId}: allocation quantity must be a whole number in 1..${maximum}; finished packs and boards remain one fixed product.`);
    }
    if (!['engineer-allocation', 'bundled-example'].includes(receipt.origin) || !receipt.rationale.trim()
      || Number.isNaN(Date.parse(receipt.allocatedAt))) issues.push(`${receipt.productId}: allocation origin, rationale or date is invalid.`);
  }
  return issues;
}
