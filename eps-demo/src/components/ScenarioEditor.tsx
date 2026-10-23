import { useEffect, useId, useRef, useState } from 'react';
import type { CSSProperties, JSX, KeyboardEvent, PointerEvent } from 'react';
import { Activity, ChevronDown, CircleHelp, GripVertical, ListFilter, Moon, Plus, ShieldCheck, SlidersHorizontal, Sun, Trash2 } from 'lucide-react';
import type { Load, LoadWindow, OrbitResult, Scenario } from '../types';
import {
  bounded, dutyFraction, MIN_WINDOW_FRACTION, moveWindow, nextWindow, normalizeWindow,
  phasePercent, phaseTime, powerPreview, resizeWindow, WINDOW_STEP, windowLanes,
} from './scenario-model';
import './scenario-editor.css';

type EditMode = 'move' | 'start' | 'end';
type ChangeLoad = (id: string, update: (load: Load) => Load) => void;
type ChangeWindow = (loadId: string, id: string, update: (window: LoadWindow) => LoadWindow) => void;
interface Drag {
  scenarioId: string;
  loadId: string;
  windowId: string;
  mode: EditMode;
  original: LoadWindow;
  pointerId: number;
  originX: number;
  width: number;
  target: HTMLElement;
}

function numberText(value: number): string { return String(Number(value.toFixed(4))); }
function newId(prefix: string): string {
  return `${prefix}-${globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`}`;
}

/** Local drafts allow clearing/retyping. Only finite, bounded values reach the parent. */
export function ScenarioNumberField({ label, accessibleLabel, value, min = 0, max, step = 0.1, unit, integer, onCommit }: {
  label: string; accessibleLabel?: string; value: number; min?: number; max?: number;
  step?: number; unit?: string; integer?: boolean; onCommit: (value: number) => void;
}): JSX.Element {
  const [draft, setDraft] = useState(numberText(value));
  const [message, setMessage] = useState('');
  const dirty = useRef(false);
  const messageId = useId();
  useEffect(() => { dirty.current = false; setDraft(numberText(value)); setMessage(''); }, [value]);
  const commit = () => {
    if (!dirty.current) return;
    dirty.current = false;
    const parsed = draft.trim() === '' ? NaN : Number(draft);
    if (!Number.isFinite(parsed)) {
      setDraft(numberText(value));
      setMessage('Enter a finite number. Previous value kept.');
      return;
    }
    const rounded = integer ? Math.round(parsed) : parsed;
    const next = bounded(rounded, min, max ?? Number.MAX_SAFE_INTEGER);
    setDraft(numberText(next));
    setMessage(next !== rounded ? `Limited to ${numberText(next)}${unit ? ` ${unit}` : ''}.` : '');
    if (Math.abs(next - value) > 1e-10) onCommit(next);
  };
  return (
    <label className="scenario-number-field">
      <span className="scenario-field-label">{label}</span>
      <span className="scenario-number-wrap">
        <input className="scenario-number-input" type="number" inputMode="decimal"
          aria-label={accessibleLabel ?? label} aria-describedby={message ? messageId : undefined}
          min={min} max={max} step={step} value={draft}
          onChange={(event) => { dirty.current = true; setDraft(event.target.value); setMessage(''); }} onBlur={commit}
          onKeyDown={(event) => {
            if (event.key === 'Enter') { event.preventDefault(); commit(); }
            if (event.key === 'Escape' && dirty.current) {
              event.preventDefault(); dirty.current = false; setDraft(numberText(value)); setMessage('');
            }
          }} />
        {unit && <span className="scenario-input-unit" aria-hidden="true">{unit}</span>}
      </span>
      {message && <span id={messageId} className="scenario-field-message" role="status">{message}</span>}
    </label>
  );
}

const NumberField = ScenarioNumberField;

function PhaseBands({ sunlightFraction }: { sunlightFraction?: number }): JSX.Element {
  return <div className="scenario-phase-bands" aria-hidden="true">
    {sunlightFraction !== undefined && <>
      <span className="scenario-sun-band" style={{ width: `${sunlightFraction * 100}%` }} />
      <span className="scenario-eclipse-band" style={{ left: `${sunlightFraction * 100}%` }} />
      <span className="scenario-phase-boundary" style={{ left: `${sunlightFraction * 100}%` }} />
    </>}
    {[0.25, 0.5, 0.75].map((phase) => <span key={phase} className="scenario-gridline" style={{ left: `${phase * 100}%` }} />)}
  </div>;
}

function TimelineAxis({ periodS, sunlightFraction }: { periodS?: number; sunlightFraction?: number }): JSX.Element {
  return <div className="scenario-axis">
    <div className="scenario-phase-legend">
      {sunlightFraction === undefined
        ? <span>Orbit phase · evaluate orbit for sun/eclipse timing</span>
        : <><span className="scenario-sun-label"><Sun size={12} /> Sunlight {phasePercent(sunlightFraction)}</span>
          <span className="scenario-eclipse-label"><Moon size={12} /> Eclipse {phasePercent(1 - sunlightFraction)}</span></>}
    </div>
    <div className="scenario-axis-ticks">
      {[0, 0.25, 0.5, 0.75, 1].map((phase) => <span key={phase} className="scenario-axis-tick" style={{ left: `${phase * 100}%` }}>
        <span>{phasePercent(phase)}</span>{periodS !== undefined && <small>{phaseTime(phase, periodS)}</small>}
      </span>)}
    </div>
  </div>;
}

export function PowerPreview({ loads, sunlightFraction, expanded = false }: { loads: Load[]; sunlightFraction?: number; expanded?: boolean }): JSX.Element {
  const { segments, averageW, peakW } = powerPreview(loads);
  const ceiling = Math.max(1, peakW * 1.15);
  const x = (phase: number) => 40 + phase * 920;
  const y = (powerW: number) => 98 - powerW / ceiling * 76;
  const line = segments.map((segment, index) => `${index === 0 ? 'M' : 'L'} ${x(segment.start)} ${y(segment.powerW)} L ${x(segment.end)} ${y(segment.powerW)}`).join(' ');
  const fill = `M 40 98 ${line.replace(/^M/, 'L')} L 960 98 Z`;
  const titleId = useId();
  return <details open={expanded || undefined} className="scenario-preview" aria-label="Instantaneous load power preview">
    <summary className="scenario-preview-summary">
      <span><Activity size={14} /> Aggregate power preview</span>
      <span className="scenario-preview-toggle">Load boundary <ChevronDown className="scenario-details-chevron" size={14} /></span>
    </summary>
    <svg className="scenario-power-svg" viewBox="0 0 1000 125" role="img" aria-labelledby={titleId}>
      <title id={titleId}>{`Exact instantaneous load demand. Average ${averageW.toFixed(2)} W, peak ${peakW.toFixed(2)} W. Active power replaces idle power.`}</title>
      {sunlightFraction !== undefined && <>
        <rect x="40" y="14" width={sunlightFraction * 920} height="84" className="scenario-svg-sun" />
        <rect x={x(sunlightFraction)} y="14" width={(1 - sunlightFraction) * 920} height="84" className="scenario-svg-eclipse" />
      </>}
      {[0, 0.5, 1].map((fraction) => <g key={fraction}>
        <line x1="40" x2="960" y1={y(fraction * ceiling)} y2={y(fraction * ceiling)} className="scenario-svg-grid" />
        <text x="32" y={y(fraction * ceiling) + 3} textAnchor="end" className="scenario-svg-label">{(fraction * ceiling).toFixed(1)}</text>
      </g>)}
      {[0, 0.25, 0.5, 0.75, 1].map((phase) => <g key={phase}>
        <line x1={x(phase)} x2={x(phase)} y1="14" y2="98" className="scenario-svg-grid" />
        <text x={x(phase)} y="117" textAnchor={phase === 0 ? 'start' : phase === 1 ? 'end' : 'middle'} className="scenario-svg-label">{phasePercent(phase)}</text>
      </g>)}
      <path d={fill} className="scenario-svg-area" />
      <line x1="40" x2="960" y1={y(averageW)} y2={y(averageW)} className="scenario-svg-average" />
      <path d={line} className="scenario-svg-demand" />
    </svg>
    <p className="scenario-preview-caption">Load boundary only. Excludes EPS losses and generation. Overlapping windows count once.</p>
  </details>;
}

function LoadEditor({ load, periodS, sunlightFraction, helpId, drag, onLoad, onWindow, onRemove, onBeginDrag, onWindowKey }: {
  load: Load; periodS?: number; sunlightFraction?: number; helpId: string; drag: Drag | null;
  onLoad: ChangeLoad; onWindow: ChangeWindow; onRemove: () => void;
  onBeginDrag: (event: PointerEvent<HTMLButtonElement>, load: Load, window: LoadWindow, mode: EditMode) => void;
  onWindowKey: (event: KeyboardEvent<HTMLButtonElement>, load: Load, window: LoadWindow, mode: EditMode) => void;
}): JSX.Element {
  const [numericOpen, setNumericOpen] = useState(false);
  const duty = dutyFraction(load.windows);
  const layout = windowLanes(load.windows);
  const freeWindow = nextWindow(load.windows);
  const label = load.name.trim() || 'Unnamed load';
  const color = /^#[\da-f]{6}$/i.test(load.color) ? load.color : '#80b7c8';
  return <article className="scenario-load" style={{ '--scenario-load-color': color } as CSSProperties} aria-label={`${label} load`}>
    <div className="scenario-load-header">
      <label className="scenario-color-picker" title={`Timeline color for ${label}`}>
        <span className="scenario-color-dot" />
        <input className="scenario-color-input" type="color" value={color} aria-label={`${label} timeline color`}
          onChange={(event) => onLoad(load.id, (current) => ({ ...current, color: event.target.value }))} />
      </label>
      <label className="scenario-load-name-field"><span className="scenario-sr-only">Load name</span>
        <input className="scenario-load-name" aria-label={`${label} load name`} value={load.name}
          onChange={(event) => onLoad(load.id, (current) => ({ ...current, name: event.target.value }))} />
      </label>
      <label className="scenario-subsystem-field"><span className="scenario-sr-only">Subsystem</span>
        <input className="scenario-subsystem" aria-label={`${label} subsystem`} value={load.subsystem} placeholder="Subsystem"
          onChange={(event) => onLoad(load.id, (current) => ({ ...current, subsystem: event.target.value }))} />
      </label>
      <label className={`scenario-essential ${load.essential ? 'scenario-essential-on' : ''}`} title="Service-priority label only. No automatic shedding.">
        <input className="scenario-checkbox" type="checkbox" checked={load.essential} aria-label={`${label} essential load`}
          onChange={(event) => onLoad(load.id, (current) => ({ ...current, essential: event.target.checked }))} />
        <ShieldCheck size={13} aria-hidden="true" /> Essential
      </label>
      <button type="button" className="scenario-icon-button scenario-delete" aria-label={`Remove ${label} load`} title={`Remove ${label}`} onClick={onRemove}><Trash2 size={14} /></button>
    </div>
    <div className="scenario-load-workbench">
      <div className="scenario-load-fields">
        <NumberField label="Active" accessibleLabel={`${label} active power (W)`} unit="W" value={load.activePowerW}
          onCommit={(value) => onLoad(load.id, (current) => ({ ...current, activePowerW: value }))} />
        <NumberField label="Idle" accessibleLabel={`${label} idle power (W)`} unit="W" value={load.idlePowerW}
          onCommit={(value) => onLoad(load.id, (current) => ({ ...current, idlePowerW: value }))} />
        <NumberField label="Rail" accessibleLabel={`${label} rail voltage (V)`} min={0.001} unit="V" value={load.railV}
          onCommit={(value) => onLoad(load.id, (current) => ({ ...current, railV: value }))} />
      </div>
      <div className="scenario-timeline-cell">
        <div className="scenario-lane" data-scenario-track="true" style={{ height: `${layout.count * 28 + 6}px` }} aria-label={`${label} orbit timeline`}>
          <PhaseBands sunlightFraction={sunlightFraction} />
          {load.windows.length === 0 && <span className="scenario-idle-label">Idle for the full orbit</span>}
          {load.windows.map((authored, index) => {
            const window = normalizeWindow(authored);
            const activeDrag = drag?.loadId === load.id && drag.windowId === window.id;
            const shortWindow = window.end - window.start <= 0.065;
            const rangeLabel = `${phasePercent(window.start)} to ${phasePercent(window.end)} of orbit`;
            return <div key={window.id} className={`scenario-window ${shortWindow ? 'scenario-window-short' : ''} ${activeDrag ? 'scenario-window-dragging' : ''}`}
              style={{ left: `${window.start * 100}%`, width: `${(window.end - window.start) * 100}%`, top: `${4 + (layout.lanes.get(window.id) ?? 0) * 28}px` }}>
              <button type="button" className="scenario-window-move" role="slider" aria-label={`Move ${label} window ${index + 1}`}
                aria-orientation="horizontal" aria-valuemin={0} aria-valuemax={Number(((1 - window.end + window.start) * 100).toFixed(3))}
                aria-valuenow={Number((window.start * 100).toFixed(3))} aria-valuetext={rangeLabel} aria-describedby={helpId}
                title={`${rangeLabel}. Drag to move. Arrow keys also work.`}
                onPointerDown={(event) => onBeginDrag(event, load, window, 'move')}
                onKeyDown={(event) => onWindowKey(event, load, window, 'move')}>
                <span className="scenario-window-label">{shortWindow ? <GripVertical size={12} /> : <>{window.end - window.start > 0.18 && <GripVertical size={11} />}{phasePercent(window.end - window.start)}</>}</span>
              </button>
              {(['start', 'end'] as const).map((edge) => <button type="button" key={edge} className={`scenario-window-handle scenario-window-handle-${edge}`} role="slider"
                aria-label={`${edge === 'start' ? 'Start' : 'End'} of ${label} window ${index + 1}`} aria-orientation="horizontal"
                aria-valuemin={edge === 'start' ? 0 : Number(((window.start + MIN_WINDOW_FRACTION) * 100).toFixed(3))}
                aria-valuemax={edge === 'start' ? Number(((window.end - MIN_WINDOW_FRACTION) * 100).toFixed(3)) : 100}
                aria-valuenow={Number((window[edge] * 100).toFixed(3))} aria-valuetext={phasePercent(window[edge])} aria-describedby={helpId}
                title={`Resize ${edge}: ${phasePercent(window[edge])}`}
                onPointerDown={(event) => onBeginDrag(event, load, window, edge)}
                onKeyDown={(event) => onWindowKey(event, load, window, edge)}><span /></button>)}
            </div>;
          })}
        </div>
        <div className="scenario-duty-line"><span><strong>{phasePercent(duty)}</strong> duty</span>
          <span>{periodS !== undefined ? `${(duty * periodS / 60).toFixed(1)} min active` : 'of one orbit'}<span className="scenario-duty-separator">·</span>{(load.idlePowerW + (load.activePowerW - load.idlePowerW) * duty).toFixed(2)} W avg</span>
        </div>
      </div>
    </div>
    <div className="scenario-window-tools">
      <details className="scenario-numeric-details" open={numericOpen} onToggle={(event) => setNumericOpen(event.currentTarget.open)}>
        <summary className="scenario-numeric-summary"><ListFilter size={13} /><span>Numeric windows</span><span className="scenario-window-count">{load.windows.length}</span><ChevronDown className="scenario-details-chevron" size={13} /></summary>
        <div className="scenario-numeric-list">
          {load.windows.length === 0 && <p className="scenario-empty-windows">No active windows. Idle power still applies. Add a window to schedule active power.</p>}
          {load.windows.map((window, index) => <div className="scenario-numeric-row" key={window.id}>
            <span className="scenario-window-number">{String(index + 1).padStart(2, '0')}</span>
            <NumberField label="Start" accessibleLabel={`${label} window ${index + 1} start (%)`} value={window.start * 100}
              max={(window.end - MIN_WINDOW_FRACTION) * 100} unit="%" step={0.1}
              onCommit={(value) => onWindow(load.id, window.id, (current) => resizeWindow(current, 'start', value / 100))} />
            <NumberField label="End" accessibleLabel={`${label} window ${index + 1} end (%)`} value={window.end * 100}
              min={(window.start + MIN_WINDOW_FRACTION) * 100} max={100} unit="%" step={0.1}
              onCommit={(value) => onWindow(load.id, window.id, (current) => resizeWindow(current, 'end', value / 100))} />
            <span className="scenario-window-duration">{phasePercent(window.end - window.start)}<small>{periodS !== undefined ? `${phaseTime(window.start, periodS)} → ${phaseTime(window.end, periodS)}` : 'orbit duration'}</small></span>
            <button type="button" className="scenario-icon-button scenario-delete" aria-label={`Remove ${label} window ${index + 1}`} title="Remove window"
              onClick={() => onLoad(load.id, (current) => ({ ...current, windows: current.windows.filter((item) => item.id !== window.id) }))}><Trash2 size={13} /></button>
          </div>)}
          <p className="scenario-numeric-hint">Percent of one orbit. Minimum width 0.1%. Overlaps form one active interval. Split a window at 100% to cross the orbit boundary.</p>
        </div>
      </details>
      <button type="button" className="scenario-add-window" aria-label={`Add ${label} window`} disabled={!freeWindow}
        title={freeWindow ? 'Add a window in the largest free interval' : 'The full orbit is active. Resize or remove a window first.'}
        onClick={() => {
          const range = nextWindow(load.windows);
          if (range) { onLoad(load.id, (current) => ({ ...current, windows: [...current.windows, { id: newId('window'), ...range }] })); setNumericOpen(true); }
        }}><Plus size={13} /> Add window</button>
    </div>
  </article>;
}

export function ScenarioEditor({ scenario, orbit, onChange, section = 'all', loadId, windowId }: {
  scenario: Scenario; orbit?: OrbitResult; onChange: (scenario: Scenario) => void;
  section?: 'all' | 'load' | 'power' | 'window' | 'preview'; loadId?: string; windowId?: string;
}): JSX.Element {
  const scenarioRef = useRef(scenario);
  const onChangeRef = useRef(onChange);
  scenarioRef.current = scenario;
  onChangeRef.current = onChange;
  const dragRef = useRef<Drag | null>(null);
  const [drag, setDrag] = useState<Drag | null>(null);
  const [announcement, setAnnouncement] = useState('');
  const helpId = useId();
  const periodS = orbit && Number.isFinite(orbit.periodS) && orbit.periodS > 0 ? orbit.periodS : undefined;
  const sunlightFraction = orbit && Number.isFinite(orbit.sunlightFraction) && orbit.sunlightFraction >= 0 && orbit.sunlightFraction <= 1 ? orbit.sunlightFraction : undefined;
  const demand = powerPreview(scenario.loads);
  const timelineHelp = 'Drag the middle to move a window, or an edge grip to resize. Arrow keys: 1%, Shift + arrow: 0.1%. Home / End: bounds. Escape cancels a drag. Short windows retain their true width and use outboard edge grips. Numeric windows provide exact start and end percentages.';

  const change = (update: (current: Scenario) => Scenario) => {
    const current = scenarioRef.current;
    const updated = update(current);
    if (updated === current) return;
    const next = { ...updated, revision: current.revision + 1 };
    scenarioRef.current = next;
    onChangeRef.current(next);
  };
  const changeLoad: ChangeLoad = (id, update) => change((current) => {
    let changed = false;
    const loads = current.loads.map((load) => {
      if (load.id !== id) return load;
      const next = update(load); changed ||= next !== load; return next;
    });
    return changed ? { ...current, loads } : current;
  });
  const changeWindow: ChangeWindow = (loadId, id, update) => changeLoad(loadId, (load) => {
    let changed = false;
    const windows = load.windows.map((window) => {
      if (window.id !== id) return window;
      const next = update(window);
      if (next.start === window.start && next.end === window.end) return window;
      changed = true; return next;
    });
    return changed ? { ...load, windows } : load;
  });

  // Capture plus window listeners: a drag ends even outside its row, on touch cancel,
  // or when the browser loses focus. Refs also avoid stale controlled-prop closures.
  useEffect(() => {
    const release = () => {
      const active = dragRef.current;
      dragRef.current = null;
      if (active?.target.hasPointerCapture?.(active.pointerId)) active.target.releasePointerCapture(active.pointerId);
      setDrag(null);
    };
    const apply = (event: globalThis.PointerEvent) => {
      const active = dragRef.current;
      if (!active || active.pointerId !== event.pointerId) return;
      if (scenarioRef.current.id !== active.scenarioId) { release(); return; }
      event.preventDefault();
      const delta = Math.round((event.clientX - active.originX) / active.width / WINDOW_STEP) * WINDOW_STEP;
      changeWindow(active.loadId, active.windowId, () => active.mode === 'move'
        ? moveWindow(active.original, delta)
        : resizeWindow(active.original, active.mode, active.original[active.mode] + delta));
    };
    const finish = (event: globalThis.PointerEvent) => {
      const active = dragRef.current;
      if (!active || active.pointerId !== event.pointerId) return;
      if (event.type === 'pointerup') apply(event);
      const load = scenarioRef.current.loads.find((item) => item.id === active.loadId);
      const window = load?.windows.find((item) => item.id === active.windowId);
      if (window) setAnnouncement(`${load?.name} window: ${phasePercent(window.start)} to ${phasePercent(window.end)} of orbit.`);
      release();
    };
    const escape = (event: globalThis.KeyboardEvent) => {
      const active = dragRef.current;
      if (event.key !== 'Escape' || !active) return;
      event.preventDefault();
      changeWindow(active.loadId, active.windowId, () => active.original);
      setAnnouncement('Window edit cancelled. Original timing restored.');
      release();
    };
    window.addEventListener('pointermove', apply, { passive: false });
    window.addEventListener('pointerup', finish);
    window.addEventListener('pointercancel', finish);
    window.addEventListener('blur', release);
    // A drag owns the first Escape before the containing contextual sheet.
    window.addEventListener('keydown', escape, true);
    return () => {
      window.removeEventListener('pointermove', apply);
      window.removeEventListener('pointerup', finish);
      window.removeEventListener('pointercancel', finish);
      window.removeEventListener('blur', release);
      window.removeEventListener('keydown', escape, true);
      const active = dragRef.current;
      dragRef.current = null;
      if (active?.target.hasPointerCapture?.(active.pointerId)) active.target.releasePointerCapture(active.pointerId);
    };
  }, []);

  useEffect(() => {
    const active = dragRef.current;
    if (active && active.scenarioId !== scenario.id) {
      dragRef.current = null;
      if (active.target.hasPointerCapture?.(active.pointerId)) active.target.releasePointerCapture(active.pointerId);
      setDrag(null);
    }
  }, [scenario.id]);

  const beginDrag = (event: PointerEvent<HTMLButtonElement>, load: Load, window: LoadWindow, mode: EditMode) => {
    if (event.button !== 0 || dragRef.current) return;
    const track = event.currentTarget.closest<HTMLElement>('[data-scenario-track]');
    const width = track?.getBoundingClientRect().width;
    if (!width) return;
    event.preventDefault(); event.stopPropagation();
    event.currentTarget.focus({ preventScroll: true });
    const active: Drag = { scenarioId: scenarioRef.current.id, loadId: load.id, windowId: window.id, mode,
      original: { ...window }, pointerId: event.pointerId, originX: event.clientX, width, target: event.currentTarget };
    dragRef.current = active; setDrag(active);
    try { event.currentTarget.setPointerCapture(event.pointerId); } catch { /* Window listeners remain the fallback. */ }
  };
  const windowKey = (event: KeyboardEvent<HTMLButtonElement>, load: Load, window: LoadWindow, mode: EditMode) => {
    if (!['ArrowLeft', 'ArrowRight', 'ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault(); event.stopPropagation();
    const step = event.shiftKey ? WINDOW_STEP : 0.01;
    const delta = ['ArrowLeft', 'ArrowDown'].includes(event.key) ? -step : step;
    let next: LoadWindow;
    if (mode === 'move') next = moveWindow(window, event.key === 'Home' ? -1 : event.key === 'End' ? 1 : delta);
    else next = resizeWindow(window, mode, event.key === 'Home' ? 0 : event.key === 'End' ? 1 : window[mode] + delta);
    changeWindow(load.id, window.id, () => next);
    setAnnouncement(`${load.name} window: ${phasePercent(next.start)} to ${phasePercent(next.end)} of orbit.`);
  };

  if (section !== 'all') {
    const load = scenario.loads.find(l => l.id === loadId);
    const win = load?.windows.find(w => w.id === windowId);
    if (section === 'preview') return <PowerPreview loads={scenario.loads} sunlightFraction={sunlightFraction} expanded />;
    if (!load) return <p>Select a load in the graph.</p>;
    if (section === 'load') return <div className="focused-load">
      <label className="field">Load name<input type="text" aria-label="Load name" value={load.name} onChange={e=>changeLoad(load.id,l=>({...l,name:e.target.value}))}/></label>
      <label className="field">Subsystem<input type="text" aria-label="Load subsystem" value={load.subsystem} onChange={e=>changeLoad(load.id,l=>({...l,subsystem:e.target.value}))}/></label>
      <label className="field">Timeline color<input type="color" aria-label="Load color" value={load.color} onChange={e=>changeLoad(load.id,l=>({...l,color:e.target.value}))}/></label>
      <label className="checkbox-label"><input type="checkbox" checked={load.essential} onChange={e=>changeLoad(load.id,l=>({...l,essential:e.target.checked}))}/>Essential service label</label>
      <p className="body-copy">Service metadata only. Automatic shedding and rail behavior remain unassessed.</p>
      <button className="button secondary" data-action="remove-load" onClick={()=>change(s=>({...s,loads:s.loads.filter(l=>l.id!==load.id)}))}><Trash2 size={14}/>Remove load</button>
    </div>;
    if (section === 'power') return <div className="focused-load"><div className="form-grid">
      <NumberField label="Active power" unit="W" value={load.activePowerW} onCommit={v=>changeLoad(load.id,l=>({...l,activePowerW:v}))}/>
      <NumberField label="Idle power" unit="W" value={load.idlePowerW} onCommit={v=>changeLoad(load.id,l=>({...l,idlePowerW:v}))}/>
      <NumberField label="Rail voltage" unit="V" min={.001} value={load.railV} onCommit={v=>changeLoad(load.id,l=>({...l,railV:v}))}/>
      </div><p>Duty {phasePercent(dutyFraction(load.windows))}. Active power replaces idle power. Overlapping windows count once.</p></div>;
    if (!win) return <p>Select a window in the graph.</p>;
    const laneStyle = {left:`${win.start*100}%`,width:`${(win.end-win.start)*100}%`,top:'7px'};
    return <div className="focused-window scenario-editor">
      <p className="scenario-sr-only" id={helpId}>{timelineHelp}</p><TimelineAxis periodS={periodS} sunlightFraction={sunlightFraction}/>
      <div className="scenario-lane" data-scenario-track="true" style={{height:58}}><PhaseBands sunlightFraction={sunlightFraction}/><div className={`scenario-window ${win.end-win.start<=.065?'scenario-window-short':''} ${drag?'scenario-window-dragging':''}`} style={laneStyle}>
        <button className="scenario-window-move" role="slider" aria-label="Move selected window" aria-valuemin={0} aria-valuemax={(1-win.end+win.start)*100} aria-valuenow={win.start*100} aria-valuetext={`${phasePercent(win.start)} to ${phasePercent(win.end)}`} aria-describedby={helpId} onPointerDown={e=>beginDrag(e,load,win,'move')} onKeyDown={e=>windowKey(e,load,win,'move')}><GripVertical size={14}/></button>
        {(['start','end'] as const).map(edge=><button key={edge} className={`scenario-window-handle scenario-window-handle-${edge}`} role="slider" aria-label={`${edge} of selected window`} aria-valuemin={edge==='start'?0:(win.start+MIN_WINDOW_FRACTION)*100} aria-valuemax={edge==='start'?(win.end-MIN_WINDOW_FRACTION)*100:100} aria-valuenow={win[edge]*100} onPointerDown={e=>beginDrag(e,load,win,edge)} onKeyDown={e=>windowKey(e,load,win,edge)}><span/></button>)}
      </div></div><div className="form-grid">
      <NumberField label="Start" accessibleLabel="Window start (%)" unit="%" value={win.start*100} max={(win.end-MIN_WINDOW_FRACTION)*100} onCommit={v=>changeWindow(load.id,win.id,w=>resizeWindow(w,'start',v/100))}/>
      <NumberField label="End" accessibleLabel="Window end (%)" unit="%" value={win.end*100} min={(win.start+MIN_WINDOW_FRACTION)*100} max={100} onCommit={v=>changeWindow(load.id,win.id,w=>resizeWindow(w,'end',v/100))}/></div>
      <p>{phasePercent(win.end-win.start)} of one orbit{periodS?` · ${phaseTime(win.start,periodS)} to ${phaseTime(win.end,periodS)}`:''}. Arrow keys move or resize. Shift uses 0.1%. Escape cancels a drag.</p>
      <button className="button secondary" data-action="remove-window" onClick={()=>changeLoad(load.id,l=>({...l,windows:l.windows.filter(w=>w.id!==win.id)}))}><Trash2 size={14}/>Remove window</button><div role="status" className="sr-only">{announcement}</div>
    </div>;
  }
  return <section className={`scenario-editor ${drag ? 'scenario-is-dragging' : ''}`} aria-label="Scenario duty cycle editor">
    <header className="scenario-editor-header">
      <div className="scenario-heading-content">
        <h2 className="scenario-title">Load duty cycles <span className="scenario-load-total">{scenario.loads.length} loads</span></h2>
        <div className="scenario-demand-summary" aria-label="Scheduled load demand, excluding EPS losses">
          <span><strong>{demand.averageW.toFixed(2)}</strong> W avg</span>
          <span><strong>{demand.peakW.toFixed(2)}</strong> W peak</span>
          {periodS !== undefined && <span><strong>{(demand.averageW * periodS / 3600).toFixed(2)}</strong> Wh / orbit</span>}
          <span className="scenario-boundary-label">Load boundary</span>
        </div>
      </div>
      <button type="button" className="scenario-button scenario-button-primary" onClick={() => {
        const load: Load = { id: newId('load'), name: `New load ${scenarioRef.current.loads.length + 1}`, subsystem: 'Unassigned', color: '#f28669',
          activePowerW: 1, idlePowerW: 0, railV: 5, essential: false, windows: [{ id: newId('window'), start: 0.2, end: 0.32 }] };
        change((current) => ({ ...current, loads: [...current.loads, load] }));
        setAnnouncement(`${load.name} added with an editable 12% duty window.`);
      }}><Plus size={15} /> Add load</button>
    </header>

    <details className="scenario-settings">
      <summary className="scenario-settings-summary">
        <span className="scenario-settings-title"><SlidersHorizontal size={14} /> Scenario settings <ChevronDown className="scenario-details-chevron" size={13} /></span>
        <span className="scenario-settings-glance">
          <span>Initial energy <strong>{phasePercent(scenario.initialEnergyFraction)}</strong><span className="scenario-glance-divider">/</span><strong>{phasePercent(scenario.minimumEnergyFraction)}</strong> reserve</span>
          <span>Illumination <strong>{numberText(scenario.illuminationFactor)}×</strong></span>
          <span><strong>{scenario.durationOrbits}</strong> {scenario.durationOrbits === 1 ? 'orbit' : 'orbits'}</span>
        </span>
      </summary>
      <div className="scenario-settings-content">
        <div className="scenario-identity">
          <label className="scenario-name-field"><span className="scenario-field-label">Scenario name</span>
            <input className="scenario-input" value={scenario.name} aria-label="Scenario name"
              onChange={(event) => change((current) => ({ ...current, name: event.target.value }))} /></label>
          <label className="scenario-kind-field"><span className="scenario-field-label">Interval type</span>
            <select className="scenario-select" value={scenario.kind} aria-label="Scenario interval type"
              onChange={(event) => change((current) => ({ ...current, kind: event.target.value as Scenario['kind'] }))}>
              <option value="nominal">Nominal repeating</option><option value="survival">Survival interval</option>
            </select></label>
          <span className="scenario-revision">REV {scenario.revision}</span>
        </div>
        <div className="scenario-controls">
          <NumberField label="Initial energy" accessibleLabel="Initial energy fraction (%)" unit="%" value={scenario.initialEnergyFraction * 100} max={100}
            onCommit={(value) => change((current) => ({ ...current, initialEnergyFraction: value / 100 }))} />
          <NumberField label="Energy reserve" accessibleLabel="Minimum energy reserve fraction (%)" unit="%" value={scenario.minimumEnergyFraction * 100} max={100}
            onCommit={(value) => change((current) => ({ ...current, minimumEnergyFraction: value / 100 }))} />
          <NumberField label="Illumination factor" accessibleLabel="Illumination factor" value={scenario.illuminationFactor} max={1} step={0.01} unit="×"
            onCommit={(value) => change((current) => ({ ...current, illuminationFactor: value }))} />
          <NumberField label="Duration" accessibleLabel="Duration in orbits" value={scenario.durationOrbits} min={1} step={1} integer unit="orbits"
            onCommit={(value) => change((current) => ({ ...current, durationOrbits: value }))} />
        </div>
        <p className="scenario-model-note">Energy fractions refer to stored energy, not charge state. Illumination scales sunlight source power. Numeric edits apply on Enter or blur. Escape cancels a draft.</p>
      </div>
    </details>
    {scenario.minimumEnergyFraction > scenario.initialEnergyFraction && <p className="scenario-warning" role="status">Initial energy is below the required energy reserve. This scenario begins in violation.</p>}

    <p className="scenario-sr-only" id={helpId}>{timelineHelp}</p>
    <div className="scenario-timeline-heading">
      <div className="scenario-timeline-caption"><span>POWER STATES <span className="scenario-caption-units">W · V</span></span><small>Active replaces idle</small>
        <details className="scenario-timeline-help"><summary>Timeline help <ChevronDown className="scenario-details-chevron" size={11} /></summary><p>{timelineHelp}</p></details>
      </div>
      <TimelineAxis periodS={periodS} sunlightFraction={sunlightFraction} />
    </div>
    <div className="scenario-load-list">
      {scenario.loads.length === 0 && <div className="scenario-empty"><Activity size={24} /><strong>No loads scheduled</strong><span>Add a load to define its active and idle demand.</span></div>}
      {scenario.loads.map((load) => <LoadEditor key={`${scenario.id}:${load.id}`} load={load} periodS={periodS} sunlightFraction={sunlightFraction}
        helpId={helpId} drag={drag} onLoad={changeLoad} onWindow={changeWindow} onBeginDrag={beginDrag} onWindowKey={windowKey}
        onRemove={() => { change((current) => ({ ...current, loads: current.loads.filter((item) => item.id !== load.id) })); setAnnouncement(`${load.name} removed.`); }} />)}
    </div>

    <PowerPreview loads={scenario.loads} sunlightFraction={sunlightFraction} />

    <details className="scenario-assumptions">
      <summary><CircleHelp size={14} /> Scenario notes & assumptions <ChevronDown className="scenario-details-chevron" size={14} /></summary>
      <div className="scenario-assumptions-content">
        <label className="scenario-notes-field"><span className="scenario-field-label">Scenario description</span>
          <textarea className="scenario-textarea" rows={3} aria-label="Scenario description" value={scenario.description}
            onChange={(event) => change((current) => ({ ...current, description: event.target.value }))} /></label>
        <label className="scenario-notes-field"><span className="scenario-field-label">Provenance / engineering assumptions</span>
          <textarea className="scenario-textarea" rows={3} aria-label="Scenario provenance and assumptions" value={scenario.provenance}
            onChange={(event) => change((current) => ({ ...current, provenance: event.target.value }))} /></label>
        <p className="scenario-scope-note">One orbit repeats for the selected duration. Sunlight starts at phase 0, followed by eclipse. Essential flags and rail voltages are metadata. This editor does not model automatic shedding, recovery, thermal behavior, charge state or hardware qualification.</p>
      </div>
    </details>
    <div className="scenario-assumption-banner"><CircleHelp size={14} /><span>Engineering assumptions, editable and scenario-specific. Example profiles are synthetic, not mission or flight hardware evidence.</span></div>
    <div className="scenario-sr-only" role="status" aria-live="polite" aria-atomic="true">{announcement}</div>
  </section>;
}
