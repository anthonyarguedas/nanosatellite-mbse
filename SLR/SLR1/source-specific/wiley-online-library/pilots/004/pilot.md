# Pilot 004: current schedule and wildcard adoption

Required changes were applied in commit: NA

Export method: adapter version 12 at `~/agent-tools/internet/skills/browser/scripts/search_wiley_online_library.py`, plus the pilot collector for complete rendered DOI comparison ledgers. This is a diagnostic pilot. It is not a final search. It uses 2011-01-01 through 2026-08-29. Every JSON artifact is nonmergeable.

## Objectives

1. Translate the schedule from commit `3194156e90497186664260a8e86435e78d2e2aa1` without proximity or pair expansion.
2. Compare complete literal and population wildcard DOI unions for every partition.
3. Validate mandatory Advanced Search and first results screenshots beside every JSON.

The [event plan](searches/event-plan.json) predeclares all 20 schedule comparison events, exact queries, hashes, source cells, controls, output paths, and screenshot paths. The [assessment](searches/assessment.json) validates the completed evidence and decisions.

## Current Wiley translation

Every ordinary term is one straight double-quoted literal in a single Anywhere (`AllField`) row. Uppercase `OR` joins ordinary blocks. Uppercase `AND` joins required factors. The current compound blocks are:

- `G_model_fixed OR G_mission_exact OR (G_mission AND M_B)`
- `G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B)`
- `C1_fixed OR G_DSL`
- `P AND M_B AND T_precise` for `BT2`

A2 uses the lossless union of `P AND E_F AND M_H` and `P AND E_F AND M_B`. Every other partition uses one direct query. This gives ten source cells for the nine partitions. The literal A1 comparison retains the historically accepted 2,770-character expression. Every other literal cell is at most 2,617 characters.

No event used a proximity operator, pair expansion, language filter, publication type facet, access restriction, controlled term, or result-driven split. `articlesChapters/default` remained the record family. Each source event used the enclosing January 2011 through August 2026 source window and checked visible `First published` dates against the exact diagnostic cutoff.

## Wildcard comparison

The candidate changes only these population alternatives:

| Explicit alternatives | Wiley candidate |
|---|---|
| `CubeSat`, `CubeSats` | `CubeSat*` |
| `nanosat`, `nanosats`, `nanosatellite`, `nanosatellites` | `nanosat*` |
| `SmallSat`, `SmallSats` | `SmallSat*` |

All other population spellings and every other concept term remain literal. The candidate saves 85 characters in each source cell. Every wildcard cell is at most 2,685 characters.

Each event completed two full page-zero-to-final-page DOI passes. The passes had the same total, page sequence, complete ordered IDs, and rendered-card hashes. The A2 union deduplicates its two predeclared branches.

| Partition | Literal cell totals | Literal union | Wildcard cell totals | Wildcard union | Complete ordered sets |
|---|---:|---:|---:|---:|---|
| `A1` | 21 | 21 | 21 | 21 | equal |
| `A2` | 34 + 106 | 129 | 34 + 106 | 129 | equal |
| `A3` | 60 | 60 | 60 | 60 | equal |
| `B1` | 86 | 86 | 86 | 86 | equal |
| `B2` | 236 | 236 | 236 | 236 | equal |
| `BG1` | 8 | 8 | 8 | 8 | equal |
| `BG2` | 32 | 32 | 32 | 32 | equal |
| `BC1` | 60 | 60 | 60 | 60 | equal |
| `BT2` | 137 | 137 | 137 | 137 | equal |

Every partition also had the same literal and wildcard ID order. No literal ID was missing. There was no wildcard-only ID to inspect. No record fell after the exact 2026-08-29 cutoff. DOI `10.1049/el.2013.1237` displayed only `April 2013`, so its exact day remains unresolved and retained in A2 and B2 under both renderings.

## Mandatory screenshots

Adapter version 12 derives `<stem>.search-page.png` and `<stem>.results-page.png` from every CLI JSON path. It exposes no screenshot opt-out. The first PNG shows the configured Advanced Search text row and available custom date controls before submission. The second shows the hydrated first result page. The JSON retains each filename, SHA-256, dimensions, email-mask count, and privacy state.

The 20 successful schedule events each have both sibling PNGs. The bounded [adapter CLI smoke](searches/adapter-smoke/automatic-screenshot-smoke.json) searched the exact DOI `10.1002/sys.70051`, returned one source result in count-only mode, and automatically saved both sibling PNGs. The assessment validates 42 PNGs in total.

## Retained failed attempts

Five null artifacts remain under [`searches/failures/`](searches/failures/):

- two A1 setup attempts before the exact authorization target was supplied, including one error masked by the initial pilot runner cleanup branch
- one literal B2 runner cleanup failure before that branch was repaired
- one wildcard A1 and one wildcard B2 isolated page-boundary failure

Fresh unchanged events later completed. These repeats did not reuse a page, pass, DOI, screenshot, or source total. Failed attempts contributed no IDs or totals to successful events.

## Decision

Accept the current Boolean translation with the two-cell A2 union. Accept and prefer `CubeSat*`, `nanosat*`, and `SmallSat*` in the population block for all nine Wiley partitions. Keep every other term literal.

This pilot establishes complete rendered DOI equivalence and screenshot behavior. It does not provide native RIS and does not replace the final adapter contract. Final record runs still require two complete ordered passes, exact visible-date accounting, page-scoped native RIS reconciliation, and both mandatory screenshots.

## Reproduction

Review-specific scripts are under [`SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot004`](../../scripts/wiley_online_library_pilot004).

```bash
PYTHONPATH=SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot004 \
python3 SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot004/build_plan.py

WILEY_AUTHORIZED_TARGET_ID=<caller-authorized-target> \
PYTHONPATH=SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot004 \
uv run SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot004/run_pilot.py

PYTHONPATH=SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot004 \
python3 SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot004/build_assessment.py

PYTHONPATH=SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot004 \
python3 SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot004/validate_pilot.py
```
