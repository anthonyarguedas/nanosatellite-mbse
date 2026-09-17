# Pilot 008: ARC Topic yield diagnostic

Pilot 008 is diagnostic and separate from final search. It uses 2011-01-01 through 2026-08-29. All source artifacts are non-mergeable.

## Objective

Exercise ARC's visible Topic autocomplete and measure how a Topic restriction changes yield. Test exact source mapping, known-item assignment, complete BG1 yield, and retention within the accepted Pilot 007 119-DOI corpus.

## Discovery

The [predeclared discovery plan](searches/discovery-plan.json) tested five labels visible in Pilot 007's BG1 Topic facet and four protocol-aligned label probes. Each successful selection was committed through the visible autocomplete and read back with a numeric `ConceptID`.

| Exact label | `ConceptID` | Sentinel | BG1 canonical DOIs |
|---|---:|---:|---:|
| `Satellites` | `135111` | 1/1 | 14/44 |
| `Small Satellites` | `135111` | 1/1 | 14/44 |
| `Spacecrafts` | `134410` | 1/1 | 22/44 |
| `Space Systems and Vehicles` | `135236` | 1/1 | 31/44 |
| `Space Systems` | `135177` | 0/1 | 15/44 |
| `Spacecraft Design` | `134469` | 0/1 | 9/44 |
| `Systems Engineering` | `138491` | 1/1 | 3/44 |
| `CubeSats` | unavailable | NA | NA |
| `Nanosatellites` | unavailable | NA | NA |

`Satellites` and `Small Satellites` resolved to the same source ID and returned equal bounded sets. This proves a shared current source identity. ARC exposes no preferred-term or synonym relation.

The union of the four distinct Topic identities that retained known eligible DOI `10.2514/6.2015-4474` retained 32 of 44 BG1 DOIs. It removed 12 records with unclassified eligibility.

## Accepted-corpus yield

The discovery trigger promoted four distinct, sentinel-retaining Topic identities. The [DOI membership plan](searches/corpus-plan.json) retrieved every expected corpus DOI but also matched DOI occurrences in references or hidden indexed content. Its six baselines admitted 32 outside canonical DOIs. The [exact-title repair](searches/corpus-title-plan.json) retrieved every expected DOI and admitted 13 outside canonical DOIs, mainly a broad title phrase and correction records.

The [final projected plan](searches/corpus-projected-plan.json) was saved before its source calls. It combined the DOI union and exact source-title union in separate ARC rows. It also declared a fixed canonical-DOI allowlist for each chunk. Every outside source match remains in the artifacts and assessment ledger. The six paired baselines retrieved all 119 accepted corpus DOIs. Two correction records remained outside the allowlist.

| Topic label | `ConceptID` | Retained | Removed | Retention |
|---|---:|---:|---:|---:|
| `Satellites` | `135111` | 55/119 | 64 | 46.22% |
| `Spacecrafts` | `134410` | 64/119 | 55 | 53.78% |
| `Space Systems and Vehicles` | `135236` | 73/119 | 46 | 61.34% |
| `Systems Engineering` | `138491` | 16/119 | 103 | 13.45% |
| Offline union of all four | separate source calls | 77/119 | 42 | 64.71% |

All four Topic identities retained the known eligible sentinel. The least restrictive tested union retained 77 of 119 records and removed 42, a 35.29% reduction. Eligibility remains unclassified for those removed records. The complete [assessment](searches/assessment.json) records every retained DOI, removed DOI, per-partition yield, source event, Topic readback, and outside-allowlist match.

## Decision

- Reject Topic as a required `AND` filter.
- Add no Topic supplement from this pilot.
- Keep the Pilot 007 hybrid route without a Topic restriction.
- Retain Pilot 008 as nonexcluding sensitivity evidence.
- Keep free-text searching mandatory.

A passing one-item recall gate cannot justify losing 42 accepted-corpus records. ARC also exposes no vocabulary version, scope notes, hierarchy, preferred-term flags, or explosion semantics.

## Runs and audit evidence

- [Discovery plan](searches/discovery-plan.json)
- [Discovery assessment](searches/discovery-assessment.json)
- [DOI membership plan](searches/corpus-plan.json)
- [Exact-title repair plan](searches/corpus-title-plan.json)
- [Predeclared projected plan](searches/corpus-projected-plan.json)
- [Complete assessment](searches/assessment.json)

Pilot 008 completed 106 successful source JSON artifacts and verified 212 mandatory screenshots. Four retained failure artifacts show that `CubeSats` and `Nanosatellites` were not offered as exact autocomplete selections in either probe. Three transient source or control failures were recovered by exact retries. No failure became zero.

Final execution still requires complete source-month treatment, exact-day handling, native export, and final-search artifacts.
