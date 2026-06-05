# E9 — Candidate codebook extensions and emergent-code consolidation

**Exploratory notice:** near-duplicate/consolidation candidates are generated from `hashing_tfidf_v1` hashing-TFIDF vectors and thresholded connected components. They are suggestions for codebook review only.

Emergent-code cards: **345**. Clusters: **337**. Candidate duplicate/near-duplicate clusters: **7**.
Cluster threshold: `0.55`.

## Likely duplicate or near-duplicate emergent-code clusters

| cluster_id | cluster_size | max_pair_similarity | candidate_codebook_extension | labels | field_paths | emergent_code_ids |
| --- | --- | --- | --- | --- | --- | --- |
| emergent_cluster_001 | 3 | 0.662612 | object-oriented-systems-engineering-method-oosem; oosem-method; oosem-methodology | object-oriented-systems-engineering-method-oosem; oosem-method; oosem-methodology | toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool=other | paper-0016::emergent-01; paper-0022::emergent-01; paper-0031::emergent-01 |
| emergent_cluster_007 | 2 | 0.876745 | artisan-studio; para-solver | artisan-studio; para-solver | toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool | paper-0079::emergent-04; paper-0079::emergent-05 |
| emergent_cluster_004 | 2 | 0.734859 | project-deliverable-availability-as-value-indicator; project-management-pbs-wbs-cbs-modeling-scope | project-deliverable-availability-as-value-indicator; project-management-pbs-wbs-cbs-modeling-scope | claimed_outcomes_value_mechanisms_evidence[].metric_or_value_indicator; mbse_objective_scope_artifacts.modeling_scope | paper-0023::emergent-01; paper-0023::emergent-07 |
| emergent_cluster_006 | 2 | 0.664910 | object-process-methodology-opm; opcloud-environment | object-process-methodology-opm; opcloud-environment | synthesis_consistency | paper-0068::emergent-01; paper-0068::emergent-02 |
| emergent_cluster_003 | 2 | 0.583894 | csrm-omg-candidate-specification; unnamed-graphical-modeling-tool | csrm-omg-candidate-specification; unnamed-graphical-modeling-tool | mbse_objective_scope_artifacts.generality_reuse_mechanism; toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool | paper-0014::emergent-01; paper-0014::emergent-06 |
| emergent_cluster_002 | 2 | 0.567682 | csrm-rax-incose-sswg-lineage; rax-incose-sswg-cube-sat-reference-model-lineage | csrm-rax-incose-sswg-lineage; rax-incose-sswg-cube-sat-reference-model-lineage | bibliographic_review_management | paper-0001::emergent-06; paper-0011::emergent-10 |
| emergent_cluster_005 | 2 | 0.562990 | ndsat-example-satellite-concept; rml-process-flow-diagrams | ndsat-example-satellite-concept; rml-process-flow-diagrams | mbse_objective_scope_artifacts.model_artifacts_used=other; study_context_population.model_maturity | paper-0034::emergent-03; paper-0034::emergent-05 |


## Codebook-extension interpretation

Rows in `outputs/tables/emergent_code_clusters.csv` include the original label, field path, rationale, evidence quote, and a `duplicate_or_near_duplicate_candidate` flag. Clusters with multiple studies or repeated labels are good candidates for controlled-vocabulary review.
