# Browser-exploration subagent contract

You are assigned one source-interface exploration session. Read `SLR/SLR1/AGENTS.md`, `searches/README.md`, [`two-mode-validation-policy.md`](../two-mode-validation-policy.md), the browser live-phase checklist, the source guideline, and relevant browser domain notes.

## Goal

Make the current real interface work and understand it well enough to freeze a deterministic evidence attempt. You are not running an evidence pilot, final search, or screening.

## Operating method

- Use one source-local `X` session and one attached canonical browser lease.
- Run only the minimum launch gate; do not run broad/full suites or build fixture matrices.
- Create/use only pages owned by the session. Never touch the protected anchor or unrelated tabs.
- Start with screenshots and semantic/accessibility inspection. Use visible source-owned navigation and controls. Treat SPA loading/hydration as bounded states, not immediate failures.
- You may retain restricted screenshots and bounded DOM/control projections needed to reproduce a technical finding. Never retain cookies, credentials, session tokens, unrelated page content, or candidate/relevance data.
- Use small sentinel/count-only queries. Record every source submit/reissue, but do not create a campaign attempt for each selector error.
- If a technical defect appears, inspect the actual page, patch it immediately in the assigned source scripts or isolated `agent-tools` worktree, perform only a minimal import/changed-path check, and retest live in the same session.
- A transient challenge may be left untouched and passively polled under a finite recorded deadline/cadence. Never click, reload, solve, evade, rotate profiles, or open another page to escape it.
- Methodological changes stop for the review owner; routine technical changes do not.

## Deliverable

Commit one concise record using [`browser-exploration-record.md`](browser-exploration-record.md), containing:

- session ID, source, dates, lease/cleanup receipt;
- routes and visible interactions tested;
- source operations and finite waits;
- observed state machine, robust selectors, and known transient states;
- patches and implementation commits;
- restricted screenshot/DOM evidence references;
- what now works live and what remains unknown; and
- a frozen proposed evidence-mode plan.

Do not update `campaign.json`, pass capability gates, screen/import records, or create a final event.
