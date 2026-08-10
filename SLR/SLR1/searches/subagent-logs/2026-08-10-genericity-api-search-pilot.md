# `pilot_not_candidate_search`: genericity/tailoring recall strategy pilot

> **Disposition after refinement:** the opaque additions remain valid retrieval diagnostics, but the unsplit relation-gated G3 query recommended in this initial report is superseded. Version 1.3 uses separately logged relation-free G1/G2, conservative C1, and model-coupled T2 partitions; see the refinement report and authoritative query plan.

**Run date:** 2026-08-10 (live activity 13:52–14:01 UTC; local start 09:49 EDT)
**Sources used live:** Scopus and IEEE Xplore only
**Status:** prospective pilot only; not a final discovery search and not a candidate search

> I am a model-assisted subagent, not a human information specialist. No record was screened, no eligibility decision was made, and no record became a candidate or evidence. I did not inspect or report titles, abstracts, or full text. All comparisons below use only opaque source IDs, source totals, and publication-date-control statuses.

## Decision

**Recommend a protocol v1.3 amendment that requires one additional candidate-generating Stream-B-G generic-model-artifact query in both Scopus and IEEE Xplore.** It must be rerun from a clean final-run directory with B1 and B2 after the amendment is approved; these pilot results must never be reused as final discovery output.

The combined G3 query produced genuine opaque-ID additions over the frozen B1∪B2 baseline:

- **Scopus:** 9 G3-only opaque IDs (12 G3, 3 in B1∪B2; B1∪B2 = 126).
- **IEEE Xplore:** 6 confirmed-current-day G3-only opaque IDs (6 G3, 0 in the confirmed B1∪B2; confirmed B1∪B2 = 59). The year/language-returned comparison is 7 G3, 1 intersecting B1∪B2, and 6 G3-only; the shared opaque ID has an unresolved exact date and is excluded from the exact-day-confirmed comparison.

This establishes extra **metadata-retrieval recall only**. It does not establish that any added opaque ID is eligible, relevant, or useful evidence.

The tailoring/reuse T1 probe is empirically a subset of B1∪B2 in both sources and should **not** become a separate discovery route. It may be retained only as an optional post-baseline subset sensitivity/tag probe.

## Controls and method

| Control | Scopus | IEEE Xplore |
|---|---|---|
| Population/model baselines | Exact current source-native B1 and B2 strings from `query-search-plan.md` | Exact current source-native B1 and B2 strings from `query-search-plan.md` |
| Years | `PUBYEAR AFT 2010 AND PUBYEAR BEF 2027` | `ranges=["2011_2026_Year"]` |
| English | `LANGUAGE(english)` | sole refinement `Language:English` |
| Publication/content type | No `DOCTYPE` clause | No `ContentType` refinement |
| Current-day control | Complete retrieval first, then opaque-ID/date-only cutoff at 2026-08-10 UTC | Same |
| Pagination/reconciliation | 25/page, `sort=eid`, two complete ordered-ID passes | 25/page, `sortType=newest`, two complete ordered-ID passes |

The analysis did not use records with an unresolved exact date in the **confirmed-current-day** IEEE overlap calculation. No returned ID was demonstrably after 2026-08-10. Scopus had zero unresolved dates. IEEE had three distinct unresolved opaque IDs across the query set; this is a date-metadata limitation, not an eligibility judgment.

All exact query strings, source request settings, query roles, and the logical T1 subset contract are preserved in private `pilot-query-definitions.json` (SHA-256 `00961bda851caa7fbe7c3d0f7e64907bdd172c7a959b79b3d5d39f08d0b8c314`).

## Query design tested

### Frozen baselines

- `S-B1`, `S-B2`, `I-B1`, and `I-B2` were fresh reruns of the frozen broad Stream-B definitions.
- The baseline set is source-local `B1 ∪ B2`; it is not a cross-source deduplication and no candidate corpus was created.

### G1/G2/G3 candidate-generating genericity expansion

