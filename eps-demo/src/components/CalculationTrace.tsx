import type { NodeId, Workspace } from '../types';
import './calculation-trace.css';

export interface Step { label: string; inputs: string; relation: string; output: string }
const format = (value: number | null | undefined, suffix = '', digits = 2) => value == null || !Number.isFinite(value) ? 'missing' : `${value.toFixed(digits)}${suffix}`;

export function stepsFor(id: NodeId, workspace: Workspace): Step[] {
  const { inputs, analysis } = workspace;
  const scenario = inputs.scenarios.find(item => item.id === inputs.activeScenarioId);
  switch (id) {
    case 'mission': return [{ label: 'Model boundary', inputs: `${format(inputs.mission.altitudeKm, ' km')} altitude`, relation: 'Circular orbit, fixed eclipse geometry', output: `${format(inputs.mission.lifetimeYears, ' years')} lifetime` }];
    case 'orbit': return [
      { label: 'Orbital period', inputs: 'h, Rₑ = 6378 km, μ = 398601 km³/s²', relation: 'Tₒ = 2π √((Rₑ + h)³ / μ)', output: format(analysis.orbit?.periodS, ' s') },
      { label: 'Eclipse angle', inputs: `h = ${format(inputs.mission.altitudeKm, ' km')}`, relation: 'ψ = arccos(Rₑ / (Rₑ + h))', output: format(analysis.orbit?.psiRad, ' rad', 4) },
      { label: 'Illumination intervals', inputs: 'Tₒ, ψ', relation: 'Tₛ/ₑ = (½ ± ψ/π) Tₒ', output: `${format(analysis.orbit?.sunlightS, ' s')} sun / ${format(analysis.orbit?.eclipseS, ' s')} eclipse` },
    ];
    case 'scenarios': return [{ label: 'Scheduled demand', inputs: `${scenario?.loads.length ?? 0} constant-power loads`, relation: 'Active power inside the union of windows. Idle power outside.', output: scenario?.name ?? 'No active scenario' }];
    case 'budget': return [
      { label: 'Sunlight energy', inputs: 'Sunlight interval + scheduled loads + additional EPS baseline', relation: 'Eₛ = ∫sun (Σ Pℓ(mode, t) + PEPS) dt', output: format(analysis.budget?.sunlightWh, ' Wh') },
      { label: 'Eclipse energy', inputs: 'Eclipse interval + scheduled loads + additional EPS baseline', relation: 'Eₑ = ∫eclipse (Σ Pℓ(mode, t) + PEPS) dt', output: format(analysis.budget?.eclipseWh, ' Wh') },
      { label: 'Coincident demand peak', inputs: 'All simultaneous load states + additional EPS baseline once', relation: 'Ppeak = maxₜ (Σ Pℓ(mode, t) + PEPS)', output: format(analysis.budget?.peakW, ' W') },
    ];
    case 'solar': return [
      { label: 'Minimum source power', inputs: `Eₛ, Eₑ, Tₛ; Xₛ = ${format(inputs.solar.sunlightEfficiency)}, Xₑ = ${format(inputs.solar.eclipseEfficiency)}`, relation: 'Pmin = (Eₛ/Xₛ + Eₑ/Xₑ) / Tₛ', output: format(analysis.solar?.minimumPowerW, ' W') },
      { label: 'One cell at EOL', inputs: `${format(inputs.solar.cellEolV, ' V')} × ${format(inputs.solar.cellEolA, ' A')}`, relation: 'Pcell,EOL = Vmp,EOL × Imp,EOL', output: format(analysis.solar?.cellPowerW, ' W') },
      { label: 'Integer count lower bound', inputs: 'Pmin, Pcell,EOL', relation: 'Ninstalled ≥ ceil(Pmin / Pcell,EOL)', output: `${format(analysis.solar?.cellCount, ' cells', 0)} (no wiring or packing inferred)` },
    ];
    case 'battery': return [
      { label: 'Preliminary energy', inputs: `Eₑ, DoD = ${format(inputs.battery.dod)}, M = ${format(inputs.battery.margin)}`, relation: 'Erequired = Eₑ / DoD × (1 + M)', output: format(analysis.battery?.requiredWh, ' Wh') },
      { label: 'Required cycling', inputs: 'Lifetime × days/year × orbits/day', relation: 'Ncycle = Nyears × Ndays/year × Norbits/day', output: `${format(analysis.battery?.cycles, ' cycles', 0)} (life fit unassessed)` },
      { label: 'Physical EOL capacity', inputs: `BOL ${format(inputs.battery.capacityWh, ' Wh')} × retained ${format(inputs.battery.retainedEnergy)}`, relation: 'Emax = fE × EBOL. Margin is not applied again.', output: format(analysis.battery?.eolCapacityWh, ' Wh') },
    ];
    case 'topology': return [{ label: 'Logical power path', inputs: `${inputs.topology.conditioning}, ${inputs.topology.distribution}, ${inputs.topology.bus}`, relation: 'Time model uses the declared constant conditioning efficiency.', output: `η = ${format(inputs.topology.efficiency)}; idle = ${format(inputs.topology.idlePowerW, ' W')}` }];
    case 'candidates': return [
      { label: 'Finite catalog scope', inputs: 'Required CSRM roles + preliminary bounds', relation: 'Enumerate fixed products and permitted whole quantities.', output: `${analysis.suggestions?.length ?? 0} screened product alternatives` },
      { label: 'Evidence gate', inputs: 'Sourced values, meanings and conditions', relation: 'Known violations reject. Missing decisive evidence stays visible.', output: 'No complete feasible-set or qualification claim' },
    ];
    case 'simulation': return [
      { label: 'Common power boundary', inputs: 'EOL source × illumination × conditioning efficiency', relation: 'PΔ = Pg − (Σ Ploads + Pidle)', output: 'External battery boundary' },
      { label: 'Charge acceptance', inputs: 'Surplus, charge-power limit and remaining capacity', relation: 'Pch = min(max(PΔ, 0), Plimit, (Emax − E)/(ηc Δt))', output: 'Unused surplus recorded separately' },
      { label: 'Stored energy update', inputs: `ηc = ${format(inputs.battery.chargeEfficiency)}, ηd = ${format(inputs.battery.dischargeEfficiency)}`, relation: 'Eₖ₊₁ = Eₖ + (ηc Pch − Pdis/ηd) Δt', output: `Minimum ${format(analysis.simulation?.minEnergyWh, ' Wh')}. Charge SoC unassessed.` },
    ];
    case 'assessment': return [{ label: 'Scoped requirement review', inputs: 'Current calculations + current product allocations', relation: 'Each applicable predicate retains its missing evidence and known violations.', output: 'Pass / fail / unassessed. Active scenario only.' }];
  }
}

/** Parameter-level detail beneath each activity in the main EPS workflow. */
export function CalculationTrace({ nodeId, workspace }: { nodeId: NodeId; workspace: Workspace }) {
  const record = workspace.records[nodeId];
  const stale = record.evaluatedRevision !== null && record.evaluatedRevision !== record.revision;
  return <details className="calculation-trace" open>
    <summary>Parameter dependency trace</summary>
    {stale && <p style={{ margin: '0 14px 12px', color: '#dbb787' }}>Current inputs are shown below. Recompute to derive their outputs. Historical results remain marked stale above.</p>}
    <div className="calculation-trace__steps">
      {stepsFor(nodeId, workspace).map((step, index) => <div className="calculation-trace__step" key={step.label}>
        <span className="calculation-trace__index">{String(index + 1).padStart(2, '0')}</span>
        <div><h4>{step.label}</h4><p className="calculation-trace__inputs">{step.inputs}</p><code>{step.relation}</code><p className="calculation-trace__output">↳ {stale ? 'Recompute for the current output' : step.output}</p></div>
      </div>)}
    </div>
  </details>;
}
