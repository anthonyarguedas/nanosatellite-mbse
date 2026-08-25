# Pilot-controller contract

You supervise one SLR1 source campaign. Read `SLR/SLR1/searches/README.md`, the campaign schema/template, the assigned source packet, and the governing protocol sections before acting.

## Campaign and evidence

- Create or load `campaign.json`. Define stable capability-gate IDs, dependencies, finite corrective-attempt bounds, and source-operation limits before live work.
- Run deterministic source-free query-byte, CLI, adapter, output-path, and infrastructure checks before allocating a live attempt ID whenever possible. A safe preflight failure is not readiness: patch the technical defect and rerun the gate.
- Preserve every attempt under a new immutable pilot ID. Never overwrite a failed or cancelled attempt. If an ID was already allocated but no source phase, lease, source operation, or source-gate evidence began, record `allocation.source_phase_started=false`; preserve the incident without charging the enacted source-phase attempt budget.
- After each attempt, checkpoint the campaign. Carry forward unaffected passed gates only by exact evidence path and SHA-256. Invalidate only the failed gate and its declared dependents.
- Report the provider's accumulated capabilities separately from the latest terminal blocker. A late failure does not erase unrelated valid evidence.

## Decisions and authorization

- Classify behavior-preserving work as `controller_technical`: parser/selector robustness, output safety, browser health or restart, target cleanup, observability, passive wait/readiness behavior, and validation packaging that leave review semantics and accounting unchanged.
- You must diagnose, patch, test, and commit demonstrated behavior-preserving defects rather than treating a safe stop as a satisfactory result. You may allocate bounded technical corrective attempts without human authorization when they stay within the campaign limits. A non-enacted source-free setup incident does not consume that enacted-attempt budget.
- Classify a proposal as `human_methodological` only when it can affect the literature review: concepts/query semantics, source or field boundary, date/language/content limits, or identity/capture/completeness rules affecting recall or PRISMA accounting.
- Present only `human_methodological` decisions to the review owner, with recommendation and evidence. Do not ask for approval of routine technical repairs or retries.

## Browser-backed live phases

- Complete reading, query generation, source-free tests, and artifact planning before acquiring the shared-browser lease. Detached subagents are source-free only.
- Use the exact shared CfT lease command and checklist in `searches/README.md`. Never create a source-specific browser, profile, or endpoint. If read-only status is unhealthy while the OS lease is free and no guardian/orphan is alive, you may use only README's canonical outside-lease reconciliation for this dedicated pilot CfT, then recheck the full launch gate; attempt executors may not do so.
- Keep the live executor attached and supervised. On cancellation, stop and collect it, verify source-writing stopped, verify owned-page cleanup and baseline preservation, and verify lease release. Record `cancelled`, not provider failure.
- A failed source operation is not reissued in the same attempt. Diagnose and patch a technical defect source-free, then give the later corrective source phase a new immutable ID under the same campaign. Do not use this rule to strand a pilot after a zero-operation source-free setup mistake.

## Handoff

- Accept a campaign under the existing protocol when all required gates pass and no methodological decision is pending. Human authorization is needed only if a review-affecting methodological change was proposed.
- Commit the accepted campaign/source packet, pin external implementation commits, and then reconcile `search-log.md`, the Part 2 source index, and `TASKS.md` serially.
