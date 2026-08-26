# Two-mode source-interface validation policy

This policy governs all new source work and supersedes broader offline-preflight, adapter-first, and repeated full-suite language in older launch plans. Historical attempt records remain unchanged.

## Architecture

Source work has two distinct modes. Do not force an unfamiliar or failing live interface directly into an immutable evidence attempt.

### Mode 1 — exploration

Use exploration whenever the current route, controls, state transitions, selectors, timing, challenge behavior, pagination, identity surface, or automation implementation is not yet understood, and whenever an evidence attempt fails for a purely technical reason.

An exploration is a **logical debugging run**, not a one-shot attempt. It may span multiple sequential `X` sessions and browser leases while one source/technical recipe remains the active objective. Every live segment still has a unique create-only session ID, finite lease, prospective source-operation cap, and verified cleanup. Sessions never overlap, and a new session never resets domain pacing or escapes a challenge/busy condition.

Exploration is agent-driven browser work:

- use one attached, leased, adapter-owned page at a time; preserve it across observations and same-page retests whenever safe;
- inspect screenshots, accessibility/semantic DOM, visible controls, bounded network-idle/state transitions, and safe stage-specific error classes;
- retain screenshots and bounded DOM/control projections only in restricted local storage when useful for debugging;
- use simple sentinel/count-only queries and retain no candidate records or relevance judgments;
- patch selectors, waits, state machines, and observability immediately, then retest on the real page;
- when no source submit occurred, prefer a same-page retest inside the current lease; when a patch requires a fresh process load or the live segment has ended, verify cleanup/release and allocate the next `X` session within the same logical run;
- treat a failed human-derived or generated automation replay as a diagnostic iteration, not as proof that the source or exploration run has failed;
- do not impose a blanket one-submit, one-replay, or one-corrective-session ceiling on exploration. Before each live segment, declare a finite rolling operation cap and obey source/domain pacing; allocate another segment only after reviewing the preceding outcome;
- prefer visible semantic interactions and source-owned routes over guessed hidden controls or rigid one-shot selectors;
- keep a compact running ledger of routes, source actions, observed states, patches, replay outcomes, and cleanup rather than producing campaign-grade prose for every selector error; and
- use a strong interactive browser agent for open-ended diagnosis. Use a small coding agent only after live behavior is understood and the patch is bounded.

A human demonstration is an input to exploration, not its technical completion criterion. Before freezing an evidence plan, the current automation must successfully replay the intended source/field/control sequence on the real page and reconcile the promised aggregate/zero/identity state with verified cleanup.

Exploration sessions live under `sources/<source>/explorations/<session-id>/` and are explicitly non-accepted. They do not use a pilot ID, satisfy a capability gate, enter PRISMA counts, or become candidates/final events.

#### Exploration exit criteria and lightweight bookkeeping

Do not close a logical exploration run merely because the first selector, patch, or automated replay failed.

- **Working:** the current adapter/helper completes a live replay of the intended bounded recipe with exact control/readback and terminal-state assertions, no prohibited behavior, and verified cleanup/release.
- **Deferred:** a challenge, persistent busy/rate-limit condition, recorded cooldown, unavailable entitlement/login decision, external setup issue, methodological question, or operator cancellation prevents safe continuation. Record the decision owner and earliest safe next condition.
- **Exhausted:** plausible source-owned routes, semantic locators, hydration/state hypotheses, and bounded technical repairs have actually been tried and recorded without producing a working replay. A collapsed error class or single failed replay is not exhaustion.
- **Safety stop:** unresolved owned-page cleanup, lease release, anchor health, proxy, or browser provenance stops all further live work until repaired; it does not establish source failure.

For each live segment, immediately preserve only the minimum durable ledger: session ID/time, exact source boundary and sentinel hash/bytes, source submits/reissues, aggregate/zero/`null`, challenge/busy intervals, patch/replay identifier, and cleanup/release. Keep raw events and diagnostics restricted and create-only. Reconcile the fuller `exploration.md` and restricted artifact index when the logical run reaches working, deferred, exhausted, or another useful checkpoint; do not hold up the next safe technical iteration for exhaustive narration, repeated hashing, or a commit after every failed selector. Commit source records and implementation at stable checkpoints without absorbing unrelated work.

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

## Minimum launch gate

Before either live mode, run only the checks needed to prevent a malformed or destructive invocation:

1. read the bounded operation and confirm review semantics are unchanged;
2. verify exact query bytes and required runtime arguments;
3. confirm the command imports/starts and destinations are create-only;
4. validate the session/manifest/receipt shape; and
5. confirm the canonical browser and lease are healthy.

Evidence-attempt retry ceilings and stale source-plan attempt counts do not cap Mode 1 debugging. Exploration remains bounded by the rolling live-segment cap, global domain pacing, access-control rules, and the exit criteria above.

Do not require a broad focused suite, full repository suite, repeated hash inventory, lint pass, or new fixture matrix before ordinary exploration or a live technical retest. Run the smallest check directly covering changed safety-critical code. Run broader suites only after the real route works and before merging or accepting a reusable deterministic implementation.

## Challenge and transient-state handling

Keep the same owned page. A transient challenge may be left untouched and passively polled under a finite recorded maximum and cadence. Never click, reload, solve, evade, rotate a profile, or create a new page to escape it. Treat loading, hydration, and SPA transitions as states to observe until a finite deadline, not immediate protocol failures.

## What remains strict

- one canonical browser process and globally serialized lease;
- no access-control solving, evasion, profile rotation, or challenge bypass;
- create-only evidence and no silent overwrites;
- exact query/source/field/date/language semantics unless the review owner approves a methodological change;
- explicit zero versus `null` failure accounting;
- no pilot screening, candidate import, or final event; and
- deterministic total, stable-identity, pagination, and completeness evidence before a source method is accepted for final searching.
