import { createEvaluationWorker } from './evaluation-worker.mjs';

let pythonCatalog;

// Python definitions are the sole catalog source. Each caller gets a detached
// projection so browser edits and import tools cannot mutate shared templates.
export async function loadCatalog({ evaluator } = {}) {
  if (evaluator) return evaluator.request({ operation: 'catalog' });
  if (!pythonCatalog) {
    const worker = createEvaluationWorker();
    pythonCatalog = worker.request({ operation: 'catalog' })
      .catch(error => { pythonCatalog = null; throw error; })
      .finally(() => worker.close());
  }
  return structuredClone(await pythonCatalog);
}
