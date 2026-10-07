// Framework boundary. Physical EPS designs are model inputs, not participants.
package FrameworkContext {
    private import FrameworkDomain::*;
    private import BoundaryViews::*;

    part def Users :> Engineers {
        port p : ~EngineeringUsePort;
        ref part systems : SystemsEngineer;
        ref part eps : EPSEngineer;
        ref part nonEps : NonEPSEngineer;
        ref part manager : ProjectManager;
        ref part stakeholders : MissionStakeholder [0..*];
    }
    part def Sources {
        port p : ~KnowledgePort;
        doc /* Literature, standards, component descriptions and supplied reference data. Source authority and supplier claims remain external. */
    }
    part def Engines :> ToBe::ModelSoftwareAnalysisEnvironment {
        port p : ~AnalysisPort;
        doc /* Declared electrical, thermal, applicable EMC, geometry, orbit/attitude, battery or RAM model execution tools. No vendor is selected. */
    }
    part def Software :> ToBe::HostSoftwareDevelopmentEnvironment {
        port p : ~HostSoftwarePort;
        doc /* External host execution toolchain coordinates declared coding, builds and SIL. Engineer approval remains required. This is no target-hardware participant. */
    }
    part def Reviewers {
        port p : ~TechnicalReviewPort;
        ref part independent : IndependentReviewer;
        ref part authority : TechnicalReviewAuthority;
        doc /* A reviewer supplies findings. The designated authority decides progression. Role occupants may overlap while responsibilities remain distinct. */
    }

    part def Context {
        ref part framework : ToBe::FutureFramework;
        part 'Engineers and stakeholders' : Users;
        alias engineers for 'Engineers and stakeholders';
        part 'Knowledge and data sources' : Sources;
        alias sources for 'Knowledge and data sources';
        part 'Model analysis tools' : Engines;
        alias tools for 'Model analysis tools';
        alias engines for 'Model analysis tools';
        part 'Host execution toolchain' : Software;
        alias software for 'Host execution toolchain';
        part 'Reviewers and authority' : Reviewers;
        alias reviewers for 'Reviewers and authority';

        interface IF01 : EngineeringUseInterface connect engineers.p to framework.p01 {
            flow engineeringInputs of EngineeringSubmission from client.engineeringSubmission to framework.engineeringSubmission;
            flow engineeringOutputs of EngineeringResponse from framework.engineeringResponse to client.engineeringResponse;
        }
        interface IF02 : KnowledgeInterface connect sources.p to framework.p02 {
            flow sourceData of SourceSubmission from client.sourceSubmission to framework.sourceSubmission;
            flow sourceRequest of SourceQuery from framework.sourceQuery to client.sourceQuery;
        }
        interface IF03 : AnalysisInterface connect tools.p to framework.p03 {
            flow analysisRequest of AnalysisRequest from framework.analysisRequest to client.analysisRequest;
            flow analysisPlan of AnalysisPlan from framework.analysisPlan to client.analysisPlan;
            flow analysisStatus of AnalysisResponse from client.analysisResponse to framework.analysisResponse;
            flow analysisResult of AnalysisResult from client.analysisResult to framework.analysisResult;
        }
        interface IF04 : HostSoftwareInterface connect software.p to framework.p04 {
            flow codingStatus of CodingResponse from client.codingResponse to framework.codingResponse;
            flow codingRequest of CodingRequest from framework.codingRequest to client.codingRequest;
            flow interfaceSpecification of EPSInterfaceSpecification from framework.interfaceSpecification to client.interfaceSpecification;
            flow softwareProduct of HostSoftwareProduct from client.softwareProduct to framework.softwareProduct;
            flow softwareResult of SoftwareRunResult from client.softwareResult to framework.softwareResult;
        }
        interface IF06 : TechnicalReviewInterface connect reviewers.p to framework.p06 {
            flow reviewFindingsDecisions of ReviewSubmission from client.reviewSubmission to framework.reviewSubmission;
            flow reviewPackage of ReviewResponse from framework.reviewResponse to client.reviewResponse;
        }

        // Report summaries use the same directed port features and payload types.
        flow 'IF-01 inputs' of EngineeringSubmission from engineers.p to framework.p01;
        flow 'Guidance and products' of EngineeringResponse from framework.p01 to engineers.p;
        flow 'IF-02 sources' of SourceSubmission from sources.p to framework.p02;
        flow 'Source queries' of SourceQuery from framework.p02 to sources.p;
        flow 'IF-03 requests' of AnalysisRequest from framework.p03 to tools.p;
        flow 'Analysis results' of AnalysisResult from tools.p to framework.p03;
        flow 'IF-04 coding and SIL' of CodingRequest from framework.p04 to software.p;
        flow 'Builds and results' of SoftwareRunResult from software.p to framework.p04;
        flow 'IF-06 packages' of ReviewResponse from framework.p06 to reviewers.p;
        flow 'Findings and decisions' of ReviewSubmission from reviewers.p to framework.p06;
        doc /* Five active versioned interfaces retain subject/context revisions and raw submissions. Receiving checks enforce identity, units, time/mode meaning, scope, source provenance and authorization before controlled registration. Incompatible information remains rejected or unresolved. IF-05 has no participant, port or flow in this context. */
    }
    part context : Context;
    #sourceTrace dependency enterpriseBoundary from context to ToBe::domain::enterprise;
}
