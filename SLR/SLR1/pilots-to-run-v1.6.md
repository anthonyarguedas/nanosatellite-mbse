# Cumulative pre-final gates for protocol version 1.6

**Review run:** `eps-mbse-slr-2026`  
**Governing protocol:** version 1.6, frozen and authorized 2026-08-10  
**Current promotion state:** **not ready for final discovery**

## Boundary and disposition rules

This register carries forward every unresolved version-1.5 gate and adds the PQDT/OATD amendment gates. A gate run is `pilot_not_candidate_search`: it may inspect source controls and mechanically parse only the metadata needed to prove totals, pagination, stable identity, exports, and normalization. It must not create candidates, perform relevance/eligibility screening, or enter PRISMA identification counts.

For every gate:

1. use dedicated pilot storage outside clean final-run directories;
2. preserve exact request/form/query, UTC and local time, controls, totals, retrieved counts, pages, stable-ID/rank ledgers or opaque hashes, native artifacts, checksums, software versions, and disposition;
3. discard no failure: authentication, challenge, entitlement, selector ambiguity, rewrite, changing total, short page, missing identity, cap, export mismatch, or timeout is total `null`, never zero;
4. accept zero only from a source-native explicit zero state under all planned controls;
5. inspect no title, author, abstract, identifier value, snippet, or full text unless a source-native export/normalizer gate mechanically requires fields; any mechanically parsed off-topic/sentinel metadata remains screening-prohibited;
6. promote a method only after its acceptance contract is met; otherwise record an explicit fail-closed disposition and do not import a partial prefix; and
7. rerun every accepted method in clean version-1.6 final storage. Passing a gate never promotes its records or dynamic aggregate to discovery.

`accepted diagnostic` below means only that a prior non-candidate gate established the stated method contract. `open` means the method cannot start final discovery until the gate passes or receives an explicit fail-closed final-source disposition. Final source retrieval requirements in the query plan remain mandatory even where a diagnostic is accepted.

The requested non-PQDT/non-OATD open gates were supervised on 2026-08-11. The authoritative dispositions, corrections, aggregate mechanics, tests, private-evidence boundary, and residuals are recorded in [`2026-08-11-v1.6-open-gate-supervision.md`](searches/subagent-logs/2026-08-11-v1.6-open-gate-supervision.md). G00/G01/G02 passed at that run boundary; the overall state remains **not ready for final discovery**.

## Cross-artifact gates

| ID | Status | Gate and acceptance contract |
|---|---|---|
| `V16-G00` | accepted diagnostic; rerun at promotion | Run `searches/tools/search_strategy_lint.py`; require protocol 1.6, dictionary 1.6, 99 physical plus 11 PQDT-aliased blocks = 110 logical blocks, all source/count contracts, 940-cell NTRS arithmetic, and zero failures. Record hashes of protocol, plan, dictionary, linter, and result. |
| `V16-G01` | accepted diagnostic; rerun after every merger change | Run the full `test_merge_search_results.py` suite. Require canonical, distinct aliases `proquest_aerospace_index`, `proquest_dissertations_theses_global`, and `oatd`; require synthetic normalized records to preserve exact source/query/rank/total provenance. |
| `V16-G02` | accepted offline contract; instantiate only at promotion | Frozen [`final-run-source-crosswalk-v1.6.json`](searches/final-run-source-crosswalk-v1.6.json), [`final-run-manifest-schema-v1.6.json`](searches/final-run-manifest-schema-v1.6.json), and [`failure-register-schema-v1.6.json`](searches/failure-register-schema-v1.6.json) define all 14 sources/12 interfaces, separate Compendex/Inspec instances and ATAI/PQDT events, OATD-only website/other-methods accounting, within-source union counting, and null-not-zero failures. Their current-byte SHA-256 values are `48caa54a0624630c3f2fb1b69e2dc2dec99fcb13632a7e83743263241a89b25c`, `fd6720eac1bd6e66021c4517ad94b68bd5330905b5ae75f3a1e4af24c63398f1`, and `6953266f0be7ca902638bdcf18681958391ace4eaea99e40e9e8e0d182d22658`; `final_run_governance_lint.py` (`9ef6622a0955ad647536c83e443391abf83aa6afbd5c217ef5904db4a86a8588`) validates two positive and eight negative synthetic contracts. The two added schema-valid negatives prove that duplicate source IDs and a valid-but-wrong OATD interface/PRISMA mapping fail crosswalk binding. Optional `--manifest PATH` schema-validates and binds any future real manifest to the exact 14 IDs each once, exact interface/PRISMA mappings, and the current crosswalk byte hash; it creates no real manifest/root. This resolves the independent audit's medium governance issue. Do not create the actual clean final manifest/root until promotion. |
| `V16-G03` | **partial; remains open** | The thesis count-wrapper subset remains non-production. The supervised non-thesis audit integrated reviewed API/session-URL security corrections, WoS offline RIS tooling/procedure, the corrected IAF wrapper, and corrected ESA transport/census controls. The active API driver/template are hash-bound and passed 17 privacy/reconciliation tests plus a fresh live privacy gate. A proposed aggregate-only NTRS 940-cell orchestrator was not promoted after independent review; no reviewed final NTRS normalizing/tagging adapter exists. Immutable version-control promotion and all final adapters/procedures remain required; then rerun the complete adapter/privacy suite and prove no secret, session URL, retained-corpus ID, or pilot record can enter final configuration. |

