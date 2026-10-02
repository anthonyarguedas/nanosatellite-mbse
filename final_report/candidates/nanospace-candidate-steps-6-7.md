# PA-NS: Nanospace with controlled EPS model and analysis integration

This note supersedes the earlier steps 6 and 7 handoff. The source problem and concerns are baseline `b826d9915407bbd861d8d39b2558048f3d534bdc`.

The complete evidence, inventory, authority rules and planned allocations are in `nanospace.json`. The SysML comparison source is `../sysml/candidates/nanospace.sysml`.

All 40 framework leaves use the same nine logical capabilities and planned V01–V40 objectives. Intended allocation is distinct from implementation and verified satisfaction. Costs, adoption effort, correctness and model validity remain empirical questions.

## Decision status

Compared alternative. Explicit analyst reuse-first priority. No stakeholder preference or measured optimum asserted.

## Responsibility nodes

| ID | Node |
|---|---|
| NS-LN-A | Engineering authoring and participation |
| NS-LN-B | Concurrent engineering coordination |
| NS-LN-C | Controlled model, analysis and software integration |
| NS-LN-D | Configuration, evidence and publication |

These are responsibility partitions. They do not imply a separate computer or executable for each node.

## Named physical inventory

| ID | Realization |
|---|---|
| NS-C01 | Browser UI and Gaphor authoring tool |
| NS-C02 | Nanospace application and database stack |
| NS-C03 | Python model and data integration runner |
| NS-C04 | EPS schema, requirement aids and validators |
| NS-C05 | BOM and sourced financial cost module |
| NS-C06 | RAM model templates and adapter |
| NS-C07 | Coupled EPS/battery/controller tool and model suite |
| NS-C08 | Calibration, credibility and telemetry assessment |
| NS-C09 | Verification and technician package generator |
| NS-C10 | cFS/F-Prime common definition and sequence integration |
| NS-C11 | Configuration, evidence, replay and review publication service |
| NS-C12 | Generic and case model library |
| NS-C13 | Working graph and expanded engineering records |
| NS-C14 | Executable, credibility and environment packages |
| NS-C15 | Released evidence and framework evaluation records |
| NS-C16 | Requirement, criterion, catalog and RAM stewardship |
| NS-C17 | Controlled synchronization, change, run and reconstruction procedure |
| NS-C18 | Technician handover and safety procedure |
| NS-C19 | Release, review, adoption and operations procedure |
| NS-C20 | Participant and authoring workstation resources |
| NS-C21 | Application/database/storage/network resources |
| NS-C22 | Analysis and software build execution resources |
| NS-C23 | Calibrated facility and target reference resources |
| NS-C24 | Source-linked knowledge and learning catalogue |
| NS-C25 | Typed graph trace, change and claim-status controller |
| NS-C26 | Time-profile composer and virtual fixture scheduler |
| NS-C27 | EPS alternative comparison assembler |
| NS-C28 | Declared discipline execution and artifact adapter pack |
| NS-C29 | Specialist analysis execution services |
| NS-C30 | EPS software mapping and target profile records |
| NS-C31 | Case, core and evaluation protocol records |
| NS-C32 | Setup declaration and evaluation observation recorder |
| NS-C33 | EPS software build and configuration environments |

Refer to the JSON for software/data/procedure facets, performers, execution/storage hosts, integrated dependencies, external services, maturity and unresolved checks.

## Planned requirement allocation

