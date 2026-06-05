# Embedding index report — SLR1 text cards

**Exploratory notice:** all embedding-derived nearest-neighbor outputs are audit aids only. They are not semantic clusters, graph edges, or validated evidence claims.

## Embedding model

- Model/version: `hashing_tfidf_v1`
- Dimensions: `384`
- Card count: `17394`
- Vector shape: `(17394, 384)`
- Default neighbor scope: within the same `unit_type` only; mixed-unit comparisons were not generated.
- Top-k per card: `5`
- Tokenization regex: `[a-z0-9]+(?:[._+#/\-][a-z0-9]+)*` with lowercase normalization and IV&V → `ivv` normalization.
- Vocabulary size: `9569`

## Card counts by unit type

| unit_type | card_count |
| --- | --- |
| claim_card | 270 |
| emergent_code_card | 345 |
| evidence_quote_card | 15937 |
| gap_mapping_card | 200 |
| limitation_card | 602 |
| study_card | 40 |


## Nearest-neighbor record counts

| unit_type | neighbor_record_count |
| --- | --- |
| claim_card | 1350 |
| emergent_code_card | 1725 |
| evidence_quote_card | 79685 |
| gap_mapping_card | 1000 |
| limitation_card | 3010 |
| study_card | 200 |


## Highest-similarity audit examples

| unit_type | rank | card_id | neighbor_card_id | cosine_similarity |
| --- | --- | --- | --- | --- |
| evidence_quote_card | 1 | evidence_quote_card::paper-0016::quote-0389 | evidence_quote_card::paper-0016::quote-0390 | 0.9825 |
| evidence_quote_card | 1 | evidence_quote_card::paper-0016::quote-0390 | evidence_quote_card::paper-0016::quote-0389 | 0.9825 |
| evidence_quote_card | 1 | evidence_quote_card::paper-0079::quote-0081 | evidence_quote_card::paper-0079::quote-0116 | 0.977959 |
| evidence_quote_card | 1 | evidence_quote_card::paper-0079::quote-0116 | evidence_quote_card::paper-0079::quote-0081 | 0.977959 |
| evidence_quote_card | 1 | evidence_quote_card::paper-0013::quote-0395 | evidence_quote_card::paper-0013::quote-0396 | 0.977817 |
| evidence_quote_card | 1 | evidence_quote_card::paper-0013::quote-0396 | evidence_quote_card::paper-0013::quote-0395 | 0.977817 |
| evidence_quote_card | 1 | evidence_quote_card::paper-0079::quote-0072 | evidence_quote_card::paper-0079::quote-0496 | 0.974514 |
| evidence_quote_card | 1 | evidence_quote_card::paper-0079::quote-0496 | evidence_quote_card::paper-0079::quote-0072 | 0.974514 |
| evidence_quote_card | 1 | evidence_quote_card::paper-0079::quote-0216 | evidence_quote_card::paper-0079::quote-0634 | 0.971439 |
| evidence_quote_card | 1 | evidence_quote_card::paper-0079::quote-0634 | evidence_quote_card::paper-0079::quote-0216 | 0.971439 |


## Outputs

- `embeddings/vectors_hashing_tfidf_v1.npy`
- `embeddings/vectorizer_hashing_tfidf_v1.json`
- `embeddings/embedding_manifest.json`
- `embeddings/nearest_neighbors.jsonl`
- `outputs/tables/nearest_neighbors_audit.csv`
- `outputs/reports/embedding_index_report.md`

## Caveats

- The fallback is deterministic and offline, but it is lexical TF-IDF hashing, not a neural semantic embedding model.
- Hash collisions can occur; signed hashing reduces but does not eliminate collision effects.
- Neighbor tables are intended for human audit and later issue inputs; no clustering, hybrid similarity graph, or GraphRAG work is performed in this issue.
