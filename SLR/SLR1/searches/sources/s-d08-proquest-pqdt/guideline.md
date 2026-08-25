---
task_id: S-D08
source_id: proquest-pqdt
source_name: ProQuest Dissertations & Theses Global
method_type: direct
status: draft
guideline_version: 0.1.0
validated_at: null
protocol_commit: 699f010f02b81dc17c7f17491dab77dbf9bb1feb
accepted_pilot_ids: []
---

# Source-specific guideline: ProQuest Dissertations & Theses Global

This is a source-free, diagnostic-only, no-screening, no-import launch bundle for the first diagnostic attempt. It is not an accepted source method and contains no live observation or completed campaign.

## 1. Source boundary and access route

The source is **ProQuest Dissertations & Theses Global (PQDT Global) only**, a separate database event on the ProQuest Platform. The intended normal routes are the PQDT database selector at `/pqdtglobal/databases/advanced` and Command Line Search at `/pqdtglobal/commandline`. The local adapter is `~/agent-tools/academic-research/skills/academic-search/scripts/search_pqdt.py`.

The selection must contain exactly one PQDT-labelled database. The preferred diagnostic label is `ProQuest Dissertations & Theses Global`; the adapter also allowlists the distinct `ProQuest Dissertations & Theses Global Full Text Included` label, which may be recorded only as one exact runtime selection, never together with the canonical label. No ATAI, parent collection, or other database may be selected. PQDT records, totals, identifiers, and provenance must never be combined with S-D07 ATAI.

The later browser phase uses the shared CfT contract in `SLR/SLR1/searches/README.md`: one lease at `127.0.0.1:9222`, one adapter-owned page at a time, a new immutable receipt, and no fresh browser/profile/port. The route, selection, and metadata behavior are current-interface requirements to test, not live observations in this draft.

## 2. Interface and field behavior

The exact source-native query strings are in [`translation-spec.json`](translation-spec.json) and `queries/`. They use the draft Command Line form `NOFT(("term 1" OR "term 2"))` for each free-text concept block and quote every finite dictionary literal. No wildcard, candidate S-C01 terminology, or unvalidated stemming assumption is used.

The paired blocks use the draft `NOFT(("left" NEAR/6 "right"))` form. `NEAR/6` is intended to represent an unordered pair with no more than five intervening lexical tokens, but its direction, distance, phrase-tokenization, and same-field behavior are **untested**. BG1, BG2, BC1, and BT2 therefore remain provisional until a current diagnostic validates the pair implementation or a protocol-permitted broader same-field fallback.

`NOFT` is the planned source-native free-text/metadata field wrapper; its exact searchable-field membership and cross-concept behavior are **untested**. P01 must compare `TI("CubeSat")`, `AB("CubeSat")`, `SU("CubeSat")`, `IF("CubeSat")`, and `NOFT("CubeSat")`. `TI` and `AB` are metadata-field candidates; `SU` is a subject-field candidate; and `IF` is an indexed-term-field candidate. None is accepted by this packet. Phrase, punctuation/hyphen normalization, acronym token boundaries, case, stemming, lemmatization, automatic expansion, and query-length behavior are all **unknown**.

The adapter's current static record allowlist targets dissertation title, authors, publication/dissertation metadata, source type, snippet, and abstract. It does not yet prove or retain subject/index descriptors. A normal visible record or thesaurus/index-term route must be inspected if the interface exposes one. Assigned descriptors, scope notes, hierarchy, narrower terms, explosion, and known-record assignment are all untested. No controlled-vocabulary supplement is accepted. Free text remains mandatory if a descriptor is later accepted.

## 3. Translation approach

This direct translation is frozen to the current protocol and dictionary. The nine files are:

- A1: `P AND E_H AND M_H` — `queries/A1.proquest-noft.txt`;
- A2: `P AND E_F AND (M_H OR M_B)` — `queries/A2.proquest-noft.txt`;
- A3: `P AND E_H AND M_B` — `queries/A3.proquest-noft.txt`;
- B1: `P AND M_H` — `queries/B1.proquest-noft.txt`;
- B2: `P AND M_B AND R` — `queries/B2.proquest-noft.txt`;
- BG1: `P AND G_model` — `queries/BG1.proquest-noft.txt`;
- BG2: `P AND G_structure` — `queries/BG2.proquest-noft.txt`;
- BC1: `P AND C1` — `queries/BC1.proquest-noft.txt`; and
- BT2: `P AND M_B AND T2` — `queries/BT2.proquest-noft.txt`.

Each partition currently has one complete offline cell. No lossless shard is required by the static adapter input ceiling, and no provider query-length limit has been observed. If a live limit is encountered, stop that operation, set its total to `null`, and define a complete stable-ID union of cells before any retry or final use. Never shorten a partition silently. The exact cell hashes and byte counts are recorded in `translation-spec.json`.

## 4. Controls and common limits

P01 predeclares the pilot-date diagnostic lower bound `2011-01-01` and upper bound `2026-08-25`. This is not the common cutoff and does not resolve P-001. PQDT has no adapter `--year-start`, `--year-end`, `--language`, `--count-only`, or `--require-complete` option. The runner therefore appends the diagnostic candidate `AND YR(2011-2026) AND LA(English)` to each probe/partition query. This year-granular suffix is a planned diagnostic, not an exact day/month cutoff or final common filter. Full-report language remains a screening field unless a reliable native limit is later validated.

