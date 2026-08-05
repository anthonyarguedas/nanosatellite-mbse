# Systematic-review controlled evidence-artifact summary

## Scope and units

The artifact set summarizes **40 reports** and **270 claim records**. Claims are nested within reports; neither reports nor claims are treated as independent implementations.
Study multi-select outputs count unique report memberships. Claim multi-select outputs count unique claim memberships. Every count CSV gives its denominator and status coverage; codebook-ordered zero categories are retained. `study_characteristics.csv` retains the controlled development-context field and its field status.

Registered review questions: RQ1: How can nanosatellite missions and EPS be modeled in a general manner with minimal knowledge about their behavior?; RQ2: What are the claimed outcomes related to reliability, reproducibility, and integrability derived from EPS modeling in nanosatellite missions?; RQ3: How have verification procedures been integrated into EPS models prior to physical development?.

## Generated outputs

### CSV data

- `data/study_characteristics.csv`
- `data/eps_relevance_counts.csv`
- `data/approach_classification_counts.csv`
- `data/claim_evidence_by_outcome.csv`
- `data/vv_linkage_counts.csv`
- `data/gap_mapping_counts.csv`
- `data/generality_reuse_mechanism_counts.csv`
- `data/ivv_integration_level_counts.csv`
- `data/reliability_subtype_counts.csv`
- `data/top_value_claims.csv`
- `data/kaslow_eps_lineage_timeline.csv`
- `data/pre_physical_verification_mechanism_counts.csv`
- `data/verification_validation_artifacts_counts.csv`
- `data/integration_test_readiness_counts.csv`
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
- `data/claim_specificity_by_evidence_confidence.csv`
- `data/evidence_type_by_baseline_comparator.csv`
- `data/eps_elements_by_vv_artifact.csv`
- `data/field_coverage_status.csv`

### Figures

SVG outputs: `figures/prisma_flow.svg`, `figures/eps_relevance_counts.svg`, `figures/claim_evidence_by_outcome.svg`, `figures/vv_linkage_counts.svg`, `figures/gap_mapping_counts.svg`, `figures/kaslow_eps_lineage_timeline.svg`, `figures/model_maturity_by_eps_relevance.svg`, `figures/eps_elements_modeled.svg`, `figures/toolchain_mechanisms_limitations.svg`, `figures/claim_evidence_anatomy.svg`, `figures/lifecycle_ivv_heatmap.svg`.
Each SVG has matching PDF and PNG derivatives. The maturity × EPS and lifecycle × IVV figures are controlled study-level cross-classifications only / not progression or direct linkage. The lifecycle × IVV display treats `none/not reported` as a controlled level and separately identifies the three reports with no selected IVV level. The claim-anatomy figure retains unmapped/invalid and unassigned classes and defines `comparator recorded`.

### Manuscript snippets

- `drafts/results_tables.tex`
- `drafts/data_summary.md`

## Corpus and evidence counts

| Metric | Count |
|---|---|
| Reports | 40 |
| Core reports | 21 |
| Supporting reports | 19 |
| Publication year range | 2013–2025 |
| Nested claim records | 270 |
| Moderate/Strong claim records | 79 |
| High-confidence extractions | 29 |
| Medium-confidence extractions | 11 |
| Unmapped/invalid baseline values | 5 |
| Unmapped/invalid MBSE mechanism values | 1 |

Claim evidence confidence: Unsupported=52, Weak=139, Moderate=77, Strong=2, unmapped/invalid controlled value=0, unassigned/no controlled value=0.

## Key controlled aggregates

### EPS relevance and model maturity

| EPS relevance | Report memberships (n=40) |
|---|---|
| system-level only | 4 |
| EPS-specific | 2 |
| power-budget/electrical-architecture | 19 |
| EPS-adjacent | 13 |
| not EPS-relevant | 2 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 0 |

