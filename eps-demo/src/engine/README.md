# Numerical engine scope

Pure TypeScript. Calculation exports from `src/engine/index.ts`:

- `calculateOrbit(altitudeKm)`
- `calculateBudget(scenario, orbit, additionalEpsPowerW = 0)`
- `sizeSolar(inputs, budget, orbit)`
- `sizeBattery(inputs, budget, orbit)`
- `suggestProducts(catalog, inputs, analysis, frozenQuantities = {})` (the fourth argument screens fixed allocations; ordinary suggestions enumerate counts)
- `simulateOrbit(inputs, scenario, orbit)`
- `assessDesign(inputs, analysis, catalog, selections, allocations?)`
- `getAllocationQuantity({ selections, allocations? }, productId)` → `number | null`
- `allocationIssues({ selections, allocations? }, catalog)` → `string[]`

Inputs are never mutated. Invalid numerical inputs used by a calculation throw an explanatory `Error`; optional unavailable physical-capacity derivatives remain null while independent requirements are sized. Missing catalog evidence returns an unassessed check and explicit missing fields.

## Sizing and propagation

Orbit geometry uses Re = 6378 km and mu = 398601 km^3/s^2 from the proposal. This is a circular orbit with fixed eclipse geometry, not an ephemeris or attitude model. Phase zero starts in sunlight. The mathematical h = 0 boundary is accepted. Negative altitudes are rejected.

Load windows are fractional, half-open intervals. Active power replaces idle power over the union of each load's windows. Empty windows have no effect. Windows crossing phase zero must be split. Integration partitions at every mode and sunlight/eclipse event. A narrow pulse is never estimated from plotting samples.

Budgets and sizing are one-orbit screens. `calculateBudget` adds its explicit additional EPS baseline once to every demand interval and retains `additionalEpsPowerW` in the result. Zero is the backwards-compatible pure-function default; the workspace requires a non-null authored baseline. Simulation independently adds the same baseline once, rather than consuming the already augmented budget. durationOrbits controls propagation only. Preliminary solar sizing uses Wh divided by sunlight hours and Xs/Xe exactly once. Preliminary battery sizing uses Ee/DoD × (1 + M). Mission cycles assume one cycle per orbit and 365.25 days per year. No cycle-life fit or inferred DoD is supplied. Required solar power and battery energy do not require installed cell/pack characterization. Missing cell EOL voltage/current leaves derived cell fields null; missing/invalid installed capacity or retention leaves `eolCapacityWh` null without changing required energy/cycles. Simulation validates its own physical energy-model inputs separately.

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

Suggestions are sorted by product ID with exact CSRM role identities. All six roles have suggestions. Distribution, processor and software suggestions retain unassessed architecture checks. No price, preference or cost ranking occurs. Missing priceUsd is visible. A preliminary match means only that its scalar screen passes at the cited conditions. Interfaces, installation, environment, protection and complete mission feasibility remain separate.

Available numbers require matching units, original text, conditions, source ID, source revision and location. Typical, nominal and estimated values establish no guaranteed bound. BOL solar data never substitutes for missing EOL data. A battery BOL preliminary match establishes no EOL, charge or cycle-life pass. EOL cell voltage/current are multiplied only at matching declared conditions.

Comparison coverage is evaluated separately in `src/catalog/`. Every role has at least three distinct options with the mandatory published facts. A covered profile establishes no installed compatibility or feasibility. Load converters are distinguished from PV receivers. Published reference-only BIRDS data is browsable and cannot be allocated.

A single battery-cell rating can populate the one-cell reference capacity. A multi-cell count leaves installed pack energy undefined until assembly data is supplied. Nominal Wh remains nominal. Efficiencies, mission retention and scalar terminal power are not invented from unrelated ratings.

## Requirement assessment and shared-type limits

Every assessment exposes EPS-01 through EPS-20, plus energy, sizing and mass subchecks. Known violations fail their affected requirements. Most full requirements remain unassessed because decisive installation, interface, protection, thermal or software data is absent.

ENERGY-RESERVE and ENERGY-CLOSURE may pass the energy model. EPS-10/11 remain unassessed on passing energy checks because charge-based state of charge and a characterized charge/voltage mapping are absent. No normalized energy value is called charge SoC. EPS-09 remains unassessed without an applicable sourced cycle-life model and conditions. A scalar cycleLife field alone cannot resolve DoD/temperature applicability with this schema.

The shared selections map still stores product IDs. Optional `AllocationReceipt[]` freezes one concept count per product across its selected roles. KNOWN-MASS and selected-product screens use only these frozen counts, never current suggestions. Missing legacy counts remain unknown. `getAllocationQuantity` returns null for missing, duplicate, role-mismatched or nonpositive/noninteger receipts; consumers also call `allocationIssues(subject, catalog)` to validate product/catalog revision, supported roles and product-level quantity bounds. No physical usage IDs, multiple independent usages of one product, assembly wiring or full BOM are inferred. Unknown harnesses, adapters, packaging/protection and volume prevent a full EPS-19 pass. The known mass lower bound can still fail an allocation.

The state layer admits only current simulation evidence to partial review. Missing/stale simulation does not gate review; its energy checks are unassessed. A newly evaluated simulation invalidates the earlier review through a nonblocking evidence dependency. Pure assessment callers must supply their own current evidence.

### Additive authored metadata contracts

`Workspace.allocations?: AllocationReceipt[]`, one receipt per product:

```ts
{ productId: string; productRevision: string; catalogRevision: string;
  roles: Role[]; quantity: number;
  origin: 'engineer-allocation' | 'bundled-example';
  rationale: string; allocatedAt: string; productSnapshot?: string; }
```

Roles must exactly match that product's current selected roles. Quantity bounds: cells 1..256, panels 1..8, finished packs/boards 1. Bundled origin is not engineer approval.

`Workspace.provenance?: ParameterProvenance[]`, one record per recorded numerical input:

```ts
{ parameter: NumericInputPath; value: number;
  kind: 'catalog-value' | 'engineering-assumption';
  rationale: string; conditions: string; sourceIds: string[];
  productId?: string; productRevision?: string; }
```

`NumericInputPath` covers mission altitude/lifetime; every solar/battery scalar; topology efficiency, idlePowerW and massAllocationKg. Values must exactly match authored inputs. Catalog-value records must match a selected product, its current record revision, the exact supported specification, source IDs and conditions. Supported transfers are cell EOL voltage/current and pack energy. Engineering assumptions never repair catalog evidence gaps. A product ID on an assumption binds it to that subject, so replacement clears it instead of reusing its rating. Missing legacy metadata is retained as missing on import.

`restoreWorkspace(raw, currentCatalog?, reviewChangedRecords?)` reconstructs authored data and fresh unevaluated records only. Local reload preserves changed catalog records with explicit review flags. Strict file import rejects incompatible evidence without replacing the open design. Exact unchanged snapshots can remain valid across additive catalog updates. Simulation and handoff stay blocked until required review is resolved. No restoration path recalculates or invents engineering approval. BIRDS-4 basis/input/default-allocation/provenance exports live in `src/data/birds4.ts`.

The shared scenario has no user closure-tolerance field or explicit repeating/recovery interval. The implemented roundoff tolerance and per-orbit nominal interval are reported assumptions. Assessment covers the active scenario only. Workspace revision/staleness enforcement belongs to the parent state layer.

## Tests

From `eps-demo/`: `npm test` and `npx tsc --noEmit`.
