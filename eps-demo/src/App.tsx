import { lazy, Suspense, useCallback, useEffect, useRef, useState } from "react";
import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  ArrowUpFromLine,
  BatteryCharging,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  FilePlus2,
  FlaskConical,
  FolderOpen,
  GitBranch,
  Layers3,
  Orbit,
  PackageSearch,
  Play,
  Plus,
  Satellite,
  ShieldCheck,
  SlidersHorizontal,
  Sun,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useWorkspace } from "./state/workspace";
import { catalog } from "./data/catalog";
import { BIRDS4_SOURCE } from "./data/scenarios";
import type { NodeId, Product, Scenario, TabId } from "./types";
import { Architecture } from "./components/Architecture";
import { AssessmentView } from "./components/AssessmentView";
import { CatalogView, ProductInspector } from "./components/CatalogView";
import { canEvaluate, NodeInspector } from "./components/NodeInspector";
import { ScenarioEditor } from "./components/ScenarioEditor";
import { StageProgress, WorkbenchGraph } from "./components/WorkbenchGraph";
import {
  Notice,
  number,
  ScenarioSwitcher,
  Sheet,
  StatusBadge,
} from "./components/ui";
import type { WorkspaceController } from "./components/ui";

const KiCadPanel = lazy(() => import("./components/KiCadPanel").then(module => ({ default: module.KiCadPanel })));

