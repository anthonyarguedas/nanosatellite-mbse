# Version-1.6 thesis-source validation round 2

**Review run:** `eps-mbse-slr-2026`  
**Validation interval:** 2026-08-10 through 2026-08-11 EDT  
**Classification:** `pilot_not_candidate_search` and offline contract validation  
**Final discovery:** not started

## Boundary

This round continued the version-1.6 PQDT/OATD and cross-artifact gates without creating a candidate set. Completed browser actors were instructed to inspect only source identity, controls, exact query echo, aggregate/explicit-zero state, ranges, and mechanical container counts. No completed report contains a title, author, abstract, snippet, source-record identifier, result/repository URL, export, full text, relevance decision, or eligibility decision. Failed browser attempts contributed no source state and no partial record. Offline fixtures are synthetic and contain no literature metadata.

## Browser validation outcomes

### OATD-B2

An internet-enabled subagent attempted one exact frozen `OATD-B2` basic-interface aggregate check in one owned target:

- interval: 2026-08-10 21:34:53.822–21:34:58.911 EDT / 2026-08-11 01:34:53.822–01:34:58.911 UTC;
- elapsed: 5.089 seconds;
- outcome: local browser/runtime `TimeoutError` before the actor confirmed an owned OATD target or inspected source state;
- query echo, aggregate, range, container count, controls, and pagination shape: not evaluated;
- total: `null`, never zero; no retry by that actor.

A later browser doctor showed four known pilot-owned OATD tabs, including a target at the exact B2 URL. Because the failed actor had not asserted target identity or returned source evidence, the orchestrator closed those four known OATD tabs without inspecting result state. The URL's existence is not accepted as query-echo, syntax, aggregate, or pagination evidence. `OATD-B2` therefore remains open and total `null`.

### PQDT native-zero/control attempt

A second internet-enabled subagent opened the normal PQDT database-selection page for the deliberately impossible sentinel:

```text
NOFT("v16pqdtzeroprobe9f7c2a6e") AND YR(2011-2026) AND LA(English)
```

It stopped on a local browser-automation command error before checkbox-state inspection. Exact selection, controls, sentinel submission, query echo, and explicit zero were not established. No database selection changed, no restoration was needed, and the owned tab was closed. The outcome is total `null`, not zero. Previously accepted aggregate-only A1/B1/B2 observations remain diagnostics; this failed sentinel adds no source evidence.

## Frozen query and aggregate-only wrapper contracts

[`../thesis-source-query-manifest-v1.6.json`](../thesis-source-query-manifest-v1.6.json) pins all 22 new-source events:

- eleven `PQDT-*` IDs mapped byte-for-byte to their normative `PQ-*` bodies;
- eleven finite, wildcard-free `OATD-*` bodies; and
- SHA-256 for every body and the frozen source-control contracts.

The frozen manifest's current-byte SHA-256 remains `df1fbc09d8fa88f7d02564445c9fb8644b40cdbeabf58fd7d57bf6a28ce23040`.

The following review-local artifacts are implemented and hash-pinned in the current validation state. They are not yet version-control promoted, are aggregate-only and non-production, and are not final retrieval adapters:

| Artifact | Current validation boundary | SHA-256 |
|---|---|---|
| [`../tools/oatd_basic_count_gate.py`](../tools/oatd_basic_count_gate.py) | one pinned OATD ID; exclusive OATD lock; one basic GET navigation; no retry; aggregate/control state only | `c74c72fcb17b3be0fb38058f2e2fb62a7b7bb8ea0a524c92299ee1dccbba01a4` |
| `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts/search_proquest_pqdt_global.py` (moved later; historical local hash) | one pinned PQDT ID; exclusive cooperative ProQuest-platform lock; no arbitrary database/query; aggregate/control state only | `08239a8dd32e18e8e898d97b621e36f6c5a38766f69a9c5c0b7ca159bbf9ec52` |
| [`../tools/test_oatd_basic_count_gate.py`](../tools/test_oatd_basic_count_gate.py) | synthetic OATD wrapper regressions | `b6edfe19f044dd939d6572e785fa2a8d0e2c84156c9089a4fa352f2b7cd33219` |
| [`../tools/test_search_proquest_pqdt_global.py`](../tools/test_search_proquest_pqdt_global.py) | synthetic PQDT wrapper regressions | `6d2e3aa40b863ff8b3293027eb70cd9b265433c5322368de9ce576e1e67d7b63` |
| [`../tools/test_thesis_source_count_gate_fixtures.py`](../tools/test_thesis_source_count_gate_fixtures.py) | synthetic shared-fixture regressions | `2a7d7e370981970b3eaf61a34db6f124423b5a0d00814d291904567ef36915cc` |
| [`../fixtures/thesis-source-count-gate-v1.6.json`](../fixtures/thesis-source-count-gate-v1.6.json) | synthetic, record-free count-gate states | `5e4f054f80d374494507fe21ac5e1a34cd1186a440e45a01e966b5563ea46414` |

