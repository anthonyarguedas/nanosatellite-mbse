// Controlled report model. Trace records are published in final_report/traceability/.
package ReportViews {
private import Views::*;
view contextView {
expose FrameworkContext::Context::*;
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
