// Publication views select existing model elements and relationships.
package ReportViews {
    private import Views::*;
    view contextView {
        expose FrameworkContext::Context::*;
        filter not @SysML::FlowUsage;
        render asInterconnectionDiagram;
    }
    // Logical component view only. Exposures select the current native parts
    // and important exchanges, with shared revision services explained in prose.
    private import FrameworkLogical::*;
    private import SysML::*;
    view logicalView {
        expose LogicalFramework::L01;
        expose LogicalFramework::L02;
        expose LogicalFramework::L03;
        expose LogicalFramework::L04;
        expose LogicalFramework::L05;
        expose LogicalFramework::L06;
        filter not @detailedExchange and not @BindingConnectorAsUsage and
               not (@ItemUsage and not @PartUsage);
        render asInterconnectionDiagram;
    }
    // Neutral views of proposed alternatives. No deployment or candidate is selected.
    view physicalCandidatesView {
        expose CandidateCOM::candidate;
        expose CandidateVS::candidate;
        expose CandidateNS::candidate;
        expose CandidateGY::candidate;
        expose CandidateCDT::candidate;
        filter @PartUsage and not @PortUsage and not @ConnectionUsage;
        render asInterconnectionDiagram;
    }
    view cometPhysicalView {
        expose CandidateCOM::Configuration::L01;
        expose CandidateCOM::Configuration::L02;
        expose CandidateCOM::Configuration::L03;
        expose CandidateCOM::Configuration::L04;
        expose CandidateCOM::Configuration::L05;
        expose CandidateCOM::Configuration::L06;
        filter @PartUsage and not @PortUsage and not @ConnectionUsage;
        render asInterconnectionDiagram;
    }
    view valispacePhysicalView {
        expose CandidateVS::Configuration::L01;
        expose CandidateVS::Configuration::L02;
        expose CandidateVS::Configuration::L03;
        expose CandidateVS::Configuration::L04;
        expose CandidateVS::Configuration::L05;
        expose CandidateVS::Configuration::L06;
        filter @PartUsage and not @PortUsage and not @ConnectionUsage;
        render asInterconnectionDiagram;
    }
    view nanospacePhysicalView {
        expose CandidateNS::Configuration::L01;
        expose CandidateNS::Configuration::L02;
        expose CandidateNS::Configuration::L03;
        expose CandidateNS::Configuration::L04;
        expose CandidateNS::Configuration::L05;
        expose CandidateNS::Configuration::L06;
        filter @PartUsage and not @PortUsage and not @ConnectionUsage;
        render asInterconnectionDiagram;
    }
    view gitYAMLPhysicalView {
        expose CandidateGY::Configuration::L01;
        expose CandidateGY::Configuration::L02;
        expose CandidateGY::Configuration::L03;
        expose CandidateGY::Configuration::L04;
        expose CandidateGY::Configuration::L05;
        expose CandidateGY::Configuration::L06;
        filter @PartUsage and not @PortUsage and not @ConnectionUsage;
        render asInterconnectionDiagram;
    }
    view customPhysicalView {
        expose CandidateCDT::Configuration::L01;
        expose CandidateCDT::Configuration::L02;
        expose CandidateCDT::Configuration::L03;
        expose CandidateCDT::Configuration::L04;
        expose CandidateCDT::Configuration::L05;
        expose CandidateCDT::Configuration::L06;
        filter @PartUsage and not @PortUsage and not @ConnectionUsage;
        render asInterconnectionDiagram;
    }
    view physicalIntegrationView {
        expose CandidateCOM::Configuration::modelLink;
        expose CandidateCOM::Configuration::codeLink;
        expose CandidateVS::Configuration::modelLink;
        expose CandidateVS::Configuration::codeLink;
        expose CandidateNS::Configuration::modelLink;
        expose CandidateNS::Configuration::codeLink;
        expose CandidateGY::Configuration::modelLink;
        expose CandidateGY::Configuration::codeLink;
        expose CandidateCDT::Configuration::modelLink;
        expose CandidateCDT::Configuration::codeLink;
        filter not @BindingConnectorAsUsage and
               not (@ItemUsage and not @PartUsage);
        render asInterconnectionDiagram;
    }
    view customNativeEnrichmentView {
        expose CandidateCDT::C01::jev;
        expose CandidateCDT::C02::nativeModel;
        expose CandidateCDT::C02::cots;
        expose CandidateCDT::C03::nativeResources;
        filter @PartUsage and not @PortUsage and not @ConnectionUsage;
        render asInterconnectionDiagram;
    }
}
