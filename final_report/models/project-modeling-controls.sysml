// Project controls on the OOSEM application and its comparison artifacts.
package ProjectModelingControls {
    private import ModelingMetadata::refinement;

    metadata def projectModelingControl;

    part def 'OOSEM Project Application' {
        doc
        /* The project activity that produces and controls the comparison model, report, evaluation
         * definitions, and recorded results. It is outside the framework solution boundary.
         */
    }

    part def 'Candidate Comparison Model' {
        doc
        /* The common descriptive model used to normalize candidate physical architectures for
         * comparison. It is distinct from every candidate's native implementation artifacts.
         */
    }

    requirement <'MC-00'> 'OOSEM Model Management Controls' {
        subject application : 'OOSEM Project Application';
        doc
        /* The OOSEM application uses a common formal representation and controlled project sources
         * so that candidate descriptions and reported results can be reviewed and reproduced. MC-01
         * and MC-02 govern study artifacts. They impose no implementation language, modeling tool,
         * repository, or configuration mechanism on a candidate framework solution.
         */

        require constraint statement {
            doc
            /* Every project modeling control is applied to the OOSEM study artifacts. */
        }
    }

    #projectModelingControl requirement <'MC-01'> 'Common SysML v2 Candidate Representation' {
        subject comparisonModel : 'Candidate Comparison Model';
        doc
        /* Every candidate framework physical architecture admitted to comparison shall be described
         * at the common comparison abstraction as conformant textual SysML v2. The description shall
         * identify its nodes, software, data, hardware or hosting resources, procedures, interfaces,
         * and logical-to-physical allocations, with evidence and assumptions distinguished. This is
         * a representation rule for the OOSEM study. Candidate implementations and their native
         * engineering artifacts are free to use other languages, methods, formats, and tools.
         * Verification is by source inspection and successful parsing and semantic validation of the
         * comparison model.
         */

        require constraint statement {
            doc
            /* Each admitted candidate has a conformant SysML v2 comparison description at the fixed
             * abstraction and evidence granularity.
             */
        }
    }

    #projectModelingControl requirement <'MC-02'> 'Version-Controlled OOSEM Source Baseline' {
        subject application : 'OOSEM Project Application';
        doc
        /* The OOSEM comparison model and report source shall be controlled as text files in one
         * version-controlled project repository, and each reported study baseline shall identify an
         * immutable repository revision. This controls the execution and reporting of the OOSEM
         * study. It does not require candidate solutions to use the same repository or configuration
         * mechanism. Verification is by repository inspection and reconstruction of the designated
         * comparison model and report from the recorded revision.
         * Supporting rationale: buruso2026modelbased Secs. 4.4 and 5.1;
         * rostamnia2026digitaltwin Secs. 8.4-8.6 and Table 13.
         */

        require constraint statement {
            doc
            /* The comparison model and report resolve to an immutable project-source revision from
             * which the reported study artifacts can be reconstructed.
             */
        }
    }

    #refinement dependency
        'Common SysML v2 Candidate Representation'
        to 'OOSEM Model Management Controls';
    #refinement dependency
        'Version-Controlled OOSEM Source Baseline'
        to 'OOSEM Model Management Controls';
} // package ProjectModelingControls
