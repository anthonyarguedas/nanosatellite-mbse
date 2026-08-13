# Search and source-interface log

**Review run:** `eps-mbse-slr-2026`<br>
**Protocol status during historical entries below:** version 1.1/1.2 pre-search validation; version-1.3 genericity, version-1.4 source-addition, version-1.5 source/completeness, and version-1.6 thesis/dissertation entries are prospective amendment design or pilots<br>
**Current protocol status:** version 1.6 thesis/dissertation amendment frozen and authorized 2026-08-10; V16-C fixed-visible-25/page Engineering Village transport successor implemented/hash-pinned offline after its 2026-08-11 prospective authorization, but not accepted live; fourteen independently searched sources/collections through twelve interfaces; common evidence cutoff 2026-08-10; no final discovery run is recorded below<br>
**Time zone unless stated otherwise:** EDT (UTC−04:00)

## Status boundary

Every entry dated 2026-08-06, 2026-08-07, 2026-08-10, or 2026-08-11 below is `pilot_not_candidate_search` unless explicitly labeled protocol-design-only: it validates source syntax, controls, pagination, export, matching, or prospective amendment design. No pilot record or opaque identifier establishes discovery provenance, relevance, eligibility, or evidence membership. Every accepted strategy must be run anew under version-1.6 authorization in a clean final-run directory; only those later final-run artifacts may create the independent candidate set.

Aggregate behavior and checksums are retained here without importing pilot hits into screening. The 2026-08-06 raw diagnostics are retained read-only in the access-controlled, Git-ignored `.searches/eps-mbse-slr-2026/interface-pilots/2026-08-06/` work area and indexed by `manifest.json` (88 files; manifest SHA-256 `0e5986a1cd43b8fb1cab65b00ba8863696127eadb579ac9b000e1492bfcd31b4`). The Web of Science export and merge diagnostics are retained under `.searches/eps-mbse-slr-2026/interface-pilots/2026-08-07/` (6 files; manifest SHA-256 `c137b96f8e5406cdbc04783bf1d2ada45446e43959e11c1ad76b0884d2bb80eb`). The population-term API/count pilots are retained under `.searches/eps-mbse-slr-2026/term-variant-pilots/2026-08-07/` (85 files; manifest SHA-256 `12b249a440bda72b4ba2a74b82e90ff3e74f23aeb9aea63a8e3dd4f37e9a8f68`). The two-pass Scopus/IEEE API pilots are under `.searches/eps-mbse-slr-2026/multipage-api-pilots/2026-08-07/`, with source manifests SHA-256 `b0b395fdd388533912511cc296300c30657dd22fc70a341687fe37b1a6f70619` (Scopus) and `c18c2c3d558be6fa8b9c7a931dfd4e40e9765d65fbecdb0ca60254278c97bd25` (IEEE).

PRESS-fix pilots are under `.searches/eps-mbse-slr-2026/press-fix-pilots/2026-08-07/`. Key manifests are: API count/strict artifacts `fda7a1ab5a373b4ab8cd25835fe2f5f5a1d1cda31ea66378ab0a8318844f2217`; browser sources `5c98bffe52e4aaa46ea15437aad538fa9dbcf0414c0a29c8eb9d77a714f086e5`; WoS follow-up `0e516843d2e40bf4aae949e94f641de442613f79cd08c6577c483a5f03f7c3bc`; revised NTRS matrix `6a39421df2e5797e47b3b34e67be71330afd7ebf851c02d88862c228a89b1a9a`; and active post-purge/corrected-rematch ESA artifacts `ae1aba9681d63237ae33b0896cefb94787c24bc4086aeb40d8fe501ecde3f8e8`. These artifacts are not the SLR corpus and must not be passed to candidate screening or represented as final-run discovery output.

## Live gate attempts — 2026-08-13

**Status:** `pilot_not_candidate_search`; these are source-access/control attempts, not final discovery. No title, author, abstract, identifier, candidate, screening decision, PRISMA count, or merge input was retained. Per the fail-closed contract, neither access state was retried.

| Gate event | UTC interval / controls | Outcome | Immutable owner-only artifact |
|---|---|---|---|
| `OATD-B2` aggregate count gate | `18:40:32.328Z`–`18:40:35.230Z`; package `oatd_basic_count_gate.py`, exact pinned manifest, loopback owned page, one navigation, no retries | `access_state`; source total `null`; retrieved/serialized records `0`; no merge/candidate import | `.searches/eps-mbse-slr-2026/live-gates/2026-08-13/oatd/oatd-b2-count-gate.json` (SHA-256 `064ac3314977c33dd8b68713971e34785bac225e0e829f1c1703b70a5b49e2b8`) |
| `W-B1` Articles & Chapters count gate | exact frozen W-B1 expression; `2011-01-01`–`2026-08-10`; Earliest; isolated visible browser; count-only; no retries | `WileyAccessError` / Cloudflare-CAPTCHA access challenge; source total `null`; pages/results `0`; no RIS, merge, or candidate import | `.searches/eps-mbse-slr-2026/live-gates/2026-08-13/wiley/w-b1-count-gate.json` (SHA-256 `8a47fe1361211e0cd26b382769da3640675565cfe4c74608469eb4b299605caa`) |
| `SN-B1` Link count gate | exact frozen SN-B1 expression; `2011-01-01`–`2026-08-10`; English; Relevance; owned visible browser; count-only | `SpringerSnapshotChangedError`: ordered canonical-path sequence changed between the required passes; total unavailable; normal JSON/CSV suppressed; no merge/candidate import | `.searches/eps-mbse-slr-2026/live-gates/2026-08-13/springer-nature-link/sn-b1-count-gate.NON_MERGEABLE_DIAGNOSTIC.json` (SHA-256 `689731af4e80b92b9bca03df8dbc4a922e9d54c66331ae583edc12e7703a5c6f`) |
| `PQ-B1` ATAI count gate | exact frozen PQ-B1 expression; only ATAI intended; `YR(2011-2026)` / `LA(English)`; isolated browser; count-only | owned page drifted before the authorized database-selection target could be confirmed; source total `null`; no source state, cards, export, merge, or candidate import | `.searches/eps-mbse-slr-2026/live-gates/2026-08-13/proquest-aerospace-index/pq-b1-count-gate.operator-failure.json` (operator failure record; SHA-256 `ee02bae79ccdc0f5daa15604b8fe83de2b6b65a4d478a75b15d67bf8cd9778d9`) |
| `I-B1` IEEE count gate | exact frozen I-B1 expression; 2011–2026; sole `Language:English` refinement; no ContentType; one-record count-only request | exact source total `39`; one source record was used transiently only to obtain the total; serialized results `0`; no abstract enrichment, merge, candidate import, or screening | `.searches/eps-mbse-slr-2026/live-gates/2026-08-13/ieee-xplore/i-b1-count-gate.json` (SHA-256 `ef7130bcaa953ded266de87dcb136103db6ca2646ee39f6819428f8e6457bb43`) |

All artifacts and their directories have owner-only `0700`/`0600` permissions. These failures leave `V16-OATD-02`, `V16-W`, `V16-SN`, and `V16-PQ` open and do not create a final-source failure disposition or a final-run root.

## Version-1.6 thesis/dissertation synchronization and source pilots — 2026-08-10

**Amendment status:** `protocol_design_only`; authorized before any valid final discovery search, screening, codebook creation, or extraction. Version 1.6 admits completed master's-level theses and doctoral dissertations/theses under every existing scientific/full-report requirement and adds exact-database ProQuest Dissertations & Theses Global (PQDT Global) plus whole-index Open Access Theses and Dissertations (OATD). The operational baseline is fourteen independently searched sources/collections through twelve interfaces. PQDT is a named database in a second, never-combined ProQuest event; OATD is a mandatory indexed online resource reported in the PRISMA website/other-methods channel. The ten direct source/query families contain 110 logical blocks; the eleven PQDT blocks normatively reuse the corresponding ProQuest `PQ-*` bodies under a distinct database selection/event/provenance, while OATD has eleven explicit finite translations.

**Pilot status:** `pilot_not_candidate_search`; completed internet-enabled subagent and orchestrator reports were restricted to source documentation, source identity, controls, syntax, aggregate totals, and mechanical row/range counts. Those completed reports confirm that no title, author, abstract, snippet, identifier value, record URL, full text, export, candidate, relevance judgment, or eligibility judgment was inspected, and no such content was preserved or imported. The later canceled B2-only runner returned no report, so no claim is made about whether it reached source navigation; it contributed no source data. Times cross the UTC date boundary; local time is EDT (UTC−04:00).

### PQDT Global aggregate gate

Two fresh isolated-profile probes reached a managed `Just a moment…` challenge before exact database selection or query submission. Their totals are `null`, not zero. A later owned-tab normal-browser follow-up verified that the only selected semantic source was **ProQuest Dissertations & Theses Global**; the displayed “Full Text Included” product-label suffix did not activate the separate Full text limiter, which remained unchecked. No all-databases, PQDT Open, institution-specific, aerospace, or other ProQuest source was selected.

Observed common controls were Relevance, 20/page, source duplicate exclusion off, no full-text/peer-review/source-type/document-type limiter, and automatic spelling plus plural/adjective variants on. The expansion state was frozen as observed, not interpreted as source-set equivalence.

| Pilot ID | Local / UTC start | Elapsed | Aggregate | Disposition |
|---|---:|---:|---:|---|
| `PQDT-A1` | 20:41:05.427 / 00:41:05.427 | 0.780 s | 1 | exact query echo; aggregate accepted as diagnostic only |
| `PQDT-B1` | 20:30:58.028 / 00:30:58.028 | 1.345 s | 17 | exact `NOFT`/year/language echo; diagnostic only |
| `PQDT-B2` | 20:31:32.738 / 00:31:32.738 | 1.113 s | 9 | exact `NOFT`/year/language echo; diagnostic only |

