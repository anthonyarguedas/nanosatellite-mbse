# E2 — EPS verification pathway map

EPS-modeled element count: **36**. Path rows: **306**.

## Common EPS verification paths

| eps_element | verification_mechanism | ivv_integration_level | study_count |
| --- | --- | --- | --- |
| power budgets | simulation-in-the-loop | simulation-in-the-loop | 10 |
| battery | simulation-in-the-loop | simulation-in-the-loop | 9 |
| battery | trade-study verification | simulation-in-the-loop | 9 |
| power budgets | trade-study verification | simulation-in-the-loop | 9 |
| power conditioning/distribution | simulation-in-the-loop | simulation-in-the-loop | 9 |
| solar panels | simulation-in-the-loop | simulation-in-the-loop | 9 |
| solar panels | trade-study verification | simulation-in-the-loop | 9 |
| loads | simulation-in-the-loop | simulation-in-the-loop | 8 |
| loads | trade-study verification | simulation-in-the-loop | 8 |
| power budgets | parametric checks | simulation-in-the-loop | 8 |
| battery | parametric checks | simulation-in-the-loop | 7 |
| margins | parametric checks | simulation-in-the-loop | 7 |
| margins | simulation-in-the-loop | simulation-in-the-loop | 7 |
| margins | trade-study verification | simulation-in-the-loop | 7 |
| modes | simulation-in-the-loop | simulation-in-the-loop | 7 |

_Showing 15 of 306 rows._


## EPS elements with verification/IV&V gaps

| eps_element | study_count | no_verification_count | no_ivv_count | top_verification_mechanisms | top_ivv_levels |
| --- | --- | --- | --- | --- | --- |
| battery | 25 | 5 | 7 | parametric checks (15); trade-study verification (14); requirements-in-the-loop (11); simulation-in-the-loop (10); virtual integration (8) | simulation-in-the-loop (9); none/not reported (7); executable/model-based checks (3); trace-linked verification artifacts (3); model-contained verification artifacts (2) |
| solar panels | 25 | 5 | 7 | parametric checks (15); trade-study verification (14); requirements-in-the-loop (11); simulation-in-the-loop (10); virtual integration (8) | simulation-in-the-loop (9); none/not reported (7); executable/model-based checks (3); trace-linked verification artifacts (3); model-contained verification artifacts (2) |
| power budgets | 23 | 5 | 6 | parametric checks (14); simulation-in-the-loop (12); trade-study verification (12); requirements-in-the-loop (11); virtual integration (7) | simulation-in-the-loop (10); none/not reported (6); executable/model-based checks (4); trace-linked verification artifacts (2); separate document only (1) |
| loads | 19 | 5 | 5 | parametric checks (11); simulation-in-the-loop (10); requirements-in-the-loop (9); trade-study verification (9); virtual integration (7) | simulation-in-the-loop (8); none/not reported (5); executable/model-based checks (4); trace-linked verification artifacts (2) |
| power conditioning/distribution | 18 | 4 | 5 | requirements-in-the-loop (10); simulation-in-the-loop (10); parametric checks (9); virtual integration (8); trade-study verification (7) | simulation-in-the-loop (9); none/not reported (5); trace-linked verification artifacts (2); executable/model-based checks (2) |
| interfaces | 16 | 4 | 5 | parametric checks (10); requirements-in-the-loop (9); simulation-in-the-loop (7); virtual integration (7); trade-study verification (6) | simulation-in-the-loop (6); none/not reported (5); executable/model-based checks (3); trace-linked verification artifacts (2) |
| modes | 14 | 4 | 4 | parametric checks (8); requirements-in-the-loop (8); simulation-in-the-loop (8); virtual integration (8); trade-study verification (7) | simulation-in-the-loop (7); none/not reported (4); trace-linked verification artifacts (2); executable/model-based checks (1) |
| margins | 14 | 2 | 2 | parametric checks (11); requirements-in-the-loop (9); trade-study verification (8); simulation-in-the-loop (7); virtual integration (6) | simulation-in-the-loop (7); executable/model-based checks (4); none/not reported (2); trace-linked verification artifacts (1) |
| other | 12 | 1 | 1 | requirements-in-the-loop (8); parametric checks (7); simulation-in-the-loop (5); trade-study verification (4); virtual integration (4) | simulation-in-the-loop (4); executable/model-based checks (3); model-contained verification artifacts (2); trace-linked verification artifacts (2); none/not reported (1) |
| degradation | 5 | 0 | 0 | parametric checks (3); trade-study verification (3); virtual integration (3); requirements-in-the-loop (2); simulation-in-the-loop (2) | executable/model-based checks (2); simulation-in-the-loop (2); trace-linked verification artifacts (1) |
| fault protection | 4 | 1 | 1 | requirements-in-the-loop (3); virtual integration (2); parametric checks (2); none/not reported (1); simulation-in-the-loop (1) | trace-linked verification artifacts (1); executable/model-based checks (1); none/not reported (1); simulation-in-the-loop (1) |
| abstract Power Subsystem | 1 | 0 | 0 | requirements-in-the-loop (1); requirements-in-the-loop at system/reference-model level (1); simulation-in-the-loop (1); simulation-in-the-loop/mission scenario execution at system level (1) | simulation-in-the-loop (1) |
| battery cycles as a CubeSat MOP | 1 | 0 | 1 | parametric checks (1); trade-study verification (1) | none/not reported (1) |
| battery/on-board energy storage | 1 | 0 | 0 | parametric checks (1); requirements-in-the-loop (1); simulation-in-the-loop (1); trade-study verification (1); virtual integration (1) | simulation-in-the-loop (1) |
| Current CRM: generic Power Subsystem placeholder in CubeSat subsystem architecture | 1 | 0 | 0 | Generic parametric checks via technical-measure constraint blocks/parametric diagrams (1); Generic satisfy/verify relationships for requirements (1); parametric checks (1); Prior RAX trade-study verification/analysis of solar panel area and battery capacity against on-board energy levels (1); trade-study verification (1) | trace-linked verification artifacts (1) |

_Showing 15 of 36 rows._


Interpretation note: `none/not reported` is retained when no controlled verification mechanism or IV&V level was coded for a study.
