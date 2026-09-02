# Pilot 004: linked current schedule and population wildcards

**Status:** passed. This is not a final search.

Required changes were applied in commit: NA

Export method: adapter version 16 at `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py` through the authorized Engineering Village browser.

## Objective

Pilot all nine Inspec partitions from protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`. Use the tested trailing population wildcards and no proximity operator or pair expansion. Confirm strict complete capture and both mandatory screenshots.

## Linked paired method

The fixed Engineering Village route selects Compendex and Inspec in one source event. Compendex Pilots 005 and 008 already ran predeclared paired events and retained each database projection separately. This pilot assesses the existing Inspec projections. It submitted no duplicate source event.

The [linked evidence plan](searches/linked-evidence-plan.json) identifies every source artifact and hash. The [assessment](searches/assessment.json) independently checks the exact current queries, controls, database labels, strict receipts, accessions, and PNG receipts.

## Wildcard evidence

Compendex Pilot 005 included separate complete Inspec projections for literal and wildcard `A1`. Both events completed two strict source passes and returned the same three Inspec accessions:

```text
16661315
23201028
26519151
```

The candidate changes only eight population literals:

| Wildcard atom | Replaced literals |
|---|---|
| `(CubeSat* WN ALL)` | `CubeSat`, `CubeSats` |
| `(nanosat* WN ALL)` | `nanosat`, `nanosats`, `nanosatellite`, `nanosatellites` |
| `(SmallSat* WN ALL)` | `SmallSat`, `SmallSats` |

Every other population term and every term in the other blocks stays literal. The adapter keeps Expert autostemming off. The [source translation approval](searches/source-translation-approval.json) accepts these three wildcard atoms in all nine Inspec schedule entries. It accepts no additional `*`, `?`, or manual `$` form.

## Current schedule results

Compendex Pilot 008 executed each current expression with the three population wildcards. Every accepted paired artifact completed two strict passes. The source-specific totals below contain only rows labelled `Inspec (Engineering Village)`.

| Partition | Inspec total | Strict passes | Screenshots |
|---|---:|---:|---:|
| `A1` | 3 | 2 | 2 |
| `A2` | 14 | 2 | 2 |
| `A3` | 4 | 2 | 2 |
| `B1` | 91 | 2 | 2 |
| `B2` | 90 | 2 | 2 |
| `BG1` | 2 | 2 | 2 |
| `BG2` | 8 | 2 | 2 |
| `BC1` | 19 | 2 | 2 |
| `BT2` | 5 | 2 | 2 |

The nine events supply 18 strict source passes and 18 mandatory screenshots. They use Published 2011 through 2026, raw `(English WN LA)`, Date (Oldest), 25 rows per rendered page, and no document type, access, or controlled vocabulary refinement.

`BG1`, `BG2`, `BC1`, and `BT2` use the current compound definitions:

- `G_model_fixed OR G_mission_exact OR (G_mission AND M_B)`
- `G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B)`
- `C1_fixed OR G_DSL`
- `P AND M_B AND T_precise`

## Mandatory screenshot contract

Adapter version 16 derives `<name>.search-page.png` and `<name>.results-page.png` from every JSON output path. It exposes no opt-out. A successful event requires both sibling PNGs and matching hash and dimension receipts.

All nine linked current-schedule JSON artifacts have both PNGs in the same directory. The configured-search image records the Expert form before submission. The results image records the verified first results page. The assessment verified every file against its JSON receipt. The shared bounded adapter validation also passed seven focused offline tests and a strict paired live check containing an Inspec record.

## Reconciliation and decision

The [Inspec reconciliation](searches/reconciliation.json) contains 162 unique stable accessions from 236 partition occurrences. It preserves complete partition provenance and contains no Compendex accession. The full ledger is retained because the union exceeds 100 records.

Accept the current no-proximity schedule with the three tested population wildcards. Keep all other ordinary terms literal. Add no Inspec Thesaurus supplement from this pilot.

The paired adapter route is ready for a separate final search. The final search must create fresh artifacts under `final-searches/` with the final common cutoff. No pilot record enters screening.

## Reproduction

Run from the repository root. The builder and validator read the immutable paired artifacts and make no source request.

```bash
PYTHONPATH=SLR/SLR1/scripts/inspec_pilot004 \
python3 SLR/SLR1/scripts/inspec_pilot004/build_linked_assessment.py

PYTHONPATH=SLR/SLR1/scripts/inspec_pilot004 \
python3 SLR/SLR1/scripts/inspec_pilot004/validate_pilot.py
```
