# ISSUE-001 — Normalize extraction and E0 data audit

## Objective

Implement the first pipeline step from `SLR/SLR1/kge-experiments/IMPLEMENTATION_PLAN.md`: flatten `SLR/SLR1/extraction.json` into provenance-rich JSONL tables and run the E0 data audit/baseline descriptive statistics.

## Repository context

- Working directory: repository root `nanosatellite-mbse`.
- Source dataset: `SLR/SLR1/extraction.json`.
- Experiment folder: `SLR/SLR1/kge-experiments/`.
- Existing reference files to read:
  - `SLR/SLR1/kge-experiments/IMPLEMENTATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/schema/kg_schema.md`
  - `SLR/SLR1/kge-experiments/ORCHESTRATION_PLAN.md`
- Do **not** modify `SLR/SLR1/extraction.json` or any extraction judgments.
- The environment has Python 3, `numpy`, and `networkx`; do not require pandas/scikit-learn/matplotlib/sentence-transformers/faiss/duckdb.

## Source shape to expect

`SLR/SLR1/extraction.json` is a JSON object with keys including:

- `generated_at`, `study_count`, `controlled_field_count`, `statistics`, `studies`.
- `studies` contains 40 study objects.
- Each study contains: `corpus_id`, `tier`, `year`, `quality_checklist`, `structured_code_summary`, `structured_limitations`, `emergent_codes`, `extraction`, `bibtex`, and possibly `v1_1_subagent_review`.
- Important nested extraction sections:
  - `bibliographic_review_management`
  - `study_context_population`
  - `mbse_objective_scope_artifacts`
  - `implementation_pathway_tailoring`
  - `toolchain_interoperability_lifecycle_continuity`
  - `eps_verification_specific`
  - `claimed_outcomes_value_mechanisms_evidence` (list)
  - `governance_roi_project_decision_linkage`
  - `gap_mapping`
  - `synthesis_consistency`

## Required implementation

Create `SLR/SLR1/kge-experiments/scripts/01_flatten_extraction.py`.

The script should:

1. Read `../extraction.json` relative to the kge-experiments folder, or accept an optional `--source` path.
2. Create output directories if missing:
   - `data/`
   - `outputs/tables/`
   - `outputs/reports/`
3. Generate these JSONL files under `SLR/SLR1/kge-experiments/data/`:
   - `studies.jsonl`
   - `study_codes.jsonl`
   - `claims.jsonl`
   - `limitations.jsonl`
   - `emergent_codes.jsonl`
   - `evidence_quotes.jsonl`
   - `gap_mappings.jsonl`
4. Preserve provenance in each generated record. Include where relevant:
   - `study_id` (from `corpus_id`)
   - stable generated IDs (`claim_id`, `evidence_quote_id`, `emergent_code_id`, etc.)
   - `source_path` / `field_path` using JSON-path-like dot notation
   - `value`, `status`, `rationale`, `evidence_quote`, `confidence` where present
   - source `generated_at` / extraction version metadata if useful
5. Flatten study-level controlled codes from both `structured_code_summary` and nested `extraction.*` sections. Handle scalar, list, dict-with-value/rationale/evidence, and missing values robustly.
6. Flatten `claimed_outcomes_value_mechanisms_evidence[]` into `claims.jsonl` with the fields named in the implementation plan:
   - `claim_text`, `outcome_category`, `specificity`, `mbse_mechanism`, `lifecycle_stage`, `evidence_type`, `metric`, `baseline`, `observed_effect`, `evidence_confidence`, `reliability_subtype`, plus provenance fields.
7. Flatten limitations from `structured_limitations` into `limitations.jsonl`.
8. Flatten emergent codes from `emergent_codes[]` into `emergent_codes.jsonl`.
9. Flatten gap mappings from `extraction.gap_mapping` into `gap_mappings.jsonl`.
10. Collect exact evidence quotes wherever available into `evidence_quotes.jsonl`, with backlink fields (`study_id`, optional `claim_id`, `field_path`, `coded_value`).
11. Generate E0 outputs:
    - `outputs/tables/field_value_counts.csv`
    - `outputs/tables/study_quality_summary.csv`
    - `outputs/reports/e0_data_audit.md`
12. In the E0 report, answer:
    - Did flattening preserve all 40 studies?
    - Do generated counts match or explain differences against the `statistics` object in source JSON?
    - Which fields appear multi-valued and need many-to-many graph edges?
    - Any missing/unexpected sections encountered?

## Implementation guidance

- Use only Python standard library modules (`json`, `csv`, `pathlib`, `argparse`, `collections`, `statistics`, etc.).
- Make the script idempotent: rerunning should overwrite generated files cleanly.
- Keep helper functions reusable for later scripts if appropriate. You may add `scripts/common.py` for JSONL/CSV/slug/path helpers if useful.
- Stable IDs should be deterministic, e.g. `paper-0001::claim-01`.
- Do not overfit to one study; inspect several studies while coding.

## Validation commands

Run from repository root:

```bash
python3 SLR/SLR1/kge-experiments/scripts/01_flatten_extraction.py
python3 - <<'PY'
from pathlib import Path
base = Path('SLR/SLR1/kge-experiments')
for rel in [
    'data/studies.jsonl', 'data/study_codes.jsonl', 'data/claims.jsonl',
    'data/limitations.jsonl', 'data/emergent_codes.jsonl', 'data/evidence_quotes.jsonl',
    'data/gap_mappings.jsonl', 'outputs/tables/field_value_counts.csv',
    'outputs/tables/study_quality_summary.csv', 'outputs/reports/e0_data_audit.md'
]:
    p = base / rel
    assert p.exists() and p.stat().st_size > 0, rel
print('ISSUE-001 outputs present')
PY
```

Also verify the study count in `data/studies.jsonl` is 40.

## Deliverables

- New/updated scripts for flattening and helpers.
- Generated `data/*.jsonl` and E0 audit outputs.
- Local git commit with message similar to: `Implement SLR1 flattening and data audit`.
- Final subagent response should include files changed, validation results, and any caveats.

## Constraints

- Do not push.
- Do not modify source extraction data.
- Do not start later experiment work in this issue.
