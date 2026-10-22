import { useState } from "react";
import {
  Activity,
  ArrowUpRight,
  CheckCircle2,
  CircleHelp,
  ClipboardCheck,
  Play,
  ShieldAlert,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import type { NodeId } from "../types";
import { canEvaluate } from "./NodeInspector";
import { EnergyPlots } from "./Plots";
import { CheckList, Notice, ScenarioSwitcher, StatusBadge } from "./ui";
import type { WorkspaceController } from "./ui";

export function AssessmentView({
  api,
  onNode,
}: {
  api: WorkspaceController;
  onNode: (id: NodeId) => void;
}) {
  const [section, setSection] = useState<"requirements" | "energy">(
    "requirements",
  );
  const [filter, setFilter] = useState("all");
  const { analysis, inputs } = api.workspace;
  const checks = analysis.checks ?? [];
  const counts = {
    pass: checks.filter((c) => c.verdict === "pass").length,
    fail: checks.filter((c) => c.verdict === "fail").length,
    unassessed: checks.filter((c) => c.verdict === "unassessed").length,
    na: checks.filter((c) => c.verdict === "not-applicable").length,
  };
  const simulationScenario = inputs.scenarios.find(
    (s) => s.id === analysis.simulation?.scenarioId,
  );
  const filtered = checks.filter(
    (c) => filter === "all" || c.verdict === filter,
  );
  return (
    <div className="tab-page assessment-page">
      <div className="page-intro">
        <div>
          <span className="eyebrow">EVIDENCE & VERIFICATION</span>
          <h1>Know what your design supports.</h1>
          <p>
            Trace every result to its criterion, assumptions, and remaining
            evidence.
          </p>
        </div>
        <button
          className="button primary"
          disabled={!canEvaluate(api, "assessment")}
          onClick={() => api.runNode("assessment")}
        >
          <Play size={14} fill="currentColor" />
          {api.statuses.assessment === "stale"
            ? "Refresh assessment"
            : "Run assessment"}
        </button>
      </div>
      <div className="assessment-context">
        <ScenarioSwitcher api={api} compact />
        <div className="report-freshness">
          <span>Requirement report</span>
          <StatusBadge status={api.statuses.assessment} />
        </div>
      </div>
      {api.statuses.assessment === "stale" && (
        <Notice kind="warning" title="Saved report is out of date">
          Mission inputs, scenario, or architecture changed. Refresh
          dependencies and rerun the assessment before using these results.
          <button className="text-button" onClick={() => onNode("assessment")}>
            Inspect stale dependencies
            <ArrowUpRight size={12} />
          </button>
        </Notice>
      )}
      <div className="assessment-counts">
        <div className="count-card pass">
          <CheckCircle2 size={17} />
          <strong>{checks.length ? counts.pass : "—"}</strong>
          <span>Pass</span>
          <small>Within the assessed scope</small>
        </div>
        <div className="count-card fail">
          <XCircle size={17} />
          <strong>{checks.length ? counts.fail : "—"}</strong>
          <span>Fail</span>
          <small>Known criterion violations</small>
        </div>
        <div className="count-card unassessed">
          <CircleHelp size={17} />
          <strong>{checks.length ? counts.unassessed : "—"}</strong>
          <span>Unassessed</span>
          <small>Decisive evidence missing</small>
        </div>
        <div className="count-card na">
          <ClipboardCheck size={17} />
          <strong>{checks.length ? counts.na : "—"}</strong>
          <span>Not applicable</span>
          <small>Outside this configuration</small>
        </div>
      </div>
      <div className="report-panel">
        <header className="report-panel-header">
          <div
            className="report-tabs"
            role="group"
            aria-label="Assessment report section"
          >
            <button
              className={section === "requirements" ? "active" : ""}
              onClick={() => setSection("requirements")}
            >
              <ShieldCheck size={14} />
              Requirements<span>{checks.length || "—"}</span>
            </button>
            <button
              className={section === "energy" ? "active" : ""}
              onClick={() => setSection("energy")}
            >
              <Activity size={14} />
              Energy timeline
            </button>
          </div>
          <span className="scope-badge">
            <ShieldAlert size={12} />
            Concept assessment
          </span>
        </header>
        {section === "requirements" ? (
          <>
            <div className="report-filter">
              <div>
                <strong>EPS requirement checks</strong>
                <span>Open a row to inspect the criterion and evidence.</span>
              </div>
              <select
                aria-label="Filter requirement verdicts"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="all">All outcomes</option>
                <option value="pass">Pass</option>
                <option value="fail">Fail</option>
                <option value="unassessed">Unassessed</option>
                <option value="not-applicable">Not applicable</option>
              </select>
            </div>
            {checks.length === 0 ? (
              <div className="large-empty">
                <ShieldCheck size={38} strokeWidth={1.2} />
                <h2>Evidence starts with evaluation</h2>
                <p>
                  Run the ready nodes to compute the energy history, then assess
                  the current design against EPS-01–20.
                </p>
                <button
                  className="button secondary"
                  onClick={() => onNode("assessment")}
                >
                  Inspect assessment inputs
                  <ArrowUpRight size={13} />
                </button>
              </div>
            ) : (
              <CheckList
                checks={filtered}
                empty="No checks have this outcome."
              />
            )}
            <div className="report-scope">
              <ShieldAlert size={16} />
              <p>
                <strong>Missing evidence is not a pass.</strong> Energy-only
                results leave charge-based reserve and replenishment criteria
                unassessed for EPS-10 and EPS-11 unless a known energy violation
                gives a fail. Hardware qualification and detailed wiring remain
                unassessed.
              </p>
            </div>
          </>
        ) : (
          <div className="energy-report">
            <div className="energy-report-heading">
              <div>
                <span className="eyebrow">
                  {simulationScenario?.name ??
                    api.activeScenario?.name ??
                    "NO ACTIVE SCENARIO"}
                </span>
                <h3>Mission energy history</h3>
              </div>
              <button
                className="button secondary small"
                disabled={!canEvaluate(api, "simulation")}
                onClick={() => api.runNode("simulation")}
              >
                <Play size={12} />
                Run simulation
              </button>
            </div>
            {analysis.simulation && api.statuses.simulation !== "complete" && (
              <Notice kind="warning" title="Stored timeline is not current">
                This history belongs to the last evaluated scenario revision.
                Recompute simulation before using it.
              </Notice>
            )}
            {analysis.simulation ? (
              <>
                <EnergyPlots
                  simulation={analysis.simulation}
                  scenario={simulationScenario}
                  stale={api.statuses.simulation !== "complete"}
                />
                <details className="disclosure">
                  <summary>Model assumptions and numerical scope</summary>
                  <ul className="plain-list">
                    {analysis.simulation.assumptions.map(
                      (assumption, index) => (
                        <li key={index}>{assumption}</li>
                      ),
                    )}
                  </ul>
                </details>
                <CheckList checks={analysis.simulation.checks} />
              </>
            ) : (
              <div className="large-empty">
                <Activity size={38} strokeWidth={1.2} />
                <h2>No energy timeline yet</h2>
                <p>
                  Provide installed solar power, battery energy, and current
                  dependencies to unlock the simulation.
                </p>
                <button
                  className="button secondary"
                  onClick={() => onNode("simulation")}
                >
                  Inspect simulation inputs
                  <ArrowUpRight size={13} />
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      <p className="page-footnote">
        Results describe their evaluated model revision and declared
        assumptions. Historical results require refresh before use. They do not
        constitute completed flight verification.
      </p>
    </div>
  );
}
