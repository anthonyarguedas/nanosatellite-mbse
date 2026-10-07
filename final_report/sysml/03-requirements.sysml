// Current framework black-box requirements. Every reused ID has the meaning below.
// FR-40 is retired. The former two-case protocol belongs only to later validation/research evaluation.
// TODO: Re-derive LA/PA allocations and V cases from these statements. No satisfaction is asserted.
package FrameworkRequirements {
    private import FrameworkDomain::*;
    private import RequirementDerivation::*;
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
    #derivation connection derive_MR_02_FR_04 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_04; }
    #derivation connection derive_MR_05_FR_04 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_04; }
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
    #sourceTrace dependency scenario_FR17_SC02 from FR_17 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR17_SC03 from FR_17 to ScenarioViews::SC03;
    #sourceTrace dependency function_FR17_F02 from FR_17 to BoundaryViews::F02;
    requirement <'FR-29'> FR_29 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain the authorized engineer disposition of each requirement correction or method/model suggestion as accepted, modified, rejected or deferred, with rationale and the exact suggestion and context revisions. */
    }
    @SourceRecord about FR_29 { identifier = "FR-29"; sourceText = "The framework shall retain the authorized engineer disposition of each requirement correction or method/model suggestion as accepted, modified, rejected or deferred, with rationale and the exact suggestion and context revisions."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 4.2 and 6.8"; }
    @PlannedRequirementCheck about FR_29 { theme = "Requirements and explained assistance"; methods = "I,T"; checkSummary = "Exercise all dispositions and an unauthorized attempt to apply a suggestion."; }
    #derivation connection derive_MR_02_FR_29 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_29; }
    #derivation connection derive_MR_05_FR_29 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_29; }
    #sourceTrace dependency scenario_FR29_SC02 from FR_29 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR29_SC05 from FR_29 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR29_F02 from FR_29 to BoundaryViews::F02;
    requirement <'FR-30'> FR_30 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall mark affected assistance stale when its requirement, mission, design, source, criterion or scope revision changes, prevent stale suggestions from being applied as current guidance and initiate reassessment for the new context. */
    }
    @SourceRecord about FR_30 { identifier = "FR-30"; sourceText = "The framework shall mark affected assistance stale when its requirement, mission, design, source, criterion or scope revision changes, prevent stale suggestions from being applied as current guidance and initiate reassessment for the new context."; sourceLocator = "Analyze System Requirements, Requirements and explained assistance"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.2 and 6.5"; }
    @PlannedRequirementCheck about FR_30 { theme = "Requirements and explained assistance"; methods = "T"; checkSummary = "Edit during a delayed response and check that the old response cannot replace current guidance."; }
    #derivation connection derive_MR_02_FR_30 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_30; }
    #derivation connection derive_MR_05_FR_30 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_30; }
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
    #derivation connection derive_MR_02_FR_41 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_41; }
    #derivation connection derive_MR_05_FR_41 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_41; }
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
    #sourceTrace dependency scenario_FR15_SC01 from FR_15 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR15_SC03 from FR_15 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR15_SC04 from FR_15 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR15_F03 from FR_15 to BoundaryViews::F03;
    requirement <'FR-12'> FR_12 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall generate and revise candidate-specific bills of materials from modeled design occurrences with assembly relationships, quantities, part and variant identifiers, source revisions and selection status. */
    }
    @SourceRecord about FR_12 { identifier = "FR-12"; sourceText = "The framework shall generate and revise candidate-specific bills of materials from modeled design occurrences with assembly relationships, quantities, part and variant identifiers, source revisions and selection status."; sourceLocator = "Analyze System Requirements, Mission concepts and preliminary design"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 3.5 and El Hachimi 4"; }
    @PlannedRequirementCheck about FR_12 { theme = "Mission concepts and preliminary design"; methods = "A,T"; checkSummary = "Compare quantities and substitutions with a reference assembly."; }
    #derivation connection derive_MR_03_FR_12 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_12; }
    #sourceTrace dependency scenario_FR12_SC03 from FR_12 to ScenarioViews::SC03;
    #sourceTrace dependency function_FR12_F03 from FR_12 to BoundaryViews::F03;
    requirement <'FR-13'> FR_13 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall calculate revision-linked EPS mass, volume and acquisition-cost estimates from the bill of materials and declared additional categories, retaining sources, price dates, currencies, availability assumptions, uncertainty and unknown values. */
    }
    @SourceRecord about FR_13 { identifier = "FR-13"; sourceText = "The framework shall calculate revision-linked EPS mass, volume and acquisition-cost estimates from the bill of materials and declared additional categories, retaining sources, price dates, currencies, availability assumptions, uncertainty and unknown values."; sourceLocator = "Analyze System Requirements, Mission concepts and preliminary design"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 3.5 and Girardello 3.2 limitations"; }
    @PlannedRequirementCheck about FR_13 { theme = "Mission concepts and preliminary design"; methods = "A,T"; checkSummary = "Recalculate after a substitution and preserve unknown prices and availability."; }
    #derivation connection derive_MR_03_FR_13 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_13; }
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
    #sourceTrace dependency scenario_FR20_SC01 from FR_20 to ScenarioViews::SC01;
    #sourceTrace dependency scenario_FR20_SC03 from FR_20 to ScenarioViews::SC03;
    #sourceTrace dependency function_FR20_F03 from FR_20 to BoundaryViews::F03;
    requirement <'FR-16'> FR_16 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall compose time-dependent subsystem loads, schedules and mode transitions with orbit, attitude, illumination, eclipse, thermal conditions and modeled EPS generation, storage, losses and protection to report power/energy balance, bus quantities and battery state within the declared model scope. */
    }
    @SourceRecord about FR_16 { identifier = "FR-16"; sourceText = "The framework shall compose time-dependent subsystem loads, schedules and mode transitions with orbit, attitude, illumination, eclipse, thermal conditions and modeled EPS generation, storage, losses and protection to report power/energy balance, bus quantities and battery state within the declared model scope."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Boan 2--4 and Casado 2--4"; }
    @PlannedRequirementCheck about FR_16 { theme = "Simulation and model credibility"; methods = "A,T"; checkSummary = "Use a temporal shortage hidden by an average power budget and check coupling against a reference."; }
    #derivation connection derive_MR_03_FR_16 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_16; }
    #derivation connection derive_MR_04_FR_16 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_16; }
    #sourceTrace dependency scenario_FR16_SC03 from FR_16 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR16_SC04 from FR_16 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR16_F04 from FR_16 to BoundaryViews::F04;
    requirement <'FR-18'> FR_18 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall exchange identified component and design models with declared electrical, thermal, applicable EMC and geometry analysis profiles, retaining input/output mappings, tool versions, units, supported effects and unsupported or lossy transfers. */
    }
    @SourceRecord about FR_18 { identifier = "FR-18"; sourceText = "The framework shall exchange identified component and design models with declared electrical, thermal, applicable EMC and geometry analysis profiles, retaining input/output mappings, tool versions, units, supported effects and unsupported or lossy transfers."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 3.5--3.6 and El Hachimi 4"; }
    @PlannedRequirementCheck about FR_18 { theme = "Simulation and model credibility"; methods = "D,T"; checkSummary = "Exercise each required discipline profile and incompatible mappings."; }
    #derivation connection derive_MR_03_FR_18 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_18; }
    #derivation connection derive_MR_04_FR_18 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_18; }
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
    #derivation connection derive_MR_05_FR_26 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_26; }
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
    #sourceTrace dependency scenario_FR27_SC03 from FR_27 to ScenarioViews::SC03;
    #sourceTrace dependency function_FR27_F04 from FR_27 to BoundaryViews::F04;
    requirement <'FR-31'> FR_31 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain scenario time bases, sample and receipt times, sampling, synchronization and known calculation/interface delays for simulated or supplied reference histories used in comparisons. */
    }
    @SourceRecord about FR_31 { identifier = "FR-31"; sourceText = "The framework shall retain scenario time bases, sample and receipt times, sampling, synchronization and known calculation/interface delays for simulated or supplied reference histories used in comparisons."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Boan 2--4 and NASA 5.3--5.4"; }
    @PlannedRequirementCheck about FR_31 { theme = "Simulation and model credibility"; methods = "A,T"; checkSummary = "Compare aligned and skewed histories with declared time tolerances."; }
    #derivation connection derive_MR_03_FR_31 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_31; }
    #derivation connection derive_MR_04_FR_31 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_31; }
    #derivation connection derive_MR_05_FR_31 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_31; }
    #sourceTrace dependency scenario_FR31_SC03 from FR_31 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR31_SC04 from FR_31 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR31_SC05 from FR_31 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR31_F04 from FR_31 to BoundaryViews::F04;
    requirement <'FR-32'> FR_32 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall check simulated and supplied reference histories for channel identity, units, timing, completeness and validity, preserving raw values, invalid samples, missing intervals and processing masks without treating missing or inactive readings as zero. */
    }
    @SourceRecord about FR_32 { identifier = "FR-32"; sourceText = "The framework shall check simulated and supplied reference histories for channel identity, units, timing, completeness and validity, preserving raw values, invalid samples, missing intervals and processing masks without treating missing or inactive readings as zero."; sourceLocator = "Analyze System Requirements, Simulation and model credibility"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 5.3--5.4 and Zhu pp.7--9"; }
    @PlannedRequirementCheck about FR_32 { theme = "Simulation and model credibility"; methods = "T"; checkSummary = "Inject missing, inactive, invalid and wrong-unit data and compare masks."; }
    #derivation connection derive_MR_03_FR_32 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_32; }
    #derivation connection derive_MR_04_FR_32 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_32; }
    #derivation connection derive_MR_05_FR_32 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_32; }
    #sourceTrace dependency scenario_FR32_SC03 from FR_32 to ScenarioViews::SC03;
    #sourceTrace dependency scenario_FR32_SC04 from FR_32 to ScenarioViews::SC04;
    #sourceTrace dependency scenario_FR32_SC05 from FR_32 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR32_F04 from FR_32 to BoundaryViews::F04;
    requirement <'FR-33'> FR_33 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain revision-linked modeled EPS interfaces and command, telemetry, event and parameter definitions with endpoint ownership, identifiers, types, units, ranges, polarity, time/mode meaning and encodings. */
    }
    @SourceRecord about FR_33 { identifier = "FR-33"; sourceText = "The framework shall retain revision-linked modeled EPS interfaces and command, telemetry, event and parameter definitions with endpoint ownership, identifiers, types, units, ranges, polarity, time/mode meaning and encodings."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.3 and Campioli 3--4"; }
    @PlannedRequirementCheck about FR_33 { theme = "Detailed interfaces and host software"; methods = "I,T"; checkSummary = "Round-trip interface definitions and reject inconsistent endpoint meanings."; }
    #derivation connection derive_MR_02_FR_33 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_33; }
    #derivation connection derive_MR_04_FR_33 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_33; }
    #sourceTrace dependency scenario_FR33_SC02 from FR_33 to ScenarioViews::SC02;
    #sourceTrace dependency scenario_FR33_SC04 from FR_33 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR33_F05 from FR_33 to BoundaryViews::F05;
    requirement <'FR-34'> FR_34 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall produce or coordinate checked mappings of the EPS interface specification to the engineer-selected host software integration profile, identifying version compatibility, unsupported behavior and lossy translations. */
    }
    @SourceRecord about FR_34 { identifier = "FR-34"; sourceText = "The framework shall produce or coordinate checked mappings of the EPS interface specification to the engineer-selected host software integration profile, identifying version compatibility, unsupported behavior and lossy translations."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 3.6 and 6.3"; }
    @PlannedRequirementCheck about FR_34 { theme = "Detailed interfaces and host software"; methods = "D,T"; checkSummary = "Check a selected profile and expose omitted or incompatible meanings."; }
    #derivation connection derive_MR_04_FR_34 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_34; }
    #sourceTrace dependency scenario_FR34_SC04 from FR_34 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR34_F05 from FR_34 to BoundaryViews::F05;
    requirement <'FR-35'> FR_35 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall specify and check modeled EPS command preconditions, order, effects, rejection/failure behavior, mode transitions, protection and recovery responsibilities against the declared control and interface requirements. */
    }
    @SourceRecord about FR_35 { identifier = "FR-35"; sourceText = "The framework shall specify and check modeled EPS command preconditions, order, effects, rejection/failure behavior, mode transitions, protection and recovery responsibilities against the declared control and interface requirements."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Casado 2--4 and NASA 3.6"; }
    @PlannedRequirementCheck about FR_35 { theme = "Detailed interfaces and host software"; methods = "A,T"; checkSummary = "Exercise nominal, rejected, protection and recovery sequences in simulated conditions."; }
    #derivation connection derive_MR_04_FR_35 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_35; }
    #sourceTrace dependency scenario_FR35_SC04 from FR_35 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR35_F05 from FR_35 to BoundaryViews::F05;
    requirement <'FR-36'> FR_36 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall coordinate coding and building of declared control/interface software through an external host execution toolchain only from an engineer-authorized detailed design release, retaining source/build revisions, dependencies, host configuration, logs and failures. */
    }
    @SourceRecord about FR_36 { identifier = "FR-36"; sourceText = "The framework shall coordinate coding and building of declared control/interface software through an external host execution toolchain only from an engineer-authorized detailed design release, retaining source/build revisions, dependencies, host configuration, logs and failures."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 3.6 and CDR paragraphs at start of 3.7"; }
    @PlannedRequirementCheck about FR_36 { theme = "Detailed interfaces and host software"; methods = "D,T"; checkSummary = "Attempt an unreleased build and then build the released design, including a toolchain failure."; }
    #derivation connection derive_MR_04_FR_36 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_36; }
    #sourceTrace dependency scenario_FR36_SC04 from FR_36 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR36_F05 from FR_36 to BoundaryViews::F05;
    requirement <'FR-19'> FR_19 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall coordinate MIL assessment of modeled EPS control against the plant and mission scenarios for nominal operation, load/supply changes, mode transitions, selected faults, protection and recovery, retaining stimuli, expected/actual responses, criteria and failures. */
    }
    @SourceRecord about FR_19 { identifier = "FR-19"; sourceText = "The framework shall coordinate MIL assessment of modeled EPS control against the plant and mission scenarios for nominal operation, load/supply changes, mode transitions, selected faults, protection and recovery, retaining stimuli, expected/actual responses, criteria and failures."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Casado 2 and NASA 5.3--5.4"; }
    @PlannedRequirementCheck about FR_19 { theme = "Detailed interfaces and host software"; methods = "D,T"; checkSummary = "Run declared nominal and fault sequences with a simulated plant and retain failed criteria."; }
    #derivation connection derive_MR_04_FR_19 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_19; }
    #sourceTrace dependency scenario_FR19_SC04 from FR_19 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR19_F05 from FR_19 to BoundaryViews::F05;
    requirement <'FR-24'> FR_24 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall coordinate SIL assessment of the declared host-executed control/interface code with simulated EPS and subsystem products, reporting requirement/ConOps outcomes and differences from corresponding MIL results for the same scenarios and comparison rules. */
    }
    @SourceRecord about FR_24 { identifier = "FR-24"; sourceText = "The framework shall coordinate SIL assessment of the declared host-executed control/interface code with simulated EPS and subsystem products, reporting requirement/ConOps outcomes and differences from corresponding MIL results for the same scenarios and comparison rules."; sourceLocator = "Analyze System Requirements, Detailed interfaces and host software"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "Zhu SIL scope and NASA 5.3--5.4"; }
    @PlannedRequirementCheck about FR_24 { theme = "Detailed interfaces and host software"; methods = "A,T"; checkSummary = "Use matching MIL/SIL inputs and a seeded code/interface discrepancy."; }
    #derivation connection derive_MR_04_FR_24 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_24; }
    #sourceTrace dependency scenario_FR24_SC04 from FR_24 to ScenarioViews::SC04;
    #sourceTrace dependency function_FR24_F05 from FR_24 to BoundaryViews::F05;
    requirement <'FR-28'> FR_28 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain EPS phase-product verification and validation plans with distinct requirement and expectation/ConOps references, subject configuration, method, conditions, inputs, expected response, criteria, observations, applicability limits and planned/executed status. */
    }
    @SourceRecord about FR_28 { identifier = "FR-28"; sourceText = "The framework shall retain EPS phase-product verification and validation plans with distinct requirement and expectation/ConOps references, subject configuration, method, conditions, inputs, expected response, criteria, observations, applicability limits and planned/executed status."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 2.4 and 5.3--5.4"; }
    @PlannedRequirementCheck about FR_28 { theme = "Evidence, controlled changes and reviews"; methods = "I,T"; checkSummary = "Distinguish planned activities from results and verification criteria from validation expectations."; }
    #derivation connection derive_MR_02_FR_28 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_28; }
    #derivation connection derive_MR_04_FR_28 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_28; }
    #derivation connection derive_MR_05_FR_28 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_28; }
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
    #derivation connection derive_MR_05_FR_05 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_05; }
    #sourceTrace dependency scenario_FR05_SC05 from FR_05 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR05_F07 from FR_05 to BoundaryViews::F07;
    requirement <'FR-06'> FR_06 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall issue a distinct successor baseline only for an authorized engineering change decision, preserving its predecessor, request, rationale, findings and dispositions and identifying regenerated, stale and unresolved products and evidence. */
    }
    @SourceRecord about FR_06 { identifier = "FR-06"; sourceText = "The framework shall issue a distinct successor baseline only for an authorized engineering change decision, preserving its predecessor, request, rationale, findings and dispositions and identifying regenerated, stale and unresolved products and evidence."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.2 and 6.5"; }
    @PlannedRequirementCheck about FR_06 { theme = "Evidence, controlled changes and reviews"; methods = "T"; checkSummary = "Accept, decline and interrupt changes without erasing the predecessor."; }
    #derivation connection derive_MR_05_FR_06 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_06; }
    #sourceTrace dependency scenario_FR06_SC05 from FR_06 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR06_F07 from FR_06 to BoundaryViews::F07;
    requirement <'FR-07'> FR_07 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall retain retrievable phase baselines that resolve exact requirement, mission, design, model, software, interface and evidence revisions with revision history and the authorized decisions that control them. */
    }
    @SourceRecord about FR_07 { identifier = "FR-07"; sourceText = "The framework shall retain retrievable phase baselines that resolve exact requirement, mission, design, model, software, interface and evidence revisions with revision history and the authorized decisions that control them."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.5--6.6"; }
    @PlannedRequirementCheck about FR_07 { theme = "Evidence, controlled changes and reviews"; methods = "I,T"; checkSummary = "Reconstruct predecessor and successor manifests and all applicable products."; }
    #derivation connection derive_MR_05_FR_07 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_07; }
    #sourceTrace dependency scenario_FR07_SC05 from FR_07 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR07_F07 from FR_07 to BoundaryViews::F07;
    requirement <'FR-08'> FR_08 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall check transferred identities, revisions, structure, quantities, units, polarity, time/mode meanings and provenance against the declared interface specification before registration, retaining incompatible raw submissions and findings without replacing controlled content. */
    }
    @SourceRecord about FR_08 { identifier = "FR-08"; sourceText = "The framework shall check transferred identities, revisions, structure, quantities, units, polarity, time/mode meanings and provenance against the declared interface specification before registration, retaining incompatible raw submissions and findings without replacing controlled content."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.3 and 6.5--6.6"; }
    @PlannedRequirementCheck about FR_08 { theme = "Evidence, controlled changes and reviews"; methods = "T"; checkSummary = "Inject identity, unit, sign and revision mismatches at each active interface."; }
    #derivation connection derive_MR_02_FR_08 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_08; }
    #derivation connection derive_MR_03_FR_08 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_08; }
    #derivation connection derive_MR_04_FR_08 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_08; }
    #derivation connection derive_MR_05_FR_08 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_08; }
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
    #derivation connection derive_MR_03_FR_09 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_09; }
    #derivation connection derive_MR_04_FR_09 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_09; }
    #derivation connection derive_MR_05_FR_09 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_09; }
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
    #derivation connection derive_MR_05_FR_10 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_10; }
    #sourceTrace dependency scenario_FR10_SC05 from FR_10 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR10_F04 from FR_10 to BoundaryViews::F04;
    requirement <'FR-11'> FR_11 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall report missing, rejected, stale, failed, out-of-domain and unresolved evidence against the affected requirements, expectations and conclusions with criticality, owner and disposition, preventing unqualified current conformity claims from affected critical gaps. */
    }
    @SourceRecord about FR_11 { identifier = "FR-11"; sourceText = "The framework shall report missing, rejected, stale, failed, out-of-domain and unresolved evidence against the affected requirements, expectations and conclusions with criticality, owner and disposition, preventing unqualified current conformity claims from affected critical gaps."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 5.3--5.4 and 6.7"; }
    @PlannedRequirementCheck about FR_11 { theme = "Evidence, controlled changes and reviews"; methods = "T"; checkSummary = "Seed every evidence status and attempt a current claim with a blocking gap."; }
    #derivation connection derive_MR_05_FR_11 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_11; }
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
    #derivation connection derive_MR_05_FR_38 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_38; }
    #sourceTrace dependency scenario_FR38_SC05 from FR_38 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR38_F08 from FR_38 to BoundaryViews::F08;
    requirement <'FR-42'> FR_42 {
        subject framework : ToBe::FutureFramework;
        doc /* The framework shall record a technical review disposition only from the designated authorized review authority against the identified baseline and agreed scoped success criteria, distinguishing prepared, accepted, conditional and progression-blocked status with rationale, conditions, closure actions, owners and dates. */
    }
    @SourceRecord about FR_42 { identifier = "FR-42"; sourceText = "The framework shall record a technical review disposition only from the designated authorized review authority against the identified baseline and agreed scoped success criteria, distinguishing prepared, accepted, conditional and progression-blocked status with rationale, conditions, closure actions, owners and dates."; sourceLocator = "Analyze System Requirements, Evidence, controlled changes and reviews"; status = "proposed, stakeholder agreement and verification pending"; citationRecord = "NASA 6.7 and 6.8"; }
    @PlannedRequirementCheck about FR_42 { theme = "Evidence, controlled changes and reviews"; methods = "I,T"; checkSummary = "Reject unauthorized or stale-baseline decisions and exercise blocking and conditional findings."; }
    #derivation connection derive_MR_05_FR_42 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_42; }
    #sourceTrace dependency scenario_FR42_SC05 from FR_42 to ScenarioViews::SC05;
    #sourceTrace dependency function_FR42_F08 from FR_42 to BoundaryViews::F08;

    item def PerformanceMeasure :> EngineeringArtifact {
        attribute observationBasis : ScalarValues::String;
        attribute units : ScalarValues::String;
        attribute referenceConfiguration : ScalarValues::String;
        attribute target : ScalarValues::String = "TBR before framework requirements baseline, with intended-use rationale";
        attribute resolutionOwner : ScalarValues::String = "Systems Engineer";
        attribute resolutionAction : ScalarValues::String = "Agree limits, workload and reference answers with stakeholders and independent experts";
        attribute resolutionGate : ScalarValues::String = "framework requirements baseline";
        attribute achieved : ScalarValues::String = "unknown, no empirical evaluation";
    }
    item <'MOP-01'> MOP_01 : PerformanceMeasure {
        attribute :>> observationBasis = "Trigger-to-acknowledgement, first current answer and completion percentiles, outages and superseded edits";
        attribute :>> units = "seconds, exceedance count";
    }
    item <'MOP-02'> MOP_02 : PerformanceMeasure {
        attribute :>> observationBasis = "Deterministic agreement, semantic precision/recall, critical misses, false positives, abstention, explanation/source correctness and recommendation eligibility/ranking";
        attribute :>> units = "counts and fractions over independent expert reference sets";
    }
    item <'MOP-03'> MOP_03 : PerformanceMeasure {
        attribute :>> observationBasis = "Budget/sizing and transfer agreement, numerical convergence, validity violations and runtime for a declared workload";
        attribute :>> units = "result-specific engineering units, violation count and seconds";
    }
    item <'MOP-04'> MOP_04 : PerformanceMeasure {
        attribute :>> observationBasis = "Impact precision/recall and stale or unauthorized outputs presented as current, including interrupted changes";
        attribute :>> units = "reference-set fractions and occurrence count";
    }
    item <'MOP-05'> MOP_05 : PerformanceMeasure {
        attribute :>> observationBasis = "Applicable reconstruction success and raw-output agreement under rules fixed before replay, including missing dependencies";
        attribute :>> units = "applicable-run fraction and result-specific residual units";
    }
    item <'MOP-06'> MOP_06 : PerformanceMeasure {
        attribute :>> observationBasis = "Review interpretation accuracy, required package omissions, correct task completion and declared-host resource footprint";
        attribute :>> units = "reference-set fractions, omission count and declared resource quantities";
    }
    #qualitativeContribution dependency MOP01_MOE01 from MOP_01 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency MOP01_MOE04 from MOP_01 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency MOP02_MOE02 from MOP_02 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOP02_MOE03 from MOP_02 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency MOP03_MOE02 from MOP_03 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOP03_MOE03 from MOP_03 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency MOP04_MOE02 from MOP_04 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency MOP04_MOE03 from MOP_04 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency MOP05_MOE03 from MOP_05 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency MOP06_MOE03 from MOP_06 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency MOP06_MOE04 from MOP_06 to FrameworkNeeds::MOE_04;
}
