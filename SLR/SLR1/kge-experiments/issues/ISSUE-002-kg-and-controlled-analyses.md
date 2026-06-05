# ISSUE-002 — Build KG and controlled-code analyses E1-E6

## Objective

Implement the property-graph MVP and controlled-code graph analyses from `IMPLEMENTATION_PLAN.md`, covering experiments E1 through E6.

This issue depends on ISSUE-001 outputs (`data/*.jsonl`). Do not redo extraction flattening except by invoking `scripts/01_flatten_extraction.py` if outputs are missing.

## Repository context

- Working directory: repository root `nanosatellite-mbse`.
- Experiment folder: `SLR/SLR1/kge-experiments/`.
- Read before coding:
  - `SLR/SLR1/kge-experiments/IMPLEMENTATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/schema/kg_schema.md`
  - `SLR/SLR1/kge-experiments/ORCHESTRATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/issues/ISSUE-001-normalize-and-audit.md`
- Source dataset must remain read-only.
- Environment: Python 3, `numpy`, `networkx` are available. Do not require pandas/scikit-learn/matplotlib/duckdb.

## Inputs

Expected from ISSUE-001:

- `SLR/SLR1/kge-experiments/data/studies.jsonl`
- `SLR/SLR1/kge-experiments/data/study_codes.jsonl`
- `SLR/SLR1/kge-experiments/data/claims.jsonl`
- `SLR/SLR1/kge-experiments/data/limitations.jsonl`
- `SLR/SLR1/kge-experiments/data/emergent_codes.jsonl`
- `SLR/SLR1/kge-experiments/data/evidence_quotes.jsonl`
- `SLR/SLR1/kge-experiments/data/gap_mappings.jsonl`

## Required implementation

Create these scripts, using shared helpers if useful:

1. `SLR/SLR1/kge-experiments/scripts/02_build_kg.py`
2. `SLR/SLR1/kge-experiments/scripts/03_controlled_graph_analyses.py`

### `02_build_kg.py`

Build a portable property graph under `SLR/SLR1/kge-experiments/kg/`:

- `nodes.csv`
- `edges.csv`
- `graph.graphml`
- `neo4j_import.cypher`
- `duckdb_graph_tables.sql`

Minimum node labels from the implementation plan/schema:

- `Study`
- `Claim`
- `OutcomeCategory`
- `EvidenceType`
- `EvidenceConfidence`
- `ReliabilitySubtype`
- `SpecificityOfClaim`
- `MBSEMechanism`
- `MetricIndicator`
- `BaselineComparator`
- `LifecycleStage`
- `ApproachClass`
- `EPSRelevance`
- `EPSElement`
- `VerificationArtifact`
- `VerificationMechanism`
- `IVVIntegrationLevel`
- `Tool`
- `InteroperabilityMechanism`
- `ToolchainLimitation`
- `ReuseMechanism`
- `TailoringRationale`
- `DevelopmentContext`
- `ModelMaturity`
- `ModelArtifact`
- `ModelingScope`
- `LimitationFlag`
- `Gap`
- `GapAddressingLevel`
- `EmergentCode`

Minimum edge types from the implementation plan/schema:

- `HAS_CLAIM`
- `CLAIMS_OUTCOME`
- `USES_MBSE_MECHANISM`
- `HAS_EVIDENCE_TYPE`
- `HAS_EVIDENCE_CONFIDENCE`
- `HAS_RELIABILITY_SUBTYPE`
- `HAS_SPECIFICITY`
- `HAS_METRIC`
- `HAS_BASELINE`
- `CLAIM_AT_LIFECYCLE_STAGE`
- `USES_TOOL`
- `HAS_INTEROPERABILITY_MECHANISM`
- `HAS_TOOLCHAIN_LIMITATION`
- `MODELS_EPS_ELEMENT`
- `USES_VERIFICATION_ARTIFACT`
- `USES_VERIFICATION_MECHANISM`
- `HAS_IVV_LEVEL`
- `ADDRESSES_LIFECYCLE_STAGE`
- `HAS_REUSE_MECHANISM`
- `HAS_APPROACH_CLASS`
- `HAS_EPS_RELEVANCE`
- `HAS_LIMITATION`
- `ADDRESSES_GAP`
- `HAS_GAP_ADDRESSING_LEVEL` (if useful)
- `HAS_EMERGENT_CODE`

Graph requirements:

- Use deterministic normalized node IDs/slugs for controlled-code nodes.
- Include provenance properties on edges: `source_field_path`, `source_value`, `rationale`, `evidence_quote`, `confidence` where available.
- Include graph construction metadata in a small `kg/graph_manifest.json`.
- Make CSVs readable with explicit columns. Suggested node columns: `id,label,type,properties_json`. Suggested edge columns: `source,target,type,source_field_path,source_value,rationale,evidence_quote,confidence,properties_json`.
- GraphML may be generated with `networkx`; convert complex/list/dict properties to strings because GraphML requires scalar values.

