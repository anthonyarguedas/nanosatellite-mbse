import { useMemo } from "react";
import {
  Background,
  BackgroundVariant,
  BaseEdge,
  EdgeText,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  ReactFlowProvider,
  getSmoothStepPath,
  useReactFlow,
} from "@xyflow/react";
import type { Edge, EdgeProps, Node, NodeProps } from "@xyflow/react";
import {
  Activity,
  BatteryCharging,
  Check,
  ChevronRight,
  CircleHelp,
  Clock3,
  Expand,
  Gauge,
  GitBranch,
  LockKeyhole,
  Maximize2,
  Minus,
  Orbit,
  Plus,
  ScanSearch,
  Settings2,
  ShieldCheck,
  SlidersHorizontal,
  Sun,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { NodeDefinition, NodeId, NodeStatus, Workspace } from "../types";
import { NODE_DEFINITIONS } from "../workflow";
import { engineeringExchange, exchangeValue } from "./engineering-exchanges";
import { number, StatusBadge } from "./ui";

const ICONS: Record<NodeId, LucideIcon> = {
  mission: Orbit,
  orbit: Gauge,
  scenarios: SlidersHorizontal,
  budget: Activity,
  solar: Sun,
  battery: BatteryCharging,
  topology: GitBranch,
  candidates: ScanSearch,
  simulation: Activity,
  assessment: ShieldCheck,
};
const POSITIONS: Record<NodeId, { x: number; y: number }> = {
  mission: { x: 0, y: 16 },
  orbit: { x: 260, y: 16 },
  scenarios: { x: 0, y: 200 },
  budget: { x: 260, y: 200 },
  solar: { x: 520, y: 16 },
  battery: { x: 520, y: 200 },
  topology: { x: 780, y: 16 },
  candidates: { x: 780, y: 200 },
  simulation: { x: 520, y: 384 },
  assessment: { x: 780, y: 384 },
};
const FIT_PADDING = {
  top: "12px",
  bottom: "32px",
  left: "20px",
  right: "20px",
} as const;
const CALCULATED = new Set<NodeId>([
  "orbit",
  "budget",
  "solar",
  "battery",
  "candidates",
  "simulation",
  "assessment",
]);
type CardData = {
  definition: NodeDefinition;
  status: NodeStatus;
  value: string;
  caption: string;
  missing: string[];
  selected: boolean;
  onSelect: (id: NodeId) => void;
};
type CardNode = Node<CardData, "workflow">;
function WorkflowCard({ data }: NodeProps<CardNode>) {
  const Icon = ICONS[data.definition.id];
  const historical =
    data.status === "stale" && CALCULATED.has(data.definition.id);
  return (
    <div
      className={`workflow-node ${data.status} ${data.selected ? "is-selected" : ""}`}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          data.onSelect(data.definition.id);
        }
      }}
      aria-label={`${data.definition.title}: ${historical ? "historical output, " : ""}${data.value}. ${data.status === "locked" ? data.missing.join(" ") : "Open inputs, results, and parameter trace."}`}
      title={
        data.status === "locked"
          ? data.missing.join("\n")
          : historical
            ? "Historical calculation. Recompute before downstream use."
            : "Current means calculation freshness, not requirement verification."
      }
    >
      <Handle type="target" position={Position.Left} id="in-left" />
      <Handle type="target" position={Position.Top} id="in-top" />
      <Handle type="target" position={Position.Right} id="in-right" />
      <Handle type="target" position={Position.Bottom} id="in-bottom" />
      <div className="node-top">
        <span className={`node-icon ${data.definition.id}`}>
          <Icon size={17} strokeWidth={1.7} />
        </span>
        <span className="node-step">
          {String(
            NODE_DEFINITIONS.findIndex((n) => n.id === data.definition.id) + 1,
          ).padStart(2, "0")}
        </span>
        {data.status === "stale" && (
          <span className="node-history-label">
            {historical ? "Historical" : "Edited inputs"}
          </span>
        )}
        {data.status === "complete" ? (
          <Check className="node-state-icon complete" size={14} />
        ) : data.status === "locked" ? (
          <LockKeyhole className="node-state-icon" size={12} />
        ) : data.status === "ready" ? (
          <span className="ready-indicator" />
        ) : (
          <Clock3 className="node-state-icon stale" size={13} />
        )}
      </div>
      <h3>{data.definition.title}</h3>
      <div className="node-value" title={data.value}>
        {historical && <span className="saved-value-prefix">Saved · </span>}
        {data.value}
      </div>
      <div className="node-bottom">
        <StatusBadge status={data.status} small />
        {data.definition.requirements.length ? (
          <span
            className="node-req"
            title={`Associated requirements, not verification: ${data.definition.requirements.join(", ")}`}
          >
            {data.definition.requirements[0]}
            {data.definition.requirements.length > 1
              ? ` +${data.definition.requirements.length - 1}`
              : ""}
          </span>
        ) : (
          <span className="node-caption">{data.caption}</span>
        )}
      </div>
      <Handle type="source" position={Position.Right} id="out-right" />
      <Handle type="source" position={Position.Bottom} id="out-bottom" />
      <Handle type="source" position={Position.Left} id="out-left" />
      <Handle type="source" position={Position.Top} id="out-top" />
    </div>
  );
}
const NODE_TYPES = { workflow: WorkflowCard };
function nodeSummary(id: NodeId, w: Workspace): [string, string] {
  const { inputs: i, analysis: a } = w;
  switch (id) {
    case "mission":
      return [
        i.mission.altitudeKm == null
          ? "Set altitude & lifetime"
          : `${number(i.mission.altitudeKm, 0)} km · ${number(i.mission.lifetimeYears, 1)} yr`,
        "Mission inputs",
      ];
    case "orbit":
      return [
        a.orbit
          ? `${number(a.orbit.periodS / 60)} min / orbit`
          : "Awaiting mission inputs",
        "Circular reference",
      ];
    case "scenarios":
      return [
        i.scenarios.find((s) => s.id === i.activeScenarioId)?.name ??
          "Create a load scenario",
        `${i.scenarios.length} cases`,
      ];
    case "budget":
      return [
        a.budget
          ? `${number(a.budget.averageW, 2)} W avg · ${number(a.budget.peakW, 2)} W peak`
          : "Integrate scheduled demand",
        "Load boundary",
      ];
    case "solar":
      return [
        a.solar
          ? `${number(a.solar.minimumPowerW, 2)} W · ${a.solar.cellCount} cells min.`
          : "Calculate EOL generation",
        "Generation",
      ];
    case "battery":
      return [
        a.battery
          ? `${number(a.battery.requiredWh, 2)} Wh required`
          : "Size for eclipse demand",
        "Energy storage",
      ];
    case "topology":
      return [
        `${i.topology.conditioning} · ${i.topology.bus} bus`,
        "Power paths",
      ];
    case "candidates":
      return [
        a.suggestions
          ? `${a.suggestions.filter((s) => s.outcome !== "rejected").length} preliminary options`
          : "Screen sourced COTS options",
        "Catalog evidence",
      ];
    case "simulation":
      return [
        a.simulation
          ? `${number(a.simulation.minEnergyWh, 2)} Wh minimum energy`
          : "Inspect the energy timeline",
        "Energy-only model",
      ];
    case "assessment":
      return [
        a.checks
          ? `${a.checks.filter((c) => c.verdict === "fail").length} fail · ${a.checks.filter((c) => c.verdict === "unassessed").length} unassessed`
          : "Return scoped findings",
        "Concept assessment",
      ];
  }
}

