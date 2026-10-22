import { describe, expect, it } from 'vitest';
import { createExampleWorkspace } from './model';
import { parseWorkspace, serializeWorkspace } from './serialization';

 describe('design file boundary', () => {
  it('round trips authored inputs and selections while discarding calculation caches', () => {
    const original = createExampleWorkspace();
    const encoded = serializeWorkspace(original, 'test-revision');
    const restored = parseWorkspace(JSON.parse(encoded));
    expect(restored.inputs).toEqual(original.inputs);
    expect(restored.selections).toEqual(original.selections);
    expect(restored).not.toHaveProperty('analysis');
    expect(JSON.parse(encoded)).toHaveProperty('catalogRevision', 'test-revision');
  });
  it('rejects wrong schemas, invalid quantities and missing structural fields', () => {
    expect(() => parseWorkspace({ schemaVersion: 2 })).toThrow(/schemaVersion/);
    const original = createExampleWorkspace();
    const broken = structuredClone(original) as unknown as { inputs: { battery: { capacityWh: unknown } } };
    broken.inputs.battery.capacityWh = '20';
    expect(() => parseWorkspace(broken)).toThrow(/finite number/);
    expect(() => parseWorkspace({ schemaVersion: 1, inputs: {} })).toThrow();
  });
  it('rejects duplicate window IDs and unknown scenario selection', () => {
    const original = createExampleWorkspace();
    original.inputs.scenarios[0].loads[0].windows = [{ id: 'duplicate', start: 0, end: 0.1 }, { id: 'duplicate', start: 0.2, end: 0.3 }];
    expect(() => parseWorkspace(original)).toThrow(/unique/);
    original.inputs.scenarios[0].loads[0].windows = [];
    original.inputs.activeScenarioId = 'absent';
    expect(() => parseWorkspace(original)).toThrow(/absent/);
  });
  it('reconstructs only known fields and sanitizes timeline colors', () => {
    const original = createExampleWorkspace();
    const raw = JSON.parse(JSON.stringify(original));
    raw.inputs.scenarios[0].loads[0].color = 'url(https://example.com)';
    raw.inputs.__proto__ = { polluted: true };
    const restored = parseWorkspace(raw);
    expect(restored.inputs.scenarios[0].loads[0].color).toBe('#7fa9c6');
    expect(restored.inputs).not.toHaveProperty('polluted');
  });
  it('accepts missing numeric values as null so the graph can request them', () => {
    const original = createExampleWorkspace();
    original.inputs.mission.altitudeKm = null;
    expect(parseWorkspace(original).inputs.mission.altitudeKm).toBeNull();
  });
});
