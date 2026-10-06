// Native views derived from the SysML v2 report model.
package ReportViews {
private import Views::*;
view contextView {
expose FrameworkContext::Context::*;
filter not @SysML::InterfaceUsage;
render asInterconnectionDiagram;
}
view logicalView {
expose FrameworkLogical::LogicalFramework::*;
filter @SysML::PartUsage;
render asTreeDiagram;
}

view selectedPhysicalView {
expose CandidateVS::Deployment::*;
render asInterconnectionDiagram;
}

}
