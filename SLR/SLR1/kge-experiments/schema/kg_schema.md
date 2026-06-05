# Proposed KG Schema for SLR1

This schema is intentionally small enough for a first implementation, but expressive enough to support evidence, toolchain, EPS, limitation, and gap analyses.

## 1. Node labels

### Study

Properties:

- `id`: corpus id, e.g. `paper-0001`
- `title`
- `year`
- `tier`
- `doi`
- `quality_score_total`
- `extraction_confidence`
- `rq1_relevance`, `rq2_relevance`, `rq3_relevance`
- `eps_relevance`
- `approach_classification`

### Claim

Properties:

- `id`: stable generated id, e.g. `paper-0001::claim-01`
- `study_id`
- `claim_text`
- `metric_detail`
- `observed_effect_or_qualitative_effect`
- `artifact_or_process_linked`
- `evidence_source`
- `threats_or_alternative_explanations`

### Controlled-code nodes

Use one node label per conceptual dimension:

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

Shared properties:

- `id`: normalized slug
- `label`: human-readable value
- `source_field_paths`: optional list

## 2. Core edges

### Study-level edges

| Edge | From | To | Source field |
|---|---|---|---|
| `HAS_APPROACH_CLASS` | Study | ApproachClass | `implementation_pathway_tailoring.approach_classification` |
| `HAS_EPS_RELEVANCE` | Study | EPSRelevance | `study_context_population.eps_relevance` |
| `ADDRESSES_RQ` | Study | RQ | `bibliographic_review_management.rq*_relevance` |
| `ADDRESSES_LIFECYCLE_STAGE` | Study | LifecycleStage | `study_context_population.lifecycle_stage_addressed` |
| `HAS_DEVELOPMENT_CONTEXT` | Study | DevelopmentContext | `study_context_population.development_context` |
| `HAS_MODEL_MATURITY` | Study | ModelMaturity | `study_context_population.model_maturity` |
| `HAS_MODELING_SCOPE` | Study | ModelingScope | `mbse_objective_scope_artifacts.modeling_scope` |
| `USES_MODEL_ARTIFACT` | Study | ModelArtifact | `mbse_objective_scope_artifacts.model_artifacts_used` |
| `HAS_REUSE_MECHANISM` | Study | ReuseMechanism | `mbse_objective_scope_artifacts.generality_reuse_mechanism` |
| `HAS_TAILORING_RATIONALE` | Study | TailoringRationale | `implementation_pathway_tailoring.tailoring_rationale` |
| `USES_TOOL` | Study | Tool | `toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool` |
| `HAS_INTEROPERABILITY_MECHANISM` | Study | InteroperabilityMechanism | `toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms` |
| `HAS_TOOLCHAIN_LIMITATION` | Study | ToolchainLimitation | `toolchain_interoperability_lifecycle_continuity.toolchain_limitations` |
| `MODELS_EPS_ELEMENT` | Study | EPSElement | `eps_verification_specific.eps_elements_modeled` |
| `USES_VERIFICATION_ARTIFACT` | Study | VerificationArtifact | `eps_verification_specific.verification_validation_artifacts` |
| `USES_VERIFICATION_MECHANISM` | Study | VerificationMechanism | `eps_verification_specific.pre_physical_development_verification_mechanism` |
| `HAS_IVV_LEVEL` | Study | IVVIntegrationLevel | `eps_verification_specific.ivv_integration_level` |
| `HAS_LIMITATION` | Study | LimitationFlag | `structured_limitations.limitation_flags` |
| `ADDRESSES_GAP` | Study | Gap | `gap_mapping.*` |
| `HAS_EMERGENT_CODE` | Study | EmergentCode | `emergent_codes[]` |

### Claim-level edges

