# BIRDS-4 scenario basis

The example is a **BIRDS-4-inspired concept study**, not a reconstructed flight EPS or a replay of flight telemetry. COTS alternatives in this demo are not claimed to have flown on BIRDS-4.

## Source

H. R. Shrestha, BIRDS-4 Project Members, G. Maeda, S. Kim, H. Masui, T. Yamauchi and M. Cho, *BIRDS-4 1U CubeSat Missions and On-Orbit Results*, 11th Nano-Satellite Symposium, 2022.

Public conference PDF: <https://nanosat11th.itu.edu.tr/assets/papers/BIRDS-4.pdf>. Retrieved successfully on 2026-10-17. SHA-256: `e344753dac510b9e42ff70cd455dcfb72e2168ceb15bfc25d15c1f0bc1cebcaf`.

The source is also present in the user's local corpus as citation candidate 2055. The full six-page text was read, including the distinctions between planned activities, demonstrated operations and failed payload exchanges.

## Sourced context

- BIRDS-4 comprised GuaraniSat-1, Maya-2 and Tsuru, three 1U CubeSats deployed from the ISS on 14 March 2021 (§§1–2).
- Its mission list includes camera imaging, APRS digipeating, store and forward, Hentenna, radiation and latch-up experiments, perovskite solar-cell measurements and attitude demonstrations (§3).
- The bus includes OBC, EPS, communications, front/rear access boards and mission boards (§4).
- The camera section discusses imaging at 400 km altitude (§5.1). The demo uses **400 km as a representative circular reference altitude**, not a precise historical orbit, epoch or complete ISS deployment state. The one-year design lifetime is a demo assumption.
- The paper reports a power-budget imbalance in its generation-shortfall discussion (§5). This motivates a separate reduced-generation example. Its reported 1604, 1202 and 1438 mWh figures are not copied into a simulation boundary or interval that the demo has not independently established.
- APRS was demonstrated. The SF-WARD flight data exchange failed because of the reported packet-mode mismatch (§§5.2–5.3). The demo's combined APRS/SF-WARD row represents planned operations, not a claim of successful SF-WARD flight service.
- The ADCS section reports reaction-wheel activations of one through four minutes on different dates, while several stabilization/pointing functions were not activated (§5.6). The example's actuator windows are illustrative. They do not claim simultaneous historical operations or working closed-loop pointing.

## Authored numerical assumptions

Every component power, idle state, supply-rail assignment, phase window, duty cycle, simultaneous demand, illumination multiplier, initial energy, energy reserve and assessment duration in `scenarios.ts` is an editable **demonstration assumption**. No per-mode measured BIRDS-4 load table was established for these values.

The example does not represent the original BIRDS-4 NiMH pack, solar installation or charger. The source's hardware identities remain mission context. The default COTS allocations below are explicit **illustrative substitutions**, never flight-hardware identifications. Manufacturer numbers retain their conditions and meanings. Adopting a typical value in the energy model establishes no guaranteed bound.

## Evaluated illustrative default

`birds4.ts` exports the mission basis, editable inputs, proposed default allocations and parameter assumptions. **Load example** constructs and evaluates the entire workflow, including catalog suggestions, simulation and EPS-01–20 review. Evaluation is not feasibility or qualification.

