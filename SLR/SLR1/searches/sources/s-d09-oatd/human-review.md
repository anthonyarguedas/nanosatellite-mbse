# Pending human methodological decisions — OATD

**Not an approval record.** `accepted_pilot_ids` remains empty. This blocked diagnostic pilot does not authorize a final search or a retry.

**Controller update — 2026-08-24:** the P01 adapter defect was confirmed and remediated code-only at external implementation commit `5ad2a3158b404cc1bafa3df473bf9755d9cd2eef`; the complete offline academic-search suite passed 148 tests. This is not live source validation. See [`controller-review.md`](controller-review.md).

**Human decision — 2026-08-24T10:45:25-04:00:** the review owner accepted the recommendations and authorized exactly one corrective P02 pilot under the scope in `controller-review.md`. This does not accept blocked P01, authorize a final search, or permit screening/candidate import.

**Human implementation direction — 2026-08-24T12:27:17-04:00:** after reviewing E-007, the review owner directed that a positively identified OATD `Server Too Busy` response must keep the adapter-owned tab open, wait, and retry rather than fail immediately. Candidate adapter version 3 implements a finite run-wide budget of two recovery attempts with default waits of 30 and 60 seconds at external commit `adbf1a06f409aa4c00f739812f9fa0a5ccbe518a`. The complete offline academic-search suite passed 161 tests and 78 subtests; no OATD, browser, or network request was made. This authorizes the code-only behavior change, not P03, a final search, screening, import, or direct reissue of E-007.

## H-OATD-01 — Retain the source boundary and reporting treatment

- **Decision needed:** Confirm that a later repaired OATD event is one separate aggregation-index event, not a merge of contributing repositories or PQDT, and remains OATD's existing PRISMA-S/PRISMA reporting treatment.
- **Evidence:** OATD's FAQ says it is an ETD index harvested from contributing repositories/consortia and explicitly distinguishes PQDT; [`official-source-documentation-receipt.json`](pilots/S-D09-P01-20260823T232059-0400/official-source-documentation-receipt.json).
- **Recommendation:** Confirm the existing protocol/crosswalk treatment. OATD is required but does not establish global ETD coverage, degree completion, full-text availability, or a record's provenance without Record Details evidence.

## H-OATD-02 — Same-field pair policy before any OATD final event

- **Decision needed:** Decide whether OATD can remain a direct-query family only if a corrective pilot validates a same-field proximity or other recall-preserving same-field construction for `G_model`, `G_structure`, `C1`, and `T2` pairs.
- **Evidence:** Current visible fields were observed, but the advanced route failed busy and the subsequent aggregate probe timed out; no proximity or field semantic was established. The draft `(left AND right)` clauses are explicitly final-use-prohibited in [`translation-spec.json`](translation-spec.json).
- **Recommendation:** Require a new corrective pilot to demonstrate a compliant source-native pair route. Do not approve record-level all-fields co-occurrence as a substitute, and do not weaken the protocol's pair rule by inference.

## H-OATD-03 — Local treatment of degree/date/language/retrieval limits

- **Decision needed:** Confirm the deferred final handling when OATD cannot safely enforce exact date, English full text, completed master's/doctoral status, or exclusion of undergraduate/non-degree/proposal/metadata-only material.
- **Evidence:** OATD's FAQ says it attempts to index freely available graduate-level records but says originating sites control metadata quality/availability; visible controls were not behaviorally validated.
- **Recommendation:** Preserve each final source total unaltered; apply the 2011-01-01/common-cutoff, language, degree-completion, and retrieval rules locally after discovery, retaining date/degree/retrieval uncertainty rather than screening in the source interface. Do not use country, CC, access, or metadata-language controls as eligibility limits absent validation.

## H-OATD-04 — Controlled-vocabulary disposition

- **Decision needed:** Confirm that no OATD subject/keyword descriptor supplement is accepted unless a new pilot establishes actual controlled-vocabulary behavior and a source-supported mapping.
- **Evidence:** The visible advanced form has a `subjects/keywords` selector, but no Record Details or hierarchy/descriptor behavior was observed.
- **Recommendation:** Retain mandatory free text only. Do not emulate a thesaurus or treat a generic subject label as MBSE.

## H-OATD-05 — Corrective-pilot authorization

- **Decision:** **Accepted and authorized** at 2026-08-24T10:45:25-04:00 for one new corrective OATD pilot using external implementation commit `5ad2a3158b404cc1bafa3df473bf9755d9cd2eef` and the exact scope in [`controller-review.md`](controller-review.md#recommended-corrective-scope).
- **Evidence:** [`adapter-review.json`](pilots/S-D09-P01-20260823T232059-0400/adapter-review.json) demonstrates the P01 defect; [`observations.md`](pilots/S-D09-P01-20260823T232059-0400/observations.md) records the no-retry stop; [`controller-review.md`](controller-review.md) records independent validation and the committed code-only remediation.
- **Boundary:** P01 remains blocked and immutable. The authorization does not permit a final search, screening, candidate import, self-approval, or an automatic retry after P02.

## P02 outcome — controller reviewed

Corrective pilot [`S-D09-P02-20260824T105026-0400`](pilots/S-D09-P02-20260824T105026-0400/) is blocked and not accepted. Six paced count-only diagnostics succeeded, but the first strict attempt returned an adapter-detected access/challenge-or-busy state with `total=null`, zero records, and no prefix; it was not retried. Independent validation and the full disposition are in [`controller-review-p02.md`](controller-review-p02.md).

## H-OATD-06 — P03 authorization

- **Decision:** **Accepted and authorized** at 2026-08-24T13:07:07-04:00 for exactly one narrower P03 using candidate adapter commit `adbf1a06f409aa4c00f739812f9fa0a5ccbe518a` and the staged health gate/residual scope in [`controller-review-p02.md`](controller-review-p02.md#decision-required).
- **Busy boundary:** Version 3's finite internal busy recovery is authorized within each P03 adapter invocation. A persistent busy/challenge/access/unsafe state remains a terminal failed execution and may not be reissued as a new execution inside P03.
- **Boundary:** P01 and P02 remain blocked and immutable. P03 may update only the OATD source packet and restricted P03 evidence. It may not run a final search, screen or classify records, import candidates, alter central files, self-accept, start P04, or commit.

## P03 outcome — controller reviewed

Corrective pilot [`S-D09-P03-20260824T130849-0400`](pilots/S-D09-P03-20260824T130849-0400/) is blocked and not accepted. Its version-3 count-only health gate succeeded with exact total 8 and zero busy retries. The next nonblank advanced-title diagnostic failed technically before any advanced result state or completed advanced-route visit was demonstrated; it retained `total=null` and zero records, then P03 stopped. Independent validation and implementation classification are in [`controller-review-p03.md`](controller-review-p03.md).

## H-OATD-07 — Any future P04 authorization

- **Decision needed:** No P04 is currently authorized. Decide only after a separate code-only fix supplies a cleanup-safe, deterministic advanced-form diagnostic pinned by commit.
- **Recommendation:** Require the offline implementation gates in [`controller-review-p03.md`](controller-review-p03.md#decision-required) before considering a new pilot ID. Do not directly reissue E-002. P01–P03 remain blocked; no final search, screening, candidate import, or central integration is authorized.
