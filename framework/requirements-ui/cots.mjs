import { readFile } from 'node:fs/promises';
import { parseTSV } from './model.mjs';
import { createEvaluationWorker } from './evaluation-worker.mjs';

export async function loadCotsFacts(product, { evaluator } = {}) {
  if (typeof product !== 'string' || !/^[a-z0-9_]+$/.test(product)) throw new Error('Choose a COTS product ID.');
  const worker = evaluator ?? createEvaluationWorker();
  try { return await worker.request({ operation: 'cots_facts', product }); }
  finally { if (!evaluator) worker.close(); }
}

function records(source) {
  const [header, ...rows] = parseTSV(source);
  return rows.filter(row => row.some(Boolean)).map(row => Object.fromEntries(header.map((name, index) => [name, row[index] ?? ''])));
}

export async function loadProducts(directory = new URL('../cots/', import.meta.url)) {
  const [products, pins] = await Promise.all(['products.tsv', 'pins.tsv'].map(async name => records(await readFile(new URL(name, directory), 'utf8'))));
  const ids = new Set();
  return products.map(row => {
    if (!/^[a-z0-9_]+$/.test(row.product_id) || ids.has(row.product_id) || !/^EPSModel::[A-Za-z][A-Za-z0-9]*$/.test(row.model_type)) throw new Error('Invalid or duplicate COTS product definition.');
    ids.add(row.product_id);
    return { id: row.product_id, name: `${row.part_number} · ${row.manufacturer}`, manufacturer: row.manufacturer,
      partNumber: row.part_number, model: row.model_type, datasheetUrl: row.datasheet_url,
      pins: pins.filter(pin => pin.product_id === row.product_id && pin.element_id === 'self')
        .map(pin => ({ number: pin.pin_number, name: pin.pin_name, kind: pin.pin_kind, direction: pin.direction })) };
  });
}