| Allocation/input | Basis and limitation |
| --- | --- |
| 3 AZUR SPACE 81780 bare cells | Conditional typical irradiated MPP pair 2.22 V × 0.969 A = 2.15118 W/cell. The three-cell lower bound establishes no series/parallel wiring, simultaneous illumination, packing or installation. |
| 1 GomSpace BP8 8S1P pack | Published recommended-range **86 Wh typical**, not 100 Wh nameplate. Separate retention and efficiency assumptions do not become BP8 EOL specifications. |
| 1 P80 configuration-1 assembly | One fixed assembly covers conditioning, distribution and processor roles. Its battery is external. No software release is allocated or invented. |
| 6.45354 W available source power | **Engineering assumption**: three conditional typical cell powers are available continuously during the modeled sunlight interval. This is not a demonstrated orbital array output or mission-radiation applicability finding. |
| 1.41 W additional EPS baseline | **Applicability assumption**: P80 1.25 W idle plus BP8 5 mA × 32 V = 0.16 W standby. P80's cited state has PMU/ACU features enabled and PDU outputs disabled. BP8 is ENA-active. Applying these states constantly is not a measured loaded-system model. Heaters are assumed off. Actual voltage, enabled-output increments, temperature and heater demand remain unassessed. Scenario OBC/loads are excluded from this baseline. |
| 0.8 retention, 0.95 charge/discharge efficiency, 3/6 W charge/discharge bounds | Editable energy-model assumptions, not sourced aging, current/pulse or efficiency guarantees. No current × nominal voltage conversion supplies the W bounds. |
| DoD 0.3, preliminary margin 0.2, conditioning efficiency 0.9, 1-year lifetime | Editable study assumptions. No cycle-life fit is invented. Margin enters preliminary battery sizing once. Retention enters physical capacity once. |
| EPS mass allocation 0.5 kg | Intentionally retained. The known board and pack alone weigh 0.8468 kg. The complete three-product indicative subtotal is 0.8624 kg. **EPS-19 fails** even before unknown auxiliaries. |

The EPS baseline is included once in both preliminary demand integration and simulation. It is not added to scenario loads and then added again. Missing baseline demand is missing data, not zero.

### Reproducible default results

At the representative 400 km circular reference: period 5553.452008 s, sunlight 3387.058730 s, eclipse 2166.393278 s. Routine scenario demand including the baseline is 3.200176720 Wh/orbit, with 2.0745 W average and 4.75 W peak. Preliminary source power is 4.320455987 W (three cells). Battery energy is 4.759773156 Wh and mission demand is 5682.519621 nominal cycles.

The assumed retained energy capacity is 68.8 Wh. Routine stored energy runs from 49.536 to 50.884802397 Wh, giving +1.348802397 Wh closure with no shortage. Energy reserve and closure subchecks pass. Full EPS-10/11 and cycle-life compliance remain unassessed. Numerical unused surplus is not verified hardware curtailment.

The two-orbit overlapping case requires 8.748233969 W and loses 2.798926050 Wh. EPS-02 and EPS-11 fail. The oversized illustrative pack avoids depletion in this particular interval. The reduced-generation case ends at 35.601659655 Wh after three orbits. Its preliminary generation screen fails. Recovery and full EPS-12 remain unassessed. These are not flight results.

## Allocation and recomputation boundaries

Apply snapshots the proposed whole-product count in one receipt per product. P80's logical roles share that receipt. Changing scenario or screening again does **not** resize hardware: the allocation remains three cells, one pack and one assembly while new suggestions may propose other counts. Reapply explicitly to snapshot a new count. Available source power remains a separate engineering assumption. Adding cells does not automatically establish improved installed generation.

The `selections` map is unchanged. Optional `allocations` receipts retain product/catalog revision, roles, quantity, origin, rationale and allocation time. Optional `provenance` records bind each recorded scalar to its exact authored value and distinguish catalog values from engineering assumptions, with rationale, conditions and source IDs. Bundled-example origin is not engineer approval. Manual edits remove inconsistent catalog provenance. Replacements clear obsolete product-bound ratings. Unbound assumptions stay assumptions and are flagged for applicability review after allocation changes.

A pack with missing energy, including ICEPS2 Type A, leaves the preliminary requirement computable and catalog suggestions refreshable. Its energy/charge/lifetime evidence remains missing. Simulation requires capacity or an explicit authored assumption. Partial requirement review and logical handoff need not wait. Advertised Wh or nominal V×Ah are not used to repair conflicting usable-energy evidence.

JSON/local storage preserve authored inputs, allocations and provenance, but discard calculation caches on restoration. **Recalculate explicitly** after reload/import. Legacy designs without receipts import without invented quantities or provenance. Their mass subtotal remains incomplete until allocations are explicitly reapplied.

The three cases are routine scheduled operations, hypothetical overlapping mission demand, and reduced-generation essential service. Automatic mode transitions, shedding decisions and recovery are outside this demo. All schedules can be edited graphically or numerically before reevaluation.
