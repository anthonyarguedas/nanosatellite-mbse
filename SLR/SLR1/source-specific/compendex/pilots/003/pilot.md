# Pilot 003: paired full-schedule strict capture

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py`, through the fixed shared browser runner.

## Objective

Run the nine direct-query partitions as one paired Compendex+Inspec Engineering Village event per partition. This is a pilot, not a final search.

Before every source use, [`preflight.json`](searches/preflight.json) regenerated each literal `ALL` expression from [`pilot_schedule`](../../../../scripts/pilot_schedule/queries.py), checked all declared `NEAR/5` pairs, and rejected `*` and `?`. Every request used the visible Published 2011–2026 controls, raw `(English WN LA)`, autostemming off, `Date (Oldest)`, no `DT` or Open Access limiter, and no controlled-term supplement.

## Paired outcomes

| ID | Paired total | Compendex | Inspec | Outcome |
|---|---:|---:|---:|---|
| [A1](searches/A1.json) | 8 | 5 | 3 | strict two-pass capture |
| [A2](searches/A2.json) | 43 | 29 | 14 | strict two-pass capture |
| [A3](searches/A3.json) | 10 | 6 | 4 | strict two-pass capture |
| [B1](searches/B1.json) | 243 | 152 | 91 | strict two-pass capture |
| [B2](searches/B2.NON_MERGEABLE_FAILURE.json) | null | null | null | explicit strict null failure |
| [BG1](searches/BG1.json) | 8 | 6 | 2 | strict two-pass capture |
| [BG2](searches/BG2.json) | 25 | 16 | 9 | strict two-pass capture |
| [BC1](searches/BC1.json) | 51 | 32 | 19 | strict two-pass capture |
| [BT2](searches/BT2.json) | 17 | 8 | 9 | strict two-pass capture |

The eight successful marker-gated JSON/CSV pairs were accepted only after the fixed adapter's internal two independent complete accession/RIS passes. Its compact public receipt retains the exact source-run controls and records. Licensed raw RIS/manifests remain only in the owner-only export directory. B2 produced no public JSON/CSV/marker. Its receipt records that a private first pass started but strict completion failed, then retains null total/accession/RIS fields rather than calling it zero or partial. That private material is quarantined and unused.

These historical pairs use the captured v2 marker protocol and remain read-only evidence. [Pilot 008](../008/pilot.md) later completed the fresh current-query B2 event with adapter v16, strict paired capture, and both mandatory screenshots. That result confirms current readiness and leaves this historical null failure unchanged.

## Reconciliation and threshold work

- [`reconciliation.json`](searches/reconciliation.json) keeps each paired event and its separate Compendex/Inspec ordered accession projections.
- [`over-100-investigation.json`](searches/over-100-investigation.json) deduplicates successful events only by database-scoped accession. Compendex is 206 unique records from 254 event occurrences. Inspec is 116 from 151. Both exceed 100, so every retained accession is listed with partition provenance. No post-hoc source narrowing, deletion, screening decision, or cross-database merge was made.

Exact DOI collisions between the two databases are a diagnostic only. Compendex and Inspec counts, accessions, and unions remain separate. The B2 null failure makes every successful-event union incomplete for the full schedule and unsuitable for final-search use.

## Limitations and decision

The protocol common evidence cutoff is still TBD. Engineering Village supplies year-level Published bounds, so exact 2026 cutoff handling is deferred to screening. No descriptor was added because no candidate had both an exact normative-block mapping and a known eligible-record assignment in the paired projections. Free text was not replaced.

No wildcard is accepted. No final-search artifact was created. A later pilot may diagnose B2 only with the same full literal expression and strict paired controls. It must not substitute a narrower query or infer the missing count.
