# EPS COTS evidence audit

Audit date: 2026-11-10 UTC. Scope: five existing EPS products, 68 added facts (46 features and 22 numeric records). No requirements, mission, UI, engine or existing fact records were changed.

## Gap audit before enrichment

The catalogue already contained charger chemistries, supported cell counts, reference-circuit charge-temperature limits, pack arrangements, current limits, and many autonomous protection flags. Those facts were retained. The useful remaining evidence gaps selected here were:

- ICEPS2 battery protection had an autonomous-controller label and voltage thresholds, but lacked individually selectable protection capabilities and recovery/inhibit semantics.
- IMEPS2 output hardware current protection was already recorded. Output overvoltage mechanism and the PBU-specific communication-reset behavior were missing.
- BQ24650 already had charge chemistry, temperature-reference limits and general OVP/OCP flags. Input UVLO scope, cycle-by-cycle response, restart policy and separate input OVP thresholds were missing.
- BQ25798 already had autonomous MPPT capability and its disabled-at-reset state. Battery discharge OCP assembly/configuration dependencies, input OCP recovery, register reset, watchdog behavior and cell-dependent voltage programming ranges were missing.
- TPS63802 already had UVLO and current protection. OVP capability, separate input/output OVP mechanisms and threshold tolerances, UVLO tolerance endpoints and thermal shutdown values were missing.

These additions supply product evidence for EPS-01, EPS-05, EPS-13 and EPS-15–18. They support configuration and operating-limit checks associated with FR-14–16 and FR-19–20. They do not establish full framework or EPS conformance.

## Primary-source retrieval

All five exact URLs returned HTTP 200 with `application/pdf`. Downloads used the supplied internet resource's `http-fetch/scripts/web_reader.py`, executed with `uv run`. Native text was inspected with `pdftotext -layout`. Artifacts, retrieval JSON and verification logs are outside the repository at `/tmp/eps-coverage.j0ZOoW/cots-evidence/`.

Retrieval times below are UTC download-completion timestamps from the saved artifacts. Page numbers refer to printed datasheet pages, which match PDF page positions for these citations.

| New source ID | Exact manufacturer URL | Revision and document date | Retrieved UTC | Downloaded SHA256 |
| --- | --- | --- | --- | --- |
| `enrichment_iceps2_20261110` | https://isispace.nl/wp-content/uploads/2025/01/ISIS-ICEPS2-DSH-0001-ICEPS2_Datasheet-01_02.pdf | Issue 1.2, 2024-07-26 | 2026-11-10T06:13:25.182Z | `ebc07b06bb9a64f32a59e052e46f0ba0158f293c59f7f84903702fbf895a68ff` |
| `enrichment_imeps2_20261110` | https://www.isispace.nl/wp-content/uploads/2025/01/ISIS-IMEPS2-DSH-0001-Datasheet-02_00.pdf | Issue 2.0, 2024-07-30 | 2026-11-10T06:13:27.425Z | `67e545caad43559f3e22243e57db998bbecd7995cbf5557996f5df7ce3632eeb` |
| `enrichment_bq24650_20261110` | https://www.ti.com/lit/ds/symlink/bq24650.pdf | SLUSA75B, revised January 2020 | 2026-11-10T06:13:24.667Z | `c62393dc9b5fc3d2da0391c018d46c97886b828c47990b2526fb5c881f78602e` |
| `enrichment_bq25798_20261110` | https://www.ti.com/lit/ds/symlink/bq25798.pdf | SLUSDV2C, revised June 2026 | 2026-11-10T06:13:24.743Z | `163e45683f62f208545920e1470054b352b4a4b0cdc201e1f19fcb1007f1e222` |
| `enrichment_tps63802_20261110` | https://www.ti.com/lit/ds/symlink/tps63802.pdf | SLVSEU9D, revised January 2021 | 2026-11-10T06:13:24.711Z | `be07deca1231c5493957bc64c2dc1cad5543bff330e49ae41caf3286fd80dca6` |

Each hash matches the corresponding pre-existing source bytes. Original source rows and retrieval times remain unchanged. New source snapshots record this retrieval for new facts without invalidating previously pinned fact revisions. Every added fact carries its exact source ID and page/section/table locator.

## Added evidence by product

### `isispace_iceps2_type_a`: 9 features

