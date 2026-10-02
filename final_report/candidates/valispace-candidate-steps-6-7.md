# PA-VS: Capella and Valispace with controlled analysis and evidence

This note supersedes the earlier steps 6 and 7 handoff. The source problem and concerns are baseline `b826d9915407bbd861d8d39b2558048f3d534bdc`.

The complete evidence, inventory, authority rules and planned allocations are in `valispace.json`. The SysML comparison source is `../sysml/candidates/valispace.sysml`.

All 40 framework leaves use the same nine logical capabilities and planned V01–V40 objectives. Intended allocation is distinct from implementation and verified satisfaction. Costs, adoption effort, correctness and model validity remain empirical questions.

## Decision status

Conditionally selected for detailed design. Explicit analyst reuse-first priority. No stakeholder preference or measured optimum asserted.

## Responsibility nodes

| ID | Node |
|---|---|
| VS-LN-ENG | Shared engineering and review |
| VS-LN-ARCH | Architecture and interfaces |
| VS-LN-ANALYSIS | Analysis and verification coordination |
| VS-LN-ASSURANCE | Configuration and evidence assurance |

These are responsibility partitions. They do not imply a separate computer or executable for each node.

## Named physical inventory

| ID | Realization |
|---|---|
| VS-PC-WEB | Valispace engineering service |
| VS-PC-CAPELLA | Capella architecture environment |
| VS-PC-BRIDGE | Controlled Python integration workflow |
| VS-PC-RUNNER | Controlled analysis launcher and result importer |
| VS-PC-FSW | Common flight/ground definition and assurance package |
| VS-PC-ARCHIVE | Controlled artifact store and export/import utility |
| VS-PC-CASE | Case engineering records |
| VS-PC-CONTRACT | Exchange and baseline contracts |
| VS-PC-MODELS | Analysis and credibility packages |
| VS-PC-EVIDENCE | Released evidence records |
| VS-PC-PROCEDURES | Framework operating procedures |
| VS-PC-HOSTS | Existing engineering compute, network and storage |
| VS-PC-GUIDANCE | Guidance and method catalogue |
| VS-PC-GOVERNANCE | Valispace governance schema and trace-impact extension |
| VS-PC-CHARACTERIZATION | Component, BOM and cost property package |
| VS-PC-EPS-TEMPLATE | Generic Capella EPS template and case bindings |
| VS-PC-SCENARIO | Time-indexed scenario composer and virtual test harness |
| VS-PC-EPS-ENGINE | Integrated OpenModelica EPS analysis backend |
| VS-PC-CREDIBILITY | Calibration, validity and residual assessment module |
| VS-PC-OBSERVATION | Observation clock and channel-quality importer |
| VS-PC-RAM | Capella-to-FMEA transformation and RAM coverage module |
| VS-PC-VERIFICATION | Valispace verification specification and readiness module |
| VS-PC-REVIEW | Baseline-linked review projection and feedback procedure |
| VS-PC-EVALUATION | Adoption and frozen-core two-case evaluation package |
| VS-HOST-VALI | Valispace service host |
| VS-HOST-ENG | Engineering workstation |
| VS-HOST-STORE | Managed evidence volume |
| VS-HOST-SPECIALIST | Declared discipline service environment |
| VS-HOST-FLIGHTBUILD | Flight software build and target evidence environment |

Refer to the JSON for software/data/procedure facets, performers, execution/storage hosts, integrated dependencies, external services, maturity and unresolved checks.

## Planned requirement allocation