Both wrappers require loopback CDP, create/close only one owned page, never call `browser.close()` or `context.close()` on the shared browser, serialize zero candidate records, and mark output non-mergeable. Both read the pinned manifest exactly once as bytes, hash and JSON-decode those same bytes, map ordinary runtime/Playwright/CDP/control/filesystem failures to fixed-code error artifacts with `source_total: null`, and publish same-directory no-clobber owner-only `0600` JSON artifacts. Both deliberately reject native zero until a live source-specific gate establishes it; neither reads result cards, IDs, ranks, exports, or record metadata.

OATD no longer scans broad headings (`h1`/`h2`): status detection is limited to `document.title` plus known page-level error selectors, while aggregate echo/control checks and mechanical `.result` counting remain bounded. PQDT makes two semantic PQDT-only selector assertions in the same owned page and, before submission, requires exactly one visible **Full text** control that is unchecked. It does not infer the absent/hidden/type/degree/access limiter state, and its cooperative lock cannot eliminate external ABA; both remain explicit `V16-PQDT-02` live residuals.

The synthetic fixture explicitly contains no candidate records. The three offline suites pass **47/47** tests (`18` OATD + `25` PQDT + `4` shared fixture), covering exact registries, one-read/no-swap manifests, exact source/route/control state, visible Full text control ambiguity, same-page selector assertions, query/form rewrites, busy/challenge/null behavior, deliberately unvalidated native zero, privacy/static DOM guards, loopback-only CDP, fixed-code runtime failure mapping, and no-clobber `0600` output.

Current-byte offline revalidation also passed `py_compile`, all three thesis-wrapper suites (47/47), scoped Ruff on the six thesis-wrapper/governance files, and `final_run_governance_lint.py`; `search_strategy_lint.py` reported 99 physical plus 11 aliased = 110 logical blocks, 22 manifest entries, six validation files, 13 source scripts, and zero failures. `final_run_governance_lint.py` reported 14 sources, 12 interfaces, two positive and eight negative synthetic contracts. The two added schema-valid negatives prove that duplicate source IDs and a valid-but-wrong OATD interface/PRISMA mapping fail crosswalk binding. Its optional `--manifest PATH` schema-validates and binds any future real manifest to the exact 14 IDs each once, exact interface/PRISMA mappings, and the current crosswalk byte hash; it creates no real manifest/root. This resolves the independent audit's medium governance issue. The Ruff result is scoped only, not a repository-wide claim; an unrelated concurrently modified ESA harvester had a low-severity `E702` note and was not changed in this remediation. JSON parsing passed for the five new JSON contracts/fixtures. No live browser, source, or query operation was run.

This validates only the offline implementation portions of `V16-PQDT-01` and `V16-OATD-01`. `V16-G03` remains open until version-control promotion and all final adapters are frozen. Live controls, B2/remaining expression acceptance, native zero, pagination, stable source identity, source caps, two passes, export/capture, normalization, merge, and date/language gates remain open.

## Post-round PQDT limiter-state hardening and OATD follow-up — 2026-08-13

This dated follow-up is `pilot_not_candidate_search` / offline contract validation only; it creates no final-run root, candidate, screening decision, PRISMA count, or merge input.

The aggregate-only PQDT wrapper now mechanically scans named Full text, peer-reviewed, source-type, document-type, degree/manuscript, and access controls across visible and non-visible `input`/`select` elements. It retains only count/boolean state, fails closed on an enabled or ambiguous named limiter, and emits no label, ID, value, URL, record, or session data. The implementation does not prove the current live ProQuest DOM mapping or eliminate external ABA; both remain `V16-PQDT-02` live residuals. Current changed-artifact SHA-256 values are:

| Artifact | SHA-256 |
|---|---|
| `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts/search_proquest_pqdt_global.py` (superseded pre-move hash) | `1757234622eeea49766543372ecb49eabdb25e1cacf10ebcbc4d606a35e79604` |
| [`../tools/test_search_proquest_pqdt_global.py`](../tools/test_search_proquest_pqdt_global.py) | `c49717e9c0150a3388fce5b64495a0d48886f3827ffb12c6926a5fbfe0cac295` |
| [`../fixtures/thesis-source-count-gate-v1.6.json`](../fixtures/thesis-source-count-gate-v1.6.json) | `e631d6a34b3876d071289db23aeca802f3f425826f3115873a6a2b79645551ae` |

