# KG + Embedding Experiments for SLR1

This folder contains a plan and reference pack for experimenting with knowledge-graph (KG) and embedding analyses over `SLR/SLR1/extraction.json`.

## Current assets

- `../extraction.json` — source structured extraction file; 40 studies, 47 controlled fields, claim-level evidence and limitations.
- `IMPLEMENTATION_PLAN.md` — full implementation plan and experiment backlog.
- `schema/kg_schema.md` — proposed property-graph schema and mapping from extraction fields.
- `experiments/experiment_manifest.json` — machine-readable experiment inventory.
- `references/references_used.json` — persisted metadata for papers used to shape the plan.
- `references/references_used.bib` — BibTeX for the same references.
- `references/reference-notes.md` — why each reference was included.
- `papers/` — locally downloaded open-access PDFs where available.
- `searches/` — raw search JSON and merged candidate corpus for KG+embedding references.

## Intended implementation style

The experiments should be implemented incrementally:

1. Normalize `extraction.json` into flat tables / JSONL.
2. Build a first property graph from controlled codes and claim-level evidence.
3. Add text embeddings for study cards, claims, evidence quotes, limitations, and emergent codes.
4. Add similarity edges and run community / centrality / gap-prioritization analyses.
5. Use the KG plus embeddings for exploratory GraphRAG-style querying over the SLR evidence base.

The goal is exploratory synthesis, not re-running the SLR search or changing the extraction protocol.
