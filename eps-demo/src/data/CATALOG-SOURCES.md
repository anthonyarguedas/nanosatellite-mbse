# Orbitwork COTS catalog: source and interpretation record

## Scope and retrieval

`catalog.json` contains **6 products**, with two solar-cell alternatives, two standalone battery-pack alternatives, and two EPS alternatives. ICEPS2 Type A also includes storage. This is a preliminary research catalog, not a compatible bill of materials or flight-qualified selection.

Retrieval date is **2026-10-17**, taken from the local shell. The UTC shell checkpoint after the PDF downloads was `2026-10-17T07:21:51Z`. Source `retrievedAt` fields retain that real calendar date. Document issue dates and hardware revisions are separate. No product hardware revision was established from these public documents. Product `revision` identifies catalog record 1 and states that gap.

Discovery used the browser skill's local Chrome Google adapter. Exact URLs were then downloaded with the HTTP-fetch skill. All six selected manufacturer PDF endpoints returned HTTP 200. Search snippets, reseller listings and general product-page claims are not numerical evidence for this catalog.

The PDF-to-Markdown OCR tool was attempted once and returned HTTP 429 with insufficient balance. Local `pdftotext -layout` extraction was used instead. Selected electrical and mechanical tables were also rendered and visually checked. Reviewed excerpts are in [`evidence/reviewed-excerpts.md`](evidence/reviewed-excerpts.md). Full downloaded PDFs and exploratory search material remain in the repository's ignored `.web-content/eps-demo/cots/` research directory. They are not runtime assets.

### Normalization and semantics

- W, Wh, V, A, kg and m are the runtime units. Percentages become dimensionless fractions. mV/mA divide by 1000, g divide by 1000, mm divide by 1000, µm divide by one million, and cm² multiply by 0.0001.
- Every contract specification key is present on every product. `missing` and `not-applicable` values are explicitly `null`, with rationale. A genuinely irrelevant role property uses `not-applicable`. An unavailable or ambiguous applicable rating uses `missing`.
- Every available specification retains original representation, conditions, semantic category, source ID and page/table location. Statistical average is mapped to `typical`. It establishes no guaranteed bound.
- Source maxima remain maxima only within their stated scope. A protection threshold, absolute maximum, recommended operating limit and typical performance point are distinct.
- Cell and pack identities are fixed. Other formats, CIC assemblies, series/parallel variants and EPS stack configurations are not silently substituted.
- No mission-years radiation prediction, battery aging fit, price estimate, array packing arrangement or loss map is invented. Arithmetic unit/area conversions and products of a sourced MPP pair are identified in each specification's rationale.

## Source register and reviewed products

### 1. AZUR SPACE 3G30C-Advanced bare cell, material 81780

- Catalog ID: `azur-3g30c-advanced-81780`
- Source ID: `azur-3g30-2025`
- Manufacturer PDF: <https://www.azurspace.com/media/uploads/file_links/file/bdb_00010892-01-00_tj3g30-advanced_8x8.pdf>
- Visible document revision: **DB 00010892-01**, issue **11-Apr-2025**. PDF has 2 pages.
- Locations: product identifiers and description, p. 1. Design and Mechanical Data and Typical Electrical Performance, p. 2.
- Exact identity: **bare cell 81780**, drawing **ZP-0005107**, 60.35 cm² active area and 80 × 80 mm outer dimensions. Assembly/CIC 81752 uses a different current column and is excluded.
- BOL: typical `Vmp = 2400 mV`, `Imp = 1008 mA`, `Voc = 2700 mV`, `Isc = 1040 mA` at AM0 WRC, 1367 W/m², 28 °C.
- Conditional EOL case: the **1E15 1 MeV electron/cm²** endpoint gives typical `Vmp = 2220 mV` and `Imp = 969 mA`. Normalized MPP power is **2.15118 W**, calculated directly from that irradiated pair. BOL MPP power is 2.4192 W. No BOL degradation extrapolation is used.
- This endpoint is real manufacturer radiation-performance evidence. Calling it an EOL case does **not** establish that this fluence matches the demo orbit, shielding or mission duration. An engineer must establish applicability. All these electrical data are typical, not conservative guarantees.
- Average Weight is `≤ 86 mg/cm² / 5.2 grams`. The normalized scalar 0.0052 kg is deliberately `typical`, with the average/upper-bound qualifier preserved. It is not an individual-cell maximum. Thickness is 150 ± 50 µm.
- Missing: price, calendar lifetime/environment mapping, guaranteed electrical extrema, installed array geometry and assembly auxiliaries. The bare-cell boundary excludes diode, coverglass, interconnects, panel and harness.

