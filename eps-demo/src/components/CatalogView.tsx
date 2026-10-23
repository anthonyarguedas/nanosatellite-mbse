import { useMemo, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BatteryCharging,
  BookOpen,
  Box,
  Check,
  CircleHelp,
  ExternalLink,
  PackageSearch,
  Search,
  ShieldAlert,
  Sun,
  X,
  Zap,
} from "lucide-react";
import type {
  Catalog,
  Product,
  Role,
  Specification,
  Suggestion,
} from "../types";
import {
  Notice,
  number,
  ROLE_NAMES,
  ROLES,
  SelectField,
  Sheet,
  StatusBadge,
} from "./ui";
import type { WorkspaceController } from "./ui";
import { getAllocationQuantity } from "../engine/allocations";
import { catalogCoverage, productCoverage } from "../catalog/coverage";
import { COMPARISON_SCOPE } from "../catalog/profiles";
import { legacyArrayForm } from "../catalog/validation";

export const SPEC_LABELS: Record<string, string> = {
  powerBolW: "Power at BOL",
  powerEolW: "Power at EOL",
  vmpBolV: "MPP voltage at BOL",
  impBolA: "MPP current at BOL",
  vmpEolV: "MPP voltage at EOL",
  impEolA: "MPP current at EOL",
  vocV: "Open-circuit voltage",
  iscA: "Short-circuit current",
  energyWh: "Rated energy",
  chargeAh: "Rated charge",
  voltageMinV: "Minimum voltage",
  voltageNominalV: "Nominal voltage",
  voltageMaxV: "Maximum voltage",
  massKg: "Mass",
  widthM: "Width",
  heightM: "Height",
  depthM: "Depth",
  inputMinV: "Input voltage, minimum",
  inputMaxV: "Input voltage, maximum",
  maxInputW: "Maximum input power",
  maxChargeA: "Charge current limit",
  maxDischargeA: "Discharge current limit",
  efficiency: "Efficiency",
  priceUsd: "Dated price",
  cycleLife: "Cycle life",
};
export function specLabel(key: string) {
  return (
    SPEC_LABELS[key] ??
    key.replace(/([A-Z])/g, " $1").replace(/^./, (char) => char.toUpperCase())
  );
}
export function specValue(spec?: Specification): string {
  if (spec?.status === "not-applicable") return "Not applicable";
  if (!spec || spec.status === "missing" || spec.value === null)
    return "Missing evidence";
  const value =
    typeof spec.value === "number"
      ? (spec.value !== 0 && Math.abs(spec.value) < .01
          ? Number(spec.value.toPrecision(4)).toString()
          : number(spec.value, Math.abs(spec.value) < 1 ? 3 : 2).replace(/\.?0+$/, ''))
      : Array.isArray(spec.value)
        ? spec.valueForm === 'min-typ-max'
          ? `min ${spec.value[0]}, typ ${spec.value[1]}, max ${spec.value[2]}`
          : spec.valueForm === 'set' ? `{${spec.value.join(', ')}}` : `[${spec.value.join(' – ')}]`
        : spec.value;
  return `${value}${spec.unit ? ` ${spec.unit}` : ""}`;
}
function bestSuggestion(productId: string, suggestions: Suggestion[] | undefined, role: Role) {
  const matches = suggestions?.filter((s) => s.productId === productId && s.role === role);
  return (
    matches?.find((s) => s.outcome === "preliminary-match") ??
    matches?.find((s) => s.outcome === "incomplete") ??
    matches?.[0]
  );
}
export function SuggestionBadge({ suggestion }: { suggestion: Suggestion }) {
  return (
    <span className={`suggestion-badge ${suggestion.outcome}`}>
      {suggestion.outcome === "preliminary-match" ? (
        <Check size={11} />
      ) : (
        <CircleHelp size={11} />
      )}
      {suggestion.outcome === "preliminary-match"
        ? "Preliminary match"
        : suggestion.outcome === "incomplete"
          ? "Screen incomplete"
          : "Rejected by screen"}
    </span>
  );
}
function ProductCard({
  product,
  suggestion,
  selected,
  onInspect,
  role,
}: {
  product: Product;
  role: Role;
  suggestion?: Suggestion;
  selected: boolean;
  onInspect: () => void;
}) {
  const coverage = productCoverage(product, role);
  const keys: string[] = ({ solar: ['powerEolW', 'vmpEolV', 'massKg'], battery: ['energyWh', 'voltageNominalV', 'massKg'],
    conditioning: ['inputMaxV', 'conditioningMode', 'massKg'], distribution: ['outputChannelCount', 'outputRails', 'massKg'],
    processor: ['processorDescription', 'programBytes', 'dataBytes'], software: ['softwareRelease', 'supportedHosts', 'serviceDefinitions'] })[role];
  const Icon = product.roles.includes("solar")
    ? Sun
    : product.roles.includes("battery")
      ? BatteryCharging
      : Zap;
  const missingCount = Object.values(product.specs).filter(
    (s) => s.status === "missing",
  ).length;
  return (
    <article className={`product-card ${selected ? "selected" : ""}`}>
      <div className="product-card-top">
        <span className="product-symbol">
          <Icon size={22} strokeWidth={1.5} />
        </span>
        <div>
          <span className="eyebrow">{product.manufacturer}</span>
          <h3>{product.name}</h3>
        </div>
        <span className="product-level">{product.catalogUse === 'reference-only' ? 'Published reference only' : product.level}</span>
      </div>
      <p className="product-description">{product.description}</p>
      <div className="role-chips">
        {product.roles.map((role) => (
          <span key={role}>{ROLE_NAMES[role]}</span>
        ))}
      </div>
      <div className="product-specs">
        {keys.map((key) => (
          <div key={key}>
            <small>{specLabel(key)}</small>
            <strong
              title={specValue(product.specs[key])}
              className={
                !product.specs[key] || product.specs[key].status === "missing"
                  ? "missing-value"
                  : ""
              }
            >
              {specValue(product.specs[key])}
            </strong>
            {product.specs[key]?.status === "available" && (
              <span>{product.specs[key].meaning}</span>
            )}
          </div>
        ))}
      </div>
      <div className="product-evidence">
        {suggestion ? (
          <SuggestionBadge suggestion={suggestion} />
        ) : (
          <span>
            <BookOpen size={12} />
            Sourced catalog record
          </span>
        )}
        <span>Comparison data {coverage.coreCovered}/{coverage.coreRequired}</span>
        {missingCount > 0 && <span>{missingCount} recorded gaps</span>}
      </div>
      <footer>
        <button className="text-button" data-focus-key={`product-${product.id}`} data-inspect-product={product.id} onClick={onInspect}>
          Inspect evidence
          <ArrowRight size={14} />
        </button>
        {selected ? (
          <span className="product-selected">
            <Check size={12} />
            Allocated
          </span>
        ) : product.sources[0] ? (
          <a
            href={product.sources[0].url}
            target="_blank"
            rel="noreferrer"
            title={product.sources[0].title}
          >
            Source document
            <ArrowUpRight size={12} />
          </a>
        ) : (
          <span className="micro-copy">No source available</span>
        )}
      </footer>
    </article>
  );
}
export interface CatalogFilters { search: string; role: string; manufacturer: string; level: string; onlyCandidates: boolean; coverage?: string }
export const DEFAULT_CATALOG_FILTERS: CatalogFilters = { search: '', role: 'all', manufacturer: 'all', level: 'all', onlyCandidates: false, coverage: 'all' };

