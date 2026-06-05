# ISSUE-003 — Text cards, deterministic embeddings, and nearest-neighbor audit tables

## Objective

Implement the text-card and embedding stages from `IMPLEMENTATION_PLAN.md`: create stable provenance-rich embedding units and a local deterministic vector/nearest-neighbor pipeline.

This issue depends on ISSUE-001 outputs (`data/*.jsonl`). Do not implement semantic clustering/hybrid graph/GraphRAG; those are later issues.

## Repository context

- Working directory: repository root `nanosatellite-mbse`.
- Experiment folder: `SLR/SLR1/kge-experiments/`.
- Read before coding:
  - `SLR/SLR1/kge-experiments/IMPLEMENTATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/ORCHESTRATION_PLAN.md`
  - `SLR/SLR1/kge-experiments/issues/ISSUE-001-normalize-and-audit.md`
- Source dataset must remain read-only.
- Environment: Python 3 and `numpy` are available. Do not require pandas/scikit-learn/matplotlib/sentence-transformers/faiss. If a stronger embedding model is already installed locally you may support it as an optional guarded path, but the default must be offline and deterministic.

## Inputs

Expected from ISSUE-001:

- `data/studies.jsonl`
- `data/study_codes.jsonl`
- `data/claims.jsonl`
- `data/limitations.jsonl`
- `data/emergent_codes.jsonl`
- `data/evidence_quotes.jsonl`
- `data/gap_mappings.jsonl`

## Required implementation

Create these scripts:

1. `SLR/SLR1/kge-experiments/scripts/04_build_embedding_cards.py`
2. `SLR/SLR1/kge-experiments/scripts/05_embed_and_neighbors.py`

### `04_build_embedding_cards.py`

Generate text-card JSONL files under `SLR/SLR1/kge-experiments/embeddings/`:

- `study_cards.jsonl`
- `claim_cards.jsonl`
- `evidence_quote_cards.jsonl`
- `emergent_code_cards.jsonl`
- `limitation_cards.jsonl`
- `gap_mapping_cards.jsonl`
- `card_index.jsonl` (combined index of all cards; each record must include `unit_type`)

Card requirements:

- Each card has deterministic `card_id`, `unit_type`, `study_id`, optional `claim_id`, `source_path`, `title`/`label`, `text`, and `metadata`.
- Preserve provenance and exact evidence quotes where available.
- `study_card` text should combine title + objective/context/toolchain/EPS summary/main findings where available.
- `claim_card` text should combine claim text, outcome category, mechanism, evidence type/source, confidence, metric/baseline/effect, and study id.
- `evidence_quote_card` text should include exact quote + study id + field path + coded value.
- `limitation_card` text should include flag/assessment/rationale/evidence quote.
- `emergent_code_card` text should include label/description/rationale/evidence.
- `gap_mapping_card` text should include gap, addressing level, rationale, and evidence quote.

### `05_embed_and_neighbors.py`

Implement a local deterministic embedding fallback named `hashing_tfidf_v1`:

- Tokenize text deterministically (lowercase, alphanumeric-ish tokens; include useful technical tokens like MBSE, EPS, IVV by lowercasing).
- Hash tokens into a fixed dimension (suggest 384 or 512) with a stable hash such as SHA-256, not Python's randomized `hash()`.
- Compute TF-IDF-like weighted hashed vectors over all cards; L2-normalize vectors.
- Save:
  - `embeddings/vectors_hashing_tfidf_v1.npy`
  - `embeddings/vectorizer_hashing_tfidf_v1.json` containing dimensions, idf/hash metadata, card count, tokenization notes, and model name
  - `embeddings/embedding_manifest.json`
  - `embeddings/nearest_neighbors.jsonl`
  - `outputs/tables/nearest_neighbors_audit.csv`
  - `outputs/reports/embedding_index_report.md`

Nearest-neighbor requirements:

- Do not mix unit types in neighbor comparisons unless explicitly recorded. Default nearest neighbors should be within the same `unit_type`.
- Include top-k neighbors (`k=5` by default), cosine similarity (dot product of normalized vectors), `card_id`, `neighbor_card_id`, `unit_type`, and concise text snippets.
- Include embedding model/version metadata in each neighbor record or in the manifest.
- Mark all embedding-derived outputs as exploratory.

## Implementation guidance

- Make scripts idempotent and runnable from repository root.
- If ISSUE-001 output is absent, call/run `01_flatten_extraction.py` or fail with a clear message.
- Use only stdlib + numpy for default operation.
- Keep card construction deterministic and stable across runs.
- It is acceptable to add reusable helper functions to `scripts/common.py` if ISSUE-001 created it; avoid breaking earlier scripts.

## Validation commands

Run from repository root:

```bash
python3 SLR/SLR1/kge-experiments/scripts/01_flatten_extraction.py
python3 SLR/SLR1/kge-experiments/scripts/04_build_embedding_cards.py
python3 SLR/SLR1/kge-experiments/scripts/05_embed_and_neighbors.py
python3 - <<'PY'
from pathlib import Path
import json
import numpy as np
base = Path('SLR/SLR1/kge-experiments')
required = [
    'embeddings/study_cards.jsonl', 'embeddings/claim_cards.jsonl',
    'embeddings/evidence_quote_cards.jsonl', 'embeddings/emergent_code_cards.jsonl',
    'embeddings/limitation_cards.jsonl', 'embeddings/gap_mapping_cards.jsonl',
    'embeddings/card_index.jsonl', 'embeddings/vectors_hashing_tfidf_v1.npy',
    'embeddings/vectorizer_hashing_tfidf_v1.json', 'embeddings/embedding_manifest.json',
    'embeddings/nearest_neighbors.jsonl', 'outputs/tables/nearest_neighbors_audit.csv',
    'outputs/reports/embedding_index_report.md'
]
for rel in required:
    p = base / rel
    assert p.exists() and p.stat().st_size > 0, rel
vectors = np.load(base / 'embeddings/vectors_hashing_tfidf_v1.npy')
card_count = sum(1 for _ in open(base / 'embeddings/card_index.jsonl', encoding='utf-8'))
assert vectors.shape[0] == card_count, (vectors.shape, card_count)
print('ISSUE-003 outputs present; vectors shape=', vectors.shape)
PY
```

## Deliverables

- Card-builder and embedding/nearest-neighbor scripts.
- Generated embedding cards, vectors, manifests, nearest-neighbor outputs, and report.
- Local git commit with message similar to: `Build SLR1 embedding cards and neighbor index`.
- Final subagent response should include files changed, vector shape, card counts by unit type, validation results, and caveats.

## Constraints

- Do not push.
- Do not modify source extraction data.
- Do not perform clustering/hybrid/GraphRAG work in this issue.