Exact selection remained unchanged after the runs. Pagination, stable source IDs, native zero, paging/export caps, RIS, exact-day accounting, two-pass retrieval, normalization, and merge remain open gates. `search_proquest_aerospace.py` was used only as an offline design/test reference and cannot be relabelled as PQDT.

### OATD interface and finite-query gate

The normal <https://oatd.org/> interface exposed a basic GET `/oatd/search?q=...` route and an advanced composer with four Boolean rows, any-field and named metadata fields, year/language/country controls, Relevance, 30/60/100 page sizes, and a Creative-Commons-only control. No degree filter was observed. Basic aggregate-only checks accepted exact phrase `"cube sat"` (12; 12/12 mechanical first-page containers) and grouped Boolean `("CubeSat" OR "CubeSats") AND ("MBSE" OR "SysML")` (18; 18/18 containers), each with an exact query echo. No container content was read.

An advanced-composer baseline returned `Server Too Busy - Please slow down` after 20.180 seconds; its total is `null`. Direct HTTP/fresh-browser orchestrator checks were challenge-blocked. After a cooldown, a separate owned-tab retry submitted the complete frozen finite `OATD-B1` through the basic route:

| Pilot ID | Local / UTC interval | Elapsed | Aggregate | Disposition |
|---|---:|---:|---:|---|
| `OATD-B1` | 20:49:08.203–20:49:10.857 / 00:49:08.203–00:49:10.857 | 2.654 s | 23 | exact echo; displayed 1–23 of 23; 23 mechanical rows; diagnostic only |
| `OATD-B2` | not submitted | n/a | `null` | owned tab had closed before state assertion/navigation; not zero |

A1 was not attempted in the cooldown retry. A later focused B2-only internet subagent produced no stdout, stderr, or source-state report within 15 minutes and was canceled by the orchestrator. That orchestration timeout adds no source result or syntax evidence: B2 remains total `null`, not zero, and no partial state is imported. The plan therefore freezes explicit finite OATD forms without assumed wildcard behavior and uses local date/language screening unless a later set-equivalence gate validates composer controls. Native zero, full B2 and remaining strings, 30-row pagination, stable identity/order, source cap, two passes, exact-day handling, repository-link provenance, normalization, and merge remain open.

### Tooling and retained pilot provenance

`search_strategy_lint.py` now passes with 99 physical query blocks plus 11 normative PQDT aliases = 110 logical blocks, dictionary/protocol version 1.6, fourteen-source/twelve-interface contracts, and all retained NTRS/IAF controls. `merge_search_results.py` now canonicalizes PQDT Global as `proquest_dissertations_theses_global` and OATD as `oatd`, separately from `proquest_aerospace_index`; its expanded 17-test offline suite passes, including synthetic PQDT/OATD DOI deduplication with both discovery provenances retained. Merger SHA-256 is `5236ea33130249e1b1c8074ed8d009def9c9b968572c65d850f290b5bfb91e32` and test SHA-256 is `2f686adc887fac7aa9fecaac0842843d7c330e59b23de4a6fdd7ef41f82eff8f`.

The owner-restricted, Git-ignored archive is `.searches/eps-mbse-slr-2026/theses-dissertations-amendment-pilots/2026-08-10/`; its 71-file manifest SHA-256 is `3a60a106975f125dc1effc4769e67f6663b7f306b86be4344c955d098bb17210`. The narrative report is [`2026-08-10-thesis-dissertation-source-pilots.md`](searches/subagent-logs/2026-08-10-thesis-dissertation-source-pilots.md). The cumulative open and carried-forward promotion gates are [`pilots-to-run-v1.6.md`](pilots-to-run-v1.6.md). No PQDT/OATD production adapter is authorized yet; adapter absence cannot waive either source, and an unresolved final access/interface failure imports no partial records.

## Version-1.6 thesis-source validation round 2 — 2026-08-10/11

**Status:** `pilot_not_candidate_search` plus synthetic offline contract validation. No final discovery query, candidate import, screening, or evidence decision occurred.

A new exact `OATD-B2` browser attempt ran from 21:34:53.822 to 21:34:58.911 EDT (01:34:53.822–01:34:58.911 UTC; 5.089 seconds) and stopped on a local browser/runtime timeout before the actor confirmed an owned target or inspected source state. A browser doctor later showed a known pilot-owned target at the exact B2 URL; the orchestrator closed it and the other known pilot-owned OATD tabs without inspecting result state. Echo, controls, range, containers, and aggregate were not established, so B2 remains total `null`, not zero. A separate impossible-string PQDT native-zero/control attempt reached the normal database-selection page but stopped on a local automation command error before checkbox-state inspection; no selection changed, no sentinel was submitted, and its total is also `null`.

The 22-event [`thesis-source-query-manifest-v1.6.json`](searches/thesis-source-query-manifest-v1.6.json) (SHA-256 `df1fbc09d8fa88f7d02564445c9fb8644b40cdbeabf58fd7d57bf6a28ce23040`) pins all PQDT aliases and finite OATD bodies plus source controls. At this historical validation boundary, review-local `oatd_basic_count_gate.py` and `search_proquest_pqdt_global.py` were implemented and hash-pinned; the later 2026-08-13 follow-up moved the PQDT wrapper to the academic-search package. They are aggregate-only, loopback-CDP, non-production validation wrappers: they expose no arbitrary source/query option, read no record cards/IDs, serialize no candidate record, cannot create merge input, and deliberately reject native zero. Both read the pinned manifest once as bytes, hash and decode those same bytes, map ordinary runtime failures to fixed-code error artifacts with `source_total: null`, and publish no-clobber owner-only `0600` JSON artifacts. OATD no longer scans broad headings (`h1`/`h2`); PQDT requires exactly one visible unchecked **Full text** control, scans named Full text/peer-reviewed/source-type/document-type/degree-manuscript/access controls including non-visible controls, and makes two same-owned-page PQDT-only selector assertions. Live confirmation of the current DOM mapping and external ABA remain explicit `V16-PQDT-02` residuals. The three synthetic suites pass **49/49** tests (`18` OATD + `27` PQDT + `4` shared-fixture). This validates only the offline implementation portions of `V16-OATD-01` and `V16-PQDT-01`; current live controls, B2/remaining query acceptance, native zero, pagination, identity, caps, two passes, export/capture, normalization, merge, and date/language gates remain open. `V16-G03` remains open until version-control promotion and all final adapters are frozen.

The frozen final-run governance contract is [`final-run-source-crosswalk-v1.6.json`](searches/final-run-source-crosswalk-v1.6.json) (`48caa54a0624630c3f2fb1b69e2dc2dec99fcb13632a7e83743263241a89b25c`), [`final-run-manifest-schema-v1.6.json`](searches/final-run-manifest-schema-v1.6.json) (`fd6720eac1bd6e66021c4517ad94b68bd5330905b5ae75f3a1e4af24c63398f1`), and [`failure-register-schema-v1.6.json`](searches/failure-register-schema-v1.6.json) (`6953266f0be7ca902638bdcf18681958391ace4eaea99e40e9e8e0d182d22658`). The review-specific PRISMA mapping places OATD alone in other methods/websites and the other thirteen structured collections in databases/registers, with separate Compendex/Inspec instances and ATAI/PQDT events. The current-byte `final_run_governance_lint.py` SHA-256 is `9ef6622a0955ad647536c83e443391abf83aa6afbd5c217ef5904db4a86a8588`; it passes 14 sources, 12 interfaces, two positive and eight negative synthetic contracts. The two added schema-valid negatives prove that duplicate source IDs and a valid-but-wrong OATD interface/PRISMA mapping fail crosswalk binding; unavailable/failed totals remain `null` and cannot import partial records or contribute flow counts. Optional `--manifest PATH` schema-validates and binds any future real manifest to the exact 14 IDs each once, exact interface/PRISMA mappings, and the current crosswalk byte hash; it creates no real manifest/root. This resolves the independent audit's medium governance issue. `V16-G02` is accepted offline and deferred for instantiation at promotion; `V16-G03` remains open overall.

Detailed methods and dispositions are in [`2026-08-11-thesis-source-validation-round-2.md`](searches/subagent-logs/2026-08-11-thesis-source-validation-round-2.md). The private, owner-restricted, Git-ignored raw archive is `.searches/eps-mbse-slr-2026/thesis-source-validation-round-2/2026-08-11/`; it has 154 indexed files and manifest SHA-256 `5e74b31983baa32855f338defee5b24e48b73312b00ea44f95625c699cc801ec`. It is non-candidate and not merge input. The review remains **not ready for final discovery**.

## V16-PQDT limiter-state hardening and OATD follow-up — 2026-08-13

**Status:** `pilot_not_candidate_search` / offline contract validation; no final discovery, candidate, screening, PRISMA count, or merge input was created.

Package `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts/search_proquest_pqdt_global.py` now scans named Full text, peer-reviewed, source-type, document-type, degree/manuscript, and access controls across visible and non-visible inputs/selects, retaining only counts and booleans and failing closed on active or ambiguous state. It requires the review-local manifest path but accepts only bytes matching its fixed SHA-256. `py_compile`, scoped Ruff, `search_strategy_lint.py`, and all thesis-wrapper regressions passed (**53/53**: 18 OATD, 31 PQDT, 4 shared). Current hashes and test details are in [`2026-08-11-thesis-source-validation-round-2.md`](searches/subagent-logs/2026-08-11-thesis-source-validation-round-2.md).

One fresh dedicated-browser aggregate-only `OATD-B1` invocation ran from `2026-08-13T17:00:33.522Z` to `2026-08-13T17:00:34.035Z` and failed closed with `access_state`; it was not retried. `source_total` is `null`; retrieved/serialized candidates are `0`; merge input and candidate import are `false`. The owner-only immutable artifact `.searches/eps-mbse-slr-2026/v16-oatd-02-20260813T170027Z-79209/OATD-B1.count-gate.json` contains only aggregate/control failure fields. It establishes neither source access nor control/aggregate state, so all OATD live gates remain open.