type Point = { x: number; y: number };
type ExchangeData = {
  label: string;
  description: string;
  value: string;
  historical: boolean;
  principal: boolean;
  feedback?: boolean;
  routeKey: string;
};
type InformationEdgeType = Edge<ExchangeData, "information">;
function roundedPath(points: Point[]) {
  let path = `M ${points[0].x},${points[0].y}`;
  for (let i = 1; i < points.length - 1; i++) {
    const before = points[i - 1],
      at = points[i],
      after = points[i + 1];
    const incoming = Math.hypot(at.x - before.x, at.y - before.y),
      outgoing = Math.hypot(after.x - at.x, after.y - at.y);
    const radius = Math.min(15, incoming / 2, outgoing / 2);
    if (!incoming || !outgoing) continue;
    const a = {
      x: at.x + ((before.x - at.x) / incoming) * radius,
      y: at.y + ((before.y - at.y) / incoming) * radius,
    };
    const b = {
      x: at.x + ((after.x - at.x) / outgoing) * radius,
      y: at.y + ((after.y - at.y) / outgoing) * radius,
    };
    path += ` L ${a.x},${a.y} Q ${at.x},${at.y} ${b.x},${b.y}`;
  }
  return `${path} L ${points.at(-1)!.x},${points.at(-1)!.y}`;
}
function InformationEdge(props: EdgeProps<InformationEdgeType>) {
  const { sourceX: sx, sourceY: sy, targetX: tx, targetY: ty, data } = props;
  const [defaultPath, defaultX, defaultY] = getSmoothStepPath({
    sourceX: sx,
    sourceY: sy,
    targetX: tx,
    targetY: ty,
    sourcePosition: props.sourcePosition,
    targetPosition: props.targetPosition,
    borderRadius: 18,
    offset: 14,
  });
  let path = defaultPath,
    labelX = defaultX,
    labelY = defaultY;
  const route = (points: Point[], label?: Point) => {
    path = roundedPath([{ x: sx, y: sy }, ...points, { x: tx, y: ty }]);
    if (label) {
      labelX = label.x;
      labelY = label.y;
    }
  };
  switch (data?.routeKey) {
    case "mission:battery":
      route(
        [
          { x: sx, y: 174 },
          { x: tx, y: 174 },
        ],
        { x: 173, y: 174 },
      );
      break;
    case "budget:solar":
      route(
        [
          { x: sx, y: 174 },
          { x: 488, y: 174 },
          { x: 488, y: ty },
        ],
        { x: 488, y: 119 },
      );
      break;
    case "battery:topology":
      route(
        [
          { x: sx, y: 174 },
          { x: tx, y: 174 },
        ],
        { x: 743, y: 174 },
      );
      break;
    case "candidates:simulation":
      route(
        [
          { x: 748, y: sy },
          { x: 748, y: 356 },
          { x: tx, y: 356 },
        ],
        { x: 655, y: 356 },
      );
      break;
    case "orbit:simulation":
      route([
        { x: sx, y: 160 },
        { x: 474, y: 160 },
        { x: 474, y: 348 },
        { x: tx, y: 348 },
      ]);
      break;
    case "solar:simulation":
      route([
        { x: 500, y: sy },
        { x: 500, y: 356 },
        { x: tx, y: 356 },
      ]);
      break;
    case "topology:simulation":
      route([
        { x: 738, y: sy },
        { x: 738, y: 342 },
        { x: tx, y: 342 },
      ]);
      break;
    case "solar:candidates":
      route([
        { x: sx, y: 160 },
        { x: 730, y: 160 },
        { x: 730, y: ty },
      ]);
      break;
    case "returned-findings":
      route(
        [
          { x: sx, y: 530 },
          { x: tx, y: 530 },
        ],
        { x: 460, y: 530 },
      );
      break;
  }
  return (
    <g>
      <title>{`${data?.historical ? "Historical exchange. " : ""}${data?.description} ${data?.value}`}</title>
      <BaseEdge
        id={props.id}
        path={path}
        markerEnd={props.markerEnd}
        style={props.style}
        interactionWidth={18}
      />
      {data?.principal && (
        <EdgeText
          x={labelX}
          y={labelY}
          label={`${data.historical && !data.feedback ? "↺ " : ""}${data.label}`}
          labelStyle={{
            fontSize: 11.5,
            fontFamily: "var(--font-ui)",
            fontWeight: 500,
            fill: data.historical || data.feedback ? "#d3b17a" : "#b1c0cb",
          }}
          labelBgStyle={{
            fill: data.feedback ? "#27251e" : "#171e26",
            fillOpacity: 0.98,
            stroke: data.feedback ? "#695539" : "#34404c",
            strokeWidth: 0.7,
          }}
          labelBgPadding={[5, 3]}
          labelBgBorderRadius={4}
        />
      )}
    </g>
  );
}
const EDGE_TYPES = { information: InformationEdge };
const HANDLES: Partial<Record<string, [string, string]>> = {
  "mission:battery": ["out-bottom", "in-top"],
  "budget:solar": ["out-top", "in-left"],
  "battery:topology": ["out-top", "in-bottom"],
  "candidates:simulation": ["out-left", "in-top"],
  "orbit:simulation": ["out-bottom", "in-top"],
  "solar:simulation": ["out-left", "in-top"],
  "topology:simulation": ["out-left", "in-top"],
  "solar:candidates": ["out-bottom", "in-left"],
  "scenarios:simulation": ["out-bottom", "in-left"],
};
function GraphControls({
  expanded,
  onExpand,
}: {
  expanded: boolean;
  onExpand: () => void;
}) {
  const flow = useReactFlow();
  return (
    <div className="graph-controls">
      <button
        aria-label="Zoom out"
        title="Zoom out"
        onClick={() => flow.zoomOut({ duration: 180 })}
      >
        <Minus size={15} />
      </button>
      <button
        aria-label="Zoom in"
        title="Zoom in"
        onClick={() => flow.zoomIn({ duration: 180 })}
      >
        <Plus size={15} />
      </button>
      <span />
      <button
        onClick={() => flow.fitView({ padding: FIT_PADDING, duration: 300 })}
        title="Fit all nodes"
      >
        <Maximize2 size={14} />
        Fit
      </button>
      <span />
      <button
        aria-label={expanded ? "Exit expanded graph" : "Expand graph"}
        title={expanded ? "Exit expanded graph" : "Expand graph"}
        onClick={onExpand}
      >
        <Expand size={14} />
      </button>
    </div>
  );
}
export function WorkbenchGraph({
  workspace,
  statuses,
  missing,
  selected,
  onSelect,
  expanded,
  onExpand,
}: {
  workspace: Workspace;
  statuses: Record<NodeId, NodeStatus>;
  missing: Record<NodeId, string[]>;
  selected: NodeId | null;
  onSelect: (id: NodeId) => void;
  expanded: boolean;
  onExpand: () => void;
}) {
  const nodes = useMemo<CardNode[]>(
    () =>
      NODE_DEFINITIONS.map((definition) => {
        const [value, caption] = nodeSummary(definition.id, workspace);
        return {
          id: definition.id,
          type: "workflow",
          position: POSITIONS[definition.id],
          data: {
            definition,
            status: statuses[definition.id],
            value,
            caption,
            missing: missing[definition.id] ?? [],
            selected: selected === definition.id,
            onSelect,
          },
          draggable: false,
          selectable: false,
        };
      }),
    [workspace, statuses, missing, selected, onSelect],
  );
  const edges = useMemo<InformationEdgeType[]>(() => {
    const forward: InformationEdgeType[] = NODE_DEFINITIONS.flatMap(
      (definition) =>
        definition.dependencies.map((dependency) => {
          const exchange = engineeringExchange(dependency, definition.id),
            key = `${dependency}:${definition.id}`;
          const vertical =
            POSITIONS[dependency].x === POSITIONS[definition.id].x;
          const [sourceHandle, targetHandle] =
            HANDLES[key] ??
            (vertical ? ["out-bottom", "in-top"] : ["out-right", "in-left"]);
          const current = statuses[dependency] === "complete",
            historical =
              statuses[dependency] === "stale" && CALCULATED.has(dependency);
          const outOfDate =
            statuses[dependency] === "stale" ||
            statuses[definition.id] === "stale";
          const color = outOfDate ? "#ad8b53" : current ? "#638a7c" : "#455160";
          return {
            id: key,
            source: dependency,
            target: definition.id,
            sourceHandle,
            targetHandle,
            type: "information" as const,
            data: {
              ...exchange,
              principal: Boolean(exchange.principal),
              value: exchangeValue(dependency, definition.id, workspace),
              historical,
              routeKey: key,
            },
            ariaLabel: `${NODE_DEFINITIONS.find((n) => n.id === dependency)?.title} to ${definition.title}: ${exchange.description}`,
            zIndex: exchange.principal ? 1 : 0,
            animated:
              Boolean(exchange.principal) &&
              current &&
              statuses[definition.id] === "ready",
            style: {
              stroke: color,
              strokeWidth: exchange.principal ? 1.5 : 1,
              strokeDasharray: current && !outOfDate ? undefined : "5 5",
              opacity: exchange.principal ? 0.85 : 0.32,
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              width: 12,
              height: 12,
              color,
            },
          };
        }),
    );
    if (workspace.analysis.checks?.length) {
      const failed = workspace.analysis.checks.filter(
          (c) => c.verdict === "fail",
        ).length,
        unknown = workspace.analysis.checks.filter(
          (c) => c.verdict === "unassessed",
        ).length;
      const historical = statuses.assessment !== "complete";
      forward.push({
        id: "returned-findings",
        source: "assessment",
        target: "budget",
        sourceHandle: "out-bottom",
        targetHandle: "in-bottom",
        type: "information",
        data: {
          label: `${historical ? "Historical findings" : "Returned findings"} · ${failed} fail / ${unknown} gaps`,
          description:
            "Requirement findings return to the engineering inputs for investigation. This is not an evaluation dependency or review authorization.",
          value: exchangeValue("assessment", "budget", workspace),
          historical,
          principal: true,
          feedback: true,
          routeKey: "returned-findings",
        },
        zIndex: 2,
        ariaLabel: "Returned engineering findings. Inspect requirement review.",
        style: {
          stroke: "#b59b6d",
          strokeWidth: 1.4,
          strokeDasharray: "2 5",
          opacity: 0.9,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 12,
          height: 12,
          color: "#b59b6d",
        },
        animated: false,
      });
    }
    return forward;
  }, [statuses, workspace]);
  const ready = Object.values(statuses).filter((s) => s === "ready").length,
    complete = Object.values(statuses).filter((s) => s === "complete").length,
    stale = Object.values(statuses).filter((s) => s === "stale").length;
  return (
    <section className="graph-panel" aria-label="Design dependency graph">
      <div className="graph-panel-header">
        <div>
          <GitBranch size={14} />
          <strong>Engineering information flow</strong>
          <span className="subtle-pill">10 activities</span>
        </div>
        <span className={`graph-hint ${stale ? "historical" : ""}`}>
          <CircleHelp size={13} />
          {stale
            ? `${stale} activities out of date · saved values are historical`
            : "Select an activity for inputs, equations, and evidence"}
        </span>
      </div>
      <div className="graph-canvas">
        <div className="graph-surface">
          <ReactFlowProvider>
            <ReactFlow<CardNode, InformationEdgeType>
              nodes={nodes}
              edges={edges}
              nodeTypes={NODE_TYPES}
              edgeTypes={EDGE_TYPES}
              fitView
              fitViewOptions={{ padding: FIT_PADDING }}
              minZoom={0.35}
              maxZoom={1.5}
              nodesDraggable={false}
              nodesConnectable={false}
              elementsSelectable={false}
              onNodeClick={(_, node) => onSelect(node.id as NodeId)}
              onEdgeClick={(_, edge) =>
                onSelect(
                  edge.data?.feedback ? "assessment" : (edge.target as NodeId),
                )
              }
              panOnScroll
              zoomOnScroll
              preventScrolling={false}
              colorMode="dark"
            >
              <Background
                variant={BackgroundVariant.Dots}
                gap={18}
                size={0.8}
                color="#3a414c"
              />
              <GraphControls expanded={expanded} onExpand={onExpand} />
              <div className="graph-legend">
                <span>
                  <i className="complete" />
                  Current
                </span>
                <span>
                  <i className="ready" />
                  Ready
                </span>
                <span>
                  <i className="locked" />
                  Missing
                </span>
                <span>
                  <i className="stale" />
                  Historical
                </span>
                <small>Dotted return = findings</small>
              </div>
            </ReactFlow>
          </ReactFlowProvider>
        </div>
      </div>
      <footer className="graph-panel-footer">
        <span>
          <i className="live-dot" />
          {complete} current<span className="separator">/</span>
          {ready} ready
        </span>
        <span>
          Current = calculation freshness, not requirement verification.
        </span>
      </footer>
    </section>
  );
}
export function StageProgress({
  statuses,
}: {
  statuses: Record<NodeId, NodeStatus>;
}) {
  const stages = [
    {
      label: "Define mission",
      icon: Orbit,
      ids: ["mission", "orbit", "scenarios"] as NodeId[],
    },
    {
      label: "Size the system",
      icon: Settings2,
      ids: ["budget", "solar", "battery", "topology"] as NodeId[],
    },
    {
      label: "Screen hardware",
      icon: ScanSearch,
      ids: ["candidates"] as NodeId[],
    },
    {
      label: "Assess the design",
      icon: ShieldCheck,
      ids: ["simulation", "assessment"] as NodeId[],
    },
  ];
  const firstIncomplete = stages.findIndex(
    (stage) => !stage.ids.every((id) => statuses[id] === "complete"),
  );
  return (
    <div className="stage-progress" aria-label="Design stages">
      {stages.map((stage, index) => {
        const done = stage.ids.every((id) => statuses[id] === "complete");
        const Icon = done ? Check : stage.icon;
        return (
          <div
            key={stage.label}
            className={`stage ${done ? "done" : ""} ${index === firstIncomplete ? "active" : ""}`}
          >
            <span className="stage-number">
              <Icon size={14} />
            </span>
            <div>
              <small>0{index + 1}</small>
              <strong>{stage.label}</strong>
            </div>
            {index < stages.length - 1 && (
              <ChevronRight className="stage-arrow" size={14} />
            )}
          </div>
        );
      })}
    </div>
  );
}
