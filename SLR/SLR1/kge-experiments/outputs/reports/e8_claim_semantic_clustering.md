# E8 — Claim semantic clustering

**Exploratory notice:** claim clusters are generated from `hashing_tfidf_v1` hashing-TFIDF vectors and thresholded connected components. They identify candidate recurrent narratives, not validated claim families.

Claim cards: **270**. Clusters: **232**. Multi-claim clusters: **14**.
Cluster threshold: `0.55`.

## Cluster summaries by dominant outcome, mechanism, and evidence confidence

| cluster_id | cluster_size | representative_claim_id | dominant_outcome_category | dominant_mbse_mechanism | dominant_evidence_confidence | weak_or_unsupported_claims | claim_ids |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claim_cluster_001 | 18 | paper-0031::claim-05 | generality/reuse | reference model reuse | Weak | 18 | paper-0001::claim-08; paper-0003::claim-09; paper-0004::claim-01; paper-0005::claim-01; paper-0005::claim-06; paper-0013::claim-01; paper-0014::claim-01; paper-0015::claim-02; paper-0016::claim-01; paper-0016::claim-06; paper-0022::claim-02; paper-0022::claim-06; paper-0031::claim-04; paper-0031::claim-05; paper-0031::claim-07; paper-0031::claim-10; paper-0031::claim-11; paper-0077::claim-01 |
| claim_cluster_002 | 9 | paper-0014::claim-02 | traceability | requirements linkage | Weak | 6 | paper-0001::claim-01; paper-0004::claim-03; paper-0011::claim-03; paper-0011::claim-08; paper-0014::claim-02; paper-0014::claim-06; paper-0015::claim-04; paper-0077::claim-04; paper-0080::claim-01 |
| claim_cluster_003 | 3 | paper-0016::claim-04 | integrability/interoperability | tool integration | Weak | 2 | paper-0004::claim-02; paper-0016::claim-04; paper-0031::claim-01 |
| claim_cluster_004 | 2 | paper-0004::claim-06 | communication/stakeholder alignment; effort reduction; generality/reuse | reference model reuse | Weak | 2 | paper-0004::claim-06; paper-0022::claim-05 |
| claim_cluster_005 | 2 | paper-0005::claim-03 | lifecycle continuity; mission assurance; traceability | artifact traceability; other | Weak | 2 | paper-0005::claim-03; paper-0015::claim-05 |
| claim_cluster_006 | 2 | paper-0011::claim-07 | decision support; integrability/interoperability | parametric analysis; tool integration | Weak | 2 | paper-0011::claim-07; paper-0013::claim-08 |
| claim_cluster_008 | 2 | paper-0016::claim-05 | effort reduction; generality/reuse | other; reference model reuse | Unsupported | 2 | paper-0016::claim-05; paper-0031::claim-09 |
| claim_cluster_011 | 2 | paper-0031::claim-06 | communication/stakeholder alignment; traceability | artifact traceability; requirements linkage | Weak | 2 | paper-0031::claim-06; paper-0077::claim-03 |
| claim_cluster_013 | 2 | paper-0071::claim-01 | decision support; risk reduction | other | Weak | 2 | paper-0071::claim-01; paper-0071::claim-03 |
| claim_cluster_014 | 2 | paper-0079::claim-03 | effort reduction; integrability/interoperability; lifecycle continuity | automated generation; model transformation; tool integration | Weak | 2 | paper-0079::claim-03; paper-0079::claim-06 |
| claim_cluster_007 | 2 | paper-0016::claim-03 | automation; decision support; integrability/interoperability | executable simulation; parametric analysis; tool integration | Moderate | 0 | paper-0016::claim-03; paper-0031::claim-08 |
| claim_cluster_009 | 2 | paper-0023::claim-04 | mission assurance; traceability | artifact traceability; requirements linkage | Moderate | 0 | paper-0023::claim-04; paper-0023::claim-06 |
| claim_cluster_010 | 2 | paper-0029::claim-03 | communication/stakeholder alignment; generality/reuse; reproducibility | other; shared repository | Moderate | 0 | paper-0029::claim-03; paper-0043::claim-07 |
| claim_cluster_012 | 2 | paper-0061::claim-01 | cost reduction; effort reduction; governance/ROI; schedule reduction | other; parametric analysis; shared repository; tool integration | Strong | 0 | paper-0061::claim-01; paper-0061::claim-02 |
| claim_cluster_021 | 1 | paper-0001::claim-09 | generality/reuse; other | executable simulation; other; tool integration | Unsupported | 1 | paper-0001::claim-09 |
| claim_cluster_022 | 1 | paper-0002::claim-01 | communication/stakeholder alignment; consistency; mission assurance; risk reduction | automated generation; shared repository | Unsupported | 1 | paper-0002::claim-01 |
| claim_cluster_023 | 1 | paper-0002::claim-02 | generality/reuse; reproducibility | other; reference model reuse; requirements linkage | Weak | 1 | paper-0002::claim-02 |
| claim_cluster_024 | 1 | paper-0002::claim-03 | completeness; traceability | artifact traceability; requirements linkage | Weak | 1 | paper-0002::claim-03 |
| claim_cluster_025 | 1 | paper-0002::claim-04 | completeness; generality/reuse | other; requirements linkage | Weak | 1 | paper-0002::claim-04 |
| claim_cluster_026 | 1 | paper-0002::claim-05 | generality/reuse | method guidance | Unsupported | 1 | paper-0002::claim-05 |
| claim_cluster_027 | 1 | paper-0003::claim-01 | decision support; lifecycle continuity; mission assurance; risk reduction | executable simulation; other; tool integration | Weak | 1 | paper-0003::claim-01 |
| claim_cluster_028 | 1 | paper-0003::claim-02 | automation; effort reduction; integrability/interoperability | executable simulation; tool integration | Weak | 1 | paper-0003::claim-02 |
| claim_cluster_031 | 1 | paper-0003::claim-05 | decision support; lifecycle continuity; mission assurance | executable simulation; other; requirements linkage; tool integration | Weak | 1 | paper-0003::claim-05 |
| claim_cluster_032 | 1 | paper-0003::claim-06 | integrability/interoperability; lifecycle continuity; mission assurance | artifact traceability; executable simulation; other; tool integration | Weak | 1 | paper-0003::claim-06 |
| claim_cluster_034 | 1 | paper-0003::claim-08 | communication/stakeholder alignment; effort reduction; generality/reuse | other; reference model reuse; shared repository | Weak | 1 | paper-0003::claim-08 |
| claim_cluster_035 | 1 | paper-0003::claim-10 | communication/stakeholder alignment; mission assurance; traceability | artifact traceability; requirements linkage; shared repository | Weak | 1 | paper-0003::claim-10 |
| claim_cluster_037 | 1 | paper-0004::claim-05 | communication/stakeholder alignment; governance/ROI; mission assurance | artifact traceability; other | Unsupported | 1 | paper-0004::claim-05 |
| claim_cluster_038 | 1 | paper-0004::claim-07 | generality/reuse; governance/ROI; lifecycle continuity | lifecycle gate support; reference model reuse | Weak | 1 | paper-0004::claim-07 |
| claim_cluster_039 | 1 | paper-0005::claim-02 | consistency; lifecycle continuity; traceability | artifact traceability; requirements linkage | Weak | 1 | paper-0005::claim-02 |
| claim_cluster_040 | 1 | paper-0005::claim-04 | integrability/interoperability; lifecycle continuity; mission assurance | executable simulation; tool integration | Unsupported | 1 | paper-0005::claim-04 |