`py_compile`, scoped Ruff, the OATD/PQDT/shared synthetic suites (**49/49**: 18/27/4), and `search_strategy_lint.py` passed. The new synthetic cases cover active non-visible limiters, duplicate/ambiguous controls, impossible count relations, and missing semantic categories. No ProQuest source session was operated during this implementation check.

A separate fresh dedicated-browser `OATD-B1` aggregate-only attempt started at `2026-08-13T17:00:33.522Z` and stopped at `2026-08-13T17:00:34.035Z` with fixed failure code `access_state`. It performed no retry; `source_total` is `null`, `results_retrieved` and serialized candidates are `0`, and it created no merge input or final discovery. The owner-only immutable artifact is `.searches/eps-mbse-slr-2026/v16-oatd-02-20260813T170027Z-79209/OATD-B1.count-gate.json`; it retains no result cards, IDs, or source metadata. It establishes neither access nor aggregate/control state, so all OATD live gates remain open.

After a healthy browser doctor, exactly one aggregate-only `PQDT-B1` invocation started at `2026-08-13T17:09:10.400Z` and stopped at `2026-08-13T17:09:14.512Z` with fixed failure code `other_fail_closed`. It was not retried. The sanitized artifact has no observed source state; `source_total` is `null`, retrieved/serialized candidates are `0`, and merge input/candidate import are `false`. It establishes none of exact PQDT selection, product route, controls, query echo, or native-zero state. The owner-only immutable artifact `.searches/eps-mbse-slr-2026/v16-pqdt-02-live-20260813T170910Z-79428/PQDT-B1.count-gate.json` has SHA-256 `77ede2188d4413eb144d57eab2952f12dc5507297c8ac7d7fe09b1d5a761f5b6`. `V16-PQDT-02` remains open.

### Corrected current-shape PQDT control sequence and package move — 2026-08-13

The first 17:09:10.400Z invocation above exposed a local wrapper fault: `configure_result_options()` passed an asynchronous generator to `any()` (`any(await control.count() ... for control ...)`), which raised before source-state serialization. Corrected offline work then materialized the control counts, added safe fixed reason/stage fields, accepted ProQuest's current always-visible `#sortType`, `#itemsPerPage`, and `#excludeDuplicate` controls when the old expander is absent, normalized the visible Full-text control label, and accepted only the fixed post-selection redirect `/pqdtglobal/commandline/advanced` alongside `/pqdtglobal/commandline`. No raw exception, provider text, result card, or record metadata is retained.

The following operator-directed corrected attempts were all `pilot_not_candidate_search`; no automatic retry occurred. Failed artifacts retain `source_total: null`, zero records, and no merge input.

| Started UTC | Outcome | Artifact SHA-256 |
|---|---|---|
| `17:14:57.014` | `protocol_mismatch` before safe reason instrumentation | `414137bfa71f151c8269e87673c039934c12d6433e058c34d610361b1fd77eb2` |
| `17:16:24.072` | `protocol_mismatch` / `result_options_missing`; current no-expander variant then corrected | `1f7de601d7d526985f100cbe27b37a3bd8d9a6b969a447ec645283b645cf7cc9` |
| `17:18:34.918` | `protocol_mismatch` / `product_route_mismatch`; fixed command-route variant then identified | `4949e0177eb8d7c7534e33c26a704fce25eb434ff4cf1cf241b6606d917b1189` |
| `17:19:50.501` | `protocol_mismatch` / `product_route_mismatch`; pre-submission control probe established `/pqdtglobal/commandline/advanced` | `72d9b6054c4965cf6f7fbc7bc47fa740623d5a1348fcaec0ed96d4afd61e2f46` |
| `17:21:01.561` | **success**: `PQDT-B1` total `17`; exact selection asserted twice; exact query echo; Relevance/20; duplicate exclusion off; spelling/plural-adjective expansion on; all named limiters inactive; no records serialized | `6f5c172e9a4a41e50bc961071079fb979eeb42b87574a37f82ad6f26171c1927` |

The successful artifact is `.searches/eps-mbse-slr-2026/v16-pqdt-02-live-route-fixed-20260813T172101Z-79760/PQDT-B1.count-gate.json` (owner-only `0600`); it is non-candidate and nonmergeable. It advances only the positive-control portion of `V16-PQDT-02`: native zero, external ABA, pagination, identity, cap, export, normalization, and date/language gates remain open.

