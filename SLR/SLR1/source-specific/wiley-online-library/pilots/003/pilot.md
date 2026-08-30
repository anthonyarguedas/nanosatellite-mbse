# Pilot 003: complete schedule and identifier-ledger diagnostic

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_wiley_online_library.py`, with a non-mergeable two-pass rendered DOI/source-ID ledger only when Wiley's native RIS route failed. This is not a final search.

## Objective

Run all nine direct-schedule entries at the diagnostic window 2011-01-01 through 2026-08-29, preserve each literal, declared pair, and Boolean relationship, and determine whether Wiley can provide complete DOI/source-ID ledgers with source-month and exact-day reconciliation.

## Method and controls

- One `Anywhere`/`AllField` row; full `articlesChapters` source family; Date/`Earliest` (the observed order is newest-to-oldest).
- No `PubType`, Language, access, peer-review, full-text, venue, Subject, or controlled-vocabulary filter.
- A1 alone uses the Pilot 002 `CubeSat*`, `nanosat*`, and `SmallSat*` compression. Its current ordered 21-ID hash is again `aa37f90bd324493e79e0875355abdfd68be1c920260525efa76f83a4632ee6c8`. Every other query is literal.
- Wiley applies the enclosing 2011-01 through 2026-08 month range. Each successful ledger stores the two-pass source-month sequence and visible `First published` client-day status. One A2 and one BT2 DOI lack day precision and remain retained as `unresolved`; none was silently excluded.
- The standard native-RIS adapter failed with `total: null` for A1 (unrecognizable RIS) and A2 (missing Export Citations control). The identifier ledgers are diagnostic and non-mergeable; they do not substitute for a final native export.

## Runs and reconciled outcomes

| ID | Source event outcome | DOI/source-ID outcome after exact-day status |
|---|---|---:|
| A1 | One complete source query | 21 IDs; 21 included |
| A2 | Full query failed with null total; lossless 3-cell union | 153 cell events → 129 IDs; 128 included + 1 unresolved |
| A3 | One complete source query | 60 IDs; 60 included |
| B1 | One complete source query | 86 IDs; 86 included |
| B2 | Cloudflare/access challenge failure | `null` total |
| BG1 | Source total changed between required passes | `null` total |
| BG2 | One complete source query | 47 IDs; 47 included |
| BC1 | Full query failed with null total; lossless 3-cell union | 62 cell events → 60 IDs; 60 included |
| BT2 | Prospective lossless 9-cell union | 720 cell events → 209 IDs; 208 included + 1 unresolved |

The 2,700-character cell ceiling is below Pilot 001's accepted 2,770-character literal A1. A2 and BC1 needed it after full-query failures; BT2 (9,013 characters) was split prospectively. The exact cell construction, complete query strings, and membership audit are in [`query-plan.json`](searches/query-plan.json).

- [Ordered ledgers, cell-event duplicate manifests, and source-month/client-day reconciliation](searches/source-id-unions.json)
- [Compact schedule assessment](searches/schedule-assessment.json)
- [Metadata and local exact-pair audit](searches/metadata-audit.json)
- [Identifier collector](../../../../scripts/wiley_online_library_pilot003/collect_source_ids.py) and [detail metadata collector](../../../../scripts/wiley_online_library_pilot003/collect_detail_metadata.py)

## Unions and high-volume work

- Stream A (`A1 ∪ A2 ∪ A3`) is complete for this diagnostic: 151 IDs.
- Core Stream B is incomplete because B2 failed; B1 alone has 86 IDs.
- Expanded Stream B is incomplete because BG1 failed; its successful BG2/BC1/BT2 subset has 256 IDs.
- The all-nine union is not claimed. The successful-partition subset has 316 IDs, but B2 and BG1 remain failures.

Every named deduplicated source cell, partition, stream, and overall successful-partition set over 100 was exhaustively audited: A2 (129), BT2 (209), BT2 cells 0001/0004/0007/0009 (102/122/106/126), Stream A (151), successful expanded B (256), and all successful partitions (316). The audit uses two-pass rendered-card title and date fields, attempts Wiley detail abstracts, and checks declared pairs in either order within one title or one abstract with at most five intervening lexical tokens. It found one visible BT2 pair (`tailoring` + `model`) and did not remove any non-confirmed DOI; an Anywhere match can be indexed or full-text material outside visible metadata.

## Result

- [x] Document source limitations

Native RIS capture is not currently reliable enough for a final Wiley run. The cell unions preserve the schedule exactly, but are pilot-only until a future native export and source-stability revalidation succeeds. B2 and BG1 remain explicit null-total failures. No final search or merge was made.