_Showing 30 of 232 rows._


## Weakly supported recurrent narratives

See `outputs/reports/weak_recurrent_claims.md`. Top entries:

| cluster_id | cluster_size | weak_or_unsupported_claims | dominant_outcome_category | dominant_mbse_mechanism |
| --- | --- | --- | --- | --- |
| claim_cluster_001 | 18 | 18 | generality/reuse | reference model reuse |
| claim_cluster_002 | 9 | 6 | traceability | requirements linkage |
| claim_cluster_003 | 3 | 2 | integrability/interoperability | tool integration |
| claim_cluster_004 | 2 | 2 | communication/stakeholder alignment; effort reduction; generality/reuse | reference model reuse |
| claim_cluster_005 | 2 | 2 | lifecycle continuity; mission assurance; traceability | artifact traceability; other |
| claim_cluster_006 | 2 | 2 | decision support; integrability/interoperability | parametric analysis; tool integration |
| claim_cluster_008 | 2 | 2 | effort reduction; generality/reuse | other; reference model reuse |
| claim_cluster_011 | 2 | 2 | communication/stakeholder alignment; traceability | artifact traceability; requirements linkage |
| claim_cluster_013 | 2 | 2 | decision support; risk reduction | other |
| claim_cluster_014 | 2 | 2 | effort reduction; integrability/interoperability; lifecycle continuity | automated generation; model transformation; tool integration |

