# Array, battery and converter input audit

Review date: 12 November 2026.

The later solar transfer-method review adds 78 feature facts and 103 native input rows for the same 53 products.
It preserves all 9,232 fact identities and revisions established by this review.

Four independent extraction tasks inspected the 53 catalog products relevant to the new EPS configuration inputs.
They used public manufacturer documents, existing catalog evidence, text extraction and visual checks where needed.
Source URLs, document revisions, hashes and retrieval dates remain in `sources.tsv`.
Numerical records retain page, table, row and derivation locators.

## Catalog changes

| Material | Result |
| --- | ---: |
| Applicable products inspected | 53 |
| Numerical parameter additions | 411 |
| New condition records | 68 |
| New condition parameters | 74 |
| New parameter, condition and feature definitions | 18 |
| New feature facts | 13 |
| New source records | 5 |
| Existing fact metadata corrections | 44 |
| Native input/evidence rows | 1,759 |

The catalog still contains 147 products.
The parameter/feature fact count increased from 8,808 to 9,232.
The additions preserve 8,764 prior fact identities and revisions unchanged.
The 44 reviewed corrections replace only their intended facts.
Their numerical values and units are unchanged.
`configuration-review.tsv` records each old/new condition, source, value kind and locator with the reason.
Saved selections of corrected facts require explicit review and rebinding.

The native input view contains 784 existing, 86 extracted and 340 derived findings.
It also records 282 unknown, 232 mission-input and 35 inapplicable findings.
A finding is a candidate input or a documented gap, not an automatically selected Property value.

## Solar products

All 12 assigned products represent one cell or one single-cell CIC.
Their structural 1S1P records describe the purchased item.
They do not select the arrangement of an installed array.
A triple-junction cell remains one physical cell.

The added data include 44 Spectrolab radiation cases with matched EOL MPP voltage/current, open-circuit voltage, short-circuit current, efficiency and power.
Each case preserves its fluence, AM0 irradiance, temperature and US or ECSS annealing procedure.
All 264 derived Spectrolab ratings were independently checked with decimal arithmetic against the original BOL values and matching retention factors.
Rounding differences between efficiency-based and MPP-product power remain visible.

There are 58 supported EOL MPP pairs across ten products, including existing AZUR and CESI CTJLC data.
CESI CTJ30 and Sharp IMM3J remain without a separately determined EOL MPP voltage/current pair.
Power, open-circuit voltage and short-circuit current do not uniquely determine that pair.

Temperature coefficients remain slopes with their stated reference and validity interval.
They are not universal temperature factors.
Radiation retention cases are not automatic calendar-life values.
Sharp's example multicell sheets and AZUR CIC outer dimensions are not installed panel footprints.

## Batteries

All 13 batteries have sourced capacity, energy and nominal-voltage information, with the original minimum, typical, nominal or derived meaning retained.
Their operating endpoints, stress boundaries and current protocols remain separate.
The twelve single-cell products now have explicit structural count records.
The GomSpace BPX retains its specified 8S1P arrangement and complete-pack ratings.
Its cell manufacturer/model remains undisclosed.

Molicel P28B, P30B, M65A, P45B and P50B currents now carry the corresponding temperature-cutoff conditions.
Only M65A explicitly identifies its cutoff as cell surface temperature.
Unspecified cutoff references remain unspecified.
M65A and P42A standard charge currents are not promoted to maximum charge limits.
Panasonic BK-3MCC fast-charge and discharge plots do not establish universal maximum current or charging-voltage ratings.

Tenergy 30005-0 retains its temperature-dependent current limits and distinct discharge endpoints.
Its handling instruction requires an endpoint strictly above 2.70 V.
The 2.5 V overdischarge prohibition is a separate boundary.
A live product page identifies a different embedded MPN and different current/voltage claims, so those values do not replace the exact-model specification.

No inspected battery has enough discharge-depth data to establish `cycle_coefficient`, `cycle_exponent`, `fit_dod_min` and `fit_dod_max` for the native power law.
All thirteen also lack a justified generic `energy_retention` value.
Conditional retained-charge data remain capacity evidence.
They do not establish retained Wh.

## Converters and chargers

Twenty converter/regulator ICs were reviewed against 18 manufacturer datasheets.
New VIN stress ratings are separate from operating ranges.
Startup and continuation floors retain output-voltage and startup-state restrictions.
Seven headline output-capability records are now nominal rather than an implied guaranteed capacity.
Minimum-duty constraints retain their passive-component and operating-mode conditions.

A universal permissible input-current rating remains unknown for all twenty ICs.
Switch/inductor current limits are different quantities.
The delivered capacity of a complete converter also depends on external components, PCB heat removal, input/output voltages and operating mode.
Typical efficiency examples and curves remain conditional.

The five charger ICs preserve separate normal input, absolute stress, programmable current, charge setting and power-path boundaries.
BQ25606 battery regulation has three discrete VSET choices with separate tolerances.
Its 22 V stress condition requires the converter off and limited exposure at room temperature.
BQ25798's 30 V stress condition also requires no switching.
Its MPPT reset values are nominal register settings, with MPPT disabled at reset.
They are not statistical typical performance or selected mission settings.

## Integrated EPS products

ICEPS2 Type A includes a 2S1P pack.
The current manufacturer product table states 22.5 Wh.
Its datasheet optional-feature summary states 28.8 Wh, while default-cell arithmetic gives 23.04 Wh.
Those source scopes are unresolved and remain separate.
The documented default-cell capacity and voltage do not identify the actual cell model.

IMEPS2's included base pack retains its stated 45 Wh, 4S1P configuration and 12.8–16 V operating interval.
The 46.08 Wh nominal arithmetic estimate does not replace that rating.
MPPT, common-rail, PBU and PDU limits retain their own channel and configuration boundaries.

Pumpkin EPSM1 includes no battery.
Its battery-port limits and supported external-pack arrangements do not define installed storage.
Its default 6 A charge profile is separate from the 8 A interface capability.
The added efficiency points describe a single buck block with its stated input power and voltage.
They are not complete-system efficiency guarantees.

## Validation and use

All table schemas, product identities, element references, source references, condition references, units and numeric types were checked.
All five new source hashes match retained original downloads.
The entire 147-product catalog loads through the existing database adapter.
A live check confirms that corrected saved fact selections become pending and can be explicitly rebound to the qualified record.

Choose a coherent condition group before defining fixed native COTS Properties.
Bind complete packs and panels at their stated product boundary.
Leave unsupported data unset.
Irradiance histories, attitude, installation space, selected packing, path efficiency, engineer margins, chosen settings and new assembly counts remain engineering inputs.
The preliminary cycle calculation assumes one cycle per orbit.
Another accepted cycle policy needs an explicitly assigned cycle estimate.
