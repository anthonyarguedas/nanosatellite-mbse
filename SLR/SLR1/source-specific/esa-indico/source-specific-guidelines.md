# ESA Indico

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py`

Save final JSON files in `final-searches/` by query ID. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. The first image records the source search page. The second records the root event results page after successful harvest completion. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: ESA Indico category 0
- URL: https://indico.esa.int/
- Route: Complete public metadata harvest followed by deterministic local matching. Do not use rendered `q` as the Boolean search.
- Evidence window: Harvest without an event date filter. Apply the evidence window to candidate reports after retrieval.
- Language: Apply no source filter. Confirm English during screening.
- Publication type: Apply no type, peer review, access, or full text filter. Event and material groups do not form a lossless eligible report type union.
- Scope: Events, Contributions, Subcontributions, and Materials from category 0. Notes and Categories remain outside the complete route.

## Complete metadata contract

A complete harvest requires two equal ordered category 0 event snapshots, every event export, and normalized metadata for every covered record. Material metadata includes stable attachment, parent, folder, filename, description, MIME, size, checksum when supplied, modified date, access state, and public download URL. Search execution makes no attachment body request.

Publish the compact result, full metadata ledger, and terminal marker as one create only transaction. Resume only from a marker bound failure artifact or sidecar with the same query, category, controls, ordered IDs, metadata digest, and completed prefix. The total deadline may increase. No other control may change. A failed harvest is not mergeable.

## Source translation

Use the concepts, compounds, and nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule).

- Literal `L(s)`: One straight double quoted literal. Local matching uses Unicode normalization, case folding, and lexical boundaries.
- Boolean: Use uppercase `AND` and `OR` with full parentheses.
- Matching fields: Event and Contribution title, description, and keywords. Material title, filename, and description. Keep phrase matching within one field.
- Controlled vocabulary decision: Add no supplement. ESA categories are an organizational hierarchy. Keywords, labels, types, and tracks are free form or event local. The source exposes no public subject descriptors, preferred terms, hierarchy expansion, or versioned vocabulary.
- Wildcard decision: Use no wildcard. The local suffix wildcard permits undeclared completions and produced broader sets in validation. Exact expressions preserve the declared concept membership.

## Execution

Create one complete category 0 metadata ledger, then evaluate all nine exact expressions against that fixed ledger. Recompute the ledger gate before every derivative result. Preserve parent event and attachment provenance. A missing record, changed root snapshot, metadata error, or failed screenshot makes the source union incomplete. See [the metadata contract note](metadata-only-contract-supersession.md) and [the readiness audit](../readiness-audit.md).
