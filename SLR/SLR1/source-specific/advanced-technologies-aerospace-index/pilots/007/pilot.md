# Pilot 007: schedule without proximity operators

Required changes were applied in commit: f794ca4dfdc64101d2a698ee314b87b803b69bcf

Export method: `~/agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py`

Pilot 007 is diagnostic. It is not a final search. It uses the labelled 2011-01-01 through 2026-08-29 pilot window. Every source artifact is non-mergeable.

## Objective

Test the direct ATAI translation of the nine-partition schedule introduced in commit `3194156e90497186664260a8e86435e78d2e2aa1`. Confirm that every complete expression runs without proximity syntax or query splitting. Repeat every total, capture complete records for `BG1`, `BG2`, `BC1`, and `BT2`, and retain both full-page screenshots for every successful source event.

## Translation

Every ordinary literal uses the Pilot 006 atom:

```text
(NOFT("literal") OR IF.EXACT("literal"))
```

The changed blocks preserve the protocol's nested Boolean definitions:

| Block or partition | Source construction |
|---|---|
| `G_model` | `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))` |
| `G_structure` | `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))` |
| `C1` | `F(C1_fixed) OR F(G_DSL)` |
| `BT2` | `F(P) AND F(M_B) AND F(T_precise)` |

The [predeclared event plan](searches/event-plan.json) contains every exact expression and term count. The complete queries range from 3,439 to 9,528 characters. Each partition fits in one query under the validated 50,000-character limit. The expressions contain no proximity operator, pair expansion, wildcard, or implicit variant request.

## Runs

The [run receipt](searches/run-receipt.json) records 22 completed events:

- two independent count-only passes for all nine partitions
- one strict complete full-record run for each changed partition

Every event selected ATAI alone, applied exact `LA(English)` and the inclusive publication-date window, left type, peer review, full text, and access unrestricted, disabled spelling and form variants, and used oldest-first ordering. Adapter v6 saved one configured-search screenshot and one first-results screenshot for each event. The [assessment](searches/assessment.json) indexes all 44 PNG paths, hashes, and dimensions.

## Screenshot repair history

The [initial omission receipt](searches/initial-screenshot-omission.json) records that the first run created no PNG because the runner explicitly disabled them. No screenshot was deleted. The adapter and every ATAI pilot runner now have no screenshot opt-out.

The first replacement attempt stopped before successful query completion because ProQuest could not prove restoration of the shared database selection. Preserve its [run receipt](searches/run-receipt-screenshot-repair-attempt1.json) and [non-mergeable failure artifact](searches/failures/count-A1-pass1-restoration.NON_MERGEABLE_FAILURE.json). A fresh execution of the unchanged 22-event plan then completed. This transient restoration failure does not change any source total or translation decision.

## Repeated totals

| Partition | Pass 1 | Pass 2 |
|---|---:|---:|
| `A1` | [0](searches/counts/pass1/A1.json) | [0](searches/counts/pass2/A1.json) |
| `A2` | [5](searches/counts/pass1/A2.json) | [5](searches/counts/pass2/A2.json) |
| `A3` | [1](searches/counts/pass1/A3.json) | [1](searches/counts/pass2/A3.json) |
| `B1` | [25](searches/counts/pass1/B1.json) | [25](searches/counts/pass2/B1.json) |
| `B2` | [34](searches/counts/pass1/B2.json) | [34](searches/counts/pass2/B2.json) |
| `BG1` | [2](searches/counts/pass1/BG1.json) | [2](searches/counts/pass2/BG1.json) |
| `BG2` | [7](searches/counts/pass1/BG2.json) | [7](searches/counts/pass2/BG2.json) |
| `BC1` | [2](searches/counts/pass1/BC1.json) | [2](searches/counts/pass2/BC1.json) |
| `BT2` | [2](searches/counts/pass1/BT2.json) | [2](searches/counts/pass2/BT2.json) |

All 18 source-total artifacts had exact query and control readback. Both passes agreed for every partition.

## Changed-partition capture

The strict adapter route completed two stable full-record passes internally for each changed partition.

