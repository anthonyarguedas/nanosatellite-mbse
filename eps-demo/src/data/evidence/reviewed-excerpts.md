# Reviewed manufacturer excerpts

Retrieved 2026-10-17. These short transcriptions retain selected original representations. They are not complete datasheets. Exact URLs, document revisions, full interpretation and SHA-256 hashes are in [`../CATALOG-SOURCES.md`](../CATALOG-SOURCES.md). PDF page references below distinguish printed and file pages where needed.

## `azur-3g30-2025`

DB 00010892-01, issue date 11-Apr-2025, p. 2. **3G30C-Adv. Bare Cell**, material 81780. The 3G30A CIC/assembly column is not used.

| Typical Electrical Performance | BOL Cell | 1E15 Cell |
| --- | ---: | ---: |
| Voc [mV] | 2700 | 2519 |
| Isc [mA] | 1040 | 1002 |
| Vmp [mV] | 2400 | 2220 |
| Imp [mA] | 1008 | 969 |
| η (1367 W/m²) [%] | 29.3 | 26.1 |

Table note: “Spectrum: AM0 WRC, 1367 W/m²; T = 28°C, fluence 1 MeV e- [e/cm²]”.

Mechanical table: `Outer Dimensions (mm) 80.00 (± 0.1) × 80.00 (± 0.1)`, `Cell Area (cm²) 60.35`, `Average Weight ≤ 86 mg/cm² / 5.2 grams`, `Thickness (µm) 150 (± 50)`.

Review: 2.220 V × 0.969 A = 2.15118 W for the stated irradiation endpoint. This is conditional typical data. It is not an assumed mission-year rating.

## `cesi-ctj30-2025`

CTJ30, filename v2025.1, no visible revision label. P. 1: `Standard sizes 6.9x3.9cm², area 26.5cm²`, `solar cell mass (81-89mg/cm²)`, `Thickness 150µm ± 20µm`.

P. 2, Performance Data: “AVERAGE ELECTRICAL OUTPUT PARAMETERS @AM0, 1367 W/m², T=25°C”.

| BOL quantity | Original value |
| --- | ---: |
| JSC [mA/cm²] | 17.8 |
| VOC [V] | 2.6 |
| Jm [mA/cm²] | 17.1 |
| Vm [V] | 2.3 |
| Pmax [mW/cm²] | 39.8 |
| Eff [%] | 29.1 |

P. 2, Radiation Degradation (Remaining Factors): `1MeV`, `1E15 e/cm²`, `ISC 0.91`, `VOC 0.93`, `PM 0.84`.

Review: current/power densities use the stated 26.5 cm² active area. No EOL Vmp/Imp are listed. The remaining factor is not converted into an invented EOL MPP pair.

## `gomspace-bp8-1.2.0`

DS 1069134 1.2.0, April 10, 2026. Printed p. 1 / PDF p. 5: `8S1P`, `3500mAh (3000mAh in recommended operating range)`, `100 Wh (86 Wh in recommended operating range)`.

Printed p. 5 / PDF p. 9, Table 2.2:

| Parameter/condition | Min | Typ | Max | Unit |
| --- | ---: | ---: | ---: | --- |
| VOP Recommended operating voltage | 23.6 | 28.8 | 32.0 | V |
| EBAT, VBAT=23.6V to 32.0V | | 86 | | Wh |
| EBAT, VBAT=23.6V to 33.6V | | 89 | | Wh |
| IOUT Discharge current | | | 4.0 | A |
| ICHG Charge current | | | 3.4 | A |
| IS, VBAT=32V, ENA active | 3.5 | 5.0 | 5.5 | mA |
| PH Heater power usage | | 6.0 | | W |

Printed p. 11 / PDF p. 15, Table 4.1: `Mass 486 g`, `Size 94.8 x 95 x 42 (L x W x H) mm`.

Review: 86 Wh is a typical recommended-range case, not EOL or a guaranteed minimum. Cycle-life/DoD and retained-capacity models are not stated.

## `gomspace-bpx-1.1.0`

DS 1076870 1.1.0, April 21, 2026. Printed p. 2 / PDF p. 6 configuration row: `8S-1P`, `8` cells, `100 Wh`, `24-33.6 V`, `28.8 V`, `3.5 Ah`.

Printed p. 3 / PDF p. 7, §1.5: “PBAT1 and PBAT2 have raw battery, and no short-circuit protection.”

