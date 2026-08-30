# Pilot 002

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py`

## Objective

Validate the exact English metadata restriction and compare complete literal `A1` with one finite native-wildcard candidate under identical source, date, type, variant, and sort controls. These are count-only diagnostics, not final searches.

## Runs

- [`A1.json`](searches/A1.json): literal `A1`. `LA(English)` and the exact 2011-01-01–2026-08-29 publication range read back.
- [`test1.json`](searches/test1.json): nonaccepted wildcard candidate under the same controls.

## Result

- [x] Change source controls or controlled vocabulary
- [x] Document a source limitation

Both runs selected Advanced Technologies & Aerospace Index alone, read back `LA(English)`, the endpoint-inclusive publication range, `Oldest first`, and spelling/form/show-variant controls off. No `DTYPE`, Document type, peer-review, full-text, access, or availability restriction was applied. The literal and candidate totals were both `0`.

| Replaced literal members | Candidate atom | Characters saved |
|---|---:|---:|
| `CubeSat`, `CubeSats` | `NOFT(CubeSat*)` | 21 |
| `nanosat`, `nanosats`, `nanosatellite`, `nanosatellites` | `NOFT(nanosat[*7])` | 69 |
| `SmallSat`, `SmallSats` | `NOFT(SmallSat*)` | 22 |

The raw query fell from 3,480 to 3,368 characters (112 saved). All other spacing, punctuation, phrase, and spelling variants remained literal. Individual extra completions were not measurable in the combined count-only run. Its observed overall total delta was `0`. No stable IDs were retained, so neither equality nor a superset was established and `test1.json` is **not accepted**. Full-text screening remains authoritative for language. `NOFT` field coverage and pair behavior were not tested by this A1 comparison and remain separate validation requirements.