## Direct bibliographic/publisher-source gates carried forward

| ID | Status | Gate and acceptance contract |
|---|---|---|
| `V16-S` | **accepted current preflight; rerun at final execution** | The final post-redaction S-B1 gate authenticated without persisting a key: total 85, two identical complete 85-record passes, four pages (25/25/25/10), stable total/unique IDs/terminal arithmetic, normalized output, and merge 85→84. Active driver/template provenance and artifact privacy passed. Pilot records remain excluded. |
| `V16-WS` | **accepted bounded preflight; final bulk run open** | Core Collection/All Editions, English BG1/BG2/BC1/BT2, and Exact-search state passed. Two ordinary one-record Custom-30 RIS exports were byte-identical, included the cited-reference sidecar path, normalized, and merged 1→1. The accepted repository implementation is a manual procedure plus offline tooling, not browser enumeration. |
| `V16-I` | **accepted current preflight; rerun at final execution** | The final post-redaction I-B2 gate returned 47 in two identical complete passes (25/22), with sole English refinement, no ContentType, one-based pages, stable total/order/IDs, normalized output, and merge 47→47. Finite I-B2/I-BT2/I-V1/I-O1 were accepted at 47/22/1/4; the exact native-zero fixture passed. |
| `V16-C` | **prospective fixed-visible-25/page successor authorized for implementation; fresh complete rerun required — not accepted** | The 2026-08-11 100/page pilot remains failed closed (`total: null`): its two-row control snapshot was rejected, and no query result, RIS, normalized/merge output, or partial prefix was imported. The successor must use paired Compendex+Inspec only, All/Knovel clear, the exact frozen controls/query, and fixed visible 25/page. Accept only stable totals; complete pagination with exactly 25 rows on every nonterminal page and terminal arithmetic; row-level database labels/handles; two identical ordered value-blind complete passes; complete native RIS reconciliation; and normalization/merge of the complete set. Any failure imports no partial prefix. |
| `V16-W` | **failed closed; final-source disposition or fresh rerun required** | A fresh W-BT2 attempt stopped at a structural access challenge before a valid result/control state. Total is `null`; no Collections retry, RIS, normalization, or merge occurred. |
| `V16-SN` | **failed closed; final-source disposition or fresh rerun required** | A fresh Springer Nature Link attempt stopped at a challenge/access page. Total is `null`; no result rows, native CSV, normalization, or merge occurred. |
| `V16-PQ` | **partial; native export remains open** | Advanced Technologies & Aerospace Index only was proved with expansion off and frozen controls: PQ-B1 total 10, two identical complete one-page opaque-ID passes; PQ-B2 count 7; explicit native zero passed. The bounded ordinary one-item dialog exposed no unambiguous RIS option, so native range/normalization/merge and remaining direct limiter evidence remain open. |
| `V16-ARC` | **failed closed; final-source disposition or fresh rerun required** | A fresh current-shape non-A1 sentinel stopped at a structural access challenge. Total is `null`; no row identity, pagination, RIS, normalization, merge, or DOI-less fallback evidence was produced. |

