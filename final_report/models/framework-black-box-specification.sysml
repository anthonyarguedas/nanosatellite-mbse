// Consolidated black-box system definition for the framework.
package FrameworkBlackBoxSpecification {
    private import ScalarValues::String;
    private import FrameworkExchangeDefinitions::*;
    private import FrameworkCriticalProperties::'Framework Evaluation Manifest';
    private import FrameworkCriticalProperties::'Measured Nanosatellite EPS Engineering Framework';

    metadata def requiredStore;

    item def 'Controlled Framework Record Set' {
        doc
        /* Required persistent information viewed at the system boundary. The definition states what
         * must be retained and retrievable. It does not select an internal storage component,
         * repository technology, or file format.
         */

        item modelRecords : 'Controlled Model Records' [0..*];
        item evidenceRecords : 'Retained Evidence Records' [0..*];
        item caseConfigurations : 'Controlled Case Configuration' [0..*];
        item evaluationManifest : 'Framework Evaluation Manifest';
        item chainAssessments : 'Evidence Chain Assessment' [0..*];
        item reproductionVerdicts : 'Reproduction Verdict' [0..*];
        item changePackages : 'Change Evidence Package' [0..*];
        item comparisonPackages : 'Candidate Comparison Package' [0..*];
        item reviewPackages : 'Review Package' [0..*];
        item reviewStatuses : 'Review Status' [0..*];
        item transferVerifications
            : FrameworkBoundaryInterfaces::'Transfer Verification Record' [0..*];
    }

    part def 'Specified Nanosatellite EPS Engineering Framework'
        :> 'Measured Nanosatellite EPS Engineering Framework' {
        doc
        /* Complete OOSEM black-box definition. Inherited features provide six boundary service
         * functions, six typed ports, and eleven measures of performance. The features below add
         * required stores and externally declared execution-resource characteristics. Internal
         * components remain unspecified.
         */

        ref #requiredStore item requiredRecords : 'Controlled Framework Record Set';

        attribute 'declared minimum execution environment' : String {
            doc
            /* Computing, storage, network, service, license, and tool prerequisites needed to
             * establish and execute a controlled framework baseline.
             */
        }
        attribute 'declared runtime dependencies' : String {
            doc
            /* Identified dependency names, versions, configurations, and acquisition instructions
             * needed to reconstruct execution from a controlled baseline.
             */
        }
    }

    part frameworkBlackBox : 'Specified Nanosatellite EPS Engineering Framework';
} // package FrameworkBlackBoxSpecification