The initial `PQDT-B1` attempt at `17:09:10.400Z` failed before source-state serialization because of a local asynchronous-generator bug in result-option validation. Operator-directed corrected follow-ups safely diagnosed the current no-expander controls and fixed `/pqdtglobal/commandline/advanced` redirect; every failed artifact is retained with `source_total: null`, zero records, and no merge input. The final aggregate-only `PQDT-B1` control at `17:21:01.561Z` succeeded: exact PQDT selection twice, exact current route, query echo, Relevance/20, duplicate exclusion off, expansion on, all named limiter states inactive, and total **17**. It serialized no record and remains `pilot_not_candidate_search`; native zero, ABA, pagination, identity, cap, export, normalization, and date/language remain open. The complete immutable artifact sequence and checksums are in [`2026-08-11-thesis-source-validation-round-2.md`](searches/subagent-logs/2026-08-11-thesis-source-validation-round-2.md). `V16-PQDT-02` is now partial, not final-ready.

## Version-1.5 source/completeness synchronization — 2026-08-10

**Status:** `protocol_design_only`; authorized before any valid final discovery search, screening, codebook creation, or extraction. Version 1.5 expands the baseline to twelve databases/collections through eleven interfaces by authorizing IAF Digital Library for IAC proceedings. It includes every permitted `search_*.py` source adapter in `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts`; arXiv, Semantic Scholar, and Google Scholar remain forbidden, while Web of Science Core Collection remains an additional normal-interface source.

The amendment also adds direct-source A3 so `A1∪A2∪A3 = P∧E_all∧M_all`; completes IEEE finite T2 inflections; restores all nine domain-language model anchors so NTRS has 51 C1 atoms and 940 cells; standardizes exact finite V1/O1 queries and local tags; freezes 2026-08-10 as the common cutoff for every electronic and citation source; and extends `search_strategy_lint.py` to all eight direct families, 88 queries, the 13 source scripts, and the new arithmetic. Those uncompleted gates are now carried forward in the cumulative [`pilots-to-run-v1.6.md`](pilots-to-run-v1.6.md). No prior pilot or IAF smoke output becomes a candidate or final count.

**IAF authorization boundary:** `authorized_final_method_not_yet_run`. The earlier public-adapter gate remains `pilot_not_candidate_search`; no planned `IAF-P-YYYY` cell has run. Final IAF discovery requires clean version-1.6 annual artifacts and deterministic local fixtures under the retained authorized method.

## Version-1.4 source-coverage synchronization — 2026-08-10

**Status:** `protocol_design_only`; authorized before any valid final discovery search, screening, codebook creation, or extraction. Version 1.4 retains the version-1.3 eligibility, RQs, genericity methodology, and search concepts while expanding the independent electronic baseline to eleven databases/collections through ten interfaces: paired Compendex+Inspec on Engineering Village, plus full Springer Nature Link, exact Advanced Technologies & Aerospace Index on ProQuest, and source-wide AIAA ARC. The added-source pilots and adapter gates remain `pilot_not_candidate_search`; none supplies a candidate or final count. Every accepted source strategy must run anew in clean version-1.4 final storage. The frozen version-1.4 protocol SHA-256 is `e909e1430f85989c6ef53a00ecd641404f5bc26e4f7f32f79d072a63bfdbc9c5`; the retained concept dictionary SHA-256 is `9aff07036892cdde7907f3f48d62c736c0727abe6a15c66505c18424f229be67`. The query plan now also records a clearly blocked post-version-1.4 IAF proposal; that prospective text does not alter the eleven-collection authorization frozen in this protocol.

**IAF status at the version-1.4 freeze (historical, superseded by version 1.5):** `prospective_source_proposal_not_authorized`. The aggregate/public-adapter gate was and remains `pilot_not_candidate_search`; no planned `IAF-P-YYYY` cell was run, and neither its smoke record nor aggregate may enter screening.

## Version-1.4 Inspec, Springer, and ProQuest source-addition pilots — 2026-08-10

**Status:** `pilot_not_candidate_search`; aggregate/interface validation only. No result was screened, admitted to the corpus, or used as evidence, and every accepted current route must run anew in clean version-1.6 storage.

| Source | Validated pilot boundary and controls | Aggregate result/status |
|---|---|---|
| Engineering Village | Compendex+Inspec simultaneously; All/Knovel clear; exact ten `C-*` strings; year/English clauses; autostemming off; Relevance; 100/page; no type filter; source deduplication off | all ten completed two identical ordered passes; `C-B1` = 119 (77 Compendex + 42 Inspec), `C-B2` = 94 (59 + 35); database-only comparators equaled the paired partitions |
| Springer Nature Link | full Link; unrestricted Keywords; English; 2011–2026; Relevance; 20/page; no content-type/brand/venue/access facet | `SN-B1` = 114 and `SN-B2` = 252; direct HTTP challenge was a failure, not zero; native-account CSV and final two-pass retrieval remain final-run gates |
| Advanced Technologies & Aerospace Index on ProQuest | only the exact Index selected; frozen `NOFT` B1/B2; year/English; Relevance; 20/page; no full-text/peer-review/type limiter; source deduplication off | `PQ-B1` = 32 and `PQ-B2` = 30; automatic spelling/form state and native RIS remain final-run preflight gates |

The private paired Engineering Village manifest has SHA-256 `9891d9987925579548cf097e05229bcaf8e0b3cd666202d28b68fbb950cd0f20`; the mixed-source tool smoke artifact has SHA-256 `73a15643ba3455c0348280f572d80cb777487b4c25cb9274bd5f099133506340`. Exact strings, source boundaries, failure rules, and remaining gates are frozen in [`query-search-plan.md`](query-search-plan.md). The historical Compendex-only entries below remain provenance for superseded diagnostics and do not replace the paired version-1.4 route.

## Prospective AIAA ARC source-addition pilots — 2026-08-10

**Status:** `pilot_not_candidate_search`; five read-only subagent jobs; no title, author, abstract, snippet, identifier value, URL, full text, relevance, eligibility, or prior corpus was inspected. AIAA Aerospace Research Central remained at <https://arc.aiaa.org/>. Direct non-browser HTTP received a Cloudflare-mitigated 403 in 0.034 seconds and was an access failure, not zero. The normal browser Advanced Search **Anywhere**/`AllField` route accepted uppercase Boolean, phrases, parentheses, and trailing wildcards with January 2011–August 2026, All content, Relevance, and no language/type/venue/OA restriction.

| Pilot | Disposition | Aggregate result | Speed/page observation |
|---|---|---:|---|
| `P-ARC-B1` | accepted count state | 308 | 16 pages at 20; form-dispatch time not accepted as end-to-end evidence |
| `P-ARC-B2` | accepted count state | 820 | 41 pages at 20; form-dispatch time not accepted as end-to-end evidence |
| `P-ARC-A1` | accepted count state | 108 | direct GET count-ready in 7.750 s |
| `P-ARC-A2-finite-100` | failed, not zero | null | hard timeout at 20.002 s |
| `P-ARC-A1-finite-page-benchmark` | count states accepted | 108 | 20/50/100 count-ready in 3.649/5.117/5.948 s; larger sizes rendered partial/lazy rows |
| `P-ARC-A2-finite-20` | count state accepted; row-hydration preflight still required | 699 | 4.413 s; provisional row selector returned 15/20 |

Twenty records/page was the fastest measured count route and is the planned enumeration size. A final page is acceptable only after the exact expected stable row/DOI-selector count renders; 50/100 remain prohibited unless a later logged contract proves complete hydration. ARC's month control over-includes through month-end, so final runs preserve the source total and apply/log an exact-day cutoff. The original pilots did not validate export or complete ordered pagination; the later off-topic adapter gates below validated the per-record RIS and complete multi-page mechanics, not any final `ARC-*` discovery run. Full methods and failure boundaries are in [`2026-08-10-aiaa-arc-source-addition-pilots.md`](searches/subagent-logs/2026-08-10-aiaa-arc-source-addition-pilots.md). The Git-ignored 20-file subagent archive manifest has SHA-256 `c1449a468949a3ab4c35d0f072170207c5370a48d09f945b3a24e5d6d600252b`. All eleven current `ARC-*` queries, including ARC-A3 and revised V1/O1, must run anew under version-1.6 authorization in clean final storage.

After the user confirmed the visible Cloudflare state had cleared, a separate `adapter_live_test_not_candidate_search` used the deliberately off-topic calibration query `"hypersonic boundary layer transition"`; no `ARC-*` strategy ran, and no calibration record was assessed for relevance/eligibility or admitted to the corpus. The first navigation briefly showed the managed challenge and then resolved in the authorized browser session without a retry navigation. Count-only mode reconciled total 856, 20/20 visible rows/DOIs, visible page size 20, visible Relevance, and two ordered first-page passes.

The live interface showed that result-page **Export Citations** posts to `/action/exportCiteProcCitation` but offers only IEEE/ACM/APA/Chicago/MLA/Harvard formatted text; its 154-byte download was `.txt`, not RIS (SHA-256 `625de557bacaf43ee17ae62ffadc2202d7adb1cd10be44ec89c742ebfe5f7404`). The source-native bibliographic route is per record: visible **Tools → Download citation**, exact `/action/showCitFormats?doi=...`, then a POST to `/action/downloadCitation` with `include=abs`, RIS, and checked Direct import. The validated response remained `https://arc.aiaa.org`, status 200, `application/x-research-info-systems;charset=UTF-8`, attachment disposition, and no redirect. One preflight plus 20 distinct first-page downloads were strict UTF-8, exactly one `TY`/`ER` record each, and DOI-reconciled; the bounded adapter run retained one normalized result by limit, remained explicitly partial, completed two search-page passes, and passed a 1/1 `aiaa_arc` merge smoke test. This calibration necessarily parsed off-topic RIS mechanically but performed no screening or candidate creation.

