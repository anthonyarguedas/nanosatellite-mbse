# Numerical engine scope

Pure TypeScript. Import the seven contract exports from `src/engine/index.ts`:

- `calculateOrbit(altitudeKm)`
- `calculateBudget(scenario, orbit)`
- `sizeSolar(inputs, budget, orbit)`
- `sizeBattery(inputs, budget, orbit)`
- `suggestProducts(catalog, inputs, analysis)`
- `simulateOrbit(inputs, scenario, orbit)`
- `assessDesign(inputs, analysis, catalog, selections)`

Inputs are never mutated. Invalid numerical inputs throw an explanatory `Error`. Missing catalog evidence returns an unassessed check and explicit missing fields.

## Sizing and propagation

Orbit geometry uses Re = 6378 km and mu = 398601 km^3/s^2 from the proposal. This is a circular orbit with fixed eclipse geometry, not an ephemeris or attitude model. Phase zero starts in sunlight. The mathematical h = 0 boundary is accepted. Negative altitudes are rejected.

Load windows are fractional, half-open intervals. Active power replaces idle power over the union of each load's windows. Empty windows have no effect. Windows crossing phase zero must be split. Integration partitions at every mode and sunlight/eclipse event. A narrow pulse is never estimated from plotting samples.

Budgets and sizing are one-orbit screens. durationOrbits controls propagation only. Preliminary solar sizing uses Wh divided by sunlight hours and Xs/Xe exactly once. Preliminary battery sizing uses Ee/DoD × (1 + M). Mission cycles assume one cycle per orbit and 365.25 days per year. No cycle-life fit or inferred DoD is supplied.

Simulation uses these explicit boundaries:

1. Source power = installed available EOL power × illumination during sunlight, zero in eclipse.
2. Conditioned power = source power × constant conditioning efficiency, once.
3. Demand = all scheduled loads + additional EPS idle power at a common boundary outside the battery terminals.
4. Stored energy changes by etaC × accepted terminal charging power or terminal discharge power / etaD.

EPS idle power must exclude consumers already in the scenario. Distribution losses beyond the declared constant model, voltage, current and temperature are uncharacterized. Sizing efficiencies Xs/Xe, DoD and margin M do not enter propagation. Fixed EOL capacity is BOL capacity × retainedEnergy once.

Charging respects both user maxChargeW and remaining energy capacity. Exact full-capacity transitions are plotted. Unused conditioned surplus is recorded in curtailedWh and surplusW. These numerical values establish no hardware curtailment, shunt or thermal capability.

A discharge above maxDischargeW stops before unsupported propagation. Depletion stops exactly at zero energy, with a retained failure and terminal-energy shortage for the remainder of the attempted physical event interval. Later intervals are unevaluated. shortageWh is therefore a lower bound for the requested duration. A reserve violation within valid physical energy bounds does not stop the run.

Fractional durations end at the exact requested time. Plot points include global 10 s ticks, exact mode/eclipse events and full/depletion transitions. Discontinuous rates have two points at the same time. `point.orbit` is elapsed fractional orbits. Integration does not depend on the plot grid. Stored-energy increments use compensated summation to avoid accumulated false closure loss from redundant mode boundaries. Runs are bounded to an estimated 250,000 plotting points.

`closureWh` is the final-minus-initial energy of the supplied duration. ENERGY-CLOSURE checks each completed nominal orbit. It excludes a fractional tail from repeating closure. A run shorter than one orbit has no repeating-closure verdict. An interrupted nominal run fails. Numerical tolerance is 32 × machine epsilon × energy capacity, not an allowed depletion margin. No recovery transition or automatic shedding is inferred for survival cases.

## Catalog screens

The bounded search covers at most 128 input products. Each solar panel is a fixed whole product, with quantities 1..8. Bare solar or battery cells use a preliminary count in 1..256 and always remain incomplete without assembly evidence. Finished packs and conditioning boards use exactly one unit. No internal panel/pack configuration, mass, dimension or rating is resized.

Suggestions are sorted by product ID, then solar/battery/conditioning role order. No price, preference or cost ranking occurs. Missing priceUsd is visible. A preliminary match means only that its scalar screen passes at the cited conditions. Interfaces, installation, environment, protection and complete mission feasibility remain separate.

Available numbers require matching units, original text, conditions, source ID, source revision and location. Typical, nominal and estimated values establish no guaranteed bound. BOL solar data never substitutes for missing EOL data. A battery BOL preliminary match establishes no EOL, charge or cycle-life pass. EOL cell voltage/current are multiplied only at matching declared conditions.

## Requirement assessment and shared-type limits

Every assessment exposes EPS-01 through EPS-20, plus energy, sizing and mass subchecks. Known violations fail their affected requirements. Most full requirements remain unassessed because decisive installation, interface, protection, thermal or software data is absent.

ENERGY-RESERVE and ENERGY-CLOSURE may pass the energy model. EPS-10/11 remain unassessed on passing energy checks because charge-based state of charge and a characterized charge/voltage mapping are absent. No normalized energy value is called charge SoC. EPS-09 remains unassessed without an applicable sourced cycle-life model and conditions. A scalar cycleLife field alone cannot resolve DoD/temperature applicability with this schema.

The shared selections map stores product IDs, not installed usage IDs or explicit quantities. KNOWN-MASS deduplicates an integrated board by product ID across its logical roles. For its candidate subtotal it uses current non-rejected suggestion quantities, otherwise one unit per selected ID. This convention is explicit in the result. A full bill of materials, several distinct usages of the same product, nested accounting boundaries and independently authorized quantities need a richer usage schema. Unknown harnesses, adapters, packaging/protection and volume prevent a full EPS-19 pass. The known mass lower bound can still fail an allocation.

The shared scenario has no user closure-tolerance field or explicit repeating/recovery interval. The implemented roundoff tolerance and per-orbit nominal interval are reported assumptions. Assessment covers the active scenario only. Workspace revision/staleness enforcement belongs to the parent state layer.

## Tests

From `eps-demo/`: `npm test` and `npx tsc --noEmit`.
