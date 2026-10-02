# PA-COM: COMET concurrent engineering with assurance and analysis services

This note supersedes the earlier steps 6 and 7 handoff. The source problem and concerns are baseline `b826d9915407bbd861d8d39b2558048f3d534bdc`.

The complete evidence, inventory, authority rules and planned allocations are in `comet.json`. The SysML comparison source is `../sysml/candidates/comet.sysml`.

All 40 framework leaves use the same nine logical capabilities and planned V01–V40 objectives. Intended allocation is distinct from implementation and verified satisfaction. Costs, adoption effort, correctness and model validity remain empirical questions.

## Decision status

Compared alternative. Explicit analyst reuse-first priority. No stakeholder preference or measured optimum asserted.

## Responsibility nodes

| ID | Node |
|---|---|
| COM-N1 | Participant and review |
| COM-N2 | Study and reference |
| COM-N3 | Assurance and evidence |
| COM-N4 | Engineering execution |

These are responsibility partitions. They do not imply a separate computer or executable for each node.

## Named physical inventory

| ID | Realization |
|---|---|
| COM-S01 | COMET server and native persistence |
| COM-S02 | COMET IME |
| COM-S03 | Microsoft Excel host |
| COM-S04 | COMET Excel add-in |
| COM-S05 | COMET exchange adapter |
| COM-S06 | Python assurance runner |
| COM-S07 | Discipline execution adapters |
| COM-S08 | RAM adapter |
| COM-S09 | Common software contract checker and cFS/F-Prime adapters |
| COM-S10 | Measurement ingestion/validation |
| COM-S11 | Review generator |
| COM-S12 | Controlled companion repository and artifact retention |
| COM-D01 | Site Directory and reference/category mapping definitions |
| COM-D02 | CubeSat/EPS Template Model |
| COM-D03 | Model Catalogue |
| COM-D04 | Study Model and requirement/compliance records |
| COM-D05 | Typed companion contracts |
| COM-D06 | Solver interfaces, case models and credibility records |
| COM-D07 | Run bundles |
| COM-D08 | Released snapshots, changes and review records |
| COM-D09 | Framework core and evaluation/onboarding records |
| COM-P01 | Tailoring and requirement author learning |
| COM-P02 | Catalogue, BOM and cost upkeep |
| COM-P03 | Moderated concurrent sessions and conflict resolution |
| COM-P04 | Semantic checks, releases and change/evidence control |
| COM-P05 | Credible analysis, RAM and software workflow |
| COM-P06 | Technician proposal and supplied-evidence handoff |
| COM-P07 | Independent reproduction, review and frozen-core evaluation |
| COM-H01 | Participant workstation |
| COM-H02 | COMET server compute and storage |
| COM-H03 | Runner compute and retained artifact storage |
| COM-H04 | Network and backup storage |
| COM-S13 | Requirement and method-profile validator |
| COM-S14 | Typed trace, impact and claim-status module |
| COM-S15 | Semantic registration and release-manifest module |
| COM-S16 | Scenario composition and coupling coordinator |
| COM-S17 | Credibility, calibration and residual assessment module |
| COM-S18 | Verification specification and readiness gate |
| COM-D10 | Requirement, decision and relation extensions |
| COM-D11 | BOM, cost, derivation and comparison workbooks |
| COM-D12 | Generic EPS architecture and software service contracts |
| COM-D13 | Scenario, exchange and execution profiles |
| COM-D14 | Model applicability, calibration and observation records |
| COM-D15 | RAM coverage and transformation records |
| COM-D16 | Verification, facility and safety specifications |
| COM-D17 | Sourced method catalogue and guided examples |
| COM-D18 | Case/core and evaluation declarations |
| COM-P08 | Method and criterion adjudication |
| COM-P09 | Calibration and model-applicability review |
| COM-P10 | RAM dependency and coverage review |

Refer to the JSON for software/data/procedure facets, performers, execution/storage hosts, integrated dependencies, external services, maturity and unresolved checks.

## Planned requirement allocation

