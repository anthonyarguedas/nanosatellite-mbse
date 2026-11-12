# COTS engineering data

The catalog contains sourced facts, their conditions and their value meanings.
It keeps minimum, nominal, typical, maximum, absolute maximum and derived values distinct.
A catalog fact is a candidate input for an engineering assessment.
Its applicability depends on the selected product configuration and operating conditions.

## Native EPS inputs

`model-inputs.tsv` maps the array, battery and converter inputs in `framework/models/eps.py` to reviewed catalog facts.
It covers the 53 products relevant to those inputs: 12 solar products, 13 batteries, 20 converters/regulators and 8 integrated EPS/charger products.
The other catalog products do not acquire battery or solar properties through this mapping.
See [the audit summary](configuration-audit.md) for coverage, source discrepancies and remaining gaps.
`configuration-review.tsv` records the 44 reviewed corrections to existing fact metadata.
Selections pinned to those old facts require explicit review and rebinding.

Each row identifies a product, internal element, native model class and Property path, catalog parameter or curve quantity, value meaning, unit, condition and source.
The note records qualifications, derivations or a reason that a value is unavailable.
Multiple rows for one Property represent different supported conditions or bounds.
They are not interchangeable defaults.
Mission and EPS requirement inputs appear to explain which values cannot come from a component datasheet.

| Status | Meaning |
| --- | --- |
| `existing` | The applicable fact already exists in the catalog |
| `extracted` | The fact was extracted from an identified source |
| `derived` | The value follows from identified inputs and stated assumptions |
| `unknown` | The necessary intrinsic information is unavailable or insufficient |
| `mission_input` | The engineer supplies the mission, operating point or installation choice |
| `not_applicable` | The Property does not describe this product or product level |

This mapping is an evidence view, not an automatic catalog loader or fact selector.
Native COTS classes still receive explicit, fixed Property definitions.
The engineer chooses coherent facts and binds the selected conditions or mode expressions.
Raw additions remain in the existing `parameters.tsv`, `conditions.tsv`, `condition-parameters.tsv`, `sources.tsv` and related tables.

## Binding rules

- Use one cell's ratings for `cell_*` Properties.
- Bind complete purchased-pack ratings to the corresponding pack Properties.
- Keep a purchased pack's specified internal series/parallel arrangement.
- Supply the counts for a new assembly, including any expression that counts assigned products.
- Keep solar EOL voltage, current and efficiency at compatible temperature, irradiance and radiation conditions.
- Treat one triple-junction solar cell as one physical cell.
- Select operating voltage limits separately from absolute stress limits.
- Preserve startup, conversion ratio, thermal and external-component restrictions.
- Use a converter's specified output capability at the assessed operating point.
- Keep switch current, current-limit thresholds and permissible source current distinct.
- Preserve channel identity for integrated EPS outputs.
- Select programmable settings explicitly within the supported intervals.
- Retain the conditions of charge, discharge and pulse current limits.
- Treat nominal voltage times rated charge as an estimated energy when that derivation is used.
- Keep capacity retention and energy retention distinct.

Typical efficiency and performance curves establish characterized points.
They establish no guaranteed limit across all modes or temperatures.
A reference irradiance or temperature describes a test condition.
It does not select the mission's illumination or temperature history.

## Inputs that can remain unresolved

Usable installation area, packing, attitude, lifetime, engineer degradation margin, path efficiency and mode allocations normally belong to the mission or installation.
A new assembly's counts belong to its configuration.
The extraction does not invent these inputs.

Standard battery datasheets often give a cycle-life result at one discharge depth and charge/discharge protocol.
That result does not determine both coefficients and a valid domain for the model's cycle power law.
An accepted cycle model needs additional characterization.
The engineer can instead explicitly assign `eps.battery_energy.maximum_dod` when using another accepted DoD criterion.

Missing data remain visible as `unknown` or `mission_input` rows.
They remain unset in the model until an applicable value or accepted calculation is supplied.
