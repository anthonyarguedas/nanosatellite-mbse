# PA-CDT: CSRM digital thread for EPS engineering

This note supersedes the earlier steps 6 and 7 handoff. The source problem and concerns are baseline `b826d9915407bbd861d8d39b2558048f3d534bdc`.

The complete evidence, inventory, authority rules and planned allocations are in `custom.json`. The SysML comparison source is `../sysml/candidates/custom.sysml`.

All 40 framework leaves use the same nine logical capabilities and planned V01–V40 objectives. Intended allocation is distinct from implementation and verified satisfaction. Costs, adoption effort, correctness and model validity remain empirical questions.

## Decision status

Compared alternative. Explicit analyst reuse-first priority. No stakeholder preference or measured optimum asserted.

## Responsibility nodes

| ID | Node |
|---|---|
| CDT-LN1 | Engineering definition and configuration |
| CDT-LN2 | Analysis execution and model assurance |
| CDT-LN3 | Verification planning and decision communication |
| CDT-PN1 | Engineering workspace and controlled store |
| CDT-PN2 | Isolated Python analysis workspace |
| CDT-PN3 | Omniverse and Isaac extension workspace |

These are responsibility partitions. They do not imply a separate computer or executable for each node.

## Named physical inventory

| ID | Realization |
|---|---|
| CDT-C1 | CSRM-derived EPS library |
| CDT-C2 | Textual SysML v2 workbench |
| CDT-C3 | Controlled records and release store |
| CDT-C4 | Python workflow and contract checker |
| CDT-C5 | EPS and battery analysis pack |
| CDT-C6 | Domain and FMI adapters |
| CDT-C7 | Flight and ground software interface profiles |
| CDT-C8 | Engineering records and view templates |
| CDT-P1 | Tailor and accept an engineering baseline |
| CDT-P2 | Maintain candidates, BOM, and cost basis |
| CDT-P3 | Select models and execute/reproduce analyses |
| CDT-P4 | Prepare a V&V and safe fault plan |
| CDT-P5 | Review software contracts and sequences |
| CDT-P6 | Release evidence and onboard users |
| CDT-X1 | OpenUSD mapping and view package |
| CDT-X2 | NVIDIA Omniverse Kit review extension |
| CDT-X3 | Isaac controlled scenario adapter |
| CDT-X4 | USD/FMI/EPS coupling |
| CDT-X5 | External SIL, HIL, and telemetry expansion |
| CDT-H1 | CPU host |
| CDT-H2 | Persistent storage and separate backup |
| CDT-H3 | Clean independent reproduction environment |
| CDT-H4 | Compatible NVIDIA GPU environment |
| CDT-M01 | Requirement guidance and applicability editor |
| CDT-M02 | Semantic trace and change-impact query engine |
| CDT-M03 | Baseline registration and semantic transfer gate |
| CDT-M04 | Evidence-status and decision compiler |
| CDT-M05 | Occurrence BOM and scoped cost reducer |
| CDT-M06 | Mission scenario and EPS comparison harness |
| CDT-M07 | Battery and FMI coupling controller |
| CDT-M08 | Credibility, calibration and residual assessor |
| CDT-M09 | Observation quality and clock reconciler |
| CDT-M10 | RAM coverage and FMEA transformer |
| CDT-M11 | Verification proposal and readiness compiler |
| CDT-M12 | EPS service mapping and sequence assessor |
| CDT-M13 | Case, review and adoption packager |
| CDT-S01 | Controlled generic and case SysML v2 EPS model |
| CDT-S02 | Guidance, method and tailoring library |
| CDT-S03 | Requirement, decision and discrepancy records |
| CDT-S04 | Registration, mapping and released-baseline manifests |
| CDT-S05 | Component, quote and lifecycle characterization |
| CDT-S06 | Frozen scenario, analysis and run packages |
| CDT-S07 | Credibility, parameter and observation records |
| CDT-S08 | Verification, facility and safety specifications |
| CDT-S09 | Target software profiles and resource ledger |
| CDT-S10 | Case, review and framework evaluation records |
| CDT-P7 | Framework evaluation and constrained case tailoring |

Refer to the JSON for software/data/procedure facets, performers, execution/storage hosts, integrated dependencies, external services, maturity and unresolved checks.

## Planned requirement allocation