A subsequent complete-mode gate restricted the same off-topic phrase to 2011, for a source total of 44. The first attempt correctly wrote total `null` when the newly opened Tools menu had not yet hydrated; the adapter was changed to poll that visible controlled menu without fixed sleeps. A clean `--require-complete` rerun then reconciled all 44 records over three pages, two identical ordered search passes (six observed result pages), visible Relevance and page size 20, contiguous ranks 1–44, 45 strict single-record native RIS files including the duplicate preflight, and a 44/44/0-removed `aiaa_arc` merge in 47 seconds. All 44 rows exposed exactly one DOI. A synthetic DOI-less-row regression now requires a fail-closed total `null` rather than silent discard. A broader planned 856-row/two-pass identifier census encountered a visible challenge at zero-based `startPage=11`, stopped without retry, and remains an access failure—not evidence that every ARC row has a DOI.

A separate read-only audit examined the full plan (1,065 lines at audit time) and found no material AIAA source/strategy defect; it identified the then-unsynchronized seven-source language in `protocol.md`, which is resolved by the authorized version-1.4 amendment. At the version-1.4 gate, `search_strategy_lint.py` checked 60 covered queries and treated IAF as blocked. Version 1.5 then checked 88 blocks across eight direct families. Version 1.6 supersedes both operational scopes: the current linter checks 99 physical plus 11 PQDT-aliased blocks (110 logical blocks), nine source-native code-block families plus the normative PQDT source-event family, PQDT/OATD/IAF/source-count contracts, NTRS 940-cell arithmetic, and all 13 `search_*.py` source scripts.

The updated adapter `~/agent-tools/academic-research/skills/academic-search/scripts/search_aiaa_arc.py` has SHA-256 `a9179b9d0d47834210b7aad9bbf3991119bd6c9ac0a8f7b01d0e6a8d402c0ed9`; all 29 offline regressions pass. The Git-ignored live-test archive has manifest SHA-256 `1460367fc92421014c110ed2c3bfc89801f998503c2469d1d4e6c659210f4ea6`; the complete gate's nested manifest is `2161085b25bb4859b7e883cdb9b58f48c6a876063ba983a6053b605293e5b31d`. Complete multi-page adapter mechanics are closed. A live fallback remains conditional on actually encountering a DOI-less row; every final `ARC-*` cell still requires clean version-1.6 storage and a fresh per-cell preflight.

## Prospective version-1.3 amendment pilots — 2026-08-10

**Status:** `pilot_not_candidate_search`; model-assisted, not a human information-specialist assessment; no screening, candidate creation, evidence use, or inspection of titles, abstracts, bibliographic metadata content, URLs, full text, prior corpora, Buruso material, or Git history. Source IDs were immediately one-way hashed or kept opaque. Every accepted final strategy must run anew after authorization in clean final-run storage; pilot zeros, overlap, or yield cannot replace a final cell/query.

The amendment adds nested RQ1-G and explicit artifact-lineage grading (`NA`, `G0`–`G4`) under non-compensatory A/E/C/T/P/I gates. Search-design adjudication rejected unsplit `P AND G AND R_ALL`: an architecture-bearing artifact could supply its own relation token, while an R gate could suppress sparse metadata. Final Stream B preserves bibliographic core `B1∪B2` (high-specificity `P∧M` plus broad-model `P∧M∧R`) and local ESA/NTRS core `P∧M`, then adds separately provenance-coded relation-free G1/G2, conservative C1, and model-coupled T2 partitions; R is an optional independent tag for exact G/C1 expansions. Stream A remains `P AND E AND M`, and retrieval through an expansion is not evidence of genericity or tailoring. See [`2026-08-10-genericity-search-design-adjudication.md`](searches/subagent-logs/2026-08-10-genericity-search-design-adjudication.md) and the resolved [`2026-08-10-v1.3-final-consistency-audit.md`](searches/subagent-logs/2026-08-10-v1.3-final-consistency-audit.md).

### API-source opaque-set pilots

All successful API routes used complete retrieval, unique stable IDs, strict source-total reconciliation, two identical ordered passes, English/2011–2026/no-type controls, and a mechanical exact-day cutoff where the source exposed dates.

| Source/partition | Pilot total | Opaque IDs outside fresh B1∪B2 | Exact-day/control note |
|---|---:|---:|---|
| Scopus relation-free G1 | 5 | 4 | all current-day accepted |
| Scopus relation-free G2 | 8 | 6 | all current-day accepted |
| Scopus C1 | 24 | 7 | all current-day accepted |
| Scopus T2 | 26 | 2 | all current-day accepted |
| IEEE relation-free G1 | 0 | 0 | valid two-pass zero |
| IEEE relation-free G2 | 7 raw | 6 confirmed-current-day | 1 unresolved date |
| IEEE C1 | 22 raw | 6 confirmed-current-day | 21 confirmed, 1 unresolved |
| IEEE T2 | 22 raw | 6 confirmed-current-day | 19 confirmed, 3 unresolved |

The rejected initial unsplit relation-gated G query nevertheless reconciled 12/12 twice in Scopus (9 additions) and 7/7 twice in IEEE (6 confirmed-date additions; one unresolved). A corrected architecture-safe split also reconciled but is retained only as an optional precision fallback. A combined exploratory X1 failed component-union equivalence and is superseded. Details: [`2026-08-10-genericity-api-search-pilot.md`](searches/subagent-logs/2026-08-10-genericity-api-search-pilot.md) and [`2026-08-10-genericity-api-refinement-pilot.md`](searches/subagent-logs/2026-08-10-genericity-api-refinement-pilot.md).

### Browser-source opaque-set pilots

| Source | Relation-free G1/G2 | G union outside fresh B1∪B2 | C1/T2 disposition |
|---|---:|---:|---|
| Web of Science Core Collection | diagnostic 2/4 only | not accepted | English refinement unavailable; G/C1/T2 attempts retained as failures/provisional diagnostics |
| Compendex | reconciled 4/8 | 8 | C1/T2 access failures; not zeros |
| Wiley Online Library | reconciled 5/13 | 9 | C1 reconciled 32/32 with 6 additions; T2 changing-total/pagination failure |

The superseded relation-gated browser pilot had found 4/7/9 additions for WoS/Compendex/Wiley. Relation-free Compendex added one more opaque ID than its gated union; Wiley's unions were identical. These are workload/recall diagnostics only. The final plan retains all prospectively specified source partitions and requires normal control/reconciliation success or a reported final source failure. Details: [`2026-08-10-genericity-browser-search-pilots.md`](searches/subagent-logs/2026-08-10-genericity-browser-search-pilots.md).

### ESA/NTRS finite-route pilots

- **ESA Indico:** deterministic fixtures passed 19/19 concept cases and 13/13 metadata/individual-attachment route cases. A no-network relation-free rematch reused the preserved complete 2026-08-07 census only as a screening-prohibited method test: 8,584 subjects and 5,664 extracted attachment texts; core B 74; G 32; C1 15; G∩C1 6; complete expansion union 41; core∩expansion 26; expansion-only 15; total B 89; unchanged A 23 and structural A-only 0; E-explicit expansion 16; independent-R tag 41; T2 tag 55. Metadata/attachment total-B routes were 20/75 with overlap 6. These subjects are not candidates and cannot be reused; a fresh whole-instance census remains mandatory.
- **NTRS (historical version-1.4 design):** all 301/301 seven-form core/G cells reconciled (126 core + 175 G): core simple sum 39/opaque union 6; G simple sum/union 1; overlap 1; G-only 0. The omitted exact `"cube sat"` 43-cell follow-up was all zero. A separate seven-form C1 run reconciled 161/161 cells with valid zeros. A focused pilot reconciled all 198/198 then-remaining cells for three population forms against 18 M, 25 G, and 23 C1 atoms. That 660-cell design is superseded by version 1.5, which restores 28 C1 language-anchor combinations per population form: 940 mandatory cells (180 core + 250 G + 510 C1) plus deterministic E/T/V1/O1 tags. The added 280 C1 cells still require a no-screening pilot and every 940-cell final run must be fresh.

ESA/NTRS implementation, coverage, and checksums are reported in [`2026-08-10-genericity-esa-ntrs-pilots.md`](searches/subagent-logs/2026-08-10-genericity-esa-ntrs-pilots.md). The owner-restricted ignored amendment-pilot tree contains 1,679 files in its final manifest; `amendment-pilot-manifest.json` SHA-256 is `6478c4dd45733a3fa0624edba9bb203cc793faabc22b51fedd25de49d9a8b9a5`. No valid final discovery search has begun.

## Scopus interface diagnostics

- **Source/platform:** Scopus Search API, Elsevier; `https://api.elsevier.com/content/search/scopus`
- **Interface/view:** authenticated API, `COMPLETE`; API key omitted from all logs
- **Client:** `search_scopus.py`; SHA-256 `1c92dde7a62b43d8003767eb0b2c7c262d35ef12ac09da430da65b642def6d9d`
- **Original diagnostic limits (superseded for type):** `PUBYEAR AFT 2010`, `PUBYEAR BEF 2027`, `LANGUAGE(english)`, and `DOCTYPE(ar|cp|ch)`. PRESS revision removes `DOCTYPE` from discovery; the original restricted counts remain only as comparators.
- **Initial transport check:** an unauthenticated request returned HTTP 401 and was correctly treated as authentication failure, not zero results.

| Pilot ID | Time (EDT) | Exact strategy | Source total | Retrieved | Disposition |
|---|---:|---|---:|---:|---|
| `P-S-A1-count` | 19:37:48 | original pre-spelling-audit `S-A1` plus year clauses; exact query in raw artifact | 3 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-A2-count` | 19:37:50 | original pre-spelling-audit `S-A2` plus year clauses; exact query in raw artifact | 9 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-B1-count` | 19:37:41 | original pre-spelling-audit `S-B1` plus year clauses; exact query in raw artifact | 75 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-B2-count` | 19:37:52 | original pre-spelling-audit `S-B2` plus year clauses; exact query in raw artifact | 55 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-V1-count` | 19:37:53 | original pre-spelling-audit `S-V1` plus year clauses; exact query in raw artifact | 1 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-O1-count` | 19:37:55 | original pre-spelling-audit `S-O1` plus year clauses; exact query in raw artifact | 4 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-A1-full-check` | 19:38:04 | same as `P-S-A1-count` | 3 | 3 | total reconciled; normalized JSON passed merge test |

