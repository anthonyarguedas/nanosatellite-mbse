import { useState } from "react";
import {
  ArrowUpRight,
  BatteryCharging,
  Box,
  Boxes,
  ChevronRight,
  CircleHelp,
  CircuitBoard,
  Code2,
  Cpu,
  GitBranch,
  Layers3,
  List,
  ShieldAlert,
  Sun,
  Workflow,
  Zap,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type {
  Catalog,
  NodeId,
  NodeStatus,
  Product,
  Role,
  Workspace,
} from "../types";
import { number, ROLES, ROLE_NAMES } from "./ui";

const ROLE_ICONS: Record<Role, LucideIcon> = {
  solar: Sun,
  battery: BatteryCharging,
  conditioning: Zap,
  distribution: GitBranch,
  processor: Cpu,
  software: Code2,
};
const ROLE_NODES: Record<Role, NodeId> = {
  solar: "solar",
  battery: "battery",
  conditioning: "topology",
  distribution: "topology",
  processor: "candidates",
  software: "candidates",
};
function logicalValue(role: Role, w: Workspace): string {
  const { analysis: a, inputs: i } = w;
  switch (role) {
    case "solar":
      return a.solar
        ? `${number(a.solar.minimumPowerW)} W min. · ${i.solar.installedPowerW === null ? `${a.solar.cellCount} cells min.` : `${number(i.solar.installedPowerW)} W installed`}`
        : "Generation not sized";
    case "battery":
      return a.battery
        ? `${number(a.battery.requiredWh)} Wh req. · ${i.battery.capacityWh === null ? "capacity undefined" : `${number(i.battery.capacityWh)} Wh BOL`}`
        : "Storage not sized";
    case "conditioning":
      return `${i.topology.conditioning} · ${i.topology.bus} bus`;
    case "distribution":
      return `${i.topology.distribution[0].toUpperCase()}${i.topology.distribution.slice(1)} transfer`;
    case "processor":
      return w.selections.processor
        ? "Host allocated · resources unassessed"
        : "Host & memory not allocated";
    case "software":
      return w.selections.software
        ? "Software allocated · host unassessed"
        : "Services & timing unassessed";
  }
}
export function Architecture({
  workspace,
  statuses,
  catalog,
  onInspect,
  onNode,
  onKiCad,
}: {
  workspace: Workspace;
  statuses: Record<NodeId, NodeStatus>;
  catalog: Catalog;
  onInspect: (product: Product) => void;
  onNode: (id: NodeId) => void;
  onKiCad?: () => void;
}) {
  const [view, setView] = useState<"structure" | "bom">("structure");
  const ids = [
    ...new Set(
      Object.values(workspace.selections).filter((id): id is string =>
        Boolean(id),
      ),
    ),
  ];
  const usages = ids.map((id, index) => ({
    product: catalog.products.find((p) => p.id === id),
    id,
    ref: `U${String(index + 1).padStart(2, "0")}`,
    roles: ROLES.filter((role) => workspace.selections[role] === id),
    quantity: Math.max(
      1,
      workspace.analysis.suggestions?.find(
        (s) => s.productId === id && s.outcome !== "rejected",
      )?.quantity ?? 1,
    ),
  }));
  const allocated = ROLES.filter((role) =>
    Boolean(workspace.selections[role]),
  ).length;
  const hasSizing = Boolean(
    workspace.analysis.solar || workspace.analysis.battery,
  );
  const massKnown = usages.reduce((sum, usage) => {
    const spec = usage.product?.specs.massKg;
    return (
      sum +
      (spec?.status === "available" && typeof spec.value === "number"
        ? spec.value * usage.quantity
        : 0)
    );
  }, 0);
  const missingMass = usages.filter(
    (usage) =>
      usage.product?.specs.massKg?.status !== "available" ||
      typeof usage.product?.specs.massKg?.value !== "number",
  ).length;
  const stale = ["solar", "battery", "topology", "candidates"].some(
    (id) => statuses[id as NodeId] === "stale",
  );
  return (
    <aside
      className="architecture-pane"
      aria-label="Persistent EPS architecture"
    >
      <header className="architecture-header">
        <div className="architecture-title">
          <span className="architecture-mark">
            <Layers3 size={18} />
          </span>
          <div>
            <span className="eyebrow">LIVE MODEL</span>
            <h2>EPS architecture</h2>
          </div>
          <span className="subtle-pill">CSRM</span>
        </div>
        <p>From reference roles to a physical system.</p>
        <div className="architecture-evolution">
          <span className="done">
            <i />
            Reference
          </span>
          <span className={hasSizing ? "done" : ""}>
            <i />
            Sized
          </span>
          <span className={ids.length ? "done" : ""}>
            <i />
            COTS
          </span>
        </div>
        <div
          className="architecture-view"
          role="group"
          aria-label="Architecture view"
        >
          <button
            onClick={() => setView("structure")}
            className={view === "structure" ? "active" : ""}
          >
            <Workflow size={13} />
            Structure<span>6</span>
          </button>
          <button
            onClick={() => setView("bom")}
            className={view === "bom" ? "active" : ""}
          >
            <List size={13} />
            Bill of materials<span>{ids.length}</span>
          </button>
        </div>
      </header>
      <div className="architecture-body">
        {stale && (
          <div className="architecture-stale">
            <ShieldAlert size={13} />
            Saved allocations or sizing may be out of date.
          </div>
        )}
        {view === "structure" ? (
          <>
            <div className="architecture-root">
              <span>
                <Box size={15} />
                Power Subsystem
              </span>
              <span>6 logical roles</span>
            </div>
            <div className="role-tree">
              {ROLES.map((role, index) => {
                const Icon = ROLE_ICONS[role];
                const usage = usages.find(
                  (u) => u.id === workspace.selections[role],
                );
                const product = usage?.product;
                const node = ROLE_NODES[role];
                const isStale = statuses[node] === "stale";
                const sized =
                  role === "solar"
                    ? Boolean(workspace.analysis.solar)
                    : role === "battery"
                      ? Boolean(workspace.analysis.battery)
                      : (role === "conditioning" || role === "distribution") &&
                        statuses.topology === "complete";
                return (
                  <button
                    key={role}
                    className={`architecture-role ${product ? "allocated" : ""} ${isStale ? "stale" : ""}`}
                    onClick={() =>
                      product ? onInspect(product) : onNode(node)
                    }
                    title={
                      product
                        ? `Inspect ${product.name}`
                        : `Inspect ${ROLE_NAMES[role]}`
                    }
                  >
                    <div className="role-heading">
                      <span className={`role-icon ${role}`}>
                        <Icon size={15} />
                      </span>
                      <strong>{ROLE_NAMES[role]}</strong>
                      <ChevronRight size={12} />
                    </div>
                    <div className="role-value">
                      {logicalValue(role, workspace)}
                    </div>
                    {product ? (
                      <div className="role-allocation">
                        <span className="usage-ref">{usage?.ref}</span>
                        <span>{product.name}</span>
                        {usage && usage.roles.length > 1 && (
                          <Boxes size={12} aria-label="Shared physical usage" />
                        )}
                      </div>
                    ) : (
                      <div className="role-state">
                        <i
                          className={isStale ? "stale" : sized ? "sized" : ""}
                        />
                        {isStale
                          ? "Stale logical result"
                          : sized
                            ? "Sized logical model"
                            : "Reference placeholder"}
                        <span className="role-index">0{index + 1}</span>
                      </div>
                    )}
                    {product && usage && usage.roles.length > 1 && (
                      <small className="shared-usage">
                        Same physical usage across {usage.roles.length} roles
                      </small>
                    )}
                  </button>
                );
              })}
            </div>
            <div className="architecture-explainer">
              <CircleHelp size={13} />
              <span>
                Composition and role allocations only. Connections and
                protection are unassessed.
              </span>
            </div>
          </>
        ) : (
          <div className="bom-view">
            <div className="section-heading">
              <h3>Unique physical usages</h3>
              <span>{usages.length}</span>
            </div>
            {usages.length === 0 ? (
              <div className="architecture-empty">
                <Boxes size={30} strokeWidth={1.2} />
                <h3>No hardware allocated yet</h3>
                <p>
                  Run COTS candidates, inspect the evidence, then apply a
                  suggestion.
                </p>
                <button
                  className="button secondary small"
                  onClick={() => onNode("candidates")}
                >
                  Explore candidates
                  <ArrowUpRight size={13} />
                </button>
              </div>
            ) : (
              usages.map((usage) => (
                <button
                  className="bom-item"
                  key={usage.id}
                  onClick={() => usage.product && onInspect(usage.product)}
                >
                  <div>
                    <span className="usage-ref">{usage.ref}</span>
                    <strong>{usage.product?.name ?? usage.id}</strong>
                    <span className="bom-quantity">×{usage.quantity}</span>
                  </div>
                  <small>
                    {usage.product?.manufacturer ?? "Catalog entry unavailable"}
                  </small>
                  <p>
                    {usage.roles.map((role) => ROLE_NAMES[role]).join(" · ")}
                  </p>
                  <div className="bom-mass">
                    {typeof usage.product?.specs.massKg?.value === "number"
                      ? `${number(usage.product.specs.massKg.value * usage.quantity, 3)} kg`
                      : "Mass not published"}
                    <span>Counted once</span>
                  </div>
                </button>
              ))
            )}
            <div className="bom-accounting">
              <strong>Accounting boundary</strong>
              <p>
                An integrated board is one physical usage, even when allocated
                to several logical roles. Software resources belong to its host.
                Harnesses and installation items remain unallocated.
              </p>
            </div>
          </div>
        )}
      </div>
      <footer className="architecture-footer">
        <div className="architecture-totals">
          <div>
            <small>Roles allocated</small>
            <strong>
              {allocated}
              <span> / 6</span>
            </strong>
          </div>
          <div>
            <small>Known product mass</small>
            <strong>
              {usages.length ? number(massKnown, 3) : "—"}
              <span> kg</span>
            </strong>
          </div>
        </div>
        {usages.length > 0 && (
          <div className="mass-disclosure">
            {missingMass
              ? `${missingMass} usage${missingMass === 1 ? "" : "s"} missing mass. Partial total only.`
              : "Catalog mass only. Integration items excluded."}
          </div>
        )}
        {onKiCad && <button className="button secondary architecture-export" aria-label="Open KiCad handoff" onClick={onKiCad}><CircuitBoard size={15} />KiCad review & design rules<ArrowUpRight size={12} /></button>}
        <div className="preliminary-note">
          <ShieldAlert size={14} />
          <span>
            Preliminary only
            <span>Not flight qualification or wiring assurance.</span>
          </span>
        </div>
      </footer>
    </aside>
  );
}
