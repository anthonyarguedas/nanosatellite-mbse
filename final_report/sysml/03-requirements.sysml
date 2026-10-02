// Controlled report model. Trace records are published in final_report/traceability/.
package FrameworkRequirements {
private import FrameworkDomain::*;
private import RequirementDerivation::*;
requirement <'FR-01'> FR_01 { subject framework : Framework; doc /* The framework shall retain each requirement as an identified record with source need, parent, rationale, observable quantities or conditions and applicable units, owner, verification method, criterion, and resolution status. A not-applicable field shall include a rationale. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-01"; sourceText = "The framework shall retain each requirement as an identified record with source need, parent, rationale, observable quantities or conditions and applicable units, owner, verification method, criterion, and resolution status. A not-applicable field shall include a rationale."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-01,C-SE-03.3,C-SE-05.1,C-EPS-04.3,C-EPS-04.3.1,C-EPS-04.3.2"; status = "proposed, verification pending"; citationRecord = "verification method I,T | proposed fixture: Round-trip a quantitative requirement and a qualitative demonstration requirement, including source, condition or quantity, applicable units and criterion. An inapplicable field retains rationale. An absent criterion remains unresolved and cannot acquire a verified label."; }
#derivation connection derive_MR_01_FR_01 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_01; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_02_FR_01 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_01; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_01_C_PM_01 from FR_01 to FrameworkConcerns::C_PM_01;
#sourceTrace dependency requirement_source_FR_01_C_SE_03_3 from FR_01 to FrameworkConcerns::C_SE_03_3;
#sourceTrace dependency requirement_source_FR_01_C_SE_05_1 from FR_01 to FrameworkConcerns::C_SE_05_1;
#sourceTrace dependency requirement_source_FR_01_C_EPS_04_3 from FR_01 to FrameworkConcerns::C_EPS_04_3;
#sourceTrace dependency requirement_source_FR_01_C_EPS_04_3_1 from FR_01 to FrameworkConcerns::C_EPS_04_3_1;
#sourceTrace dependency requirement_source_FR_01_C_EPS_04_3_2 from FR_01 to FrameworkConcerns::C_EPS_04_3_2;
requirement <'FR-02'> FR_02 { subject framework : Framework; doc /* The framework shall provide requirement and traceability templates, worked EPS examples, and a guided reference workflow that covers writing criteria, linking evidence, and interpreting gaps. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-02"; sourceText = "The framework shall provide requirement and traceability templates, worked EPS examples, and a guided reference workflow that covers writing criteria, linking evidence, and interpreting gaps."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-01,C-PM-01.1,C-SE-01.1,C-SE-01.1.1,C-EPS-02.1,C-NE-02,C-NE-02.4,C-NE-02.4.1,C-NE-02.4.2"; status = "proposed, verification pending"; citationRecord = "verification method I,D | proposed fixture: Inspect the learning package and demonstrate the workflow from a declared clean start. Measure learner effort and errors without imposing an unagreed time limit."; }
#derivation connection derive_MR_01_FR_02 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_02; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_11_FR_02 { end #original ::> FrameworkNeeds::MR_11; end #derive ::> FR_02; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_02_C_PM_01 from FR_02 to FrameworkConcerns::C_PM_01;
#sourceTrace dependency requirement_source_FR_02_C_PM_01_1 from FR_02 to FrameworkConcerns::C_PM_01_1;
#sourceTrace dependency requirement_source_FR_02_C_SE_01_1 from FR_02 to FrameworkConcerns::C_SE_01_1;
#sourceTrace dependency requirement_source_FR_02_C_SE_01_1_1 from FR_02 to FrameworkConcerns::C_SE_01_1_1;
#sourceTrace dependency requirement_source_FR_02_C_EPS_02_1 from FR_02 to FrameworkConcerns::C_EPS_02_1;
#sourceTrace dependency requirement_source_FR_02_C_NE_02 from FR_02 to FrameworkConcerns::C_NE_02;
#sourceTrace dependency requirement_source_FR_02_C_NE_02_4 from FR_02 to FrameworkConcerns::C_NE_02_4;
#sourceTrace dependency requirement_source_FR_02_C_NE_02_4_1 from FR_02 to FrameworkConcerns::C_NE_02_4_1;
#sourceTrace dependency requirement_source_FR_02_C_NE_02_4_2 from FR_02 to FrameworkConcerns::C_NE_02_4_2;
requirement <'FR-03'> FR_03 { subject framework : Framework; doc /* The framework shall retain a source-linked catalogue of requirement derivation and verification methods, standards, and activity templates with applicability, tailoring rationale, and limitations. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-03"; sourceText = "The framework shall retain a source-linked catalogue of requirement derivation and verification methods, standards, and activity templates with applicability, tailoring rationale, and limitations."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-03.3.1.3,C-SE-03.3.1.3.1,C-SE-03.3.1.3.2,C-SE-03.4,C-SE-03.4.1,C-SE-03.4.2,C-SE-05.2.1.1,C-EPS-04.4,C-EPS-04.4.1,C-EPS-04.4.2,C-EPS-04.4.4,C-EPS-04.4.4.1"; status = "proposed, verification pending"; citationRecord = "verification method I,D | proposed fixture: For subsystem and component fixtures retrieve the chosen method and its source, conditions, tailoring decision, and excluded alternatives. A catalogue entry does not assert standards compliance."; }
#derivation connection derive_MR_01_FR_03 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_03; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_07_FR_03 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_03; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_11_FR_03 { end #original ::> FrameworkNeeds::MR_11; end #derive ::> FR_03; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_03_C_SE_03_3_1_3 from FR_03 to FrameworkConcerns::C_SE_03_3_1_3;
#sourceTrace dependency requirement_source_FR_03_C_SE_03_3_1_3_1 from FR_03 to FrameworkConcerns::C_SE_03_3_1_3_1;
#sourceTrace dependency requirement_source_FR_03_C_SE_03_3_1_3_2 from FR_03 to FrameworkConcerns::C_SE_03_3_1_3_2;
#sourceTrace dependency requirement_source_FR_03_C_SE_03_4 from FR_03 to FrameworkConcerns::C_SE_03_4;
#sourceTrace dependency requirement_source_FR_03_C_SE_03_4_1 from FR_03 to FrameworkConcerns::C_SE_03_4_1;
#sourceTrace dependency requirement_source_FR_03_C_SE_03_4_2 from FR_03 to FrameworkConcerns::C_SE_03_4_2;
#sourceTrace dependency requirement_source_FR_03_C_SE_05_2_1_1 from FR_03 to FrameworkConcerns::C_SE_05_2_1_1;
#sourceTrace dependency requirement_source_FR_03_C_EPS_04_4 from FR_03 to FrameworkConcerns::C_EPS_04_4;
#sourceTrace dependency requirement_source_FR_03_C_EPS_04_4_1 from FR_03 to FrameworkConcerns::C_EPS_04_4_1;
#sourceTrace dependency requirement_source_FR_03_C_EPS_04_4_2 from FR_03 to FrameworkConcerns::C_EPS_04_4_2;
#sourceTrace dependency requirement_source_FR_03_C_EPS_04_4_4 from FR_03 to FrameworkConcerns::C_EPS_04_4_4;
#sourceTrace dependency requirement_source_FR_03_C_EPS_04_4_4_1 from FR_03 to FrameworkConcerns::C_EPS_04_4_4_1;
requirement <'FR-04'> FR_04 { subject framework : Framework; doc /* The framework shall retrieve applicable links from needs and requirements to design decisions, model inputs, verification criteria and results, and retrieve the reverse paths. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-04"; sourceText = "The framework shall retrieve applicable links from needs and requirements to design decisions, model inputs, verification criteria and results, and retrieve the reverse paths."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-01,C-SE-02,C-SE-02.1,C-EPS-02,C-EPS-03,C-EPS-03.1,C-EPS-03.2"; status = "proposed, verification pending"; citationRecord = "verification method T | proposed fixture: Compare both query directions with the fixture relation set. Missing, ambiguous and stale endpoints remain visible."; }
#derivation connection derive_MR_02_FR_04 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_04; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_10_FR_04 { end #original ::> FrameworkNeeds::MR_10; end #derive ::> FR_04; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_04_C_SE_01 from FR_04 to FrameworkConcerns::C_SE_01;
#sourceTrace dependency requirement_source_FR_04_C_SE_02 from FR_04 to FrameworkConcerns::C_SE_02;
#sourceTrace dependency requirement_source_FR_04_C_SE_02_1 from FR_04 to FrameworkConcerns::C_SE_02_1;
#sourceTrace dependency requirement_source_FR_04_C_EPS_02 from FR_04 to FrameworkConcerns::C_EPS_02;
#sourceTrace dependency requirement_source_FR_04_C_EPS_03 from FR_04 to FrameworkConcerns::C_EPS_03;
#sourceTrace dependency requirement_source_FR_04_C_EPS_03_1 from FR_04 to FrameworkConcerns::C_EPS_03_1;
#sourceTrace dependency requirement_source_FR_04_C_EPS_03_2 from FR_04 to FrameworkConcerns::C_EPS_03_2;
requirement <'FR-05'> FR_05 { subject framework : Framework; doc /* The framework shall identify the requirements, EPS and non-EPS allocations, BOMs, models, software definitions, procedures, and evidence affected by a designated change. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-05"; sourceText = "The framework shall identify the requirements, EPS and non-EPS allocations, BOMs, models, software definitions, procedures, and evidence affected by a designated change."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-02.1.2,C-SE-01,C-SE-03,C-SE-03.1,C-SE-03.1.1,C-SE-03.2,C-SE-04,C-SE-04.1,C-SE-04.1.1,C-SE-09,C-SE-09.1,C-SE-09.2,C-SE-09.2.1,C-EPS-01,C-EPS-01.1,C-EPS-04,C-EPS-04.1,C-EPS-04.1.1,C-EPS-04.2,C-NE-02.1"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Use seeded cross-subsystem and component changes. Compare the returned impact set and unresolved coverage with an adjudicated reference."; }
#derivation connection derive_MR_02_FR_05 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_05; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_03_FR_05 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_05; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_08_FR_05 { end #original ::> FrameworkNeeds::MR_08; end #derive ::> FR_05; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_05_C_PM_02_1_2 from FR_05 to FrameworkConcerns::C_PM_02_1_2;
#sourceTrace dependency requirement_source_FR_05_C_SE_01 from FR_05 to FrameworkConcerns::C_SE_01;
#sourceTrace dependency requirement_source_FR_05_C_SE_03 from FR_05 to FrameworkConcerns::C_SE_03;
#sourceTrace dependency requirement_source_FR_05_C_SE_03_1 from FR_05 to FrameworkConcerns::C_SE_03_1;
#sourceTrace dependency requirement_source_FR_05_C_SE_03_1_1 from FR_05 to FrameworkConcerns::C_SE_03_1_1;
#sourceTrace dependency requirement_source_FR_05_C_SE_03_2 from FR_05 to FrameworkConcerns::C_SE_03_2;
#sourceTrace dependency requirement_source_FR_05_C_SE_04 from FR_05 to FrameworkConcerns::C_SE_04;
#sourceTrace dependency requirement_source_FR_05_C_SE_04_1 from FR_05 to FrameworkConcerns::C_SE_04_1;
#sourceTrace dependency requirement_source_FR_05_C_SE_04_1_1 from FR_05 to FrameworkConcerns::C_SE_04_1_1;
#sourceTrace dependency requirement_source_FR_05_C_SE_09 from FR_05 to FrameworkConcerns::C_SE_09;
#sourceTrace dependency requirement_source_FR_05_C_SE_09_1 from FR_05 to FrameworkConcerns::C_SE_09_1;
#sourceTrace dependency requirement_source_FR_05_C_SE_09_2 from FR_05 to FrameworkConcerns::C_SE_09_2;
#sourceTrace dependency requirement_source_FR_05_C_SE_09_2_1 from FR_05 to FrameworkConcerns::C_SE_09_2_1;
#sourceTrace dependency requirement_source_FR_05_C_EPS_01 from FR_05 to FrameworkConcerns::C_EPS_01;
#sourceTrace dependency requirement_source_FR_05_C_EPS_01_1 from FR_05 to FrameworkConcerns::C_EPS_01_1;
#sourceTrace dependency requirement_source_FR_05_C_EPS_04 from FR_05 to FrameworkConcerns::C_EPS_04;
#sourceTrace dependency requirement_source_FR_05_C_EPS_04_1 from FR_05 to FrameworkConcerns::C_EPS_04_1;
#sourceTrace dependency requirement_source_FR_05_C_EPS_04_1_1 from FR_05 to FrameworkConcerns::C_EPS_04_1_1;
#sourceTrace dependency requirement_source_FR_05_C_EPS_04_2 from FR_05 to FrameworkConcerns::C_EPS_04_2;
#sourceTrace dependency requirement_source_FR_05_C_NE_02_1 from FR_05 to FrameworkConcerns::C_NE_02_1;
requirement <'FR-06'> FR_06 { subject framework : Framework; doc /* The framework shall issue a successor baseline for an accepted change that retains its request and failed-gate context and marks affected evidence as regenerated, stale, or unresolved. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-06"; sourceText = "The framework shall issue a successor baseline for an accepted change that retains its request and failed-gate context and marks affected evidence as regenerated, stale, or unresolved."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-02.1.2,C-SE-03,C-SE-03.1,C-SE-03.1.1,C-SE-04,C-SE-04.1,C-SE-04.1.1,C-SE-07.3,C-EPS-03,C-EPS-03.1,C-EPS-03.2,C-EPS-04,C-EPS-04.1,C-EPS-04.1.1"; status = "proposed, verification pending"; citationRecord = "verification method T | proposed fixture: Exercise a failed verification gate followed by correction. Preserve the prior baseline and prevent stale results from appearing current."; }
#derivation connection derive_MR_02_FR_06 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_06; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_05_FR_06 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_06; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_07_FR_06 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_06; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_06_C_PM_02_1_2 from FR_06 to FrameworkConcerns::C_PM_02_1_2;
#sourceTrace dependency requirement_source_FR_06_C_SE_03 from FR_06 to FrameworkConcerns::C_SE_03;
#sourceTrace dependency requirement_source_FR_06_C_SE_03_1 from FR_06 to FrameworkConcerns::C_SE_03_1;
#sourceTrace dependency requirement_source_FR_06_C_SE_03_1_1 from FR_06 to FrameworkConcerns::C_SE_03_1_1;
#sourceTrace dependency requirement_source_FR_06_C_SE_04 from FR_06 to FrameworkConcerns::C_SE_04;
#sourceTrace dependency requirement_source_FR_06_C_SE_04_1 from FR_06 to FrameworkConcerns::C_SE_04_1;
#sourceTrace dependency requirement_source_FR_06_C_SE_04_1_1 from FR_06 to FrameworkConcerns::C_SE_04_1_1;
#sourceTrace dependency requirement_source_FR_06_C_SE_07_3 from FR_06 to FrameworkConcerns::C_SE_07_3;
#sourceTrace dependency requirement_source_FR_06_C_EPS_03 from FR_06 to FrameworkConcerns::C_EPS_03;
#sourceTrace dependency requirement_source_FR_06_C_EPS_03_1 from FR_06 to FrameworkConcerns::C_EPS_03_1;
#sourceTrace dependency requirement_source_FR_06_C_EPS_03_2 from FR_06 to FrameworkConcerns::C_EPS_03_2;
#sourceTrace dependency requirement_source_FR_06_C_EPS_04 from FR_06 to FrameworkConcerns::C_EPS_04;
#sourceTrace dependency requirement_source_FR_06_C_EPS_04_1 from FR_06 to FrameworkConcerns::C_EPS_04_1;
#sourceTrace dependency requirement_source_FR_06_C_EPS_04_1_1 from FR_06 to FrameworkConcerns::C_EPS_04_1_1;
requirement <'FR-07'> FR_07 { subject framework : Framework; doc /* The framework shall retain identified, retrievable baselines of engineering records, case configuration, and evidence with revision history and distinct identities for accepted successors. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-07"; sourceText = "The framework shall retain identified, retrievable baselines of engineering records, case configuration, and evidence with revision history and distinct identities for accepted successors."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-05.1,C-SE-07,C-EPS-05.4,C-NE-01.2"; status = "proposed, verification pending"; citationRecord = "verification method T | proposed fixture: Reconstruct two revisions after a change and compare their manifests and contents. Attempted overwrite cannot erase the retained prior baseline."; }
#derivation connection derive_MR_02_FR_07 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_07; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_09_FR_07 { end #original ::> FrameworkNeeds::MR_09; end #derive ::> FR_07; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_07_C_PM_05_1 from FR_07 to FrameworkConcerns::C_PM_05_1;
#sourceTrace dependency requirement_source_FR_07_C_SE_07 from FR_07 to FrameworkConcerns::C_SE_07;
#sourceTrace dependency requirement_source_FR_07_C_EPS_05_4 from FR_07 to FrameworkConcerns::C_EPS_05_4;
#sourceTrace dependency requirement_source_FR_07_C_NE_01_2 from FR_07 to FrameworkConcerns::C_NE_01_2;
requirement <'FR-08'> FR_08 { subject framework : Framework; doc /* The framework shall check transferred identifiers, structure, quantities, units, polarity, time bases, interface meanings, and provenance against a declared contract and retain explicit rejection findings. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-08"; sourceText = "The framework shall check transferred identifiers, structure, quantities, units, polarity, time bases, interface meanings, and provenance against a declared contract and retain explicit rejection findings."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-05,C-PM-05.1,C-SE-07,C-SE-07.1,C-SE-07.1.1,C-EPS-04.4.4.2,C-EPS-05.4,C-NE-01.2"; status = "proposed, verification pending"; citationRecord = "verification method T | proposed fixture: Inject unit, sign, identifier and time-base mismatches. Reject incompatible transfers without replacing controlled content. Record unsupported or lossy mappings."; }
#derivation connection derive_MR_02_FR_08 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_08; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_09_FR_08 { end #original ::> FrameworkNeeds::MR_09; end #derive ::> FR_08; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_08_C_PM_05 from FR_08 to FrameworkConcerns::C_PM_05;
#sourceTrace dependency requirement_source_FR_08_C_PM_05_1 from FR_08 to FrameworkConcerns::C_PM_05_1;
#sourceTrace dependency requirement_source_FR_08_C_SE_07 from FR_08 to FrameworkConcerns::C_SE_07;
#sourceTrace dependency requirement_source_FR_08_C_SE_07_1 from FR_08 to FrameworkConcerns::C_SE_07_1;
#sourceTrace dependency requirement_source_FR_08_C_SE_07_1_1 from FR_08 to FrameworkConcerns::C_SE_07_1_1;
#sourceTrace dependency requirement_source_FR_08_C_EPS_04_4_4_2 from FR_08 to FrameworkConcerns::C_EPS_04_4_4_2;
#sourceTrace dependency requirement_source_FR_08_C_EPS_05_4 from FR_08 to FrameworkConcerns::C_EPS_05_4;
#sourceTrace dependency requirement_source_FR_08_C_NE_01_2 from FR_08 to FrameworkConcerns::C_NE_01_2;
requirement <'FR-09'> FR_09 { subject framework : Framework; doc /* The framework shall associate each result with its producer, method, requirement and decision, design and hardware configuration, software and model versions, parameter set, input data, environment, and raw output. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-09"; sourceText = "The framework shall associate each result with its producer, method, requirement and decision, design and hardware configuration, software and model versions, parameter set, input data, environment, and raw output."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-05.1,C-SE-07,C-SE-07.2,C-EPS-05.4,C-NE-01.2"; status = "proposed, verification pending"; citationRecord = "verification method I,T | proposed fixture: Trace an analytical and a supplied measurement result to every applicable configuration item. An unknown identity remains a gap and blocks a contradictory validity claim."; }
#derivation connection derive_MR_02_FR_09 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_09; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_05_FR_09 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_09; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_09_FR_09 { end #original ::> FrameworkNeeds::MR_09; end #derive ::> FR_09; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_09_C_PM_05_1 from FR_09 to FrameworkConcerns::C_PM_05_1;
#sourceTrace dependency requirement_source_FR_09_C_SE_07 from FR_09 to FrameworkConcerns::C_SE_07;
#sourceTrace dependency requirement_source_FR_09_C_SE_07_2 from FR_09 to FrameworkConcerns::C_SE_07_2;
#sourceTrace dependency requirement_source_FR_09_C_EPS_05_4 from FR_09 to FrameworkConcerns::C_EPS_05_4;
#sourceTrace dependency requirement_source_FR_09_C_NE_01_2 from FR_09 to FrameworkConcerns::C_NE_01_2;
requirement <'FR-10'> FR_10 { subject framework : Framework; doc /* The framework shall provide controlled instructions and dependencies to reconstruct and execute a designated analysis and compare its raw outputs using declared result-specific rules and tolerances. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-10"; sourceText = "The framework shall provide controlled instructions and dependencies to reconstruct and execute a designated analysis and compare its raw outputs using declared result-specific rules and tolerances."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-04"; status = "proposed, verification pending"; citationRecord = "verification method D,T | proposed fixture: An independent participant replays a baseline from a clean declared environment. Retain logs, seeds when relevant, failures and comparison verdicts. Tolerances are fixed before replay."; }
#derivation connection derive_MR_09_FR_10 { end #original ::> FrameworkNeeds::MR_09; end #derive ::> FR_10; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_10_C_PM_04 from FR_10 to FrameworkConcerns::C_PM_04;
requirement <'FR-11'> FR_11 { subject framework : Framework; doc /* The framework shall report missing, rejected, stale, out-of-domain, failed, and unresolved evidence with its affected claim, criticality rationale, owner and disposition. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-11"; sourceText = "The framework shall report missing, rejected, stale, out-of-domain, failed, and unresolved evidence with its affected claim, criticality rationale, owner and disposition."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-05.1,C-SE-07,C-EPS-05.4,C-NE-01.2"; status = "proposed, verification pending"; citationRecord = "verification method T | proposed fixture: Seed each status including a critical finding. A claim affected by unresolved critical evidence cannot receive an unqualified supported or verified status."; }
#derivation connection derive_MR_02_FR_11 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_11; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_05_FR_11 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_11; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_10_FR_11 { end #original ::> FrameworkNeeds::MR_10; end #derive ::> FR_11; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_11_C_PM_05_1 from FR_11 to FrameworkConcerns::C_PM_05_1;
#sourceTrace dependency requirement_source_FR_11_C_SE_07 from FR_11 to FrameworkConcerns::C_SE_07;
#sourceTrace dependency requirement_source_FR_11_C_EPS_05_4 from FR_11 to FrameworkConcerns::C_EPS_05_4;
#sourceTrace dependency requirement_source_FR_11_C_NE_01_2 from FR_11 to FrameworkConcerns::C_NE_01_2;
requirement <'FR-12'> FR_12 { subject framework : Framework; doc /* The framework shall generate and revise a candidate-specific BOM from identified physical design items with assembly, quantities, part identifiers, variant and selection status, and source revision. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-12"; sourceText = "The framework shall generate and revise a candidate-specific BOM from identified physical design items with assembly, quantities, part identifiers, variant and selection status, and source revision."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-02,C-PM-02.1,C-PM-02.1.1,C-PM-02.1.2"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Compare two alternative assemblies and one component substitution with a reference BOM. Candidate alternatives remain distinct. Missing part data is reported."; }
#derivation connection derive_MR_03_FR_12 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_12; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_12_C_PM_02 from FR_12 to FrameworkConcerns::C_PM_02;
#sourceTrace dependency requirement_source_FR_12_C_PM_02_1 from FR_12 to FrameworkConcerns::C_PM_02_1;
#sourceTrace dependency requirement_source_FR_12_C_PM_02_1_1 from FR_12 to FrameworkConcerns::C_PM_02_1_1;
#sourceTrace dependency requirement_source_FR_12_C_PM_02_1_2 from FR_12 to FrameworkConcerns::C_PM_02_1_2;
requirement <'FR-13'> FR_13 { subject framework : Framework; doc /* The framework shall derive a revision-linked financial estimate from the BOM and declared additional cost categories while retaining price source, date, currency, quantity, estimate basis, uncertainty and missing data. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-13"; sourceText = "The framework shall derive a revision-linked financial estimate from the BOM and declared additional cost categories while retaining price source, date, currency, quantity, estimate basis, uncertainty and missing data."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-02,C-PM-02.1.2"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Recalculate a sourced-price fixture after a quantity and part change. Match reference arithmetic and preserve unknown costs. Do not import historical project costs as new framework measurements."; }
#derivation connection derive_MR_03_FR_13 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_13; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_13_C_PM_02 from FR_13 to FrameworkConcerns::C_PM_02;
#sourceTrace dependency requirement_source_FR_13_C_PM_02_1_2 from FR_13 to FrameworkConcerns::C_PM_02_1_2;
requirement <'FR-14'> FR_14 { subject framework : Framework; doc /* The framework shall produce a comparison of designated EPS architectures using a common requirement, assumption, evidence and criterion basis with feasibility status, raw measures, uncertainty and decision rationale. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-14"; sourceText = "The framework shall produce a comparison of designated EPS architectures using a common requirement, assumption, evidence and criterion basis with feasibility status, raw measures, uncertainty and decision rationale."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-02.1.1,C-SE-03.2,C-EPS-01,C-EPS-01.1,C-EPS-04.2"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Compare candidates with a failing requirement and incomplete evidence. Keep feasibility and unknown status separate from ranking. Any preference weights are declared before results."; }
#derivation connection derive_MR_03_FR_14 { end #original ::> FrameworkNeeds::MR_03; end #derive ::> FR_14; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_04_FR_14 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_14; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_14_C_PM_02_1_1 from FR_14 to FrameworkConcerns::C_PM_02_1_1;
#sourceTrace dependency requirement_source_FR_14_C_SE_03_2 from FR_14 to FrameworkConcerns::C_SE_03_2;
#sourceTrace dependency requirement_source_FR_14_C_EPS_01 from FR_14 to FrameworkConcerns::C_EPS_01;
#sourceTrace dependency requirement_source_FR_14_C_EPS_01_1 from FR_14 to FrameworkConcerns::C_EPS_01_1;
#sourceTrace dependency requirement_source_FR_14_C_EPS_04_2 from FR_14 to FrameworkConcerns::C_EPS_04_2;
requirement <'FR-15'> FR_15 { subject framework : Framework; doc /* The framework shall provide a configurable generic EPS representation covering requirements, functions, logical and physical elements, interfaces, modes and states, with case-specific parameter and extension records. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-15"; sourceText = "The framework shall provide a configurable generic EPS representation covering requirements, functions, logical and physical elements, interfaces, modes and states, with case-specific parameter and extension records."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: "; status = "proposed, verification pending"; citationRecord = "verification method I,D | proposed fixture: Instantiate the representation in two contrasting cases and trace a requirement through function, allocation, interface and analysis. An extension retains its relation to the generic core."; }
#derivation connection derive_MR_04_FR_15 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_15; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_11_FR_15 { end #original ::> FrameworkNeeds::MR_11; end #derive ::> FR_15; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
requirement <'FR-16'> FR_16 { subject framework : Framework; doc /* The framework shall compose time-dependent subsystem demand, duty cycles, schedules and mode transitions with orbit, attitude, irradiance, eclipse, thermal conditions and EPS supply and protection behavior. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-16"; sourceText = "The framework shall compose time-dependent subsystem demand, duty cycles, schedules and mode transitions with orbit, attitude, irradiance, eclipse, thermal conditions and EPS supply and protection behavior."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-03.3.1.2,C-SE-06,C-SE-06.1,C-SE-06.2,C-EPS-01.1.4,C-NE-01.1,C-NE-01.1.1"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Use a fixture whose average budget passes while a coupled load and illumination event creates a transient shortage. Inspect inputs, interactions and event timing against a reference calculation."; }
#derivation connection derive_MR_04_FR_16 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_16; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_05_FR_16 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_16; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_08_FR_16 { end #original ::> FrameworkNeeds::MR_08; end #derive ::> FR_16; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_16_C_SE_03_3_1_2 from FR_16 to FrameworkConcerns::C_SE_03_3_1_2;
#sourceTrace dependency requirement_source_FR_16_C_SE_06 from FR_16 to FrameworkConcerns::C_SE_06;
#sourceTrace dependency requirement_source_FR_16_C_SE_06_1 from FR_16 to FrameworkConcerns::C_SE_06_1;
#sourceTrace dependency requirement_source_FR_16_C_SE_06_2 from FR_16 to FrameworkConcerns::C_SE_06_2;
#sourceTrace dependency requirement_source_FR_16_C_EPS_01_1_4 from FR_16 to FrameworkConcerns::C_EPS_01_1_4;
#sourceTrace dependency requirement_source_FR_16_C_NE_01_1 from FR_16 to FrameworkConcerns::C_NE_01_1;
#sourceTrace dependency requirement_source_FR_16_C_NE_01_1_1 from FR_16 to FrameworkConcerns::C_NE_01_1_1;
requirement <'FR-17'> FR_17 { subject framework : Framework; doc /* The framework shall record how sourced component power and thermal characteristics and subsystem behavior become EPS or component requirement parameters, including units, uncertainties, allowable ranges and criterion decisions. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-17"; sourceText = "The framework shall record how sourced component power and thermal characteristics and subsystem behavior become EPS or component requirement parameters, including units, uncertainties, allowable ranges and criterion decisions."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-03,C-SE-03.3,C-SE-03.3.1,C-SE-03.3.1.1,C-SE-03.3.1.2,C-SE-03.3.1.3,C-SE-03.3.1.3.1,C-SE-03.3.1.3.2,C-SE-04,C-EPS-04,C-EPS-04.3,C-EPS-04.3.1,C-EPS-04.3.2"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Derive a fixture allocation from datasheet and supplied measurement inputs using a declared method. Preserve assumptions and flag unsupported ranges and undecided pass/fail values."; }
#derivation connection derive_MR_01_FR_17 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_17; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_02_FR_17 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_17; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_04_FR_17 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_17; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_17_C_SE_03 from FR_17 to FrameworkConcerns::C_SE_03;
#sourceTrace dependency requirement_source_FR_17_C_SE_03_3 from FR_17 to FrameworkConcerns::C_SE_03_3;
#sourceTrace dependency requirement_source_FR_17_C_SE_03_3_1 from FR_17 to FrameworkConcerns::C_SE_03_3_1;
#sourceTrace dependency requirement_source_FR_17_C_SE_03_3_1_1 from FR_17 to FrameworkConcerns::C_SE_03_3_1_1;
#sourceTrace dependency requirement_source_FR_17_C_SE_03_3_1_2 from FR_17 to FrameworkConcerns::C_SE_03_3_1_2;
#sourceTrace dependency requirement_source_FR_17_C_SE_03_3_1_3 from FR_17 to FrameworkConcerns::C_SE_03_3_1_3;
#sourceTrace dependency requirement_source_FR_17_C_SE_03_3_1_3_1 from FR_17 to FrameworkConcerns::C_SE_03_3_1_3_1;
#sourceTrace dependency requirement_source_FR_17_C_SE_03_3_1_3_2 from FR_17 to FrameworkConcerns::C_SE_03_3_1_3_2;
#sourceTrace dependency requirement_source_FR_17_C_SE_04 from FR_17 to FrameworkConcerns::C_SE_04;
#sourceTrace dependency requirement_source_FR_17_C_EPS_04 from FR_17 to FrameworkConcerns::C_EPS_04;
#sourceTrace dependency requirement_source_FR_17_C_EPS_04_3 from FR_17 to FrameworkConcerns::C_EPS_04_3;
#sourceTrace dependency requirement_source_FR_17_C_EPS_04_3_1 from FR_17 to FrameworkConcerns::C_EPS_04_3_1;
#sourceTrace dependency requirement_source_FR_17_C_EPS_04_3_2 from FR_17 to FrameworkConcerns::C_EPS_04_3_2;
requirement <'FR-18'> FR_18 { subject framework : Framework; doc /* The framework shall exchange identified EPS component and design data with declared electrical, thermal, EMC and CAD analysis tools and retain model mappings, applicable outputs and unsupported checks. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-18"; sourceText = "The framework shall exchange identified EPS component and design data with declared electrical, thermal, EMC and CAD analysis tools and retain model mappings, applicable outputs and unsupported checks."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-03,C-PM-03.1,C-SE-03.3.1,C-SE-03.3.1.1,C-EPS-01.1.1,C-EPS-04.4.4.2"; status = "proposed, verification pending"; citationRecord = "verification method D,T | proposed fixture: Every electrical, thermal, EMC and CAD exchange profile required by the frozen minimum shall complete its reference request/result exchange and declared identity, quantity, unit, meaning and revision checks. Retain unsupported mappings and development gaps. A missing required profile remains not verified or undetermined and cannot pass V18. A narrower minimum requires a reviewed scope disposition before evaluation."; }
#derivation connection derive_MR_04_FR_18 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_18; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_07_FR_18 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_18; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_18_C_PM_03 from FR_18 to FrameworkConcerns::C_PM_03;
#sourceTrace dependency requirement_source_FR_18_C_PM_03_1 from FR_18 to FrameworkConcerns::C_PM_03_1;
#sourceTrace dependency requirement_source_FR_18_C_SE_03_3_1 from FR_18 to FrameworkConcerns::C_SE_03_3_1;
#sourceTrace dependency requirement_source_FR_18_C_SE_03_3_1_1 from FR_18 to FrameworkConcerns::C_SE_03_3_1_1;
#sourceTrace dependency requirement_source_FR_18_C_EPS_01_1_1 from FR_18 to FrameworkConcerns::C_EPS_01_1_1;
#sourceTrace dependency requirement_source_FR_18_C_EPS_04_4_4_2 from FR_18 to FrameworkConcerns::C_EPS_04_4_4_2;
requirement <'FR-19'> FR_19 { subject framework : Framework; doc /* The framework shall execute or coordinate declared virtual EPS and component verification scenarios for dynamic loads, supply changes, protection events, rare faults, and controller electrical and timing constraints. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-19"; sourceText = "The framework shall execute or coordinate declared virtual EPS and component verification scenarios for dynamic loads, supply changes, protection events, rare faults, and controller electrical and timing constraints."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-03,C-PM-03.1,C-PM-03.1.1,C-SE-03.2,C-SE-06,C-SE-06.1,C-SE-06.2,C-EPS-01,C-EPS-01.1,C-EPS-01.1.1,C-EPS-01.1.2,C-EPS-01.1.3,C-EPS-01.1.4,C-EPS-01.1.5,C-EPS-04.2,C-NE-01,C-NE-01.1,C-NE-01.1.1,C-NE-01.1.2,C-TFT-01.4,C-TFT-01.4.1"; status = "proposed, verification pending"; citationRecord = "verification method D,T | proposed fixture: Retain stimulus, conditions, expected response, outputs and status for nominal and failure fixtures. Unsupported behavior and physical validation needs are explicit, including COTS evidence gaps."; }
#derivation connection derive_MR_04_FR_19 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_19; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_07_FR_19 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_19; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_19_C_PM_03 from FR_19 to FrameworkConcerns::C_PM_03;
#sourceTrace dependency requirement_source_FR_19_C_PM_03_1 from FR_19 to FrameworkConcerns::C_PM_03_1;
#sourceTrace dependency requirement_source_FR_19_C_PM_03_1_1 from FR_19 to FrameworkConcerns::C_PM_03_1_1;
#sourceTrace dependency requirement_source_FR_19_C_SE_03_2 from FR_19 to FrameworkConcerns::C_SE_03_2;
#sourceTrace dependency requirement_source_FR_19_C_SE_06 from FR_19 to FrameworkConcerns::C_SE_06;
#sourceTrace dependency requirement_source_FR_19_C_SE_06_1 from FR_19 to FrameworkConcerns::C_SE_06_1;
#sourceTrace dependency requirement_source_FR_19_C_SE_06_2 from FR_19 to FrameworkConcerns::C_SE_06_2;
#sourceTrace dependency requirement_source_FR_19_C_EPS_01 from FR_19 to FrameworkConcerns::C_EPS_01;
#sourceTrace dependency requirement_source_FR_19_C_EPS_01_1 from FR_19 to FrameworkConcerns::C_EPS_01_1;
#sourceTrace dependency requirement_source_FR_19_C_EPS_01_1_1 from FR_19 to FrameworkConcerns::C_EPS_01_1_1;
#sourceTrace dependency requirement_source_FR_19_C_EPS_01_1_2 from FR_19 to FrameworkConcerns::C_EPS_01_1_2;
#sourceTrace dependency requirement_source_FR_19_C_EPS_01_1_3 from FR_19 to FrameworkConcerns::C_EPS_01_1_3;
#sourceTrace dependency requirement_source_FR_19_C_EPS_01_1_4 from FR_19 to FrameworkConcerns::C_EPS_01_1_4;
#sourceTrace dependency requirement_source_FR_19_C_EPS_01_1_5 from FR_19 to FrameworkConcerns::C_EPS_01_1_5;
#sourceTrace dependency requirement_source_FR_19_C_EPS_04_2 from FR_19 to FrameworkConcerns::C_EPS_04_2;
#sourceTrace dependency requirement_source_FR_19_C_NE_01 from FR_19 to FrameworkConcerns::C_NE_01;
#sourceTrace dependency requirement_source_FR_19_C_NE_01_1 from FR_19 to FrameworkConcerns::C_NE_01_1;
#sourceTrace dependency requirement_source_FR_19_C_NE_01_1_1 from FR_19 to FrameworkConcerns::C_NE_01_1_1;
#sourceTrace dependency requirement_source_FR_19_C_NE_01_1_2 from FR_19 to FrameworkConcerns::C_NE_01_1_2;
#sourceTrace dependency requirement_source_FR_19_C_TFT_01_4 from FR_19 to FrameworkConcerns::C_TFT_01_4;
#sourceTrace dependency requirement_source_FR_19_C_TFT_01_4_1 from FR_19 to FrameworkConcerns::C_TFT_01_4_1;
requirement <'FR-20'> FR_20 { subject framework : Framework; doc /* The framework shall integrate identified battery electrical, thermal and degradation models with mission loads and retain the states, health and lifetime outputs, assumptions and uncertainty supported by each model. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-20"; sourceText = "The framework shall integrate identified battery electrical, thermal and degradation models with mission loads and retain the states, health and lifetime outputs, assumptions and uncertainty supported by each model."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-08,C-SE-08.1,C-SE-08.2,C-SE-08.3,C-EPS-05,C-EPS-05.3,C-EPS-05.3.1,C-EPS-06,C-EPS-06.1,C-EPS-06.2,C-EPS-06.3"; status = "proposed, verification pending"; citationRecord = "verification method A,D | proposed fixture: Replay fresh and aged battery fixtures under different load and temperature profiles. Verify coupling and provenance. Missing aging mechanisms and latent-state uncertainty remain visible."; }
#derivation connection derive_MR_05_FR_20 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_20; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_20_C_SE_08 from FR_20 to FrameworkConcerns::C_SE_08;
#sourceTrace dependency requirement_source_FR_20_C_SE_08_1 from FR_20 to FrameworkConcerns::C_SE_08_1;
#sourceTrace dependency requirement_source_FR_20_C_SE_08_2 from FR_20 to FrameworkConcerns::C_SE_08_2;
#sourceTrace dependency requirement_source_FR_20_C_SE_08_3 from FR_20 to FrameworkConcerns::C_SE_08_3;
#sourceTrace dependency requirement_source_FR_20_C_EPS_05 from FR_20 to FrameworkConcerns::C_EPS_05;
#sourceTrace dependency requirement_source_FR_20_C_EPS_05_3 from FR_20 to FrameworkConcerns::C_EPS_05_3;
#sourceTrace dependency requirement_source_FR_20_C_EPS_05_3_1 from FR_20 to FrameworkConcerns::C_EPS_05_3_1;
#sourceTrace dependency requirement_source_FR_20_C_EPS_06 from FR_20 to FrameworkConcerns::C_EPS_06;
#sourceTrace dependency requirement_source_FR_20_C_EPS_06_1 from FR_20 to FrameworkConcerns::C_EPS_06_1;
#sourceTrace dependency requirement_source_FR_20_C_EPS_06_2 from FR_20 to FrameworkConcerns::C_EPS_06_2;
#sourceTrace dependency requirement_source_FR_20_C_EPS_06_3 from FR_20 to FrameworkConcerns::C_EPS_06_3;
requirement <'FR-21'> FR_21 { subject framework : Framework; doc /* The framework shall associate each analytical verification claim with the model intended use, tested validity domain, calibration and validation evidence, uncertainty and acceptable prediction-error rule. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-21"; sourceText = "The framework shall associate each analytical verification claim with the model intended use, tested validity domain, calibration and validation evidence, uncertainty and acceptable prediction-error rule."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-03,C-PM-03.1,C-PM-04,C-SE-06,C-SE-06.1,C-SE-06.2,C-SE-08,C-SE-08.1,C-SE-08.2,C-SE-08.3,C-EPS-01.1.1,C-EPS-05,C-EPS-05.1,C-EPS-05.1.1,C-EPS-05.2,C-EPS-05.2.1,C-EPS-06,C-EPS-06.1,C-EPS-06.2,C-EPS-06.3,C-EPS-07,C-EPS-07.1,C-EPS-07.2,C-EPS-08,C-EPS-08.1"; status = "proposed, verification pending"; citationRecord = "verification method I,T | proposed fixture: Exercise an in-domain and an extrapolated claim. Separate calibration from validation data where available. Flag untested domains and absent error limits. Prediction accuracy limits require prior agreement."; }
#derivation connection derive_MR_05_FR_21 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_21; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_09_FR_21 { end #original ::> FrameworkNeeds::MR_09; end #derive ::> FR_21; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_21_C_PM_03 from FR_21 to FrameworkConcerns::C_PM_03;
#sourceTrace dependency requirement_source_FR_21_C_PM_03_1 from FR_21 to FrameworkConcerns::C_PM_03_1;
#sourceTrace dependency requirement_source_FR_21_C_PM_04 from FR_21 to FrameworkConcerns::C_PM_04;
#sourceTrace dependency requirement_source_FR_21_C_SE_06 from FR_21 to FrameworkConcerns::C_SE_06;
#sourceTrace dependency requirement_source_FR_21_C_SE_06_1 from FR_21 to FrameworkConcerns::C_SE_06_1;
#sourceTrace dependency requirement_source_FR_21_C_SE_06_2 from FR_21 to FrameworkConcerns::C_SE_06_2;
#sourceTrace dependency requirement_source_FR_21_C_SE_08 from FR_21 to FrameworkConcerns::C_SE_08;
#sourceTrace dependency requirement_source_FR_21_C_SE_08_1 from FR_21 to FrameworkConcerns::C_SE_08_1;
#sourceTrace dependency requirement_source_FR_21_C_SE_08_2 from FR_21 to FrameworkConcerns::C_SE_08_2;
#sourceTrace dependency requirement_source_FR_21_C_SE_08_3 from FR_21 to FrameworkConcerns::C_SE_08_3;
#sourceTrace dependency requirement_source_FR_21_C_EPS_01_1_1 from FR_21 to FrameworkConcerns::C_EPS_01_1_1;
#sourceTrace dependency requirement_source_FR_21_C_EPS_05 from FR_21 to FrameworkConcerns::C_EPS_05;
#sourceTrace dependency requirement_source_FR_21_C_EPS_05_1 from FR_21 to FrameworkConcerns::C_EPS_05_1;
#sourceTrace dependency requirement_source_FR_21_C_EPS_05_1_1 from FR_21 to FrameworkConcerns::C_EPS_05_1_1;
#sourceTrace dependency requirement_source_FR_21_C_EPS_05_2 from FR_21 to FrameworkConcerns::C_EPS_05_2;
#sourceTrace dependency requirement_source_FR_21_C_EPS_05_2_1 from FR_21 to FrameworkConcerns::C_EPS_05_2_1;
#sourceTrace dependency requirement_source_FR_21_C_EPS_06 from FR_21 to FrameworkConcerns::C_EPS_06;
#sourceTrace dependency requirement_source_FR_21_C_EPS_06_1 from FR_21 to FrameworkConcerns::C_EPS_06_1;
#sourceTrace dependency requirement_source_FR_21_C_EPS_06_2 from FR_21 to FrameworkConcerns::C_EPS_06_2;
#sourceTrace dependency requirement_source_FR_21_C_EPS_06_3 from FR_21 to FrameworkConcerns::C_EPS_06_3;
#sourceTrace dependency requirement_source_FR_21_C_EPS_07 from FR_21 to FrameworkConcerns::C_EPS_07;
#sourceTrace dependency requirement_source_FR_21_C_EPS_07_1 from FR_21 to FrameworkConcerns::C_EPS_07_1;
#sourceTrace dependency requirement_source_FR_21_C_EPS_07_2 from FR_21 to FrameworkConcerns::C_EPS_07_2;
#sourceTrace dependency requirement_source_FR_21_C_EPS_08 from FR_21 to FrameworkConcerns::C_EPS_08;
#sourceTrace dependency requirement_source_FR_21_C_EPS_08_1 from FR_21 to FrameworkConcerns::C_EPS_08_1;
requirement <'FR-22'> FR_22 { subject framework : Framework; doc /* The framework shall use supplied measurements to create an identified calibration or parameter-update record with data quality, prior and revised parameters, residuals and affected analyses. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-22"; sourceText = "The framework shall use supplied measurements to create an identified calibration or parameter-update record with data quality, prior and revised parameters, residuals and affected analyses."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-04,C-SE-07.3,C-SE-08.1,C-EPS-05,C-EPS-05.1,C-EPS-05.1.1,C-EPS-05.2,C-EPS-05.2.1"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Apply a measurement fixture, compare the declared calibration result with a reference, retain both parameter revisions, and flag analyses affected by drift or update."; }
#derivation connection derive_MR_02_FR_22 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_22; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_05_FR_22 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_22; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_09_FR_22 { end #original ::> FrameworkNeeds::MR_09; end #derive ::> FR_22; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_22_C_PM_04 from FR_22 to FrameworkConcerns::C_PM_04;
#sourceTrace dependency requirement_source_FR_22_C_SE_07_3 from FR_22 to FrameworkConcerns::C_SE_07_3;
#sourceTrace dependency requirement_source_FR_22_C_SE_08_1 from FR_22 to FrameworkConcerns::C_SE_08_1;
#sourceTrace dependency requirement_source_FR_22_C_EPS_05 from FR_22 to FrameworkConcerns::C_EPS_05;
#sourceTrace dependency requirement_source_FR_22_C_EPS_05_1 from FR_22 to FrameworkConcerns::C_EPS_05_1;
#sourceTrace dependency requirement_source_FR_22_C_EPS_05_1_1 from FR_22 to FrameworkConcerns::C_EPS_05_1_1;
#sourceTrace dependency requirement_source_FR_22_C_EPS_05_2 from FR_22 to FrameworkConcerns::C_EPS_05_2;
#sourceTrace dependency requirement_source_FR_22_C_EPS_05_2_1 from FR_22 to FrameworkConcerns::C_EPS_05_2_1;
requirement <'FR-23'> FR_23 { subject framework : Framework; doc /* The framework shall record the selected model fidelity, execution environment, time step, measured or estimated runtime and interface delays for each declared SIL or HIL interaction profile. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-23"; sourceText = "The framework shall record the selected model fidelity, execution environment, time step, measured or estimated runtime and interface delays for each declared SIL or HIL interaction profile."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-03.1.1,C-EPS-01.1.2,C-EPS-01.1.3,C-EPS-05.3,C-EPS-05.3.1,C-NE-02.5,C-NE-02.5.1,C-NE-02.5.2,C-TFT-02.3,C-TFT-02.3.1"; status = "proposed, verification pending"; citationRecord = "verification method I,T | proposed fixture: Profile a declared executable model and replay timestamped input/output fixtures. Real-time suitability remains unresolved until the applicable hardware and deadline are verified."; }
#derivation connection derive_MR_05_FR_23 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_23; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_07_FR_23 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_23; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_08_FR_23 { end #original ::> FrameworkNeeds::MR_08; end #derive ::> FR_23; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_23_C_PM_03_1_1 from FR_23 to FrameworkConcerns::C_PM_03_1_1;
#sourceTrace dependency requirement_source_FR_23_C_EPS_01_1_2 from FR_23 to FrameworkConcerns::C_EPS_01_1_2;
#sourceTrace dependency requirement_source_FR_23_C_EPS_01_1_3 from FR_23 to FrameworkConcerns::C_EPS_01_1_3;
#sourceTrace dependency requirement_source_FR_23_C_EPS_05_3 from FR_23 to FrameworkConcerns::C_EPS_05_3;
#sourceTrace dependency requirement_source_FR_23_C_EPS_05_3_1 from FR_23 to FrameworkConcerns::C_EPS_05_3_1;
#sourceTrace dependency requirement_source_FR_23_C_NE_02_5 from FR_23 to FrameworkConcerns::C_NE_02_5;
#sourceTrace dependency requirement_source_FR_23_C_NE_02_5_1 from FR_23 to FrameworkConcerns::C_NE_02_5_1;
#sourceTrace dependency requirement_source_FR_23_C_NE_02_5_2 from FR_23 to FrameworkConcerns::C_NE_02_5_2;
#sourceTrace dependency requirement_source_FR_23_C_TFT_02_3 from FR_23 to FrameworkConcerns::C_TFT_02_3;
#sourceTrace dependency requirement_source_FR_23_C_TFT_02_3_1 from FR_23 to FrameworkConcerns::C_TFT_02_3_1;
requirement <'FR-24'> FR_24 { subject framework : Framework; doc /* The framework shall compare designated charging and power-management policies under declared load, thermal, health, electrical and timing conditions with safety constraints and policy-specific outcome evidence. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-24"; sourceText = "The framework shall compare designated charging and power-management policies under declared load, thermal, health, electrical and timing conditions with safety constraints and policy-specific outcome evidence."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-EPS-01.1.2,C-EPS-01.1.3,C-EPS-08,C-EPS-08.1"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Replay a baseline and a changed policy against the same fixture conditions. A model prediction cannot be labeled a demonstrated hardware improvement. Retain pending SIL, HIL or hardware evidence."; }
#derivation connection derive_MR_05_FR_24 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_24; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_04_FR_24 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_24; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_24_C_EPS_01_1_2 from FR_24 to FrameworkConcerns::C_EPS_01_1_2;
#sourceTrace dependency requirement_source_FR_24_C_EPS_01_1_3 from FR_24 to FrameworkConcerns::C_EPS_01_1_3;
#sourceTrace dependency requirement_source_FR_24_C_EPS_08 from FR_24 to FrameworkConcerns::C_EPS_08;
#sourceTrace dependency requirement_source_FR_24_C_EPS_08_1 from FR_24 to FrameworkConcerns::C_EPS_08_1;
requirement <'FR-25'> FR_25 { subject framework : Framework; doc /* The framework shall compare time-correlated EPS telemetry with modeled expected behavior while retaining operating mode, model validity, degradation and sensor uncertainty, and alternative fault explanations. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-25"; sourceText = "The framework shall compare time-correlated EPS telemetry with modeled expected behavior while retaining operating mode, model validity, degradation and sensor uncertainty, and alternative fault explanations."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-EPS-07,C-EPS-07.1,C-EPS-07.2"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Use nominal, degrading, noisy and injected-fault fixtures. Retain residuals and diagnoses with TP, FP and FN against an expert reference. No pre-threshold detection capability is presumed."; }
#derivation connection derive_MR_05_FR_25 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_25; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_04_FR_25 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_25; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_25_C_EPS_07 from FR_25 to FrameworkConcerns::C_EPS_07;
#sourceTrace dependency requirement_source_FR_25_C_EPS_07_1 from FR_25 to FrameworkConcerns::C_EPS_07_1;
#sourceTrace dependency requirement_source_FR_25_C_EPS_07_2 from FR_25 to FrameworkConcerns::C_EPS_07_2;
requirement <'FR-26'> FR_26 { subject framework : Framework; doc /* The framework shall identify the RAM variables and failure assumptions applicable to designated EPS and spacecraft requirements and report their verification-method coverage and gaps. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-26"; sourceText = "The framework shall identify the RAM variables and failure assumptions applicable to designated EPS and spacecraft requirements and report their verification-method coverage and gaps."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-05,C-SE-05.1,C-SE-05.2,C-SE-05.2.1,C-SE-05.2.1.1"; status = "proposed, verification pending"; citationRecord = "verification method I,T | proposed fixture: Compare the declared RAM variable and requirement set with a reference. Report analysis, inspection, demonstration or test rationale without forcing every claim to use analysis."; }
#derivation connection derive_MR_06_FR_26 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_26; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_01_FR_26 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_26; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_26_C_SE_05 from FR_26 to FrameworkConcerns::C_SE_05;
#sourceTrace dependency requirement_source_FR_26_C_SE_05_1 from FR_26 to FrameworkConcerns::C_SE_05_1;
#sourceTrace dependency requirement_source_FR_26_C_SE_05_2 from FR_26 to FrameworkConcerns::C_SE_05_2;
#sourceTrace dependency requirement_source_FR_26_C_SE_05_2_1 from FR_26 to FrameworkConcerns::C_SE_05_2_1;
#sourceTrace dependency requirement_source_FR_26_C_SE_05_2_1_1 from FR_26 to FrameworkConcerns::C_SE_05_2_1_1;
requirement <'FR-27'> FR_27 { subject framework : Framework; doc /* The framework shall generate a declared RAM analysis representation from identified functions, components and failure dependencies with traceable transformation rules and sourced or missing reliability data. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-27"; sourceText = "The framework shall generate a declared RAM analysis representation from identified functions, components and failure dependencies with traceable transformation rules and sourced or missing reliability data."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-05,C-SE-05.2,C-SE-05.2.1,C-SE-05.2.1.2,C-SE-05.2.1.2.1"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Generate an FMEA, fault tree or other justified representation for a reference design and its changed variant. Compare entities and dependencies with an expert model. Missing probabilities cannot become factual reliability estimates."; }
#derivation connection derive_MR_06_FR_27 { end #original ::> FrameworkNeeds::MR_06; end #derive ::> FR_27; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_27_C_SE_05 from FR_27 to FrameworkConcerns::C_SE_05;
#sourceTrace dependency requirement_source_FR_27_C_SE_05_2 from FR_27 to FrameworkConcerns::C_SE_05_2;
#sourceTrace dependency requirement_source_FR_27_C_SE_05_2_1 from FR_27 to FrameworkConcerns::C_SE_05_2_1;
#sourceTrace dependency requirement_source_FR_27_C_SE_05_2_1_2 from FR_27 to FrameworkConcerns::C_SE_05_2_1_2;
#sourceTrace dependency requirement_source_FR_27_C_SE_05_2_1_2_1 from FR_27 to FrameworkConcerns::C_SE_05_2_1_2_1;
requirement <'FR-28'> FR_28 { subject framework : Framework; doc /* The framework shall retain each EPS or component verification activity with requirement, method, DUT baseline, applicable quantities or observable conditions, inputs, expected response, criterion, evidence variables and status. An inapplicable field shall retain its rationale. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-28"; sourceText = "The framework shall retain each EPS or component verification activity with requirement, method, DUT baseline, applicable quantities or observable conditions, inputs, expected response, criterion, evidence variables and status. An inapplicable field shall retain its rationale."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-03.2,C-SE-03.3,C-SE-03.4,C-SE-03.4.1,C-SE-03.4.2,C-SE-03.4.3,C-SE-03.4.3.1,C-SE-05.2,C-SE-05.2.1,C-SE-05.2.1.1,C-EPS-01,C-EPS-01.1,C-EPS-03,C-EPS-03.1,C-EPS-03.2,C-EPS-04.2,C-EPS-04.3,C-EPS-04.3.1,C-EPS-04.3.2,C-EPS-04.4,C-EPS-04.4.1,C-EPS-04.4.2,C-EPS-04.4.3,C-EPS-04.4.3.1,C-EPS-04.4.4,C-EPS-04.4.4.1,C-EPS-04.4.4.2,C-NE-01,C-NE-01.1,C-TFT-01,C-TFT-01.1,C-TFT-02,C-TFT-02.1,C-TFT-02.2"; status = "proposed, verification pending"; citationRecord = "verification method I,T | proposed fixture: Inspect quantitative analysis/test and qualitative inspection/demonstration fixtures against their method-specific fields. Check the applicable quantity or observable condition, criterion, expected response and evidence. An inapplicable field retains rationale. Missing mandatory fields, failed gates and unresolved criteria remain explicit and prevent an unsupported verdict."; }
#derivation connection derive_MR_07_FR_28 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_28; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_01_FR_28 { end #original ::> FrameworkNeeds::MR_01; end #derive ::> FR_28; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_28_C_SE_03_2 from FR_28 to FrameworkConcerns::C_SE_03_2;
#sourceTrace dependency requirement_source_FR_28_C_SE_03_3 from FR_28 to FrameworkConcerns::C_SE_03_3;
#sourceTrace dependency requirement_source_FR_28_C_SE_03_4 from FR_28 to FrameworkConcerns::C_SE_03_4;
#sourceTrace dependency requirement_source_FR_28_C_SE_03_4_1 from FR_28 to FrameworkConcerns::C_SE_03_4_1;
#sourceTrace dependency requirement_source_FR_28_C_SE_03_4_2 from FR_28 to FrameworkConcerns::C_SE_03_4_2;
#sourceTrace dependency requirement_source_FR_28_C_SE_03_4_3 from FR_28 to FrameworkConcerns::C_SE_03_4_3;
#sourceTrace dependency requirement_source_FR_28_C_SE_03_4_3_1 from FR_28 to FrameworkConcerns::C_SE_03_4_3_1;
#sourceTrace dependency requirement_source_FR_28_C_SE_05_2 from FR_28 to FrameworkConcerns::C_SE_05_2;
#sourceTrace dependency requirement_source_FR_28_C_SE_05_2_1 from FR_28 to FrameworkConcerns::C_SE_05_2_1;
#sourceTrace dependency requirement_source_FR_28_C_SE_05_2_1_1 from FR_28 to FrameworkConcerns::C_SE_05_2_1_1;
#sourceTrace dependency requirement_source_FR_28_C_EPS_01 from FR_28 to FrameworkConcerns::C_EPS_01;
#sourceTrace dependency requirement_source_FR_28_C_EPS_01_1 from FR_28 to FrameworkConcerns::C_EPS_01_1;
#sourceTrace dependency requirement_source_FR_28_C_EPS_03 from FR_28 to FrameworkConcerns::C_EPS_03;
#sourceTrace dependency requirement_source_FR_28_C_EPS_03_1 from FR_28 to FrameworkConcerns::C_EPS_03_1;
#sourceTrace dependency requirement_source_FR_28_C_EPS_03_2 from FR_28 to FrameworkConcerns::C_EPS_03_2;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_2 from FR_28 to FrameworkConcerns::C_EPS_04_2;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_3 from FR_28 to FrameworkConcerns::C_EPS_04_3;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_3_1 from FR_28 to FrameworkConcerns::C_EPS_04_3_1;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_3_2 from FR_28 to FrameworkConcerns::C_EPS_04_3_2;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_4 from FR_28 to FrameworkConcerns::C_EPS_04_4;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_4_1 from FR_28 to FrameworkConcerns::C_EPS_04_4_1;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_4_2 from FR_28 to FrameworkConcerns::C_EPS_04_4_2;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_4_3 from FR_28 to FrameworkConcerns::C_EPS_04_4_3;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_4_3_1 from FR_28 to FrameworkConcerns::C_EPS_04_4_3_1;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_4_4 from FR_28 to FrameworkConcerns::C_EPS_04_4_4;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_4_4_1 from FR_28 to FrameworkConcerns::C_EPS_04_4_4_1;
#sourceTrace dependency requirement_source_FR_28_C_EPS_04_4_4_2 from FR_28 to FrameworkConcerns::C_EPS_04_4_4_2;
#sourceTrace dependency requirement_source_FR_28_C_NE_01 from FR_28 to FrameworkConcerns::C_NE_01;
#sourceTrace dependency requirement_source_FR_28_C_NE_01_1 from FR_28 to FrameworkConcerns::C_NE_01_1;
#sourceTrace dependency requirement_source_FR_28_C_TFT_01 from FR_28 to FrameworkConcerns::C_TFT_01;
#sourceTrace dependency requirement_source_FR_28_C_TFT_01_1 from FR_28 to FrameworkConcerns::C_TFT_01_1;
#sourceTrace dependency requirement_source_FR_28_C_TFT_02 from FR_28 to FrameworkConcerns::C_TFT_02;
#sourceTrace dependency requirement_source_FR_28_C_TFT_02_1 from FR_28 to FrameworkConcerns::C_TFT_02_1;
#sourceTrace dependency requirement_source_FR_28_C_TFT_02_2 from FR_28 to FrameworkConcerns::C_TFT_02_2;
requirement <'FR-29'> FR_29 { subject framework : Framework; doc /* The framework shall produce a technician-readable verification proposal that specifies conditions, equipment and fixture identities, DUT connections, stimulus sequence, observations and evidence-generation procedure. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-29"; sourceText = "The framework shall produce a technician-readable verification proposal that specifies conditions, equipment and fixture identities, DUT connections, stimulus sequence, observations and evidence-generation procedure."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-03.4.3,C-SE-03.4.3.1,C-EPS-01.1.4,C-EPS-04.4.3,C-EPS-04.4.3.1,C-TFT-01,C-TFT-01.1,C-TFT-01.3,C-TFT-02,C-TFT-02.1,C-TFT-02.2"; status = "proposed, verification pending"; citationRecord = "verification method I,D | proposed fixture: A technician or qualified proxy checks a fixture proposal against a declared completeness checklist and identifies how equipment interacts with the DUT. Facility feasibility remains a separate decision."; }
#derivation connection derive_MR_07_FR_29 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_29; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_29_C_SE_03_4_3 from FR_29 to FrameworkConcerns::C_SE_03_4_3;
#sourceTrace dependency requirement_source_FR_29_C_SE_03_4_3_1 from FR_29 to FrameworkConcerns::C_SE_03_4_3_1;
#sourceTrace dependency requirement_source_FR_29_C_EPS_01_1_4 from FR_29 to FrameworkConcerns::C_EPS_01_1_4;
#sourceTrace dependency requirement_source_FR_29_C_EPS_04_4_3 from FR_29 to FrameworkConcerns::C_EPS_04_4_3;
#sourceTrace dependency requirement_source_FR_29_C_EPS_04_4_3_1 from FR_29 to FrameworkConcerns::C_EPS_04_4_3_1;
#sourceTrace dependency requirement_source_FR_29_C_TFT_01 from FR_29 to FrameworkConcerns::C_TFT_01;
#sourceTrace dependency requirement_source_FR_29_C_TFT_01_1 from FR_29 to FrameworkConcerns::C_TFT_01_1;
#sourceTrace dependency requirement_source_FR_29_C_TFT_01_3 from FR_29 to FrameworkConcerns::C_TFT_01_3;
#sourceTrace dependency requirement_source_FR_29_C_TFT_02 from FR_29 to FrameworkConcerns::C_TFT_02;
#sourceTrace dependency requirement_source_FR_29_C_TFT_02_1 from FR_29 to FrameworkConcerns::C_TFT_02_1;
#sourceTrace dependency requirement_source_FR_29_C_TFT_02_2 from FR_29 to FrameworkConcerns::C_TFT_02_2;
requirement <'FR-30'> FR_30 { subject framework : Framework; doc /* The framework shall include hazards, battery and electronics operating limits, fault-injection envelope, isolation, abort conditions and responsible safety-review status in each proposed physical verification activity. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-30"; sourceText = "The framework shall include hazards, battery and electronics operating limits, fault-injection envelope, isolation, abort conditions and responsible safety-review status in each proposed physical verification activity."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-EPS-01.1.5,C-TFT-01,C-TFT-01.2,C-TFT-01.4,C-TFT-01.4.1"; status = "proposed, verification pending"; citationRecord = "verification method I,T | proposed fixture: Use a safe virtual fault fixture and an incomplete physical proposal. Missing limits or approval status block a ready-for-physical-execution label. The framework does not authorize laboratory operations."; }
#derivation connection derive_MR_07_FR_30 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_30; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_04_FR_30 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_30; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_30_C_EPS_01_1_5 from FR_30 to FrameworkConcerns::C_EPS_01_1_5;
#sourceTrace dependency requirement_source_FR_30_C_TFT_01 from FR_30 to FrameworkConcerns::C_TFT_01;
#sourceTrace dependency requirement_source_FR_30_C_TFT_01_2 from FR_30 to FrameworkConcerns::C_TFT_01_2;
#sourceTrace dependency requirement_source_FR_30_C_TFT_01_4 from FR_30 to FrameworkConcerns::C_TFT_01_4;
#sourceTrace dependency requirement_source_FR_30_C_TFT_01_4_1 from FR_30 to FrameworkConcerns::C_TFT_01_4_1;
requirement <'FR-31'> FR_31 { subject framework : Framework; doc /* The framework shall record the time base, sampling and synchronization rules and known measurement, calculation and output delays for applied stimuli, responses and telemetry. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-31"; sourceText = "The framework shall record the time base, sampling and synchronization rules and known measurement, calculation and output delays for applied stimuli, responses and telemetry."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-03.4.3,C-SE-03.4.3.1,C-EPS-03,C-EPS-03.1,C-EPS-03.2,C-EPS-04.4.3,C-EPS-04.4.3.1,C-EPS-04.4.4,C-EPS-04.4.4.1,C-TFT-02,C-TFT-02.1,C-TFT-02.2,C-TFT-02.3,C-TFT-02.3.1"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Align a known timestamp fixture and expose injected skew and missing timing metadata. Report alignment error or uncertainty against the agreed profile, with no invented global limit."; }
#derivation connection derive_MR_07_FR_31 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_31; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_09_FR_31 { end #original ::> FrameworkNeeds::MR_09; end #derive ::> FR_31; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_31_C_SE_03_4_3 from FR_31 to FrameworkConcerns::C_SE_03_4_3;
#sourceTrace dependency requirement_source_FR_31_C_SE_03_4_3_1 from FR_31 to FrameworkConcerns::C_SE_03_4_3_1;
#sourceTrace dependency requirement_source_FR_31_C_EPS_03 from FR_31 to FrameworkConcerns::C_EPS_03;
#sourceTrace dependency requirement_source_FR_31_C_EPS_03_1 from FR_31 to FrameworkConcerns::C_EPS_03_1;
#sourceTrace dependency requirement_source_FR_31_C_EPS_03_2 from FR_31 to FrameworkConcerns::C_EPS_03_2;
#sourceTrace dependency requirement_source_FR_31_C_EPS_04_4_3 from FR_31 to FrameworkConcerns::C_EPS_04_4_3;
#sourceTrace dependency requirement_source_FR_31_C_EPS_04_4_3_1 from FR_31 to FrameworkConcerns::C_EPS_04_4_3_1;
#sourceTrace dependency requirement_source_FR_31_C_EPS_04_4_4 from FR_31 to FrameworkConcerns::C_EPS_04_4_4;
#sourceTrace dependency requirement_source_FR_31_C_EPS_04_4_4_1 from FR_31 to FrameworkConcerns::C_EPS_04_4_4_1;
#sourceTrace dependency requirement_source_FR_31_C_TFT_02 from FR_31 to FrameworkConcerns::C_TFT_02;
#sourceTrace dependency requirement_source_FR_31_C_TFT_02_1 from FR_31 to FrameworkConcerns::C_TFT_02_1;
#sourceTrace dependency requirement_source_FR_31_C_TFT_02_2 from FR_31 to FrameworkConcerns::C_TFT_02_2;
#sourceTrace dependency requirement_source_FR_31_C_TFT_02_3 from FR_31 to FrameworkConcerns::C_TFT_02_3;
#sourceTrace dependency requirement_source_FR_31_C_TFT_02_3_1 from FR_31 to FrameworkConcerns::C_TFT_02_3_1;
requirement <'FR-32'> FR_32 { subject framework : Framework; doc /* The framework shall check expected telemetry channels, units, timestamps, completeness and sensor validity conditions and preserve raw samples, invalid values and processing masks. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-32"; sourceText = "The framework shall check expected telemetry channels, units, timestamps, completeness and sensor validity conditions and preserve raw samples, invalid values and processing masks."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-03.4.3,C-SE-03.4.3.1,C-EPS-03,C-EPS-03.1,C-EPS-03.2,C-EPS-04.4.3,C-EPS-04.4.3.1,C-EPS-04.4.4,C-EPS-04.4.4.1,C-EPS-07,C-EPS-07.1,C-EPS-07.2,C-TFT-02,C-TFT-02.1,C-TFT-02.2,C-TFT-02.4,C-TFT-02.4.1"; status = "proposed, verification pending"; citationRecord = "verification method T | proposed fixture: Inject missing samples, inactive sensors and invalid values. Do not treat inactive invalid readings as valid measurements. Match the fixture quality verdict and retained raw data."; }
#derivation connection derive_MR_07_FR_32 { end #original ::> FrameworkNeeds::MR_07; end #derive ::> FR_32; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_05_FR_32 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_32; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_09_FR_32 { end #original ::> FrameworkNeeds::MR_09; end #derive ::> FR_32; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_32_C_SE_03_4_3 from FR_32 to FrameworkConcerns::C_SE_03_4_3;
#sourceTrace dependency requirement_source_FR_32_C_SE_03_4_3_1 from FR_32 to FrameworkConcerns::C_SE_03_4_3_1;
#sourceTrace dependency requirement_source_FR_32_C_EPS_03 from FR_32 to FrameworkConcerns::C_EPS_03;
#sourceTrace dependency requirement_source_FR_32_C_EPS_03_1 from FR_32 to FrameworkConcerns::C_EPS_03_1;
#sourceTrace dependency requirement_source_FR_32_C_EPS_03_2 from FR_32 to FrameworkConcerns::C_EPS_03_2;
#sourceTrace dependency requirement_source_FR_32_C_EPS_04_4_3 from FR_32 to FrameworkConcerns::C_EPS_04_4_3;
#sourceTrace dependency requirement_source_FR_32_C_EPS_04_4_3_1 from FR_32 to FrameworkConcerns::C_EPS_04_4_3_1;
#sourceTrace dependency requirement_source_FR_32_C_EPS_04_4_4 from FR_32 to FrameworkConcerns::C_EPS_04_4_4;
#sourceTrace dependency requirement_source_FR_32_C_EPS_04_4_4_1 from FR_32 to FrameworkConcerns::C_EPS_04_4_4_1;
#sourceTrace dependency requirement_source_FR_32_C_EPS_07 from FR_32 to FrameworkConcerns::C_EPS_07;
#sourceTrace dependency requirement_source_FR_32_C_EPS_07_1 from FR_32 to FrameworkConcerns::C_EPS_07_1;
#sourceTrace dependency requirement_source_FR_32_C_EPS_07_2 from FR_32 to FrameworkConcerns::C_EPS_07_2;
#sourceTrace dependency requirement_source_FR_32_C_TFT_02 from FR_32 to FrameworkConcerns::C_TFT_02;
#sourceTrace dependency requirement_source_FR_32_C_TFT_02_1 from FR_32 to FrameworkConcerns::C_TFT_02_1;
#sourceTrace dependency requirement_source_FR_32_C_TFT_02_2 from FR_32 to FrameworkConcerns::C_TFT_02_2;
#sourceTrace dependency requirement_source_FR_32_C_TFT_02_4 from FR_32 to FrameworkConcerns::C_TFT_02_4;
#sourceTrace dependency requirement_source_FR_32_C_TFT_02_4_1 from FR_32 to FrameworkConcerns::C_TFT_02_4_1;
requirement <'FR-33'> FR_33 { subject framework : Framework; doc /* The framework shall retain revision-linked EPS command, telemetry, event and parameter definitions with identifiers, types, units, ranges and encodings mapped to hardware, functional software and ground dictionaries. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-33"; sourceText = "The framework shall retain revision-linked EPS command, telemetry, event and parameter definitions with identifiers, types, units, ranges and encodings mapped to hardware, functional software and ground dictionaries."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-09,C-SE-09.1,C-SE-09.2,C-SE-09.2.1,C-SE-09.3,C-SE-10,C-SE-10.1,C-SE-10.2,C-EPS-09,C-EPS-09.1,C-EPS-09.2,C-NE-02,C-NE-02.1,C-NE-02.2"; status = "proposed, verification pending"; citationRecord = "verification method I,T | proposed fixture: Compare model, flight and ground fixtures against a shared contract. Detect a changed definition in one representation and report every affected mapping."; }
#derivation connection derive_MR_08_FR_33 { end #original ::> FrameworkNeeds::MR_08; end #derive ::> FR_33; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_02_FR_33 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_33; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_33_C_SE_09 from FR_33 to FrameworkConcerns::C_SE_09;
#sourceTrace dependency requirement_source_FR_33_C_SE_09_1 from FR_33 to FrameworkConcerns::C_SE_09_1;
#sourceTrace dependency requirement_source_FR_33_C_SE_09_2 from FR_33 to FrameworkConcerns::C_SE_09_2;
#sourceTrace dependency requirement_source_FR_33_C_SE_09_2_1 from FR_33 to FrameworkConcerns::C_SE_09_2_1;
#sourceTrace dependency requirement_source_FR_33_C_SE_09_3 from FR_33 to FrameworkConcerns::C_SE_09_3;
#sourceTrace dependency requirement_source_FR_33_C_SE_10 from FR_33 to FrameworkConcerns::C_SE_10;
#sourceTrace dependency requirement_source_FR_33_C_SE_10_1 from FR_33 to FrameworkConcerns::C_SE_10_1;
#sourceTrace dependency requirement_source_FR_33_C_SE_10_2 from FR_33 to FrameworkConcerns::C_SE_10_2;
#sourceTrace dependency requirement_source_FR_33_C_EPS_09 from FR_33 to FrameworkConcerns::C_EPS_09;
#sourceTrace dependency requirement_source_FR_33_C_EPS_09_1 from FR_33 to FrameworkConcerns::C_EPS_09_1;
#sourceTrace dependency requirement_source_FR_33_C_EPS_09_2 from FR_33 to FrameworkConcerns::C_EPS_09_2;
#sourceTrace dependency requirement_source_FR_33_C_NE_02 from FR_33 to FrameworkConcerns::C_NE_02;
#sourceTrace dependency requirement_source_FR_33_C_NE_02_1 from FR_33 to FrameworkConcerns::C_NE_02_1;
#sourceTrace dependency requirement_source_FR_33_C_NE_02_2 from FR_33 to FrameworkConcerns::C_NE_02_2;
requirement <'FR-34'> FR_34 { subject framework : Framework; doc /* The framework shall produce or coordinate checked mappings of the EPS software contract to declared cFS software-bus and F-Prime typed-connection profiles and identify behavior and implementation gaps. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-34"; sourceText = "The framework shall produce or coordinate checked mappings of the EPS software contract to declared cFS software-bus and F-Prime typed-connection profiles and identify behavior and implementation gaps."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-09,C-SE-09.1,C-SE-09.2,C-SE-09.2.1,C-SE-09.3,C-EPS-09,C-EPS-09.1,C-EPS-09.2,C-NE-02,C-NE-02.1,C-NE-02.2,C-NE-02.3,C-NE-02.3.1"; status = "proposed, verification pending"; citationRecord = "verification method D,T | proposed fixture: Round-trip or validate reference message and port mappings in both profiles. Declare framework version and unsupported exports. Architecture or dictionary generation is distinct from mission-specific functionality."; }
#derivation connection derive_MR_08_FR_34 { end #original ::> FrameworkNeeds::MR_08; end #derive ::> FR_34; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_34_C_SE_09 from FR_34 to FrameworkConcerns::C_SE_09;
#sourceTrace dependency requirement_source_FR_34_C_SE_09_1 from FR_34 to FrameworkConcerns::C_SE_09_1;
#sourceTrace dependency requirement_source_FR_34_C_SE_09_2 from FR_34 to FrameworkConcerns::C_SE_09_2;
#sourceTrace dependency requirement_source_FR_34_C_SE_09_2_1 from FR_34 to FrameworkConcerns::C_SE_09_2_1;
#sourceTrace dependency requirement_source_FR_34_C_SE_09_3 from FR_34 to FrameworkConcerns::C_SE_09_3;
#sourceTrace dependency requirement_source_FR_34_C_EPS_09 from FR_34 to FrameworkConcerns::C_EPS_09;
#sourceTrace dependency requirement_source_FR_34_C_EPS_09_1 from FR_34 to FrameworkConcerns::C_EPS_09_1;
#sourceTrace dependency requirement_source_FR_34_C_EPS_09_2 from FR_34 to FrameworkConcerns::C_EPS_09_2;
#sourceTrace dependency requirement_source_FR_34_C_NE_02 from FR_34 to FrameworkConcerns::C_NE_02;
#sourceTrace dependency requirement_source_FR_34_C_NE_02_1 from FR_34 to FrameworkConcerns::C_NE_02_1;
#sourceTrace dependency requirement_source_FR_34_C_NE_02_2 from FR_34 to FrameworkConcerns::C_NE_02_2;
#sourceTrace dependency requirement_source_FR_34_C_NE_02_3 from FR_34 to FrameworkConcerns::C_NE_02_3;
#sourceTrace dependency requirement_source_FR_34_C_NE_02_3_1 from FR_34 to FrameworkConcerns::C_NE_02_3_1;
requirement <'FR-35'> FR_35 { subject framework : Framework; doc /* The framework shall specify and check EPS command preconditions, order, expected effects, rejection and failure behavior, mode transitions and recovery responsibilities across EPS, telemetry, fault-management and safe-mode functions. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-35"; sourceText = "The framework shall specify and check EPS command preconditions, order, expected effects, rejection and failure behavior, mode transitions and recovery responsibilities across EPS, telemetry, fault-management and safe-mode functions."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-10,C-SE-10.1,C-SE-10.2,C-EPS-10,C-EPS-10.1,C-NE-01.1.2,C-NE-02"; status = "proposed, verification pending"; citationRecord = "verification method A,T | proposed fixture: Replay nominal, rejected and recovery sequences with a qualified software reference. Confirm functional flow and ownership without claiming deployment of flight software."; }
#derivation connection derive_MR_08_FR_35 { end #original ::> FrameworkNeeds::MR_08; end #derive ::> FR_35; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_04_FR_35 { end #original ::> FrameworkNeeds::MR_04; end #derive ::> FR_35; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_35_C_SE_10 from FR_35 to FrameworkConcerns::C_SE_10;
#sourceTrace dependency requirement_source_FR_35_C_SE_10_1 from FR_35 to FrameworkConcerns::C_SE_10_1;
#sourceTrace dependency requirement_source_FR_35_C_SE_10_2 from FR_35 to FrameworkConcerns::C_SE_10_2;
#sourceTrace dependency requirement_source_FR_35_C_EPS_10 from FR_35 to FrameworkConcerns::C_EPS_10;
#sourceTrace dependency requirement_source_FR_35_C_EPS_10_1 from FR_35 to FrameworkConcerns::C_EPS_10_1;
#sourceTrace dependency requirement_source_FR_35_C_NE_01_1_2 from FR_35 to FrameworkConcerns::C_NE_01_1_2;
#sourceTrace dependency requirement_source_FR_35_C_NE_02 from FR_35 to FrameworkConcerns::C_NE_02;
requirement <'FR-36'> FR_36 { subject framework : Framework; doc /* The framework shall retain a versioned OBC, operating-system, flight-framework and toolchain configuration with compatibility evidence and processor, memory, timing and power budget evidence for EPS functions. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-36"; sourceText = "The framework shall retain a versioned OBC, operating-system, flight-framework and toolchain configuration with compatibility evidence and processor, memory, timing and power budget evidence for EPS functions."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-NE-02,C-NE-02.4,C-NE-02.4.1,C-NE-02.4.2,C-NE-02.5,C-NE-02.5.1,C-NE-02.5.2"; status = "proposed, verification pending"; citationRecord = "verification method I,A,T | proposed fixture: Inspect a build/deployment profile and reference resource records. Distinguish measurements, estimates and unknown target compatibility. Check against mission-supplied allocations when available."; }
#derivation connection derive_MR_08_FR_36 { end #original ::> FrameworkNeeds::MR_08; end #derive ::> FR_36; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_05_FR_36 { end #original ::> FrameworkNeeds::MR_05; end #derive ::> FR_36; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_36_C_NE_02 from FR_36 to FrameworkConcerns::C_NE_02;
#sourceTrace dependency requirement_source_FR_36_C_NE_02_4 from FR_36 to FrameworkConcerns::C_NE_02_4;
#sourceTrace dependency requirement_source_FR_36_C_NE_02_4_1 from FR_36 to FrameworkConcerns::C_NE_02_4_1;
#sourceTrace dependency requirement_source_FR_36_C_NE_02_4_2 from FR_36 to FrameworkConcerns::C_NE_02_4_2;
#sourceTrace dependency requirement_source_FR_36_C_NE_02_5 from FR_36 to FrameworkConcerns::C_NE_02_5;
#sourceTrace dependency requirement_source_FR_36_C_NE_02_5_1 from FR_36 to FrameworkConcerns::C_NE_02_5_1;
#sourceTrace dependency requirement_source_FR_36_C_NE_02_5_2 from FR_36 to FrameworkConcerns::C_NE_02_5_2;
requirement <'FR-37'> FR_37 { subject framework : Framework; doc /* The framework shall produce filtered context, structure, interface and selected-design views from controlled EPS records with identifiers, units, legends and links to the represented baseline. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-37"; sourceText = "The framework shall produce filtered context, structure, interface and selected-design views from controlled EPS records with identifiers, units, legends and links to the represented baseline."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-02,C-SE-02.1,C-EPS-11,C-EPS-11.1"; status = "proposed, verification pending"; citationRecord = "verification method I,D | proposed fixture: Compare generated views with a fixture model and apply a declared reviewer task checklist. Assess correctness and readability without proliferating requirement, measure, scenario or state diagrams."; }
#derivation connection derive_MR_10_FR_37 { end #original ::> FrameworkNeeds::MR_10; end #derive ::> FR_37; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_37_C_SE_02 from FR_37 to FrameworkConcerns::C_SE_02;
#sourceTrace dependency requirement_source_FR_37_C_SE_02_1 from FR_37 to FrameworkConcerns::C_SE_02_1;
#sourceTrace dependency requirement_source_FR_37_C_EPS_11 from FR_37 to FrameworkConcerns::C_EPS_11;
#sourceTrace dependency requirement_source_FR_37_C_EPS_11_1 from FR_37 to FrameworkConcerns::C_EPS_11_1;
requirement <'FR-38'> FR_38 { subject framework : Framework; doc /* The framework shall assemble the designated requirement, decision, design, evidence, assumptions, uncertainty, validity limits, findings and dispositions into a baseline-linked review package. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-38"; sourceText = "The framework shall assemble the designated requirement, decision, design, evidence, assumptions, uncertainty, validity limits, findings and dispositions into a baseline-linked review package."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-SE-02,C-SE-02.1,C-EPS-11,C-EPS-11.1"; status = "proposed, verification pending"; citationRecord = "verification method I,D | proposed fixture: An independent reviewer locates the designated claims and evidence and records findings and outcomes. Keep author status, reviewer outcome and approval authority distinct."; }
#derivation connection derive_MR_10_FR_38 { end #original ::> FrameworkNeeds::MR_10; end #derive ::> FR_38; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_02_FR_38 { end #original ::> FrameworkNeeds::MR_02; end #derive ::> FR_38; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_38_C_SE_02 from FR_38 to FrameworkConcerns::C_SE_02;
#sourceTrace dependency requirement_source_FR_38_C_SE_02_1 from FR_38 to FrameworkConcerns::C_SE_02_1;
#sourceTrace dependency requirement_source_FR_38_C_EPS_11 from FR_38 to FrameworkConcerns::C_EPS_11;
#sourceTrace dependency requirement_source_FR_38_C_EPS_11_1 from FR_38 to FrameworkConcerns::C_EPS_11_1;
requirement <'FR-39'> FR_39 { subject framework : Framework; doc /* The framework shall declare prerequisites, resource footprint, licenses, dependencies and learning instructions for its minimum workflow and record adoption, adaptation, change, reproduction and direct-cost observations under one evaluation protocol. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-39"; sourceText = "The framework shall declare prerequisites, resource footprint, licenses, dependencies and learning instructions for its minimum workflow and record adoption, adaptation, change, reproduction and direct-cost observations under one evaluation protocol."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-01,C-PM-01.2,C-PM-05,C-SE-01.1,C-SE-01.1.1,C-EPS-02.1,C-NE-02.4,C-NE-02.4.1,C-NE-02.4.2"; status = "proposed, verification pending"; citationRecord = "verification method I,D | proposed fixture: Demonstrate the minimum workflow from a clean declared environment. Record wall-clock time separately from active person-hours and state the cost period and inclusions. Unknown cost stays unknown."; }
#derivation connection derive_MR_11_FR_39 { end #original ::> FrameworkNeeds::MR_11; end #derive ::> FR_39; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#derivation connection derive_MR_09_FR_39 { end #original ::> FrameworkNeeds::MR_09; end #derive ::> FR_39; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_39_C_PM_01 from FR_39 to FrameworkConcerns::C_PM_01;
#sourceTrace dependency requirement_source_FR_39_C_PM_01_2 from FR_39 to FrameworkConcerns::C_PM_01_2;
#sourceTrace dependency requirement_source_FR_39_C_PM_05 from FR_39 to FrameworkConcerns::C_PM_05;
#sourceTrace dependency requirement_source_FR_39_C_SE_01_1 from FR_39 to FrameworkConcerns::C_SE_01_1;
#sourceTrace dependency requirement_source_FR_39_C_SE_01_1_1 from FR_39 to FrameworkConcerns::C_SE_01_1_1;
#sourceTrace dependency requirement_source_FR_39_C_EPS_02_1 from FR_39 to FrameworkConcerns::C_EPS_02_1;
#sourceTrace dependency requirement_source_FR_39_C_NE_02_4 from FR_39 to FrameworkConcerns::C_NE_02_4;
#sourceTrace dependency requirement_source_FR_39_C_NE_02_4_1 from FR_39 to FrameworkConcerns::C_NE_02_4_1;
#sourceTrace dependency requirement_source_FR_39_C_NE_02_4_2 from FR_39 to FrameworkConcerns::C_NE_02_4_2;
requirement <'FR-40'> FR_40 { subject framework : Framework; doc /* The framework shall apply an identified common core to two predefined contrasting EPS cases using declared parameters, mappings and extensions and retain case outcomes and any core changes. */ require constraint statement { doc /* Informal proposed obligation. Semantic checking does not execute this constraint. */ } }
@SourceRecord { identifier = "FR-40"; sourceText = "The framework shall apply an identified common core to two predefined contrasting EPS cases using declared parameters, mappings and extensions and retain case outcomes and any core changes."; sourceLocator = "final_report/traceability/framework-baseline.json | source concerns: C-PM-05"; status = "proposed, verification pending"; citationRecord = "verification method I,D,T | proposed fixture: Complete the same declared workflow in both cases without undeclared or post hoc core changes. If the core changes, rebaseline and rerun both cases before a reuse claim. No implementation or successful outcome is asserted here."; }
#derivation connection derive_MR_11_FR_40 { end #original ::> FrameworkNeeds::MR_11; end #derive ::> FR_40; doc /* Author-reviewed derivation of framework support from the enterprise obligation. No verified implementation satisfaction is asserted. */ }
#sourceTrace dependency requirement_source_FR_40_C_PM_05 from FR_40 to FrameworkConcerns::C_PM_05;

}
