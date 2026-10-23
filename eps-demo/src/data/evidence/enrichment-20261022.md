# Reviewed enrichment excerpts, 22 October 2026

The source register identifies exact URLs, revisions, dates, publishers, hashes and checked locations. Values below retain their source meanings. Source coverage is separate from mission applicability and architecture feasibility. Raw PDFs, rendered pages and firmware archives remain outside tracked/runtime assets.

## Solar cells

All four new/re-reviewed packets describe bare cells. Their CIC assemblies, external protection, coverglass, interconnects and installation are separate boundaries. The original CESI record remains available and incomplete.

| Bare cell | BOL Vmp / Imp / calculated W | Named 1E15 endpoint Vmp / Imp / calculated W | Envelope and source mass |
| --- | --- | --- | --- |
| AZUR 81780 | 2.400 V / 1.008 A / 2.4192 W | 2.220 V / 0.969 A / 2.15118 W | 80 × 80 mm, 150 ±50 µm, population-average ≤5.2 g |
| AZUR 82921 | 3.015 V / 0.433 A / 1.305495 W | 2.786 V / 0.423 A / 1.178478 W | 40.08 × 80.08 mm, 195 ±25 µm, population-average ≤3.3 g |
| AZUR HP 82645 | 2.395 V / 1.284 A / 3.07518 W | 2.215 V / 1.234 A / 2.73331 W | 145.90 × 60.69 mm, 245 ±25 µm, population-average ≤10.4 g |
| Spectrolab XTE-SF, 27 cm² reference | 2.435 V / 0.4833 A / 1.1768355 W | 2.0941 V / 0.473634 A / 0.9918369594 W, nominal derived AIAA case | Drawing labels 6.91 and 3.97 have no stated units. Width and height remain missing. Thickness and areal-mass options are intervals, not a paired fixed ordering configuration. |

AZUR conditions are AM0 WRC, 1367 W/m², 28 °C, except 82921 at 25 °C. The named radiation endpoint is 1 MeV electrons/cm². XTE-SF uses 1353 W/m² and 28 °C. Its AIAA Vmp and Jmp factors are independently published, not invented from one power-retention factor. The alternative ECSS factors remain separate. A fluence is not a mission year, and reference MPP power is not installed array generation.

AZUR sheets p. 2 explicitly give typical electrical tables. Their BOL voltage temperature coefficients are negative. For 81780 and HP, dVoc/dT is −6.2 mV/°C and dVmp/dT is −6.7 mV/°C. For 82921 they are −8.4 and −8.6 mV/°C. Numeric V/K records preserve these signs. Full ordered radiation/coefficient tables remain source-linked text. No curve solver or extrapolation is supplied. The coefficient domain is 28–140 °C, including the explicit gap below 28 °C for 82921's 25 °C electrical reference.

HP 82645 is 145.9 mm long. It is unsuitable for an assumed body-mounted 1U face. A deployed or other installation needs separate assembly, area, packing, orientation and harness evidence. Comparison coverage never removes this warning.

The 81780 additive review preserves every old specification object and all six original Source identity fields, including the 17 October retrieval date. Its re-reviewed bytes have the same SHA-256. CIC Imp values are not substituted into the bare-cell columns.

## Battery cells and packs

Three distinct Saft SKUs provide complete comparison facts for one sleeved cell each. They are 1S1P reference boundaries, not finished flight packs.

| Cell | Manufacturer nominal Wh | Typical Ah | Warm-domain continuous charge cap | Warm-domain continuous discharge cap | Typical mass | Thickness × width × height including terminals |
| --- | --- | --- | --- | --- | --- | --- |
| MP 144350 xlr | 9.4 | 2.6 | 2.6 A, 0–60 °C | 5 A, +15–60 °C | ~66 g | 14.5 × 42.9 × 50.1 mm |
| MP 174865 xlr | 19.3 | 5.3 | 5 A, 0–60 °C | 10 A, +10–60 °C | ~121 g | 19.0 × 48.0 × 65.0 mm |
| MP 176065 xlr | 24.8 | 6.8 | 6.8 A, 0–60 °C | 13.6 A, +10–60 °C | ~150 g | 19.6 × 60.1 × 65.2 mm |

