# S-D03 P05 observations

**Status:** failed closed at the first conditional operation; diagnostic only; not accepted; no later P05 operation ran.

## Scope and safeguards

- Immutable source-phase successor attempt: `S-D03-P05-20260825T124244-0400`.
- The prior source-free setup incident `S-D03-P05-20260825T123832-0400` is preserved separately with `source_phase_started=false`; the successor used the infrastructure-supported 600-second lease timeout without changing source scope or review semantics.
- `diagnostic_only=true`, `screening_performed=false`, and `candidate_import_permitted=false` applied throughout. No records were screened, imported, exported, or used for S-C01 or a final event.
- Only exact tracked `queries/A1.ieee-query.txt` was used. No partition, NEAR/6, prior parser/count, S-C01, export, or unrelated-record operation was run.

## Browser phase

- The launch-gate recheck reported healthy dedicated CfT epoch `uaShS7G1rXVB9KQFA1A6iw6LznsLaesk`, runtime/disk version `152.0.7977.54`, one inert broker anchor, canonical profile and endpoint, a free OS lease, and no guardian/orphan child.
- The complete attached phase ran under the canonical lease wrapper and process-scoped `caffeinate -dims`. The lease receipt records the canonical endpoint/profile, the same browser epoch, child exit code 1, `verified-clean` target cleanup, and released state. Postflight status reported one preserved anchor, a free/released lease, and a healthy CfT.
- AC power remained at 100%. The exact phase-window Sleep/Wake/DarkWake check found 0/0/0 events. No challenge, login, access, or busy condition was observed.

## Operation ledger

1. **`G-YEAR-CONTROL` / `op-01-year-a1` — failed closed.** The exact A1 query echo was observed. The visible 2011–2026 year control was present, enabled after fill, read back both requested bounds, and was clicked once. Passive post-click stabilization remained unresolved; the rendered state had the exact query echo but a mismatched range summary (`one`) with five cards. The adapter returned `IEEEProtocolError` at `year_post_click_stabilization`, total `null`, zero pages, and zero records. This is null, not zero, and no partial prefix was retained.
2. **`G-CONTENT-CONTROL` — not run.** The year gate was not healthy, so no content-type control was issued.
3. **`G-LANGUAGE-CONTROL` — not run.** The year gate was not healthy, so the probe did not run and English was never selected or applied.
4. **`G-COMPLETENESS` — not run.** No operation-2 total existed; no adaptive bounded capture was issued.

There were no retries or reissues. The first failed source operation stopped the phase immediately under the declared fail-closed rule. P05 source-phase totals are therefore `null` for the attempted year operation and not-run for operations 2–4; records retrieved/imported are 0/0.

## Disposition

- `code_issue=unresolved`: the safe artifact establishes a failed visible year-control invariant, but this attempt did not independently distinguish a source-side control behavior from an adapter stabilization/parser invariant. No adapter or probe code was changed.
- The accumulated P01–P04 evidence, diagnostic partition counts, and authorized `D-METHOD-NEAR6` decision remain immutable and unaffected. P05 does not supersede or reinterpret them.
- The campaign remains technically blocked. The smallest next action is controller review of this null year-control artifact and, if warranted, a separately authorized technical correction; do not run content, language, completeness, S-C01, or final-search work from this failed attempt.