The conservative G strategy was `P AND G-artifact AND structured-SE relation`:

- **G1 core artifact cluster:** exact phrases for generic/reusable/configurable models, model templates, and mission-agnostic/mission-independent models or architectures.
- **G2 structural artifact cluster:** reference architecture, domain model, metamodel, product-line/product-family model, or a variation point coupled to model/architecture.
- **Relation anchor:** requirement, function, behavior, architecture, interface, traceability, parametric, verification, or validation variants.
- **G3:** the tested combined G1 OR G2 implementation. In both sources, its opaque-ID set exactly matched the separately retrieved G1∪G2 union.

No bare `generic`, `modular`, `configurable`, `adapt`, or `template` was used without a model/architecture artifact coupling. The G strategy does not require EPS vocabulary, because it is an embedded-thread recall route rather than an EPS-explicit filter.

### T1 tailoring characterization probe

T1 used `P AND [B1-M OR (B2-M AND B2-relation)] AND coupled-tailoring-artifact`. Thus, under identical controls, it is logically a subset of `B1∪B2`. Tailoring terms included tailor/customize/adapt/configure/parameterize/instantiate/variability/reuse/template forms only when coupled to a structured-model or architecture artifact; the full source-native strings are in the query-definition artifact.

## Complete retrieval totals and date controls

`retrieved` is shown as pass-1/pass-2. Every successful row had stable source totals, unique source IDs, `retrieved == source total`, and identical ordered passes.

| Source | Query | Source total | Retrieved | Confirmed on/before 2026-08-10 | After cutoff removed | Exact date unresolved |
|---|---:|---:|---:|---:|---:|---:|
| Scopus | B1 | 85 | 85 / 85 | 85 | 0 | 0 |
| Scopus | B2 | 68 | 68 / 68 | 68 | 0 | 0 |
| Scopus | G1 | 4 | 4 / 4 | 4 | 0 | 0 |
| Scopus | G2 | 8 | 8 / 8 | 8 | 0 | 0 |
| Scopus | G3 | 12 | 12 / 12 | 12 | 0 | 0 |
| Scopus | T1 | 44 | 44 / 44 | 44 | 0 | 0 |
| IEEE Xplore | B1 | 39 | 39 / 39 | 38 | 0 | 1 |
| IEEE Xplore | B2 | 47 | 47 / 47 | 44 | 0 | 3 |
| IEEE Xplore | G1 | 0 | 0 / 0 | 0 | 0 | 0 |
| IEEE Xplore | G2 | 7 | 7 / 7 | 6 | 0 | 1 |
| IEEE Xplore | G3 | 7 | 7 / 7 | 6 | 0 | 1 |
| IEEE Xplore | T1 | 19 | 19 / 19 | 17 | 0 | 2 |

## Opaque-ID overlap against B1∪B2

“Within baseline” and “intersection” are the same set (`G∩B`); both are shown to make the requested reconciliation explicit. No source IDs are displayed; set digests are retained in the machine-readable analysis artifact.

### G variants, confirmed-current-day sets

| Source | Variant | Baseline B1∪B2 | G set | Within baseline / intersection | G-only | Baseline-only | G subset of B? |
|---|---|---:|---:|---:|---:|---:|---|
| Scopus | G1 | 126 | 4 | 1 | 3 | 125 | No |
| Scopus | G2 | 126 | 8 | 2 | 6 | 124 | No |
| Scopus | G3 combined | 126 | 12 | 3 | **9** | 123 | No |
| IEEE Xplore | G1 | 59 | 0 | 0 | 0 | 59 | Yes (empty) |
| IEEE Xplore | G2 | 59 | 6 | 0 | 6 | 59 | No |
| IEEE Xplore | G3 combined | 59 | 6 | 0 | **6** | 59 | No |

The source-year/language IEEE G3 arithmetic, retained separately because of the unresolved-date limitation, is: B1∪B2 = 62; G3 = 7; intersection/within baseline = 1; G-only = 6; baseline-only = 61. G3 equals G1∪G2 in both source/control views.

