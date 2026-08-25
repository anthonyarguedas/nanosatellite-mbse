# Controller review — OATD corrective pilot P03

**Reviewed:** 2026-08-24T13:40:15-04:00  
**Disposition:** blocked; not accepted; no P04 or final search authorized.

This is a controller review, not an approval record. P03 remains immutable at [`S-D09-P03-20260824T130849-0400`](pilots/S-D09-P03-20260824T130849-0400/).

## Independent validation

Controller checks passed for:

- all tracked and restricted JSON parsing;
- the tracked pilot-manifest schema and blocked/diagnostic/no-screening/no-import invariants;
- all 17 indexed evidence paths, SHA-256 values, and claim references;
- E-001's exact total 8, zero retained rows/details, count-only/non-mergeable status, zero busy retries, and marker binding to the exact JSON bytes;
- E-002's `total=null`, zero records, absent marker/CSV, and no later source execution;
- 246 seconds between E-001 completion and E-002 start;
- all 12 query hashes, character counts, terminal LFs, 292 pair clauses, and BT2's 224-clause four-cell algebra;
- pair-bearing cells remaining final-use-prohibited;
- the external candidate remaining clean at commit `adbf1a06f409aa4c00f739812f9fa0a5ccbe518a`, adapter version 3, SHA-256 `2e4a403725aea006f7d41798846cc3be7317aa0ff1946eed4fd2243ada039fbc`;
- both protected anchors remaining at `chrome://newtab/`, with no surviving OATD page at final postflight/controller review;
- no actual Sleep/Wake/DarkWake event in the pilot/controller-review window; and
- the shared search-infrastructure validator and `git diff --check`.

The pilot's restricted integrity receipt passed. Additional controller evidence is under:

`.searches/s-d09-oatd-restricted/S-D09-P03-20260824T130849-0400/controller-review/`

Its `SHA256SUMS` file has SHA-256 `18110ddf046276d837d48333272b2c3d6937e5e3e37559e86cb69b80b8159855`.

## Execution and implementation classification

- **E-001:** valid version-3 count-only health gate. It reconfirmed the normal basic route, exact echo/total 8, fixed controls, no details, marker publication, and zero busy retries. It does not validate busy recovery, records, exhaustion, or strict completion.
- **E-002:** terminal technical failure with `total=null` and zero records. The normal home form and visible field/control inventory were observed, but no post-submit source state, query echo, total, or advanced-result route was captured. Dedicated-profile history contains the E-002 home visit but no advanced-search-composer visit; a completed advanced source submission is therefore not demonstrated.
- **Review-specific direct utility:** `code_issue=true`. Static inspection and postflight evidence show that page closure was attempted only after leaving the live Playwright connection context. The receipt asserted `owner_page_closed=true`, while the first postflight CDP list proved the owned OATD page remained open. Targeted controller cleanup closed only that identified page and preserved both anchors.
- **Pinned candidate adapter:** no defect was demonstrated by P03's successful basic gate. Its busy-recovery, detail, strict, CSV, and advanced behavior remain untested or outside that adapter; overall candidate-adapter classification remains `unresolved`, not failed.
- **Source/interface:** no advanced-field or source defect was demonstrated. E-002 is not a source zero and cannot establish field semantics, controls, pair behavior, or source busy/access behavior.

Stopping after E-002 was correct. A technical failure may not be reissued inside the same pilot merely because later review identifies its cause.

## Methodological impact

P03 supports no protocol semantic change and cannot be accepted as the OATD source guideline. Same-field pair semantics, advanced fields, controlled/indexed terms, controls, remaining parser contrasts, positive Record Details, stable identity, pagination, strict completeness, CSV publication, and all planned cells remain unresolved. BG1, BG2, BC1, and BT2 remain final-use-prohibited.

No screening, candidate import, final event, central-file integration, or later OATD source operation occurred.

## Decision required

No P04 is authorized. Before any later advanced-field pilot:

1. create a separate code-only, offline-tested advanced diagnostic that keeps cleanup inside a live Playwright context and verifies target disappearance before claiming closure;
2. prove deterministic normal form submission/navigation and bounded allowlisted post-submit-state handling offline;
3. pin that implementation by commit without altering P03;
4. obtain explicit human authorization for a new pilot ID; and
5. retain candidate adapter v3's finite busy policy and the no-new-execution-retry stop rule.

Until those steps and explicit authorization are complete, do not reissue E-002, launch P04, screen/import records, or run a final OATD search.
