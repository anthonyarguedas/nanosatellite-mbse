import { describe, expect, it } from 'vitest';
import { acceptAltitude, cosineSimilarity, queryProblem, searchLexical } from './retrieval';
import type { MissionAnalogue, MissionCatalogue, MissionRecord } from './types';

const mission = (id: string, description: string, altitude: number | [number, number] | null = 500): MissionRecord => ({
  id, name: id, identity: `Exact fixture ${id}`, revision: 'test-1', description, descriptionSourceIds: ['test-source'],
  status: 'study', epoch: 'Synthetic test', statusDetail: 'Synthetic fixture only.',
  orbit: { altitudeKm: altitude === null ? null : { value: altitude, sourceIds: ['test-source'], original: String(altitude), meaning: 'Synthetic test value.' }, orbitType: null, inclinationDeg: null },
  sources: [{ id: 'test-source', title: 'Synthetic test evidence', url: 'https://example.com', revision: 'test', location: 'fixture', retrievedAt: '2026-10-17', quotes: ['Synthetic fixture.'] }], caveats: [],
});
const catalogue: MissionCatalogue = { revision: 'test-1', missions: [
  mission('rain', 'Compact radar measures rain precipitation and cloud profiles.'),
  mission('land', 'A camera images vegetation and agriculture on Earth then downlinks pictures.'),
  mission('plasma', 'Receive scattered radar signals from plasma irregularities in the polar ionosphere.', [410, 820]),
] };
const analogue = (record: MissionRecord): MissionAnalogue => ({ mission: record, score: 0.7, method: 'lexical-tfidf', matchedTerms: [], catalogueRevision: 'test-1' });

describe('mission analogue vectors', () => {
  it('calculates cosine, including zero vectors, without returning probabilities', () => {
    expect(cosineSimilarity([1, 0], [1, 0])).toBe(1);
    expect(cosineSimilarity([1, 0], [0, 1])).toBe(0);
    expect(cosineSimilarity([1, 0], [-1, 0])).toBe(-1);
    expect(cosineSimilarity([0, 0], [1, 1])).toBe(0);
    expect(cosineSimilarity([1e300, 0], [1e300, 0])).toBe(1);
    expect(cosineSimilarity([1e-300, 0], [1e-300, 0])).toBe(1);
    expect(() => cosineSimilarity([1], [1, 2])).toThrow();
    expect(() => cosineSimilarity([NaN], [1])).toThrow();
  });
  it('ranks reviewed ConOps by lexical vector cosine and preserves method and revision', () => {
    const result = searchLexical('Measure precipitation and rain cloud profiles with a compact radar in a satellite.', catalogue);
    expect(result.matches[0].mission.id).toBe('rain');
    expect(result.method).toBe('lexical-tfidf');
    expect(result.matches[0].catalogueRevision).toBe('test-1');
    expect(result.matches[0].matchedTerms).toContain('precipitation');
    expect(searchLexical('Measure precipitation and rain cloud profiles with a compact radar in a satellite.', catalogue)).toEqual(result);
  });
  it.each(['', 'Earth', 'satellite mission orbit data', 'Suggest a tomato pasta recipe for dinner with basil and cheese.', 'Monitor CPU servers and optimize database memory consumption.', 'Map Martian vegetation with an imaging camera in Mars orbit.', 'Provide geostationary satellite communications and continuous ground contact.'])('abstains on sparse or unrelated text: %s', query => {
    expect(searchLexical(query, catalogue).matches).toEqual([]);
  });
  it('does not offer zero-overlap results even when a generic space word is present', () => {
    expect(searchLexical('A satellite will bake delicious pizza and prepare tomato pasta for dinner.', catalogue).status).toBe('abstained');
  });
  it('bounds query and result counts', () => {
    expect(queryProblem('Receive short messages from Internet of Things terminals across Morocco and relay them to a ground station.')).toBeNull();
    expect(queryProblem('x'.repeat(2001))).not.toBeNull();
    expect(searchLexical('Measure rain precipitation radar and camera vegetation on Earth.', catalogue, 1).matches.length).toBeLessThanOrEqual(1);
    expect(searchLexical('Measure rain precipitation radar and camera vegetation on Earth.', { revision: 'empty', missions: [] }).status).toBe('abstained');
  });
});

describe('engineer acceptance boundary', () => {
  it('returns the exact sourced scalar and never edits an input object', () => {
    const record = catalogue.missions[0];
    const before = JSON.stringify(record);
    const accepted = acceptAltitude(analogue(record), new Date('2026-10-17T00:00:00Z'));
    expect(accepted.altitudeKm).toBe(500);
    expect(accepted.acceptedAt).toBe('2026-10-17T00:00:00.000Z');
    expect(JSON.stringify(record)).toBe(before);
  });
  it('never averages a range or invents missing altitude', () => {
    expect(() => acceptAltitude(analogue(catalogue.missions[2]))).toThrow(/scalar/);
    expect(() => acceptAltitude(analogue(mission('missing', 'Some activity', null)))).toThrow(/scalar/);
  });
  it('requires resolvable parameter provenance', () => {
    const record = { ...catalogue.missions[0], sources: [] };
    expect(() => acceptAltitude(analogue(record))).toThrow(/source/);
    expect(() => acceptAltitude(analogue(mission('invalid', 'Some activity', Infinity)))).toThrow();
  });
});