These are dynamic interface counts, not identification or inclusion counts.

## Web of Science Core Collection browser diagnostics

- **Source/platform:** Clarivate Web of Science, **Web of Science Core Collection**; <https://www.webofscience.com/wos/woscc/basic-search>
- **Interface:** normal browser Basic Document Search, one complete Boolean expression in the `Topic` field; Advanced Search was inspected as a documented fallback but was not substituted for the six Basic Search pilots
- **Browser report:** [`2026-08-07-wos-interface-validation.md`](searches/subagent-logs/2026-08-07-wos-interface-validation.md)
- **Original common settings (superseded for type):** Publication Date 2011-01-01 through 2026-08-06; Language `English`; Document Type `Article OR Book Chapter OR Proceedings Paper`; Relevance sort; observed page size 50. PRESS revision removes the Document Type restriction and reruns through 2026-08-07.
- **Database/edition state:** `Search in: Web of Science Core Collection`; `Editions: All`, with SCI-EXPANDED, SSCI, AHCI/A&HCI, CPCI-S, CPCI-SSH, BKCI-S, BKCI-SSH, ESCI, CCR-EXPANDED, and IC all visible and selected
- **Timing caveat:** live Search History displayed the exact query, controls, total, and time of day but not the calendar date. The six 21:29–21:32 EDT entries are dated 2026-08-06 from the preserved overnight session context; the history/export validation occurred 2026-08-07.

| Pilot ID | Time (EDT) | Exact strategy | Source total | Diagnostic handling | Disposition |
|---|---:|---|---:|---|---|
| `P-WS-A1` | 21:29 | pre-PRESS WS-A1 preserved in the dated browser report | 1 | one-record ordinary RIS export and merge preflight | syntax/controls/count accepted; strategy superseded |
| `P-WS-A2` | 21:30 | pre-PRESS WS-A2 preserved in the dated browser report | 0 | zero-result history entry | valid zero; strategy superseded |
| `P-WS-B1` | 21:31 | pre-PRESS WS-B1 preserved in the dated browser report | 43 | result page/count only | syntax/controls/count accepted; strategy superseded |
| `P-WS-B2` | 21:31 | pre-PRESS WS-B2 preserved in the dated browser report | 29 | result page/count only | syntax/controls/count accepted; strategy superseded |
| `P-WS-V1` | 21:32 | pre-PRESS WS-V1 preserved in the dated browser report | 1 | result page/count only | syntax/controls/count accepted; strategy superseded |
| `P-WS-O1` | 21:32 | pre-PRESS WS-O1 preserved in the dated browser report | 1 | result page/count only | syntax/controls/count accepted; strategy superseded |

Ordinary page-level **Export → RIS (other reference software)** succeeded without credentials on 2026-08-07. The dialog supported explicit record ranges of no more than 1,000 records per export. The validated one-record route used range 1–1 and Custom selection (30), including accession number, DOI, abstract, editions, and cited references; it produced one native RIS record with 31 `CR` tags. The untouched native RIS has SHA-256 `08008465e75f29fda995d58057ed8f818a442f598aa07aa9d2d172c2f0508263`. A separate earlier Full Record RIS has SHA-256 `c7cde3b602e50515b3f9c9caea803dc46a072ae2ff5306e0f4742dc585dede39`. Fast 5000 opened a Clarivate-login route in the prior session and is prohibited as the planned export path; this did not block ordinary RIS export.

`ris_to_merge_csv.py` converted the native RIS to the common one-row CSV schema while preserving exact query, global rank 1, source total 1, WoS accession in `Paper ID`, DOI, title, authors, year, and abstract (normalized CSV SHA-256 `2c5845d9a0b75bb18b0d58c31c24e6ccf46f703ca50b7af8f0d1f158c6a1c3a5`). A reproducible sidecar retained all 31 cited-reference strings (SHA-256 `fbd8f9807a82590b21e989b8b9bd2c0c9b092132f2d6296aedcf04b4d21791f1`). After adding explicit Web of Science aliases, `merge_search_results.py` canonicalized the source as `web_of_science_core_collection` and reconciled 1 raw/1 unique/0 removed (merged JSON SHA-256 `dd8ea3597ff593f51fc83ee945d74e7b4cadfa0193af7fa639e4cab21e3a5bc8`). The post-fix merger SHA-256 is `fcf0168dd25480dc882de6e53c505fb47eebc3839d772bd96fdfc1b1c921dde4`; all seven offline regression tests passed.

All WoS counts, records, and exports above are dynamic interface diagnostics, not identification, screening, or inclusion evidence. Rerun the six core/sensitivity Topic strategies, all version-1.3-defined expansions retained by version 1.4, and the export/merge preflight in the final run.

## IEEE Xplore interface diagnostics

- **Source/platform:** IEEE Xplore; `https://ieeexplore.ieee.org/rest/search`
- **Count-pilot client:** `search_ieee_xplore.py`; SHA-256 `eee08f82ab70620c70f06d09090208ece811bb9b801e6420c55b864074e0a3e9`
- **CSV-provenance revision:** SHA-256 `7d09758723b759f03d5db95264bfce4c749f43022dd6b2d9c51a1d0be033ab77`; a second complete I-A1 diagnostic still returned/reconciled 4 and its CSV preserved source, exact query, rank, and source total through the merge test
- **Original diagnostic limits (superseded for type):** years 2011–2026; content types `Journals`, `Conferences`, `Books`; language `English`. PRESS revision retains years/language but omits every Content Type refinement.
- **Initial transport check:** a bare curl POST returned HTTP 418 and was treated as an access/challenge response, not zero results. The client used its validated request behavior successfully.

| Pilot ID | Time (UTC) | Exact strategy | Source total | Retrieved | Disposition |
|---|---:|---|---:|---:|---|
| `P-I-A1-count` | 23:36:41 | original pre-spelling-audit `I-A1`; exact query in raw artifact | 4 | count-only | syntax/facets accepted; superseded P block |
| `P-I-A2-count` | 23:36:44 | original pre-spelling-audit `I-A2`; exact query in raw artifact | 2 | count-only | syntax/facets accepted; superseded P block |
| `P-I-B1-count` | 23:36:24 | original pre-spelling-audit `I-B1`; exact query in raw artifact | 38 | count-only | syntax/facets accepted; superseded P block |
| `P-I-B2-count` | 23:36:45 | original pre-spelling-audit `I-B2`; exact query in raw artifact | 42 | count-only | syntax/facets accepted; superseded P block |
| `P-I-V1-count` | 23:36:49 | original pre-spelling-audit `I-V1`; exact query in raw artifact | 1 | count-only | syntax/facets accepted; superseded P block |
| `P-I-O1-count` | 23:36:51 | original pre-spelling-audit `I-O1`; exact query in raw artifact | 4 | count-only | syntax/facets accepted; superseded P block |
| `P-I-A1-full-check` | 23:37:11 | same as `P-I-A1-count` | 4 | 4 | total reconciled; normalized JSON and CSV each passed merge test |

Count-only runs deliberately discarded the one response record. These are dynamic interface counts, not identification or inclusion counts.

## Scopus and IEEE Xplore multi-page API validation

**Status:** completed `pilot_not_candidate_search`; no record was screened, retained as a candidate, or used as evidence. The full reproducibility report is [`2026-08-07-scopus-ieee-multipage-api-validation.md`](searches/subagent-logs/2026-08-07-scopus-ieee-multipage-api-validation.md); non-secret request templates and the reusable reconciler are [`searches/api-pagination-request-templates.json`](searches/api-pagination-request-templates.json) and [`searches/tools/api_pagination_reconcile.py`](searches/tools/api_pagination_reconcile.py).

| Pilot | Run (EDT) | Observed native pagination/order | Source total; retrieved in pass 1/pass 2 | Reconciliation and merge preflight |
|---|---|---|---:|---|
| `P-S-B1-multipage-historical-type-filter` | 10:49:48–10:49:57 | Scopus `count=25`, zero-based `start=0,25,50,75`; `COMPLETE`; `sort=eid`; 25/25/25/5 records; historical `DOCTYPE` clause | 80; 80/80 | all four `startIndex` values matched; 80 unique EIDs; no duplicate/missing page; ordered passes identical; 80 raw/80 unique merge; request superseded for type |
| `P-I-B2-multipage-historical-type-filter` | 10:49:48–10:49:54 | IEEE `rowsPerPage=25`, one-based `pageNumber=1,2`; `sortType=newest`; 25/17 records; historical ContentType facets | 42; 42/42 | 42 unique articleNumbers; no duplicate/missing page; ordered passes identical; 42 raw/42 unique merge; request superseded for type |
| `P-S-B1-multipage-PRESS-unrestricted` | 11:27:45–11:27:56 | corrected final S-B1; no `DOCTYPE`; `start=0,25,50,75`; 25/25/25/10 records | 85; 85/85 | 85 unique EIDs; two ordered passes identical; no retry/missing/duplicate page or ID; 85 raw/84 bibliographically unique merge |
| `P-I-B2-multipage-PRESS-unrestricted` | 11:27:45–11:27:53 | corrected final I-B2; sole facet `Language:English`; `pageNumber=1,2`; 25/22 records | 47; 47/47 | 47 unique article numbers; two ordered passes identical; no retry/missing/duplicate page or ID; 47 raw/47 unique merge |