### `03_controlled_graph_analyses.py`

Generate controlled-code experiment outputs for E1-E6 under:

- `outputs/tables/`
- `outputs/reports/`
- `outputs/graph_exports/`
- `outputs/figures/`

Required outputs:

E1 — Claim-evidence graph:

- `outputs/graph_exports/claim_evidence_graph.graphml`
- `outputs/tables/unsupported_claims.csv`
- `outputs/tables/claim_outcome_evidence_counts.csv`
- `outputs/reports/e1_claim_evidence.md`
- A simple alluvial/Sankey substitute is acceptable as CSV/text/SVG if plotting libraries are unavailable.

E2 — EPS verification pathway map:

- `outputs/tables/eps_verification_paths.csv`
- `outputs/reports/eps_gap_map.md`
- `outputs/graph_exports/eps_verification_paths.graphml`

E3 — Toolchain interoperability network:

- `outputs/graph_exports/tool_cooccurrence.graphml`
- `outputs/tables/toolchain_limitations_heatmap.csv`
- `outputs/tables/tool_interoperability_counts.csv`
- `outputs/reports/e3_toolchain_interoperability.md`

E4 — Reuse/generality evidence map:

- `outputs/tables/reuse_evidence_map.csv`
- `outputs/reports/reusable_artifact_candidates.md`

E5 — Limitation/gap co-occurrence graph:

- `outputs/graph_exports/limitation_gap_graph.graphml`
- `outputs/tables/bottlenecks_ranked.csv`
- `outputs/tables/gap_limitation_heatmap.csv`
- `outputs/reports/e5_limitation_gap_bottlenecks.md`

E6 — Lifecycle coverage graph:

- `outputs/tables/lifecycle_coverage.csv`
- `outputs/reports/lifecycle_artifact_evidence.md`
- `outputs/graph_exports/lifecycle_artifact_evidence.graphml`

## Implementation guidance

- Use only data from flattened JSONL and/or the source extraction; do not mutate source.
- Prefer straightforward counts, co-occurrences, and NetworkX centrality over heavy dependencies.
- For simple visual outputs, CSV/GraphML/Markdown is acceptable; if you generate SVG manually, keep it deterministic.
- If ISSUE-001 has not produced data yet, run the flatten script rather than duplicating logic.
- Make scripts idempotent and robust to empty/missing optional fields.

## Validation commands

Run from repository root:

```bash
python3 SLR/SLR1/kge-experiments/scripts/01_flatten_extraction.py
python3 SLR/SLR1/kge-experiments/scripts/02_build_kg.py
python3 SLR/SLR1/kge-experiments/scripts/03_controlled_graph_analyses.py
python3 - <<'PY'
from pathlib import Path
base = Path('SLR/SLR1/kge-experiments')
required = [
    'kg/nodes.csv', 'kg/edges.csv', 'kg/graph.graphml', 'kg/neo4j_import.cypher',
    'kg/duckdb_graph_tables.sql', 'kg/graph_manifest.json',
    'outputs/graph_exports/claim_evidence_graph.graphml', 'outputs/tables/unsupported_claims.csv',
    'outputs/tables/claim_outcome_evidence_counts.csv', 'outputs/reports/e1_claim_evidence.md',
    'outputs/tables/eps_verification_paths.csv', 'outputs/reports/eps_gap_map.md',
    'outputs/graph_exports/eps_verification_paths.graphml', 'outputs/graph_exports/tool_cooccurrence.graphml',
    'outputs/tables/toolchain_limitations_heatmap.csv', 'outputs/tables/tool_interoperability_counts.csv',
    'outputs/reports/e3_toolchain_interoperability.md', 'outputs/tables/reuse_evidence_map.csv',
    'outputs/reports/reusable_artifact_candidates.md', 'outputs/graph_exports/limitation_gap_graph.graphml',
    'outputs/tables/bottlenecks_ranked.csv', 'outputs/tables/gap_limitation_heatmap.csv',
    'outputs/reports/e5_limitation_gap_bottlenecks.md', 'outputs/tables/lifecycle_coverage.csv',
    'outputs/reports/lifecycle_artifact_evidence.md', 'outputs/graph_exports/lifecycle_artifact_evidence.graphml'
]
for rel in required:
    p = base / rel
    assert p.exists() and p.stat().st_size > 0, rel
print('ISSUE-002 outputs present')
PY
```

## Deliverables

- KG construction script and generated `kg/` artifacts.
- Controlled-code analysis script and E1-E6 outputs.
- Local git commit with message similar to: `Build SLR1 KG and controlled analyses`.
- Final subagent response should include files changed, validation results, notable counts, and caveats.

## Constraints

- Do not push.
- Do not modify source extraction data.
- Do not implement embedding/semantic/GraphRAG work in this issue.
