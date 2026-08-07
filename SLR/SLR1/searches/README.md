# Search-support artifacts

This directory contains the reproducibility artifacts for the pre-freeze SLR search strategy. Protocol version 1.2 was frozen and authorized on 2026-08-07. The dated pilot logs document interface and implementation validation only: they are **not** candidate/evidence searches and must not be used as discovery results.

## Configuration and dictionaries

- `api-pagination-request-templates.json` — Non-secret Scopus/IEEE API request templates, pagination rules, retry policy, and validation contract.
- `search-concept-dictionary.json` — Frozen P/E/M search vocabulary (population, EPS, MBSE), optional O/V tags, normalization rules, and ESA candidate logic.

## Matcher fixtures

- `fixtures/esa-matcher-regression.json` — Synthetic test cases defining expected ESA metadata/attachment matching behavior.
- `fixtures/esa-matcher-regression-results.json` — Recorded result of those tests: all 10 fixtures passed.

## Tools

- `tools/api_pagination_reconcile.py` — Retrieves all Scopus or IEEE API pages safely, checks stable totals/order/IDs, removes secrets, and rejects incomplete results.
- `tools/concept_matcher.py` — Deterministically matches dictionary terms in text/JSON and runs the matcher fixtures.
- `tools/esa_indico_harvest_match.py` — Harvests the whole ESA Indico instance, inventories attachments, extracts text, and applies metadata plus attachment matching.
- `tools/esa_indico_rematch.py` — Re-runs ESA matching from an already harvested local archive without downloading attachments again.
- `tools/search_strategy_lint.py` — Static checks that all source-specific query translations retain required PRESS-corrected terms and controls.

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
- `subagent-logs/2026-08-07-ntrs-revised-matrix-validation.md` — Validates the final 108-cell NTRS population × MBSE matrix and its local EPS tag.
- `subagent-logs/2026-08-07-esa-attachment-first-validation.md` — Validates the full ESA census and attachment-first matching approach, including coverage failures and corrected association logic.

`worklogs/` currently contains no files.
