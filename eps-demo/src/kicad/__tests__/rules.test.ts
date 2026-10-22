import { describe, expect, it } from 'vitest';
import { buildReviewedKiCadRules, getKiCadArchitectureFingerprint } from '../index';
import type { ApprovedDimension, ReviewedPhysicalRules } from '../index';
import { fixture } from './fixtures';

export function syntheticRules(fingerprint = 'synthetic-architecture'): ReviewedPhysicalRules {
  const d = (minimumMm: number, id: 'EPS-07' | 'EPS-03' | 'EPS-20' = 'EPS-07'): ApprovedDimension => ({ minimumMm,
    requirementIds: [id], sourceIds: ['synthetic'], rationale: 'Arbitrary unit test value, no physical EPS derivation or real approval.',
    derivation: { method: 'Synthetic test only', conditions: 'Synthetic test only', margin: 'Synthetic test only' } });
  return {
    schemaVersion: 1, architectureFingerprint: fingerprint, catalogRevision: 'synthetic-catalog-1', physicalNetlistRevision: 'synthetic-netlist-1',
    approval: { status: 'approved', engineer: 'SYNTHETIC TEST ONLY, no engineering authority', date: '2026-10-17' },
    sources: [{ id: 'synthetic', url: 'https://example.org/synthetic-test', revision: 'test-1', location: 'Unit test, not design evidence' }],
    knownNets: ['EPS_BUS'], fabrication: { sourceIds: ['synthetic'], minimumTrackWidthMm: 0.1, minimumClearanceMm: 0.1,
      minimumViaDiameterMm: 0.4, minimumDrillMm: 0.2, minimumAnnularWidthMm: 0.1, minimumEdgeClearanceMm: 0.1 },
    classes: [{ name: 'EPS_POWER', nets: ['EPS_BUS'], trackWidth: { ...d(0.8), preferredMm: 0.8 }, clearance: d(0.5, 'EPS-03'),
      viaDiameter: { ...d(0.8), preferredMm: 0.8 }, viaDrill: { ...d(0.4), preferredMm: 0.4, maximumMm: 0.4 } }],
    edgeClearance: d(0.5, 'EPS-20'),
  };
}

describe('reviewed EPS to KiCad rule translation', () => {
  it('emits only approved geometric constraints, traceability and explicit routing defaults', () => {
    const rules = syntheticRules();
    const result = buildReviewedKiCadRules(rules, rules.architectureFingerprint);
    const dru = result.files.find(f => f.name.endsWith('.kicad_dru'))!.content;
    expect(dru).toContain('(version 1)');
    expect(dru).toContain('(constraint track_width (min 0.8mm) (opt 0.8mm))');
    expect(dru).toContain('(constraint hole_size (min 0.4mm) (opt 0.4mm) (max 0.4mm))');
    expect(dru).toContain("A.Type == 'Via'");
    expect(dru).toContain("B.NetName == 'EPS_BUS'");
    expect(dru).not.toContain('(constraint via_drill');
    expect(dru).toContain('EPS-07 | sources: synthetic');
    const manifest = JSON.parse(result.files.find(f => f.name === 'physical-rules-manifest.json')!.content);
    expect(manifest.rules).toHaveLength(5);
    expect(manifest.generatedBoard).toBe(false);
    expect(manifest.ruleApplicationValidated).toBe(false);
    expect(buildReviewedKiCadRules(rules, rules.architectureFingerprint)).toEqual(result);
  });
  it('fingerprints inputs, allocations, quantities and selected catalog revisions', () => {
    const { workspace, catalog } = fixture();
    const first = getKiCadArchitectureFingerprint(workspace, catalog);
    catalog.products[0].revision = 'changed';
    expect(getKiCadArchitectureFingerprint(workspace, catalog)).not.toBe(first);
    expect(() => buildReviewedKiCadRules(syntheticRules(first), 'changed')).toThrow(/stale/);
  });
  it('gates unapproved or unsourced values and missing derivation conditions', () => {
    const r = syntheticRules();
    r.approval.engineer = '';
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/approval/);
    r.approval.engineer = 'Test';
    r.classes[0].trackWidth.sourceIds = ['missing'];
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/sources/);
    r.classes[0].trackWidth.sourceIds = ['synthetic'];
    r.classes[0].trackWidth.derivation.conditions = '';
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/conditions/);
  });
  it('gates geometry inconsistent with fabrication bounds or the maximum drill', () => {
    const r = syntheticRules();
    r.classes[0].trackWidth.minimumMm = 0.01;
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/fabrication/);
    r.classes[0].trackWidth.minimumMm = 0.8;
    delete r.classes[0].viaDrill.maximumMm;
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/maximum drill/);
    r.classes[0].viaDrill.maximumMm = 0.7;
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/annular/);
  });
  it('rejects ambiguous, unknown and overlapping net assignments', () => {
    const r = syntheticRules();
    r.classes[0].nets = ['EPS_*'];
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/unknown|unsupported/);
    r.classes[0].nets = ['MISSING'];
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/unknown/);
    r.classes[0].nets = ['EPS_BUS', 'EPS_BUS'];
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/overlapping/);
  });
  it('rejects net-name and source-ID control characters', () => {
    const r = syntheticRules();
    r.knownNets = ['EPS_BUS\n'];
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/literal names/);
    r.knownNets = ['EPS_BUS'];
    r.sources[0].id = 'synthetic\n(rule injected';
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/safe ID/);
  });
  it('rejects structurally incomplete imported JSON with an actionable gate', () => {
    for (const raw of [null, {}, { sources: [] }, { ...syntheticRules(), classes: [null] }]) {
      expect(() => buildReviewedKiCadRules(raw as unknown as ReviewedPhysicalRules, 'synthetic-architecture')).toThrow(/KiCad physical rules blocked/);
    }
    const r = syntheticRules();
    delete (r.classes[0].trackWidth as Partial<ApprovedDimension>).requirementIds;
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/requirement references/);
  });
  it('requires every fabrication minimum rather than allowing absent values to become NaN', () => {
    const r = syntheticRules();
    delete (r.fabrication as Partial<ReviewedPhysicalRules['fabrication']>).minimumTrackWidthMm;
    expect(() => buildReviewedKiCadRules(r, r.architectureFingerprint)).toThrow(/minimumTrackWidthMm/);
  });
  it('orders overlapping clearance rules so the larger explicit minimum wins', () => {
    const r = syntheticRules();
    r.knownNets.push('AUX');
    r.classes.push({ ...structuredClone(r.classes[0]), name: 'AUX_POWER', nets: ['AUX'], clearance: { ...r.classes[0].clearance, minimumMm: 0.75 } });
    const dru = buildReviewedKiCadRules(r, r.architectureFingerprint).files[0].content;
    expect(dru.indexOf('EPS_POWER_clearance')).toBeLessThan(dru.indexOf('AUX_POWER_clearance'));
  });
  it('retains unresolved net assignments and external assessment scope', () => {
    const r = syntheticRules();
    r.knownNets.push('UNASSIGNED');
    const result = buildReviewedKiCadRules(r, r.architectureFingerprint);
    expect(result.warnings.join(' ')).toContain('UNASSIGNED');
    expect(result.scope).toContain('No current-to-width');
  });
});
