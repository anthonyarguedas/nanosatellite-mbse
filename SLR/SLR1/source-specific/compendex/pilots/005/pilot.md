# Pilot 005: A1 trailing wildcard comparison

Required changes were applied in commit: NA

Export method: the strict Python API of `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py` through the shared authorized browser.

Pilot 005 is diagnostic. Every artifact is non-mergeable. The source window is Published 2011-2026. The common evidence cutoff remains TBD. Screen records in the cutoff year against the later exact cutoff.

## Objective

Complete the wildcard comparison deferred by Pilot 002. Compare current literal A1 with one conservative three-family trailing `*` candidate under identical paired Compendex and Inspec controls. Base the Compendex decision on complete database-scoped stable-accession sets. Totals alone cannot support adoption.

## Predeclared candidate

The [event plan](searches/event-plan.json) was created before source execution. It pins protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`, the reviewed term snapshot, both source-affecting pilot scripts, and adapter v15.

The candidate changes only these A1 population atoms:

| Literal atoms | Candidate atom |
|---|---|
| `("CubeSat" WN ALL) OR ("CubeSats" WN ALL)` | `(CubeSat* WN ALL)` |
| `("nanosat" WN ALL) OR ("nanosats" WN ALL) OR ("nanosatellite" WN ALL) OR ("nanosatellites" WN ALL)` | `(nanosat* WN ALL)` |
| `("SmallSat" WN ALL) OR ("SmallSats" WN ALL)` | `(SmallSat* WN ALL)` |

Every other P term and every E_H and M_H term stays literal. Phrase order, punctuation, field wrappers, Boolean relationships, and controls are unchanged. The complete expression falls from 3,856 to 3,726 characters, a reduction of 130 characters (3.37%).

Engineering Village documents `*` as zero or more characters and a terminal `*` as truncation. The candidates can admit future suffix tokens such as `CubeSatellite`, `CubeSatellites`, `SmallSatellite`, and `SmallSatellites`, plus other terms with the same prefixes. The plan therefore required complete set evidence and prohibited adoption from equal totals alone.

## Runs

The [run receipt](searches/run-receipt.json) records two successful events:

- [literal A1](searches/cells/literal-A1.json)
- [wildcard A1](searches/cells/wildcard-A1.json)

Each event completed two independent source-exhaustive passes. The four source passes used native RIS for every record and reconciled the same ordered database-scoped accessions within each event. Both events had exact source query echo and identical controls:

- Compendex and Inspec selected together, database mask `3`
- Published 2011-2026, Updates inactive
- raw `(English WN LA)`
- Expert autostemming off
- Date (Oldest), 25 records per rendered page
- no document type, Open Access, or controlled-vocabulary restriction

Raw licensed RIS was reconciled in memory and was not persisted. No failed or partial attempt was retained.

## Complete set comparison

The [assessment](searches/assessment.json) keeps the two database projections separate.

| Database | Literal | Wildcard | Literal IDs missing | Wildcard-only IDs | Result |
|---|---:|---:|---:|---:|---|
| Compendex | 6 | 6 | 0 | 0 | equal complete sets |
| Inspec | 3 | 3 | 0 | 0 | equal complete sets |
| Paired event | 9 | 9 | 0 | 0 | descriptive sum only |

The ordered Compendex accession sequence was identical in both events:

```text
20142217768546
20171603573466
20241215772241
20232514262795
20251518218533
20263421355398
```

The ordered Inspec sequence was also identical: `16661315`, `23201028`, and `26519151`.

Historical Pilot 003 A1 had five Compendex records and three Inspec records. The current literal baseline adds Compendex accession `20263421355398`. This corpus update makes the current complete literal event the comparison baseline.

## Decision

The predeclared assessment accepted the three-family population compression for Compendex A1. The reviewer subsequently approved the same translation for **all nine Compendex schedule entries**. The [source translation approval](searches/source-translation-approval.json) records this later decision without changing the pilot's A1 evidence scope.

Apply these replacements in every `F(P)` block:

- `CubeSat` and `CubeSats` become `CubeSat*`
- `nanosat`, `nanosats`, `nanosatellite`, and `nanosatellites` become `nanosat*`
- `SmallSat` and `SmallSats` become `SmallSat*`

Use each unquoted wildcard token inside its own `WN ALL` atom. Preserve every other literal, phrase, field wrapper, and Boolean relationship. The paired Inspec projection remains separate, and its translation decision remains outside this Compendex pilot. Database updates can introduce new suffix completions, which remain subject to normal screening.

No `?`, manual stemming, autostemming, punctuation normalization, controlled term, or additional wildcard is accepted.

## Adapter v16 screenshot validation

The post-pilot [adapter validation](searches/adapter-v16-screenshot-validation.json) records seven focused offline tests and two bounded live checks. A one-record Compendex event and a two-record strict paired event each saved a full-page configured-search PNG and verified-results PNG beside the JSON. The JSON receipts matched both image hashes and dimensions. Each image masked the visible account identity element.

Adapter v16 exposes no screenshot opt-out. Strict execution captures both images during pass 1 and still completes the independent pass 2. The strict validation retained a usable marker-gated JSON/CSV pair. Temporary live-check outputs were removed after their safe metadata was recorded. These checks did not run a final search.

## Reproduction

Run from the repository root. The source runner refuses to overwrite an existing event and stops after the first failure.

```bash
PYTHONPATH=SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005 \
python3 SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005/build_plan.py \
  --output SLR/SLR1/source-specific/compendex/pilots/005/searches/event-plan.json

caffeinate -dims uv run \
  "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/compendex/pilots/005/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/compendex/pilots/005 \
  --receipt SLR/SLR1/source-specific/compendex/pilots/005/searches/run-receipt.json

PYTHONPATH=SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005 \
python3 SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/compendex/pilots/005 \
  --plan SLR/SLR1/source-specific/compendex/pilots/005/searches/event-plan.json \
  --run-receipt SLR/SLR1/source-specific/compendex/pilots/005/searches/run-receipt.json \
  --output SLR/SLR1/source-specific/compendex/pilots/005/searches/assessment.json

PYTHONPATH=SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005 \
python3 SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005/validate_pilot.py
```
