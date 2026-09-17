# Completed OATD final searches

Completed on 2026-09-05 at 06:31:21 UTC. The successful final artifacts are in [`corrective-013/`](corrective-013/).

- **27 source records**, from 35 gate occurrences.
- **24 required gate passes validated**, with two initial passes and one final confirmation per gate.
- **27 full abstracts** in [`full-abstracts.json`](corrective-013/full-abstracts.json).
- **27 source publication types**, with native degree, degree level, language, and issued date metadata retained when present.
- **16 gate screenshots**, bound to their JSON artifacts by terminal markers.

## Files to use

| File | Purpose |
|---|---|
| [`corrective-013/hydrated-union.json`](corrective-013/hydrated-union.json) | Complete source discovery event and original OATD metadata |
| [`corrective-013/full-abstracts.json`](corrective-013/full-abstracts.json) | Complete screening metadata, including full abstracts and their provenance |
| [`corrective-013/gates/`](corrective-013/gates/) | Queries, all three ID passes per gate, hydrated records, and screenshots |
| [`corrective-013/validation-report.json`](corrective-013/validation-report.json) | Successful source, record, count, and terminal-marker validation |
| [`corrective-013/full-abstracts-validation.json`](corrective-013/full-abstracts-validation.json) | Successful full-abstract and provenance validation |
| [`corrective-013/assessment.json`](corrective-013/assessment.json) | Final source assessment |

Use `full-abstracts.json` for complete abstract text. Join its `records` to the source union by `paperId`. It preserves the same 27 IDs, original OATD abstracts, and gate provenance. It is a metadata sidecar and creates no additional discovery event. Count the source union once.

OATD supplied 18 complete displayed abstracts, eight truncated abstracts, and one absent abstract. Linked repository metadata and the Keio thesis abstract page supplied the nine complete replacements. All replacements match the source title and the entire available OATD abstract prefix when present.

`publicationType` describes the OATD ETD scope. Native Degree and Degree Level remain separate. These source values do not assign reviewer screening codes. Six records lack a native OATD degree level. Repository type evidence is retained where obtained.

## Gate totals

| Gate | Records |
|---|---:|
| G1-MH | 17 |
| G2A-MB-EF | 2 |
| G2B-MB-EH | 2 |
| G2C-MB-R | 10 |
| G2D-MB-T | 0 |
| G3-GMODEL | 0 |
| G4-GSTRUCTURE | 3 |
| G5-C1 | 1 |

The final confirmation matched both initial sets for every gate. Five additional gate passes supplied native detail contexts in the successful continuation. They add no discovery records.

## Audit and next step

The [code audit](code-audit/README.md) documents the corrected navigation, completeness, and metadata capture problems. Complete final passes and validated detail checkpoints were retained through declared continuations. No pilot record was reused. The earlier terminal failure assessment is superseded by this successful final assessment.

The common cutoff remains **2026-08-24**. Two 2026 records require exact date screening. Earlier failed attempts remain available as historical evidence and contribute no additional discovery events.
