import { useEffect, useId, useRef, useState } from "react";
import type { ReactNode } from "react";
import {
  AlertCircle,
  ArrowLeft,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  LockKeyhole,
  X,
  XCircle,
} from "lucide-react";
import type {
  Check as DesignCheck,
  DesignInputs,
  NodeId,
  NodeStatus,
  Role,
  Scenario,
  Workspace,
} from "../types";

export interface WorkspaceController {
  workspace: Workspace;
  statuses: Record<NodeId, NodeStatus>;
  missing: Record<NodeId, string[]>;
  activeScenario: Scenario | undefined;
  runNode: (id: NodeId) => void;
  runAll: () => void;
  updateInputs: (
    node: NodeId,
    updater: (inputs: DesignInputs) => DesignInputs,
  ) => void;
  updateScenario: (scenario: Scenario) => void;
  setActiveScenario: (id: string) => void;
  selectProduct: (role: Role, productId: string) => void;
  loadExample: () => void;
  reset: () => void;
  download: () => void;
  restore: (file: File) => Promise<void>;
  error: string | null;
  clearError: () => void;
}

export const ROLE_NAMES: Record<Role, string> = {
  solar: "Solar Arrays",
  battery: "Batteries",
  conditioning: "Regulators & Converters",
  distribution: "Power Circuits & Switches",
  processor: "Processor & Memory",
  software: "Software",
};
export const ROLES: Role[] = [
  "solar",
  "battery",
  "conditioning",
  "distribution",
  "processor",
  "software",
];
export const STATUS_LABELS: Record<NodeStatus, string> = {
  complete: "Current",
  ready: "Ready to run",
  stale: "Out of date",
  locked: "Needs inputs",
};
export function number(value: number | null | undefined, digits = 1): string {
  return value == null || !Number.isFinite(value)
    ? "—"
    : value.toLocaleString("en-US", {
        maximumFractionDigits: digits,
        minimumFractionDigits: digits,
      });
}
export function unit(
  value: number | null | undefined,
  suffix: string,
  digits = 1,
): string {
  return value == null || !Number.isFinite(value)
    ? "Not yet defined"
    : `${number(value, digits)} ${suffix}`;
}
export function StatusBadge({
  status,
  small = false,
}: {
  status: NodeStatus;
  small?: boolean;
}) {
  const Icon =
    status === "complete"
      ? Check
      : status === "locked"
        ? LockKeyhole
        : status === "stale"
          ? Clock3
          : null;
  return (
    <span
      className={`status-badge ${status} ${small ? "small" : ""}`}
      title={
        status === "complete"
          ? "Calculation is current. Requirement verification is assessed separately."
          : status === "stale"
            ? "Saved outputs are historical. Recompute before downstream use."
            : STATUS_LABELS[status]
      }
    >
      {Icon ? <Icon size={11} /> : <span className="status-dot" />}
      {STATUS_LABELS[status]}
    </span>
  );
}
export function Notice({
  children,
  kind = "info",
  title,
}: {
  children: ReactNode;
  kind?: "info" | "warning" | "danger";
  title?: string;
}) {
  const Icon = kind === "info" ? CircleHelp : AlertCircle;
  return (
    <div className={`notice ${kind}`}>
      <Icon size={16} />
      <div>
        {title && <strong>{title}</strong>}
        <div>{children}</div>
      </div>
    </div>
  );
}
export function NumberField({
  label,
  value,
  onChange,
  suffix,
  hint,
  min,
  max,
  step = "any",
}: {
  label: string;
  value: number | null;
  onChange: (value: number | null) => void;
  suffix?: string;
  hint?: string;
  min?: number;
  max?: number;
  step?: number | "any";
}) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <div className="number-input">
        <input
          id={id}
          type="number"
          value={value ?? ""}
          min={min}
          max={max}
          step={step}
          placeholder="Not defined"
          onChange={(e) =>
            onChange(e.target.value === "" ? null : Number(e.target.value))
          }
          aria-describedby={hint ? `${id}-hint` : undefined}
        />
        {suffix && <span>{suffix}</span>}
      </div>
      {hint && <small id={`${id}-hint`}>{hint}</small>}
    </div>
  );
}
export function SelectField({
  label,
  value,
  onChange,
  children,
  hint,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  children: ReactNode;
  hint?: string;
}) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <div className="select-wrap">
        <select
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          {children}
        </select>
        <ChevronDown size={13} />
      </div>
      {hint && <small>{hint}</small>}
    </div>
  );
}
export function ScenarioSwitcher({
  api,
  compact = false,
}: {
  api: WorkspaceController;
  compact?: boolean;
}) {
  return (
    <div className={`scenario-switcher ${compact ? "compact" : ""}`}>
      <SelectField
        label="Active scenario"
        value={api.workspace.inputs.activeScenarioId}
        onChange={api.setActiveScenario}
      >
        {api.workspace.inputs.scenarios.length === 0 && (
          <option value="">No scenarios</option>
        )}
        {api.workspace.inputs.scenarios.map((s) => (
          <option key={s.id} value={s.id}>
            {s.name}
          </option>
        ))}
      </SelectField>
      {!compact && (
        <span className="micro-copy">
          One scenario is evaluated at a time. Switching scenarios invalidates
          downstream results.
        </span>
      )}
    </div>
  );
}
export function Metric({
  label,
  value,
  hint,
  className = "",
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  className?: string;
}) {
  return (
    <div className={`metric ${className}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {hint && <small>{hint}</small>}
    </div>
  );
}
export function Sheet({
  title,
  eyebrow,
  children,
  footer,
  onClose,
  backLabel = "Back to workbench",
}: {
  title: string;
  eyebrow?: string;
  children: ReactNode;
  footer?: ReactNode;
  onClose: () => void;
  backLabel?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const closeRef = useRef(onClose);
  closeRef.current = onClose;
  const id = useId();
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const element = ref.current;
    element?.querySelector<HTMLElement>("button")?.focus();
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        closeRef.current();
      }
      if (e.key === "Tab" && element) {
        const items = Array.from(
          element.querySelectorAll<HTMLElement>(
            'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex="0"]',
          ),
        ).filter((item) => item.getClientRects().length > 0);
        const first = items[0];
        const last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("keydown", handleKey);
      if (previous?.isConnected) previous.focus();
    };
  }, []);
  return (
    <div className="sheet-layer">
      <button
        className="sheet-scrim"
        aria-label="Close inspector"
        onClick={onClose}
      />
      <div
        className="sheet"
        role="dialog"
        aria-modal="true"
        aria-labelledby={id}
        ref={ref}
      >
        <div className="sheet-top">
          <button className="text-button" onClick={onClose}>
            <ArrowLeft size={14} />
            {backLabel}
          </button>
          <button
            className="icon-button"
            aria-label="Close inspector"
            onClick={onClose}
          >
            <X size={17} />
          </button>
        </div>
        <header className="sheet-heading">
          {eyebrow && <span className="eyebrow">{eyebrow}</span>}
          <h2 id={id}>{title}</h2>
        </header>
        <div className="sheet-content">{children}</div>
        {footer && <footer className="sheet-footer">{footer}</footer>}
      </div>
    </div>
  );
}
export function CheckList({
  checks,
  empty = "Run the assessment to see evidence and requirement results.",
}: {
  checks: DesignCheck[];
  empty?: string;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);
  if (checks.length === 0)
    return (
      <div className="empty-inline">
        <CircleHelp size={24} />
        <p>{empty}</p>
      </div>
    );
  return (
    <div className="check-list">
      {checks.map((check, index) => {
        const Icon =
          check.verdict === "pass"
            ? CheckCircle2
            : check.verdict === "fail"
              ? XCircle
              : CircleHelp;
        const key = `${check.id}-${index}`;
        return (
          <div
            key={key}
            className={`check-item ${check.verdict} ${check.id.length > 10 ? "long-id" : ""}`}
          >
            <button
              className="check-summary"
              onClick={() => setExpanded(expanded === key ? null : key)}
              aria-expanded={expanded === key}
            >
              <Icon size={17} />
              <span className="check-id">{check.id}</span>
              <span className="check-title">{check.title}</span>
              <span className={`verdict ${check.verdict}`}>
                {check.verdict === "not-applicable"
                  ? "N/A"
                  : check.verdict === "unassessed"
                    ? "Unassessed"
                    : check.verdict === "pass"
                      ? "Pass"
                      : "Fail"}
              </span>
              <ChevronDown
                size={14}
                className={expanded === key ? "rotate" : ""}
              />
            </button>
            {expanded === key && (
              <div className="check-detail">
                <p>{check.detail}</p>
                {check.equation && (
                  <code className="equation">{check.equation}</code>
                )}
                {check.scope && (
                  <p className="scope-line">
                    <strong>Scope</strong> {check.scope}
                  </p>
                )}
                {!!check.sourceIds?.length && (
                  <p className="source-ids">
                    Evidence references: {check.sourceIds.join(", ")}
                  </p>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
