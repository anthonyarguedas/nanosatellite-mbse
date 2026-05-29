# Review Protocol

## PICOC

| Population | Intervention | Comparison | Outcome | Context | Related Research Question(s) |
|--|--|--|--|--|--|
| Nanosatellite missions | MBSE | | Generality | | 1 |
| Electrical Power System (EPS) for nanosatellite missions | MBSE | | Generality | | 1 |
| EPS for nanosatellite missions | MBSE | | Reliability, reproducibility and integrability | | 2 |
| EPS for nanosatellite missions | Verification procedure modeling using MBSE | | | | 3 |

## Research questions

1. How can nanosatellite missions and EPS be modeled in a general manner with minimal knowledge about their behavior?

2. What are the claimed outcomes related to reliability, reproducibility, and integrability derived from EPS modeling in nanosatellite missions?

3. How have verification procedures been integrated into EPS models prior to physical development?

## Databases to search
- Scopus
- IEEE Xplore

## Inclusion/Exclusion criteria

| Criterion | Applicable to Question(s) |
|--|--|
| Time range: 2013-2026 | 1-3 |
| Language: English | 1-3 |
| Conference and journal papers only | 1-3 |
| Either open access or available in TEC libraries | 1-3 |
| Nanosatellite-class missions only, not larger, not smaller (CanSat) | 1-3 |
| System-level or EPS MBSE model, not other subsystem-level or non-MBSE model | 1 |
| MBSE models only | 2 |
| The outcomes must be attributed to MBSE, not to the EPS technology choices | 2 |
| Must present an integration, verification, and validation (IVV) model using MBSE | 3 |

## Quality checklist

All questions use the scale:
- No = 0
- Insufficiently = 0.5
- Yes = 1

Quality scores are used for sensitivity and confidence in synthesis, not as automatic exclusion thresholds.

- Was the research published in a credible venue?
- Do the researchers discuss limitations, threats to validity, assumptions, or scope boundaries?
- Is the nanosatellite/CubeSat mission context and lifecycle stage described clearly enough to interpret applicability?
- Are the MBSE method, language, toolchain, model artifacts, and system boundary described clearly enough to support replication or comparison?
- Are claimed outcomes explicitly linked to MBSE artifacts, MBSE activities, or model-enabled process changes rather than asserted generically?
- Is evidence provided for claimed outcomes, such as metrics, baseline comparison, case-study results, executable simulation results, model checks, stakeholder evaluation, reuse evidence, integration/test results, or flight/operational data?
- Are requirements, verification, validation, design decisions, or lifecycle gates traced to model artifacts when such traceability is central to the paper?
- Are model availability, open-source assets, reusable packages, data exchange mechanisms, or sufficient implementation details reported to assess reproducibility and toolchain continuity?

## Extraction fields

### Bibliographic and review-management fields

- Corpus ID and extraction file path.
- Tier/status in this review: core, supporting, background, or excluded-after-full-text, with rationale.
- Citation, title, authors, year, venue, DOI/URL, publisher, and venue type.
- Source database/query or citation-chasing route.
- Research question(s) addressed and relevance level for each RQ: none, partial, high.
- Lineage/overlap notes when the paper belongs to a recurring CubeSat reference-model, mission case, or toolchain family.

### Study context and population

- Mission/platform: CubeSat/nanosatellite class, size/form factor, mission name, mission domain, organization type, and project maturity.
- Lifecycle stage addressed: concept/pre-Phase A, Phase A/B, PDR, CDR, implementation, integration and test, operations, or not reported.
- Development context: academic/student, agency, industry/NewSpace, distributed team, agile/concurrent design, rapid prototyping, resource-constrained mission, or not reported.
- EPS relevance: system-level only, EPS-specific, power-budget/electrical-architecture, EPS-adjacent, or not EPS-relevant.
- Model maturity: conceptual framework, reference model/template, prototype demonstration, executable model, project-applied model, validated/operational model, or not reported.

