# GraphRAG demo limitations and quality controls

This E12 demo is a local, deterministic GraphRAG-style retrieval exercise over the SLR1 extraction artifacts.

## What is controlled vs exploratory

- Controlled provenance comes from `data/*.jsonl` and `kg/nodes.csv` / `kg/edges.csv` generated from the source extraction.
- Retrieval uses `hashing_tfidf_v1`, a deterministic lexical TF-IDF hashing fallback, not a neural embedding model.
- Answer ranking uses transparent question-specific heuristics over retrieved cards and controlled fields.
- The generated answers are exploratory synthesis aids, not new coded SLR judgments.

## Counts

| question_id | answer_source_rows |
| --- | --- |
| q1_eps_pre_physical_verification | 10 |
| q2_simulation_in_the_loop_toolchains | 12 |
| q3_effort_reduction_baselines | 26 |
| q4_reusable_reference_models | 12 |


| unit_type | retrieved_top_card_mentions |
| --- | --- |
| evidence_quote_card | 32 |
| claim_card | 32 |
| limitation_card | 24 |
| study_card | 21 |
| gap_mapping_card | 11 |


## Caveats

- Lexical hashing retrieval can miss semantically relevant records if terminology differs from the question.
- KG expansion is one to two hops over the controlled-code property graph; it does not prove causal support among every connected node.
- Evidence quotes/snippets are extracted provenance snippets and may need verification against full papers.
- The corpus has 40 studies; no statistical significance is claimed.
- Availability of reusable artifacts is inferred from extraction fields such as `open package`, reproducibility reporting, and `model_not_available` flags; it is not a live artifact-access check.
