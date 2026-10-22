import { cosineSimilarity, missionSearchText, queryProblem, tokenize } from './retrieval';
import type { MissionAnalogue, MissionCatalogue, MissionSearchResult } from './types';

export const SEMANTIC_ENDPOINT = 'http://127.0.0.1:8767/embed';
export const QWEN_MODEL = 'Qwen/Qwen3-Embedding-0.6B';
export const QWEN_REVISION = '97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3';

export async function searchSemantic(
  query: string,
  catalogue: MissionCatalogue,
  signal?: AbortSignal,
): Promise<MissionSearchResult> {
  const problem = queryProblem(query);
  if (problem) return { status: 'abstained', matches: [], reason: problem, method: 'semantic-qwen' };
  if (!catalogue.missions.length) return { status: 'abstained', matches: [], reason: 'The mission catalogue is empty.', method: 'semantic-qwen' };
  if (catalogue.missions.length > 12) throw new Error('The local demo supports at most twelve reviewed descriptions.');
  const response = await fetch(SEMANTIC_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, documents: catalogue.missions.map(missionSearchText) }),
    signal: signal ? AbortSignal.any([signal, AbortSignal.timeout(120_000)]) : AbortSignal.timeout(120_000),
    credentials: 'omit',
    cache: 'no-store',
  });
  if (!response.ok) throw new Error(`Local semantic service returned ${response.status}.`);
  const data: unknown = await response.json();
  if (!data || typeof data !== 'object') throw new Error('Invalid semantic response.');
  const result = data as Record<string, unknown>;
  const validVector = (value: unknown): value is number[] => Array.isArray(value) && value.length === 1024 && value.every(v => typeof v === 'number' && Number.isFinite(v));
  if (result.model !== QWEN_MODEL || result.revision !== QWEN_REVISION || !validVector(result.queryVector)
    || !Array.isArray(result.documentVectors) || result.documentVectors.length !== catalogue.missions.length
    || !result.documentVectors.every(validVector)) {
    throw new Error('The local service returned an unexpected model, revision or vector shape.');
  }
  const queryVector = result.queryVector;
  const documentVectors = result.documentVectors as number[][];
  const queryTerms = tokenize(query);
  const matches = catalogue.missions.map((mission, index): MissionAnalogue => ({
    mission,
    score: cosineSimilarity(queryVector, documentVectors[index]),
    method: 'semantic-qwen',
    matchedTerms: [...new Set(queryTerms.filter(term => tokenize(missionSearchText(mission)).includes(term)))],
    catalogueRevision: catalogue.revision,
  })).filter(match => match.score >= 0.55)
    .sort((a, b) => b.score - a.score || a.mission.id.localeCompare(b.mission.id)).slice(0, 3);
  return {
    status: matches.length ? 'matches' : 'abstained', matches, method: 'semantic-qwen',
    reason: matches.length ? 'Qwen text embeddings ranked by cosine similarity. Scores are uncalibrated retrieval ranks.'
      : 'No description clears the conservative demo retrieval threshold. No analogue is shown.',
  };
}
