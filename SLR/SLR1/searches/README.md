# Search-support artifacts

This directory contains reproducibility artifacts for the frozen SLR search strategy. Protocol version 1.3 was prospectively amended, frozen, and authorized on 2026-08-10. Dated pilot logs document interface, implementation, and no-screening recall validation only: they are **not** candidate/evidence searches and must not be used as discovery results.

## Configuration and dictionaries

- `api-pagination-request-templates.json` — Non-secret Scopus/IEEE API request templates, pagination rules, retry policy, and validation contract.
- `search-concept-dictionary.json` — Frozen version-1.3 P/E/M/G/C1/T vocabulary, optional O/V/R tags, normalization rules, and ESA candidate logic.

## Matcher fixtures

- `fixtures/esa-matcher-regression.json` — Synthetic test cases defining expected ESA metadata/attachment matching behavior.
- `fixtures/esa-matcher-regression-results.json` — Recorded result of the current synthetic suite: all 19 fixtures passed.

## Tools

- `tools/api_pagination_reconcile.py` — Retrieves all Scopus or IEEE API pages safely, checks stable totals/order/IDs, removes secrets, and rejects incomplete results.
- `tools/concept_matcher.py` — Deterministically matches dictionary terms in text/JSON and runs the matcher fixtures.
- `tools/esa_indico_harvest_match.py` — Harvests the whole ESA Indico instance, inventories attachments, extracts text, and applies metadata plus attachment matching.
- `tools/esa_indico_rematch.py` — Re-runs ESA matching from an already harvested local archive without downloading attachments again.
- `tools/esa_genericity_route_regression.py` — Checks version-1.3 genericity-route behavior against synthetic route fixtures.
- `tools/search_strategy_lint.py` — Static checks that all source-specific version-1.3 translations retain required PRESS corrections, expansion partitions, and controls.

## Pilot and audit logs

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

`worklogs/` currently contains no files.