The delegated historical pilots used the then-current type filters. After MAJOR-01/02/07 corrections, the same audited driver completed fresh broad pilots with spaced-plural/crossed-model variants and no publication/content-type filter; exact prospective request shapes and both generations of pilot descriptors are separated in `api-pagination-request-templates.json`. Both used a 30-second timeout, three retries after the initial attempt for network/408/425/429/5xx failures, `Retry-After` or capped exponential backoff, one permitted clean restart after a changed total, and a hard failure unless all expected pages, unique ordered IDs, matching two-pass order, and `retrieved == source total` hold. Redirect, access/challenge, non-JSON, offset, short-page, duplicate-page/ID, or repeated-total-change conditions are failures, not zero results or partial candidates. The driver strips credential-like fields and IEEE `userInfo`; credentials/cookies/tokens were not written.

At the close of the version-1.2 pilot, the template SHA-256 was `15087ec37cf4c510fae78583df248c28703a3257365e8e1dea6d73cd4b48a66a` and the driver SHA-256 was `be9fd8a5202ddb8ef5fec96855d119d840a8c9fbcbbb1f8393836df594d6801e`; these historical values do not describe the version-1.3 files. Corrected broad-pilot manifests are `e89596345c9da44c09807b71ba205dd6a350e7de515251b443fdaad045c0a3f9` (Scopus) and `1d475b5e8fd562459c011fc8fc678f8d374b9dc87435b6c50e1a0e0b8b998934` (IEEE). Rerun every final query post-authorization in a clean final-run directory; these pilot records remain superseded and are never candidates.

## PRESS-corrected Scopus and IEEE syntax/count pilots

**Run:** 2026-08-07 11:13–11:28 EDT; all outputs are `pilot_not_candidate_search`. The exact final strings are the displayed blocks in `query-search-plan.md`. No record was screened or retained.

| Source | A1 | A2 | B1 | B2 | V1 | O1 | Final B1 versus old type-restricted B1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Scopus `COMPLETE` | 3 | 10 | 85 | 68 | 1 | 4 | 85 versus 80 (+5) |
| IEEE Xplore | 4 | 6 | 39 | 47 | 1 | 4 | 39 versus 38 (+1) |

Scopus queries retained `LANGUAGE(english)` and explicit `PUBYEAR AFT 2010 AND PUBYEAR BEF 2027` but no `DOCTYPE`; IEEE retained years 2011–2026 and `Language:English` but no ContentType facet. A matched B1 population comparison found no displayed-count change from adding `"nano satellites"` in Scopus (85→85) or adding standalone `nanosat` plus `"nano satellites"` in IEEE (39→39); equal counts do not prove set identity. Both APIs expose no separate automatic stemming/lemmatization request parameter in the frozen route, so no equivalence is inferred and all explicit variants remain.

IEEE's academic client retrieved the complete unrestricted I-B2 set in two pages (25/22; 47/47) and its merge smoke test reconciled 47 raw/47 unique. The generic Scopus academic client reached the source but failed normalization on a null author given-name; this is a client error, not a source failure or zero. The audited reconciler safely handled that value and completed the corrected unrestricted Scopus two-pass 85/85 preflight recorded above. Both source controls include the rest of 2026, so final execution preserves the source total and separately logs records removed after the exact run-day first-formal-publication cutoff.

## ESA Indico interface diagnostics

- **Source/interface:** full public ESA Indico instance; `https://indico.esa.int/export/categ/0.json`
- **Root run:** 2026-08-06 19:23:31 EDT; HTTP 200; 2,512,942 bytes; SHA-256 `cd981bbfbd5e9fac036f790805bb6ea5a0dfab3a77d9b09d063e6262cad30312`
- **Observed root total:** 437 unique events. The root event-ID set exactly equaled the union of child exports 5, 6, and 7; category 9 was a subset of category 6. Child counts were 3, 377, 57, and 1 respectively.
- **Date check:** all 437 root events had parseable start dates; 408 fell from 2011-01-01 through 2026-08-06.
- **Coverage IDs:** 161, 329, 386, 407, and 472 were all present.
- **Contribution-shape checks:** each tested `export/event/{id}.json?detail=contributions` request returned HTTP 200 and one event in `results[0]`; contribution counts must be read from `results[0].contributions`, not top-level `count`. Diagnostic nested counts for the five coverage events were 15, 35, 46, 62, and 15.

This validates the original census and response shape only. The full root/child comparison and all in-window contribution exports must be rerun after authorization.

### PRESS-corrected attachment-first dry run

A complete `pilot_not_candidate_search` ran 2026-08-07 11:05:23–12:11:29 EDT with the frozen dictionary/matcher/fixtures and no metadata gate. It retrieved all 408/408 in-window event exports and parsed 8,394 contributions. Before matching, it inventoried 6,770 material associations and attempted all 5,690 unique document-like URLs: 5,686 retrieved, 5,664 text-parsed, four retrieval failures, and 22 unparseable/no-text coverage failures.

The first matcher pass revealed that event-level attachment text was being inherited by every contribution at the event; those inflated route counts are superseded and were never screened. After correcting the prospective harvester and re-matching the same complete saved census with zero network requests, joined metadata yielded 17 Stream-B subjects; attachment text yielded 62; five overlapped; the union was 74, including **57 attachment-only** subjects. The EPS-explicit tag reconciled as `A∩B=23`, `B-only=51`, and `A-only=0`. These are aggregate matcher diagnostics only and no item was screened or retained. Root IDs again equaled category 5∪6∪7, category 9 remained a subset of 6, and all five known coverage IDs were present.

- Dictionary SHA-256 `1b2416c22840bd780d9b47f3ff81c6fd6466f13d52ee9d2ca7b429161a4232ab`
- Matcher SHA-256 `895d7e8fb333d1ce684cda02e6ca795f6fbc29ee70a16cc894c5d8eaaa0203eb`; fixtures 10/10 passed
- Corrected harvester SHA-256 `78ff39c67371b4948bbae14b9cdbdf2b9b92f54bcd67858a8c35b5ef41e04d2b`; no-network rematcher SHA-256 `ff2d71659089b18c935c636c6ce09bd3b5ae5c6887c247b2dc864e01ff1ada39`
- Corrected rematch output SHA-256 `8d54a4e17f6e2c8e2922ef8a4beae29f87838c664e4e581a55036ba2ea7173b4`
- Active private retained-artifact manifest SHA-256 `ae1aba9681d63237ae33b0896cefb94787c24bc4086aeb40d8fe501ecde3f8e8`
- Detailed report: [`2026-08-07-esa-attachment-first-validation.md`](searches/subagent-logs/2026-08-07-esa-attachment-first-validation.md)

Downloaded pilot binaries were purged after text/checksum derivation for storage/rights minimization; per-attachment status and SHA-256 remain private. The complete final census/match must be rerun after authorization and this pilot union cannot become candidates.

## NASA NTRS interface diagnostics

- **Source/UI:** `https://ntrs.nasa.gov/search`
- **Endpoint:** `POST https://ntrs.nasa.gov/api/citations/search`
- **Common body controls:** `published.gte=2011-01-01`, `published.lte=2026-08-06`, `page.size` as shown, zero-based `page.from`
- **Normalized-client check:** `search_ntrs.py` SHA-256 `b2a51f682fecd5acf19dc8730fb636cdaba3957372f331ead67ae96b0a115f4d` retrieved/reconciled all 4 records for diagnostic `CubeSat MBSE`; its JSON passed `merge_search_results.py`

| Pilot ID | Exact `q` | Total | Observation |
|---|---|---:|---|
| `P-N-T01` | `CubeSat MBSE` | 4 | simple spaces accepted |
| `P-N-T02` | `CubeSat AND MBSE` | 4 | same complete ID set as T01, different order |
| `P-N-T03` | `CubeSat OR MBSE` | 0 | Boolean OR unreliable; prohibit |
| `P-N-T04` | `(CubeSat OR nanosatellite) AND MBSE` | 0 | grouped Boolean unreliable; prohibit |
| `P-N-T05` | `CubeSat "model-based systems engineering"` | 2 | phrase quoting materially restrictive |
| `P-N-T06` | `CubeSat model-based systems engineering` | 7 | unquoted words differ from exact phrase |
| `P-N-T07` | `CubeSat SysML` | 0 | valid zero-result diagnostic |
| `P-N-T08` | `nanosatellite "electrical power system" MBSE` | 0 | valid zero-result diagnostic |
| `P-N-T09` | `"nano-satellite" "system model"` | 0 | valid zero-result diagnostic |

Further controls confirmed `page.size=100`; two `CubeSat` pages at `from=0` and `from=5` returned nonoverlapping five-record samples with stable total 841. The publication-date filter changed the broad `CubeSat` total from 857 (1900 start) to 841 (2011 start) and 161 (2020 start). Final cells therefore use only spaces and quoted phrases, fixed pages of 100, no Boolean operators/parentheses, and complete reconciliation to `stats.total`.

## NTRS PRESS-corrected matrix validation

- **Run:** 2026-08-07 11:24:17–11:30:15 EDT; `pilot_not_candidate_search`; no screening, full-text retrieval, candidate classification, or evidence use
- **Historical version-1.2 specification (superseded):** six exact P terms × eighteen exact M terms = **108 P×M cells**; no Boolean operators, parentheses, fields, or wildcards
- **Date/page body:** `published.gte=2011-01-01`, `published.lte=2026-08-07`, `page.size=100`, zero-based `page.from`
- **Completion:** 108 attempted / 108 HTTP-200 complete / 0 failed; 108 pages reopened and reconciled; 0 retries or total changes
- **Aggregate diagnostic only:** simple overlapping sum 39/39; six unique NTRS IDs; no record screened
- **Normal UI:** representative `CubeSat MBSE`, `nanosat MBSE`, `"nano satellites" "systems modeling language"`, and `CubeSat "object-oriented systems model"` forms were accepted; UI totals are not equated to date-limited API totals
- **Full-E local tag:** dictionary 25/25 E forms and fixtures 10/10 passed; over the six-ID metadata union, `A∩B=1`, `B-only=5`, `A-only=0`, union=6. A is a structural tag, not an additional discovery stream.
- **Artifacts:** detailed report [`2026-08-07-ntrs-revised-matrix-validation.md`](searches/subagent-logs/2026-08-07-ntrs-revised-matrix-validation.md); private 458-entry raw manifest SHA-256 `6a39421df2e5797e47b3b34e67be71330afd7ebf851c02d88862c228a89b1a9a`

