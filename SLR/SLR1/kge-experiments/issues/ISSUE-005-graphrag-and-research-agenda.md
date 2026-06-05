# ISSUE-005 — GraphRAG demo and research-agenda prioritization E12-E13

## Objective

Implement the final experiment backlog items from `IMPLEMENTATION_PLAN.md`:

- E12 — GraphRAG over SLR evidence
- E13 — Research agenda prioritization

Also add simple run documentation/driver support so the full pipeline is reproducible.

This issue depends on outputs from ISSUE-001 through ISSUE-004.

## Repository context

- Working directory: repository root `nanosatellite-mbse`.
- Experiment folder: `SLR/SLR1/kge-experiments/`.
- Read before coding:
  - `SLR/SLR1/kge-experiments/IMPLEMENTATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/schema/kg_schema.md`
  - `SLR/SLR1/kge-experiments/ORCHESTRATION_PLAN.md`
  - Earlier issue files, especially ISSUE-003 and ISSUE-004.
- Source extraction must remain read-only.
- Environment: Python 3, `numpy`, `networkx` are available. Do not require API access or external model downloads.

## Required implementation

Create these scripts:

1. `SLR/SLR1/kge-experiments/scripts/08_graphrag_demo.py`
2. `SLR/SLR1/kge-experiments/scripts/09_research_agenda.py`
3. `SLR/SLR1/kge-experiments/scripts/run_pipeline.py` (driver to run scripts 01-09 in order)

Update `SLR/SLR1/kge-experiments/README.md` with:

- what the pipeline generates;
- how to rerun it from repo root;
- dependency note: default embeddings use deterministic `hashing_tfidf_v1` fallback because heavyweight embedding/plotting dependencies are not assumed;
- provenance/quality-control note that semantic outputs are exploratory.

### `08_graphrag_demo.py`

Implement a local GraphRAG-style demo using existing vector/card artifacts and KG CSV/GraphML.

Questions to answer (from the implementation plan):

1. “Which papers provide the strongest evidence for EPS pre-physical verification?”
2. “What toolchains support simulation-in-the-loop verification?”
3. “Which claims about effort reduction have baseline comparators?”
4. “Where are reusable reference models available?”

Retrieval recipe:

1. Embed the question using the same `hashing_tfidf_v1` vectorizer metadata from ISSUE-003.
2. Retrieve top cards from relevant unit types (claims, studies, evidence quotes, limitations/gap cards as appropriate).
3. Expand in KG by 1–2 hops: study → claims → evidence type/confidence → limitations/gaps/toolchain/EPS/reuse as relevant.
4. Produce answers with citations to `corpus_id`, field paths, claim IDs where applicable, and evidence quotes/snippets.
5. Preserve retrieval traces for every answer.

Required outputs:

- `outputs/reports/graphrag_demo_questions.md`
- `outputs/reports/graphrag_limitations.md`
- `outputs/tables/graphrag_answer_sources.csv`
- `outputs/reports/retrieval_traces.jsonl` (or `outputs/graph_exports/retrieval_traces.jsonl` if documented; prefer reports path for validation)

### `09_research_agenda.py`

Implement E13 research agenda prioritization.

Use available data from `gap_mappings.jsonl`, `claims.jsonl`, `limitations.jsonl`, `study_codes.jsonl`, and controlled analysis outputs. Implement a transparent scoring formula inspired by the plan:

```text
gap_priority = frequency
             + weak_evidence_weight
             + eps_specificity_weight
             + lifecycle_undercoverage_weight
             + model_unavailability_weight
             + no_independent_validation_weight
```

Guidance:

- Keep the formula simple and documented in output metadata/report.
- Use weak/unsupported evidence counts where possible.
- Use EPS relevance / EPS-specific fields to weight gaps connected to EPS-specific evidence needs.
- Use limitation flags such as `model_not_available`, `no_independent_validation`, and `no_physical_test_or_flight_evidence`.
- Use lifecycle coverage outputs from E6 if available, or compute from flattened data.
- Do not overclaim statistical significance; this is exploratory prioritization over a 40-study corpus.

Required outputs:

- `outputs/tables/research_gap_priorities.csv`
- `outputs/reports/future_research_agenda.md`
- `outputs/reports/e13_research_agenda_prioritization.md`

### `run_pipeline.py`

- Run scripts `01_flatten_extraction.py` through `09_research_agenda.py` in order.
- Use subprocess with clear status messages.
- Exit nonzero on failure.
- Should be runnable from repository root:

```bash
python3 SLR/SLR1/kge-experiments/scripts/run_pipeline.py
```

## Validation commands

Run from repository root:

```bash
python3 SLR/SLR1/kge-experiments/scripts/run_pipeline.py
python3 - <<'PY'
from pathlib import Path
base = Path('SLR/SLR1/kge-experiments')
required = [
    'outputs/reports/graphrag_demo_questions.md', 'outputs/reports/graphrag_limitations.md',
    'outputs/tables/graphrag_answer_sources.csv', 'outputs/reports/retrieval_traces.jsonl',
    'outputs/tables/research_gap_priorities.csv', 'outputs/reports/future_research_agenda.md',
    'outputs/reports/e13_research_agenda_prioritization.md', 'README.md'
]
for rel in required:
    p = base / rel
    assert p.exists() and p.stat().st_size > 0, rel
print('ISSUE-005 outputs present')
PY
```

## Deliverables

- GraphRAG demo, research agenda, and full-pipeline driver scripts.
- Generated E12-E13 outputs.
- Updated README with rerun instructions and limitations.
- Local git commit with message similar to: `Add GraphRAG demo and research agenda pipeline`.
- Final subagent response should include files changed, validation results, answer/source counts, top research gaps, and caveats.

## Constraints

- Do not push.
- Do not modify source extraction data.
- Do not remove issue files; orchestration cleanup will happen after validation.
