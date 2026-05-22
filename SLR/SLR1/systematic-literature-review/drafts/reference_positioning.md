# Reference positioning for SLR1 relative to Buruso et al. (2026)

## 1. Buruso et al. review structure to emulate selectively

Buruso et al. \cite{Buruso2026MBSESpace} is a broad comprehensive literature review of MBSE in space applications. It should be used as the positioning baseline, not as a structure to duplicate fully.

### Section 2: Literature Review Method

Relevant structural elements to emulate:

- **Transparent protocol and review type.** Buruso et al. frame the review using PRISMA-inspired selection logic, explicit scope, inclusion/exclusion criteria, review procedure, data collection, synthesis method, inter-rater reliability, and validity discussion.
- **A domain-specific organizing framework.** Their method introduces five MBSE activity anchors: requirements management, model development, simulation and analysis, configuration management, and collaboration/communication. These anchors connect ISO/IEC/IEEE 15288 and ISO/IEC/IEEE 24641 lifecycle thinking to practical MBSE implementation.
- **Research questions aligned to extraction.** Their RQs target methods, modeling languages, tools, relationships between enablers and MBSE phases, and challenges/opportunities.
- **Coding logic.** They classify methods bottom-up into Pure, Enhanced, Extended, and Integrated MBSE, while classifying languages and tools more top-down by role/function.
- **Validity measures.** They include external rater agreement for the classification scheme.

How SLR1 should differ:

- Use Buruso et al.'s five phases and four MBSE-approach classes as **sensitizing categories**, but make the SLR1 protocol RQs primary: nanosatellite/EPS general modeling, claimed value outcomes, and pre-physical-development V\&V linkage.
- Replace broad space-system inclusion with the protocol's narrower population: nanosatellite-class missions and EPS-relevant MBSE.
- Emphasize claim-evidence extraction, governance/ROI linkage, and EPS/V\&V artifacts more than broad method/language/tool taxonomy.

### Section 3: Statistical Overview and Synthesis Analysis

Relevant structural elements to emulate:

- **Descriptive corpus overview.** Buruso et al. summarize publication years, countries, affiliations, venues, and mission categories before deeper synthesis.
- **Mission-category positioning.** Their mission categories show that CubeSat and SmallSat studies are substantial but only part of the wider space-MBSE literature.
- **Phase-based synthesis.** They describe how requirements management, model development, simulation/analysis, configuration management, and collaboration/communication appear across their corpus.
- **Enabler taxonomy.** They synthesize four MBSE methodology archetypes, four language classes, and six broad tool classes.

How SLR1 should differ:

- Provide corpus statistics only insofar as they explain evidence strength and applicability to nanosatellite/EPS contexts.
- Use modeling-focus groups already identified in the scoping report: whole nanosatellite with EPS/power as a subsystem, generic whole nanosatellite with no explicit EPS, and EPS-only/EPS-first.
- Treat method/language/tool counts as support for RQ interpretation, not as a standalone result because Buruso et al. already provide the broad space-sector taxonomy.

### Section 4: Findings of the CLR

Relevant structural elements to emulate:

- **Results organized by classification crossed with MBSE phase.** Buruso et al. discuss how method archetypes, languages, and tool classes support the five phases.
- **Lifecycle overlay.** Their Section 4.4 links MBSE phases to NASA lifecycle stages and explains how activities such as requirements, model development, simulation, configuration management, and collaboration recur across lifecycle gates.
- **Use of examples.** They use representative mission/tool examples to interpret patterns rather than only reporting counts.

How SLR1 should differ:

- Organize findings by the SLR1 RQs rather than by enabler taxonomy:
  - RQ1: How nanosatellite missions and EPS are modeled with limited prior behavior knowledge.
  - RQ2: What reliability, reproducibility, and integrability outcomes are claimed, and what evidence supports them.
  - RQ3: How verification procedures are integrated into models before physical development.
- Include enabler/phase analysis as a cross-cutting explanatory layer only where it clarifies value mechanisms, implementation pathway, or V\&V readiness.
- Highlight that SLR1's scoping synthesis found 40 accessible extracted studies, with 32 whole-nanosatellite studies including EPS/power as a subsystem, 7 generic/no-explicit-EPS studies, and only 1 EPS-only or EPS-first study.

### Section 5: Global Discussion

Relevant structural elements to emulate:

- **Objective-driven MBSE discussion.** Buruso et al. argue that MBSE value depends on clearly defined objectives, lifecycle scope, model usage, governance, and evaluation criteria.
- **Context-driven enabler selection.** They caution that no single method/tool/language is sufficient; enablers must be selected according to mission complexity, resource constraints, lifecycle needs, and organizational maturity.
- **Gaps table as research agenda.** Table 5 summarizes five gaps: unclear practical implementation pathways, fragmented toolchains, resource-mismatched frameworks for small missions, weak integration between artifacts/governance/ROI, and misalignment with evolving space-industry demands.

How SLR1 should differ:

