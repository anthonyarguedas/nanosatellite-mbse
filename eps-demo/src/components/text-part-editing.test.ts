import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import { createWorkspace, emptyInputs } from '../state/model';
import { restoreWorkspace, serializeWorkspace } from '../state/serialization';
import { replaceAuthoredPart, textParts } from './flow-tasks';

describe('bounded authored text-node edits', () => {
  it('allows a complete 2,000-character query that survives canonical restoration', () => {
    const workspace = createWorkspace(emptyInputs());
    const query = replaceAuthoredPart('', 0, 'x'.repeat(2000));
    expect(query).toHaveLength(2000);
    workspace.inputs.mission.conOps = query!;
    const restored = restoreWorkspace(JSON.parse(serializeWorkspace(workspace, catalog.revision)));
    expect(restored.inputs.mission.conOps).toBe(query);
  });

  it('rejects an overlong replacement instead of persisting or truncating it', () => {
    expect(replaceAuthoredPart('', 0, 'x'.repeat(2001))).toBeNull();
  });

  it('applies the total limit across all existing text parts', () => {
    const text = 'x'.repeat(2000);
    const parts = textParts(text);
    expect(parts.length).toBeGreaterThan(1);
    for (let index = 0; index < parts.length; index++) {
      expect(replaceAuthoredPart(text, index, parts[index] + 'x')).toBeNull();
      expect(replaceAuthoredPart(text, index, parts[index])).toBe(text);
    }
  });

  it('preserves the untouched Unicode text and whitespace when editing one part', () => {
    const text = 'Satellite 🛰️ notes\n'.repeat(70);
    const parts = textParts(text);
    const expected = [...parts];
    expected[1] = 'Edited notes\n';
    expect(replaceAuthoredPart(text, 1, expected[1])).toBe(expected.join(''));
    expect(parts.join('')).toBe(text);
  });

  it('allows shortening a full field and rejects removed part identities', () => {
    const text = 'x'.repeat(2000);
    expect(replaceAuthoredPart(text, 0, '')).toHaveLength(2000 - textParts(text)[0].length);
    for (const index of [-1, 0.5, NaN, textParts(text).length]) {
      expect(replaceAuthoredPart(text, index, 'replacement')).toBeNull();
    }
  });
});