| Partition | Complete records | Screenshots | Stable IDs |
|---|---:|---|---|
| [`BG1`](searches/records/BG1.json) | 2 | [search](searches/records/BG1.search-page.png), [results](searches/records/BG1.results-page.png) | `2545579279`, `2429649929` |
| [`BG2`](searches/records/BG2.json) | 7 | [search](searches/records/BG2.search-page.png), [results](searches/records/BG2.results-page.png) | `1721311269`, `3346991324`, `1762095042`, `1918723567`, `2331489829`, `2339214951`, `2494648056` |
| [`BC1`](searches/records/BC1.json) | 2 | [search](searches/records/BC1.search-page.png), [results](searches/records/BC1.results-page.png) | `1825532815`, `3191429714` |
| [`BT2`](searches/records/BT2.json) | 2 | [search](searches/records/BT2.search-page.png), [results](searches/records/BT2.results-page.png) | `2716309451`, `3110282684` |

The four captures contain 13 record occurrences and 13 distinct ATAI IDs. No ID crosses two changed partitions.

Visible title and abstract metadata shows the expected source matches. `BG1` records contain `generic model`. All seven `BG2` records contain `metamodel`. The direct `BT2` records contain `M_B` terms together with `tailoring`, `customized`, or `instantiating`. One `BC1` record uses `reference model data` outside visible MBSE context. Three `BG2` IDs share one ontology title and three share one attitude-control title. These observations show expected recall-block noise and possible report versions. They do not justify source narrowing or screening decisions.

## Effect of the semantic change

The [assessment](searches/assessment.json) compares the current records with the superseded pair-based pilot records. This comparison describes changed concept definitions. It is not a recall benchmark.

| Partition | Superseded total | Current total | Stable-ID result |
|---|---:|---:|---|
| `BG1` | 2 | 2 | Same two historical IDs |
| `BG2` | 7 | 7 | Same seven historical IDs |
| `BC1` | 2 | 2 | Same two Pilot 006 IDs |
| `BT2` | 3 | 2 | Current and superseded sets are disjoint |

Current `BT2` adds `2716309451` and `3110282684`. The superseded construction returned `1825532815`, `2728408177`, and `3243962233`. The new definition removes broad reuse, configuration, specialization, and adaptation pairs. It adds direct precise tailoring terms in the independent `M_B` context. The set change follows that protocol decision.

## Result

Change the source translation and schedule.

Accept one direct, fully parenthesized ATAI query per partition. Use `(NOFT(L(s)) OR IF.EXACT(L(s)))` for every ordinary term. Render the shared compound blocks with nested `AND` and `OR`. Use no proximity operator or pair expansion. Keep all Pilot 006 field, language, and no-filter decisions.

No query split, source limitation, wildcard, controlled-vocabulary supplement, or result-driven refinement is needed. Final screening remains authoritative.

## Validation and reproduction

The [non-mergeable marking receipt](searches/nonmergeable-marking.json) covers 22 successful source artifacts and the retained restoration failure. The [validation report](searches/validation-report.json) checks query membership, source readback, controls, all 44 screenshot files and receipts, repeated totals, strict captures, stable IDs, documentation links, and guideline synchronization.

Review-specific scripts are under [`SLR/SLR1/scripts/atai_pilot007`](../../../../scripts/atai_pilot007). The core commands are:

```bash
python3 SLR/SLR1/scripts/atai_pilot007/build_plan.py \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007/searches/event-plan.json

uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser.py -- \
  python3 SLR/SLR1/scripts/atai_pilot007/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007 \
  --receipt SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007/searches/run-receipt.json

python3 SLR/SLR1/scripts/atai_pilot007/mark_source_artifacts_nonmergeable.py \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007 \
  --receipt SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007/searches/nonmergeable-marking.json

python3 SLR/SLR1/scripts/atai_pilot007/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007 \
  --pilot003-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/003 \
  --pilot006-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/006 \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007/searches/assessment.json

python3 SLR/SLR1/scripts/atai_pilot007/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007 \
  --guideline SLR/SLR1/source-specific/advanced-technologies-aerospace-index/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/007/searches/validation-report.json
```