- Treat Table 5 as the explicit justification for this narrower review.
- Focus the discussion on how those broad gaps manifest in nanosatellite and EPS-relevant studies.
- Make value evidence central: distinguish asserted benefits from supported benefits, and identify where MBSE artifacts are actually linked to verification, project decisions, reproducibility, or integration/test readiness.

## 2. Mapping Buruso Table 5 gaps to SLR1's unique contribution

| Buruso Table 5 gap | Buruso opportunity/future direction | SLR1 unique contribution |
|---|---|---|
| Lack of clear practical implementation pathways for new adopters, including unclear objectives and process boundaries | Five MBSE phase anchors aligned with lifecycle stages; future work should connect application objectives, MBSE artifacts, and evaluation criteria | SLR1 narrows the pathway question to nanosatellite-class and EPS-relevant MBSE. It extracts reported implementation steps, inputs/outputs, actors, prerequisites, completion criteria, lifecycle gates, and handoffs. It can show whether papers provide reusable pathways or only case-specific demonstrations. |
| Fragmented toolchains and lack of interoperability across tools and lifecycle stages | Map phases to enablers; future work should advance integrated digital-engineering environments and downstream continuity into Phases C/D | SLR1 examines actual nanosatellite/EPS toolchains and data flows, including SysML--simulation coupling, spreadsheets, XMI/XML/API/script bridges, model transformations, and manual synchronization. The distinctive focus is whether toolchains preserve semantic continuity into pre-physical verification, software/hardware/system integration readiness, and EPS/power-budget checks. |
| Resource-mismatched MBSE frameworks for lightweight or small-scale missions | Tailor Pure, Enhanced, Extended, and Integrated MBSE by mission scale and maturity; develop modular/scalable playbooks for CubeSats | SLR1 is centered on the resource-constrained mission class. It can identify which practices appear lightweight enough for CubeSat/nanosatellite teams, which require enterprise-level maturity, and where open-source or docs-as-code approaches reduce adoption burden. |
| Lack of integration between MBSE artifacts, project governance, and evidence for ROI | Align phases with programmatic gates and critical design events; future work should define governance, lifecycle traceability, and value-realization metrics | SLR1's extraction protocol includes governance, ROI, project-decision linkage, value mechanisms, evidence type, metrics, baselines, and confidence ratings. This enables a value-driven synthesis rather than another list of generic MBSE benefits. |
| Misalignment between MBSE strategies and evolving demands of the space industry | Contextualize selective MBSE implementation for NewSpace risk tolerance, rapid iteration, and distributed teams; study prototype-to-production transitions | SLR1 focuses on nanosatellite/NewSpace-like constraints: academic/student missions, rapid prototyping, distributed teams, concurrent/agile workflows, and limited resources. It can assess whether MBSE supports in-house design, test, manufacturing, and V\&V without imposing heavyweight enterprise practice. |

Overall positioning: Buruso et al. identify the broad space-MBSE gaps; SLR1 investigates whether and how those gaps are addressed in the narrower but practically important nanosatellite/EPS literature, with special attention to value evidence and V\&V linkage.

## 3. Recommended body outline and subsection titles for the SLR1 manuscript

No abstract, introduction, or conclusion sections are included here.

### 2. Review method

- **2.1 Review scope and protocol basis**
- **2.2 Research questions**
- **2.3 Search sources, search strings, and study identification**
- **2.4 Screening, eligibility, and retrieval**
- **2.5 Quality appraisal and sensitivity use**
- **2.6 Data extraction schema**
- **2.7 Coding and synthesis strategy**
- **2.8 Relationship to prior space-MBSE synthesis**
- **2.9 Threats to validity**

### 3. Corpus overview

- **3.1 PRISMA-style flow and accessible corpus**
- **3.2 Publication years, venues, and study tiers**
- **3.3 Nanosatellite mission context and lifecycle stage**
- **3.4 Modeling focus: whole nanosatellite, EPS-as-subsystem, and EPS-first studies**
- **3.5 Model maturity and reproducibility characteristics**
- **3.6 Quality-score distribution and evidence implications**

### 4. RQ1 results: General nanosatellite and EPS modeling with limited behavior knowledge

- **4.1 Modeling scopes and abstraction levels**
- **4.2 Reference models, templates, profiles, libraries, and reusable workflows**
- **4.3 EPS representation in system-level models**
- **4.4 EPS-only and EPS-first modeling evidence**
- **4.5 Required prior domain/behavior knowledge and how papers reduce it**
- **4.6 Implementation pathways and tailoring for resource-constrained teams**

### 5. RQ2 results: Claimed value from EPS/nanosatellite MBSE

- **5.1 Claimed outcome categories**
- **5.2 Reliability and mission-assurance claims**
- **5.3 Reproducibility, reuse, and model/package availability claims**
- **5.4 Integrability, interoperability, and lifecycle-continuity claims**
- **5.5 Evidence types, metrics, baselines, and confidence ratings**
- **5.6 Gaps between generic MBSE claims and EPS-specific evidence**

### 6. RQ3 results: Verification and validation linkage before physical development

