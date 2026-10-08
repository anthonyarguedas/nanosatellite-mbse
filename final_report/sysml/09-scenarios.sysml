// Native mission scenarios, typed exchanges and controlled framework behavior.
// Framework actions are blue ActionUsage. External human/tool actions are amber PerformActionUsage.
package ScenarioViews {
    private import ScalarValues::*;
    private import FrameworkDomain::*;
    private import BoundaryViews::*;
    private import StandardViewDefinitions::*;
    ref part framework : ToBe::FutureFramework = FrameworkContext::context.framework;
    ref part systemsEngineer : SystemsEngineer = FrameworkContext::context.engineers.systems;
    ref part epsEngineer : EPSEngineer = FrameworkContext::context.engineers.eps;
    ref part analysisTools : FrameworkContext::Engines = FrameworkContext::context.tools;
    ref part hostToolchain : FrameworkContext::Software = FrameworkContext::context.software;
    ref part reviewers : IndependentReviewer = FrameworkContext::context.reviewers.independent;
    ref part reviewAuthority : TechnicalReviewAuthority = FrameworkContext::context.reviewers.authority;
    metadata def FrameworkAction { :>> annotatedElement : SysML::ActionUsage; ref performer : SysML::PartUsage; ref function : SysML::ActionDefinition; attribute fillColor : String; }
    metadata def ExternalAction { :>> annotatedElement : SysML::PerformActionUsage; ref performer : SysML::PartUsage; attribute fillColor : String; }
    metadata def MissionScenario { attribute useCase : String; attribute title : String; }
    doc /* Full SC01--05 specify primary, alternative, stressing and failure behavior at the future framework boundary. SC05 is invoked for reviews and controlled changes in SC01--04. Compact native report summaries expose their main interaction stages. Exact actor/action responsibility, typed information and exceptions remain in the full scenarios. No implementation or executed framework V&V is asserted. */
    action def SC01External1 { out item mission : MissionDefinition; doc /* Agree expectations and constraints with mission stakeholders and non-EPS engineers. Submit nominal/degraded ConOps, orbit, attitude, environment, duration and modes/loads. Sparse properties remain assumptions. */ }
    action def SC01External3 { in item plan : AnalysisPlan; out item result : AnalysisResult; doc /* Execute the declared model analysis in its identified host environment. Return raw outputs, versions, runtime, logs and failures. A missing profile or input returns a failed/partial result, not a feasible conclusion. */ }
    action def SC01External5 { in item study : DesignStudy; out item decision : EngineeringDecision; out attribute accepted : Boolean; doc /* Review feasibility with stakeholders and EPS/non-EPS engineers. Choose, revise, decline or defer a concept with rationale. accepted means an authorized engineer selected a supported concept. It is not an MCR progression decision. */ }
    action def <'SC01'> SC01 {
        @MissionScenario { useCase = "UC01"; title = "Establish a feasible EPS mission concept"; }
        doc /* Establish a feasible EPS mission concept. The output is controlled phase products or explicit open findings. Review acceptance is a separate authorized decision through SC05. */
        perform action 'SE: define mission' : SC01External1 { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: plan concepts' { in item mission : MissionDefinition; out item plan : AnalysisPlan; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F03 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Configure candidate generation/storage/distribution representations. F01 recommends concept methods from available data and maturity. Calculate initial budgets and sizing and identify uncertain parameters. Form a common concept-analysis plan from engineer-approved scope and criteria. */ }
        perform action 'Tool: analyze concepts' : SC01External3 { @ExternalAction { performer = analysisTools meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: assess feasibility' { in item result : AnalysisResult; out item study : DesignStudy; out attribute usable : Boolean; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F03 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Compare concept budgets, energy margins, constraints and uncertainty. F04 checks model applicability. usable requires the inputs and supported results needed by the declared feasibility question. Missing data, impossible energy balance or uncertain close alternatives remain explicit. */ }
        perform action 'SE: choose concept' : SC01External5 { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: retain concept' { in item decision : EngineeringDecision; out item product : DesignConfiguration; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Retain the selected concept, ConOps, budgets, decisions and evidence as controlled proposed phase products. F08 prepares views for MCR. SC05 records the separate authorized review decision. */ }
        action 'FW: keep concept open' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Retain assumptions, missing sources, infeasible constraints, partial results and the declined/deferred decision. Request corrected mission inputs or further evidence. No feasible concept or review acceptance is invented. */ }
        attribute usable : Boolean = 'FW: assess feasibility'.usable;
        attribute accepted : Boolean = 'SE: choose concept'.accepted;
        decide 'Proceed?';
        merge 'Complete';
        first start then 'SE: define mission';
        first 'SE: define mission' then 'FW: plan concepts';
        first 'FW: plan concepts' then 'Tool: analyze concepts';
        first 'Tool: analyze concepts' then 'FW: assess feasibility';
        first 'FW: assess feasibility' then 'SE: choose concept';
        first 'SE: choose concept' then 'Proceed?';
        succession proceed first 'Proceed?' if usable and accepted then 'FW: retain concept' {
            succession '[usable and accepted]' [0..1] first 'Proceed?' then 'FW: retain concept';
            bind '[usable and accepted]' = transitionLink;
        }
        succession hold first 'Proceed?' if not (usable and accepted) then 'FW: keep concept open' {
            succession '[not (usable and accepted)]' [0..1] first 'Proceed?' then 'FW: keep concept open';
            bind '[not (usable and accepted)]' = transitionLink;
        }
        flow exchange1 of MissionDefinition from 'SE: define mission'.mission to 'FW: plan concepts'.mission;
        flow exchange2 of AnalysisPlan from 'FW: plan concepts'.plan to 'Tool: analyze concepts'.plan;
        flow exchange3 of AnalysisResult from 'Tool: analyze concepts'.result to 'FW: assess feasibility'.result;
        flow exchange4 of DesignStudy from 'FW: assess feasibility'.study to 'SE: choose concept'.study;
        flow exchange5 of EngineeringDecision from 'SE: choose concept'.decision to 'FW: retain concept'.decision;
        first 'FW: retain concept' then 'Complete';
        first 'FW: keep concept open' then 'Complete';
        first 'Complete' then done;
    }
    allocate SC01::'SE: define mission' to systemsEngineer;
    allocate SC01::'FW: plan concepts' to framework;
    allocate SC01::'Tool: analyze concepts' to analysisTools;
    allocate SC01::'FW: assess feasibility' to framework;
    allocate SC01::'SE: choose concept' to systemsEngineer;
    allocate SC01::'FW: retain concept' to framework;
    allocate SC01::'FW: keep concept open' to framework;
    #sourceTrace dependency scenario_UC01 from SC01 to FrameworkNeeds::UC01;
    #proposedDerivation dependency scenario_SC01_MR01 from SC01 to FrameworkNeeds::MR_01;
    #sourceTrace dependency review_SC01 from SC01 to SC05;
    action def SC01Summary {
        doc /* Main interaction summary of SC01. Coordinated tool work and alternative/failure paths are specified by the full scenario and report prose. */
        action def 'Submit';
        perform action 'SE: define mission' : 'Submit' { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep0 from 'SE: define mission' to SC01::'SE: define mission';
        action 'FW: plan concepts' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F03 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } }
        #sourceTrace dependency summaryStep1 from 'FW: plan concepts' to SC01::'FW: plan concepts';
        action def 'Decide';
        perform action 'SE: choose concept' : 'Decide' { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep2 from 'SE: choose concept' to SC01::'SE: choose concept';
        first start then 'SE: define mission';
        first 'SE: define mission' then 'FW: plan concepts';
        first 'FW: plan concepts' then 'SE: choose concept';
        first 'SE: choose concept' then done;
    }
    allocate SC01Summary::'SE: define mission' to systemsEngineer;
    allocate SC01Summary::'FW: plan concepts' to framework;
    allocate SC01Summary::'SE: choose concept' to systemsEngineer;
    #sourceTrace dependency summary_SC01 from SC01Summary to SC01;
    view sc01View : ActionFlowView {
        expose SC01Summary::**;
        filter @SysML::ActionUsage or @SysML::SuccessionAsUsage;
        attribute depth = -1;
        attribute showInheritedRows = false;
        attribute showAnnotationRows = false;
    }
    action def SC02External1 { out item submission : EngineeringSubmission; doc /* Submit new or edited EPS/component drafts, parent spacecraft requirements, mission scenarios, interfaces and the current question/context revision. Engineers define criteria and source authority. */ }
    action def SC02External3 { in item response : EngineeringResponse; out item submission : EngineeringSubmission; out attribute authorized : Boolean; doc /* Accept, modify, reject or defer each suggestion with rationale. Approve proposed requirement/criterion changes only within the assigned engineering authority. A suggestion or similarity score establishes no technical correctness. */ }
    action def SC02External5 { in item reviewPackage : ReviewPackage; out item findings : ReviewSubmission; out attribute resolved : Boolean; doc /* Independently assess correctness, feasibility, verifiability, uniqueness and consistency with stakeholder expectations and ConOps. Report unresolved findings. resolved means all blocking requirement-validation findings are dispositioned. SRR progression belongs to the authority through SC05. */ }
    action def <'SC02'> SC02 {
        @MissionScenario { useCase = "UC02"; title = "Define and validate EPS requirements and interfaces"; }
        doc /* Define and validate EPS requirements and interfaces. The output is controlled phase products or explicit open findings. UC02 is reused for requirement refinement through detailed design. Review acceptance is a separate authorized decision through SC05. */
        perform action 'SE: edit requirements' : SC02External1 { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: check and recommend' { in item submission : EngineeringSubmission; out item response : EngineeringResponse; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F02 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Check deterministic identifiers, required fields, responsible product, single shall, units and declared limits against NASA Appendix C plus the expert-approved project reference. Flag probable semantic duplicates by subject, level, mode, conditions and quantity. Compare declared scenarios, functions, interfaces and risks for probable gaps and sources for conflicts. Explain each rule/passage and corrective suggestion, uncertainty and unassessed scope. F01 recommends applicable derivation/V&V methods and alternatives. Record delay and context revisions. New edits invalidate guidance before a late response can become current. */ }
        perform action 'SE: dispose suggestions' : SC02External3 { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: derive and allocate' { in item submission : EngineeringSubmission; out item reviewPackage : ReviewPackage; out attribute current : Boolean; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F02 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Apply authorized current revisions, derive limits by the chosen method and allocate from spacecraft to EPS and components. Retain assumptions, verification criteria and reverse links. current is false for a changed context, stale suggestion or unresolved allocation/source conflict. F08 prepares the requirement/interface review package. */ }
        perform action 'Reviewer: validate requirements' : SC02External5 { @ExternalAction { performer = reviewers meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: retain requirements' { in item findings : ReviewSubmission; out item records : EngineeringResponse; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Retain approved requirements, interfaces, allocations, methods and validation findings with their exact context and engineer dispositions. Keep technical review status prepared until SC05 receives an authorized decision. */ }
        action 'FW: retain draft findings' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Retain stale or unsupported assistance, source conflicts, probable defects and pending dispositions. Trigger reassessment after edits. Keep drafts unresolved and preserve controlled predecessors. Report unavailable checks distinctly from no finding. */ }
        attribute current : Boolean = 'FW: derive and allocate'.current;
        attribute authorized : Boolean = 'SE: dispose suggestions'.authorized;
        attribute resolved : Boolean = 'Reviewer: validate requirements'.resolved;
        decide 'Proceed?';
        merge 'Complete';
        first start then 'SE: edit requirements';
        first 'SE: edit requirements' then 'FW: check and recommend';
        first 'FW: check and recommend' then 'SE: dispose suggestions';
        first 'SE: dispose suggestions' then 'FW: derive and allocate';
        first 'FW: derive and allocate' then 'Reviewer: validate requirements';
        first 'Reviewer: validate requirements' then 'Proceed?';
        succession proceed first 'Proceed?' if current and authorized and resolved then 'FW: retain requirements' {
            succession '[current and authorized and resolved]' [0..1] first 'Proceed?' then 'FW: retain requirements';
            bind '[current and authorized and resolved]' = transitionLink;
        }
        succession hold first 'Proceed?' if not (current and authorized and resolved) then 'FW: retain draft findings' {
            succession '[not (current and authorized and resolved)]' [0..1] first 'Proceed?' then 'FW: retain draft findings';
            bind '[not (current and authorized and resolved)]' = transitionLink;
        }
        flow exchange1 of EngineeringSubmission from 'SE: edit requirements'.submission to 'FW: check and recommend'.submission;
        flow exchange2 of EngineeringResponse from 'FW: check and recommend'.response to 'SE: dispose suggestions'.response;
        flow exchange3 of EngineeringSubmission from 'SE: dispose suggestions'.submission to 'FW: derive and allocate'.submission;
        flow exchange4 of ReviewPackage from 'FW: derive and allocate'.reviewPackage to 'Reviewer: validate requirements'.reviewPackage;
        flow exchange5 of ReviewSubmission from 'Reviewer: validate requirements'.findings to 'FW: retain requirements'.findings;
        first 'FW: retain requirements' then 'Complete';
        first 'FW: retain draft findings' then 'Complete';
        first 'Complete' then done;
    }
    allocate SC02::'SE: edit requirements' to systemsEngineer;
    allocate SC02::'FW: check and recommend' to framework;
    allocate SC02::'SE: dispose suggestions' to systemsEngineer;
    allocate SC02::'FW: derive and allocate' to framework;
    allocate SC02::'Reviewer: validate requirements' to reviewers;
    allocate SC02::'FW: retain requirements' to framework;
    allocate SC02::'FW: retain draft findings' to framework;
    #sourceTrace dependency scenario_UC02 from SC02 to FrameworkNeeds::UC02;
    #proposedDerivation dependency scenario_SC02_MR02 from SC02 to FrameworkNeeds::MR_02;
    #proposedDerivation dependency scenario_SC02_MR03 from SC02 to FrameworkNeeds::MR_03;
    #proposedDerivation dependency scenario_SC02_MR04 from SC02 to FrameworkNeeds::MR_04;
    #proposedDerivation dependency scenario_SC02_MR05 from SC02 to FrameworkNeeds::MR_05;
    #sourceTrace dependency review_SC02 from SC02 to SC05;
    action def SC02Summary {
        doc /* Main interaction summary of SC02. Coordinated tool work and alternative/failure paths are specified by the full scenario and report prose. */
        action def 'Submit';
        perform action 'SE: edit requirements' : 'Submit' { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep0 from 'SE: edit requirements' to SC02::'SE: edit requirements';
        action 'FW: check and recommend' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F02 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } }
        #sourceTrace dependency summaryStep1 from 'FW: check and recommend' to SC02::'FW: check and recommend';
        action def 'Decide';
        perform action 'SE: dispose suggestions' : 'Decide' { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep2 from 'SE: dispose suggestions' to SC02::'SE: dispose suggestions';
        first start then 'SE: edit requirements';
        first 'SE: edit requirements' then 'FW: check and recommend';
        first 'FW: check and recommend' then 'SE: dispose suggestions';
        first 'SE: dispose suggestions' then done;
    }
    allocate SC02Summary::'SE: edit requirements' to systemsEngineer;
    allocate SC02Summary::'FW: check and recommend' to framework;
    allocate SC02Summary::'SE: dispose suggestions' to systemsEngineer;
    #sourceTrace dependency summary_SC02 from SC02Summary to SC02;
    view sc02View : ActionFlowView {
        expose SC02Summary::**;
        filter @SysML::ActionUsage or @SysML::SuccessionAsUsage;
        attribute depth = -1;
        attribute showInheritedRows = false;
        attribute showAnnotationRows = false;
    }
    action def SC03External1 { out item configuration : DesignConfiguration; doc /* Submit modeled candidate architectures, component properties, spacecraft allocations, resource limits and trade criteria. Agree pointing, thermal and load/mode assumptions with non-EPS engineers. Candidate hardware inputs are models and components, not executing hardware. */ }
    action def SC03External3 { in item plan : AnalysisPlan; out item result : AnalysisResult; doc /* Execute coupled electrical, thermal, applicable EMC/geometry and RAM profiles. Return generation/demand, energy, bus and battery histories, numerical settings, logs, runtime and failed/partial status. Run success gives no independent model validity. */ }
    action def SC03External5 { in item study : DesignStudy; out item decision : EngineeringDecision; out attribute accepted : Boolean; doc /* Resolve cross-subsystem incompatibilities with the systems/non-EPS engineers. Select, revise or defer the preliminary design against requirements, resources and acceptable risk. Record rationale and remaining limitations. */ }
    action def <'SC03'> SC03 {
        @MissionScenario { useCase = "UC03"; title = "Justify the EPS preliminary design"; }
        doc /* Justify the EPS preliminary design. The output is controlled phase products or explicit open findings. Review acceptance is a separate authorized decision through SC05. */
        perform action 'EPS: propose designs' : SC03External1 { @ExternalAction { performer = epsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: plan design analyses' { in item configuration : DesignConfiguration; out item plan : AnalysisPlan; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F04 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* F03 calculates preliminary power/energy budgets, array/battery sizing and mass/volume estimates from modeled component and design data. F01 proposes models and analysis methods at the fidelity needed by the trade question. Form time-dependent mission-load/EPS scenarios and applicable RAM analyses. Battery thermal/aging mechanisms are included only when the intended question needs them and suitable evidence exists. */ }
        perform action 'Tool: simulate designs' : SC03External3 { @ExternalAction { performer = analysisTools meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: compare evidence' { in item result : AnalysisResult; out item study : DesignStudy; out attribute usable : Boolean; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F04 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Assess numerical convergence, intended use, fidelity omissions, calibration and independent model assessment. F03 compares mandatory feasibility separately from preference ranking with uncertainty/sensitivity. Expose temporal shortages hidden by average budgets, missing reliability rates and incompatible subsystem assumptions. usable requires the supported evidence specified by the decision criteria. */ }
        perform action 'EPS: justify selection' : SC03External5 { @ExternalAction { performer = epsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: retain design' { in item decision : EngineeringDecision; out item configuration : DesignConfiguration; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Retain the selected design and allocation, sizing/trade results, interface specifications, margins, risk dispositions and V&V plans for MDR/SDR or PDR through SC05. */ }
        action 'FW: retain design gaps' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Keep failed numerical checks, invalid model domains, unsupported mechanisms, missing reliability inputs and rejected design choices. Propose revised assumptions, independent supplied evidence or alternate models. Missing hardware evidence stays an external limitation with no physical-test proposal. */ }
        attribute usable : Boolean = 'FW: compare evidence'.usable;
        attribute accepted : Boolean = 'EPS: justify selection'.accepted;
        decide 'Proceed?';
        merge 'Complete';
        first start then 'EPS: propose designs';
        first 'EPS: propose designs' then 'FW: plan design analyses';
        first 'FW: plan design analyses' then 'Tool: simulate designs';
        first 'Tool: simulate designs' then 'FW: compare evidence';
        first 'FW: compare evidence' then 'EPS: justify selection';
        first 'EPS: justify selection' then 'Proceed?';
        succession proceed first 'Proceed?' if usable and accepted then 'FW: retain design' {
            succession '[usable and accepted]' [0..1] first 'Proceed?' then 'FW: retain design';
            bind '[usable and accepted]' = transitionLink;
        }
        succession hold first 'Proceed?' if not (usable and accepted) then 'FW: retain design gaps' {
            succession '[not (usable and accepted)]' [0..1] first 'Proceed?' then 'FW: retain design gaps';
            bind '[not (usable and accepted)]' = transitionLink;
        }
        flow exchange1 of DesignConfiguration from 'EPS: propose designs'.configuration to 'FW: plan design analyses'.configuration;
        flow exchange2 of AnalysisPlan from 'FW: plan design analyses'.plan to 'Tool: simulate designs'.plan;
        flow exchange3 of AnalysisResult from 'Tool: simulate designs'.result to 'FW: compare evidence'.result;
        flow exchange4 of DesignStudy from 'FW: compare evidence'.study to 'EPS: justify selection'.study;
        flow exchange5 of EngineeringDecision from 'EPS: justify selection'.decision to 'FW: retain design'.decision;
        first 'FW: retain design' then 'Complete';
        first 'FW: retain design gaps' then 'Complete';
        first 'Complete' then done;
    }
    allocate SC03::'EPS: propose designs' to epsEngineer;
    allocate SC03::'FW: plan design analyses' to framework;
    allocate SC03::'Tool: simulate designs' to analysisTools;
    allocate SC03::'FW: compare evidence' to framework;
    allocate SC03::'EPS: justify selection' to epsEngineer;
    allocate SC03::'FW: retain design' to framework;
    allocate SC03::'FW: retain design gaps' to framework;
    #sourceTrace dependency scenario_UC03 from SC03 to FrameworkNeeds::UC03;
    #proposedDerivation dependency scenario_SC03_MR03 from SC03 to FrameworkNeeds::MR_03;
    #proposedDerivation dependency scenario_SC03_MR04 from SC03 to FrameworkNeeds::MR_04;
    #sourceTrace dependency review_SC03 from SC03 to SC05;
    action def SC03Summary {
        doc /* Main interaction summary of SC03. Coordinated tool work and alternative/failure paths are specified by the full scenario and report prose. */
        action def 'Submit';
        perform action 'EPS: propose designs' : 'Submit' { @ExternalAction { performer = epsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep0 from 'EPS: propose designs' to SC03::'EPS: propose designs';
        action 'FW: compare evidence' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F04 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } }
        #sourceTrace dependency summaryStep1 from 'FW: compare evidence' to SC03::'FW: compare evidence';
        action def 'Decide';
        perform action 'EPS: justify selection' : 'Decide' { @ExternalAction { performer = epsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep2 from 'EPS: justify selection' to SC03::'EPS: justify selection';
        first start then 'EPS: propose designs';
        first 'EPS: propose designs' then 'FW: compare evidence';
        first 'FW: compare evidence' then 'EPS: justify selection';
        first 'EPS: justify selection' then done;
    }
    allocate SC03Summary::'EPS: propose designs' to epsEngineer;
    allocate SC03Summary::'FW: compare evidence' to framework;
    allocate SC03Summary::'EPS: justify selection' to epsEngineer;
    #sourceTrace dependency summary_SC03 from SC03Summary to SC03;
    view sc03View : ActionFlowView {
        expose SC03Summary::**;
        filter @SysML::ActionUsage or @SysML::SuccessionAsUsage;
        attribute depth = -1;
        attribute showInheritedRows = false;
        attribute showAnnotationRows = false;
    }
    action def SC04External1 { out item specification : EPSInterfaceSpecification; doc /* Submit detailed EPS component/control models, interface/software design, scenarios and acceptance criteria. Identify the declared host-executed control/interface software scope. Detailed design is prepared for scoped CDR through SC05 before deliverable coding. */ }
    action def SC04External3 { in item plan : AnalysisPlan; out item result : AnalysisResult; doc /* Execute modeled control and plant with declared mission scenarios. Return expected/actual histories, numerical settings, failures and raw evidence. No target processor executes. */ }
    action def SC04External5 { in item request : CodingRequest; out item result : SoftwareRunResult; doc /* Perform the declared coding and build using the approved design and selected host profile. Exercise the declared control/interface code against simulated EPS/subsystem products for the matching MIL scenarios. Return source/build versions, dependencies, logs, actual outputs, failures and host environment. */ }
    action def SC04External7 { in item response : EngineeringResponse; out item decision : EngineeringDecision; doc /* Approve, revise or defer the scoped model/software products and finding dispositions. Engineer approval neither closes unsupported predictions nor grants review progression. Submit the resulting baseline through SC05. */ }
    action def <'SC04'> SC04 {
        @MissionScenario { useCase = "UC04"; title = "Complete detailed EPS models and software"; }
        doc /* Complete detailed EPS models and software. The output is controlled phase products or explicit open findings. Review acceptance is a separate authorized decision through SC05. */
        perform action 'EPS: define detailed design' : SC04External1 { @ExternalAction { performer = epsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: plan MIL' { in item specification : EPSInterfaceSpecification; out item plan : AnalysisPlan; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F05 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Check detailed interface types, units, ranges, timing/mode meaning, command guards/effects and recovery responsibilities. F04 records fidelity and credibility limits. F06 specifies EPS requirement and ConOps assessment, including nominal and selected faults/protection. Prepare the simulated plant/controller MIL plan. */ }
        perform action 'Tool: execute MIL' : SC04External3 { @ExternalAction { performer = analysisTools meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: check design release' { in item result : AnalysisResult; out item request : CodingRequest; out attribute released : Boolean; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F05 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Retain MIL results and detailed design findings. Check the authorized scoped CDR design release, software scope, compatible integration profile and host dependencies. released is false for missing/unauthorized release, stale design revisions or blocking design findings. Form the approved coding/build/SIL request only for the released design. */ }
        perform action 'Host tool: code and SIL' : SC04External5 { @ExternalAction { performer = hostToolchain meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: assess MIL and SIL' { in item result : SoftwareRunResult; out item response : EngineeringResponse; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F06 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Compare applicable requirement and ConOps criteria and MIL/SIL differences under fixed comparison rules. Preserve mismatches, interface gaps and partial failures. F08 prepares released model/software data, evidence and integration configurations/procedures for scoped end-of-C SIR. */ }
        perform action 'EPS: approve products' : SC04External7 { @ExternalAction { performer = epsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: block coding' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Preserve design-release blockers and the current design baseline. Request correction or authorized review. Deliverable coding is blocked without the scoped CDR design release. Failed SIL returns through the assessment path with unresolved findings and no integration-readiness claim. */ }
        attribute released : Boolean = 'FW: check design release'.released;
        decide 'Proceed?';
        merge 'Complete';
        first start then 'EPS: define detailed design';
        first 'EPS: define detailed design' then 'FW: plan MIL';
        first 'FW: plan MIL' then 'Tool: execute MIL';
        first 'Tool: execute MIL' then 'FW: check design release';
        first 'FW: check design release' then 'Proceed?';
        succession proceed first 'Proceed?' if released then 'Host tool: code and SIL' {
            succession '[released]' [0..1] first 'Proceed?' then 'Host tool: code and SIL';
            bind '[released]' = transitionLink;
        }
        succession hold first 'Proceed?' if not released then 'FW: block coding' {
            succession '[not released]' [0..1] first 'Proceed?' then 'FW: block coding';
            bind '[not released]' = transitionLink;
        }
        first 'Host tool: code and SIL' then 'FW: assess MIL and SIL';
        first 'FW: assess MIL and SIL' then 'EPS: approve products';
        flow exchange1 of EPSInterfaceSpecification from 'EPS: define detailed design'.specification to 'FW: plan MIL'.specification;
        flow exchange2 of AnalysisPlan from 'FW: plan MIL'.plan to 'Tool: execute MIL'.plan;
        flow exchange3 of AnalysisResult from 'Tool: execute MIL'.result to 'FW: check design release'.result;
        flow exchange4 of CodingRequest from 'FW: check design release'.request to 'Host tool: code and SIL'.request;
        flow exchange5 of SoftwareRunResult from 'Host tool: code and SIL'.result to 'FW: assess MIL and SIL'.result;
        flow exchange6 of EngineeringResponse from 'FW: assess MIL and SIL'.response to 'EPS: approve products'.response;
        first 'EPS: approve products' then 'Complete';
        first 'FW: block coding' then 'Complete';
        first 'Complete' then done;
    }
    allocate SC04::'EPS: define detailed design' to epsEngineer;
    allocate SC04::'FW: plan MIL' to framework;
    allocate SC04::'Tool: execute MIL' to analysisTools;
    allocate SC04::'FW: check design release' to framework;
    allocate SC04::'Host tool: code and SIL' to hostToolchain;
    allocate SC04::'FW: assess MIL and SIL' to framework;
    allocate SC04::'EPS: approve products' to epsEngineer;
    allocate SC04::'FW: block coding' to framework;
    #sourceTrace dependency scenario_UC04 from SC04 to FrameworkNeeds::UC04;
    #proposedDerivation dependency scenario_SC04_MR05 from SC04 to FrameworkNeeds::MR_05;
    #proposedDerivation dependency scenario_SC04_MR06 from SC04 to FrameworkNeeds::MR_06;
    #sourceTrace dependency review_SC04 from SC04 to SC05;
    action def SC04Summary {
        doc /* Main interaction summary of SC04. Coordinated tool work and alternative/failure paths are specified by the full scenario and report prose. */
        action def 'Submit';
        perform action 'EPS: define detailed design' : 'Submit' { @ExternalAction { performer = epsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep0 from 'EPS: define detailed design' to SC04::'EPS: define detailed design';
        action def 'Execute';
        perform action 'Host tool: code and SIL' : 'Execute' { @ExternalAction { performer = hostToolchain meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep1 from 'Host tool: code and SIL' to SC04::'Host tool: code and SIL';
        action 'FW: assess MIL and SIL' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F06 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } }
        #sourceTrace dependency summaryStep2 from 'FW: assess MIL and SIL' to SC04::'FW: assess MIL and SIL';
        first start then 'EPS: define detailed design';
        first 'EPS: define detailed design' then 'Host tool: code and SIL';
        first 'Host tool: code and SIL' then 'FW: assess MIL and SIL';
        first 'FW: assess MIL and SIL' then done;
    }
    allocate SC04Summary::'EPS: define detailed design' to epsEngineer;
    allocate SC04Summary::'Host tool: code and SIL' to hostToolchain;
    allocate SC04Summary::'FW: assess MIL and SIL' to framework;
    #sourceTrace dependency summary_SC04 from SC04Summary to SC04;
    view sc04View : ActionFlowView {
        expose SC04Summary::**;
        filter @SysML::ActionUsage or @SysML::SuccessionAsUsage;
        attribute depth = -1;
        attribute showInheritedRows = false;
        attribute showAnnotationRows = false;
    }
    action def SC05External1 { out item submission : EngineeringSubmission; doc /* Request a controlled change or designated phase review for an exact baseline. Submit replacements, rationale, authority and agreed scoped entrance/success criteria. A review without change uses the current baseline. */ }
    action def SC05External3 { in item plan : AnalysisPlan; out item result : AnalysisResult; doc /* Execute the declared affected model assessments or coordinate declared host MIL/SIL profiles. Replay unaffected reference outputs where required by the change plan. Return raw results, failures and comparison outcomes. No fixed number of mission cases is required. */ }
    action def SC05External5 { in item reviewPackage : ReviewPackage; out item findings : ReviewSubmission; doc /* Independently assess the package against its scoped criteria and report blocking, conditional or advisory findings. Missing affected results and contested dispositions remain visible. */ }
    action def SC05External6 { in item findings : ReviewSubmission; out item submission : ReviewSubmission; out attribute authorized : Boolean; out attribute current : Boolean; doc /* Issue accepted, conditional or progression-blocked disposition against the exact reviewed baseline and agreed scoped success criteria. Conditional progression needs limits, accountable closure actions, owners and due dates. Blocking findings prevent progression. A newer context invalidates the currency of this decision. authorized and current identify a genuine designated-authority decision for the current baseline. */ }
    action def <'SC05'> SC05 {
        @MissionScenario { useCase = "UC05"; title = "Maintain and review coherent phase baselines"; }
        doc /* Maintain and review coherent phase baselines. The output is controlled phase products or explicit open findings. Review acceptance is a separate authorized decision through SC05. */
        perform action 'SE: request change or review' : SC05External1 { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: assess impacts' { in item submission : EngineeringSubmission; out item plan : AnalysisPlan; out attribute changed : Boolean; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Check transfers and permissions before registration. Identify reciprocal requirement, interface, budget, model/software, guidance and evidence impacts, including unresolved dependencies. On change, immediately invalidate affected assistance/evidence. Obtain the authorized engineer change decision before retaining a successor proposal. Reject incompatible/declined changes without replacing the predecessor. changed indicates accepted changes with required repeated analyses, MIL/SIL or EPS product V&V. */ }
        perform action 'Tool: repeat assessments' : SC05External3 { @ExternalAction { performer = analysisTools meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: prepare review' { in item result : AnalysisResult; out item reviewPackage : ReviewPackage; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F08 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Use applicable current results and preserve failed/partial/cancelled runs, stale evidence and critical gaps. Reconstruct the candidate phase baseline. Check agreed review entrance criteria, generate readable views and assemble requirement/expectation coverage, design and decision justification, credibility limits and finding dispositions. No changed baseline or package is automatically accepted. */ }
        perform action 'Reviewer: report findings' : SC05External5 { @ExternalAction { performer = reviewers meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        perform action 'Authority: decide progression' : SC05External6 { @ExternalAction { performer = reviewAuthority meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        action 'FW: record disposition' { in item submission : ReviewSubmission; out item baseline : PhaseBaseline; @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Record the authorized current disposition separately from preparation. Preserve predecessor and successor identities, criteria, findings, conditions and closure actions. Only accepted or properly conditional decisions with no blocking finding permit declared progression. F08 retains the reconstructable review record. */ }
        action 'FW: keep review pending' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } doc /* Reject unauthorized or stale-baseline review decisions and retain their reasons. Keep the last controlled baseline and report pending/blocked progression. Reopen affected work after failed checks or changes and request a new review of the current package. */ }
        attribute changed : Boolean = 'FW: assess impacts'.changed;
        attribute authorized : Boolean = 'Authority: decide progression'.authorized;
        attribute current : Boolean = 'Authority: decide progression'.current;
        decide 'Proceed?';
        merge 'Complete';
        first start then 'SE: request change or review';
        first 'SE: request change or review' then 'FW: assess impacts';
        decide 'Reassess?';
        action 'FW: reuse current evidence' {
            out item result : AnalysisResult;
            @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F07 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; }
            doc /* Review without an accepted change retrieves applicable current evidence from the exact baseline. Missing or stale results stay gaps. No unaffected execution is required. */
        }
        first 'FW: assess impacts' then 'Reassess?';
        succession repeatAffected first 'Reassess?' if changed then 'Tool: repeat assessments' {
            succession '[changed]' [0..1] first 'Reassess?' then 'Tool: repeat assessments';
            bind '[changed]' = transitionLink;
        }
        succession useCurrent first 'Reassess?' if not changed then 'FW: reuse current evidence' {
            succession '[not changed]' [0..1] first 'Reassess?' then 'FW: reuse current evidence';
            bind '[not changed]' = transitionLink;
        }
        merge 'Assessment evidence';
        first 'FW: reuse current evidence' then 'Assessment evidence';
        first 'Assessment evidence' then 'FW: prepare review';
        flow currentEvidence of AnalysisResult from 'FW: reuse current evidence'.result to 'FW: prepare review'.result;
        first 'Tool: repeat assessments' then 'Assessment evidence';
        first 'FW: prepare review' then 'Reviewer: report findings';
        first 'Reviewer: report findings' then 'Authority: decide progression';
        first 'Authority: decide progression' then 'Proceed?';
        succession proceed first 'Proceed?' if authorized and current then 'FW: record disposition' {
            succession '[authorized and current]' [0..1] first 'Proceed?' then 'FW: record disposition';
            bind '[authorized and current]' = transitionLink;
        }
        succession hold first 'Proceed?' if not (authorized and current) then 'FW: keep review pending' {
            succession '[not (authorized and current)]' [0..1] first 'Proceed?' then 'FW: keep review pending';
            bind '[not (authorized and current)]' = transitionLink;
        }
        flow exchange1 of EngineeringSubmission from 'SE: request change or review'.submission to 'FW: assess impacts'.submission;
        flow exchange2 of AnalysisPlan from 'FW: assess impacts'.plan to 'Tool: repeat assessments'.plan;
        flow exchange3 of AnalysisResult from 'Tool: repeat assessments'.result to 'FW: prepare review'.result;
        flow exchange4 of ReviewPackage from 'FW: prepare review'.reviewPackage to 'Reviewer: report findings'.reviewPackage;
        flow exchange5 of ReviewSubmission from 'Reviewer: report findings'.findings to 'Authority: decide progression'.findings;
        flow exchange6 of ReviewSubmission from 'Authority: decide progression'.submission to 'FW: record disposition'.submission;
        first 'FW: record disposition' then 'Complete';
        first 'FW: keep review pending' then 'Complete';
        first 'Complete' then done;
    }
    allocate SC05::'SE: request change or review' to systemsEngineer;
    allocate SC05::'FW: assess impacts' to framework;
    allocate SC05::'FW: reuse current evidence' to framework;
    allocate SC05::'Tool: repeat assessments' to analysisTools;
    allocate SC05::'FW: prepare review' to framework;
    allocate SC05::'Reviewer: report findings' to reviewers;
    allocate SC05::'Authority: decide progression' to reviewAuthority;
    allocate SC05::'FW: record disposition' to framework;
    allocate SC05::'FW: keep review pending' to framework;
    #sourceTrace dependency scenario_UC05 from SC05 to FrameworkNeeds::UC05;
    #proposedDerivation dependency scenario_SC05_MR01 from SC05 to FrameworkNeeds::MR_01;
    #proposedDerivation dependency scenario_SC05_MR02 from SC05 to FrameworkNeeds::MR_02;
    #proposedDerivation dependency scenario_SC05_MR03 from SC05 to FrameworkNeeds::MR_03;
    #proposedDerivation dependency scenario_SC05_MR04 from SC05 to FrameworkNeeds::MR_04;
    #proposedDerivation dependency scenario_SC05_MR05 from SC05 to FrameworkNeeds::MR_05;
    #proposedDerivation dependency scenario_SC05_MR06 from SC05 to FrameworkNeeds::MR_06;
    action def SC05Summary {
        doc /* Main interaction summary of SC05. Coordinated tool work and alternative/failure paths are specified by the full scenario and report prose. */
        action def 'Submit';
        perform action 'SE: request change or review' : 'Submit' { @ExternalAction { performer = systemsEngineer meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep0 from 'SE: request change or review' to SC05::'SE: request change or review';
        action 'FW: prepare review' { @FrameworkAction { performer = framework meta SysML::PartUsage; function = BoundaryViews::F08 meta SysML::ActionDefinition; fillColor = "#DCEEF8"; } }
        #sourceTrace dependency summaryStep1 from 'FW: prepare review' to SC05::'FW: prepare review';
        action def 'Decide';
        perform action 'Authority: decide progression' : 'Decide' { @ExternalAction { performer = reviewAuthority meta SysML::PartUsage; fillColor = "#FFF0D6"; } }
        #sourceTrace dependency summaryStep2 from 'Authority: decide progression' to SC05::'Authority: decide progression';
        first start then 'SE: request change or review';
        first 'SE: request change or review' then 'FW: prepare review';
        first 'FW: prepare review' then 'Authority: decide progression';
        first 'Authority: decide progression' then done;
    }
    allocate SC05Summary::'SE: request change or review' to systemsEngineer;
    allocate SC05Summary::'FW: prepare review' to framework;
    allocate SC05Summary::'Authority: decide progression' to reviewAuthority;
    #sourceTrace dependency summary_SC05 from SC05Summary to SC05;
    view sc05View : ActionFlowView {
        expose SC05Summary::**;
        filter @SysML::ActionUsage or @SysML::SuccessionAsUsage;
        attribute depth = -1;
        attribute showInheritedRows = false;
        attribute showAnnotationRows = false;
    }

    item def PrepareReview;
    item def SubmitReview;
    item def DecideReview :> TechnicalReviewDecision {
        doc /* Initial or renewed authority decision for the exact baseline and scoped success criteria. The event carries the authority's disposition. Prior-condition closure evidence is separate. */
    }
    item def EditContext;
    item def RequestAssistance;
    item def ReturnAssistance;
    item def ApplySuggestion;
    state def BaselineControl {
        attribute entranceComplete : Boolean;
        attribute authorizedCurrent : Boolean;
        attribute blocking : Boolean;
        attribute conditionalRecordsComplete : Boolean;
        attribute closureComplete : Boolean;
        entry; then draft;
        state draft;
        state prepared;
        state underReview;
        state acceptedBaseline;
        state conditional;
        state progressionBlocked;
        transition prepare first draft accept PrepareReview if entranceComplete then prepared;
        transition submit first prepared accept SubmitReview then underReview;
        transition approve first underReview accept decision : DecideReview if authorizedCurrent and not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;
        transition constrain first underReview accept decision : DecideReview if authorizedCurrent and not blocking and decision.disposition == ReviewDisposition::conditional and conditionalRecordsComplete then conditional;
        transition block first underReview accept decision : DecideReview if authorizedCurrent and decision.disposition == ReviewDisposition::progressionBlocked then progressionBlocked;
        transition closeConditions first conditional accept decision : DecideReview if authorizedCurrent and closureComplete and not blocking and decision.disposition == ReviewDisposition::accepted then acceptedBaseline;
        transition renewConditional first conditional accept decision : DecideReview if authorizedCurrent and not blocking and decision.disposition == ReviewDisposition::conditional and conditionalRecordsComplete then conditional;
        transition blockRenewal first conditional accept decision : DecideReview if authorizedCurrent and decision.disposition == ReviewDisposition::progressionBlocked then progressionBlocked;
        transition reviseBlocked first progressionBlocked accept EditContext then draft;
        transition reviseAccepted first acceptedBaseline accept EditContext then draft;
        transition reviseConditional first conditional accept EditContext then draft;
        transition revisePrepared first prepared accept EditContext then draft;
        transition reviseReview first underReview accept EditContext then draft;
        doc /* Per proposed phase-baseline revision. Editing an accepted revision creates a draft successor while retaining the accepted predecessor. Prepared means entrance complete. authorizedCurrent denotes the L07 authority, exact baseline and scoped criteria checks. blocking includes critical evidence gaps. conditionalRecordsComplete describes the new decision's rationale, limits, closure actions, owners and dates. closureComplete describes evidence closing prior conditions. Only an explicitly accepted decision with no blockers can establish acceptance. Renewed acceptance also requires prior closure evidence. A renewed conditional decision retains conditional status with its new conditions, even after prior conditions close. A renewed progression-blocked decision blocks progression. Unauthorized, stale, inconsistent or incomplete decisions change no state. */
    }
    state def GuidanceControl {
        attribute sameContext : Boolean;
        attribute authorized : Boolean;
        entry; then pending;
        state pending;
        state current;
        state stale;
        transition response first pending accept ReturnAssistance if sameContext then current;
        transition lateResponse first pending accept ReturnAssistance if not sameContext then stale;
        transition editPending first pending accept EditContext then stale;
        transition editCurrent first current accept EditContext then stale;
        transition reassess first stale accept RequestAssistance then pending;
        transition apply first current accept ApplySuggestion if sameContext and authorized then current;
        doc /* Per assistance request/context revision. Changes invalidate outputs immediately. Pending/unavailable is explicit. No stale suggestion can be applied as current. Dispositions remain stored after reassessment. */
    }
    #sourceTrace dependency control_FR30 from GuidanceControl to FrameworkRequirements::FR_30;
    #sourceTrace dependency control_FR42 from BaselineControl to FrameworkRequirements::FR_42;
}
