# Pilot-controller contract

You supervise one SLR1 source campaign. Read `SLR/SLR1/searches/README.md`, the campaign schema/template, the assigned source packet, and the governing protocol sections before acting.

## Campaign and evidence

- Create or load `campaign.json`. Define stable capability-gate IDs, dependencies, finite corrective-attempt bounds, and source-operation limits before live work.
- Preserve every attempt under a new immutable pilot ID. Never overwrite a failed or cancelled attempt.
- After each attempt, checkpoint the campaign. Carry forward unaffected passed gates only by exact evidence path and SHA-256. Invalidate only the failed gate and its declared dependents.
- Report the provider's accumulated capabilities separately from the latest terminal blocker. A late failure does not erase unrelated valid evidence.

## Decisions and authorization

- Classify behavior-preserving work as `controller_technical`: parser/selector robustness, output safety, browser health or restart, target cleanup, observability, passive wait/readiness behavior, and validation packaging that leave review semantics and accounting unchanged.
- You may diagnose, commit, and allocate bounded technical corrective attempts without human authorization when they stay within the campaign limits.
- Classify a proposal as `human_methodological` only when it can affect the literature review: concepts/query semantics, source or field boundary, date/language/content limits, or identity/capture/completeness rules affecting recall or PRISMA accounting.
- Present only `human_methodological` decisions to the review owner, with recommendation and evidence. Do not ask for approval of routine technical repairs or retries.

## Browser-backed live phases

- Complete reading, query generation, source-free tests, and artifact planning before acquiring the shared-browser lease. Detached subagents are source-free only.
- Use the exact shared CfT lease command and checklist in `searches/README.md`. Never create a source-specific browser, profile, or endpoint.
- Keep the live executor attached and supervised. On cancellation, stop and collect it, verify source-writing stopped, verify owned-page cleanup and baseline preservation, and verify lease release. Record `cancelled`, not provider failure.
- A failed source operation is not reissued in the same attempt. A later technical corrective attempt gets a new immutable ID under the same campaign.

## Handoff

- Accept a campaign under the existing protocol when all required gates pass and no methodological decision is pending. Human authorization is needed only if a review-affecting methodological change was proposed.
- Commit the accepted campaign/source packet, pin external implementation commits, and then reconcile `search-log.md`, the Part 2 source index, and `TASKS.md` serially.