- **6.1 Verification artifacts represented in the model**
- **6.2 Requirements traceability and verification matrices**
- **6.3 Parametric, budget, margin, and constraint checks**
- **6.4 Executable simulation, scenario verification, and virtual integration**
- **6.5 Test cases, automated tests, SIL/HIL, and integration/test readiness**
- **6.6 Weak or missing model-linked V\&V evidence**

### 7. Cross-cutting synthesis

- **7.1 MBSE approach tailoring: Pure, Enhanced, Extended, and Integrated patterns in nanosatellite studies**
- **7.2 Toolchain and interoperability patterns relevant to EPS and V\&V**
- **7.3 Lifecycle and review-gate coverage**
- **7.4 Governance, configuration management, and value-realization evidence**
- **7.5 NewSpace, academic, and resource-constrained adoption implications**

### 8. Discussion

- **8.1 How nanosatellite/EPS evidence extends the broad space-MBSE review landscape**
- **8.2 What should be emulated from current practice**
- **8.3 What remains under-evidenced: value, ROI, and verification continuity**
- **8.4 Research agenda for value-driven MBSE in nanosatellite EPS development**

## 4. Cautions: broad claims to keep concise because Buruso et al. already cover them

- **Do not re-taxonomize MBSE methods for space applications.** Buruso et al. already provide Pure, Enhanced, Extended, and Integrated MBSE archetypes. SLR1 should use these categories only to interpret nanosatellite tailoring and evidence strength.
- **Do not provide a long general history of SysML, UML, LML, Modelica, AADL, XML/XMI, APIs, Python, or data languages.** Buruso et al. already explain their roles. SLR1 should report only corpus-specific use and implications for EPS modeling, traceability, and V\&V.
- **Do not catalogue general MBSE tools across space engineering.** Cameo/MagicDraw, MATLAB/Simulink, STK/GMAT, Capella/Arcadia, OpenMBEE, ModelCenter, PLM tools, and agency frameworks are already broadly covered. In SLR1, tool names should appear only when they affect implementation pathway, interoperability, reproducibility, or verification readiness.
- **Do not restate generic MBSE benefits as findings.** Claims such as reduced cost, reduced schedule, better communication, single source of truth, improved reliability, or improved integration should be treated as evidence-coded claims. Report whether each is asserted, illustrated, simulated, measured, compared to a baseline, reused, or linked to integration/test/flight evidence.
- **Do not overgeneralize from CubeSat reference-model lineages.** Several studies may reuse or extend the same reference-model family. Treat lineage/overlap explicitly so that repeated publications do not appear as independent confirmation.
- **Do not claim that broad space-MBSE toolchain integration has been solved.** Buruso et al. identify fragmentation as a continuing gap. SLR1 should assess whether nanosatellite/EPS studies provide concrete continuity across requirements, architecture, analysis, verification, and integration/test.
- **Do not make broad NASA/ESA/MB4SE institutional adoption claims unless needed for context.** Cite Buruso et al. for sector-level context and keep SLR1 centered on nanosatellite and EPS evidence.
- **Do not let method/language/tool frequency overshadow the RQs.** The manuscript should foreground generality, value evidence, and pre-physical V\&V linkage.

## 5. Suggested citation phrasing using `Buruso2026MBSESpace`

### Positioning in the introduction or related-work setup

> A recent comprehensive review of MBSE in space applications synthesized 126 studies and mapped MBSE methods, languages, and tools across requirements management, model development, simulation and analysis, configuration management, and collaboration/communication phases \cite{Buruso2026MBSESpace}. Rather than repeating that broad enabler taxonomy, this review examines a narrower question: how MBSE is used in nanosatellite and EPS-relevant studies to support general modeling, value realization, and model-linked verification before physical development.

### Positioning the gap

> Buruso et al. identify persistent gaps in practical implementation pathways, toolchain interoperability, lightweight MBSE for small missions, governance/ROI linkage, and alignment with NewSpace-style development \cite{Buruso2026MBSESpace}. These gaps motivate the present review's focus on nanosatellite-class missions, where resource constraints and rapid iteration make heavyweight MBSE adoption difficult, and where EPS/power models provide an important test case for value-driven MBSE.

### Positioning in the method section

> We use the five MBSE activity anchors synthesized by Buruso et al. \cite{Buruso2026MBSESpace} as sensitizing categories during coding, while retaining the protocol research questions as the primary synthesis structure. This allows comparison with the broader space-MBSE literature without duplicating its method/language/tool taxonomy.

### Positioning in results/discussion

> Our findings complement Buruso et al.'s broad space-sector synthesis \cite{Buruso2026MBSESpace} by showing how the same implementation challenges appear in nanosatellite/EPS studies: many papers report system-level architecture, toolchain, and traceability benefits, but fewer provide EPS-specific evidence, quantified value, or verification artifacts integrated into models before physical development.

### Concise citation when reporting common enablers

> The dominance of SysML-centered modeling and the recurring coupling of architecture models with simulation, analysis, and lifecycle-management tools are consistent with the wider space-MBSE patterns reported by Buruso et al. \cite{Buruso2026MBSESpace}; here, we focus on whether those enablers support EPS-specific value claims and V\&V continuity.
