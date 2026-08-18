# Protocol for a Systematic Review of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems

- **Working branch:** `slr1-1.1-restart`
- **Common evidence cutoff:** <replace this with the date when searches were run, once they're run>

> **Protocol parts:** **1 — Scope and definitions** (this file) · [2 — Discovery and appraisal](protocol-discovery-and-appraisal.md) · [3 — Extraction and synthesis](protocol-extraction-and-synthesis.md)

## Review status and restart policy

This protocol defines a **new systematic review run** (branch `slr1-1.1-restart`) focused on nanosatellite electrical power system (EPS) MBSE. It is not an amendment to, or an update of, the earlier whole-nanosatellite/EPS review (`main` branch).

The earlier searches, screening decisions, corpus, extractions, codebook, synthesis, and manuscript are treated as legacy or pilot artifacts. A failed earlier attempt was abandoned and its search outputs were removed; it supplies no discovery events, records, decisions, or evidence to this run. In particular:

- no previously identified report is automatically included;
- all records must be found through a search documented in the current query plan or through a citation-chasing route and screened against this protocol;
- `markdown/` and `pdfs/` were retained only as a source-file cache outside the search evidence base;
- previous reports may be used only as known-item recall checks when refining the search;
- every included report must be newly extracted from its full text against a new run-specific codebook; prior extraction may be consulted only during a later discrepancy audit and may not supply new-run evidence;
- prior counts and classifications must not be carried into the new synthesis;

## Reporting framework

PRISMA-P (2015) guides this protocol; PRISMA-S (2021) guides the design, execution, preservation, and reporting of every search in [`query-search-plan.md`](query-search-plan.md); and PRISMA 2020 will guide the completed review, abstract, checklist, and flow diagram. These are reporting guidelines, not evidence-validity instruments. Health-review terminology is adapted to this engineering evidence map without inventing clinical effect measures, risk-of-bias tools, or GRADE ratings.

This is a new review, not an update. The completed review will use the PRISMA 2020 flow template for a new systematic review using databases and other sources. Identification and selection are counted at record/report level; report families, EPS threads, reusable-artifact lineages, tailoring applications, outcome/burden records, and V&V records are linked analytic units reported with separate denominators.

Official guidance to use at the applicable stage:

