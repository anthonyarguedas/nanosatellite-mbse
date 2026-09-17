# Pilot 005: exact candidate-union gate counts

Required changes were applied in commit: 38aedc3de4731e0da5f063a053e92ebd88a84db0

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`

## Objective

Replace the fragile 1,249-record `P`-only hydration route with smaller exact Boolean gates. Test every gate by count only under the same English metadata and 2011 through 2026 controls. This is a diagnostic pilot. It is not a final search.

## Exact union identity

The eight accepted gates retain every schedule literal and Boolean branch:

```text
(P AND M_H)
OR (P AND M_B AND E_F)
OR (P AND M_B AND E_H)
OR (P AND M_B AND R)
OR (P AND M_B AND T_precise)
OR (P AND G_model)
OR (P AND G_structure)
OR (P AND C1)
```

This union equals the original nine-partition union. `B1` contains `A1` and the `M_H` branch of `A2`. The four `M_B` gates cover the remaining `A2` branch, `A3`, `B2`, and `BT2`. The final three gates equal `BG1`, `BG2`, and `BC1`. The [split continuation plan](searches/split-continuation-plan.json) records the branch mapping and exact queries.

No gate adds a term, wildcard, proximity operator, filter, or result-derived refinement. Every complete route was between 1,608 and 2,775 characters including English and year controls, below the adapter's 8,000-character ceiling.

## Runs

The [initial plan](searches/event-plan.json) imposed a 30-minute cooldown after Pilot 004's HTTP 504, used count-only requests, waited two minutes between events, and stopped after the first failure.

`G1-MH` completed with exact query readback and total `16`. Its JSON, terminal marker, and both mandatory screenshots were valid. The [initial runner](searches/run-receipt.json) stopped because it incorrectly asked the generic merger to admit this deliberately nonmergeable count artifact. Generic admission correctly returned false. The [first continuation](searches/continuation-plan.json) adopted the marker-bound count without repeating the source request.

The combined `G2-MB` route did not become ready within 180 seconds. It has no query readback or total. The [first continuation receipt](searches/continuation-run-receipt.json) retains this null failure. Four exact smaller branches replaced it after another 30-minute cooldown.

The [split continuation receipt](searches/split-continuation-run-receipt.json) completed all seven remaining count events. Every successful event used exact query readback, opened no Record Details page, remained nonmergeable, and retained both mandatory screenshots and a terminal marker.

| Gate | Original coverage | Total |
|---|---|---:|
| `G1-MH` | `B1`, including `A1` and the `M_H` arm of `A2` | 16 |
| `G2A-MB-EF` | `M_B` arm of `A2` | 2 |
| `G2B-MB-EH` | `A3` | 2 |
| `G2C-MB-R` | `B2` | 10 |
| `G2D-MB-T` | `BT2` | 0 |
| `G3-GMODEL` | `BG1` | 0 |
| `G4-GSTRUCTURE` | `BG2` | 3 |
| `G5-C1` | `BC1` | 1 |

The gate occurrence total is `34`. Cross-gate duplicates are unresolved because count-only events expose no stable-ID sets. Therefore `34` is an upper bound, not an exact union total. It is 97.278% below the dated `P`-only total of `1,249`. The largest individual gate returned `16`.

The [assessment](searches/assessment.json) records the arithmetic and decision. The [validation report](searches/validation-report.json) revalidated all eight artifacts, 16 screenshots, terminal markers, exact counts, the null combined-gate failure, and the algebraic branch mapping.

## Result

Retire the broad `P`-only detail harvest. Use these eight exact gates in the next card-ID union pilot. That pilot must collect complete stable-ID snapshots for every gate, reconcile each gate, deduplicate the cross-gate union, preserve gate provenance, and hydrate each unique union ID once.

Pilot 005 establishes no exact candidate-union total and creates no final-search artifact. Final execution remains open until the ID-union route passes complete capture and checkpoint validation.
