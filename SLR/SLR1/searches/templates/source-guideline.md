---
task_id: REPLACE
source_id: REPLACE
source_name: REPLACE
method_type: direct_or_local
status: draft
guideline_version: 0.1.0
validated_at: null
protocol_commit: REPLACE
accepted_pilot_ids: []
---

# Source-specific guideline: REPLACE

## 1. Source boundary and access route

State the database or collection boundary, platform, interface, authorized route, and exclusions. Do not record credentials, cookies, session IDs, or private URLs.

## 2. Interface and field behavior

Record visible/native fields, phrase and Boolean behavior, precedence, punctuation, acronym handling, stemming, lemmatization, automatic expansion, wildcard behavior, and evidence links. Establish whether a genuine controlled vocabulary or distinct indexed-term field exists; where available, record exact descriptors, scope and hierarchy, explosion behavior, field syntax, mapping to free-text concepts, and known-item tests. Otherwise record that none is usable.

## 3. Translation approach

For a direct source, link `translation-spec.json` and cover A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2. Explain any lossless cell union and query-length handling. Free text remains mandatory; accepted controlled terms are OR supplements within the concept they map to.

For a local source, link `local-method-spec.json` and define the source universe, routes, normalization, candidate logic, independent tags, partitions, and invariants.

## 4. Controls and common limits

State controls, selected databases, evidence-window implementation, date precision, language handling, prohibited discovery limits, result ordering, and any client-side handling.

## 5. Retrieval, pagination, and export

State page size, pagination or harvest route, exported/retained fields, source-reported versus retrieved totals, source caps, rights restrictions, and preservation method.

## 6. Stable identity and completeness

Define stable identifiers, duplicate handling, two-pass or equivalent completeness proof, total/row reconciliation, and behavior when an identifier is absent.

## 7. Failure and zero rules

List access, query, control, total, range, page, export, parsing, identity, and completeness failures. State when `total=0` is valid and when `total=null` is mandatory. Partial prefixes are never imported.

## 8. Final-run procedure

Give the ordered procedure that a later `R-002` operator can execute without relying on pilot memory. Do not execute it during the pilot.

## 9. Validation evidence

Link accepted pilot manifests and evidence. Distinguish observed interface behavior, official documentation, inference, and untested items. After human approval, let `search-log.md` point to the approval commit and pin any external implementation by commit; do not add a separate approval-hash ledger.

## 10. Remaining limits and protocol impact

List unresolved items, access dependencies, source-native limitations, fallback/failure disposition, and whether any protocol semantics changed.
