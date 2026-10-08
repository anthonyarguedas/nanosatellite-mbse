// Current framework black-box requirements. Every reused ID has the meaning below.
// FR-12 and FR-40 are retired. The former two-case protocol belongs only to later validation/research evaluation.
// TODO: Re-derive LA/PA allocations and V cases from these statements. No satisfaction is asserted.
package FrameworkRequirements {
    private import FrameworkDomain::*;
    private import RequirementDerivation::*;
    metadata def RequirementExchange {
        attribute inputs : ScalarValues::String [0..*];
        attribute outputs : ScalarValues::String [0..*];
    }
    metadata def PlannedRequirementCheck {
        attribute theme : ScalarValues::String;
        attribute methods : ScalarValues::String;
        attribute checkSummary : ScalarValues::String;
        attribute status : ScalarValues::String = "planned, not executed";
    }
    requirement <'FR-01'> FR_01 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain each requirement with its identifier, revision, statement, product level, source and parent revisions, rationale, owner, conditions or quantities, applicable units, verification method, criterion and resolution status, including reasons for unresolved or inapplicable fields. */
    }
    @SourceRecord about FR_01 { identifier = "FR-01"; sourceText = "The framework shall retain each requirement with its identifier, revision, statement, product level, source and parent revisions, rationale, owner, conditions or quantities, applicable units, verification method, criterion and resolution status, including reasons for unresolved or inapplicable fields."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 4.2 and Appendix C"; }
    @PlannedRequirementCheck about FR_01 { theme = "Requirements and explained assistance"; methods = "I,T"; checkSummary = "Round-trip quantitative and qualitative records, including unresolved criteria."; }
    #derivation connection derive_MR_01_FR_01 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_01; }
    #derivation connection derive_MR_02_FR_01 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_01; }
    #sourceTrace dependency scenario_FR01_SC01 from FR_01 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR01_SC02 from FR_01 to ScenarioViews::SC02;
    #sourceTrace dependency function_FR01_F02 from FR_01 to BoundaryViews::F02;
    requirement <'FR-02'> FR_02 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall check created or edited requirement drafts on each edit or request for declared deterministic quality errors, probable semantic duplicates, coverage gaps and source conflicts, returning affected text or records, the rule or cited passage, corrective suggestions or questions, uncertainty and assessment limits. */
    }
    @SourceRecord about FR_02 { identifier = "FR-02"; sourceText = "The framework shall check created or edited requirement drafts on each edit or request for declared deterministic quality errors, probable semantic duplicates, coverage gaps and source conflicts, returning affected text or records, the rule or cited passage, corrective suggestions or questions, uncertainty and assessment limits."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 4.2.1.2.4 and Appendix C"; }
    @PlannedRequirementCheck about FR_02 { theme = "Requirements and explained assistance"; methods = "A,T"; checkSummary = "Compare clean and seeded drafts with an independent expert reference, including valid similar requirements and missed defects."; }
    #derivation connection derive_MR_02_FR_02 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_02; }
    #sourceTrace dependency scenario_FR02_SC02 from FR_02 to ScenarioViews::SC02;
    #sourceTrace dependency function_FR02_F02 from FR_02 to BoundaryViews::F02;
    requirement <'FR-03'> FR_03 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall recommend derivation, analysis, verification and validation methods or models on edits or requests using the current lifecycle stage, engineering question, requirements, available inputs, validity, resources and scope, with applicability conditions, rationale, cited sources, alternatives and rejection records. */
    }
    @SourceRecord about FR_03 { identifier = "FR-03"; sourceText = "The framework shall recommend derivation, analysis, verification and validation methods or models on edits or requests using the current lifecycle stage, engineering question, requirements, available inputs, validity, resources and scope, with applicability conditions, rationale, cited sources, alternatives and rejection records."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.8.1.2.1--5"; }
    @PlannedRequirementCheck about FR_03 { theme = "Requirements and explained assistance"; methods = "A,T"; checkSummary = "Use contextual queries whose eligible methods change with inputs, maturity or intended use."; }
    #derivation connection derive_MR_01_FR_03 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_03; }
    #derivation connection derive_MR_02_FR_03 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_03; }
    #derivation connection derive_MR_03_FR_03 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_03; }
    #derivation connection derive_MR_04_FR_03 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_03; }
    #derivation connection derive_MR_05_FR_03 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_03; }
    #derivation connection derive_MR_06_FR_03 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_03; }
    #sourceTrace dependency scenario_FR03_SC01 from FR_03 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR03_SC02 from FR_03 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR03_SC03 from FR_03 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR03_SC04 from FR_03 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR03_SC05 from FR_03 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR03_F01 from FR_03 to BoundaryViews::F01;
    requirement <'FR-04'> FR_04 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retrieve forward and reverse links among expectations, ConOps scenarios, requirements, function and element allocations, interfaces, decisions and applicable evidence, reporting missing or ambiguous endpoints and coverage against the declared reference set. */
    }
    @SourceRecord about FR_04 { identifier = "FR-04"; sourceText = "The framework shall retrieve forward and reverse links among expectations, ConOps scenarios, requirements, function and element allocations, interfaces, decisions and applicable evidence, reporting missing or ambiguous endpoints and coverage against the declared reference set."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 4.1--4.2 and 6.2"; }
    @PlannedRequirementCheck about FR_04 { theme = "Requirements and explained assistance"; methods = "T"; checkSummary = "Compare both query directions and coverage with a known relationship set."; }
    #derivation connection derive_MR_01_FR_04 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_04; }
    #derivation connection derive_MR_02_FR_04 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_04; }
    #derivation connection derive_MR_03_FR_04 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_04; }
    #derivation connection derive_MR_04_FR_04 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_04; }
    #derivation connection derive_MR_05_FR_04 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_04; }
    #derivation connection derive_MR_06_FR_04 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_04; }
    #sourceTrace dependency scenario_FR04_SC02 from FR_04 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR04_SC05 from FR_04 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR04_F02 from FR_04 to BoundaryViews::F02;
    requirement <'FR-17'> FR_17 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall produce proposed EPS and component requirement allocations from identified spacecraft requirements, scenarios and sourced design quantities using a declared derivation method, retaining parent links, units, assumptions, uncertainty and engineer dispositions. */
    }
    @SourceRecord about FR_17 { identifier = "FR-17"; sourceText = "The framework shall produce proposed EPS and component requirement allocations from identified spacecraft requirements, scenarios and sourced design quantities using a declared derivation method, retaining parent links, units, assumptions, uncertainty and engineer dispositions."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 4.2--4.3"; }
    @PlannedRequirementCheck about FR_17 { theme = "Requirements and explained assistance"; methods = "A,T"; checkSummary = "Recalculate an allocation and follow it to the parent and source quantities."; }
    #derivation connection derive_MR_02_FR_17 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_17; }
    #derivation connection derive_MR_03_FR_17 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_17; }
    #derivation connection derive_MR_04_FR_17 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_17; }
    #derivation connection derive_MR_05_FR_17 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_17; }
    #sourceTrace dependency scenario_FR17_SC02 from FR_17 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR17_SC03 from FR_17 to ScenarioViews::SC03;
    #sourceTrace dependency function_FR17_F02 from FR_17 to BoundaryViews::F02;
    requirement <'FR-29'> FR_29 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain the authorized engineer disposition of each requirement correction or method/model suggestion as accepted, modified, rejected or deferred, with rationale and the exact suggestion and context revisions. */
    }
    @SourceRecord about FR_29 { identifier = "FR-29"; sourceText = "The framework shall retain the authorized engineer disposition of each requirement correction or method/model suggestion as accepted, modified, rejected or deferred, with rationale and the exact suggestion and context revisions."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 4.2 and 6.8"; }
    @PlannedRequirementCheck about FR_29 { theme = "Requirements and explained assistance"; methods = "I,T"; checkSummary = "Exercise all dispositions and an unauthorized attempt to apply a suggestion."; }
    #derivation connection derive_MR_01_FR_29 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_29; }
    #derivation connection derive_MR_02_FR_29 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_29; }
    #derivation connection derive_MR_03_FR_29 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_29; }
    #derivation connection derive_MR_04_FR_29 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_29; }
    #derivation connection derive_MR_05_FR_29 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_29; }
    #derivation connection derive_MR_06_FR_29 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_29; }
    #sourceTrace dependency scenario_FR29_SC02 from FR_29 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR29_SC05 from FR_29 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR29_F02 from FR_29 to BoundaryViews::F02;
    requirement <'FR-30'> FR_30 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall mark affected assistance stale when its requirement, mission, design, source, criterion or scope revision changes, prevent stale suggestions from being applied as current guidance and initiate reassessment for the new context. */
    }
    @SourceRecord about FR_30 { identifier = "FR-30"; sourceText = "The framework shall mark affected assistance stale when its requirement, mission, design, source, criterion or scope revision changes, prevent stale suggestions from being applied as current guidance and initiate reassessment for the new context."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.2 and 6.5"; }
    @PlannedRequirementCheck about FR_30 { theme = "Requirements and explained assistance"; methods = "T"; checkSummary = "Edit during a delayed response and check that the old response cannot replace current guidance."; }
    #derivation connection derive_MR_01_FR_30 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_30; }
    #derivation connection derive_MR_02_FR_30 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_30; }
    #derivation connection derive_MR_03_FR_30 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_30; }
    #derivation connection derive_MR_04_FR_30 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_30; }
    #derivation connection derive_MR_05_FR_30 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_30; }
    #derivation connection derive_MR_06_FR_30 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_30; }
    #sourceTrace dependency scenario_FR30_SC02 from FR_30 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR30_SC05 from FR_30 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR30_F01 from FR_30 to BoundaryViews::F01;
    requirement <'FR-39'> FR_39 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall propose next engineering activities and repeated assessments from the declared phase, product maturity, dependencies, open findings and review criteria, identifying unmet prerequisites and the rationale for each proposal. */
    }
    @SourceRecord about FR_39 { identifier = "FR-39"; sourceText = "The framework shall propose next engineering activities and repeated assessments from the declared phase, product maturity, dependencies, open findings and review criteria, identifying unmet prerequisites and the rationale for each proposal."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 3.3--3.6 and 6.7"; }
    @PlannedRequirementCheck about FR_39 { theme = "Requirements and explained assistance"; methods = "A,D"; checkSummary = "Change maturity and blocking findings and inspect the revised activity proposals."; }
    #derivation connection derive_MR_01_FR_39 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_39; }
    #derivation connection derive_MR_02_FR_39 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_39; }
    #derivation connection derive_MR_03_FR_39 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_39; }
    #derivation connection derive_MR_04_FR_39 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_39; }
    #derivation connection derive_MR_05_FR_39 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_39; }
    #derivation connection derive_MR_06_FR_39 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_39; }
    #sourceTrace dependency scenario_FR39_SC01 from FR_39 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR39_SC02 from FR_39 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR39_SC03 from FR_39 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR39_SC04 from FR_39 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR39_SC05 from FR_39 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR39_F01 from FR_39 to BoundaryViews::F01;
    requirement <'FR-41'> FR_41 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall acknowledge each assistance trigger and return a finding, recommendation or explicit pending/unavailable status within the engineer-approved interactive response limits, recording trigger, first-response and completion times for the current context. */
    }
    @SourceRecord about FR_41 { identifier = "FR-41"; sourceText = "The framework shall acknowledge each assistance trigger and return a finding, recommendation or explicit pending/unavailable status within the engineer-approved interactive response limits, recording trigger, first-response and completion times for the current context."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "OOSEM 17.3.3 performance properties and NASA 4.2.1.2.5"; }
    @PlannedRequirementCheck about FR_41 { theme = "Requirements and explained assistance"; methods = "T"; checkSummary = "Measure response delay under the declared workload, including outage and superseded edits."; }
    #derivation connection derive_MR_01_FR_41 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_41; }
    #derivation connection derive_MR_02_FR_41 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_41; }
    #derivation connection derive_MR_03_FR_41 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_41; }
    #derivation connection derive_MR_04_FR_41 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_41; }
    #derivation connection derive_MR_05_FR_41 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_41; }
    #derivation connection derive_MR_06_FR_41 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_41; }
    #sourceTrace dependency scenario_FR41_SC02 from FR_41 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR41_SC05 from FR_41 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR41_F01 from FR_41 to BoundaryViews::F01;
    requirement <'FR-25'> FR_25 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain mission expectations, constraints and nominal/degraded ConOps scenarios with orbit, attitude, duration, environmental conditions, subsystem modes, load schedules and transitions as revision-linked inputs to EPS requirements and analysis. */
    }
    @SourceRecord about FR_25 { identifier = "FR-25"; sourceText = "The framework shall retain mission expectations, constraints and nominal/degraded ConOps scenarios with orbit, attitude, duration, environmental conditions, subsystem modes, load schedules and transitions as revision-linked inputs to EPS requirements and analysis."; sourceLocator = "Analyze System Requirements, Mission concepts and preliminary design"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 4.1 and Boan 2--3"; }
    @PlannedRequirementCheck about FR_25 { theme = "Mission concepts and preliminary design"; methods = "I,T"; checkSummary = "Revise a degraded mode and trace its requirement and analysis inputs."; }
    #derivation connection derive_MR_01_FR_25 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_25; }
    #derivation connection derive_MR_02_FR_25 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_25; }
    #sourceTrace dependency scenario_FR25_SC01 from FR_25 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR25_SC02 from FR_25 to ScenarioViews::SC02;
    #sourceTrace dependency function_FR25_F03 from FR_25 to BoundaryViews::F03;
    requirement <'FR-15'> FR_15 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall configure EPS design representations through identified parameters, component variants and extensions covering generation, storage, conversion, regulation, protection, distribution, control, interfaces and requirement allocations. */
    }
    @SourceRecord about FR_15 { identifier = "FR-15"; sourceText = "The framework shall configure EPS design representations through identified parameters, component variants and extensions covering generation, storage, conversion, regulation, protection, distribution, control, interfaces and requirement allocations."; sourceLocator = "Analyze System Requirements, Mission concepts and preliminary design"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "El Hachimi 2--4 and Girardello 2--3"; }
    @PlannedRequirementCheck about FR_15 { theme = "Mission concepts and preliminary design"; methods = "I,D"; checkSummary = "Configure alternate EPS topologies and retain the distinct allocation and extension revisions."; }
    #derivation connection derive_MR_01_FR_15 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_15; }
    #derivation connection derive_MR_03_FR_15 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_15; }
    #derivation connection derive_MR_04_FR_15 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_15; }
    #derivation connection derive_MR_05_FR_15 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_15; }
    #sourceTrace dependency scenario_FR15_SC01 from FR_15 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR15_SC03 from FR_15 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR15_SC04 from FR_15 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR15_F03 from FR_15 to BoundaryViews::F03;
    requirement <'FR-13'> FR_13 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall calculate revision-linked EPS mass and volume estimates from modeled component and design data, retaining sources, units, aggregation assumptions, uncertainty and unknown values. */
    }
    @SourceRecord about FR_13 { identifier = "FR-13"; sourceText = "The framework shall calculate revision-linked EPS mass and volume estimates from modeled component and design data, retaining sources, units, aggregation assumptions, uncertainty and unknown values."; sourceLocator = "Analyze System Requirements, Mission concepts and preliminary design"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 3.5 and Girardello 3.2 limitations"; }
    @PlannedRequirementCheck about FR_13 { theme = "Mission concepts and preliminary design"; methods = "A,T"; checkSummary = "Recalculate mass and volume after a component substitution and preserve unknown properties and aggregation assumptions."; }
    #derivation connection derive_MR_03_FR_13 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_13; }
    #derivation connection derive_MR_04_FR_13 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_13; }
    #sourceTrace dependency scenario_FR13_SC03 from FR_13 to ScenarioViews::SC03;
    #sourceTrace dependency function_FR13_F03 from FR_13 to BoundaryViews::F03;
    requirement <'FR-14'> FR_14 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall compare designated EPS concepts and architectures on common requirements, mission assumptions and engineer-approved criteria, separating mandatory feasibility from preference ranking and reporting raw measures, margins, uncertainty, sensitivity, risks and selection rationale. */
    }
    @SourceRecord about FR_14 { identifier = "FR-14"; sourceText = "The framework shall compare designated EPS concepts and architectures on common requirements, mission assumptions and engineer-approved criteria, separating mandatory feasibility from preference ranking and reporting raw measures, margins, uncertainty, sensitivity, risks and selection rationale."; sourceLocator = "Analyze System Requirements, Mission concepts and preliminary design"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.8.1.2.1--5"; }
    @PlannedRequirementCheck about FR_14 { theme = "Mission concepts and preliminary design"; methods = "A,T"; checkSummary = "Use infeasible and closely ranked alternatives with uncertain inputs."; }
    #derivation connection derive_MR_01_FR_14 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_14; }
    #derivation connection derive_MR_03_FR_14 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_14; }
    #derivation connection derive_MR_04_FR_14 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_14; }
    #sourceTrace dependency scenario_FR14_SC01 from FR_14 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR14_SC03 from FR_14 to ScenarioViews::SC03;
    #sourceTrace dependency function_FR14_F03 from FR_14 to BoundaryViews::F03;
    requirement <'FR-20'> FR_20 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall calculate preliminary generation, demand and energy budgets and array/battery sizing for the declared mission modes, including sourced efficiencies, duty cycles, eclipse duration, allowable battery operating limits, degradation assumptions and engineer-defined margins. */
    }
    @SourceRecord about FR_20 { identifier = "FR-20"; sourceText = "The framework shall calculate preliminary generation, demand and energy budgets and array/battery sizing for the declared mission modes, including sourced efficiencies, duty cycles, eclipse duration, allowable battery operating limits, degradation assumptions and engineer-defined margins."; sourceLocator = "Analyze System Requirements, Mission concepts and preliminary design"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Boan 2--4, El Hachimi 3 and Girardello 2.2"; }
    @PlannedRequirementCheck about FR_20 { theme = "Mission concepts and preliminary design"; methods = "A,T"; checkSummary = "Compare sizing and energy balance with independent calculations, including an infeasible eclipse case."; }
    #derivation connection derive_MR_01_FR_20 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_20; }
    #derivation connection derive_MR_03_FR_20 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_20; }
    #derivation connection derive_MR_04_FR_20 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_20; }
    #sourceTrace dependency scenario_FR20_SC01 from FR_20 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR20_SC03 from FR_20 to ScenarioViews::SC03;
    #sourceTrace dependency function_FR20_F03 from FR_20 to BoundaryViews::F03;
    requirement <'FR-16'> FR_16 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall compose time-dependent subsystem loads, schedules and mode transitions with orbit, attitude, illumination, eclipse, thermal conditions and modeled EPS generation, storage, losses and protection to report power/energy balance, bus quantities and battery state within the declared model scope. */
    }
    @SourceRecord about FR_16 { identifier = "FR-16"; sourceText = "The framework shall compose time-dependent subsystem loads, schedules and mode transitions with orbit, attitude, illumination, eclipse, thermal conditions and modeled EPS generation, storage, losses and protection to report power/energy balance, bus quantities and battery state within the declared model scope."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Boan 2--4 and Casado 2--4"; }
    @PlannedRequirementCheck about FR_16 { theme = "Simulation and model credibility"; methods = "A,T"; checkSummary = "Use whole-CUBICS histories with a temporal shortage hidden by an average budget. Perturb load, mode or illumination and compare the mapped EPS numerical response with an independent reference within model scope."; }
    @RequirementExchange about FR_16 { inputs = ("Whole-CUBICS mission/subsystem load and mode histories", "orbit/attitude/illumination/thermal histories", "EPS models"); outputs = ("Power/energy balance", "bus quantities", "battery state histories"); }
    #derivation connection derive_MR_03_FR_16 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_16; }
    #derivation connection derive_MR_04_FR_16 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_16; }
    #derivation connection derive_MR_05_FR_16 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_16; }
    #derivation connection derive_MR_06_FR_16 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_16; }
    #sourceTrace dependency scenario_FR16_SC03 from FR_16 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR16_SC04 from FR_16 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR16_F04 from FR_16 to BoundaryViews::F04;
    requirement <'FR-18'> FR_18 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall exchange identified component and design models through declared electrical, thermal, applicable EMC and geometry profiles and couple EPS analyses to the required NVIDIA Omniverse whole-CUBICS simulation. The coupling shall receive spacecraft and subsystem scenario inputs and return EPS states and results under declared directions, entity/channel mappings, quantities and units, model/tool revisions, supported effects, execution status and unsupported or lossy transfers. */
    }
    @SourceRecord about FR_18 { identifier = "FR-18"; sourceText = "The framework shall exchange identified component and design models through declared electrical, thermal, applicable EMC and geometry profiles and couple EPS analyses to the required NVIDIA Omniverse whole-CUBICS simulation. The coupling shall receive spacecraft and subsystem scenario inputs and return EPS states and results under declared directions, entity/channel mappings, quantities and units, model/tool revisions, supported effects, execution status and unsupported or lossy transfers."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Stakeholder Omniverse whole-CUBICS constraint, NASA 3.5--3.6, El Hachimi 4 and handpicked-0001 (Zhu) pp.4--5 scene/data binding and streamed physics outputs. No CUBICS compatibility demonstrated."; }
    @PlannedRequirementCheck about FR_18 { theme = "Simulation and model credibility"; methods = "D,T"; checkSummary = "Exercise each discipline profile and incompatible mappings. Perturb an incoming whole-CUBICS history, compare the EPS numerical effect independently and return its identified response to the same scenario. Scene-only updates or missing numerical exchange cannot pass. Retain failed/partial status and transfer limits."; }
    @RequirementExchange about FR_18 { inputs = ("Component/design model revisions", "discipline and Omniverse coupling profiles", "whole-CUBICS model/scenario revisions", "spacecraft/subsystem scenario histories", "directed mappings", "returned tool responses"); outputs = ("Exchanged component/design models", "mapped EPS analysis inputs", "EPS states/results returned to the same whole-CUBICS scenario", "mapping findings", "execution status", "transfer limitations"); }
    #derivation connection derive_MR_03_FR_18 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_18; }
    #derivation connection derive_MR_04_FR_18 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_18; }
    #derivation connection derive_MR_05_FR_18 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_18; }
    #derivation connection derive_MR_06_FR_18 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_18; }
    #sourceTrace dependency scenario_FR18_SC03 from FR_18 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR18_SC04 from FR_18 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR18_F04 from FR_18 to BoundaryViews::F04;
    requirement <'FR-21'> FR_21 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall associate each model-supported conclusion with intended use, selected fidelity, included and omitted mechanisms, numerical checks, validity domain, uncertainty, calibration evidence and independent assessment evidence or explicit gaps, with engineer-approved prediction-error rules. */
    }
    @SourceRecord about FR_21 { identifier = "FR-21"; sourceText = "The framework shall associate each model-supported conclusion with intended use, selected fidelity, included and omitted mechanisms, numerical checks, validity domain, uncertainty, calibration evidence and independent assessment evidence or explicit gaps, with engineer-approved prediction-error rules."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 5.3--5.4, Casado 2--4 and Zhu pp.7--9"; }
    @PlannedRequirementCheck about FR_21 { theme = "Simulation and model credibility"; methods = "I,T"; checkSummary = "Attempt conclusions outside validity and with missing independent evidence."; }
    #derivation connection derive_MR_03_FR_21 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_21; }
    #derivation connection derive_MR_04_FR_21 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_21; }
    #derivation connection derive_MR_05_FR_21 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_21; }
    #derivation connection derive_MR_06_FR_21 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_21; }
    #sourceTrace dependency scenario_FR21_SC03 from FR_21 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR21_SC04 from FR_21 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR21_SC05 from FR_21 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR21_F04 from FR_21 to BoundaryViews::F04;
    requirement <'FR-22'> FR_22 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall propose identified model calibration or parameter revisions from quality-checked supplied reference data, retaining prior/revised values, data revisions, residuals, uncertainty and affected analyses separately from independent model assessment. */
    }
    @SourceRecord about FR_22 { identifier = "FR-22"; sourceText = "The framework shall propose identified model calibration or parameter revisions from quality-checked supplied reference data, retaining prior/revised values, data revisions, residuals, uncertainty and affected analyses separately from independent model assessment."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Zhu pp.7--9 and NASA 6.5"; }
    @PlannedRequirementCheck about FR_22 { theme = "Simulation and model credibility"; methods = "A,T"; checkSummary = "Calibrate from supplied data, retain separate assessment data and decline an update."; }
    #derivation connection derive_MR_03_FR_22 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_22; }
    #derivation connection derive_MR_04_FR_22 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_22; }
    #derivation connection derive_MR_05_FR_22 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_22; }
    #derivation connection derive_MR_06_FR_22 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_22; }
    #sourceTrace dependency scenario_FR22_SC03 from FR_22 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR22_SC04 from FR_22 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR22_SC05 from FR_22 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR22_F04 from FR_22 to BoundaryViews::F04;
    requirement <'FR-23'> FR_23 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain the fidelity, solver and coupling configuration, time step, convergence rules, execution environment, required resources and estimated/measured runtime for each analysis, MIL or SIL run, with unmet resource or numerical limits reported. */
    }
    @SourceRecord about FR_23 { identifier = "FR-23"; sourceText = "The framework shall retain the fidelity, solver and coupling configuration, time step, convergence rules, execution environment, required resources and estimated/measured runtime for each analysis, MIL or SIL run, with unmet resource or numerical limits reported."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "OOSEM 17.3.3 and Boan 2--4"; }
    @PlannedRequirementCheck about FR_23 { theme = "Simulation and model credibility"; methods = "I,T"; checkSummary = "Change the time step, solver and resource limits and inspect the run configuration and findings."; }
    #derivation connection derive_MR_03_FR_23 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_23; }
    #derivation connection derive_MR_04_FR_23 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_23; }
    #derivation connection derive_MR_05_FR_23 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_23; }
    #derivation connection derive_MR_06_FR_23 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_23; }
    #sourceTrace dependency scenario_FR23_SC03 from FR_23 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR23_SC04 from FR_23 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR23_F04 from FR_23 to BoundaryViews::F04;
    requirement <'FR-26'> FR_26 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall identify reliability, availability and maintainability analyses applicable to the designated EPS requirements, ConOps and risks, retaining the chosen measures, failure/repair assumptions, method coverage and reasons for exclusions. */
    }
    @SourceRecord about FR_26 { identifier = "FR-26"; sourceText = "The framework shall identify reliability, availability and maintainability analyses applicable to the designated EPS requirements, ConOps and risks, retaining the chosen measures, failure/repair assumptions, method coverage and reasons for exclusions."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "OOSEM 17.3.3 failure analysis and NASA 4.2"; }
    @PlannedRequirementCheck about FR_26 { theme = "Simulation and model credibility"; methods = "I,T"; checkSummary = "Assess applicability with and without repair or redundancy assumptions."; }
    #derivation connection derive_MR_03_FR_26 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_26; }
    #derivation connection derive_MR_04_FR_26 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_26; }
    #derivation connection derive_MR_05_FR_26 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_26; }
    #derivation connection derive_MR_06_FR_26 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_26; }
    #sourceTrace dependency scenario_FR26_SC03 from FR_26 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR26_SC05 from FR_26 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR26_F04 from FR_26 to BoundaryViews::F04;
    requirement <'FR-27'> FR_27 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall generate the selected RAM analysis representation from identified functions, components and failure dependencies using declared transformation rules, preserving sourced or missing failure/repair data and uncertainty in the reported results. */
    }
    @SourceRecord about FR_27 { identifier = "FR-27"; sourceText = "The framework shall generate the selected RAM analysis representation from identified functions, components and failure dependencies using declared transformation rules, preserving sourced or missing failure/repair data and uncertainty in the reported results."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "OOSEM 17.3.3 and 17.3.6"; }
    @PlannedRequirementCheck about FR_27 { theme = "Simulation and model credibility"; methods = "A,T"; checkSummary = "Compare transformations and results with a reference and leave missing rates unresolved."; }
    #derivation connection derive_MR_03_FR_27 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_27; }
    #derivation connection derive_MR_04_FR_27 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_27; }
    #sourceTrace dependency scenario_FR27_SC03 from FR_27 to ScenarioViews::SC03;
    #sourceTrace dependency function_FR27_F04 from FR_27 to BoundaryViews::F04;
    requirement <'FR-31'> FR_31 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain and check scenario time bases, sample and receipt times, sampling, synchronization and known calculation/interface delays for simulated or supplied reference histories, including coupled exchanges, against declared timing rules, reporting missing timing data and exceeded synchronization limits. */
    }
    @SourceRecord about FR_31 { identifier = "FR-31"; sourceText = "The framework shall retain and check scenario time bases, sample and receipt times, sampling, synchronization and known calculation/interface delays for simulated or supplied reference histories, including coupled exchanges, against declared timing rules, reporting missing timing data and exceeded synchronization limits."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Boan 2--4, NASA 5.3--5.4, Casado 3 timing distinctions and handpicked-0001 (Zhu) pp.4--5 data mappings/update rates. No hard real-time obligation."; }
    @PlannedRequirementCheck about FR_31 { theme = "Simulation and model credibility"; methods = "A,T"; checkSummary = "Seed clock offset, delayed/out-of-order samples and missing timing. Compare checked alignments, delays and exceeded/unknown limits with fixed timing references. Distinguish scenario/sample/receipt times, scene update rate and numerical time step."; }
    @RequirementExchange about FR_31 { inputs = ("Exchanged/simulated/reference histories", "scenario time references", "sampling/exchange timing", "synchronization rules and limits", "known delays"); outputs = ("Timing and synchronization records", "checked alignments", "timing gaps", "limit findings"); }
    #derivation connection derive_MR_03_FR_31 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_31; }
    #derivation connection derive_MR_04_FR_31 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_31; }
    #derivation connection derive_MR_05_FR_31 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_31; }
    #derivation connection derive_MR_06_FR_31 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_31; }
    #sourceTrace dependency scenario_FR31_SC03 from FR_31 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR31_SC04 from FR_31 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR31_SC05 from FR_31 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR31_F04 from FR_31 to BoundaryViews::F04;
    requirement <'FR-32'> FR_32 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall check exchanged, simulated and supplied reference histories for entity/channel identity, units, timing, completeness and validity before numerical use, preserving raw values, invalid samples, missing intervals and processing masks without treating missing or inactive readings as zero. */
    }
    @SourceRecord about FR_32 { identifier = "FR-32"; sourceText = "The framework shall check exchanged, simulated and supplied reference histories for entity/channel identity, units, timing, completeness and validity before numerical use, preserving raw values, invalid samples, missing intervals and processing masks without treating missing or inactive readings as zero."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 5.3--5.4 and handpicked-0001 (Zhu) pp.4--5 entity/unit/data mappings and pp.7--9 assessment basis"; }
    @PlannedRequirementCheck about FR_32 { theme = "Simulation and model credibility"; methods = "T"; checkSummary = "Seed wrong entity/channel/revision, unit/sign/frame mismatch and missing, inactive or invalid samples. Compare admission findings and masks with a fixed reference before numerical use. Preserve raw histories and unchanged controlled content for rejected transfers."; }
    @RequirementExchange about FR_32 { inputs = ("Exchanged/simulated/reference histories", "entity/channel mappings", "quantity/unit definitions", "timing metadata", "validity rules"); outputs = ("Admission/quality findings", "preserved raw histories", "invalid/missing/inactive status", "processing masks"); }
    #derivation connection derive_MR_03_FR_32 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_32; }
    #derivation connection derive_MR_04_FR_32 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_32; }
    #derivation connection derive_MR_05_FR_32 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_32; }
    #derivation connection derive_MR_06_FR_32 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_32; }
    #sourceTrace dependency scenario_FR32_SC03 from FR_32 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR32_SC04 from FR_32 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR32_SC05 from FR_32 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR32_F04 from FR_32 to BoundaryViews::F04;
    requirement <'FR-33'> FR_33 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain revision-linked modeled EPS interfaces and command, telemetry, event and parameter definitions with endpoint ownership, directions, identifiers, types, units, ranges, polarity, time/mode meaning and encodings. */
    }
    @SourceRecord about FR_33 { identifier = "FR-33"; sourceText = "The framework shall retain revision-linked modeled EPS interfaces and command, telemetry, event and parameter definitions with endpoint ownership, directions, identifiers, types, units, ranges, polarity, time/mode meaning and encodings."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.3, Campioli 3--4 and review-0853 (Halvorson and Thomas) Secs.3--4 interface/ground-definition mapping"; }
    @PlannedRequirementCheck about FR_33 { theme = "Detailed interfaces and host software"; methods = "I,T"; checkSummary = "Round-trip endpoint ownership/directions and all interface and ground-definition fields. Reject inconsistent identifiers, types, units, ranges, polarity and temporal meanings against an independent reference. Structural checks supply no behavior verdict."; }
    @RequirementExchange about FR_33 { inputs = ("Modeled EPS endpoint/port interfaces", "command, telemetry, event and parameter definitions"); outputs = ("Revision-linked EPS interface and ground-definition specifications"); }
    #derivation connection derive_MR_02_FR_33 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_33; }
    #derivation connection derive_MR_04_FR_33 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_33; }
    #derivation connection derive_MR_05_FR_33 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_33; }
    #derivation connection derive_MR_06_FR_33 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_33; }
    #sourceTrace dependency scenario_FR33_SC02 from FR_33 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR33_SC04 from FR_33 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR33_F05 from FR_33 to BoundaryViews::F05;
    requirement <'FR-34'> FR_34 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall produce or coordinate checked mappings of the EPS interface specification to the required versioned F Prime host integration profile, covering component, port, topology, command, telemetry, event and parameter definitions and identifying version compatibility, unsupported behavior and lossy translations. */
    }
    @SourceRecord about FR_34 { identifier = "FR-34"; sourceText = "The framework shall produce or coordinate checked mappings of the EPS interface specification to the required versioned F Prime host integration profile, covering component, port, topology, command, telemetry, event and parameter definitions and identifying version compatibility, unsupported behavior and lossy translations."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Stakeholder F Prime constraint, NASA 3.6 and 6.3, review-0853 (Halvorson and Thomas) Secs.3--4 architecture/ground-definition mapping and handwritten behavior distinction. No complete behavior generation or FPP-only mandate."; }
    @PlannedRequirementCheck about FR_34 { theme = "Detailed interfaces and host software"; methods = "D,T"; checkSummary = "Compare required F Prime component/instance/port/topology and command/telemetry/event/parameter mappings with an independent reference at declared actual profile/tool/representation versions. Seed conflicts, wrong directions/types, missing meanings and incompatible versions. Retain unsupported behavior and lossy translations."; }
    @RequirementExchange about FR_34 { inputs = ("EPS interface specification", "software component/instance ownership and connectivity", "required F Prime profile", "supported representation/tool versions"); outputs = ("Checked F Prime mappings and definitions", "compatibility findings", "unsupported/lossy-translation records"); }
    #derivation connection derive_MR_05_FR_34 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_34; }
    #derivation connection derive_MR_06_FR_34 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_34; }
    #sourceTrace dependency scenario_FR34_SC04 from FR_34 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR34_F05 from FR_34 to BoundaryViews::F05;
    requirement <'FR-35'> FR_35 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall specify and check modeled EPS command preconditions, order, effects, rejection/failure behavior, mode transitions, protection and recovery responsibilities against the declared control and interface requirements. */
    }
    @SourceRecord about FR_35 { identifier = "FR-35"; sourceText = "The framework shall specify and check modeled EPS command preconditions, order, effects, rejection/failure behavior, mode transitions, protection and recovery responsibilities against the declared control and interface requirements."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Casado 2--4 and NASA 3.6"; }
    @PlannedRequirementCheck about FR_35 { theme = "Detailed interfaces and host software"; methods = "A,T"; checkSummary = "Exercise nominal, rejected, protection and recovery sequences in simulated conditions."; }
    @RequirementExchange about FR_35 { inputs = ("Modeled command/control behavior", "control/interface requirements"); outputs = ("Checked behavior specifications", "discrepancy findings"); }
    #derivation connection derive_MR_05_FR_35 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_35; }
    #derivation connection derive_MR_06_FR_35 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_35; }
    #sourceTrace dependency scenario_FR35_SC04 from FR_35 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR35_F05 from FR_35 to BoundaryViews::F05;
    requirement <'FR-36'> FR_36 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall coordinate coding and host building of declared F Prime EPS control/interface flight software through an external toolchain only from a current engineer-authorized detailed design release, retaining source/build revisions, toolchain versions, dependencies, host configuration, logs and failures. */
    }
    @SourceRecord about FR_36 { identifier = "FR-36"; sourceText = "The framework shall coordinate coding and host building of declared F Prime EPS control/interface flight software through an external toolchain only from a current engineer-authorized detailed design release, retaining source/build revisions, toolchain versions, dependencies, host configuration, logs and failures."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Stakeholder F Prime/host-only constraints, NASA 3.6 and 6.7 Table 6.7-1 CDR-before-coding rule, review-0853 (Halvorson and Thomas) Secs.3--4 written/reused behavior and build dependencies"; }
    @PlannedRequirementCheck about FR_36 { theme = "Detailed interfaces and host software"; methods = "D,T"; checkSummary = "Reject stale, unreleased and unauthorized design requests. Coordinate an authorized current-release F Prime host build, retaining exact source/build, toolchain/dependency/host revisions, logs and generation/compilation failures. Review acceptance cannot replace exact authorization. Build success supplies no SIL verdict."; }
    @RequirementExchange about FR_36 { inputs = ("Current authorized design/interface release", "declared software scope", "F Prime mappings", "host/toolchain/dependency configuration", "returned tool responses"); outputs = ("Authorized coding/build requests", "retained source/build products", "exact configuration records", "logs", "failures"); }
    #derivation connection derive_MR_06_FR_36 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_36; }
    #sourceTrace dependency scenario_FR36_SC04 from FR_36 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR36_F05 from FR_36 to BoundaryViews::F05;
    requirement <'FR-19'> FR_19 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall coordinate MIL assessment of modeled EPS control against the plant and mission scenarios for nominal operation, load/supply changes, mode transitions, selected faults, protection and recovery, retaining stimuli, expected/actual responses, criteria and failures. */
    }
    @SourceRecord about FR_19 { identifier = "FR-19"; sourceText = "The framework shall coordinate MIL assessment of modeled EPS control against the plant and mission scenarios for nominal operation, load/supply changes, mode transitions, selected faults, protection and recovery, retaining stimuli, expected/actual responses, criteria and failures."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Casado 2 and NASA 5.3--5.4"; }
    @PlannedRequirementCheck about FR_19 { theme = "Detailed interfaces and host software"; methods = "D,T"; checkSummary = "Run declared nominal and fault sequences with a simulated plant and retain stimuli, expected/actual state/event responses and failed criteria for matched SIL comparison."; }
    @RequirementExchange about FR_19 { inputs = ("Controller/plant models", "mission scenarios", "MIL criteria"); outputs = ("MIL requests", "retained stimuli/responses", "criterion outcomes/failures"); }
    #derivation connection derive_MR_05_FR_19 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_19; }
    #derivation connection derive_MR_06_FR_19 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_19; }
    #sourceTrace dependency scenario_FR19_SC04 from FR_19 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR19_F05 from FR_19 to BoundaryViews::F05;
    requirement <'FR-24'> FR_24 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall coordinate SIL assessment of released F Prime host-executed EPS control/interface software with simulated EPS and subsystem products connected to NVIDIA Omniverse whole-CUBICS simulation, reporting requirement/ConOps outcomes and differences from corresponding MIL results for the same scenarios and comparison rules. */
    }
    @SourceRecord about FR_24 { identifier = "FR-24"; sourceText = "The framework shall coordinate SIL assessment of released F Prime host-executed EPS control/interface software with simulated EPS and subsystem products connected to NVIDIA Omniverse whole-CUBICS simulation, reporting requirement/ConOps outcomes and differences from corresponding MIL results for the same scenarios and comparison rules."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Stakeholder F Prime/Omniverse and host-only constraints, handpicked-0001 (Zhu) p.3 SIL definition and scope, NASA 5.3--5.4. No executed CUBICS SIL evidence."; }
    @PlannedRequirementCheck about FR_24 { theme = "Detailed interfaces and host software"; methods = "A,T"; checkSummary = "Execute released F Prime host software with simulated EPS/subsystem products connected to the same whole-CUBICS scenario. Use matched MIL results and fixed comparison rules. Seed a code/interface discrepancy and failed/partial runs. Retain raw host responses, requirement/ConOps outcomes, differences, status and limits. Builds and scene updates supply no SIL evidence."; }
    @RequirementExchange about FR_24 { inputs = ("Released F Prime host code/build", "simulated EPS/subsystem products", "whole-CUBICS scenario and coupling-profile revisions", "matched MIL results", "fixed comparison rules"); outputs = ("SIL requests", "retained host responses", "requirement/ConOps outcomes", "MIL/SIL differences with execution status and limits"); }
    #derivation connection derive_MR_06_FR_24 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_24; }
    #sourceTrace dependency scenario_FR24_SC04 from FR_24 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR24_F05 from FR_24 to BoundaryViews::F05;
    requirement <'FR-28'> FR_28 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain EPS phase-product verification and validation plans with distinct requirement and expectation/ConOps references, subject configuration, method, conditions, inputs, expected response, criteria, observations, applicability limits and planned/executed status. */
    }
    @SourceRecord about FR_28 { identifier = "FR-28"; sourceText = "The framework shall retain EPS phase-product verification and validation plans with distinct requirement and expectation/ConOps references, subject configuration, method, conditions, inputs, expected response, criteria, observations, applicability limits and planned/executed status."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 2.4 and 5.3--5.4"; }
    @PlannedRequirementCheck about FR_28 { theme = "Evidence, controlled changes and reviews"; methods = "I,T"; checkSummary = "Distinguish planned activities from results and verification criteria from validation expectations."; }
    #derivation connection derive_MR_01_FR_28 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_28; }
    #derivation connection derive_MR_02_FR_28 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_28; }
    #derivation connection derive_MR_03_FR_28 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_28; }
    #derivation connection derive_MR_04_FR_28 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_28; }
    #derivation connection derive_MR_05_FR_28 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_28; }
    #derivation connection derive_MR_06_FR_28 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_28; }
    #sourceTrace dependency scenario_FR28_SC02 from FR_28 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR28_SC04 from FR_28 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR28_SC05 from FR_28 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR28_F06 from FR_28 to BoundaryViews::F06;
    requirement <'FR-05'> FR_05 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall identify reciprocal impacts of a proposed mission, requirement, component, interface, model or software change on EPS/non-EPS allocations, budgets, trades, plans, guidance and evidence, reporting unresolved dependencies and required reassessments. */
    }
    @SourceRecord about FR_05 { identifier = "FR-05"; sourceText = "The framework shall identify reciprocal impacts of a proposed mission, requirement, component, interface, model or software change on EPS/non-EPS allocations, budgets, trades, plans, guidance and evidence, reporting unresolved dependencies and required reassessments."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.2--6.5 and Gateau 3.2"; }
    @PlannedRequirementCheck about FR_05 { theme = "Evidence, controlled changes and reviews"; methods = "A,T"; checkSummary = "Compare the impact set of coupled load, pointing and interface changes with an expert reference."; }
    #derivation connection derive_MR_01_FR_05 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_05; }
    #derivation connection derive_MR_02_FR_05 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_05; }
    #derivation connection derive_MR_03_FR_05 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_05; }
    #derivation connection derive_MR_04_FR_05 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_05; }
    #derivation connection derive_MR_05_FR_05 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_05; }
    #derivation connection derive_MR_06_FR_05 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_05; }
    #sourceTrace dependency scenario_FR05_SC05 from FR_05 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR05_F07 from FR_05 to BoundaryViews::F07;
    requirement <'FR-06'> FR_06 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall issue a distinct successor baseline only for an authorized engineering change decision, preserving its predecessor, request, rationale, findings and dispositions and identifying regenerated, stale and unresolved products and evidence. */
    }
    @SourceRecord about FR_06 { identifier = "FR-06"; sourceText = "The framework shall issue a distinct successor baseline only for an authorized engineering change decision, preserving its predecessor, request, rationale, findings and dispositions and identifying regenerated, stale and unresolved products and evidence."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.2 and 6.5"; }
    @PlannedRequirementCheck about FR_06 { theme = "Evidence, controlled changes and reviews"; methods = "T"; checkSummary = "Accept, decline and interrupt changes without erasing the predecessor."; }
    #derivation connection derive_MR_01_FR_06 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_06; }
    #derivation connection derive_MR_02_FR_06 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_06; }
    #derivation connection derive_MR_03_FR_06 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_06; }
    #derivation connection derive_MR_04_FR_06 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_06; }
    #derivation connection derive_MR_05_FR_06 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_06; }
    #derivation connection derive_MR_06_FR_06 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_06; }
    #sourceTrace dependency scenario_FR06_SC05 from FR_06 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR06_F07 from FR_06 to BoundaryViews::F07;
    requirement <'FR-07'> FR_07 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain retrievable phase baselines that resolve exact requirement, mission, design, model, software, interface and evidence revisions with revision history and the authorized decisions that control them. */
    }
    @SourceRecord about FR_07 { identifier = "FR-07"; sourceText = "The framework shall retain retrievable phase baselines that resolve exact requirement, mission, design, model, software, interface and evidence revisions with revision history and the authorized decisions that control them."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.5--6.6"; }
    @PlannedRequirementCheck about FR_07 { theme = "Evidence, controlled changes and reviews"; methods = "I,T"; checkSummary = "Reconstruct predecessor and successor manifests and all applicable products."; }
    #derivation connection derive_MR_01_FR_07 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_07; }
    #derivation connection derive_MR_02_FR_07 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_07; }
    #derivation connection derive_MR_03_FR_07 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_07; }
    #derivation connection derive_MR_04_FR_07 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_07; }
    #derivation connection derive_MR_05_FR_07 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_07; }
    #derivation connection derive_MR_06_FR_07 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_07; }
    #sourceTrace dependency scenario_FR07_SC05 from FR_07 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR07_F07 from FR_07 to BoundaryViews::F07;
    requirement <'FR-08'> FR_08 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall check transferred identities, revisions, structure, quantities, units, polarity, time/mode meanings and provenance against the declared interface specification before registration, retaining incompatible raw submissions and findings without replacing controlled content. */
    }
    @SourceRecord about FR_08 { identifier = "FR-08"; sourceText = "The framework shall check transferred identities, revisions, structure, quantities, units, polarity, time/mode meanings and provenance against the declared interface specification before registration, retaining incompatible raw submissions and findings without replacing controlled content."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.3 and 6.5--6.6"; }
    @PlannedRequirementCheck about FR_08 { theme = "Evidence, controlled changes and reviews"; methods = "T"; checkSummary = "Inject identity, unit, sign and revision mismatches at each active interface."; }
    #derivation connection derive_MR_01_FR_08 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_08; }
    #derivation connection derive_MR_02_FR_08 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_08; }
    #derivation connection derive_MR_03_FR_08 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_08; }
    #derivation connection derive_MR_04_FR_08 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_08; }
    #derivation connection derive_MR_05_FR_08 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_08; }
    #derivation connection derive_MR_06_FR_08 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_08; }
    #sourceTrace dependency scenario_FR08_SC02 from FR_08 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR08_SC03 from FR_08 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR08_SC04 from FR_08 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR08_SC05 from FR_08 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR08_F07 from FR_08 to BoundaryViews::F07;
    requirement <'FR-09'> FR_09 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall associate each analysis or software result with its requirement/expectation, method, scenario, design/model/software/input revisions, parameters, producer, execution environment, raw outputs, logs and execution status, preserving failed, cancelled and partial runs. */
    }
    @SourceRecord about FR_09 { identifier = "FR-09"; sourceText = "The framework shall associate each analysis or software result with its requirement/expectation, method, scenario, design/model/software/input revisions, parameters, producer, execution environment, raw outputs, logs and execution status, preserving failed, cancelled and partial runs."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 5.3--5.4 and 6.6"; }
    @PlannedRequirementCheck about FR_09 { theme = "Evidence, controlled changes and reviews"; methods = "I,T"; checkSummary = "Trace successful, failed, cancelled and partial outputs to their configurations."; }
    #derivation connection derive_MR_01_FR_09 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_09; }
    #derivation connection derive_MR_02_FR_09 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_09; }
    #derivation connection derive_MR_03_FR_09 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_09; }
    #derivation connection derive_MR_04_FR_09 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_09; }
    #derivation connection derive_MR_05_FR_09 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_09; }
    #derivation connection derive_MR_06_FR_09 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_09; }
    #sourceTrace dependency scenario_FR09_SC03 from FR_09 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR09_SC04 from FR_09 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR09_SC05 from FR_09 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR09_F07 from FR_09 to BoundaryViews::F07;
    requirement <'FR-10'> FR_10 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall provide the controlled inputs, dependencies and instructions to reconstruct a designated analysis or MIL/SIL run and compare its raw outputs using result-specific rules and tolerances fixed before replay, retaining comparison failures and missing dependencies. */
    }
    @SourceRecord about FR_10 { identifier = "FR-10"; sourceText = "The framework shall provide the controlled inputs, dependencies and instructions to reconstruct a designated analysis or MIL/SIL run and compare its raw outputs using result-specific rules and tolerances fixed before replay, retaining comparison failures and missing dependencies."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 5.3--5.4 and OOSEM 17.3.3 stores"; }
    @PlannedRequirementCheck about FR_10 { theme = "Evidence, controlled changes and reviews"; methods = "D,T"; checkSummary = "Independently replay in the declared host environment and compare under fixed tolerances."; }
    #derivation connection derive_MR_01_FR_10 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_10; }
    #derivation connection derive_MR_02_FR_10 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_10; }
    #derivation connection derive_MR_03_FR_10 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_10; }
    #derivation connection derive_MR_04_FR_10 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_10; }
    #derivation connection derive_MR_05_FR_10 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_10; }
    #derivation connection derive_MR_06_FR_10 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_10; }
    #sourceTrace dependency scenario_FR10_SC05 from FR_10 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR10_F04 from FR_10 to BoundaryViews::F04;
    requirement <'FR-11'> FR_11 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall report missing, rejected, stale, failed, out-of-domain and unresolved evidence against the affected requirements, expectations and conclusions with criticality, owner and disposition, preventing unqualified current conformity claims from affected critical gaps. */
    }
    @SourceRecord about FR_11 { identifier = "FR-11"; sourceText = "The framework shall report missing, rejected, stale, failed, out-of-domain and unresolved evidence against the affected requirements, expectations and conclusions with criticality, owner and disposition, preventing unqualified current conformity claims from affected critical gaps."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 5.3--5.4 and 6.7"; }
    @PlannedRequirementCheck about FR_11 { theme = "Evidence, controlled changes and reviews"; methods = "T"; checkSummary = "Seed every evidence status and attempt a current claim with a blocking gap."; }
    #derivation connection derive_MR_01_FR_11 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_11; }
    #derivation connection derive_MR_02_FR_11 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_11; }
    #derivation connection derive_MR_03_FR_11 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_11; }
    #derivation connection derive_MR_04_FR_11 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_11; }
    #derivation connection derive_MR_05_FR_11 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_11; }
    #derivation connection derive_MR_06_FR_11 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_11; }
    #sourceTrace dependency scenario_FR11_SC05 from FR_11 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR11_F06 from FR_11 to BoundaryViews::F06;
    requirement <'FR-37'> FR_37 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall generate filtered mission, requirement-allocation, design, interface and analysis views from controlled EPS records with baseline identification, readable units, legends and links to represented records. */
    }
    @SourceRecord about FR_37 { identifier = "FR-37"; sourceText = "The framework shall generate filtered mission, requirement-allocation, design, interface and analysis views from controlled EPS records with baseline identification, readable units, legends and links to represented records."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "OOSEM 17.3.3 and NASA 6.7"; }
    @PlannedRequirementCheck about FR_37 { theme = "Evidence, controlled changes and reviews"; methods = "I,D"; checkSummary = "Compare views with their source baseline and follow represented record links."; }
    #derivation connection derive_MR_01_FR_37 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_37; }
    #derivation connection derive_MR_02_FR_37 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_37; }
    #derivation connection derive_MR_03_FR_37 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_37; }
    #derivation connection derive_MR_04_FR_37 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_37; }
    #derivation connection derive_MR_05_FR_37 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_37; }
    #derivation connection derive_MR_06_FR_37 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_37; }
    #sourceTrace dependency scenario_FR37_SC01 from FR_37 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR37_SC02 from FR_37 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR37_SC03 from FR_37 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR37_SC04 from FR_37 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR37_SC05 from FR_37 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR37_F08 from FR_37 to BoundaryViews::F08;
    requirement <'FR-38'> FR_38 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall assemble a phase-baseline review package against the designated MCR, SRR, MDR/SDR, PDR, scoped CDR or scoped SIR entrance and success criteria, including applicable coverage, decisions, design, evidence, model limits, risks, gaps and finding dispositions. */
    }
    @SourceRecord about FR_38 { identifier = "FR-38"; sourceText = "The framework shall assemble a phase-baseline review package against the designated MCR, SRR, MDR/SDR, PDR, scoped CDR or scoped SIR entrance and success criteria, including applicable coverage, decisions, design, evidence, model limits, risks, gaps and finding dispositions."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 3.3--3.6 and 6.7"; }
    @PlannedRequirementCheck about FR_38 { theme = "Evidence, controlled changes and reviews"; methods = "I,D"; checkSummary = "Prepare phase-specific packages, including CDR design release and SIR released-product evidence."; }
    #derivation connection derive_MR_01_FR_38 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_38; }
    #derivation connection derive_MR_02_FR_38 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_38; }
    #derivation connection derive_MR_03_FR_38 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_38; }
    #derivation connection derive_MR_04_FR_38 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_38; }
    #derivation connection derive_MR_05_FR_38 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_38; }
    #derivation connection derive_MR_06_FR_38 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_38; }
    #sourceTrace dependency scenario_FR38_SC05 from FR_38 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR38_F08 from FR_38 to BoundaryViews::F08;
    requirement <'FR-42'> FR_42 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall record a technical review disposition only from the designated authorized review authority against the identified baseline and agreed scoped success criteria, distinguishing prepared, accepted, conditional and progression-blocked status with rationale, conditions, closure actions, owners and dates. */
    }
    @SourceRecord about FR_42 { identifier = "FR-42"; sourceText = "The framework shall record a technical review disposition only from the designated authorized review authority against the identified baseline and agreed scoped success criteria, distinguishing prepared, accepted, conditional and progression-blocked status with rationale, conditions, closure actions, owners and dates."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.7 and 6.8"; }
    @PlannedRequirementCheck about FR_42 { theme = "Evidence, controlled changes and reviews"; methods = "I,T"; checkSummary = "Reject unauthorized or stale-baseline decisions and exercise blocking and conditional findings."; }
    #derivation connection derive_MR_01_FR_42 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_42; }
    #derivation connection derive_MR_02_FR_42 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_42; }
    #derivation connection derive_MR_03_FR_42 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_42; }
    #derivation connection derive_MR_04_FR_42 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_42; }
    #derivation connection derive_MR_05_FR_42 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_42; }
    #derivation connection derive_MR_06_FR_42 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_42; }
    #sourceTrace dependency scenario_FR42_SC05 from FR_42 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR42_F08 from FR_42 to BoundaryViews::F08;

    item def PerformanceMeasure :> EngineeringArtifact {
        doc /* Planned framework measurement protocols supply no satisfaction or empirical verdict.
         * Declare workload, configuration, references and comparison rules before assessment.
         * State each proportion's numerator and denominator, including precision and recall reference sets.
         * Report defect families, discipline profiles and criticality classes separately.
         * Retain failures, unsupported cases, abstentions and exclusions with their reasons.
         * Independent calculation agreement using the same model is distinct from physical prediction validity.
         * Per-case functional checks imply no automatic 100 percent or zero desired target.
         * MOE contributions are qualitative. MOE-04 concerns adoption burden only.
         */
        attribute observationBasis : ScalarValues::String;
        attribute units : ScalarValues::String;
        attribute protocol : ScalarValues::String;
        attribute referenceConfiguration : ScalarValues::String;
        attribute target : ScalarValues::String = "";
        attribute targetSource : ScalarValues::String = "";
        attribute achieved : ScalarValues::String = "unknown, no empirical evaluation";
    }
    item <'MOP-FR01'> MOP_FR01 : PerformanceMeasure {
        attribute :>> observationBasis = "Requirement record fidelity. Share of reference records recovered with correct fields, revisions and resolution reasons after creation, editing and export/import.";
        attribute :>> units = "% of exercised records";
        attribute :>> protocol = "Compare controlled quantitative, qualitative, unresolved and inapplicable records with an independent source set under declared record volumes.";
        attribute :>> referenceConfiguration = "FR-01 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR02'> MOP_FR02 : PerformanceMeasure {
        attribute :>> observationBasis = "Drafting finding quality. Precision and recall for each defect family, with critical misses, false findings, abstentions and source/explanation errors reported separately.";
        attribute :>> units = "precision and recall fractions, counts";
        attribute :>> protocol = "Use blind independent expert labels, clean controls and seeded defects. Separate deterministic defects from probable duplicates, coverage gaps and source conflicts.";
        attribute :>> referenceConfiguration = "FR-02 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR03'> MOP_FR03 : PerformanceMeasure {
        attribute :>> observationBasis = "Recommendation applicability. Precision and recall of eligible methods/models against expert references, with rationale/source correctness and no-eligible-option outcomes reported separately.";
        attribute :>> units = "precision and recall fractions, counts";
        attribute :>> protocol = "Fix eligible option sets by phase, question, inputs, validity, scope and resources. Label derivation, analysis, verification and validation queries independently.";
        attribute :>> referenceConfiguration = "FR-03 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR04'> MOP_FR04 : PerformanceMeasure {
        attribute :>> observationBasis = "Trace retrieval quality. Precision and recall of returned forward/reverse relations and endpoint-gap findings against a known reference graph.";
        attribute :>> units = "precision and recall fractions";
        attribute :>> protocol = "Query declared expectation, ConOps, requirement, allocation, interface, decision and evidence reference sets, including missing and ambiguous endpoints.";
        attribute :>> referenceConfiguration = "FR-04 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR05'> MOP_FR05 : PerformanceMeasure {
        attribute :>> observationBasis = "Change-impact quality. Precision and recall of reciprocal impact sets against independent reference changes, with missed critical impacts and unresolved dependencies reported separately.";
        attribute :>> units = "precision and recall fractions, counts";
        attribute :>> protocol = "Exercise mission, requirement, component, interface, model and software changes in both EPS/non-EPS directions under fixed dependency sets.";
        attribute :>> referenceConfiguration = "FR-05 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR06'> MOP_FR06 : PerformanceMeasure {
        attribute :>> observationBasis = "Successor-baseline handling accuracy. Share of change sequences that produce the correct authorized successor and retain the predecessor, decision links and product status.";
        attribute :>> units = "% of exercised change sequences";
        attribute :>> protocol = "Compare independent event/state references for accepted, declined, unauthorized, concurrent and interrupted changes.";
        attribute :>> referenceConfiguration = "FR-06 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR07'> MOP_FR07 : PerformanceMeasure {
        attribute :>> observationBasis = "Baseline retrieval reliability. Share of retrieval requests that recover the exact applicable revisions, controlling decisions and history, with retrieval time reported separately.";
        attribute :>> units = "% of retrieval requests, seconds";
        attribute :>> protocol = "Retrieve predecessor and successor baselines after later edits and a declared restore. Compare independent manifests and content.";
        attribute :>> referenceConfiguration = "FR-07 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR08'> MOP_FR08 : PerformanceMeasure {
        attribute :>> observationBasis = "Transfer admission error. False acceptance of incompatible submissions and false rejection of compatible submissions, with controlled-content corruption counted separately.";
        attribute :>> units = "fractions per reference submission class, counts";
        attribute :>> protocol = "Exercise each active interface using independently specified identity, revision, structure, quantity/unit, polarity, time/mode and provenance cases.";
        attribute :>> referenceConfiguration = "FR-08 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR09'> MOP_FR09 : PerformanceMeasure {
        attribute :>> observationBasis = "Result provenance fidelity. Share of retained results whose configuration links, raw outputs, logs and execution status match independent run records.";
        attribute :>> units = "% of exercised results";
        attribute :>> protocol = "Include successful, failed, cancelled and partial analyses/software runs, plus unknown dependency identities.";
        attribute :>> referenceConfiguration = "FR-09 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR10'> MOP_FR10 : PerformanceMeasure {
        attribute :>> observationBasis = "Independent replay success. Share of designated runs reconstructed with available declared dependencies and raw outputs satisfying rules fixed before replay.";
        attribute :>> units = "% of designated replay attempts";
        attribute :>> protocol = "Use an independent operator and clean declared host. Retain missing dependencies and failed comparisons in the attempt denominator, with exclusion reasons explicit.";
        attribute :>> referenceConfiguration = "FR-10 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR11'> MOP_FR11 : PerformanceMeasure {
        attribute :>> observationBasis = "Evidence-gap reporting quality. Precision and recall of gap-to-conclusion associations, with unsupported current conformity claims and missed critical gaps counted separately.";
        attribute :>> units = "precision and recall fractions, counts";
        attribute :>> protocol = "Seed missing, rejected, stale, failed, out-of-domain and unresolved evidence under independent criticality and claim-admission references.";
        attribute :>> referenceConfiguration = "FR-11 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR13'> MOP_FR13 : PerformanceMeasure {
        attribute :>> observationBasis = "Mass/volume calculation agreement. Absolute difference between framework estimates and independent calculations using the same component quantities, sources and declared roll-up or geometry method.";
        attribute :>> units = "kg and cubic metres, separately";
        attribute :>> protocol = "Exercise substitutions, unit conversions, uncertainty and unknown source values. No BOM or price obligation. Compare implementation arithmetic rather than fabricated EPS measurements.";
        attribute :>> referenceConfiguration = "FR-13 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR14'> MOP_FR14 : PerformanceMeasure {
        attribute :>> observationBasis = "Trade calculation agreement. Share of feasibility classifications and preference-order comparisons matching independent calculations under the same alternatives, inputs and approved criteria.";
        attribute :>> units = "% of evaluated classifications/comparisons";
        attribute :>> protocol = "Fix feasibility rules, weighting or ordering method and uncertainty cases. Report numerical measure/margin differences and ties separately. This concerns EPS concept trades, not selection of a framework candidate.";
        attribute :>> referenceConfiguration = "FR-14 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR15'> MOP_FR15 : PerformanceMeasure {
        attribute :>> observationBasis = "Design configuration fidelity. Share of parameter, variant and extension cases whose configured representations and allocations match their independent specifications.";
        attribute :>> units = "% of exercised configuration cases";
        attribute :>> protocol = "Include alternate EPS topologies and all required generation, storage, conversion, regulation, protection, distribution, control and interface representations.";
        attribute :>> referenceConfiguration = "FR-15 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR16'> MOP_FR16 : PerformanceMeasure {
        attribute :>> observationBasis = "Coupled-history calculation agreement. Maximum absolute error and root mean square error per channel against independent execution of the same declared EPS and mission model with matched inputs/time bases.";
        attribute :>> units = "per-channel result units, including W, Wh, V and state fraction";
        attribute :>> protocol = "Use nominal/degraded histories, transient shortages, illumination/eclipse, load and thermal changes. Keep numerical implementation agreement separate from physical prediction validity.";
        attribute :>> referenceConfiguration = "FR-16 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR17'> MOP_FR17 : PerformanceMeasure {
        attribute :>> observationBasis = "Allocation proposal agreement. Share of proposed allocations whose parent/source links and engineering quantities agree with independent application of the declared derivation method.";
        attribute :>> units = "% of exercised allocations, result-specific residual units";
        attribute :>> protocol = "Fix spacecraft requirements, scenarios, source quantities, unit conversions, assumptions and uncertainty. Record expert disagreement and engineer dispositions separately.";
        attribute :>> referenceConfiguration = "FR-17 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR18'> MOP_FR18 : PerformanceMeasure {
        attribute :>> observationBasis = "Model-exchange fidelity. Share of reference mapping items whose numerical, quantity/unit, geometry, identity and time/mode meanings are preserved across required discipline profiles and whole-CUBICS Omniverse coupling.";
        attribute :>> units = "% of reference mapping items, unreported-loss count";
        attribute :>> protocol = "Exercise incoming spacecraft/subsystem scenario histories and outgoing EPS states/results. Report every profile separately. Scene display alone supplies no numerical coupling evidence.";
        attribute :>> referenceConfiguration = "FR-18 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR19'> MOP_FR19 : PerformanceMeasure {
        attribute :>> observationBasis = "MIL orchestration accuracy. Share of prescribed MIL requests, returned stimuli/responses and criterion outcomes correctly coordinated and retained against independent run references.";
        attribute :>> units = "% of exercised MIL assessment cases";
        attribute :>> protocol = "Include nominal, transition, selected-fault, protection/recovery and failed runs. A correctly reported controller failure can be correct framework behavior.";
        attribute :>> referenceConfiguration = "FR-19 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR20'> MOP_FR20 : PerformanceMeasure {
        attribute :>> observationBasis = "Budget/sizing calculation agreement. Absolute errors against independent generation, demand, energy, array and battery calculations using identical declared inputs, equations and margins.";
        attribute :>> units = "W, Wh, square metres and Ah or selected sizing units, separately";
        attribute :>> protocol = "Use multiple mission modes, eclipse and degradation cases, including infeasible inputs. Residuals assess framework calculation correctness rather than the adequacy of product capacity.";
        attribute :>> referenceConfiguration = "FR-20 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR21'> MOP_FR21 : PerformanceMeasure {
        attribute :>> observationBasis = "Credibility association quality. Share of conclusions with correct intended-use and credibility links, with precision/recall of validity and missing-evidence findings reported separately.";
        attribute :>> units = "% of reference conclusions, precision and recall fractions";
        attribute :>> protocol = "Compare independent in-domain, extrapolated, numerically unsupported and missing-independent-evidence cases. Preserve calibration and assessment distinctions.";
        attribute :>> referenceConfiguration = "FR-21 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR22'> MOP_FR22 : PerformanceMeasure {
        attribute :>> observationBasis = "Calibration-proposal calculation agreement. Parameter and residual differences from an independent calculation using the same supplied calibration data, declared model and fitting method.";
        attribute :>> units = "parameter-specific units and residual units, separately";
        attribute :>> protocol = "Fix calibration objective, masks, parameter bounds, initialization and stochastic rules. Use an agreed solution-equivalence rule for nonunique parameter sets. Preserve prior/proposed values, revisions, uncertainty and affected analyses. Keep independent assessment data separate. Proposal acceptance is an engineer disposition.";
        attribute :>> referenceConfiguration = "FR-22 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR23'> MOP_FR23 : PerformanceMeasure {
        attribute :>> observationBasis = "Run configuration fidelity. Share of run records whose fidelity, solver/coupling, time step, convergence, environment, resources and runtime entries match independent execution manifests.";
        attribute :>> units = "% of exercised run records";
        attribute :>> protocol = "Change solvers, steps and resource limits across analysis, MIL and SIL. Assess numerical/resource finding correctness separately. External solver runtime supplies no automatic framework delay target.";
        attribute :>> referenceConfiguration = "FR-23 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR24'> MOP_FR24 : PerformanceMeasure {
        attribute :>> observationBasis = "SIL comparison-report accuracy. Share of matched F Prime SIL/MIL cases with correct configuration/scenario pairing, requirement/ConOps outcomes and difference reports.";
        attribute :>> units = "% of exercised matched assessment cases";
        attribute :>> protocol = "Use released host code and matched scenarios connected to the whole-CUBICS simulation. Seed code/interface discrepancies and failed runs. Assess reporting, not controller pass rate.";
        attribute :>> referenceConfiguration = "FR-24 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR25'> MOP_FR25 : PerformanceMeasure {
        attribute :>> observationBasis = "Mission/ConOps record fidelity. Share of recovered scenario records whose expectations, constraints, environmental histories, subsystem modes, schedules, transitions and revision links match source records.";
        attribute :>> units = "% of exercised scenario records";
        attribute :>> protocol = "Create, edit and retrieve nominal/degraded scenarios, including changed mission context and explicit missing values.";
        attribute :>> referenceConfiguration = "FR-25 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR26'> MOP_FR26 : PerformanceMeasure {
        attribute :>> observationBasis = "RAM-method applicability. Precision and recall of applicable reliability, availability and maintainability methods against independent expert references, with exclusion-rationale errors reported separately.";
        attribute :>> units = "precision and recall fractions, counts";
        attribute :>> protocol = "Vary requirements, ConOps, repairability, redundancy, risks and data availability. No spacecraft reliability or repair-time target transfers to this measure.";
        attribute :>> referenceConfiguration = "FR-26 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR27'> MOP_FR27 : PerformanceMeasure {
        attribute :>> observationBasis = "RAM transformation agreement. Share of generated structure/dependency items matching an independent representation under the same declared transformation rules, with result residuals reported separately.";
        attribute :>> units = "% of reference structure/dependency items, result-specific residual units";
        attribute :>> protocol = "Include dependency combinations, sourced/missing rates and uncertainty. Compare transformation/calculation correctness rather than an EPS reliability threshold.";
        attribute :>> referenceConfiguration = "FR-27 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR28'> MOP_FR28 : PerformanceMeasure {
        attribute :>> observationBasis = "V&V plan fidelity. Share of plan and observation records recovered with correct subjects, conditions, criteria, requirement/expectation references and planned/executed status.";
        attribute :>> units = "% of exercised plan/observation records";
        attribute :>> protocol = "Create, revise and recover verification and validation plans with incomplete criteria and explicit applicability limits. Treat plan status separately from product conformity.";
        attribute :>> referenceConfiguration = "FR-28 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR29'> MOP_FR29 : PerformanceMeasure {
        attribute :>> observationBasis = "Suggestion disposition fidelity. Share of decision records that retain the correct authorized disposition, rationale and exact suggestion/context revisions.";
        attribute :>> units = "% of exercised disposition events";
        attribute :>> protocol = "Exercise accepted, modified, rejected and deferred decisions, context changes and unauthorized attempts.";
        attribute :>> referenceConfiguration = "FR-29 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR30'> MOP_FR30 : PerformanceMeasure {
        attribute :>> observationBasis = "Stale-guidance exposure. Count of stale suggestions presented/applied as current, with delay from context edit to invalidation and reassessment request reported separately.";
        attribute :>> units = "occurrences and seconds";
        attribute :>> protocol = "Exercise source, criterion, mission, requirement, design and scope edits during delayed responses and concurrent updates. Fix the observation window and exact revision-event sequence.";
        attribute :>> referenceConfiguration = "FR-30 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR31'> MOP_FR31 : PerformanceMeasure {
        attribute :>> observationBasis = "Timing-handling agreement. Timing metadata and alignment residuals against known sample/receipt times, time bases and imposed delays, with synchronization-gap classification errors reported separately.";
        attribute :>> units = "seconds and classification-error fraction";
        attribute :>> protocol = "Use aligned/skewed histories with declared sampling, interface/calculation delay and synchronization limits. Compare retained timing records and checked alignments with independent references, including missing timing data and exceeded limits.";
        attribute :>> referenceConfiguration = "FR-31 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR32'> MOP_FR32 : PerformanceMeasure {
        attribute :>> observationBasis = "History-quality finding agreement. Precision and recall of channel, unit, time, completeness and validity findings against independent sample/interval masks.";
        attribute :>> units = "precision and recall fractions, raw-value-change count";
        attribute :>> protocol = "Inject missing, inactive, invalid, misidentified, wrong-unit and skewed samples before numerical use. Preserve raw values and distinguish absent readings from physical zeros. Compare admission findings and processing masks with independent references.";
        attribute :>> referenceConfiguration = "FR-32 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR33'> MOP_FR33 : PerformanceMeasure {
        attribute :>> observationBasis = "Interface-definition fidelity. Share of recovered definitions whose endpoint ownership, direction, revisions, identifiers, types, units, ranges, polarity, time/mode meanings and encodings match source specifications.";
        attribute :>> units = "% of exercised interface-definition records";
        attribute :>> protocol = "Round-trip electrical and command/telemetry/event/parameter definitions, including changed revisions and inconsistent endpoints.";
        attribute :>> referenceConfiguration = "FR-33 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR34'> MOP_FR34 : PerformanceMeasure {
        attribute :>> observationBasis = "F Prime mapping fidelity. Share of independently specified interface mappings that preserve declared meanings, with compatibility, unsupported-behavior and unreported-loss errors counted separately.";
        attribute :>> units = "% of reference mapping items, counts";
        attribute :>> protocol = "Pin F Prime/profile versions. Exercise component, port, topology, command, telemetry, event and parameter mappings, version changes and deliberately unsupported translations.";
        attribute :>> referenceConfiguration = "FR-34 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR35'> MOP_FR35 : PerformanceMeasure {
        attribute :>> observationBasis = "Control-behavior finding quality. Precision and recall of discrepancies in command preconditions, ordering/effects, rejection, transitions and protection/recovery responsibilities against independent references.";
        attribute :>> units = "precision and recall fractions";
        attribute :>> protocol = "Use clean and seeded simulated behavior sequences under declared control/interface requirements. Count missed critical discrepancies separately.";
        attribute :>> referenceConfiguration = "FR-35 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR36'> MOP_FR36 : PerformanceMeasure {
        attribute :>> observationBasis = "Host coding/build coordination accuracy. Share of requests handled with correct current design authority, F Prime build/source identity, configuration, dependency, log and failure records.";
        attribute :>> units = "% of exercised request/response sequences";
        attribute :>> protocol = "Attempt unreleased, stale, unauthorized and valid released work, plus external toolchain failures. A retained failed build differs from an orchestration failure.";
        attribute :>> referenceConfiguration = "FR-36 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR37'> MOP_FR37 : PerformanceMeasure {
        attribute :>> observationBasis = "Engineering-view interpretation accuracy. Share of fixed questions answered correctly from generated views, including baseline, allocation, units, interface and result meaning.";
        attribute :>> units = "% of independent reference questions";
        attribute :>> protocol = "Use fixed filtered-view tasks and independent expected answers. Declare participants, training and view configuration. Separate wrong answers, unreadable content and unanswerable items.";
        attribute :>> referenceConfiguration = "FR-37 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR38'> MOP_FR38 : PerformanceMeasure {
        attribute :>> observationBasis = "Review-package coverage. Share of independently listed applicable package items present with correct baseline/criterion revisions and content, with critical omissions counted separately.";
        attribute :>> units = "% of applicable checklist items, counts";
        attribute :>> protocol = "Use gate-specific MCR, SRR, MDR/SDR, PDR, CDR and SIR lists. Package preparation supplies no acceptance decision.";
        attribute :>> referenceConfiguration = "FR-38 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR39'> MOP_FR39 : PerformanceMeasure {
        attribute :>> observationBasis = "Activity-proposal applicability. Precision and recall of eligible next/repeated activities and unmet prerequisites against independent phase/maturity/dependency references.";
        attribute :>> units = "precision and recall fractions";
        attribute :>> protocol = "Change phase, maturity, dependencies and blocking/open findings. Label proposal rationale correctness and expert disagreement separately.";
        attribute :>> referenceConfiguration = "FR-39 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR41'> MOP_FR41 : PerformanceMeasure {
        attribute :>> observationBasis = "Assistance response delay. Trigger-to-acknowledgement, first current finding/recommendation or explicit status, and completion delay distributions under declared workload.";
        attribute :>> units = "seconds, completed/unavailable request counts";
        attribute :>> protocol = "Report acknowledgement, substantive guidance and pending/unavailable status separately, including outages and superseded edits. Record the request denominator and unfinished-response observation window.";
        attribute :>> referenceConfiguration = "FR-41 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }
    item <'MOP-FR42'> MOP_FR42 : PerformanceMeasure {
        attribute :>> observationBasis = "Review disposition accuracy. Share of decision-event sequences with correct authority, baseline/criteria bindings, progression status and condition/closure records.";
        attribute :>> units = "% of exercised decision-event sequences";
        attribute :>> protocol = "Exercise prepared, accepted, conditional and blocked outcomes, stale/unauthorized decisions and renewed condition closure under independent state references.";
        attribute :>> referenceConfiguration = "FR-42 case set, declared workload and framework/tool/host configuration, independent reference revisions and comparison rules";
    }

    dependency MOPFR01_FR01 from MOP_FR01 to FR_01;
    #qualitativeContribution dependency MOPFR01_MOE03 from MOP_FR01 to FrameworkNeeds::MOE_03;
    dependency MOPFR02_FR02 from MOP_FR02 to FR_02;
    #qualitativeContribution dependency MOPFR02_MOE02 from MOP_FR02 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR02_MOE03 from MOP_FR02 to FrameworkNeeds::MOE_03;
    dependency MOPFR03_FR03 from MOP_FR03 to FR_03;
    #qualitativeContribution dependency MOPFR03_MOE02 from MOP_FR03 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR03_MOE03 from MOP_FR03 to FrameworkNeeds::MOE_03;
    dependency MOPFR04_FR04 from MOP_FR04 to FR_04;
    #qualitativeContribution dependency MOPFR04_MOE03 from MOP_FR04 to FrameworkNeeds::MOE_03;
    dependency MOPFR05_FR05 from MOP_FR05 to FR_05;
    #qualitativeContribution dependency MOPFR05_MOE02 from MOP_FR05 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR05_MOE03 from MOP_FR05 to FrameworkNeeds::MOE_03;
    dependency MOPFR06_FR06 from MOP_FR06 to FR_06;
    #qualitativeContribution dependency MOPFR06_MOE03 from MOP_FR06 to FrameworkNeeds::MOE_03;
    dependency MOPFR07_FR07 from MOP_FR07 to FR_07;
    #qualitativeContribution dependency MOPFR07_MOE01 from MOP_FR07 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency MOPFR07_MOE03 from MOP_FR07 to FrameworkNeeds::MOE_03;
    dependency MOPFR08_FR08 from MOP_FR08 to FR_08;
    #qualitativeContribution dependency MOPFR08_MOE02 from MOP_FR08 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR08_MOE03 from MOP_FR08 to FrameworkNeeds::MOE_03;
    dependency MOPFR09_FR09 from MOP_FR09 to FR_09;
    #qualitativeContribution dependency MOPFR09_MOE03 from MOP_FR09 to FrameworkNeeds::MOE_03;
    dependency MOPFR10_FR10 from MOP_FR10 to FR_10;
    #qualitativeContribution dependency MOPFR10_MOE03 from MOP_FR10 to FrameworkNeeds::MOE_03;
    dependency MOPFR11_FR11 from MOP_FR11 to FR_11;
    #qualitativeContribution dependency MOPFR11_MOE02 from MOP_FR11 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR11_MOE03 from MOP_FR11 to FrameworkNeeds::MOE_03;
    dependency MOPFR13_FR13 from MOP_FR13 to FR_13;
    #qualitativeContribution dependency MOPFR13_MOE02 from MOP_FR13 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR13_MOE03 from MOP_FR13 to FrameworkNeeds::MOE_03;
    dependency MOPFR14_FR14 from MOP_FR14 to FR_14;
    #qualitativeContribution dependency MOPFR14_MOE02 from MOP_FR14 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR14_MOE03 from MOP_FR14 to FrameworkNeeds::MOE_03;
    dependency MOPFR15_FR15 from MOP_FR15 to FR_15;
    #qualitativeContribution dependency MOPFR15_MOE03 from MOP_FR15 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency MOPFR15_MOE04 from MOP_FR15 to FrameworkNeeds::MOE_04;
    dependency MOPFR16_FR16 from MOP_FR16 to FR_16;
    #qualitativeContribution dependency MOPFR16_MOE02 from MOP_FR16 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR16_MOE03 from MOP_FR16 to FrameworkNeeds::MOE_03;
    dependency MOPFR17_FR17 from MOP_FR17 to FR_17;
    #qualitativeContribution dependency MOPFR17_MOE02 from MOP_FR17 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR17_MOE03 from MOP_FR17 to FrameworkNeeds::MOE_03;
    dependency MOPFR18_FR18 from MOP_FR18 to FR_18;
    #qualitativeContribution dependency MOPFR18_MOE02 from MOP_FR18 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR18_MOE03 from MOP_FR18 to FrameworkNeeds::MOE_03;
    dependency MOPFR19_FR19 from MOP_FR19 to FR_19;
    #qualitativeContribution dependency MOPFR19_MOE02 from MOP_FR19 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR19_MOE03 from MOP_FR19 to FrameworkNeeds::MOE_03;
    dependency MOPFR20_FR20 from MOP_FR20 to FR_20;
    #qualitativeContribution dependency MOPFR20_MOE02 from MOP_FR20 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR20_MOE03 from MOP_FR20 to FrameworkNeeds::MOE_03;
    dependency MOPFR21_FR21 from MOP_FR21 to FR_21;
    #qualitativeContribution dependency MOPFR21_MOE02 from MOP_FR21 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR21_MOE03 from MOP_FR21 to FrameworkNeeds::MOE_03;
    dependency MOPFR22_FR22 from MOP_FR22 to FR_22;
    #qualitativeContribution dependency MOPFR22_MOE02 from MOP_FR22 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR22_MOE03 from MOP_FR22 to FrameworkNeeds::MOE_03;
    dependency MOPFR23_FR23 from MOP_FR23 to FR_23;
    #qualitativeContribution dependency MOPFR23_MOE03 from MOP_FR23 to FrameworkNeeds::MOE_03;
    dependency MOPFR24_FR24 from MOP_FR24 to FR_24;
    #qualitativeContribution dependency MOPFR24_MOE02 from MOP_FR24 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR24_MOE03 from MOP_FR24 to FrameworkNeeds::MOE_03;
    dependency MOPFR25_FR25 from MOP_FR25 to FR_25;
    #qualitativeContribution dependency MOPFR25_MOE03 from MOP_FR25 to FrameworkNeeds::MOE_03;
    dependency MOPFR26_FR26 from MOP_FR26 to FR_26;
    #qualitativeContribution dependency MOPFR26_MOE02 from MOP_FR26 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR26_MOE03 from MOP_FR26 to FrameworkNeeds::MOE_03;
    dependency MOPFR27_FR27 from MOP_FR27 to FR_27;
    #qualitativeContribution dependency MOPFR27_MOE02 from MOP_FR27 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR27_MOE03 from MOP_FR27 to FrameworkNeeds::MOE_03;
    dependency MOPFR28_FR28 from MOP_FR28 to FR_28;
    #qualitativeContribution dependency MOPFR28_MOE03 from MOP_FR28 to FrameworkNeeds::MOE_03;
    dependency MOPFR29_FR29 from MOP_FR29 to FR_29;
    #qualitativeContribution dependency MOPFR29_MOE03 from MOP_FR29 to FrameworkNeeds::MOE_03;
    dependency MOPFR30_FR30 from MOP_FR30 to FR_30;
    #qualitativeContribution dependency MOPFR30_MOE02 from MOP_FR30 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR30_MOE03 from MOP_FR30 to FrameworkNeeds::MOE_03;
    dependency MOPFR31_FR31 from MOP_FR31 to FR_31;
    #qualitativeContribution dependency MOPFR31_MOE02 from MOP_FR31 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR31_MOE03 from MOP_FR31 to FrameworkNeeds::MOE_03;
    dependency MOPFR32_FR32 from MOP_FR32 to FR_32;
    #qualitativeContribution dependency MOPFR32_MOE02 from MOP_FR32 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR32_MOE03 from MOP_FR32 to FrameworkNeeds::MOE_03;
    dependency MOPFR33_FR33 from MOP_FR33 to FR_33;
    #qualitativeContribution dependency MOPFR33_MOE03 from MOP_FR33 to FrameworkNeeds::MOE_03;
    dependency MOPFR34_FR34 from MOP_FR34 to FR_34;
    #qualitativeContribution dependency MOPFR34_MOE02 from MOP_FR34 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR34_MOE03 from MOP_FR34 to FrameworkNeeds::MOE_03;
    dependency MOPFR35_FR35 from MOP_FR35 to FR_35;
    #qualitativeContribution dependency MOPFR35_MOE02 from MOP_FR35 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR35_MOE03 from MOP_FR35 to FrameworkNeeds::MOE_03;
    dependency MOPFR36_FR36 from MOP_FR36 to FR_36;
    #qualitativeContribution dependency MOPFR36_MOE02 from MOP_FR36 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR36_MOE03 from MOP_FR36 to FrameworkNeeds::MOE_03;
    dependency MOPFR37_FR37 from MOP_FR37 to FR_37;
    #qualitativeContribution dependency MOPFR37_MOE03 from MOP_FR37 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency MOPFR37_MOE04 from MOP_FR37 to FrameworkNeeds::MOE_04;
    dependency MOPFR38_FR38 from MOP_FR38 to FR_38;
    #qualitativeContribution dependency MOPFR38_MOE03 from MOP_FR38 to FrameworkNeeds::MOE_03;
    dependency MOPFR39_FR39 from MOP_FR39 to FR_39;
    #qualitativeContribution dependency MOPFR39_MOE02 from MOP_FR39 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOPFR39_MOE03 from MOP_FR39 to FrameworkNeeds::MOE_03;
    dependency MOPFR41_FR41 from MOP_FR41 to FR_41;
    #qualitativeContribution dependency MOPFR41_MOE01 from MOP_FR41 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency MOPFR41_MOE04 from MOP_FR41 to FrameworkNeeds::MOE_04;
    dependency MOPFR42_FR42 from MOP_FR42 to FR_42;
    #qualitativeContribution dependency MOPFR42_MOE03 from MOP_FR42 to FrameworkNeeds::MOE_03;
}