const TABS: { id: TabId; label: string; icon: LucideIcon }[] = [
  { id: "graph", label: "Design graph", icon: GitBranch },
  { id: "scenarios", label: "Scenarios", icon: SlidersHorizontal },
  { id: "catalog", label: "COTS catalog", icon: PackageSearch },
  { id: "assessments", label: "Assessments", icon: ShieldCheck },
];
function OrbitworkLogo() {
  return (
    <span className="brand-logo" aria-hidden="true">
      <svg width="30" height="30" viewBox="0 0 30 30">
        <circle
          cx="15"
          cy="15"
          r="5.5"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
        <ellipse
          cx="15"
          cy="15"
          rx="14"
          ry="8"
          transform="rotate(-42 15 15)"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.4"
        />
        <circle cx="24.2" cy="7" r="2.5" fill="currentColor" />
        <path
          d="M11 15h8M15 11v8"
          stroke="currentColor"
          strokeWidth="1"
          opacity=".65"
        />
      </svg>
    </span>
  );
}
function GraphOverview({
  api,
  onNode,
  onLoad,
  expanded,
  onExpand,
  selected,
}: {
  api: WorkspaceController;
  onNode: (id: NodeId) => void;
  onLoad: () => void;
  expanded: boolean;
  onExpand: () => void;
  selected: NodeId | null;
}) {
  const { analysis, inputs } = api.workspace;
  const blank = inputs.mission.altitudeKm === null && !analysis.orbit;
  const stats: {
    label: string;
    value: number | undefined;
    unit: string;
    icon: LucideIcon;
    node: NodeId;
  }[] = [
    {
      label: "Orbital period",
      value: analysis.orbit ? analysis.orbit.periodS / 60 : undefined,
      unit: "min",
      icon: Orbit,
      node: "orbit",
    },
    {
      label: "Average demand",
      value: analysis.budget?.averageW,
      unit: "W",
      icon: Activity,
      node: "budget",
    },
    {
      label: "Solar minimum",
      value: analysis.solar?.minimumPowerW,
      unit: "W",
      icon: Sun,
      node: "solar",
    },
    {
      label: "Battery required",
      value: analysis.battery?.requiredWh,
      unit: "Wh",
      icon: BatteryCharging,
      node: "battery",
    },
  ];
  return (
    <div className={`graph-page ${expanded ? "graph-is-expanded" : ""}`}>
      <div className="graph-overview">
        <div className="page-intro graph-intro">
          <div>
            <span className="eyebrow">
              ELECTRICAL POWER SYSTEM{" "}
              <span className="eyebrow-separator">/</span> CONCEPT DESIGN
            </span>
            <h1>Every decision, connected.</h1>
            <p>From mission orbit to a power system you can assess.</p>
          </div>
          <div className="design-revision">
            <span className="live-dot" />
            <span>
              Local design<span>EPS calculations run in your browser</span>
            </span>
          </div>
        </div>
        {blank && (
          <div className="reset-welcome">
            <span className="welcome-orbit">
              <Satellite size={27} strokeWidth={1.3} />
            </span>
            <div>
              <strong>Your next mission starts here.</strong>
              <p>
                Define an altitude and lifetime to unlock the first calculation,
                or explore a worked example.
              </p>
            </div>
            <button className="button secondary small" onClick={onLoad}>
              Load example
            </button>
            <button
              className="button primary small"
              onClick={() => onNode("mission")}
            >
              Define mission
              <ArrowRight size={13} />
            </button>
          </div>
        )}
        <div className="key-stats">
          {stats.map((stat) => (
            <button
              className={`key-stat ${api.statuses[stat.node] === "stale" ? "stale" : ""}`}
              key={stat.label}
              onClick={() => onNode(stat.node)}
            >
              <span className="key-stat-label">
                <stat.icon size={13} />
                {stat.label}
                {api.statuses[stat.node] === "stale" && (
                  <span className="stat-stale">Stale</span>
                )}
              </span>
              <strong>
                {number(stat.value)}
                <span>{stat.unit}</span>
              </strong>
              <ChevronRight size={13} className="stat-chevron" />
            </button>
          ))}
        </div>
        <StageProgress statuses={api.statuses} />
      </div>
      <WorkbenchGraph
        workspace={api.workspace}
        statuses={api.statuses}
        missing={api.missing}
        selected={selected}
        onSelect={onNode}
        expanded={expanded}
        onExpand={onExpand}
      />
      <div className="graph-page-bottom">
        <FlaskConical size={13} />
        <span>Preliminary engineering, with assumptions in the open.</span>
        <span className="graph-bottom-shortcut">
          Click a node to edit, run, or inspect evidence.
        </span>
      </div>
    </div>
  );
}
function ScenariosView({
  api,
  onNode,
}: {
  api: WorkspaceController;
  onNode: (id: NodeId) => void;
}) {
  const createScenario = () => {
    const scenario: Scenario = {
      id: `scenario-${crypto.randomUUID()}`,
      name: "New operating case",
      kind: "nominal",
      description: "An engineer-authored mission operating case.",
      revision: 1,
      illuminationFactor: 1,
      initialEnergyFraction: 0.8,
      minimumEnergyFraction: 0.2,
      durationOrbits: 1,
      loads: [],
      provenance:
        "Engineer-authored scenario. Initial defaults are editable demonstration assumptions, not mission requirements.",
    };
    api.updateScenario(scenario);
    api.setActiveScenario(scenario.id);
  };
  return (
    <div className="tab-page scenarios-page">
      <header className="scenario-workspace-header">
        <div className="scenario-view-title">
          <span className="eyebrow">MISSION OPERATING CASES</span>
          <h1>Operating scenarios</h1>
        </div>
        <ScenarioSwitcher api={api} compact />
        <div className="scenario-view-actions">
          <StatusBadge status={api.statuses.scenarios} />
          <button className="button secondary" onClick={createScenario}>
            <Plus size={14} />
            New scenario
          </button>
          <button className="button secondary" onClick={() => onNode("budget")}>
            <Activity size={15} />
            Power budget
          </button>
        </div>
      </header>
      <p className="scenario-basis-note">
        <CircleHelp size={13} />
        <span>
          {api.activeScenario?.id.startsWith("birds4-") ? (
            <>
              BIRDS-4 activities are sourced. Powers, rails, schedules, and
              energy criteria are editable study assumptions.{" "}
              <a href={BIRDS4_SOURCE.url} target="_blank" rel="noreferrer">
                Mission source §§3–5.6 ↗
              </a>
            </>
          ) : (
            "Engineer-authored operating case. Powers, schedules, and energy criteria are explicit assumptions."
          )}
        </span>
      </p>
      {api.statuses.orbit !== "complete" && (
        <Notice kind="warning" title="Orbit timing is not current">
          Load windows use orbit fractions. Evaluate the orbit before relying on
          minute-based timing.
          <button className="text-button" onClick={() => onNode("orbit")}>
            Inspect orbit inputs
            <ArrowRight size={12} />
          </button>
        </Notice>
      )}
      {api.activeScenario ? (
        <div className="scenario-editor-host">
          <ScenarioEditor
            scenario={api.activeScenario}
            orbit={api.workspace.analysis.orbit}
            onChange={api.updateScenario}
          />
        </div>
      ) : (
        <div className="large-empty">
          <SlidersHorizontal size={36} strokeWidth={1.2} />
          <h2>No active scenario</h2>
          <p>
            Create an operating case, then add loads and schedule their active
            windows. Energy criteria remain explicit engineer assumptions.
          </p>
          <button className="button primary" onClick={createScenario}>
            <Plus size={14} />
            Create first scenario
          </button>
        </div>
      )}
      <p className="page-footnote">
        Demonstration scenarios are authored assumptions. Editing a load,
        schedule, or energy criterion marks dependent calculations stale.
      </p>
    </div>
  );
}
export default function App() {
  const api = useWorkspace();
  const [tab, setTab] = useState<TabId>("graph");
  const [selected, setSelected] = useState<NodeId | null>(null);
  const [product, setProduct] = useState<Product | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showKiCad, setShowKiCad] = useState(false);
  const [confirmNew, setConfirmNew] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const openNode = useCallback((id: NodeId) => {
    setSelected(id);
    setProduct(null);
    setShowHelp(false);
    setShowKiCad(false);
    setConfirmNew(false);
  }, []);
  const inspectProduct = useCallback((item: Product) => {
    setProduct(item);
    setShowHelp(false);
    setShowKiCad(false);
    setConfirmNew(false);
  }, []);
  const openKiCad = useCallback(() => {
    setSelected(null); setProduct(null); setShowHelp(false); setConfirmNew(false); setShowKiCad(true);
  }, []);
  const closeNode = useCallback(() => setSelected(null), []);
  const closeProduct = useCallback(() => setProduct(null), []);
  const navigate = useCallback((id: TabId) => {
    setTab(id);
    setSelected(null);
    setProduct(null);
    setShowHelp(false);
    setShowKiCad(false);
    setConfirmNew(false);
  }, []);
  const loadExample = () => {
    api.loadExample();
    navigate("graph");
    setToast(
      "BIRDS-4-inspired example loaded. Numerical schedules and powers are study assumptions.",
    );
  };
  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(null), 6500);
    return () => window.clearTimeout(timeout);
  }, [toast]);
  const runnable = (Object.keys(api.statuses) as NodeId[]).filter(
    (id) =>
      (api.statuses[id] === "ready" || api.statuses[id] === "stale") &&
      canEvaluate(api, id),
  );
  const error = importError ?? api.error;
  return (
    <div className="app-shell">
      <header className="topbar">
        <a
          href="#design"
          className="brand"
          onClick={(e) => {
            e.preventDefault();
            navigate("graph");
          }}
          aria-label="Orbitwork home"
        >
          <OrbitworkLogo />
          <span>
            orbitwork<span className="brand-period">.</span>
          </span>
        </a>
        <span className="topbar-divider" />
        <div className="mission-breadcrumb">
          <span>CubeSat</span>
          <ChevronRight size={12} />
          <strong title={api.workspace.inputs.mission.name}>
            {api.workspace.inputs.mission.name || "Untitled mission"}
          </strong>
          <ChevronRight size={12} />
          <span>EPS design</span>
        </div>
        <span className="local-badge">
          <span className="live-dot" />
          LOCAL DEMO
        </span>
        <div className="topbar-actions">
          <div className="file-actions">
            <button
              className="icon-button"
              aria-label="Import design JSON"
              title="Import design JSON"
              onClick={() => fileInput.current?.click()}
            >
              <ArrowUpFromLine size={16} />
            </button>
            <button
              className="icon-button"
              aria-label="Export design JSON"
              title="Export design JSON"
              onClick={() => {
                api.download();
                setToast(
                  "Design exported as JSON, including inputs, selections, and saved results.",
                );
              }}
            >
              <ArrowDownToLine size={16} />
            </button>
          </div>
          <button
            className="button quiet"
            onClick={() => {
              setSelected(null);
              setProduct(null);
              setShowHelp(false);
              setShowKiCad(false);
              setConfirmNew(true);
            }}
          >
            <Plus size={14} />
            New design
          </button>
          <button
            className="button secondary load-example"
            onClick={loadExample}
          >
            <FolderOpen size={14} />
            Load example
          </button>
          <button
            className="button primary run-all"
            disabled={runnable.length === 0}
            onClick={() => {
              api.runAll();
              setToast(
                "Ready nodes evaluated in dependency order. Inspect the graph for remaining inputs.",
              );
            }}
          >
            <Play size={13} fill="currentColor" />
            Run ready nodes
          </button>
        </div>
        <input
          className="sr-only"
          ref={fileInput}
          type="file"
          accept=".json,application/json"
          aria-label="Import design file"
          tabIndex={-1}
          onChange={async (e) => {
            const file = e.target.files?.[0];
            e.target.value = "";
            if (!file) return;
            setImportError(null);
            api.clearError();
            try {
              await api.restore(file);
              setSelected(null);
              setProduct(null);
              setShowKiCad(false);
            } catch (cause) {
              setImportError(
                cause instanceof Error
                  ? cause.message
                  : "The design could not be imported. Choose a valid Orbitwork JSON file.",
              );
            }
          }}
        />
      </header>
      <div className="workbench">
        <nav className="icon-rail" aria-label="Workbench navigation">
          <div className="rail-spacecraft">
            <Satellite size={21} strokeWidth={1.4} />
          </div>
          {TABS.map((item) => (
            <button
              key={item.id}
              className={`rail-button ${tab === item.id ? "active" : ""}`}
              aria-label={item.label}
              title={item.label}
              aria-current={tab === item.id ? "page" : undefined}
              onClick={() => navigate(item.id)}
            >
              <item.icon size={19} strokeWidth={1.6} />
            </button>
          ))}
          <div className="rail-bottom">
            <button
              className={`rail-button ${showHelp ? "active" : ""}`}
              aria-label="Model scope and help"
              title="Model scope and help"
              onClick={() => {
                setSelected(null);
                setProduct(null);
                setConfirmNew(false);
                setShowKiCad(false);
                setShowHelp(true);
              }}
            >
              <CircleHelp size={19} strokeWidth={1.5} />
            </button>
            <span>v0.1</span>
          </div>
        </nav>
        <main className="main-workspace" id="design">
          <div
            className="workspace-tabs"
            role="tablist"
            aria-label="Design views"
          >
            {TABS.map((item) => (
              <button
                id={`tab-${item.id}`}
                key={item.id}
                role="tab"
                aria-selected={tab === item.id}
                aria-controls={`panel-${item.id}`}
                className={tab === item.id ? "active" : ""}
                onClick={() => navigate(item.id)}
              >
                <item.icon size={15} />
                {item.label}
                {item.id === "catalog" && (
                  <span className="tab-count">{catalog.products.length}</span>
                )}
              </button>
            ))}
            <span className="workspace-label">
              <Layers3 size={12} />
              EPS workbench
            </span>
          </div>
          <div
            className="main-scroll"
            role="tabpanel"
            id={`panel-${tab}`}
            aria-labelledby={`tab-${tab}`}
          >
            {tab === "graph" && (
              <GraphOverview
                api={api}
                onNode={openNode}
                onLoad={loadExample}
                expanded={expanded}
                onExpand={() => setExpanded((value) => !value)}
                selected={selected}
              />
            )}
            {tab === "scenarios" && (
              <ScenariosView api={api} onNode={openNode} />
            )}
            {tab === "catalog" && (
              <CatalogView
                api={api}
                catalog={catalog}
                onInspect={inspectProduct}
                onCandidates={() => openNode("candidates")}
              />
            )}
            {tab === "assessments" && (
              <AssessmentView api={api} onNode={openNode} />
            )}
          </div>
          {product ? (
            <ProductInspector
              key={product.id}
              product={product}
              api={api}
              onClose={closeProduct}
              onCandidates={() => openNode("candidates")}
              onApplied={() =>
                setToast(
                  "Product allocated. Review changed inputs and refresh any stale analyses.",
                )
              }
            />
          ) : selected ? (
            <NodeInspector
              key={selected}
              id={selected}
              api={api}
              catalog={catalog}
              onClose={closeNode}
              onNavigate={navigate}
              onInspect={inspectProduct}
              onNode={openNode}
            />
          ) : null}
          {showKiCad && <Suspense fallback={<Sheet title="KiCad handoff" onClose={() => setShowKiCad(false)}><p className="body-copy">Loading the local exporter…</p></Sheet>}><KiCadPanel workspace={api.workspace} catalog={catalog} onClose={() => setShowKiCad(false)} onNode={openNode} /></Suspense>}
          {showHelp && (
            <Sheet
              title="Engineering with the evidence in view."
              eyebrow="ABOUT THIS WORKSPACE"
              onClose={() => setShowHelp(false)}
            >
              <p className="body-copy">
                Orbitwork is a local proof of concept for preliminary CubeSat
                electrical power system design. It follows the six EPS roles in
                the CubeSat System Reference Model (CSRM).
              </p>
              <section className="inspector-section">
                <h3>A connected workflow</h3>
                <ol className="help-steps">
                  <li>
                    <strong>Define</strong> altitude, lifetime, and scheduled
                    operating cases.
                  </li>
                  <li>
                    <strong>Size</strong> generation and storage using explicit
                    engineering assumptions.
                  </li>
                  <li>
                    <strong>Inspect</strong> sourced commercial products and
                    missing evidence.
                  </li>
                  <li>
                    <strong>Assess</strong> energy histories and parameter-based
                    EPS criteria.
                  </li>
                </ol>
              </section>
              <Notice kind="warning" title="Concept scope only">
                This prototype uses an energy-only simulation. It establishes no
                charge-based state of charge, complete electrical compatibility,
                protection behavior, geometric fit, or flight qualification.
              </Notice>
              <section className="inspector-section">
                <h3>How freshness works</h3>
                <p className="body-copy">
                  A node unlocks when its required inputs and upstream results
                  are current. Edits preserve saved results and mark affected
                  outputs stale. Refresh the dependencies before evaluating a
                  downstream node or applying a product suggestion.
                </p>
                <div className="help-statuses">
                  {(["complete", "ready", "stale", "locked"] as const).map(
                    (status) => (
                      <StatusBadge status={status} key={status} />
                    ),
                  )}
                </div>
              </section>
              <section className="inspector-section">
                <h3>Your design stays local</h3>
                <p className="body-copy">
                  No account or cloud service is required. EPS calculations and
                  offline lexical retrieval run in the browser. Optional semantic
                  retrieval uses a local Qwen service on this computer. Use JSON
                  import and export to save the authored design and its sources.
                  Export before starting a new design.
                </p>
              </section>
              <section className="inspector-section">
                <h3>Method & sources</h3>
                <p className="body-copy">
                  The design proposal grounds the circular orbit, preliminary
                  sizing equations, CSRM component roles, and EPS-01–20
                  criteria. Orbit and sizing follow El Hachimi et al., Sections
                  2–3. Each catalog property retains its manufacturer source,
                  revision, location, meaning, and conditions.
                </p>
              </section>
            </Sheet>
          )}
          {confirmNew && (
            <Sheet
              title="Start a new design?"
              eyebrow="LOCAL WORKSPACE"
              onClose={() => setConfirmNew(false)}
              footer={
                <div className="confirm-actions">
                  <button
                    className="button secondary"
                    onClick={() => setConfirmNew(false)}
                  >
                    Keep current design
                  </button>
                  <button
                    className="button primary"
                    onClick={() => {
                      api.reset();
                      navigate("graph");
                      setToast(
                        "New design created. Define the mission to begin.",
                      );
                    }}
                  >
                    <FilePlus2 size={15} />
                    Create new design
                  </button>
                </div>
              }
            >
              <div className="new-design-illustration">
                <OrbitworkLogo />
              </div>
              <p className="body-copy">
                Your current local workspace will be replaced. Export the
                current design first if you want to keep its inputs,
                allocations, and results.
              </p>
              <button
                className="button secondary full-width"
                onClick={api.download}
              >
                <ArrowDownToLine size={15} />
                Export current design
              </button>
              <Notice>
                The new workspace begins with an unsized reference architecture.
                Missing inputs remain explicit.
              </Notice>
            </Sheet>
          )}
        </main>
        <Architecture
          workspace={api.workspace}
          statuses={api.statuses}
          catalog={catalog}
          onInspect={inspectProduct}
          onNode={openNode}
          onKiCad={openKiCad}
        />
      </div>
      {error && (
        <div className="app-notification error" role="alert">
          <CircleHelp size={18} />
          <div>
            <strong>We couldn't complete that action.</strong>
            <p>{error}</p>
          </div>
          <button
            className="icon-button"
            aria-label="Dismiss error"
            onClick={() => {
              setImportError(null);
              api.clearError();
            }}
          >
            <X size={16} />
          </button>
        </div>
      )}
      {toast && !error && (
        <div className="app-notification" role="status">
          <CheckCircle2 size={17} />
          <span>{toast}</span>
          <button
            className="icon-button"
            aria-label="Dismiss notification"
            onClick={() => setToast(null)}
          >
            <X size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
