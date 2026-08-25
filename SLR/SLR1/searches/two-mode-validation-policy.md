# Two-mode source-interface validation policy

This policy governs all new source work and supersedes broader offline-preflight, adapter-first, and repeated full-suite language in older launch plans. Historical attempt records remain unchanged.

## Architecture

Source work has two distinct modes. Do not force an unfamiliar or failing live interface directly into an immutable evidence attempt.

### Mode 1 — exploration

Use exploration whenever the current route, controls, state transitions, selectors, timing, challenge behavior, pagination, or identity surface is not yet understood, and whenever an evidence attempt fails for a purely technical reason.

Exploration is agent-driven browser work:

- use one attached, leased, adapter-owned page for an iterative session;
- inspect screenshots, accessibility/semantic DOM, visible controls, bounded network-idle/state transitions, and safe console/error classes;
- retain screenshots and bounded DOM/control projections only in restricted local storage when useful for debugging;
- use simple sentinel/count-only queries and retain no candidate records or relevance judgments;
- patch selectors, waits, state machines, and observability immediately and retest on the real page in the same session when no query/native submit occurred;
- prefer visible semantic interactions and source-owned routes over guessed hidden controls or rigid one-shot selectors;
- record one concise exploration log with routes tested, source actions, observed states, patches, and cleanup—not a campaign attempt for every selector error; and
- use a strong interactive browser agent for open-ended diagnosis. Use a small coding agent only after the live behavior is understood and the patch is bounded.

Exploration sessions live under `sources/<source>/explorations/<session-id>/` and are explicitly non-accepted. They do not use a pilot ID, satisfy a capability gate, enter PRISMA counts, or become candidates/final events.

### Mode 2 — evidence

Enter evidence mode only after exploration has demonstrated a working route and frozen:

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
