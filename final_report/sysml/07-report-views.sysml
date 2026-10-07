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
        expose LogicalFramework::L07;
        expose LogicalFramework::L08;
        filter not @detailedExchange and not @BindingConnectorAsUsage and
               not (@ItemUsage and not @PartUsage);
        render asInterconnectionDiagram;
    }
    // Computing roles and their existing typed connections are shown separately
    // to keep the deployment figure readable in portrait orientation.
    private import CandidateCDT::*;
    view selectedPhysicalView {
        expose CandidateCDT::Configuration::N1;
        expose CandidateCDT::Configuration::N2;
        expose CandidateCDT::Configuration::N3;
        filter @PartUsage and not @PortUsage and not @ConnectionUsage;
        render asInterconnectionDiagram;
    }
    view deploymentInterfacesView {
        expose CandidateCDT::Configuration::adviceLink;
        expose CandidateCDT::Configuration::releasedData;
        expose CandidateCDT::Configuration::sourceAdvice;
        expose CandidateCDT::Configuration::modelLink;
        expose CandidateCDT::Configuration::codeLink;
        filter not @BindingConnectorAsUsage and
               not (@ItemUsage and not @PartUsage);
        render asInterconnectionDiagram;
    }
}
