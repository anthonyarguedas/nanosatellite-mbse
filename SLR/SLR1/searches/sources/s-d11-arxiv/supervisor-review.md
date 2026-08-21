# Supervising review — S-D11 arXiv

- **Reviewed:** 2026-08-21
- **Pilot:** `S-D11-P01-20260821T045351+0000`
- **Reviewer role:** supervising subagent; this is **not independent human review**
- **Disposition:** **retain the diagnostic draft and `skip_for_now`; do not accept the guideline or translations**

## Review performed

I collected the depth-2 worker's JSON event log (exit 0), including its recorded browser/tool failures, read every packet file and representative ignored raw receipts, and independently parsed all packet/worklog JSON. The pilot manifest validates against `slr1-pilot-manifest/v1`. The 11 normative partitions and 15 declared cells reconcile to the dictionary, query files, byte hashes, UTF-8/BOM/LF/whitespace checks, and no-`SmallSat`/no-wildcard rules. The split designs are locally lossless in text: BG1 is direct-term union pair-cell; BG2 is direct-term union product-line pair-cell union variation-point pair-cell; BC1 is direct-term union domain-language pair-cell. All listed non-self hashes reconcile. The packet and its ignored worklog stay within the assigned write boundary; no final event, shared integration edit, screening, candidate import, full-text/PDF retrieval, or commit occurred.

## Decision

The pilot provides useful bounded rendered-UI evidence for arXiv's multidisciplinary boundary, All fields, visible row controls, no category/content restriction, lower-bound control, lack of a Language control, simple grammar probes, canonical base-ID/history affordance, and one small two-pass page/range/base-ID ledger. It also correctly identifies that a most-recent-submission upper bound is not lossless for the protocol's earliest substantial completed-version rule, so the draft future method requires unbounded discovery plus local version-history/date handling.

It is not sufficient for acceptance. The normal visible **Add another term +** control became unavailable before `BG2-C2` submission. Per the stop rule, `BG2-C3`, both BC1 cells, BT2, V1, and O1 remain unexecuted; no incomplete union can be accepted. The exact P-001 cutoff, multi-revision history capture, source-wide cap/export behavior, and complete per-cell final two-pass method are also unverified. The event log additionally contains a malformed selector, unavailable Search control, local undefined-variable, and macOS `find -printf` errors; these are recorded diagnostics, not successful source evidence.

One raw-evidence inconsistency must remain visible: `two-pass-pagination-ledger.json` records `next_enabled: true` on the final page, while the separate final-control receipt shows `pagination-next is-invisible` and no href. The guideline's conservative final-page rule follows the direct final-control receipt, but the conflicting ledger flag means it cannot independently establish final-page-control semantics. No raw receipt was rewritten.

Therefore preserve `guideline.md` and `translation-spec.json` as draft/blocked. No protocol semantic change or task completion is approved.

## Focused follow-up

1. In a new owned normal arXiv Advanced Search tab, reproduce the multi-row construction and resolve the unavailable third-row action without changing or narrowing any cell.
2. Revalidate `BG2-C2/C3`, BC1, BT2, V1, and O1, then complete every cell of each lossless union with stable base-ID provenance.
3. Set `P-001`; validate unbounded discovery plus full visible multi-version history/date capture on a genuinely multi-revision report. Only versions available by the cutoff may later be used.
4. Recheck final-page semantics, source cap/export availability, stable base-ID/version behavior, and two complete per-cell page/range/ID passes before any final event.
