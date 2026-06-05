# Implementation Plan: KG + Embedding Experiments over `SLR/SLR1/extraction.json`

## 1. Purpose

Use the structured SLR1 extraction as a small but rich evidence base for experimenting with:

- knowledge graphs for explicit evidence structure, provenance, and queryability;
- text embeddings for semantic similarity, clustering, inconsistency detection, and retrieval;
- hybrid KG + embedding analyses for evidence maps, gap identification, and GraphRAG-style exploration.

The dataset currently has 40 studies, 47 controlled fields, claim-level evidence entries, limitation assessments, emergent codes, and gap mappings. This is enough to test a useful graph/embedding workflow without needing a large corpus.

## 2. Non-goals

- Do not modify the underlying SLR protocol or extracted judgments during experiments.
- Do not treat embeddings as a replacement for controlled coding.
- Do not use generated clusters as evidence unless they can be traced back to specific extraction fields and evidence quotes.
- Do not overclaim statistical significance; this is an exploratory synthesis layer over a 40-study corpus.

## 3. Source data

Input:

```text
SLR/SLR1/extraction.json
```

Important source sections:

- `studies[].corpus_id`
- `studies[].year`
- `studies[].tier`
- `studies[].structured_code_summary`
- `studies[].structured_limitations`
- `studies[].emergent_codes`
- `studies[].extraction.*`
- `studies[].extraction.claimed_outcomes_value_mechanisms_evidence[]`
- `studies[].bibtex`

Important repeated controlled dimensions:

- RQ relevance: `rq1_relevance`, `rq2_relevance`, `rq3_relevance`
- approach class: `Pure MBSE`, `Enhanced MBSE`, `Extended MBSE`, `Integrated MBSE/digital engineering`
- EPS relevance and EPS elements modeled
- tool/language/toolchain fields
- interoperability mechanisms
- verification/validation artifacts
- pre-physical verification mechanisms
- IV&V integration level
- outcome categories
- evidence type
- evidence confidence rating
- limitation flags
- gap mapping values
- generality/reuse mechanisms

## 4. Planned implementation artifacts

Create these generated artifacts once implementation begins:

```text
data/
  studies.jsonl
  claims.jsonl
  study_codes.jsonl
  limitations.jsonl
  emergent_codes.jsonl
  evidence_quotes.jsonl

kg/
  nodes.csv
  edges.csv
  graph.graphml
  neo4j_import.cypher
  duckdb_graph_tables.sql

embeddings/
  study_cards.jsonl
  claim_cards.jsonl
  evidence_quote_cards.jsonl
  emergent_code_cards.jsonl
  limitation_cards.jsonl
  vectors_<model>.npy
  vector_index.faiss        # optional
  nearest_neighbors.jsonl

outputs/
  tables/
  figures/
  graph_exports/
  reports/
```

## 5. Normalization pipeline

### Step 5.1: Flatten source JSON

Write a script such as:

```text
scripts/01_flatten_extraction.py
```

Recommended tables:

1. `studies`
   - `study_id`, `year`, `tier`, `title`, `authors`, `venue`, `doi`, `quality_score_total`, `extraction_confidence`
2. `study_codes`
   - `study_id`, `field_path`, `value`, `status`, `rationale`, `evidence_quote`, `confidence`
3. `claims`
   - `claim_id`, `study_id`, `claim_text`, `outcome_category`, `specificity`, `mbse_mechanism`, `lifecycle_stage`, `evidence_type`, `metric`, `baseline`, `observed_effect`, `evidence_confidence`, `reliability_subtype`
4. `limitations`
   - `study_id`, `flag`, `source`, `assessment`, `rationale`, `evidence_quote`
5. `emergent_codes`
   - `study_id`, `field_path`, `label`, `description`, `rationale`, `evidence_quote`
6. `gap_mappings`
   - `study_id`, `gap`, `level`, `rationale`, `evidence_quote`

### Step 5.2: Build text cards for embeddings

Create stable, provenance-rich text units:

- `study_card`: title + abstract if available + objective + context + toolchain + EPS summary + main findings.
- `claim_card`: claim text + outcome category + mechanism + evidence type + evidence source + confidence.
- `evidence_quote_card`: exact quote + study id + field path + coded value.
- `limitation_card`: limitation flag + assessment + rationale + evidence quote.
- `emergent_code_card`: label + description + rationale + evidence.

Each card should keep `source_path` back to the JSON field.

## 6. KG build plan

Use either NetworkX for local experimentation or Neo4j for graph querying. The first implementation should be simple property-graph CSVs, because they are portable.

### Minimum viable graph

Nodes:

