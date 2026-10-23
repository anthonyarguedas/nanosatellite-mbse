import { lazy, Suspense, useEffect } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BatteryCharging,
  BookOpen,
  CircleHelp,
  Clock3,
  FileSliders,
  Play,
  ShieldAlert,
  Sun,
} from "lucide-react";
import type {
  Catalog,
  DesignInputs,
  NodeDefinition,
  NodeId,
  Product,
  Role,
  TabId,
} from "../types";
import { NODE_DEFINITIONS } from "../workflow";
import { SuggestionBadge } from "./CatalogView";
import { CalculationTrace } from "./CalculationTrace";
import { engineeringExchange, exchangeValue } from "./engineering-exchanges";
import { simulationPlotBasis } from "./result-history";
import { DemandPlot, EnergyPlots, OrbitDiagram } from "./Plots";
import {
  CheckList,
  Metric,
  Notice,
  NumberField,
  number,
  ROLE_NAMES,
  ScenarioSwitcher,
  Sheet,
  StatusBadge,
  unit,
} from "./ui";
import type { WorkspaceController } from "./ui";
import { applyMissionAnalogue } from "../mission-assist/integration";
import { TopologyChoices } from "./TopologyChoices";
import { InputBasis } from "./InputBasis";
import type { VariationId } from './design-canvas-model';

const MissionAssist = lazy(() => import("../mission-assist"));

