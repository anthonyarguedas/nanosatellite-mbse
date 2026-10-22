# Mission analogue assistance

## Feasibility and scope

Plain text ConOps can retrieve similar mission descriptions. It cannot determine a unique orbit. This prototype offers two explicit methods over a small reviewed catalogue:

- **Semantic embeddings + cosine:** optional loopback service with the pinned `Qwen/Qwen3-Embedding-0.6B` model. Both descriptions and the query are embedded locally. Cosine is calculated in TypeScript. The service reuses the existing cached model and never opens the paper index.
- **Lexical TF-IDF vectors + cosine:** immediate offline browser demo. This compares normalized words, not semantic embeddings. It needs no service, model download, network request or credentials.

Method selection is explicit. A failed semantic request produces an unavailable state. It never silently substitutes lexical results. Default selection is semantic. Select lexical mode to test immediately without starting Python.

Only reviewed operational descriptions determine retrieval ranks. Orbit numbers and inferred spacecraft properties do not influence the descriptions or the ranking. Scores are uncalibrated catalogue ranks. They are neither probabilities nor proof that the new mission can use an analogue's orbit.

## Integration API

Entry point: `src/mission-assist/index.ts`.

```tsx
import { lazy, Suspense } from 'react';
import { applyMissionAnalogue } from './mission-assist/integration';
const MissionAssist = lazy(() => import('./mission-assist'));

// Inside the mission inspector, using the canonical workspace hook:
<Suspense fallback={<p>Loading mission analogues…</p>}>
  <MissionAssist
    initialQuery={workspace.inputs.mission.conOps ?? ''}
    onQueryChange={query => updateInputs('mission', inputs => ({
      ...inputs, mission: { ...inputs.mission, conOps: query },
    }))}
    onApply={match => updateInputs('mission', inputs =>
      applyMissionAnalogue(inputs, match, inputs.mission.conOps ?? ''))}
  />
</Suspense>
```

`MissionAssist({ onApply: (match: MissionMatch) => void })` has named and default exports. It never imports or alters workspace state. The host must call its normal `updateInputs('mission', …)` path. This preserves dependency invalidation and leaves results stale until recomputed. Do not call an engine function automatically on retrieval or acceptance.

A result card requires an acceptance checkbox and a separate apply button. Only a sourced scalar altitude can produce `MissionMatch`. It contains the exact `altitudeKm`, `acceptedAt`, complete mission record and sources, catalogue revision, method and cosine score. No inclination, orbit type, mission lifetime or load profile is transferred. Ranges remain visible and cannot be averaged or applied by the helper. Resolve them through separate orbit analysis and explicit mission inputs.

The integrated workspace retains `mission.conOps` and `mission.orbitSuggestion`. The receipt preserves mission identity, status and revision, parameter epoch, catalogue revision, method, cosine, original altitude representation and interpretation, source references, query and acceptance time. JSON import validates this evidence and its agreement with the authored altitude and ConOps. Calculation caches are discarded. Editing altitude or ConOps clears the previous receipt. Editing ConOps is an authored context change and invalidates dependent outputs. Search alone changes no numerical mission parameters.

Other exports:

- `searchLexical(query, catalogue, limit?)` returns `MissionSearchResult` synchronously.
- `cosineSimilarity(a, b)` checks dimensions and finite values.
- `missionSearchText(mission)`, `tokenize(text)`, `queryProblem(query)` support review and tests.
- `acceptAltitude(analogue, now?)` checks scalar source references and returns `MissionMatch` without mutation.
- Types: `MissionCatalogue`, `MissionRecord`, `MissionParameter<T>`, `MissionSource`, `MissionAnalogue`, `MissionMatch`, `MissionSearchResult`, `RetrievalMethod`.
- `MISSION_QUERY_EXAMPLES` provides authored synthetic examples, including unrelated input.
- Optional async helper: `searchSemantic(query, catalogue, signal?)` from `src/mission-assist/semantic.ts`. It is dynamically imported only when semantic search is requested.

All styles are scoped beneath `.mission-assist`. No global styles or shared types are changed. Lazy load the feature in the mission inspector as above. No large library is added to the GUI bundle.

## Optional semantic runtime

There are **no new npm dependencies** and **no runtime model downloads** in this implementation. The frontend uses `fetch` to a fixed loopback address. The service requires Python with `torch`, `sentence-transformers` and their existing dependencies. It uses the exact cached model revision `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`, 1024 dimensions. Model files are about 1.2 GB, plus Python and inference memory. This is a local development service, not browser inference.

From `eps-demo/`, the convenience command selects the existing research environment and cache, or `EPS_PYTHON` and `HF_HOME` overrides:

```sh
npm run assist:serve
```

It allows the local Vite development and preview origins on ports 5173 and 4173. The model remains offline. The direct research-environment invocation is also available:

```sh
PYTHONDONTWRITEBYTECODE=1 \
  /Users/antho/nanosatellite-mbse/embeddings/.venv/bin/python \
  src/mission-assist/serve_semantic.py \
  --hf-home /Users/antho/nanosatellite-mbse/embeddings/.cache/huggingface
```

Portable invocation:

```sh
python src/mission-assist/serve_semantic.py --hf-home /path/to/existing/huggingface-cache
```

If the cache uses a separate `sentence-transformers` folder below `HF_HOME`, the service discovers that existing folder. `SENTENCE_TRANSFORMERS_HOME` can override it. The model must already be cached. Offline flags and `local_files_only=True` prohibit downloads. Missing dependencies or cache files produce HTTP 503 and a visible unavailable UI state.