export function CatalogView({
  api,
  catalog,
  onInspect,
  onCandidates,
  filters,
  onFiltersChange,
}: {
  api: WorkspaceController;
  catalog: Catalog;
  onInspect: (product: Product) => void;
  onCandidates: () => void;
  filters?: CatalogFilters;
  onFiltersChange?: (filters: CatalogFilters) => void;
}) {
  const [localFilters, setLocalFilters] = useState(DEFAULT_CATALOG_FILTERS);
  const currentFilters = filters ?? localFilters;
  const { search, role, manufacturer, level, onlyCandidates, coverage: coverageFilter = 'all' } = currentFilters;
  const coverageReport = useMemo(() => catalogCoverage(catalog), [catalog]);
  const change = (patch: Partial<CatalogFilters>) => (onFiltersChange ?? setLocalFilters)({ ...currentFilters, ...patch });
  const setSearch = (search: string) => change({ search });
  const setRole = (role: string) => change({ role });
  const setManufacturer = (manufacturer: string) => change({ manufacturer });
  const setLevel = (level: string) => change({ level });
  const setOnlyCandidates = (onlyCandidates: boolean) => change({ onlyCandidates });
  const suggestions = api.workspace.analysis.suggestions;
  const manufacturers = [
    ...new Set(catalog.products.map((p) => p.manufacturer)),
  ].sort();
  const levels = [...new Set(catalog.products.map((p) => p.level))].sort();
  const filtered = useMemo(
    () =>
      catalog.products.filter((product) => {
        const query = search.trim().toLowerCase();
        return (
          (!query ||
            `${product.name} ${product.manufacturer} ${product.partNumber} ${product.description}`
              .toLowerCase()
              .includes(query)) &&
          (role === "all" || product.roles.includes(role as Role)) &&
          (manufacturer === "all" || product.manufacturer === manufacturer) &&
          (level === "all" || product.level === level) &&
          (coverageFilter === 'all' || product.roles.filter(r => role === 'all' || r === role).some(r => productCoverage(product, r).comparisonCovered === (coverageFilter === 'covered'))) &&
          (!onlyCandidates ||
            suggestions?.some((s) => s.productId === product.id))
        );
      }),
    [catalog, search, role, manufacturer, level, onlyCandidates, suggestions, coverageFilter],
  );
  const clear = () => (onFiltersChange ?? setLocalFilters)({ ...DEFAULT_CATALOG_FILTERS });
  return (
    <div className="tab-page catalog-page">
      <div className="page-intro">
        <div>
          <span className="eyebrow">SOURCES, CONDITIONS & MISSING DATA</span>
          <h3>Inspect before allocating.</h3>
          <p>
            Inspect the original specifications, conditions, and gaps before you
            allocate.
          </p>
        </div>
        <button className="button secondary" onClick={onCandidates}>
          <PackageSearch size={15} />
          Candidate screening
          <ArrowUpRight size={13} />
        </button>
      </div>
      <div className="catalog-toolbar">
        <div className="search-field">
          <Search size={16} />
          <input
            type="search"
            aria-label="Search catalog products"
            placeholder="Search products, manufacturers, part numbers…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button
              className="icon-button"
              aria-label="Clear product search"
              onClick={() => setSearch("")}
            >
              <X size={13} />
            </button>
          )}
        </div>
        <div className="catalog-filters">
          <SelectField label="CSRM role" value={role} onChange={setRole}>
            <option value="all">All roles</option>
            {ROLES.map((r) => (
              <option key={r} value={r}>
                {ROLE_NAMES[r]}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="Manufacturer"
            value={manufacturer}
            onChange={setManufacturer}
          >
            <option value="all">All manufacturers</option>
            {manufacturers.map((m) => (
              <option key={m}>{m}</option>
            ))}
          </SelectField>
          <SelectField label="Comparison data" value={coverageFilter} onChange={coverage => change({ coverage })}>
            <option value="all">All coverage</option><option value="covered">Required profile data covered</option><option value="gaps">Missing core data</option>
          </SelectField>
          <SelectField label="Product level" value={level} onChange={setLevel}>
            <option value="all">All levels</option>
            {levels.map((l) => (
              <option key={l}>{l}</option>
            ))}
          </SelectField>
        </div>
      </div>
      <details className="disclosure"><summary>Comparison profile coverage · target 3 distinct options per role</summary>
        <p className="section-caption">{COMPARISON_SCOPE}</p>
        <ul className="plain-list">{coverageReport.roles.map(item => <li key={item.role}>{ROLE_NAMES[item.role]}: {item.coveredOptions} profile-covered / {item.distinctOptions} distinct options ({item.records} records). Target deficit: {item.deficit}.</li>)}</ul>
      </details>
      <div className="catalog-results-bar">
        <div>
          <strong>{filtered.length}</strong> products
          <span> / catalog {catalog.revision}</span>
        </div>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={onlyCandidates}
            onChange={(e) => setOnlyCandidates(e.target.checked)}
          />
          Candidate suggestions only
        </label>
      </div>
      {suggestions && api.statuses.candidates !== "complete" && (
        <Notice kind="warning" title="Candidate screen is not current">
          Catalog records remain browseable. Recompute candidates before
          applying a selection.
        </Notice>
      )}
      {!suggestions && onlyCandidates && (
        <Notice>
          Candidate suggestions have not been calculated. Open candidate
          screening to run the current design.
        </Notice>
      )}
      {filtered.length === 0 ? (
        <div className="large-empty">
          <PackageSearch size={36} strokeWidth={1.2} />
          <h2>No products in this view</h2>
          <p>Try a different role, manufacturer, or search term.</p>
          <button className="button secondary" onClick={clear}>
            Clear filters
          </button>
        </div>
      ) : (
        <div className="product-grid">
          {filtered.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              role={role === 'all' ? product.roles[0] : role as Role}
              suggestion={bestSuggestion(product.id, suggestions, role === 'all' ? product.roles[0] : role as Role)}
              selected={Object.values(api.workspace.selections).includes(
                product.id,
              )}
              onInspect={() => onInspect(product)}
            />
          ))}
        </div>
      )}
      <div className="catalog-disclaimer">
        <ShieldAlert size={15} />
        <p>
          Catalog evidence supports preliminary comparison. Typical ratings
          establish no guaranteed operating limit. Availability, pricing,
          integration, and qualification are unassessed unless explicitly
          sourced.
        </p>
      </div>
    </div>
  );
}
export function ProductInspector({
  product,
  catalog,
  api,
  onClose,
  onCandidates,
  onApplied,
}: {
  product: Product;
  catalog: Catalog;
  api: WorkspaceController;
  onClose: () => void;
  onCandidates: () => void;
  onApplied: () => void;
}) {
  const suggestions =
    api.workspace.analysis.suggestions?.filter(
      (s) => s.productId === product.id,
    ) ?? [];
  const [selectedRole, setSelectedRole] = useState<string>(
    suggestions[0]?.role ?? product.roles[0],
  );
  const suggestion = suggestions.find((s) => s.role === selectedRole);
  const fresh = api.statuses.candidates === "complete";
  const canApply =
    fresh && Boolean(suggestion) && suggestion?.outcome !== "rejected" && !suggestion?.checks.some(check => check.verdict === 'fail');
  const alreadySelected =
    api.workspace.selections[selectedRole as Role] === product.id;
  const allocatedQuantity = getAllocationQuantity(api.workspace, product.id);
  const receipt = api.workspace.allocations?.find(item => item.productId === product.id);
  const confirmed = alreadySelected && allocatedQuantity === suggestion?.quantity
    && receipt?.productRevision === product.revision;
  const coverage = productCoverage(product, selectedRole as Role);
  const missing = Object.entries(product.specs).filter(
    ([, spec]) => spec.status === "missing",
  );
  return (
    <Sheet
      title={product.name}
      eyebrow={`${product.manufacturer} / ${product.level} / ${product.partNumber}`}
      onClose={onClose}
      footer={
        <>
          <div className="allocation-controls">
            <SelectField
              label="Selection role"
              value={selectedRole}
              onChange={setSelectedRole}
            >
              {[
                ...new Set([
                  ...suggestions.map((s) => s.role),
                  ...product.roles,
                ]),
              ].map((role) => (
                <option key={role} value={role}>
                  {ROLE_NAMES[role]}
                </option>
              ))}
            </SelectField>
            <button
              className="button primary"
              disabled={!canApply}
              onClick={() => {
                api.selectProduct(selectedRole as Role, product.id);
                onApplied();
              }}
            >
              {confirmed ? (
                <><Check size={14} />Reapply allocation ×{allocatedQuantity}</>
              ) : (
                <>{alreadySelected ? "Update allocation" : "Allocate product"}{suggestion && ` ×${suggestion.quantity}`}<ArrowRight size={14} /></>
              )}
            </button>
          </div>
          <small className="allocation-disclosure">
            {!fresh
              ? "Run a fresh candidate screen to enable selection."
              : product.catalogUse === 'reference-only'
                ? 'Published mission context only. No characterized finished pack or procurement allocation is inferred.'
                : !suggestion
                ? "No candidate suggestion supports this role."
                : suggestion.outcome === "rejected"
                  ? "A known violation blocks this selection."
                  : suggestion.outcome === "incomplete"
                    ? "Preliminary allocation. Missing evidence remains unassessed."
                    : "Preliminary match only. Review all conditions before use."}
          </small>
        </>
      }
    >
      <div className="product-inspector-meta">
        <span className="subtle-pill">Revision {product.revision}</span>
        <div className="role-chips">
          {product.roles.map((role) => (
            <span key={role}>{ROLE_NAMES[role]}</span>
          ))}
        </div>
      </div>
      <p className="body-copy">{product.description}</p>
      <section className="inspector-section" data-testid="comparison-coverage">
        <h3>{ROLE_NAMES[selectedRole as Role]} comparison data: {coverage.coreCovered}/{coverage.coreRequired}</h3>
        <p className="section-caption">Profile {coverage.profileRevision}. {coverage.scope}</p>
        {coverage.identityIssues.length > 0 && <Notice title="Identity gaps"><ul className="plain-list">{coverage.identityIssues.map(issue => <li key={issue}>{issue}</li>)}</ul></Notice>}
        <details className="disclosure"><summary>Missing required comparison data ({coverage.coreRequired - coverage.coreCovered})</summary>
          <ul className="plain-list">{coverage.core.filter(item => !item.covered).map(item => <li key={item.id}><strong>{item.label}</strong><ul>{item.issues.map((issue, index) => <li key={index}>{issue}</li>)}</ul></li>)}</ul>
        </details>
        <details className="disclosure"><summary>Richer characterization gaps ({coverage.richer.filter(item => !item.covered).length})</summary>
          <ul className="plain-list">{coverage.richer.filter(item => !item.covered).map(item => <li key={item.id}>{item.label}: {item.issues.join('. ')}</li>)}</ul>
        </details>
      </section>
      {suggestion ? (
        <section className="inspector-section">
          <div className="section-heading">
            <h3>Candidate screen</h3>
            <StatusBadge status={api.statuses.candidates} small />
          </div>
          <SuggestionBadge suggestion={suggestion} />
          <p className="body-copy">{suggestion.reason}</p>
          <div className="quantity-note">
            <Box size={14} />
            Suggested concept count <strong>×{suggestion.quantity}</strong>
          </div>
          <p className="section-caption">{allocatedQuantity === null ? "No frozen count is recorded for this product." : `Current allocated concept count: ${allocatedQuantity}.`} Applying the product explicitly freezes the suggested count. Installed arrangement and electrical compatibility remain unassessed.</p>
          {suggestion.missing.length > 0 && (
            <Notice kind="warning" title="Incomplete evidence">
              <ul className="plain-list">
                {suggestion.missing.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </Notice>
          )}
          {suggestion.checks.length > 0 && (
            <details className="disclosure">
              <summary>
                View screening checks <span>{suggestion.checks.length}</span>
              </summary>
              <div className="mini-checks">
                {suggestion.checks.map((check, i) => (
                  <div key={`${check.id}-${i}`}>
                    <span className={`verdict ${check.verdict}`}>
                      {check.verdict}
                    </span>
                    <strong>
                      {check.id} · {check.title}
                    </strong>
                    <p>{check.detail}</p>
                  </div>
                ))}
              </div>
            </details>
          )}
        </section>
      ) : (
        <Notice title="Catalog record, not a selection recommendation">
          Run the current design's candidate screen to assess this product.
          <button className="text-button" onClick={onCandidates}>
            Open candidate screening
            <ArrowRight size={13} />
          </button>
        </Notice>
      )}
      <section className="inspector-section">
        <div className="section-heading">
          <h3>Source specifications</h3>
          <span>{missing.length} missing</span>
        </div>
        <p className="section-caption">
          Every value retains its meaning, original representation, and
          operating conditions.
        </p>
        <div className="specification-list">
          {Object.entries(product.specs).map(([key, spec]) => {
            const sources = product.sources.filter(s => s.id === spec.sourceId || spec.additionalSourceIds?.includes(s.id));
            return (
              <details className={`specification ${spec.status}`} key={key}>
                <summary>
                  <span>{specLabel(key)}</span>
                  <strong>{specValue({ ...spec, valueForm: spec.valueForm ?? legacyArrayForm(product, key) })}</strong>
                  <span className="spec-meaning">
                    {spec.status === "available"
                      ? spec.meaning
                      : spec.status === "missing"
                        ? "missing"
                        : "N/A"}
                  </span>
                </summary>
                <div className="specification-detail">
                  <dl>
                    <dt>Original</dt>
                    <dd>{spec.original || "No original value published."}</dd>
                    <dt>Conditions</dt>
                    <dd>{spec.conditions || "Conditions not specified."}</dd>
                    {spec.rationale && (
                      <>
                        <dt>Rationale</dt>
                        <dd>{spec.rationale}</dd>
                      </>
                    )}
                    <dt>Location</dt>
                    <dd>{spec.location || "Not specified"}</dd>
                    <dt>Source</dt>
                    <dd>
                      {sources.length ? sources.map(source => (
                        <a key={source.id} href={source.url} target="_blank" rel="noreferrer">
                          {source.title}
                          <ExternalLink size={11} />
                        </a>
                      )) : (
                        "No source for this property"
                      )}
                    </dd>
                  </dl>
                </div>
              </details>
            );
          })}
        </div>
      </section>
      <details className="inspector-section disclosure">
        <summary>Supported configurations</summary>
        {product.supportedConfigurations.length ? (
          <ul className="plain-list">
            {product.supportedConfigurations.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="body-copy">Configuration evidence is not available.</p>
        )}
      </details>
      <section className="inspector-section">
        <h3>Accounting boundary</h3>
        <p className="body-copy">{product.accountingBoundary}</p>
        {product.caveats.length > 0 && (
          <Notice kind="warning" title="Scope & caveats">
            <ul className="plain-list">
              {product.caveats.map((caveat, i) => (
                <li key={i}>{caveat}</li>
              ))}
            </ul>
          </Notice>
        )}
      </section>
      <section className="inspector-section">
        <div className="section-heading">
          <h3>Original sources</h3>
          <BookOpen size={15} />
        </div>
        {product.sources.map((source) => (
          <div className="source-card" key={source.id}>
            <a href={source.url} target="_blank" rel="noreferrer">
              {source.title}
              <ArrowUpRight size={14} />
            </a>
            <small>
              {source.revision} · {source.location}
            </small>
            <span>Retrieved {source.retrievedAt}</span>
            <small>Publisher: {source.publisher ?? 'Not recorded'} · Kind: {source.kind ?? 'Legacy source record'}</small>
            {source.sha256 && <details className="disclosure"><summary>Reviewed content SHA-256</summary><code>{source.sha256}</code></details>}
            <a
              className="source-url"
              href={source.url}
              target="_blank"
              rel="noreferrer"
            >
              {source.url}
            </a>
          </div>
        ))}
      </section>
    </Sheet>
  );
}
