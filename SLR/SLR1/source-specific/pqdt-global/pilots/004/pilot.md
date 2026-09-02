# Pilot 004: current schedule and bounded wildcard adoption

Required changes were applied in commit: ea207806e8398cac3befd50340c57c608b108e32

Export method: adapter version 5 at `~/agent-tools/internet/skills/browser/scripts/search_pqdt.py`. This is a diagnostic pilot. It is not a final search. It uses source years 2011 through 2026 and the diagnostic cutoff 2026-08-29. The pilot plan, run receipt, assessment, and derived unions are nonmergeable.

## Objectives

1. Translate the schedule from commit `3194156e90497186664260a8e86435e78d2e2aa1` without proximity or pair expansion.
2. Use bounded wildcards for every variant family with a safe common ProQuest stem.
3. Compare complete literal and wildcard document-ID sets for every partition.
4. Validate mandatory search-page and results-page screenshots beside every successful JSON.

The [event plan](searches/event-plan.json) predeclares all 18 source events, exact queries, hashes, controls, output paths, and screenshot paths. The [assessment](searches/assessment.json) validates the completed evidence and decision.

## Translation

Each literal atom is `NOFT("literal")`. Uppercase `OR` joins ordinary blocks. Uppercase `AND` joins required factors. The compound blocks are:

- `G_model_fixed OR G_mission_exact OR (G_mission AND M_B)`
- `G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B)`
- `C1_fixed OR G_DSL`
- `P AND M_B AND T_precise` for BT2

Each wildcard family uses `NOFT(stem[*n])`. A multiword pattern keeps the whole ordered phrase in straight double quotes. The bound is the smallest value that covers every declared suffix. Singleton terms, punctuation alternatives, spacing alternatives, and unsafe stems remain literal.

The candidate uses 128 bounded wildcard families. They replace 292 explicit term occurrences across the ordinary blocks. Every partition remains one source expression.

| Partition | Literal characters | Wildcard characters | Reduction | Wildcard operators |
|---|---:|---:|---:|---:|
| `A1` | 3,480 | 2,421 | 1,059 | 38 |
| `A2` | 4,325 | 2,939 | 1,386 | 48 |
| `A3` | 2,724 | 1,466 | 1,258 | 45 |
| `B1` | 2,350 | 1,758 | 592 | 20 |
| `B2` | 2,788 | 1,313 | 1,475 | 47 |
| `BG1` | 2,780 | 1,513 | 1,267 | 42 |
| `BG2` | 2,220 | 1,200 | 1,020 | 36 |
| `BC1` | 1,555 | 925 | 630 | 25 |
| `BT2` | 2,356 | 998 | 1,358 | 34 |

All expressions are below the adapter's 50,000-character limit. No event used a proximity operator, pair expansion, result-driven split, controlled term, degree or document-type limit, access restriction, or full-text limit.

## Controls and capture

Every event used the exact PQDT Global scope, `YR(2011-2026)`, `LA(English)`, `DateAsc` (Oldest first), and 20 records per page. Duplicate exclusion, spelling variants, form variants, Show variants, and Full text were frozen off.

Each event completed two full rendered passes. The passes reconciled the source total and complete ordered numeric PQDT document IDs. Successful JSON artifacts are bound by the adapter's create-only PQDT commit marker.

PQDT exposes year precision through `YR`. Records dated 2026 remain for later screening against the exact 2026-08-29 diagnostic cutoff. The language clause is metadata evidence. Full-report language remains a screening decision.

## Literal and wildcard comparison

Each wildcard event ran directly after its literal counterpart when source conditions allowed. Every pair returned the same complete IDs in the same source order.

| Partition | Literal total | Wildcard total | Sets | Order |
|---|---:|---:|---|---|
| `A1` | 1 | 1 | equal | equal |
| `A2` | 3 | 3 | equal | equal |
| `A3` | 1 | 1 | equal | equal |
| `B1` | 21 | 21 | equal | equal |
| `B2` | 13 | 13 | equal | equal |
| `BG1` | 1 | 1 | equal | equal |
| `BG2` | 3 | 3 | equal | equal |
| `BC1` | 3 | 3 | equal | equal |
| `BT2` | 1 | 1 | equal | equal |

No literal ID was missing from a wildcard result. There were no wildcard-only IDs to review. The literal and wildcard all-schedule unions each contain the same 29 distinct document IDs.

## Mandatory screenshots

Adapter version 5 derives `<stem>.search-page.png` and `<stem>.results-page.png` from every CLI JSON path. It provides no screenshot opt-out. The first PNG shows the fully configured Command Line Search form before submission. The second shows the hydrated first results page. The JSON retains each sibling filename, SHA-256, dimensions, email-mask count, and privacy state.

The 18 successful schedule events each have both sibling PNGs. The bounded [adapter smoke](searches/adapter-smoke/automatic-screenshot-smoke.json) returned one count-only result and automatically created both sibling PNGs. The pilot validates 38 successful-run PNGs in total, including the smoke pair.

## Retained failed attempts

Three null-total failure JSONs remain under [`searches/failures/`](searches/failures/). The first wildcard B1 attempt stopped before screenshot capture on an unexpected browser workflow failure. The first literal BC1 and BT2 attempts completed both screenshot captures, then failed closed because owned-page cleanup could not be verified. Their four PNGs remain beside the moved failure JSONs.

Fresh runs of the unchanged predeclared queries completed. They used new owned pages and empty create-only canonical destinations after the failed artifacts were moved intact to `failures/`. Failed attempts contributed no total, record, or ID to the assessment.

## Decision

Accept the current Boolean translation. Accept and prefer all 128 declared bounded wildcard families for every partition. Keep singleton terms, punctuation alternatives, spacing alternatives, and unsafe stems literal.

This pilot establishes complete document-ID equivalence and mandatory screenshot behavior. It does not create a final search. Final record collection still requires a fresh strict run, the fixed source controls, two complete ordered passes, a marker-bound output, both screenshots, and cutoff screening for 2026 records.

## Reproduction

Review-specific scripts are under [`SLR/SLR1/scripts/pqdt_pilot004`](../../../../scripts/pqdt_pilot004).

```bash
PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot004 \
python3 SLR/SLR1/scripts/pqdt_pilot004/build_plan.py --check

caffeinate -dims uv run \
  ~/agent-tools/internet/skills/browser/scripts/run_with_browser.py -- \
  python3 SLR/SLR1/scripts/pqdt_pilot004/run_pilot.py --resume

PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot004 \
python3 SLR/SLR1/scripts/pqdt_pilot004/build_assessment.py --inspect

PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot004 \
python3 SLR/SLR1/scripts/pqdt_pilot004/validate_pilot.py
```
