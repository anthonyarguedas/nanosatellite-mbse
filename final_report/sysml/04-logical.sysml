// Proposed framework specifications and trace relationships.
// Source locators retain historical provenance.
package FrameworkLogical {
private import FrameworkDomain::*;
port def ControlPort { inout item record : EngineeringArtifact; }
interface def Control { end a : ControlPort; end b : ControlPort; }
part def <'L01'> Guidance { doc /* Engineering guidance and knowledge. Curate sourced standards/method choices, requirement/verification templates, examples, reusable EPS patterns, analysis recipes, and reviewed lessons. Identify assumptions and scope of reuse. Inputs and outputs: Case goals and user task → tailored guidance/recipe proposals. Reviewed findings → new knowledge revision. Limits: Recommends methods without declaring standard compliance or authorizing a design. */
port records : ControlPort;
ref item knowledgeCaseReview : KnowledgeCaseReview [0..*];
}
@SourceRecord { identifier = "L01"; sourceText = "Engineering guidance and knowledge"; sourceLocator = "final_report/traceability/logical-architecture.json"; status = "author-reviewed logical responsibility; physical realization and verification pending"; citationRecord = ""; }
part def <'L02'> Governance { doc /* Needs, requirements and decision governance. Maintain needs/MOEs, requirements at EPS/subsystem/component levels, criteria references, rationale, dependency semantics, impact sets, verification status, and change/discrepancy dispositions. Inputs and outputs: Authored requirements, architecture/property changes, verdicts → impact/change and decision records. Limits: Owns the engineering justification graph. Human authorities accept/reject changes. */
port records : ControlPort;
ref item needRequirementDecision : NeedRequirementDecision [0..*];
}
@SourceRecord { identifier = "L02"; sourceText = "Needs, requirements and decision governance"; sourceLocator = "final_report/traceability/logical-architecture.json"; status = "author-reviewed logical responsibility; physical realization and verification pending"; citationRecord = ""; }
part def <'L03'> Contracts { doc /* Architecture and service contracts. Represent EPS structure, functions, allocations, interfaces, modes, constraints, and hardware/software views. Define shared commands, telemetry, events, parameters, guards/effects, mode/recovery responsibilities, and target mappings. Publish supported dictionaries, scaffolds, and contract tests. Inputs and outputs: Requirements and component bindings → architecture/service-contract revisions and checked export packages. Limits: Hardware and software decompositions can differ with explicit mappings. Native electrical/geometry/software tools remain replaceable. Mission behavior and target deployment still require implementation/verification. */
port records : ControlPort;
ref item architectureServiceContract : ArchitectureServiceContract [0..*];
ref item ePSModelArtifact : EPSModelArtifact [0..*];
ref item softwareArtifact : SoftwareArtifact [0..*];
}
@SourceRecord { identifier = "L03"; sourceText = "Architecture and service contracts"; sourceLocator = "final_report/traceability/logical-architecture.json"; status = "author-reviewed logical responsibility; physical realization and verification pending"; citationRecord = ""; }
part def <'L04'> Components { doc /* Component and lifecycle characterization. Maintain sourced COTS/custom component descriptions, ranges, electrical/thermal/resource properties, tolerances, heritage/evidence limits, RAM assumptions, options, quantities, BOMs, and scoped cost rollups. Bind candidate properties to architecture occurrences and model parameters. Inputs and outputs: Supplier/native design/test information and architecture revision → characterization/BOM/cost/RAM input revisions with unknowns. Limits: Datasheet and heritage claims stay separate from mission verification. No default failure rate or cost. */
port records : ControlPort;
ref item componentCharacterization : ComponentCharacterization [0..*];
ref item bOMCostRAM : BOMCostRAM [0..*];
}
@SourceRecord { identifier = "L04"; sourceText = "Component and lifecycle characterization"; sourceLocator = "final_report/traceability/logical-architecture.json"; status = "author-reviewed logical responsibility; physical realization and verification pending"; citationRecord = ""; }
part def <'L05'> Analysis { doc /* Scenario and analysis orchestration. Specify orbit/attitude/environment/load/mode/fault/control sequences, compose applicable analysis models, execute static/dynamic/resource/RAM analyses, compare options consistently, and reproduce runs. Manage numerical coupling, elapsed simulation time, fidelity/runtime tradeoffs, and external engine results. Inputs and outputs: Frozen analysis plan, configurations, models, validity decision, criteria → run manifest, raw outputs, logs, derived quantities, candidate comparison. Limits: Execution success is distinct from credibility and verification verdict. No imposed simulator or transport. */
port records : ControlPort;
ref item scenarioAnalysisPlan : ScenarioAnalysisPlan [0..*];
ref item runPackage : RunPackage [0..*];
}
@SourceRecord { identifier = "L05"; sourceText = "Scenario and analysis orchestration"; sourceLocator = "final_report/traceability/logical-architecture.json"; status = "author-reviewed logical responsibility; physical realization and verification pending"; citationRecord = ""; }
part def <'L06'> Credibility { doc /* Model credibility and observation reconciliation. Register model purpose, assumptions, parameters, validity domain, error/uncertainty and calibration/validation basis. Interpret raw observations through calibration, active-unit mapping, quality and clock information. Compare expected/observed behavior and propose model/property updates or fault hypotheses. Inputs and outputs: Model/scenario context, results, observations → applicability/credibility report, residuals, ambiguity, calibration proposal. Limits: Preserves independent validation evidence. A new parameter fit creates a proposed revision. No automatic model overwrite, confirmed fault diagnosis, or actuation. */
port records : ControlPort;
ref item modelCredibility : ModelCredibility [0..*];
ref item observationPackage : ObservationPackage [0..*];
}
@SourceRecord { identifier = "L06"; sourceText = "Model credibility and observation reconciliation"; sourceLocator = "final_report/traceability/logical-architecture.json"; status = "author-reviewed logical responsibility; physical realization and verification pending"; citationRecord = ""; }
part def <'L07'> Verification { doc /* Verification specification and safety. Define inspection/analysis/demonstration/test cases, criteria, conditions, DUT/equipment interaction, procedures, capture completeness, hazards, fault bounds, aborts, and readiness. Evaluate admissible results and retain remaining obligations. Inputs and outputs: Requirements, contracts, model-credibility reports, results, technician decisions → specification, readiness record, EPS evidence verdict, residual verification plan. Limits: Technician/facility approval and physical protections remain external authority. Missing safety information blocks physical handoff. EPS verification and framework verification have different subjects. */
port records : ControlPort;
ref item verificationSpecification : VerificationSpecification [0..*];
}
@SourceRecord { identifier = "L07"; sourceText = "Verification specification and safety"; sourceLocator = "final_report/traceability/logical-architecture.json"; status = "author-reviewed logical responsibility; physical realization and verification pending"; citationRecord = ""; }
part def <'L08'> Configuration { doc /* Information and configuration authority. Control identities, schemas, shared quantity/time vocabulary, relation types, artifact registrations, immutable baseline/run manifests, provenance, dependency revisions, transfer checks, and recoverable evidence custody. Inputs and outputs: Domain submissions and native tool artifacts → accepted registrations/baselines, transformation/quality checks, retrieval and reconstruction packages. Limits: Governs accepted information and revision identity. Domain owners define meaning and humans authorize decisions. Storage, schema syntax, languages, and deployment remain open. */
port records : ControlPort;
ref item baselineManifest : BaselineManifest [0..*];
}
@SourceRecord { identifier = "L08"; sourceText = "Information and configuration authority"; sourceLocator = "final_report/traceability/logical-architecture.json"; status = "author-reviewed logical responsibility; physical realization and verification pending"; citationRecord = ""; }
part def <'L09'> Review { doc /* Case workspace and technical review. Provide role-oriented authoring, guided tailoring, tasks, reviewable tables/plots and a few architecture/interface views. Present traces, changes, findings, costs and uncertainty. Capture review outcomes and framework evaluation task/effort/cost observations. Inputs and outputs: Controlled domain/evidence packages and guidance → case declarations, review packages, findings, task/evaluation records, lesson proposals. Limits: User-facing interface capability. Multiple stakeholder roles may be performed by one person. Rendering is derived from accepted records. Reviews confer no simulated stakeholder approval. */
port records : ControlPort;
ref item knowledgeCaseReview : KnowledgeCaseReview [0..*];
ref item frameworkEvaluation : FrameworkEvaluation [0..*];
}
@SourceRecord { identifier = "L09"; sourceText = "Case workspace and technical review"; sourceLocator = "final_report/traceability/logical-architecture.json"; status = "author-reviewed logical responsibility; physical realization and verification pending"; citationRecord = ""; }
part def LogicalFramework :> Framework {
part L01 : Guidance;
part L02 : Governance;
part L03 : Contracts;
part L04 : Components;
part L05 : Analysis;
part L06 : Credibility;
part L07 : Verification;
part L08 : Configuration;
part L09 : Review;
interface LC01_01 : Control connect L01.records to L09.records;
interface LC01_02 : Control connect L01.records to L02.records;
interface LC01_03 : Control connect L01.records to L04.records;
interface LC01_04 : Control connect L01.records to L07.records;
interface LC02_05 : Control connect L01.records to L08.records;
interface LC02_06 : Control connect L02.records to L08.records;
interface LC02_07 : Control connect L03.records to L08.records;
interface LC02_08 : Control connect L04.records to L08.records;
interface LC02_09 : Control connect L05.records to L08.records;
interface LC02_10 : Control connect L06.records to L08.records;
interface LC02_11 : Control connect L07.records to L08.records;
interface LC02_12 : Control connect L09.records to L08.records;
interface LC03_13 : Control connect L02.records to L03.records;
interface LC03_14 : Control connect L02.records to L04.records;
interface LC03_15 : Control connect L02.records to L06.records;
interface LC03_16 : Control connect L02.records to L07.records;
interface LC04_17 : Control connect L03.records to L04.records;
interface LC05_18 : Control connect L03.records to L05.records;
interface LC05_19 : Control connect L04.records to L05.records;
interface LC05_20 : Control connect L06.records to L05.records;
interface LC05_21 : Control connect L07.records to L05.records;
interface LC06_22 : Control connect L05.records to L06.records;
interface LC06_23 : Control connect L06.records to L07.records;
interface LC06_24 : Control connect L07.records to L02.records;
interface LC07_25 : Control connect L03.records to L07.records;
interface LC07_26 : Control connect L03.records to L05.records;
interface LC08_27 : Control connect L06.records to L04.records;
interface LC08_28 : Control connect L06.records to L03.records;
interface LC08_29 : Control connect L06.records to L02.records;
interface LC09_30 : Control connect L02.records to L09.records;
interface LC09_31 : Control connect L04.records to L09.records;
interface LC09_32 : Control connect L06.records to L09.records;
interface LC09_33 : Control connect L07.records to L09.records;
interface LC09_34 : Control connect L08.records to L09.records;
interface LC10_35 : Control connect L09.records to L01.records;
interface LC10_36 : Control connect L07.records to L01.records;
interface LC10_37 : Control connect L06.records to L01.records;
}
part logical : LogicalFramework;
item LC01Contract : EngineeringArtifact { doc /* L01 ↔ L09, L02, L04, L07 | Knowledge query/guidance/recipe and reviewed lesson proposal. A knowledge change has its own revision and affected-use references. */ }
item LC02Contract : EngineeringArtifact { doc /* Every capability ↔ L08 | Read exact baseline, submit identified revision, register artifact, verify transfer, retrieve evidence, and propose successor baseline. Common envelope and typed registration outcome. */ }
item LC03Contract : EngineeringArtifact { doc /* L02 ↔ L03, L04, L06, L07 | Requirement/criterion/dependency/change-impact and domain change proposals. L02 coordinates impact across design, model, service, BOM/cost and evidence. */ }
item LC04Contract : EngineeringArtifact { doc /* L03 ↔ L04 | Architecture occurrence/component binding, interface constraints, characterization/BOM and RAM topology inputs. Occurrence quantities remain distinct from catalog definitions. */ }
item LC05Contract : EngineeringArtifact { doc /* L03, L04, L06, L07 → L05 | Architecture/service/configuration, component/model inputs, applicability report, scenario and verification criteria → a frozen analysis/run request. Missing information prevents an unsupported verification claim. */ }
item LC06Contract : EngineeringArtifact { doc /* L05 → L06 → L07 → L02 | Raw run package → applicability/expected-observed assessment → evidence verdict/residual obligations → requirement/decision status and change proposal. LC02 controls each revision. */ }
item LC07Contract : EngineeringArtifact { doc /* L03 ↔ L07 and L05 | Service contract, target export/mapping and guard/effect/resource-test specifications ↔ checked generated artifacts and contract-test results. Same contract revision binds hardware/model/flight/ground views. */ }
item LC08Contract : EngineeringArtifact { doc /* L06 ↔ L04, L03, L02 | Observation/calibration/diagnostic finding → proposed parameter, characterization, architecture or requirement change. A successor run is required for affected claims. */ }
item LC09Contract : EngineeringArtifact { doc /* L02, L04, L06, L07, L08 → L09 | Decision/trace/BOM/cost/credibility/verdict/evidence package → derived review views. Findings/dispositions return to the responsible capability via L02. */ }
item LC10Contract : EngineeringArtifact { doc /* L09, L07, L06 → L01 | Reviewed reusable lesson, example and method/recipe correction. L01 separates local empirical learning from general literature claims. */ }
#sourceTrace dependency contract_LC01_01 from LogicalFramework::LC01_01 to LC01Contract;
#sourceTrace dependency contract_LC01_02 from LogicalFramework::LC01_02 to LC01Contract;
#sourceTrace dependency contract_LC01_03 from LogicalFramework::LC01_03 to LC01Contract;
#sourceTrace dependency contract_LC01_04 from LogicalFramework::LC01_04 to LC01Contract;
#sourceTrace dependency contract_LC02_05 from LogicalFramework::LC02_05 to LC02Contract;
#sourceTrace dependency contract_LC02_06 from LogicalFramework::LC02_06 to LC02Contract;
#sourceTrace dependency contract_LC02_07 from LogicalFramework::LC02_07 to LC02Contract;
#sourceTrace dependency contract_LC02_08 from LogicalFramework::LC02_08 to LC02Contract;
#sourceTrace dependency contract_LC02_09 from LogicalFramework::LC02_09 to LC02Contract;
#sourceTrace dependency contract_LC02_10 from LogicalFramework::LC02_10 to LC02Contract;
#sourceTrace dependency contract_LC02_11 from LogicalFramework::LC02_11 to LC02Contract;
#sourceTrace dependency contract_LC02_12 from LogicalFramework::LC02_12 to LC02Contract;
#sourceTrace dependency contract_LC03_13 from LogicalFramework::LC03_13 to LC03Contract;
#sourceTrace dependency contract_LC03_14 from LogicalFramework::LC03_14 to LC03Contract;
#sourceTrace dependency contract_LC03_15 from LogicalFramework::LC03_15 to LC03Contract;
#sourceTrace dependency contract_LC03_16 from LogicalFramework::LC03_16 to LC03Contract;
#sourceTrace dependency contract_LC04_17 from LogicalFramework::LC04_17 to LC04Contract;
#sourceTrace dependency contract_LC05_18 from LogicalFramework::LC05_18 to LC05Contract;
#sourceTrace dependency contract_LC05_19 from LogicalFramework::LC05_19 to LC05Contract;
#sourceTrace dependency contract_LC05_20 from LogicalFramework::LC05_20 to LC05Contract;
#sourceTrace dependency contract_LC05_21 from LogicalFramework::LC05_21 to LC05Contract;
#sourceTrace dependency contract_LC06_22 from LogicalFramework::LC06_22 to LC06Contract;
#sourceTrace dependency contract_LC06_23 from LogicalFramework::LC06_23 to LC06Contract;
#sourceTrace dependency contract_LC06_24 from LogicalFramework::LC06_24 to LC06Contract;
#sourceTrace dependency contract_LC07_25 from LogicalFramework::LC07_25 to LC07Contract;
#sourceTrace dependency contract_LC07_26 from LogicalFramework::LC07_26 to LC07Contract;
#sourceTrace dependency contract_LC08_27 from LogicalFramework::LC08_27 to LC08Contract;
#sourceTrace dependency contract_LC08_28 from LogicalFramework::LC08_28 to LC08Contract;
#sourceTrace dependency contract_LC08_29 from LogicalFramework::LC08_29 to LC08Contract;
#sourceTrace dependency contract_LC09_30 from LogicalFramework::LC09_30 to LC09Contract;
#sourceTrace dependency contract_LC09_31 from LogicalFramework::LC09_31 to LC09Contract;
#sourceTrace dependency contract_LC09_32 from LogicalFramework::LC09_32 to LC09Contract;
#sourceTrace dependency contract_LC09_33 from LogicalFramework::LC09_33 to LC09Contract;
#sourceTrace dependency contract_LC09_34 from LogicalFramework::LC09_34 to LC09Contract;
#sourceTrace dependency contract_LC10_35 from LogicalFramework::LC10_35 to LC10Contract;
#sourceTrace dependency contract_LC10_36 from LogicalFramework::LC10_36 to LC10Contract;
#sourceTrace dependency contract_LC10_37 from LogicalFramework::LC10_37 to LC10Contract;
#primaryResponsibility allocation responsibility_FR_01_L02 allocate FrameworkRequirements::FR_01 to logical.L02;
#primaryResponsibility allocation responsibility_FR_02_L01 allocate FrameworkRequirements::FR_02 to logical.L01;
#supportingResponsibility allocation responsibility_FR_02_L09 allocate FrameworkRequirements::FR_02 to logical.L09;
#primaryResponsibility allocation responsibility_FR_03_L01 allocate FrameworkRequirements::FR_03 to logical.L01;
#supportingResponsibility allocation responsibility_FR_03_L07 allocate FrameworkRequirements::FR_03 to logical.L07;
#primaryResponsibility allocation responsibility_FR_04_L02 allocate FrameworkRequirements::FR_04 to logical.L02;
#supportingResponsibility allocation responsibility_FR_04_L08 allocate FrameworkRequirements::FR_04 to logical.L08;
#primaryResponsibility allocation responsibility_FR_05_L02 allocate FrameworkRequirements::FR_05 to logical.L02;
#supportingResponsibility allocation responsibility_FR_05_L08 allocate FrameworkRequirements::FR_05 to logical.L08;
#primaryResponsibility allocation responsibility_FR_06_L02 allocate FrameworkRequirements::FR_06 to logical.L02;
#supportingResponsibility allocation responsibility_FR_06_L08 allocate FrameworkRequirements::FR_06 to logical.L08;
#primaryResponsibility allocation responsibility_FR_07_L08 allocate FrameworkRequirements::FR_07 to logical.L08;
#primaryResponsibility allocation responsibility_FR_08_L08 allocate FrameworkRequirements::FR_08 to logical.L08;
#primaryResponsibility allocation responsibility_FR_09_L08 allocate FrameworkRequirements::FR_09 to logical.L08;
#supportingResponsibility allocation responsibility_FR_09_L06 allocate FrameworkRequirements::FR_09 to logical.L06;
#primaryResponsibility allocation responsibility_FR_10_L05 allocate FrameworkRequirements::FR_10 to logical.L05;
#supportingResponsibility allocation responsibility_FR_10_L08 allocate FrameworkRequirements::FR_10 to logical.L08;
#supportingResponsibility allocation responsibility_FR_10_L09 allocate FrameworkRequirements::FR_10 to logical.L09;
#primaryResponsibility allocation responsibility_FR_11_L02 allocate FrameworkRequirements::FR_11 to logical.L02;
#supportingResponsibility allocation responsibility_FR_11_L07 allocate FrameworkRequirements::FR_11 to logical.L07;
#supportingResponsibility allocation responsibility_FR_11_L09 allocate FrameworkRequirements::FR_11 to logical.L09;
#primaryResponsibility allocation responsibility_FR_12_L04 allocate FrameworkRequirements::FR_12 to logical.L04;
#primaryResponsibility allocation responsibility_FR_13_L04 allocate FrameworkRequirements::FR_13 to logical.L04;
#primaryResponsibility allocation responsibility_FR_14_L05 allocate FrameworkRequirements::FR_14 to logical.L05;
#supportingResponsibility allocation responsibility_FR_14_L04 allocate FrameworkRequirements::FR_14 to logical.L04;
#supportingResponsibility allocation responsibility_FR_14_L02 allocate FrameworkRequirements::FR_14 to logical.L02;
#primaryResponsibility allocation responsibility_FR_15_L03 allocate FrameworkRequirements::FR_15 to logical.L03;
#primaryResponsibility allocation responsibility_FR_16_L05 allocate FrameworkRequirements::FR_16 to logical.L05;
#supportingResponsibility allocation responsibility_FR_16_L03 allocate FrameworkRequirements::FR_16 to logical.L03;
#supportingResponsibility allocation responsibility_FR_16_L04 allocate FrameworkRequirements::FR_16 to logical.L04;
#primaryResponsibility allocation responsibility_FR_17_L02 allocate FrameworkRequirements::FR_17 to logical.L02;
#supportingResponsibility allocation responsibility_FR_17_L04 allocate FrameworkRequirements::FR_17 to logical.L04;
#primaryResponsibility allocation responsibility_FR_18_L03 allocate FrameworkRequirements::FR_18 to logical.L03;
#supportingResponsibility allocation responsibility_FR_18_L05 allocate FrameworkRequirements::FR_18 to logical.L05;
#supportingResponsibility allocation responsibility_FR_18_L08 allocate FrameworkRequirements::FR_18 to logical.L08;
#primaryResponsibility allocation responsibility_FR_19_L05 allocate FrameworkRequirements::FR_19 to logical.L05;
#supportingResponsibility allocation responsibility_FR_19_L07 allocate FrameworkRequirements::FR_19 to logical.L07;
#primaryResponsibility allocation responsibility_FR_20_L05 allocate FrameworkRequirements::FR_20 to logical.L05;
#supportingResponsibility allocation responsibility_FR_20_L06 allocate FrameworkRequirements::FR_20 to logical.L06;
#supportingResponsibility allocation responsibility_FR_20_L04 allocate FrameworkRequirements::FR_20 to logical.L04;
#primaryResponsibility allocation responsibility_FR_21_L06 allocate FrameworkRequirements::FR_21 to logical.L06;
#supportingResponsibility allocation responsibility_FR_21_L07 allocate FrameworkRequirements::FR_21 to logical.L07;
#primaryResponsibility allocation responsibility_FR_22_L06 allocate FrameworkRequirements::FR_22 to logical.L06;
#supportingResponsibility allocation responsibility_FR_22_L04 allocate FrameworkRequirements::FR_22 to logical.L04;
#supportingResponsibility allocation responsibility_FR_22_L02 allocate FrameworkRequirements::FR_22 to logical.L02;
#primaryResponsibility allocation responsibility_FR_23_L05 allocate FrameworkRequirements::FR_23 to logical.L05;
#supportingResponsibility allocation responsibility_FR_23_L06 allocate FrameworkRequirements::FR_23 to logical.L06;
#primaryResponsibility allocation responsibility_FR_24_L05 allocate FrameworkRequirements::FR_24 to logical.L05;
#supportingResponsibility allocation responsibility_FR_24_L06 allocate FrameworkRequirements::FR_24 to logical.L06;
#supportingResponsibility allocation responsibility_FR_24_L07 allocate FrameworkRequirements::FR_24 to logical.L07;
#primaryResponsibility allocation responsibility_FR_25_L06 allocate FrameworkRequirements::FR_25 to logical.L06;
#primaryResponsibility allocation responsibility_FR_26_L02 allocate FrameworkRequirements::FR_26 to logical.L02;
#supportingResponsibility allocation responsibility_FR_26_L04 allocate FrameworkRequirements::FR_26 to logical.L04;
#supportingResponsibility allocation responsibility_FR_26_L07 allocate FrameworkRequirements::FR_26 to logical.L07;
#primaryResponsibility allocation responsibility_FR_27_L04 allocate FrameworkRequirements::FR_27 to logical.L04;
#supportingResponsibility allocation responsibility_FR_27_L05 allocate FrameworkRequirements::FR_27 to logical.L05;
#supportingResponsibility allocation responsibility_FR_27_L08 allocate FrameworkRequirements::FR_27 to logical.L08;
#primaryResponsibility allocation responsibility_FR_28_L07 allocate FrameworkRequirements::FR_28 to logical.L07;
#primaryResponsibility allocation responsibility_FR_29_L07 allocate FrameworkRequirements::FR_29 to logical.L07;
#supportingResponsibility allocation responsibility_FR_29_L09 allocate FrameworkRequirements::FR_29 to logical.L09;
#primaryResponsibility allocation responsibility_FR_30_L07 allocate FrameworkRequirements::FR_30 to logical.L07;
#primaryResponsibility allocation responsibility_FR_31_L06 allocate FrameworkRequirements::FR_31 to logical.L06;
#supportingResponsibility allocation responsibility_FR_31_L08 allocate FrameworkRequirements::FR_31 to logical.L08;
#primaryResponsibility allocation responsibility_FR_32_L06 allocate FrameworkRequirements::FR_32 to logical.L06;
#supportingResponsibility allocation responsibility_FR_32_L08 allocate FrameworkRequirements::FR_32 to logical.L08;
#primaryResponsibility allocation responsibility_FR_33_L03 allocate FrameworkRequirements::FR_33 to logical.L03;
#primaryResponsibility allocation responsibility_FR_34_L03 allocate FrameworkRequirements::FR_34 to logical.L03;
#supportingResponsibility allocation responsibility_FR_34_L05 allocate FrameworkRequirements::FR_34 to logical.L05;
#primaryResponsibility allocation responsibility_FR_35_L03 allocate FrameworkRequirements::FR_35 to logical.L03;
#supportingResponsibility allocation responsibility_FR_35_L05 allocate FrameworkRequirements::FR_35 to logical.L05;
#supportingResponsibility allocation responsibility_FR_35_L07 allocate FrameworkRequirements::FR_35 to logical.L07;
#primaryResponsibility allocation responsibility_FR_36_L03 allocate FrameworkRequirements::FR_36 to logical.L03;
#supportingResponsibility allocation responsibility_FR_36_L04 allocate FrameworkRequirements::FR_36 to logical.L04;
#supportingResponsibility allocation responsibility_FR_36_L05 allocate FrameworkRequirements::FR_36 to logical.L05;
#primaryResponsibility allocation responsibility_FR_37_L09 allocate FrameworkRequirements::FR_37 to logical.L09;
#primaryResponsibility allocation responsibility_FR_38_L09 allocate FrameworkRequirements::FR_38 to logical.L09;
#supportingResponsibility allocation responsibility_FR_38_L02 allocate FrameworkRequirements::FR_38 to logical.L02;
#supportingResponsibility allocation responsibility_FR_38_L08 allocate FrameworkRequirements::FR_38 to logical.L08;
#primaryResponsibility allocation responsibility_FR_39_L09 allocate FrameworkRequirements::FR_39 to logical.L09;
#supportingResponsibility allocation responsibility_FR_39_L01 allocate FrameworkRequirements::FR_39 to logical.L01;
#supportingResponsibility allocation responsibility_FR_39_L08 allocate FrameworkRequirements::FR_39 to logical.L08;
#primaryResponsibility allocation responsibility_FR_40_L09 allocate FrameworkRequirements::FR_40 to logical.L09;
#supportingResponsibility allocation responsibility_FR_40_L01 allocate FrameworkRequirements::FR_40 to logical.L01;
#supportingResponsibility allocation responsibility_FR_40_L08 allocate FrameworkRequirements::FR_40 to logical.L08;
allocation function_F01_L01 allocate logical.f01 to logical.L01;
allocation function_F01_L09 allocate logical.f01 to logical.L09;
allocation function_F01_L08 allocate logical.f01 to logical.L08;
allocation function_F02_L02 allocate logical.f02 to logical.L02;
allocation function_F02_L03 allocate logical.f02 to logical.L03;
allocation function_F02_L07 allocate logical.f02 to logical.L07;
allocation function_F03_L04 allocate logical.f03 to logical.L04;
allocation function_F03_L05 allocate logical.f03 to logical.L05;
allocation function_F03_L06 allocate logical.f03 to logical.L06;
allocation function_F04_L05 allocate logical.f04 to logical.L05;
allocation function_F04_L06 allocate logical.f04 to logical.L06;
allocation function_F04_L08 allocate logical.f04 to logical.L08;
allocation function_F05_L03 allocate logical.f05 to logical.L03;
allocation function_F05_L07 allocate logical.f05 to logical.L07;
allocation function_F05_L05 allocate logical.f05 to logical.L05;
allocation function_F06_L07 allocate logical.f06 to logical.L07;
allocation function_F06_L03 allocate logical.f06 to logical.L03;
allocation function_F06_L06 allocate logical.f06 to logical.L06;
allocation function_F07_L08 allocate logical.f07 to logical.L08;
allocation function_F07_L02 allocate logical.f07 to logical.L02;
allocation function_F07_L06 allocate logical.f07 to logical.L06;
allocation function_F07_L04 allocate logical.f07 to logical.L04;
allocation function_F08_L09 allocate logical.f08 to logical.L09;
allocation function_F08_L02 allocate logical.f08 to logical.L02;
allocation function_F08_L01 allocate logical.f08 to logical.L01;
allocation function_F08_L08 allocate logical.f08 to logical.L08;

}