- [PRISMA-P protocols and checklist](https://www.prisma-statement.org/protocols);
- [PRISMA-S search reporting](https://www.prisma-statement.org/prisma-search) and [Rethlefsen et al. (2021)](https://doi.org/10.1186/s13643-020-01542-z); and
- [PRISMA 2020 statement](https://www.prisma-statement.org/prisma-2020-statement), [checklist](https://www.prisma-statement.org/prisma-2020-checklist), [abstract guidance](https://www.prisma-statement.org/abstracts), and [flow templates](https://www.prisma-statement.org/prisma-2020-flow-diagram).

Registration/contact declarations, contributor and guarantor details, and funding/sponsor and competing-interest declarations are intentionally deferred at this stage. Their absence must be stated accurately; this protocol is not represented as administratively PRISMA-P-complete.

## Review objective

To synthesize how nanosatellite EPSs are represented through MBSE, why those models are constructed, which inputs and assumptions they depend on, how they are reused or tailored, what bounded genericity is specified or demonstrated for identifiable EPS-linked artifacts, which beneficial, null, mixed, or adverse EPS-linked outcomes and implementation burdens are reported, and how EPS verification and validation (V&V) are integrated before physical integration or test.

For reusable artifacts, the review will map the declared applicability envelope, reusable core, variation points, tailoring pathway and footprint, demonstrated target contexts, post-tailoring assurance, dependence, and genericity evidence tier. It will not certify context-free, universal, or “true” genericity.

The analytic scope includes both:

1. **EPS-primary MBSE**, where the EPS is the principal modeled system or viewpoint; and
2. **embedded EPS model threads**, where a broader nanosatellite model contains an explicit, extractable chain linking EPS content to systems-engineering artifacts or activities.

Generic whole-spacecraft MBSE evidence does not answer the research questions merely because EPS and another artifact occur in the same report.

## PICOC

| Population | Intervention | Comparison | Outcome | Context | Related RQ(s) |
|---|---|---|---|---|---|
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-primary MBSE or an explicit embedded EPS model thread | Not required | EPS representation, model purpose, required inputs and assumptions, abstraction, artifact identity/lineage, declared applicability envelope, reusable core, variation points, tailoring and its footprint, demonstrated coverage and assurance, bounded-genericity evidence tier, and required roles/resources | Nanosatellite systems engineering across the lifecycle | RQ1, including RQ1-G |
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-linked MBSE artifacts, analyses, and model-enabled activities | When reported: document-centric practice, manual analysis, alternative toolchain, previous mission/model, or other explicit comparator | Beneficial, null, mixed, or adverse EPS-linked technical and engineering-process outcomes and implementation burdens, especially reliability/mission assurance, reproducibility/reuse, and integrability/interoperability | Nanosatellite development and decision making | RQ2 |
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-specific or system-wide EPS-linked model-based V&V before physical integration or test | Separate or document-based V&V, manual checking, another method, or no comparator when reported | V&V scope and object, traceability to V&V artifacts, executable checks, verdicts, virtual integration, and model-to-test continuity | Pre-physical analysis and V&V, with downstream physical links recorded separately | RQ3 |

## Research questions

1. **RQ1 — representation, purpose, and prerequisites.** How are nanosatellite EPSs represented in EPS-primary MBSE models and embedded EPS model threads; for what stated purposes; what inputs, assumptions, abstraction choices, roles, skills, and resources are reported; and how are the models reused or tailored?

   **RQ1-G — bounded reuse and tailoring.** For each eligible EPS model thread, what, if any, reusable EPS MBSE artifact and artifact lineage is reported; what declared applicability envelope, reusable core, variation points, dependencies, and tailoring pathway does it have; which materially distinct target-context applications and post-tailoring assurances are reported; and at what non-compensatory evidence tier is bounded reuse supported?

2. **RQ2 — EPS-linked outcomes, burdens, and evidence.** Which beneficial, null, mixed, or adverse EPS-specific technical or engineering-process outcomes, and which implementation burdens, are explicitly attributed to EPS MBSE artifacts or model-enabled activities; through what mechanisms; and with what supporting evidence?

3. **RQ3 — EPS-linked pre-physical V&V.** How are EPS-specific or system-wide EPS-linked pre-physical V&V activities connected to EPS requirements, model elements, analyses, or interfaces; what is the object of verification or validation; and what level of preparation, execution, result reporting, and model-to-test continuity is demonstrated?

RQ1–RQ3 are co-primary mapping questions. RQ1-G is a prespecified analytic stratum nested within RQ1, not a fourth eligibility question: an eligible report need not claim genericity or report reuse. Within RQ2, reliability/mission assurance, reproducibility/reuse, and integrability/interoperability are prespecified priority presentation strata, not eligibility filters; the open outcome/burden set is coded and reported direction-neutrally without post-hoc suppression of other domains.

## Operational definitions

### Nanosatellite population

An eligible platform is an actual or intended orbital spacecraft that the source identifies as a CubeSat or nanosatellite, including recognized CubeSat form factors even when a particular implementation falls outside a strict 1--10 kg mass definition. A reference, template, or early-phase design model may qualify without a named or realized mission when its stated target population is orbital CubeSat/nanosatellite development.

`SmallSat` and “small satellite” are not treated as synonyms for the eligible population. A generic SmallSat/small-satellite label alone does not establish CubeSat/nanosatellite-class eligibility, even when the report may be relevant to broader small-spacecraft engineering.

Exclude:

- CanSats and other non-orbital educational demonstrators;
- PocketQube/picosatellite-only studies unless a separable CubeSat/nanosatellite case is also reported;
- generic SmallSat/small-satellite studies, larger small satellites, or conventional spacecraft unless the source also identifies a CubeSat/nanosatellite-class case and its results can be extracted separately; and
- mixed-platform evidence when nanosatellite-specific findings cannot be separated.

### EPS boundary

EPS content may include power generation; solar arrays; storage and battery management; conversion, conditioning, regulation, and distribution; protection, monitoring, and control; electrical buses and harnesses; power interfaces; operational modes; load and energy profiles; power/energy budgets and margins; degradation; faults and fault management; and relevant requirements.

Other subsystems are in scope only as explicit EPS loads, interfaces, environmental dependencies, operating-mode drivers, or sources of EPS requirements. Their internal design is not synthesized.

### MBSE qualification

A report need not use the acronym “MBSE,” but it must describe a structured system model used for a systems-engineering purpose and provide extractable evidence of modeled elements and relationships across at least two systems-engineering concerns, such as requirements, functions/behavior, architecture, interfaces, parametrics/analysis, design decisions, or V&V. For report eligibility, those relationships must involve the same EPS entity or thread used to justify inclusion; unrelated report-level MBSE does not qualify otherwise isolated EPS content.

Examples may include SysML, Arcadia/Capella, object-oriented systems models, reference models, or connected digital-engineering environments. A stand-alone circuit model, battery model, SPICE/MATLAB/Simulink simulation, optimization, power-budget spreadsheet, or component-sizing calculation is not MBSE by itself. It qualifies only when its inputs or outputs are explicitly bound, traced, transformed, or otherwise linked to a structured system model.

### Bounded genericity, reusable artifacts, and tailoring

For RQ1-G, **genericity means bounded transferability**: the extent to which the documented core of an identifiable EPS-linked MBSE artifact can be adopted or tailored for stated target contexts within a declared applicability envelope. Genericity is not an intrinsic or context-free property of a paper, diagram, language, tool, repository, workflow, or model merely because it is called generic, reference, standard, template, reusable, configurable, modular, scalable, lightweight, open, or mission-agnostic.

A **reusable EPS MBSE artifact** is a source-identifiable structured-model asset or documented package of assets that contains, or is explicitly bound to, a qualifying EPS thread and its modeled relations. It may be a reference/template model, metamodel or profile carrying EPS semantics, model library or pattern, interface contract, parametric-model package, transformation/generator with persistent model content, or a larger reusable spacecraft model with a separately reconstructable EPS portion. Public availability is recorded but is not required. A reusable method, workflow, toolchain, transformation procedure, or guidance document is coded as **method/workflow reuse** unless persistent EPS model content and its lineage are identified; a specific-mission artifact does not become generic merely because its method might be reused.

An **artifact lineage** links a base artifact and any versions or derived instances for which identity and continuity are source-supported by a name/version, repository or package identifier, explicit derivation, transformation record, shared model identifiers, or a reconstructable retained core. Shared authors, organization, tool, topic, terminology, or diagrams alone are insufficient. Materially changed cores or unresolved identity are kept as separate/uncertain lineages rather than merged.

A **declared applicability envelope (DAE)** is the source-locatable intended scope for reuse: target platform or mission context, intended lifecycle use or decision, EPS/model boundary and abstraction, material dependencies and required inputs, applicable architecture/interface/tool assumptions, and stated exclusions or limits. At minimum for the genericity profile, the source must report the intended target class/context, intended lifecycle use or decision, EPS/model boundary and abstraction, and at least one material condition, dependency, required input, or exclusion. Evidence may be assembled across explicitly linked reports while preserving the provenance of each field, but an observed mission, a broad “for CubeSats” label, or reviewer expertise cannot fill a missing envelope.

A **reusable core** comprises the model elements, relations, constraints, interfaces, semantics, or packaged assets stated or reconstructably shown to persist across applications. A **variation point** is a source-described location, option, range, rule, or dependency by which the core may vary. **Tailoring** is a source-described configuration, parameterization, selection, specialization, extension, deletion/substitution, interface mapping, transformation/generation, or explicitly justified unchanged adoption that produces or selects a target-specific instance. A parameter sweep or scenario run in one unchanged mission model is analysis, not a cross-context tailoring application. Unstructured reconstruction may demonstrate reuse of a method, but it supports artifact reuse only when lineage and retained core are established.

A **tailoring application** is one artifact-lineage-to-target-context application. The artifact's originating development case counts only when the source identifies it as an adoption/configuration of the same reusable core and reports the retained-core/change or justified-as-is evidence; merely being the mission in which the artifact was created does not count as transfer. Its context tuple records the mission/platform, lifecycle purpose, EPS architecture and interfaces, environment/operations, tool/model configuration, relevant envelope dimensions, what core remained, what changed or was intentionally unchanged, rationale, implementation footprint, and result. Two applications are materially distinct only when they differ on at least one DAE dimension that exercises or tests the claimed reuse; two reports, scenarios, revisions, or names for the same underlying implementation are not distinct applications.

**Demonstrated coverage** is the subset of the DAE represented by reported tailoring applications. It is never assumed to equal the claimed envelope. **Post-tailoring assurance** requires an identifiable tailored configuration, an intended-use-relevant criterion or oracle, an executed check after tailoring, and a reported result or verdict. A syntax, import, or build check alone is insufficient unless that is itself the stated intended use. Assurance may cross-link to RQ3, but it becomes a direct RQ3 V&V record only when the existing EPS target–model-to-V&V bridge–method/intent rule is also met; validation of a base model does not transfer automatically to a derived instance.

Every eligible EPS thread receives an RQ1-G disposition of `not_an_artifact_or_method_only`, `artifact_no_reuse_indication`, `genericity_or_reuse_claim`, `reported_reuse_without_bounded_specification`, `bounded_reuse_candidate`, or `unclear`. Where an EPS-linked artifact is identifiable, the following non-compensatory profile is coded at artifact-lineage/version/scope level; method/workflow-only cases receive `NA` without inventing an artifact lineage. The letters are local profile labels, not the Population block used in searching:

| Gate | Minimum source-supported evidence |
|---|---|
| **A — artifact/lineage** | Identifiable EPS-relevant artifact and source-locatable lineage across any claimed instances. |
| **E — envelope** | Minimum DAE, with each component and source location retained. |
| **C — core and variation design** | Identified reusable core plus variation points, tailoring rules, and prerequisites; alternatively, an explicit bounded reuse-as-is rule. |
| **T — transfer/tailoring** | Actual target-context applications with the retained core, changes or justified unchanged adoption, and rationale reported; credited contexts must be materially distinct. |
| **P — post-tailoring assurance** | For every context credited toward demonstrated reuse, an intended-use-relevant criterion, executed post-tailoring check, and result/verdict. |
| **I — independent transfer** | At least one credited context is separately adopted or tailored and post-tailoring assured by an adopter team independent of the artifact's originating implementation family, with the adoption and result corroborated in a report, artifact, or data record attributable to that independent adopter/evaluator rather than only asserted by the originator. An external organization/team normally qualifies when lineage continuity is established; a same-organization separate team qualifies only when the source supports separate implementation control, no material participation by the originating implementation team, and a distinct assured application. Independent review of the originator's unchanged instance, disjoint author lists, companion reports, a shared underlying implementation, and unclear relationships do not qualify. |

Code each gate as `demonstrated`, `partial`, `not_reported`, `uncertain`, `none`, or narrowly justified `not_applicable`, with source locations and confidence. **Only `demonstrated` satisfies a gate required by a tier.** `not_applicable` may describe a gate not required at the assigned lower tier but never substitutes for a required gate; `none` means the source affirmatively indicates that the condition was absent or failed, whereas `not_reported` means it cannot be assessed. `partial`, `not_reported`, `uncertain`, `none`, `not_applicable`, and reviewer-inference-only evidence fail a required gate but—apart from source-supported `none`—are not evidence that the underlying capability is absent. Explicit unchanged adoption may satisfy T only when its conditions, target context, retained core, and rationale are reported; it never waives E, C, or P.

Assign the highest cumulative **genericity evidence tier** supported:

| Tier | Minimum conditions | Interpretation |
|---|---|---|
| **`NA`** | No identifiable EPS model artifact, or method/workflow reuse only | Artifact genericity is not rated; method/workflow reuse remains in RQ1. |
| **`G0_artifact_only`** | An EPS-linked artifact is identified, but no genericity/reuse claim or application is reported | No genericity evidence reported; not evidence of non-reusability. |
| **`G1_claimed_or_unbounded`** | A is supported and the source makes a genericity/reuse claim or reports a traceable but unbounded reuse indication | Claim or indication only; bounded reuse is not established. |
| **`G2_bounded_reuse_specified`** | A ∧ E ∧ C | Prospective bounded reuse is specified; actual transfer need not have been demonstrated. |
| **`G3_bounded_reuse_demonstrated`** | G2 ∧ T for at least two materially distinct target contexts ∧ P for every credited context | Bounded reuse is demonstrated, potentially within one dependent implementation family. |
| **`G4_independently_corroborated`** | G3 ∧ I, with the independent application itself meeting T and P | Bounded transfer is independently adopted and assured, still only for the demonstrated subset of the DAE. |

The cumulative caps are explicit: missing A yields `NA`; A without E∧C cannot exceed G1; one assured application, multiple unassured applications, the uninstantiated originating development case, or repeated reports of one application cannot exceed G2; two materially distinct assured applications of the reusable core can reach G3; and only an independently adopted/tailored, independently corroborated, and assured credited application can reach G4. A wider claimed envelope, a larger model, more parameters, public artifact availability, a higher report-quality score, or strength on another gate cannot compensate for a missing gate or produce a higher tier. Tiers are ordinal evidence classes, not numeric scores, model-quality rankings, maturity levels, benefit measures, prevalence estimates, or guarantees of suitability for untested contexts. Assign one highest tier only after checking every lower-tier prerequisite; retain the gate vector alongside it so artifacts tied at a tier are not implied to be equivalent. Claim concordance (`not_evaluated`, `supported_in_tested_contexts`, `partially_supported`, `mixed`, `not_supported`, or `unclear`) and envelope breadth are reported separately. Failed tailoring, out-of-envelope applications, burdens, and contradictory evidence are retained rather than netted into the tier.

The phrase **generic whole-spacecraft MBSE** in the exclusion rule means whole-spacecraft evidence with no qualifying EPS thread; it is not a judgment about the model's genericity. A whole-spacecraft reusable artifact may receive an RQ1-G profile only for its EPS-linked content and only after normal Route A/B eligibility is established. Genericity status and tier never determine report eligibility.

### Eligible EPS evidence routes

A full-text report is assigned one of two mutually exclusive eligibility routes. Route A takes precedence only when the stated objective, modeled viewpoint/boundary, and substantive method or results center on EPS. Otherwise, a qualifying report is Route B. A report may contain multiple EPS threads, but its report-level route remains fixed.

- **Route A — EPS-primary MBSE:** the EPS, electrical-power viewpoint, or a defined EPS function/architecture is the principal modeled boundary, and the report provides an identifiable EPS model artifact plus at least one explicit relation involving that EPS content and a second systems-engineering concern.
- **Route B — embedded EPS model thread:** a broader nanosatellite MBSE report contains at least one qualifying EPS thread meeting all three conditions below.

A qualifying embedded EPS model thread requires:

1. an **EPS anchor**: a named EPS requirement, function, behavior, component, interface, mode, load/profile, budget, parameter, constraint, or hazard;
2. a **model anchor**: an identifiable representation of that EPS content in a structured system-model artifact or explicitly connected analysis model; and
3. an **explicit bridge**: a reported, source-locatable relation connecting the EPS anchor to a second concern such as a requirement, behavior, architecture/interface, analysis, decision, output, or V&V artifact. Eligible bridges include allocation, trace, satisfy/refine/verify relations, interface/flow, parametric binding, transformation, and data mapping.

Containment in a generic spacecraft breakdown, an EPS label, or an equipment-list entry may establish where an anchor appears but is not a sufficient bridge by itself. The source need not name a formal relation type, but the relation's endpoints and meaning must be reconstructable. The anchors and bridge must be supported by text, a figure/table, a model extract, a trace record, or another locatable source. Keyword presence, reviewer inference, or report-level co-occurrence is insufficient.

### MBSE-enabled outcomes and implementation burdens versus EPS engineering outputs

An **EPS engineering/model output** is a result such as minimum state of charge, power margin, battery capacity, solar-array area, voltage/current, energy balance, or a selected architecture. Such outputs are extracted for RQ1 and may support RQ2 or RQ3, but they are not automatically evidence of MBSE value.

An **RQ2-eligible outcome or implementation-burden record** must provide:

1. an eligible EPS model thread or named EPS-linked model artifact/activity;
2. a reported beneficial, null, mixed, or adverse technical or engineering-process outcome, or an implementation burden, explicitly attributed to that EPS artifact/activity rather than to an EPS technology choice; and
3. extractable result or claim wording and the evidence, if any, offered for it.

The proposed model-enabled mechanism is extracted when stated and coded `not_reported` when absent; missing mechanism reporting lowers interpretability but does not erase an otherwise explicit EPS-attributed record. A generic claim about MBSE in a report containing EPS material is not EPS-specific evidence. Assertion-only claims may be retained but must be classified as unsupported rather than as demonstrated effects.

A null outcome requires an evaluated result indicating no observed effect or difference; it is not synonymous with `not_reported`, missing evidence, or absence of a claim. Split separable benefits, adverse effects, null findings, and burdens into atomic records. Use `mixed/conditional` only when direction varies inseparably by scenario, metric, actor, or condition. An implementation burden may coexist with a beneficial outcome and must not be netted against it by reviewer inference. Generic project- or report-level MBSE burdens may be retained as RQ1 context, but they enter direct RQ2 synthesis only when explicitly attributed to the qualifying EPS thread.

A power or energy margin alone is not an EPS-reliability result. Reliability coding requires an explicit connection to failure, fault tolerance, availability, risk, assurance, or another defined reliability construct. Reproducibility/reuse and integrability/interoperability claims must likewise be kept distinct from mere model availability or diagram co-occurrence.

### Direct EPS-linked pre-physical V&V

An **EPS-linked RQ3 V&V record** requires:

1. an **EPS target**: a named EPS requirement, model element, parameter, mode, interface, behavior, function, or hazard, or a system-wide target explicitly decomposed, allocated, or traced to such EPS content;
2. an **explicit model-to-V&V bridge**: a trace, shared identifier, binding, port/data mapping, transformation, generated artifact, allocation, or other reported link; and
3. a **V&V method, intent, or artifact**: the source presents the activity as verification, validation, compliance/requirement checking, virtual integration, a model-derived test activity, or another V&V function.

Classify each candidate record independently by **linkage scope**:

- **`eps_specific`:** the V&V target and activity are explicitly EPS-specific;
- **`system_wide_eps_linked`:** a broader system-level activity contains a named, reconstructable EPS target and bridge;
- **`system_wide_cooccurrence`:** system-wide V&V and EPS content occur in the same report without the required direct link; or
- **`unclear`:** the scope cannot be resolved from the report.

Both `eps_specific` and `system_wide_eps_linked` records may enter direct RQ3 synthesis, but they are always reported separately and the scope of any result or verdict is retained. `system_wide_cooccurrence` is a near miss and cannot support an EPS-specific conclusion.

Classify the **object of V&V** separately from scope and execution environment:

- **model verification:** whether a model, transformation, or executable representation was implemented correctly against its specification or formulation;
- **model validation:** whether a model is adequate or credible for its stated intended use against an authoritative reference, data, or expected behavior;
- **system/design verification:** whether the EPS or wider system design satisfies specified requirements or criteria;
- **system/design validation:** whether the design supports intended stakeholder, operational, or mission needs;
- **multiple:** more than one of these objects is explicitly demonstrated; or
- **unclear.**

Preserve the source's terminology separately from the reviewer's normalized code and rationale. Executing a method in a model does not automatically make the activity model verification or model validation; for example, a virtual requirement check may be system/design verification. MIL, SIL, PIL, HIL, virtual testbeds, and other execution environments are likewise coded separately from the object of V&V.

Criterion, execution, and result completeness are then stratified rather than used to suppress an otherwise explicit linked record:

- **EPS-linked V&V:** the target, bridge, and V&V method/intent/artifact are reported;
- **criterion-complete EPS-linked V&V:** the record additionally reports a requirement, threshold, expected behavior, formal property, acceptance criterion, or pass/fail oracle;
- **executed pre-physical V&V:** the linked method is executed before physical integration or test of the target EPS and a result or verdict is reported; and
- **model-to-test continuity/closure:** a downstream physical artifact or activity is linked, with closure reserved for reported comparison and disposition of results.

A simulation or trade study with no stated V&V/checking intent and no criterion is analysis rather than V&V. A source-claimed verification activity with an unreported criterion remains an EPS-linked record but is not criterion-complete. Generic system V&V and EPS content appearing in the same report without an explicit bridge are co-occurrence only and do not answer RQ3.

For this review, **pre-physical V&V** means a model-based V&V artifact or activity prepared or executed before physical integration or physical testing of the target EPS design. Model-derived preparation for a later physical test is included as preparation. MIL and SIL may qualify when the target EPS hardware remains virtual. PIL and HIL are classified by the hardware actually present: they are not counted as wholly pre-physical when target EPS hardware participates, but representative or non-target hardware does not by itself convert a still-virtual target EPS into a physical EPS test. Bench, environmental, integration, operational, and flight evidence are recorded as downstream model-to-test continuity. When timing or target-relative physicality is unclear, it is coded uncertain and is not counted as demonstrated pre-physical execution.

---

**Next:** [Part 2 — Discovery and appraisal](protocol-discovery-and-appraisal.md)
