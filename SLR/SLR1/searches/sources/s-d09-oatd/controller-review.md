# Controller review — OATD pilot P01

**Reviewed:** 2026-08-24T01:51:59-04:00  
**Disposition:** P01 blocked and not accepted; corrective P02 authorized by the review owner at 2026-08-24T10:45:25-04:00; no final search authorized.

This is a controller review, not an approval record. The immutable pilot remains [`S-D09-P01-20260823T232059-0400`](pilots/S-D09-P01-20260823T232059-0400/).

## Artifact and evidence review

Independent controller checks passed for:

- JSON parsing of every tracked and restricted P01 JSON artifact;
- the tracked pilot-manifest schema;
- all 12 query-file hashes, UTF-8/terminal-LF rules, character counts, and the nine-partition/BT2-cell schedule;
- declared evidence paths and SHA-256 values;
- local Markdown links and packet cross-references;
- diagnostic-only, no-screening, no-import, blocked-status invariants;
- `git diff --check`; and
- the shared new-run search-infrastructure validator.

The browser preflight, active `caffeinate -dims` assertion, AC power, anchor preservation, postflight health check, and absence of an actual pilot-window Sleep/Wake/DarkWake event are adequately evidenced for this blocked run. Controller-created raw preflight files were copied without changing P01 source observations to the ignored durable location:

`.searches/s-d09-oatd-restricted/S-D09-P01-20260823T232059-0400/controller-preflight/`

Its `SHA256SUMS` file has SHA-256 `5ddf6ee3059c43df0adb9894f75638a7a7db9de1b8638900a29f9fa3026f8cea`.

## Implementation classification

- **E-003 custom browser-harness timeout:** `unresolved`. It produced no recoverable source ledger and is not evidence of OATD parser behavior or of an OATD source failure.
- **Candidate adapter at P01 commit `3231ebddefcc3e7bc707b2a7d66fbe831d363286`:** `code_issue=true`. Static inspection confirmed overwrite exposure, one-pass completion/report-readiness exposure, and missing count-only and strict two-pass gates.
- **Source/interface:** no source defect was established. The explicit native zero remains valid; the advanced busy response and transport timeout remain `total=null`.

A separate code-only remediation was completed in the external `agent-tools` repository without live OATD, browser, or review-artifact access. The final implementation commit is:

`5ad2a3158b404cc1bafa3df473bf9755d9cd2eef`

It contains the preceding fixes `8592359cc7612cd84ac629447e1799c0c085b2ed` and `a9c305b271a0b5087cf8babf331ebeb6c2229eca`. The final adapter reports version `2` and adds no-clobber marker-gated publication, non-reportable count-only diagnostics, strict two-pass exhaustion and ordered-ID reconciliation, fail-closed prefix handling, inter-pass pacing, persisted transaction verification, canonical path handling, and companion-CSV safeguards. Independent controller execution of the complete offline academic-search suite passed **148 tests**. These are implementation checks only; no source behavior has been validated with the repaired adapter.

## Methodological review

P01 supports no protocol semantic change. The recommendations on source boundary, local date/language/degree handling, and controlled-vocabulary restraint restate the current protocol and do not authorize a final method. Pair-bearing draft queries remain prohibited because no same-field proximity or compliant broader same-field route was demonstrated.

The review owner accepted the recommendation and authorized one corrective pilot with a new immutable ID at 2026-08-24T10:45:25-04:00. P01 remains blocked and this is not final-search authorization.

## Recommended corrective scope

Authorize `S-D09-P02-<new timestamp>` to use only external implementation commit `5ad2a3158b404cc1bafa3df473bf9755d9cd2eef` and to:

1. re-run the dedicated browser/power/anchor preflight;
2. use count-only mode for paced parser, phrase, Boolean, punctuation, acronym, wildcard, length, and all-cell syntax diagnostics;
3. validate a same-field pair/proximity implementation or record OATD's inability to represent pair-bearing partitions;
4. test positive Record Details identity, repository/resource provenance, optional subject/degree metadata, and controlled-vocabulary absence or behavior;
5. test year/language and other visible controls without treating them as eligibility decisions;
6. complete a small positive multi-page or otherwise bounded two-pass identity/completeness check, plus explicit-zero and fail-closed behavior;
7. reconcile all nine partitions and any lossless cells without screening or candidate import; and
8. update only the OATD packet, then stop for controller and human review.

P02 is authorized to begin. Until it completes and is separately accepted, keep `S-D09`, `TASKS.md`, `search-log.md`, and the Part 2 source index pending.
