# S-L02 P04 execution plan — ESA Indico

> **Current validation policy:** Follow the [live-first source-pilot policy](../../live-first-validation-policy.md). It supersedes any broader offline-suite prerequisite below: run only the minimum launch gate, inspect failures on the real owned page, patch technical defects immediately, and retest live after minimal changed-path checks.


**Status:** source-free launch plan only. P04 has not run and makes no current-interface claim. The plan is diagnostic, sequential, bounded, and cannot create candidates, screening records, a final event, or a source total.

## Purpose and fixed method

P01–P03 remain immutable historical evidence. P04 has exactly two conditional source operations:

1. inspect a fixed, bounded set of twelve previously enumerated event IDs for a non-empty documented `subContributions` record or an irregular/external material route; and
2. if either route is found, traverse at most two selected events with the current local harvester, generate the real nested/irregular queue, and terminally test at most one item of each queue kind.

The normative method remains [`local-method-spec.json`](local-method-spec.json), locked to dictionary SHA-256 `61526b5d617a2af332aa3bb5d2a57b01dce60988c321d5c6deb807549fca076f`. The nine files under [`queries/`](queries/) are exact local partition contracts; ESA has no accepted lossless Boolean query submission. No term, Boolean relation, source/field boundary, date/language/content limit, recall rule, completeness definition, or PRISMA rule is changed.

This is not an all-time census. It does not query the one-box search, category sentinels, a fresh root universe, PDFs, OCR, matching, or candidates. An empty result in this bounded shape scan is only “no target in these twelve inspected event exports,” never an ESA zero.

## Runtime allocation and namespace

There is no `campaign.json` for this source yet. Do **not** fabricate a campaign or P04 attempt in this source-free preparation. At runtime, before any ESA request:

```bash
ROOT=/Users/antho/nanosatellite-mbse
SCRIPT="$ROOT/SLR/SLR1/scripts/esa_indico_local_harvest.py"
DICT="$ROOT/SLR/SLR1/searches/search-concept-dictionary.json"
TEMPLATE_CAMPAIGN="$ROOT/SLR/SLR1/searches/templates/pilot-campaign.template.json"
TEMPLATE_MANIFEST="$ROOT/SLR/SLR1/searches/templates/pilot-manifest.template.json"
P03="$ROOT/SLR/SLR1/searches/sources/s-l02-esa-indico/pilots/S-L02-P03-20260823T135313-0400"
STAMP="$(date +%Y%m%dT%H%M%S%z)"
PILOT_DATE="$(date +%F)"
ATTEMPT_ID="S-L02-P04-$STAMP"
CAMPAIGN_ID="S-L02-C01-$STAMP"
PACKET="$ROOT/SLR/SLR1/searches/sources/s-l02-esa-indico/pilots/$ATTEMPT_ID"
RESTRICTED="$ROOT/.searches/esa-indico/$ATTEMPT_ID"
PROTOCOL_COMMIT="$(git -C "$ROOT" rev-parse HEAD)"
mkdir -p "$PACKET" "$RESTRICTED"
```

`STAMP` is created once and never reused. Every output, queue, receipt, and manifest path below is under this new attempt namespace; no file is pre-created or overwritten. `PILOT_DATE` is the actual local execution date and is recorded as the **diagnostic upper bound only**. It is not `P-001`, a publication-date cutoff, or an event-date filter. ESA event and attachment dates remain metadata, as required by the guideline.

Before source work, instantiate a new `campaign.json` and first `manifest.json` from the two shared templates, changing only the runtime identity/fingerprint/allocation fields and the local-harvest gate catalog. Set `task_id=S-L02`, `source_id=esa-indico`, `method_type=local_harvest`, `diagnostic_only=true`, `screening_performed=false`, `candidate_import_permitted=false`, and `candidate_records_imported=0`. Use `attempt_kind=initial`, `authorized_by=controller`, `prospectively_authorized=true`, `maximum_source_operations_per_attempt=2`, and no human methodological decision. The initial campaign must remain unaccepted and must list these gates: `G-SOURCE-BOUNDARY`, `G-LOCAL-CANDIDATE-LOGIC`, `G-LOCAL-TAGGING`, `G-LOCAL-HARVEST-COVERAGE`, `G-LOCAL-IDENTITY`, `G-CONTROLLED-VOCABULARY`, `G-DATE-CONTROL`, `G-LANGUAGE-CONTROL`, `G-RETRIEVAL`, `G-COMPLETENESS`, and `G-FAILURE-BEHAVIOR`. Compute the manifest SHA-256 after writing it, place that hash in the campaign, and validate both against the shared schemas before the first request. Do not mark a gate passed merely because P03 exists; carry forward only exact, unchanged evidence with its hash.

