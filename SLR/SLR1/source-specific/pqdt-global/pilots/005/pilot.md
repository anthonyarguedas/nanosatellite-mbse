# Pilot 005: PQ Subject and Index term value test

Required changes were applied in commit: NA

This is a diagnostic pilot. It creates no final-search union. The source events use the same 2011 through 2026 window and 2026-08-29 diagnostic cutoff as Pilot 004. PQDT applies year precision, so later screening must check records from 2026 against the exact cutoff.

Export method: adapter version 5 at `~/agent-tools/internet/skills/browser/scripts/search_pqdt.py`, with the bounded [pilot union bridge](../../../../scripts/pqdt_pilot005/pqdt_union_bridge.py) described below.

## Objective

Inspect PQ Subject (`PSUB.EXACT`) and Index term (`IF.EXACT`) labels assigned to selected known records. Map valid candidates to protocol blocks. Compare the complete free-text schedule with free-text plus descriptor unions. Review every descriptor-only record before deciding whether to adopt a supplement.

The [preflight](searches/preflight.json) selected 14 Pilot 004 records whose title or abstract explicitly joins a CubeSat or nanosatellite case to MBSE, SysML, digital engineering, or structured system-model work. They are known items for this vocabulary test. Their selection is not a final eligibility decision.

## Assigned terms

The [assigned-term harvest](searches/assigned-terms.json) opened each record's source-created Abstract/Details view twice. It classified field assignments from the source's lateral-search routes:

- `mainsubject` is PQ Subject (`PSUB.EXACT`).
- `if` is Index term (keyword) (`IF.EXACT`).
- the broader `subject` route is context only and was not treated as either exact index.

Both complete passes returned the same ordered assignments. The 14 records contained nine distinct PQ Subject labels and 42 distinct Index term labels. Four records had `Systems engineering` as a PQ Subject. Index term assignments included population labels on nine records, mapped M_H labels on four, mapped M_B labels on three, and mapped R labels on five.

Three retained [assignment failures](searches/failures/) document an overstrict requirement that every record have a PQ Subject, a source menu that intercepted one Abstract/Details click, and shared-browser target churn. The active run accepts an empty field assignment, uses a bounded source click fallback, and preserves exact product, record, field-route, two-pass, privacy, cleanup, and scope checks.

## Candidate mapping and validation

The initial [candidate map](searches/candidate-map-initial.json) tested assigned capitalization. Its [initial validation](searches/candidate-validation-initial.json) found 24 exact labels and four absent exact labels. PQ Subject uses lower-case browse labels for `systems engineering` and `product design`. The Index term browse similarly exposes lower-case `system architecture`. The revised [candidate map](searches/candidate-map.json) tested these source forms.

The final [two-pass validation](searches/candidate-validation.json) tested 28 assigned candidates through the correct Subject or Index term browse, checkbox, and Add-to-search path. It verified 27 exact labels. Assigned Index term `Architecture` had no exact selectable label as `Architecture` or `architecture` and was excluded. Two retained [candidate-validation failures](searches/failures/) record shared-browser target changes before source interaction. The [validated map](searches/validated-candidate-map.json) contains:

| Protocol block | Validated construction |
|---|---|
| `P` | Ten exact IF labels for CubeSat, Cube Satellites, Small satellites, and narrower CubeSat phrases |
| `M_H` | Four specific IF labels, plus `(PSUB or IF Systems engineering) AND (IF System modeling or Executable modeling)` |
| `M_B` | Five exact IF labels for System modeling, Digital Engineering, Digital Twin, and System architecture model |
| `R` | Four exact IF architecture or requirements labels plus PSUB product design |

No assigned exact PSUB or IF candidate mapped safely to `E_H`, `E_F`, `G_model`, `G_structure`, `C1`, or `T_precise`. In particular, `Budgets` lacked an electrical power or energy qualifier. `Scalable systems architecture` established an R concern, not a reusable artifact.

PQDT exposes flat label indexes. It publishes no term IDs, vocabulary release, preferred-term relation, scope notes, hierarchy, explosion, focus, or major-topic state. The pilot requested none of those unsupported properties.