Saft manual pp. 7–10 defines nominal Wh as nominal V × Ah. These are not measured or guaranteed usable Wh. Typical Ah uses C/5, +25 °C and a 2.5 V cutoff. All three have 3.65 V nominal and a 4.2 ±0.05 V CC/CV charge setpoint. Charge termination is C/100 or ten hours maximum. No current × nominal V power guarantee is created.

The separate source temperature domains are charging −30–60 °C and discharge −35–60 °C. Warm current caps do not apply throughout them. Charging derates to approximately C/8 at −20–0 °C and C/20 at −30–−20 °C. MP144350 discharge derates from 2C at +15–60 °C to C at −20–15 °C, C/2 at −30–−20 °C and C/5 at −35–−30 °C. MP174865/176065 use 2C at +10–60 °C, C at −30–10 °C and C/5 at −35–−30 °C. The lower exact cell-sheet current cap also applies. MP176065's 14 A sheet row is limited by the manual's 2C × 6.8 Ah = 13.6 A warm-domain rule. Its original 14 A row remains separate.

Saft sheets p. 2 show discharge/temperature curves and conditional charge-capacity retention/resistance histories. Charge retention is not retained energy fE. No mission retention, separate energy/coulombic efficiencies, applicable DoD-life fit or orbital-aging law is supplied. The malformed cycle-bullet charge-rate label and the MP174865 subtitle typo remain disclosed. Bare-cell assembly needs external mechanical/electrical integration, charger and safety/thermal electronics.

HY-LINE HI0202SN04 p. 2 gives 4.84 Ah, 35.2 Wh UN38.3/nameplate, 7.2 V nominal, 2 A charge and average discharge <7 A. Its physical-table maxima conflict with the toleranced p. 3 drawing. Canonical dimensions remain missing. BMS overcurrent thresholds are not permissible continuous currents. The chart's illustrated discharge is not integrated into a fabricated usable-energy or efficiency scalar.

OPTIMUS-30 retains 30 Wh, typical 268 g and its fixed envelope. The 1.95 A joint charge/discharge row, missing arrangement/Ah, and absence of separate charging/discharging temperature intervals remain gaps. It is a useful finished-pack browsing option, not a fully covered battery model.

BP8/BPX preserve their original energy/current interpretation. Added absolute temperature intervals remain numeric Celsius intervals and explicitly separate from recommended derated operating envelopes. ICEPS2 Type A energy remains missing because advertisement and default-cell data conflict.

### BIRDS-4/Tsuru reference only

Jara et al., Data in Brief 2022, pp. 6–7 and Table 2 identifies six BK-3MCCE NiMH cells in 3S2P. Source nominal cell data are 1.2 V, 2000 mAh and 26 g. Arithmetic gives 14.4 nominal Wh, 4 nominal Ah and a 156 g cell subtotal. Enclosure, heater, insulation, wiring and complete pack geometry/mass are not characterized. The battery-current sign in the published trace is negative for charging, opposite the report's battery-port convention. No trace or flight-pack model is silently adopted. The record is reference-only and cannot be allocated. The default illustrative BIRDS study is unchanged.

## Electronics modules

| Converter module | Sourced function and boundary | Important conditions |
| --- | --- | --- |
| Pololu D24V5F5 #2843 | Complete 5 V / 0.5 A load buck module, 0.6 g | Required input rises from about 5.1 V at light load to about 5.6 V at 0.5 A. About 200 µA no-load is typical in description and maximum in Specs. Preserve both meanings. |
| Pololu D36V28F12 #3786 | Complete 12 V load buck module, 3.3 g | 2.4 A typical maximum continuous at 36 V input. Forward maximum 50 V is distinct from −40 V reverse protection. No-load current is 1–3 mA typical. |
| Pololu S13V10F5 #4083 | Complete 5 V load buck-boost module, 0.6 g | 2.8–22 V input, typical 1 A at applicable conditions, 10–20 mA no-load. No enable or reverse protection is claimed. Original inch dimensions are retained consistently. |

