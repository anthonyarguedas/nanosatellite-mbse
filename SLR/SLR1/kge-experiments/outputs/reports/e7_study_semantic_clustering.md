# E7 — Study semantic clustering

**Exploratory notice:** clusters and disagreements are generated from the deterministic `hashing_tfidf_v1` hashing-TFIDF fallback and are audit aids only.

## Method

- Projection: PCA via `numpy.linalg.svd` as a dependency-light fallback for the intended UMAP output. The SVG is still named `study_umap.svg` for the planned artifact, but its metadata and this report identify it as PCA/SVD fallback.
- Clustering: thresholded connected components over same-unit study-card cosine similarities.
- Study cluster threshold: `0.65`.
- Disagreement-list threshold: `0.6`.

Study cards: **40**. Clusters: **31** total; **2** multi-study clusters.

## Cluster summaries

| cluster_id | cluster_size | representative_study_id | dominant_approach_classification | dominant_eps_relevance | dominant_model_maturity | study_ids |
| --- | --- | --- | --- | --- | --- | --- |
| study_cluster_001 | 7 | paper-0054 | Integrated MBSE/digital engineering | power-budget/electrical-architecture | executable model; prototype demonstration | paper-0043; paper-0054; paper-0059; paper-0063; paper-0078; paper-0079; paper-0080 |
| study_cluster_002 | 4 | paper-0016 | Extended MBSE | power-budget/electrical-architecture | reference model/template | paper-0004; paper-0016; paper-0022; paper-0031 |
| study_cluster_003 | 1 | paper-0001 | Extended MBSE | power-budget/electrical-architecture | executable model; prototype demonstration; reference model/template | paper-0001 |
| study_cluster_004 | 1 | paper-0002 | Pure MBSE | system-level only | conceptual framework; prototype demonstration; reference model/template | paper-0002 |
| study_cluster_005 | 1 | paper-0003 | Integrated MBSE/digital engineering | power-budget/electrical-architecture | executable model; project-applied model; prototype demonstration; reference model/template | paper-0003 |
| study_cluster_006 | 1 | paper-0005 | Extended MBSE | EPS-adjacent | prototype demonstration; reference model/template | paper-0005 |
| study_cluster_007 | 1 | paper-0007 | Enhanced MBSE | EPS-adjacent; EPS-adjacent: battery-cycle and solar-cell-life MOPs appear, but no EPS subsystem architecture, power budget, or EPS verification procedure is presented. | conceptual framework; prototype demonstration; reference model/template | paper-0007 |
| study_cluster_008 | 1 | paper-0008 | Integrated MBSE/digital engineering | power-budget/electrical-architecture | conceptual framework; executable model; project-applied model; prototype demonstration; reference model/template | paper-0008 |
| study_cluster_009 | 1 | paper-0010 | Enhanced MBSE | system-level only | conceptual framework | paper-0010 |
| study_cluster_010 | 1 | paper-0011 | Pure MBSE | EPS-adjacent | project-applied model; reference model/template | paper-0011 |
| study_cluster_011 | 1 | paper-0012 | Extended MBSE | power-budget/electrical-architecture | conceptual framework; executable model; prototype demonstration | paper-0012 |
| study_cluster_012 | 1 | paper-0013 | Extended MBSE | EPS-adjacent | prototype demonstration; reference model/template | paper-0013 |
| study_cluster_013 | 1 | paper-0014 | Extended MBSE | EPS-adjacent | conceptual framework; reference model/template | paper-0014 |
| study_cluster_014 | 1 | paper-0015 | Pure MBSE | EPS-adjacent | conceptual framework; prototype demonstration; reference model/template | paper-0015 |
| study_cluster_015 | 1 | paper-0023 | Extended MBSE | power-budget/electrical-architecture | conceptual framework; project-applied model; prototype demonstration; reference model/template | paper-0023 |
| study_cluster_016 | 1 | paper-0024 | Extended MBSE | not EPS-relevant; not EPS-relevant; Power System only appears as high-level subsystem | conceptual framework; prototype demonstration | paper-0024 |
| study_cluster_017 | 1 | paper-0026 | Enhanced MBSE | EPS-specific | prototype demonstration; reference model/template | paper-0026 |
| study_cluster_018 | 1 | paper-0027 | Enhanced MBSE | power-budget/electrical-architecture | executable model; project-applied model; prototype demonstration | paper-0027 |
| study_cluster_019 | 1 | paper-0029 | Extended MBSE | power-budget/electrical-architecture | conceptual framework; executable model; prototype demonstration; reference model/template | paper-0029 |
| study_cluster_020 | 1 | paper-0033 | Enhanced MBSE | power-budget/electrical-architecture | executable model; project-applied model; prototype demonstration | paper-0033 |
| study_cluster_021 | 1 | paper-0034 | Pure MBSE | system-level only | conceptual framework; prototype demonstration | paper-0034 |
| study_cluster_022 | 1 | paper-0037 | Enhanced MBSE | EPS-adjacent | project-applied model; prototype demonstration | paper-0037 |
| study_cluster_023 | 1 | paper-0039 | Pure MBSE | power-budget/electrical-architecture | project-applied model; prototype demonstration; reference model/template | paper-0039 |
| study_cluster_024 | 1 | paper-0041 | Enhanced MBSE | power-budget/electrical-architecture | executable model; prototype demonstration | paper-0041 |
| study_cluster_025 | 1 | paper-0046 | Enhanced MBSE | EPS-adjacent | prototype demonstration | paper-0046 |