## Free-text and descriptor unions

The [event plan](searches/event-plan.json) predeclared 18 adjacent events. Each augmented query joins the validated descriptor construction to its complete free-text block with `OR`. Free text remains mandatory. Every event used exact PQDT scope, `YR(2011-2026)`, `LA(English)`, Oldest first, 20 records per page, and disabled duplicate, spelling, form, Show variants, and Full text controls.

The general adapter's typed-facet guard rejected the first augmented A1 command before source submission because the raw expression contained several IF clauses. The [pre-bridge plan](searches/event-plan.before-union-bridge.json) and [stopped receipt](searches/run-receipt.before-union-bridge.json) preserve that local failure. The pilot-local bridge permits several raw PSUB or IF clauses only when no typed Subject or Index term is requested. It leaves the raw query unchanged. Exact source query echo, strict two-pass traversal, stable IDs, source controls, screenshots, marker publication, scope restoration, and owned-page cleanup remain mandatory. The accepted final translation needs no bridge because it uses no descriptor supplement.

The active [run receipt](searches/run-receipt.json) validates all 18 strict events and 36 mandatory screenshots. The [set comparison](searches/set-comparison.json) found the same complete IDs in the same source order for every pair:

| Partition | Free text | Augmented | Descriptor only |
|---|---:|---:|---:|
| `A1` | 1 | 1 | 0 |
| `A2` | 3 | 3 | 0 |
| `A3` | 1 | 1 | 0 |
| `B1` | 21 | 21 | 0 |
| `B2` | 13 | 13 | 0 |
| `BG1` | 1 | 1 | 0 |
| `BG2` | 3 | 3 | 0 |
| `BC1` | 3 | 3 | 0 |
| `BT2` | 1 | 1 | 0 |

The free-text and augmented schedule unions each contain the same 29 numeric PQDT document IDs.

## Descriptor-only review

The predeclared review frame is the augmented schedule union minus the free-text schedule union. The [review artifact](searches/descriptor-only-review.json) records an empty frame because every partition pair was equal. Therefore zero descriptor-only records required concept review. This is a completed zero-record review, not an omitted review step.

## Decision

The [inclusion assessment](searches/inclusion-assessment.json) records `do_not_add_pq_subject_or_index_term_supplement`.

- The pilot established bounded record assignment and exact source mapping for 27 candidates.
- Every tested union retained its complete free-text baseline.
- No descriptor added a stable ID in any partition.
- The mapped labels cover only part of the selected known-record set and cannot replace free text.
- Adoption would add query and transport complexity without observed recall value.

Retain the accepted bounded-wildcard `NOFT` schedule without `PSUB.EXACT` or `IF.EXACT`. A new label requires another assigned-record mapping and complete no-loss value comparison before adoption.

## Reproduction

Run from the repository root.

```bash
PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot005 \
python3 SLR/SLR1/scripts/pqdt_pilot005/build_preflight.py --check

caffeinate -dims uv run \
  "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/scripts/pqdt_pilot005/harvest_assigned_terms.py

PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot005 \
python3 SLR/SLR1/scripts/pqdt_pilot005/build_candidate_map.py --check

caffeinate -dims uv run \
  "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/scripts/pqdt_pilot005/validate_candidates.py

PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot005 \
python3 SLR/SLR1/scripts/pqdt_pilot005/build_validated_map.py --check

PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot005 \
python3 SLR/SLR1/scripts/pqdt_pilot005/build_event_plan.py --check

caffeinate -dims uv run \
  "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/scripts/pqdt_pilot005/run_pilot.py --resume

PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot005 \
python3 SLR/SLR1/scripts/pqdt_pilot005/build_comparison.py --check

PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot005 \
python3 SLR/SLR1/scripts/pqdt_pilot005/build_descriptor_review.py --check

PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot005 \
python3 SLR/SLR1/scripts/pqdt_pilot005/build_assessment.py --check

PYTHONPATH=SLR/SLR1/scripts/pqdt_pilot005 \
python3 SLR/SLR1/scripts/pqdt_pilot005/validate_pilot.py
```
