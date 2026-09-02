# Pilot 004: current schedule, wildcard adoption, and mandatory screenshots

Required changes were applied in commit: 49c0cca95b2f4d5551a0d1cb5ce24dc01a8ba7b8

Export method: adapter version 10 at `~/agent-tools/internet/skills/browser/scripts/search_springer_link.py`, plus the pilot collector for complete rendered card-path ledgers. This pilot is diagnostic. It is not a final search. It uses 2011-01-01 through 2026-08-29. Every JSON artifact is nonmergeable.

## Objectives

1. Translate the schedule from commit `3194156e90497186664260a8e86435e78d2e2aa1` without proximity or pair expansion.
2. Compare complete literal and population wildcard card-path unions for every partition.
3. Validate mandatory configured Advanced Search and hydrated first-results screenshots beside every search JSON.

The initial [event plan](searches/event-plan.json) proposed direct queries. The source failures led to an [A2 branch plan](searches/event-plan-v2.json), an [A2 stable-pagination plan](searches/event-plan-v3.json), and the completed [year-partitioned B2 plan](searches/event-plan-v4.json) with 74 source events. The [snapshot retest plan](searches/snapshot-retest-plan.json) contains eight fresh paired events. The [assessment](searches/assessment.json) validates all evidence and decisions.

## Current Springer translation

Every ordinary term is one straight double-quoted literal in the raw Keywords field. Uppercase `OR` joins ordinary blocks. Uppercase `AND` joins required factors. The current compound blocks are:

- `G_model_fixed OR G_mission_exact OR (G_mission AND M_B)`
- `G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B)`
- `C1_fixed OR G_DSL`
- `P AND M_B AND T_precise` for `BT2`

A1, A3, B1, BG1, BG2, BC1, and BT2 each use one direct query. A2 uses one complete `M_H` cell and four fixed contiguous `M_B` term cells. B2 uses one complete query per source year. The historically unstable 2021, 2022, and 2024 B2 years use a fixed two-by-two union of contiguous `M_B` and `R` groups. These cells preserve every ordinary term and Boolean relationship.

No event used a proximity operator, pair expansion, content type filter, access restriction, taxonomy, controlled term, or result-driven term restriction. Every event used `En`, source year controls, and `oldestFirst`.

The source-driven cell plan followed recorded failures:

- The 3,435-character direct literal A2 route timed out before rendered readiness on three fresh attempts.
- The complete literal A2 `M_B` branch repeated a card path across pages after bounded retries on three fresh attempts.
- The complete literal B2 route repeated a card path across pages after bounded retries on three fresh attempts.

Failed attempts supplied no source IDs or totals. The final cells completed two full passes each.

## Complete schedule comparison

The raw union covers every source-year card path. The diagnostic-window union removes only a card with a visible date proved outside 2011-01-01 through 2026-08-29. It retains unresolved day values. This pilot does not replace final detail-date reconciliation.

| Partition | Cells per variant | Literal cell sum | Literal union | Literal diagnostic window | Wildcard cell sum | Wildcard union | Wildcard diagnostic window | Wildcard-only |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `A1` | 1 | 59 | 59 | 59 | 59 | 59 | 59 | 0 |
| `A2` | 5 | 387 | 330 | 330 | 387 | 330 | 330 | 0 |
| `A3` | 1 | 126 | 126 | 126 | 127 | 127 | 127 | 1 |
| `B1` | 1 | 243 | 243 | 243 | 243 | 243 | 243 | 0 |
| `B2` | 25 | 712 | 539 | 537 | 714 | 541 | 539 | 2 |
| `BG1` | 1 | 32 | 32 | 32 | 32 | 32 | 32 | 0 |
| `BG2` | 1 | 91 | 91 | 91 | 91 | 91 | 91 | 0 |
| `BC1` | 1 | 140 | 140 | 137 | 140 | 140 | 137 | 0 |
| `BT2` | 1 | 268 | 268 | 267 | 269 | 269 | 268 | 1 |

Every wildcard union retained every literal stable card path. Six partition sets were equal. A3, B2, and BT2 contained wildcard-only paths from the same two records.

## Wildcard decision

The candidate changes only these population alternatives:

| Explicit alternatives | Springer candidate |
|---|---|
| `CubeSat`, `CubeSats` | `CubeSat*` |
| `nanosat`, `nanosats`, `nanosatellite`, `nanosatellites` | `nanosat*` |
| `SmallSat`, `SmallSats` | `SmallSat*` |

