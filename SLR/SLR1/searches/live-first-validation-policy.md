# Live-first source-pilot validation policy

This policy supersedes broader offline preflight and repeated full-suite language in older source launch plans. Historical attempt records remain unchanged.

## Before live work

Run only the minimum checks needed to prevent a malformed or destructive invocation:

1. read the exact bounded operation and confirm review semantics are unchanged;
2. verify exact query bytes and required runtime arguments;
3. confirm the command imports/starts and destinations are create-only;
4. validate the new manifest/receipt shape; and
5. confirm the canonical browser and lease are healthy.

Do not require a broad focused suite, full repository suite, repeated hash inventory, lint pass, or new fixture matrix before an ordinary pilot or technical retry. Run the smallest test directly covering code changed for safety or the observed failure. Run broader suites only after the live route works and before accepting or merging a reusable implementation.

## On a technical failure

A technical failure is the start of diagnosis, not a terminal handoff. Inspect the actual owned page with screenshots, semantic DOM projection, and bounded state polling. Preserve challenge/access boundaries and do not inspect credentials, cookies, or unrelated tabs.

If no query or native submit occurred, keep the attempt open when practical, patch the selector/wait/observability defect, and run a distinct logged technical-retest operation within a finite cap. If a query was submitted, preserve it and use a separately logged bounded retry or corrective attempt. In either case, perform the live retest promptly after only minimal changed-path checks.

## What remains strict

- one canonical browser process and globally serialized lease;
- no access-control solving, evasion, profile rotation, or challenge bypass;
- create-only evidence and no silent overwrites;
- exact query/source/field/date/language semantics unless the review owner approves a methodological change;
- explicit zero versus `null` failure accounting;
- no pilot screening, candidate import, or final event; and
- deterministic total, stable-identity, and completeness evidence before a source method is accepted for final searching.