Printed p. 4 / PDF p. 8, Table 2.2:

| Parameter/condition | Min | Typ | Max | Unit |
| --- | ---: | ---: | ---: | --- |
| VOP, 8S1P | 23.6 | 28.8 | 32.0 | V |
| EBAT, VBAT=23.6V to 32.0V | | 87 | | Wh |
| EBAT, VBAT=23.6V to 33.6V | | 89 | | Wh |
| IOUT, four power pins with ECSS-Q-ST-30-11C derating | | | 6.0 | A |
| ICHG, 8S1P, limited by cell max charge current | | | 3.4 | A |
| ICHG, 4S2P (excluded variant) | | | 6.0 | A |
| IOC Overcurrent protection | | None | | A |

Printed p. 1 instead says `86 Wh in recommended operating range`. Printed p. 13 / PDF p. 17, Table 7.1: `Mass 500 g`, `93 x 86 x 41 (L x W x H) mm`.

Review: explicit Table 2.2 case adopted with the 86/87 Wh disagreement disclosed. 4S2P current is not imported into 8S1P. External protection remains necessary.

## `gomspace-p80-2.3.0`

DS 1047423 2.3.0, September 24, 2024. Printed p. 2 / PDF p. 9: “The battery (NanoPower BP8) is not part of the EPS, but a seperate product.”

Printed p. 5 / PDF p. 12, Table 1.1: configuration `1`, `1xPMU, 1xACU, 1xPDU`. Printed p. 3 / PDF p. 10 describes hardware watchdogs that monitor each MCU.

Printed pp. 7–8 / PDF pp. 14–15, Table 2.2:

| Parameter/condition | Typ | Max | Unit |
| --- | ---: | ---: | --- |
| PMU VIN Operating voltage | 28.8 | 33.6 | V |
| PMU PIDL, all features enabled | 500 | | mW |
| PDU PIDL, all channels disabled | 450 | | mW |
| ACU PIDL, all features enabled | 300 | | mW |
| VPV, VOC < max(VBAT) | | 25.0 | V |
| IPV per channel (0–11), ITOT < 12 A | | 1.1 | A |

Printed p. 22 / PDF p. 29, Table 4.1, configuration 1: `Length 95.0 mm`, `Width 95.0 mm`, `Height 38.8 mm`, `Mass 360.8 g`.

Review: sum of typical idle terms is 1.25 W in the stated mixed enabled/disabled state. Configuration-1 mass includes its three submodules once. No battery or independent software allocation is added.

## `isis-iceps2-1.2`

ISIS-ICEPS2-DSH-0001, issue 1.2, 2024-07-26. P. 6: `Type A: PIU + PBP-2S1P`; the PBP-2S1P cannot be used with the DaughterBoard.

P. 2 advertises `28.2Wh to 57.6Wh` and the optional 2S1P pack as `7.2V and 4A or 28.8Wh`. The source prints A, not Ah, in that bullet. It is not silently corrected.

Table 2, pp. 8–9:

| Item | Original representation |
| --- | --- |
| Cell nominal capacity, Typ | 3.2 Ah |
| Cell voltage, absolute maximum, Min/Typ/Max | 2.5 / 3.6 / 4.0 V |
| Type A pack configuration | 2 in series |
| Type A functional MPPT voltage, Min/Max | 3.5 / 7.5 V |
| Maximum input voltage MPPT, Max | 15.0 V |
| Input current per channel, Max | 2 A |
| Type A operating voltage, software limits, Min | 6.0 V |
| Battery charge current, Min/Typ/Max | 1.60 / 1.78 / 1.96 A |
| Battery discharge current, Min/Typ/Max | 4.0 / 4.45 / 4.9 A |
| Mass Type A, Min/Typ/Max | 179 / 184 / 189 gram |
| Type A IU mainboard + 2 cell BP, excluding CSKB | 96 x 92 x 26.5 mm |

P. 2 explicitly lists FRAM-based, low-power MCUs for control and telemetry. P. 7 gives `Static (Idle) consumption`, Typ `93 mW`.

Review: usable Wh is missing due to the advertised/default-cell discrepancy. Current tuples do not become guaranteed safe pack limits. MPPT tracking range, absolute maximum and software cutoff retain distinct meanings. No cycle-life/EOL model is inferred from storage recoverability.
