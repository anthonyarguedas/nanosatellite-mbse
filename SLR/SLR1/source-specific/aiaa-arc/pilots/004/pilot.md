# Pilot 004: known-item recall gate and complete field-union diagnostics

This is a diagnostic pilot, not a final search. It uses 2011-01-01 through 2026-08-29 and non-mergeable artifacts only.

## Known eligible ARC sentinel

The required source-indexing event retrieved DOI [`10.2514/6.2015-4474`](searches/known-item-source-indexing-doi-retry1.json) with its ARC title and stable source ID. The earlier null source failure is retained beside it as [`known-item-source-indexing-doi.NON_MERGEABLE_FAILURE.json`](searches/known-item-source-indexing-doi.NON_MERGEABLE_FAILURE.json).

[Source-located PDF and eligibility evidence](searches/known-item-evidence.json) identifies this as an English 11-page 2015 AIAA SPACE conference paper and a known eligible Route B embedded-EPS sentinel. Its source-located applicable schedule partitions are **A2, B1, B2, BC1, and BT2**:

- `A2`: `CubeSat`, functional EPS literals `solar panel`/`battery`, and MBSE/model terms;
- `B1`: `CubeSat` and explicit MBSE terms;
- `B2`: `CubeSat`, reference/system model terms, and relationship terms;
- `BC1`: `CubeSat` and `reference model`; and
- `BT2`: `CubeSat`, `reference model`, and the declared five-token `adapted`/`model` pair.

`A1` and `A3` have no source-located `E_H` literal; `BG1` and `BG2` have no source-located `G_model` or `G_structure` literal/pair. ARC nevertheless returned the DOI in A1/A3 final diagnostics; that is an unclassified hidden-index/full-text behavior, not evidence that the sentinel belongs to those source-located partitions.

The [recall decision](searches/known-item-recall.json) is `accepted_observed_known_item_recall`: every applicable proposed union retrieved the DOI. BT2 retained all four disjoint T2 subcells. The three earlier unresolved-attempt records remain as [attempt 1](searches/known-item-recall-attempt1-unresolved.json), [attempt 2](searches/known-item-recall-attempt2-unresolved.json), and [attempt 3](searches/known-item-recall-attempt3-unresolved.json); their null source/export failures were recovered by later exact retries and were not changed to zeros.

This accepts the field union only for this observed known-item gate. It does not prove recall for unknown records, classify hidden matches as false, or make a final search.

## Fielded schedule and DOI-first unions

The [primary P-field counts](searches/primary-field-union.json) used Title, Keywords, and Abstract separately. Every partition except BC1 exceeded the 100-record conservative cell-sum threshold and therefore used the exact 3-by-3 P/defining-block refinement. BT2 retained four disjoint 56-pair T2 OR subcells. The [normal-CLI final-cell capture](searches/final-cell-capture.json) contains complete non-mergeable previews for positive cells and exact count-only receipts only for zero cells.

| ID | Primary cell-sum bound | Final source events | DOI-first union |
|---|---:|---:|---:|
| A1 | 140 | 42 | 18 |
| A2 | 479 | 119 | 40 |
| A3 | 144 | 33 | 12 |
| B1 | 394 | 87 | 37 |
| B2 | 283 | 56 | 23 |
| BG1 | 2,307 | 93 | 52 |
| BG2 | 1,722 | 20 | 10 |
| BC1 | 52 | 52 | 36 |
| BT2 | 1,018 | 205 | 23 |

The [union reconciliation](searches/schedule-unions.json) preserves raw ARC manifestation IDs, normalizes DOI identity before an ARC `@` virtual-collection suffix, and lists every duplicate event and recovered null failure. Every cell total reconciles to its retained source events. No DOI-first union exceeded 100; overlapping raw cell events (notably BT2's 205) did not trigger the deduplicated-record threshold.

The [exact visible-title audit](searches/visible-title-term-audit.json) applies the declared literals and five-token pair rule only to retained rendered titles. It records warnings where a title does not visibly show every block. Those warnings are not false-match, language, eligibility, or exclusion decisions: ARC Anywhere can match hidden indexing or full text, and preview output does not retain all metadata fields.

## Controls and limits

- All source calls used the repaired normal repeatable `--field-row` CLI, not Pilot 003's import-side count writer.
- No Language, publication-type, Topic, access restriction, full-text/access, or wildcard filter was used.
- ARC supplied only inclusive native months. Totals are conservative source-month totals through August 2026 before exact-day exclusions at the 2026-08-29 diagnostic cutoff.
- Positive cells are complete rendered-card previews with stable DOI IDs. They are explicitly non-mergeable; zero cells retain no IDs and use a normal-CLI exact count-only fallback.
- The source had transient visible citation-export-form failures. Every null failure receipt remains under `searches/`; recovered retries are linked in the union receipt. No failure became a zero.

## Reproduction and validation

Pilot 004 extends, rather than copies, Pilot 003's query construction in [`scripts/aiaa_arc_pilot004`](../../../../scripts/aiaa_arc_pilot004). It requires the read-only integration adapter while using the canonical shared local Chrome runner:

```bash
AIAA_ARC_ADAPTER=/Users/antho/agent-tools-worktrees/slr-integration/internet/skills/browser/scripts/search_aiaa_arc.py \
  caffeinate -dims uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser.py -- \
  python3 SLR/SLR1/scripts/aiaa_arc_pilot004/run_pilot.py --phase all

python3 SLR/SLR1/scripts/aiaa_arc_pilot004/build_assessment.py
python3 SLR/SLR1/scripts/aiaa_arc_pilot004/validate_pilot.py
```

The ignored PDF cache is not committed; recreate the source-located sentinel register with `build_known_item_evidence.py --pdf SLR/SLR1/pdfs/paper-0022_2015_cubesat-model-based-system-engineering-mbse-reference-model-application-in-the-concept-lif.pdf` where that project cache is available.

See the [source guideline](../../source-specific-guidelines.md) for fixed ARC configuration and the prospective, non-final route.