The prior 136-cell design and selected nine-term E_N matrix were superseded by this version-1.2 pilot; versions 1.3 and 1.4 successively superseded the 108-cell design. Version 1.6 retains all 940 P×M/G/C1 cells, deduplication across partitions, and frozen E/T/V1/O1 tagging as specified above and in the query plan.

## Wiley Online Library browser diagnostics

- **Source/platform:** full Wiley Online Library; <https://onlinelibrary.wiley.com/search/advanced>
- **Endpoint:** `https://onlinelibrary.wiley.com/action/doSearch`
- **Browser reports:** [`2026-08-06-wiley-interface-validation.md`](searches/subagent-logs/2026-08-06-wiley-interface-validation.md) and [`2026-08-06-wiley-export-followup.md`](searches/subagent-logs/2026-08-06-wiley-export-followup.md)
- **Observed field:** `Anywhere` / `AllField`; exact uppercase Boolean, groups, phrases, and non-leading wildcards accepted
- **Date controls:** January 2011 through August 2026; source normalizes through month-end, requiring report-level run-date screening

| Pilot ID | Time (EDT) | Exact strategy | Articles & Chapters | Collections | Disposition |
|---|---:|---|---:|---:|---|
| `P-W-A1` | 19:25:08 | original pre-spelling-audit `W-A1`; exact query in browser report | 7 | not recorded | accepted; superseded P block |
| `P-W-A2` | 20:23:50 | original pre-spelling-audit `W-A2`; exact query in browser report | 40 | 2 | accepted; superseded P block |
| `P-W-B1` | 19:27:59–19:28:20 | original pre-spelling-audit `W-B1`; exact query in browser report | 44 | 1 | accepted; three pages; superseded P block |
| `P-W-B2` | 20:24:21 | original pre-spelling-audit `W-B2`; exact query in browser report | 105 | 4 | accepted; superseded P block |
| `P-W-V1` | 19:33:32–19:33:52 | original pre-spelling-audit `W-V1`; exact query in browser report | 17 | 1 | accepted at 690 characters; superseded P block |
| `P-W-O1` | 19:34:23–19:34:43 | original pre-spelling-audit `W-O1`; exact query in browser report | 21 | 1 | accepted; superseded P block |

Pagination is 20 records with zero-based `startPage`. Export is page-scoped; 20 was a tested-safe selection size. Wiley exposed RIS and other citation formats but no native CSV. A normal one-record W-A1 RIS export with abstracts succeeded (SHA-256 `159debf96aeaa0768f578e4cdbee5b804c2342dd2abe8747668337b937f103e9`) and contained one `N2` abstract. `ris_to_merge_csv.py` (SHA-256 `9099bff33f49f4ac27b91ae0ea711825b01d81cd139aed1be9c1682ab98575c1`) produced a 1-row normalized CSV, and `merge_search_results.py` (SHA-256 `ea1098e54f176aae98e75da7f1b4174b5ad138ccbbdd555360c64831e57e6cd4`) preserved Wiley source, exact query, source total, global rank, and 1/1 raw/unique counts. Repeat this export/merge preflight after authorization and never label normalized CSV as native Wiley output.

## Historical pre-version-1.4 Compendex-only/Engineering Village browser diagnostics

- **Source/platform:** Compendex-only on Elsevier Engineering Village Expert Search; this section is superseded by the paired Compendex+Inspec version-1.4 route; <https://www.engineeringvillage.com/search/expert.url?database=1>
- **Browser reports:** [`2026-08-06-compendex-interface-validation.md`](searches/subagent-logs/2026-08-06-compendex-interface-validation.md) and [`2026-08-06-compendex-export-followup.md`](searches/subagent-logs/2026-08-06-compendex-export-followup.md)
- **Validated fields/syntax:** `KY` Subject/Title/Abstract, `YR`, `LA`, uppercase Boolean, parentheses, quoted phrases, and explicit wildcards; Compendex-only selected in the UI
- **Historical final-setting diagnostic:** C-B1 with `AND (2011-* WN YR) AND (({English}) WN LA)`, Relevance, 100/page, autostemming off, no document-type or `WN DB` clause returned 72 at 2026-08-06 20:12:09 EDT. The server summary retained a broad `1884–2026` coverage label; the version-1.6 paired final run must set the UI Published range, retain the literal year clause, and audit exported years in both databases.

Earlier syntax pilots with autostemming on and `JA|CA|CP|CH` returned C-A1 = 3, C-A2 = 4, C-B1 = 68, C-B2 = 42, C-V1 = 1, and C-O1 = 1. Those settings were superseded by the higher-recall plan and the counts are not identification counts.

A normal one-record CSV Detailed export succeeded after setting Chrome's download behavior. The untouched 29-column native file had SHA-256 `bd5e879e4d13841a7c8a877b8d64d93eebfde628d3ef77ea5af6d22f5145775f`; it omitted exact query and rank. A normalized CSV (SHA-256 `99108152649565600f4794c495ea358549b3845a12f2118aeb83024d1c73c7de`) added common provenance and passed `merge_search_results.py`, preserving Compendex source, exact query, rank 1, and 1/1 raw/unique counts. Pilot record metadata is not retained in the review workspace; the export/normalization preflight must be repeated through the paired Compendex+Inspec route in clean version-1.6 storage.

## Population-spelling pre-freeze audit

Two detailed reports preserve the 2026-08-07 audit: [`2026-08-07-population-term-audit.md`](searches/subagent-logs/2026-08-07-population-term-audit.md) for browser sources and [`2026-08-07-api-population-term-audit.md`](searches/subagent-logs/2026-08-07-api-population-term-audit.md) for IEEE/NTRS and the initial-failure/successful-retry Scopus API checks. No record was screened, exported from the browser sources, retained as a candidate, or used as evidence.

- **Compendex:** under matched final controls with autostemming off, original C-B1 = 72 and revised C-B1 = 76 (+4). Revised C-V1 = 1 and C-O1 = 1. The revised block explicitly adds `cubesats` and `"nano-satellites"` and supersedes the original P block.
- **Wiley:** original versus revised W-B1 remained 44 Articles & Chapters and 1 Collection; revised W-V1 = 17 plus 1 Collection and W-O1 = 21 plus 1 Collection. The added phrase was accepted; equal totals do not establish set equivalence.
- **Scopus:** under matched normal-web-UI controls, original S-B1 = 75 and revised S-B1 = 80 (+5). The initial API recheck failed authentication; empty shells written with `total: 0` are invalid and are not source results. After institutional network access became available, the `COMPLETE`-view API retry successfully reproduced 75 and 80. Final Scopus execution still requires a fresh post-authorization authentication preflight.
- **IEEE Xplore:** original and revised I-B1 both returned 38; revised I-V1 = 1 and I-O1 = 4. The complete revised population block was accepted; equal totals do not establish set equivalence.
- **NTRS (superseded matrix decision):** the first 56-cell diagnostic tested eight population spellings against seven then-planned `M_N` terms and found source-unique yield for `CubeSats`. PRESS review subsequently identified omitted frozen P/M terms. The 136-cell P/E/M design was retired; the then-corrected version-1.2 baseline was 108 complete P×M cells (six P × eighteen M), followed by a full-E local tag. Version 1.3 subsequently retained all ten source-representable P forms and added G/C1; version 1.4 retained a 660-cell design, which version 1.5 supersedes with the complete 940-cell matrix.

Those population-audit expressions were later superseded by the PRESS corrections adding bare IEEE `nanosat`, spaced plural `"nano satellites"` everywhere, and the complete NTRS P/M matrix. The exact corrected implementations and fresh pilots are logged below; every strategy must still be rerun after authorization.

## PRESS-corrected browser-source pilots

**Runs:** 2026-08-07 11:21–12:19 EDT; all are `pilot_not_candidate_search`. Exact strings were byte-for-byte extracted from the final WS/C/W blocks. No record was screened, retained, or used as evidence.

| Source | A1 | A2 | B1 | B2 | V1 | O1 |
|---|---:|---:|---:|---:|---:|---:|
| WoS Core Collection | 1 | 0 | 43 | 34 | 1 | 1 |
| Compendex | 3 | 6 | 76 | 58 | 1 | 1 |
| Wiley Articles & Chapters | 7 | 46 | 44 | 103 | 17 | 21 |
| Wiley Collections | unresolved/not zero | 2 | 1 | 4 | 1 | 1 |

**WoS controls:** Basic/Topic; Core Collection; Editions All with all ten available indexes; Publication Date 2011-01-01–2026-08-07; English; no Document Type; Relevance and 50/page where results existed. The clean WS-A2 execution displayed `Your search found no results`, validating zero after two earlier navigation failures. Final unrestricted WS-B1 and the old three-type-restricted comparator both returned 43; no equivalence is inferred. Final B1 versus removal only of `"nano satellites"` was also 43→43. Advanced `Exact search` was observed unchanged at `aria-checked=false`; no stemming/lemmatization meaning was inferred. A fresh ordinary non-Fast-5000 unrestricted WS-B1 RIS range 1–1 completed (391 bytes; SHA-256 `cc7bf2061a2f9181d25a86008a1182da46c132f51b6aec83cf30103fe378de75`).

**Compendex controls:** Compendex only; Published 2011–Latest plus the literal `YR`/English suffix; autostemming OFF; Relevance; 100/page; no type filter. Final B1 versus removal only of `"nano satellites"` was 76→76. C-B1/B2 fit one page. Preserve the source total and apply the exact run-day publication cutoff after export.