**V16-C control-only follow-up:** A later existing-CDP control probe stopped before any mutation or query submission because the current shared selection had All+Knovel selected. It recorded `NULL_CURRENT_SELECTION_NOT_PAIRED_NO_MUTATION`, `total: null`, and evidence SHA-256 `640f625c2000b94ba6ae33e622e2b393519a00354fec2c06892f13f39816834c`; it supplies no page-size result. A canceled pre-execution draft that would have launched fresh Chrome supplied no source evidence. Neither item accepts the predecessor or the 25/page successor.

## PQDT Global gates

The aggregate-only 2026-08-10 browser pilot proved exact PQDT-only selection and exact A1/B1/B2 echoes with Relevance, 20/page, duplicate exclusion off, Full text off, and automatic variants on. Aggregates 1/17/9 remain non-candidate diagnostics. Fresh isolated profiles were challenge-blocked. The following remain open.

| ID | Status | Gate and acceptance contract |
|---|---|---|
| `V16-PQDT-01` | offline count-wrapper implementation accepted; live/retrieval promotion open | [`search_proquest_pqdt_global.py`](searches/tools/search_proquest_pqdt_global.py) accepts only the eleven pinned `PQDT-*` IDs, targets only `pqdtglobal`, exposes no arbitrary database/query option, and makes two semantic PQDT-only selector assertions in the same owned page. Before submission it requires exactly one visible **Full text** control and requires it unchecked. It reads no cards/IDs, emits no merge input, inherits no ATAI cap/export/ID assumption, and deliberately rejects native zero. Its synthetic tests pass. The wrapper is aggregate-only, non-production, and cannot itself satisfy PQDT-02 through PQDT-05 or final retrieval. |
| `V16-PQDT-02` | open | In an authorized normal session, re-prove exact database/product label, product route, expansion on, duplicate exclusion off, Relevance, page size, exact query echo, and explicit native-zero state. The offline wrapper's exactly-one-visible-unchecked **Full text** assertion does not prove absent/hidden/type/degree/access limiter state; that proof remains an explicit live residual. Its cooperative lock also cannot eliminate external ABA, which remains an explicit live residual. A challenge or entitlement/selector ambiguity is total `null`. |
| `V16-PQDT-03` | open | Establish source total, one-based pagination, terminal-page arithmetic, stable ProQuest record identity, duplicate/missing-ID behavior, total-change behavior, actual pageable ceiling, and two identical complete ordered rank/ID passes using an off-topic or screening-prohibited sentinel. |
| `V16-PQDT-04` | open | Run a one-record native RIS preflight, record fields and actual per-export limit, then reconcile a safe multi-record batch exactly to the ordered source IDs. Preserve native bytes; normalize with source `proquest_dissertations_theses_global`, exact query, total, and global ranks; strip session/account parameters; pass merge smoke. |
| `V16-PQDT-05` | open | Prove year/language semantics and local exact-day accounting, including year-only 2026 unresolved handling. Record degree/manuscript/institution/date/access fields without enabling a discovery degree, manuscript, institution, peer-review, full-text, or OA limiter. |

## OATD gates

The 2026-08-10 browser pilots proved quoted phrases, grouped uppercase Boolean syntax, exact query echoes, and complete finite `OATD-B1` acceptance with aggregate/range/row count 23/23. One composer request returned `Server Too Busy`, direct/fresh routes encountered challenge states, B2 was not executed after an owned-tab state failure, a later B2-only subagent was canceled after 15 minutes with no stdout/stderr/source-state report, and a subsequent B2 retry stopped on a browser/runtime timeout before asserting source state. A pilot-owned B2 URL tab was later closed without result-state inspection. These remain non-candidate diagnostics; no failed B2 attempt supplies a zero or syntax result.

