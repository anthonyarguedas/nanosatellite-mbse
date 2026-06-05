# ISSUE-006 — Final validation and cleanup readiness

## Objective

Perform final validation of the implemented KG + embedding experiment pipeline. Fix small issues needed to make the full pipeline reproducible and confirm readiness for orchestration cleanup of temporary issue files.

This issue depends on ISSUE-001 through ISSUE-005 being implemented.

## Repository context

- Working directory: repository root `nanosatellite-mbse`.
- Experiment folder: `SLR/SLR1/kge-experiments/`.
- Source extraction: `SLR/SLR1/extraction.json` must remain unchanged.
- Read before validating:
  - `SLR/SLR1/kge-experiments/ORCHESTRATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/IMPLEMENTATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/README.md`
  - All previous issue files under `SLR/SLR1/kge-experiments/issues/`

## Required validation and fixes

1. Run the full pipeline from repository root:

   ```bash
   python3 SLR/SLR1/kge-experiments/scripts/run_pipeline.py
   ```

2. Verify core artifact groups exist and are non-empty:

   - `data/studies.jsonl`
   - `data/claims.jsonl`
   - `data/study_codes.jsonl`
   - `data/limitations.jsonl`
   - `data/emergent_codes.jsonl`
   - `data/evidence_quotes.jsonl`
   - `data/gap_mappings.jsonl`
   - `kg/nodes.csv`
   - `kg/edges.csv`
   - `kg/graph.graphml`
   - `embeddings/card_index.jsonl`
   - `embeddings/vectors_hashing_tfidf_v1.npy`
   - `embeddings/nearest_neighbors.jsonl`
   - E0-E13 reports/tables listed in earlier issue files.

3. Verify study count:

   - `data/studies.jsonl` contains 40 records.

4. Verify source extraction is not modified:

   - `git diff -- SLR/SLR1/extraction.json` should be empty.

5. Verify README/rerun instructions:

   - `README.md` in `kge-experiments/` names the pipeline command.
   - README documents deterministic `hashing_tfidf_v1` fallback and exploratory status of semantic outputs.

6. Verify idempotence:

   - Rerunning `run_pipeline.py` should complete without duplicate/append artifacts or inconsistent counts.

7. If validation fails, make minimal fixes only. Do not redesign the pipeline unless necessary.

8. Produce a final validation report:

   - `SLR/SLR1/kge-experiments/outputs/reports/final_validation.md`

The final validation report should include:

- commands run;
- artifact presence summary;
- key counts (studies, claims, cards, KG nodes/edges, similarity edges if available);
- confirmation that `SLR/SLR1/extraction.json` was not modified;
- known caveats/limitations.

## Validation command snippet

You may use this as a starting point:

```bash
python3 SLR/SLR1/kge-experiments/scripts/run_pipeline.py
python3 - <<'PY'
from pathlib import Path
base = Path('SLR/SLR1/kge-experiments')
required = [
    'data/studies.jsonl', 'data/claims.jsonl', 'data/study_codes.jsonl',
    'data/limitations.jsonl', 'data/emergent_codes.jsonl', 'data/evidence_quotes.jsonl',
    'data/gap_mappings.jsonl', 'kg/nodes.csv', 'kg/edges.csv', 'kg/graph.graphml',
    'embeddings/card_index.jsonl', 'embeddings/vectors_hashing_tfidf_v1.npy',
    'embeddings/nearest_neighbors.jsonl', 'outputs/reports/e0_data_audit.md',
    'outputs/reports/e1_claim_evidence.md', 'outputs/reports/e7_study_semantic_clustering.md',
    'outputs/reports/graphrag_demo_questions.md', 'outputs/reports/future_research_agenda.md'
]
missing = []
for rel in required:
    p = base / rel
    if not p.exists() or p.stat().st_size == 0:
        missing.append(rel)
if missing:
    raise SystemExit('missing/empty: ' + ', '.join(missing))
study_count = sum(1 for _ in open(base / 'data/studies.jsonl', encoding='utf-8'))
assert study_count == 40, study_count
print('core validation OK')
PY
git diff -- SLR/SLR1/extraction.json
```

## Deliverables

- Any minimal fixes required for full pipeline validation.
- `outputs/reports/final_validation.md`.
- Local git commit with message similar to: `Validate SLR1 KG embedding pipeline`.
- Final subagent response should include validation status, files changed, commands run, key counts, and any caveats.

## Constraints

- Do not push.
- Do not remove issue files; the orchestrator will clean them up after this issue passes.
- Do not alter source extraction data or SLR protocol files.
