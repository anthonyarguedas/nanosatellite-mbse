// Proposed framework specifications and trace relationships.
// Source locators retain historical provenance.
package FrameworkNeeds {
private import FrameworkDomain::*;
requirement <'MN-01'> MN_01 { subject enterprise : EngineeringEnterprise; doc /* Enable engineers to learn requirement writing and maintain sourced, verifiable requirements with reusable templates and verification criteria. */ }
@SourceRecord { identifier = "MN-01"; sourceText = "Enable engineers to learn requirement writing and maintain sourced, verifiable requirements with reusable templates and verification criteria."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-01'> MR_01 { subject enterprise : EngineeringEnterprise; doc /* The EPS engineering enterprise shall produce reviewable framework-supported EPS and component requirements whose source, observable quantities or conditions, verification method, criterion, and unresolved decisions are explicit. */ }
@SourceRecord { identifier = "MR-01"; sourceText = "The EPS engineering enterprise shall produce reviewable framework-supported EPS and component requirements whose source, observable quantities or conditions, verification method, criterion, and unresolved decisions are explicit."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_01 from MR_01 to MN_01;
item <'MOE-01'> MOE_01 : FrameworkEvaluation { doc /* Requirement authoring and update effort (person-hours). Report defects found by a qualified reviewer and completeness against the declared requirement record schema. */ }
#sourceTrace dependency measure_MN_01 from MOE_01 to MN_01;
#sourceTrace dependency need_source_MN_01_C_PM_01 from MN_01 to FrameworkConcerns::C_PM_01;
#sourceTrace dependency need_source_MN_01_C_PM_01_1 from MN_01 to FrameworkConcerns::C_PM_01_1;
#sourceTrace dependency need_source_MN_01_C_SE_01_1 from MN_01 to FrameworkConcerns::C_SE_01_1;
#sourceTrace dependency need_source_MN_01_C_SE_01_1_1 from MN_01 to FrameworkConcerns::C_SE_01_1_1;
#sourceTrace dependency need_source_MN_01_C_SE_03 from MN_01 to FrameworkConcerns::C_SE_03;
#sourceTrace dependency need_source_MN_01_C_SE_03_3 from MN_01 to FrameworkConcerns::C_SE_03_3;
#sourceTrace dependency need_source_MN_01_C_SE_03_3_1 from MN_01 to FrameworkConcerns::C_SE_03_3_1;
#sourceTrace dependency need_source_MN_01_C_SE_03_3_1_1 from MN_01 to FrameworkConcerns::C_SE_03_3_1_1;
#sourceTrace dependency need_source_MN_01_C_SE_03_3_1_3 from MN_01 to FrameworkConcerns::C_SE_03_3_1_3;
#sourceTrace dependency need_source_MN_01_C_SE_03_3_1_3_1 from MN_01 to FrameworkConcerns::C_SE_03_3_1_3_1;
#sourceTrace dependency need_source_MN_01_C_SE_03_3_1_3_2 from MN_01 to FrameworkConcerns::C_SE_03_3_1_3_2;
#sourceTrace dependency need_source_MN_01_C_SE_03_4 from MN_01 to FrameworkConcerns::C_SE_03_4;
#sourceTrace dependency need_source_MN_01_C_SE_03_4_1 from MN_01 to FrameworkConcerns::C_SE_03_4_1;
#sourceTrace dependency need_source_MN_01_C_SE_03_4_2 from MN_01 to FrameworkConcerns::C_SE_03_4_2;
#sourceTrace dependency need_source_MN_01_C_SE_05_1 from MN_01 to FrameworkConcerns::C_SE_05_1;
#sourceTrace dependency need_source_MN_01_C_EPS_02_1 from MN_01 to FrameworkConcerns::C_EPS_02_1;
#sourceTrace dependency need_source_MN_01_C_EPS_04 from MN_01 to FrameworkConcerns::C_EPS_04;
#sourceTrace dependency need_source_MN_01_C_EPS_04_3 from MN_01 to FrameworkConcerns::C_EPS_04_3;
#sourceTrace dependency need_source_MN_01_C_EPS_04_3_1 from MN_01 to FrameworkConcerns::C_EPS_04_3_1;
#sourceTrace dependency need_source_MN_01_C_EPS_04_3_2 from MN_01 to FrameworkConcerns::C_EPS_04_3_2;
#sourceTrace dependency need_source_MN_01_C_EPS_04_4 from MN_01 to FrameworkConcerns::C_EPS_04_4;
#sourceTrace dependency need_source_MN_01_C_EPS_04_4_1 from MN_01 to FrameworkConcerns::C_EPS_04_4_1;
#sourceTrace dependency need_source_MN_01_C_EPS_04_4_2 from MN_01 to FrameworkConcerns::C_EPS_04_4_2;
requirement <'MN-02'> MN_02 { subject enterprise : EngineeringEnterprise; doc /* Keep needs, requirements, design decisions, subsystem allocations, models, software interfaces, and verification evidence consistent as EPS and other subsystem designs change. */ }
@SourceRecord { identifier = "MN-02"; sourceText = "Keep needs, requirements, design decisions, subsystem allocations, models, software interfaces, and verification evidence consistent as EPS and other subsystem designs change."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-02'> MR_02 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall identify the affected evidence for each designated change and issue a successor baseline with regenerated or explicitly stale evidence and retained discrepancy status. */ }
@SourceRecord { identifier = "MR-02"; sourceText = "The enterprise shall identify the affected evidence for each designated change and issue a successor baseline with regenerated or explicitly stale evidence and retained discrepancy status."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_02 from MR_02 to MN_02;
item <'MOE-02'> MOE_02 : FrameworkEvaluation { doc /* Correct change turnaround (elapsed hours) and active effort. On a blinded reference set report TP, FP, FN and affected-artifact accuracy against a qualified reviewer. Faster incomplete changes receive no comparative credit. */ }
#sourceTrace dependency measure_MN_02 from MOE_02 to MN_02;
#sourceTrace dependency need_source_MN_02_C_PM_02_1_2 from MN_02 to FrameworkConcerns::C_PM_02_1_2;
#sourceTrace dependency need_source_MN_02_C_PM_05 from MN_02 to FrameworkConcerns::C_PM_05;
#sourceTrace dependency need_source_MN_02_C_PM_05_1 from MN_02 to FrameworkConcerns::C_PM_05_1;
#sourceTrace dependency need_source_MN_02_C_SE_01 from MN_02 to FrameworkConcerns::C_SE_01;
#sourceTrace dependency need_source_MN_02_C_SE_02 from MN_02 to FrameworkConcerns::C_SE_02;
#sourceTrace dependency need_source_MN_02_C_SE_02_1 from MN_02 to FrameworkConcerns::C_SE_02_1;
#sourceTrace dependency need_source_MN_02_C_SE_03 from MN_02 to FrameworkConcerns::C_SE_03;
#sourceTrace dependency need_source_MN_02_C_SE_03_1 from MN_02 to FrameworkConcerns::C_SE_03_1;
#sourceTrace dependency need_source_MN_02_C_SE_03_1_1 from MN_02 to FrameworkConcerns::C_SE_03_1_1;
#sourceTrace dependency need_source_MN_02_C_SE_03_2 from MN_02 to FrameworkConcerns::C_SE_03_2;
#sourceTrace dependency need_source_MN_02_C_SE_04 from MN_02 to FrameworkConcerns::C_SE_04;
#sourceTrace dependency need_source_MN_02_C_SE_04_1 from MN_02 to FrameworkConcerns::C_SE_04_1;
#sourceTrace dependency need_source_MN_02_C_SE_04_1_1 from MN_02 to FrameworkConcerns::C_SE_04_1_1;
#sourceTrace dependency need_source_MN_02_C_SE_07 from MN_02 to FrameworkConcerns::C_SE_07;
#sourceTrace dependency need_source_MN_02_C_SE_07_1 from MN_02 to FrameworkConcerns::C_SE_07_1;
#sourceTrace dependency need_source_MN_02_C_SE_07_1_1 from MN_02 to FrameworkConcerns::C_SE_07_1_1;
#sourceTrace dependency need_source_MN_02_C_SE_07_2 from MN_02 to FrameworkConcerns::C_SE_07_2;
#sourceTrace dependency need_source_MN_02_C_SE_07_3 from MN_02 to FrameworkConcerns::C_SE_07_3;
#sourceTrace dependency need_source_MN_02_C_SE_09 from MN_02 to FrameworkConcerns::C_SE_09;
#sourceTrace dependency need_source_MN_02_C_SE_09_1 from MN_02 to FrameworkConcerns::C_SE_09_1;
#sourceTrace dependency need_source_MN_02_C_SE_09_2 from MN_02 to FrameworkConcerns::C_SE_09_2;
#sourceTrace dependency need_source_MN_02_C_SE_09_2_1 from MN_02 to FrameworkConcerns::C_SE_09_2_1;
#sourceTrace dependency need_source_MN_02_C_EPS_01 from MN_02 to FrameworkConcerns::C_EPS_01;
#sourceTrace dependency need_source_MN_02_C_EPS_01_1 from MN_02 to FrameworkConcerns::C_EPS_01_1;
#sourceTrace dependency need_source_MN_02_C_EPS_02 from MN_02 to FrameworkConcerns::C_EPS_02;
#sourceTrace dependency need_source_MN_02_C_EPS_03 from MN_02 to FrameworkConcerns::C_EPS_03;
#sourceTrace dependency need_source_MN_02_C_EPS_03_1 from MN_02 to FrameworkConcerns::C_EPS_03_1;
#sourceTrace dependency need_source_MN_02_C_EPS_03_2 from MN_02 to FrameworkConcerns::C_EPS_03_2;
#sourceTrace dependency need_source_MN_02_C_EPS_04 from MN_02 to FrameworkConcerns::C_EPS_04;
#sourceTrace dependency need_source_MN_02_C_EPS_04_1 from MN_02 to FrameworkConcerns::C_EPS_04_1;
#sourceTrace dependency need_source_MN_02_C_EPS_04_1_1 from MN_02 to FrameworkConcerns::C_EPS_04_1_1;
#sourceTrace dependency need_source_MN_02_C_EPS_04_2 from MN_02 to FrameworkConcerns::C_EPS_04_2;
#sourceTrace dependency need_source_MN_02_C_EPS_05_2 from MN_02 to FrameworkConcerns::C_EPS_05_2;
#sourceTrace dependency need_source_MN_02_C_EPS_05_2_1 from MN_02 to FrameworkConcerns::C_EPS_05_2_1;
#sourceTrace dependency need_source_MN_02_C_EPS_05_4 from MN_02 to FrameworkConcerns::C_EPS_05_4;
#sourceTrace dependency need_source_MN_02_C_NE_01_2 from MN_02 to FrameworkConcerns::C_NE_01_2;
#sourceTrace dependency need_source_MN_02_C_NE_02_1 from MN_02 to FrameworkConcerns::C_NE_02_1;
requirement <'MN-03'> MN_03 { subject enterprise : EngineeringEnterprise; doc /* Maintain bills of materials and cost estimates across EPS candidate architectures and controlled design changes. */ }
@SourceRecord { identifier = "MN-03"; sourceText = "Maintain bills of materials and cost estimates across EPS candidate architectures and controlled design changes."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-03'> MR_03 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall obtain a revision-linked BOM and financial estimate for each designated EPS candidate, with sourced prices, quantities, assumptions, uncertainty, and missing cost data visible. */ }
@SourceRecord { identifier = "MR-03"; sourceText = "The enterprise shall obtain a revision-linked BOM and financial estimate for each designated EPS candidate, with sourced prices, quantities, assumptions, uncertainty, and missing cost data visible."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_03 from MR_03 to MN_03;
item <'MOE-03'> MOE_03 : FrameworkEvaluation { doc /* BOM and cost update effort (person-hours). Report differences from a reference BOM and estimate, missing priced items, and estimate uncertainty. This is separate from framework operating cost. */ }
#sourceTrace dependency measure_MN_03 from MOE_03 to MN_03;
#sourceTrace dependency need_source_MN_03_C_PM_02 from MN_03 to FrameworkConcerns::C_PM_02;
#sourceTrace dependency need_source_MN_03_C_PM_02_1 from MN_03 to FrameworkConcerns::C_PM_02_1;
#sourceTrace dependency need_source_MN_03_C_PM_02_1_1 from MN_03 to FrameworkConcerns::C_PM_02_1_1;
#sourceTrace dependency need_source_MN_03_C_PM_02_1_2 from MN_03 to FrameworkConcerns::C_PM_02_1_2;
#sourceTrace dependency need_source_MN_03_C_SE_03_2 from MN_03 to FrameworkConcerns::C_SE_03_2;
#sourceTrace dependency need_source_MN_03_C_EPS_01 from MN_03 to FrameworkConcerns::C_EPS_01;
#sourceTrace dependency need_source_MN_03_C_EPS_01_1 from MN_03 to FrameworkConcerns::C_EPS_01_1;
#sourceTrace dependency need_source_MN_03_C_EPS_04_2 from MN_03 to FrameworkConcerns::C_EPS_04_2;
requirement <'MN-04'> MN_04 { subject enterprise : EngineeringEnterprise; doc /* Assess dynamic mission loads, energy shortages, thermal and EMC concerns, subsystem interactions, component choices, and controller constraints before hardware fabrication. */ }
@SourceRecord { identifier = "MN-04"; sourceText = "Assess dynamic mission loads, energy shortages, thermal and EMC concerns, subsystem interactions, component choices, and controller constraints before hardware fabrication."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-04'> MR_04 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall justify designated early EPS decisions using time-dependent mission and component analyses with explicit interface conditions, applicable constraints, and unsupported checks visible. */ }
@SourceRecord { identifier = "MR-04"; sourceText = "The enterprise shall justify designated early EPS decisions using time-dependent mission and component analyses with explicit interface conditions, applicable constraints, and unsupported checks visible."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_04 from MR_04 to MN_04;
item <'MOE-04'> MOE_04 : FrameworkEvaluation { doc /* Coverage of decision-relevant checks and known issues found in reference fixtures. Report analysis turnaround and effort. Physical EPS defect reduction remains an empirical outcome outside framework acceptance. */ }
#sourceTrace dependency measure_MN_04 from MOE_04 to MN_04;
#sourceTrace dependency need_source_MN_04_C_PM_03 from MN_04 to FrameworkConcerns::C_PM_03;
#sourceTrace dependency need_source_MN_04_C_PM_03_1 from MN_04 to FrameworkConcerns::C_PM_03_1;
#sourceTrace dependency need_source_MN_04_C_PM_03_1_1 from MN_04 to FrameworkConcerns::C_PM_03_1_1;
#sourceTrace dependency need_source_MN_04_C_SE_03 from MN_04 to FrameworkConcerns::C_SE_03;
#sourceTrace dependency need_source_MN_04_C_SE_03_2 from MN_04 to FrameworkConcerns::C_SE_03_2;
#sourceTrace dependency need_source_MN_04_C_SE_03_3_1 from MN_04 to FrameworkConcerns::C_SE_03_3_1;
#sourceTrace dependency need_source_MN_04_C_SE_03_3_1_1 from MN_04 to FrameworkConcerns::C_SE_03_3_1_1;
#sourceTrace dependency need_source_MN_04_C_SE_03_3_1_2 from MN_04 to FrameworkConcerns::C_SE_03_3_1_2;
#sourceTrace dependency need_source_MN_04_C_SE_03_3_1_3 from MN_04 to FrameworkConcerns::C_SE_03_3_1_3;
#sourceTrace dependency need_source_MN_04_C_SE_03_3_1_3_1 from MN_04 to FrameworkConcerns::C_SE_03_3_1_3_1;
#sourceTrace dependency need_source_MN_04_C_SE_03_3_1_3_2 from MN_04 to FrameworkConcerns::C_SE_03_3_1_3_2;
#sourceTrace dependency need_source_MN_04_C_SE_06 from MN_04 to FrameworkConcerns::C_SE_06;
#sourceTrace dependency need_source_MN_04_C_SE_06_1 from MN_04 to FrameworkConcerns::C_SE_06_1;
#sourceTrace dependency need_source_MN_04_C_SE_06_2 from MN_04 to FrameworkConcerns::C_SE_06_2;
#sourceTrace dependency need_source_MN_04_C_EPS_01 from MN_04 to FrameworkConcerns::C_EPS_01;
#sourceTrace dependency need_source_MN_04_C_EPS_01_1 from MN_04 to FrameworkConcerns::C_EPS_01_1;
#sourceTrace dependency need_source_MN_04_C_EPS_01_1_1 from MN_04 to FrameworkConcerns::C_EPS_01_1_1;
#sourceTrace dependency need_source_MN_04_C_EPS_01_1_2 from MN_04 to FrameworkConcerns::C_EPS_01_1_2;
#sourceTrace dependency need_source_MN_04_C_EPS_01_1_3 from MN_04 to FrameworkConcerns::C_EPS_01_1_3;
#sourceTrace dependency need_source_MN_04_C_EPS_01_1_4 from MN_04 to FrameworkConcerns::C_EPS_01_1_4;
#sourceTrace dependency need_source_MN_04_C_EPS_01_1_5 from MN_04 to FrameworkConcerns::C_EPS_01_1_5;
#sourceTrace dependency need_source_MN_04_C_EPS_04_2 from MN_04 to FrameworkConcerns::C_EPS_04_2;
#sourceTrace dependency need_source_MN_04_C_EPS_04_4_4_2 from MN_04 to FrameworkConcerns::C_EPS_04_4_4_2;
#sourceTrace dependency need_source_MN_04_C_EPS_07 from MN_04 to FrameworkConcerns::C_EPS_07;
#sourceTrace dependency need_source_MN_04_C_EPS_07_1 from MN_04 to FrameworkConcerns::C_EPS_07_1;
#sourceTrace dependency need_source_MN_04_C_EPS_07_2 from MN_04 to FrameworkConcerns::C_EPS_07_2;
#sourceTrace dependency need_source_MN_04_C_NE_01 from MN_04 to FrameworkConcerns::C_NE_01;
#sourceTrace dependency need_source_MN_04_C_NE_01_1 from MN_04 to FrameworkConcerns::C_NE_01_1;
#sourceTrace dependency need_source_MN_04_C_NE_01_1_1 from MN_04 to FrameworkConcerns::C_NE_01_1_1;
#sourceTrace dependency need_source_MN_04_C_NE_01_1_2 from MN_04 to FrameworkConcerns::C_NE_01_1_2;
#sourceTrace dependency need_source_MN_04_C_TFT_01_4 from MN_04 to FrameworkConcerns::C_TFT_01_4;
#sourceTrace dependency need_source_MN_04_C_TFT_01_4_1 from MN_04 to FrameworkConcerns::C_TFT_01_4_1;
requirement <'MN-05'> MN_05 { subject enterprise : EngineeringEnterprise; doc /* Use EPS and battery models with documented calibration, validity domains, electrothermal and aging assumptions, uncertainty, and evidence appropriate to the intended decision. */ }
@SourceRecord { identifier = "MN-05"; sourceText = "Use EPS and battery models with documented calibration, validity domains, electrothermal and aging assumptions, uncertainty, and evidence appropriate to the intended decision."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-05'> MR_05 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall distinguish predictions supported within a documented model validity domain from extrapolation and shall distinguish a predicted control-policy benefit from a demonstrated hardware benefit. */ }
@SourceRecord { identifier = "MR-05"; sourceText = "The enterprise shall distinguish predictions supported within a documented model validity domain from extrapolation and shall distinguish a predicted control-policy benefit from a demonstrated hardware benefit."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_05 from MR_05 to MN_05;
item <'MOE-05'> MOE_05 : FrameworkEvaluation { doc /* Intended decisions covered by applicable model evidence. Report voltage, temperature, energy, health or lifetime residuals in their own units, uncertainty, runtime, and parameter-update delay. Limits require agreement for each intended use. */ }
#sourceTrace dependency measure_MN_05 from MOE_05 to MN_05;
#sourceTrace dependency need_source_MN_05_C_PM_03_1_1 from MN_05 to FrameworkConcerns::C_PM_03_1_1;
#sourceTrace dependency need_source_MN_05_C_SE_07_3 from MN_05 to FrameworkConcerns::C_SE_07_3;
#sourceTrace dependency need_source_MN_05_C_SE_08 from MN_05 to FrameworkConcerns::C_SE_08;
#sourceTrace dependency need_source_MN_05_C_SE_08_1 from MN_05 to FrameworkConcerns::C_SE_08_1;
#sourceTrace dependency need_source_MN_05_C_SE_08_2 from MN_05 to FrameworkConcerns::C_SE_08_2;
#sourceTrace dependency need_source_MN_05_C_SE_08_3 from MN_05 to FrameworkConcerns::C_SE_08_3;
#sourceTrace dependency need_source_MN_05_C_EPS_01_1_2 from MN_05 to FrameworkConcerns::C_EPS_01_1_2;
#sourceTrace dependency need_source_MN_05_C_EPS_01_1_3 from MN_05 to FrameworkConcerns::C_EPS_01_1_3;
#sourceTrace dependency need_source_MN_05_C_EPS_05 from MN_05 to FrameworkConcerns::C_EPS_05;
#sourceTrace dependency need_source_MN_05_C_EPS_05_1 from MN_05 to FrameworkConcerns::C_EPS_05_1;
#sourceTrace dependency need_source_MN_05_C_EPS_05_1_1 from MN_05 to FrameworkConcerns::C_EPS_05_1_1;
#sourceTrace dependency need_source_MN_05_C_EPS_05_2 from MN_05 to FrameworkConcerns::C_EPS_05_2;
#sourceTrace dependency need_source_MN_05_C_EPS_05_2_1 from MN_05 to FrameworkConcerns::C_EPS_05_2_1;
#sourceTrace dependency need_source_MN_05_C_EPS_05_3 from MN_05 to FrameworkConcerns::C_EPS_05_3;
#sourceTrace dependency need_source_MN_05_C_EPS_05_3_1 from MN_05 to FrameworkConcerns::C_EPS_05_3_1;
#sourceTrace dependency need_source_MN_05_C_EPS_06 from MN_05 to FrameworkConcerns::C_EPS_06;
#sourceTrace dependency need_source_MN_05_C_EPS_06_1 from MN_05 to FrameworkConcerns::C_EPS_06_1;
#sourceTrace dependency need_source_MN_05_C_EPS_06_2 from MN_05 to FrameworkConcerns::C_EPS_06_2;
#sourceTrace dependency need_source_MN_05_C_EPS_06_3 from MN_05 to FrameworkConcerns::C_EPS_06_3;
#sourceTrace dependency need_source_MN_05_C_EPS_07 from MN_05 to FrameworkConcerns::C_EPS_07;
#sourceTrace dependency need_source_MN_05_C_EPS_07_1 from MN_05 to FrameworkConcerns::C_EPS_07_1;
#sourceTrace dependency need_source_MN_05_C_EPS_07_2 from MN_05 to FrameworkConcerns::C_EPS_07_2;
#sourceTrace dependency need_source_MN_05_C_EPS_08 from MN_05 to FrameworkConcerns::C_EPS_08;
#sourceTrace dependency need_source_MN_05_C_EPS_08_1 from MN_05 to FrameworkConcerns::C_EPS_08_1;
#sourceTrace dependency need_source_MN_05_C_NE_02_5 from MN_05 to FrameworkConcerns::C_NE_02_5;
#sourceTrace dependency need_source_MN_05_C_NE_02_5_1 from MN_05 to FrameworkConcerns::C_NE_02_5_1;
#sourceTrace dependency need_source_MN_05_C_NE_02_5_2 from MN_05 to FrameworkConcerns::C_NE_02_5_2;
#sourceTrace dependency need_source_MN_05_C_TFT_02_4 from MN_05 to FrameworkConcerns::C_TFT_02_4;
#sourceTrace dependency need_source_MN_05_C_TFT_02_4_1 from MN_05 to FrameworkConcerns::C_TFT_02_4_1;
requirement <'MN-06'> MN_06 { subject enterprise : EngineeringEnterprise; doc /* Identify RAM variables in requirements and generate reusable RAM analysis models from the evolving EPS and spacecraft design. */ }
@SourceRecord { identifier = "MN-06"; sourceText = "Identify RAM variables in requirements and generate reusable RAM analysis models from the evolving EPS and spacecraft design."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-06'> MR_06 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall relate designated RAM claims to requirements, design failure dependencies, generated analysis models, input assumptions, and verification evidence or explicit gaps. */ }
@SourceRecord { identifier = "MR-06"; sourceText = "The enterprise shall relate designated RAM claims to requirements, design failure dependencies, generated analysis models, input assumptions, and verification evidence or explicit gaps."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_06 from MR_06 to MN_06;
item <'MOE-06'> MOE_06 : FrameworkEvaluation { doc /* RAM model preparation effort and coverage of the declared failure and requirement set. Report model generation differences from an expert reference. No framework verdict establishes achieved spacecraft RAM. */ }
#sourceTrace dependency measure_MN_06 from MOE_06 to MN_06;
#sourceTrace dependency need_source_MN_06_C_SE_05 from MN_06 to FrameworkConcerns::C_SE_05;
#sourceTrace dependency need_source_MN_06_C_SE_05_1 from MN_06 to FrameworkConcerns::C_SE_05_1;
#sourceTrace dependency need_source_MN_06_C_SE_05_2 from MN_06 to FrameworkConcerns::C_SE_05_2;
#sourceTrace dependency need_source_MN_06_C_SE_05_2_1 from MN_06 to FrameworkConcerns::C_SE_05_2_1;
#sourceTrace dependency need_source_MN_06_C_SE_05_2_1_1 from MN_06 to FrameworkConcerns::C_SE_05_2_1_1;
#sourceTrace dependency need_source_MN_06_C_SE_05_2_1_2 from MN_06 to FrameworkConcerns::C_SE_05_2_1_2;
#sourceTrace dependency need_source_MN_06_C_SE_05_2_1_2_1 from MN_06 to FrameworkConcerns::C_SE_05_2_1_2_1;
requirement <'MN-07'> MN_07 { subject enterprise : EngineeringEnterprise; doc /* Define EPS and component verification activities with usable procedures, conditions, equipment and DUT interfaces, safety information, observable variables, and valid synchronized telemetry. */ }
@SourceRecord { identifier = "MN-07"; sourceText = "Define EPS and component verification activities with usable procedures, conditions, equipment and DUT interfaces, safety information, observable variables, and valid synchronized telemetry."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-07'> MR_07 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall provide a reviewable verification proposal and evidence contract for each designated activity, with feasibility and safety decisions reserved to the responsible engineers and testing facility. */ }
@SourceRecord { identifier = "MR-07"; sourceText = "The enterprise shall provide a reviewable verification proposal and evidence contract for each designated activity, with feasibility and safety decisions reserved to the responsible engineers and testing facility."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_07 from MR_07 to MN_07;
item <'MOE-07'> MOE_07 : FrameworkEvaluation { doc /* Proposal preparation and technician clarification effort. Report missing proposal fields, evidence completeness, invalid samples, and synchronization uncertainty. Physical fault limits and timing tolerances require facility agreement. */ }
#sourceTrace dependency measure_MN_07 from MOE_07 to MN_07;
#sourceTrace dependency need_source_MN_07_C_SE_03_4 from MN_07 to FrameworkConcerns::C_SE_03_4;
#sourceTrace dependency need_source_MN_07_C_SE_03_4_1 from MN_07 to FrameworkConcerns::C_SE_03_4_1;
#sourceTrace dependency need_source_MN_07_C_SE_03_4_2 from MN_07 to FrameworkConcerns::C_SE_03_4_2;
#sourceTrace dependency need_source_MN_07_C_SE_03_4_3 from MN_07 to FrameworkConcerns::C_SE_03_4_3;
#sourceTrace dependency need_source_MN_07_C_SE_03_4_3_1 from MN_07 to FrameworkConcerns::C_SE_03_4_3_1;
#sourceTrace dependency need_source_MN_07_C_SE_05_2 from MN_07 to FrameworkConcerns::C_SE_05_2;
#sourceTrace dependency need_source_MN_07_C_SE_05_2_1 from MN_07 to FrameworkConcerns::C_SE_05_2_1;
#sourceTrace dependency need_source_MN_07_C_SE_05_2_1_1 from MN_07 to FrameworkConcerns::C_SE_05_2_1_1;
#sourceTrace dependency need_source_MN_07_C_EPS_01_1_4 from MN_07 to FrameworkConcerns::C_EPS_01_1_4;
#sourceTrace dependency need_source_MN_07_C_EPS_01_1_5 from MN_07 to FrameworkConcerns::C_EPS_01_1_5;
#sourceTrace dependency need_source_MN_07_C_EPS_03 from MN_07 to FrameworkConcerns::C_EPS_03;
#sourceTrace dependency need_source_MN_07_C_EPS_03_1 from MN_07 to FrameworkConcerns::C_EPS_03_1;
#sourceTrace dependency need_source_MN_07_C_EPS_03_2 from MN_07 to FrameworkConcerns::C_EPS_03_2;
#sourceTrace dependency need_source_MN_07_C_EPS_04_3 from MN_07 to FrameworkConcerns::C_EPS_04_3;
#sourceTrace dependency need_source_MN_07_C_EPS_04_3_1 from MN_07 to FrameworkConcerns::C_EPS_04_3_1;
#sourceTrace dependency need_source_MN_07_C_EPS_04_3_2 from MN_07 to FrameworkConcerns::C_EPS_04_3_2;
#sourceTrace dependency need_source_MN_07_C_EPS_04_4 from MN_07 to FrameworkConcerns::C_EPS_04_4;
#sourceTrace dependency need_source_MN_07_C_EPS_04_4_1 from MN_07 to FrameworkConcerns::C_EPS_04_4_1;
#sourceTrace dependency need_source_MN_07_C_EPS_04_4_2 from MN_07 to FrameworkConcerns::C_EPS_04_4_2;
#sourceTrace dependency need_source_MN_07_C_EPS_04_4_3 from MN_07 to FrameworkConcerns::C_EPS_04_4_3;
#sourceTrace dependency need_source_MN_07_C_EPS_04_4_3_1 from MN_07 to FrameworkConcerns::C_EPS_04_4_3_1;
#sourceTrace dependency need_source_MN_07_C_EPS_04_4_4 from MN_07 to FrameworkConcerns::C_EPS_04_4_4;
#sourceTrace dependency need_source_MN_07_C_EPS_04_4_4_1 from MN_07 to FrameworkConcerns::C_EPS_04_4_4_1;
#sourceTrace dependency need_source_MN_07_C_EPS_04_4_4_2 from MN_07 to FrameworkConcerns::C_EPS_04_4_4_2;
#sourceTrace dependency need_source_MN_07_C_NE_01 from MN_07 to FrameworkConcerns::C_NE_01;
#sourceTrace dependency need_source_MN_07_C_NE_01_1 from MN_07 to FrameworkConcerns::C_NE_01_1;
#sourceTrace dependency need_source_MN_07_C_TFT_01 from MN_07 to FrameworkConcerns::C_TFT_01;
#sourceTrace dependency need_source_MN_07_C_TFT_01_1 from MN_07 to FrameworkConcerns::C_TFT_01_1;
#sourceTrace dependency need_source_MN_07_C_TFT_01_2 from MN_07 to FrameworkConcerns::C_TFT_01_2;
#sourceTrace dependency need_source_MN_07_C_TFT_01_3 from MN_07 to FrameworkConcerns::C_TFT_01_3;
#sourceTrace dependency need_source_MN_07_C_TFT_01_4 from MN_07 to FrameworkConcerns::C_TFT_01_4;
#sourceTrace dependency need_source_MN_07_C_TFT_01_4_1 from MN_07 to FrameworkConcerns::C_TFT_01_4_1;
#sourceTrace dependency need_source_MN_07_C_TFT_02 from MN_07 to FrameworkConcerns::C_TFT_02;
#sourceTrace dependency need_source_MN_07_C_TFT_02_1 from MN_07 to FrameworkConcerns::C_TFT_02_1;
#sourceTrace dependency need_source_MN_07_C_TFT_02_2 from MN_07 to FrameworkConcerns::C_TFT_02_2;
#sourceTrace dependency need_source_MN_07_C_TFT_02_3 from MN_07 to FrameworkConcerns::C_TFT_02_3;
#sourceTrace dependency need_source_MN_07_C_TFT_02_3_1 from MN_07 to FrameworkConcerns::C_TFT_02_3_1;
#sourceTrace dependency need_source_MN_07_C_TFT_02_4 from MN_07 to FrameworkConcerns::C_TFT_02_4;
#sourceTrace dependency need_source_MN_07_C_TFT_02_4_1 from MN_07 to FrameworkConcerns::C_TFT_02_4_1;
requirement <'MN-08'> MN_08 { subject enterprise : EngineeringEnterprise; doc /* Keep command, telemetry, event, parameter, mode and recovery definitions consistent with EPS hardware and support cFS and F-Prime mappings and target resource assessment. */ }
@SourceRecord { identifier = "MN-08"; sourceText = "Keep command, telemetry, event, parameter, mode and recovery definitions consistent with EPS hardware and support cFS and F-Prime mappings and target resource assessment."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-08'> MR_08 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall produce revision-linked EPS software integration contracts, framework-specific mappings, command and mode checks, and processor, memory, timing and power evidence for the declared target configuration. */ }
@SourceRecord { identifier = "MR-08"; sourceText = "The enterprise shall produce revision-linked EPS software integration contracts, framework-specific mappings, command and mode checks, and processor, memory, timing and power evidence for the declared target configuration."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_08 from MR_08 to MN_08;
item <'MOE-08'> MOE_08 : FrameworkEvaluation { doc /* Interface discrepancy detection and integration effort on common reference fixtures. Report dictionary and behavior coverage, configuration compatibility status, and target resource estimates or measurements. Unverified target deployment stays explicit. */ }
#sourceTrace dependency measure_MN_08 from MOE_08 to MN_08;
#sourceTrace dependency need_source_MN_08_C_SE_09 from MN_08 to FrameworkConcerns::C_SE_09;
#sourceTrace dependency need_source_MN_08_C_SE_09_1 from MN_08 to FrameworkConcerns::C_SE_09_1;
#sourceTrace dependency need_source_MN_08_C_SE_09_2 from MN_08 to FrameworkConcerns::C_SE_09_2;
#sourceTrace dependency need_source_MN_08_C_SE_09_2_1 from MN_08 to FrameworkConcerns::C_SE_09_2_1;
#sourceTrace dependency need_source_MN_08_C_SE_09_3 from MN_08 to FrameworkConcerns::C_SE_09_3;
#sourceTrace dependency need_source_MN_08_C_SE_10 from MN_08 to FrameworkConcerns::C_SE_10;
#sourceTrace dependency need_source_MN_08_C_SE_10_1 from MN_08 to FrameworkConcerns::C_SE_10_1;
#sourceTrace dependency need_source_MN_08_C_SE_10_2 from MN_08 to FrameworkConcerns::C_SE_10_2;
#sourceTrace dependency need_source_MN_08_C_EPS_09 from MN_08 to FrameworkConcerns::C_EPS_09;
#sourceTrace dependency need_source_MN_08_C_EPS_09_1 from MN_08 to FrameworkConcerns::C_EPS_09_1;
#sourceTrace dependency need_source_MN_08_C_EPS_09_2 from MN_08 to FrameworkConcerns::C_EPS_09_2;
#sourceTrace dependency need_source_MN_08_C_EPS_10 from MN_08 to FrameworkConcerns::C_EPS_10;
#sourceTrace dependency need_source_MN_08_C_EPS_10_1 from MN_08 to FrameworkConcerns::C_EPS_10_1;
#sourceTrace dependency need_source_MN_08_C_NE_01_1_2 from MN_08 to FrameworkConcerns::C_NE_01_1_2;
#sourceTrace dependency need_source_MN_08_C_NE_02 from MN_08 to FrameworkConcerns::C_NE_02;
#sourceTrace dependency need_source_MN_08_C_NE_02_1 from MN_08 to FrameworkConcerns::C_NE_02_1;
#sourceTrace dependency need_source_MN_08_C_NE_02_2 from MN_08 to FrameworkConcerns::C_NE_02_2;
#sourceTrace dependency need_source_MN_08_C_NE_02_3 from MN_08 to FrameworkConcerns::C_NE_02_3;
#sourceTrace dependency need_source_MN_08_C_NE_02_3_1 from MN_08 to FrameworkConcerns::C_NE_02_3_1;
#sourceTrace dependency need_source_MN_08_C_NE_02_4 from MN_08 to FrameworkConcerns::C_NE_02_4;
#sourceTrace dependency need_source_MN_08_C_NE_02_4_1 from MN_08 to FrameworkConcerns::C_NE_02_4_1;
#sourceTrace dependency need_source_MN_08_C_NE_02_4_2 from MN_08 to FrameworkConcerns::C_NE_02_4_2;
#sourceTrace dependency need_source_MN_08_C_NE_02_5 from MN_08 to FrameworkConcerns::C_NE_02_5;
#sourceTrace dependency need_source_MN_08_C_NE_02_5_1 from MN_08 to FrameworkConcerns::C_NE_02_5_1;
#sourceTrace dependency need_source_MN_08_C_NE_02_5_2 from MN_08 to FrameworkConcerns::C_NE_02_5_2;
requirement <'MN-09'> MN_09 { subject enterprise : EngineeringEnterprise; doc /* Enable independent reproduction and reuse of early EPS analysis and later supplied measurements without losing configuration or validity context. */ }
@SourceRecord { identifier = "MN-09"; sourceText = "Enable independent reproduction and reuse of early EPS analysis and later supplied measurements without losing configuration or validity context."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-09'> MR_09 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall permit an independent participant to reconstruct each designated analysis from its controlled baseline and evaluate agreement using result-specific comparison rules fixed before execution. */ }
@SourceRecord { identifier = "MR-09"; sourceText = "The enterprise shall permit an independent participant to reconstruct each designated analysis from its controlled baseline and evaluate agreement using result-specific comparison rules fixed before execution."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_09 from MR_09 to MN_09;
item <'MOE-09'> MOE_09 : FrameworkEvaluation { doc /* Successful designated reproductions / attempted designated reproductions, independent active effort, and reconstruction gaps. Agreement limits are result-specific. Reduced use of physical replicas is a future hypothesis. */ }
#sourceTrace dependency measure_MN_09 from MOE_09 to MN_09;
#sourceTrace dependency need_source_MN_09_C_PM_04 from MN_09 to FrameworkConcerns::C_PM_04;
#sourceTrace dependency need_source_MN_09_C_PM_05_1 from MN_09 to FrameworkConcerns::C_PM_05_1;
#sourceTrace dependency need_source_MN_09_C_SE_07 from MN_09 to FrameworkConcerns::C_SE_07;
#sourceTrace dependency need_source_MN_09_C_SE_07_2 from MN_09 to FrameworkConcerns::C_SE_07_2;
#sourceTrace dependency need_source_MN_09_C_EPS_05_4 from MN_09 to FrameworkConcerns::C_EPS_05_4;
#sourceTrace dependency need_source_MN_09_C_NE_01_2 from MN_09 to FrameworkConcerns::C_NE_01_2;
requirement <'MN-10'> MN_10 { subject enterprise : EngineeringEnterprise; doc /* Provide readable design views and requirement-to-design-to-evidence reviews with visible assumptions, limitations, and finding dispositions. */ }
@SourceRecord { identifier = "MN-10"; sourceText = "Provide readable design views and requirement-to-design-to-evidence reviews with visible assumptions, limitations, and finding dispositions."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-10'> MR_10 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall provide a controlled review package from which a reviewer can locate the designated design, decision rationale, applicable evidence, and unresolved findings. */ }
@SourceRecord { identifier = "MR-10"; sourceText = "The enterprise shall provide a controlled review package from which a reviewer can locate the designated design, decision rationale, applicable evidence, and unresolved findings."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_10 from MR_10 to MN_10;
item <'MOE-10'> MOE_10 : FrameworkEvaluation { doc /* Review preparation effort and reviewer task completion, interpretation accuracy, and clarification effort on a fixed task set. Readability needs a reviewer protocol, not an invented visual score. */ }
#sourceTrace dependency measure_MN_10 from MOE_10 to MN_10;
#sourceTrace dependency need_source_MN_10_C_SE_02 from MN_10 to FrameworkConcerns::C_SE_02;
#sourceTrace dependency need_source_MN_10_C_SE_02_1 from MN_10 to FrameworkConcerns::C_SE_02_1;
#sourceTrace dependency need_source_MN_10_C_EPS_11 from MN_10 to FrameworkConcerns::C_EPS_11;
#sourceTrace dependency need_source_MN_10_C_EPS_11_1 from MN_10 to FrameworkConcerns::C_EPS_11_1;
requirement <'MN-11'> MN_11 { subject enterprise : EngineeringEnterprise; doc /* Provide a declared minimum environment, learning path and reusable core suitable for contrasting EPS contexts, with adoption, adaptation and direct operating burdens visible. */ }
@SourceRecord { identifier = "MN-11"; sourceText = "Provide a declared minimum environment, learning path and reusable core suitable for contrasting EPS contexts, with adoption, adaptation and direct operating burdens visible."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
requirement <'MR-11'> MR_11 { subject enterprise : EngineeringEnterprise; doc /* The enterprise shall complete the declared reference workflow in two contrasting EPS cases using an identified common core, declared case adaptations, and independently reconstructable environment instructions. */ }
@SourceRecord { identifier = "MR-11"; sourceText = "The enterprise shall complete the declared reference workflow in two contrasting EPS cases using an identified common core, declared case adaptations, and independently reconstructable environment instructions."; sourceLocator = "final_report/traceability/framework-baseline.json"; status = "author-reviewed derivation; stakeholder approval and empirical verification pending"; citationRecord = ""; }
#proposedDerivation dependency need_MN_11 from MR_11 to MN_11;
item <'MOE-11'> MOE_11 : FrameworkEvaluation { doc /* Adoption and case adaptation effort (active person-hours), direct framework cost (CAD over a declared period), and case completion status. Report required computing, licenses and services. Resource ceilings require stakeholder agreement. */ }
#sourceTrace dependency measure_MN_11 from MOE_11 to MN_11;
#sourceTrace dependency need_source_MN_11_C_PM_01 from MN_11 to FrameworkConcerns::C_PM_01;
#sourceTrace dependency need_source_MN_11_C_PM_01_1 from MN_11 to FrameworkConcerns::C_PM_01_1;
#sourceTrace dependency need_source_MN_11_C_PM_01_2 from MN_11 to FrameworkConcerns::C_PM_01_2;
#sourceTrace dependency need_source_MN_11_C_PM_05 from MN_11 to FrameworkConcerns::C_PM_05;
#sourceTrace dependency need_source_MN_11_C_SE_01_1 from MN_11 to FrameworkConcerns::C_SE_01_1;
#sourceTrace dependency need_source_MN_11_C_SE_01_1_1 from MN_11 to FrameworkConcerns::C_SE_01_1_1;
#sourceTrace dependency need_source_MN_11_C_EPS_02_1 from MN_11 to FrameworkConcerns::C_EPS_02_1;
#sourceTrace dependency need_source_MN_11_C_NE_02 from MN_11 to FrameworkConcerns::C_NE_02;
#sourceTrace dependency need_source_MN_11_C_NE_02_4 from MN_11 to FrameworkConcerns::C_NE_02_4;
#sourceTrace dependency need_source_MN_11_C_NE_02_4_1 from MN_11 to FrameworkConcerns::C_NE_02_4_1;
#sourceTrace dependency need_source_MN_11_C_NE_02_4_2 from MN_11 to FrameworkConcerns::C_NE_02_4_2;
item reported_as_is_context_1 : EngineeringArtifact { doc /* ASCEND is associated with student rocketry and avionics teams. The club uses tasks approved by senior members and PDR, CDR and FRR gates.
Exact baseline excerpt:
ASCEND is currently associated to a Rocketry Team and an Avionics Team of a student club.
The Rocketry Team operates on requirements given by Rocketry Competition Organizers.
The requirements are stated in terms of the target maximum height or maximum acceleration of the rocket.
One competition imposed the requirement of launching and returning to ground an egg without breaking it, which can only be validated via demonstration.
The Team Captains convert the requirements of a competition to atomic tasks.
Tasks are performed by any club member and approved by senior members.
The club performs the PDR, CDR, and FRR review gates. */ }
@SourceRecord { identifier = "OBS-01"; sourceText = "ASCEND is associated with student rocketry and avionics teams. The club uses tasks approved by senior members and PDR, CDR and FRR gates.\nExact baseline excerpt:\nASCEND is currently associated to a Rocketry Team and an Avionics Team of a student club.\nThe Rocketry Team operates on requirements given by Rocketry Competition Organizers.\nThe requirements are stated in terms of the target maximum height or maximum acceleration of the rocket.\nOne competition imposed the requirement of launching and returning to ground an egg without breaking it, which can only be validated via demonstration.\nThe Team Captains convert the requirements of a competition to atomic tasks.\nTasks are performed by any club member and approved by senior members.\nThe club performs the PDR, CDR, and FRR review gates."; sourceLocator = "{\"path\": \"final_report/solucion.tex\", \"lines\": [193, 199], \"baseline_head\": \"b826d9915407bbd861d8d39b2558048f3d534bdc\"}"; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item reported_as_is_context_2 : EngineeringArtifact { doc /* Observed club development emphasizes reuse and atomic edits. Battery sizing used component datasheet on/off power and estimated duty cycles.
Exact baseline excerpt:
There is a large emphasis on technology reuse at the club, so most tasks are formulated as atomic edits to existing designs.
Furthermore, most of the tasks for a particular competition involve development activities like PCB manufacturing, soldering, and assembly.
One observed task involved adding a COTS to a PCB, which was specified in the task title. The task was broken down into subtasks, one of which required to connect a capacitor to the COTS, possibly prescribed by its datasheet.

The competition requirements include the radio communications technologies allowed for rocket launch commands and telemetry.
Thus, radio transceivers are some of the first COTS chosen for rocket designs.
The egg mission also introduced a payload consisting of 1U unit with a mechanically damping material to protect the egg, and heat pumps to maintain its temperature within a range inspired by an incubator machine.

Multiple lithium-ion cells were used to power the latest revision of the egg incubator payload.
To size them, a power budget was generated by consulting the datasheets of the already chosen components and extracting "on" and "off" power consumption values, then estimating the duty cycle of each component for one launch.
The duty cycle of telemetry components is estimated from the telemetry frequency requirements of the competition. For the rest of the components, it is conservatively assumed that they are always on. */ }
@SourceRecord { identifier = "OBS-02"; sourceText = "Observed club development emphasizes reuse and atomic edits. Battery sizing used component datasheet on/off power and estimated duty cycles.\nExact baseline excerpt:\nThere is a large emphasis on technology reuse at the club, so most tasks are formulated as atomic edits to existing designs.\nFurthermore, most of the tasks for a particular competition involve development activities like PCB manufacturing, soldering, and assembly.\nOne observed task involved adding a COTS to a PCB, which was specified in the task title. The task was broken down into subtasks, one of which required to connect a capacitor to the COTS, possibly prescribed by its datasheet.\n\nThe competition requirements include the radio communications technologies allowed for rocket launch commands and telemetry.\nThus, radio transceivers are some of the first COTS chosen for rocket designs.\nThe egg mission also introduced a payload consisting of 1U unit with a mechanically damping material to protect the egg, and heat pumps to maintain its temperature within a range inspired by an incubator machine.\n\nMultiple lithium-ion cells were used to power the latest revision of the egg incubator payload.\nTo size them, a power budget was generated by consulting the datasheets of the already chosen components and extracting \"on\" and \"off\" power consumption values, then estimating the duty cycle of each component for one launch.\nThe duty cycle of telemetry components is estimated from the telemetry frequency requirements of the competition. For the rest of the components, it is conservatively assumed that they are always on."; sourceLocator = "{\"path\": \"final_report/solucion.tex\", \"lines\": [201, 211], \"baseline_head\": \"b826d9915407bbd861d8d39b2558048f3d534bdc\"}"; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item reported_as_is_context_3 : EngineeringArtifact { doc /* Observed payload power interfaces and battery endurance checks used assembled hardware, realistic telemetry and a controlled temperature environment.
Exact baseline excerpt:
A PCB design was observed consisting of multiple boards connected perpendicularly via PCI to a backplane that was the size of a 1U face.
Status indicator LEDs were observed for 3.3 and 5 volt buses.
The power source of the payload is verified experimentally.
The payload is fully assembled and set to provide telemetry at a realistic frequency while powered by the battery.
It is then inserted into a temperature controlled environment like a refrigerator so the heat pumps can be observed under representative operation conditions, and left to operate until the battery power runs out.
If the time from experiment start to power depletion is greater than the mission period, the power requirements are taken to be verified.
In practice, the battery life is several times larger than the mission period. */ }
@SourceRecord { identifier = "OBS-03"; sourceText = "Observed payload power interfaces and battery endurance checks used assembled hardware, realistic telemetry and a controlled temperature environment.\nExact baseline excerpt:\nA PCB design was observed consisting of multiple boards connected perpendicularly via PCI to a backplane that was the size of a 1U face.\nStatus indicator LEDs were observed for 3.3 and 5 volt buses.\nThe power source of the payload is verified experimentally.\nThe payload is fully assembled and set to provide telemetry at a realistic frequency while powered by the battery.\nIt is then inserted into a temperature controlled environment like a refrigerator so the heat pumps can be observed under representative operation conditions, and left to operate until the battery power runs out.\nIf the time from experiment start to power depletion is greater than the mission period, the power requirements are taken to be verified.\nIn practice, the battery life is several times larger than the mission period."; sourceLocator = "{\"path\": \"final_report/solucion.tex\", \"lines\": [213, 219], \"baseline_head\": \"b826d9915407bbd861d8d39b2558048f3d534bdc\"}"; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item reported_as_is_context_4 : EngineeringArtifact { doc /* The egg payload uses measured accelerations and drops for damping iteration. OpenRocket analyses support rocket height and acceleration checks before development.
Exact baseline excerpt:
The demonstratable requirement to protect an egg has been related to the measurable variable of acceleration in the egg chamber. An IMU was placed inside this chamber, which is mechanically damped, and another in a rigid point of the payload chassis.
The difference in acceleration between the two IMUs during realistic launches is analyzed to iterative on the damping design.
Launches are recreated by manually dropping the payload from a representative height.
The drop data, and naturally an inspection of the egg, is used to characterize the damping as "too soft" or "too hard".

Maximum rocket height and maximum rocket acceleration requirements are verified at the design phase using the OpenRocket software.
This software works with abstract representations of rocket components (nose, stages, etc.) can be parametrized, combined, and then simulated.
Rocket height and acceleration requirements are taken to be verified based on the results of the simulatins, and only then does development start. */ }
@SourceRecord { identifier = "OBS-04"; sourceText = "The egg payload uses measured accelerations and drops for damping iteration. OpenRocket analyses support rocket height and acceleration checks before development.\nExact baseline excerpt:\nThe demonstratable requirement to protect an egg has been related to the measurable variable of acceleration in the egg chamber. An IMU was placed inside this chamber, which is mechanically damped, and another in a rigid point of the payload chassis.\nThe difference in acceleration between the two IMUs during realistic launches is analyzed to iterative on the damping design.\nLaunches are recreated by manually dropping the payload from a representative height.\nThe drop data, and naturally an inspection of the egg, is used to characterize the damping as \"too soft\" or \"too hard\".\n\nMaximum rocket height and maximum rocket acceleration requirements are verified at the design phase using the OpenRocket software.\nThis software works with abstract representations of rocket components (nose, stages, etc.) can be parametrized, combined, and then simulated.\nRocket height and acceleration requirements are taken to be verified based on the results of the simulatins, and only then does development start."; sourceLocator = "{\"path\": \"final_report/solucion.tex\", \"lines\": [221, 228], \"baseline_head\": \"b826d9915407bbd861d8d39b2558048f3d534bdc\"}"; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item reported_as_is_context_5 : EngineeringArtifact { doc /* The club reports about two months of onboarding. ASCEND researchers report nine months on one EPS requirements-to-high-level-design iteration.
Exact baseline excerpt:
The club reports that it takes about 2 months to onboard new members to the point where they can complete tasks.
Separately, ASCEND researchers have spent 9 months on one iteration of an EPS design following a more traditional systems engineering approach, starting from requirements and currently advenced up to high-level design, with a power budget completed and battery and panel options compared but no component selections yet. */ }
@SourceRecord { identifier = "OBS-05"; sourceText = "The club reports about two months of onboarding. ASCEND researchers report nine months on one EPS requirements-to-high-level-design iteration.\nExact baseline excerpt:\nThe club reports that it takes about 2 months to onboard new members to the point where they can complete tasks.\nSeparately, ASCEND researchers have spent 9 months on one iteration of an EPS design following a more traditional systems engineering approach, starting from requirements and currently advenced up to high-level design, with a power budget completed and battery and panel options compared but no component selections yet."; sourceLocator = "{\"path\": \"final_report/solucion.tex\", \"lines\": [230, 231], \"baseline_head\": \"b826d9915407bbd861d8d39b2558048f3d534bdc\"}"; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item intro_context_1 : EngineeringArtifact { doc /* Early EPS evidence fragmentation hinders traceability, reproducibility and issue detection.
Exact baseline excerpt:
Evidence fragmentation during the early lifecycle phases of nanosatellite electrical power systems hinders the traceability between needs and requirements, architecture decisions, and the analytical evidence that supports them. Furthermore, it hinfers the reproducibility of analyses and the capability to detect design inconsistencies before advacing to physical verification and validation phases. */ }
@SourceRecord { identifier = "CTX-01"; sourceText = "Early EPS evidence fragmentation hinders traceability, reproducibility and issue detection.\nExact baseline excerpt:\nEvidence fragmentation during the early lifecycle phases of nanosatellite electrical power systems hinders the traceability between needs and requirements, architecture decisions, and the analytical evidence that supports them. Furthermore, it hinfers the reproducibility of analyses and the capability to detect design inconsistencies before advacing to physical verification and validation phases."; sourceLocator = "\"final_report/intro.tex\""; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item intro_context_2 : EngineeringArtifact { doc /* Characterize EPS needs, requirements, interfaces and criteria. Define framework flow. Provide generic EPS functions, logical/physical elements, modes/states and requirements. Characterize early EPS V&V. Evaluate two contrasting cases.
Exact baseline excerpt:
An MBSE framework is defined following Buruso et al. \cite{buruso2026modelbased} as the integration of MBSE methods, MBSE languages, and MBSE tools within and throughout the relevant lifecycle phases. The secondary objectives of this project are: to characterize the needs, requirements, interfaces and technical criteria of nanosatellite EPS; to define the operational flow of modeling, analysis, and evidence management of the MBSE framework; to model a generic EPS architecture with functions, logical and physical components, interfaces, modes and states, and requirements; to characterize early EPS verification and validation within the EPS framework; to evaluate the framework on two contrasting EPS case studies. */ }
@SourceRecord { identifier = "CTX-02"; sourceText = "Characterize EPS needs, requirements, interfaces and criteria. Define framework flow. Provide generic EPS functions, logical/physical elements, modes/states and requirements. Characterize early EPS V&V. Evaluate two contrasting cases.\nExact baseline excerpt:\nAn MBSE framework is defined following Buruso et al. \\cite{buruso2026modelbased} as the integration of MBSE methods, MBSE languages, and MBSE tools within and throughout the relevant lifecycle phases. The secondary objectives of this project are: to characterize the needs, requirements, interfaces and technical criteria of nanosatellite EPS; to define the operational flow of modeling, analysis, and evidence management of the MBSE framework; to model a generic EPS architecture with functions, logical and physical components, interfaces, modes and states, and requirements; to characterize early EPS verification and validation within the EPS framework; to evaluate the framework on two contrasting EPS case studies."; sourceLocator = "\"final_report/intro.tex\""; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item intro_context_3 : EngineeringArtifact { doc /* Verify evidence chains, reproduction, discrepancy handling and two-case reuse. Measure correct change time, adaptation/reproduction/adoption effort, direct cost and detection accuracy against a qualified person.
Exact baseline excerpt:
It will be verified that the framework satifies the requirements imposed on it, including, among other, to maintaince valid evidence chains, to reproduce EPS analyses, identify and manage critical discrepancies, and to complete the two case studies without introducing post hoc modifications to the framework.
The fulfillment of requirements is associated to quantitative metrics, which include the time taken to correctly process a change, the effort (person-hours) required to adapt the framework to a case study, the effort needed to reproduce an analysis independently, adoption effort, direct usage cost, and the accuracy to detect inconsistencies (compared to a qualified person).
The two case studies will allow to determine whether the same framework core can be applied to contrasting EPS configurations, preserving the traceability and reproducibility of the generated evidence. */ }
@SourceRecord { identifier = "CTX-03"; sourceText = "Verify evidence chains, reproduction, discrepancy handling and two-case reuse. Measure correct change time, adaptation/reproduction/adoption effort, direct cost and detection accuracy against a qualified person.\nExact baseline excerpt:\nIt will be verified that the framework satifies the requirements imposed on it, including, among other, to maintaince valid evidence chains, to reproduce EPS analyses, identify and manage critical discrepancies, and to complete the two case studies without introducing post hoc modifications to the framework.\nThe fulfillment of requirements is associated to quantitative metrics, which include the time taken to correctly process a change, the effort (person-hours) required to adapt the framework to a case study, the effort needed to reproduce an analysis independently, adoption effort, direct usage cost, and the accuracy to detect inconsistencies (compared to a qualified person).\nThe two case studies will allow to determine whether the same framework core can be applied to contrasting EPS configurations, preserving the traceability and reproducibility of the generated evidence."; sourceLocator = "\"final_report/intro.tex\""; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item additional_source_context_1 : EngineeringArtifact { doc /* The current project is intended as a precedent for that large-scale ambition, covering the electrical power subsystem in its lifecycle phases prior to commissiong or developing hardware (early phases), and is founded in the experience gained in previous EPS design efforts at ASCEND. Therefore, the particular problem addressed by this project is: */ }
@SourceRecord { identifier = "CTX-04"; sourceText = "The current project is intended as a precedent for that large-scale ambition, covering the electrical power subsystem in its lifecycle phases prior to commissiong or developing hardware (early phases), and is founded in the experience gained in previous EPS design efforts at ASCEND. Therefore, the particular problem addressed by this project is:"; sourceLocator = "\"final_report/intro.tex\""; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item additional_source_context_2 : EngineeringArtifact { doc /* The lifecycle of the framework, which crucially must be distinguished from the lifecycle of its EPS system of interest, follows the Object-Oriented Systems Engineering Methodology (OOSEM) \cite{friedenthal2014practical}. The engineering process is formalized by using the Systems Modeling Language version 2 (SysML v2) to represent requirements and their solution. Candidate solutions remain free to implement other methods, languages, formats, and tools as part of their behavior. */ }
@SourceRecord { identifier = "CTX-05"; sourceText = "The lifecycle of the framework, which crucially must be distinguished from the lifecycle of its EPS system of interest, follows the Object-Oriented Systems Engineering Methodology (OOSEM) \\cite{friedenthal2014practical}. The engineering process is formalized by using the Systems Modeling Language version 2 (SysML v2) to represent requirements and their solution. Candidate solutions remain free to implement other methods, languages, formats, and tools as part of their behavior."; sourceLocator = "\"final_report/intro.tex\""; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item additional_source_context_3 : EngineeringArtifact { doc /* A project proposal was written before a complete understanding of the stakeholders' needs was achieved. Said proposal defined objectives, deliverables, indicators, and deadlines that form the research contribution baseline, without specifying the framework itself.
The assessment of the objective deliverables against their indicators and deadlines will be carried out separately from the framework integration and verification that happens within OOSEM (Section \ref{section:integrate-and-verify-system}). */ }
@SourceRecord { identifier = "CTX-06"; sourceText = "A project proposal was written before a complete understanding of the stakeholders' needs was achieved. Said proposal defined objectives, deliverables, indicators, and deadlines that form the research contribution baseline, without specifying the framework itself.\nThe assessment of the objective deliverables against their indicators and deadlines will be carried out separately from the framework integration and verification that happens within OOSEM (Section \\ref{section:integrate-and-verify-system})."; sourceLocator = "\"final_report/solucion.tex\""; status = "reported baseline context; scoped observations only"; citationRecord = ""; }
item <'EX-01'> EX_01 : EngineeringArtifact { doc /* Candidate count, design-change frequency, and failed external verification gates are inputs and external drivers. The framework manages impact and evidence. It cannot guarantee fewer changes or gates. */ }
item <'EX-02'> EX_02 : EngineeringArtifact { doc /* Redesign cost, actual thermal/EMC/power defects, and hardware fabrication are external outcomes. The framework supports early analysis and exposes absent evidence. Physical qualification remains separate. */ }
item <'EX-03'> EX_03 : EngineeringArtifact { doc /* Mission troubleshooting and the cost of physical EPS replicas occur after this project early-phase scope. Retained model and measurement evidence supports future troubleshooting. Replacement of replicas is unverified. */ }
item <'EX-04'> EX_04 : EngineeringArtifact { doc /* Actual CubeSat RAM depends on hardware, software, mission conditions and operations. Framework acceptance covers RAM requirements, transformations and evidence, not achieved spacecraft reliability. */ }
item <'EX-05'> EX_05 : EngineeringArtifact { doc /* The proportion verified by testing is governed by applicable requirements and model credibility. Analysis is used when justified. The framework does not force substitution of analysis for mandatory physical tests. */ }
item <'EX-06'> EX_06 : EngineeringArtifact { doc /* Complete non-EPS subsystem acceptance is external. The framework covers EPS-facing demand, supply/protection interactions, interface data and associated evidence. */ }
use case <'SC01'> SC01 { subject enterprise : EngineeringEnterprise; actor engineers : Engineers; objective { doc /* Tailor and justify an EPS option */ } doc /* Source narrative follows. Its provisional N/RF labels are provenance only. Final IDs and responsibility links are in the reviewed common baseline.
**Concern causes:** expensive learning/tools and adaptation, many component/topology choices, stale BOM/cost, RAM gaps, prototype dependence, and unreadable justification (N01–N03, N05, N07).

1. The team declares mission scope, available resources, knowledge gaps and required early decision. L09 obtains L01 guidance and records the case/common-core/tailoring basis in L08.
2. L02 captures requirements, criteria and RAM obligations. L03 defines a generic EPS configuration and options. L04 binds sourced component properties, BOM quantities, quotes and missing evidence.
3. L05 runs the declared power, thermal, EMC, RAM or other applicable comparisons on a common scenario basis. L06 checks model applicability. L07 records admissible evidence and remaining verification obligations.
4. L09 presents options, tradeoffs, trace chains and unknowns. The responsible engineer records the decision in L02. L08 freezes the package. A reviewed learning item can return to L01.

**Exception:** missing properties, criteria, quote scope or applicable model evidence remain visible and can leave comparison/decision status unresolved. No score fabricates missing data. **Framework test:** another user reconstructs the package and repeats a named analysis. A contrasting case changes only permitted parameters/extensions/mappings. Core defects remain defects and require a separate revised-baseline evaluation. */ }
use case <'SC02'> SC02 { subject enterprise : EngineeringEnterprise; actor engineers : Engineers; objective { doc /* Process a coupled load and EPS service change */ } doc /* Source narrative follows. Its provisional N/RF labels are provenance only. Final IDs and responsibility links are in the reviewed common baseline.
**Concern causes:** reciprocal subsystem/EPS updates, duty-cycle/mode ambiguity, temporary energy deficits, hardware/software regrouping and duplicated service definitions, integration and target resource uncertainty (N06, N08–N10, N13).

1. A non-EPS engineer changes payload activity or attitude behavior. L02 records the proposed change and requests L03/L04/L06/L07 dependencies. Impact includes load profiles, power requirements, component limits, battery assumptions, software/service definitions, BOM/cost, and verification evidence where applicable.
2. L03 revises the affected supply and shared service contract with separate hardware/software allocations. A target adapter generates only its supported artifacts and reports unmapped behavior or target compatibility. L07 specifies command guards, effects, telemetry validity, safe-mode/recovery coordination and software resource checks.
3. L05 executes a time-indexed scenario with changed attitude, generation, demand and mode transitions. L06 reports applicability and mismatches. L07 evaluates the relevant early EPS criteria, including service conformance. Static energy surplus cannot by itself close the dynamic obligation.
4. L02 presents candidate changes and residual verification needs for engineer disposition. L08 records a successor baseline only after the declared checks and authorizations. L09 communicates both upstream/downstream impacts.

**Exception:** unsupported cFS/F Prime/OS mapping, unknown memory/timing/power budgets, semantic loss or invalid model domain blocks the corresponding claim. **Framework test:** inject a unit/telemetry or command-condition mismatch and a reference dynamic-energy inconsistency. Check the impact set and retained stale evidence, then replay the corrected baseline. Framework processing time counts only a correct outcome. */ }
use case <'SC03'> SC03 { subject enterprise : EngineeringEnterprise; actor engineers : Engineers; objective { doc /* Resolve a failed protection gate and prepare safe later testing */ } doc /* Source narrative follows. Its provisional N/RF labels are provenance only. Final IDs and responsibility links are in the reviewed common baseline.
**Concern causes:** sparse black-box evidence after failure, uncertain model calibration/battery health, anomaly versus noise/degradation ambiguity, hazardous fault tests, incomplete setup, invalid/inactive telemetry and clock/loop delays (N05, N09–N12, N14).

1. An EPS engineer receives a failed or inconclusive protection/control assessment. L08 preserves raw stimuli, currents/voltages/temperatures, states/events, setup, criterion and all source revisions. L06 checks channel validity, synchronization, parameter/domain evidence and alternative fault explanations.
2. L06 proposes a calibration/property/design update through L02. L04/L03 produce identified revisions. L05 repeats the affected scenarios, and L07 keeps safety, prediction agreement and policy effectiveness as separate obligations.
3. L07 compiles the future DUT/equipment connection, procedure, stimuli, capture, limits, abort/recovery and residual physical-test needs. The technician records feasibility and safety disposition. Missing limits, protection or timing capability prevents physical handoff.
4. If later observations are supplied under an approved setup, L06 checks their quality and updates credibility through a new revision. L02 scopes affected prior decisions. Reanalysis creates new evidence. L09 presents the failed-gate explanation and remaining actions.

**Exception:** missing independent validation, unknown safe fault limits, deactivated sensors, uncertain active-unit mapping, or unbounded loop delay yields blocked/inconclusive status. Simulation agreement alone cannot authorize a dangerous hardware experiment. **Framework test:** use recorded data and a review exercise to prove the gate and feedback behavior. No hazardous hardware test is needed to verify that the framework blocks an incomplete proposal. */ }

}
