# Pilot 003: complete partition and supporting-search diagnostic

Required changes were applied in commit: NA. This is pilot-only evidence. No fixed source decision or completion state was changed.

Export method: `~/agent-tools/internet/skills/browser/scripts/search_web_of_science.py`, through the shared-browser wrapper.

## Objective

Run the complete nine-partition direct schedule and the four-partition prior-secondary-review schedule as diagnostic Web of Science Core Collection events. Preserve all concept literals, declared pairs, and Boolean relations. Use the accepted ten-wildcard population translation for `A1` only. Capture complete ordered WOS/UT ledgers and keep the main and supporting records separate. This is not a final search or candidate import.

## Method

The [query plan](searches/query-plan.json) is generated from the shared [pilot schedule](../../../../scripts/pilot_schedule/queries.py). All events used the current all-edition Core Collection scope, source-observed exact raw query echo, and `--require-complete` two-pass ordered-ID capture. Nonzero events also read back Date: oldest first and native RIS reconciliation. The native `PSR3` zero follows the source zero-result contract without a result-page sort.

- Main events use raw Topic clauses plus `PY=(2011-2026) AND LA=(English)`. No document-type, subject, access, peer-review, or controlled-vocabulary filter was used.
- Supporting events use the source-inception `PY=(1900-2026)` control solely to set the same 2026 upper year while imposing no protocol lower date limit. They have no language, type, subject, access, or peer-review filter.
- `A1` alone uses Pilot 002's accepted ten wildcard atoms. Every other main and PSR partition is the literal `pilot_schedule` translation.
- The `2026-08-29` boundary is diagnostic. Raw `PY` events are retained intact, then [30 distinct 2026 WOS IDs were date-screened](searches/analysis/cutoff-screening.json) using inclusive before/after native `DOP` controls.

## Runs

### Main direct-search pilot events

| ID | Raw artifact | Source total / ordered IDs | Translation |
|---|---|---:|---|
| A1 | [A1](searches/main/A1.json) | 1 / 1 | accepted ten-wildcard A1 only |
| A2 | [A2](searches/main/A2.json) | 11 / 11 | literal |
| A3 | [A3](searches/main/A3.json) | 2 / 2 | literal |
| B1 | [B1](searches/main/B1.json) | 93 / 93 | literal |
| B2 | [B2](searches/main/B2.json) | 78 / 78 | literal |
| BG1 | [BG1](searches/main/BG1.json) | 3 / 3 | literal |
| BG2 | [BG2](searches/main/BG2.json) | 8 / 8 | literal |
| BC1 | [BC1](searches/main/BC1.json) | 17 / 17 | literal |
| BT2 | [BT2](searches/main/BT2.json) | 6 / 6 | literal |

The nine events contain 219 source discovery-event occurrences and reconcile to a 155-ID ordered main union. Stream A is 12 IDs. Core Stream B is 144. Expanded Stream B is 31. The [reconciliation ledger](searches/analysis/reconciliation.json) retains every ordered per-event and union ID and membership.

### Supporting prior-secondary-review pilot events

| ID | Raw artifact | Source total / ordered IDs | Controls |
|---|---|---:|---|
| PSR1 | [PSR1](searches/psr/PSR1.json) | 22 / 22 | source inception–2026, all languages/types |
| PSR2 | [PSR2](searches/psr/PSR2.json) | 60 / 60 | source inception–2026, all languages/types |
| PSR3 | [PSR3](searches/psr/PSR3.json) | 0 / 0 | source inception–2026, all languages/types |
| PSR4 | [PSR4](searches/psr/PSR4.json) | 27 / 27 | source inception–2026, all languages/types |

The four supporting events contain 109 source discovery-event occurrences and reconcile to a separate 102-ID ordered PSR union. They are not merged into the main 155-ID union or any main PRISMA flow.

## Diagnostic checks

- [Known-item checks](searches/analysis/known-item-check.json): `A1` retrieved Pilot 002's `WOS:001027247800008`. Buruso et al. (DOI `10.1002/sys.70051`) was retrieved through successful `PSR1` and `PSR2` events as `WOS:001705529700001`. It was not inserted manually.
- [Exact-cutoff control plan](searches/analysis/cutoff-control-plan.json), [on/before result](searches/analysis/cutoff-on-or-before-2026-08-29.json), and [after result](searches/analysis/cutoff-after-2026-08-29.json): 29 of the 30 distinct 2026 IDs matched the inclusive native `DOP` range through 2026-08-29. `WOS:001795013500001` matched the after-cutoff control (visible projection `Nov 2026`). The diagnostic date-screened view is 154 main IDs (143 core Stream B) and 102 PSR IDs, while raw `PY` event ledgers remain intact and are not retrospectively edited.
- [Local NEAR/6 audit](searches/analysis/near6-local-validation.json): across 61 event rows from paired-block partitions, 2 visibly contained a declared pair within the protocol's five-token rule, 16 visibly matched a fixed non-pair literal, 0 had an observable six-token-only pair, and 43 were not verifiable from retained title/snippet fields. Unobservable Topic fields were not treated as false matches.
- [Over-100 investigation](searches/analysis/high-volume-investigation.json): the deduplicated core Stream B (144), all-main union (155), and PSR union (102) each received a non-narrowing stable-ID membership, cutoff, and retained-field audit. No candidate DT union or other filter was used, and no narrower translation is accepted.

## Result

No guideline change is accepted. The pilot confirms the current literal schedule and the existing A1-only wildcard exception, but it also retains these source limitations:

1. `PY` is year-level. The DOP controls screen the diagnostic cutoff, but Clarivate does not universally document DOP's Early Access versus final-publication basis.
2. Topic may match retained title/snippet text, unretained abstract/author-keyword/Keywords Plus text, or source-normalized variants. The local pair audit can validate only fields retained in the artifact.
3. The normalized public receipt retains complete ordered result rows, exact totals, and native RIS digests. The adapter's internal two-pass ledger is validated during capture but is not published as a licensed export.
4. These are pilots only. The Pilot 003 plan, reconciliation, and diagnostic receipts are marked `do_not_merge`. Raw adapter receipts remain `report_ready: false` beneath the pilot directory. No final-search, candidate-screening decision/flow, PRISMA, or completion-state artifact was created or changed.

Offline plan, reconciliation, and artifact checks are reproducible with [query membership](../../../../scripts/wos_pilot003/test_queries.py), [runner](../../../../scripts/wos_pilot003/run_pilot.py), [analysis](../../../../scripts/wos_pilot003/analyze_pilot.py), and [validation](../../../../scripts/wos_pilot003/validate_pilot.py).