The canonical wrapper was then moved to `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts/search_proquest_pqdt_global.py`; the former review-local implementation was removed. The moved wrapper requires `--query-manifest` and accepts only bytes matching the immutable review manifest SHA-256, so the external location does not permit arbitrary query contracts. Current SHA-256 values are wrapper `70b63eba3927a14bf892450b85225be5465d6032b6bd9e73720e4860e5197e98`, review-local wrapper test `a4363273b368a2ef22e81eb3c78f17b3687e0bde7279a05ba556dfe4398808fc`, fixture `e631d6a34b3876d071289db23aeca802f3f425826f3115873a6a2b79645551ae`, and manifest `df1fbc09d8fa88f7d02564445c9fb8644b40cdbeabf58fd7d57bf6a28ce23040`. `py_compile`, scoped Ruff, strategy lint, and the OATD/PQDT/shared suites passed **53/53** (18/31/4). The wrapper remains aggregate-only and non-production.

## Final-run governance contract

A first-party PRISMA/PRISMA-S methods subagent found that PRISMA does not prescribe one universal classification for publisher/event platforms. The review therefore freezes one explicit review-specific rule: OATD alone is `other_methods` / `website`; each other bounded structured operational collection is `databases_and_registers` / `database`, regardless of browser, API, export, or local-harvest transport. No source appears in both channels.

The contract preserves fourteen identification sources through twelve interfaces, including separate Compendex and Inspec instances in simultaneous Engineering Village events and separate ATAI-only and PQDT-only ProQuest events. Engineering Village's combined total, any combined ProQuest platform total, IAF annual harvest totals, ESA material totals, NTRS cell totals, and OATD repository links are audit/provenance values rather than extra PRISMA identification units.

| Artifact | SHA-256 |
|---|---|
| [`../final-run-source-crosswalk-v1.6.json`](../final-run-source-crosswalk-v1.6.json) | `48caa54a0624630c3f2fb1b69e2dc2dec99fcb13632a7e83743263241a89b25c` |
| [`../final-run-manifest-schema-v1.6.json`](../final-run-manifest-schema-v1.6.json) | `fd6720eac1bd6e66021c4517ad94b68bd5330905b5ae75f3a1e4af24c63398f1` |
| [`../failure-register-schema-v1.6.json`](../failure-register-schema-v1.6.json) | `6953266f0be7ca902638bdcf18681958391ace4eaea99e40e9e8e0d182d22658` |
| [`../tools/final_run_governance_lint.py`](../tools/final_run_governance_lint.py) | `9ef6622a0955ad647536c83e443391abf83aa6afbd5c217ef5904db4a86a8588` |

`final_run_governance_lint.py` passes with 14 sources, 12 interfaces, two positive in-memory contracts, and eight negative contracts. The two added schema-valid negatives prove that duplicate source IDs and a valid-but-wrong OATD interface/PRISMA mapping fail crosswalk binding. Optional `--manifest PATH` schema-validates and binds any future real manifest to the exact 14 IDs each once, exact interface/PRISMA mappings, and the current crosswalk byte hash. It proves that a valid zero requires numeric zero, unavailable/failed totals require `null`, and failures cannot import partial records or contribute a flow count. It creates no real final manifest/root and executes no source query. The independent audit's medium governance issue is resolved; the actual clean final manifest/failure-register instances remain deferred until explicit promotion.

Method references:

- <https://www.prisma-statement.org/prisma-2020-flow-diagram>
- <https://www.prisma-statement.org/prisma-search>
- <https://osf.io/y765x/>
- <https://doi.org/10.5195/jmla.2022.1449>

## Disposition

- `V16-G02`: offline governance contract accepted; instantiate only at promotion.
- `V16-G03`: remains open until version-control promotion and all final adapters are frozen; the thesis-source aggregate wrappers are only implemented and hash-pinned in the current validation state.
- `V16-PQDT-01` and `V16-OATD-01`: offline count-wrapper implementation is validated; the wrappers remain aggregate-only, non-production, and live/retrieval promotion remains open.
- `V16-PQDT-02`: partial after the non-candidate live positive-control confirmation; explicit native zero and all retrieval gates remain open. `V16-PQDT-03`–`05` and `V16-OATD-02`–`05`: open.
- The review is **not ready for final discovery**.

The private, owner-restricted, Git-ignored raw archive is `.searches/eps-mbse-slr-2026/thesis-source-validation-round-2/2026-08-11/`; it has 154 indexed files and manifest SHA-256 `5e74b31983baa32855f338defee5b24e48b73312b00ea44f95625c699cc801ec`. It is non-candidate and not merge input.
