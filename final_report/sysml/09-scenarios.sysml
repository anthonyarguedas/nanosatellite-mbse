// OOSEM mission scenarios: enterprise actor actions and black-box system functions.
// Planned behavior, not executed tests, accepted changes, or authorized facility work.
package ScenarioViews {
    private import ScalarValues::*;
    private import StandardViewDefinitions::*;

    doc /* These scenarios refine SC01/UC01, SC02/UC02 and SC03/UC03 at the
        framework boundary. The framework checks, coordinates analyses, proposes
        revisions and preserves evidence. Engineers make engineering decisions;
        reviewers make review findings; the facility alone authorizes physical
        work. No EPS operation or physical test execution is a framework action.

        Responsibility metadata records the performer and intended fill color.
        scenarios.toml bridges those responsibilities to native metaclass styles:
        ActionUsage for framework functions, PerformActionUsage for calls to real
        external actor behavior. Syside does not select arbitrary metadata tags
        for coloring and does not consume a custom RenderStyle annotation.
        Initial/final circles are the inherited start/done snapshots. Named
        start/done merge nodes identify the scenario boundaries and collect
        alternative paths without a join that would wait for mutually exclusive
        outcomes. Guards describe observed conditions, not asserted test results.
        Each conditional succession also declares an optional named succession
        bound to its inherited transitionLink. It is the same guarded HappensBefore
        link, not an additional unconditional route. The explicit binding lets
        Syside 0.10.3 render the link and its short guard label. The Kernel library's
        TransitionPerformances::TPCGuardConstraint still governs that link.
    */

    // References to the actual report-context participants, not a new architecture.
    ref part framework : FrameworkDomain::Framework = FrameworkContext::context.framework;
    ref part engineers : FrameworkContext::Users = FrameworkContext::context.engineers;
    ref part reviewers : FrameworkContext::Reviewers = FrameworkContext::context.reviewers;
    ref part facility : FrameworkContext::Facility = FrameworkContext::context.facility;
    part def SafetyAuthority :> FrameworkDomain::Role {
        doc /* External responsible safety-review role. No staffing is asserted. */
    }
    ref part safetyAuthority : SafetyAuthority;

    metadata def FrameworkAction {
        :>> annotatedElement : SysML::ActionUsage;
        ref performer : SysML::PartUsage;
        attribute fillColor : String;
    }
    metadata def ExternalAction {
        :>> annotatedElement : SysML::PerformActionUsage;
        ref performer : SysML::PartUsage;
        attribute fillColor : String;
    }
    metadata def MissionScenario;

    // These definitions specify genuine external behavior invoked by the scenarios.
    action def Tailor {
        doc /* Engineers declare the case, the controlled common core and allowed
            adaptations. They write requirements and acceptance criteria, choose
            candidate options and submit sourced component, quantity and quote
            records. The framework does not invent missing stakeholder criteria. */
    }
    action def Review {
        doc /* External reviewers inspect the scoped evidence, assumptions,
            uncertainty, model applicability and unresolved findings. Their review
            findings do not replace the responsible engineer's disposition. */
    }
    action def Decide {
        doc /* Engineers retain their disposition of the options and review
            findings, including acceptance, rejection or an open decision. Gaps or
            unsupported checks cannot become supported claims by disposition. */
    }
    action def Request {
        doc /* Engineers identify a load, attitude, supply or software change and
            its subject baseline, rationale and submitted replacement records. */
    }
    action def Approve {
        out attribute accepted : Boolean;
        doc /* Engineers accept or decline the reviewed change proposal. This
            decision is external. Acceptance permits a successor to be issued;
            it does not prove that unresolved claims are correct or supported. */
    }
    action def ReviewRepair {
        out attribute endorsed : Boolean;
        doc /* Engineers endorse or decline the proposed repair/test plan after
            reviewing proposed calibration/parameter updates, affected
            claim reassessments and the physical verification proposal, and retain
            a disposition. Pending or declined endorsement blocks readiness.
            Calibration and intended-use validation remain separate.
            Reviewing a proposal does not adopt a parameter revision automatically
            or authorize hardware operation. */
    }
    action def SafetyReview {
        out attribute cleared : Boolean;
        doc /* The external safety authority records review of hazards, operating
            limits, fault envelope, isolation, abort/recovery and responsible
            persons. Missing or uncleared review is false for the readiness guard;
            safety clearance is not facility authorization. */
    }
    action def Authorize {
        out attribute granted : Boolean;
        doc /* The facility grants or withholds authorization for the identified
            proposal, equipment/DUT configuration and procedure. Availability and
            local safety/operating rules are its responsibility. Physical execution
            would be a later external scenario and is not modeled as performed. */
    }

    action def 'SC01 / UC01' {
        @MissionScenario;
        doc /* Primary scenario path: define a controlled case, bind sourced
            options, coordinate applicable analyses on a common basis, review
            evidence, retain engineer disposition and a reconstructable package.
            Alternative paths retain gaps and undetermined claims. The checks
            apply to each scoped option/analysis family; partial results and gaps
            may coexist in the final review package. */

        attribute ready : Boolean = 'FW: bind options'.ready;
        attribute supported : Boolean = 'FW: coordinate analyses'.supported;
        merge 'SC01 start';
        perform action 'Engineer: tailor' : Tailor {
            @ExternalAction { performer = engineers meta SysML::PartUsage; fillColor = "#FFF0D6"; }
        }
        action 'FW: bind options' {
            out attribute ready : Boolean;
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Bind component identities, source revisions, quantities and
                dated quotes to the options. Check the common requirements,
                assumptions, criteria and model evidence for the scoped comparison.
                ready is false for any missing required data, prices, criteria or
                model evidence. An absent price or sample is not a zero. */
        }
        decide 'Inputs ready?';
        action 'FW: retain gaps' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Preserve the missing-data, price, criterion or model-evidence
                findings with affected claims and owners. Do not invent inputs or
                assert a completed comparison for the incomplete scope. */
        }
        action 'FW: coordinate analyses' {
            out attribute supported : Boolean;
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Run or coordinate applicable analyses under identified profiles
                on the common comparison basis. Preserve models, versions, inputs,
                raw outputs and applicability limits. supported is false when a
                requested check lacks a supported method/profile/model or usable
                evidence. The framework is not operating the EPS hardware. */
        }
        decide 'Checks supported?';
        action 'FW: mark undetermined' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Keep unsupported checks and their associated claims undetermined.
                Preserve valid partial results without an unqualified conclusion. */
        }
        merge 'Evidence';
        perform action 'Reviewer: review' : Review {
            @ExternalAction { performer = reviewers meta SysML::PartUsage; fillColor = "#FFF0D6"; }
        }
        perform action 'Engineer: decide' : Decide {
            @ExternalAction { performer = engineers meta SysML::PartUsage; fillColor = "#FFF0D6"; }
        }
        action 'FW: retain package' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Retain the scoped evidence, gaps, unsupported checks, reviewer
                findings and engineer disposition. Pin inputs, dependencies,
                models, methods, environment and comparison rules so the package
                can be reconstructed, including when a decision remains open. */
        }
        merge 'SC01 done';

        first start then 'SC01 start';
        first 'SC01 start' then 'Engineer: tailor';
        first 'Engineer: tailor' then 'FW: bind options';
        first 'FW: bind options' then 'Inputs ready?';
        succession inputsReady first 'Inputs ready?' if ready then 'FW: coordinate analyses' {
            succession '[ready]' [0..1] first 'Inputs ready?' then 'FW: coordinate analyses';
            bind '[ready]' = transitionLink;
        }
        succession inputsMissing first 'Inputs ready?' if not ready then 'FW: retain gaps' {
            succession '[not ready]' [0..1] first 'Inputs ready?' then 'FW: retain gaps';
            bind '[not ready]' = transitionLink;
        }
        first 'FW: retain gaps' then 'Evidence';
        first 'FW: coordinate analyses' then 'Checks supported?';
        succession checksSupported first 'Checks supported?' if supported then 'Evidence' {
            succession '[supported]' [0..1] first 'Checks supported?' then 'Evidence';
            bind '[supported]' = transitionLink;
        }
        succession checksUnsupported first 'Checks supported?' if not supported then 'FW: mark undetermined' {
            succession '[not supported]' [0..1] first 'Checks supported?' then 'FW: mark undetermined';
            bind '[not supported]' = transitionLink;
        }
        first 'FW: mark undetermined' then 'Evidence';
        first 'Evidence' then 'Reviewer: review';
        first 'Reviewer: review' then 'Engineer: decide';
        first 'Engineer: decide' then 'FW: retain package';
        first 'FW: retain package' then 'SC01 done';
        first 'SC01 done' then done;
    }

    action def 'SC02 / UC02' {
        @MissionScenario;
        doc /* Primary scenario path: register a compatible change, identify
            reciprocal impacts, revise records and reassess claims, review and
            accept the proposal, then issue a successor. A rejected transfer or
            declined change retains the previous accepted baseline. */

        attribute compatible : Boolean = 'FW: check transfer'.compatible;
        attribute accepted : Boolean = 'Engineer: approve'.accepted;
        merge 'SC02 start';
        perform action 'Engineer: request' : Request {
            @ExternalAction { performer = engineers meta SysML::PartUsage; fillColor = "#FFF0D6"; }
        }
        action 'FW: check transfer' {
            out attribute compatible : Boolean;
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Retain the raw request; check identifiers, dimensions, units,
                polarity, time/mode meanings, interfaces and provenance against
                the declared transfer contract before registering accepted content.
                Incompatible content cannot revise the accepted baseline. */
        }
        decide 'Compatible?';
        action 'FW: revise and reassess' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Register compatible content as a proposal. Identify reciprocal
                impacts on requirements, EPS/non-EPS models, BOMs, software/ground
                dictionaries, procedures and verification. Revise affected records
                and reassess associated claims. Distinguish regenerated, stale and
                unresolved evidence. Expose unsupported software targets and missing
                processor, memory, timing and power resource evidence explicitly.
                This action cannot make the engineering acceptance decision. */
        }
        perform action 'Reviewer: review' : Review {
            @ExternalAction { performer = reviewers meta SysML::PartUsage; fillColor = "#FFF0D6"; }
        }
        perform action 'Engineer: approve' : Approve {
            @ExternalAction { performer = engineers meta SysML::PartUsage; fillColor = "#FFF0D6"; }
        }
        decide 'Accepted?';
        action 'FW: issue successor' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Issue a distinct reviewed successor only after external
                acceptance. Retain the request, impacts, previous baseline,
                disposition and regenerated/stale/unresolved evidence statuses.
                An accepted successor is not itself proof of supported claims. */
        }
        merge 'Hold';
        action 'FW: keep baseline' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Reject incompatible transfers with explicit findings or retain
                the declined proposal and external disposition. Preserve the
                previous accepted baseline and raw submission in either case. */
        }
        merge 'SC02 done';

        first start then 'SC02 start';
        first 'SC02 start' then 'Engineer: request';
        first 'Engineer: request' then 'FW: check transfer';
        first 'FW: check transfer' then 'Compatible?';
        succession compatibleChange first 'Compatible?' if compatible then 'FW: revise and reassess' {
            succession '[compatible]' [0..1] first 'Compatible?' then 'FW: revise and reassess';
            bind '[compatible]' = transitionLink;
        }
        succession rejectedTransfer first 'Compatible?' if not compatible then 'Hold' {
            succession '[not compatible]' [0..1] first 'Compatible?' then 'Hold';
            bind '[not compatible]' = transitionLink;
        }
        first 'FW: revise and reassess' then 'Reviewer: review';
        first 'Reviewer: review' then 'Engineer: approve';
        first 'Engineer: approve' then 'Accepted?';
        succession acceptedChange first 'Accepted?' if accepted then 'FW: issue successor' {
            succession '[accepted]' [0..1] first 'Accepted?' then 'FW: issue successor';
            bind '[accepted]' = transitionLink;
        }
        succession declinedChange first 'Accepted?' if not accepted then 'Hold' {
            succession '[not accepted]' [0..1] first 'Accepted?' then 'Hold';
            bind '[not accepted]' = transitionLink;
        }
        first 'Hold' then 'FW: keep baseline';
        first 'FW: issue successor' then 'SC02 done';
        first 'FW: keep baseline' then 'SC02 done';
        first 'SC02 done' then done;
    }

    action def 'SC03 / UC03' {
        @MissionScenario;
        doc /* Primary scenario path: reconcile failed-gate observations, propose
            a parameter/model update and physical verification plan, receive
            engineering and safety reviews, check readiness and ask the facility
            for authorization. Invalid evidence, missing readiness conditions and
            withheld authorization are distinct failure/exception scenarios. */

        attribute usable : Boolean = 'FW: reconcile failure'.usable;
        attribute complete : Boolean = 'FW: propose repair and test'.complete;
        attribute endorsed : Boolean = 'Engineer: review'.endorsed;
        attribute cleared : Boolean = 'Safety: review'.cleared;
        attribute ready : Boolean = complete and endorsed and cleared;
        attribute granted : Boolean = 'Facility: authorize'.granted;
        merge 'SC03 start';
        action 'FW: reconcile failure' {
            out attribute usable : Boolean;
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Retain the failed-gate inputs, diagnostic variables, raw samples,
                invalid values and masks. Check data quality, channel/unit meaning,
                sample/receipt timing, synchronization and model applicability.
                usable is false when these conditions cannot support the proposed
                reconciliation. Preserve alternative fault explanations. */
        }
        decide 'Evidence usable?';
        action 'FW: retain unresolved' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Preserve the failed-gate context and affected unresolved claims.
                Request correction or separately identified evidence; do not
                calibrate from invalid data or claim a resolved failure. */
        }
        action 'FW: propose repair and test' {
            out attribute complete : Boolean;
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Propose identified model/parameter updates with prior/revised
                values, calibration residuals and affected analyses. Reassess the
                affected claims; intended-use validation requires separately
                identified evidence and remains distinct from calibration.
                Assemble the DUT/equipment identities and connections, stimulus
                sequence, capture channels, quantities, time base, observations
                and evidence procedure. Include operating limits, hazards, fault
                injection envelope, isolation, abort/recovery and safety-review
                responsibility. complete is false if required limits, interfaces
                or capture/procedure/safety content is missing. This proposal does
                not adopt a revision or operate the DUT or facility equipment. */
        }
        perform action 'Engineer: review' : ReviewRepair {
            @ExternalAction { performer = engineers meta SysML::PartUsage; fillColor = "#FFF0D6"; }
        }
        perform action 'Safety: review' : SafetyReview {
            @ExternalAction { performer = safetyAuthority meta SysML::PartUsage; fillColor = "#FFF0D6"; }
        }
        decide 'Ready?';
        action 'FW: block readiness' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Missing limits, equipment/DUT interfaces, capture/procedure
                content, engineering endorsement or responsible safety clearance
                block physical readiness.
                Keep the proposal and blockers; request corrective review rather
                than request execution. Framework readiness checking is not
                facility authorization. */
        }
        perform action 'Facility: authorize' : Authorize {
            @ExternalAction { performer = facility meta SysML::PartUsage; fillColor = "#FFF0D6"; }
        }
        decide 'Authorized?';
        action 'FW: retain authorization' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Retain the external authorization and its exact proposal,
                configuration, limits and review records. No physical operation
                or successful test is asserted by completion of this scenario. */
        }
        action 'FW: retain withholding' {
            @FrameworkAction { performer = framework meta SysML::PartUsage; fillColor = "#DCEEF8"; }
            doc /* Retain withheld/pending authorization and the facility's reasons.
                No authorization and no physical execution are presumed. */
        }
        merge 'SC03 done';

        first start then 'SC03 start';
        first 'SC03 start' then 'FW: reconcile failure';
        first 'FW: reconcile failure' then 'Evidence usable?';
        succession usableEvidence first 'Evidence usable?' if usable then 'FW: propose repair and test' {
            succession '[usable]' [0..1] first 'Evidence usable?' then 'FW: propose repair and test';
            bind '[usable]' = transitionLink;
        }
        succession unusableEvidence first 'Evidence usable?' if not usable then 'FW: retain unresolved' {
            succession '[not usable]' [0..1] first 'Evidence usable?' then 'FW: retain unresolved';
            bind '[not usable]' = transitionLink;
        }
        first 'FW: propose repair and test' then 'Engineer: review';
        first 'Engineer: review' then 'Safety: review';
        first 'Safety: review' then 'Ready?';
        succession readyProposal first 'Ready?' if ready then 'Facility: authorize' {
            succession '[ready]' [0..1] first 'Ready?' then 'Facility: authorize';
            bind '[ready]' = transitionLink;
        }
        succession blockedProposal first 'Ready?' if not ready then 'FW: block readiness' {
            succession '[not ready]' [0..1] first 'Ready?' then 'FW: block readiness';
            bind '[not ready]' = transitionLink;
        }
        first 'Facility: authorize' then 'Authorized?';
        succession authorizedWork first 'Authorized?' if granted then 'FW: retain authorization' {
            succession '[granted]' [0..1] first 'Authorized?' then 'FW: retain authorization';
            bind '[granted]' = transitionLink;
        }
        succession withheldWork first 'Authorized?' if not granted then 'FW: retain withholding' {
            succession '[not granted]' [0..1] first 'Authorized?' then 'FW: retain withholding';
            bind '[not granted]' = transitionLink;
        }
        first 'FW: retain unresolved' then 'SC03 done';
        first 'FW: block readiness' then 'SC03 done';
        first 'FW: retain authorization' then 'SC03 done';
        first 'FW: retain withholding' then 'SC03 done';
        first 'SC03 done' then done;
    }

    // Explicit behavioral responsibility allocations; hidden from the flow views.
    allocate 'SC01 / UC01'::'Engineer: tailor' to engineers;
    allocate 'SC01 / UC01'::'FW: bind options' to framework;
    allocate 'SC01 / UC01'::'FW: retain gaps' to framework;
    allocate 'SC01 / UC01'::'FW: coordinate analyses' to framework;
    allocate 'SC01 / UC01'::'FW: mark undetermined' to framework;
    allocate 'SC01 / UC01'::'Reviewer: review' to reviewers;
    allocate 'SC01 / UC01'::'Engineer: decide' to engineers;
    allocate 'SC01 / UC01'::'FW: retain package' to framework;
    allocate 'SC02 / UC02'::'Engineer: request' to engineers;
    allocate 'SC02 / UC02'::'FW: check transfer' to framework;
    allocate 'SC02 / UC02'::'FW: revise and reassess' to framework;
    allocate 'SC02 / UC02'::'Reviewer: review' to reviewers;
    allocate 'SC02 / UC02'::'Engineer: approve' to engineers;
    allocate 'SC02 / UC02'::'FW: issue successor' to framework;
    allocate 'SC02 / UC02'::'FW: keep baseline' to framework;
    allocate 'SC03 / UC03'::'FW: reconcile failure' to framework;
    allocate 'SC03 / UC03'::'FW: retain unresolved' to framework;
    allocate 'SC03 / UC03'::'FW: propose repair and test' to framework;
    allocate 'SC03 / UC03'::'Engineer: review' to engineers;
    allocate 'SC03 / UC03'::'Safety: review' to safetyAuthority;
    allocate 'SC03 / UC03'::'FW: block readiness' to framework;
    allocate 'SC03 / UC03'::'Facility: authorize' to facility;
    allocate 'SC03 / UC03'::'FW: retain authorization' to framework;
    allocate 'SC03 / UC03'::'FW: retain withholding' to framework;

    view sc01View : ActionFlowView {
        expose 'SC01 / UC01'::**;
        filter not (@SysML::AllocationUsage or @SysML::AttributeUsage);
        attribute depth = -1;
        attribute showInheritedRows = false;
        attribute showAnnotationRows = false;
    }
    view sc02View : ActionFlowView {
        expose 'SC02 / UC02'::**;
        filter not (@SysML::AllocationUsage or @SysML::AttributeUsage);
        attribute depth = -1;
        attribute showInheritedRows = false;
        attribute showAnnotationRows = false;
    }
    view sc03View : ActionFlowView {
        expose 'SC03 / UC03'::**;
        filter not (@SysML::AllocationUsage or @SysML::AttributeUsage);
        attribute depth = -1;
        attribute showInheritedRows = false;
        attribute showAnnotationRows = false;
    }
}
