# Browser-exploration technical-development contract

You are assigned one source and one technical recipe. Read the two-mode policy, shared browser rules, source guideline/latest failure, relevant domain note, adapter, and focused tests. Do not read or update unrelated source packets.

## Goal

Make the current automation work on the real source. Mode 1 is technical development, not a review run, pilot, or evidence collection exercise.

## Operating method

- Use one disposable ignored workspace under `.searches/`; do not create a formal `X` packet, manifest, ledger, launch-gate file, evidence index, or tracked exploration record.
- Check command startup and canonical browser/lease health in memory. Use the lease runner's temporary receipt; do not copy or hash it.
- Use one owned page and one source recipe at a time. Keep browser phases globally serialized.
- Use a small sentinel/count-only query and retain no candidate records or relevance judgments.
- Inspect screenshots, semantic DOM, visible controls, hydration states, and safe stage-specific errors.
- Patch the assigned source script or isolated `agent-tools` worktree, run the smallest focused test, and replay immediately.
- If a replay fails, diagnose and continue. Reuse the page when safe or cleanly release and start another lease. Evidence-attempt caps and formal session counts do not limit technical debugging.
- Use a temporary human recorder only when it is the fastest way to learn the widget sequence. Analyze it and update automation; no formal demonstration record is required.
- Prefer role/name, labels, stable `data-*`, and source-owned route/state assertions. Avoid positional selectors, arbitrary sleeps, opaque routes, challenge selectors, login actions, and bypass behavior.
- Never interact with a CAPTCHA/challenge. Honor source busy/cooldown behavior and never use a new page/profile to escape it.

## Completion

Working means the current adapter completes a live replay with exact source/field/control readback, reconciled aggregate/zero/identity state, and verified owned-page/lease cleanup. A first failed replay is not a terminal outcome.

Pause only for a persistent challenge/busy/cooldown, access or setup owner, methodological decision, operator cancellation, exhausted plausible technical options, or unresolved cleanup/browser safety.

When working, commit the bounded adapter/helper and focused tests. Update a domain note only for a durable technical fact. Do not create source-packet documentation, update a campaign, pass a gate, screen/import records, or create a final event. Formal documentation begins with the later frozen evidence run.
