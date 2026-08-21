---
task_id: S-L02
source_id: esa-indico
source_name: ESA Indico
method_type: local_harvest
status: draft
guideline_version: 0.1.0
validated_at: null
protocol_commit: 7d564870a36d049716b66c9f9770554ecb04e414
accepted_pilot_ids: []
---

# Source-specific guideline: ESA Indico

**Draft disposition:** `revise`; this packet is not accepted and cannot authorize a final event. The current pilot found a provisional object traversal, but not a complete source-universe proof. [inferred — [E04](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E04), [E06](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E06)]

**Claim labels:** `observed` means a bounded anonymous diagnostic; `official_documentation` means a source or protocol document; `inferred` means this draft's explicit implementation choice; and `untested` means it cannot support acceptance.

## 1. Source boundary and access route

ESA Indico is the protocol's local-harvest source for the full public event and contribution database. [official_documentation — [protocol](../../../protocol-discovery-and-appraisal.md#electronic-databases-collections-and-indexed-online-resources)] The current anonymous Indico UI code exposes Events, Contributions (the paired `contribution` and `subcontribution` search types), Materials (`attachment`), Notes (`event_note`), and Categories. [observed — [E02](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E02)]

The draft source boundary includes public events, contributions, sub-contributions when present, event- and child-level attachments, and public event notes. [inferred — [E06](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E06)] A note is not safely omitted: a bounded note result exposed a `content` field and a note route redirected to a public session-note route. [observed — [E06](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E06)] Categories and session/timetable blocks are structural traversal objects, not candidate text routes. [inferred — [local method](local-method-spec.json#source_boundary)]

Use only anonymous same-origin HTTPS routes: `/export/categ/0.json`, `/export/event/{id}.json?detail=contributions`, `/event/{id}/timetable/`, selected public timetable-note routes, and public attachment URLs. [observed — [E04](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E04), [E06](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E06), [E08](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E08)] Do not authenticate, use cookies, follow an external attachment target, or attempt private objects. [inferred — [local method](local-method-spec.json#materials_and_access)]

ESA's general `www.esa.int/esearch` page, formal ESA Publications listings, and the separately hosted ESA Archives Portal/SHIP are not substitutes for this Indico universe. The Publications page describes formal-reference listings; the Archives page describes historical holdings and login-gated downloads. [official_documentation — [E10](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E10)]

## 2. Interface and field behavior

The public search endpoint is `GET https://indico.esa.int/search/api/search` with `q`, repeated `type`, and opaque `page` values. It returned event title/description/date fields, contribution title/description/IDs, attachment filename/modified-date/IDs, and note content/IDs in bounded diagnostics. [observed — [E01](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E01), [E03](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E03)]

Do not treat source search text as a Boolean language. In a complete three-event sample, implicit `satellite space` and quoted text returned one event; `satellite AND space` and `satellite NOT space` returned explicit zero; `satellite OR space`, parenthesized, and symbolic variants did not yield the union with the ten-plus-page `space` result. Field-like `title:` and `description:` forms returned zero in the test. [observed — [E01](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E01)] This prevents lossless direct A1/A2/A3/B1/B2/BG1/BG2/BC1/BT2/V1/O1 translations. [inferred — [E01](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E01)]

The source's first-page case behavior was equal for `MBSE`/`mbse` and `CubeSat`/`cubesat`; hyphenated `cube-sat` differed from `cube sat`; and `nanosat*` only matched the observed first page for `nanosat`. These bounded results do not validate a source-wide wildcard, phrase, stemming, or expansion rule. [observed — [E02](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E02)]

Use the deterministic local normalizer, finite aliases, phrase definition, token-boundary acronym rule, and explicit-pair rule in [`local-method-spec.json`](local-method-spec.json#normalization), never source-side expansion. [inferred — [local method](local-method-spec.json#normalization)]

## 3. Translation approach

ESA Indico is a local method, not a direct translation source. The executable draft is [`local-method-spec.json`](local-method-spec.json); it integrity-pins the normative concept dictionary and resolves P, E, M, `G_model`, `G_structure`, C1, R, T2, V1, and O1 from it without adding terms. [official_documentation — [dictionary](../../search-concept-dictionary.json), [local method](local-method-spec.json#term_source)]

For one object-route only, core-B is `P AND M`; the Stream-A tag is `P AND E AND M`; BG1/BG2/BC1 are `P AND G_model`, `P AND G_structure`, and `P AND C1`; R and T2 are independent tags; and V1/O1 tags retain their complete `P AND E_probe AND M_probe AND V1/O1` sensitivity logic. [official_documentation — [protocol](../../../protocol-discovery-and-appraisal.md#local-harvest-methods), [local method](local-method-spec.json#candidate_logic)] T2 is a tag rather than a local candidate expansion. [official_documentation — [dictionary](../../search-concept-dictionary.json#/local_method_minimum)]

Metadata and file-content routes are deliberately separate, as are events, contributions, sub-contributions, attachments, and notes. Terms never combine across records, parent/child objects, fields separated by a route boundary, attachment metadata and attachment body, or routes. [official_documentation — [protocol](../../../protocol-discovery-and-appraisal.md#local-harvest-methods); inferred — [local method](local-method-spec.json#matching_routes)]

## 4. Controls and common limits

The approved evidence cutoff is not yet set, so this draft cannot execute a final date-bounded event. [official_documentation — [protocol](../../../protocol-discovery-and-appraisal.md#known-items-and-common-limits)] Preserve event/contribution dates, material/note modification timestamps, timezone, and provenance; treat a modification date as a proxy, retain unresolved dates, and do not silently exclude them. [inferred — [local method](local-method-spec.json#date_and_language)]

Do not apply a publication-type, access, venue, content-type, or English search limit. The bounded export exposed `language=null`, so language remains unknown until screening. [observed — [E07](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E07); official_documentation — [protocol](../../../protocol-discovery-and-appraisal.md#known-items-and-common-limits)]

Use one anonymous request at a time, a minimum 0.5-second delay, bounded 408/425/429/5xx retry rules, and a hard failure after the specified retries. The server's actual rate limit remains untested; the pilot observed successful bounded requests only. [inferred — [local method](local-method-spec.json#materials_and_access); untested — [E01](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E01)]

## 5. Retrieval, pagination, and export

The diagnostic search route returns up to ten records per observed page, uses a cursor-like `page` value, and commonly returns `total=-1`; repeated first pages and the next cursor produced stable ordered IDs in bounded contribution and material tests. [observed — [E02](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E02), [E03](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E03)] It is diagnostic-only and never the final harvest route. [inferred — [local method](local-method-spec.json#interface_classification)]

The provisional harvest is specified to start at root category 0, then retrieve each event export with `detail=contributions`, its public timetable, every listed note, and every listed public attachment. [inferred — [E06](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E06), [E07](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E07)] The event export can expose event-level attachments even where it has zero contributions, and it can expose many child contributions and child attachments. [observed — [E06](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E06), [E07](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E07)]

A public PDF example was retrieved and parsed successfully without retaining its text; the tested ZIP returned 400 to HEAD and 206 to a bounded GET range, while full archive traversal remains unvalidated. [observed — [E08](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E08)] Every unprotected file must be retrieved and parsed, or the final source event fails rather than silently omitting material. [inferred — [local method](local-method-spec.json#materials_and_access)]

## 6. Stable identity and completeness

Use event ID; event ID plus contribution `db_id`/canonical URL; event/parent/sub-contribution source identifiers; event/folder/attachment ID plus canonical URL; and event/note ID plus the timetable-note route. Do not use a contribution friendly/display ID alone. [observed — [E07](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E07); inferred — [local method](local-method-spec.json#object_identity_and_duplicate_policy)]

A bounded category-0 range returned a row count equal to its source count twice with the same order, but it also returned long-running events beginning before the requested range and a category-5 event absent from category 6. [observed — [E04](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E04), [E05](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E05)] This is evidence for a future validation design, not a proof that category 0 is exhaustive, recursive, uncapped, or complete for undated events. [inferred — [local method](local-method-spec.json#universe_and_completion)]

A bounded event-293 reconciliation found equal 35-item export and timetable contribution-friendly-ID ledgers and timetable links for note IDs 2–5. [observed — [E06](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E06)] It does not validate all events, all sub-contributions, or all public-note coverage. [untested — [local method](local-method-spec.json#universe_and_completion)]

## 7. Failure and zero rules

Only a parsed, fully covered route with a source explicit zero may be reported as zero. A `total=-1` search result is not an exact count. [observed — [E01](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E01)]

Set the source-event total to `null` and import nothing for access/login redirects, transport failure, malformed JSON/HTML, count-row mismatch, changed two-pass order, duplicate/missing stable identifier, unproved root scope, missing child reconciliation, unprotected attachment retrieval failure, checksum mismatch, unsupported type, parse failure, or incomplete archive traversal. [official_documentation — [protocol](../../../protocol-discovery-and-appraisal.md#pilots-and-final-search-events); inferred — [local method](local-method-spec.json#universe_and_completion)]

An explicitly protected folder is outside the anonymous-public material universe, not a zero; record its protected count and do not bypass access controls. [observed — [E05](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E05); inferred — [local method](local-method-spec.json#materials_and_access)]

## 8. Final-run procedure

1. Stop immediately unless P-001 supplies the common cutoff and every U1–U4 gate in the local method is verified. [official_documentation — [protocol](../../../protocol-discovery-and-appraisal.md#known-items-and-common-limits); untested — [local method](local-method-spec.json#universe_and_completion)]
2. Run two full, fixed root-category enumerations; reconcile every partition's count, ordered event ledger, categories, and overlap. [inferred — [local method](local-method-spec.json#universe_and_completion)]
3. For each event, obtain its export, timetable, public-note routes, and every public material; reconcile child IDs and parse every supported body under the failure rules. [inferred — [local method](local-method-spec.json#universe_and_completion)]
4. Normalize and match each independent route, retain witnesses and bit-vector overlap accounting, then apply the local date handling without screening or eligibility decisions. [inferred — [local method](local-method-spec.json#candidate_logic)]
5. Only after a complete successful source event may a supervisor authorize the separate final-event procedure and later screening. [official_documentation — [protocol](../../../protocol-discovery-and-appraisal.md#pilots-and-final-search-events)]

This pilot executed none of these final steps. [observed — [manifest](pilots/S-L02-P01-20260821T000344-0400/manifest.json)]

## 9. Validation evidence

The diagnostic packet is [`S-L02-P01-20260821T000344-0400`](pilots/S-L02-P01-20260821T000344-0400/). Its [manifest](pilots/S-L02-P01-20260821T000344-0400/manifest.json) forbids screening and import; its [observations](pilots/S-L02-P01-20260821T000344-0400/observations.md) and [evidence index](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json) label every claim and point to safe summaries or ignored raw worklogs. [observed — [manifest](pilots/S-L02-P01-20260821T000344-0400/manifest.json)]

Observed interface evidence supports local-harvest classification, fields, bounded page behavior, event/contribution/material identity behavior, notes, protected folders, and one public PDF parse. [observed — [E01](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E01), [E03](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E03), [E05](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E05), [E06](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E06), [E08](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E08)]

## 10. Remaining limits and protocol impact

The unverified root-universe proof, all-event timetable/note coverage, actual sub-contribution instances, full attachment-type/archive parsing, link-attachment policy, and server rate ceiling block acceptance. [untested — [local method](local-method-spec.json#universe_and_completion)] The recommended disposition is **revise**, not accept or silently skip ESA Indico. [inferred — [manifest](pilots/S-L02-P01-20260821T000344-0400/manifest.json)]

No protocol semantics were changed and no shared protocol, dictionary, schema, task, log, or final-event file was edited. [observed — [manifest](pilots/S-L02-P01-20260821T000344-0400/manifest.json)] A supervisor must decide whether the observed public note route belongs in the intended source boundary; excluding it would require a documented, committed protocol/source-boundary decision before any final event. [inferred — [E06](pilots/S-L02-P01-20260821T000344-0400/evidence-index.json#E06)]
