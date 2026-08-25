# Source-controller contract

You supervise one SLR1 source through two modes. Read `SLR/SLR1/searches/README.md`, [`two-mode-validation-policy.md`](../two-mode-validation-policy.md), the assigned source packet, and governing protocol sections.

## Choose the mode

- Use **exploration mode** when the current route, selectors, timing, controls, challenge behavior, pagination, or identity surface is unknown, or after an evidence attempt fails technically.
- Use **evidence mode** only after a live exploration has demonstrated the route and frozen the interaction recipe, implementation commit, exact semantics, and expected evidence.
- Do not create repeated evidence attempts to debug an interface.

## Exploration mode

- Allocate one source-local `X` session, not a pilot/campaign attempt.
- Pass only the minimum launch gate: exact query bytes, command startup, create-only destinations, session receipt shape, and healthy browser/lease.
- Use a strong interactive agent on one attached, leased, owned page. Allow screenshots, accessibility/semantic DOM inspection, bounded state polling, visible interactions, and restricted local diagnostic captures.
- Use simple sentinel/count-only operations. Retain no candidate records or relevance judgments.
- Patch behavior-preserving selectors, waits, state machines, and observability immediately in the assigned source scripts or an isolated `agent-tools` worktree. Run only minimal changed-path checks and retest live in the same exploration session.
- Keep one concise exploration log: routes/actions, source operations, observed states, patches/commits, restricted evidence references, and cleanup. Exploration cannot pass a campaign gate.

## Freeze before evidence

Record the working source/interface boundary, visible interaction recipe, adapter/helper commit, query/field/control semantics, finite waits, output contract, expected totals/identity/pagination evidence, and deterministic failure rules.

## Evidence mode

- Create/load `campaign.json` and allocate one immutable `P` attempt for the frozen bounded capability plan.
- The evidence agent executes; it does not patch implementation code during the attempt.
- Record exact operations, controls, zero versus `null`, totals, stable IDs, coverage, cleanup, and immutable hashes. No screening/import/final event.
- On technical failure, preserve the attempt once and return to exploration. On methodological uncertainty, ask the review owner. Do not keep retrying in evidence mode.
- Checkpoint only evidence-mode observations. Carry forward unaffected passed gates by exact path/hash and invalidate only declared dependents.

## Decisions

- `controller_technical`: selectors, timing, state handling, output safety, browser health, cleanup, observability, and packaging that leave review semantics unchanged.
- `human_methodological`: concepts/query semantics, source/field boundary, date/language/content limits, recall, or identity/capture/completeness meaning affecting review accounting.
- Never ask the owner to authorize routine technical exploration or repair.

## Browser and cleanup

Use only the canonical shared CfT lease/profile/endpoint. The controller may run README's bounded outside-lease reconciliation when status is unhealthy and the lease is free with no guardian/orphan. Keep every live child attached. Never mutate the protected anchor, use another profile/endpoint, solve/bypass a challenge, or leave an orphan. Verify owned-page closure and lease release.

## Acceptance

Accept only after deterministic evidence-mode gates pass and no methodological decision is pending. Before acceptance/merge, run the broader relevant regression suite once, pin implementations, and then reconcile `search-log.md`, the Part 2 source index, and `TASKS.md` serially.
