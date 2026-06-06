# ISSUE-006 — Final validation report

Date: 2026-06-05

## Commands run

From repository root:

```bash
python3 SLR/SLR1/kge-experiments/scripts/run_pipeline.py
```

Additional validation commands/snippets run:

```bash
# Core ISSUE-006 required-artifact check and 40-study assertion.
python3 - <<'PY'
from pathlib import Path
# checked required core paths for existence/non-empty and asserted studies.jsonl == 40
PY

# Comprehensive ISSUE-001 through ISSUE-005 artifact presence and count validation.
python3 - <<'PY'
from pathlib import Path
# checked all required prior-issue outputs, JSONL/CSV row counts, vector shape, and hybrid SIMILAR_TO edges
PY

# README rerun/fallback/exploratory-status check.
python3 - <<'PY'
from pathlib import Path
# checked pipeline command, hashing_tfidf_v1, and exploratory wording in README.md
PY

git diff -- SLR/SLR1/extraction.json
```

Idempotence was validated by hashing generated artifacts under `data/`, `kg/`, `embeddings/`, and `outputs/`, rerunning:

```bash
python3 SLR/SLR1/kge-experiments/scripts/run_pipeline.py
diff -u /tmp/slr1_pipeline_hashes_before.txt /tmp/slr1_pipeline_hashes_after.txt
```

No differences were found across 71 generated artifact files before this final report was written.

## Artifact presence summary

All required artifacts from ISSUE-001 through ISSUE-005 were present and non-empty, including:

- flattened JSONL tables in `data/`;
- KG exports in `kg/` (`nodes.csv`, `edges.csv`, `graph.graphml`, Cypher, DuckDB SQL, manifest);
- embedding cards, deterministic `hashing_tfidf_v1` vectors, vectorizer metadata, manifest, and nearest-neighbor outputs in `embeddings/`;
- E0 through E13 tables/reports/graph exports under `outputs/`.

E0-E13 report/table coverage was confirmed: `e0_data_audit.md`, `e1_claim_evidence.md`, `eps_gap_map.md`, `e3_toolchain_interoperability.md`, `reusable_artifact_candidates.md`, `e5_limitation_gap_bottlenecks.md`, `lifecycle_artifact_evidence.md`, `e7_study_semantic_clustering.md`, `e8_claim_semantic_clustering.md`, `candidate_codebook_extensions.md`, `audit_queue.md`, `e11_hybrid_similarity_graph.md`, `graphrag_demo_questions.md`, and `e13_research_agenda_prioritization.md` / `future_research_agenda.md`.

## Key counts

| Metric | Count |
| --- | ---: |
| Studies | 40 |
| Study-code records | 7,370 |
| Claims | 270 |
| Limitations | 602 |
| Emergent codes | 345 |
| Evidence quotes | 15,937 |
| Gap mappings | 200 |
| KG nodes | 1,401 |
| KG edges | 8,034 |
| Embedding cards | 17,394 |
| Vector shape | 17,394 × 384 |
| Nearest-neighbor records | 86,970 |
| Audit queue rows | 60 |
| Hybrid graph nodes | 1,401 |
| Hybrid graph edges | 8,044 |
| Hybrid `SIMILAR_TO` edges | 10 |
| GraphRAG answer-source rows | 60 |
| Retrieval traces | 4 |
| Research-gap priority rows | 5 |

## README and source-diff checks

- `README.md` documents the repository-root pipeline command: `python3 SLR/SLR1/kge-experiments/scripts/run_pipeline.py`.
- `README.md` documents the deterministic offline `hashing_tfidf_v1` fallback.
- `README.md` labels semantic, hybrid-similarity, GraphRAG, and research-agenda outputs as exploratory synthesis aids.
- `git diff -- SLR/SLR1/extraction.json` produced no output; the source extraction was not modified.

## Minimal fixes made during validation

- Replaced run-time manifest timestamps in KG and embedding manifests with a deterministic timestamp derived from the source extraction `generated_at` value.
- Stabilized tie ordering in hybrid-community `top_node_types` and research-gap `top_limitation_flags` summaries so reruns are byte-stable.

## Known caveats and limitations

- Embeddings use deterministic lexical hashing-TFIDF (`hashing_tfidf_v1`), not a neural sentence embedding model.
- Semantic clusters and nearest neighbors are exploratory audit aids and require human review before interpretation.
- E7 projection/clustering uses dependency-light PCA/SVD and nearest-neighbor/component fallbacks rather than UMAP/HDBSCAN.
- E11 similarity thresholds are model/corpus-specific; claim-card similarity uses an audited fallback threshold because the implementation-plan neural-embedding threshold produced no claim edges with hashing-TFIDF.
- GraphRAG demo answers are local retrieval/graph-expansion demonstrations without external LLM/API calls.
- E13 gap prioritization is a transparent exploratory scoring over a 40-study corpus, not a statistical significance test.
