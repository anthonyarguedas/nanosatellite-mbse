# E6 — Lifecycle coverage graph

Lifecycle stages represented: **10**. Graph nodes: **49**; edges: **274**.

## Lifecycle coverage by stage

| lifecycle_stage | study_count | claim_count | strong_claims | moderate_claims | weak_claims | unsupported_claims | verification_artifact_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| concept/pre-Phase A | 36 | 193 | 2 | 58 | 104 | 29 | 32 |
| Phase A/B | 24 | 137 | 2 | 42 | 71 | 22 | 24 |
| implementation | 21 | 69 | 0 | 12 | 41 | 16 | 21 |
| operations | 18 | 34 | 0 | 10 | 16 | 8 | 22 |
| integration and test | 14 | 31 | 0 | 3 | 21 | 7 | 26 |
| not reported | 9 | 15 | 0 | 0 | 8 | 7 | 12 |
| PDR | 3 | 10 | 0 | 4 | 5 | 1 | 5 |
| CDR | 3 | 8 | 0 | 3 | 3 | 2 | 5 |
| conceptual design | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| detailed design | 1 | 0 | 0 | 0 | 0 | 0 | 0 |


## Artifact/evidence interpretation

Later lifecycle stages (e.g., PDR, CDR, integration and test, operations) should be read against both claim counts and verification-artifact coverage. Counts are controlled-code co-occurrences; they do not imply that every artifact directly verifies every claim in the same study.