**Wiley controls:** whole platform; one AllField row; January 2011–August 2026; no type/language/venue/OA facet. Final B1 versus removal only of `"nano satellites"` remained 44 Articles & Chapters and one Collection. W-B2 reconciled page 6 with three cards at 20/page against 103. The source rendered sort `Date`; final execution records the actual declared sort and separately removes records after the exact run day because the source range extends through month-end.

Detailed report: [`2026-08-07-press-browser-source-validation.md`](searches/subagent-logs/2026-08-07-press-browser-source-validation.md). Private manifests: `5c98bffe52e4aaa46ea15437aad538fa9dbcf0414c0a29c8eb9d77a714f086e5` (27-file main browser pilot) and `0e516843d2e40bf4aae949e94f641de442613f79cd08c6577c483a5f03f7c3bc` (16-file WoS follow-up).

## Prospective citation-chasing platform decision

**Decision date:** 2026-08-07, before freeze and before any valid citation search. No citation-chasing event was executed for this decision.

- Backward chasing will inspect each seed report's complete full-text reference list; indexed reference exports are aids, not substitutes.
- Forward chasing will search **both Scopus and Web of Science Core Collection** for every included report and relevant secondary-review seed. Scopus uses its normal record/`Cited by` interface; WoSCC uses `Citing Articles` and Cited Reference Search with all available Core Collection editions.
- If a seed is not indexed, use DOI/title/cited-reference searching where the platform supports it and log the exact route. A zero result or failure in one platform never waives the other.
- Log seed, direction, platform, exact route, cycle, dates, source/retrieved totals, candidates, duplicates, decisions, failures, and stopping result. Retain `discovery_route=citation_chasing` separately from bibliographic source.
- Newly included reports become next-cycle seeds. Stop only after a complete backward and dual-platform forward cycle yields no new eligible report. Google Scholar and Semantic Scholar are not fallback citation indexes.

## Version-1.6 supervised open-gate run — 2026-08-11

**Status:** `pilot_not_candidate_search`; **not ready for final discovery**. No pilot record, native export, normalized output, source ID, merge product, or aggregate from this run may enter candidate generation, screening, synthesis, PRISMA counts, or final-run input. PQDT/OATD source operations were outside this supervised run.

The authoritative report is [`2026-08-11-v1.6-open-gate-supervision.md`](searches/subagent-logs/2026-08-11-v1.6-open-gate-supervision.md); owner-only evidence is under `.searches/eps-mbse-slr-2026/open-gate-pilots/2026-08-11-supervised/`.

| Outcome | Gates | Current result |
|---|---|---|
| Accepted bounded/current diagnostic | `V16-S`, `V16-WS`, `V16-I`, `V16-IAF-01`, `V16-IAF-02`, `V16-ESA-02`, `V16-NTRS-01` | Current method contracts passed; every source must still be rerun in clean final storage. |
| Partial/open | `V16-G03`, `V16-PQ` | Final adapters/immutable promotion remain incomplete; Aerospace Index native RIS/merge remains open. |
| Failed closed | `V16-C`, `V16-W`, `V16-SN`, `V16-ARC` | Totals are `null`, never zero; no partial prefix was imported. |

Safe aggregate mechanics: Scopus 85 in each of two four-page passes (merge 85→84); IEEE 47 in each of two two-page passes (merge 47→47), with finite I-B2/I-BT2/I-V1/I-O1 totals 47/22/1/4; Aerospace Index PQ-B1 10 in two identical one-page passes and PQ-B2 7; NTRS restored-C1 280/280 explicit native zeros; corrected ESA root 437 with 408 in-window events, five bounded event exports, and 12/12 bounded attachment retrieval/parses. WoS controls and two one-record ordinary RIS passes also passed. These are interface diagnostics, not identification counts.

The final API privacy/provenance rerun used reconciler `2e5ffe894d83dc80186a85f171aa47120dac0f9cc6778045a2324257bad8db5e` and request template `cca156fd09b1c63da8522d483e906acc6d5258e508b1429b7147d772a7e6b0aa`; 12 raw, 16 request, four normalized, and two merge artifacts passed direct/encoded/nested/userinfo/malformed URL and in-memory credential scans. G00/G01/G02 passed at the recorded run boundary (110 queries; 17 merger tests; 14 sources/12 interfaces with two positive/eight negative governance contracts).

## V16-C prospective Engineering Village transport amendment — 2026-08-11

**Status:** `protocol_design_only` at the historical amendment boundary; the fixed-visible-25/page successor is now implemented and hash-pinned offline, but remains unaccepted live. Fixed visible page size is enumeration transport, not search-set semantics: it changes neither the paired Compendex+Inspec source boundary nor the frozen query or other controls.

All prior 100/page observations, including the paired-database 100/page table and the historical Compendex-only diagnostics, remain historical `pilot_not_candidate_search` evidence. The 2026-08-11 V16-C 100/page pilot remains failed (`total:null`, no prefix): its two-row control snapshot was rejected, and it contributed no accepted query result, RIS, normalized/merge output, or partial import. The prospective 25/page successor does not retroactively accept that failure.

A later existing-CDP control probe stopped before mutation or query submission because the current shared selection had All+Knovel selected. Its fixed result was `NULL_CURRENT_SELECTION_NOT_PAIRED_NO_MUTATION`, with `total:null` and evidence SHA-256 `640f625c2000b94ba6ae33e622e2b393519a00354fec2c06892f13f39816834c`. It supplies no page-size result. A canceled pre-execution draft that would have launched fresh Chrome supplied no source evidence.

On 2026-08-13, exactly one strict paired fixed-25 value-blind attempt followed a healthy browser doctor but failed before a valid source/result state on fixed safe host-origin reassertion (adapter exit `1`). Totals, pages, passes, export, normalization, and merge are `null`/unavailable; no JSON, CSV, or commit marker was produced, and there was no retry, metadata/ID inspection, candidate, or final discovery. Evidence MANIFEST SHA-256: `e3a36ec2777b0abf12b567d18f3b816d5fe3e82a326a71a99a9d25c18ee3e7e9`. V16-C remains open/not accepted; the adapter remains offline clean.

A fresh complete rerun is required before acceptance: paired Compendex+Inspec only; All/Knovel clear; exact controls/query; fixed visible 25/page; 25 rows on every nonterminal page; terminal arithmetic; stable totals; database labels/handles; two identical ordered value-blind passes; complete native RIS reconciliation; and normalization/merge of the complete set. Any failure remains `total:null` with no partial prefix. This amendment changes no other gate outcome.

## Post-supervision existing-source follow-up — 2026-08-13

**Status:** `pilot_not_candidate_search`; this is a post-supervision implementation/verification update, not a replacement for the historical 2026-08-11 run-boundary evidence. No final discovery, candidate, screening, PRISMA, or merge input was created.

The latest clean verification found the scoped external adapters independently CLEAN at Critical/High/Medium after 198 tests: Compendex 49, ATAI 47, Springer 45, and ARC 57. `py_compile` and Ruff passed. Adapter/test pins: Compendex `fd7bfb31b1680a327dd38cb856c908c02e3cda581723b1bf7644a8e986326963` / `299b1c139a84f863038025120f765332be46460c65b9b762f7d4dfec5dfe6edc`; ATAI `7dda7f2f7fd2ae269e10cc5e309ff9218256a045fed5f2b9502917f12a437323` / `5ca053886648301a86855b5cfccc5be610d22ecafb1e1b8416e93c7a81e8412a`; Springer `36e4a40c2f7b7b3a743e8a1fe343dd24aceaea3f9cef1004116b078f86b565c9` / `2874ae848dc120b9053db6acf62b4c54133229bf1060b04155beaa93146e10bb`; ARC `066deaf616b1a39ea6c0e0aba365429a9ab791ec3481208bff333605dd548b24` / `2407f6fc1edf8beafd249564d62a2a48c89b55deb32bebf68905e74b6838e7dc`.

Offline verification does not pass a live source gate. Compendex needs the fresh complete paired fixed-25 rerun; the single 2026-08-13 strict paired attempt failed on fixed safe host-origin reassertion before a valid source/result state (adapter exit `1`), with no retry or source values. Wiley's count-only successor failed `WileyBrowserError`, total `null`, before B/C phases. ATAI's corrected live follow-up proved hierarchy, ATAI-only routing, and ABA-safe restoration, then reached ambiguous result controls; total/export are `null` and export was unattempted.

V16-SN made exactly one count-only `SN-B1` invocation after browser doctor passed. No safe Springer target was available, so it used only adapter-owned-page CDP mode; it exited `1` in 4 seconds with total `null`, pages `0`, and records `0`. The raw diagnostic was destroyed for query risk, no detailed error was retained, and there was no retry. It proved neither access nor controls/count/page shape; all full V16-SN gates remain open. MANIFEST SHA-256: `eedf0f21c6c8e085ada40163b526e253ed07f5b79f4d65eb41ec10e5f9bc18a8`.

V16-ARC stopped pre-source, not on an asserted access challenge: no ARC target was safely discoverable and no frozen cap-fitting (≤100) non-A1 sentinel was available without guessing. The adapter had `0` invocations, total is `null`, and no source action occurred. It established no access, controls, count, or page state; all full V16-ARC gates remain open. MANIFEST SHA-256: `a91fd603bf5e7ef828968c9ddccafe0403e700e535d34490fa9004058617f2d0`.

Neither dated attempt produced a candidate or final discovery. Historical Springer/ARC access challenges remain historical evidence only; they are not claimed for these attempts. Scopus, WoS, and IEEE retain their accepted diagnostics/final clean runs. V16-G03 remains open; **the review is not ready for final discovery**.

The owner-only, Git-ignored archive `.searches/eps-mbse-slr-2026/existing-source-followups/2026-08-11/` is an owner-only snapshot at its manifest boundary, not a globally completed archive: later 2026-08-13 jobs and evidence are outside it. It is non-candidate and nonmergeable: 41 jobs, 284 indexed files, 231,240,080 bytes, manifest SHA-256 `33b09fbe986c1a1b0216b6825b4ca889f879823dcb3084e7de46b1f233a30850`.
