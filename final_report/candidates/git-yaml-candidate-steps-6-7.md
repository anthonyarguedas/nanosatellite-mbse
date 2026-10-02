# PA-GY: Lightweight Git and YAML engineering framework

This note supersedes the earlier steps 6 and 7 handoff. The source problem and concerns are baseline `b826d9915407bbd861d8d39b2558048f3d534bdc`.

The complete evidence, inventory, authority rules and planned allocations are in `git-yaml.json`. The SysML comparison source is `../sysml/candidates/git-yaml.sysml`.

All 40 framework leaves use the same nine logical capabilities and planned V01–V40 objectives. Intended allocation is distinct from implementation and verified satisfaction. Costs, adoption effort, correctness and model validity remain empirical questions.

## Decision status

Compared alternative. Explicit analyst reuse-first priority. No stakeholder preference or measured optimum asserted.

## Responsibility nodes

| ID | Node |
|---|---|
| GY-N1 | Engineering definition and decision support |
| GY-N2 | Configuration and dependency control |
| GY-N3 | Analysis and implementation integration |
| GY-N4 | Review and verification evidence delivery |

These are responsibility partitions. They do not imply a separate computer or executable for each node.

## Named physical inventory

| ID | Realization |
|---|---|
| GY-C1 | Git repository and review tooling |
| GY-C2 | Engineering schema and reusable examples |
| GY-C3 | Python validation and change service |
| GY-C4 | Document and view generator |
| GY-C5 | Controlled task runner and tool adapters |
| GY-C6 | EPS analysis assets and configured runtimes |
| GY-C7 | Flight/ground definition exporters and test harness |
| GY-C8 | Evidence artifacts and execution manifests |
| GY-C9 | Authoring, change, review and onboarding playbook |
| GY-C10 | Calibration and facility handoff playbook |
| GY-C11 | Declared computing and storage resources |
| GY-C12 | Requirement and method record profile |
| GY-C13 | Typed trace index and change engine |
| GY-C14 | Transfer, provenance and release gate |
| GY-C15 | Component characterization and BOM/cost module |
| GY-C16 | Scenario, battery and controller SIL harness |
| GY-C17 | Credibility, calibration and anomaly module |
| GY-C18 | Discipline exchange adapters and profiles |
| GY-C19 | RAM coverage and FMEA transformation module |
| GY-C20 | Verification specification and safety package builder |
| GY-C21 | Observation timing and quality module |
| GY-C22 | Target build and resource evidence adapter |
| GY-C23 | Case and evaluation manifest manager |
| GY-C24 | Generic EPS architecture and service record library |
| GY-C25 | PyBaMM battery runtime dependency |

Refer to the JSON for software/data/procedure facets, performers, execution/storage hosts, integrated dependencies, external services, maturity and unresolved checks.

## Planned requirement allocation

| Requirement | Logical responsibility | Intended physical realization | Planned verification |
|---|---|---|---|
| FR-01 | L02 | GY-C12, GY-C2, GY-C14 | V01 |
| FR-02 | L01, L09 | GY-C12, GY-C9, GY-C4, GY-C23 | V02 |
| FR-03 | L01, L07 | GY-C12, GY-C20, GY-C9 | V03 |
| FR-04 | L02, L08 | GY-C12, GY-C13, GY-C3, GY-C8 | V04 |
| FR-05 | L02, L08 | GY-C13, GY-C15, GY-C24, GY-C7, GY-C20 | V05 |
| FR-06 | L02, L08 | GY-C13, GY-C14, GY-C1, GY-C8, GY-C9 | V06 |
| FR-07 | L08 | GY-C1, GY-C14, GY-C8 | V07 |
| FR-08 | L08 | GY-C14, GY-C3, GY-C18, GY-C2 | V08 |
| FR-09 | L08, L06 | GY-C14, GY-C8, GY-C17, GY-C21 | V09 |
| FR-10 | L05, L08, L09 | GY-C5, GY-C16, GY-C8, GY-C9, GY-C23 | V10 |
| FR-11 | L02, L07, L09 | GY-C13, GY-C20, GY-C4, GY-C8 | V11 |
| FR-12 | L04 | GY-C15, GY-C24, GY-C2, GY-C4 | V12 |
| FR-13 | L04 | GY-C15, GY-C2, GY-C4 | V13 |
| FR-14 | L05, L04, L02 | GY-C16, GY-C15, GY-C12, GY-C17, GY-C20, GY-C4 | V14 |
| FR-15 | L03 | GY-C24, GY-C12, GY-C2, GY-C23 | V15 |
| FR-16 | L05, L03, L04 | GY-C16, GY-C24, GY-C15, GY-C25, GY-C6 | V16 |
| FR-17 | L02, L04 | GY-C12, GY-C15, GY-C16, GY-C9 | V17 |
| FR-18 | L03, L05, L08 | GY-C18, GY-C14, GY-C5, GY-C24 | V18 |
| FR-19 | L05, L07 | GY-C16, GY-C20, GY-C5, GY-C17, GY-C25 | V19 |
| FR-20 | L05, L06, L04 | GY-C16, GY-C25, GY-C17, GY-C15 | V20 |
| FR-21 | L06, L07 | GY-C17, GY-C20, GY-C10, GY-C8 | V21 |
| FR-22 | L06, L04, L02 | GY-C17, GY-C21, GY-C13, GY-C14, GY-C10 | V22 |
| FR-23 | L05, L06 | GY-C16, GY-C17, GY-C21, GY-C8 | V23 |
| FR-24 | L05, L06, L07 | GY-C16, GY-C25, GY-C17, GY-C20 | V24 |
| FR-25 | L06 | GY-C17, GY-C21, GY-C16, GY-C8 | V25 |
| FR-26 | L02, L04, L07 | GY-C12, GY-C19, GY-C15, GY-C20 | V26 |
| FR-27 | L04, L05, L08 | GY-C19, GY-C24, GY-C15, GY-C14 | V27 |
| FR-28 | L07 | GY-C20, GY-C12, GY-C2, GY-C8 | V28 |
| FR-29 | L07, L09 | GY-C20, GY-C4, GY-C10, GY-C24 | V29 |
| FR-30 | L07 | GY-C20, GY-C10, GY-C15, GY-C8 | V30 |
| FR-31 | L06, L08 | GY-C21, GY-C14, GY-C8 | V31 |
| FR-32 | L06, L08 | GY-C21, GY-C14, GY-C8 | V32 |
| FR-33 | L03 | GY-C24, GY-C7, GY-C14, GY-C2 | V33 |
| FR-34 | L03, L05 | GY-C7, GY-C24, GY-C22, GY-C14 | V34 |
| FR-35 | L03, L05, L07 | GY-C7, GY-C24, GY-C16, GY-C20 | V35 |
| FR-36 | L03, L04, L05 | GY-C22, GY-C7, GY-C15, GY-C8 | V36 |
| FR-37 | L09 | GY-C4, GY-C24, GY-C14 | V37 |
| FR-38 | L09, L02, L08 | GY-C4, GY-C8, GY-C12, GY-C20, GY-C9 | V38 |
| FR-39 | L09, L01, L08 | GY-C23, GY-C9, GY-C11, GY-C1, GY-C6 | V39 |
| FR-40 | L09, L01, L08 | GY-C23, GY-C24, GY-C1, GY-C8, GY-C9 | V40 |

Each JSON allocation retains its realization mechanism, exact source locators and implementation gap. Framework verification, case EPS acceptance and project assessment have separate subjects.
