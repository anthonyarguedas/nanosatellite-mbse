# Semantic Scholar Supplementary-Discovery Worklog

- **Review run:** `eps-mbse-slr-2026`
- **Delegated scope:** Semantic Scholar supplementary discovery only. No screening, cross-source merge, retrieval, citation chasing, or edits to shared review artifacts were performed.
- **Search date:** 2026-08-06
- **Output directory verified before writing:** `/Users/antho/nanosatellite-mbse/SLR/SLR1/searches/semantic-scholar`
- **Protocol/plan inputs reused:** `SLR/SLR1/protocol.md` and `SLR/SLR1/query-search-plan.md`; newly returned metadata/worklogs from the Scopus and IEEE primary slices were used only to identify terminology and indexing gaps. No Git history, legacy artifacts, `markdown/`, or `pdfs/` content was inspected.

## Execution convention and failure interpretation

All requests used only the academic-search Semantic Scholar script:

```bash
uv run ~/agent-tools/academic-research/skills/academic-search/scripts/search_semantic_scholar.py
```

Every request supplied `--year-start 2013 --year-end 2026 --limit 30 --max-pages 1`. The script therefore sent the Semantic Scholar query with the inclusive `year:2013-2026` prefix. The initial six probes are the six short natural-language probes specified in the plan. A final, deliberately small recovery batch added phrase-rich coverage for primary-source terminology gaps.

The nine requests all reached the Semantic Scholar endpoint but failed on **page 1** with `HTTP 403: {"message":"Forbidden"}`. This is a service/access failure, **not** a zero-result search. The script caught the HTTP exception and initially serialized the fallback shape `total: 0`, `pages_retrieved: 0`, and `results: []` while exiting successfully. During post-integration QA, each saved artifact was explicitly annotated under `output_metadata` with `status: service_failure_http_403`, the HTTP failure, and `source_total_reported: false`; the query, fallback fields, result array, and original extraction timestamp were preserved. Accordingly, every top-level `total: 0` remains a scripted fallback rather than an API-reported total. There was no source-reported hit count, rank list, or metadata record to screen.

The artifact `output_metadata.extracted_at` values are local EDT (`UTC-04:00`); the table gives both that exact saved value and its UTC conversion. Requests were grouped in batches of three. After the first batch's failures, the later batches were issued serially within their three-query batches after 20- and 60-second cooldowns, respectively, rather than repeatedly issuing concurrent requests against a forbidden endpoint.

## Complete query log

`Selection limit` records the request's deterministic diagnostic window, not a screened subset. `—` in **Source total** means the API did not report a total.