The campaign source-operation maximum is **2**. HTTP retry/backoff is internal route handling, not another source operation: maximum two retries for 408/425/429/5xx, no retry for access/challenge/3xx, and at least 0.5 seconds between sequential requests. Use timeout 45 seconds. No parallel requests. Under the current SLR1 policy, this complete HTTP live phase is globally serial and must not overlap any browser-backed or other HTTP/local source phase. The source operation is failed/null on any unreconciled response, even if earlier rows were usable.

## Source-free preflight

Run these commands before allocating the live attempt. They make no ESA request:

```bash
cd "$ROOT"
python3 "$SCRIPT" --help >/dev/null
uv run --offline --with 'jsonschema>=4.0' \
  python -m unittest -v SLR/SLR1/scripts/test_esa_indico_local_harvest.py
uv run --offline SLR/SLR1/scripts/validate_search_infrastructure.py
shasum -a 256 "$SCRIPT" \
  SLR/SLR1/scripts/test_esa_indico_local_harvest.py \
  "$ROOT/SLR/SLR1/searches/sources/s-l02-esa-indico/local-method-spec.json" \
  "$ROOT/SLR/SLR1/searches/sources/s-l02-esa-indico/translation-spec.json"
```

A preflight failure stops allocation. Do not use a provider fallback, run the one-box probe, or call any network command to repair a source-free failure.

## Immutable P04 input event set

P03's immutable 2020–2024 cap receipt lists the following first twelve IDs already inspected for export shape: `424 443 452 404 331 332 320 321 346 518 431 372`. P04 uses the next twelve in that same immutable source order, and no others:

```text
453 448 373 379 387 340 262 416 438 430 334 425
```

This is a reproducible bounded diagnostic sample, not a claim that the P03 response was complete or uncapped. Do not replace an ID, append a convenient event, or launch a new category census when a target is absent.

## Exact operation order

Run all HTTP operations through the current review-specific script, directly and anonymously, with redirects disabled. ESA is an HTTP/local-harvest method; it is not a browser-backed phase, so do not acquire a CfT lease, use CDP, open a browser, or access a provider endpoint outside the script. If a future operator chooses a manual/browser queue resolution, the shared CfT lease contract applies to that manual phase; never create a fresh browser/profile/port.

### Operation 1 — bounded nested/irregular shape search

Output namespace: `$RESTRICTED/op-01-shape-search.json` and `$RESTRICTED/op-01-target-selection.json`.

```bash
set -euo pipefail
uv run "$SCRIPT" probe-event-material-shapes \
  --event-id 453 --event-id 448 --event-id 373 --event-id 379 \
  --event-id 387 --event-id 340 --event-id 262 --event-id 416 \
  --event-id 438 --event-id 430 --event-id 334 --event-id 425 \
  --max-events 12 \
  --timeout 45 --min-request-interval 0.5 --retries 2 \
  --output-path "$RESTRICTED/op-01-shape-search.json"
```

This performs at most twelve event-export GETs, requests only `detail=subcontributions`, retains safe IDs/counts/route classes/hashes, and does not fetch owner pages or material bytes. Require `failed_event_ids` to be empty before selecting a target. Select, in source order, the first successful event with `subcontribution_count > 0` as `nested_event_id` and the first successful event with a non-empty `irregular_or_external_attachment_ids` list as `irregular_event_id`; deduplicate if they are the same. A failed event is a coverage failure, not a zero.

Use this source-free selection step; it writes only safe target IDs and bounds:

```bash
if [[ "$(jq '.failed_event_ids | length' "$RESTRICTED/op-01-shape-search.json")" != 0 ]]; then
  printf '%s\n' 'Operation 1 had a failed event; stop with null coverage.' >&2
  exit 1
fi
NESTED_EVENT_ID="$(jq -r '[.events[] | select(.status == "success" and ((.subcontribution_count // 0) > 0)) | .event_id] | first // ""' "$RESTRICTED/op-01-shape-search.json")"
IRREGULAR_EVENT_ID="$(jq -r '[.events[] | select(.status == "success" and ((.irregular_or_external_attachment_ids // []) | length > 0)) | .event_id] | first // ""' "$RESTRICTED/op-01-shape-search.json")"
jq -n \
  --arg pilot_date "$PILOT_DATE" \
  --arg nested_event_id "$NESTED_EVENT_ID" \
  --arg irregular_event_id "$IRREGULAR_EVENT_ID" \
  --argjson inspected_event_ids '["453","448","373","379","387","340","262","416","438","430","334","425"]' \
  '{schema_version:"esa-indico-p04-target-selection/v1", diagnostic_only:true, pilot_date:$pilot_date, inspected_event_ids:$inspected_event_ids, nested_event_id:($nested_event_id | if . == "" then null else . end), irregular_event_id:($irregular_event_id | if . == "" then null else . end), candidate_import_permitted:false}' \
  > "$RESTRICTED/op-01-target-selection.json"
```

