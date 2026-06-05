# KG + Embedding Experiments for SLR1

This folder contains reproducible knowledge-graph (KG), deterministic embedding, hybrid graph, GraphRAG-style, and research-agenda experiments over the read-only source extraction `SLR/SLR1/extraction.json`.

## Current assets

- `../extraction.json` — source structured extraction file; 40 studies, 47 controlled fields, claim-level evidence and limitations.
- `IMPLEMENTATION_PLAN.md` — full implementation plan and experiment backlog.
- `schema/kg_schema.md` — property-graph schema and mapping from extraction fields.
- `scripts/` — runnable pipeline scripts `01_flatten_extraction.py` through `09_research_agenda.py`, plus `run_pipeline.py`.
- `data/` — flattened JSONL tables for studies, controlled codes, claims, limitations, emergent codes, evidence quotes, and gap mappings.
- `kg/` — portable property-graph exports (`nodes.csv`, `edges.csv`, GraphML, Neo4j Cypher, DuckDB SQL).
- `embeddings/` — provenance-rich text cards, deterministic vectors, vectorizer metadata, manifest, and nearest-neighbor records.
- `outputs/tables/` — controlled-code analyses, semantic audit tables, GraphRAG answer sources, and research-gap priorities.
- `outputs/reports/` — E0–E13 reports, GraphRAG answers/traces, audit notes, and future research agenda.
- `outputs/graph_exports/` and `outputs/figures/` — GraphML exports and dependency-light figure/table substitutes.
- `references/`, `papers/`, and `searches/` — background KG+embedding literature assets used to shape the plan.

## What the pipeline generates

The full pipeline normalizes the extraction, builds a KG, runs controlled graph analyses (E1–E6), builds embedding cards and deterministic nearest neighbors, runs semantic clustering/audit and hybrid similarity graph analyses (E7–E11), produces an exploratory GraphRAG demo (E12), and ranks future research gaps (E13).

Key final outputs include:

- `outputs/reports/graphrag_demo_questions.md`
- `outputs/reports/graphrag_limitations.md`
- `outputs/reports/retrieval_traces.jsonl`
- `outputs/tables/graphrag_answer_sources.csv`
- `outputs/tables/research_gap_priorities.csv`
- `outputs/reports/future_research_agenda.md`
- `outputs/reports/e13_research_agenda_prioritization.md`

## Rerun from repository root

```bash
python3 SLR/SLR1/kge-experiments/scripts/run_pipeline.py
```

Individual stages can also be run directly from the repository root, for example:

```bash
python3 SLR/SLR1/kge-experiments/scripts/08_graphrag_demo.py
python3 SLR/SLR1/kge-experiments/scripts/09_research_agenda.py
```

## Dependencies and embedding fallback

The default embedding/index path uses `hashing_tfidf_v1`, a deterministic offline TF-IDF-style hashing vectorizer implemented with the Python standard library plus `numpy`. Heavyweight embedding, plotting, FAISS, UMAP, HDBSCAN, or API dependencies are not assumed. Where the implementation plan called for UMAP/HDBSCAN, the scripts document dependency-light PCA/SVD and thresholded-neighbor fallbacks.

## Provenance and quality controls

Generated insights preserve study IDs, claim IDs where applicable, field paths, controlled values, snippets/evidence quotes, and model/index metadata. Semantic, hybrid-similarity, GraphRAG, and research-agenda outputs are exploratory synthesis aids over a 40-study corpus; they do not modify the source extraction and should not be treated as statistically significant or as automatic corrections to the SLR coding.
