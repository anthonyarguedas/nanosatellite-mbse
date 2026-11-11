#!/usr/bin/env node
// Create optional report assessments through the existing named-session store.
// Reading definitions pins their source revisions and never executes them.
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { loadCatalog } from '../catalog.mjs';
import { loadCotsFacts } from '../cots.mjs';
import { loadScriptCatalog } from '../python.mjs';
import { createSessions } from '../sessions.mjs';
import { createReportWorkspace, reportProfiles } from '../analyses/report-workspaces.mjs';

try {
  const { values, positionals } = parseArgs({ allowPositionals: true, options: {
    name: { type: 'string' }, mission: { type: 'string' }, list: { type: 'boolean' }, help: { type: 'boolean' },
  } });
  const usage = 'Usage: node tools/create-report-session.mjs <profile> [--name "Name"] [--mission path.json]\n'
    + '       node tools/create-report-session.mjs --list';
  if (values.help) console.log(usage);
  else if (values.list && !positionals.length) {
    for (const profile of reportProfiles()) console.log(`${profile.id}\t${profile.name}`);
  } else {
    const selected = reportProfiles().find(profile => profile.id === positionals[0]);
    if (positionals.length !== 1 || !selected || values.list) throw new Error(usage);
    const modelPath = values.mission ? resolve(values.mission) : process.env.MISSION_FILE ? resolve(process.env.MISSION_FILE)
      : fileURLToPath(new URL('../../missions/mission.json', import.meta.url));
    const [catalog, definitions] = await Promise.all([loadCatalog(), loadScriptCatalog(process.env.VERIFICATION_SCRIPTS_DIR)]);
    const cotsFacts = Object.fromEntries(await Promise.all(selected.products.map(async product => [product, (await loadCotsFacts(product)).facts])));
    const workspace = createReportWorkspace(catalog, definitions, selected.id, { cotsFacts });
    const result = await createSessions(modelPath, { catalog }).create({ name: values.name || selected.name, template: 'copy', workspace });
    console.log(`${result.session.name}\n${resolve(dirname(modelPath), 'sessions', result.session.id, `${result.session.id}.json`)}\n`
      + `Open the Session picker or ?session=${result.session.id}#report-eps.\nInputs and acceptance limits are unset. No analysis was executed.`);
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
