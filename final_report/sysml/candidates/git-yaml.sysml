// Current proposed physical candidate. No satisfaction or empirical result.
package CandidateGY {
    private import PhysicalVocabulary::*;
    private import FrameworkDomain::*;
    private import FrameworkLogical::*;
    doc /* PA-GY: Git/YAML engineering definitions. Retain: portable reviewable text is a distinct authoring choice. Source prototypes exclude requirement/test management, so all engineering semantics, assistance and evidence controls are proposed additions. Git alone supplies no approval or engineering meaning. Editor/Python on local engineering workstation, local assistance service and Git/archive service. YAML owns engineering fields only through an approved typed schema with units, relationships and semantic checks. Human-readable text review and nontechnical contributor usability require proof. */
    part def C01 :> ExchangeSoftware {
        doc /* Editor/Python panel and generated engineering/review documents. Check every external mapping for stable identities, revisions, structure, units, polarity and time/mode meaning. Preserve rejected raw transfers. Views resolve one controlled baseline. */
        perform action :>> checkTransfer;
        perform action :>> makeViews;
    }
    @ComponentSpecification about C01 { tools = "Editor/Python panel and generated engineering/review documents"; authority = "Check every external mapping for stable identities, revisions, structure, units, polarity and time/mode meaning. Preserve rejected raw transfers. Views resolve one controlled baseline."; verificationNeed = "Verify assigned current FR checks, interfaces, failure/currency paths and source/profile limitations. Implementation pending."; status = "proposed, not verified"; }
    part def C02 :> AssistanceSoftware {
        doc /* Local Python active assistance with pinned Qwen/BM25. Active Python drafting rules, BM25/local pinned Qwen retrieval/reranking, optional admitted pinned Jev scoring, controlled applicability and separate cited rule/source/context explanations. Retain uncertainty, no eligible/unavailable status and human dispositions. */
        perform action :>> acknowledge;
        perform action checkDraft : PhysicalCheckDraft :>> AssistanceSoftware::checkDraft;
        perform action :>> dispose;
        perform action recommend : PhysicalRecommendMethods :>> AssistanceSoftware::recommend;
        perform action reassess : PhysicalReassessAssistance :>> AssistanceSoftware::reassess {
            perform action checkDraft :>> checkDraft references CandidateGY::C02::checkDraft;
            perform action recommend :>> recommend references CandidateGY::C02::recommend;
        }
    }
    @ComponentSpecification about C02 { tools = "Local Python active assistance with pinned Qwen/BM25"; authority = "Active Python drafting rules, BM25/local pinned Qwen retrieval/reranking, optional admitted pinned Jev scoring, controlled applicability and separate cited rule/source/context explanations. Retain uncertainty, no eligible/unavailable status and human dispositions."; verificationNeed = "Verify assigned current FR checks, interfaces, failure/currency paths and source/profile limitations. Implementation pending."; status = "proposed, not verified"; }
    part def C03 :> RequirementsSoftware {
        doc /* Typed YAML requirement records with Python links and allocation rules. Retain requirement meaning and proposed derivation/allocation. Reviewed record changes preserve unresolved fields and exact parents. Similarity and imported functions are not requirement derivation. */
        perform action :>> deriveAllocate;
        perform action :>> retainRequirements;
        perform action :>> traceLinks;
    }
    @ComponentSpecification about C03 { tools = "Typed YAML requirement records with Python links and allocation rules"; authority = "Retain requirement meaning and proposed derivation/allocation. Reviewed record changes preserve unresolved fields and exact parents. Similarity and imported functions are not requirement derivation."; verificationNeed = "Verify assigned current FR checks, interfaces, failure/currency paths and source/profile limitations. Implementation pending."; status = "proposed, not verified"; }
    part def C04 :> DesignSoftware {
        doc /* Typed YAML mission/EPS/interface definitions and Python calculations. Own mission/ConOps, modeled component occurrences, variants, BOM quantities and sourced budgets/sizing, dated EPS acquisition estimates, feasibility-first trades and detailed control/interface definitions. */
        perform action :>> budgetSize;
        perform action :>> compareDesigns;
        perform action :>> defineDesign;
        perform action :>> defineInterfaces;
    }
    @ComponentSpecification about C04 { tools = "Typed YAML mission/EPS/interface definitions and Python calculations"; authority = "Own mission/ConOps, modeled component occurrences, variants, BOM quantities and sourced budgets/sizing, dated EPS acquisition estimates, feasibility-first trades and detailed control/interface definitions."; verificationNeed = "Verify assigned current FR checks, interfaces, failure/currency paths and source/profile limitations. Implementation pending."; status = "proposed, not verified"; }
    part def C05 :> AnalysisSoftware {
        doc /* Python plans, specialist-model adapters and host work coordination. Plan declared coupled numerical, RAM and MIL profiles. Coordinate external models and exact released host coding/build/SIL. Preserve solver/coupling/resources, matched stimuli and replay rules. Every mandatory discipline profile needs verification. */
        perform action :>> compareMILSil;
        perform action :>> coordinateCoding;
        perform action :>> planAnalysis;
        perform action :>> planMIL;
        perform action :>> replay;
        perform action :>> verifyProfiles;
        perform action :>> verifyHostProfiles;
    }
    @ComponentSpecification about C05 { tools = "Python plans, specialist-model adapters and host work coordination"; authority = "Plan declared coupled numerical, RAM and MIL profiles. Coordinate external models and exact released host coding/build/SIL. Preserve solver/coupling/resources, matched stimuli and replay rules. Every mandatory discipline profile needs verification."; verificationNeed = "Verify assigned current FR checks, interfaces, failure/currency paths and source/profile limitations. Implementation pending."; status = "proposed, not verified"; }
    part def C06 :> CredibilitySoftware {
        doc /* Python credibility and supplied-history assessment. Check intended use, fidelity, omissions, validity, numerics and history quality. Preserve raw values and masks, sample/receipt times and residual units. Separate supplied-data calibration proposals from independent assessment. */
        perform action :>> assessModel;
        perform action :>> proposeCalibration;
    }
    @ComponentSpecification about C06 { tools = "Python credibility and supplied-history assessment"; authority = "Check intended use, fidelity, omissions, validity, numerics and history quality. Preserve raw values and masks, sample/receipt times and residual units. Separate supplied-data calibration proposals from independent assessment."; verificationNeed = "Verify assigned current FR checks, interfaces, failure/currency paths and source/profile limitations. Implementation pending."; status = "proposed, not verified"; }
    part def C07 :> ReviewSoftware {
        doc /* Python EPS/review assessments and generated baseline-linked views. Plan EPS verification/validation against separate requirements/expectations. Assess critical gaps, prepare scoped review packages and record only current designated-authority decisions. Prepared is not accepted. */
        perform action :>> assessProduct;
        perform action :>> planAssessment;
        perform action :>> prepareReview;
        perform action :>> recordReview;
    }
    @ComponentSpecification about C07 { tools = "Python EPS/review assessments and generated baseline-linked views"; authority = "Plan EPS verification/validation against separate requirements/expectations. Assess critical gaps, prepare scoped review packages and record only current designated-authority decisions. Prepared is not accepted."; verificationNeed = "Verify assigned current FR checks, interfaces, failure/currency paths and source/profile limitations. Implementation pending."; status = "proposed, not verified"; }
    part def C08 :> ConfigurationSoftware {
        doc /* Git-reviewed text definitions, managed archive and Python revision/impact index. Git and a managed raw-result/source archive preserve exact revisions, impacts, predecessors and authorized successors. Rebuildable indexes do not own engineering fields. Invalidate edited/pending guidance immediately and recheck latest context before display/application. */
        perform action :>> invalidate;
        perform action :>> preserveRun;
        perform action :>> retrieveBaseline;
        perform action :>> successor;
        perform action checkCurrency : PhysicalCheckCurrency :>> ConfigurationSoftware::checkCurrency;
    }
    @ComponentSpecification about C08 { tools = "Git-reviewed text definitions, managed archive and Python revision/impact index"; authority = "Git and a managed raw-result/source archive preserve exact revisions, impacts, predecessors and authorized successors. Rebuildable indexes do not own engineering fields. Invalidate edited/pending guidance immediately and recheck latest context before display/application."; verificationNeed = "Verify assigned current FR checks, interfaces, failure/currency paths and source/profile limitations. Implementation pending."; status = "proposed, not verified"; }
    part def Configuration :> LogicalFramework {
        part :>> L01 : C01;
        part :>> L02 : C02 {
            perform action checkDraft : PhysicalCheckDraft :>> C02::checkDraft, FrameworkLogical::Assistance::checkDraft;
            perform action recommend : PhysicalRecommendMethods :>> C02::recommend, FrameworkLogical::Assistance::recommend;
            perform action reassess : PhysicalReassessAssistance :>> C02::reassess, FrameworkLogical::Assistance::reassess;
        }
        part :>> L03 : C03;
        part :>> L04 : C04;
        part :>> L05 : C05;
        part :>> L06 : C06;
        part :>> L07 : C07;
        part :>> L08 : C08 {
            perform action checkCurrency : PhysicalCheckCurrency :>> C08::checkCurrency, FrameworkLogical::Configuration::checkCurrency;
        }
        part N1 : EngineeringHost;
        part N2 : AssistanceHost;
        part N3 : ArchiveHost;
        part engineeringNode : ResponsibilityNode;
        part assistanceNode : ResponsibilityNode;
        part evidenceNode : ResponsibilityNode;
        part models : ModelEnvironment;
        part hostCode : HostToolchain;
        ref item modelRecords : ModelData [0..*];
        ref item sourceAndAdviceRecords : AdviceData [0..*];
        ref item rawResultsAndReleases : ReleaseData [0..*];
        perform action engineeringProcedure : EngineeringProcedure;
        perform action reviewProcedure : ReviewProcedure;
        perform action assistance : PhysicalAssistanceRealization {
            perform action checkDraft :>> checkDraft references L02.checkDraft;
            perform action recommend :>> recommend references L02.recommend;
            perform action reassess :>> reassess references L02.reassess;
            perform action checkReply :>> checkReply references L08.checkCurrency;
            perform action checkApplication :>> checkApplication references L08.checkCurrency;
        }
        perform action concept : PhysicalConceptRealization {
            perform action :>> execute { perform action profiles :>> profiles references L05.verifyProfiles; }
        }
        perform action designRun : PhysicalDesignRealization {
            perform action :>> execute { perform action profiles :>> profiles references L05.verifyProfiles; }
        }
        perform action software : PhysicalSoftwareRealization {
            perform action :>> executeMIL { perform action profiles :>> profiles references L05.verifyProfiles; }
            perform action :>> codeBuildSil { perform action profiles :>> profiles references L05.verifyHostProfiles; }
        }
        perform action changeReview : PhysicalChangeReviewRealization {
            perform action reassessAdvice :>> reassessAdvice references L02.reassess;
            perform action :>> repeat { perform action profiles :>> profiles references L05.verifyProfiles; }
        }
        perform action replayRun : PhysicalReplayRealization {
            perform action :>> execute { perform action profiles :>> profiles references L05.verifyProfiles; }
        }
        perform action calibration : PhysicalCalibrationRealization {
            perform action reassess :>> reassess references L02.reassess;
            perform action :>> repeat { perform action profiles :>> profiles references L05.verifyProfiles; }
        }
        bind N1.exchange = L01;
        bind N1.requirements = L03;
        bind N1.design = L04;
        bind N1.analyses = L05;
        bind N1.credibility = L06;
        bind N1.review = L07;
        bind N2.advice = L02;
        bind N3.configuration = L08;
        bind N1.models = L01.p03;
        bind N1.hostCode = L01.p04;
        interface adviceLink connect N1.assistance to N2.assistance;
        interface releasedData connect N1.revisions to N3.engineering;
        interface sourceAdvice connect N2.revisions to N3.assistance;
        interface modelLink connect N1.models to models.requests;
        interface codeLink connect N1.hostCode to hostCode.requests;
    }
    @SourceRecord about Configuration { identifier = "PA-GY"; sourceText = "Retain: portable reviewable text is a distinct authoring choice. Source prototypes exclude requirement/test management, so all engineering semantics, assistance and evidence controls are proposed additions. Git alone supplies no approval or engineering meaning."; sourceLocator = "Synthesize Candidate Physical Architectures and conditional comparison"; status = "proposed, access and verification pending"; citationRecord = "kanavouras2024lightweight, chiu2023sealion"; }
    part candidate : Configuration;
    #logicalRealization allocation logical_L01 allocate logical.L01 to candidate.L01;
    #executionHost allocation host_L01 allocate candidate.L01 to candidate.N1;
    allocation node_L01 allocate logical.L01 to candidate.engineeringNode;
    #logicalRealization allocation logical_L02 allocate logical.L02 to candidate.L02;
    #executionHost allocation host_L02 allocate candidate.L02 to candidate.N2;
    allocation node_L02 allocate logical.L02 to candidate.assistanceNode;
    #logicalRealization allocation logical_L03 allocate logical.L03 to candidate.L03;
    #executionHost allocation host_L03 allocate candidate.L03 to candidate.N1;
    allocation node_L03 allocate logical.L03 to candidate.engineeringNode;
    #logicalRealization allocation logical_L04 allocate logical.L04 to candidate.L04;
    #executionHost allocation host_L04 allocate candidate.L04 to candidate.N1;
    allocation node_L04 allocate logical.L04 to candidate.engineeringNode;
    #logicalRealization allocation logical_L05 allocate logical.L05 to candidate.L05;
    #executionHost allocation host_L05 allocate candidate.L05 to candidate.N1;
    allocation node_L05 allocate logical.L05 to candidate.engineeringNode;
    #logicalRealization allocation logical_L06 allocate logical.L06 to candidate.L06;
    #executionHost allocation host_L06 allocate candidate.L06 to candidate.N1;
    allocation node_L06 allocate logical.L06 to candidate.engineeringNode;
    #logicalRealization allocation logical_L07 allocate logical.L07 to candidate.L07;
    #executionHost allocation host_L07 allocate candidate.L07 to candidate.N1;
    allocation node_L07 allocate logical.L07 to candidate.engineeringNode;
    #logicalRealization allocation logical_L08 allocate logical.L08 to candidate.L08;
    #executionHost allocation host_L08 allocate candidate.L08 to candidate.N3;
    allocation node_L08 allocate logical.L08 to candidate.evidenceNode;
    #persistentStorage allocation store_modelRecords allocate candidate.modelRecords to candidate.N1;
    #persistentStorage allocation store_sourceAndAdviceRecords allocate candidate.sourceAndAdviceRecords to candidate.N2;
    #persistentStorage allocation store_rawResultsAndReleases allocate candidate.rawResultsAndReleases to candidate.N3;
    #procedurePerformer allocation engineeringOperator allocate candidate.engineeringProcedure to ScenarioViews::systemsEngineer;
    #procedurePerformer allocation reviewOperator allocate candidate.reviewProcedure to ScenarioViews::reviewAuthority;
    allocation guidanceState allocate logical.L08.assistanceCurrency to candidate.L08.assistanceCurrency;
    allocation reviewState allocate logical.L07.reviewState to candidate.L07.reviewState;
    #physicalPrimary allocation FR_01_primary allocate FrameworkRequirements::FR_01 to candidate.L03 {
        @PhysicalAllocation { rationale = "Typed YAML requirement records with Python links and allocation rules. Requirement semantics and unresolved fields belong with the allocated requirement record."; plannedCheck = "I,T: Round-trip quantitative and qualitative records, including unresolved criteria."; operation = CandidateGY::C03::retainRequirements meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_01_L08 allocate FrameworkRequirements::FR_01 to candidate.L08;
    dependency operation_FR_01 from FrameworkRequirements::FR_01 to CandidateGY::C03::retainRequirements;
    #physicalPrimary allocation FR_02_primary allocate FrameworkRequirements::FR_02 to candidate.L02 {
        @PhysicalAllocation { rationale = "Local Python active assistance with pinned Qwen/BM25. Active rule and probable semantic checks share explained assistance, separate from technical approval."; plannedCheck = "A,T: Compare clean and seeded drafts with an independent expert reference, including valid similar requirements and missed defects."; operation = CandidateGY::C02::checkDraft meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_02_L03 allocate FrameworkRequirements::FR_02 to candidate.L03;
    dependency operation_FR_02 from FrameworkRequirements::FR_02 to CandidateGY::C02::checkDraft;
    #physicalPrimary allocation FR_03_primary allocate FrameworkRequirements::FR_03 to candidate.L02 {
        @PhysicalAllocation { rationale = "Local Python active assistance with pinned Qwen/BM25. Contextual eligibility and explained alternatives belong to assistance, with model validity supplied by credibility."; plannedCheck = "A,T: Use contextual queries whose eligible methods change with inputs, maturity or intended use."; operation = CandidateGY::C02::recommend meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_03_L06 allocate FrameworkRequirements::FR_03 to candidate.L06;
    dependency operation_FR_03 from FrameworkRequirements::FR_03 to CandidateGY::C02::recommend;
    #physicalPrimary allocation FR_04_primary allocate FrameworkRequirements::FR_04 to candidate.L03 {
        @PhysicalAllocation { rationale = "Typed YAML requirement records with Python links and allocation rules. Requirements ownership defines link/coverage meaning while configuration preserves exact endpoints."; plannedCheck = "T: Compare both query directions and coverage with a known relationship set."; operation = CandidateGY::C03::traceLinks meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_04_L08 allocate FrameworkRequirements::FR_04 to candidate.L08;
    dependency operation_FR_04 from FrameworkRequirements::FR_04 to CandidateGY::C03::traceLinks;
    #physicalPrimary allocation FR_05_primary allocate FrameworkRequirements::FR_05 to candidate.L08 {
        @PhysicalAllocation { rationale = "Git-reviewed text definitions, managed archive and Python revision/impact index. Cross-domain revision dependencies determine impacts and repeated work."; plannedCheck = "A,T: Compare the impact set of coupled load, pointing and interface changes with an expert reference."; operation = CandidateGY::C08::invalidate meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_05_L03 allocate FrameworkRequirements::FR_05 to candidate.L03;
    #physicalSupport allocation FR_05_L04 allocate FrameworkRequirements::FR_05 to candidate.L04;
    dependency operation_FR_05 from FrameworkRequirements::FR_05 to CandidateGY::C08::invalidate;
    #physicalPrimary allocation FR_06_primary allocate FrameworkRequirements::FR_06 to candidate.L08 {
        @PhysicalAllocation { rationale = "Git-reviewed text definitions, managed archive and Python revision/impact index. Only configuration can preserve predecessors and issue an authorized distinct successor."; plannedCheck = "T: Accept, decline and interrupt changes without erasing the predecessor."; operation = CandidateGY::C08::successor meta SysML::ActionUsage; }
    }
    dependency operation_FR_06 from FrameworkRequirements::FR_06 to CandidateGY::C08::successor;
    #physicalPrimary allocation FR_07_primary allocate FrameworkRequirements::FR_07 to candidate.L08 {
        @PhysicalAllocation { rationale = "Git-reviewed text definitions, managed archive and Python revision/impact index. Exact product/evidence revisions and decisions define a reconstructible baseline."; plannedCheck = "I,T: Reconstruct predecessor and successor manifests and all applicable products."; operation = CandidateGY::C08::retrieveBaseline meta SysML::ActionUsage; }
    }
    dependency operation_FR_07 from FrameworkRequirements::FR_07 to CandidateGY::C08::retrieveBaseline;
    #physicalPrimary allocation FR_08_primary allocate FrameworkRequirements::FR_08 to candidate.L01 {
        @PhysicalAllocation { rationale = "Editor/Python panel and generated engineering/review documents. The external receiving responsibility checks meaning before controlled registration."; plannedCheck = "T: Inject identity, unit, sign and revision mismatches at each active interface."; operation = CandidateGY::C01::checkTransfer meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_08_L08 allocate FrameworkRequirements::FR_08 to candidate.L08;
    dependency operation_FR_08 from FrameworkRequirements::FR_08 to CandidateGY::C01::checkTransfer;
    #physicalPrimary allocation FR_09_primary allocate FrameworkRequirements::FR_09 to candidate.L08 {
        @PhysicalAllocation { rationale = "Git-reviewed text definitions, managed archive and Python revision/impact index. Preservation links every status and raw output to its execution configuration."; plannedCheck = "I,T: Trace successful, failed, cancelled and partial outputs to their configurations."; operation = CandidateGY::C08::preserveRun meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_09_L05 allocate FrameworkRequirements::FR_09 to candidate.L05;
    dependency operation_FR_09 from FrameworkRequirements::FR_09 to CandidateGY::C08::preserveRun;
    #physicalPrimary allocation FR_10_primary allocate FrameworkRequirements::FR_10 to candidate.L05 {
        @PhysicalAllocation { rationale = "Python plans, specialist-model adapters and host work coordination. Analysis coordination owns replay and comparison, configuration supplies fixed dependencies."; plannedCheck = "D,T: Independently replay in the declared host environment and compare under fixed tolerances."; operation = CandidateGY::C05::replay meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_10_L08 allocate FrameworkRequirements::FR_10 to candidate.L08;
    dependency operation_FR_10 from FrameworkRequirements::FR_10 to CandidateGY::C05::replay;
    #physicalPrimary allocation FR_11_primary allocate FrameworkRequirements::FR_11 to candidate.L07 {
        @PhysicalAllocation { rationale = "Python EPS/review assessments and generated baseline-linked views. Applicability and critical evidence gaps govern phase-product claims."; plannedCheck = "T: Seed every evidence status and attempt a current claim with a blocking gap."; operation = CandidateGY::C07::assessProduct meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_11_L06 allocate FrameworkRequirements::FR_11 to candidate.L06;
    #physicalSupport allocation FR_11_L08 allocate FrameworkRequirements::FR_11 to candidate.L08;
    dependency operation_FR_11 from FrameworkRequirements::FR_11 to CandidateGY::C07::assessProduct;
    #physicalPrimary allocation FR_12_primary allocate FrameworkRequirements::FR_12 to candidate.L04 {
        @PhysicalAllocation { rationale = "Typed YAML mission/EPS/interface definitions and Python calculations. BOM occurrences are the modeled design, distinct from component catalogue definitions."; plannedCheck = "A,T: Compare quantities and substitutions with a reference assembly."; operation = CandidateGY::C04::budgetSize meta SysML::ActionUsage; }
    }
    dependency operation_FR_12 from FrameworkRequirements::FR_12 to CandidateGY::C04::budgetSize;
    #physicalPrimary allocation FR_13_primary allocate FrameworkRequirements::FR_13 to candidate.L04 {
        @PhysicalAllocation { rationale = "Typed YAML mission/EPS/interface definitions and Python calculations. The same occurrence basis supports consistent dated resource and acquisition estimates."; plannedCheck = "A,T: Recalculate after a substitution and preserve unknown prices and availability."; operation = CandidateGY::C04::budgetSize meta SysML::ActionUsage; }
    }
    dependency operation_FR_13 from FrameworkRequirements::FR_13 to CandidateGY::C04::budgetSize;
    #physicalPrimary allocation FR_14_primary allocate FrameworkRequirements::FR_14 to candidate.L04 {
        @PhysicalAllocation { rationale = "Typed YAML mission/EPS/interface definitions and Python calculations. Mandatory supported feasibility precedes engineer preference ranking."; plannedCheck = "A,T: Use infeasible and closely ranked alternatives with uncertain inputs."; operation = CandidateGY::C04::compareDesigns meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_14_L06 allocate FrameworkRequirements::FR_14 to candidate.L06;
    dependency operation_FR_14 from FrameworkRequirements::FR_14 to CandidateGY::C04::compareDesigns;
    #physicalPrimary allocation FR_15_primary allocate FrameworkRequirements::FR_15 to candidate.L04 {
        @PhysicalAllocation { rationale = "Typed YAML mission/EPS/interface definitions and Python calculations. EPS variants and extensions remain coherent with design allocations."; plannedCheck = "I,D: Configure alternate EPS topologies and retain the distinct allocation and extension revisions."; operation = CandidateGY::C04::defineDesign meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_15_L03 allocate FrameworkRequirements::FR_15 to candidate.L03;
    dependency operation_FR_15 from FrameworkRequirements::FR_15 to CandidateGY::C04::defineDesign;
    #physicalPrimary allocation FR_16_primary allocate FrameworkRequirements::FR_16 to candidate.L05 {
        @PhysicalAllocation { rationale = "Python plans, specialist-model adapters and host work coordination. Coupled temporal composition and controlled tool execution realize mission-load/EPS analysis."; plannedCheck = "A,T: Use a temporal shortage hidden by an average power budget and check coupling against a reference."; operation = CandidateGY::C05::planAnalysis meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_16_L04 allocate FrameworkRequirements::FR_16 to candidate.L04;
    dependency operation_FR_16 from FrameworkRequirements::FR_16 to CandidateGY::C05::planAnalysis;
    #physicalPrimary allocation FR_17_primary allocate FrameworkRequirements::FR_17 to candidate.L03 {
        @PhysicalAllocation { rationale = "Typed YAML requirement records with Python links and allocation rules. Derivation connects spacecraft parents to EPS/component quantities and dispositions."; plannedCheck = "A,T: Recalculate an allocation and follow it to the parent and source quantities."; operation = CandidateGY::C03::deriveAllocate meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_17_L04 allocate FrameworkRequirements::FR_17 to candidate.L04;
    dependency operation_FR_17 from FrameworkRequirements::FR_17 to CandidateGY::C03::deriveAllocate;
    #physicalPrimary allocation FR_18_primary allocate FrameworkRequirements::FR_18 to candidate.L05 {
        @PhysicalAllocation { rationale = "Python plans, specialist-model adapters and host work coordination. Discipline execution profiles expose tool/version mappings and unsupported transfers."; plannedCheck = "D,T: Exercise each required discipline profile and incompatible mappings."; operation = CandidateGY::C05::planAnalysis meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_18_L01 allocate FrameworkRequirements::FR_18 to candidate.L01;
    #physicalSupport allocation FR_18_L04 allocate FrameworkRequirements::FR_18 to candidate.L04;
    dependency operation_FR_18 from FrameworkRequirements::FR_18 to CandidateGY::C05::planAnalysis;
    #physicalPrimary allocation FR_19_primary allocate FrameworkRequirements::FR_19 to candidate.L05 {
        @PhysicalAllocation { rationale = "Python plans, specialist-model adapters and host work coordination. Controlled MIL stimuli and responses follow the detailed design and assessment criteria."; plannedCheck = "D,T: Run declared nominal and fault sequences with a simulated plant and retain failed criteria."; operation = CandidateGY::C05::planMIL meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_19_L04 allocate FrameworkRequirements::FR_19 to candidate.L04;
    #physicalSupport allocation FR_19_L07 allocate FrameworkRequirements::FR_19 to candidate.L07;
    dependency operation_FR_19 from FrameworkRequirements::FR_19 to CandidateGY::C05::planMIL;
    #physicalPrimary allocation FR_20_primary allocate FrameworkRequirements::FR_20 to candidate.L04 {
        @PhysicalAllocation { rationale = "Typed YAML mission/EPS/interface definitions and Python calculations. Preliminary equations and margins belong with mission assumptions and candidate sizing."; plannedCheck = "A,T: Compare sizing and energy balance with independent calculations, including an infeasible eclipse case."; operation = CandidateGY::C04::budgetSize meta SysML::ActionUsage; }
    }
    dependency operation_FR_20 from FrameworkRequirements::FR_20 to CandidateGY::C04::budgetSize;
    #physicalPrimary allocation FR_21_primary allocate FrameworkRequirements::FR_21 to candidate.L06 {
        @PhysicalAllocation { rationale = "Python credibility and supplied-history assessment. Intended use, numerics, omissions and independent evidence bound model-supported conclusions."; plannedCheck = "I,T: Attempt conclusions outside validity and with missing independent evidence."; operation = CandidateGY::C06::assessModel meta SysML::ActionUsage; }
    }
    dependency operation_FR_21 from FrameworkRequirements::FR_21 to CandidateGY::C06::assessModel;
    #physicalPrimary allocation FR_22_primary allocate FrameworkRequirements::FR_22 to candidate.L06 {
        @PhysicalAllocation { rationale = "Python credibility and supplied-history assessment. Calibration proposals preserve prior values and independent assessment separation."; plannedCheck = "A,T: Calibrate from supplied data, retain separate assessment data and decline an update."; operation = CandidateGY::C06::proposeCalibration meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_22_L08 allocate FrameworkRequirements::FR_22 to candidate.L08;
    dependency operation_FR_22 from FrameworkRequirements::FR_22 to CandidateGY::C06::proposeCalibration;
    #physicalPrimary allocation FR_23_primary allocate FrameworkRequirements::FR_23 to candidate.L05 {
        @PhysicalAllocation { rationale = "Python plans, specialist-model adapters and host work coordination. Every execution plan retains solver/coupling/resource settings, later joined to measured results."; plannedCheck = "I,T: Change the time step, solver and resource limits and inspect the run configuration and findings."; operation = CandidateGY::C05::planAnalysis meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_23_L08 allocate FrameworkRequirements::FR_23 to candidate.L08;
    dependency operation_FR_23 from FrameworkRequirements::FR_23 to CandidateGY::C05::planAnalysis;
    #physicalPrimary allocation FR_24_primary allocate FrameworkRequirements::FR_24 to candidate.L05 {
        @PhysicalAllocation { rationale = "Python plans, specialist-model adapters and host work coordination. Corresponding declared host SIL and MIL scenarios support meaningful differences."; plannedCheck = "A,T: Use matching MIL/SIL inputs and a seeded code/interface discrepancy."; operation = CandidateGY::C05::compareMILSil meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_24_L06 allocate FrameworkRequirements::FR_24 to candidate.L06;
    #physicalSupport allocation FR_24_L07 allocate FrameworkRequirements::FR_24 to candidate.L07;
    dependency operation_FR_24 from FrameworkRequirements::FR_24 to CandidateGY::C05::compareMILSil;
    #physicalPrimary allocation FR_25_primary allocate FrameworkRequirements::FR_25 to candidate.L04 {
        @PhysicalAllocation { rationale = "Typed YAML mission/EPS/interface definitions and Python calculations. Mission and degraded ConOps revisions supply the common design and analysis basis."; plannedCheck = "I,T: Revise a degraded mode and trace its requirement and analysis inputs."; operation = CandidateGY::C04::defineDesign meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_25_L03 allocate FrameworkRequirements::FR_25 to candidate.L03;
    dependency operation_FR_25 from FrameworkRequirements::FR_25 to CandidateGY::C04::defineDesign;
    #physicalPrimary allocation FR_26_primary allocate FrameworkRequirements::FR_26 to candidate.L05 {
        @PhysicalAllocation { rationale = "Python plans, specialist-model adapters and host work coordination. RAM applicability follows requirements, ConOps, risks and justified exclusions."; plannedCheck = "I,T: Assess applicability with and without repair or redundancy assumptions."; operation = CandidateGY::C05::planAnalysis meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_26_L02 allocate FrameworkRequirements::FR_26 to candidate.L02;
    dependency operation_FR_26 from FrameworkRequirements::FR_26 to CandidateGY::C05::planAnalysis;
    #physicalPrimary allocation FR_27_primary allocate FrameworkRequirements::FR_27 to candidate.L05 {
        @PhysicalAllocation { rationale = "Python plans, specialist-model adapters and host work coordination. Selected RAM transformations follow design failure dependencies without invented rates."; plannedCheck = "A,T: Compare transformations and results with a reference and leave missing rates unresolved."; operation = CandidateGY::C05::planAnalysis meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_27_L04 allocate FrameworkRequirements::FR_27 to candidate.L04;
    dependency operation_FR_27 from FrameworkRequirements::FR_27 to CandidateGY::C05::planAnalysis;
    #physicalPrimary allocation FR_28_primary allocate FrameworkRequirements::FR_28 to candidate.L07 {
        @PhysicalAllocation { rationale = "Python EPS/review assessments and generated baseline-linked views. Verification requirements and validation expectations need distinct phase-product plans."; plannedCheck = "I,T: Distinguish planned activities from results and verification criteria from validation expectations."; operation = CandidateGY::C07::planAssessment meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_28_L03 allocate FrameworkRequirements::FR_28 to candidate.L03;
    dependency operation_FR_28 from FrameworkRequirements::FR_28 to CandidateGY::C07::planAssessment;
    #physicalPrimary allocation FR_29_primary allocate FrameworkRequirements::FR_29 to candidate.L02 {
        @PhysicalAllocation { rationale = "Local Python active assistance with pinned Qwen/BM25. All assistance dispositions retain human authority and exact suggestion/context identity."; plannedCheck = "I,T: Exercise all dispositions and an unauthorized attempt to apply a suggestion."; operation = CandidateGY::C02::dispose meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_29_L01 allocate FrameworkRequirements::FR_29 to candidate.L01;
    #physicalSupport allocation FR_29_L08 allocate FrameworkRequirements::FR_29 to candidate.L08;
    dependency operation_FR_29 from FrameworkRequirements::FR_29 to CandidateGY::C02::dispose;
    #physicalPrimary allocation FR_30_primary allocate FrameworkRequirements::FR_30 to candidate.L08 {
        @PhysicalAllocation { rationale = "Git-reviewed text definitions, managed archive and Python revision/impact index. Revision and pending-work currency require immediate invalidation and delayed-response checks."; plannedCheck = "T: Edit during a delayed response and check that the old response cannot replace current guidance."; operation = CandidateGY::C08::invalidate meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_30_L02 allocate FrameworkRequirements::FR_30 to candidate.L02;
    dependency operation_FR_30 from FrameworkRequirements::FR_30 to CandidateGY::C08::invalidate;
    #physicalPrimary allocation FR_31_primary allocate FrameworkRequirements::FR_31 to candidate.L06 {
        @PhysicalAllocation { rationale = "Python credibility and supplied-history assessment. History comparison needs explicit sample/receipt time bases and known delays."; plannedCheck = "A,T: Compare aligned and skewed histories with declared time tolerances."; operation = CandidateGY::C06::assessModel meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_31_L05 allocate FrameworkRequirements::FR_31 to candidate.L05;
    dependency operation_FR_31 from FrameworkRequirements::FR_31 to CandidateGY::C06::assessModel;
    #physicalPrimary allocation FR_32_primary allocate FrameworkRequirements::FR_32 to candidate.L06 {
        @PhysicalAllocation { rationale = "Python credibility and supplied-history assessment. History validity and masks must preserve missing/inactive values rather than zero filling."; plannedCheck = "T: Inject missing, inactive, invalid and wrong-unit data and compare masks."; operation = CandidateGY::C06::assessModel meta SysML::ActionUsage; }
    }
    dependency operation_FR_32 from FrameworkRequirements::FR_32 to CandidateGY::C06::assessModel;
    #physicalPrimary allocation FR_33_primary allocate FrameworkRequirements::FR_33 to candidate.L04 {
        @PhysicalAllocation { rationale = "Typed YAML mission/EPS/interface definitions and Python calculations. Detailed interface meaning and ownership belong to the modeled EPS design."; plannedCheck = "I,T: Round-trip interface definitions and reject inconsistent endpoint meanings."; operation = CandidateGY::C04::defineInterfaces meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_33_L03 allocate FrameworkRequirements::FR_33 to candidate.L03;
    dependency operation_FR_33 from FrameworkRequirements::FR_33 to CandidateGY::C04::defineInterfaces;
    #physicalPrimary allocation FR_34_primary allocate FrameworkRequirements::FR_34 to candidate.L04 {
        @PhysicalAllocation { rationale = "Typed YAML mission/EPS/interface definitions and Python calculations. Engineer-selected integration mappings preserve detailed interface meanings and version gaps."; plannedCheck = "D,T: Check a selected profile and expose omitted or incompatible meanings."; operation = CandidateGY::C04::defineInterfaces meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_34_L05 allocate FrameworkRequirements::FR_34 to candidate.L05;
    dependency operation_FR_34 from FrameworkRequirements::FR_34 to CandidateGY::C04::defineInterfaces;
    #physicalPrimary allocation FR_35_primary allocate FrameworkRequirements::FR_35 to candidate.L04 {
        @PhysicalAllocation { rationale = "Typed YAML mission/EPS/interface definitions and Python calculations. Control preconditions/effects/recovery are detailed design responsibilities checked in simulation."; plannedCheck = "A,T: Exercise nominal, rejected, protection and recovery sequences in simulated conditions."; operation = CandidateGY::C04::defineInterfaces meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_35_L05 allocate FrameworkRequirements::FR_35 to candidate.L05;
    dependency operation_FR_35 from FrameworkRequirements::FR_35 to CandidateGY::C04::defineInterfaces;
    #physicalPrimary allocation FR_36_primary allocate FrameworkRequirements::FR_36 to candidate.L05 {
        @PhysicalAllocation { rationale = "Python plans, specialist-model adapters and host work coordination. External host coordination is gated by a current specific detailed-design authorization."; plannedCheck = "D,T: Attempt an unreleased build and then build the released design, including a toolchain failure."; operation = CandidateGY::C05::coordinateCoding meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_36_L08 allocate FrameworkRequirements::FR_36 to candidate.L08;
    dependency operation_FR_36 from FrameworkRequirements::FR_36 to CandidateGY::C05::coordinateCoding;
    #physicalPrimary allocation FR_37_primary allocate FrameworkRequirements::FR_37 to candidate.L01 {
        @PhysicalAllocation { rationale = "Editor/Python panel and generated engineering/review documents. User-facing views derive from controlled records and never define an independent baseline."; plannedCheck = "I,D: Compare views with their source baseline and follow represented record links."; operation = CandidateGY::C01::makeViews meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_37_L08 allocate FrameworkRequirements::FR_37 to candidate.L08;
    dependency operation_FR_37 from FrameworkRequirements::FR_37 to CandidateGY::C01::makeViews;
    #physicalPrimary allocation FR_38_primary allocate FrameworkRequirements::FR_38 to candidate.L07 {
        @PhysicalAllocation { rationale = "Python EPS/review assessments and generated baseline-linked views. Scoped entrance/success evidence needs coherent phase-product assessment, not automatic acceptance."; plannedCheck = "I,D: Prepare phase-specific packages, including CDR design release and SIR released-product evidence."; operation = CandidateGY::C07::prepareReview meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_38_L01 allocate FrameworkRequirements::FR_38 to candidate.L01;
    #physicalSupport allocation FR_38_L08 allocate FrameworkRequirements::FR_38 to candidate.L08;
    dependency operation_FR_38 from FrameworkRequirements::FR_38 to CandidateGY::C07::prepareReview;
    #physicalPrimary allocation FR_39_primary allocate FrameworkRequirements::FR_39 to candidate.L02 {
        @PhysicalAllocation { rationale = "Local Python active assistance with pinned Qwen/BM25. Activity advice uses maturity, dependencies, findings and review prerequisites."; plannedCheck = "A,D: Change maturity and blocking findings and inspect the revised activity proposals."; operation = CandidateGY::C02::recommend meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_39_L07 allocate FrameworkRequirements::FR_39 to candidate.L07;
    #physicalSupport allocation FR_39_L08 allocate FrameworkRequirements::FR_39 to candidate.L08;
    dependency operation_FR_39 from FrameworkRequirements::FR_39 to CandidateGY::C02::recommend;
    #physicalPrimary allocation FR_41_primary allocate FrameworkRequirements::FR_41 to candidate.L02 {
        @PhysicalAllocation { rationale = "Local Python active assistance with pinned Qwen/BM25. Interactive assistance owns trigger/response/completion status while infrastructure supplies time/context."; plannedCheck = "T: Measure response delay under the declared workload, including outage and superseded edits."; operation = CandidateGY::C02::acknowledge meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_41_L01 allocate FrameworkRequirements::FR_41 to candidate.L01;
    #physicalSupport allocation FR_41_L08 allocate FrameworkRequirements::FR_41 to candidate.L08;
    dependency operation_FR_41 from FrameworkRequirements::FR_41 to CandidateGY::C02::acknowledge;
    #physicalPrimary allocation FR_42_primary allocate FrameworkRequirements::FR_42 to candidate.L07 {
        @PhysicalAllocation { rationale = "Python EPS/review assessments and generated baseline-linked views. Only designated-authority current decisions change review disposition, separately from preparation."; plannedCheck = "I,T: Reject unauthorized or stale-baseline decisions and exercise blocking and conditional findings."; operation = CandidateGY::C07::recordReview meta SysML::ActionUsage; }
    }
    #physicalSupport allocation FR_42_L08 allocate FrameworkRequirements::FR_42 to candidate.L08;
    dependency operation_FR_42 from FrameworkRequirements::FR_42 to CandidateGY::C07::recordReview;
    // Allocation aliases index the performed candidate usages. They carry no control semantics.
    package LogicalRealization {
        alias AssistanceRealization for Configuration::assistance;
        alias ConceptRealization for Configuration::concept;
        alias DesignRealization for Configuration::designRun;
        alias SoftwareRealization for Configuration::software;
        alias ChangeReviewRealization for Configuration::changeReview;
        alias ReplayRealization for Configuration::replayRun;
        alias CalibrationRealization for Configuration::calibration;
    }
    allocate LogicalRealization::DesignRealization::execute to candidate.L05;
    allocate LogicalRealization::ConceptRealization::execute to candidate.L05;
    allocate LogicalRealization::SoftwareRealization::executeMIL to candidate.L05;
    allocate LogicalRealization::SoftwareRealization::codeBuildSil to candidate.L05;
    allocate LogicalRealization::ChangeReviewRealization::repeat to candidate.L05;
    allocate LogicalRealization::ReplayRealization::execute to candidate.L05;
    allocate LogicalRealization::CalibrationRealization::repeat to candidate.L05;
    allocate candidate.concept.execute.execute.models to candidate.models;
    allocate candidate.designRun.execute.execute.models to candidate.models;
    allocate candidate.software.executeMIL.execute.models to candidate.models;
    allocate candidate.software.codeBuildSil.execute to candidate.hostCode;
    allocate candidate.changeReview.repeat.execute.models to candidate.models;
    allocate candidate.replayRun.execute.execute.models to candidate.models;
    allocate candidate.calibration.repeat.execute.models to candidate.models;
    allocate candidate.concept.execute.execute.sil.execute to candidate.hostCode;
    allocate candidate.designRun.execute.execute.sil.execute to candidate.hostCode;
    allocate candidate.software.executeMIL.execute.sil.execute to candidate.hostCode;
    allocate candidate.changeReview.repeat.execute.sil.execute to candidate.hostCode;
    allocate candidate.replayRun.execute.execute.sil.execute to candidate.hostCode;
    allocate candidate.calibration.repeat.execute.sil.execute to candidate.hostCode;
    bind candidate.concept.execute.execute.models.endpoint = candidate.models.requests;
    bind candidate.designRun.execute.execute.models.endpoint = candidate.models.requests;
    bind candidate.software.executeMIL.execute.models.endpoint = candidate.models.requests;
    bind candidate.software.codeBuildSil.execute.endpoint = candidate.hostCode.requests;
    bind candidate.changeReview.repeat.execute.models.endpoint = candidate.models.requests;
    bind candidate.replayRun.execute.execute.models.endpoint = candidate.models.requests;
    bind candidate.calibration.repeat.execute.models.endpoint = candidate.models.requests;
    bind candidate.concept.execute.execute.sil.execute.endpoint = candidate.hostCode.requests;
    bind candidate.designRun.execute.execute.sil.execute.endpoint = candidate.hostCode.requests;
    bind candidate.software.executeMIL.execute.sil.execute.endpoint = candidate.hostCode.requests;
    bind candidate.changeReview.repeat.execute.sil.execute.endpoint = candidate.hostCode.requests;
    bind candidate.replayRun.execute.execute.sil.execute.endpoint = candidate.hostCode.requests;
    bind candidate.calibration.repeat.execute.sil.execute.endpoint = candidate.hostCode.requests;
    allocate LogicalRealization::AssistanceRealization::receive to candidate.L01;
    allocate LogicalRealization::AssistanceRealization::capture to candidate.L08;
    allocate LogicalRealization::AssistanceRealization::invalidateOnEdit to candidate.L08;
    allocate LogicalRealization::AssistanceRealization::acknowledge to candidate.L02;
    allocate LogicalRealization::AssistanceRealization::retainDraft to candidate.L03;
    allocate LogicalRealization::AssistanceRealization::checkDraft to candidate.L02;
    allocate LogicalRealization::AssistanceRealization::recommend to candidate.L02;
    allocate LogicalRealization::AssistanceRealization::checkReply to candidate.L08;
    allocate LogicalRealization::AssistanceRealization::present to candidate.L01;
    allocate LogicalRealization::AssistanceRealization::dispose to candidate.L02;
    allocate LogicalRealization::AssistanceRealization::checkApplication to candidate.L08;
    allocate LogicalRealization::AssistanceRealization::derive to candidate.L03;
    allocate LogicalRealization::AssistanceRealization::trace to candidate.L03;
    allocate LogicalRealization::AssistanceRealization::retainValidation to candidate.L08;
    allocate LogicalRealization::AssistanceRealization::retainDisposition to candidate.L08;
    allocate LogicalRealization::AssistanceRealization::invalidate to candidate.L08;
    allocate LogicalRealization::AssistanceRealization::reassess to candidate.L02;
    allocate LogicalRealization::AssistanceRealization::rejectTransfer to candidate.L08;
    allocate LogicalRealization::AssistanceRealization::rejectDisposition to candidate.L08;
    allocate LogicalRealization::DesignRealization::receive to candidate.L01;
    allocate LogicalRealization::DesignRealization::configure to candidate.L04;
    allocate LogicalRealization::DesignRealization::budget to candidate.L04;
    allocate LogicalRealization::DesignRealization::planCriteria to candidate.L07;
    allocate LogicalRealization::DesignRealization::plan to candidate.L05;
    allocate LogicalRealization::DesignRealization::receiveResult to candidate.L01;
    allocate LogicalRealization::DesignRealization::preserve to candidate.L08;
    allocate LogicalRealization::DesignRealization::checkCurrent to candidate.L08;
    allocate LogicalRealization::DesignRealization::credibility to candidate.L06;
    allocate LogicalRealization::DesignRealization::assess to candidate.L07;
    allocate LogicalRealization::DesignRealization::compare to candidate.L04;
    allocate LogicalRealization::DesignRealization::checkSelection to candidate.L08;
    allocate LogicalRealization::DesignRealization::retainSelection to candidate.L08;
    allocate LogicalRealization::DesignRealization::retainGaps to candidate.L08;
    allocate LogicalRealization::ConceptRealization::receive to candidate.L01;
    allocate LogicalRealization::ConceptRealization::configure to candidate.L04;
    allocate LogicalRealization::ConceptRealization::budget to candidate.L04;
    allocate LogicalRealization::ConceptRealization::planCriteria to candidate.L07;
    allocate LogicalRealization::ConceptRealization::plan to candidate.L05;
    allocate LogicalRealization::ConceptRealization::receiveResult to candidate.L01;
    allocate LogicalRealization::ConceptRealization::preserve to candidate.L08;
    allocate LogicalRealization::ConceptRealization::checkCurrent to candidate.L08;
    allocate LogicalRealization::ConceptRealization::credibility to candidate.L06;
    allocate LogicalRealization::ConceptRealization::assess to candidate.L07;
    allocate LogicalRealization::ConceptRealization::compare to candidate.L04;
    allocate LogicalRealization::ConceptRealization::checkSelection to candidate.L08;
    allocate LogicalRealization::ConceptRealization::retainSelection to candidate.L08;
    allocate LogicalRealization::ConceptRealization::retainGaps to candidate.L08;
    allocate LogicalRealization::ConceptRealization::makeConfiguration to candidate.L04;
    allocate LogicalRealization::SoftwareRealization::receive to candidate.L01;
    allocate LogicalRealization::SoftwareRealization::interfaces to candidate.L04;
    allocate LogicalRealization::SoftwareRealization::planCriteria to candidate.L07;
    allocate LogicalRealization::SoftwareRealization::planMIL to candidate.L05;
    allocate LogicalRealization::SoftwareRealization::receiveMIL to candidate.L01;
    allocate LogicalRealization::SoftwareRealization::preserveMIL to candidate.L08;
    allocate LogicalRealization::SoftwareRealization::assessMIL to candidate.L06;
    allocate LogicalRealization::SoftwareRealization::checkRelease to candidate.L08;
    allocate LogicalRealization::SoftwareRealization::coordinate to candidate.L05;
    allocate LogicalRealization::SoftwareRealization::receiveSIL to candidate.L01;
    allocate LogicalRealization::SoftwareRealization::preserveSIL to candidate.L08;
    allocate LogicalRealization::SoftwareRealization::checkCurrent to candidate.L08;
    allocate LogicalRealization::SoftwareRealization::compare to candidate.L05;
    allocate LogicalRealization::SoftwareRealization::credibility to candidate.L06;
    allocate LogicalRealization::SoftwareRealization::assess to candidate.L07;
    allocate LogicalRealization::SoftwareRealization::present to candidate.L01;
    allocate LogicalRealization::SoftwareRealization::checkProducts to candidate.L08;
    allocate LogicalRealization::SoftwareRealization::retainProducts to candidate.L08;
    allocate LogicalRealization::SoftwareRealization::block to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::receive to candidate.L01;
    allocate LogicalRealization::ChangeReviewRealization::invalidate to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::checkChange to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::successor to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::reassessAdvice to candidate.L02;
    allocate LogicalRealization::ChangeReviewRealization::planRepeat to candidate.L05;
    allocate LogicalRealization::ChangeReviewRealization::receiveResult to candidate.L01;
    allocate LogicalRealization::ChangeReviewRealization::preserve to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::credibility to candidate.L06;
    allocate LogicalRealization::ChangeReviewRealization::retrieve to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::assess to candidate.L07;
    allocate LogicalRealization::ChangeReviewRealization::views to candidate.L01;
    allocate LogicalRealization::ChangeReviewRealization::prepare to candidate.L07;
    allocate LogicalRealization::ChangeReviewRealization::checkBaseline to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::checkDecision to candidate.L07;
    allocate LogicalRealization::ChangeReviewRealization::record to candidate.L07;
    allocate LogicalRealization::ChangeReviewRealization::retain to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::holdChange to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::holdReview to candidate.L08;
    allocate LogicalRealization::ChangeReviewRealization::rejectReview to candidate.L08;
    allocate LogicalRealization::ReplayRealization::prepare to candidate.L08;
    allocate LogicalRealization::ReplayRealization::receive to candidate.L01;
    allocate LogicalRealization::ReplayRealization::preserve to candidate.L08;
    allocate LogicalRealization::ReplayRealization::compare to candidate.L05;
    allocate LogicalRealization::ReplayRealization::retain to candidate.L08;
    allocate LogicalRealization::ReplayRealization::missing to candidate.L08;
    allocate LogicalRealization::CalibrationRealization::receive to candidate.L01;
    allocate LogicalRealization::CalibrationRealization::checkData to candidate.L06;
    allocate LogicalRealization::CalibrationRealization::propose to candidate.L06;
    allocate LogicalRealization::CalibrationRealization::prepareChange to candidate.L08;
    allocate LogicalRealization::CalibrationRealization::invalidate to candidate.L08;
    allocate LogicalRealization::CalibrationRealization::checkChange to candidate.L08;
    allocate LogicalRealization::CalibrationRealization::successor to candidate.L08;
    allocate LogicalRealization::CalibrationRealization::reassess to candidate.L02;
    allocate LogicalRealization::CalibrationRealization::planRepeat to candidate.L05;
    allocate LogicalRealization::CalibrationRealization::receiveResult to candidate.L01;
    allocate LogicalRealization::CalibrationRealization::preserve to candidate.L08;
    allocate LogicalRealization::CalibrationRealization::credibility to candidate.L06;
    allocate LogicalRealization::CalibrationRealization::assess to candidate.L07;
    allocate LogicalRealization::CalibrationRealization::retainEvidence to candidate.L08;
    allocate LogicalRealization::CalibrationRealization::retain to candidate.L08;
    allocate LogicalRealization::CalibrationRealization::unusable to candidate.L08;
    allocate candidate.L02.checkDraft.pipeline.rules to candidate.L02.rules;
    allocate candidate.L02.checkDraft.pipeline.sources to candidate.L02.localScoring;
    allocate candidate.L02.checkDraft.pipeline.retrieve to candidate.L02.localScoring;
    allocate candidate.L02.checkDraft.pipeline.scores to candidate.L02;
    allocate candidate.L02.checkDraft.pipeline.applicability to candidate.L02;
    allocate candidate.L02.checkDraft.pipeline.explain to candidate.L02.explanation;
    allocate candidate.L02.checkDraft.pipeline.none to candidate.L02.explanation;
    allocate candidate.L02.checkDraft.pipeline.currency to candidate.L08;
    allocate candidate.L02.checkDraft.pipeline.publish to candidate.L01;
    allocate candidate.L02.checkDraft.pipeline.stale to candidate.L08;
    allocate candidate.L02.recommend.pipeline.rules to candidate.L02.rules;
    allocate candidate.L02.recommend.pipeline.sources to candidate.L02.localScoring;
    allocate candidate.L02.recommend.pipeline.retrieve to candidate.L02.localScoring;
    allocate candidate.L02.recommend.pipeline.scores to candidate.L02;
    allocate candidate.L02.recommend.pipeline.applicability to candidate.L02;
    allocate candidate.L02.recommend.pipeline.explain to candidate.L02.explanation;
    allocate candidate.L02.recommend.pipeline.none to candidate.L02.explanation;
    allocate candidate.L02.recommend.pipeline.currency to candidate.L08;
    allocate candidate.L02.recommend.pipeline.publish to candidate.L01;
    allocate candidate.L02.recommend.pipeline.stale to candidate.L08;
    allocate candidate.concept.execute.profiles to candidate.L05;
    allocate candidate.designRun.execute.profiles to candidate.L05;
    allocate candidate.software.executeMIL.profiles to candidate.L05;
    allocate candidate.software.codeBuildSil.profiles to candidate.L05;
    allocate candidate.changeReview.repeat.profiles to candidate.L05;
    allocate candidate.replayRun.execute.profiles to candidate.L05;
    allocate candidate.calibration.repeat.profiles to candidate.L05;
}