If both target IDs are empty, stop P04 after this operation. Record `source_reported_total=null` for the bounded search, `records_imported=0`, and the terminal reason “no target in the twelve inspected event exports; nested and irregular routes remain untested.” Do not run another search. This branch is a ready handoff for a reviewer to decide whether the existing failure-closed method is sufficient; it is not evidence that ESA lacks either route.

### Operation 2 — selected owner/material traversal and queue terminal tests

Run this operation only when at least one target ID exists. Pass one `--event-id` for `nested_event_id` when present and one for `irregular_event_id` when present, never more than two and never a duplicate. The selected-event route is bounded to 80 contribution owner pages and 150 all-route attachments per event. The attachment bound is checked before direct access probes; exceeding it fails closed.

```bash
EVENT_ARGS=()
if [[ -n "$NESTED_EVENT_ID" ]]; then
  EVENT_ARGS+=(--event-id "$NESTED_EVENT_ID")
fi
if [[ -n "$IRREGULAR_EVENT_ID" && "$IRREGULAR_EVENT_ID" != "$NESTED_EVENT_ID" ]]; then
  EVENT_ARGS+=(--event-id "$IRREGULAR_EVENT_ID")
fi

uv run "$SCRIPT" harvest-event \
  "${EVENT_ARGS[@]}" --max-events 2 \
  --max-contribution-pages 80 --max-attachments 150 \
  --dictionary "$DICT" \
  --expected-dictionary-sha256 61526b5d617a2af332aa3bb5d2a57b01dce60988c321d5c6deb807549fca076f \
  --probe-material-access \
  --timeout 45 --min-request-interval 0.5 --retries 2 \
  --protocol-commit "$PROTOCOL_COMMIT" \
  --output-path "$RESTRICTED/op-02-event-run.json" \
  --queue-output-path "$RESTRICTED/op-02-full-queue.json"
```

Do not pass `--download-pdfs`, `--secure-material-dir`, `--match-metadata`, or any OCR option. The operation may fetch at most two event exports, two event pages, 160 contribution owner pages, and 300 direct-material access probes in total. It never retains a response body in Git and never emits matching output. Require event/export count and stable-ID, owner/path, and export/static attachment reconciliation before using a queue. Any owner-page failure, missing export-declared-unprotected link, identity conflict, redirect, challenge, wrong media classification, or bound failure stops the operation and leaves all source totals null.

The output queue may contain unrelated PDF/non-PDF/access items. P04 resolves **at most one** nested queue item and **at most one** irregular/external queue item, selected by first occurrence in the full queue. Create one-item queue files in `$RESTRICTED` with `jq`; do not edit the full immutable queue:

```bash
if jq -e '[.items[] | select(.action == "inspect_public_subcontribution_route")] | length > 0' \
  "$RESTRICTED/op-02-full-queue.json" >/dev/null; then
  jq '{queue_schema_version, created_at, protocol_commit, diagnostic_only, items: ([.items[] | select(.action == "inspect_public_subcontribution_route")][0] | [.])}' \
    "$RESTRICTED/op-02-full-queue.json" > "$RESTRICTED/op-02-nested-queue.json"
fi
if jq -e '[.items[] | select(.action == "resolve_irregular_or_external_material")] | length > 0' \
  "$RESTRICTED/op-02-full-queue.json" >/dev/null; then
  jq '{queue_schema_version, created_at, protocol_commit, diagnostic_only, items: ([.items[] | select(.action == "resolve_irregular_or_external_material")][0] | [.])}' \
    "$RESTRICTED/op-02-full-queue.json" > "$RESTRICTED/op-02-irregular-queue.json"
fi
```