| Model maturity | Report memberships (n=40) |
|---|---|
| conceptual framework | 18 |
| reference model/template | 22 |
| prototype demonstration | 35 |
| executable model | 17 |
| project-applied model | 18 |
| validated/operational model | 0 |
| not reported | 0 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 0 |

| Lifecycle stage addressed | Report memberships (n=40; multi-label) |
|---|---|
| concept/pre-Phase A | 36 |
| Phase A/B | 21 |
| PDR | 2 |
| CDR | 2 |
| implementation | 17 |
| integration and test | 11 |
| operations | 17 |
| not reported | 0 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 0 |

### Model artifacts, EPS elements, toolchain, and claim evidence

| Model artifact used | Report memberships (n=40; multi-label) |
|---|---|
| requirements diagrams/tables | 28 |
| block definition/internal block diagrams | 29 |
| state/activity/sequence diagrams | 23 |
| parametrics | 29 |
| trade-study models | 16 |
| interface control models | 15 |
| power budgets | 21 |
| FMEA/risk models | 2 |
| test cases/procedures | 8 |
| verification matrices | 4 |
| executable simulations | 21 |
| generated documents | 12 |
| other | 37 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 0 |

| EPS element modeled | Report memberships (n=40; multi-label) |
|---|---|
| solar panels | 25 |
| battery | 25 |
| power conditioning/distribution | 18 |
| loads | 19 |
| modes | 14 |
| margins | 14 |
| power budgets | 23 |
| degradation | 5 |
| fault protection | 4 |
| interfaces | 16 |
| other | 12 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 7 |

The EPS-elements figure states coded coverage 33/40 and statuses not reported=1, not applicable=5, none=1. Its separated neutral bar shows the 7 reports with no selected controlled value; that bar is not an EPS element.

| Interoperability mechanism | Report memberships (n=40; multi-label) |
|---|---|
| model transformation | 9 |
| API | 2 |
| plugin | 6 |
| co-simulation | 3 |
| generated code | 3 |
| import/export | 20 |
| XML/XMI | 6 |
| ReqIF | 0 |
| spreadsheets | 10 |
| scripts | 14 |
| manual synchronization | 3 |
| not reported | 0 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 11 |

| Toolchain limitation | Report memberships (n=40; multi-label) |
|---|---|
| vendor lock-in | 4 |
| manual translation | 4 |
| broken traceability | 1 |
| missing interfaces | 20 |
| scalability issues | 7 |
| licensing/cost | 5 |
| not reported | 0 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 15 |

The toolchain figure gives field-status context: interoperability coded 29/40, not-reported status 10, uncertain 1; limitations coded 25/40, not-reported status 15. It shows separated neutral no-selected-value bars (11 and 15), not a misleading `not reported` category bar.

| Claim specificity | Claim memberships (n=270) |
|---|---|
| EPS-specific | 17 |
| nanosatellite system-level | 197 |
| generic space-system | 16 |
| generic MBSE | 39 |
| unclear | 1 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 0 |

| Evidence type | Claim memberships (n=270; multi-label) |
|---|---|
| Assertion only / no evidence | 72 |
| Illustrative example or conceptual argument | 175 |
| Single case-study demonstration | 106 |
| Executable model or simulation result | 36 |
| Trade-study or requirements-checking result | 30 |
| Quantitative metric without baseline | 18 |
| Quantitative comparison with baseline or counterfactual | 3 |
| Stakeholder/user/expert evaluation | 6 |
| Reuse/replication across projects | 2 |
| Integration/test/operational/flight evidence | 2 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 0 |

| Baseline/comparator | Claim memberships (n=270) |
|---|---|
| previous document-centric process | 36 |
| manual analysis | 13 |
| alternative toolchain | 2 |
| previous mission | 2 |
| none | 35 |
| not reported | 177 |
| unmapped/invalid controlled value | 5 |
| unassigned/no controlled value | 0 |

