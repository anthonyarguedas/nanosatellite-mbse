# PQDT rendered-route exploration

- **Session ID:** `S-D08-X01-20260825T205023-0400`
- **Source:** ProQuest Dissertations & Theses Global (PQDT Global)
- **Started / ended:** 2026-08-25T20:51:06-04:00 / 2026-08-25T21:00:47-04:00
- **Controller / interactive agent:** Pi controller / Terra interactive browser agent
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `4504968625e7ccedc154c9735f36d8e9a6fc9848f2bff97b71b40f89c565294e`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event
- **Terminal status:** technically incomplete before sentinel submission; cleanup and lease release were verified

## Question and starting state

P01/P02 collapsed the first field/thesaurus operation to `PQDTMetadataProtocolError`. X01 inspected the concrete database-selection and Command Line states, identified the failed invariants, and patched their selectors and observability before any query was submitted.

## Real-page observations

The normal database-selection route was `/pqdtglobal/databases/advanced`, with PQDT source identity, no challenge/login/access state, and 15 visible database checkboxes. Exactly one allowlisted database was selected: **ProQuest Dissertations & Theses Global Full Text Included**. Current checkboxes did not use the adapter's historical `input[id^='dbcb_']` selector, which returned zero controls. The working semantic label came from explicit, nested, or ARIA labelling. This selected database variant is distinct from the Command Line **Full text** limiter.

The normal Command Line navigation redirected to `/pqdtglobal/commandline/advanced`. It exposed one `#searchTerm`, one `#submit_7`, one unchecked Full text limiter, one field selector, and visible **Look up terms**, **Field codes**, and **Command line help** links. No explicit thesaurus control was observed. The field menu contained title-, abstract-, subject/keyword-, and index/term-labelled choices.

Sort, page size, duplicate exclusion, spelling variants, and plural/adjective variants were not missing: they were intentionally collapsed behind one visible **Result page options** link. Expanding it exposed Relevance, page size 20, duplicate exclusion off, spelling on, and plural/adjective variants on. Expansion also produced an optional **What is your role?** survey. It was not an access challenge; the agent closed its unique visible Close control without answering it or using a keyboard shortcut. The controls remained visible and correctly configured afterward.

Thus P02's protocol error concealed two current-interface mismatches: obsolete database checkbox IDs and a parser that required result-page controls before expanding their normal disclosure. The retained screenshots and summary preserve this concrete state only in restricted storage; no account/session/CSRF value, raw DOM, query, result card, or record was retained.

Two source navigations and two non-query visible interactions (expand and survey Close) occurred. `TI("CubeSat")` was not submitted because the cleanup deadline arrived before the patched scripts could be correctly reevaluated on the same page. The page-close command disconnected the harness before its immediate check, but the outer lease runner independently recorded `child_exit_code=0`, `cleanup=verified-clean`, one preserved anchor, and `state=released`. The exact phase contained zero Sleep/Wake/DarkWake events under `caffeinate -dims`.

## Iterations

| Iteration | Visible action or observation | Source submit? | Technical change | Live result |
|---|---|---:|---|---|
| 1 | Opened database selection; mapped visible checkboxes and exact selected allowlisted label. | no | widened projection to semantic checkbox labels while retaining only allowlisted PQDT text | Historical `dbcb_` invariant explained. |
| 2 | Opened Command Line route; mapped query, submit, field/lookup, Full text, and collapsed options. | no | modelled collapsed versus required-expanded result controls | Normal redirect and basic form proved. |
| 3 | Expanded Result page options and closed the optional role survey through its unique Close control. | no | added deterministic expansion, optional-survey Close handling, and focused tests | Relevance/20/dedup-off/spelling-on/plural-on observed. |
| 4 | Added safe probe stages and selected-database context, then attempted same-page code reparse. | no | agent-tools `fbe5b9117170c483207ffbe3f1865ca7c541897c`; review probe `09eed453aa3a19d567b2610dde400d3f72375728` | Manual states were clear, but code reparse was not completed before cleanup. |

## Working interaction recipe

Live-observed steps are: open the PQDT database route; require exactly one selected allowlisted PQDT label; navigate to Command Line and allow its `/advanced` redirect; require one visible query/submit pair and Full text off; expand the unique Result page options link; close only the exact optional role survey if present; then verify Relevance, 20, duplicate exclusion off, spelling on, and plural/adjective variants on.

This is not yet a working query recipe because the patched parser and `TI("CubeSat")` aggregate result were not demonstrated end to end.

## Implementation

- **Adapter/helper commit:** `fbe5b9117170c483207ffbe3f1865ca7c541897c`
- **Review probe commit:** `09eed453aa3a19d567b2610dde400d3f72375728`
- **Changes:** semantic database labels; collapsed/expanded option state; unique role-survey Close; staged safe probe failures; current PQDT domain notes
- **Minimal changed-path checks:** focused adapter suite 10 tests passed during the phase; three postflight current-interface tests passed after survey handling; six probe-runner tests passed; `py_compile` and diff checks passed
- **Live validation status:** manual routes/interactions observed; patched end-to-end parser and sentinel remain unvalidated
- **Remaining unknowns:** patched database/form parser completion, `TI("CubeSat")` query echo/total or native zero, and any result transition

## Proposed evidence attempt

**Not frozen.** Evidence mode remains prohibited. A later exploration must first run the pinned projections/parsers on both observed routes, then submit exact `TI("CubeSat")` once and reconcile the exact query echo, selected database, controls, and aggregate total or explicit zero with zero retained records. Only after that works may the existing staged evidence plan be frozen. Any changed selection, modal/control ambiguity, missing echo/total, access condition, or cleanup failure remains `total=null` with no prefix.
