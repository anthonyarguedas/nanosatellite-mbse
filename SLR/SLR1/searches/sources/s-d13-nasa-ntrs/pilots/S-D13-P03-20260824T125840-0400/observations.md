# NTRS browser corrective diagnostic observations — S-D13-P03-20260824T125840-0400

## Status and boundary

**Status: blocked at the mandatory initial rendered gate.** This is exactly one diagnostic-only browser pilot. `screening_performed=false`, `candidate_import_permitted=false`, no candidate records were retained, and every unreconciled search/transport value is `null` rather than zero.

- **[observed]** P03 was allocated before its browser/source operation. It snapshots the root packet, immutable P01/P02, repository state, and the pinned adapter at `ff6ed0facc70f95a3096b8ef49b35619b24cacc9`; see [allocation receipts](pinned-adapter-commit.txt), [root hashes](pre-existing-root-packet-sha256.txt), [P01 hashes](pre-existing-p01-sha256.txt), and [P02 hashes](pre-existing-p02-sha256.txt).
- **[observed]** The controller-created dedicated browser remained on the sole New Tab anchor before source work; its runtime/on-disk version match, AC/100% state, P03 controller `caffeinate -dims` assertions, and sanitized controller receipts are recorded in [browser preflight](browser-controller-preflight-sanitized.json). No profile, worktree, or controller temporary path was retained.
- **[observed]** The pinned static guard found no direct NTRS API transport or fallback in `search_ntrs.py`; its intended route is the normal rendered first-party `/search` UI. See [offline validation](pinned-adapter-offline-validation.json).
- **[observed]** No login, credential, CAPTCHA/challenge action, cookie/session handling, PDF download, API call, page-side fetch/XHR, network response inspection, screening, import, shared-file edit, adapter edit, staging, or commit occurred.

## One mandatory live gate

| Execution | Exact planned visible query | Controls | Result | Total / rows |
|---|---|---|---|---:|
| `NTRS-P03-G01` | [`nanosatellite`](queries/G01-minimal-nanosatellite.txt) | rendered UI; one adapter-owned tab; count-only; `limit=1`; `max-pages=1`; no date filter; no detail retrieval; 90 s finite timeout; no retries | **[observed]** adapter exit 1, `NTRSRequestError`, `error_stage=navigation` | `null` / 0 |

- **[observed]** The safe adapter artifact is [G01](adapter-artifacts/G01-minimal-nanosatellite-count-only.json). It reports `total=null`, `results=[]`, no pages, no source total, no range, no canonical ID, no visible form/query echo, no controls, and no explicit zero.
- **[observed]** The G01 route failed before date controls were examined, so no date bound was sent. The diagnostic upper bound `2026-08-24` was consequently not used and is not P-001.
- **[observed]** The adapter closed its own page. The original anchor remained the only page target after exit: [post-gate targets](browser-targets-after-gate.json).
- **[inferred]** The generic navigation-stage failure cannot distinguish a current source/access/navigation condition from an adapter navigation defect without another live attempt. The pilot is not authorized to make that attempt.

## Stop rule and untested scope

- **[observed]** The mandatory gate was not a reconciled visible query/total/range/rows result and was not a native explicit zero. The no-retry stop rule was applied immediately: [stop decision](stop-decision.json).
- **[observed]** No subsequent live adapter invocation, manual NTRS browser operation, static-client request, query contrast, detail visit, date test, export, or partition transport occurred.
- **[untested]** The public full-NTRS versus registered/PubSpace boundary, current form selectors, q field scope, query echo/rewrite, Boolean and precedence semantics, phrases, case, punctuation/hyphen handling, token boundaries, wildcard/expansion/escaping, visible date/language/limit controls, subject/keyword behavior, controlled vocabulary, ordering, page size, pagination, canonical ID stability, export, native zero, two-page traversal, and two-pass completeness remain unvalidated in P03.
- **[untested]** No native unordered same-field <=5-token pair transport is established. The exact paired-term requirement remains unchanged; no broad all-record fallback or semantic weakening was accepted.

## Nine-partition accounting

- **[observed]** All nine required partitions are explicitly accounted for as `blocked_not_sent_after_G01_navigation_failure`, with `source_reported_total=null`, 0 retained records, and no partial prefix: [partition accounting](partition-accounting.json).
- **[observed]** The draft cells A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2 remain immutable root drafts. P03 neither transported nor promoted them.
- **[inferred]** There is no supported source-packet replacement, so P03 intentionally has no `draft-source-packet/` proposal.

## Code issue and methodological impact

- **[observed]** `code_issue=unresolved`, not `true` or `false`: the static rendered-only guard and clean pinned worktree do not demonstrate a defect, while the live navigation failure prevents a live clearance. See [assessment](code-issue-assessment.json).
- **[observed]** P01 and P02 remain immutable blocked pilots; P03 does not reinterpret their API/HTTP failures as browser behavior.
- **[inferred]** No protocol semantic change is proposed. The source boundary, nine partitions, literal dictionary, S-C01 exclusion, date policy, and exact paired-term semantics remain unchanged. The impact is an unresolved browser-navigation/source-access limitation.

## Recommended smallest next action

**[inferred]** Do not patch from this P03 evidence alone. A controller should first independently establish that the normal public rendered NTRS `/search` interface is reachable in a fresh dedicated browser, then seek new human authorization for a new immutable pilot. If that separately controlled observation shows the UI reachable while the adapter alone repeats this navigation-stage failure, assign a separate adapter-fix task; do not modify P03 or retry it.
