# S-D13-P04 NTRS diagnostic observations

## Terminal status and scope

**[observed]** Attempt `S-D13-P04-20260825T040250-0400` was allocated as the prospectively authorized controller-technical attempt under `D-TECH-NEXT-P04`. It is **blocked before live work** by a source-free immutable-input preflight failure. The attempt performed **0 of 2** permitted NTRS source operations.

**[observed]** The exact P04 plan's source-free tests and help checks passed: the rendered adapter suite ran 34 tests, the source-health suite ran 14 tests, and both CLIs accepted their help checks. The shared source-free infrastructure validator and `git diff --check` also passed.

**[observed]** The immutable P03 minimal query file has 13 UTF-8 bytes, text `nanosatellite`, and SHA-256 `3fc7d31e9abb58d42acd5c95a9549835545de822d0843e28265c6979b1a466d4`. The plan's expected SHA-256 matches, but the plan's exact raw-byte assertion requires `nanosatellite` plus a final newline (14 bytes). The immutable file does not contain that newline. P03 was not edited and no substitute query was created.

**[observed]** The plan materials compare semantically with their on-disk copies. The only byte differences found in the embedded campaign, resume plan, and execution plan were final-newline presentation differences; the contract and checklist copies matched exactly. No protocol, dictionary, source boundary, query semantics, date filter, or pair rule was changed.

## Operations and accounting

| Planned operation | Status | Source total | Records | Evidence |
|---|---|---:|---:|---|
| 1. One source-health root navigation | **not invoked** | `null` / unobserved | 0 | `preflight.json` |
| 2. One conditional rendered count-only `nanosatellite` navigation | **not authorized** | `null` / unobserved | 0 | `preflight.json` |

`PILOT_DATE=2026-08-25` was recorded only as the diagnostic ledger date and was not sent as a date filter. There is no source-reported total, no explicit source zero, no retrieved record, and no imported record. No health receipt or adapter output was created. Their writer-owned paths remain create-only and absent in the restricted ledger.

No retry, busy reissue, API request, HTTP probe, partition, second query, detail visit, export, completeness pass, screening, candidate import, partial-prefix import, PRISMA identification, or final event occurred. No OATD or other source was accessed.

## Browser, lease, power, and cleanup

**[observed]** Only the explicitly read-only shared-lease status command was used after the source-free blocker. Its sanitized record shows one inert anchor, one inert page, a released lease, a free OS lock, no live orphan child/group, matching runtime/on-disk CfT versions, and stale-or-missing browser-epoch provenance. It did not establish a healthy live-phase browser service.

**[observed]** No P04 lease was acquired, no lease receipt was created, no adapter-owned page was created, no anchor was navigated or closed, no source writer existed, and no child required collection. Browser repair/restart/configuration was not attempted.

**[untested]** Phase-scoped AC-power, outer/phase caffeination, and Sleep/Wake measurements were not made because the live phase was never entered. The safe power/sleep record therefore reports `not_measured`, not a passed live health claim.

## Capability and code decisions

**[observed]** The P04 source-free preflight did not exercise `G-SOURCE-HEALTH` or `G-RENDERED-NAVIGATION`. The campaign therefore preserves the exact-hash P01/P02/P03 evidence and current statuses: `G-SOURCE-HEALTH=blocked`, `G-RENDERED-NAVIGATION=failed`, and dependent `G-PARTITION-TRANSPORT=blocked`. No partition or completeness gate is promoted.

**[observed]** `code_issue=unresolved`. The current adapter and health probe passed their source-free tests, but neither was run against NTRS. The observed blocker is the immutable plan/query byte-contract inconsistency, with an independent stale/missing browser-epoch health result; neither demonstrates a live adapter defect or a provider result.

**[observed]** No methodological decision was made and no human authorization beyond the existing technical allocation was requested. The smallest next action is source-free reconciliation of the P04 exact-byte contract and browser-epoch preflight before any future live phase is considered; do not alter P03 or rerun this attempt.
