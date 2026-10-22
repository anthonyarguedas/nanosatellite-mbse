import type { DesignInputs, MissionAnalogueReceipt } from '../types';
import type { MissionMatch } from './types';
import { acceptAltitude } from './retrieval';

/** Preserve the accepted evidence without treating its similarity score as a suitability probability. */
export function missionReceipt(match: MissionMatch, query: string): MissionAnalogueReceipt {
  if (query.length > 2000) throw new Error('Mission ConOps must be at most 2000 characters.');
  const reviewed = acceptAltitude(match, new Date(match.acceptedAt));
  if (reviewed.altitudeKm !== match.altitudeKm) throw new Error('The accepted altitude differs from its sourced scalar value.');
  if (reviewed.altitudeKm > 100000) throw new Error('This altitude is outside the circular EPS demo domain.');
  if (!Number.isFinite(match.score) || match.score < -1 || match.score > 1) throw new Error('The analogue cosine score is invalid.');
  const parameter = match.mission.orbit.altitudeKm!;
  return {
    missionId: match.mission.id, missionName: match.mission.name, missionRevision: match.mission.revision,
    missionStatus: match.mission.status, missionEpoch: match.mission.epoch, catalogueRevision: match.catalogueRevision,
    method: match.method, cosine: match.score, altitudeKm: match.altitudeKm,
    parameterOriginal: parameter.original, parameterMeaning: parameter.meaning, parameterSourceIds: [...parameter.sourceIds],
    acceptedAt: reviewed.acceptedAt, query,
    sources: match.mission.sources.map(source => ({ id: source.id, title: source.title, url: source.url, revision: source.revision, location: source.location, retrievedAt: source.retrievedAt })),
  };
}

export function applyMissionAnalogue(inputs: DesignInputs, match: MissionMatch, query: string): DesignInputs {
  return { ...inputs, mission: { ...inputs.mission, altitudeKm: match.altitudeKm, conOps: query, orbitSuggestion: missionReceipt(match, query) } };
}
