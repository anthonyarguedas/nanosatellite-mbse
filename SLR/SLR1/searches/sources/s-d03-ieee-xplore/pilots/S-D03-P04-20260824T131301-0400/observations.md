# S-D03 P04 observations

**Status:** failed closed at the required publication-year control; diagnostic only; not accepted; not authorized for a final run or IEEE S-C01.

## Scope and safeguards

- **[observed]** This is immutable pilot `S-D03-P04-20260824T131301-0400` under protocol commit `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **[observed]** `diagnostic_only=true`, `screening_performed=false`, and `candidate_import_permitted=false` applied throughout. No record was screened, imported, deduplicated as a candidate, or used in a final discovery event.
- **[observed]** All raw adapter outputs, stdout/stderr, identity salt, and support files remain restricted. Tracked evidence contains only method text, exact public query files, aggregate counts, hashes, and safe references.
- **[observed]** P04 used only the isolated controller-assigned browser endpoint and preserved the original `about:blank` anchor. No port-9222 action, browser harness/daemon, REST endpoint, native export, login, CAPTCHA response, adapter edit, staging, or commit occurred.

## Preflight and draft preparation

- **[observed]** Browser runtime/disk version matched at `151.0.7922.174`; launcher, AC power, sleep assertions, one-anchor state, and zero preflight Sleep/Wake/DarkWake events passed. The committed adapter and focused-test SHA-256 values matched the P04 authorization; its focused suite passed 15 tests before live work.
- **[observed]** The pre-live dictionary-v4 audit passed for all nine current one-cell drafts with individually fielded `All Metadata` atoms, quoted normative terms, explicit parentheses, no wildcard, and the existing `NEAR/5` pair grouping.

## A1 fix gate and NEAR/6 gate

1. **[observed] A1 fix gate passed.** The exact unsegmented `queries/A1.ieee-query.txt` count-only run had an exact echo, exact total 5, zero retained records, and safe owned-page closure. This bounded-live-validates the committed P03 small-result-page adapter fix.
2. **[observed] NEAR/6 gate passed.** The four predeclared generic count-only diagnostics had exact echoes and zero retained records. Forward and reverse totals were both 573,342; grouped and distributed totals were both 670,735.
3. **[inferred]** `NEAR/6` is a broader same-field implementation that cannot lose a protocol pair with at most five intervening tokens under either common counting convention, but may admit one extra token. It remains pending human approval rather than being exact equivalence.
4. **[observed]** After that gate, all nine dictionary-v4 drafts were regenerated. A1/A2/A3/B1/B2 were byte-unchanged; BG1/BG2/BC1/BT2 use `NEAR/6` only for pair rules. The post-regeneration algebra/term/grouping audit passed.

## Partition outcomes

| Partition | Safe count-only outcome | Basis |
|---|---:|---|
| A1 | 5 | observed |
| A2 | 11 | observed |
| A3 | 4 | observed |
| B1 | 39 | observed |
| B2 | 65 | observed |
| BG1 | 0, native explicit zero | observed |
| BG2 | 8 | observed |
| BC1 | 23 | observed |
| BT2 | 11 | observed |

Every result had the exact query echo, exact numeric total or native zero, zero retrieved records, and a restricted raw artifact. No cell total is a final-event total or a candidate count.

## Terminal control failure

- **[observed]** After all nine partition cells passed, P04 ran its predeclared generic CubeSat-and-MBSE count-only diagnostic with the visible 2011–2026 publication-year control. The adapter returned `IEEEProtocolError`, `total=null`, zero pages, and zero records despite an exact query echo.
- **[observed]** This is null, not zero. P04 stopped immediately; it did not run the multiple-content-type diagnostic, Language structural probe, exact-A1 full-detail repetitions, Q1–Q3 selection, multipage capture, native export, or any S-C01 action.
- **[observed]** `code_issue=unresolved`. The safe artifact establishes neither a source-control failure nor a demonstrated adapter defect, so P04 did not patch, retry, or relax the control requirement.

## Postflight and impact

- **[observed]** Postflight launcher/version/anchor/AC/assertion checks passed. The original anchor remained the only page target after final adapter closure; the exact P04 window had zero Sleep, Wake, and DarkWake events. Adapter/test bytes and clean assigned-path status remained unchanged. P01–P03 hashes matched their pre-P04 digest.
- **[observed]** No protocol semantic change was made. The broader `NEAR/6` source implementation is allowed by the existing fallback rule but needs human approval before acceptance.
- **[observed]** IEEE S-C01 remains wholly unstarted and explicitly excluded. S-D03 method work is not complete enough for separate IEEE S-C01 authorization.

## Smallest next action

**[inferred]** Controller and human review of the null visible-year-control diagnostic, with a decision on whether a newly authorized, narrowly scoped corrective pilot may diagnose the control behavior. Do not authorize S-C01 or a final IEEE event first.
