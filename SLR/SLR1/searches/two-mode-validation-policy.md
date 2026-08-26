# Two-mode source-interface validation policy

This policy governs all new source work and supersedes broader offline-preflight, adapter-first, and repeated full-suite language in older launch plans. Historical attempt records remain unchanged.

## Architecture

Source work has two distinct modes. Do not force an unfamiliar or failing live interface directly into an immutable evidence attempt.

### Mode 1 — exploration

Use exploration whenever the current route, controls, state transitions, selectors, timing, challenge behavior, pagination, identity surface, or automation implementation is not yet understood, and whenever an evidence attempt fails for a purely technical reason.

Mode 1 is ordinary technical development, not a review run. Its purpose is to make the source script work before review evidence is collected.

- Work on one source/technical recipe at a time and serialize browser leases.
- Use one disposable ignored workspace for screenshots, recorder output, lease receipts, and debug output. Let `mktemp` or the runner create unique paths; do not create tracked `X` packets, launch-gate files, manifests, ledgers, evidence indexes, or per-iteration hashes.
- Do not copy checklists or write preflight reports. Check command startup, browser/lease health, and any known proxy risk in memory, then run the test.
- Use simple sentinel/count-only queries and retain no candidate records or relevance judgments.
- Inspect the real page, patch selectors/state machines/observability, run the smallest focused test, and replay immediately. Reuse the owned page when safe; otherwise cleanly release and start another lease in the same technical loop.
- A human demonstration may be recorded temporarily when it is the fastest way to learn the visible sequence. Analyze it, update the automation, and discard or keep the temporary recording only as needed for debugging.
- Do not impose evidence-attempt caps, formal session counts, or a fixed number of technical retries. Continue while plausible source-owned routes, semantic controls, hydration hypotheses, or implementation fixes remain.
- Prefer visible semantic interactions and source-owned routes over hidden controls or brittle positional selectors.

A human demonstration is not technical completion. Mode 1 is **working** only when the current automation successfully replays the intended source/field/control sequence on the real page, reconciles the required aggregate/zero/identity state, and cleans up its owned page and lease.

Stop or pause technical development only when:

- a challenge, persistent busy/rate-limit condition, cooldown, entitlement/login decision, external setup issue, methodological question, or operator cancellation prevents safe continuation;
- plausible technical options have actually been exhausted; or
- browser provenance, proxy, owned-page cleanup, anchor health, or lease release is unresolved.

A first failed selector or replay is never exhaustion. Mode 1 creates no campaign evidence, PRISMA count, candidate, final event, or required source-packet documentation. Commit the working adapter/helper and focused tests at a useful code checkpoint; formal run documentation begins in Mode 2.

### Mode 2 — evidence

Enter evidence mode only after exploration has demonstrated a working automated replay and frozen:

- the source/interface boundary;
- a concise interaction recipe and state machine;
- the adapter/helper commit and safe output contract;
- exact query/field/control semantics for the capability being tested; and
- the expected total, identity, pagination, or failure evidence.

Evidence mode is deterministic and auditable:

- allocate an immutable campaign attempt;
- execute the exact bounded capability plan without exploratory patching;
- record explicit zero versus `null`, totals, controls, identities, coverage, cleanup, and hashes;
- retain no screening decisions or candidate imports; and
- require deterministic total, stable-identity, and completeness evidence before accepting a final-search method.

If evidence mode exposes a technical failure, preserve that attempt once, return to exploration mode, fix and live-validate the interface there, then allocate a new evidence attempt only when the route works. Do not create a chain of evidence attempts merely to debug selectors.

## Launch checks

For Mode 1, do the checks in memory and create no launch-gate artifact:

1. confirm the source boundary, simple sentinel, and intended controls;
2. confirm the command imports/starts and uses a disposable output path; and
3. confirm the canonical browser/lease is healthy, plus a quick proxy check when relevant.

Then run the live test. Do not require manifests, receipt-shape validation, query hashing, permission-setting ceremonies, broad suites, repeated hash inventories, lint, or fixture matrices. The lease runner may write its operational receipt in the disposable workspace; it is not review evidence and need not be indexed.

Mode 2 retains create-only destinations, immutable receipts, exact query/control provenance, and the formal evidence checks required by its frozen plan.

## Challenge and transient-state handling

Keep the same owned page. A transient challenge may be left untouched and passively polled under a finite recorded maximum and cadence. Never click, reload, solve, evade, rotate a profile, or create a new page to escape it. Treat loading, hydration, and SPA transitions as states to observe until a finite deadline, not immediate protocol failures.

## What remains strict

- one canonical browser process and globally serialized lease;
- no access-control solving, evasion, profile rotation, or challenge bypass;
- no overwrite of tracked review artifacts or Mode 2 evidence; disposable Mode 1 outputs may be replaced inside their ignored workspace;
- exact query/source/field/date/language semantics unless the review owner approves a methodological change;
- explicit zero versus `null` failure accounting;
- no pilot screening, candidate import, or final event; and
- deterministic total, stable-identity, pagination, and completeness evidence before a source method is accepted for final searching.
