# Model scope and traceability

The implementation follows the equations and proposed selection method in `final_report/design-proposal.tex`. It implements a bounded subset of that design. `final_report/eps-requirements.tex` supplies the requirement meanings.

## Equations

| Proposal label | Demo use |
| --- | --- |
| `orbit-period`, `sunlight-period`, `eclipse-period`, `eclipse-geometry` | Circular orbit timing. Earth radius is 6378 km. Gravitational parameter is 398601 km³/s². A single contiguous sunlight interval starts at phase zero. This geometry has no beta-angle, attitude or seasonal model. |
| `minimum-panel-power` | Preliminary source power from sunlight/eclipse load energy and separate path-efficiency assumptions. Wh is divided by sunlight hours. |
| `solar-cell-eol-power`, `solar-cell-count`, `pv-integer-configuration` | EOL maximum-power cell estimate and upward-rounded count. This is a total-count lower bound. No series wiring, face packing or installation is inferred. |
| `battery-mission-cycles`, `battery-energy` | Mission cycling count and eclipse energy divided by declared DoD, with one preliminary degradation margin. The DoD is an engineering input. |
| `battery-cycle-life` | No fabricated fit is supplied. Required cycles are displayed. Cycle-life compliance remains unassessed without a sourced applicable model. |
| `battery-discharge-demand`, `battery-charge-acceptance`, `battery-energy-propagation` | Explicit energy-only propagation. Remaining energy capacity and a declared charge-power limit cap charging. Battery efficiency is applied once in the corresponding direction. |
| `nominal-energy-feasibility` | The energy-closure part is inspected. Energy reserve is a separate, explicitly declared scenario criterion. Charge SoC predicates remain unassessed. |
| `eps-product-budgets` | Known mass subtotals for unique selected physical products. Missing mass, auxiliaries and geometric evidence prevent a complete resource verdict. |
| `eps-feasible-catalog-set`, selection algorithm | Finite catalog screening retains incomplete and rejected alternatives. The demo does not establish the complete feasible set or rank unknown costs. |

Energy is presented in Wh. Time integration converts W·s to Wh using 3600 s/h. The full proposal uses J internally in its equations. The two representations are equivalent at this boundary.

## Energy boundary

`solar.installedPowerW` is the engineer-declared available EOL source power during sunlight. `topology.efficiency` is a constant conditioning efficiency. The scenario illumination factor scales source availability. EPS idle demand is added once at the common external battery boundary. Loads are constant-power values at that same simplified boundary.

The preliminary sunlight/eclipse efficiencies `Xs` and `Xe` belong to the sizing screen. They are not multiplied into the time simulation again. The battery model separately applies charge and discharge energy efficiencies.

The energy simulation does not derive the available power of a real installed panel from orientation, temperature, an I–V curve, DET bus voltage or shared MPPT tracker behavior. DET propagation is gated until such a model exists. Changing logical transfer/bus choices alone does not solve a detailed circuit.

Physical EOL capacity is `capacityWh × retainedEnergy`. Preliminary margin is not applied a second time. The declared battery discharge limit is independent of capacity. Exceeding a limit or exhausting energy remains a known failure. Numerical surplus is reported separately from a verified hardware curtailment capability.

The scenario's initial and minimum fractions refer to **normalized stored energy**. They do not define charge SoC or prove a cycle-life DoD limit. The UI and export retain this distinction.

## Requirement outcomes

| Requirements | Bounded demo evidence |
| --- | --- |
| EPS-01 to EPS-07 | Catalog capability and selected numerical screens where data exists. Complete configurations, electrical limits, chargers, rail supply, pulses and operating envelopes remain unassessed when decisive data is missing. |
| EPS-08 | Preliminary capacity calculation and retained-energy assumption. A passed numerical screen does not complete the physical pack assessment. |
| EPS-09 | Required mission cycles only. No invented cycle-life curve. |
| EPS-10 to EPS-12 | Energy history, reserve, power-limit and replenishment subchecks for the active scenario. Charge SoC and unsupported survival/recovery behavior remain gaps. Known energy violations fail. |
| EPS-13 to EPS-18 | No complete thermal, surplus-disposal, protection, control-state or service-interface verification. Explicit unassessed outcomes. |
| EPS-19 | Known physical mass subtotal with integrated-board deduplication. Missing auxiliaries, mass, volume or allocations remain visible. |
| EPS-20 | No installation geometry or array packing solution. Unassessed. |

## Revision semantics

Every graph node has an input revision and an evaluated revision. An input change increments the originating node and all transitive descendants once. Previously evaluated outputs stay visible with a stale label. New outputs with missing prerequisites stay locked. Evaluation requires valid inputs and current dependencies. Run-ready evaluation walks the DAG in topological order.

Energy plots retain the evaluated scenario revision, reserve and requested duration. Power-budget plots retain their original orbit timing. A stale history uses that saved context. It does not silently adopt newly edited criteria.

Mission analogue acceptance changes only the numerical altitude and retains an evidence receipt. ConOps drafts are saved as mission context. Altitude or ConOps edits clear an inconsistent prior receipt. Vector similarity is a retrieval rank and supplies no orbital suitability verdict.

Product allocation requires current catalog screening and excludes known rejected suggestions. An allocation may still have missing evidence. A product substitution renews applicable sizing and scenario assessments. Replacing a product with identical numerical properties still invalidates the assessment subject.

JSON import reconstructs known authored fields, validates structure and identifiers, and discards imported calculation caches. The current local catalog supplies product data after import. Exports include catalog revision, selected source records, node revisions and scope. No imported passing verdict is accepted as new evidence.

## Deliberate exclusions

KiCad exports contain opaque logical usage sheets and routed functional associations. Physical routing remains gated by reviewed terminals, footprints, connectivity and board constraints. Approved geometric rule sidecars retain their requirement/source derivations and fingerprint binding. They do not establish the correctness of those derivations or complete EPS requirements.

This demo does not implement the framework's future requirements concerning general AI assistance, full SysML modeling, inter-subsystem collaboration, formal phase reviews, F Prime, Omniverse, calibration, MIL, SIL, RAM, model credibility qualification or flight readiness. Their behavior remains undecided or outside this proof of concept.
