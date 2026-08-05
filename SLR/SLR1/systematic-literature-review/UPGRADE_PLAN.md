# SLR Upgrade Plan

Goal: upgrade the SLR into an **evidence-chain review** that extracts maximum value from the existing extraction data.

The upgraded manuscript should answer:

> What is modeled, how mature/generalizable is it, what value is claimed, what evidence supports that value, and how far does the model reach toward verification/test?

## 1. Keep the current primary variables as the backbone

These remain the core manuscript variables.

| Review concern | Primary variables |
|---|---|
| General nanosatellite/EPS modeling | EPS relevance, modeling scope, model maturity, generality/reuse mechanism |
| Claimed MBSE value | outcome domain, evidence confidence, metric/baseline availability |
| Reliability/reproducibility/integrability | reliability subtype, claim specificity, claim-evidence linkage |
| Pre-physical verification | V\&V linkage category, IVV integration level, simulation/test-readiness evidence |
| Buruso Table 5 gaps | implementation pathway, toolchain fragmentation, lightweight tailoring, governance/ROI, NewSpace/agile fit |

These should remain the main Results structure.

## 2. Add the strongest missing variables

Add these because they extract more value from the existing protocol data.

| New variable | Why add it | Best use |
|---|---|---|
| **Lifecycle stage addressed** | Shows whether evidence is concentrated before PDR and weak in integration/test. | Results + Discussion |
| **Model maturity** | Shows whether work is conceptual, prototype, executable, project-applied, or validated. | Main figure/table |
| **Model artifacts used** | Shows what MBSE artifacts actually carry generality/V\&V. | Results table or appendix |
| **EPS elements modeled** | Makes the EPS contribution concrete. | Main figure/table |
| **Interoperability mechanisms and limitations** | Turns tool lists into evidence about fragmentation. | Results + Buruso-gap discussion |
| **Claim specificity, evidence type, baseline comparator** | Explains why value claims are weak or strong. | Main RQ2 analysis |
| **Governance/ROI/project decision linkage** | Supports the value-driven MBSE gap. | Discussion, not necessarily main graph |

## 3. Reorganize the Results section around an evidence chain

Recommended Results structure:

1. **Search, study characteristics, and quality**
   - PRISMA
   - quality score
   - core/supporting studies
   - extraction confidence

2. **RQ1: Modeling generality and EPS representation**
   - EPS relevance
   - model maturity
   - modeling scope/artifacts
   - generality/reuse mechanisms
   - EPS elements modeled

3. **MBSE approach and toolchain continuity**
   - Pure/Enhanced/Extended/Integrated
   - tool/language summary
   - interoperability mechanisms
   - toolchain limitations

4. **RQ2: Claimed outcomes and evidence strength**
   - outcome domains
   - evidence confidence
   - evidence type
   - metric/baseline availability
   - claim specificity
   - reliability subtype

5. **RQ3: Verification and validation integration**
   - V\&V linkage categories
   - IVV integration level
   - V\&V artifacts
   - integration/test readiness
   - lifecycle stage x IVV maturity

6. **Gap mapping**
   - Buruso-inspired gap table/figure
   - practical implementation pathway
   - interoperability
   - lightweight tailoring
   - governance/ROI
   - NewSpace/agile/distributed fit

## 4. Add or upgrade figures/tables

Recommended figure/table package:

| Artifact | Status | Purpose |
|---|---|---|
| PRISMA flow | Keep | Review transparency |
| EPS relevance counts | Keep or combine | Shows EPS-specific evidence is sparse |
| **EPS relevance x model maturity heatmap** | Add | Stronger than EPS relevance alone |
| **EPS elements modeled bar chart** | Add | Shows what EPS modeling actually means |
| Generality/reuse mechanism table | Keep/upgrade | Supports RQ1 |
| Approach classification table | Keep | Positions the studies relative to Buruso |
| **Toolchain mechanisms + limitations table** | Add | Supports fragmentation/interoperability discussion |
| Claim evidence by outcome | Keep | Core RQ2 evidence |
| **Evidence type + baseline availability table** | Add | Explains why claims are weak |
| Reliability subtype table | Keep | Prevents overclaiming EPS reliability |
| V\&V linkage counts | Keep | Core RQ3 evidence |
| **Lifecycle stage x IVV integration level heatmap** | Add if space permits | Shows verification does not mature into test/integration |
| Gap mapping counts | Keep | Connects to Buruso Table 5 |
| Kaslow/CSRM lineage timeline | Keep in Discussion | Interpretive evidence map |