### 2. CESI CTJ30 bare cell, 26.5 cm² format

- Catalog ID: `cesi-ctj30-26p5`
- Source ID: `cesi-ctj30-2025`
- Manufacturer PDF: <https://www.cesi.it/app/uploads/2025/04/CESI-CTJ30-v2025.1.pdf>
- Visible revision: **not stated**. Filename contains `v2025.1`, and document copyright says 2025. Neither establishes product hardware revision. PDF has 2 pages.
- Locations: size, areal mass and thickness bullets, p. 1. Performance Data and Radiation Degradation tables, p. 2.
- Exact format: 6.9 × 3.9 cm envelope, 26.5 cm² active area, 150 ± 20 µm thick. CTJ30-Thin and larger CTJ30 formats are excluded.
- BOL average electrical output is tabulated at AM0, 1367 W/m², 25 °C. `Jm = 17.1 mA/cm²` gives **0.45315 A**, `Jsc = 17.8 mA/cm²` gives **0.4717 A**, and `Pmax = 39.8 mW/cm²` gives **1.0547 W** for this active area. Vm is 2.3 V and Voc is 2.6 V.
- The independently rounded average columns are not exactly algebraically equal: Vm × Jm is 39.33 mW/cm², versus tabulated Pmax 39.8 mW/cm² (about 1.18% difference relative to Pmax). The direct Pmax density is retained rather than silently replacing it. This is recorded in caveats and the coherence-check tolerance.
- Efficiency differs across contexts: feature headline 29.5%, illustrative curve 29.7%, electrical table 29.1%. The explicitly conditioned table value, 0.291, is adopted.
- The source gives radiation remaining factors, including **PM = 0.84 at 1 MeV, 1E15 e/cm²**. That factor is retained separately. Absolute EOL power, Vmp and Imp remain **missing**. No EOL MPP pair is synthesized from a remaining-power factor.
- Areal mass 81–89 mg/cm² converts to a **[0.0021465, 0.0023585] kg interval**, not a guaranteed scalar. Code that only accepts scalar mass must leave its mass screen unresolved.
- Missing: absolute EOL MPP pair, guaranteed extrema, price, installed array and auxiliaries. No cell efficiency is reused as EPS conditioning efficiency.

### 3. GomSpace NanoPower BP8 100 Wh, 8S1P

- Catalog ID: `gomspace-bp8-100wh-8s1p`
- Source ID: `gomspace-bp8-1.2.0`
- Manufacturer PDF: <https://gomspace.com/wp-content/uploads/2025/08/gs-ds-nanopower-bp8-100-Wh-2.pdf>
- Visible revision: **DS 1069134, 1.2.0, April 10, 2026**. Use document contents, not the older upload-directory date. Printed pp. 1–13 are PDF pp. 5–17.
- Locations: features p. 1, Table 2.2 pp. 5–6, Table 4.1 p. 11.
- The adopted energy is **86 Wh typical over 23.6–32.0 V**. Recommended-range charge is **3.0 Ah nominal** for 8S1P. Bus typical voltage is 28.8 V. These quantities have distinct meanings and are not exact V×Ah battery models.
- The 100 Wh and 3.5 Ah nameplate/full-range values are preserved separately. They are not substituted for recommended-range usable energy. No EOL rating is supplied.
- Table maxima: charge **3.4 A**, discharge **4.0 A**. No pulse duration or full thermal derating envelope is supplied for these rows. Protection thresholds and the 33.6 V absolute/full-charge case are separate from the recommended 32.0 V upper operating value.
- Physical data: **486 g**, **94.8 × 95 × 42 mm (L × W × H)**. Catalog axes map to L, W and H in order, with no installation orientation inferred.
- The complete pack includes protection, balancing, electronics and heater. Typical heater power is 6 W. ENA-active standby current is 5 mA at 32 V. Those are internal consumers, not additional physical packs.
- Missing: cycle-life versus DoD domain and criteria, EOL energy/charge retention, separate charge/discharge energy and coulombic efficiencies, price and detailed transient/thermal envelope. Telemetry SoC estimation alone supplies none of the demo's charge-state propagation data.