| Edge | From | To | Source field |
|---|---|---|---|
| `HAS_CLAIM` | Study | Claim | `claimed_outcomes_value_mechanisms_evidence[]` |
| `CLAIMS_OUTCOME` | Claim | OutcomeCategory | `outcome_category` |
| `HAS_SPECIFICITY` | Claim | SpecificityOfClaim | `specificity_of_claim` |
| `USES_MBSE_MECHANISM` | Claim | MBSEMechanism | `mbse_mechanism` |
| `CLAIM_AT_LIFECYCLE_STAGE` | Claim | LifecycleStage | `lifecycle_stage` |
| `HAS_EVIDENCE_TYPE` | Claim | EvidenceType | `evidence_type` |
| `HAS_METRIC` | Claim | MetricIndicator | `metric_or_value_indicator` |
| `HAS_BASELINE` | Claim | BaselineComparator | `baseline_comparator` |
| `HAS_EVIDENCE_CONFIDENCE` | Claim | EvidenceConfidence | `evidence_confidence_rating` |
| `HAS_RELIABILITY_SUBTYPE` | Claim | ReliabilitySubtype | `reliability_subtype` |

### Embedding-derived edges

Add only after auditing nearest-neighbor quality.

| Edge | From | To | Properties |
|---|---|---|---|
| `SIMILAR_TO` | Study | Study | `model`, `cosine`, `unit_type='study_card'` |
| `SIMILAR_TO` | Claim | Claim | `model`, `cosine`, `unit_type='claim_card'` |
| `SIMILAR_TO` | EmergentCode | EmergentCode | `model`, `cosine`, `unit_type='emergent_code_card'` |
| `SEMANTICALLY_SUPPORTS` | EvidenceQuote | Claim | optional, if evidence quotes are embedded separately |

## 3. Provenance properties on edges

Every edge derived from extraction data should include:

- `source_field_path`
- `source_value`
- `rationale` where available
- `evidence_quote` where available
- `confidence` where available
- `extraction_version` or source JSON timestamp

## 4. Naming and normalization

Recommended slugs:

```text
lowercase(value)
replace non-alphanumeric with _
strip duplicate underscores
```

Examples:

- `simulation-in-the-loop` → `simulation_in_the_loop`
- `power-budget/electrical-architecture` → `power_budget_electrical_architecture`
- `no_physical_test_or_flight_evidence` remains unchanged

## 5. Example Cypher-style questions

### Weakly supported benefit claims

```cypher
MATCH (s:Study)-[:HAS_CLAIM]->(c:Claim)-[:CLAIMS_OUTCOME]->(o:OutcomeCategory),
      (c)-[:HAS_EVIDENCE_CONFIDENCE]->(ec:EvidenceConfidence)
WHERE ec.label IN ['Weak', 'Unsupported']
RETURN o.label, count(c) AS n
ORDER BY n DESC;
```

### EPS elements with verification mechanisms

```cypher
MATCH (s:Study)-[:MODELS_EPS_ELEMENT]->(e:EPSElement)
OPTIONAL MATCH (s)-[:USES_VERIFICATION_MECHANISM]->(v:VerificationMechanism)
OPTIONAL MATCH (s)-[:HAS_IVV_LEVEL]->(i:IVVIntegrationLevel)
RETURN e.label, v.label, i.label, count(DISTINCT s) AS studies
ORDER BY studies DESC;
```

### Toolchain limitations by tool

```cypher
MATCH (s:Study)-[:USES_TOOL]->(t:Tool),
      (s)-[:HAS_TOOLCHAIN_LIMITATION]->(l:ToolchainLimitation)
RETURN t.label, l.label, count(DISTINCT s) AS studies
ORDER BY studies DESC;
```

### Similar claims with different evidence ratings

```cypher
MATCH (c1:Claim)-[sim:SIMILAR_TO]->(c2:Claim),
      (c1)-[:HAS_EVIDENCE_CONFIDENCE]->(e1:EvidenceConfidence),
      (c2)-[:HAS_EVIDENCE_CONFIDENCE]->(e2:EvidenceConfidence)
WHERE e1.label <> e2.label AND sim.cosine >= 0.82
RETURN c1.id, c2.id, sim.cosine, e1.label, e2.label, c1.claim_text, c2.claim_text
ORDER BY sim.cosine DESC;
```

## 6. First-pass graph simplification

For the first implementation, skip low-yield nodes such as authors and venues unless needed. Focus on claims, tools, EPS, verification, limitations, and gaps.