### MBSE objective, scope, and artifacts

- Stated objective/pain point for applying MBSE.
- Modeling scope: mission, system, subsystem, EPS, requirements, architecture, behavior, interfaces, budgets, verification, operations, simulation, manufacturing/test, or other.
- System boundary and level of abstraction, including what is deliberately modeled minimally or excluded.
- Required prior behavioral/domain knowledge and how the method handles limited behavioral knowledge.
- Model artifacts used: requirements diagrams/tables, block definition/internal block diagrams, state/activity/sequence diagrams, parametrics, trade-study models, interface control models, power budgets, FMEA/risk models, test cases/procedures, verification matrices, executable simulations, generated documents, or other.
- Generality/reuse mechanism: template, reference model, profile, library, pattern, transformation, reusable workflow, open package, method guidance, high-level abstraction, mission-agnostic architecture, interface-focused model, low-dynamics / non-detailed-behavior model, or specific-mission model with reusable method only.

### Implementation pathway and tailoring

- MBSE implementation steps or phases reported by the paper.
- Inputs, outputs, actors/roles, prerequisites, completion criteria, and handoffs for each reported step, if available.
- Mapping of MBSE activities to systems-engineering activities and lifecycle gates such as SRR, PDR, CDR, integration, test, or operations.
- Approach classification for tailoring, coded when enough information is available:
  - Pure MBSE: primarily system-model-centered with limited external analysis/tool integration.
  - Enhanced MBSE: system model plus selected analysis/simulation or document-generation support.
  - Extended MBSE: model connected across multiple engineering domains, lifecycle stages, or traceability chains.
  - Integrated MBSE/digital engineering: connected environment spanning modeling, simulation, analysis, verification, and downstream software/hardware/system integration.
- Tailoring rationale: mission scale, team maturity, cost, schedule, risk tolerance, available tools, open-source preference, or organizational constraints.
- Adoption guidance for new users: explicit playbook, partial guidance, implied from case study, or absent.

### Toolchain, interoperability, and lifecycle continuity

- MBSE language/method/tool: SysML, Capella/Arcadia, MATLAB/Simulink, STK, ModelCenter, Cameo/MagicDraw, OpenMBEE, Python, requirements tools, PLM/ALM tools, custom tools, open-source packages, or other.
- Toolchain architecture and data flow between tools.
- Interoperability mechanisms: model transformation, API, plugin, co-simulation, generated code, import/export, XML/XMI, ReqIF, spreadsheets, scripts, manual synchronization, or not reported.
- Evidence of syntax/semantic continuity across lifecycle stages or downstream engineering activities.
- Software/hardware/system integration readiness supported by the toolchain.
- Toolchain limitations: vendor lock-in, manual translation, broken traceability, missing interfaces, scalability issues, licensing/cost, or not reported.
- Availability/reproducibility of tools, models, data, scripts, or packages.

### EPS and verification-specific extraction

- EPS elements modeled: solar panels, battery, power conditioning/distribution, loads, modes, margins, power budgets, degradation, fault protection, interfaces, or other.
- EPS requirements represented and how they are linked to architecture, behavior, analysis, or verification artifacts.
- Integration, verification, and validation (IVV) artifacts: verification matrix, test cases, test procedures, simulation scenarios, acceptance criteria, executable checks, generated test artifacts, SIL/HIL links, or automated tests.
- Pre-physical-development verification mechanism: requirements-in-the-loop, simulation-in-the-loop, parametric checks, model checking, trade-study verification, virtual integration, or not reported.
- IVV integration level: none/not reported, separate document only, verification matrix adjacent to model, trace-linked verification artifacts, model-contained verification artifacts, executable/model-based checks, simulation-in-the-loop, software/hardware-in-the-loop, or physical integration/test only.
- Evidence that verification artifacts are integrated into the EPS/system model rather than documented separately.
- Integration/test readiness: links to hardware integration, software integration, flat-sat/testbed, environmental test, operational validation, or not reported.

