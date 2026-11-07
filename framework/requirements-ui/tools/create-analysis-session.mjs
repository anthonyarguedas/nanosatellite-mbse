#!/usr/bin/env node
// Create named workspaces through the existing session store. Never run scripts.
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { loadCatalog } from '../catalog.mjs';
import { loadScriptCatalog } from '../python.mjs';
import { createSessions } from '../sessions.mjs';
import { createStore } from '../storage.mjs';
import { addScenarioAnalysis, createAnalysisTestWorkspace, createMPPTWorkspace } from '../analyses/workspaces.mjs';

try {
  const { values, positionals } = parseArgs({ allowPositionals: true, options: {
    name: { type: 'string' }, mission: { type: 'string' }, from: { type: 'string' }, orbit: { type: 'string' }, help: { type: 'boolean' },
  } });
  const usage = 'Usage: node tools/create-analysis-session.mjs demo|mppt|scenario [--name "Name"] [--mission path.json] [--from current|session-id] [--orbit requirement-key]';
  if (values.help) { console.log(usage); }
  else {
    const [kind] = positionals;
    if (positionals.length !== 1 || !['demo', 'mppt', 'scenario'].includes(kind)) throw new Error(usage);
    if (kind !== 'scenario' && (values.from || values.orbit)) throw new Error('--from and --orbit apply only to scenario copies.');
    const modelPath = values.mission ? resolve(values.mission) : process.env.MISSION_FILE ? resolve(process.env.MISSION_FILE)
      : fileURLToPath(new URL('../../missions/mission.json', import.meta.url));
    const [catalog, definitions] = await Promise.all([loadCatalog(), loadScriptCatalog(process.env.VERIFICATION_SCRIPTS_DIR)]);
    const sessions = createSessions(modelPath, { catalog });
    let workspace;
    if (kind === 'demo') workspace = createAnalysisTestWorkspace(catalog, definitions);
    else if (kind === 'mppt') workspace = createMPPTWorkspace(catalog, definitions);
    else {
      const from = values.from || 'current';
      const store = from === 'current' ? createStore(modelPath, { catalog, createIfMissing: false }) : (await sessions.get(from)).store;
      workspace = addScenarioAnalysis((await store.read()).workspace, catalog, definitions, { orbitKey: values.orbit });
    }
    const defaultNames = { demo: 'Illumination + MPPT test bench', mppt: 'MPPT analysis (inputs required)', scenario: 'Illumination analysis (inputs required)' };
    const result = await sessions.create({ name: values.name || defaultNames[kind], template: 'copy', workspace });
    console.log(`${result.session.name}\n${resolve(dirname(modelPath), 'sessions', result.session.id, `${result.session.id}.json`)}\nOpen the Session picker or ?session=${result.session.id}#${kind === 'scenario' ? 'mission' : 'mppt-eps'}.`);
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
