import type { MissionAnalogue, MissionCatalogue, MissionMatch, MissionRecord, MissionSearchResult } from './types';

const STOP_WORDS = new Set(('a an and are as at be by can do for from has have how i in into is it its of on or our that the their them they this to use using we will with would want need satellite satellites spacecraft mission missions orbit orbital data collect collection study studies observe observation operations concept').split(' '));

/** Simple English token normalization. This is lexical processing, not an embedding model. */
export function tokenize(text: string): string[] {
  return (text.toLowerCase().normalize('NFKD').match(/[a-z0-9]+/g) ?? [])
    .filter(token => token.length > 2 && !STOP_WORDS.has(token))
    .map(token => token.length > 5 && token.endsWith('ies') ? `${token.slice(0, -3)}y`
      : token.length > 5 && token.endsWith('ing') ? token.slice(0, -3)
        : token.length > 4 && token.endsWith('s') && !token.endsWith('ss') ? token.slice(0, -1) : token);
}

export function missionSearchText(mission: MissionRecord): string {
  // Orbit numbers and heritage do not improve the rank. Search the reviewed ConOps only.
  return `${mission.name}. ${mission.description}`;
}

export function queryProblem(query: string): string | null {
  if (!query.trim()) return 'Describe the mission objective, payload and intended operations first.';
  if (query.length > 2000) return 'Use at most 2,000 characters for this bounded demo.';
  if (query.trim().length < 24 || new Set(tokenize(query)).size < 3) {
    return 'Add a concrete objective and payload or activity. This description is too sparse.';
  }
  // Explicit regimes outside this Earth LEO catalogue must not inherit its altitudes.
  if (/\b(mars|martian|moon|lunar|cislunar|venus|jupiter|saturn|heliocentric|interplanetary|geostationary|geosynchronous|geo)\b/i.test(query)) {
    return 'This bounded catalogue and EPS model cover low Earth orbit. The requested orbital context needs independent mission analysis.';
  }
  // Conservative scope gate for this small English catalogue. It is an authored heuristic.
  if (!/\b(satellites?|spacecraft|orbit\w*|earth|imaging|camera|vegetation|climate|clouds?|rain\w*|radar|radiomet\w*|weather|plasma|ionosph\w*|astronom\w*|stars?|stellar|exoplanet\w*|ships?|maritime|ais|aviation|aircraft|ads[-\s]?b|iot|internet\s+of\s+things|ground\s+station|crops?|agricultur\w*|multispectral|land\s+cover|telemetry|remote\s+sens\w*|intersatellite)\b/i.test(query)) {
    return 'No clear topic covered by this mission catalogue. Add a space mission objective, or use independent mission analysis.';
  }
  return null;
}

export function cosineSimilarity(a: readonly number[], b: readonly number[]): number {
  if (!a.length || a.length !== b.length || !a.every(Number.isFinite) || !b.every(Number.isFinite)) {
    throw new Error('Embedding vectors must have equal nonzero dimensions and finite values.');
  }
  let scaleA = 0;
  let scaleB = 0;
  for (let i = 0; i < a.length; i++) {
    scaleA = Math.max(scaleA, Math.abs(a[i])); scaleB = Math.max(scaleB, Math.abs(b[i]));
  }
  if (!scaleA || !scaleB) return 0;
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    const x = a[i] / scaleA;
    const y = b[i] / scaleB;
    dot += x * y; normA += x ** 2; normB += y ** 2;
  }
  return Math.max(-1, Math.min(1, dot / Math.sqrt(normA * normB)));
}

function abstain(reason: string, method: MissionSearchResult['method']): MissionSearchResult {
  return { status: 'abstained', matches: [], reason, method };
}

/** Reproducible, offline TF-IDF vector cosine search. No semantic claim. */
export function searchLexical(query: string, catalogue: MissionCatalogue, limit = 3): MissionSearchResult {
  const problem = queryProblem(query);
  if (problem) return abstain(problem, 'lexical-tfidf');
  const documents = catalogue.missions.map(mission => tokenize(missionSearchText(mission)));
  const terms = [...new Set(documents.flat())].sort();
  const documentFrequency = new Map(terms.map(term => [term, documents.filter(doc => doc.includes(term)).length]));
  const vector = (tokens: string[]) => terms.map(term => {
    const count = tokens.filter(token => token === term).length;
    return count ? (1 + Math.log(count)) * (1 + Math.log((documents.length + 1) / (1 + (documentFrequency.get(term) ?? 0)))) : 0;
  });
  const queryTokens = tokenize(query);
  if (!terms.length) return abstain('The mission catalogue is empty.', 'lexical-tfidf');
  const queryVector = vector(queryTokens);
  const matches = catalogue.missions.map((mission, index): MissionAnalogue => ({
    mission,
    score: cosineSimilarity(queryVector, vector(documents[index])),
    method: 'lexical-tfidf',
    matchedTerms: [...new Set(queryTokens.filter(term => documents[index].includes(term)))],
    catalogueRevision: catalogue.revision,
  })).filter(match => match.score >= 0.16 && match.matchedTerms.length >= 2)
    .sort((a, b) => b.score - a.score || a.mission.id.localeCompare(b.mission.id))
    .slice(0, Math.max(0, Math.min(5, limit)));
  return matches.length ? {
    status: 'matches', matches, method: 'lexical-tfidf',
    reason: 'Shared words in reviewed mission descriptions. Scores rank this catalogue only.',
  } : abstain('Insufficient shared mission detail. No analogue is shown. Rephrase the objective or expand the reviewed catalogue.', 'lexical-tfidf');
}

/** Converts one reviewed scalar into an application event. Ranges are never averaged. */
export function acceptAltitude(analogue: MissionAnalogue, now = new Date()): MissionMatch {
  const parameter = analogue.mission.orbit.altitudeKm;
  const altitudeKm = parameter?.value;
  if (typeof altitudeKm !== 'number' || !Number.isFinite(altitudeKm) || altitudeKm <= 0 || !parameter?.sourceIds.length) {
    throw new Error('A sourced scalar altitude is required. Ranges and missing values need separate orbit analysis.');
  }
  if (!parameter.sourceIds.every(id => analogue.mission.sources.some(source => source.id === id))) {
    throw new Error('The altitude source is absent from the mission record.');
  }
  return { ...analogue, altitudeKm, acceptedAt: now.toISOString() };
}
