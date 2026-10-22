import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { createElement } from 'react';
import catalogueData from '../data/missions.json';
import { MissionAssist, MISSION_QUERY_EXAMPLES } from './MissionAssist';
import { searchLexical } from './retrieval';
import type { MissionCatalogue } from './types';

const catalogue = catalogueData as MissionCatalogue;

describe('reviewed mission catalogue', () => {
  it('is a bounded, uniquely identified revisioned catalogue', () => {
    expect(catalogue.revision.length).toBeGreaterThan(0);
    expect(catalogue.missions.length).toBeGreaterThanOrEqual(6);
    expect(catalogue.missions.length).toBeLessThanOrEqual(10);
    expect(new Set(catalogue.missions.map(mission => mission.id)).size).toBe(catalogue.missions.length);
  });
  it('retains sources, quotes, context, epochs and explicit missing fields', () => {
    for (const mission of catalogue.missions) {
      expect(mission.identity.length).toBeGreaterThan(10);
      expect(mission.epoch.length).toBeGreaterThan(4);
      expect(['flown', 'study']).toContain(mission.status);
      expect(mission.statusDetail.length).toBeGreaterThan(10);
      expect(mission.revision.length).toBeGreaterThan(0);
      expect(mission.descriptionSourceIds.length).toBeGreaterThan(0);
      expect(Object.keys(mission.orbit).sort()).toEqual(['altitudeKm', 'inclinationDeg', 'orbitType']);
      const sourceIds = mission.sources.map(source => source.id);
      expect(new Set(sourceIds).size).toBe(sourceIds.length);
      for (const source of mission.sources) {
        expect(source.url).toMatch(/^https:\/\//);
        expect(source.location.length).toBeGreaterThan(0);
        expect(source.revision.length).toBeGreaterThan(0);
        expect(source.retrievedAt).toMatch(/^\d{4}-\d{2}-\d{2}/);
        expect(source.quotes.length).toBeGreaterThan(0);
      }
      for (const id of mission.descriptionSourceIds) expect(sourceIds).toContain(id);
      for (const field of Object.values(mission.orbit)) {
        if (field === null) continue;
        expect(field.sourceIds.length).toBeGreaterThan(0);
        expect(field.original.length).toBeGreaterThan(0);
        expect(field.meaning.length).toBeGreaterThan(10);
        for (const id of field.sourceIds) expect(sourceIds).toContain(id);
      }
      const altitude = mission.orbit.altitudeKm?.value;
      if (Array.isArray(altitude)) {
        expect(altitude.length).toBe(2);
        expect(altitude.every(Number.isFinite)).toBe(true);
        expect(altitude[0]).toBeGreaterThan(0);
        expect(altitude[1]).toBeGreaterThanOrEqual(altitude[0]);
      } else if (altitude !== undefined) {
        expect(Number.isFinite(altitude)).toBe(true);
        expect(altitude).toBeGreaterThan(0);
      }
    }
  });
  it('separates the sourced RAX-2 flight interval from MBSE simulation values', () => {
    const rax = catalogue.missions.find(mission => mission.name === 'RAX-2');
    expect(rax?.status).toBe('flown');
    expect(rax?.orbit.altitudeKm?.value).toEqual([410, 820]);
    expect(rax?.orbit.inclinationDeg?.value).toBe(101.5);
  });
  it('uses explicit JPL orbit evidence for ASTERIA without inferring an ISS orbit', () => {
    const asteria = catalogue.missions.find(mission => mission.name === 'ASTERIA');
    expect(asteria?.orbit.altitudeKm?.value).toBe(400);
    expect(asteria?.orbit.inclinationDeg?.value).toBe(51.6);
    expect(asteria?.orbit.altitudeKm?.sourceIds).toContain('jpl-asteria-telecom-2019');
    expect(asteria?.orbit.altitudeKm?.meaning).toContain('Approximate');
  });
  it('labels the UM5-SAT orbit as a design case and keeps exact scalar value', () => {
    const um5 = catalogue.missions.find(mission => mission.id === 'um5-sat-2025-study');
    expect(um5?.status).toBe('study');
    expect(um5?.orbit.altitudeKm?.value).toBe(550);
  });
  it.each([
    ['Vegetation imaging', 'proba-v'],
    ['Ionosphere radar', 'rax-2'],
    ['Rainfall radar', 'raincube'],
  ])('matches the authored %s example through honestly labeled lexical vectors', (label, expected) => {
    const example = MISSION_QUERY_EXAMPLES.find(item => item.label === label)!;
    const result = searchLexical(example.text, catalogue);
    expect(result.matches[0]?.mission.name.toLowerCase()).toContain(expected);
    expect(result.method).toBe('lexical-tfidf');
  });
  it('abstains on the authored unrelated example', () => {
    const example = MISSION_QUERY_EXAMPLES.find(item => item.label === 'Unrelated input')!;
    expect(searchLexical(example.text, catalogue).status).toBe('abstained');
  });
  it('renders the component without searching or exposing a recommendation', () => {
    let applications = 0;
    const html = renderToStaticMarkup(createElement(MissionAssist, { onApply: () => applications++ }));
    expect(html).toContain('Start from your ConOps');
    expect(html).toContain('Lexical TF-IDF');
    expect(html).toContain('Similarity is an uncalibrated rank');
    expect(html).not.toContain('Accept 550 km');
    expect(applications).toBe(0);
  });
});
