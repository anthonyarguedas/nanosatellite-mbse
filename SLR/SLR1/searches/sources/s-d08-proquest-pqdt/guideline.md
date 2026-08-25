---
task_id: S-D08
source_id: proquest-pqdt
source_name: ProQuest Dissertations & Theses Global
method_type: direct
status: draft_blocked_return_to_exploration
guideline_version: 0.1.0
validated_at: null
protocol_commit: 699f010f02b81dc17c7f17491dab77dbf9bb1feb
accepted_pilot_ids: []
---

# Source-specific guideline: ProQuest Dissertations & Theses Global

> **Two-mode validation:** Apply the [current policy](../../two-mode-validation-policy.md). First use agent-driven exploration to make the real interface work; then use a separate frozen deterministic evidence attempt. Exploration findings guide implementation but do not pass acceptance gates.


This is a blocked, diagnostic-only, no-screening/no-import draft. P01 and P02 are immutable technical failures at the first live field/thesaurus route; they establish no source total or accepted interface behavior. Continue under [`resume-plan.md`](resume-plan.md) in exploration mode before another evidence attempt.

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

P01 predeclares the pilot-date diagnostic lower bound `2011-01-01` and upper bound `2026-08-25`. This is not the common cutoff and does not resolve P-001. PQDT has no separate adapter `--year-start`, `--year-end`, or `--language` option. The runner therefore appends the diagnostic candidate `AND YR(2011-2026) AND LA(English)` to each probe/partition query. This year-granular suffix is a planned diagnostic, not an exact day/month cutoff or final common filter. Full-report language remains a screening field unless a reliable native limit is later validated. Agent-tools commit `17a64bf` adds source-free-tested `--count-only` and strict `--require-complete` modes without changing those controls or query semantics.

No degree subtype, publication-type, access, full-text, peer-review, venue, or content restriction is imposed. PQDT source scope does not by itself establish completed degree status or scientific eligibility. The adapter's planned visible controls are Relevance sort, 20 records per page, source duplicate exclusion off, spelling and plural/adjective variants on, and full-text limiter off. Whether the current interface exposes and persists those states must be tested.

## 5. Retrieval, pagination, and export

The existing adapter uses normal rendered Command Line Search, an exact PQDT-only selection, rendered result cards, and the normal Abstract/Details route. Its static implementation targets numeric ProQuest document IDs, title/author/publication metadata, source type, snippets, abstracts, source ranks, a rendered total, and 20-record pages. These are implementation intent only until P01 observes them. RIS, full-text download, and native export are not automated. Diagnostic JSON and optional normalized CSV are create-only evidence, never screening or import inputs.

P01 uses record-free `--count-only --limit 1 --max-pages 1` for field and partition diagnostics. A rendered total can be recorded only when the adapter reconciles it; count-only outputs are explicitly non-reportable and retain no records. If exact A1 is positive and at most 40, P01 conditionally exercises `--require-complete --limit 40 --max-pages 2`: two exhaustive rendered passes must reconcile the total and identical ordered numeric ProQuest document IDs, and only a create-only terminal marker can make that bounded output mergeable. A1 zero or a total above 40 skips the strict diagnostic rather than substituting another query. P01 still cannot prove all-cell final completeness.

## 6. Stable identity and completeness

The proposed identity is the numeric ProQuest document ID from the canonical PQDT result/detail route, reconciled to the rendered title. Missing, duplicate, changed, or ambiguous IDs fail closed. P01 may retrieve at most one detail record per bounded operation and records only allowlisted metadata.

P01 can prove bounded A1 completeness only if its natural count falls within the predeclared 1–40 range and both strict passes succeed. Otherwise `G-COMPLETENESS` remains untested. A later accepted final procedure must set bounds covering every successful partition cell, retrieve every record, reconcile each reported total to rendered rows and IDs, and run the same two-pass ordered-ID stability check. A positive count or complete-looking first page alone never satisfies completeness.

## 7. Failure and zero rules

An explicit, current native zero-result state with a matching query, exact PQDT product, and valid controls is the only accepted zero. Loading, blank, syntax, challenge, login, access, busy, redirect, changed database selection, missing/ambiguous field or control, missing/conflicting total, page shortfall, rank/ID mismatch, detail mismatch, query rewrite, export issue, or incomplete metadata diagnostic is a failure with `total=null` and zero retrieved/imported records. A positive rendered total with a bounded prefix is not complete and is never imported.

Challenges are never solved or retried. A busy condition may be passively waited on only under the finite policy recorded by the controller; this P01 plan declares no source-operation reissue. Stop the source operation on the first such condition, preserve its failure artifact, close only the owned page, and verify cleanup and lease release.

## 8. Final-run procedure

A later operator must first establish P-001 and an accepted campaign, then run the ordered procedure in [`p01-execution-plan.md`](p01-execution-plan.md) with a new final manifest and event namespace. For every partition, use its exact query file, append only the accepted date/language controls, select one PQDT database label, use the shared lease contract, and use a separately accepted complete retrieval/stability procedure. Keep D08 totals and provenance separate from D07. No final operation is authorized by this draft pilot bundle.

## 9. Validation evidence

Campaign [`S-D08-C01`](campaign.json) preserves P01/P02 technical failures. Their live evidence is useful only to motivate exploration; neither passes a gate. Agent-tools source-free tests cover intended count/strict contracts but do not establish current PQDT behavior. The next accepted behavioral evidence must come from a frozen evidence attempt after `S-D08-X01` demonstrates the route live.

The runtime acceptance catalog is `G-SOURCE-BOUNDARY`, `G-QUERY-TRANSPORT`, `G-FIELD-BOUNDARY`, `G-CONTROLLED-VOCABULARY`, `G-DATE-CONTROL`, `G-LANGUAGE-CONTROL`, `G-CONTENT-CONTROL`, `G-RETRIEVAL`, `G-PAGINATION-CONTROL`, `G-PAGE-IDENTITY`, `G-COMPLETENESS`, and `G-FAILURE-BEHAVIOR`. The acceptance campaign must link immutable P01 evidence by SHA-256 and distinguish `observed`, `official_documentation`, `inferred`, and `untested`. No source gate can be accepted from this draft or from static code alone.

## 10. Remaining limits and protocol impact

The source returns to exploration mode and is not ready for source acceptance or a final search. The principal blockers are the current database-selection/Command Line route, field/thesaurus projection, dissertation metadata/subject behavior, pair semantics, date/language controls, rendered retrieval, stable identity, and live validation of count/strict-complete behavior. No concept, Boolean relationship, source boundary, evidence-window rule, language/content rule, recall rule, completeness definition, or PRISMA accounting rule was changed.
