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
| [`../tools/search_proquest_pqdt_global.py`](../tools/search_proquest_pqdt_global.py) | one pinned PQDT ID; exclusive cooperative ProQuest-platform lock; no arbitrary database/query; aggregate/control state only | `08239a8dd32e18e8e898d97b621e36f6c5a38766f69a9c5c0b7ca159bbf9ec52` |
| [`../tools/test_oatd_basic_count_gate.py`](../tools/test_oatd_basic_count_gate.py) | synthetic OATD wrapper regressions | `b6edfe19f044dd939d6572e785fa2a8d0e2c84156c9089a4fa352f2b7cd33219` |
| [`../tools/test_search_proquest_pqdt_global.py`](../tools/test_search_proquest_pqdt_global.py) | synthetic PQDT wrapper regressions | `6d2e3aa40b863ff8b3293027eb70cd9b265433c5322368de9ce576e1e67d7b63` |
| [`../tools/test_thesis_source_count_gate_fixtures.py`](../tools/test_thesis_source_count_gate_fixtures.py) | synthetic shared-fixture regressions | `2a7d7e370981970b3eaf61a34db6f124423b5a0d00814d291904567ef36915cc` |
| [`../fixtures/thesis-source-count-gate-v1.6.json`](../fixtures/thesis-source-count-gate-v1.6.json) | synthetic, record-free count-gate states | `5e4f054f80d374494507fe21ac5e1a34cd1186a440e45a01e966b5563ea46414` |

Both wrappers require loopback CDP, create/close only one owned page, never call `browser.close()` or `context.close()` on the shared browser, serialize zero candidate records, and mark output non-mergeable. Both read the pinned manifest exactly once as bytes, hash and JSON-decode those same bytes, map ordinary runtime/Playwright/CDP/control/filesystem failures to fixed-code error artifacts with `source_total: null`, and publish same-directory no-clobber owner-only `0600` JSON artifacts. Both deliberately reject native zero until a live source-specific gate establishes it; neither reads result cards, IDs, ranks, exports, or record metadata.

OATD no longer scans broad headings (`h1`/`h2`): status detection is limited to `document.title` plus known page-level error selectors, while aggregate echo/control checks and mechanical `.result` counting remain bounded. PQDT makes two semantic PQDT-only selector assertions in the same owned page and, before submission, requires exactly one visible **Full text** control that is unchecked. It does not infer the absent/hidden/type/degree/access limiter state, and its cooperative lock cannot eliminate external ABA; both remain explicit `V16-PQDT-02` live residuals.

The synthetic fixture explicitly contains no candidate records. The three offline suites pass **47/47** tests (`18` OATD + `25` PQDT + `4` shared fixture), covering exact registries, one-read/no-swap manifests, exact source/route/control state, visible Full text control ambiguity, same-page selector assertions, query/form rewrites, busy/challenge/null behavior, deliberately unvalidated native zero, privacy/static DOM guards, loopback-only CDP, fixed-code runtime failure mapping, and no-clobber `0600` output.

Current-byte offline revalidation also passed `py_compile`, all three thesis-wrapper suites (47/47), scoped Ruff on the six thesis-wrapper/governance files, and `final_run_governance_lint.py`; `search_strategy_lint.py` reported 99 physical plus 11 aliased = 110 logical blocks, 22 manifest entries, six validation files, 13 source scripts, and zero failures. `final_run_governance_lint.py` reported 14 sources, 12 interfaces, two positive and eight negative synthetic contracts. The two added schema-valid negatives prove that duplicate source IDs and a valid-but-wrong OATD interface/PRISMA mapping fail crosswalk binding. Its optional `--manifest PATH` schema-validates and binds any future real manifest to the exact 14 IDs each once, exact interface/PRISMA mappings, and the current crosswalk byte hash; it creates no real manifest/root. This resolves the independent audit's medium governance issue. The Ruff result is scoped only, not a repository-wide claim; an unrelated concurrently modified ESA harvester had a low-severity `E702` note and was not changed in this remediation. JSON parsing passed for the five new JSON contracts/fixtures. No live browser, source, or query operation was run.

This validates only the offline implementation portions of `V16-PQDT-01` and `V16-OATD-01`. `V16-G03` remains open until version-control promotion and all final adapters are frozen. Live controls, B2/remaining expression acceptance, native zero, pagination, stable source identity, source caps, two passes, export/capture, normalization, merge, and date/language gates remain open.

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
- `V16-PQDT-02`–`05` and `V16-OATD-02`–`05`: open.
- The review is **not ready for final discovery**.

The private, owner-restricted, Git-ignored raw archive is `.searches/eps-mbse-slr-2026/thesis-source-validation-round-2/2026-08-11/`; it has 154 indexed files and manifest SHA-256 `5e74b31983baa32855f338defee5b24e48b73312b00ea44f95625c699cc801ec`. It is non-candidate and not merge input.
