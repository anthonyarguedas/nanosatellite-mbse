# E11 — Hybrid similarity graph

**Exploratory notice:** `SIMILAR_TO` edges are embedding-derived audit links from `hashing_tfidf_v1` nearest neighbors. They are not controlled-code assertions and do not modify the base KG.

## Inputs and graph construction

- Base KG input: `kg/nodes.csv` (**1401** nodes) and `kg/edges.csv` (**8034** edges).
- Embedding input: `embeddings/nearest_neighbors.jsonl` plus card metadata from `embeddings/card_index.jsonl`.
- Hybrid output: `outputs/graph_exports/hybrid_similarity_graph.graphml`.
- Base `kg/edges.csv` was not overwritten.

## Thresholds and similarity-edge counts

| unit_type | plan_threshold | audited_threshold_used | plan_directed_neighbor_records | audited_directed_neighbor_records | deduplicated_similarity_edges |
| --- | --- | --- | --- | --- | --- |
| study_card | 0.72 | 0.72 | 2 | 2 | 1 |
| claim_card | 0.78 | 0.65 | 0 | 16 | 8 |
| emergent_code_card | 0.78 | 0.78 | 2 | 2 | 1 |


The implementation-plan claim threshold (`0.78`) produced zero claim-card edges with the deterministic hashing-TFIDF fallback, whose nearest-neighbor cosine range is compressed relative to neural sentence embeddings. For E11, the audited claim threshold is lowered to `0.65` and documented here; study (`0.72`) and emergent-code (`0.78`) thresholds retain the plan values.

Total deduplicated `SIMILAR_TO` edges added: **10**.
Hybrid graph total: **1401** nodes and **8044** edges.

## Highest-similarity edges

| unit_type | source_node | target_node | cosine | threshold |
| --- | --- | --- | --- | --- |
| emergent_code_card | emergentcode::artisan_studio | emergentcode::para_solver | 0.876745 | 0.78 |
| study_card | paper-0043 | paper-0054 | 0.72583 | 0.72 |
| claim_card | paper-0016::claim-05 | paper-0031::claim-09 | 0.680094 | 0.65 |
| claim_card | paper-0005::claim-03 | paper-0015::claim-05 | 0.66812 | 0.65 |
| claim_card | paper-0016::claim-06 | paper-0022::claim-06 | 0.665046 | 0.65 |
| claim_card | paper-0011::claim-03 | paper-0014::claim-02 | 0.658266 | 0.65 |
| claim_card | paper-0005::claim-06 | paper-0016::claim-06 | 0.655876 | 0.65 |
| claim_card | paper-0004::claim-06 | paper-0022::claim-05 | 0.654655 | 0.65 |
| claim_card | paper-0005::claim-01 | paper-0077::claim-01 | 0.654451 | 0.65 |
| claim_card | paper-0016::claim-06 | paper-0031::claim-10 | 0.650418 | 0.65 |


## Communities

Community method: `networkx.greedy_modularity_communities(weighted undirected projection)` over an undirected weighted projection of controlled-code and similarity edges.
Communities detected: **2**.

| community_id | node_count | similarity_edge_count_internal | study_count | claim_count | emergent_code_count | representative_studies | representative_claims |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hybrid_community_002 | 361 | 8 | 0 | 270 | 0 |  | paper-0008::claim-03; paper-0078::claim-05; paper-0023::claim-07; paper-0026::claim-01; paper-0081::claim-07; paper-0003::claim-04; paper-0027::claim-05; paper-0054::claim-06 |
| hybrid_community_001 | 1040 | 2 | 40 | 0 | 340 | paper-0003; paper-0008; paper-0022; paper-0013; paper-0031; paper-0023; paper-0001; paper-0027 |  |


Caveats: the local embedding fallback is lexical hashing-TFIDF, so thresholds are corpus/model-specific. Similarity edges should be manually inspected before they are used as evidence.