If the article becomes too long, move model artifacts, full toolchain details, and sensitivity checks to an appendix.

## 5. Add cross-tabs to extract deeper value

Best cross-tabs:

1. **EPS relevance x model maturity**  
   Shows whether EPS-specific studies are mature or mostly prototype/preliminary.

2. **Lifecycle stage x IVV integration level**  
   Shows whether verification remains pre-physical.

3. **Outcome domain x evidence confidence**  
   Already partly done; keep central.

4. **Claim specificity x evidence confidence**  
   Shows whether EPS-specific claims are weaker/rarer than generic MBSE claims.

5. **Evidence type x baseline comparator**  
   Shows why strong claims are rare.

6. **EPS elements modeled x V\&V artifact type**  
   Useful for a stronger EPS-specific contribution.

## 6. Strengthen Discussion around five findings

Use the upgraded variables to support these discussion claims:

1. **Whole-CubeSat MBSE is more mature than EPS-specific MBSE**  
   Supported by EPS relevance, model maturity, and the Kaslow/CSRM lineage.

2. **EPS modeling is mostly power-budget/energy-balance modeling**  
   Supported by EPS elements modeled: solar panels, batteries, loads, and budgets dominate; degradation and fault protection are rare.

3. **Value claims are common but weakly evidenced**  
   Supported by claim evidence confidence, evidence type, metrics, and baseline/comparator data.

4. **Pre-physical V\&V exists, but continuous model-to-test verification is rare**  
   Supported by V\&V linkage, IVV integration level, lifecycle stage, and integration/test readiness.

5. **Toolchain and governance gaps remain the bottleneck**  
   Supported by interoperability mechanisms, toolchain limitations, governance/ROI variables, and Buruso gap mapping.

## 7. Implementation tasks in the repository

Update:

- `SLR/SLR1/systematic-literature-review/scripts/generate_slr_artifacts.py`
- `SLR/SLR1/systematic-literature-review/drafts/data_summary.md`
- `SLR/SLR1/systematic-literature-review/drafts/results_tables.tex`
- `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex`

### New CSV outputs

Generate these additional CSVs:

- `data/lifecycle_stage_counts.csv`
- `data/model_maturity_counts.csv`
- `data/model_maturity_by_eps_relevance.csv`
- `data/model_artifacts_counts.csv`
- `data/eps_elements_modeled_counts.csv`
- `data/interoperability_mechanisms_counts.csv`
- `data/toolchain_limitations_counts.csv`
- `data/claim_specificity_counts.csv`
- `data/evidence_type_counts.csv`
- `data/baseline_comparator_counts.csv`
- `data/lifecycle_by_ivv_integration_level.csv`
- `data/governance_roi_counts.csv`

### New figure outputs

Generate these additional figures:

- `figures/model_maturity_by_eps_relevance.{pdf,png,svg}`
- `figures/eps_elements_modeled.{pdf,png,svg}`
- `figures/toolchain_mechanisms_limitations.{pdf,png,svg}`
- `figures/claim_evidence_anatomy.{pdf,png,svg}`
- `figures/lifecycle_ivv_heatmap.{pdf,png,svg}`

## 8. Final manuscript logic

The upgraded SLR should make this argument:

> The nanosatellite MBSE literature contains many reusable system-level models and many claimed benefits, but the evidence chain weakens as the focus narrows to EPS, quantified value, and verification closure. EPS modeling is usually represented through power budgets, solar/battery/load abstractions, and pre-physical simulations. However, few studies provide EPS-specific model maturity, baseline-backed value evidence, governance/ROI linkage, or continuous model-to-test verification.

This is the highest-value synthesis that can be extracted from the current data.
