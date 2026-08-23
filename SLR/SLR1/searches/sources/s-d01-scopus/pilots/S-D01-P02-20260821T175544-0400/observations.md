# S-D01 Scopus P02 follow-up observations

- **Pilot ID:** `S-D01-P02-20260821T175544-0400`
- **Status:** `failed` focused diagnostic pilot; not accepted and not report-ready.
- **Live-execution window:** 2026-08-21T17:55:44-04:00 to 2026-08-21T17:56:07-04:00.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** No screening, candidate import, final event, full-text retrieval, or source fallback occurred. P01 is preserved unchanged.

Basis labels: **[observed]** is a P02 command, saved-artifact, or local rendered-route observation; **[official_documentation]** is a source claim independently documented by Scopus; **[inferred]** is a conservative conclusion; and **[untested]** remains unresolved. Protocol instructions are identified separately.

## 1. Supplied corrected-adapter preflight

- **[observed]** The supplied `search_scopus.py` worktree was dirty and uncommitted. P02 recorded the exact script SHA-256 `af14a53013eb446cc9c605dcda1623d22476fb1aa724f0b224d3d03330b5d7c3`; this is a supplied implementation fingerprint, not a released adapter version.
- **[observed]** The required focused suite was run before any live route: `uv run --project <supplied-academic-search-worktree> pytest -q <focused-scopus-browser-test-file>`. It passed: **16 passed in 0.05s**. The reviewed dirty changes cover the current rendered route, native Monaco input/readback, range and selection-rank reconciliation, explicit-zero recognition, and the fail-closed display-cap condition.
- **[observed]** The local loopback CDP version endpoint was reachable (protocol 1.3). It had zero existing page targets. That was not treated as an error because the adapter owns its tab; P02 did not launch another browser or select, navigate, close, or otherwise alter a user tab.
- **[inferred]** The passing focused tests establish only offline behavior covered by their fixtures. They do not establish that the current live Scopus route can be submitted or reconciled safely.

## 2. Exact input and live count-only route

- **[observed]** Before execution, P02 verified the exact existing `queries/A1.scopus-advanced.txt` bytes: 2,096 bytes (2,095 characters excluding its terminal LF), SHA-256 `8fd3fb75d5e963df0d11a667bc865fac6aa611173dff266ba595f7e20667be88`. The query was not edited or translated.
- **[observed]** `P02-A1-COUNT-01` used the supplied adapter through the same loopback Chrome context that P01 had observed as authorized, with `--count-only`, `--limit 10`, and `--max-pages 1`. P02 did not independently re-establish Scopus access before the adapter failed. It saved one non-overwriting restricted JSON artifact, which was read in full after the command.
- **[observed]** That artifact reports `ScopusRequestError`, `total: null`, `pages_retrieved: 0`, `source_entries_retrieved: 0`, `results_retrieved: 0`, and an empty results list. It therefore records neither a source zero nor a partial candidate prefix. Its safe checksum/count receipt is [`adapter-and-count-receipt.json`](adapter-and-count-receipt.json); the full artifact is indexed in [`evidence-index.json`](evidence-index.json).
- **[inferred]** The safe error type does not identify whether the live failure was navigation, form readiness, native editor interaction, or another request-stage condition. P02 makes no access, syntax, source-total, or source-behavior conclusion from it.

## 3. Required follow-up executions deliberately not run

- **[protocol]** The P02 plan permits record, repeat, pagination, explicit-zero, and broad-cap runs only after the initial A1 count-only route succeeds.
- **[observed]** Because `P02-A1-COUNT-01` failed before a reconciled source result, P02 did **not** run the A1 full-abstract retrieval or repeat; A2 multi-page retrieval or repeat; BT2-03 explicit-zero diagnostic; or broad `TITLE-ABS-KEY("CubeSat")` display-cap diagnostic. It did not use `--skip-full-abstracts` for any intended record test because no intended record test began.
- **[inferred]** Avoiding those executions is the fail-closed disposition. A second live query could not repair or reinterpret the failed A1 execution, and a manual/user-tab fallback would not validate the supplied adapter.

## 4. Current capability assessment

- **[observed]** The adapter's focused tests include a fixture asserting that a rendered total at or above 2,000 raises a display-cap failure. P02 did not reach a live broad query, so this is offline adapter-policy coverage only.
- **[untested]** P02 does not prove a current Scopus count, record retrieval, native full-abstract availability, pagination, stable identity, two-pass completeness, explicit-zero handling on the live route, or the live display-cap failure path.
- **[untested]** P02 does not resolve P01's `W/n` endpoint/intervening-token uncertainty, controlled-vocabulary hierarchy/scope/explosion question, actual export behavior, or the earlier broad-count discrepancy. It inspected no controlled term, descriptor, hierarchy, or known record.
- **[protocol]** `S-C01` remains a dependency. No candidate MBSE terminology was tested, accepted, rejected, added, or screened. `P-001` remains unresolved; no date, language, publication-type, access, venue, peer-review, or content restriction was applied.

## 5. Recommendation and human verification

**[inferred] Recommend `revise` / a supervised repeat after diagnosis, not acceptance.** The supplied corrected adapter is not currently evidenced as a safe live capture route. A human supervisor must inspect the P02 restricted failure artifact and the supplied dirty implementation, diagnose the request-stage failure without altering user tabs or bypassing access controls, then authorize a new non-overwriting pilot only if a fresh count-only route can complete. Any later successful pilot must still separately establish the bounded full-abstract route, deterministic repeat identities, multi-page completeness, explicit zero, broad cap failure, export/capture conditions, `W/n`, controlled-vocabulary behavior, `S-C01`, and `P-001` requirements.

No protocol semantic change is proposed. The draft guideline and `translation-spec.json` remain unchanged: P02 produced no successful source-query result supporting an operating or translation change, and leaving the source-level files intact preserves P01's recorded checksums. This direct negative live-route evidence is contained in the P02 artifacts.