| Controlled outcome domain | Claim-domain memberships (n=270 nested claims; domains can overlap) |
|---|---|
| Reliability / mission assurance / risk | 86 |
| Reproducibility / reuse / openness | 87 |
| Integrability / interoperability / lifecycle continuity | 114 |
| Traceability / consistency / requirements quality | 121 |
| Cost / schedule / effort / efficiency / automation | 85 |
| Governance / ROI / project decisions | 10 |
| Decision support / analysis / trade-space / feasibility | 82 |
| Communication / collaboration / knowledge | 59 |
| Generality / scalability / tailoring | 79 |
| Other / uncategorized controlled outcome | 13 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 0 |

### Direct V&V source fields and derived linkage

RQ3 direct controlled fields are reported separately from the derived linkage map. Reports with at least one coded value are 26 for explicitly pre-physical verification mechanisms, 24 for verification/validation artifacts, and 10 for integration/test readiness. Their status coverage is: explicitly pre-physical verification mechanisms, coded=26/40; not reported=9/40; not applicable=2/40; none=3/40; uncertain=0/40; unassigned/no explicit status=0/40; verification/validation artifacts, coded=24/40; not reported=9/40; not applicable=2/40; none=4/40; uncertain=1/40; unassigned/no explicit status=0/40; integration/test readiness, coded=10/40; not reported=29/40; not applicable=1/40; none=0/40; uncertain=0/40; unassigned/no explicit status=0/40.

| Pre-physical verification mechanism | Report memberships (n=40; multi-label) |
|---|---|
| requirements-in-the-loop | 17 |
| simulation-in-the-loop | 15 |
| parametric checks | 19 |
| model checking | 0 |
| trade-study verification | 15 |
| virtual integration | 10 |
| not reported | 0 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 14 |

| Verification/validation artifact | Report memberships (n=40; multi-label) |
|---|---|
| verification matrix | 4 |
| test cases | 5 |
| test procedures | 6 |
| simulation scenarios | 15 |
| acceptance criteria | 10 |
| executable checks | 14 |
| generated test artifacts | 0 |
| SIL/HIL links | 2 |
| automated tests | 1 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 16 |

| Integration/test readiness | Report memberships (n=40; multi-label) |
|---|---|
| links to hardware integration | 6 |
| software integration | 8 |
| flat-sat/testbed | 0 |
| environmental test | 0 |
| operational validation | 4 |
| not reported | 0 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 30 |

Derived V&V linkage categories are a mixed-source union of coded values across verification/validation artifacts, explicitly pre-physical verification mechanisms, and integration/test readiness. The generic/planned fallback additionally uses controlled RQ3 relevance when no coded artifact or pre-physical mechanism is selected. The map is not a direct pre-physical-only measure: only the mechanism source field is explicitly pre-physical. A readiness link denotes readiness, not completed integration/test closure.

| Derived V&V linkage category | Derived report memberships (n=40; categories can overlap) |
|---|---|
| Requirements-to-model traceability or verification matrix | 19 |
| Executable simulation or scenario analysis | 22 |
| Parametric/budget/constraint checks | 23 |
| Test cases/procedures/V&V activity packages | 21 |
| External tool or data-flow coupling for V&V | 11 |
| Physical/SIL/HIL/integration-test readiness link | 10 |
| EPS/power-relevant V&V artifact/mechanism co-reporting | 25 |
| No coded V&V artifact or pre-physical mechanism | 12 |
| Generic/planned V&V linkage only | 3 |

### IVV and governance/ROI

| IVV integration level | Report memberships (n=40) |
|---|---|
| none/not reported | 10 |
| separate document only | 1 |
| verification matrix adjacent to model | 0 |
| trace-linked verification artifacts | 5 |
| model-contained verification artifacts | 2 |
| executable/model-based checks | 6 |
| simulation-in-the-loop | 12 |
| software/hardware-in-the-loop | 1 |
| physical integration/test only | 0 |
| unmapped/invalid controlled value | 0 |
| unassigned/no controlled value | 3 |

