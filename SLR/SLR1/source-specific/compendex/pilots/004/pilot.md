# Pilot 004: Ei Thesaurus value test

Required changes were applied in commit: NA

This is a diagnostic pilot. Every artifact is non-mergeable. The diagnostic window is Published 2011-2026. The common evidence cutoff remains TBD. Screen records in the cutoff year against the later exact cutoff.

Export method: the fixed `search_compendex.py` adapter v15 through the shared authorized browser. The pilot-local runner uses the adapter's source controls, exact query readback, stable accessions, and native RIS functions. Its terminal one-page reconciliation adds a conservative diagnostic check without weakening the adapter contract.

## Objective

Validate assigned Compendex Ei Thesaurus candidates. Inspect exact identity, hierarchy, scope notes, and selected-record assignments. Test whether source-mapped P and context-qualified M_H descriptors add an accession beyond the current literal B1 translation.

## Current schedule boundary

[`preflight.json`](searches/preflight.json) pins the source translation to protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`. Every current term is an independent `("literal" WN ALL)` atom. The generated nine-partition schedule contains no proximity operator, pair expansion, or wildcard.

The commit changed BG1, BG2, BC1, and BT2. B1 remained `P AND M_H`. Pilot 003's changed-partition sets are superseded. This pilot uses its two B1 native RIS passes only for record-level assignment evidence.

## Assigned terms

[`assigned-controlled-terms.json`](searches/assigned-controlled-terms.json) reconciles eleven title-explicit CubeSat or nanosatellite MBSE/system-model records across the two private Pilot 003 B1 RIS passes. The ordered assignments were identical. The public artifact retains no raw RIS or private path.

The records supplied 51 distinct `KW` indexing terms. Candidate assignments were:

| Candidate | Assigned selected records |
|---|---:|
| `Nanosatellites` | 2 |
| `Small satellites` | 1 |
| `Systems engineering` | 7 |
| `Modeling languages` | 4 |
| `SysML` | 0 |

`Systems engineering` and `Modeling languages` were jointly assigned to three selected records. The selected records are known items for this vocabulary test. They are not final screening decisions.

## Ei Thesaurus validation

[`ei-thesaurus-candidates.json`](searches/ei-thesaurus-candidates.json) repeated every lookup twice through the licensed exact-term surface. The two passes returned the same identities, relations, and scope metadata.

| Term | Ei ID | Outcome |
|---|---:|---|
| `Nanosatellites` | `18096` | exact assigned P descriptor |
| `Small satellites` | `3444` | exact assigned P descriptor |
| `Systems engineering` | `8964` | exact assigned M_H context descriptor |
| `Modeling languages` | `18655` | exact assigned M_H modeling descriptor |
| `SysML` | `23054` | exact descriptor without selected-record assignment |
| `Model-based systems engineering` | none | no exact preferred term |
| `CubeSat` | none | no exact preferred term |

Each exact record exposed its broader, related, and narrower relations where present. Each scope page exposed an introduced date and related classification codes. No tested scope page exposed a prose note. The source exposed no hierarchy explosion or focus control. No hierarchy relation was added to a query.

The protocol prevents generic `Systems engineering` from satisfying M_H alone. The tested M_H candidate was:

```text
({Systems engineering} WN CV)
AND
({Modeling languages} WN CV)
```

The two P descriptors were joined with `OR`. Each controlled construction was joined to its complete normative free-text block with `OR`.

## Value comparison

[`value-comparison.json`](searches/value-comparison.json) links two independent captures for each cell under [`cells/`](searches/cells/). Positive known-set cells reproduced the assignment evidence. The two candidate-only cells are a lossless decomposition of augmented B1 minus current literal B1.

| Cell | Compendex total | Outcome |
|---|---:|---|
| Selected records × P descriptors | 3 | same three accessions in both passes |
| Selected records × context-qualified M_H | 3 | same three accessions in both passes |
| Selected records × `SysML` | 0 | explicit source zero twice |
| B1 M_H candidate-only route | 0 | explicit source zero twice |
| B1 P candidate-only route | 0 | explicit source zero twice |

The candidate-only accession union is empty. The tested descriptor augmentation added no current B1 record. The P and M_H controlled constructions each matched only 3 of 11 selected records, so controlled terms cannot replace free text.

## Adapter repair validation

The initial Pilot 004 run exposed a current portal change. Positive pages rendered the exact total, `1 of N pages`, rows, stable accessions, controls, and native RIS without a numeric result interval. The portal also rendered mirrored top and bottom Next anchors with the same legacy ID and briefly cleared the old rows after a Next click.

Adapter v15 treats the interval as optional corroboration and validates it when present. It scopes Next to the top `#query-bar` paginator and waits through the brief empty-row shell after one guarded click. It still requires exact total, page, row, control, stable-ID, and native RIS reconciliation.

