# Pilot 021: clean current literal PSR completion

**Status:** passed diagnostic. This is not a final search.

## Scope and controls

The [predeclared plan](searches/event-plan.json) ran all four current literal PSR partitions as fresh events. PSR2 and PSR4 ran first. PSR4 uses the compound definitions introduced by commit `3194156e90497186664260a8e86435e78d2e2aa1`.

Each event used Documents scope, Date (oldest), a 50-row page size, the inclusive 2026 upper year bound, and no lower year. No language, document type, subject, access, peer-review, or Search within restriction was applied. No wildcard or proximity operator was used. Full abstracts were skipped for this stable-ID completion pilot.

## Results

| Partition | Source total | Pages per pass | Order differences | Evidence |
|---|---:|---:|---:|---|
| `PSR1` | 53 | 2 | 0 | [JSON](searches/events/PSR1.attempt-01.json), [search screenshot](searches/events/PSR1.attempt-01.search-page.png), [results screenshot](searches/events/PSR1.attempt-01.results-page.png) |
| `PSR2` | 237 | 5 | 0 | [JSON](searches/events/PSR2.attempt-01.json), [search screenshot](searches/events/PSR2.attempt-01.search-page.png), [results screenshot](searches/events/PSR2.attempt-01.results-page.png) |
| `PSR3` | 1 | 1 | 0 | [JSON](searches/events/PSR3.attempt-01.json), [search screenshot](searches/events/PSR3.attempt-01.search-page.png), [results screenshot](searches/events/PSR3.attempt-01.results-page.png) |
| `PSR4` | 68 | 2 | 0 | [JSON](searches/events/PSR4.attempt-01.json), [search screenshot](searches/events/PSR4.attempt-01.search-page.png), [results screenshot](searches/events/PSR4.attempt-01.results-page.png) |

All four events completed on their first attempt. Each has two exhaustive passes, equal complete stable-ID sets, an `academic-search-scopus-strict-two-pass/v2` receipt, a valid terminal marker, and both mandatory screenshot receipts. The four events contain 359 records and 326 unique Scopus publication IDs. There are 33 cross-partition duplicate occurrences.

Buruso et al. (2026), DOI `10.1002/sys.70051`, remains retrieved as `SCOPUS-PUBLICATION:105032155734`. It occurs in PSR1 and PSR2 with the exact expected title. The current source rows leave the DOI field blank, so the stable ID and title provide the live source confirmation.

## Adapter repair and decision

Pilot 020 showed that a result title containing the word “Next” was mistaken for an enabled paginator on PSR2's final page. The repaired parser recognizes exact Next controls and excludes arbitrary result links. The [adapter test report](searches/adapter-test-report.json) passes the targeted and broader regression sets. PSR2 then completed both five-page passes with all 237 IDs.

The [assessment](searches/assessment.json) and [final validation](searches/validation-report-final.json) pass. They confirm strict completion of PSR2 and PSR4, all four current literal partitions, eight required screenshots, unrestricted PSR controls, and known-item recall. The literal Scopus PSR translation is ready for later clean final events. This pilot does not authorize reuse of its records as final-search results.