Only create the corresponding receipt/template/validation artifacts when the one-item queue exists. Use `receipt-templates` to create a content-free template, then fill one receipt from the actual terminal route. A nested receipt is valid only if it reports `route_enumerated_and_all_materials_terminal`, an identified operator, a 64-character `coverage_receipt_sha256`, and at least one observed material attachment ID or validated ESA attachment path. An irregular/external receipt is valid only if its terminal outcome is `text_extracted` or `manual_text_extracted`, it includes the queued attachment ID, operator, completion time, and `text_sha256_or_failure_reason`. Retain no source text, browser URL, cookie, redirect target, or private data.

Validate each one-item receipt exactly once:

```bash
if [[ -f "$RESTRICTED/op-02-nested-queue.json" ]]; then
  uv run "$SCRIPT" receipt-templates \
    --queue-path "$RESTRICTED/op-02-nested-queue.json" \
    --output-path "$RESTRICTED/op-02-nested-receipt-template.json"
  # Fill the template as the content-free receipt contract, then:
  uv run "$SCRIPT" validate-receipts \
    --queue-path "$RESTRICTED/op-02-nested-queue.json" \
    --receipt-path "$RESTRICTED/op-02-nested-receipt.json" \
    --output-path "$RESTRICTED/op-02-nested-receipt-validation.json"
fi

if [[ -f "$RESTRICTED/op-02-irregular-queue.json" ]]; then
  uv run "$SCRIPT" receipt-templates \
    --queue-path "$RESTRICTED/op-02-irregular-queue.json" \
    --output-path "$RESTRICTED/op-02-irregular-receipt-template.json"
  # Fill the template as the content-free receipt contract, then:
  uv run "$SCRIPT" validate-receipts \
    --queue-path "$RESTRICTED/op-02-irregular-queue.json" \
    --receipt-path "$RESTRICTED/op-02-irregular-receipt.json" \
    --output-path "$RESTRICTED/op-02-irregular-receipt-validation.json"
fi
```

A validation result with `coverage_complete=false`, an absent receipt, an unsupported-media outcome, or an access/parse failure is an incomplete terminal route and leaves coverage `null`; do not convert it into a no-match or retry the source operation. Queue validation is diagnostic and does not authorize matching, screening, or import.

## Gates supported and not supported

P04 can add bounded evidence only to:

- `G-LOCAL-HARVEST-COVERAGE`: explicit event export, nested queue, irregular queue, and terminal receipt reconciliation;
- `G-LOCAL-IDENTITY`: composite nested IDs and event/owner/attachment identity checks;
- `G-RETRIEVAL`: only the selected owner/material route and safe access classification;
- `G-COMPLETENESS`: only the declared twelve-event shape operation and one-item queue reconciliation; never source-wide completeness; and
- `G-FAILURE-BEHAVIOR`: failed-event, bound, access, and receipt failures remain null/incomplete.

It does not pass or establish `G-SOURCE-BOUNDARY`, `G-LOCAL-CANDIDATE-LOGIC`, `G-LOCAL-TAGGING`, `G-CONTROLLED-VOCABULARY`, `G-DATE-CONTROL`, or `G-LANGUAGE-CONTROL`. Existing P03 code/method evidence may be carried forward only by exact hash in the runtime campaign. P04's pilot-date label is not a date-control proof.

## Hard stops and terminal accounting

Stop the attempt without a new source request on: any nonzero CLI exit; a failed event in Operation 1; an HTTP 3xx/401/403/418/challenge; exhausted retryable status; timeout; malformed JSON/HTML; count/row mismatch; duplicate or conflicting identity; missing owner-page material; attachment bound overflow; queue ID mismatch; receipt failure; unexpected output collision; or any request to widen the event set. Do not retry a failed operation in this attempt.

Record every failed or unresolved source operation with `source_reported_total=null`, `records_retrieved=0` for the failed operation, and `records_imported=0`. A bounded set of successful event exports may record its native per-export `count=1` sum as an operation-unit count only; label it as such and never present it as an ESA population total. An empty `subContributions` list is an observed bounded shape, not an explicit source zero. Keep the full queue and all safe receipts outside the shared source packet until the immutable manifest/evidence index is created; then copy only safe hashes, counts, IDs, route paths, states, and logical secure references into the new P04 packet.

After cleanup of any optional manual/browser queue phase, verify no owned page remains and any shared lease is released before writing the terminal manifest. Update the runtime campaign once, preserve P01–P03, set `accepted_pilot_ids=[]`, and leave the campaign unaccepted. Run the shared validator and focused tests. Commit only the source-specific bundle; never edit shared integration files.
