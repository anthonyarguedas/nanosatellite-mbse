# ISSUE-004 — Semantic clustering, consistency audit, and hybrid similarity graph E7-E11

## Objective

Implement semantic experiments E7-E11 from `IMPLEMENTATION_PLAN.md` using the local embedding artifacts and KG artifacts produced by earlier issues.

This issue depends on:

- ISSUE-001 flattening outputs (`data/*.jsonl`)
- ISSUE-002 KG outputs (`kg/nodes.csv`, `kg/edges.csv`, `kg/graph.graphml`)
- ISSUE-003 embedding outputs (`embeddings/card_index.jsonl`, `embeddings/vectors_hashing_tfidf_v1.npy`, `embeddings/nearest_neighbors.jsonl`)

## Repository context

- Working directory: repository root `nanosatellite-mbse`.
- Experiment folder: `SLR/SLR1/kge-experiments/`.
- Read before coding:
  - `SLR/SLR1/kge-experiments/IMPLEMENTATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/schema/kg_schema.md`
  - `SLR/SLR1/kge-experiments/ORCHESTRATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/issues/ISSUE-003-embedding-cards-and-neighbors.md`
- Source extraction must remain read-only.
- Environment: Python 3, `numpy`, `networkx` are available. Do not require pandas/scikit-learn/matplotlib/umap/hdbscan.

## Required implementation

Create these scripts:

1. `SLR/SLR1/kge-experiments/scripts/06_semantic_analyses.py`
2. `SLR/SLR1/kge-experiments/scripts/07_hybrid_graph.py`

### `06_semantic_analyses.py`

Generate E7-E10 outputs from embedding/card artifacts.

Because UMAP/HDBSCAN are not available, use deterministic dependency-light substitutes:

- Use PCA/SVD via `numpy.linalg.svd` for 2D projections. Name files clearly as PCA fallback while satisfying the intended 2D projection output.
- Use thresholded nearest-neighbor connected components and/or a simple deterministic agglomerative approach for clusters.
- Mark all semantic outputs as exploratory.

Required outputs:

E7 — Study semantic clustering:

- `outputs/tables/study_clusters.csv`
- `outputs/tables/study_projection.csv`
- `outputs/figures/study_umap.svg` (can be a PCA/SVD fallback SVG; note this in metadata/report)
- `outputs/reports/e7_study_semantic_clustering.md`
- Include approach class, EPS relevance, and model maturity columns where available.
- Include a disagreement list: semantically similar studies with different controlled labels.

E8 — Claim semantic clustering:

- `outputs/tables/claim_clusters.csv`
- `outputs/reports/weak_recurrent_claims.md`
- `outputs/reports/e8_claim_semantic_clustering.md`
- Summarize clusters by dominant outcome category, mechanism, and evidence confidence.

E9 — Emergent-code consolidation:

- `outputs/tables/emergent_code_clusters.csv`
- `outputs/reports/candidate_codebook_extensions.md`
- Identify likely duplicate/near-duplicate emergent code clusters.

E10 — Consistency and miscoding audit:

- `outputs/tables/audit_queue.csv`
- `outputs/reports/audit_queue.md`
- Flag potential review pairs such as:
  - semantically similar claims with different `evidence_confidence_rating`;
  - semantically similar studies with different `approach_classification`;
  - studies with similar EPS verification descriptions but different `ivv_integration_level`.
- Each audit row must include similarity score, IDs, differing controlled fields, snippets, and evidence/provenance when available.
- Do not make automatic corrections.

### `07_hybrid_graph.py`

Generate E11 hybrid similarity graph artifacts:

- Read `kg/nodes.csv`, `kg/edges.csv`, and embedding nearest neighbors.
- Add `SIMILAR_TO` edges for same-unit neighbors above audited thresholds. Initial thresholds from the implementation plan:
  - study cards: cosine >= 0.72
  - claim cards: cosine >= 0.78
  - emergent code cards: choose a documented threshold around 0.78 unless evidence suggests adjustment.
- Include edge properties: `model`, `cosine`, `unit_type`, `source='embedding_nearest_neighbors'`, and exploratory flag.
- Run NetworkX community detection or connected components on the combined graph.

Required outputs:

- `outputs/graph_exports/hybrid_similarity_graph.graphml`
- `outputs/tables/hybrid_communities.csv`
- `outputs/reports/e11_hybrid_similarity_graph.md`
- Optionally `kg/edges_with_similarity.csv` if useful; do not overwrite the base `kg/edges.csv` without clear documentation.

## Implementation guidance

- Reuse card metadata to map `card_id` back to `Study`, `Claim`, or `EmergentCode` KG node IDs.
- Preserve model metadata from `embeddings/embedding_manifest.json`.
- Make outputs deterministic and idempotent.
- If dependencies are missing, fail with a clear message about which earlier issue output must be generated.
- Keep the base KG unchanged; hybrid outputs should be clearly separate.

## Validation commands

Run from repository root:

```bash
python3 SLR/SLR1/kge-experiments/scripts/01_flatten_extraction.py
python3 SLR/SLR1/kge-experiments/scripts/02_build_kg.py
python3 SLR/SLR1/kge-experiments/scripts/04_build_embedding_cards.py
python3 SLR/SLR1/kge-experiments/scripts/05_embed_and_neighbors.py
python3 SLR/SLR1/kge-experiments/scripts/06_semantic_analyses.py
python3 SLR/SLR1/kge-experiments/scripts/07_hybrid_graph.py
python3 - <<'PY'
from pathlib import Path
base = Path('SLR/SLR1/kge-experiments')
required = [
    'outputs/tables/study_clusters.csv', 'outputs/tables/study_projection.csv',
    'outputs/figures/study_umap.svg', 'outputs/reports/e7_study_semantic_clustering.md',
    'outputs/tables/claim_clusters.csv', 'outputs/reports/weak_recurrent_claims.md',
    'outputs/reports/e8_claim_semantic_clustering.md', 'outputs/tables/emergent_code_clusters.csv',
    'outputs/reports/candidate_codebook_extensions.md', 'outputs/tables/audit_queue.csv',
    'outputs/reports/audit_queue.md', 'outputs/graph_exports/hybrid_similarity_graph.graphml',
    'outputs/tables/hybrid_communities.csv', 'outputs/reports/e11_hybrid_similarity_graph.md'
]
for rel in required:
    p = base / rel
    assert p.exists() and p.stat().st_size > 0, rel
print('ISSUE-004 outputs present')
PY
```

## Deliverables

- Semantic analysis and hybrid graph scripts.
- Generated E7-E11 outputs.
- Local git commit with message similar to: `Add semantic audits and hybrid similarity graph`.
- Final subagent response should include files changed, validation results, counts of clusters/audit rows/similarity edges, and caveats.

## Constraints

- Do not push.
- Do not modify source extraction data.
- Do not implement GraphRAG or research agenda scoring in this issue.