`none/not reported` is a controlled IVV level (10 reports), distinct from the three reports with no selected IVV level.

| Separate controlled measure | Category | Report memberships (n=40) |
|---|---|---|
| model governance strategy | ownership | 10 |
| model governance strategy | configuration/change control | 7 |
| model governance strategy | review process | 11 |
| model governance strategy | model quality criteria | 9 |
| model governance strategy | naming/versioning conventions | 5 |
| model governance strategy | not reported | 0 |
| model governance strategy | unmapped/invalid controlled value | 0 |
| model governance strategy | unassigned/no controlled value | 23 |
| ROI/value-realization evidence | cost of MBSE adoption | 0 |
| ROI/value-realization evidence | training/tooling effort | 0 |
| ROI/value-realization evidence | saved effort | 2 |
| ROI/value-realization evidence | schedule effect | 2 |
| ROI/value-realization evidence | avoided rework | 1 |
| ROI/value-realization evidence | reuse value | 1 |
| ROI/value-realization evidence | decision quality | 3 |
| ROI/value-realization evidence | mission assurance benefit | 0 |
| ROI/value-realization evidence | not reported | 0 |
| ROI/value-realization evidence | unmapped/invalid controlled value | 0 |
| ROI/value-realization evidence | unassigned/no controlled value | 35 |
| governance gap classification (all-study mapping) | addressed with evidence | 7 |
| governance gap classification (all-study mapping) | addressed conceptually | 20 |
| governance gap classification (all-study mapping) | mentioned only | 13 |
| governance gap classification (all-study mapping) | not addressed | 0 |
| governance gap classification (all-study mapping) | unmapped/invalid controlled value | 0 |
| governance gap classification (all-study mapping) | unassigned/no controlled value | 0 |

The governance/ROI table deliberately does not derive project-decision counts from claim prose or outcome categories. It separately reports the model-governance field, ROI/value-realization field, and existing all-study governance gap classification.

## Field coverage and unassigned values

Status entries are n/N records for the named field. `Unassigned value` means that the record contains no selected controlled label; it is distinct from an explicit `not reported`, `none`, `not applicable`, or `uncertain` status.

| Field | Unit | coded | not reported | not applicable | none | uncertain | unassigned status | unassigned value |
|---|---|---|---|---|---|---|---|---|
| Lifecycle stage addressed | report N=40 | 40/40 | 0/40 | 0/40 | 0/40 | 0/40 | 0/40 | 0/40 |
| Development context | report N=40 | 38/40 | 2/40 | 0/40 | 0/40 | 0/40 | 0/40 | 2/40 |
| Model maturity | report N=40 | 40/40 | 0/40 | 0/40 | 0/40 | 0/40 | 0/40 | 0/40 |
| Model artifacts used | report N=40 | 40/40 | 0/40 | 0/40 | 0/40 | 0/40 | 0/40 | 0/40 |
| EPS elements modeled | report N=40 | 33/40 | 1/40 | 5/40 | 1/40 | 0/40 | 0/40 | 7/40 |
| Interoperability mechanisms | report N=40 | 29/40 | 10/40 | 0/40 | 0/40 | 1/40 | 0/40 | 11/40 |
| Toolchain limitations | report N=40 | 25/40 | 15/40 | 0/40 | 0/40 | 0/40 | 0/40 | 15/40 |
| Verification/validation artifacts | report N=40 | 24/40 | 9/40 | 2/40 | 4/40 | 1/40 | 0/40 | 16/40 |
| Pre-physical verification mechanism | report N=40 | 26/40 | 9/40 | 2/40 | 3/40 | 0/40 | 0/40 | 14/40 |
| Integration/test readiness | report N=40 | 10/40 | 29/40 | 1/40 | 0/40 | 0/40 | 0/40 | 30/40 |
| IVV integration level | report N=40 | 27/40 | 7/40 | 2/40 | 4/40 | 0/40 | 0/40 | 3/40 |
| Model governance strategy | report N=40 | 17/40 | 23/40 | 0/40 | 0/40 | 0/40 | 0/40 | 23/40 |
| ROI/value-realization evidence | report N=40 | 5/40 | 35/40 | 0/40 | 0/40 | 0/40 | 0/40 | 35/40 |
| Claim specificity | claim N=270 | 270/270 | 0/270 | 0/270 | 0/270 | 0/270 | 0/270 | 0/270 |
| Evidence type | claim N=270 | 270/270 | 0/270 | 0/270 | 0/270 | 0/270 | 0/270 | 0/270 |
| Baseline comparator | claim N=270 | 248/270 | 22/270 | 0/270 | 0/270 | 0/270 | 0/270 | 0/270 |