### 4. GomSpace NanoPower BPX 100 Wh, 8S1P

- Catalog ID: `gomspace-bpx-100wh-8s1p`
- Source ID: `gomspace-bpx-1.1.0`
- Manufacturer PDF: <https://gomspace.com/wp-content/uploads/2025/09/gs-ds-nanopower-BPX-100-Wh-1076870-1.1.0.pdf>
- Visible revision: **DS 1076870, 1.1.0, April 21, 2026**. Printed pp. 1–14 are PDF pp. 5–18.
- Locations: features p. 1, configuration table p. 2, raw-output protection statement §1.5 p. 3, Table 2.2 p. 4, heater Table 6.1 p. 9, physical Table 7.1 p. 13.
- Exact selected factory configuration is **8S1P**. The 4S2P option has different voltage and charge limits and is outside this record.
- Adopted energy is the electrical-table **87 Wh typical over 23.6–32.0 V**. The features paragraph instead says 86 Wh in the recommended range. Both representations are disclosed. No guaranteed minimum is claimed. Recommended-range charge is 3.0 Ah nominal, and typical voltage is 28.8 V. Full/nameplate 100 Wh and 3.5 Ah values are separate.
- Charge maximum for **8S1P is 3.4 A**, not the 4S2P 6 A value. Discharge maximum is 6 A with the stated four-power-pin derating per ECSS-Q-ST-30-11C.
- **PBAT1/PBAT2 are raw battery outputs with no short-circuit protection.** An external protected power path must be included and assessed. BP8's protection capability is not transferred to BPX.
- Physical data: **500 g**, **93 × 86 × 41 mm (L × W × H)**. Heater typical power is 6 W at 32 V. ENA-active standby current is 5 mA.
- Missing: cycle-life domain, aging/retained-capacity model, separate energy/coulombic efficiencies, price and complete transient/thermal derating evidence. External protection and EPS are outside pack mass.

### 5. GomSpace NanoPower P80, configuration 1

- Catalog ID: `gomspace-p80-config1`
- Source ID: `gomspace-p80-2.3.0`
- Manufacturer PDF: <https://gomspace.com/wp-content/uploads/2025/09/Data-Sheet-NanoPower-P80.pdf>
- Visible revision: **DS 1047423, 2.3.0, September 24, 2024**. Printed pp. 1–23 are PDF pp. 8–30.
- Locations: functional overview pp. 1–3, configuration Table 1.1 p. 5, Table 2.2 pp. 7–8, efficiency Figure 2.1 p. 8, physical Table 4.1 p. 22.
- Fixed record: **1 PMU + 1 ACU + 1 PDU**, complete enclosure. Mass **360.8 g**, envelope **95 × 95 × 38.8 mm**. Other stack counts cannot reuse these values.
- Schema limitation: canonical `level` has no assembly option. `board` therefore denotes this explicitly identified enclosed multi-board assembly. Shared types were not changed.
- Roles conditioning, distribution and processor refer to **one installed physical assembly**. Count its mass and idle consumption once. The datasheet expressly states that **BP8 is a separate product**, so no battery role or capacity is assigned to P80.
- PV input maximum is **25.0 V**, with separate footnote `VOC < max(VBAT)`. Per-channel PV current maximum is **1.1 A**, subject to total current. Shared-bus operating voltage is 28.8 V typical, 33.6 V maximum. The VIN minimum column is blank. A 9.5 V fallback point is not a minimum tracking voltage.
- Typical idle consumption for the fixed state is 500 mW PMU + 300 mW ACU (features enabled) + 450 mW PDU (outputs disabled) = **1.25 W**. Integrated MCU execution is already inside this boundary.
- The document explicitly describes MCUs and watchdogs, which supports a processor role. Model, memory, available resources, versioned firmware and scheduling evidence remain absent. No software role is asserted.
- Missing: complete startup/tracking and absolute PV envelope, aggregate input W limit, one applicable scalar total conversion efficiency, price and full software/protection/integration evidence. Efficiency curves were not digitized or reduced to an optimistic scalar. Multiplying all channel maxima is not a supported aggregate power rating.