- `Study`
- `Claim`
- `OutcomeCategory`
- `EvidenceType`
- `EvidenceConfidence`
- `MBSEMechanism`
- `Tool`
- `InteroperabilityMechanism`
- `EPSElement`
- `VerificationMechanism`
- `IVVIntegrationLevel`
- `LifecycleStage`
- `ReuseMechanism`
- `ApproachClass`
- `LimitationFlag`
- `Gap`
- `EmergentCode`

Edges:

- `Study HAS_CLAIM Claim`
- `Claim CLAIMS_OUTCOME OutcomeCategory`
- `Claim USES_MBSE_MECHANISM MBSEMechanism`
- `Claim HAS_EVIDENCE_TYPE EvidenceType`
- `Claim HAS_EVIDENCE_CONFIDENCE EvidenceConfidence`
- `Study USES_TOOL Tool`
- `Study HAS_INTEROPERABILITY_MECHANISM InteroperabilityMechanism`
- `Study MODELS_EPS_ELEMENT EPSElement`
- `Study USES_VERIFICATION_MECHANISM VerificationMechanism`
- `Study HAS_IVV_LEVEL IVVIntegrationLevel`
- `Study ADDRESSES_LIFECYCLE_STAGE LifecycleStage`
- `Study HAS_REUSE_MECHANISM ReuseMechanism`
- `Study HAS_APPROACH_CLASS ApproachClass`
- `Study HAS_LIMITATION LimitationFlag`
- `Study ADDRESSES_GAP Gap`
- `Study HAS_EMERGENT_CODE EmergentCode`

## 7. Embedding plan

### Candidate models

Start with a local, reproducible model:

- `sentence-transformers/all-MiniLM-L6-v2` for fast testing.
- `BAAI/bge-small-en-v1.5` or `BAAI/bge-base-en-v1.5` for stronger retrieval.

Optional API model:

- `text-embedding-3-small` or equivalent if API access is available.

### Embedding units

Embed separately:

1. studies
2. claims
3. evidence quotes
4. limitations
5. emergent codes
6. gap mapping rationales

Do not mix units in one vector index without a `unit_type` property; otherwise semantic neighbors become hard to interpret.

### Similarity thresholds

Use empirical thresholding:

- top-k nearest neighbors for exploration, e.g. `k=5`;
- cosine similarity threshold for graph edges, initially `>= 0.78` for claims and `>= 0.72` for study cards, then tune by manual inspection.

Add similarity edges only after saving nearest-neighbor audit tables.

## 8. Experiment backlog

### E0 — Data audit and baseline descriptive stats

Goal: verify that flattened outputs match existing aggregate statistics.

Outputs:

- `outputs/tables/field_value_counts.csv`
- `outputs/tables/study_quality_summary.csv`
- `outputs/reports/e0_data_audit.md`

Questions:

- Did flattening preserve all 40 studies?
- Are code counts identical to `statistics` in the source JSON?
- Which fields are multi-valued and need many-to-many edges?

### E1 — Claim-evidence graph

Goal: map every value claim to outcome category, mechanism, evidence type, and confidence.

Queries:

- Which outcome categories are mostly unsupported or weak?
- Which MBSE mechanisms are associated with moderate/strong evidence?
- Which studies make many claims but provide weak evidence?

Outputs:

- claim-evidence Sankey or alluvial diagram
- claim subgraph exports
- ranked list of unsupported high-frequency claims

### E2 — EPS verification pathway map

Goal: connect EPS modeled elements to verification mechanisms and IV&V integration levels.

Queries:

- Which EPS elements are commonly modeled but rarely verified?
- Which studies connect power budgets, batteries, solar panels, and loads to simulation-in-the-loop or executable checks?
- Is EPS-specific evidence distinct from system-level-only evidence?

Outputs:

- EPS element → verification mechanism → IV&V level graph
- table of EPS gaps by element

### E3 — Toolchain interoperability network

Goal: analyze tool/language combinations and interoperability mechanisms.

Queries:

- Which tools co-occur most often?
- Are import/export and spreadsheets dominant over semantic transformations or APIs?
- Which toolchains are associated with tool dependency, vendor lock-in, or manual translation limitations?

Outputs:

- tool co-occurrence graph
- tool → interoperability mechanism heatmap
- limitation overlay graph

### E4 — Reuse/generality evidence map

Goal: separate real reusable artifacts from reusable-method claims.

Queries:

- Which studies claim templates/reference models/open packages?
- Which reuse claims have actual availability evidence?
- Are high-level abstractions associated with model availability?

Outputs:

- reuse mechanism → evidence type → availability map
- ranked reusable artifact candidates

### E5 — Limitation/gap co-occurrence graph

Goal: identify dominant research bottlenecks.

Queries:

- Which limitation flags co-occur most strongly?
- Which gaps are only conceptually addressed while linked to weak evidence?
- Are `model_not_available`, `no_independent_validation`, and `no_physical_test_or_flight_evidence` central limitations?

Outputs:

- limitation co-occurrence network
- gap × limitation heatmap
- centrality-ranked bottleneck list

### E6 — Lifecycle coverage graph

Goal: characterize where in lifecycle the evidence concentrates.

Queries:

- Are concept/pre-Phase A studies overrepresented?
- Which outcomes are supported past PDR/CDR/I&T?
- Which verification artifacts appear in later stages?

Outputs:

- lifecycle stage coverage plot
- lifecycle → artifact → evidence confidence graph

### E7 — Study semantic clustering

Goal: cluster papers by semantic content and compare clusters against controlled approach classes.

Method:

- Embed `study_card`.
- Project with UMAP.
- Cluster with HDBSCAN or agglomerative clustering.
- Compare clusters with approach class, EPS relevance, and model maturity.

Outputs:

- 2D UMAP plot colored by approach class and EPS relevance
- cluster summaries generated from nearest representative studies
- disagreement list: semantically similar studies with different controlled labels

### E8 — Claim semantic clustering

Goal: identify recurring benefit narratives independent of controlled labels.

Method:

- Embed `claim_card`.
- Cluster claims.
- Summarize clusters by dominant outcome category, mechanism, and evidence confidence.

Outputs:

- claim cluster table
- recurring claim families
- weakly supported high-frequency benefit narratives

### E9 — Emergent-code consolidation

Goal: determine whether emergent codes should become controlled vocabulary candidates.

Method:

- Embed emergent code descriptions and rationales.
- Cluster near-duplicates.
- Link emergent codes to controlled fields and studies.

Outputs:

- candidate codebook extensions
- duplicate/near-duplicate emergent code clusters

### E10 — Consistency and miscoding audit

Goal: flag potential extraction inconsistencies for human review.

Methods:

- Find semantically similar claims with different `evidence_confidence_rating`.
- Find semantically similar studies with different `approach_classification`.
- Find studies with similar EPS verification descriptions but different `ivv_integration_level`.

Outputs:

- audit queue CSV, not automatic corrections
- explanation for each flagged pair: similarity score + differing controlled fields + evidence quotes

### E11 — Hybrid similarity graph

Goal: augment the KG with `SIMILAR_TO` edges from embeddings.

Method:

- Add `Study SIMILAR_TO Study` and `Claim SIMILAR_TO Claim` edges based on audited thresholds.
- Run community detection on the combined controlled-code + similarity graph.

Outputs:

- graph communities
- representative studies/claims by community
- comparison to controlled clusters

### E12 — GraphRAG over SLR evidence

Goal: query the evidence base using both vector retrieval and graph expansion.

Example questions:

- “Which papers provide the strongest evidence for EPS pre-physical verification?”
- “What toolchains support simulation-in-the-loop verification?”
- “Which claims about effort reduction have baseline comparators?”
- “Where are reusable reference models available?”

Retrieval recipe:

1. Embed question and retrieve top claims/studies/evidence quotes.
2. Expand in KG by 1–2 hops: study → claims → evidence type/confidence → limitations/gaps.
3. Return answer with citations to `corpus_id`, field paths, and evidence quotes.

Outputs:

- `outputs/reports/graphrag_demo_questions.md`
- retrieval traces for every answer

### E13 — Research agenda prioritization

Goal: rank gaps by frequency, evidence weakness, EPS relevance, lifecycle importance, and lack of reusable artifacts.

Potential score:

```text
gap_priority = frequency
             + weak_evidence_weight
             + eps_specificity_weight
             + lifecycle_undercoverage_weight
             + model_unavailability_weight
             + no_independent_validation_weight
```

Outputs:

- ranked research gaps
- defensible future research agenda table

## 9. Quality controls

Every generated insight should preserve provenance:

- `study_id`
- `claim_id` if claim-level
- `field_path`
- controlled code value
- exact evidence quote where available
- embedding model and vector index version if embedding-derived
- graph construction version

Any embedding-derived finding should be labeled as exploratory unless manually validated.

## 10. Suggested implementation order

1. E0: flatten and validate.
2. Build KG MVP.
3. E1, E2, E3: run controlled-code graph analyses.
4. Build text cards and embeddings.
5. E7, E8, E9: semantic clusters.
6. Add similarity edges and run E10/E11.
7. Prototype GraphRAG E12.
8. Compile E13 research agenda.

## 11. Useful references persisted here

Metadata and BibTeX are in:

- `references/references_used.json`
- `references/references_used.bib`

Downloaded open-access PDFs are in:

- `papers/`

Search provenance is in:

- `searches/`
