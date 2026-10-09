// Approved stakeholder concerns with stable identifiers and explicit causal links.
// SourceRecord locators retain the original concern baseline provenance.
package FrameworkConcerns {
    private import FrameworkDomain::*;
    metadata def CurrentDisposition {
        attribute scopeStatus : ScalarValues::String;
        attribute disposition : ScalarValues::String;
        attribute moeIdentifiers : ScalarValues::String;
    }
    concern <'C-PM-01'> C_PM_01 { subject enterprise : EngineeringEnterprise; stakeholder role : ProjectManager; doc /* the high effort and cost to maintain verifiable requirements; */ }
    @SourceRecord about C_PM_01 { identifier = "C-PM-01"; sourceText = "the high effort and cost to maintain verifiable requirements;"; sourceLocator = "final_report/apendice.tex#C-PM-01 (current concern anchor, line 25)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_PM_01 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Correct requirement work, learning effort and access costs for software and data."; moeIdentifiers = "MOE-01,MOE-04,MOE-05"; }
    concern <'C-PM-01.1'> C_PM_01_1 { subject enterprise : EngineeringEnterprise; stakeholder role : ProjectManager; doc /* the high effort to learn to write verifiable requirements; */ }
    @SourceRecord about C_PM_01_1 { identifier = "C-PM-01.1"; sourceText = "the high effort to learn to write verifiable requirements;"; sourceLocator = "final_report/apendice.tex#C-PM-01.1 (current concern anchor, line 28)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_PM_01_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Learning to produce correct, verifiable requirements."; moeIdentifiers = "MOE-01,MOE-04"; }
    #sourceTrace dependency causal_C_PM_01_1 from C_PM_01_1 to C_PM_01;
    concern <'C-PM-01.2'> C_PM_01_2 { subject enterprise : EngineeringEnterprise; stakeholder role : ProjectManager; doc /* the high cost of requirements management tools used in the industry as a barrier to adoption, and; */ }
    @SourceRecord about C_PM_01_2 { identifier = "C-PM-01.2"; sourceText = "the high cost of requirements management tools used in the industry as a barrier to adoption, and;"; sourceLocator = "final_report/apendice.tex#C-PM-01.2 (current concern anchor, line 30)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_PM_01_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Tool prices and access restrictions affect affordability. Person-hours measure effort separately."; moeIdentifiers = "MOE-05"; }
    #sourceTrace dependency causal_C_PM_01_2 from C_PM_01_2 to C_PM_01;
    concern <'C-PM-03'> C_PM_03 { subject enterprise : EngineeringEnterprise; stakeholder role : ProjectManager; doc /* the high cost and effort of redesign after hardware fabrication \citep[Secs.~4--5]{handpicked-0003}; */ }
    @SourceRecord about C_PM_03 { identifier = "C-PM-03"; sourceText = "the high cost and effort of redesign after hardware fabrication \\citep[Secs.~4--5]{handpicked-0003};"; sourceLocator = "final_report/apendice.tex#C-PM-03 (current concern anchor, line 33)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0003"; }
    @CurrentDisposition about C_PM_03 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Earlier modeled issue detection covers supported disciplines. Avoided fabrication cost and prototype replacement are external outcomes."; moeIdentifiers = "MOE-02,MOE-06"; }
    concern <'C-PM-03.1'> C_PM_03_1 { subject enterprise : EngineeringEnterprise; stakeholder role : ProjectManager; doc /* the late detection of thermal, electromagnetic compatibility, and power design issues \citep[Secs.~1 and~4]{handpicked-0003}; */ }
    @SourceRecord about C_PM_03_1 { identifier = "C-PM-03.1"; sourceText = "the late detection of thermal, electromagnetic compatibility, and power design issues \\citep[Secs.~1 and~4]{handpicked-0003};"; sourceLocator = "final_report/apendice.tex#C-PM-03.1 (current concern anchor, line 36)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0003"; }
    @CurrentDisposition about C_PM_03_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Earlier modeled issue detection covers supported disciplines. Avoided fabrication cost and prototype replacement are external outcomes."; moeIdentifiers = "MOE-02,MOE-06"; }
    #sourceTrace dependency causal_C_PM_03_1 from C_PM_03_1 to C_PM_03;
    concern <'C-PM-03.1.1'> C_PM_03_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : ProjectManager; doc /* the dependence of early verification on the availability of physical prototypes \citep[p.~3]{handpicked-0001}; */ }
    @SourceRecord about C_PM_03_1_1 { identifier = "C-PM-03.1.1"; sourceText = "the dependence of early verification on the availability of physical prototypes \\citep[p.~3]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-PM-03.1.1 (current concern anchor, line 39)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_PM_03_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Earlier modeled issue detection covers supported disciplines. Avoided fabrication cost and prototype replacement are external outcomes."; moeIdentifiers = "MOE-02,MOE-06"; }
    #sourceTrace dependency causal_C_PM_03_1_1 from C_PM_03_1_1 to C_PM_03_1;
    concern <'C-PM-04'> C_PM_04 { subject enterprise : EngineeringEnterprise; stakeholder role : ProjectManager; doc /* the high cost of maintaining physical EPS replicas for mission troubleshooting \citep[Sec.~1]{review-0573}; */ }
    @SourceRecord about C_PM_04 { identifier = "C-PM-04"; sourceText = "the high cost of maintaining physical EPS replicas for mission troubleshooting \\citep[Sec.~1]{review-0573};"; sourceLocator = "final_report/apendice.tex#C-PM-04 (current concern anchor, line 43)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0573"; }
    @CurrentDisposition about C_PM_04 { scopeStatus = "current as-is context, physical/facility work excluded"; disposition = "Replica maintenance cost remains external context. Operational troubleshooting and replica replacement are excluded."; moeIdentifiers = "MOE-06"; }
    concern <'C-PM-05'> C_PM_05 { subject enterprise : EngineeringEnterprise; stakeholder role : ProjectManager; doc /* the high effort and cost to adapt engineering tools to the team's mission scale and resources \citep[Sec.~5.1]{buruso2026modelbased}; */ }
    @SourceRecord about C_PM_05 { identifier = "C-PM-05"; sourceText = "the high effort and cost to adapt engineering tools to the team's mission scale and resources \\citep[Sec.~5.1]{buruso2026modelbased};"; sourceLocator = "final_report/apendice.tex#C-PM-05 (current concern anchor, line 45)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "buruso2026modelbased"; }
    @CurrentDisposition about C_PM_05 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Correct mission adaptation, learning and declared costs of software, data and host computing."; moeIdentifiers = "MOE-01,MOE-04,MOE-05"; }
    concern <'C-PM-05.1'> C_PM_05_1 { subject enterprise : EngineeringEnterprise; stakeholder role : ProjectManager; doc /* C-SE-2 */ }
    @SourceRecord about C_PM_05_1 { identifier = "C-PM-05.1"; sourceText = "C-SE-2"; sourceLocator = "final_report/apendice.tex#C-PM-05.1 (current concern anchor, line 48)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_PM_05_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Consistency work during adoption affects effort, early information defects and evidence reconstruction. This occurrence aliases C-SE-07 and shares its observations."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-04,MOE-06"; }
    #sourceTrace dependency causal_C_PM_05_1 from C_PM_05_1 to C_PM_05;
    #aliasReference dependency alias_C_PM_05_1 from C_PM_05_1 to C_SE_07;
    concern <'C-SE-01'> C_SE_01 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to maintain traceability from requirements to design decisions; */ }
    @SourceRecord about C_SE_01 { identifier = "C-SE-01"; sourceText = "the high effort to maintain traceability from requirements to design decisions;"; sourceLocator = "final_report/apendice.tex#C-SE-01 (current concern anchor, line 53)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_01 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Trace maintenance and tool learning support correct tasks and independent reconstruction."; moeIdentifiers = "MOE-01,MOE-03,MOE-04"; }
    concern <'C-SE-01.1'> C_SE_01_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* (C-SE-1-1) the high effort to learn how to use tools for requirements to design traceability; */ }
    @SourceRecord about C_SE_01_1 { identifier = "C-SE-01.1"; sourceText = "(C-SE-1-1) the high effort to learn how to use tools for requirements to design traceability;"; sourceLocator = "final_report/apendice.tex#C-SE-01.1 (current concern anchor, line 56)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_01_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Trace maintenance and tool learning support correct tasks and independent reconstruction."; moeIdentifiers = "MOE-01,MOE-03,MOE-04"; }
    #sourceTrace dependency causal_C_SE_01_1 from C_SE_01_1 to C_SE_01;
    concern <'C-SE-01.1.1'> C_SE_01_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to learn how to use MBSE tools; */ }
    @SourceRecord about C_SE_01_1_1 { identifier = "C-SE-01.1.1"; sourceText = "the high effort to learn how to use MBSE tools;"; sourceLocator = "final_report/apendice.tex#C-SE-01.1.1 (current concern anchor, line 59)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_01_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Trace maintenance and tool learning support correct tasks and independent reconstruction."; moeIdentifiers = "MOE-01,MOE-03,MOE-04"; }
    #sourceTrace dependency causal_C_SE_01_1_1 from C_SE_01_1_1 to C_SE_01_1;
    concern <'C-SE-02'> C_SE_02 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to communicate effectively requirement verification and validation evidence to stakeholders; */ }
    @SourceRecord about C_SE_02 { identifier = "C-SE-02"; sourceText = "the high effort to communicate effectively requirement verification and validation evidence to stakeholders;"; sourceLocator = "final_report/apendice.tex#C-SE-02 (current concern anchor, line 63)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_02 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Communication effort affects evidence and trace presentation. Reviewers assess interpretation and reconstruction."; moeIdentifiers = "MOE-01,MOE-03"; }
    concern <'C-SE-02.1'> C_SE_02_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to communicate effectively the requirements to design to verification evidence traces to stakeholders; */ }
    @SourceRecord about C_SE_02_1 { identifier = "C-SE-02.1"; sourceText = "the high effort to communicate effectively the requirements to design to verification evidence traces to stakeholders;"; sourceLocator = "final_report/apendice.tex#C-SE-02.1 (current concern anchor, line 66)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_02_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Communication effort affects evidence and trace presentation. Reviewers assess interpretation and reconstruction."; moeIdentifiers = "MOE-01,MOE-03"; }
    #sourceTrace dependency causal_C_SE_02_1 from C_SE_02_1 to C_SE_02;
    concern <'C-SE-03'> C_SE_03 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to maintain EPS requirements up to date when the designs of other subsystems change; */ }
    @SourceRecord about C_SE_03 { identifier = "C-SE-03"; sourceText = "the high effort to maintain EPS requirements up to date when the designs of other subsystems change;"; sourceLocator = "final_report/apendice.tex#C-SE-03 (current concern anchor, line 69)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Controlled subsystem changes affect reassessment effort, early incompatibilities and evidence currency."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    concern <'C-SE-03.1'> C_SE_03_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the amount of other subsystem design changes; */ }
    @SourceRecord about C_SE_03_1 { identifier = "C-SE-03.1"; sourceText = "the amount of other subsystem design changes;"; sourceLocator = "final_report/apendice.tex#C-SE-03.1 (current concern anchor, line 72)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Controlled subsystem changes affect reassessment effort, early incompatibilities and evidence currency."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_1 from C_SE_03_1 to C_SE_03;
    concern <'C-SE-03.1.1'> C_SE_03_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the amount of verification gates failed by other subsystem designs; */ }
    @SourceRecord about C_SE_03_1_1 { identifier = "C-SE-03.1.1"; sourceText = "the amount of verification gates failed by other subsystem designs;"; sourceLocator = "final_report/apendice.tex#C-SE-03.1.1 (current concern anchor, line 75)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Controlled subsystem changes affect reassessment effort, early incompatibilities and evidence currency."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_1_1 from C_SE_03_1_1 to C_SE_03_1;
    concern <'C-SE-03.2'> C_SE_03_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* C-EPS-1 */ }
    @SourceRecord about C_SE_03_2 { identifier = "C-SE-03.2"; sourceText = "C-EPS-1"; sourceLocator = "final_report/apendice.tex#C-SE-03.2 (current concern anchor, line 78)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "These aliases of C-EPS-01 share its bounded contribution from repeated modeled verification. Physical campaigns remain excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_SE_03_2 from C_SE_03_2 to C_SE_03;
    #aliasReference dependency alias_C_SE_03_2 from C_SE_03_2 to C_EPS_01;
    concern <'C-SE-03.3'> C_SE_03_3 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to define pass/fail criteria for EPS requirements; */ }
    @SourceRecord about C_SE_03_3 { identifier = "C-SE-03.3"; sourceText = "the high effort to define pass/fail criteria for EPS requirements;"; sourceLocator = "final_report/apendice.tex#C-SE-03.3 (current concern anchor, line 80)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Criteria, quantities, behavioral representations and sourced budgeting methods affect effort and correct conclusions."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_3 from C_SE_03_3 to C_SE_03;
    concern <'C-SE-03.3.1'> C_SE_03_3_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to translate the behavior and thermal and power characteristics of other subsystems into EPS requirement parameters; */ }
    @SourceRecord about C_SE_03_3_1 { identifier = "C-SE-03.3.1"; sourceText = "the high effort to translate the behavior and thermal and power characteristics of other subsystems into EPS requirement parameters;"; sourceLocator = "final_report/apendice.tex#C-SE-03.3.1 (current concern anchor, line 83)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_3_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Criteria, quantities, behavioral representations and sourced budgeting methods affect effort and correct conclusions."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_3_1 from C_SE_03_3_1 to C_SE_03_3;
    concern <'C-SE-03.3.1.1'> C_SE_03_3_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to determine the thermal and power characteristics of subsystem components; */ }
    @SourceRecord about C_SE_03_3_1_1 { identifier = "C-SE-03.3.1.1"; sourceText = "the high effort to determine the thermal and power characteristics of subsystem components;"; sourceLocator = "final_report/apendice.tex#C-SE-03.3.1.1 (current concern anchor, line 86)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_3_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Criteria, quantities, behavioral representations and sourced budgeting methods affect effort and correct conclusions."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_3_1_1 from C_SE_03_3_1_1 to C_SE_03_3_1;
    concern <'C-SE-03.3.1.2'> C_SE_03_3_1_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the large amount of possible representations of component behavior relevant to power consumption like duty cycles and operation modes; */ }
    @SourceRecord about C_SE_03_3_1_2 { identifier = "C-SE-03.3.1.2"; sourceText = "the large amount of possible representations of component behavior relevant to power consumption like duty cycles and operation modes;"; sourceLocator = "final_report/apendice.tex#C-SE-03.3.1.2 (current concern anchor, line 88)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_3_1_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Criteria, quantities, behavioral representations and sourced budgeting methods affect effort and correct conclusions."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_3_1_2 from C_SE_03_3_1_2 to C_SE_03_3_1;
    concern <'C-SE-03.3.1.3'> C_SE_03_3_1_3 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the large amount of possible methods to convert behavior and thermal and power characteristics into EPS requirement parameters, including power budgeting; */ }
    @SourceRecord about C_SE_03_3_1_3 { identifier = "C-SE-03.3.1.3"; sourceText = "the large amount of possible methods to convert behavior and thermal and power characteristics into EPS requirement parameters, including power budgeting;"; sourceLocator = "final_report/apendice.tex#C-SE-03.3.1.3 (current concern anchor, line 90)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_3_1_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Criteria, quantities, behavioral representations and sourced budgeting methods affect effort and correct conclusions."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_3_1_3 from C_SE_03_3_1_3 to C_SE_03_3_1;
    concern <'C-SE-03.3.1.3.1'> C_SE_03_3_1_3_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the large amount of applicable standards; */ }
    @SourceRecord about C_SE_03_3_1_3_1 { identifier = "C-SE-03.3.1.3.1"; sourceText = "the large amount of applicable standards;"; sourceLocator = "final_report/apendice.tex#C-SE-03.3.1.3.1 (current concern anchor, line 93)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_3_1_3_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Criteria, quantities, behavioral representations and sourced budgeting methods affect effort and correct conclusions."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_3_1_3_1 from C_SE_03_3_1_3_1 to C_SE_03_3_1_3;
    concern <'C-SE-03.3.1.3.2'> C_SE_03_3_1_3_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the large amount of methods published in the academic literature; */ }
    @SourceRecord about C_SE_03_3_1_3_2 { identifier = "C-SE-03.3.1.3.2"; sourceText = "the large amount of methods published in the academic literature;"; sourceLocator = "final_report/apendice.tex#C-SE-03.3.1.3.2 (current concern anchor, line 95)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_3_1_3_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Criteria, quantities, behavioral representations and sourced budgeting methods affect effort and correct conclusions."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_3_1_3_2 from C_SE_03_3_1_3_2 to C_SE_03_3_1_3;
    concern <'C-SE-03.4'> C_SE_03_4 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to define verification activities for EPS requirements; */ }
    @SourceRecord about C_SE_03_4 { identifier = "C-SE-03.4"; sourceText = "the high effort to define verification activities for EPS requirements;"; sourceLocator = "final_report/apendice.tex#C-SE-03.4 (current concern anchor, line 100)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_4 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Selecting applicable verification methods affects effort, early misses and evidence coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_4 from C_SE_03_4 to C_SE_03;
    concern <'C-SE-03.4.1'> C_SE_03_4_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the large amount of applicable standards; */ }
    @SourceRecord about C_SE_03_4_1 { identifier = "C-SE-03.4.1"; sourceText = "the large amount of applicable standards;"; sourceLocator = "final_report/apendice.tex#C-SE-03.4.1 (current concern anchor, line 103)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_4_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Selecting applicable verification methods affects effort, early misses and evidence coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_4_1 from C_SE_03_4_1 to C_SE_03_4;
    concern <'C-SE-03.4.2'> C_SE_03_4_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the large amount of potential verification activities published in the academic literature; */ }
    @SourceRecord about C_SE_03_4_2 { identifier = "C-SE-03.4.2"; sourceText = "the large amount of potential verification activities published in the academic literature;"; sourceLocator = "final_report/apendice.tex#C-SE-03.4.2 (current concern anchor, line 105)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_03_4_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Selecting applicable verification methods affects effort, early misses and evidence coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_03_4_2 from C_SE_03_4_2 to C_SE_03_4;
    concern <'C-SE-04'> C_SE_04 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to maintain power requirements for non-EPS subsystems up to date when the EPS design changes; */ }
    @SourceRecord about C_SE_04 { identifier = "C-SE-04"; sourceText = "the high effort to maintain power requirements for non-EPS subsystems up to date when the EPS design changes;"; sourceLocator = "final_report/apendice.tex#C-SE-04 (current concern anchor, line 109)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_04 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Reciprocal EPS changes and failed gates affect reassessment effort, incompatibilities and evidence currency."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    concern <'C-SE-04.1'> C_SE_04_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the amount of EPS design changes; */ }
    @SourceRecord about C_SE_04_1 { identifier = "C-SE-04.1"; sourceText = "the amount of EPS design changes;"; sourceLocator = "final_report/apendice.tex#C-SE-04.1 (current concern anchor, line 112)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_04_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Reciprocal EPS changes and failed gates affect reassessment effort, incompatibilities and evidence currency."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_04_1 from C_SE_04_1 to C_SE_04;
    concern <'C-SE-04.1.1'> C_SE_04_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the amount of verification gates failed by the EPS designs; */ }
    @SourceRecord about C_SE_04_1_1 { identifier = "C-SE-04.1.1"; sourceText = "the amount of verification gates failed by the EPS designs;"; sourceLocator = "final_report/apendice.tex#C-SE-04.1.1 (current concern anchor, line 115)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_04_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Reciprocal EPS changes and failed gates affect reassessment effort, incompatibilities and evidence currency."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_SE_04_1_1 from C_SE_04_1_1 to C_SE_04_1;
    concern <'C-SE-05'> C_SE_05 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the low reliability, availability, and maintainability (RAM) of CubeSat designs; */ }
    @SourceRecord about C_SE_05 { identifier = "C-SE-05"; sourceText = "the low reliability, availability, and maintainability (RAM) of CubeSat designs;"; sourceLocator = "final_report/apendice.tex#C-SE-05 (current concern anchor, line 119)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_05 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Applicable RAM omissions and evidence coverage inform assessment. Actual spacecraft RAM remains an external outcome."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    concern <'C-SE-05.1'> C_SE_05_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the insufficient coverage of RAM variables in CubeSat and subsystem requirements; */ }
    @SourceRecord about C_SE_05_1 { identifier = "C-SE-05.1"; sourceText = "the insufficient coverage of RAM variables in CubeSat and subsystem requirements;"; sourceLocator = "final_report/apendice.tex#C-SE-05.1 (current concern anchor, line 122)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_05_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Applicable RAM omissions and evidence coverage inform assessment. Actual spacecraft RAM remains an external outcome."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_05_1 from C_SE_05_1 to C_SE_05;
    concern <'C-SE-05.2'> C_SE_05_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to verify requirements related to RAM variables; */ }
    @SourceRecord about C_SE_05_2 { identifier = "C-SE-05.2"; sourceText = "the high effort to verify requirements related to RAM variables;"; sourceLocator = "final_report/apendice.tex#C-SE-05.2 (current concern anchor, line 124)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_05_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "RAM models and analyses affect effort, issue detection and supported evidence. Operational RAM demonstration remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_05_2 from C_SE_05_2 to C_SE_05;
    concern <'C-SE-05.2.1'> C_SE_05_2_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high cost and effort to obtain evidence to verify requirements related to RAM variables; */ }
    @SourceRecord about C_SE_05_2_1 { identifier = "C-SE-05.2.1"; sourceText = "the high cost and effort to obtain evidence to verify requirements related to RAM variables;"; sourceLocator = "final_report/apendice.tex#C-SE-05.2.1 (current concern anchor, line 127)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_05_2_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Existing data and applicable analyses affect effort, cost and RAM evidence coverage. Physical campaigns remain external evidence gaps."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_SE_05_2_1 from C_SE_05_2_1 to C_SE_05_2;
    concern <'C-SE-05.2.1.1'> C_SE_05_2_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the proportion of requirements related to RAM variables that are verified via demonstration or testing instead of inspection or analysis; */ }
    @SourceRecord about C_SE_05_2_1_1 { identifier = "C-SE-05.2.1.1"; sourceText = "the proportion of requirements related to RAM variables that are verified via demonstration or testing instead of inspection or analysis;"; sourceLocator = "final_report/apendice.tex#C-SE-05.2.1.1 (current concern anchor, line 130)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_05_2_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Existing data and applicable analyses affect effort, cost and RAM evidence coverage. Physical campaigns remain external evidence gaps."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_SE_05_2_1_1 from C_SE_05_2_1_1 to C_SE_05_2_1;
    concern <'C-SE-05.2.1.2'> C_SE_05_2_1_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to perform RAM analyses on CubeSat and subsystem designs; */ }
    @SourceRecord about C_SE_05_2_1_2 { identifier = "C-SE-05.2.1.2"; sourceText = "the high effort to perform RAM analyses on CubeSat and subsystem designs;"; sourceLocator = "final_report/apendice.tex#C-SE-05.2.1.2 (current concern anchor, line 132)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_05_2_1_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "RAM models and analyses affect effort, issue detection and supported evidence. Operational RAM demonstration remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_05_2_1_2 from C_SE_05_2_1_2 to C_SE_05_2_1;
    concern <'C-SE-05.2.1.2.1'> C_SE_05_2_1_2_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to generate RAM analysis models of the CubeSat and subsystem designs; */ }
    @SourceRecord about C_SE_05_2_1_2_1 { identifier = "C-SE-05.2.1.2.1"; sourceText = "the high effort to generate RAM analysis models of the CubeSat and subsystem designs;"; sourceLocator = "final_report/apendice.tex#C-SE-05.2.1.2.1 (current concern anchor, line 135)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_05_2_1_2_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "RAM models and analyses affect effort, issue detection and supported evidence. Operational RAM demonstration remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_05_2_1_2_1 from C_SE_05_2_1_2_1 to C_SE_05_2_1_2;
    concern <'C-SE-06'> C_SE_06 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the low capability to detect temporary mission energy shortages before hardware integration \citep[Sec.~VI]{review-1231}; */ }
    @SourceRecord about C_SE_06 { identifier = "C-SE-06"; sourceText = "the low capability to detect temporary mission energy shortages before hardware integration \\citep[Sec.~VI]{review-1231};"; sourceLocator = "final_report/apendice.tex#C-SE-06 (current concern anchor, line 141)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-1231"; }
    @CurrentDisposition about C_SE_06 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Transient shortages and mode interactions affect early detection and coverage within declared model fidelity. Hardware integration evidence remains external."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    concern <'C-SE-06.1'> C_SE_06_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the use of average power budgets that omit interactions between attitude, solar generation, and changing load demand \citep[Secs.~I and~VI]{review-1231}; */ }
    @SourceRecord about C_SE_06_1 { identifier = "C-SE-06.1"; sourceText = "the use of average power budgets that omit interactions between attitude, solar generation, and changing load demand \\citep[Secs.~I and~VI]{review-1231};"; sourceLocator = "final_report/apendice.tex#C-SE-06.1 (current concern anchor, line 144)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-1231"; }
    @CurrentDisposition about C_SE_06_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Transient shortages and mode interactions affect early detection and coverage within declared model fidelity. Hardware integration evidence remains external."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_06_1 from C_SE_06_1 to C_SE_06;
    concern <'C-SE-06.2'> C_SE_06_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the insufficient coverage of subsystem interactions and operating mode transitions in verification \citep[Sec.~8.1.7]{handpicked-0003}\citep[Sec.~3.1]{review-0573}; */ }
    @SourceRecord about C_SE_06_2 { identifier = "C-SE-06.2"; sourceText = "the insufficient coverage of subsystem interactions and operating mode transitions in verification \\citep[Sec.~8.1.7]{handpicked-0003}\\citep[Sec.~3.1]{review-0573};"; sourceLocator = "final_report/apendice.tex#C-SE-06.2 (current concern anchor, line 146)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0003,review-0573"; }
    @CurrentDisposition about C_SE_06_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Transient shortages and mode interactions affect early detection and coverage within declared model fidelity. Hardware integration evidence remains external."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_06_2 from C_SE_06_2 to C_SE_06;
    concern <'C-SE-07'> C_SE_07 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* (C-SE-2) the high effort to maintain consistent information across requirements, simulation models, hardware, and verification evidence \citep[Secs.~4.4 and~5.1]{buruso2026modelbased}; */ }
    @SourceRecord about C_SE_07 { identifier = "C-SE-07"; sourceText = "(C-SE-2) the high effort to maintain consistent information across requirements, simulation models, hardware, and verification evidence \\citep[Secs.~4.4 and~5.1]{buruso2026modelbased};"; sourceLocator = "final_report/apendice.tex#C-SE-07 (current concern anchor, line 149)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "buruso2026modelbased"; }
    @CurrentDisposition about C_SE_07 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Data conversion, version control and reassessment affect effort, early semantic defects and evidence reconstruction. Measurements are supplied data. Hardware acquisition is excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    concern <'C-SE-07.1'> C_SE_07_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to reconcile incompatible modeling and simulation data formats \citep[Sec.~5.1]{buruso2026modelbased}; */ }
    @SourceRecord about C_SE_07_1 { identifier = "C-SE-07.1"; sourceText = "the high effort to reconcile incompatible modeling and simulation data formats \\citep[Sec.~5.1]{buruso2026modelbased};"; sourceLocator = "final_report/apendice.tex#C-SE-07.1 (current concern anchor, line 152)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "buruso2026modelbased"; }
    @CurrentDisposition about C_SE_07_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Data conversion, version control and reassessment affect effort, early semantic defects and evidence reconstruction. Measurements are supplied data. Hardware acquisition is excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_07_1 from C_SE_07_1 to C_SE_07;
    concern <'C-SE-07.1.1'> C_SE_07_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the risk of semantic misalignment and information loss during manual data conversions \citep[Sec.~5.1]{buruso2026modelbased}; */ }
    @SourceRecord about C_SE_07_1_1 { identifier = "C-SE-07.1.1"; sourceText = "the risk of semantic misalignment and information loss during manual data conversions \\citep[Sec.~5.1]{buruso2026modelbased};"; sourceLocator = "final_report/apendice.tex#C-SE-07.1.1 (current concern anchor, line 155)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "buruso2026modelbased"; }
    @CurrentDisposition about C_SE_07_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Data conversion, version control and reassessment affect effort, early semantic defects and evidence reconstruction. Measurements are supplied data. Hardware acquisition is excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_07_1_1 from C_SE_07_1_1 to C_SE_07_1;
    concern <'C-SE-07.2'> C_SE_07_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to associate each verification result with the applicable design, software, model, and input data versions \citep[Sec.~4.4]{buruso2026modelbased}; */ }
    @SourceRecord about C_SE_07_2 { identifier = "C-SE-07.2"; sourceText = "the high effort to associate each verification result with the applicable design, software, model, and input data versions \\citep[Sec.~4.4]{buruso2026modelbased};"; sourceLocator = "final_report/apendice.tex#C-SE-07.2 (current concern anchor, line 158)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "buruso2026modelbased"; }
    @CurrentDisposition about C_SE_07_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Data conversion, version control and reassessment affect effort, early semantic defects and evidence reconstruction. Measurements are supplied data. Hardware acquisition is excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_07_2 from C_SE_07_2 to C_SE_07;
    concern <'C-SE-07.3'> C_SE_07_3 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to carry measured behavior and revised model parameters back into design analyses \citep[Sec.~4.4]{buruso2026modelbased}\citep[p.~2]{handpicked-0001}; */ }
    @SourceRecord about C_SE_07_3 { identifier = "C-SE-07.3"; sourceText = "the high effort to carry measured behavior and revised model parameters back into design analyses \\citep[Sec.~4.4]{buruso2026modelbased}\\citep[p.~2]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-SE-07.3 (current concern anchor, line 160)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "buruso2026modelbased,handpicked-0001"; }
    @CurrentDisposition about C_SE_07_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Data conversion, version control and reassessment affect effort, early semantic defects and evidence reconstruction. Measurements are supplied data. Hardware acquisition is excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_07_3 from C_SE_07_3 to C_SE_07;
    concern <'C-SE-08'> C_SE_08 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to establish that analysis results are credible verification evidence \citep[Sec.~6]{review-1251}; */ }
    @SourceRecord about C_SE_08 { identifier = "C-SE-08"; sourceText = "the high effort to establish that analysis results are credible verification evidence \\citep[Sec.~6]{review-1251};"; sourceLocator = "final_report/apendice.tex#C-SE-08 (current concern anchor, line 163)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-1251"; }
    @CurrentDisposition about C_SE_08 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Model credibility assessment affects effort, early conclusions and reviewable validity and error limits. Unsupported extrapolation remains explicit."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    concern <'C-SE-08.1'> C_SE_08_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* C-EPS-2 */ }
    @SourceRecord about C_SE_08_1 { identifier = "C-SE-08.1"; sourceText = "C-EPS-2"; sourceLocator = "final_report/apendice.tex#C-SE-08.1 (current concern anchor, line 166)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_08_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Model fidelity and declared host runtime and resource costs affect task burden and credible conclusions. Hardware interaction qualification remains external. C-SE-08.1 aliases C-EPS-05."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_SE_08_1 from C_SE_08_1 to C_SE_08;
    #aliasReference dependency alias_C_SE_08_1 from C_SE_08_1 to C_EPS_05;
    concern <'C-SE-08.2'> C_SE_08_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to define model validity ranges and acceptable prediction errors for the intended verification decisions \citep[Sec.~6]{review-1251}; */ }
    @SourceRecord about C_SE_08_2 { identifier = "C-SE-08.2"; sourceText = "the high effort to define model validity ranges and acceptable prediction errors for the intended verification decisions \\citep[Sec.~6]{review-1251};"; sourceLocator = "final_report/apendice.tex#C-SE-08.2 (current concern anchor, line 168)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-1251"; }
    @CurrentDisposition about C_SE_08_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Model credibility assessment affects effort, early conclusions and reviewable validity and error limits. Unsupported extrapolation remains explicit."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_08_2 from C_SE_08_2 to C_SE_08;
    concern <'C-SE-08.3'> C_SE_08_3 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the uncertainty in predictions outside the tested loads, temperatures, and battery aging states \citep[pp.~5 and~8--9]{handpicked-0001}; */ }
    @SourceRecord about C_SE_08_3 { identifier = "C-SE-08.3"; sourceText = "the uncertainty in predictions outside the tested loads, temperatures, and battery aging states \\citep[pp.~5 and~8--9]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-SE-08.3 (current concern anchor, line 170)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_SE_08_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Model credibility assessment affects effort, early conclusions and reviewable validity and error limits. Unsupported extrapolation remains explicit."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_08_3 from C_SE_08_3 to C_SE_08;
    concern <'C-SE-09'> C_SE_09 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* (C-SE-3) the high effort to keep EPS hardware interfaces and flight software architecture consistent as the design changes \citep[Secs.~3--4]{review-0853}; */ }
    @SourceRecord about C_SE_09 { identifier = "C-SE-09"; sourceText = "(C-SE-3) the high effort to keep EPS hardware interfaces and flight software architecture consistent as the design changes \\citep[Secs.~3--4]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-SE-09 (current concern anchor, line 173)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_SE_09 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Interface changes affect effort, early mismatches and consistent evidence from models and host software. Flight deployment qualification remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    concern <'C-SE-09.1'> C_SE_09_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the difference between physical component groupings and the functional groupings used by flight software \citep[Sec.~3]{review-0853}; */ }
    @SourceRecord about C_SE_09_1 { identifier = "C-SE-09.1"; sourceText = "the difference between physical component groupings and the functional groupings used by flight software \\citep[Sec.~3]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-SE-09.1 (current concern anchor, line 176)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_SE_09_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Interface changes affect effort, early mismatches and consistent evidence from models and host software. Flight deployment qualification remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_09_1 from C_SE_09_1 to C_SE_09;
    concern <'C-SE-09.2'> C_SE_09_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to propagate EPS interface changes into software requirements and implementations \citep[Secs.~3--4]{review-0853}; */ }
    @SourceRecord about C_SE_09_2 { identifier = "C-SE-09.2"; sourceText = "the high effort to propagate EPS interface changes into software requirements and implementations \\citep[Secs.~3--4]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-SE-09.2 (current concern anchor, line 178)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_SE_09_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Interface changes affect effort, early mismatches and consistent evidence from models and host software. Flight deployment qualification remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_09_2 from C_SE_09_2 to C_SE_09;
    concern <'C-SE-09.2.1'> C_SE_09_2_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the late discovery of interface mismatches when hardware and software modules are developed separately \citep[Sec.~3]{review-0853}; */ }
    @SourceRecord about C_SE_09_2_1 { identifier = "C-SE-09.2.1"; sourceText = "the late discovery of interface mismatches when hardware and software modules are developed separately \\citep[Sec.~3]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-SE-09.2.1 (current concern anchor, line 181)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_SE_09_2_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Interface changes affect effort, early mismatches and consistent evidence from models and host software. Flight deployment qualification remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_09_2_1 from C_SE_09_2_1 to C_SE_09_2;
    concern <'C-SE-09.3'> C_SE_09_3 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* C-EPS-3 */ }
    @SourceRecord about C_SE_09_3 { identifier = "C-SE-09.3"; sourceText = "C-EPS-3"; sourceLocator = "final_report/apendice.tex#C-SE-09.3 (current concern anchor, line 184)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_SE_09_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Interface changes affect effort, early mismatches and consistent evidence from models and host software. Flight deployment qualification remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_09_3 from C_SE_09_3 to C_SE_09;
    #aliasReference dependency alias_C_SE_09_3 from C_SE_09_3 to C_EPS_09;
    concern <'C-SE-10'> C_SE_10 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to coordinate EPS control, telemetry collection, fault recovery, and spacecraft safe mode \citep[Sec.~V]{citation-0136}; */ }
    @SourceRecord about C_SE_10 { identifier = "C-SE-10"; sourceText = "the high effort to coordinate EPS control, telemetry collection, fault recovery, and spacecraft safe mode \\citep[Sec.~V]{citation-0136};"; sourceLocator = "final_report/apendice.tex#C-SE-10 (current concern anchor, line 187)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "citation-0136"; }
    @CurrentDisposition about C_SE_10 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Coordination affects effort, early mode and recovery defects, and reviewable MIL/SIL evidence. Operational safe mode assurance remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    concern <'C-SE-10.1'> C_SE_10_1 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the distribution of these responsibilities across separate flight software applications \citep[Sec.~V]{citation-0136}; */ }
    @SourceRecord about C_SE_10_1 { identifier = "C-SE-10.1"; sourceText = "the distribution of these responsibilities across separate flight software applications \\citep[Sec.~V]{citation-0136};"; sourceLocator = "final_report/apendice.tex#C-SE-10.1 (current concern anchor, line 190)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "citation-0136"; }
    @CurrentDisposition about C_SE_10_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Coordination affects effort, early mode and recovery defects, and reviewable MIL/SIL evidence. Operational safe mode assurance remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_10_1 from C_SE_10_1 to C_SE_10;
    concern <'C-SE-10.2'> C_SE_10_2 { subject enterprise : EngineeringEnterprise; stakeholder role : SystemsEngineer; doc /* the high effort to specify how EPS commands and telemetry relate to spacecraft mode changes and recovery actions \citep[Sec.~V]{citation-0136}; */ }
    @SourceRecord about C_SE_10_2 { identifier = "C-SE-10.2"; sourceText = "the high effort to specify how EPS commands and telemetry relate to spacecraft mode changes and recovery actions \\citep[Sec.~V]{citation-0136};"; sourceLocator = "final_report/apendice.tex#C-SE-10.2 (current concern anchor, line 192)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "citation-0136"; }
    @CurrentDisposition about C_SE_10_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Coordination affects effort, early mode and recovery defects, and reviewable MIL/SIL evidence. Operational safe mode assurance remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_SE_10_2 from C_SE_10_2 to C_SE_10;
    concern <'C-EPS-01'> C_EPS_01 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* (C-EPS-1) the high cost and effort to verify the EPS design after EPS requirements change; */ }
    @SourceRecord about C_EPS_01 { identifier = "C-EPS-01"; sourceText = "(C-EPS-1) the high cost and effort to verify the EPS design after EPS requirements change;"; sourceLocator = "final_report/apendice.tex#C-EPS-01 (current concern anchor, line 197)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_01 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Repeated modeled verification affects effort, early defects, evidence and costs of data and host computing. COTS, bench, hazardous fault and target timing conclusions require external evidence."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    concern <'C-EPS-01.1'> C_EPS_01_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high cost and effort to obtain evidence to verify EPS designs and compare candidate EPS physical architectures; */ }
    @SourceRecord about C_EPS_01_1 { identifier = "C-EPS-01.1"; sourceText = "the high cost and effort to obtain evidence to verify EPS designs and compare candidate EPS physical architectures;"; sourceLocator = "final_report/apendice.tex#C-EPS-01.1 (current concern anchor, line 200)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_01_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Repeated modeled verification affects effort, early defects, evidence and costs of data and host computing. COTS, bench, hazardous fault and target timing conclusions require external evidence."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_01_1 from C_EPS_01_1 to C_EPS_01;
    concern <'C-EPS-01.1.1'> C_EPS_01_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to verify candidate COTS for EPS designs; */ }
    @SourceRecord about C_EPS_01_1_1 { identifier = "C-EPS-01.1.1"; sourceText = "the high effort to verify candidate COTS for EPS designs;"; sourceLocator = "final_report/apendice.tex#C-EPS-01.1.1 (current concern anchor, line 203)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_01_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Repeated modeled verification affects effort, early defects, evidence and costs of data and host computing. COTS, bench, hazardous fault and target timing conclusions require external evidence."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_01_1_1 from C_EPS_01_1_1 to C_EPS_01_1;
    concern <'C-EPS-01.1.2'> C_EPS_01_1_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the dependence of controller verification on the availability of complete physical prototypes \citep[p.~3]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_01_1_2 { identifier = "C-EPS-01.1.2"; sourceText = "the dependence of controller verification on the availability of complete physical prototypes \\citep[p.~3]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-01.1.2 (current concern anchor, line 205)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_EPS_01_1_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Repeated modeled verification affects effort, early defects, evidence and costs of data and host computing. COTS, bench, hazardous fault and target timing conclusions require external evidence."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_01_1_2 from C_EPS_01_1_2 to C_EPS_01_1;
    concern <'C-EPS-01.1.3'> C_EPS_01_1_3 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to exercise controller changes under realistic electrical and timing constraints \citep[p.~3]{handpicked-0001}\citep[Sec.~3]{review-0573}; */ }
    @SourceRecord about C_EPS_01_1_3 { identifier = "C-EPS-01.1.3"; sourceText = "the high effort to exercise controller changes under realistic electrical and timing constraints \\citep[p.~3]{handpicked-0001}\\citep[Sec.~3]{review-0573};"; sourceLocator = "final_report/apendice.tex#C-EPS-01.1.3 (current concern anchor, line 207)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001,review-0573"; }
    @CurrentDisposition about C_EPS_01_1_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Repeated modeled verification affects effort, early defects, evidence and costs of data and host computing. COTS, bench, hazardous fault and target timing conclusions require external evidence."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_01_1_3 from C_EPS_01_1_3 to C_EPS_01_1;
    concern <'C-EPS-01.1.4'> C_EPS_01_1_4 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to reproduce orbital changes in irradiance, temperature, and load demand on the test bench \citep[Secs.~3.2 and~4]{review-0573}; */ }
    @SourceRecord about C_EPS_01_1_4 { identifier = "C-EPS-01.1.4"; sourceText = "the high effort to reproduce orbital changes in irradiance, temperature, and load demand on the test bench \\citep[Secs.~3.2 and~4]{review-0573};"; sourceLocator = "final_report/apendice.tex#C-EPS-01.1.4 (current concern anchor, line 209)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0573"; }
    @CurrentDisposition about C_EPS_01_1_4 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Repeated modeled verification affects effort, early defects, evidence and costs of data and host computing. COTS, bench, hazardous fault and target timing conclusions require external evidence."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_01_1_4 from C_EPS_01_1_4 to C_EPS_01_1;
    concern <'C-EPS-01.1.5'> C_EPS_01_1_5 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high cost and safety risk of obtaining evidence for rare or hazardous fault conditions \citep[p.~5]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_01_1_5 { identifier = "C-EPS-01.1.5"; sourceText = "the high cost and safety risk of obtaining evidence for rare or hazardous fault conditions \\citep[p.~5]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-01.1.5 (current concern anchor, line 211)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_EPS_01_1_5 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Repeated modeled verification affects effort, early defects, evidence and costs of data and host computing. COTS, bench, hazardous fault and target timing conclusions require external evidence."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_01_1_5 from C_EPS_01_1_5 to C_EPS_01_1;
    concern <'C-EPS-02'> C_EPS_02 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to maintain traceability from EPS requirements to EPS design decisions; */ }
    @SourceRecord about C_EPS_02 { identifier = "C-EPS-02"; sourceText = "the high effort to maintain traceability from EPS requirements to EPS design decisions;"; sourceLocator = "final_report/apendice.tex#C-EPS-02 (current concern anchor, line 215)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_02 { scopeStatus = "current context with bounded model/software contribution"; disposition = "EPS trace maintenance, reconstruction and learning traceability tools affect the measures. The alias retains its own ID."; moeIdentifiers = "MOE-01,MOE-03,MOE-04"; }
    concern <'C-EPS-02.1'> C_EPS_02_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* (C-SE-1-1) */ }
    @SourceRecord about C_EPS_02_1 { identifier = "C-EPS-02.1"; sourceText = "(C-SE-1-1)"; sourceLocator = "final_report/apendice.tex#C-EPS-02.1 (current concern anchor, line 218)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_02_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "EPS trace maintenance, reconstruction and learning traceability tools affect the measures. The alias retains its own ID."; moeIdentifiers = "MOE-01,MOE-03,MOE-04"; }
    #sourceTrace dependency causal_C_EPS_02_1 from C_EPS_02_1 to C_EPS_02;
    #aliasReference dependency alias_C_EPS_02_1 from C_EPS_02_1 to C_SE_01_1;
    concern <'C-EPS-03'> C_EPS_03 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to translate the verification evidence of failed gates into an updated EPS design; */ }
    @SourceRecord about C_EPS_03 { identifier = "C-EPS-03"; sourceText = "the high effort to translate the verification evidence of failed gates into an updated EPS design;"; sourceLocator = "final_report/apendice.tex#C-EPS-03 (current concern anchor, line 221)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_03 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Interpreting failed results and updating designs affect effort. Retained internal variables and traces support early diagnosis and review usefulness."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    concern <'C-EPS-03.1'> C_EPS_03_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the amount of variables relevant to EPS design included in verification evidence, which normally include only the inputs and outputs of the EPS as a black box; */ }
    @SourceRecord about C_EPS_03_1 { identifier = "C-EPS-03.1"; sourceText = "the amount of variables relevant to EPS design included in verification evidence, which normally include only the inputs and outputs of the EPS as a black box;"; sourceLocator = "final_report/apendice.tex#C-EPS-03.1 (current concern anchor, line 224)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_03_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Interpreting failed results and updating designs affect effort. Retained internal variables and traces support early diagnosis and review usefulness."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_03_1 from C_EPS_03_1 to C_EPS_03;
    concern <'C-EPS-03.2'> C_EPS_03_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to maintain traceability from verification evidence to EPS design decisions; */ }
    @SourceRecord about C_EPS_03_2 { identifier = "C-EPS-03.2"; sourceText = "the high effort to maintain traceability from verification evidence to EPS design decisions;"; sourceLocator = "final_report/apendice.tex#C-EPS-03.2 (current concern anchor, line 226)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_03_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Interpreting failed results and updating designs affect effort. Retained internal variables and traces support early diagnosis and review usefulness."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_03_2 from C_EPS_03_2 to C_EPS_03;
    concern <'C-EPS-04'> C_EPS_04 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to maintain EPS component requirements up to date when EPS designs change; */ }
    @SourceRecord about C_EPS_04 { identifier = "C-EPS-04"; sourceText = "the high effort to maintain EPS component requirements up to date when EPS designs change;"; sourceLocator = "final_report/apendice.tex#C-EPS-04 (current concern anchor, line 229)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Component changes, quantities and allowable ranges affect correct reassessment effort, early incompatibilities and current coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    concern <'C-EPS-04.1'> C_EPS_04_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the amount of EPS design changes; */ }
    @SourceRecord about C_EPS_04_1 { identifier = "C-EPS-04.1"; sourceText = "the amount of EPS design changes;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.1 (current concern anchor, line 232)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Component changes, quantities and allowable ranges affect correct reassessment effort, early incompatibilities and current coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_04_1 from C_EPS_04_1 to C_EPS_04;
    concern <'C-EPS-04.1.1'> C_EPS_04_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the amount of verification gates failed by the EPS designs; */ }
    @SourceRecord about C_EPS_04_1_1 { identifier = "C-EPS-04.1.1"; sourceText = "the amount of verification gates failed by the EPS designs;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.1.1 (current concern anchor, line 235)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Component changes, quantities and allowable ranges affect correct reassessment effort, early incompatibilities and current coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_04_1_1 from C_EPS_04_1_1 to C_EPS_04_1;
    concern <'C-EPS-04.2'> C_EPS_04_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* C-EPS-1 */ }
    @SourceRecord about C_EPS_04_2 { identifier = "C-EPS-04.2"; sourceText = "C-EPS-1"; sourceLocator = "final_report/apendice.tex#C-EPS-04.2 (current concern anchor, line 238)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "These aliases of C-EPS-01 share its bounded contribution from repeated modeled verification. Physical campaigns remain excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_04_2 from C_EPS_04_2 to C_EPS_04;
    #aliasReference dependency alias_C_EPS_04_2 from C_EPS_04_2 to C_EPS_01;
    concern <'C-EPS-04.3'> C_EPS_04_3 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to define pass/fail criteria for EPS component requirements; */ }
    @SourceRecord about C_EPS_04_3 { identifier = "C-EPS-04.3"; sourceText = "the high effort to define pass/fail criteria for EPS component requirements;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.3 (current concern anchor, line 240)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Component changes, quantities and allowable ranges affect correct reassessment effort, early incompatibilities and current coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_04_3 from C_EPS_04_3 to C_EPS_04;
    concern <'C-EPS-04.3.1'> C_EPS_04_3_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to determine the measurable variables of EPS components; */ }
    @SourceRecord about C_EPS_04_3_1 { identifier = "C-EPS-04.3.1"; sourceText = "the high effort to determine the measurable variables of EPS components;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.3.1 (current concern anchor, line 243)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_3_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Component changes, quantities and allowable ranges affect correct reassessment effort, early incompatibilities and current coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_04_3_1 from C_EPS_04_3_1 to C_EPS_04_3;
    concern <'C-EPS-04.3.2'> C_EPS_04_3_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to determine the allowable ranges of the relevant measurable variables of all EPS components; */ }
    @SourceRecord about C_EPS_04_3_2 { identifier = "C-EPS-04.3.2"; sourceText = "the high effort to determine the allowable ranges of the relevant measurable variables of all EPS components;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.3.2 (current concern anchor, line 245)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_3_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Component changes, quantities and allowable ranges affect correct reassessment effort, early incompatibilities and current coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_04_3_2 from C_EPS_04_3_2 to C_EPS_04_3;
    concern <'C-EPS-04.4'> C_EPS_04_4 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to define verification activities for EPS component requirements; */ }
    @SourceRecord about C_EPS_04_4 { identifier = "C-EPS-04.4"; sourceText = "the high effort to define verification activities for EPS component requirements;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.4 (current concern anchor, line 248)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_4 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Applicable component verification plans and methods affect effort, early defects and coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_04_4 from C_EPS_04_4 to C_EPS_04;
    concern <'C-EPS-04.4.1'> C_EPS_04_4_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the large amount of applicable standards; */ }
    @SourceRecord about C_EPS_04_4_1 { identifier = "C-EPS-04.4.1"; sourceText = "the large amount of applicable standards;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.4.1 (current concern anchor, line 251)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_4_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Applicable component verification plans and methods affect effort, early defects and coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_04_4_1 from C_EPS_04_4_1 to C_EPS_04_4;
    concern <'C-EPS-04.4.2'> C_EPS_04_4_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the large amount of potential verification activities published in the academic literature; */ }
    @SourceRecord about C_EPS_04_4_2 { identifier = "C-EPS-04.4.2"; sourceText = "the large amount of potential verification activities published in the academic literature;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.4.2 (current concern anchor, line 253)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_4_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Applicable component verification plans and methods affect effort, early defects and coverage."; moeIdentifiers = "MOE-01,MOE-02,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_04_4_2 from C_EPS_04_4_2 to C_EPS_04_4;
    concern <'C-EPS-04.4.4'> C_EPS_04_4_4 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to specify inspection, analysis, and demonstration conditions, how they interact with the component under test, and the procedure to generate verification evidence; */ }
    @SourceRecord about C_EPS_04_4_4 { identifier = "C-EPS-04.4.4"; sourceText = "the high effort to specify inspection, analysis, and demonstration conditions, how they interact with the component under test, and the procedure to generate verification evidence;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.4.4 (current concern anchor, line 255)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_4_4 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Procedure and tool compatibility, with informative evidence, support correct scoped checks. Physical component testing is excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_04_4_4 from C_EPS_04_4_4 to C_EPS_04_4;
    concern <'C-EPS-04.4.4.1'> C_EPS_04_4_4_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the large amount of variables that can be included in verification evidence to increase the translateability of evidence to an updated component choice or design in case of a failure; */ }
    @SourceRecord about C_EPS_04_4_4_1 { identifier = "C-EPS-04.4.4.1"; sourceText = "the large amount of variables that can be included in verification evidence to increase the translateability of evidence to an updated component choice or design in case of a failure;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.4.4.1 (current concern anchor, line 258)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_4_4_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Procedure and tool compatibility, with informative evidence, support correct scoped checks. Physical component testing is excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_04_4_4_1 from C_EPS_04_4_4_1 to C_EPS_04_4_4;
    concern <'C-EPS-04.4.4.2'> C_EPS_04_4_4_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* compatibility of specialized EPS engineering tools, like CAD and electrical simulators, with inspection, demonstration, and analysis procedures; */ }
    @SourceRecord about C_EPS_04_4_4_2 { identifier = "C-EPS-04.4.4.2"; sourceText = "compatibility of specialized EPS engineering tools, like CAD and electrical simulators, with inspection, demonstration, and analysis procedures;"; sourceLocator = "final_report/apendice.tex#C-EPS-04.4.4.2 (current concern anchor, line 260)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_04_4_4_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Procedure and tool compatibility, with informative evidence, support correct scoped checks. Physical component testing is excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_04_4_4_2 from C_EPS_04_4_4_2 to C_EPS_04_4_4;
    concern <'C-EPS-05'> C_EPS_05 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* (C-EPS-2) the high effort to keep EPS behavioral models representative of the physical design \citep[p.~2]{handpicked-0001}\citep[Sec.~6]{review-1251}; */ }
    @SourceRecord about C_EPS_05 { identifier = "C-EPS-05"; sourceText = "(C-EPS-2) the high effort to keep EPS behavioral models representative of the physical design \\citep[p.~2]{handpicked-0001}\\citep[Sec.~6]{review-1251};"; sourceLocator = "final_report/apendice.tex#C-EPS-05 (current concern anchor, line 265)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001,review-1251"; }
    @CurrentDisposition about C_EPS_05 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Model fidelity and declared host runtime and resource costs affect task burden and credible conclusions. Hardware interaction qualification remains external. C-SE-08.1 aliases C-EPS-05."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    concern <'C-EPS-05.1'> C_EPS_05_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to calibrate nonlinear component models against experimental data \citep[Sec.~4.1]{review-1251}; */ }
    @SourceRecord about C_EPS_05_1 { identifier = "C-EPS-05.1"; sourceText = "the high effort to calibrate nonlinear component models against experimental data \\citep[Sec.~4.1]{review-1251};"; sourceLocator = "final_report/apendice.tex#C-EPS-05.1 (current concern anchor, line 268)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-1251"; }
    @CurrentDisposition about C_EPS_05_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Calibration and updates from supplied data affect effort, drift detection and credible current evidence. New measurements and operational model tracking remain excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_05_1 from C_EPS_05_1 to C_EPS_05;
    concern <'C-EPS-05.1.1'> C_EPS_05_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the amount of interacting model parameters and calibration measurements \citep[Sec.~4.1]{review-1251}\citep[p.~8]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_05_1_1 { identifier = "C-EPS-05.1.1"; sourceText = "the amount of interacting model parameters and calibration measurements \\citep[Sec.~4.1]{review-1251}\\citep[p.~8]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-05.1.1 (current concern anchor, line 271)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-1251,handpicked-0001"; }
    @CurrentDisposition about C_EPS_05_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Calibration and updates from supplied data affect effort, drift detection and credible current evidence. New measurements and operational model tracking remain excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_05_1_1 from C_EPS_05_1_1 to C_EPS_05_1;
    concern <'C-EPS-05.2'> C_EPS_05_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the divergence of model predictions from hardware behavior as operating conditions and component health change \citep[p.~2]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_05_2 { identifier = "C-EPS-05.2"; sourceText = "the divergence of model predictions from hardware behavior as operating conditions and component health change \\citep[p.~2]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-05.2 (current concern anchor, line 274)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_EPS_05_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Calibration and updates from supplied data affect effort, drift detection and credible current evidence. New measurements and operational model tracking remain excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_05_2 from C_EPS_05_2 to C_EPS_05;
    concern <'C-EPS-05.2.1'> C_EPS_05_2_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the delay between collecting measurements and updating model parameters \citep[p.~2]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_05_2_1 { identifier = "C-EPS-05.2.1"; sourceText = "the delay between collecting measurements and updating model parameters \\citep[p.~2]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-05.2.1 (current concern anchor, line 277)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_EPS_05_2_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Calibration and updates from supplied data affect effort, drift detection and credible current evidence. New measurements and operational model tracking remain excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_05_2_1 from C_EPS_05_2_1 to C_EPS_05_2;
    concern <'C-EPS-05.3'> C_EPS_05_3 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the computational cost of coupled electrical, thermal, and degradation models \citep[pp.~2--3]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_05_3 { identifier = "C-EPS-05.3"; sourceText = "the computational cost of coupled electrical, thermal, and degradation models \\citep[pp.~2--3]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-05.3 (current concern anchor, line 280)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_EPS_05_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Model fidelity and declared host runtime and resource costs affect task burden and credible conclusions. Hardware interaction qualification remains external. C-SE-08.1 aliases C-EPS-05."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_05_3 from C_EPS_05_3 to C_EPS_05;
    concern <'C-EPS-05.3.1'> C_EPS_05_3_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the conflict between model fidelity and the execution time available for interaction with hardware \citep[pp.~2--3]{handpicked-0001}\citep[Sec.~3]{review-0573}; */ }
    @SourceRecord about C_EPS_05_3_1 { identifier = "C-EPS-05.3.1"; sourceText = "the conflict between model fidelity and the execution time available for interaction with hardware \\citep[pp.~2--3]{handpicked-0001}\\citep[Sec.~3]{review-0573};"; sourceLocator = "final_report/apendice.tex#C-EPS-05.3.1 (current concern anchor, line 283)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001,review-0573"; }
    @CurrentDisposition about C_EPS_05_3_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Model fidelity and declared host runtime and resource costs affect task burden and credible conclusions. Hardware interaction qualification remains external. C-SE-08.1 aliases C-EPS-05."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_05_3_1 from C_EPS_05_3_1 to C_EPS_05_3;
    concern <'C-EPS-05.4'> C_EPS_05_4 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* C-SE-2 */ }
    @SourceRecord about C_EPS_05_4 { identifier = "C-EPS-05.4"; sourceText = "C-SE-2"; sourceLocator = "final_report/apendice.tex#C-EPS-05.4 (current concern anchor, line 286)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_05_4 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Calibration and updates from supplied data affect effort, drift detection and credible current evidence. New measurements and operational model tracking remain excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_05_4 from C_EPS_05_4 to C_EPS_05;
    #aliasReference dependency alias_C_EPS_05_4 from C_EPS_05_4 to C_SE_07;
    concern <'C-EPS-06'> C_EPS_06 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high uncertainty in battery energy availability and remaining lifetime under mission loads \citep[Sec.~3]{handpicked-0003}\citep[pp.~1--3]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_06 { identifier = "C-EPS-06"; sourceText = "the high uncertainty in battery energy availability and remaining lifetime under mission loads \\citep[Sec.~3]{handpicked-0003}\\citep[pp.~1--3]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-06 (current concern anchor, line 289)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0003,handpicked-0001"; }
    @CurrentDisposition about C_EPS_06 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Battery states, aging, loads and temperature inform early issues and evidence limits. Measured battery lifetime improvement remains an external outcome."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    concern <'C-EPS-06.1'> C_EPS_06_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the limited visibility of internal battery states, including state of charge and state of health, from directly measured signals \citep[p.~1]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_06_1 { identifier = "C-EPS-06.1"; sourceText = "the limited visibility of internal battery states, including state of charge and state of health, from directly measured signals \\citep[p.~1]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-06.1 (current concern anchor, line 292)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_EPS_06_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Battery states, aging, loads and temperature inform early issues and evidence limits. Measured battery lifetime improvement remains an external outcome."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_06_1 from C_EPS_06_1 to C_EPS_06;
    concern <'C-EPS-06.2'> C_EPS_06_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the omission of long term degradation mechanisms from simplified battery models \citep[pp.~1--3]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_06_2 { identifier = "C-EPS-06.2"; sourceText = "the omission of long term degradation mechanisms from simplified battery models \\citep[pp.~1--3]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-06.2 (current concern anchor, line 294)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_EPS_06_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Battery states, aging, loads and temperature inform early issues and evidence limits. Measured battery lifetime improvement remains an external outcome."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_06_2 from C_EPS_06_2 to C_EPS_06;
    concern <'C-EPS-06.3'> C_EPS_06_3 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the coupled effects of load profiles, temperature, and depth of discharge on battery aging \citep[Sec.~3]{handpicked-0003}\citep[p.~3]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_06_3 { identifier = "C-EPS-06.3"; sourceText = "the coupled effects of load profiles, temperature, and depth of discharge on battery aging \\citep[Sec.~3]{handpicked-0003}\\citep[p.~3]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-06.3 (current concern anchor, line 296)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0003,handpicked-0001"; }
    @CurrentDisposition about C_EPS_06_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Battery states, aging, loads and temperature inform early issues and evidence limits. Measured battery lifetime improvement remains an external outcome."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_06_3 from C_EPS_06_3 to C_EPS_06;
    concern <'C-EPS-07'> C_EPS_07 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the low capability to detect EPS anomalies before protection thresholds are exceeded \citep[Sec.~5.1]{review-1251}; */ }
    @SourceRecord about C_EPS_07 { identifier = "C-EPS-07"; sourceText = "the low capability to detect EPS anomalies before protection thresholds are exceeded \\citep[Sec.~5.1]{review-1251};"; sourceLocator = "final_report/apendice.tex#C-EPS-07 (current concern anchor, line 299)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-1251"; }
    @CurrentDisposition about C_EPS_07 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Declared anomaly and protection scenarios inform assessment and evidence. General operational detection before protection thresholds is outside scope."; moeIdentifiers = "MOE-02,MOE-03,MOE-06"; }
    concern <'C-EPS-07.1'> C_EPS_07_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to determine the expected EPS response from operating states and telemetry spread across subsystem views \citep[Sec.~5.1]{review-1251}; */ }
    @SourceRecord about C_EPS_07_1 { identifier = "C-EPS-07.1"; sourceText = "the high effort to determine the expected EPS response from operating states and telemetry spread across subsystem views \\citep[Sec.~5.1]{review-1251};"; sourceLocator = "final_report/apendice.tex#C-EPS-07.1 (current concern anchor, line 302)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-1251"; }
    @CurrentDisposition about C_EPS_07_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Response and fault interpretation affect effort, confirmed modeled issues and review accuracy. Faults, degradation and measurement error remain distinct."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_07_1 from C_EPS_07_1 to C_EPS_07;
    concern <'C-EPS-07.2'> C_EPS_07_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to distinguish component faults from normal degradation and measurement error \citep[Sec.~6]{review-1251}; */ }
    @SourceRecord about C_EPS_07_2 { identifier = "C-EPS-07.2"; sourceText = "the high effort to distinguish component faults from normal degradation and measurement error \\citep[Sec.~6]{review-1251};"; sourceLocator = "final_report/apendice.tex#C-EPS-07.2 (current concern anchor, line 304)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-1251"; }
    @CurrentDisposition about C_EPS_07_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Response and fault interpretation affect effort, confirmed modeled issues and review accuracy. Faults, degradation and measurement error remain distinct."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_07_2 from C_EPS_07_2 to C_EPS_07;
    concern <'C-EPS-08'> C_EPS_08 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to verify that battery charging and power management decisions are safe and effective \citep[pp.~2 and~6]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_08 { identifier = "C-EPS-08"; sourceText = "the high effort to verify that battery charging and power management decisions are safe and effective \\citep[pp.~2 and~6]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-08 (current concern anchor, line 307)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_EPS_08 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Control assessment affects effort, modeled policy defects and evidence. Hardware safety and hardware benefit require separate external evidence."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    concern <'C-EPS-08.1'> C_EPS_08_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the gap between accurate battery behavior predictions and evidence that a control policy improves hardware performance \citep[p.~2]{handpicked-0001}; */ }
    @SourceRecord about C_EPS_08_1 { identifier = "C-EPS-08.1"; sourceText = "the gap between accurate battery behavior predictions and evidence that a control policy improves hardware performance \\citep[p.~2]{handpicked-0001};"; sourceLocator = "final_report/apendice.tex#C-EPS-08.1 (current concern anchor, line 310)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0001"; }
    @CurrentDisposition about C_EPS_08_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Control assessment affects effort, modeled policy defects and evidence. Hardware safety and hardware benefit require separate external evidence."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_08_1 from C_EPS_08_1 to C_EPS_08;
    concern <'C-EPS-09'> C_EPS_09 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* (C-EPS-3) the high effort to maintain consistent EPS command, telemetry, event, and parameter definitions across models, flight software, and ground software \citep[Secs.~3--4]{review-0853}; */ }
    @SourceRecord about C_EPS_09 { identifier = "C-EPS-09"; sourceText = "(C-EPS-3) the high effort to maintain consistent EPS command, telemetry, event, and parameter definitions across models, flight software, and ground software \\citep[Secs.~3--4]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-EPS-09 (current concern anchor, line 313)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_EPS_09 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Shared interface and software definitions affect effort, early inconsistencies and reviewable host mappings. Flight and ground operations qualification remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    concern <'C-EPS-09.1'> C_EPS_09_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to separately implement command, telemetry, event, and parameter definitions in the model export workflow described by \citet[Sec.~3]{review-0853}; */ }
    @SourceRecord about C_EPS_09_1 { identifier = "C-EPS-09.1"; sourceText = "the high effort to separately implement command, telemetry, event, and parameter definitions in the model export workflow described by \\citet[Sec.~3]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-EPS-09.1 (current concern anchor, line 316)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_EPS_09_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Shared interface and software definitions affect effort, early inconsistencies and reviewable host mappings. Flight and ground operations qualification remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_09_1 from C_EPS_09_1 to C_EPS_09;
    concern <'C-EPS-09.2'> C_EPS_09_2 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to translate modeled EPS behavior into mission-specific software functions \citep[Sec.~3]{review-0853}; */ }
    @SourceRecord about C_EPS_09_2 { identifier = "C-EPS-09.2"; sourceText = "the high effort to translate modeled EPS behavior into mission-specific software functions \\citep[Sec.~3]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-EPS-09.2 (current concern anchor, line 318)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_EPS_09_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Shared interface and software definitions affect effort, early inconsistencies and reviewable host mappings. Flight and ground operations qualification remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_09_2 from C_EPS_09_2 to C_EPS_09;
    concern <'C-EPS-10'> C_EPS_10 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to specify and verify EPS command execution conditions and expected effects \citep[Secs.~4--5]{review-0853}; */ }
    @SourceRecord about C_EPS_10 { identifier = "C-EPS-10"; sourceText = "the high effort to specify and verify EPS command execution conditions and expected effects \\citep[Secs.~4--5]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-EPS-10 (current concern anchor, line 321)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_EPS_10 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Command specification and assessment affect effort, early sequence defects and simulated guard and effect evidence. Flight execution remains excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    concern <'C-EPS-10.1'> C_EPS_10_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to translate EPS behavior into command sequences and confirm their functional flow with the flight software team \citep[Sec.~5]{review-0853}; */ }
    @SourceRecord about C_EPS_10_1 { identifier = "C-EPS-10.1"; sourceText = "the high effort to translate EPS behavior into command sequences and confirm their functional flow with the flight software team \\citep[Sec.~5]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-EPS-10.1 (current concern anchor, line 324)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_EPS_10_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Command specification and assessment affect effort, early sequence defects and simulated guard and effect evidence. Flight execution remains excluded."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_EPS_10_1 from C_EPS_10_1 to C_EPS_10;
    concern <'C-EPS-11'> C_EPS_11 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to communicate EPS designs during technical reviews; */ }
    @SourceRecord about C_EPS_11 { identifier = "C-EPS-11"; sourceText = "the high effort to communicate EPS designs during technical reviews;"; sourceLocator = "final_report/apendice.tex#C-EPS-11 (current concern anchor, line 327)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_11 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Effort to prepare accurate views and independent review interpretation."; moeIdentifiers = "MOE-01,MOE-03"; }
    concern <'C-EPS-11.1'> C_EPS_11_1 { subject enterprise : EngineeringEnterprise; stakeholder role : EPSEngineer; doc /* the high effort to generate readable, accurate, and informative graphical representations of EPS designs; */ }
    @SourceRecord about C_EPS_11_1 { identifier = "C-EPS-11.1"; sourceText = "the high effort to generate readable, accurate, and informative graphical representations of EPS designs;"; sourceLocator = "final_report/apendice.tex#C-EPS-11.1 (current concern anchor, line 330)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_EPS_11_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Effort to prepare accurate views and independent review interpretation."; moeIdentifiers = "MOE-01,MOE-03"; }
    #sourceTrace dependency causal_C_EPS_11_1 from C_EPS_11_1 to C_EPS_11;
    concern <'C-NE-01'> C_NE_01 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the high cost and effort to verify a subsystem design; */ }
    @SourceRecord about C_NE_01 { identifier = "C-NE-01"; sourceText = "the high cost and effort to verify a subsystem design;"; sourceLocator = "final_report/apendice.tex#C-NE-01 (current concern anchor, line 335)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_NE_01 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Subsystem power assessment affects effort, costs of data and host computing, early defects and evidence. Physical subsystem acceptance remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    concern <'C-NE-01.1'> C_NE_01_1 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the high cost and effort to verify the power requirements of a subsystem design; */ }
    @SourceRecord about C_NE_01_1 { identifier = "C-NE-01.1"; sourceText = "the high cost and effort to verify the power requirements of a subsystem design;"; sourceLocator = "final_report/apendice.tex#C-NE-01.1 (current concern anchor, line 338)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_NE_01_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Subsystem power assessment affects effort, costs of data and host computing, early defects and evidence. Physical subsystem acceptance remains external."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-05,MOE-06"; }
    #sourceTrace dependency causal_C_NE_01_1 from C_NE_01_1 to C_NE_01;
    concern <'C-NE-01.1.1'> C_NE_01_1_1 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the high effort to reproduce the subsystem's dynamic current demand during mission operations \citep[Sec.~8.1.7]{handpicked-0003}; */ }
    @SourceRecord about C_NE_01_1_1 { identifier = "C-NE-01.1.1"; sourceText = "the high effort to reproduce the subsystem's dynamic current demand during mission operations \\citep[Sec.~8.1.7]{handpicked-0003};"; sourceLocator = "final_report/apendice.tex#C-NE-01.1.1 (current concern anchor, line 341)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0003"; }
    @CurrentDisposition about C_NE_01_1_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Dynamic loads, supply events and consistency work affect effort, early interaction defects and evidence within model and software limits."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_NE_01_1_1 from C_NE_01_1_1 to C_NE_01_1;
    concern <'C-NE-01.1.2'> C_NE_01_1_2 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the high effort to verify subsystem behavior during EPS supply changes and protection events \citep[Secs.~8.1.6--8.1.7]{handpicked-0003}; */ }
    @SourceRecord about C_NE_01_1_2 { identifier = "C-NE-01.1.2"; sourceText = "the high effort to verify subsystem behavior during EPS supply changes and protection events \\citep[Secs.~8.1.6--8.1.7]{handpicked-0003};"; sourceLocator = "final_report/apendice.tex#C-NE-01.1.2 (current concern anchor, line 343)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "handpicked-0003"; }
    @CurrentDisposition about C_NE_01_1_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Dynamic loads, supply events and consistency work affect effort, early interaction defects and evidence within model and software limits."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_NE_01_1_2 from C_NE_01_1_2 to C_NE_01_1;
    concern <'C-NE-01.2'> C_NE_01_2 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* C-SE-2 */ }
    @SourceRecord about C_NE_01_2 { identifier = "C-NE-01.2"; sourceText = "C-SE-2"; sourceLocator = "final_report/apendice.tex#C-NE-01.2 (current concern anchor, line 346)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_NE_01_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Dynamic loads, supply events and consistency work affect effort, early interaction defects and evidence within model and software limits."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-06"; }
    #sourceTrace dependency causal_C_NE_01_2 from C_NE_01_2 to C_NE_01;
    #aliasReference dependency alias_C_NE_01_2 from C_NE_01_2 to C_SE_07;
    concern <'C-NE-02'> C_NE_02 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the high effort to integrate EPS services with flight software frameworks such as cFS and F-Prime \citep[Secs.~3--5]{review-0853}\citep[Sec.~III.B]{citation-0136}; */ }
    @SourceRecord about C_NE_02 { identifier = "C-NE-02"; sourceText = "the high effort to integrate EPS services with flight software frameworks such as cFS and F-Prime \\citep[Secs.~3--5]{review-0853}\\citep[Sec.~III.B]{citation-0136};"; sourceLocator = "final_report/apendice.tex#C-NE-02 (current concern anchor, line 349)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853,citation-0136"; }
    @CurrentDisposition about C_NE_02 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Host integration, mappings and adaptation affect effort, early interface defects and evidence. Selected profiles provide no target deployment qualification."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-04,MOE-06"; }
    concern <'C-NE-02.1'> C_NE_02_1 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* C-SE-3 */ }
    @SourceRecord about C_NE_02_1 { identifier = "C-NE-02.1"; sourceText = "C-SE-3"; sourceLocator = "final_report/apendice.tex#C-NE-02.1 (current concern anchor, line 352)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_NE_02_1 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Host integration, mappings and adaptation affect effort, early interface defects and evidence. Selected profiles provide no target deployment qualification."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-04,MOE-06"; }
    #sourceTrace dependency causal_C_NE_02_1 from C_NE_02_1 to C_NE_02;
    #aliasReference dependency alias_C_NE_02_1 from C_NE_02_1 to C_SE_09;
    concern <'C-NE-02.2'> C_NE_02_2 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* C-EPS-3 */ }
    @SourceRecord about C_NE_02_2 { identifier = "C-NE-02.2"; sourceText = "C-EPS-3"; sourceLocator = "final_report/apendice.tex#C-NE-02.2 (current concern anchor, line 354)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = ""; }
    @CurrentDisposition about C_NE_02_2 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Host integration, mappings and adaptation affect effort, early interface defects and evidence. Selected profiles provide no target deployment qualification."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-04,MOE-06"; }
    #sourceTrace dependency causal_C_NE_02_2 from C_NE_02_2 to C_NE_02;
    #aliasReference dependency alias_C_NE_02_2 from C_NE_02_2 to C_EPS_09;
    concern <'C-NE-02.3'> C_NE_02_3 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the high effort to map EPS interfaces onto framework-specific communication mechanisms \citep[Sec.~3]{review-0853}; */ }
    @SourceRecord about C_NE_02_3 { identifier = "C-NE-02.3"; sourceText = "the high effort to map EPS interfaces onto framework-specific communication mechanisms \\citep[Sec.~3]{review-0853};"; sourceLocator = "final_report/apendice.tex#C-NE-02.3 (current concern anchor, line 356)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "review-0853"; }
    @CurrentDisposition about C_NE_02_3 { scopeStatus = "current context with bounded model/software contribution"; disposition = "Host integration, mappings and adaptation affect effort, early interface defects and evidence. Selected profiles provide no target deployment qualification."; moeIdentifiers = "MOE-01,MOE-02,MOE-03,MOE-04,MOE-06"; }
    #sourceTrace dependency causal_C_NE_02_3 from C_NE_02_3 to C_NE_02;
    concern <'C-NE-02.4'> C_NE_02_4 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the high effort to configure and deploy the selected framework on the OBC processor and operating system \citep[Sec.~III.B]{citation-0136}; */ }
    @SourceRecord about C_NE_02_4 { identifier = "C-NE-02.4"; sourceText = "the high effort to configure and deploy the selected framework on the OBC processor and operating system \\citep[Sec.~III.B]{citation-0136};"; sourceLocator = "final_report/apendice.tex#C-NE-02.4 (current concern anchor, line 358)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "citation-0136"; }
    @CurrentDisposition about C_NE_02_4 { scopeStatus = "current target context, target qualification excluded"; disposition = "Host preparation, learning, adaptation and host resource records contribute in scope. OBC deployment and processor, memory, timing and power qualification remain external obligations."; moeIdentifiers = "MOE-01,MOE-03,MOE-04,MOE-06"; }
    #sourceTrace dependency causal_C_NE_02_4 from C_NE_02_4 to C_NE_02;
    concern <'C-NE-02.4.1'> C_NE_02_4_1 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the high effort to learn framework configuration and integration tools \citep[Sec.~III.B]{citation-0136}; */ }
    @SourceRecord about C_NE_02_4_1 { identifier = "C-NE-02.4.1"; sourceText = "the high effort to learn framework configuration and integration tools \\citep[Sec.~III.B]{citation-0136};"; sourceLocator = "final_report/apendice.tex#C-NE-02.4.1 (current concern anchor, line 361)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "citation-0136"; }
    @CurrentDisposition about C_NE_02_4_1 { scopeStatus = "current target context, target qualification excluded"; disposition = "Host preparation, learning, adaptation and host resource records contribute in scope. OBC deployment and processor, memory, timing and power qualification remain external obligations."; moeIdentifiers = "MOE-01,MOE-03,MOE-04,MOE-06"; }
    #sourceTrace dependency causal_C_NE_02_4_1 from C_NE_02_4_1 to C_NE_02_4;
    concern <'C-NE-02.5'> C_NE_02_5 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the high effort to verify processor, memory, timing, and power budgets for EPS flight software functions \citep[Secs.~III.A.3, IV.A.1 and~VI.B--C]{citation-0136}; */ }
    @SourceRecord about C_NE_02_5 { identifier = "C-NE-02.5"; sourceText = "the high effort to verify processor, memory, timing, and power budgets for EPS flight software functions \\citep[Secs.~III.A.3, IV.A.1 and~VI.B--C]{citation-0136};"; sourceLocator = "final_report/apendice.tex#C-NE-02.5 (current concern anchor, line 364)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "citation-0136"; }
    @CurrentDisposition about C_NE_02_5 { scopeStatus = "current target context, target qualification excluded"; disposition = "Host preparation, learning, adaptation and host resource records contribute in scope. OBC deployment and processor, memory, timing and power qualification remain external obligations."; moeIdentifiers = "MOE-01,MOE-03,MOE-04,MOE-06"; }
    #sourceTrace dependency causal_C_NE_02_5 from C_NE_02_5 to C_NE_02;
    concern <'C-NE-02.5.2'> C_NE_02_5_2 { subject enterprise : EngineeringEnterprise; stakeholder role : NonEPSEngineer; doc /* the interaction between operating system capabilities, processor performance, and power consumption \citep[Sec.~III.A.3]{citation-0136}; */ }
    @SourceRecord about C_NE_02_5_2 { identifier = "C-NE-02.5.2"; sourceText = "the interaction between operating system capabilities, processor performance, and power consumption \\citep[Sec.~III.A.3]{citation-0136};"; sourceLocator = "final_report/apendice.tex#C-NE-02.5.2 (current concern anchor, line 367)"; status = "current source assertion preserved, new stakeholder approval pending"; citationRecord = "citation-0136"; }
    @CurrentDisposition about C_NE_02_5_2 { scopeStatus = "current target context, target qualification excluded"; disposition = "Host preparation, learning, adaptation and host resource records contribute in scope. OBC deployment and processor, memory, timing and power qualification remain external obligations."; moeIdentifiers = "MOE-01,MOE-03,MOE-04,MOE-06"; }
    #sourceTrace dependency causal_C_NE_02_5_2 from C_NE_02_5_2 to C_NE_02_5;

    // BEGIN COMPLETE CONCERN-MOE CONTRIBUTIONS
    // Each occurrence has explicit bounded links. Aliases share observations.
    #qualitativeContribution dependency contribution_C_PM_01_MOE_01 from C_PM_01 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_PM_01_MOE_04 from C_PM_01 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_PM_01_MOE_05 from C_PM_01 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_PM_01_1_MOE_01 from C_PM_01_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_PM_01_1_MOE_04 from C_PM_01_1 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_PM_01_2_MOE_05 from C_PM_01_2 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_PM_03_MOE_02 from C_PM_03 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_PM_03_MOE_06 from C_PM_03 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_PM_03_1_MOE_02 from C_PM_03_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_PM_03_1_MOE_06 from C_PM_03_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_PM_03_1_1_MOE_02 from C_PM_03_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_PM_03_1_1_MOE_06 from C_PM_03_1_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_PM_04_MOE_06 from C_PM_04 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_PM_05_MOE_01 from C_PM_05 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_PM_05_MOE_04 from C_PM_05 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_PM_05_MOE_05 from C_PM_05 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_PM_05_1_MOE_01 from C_PM_05_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_PM_05_1_MOE_02 from C_PM_05_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_PM_05_1_MOE_03 from C_PM_05_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_PM_05_1_MOE_04 from C_PM_05_1 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_PM_05_1_MOE_06 from C_PM_05_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_01_MOE_01 from C_SE_01 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_01_MOE_03 from C_SE_01 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_01_MOE_04 from C_SE_01 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_SE_01_1_MOE_01 from C_SE_01_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_01_1_MOE_03 from C_SE_01_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_01_1_MOE_04 from C_SE_01_1 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_SE_01_1_1_MOE_01 from C_SE_01_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_01_1_1_MOE_03 from C_SE_01_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_01_1_1_MOE_04 from C_SE_01_1_1 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_SE_02_MOE_01 from C_SE_02 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_02_MOE_03 from C_SE_02 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_02_1_MOE_01 from C_SE_02_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_02_1_MOE_03 from C_SE_02_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_MOE_01 from C_SE_03 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_MOE_02 from C_SE_03 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_MOE_03 from C_SE_03 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_1_MOE_01 from C_SE_03_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_1_MOE_02 from C_SE_03_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_1_MOE_03 from C_SE_03_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_1_1_MOE_01 from C_SE_03_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_1_1_MOE_02 from C_SE_03_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_1_1_MOE_03 from C_SE_03_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_2_MOE_01 from C_SE_03_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_2_MOE_02 from C_SE_03_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_2_MOE_03 from C_SE_03_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_2_MOE_05 from C_SE_03_2 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_SE_03_2_MOE_06 from C_SE_03_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_03_3_MOE_01 from C_SE_03_3 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_3_MOE_02 from C_SE_03_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_3_MOE_03 from C_SE_03_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_MOE_01 from C_SE_03_3_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_MOE_02 from C_SE_03_3_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_MOE_03 from C_SE_03_3_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_1_MOE_01 from C_SE_03_3_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_1_MOE_02 from C_SE_03_3_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_1_MOE_03 from C_SE_03_3_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_2_MOE_01 from C_SE_03_3_1_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_2_MOE_02 from C_SE_03_3_1_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_2_MOE_03 from C_SE_03_3_1_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_MOE_01 from C_SE_03_3_1_3 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_MOE_02 from C_SE_03_3_1_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_MOE_03 from C_SE_03_3_1_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_1_MOE_01 from C_SE_03_3_1_3_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_1_MOE_02 from C_SE_03_3_1_3_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_1_MOE_03 from C_SE_03_3_1_3_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_2_MOE_01 from C_SE_03_3_1_3_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_2_MOE_02 from C_SE_03_3_1_3_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_2_MOE_03 from C_SE_03_3_1_3_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_4_MOE_01 from C_SE_03_4 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_4_MOE_02 from C_SE_03_4 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_4_MOE_03 from C_SE_03_4 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_4_1_MOE_01 from C_SE_03_4_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_4_1_MOE_02 from C_SE_03_4_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_4_1_MOE_03 from C_SE_03_4_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_03_4_2_MOE_01 from C_SE_03_4_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_03_4_2_MOE_02 from C_SE_03_4_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_03_4_2_MOE_03 from C_SE_03_4_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_04_MOE_01 from C_SE_04 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_04_MOE_02 from C_SE_04 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_04_MOE_03 from C_SE_04 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_04_1_MOE_01 from C_SE_04_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_04_1_MOE_02 from C_SE_04_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_04_1_MOE_03 from C_SE_04_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_04_1_1_MOE_01 from C_SE_04_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_04_1_1_MOE_02 from C_SE_04_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_04_1_1_MOE_03 from C_SE_04_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_05_MOE_02 from C_SE_05 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_05_MOE_03 from C_SE_05 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_05_MOE_06 from C_SE_05 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_05_1_MOE_02 from C_SE_05_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_05_1_MOE_03 from C_SE_05_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_05_1_MOE_06 from C_SE_05_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_05_2_MOE_01 from C_SE_05_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_05_2_MOE_02 from C_SE_05_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_05_2_MOE_03 from C_SE_05_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_05_2_MOE_06 from C_SE_05_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_MOE_01 from C_SE_05_2_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_MOE_02 from C_SE_05_2_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_MOE_03 from C_SE_05_2_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_MOE_05 from C_SE_05_2_1 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_MOE_06 from C_SE_05_2_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_1_MOE_01 from C_SE_05_2_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_1_MOE_02 from C_SE_05_2_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_1_MOE_03 from C_SE_05_2_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_1_MOE_05 from C_SE_05_2_1_1 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_1_MOE_06 from C_SE_05_2_1_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_2_MOE_01 from C_SE_05_2_1_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_2_MOE_02 from C_SE_05_2_1_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_2_MOE_03 from C_SE_05_2_1_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_2_MOE_06 from C_SE_05_2_1_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_2_1_MOE_01 from C_SE_05_2_1_2_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_2_1_MOE_02 from C_SE_05_2_1_2_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_2_1_MOE_03 from C_SE_05_2_1_2_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_05_2_1_2_1_MOE_06 from C_SE_05_2_1_2_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_06_MOE_02 from C_SE_06 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_06_MOE_03 from C_SE_06 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_06_MOE_06 from C_SE_06 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_06_1_MOE_02 from C_SE_06_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_06_1_MOE_03 from C_SE_06_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_06_1_MOE_06 from C_SE_06_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_06_2_MOE_02 from C_SE_06_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_06_2_MOE_03 from C_SE_06_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_06_2_MOE_06 from C_SE_06_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_07_MOE_01 from C_SE_07 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_07_MOE_02 from C_SE_07 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_07_MOE_03 from C_SE_07 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_07_MOE_06 from C_SE_07 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_07_1_MOE_01 from C_SE_07_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_07_1_MOE_02 from C_SE_07_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_07_1_MOE_03 from C_SE_07_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_07_1_MOE_06 from C_SE_07_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_07_1_1_MOE_01 from C_SE_07_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_07_1_1_MOE_02 from C_SE_07_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_07_1_1_MOE_03 from C_SE_07_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_07_1_1_MOE_06 from C_SE_07_1_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_07_2_MOE_01 from C_SE_07_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_07_2_MOE_02 from C_SE_07_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_07_2_MOE_03 from C_SE_07_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_07_2_MOE_06 from C_SE_07_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_07_3_MOE_01 from C_SE_07_3 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_07_3_MOE_02 from C_SE_07_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_07_3_MOE_03 from C_SE_07_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_07_3_MOE_06 from C_SE_07_3 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_08_MOE_01 from C_SE_08 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_08_MOE_02 from C_SE_08 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_08_MOE_03 from C_SE_08 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_08_MOE_06 from C_SE_08 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_08_1_MOE_01 from C_SE_08_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_08_1_MOE_02 from C_SE_08_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_08_1_MOE_03 from C_SE_08_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_08_1_MOE_05 from C_SE_08_1 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_SE_08_1_MOE_06 from C_SE_08_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_08_2_MOE_01 from C_SE_08_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_08_2_MOE_02 from C_SE_08_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_08_2_MOE_03 from C_SE_08_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_08_2_MOE_06 from C_SE_08_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_08_3_MOE_01 from C_SE_08_3 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_08_3_MOE_02 from C_SE_08_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_08_3_MOE_03 from C_SE_08_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_08_3_MOE_06 from C_SE_08_3 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_09_MOE_01 from C_SE_09 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_09_MOE_02 from C_SE_09 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_09_MOE_03 from C_SE_09 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_09_MOE_06 from C_SE_09 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_09_1_MOE_01 from C_SE_09_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_09_1_MOE_02 from C_SE_09_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_09_1_MOE_03 from C_SE_09_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_09_1_MOE_06 from C_SE_09_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_09_2_MOE_01 from C_SE_09_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_09_2_MOE_02 from C_SE_09_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_09_2_MOE_03 from C_SE_09_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_09_2_MOE_06 from C_SE_09_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_09_2_1_MOE_01 from C_SE_09_2_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_09_2_1_MOE_02 from C_SE_09_2_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_09_2_1_MOE_03 from C_SE_09_2_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_09_2_1_MOE_06 from C_SE_09_2_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_09_3_MOE_01 from C_SE_09_3 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_09_3_MOE_02 from C_SE_09_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_09_3_MOE_03 from C_SE_09_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_09_3_MOE_06 from C_SE_09_3 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_10_MOE_01 from C_SE_10 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_10_MOE_02 from C_SE_10 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_10_MOE_03 from C_SE_10 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_10_MOE_06 from C_SE_10 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_10_1_MOE_01 from C_SE_10_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_10_1_MOE_02 from C_SE_10_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_10_1_MOE_03 from C_SE_10_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_10_1_MOE_06 from C_SE_10_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_SE_10_2_MOE_01 from C_SE_10_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_SE_10_2_MOE_02 from C_SE_10_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_SE_10_2_MOE_03 from C_SE_10_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_SE_10_2_MOE_06 from C_SE_10_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_01_MOE_01 from C_EPS_01 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_01_MOE_02 from C_EPS_01 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_01_MOE_03 from C_EPS_01 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_01_MOE_05 from C_EPS_01 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_01_MOE_06 from C_EPS_01 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_01_1_MOE_01 from C_EPS_01_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_01_1_MOE_02 from C_EPS_01_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_01_1_MOE_03 from C_EPS_01_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_01_1_MOE_05 from C_EPS_01_1 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_01_1_MOE_06 from C_EPS_01_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_01_1_1_MOE_01 from C_EPS_01_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_01_1_1_MOE_02 from C_EPS_01_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_01_1_1_MOE_03 from C_EPS_01_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_01_1_1_MOE_05 from C_EPS_01_1_1 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_01_1_1_MOE_06 from C_EPS_01_1_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_01_1_2_MOE_01 from C_EPS_01_1_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_01_1_2_MOE_02 from C_EPS_01_1_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_01_1_2_MOE_03 from C_EPS_01_1_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_01_1_2_MOE_05 from C_EPS_01_1_2 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_01_1_2_MOE_06 from C_EPS_01_1_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_01_1_3_MOE_01 from C_EPS_01_1_3 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_01_1_3_MOE_02 from C_EPS_01_1_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_01_1_3_MOE_03 from C_EPS_01_1_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_01_1_3_MOE_05 from C_EPS_01_1_3 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_01_1_3_MOE_06 from C_EPS_01_1_3 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_01_1_4_MOE_01 from C_EPS_01_1_4 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_01_1_4_MOE_02 from C_EPS_01_1_4 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_01_1_4_MOE_03 from C_EPS_01_1_4 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_01_1_4_MOE_05 from C_EPS_01_1_4 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_01_1_4_MOE_06 from C_EPS_01_1_4 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_01_1_5_MOE_01 from C_EPS_01_1_5 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_01_1_5_MOE_02 from C_EPS_01_1_5 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_01_1_5_MOE_03 from C_EPS_01_1_5 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_01_1_5_MOE_05 from C_EPS_01_1_5 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_01_1_5_MOE_06 from C_EPS_01_1_5 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_02_MOE_01 from C_EPS_02 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_02_MOE_03 from C_EPS_02 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_02_MOE_04 from C_EPS_02 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_EPS_02_1_MOE_01 from C_EPS_02_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_02_1_MOE_03 from C_EPS_02_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_02_1_MOE_04 from C_EPS_02_1 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_EPS_03_MOE_01 from C_EPS_03 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_03_MOE_02 from C_EPS_03 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_03_MOE_03 from C_EPS_03 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_03_1_MOE_01 from C_EPS_03_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_03_1_MOE_02 from C_EPS_03_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_03_1_MOE_03 from C_EPS_03_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_03_2_MOE_01 from C_EPS_03_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_03_2_MOE_02 from C_EPS_03_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_03_2_MOE_03 from C_EPS_03_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_MOE_01 from C_EPS_04 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_MOE_02 from C_EPS_04 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_MOE_03 from C_EPS_04 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_1_MOE_01 from C_EPS_04_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_1_MOE_02 from C_EPS_04_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_1_MOE_03 from C_EPS_04_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_1_1_MOE_01 from C_EPS_04_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_1_1_MOE_02 from C_EPS_04_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_1_1_MOE_03 from C_EPS_04_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_2_MOE_01 from C_EPS_04_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_2_MOE_02 from C_EPS_04_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_2_MOE_03 from C_EPS_04_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_2_MOE_05 from C_EPS_04_2 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_04_2_MOE_06 from C_EPS_04_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_04_3_MOE_01 from C_EPS_04_3 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_3_MOE_02 from C_EPS_04_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_3_MOE_03 from C_EPS_04_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_3_1_MOE_01 from C_EPS_04_3_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_3_1_MOE_02 from C_EPS_04_3_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_3_1_MOE_03 from C_EPS_04_3_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_3_2_MOE_01 from C_EPS_04_3_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_3_2_MOE_02 from C_EPS_04_3_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_3_2_MOE_03 from C_EPS_04_3_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_4_MOE_01 from C_EPS_04_4 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_4_MOE_02 from C_EPS_04_4 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_4_MOE_03 from C_EPS_04_4 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_4_1_MOE_01 from C_EPS_04_4_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_4_1_MOE_02 from C_EPS_04_4_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_4_1_MOE_03 from C_EPS_04_4_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_4_2_MOE_01 from C_EPS_04_4_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_4_2_MOE_02 from C_EPS_04_4_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_4_2_MOE_03 from C_EPS_04_4_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_MOE_01 from C_EPS_04_4_4 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_MOE_02 from C_EPS_04_4_4 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_MOE_03 from C_EPS_04_4_4 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_MOE_06 from C_EPS_04_4_4 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_1_MOE_01 from C_EPS_04_4_4_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_1_MOE_02 from C_EPS_04_4_4_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_1_MOE_03 from C_EPS_04_4_4_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_1_MOE_06 from C_EPS_04_4_4_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_2_MOE_01 from C_EPS_04_4_4_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_2_MOE_02 from C_EPS_04_4_4_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_2_MOE_03 from C_EPS_04_4_4_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_04_4_4_2_MOE_06 from C_EPS_04_4_4_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_05_MOE_01 from C_EPS_05 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_05_MOE_02 from C_EPS_05 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_05_MOE_03 from C_EPS_05 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_05_MOE_05 from C_EPS_05 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_05_MOE_06 from C_EPS_05 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_05_1_MOE_01 from C_EPS_05_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_05_1_MOE_02 from C_EPS_05_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_05_1_MOE_03 from C_EPS_05_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_05_1_MOE_06 from C_EPS_05_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_05_1_1_MOE_01 from C_EPS_05_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_05_1_1_MOE_02 from C_EPS_05_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_05_1_1_MOE_03 from C_EPS_05_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_05_1_1_MOE_06 from C_EPS_05_1_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_05_2_MOE_01 from C_EPS_05_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_05_2_MOE_02 from C_EPS_05_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_05_2_MOE_03 from C_EPS_05_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_05_2_MOE_06 from C_EPS_05_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_05_2_1_MOE_01 from C_EPS_05_2_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_05_2_1_MOE_02 from C_EPS_05_2_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_05_2_1_MOE_03 from C_EPS_05_2_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_05_2_1_MOE_06 from C_EPS_05_2_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_05_3_MOE_01 from C_EPS_05_3 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_05_3_MOE_02 from C_EPS_05_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_05_3_MOE_03 from C_EPS_05_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_05_3_MOE_05 from C_EPS_05_3 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_05_3_MOE_06 from C_EPS_05_3 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_05_3_1_MOE_01 from C_EPS_05_3_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_05_3_1_MOE_02 from C_EPS_05_3_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_05_3_1_MOE_03 from C_EPS_05_3_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_05_3_1_MOE_05 from C_EPS_05_3_1 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_EPS_05_3_1_MOE_06 from C_EPS_05_3_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_05_4_MOE_01 from C_EPS_05_4 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_05_4_MOE_02 from C_EPS_05_4 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_05_4_MOE_03 from C_EPS_05_4 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_05_4_MOE_06 from C_EPS_05_4 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_06_MOE_02 from C_EPS_06 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_06_MOE_03 from C_EPS_06 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_06_MOE_06 from C_EPS_06 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_06_1_MOE_02 from C_EPS_06_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_06_1_MOE_03 from C_EPS_06_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_06_1_MOE_06 from C_EPS_06_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_06_2_MOE_02 from C_EPS_06_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_06_2_MOE_03 from C_EPS_06_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_06_2_MOE_06 from C_EPS_06_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_06_3_MOE_02 from C_EPS_06_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_06_3_MOE_03 from C_EPS_06_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_06_3_MOE_06 from C_EPS_06_3 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_07_MOE_02 from C_EPS_07 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_07_MOE_03 from C_EPS_07 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_07_MOE_06 from C_EPS_07 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_07_1_MOE_01 from C_EPS_07_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_07_1_MOE_02 from C_EPS_07_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_07_1_MOE_03 from C_EPS_07_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_07_1_MOE_06 from C_EPS_07_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_07_2_MOE_01 from C_EPS_07_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_07_2_MOE_02 from C_EPS_07_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_07_2_MOE_03 from C_EPS_07_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_07_2_MOE_06 from C_EPS_07_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_08_MOE_01 from C_EPS_08 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_08_MOE_02 from C_EPS_08 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_08_MOE_03 from C_EPS_08 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_08_MOE_06 from C_EPS_08 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_08_1_MOE_01 from C_EPS_08_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_08_1_MOE_02 from C_EPS_08_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_08_1_MOE_03 from C_EPS_08_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_08_1_MOE_06 from C_EPS_08_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_09_MOE_01 from C_EPS_09 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_09_MOE_02 from C_EPS_09 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_09_MOE_03 from C_EPS_09 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_09_MOE_06 from C_EPS_09 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_09_1_MOE_01 from C_EPS_09_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_09_1_MOE_02 from C_EPS_09_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_09_1_MOE_03 from C_EPS_09_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_09_1_MOE_06 from C_EPS_09_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_09_2_MOE_01 from C_EPS_09_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_09_2_MOE_02 from C_EPS_09_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_09_2_MOE_03 from C_EPS_09_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_09_2_MOE_06 from C_EPS_09_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_10_MOE_01 from C_EPS_10 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_10_MOE_02 from C_EPS_10 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_10_MOE_03 from C_EPS_10 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_10_MOE_06 from C_EPS_10 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_10_1_MOE_01 from C_EPS_10_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_10_1_MOE_02 from C_EPS_10_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_EPS_10_1_MOE_03 from C_EPS_10_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_10_1_MOE_06 from C_EPS_10_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_EPS_11_MOE_01 from C_EPS_11 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_11_MOE_03 from C_EPS_11 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_EPS_11_1_MOE_01 from C_EPS_11_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_EPS_11_1_MOE_03 from C_EPS_11_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_01_MOE_01 from C_NE_01 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_01_MOE_02 from C_NE_01 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_NE_01_MOE_03 from C_NE_01 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_01_MOE_05 from C_NE_01 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_NE_01_MOE_06 from C_NE_01 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_01_1_MOE_01 from C_NE_01_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_01_1_MOE_02 from C_NE_01_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_NE_01_1_MOE_03 from C_NE_01_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_01_1_MOE_05 from C_NE_01_1 to FrameworkNeeds::MOE_05;
    #qualitativeContribution dependency contribution_C_NE_01_1_MOE_06 from C_NE_01_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_01_1_1_MOE_01 from C_NE_01_1_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_01_1_1_MOE_02 from C_NE_01_1_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_NE_01_1_1_MOE_03 from C_NE_01_1_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_01_1_1_MOE_06 from C_NE_01_1_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_01_1_2_MOE_01 from C_NE_01_1_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_01_1_2_MOE_02 from C_NE_01_1_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_NE_01_1_2_MOE_03 from C_NE_01_1_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_01_1_2_MOE_06 from C_NE_01_1_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_01_2_MOE_01 from C_NE_01_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_01_2_MOE_02 from C_NE_01_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_NE_01_2_MOE_03 from C_NE_01_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_01_2_MOE_06 from C_NE_01_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_02_MOE_01 from C_NE_02 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_02_MOE_02 from C_NE_02 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_NE_02_MOE_03 from C_NE_02 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_02_MOE_04 from C_NE_02 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_NE_02_MOE_06 from C_NE_02 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_02_1_MOE_01 from C_NE_02_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_02_1_MOE_02 from C_NE_02_1 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_NE_02_1_MOE_03 from C_NE_02_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_02_1_MOE_04 from C_NE_02_1 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_NE_02_1_MOE_06 from C_NE_02_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_02_2_MOE_01 from C_NE_02_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_02_2_MOE_02 from C_NE_02_2 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_NE_02_2_MOE_03 from C_NE_02_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_02_2_MOE_04 from C_NE_02_2 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_NE_02_2_MOE_06 from C_NE_02_2 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_02_3_MOE_01 from C_NE_02_3 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_02_3_MOE_02 from C_NE_02_3 to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency contribution_C_NE_02_3_MOE_03 from C_NE_02_3 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_02_3_MOE_04 from C_NE_02_3 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_NE_02_3_MOE_06 from C_NE_02_3 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_02_4_MOE_01 from C_NE_02_4 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_02_4_MOE_03 from C_NE_02_4 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_02_4_MOE_04 from C_NE_02_4 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_NE_02_4_MOE_06 from C_NE_02_4 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_02_4_1_MOE_01 from C_NE_02_4_1 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_02_4_1_MOE_03 from C_NE_02_4_1 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_02_4_1_MOE_04 from C_NE_02_4_1 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_NE_02_4_1_MOE_06 from C_NE_02_4_1 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_02_5_MOE_01 from C_NE_02_5 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_02_5_MOE_03 from C_NE_02_5 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_02_5_MOE_04 from C_NE_02_5 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_NE_02_5_MOE_06 from C_NE_02_5 to FrameworkNeeds::MOE_06;
    #qualitativeContribution dependency contribution_C_NE_02_5_2_MOE_01 from C_NE_02_5_2 to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency contribution_C_NE_02_5_2_MOE_03 from C_NE_02_5_2 to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency contribution_C_NE_02_5_2_MOE_04 from C_NE_02_5_2 to FrameworkNeeds::MOE_04;
    #qualitativeContribution dependency contribution_C_NE_02_5_2_MOE_06 from C_NE_02_5_2 to FrameworkNeeds::MOE_06;
    // END COMPLETE CONCERN-MOE CONTRIBUTIONS
}