### 6. ISISPACE ICEPS2 Type A, PIU + PBP-2S1P

- Catalog ID: `isis-iceps2-type-a`
- Source ID: `isis-iceps2-1.2`
- Manufacturer PDF: <https://isispace.nl/wp-content/uploads/2025/01/ISIS-ICEPS2-DSH-0001-ICEPS2_Datasheet-01_02.pdf>
- Visible revision: **ISIS-ICEPS2-DSH-0001, issue 1.2, 2024-07-26**. PDF and printed page numbers coincide, pp. 1–10.
- Locations: features p. 2, functions p. 5, Type definitions p. 6, Table 2 pp. 7–9.
- Exact selected Type A includes the **PIU mainboard and directly mounted two-cell PBP-2S1P**. It cannot use the DaughterBoard. Type B/C ratings, extra trackers and voltage domains are not imported.
- Conditioning, distribution, battery and processor roles refer to **one physical Type A usage**. Typical mass **184 g** includes battery, board, heater and MCUs, with source min/typ/max 179/184/189 g. Envelope **96 × 92 × 26.5 mm**, excluding CSKB. EGSE, stack frames, harness and external mounting are separate.
- **Energy is unresolved.** Page 2 advertises 28.2–57.6 Wh and gives a 7.2 V / 28.8 Wh two-cell option. Table 2 p. 8 gives the default cell capacity as 3.2 Ah and nominal cell voltage 3.6 V. Two series cells retain 3.2 Ah and would imply 23.04 nominal Wh. This does not establish characterized usable energy and conflicts with the advertisement. `energyWh` is `null`/`missing`. The sourced 3.2 Ah charge capacity is retained with its default-cell condition.
- Type A functional MPPT interval is **3.5–7.5 V**. The separate **15 V maximum** is kept in `absoluteInputMaxV`. Footnote 11 permits 2 V on other channels once one channel is above 3.5 V. Footnote 12 describes pass-through without boost tracking above the functional interval. Per-channel specified input current is 2 A, with a different hardware limit of 2.5 A.
- Generic max battery current fields remain missing. Source charge-current tuple **[1.60, 1.78, 1.96] A** and discharge tuple **[4.0, 4.45, 4.9] A** are preserved as [min, typ, max]. The public table does not establish a separate safe continuous cell/pack envelope or clearly identify how to use threshold tolerances.
- The 6.0 V minimum is explicitly a **software operating limit**, not a cell absolute minimum. A recommended upper pack limit is unresolved. The source's 4 V/cell absolute maximum, 8.27 V typical overvoltage activation and 8 V EGSE maximum are distinct.
- Storage recoverability ≥80% under specified storage conditions is **not** an orbital cycling/EOL retention model. It is not used for `retainedEnergyFraction`.
- FRAM-based low-power MCUs for control/telemetry are explicit, supporting the processor role. No software release or available-host-resource claim is made.
- Missing: consistent usable energy, cycle-life domain, EOL retention, separate battery efficiencies, conversion loss map, aggregate input W rating, firmware/timing evidence and price.

