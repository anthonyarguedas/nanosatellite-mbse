# Pilot 005: repaired schedule and standalone wildcards

Required changes were applied in commit: NA

Pilot 005 is diagnostic. It is not a final search. It uses the inclusive publication window 2011-01-01 through 2026-08-29.

## Objective

Validate adapter v13 after Pilot 004's stale-state finding. Run all nine current partitions in complete literal and wildcard forms. Compare canonical NTRS citation-ID sets rather than totals alone.

The [predeclared plan](searches/event-plan.json) pins protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`, the exact queries, adapter hash, controls, output paths, screenshots, and null-only retry policy. Every accepted event used two complete ordered rendered passes, `Publication Date (Oldest)`, page size 100, and no language, type, access, collection, source, distribution, subject, keyword, or controlled-vocabulary filter.

## Wildcard candidate

The candidate uses every useful standalone-token morphology compression. It has 26 wildcard atoms and replaces 88 literals.

| Block | Wildcard atoms |
|---|---|
| `P` | `CubeSat*`, `nanosat*`, `SmallSat*` |
| `R` | `requirement*`, `function*`, `behavior*`, `behaviour*`, `architectur*`, `interface*`, `trace*`, `allocat*`, `constraint*`, `parametric*`, `analys*`, `design*`, `decision*`, `tradeoff*`, `verif*`, `validat*` |
| `G_structure_fixed` | `metamodel*` |
| `T_precise` | `tailor*`, `customiz*`, `customis*`, `parameteriz*`, `parameteris*`, `instantiat*` |

Every wildcard is one unquoted source term ending in `*`. All phrases, punctuation forms, acronyms, proper names, isolated terms, and Boolean relationships remain literal. Acronyms remain quoted so they match standalone lexical tokens.

## Complete set comparison

The [run receipt](searches/run-receipt.json) records 18 accepted strict events from 19 attempts. One BG2 wildcard attempt failed during owned-page allocation. Its artifact is null, empty, and non-mergeable. The unchanged retry succeeded.

| Partition | Literal | Wildcard | Set relation | Query reduction |
|---|---:|---:|---|---:|
| `A1` | 0 | 0 | equal | 80 |
| `A2` | 2 | 2 | equal | 80 |
| `A3` | 0 | 0 | equal | 80 |
| `B1` | 11 | 11 | equal | 80 |
| `B2` | 4 | 4 | equal | 591 |
| `BG1` | 0 | 0 | equal | 80 |
| `BG2` | 2 | 2 | equal | 96 |
| `BC1` | 0 | 0 | equal | 80 |
| `BT2` | 0 | 0 | equal | 480 |

The literal and wildcard schedule unions each contain 14 canonical IDs. No literal ID is missing. No wildcard-only ID is present. The largest partition contains 11 records, so the 100-record investigation threshold did not trigger.

All 18 accepted JSON artifacts have both mandatory sibling screenshots. The [assessment](searches/assessment.json) verifies 36 PNG hashes and dimensions, all terminal markers, exact queries, dates, empty limiters, complete passes, and set equality.

## Decision

Accept the 26 standalone wildcard atoms for every applicable main partition. This is the validated wildcard boundary. Keep every other term literal unless later positive set evidence supports another replacement.

Pilot 006 tests a more aggressive all-family candidate. It loses literal records and confirms that phrase and multi-term wildcard compression must remain excluded.
