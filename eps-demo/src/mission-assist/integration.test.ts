import { describe, expect, it } from 'vitest';
import missionData from '../data/missions.json';
import { catalog } from '../data/catalog';
import { changeInputs, createExampleWorkspace, evaluateReady } from '../state/model';
import { parseWorkspace, serializeWorkspace } from '../state/serialization';
import { nodeStatuses } from '../workflow';
import { acceptAltitude } from './retrieval';
import { applyMissionAnalogue, missionReceipt } from './integration';
import type { MissionCatalogue } from './types';

const missions = missionData as MissionCatalogue;
const query = 'Demonstrate satellite software and payload experiments while downlinking the observation data.';
function accepted() {
  return acceptAltitude({ mission: missions.missions.find(item => item.id === 'ops-sat-2019')!, score: 0.7, method: 'lexical-tfidf', matchedTerms: [], catalogueRevision: missions.revision }, new Date('2026-10-17T08:00:00Z'));
}

 describe('mission assistance host boundary', () => {
  it('applies only the sourced altitude and acceptance provenance', () => {
    const original = createExampleWorkspace();
    const next = applyMissionAnalogue(original.inputs, accepted(), query);
    expect(next.mission.altitudeKm).toBe(515);
    expect(next.mission.name).toBe(original.inputs.mission.name);
    expect(next.mission.lifetimeYears).toBe(original.inputs.mission.lifetimeYears);
    expect(next.scenarios).toEqual(original.inputs.scenarios);
    expect(next.mission.orbitSuggestion?.parameterOriginal).toBe(accepted().mission.orbit.altitudeKm?.original);
    expect(next.mission.orbitSuggestion?.sources.length).toBeGreaterThan(0);
    expect(original.inputs.mission.altitudeKm).toBe(400);
  });
  it('invalidates every dependent output through the normal workspace mutation', () => {
    const original = evaluateReady(createExampleWorkspace());
    const next = changeInputs(original, inputs => applyMissionAnalogue(inputs, accepted(), query));
    expect(Object.values(nodeStatuses(next)).filter(status => status === 'stale')).toHaveLength(9);
    expect(nodeStatuses(next).scenarios).toBe('complete');
    expect(next.analysis.orbit).toEqual(original.analysis.orbit);
  });
  it('round trips ConOps and accepted source context without trusting analysis caches', () => {
    const original = changeInputs(createExampleWorkspace(), inputs => applyMissionAnalogue(inputs, accepted(), query));
    const restored = parseWorkspace(JSON.parse(serializeWorkspace(original, catalog.revision)));
    expect(restored.inputs.mission).toEqual(original.inputs.mission);
    expect(restored).not.toHaveProperty('analysis');
  });
  it('clears an acceptance receipt when the altitude or ConOps changes manually', () => {
    const original = changeInputs(createExampleWorkspace(), inputs => applyMissionAnalogue(inputs, accepted(), query));
    const changed = changeInputs(original, inputs => { inputs.mission.altitudeKm = 600; return inputs; });
    expect(changed.inputs.mission.orbitSuggestion).toBeUndefined();
    const reworded = changeInputs(original, inputs => { inputs.mission.conOps = 'A different mission concept.'; return inputs; });
    expect(reworded.inputs.mission.orbitSuggestion).toBeUndefined();
    expect(original.inputs.mission.orbitSuggestion).toBeDefined();
  });
  it('rejects mismatched source values and corrupted imported acceptance receipts', () => {
    expect(() => missionReceipt({ ...accepted(), altitudeKm: 999 }, query)).toThrow(/sourced scalar/);
    expect(() => missionReceipt({ ...accepted(), score: NaN }, query)).toThrow(/cosine/);
    const workspace = changeInputs(createExampleWorkspace(), inputs => applyMissionAnalogue(inputs, accepted(), query));
    const raw = JSON.parse(serializeWorkspace(workspace, catalog.revision));
    raw.inputs.mission.altitudeKm = 999;
    expect(() => parseWorkspace(raw)).toThrow(/does not match/);
    raw.inputs.mission.altitudeKm = 515;
    raw.inputs.mission.orbitSuggestion.cosine = 100;
    expect(() => parseWorkspace(raw)).toThrow(/invalid score/);
  });
});