## Audit hashes of downloaded PDFs

These SHA-256 values identify the actual bytes reviewed, independently of later changes at the same URL.

| Source ID | SHA-256 |
| --- | --- |
| `azur-3g30-2025` | `07a7f5ff5cbaa358a79cd1430fbaa496a51a0c62e03b82221f249f5bd77821ff` |
| `cesi-ctj30-2025` | `c1ef6726a695e7d5f4ee8543c3fec154308c824c1eff5614494eccbda4311431` |
| `gomspace-bp8-1.2.0` | `84455cefcec0025285cba85c6820ae190837e7e37c71f58f09573e1b1c49b20a` |
| `gomspace-bpx-1.1.0` | `8669f8ab693c80e32ffb2a783e1ad1ad7fb76a18dd5888331c131a2a2aec1641` |
| `gomspace-p80-2.3.0` | `1d1c24838633ac4c699dc07f9b70e701cd2565e29c1c751e7e314585611b178c` |
| `isis-iceps2-1.2` | `ebc07b06bb9a64f32a59e052e46f0ba0158f293c59f7f84903702fbf895a68ff` |

## Coverage limits and excluded material

- This compact edition contains cells, not finished solar panels. Cell counts do not imply a supported manufactured panel, installed orientation, illumination, packing or wiring configuration.
- There are no independent software products. Explicit integrated MCU descriptions support processor coverage only within their host assembly. Software service/version/resource and deadline verification remain unresolved.
- All prices are missing. No procurement cost, current availability, lead time or obsolescence conclusion is supported by a datasheet or search result alone.
- Public documents do not establish all interconnects, charger compatibility, converter operating envelopes, temperature histories, fault independence, protection timing, qualification configuration, or geometric fit. Catalog role coverage is not a passed EPS requirement.
- Battery cycle-life/DoD models are missing for all battery-bearing entries. No `a,b` coefficients, EOL factors or retained-capacity curves are fabricated. EPS-09 and charge-based portions of EPS-10/11 remain unassessed without additional evidence. Typical Wh alone cannot establish guaranteed usable energy.
- The legacy manufacturer P31u URL returned 404 and was excluded. EnduroSat solar-panel discovery exposed a download modal rather than an immediately accessible direct PDF. No gated form was submitted. Static ISISPACE/GomSpace listing extracts that contained mostly navigation were not used as specification sources.
- Manufacturer endpoints may reuse old upload paths for newer document contents. The revision printed inside each retrieved PDF takes precedence over the directory year and filename.

## Checks and reproduction

Run from the worktree root:

```sh
node eps-demo/src/data/validate-catalog.mjs
```

The dependency-free validator checks the canonical Catalog/Product/Source/Specification shape, all 25 required specification keys and units, enums and nullable values, unique product/source references, manufacturer PDF URLs and real retrieval date, valid numerical values, voltage ordering, MPP coherence, separate tracking/absolute limits, explicit aging/efficiency gaps, absence of price/software assertions and deduplicated integrated boundaries. It also verifies at least two alternatives per major role. The CESI independently rounded average table permits a documented 2% arithmetic sanity tolerance. No tolerance is used to upgrade typical data to a guarantee.

Reviewed validation result: **PASS**, 6 products and 200 specification records (88 available, 47 missing, 65 not applicable), with 2,839 assertions. A temporary TypeScript literal also passed `satisfies Catalog` against the unchanged canonical `src/types.ts`. Eight deliberately corrupted datasets were rejected (omitted field, unavailable zero, dangling source, wrong irradiated current, duplicate product, invented cycle-life model, unsupported software role, and substituted absolute/tracking voltage). This is a catalog check, not a full application build.

The data is intentionally incomplete where evidence is incomplete. Passing this validator establishes dataset consistency, not product compatibility, mission feasibility or flight verification.