### T1 subset result

| Source/control set | Baseline B1∪B2 | T1 | Within baseline / intersection | T1-only | Baseline-only | Subset confirmed? |
|---|---:|---:|---:|---:|---:|---|
| Scopus, confirmed current day | 126 | 44 | 44 | 0 | 82 | Yes |
| IEEE Xplore, year/language returned | 62 | 19 | 19 | 0 | 43 | Yes |
| IEEE Xplore, confirmed current day | 59 | 17 | 17 | 0 | 42 | Yes |

## Recommended v1.3 addition: G3

Add this as a **required additional Stream-B-G candidate-generating recall route** for each of Scopus and IEEE Xplore. Preserve B1 and B2 unchanged; G3 supplements them. In a final run, merge/deduplicate only after all three complete, reconciled source runs have succeeded under the amendment.

### Scopus `S-G3` exact query

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture" OR "reference architecture" OR "domain model" OR metamodel OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture))) AND TITLE-ABS-KEY(requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

Use the existing Scopus API contract unchanged: `COMPLETE`, `count=25`, zero-based `start`, `sort=eid`, in-memory `X-ELS-APIKey`, no document-type restriction, complete two-pass reconciliation, then an exact-day first-formal-publication cutoff. Do not serialize the key.

### IEEE Xplore `I-G3` exact query

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture" OR "reference architecture" OR "domain model" OR metamodel OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture))) AND (requirement OR requirements OR function OR functions OR behavior OR behaviors OR behaviour OR behaviours OR architecture OR architectures OR interface OR interfaces OR traceability OR parametric OR parametrics OR verification OR validation)
```

Use the existing IEEE request shape unchanged except `queryText`: 25/page, one-based `pageNumber`, `sortType=newest`, `ranges=["2011_2026_Year"]`, sole `Language:English` refinement, and **no** `ContentType` refinement. Retrieve two complete ordered passes and apply the exact-day cutoff afterward.

### Precision risk and safeguard

G3 can retrieve generic architecture, software/product-line, or language/metamodel work that is not ultimately within review scope. The P block and structured-SE relation anchor reduce that risk, but cannot quantify it without screening; no such screening occurred here. This is an acceptable recall-oriented Stream-B workload consequence, not a rationale to add a publication-type, EPS, outcome, tailoring, access, or lightweight filter. The final process must apply the protocol’s ordinary screening rules only after valid discovery artifacts are merged.

## T1 recommendation

Do **not** add T1 as a fourth discovery route. Its observed zero `T1-only` sets match its Boolean subset construction. If the parent wants a reproducible descriptive sensitivity check, retain T1 as an optional tag/subset probe after B1∪B2 (and G3) retrieval; do not use it to gate eligibility or to create a separate discovery event.

## Reconciliation issue retained as a failure, not relabeled as zero

The first exact-query G1 attempts using the frozen driver failed its parser before valid reconciliation:

- Scopus: terminal response advertised `itemsPerPage=4` rather than the requested 25.
- IEEE Xplore: a zero-result response advertised `totalPages=1` rather than the driver’s expected 0.

Those failures are retained under `runs/S-G1` and `runs/I-G1` and are **not** interpreted as zero-result searches. A job-local adapter (SHA-256 `31be348b10cfdb1eb0ffdd0e4f17b85be05cadf3d2e5e1725b9ba7539c3cb6d3`) accepted only these terminal-page conventions while preserving strict request shape, ID uniqueness, total stability, two-pass ordering, and `retrieved == source total`. Clean exact-query reruns then yielded the successful G1 rows above. The adapter rationale is retained privately as `provenance/terminal-page-adapter-rationale.md`. A v1.3 implementation should incorporate and test this narrow source-interface accommodation prospectively rather than silently treating a parser failure as a source zero.

## Provenance, tool versions, and artifacts

- Tool/runtime observed: `uv 0.9.28 (0e1351e40 2026-01-29)`; the reconciler runtime reported CPython 3.13.5 and `requests 2.34.2`.
- Frozen request template SHA-256: `15087ec37cf4c510fae78583df248c28703a3257365e8e1dea6d73cd4b48a66a`.
- Frozen reconciler SHA-256: `be9fd8a5202ddb8ef5fec96855d119d840a8c9fbcbbb1f8393836df594d6801e`.
- Opaque-ID/date/overlap analyzer SHA-256: `fc5fe72088f49777968983c9b799f131d1c19dca57fbdc259aa8487723129a15`.
- Machine-readable opaque-ID analysis SHA-256: `5c7cb22f8b3cdb8c3210554d63c76d691e72b97e8732715adafb64f8d0e5565e`.
- Executive summary SHA-256: `3bf8d130c3b783e066f14bf9dd9b668ad8cd291647ad720c2e40d222b6efb2d9`.
- Each successful run has a private `manifest.json` with raw-page/request/reconciliation file checksums. The final job-level SHA-256 manifest is `artifact-manifest.sha256` (created after this report; it excludes only itself and the `uv` dependency cache).

All pilot artifacts—including raw source response pages, request descriptors, page-ID reconciliations, failure artifacts, query definitions, analyses, and reports—are only under:

```text
/var/folders/db/fjbrfx1n1kz6lrqlm7jvryp00000gn/T/pi-subagent-search-20260810-094714-7551-16193
```

No repository artifact was edited; no output was merged into `SLR/SLR1`, a candidate corpus, or a screening log. Credentials/cookies/tokens were neither exposed nor serialized.

## Complete command/tool inventory

A verbatim safe command inventory is retained privately as `commands-and-tools.md`. The complete tool/command list is also summarized here (no command contains a secret):

1. **`functions.read`:** protocol (two chunks), query plan (two chunks), academic-search skill, allowed API template/reconciler, allowed Scopus/IEEE client sources, then only job-local non-bibliographic provenance, validation, adapter, opaque-ID analysis, executive-summary, and manifest artifacts. No prohibited cache/corpus/history material was read.
2. **`functions.write`:** job-local `pilot-query-definitions.json`, adapter rationale, opaque-ID analysis script, `commands-and-tools.md`, and this `report.md`.
3. **`functions.edit`:** job-local terminal-page adapter; job-local query definition to add G3; job-local analyzer to add G3/timing fields; job-local command inventory finalization. No repository file was edited.
4. **`functions.bash` setup/provenance:** `mkdir -p "$JOB"`; create private subdirectories; `date`, `uv --version`, `python3 --version`, a present/absent-only secure-variable check, `shasum -a 256`; `jq -e` query-definition checks; a readable-only test of the secure Scopus runtime file; adapter copy/help/checksum commands.
5. **`functions.bash` live source calls (all via `UV_CACHE_DIR="$JOB/.uv-cache" uv run …api_pagination_reconcile.py` or its job-local adapter):** paired Scopus/IEEE B1; paired B2; paired G1 initial frozen-driver attempts (retained failures); paired G1 adapter reruns; paired G2; paired T1; paired G3. Every invocation used `--passes 2 --classification pilot_not_candidate_search`; Scopus used `--scopus-sort eid`, and IEEE used years 2011–2026, English, `newest`, and `--ieee-no-content-type-filter`. Scopus commands loaded the secure runtime in memory only; its contents were never emitted.
6. **`functions.bash` analysis/finalization:** `uv run` opaque-ID analyzer help/execution (then a rerun after G3), a `jq` safe-field projection, key-artifact checksums, JSON syntax validation, and three final `find | sort | xargs shasum` manifest generations (the last after the report-inventory correction).
7. **`multi_tool_use.parallel`:** dispatch wrapper for independent reads and paired source calls only.

The only live endpoints were Scopus and IEEE Xplore. No Google Scholar, Semantic Scholar, arXiv, or other source was contacted.