| Requirement | Logical responsibility | Intended physical realization | Planned verification |
|---|---|---|---|
| FR-01 | L02 | NS-C01, NS-C04, NS-C12, NS-C13, NS-C16 | V01 |
| FR-02 | L01, L09 | NS-C04, NS-C16, NS-C19, NS-C24, NS-C31, NS-C32 | V02 |
| FR-03 | L01, L07 | NS-C04, NS-C09, NS-C16, NS-C24 | V03 |
| FR-04 | L02, L08 | NS-C02, NS-C12, NS-C13, NS-C15, NS-C25 | V04 |
| FR-05 | L02, L08 | NS-C03, NS-C13, NS-C17, NS-C25 | V05 |
| FR-06 | L02, L08 | NS-C11, NS-C13, NS-C15, NS-C17, NS-C25 | V06 |
| FR-07 | L08 | NS-C02, NS-C11, NS-C13, NS-C15, NS-C19 | V07 |
| FR-08 | L08 | NS-C03, NS-C04, NS-C13, NS-C17, NS-C28 | V08 |
| FR-09 | L08, L06 | NS-C08, NS-C11, NS-C14, NS-C15, NS-C28 | V09 |
| FR-10 | L05, L08, L09 | NS-C03, NS-C11, NS-C14, NS-C17, NS-C19, NS-C31 | V10 |
| FR-11 | L02, L07, L09 | NS-C04, NS-C09, NS-C13, NS-C15, NS-C25 | V11 |
| FR-12 | L04 | NS-C03, NS-C05, NS-C12, NS-C13, NS-C16 | V12 |
| FR-13 | L04 | NS-C05, NS-C13, NS-C15, NS-C16 | V13 |
| FR-14 | L05, L04, L02 | NS-C05, NS-C13, NS-C15, NS-C25, NS-C27 | V14 |
| FR-15 | L03 | NS-C01, NS-C04, NS-C12, NS-C31 | V15 |
| FR-16 | L05, L03, L04 | NS-C07, NS-C12, NS-C13, NS-C14, NS-C26, NS-C29 | V16 |
| FR-17 | L02, L04 | NS-C04, NS-C05, NS-C12, NS-C13, NS-C16, NS-C24 | V17 |
| FR-18 | L03, L05, L08 | NS-C03, NS-C04, NS-C12, NS-C14, NS-C28, NS-C29 | V18 |
| FR-19 | L05, L07 | NS-C07, NS-C09, NS-C14, NS-C18, NS-C26, NS-C29 | V19 |
| FR-20 | L05, L06, L04 | NS-C07, NS-C08, NS-C13, NS-C14, NS-C28, NS-C29 | V20 |
| FR-21 | L06, L07 | NS-C08, NS-C09, NS-C14, NS-C15 | V21 |
| FR-22 | L06, L04, L02 | NS-C08, NS-C13, NS-C14, NS-C17, NS-C25, NS-C28, NS-C29 | V22 |
| FR-23 | L05, L06 | NS-C07, NS-C08, NS-C14, NS-C28, NS-C29, NS-C30 | V23 |
| FR-24 | L05, L06, L07 | NS-C07, NS-C08, NS-C09, NS-C14, NS-C26, NS-C29 | V24 |
| FR-25 | L06 | NS-C08, NS-C12, NS-C14, NS-C15, NS-C25 | V25 |
| FR-26 | L02, L04, L07 | NS-C04, NS-C06, NS-C09, NS-C13, NS-C16 | V26 |
| FR-27 | L04, L05, L08 | NS-C03, NS-C06, NS-C12, NS-C13, NS-C14, NS-C29 | V27 |
| FR-28 | L07 | NS-C04, NS-C09, NS-C13, NS-C15, NS-C18 | V28 |
| FR-29 | L07, L09 | NS-C09, NS-C13, NS-C18, NS-C23 | V29 |
| FR-30 | L07 | NS-C09, NS-C13, NS-C18, NS-C23, NS-C25 | V30 |
| FR-31 | L06, L08 | NS-C04, NS-C08, NS-C14, NS-C15, NS-C18 | V31 |
| FR-32 | L06, L08 | NS-C04, NS-C08, NS-C14, NS-C15 | V32 |
| FR-33 | L03 | NS-C04, NS-C10, NS-C12, NS-C13, NS-C30 | V33 |
| FR-34 | L03, L05 | NS-C03, NS-C10, NS-C14, NS-C30, NS-C33 | V34 |
| FR-35 | L03, L05, L07 | NS-C07, NS-C09, NS-C10, NS-C12, NS-C14, NS-C26, NS-C30 | V35 |
| FR-36 | L03, L04, L05 | NS-C05, NS-C10, NS-C14, NS-C15, NS-C23, NS-C30, NS-C33 | V36 |
| FR-37 | L09 | NS-C01, NS-C03, NS-C11, NS-C12, NS-C15, NS-C19 | V37 |
| FR-38 | L09, L02, L08 | NS-C11, NS-C13, NS-C15, NS-C19, NS-C25 | V38 |
| FR-39 | L09, L01, L08 | NS-C11, NS-C19, NS-C20, NS-C21, NS-C22, NS-C24, NS-C31, NS-C32 | V39 |
| FR-40 | L09, L01, L08 | NS-C04, NS-C11, NS-C12, NS-C14, NS-C19, NS-C31, NS-C32 | V40 |

Each JSON allocation retains its realization mechanism, exact source locators and implementation gap. Framework verification, case EPS acceptance and project assessment have separate subjects.