| ID | Stream | Exact query | Years / request limit | Saved local time (UTC) | Raw path | Source total | Retrieved | Assessment / gaps targeted | Retained for merge? | Selection limit / refinement lineage |
|---|---|---|---|---|---|---:|---:|---|---|---|
| SS-A1-P1 | A | `CubeSat electrical power system model-based systems engineering` | 2013–2026; 30; 1 page | `2026-08-06T10:30:54.671299` (`14:30:54Z`) | `searches/semantic-scholar/SS-A1-P1-cubesat-eps-mbse.json` | — (raw fallback `0`) | 0 | **Failed:** HTTP 403 before first page. Planned explicit EPS-primary/MBSE baseline; no source records to assess. | No | Ranks 1–30 requested; none returned. Planned-probe root; no data-driven successor. |
| SS-A2-P1 | A | `nanosatellite power subsystem SysML` | 2013–2026; 30; 1 page | `2026-08-06T10:30:54.671246` (`14:30:54Z`) | `searches/semantic-scholar/SS-A2-P1-nanosatellite-power-sysml.json` | — (raw fallback `0`) | 0 | **Failed:** HTTP 403 before first page. Planned EPS subsystem/SysML route; no source records to assess. | No | Ranks 1–30 requested; none returned. Planned-probe root; no data-driven successor. |
| SS-A3-P1 | A | `CubeSat MBSE power budget` | 2013–2026; 30; 1 page | `2026-08-06T10:30:54.558901` (`14:30:54Z`) | `searches/semantic-scholar/SS-A3-P1-cubesat-mbse-budget.json` | — (raw fallback `0`) | 0 | **Failed:** HTTP 403 before first page. Planned structured power/energy-budget route; no source records to assess. | No | Ranks 1–30 requested; none returned. Planned-probe root; expanded conceptually by SS-A5-R1 once primary terminology was audited. |
| SS-A4-P1 | A | `CubeSat system reference model electrical power` | 2013–2026; 30; 1 page | `2026-08-06T10:31:43.691530` (`14:31:43Z`) | `searches/semantic-scholar/SS-A4-P1-cubesat-reference-model-electrical-power.json` | — (raw fallback `0`) | 0 | **Failed:** HTTP 403 before first page. Planned EPS-bearing reference-model/template bridge; no source records to assess. | No | Ranks 1–30 requested; none returned. Planned-probe root; reference-model lineage is separately tested by SS-B2-R1 without an EPS requirement. |
| SS-B1-P1 | B (EPS-free) | `nanosatellite model-based systems engineering` | 2013–2026; 30; 1 page | `2026-08-06T10:31:43.945770` (`14:31:43Z`) | `searches/semantic-scholar/SS-B1-P1-nanosatellite-mbse.json` | — (raw fallback `0`) | 0 | **Failed:** HTTP 403 before first page. Planned broad embedded-thread recall; it deliberately has no EPS, outcome, or V&V gate. | No | Ranks 1–30 requested; none returned. Planned-probe root; no data-driven successor. |
| SS-V1-P1 | A sensitivity (V&V) | `CubeSat SysML verification power` | 2013–2026; 30; 1 page | `2026-08-06T10:31:44.197351` (`14:31:44Z`) | `searches/semantic-scholar/SS-V1-P1-cubesat-sysml-verification-power.json` | — (raw fallback `0`) | 0 | **Failed:** HTTP 403 before first page. Planned optional EPS-linked verification sensitivity probe; V&V was not imposed on A or B baselines. | No | Ranks 1–30 requested; none returned. Planned-probe root; no data-driven successor. |
| SS-A5-R1 | A | `CubeSat power budget interface SysML` | 2013–2026; 30; 1 page | `2026-08-06T10:35:48.514837` (`14:35:48Z`) | `searches/semantic-scholar/SS-A5-R1-cubesat-power-budget-interface-sysml.json` | — (raw fallback `0`) | 0 | **Failed:** HTTP 403 before first page. Short phrase-rich recovery probe for the primary-observed structured EPS budget/interface gap. | No | Ranks 1–30 requested; none returned. Conceptual successor to SS-A3-P1, not a result-driven refinement. |
| SS-B2-R1 | B (EPS-free) | `CubeSat System Reference Model` | 2013–2026; 30; 1 page | `2026-08-06T10:35:48.967904` (`14:35:48Z`) | `searches/semantic-scholar/SS-B2-R1-cubesat-system-reference-model.json` | — (raw fallback `0`) | 0 | **Failed:** HTTP 403 before first page. Lineage-recovery probe for reference/template models and weakly indexed proceedings/chapters. This phrase was independently exposed by the new IEEE primary metadata, so its targeted use complies with the plan's lineage-recovery rule. | No | Ranks 1–30 requested; none returned. EPS-free complement to SS-A4-P1; not a result-driven refinement. |
| SS-B3-R1 | B (EPS-free) | `CubeSat digital engineering requirements traceability` | 2013–2026; 30; 1 page | `2026-08-06T10:35:49.256282` (`14:35:49Z`) | `searches/semantic-scholar/SS-B3-R1-cubesat-digital-engineering-requirements-traceability.json` | — (raw fallback `0`) | 0 | **Failed:** HTTP 403 before first page. Short phrase-rich embedded-thread probe for digital engineering, requirements, and traceability; no EPS term and no outcome/V&V universal gate. | No | Ranks 1–30 requested; none returned. Coverage expansion from the primary metadata audit, not a result-driven refinement. |

## Readback and JSON validation

- Every saved JSON artifact was read after its run. Each full `results` list was inspected; all nine lists were empty because the endpoint failed before page one.
- A final local validation parsed **9/9** JSON files and confirmed each has a nonempty query string, numeric `total`/`pages_retrieved`, an array `results`, and an `output_metadata.extracted_at` timestamp.
- The expected failure serialization was also verified for every artifact: `total == 0`, `pages_retrieved == 0`, and `results.length == 0`. This validates file integrity only; it does **not** convert the HTTP 403 failures into valid zero-hit results.
- No result had a source rank, DOI, title, author list, abstract, publication type, or year available to inspect beyond the query metadata itself.

## Query-development rationale, coverage, and refinement lineage

The six plan probes were intentionally short rather than Scopus-style Boolean expressions. The recovery batch was based only on observed terminology from the newly returned primary metadata:

| Coverage cluster / observed primary indexing risk | Probe(s) | Status and interpretation |
|---|---|---|
| EPS-primary structured models; electrical architecture | SS-A1-P1, SS-A2-P1 | Attempted; endpoint failed before relevance/coverage could be assessed. |
| Parametric power/energy budgets bound to system models | SS-A3-P1 | Attempted; endpoint failed. |
| Structured EPS budgets and interfaces | SS-A5-R1 | Attempted as the phrase-rich successor concept to SS-A3-P1; endpoint failed. |
| Reference/template/domain models; conference/proceedings and chapter recovery | SS-A4-P1, SS-B2-R1 | Attempted. SS-B2-R1 uses the independently primary-exposed CubeSat System Reference Model lineage; the skill exposes no reliable Semantic Scholar publication-type filter, so it was a targeted ranked-discovery probe rather than a type-restricted search. Endpoint failed. |
| Whole-spacecraft MBSE with potentially embedded EPS threads | SS-B1-P1 | Attempted with deliberately EPS-free Stream B; endpoint failed. |
| Requirements, traceability, digital engineering, transformations/interoperability | SS-B3-R1 | Attempted with deliberately EPS-free Stream B; endpoint failed. |
| EPS-linked requirements/V&V and model-to-V&V terminology | SS-V1-P1 | Attempted only as an optional sensitivity probe; endpoint failed. It did not narrow or gate Stream A/B. |

