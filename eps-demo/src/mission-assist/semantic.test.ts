import { afterEach, describe, expect, it, vi } from 'vitest';
import { searchSemantic, QWEN_MODEL, QWEN_REVISION } from './semantic';
import type { MissionCatalogue } from './types';

const catalogue: MissionCatalogue = { revision: 'fixture', missions: [{
  id: 'radar-fixture', name: 'Synthetic radar', identity: 'Synthetic fixture only', revision: 'test',
  description: 'Measure precipitation profiles with a compact radar.', descriptionSourceIds: [],
  status: 'study', epoch: 'test', statusDetail: 'Synthetic fixture',
  orbit: { altitudeKm: null, orbitType: null, inclinationDeg: null }, sources: [], caveats: [],
}] };
const vector = (axis: number) => Array.from({ length: 1024 }, (_, i) => i === axis ? 1 : 0);
afterEach(() => vi.unstubAllGlobals());

describe('semantic method honesty', () => {
  it('abstains on unrelated input without calling a service', async () => {
    const fetch = vi.fn(); vi.stubGlobal('fetch', fetch);
    expect((await searchSemantic('Suggest a tomato pasta recipe for dinner with basil and cheese.', catalogue)).status).toBe('abstained');
    expect(fetch).not.toHaveBeenCalled();
  });
  it('abstains on an empty catalogue without calling a service', async () => {
    const fetch = vi.fn(); vi.stubGlobal('fetch', fetch);
    expect((await searchSemantic('Measure precipitation clouds with a compact satellite radar.', { revision: 'empty', missions: [] })).status).toBe('abstained');
    expect(fetch).not.toHaveBeenCalled();
  });
  it('calculates actual embedding cosine while preserving semantic method identity', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({
      model: QWEN_MODEL, revision: QWEN_REVISION, queryVector: vector(0), documentVectors: [vector(0)],
    }) }));
    const result = await searchSemantic('Measure precipitation clouds with a compact satellite radar.', catalogue);
    expect(result.method).toBe('semantic-qwen');
    expect(result.matches[0].score).toBe(1);
    expect(result.matches[0].mission.id).toBe('radar-fixture');
  });
  it('withholds unrelated embeddings below the demo threshold', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({
      model: QWEN_MODEL, revision: QWEN_REVISION, queryVector: vector(0), documentVectors: [vector(1)],
    }) }));
    expect((await searchSemantic('Measure precipitation clouds with a compact satellite radar.', catalogue)).status).toBe('abstained');
  });
  it('reports service failure instead of producing lexical results', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('unavailable')));
    await expect(searchSemantic('Measure precipitation clouds with a compact satellite radar.', catalogue)).rejects.toThrow('unavailable');
  });
  it('rejects incorrect model identity and vector shapes', async () => {
    const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ model: QWEN_MODEL, revision: QWEN_REVISION, queryVector: [1], documentVectors: [] }) });
    vi.stubGlobal('fetch', fetch);
    await expect(searchSemantic('Measure precipitation clouds with a compact satellite radar.', catalogue)).rejects.toThrow(/unexpected/);
    expect(JSON.parse(fetch.mock.calls[0][1].body).query).toContain('precipitation');
    expect(fetch.mock.calls[0][0]).toBe('http://127.0.0.1:8767/embed');
    expect(fetch.mock.calls[0][1].credentials).toBe('omit');
  });
});
