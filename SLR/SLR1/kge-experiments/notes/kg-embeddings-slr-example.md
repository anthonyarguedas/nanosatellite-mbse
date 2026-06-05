# Closest Saved Examples: KG + Embeddings for Literature Review / SLR Outputs

## Best KG + retrieval/embedding example

**Xie, Song & Watson (2025)** — *A Knowledge Graph-Based RAG-GLLM Approach for Literature Review and Knowledge Discovery*

Saved PDF:

```text
SLR/SLR1/kge-experiments/papers/xie_2025_kg_rag_gllm_literature_review.pdf
```

Extracted text:

```text
SLR/SLR1/kge-experiments/notes/texts/xie_2025_kg_rag_gllm_literature_review.txt
```

Why it is useful:

- It explicitly argues that ordinary RAG over text embeddings is too fragmented for literature synthesis.
- It proposes a KG-based RAG/GLLM architecture where review knowledge is stored as nodes and edges.
- It defines five literature-review analysis levels: concept, relationship, model, theory, and theme.
- It shows an early prototype and benchmark for concept extraction.
- It is directly relevant to the planned GraphRAG experiment over `SLR/SLR1/extraction.json`.

Caveat:

- It is a research-in-progress paper, not a fully completed SLR case study.

## Best finished evidence-map / review-output example

**Mallavarapu et al. (2026)** — *Interactive Evidence Maps for Visualizing and Understanding Systematic Reviews*

Saved PDF:

```text
SLR/SLR1/kge-experiments/papers/mallavarapu_2026_interactive_evidence_maps.pdf
```

Extracted text:

```text
SLR/SLR1/kge-experiments/notes/texts/mallavarapu_2026_interactive_evidence_maps.txt
```

Why it is useful:

- It applies an LLM/topic-modeling pipeline to data from a published scoping review.
- It shows what a finished interactive evidence map can look like: studies as nodes, topic clusters, coded-field filters, details-on-demand, and navigation controls.
- It is the strongest saved example for the “finished product” style we could emulate for `SLR/SLR1/extraction.json`.

Caveat:

- It is not a formal KG paper; it is closer to an interactive knowledge/evidence map using topic modeling and structured review codes.

## Useful complete SLR about KG embeddings

**Doh et al. (2022)** — *A Systematic Review of Deep Knowledge Graph-Based Recommender Systems, with Focus on Explainable Embeddings*

Saved PDF:

```text
SLR/SLR1/kge-experiments/papers/doh_2022_deep_kg_recommender_systems_slr_embeddings.pdf
```

Why it is useful:

- It is a complete systematic review centered on knowledge graphs and embeddings.
- It provides taxonomies and tables that show how KG-embedding methods are presented in a polished SLR.

Caveat:

- It reviews KG-embedding systems; it does not use KG embeddings to build a graph of the SLR evidence base.

## Bottom line

I did not find a perfect open-access paper that is simultaneously:

1. a completed SLR,
2. represents the SLR output as a knowledge graph,
3. uses text embeddings/KG embeddings for semantic analysis, and
4. provides a polished final artifact.

The closest practical model is therefore to combine:

- Xie et al. (KG + RAG/embedding design for literature review), and
- Mallavarapu et al. (finished interactive evidence-map artifact for a systematic/scoping review).

For SLR1, this suggests a final product with both:

- a KG-backed evidence layer: studies, claims, evidence, EPS elements, tools, limitations, gaps;
- an embedding-backed exploration layer: semantic clusters, similarity edges, and interactive filtering.