There is no evidence-based overbreadth/precision refinement lineage because Semantic Scholar returned neither a total nor a first ranked record for any query. The only lineage after the planned roots is conceptual and explicitly marked as such: SS-A3-P1 → SS-A5-R1 (budget → budget/interface), SS-A4-P1 → SS-B2-R1 (EPS-bearing reference-model wording → EPS-free reference-model lineage recovery), and primary-metadata audit → SS-B3-R1 (digital engineering/requirements/traceability). It would be invalid to label any failed request as too narrow, too broad, or a zero result.

## Deterministic selection procedure

No final Semantic Scholar query was accepted, and no ranked record was available for selection. Therefore the final selection count is **0**, not a truncated top-*N* set.

If endpoint access is restored, the deterministic procedure for this supplementary source is:

1. Rerun every failed query from rank 1 with the same years and save/read the raw JSON.
2. For a query with `total <= 70`, retrieve and retain every ranked record (`--limit 70 --max-pages 1` is sufficient) rather than selecting a subset.
3. For a query with `total > 70`, inspect the first diagnostic ranks only to refine it into a shorter phrase-rich query; do not declare an unexamined top-*N* list final.
4. Accept only refined queries with a documented manageable total and retrieve all records at ranks `1..total`; preserve query/rank provenance. Stream B remains EPS-free, and outcome/V&V wording remains optional sensitivity coverage rather than a universal filter.
5. Deduplicate accepted Semantic Scholar records against new primary metadata first by normalized DOI, then by normalized title (case-folded, Unicode/punctuation/whitespace-normalized) plus year/author check when metadata are available. This later integration step is outside this slice.

## New-primary metadata comparator and novel-title result

For an auditable novelty comparator, I inspected only the **new primary final-input metadata** documented by the Scopus and IEEE worklogs: five final Scopus files (`S-A1`, `S-A2`, `S-B1r1`, `S-B3`, `S-B4`) and six final IEEE files (`I-A1-F1`, `I-A2-F1`, `I-A4-F1`, `I-A5-F1`, `I-B1-F1`, `I-B2-F1`). This is not a shared merge artifact.

- Primary final-input raw occurrences: **301**.
- Comparator title keys: **143** after lower-casing and conservative ASCII-transliteration/punctuation/whitespace normalization.
- Distinct nonempty primary DOI strings: **106**.
- Semantic Scholar source records available for comparison: **0**.
- DOI matches to the new primary set: **0**; normalized-title matches: **0**; source-unique / primary-novel Semantic Scholar titles: **0**; retained Semantic Scholar candidates: **0**.

These zeros mean *no records were delivered by a failed service*, not that Semantic Scholar has no relevant literature. No cross-source deduplication artifact was written and no title/abstract screening inference was made.

## Final handoff, source limitations, and stopping rationale

### Final Semantic Scholar merge set

- **Accepted final query IDs:** none.
- **Merge-input raw files:** none.
- **Raw records retrieved from the source:** 0.
- **Unique Semantic Scholar candidates:** 0.
- **Primary-novel Semantic Scholar candidates:** 0.

### Source limitations / risks

1. Semantic Scholar's Graph API search endpoint returned HTTP 403 for every one of nine varied queries, including the six planned probes and three spaced phrase-rich recovery probes. It supplied no source total or ranked metadata.
2. The process environment did not expose `SEMANTIC_SCHOLAR_API_KEY` (the skill may separately load a local dotenv file, whose contents were not inspected). The integration agent should treat credential/endpoint authorization, network policy, or a temporary service block as unresolved—not infer query failure.
3. The supplied script's error handling initially wrote a parseable empty response without embedding the HTTP error. Post-integration QA added explicit failure annotations to each artifact's `output_metadata`, so the saved JSON is now self-describing while retaining the script's original fallback fields.
4. Semantic Scholar was not usable here to recover sparse conference/proceedings/chapter metadata, reference/template lineages, structured interfaces, requirements/V&V, or digital-engineering records. Those recall risks remain with the primary databases, later Google Scholar fallback if separately authorized, and protocol-required citation chasing after full-text inclusions.
5. No claim about publication type, English language, EPS anchor, model anchor, explicit bridge, outcome, or V&V can be drawn from these failed requests.

### Stopping rationale

All six prescribed starting probes and one carefully limited three-query gap-recovery batch were attempted, read back, and validated. The endpoint failed consistently before page one across both Stream A and deliberately EPS-free Stream B, with a 60-second cooldown before the recovery batch. Continuing to vary queries would neither test recall nor yield a defensible result set and would unnecessarily repeat requests to a forbidden service. This supplementary slice therefore stops with a documented service failure rather than misreporting zero hits or fabricating a final query set. Rerun this slice after Semantic Scholar API access is restored; until then, do not pass any of these empty failure artifacts to the later merge as candidate inputs.
