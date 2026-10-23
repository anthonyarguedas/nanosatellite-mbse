import { useMemo, useState } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, BatteryCharging, Clock3, Moon, Sun } from "lucide-react";
import type {
  BudgetResult,
  OrbitResult,
  Scenario,
  SimulationResult,
} from "../types";
import { Metric, Notice, number, unit } from "./ui";
import {
  budgetPlotBasis,
  savedCaseLabel,
  simulationPlotBasis,
} from "./result-history";

export function SavedResultLabel({
  kind,
  scenarioId,
  scenarioRevision,
  scenario,
  stale = false,
}: {
  kind: string;
  scenarioId?: string;
  scenarioRevision?: number;
  scenario?: Scenario;
  stale?: boolean;
}) {
  return (
    <div
      className={`saved-result-label ${stale ? "historical" : ""}`}
      role="note"
      title={savedCaseLabel(scenarioId, scenarioRevision)}
    >
      <Clock3 size={14} />
      <div>
        <strong>
          {stale ? "Historical" : "Saved"} {kind}
        </strong>
        <span>
          {scenario?.name ?? scenarioId ?? "Case identity not recorded"}
        </span>
        <small>{savedCaseLabel(scenarioId, scenarioRevision)}</small>
      </div>
    </div>
  );
}

const GRID = "#2c323b";
const tooltipStyle = {
  background: "#20262e",
  border: "1px solid #404854",
  borderRadius: 8,
  fontSize: 11,
  color: "#e9edf3",
  boxShadow: "0 8px 32px #0006",
};
const axis = { fill: "#87919e", fontSize: 10, fontFamily: "inherit" };
export function OrbitDiagram({
  orbit,
  altitudeKm,
}: {
  orbit?: OrbitResult;
  altitudeKm: number | null;
}) {
  return (
    <div className="orbit-visual">
      <svg
        viewBox="0 0 410 180"
        role="img"
        aria-label="Illustrative circular orbit with sunlight and eclipse, not to scale"
      >
        <defs>
          <radialGradient id="earth-shade">
            <stop offset="0%" stopColor="#31505d" />
            <stop offset="100%" stopColor="#182934" />
          </radialGradient>
        </defs>
        <g stroke="#ac8752" strokeWidth="1" opacity=".5">
          {[48, 68, 88, 108, 128].map((y) => (
            <path key={y} d={`M 7 ${y} L 72 ${y}`} />
          ))}
        </g>
        <circle
          cx="164"
          cy="88"
          r="68"
          fill="none"
          stroke="#3d4752"
          strokeWidth="1"
          strokeDasharray="3 5"
        />
        <path
          d="M 164 20 A 68 68 0 0 0 164 156"
          fill="none"
          stroke="#f2b565"
          strokeWidth="2"
        />
        <path
          d="M 164 20 A 68 68 0 0 1 164 156"
          fill="none"
          stroke="#728198"
          strokeWidth="2"
        />
        <path
          d="M 194 64 L 248 43 L 248 133 L 194 112 Z"
          fill="#171c24"
          opacity=".8"
        />
        <circle
          cx="164"
          cy="88"
          r="34"
          fill="url(#earth-shade)"
          stroke="#4a6570"
        />
        <ellipse
          cx="164"
          cy="88"
          rx="14"
          ry="34"
          fill="none"
          stroke="#496574"
          opacity=".5"
        />
        <path
          d="M 131 88 H 197 M 138 70 Q 164 83 190 70 M 138 106 Q 164 93 190 106"
          fill="none"
          stroke="#496574"
          opacity=".5"
        />
        <g transform="translate(119 37) rotate(-37)">
          <rect x="-4" y="-4" width="8" height="8" rx="1" fill="#f18c63" />
          <path
            d="M -15 -4 H -6 V 4 H -15 Z M 6 -4 H 15 V 4 H 6 Z"
            fill="#648b9e"
          />
        </g>
        <text x="274" y="58" fill="#8e99a6" fontSize="10" letterSpacing="1">
          CIRCULAR ORBIT
        </text>
        <text x="274" y="86" fill="#e9edf3" fontSize="23" fontWeight="500">
          {altitudeKm == null ? "—" : number(altitudeKm, 0)}
          <tspan fill="#87919e" fontSize="12">
            {" "}
            km
          </tspan>
        </text>
        <text x="274" y="108" fill="#87919e" fontSize="10">
          altitude above Earth
        </text>
        <text x="108" y="175" fill="#626d7b" fontSize="9">
          Illustrative · not to scale
        </text>
      </svg>
      {orbit && (
        <div className="metric-grid three">
          <Metric
            label="Orbital period"
            value={unit(orbit.periodS / 60, "min")}
          />
          <Metric
            label="Sunlight"
            value={
              <>
                <Sun size={12} />
                {number(orbit.sunlightS / 60)} min
              </>
            }
          />
          <Metric
            label="Eclipse"
            value={
              <>
                <Moon size={12} />
                {number(orbit.eclipseS / 60)} min
              </>
            }
          />
        </div>
      )}
    </div>
  );
}
export function DemandPlot({
  budget,
  orbit,
  scenario,
  stale = false,
}: {
  budget: BudgetResult;
  orbit?: OrbitResult;
  scenario?: Scenario;
  stale?: boolean;
}) {
  const basis = budgetPlotBasis(budget, orbit);
  const max = basis.periodS !== undefined ? basis.periodS / 60 : 100;
  const data = budget.samples.map((sample) => ({
    time: sample.phase * max,
    demand: sample.powerW,
  }));
  return (
    <div
      className="demand-result"
      data-orbit-period-s={basis.periodS}
      data-sunlight-fraction={basis.sunlightFraction}
    >
      <SavedResultLabel
        kind="power budget"
        scenarioId={budget.scenarioId}
        scenarioRevision={budget.scenarioRevision}
        scenario={scenario}
        stale={stale}
      />
      {stale && basis.legacyTiming && (
        <p className="legacy-result-note">
          This older result did not retain orbit timing. Current orbit values
          are a legacy fallback, not its original calculation basis.
        </p>
      )}
      <div className="plot-card">
        <div className="plot-heading">
          <div>
            <Activity size={14} />
            <strong>{budget.additionalEpsPowerW ? "Spacecraft loads + EPS baseline" : "Scheduled load demand"}</strong>
          </div>
          <span>W</span>
        </div>
        <div className="plot-area demand-plot">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={data}
              margin={{ top: 12, right: 10, bottom: 4, left: -25 }}
            >
              <CartesianGrid
                stroke={GRID}
                strokeDasharray="3 5"
                vertical={false}
              />
              <XAxis
                dataKey="time"
                type="number"
                domain={[0, max]}
                tick={axis}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => number(value, 0)}
                minTickGap={25}
              />
              <YAxis tick={axis} tickLine={false} axisLine={false} />
              {basis.sunlightFraction !== undefined && (
                <ReferenceArea
                  x1={basis.sunlightFraction * max}
                  x2={max}
                  fill="#8996ab"
                  fillOpacity={0.07}
                />
              )}
              <Tooltip
                contentStyle={tooltipStyle}
                labelFormatter={(value) =>
                  `${number(Number(value))} ${basis.periodS !== undefined ? "min" : "% of orbit"}`
                }
                formatter={(value) => [`${number(Number(value))} W`, "Demand"]}
              />
              <Area
                type="stepAfter"
                dataKey="demand"
                stroke="#85c7ca"
                fill="#77b8bc"
                fillOpacity={0.08}
                strokeWidth={1.8}
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        <div className="plot-axis-label">
          {basis.periodS !== undefined
            ? "Time in saved orbit (minutes)"
            : "Orbit phase (%)"}
          <span className="legend-key">
            <i className="eclipse" />
            Shaded region: eclipse
          </span>
        </div>
      </div>
    </div>
  );
}
export function EnergyPlots({
  simulation,
  scenario,
  compact = false,
  stale = false,
  section = 'all',
  units,
  onUnitsChange,
}: {
  simulation: SimulationResult;
  section?: 'all' | 'power' | 'energy' | 'outcome';
  units?: 'percent' | 'wh';
  onUnitsChange?: (value:'percent'|'wh')=>void;
  scenario?: Scenario;
  compact?: boolean;
  stale?: boolean;
}) {
  const [localMode, setLocalMode] = useState<"percent" | "wh">("percent");
  const mode=units??localMode;
  const setMode=onUnitsChange??setLocalMode;
  const data = useMemo(
    () =>
      simulation.points.map((point) => ({
        time: point.timeS / 60,
        generation: point.generationW,
        demand: point.demandW,
        energy: mode === "percent" ? point.energyPercent : point.batteryWh,
      })),
    [simulation, mode],
  );
  const eclipses = useMemo(() => {
    const ranges: { start: number; end: number }[] = [];
    let start: number | null = null;
    simulation.points.forEach((point, index) => {
      if (!point.sunlight && start === null) start = point.timeS / 60;
      if (
        start !== null &&
        (point.sunlight || index === simulation.points.length - 1)
      ) {
        ranges.push({ start, end: point.timeS / 60 });
        start = null;
      }
    });
    return ranges;
  }, [simulation]);
  const basis = simulationPlotBasis(simulation, scenario);
  const reserve = mode === "percent" ? basis.reservePercent : basis.reserveWh;
  const maximum = basis.durationS > 0 ? basis.durationS / 60 : 1;
  const axisX = (
    <XAxis
      dataKey="time"
      type="number"
      domain={[0, maximum]}
      tick={axis}
      tickLine={false}
      axisLine={false}
      tickFormatter={(value) => number(value, 0)}
      minTickGap={35}
    />
  );
  const unassessedTail =
    simulation.stoppedAtS !== null &&
    basis.durationS > simulation.stoppedAtS ? (
      <ReferenceArea
        x1={simulation.stoppedAtS / 60}
        x2={maximum}
        fill="#b65b6c"
        fillOpacity={0.065}
      />
    ) : null;
  const eclipseAreas = eclipses.map((range, index) => (
    <ReferenceArea
      key={index}
      x1={range.start}
      x2={range.end}
      fill="#8996ab"
      fillOpacity={0.075}
    />
  ));
  return (
    <div
      className={`energy-plots ${compact ? "compact" : ""}`}
      data-reserve-wh={basis.reserveWh}
      data-duration-s={basis.durationS}
    >
      <SavedResultLabel
        kind="energy run"
        scenarioId={simulation.scenarioId}
        scenarioRevision={simulation.scenarioRevision}
        scenario={scenario}
        stale={stale}
      />
      {stale && basis.legacyReserve && (
        <p className="legacy-result-note">
          This older run did not retain its reserve criterion. The current
          reserve is shown only as a legacy reference, not as the criterion
          originally assessed.
        </p>
      )}
      {section === 'all' && <Notice kind="warning" title="Energy-only model">
        Normalized stored energy is not charge-based state of charge. Voltage,
        charge reserve, thermal behavior and detailed interfaces remain outside
        this model.
      </Notice>}
      {(section === 'all' || section === 'power') && <div className="plot-card">
        <div className="plot-heading">
          <div>
            <Sun size={14} />
            <strong>Generation & demand</strong>
          </div>
          <div className="chart-legend">
            <span>
              <i className="generation" />
              Generation
            </span>
            <span>
              <i className="demand" />
              Demand
            </span>
          </div>
        </div>
        <div className="plot-area power-plot">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={data}
              margin={{ top: 12, right: 15, bottom: 2, left: -20 }}
            >
              <CartesianGrid
                stroke={GRID}
                strokeDasharray="3 5"
                vertical={false}
              />
              {axisX}
              <YAxis
                tick={axis}
                tickLine={false}
                axisLine={false}
                unit=" W"
                width={56}
              />
              {eclipseAreas}
              {unassessedTail}
              <Tooltip
                contentStyle={tooltipStyle}
                labelFormatter={(value) => `${number(Number(value))} min`}
                formatter={(value, name) => [
                  `${number(Number(value))} W`,
                  name === "generation" ? "Generation" : "Demand",
                ]}
              />
              <Line
                type="stepAfter"
                dataKey="generation"
                stroke="#edb870"
                strokeWidth={1.6}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="stepAfter"
                dataKey="demand"
                stroke="#7dbacb"
                strokeWidth={1.7}
                dot={false}
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>}
      {(section === 'all' || section === 'energy') && <div className="plot-card">
        <div className="plot-heading">
          <div>
            <BatteryCharging size={14} />
            <strong>Stored energy</strong>
          </div>
          <div
            className="segmented tiny"
            role="group"
            aria-label="Stored energy units"
          >
            <button
              className={mode === "percent" ? "active" : ""}
              onClick={() => setMode("percent")}
            >
              %
            </button>
            <button
              className={mode === "wh" ? "active" : ""}
              onClick={() => setMode("wh")}
            >
              Wh
            </button>
          </div>
        </div>
        <div className="plot-area stored-energy-plot">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={data}
              margin={{ top: 12, right: 15, bottom: 2, left: -20 }}
            >
              <CartesianGrid
                stroke={GRID}
                strokeDasharray="3 5"
                vertical={false}
              />
              {axisX}
              <YAxis
                tick={axis}
                tickLine={false}
                axisLine={false}
                domain={
                  mode === "percent" ? [0, 100] : [0, simulation.capacityWh]
                }
                unit={mode === "percent" ? "%" : ""}
                width={56}
              />
              {eclipseAreas}
              {unassessedTail}
              <Tooltip
                contentStyle={tooltipStyle}
                labelFormatter={(value) => `${number(Number(value))} min`}
                formatter={(value) => [
                  `${number(Number(value))} ${mode === "percent" ? "%" : "Wh"}`,
                  "Stored energy",
                ]}
              />
              {reserve !== undefined && (
                <ReferenceLine
                  y={reserve}
                  stroke="#d7955f"
                  strokeDasharray="4 4"
                />
              )}
              <Area
                type="linear"
                dataKey="energy"
                stroke="#80c6b2"
                fill="#80c6b2"
                fillOpacity={0.07}
                strokeWidth={1.9}
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        <div className="plot-axis-label">
          Elapsed time (minutes)
          <span className="legend-key">
            <i className="eclipse" />
            Eclipse
            {reserve !== undefined && (
              <>
                <i className="reserve" />
                {basis.legacyReserve
                  ? "Current reserve (legacy fallback)"
                  : "Saved reserve"}{" "}
                {number(reserve)}
                {mode === "percent" ? "%" : " Wh"}
              </>
            )}
          </span>
        </div>
      </div>}
      {(section === 'all' || section === 'outcome') && <div className="metric-grid three">
        <Metric
          label="Minimum energy"
          value={unit(simulation.minEnergyWh, "Wh")}
        />
        <Metric
          label="Energy closure"
          value={`${simulation.closureWh > 0 ? "+" : ""}${number(simulation.closureWh)} Wh`}
          hint="End minus start"
        />
        <Metric
          label="Unserved energy (lower bound)"
          value={unit(simulation.shortageWh, "Wh")}
          className={simulation.shortageWh > 0 ? "danger-text" : ""}
        />
      </div>}
      {simulation.stoppedAtS !== null && (
        <Notice kind="danger" title="Simulation stopped">
          An invalid battery state was reached at{" "}
          {number(simulation.stoppedAtS / 60)} minutes. The remaining interval
          was not assessed.
        </Notice>
      )}
    </div>
  );
}
