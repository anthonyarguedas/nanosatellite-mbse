# Search-support artifacts

This directory contains reproducibility artifacts for the frozen SLR search strategy. Protocol version 1.5 was prospectively amended, frozen, and authorized on 2026-08-10; it retains the version-1.3 genericity methodology and synchronizes twelve databases/collections through eleven interfaces, including authorized IAF IAC proceedings. Dated pilot logs document interface, implementation, and no-screening recall validation only: they are **not** candidate/evidence searches and must not be used as discovery results. Every final source run must use clean version-1.5 storage and the common 2026-08-10 evidence cutoff.

## Authorized scripted sources

Every permitted adapter in `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts` is represented: `search_scopus.py`, `search_ieee_xplore.py`, `search_compendex.py` (paired Compendex+Inspec), `search_wiley_online_library.py`, `search_springer_link.py`, `search_proquest_aerospace.py`, `search_aiaa_arc.py`, `search_iaf_digital_library.py`, `search_esa_indico.py`, and `search_ntrs.py`. Web of Science Core Collection is additionally searched through its normal interface. `search_arxiv.py`, `search_semantic_scholar.py`, and `search_google_scholar.py` are explicitly forbidden.

## Configuration and dictionaries

- `api-pagination-request-templates.json` — Non-secret Scopus/IEEE API request templates, pagination rules, retry policy, and validation contract.
- `search-concept-dictionary.json` — Frozen version-1.5 P/E/M/G/C1/T vocabulary, complete finite T inflections, exact cross-source V1/O1 subsets, optional broader O/V/R tags, normalization rules, and ESA/IAF/NTRS local-tag logic.

## Matcher fixtures

- `fixtures/esa-matcher-regression.json` — Synthetic test cases defining expected ESA metadata/attachment matching behavior.
- `fixtures/esa-matcher-regression-results.json` — Recorded result of the current synthetic suite: all 21 fixtures passed, including finite third-person T2 and V1/O1 tags.
- `fixtures/esa-genericity-route-regression.json` and `fixtures/esa-genericity-route-regression-results.json` — Isolated metadata/attachment genericity-route cases; all 9 current fixtures pass.

## Tools

- `tools/api_pagination_reconcile.py` — Retrieves all Scopus or IEEE API pages safely, checks stable totals/order/IDs, removes secrets, and rejects incomplete results.
- `tools/concept_matcher.py` — Deterministically matches dictionary terms in text/JSON and runs the matcher fixtures.
- `tools/esa_indico_harvest_match.py` — Harvests the whole ESA Indico instance, inventories attachments, extracts text, and applies metadata plus attachment matching.
- `tools/esa_indico_rematch.py` — Re-runs ESA matching from an already harvested local archive without downloading attachments again.
- `tools/esa_genericity_route_regression.py` — Checks version-1.3 genericity-route behavior against synthetic route fixtures.
- `tools/search_strategy_lint.py` — Static version-1.5 checks for all eight direct query families and 88 query blocks; complete A3, finite T2/V1/O1, NTRS 940-cell/C1-anchor arithmetic, twelve-collection/eleven-interface and IAF authorization, ARC controls, and exact accounting of all 13 `search_*.py` source scripts.

## Pilot and audit logs

- `../pilots-to-run-v1.5.md` — Mandatory remaining pre-final pilots and source-specific final-run preflights; every output is non-candidate and must be separated from final discovery.

- `subagent-logs/2026-08-06-compendex-interface-validation.md` — Initial Engineering Village/Compendex syntax, control, pagination, and export investigation.
- `subagent-logs/2026-08-06-compendex-export-followup.md` — Follow-up proving a Detailed CSV export can be normalized and merged.
- `subagent-logs/2026-08-06-wiley-interface-validation.md` — Initial Wiley Advanced Search syntax, fields, date behavior, pagination, and export-route investigation.
- `subagent-logs/2026-08-06-wiley-export-followup.md` — Follow-up proving Wiley RIS export, normalization, and merge compatibility.
- `subagent-logs/2026-08-07-model-assisted-PRESS-review.md` — PRESS-style review that identified seven major search-strategy issues needing correction.
- `subagent-logs/2026-08-07-press-finding-resolution.md` — Closure matrix showing how each PRESS finding was corrected and validated.
- `subagent-logs/2026-08-07-population-term-audit.md` — Browser-based check of CubeSat/nanosatellite spelling variants in Compendex, Wiley, and Scopus.
- `subagent-logs/2026-08-07-api-population-term-audit.md` — Equivalent spelling and transport/authentication checks for IEEE, NTRS, and Scopus APIs.
- `subagent-logs/2026-08-07-press-api-query-validation.md` — Validates corrected Scopus/IEEE queries, removal of type filters, and complete retrieval/merge preflights.
- `subagent-logs/2026-08-07-scopus-ieee-multipage-api-validation.md` — Detailed audit of multi-page Scopus/IEEE pagination, ordering, retries, reconciliation, and secret handling.
- `subagent-logs/2026-08-07-wos-interface-validation.md` — Web of Science Core Collection interface, edition selection, RIS export, cited-reference preservation, and merge validation.
- `subagent-logs/2026-08-07-press-browser-source-validation.md` — Re-validates corrected WoS, Compendex, and Wiley queries and browser controls after PRESS fixes.
- `subagent-logs/2026-08-07-ntrs-revised-matrix-validation.md` — Preserves the superseded 108-cell NTRS matrix pilot and its local EPS tag.
- `subagent-logs/2026-08-07-esa-attachment-first-validation.md` — Validates the full ESA census and attachment-first matching approach, including coverage failures and corrected association logic.
- `subagent-logs/2026-08-10-genericity-methodology-review.md` and `2026-08-10-genericity-search-design-adjudication.md` — Define and adjudicate the version-1.3 reusable-artifact/tailoring recall design.
- `subagent-logs/2026-08-10-genericity-api-search-pilot.md`, `2026-08-10-genericity-api-refinement-pilot.md`, `2026-08-10-genericity-browser-search-pilots.md`, and `2026-08-10-genericity-esa-ntrs-pilots.md` — Preserve aggregate-only, no-screening interface diagnostics for the added partitions.
- `subagent-logs/2026-08-10-v1.3-final-consistency-audit.md` — Records the final cross-artifact consistency gate.
- `subagent-logs/2026-08-10-browser-search-acceleration-and-interface-policy.md` — Records deterministic Wiley/Compendex work, the WoS automation gate, benchmarks, and the API-versus-browser decision.
- `subagent-logs/2026-08-10-aiaa-arc-source-addition-pilots.md` — Records the original AIAA ARC source/syntax/count pilots, browser timings, page-size failures, and the fast result-tab contract. The later off-topic per-record RIS and complete multi-page adapter gates are summarized in `../search-log.md`; their aggregate count, exact native preflight, access-failure record, complete 44-record gate, and manifests are retained only in the Git-ignored `.searches/eps-mbse-slr-2026/aiaa-arc-adapter-live-test/2026-08-10/` archive.

`worklogs/` currently contains no files.
