import { useRef, useState } from 'react';
import { ArrowDownToLine, ArrowRight, Cable, Check, CircuitBoard, FileJson, LockKeyhole, Network, Upload } from 'lucide-react';
import type { Catalog, NodeId, Workspace } from '../types';
import { buildKiCadExport, buildReviewedKiCadRules, createKiCadZip, getKiCadArchitectureFingerprint, getKiCadReadiness } from '../kicad';
import type { KiCadExport, ReviewedPhysicalRules } from '../kicad';
import { Notice, Sheet } from './ui';
import './kicad-panel.css';

function saveBlob(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url; link.download = name; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function saveProject(result: KiCadExport, name: string) {
  const bytes = createKiCadZip(result.files);
  saveBlob(new Blob([bytes], { type: 'application/zip' }), name);
}
function ruleTemplate(workspace: Workspace, catalog: Catalog) {
  const dimension = (ids: string[]) => ({ minimumMm: null, requirementIds: ids, sourceIds: ['reviewed-source'], rationale: '', derivation: { method: '', conditions: '', margin: '' } });
  return {
    scope: 'INPUT TEMPLATE ONLY. No physical values or approval are supplied. Fill from reviewed engineering evidence. This is not a flight design or a PCB.',
    schemaVersion: 1, architectureFingerprint: getKiCadArchitectureFingerprint(workspace, catalog), catalogRevision: catalog.revision,
    physicalNetlistRevision: '', approval: { status: 'unreviewed', engineer: '', date: '' },
    sources: [{ id: 'reviewed-source', url: '', revision: '', location: '' }], knownNets: [],
    fabrication: { sourceIds: ['reviewed-source'], minimumTrackWidthMm: null, minimumClearanceMm: null, minimumViaDiameterMm: null, minimumDrillMm: null, minimumAnnularWidthMm: null, minimumEdgeClearanceMm: null },
    classes: [{ name: 'EPS_POWER', nets: [], trackWidth: dimension(['EPS-07']), clearance: dimension(['EPS-03']), viaDiameter: dimension(['EPS-07']), viaDrill: { ...dimension(['EPS-07']), maximumMm: null } }],
    edgeClearance: dimension(['EPS-20']),
  };
}
function checkedRules(value: unknown, catalog: Catalog): ReviewedPhysicalRules {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('The rule profile must be a JSON object. Start from the rule input template.');
  const input = value as Record<string, unknown>;
  if (input.schemaVersion !== 1) throw new Error('Unsupported rule profile. Expected schemaVersion 1.');
  if (input.catalogRevision !== catalog.revision) throw new Error('The rule profile uses another catalog revision. Review it against the current architecture.');
  for (const [key, max] of [['sources', 256], ['knownNets', 2048], ['classes', 64]] as const) {
    if (!Array.isArray(input[key]) || input[key].length > max) throw new Error(`${key} must be a list of at most ${max} items.`);
  }
  if (!input.fabrication || !input.approval || !input.edgeClearance) throw new Error('Supply fabrication limits, approval and board-edge constraints. Use the rule input template.');
  return value as ReviewedPhysicalRules;
}

export function KiCadPanel({ workspace, catalog, onClose, onNode }: { workspace: Workspace; catalog: Catalog; onClose: () => void; onNode: (id: NodeId) => void }) {
  const readiness = getKiCadReadiness(workspace, catalog);
  const [error, setError] = useState<string | null>(null);
  const [rules, setRules] = useState<{ result: KiCadExport; fingerprint: string } | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const fingerprint = getKiCadArchitectureFingerprint(workspace, catalog);
  async function importRules(file: File) {
    setError(null); setRules(null);
    try {
      if (file.size > 2_000_000) throw new Error('Rule profiles must be smaller than 2 MB.');
      const input = checkedRules(JSON.parse(await file.text()), catalog);
      setRules({ result: buildReviewedKiCadRules(input, fingerprint), fingerprint });
    } catch (cause) {
      setError(cause instanceof TypeError ? 'The rule profile is incomplete. Use the input template and fill every required section and approved dimension.' : cause instanceof Error ? cause.message : 'The rule profile could not be read.');
    }
  }
  return <Sheet title="From architecture to KiCad." eyebrow="ENGINEERING HANDOFF" onClose={onClose} footer={<div className="kicad-panel__footer"><span>Logical review project<br /><small>Physical PCB routing remains gated.</small></span><button className="button primary" disabled={!readiness.ready} onClick={() => {
    try { saveProject(buildKiCadExport(workspace, catalog), 'orbitwork-kicad-review.zip'); setError(null); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'The project could not be exported.'); }
  }}><ArrowDownToLine size={14} />Download review ZIP</button></div>}>
    <p className="body-copy">Export the current COTS allocation as a real KiCad project. The drawing uses automatically placed sheets and routed logical associations.</p>
    <div className="kicad-panel__states">
      <div className={readiness.ready ? 'available' : ''}><Network size={17} /><span>Review drawing<strong>{readiness.ready ? 'Ready to export' : 'Needs current allocations'}</strong></span>{readiness.ready ? <Check size={15} /> : <LockKeyhole size={14} />}</div>
      <div><CircuitBoard size={17} /><span>Physical PCB routing<strong>Missing physical design inputs</strong></span><LockKeyhole size={14} /></div>
    </div>
    <Notice kind="warning" title="Review drawing, with explicit limits">Named ports describe functional intent. They are not manufacturer pin numbers or verified electrical nets. No COTS internal circuit or physical PCB is generated.</Notice>
    {!readiness.ready && <section className="inspector-section"><h3>Complete these prerequisites</h3><ul className="plain-list">{readiness.blockers.map(item => <li key={item}>{item}</li>)}</ul><button className="button secondary full-width" onClick={() => onNode('candidates')}>Inspect COTS suggestions<ArrowRight size={13} /></button></section>}
    <section className="inspector-section"><h3>The review pipeline</h3><ol className="kicad-panel__pipeline"><li><span>01</span><div><strong>Freeze current allocations</strong><p>Exact catalog revisions, sources and quantities. Integrated roles share one physical usage.</p></div></li><li><span>02</span><div><strong>Place and route the drawing</strong><p>Logical associations avoid sheets and existing wires. Any unresolved association stays in the manifest.</p></div></li><li><span>03</span><div><strong>Inspect in KiCad</strong><p>Open the schematic and child sheets together. The local validation command retains rendered sheets, netlist and electrical rule findings.</p></div></li></ol><p className="section-caption">The exported README includes the local validation command. An electrical check on opaque sheets does not assess the actual COTS circuit.</p></section>
    <details className="disclosure"><summary>What blocks physical autorouting?</summary><ul className="plain-list">{readiness.physicalGates.map(item => <li key={item}>{item}</li>)}</ul><p className="body-copy">The current catalog does not establish these inputs. A configured external PCB router would follow the reviewed physical netlist and board constraints.</p></details>
    <section className="inspector-section"><div className="section-heading"><h3>Requirements → physical rules</h3><Cable size={15} /></div><p className="body-copy">Selected EPS requirements can inform reviewed track widths, via geometry and spacing. Current, voltage and temperature alone do not define safe geometric rules.</p><Notice>Energy balance, operating envelopes, protection behavior and full installation fit remain external assessments. Passing board checks leaves known EPS failures unchanged.</Notice>
      <details className="disclosure"><summary>Import an approved rule profile</summary><p className="body-copy">Supply a physical netlist revision, exact nets, fabrication minima, source references, derived dimensions and explicit engineer approval. The template contains no assumed physical values.</p><div className="kicad-panel__actions"><button className="button secondary small" disabled={!readiness.ready} onClick={() => saveBlob(new Blob([JSON.stringify(ruleTemplate(workspace, catalog), null, 2)], { type: 'application/json' }), 'orbitwork-rule-input-template.json')}><FileJson size={14} />Input template</button><button className="button secondary small" disabled={!readiness.ready} onClick={() => fileInput.current?.click()}><Upload size={14} />Import reviewed JSON</button></div><input type="file" className="sr-only" accept=".json,application/json" aria-label="Import approved KiCad rule profile" tabIndex={-1} ref={fileInput} onChange={event => { const file = event.target.files?.[0]; event.target.value = ''; if (file) void importRules(file); }} /><p className="section-caption">Profiles bind to this exact architecture fingerprint. A source substitution or reevaluation requires review of that binding.</p><code className="kicad-panel__fingerprint">{fingerprint}</code>
        {rules && rules.fingerprint !== fingerprint && <Notice kind="warning" title="Generated rule files are stale">The architecture changed. Review and import a profile bound to the current fingerprint before downloading rule files.</Notice>}
        {rules && rules.fingerprint === fingerprint && <div className="kicad-panel__rule-result"><strong>{rules.result.files.length} rule sidecars generated</strong><p>Approved bounds only. These files create no PCB and have not been checked on your physical layout.</p><button className="button secondary small" disabled={!readiness.ready} onClick={() => saveProject(rules.result, 'orbitwork-reviewed-rule-sidecars.zip')}><ArrowDownToLine size={13} />Download rule sidecars</button><details className="disclosure"><summary>Rule scope and validation warnings</summary><ul className="plain-list">{rules.result.warnings.map(item => <li key={item}>{item}</li>)}</ul></details></div>}
      </details>
    </section>
    <details className="disclosure"><summary>Catalog evidence and export warnings</summary><ul className="plain-list">{readiness.warnings.map(item => <li key={item}>{item}</li>)}</ul></details>
    {error && <div role="alert"><Notice kind="danger" title="Export needs attention">{error}</Notice></div>}
  </Sheet>;
}