These devices regulate DC load rails. Their documented functions include no PV MPPT/DET controller or battery charger. The comparison profile's technical applicability correction removes only the PV permissible-source-current requirement from an explicitly sourced load-converter branch. It retains input operating interval, output voltage and continuous current, channel organization, state consumption, physical dimensions/mass and all common boundary evidence. A switch threshold or output current never substitutes for PV source current. PV receivers retain their original current requirement. No-load consumption is not an unconditional power scalar, and these modules never become MPPT replacements merely by being allocated to the broad Regulator/Converter role.

Pololu Mini Pushbutton LV #2808 and Big Pushbutton HP #2813 are distinct purchased switches. At 12 V, 22 °C ambient in still air, 3 A (LV) and 6 A (HP) warm the MOSFETs to 55 °C. Higher source rows reach 150 °C. These are thermal observations, not automatic shutdown thresholds. Recommended voltage intervals differ from absolute limits. ON consumption is approximately 210 µA/V and 120 µA/V respectively. Near the upper range they can start ON. Neither is claimed as guaranteed fail-off, fully isolated, overcurrent-protected or thermally protected. External protection remains an installed requirement.

TPS2113A carrier #2596 is a two-input/one-output source mux, not a two-output distributor. Its factory limit is nominal 0.5 A. A supported 2 A setting requires an external 330 Ω resistor and retains threshold tolerance. Complete carrier consumption is missing. IC-only quiescent current is not assigned to the board.

A-Star 32U4 Micro #3101 is a complete 1.3 g module, with connector-inclusive 0.6 ×1.05 ×0.18 inch envelope excluding headers. ATmega32U4, 16 MHz, 32 KiB Flash and 2560 bytes SRAM are sourced. The supplied bootloader reserves 4 KiB. VIN is 5.5–15 V or USB 5 V. The approximately 25 mA self-load is at the internal 5 V rail. VIN LDO loss is separate. No arbitrary EPS firmware compatibility is inferred.

Pico SC0915 and Pico2 SC1631 retain real RP2040/RP2350 identity, clock, memory, interfaces and complete-module operating-state measurements. Their 21 ×51 ×1 mm figures describe the PCB. Manufacturer mass and connector-inclusive three-dimensional envelopes remain missing. Retailer mass or guessed USB height is not substituted.

### Integrated EPS boundaries

The EnduroSat Rev 1.2 one-pack EPS is one physical product across storage, conditioning, distribution and MCU roles. Its 198 g mass and 95.9 ×90.2 ×21.2 mm envelope include the fixed 1S2P battery. No second battery product is counted. The manual's 4/9 A PCM rows and 1.8 A customizable PV overcurrent threshold are not conservative permissible continuous ratings. The charger 0.49 A maximum setting is recorded separately from the missing battery charge-acceptance rating. H1-48/H1-51 LUP pin assignments conflict between schematic and table. Resolve before wiring.

P60 means one Dock plus one shielded ACU-200 and one shielded PDU-200 in the named 16 V configuration. The 191 g component sum is estimated and cites all three documents. Its complete assembly envelope and state-specific 16 V idle remain missing. Historical 8 V efficiency curves do not characterize the selected 16 V assembly. The optional NanoMind is excluded. Converter factory choices need an actual option sheet. The H2-29 rail/GND contradiction remains visible.

P80's newly reviewed 5 V PDU curve interval is approximately 0.925–0.94 at 28.8 V input and 2 A output. It is one path, not complete EPS efficiency. Idle inclusion and temperature are unresolved. No automatic change to topology efficiency or EPS baseline demand occurs.

## Actual EPS software

Four maintained/released implementations or services are pinned to exact commits and source files. They are not generic OS/SDK alternatives.