No degree subtype, publication-type, access, full-text, peer-review, venue, or content restriction is imposed. PQDT source scope does not by itself establish completed degree status or scientific eligibility. The adapter's planned visible controls are Relevance sort, 20 records per page, source duplicate exclusion off, spelling and plural/adjective variants on, and full-text limiter off. Whether the current interface exposes and persists those states must be tested.

## 5. Retrieval, pagination, and export

The existing adapter uses normal rendered Command Line Search, an exact PQDT-only selection, rendered result cards, and the normal Abstract/Details route. Its static implementation targets numeric ProQuest document IDs, title/author/publication metadata, source type, snippets, abstracts, source ranks, a rendered total, and 20-record pages. These are implementation intent only until P01 observes them. RIS, full-text download, and native export are not automated. Diagnostic JSON and optional normalized CSV are create-only evidence, never screening or import inputs.

PQDT lacks `--count-only` and `--require-complete`. P01 therefore uses a small bounded metadata diagnostic (`--limit 1 --max-pages 1`) rather than claiming record exhaustion or completeness. A rendered total can be recorded as a source total for that operation only when the adapter reconciles it, but the bounded metadata prefix is not a complete source result and is never imported. The current adapter has no final two-pass completeness mode; completeness remains an explicit blocker for acceptance until an accepted source-specific procedure proves it.

## 6. Stable identity and completeness

The proposed identity is the numeric ProQuest document ID from the canonical PQDT result/detail route, reconciled to the rendered title. Missing, duplicate, changed, or ambiguous IDs fail closed. P01 may retrieve at most one detail record per bounded operation and records only allowlisted metadata.

P01 does not prove completeness. A later accepted final procedure must retrieve every record in every successful partition cell, reconcile the reported total to rendered rows and IDs, and add an equivalent two-pass ordered-ID stability check through an accepted adapter/runner correction. Until that exists, a positive PQDT total or a complete-looking first page cannot satisfy `G-COMPLETENESS`. No completeness claim is made now.

## 7. Failure and zero rules

An explicit, current native zero-result state with a matching query, exact PQDT product, and valid controls is the only accepted zero. Loading, blank, syntax, challenge, login, access, busy, redirect, changed database selection, missing/ambiguous field or control, missing/conflicting total, page shortfall, rank/ID mismatch, detail mismatch, query rewrite, export issue, or incomplete metadata diagnostic is a failure with `total=null` and zero retrieved/imported records. A positive rendered total with a bounded prefix is not complete and is never imported.

Challenges are never solved or retried. A busy condition may be passively waited on only under the finite policy recorded by the controller; this P01 plan declares no source-operation reissue. Stop the source operation on the first such condition, preserve its failure artifact, close only the owned page, and verify cleanup and lease release.

## 8. Final-run procedure

A later operator must first establish P-001 and an accepted campaign, then run the ordered procedure in [`p01-execution-plan.md`](p01-execution-plan.md) with a new final manifest and event namespace. For every partition, use its exact query file, append only the accepted date/language controls, select one PQDT database label, use the shared lease contract, and use a separately accepted complete retrieval/stability procedure. Keep D08 totals and provenance separate from D07. No final operation is authorized by this draft pilot bundle.

## 9. Validation evidence

There is no campaign, manifest, pilot evidence, accepted pilot ID, source total, or current-interface observation in this brand-new packet. The source-free evidence is the exact translation/specification and focused offline tests:

- `SLR/SLR1/scripts/test_proquest_source_packets.py` checks packet/file/hash invariants; and
- `../agent-tools/academic-research/skills/academic-search/tests/test_proquest_slr1_readiness.py` checks the existing adapter's offline CLI, form, and exact database-boundary parsers.

The runtime acceptance catalog is `G-SOURCE-BOUNDARY`, `G-QUERY-TRANSPORT`, `G-FIELD-BOUNDARY`, `G-CONTROLLED-VOCABULARY`, `G-DATE-CONTROL`, `G-LANGUAGE-CONTROL`, `G-CONTENT-CONTROL`, `G-RETRIEVAL`, `G-PAGINATION-CONTROL`, `G-PAGE-IDENTITY`, `G-COMPLETENESS`, and `G-FAILURE-BEHAVIOR`. The acceptance campaign must link immutable P01 evidence by SHA-256 and distinguish `observed`, `official_documentation`, `inferred`, and `untested`. No source gate can be accepted from this draft or from static code alone.

## 10. Remaining limits and protocol impact

The bundle is ready for a bounded, source-free-reviewed P01 launch, not ready for source acceptance or a final search. The principal blockers are current source boundary/field observations, dissertation metadata/subject behavior, thesaurus behavior, pair semantics, date/language controls, rendered retrieval, stable identity, and especially completeness because the existing PQDT adapter has no count-only or strict-complete mode. No concept, Boolean relationship, source boundary, evidence-window rule, language/content rule, recall rule, completeness definition, or PRISMA accounting rule was changed.
