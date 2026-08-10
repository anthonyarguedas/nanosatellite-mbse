# Browser-source reusable-artifact search pilots

**Date:** 2026-08-10
**Classification:** `pilot_not_candidate_search`
**Assessment:** model-assisted; not a human information specialist; no screening

The pilots handled source totals, frozen controls, pagination/reconciliation fields, and source-prefixed one-way opaque IDs only. No title, abstract, author, URL, bibliographic metadata content, full text, report identity, eligibility, or evidence was inspected. A failure is not a zero. Pilot output cannot enter the candidate corpus.

## Precise G1/G2 artifacts

An initial implementation appended the old B2 relation block. All retrieved routes reconciled, and opaque additions were observed, but that logic was rejected because an architecture-bearing artifact could supply its own relation token.

| Initial relation-gated pilot | G1 | G2 | Fresh B1∪B2 | G union | G outside B |
|---|---:|---:|---:|---:|---:|
| Web of Science Core Collection | 2 | 4 | 59 | 6 | 4 |
| Compendex | 3 | 8 | 111 | 11 | 7 |
| Wiley Online Library | 5 | 13 | 124 | 16 | 9 |

A focused follow-up reran relation-free `P AND G1` and `P AND G2` as separate source events:

| Relation-free pilot | G1 | G2 | G union | G outside fresh B1∪B2 | Status/control note |
|---|---:|---:|---:|---:|---|
| Web of Science Core Collection | 2 diagnostic | 4 diagnostic | not accepted | not accepted | Exact dates/Core Collection/All Editions/Topic/no type were observed, but an executable English refinement was unavailable; retained as failures. |
| Compendex | 4 | 8 | 12 | 8 | Reconciled; Compendex-only/KY/autostemming off/literal English and year; exact-day status remains unresolved under `Latest`. |
| Wiley Online Library | 5 | 13 | 16 | 9 | Reconciled; Articles & Chapters/Anywhere/Jan 2011–Aug 2026; language and exact-day remain unresolved under source controls. |

For Compendex, relation-free G added one opaque ID beyond the prior gated G union; Wiley's relation-free and gated G unions were set-identical. These comparisons support relation-free recall as the final design, not record relevance.

## Conservative C1 and model-coupled T2

A separate follow-up tested the conservative central-asset block and model/architecture-coupled tailoring block from the amended plan.

| Source | C1 result | T2 result | Disposition |
|---|---|---|---|
| Web of Science Core Collection | provisional total 4; 1 provisional addition | provisional total 8; 0 provisional additions | Neither accepted: required English refinement was unavailable and completion controls were not satisfied. |
| Compendex | access failure | access failure | Not a zero; retain final strategies and require a controlled clean rerun. |
| Wiley Online Library | 32/32 reconciled; 6 additions | changing total/pagination failure (102 observed) | Accept C1 as a recall diagnostic. Retain T2 prospectively but do not treat the failed snapshot as a set or count. |

The Scopus/IEEE pilots reported separately also found C1 and T2 additions. The authoritative version-1.3 plan therefore keeps relation-free G1/G2, C1, and—where not structurally contained—T2 as separately provenance-coded Stream-B partitions in all five bibliographic interfaces. Browser access/control failures must be corrected during the final run; they do not authorize omission or reuse of pilot records.

## Preservation

Private no-screening artifacts are stored under the ignored protocol-amendment pilot tree with restrictive permissions and SHA-256 manifests. The relation-free browser-pilot manifest hash at integration was `2b7cc2a5031187418bd29a144fa9e08e9cffd3b574bf87ccc741bc3bd2636564`. Exact authoritative final strings are in `query-search-plan.md`; initial relation-gated strings are superseded comparators only.
