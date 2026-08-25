# S-D03 P03 observations

**Status:** failed closed after the authorized corrective diagnosis; diagnostic only; not accepted; not authorized for a final run.

## Scope and safeguards

- **[observed]** Immutable pilot ID: `S-D03-P03-20260824T120555-0400`.
- **[observed]** `diagnostic_only=true`, `screening_performed=false`, and `candidate_import_permitted=false` applied throughout.
- **[observed]** P03 ran exactly three live IEEE operations: one short count-only control, one exact full-A1 state-stage probe, and one exact full-A1 adapter retry.
- **[observed]** No A2–BT2 cell, S-C01 operation, controlled-vocabulary test, NEAR/5 decision, final event, record retrieval, pagination, export, screening, candidate import, or adaptive retry occurred.
- **[observed]** Raw adapter/probe artifacts, stdout/stderr, support scripts, and any raw query/session context remain restricted. This tracked packet contains only exact query files, hashes, safe aggregate outcomes, and restricted references.

## Predeclared exact inputs

- **[observed]** The restricted generator rebuilt P03 inputs from the current v4 dictionary and verified the full A1 reference is byte-identical to `queries/A1.ieee-query.txt`: `P AND E_H AND M_H`, with 20/38/28 terms and 86 individually fielded atoms.
- **[observed]** The exact submitted full-A1 text had 3,582 raw UTF-8 characters, 4,802 form-encoded `queryText` characters, and a 4,879-character initial URL; its query file has one terminal LF and SHA-256 `bf8caf009e189c1869619b399fc43629a7f4ad96bbd111587214351e8d2cce01`.
- **[observed]** The short A1-shaped control used the first frozen normative P, E_H, and M_H representatives with explicit parenthesized AND; it has three atoms.
- **[observed]** The predeclared split was fixed before source work: A1-01 uses E_H terms 1–18 and A1-02 uses terms 19–38, while each retains all P and M_H terms. `a1-algebra-term-audit.json` proves the lossless algebra and records that cell totals must never be summed.

## Exact live outcomes

1. **[observed] P03-E01 short control.** The one adapter count-only control had an exact query echo and a validated native zero: total 0, one rendered page, zero retained records, and a clean anchor census after owned-page closure.
2. **[observed] P03-E02 exact full-A1 state-stage probe.** The one temporary Playwright page received response status 200 on the expected IEEE host/path. It had one exact query echo, a ready source root/header, ranged-summary class, five cards, one active sort, zero active page-size/pagination controls, no challenge/login flag, and all allowlisted terminal category booleans false except `none=true`. It retained no page text, HTML, records, screenshot, session URL, or source total.
3. **[observed] P03-E03 exact full-A1 adapter retry.** The one unchanged pinned-adapter count-only retry had an exact query echo but failed with `IEEEProtocolError`, total null, zero pages, and zero records. It did not retain a prefix.
4. **[observed] Split gate.** It did not run. The valid-state-plus-adapter-failure branch requires `code_issue=true` and a stop before A1-01 or A1-02.

## Classification and disposition

- **[observed]** `code_issue=true`. P03 directly observed a valid reconciled rendered state for the exact full A1 while the unchanged pinned adapter rejected the same exact query. No access condition, query rewrite, source syntax rejection, or source length/term category was observed.
- **[observed]** No source maximum length or term ceiling was established. The five-card state is not a retrieved record set, and it does not establish source-total, identity, union, pagination, or completeness behavior.
- **[observed]** The focused 13-test suite (plus two subtests) passed once before live work. The pinned adapter file and focused-test SHA-256 values matched their assigned values before and after the pilot; no adapter code was edited.
- **[inferred]** A separate code-fix task should reconcile the adapter's current rendered-state invariant with P03's rights-safe projection, add focused regression coverage, and be committed before any new human-authorized pilot. P03 itself must not patch or retry it.

## Remaining limits and impact

- **[observed]** The draft method remains unaccepted and `accepted_pilot_ids` remains empty. Method completion is not ready.
- **[observed]** IEEE S-C01 remains wholly unstarted and is not ready.
- **[observed]** No protocol semantics changed. The dictionary, crosswalk, protocol files, task register, search log, final-events area, screening/candidate data, adapter code, staging, and Git history were not changed.
- **[inferred]** The smallest next action is controller/human review of P03 followed, if approved, by a separate adapter-code-fix subagent and commit; only then can a new narrowly authorized pilot decide whether any source-cell retry is appropriate.
