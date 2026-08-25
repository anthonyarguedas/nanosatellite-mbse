# Controller review — OATD corrective pilot P02

**Reviewed:** 2026-08-24T11:23:20-04:00  
**Disposition:** blocked; not accepted; no P03 or final search authorized.

This is a controller review, not an approval record. P02 remains immutable at [`S-D09-P02-20260824T105026-0400`](pilots/S-D09-P02-20260824T105026-0400/).

## Controller validation

Independent checks passed for:

- every tracked and restricted JSON artifact;
- the tracked pilot-manifest schema and blocked/diagnostic/no-screening/no-import invariants;
- all 28 indexed evidence paths and SHA-256 values;
- all local Markdown links;
- all 12 query-cell hashes, character counts, terminal-LF rules, partition/cell mappings, 292 pair clauses, and BT2 union accounting;
- six count-only artifacts having no rows/details and remaining non-mergeable/non-report-ready;
- each count-only marker binding the exact JSON bytes and destination;
- E-007 having `total=null`, zero records, no prefix, no CSV, and no terminal marker;
- no adapter/source invocation after E-007;
- at least 20 seconds between completed source queries;
- the fixed external implementation remaining exactly at commit `5ad2a3158b404cc1bafa3df473bf9755d9cd2eef` with a clean worktree;
- the controller anchor remaining the sole page at postflight and review; and
- no actual Sleep/Wake/DarkWake event across the complete P02/controller-review window.

The shared new-run infrastructure validator and `git diff --check` also pass.

The controller's required pre-P02 restart evidence—capturing the actual clamshell sleep, graceful process-scoped restart, fresh runtime/disk equality check, new anchor, active sleep assertions, and review-time extension—was copied to:

`.searches/s-d09-oatd-restricted/S-D09-P02-20260824T105026-0400/controller-preflight/`

Its `SHA256SUMS` file has SHA-256 `259d51afaba2995357d64106e00520957d680a42f55bdc88d1b620474c32faa3`.

## Source and implementation classification

- **E-001–E-006:** valid, paced, count-only diagnostic events. They establish exact query echo, current fixed basic controls, uppercase `AND`/`OR` syntax, accepted explicit parentheses, and accepted straight-quote syntax. Equal totals do not establish record identity or phrase semantics.
- **E-004/E-005:** the parenthesized and unparenthesized expressions produced 1,332 and 2 respectively. This supports a conservative requirement for explicit grouping; it does not establish a general precedence law.
- **E-007:** confirmed `access_or_busy` source state. The safe adapter label does not distinguish a transient challenge from `Server Too Busy`; neither state is zero or a scientific/source-content result. The event failed closed and was not retried.
- **Implementation:** `code_issue=false` for P02. Count-only, marker publication, owned-page cleanup, and strict error accounting behaved as designed. Successful live strict traversal/CSV publication remains untested rather than failed.
- **Source method:** incomplete. Advanced fields, pair semantics, controlled/indexed terms, controls, positive Record Details, stable identity, pagination, complete strict traversal, and all planned query cells remain unresolved.

## Methodological impact

P02 supports no protocol semantic change and cannot be accepted as the OATD source guideline. Pair-bearing cells remain final-use-prohibited because no same-field proximity or compliant broader same-field construction was demonstrated. `S-D09`, `TASKS.md`, `search-log.md`, and the Part 2 source index must remain pending.

## Post-review implementation direction

At 2026-08-24T12:27:17-04:00, the review owner directed a prospective behavior change: a positively identified OATD `Server Too Busy` response must keep the owned tab open, wait, and retry within the same invocation rather than immediately unwind. This does not mutate P02 or invalidate its fail-closed artifact; version 2 followed P02's then-authorized no-retry rule.

The code-only replacement is external commit `adbf1a06f409aa4c00f739812f9fa0a5ccbe518a`, adapter version 3, script SHA-256 `2e4a403725aea006f7d41798846cc3be7317aa0ff1946eed4fd2243ada039fbc`. It uses a run-wide two-attempt recovery budget with default 30- then 60-second waits, requires an exclusive busy page, revalidates the exact route, reconstructs the canonical OATD GET URL in memory, and reissues that URL rather than the mutable current destination. It never retries a challenge, access denial, CAPTCHA, syntax state, redirect, source-content page, or unsafe route. Persistent/recurrent busy still fails closed, and failure artifacts retain the actual extra-request count. The complete offline academic-search suite passed 161 tests and 78 subtests; no live OATD, browser, or network request occurred. Live behavior remains untested.

## Decision required

The review owner must still decide whether to authorize a separate P03. The code-only direction above does not authorize a source invocation or direct reissue of E-007. In a later authorized invocation, version 3's finite internal recovery of a positively identified busy response is permitted and is not a separate pilot execution retry.

If authorized later, the smallest defensible P03 scope is:

1. fresh post-sleep browser preflight and one paced count-only health gate using candidate commit `adbf1a06f409aa4c00f739812f9fa0a5ccbe518a`;
2. stop if the gate returns a challenge, durable access state, unsafe route, or busy state that persists after the finite internal retry budget;
3. if healthy or safely recovered, use substantially slower source pacing and complete only the unresolved parser/advanced-field/pair/control checks;
4. defer strict Record Details traversal until a separate preflight count remains stable after a longer quiet interval;
5. submit all 12 planned cells only after pair semantics are resolved; and
6. stop after the newly authorized pilot without screening, import, self-approval, or central integration.

Until such authorization is explicit, do not launch P03 or reissue E-007.
