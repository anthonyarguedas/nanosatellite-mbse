# Pilot 003: complete ID diagnostic and large set investigation

**Status:** diagnostic only. This is not a final search and does not change the Scopus completion state.

## Scope and controls

The [shared pilot schedule](../../../../scripts/pilot_schedule/queries.py) supplied every literal, declared pair, and Boolean relationship. Main events used source years 2011–2026, the visible **Language: English** facet, **Documents**, and **Date (oldest)**. PSR events used only the upper 2026 source year, Documents, and Date (oldest): no lower bound, language, type, subject, access, or peer-review restriction. No event used `DOCTYPE`.

`2026-08-29` is diagnostic only. Every 2026 record remains unresolved against that day-level cutoff. The 10-wildcard A1 proposal remains unaccepted. No wildcard appears in this pilot.

The read-only Scopus adapter's repaired native abstract follow-up was used. Its normal key-entry path intermittently failed before search. The focused pilot harness used one target-scoped text-entry event and required the same exact Monaco readback before the single source Search click. It does not alter query text or source controls. The native multi-row **Show all abstracts** control still failed safely in several events. Strict two-pass publication-ID ledgers were collected without abstracts, and the failure artifacts were retained. A one-record EID follow-up proves the native abstract route when it renders. Missing batch abstracts are not recoded as unavailable.

## Outcomes

| Route | ID | Source total / stable-ID union | Status |
|---|---|---:|---|
| Main | A1 | 6 | complete ID ledger |
| Main | A2 | 33 | complete ID ledger |
| Main | A3 | 11 | complete ID ledger |
| Main | B1 | 164 | complete ID ledger, investigated (>100) |
| Main | B2 | 180 | complete ID ledger, investigated (>100) |
| Main | BG1 | 8 | complete ID ledger |
| Main | BG2 | 17 | complete ID ledger |
| Main | BC1 | 32 | complete ID ledger |
| Main | BT2 | 13 | complete ID ledger |
| PSR | PSR1 | 53 | complete ID ledger |
| PSR | PSR2 | 237 in full count-only event | no complete union: retained null-total failures in full and lossless-cell routes |
| PSR | PSR3 | 1 | complete ID ledger |
| PSR | PSR4 | `null` | no complete union: retained null-total failures in full and lossless-cell routes |

The main union is **327** unique Scopus publication IDs from 464 source-event records (137 cross-partition overlaps). Native EID-constrained follow-up recovered **111** full abstracts. **216** remain uncollected after safe batch failures, not labelled absent. The completed PSR1+PSR3 subunion is **54** IDs. Its constrained follow-up recovered **24** abstracts. PSR2 and PSR4 are deliberately not folded into a partial PSR union.

- [All outcome and stable-ID union receipt](searches/stable-id-unions-final.json)
- [Main EID abstract-follow-up receipt](searches/main/abstract-follow-up-all/abstract-follow-up-receipt.json)
- [Completed-PSR-subunion abstract-follow-up receipt](searches/psr/abstract-follow-up-complete-subunion/abstract-follow-up-receipt.json)
- [Main strict ID artifacts](searches/main/strict-ids/) and [B1/B2 large-page receipts](searches/main/strict-ids-B200/)
- [PSR strict artifacts](searches/psr/strict-ids/) and [lossless-cell attempts](searches/psr/strict-cells-2500-PSR2/)
- [Safe failure and retry receipts](searches/main/strict/run-receipt.json), [PSR route receipts](searches/psr/strict-ids/run-receipt.json)

## Recovery safeguards

The historical Pilot 003 artifacts above are retained as historical evidence and
are not rewritten by this recovery work. This repair makes no new unlinked live
numeric claim about those historical cells. It requires a current positive page
to reconcile native range, rows, IDs, sort, page size, and pagination; an
explicit zero must instead prove zero rows and the absence of pagination, sort,
page-size, and abstract controls before any control is called not applicable.

The historical PSR2 cells 02, 03, and 08 and PSR4 cells 06 through 08 failed
because a requested page size was treated as mandatory on an explicit zero
page. Those failure artifacts do not establish a strict historical total or a
union. The repaired adapter records zero-page sort, page size, and abstract
retrieval as `not_applicable`, while positive pages remain strict.

PSR2 cell 12 has a historical complete first-pass artifact but no matching
second pass. That artifact remains diagnostic only. A future pass-two failure
may retain an ID-free safe diagnostic, but it never publishes a top-level total,
rows, or mergeable union. PSR2 and PSR4 remain incomplete.

The archival counts of 216 main and 30 completed-PSR-subunion abstracts that
were not recovered remain unresolved historical accounting, not a new live
assertion. Future EID follow-up uses deterministic recursive bisection under an
output-root lock and durable per-node action journal. It preserves every failed
parent, never auto-replays an ambiguous delivery, and accepts only marker-bound
compact strict two-pass leaves whose source/export totals and unique returned ID
set exactly match the requested IDs. Current leaves bind the canonical EID-only
executed query, the closed compact v3 two-pass receipt, the shared terminal
commit-marker verifier, and matching publication/merge transaction bindings.
The child receives only an adapter-private staging path outside the mutable
caller root. After verification, descriptor-relative create-only publication
writes into the originally opened root, so a late rename or symlink cannot
redirect an artifact or receipt. Recovery settings, including the cumulative
source-attempt cap, are sealed before any action. A changed setting is rejected
before launch. A singleton failure remains unresolved and is not relabelled as
no abstract. Immutable migration manifests bind accepted legacy leaves to their
historical artifact and marker digests for rebuilds without pretending they are
v3 recovery output.

## Large-set investigation

B1, B2, their 298-ID union, the 327-ID main union, and PSR2's 237-result count triggered investigation. Only validated controls were retained. There was no lossless `DOCTYPE`, subject, access, or indexed-term restriction: Scopus has no searchable thesaurus or expansion switch, and observed document-type labels are incomplete. B1/B2 contain no declared paired block, so an exact local pair filter is not applicable. No local metadata observation was used to discard a source record. PSR2 was split only at existing OR factors, preserving all source atoms and Boolean factors. Its unresolved cells remain failures rather than a narrower replacement.

- [Large-set investigation and non-refinement decision](searches/investigations/over-100.json)
- [Exact local pair audit using retained titles and available native abstracts (audit only, no records removed)](searches/investigations/local-pair-checks-with-available-abstracts.json)
- [Nested lossless recovery plans and receipts](searches/psr/nested-plans/)

## PSR known item

Buruso et al. (2026), DOI `10.1002/sys.70051`, is indexed as `SCOPUS-PUBLICATION:105032155734` and is present in complete `PSR1`. Recall therefore passes for this indexed known item. The direct full-abstract diagnostic failed safely, while the ID-only check completed.

- [Known-item receipt](searches/diagnostics/PSR-known-item-recall.json)

## Limitations and next step

This pilot establishes only diagnostic source behavior and candidate IDs. It does not screen records, settle cutoff-day eligibility, accept the wildcard proposal, accept a document-type limiter, or authorize final searches. Native multi-record abstract expansion and some PSR cells remain source/adapter failures with `total: null`, preserved with allowlisted stage and reason. A later pilot must obtain a complete PSR2/PSR4 union before any supporting-search completion claim.
