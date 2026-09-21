// Initial OOSEM logical decomposition of the framework.
package FrameworkLogicalDecomposition {
    private import FrameworkBlackBoxSpecification
            ::'Specified Nanosatellite EPS Engineering Framework';

    doc
    /* This package defines the implementation-independent decomposition used to begin the OOSEM
     * Define Logical Architecture activity. The logical framework inherits the complete black-box
     * specification and adds only abstract responsibilities. Products, file formats, protocols,
     * deployment nodes, and physical components remain open for physical architecture synthesis.
     *
     * Evidence basis: the mandatory black-box requirements and their literature traces are the
     * primary architecture inputs. Buruso et al. (2026), Secs. 4.4 and 5.1 and Table 5, support
     * lifecycle continuity, interoperability, modularity, and resource fit. Rostamnia et al. (2026),
     * Secs. 8.4-8.6 and Table 13, support explicit interfaces, shared semantics, configuration
     * governance, provenance, and assurance. Rojas Ramirez et al. (2022), Sec. 4.2.3, supports
     * transfer verification. Vizitiu et al. (2025), Sec. 4.7 and Table 3, supports efficiency,
     * collaboration, traceability, error reduction, and flexibility as evaluation concerns.
     */

    part def 'Logical Component' {
        doc
        /* Abstract responsibility within the framework logical design. A logical component may be
         * allocated to hardware, software, data, or procedure components in multiple ways.
         */
    }

    part def 'External Interface Component' :> 'Logical Component' {
        doc
        /* Mediates one black-box boundary while preserving its defined item types, directions,
         * transfer status, and semantics without selecting a transport or file format.
         */
    }

    part def 'Application Component' :> 'Logical Component' {
        doc
        /* Performs the application logic that transforms black-box requests and controlled records
         * into the assessments, packages, verdicts, and statuses required by the service functions.
         */
    }

    part def 'Infrastructure Component' :> 'Logical Component' {
        doc
        /* Manages internally generated control, configuration, evidence, provenance, transfer
         * assurance, and measurement responsibilities shared by the application components.
         */
    }

    // External interface components correspond one-to-one with the six black-box interfaces.
    part def <'LIF-01'> 'Mission Application Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-01 traffic with the Academic Mission Team. */
    }

    part def <'LIF-02'> 'Research Governance Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-02 traffic with the Academic Researcher. */
    }

    part def <'LIF-03'> 'Independent Review Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-03 traffic with the Reviewer. */
    }

    part def <'LIF-04'> 'Model Control Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-04 traffic with the Versioned System Model. */
    }

    part def <'LIF-05'> 'Analysis Execution Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-05 traffic with Analysis Tools. */
    }

    part def <'LIF-06'> 'Evidence Custody Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-06 traffic with the Evidence Repository. */
    }

    // Application components initially correspond one-to-one with the six black-box services.
    part def <'LAP-01'> 'Evidence Chain Manager' :> 'Application Component' {
        doc
        /* Scopes and validates designated evidence chains and issues their assessments. */
    }

    part def <'LAP-02'> 'Case Configuration Manager' :> 'Application Component' {
        doc
        /* Captures, validates, and issues controlled EPS case configurations and status. */
    }

    part def <'LAP-03'> 'Analysis Reproduction Manager' :> 'Application Component' {
        doc
        /* Prepares controlled reproduction packages, evaluates results, and issues verdicts. */
    }

    part def <'LAP-04'> 'Design Change Assessment Manager' :> 'Application Component' {
        doc
        /* Validates change requests, determines impact, and assembles change evidence. */
    }

    part def <'LAP-05'> 'Candidate Evaluation Manager' :> 'Application Component' {
        doc
        /* Establishes a common comparison basis, gates feasibility, and compares EPS candidates. */
    }

    part def <'LAP-06'> 'Design Review Manager' :> 'Application Component' {
        doc
        /* Assembles review packages, coordinates selected reproduction, and manages findings. */
    }

    // Infrastructure components provide shared logical resources and controls.
    part def <'LIN-01'> 'Workflow Control Manager' :> 'Infrastructure Component' {
        doc
        /* Dispatches service work, applies terminal outcome guards, exposes discrepancies, and
         * controls recovery according to the inherited operational state behavior.
         */
    }

    part def <'LIN-02'> 'Transfer Assurance Manager' :> 'Infrastructure Component' {
        doc
        /* Checks source and configuration identity, structural completeness, semantic
         * compatibility, and provenance before any boundary transfer is accepted.
         */
    }

    part def <'LIN-03'> 'Baseline and Configuration Manager' :> 'Infrastructure Component' {
        doc
        /* Controls the common core, case configurations, immutable baseline identities, approved
         * adaptations, and distinct successor revisions.
         */
    }

    part def <'LIN-04'> 'Evidence and Provenance Manager' :> 'Infrastructure Component' {
        doc
        /* Retains and retrieves the required model, evidence, assessment, verdict, package,
         * discrepancy, trace, and provenance records by item and baseline identity.
         */
    }

    part def <'LIN-05'> 'Evaluation Measurement Manager' :> 'Infrastructure Component' {
        doc
        /* Applies the fixed evaluation manifest and measurement protocols while preserving raw
         * observations, correctness gates, uncertainty, and derived MOP results.
         */
    }

    part def <'LA-00'> 'Logical Nanosatellite EPS Engineering Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Logical specialization of the complete framework black box. The parts below define the
         * initial responsibility decomposition. Their interactions, ports, stores, properties, and
         * state behavior are refined in the following logical architecture steps.
         */

        part missionApplicationInterface : 'Mission Application Interface Manager';
        part researchGovernanceInterface : 'Research Governance Interface Manager';
        part independentReviewInterface : 'Independent Review Interface Manager';
        part modelControlInterface : 'Model Control Interface Manager';
        part analysisExecutionInterface : 'Analysis Execution Interface Manager';
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager';

        part evidenceChainManager : 'Evidence Chain Manager';
        part caseConfigurationManager : 'Case Configuration Manager';
        part analysisReproductionManager : 'Analysis Reproduction Manager';
        part designChangeAssessmentManager : 'Design Change Assessment Manager';
        part candidateEvaluationManager : 'Candidate Evaluation Manager';
        part designReviewManager : 'Design Review Manager';

        part workflowControlManager : 'Workflow Control Manager';
        part transferAssuranceManager : 'Transfer Assurance Manager';
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager';
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager';
        part evaluationMeasurementManager : 'Evaluation Measurement Manager';
    }

    part frameworkLogical : 'Logical Nanosatellite EPS Engineering Framework';
} // package FrameworkLogicalDecomposition