| Requirement | Logical responsibility | Intended physical realization | Planned verification |
|---|---|---|---|
| FR-01 | L02 | CDT-M01, CDT-C2, CDT-S03, CDT-P1 | V01 |
| FR-02 | L01, L09 | CDT-M01, CDT-C1, CDT-S02, CDT-P6 | V02 |
| FR-03 | L01, L07 | CDT-M01, CDT-M11, CDT-S02, CDT-S08, CDT-P1, CDT-P4 | V03 |
| FR-04 | L02, L08 | CDT-M02, CDT-S01, CDT-S03, CDT-S04, CDT-C2 | V04 |
| FR-05 | L02, L08 | CDT-M02, CDT-S04, CDT-S05, CDT-S09, CDT-S08, CDT-P1 | V05 |
| FR-06 | L02, L08 | CDT-M03, CDT-M04, CDT-C3, CDT-S03, CDT-S04, CDT-P1 | V06 |
| FR-07 | L08 | CDT-C3, CDT-M03, CDT-S04, CDT-H2 | V07 |
| FR-08 | L08 | CDT-M03, CDT-C6, CDT-S04 | V08 |
| FR-09 | L08, L06 | CDT-M03, CDT-M09, CDT-S04, CDT-S06, CDT-S07 | V09 |
| FR-10 | L05, L08, L09 | CDT-M06, CDT-M13, CDT-S04, CDT-S06, CDT-P3, CDT-P7, CDT-H3 | V10 |
| FR-11 | L02, L07, L09 | CDT-M04, CDT-S03, CDT-S07, CDT-S08, CDT-S10, CDT-P1 | V11 |
| FR-12 | L04 | CDT-M05, CDT-S01, CDT-S05, CDT-P2 | V12 |
| FR-13 | L04 | CDT-M05, CDT-S05, CDT-S06, CDT-P2 | V13 |
| FR-14 | L05, L04, L02 | CDT-M06, CDT-M04, CDT-M05, CDT-S06, CDT-S03, CDT-P2, CDT-P3 | V14 |
| FR-15 | L03 | CDT-C1, CDT-C2, CDT-S01, CDT-S02, CDT-P1 | V15 |
| FR-16 | L05, L03, L04 | CDT-M06, CDT-M07, CDT-C5, CDT-S01, CDT-S05, CDT-S06 | V16 |
| FR-17 | L02, L04 | CDT-M01, CDT-M05, CDT-S03, CDT-S05, CDT-S06, CDT-P1 | V17 |
| FR-18 | L03, L05, L08 | CDT-C6, CDT-M03, CDT-S01, CDT-S04, CDT-P3 | V18 |
| FR-19 | L05, L07 | CDT-M06, CDT-M07, CDT-M11, CDT-C5, CDT-S06, CDT-S08, CDT-P3 | V19 |
| FR-20 | L05, L06, L04 | CDT-M07, CDT-M08, CDT-C5, CDT-C6, CDT-S06, CDT-S07 | V20 |
| FR-21 | L06, L07 | CDT-M08, CDT-M04, CDT-S07, CDT-S08, CDT-P3 | V21 |
| FR-22 | L06, L04, L02 | CDT-M08, CDT-M09, CDT-M02, CDT-S05, CDT-S07, CDT-S03, CDT-P3 | V22 |
| FR-23 | L05, L06 | CDT-M06, CDT-M09, CDT-S06, CDT-S07, CDT-S08, CDT-P3 | V23 |
| FR-24 | L05, L06, L07 | CDT-M06, CDT-M07, CDT-M08, CDT-M11, CDT-S06, CDT-S07, CDT-S08, CDT-P3 | V24 |
| FR-25 | L06 | CDT-M08, CDT-M09, CDT-S07, CDT-S06, CDT-P3 | V25 |
| FR-26 | L02, L04, L07 | CDT-M10, CDT-M01, CDT-S03, CDT-S05, CDT-S08, CDT-P1, CDT-P3 | V26 |
| FR-27 | L04, L05, L08 | CDT-M10, CDT-M06, CDT-M03, CDT-S01, CDT-S05, CDT-S06, CDT-P3 | V27 |
| FR-28 | L07 | CDT-M11, CDT-S03, CDT-S08, CDT-P4 | V28 |
| FR-29 | L07, L09 | CDT-M11, CDT-M13, CDT-S08, CDT-P4 | V29 |
| FR-30 | L07 | CDT-M11, CDT-S08, CDT-P4 | V30 |
| FR-31 | L06, L08 | CDT-M09, CDT-M03, CDT-S07, CDT-S08, CDT-P3 | V31 |
| FR-32 | L06, L08 | CDT-M09, CDT-M03, CDT-S07, CDT-S04, CDT-P3 | V32 |
| FR-33 | L03 | CDT-C7, CDT-M12, CDT-M02, CDT-S01, CDT-S09, CDT-P5 | V33 |
| FR-34 | L03, L05 | CDT-M12, CDT-C6, CDT-S09, CDT-S06, CDT-P5 | V34 |
| FR-35 | L03, L05, L07 | CDT-M12, CDT-M06, CDT-M11, CDT-S01, CDT-S06, CDT-S08, CDT-P5 | V35 |
| FR-36 | L03, L04, L05 | CDT-M12, CDT-M06, CDT-S09, CDT-S05, CDT-P5 | V36 |
| FR-37 | L09 | CDT-C2, CDT-M13, CDT-S01, CDT-S04, CDT-S10, CDT-P6 | V37 |
| FR-38 | L09, L02, L08 | CDT-M13, CDT-M04, CDT-S03, CDT-S04, CDT-S05, CDT-S07, CDT-S08, CDT-S10, CDT-P6 | V38 |
| FR-39 | L09, L01, L08 | CDT-M13, CDT-S02, CDT-S04, CDT-S10, CDT-P6, CDT-P7, CDT-H1, CDT-H2, CDT-H3 | V39 |
| FR-40 | L09, L01, L08 | CDT-M13, CDT-C1, CDT-S01, CDT-S02, CDT-S04, CDT-S10, CDT-P1, CDT-P7 | V40 |

Each JSON allocation retains its realization mechanism, exact source locators and implementation gap. Framework verification, case EPS acceptance and project assessment have separate subjects.
