# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems

- **Working branch:** `slr1-1.1-restart`
- **Common evidence cutoff:** **TBD.** Set one exact calendar date before the first final search and use it unchanged for every source and citation route. **Task:** [`P-001`](TASKS.md).

> **Protocol parts:** **1 — Scope and definitions** (this file) · [2 — Discovery and appraisal](protocol-discovery-and-appraisal.md) · [3 — Extraction and synthesis](protocol-extraction-and-synthesis.md) · [Supporting need assessment — Prior secondary reviews](protocol-prior-secondary-reviews.md)

## Review type and terminology

This work is a **systematic review with an evidence-map synthesis**. Throughout the protocol, *systematic review* names the overall method of identifying, selecting, appraising, and synthesizing evidence; *evidence map* names the structured descriptive output. Do not call the work a *systematic mapping study*: Kitchenham and Charters use that term for broad, high-level classification with deliberately limited extraction, whereas this review performs in-depth extraction and appraisal of linked evidence units.

Use the evidence-unit terms in [Units of evidence and counting](#units-of-evidence-and-counting) rather than using *study* for every object. In particular, a **record** is a search result, a **report** is a document, and a **study or implementation report family** is the source-supported underlying investigation or implementation represented by one or more reports. EPS threads, artifact profiles, tailoring applications, outcome or burden records, and V&V records are analytic evidence units, not additional studies or PRISMA reports.

## Review status and restart policy

This protocol defines a **new systematic review run** on model-based systems engineering (MBSE) for nanosatellite electrical power systems (EPSs). The work is on branch `slr1-1.1-restart`. It is not an amendment to or update of the earlier whole-nanosatellite/EPS review on the `main` branch.

Treat all material from the earlier review as legacy or pilot material. This includes searches, screening decisions, the report set, extractions, the codebook, the synthesis, and the manuscript. An earlier restart attempt failed, and its search results were removed. Nothing from that attempt counts as a search event, record, decision, or item of evidence in this run.

The following rules apply:

- Do not include a report automatically because an earlier review found it.
- Find every main-review primary-evidence record through a search defined in [Part 2](protocol-discovery-and-appraisal.md#search-strategy) or through a recorded citation search. Then screen it under this protocol. Supporting-search records follow their separate [prior-secondary-review protocol](protocol-prior-secondary-reviews.md).
- Use `markdown/` and `pdfs/` only as a cache of source files. They are not part of the search evidence base.
- Use reports found before this run only to check whether the applicable search can find known items.
- Extract every included main-review report again from its full text, using a new codebook made for this run.
- Consult an old extraction only in a later discrepancy audit. Do not copy old evidence into the new extraction.
- Do not carry old counts or classifications into the new synthesis.

Track every unresolved action or deferred field stated in any `protocol*.md` file in [`TASKS.md`](TASKS.md) before committing it. Each task must name the protocol sections to review or update. Mark a task complete only after its outputs exist and those sections have been reconciled.

## Reporting framework

Use the following guidance:

- [PRISMA-P (2015) protocols and checklist](https://www.prisma-statement.org/protocols) for this protocol;
- [PRISMA-S (2021) search reporting](https://www.prisma-statement.org/prisma-search) and [Rethlefsen et al. (2021)](https://doi.org/10.1186/s13643-020-01542-z) to design the strategy in [Part 2](protocol-discovery-and-appraisal.md#search-strategy) and to run, save, and report every search in a search log;
- Kitchenham and Charters (2007), *Guidelines for performing Systematic Literature Reviews in Software Engineering*, as complementary engineering conduct guidance for PICOC framing, heterogeneous evidence, protocol and form piloting, selection and extraction consistency, duplicate-report handling, and descriptive or narrative synthesis; and
- the [PRISMA 2020 statement](https://www.prisma-statement.org/prisma-2020-statement), [checklist](https://www.prisma-statement.org/prisma-2020-checklist), [abstract guidance](https://www.prisma-statement.org/abstracts), and [flow templates](https://www.prisma-statement.org/prisma-2020-flow-diagram) for the completed review.

PRISMA supplies reporting guidance; Kitchenham and Charters supply complementary engineering-review conduct guidance. Neither proves that evidence is valid. This systematic review produces an engineering evidence map, so do not invent clinical effect measures, clinical risk-of-bias tools, or GRADE ratings.

This is a new review, not an update. Use the PRISMA 2020 flow diagram for a new systematic review that uses databases and other sources. Count identification and selection at the record and report level. Other units—report families, EPS threads, reusable-artifact lineages, tailoring applications, outcome or burden records, and verification and validation (V&V) records—are linked units of analysis. Report a separate denominator for each one.

Registration and contact details, contributor and guarantor details, and declarations about funding, sponsors, and competing interests will be completed later. State clearly when any of these details are still absent. Do not claim that this protocol is administratively complete under PRISMA-P. **Task:** [`P-002`](TASKS.md).

## Need for this review

Before the first final primary-evidence search, conduct the bounded [prior-secondary-review search and CRD/DARE assessment](protocol-prior-secondary-reviews.md). This supporting process uses only Scopus and Web of Science Core Collection, has separate records and counts, and is not a tertiary review. It will determine whether an existing review already covers the nanosatellite-EPS population, direct MBSE relationship, and RQ1–RQ3; identify scope, currency, or methodological gaps; and provide the source-located justification for proceeding. Complete tasks [`PR-001`](TASKS.md) and [`PR-002`](TASKS.md) before [`R-002`](TASKS.md).

A prior review, including Buruso et al. (2026), cannot answer RQ1–RQ3 as evidence in this review and cannot insert its included reports into the primary corpus. If the supporting assessment identifies potential redundancy, reconsider and commit the rationale and any affected protocol scope before beginning the main final searches.

## Review objective

The review will map how MBSE represents and supports nanosatellite EPS work, including its purposes, inputs and assumptions, implementation, reuse and tailoring, reported outcomes and burdens, and links to V&V before physical integration or testing. For identifiable reusable artifacts, it will assess only source-supported reuse within stated limits; it will not certify universal or context-free genericity.

The formal questions and analytical dimensions below govern the review. Eligible evidence may be EPS-primary or an embedded EPS model thread, but in either case the source must provide the direct EPS-to-model relationship defined under [eligible EPS evidence routes](#eligible-eps-evidence-routes).

## PICOC

| Population | Intervention | Comparison | Outcome | Context | Related RQ(s) |
|---|---|---|---|---|---|
| EPSs for orbital CubeSat or nanosatellite-class missions | EPS-primary MBSE or a clear embedded EPS model thread | Not required | How the EPS is represented; why the model is used; inputs and assumptions; level of abstraction; artifact identity and lineage; stated range of use; reusable core; variation points; tailoring and its effort; demonstrated uses and checks; evidence tier for bounded reuse; and required roles and resources | Nanosatellite systems engineering throughout the lifecycle | RQ1 |
| EPSs for orbital CubeSat or nanosatellite-class missions | EPS-linked MBSE artifacts, analyses, and model-enabled work | When reported: document-based practice, manual analysis, another toolchain, an earlier mission or model, or another clear comparator | Beneficial, null, mixed, or adverse EPS-linked technical and process outcomes, plus implementation burdens. Priority topics are reliability and mission assurance, reproducibility and reuse, and integration and interoperability | Nanosatellite development and decision-making | RQ2 |
| EPSs for orbital CubeSat or nanosatellite-class missions | EPS-specific or system-wide-but-EPS-linked model-based V&V before physical integration or test | When reported: separate or document-based V&V, manual checking, another method, or no comparator | V&V scope and object, links to V&V artifacts, executable checks, results, virtual integration, and continuity from model to test | Analysis and V&V before physical work, with later physical links recorded separately | RQ3 |

## Research questions

1. **RQ1 — representation, use, and implementation.** How are nanosatellite EPSs represented and used in MBSE approaches, and what inputs, assumptions, implementation needs and footprint, and bounded reuse or tailoring practices are reported? What evidence supports these characterizations?

2. **RQ2 — EPS-linked outcomes and burdens.** What technical or process outcomes and implementation burdens are explicitly attributed to EPS-linked MBSE, and what mechanisms and evidence are reported for those attributions?

3. **RQ3 — EPS-linked pre-physical V&V.** How is EPS-linked MBSE connected to V&V before physical integration or testing, and what evidence is reported for its criteria, execution, results, and model-to-test continuity?

### Prespecified analytical dimensions

- **RQ1:** EPS boundary and representation; purpose and supported decisions; abstraction; material inputs and assumptions; roles, skills, resources, and implementation footprint; and reported reuse or tailoring practices. Artifact identity and lineage; declared applicability envelope; reusable core; variation points and dependencies; tailoring process and effort; materially distinct applications; post-tailoring assurance; the A/E/C/T/P/I evidence profile and resulting tier; and methodological appraisal and claim-specific support for evaluative characterizations.
- **RQ2:** claim kind and scope; outcome or burden category; reported and evidence-supported direction; explicit EPS attribution; mechanism; direct or surrogate measurement; comparator adequacy and confounding when applicable; evaluation design and methodological appraisal; evidence type; and record-level claim support.
- **RQ3:** EPS target and model-to-V&V bridge; linkage scope; V&V object and criterion or oracle; preparation and execution; result or verdict; direct or surrogate measurement; evaluation design and methodological appraisal; claim-specific support; and later model-to-test continuity or closure.

The three mapping areas are equally important. RQ1 is not an additional eligibility test. A report can be eligible without claiming that a model is generic or reusable.

Within RQ2, reliability and mission assurance, reproducibility and reuse, and integration and interoperability are priority categories for presentation. They are not eligibility tests. Code all eligible outcomes and burdens without favoring a direction or hiding other categories after seeing the results.

## Operational definitions

### Nanosatellite population

An eligible platform is an actual or planned orbital spacecraft that the source calls a CubeSat or nanosatellite. Recognized CubeSat form factors are eligible even if a particular spacecraft is outside the strict 1–10 kg nanosatellite range. A reference, template, or early design model can be eligible without a named or built mission if it clearly targets orbital CubeSat or nanosatellite development.

Do not treat `SmallSat` or “small satellite” as a synonym for CubeSat or nanosatellite. That label alone is not enough, even if the report is relevant to wider small-spacecraft engineering.

Exclude:

- CanSats and other educational demonstrators that are not orbital;
- studies only about PocketQubes or picosatellites, unless they also report a separate CubeSat or nanosatellite case;
- generic SmallSat studies, larger small satellites, and conventional spacecraft, unless the source also identifies a CubeSat or nanosatellite-class case and reports its results separately; and
- mixed-platform evidence when the nanosatellite findings cannot be separated.

### EPS boundary

EPS content can include:

- power generation and solar arrays;
- energy storage and battery management;
- conversion, conditioning, regulation, and distribution;
- protection, monitoring, and control;
- electrical buses and harnesses;
- power interfaces;
- operating modes and load or energy profiles;
- power and energy budgets and margins;
- degradation;
- faults and fault management; and
- related requirements.

Include another subsystem only when it is clearly an EPS load, interface, environmental dependency, operating-mode driver, or source of an EPS requirement. Do not synthesize that subsystem's internal design.

### MBSE qualification

A report does not have to use the term “MBSE.” It must, however, describe a structured system model used for a systems-engineering purpose. The report must show modeled elements and explicit relationships across at least two systems-engineering concerns. Examples of concerns are requirements, function or behavior, architecture, interfaces, parametric analysis, design decisions, and V&V.

The relationships must involve the same EPS entity or thread that makes the report eligible. Whole-report MBSE work that is unrelated to isolated EPS content does not qualify that EPS content.

Qualifying approaches may use SysML, Arcadia or Capella, object-oriented system models, reference models, or connected digital-engineering environments. A stand-alone circuit or battery model, SPICE/MATLAB/Simulink simulation, optimization, power-budget spreadsheet, or component-sizing calculation is not MBSE by itself. It qualifies only if the source explicitly binds, traces, transforms, or otherwise connects its inputs or outputs to a structured system model.

### Bounded genericity, reusable artifacts, and tailoring

#### What genericity means in this review

For RQ1, **genericity means bounded transferability**. It asks whether teams can adopt or tailor the documented core of an identifiable EPS-linked MBSE artifact for stated target settings inside a declared range of use.

Genericity is not an unlimited property of a paper, diagram, language, tool, repository, workflow, or model. A label such as *generic*, *reference*, *standard*, *template*, *reusable*, *configurable*, *modular*, *scalable*, *lightweight*, *open*, or *mission-agnostic* is not proof by itself.

#### Reusable artifact and artifact lineage

A **reusable EPS MBSE artifact** is a source-identifiable structured-model asset, or documented package of assets, that contains a qualifying EPS thread or is explicitly connected to one. It can be:

- a reference or template model;
- a metamodel or profile that carries EPS meaning;
- a model library or pattern;
- an interface contract;
- a parametric-model package;
- a transformation or generator with persistent model content; or
- a larger reusable spacecraft model whose EPS part can be reconstructed separately.

Public access is recorded but is not required. Code a reusable method, workflow, toolchain, transformation process, or guidance document as **method/workflow reuse** unless the source identifies persistent EPS model content and its lineage. A mission-specific artifact does not become generic merely because its method could be reused.

An **artifact lineage** connects a base artifact to versions or derived instances. The source must support continuity through evidence such as a name and version, repository or package ID, stated derivation, transformation record, shared model IDs, or a reusable core that can be reconstructed. Shared authors, organizations, tools, topics, terms, or similar diagrams are not enough. Keep artifacts in separate or uncertain lineages when their cores changed materially or their identity is unresolved.

#### Declared applicability envelope

A **declared applicability envelope (DAE)** states where the source says an artifact can be reused. Record:

- the target platform or mission setting;
- the intended lifecycle use or decision;
- the EPS and model boundary and level of abstraction;
- material dependencies and required inputs;
- relevant architecture, interface, and tool assumptions; and
- stated exclusions or limits.

At a minimum, the source must report the target class or setting, the intended lifecycle use or decision, the EPS/model boundary and abstraction, and at least one material condition, dependency, required input, or exclusion.

Evidence can come from explicitly linked reports, but preserve the source for every field. Do not fill a missing envelope from a single observed mission, a broad phrase such as “for CubeSats,” or reviewer knowledge.

#### Reusable core, variation points, and tailoring

A **reusable core** is the set of model elements, relationships, constraints, interfaces, meanings, or packaged assets that the source states or clearly shows remain across uses.

A **variation point** is a source-described place, option, range, rule, or dependency through which that core can vary.

**Tailoring** means using a source-described process to create or select a target-specific instance. It can involve configuration, parameterization, selection, specialization, extension, deletion or substitution, interface mapping, transformation or generation, or a clearly justified decision to use the artifact unchanged.

A parameter sweep or scenario run in one unchanged mission model is analysis, not tailoring across settings. Rebuilding a model without structure may show reuse of a method. It shows reuse of an artifact only when the source establishes the artifact lineage and the retained core.

A **tailoring application** is one use of an artifact lineage in one target setting. The original development mission counts only if the source identifies it as an adoption or configuration of the same reusable core and reports what was kept and changed, or why it was used unchanged. The mission where an artifact happened to be created does not by itself show transfer.

For each application, record:

- mission or platform;
- lifecycle purpose;
- EPS architecture and interfaces;
- environment and operations;
- tool and model configuration;
- other relevant parts of the DAE;
- what stayed the same;
- what changed, or why nothing changed;
- why the choices were made;
- the work and resources required; and
- the result.

Two applications are **materially distinct** only if they differ on at least one DAE dimension in a way that exercises or tests the reuse claim. Two papers, scenarios, revisions, or names for the same implementation do not count as two applications.

#### Demonstrated coverage and post-tailoring assurance

**Demonstrated coverage** is the part of the DAE represented by reported tailoring applications. Never assume that it covers the whole claimed envelope.

**Post-tailoring assurance** requires all four of the following:

1. an identifiable tailored configuration;
2. a criterion or oracle relevant to its intended use;
3. a check run after tailoring; and
4. a reported result or verdict.

A syntax, import, or build check is not enough unless that check is the artifact's stated intended use. An assurance activity can also link to RQ3, but it is a direct RQ3 record only if it separately meets the EPS target–model-to-V&V bridge–method/intent rule. Validation of a base model does not automatically validate a derived instance.

#### RQ1 dispositions and evidence gates

Give every eligible EPS thread one of these RQ1 dispositions:

- `not_an_artifact_or_method_only`;
- `artifact_no_reuse_indication`;
- `genericity_or_reuse_claim`;
- `reported_reuse_without_bounded_specification`;
- `bounded_reuse_candidate`; or
- `unclear`.

When an EPS-linked artifact can be identified, assess the following gates at the artifact-lineage, version, and scope level. Method- or workflow-only cases receive `NA`; do not invent an artifact lineage for them. These gate letters apply only to this profile. They are not the Population block used in the search.

| Gate | Minimum evidence from the source |
|---|---|
| **A — artifact/lineage** | The EPS-relevant artifact is identifiable, and the source provides locatable lineage evidence for any claimed instances. |
| **E — envelope** | The minimum DAE is reported, and the location of each part is recorded. |
| **C — core and variation design** | The reusable core, variation points, tailoring rules, and prerequisites are identified. A clear, bounded rule for reuse without changes is an acceptable alternative. |
| **T — transfer/tailoring** | The source reports actual target-setting applications, what core was retained, what changed or why it stayed unchanged, and why. Any settings credited as separate must be materially distinct. |
| **P — post-tailoring assurance** | Every application credited as demonstrated reuse has an intended-use criterion, a post-tailoring check that was run, and a result or verdict. |
| **I — independent transfer** | At least one credited application was separately adopted or tailored and assured by a team independent of the artifact's original implementation family. A report, artifact, or data record attributable to that independent adopter or evaluator must confirm both the adoption and the result; the originator's claim alone is not enough. An outside organization or team normally qualifies when lineage is established. A separate team in the same organization qualifies only if the source shows separate control of the implementation, no material work by the original implementation team, and a distinct assured application. Independent review of the originator's unchanged instance, different author lists, companion papers, a shared implementation, or an unclear relationship does not qualify. |

Code each gate as one of:

- `demonstrated`;
- `partial`;
- `not_reported`;
- `uncertain`;
- `none`; or
- `not_applicable`, with a narrow justification.

Record a source location and coding confidence for each gate. Only `demonstrated` satisfies a gate required for a tier. `not_applicable` may describe a gate that a lower tier does not require, but it cannot replace a required gate. Use `none` when the source clearly says that a condition was absent or failed. Use `not_reported` when the source does not provide enough information to assess it.

`partial`, `not_reported`, `uncertain`, `none`, `not_applicable`, and evidence based only on reviewer inference all fail a required gate. Except for a source-supported `none`, however, these codes do not prove that the underlying capability is absent. Unchanged adoption can satisfy T only when the source reports its conditions, target setting, retained core, and reason. It never removes the need for E, C, or P.

#### Genericity evidence tiers

Assign the highest cumulative tier that the evidence supports:

| Tier | Minimum conditions | Meaning |
|---|---|---|
| **`NA`** | There is no identifiable EPS model artifact, or only a method or workflow is reused | Do not rate artifact genericity. Keep method or workflow reuse under RQ1. |
| **`G0_artifact_only`** | An EPS-linked artifact is identified, but the source reports no genericity or reuse claim and no application | No genericity evidence was reported. This does not prove that the artifact cannot be reused. |
| **`G1_claimed_or_unbounded`** | A is met, and the source claims genericity or reuse, or reports a traceable but unbounded sign of reuse | This is a claim or indication only. Bounded reuse is not established. |
| **`G2_bounded_reuse_specified`** | A ∧ E ∧ C | The source specifies bounded reuse in advance. It does not have to show actual transfer. |
| **`G3_bounded_reuse_demonstrated`** | G2, plus T for at least two materially distinct target settings, plus P for every credited setting | The source demonstrates bounded reuse. The applications may still belong to one dependent implementation family. |
| **`G4_independently_corroborated`** | G3 plus I, and the independent application itself meets T and P | An independent team adopted or tailored the artifact and checked it. The finding still applies only to the demonstrated part of the DAE. |

Apply these caps exactly:

- Missing A gives `NA`.
- A without both E and C cannot rise above G1.
- One assured application, several unassured applications, an original development case that was not presented as reuse, or repeated reports of one application cannot rise above G2.
- Two materially distinct and assured applications of the reusable core can reach G3.
- G4 requires a credited application that was independently adopted or tailored, independently confirmed, and assured.

A broad claimed envelope, a larger model, more parameters, public access, or strong evidence for another gate cannot make up for a missing gate.

The tiers are ordered evidence classes. They are not numeric scores, model-quality rankings, maturity levels, measures of benefit or prevalence, or promises that an artifact will suit an untested setting. Assign one highest tier only after checking every lower-tier requirement. Keep the gate vector so that two artifacts at the same tier are not assumed to be equal.

Report claim agreement separately as `not_evaluated`, `supported_in_tested_contexts`, `partially_supported`, `mixed`, `not_supported`, or `unclear`. Also report the width of the envelope separately. Keep failed tailoring, uses outside the envelope, burdens, and conflicting evidence; do not average them into the tier.

The exclusion term **generic whole-spacecraft MBSE** means whole-spacecraft evidence with no qualifying EPS thread. It says nothing about whether the model itself is generic. A reusable whole-spacecraft artifact can receive an RQ1 profile only for its EPS-linked content and only after it passes the normal Route A or Route B eligibility rules. Genericity status and tier never decide whether a report is eligible.

### Eligible EPS evidence routes

Assign each full-text report to one of two routes. The routes are mutually exclusive. Use Route A only when the report's objective, modeled viewpoint or boundary, and substantial methods or results focus on the EPS. Otherwise, use Route B if it has a qualifying embedded thread. A report can contain several EPS threads, but its report-level route does not change.

- **Route A — EPS-primary MBSE:** The EPS, electrical-power viewpoint, or a defined EPS function or architecture is the main modeled boundary. The report identifies an EPS model artifact and at least one explicit relationship between that EPS content and another systems-engineering concern.
- **Route B — embedded EPS model thread:** A wider nanosatellite MBSE report contains at least one EPS thread that meets all three tests below.

A qualifying embedded thread needs:

1. an **EPS anchor**: a named EPS requirement, function, behavior, component, interface, mode, load or profile, budget, parameter, constraint, or hazard;
2. a **model anchor**: an identifiable representation of that EPS content in a structured system-model artifact or a clearly connected analysis model; and
3. an **explicit bridge**: a locatable relationship between the EPS anchor and a second concern, such as a requirement, behavior, architecture or interface, analysis, decision, output, or V&V artifact. Examples include allocation, trace, satisfy/refine/verify relations, interfaces or flows, parametric bindings, transformations, and data mappings.

An EPS label, equipment-list entry, or place in a general spacecraft breakdown can show where an anchor appears, but it is not a bridge by itself. The source does not have to name a formal relationship type. Its endpoints and meaning must still be clear enough to reconstruct.

Support the anchors and bridge with text, a figure or table, a model extract, a trace record, or another identifiable location in the source. Keywords, reviewer inference, or items that merely appear in the same report are not enough.

### MBSE-enabled outcomes and implementation burdens versus EPS engineering outputs

An **EPS engineering or model output** is a technical result such as minimum state of charge, power margin, battery capacity, solar-array area, voltage or current, energy balance, or a selected architecture. Extract these outputs for RQ1. They may also support RQ2 or RQ3, but they are not evidence of MBSE value on their own.

An outcome or implementation-burden record is eligible for RQ2 only when it has all three of the following:

1. an eligible EPS thread or a named EPS-linked model artifact or activity;
2. a reported beneficial, null, mixed, or adverse technical or process outcome, or an implementation burden, that the source explicitly attributes to that EPS artifact or activity rather than to a choice of EPS technology; and
3. wording for the result or claim that can be extracted, together with any evidence the source gives.

Record the proposed model-enabled mechanism when the source states it. Otherwise use `not_reported`. A missing mechanism makes the claim harder to interpret but does not remove an otherwise clear EPS-attributed record.

Eligibility records the source's explicit attribution; it does not establish that MBSE caused the outcome. During extraction, classify the kind and scope of claim, the directness of each measure, comparator adequacy when a comparison or causal claim requires one, possible confounding, fitness and conduct of the evaluation design, and the resulting support for that specific claim. Keep author attribution, observed association, and reviewer assessment of causal support separate.

A general claim about MBSE is not EPS-specific evidence merely because the same report contains EPS material. Keep claims supported only by assertion, but label them unsupported rather than treating them as demonstrated effects.

A null outcome means that an evaluation found no observed effect or difference. It does not mean `not_reported`, missing evidence, or no claim. Split benefits, adverse effects, null findings, and burdens into separate atomic records whenever possible. Use `mixed/conditional` only when directions cannot be separated by scenario, measure, actor, or condition.

A burden can exist alongside a benefit. Do not decide a net effect on the authors' behalf. General project-level MBSE burdens can be kept as RQ1 context. They enter direct RQ2 synthesis only when the source clearly links them to the qualifying EPS thread.

A power or energy margin alone is not a reliability result. Reliability requires a stated link to failure, fault tolerance, availability, risk, assurance, or another defined reliability concept. In the same way, do not infer reproducibility or reuse from model availability, or integration or interoperability from diagrams that merely appear together.

Classify measures as direct, surrogate, intermediate or process measures, or unclear relative to the construct claimed. A surrogate can support only the measured construct unless the source supplies a credible rationale or validation for the wider interpretation. For example, a successful model import can directly show one interoperability event but not general interoperability, and reduced artifact-generation time does not by itself establish an overall schedule reduction.

### Direct EPS-linked pre-physical V&V

A record is eligible for EPS-linked RQ3 synthesis only when it has all three of the following:

1. an **EPS target**: a named EPS requirement, model element, parameter, mode, interface, behavior, function, or hazard; or a wider system target that is clearly decomposed, allocated, or traced to named EPS content;
2. an **explicit model-to-V&V bridge**: a reported trace, shared ID, binding, port or data mapping, transformation, generated artifact, allocation, or another clear link; and
3. a **V&V method, intent, or artifact**: the source presents the work as verification, validation, compliance or requirement checking, virtual integration, a model-derived test activity, or another V&V function.

Classify each candidate record by its **linkage scope**:

- **`eps_specific`:** both the target and the V&V activity are clearly about the EPS;
- **`system_wide_eps_linked`:** a wider system activity includes a named EPS target and a bridge that can be reconstructed;
- **`system_wide_cooccurrence`:** system-wide V&V and EPS content appear in the same report without the required direct link; or
- **`unclear`:** the report does not make the scope clear.

Both `eps_specific` and `system_wide_eps_linked` records can enter direct RQ3 synthesis. Always report them separately and keep the scope of any result or verdict. `system_wide_cooccurrence` is a near miss and cannot support an EPS-specific conclusion.

Also classify the **object of V&V**, separately from scope and execution environment:

- **model verification:** checking whether a model, transformation, or executable representation was implemented correctly against its specification or formulation;
- **model validation:** checking whether a model is adequate or credible for its intended use against an authoritative reference, data, or expected behavior;
- **system/design verification:** checking whether the EPS or wider design meets stated requirements or criteria;
- **system/design validation:** checking whether the design meets stakeholder, operational, or mission needs;
- **multiple:** the source clearly demonstrates more than one of these objects; or
- **unclear.**

Keep the source's own term as well as the reviewer's normalized code and reason. Running a method in a model does not automatically make it model verification or model validation. For example, a virtual requirement check can be system or design verification. Code execution settings such as MIL, SIL, PIL, HIL, and virtual testbeds separately from the V&V object.

Classify completeness in stages. Do not discard an otherwise explicit linked record only because a later stage is missing:

- **EPS-linked V&V:** target, bridge, and V&V method, intent, or artifact are reported.
- **Criterion-complete EPS-linked V&V:** the record also gives a requirement, threshold, expected behavior, formal property, acceptance criterion, or pass/fail oracle.
- **Executed pre-physical V&V:** the linked method was run before physical integration or testing of the target EPS, and the source reports a result or verdict.
- **Model-to-test continuity/closure:** the source links a later physical artifact or activity. Reserve *closure* for cases that compare results and report how differences were handled.

A simulation or trade study without a stated V&V or checking purpose and without a criterion is analysis, not V&V. If a source calls an activity verification but does not report its criterion, keep it as an EPS-linked record but do not call it criterion-complete. General system V&V that merely appears beside EPS content does not answer RQ3.

For this review, **pre-physical V&V** is a model-based V&V artifact or activity prepared or run before physical integration or testing of the target EPS design. Preparation of a model-derived later physical test is included as preparation. MIL and SIL can qualify while the target EPS hardware remains virtual.

Classify PIL and HIL according to the hardware actually used. They are not wholly pre-physical if target EPS hardware takes part. Representative hardware or hardware outside the target EPS does not turn an otherwise virtual target-EPS activity into a physical EPS test. Record bench, environmental, integration, operational, and flight evidence as later model-to-test continuity. If the timing or target hardware is unclear, code it `uncertain` and do not count it as demonstrated pre-physical execution.

The RQ3 completeness stages are claim-specific descriptors, not a general evidence hierarchy. Target–bridge–method evidence supports the existence of an EPS-linked V&V activity; criterion, execution, and result support an executed-check claim; an appropriate oracle is required for model or design validation; and linked physical evidence supports continuity only for the artifacts and comparisons actually traced. Operational or flight maturity does not automatically strengthen a different claim.

## Units of evidence and counting

Use the following linked units. They do not form a simple hierarchy because report families and artifact lineages may cross reports and implementations.

1. **Study or implementation report family:** one underlying investigation, mission or design implementation, artifact release, or substantially shared model or toolchain use represented by one or more reports. Require source-supported overlap; a shared topic, organization, or tool is not enough.
2. **Report:** one distinct publication, preprint, institutional report, or completed thesis or dissertation. Treat an arXiv preprint and a later formal version as candidate manifestations of the same report: merge them only when no difference material to this review is found, and otherwise retain them as companion reports in the same family. Preserve version-level dates, provenance, and substantive differences in either case.
3. **EPS model thread:** one qualifying EPS-primary or embedded chain within a report.
4. **Reusable EPS artifact lineage and genericity profile:** one identifiable base artifact and its source-supported versions or derived instances. Split profiles when versions or scopes differ materially.
5. **Tailoring application:** one use of an artifact lineage in one target setting, including a justified unchanged adoption. Merge repeated reporting of the same application.
6. **Outcome or implementation-burden record:** one atomic direction or burden linked, or possibly linked, to an EPS thread.
7. **V&V record:** one target–method–scenario activity or artifact linked, or possibly linked, to an EPS thread.

Record source-supported family and lineage relationships, their reasons, evidence locations, and relationship coding confidence. Do not move evidence silently between reports, versions, applications, or families. A report can belong to more than one family only when it genuinely covers separate implementations or evaluations.

PRISMA identification and selection counts remain at record and report level. Report separate denominators for families, reports, threads, artifact lineages and profiles, tailoring applications, inputs and assumptions, outcomes and burdens, and V&V records. A report count is not a count of independent implementations or transfers.

Use linked IDs such as `family_id`, `report_id:thread_id`, `artifact_lineage_id:genericity_profile_id`, `artifact_lineage_id:tailoring_application_id`, `report_id:thread_id:outcome_burden_id`, and `report_id:thread_id:vnv_id`. Prefer normalized DOI for report identity, supplemented by source and report identifiers. Old IDs and discovery paths are provenance only.

---

**Next:** [Part 2 — Discovery and appraisal](protocol-discovery-and-appraisal.md)