export function canEvaluate(api: WorkspaceController, id: NodeId) {
  const definition = NODE_DEFINITIONS.find((node) => node.id === id);
  return (
    api.statuses[id] !== "locked" &&
    (api.missing[id]?.length ?? 0) === 0 &&
    Boolean(
      definition?.dependencies.every(
        (dependency) => api.statuses[dependency] === "complete",
      ),
    )
  );
}
function downstream(id: NodeId): NodeDefinition[] {
  const affected = new Set<NodeId>([id]);
  NODE_DEFINITIONS.forEach((node) => {
    if ([...node.dependencies, ...node.evidenceDependencies ?? []].some((dependency) => affected.has(dependency)))
      affected.add(node.id);
  });
  return NODE_DEFINITIONS.filter(
    (node) => node.id !== id && affected.has(node.id),
  );
}
function CandidateChoices({
  api,
  catalog,
  onInspect,
}: {
  api: WorkspaceController;
  catalog: Catalog;
  onInspect: (product: Product) => void;
}) {
  const suggestions = api.workspace.analysis.suggestions;
  if (!suggestions)
    return (
      <div className="empty-inline">
        <CircleHelp size={28} />
        <h3>Ready to find hardware?</h3>
        <p>
          Calculate this activity to compare the current sizing and topology against
          sourced catalog records. Missing evidence stays visible.
        </p>
      </div>
    );
  const fresh = api.statuses.candidates === "complete";
  const roles = [...new Set(suggestions.map((suggestion) => suggestion.role))];
  return (
    <>
      <div className="candidate-selects">
        {roles.map((role) => {
          const choices = suggestions.filter((s) => s.role === role);
          const selected = api.workspace.selections[role] ?? "";
          return (
            <div className="field" key={role}>
              <label htmlFor={`candidate-${role}`}>{ROLE_NAMES[role]}</label>
              <div className="select-wrap">
                <select
                  id={`candidate-${role}`}
                  value={selected}
                  disabled={!fresh}
                  onChange={(e) => {
                    if (e.target.value) api.selectProduct(role, e.target.value);
                  }}
                >
                  <option value="">Choose a candidate…</option>
                  {selected &&
                    !choices.some((s) => s.productId === selected) && (
                      <option value={selected}>
                        Previous selection (not in this screen)
                      </option>
                    )}
                  {choices.map((s) => (
                    <option
                      key={`${s.productId}-${s.role}`}
                      value={s.productId}
                      disabled={s.outcome === "rejected"}
                    >
                      {catalog.products.find((p) => p.id === s.productId)
                        ?.name ?? s.productId}{" "}
                      ·{" "}
                      {s.outcome === "incomplete"
                        ? "incomplete evidence"
                        : s.outcome === "rejected"
                          ? "rejected"
                          : "preliminary match"}
                      {s.quantity > 1 ? ` · screening count ${s.quantity}` : ""}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          );
        })}
      </div>
      <p className="section-caption">
        Screening counts are sizing estimates, not installed quantities.
        Applying a suggestion uses sourced fields where available and can mark
        dependent analyses stale. A preliminary allocation is not qualification.
      </p>
      <div className="candidate-list">
        {suggestions.map((suggestion, index) => {
          const product = catalog.products.find(
            (p) => p.id === suggestion.productId,
          );
          return (
            <article
              className={`candidate-item ${suggestion.outcome}`}
              key={`${suggestion.productId}-${suggestion.role}-${index}`}
            >
              <div className="candidate-item-top">
                <span>
                  {ROLE_NAMES[suggestion.role]} · screening count {suggestion.quantity}
                </span>
                <SuggestionBadge suggestion={suggestion} />
              </div>
              <h4>{product?.name ?? suggestion.productId}</h4>
              <small>{product?.manufacturer}</small>
              <p>{suggestion.reason}</p>
              {suggestion.missing.length > 0 && (
                <div className="missing-evidence">
                  <ShieldAlert size={12} />
                  {suggestion.missing.length} evidence gaps
                </div>
              )}
              {product && (
                <button
                  className="text-button"
                  data-focus-key={`product-${product.id}-${suggestion.role}`}
                  onClick={() => onInspect(product)}
                >
                  Inspect specifications
                  <ArrowUpRight size={13} />
                </button>
              )}
            </article>
          );
        })}
      </div>
    </>
  );
}
export const SCOPES: Record<NodeId, string> = {
  mission:
    "Engineer-authored mission assumptions. Altitude and lifetime are inputs, not inferred mission requirements.",
  orbit:
    "Ideal circular orbit using the eclipse geometry in the design proposal. Attitude, seasonal illumination, perturbations, and thermal effects are outside this model.",
  scenarios:
    "Mission activities may be sourced. All numerical powers, rail assignments, phase windows, illumination, and energy criteria are explicit study assumptions. Windows are fractions of one orbit. Active power replaces idle power. Overlapping windows for a load are unioned.",
  budget:
    "Scheduled constant-power loads and the additional EPS baseline are integrated over sunlight and eclipse. Average energy does not establish rail, pulse, current, or protection compliance.",
  solar:
    "Preliminary source-boundary EOL generation screen. Cell count is rounded up. It establishes no series/parallel arrangement, pointing, packing, or input-voltage compatibility. Xs and Xe belong to sizing only.",
  battery:
    "DoD and margin are explicit engineering assumptions. Cycle demand is calculated from mission duration. No cycle-life fit or qualification is invented. Margin is applied once in preliminary sizing. Retained energy sets physical EOL capacity.",
  topology:
    "Logical topology choices and a constant conditioning efficiency for the energy simulation. This model establishes no wiring, electrical interface, protection, or fault-independence assurance. Conditioning efficiency is separate from sizing efficiencies Xs and Xe.",
  candidates:
    "A bounded preliminary catalog screen. Unknown evidence is separate from a known violation. Typical values establish no guaranteed limits. Rejected suggestions cannot be selected.",
  simulation:
    "Explicit energy-only propagation with constant efficiencies, finite charge/discharge power, and scheduled loads. Charge-based state of charge, voltage, temperature, transients, and protection behavior are unassessed.",
  assessment:
    "Concept assessment against EPS-01–20. A known violation fails. Missing decisive evidence remains unassessed. An energy-only pass cannot establish charge-based reserve or replenishment compliance for EPS-10 and EPS-11.",
};
export function NodeInspector({
  id,
  role,
  variation,
  onCatalog,
  api,
  catalog,
  onClose,
  onNavigate,
  onInspect,
  onNode,
}: {
  id: NodeId;
  role?: Role;
  variation?: VariationId;
  onCatalog?: (role?: Role) => void;
  api: WorkspaceController;
  catalog: Catalog;
  onClose: () => void;
  onNavigate: (tab: TabId) => void;
  onInspect: (product: Product) => void;
  onNode: (id: NodeId) => void;
}) {
  useEffect(() => {
    if (!variation) return;
    const frame = requestAnimationFrame(() => {
      const target = document.querySelector<HTMLElement>(`[data-topology-axis="${variation}"]`);
      target?.focus({ preventScroll: true });
      target?.scrollIntoView({ block: 'center' });
    });
    return () => cancelAnimationFrame(frame);
  }, [variation]);
  const allocatedProduct = role ? catalog.products.find(product => product.id === api.workspace.selections[role]) : undefined;
  const definition = NODE_DEFINITIONS.find((node) => node.id === id)!;
  const { inputs, analysis } = api.workspace;
  const savedSimulationScenario = inputs.scenarios.find(
    (s) => s.id === analysis.simulation?.scenarioId,
  );
  const savedSimulationBasis = analysis.simulation
    ? simulationPlotBasis(analysis.simulation, savedSimulationScenario)
    : undefined;
  const status = api.statuses[id];
  const missing = api.missing[id] ?? [];
  const canRun = canEvaluate(api, id);
  const affected = downstream(id);
  const blockedDependency = definition.dependencies.find(dependency => api.statuses[dependency] !== 'complete');
  const editMission = (
    key: "name" | "altitudeKm" | "lifetimeYears",
    value: string | number | null,
  ) =>
    api.updateInputs("mission", (current) => ({
      ...current,
      mission: { ...current.mission, [key]: value },
    }));
  const editSolar = (key: keyof DesignInputs["solar"], value: number | null) =>
    api.updateInputs("solar", (current) => ({
      ...current,
      solar: { ...current.solar, [key]: value },
    }));
  const editBattery = (
    key: keyof DesignInputs["battery"],
    value: number | null,
  ) =>
    api.updateInputs("battery", (current) => ({
      ...current,
      battery: { ...current.battery, [key]: value },
    }));
  const editTopology = (patch: Partial<DesignInputs["topology"]>) =>
    api.updateInputs("topology", (current) => ({
      ...current,
      topology: { ...current.topology, ...patch },
    }));
  const evaluatedAt = api.workspace.records[id]?.evaluatedAt;
  return (
    <Sheet
      title={role ? ROLE_NAMES[role] : definition.title}
      eyebrow={role ? 'CSRM LOGICAL ROLE · LIVE EPS' : 'ENGINEERING ACTIVITY · PRELIMINARY MODEL'}
      onClose={onClose}
      footer={
        <>
          <div className="node-run-footer">
            <div>
              <StatusBadge status={status} />
              <small>
                {canRun
                  ? "All required dependencies are current."
                  : "Resolve missing or stale inputs before running."}
              </small>
            </div>
            <button
              className="button secondary"
              disabled={!canRun}
              onClick={() => api.runNode(id)}
            >
              <Play size={14} fill="currentColor" />
              {status === "stale"
                ? "Recompute"
                : status === "complete"
                  ? "Run again"
                  : "Calculate activity"}
            </button>
          </div>
        </>
      }
    >
      <p className="inspector-subtitle">{role ? 'Logical role allocation, associated model inputs and available evidence.' : definition.subtitle}</p>
      {status === "complete" && (
        <p className="freshness-disclaimer">
          Calculation current. Requirement verification is assessed separately.
        </p>
      )}
      {status === "stale" && (
        <Notice kind="warning" title="Historical results · inputs changed">
          An input or upstream result changed. These results remain visible for
          comparison and must be recomputed before downstream use.
          {definition.dependencies.some(
            (dep) => api.statuses[dep] !== "complete",
          ) && (
            <p>
              Refresh upstream:{" "}
              {definition.dependencies
                .filter((dep) => api.statuses[dep] !== "complete")
                .map(
                  (dep) =>
                    NODE_DEFINITIONS.find((node) => node.id === dep)?.title,
                )
                .join(", ")}
              .
            </p>
          )}
        </Notice>
      )}
      {missing.length > 0 && (
        <Notice kind="warning" title="Inputs needed for this activity">
          <ul className="plain-list">
            {missing.map((reason, index) => (
              <li key={index}>{reason}</li>
            ))}
          </ul>
          {blockedDependency && <button className="text-button" data-focus-key={`node-${blockedDependency}`} onClick={() => onNode(blockedDependency)}>Inspect {NODE_DEFINITIONS.find(node => node.id === blockedDependency)?.title}<ArrowRight size={13} /></button>}
        </Notice>
      )}
      <div className="node-work-view">
        {role && <section className="inspector-section role-allocation-context"><h3>Current role allocation</h3>
          {allocatedProduct ? <><button className="role-evidence-button" data-focus-key={`product-${allocatedProduct.id}`} onClick={() => onInspect(allocatedProduct)}><strong>{allocatedProduct.name}</strong><span>Inspect sourced evidence <ArrowUpRight size={13} /></span></button><p className="section-caption">A shared board remains one physical usage across its allocated roles. Role coverage does not prove electrical capacity or compatibility.</p></> : <Notice title="No product allocated">This is a logical reference role. A physical implementation has not been selected.</Notice>}
          <button className="button secondary full-width" data-focus-key="role-catalog" onClick={() => onCatalog ? onCatalog(role) : onNavigate('catalog')}>Compare products for this role<ArrowRight size={13} /></button>
          {(role === 'processor' || role === 'software') && <Notice kind="warning" title="Resources and services unassessed">Allocation does not establish memory capacity, task timing, host compatibility, protection autonomy or implemented software behavior.</Notice>}
        </section>}
        {id === "mission" && (
          <>
            <details className="mission-helper-entry">
              <summary><BookOpen size={15} />Explore mission analogues from ConOps</summary>
              <p className="body-copy">Orbit unknown? Compare sourced mission descriptions and explicitly accept an altitude as a circular study assumption.</p>
              <Suspense fallback={<p className="body-copy">Loading the local mission catalogue…</p>}>
                <MissionAssist
                  initialQuery={inputs.mission.conOps ?? ""}
                  onQueryChange={query => api.updateInputs("mission", current => ({ ...current, mission: { ...current.mission, conOps: query } }))}
                  onApply={match => api.updateInputs("mission", current => applyMissionAnalogue(current, match, current.mission.conOps ?? ""))}
                />
              </Suspense>
            </details>
            <section className="inspector-section">
              <div className="section-heading">
                <h3>Mission assumptions</h3>
                <span className="assumption-label">Engineer input</span>
              </div>
              <div className="field">
                <label htmlFor="mission-name">Design name</label>
                <input
                  id="mission-name"
                  type="text"
                  maxLength={200}
                  value={inputs.mission.name}
                  onChange={(e) => editMission("name", e.target.value)}
                  placeholder="Name your mission"
                />
              </div>
              <div className="form-grid">
                <NumberField
                  label="Orbit altitude"
                  value={inputs.mission.altitudeKm}
                  suffix="km"
                  min={1}
                  onChange={(value) => editMission("altitudeKm", value)}
                  hint="Representative circular reference. The BIRDS-4 example uses the camera discussion's 400 km context, not a precise flown orbit."
                />
                <NumberField
                  label="Mission lifetime"
                  value={inputs.mission.lifetimeYears}
                  suffix="years"
                  min={0}
                  onChange={(value) => editMission("lifetimeYears", value)}
                  hint="Used to calculate required cycling."
                />
              </div>
              <p className="section-caption">
                Clear a numeric field to leave it undefined. Missing values lock
                calculations that depend on them.
              </p>
            </section>
            {inputs.mission.orbitSuggestion && <Notice title={`Altitude source: ${inputs.mission.orbitSuggestion.missionName}`}>
              <p>{inputs.mission.orbitSuggestion.parameterOriginal}. {inputs.mission.orbitSuggestion.parameterMeaning}</p>
              <p>{inputs.mission.orbitSuggestion.method === "semantic-qwen" ? "Local Qwen semantic cosine" : "Offline TF-IDF cosine"}: {number(inputs.mission.orbitSuggestion.cosine, 3)}. Retrieval rank, not suitability probability.</p>
              <p>Parameter epoch: {inputs.mission.orbitSuggestion.missionEpoch}</p>
              <p>Accepted {inputs.mission.orbitSuggestion.acceptedAt}. Mission record {inputs.mission.orbitSuggestion.missionRevision}.</p>
              {inputs.mission.orbitSuggestion.sources.filter(source => inputs.mission.orbitSuggestion!.parameterSourceIds.includes(source.id)).map(source => <a key={source.id} className="mission-origin-source" href={source.url} target="_blank" rel="noreferrer">{source.title} · {source.revision} · {source.location}</a>)}
            </Notice>}
            {inputs.mission.name.includes("BIRDS-4") && (
              <Notice title="BIRDS-4-inspired concept study">
                Mission activities are sourced. Lifetime and numerical EPS
                assumptions are authored. Catalog alternatives are not claimed
                to be the flown architecture.
              </Notice>
            )}
            <OrbitDiagram
              orbit={
                api.statuses.orbit === "complete" ? analysis.orbit : undefined
              }
              altitudeKm={inputs.mission.altitudeKm}
            />
          </>
        )}
        {id === "orbit" && (
          <>
            <OrbitDiagram
              orbit={analysis.orbit}
              altitudeKm={status === "stale" ? null : inputs.mission.altitudeKm}
            />
            {analysis.orbit && (
              <div className="metric-grid two">
                <Metric
                  label="Orbits per day"
                  value={number(analysis.orbit.orbitsPerDay, 2)}
                />
                <Metric
                  label="Sunlight fraction"
                  value={`${number(analysis.orbit.sunlightFraction * 100)}%`}
                />
              </div>
            )}
            <button className="text-button" onClick={() => onNode("mission")}>
              Edit altitude and lifetime
              <ArrowRight size={13} />
            </button>
          </>
        )}
        {id === "scenarios" && (
          <>
            <ScenarioSwitcher api={api} />
            {api.activeScenario ? (
              <>
                <p className="body-copy">{api.activeScenario.description}</p>
                <div className="metric-grid two">
                  <Metric
                    label="Scheduled loads"
                    value={api.activeScenario.loads.length}
                  />
                  <Metric
                    label="Duration"
                    value={`${number(api.activeScenario.durationOrbits, 0)} orbits`}
                  />
                  <Metric
                    label="Illumination factor"
                    value={`${number(api.activeScenario.illuminationFactor * 100, 0)}%`}
                  />
                  <Metric
                    label="Minimum energy reserve"
                    value={`${number(api.activeScenario.minimumEnergyFraction * 100, 0)}%`}
                  />
                </div>
                <Notice title="Authored demonstration scenario">
                  {api.activeScenario.provenance}
                </Notice>
              </>
            ) : (
              <Notice kind="warning">
                No active scenario is defined. Open the scenario editor to
                create an operating case and add loads.
              </Notice>
            )}
            <button
              className="button secondary full-width"
              onClick={() => onNavigate("scenarios")}
            >
              <FileSliders size={15} />
              Open scenario editor
              <ArrowRight size={14} />
            </button>
          </>
        )}
        {id === "budget" && (
          <>
            <ScenarioSwitcher api={api} compact />
            <NumberField label="Additional EPS baseline" value={inputs.topology.idlePowerW} suffix="W" min={0} onChange={value => editTopology({ idlePowerW: value })} hint="Added once to scheduled spacecraft loads in both sizing and simulation. Review operating-state applicability and excluded heater demand." />
            {analysis.budget ? (
              <>
                <div className="metric-grid two">
                  <Metric
                    label="Average demand"
                    value={unit(analysis.budget.averageW, "W")}
                  />
                  <Metric
                    label="Peak demand"
                    value={unit(analysis.budget.peakW, "W")}
                  />
                  <Metric
                    label="Sunlight energy"
                    value={unit(analysis.budget.sunlightWh, "Wh")}
                  />
                  <Metric
                    label="Eclipse energy"
                    value={unit(analysis.budget.eclipseWh, "Wh")}
                  />
                </div>
                <DemandPlot
                  budget={analysis.budget}
                  orbit={analysis.orbit}
                  scenario={
                    inputs.scenarios.find(
                      (s) => s.id === analysis.budget?.scenarioId,
                    ) ??
                    (analysis.budget.scenarioId === undefined
                      ? api.activeScenario
                      : undefined)
                  }
                  stale={status !== "complete"}
                />
              </>
            ) : (
              <div className="empty-inline">
                <Sun size={28} />
                <p>Run the budget to integrate the active load schedule.</p>
              </div>
            )}
            <button
              className="text-button"
              onClick={() => onNavigate("scenarios")}
            >
              Edit the load schedule
              <ArrowRight size={13} />
            </button>
          </>
        )}
        {id === "solar" && (
          <>
            {analysis.solar && (
              <div className="result-highlight">
                <Sun size={24} />
                <div>
                  <small>Minimum source-boundary EOL power</small>
                  <strong>
                    {number(analysis.solar.minimumPowerW)} <span>W</span>
                  </strong>
                </div>
                <div>
                  <small>Rounded cell count</small>
                  <strong>{analysis.solar.cellCount ?? "Unresolved"}</strong>
                </div>
              </div>
            )}
            <section className="inspector-section">
              <div className="section-heading">
                <h3>Preliminary sizing</h3>
                <span className="assumption-label">Engineer input</span>
              </div>
              <div className="form-grid">
                <NumberField
                  label="Sunlight path efficiency, Xs"
                  value={inputs.solar.sunlightEfficiency}
                  suffix="0–1"
                  min={0.001}
                  max={1}
                  onChange={(value) => editSolar("sunlightEfficiency", value)}
                />
                <NumberField
                  label="Eclipse path efficiency, Xe"
                  value={inputs.solar.eclipseEfficiency}
                  suffix="0–1"
                  min={0.001}
                  max={1}
                  onChange={(value) => editSolar("eclipseEfficiency", value)}
                />
                <NumberField
                  label="Cell EOL MPP voltage"
                  value={inputs.solar.cellEolV}
                  suffix="V"
                  min={0.001}
                  onChange={(value) => editSolar("cellEolV", value)}
                />
                <NumberField
                  label="Cell EOL MPP current"
                  value={inputs.solar.cellEolA}
                  suffix="A"
                  min={0.001}
                  onChange={(value) => editSolar("cellEolA", value)}
                />
              </div>
            </section>
            <section className="inspector-section">
              <h3>Installed generation</h3>
              <NumberField
                label="Available source-boundary EOL power"
                value={inputs.solar.installedPowerW}
                suffix="W"
                min={0}
                onChange={(value) => editSolar("installedPowerW", value)}
                hint="Separate engineer input for simulation. Sizing does not automatically install a panel or define an array."
              />
              <Notice>
                Illumination is applied by the active scenario. Conditioning
                efficiency is applied once in the simulation, separately from Xs
                and Xe.
              </Notice>
            </section>
          </>
        )}
        {id === "battery" && (
          <>
            {analysis.battery && (
              <>
                <div className="result-highlight">
                  <BatteryCharging size={24} />
                  <div>
                    <small>Preliminary required capacity</small>
                    <strong>
                      {number(analysis.battery.requiredWh)} <span>Wh</span>
                    </strong>
                  </div>
                </div>
                <div className="metric-grid two">
                  <Metric
                    label="Required mission cycles"
                    value={number(analysis.battery.cycles, 0)}
                    hint="Demand, not a supported life rating"
                  />
                  <Metric
                    label="Effective EOL capacity"
                    value={unit(analysis.battery.eolCapacityWh, "Wh")}
                  />
                </div>
              </>
            )}
            <section className="inspector-section">
              <div className="section-heading">
                <h3>Sizing assumptions</h3>
                <span className="assumption-label">Engineer input</span>
              </div>
              <div className="form-grid">
                <NumberField
                  label="Design DoD limit"
                  value={inputs.battery.dod}
                  suffix="0–1"
                  min={0.001}
                  max={1}
                  onChange={(value) => editBattery("dod", value)}
                />
                <NumberField
                  label="Degradation sizing margin, M"
                  value={inputs.battery.margin}
                  suffix="fraction"
                  min={0}
                  onChange={(value) => editBattery("margin", value)}
                />
              </div>
              <Notice kind="warning">
                DoD is an assumption until supported by applicable cell or pack
                cycle-life evidence. No empirical cycle-life coefficients are
                assumed.
              </Notice>
            </section>
            <section className="inspector-section">
              <h3>Installed storage & energy model</h3>
              {inputs.battery.capacityWh === null && <Notice kind="warning" title="Pack usable energy is unresolved">Preliminary sizing and catalog screening can continue. Simulation needs characterized capacity or an explicit study assumption below. You can also compare another pack. No previous product rating is reused.</Notice>}
              <div className="form-grid">
                <NumberField
                  label="BOL pack energy"
                  value={inputs.battery.capacityWh}
                  suffix="Wh"
                  min={0.001}
                  onChange={(value) => editBattery("capacityWh", value)}
                  hint="A manual value is recorded as an engineering assumption. The selected product's missing catalog evidence remains unresolved."
                />
                <NumberField
                  label="Retained energy factor, fE"
                  value={inputs.battery.retainedEnergy}
                  suffix="0–1"
                  min={0.001}
                  max={1}
                  onChange={(value) => editBattery("retainedEnergy", value)}
                />
              </div>
              <details className="disclosure battery-energy-assumptions"><summary>Charge / discharge assumptions & power limits</summary>
              <div className="form-grid">
                <NumberField
                  label="Charge energy efficiency"
                  value={inputs.battery.chargeEfficiency}
                  suffix="0–1"
                  min={0.001}
                  max={1}
                  onChange={(value) => editBattery("chargeEfficiency", value)}
                />
                <NumberField
                  label="Discharge energy efficiency"
                  value={inputs.battery.dischargeEfficiency}
                  suffix="0–1"
                  min={0.001}
                  max={1}
                  onChange={(value) =>
                    editBattery("dischargeEfficiency", value)
                  }
                />
                <NumberField
                  label="Maximum charge power"
                  value={inputs.battery.maxChargeW}
                  suffix="W"
                  min={0}
                  onChange={(value) => editBattery("maxChargeW", value)}
                />
                <NumberField
                  label="Maximum discharge power"
                  value={inputs.battery.maxDischargeW}
                  suffix="W"
                  min={0}
                  onChange={(value) => editBattery("maxDischargeW", value)}
                />
              </div>
              </details>
              <p className="section-caption">
                EOL capacity = BOL pack energy × retained energy. The
                preliminary margin is not applied again.
              </p>
            </section>
          </>
        )}
        {id === "topology" && (
          <>
            <section className="inspector-section">
              <h3>Power architecture choices</h3>
              <TopologyChoices topology={inputs.topology} onChange={editTopology} />
            </section>
            <section className="inspector-section">
              <div className="section-heading">
                <h3>Simulation & resource assumptions</h3>
                <span className="assumption-label">Engineer input</span>
              </div>
              <NumberField
                label="Constant conditioning efficiency"
                value={inputs.topology.efficiency}
                suffix="0–1"
                min={0.001}
                max={1}
                onChange={(value) => editTopology({ efficiency: value })}
                hint="Energy simulation only. This is not reused as Xs or Xe."
              />
              <div className="form-grid">
                <NumberField
                  label="EPS idle consumption"
                  value={inputs.topology.idlePowerW}
                  suffix="W"
                  min={0}
                  onChange={(value) => editTopology({ idlePowerW: value })}
                />
                <NumberField
                  label="EPS mass allocation"
                  value={inputs.topology.massAllocationKg}
                  suffix="kg"
                  min={0.001}
                  onChange={(value) =>
                    editTopology({ massAllocationKg: value })
                  }
                />
              </div>
              <Notice kind="warning">
                A constant efficiency does not characterize attainable DET
                operating points, conversion envelopes, or detailed distribution
                losses.
              </Notice>
            </section>
          </>
        )}
        {id === "candidates" && (
          <>
            {!role && <CandidateChoices
              api={api}
              catalog={catalog}
              onInspect={onInspect}
            />}
            <button
              className="button secondary full-width"
              onClick={() => onNavigate("catalog")}
            >
              Browse the complete COTS catalog
              <ArrowRight size={13} />
            </button>
          </>
        )}
        {id === "simulation" && (
          <>
            <details
              className="run-setup"
              open={analysis.simulation ? undefined : true}
            >
              <summary>
                Next run ·{" "}
                {api.activeScenario?.name ?? "select an operating case"}
              </summary>
              <div>
                <ScenarioSwitcher api={api} compact />
                {api.activeScenario && (
                  <div className="metric-grid three">
                    <Metric
                      label="Initial energy input"
                      value={`${number(api.activeScenario.initialEnergyFraction * 100, 0)}%`}
                    />
                    <Metric
                      label="Reserve input"
                      value={`${number(api.activeScenario.minimumEnergyFraction * 100, 0)}%`}
                    />
                    <Metric
                      label="Duration input"
                      value={`${number(api.activeScenario.durationOrbits, 0)} orbits`}
                    />
                  </div>
                )}
                <button
                  className="text-button"
                  onClick={() => onNavigate("scenarios")}
                >
                  Edit scenario and energy assumptions
                  <ArrowRight size={13} />
                </button>
              </div>
            </details>
            {analysis.simulation && savedSimulationBasis ? (
              <>
                <div className="metric-grid three saved-run-metrics">
                  <Metric
                    label="Initial energy (saved)"
                    value={`${number(savedSimulationBasis.initialPercent, 0)}%`}
                  />
                  <Metric
                    label={
                      savedSimulationBasis.legacyReserve
                        ? "Reserve (legacy reference)"
                        : "Reserve (saved)"
                    }
                    value={
                      savedSimulationBasis.reservePercent === undefined
                        ? "Not recorded"
                        : `${number(savedSimulationBasis.reservePercent, 0)}%`
                    }
                  />
                  <Metric
                    label={
                      analysis.simulation.durationS === undefined
                        ? "Recorded history"
                        : "Requested duration (saved)"
                    }
                    value={unit(savedSimulationBasis.durationS / 60, "min")}
                  />
                </div>
                <EnergyPlots
                  simulation={analysis.simulation}
                  scenario={savedSimulationScenario}
                  stale={status !== "complete"}
                  compact
                />
                <CheckList checks={analysis.simulation.checks} />
                <details className="disclosure">
                  <summary>Simulation assumptions</summary>
                  <ul className="plain-list">
                    {analysis.simulation.assumptions.map(
                      (assumption, index) => (
                        <li key={index}>{assumption}</li>
                      ),
                    )}
                  </ul>
                </details>
              </>
            ) : (
              <Notice title="Inspect the history, not just the average">
                Run the energy model to compare generation, scheduled demand,
                and stored energy over the scenario. This is an energy-only
                assessment.
              </Notice>
            )}
          </>
        )}
        {id === "assessment" && (
          <>
            <Notice title="Three outcomes, distinct meanings">
              Pass requires evidence for the declared scope. Known violations
              fail. Missing decisive evidence remains unassessed.
            </Notice>
            <CheckList checks={analysis.checks ?? []} />
            <button
              className="button secondary full-width"
              onClick={() => onNavigate("assessments")}
            >
              Open assessment report
              <ArrowRight size={13} />
            </button>
          </>
        )}
      </div>
      <InputBasis workspace={api.workspace} catalog={catalog} node={id} />
      <details className="inspector-section calculation-section disclosure" data-testid="calculation-details">
        <summary>Equations, dependencies & model scope</summary>
        <div className="requirement-chips">{definition.requirements.map(requirement => <span key={requirement}>{requirement}</span>)}{evaluatedAt && <span className="evaluated-time"><Clock3 size={11} />Last run {new Date(evaluatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>}</div>
        {definition.dependencies.length > 0 && <div className="dependency-chips"><span>Depends on</span>{definition.dependencies.map(dep => <button key={dep} className={api.statuses[dep]} data-focus-key={`node-${dep}`} onClick={() => onNode(dep)}><i />{NODE_DEFINITIONS.find(node => node.id === dep)?.title}<ArrowUpRight size={10} /></button>)}</div>}
        {definition.dependencies.length > 0 && (
          <section className="received-exchanges">
            <h3>Engineering information received</h3>
            {definition.dependencies.map((source) => {
              const exchange = engineeringExchange(source, id);
              const historical =
                api.statuses[source] === "stale" &&
                !["mission", "scenarios", "topology"].includes(source);
              return (
                <div
                  className={`received-exchange ${historical ? "historical" : ""}`}
                  key={source}
                >
                  <div>
                    <span>{exchange.label}</span>
                    <button
                      className="text-button"
                      onClick={() => onNode(source)}
                    >
                      {
                        NODE_DEFINITIONS.find((node) => node.id === source)
                          ?.title
                      }
                      <ArrowUpRight size={11} />
                    </button>
                  </div>
                  <p>
                    {historical ? "Historical · " : ""}
                    {exchangeValue(source, id, api.workspace)}
                  </p>
                  <small>{exchange.description}</small>
                </div>
              );
            })}
          </section>
        )}
        <CalculationTrace nodeId={id} workspace={api.workspace} />
        <div className="section-heading">
          <h3>Equation & model scope</h3>
          <BookOpen size={14} />
        </div>
        <code className="equation">{definition.equation}</code>
        <p className="body-copy">{SCOPES[id]}</p>
        <details className="disclosure">
          <summary>Sources & change impact</summary>
          <p className="body-copy">
            Design proposal: Orbit Requirements and Power Budget, EPS Component
            Selection, and parameter-based requirements EPS-01–20. Preliminary
            orbit and sizing equations follow El Hachimi et al., Sections 2–3.
          </p>
          {affected.length > 0 && (
            <>
              <strong className="small-heading">
                Outputs affected by edits here
              </strong>
              <div className="affected-nodes">
                {affected.map((node) => (
                  <span key={node.id}>{node.title}</span>
                ))}
              </div>
            </>
          )}
        </details>
      </details>
    </Sheet>
  );
}
