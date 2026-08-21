# ESA Indico diagnostic observations — S-L02-P01-20260821T000344-0400

**Status:** blocked diagnostic pilot; no final event, screening, candidate construction, relevance assessment, or import occurred. [observed — E11]

**Claim-label convention:** `observed`, `official_documentation`, `inferred`, and `untested` have the meanings in the source-packet guideline. Each evidence ID resolves in [evidence-index.json](evidence-index.json).

## Source boundary

- [observed — E12, E01–E10] The preserved 2026-08-20 interface-only diagnostic was not used as proof; every behavior used by this draft was independently rechecked in the current pilot.
- [observed — E02] The downloaded current public search client defines Events, Contributions (paired `contribution` + `subcontribution`), Materials (`attachment`), Notes (`event_note`), and Categories.
- [observed — E06] Public notes are not merely a UI label: a bounded `event_note` response had content and ID fields, while note ID 5 resolved anonymously to an event-session note route.
- [observed — E04, E06, E07] Public root-category, event-export, timetable, contribution, and attachment routes are all reachable anonymously in bounded samples.
- [official_documentation — E10] ESA general search, ESA Publications listings, and ESA Archives/SHIP are separate ESA website, formal-publication, and historical-archive scopes rather than replacements for the Indico object universe.
- [inferred — E06] A complete local method must retain public event notes as independent text routes; excluding their text would leave a known public search object class unaccounted for.

## Direct-search diagnosis

- [observed — E01] Event `satellite space` and quoted `"satellite space"` returned one record; textual `AND`/`NOT` returned explicit zero; textual `OR`, parentheses, `&&`, `||`, and `-` forms did not yield the expected Boolean set.
- [observed — E01] Field-like `title:satellite` and `description:satellite` returned explicit zero in the bounded test.
- [observed — E01, E02, E03] Search totals were often `-1` for nonzero event/contribution/attachment/note groups; ten-record pages used opaque cursor-like values and bounded repeat passes preserved first-page order.
- [observed — E02] Sending either contribution type alone returned zero in this test; sending both source types together returned records. A live sub-contribution record was not observed.
- [observed — E02] Case-equivalent first pages were observed for MBSE and CubeSat; `cube-sat` differed from `cube sat`; `nanosat*` was only first-page-equal to `nanosat`.
- [inferred — E01, E02] The current interface cannot losslessly represent the protocol's direct Boolean schedule; direct query translation is prohibited for this source.

## Universe, fields, and identity

- [observed — E04] Two bounded root-category-0 requests had count=row count and identical order, but no pagination object.
- [observed — E05] Root category 0 returned a category-5 event absent from category 6 and returned long-running events that began before the requested window; category-6-only and start-date-only assumptions would lose objects.
- [observed — E07] Event export ID 644 exposed 149 unique contribution `db_id`/canonical-URL pairs; a source-search contribution ID matched `db_id`, not the export's friendly/display ID.
- [observed — E06] Event 293's export and anonymous timetable each exposed exactly 35 identical contribution friendly IDs; its timetable exposed note query IDs 2–5.
- [observed — E05] Public category output can show protected folders; no login or private-access attempt was made.
- [inferred — E04, E05, E06] Root-category enumeration followed by event export and timetable/note traversal is a candidate traversal design, but it is not a complete-universe proof.

## Materials and access

- [observed — E08] One public PDF attachment returned HTTP 200 and parsed successfully with `pdfinfo` and `pdftotext`; only technical checksums/metadata were retained.
- [observed — E08] A public ZIP attachment returned HTTP 400 to HEAD but HTTP 206 and ZIP magic to a bounded GET range; full archive traversal was not performed.
- [inferred — E08] An unprotected listed material that cannot be retrieved, checksum-validated, or parsed must fail the source event rather than be treated as a lexical non-match.

## Completeness disposition

- [untested — E04, E05] The pilot did not prove category-0 recursive scope, absence of a full-range cap, coverage of undated events, or a fixed full date-partition plan.
- [untested — E06] The pilot did not prove that every public event exposes a complete anonymous timetable/note ledger or validate actual sub-contribution field behavior.
- [untested — E08] Full ZIP recursion, all non-PDF types, external link attachments, parser-failure prevalence, full-run storage, and rate-limit ceiling remain untested.
- [inferred — E01, E04, E06, E08] Recommendation: **revise** the ESA Indico packet and re-pilot the named hard gates before any final source event. No acceptance is recommended now.

## Protocol impact

- [observed — E11] No protocol semantic, task, log, dictionary, crosswalk, schema, template, final-event, or external-tool file was changed.
- [inferred — E06] A supervisor must decide and commit any change to the intended treatment of public `event_note` objects before a final run; this worker made no such change.