| ID | Status | Gate and acceptance contract |
|---|---|---|
| `V16-OATD-01` | offline count-wrapper implementation accepted; live/retrieval promotion open | [`oatd_basic_count_gate.py`](searches/tools/oatd_basic_count_gate.py) accepts only the eleven pinned finite `OATD-*` IDs, one owned loopback-CDP target, one basic-GET navigation, and no retry. Its page-state check does not scan broad headings (`h1`/`h2`) or card content; it fail-closes on echo/control/access drift, deliberately rejects native zero, and serializes no card/ID/record or merge input. The wrapper is aggregate-only and non-production. Synthetic tests pass; current live control behavior and all OATD-02 through OATD-05 requirements remain open. |
| `V16-OATD-02` | open | Re-prove complete finite B1 and establish complete finite B2 without rewrite. Mechanically preflight all remaining frozen expressions. If one expression exceeds a real source limit, define complete finite source-representable cells prospectively and prove their union contract; do not narrow concepts. |
| `V16-OATD-03` | open | Establish explicit native zero, 30-row and terminal-page arithmetic, pagination parameter, stable result order, one unique OATD record identifier/canonical URL per row, changed-total behavior, duplicates, and any source cap. Require two identical complete ordered passes where exposed. |
| `V16-OATD-04` | open | Validate a rights-aware raw/normalized capture route and merge smoke with source `oatd`, exact query, total, rank, OATD identity, and separate linked-repository URL. The repository is retrieval provenance, not a second discovery event. |
| `V16-OATD-05` | open | Validate local date/language screening fields and exact-day accounting. Record missing/translated metadata, repository participation/rights, embargo/broken-link state, and unresolved 2026 dates. Composer year/language controls may replace local handling only after a logged set-equivalence/metadata-quality gate. |

For any OATD busy/challenge response, stop without immediate retry and record total `null`. Do not bypass source load or access controls.

## Special local-source gates carried forward

| ID | Status | Gate and acceptance contract |
|---|---|---|
| `V16-IAF-01` | **accepted corrected offline route** | Independent review rejected the first wrapper. The authoritative correction consumes the official adapter `results` envelope, binds unique `paperId`, matches only field-local title/abstract, enforces model/architecture-coupled T2, and emits the required provenance subtypes. Unit tests 9/9 and strict fixtures 19/19 passed, together with retained ESA 21/21 and 9/9 regressions. |
| `V16-IAF-02` | **accepted bounded diagnostic; final annual harvest open** | The public index reconciled IAC-2011–IAC-2026 exactly once each; a cap-fitting sentinel completed two identical 50/page passes; an impossible sentinel produced two explicit native zeros; synthetic cap failure produced no prefix. No sentinel record became a candidate. |
| `V16-ESA-01` | accepted diagnostic; rerun at promotion | Current base/concept 21/21, genericity-route 9/9, supplemental attachment 4/4, and local transport/identity 17/17 passed with the corrected dictionary/matcher/harvester. |
| `V16-ESA-02` | **accepted corrected bounded preflight; full final census open** | A fresh independent run reconciled root 437/437 with children 3/377/57/1, root = 5∪6∪7, 9⊆6, and 408 in-window events. Five newly selected ID/date-only events reconciled exactly; 12/12 mechanically selected document attachments were anonymously retrieved and parsed; route isolation, canonical transport, session/response closure, and no-auth/no-cookie checks passed. |
| `V16-NTRS-01` | **accepted diagnostic; final 940-cell retrieval open** | All 280 restored C1 cells reconciled twice as explicit native zeros: 280/280 complete, 560 logical requests, no failure, raw ID, or source metadata retained. These zeros do not authorize omission of any final cell. |
| `V16-NTRS-02` | accepted offline arithmetic; rerun at promotion | Verify 180 core + 250 G + 510 C1 = 940 mandatory final cells and deterministic full-E/T2/V1/O1 tag fixtures under dictionary 1.6. Preserve all ten population forms and all 51 C1 atoms. |

## Promotion record

Before any valid final discovery query, create a dated promotion record containing:

- the disposition and evidence path for every gate above;
- hashes and test results for protocol, query plan, dictionary, linter, source wrappers, merger, normalizers, fixtures, and request templates;
- a statement that all pilot directories are excluded from final-run input discovery;
- the empty, clean version-1.6 final-run root and its initial manifest;
- the 14-source PRISMA-S/failure-register crosswalk; and
- explicit operator approval to begin final discovery.

A failed gate does not silently remove a source. If it cannot be corrected prospectively, record a source/interface failure under the protocol, import no partial records, and retain the failure in PRISMA-S and the final limitations report.