### Claimed outcomes, value mechanisms, and evidence

For every claimed MBSE outcome, extract a separate claim-evidence record:

- Claim text or concise paraphrase.
- Outcome category: reliability, reproducibility, integrability/interoperability, generality/reuse, traceability, consistency, completeness, defect/error reduction, cost reduction, schedule reduction, effort reduction, automation, decision support, communication/stakeholder alignment, risk reduction, mission assurance, lifecycle continuity, governance/ROI, or other.
- Reliability subtype, when the outcome category includes reliability or a reliability-adjacent claim: EPS reliability, system/mission reliability, process reliability, model consistency/reliability, mission assurance, defect/error reduction, generic reliability claim, or not applicable.
- Specificity of claim: EPS-specific, nanosatellite system-level, generic space-system, generic MBSE, or unclear.
- MBSE mechanism proposed to create the value: artifact traceability, executable simulation, parametric analysis, reference model reuse, automated generation, model transformation, shared repository, requirements linkage, tool integration, lifecycle gate support, or other.
- Artifact/process linked to the claim.
- Lifecycle stage where the value is claimed to occur.
- Evidence type:
  - Assertion only / no evidence.
  - Illustrative example or conceptual argument.
  - Single case-study demonstration.
  - Executable model or simulation result.
  - Trade-study or requirements-checking result.
  - Quantitative metric without baseline.
  - Quantitative comparison with baseline or counterfactual.
  - Stakeholder/user/expert evaluation.
  - Reuse/replication across projects.
  - Integration/test/operational/flight evidence.
- Metric or value indicator used, if any: time, effort, defects, requirement coverage, trace links, model reuse, integration failures, test coverage, cost, schedule, power margin, reliability proxy, or other.
- Baseline/comparator: previous document-centric process, manual analysis, alternative toolchain, previous mission, none, or not reported.
- Observed effect size or qualitative effect.
- Evidence source: section/page/figure/table and direct quote where possible.
- Evidence confidence rating:
  - Unsupported: claim is asserted without extractable evidence.
  - Weak: plausible explanation or illustrative/single-case evidence without metrics or baseline.
  - Moderate: traceable case evidence, simulation/checking result, or metric, but with limited baseline/independent validation.
  - Strong: quantitative baseline comparison, repeated reuse, independent validation, integration/test evidence, or operational/flight evidence.
- Threats or alternative explanations for the claim.

### Governance, ROI, and project-decision linkage

- Model governance strategy: ownership, configuration/change control, review process, model quality criteria, naming/versioning conventions, or not reported.
- Traceability from model artifacts to project deliverables, milestone decisions, design reviews, assurance cases, or management reports.
- Evaluation criteria used to judge model quality or usefulness.
- ROI/value-realization evidence: cost of MBSE adoption, training/tooling effort, saved effort, schedule effect, avoided rework, reuse value, decision quality, mission assurance benefit, or not reported.
- Programmatic gates or critical design events supported by the model.
- Model-derived performance indicators or management metrics.

### Gap-mapping fields for synthesis

Map each paper to the recent space-MBSE review gaps without treating those gaps as new RQs:

- Does the paper provide a practical implementation pathway for adopters?
- Does the paper address toolchain fragmentation or interoperability?
- Does the paper tailor MBSE to lightweight/resource-constrained nanosatellite missions?
- Does the paper connect MBSE artifacts to governance, project deliverables, or ROI/value evidence?
- Does the paper align MBSE with NewSpace/agile/distributed/rapid-iteration demands?
- For each mapped gap: addressed with evidence, addressed conceptually, mentioned only, or not addressed.

### Synthesis and consistency fields

- Key findings relevant to each RQ.
- Limitations/gaps stated by the authors.
- Extractor-identified limitations/gaps.
- Direct evidence quotes supporting classification decisions and claimed outcomes.
- Notes for consistency with other papers in the same lineage.
- Extraction confidence: high, medium, or low, with reason.
