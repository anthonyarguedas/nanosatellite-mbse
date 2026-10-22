import type { Load, LoadWindow } from '../types';

/** Editor resolution, not a hardware timing limit. Windows never wrap past phase 1. */
export const MIN_WINDOW_FRACTION = 0.001;
export const WINDOW_STEP = 0.001;

export function bounded(value: number, min: number, max: number): number {
  return Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : min;
}

export function normalizeWindow(window: LoadWindow): LoadWindow {
  const start = bounded(window.start, 0, 1 - MIN_WINDOW_FRACTION);
  return { ...window, start, end: bounded(window.end, start + MIN_WINDOW_FRACTION, 1) };
}

export function moveWindow(window: LoadWindow, delta: number): LoadWindow {
  const normalized = normalizeWindow(window);
  const width = normalized.end - normalized.start;
  const start = bounded(normalized.start + delta, 0, 1 - width);
  return { ...normalized, start, end: Math.min(1, start + width) };
}

export function resizeWindow(window: LoadWindow, edge: 'start' | 'end', phase: number): LoadWindow {
  const normalized = normalizeWindow(window);
  return edge === 'start'
    ? { ...normalized, start: bounded(phase, 0, normalized.end - MIN_WINDOW_FRACTION) }
    : { ...normalized, end: bounded(phase, normalized.start + MIN_WINDOW_FRACTION, 1) };
}

/** Merge the union, including touching windows. Authored window identities stay intact. */
export function mergedWindows(windows: LoadWindow[]): { start: number; end: number }[] {
  const sorted = windows
    .filter((window) => Number.isFinite(window.start) && Number.isFinite(window.end) && window.end > window.start)
    .map((window) => ({ start: bounded(window.start, 0, 1), end: bounded(window.end, 0, 1) }))
    .filter((window) => window.end > window.start)
    .sort((a, b) => a.start - b.start);
  const merged: { start: number; end: number }[] = [];
  for (const window of sorted) {
    const last = merged[merged.length - 1];
    if (last && window.start <= last.end) last.end = Math.max(last.end, window.end);
    else merged.push({ ...window });
  }
  return merged;
}

export function dutyFraction(windows: LoadWindow[]): number {
  return bounded(mergedWindows(windows).reduce((sum, window) => sum + window.end - window.start, 0), 0, 1);
}

export function loadPowerAt(load: Load, phase: number): number {
  return load.windows.some((window) => phase >= window.start && phase < window.end)
    ? load.activePowerW
    : load.idlePowerW;
}

export interface PowerSegment { start: number; end: number; powerW: number }

/** Exact event intervals, rather than a sampling approximation of short windows. */
export function powerPreview(loads: Load[]): { segments: PowerSegment[]; averageW: number; peakW: number } {
  const boundaries = [...new Set([0, 1, ...loads.flatMap((load) =>
    mergedWindows(load.windows).flatMap((window) => [window.start, window.end]),
  )])].sort((a, b) => a - b);
  const segments = boundaries.slice(0, -1).map((start, index) => {
    const end = boundaries[index + 1];
    return { start, end, powerW: loads.reduce((sum, load) => sum + loadPowerAt(load, (start + end) / 2), 0) };
  });
  return {
    segments,
    averageW: segments.reduce((sum, segment) => sum + (segment.end - segment.start) * segment.powerW, 0),
    peakW: Math.max(0, ...segments.map((segment) => segment.powerW)),
  };
}

/** Add into the largest free interval. A fully active load has no free interval. */
export function nextWindow(windows: LoadWindow[]): { start: number; end: number } | null {
  const merged = mergedWindows(windows);
  const gaps: { start: number; end: number }[] = [];
  let cursor = 0;
  for (const window of merged) {
    if (window.start > cursor) gaps.push({ start: cursor, end: window.start });
    cursor = window.end;
  }
  if (cursor < 1) gaps.push({ start: cursor, end: 1 });
  const gap = gaps.sort((a, b) => (b.end - b.start) - (a.end - a.start))[0];
  if (!gap || gap.end - gap.start < MIN_WINDOW_FRACTION - 1e-10) return null;
  const width = Math.min(0.12, gap.end - gap.start);
  const start = gap.start + (gap.end - gap.start - width) / 2;
  return { start, end: start + width };
}

/** Overlapping authored windows get separate visual lanes and remain individually editable. */
export function windowLanes(windows: LoadWindow[]): { lanes: Map<string, number>; count: number } {
  const ends: number[] = [];
  const lanes = new Map<string, number>();
  for (const window of [...windows].sort((a, b) => a.start - b.start)) {
    let lane = ends.findIndex((end) => end <= window.start);
    if (lane < 0) lane = ends.length;
    ends[lane] = window.end;
    lanes.set(window.id, lane);
  }
  return { lanes, count: Math.max(1, ends.length) };
}

export function phasePercent(phase: number): string {
  return `${Number((phase * 100).toFixed(1))}%`;
}

export function phaseTime(phase: number, periodS: number): string {
  const seconds = Math.round(phase * periodS);
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
}
