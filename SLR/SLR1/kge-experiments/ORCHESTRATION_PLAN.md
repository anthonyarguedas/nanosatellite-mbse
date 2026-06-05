# Orchestration Plan: Implement KG + Embedding Experiments

Date: 2026-06-05

## End goal

Implement the experiment backlog described in `SLR/SLR1/kge-experiments/IMPLEMENTATION_PLAN.md` over the source dataset `SLR/SLR1/extraction.json`, producing reproducible scripts and generated artifacts under `SLR/SLR1/kge-experiments/` without changing the underlying SLR extraction judgments.

## Constraints and quality controls

- Treat `SLR/SLR1/extraction.json` as read-only input.
- Preserve provenance in generated records and analyses: `study_id`, `claim_id` where applicable, `field_path`, coded value, rationale, evidence quote, source path, and model/index metadata for embedding-derived outputs.
- Label embedding-derived findings as exploratory/audit queues, not automatic corrections.
- Avoid internet/API dependencies. The local environment currently has Python 3, `numpy`, and `networkx`; common packages such as pandas, scikit-learn, matplotlib, sentence-transformers, faiss, duckdb, and hdbscan are not available. Scripts should use the Python standard library plus available libraries, with optional imports only when guarded.
- Generate portable artifacts: JSONL, CSV, GraphML, Cypher, SQL, Markdown, and simple SVG/text figures where image libraries are unavailable.
- Do not push. Commits may be made locally to document progress.
- Temporary issue files in `SLR/SLR1/kge-experiments/issues/` are orchestration artifacts and should be removed after implementation is complete.

## Work breakdown and dependencies

1. **ISSUE-001 — Normalize extraction and E0 audit**
   - Build `scripts/01_flatten_extraction.py`.
   - Generate `data/*.jsonl`, baseline audit tables, and `outputs/reports/e0_data_audit.md`.
   - This is the dependency for all later work.

2. **ISSUE-002 — Build KG and controlled-code analyses E1-E6**
   - Build property-graph artifacts under `kg/` from flattened data.
   - Generate controlled-code experiment outputs for E1 through E6.
   - Depends on ISSUE-001.

3. **ISSUE-003 — Build text cards, deterministic embeddings, and nearest-neighbor audit tables**
   - Build text cards for studies, claims, evidence quotes, limitations, emergent codes, and gap rationales.
   - Implement deterministic local vectorization and nearest-neighbor outputs; optionally use stronger models only if already installed.
   - Depends on ISSUE-001.

4. **ISSUE-004 — Semantic clustering, consistency audit, and hybrid similarity graph E7-E11**
   - Use embedding/card artifacts plus KG to produce study/claim/emergent clusters, audit queues, and hybrid graph outputs.
   - Depends on ISSUE-002 and ISSUE-003.

5. **ISSUE-005 — GraphRAG demo and research-agenda prioritization E12-E13**
   - Implement evidence-grounded GraphRAG demo questions and ranked research gaps.
   - Update documentation/run instructions.
   - Depends on ISSUE-002, ISSUE-003, and ISSUE-004.

6. **ISSUE-006 — Final validation and cleanup readiness**
   - Run the full pipeline from a clean generated-artifact state.
   - Verify expected outputs exist, scripts are idempotent, source extraction is unchanged, and generated reports describe limitations/fallback embedding model.
   - Depends on all implementation issues.

## Delegation protocol

Each issue is written as a self-contained Markdown file under `SLR/SLR1/kge-experiments/issues/`. A Pi subagent will be launched for each issue with explicit instructions to:

- read the issue file and relevant plan/schema files;
- make only the changes needed for that issue;
- run and report validation commands;
- commit locally with an issue-specific message if changes are successful;
- never push;
- return a concise summary including files changed, outputs generated, validation results, and any blockers.

## Acceptance criteria

- `SLR/SLR1/kge-experiments/scripts/` contains a reproducible pipeline for flattening, KG construction, embeddings, experiments, GraphRAG, and research agenda generation.
- Planned artifact directories exist and contain the expected generated outputs:
  - `data/`
  - `kg/`
  - `embeddings/`
  - `outputs/tables/`
  - `outputs/figures/`
  - `outputs/graph_exports/`
  - `outputs/reports/`
- E0 through E13 each have at least one corresponding generated table/report/graph artifact.
- `README.md` documents how to rerun the pipeline and notes the deterministic local embedding fallback.
- Validation shows source study count is 40 and `SLR/SLR1/extraction.json` was not modified.
- Temporary issue files are removed in a final cleanup commit.