_Showing 25 of 31 rows._


## Semantically similar studies with different controlled labels

| similarity | study_id_1 | study_id_2 | differing_controlled_labels |
| --- | --- | --- | --- |
| 0.725830 | paper-0043 | paper-0054 | approach_classification: Integrated MBSE/digital engineering vs Enhanced MBSE | model_maturity: conceptual framework; executable model; prototype demonstration vs executable model; project-applied model; prototype demonstration |
| 0.715728 | paper-0054 | paper-0078 | approach_classification: Enhanced MBSE vs Extended MBSE | model_maturity: executable model; project-applied model; prototype demonstration vs project-applied model |
| 0.685979 | paper-0063 | paper-0079 | eps_relevance: system-level only vs EPS-adjacent | model_maturity: executable model; project-applied model; prototype demonstration vs conceptual framework; executable model; project-applied model; prototype demonstration; reference model/template |
| 0.685525 | paper-0059 | paper-0079 | eps_relevance: EPS-specific vs EPS-adjacent | model_maturity: executable model; prototype demonstration vs conceptual framework; executable model; project-applied model; prototype demonstration; reference model/template |
| 0.677890 | paper-0004 | paper-0016 | approach_classification: Extended MBSE vs Enhanced MBSE | model_maturity: conceptual framework; prototype demonstration; reference model/template vs conceptual framework; project-applied model; prototype demonstration; reference model/template |
| 0.677377 | paper-0043 | paper-0078 | approach_classification: Integrated MBSE/digital engineering vs Extended MBSE | model_maturity: conceptual framework; executable model; prototype demonstration vs project-applied model |
| 0.667543 | paper-0016 | paper-0031 | approach_classification: Enhanced MBSE vs Extended MBSE | model_maturity: conceptual framework; project-applied model; prototype demonstration; reference model/template vs executable model; project-applied model; prototype demonstration; reference model/template |
| 0.662395 | paper-0054 | paper-0059 | approach_classification: Enhanced MBSE vs Integrated MBSE/digital engineering | eps_relevance: power-budget/electrical-architecture vs EPS-specific | model_maturity: executable model; project-applied model; prototype demonstration vs executable model; prototype demonstration |
| 0.655760 | paper-0043 | paper-0079 | eps_relevance: power-budget/electrical-architecture vs EPS-adjacent | model_maturity: conceptual framework; executable model; prototype demonstration vs conceptual framework; executable model; project-applied model; prototype demonstration; reference model/template |
| 0.654032 | paper-0054 | paper-0079 | approach_classification: Enhanced MBSE vs Integrated MBSE/digital engineering | eps_relevance: power-budget/electrical-architecture vs EPS-adjacent | model_maturity: executable model; project-applied model; prototype demonstration vs conceptual framework; executable model; project-applied model; prototype demonstration; reference model/template |
| 0.651515 | paper-0078 | paper-0080 | approach_classification: Extended MBSE vs Enhanced MBSE | model_maturity: project-applied model vs executable model; project-applied model; prototype demonstration |
| 0.650532 | paper-0016 | paper-0022 | approach_classification: Enhanced MBSE vs Extended MBSE | model_maturity: conceptual framework; project-applied model; prototype demonstration; reference model/template vs conceptual framework; reference model/template |
| 0.648953 | paper-0016 | paper-0054 | model_maturity: conceptual framework; project-applied model; prototype demonstration; reference model/template vs executable model; project-applied model; prototype demonstration |
| 0.648457 | paper-0053 | paper-0079 | approach_classification: Extended MBSE vs Integrated MBSE/digital engineering | eps_relevance: power-budget/electrical-architecture vs EPS-adjacent | model_maturity: executable model; project-applied model; prototype demonstration vs conceptual framework; executable model; project-applied model; prototype demonstration; reference model/template |
| 0.644690 | paper-0027 | paper-0029 | approach_classification: Enhanced MBSE vs Extended MBSE | model_maturity: executable model; project-applied model; prototype demonstration vs conceptual framework; executable model; prototype demonstration; reference model/template |
| 0.643381 | paper-0053 | paper-0054 | approach_classification: Extended MBSE vs Enhanced MBSE |
| 0.642535 | paper-0016 | paper-0080 | model_maturity: conceptual framework; project-applied model; prototype demonstration; reference model/template vs executable model; project-applied model; prototype demonstration |
| 0.639591 | paper-0054 | paper-0063 | approach_classification: Enhanced MBSE vs Integrated MBSE/digital engineering | eps_relevance: power-budget/electrical-architecture vs system-level only |
| 0.639288 | paper-0080 | paper-0081 | approach_classification: Enhanced MBSE vs Extended MBSE | eps_relevance: power-budget/electrical-architecture vs EPS-adjacent | model_maturity: executable model; project-applied model; prototype demonstration vs conceptual framework; prototype demonstration; reference model/template |
| 0.638644 | paper-0001 | paper-0004 | model_maturity: executable model; prototype demonstration; reference model/template vs conceptual framework; prototype demonstration; reference model/template |
| 0.638443 | paper-0033 | paper-0043 | approach_classification: Enhanced MBSE vs Integrated MBSE/digital engineering | model_maturity: executable model; project-applied model; prototype demonstration vs conceptual framework; executable model; prototype demonstration |
| 0.637946 | paper-0053 | paper-0059 | approach_classification: Extended MBSE vs Integrated MBSE/digital engineering | eps_relevance: power-budget/electrical-architecture vs EPS-specific | model_maturity: executable model; project-applied model; prototype demonstration vs executable model; prototype demonstration |
| 0.635310 | paper-0016 | paper-0079 | approach_classification: Enhanced MBSE vs Integrated MBSE/digital engineering | eps_relevance: power-budget/electrical-architecture vs EPS-adjacent | model_maturity: conceptual framework; project-applied model; prototype demonstration; reference model/template vs conceptual framework; executable model; project-applied model; prototype demonstration; reference model/template |
| 0.634806 | paper-0043 | paper-0080 | approach_classification: Integrated MBSE/digital engineering vs Enhanced MBSE | model_maturity: conceptual framework; executable model; prototype demonstration vs executable model; project-applied model; prototype demonstration |
| 0.633593 | paper-0053 | paper-0078 | model_maturity: executable model; project-applied model; prototype demonstration vs project-applied model |

_Showing 25 of 89 rows._


Outputs: `outputs/tables/study_clusters.csv`, `outputs/tables/study_projection.csv`, and `outputs/figures/study_umap.svg`.