- UPSat: real EPS application, with README STM32L100RCT6 conflicting with the STM32L152RBTx build target. Supported host remains missing.
- SpaceLab EPS2 v0.4: actual EPS control/services, with v0.3 release intent versus bundled v0.2 hardware schematic. The 32 MHz clock request conflicts with the named MSP430F6659's 20 MHz CPU maximum. A clock API also has Hz/kHz ambiguity. Supported host and actual wall-clock behavior remain unresolved.
- Quetzal-1: source-declared custom ATmega328P EPS deployment. Exact installed core/clock is unverified. Literal 0x99 I2C notation needs addressing interpretation. A trailing 10 ms delay is neither WCET nor a guaranteed period/deadline. Jump-to-zero reset and OBC protection responsibilities remain explicit.
- KubOS Clyde3G EPS service v0.1.0, commit `949597c919bdc3d0f2c602b97343a9cedead0332`: actual Linux I2C/GraphQL telemetry, watchdog and control service on documented KubOS OBC targets. Source example uses `/dev/i2c-1`, address 0x2B and UDP 127.0.0.1:8100. It is not internal EPS charging/MPPT firmware and establishes no STARBUCK-NANO, ICEPS2 or installed electrical compatibility. The watchdog worker's 60 s wait and ignored kick errors are not deadline evidence. Resource usage belongs to the external execution host once.

Memory demand, WCET, scheduling and deadline evidence remain missing. Build/source review supplies no independent successful deployment, flight verification or software resource/timing pass.

## Final additive choices and source errata

Four further real options complete the six comparison targets without changing profile 1.1. Source hashes, precise checked locations and field bindings are in the source register.

- **Pololu Big Pushbutton MP #2812:** different MOSFETs and current behavior from HP #2813, despite the same 2.7 g mass and mechanical envelope. MP combined on-resistance is 40 mΩ at 4.5 V or 30 mΩ at 10 V. At 12 V, 22 °C ambient and still air, 4 A heats its MOSFETs to 55 °C and 8 A reaches 150 °C. Those are thermal observations. The 40 A headline requires brief operation or sufficient cooling and has no characterized pulse duration. Recommended supply is 4.5–32 V, distinct from the 40 V absolute maximum. OFF current is below 0.01 µA. No guaranteed fail-off, complete isolation or active overcurrent/thermal cutoff is inferred.
- **A-Star 32U4 Mini LV #3103/ac02b:** a complete 3.4 g board with a TPS63061 buck-boost supply from 2.7–11.8 V. Manufacturer dimensions are 0.7 ×1.95 ×0.23 inch, including USB overhang and excluding headers. The product-specific MCU/LED self-load is 30–40 mA at the internal 5 V rail. Conversion losses and external peripherals remain separate.
- **A-Star 32U4 Mini SV #3145/ac02f:** a different ISL85418 buck architecture with 5–40 V input. The 5 V minimum applies at light load. Dropout increases with load, and input above 6 V supports full regulator output capability. The obsolete #3104/ac02c is excluded. Both Minis retain actual ATmega32U4 memory/clock and 4 KiB bootloader reservations. Their 30–40 mA point is not the Micro's 25 mA point. No researched EPS firmware compatibility is inferred.
- **KubOS GomSpace P31U external C API:** an implemented, callable command/telemetry component on an external Linux OBC, pinned to commit `949597c919bdc3d0f2c602b97343a9cedead0332`. CMake declares C library 1.0.0. Optional Rust wrapper/client versions are separate. Real C packet handling and Linux i2c-dev/ioctl/read/write code are present. This is a different hardware service from Clyde3G, not an autonomous EPS firmware or generic SDK alternative. The caller supplies bus/address. C example 0x02 and Rust prose 0x08 are not universal validated defaults. Housekeeping layout/packing differs from a referenced datasheet. Rust heater selector Both=2 conflicts with the C range 0..1, and Rust bus-string termination needs review. The header's 1–30 s configuration-save window conflicts with the client's 600 ms sequence. Watchdog sleeps and ignored kick errors provide no timing guarantee. A process-global connection supplies no demonstrated multi-device/concurrency guarantee. Memory, WCET and scheduling remain missing.

The independent source audit corrects only the HP 82645 radiation-axis condition from 25 °C to **28 °C**. The 82921 axis remains **25 °C**. Existing scalar electrical conditions and PDF hashes do not change. All three Saft `maxDischargeA` records now carry manual p. 10, section 4.4 footnote [3]: maximum voltage, current and temperature conditions may not be mutually inclusive. Numerical ceilings and derating remain unchanged. The larger-cell descriptions name MP174865 and MP176065 correctly. MP144350's redundant false-NA nameplate aliases are removed while canonical nominal Wh and typical Ah remain unchanged.