- On internal `battery`: autonomous charge/discharge overcurrent protection, autonomous overvoltage protection and autonomous undervoltage protection. Page 5 explicitly describes charge/discharge current limiting and states that battery electronics other than the heater switch operate independently of the MCU. Page 8, Table 2, supplies separate charge and discharge voltage limits.
- Charge lockout action and voltage-hysteresis recovery. Discharge lockout and recovery retain the separate charge-undervoltage trickle bypass. Evidence: pages 5 and 8, Table 2 and footnote 16.
- Conditional inhibit semantics for the optional three-separation-switch arrangement. Low side must connect before high side, and RBF overrides to inhibited. Evidence: page 5. This records an option rule, not an assertion that this option is assembled.

The existing Type A 2S1P arrangement, chemistry, temperature conditions and thresholds remain unchanged. Current limiting is not represented as a guaranteed fault-current disconnect.

### `isispace_imeps2_base_4s1p`: 8 features

- Autonomous OVP and `tvs_transient_clamp` action on each existing output domain: `vd0_vbat`, `vd1_5v` and `vd2_3v3`. Evidence: page 2 explicitly identifies TVS diodes on output load channels, and page 8, Table 1, specifies OVP on all domains.
- Automatic battery heater control availability on `battery`. Page 9 describes a closed-loop controller with configurable enable and thresholds. No enabled-by-default claim was added.
- PBU communication watchdog action on `battery`: unit reset does not interrupt power provision. Evidence: page 9, Table 1. This is narrower than the existing overall stack/unit reset label.

TVS protection is a transient clamp. It is not a battery charge cutoff, sustained-overvoltage disconnect or a known clamping-voltage rating. The finished 4S1P pack remains fixed.

### `ti_bq24650rvar`: 11 features and 8 numeric records

- VCC UVLO capability and action. All IC circuits, including VREF, are disabled below UVLO. This is input/controller UVLO evidence, not proof of a pack discharge switch. Evidence: page 16, Section 8.3.13.
- Separate start/resume and continuing-charge TS windows, MPPSET enable levels and mandatory TERM_EN termination, required external buck circuitry and NTC divider for battery temperature monitoring. Evidence: pages 4, 14, 17 and 23, including Section 8.3.17 and Figure 15. The existing 0–45 °C solar-reference window remains a reference-circuit result, not an immutable controller temperature window.
- Cycle-by-cycle high-side gate turnoff at 200% programmed charging current and automatic recovery below the overcurrent threshold. The 80 mV typical sense threshold is conditioned on synchronous operation with rising charge current at 25 °C. Evidence: page 8 electrical characteristics and page 17, Section 8.3.15.
- Charge restart triggers: recharge threshold, POR or MPPSET below 75 mV. Evidence: page 14, Section 8.3.5.
- Battery OVP gate inhibition until voltage falls below 102% regulation, including the SRP-to-ground sink. Evidence: page 17, Section 8.3.14.
- Typical thermal shutdown 418.15 K (145 °C), 15 K hysteresis and automatic restart below 130 °C. Evidence: pages 8 and 17, Section 8.3.16. These are protection characteristics, not recommended operating temperatures.
- UVLO rising minimum/maximum endpoints of 3.65/4 V supplement the existing 3.85 V typical value. Evidence: page 7.
- New internal `vcc` records separate input ACOV from battery OVP: 31/32/33 V minimum/typical/maximum and charge-disable action. Evidence: page 7 and page 16, Section 8.3.12. The existing 28 V recommended input ceiling remains unchanged.

### `ti_bq25798rqmr`: 12 features and 2 numeric records

- Battery discharge disconnect requires an external ship FET, `SFET_PRESENT=1` and `EN_BATOC=1`. Otherwise the described overcurrent indication does not establish disconnect behavior. Evidence: page 52, Section 7.3.13.1.7. No unconditional battery discharge-protection Boolean was added.
- Input OCP behavior is gated by `EN_IBUS_OCP`. Recovery requires clearing `EN_HIZ` and `DIS_ACDRV`, or removing/replacing the adapter. Evidence: page 52, Section 7.3.13.1.8.
- Input undervoltage protection is scoped to power-up POORSRC testing, stopping switching and retesting after a typical seven minutes. Evidence: page 51, Section 7.3.13.1.3. It is not a battery undervoltage-disconnect claim.
- TS policy explicitly retains `TS_IGNORE`: bypassing TS removes battery NTC qualification. It does not disable the separate die-temperature shutdown. Evidence: pages 45–46, Section 7.3.9.5.1.
- PROG sampling, CELL-write reset dependencies and allowed charge-voltage ranges for 1S/2S/3S/4S. Evidence: pages 25–26, Tables 7-1 and 7-2. A global voltage range alone does not establish that every voltage is legal for every cell count.
- Required configuration circuitry and conditional ship-FET isolation are explicit. Evidence: pages 25, 46 and 49–52.
- Watchdog expiry returns to default mode with selective register resets. Watchdog disable is supported. The largest programmable timeout is 160 s nominal, not a guaranteed measured maximum. Evidence: page 56 and page 72, Table 7-26.
- REG_RST resets marked registers/timers without repeating input FET detection or default VINDPM sampling. Evidence: page 56, Section 7.4.2.
- System power reset has a 0.35 s typical ship-FET off interval, conditioned on the external ship FET being present. Evidence: page 51, Section 7.3.12.3. This differs from the QON input hold time and from register reset.