Open the app at `http://127.0.0.1:5173` or `http://localhost:5173`. The service binds only `127.0.0.1:8767`. Use `--allow-origin http://127.0.0.1:5174` for a different local Vite port. The frontend endpoint is fixed in `semantic.ts`. Stop the foreground service with Ctrl+C.

`GET /health` reports model identity and whether the model has loaded. `POST /embed` accepts `{query, documents}`. It lazily loads the model and caches up to four sets of catalogue vectors in memory. It keeps no query history, writes no text logs and saves no embeddings to disk. HTTP bodies, document count and text length are bounded. CORS allows the configured local HTTP development origins only. The frontend validates model revision, finite values and vector shape before computing cosine. It sends no credentials.

Do not expose this service on a network. It is a single-user proof of concept. An HTTPS deployment needs a suitable local transport or a packaged browser model. A production browser option could lazy load a pinned Transformers.js/MiniLM model, but would need model licensing, download/cache behavior, browser performance, privacy and retrieval-quality tests. It is not implemented or claimed here.

## Evidence and limitations

Each catalogue record preserves exact identity, source revision, source snippets, source location, retrieval date, status epoch and field provenance. A reported design orbit remains a design orbit even if the spacecraft later flew. No record supplies a current ephemeris. Missing parameters stay null. Do not infer a launch orbit, Sun-synchronous inclination or flight status from a mission name or a similarity score.

The catalogue contains eight records: OPS-SAT, Proba-V, RainCube, ASTERIA, AAUSAT4, TEMPEST-D, RAX-2 and the explicitly labeled UM5-SAT EPS case study. Direct scalar application is available for OPS-SAT (515 km), Proba-V (820 km), ASTERIA (approximately 400 km) and the UM5-SAT study (550 km). RAX-2 and AAUSAT4 retain altitude intervals. RainCube has a missing numerical altitude in the reviewed sources. TEMPEST-D's image caption gives height above a storm rather than precision Earth-referenced orbital elements, so its transferable altitude remains missing. Missing values are deliberate evidence boundaries.

The local corpus was searched in vector mode with the Qwen reranker. Twelve initial chunks and twelve focused mission chunks were inspected. Critical RAX and UM5-SAT claims were checked in the full Markdown articles. ASTERIA's approximate 400 km altitude and 51.6 degree inclination were checked in the full JPL telecommunications report, specifically its mission orbit description in Section 1.3. Cached content classifications were read through SQLite `mode=ro` and `query_only=ON`, with corpus synchronization disabled. No Jev API search, index rebuild or shared cache mutation was performed. Official mission pages supplement that evidence.

The RAX example illustrates a provenance trap. The 2012 article explicitly reports RAX-2's 410 by 820 km orbit. The later 2014 MBSE paper says its model is not an accurate RAX satellite model and varies orbit values in a simulation trade study. Those simulation values are excluded from the mission catalogue. The atmosphere's scientific target altitude is also excluded from spacecraft altitude.

The demo uses authored sparse-input and topic gates. Lexical results require cosine at least 0.16 and two shared content terms. Semantic results require cosine at least 0.55. These are conservative demonstration thresholds, not calibrated suitability limits. Sparse, generic and unrelated input abstains. Explicit lunar, interplanetary and geostationary contexts are outside this Earth LEO demo and also abstain. Some relevant paraphrases will also abstain. Repeated generic space words and unrelated text with the word “satellite” are covered by tests. Broader multilingual use, negation, conflicting requirements and reliable out-of-domain rejection need a reviewed evaluation set.

The EPS engine uses simplified circular geometry. Catalogue orbit labels and inclinations provide evidence context only. The feature adds no SSO/J2, beta-angle, seasonal, eccentric-orbit, launch, coverage or revisit analysis. Independent engineering must assess launch availability, payload resolution, revisit, ground contacts, radiation, drag, disposal and illumination before any orbit choice is considered feasible.

## Tests and synthetic examples

```sh
npx vitest run src/mission-assist
(cd src/mission-assist && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_semantic_service.py)
npx tsc --noEmit
```

With the optional service running, execute the real model smoke checks:

```sh
PYTHONDONTWRITEBYTECODE=1 python src/mission-assist/check_semantic_live.py
```

Executed on 17 October 2026: TypeScript checking passed, 30 Vitest tests passed, six Python service tests passed and six real Qwen smoke checks passed. The live top matches were Proba-V (0.664), RAX-2 (0.737), RainCube (0.742), ASTERIA (0.750) and UM5-SAT (0.680). A deliberately unrelated recipe containing the word “satellite” stayed below threshold (highest cosine 0.498). These are synthetic retrieval examples, not an evaluation of orbital suitability. Integrated host UI behavior still needs the host application's browser checks.

Try the UI example buttons for vegetation imaging, ionosphere radar, rainfall radar and unrelated text. Both methods should rank relevant reviewed descriptions. The unrelated recipe should abstain without a service request. Semantic scores are not expected to equal lexical scores. If the service is stopped, a semantic search should show unavailable. Selecting lexical mode should still work.

Verify acceptance separately: searching changes no inputs, an unchecked card cannot apply, a range cannot apply, and accepting a scalar changes only the numerical altitude through the host and stores the source receipt. Prior downstream results must become stale. The host integration has focused tests for invalidation, manual-change receipt clearing and JSON persistence. Real-browser checks remain a separate development activity.
