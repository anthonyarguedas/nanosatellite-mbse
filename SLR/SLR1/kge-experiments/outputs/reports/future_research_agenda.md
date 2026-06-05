# Future research agenda from E13 gap prioritization

**Exploratory notice:** this agenda ranks research needs over the 40-study SLR1 extraction. It is a transparent prioritization aid, not a statistical significance test.

## Ranked priorities

| rank | gap | gap_priority_score | frequency | weak_evidence_weight | eps_specificity_weight | model_unavailable_study_count | recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | newspace_agile_distributed_rapid_iteration_alignment | 175.30 | 34 | 79.30 | 14.00 | 28 | Design and evaluate MBSE workflows for rapid, distributed NewSpace iteration, including evidence from multi-team use, versioned model repositories, and independent validation beyond concept demonstrations. |
| 2 | governance_project_deliverables_roi | 154.50 | 33 | 59.50 | 14.00 | 30 | Connect models to project deliverables, governance gates, cost/schedule baselines, and ROI evidence; prioritize studies with explicit comparators and decision records. |
| 3 | lightweight_resource_constrained_tailoring | 111.40 | 25 | 40.90 | 9.50 | 22 | Develop lightweight EPS/nanosatellite-specific tailoring patterns that preserve verification rigor while reducing modeling burden for resource-constrained teams. |
| 4 | toolchain_fragmentation_interoperability | 101.10 | 21 | 40.60 | 8.50 | 20 | Evaluate open, interoperable toolchains with reproducible transformations, APIs/co-simulation links, and traceable data handoffs across SysML, analysis, simulation, and requirements tools. |
| 5 | practical_implementation_pathway | 47.20 | 11 | 16.20 | 4.00 | 10 | Publish implementation playbooks, reference workflows, and reusable artifacts with evidence from project application and independent replication. |


## Recommended agenda items

### 1. `newspace_agile_distributed_rapid_iteration_alignment`

- Priority score: **175.30** using `e13_gap_priority_v1`.
- Evidence need: 34 under-addressed studies out of 40 mapped studies; levels = addressed with evidence 6, conceptual 11, mentioned only 15, not addressed 8.
- Main signals: weak evidence weight 79.30; EPS-specific need 14.00; lifecycle undercoverage 17.00; model unavailability 14.00; independent/physical validation gap 17.00.
- Proposed focus: Design and evaluate MBSE workflows for rapid, distributed NewSpace iteration, including evidence from multi-team use, versioned model repositories, and independent validation beyond concept demonstrations.
- Example contributing studies: paper-0031; paper-0005; paper-0013; paper-0015; paper-0003; paper-0022; paper-0077; paper-0011; paper-0023; paper-0080

### 2. `governance_project_deliverables_roi`

- Priority score: **154.50** using `e13_gap_priority_v1`.
- Evidence need: 33 under-addressed studies out of 40 mapped studies; levels = addressed with evidence 7, conceptual 20, mentioned only 13, not addressed 0.
- Main signals: weak evidence weight 59.50; EPS-specific need 14.00; lifecycle undercoverage 16.50; model unavailability 15.00; independent/physical validation gap 16.50.
- Proposed focus: Connect models to project deliverables, governance gates, cost/schedule baselines, and ROI evidence; prioritize studies with explicit comparators and decision records.
- Example contributing studies: paper-0031; paper-0005; paper-0013; paper-0015; paper-0003; paper-0022; paper-0077; paper-0011; paper-0080; paper-0004

### 3. `lightweight_resource_constrained_tailoring`

- Priority score: **111.40** using `e13_gap_priority_v1`.
- Evidence need: 25 under-addressed studies out of 40 mapped studies; levels = addressed with evidence 15, conceptual 21, mentioned only 3, not addressed 1.
- Main signals: weak evidence weight 40.90; EPS-specific need 9.50; lifecycle undercoverage 12.50; model unavailability 11.00; independent/physical validation gap 12.50.
- Proposed focus: Develop lightweight EPS/nanosatellite-specific tailoring patterns that preserve verification rigor while reducing modeling burden for resource-constrained teams.
- Example contributing studies: paper-0031; paper-0005; paper-0013; paper-0015; paper-0003; paper-0022; paper-0077; paper-0011; paper-0080; paper-0004

### 4. `toolchain_fragmentation_interoperability`

- Priority score: **101.10** using `e13_gap_priority_v1`.
- Evidence need: 21 under-addressed studies out of 40 mapped studies; levels = addressed with evidence 19, conceptual 13, mentioned only 6, not addressed 2.
- Main signals: weak evidence weight 40.60; EPS-specific need 8.50; lifecycle undercoverage 10.50; model unavailability 10.00; independent/physical validation gap 10.50.
- Proposed focus: Evaluate open, interoperable toolchains with reproducible transformations, APIs/co-simulation links, and traceable data handoffs across SysML, analysis, simulation, and requirements tools.
- Example contributing studies: paper-0031; paper-0005; paper-0013; paper-0015; paper-0022; paper-0077; paper-0011; paper-0023; paper-0004; paper-0016

### 5. `practical_implementation_pathway`

- Priority score: **47.20** using `e13_gap_priority_v1`.
- Evidence need: 11 under-addressed studies out of 40 mapped studies; levels = addressed with evidence 29, conceptual 11, mentioned only 0, not addressed 0.
- Main signals: weak evidence weight 16.20; EPS-specific need 4.00; lifecycle undercoverage 5.50; model unavailability 5.00; independent/physical validation gap 5.50.
- Proposed focus: Publish implementation playbooks, reference workflows, and reusable artifacts with evidence from project application and independent replication.
- Example contributing studies: paper-0031; paper-0015; paper-0022; paper-0077; paper-0011; paper-0004; paper-0016; paper-0014; paper-0010; paper-0034

## Lifecycle evidence context from E6

Lifecycle coverage is used as a quality-control context for the lifecycle-undercoverage component; it is not a separate statistical model.

| lifecycle_stage | study_count | claim_count | weak_or_unsupported_claims | moderate_or_strong_claims | verification_artifact_count |
| --- | --- | --- | --- | --- | --- |
| concept/pre-Phase A | 36 | 193 | 133 | 60 | 32 |
| Phase A/B | 24 | 137 | 93 | 44 | 24 |
| implementation | 21 | 69 | 57 | 12 | 21 |
| integration and test | 14 | 31 | 28 | 3 | 26 |
| operations | 18 | 34 | 24 | 10 | 22 |
| not reported | 9 | 15 | 15 | 0 | 12 |
| PDR | 3 | 10 | 6 | 4 | 5 |
| CDR | 3 | 8 | 5 | 3 | 5 |
| conceptual design | 1 | 0 | 0 | 0 | 0 |
| detailed design | 1 | 0 | 0 | 0 | 0 |


## Caveats

- Gap mappings appear for every study; the ranking therefore emphasizes under-addressed mappings (`addressed conceptually`, `mentioned only`, `not addressed`) rather than raw mapping presence alone.
- Limitation flags such as `no_independent_validation` and `incomplete_lifecycle_coverage` are frequent across this corpus, so they should be interpreted as systematic bottleneck signals, not study-level blame.
- Model availability is inferred from extracted limitation/reproducibility fields and was not rechecked online.