### `ti_tps63802dlar`: 6 features and 12 numeric records

- Autonomous OVP capability. New internal `input_supply` and `output_supply` records distinguish reverse-boost input protection (forces PFM and interrupts negative current) from output protection (stops switching). Evidence: page 12, Sections 9.3.8–9.3.9.
- Each internal OVP threshold retains 5.5/5.7/5.9 V minimum/typical/maximum values. Evidence: page 6, Section 8.5. These thresholds do not extend the existing recommended 5.5 V input limit or 5.2 V output limit.
- UVLO falling minimum/maximum 1.2/1.29 V apply once started with VOUT at least 1.8 V. Rising minimum/maximum are 1.6/1.79 V. Existing typical values remain unchanged. Evidence: page 6 and page 11, Section 9.3.4. Existing recommended startup limits remain separate.
- Typical thermal shutdown is 423.15 K (150 °C), with 20 K hysteresis and automatic restart. Evidence: pages 6 and 12, Section 9.3.7. Existing recommended junction maximum remains 398.15 K (125 °C).
- Required inductor/capacitors, feedback divider with low-side resistance below 100 kohm, and terminated EN/MODE inputs. Evidence: pages 5 and 10–12. No default state for floating inputs was invented.

## Schema and verification

The existing TSV schema is retained. Three String definitions add `required_external_circuitry`, `reset_policy` and `charge_temperature_policy`. One Real definition adds `system_power_reset_off_time` in seconds. Three conditions and three internal elements distinguish the new evidence. String canonical units remain empty. No downloaded bytes or fixtures were added to the repository.

- `node --test framework/requirements-ui/test/cots-enrichment.test.mjs framework/requirements-ui/test/cots.test.mjs framework/requirements-ui/test/cots-ux.test.mjs`: 14 passed, 3 browser tests skipped because `PLAYWRIGHT_MODULE` was unset.
- `node --test framework/requirements-ui/test/*.test.mjs`: 227 passed, 14 skipped, 0 failed.
- Full worker catalogue resolution: 99 products loaded. All 68 new facts resolved through `resolve_components`. Regression tests also resolve every new binding through the supervised evaluation worker and check that stale revisions become pending.
- Comparison with a pre-edit worker snapshot: all 5,383 previous facts retained identical projections, including IDs, revisions, values, conditions, source metadata and internal-element metadata.
- All TSV row widths and all five downloaded SHA256 values were checked. `git diff --check` passed.

## Remaining uncertainties and access limits

No retrieval failures or access walls occurred for the five selected URLs. No new false feature was inferred from an omitted feature list. Unknowns remain absent.

- ICEPS2: the actual optional separation-switch assembly, hardware trip/reset delay tolerances, fault stress/SOA and processor-failure truth-table coverage need configuration-specific evidence.
- IMEPS2: battery hardware UV/OV cutoff thresholds, hysteresis, recovery delays, cell charging-temperature limits, TVS clamp voltage/energy ratings and detailed heater settings remain unknown from the inspected public datasheet. The PBU low-power mode does not establish autonomous battery disconnect.
- BQ24650: the implemented thermistor/divider, battery chemistry/cell policy, MOSFET/sense-path thermal/SOA ratings and circuit stability must be supplied. Autonomous charger control does not establish complete pack protection or battery load isolation.
- BQ25798: assembled ship/input FETs, actual enable/register settings, NTC network, CELL-compatible VREG and watchdog servicing policy must be supplied. Reset-time guarantees and external power-switch ratings need their own evidence. Capability flags do not establish that optional protections are enabled.
- TPS63802: fitted passives, pin bias, startup load/capacitance, mode-dependent current envelope and thermal design remain configuration inputs. OVP limits are not recommended operating limits or a guarantee against arbitrary externally forced faults.
- Flight qualification, radiation response, lifetime reliability, full thermal histories, harness/adapter ratings and installation geometry are outside these manufacturer fact additions. No absent qualification or reliability value was fabricated.
