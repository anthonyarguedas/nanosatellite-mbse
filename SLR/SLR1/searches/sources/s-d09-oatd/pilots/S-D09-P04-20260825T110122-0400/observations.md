# OATD corrective diagnostic observations — S-D09-P04-20260825T110122-0400

**Status:** blocked; diagnostic only. No screening, candidate import, final event, Record Details visit, full-text route, planned partition-cell submission, strict traversal, CSV publication, or relevance classification occurred.

## Authorization and fixed scope

- **[controller_technical]** This is the one controller-authorized P04 under `D-TECH-NEXT-P04` in campaign `S-D09-C01-20260824T161325-0400`. It is behavior-preserving technical work and changes no concept, query semantics, field/source boundary, limit, recall, identity, completeness, or PRISMA rule.
- **[observed]** Source-free gates passed before allocation: 41 focused tests, probe CLI help, script hashes, the shared pre-final validator, `git diff --check`, and byte-stable query/campaign checks. The exact query was recovered from immutable P03 evidence as `CubeSat AND SysML`; the exact field label was `title`; `query_file=none`.
- **[observed]** The live phase used owner `S-D09-P04-20260825T110122-0400`, source `oatd`, a new immutable lease receipt, the supervisor-owned shared CfT at `http://127.0.0.1:9222`, `--wait 60`, a 180-second probe deadline, and the fixed busy policy of at most two same-tab reissues after 30- and 60-second waits.

## Operation and terminal state

| Operation | Exact action | Dispatched | Total | Records | Busy reissues | Outcome |
|---|---|---:|---:|---:|---:|---|
| O-001 | One corrected nonblank advanced-form diagnostic: `CubeSat AND SysML` in `title` | no | `null` | 0 | 0 | **blocked** — `challenge_before_submission` |
| O-002 | Conditional same-tab reissue after 30 seconds | no | `null` | 0 | 0 | not reached; challenge stop |
| O-003 | Conditional same-tab reissue after 60 seconds | no | `null` | 0 | 0 | not reached; challenge stop |

- **[observed]** The probe reached an access-control/verification challenge before a canonical advanced form, field mapping, nonblank readback, or native submit was verified. `native_submit_clicked=false`; the probe classified `challenge_before_submission` and returned `source_reported_total=null`.
- **[observed]** The challenge was not solved, bypassed, clicked, reloaded, waited through, or retried. It was not a safe busy state, so the prospectively authorized busy recovery was not used. There is no native zero and no partial prefix.
- **[observed]** The performed source-operation count is 1 of the P04 cap of 3; busy retries attempted/completed are 0/0. P04 is terminal and was not reissued.

## Browser, provenance, pacing, and cleanup

- **[observed]** Independent preflight and postflight retained browser epoch `5ASpPQYHIFJh_uD--zoyM7LG5u6fCcKh`, CfT runtime/on-disk version `152.0.7977.54`, fixed profile identity `/Users/antho/agent-tools/.browser-profiles/chrome-automation`, one protected inert anchor, and one CfT process using the profile at the canonical endpoint. The broker anchor was not navigated or closed.
- **[observed]** The complete phase ran attached beneath process-scoped `caffeinate -dims`; AC power was present and no actual Sleep/Wake/DarkWake transition was observed in the pre/post checks. The global OATD quiet interval was already satisfied from the prior known OATD operation, and the mandated 60-second wait was retained in the lease command.
- **[observed]** The lease receipt reports `cleanup=verified-clean`, child exit code 1 (the expected blocked probe result), and `state=released`. The probe receipt independently verifies the owned page was distinct, closed while live, disappeared, and that the baseline page and exact target set were preserved. Independent postflight confirms one remaining `about:blank` page and a free lease.

## Gate disposition and carry-forward

- **Passed/carry-forward unchanged:** `G-BOUNDARY`, `G-QUERY-CONSTRUCTION`, `G-BASIC-PARSER`, `G-BASIC-COUNT`, and `G-V3-HEALTH`, by the exact prior campaign paths and hashes. P04 did not retest or alter them.
- **Failed/blocked:** `G-ADVANCED-FORM` remains failed: the required safe post-submit/result state was not reached because of the challenge before submission. `G-PAIR-SEMANTICS` remains blocked; no pair-bearing cell is usable. BG1, BG2, BC1, and BT2 remain final-use-prohibited.
- **Untested/dependent:** `G-BUSY-RECOVERY` is untested because no exclusive busy state occurred. Date, language, content, retrieval, stable identity, pagination, completeness, controlled-vocabulary, and all planned-cell behavior remain unresolved.
- **Failure behavior:** the challenge produced `total=null`, zero retrieved records, and no prefix. It must not be represented as a source zero.

## Decisions and impact

- **Technical decision:** execute exactly the scoped P04 diagnostic and stop fail-closed on challenge; no code defect was demonstrated (`code_issue=false`).
- **Methodological decision:** none requested or made. No protocol or semantic impact.
- **Smallest next action:** retain this immutable blocked attempt and obtain controller/review-owner disposition; do not automatically retry or run a final OATD event. Any future source work needs separate explicit authorization and must still resolve the same-field pair and remaining source gates.

See [`evidence-index.json`](evidence-index.json) and the restricted operation ledger for immutable evidence links and checksums.