All other population spellings and every other concept term remain literal. Link offers an unbounded unquoted trailing `*`, and quoted wildcard phrases did not expand in validated contrasts. The source has no bounded suffix form for reproducing the other declared families exactly. The accepted candidate saves 85 characters in every source cell.

Fresh paired retests reproduced the wildcard-only paths. The bounded [visible-context investigation](searches/wildcard-only-investigation.json) found:

- `/article/10.1038/s44359-026-00173-2` uses `smallsats` for aerospace high-specific-power applications.
- `/chapter/10.1007/978-3-031-96146-5_11` uses the misspelling `cubesates` for an inter-satellite link. The same report also names `cubesat`, `CubeSats`, and `NanoSats`.

Both records remain within the intended population meaning. Accept and prefer `CubeSat*`, `nanosat*`, and `SmallSat*` in every partition.

## Mandatory screenshots

Adapter version 10 derives `<stem>.search-page.png` and `<stem>.results-page.png` from every CLI JSON path. It exposes no screenshot option. The first PNG shows the configured Advanced Search fields and source-year controls before submission. The second shows the hydrated first results page. The JSON retains each filename, SHA-256, dimensions, privacy-mask count, and privacy state.

The 82 successful schedule and retest events each have both sibling PNGs. The bounded [adapter CLI smoke](searches/adapter-smoke/automatic-screenshot-smoke.NON_MERGEABLE_DIAGNOSTIC.json) returned one result in count-only mode and automatically saved both sibling PNGs. The assessment validates 166 PNGs.

## New detail-route limitation

The wildcard-only Nature Reviews Clean Technology record uses the exact Link card route `/article/10.1038/s44359-026-00173-2`. Its rendered canonical link is `https://www.nature.com/articles/s44359-026-00173-2`.

Adapter version 10 rejects that external `www.nature.com` canonical link under the Pilot 004 detail contract. This fail-closed behavior prevents that adapter version from completing the affected partitions. [Pilot 005](../005/pilot.md) later validated the Link-to-Nature relationship and implemented it in adapter version 11. [Pilot 006](../006/pilot.md) later validated exact-day reconciliation and shared-browser strict complete publication.

## Retained failed attempts

Eighteen null artifacts remain under [`searches/failures/`](searches/failures/). Nine established the superseded direct A2, A2 `M_B`, and direct B2 routes. Nine transient page, screenshot, or browser attempts later completed unchanged. Failed attempts contributed no source ID or total.

## Decision

- Accept the current Boolean translation with five A2 cells and 25 B2 cells per variant.
- Accept and prefer the three population wildcards in all nine partitions.
- Keep every other term literal.
- Keep `En`, broad content coverage, and `oldestFirst`.
- Keep no content type, access, taxonomy, controlled vocabulary, proximity, or pair restriction.
- Require both automatic sibling screenshots for every adapter search event.
- Pilot 005 later resolved the external Nature canonical-link route. Pilot 006 later resolved the exact-day and shared-browser readiness gates.

## Reproduction

Review-specific scripts are under [`SLR/SLR1/scripts/springer_nature_link_pilot004`](../../../../scripts/springer_nature_link_pilot004).

```bash
PYTHONPATH=SLR/SLR1/scripts/springer_nature_link_pilot004 \
python3 SLR/SLR1/scripts/springer_nature_link_pilot004/build_plan.py \
  --year-partitioned-b2 \
  --output SLR/SLR1/source-specific/springer-nature-link/pilots/004/searches/event-plan-v4.json

PYTHONPATH=SLR/SLR1/scripts/springer_nature_link_pilot004 \
uv run SLR/SLR1/scripts/springer_nature_link_pilot004/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/springer-nature-link/pilots/004/searches/event-plan-v4.json \
  --resume

PYTHONPATH=SLR/SLR1/scripts/springer_nature_link_pilot004 \
uv run SLR/SLR1/scripts/springer_nature_link_pilot004/inspect_wildcard_only.py

PYTHONPATH=SLR/SLR1/scripts/springer_nature_link_pilot004 \
python3 SLR/SLR1/scripts/springer_nature_link_pilot004/build_assessment.py

PYTHONPATH=SLR/SLR1/scripts/springer_nature_link_pilot004 \
python3 SLR/SLR1/scripts/springer_nature_link_pilot004/validate_pilot.py
```