| Requirement | Logical responsibility | Intended physical realization | Planned verification |
|---|---|---|---|
| FR-01 | L02 | VS-PC-WEB, VS-PC-GOVERNANCE, VS-PC-CASE, VS-PC-GUIDANCE | V01 |
| FR-02 | L01, L09 | VS-PC-GUIDANCE, VS-PC-WEB, VS-PC-PROCEDURES, VS-PC-EVALUATION | V02 |
| FR-03 | L01, L07 | VS-PC-GUIDANCE, VS-PC-VERIFICATION, VS-PC-CASE | V03 |
| FR-04 | L02, L08 | VS-PC-GOVERNANCE, VS-PC-BRIDGE, VS-PC-CONTRACT, VS-PC-ARCHIVE | V04 |
| FR-05 | L02, L08 | VS-PC-GOVERNANCE, VS-PC-BRIDGE, VS-PC-CONTRACT, VS-PC-CASE | V05 |
| FR-06 | L02, L08 | VS-PC-GOVERNANCE, VS-PC-ARCHIVE, VS-PC-CONTRACT, VS-PC-PROCEDURES | V06 |
| FR-07 | L08 | VS-PC-ARCHIVE, VS-PC-CONTRACT, VS-PC-BRIDGE, VS-PC-PROCEDURES | V07 |
| FR-08 | L08 | VS-PC-BRIDGE, VS-PC-CONTRACT, VS-PC-ARCHIVE | V08 |
| FR-09 | L08, L06 | VS-PC-CONTRACT, VS-PC-EVIDENCE, VS-PC-ARCHIVE, VS-PC-CREDIBILITY, VS-PC-OBSERVATION | V09 |
| FR-10 | L05, L08, L09 | VS-PC-SCENARIO, VS-PC-RUNNER, VS-PC-ARCHIVE, VS-PC-MODELS, VS-PC-EVALUATION | V10 |
| FR-11 | L02, L07, L09 | VS-PC-GOVERNANCE, VS-PC-VERIFICATION, VS-PC-REVIEW, VS-PC-EVIDENCE | V11 |
| FR-12 | L04 | VS-PC-CHARACTERIZATION, VS-PC-WEB, VS-PC-CASE, VS-PC-BRIDGE | V12 |
| FR-13 | L04 | VS-PC-CHARACTERIZATION, VS-PC-WEB, VS-PC-CASE | V13 |
| FR-14 | L05, L04, L02 | VS-PC-SCENARIO, VS-PC-CHARACTERIZATION, VS-PC-GOVERNANCE, VS-PC-WEB, VS-PC-CREDIBILITY | V14 |
| FR-15 | L03 | VS-PC-EPS-TEMPLATE, VS-PC-CAPELLA, VS-PC-CASE, VS-PC-WEB, VS-PC-CONTRACT | V15 |
| FR-16 | L05, L03, L04 | VS-PC-SCENARIO, VS-PC-EPS-ENGINE, VS-PC-MODELS, VS-PC-CHARACTERIZATION, VS-PC-EPS-TEMPLATE | V16 |
| FR-17 | L02, L04 | VS-PC-GOVERNANCE, VS-PC-CHARACTERIZATION, VS-PC-GUIDANCE, VS-PC-CASE | V17 |
| FR-18 | L03, L05, L08 | VS-PC-BRIDGE, VS-PC-CONTRACT, VS-PC-RUNNER, VS-PC-CAPELLA, VS-PC-ARCHIVE | V18 |
| FR-19 | L05, L07 | VS-PC-SCENARIO, VS-PC-EPS-ENGINE, VS-PC-VERIFICATION, VS-PC-MODELS, VS-PC-EVIDENCE | V19 |
| FR-20 | L05, L06, L04 | VS-PC-EPS-ENGINE, VS-PC-SCENARIO, VS-PC-MODELS, VS-PC-CREDIBILITY, VS-PC-CHARACTERIZATION | V20 |
| FR-21 | L06, L07 | VS-PC-CREDIBILITY, VS-PC-VERIFICATION, VS-PC-MODELS, VS-PC-EVIDENCE | V21 |
| FR-22 | L06, L04, L02 | VS-PC-CREDIBILITY, VS-PC-OBSERVATION, VS-PC-CHARACTERIZATION, VS-PC-GOVERNANCE, VS-PC-MODELS | V22 |
| FR-23 | L05, L06 | VS-PC-SCENARIO, VS-PC-CREDIBILITY, VS-PC-RUNNER, VS-PC-MODELS, VS-PC-OBSERVATION | V23 |
| FR-24 | L05, L06, L07 | VS-PC-SCENARIO, VS-PC-EPS-ENGINE, VS-PC-CREDIBILITY, VS-PC-VERIFICATION, VS-PC-MODELS | V24 |
| FR-25 | L06 | VS-PC-CREDIBILITY, VS-PC-OBSERVATION, VS-PC-MODELS, VS-PC-EVIDENCE | V25 |
| FR-26 | L02, L04, L07 | VS-PC-GOVERNANCE, VS-PC-RAM, VS-PC-CHARACTERIZATION, VS-PC-VERIFICATION | V26 |
| FR-27 | L04, L05, L08 | VS-PC-RAM, VS-PC-CAPELLA, VS-PC-CHARACTERIZATION, VS-PC-CONTRACT, VS-PC-MODELS | V27 |
| FR-28 | L07 | VS-PC-VERIFICATION, VS-PC-WEB, VS-PC-CASE, VS-PC-EVIDENCE | V28 |
| FR-29 | L07, L09 | VS-PC-VERIFICATION, VS-PC-REVIEW, VS-PC-ARCHIVE, VS-PC-PROCEDURES | V29 |
| FR-30 | L07 | VS-PC-VERIFICATION, VS-PC-CASE, VS-PC-PROCEDURES, VS-PC-EVIDENCE | V30 |
| FR-31 | L06, L08 | VS-PC-OBSERVATION, VS-PC-CONTRACT, VS-PC-EVIDENCE, VS-PC-ARCHIVE | V31 |
| FR-32 | L06, L08 | VS-PC-OBSERVATION, VS-PC-CONTRACT, VS-PC-EVIDENCE, VS-PC-ARCHIVE | V32 |
| FR-33 | L03 | VS-PC-FSW, VS-PC-CAPELLA, VS-PC-CONTRACT, VS-PC-CASE | V33 |
| FR-34 | L03, L05 | VS-PC-FSW, VS-PC-RUNNER, VS-PC-CONTRACT, VS-PC-EVIDENCE | V34 |
| FR-35 | L03, L05, L07 | VS-PC-FSW, VS-PC-SCENARIO, VS-PC-VERIFICATION, VS-PC-CAPELLA, VS-PC-EVIDENCE | V35 |
| FR-36 | L03, L04, L05 | VS-PC-FSW, VS-PC-CHARACTERIZATION, VS-PC-SCENARIO, VS-PC-EVIDENCE, VS-PC-CONTRACT | V36 |
| FR-37 | L09 | VS-PC-REVIEW, VS-PC-CAPELLA, VS-PC-WEB, VS-PC-CASE, VS-PC-CONTRACT | V37 |
| FR-38 | L09, L02, L08 | VS-PC-REVIEW, VS-PC-GOVERNANCE, VS-PC-ARCHIVE, VS-PC-EVIDENCE, VS-PC-CONTRACT | V38 |
| FR-39 | L09, L01, L08 | VS-PC-EVALUATION, VS-PC-GUIDANCE, VS-PC-PROCEDURES, VS-PC-CONTRACT, VS-PC-HOSTS | V39 |
| FR-40 | L09, L01, L08 | VS-PC-EVALUATION, VS-PC-GUIDANCE, VS-PC-EPS-TEMPLATE, VS-PC-CASE, VS-PC-CONTRACT, VS-PC-ARCHIVE | V40 |

Each JSON allocation retains its realization mechanism, exact source locators and implementation gap. Framework verification, case EPS acceptance and project assessment have separate subjects.
