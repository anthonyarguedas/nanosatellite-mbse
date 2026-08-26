# Browser-exploration subagent contract

You are assigned one source-interface **logical exploration run** for one bounded technical recipe. Read `SLR/SLR1/AGENTS.md`, `searches/README.md`, [`two-mode-validation-policy.md`](../two-mode-validation-policy.md), the browser live-phase checklist, the source guideline, and relevant browser domain notes. The run may span multiple sequential create-only `X` sessions; it never overlaps another live source phase.

## Goal

Make the current real interface work and understand it well enough to freeze a deterministic evidence attempt. You are not running an evidence pilot, final search, or screening.

## Operating method

- Use one attached canonical browser lease and one owned page at a time. Reuse the same page/session for safe technical retests; if code reload or lease completion requires a new segment, verify cleanup/release and allocate the next source-local `X` session within this run.
- Run only the minimum launch gate; do not run broad/full suites or build fixture matrices.
- Create/use only pages owned by the session. Never touch the protected anchor or unrelated tabs.
- Start with screenshots and semantic/accessibility inspection. Use visible source-owned navigation and controls. Treat SPA loading/hydration as bounded states, not immediate failures.
- You may retain restricted screenshots and bounded DOM/control projections needed to reproduce a technical finding. Never retain cookies, credentials, session tokens, unrelated page content, or candidate/relevance data.
- Use small sentinel/count-only queries. Record every source submit/reissue, but do not create a campaign attempt for each selector error.
- If a technical defect appears, inspect the actual page, patch it immediately in the assigned source scripts or isolated `agent-tools` worktree, perform only a minimal import/changed-path check, and retest live. A failed replay is a diagnostic iteration; continue unless a deferred, exhausted, or safety-stop criterion in the policy is actually met.
- Do not inherit evidence-attempt retry ceilings as exploration limits. Declare a finite rolling source-operation cap for each live segment, review the outcome before the next segment, and honor global domain pacing throughout.
- Do not call the automation working until the current implementation completes a real-page replay with exact control/readback and terminal-state assertions plus verified cleanup.
- A transient challenge may be left untouched and passively polled under a finite recorded deadline/cadence. Never click, reload, solve, evade, rotate profiles, or open another page to escape it.
- Methodological changes stop for the review owner; routine technical changes do not.

## Deliverable

Keep a lightweight restricted running journal during active debugging. For each live segment preserve immediately: session ID/time, source boundary and sentinel hash/bytes, source submits/reissues, aggregate/zero/`null`, challenge/busy intervals, patch/replay identifier, and verified cleanup/release. Do not pause a safe next iteration for campaign-grade prose, repeated hash inventories, or a commit after every selector error.

When the logical run reaches a working, deferred, exhausted, or useful checkpoint, reconcile concise source-local records using [`browser-exploration-record.md`](browser-exploration-record.md), containing:

- logical run and session IDs, source, dates, and lease/cleanup receipts;
- routes and visible interactions tested;
- source operations, rolling caps, and finite waits;
- observed state machine, robust selectors, and known transient states;
- patches, focused checks, and live replay outcomes;
- restricted screenshot/DOM evidence references;
- what now works live or the specific deferred/exhausted blocker; and
- a frozen proposed evidence-mode plan **only when the automated replay works**.

Do not update `campaign.json`, pass capability gates, screen/import records, or create a final event.
