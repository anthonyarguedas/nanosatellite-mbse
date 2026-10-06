// Report-only views of FrameworkLogical::logical. No new architectural parts,
// deployments, services or requirement satisfaction assertions are introduced.
// Each reference is bound to the existing part and retains its definition,
// typed record references and ControlPort. Documentation summarizes those
// records, required/provided services and existing primaryResponsibility
// allocations. The three groups organize views, not additional subsystems.
package LogicalResponsibilityViews {
    private import Views::*;
    private import FrameworkLogical::*;

    // L01: KnowledgeCaseReview; L02: NeedRequirementDecision;
    // L03: ArchitectureServiceContract, EPSModelArtifact, SoftwareArtifact.
    package DefinitionResponsibilities {
        ref part L01 : Guidance = logical.L01 {
            doc /* Engineering guidance and knowledge
Records: Sourced methods, templates, examples and lessons.
Required: Case goals and reviewed findings.
Provided: Applicable guidance and analysis recipes.
Primary FR: 02, 03. */
        }
        ref part L02 : Governance = logical.L02 {
            doc /* Needs, requirements and decision governance
Records: Requirements, decisions, links, impacts and dispositions.
Required: Domain revisions and evidence verdicts.
Provided: Derived requirements; affected assertions and changes.
Primary FR: 01, 04, 05, 06, 11, 17, 26. */
        }
        ref part L03 : Contracts = logical.L03 {
            doc /* Architecture and service contracts
Records: Generic/case structure, interfaces, modes and software contracts.
Required: Requirements and component properties.
Provided: Mappings, dictionaries and sequence specifications.
Primary FR: 15, 18, 33, 34, 35, 36. */
        }
    }
    // L04: ComponentCharacterization, BOMCostRAM;
    // L05: ScenarioAnalysisPlan, RunPackage;
    // L06: ModelCredibility, ObservationPackage.
    package AnalysisResponsibilities {
        ref part L04 : Components = logical.L04 {
            doc /* Component and lifecycle characterization
Records: Component facts, occurrence quantities, BOMs, quotes and failures.
Required: Architecture revisions and source updates.
Provided: Cost estimates and RAM representations, with unknowns.
Primary FR: 12, 13, 27. */
        }
        ref part L05 : Analysis = logical.L05 {
            doc /* Scenario and analysis orchestration
Records: Analysis plans, run packages and replay instructions.
Required: Frozen inputs, models, applicability and criteria.
Provided: Dynamic, virtual and battery/policy results;
common-basis comparisons and reproducible runs.
Primary FR: 10, 14, 16, 19, 20, 23, 24. */
        }
        ref part L06 : Credibility = logical.L06 {
            doc /* Model credibility and observation reconciliation
Records: Validity, calibration/validation, observation quality and timing.
Required: Models, results and supplied observation data.
Provided: Credibility assessments, residuals, alternatives and update proposals.
Primary FR: 21, 22, 25, 31, 32. */
        }
    }
    // L07: VerificationSpecification; L08: BaselineManifest;
    // L09: KnowledgeCaseReview, FrameworkEvaluation.
    package AssuranceResponsibilities {
        ref part L07 : Verification = logical.L07 {
            doc /* Verification specification and safety
Records: Verification specifications, proposals and scoped verdicts.
Required: Criteria, DUT/equipment profiles and admissible results.
Provided: Procedures, readiness and residual verification obligations.
Primary FR: 28, 29, 30. */
        }
        ref part L08 : Configuration = logical.L08 {
            doc /* Information and configuration authority
Records: Controlled identities, revisions and evidence custody.
Required: Identified domain and native-tool artifacts.
Provided: Checked transfers, baselines and reconstruction packages.
Primary FR: 07, 08, 09. */
        }
        ref part L09 : Review = logical.L09 {
            doc /* Case workspace and technical review
Records: Case declarations, findings, environment/evaluation records.
Required: Controlled evidence and guidance.
Provided: Views, reviews, adoption and two-case evaluation outcomes.
Primary FR: 37, 38, 39, 40. */
        }
    }
    view definitionResponsibilities {
        expose DefinitionResponsibilities::*;
        render asTreeDiagram;
    }
    view analysisResponsibilities {
        expose AnalysisResponsibilities::*;
        render asTreeDiagram;
    }
    view assuranceResponsibilities {
        expose AssuranceResponsibilities::*;
        render asTreeDiagram;
    }
}
