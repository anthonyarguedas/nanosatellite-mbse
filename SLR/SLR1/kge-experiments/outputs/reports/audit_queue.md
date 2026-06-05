# E10 — Consistency and miscoding audit queue

**Exploratory notice:** this queue flags potential review pairs from semantic similarity and controlled-field disagreements. It makes **no automatic corrections**.

## Thresholds

- Similar claims with different `evidence_confidence_rating`: `0.55` over `hashing_tfidf_v1` claim-card cosine.
- Similar studies with different `approach_classification`: `0.65` over `hashing_tfidf_v1` study-card cosine.
- Similar EPS verification descriptions with different `ivv_integration_level`: `0.5` over local TF-IDF cosine on EPS verification field text.
- Per-type row cap: `40`.

Audit rows: **60**.

## Rows by audit type

| audit_type | row_count |
| --- | --- |
| similar_claims_different_evidence_confidence | 11 |
| similar_eps_verification_different_ivv_level | 40 |
| similar_studies_different_approach_classification | 9 |


## Highest-priority rows

| audit_id | audit_type | priority | similarity_score | id_1 | id_2 | differing_controlled_fields | field_value_1 | field_value_2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| audit-0001 | similar_claims_different_evidence_confidence | medium | 0.665046 | paper-0016::claim-06 | paper-0022::claim-06 | evidence_confidence_rating | Weak | Unsupported |
| audit-0002 | similar_claims_different_evidence_confidence | medium | 0.658266 | paper-0011::claim-03 | paper-0014::claim-02 | evidence_confidence_rating | Moderate | Weak |
| audit-0003 | similar_claims_different_evidence_confidence | medium | 0.655876 | paper-0005::claim-06 | paper-0016::claim-06 | evidence_confidence_rating | Unsupported | Weak |
| audit-0004 | similar_claims_different_evidence_confidence | medium | 0.600729 | paper-0005::claim-06 | paper-0031::claim-10 | evidence_confidence_rating | Unsupported | Weak |
| audit-0005 | similar_claims_different_evidence_confidence | low | 0.582641 | paper-0001::claim-01 | paper-0004::claim-03 | evidence_confidence_rating | Unsupported | Weak |
| audit-0006 | similar_claims_different_evidence_confidence | low | 0.574947 | paper-0022::claim-06 | paper-0031::claim-10 | evidence_confidence_rating | Unsupported | Weak |
| audit-0007 | similar_claims_different_evidence_confidence | low | 0.570400 | paper-0011::claim-03 | paper-0077::claim-04 | evidence_confidence_rating | Moderate | Weak |
| audit-0008 | similar_claims_different_evidence_confidence | low | 0.562066 | paper-0004::claim-02 | paper-0016::claim-04 | evidence_confidence_rating | Moderate | Weak |
| audit-0009 | similar_claims_different_evidence_confidence | low | 0.560716 | paper-0001::claim-08 | paper-0003::claim-09 | evidence_confidence_rating | Weak | Unsupported |
| audit-0010 | similar_claims_different_evidence_confidence | low | 0.558466 | paper-0011::claim-08 | paper-0077::claim-04 | evidence_confidence_rating | Moderate | Weak |
| audit-0011 | similar_claims_different_evidence_confidence | low | 0.555882 | paper-0004::claim-03 | paper-0015::claim-04 | evidence_confidence_rating | Weak | Moderate |
| audit-0012 | similar_eps_verification_different_ivv_level | high | 0.828714 | paper-0012 | paper-0027 | ivv_integration_level | executable/model-based checks | simulation-in-the-loop |
| audit-0013 | similar_eps_verification_different_ivv_level | high | 0.776335 | paper-0001 | paper-0012 | ivv_integration_level | simulation-in-the-loop | executable/model-based checks |
| audit-0014 | similar_eps_verification_different_ivv_level | high | 0.775671 | paper-0012 | paper-0053 | ivv_integration_level | executable/model-based checks | simulation-in-the-loop |
| audit-0015 | similar_eps_verification_different_ivv_level | high | 0.747355 | paper-0027 | paper-0041 | ivv_integration_level | simulation-in-the-loop | executable/model-based checks |
| audit-0016 | similar_eps_verification_different_ivv_level | high | 0.703470 | paper-0001 | paper-0041 | ivv_integration_level | simulation-in-the-loop | executable/model-based checks |
| audit-0017 | similar_eps_verification_different_ivv_level | medium | 0.697394 | paper-0039 | paper-0043 | ivv_integration_level | none/not reported | simulation-in-the-loop |
| audit-0018 | similar_eps_verification_different_ivv_level | medium | 0.697202 | paper-0054 | paper-0078 | ivv_integration_level | separate document only | trace-linked verification artifacts |
| audit-0019 | similar_eps_verification_different_ivv_level | medium | 0.688638 | paper-0014 | paper-0077 | ivv_integration_level | trace-linked verification artifacts | model-contained verification artifacts |
| audit-0020 | similar_eps_verification_different_ivv_level | medium | 0.674007 | paper-0053 | paper-0078 | ivv_integration_level | simulation-in-the-loop | trace-linked verification artifacts |
| audit-0021 | similar_eps_verification_different_ivv_level | medium | 0.672328 | paper-0059 | paper-0078 | ivv_integration_level | simulation-in-the-loop | trace-linked verification artifacts |
| audit-0022 | similar_eps_verification_different_ivv_level | medium | 0.671726 | paper-0061 | paper-0081 | ivv_integration_level | executable/model-based checks | none/not reported |
| audit-0023 | similar_eps_verification_different_ivv_level | medium | 0.653986 | paper-0078 | paper-0079 | ivv_integration_level | trace-linked verification artifacts | simulation-in-the-loop |
| audit-0024 | similar_eps_verification_different_ivv_level | medium | 0.647220 | paper-0001 | paper-0078 | ivv_integration_level | simulation-in-the-loop | trace-linked verification artifacts |
| audit-0025 | similar_eps_verification_different_ivv_level | medium | 0.646606 | paper-0012 | paper-0033 | ivv_integration_level | executable/model-based checks | simulation-in-the-loop |

_Showing 25 of 60 rows._


Every CSV row includes snippets plus evidence/provenance where available. Reviewers should inspect source extraction evidence before deciding whether any recoding is warranted.