## PRISMA flow

The PRISMA figure is rendered from parsed flow counts, not copied from another figure: raw records=199; duplicates removed=118; screened=81; excluded=37; reports sought=44; not retrieved=4; reports included=40.

## Assumptions

- Outcome-domain synthesis uses the declared exact-code mapping only; a controlled `generality/reuse` code can contribute to both reuse and generality domains, while uncontrolled outcome text cannot create a domain membership.
- In the claim-anatomy figure, `comparator recorded` groups only the four exact baseline codes `previous document-centric process`, `manual analysis`, `alternative toolchain`, and `previous mission`. `none`, `not reported`, unmapped/invalid, and unassigned remain separate.
- Matrix cells are report or claim memberships, as stated in each CSV; multi-label fields can make matrix totals exceed the number of reports or claims. The maturity × EPS and lifecycle × IVV displays are cross-classifications only / not progression or direct linkage.

## Controlled-code and QA safeguards

- `extraction_codebook.json` is loaded at runtime. The generator validates codebook version 1.1, exact extraction-ID coverage, structured-summary field coverage, exact controlled labels, statuses, and applicable single-/multi-select cardinality.
- Canonical claim fields normalize typed wrappers and the documented aliases `outcome_category|category`, `specificity_of_claim|specificity`, `mbse_mechanism|mechanism`, and `evidence_confidence_rating|evidence_confidence`. Stable claim references use `corpus_id:claim_id`, with an `id` alias or a 1-based index only when needed.
- The five non-codebook baseline strings in `paper-0007` are retained as `unmapped/invalid controlled value` (n=5); they are not mapped to `none` or `not reported`. The same explicit QA class captures the one invalid claim-level MBSE mechanism value.
- `field_coverage_status.csv` includes status and selected-value coverage for every codebook field at the structured-summary level and, for canonical claim fields, at the claim-record level. It also records unmapped/invalid and unassigned classes.
- Derived V&V linkage categories use only values whose source field has status `coded`; a non-coded selected value, including the allowed `not reported` literal, cannot create a derived V&V membership. The derived map mixes verification/validation-artifact, explicitly pre-physical-mechanism, and integration/test-readiness fields; it does not make every category directly pre-physical, and readiness is not completed integration/test closure.

## Interpretation limits

- All synthesis aggregates use controlled codes only. Claim text, quotations, open coding, and emergent observations are displayed only as audit context where applicable and never classify a count.
- Multi-label co-reporting is not causal linkage. Lifecycle × IVV cells do not establish a developmental progression or direct linkage, and EPS-element × V&V-artifact cells do not establish element-level V&V relationships.
- Report counts should not be interpreted as independent implementation counts; recurring reference-model lineages can represent related publications. The retained lineage graphic is a selected evidence map (n=19), not an all-corpus aggregate or a derivation chain; title-derived labels aid reading while corpus IDs remain in the CSV for audit, and outlines mean executable/model-based checks or simulation-in-the-loop.
- Missing, none, not-reported, not-applicable, uncertain, and unassigned statuses are retained rather than filled from prose. The analysis performs no paper recoding.