Bounded live repair checks completed:

- A three-record Compendex strict two-pass run completed.
- A 26-record diagnostic crossed from page 1 to page 2.
- A paired strict two-pass DOI run returned one Compendex and one Inspec record.

The value cells were rerun under v15. Both positive known-set controls were accepted by the fixed adapter without a rendered interval. The pilot-local contract remains limited to a terminal one-page diagnostic. The adapter now supports guarded multi-page traversal. No final schedule was run.

## Decision

[`inclusion-assessment.json`](searches/inclusion-assessment.json) records `do_not_add_ei_thesaurus_supplement`.

- Four candidates have bounded exact mapping and assignment evidence.
- The context-qualified M_H construction follows the protocol.
- Both lossless B1 candidate-only routes returned source zero twice.
- The controlled constructions would omit most selected known records if used as replacements.
- `SysML` lacked selected-record assignment evidence.
- Direct preferred terms for `Model-based systems engineering` and `CubeSat` were absent.

Retain the complete post-proximity literal `ALL` schedule with no Ei Thesaurus supplement. Keep free text mandatory. Apply no explosion, focus, `MH`, or `CVM` restriction. This decision covers the tested P and M_H candidates. It does not establish the value of every possible descriptor for every other concept.

## Reproduction

Run from the repository root. `$EV_P003_B1_RIS` names the owner-only Pilot 003 B1 native directory and is never written to a public artifact.

```bash
python3 SLR/SLR1/source-specific/compendex/scripts/compendex_pilot004/build_preflight.py \
  --output SLR/SLR1/source-specific/compendex/pilots/004/searches/preflight.json

python3 SLR/SLR1/source-specific/compendex/scripts/compendex_pilot004/harvest_assigned_terms.py \
  --pass-1-dir "$EV_P003_B1_RIS/pass-1" \
  --pass-2-dir "$EV_P003_B1_RIS/pass-2" \
  --public-b1 SLR/SLR1/source-specific/compendex/pilots/003/searches/B1.json \
  --output SLR/SLR1/source-specific/compendex/pilots/004/searches/assigned-controlled-terms.json

caffeinate -dims python3 "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/source-specific/compendex/scripts/compendex_pilot004/validate_thesaurus_candidates.py \
  --assignments SLR/SLR1/source-specific/compendex/pilots/004/searches/assigned-controlled-terms.json \
  --output SLR/SLR1/source-specific/compendex/pilots/004/searches/ei-thesaurus-candidates.json \
  --failure-output SLR/SLR1/source-specific/compendex/pilots/004/searches/ei-thesaurus-candidates.NON_MERGEABLE_FAILURE.json

caffeinate -dims python3 "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/source-specific/compendex/scripts/compendex_pilot004/run_value_comparison.py \
  --assignments SLR/SLR1/source-specific/compendex/pilots/004/searches/assigned-controlled-terms.json \
  --candidates SLR/SLR1/source-specific/compendex/pilots/004/searches/ei-thesaurus-candidates.json \
  --output-dir SLR/SLR1/source-specific/compendex/pilots/004/searches/cells \
  --reconciliation SLR/SLR1/source-specific/compendex/pilots/004/searches/value-comparison.json \
  --failure-output SLR/SLR1/source-specific/compendex/pilots/004/searches/value-comparison.NON_MERGEABLE_FAILURE.json

python3 SLR/SLR1/source-specific/compendex/scripts/compendex_pilot004/build_assessment.py \
  --preflight SLR/SLR1/source-specific/compendex/pilots/004/searches/preflight.json \
  --assignments SLR/SLR1/source-specific/compendex/pilots/004/searches/assigned-controlled-terms.json \
  --candidates SLR/SLR1/source-specific/compendex/pilots/004/searches/ei-thesaurus-candidates.json \
  --comparison SLR/SLR1/source-specific/compendex/pilots/004/searches/value-comparison.json \
  --output SLR/SLR1/source-specific/compendex/pilots/004/searches/inclusion-assessment.json

python3 SLR/SLR1/source-specific/compendex/scripts/compendex_pilot004/validate_pilot.py
```