| Requirement | Logical responsibility | Intended physical realization | Planned verification |
|---|---|---|---|
| FR-01 | L02 | COM-S01, COM-S02, COM-S13, COM-D04, COM-D10, COM-P01, COM-P08 | V01 |
| FR-02 | L01, L09 | COM-S02, COM-S03, COM-D02, COM-D17, COM-D18, COM-P01 | V02 |
| FR-03 | L01, L07 | COM-S13, COM-D17, COM-D16, COM-P08 | V03 |
| FR-04 | L02, L08 | COM-S05, COM-S14, COM-S15, COM-D04, COM-D10, COM-D07, COM-D08, COM-P04 | V04 |
| FR-05 | L02, L08 | COM-S14, COM-D10, COM-D12, COM-D11, COM-D13, COM-D16, COM-D08, COM-P03, COM-P04 | V05 |
| FR-06 | L02, L08 | COM-S14, COM-S15, COM-S12, COM-D10, COM-D08, COM-D07, COM-P04 | V06 |
| FR-07 | L08 | COM-S05, COM-S15, COM-S12, COM-D04, COM-D08, COM-D07, COM-P04 | V07 |
| FR-08 | L08 | COM-S05, COM-S15, COM-D01, COM-D05, COM-D13, COM-D08, COM-P04 | V08 |
| FR-09 | L08, L06 | COM-S15, COM-S10, COM-S07, COM-D07, COM-D14, COM-D08, COM-P04 | V09 |
| FR-10 | L05, L08, L09 | COM-S03, COM-S04, COM-S16, COM-S15, COM-S12, COM-D11, COM-D13, COM-D07, COM-D18, COM-P07 | V10 |
| FR-11 | L02, L07, L09 | COM-S14, COM-S18, COM-S17, COM-S11, COM-D10, COM-D14, COM-D16, COM-D08, COM-P04 | V11 |
| FR-12 | L04 | COM-S01, COM-S03, COM-S04, COM-D03, COM-D04, COM-D11, COM-P02 | V12 |
| FR-13 | L04 | COM-S03, COM-S04, COM-D03, COM-D11, COM-P02 | V13 |
| FR-14 | L05, L04, L02 | COM-S03, COM-S16, COM-S14, COM-D11, COM-D13, COM-D07, COM-D10, COM-P02, COM-P05 | V14 |
| FR-15 | L03 | COM-S01, COM-S02, COM-S13, COM-D01, COM-D02, COM-D04, COM-D12, COM-D18, COM-P01 | V15 |
| FR-16 | L05, L03, L04 | COM-S16, COM-S07, COM-D04, COM-D12, COM-D13, COM-D06, COM-P05 | V16 |
| FR-17 | L02, L04 | COM-S03, COM-S13, COM-D03, COM-D11, COM-D10, COM-D17, COM-P08 | V17 |
| FR-18 | L03, L05, L08 | COM-S05, COM-S07, COM-S15, COM-D12, COM-D13, COM-D06, COM-D07, COM-P05 | V18 |
| FR-19 | L05, L07 | COM-S16, COM-S07, COM-S18, COM-D13, COM-D16, COM-D07, COM-P05 | V19 |
| FR-20 | L05, L06, L04 | COM-S16, COM-S07, COM-S17, COM-D03, COM-D06, COM-D13, COM-D14, COM-D07, COM-P05, COM-P09 | V20 |
| FR-21 | L06, L07 | COM-S17, COM-S18, COM-D06, COM-D14, COM-D16, COM-D07, COM-P09 | V21 |
| FR-22 | L06, L04, L02 | COM-S17, COM-S07, COM-S14, COM-D03, COM-D14, COM-D07, COM-D10, COM-P09 | V22 |
| FR-23 | L05, L06 | COM-S16, COM-S17, COM-S10, COM-D13, COM-D14, COM-D07, COM-P05, COM-P09 | V23 |
| FR-24 | L05, L06, L07 | COM-S16, COM-S07, COM-S17, COM-S18, COM-D13, COM-D14, COM-D16, COM-D07, COM-P05, COM-P09 | V24 |
| FR-25 | L06 | COM-S10, COM-S17, COM-D12, COM-D14, COM-D07, COM-P09 | V25 |
| FR-26 | L02, L04, L07 | COM-S13, COM-S08, COM-S18, COM-D10, COM-D03, COM-D15, COM-D16, COM-P08, COM-P10 | V26 |
| FR-27 | L04, L05, L08 | COM-S08, COM-S16, COM-S15, COM-D04, COM-D12, COM-D15, COM-D13, COM-D07, COM-P10 | V27 |
| FR-28 | L07 | COM-S13, COM-S18, COM-D10, COM-D16, COM-P06, COM-P08 | V28 |
| FR-29 | L07, L09 | COM-S18, COM-S11, COM-D12, COM-D16, COM-D18, COM-P06 | V29 |
| FR-30 | L07 | COM-S18, COM-D03, COM-D16, COM-D08, COM-P06 | V30 |
| FR-31 | L06, L08 | COM-S10, COM-S15, COM-D13, COM-D14, COM-D07, COM-P06 | V31 |
| FR-32 | L06, L08 | COM-S10, COM-S15, COM-D12, COM-D14, COM-D07, COM-P06 | V32 |
| FR-33 | L03 | COM-S09, COM-S15, COM-D12, COM-D04, COM-D08, COM-P05 | V33 |
| FR-34 | L03, L05 | COM-S09, COM-S16, COM-D12, COM-D13, COM-D07, COM-P05 | V34 |
| FR-35 | L03, L05, L07 | COM-S09, COM-S16, COM-S18, COM-D12, COM-D13, COM-D16, COM-D07, COM-P05 | V35 |
| FR-36 | L03, L04, L05 | COM-S09, COM-S16, COM-D12, COM-D13, COM-D03, COM-D07, COM-P05 | V36 |
| FR-37 | L09 | COM-S02, COM-S11, COM-D04, COM-D12, COM-D08, COM-P07 | V37 |
| FR-38 | L09, L02, L08 | COM-S11, COM-S14, COM-S15, COM-D10, COM-D11, COM-D14, COM-D16, COM-D08, COM-P03, COM-P07 | V38 |
| FR-39 | L09, L01, L08 | COM-S02, COM-S03, COM-S11, COM-S15, COM-D17, COM-D18, COM-D09, COM-P01, COM-P07 | V39 |
| FR-40 | L09, L01, L08 | COM-S01, COM-S02, COM-S15, COM-D02, COM-D04, COM-D12, COM-D18, COM-D09, COM-P01, COM-P07 | V40 |

Each JSON allocation retains its realization mechanism, exact source locators and implementation gap. Framework verification, case EPS acceptance and project assessment have separate subjects.
