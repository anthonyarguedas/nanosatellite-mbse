# P01 execution plan — S-D10 AIAA Aerospace Research Central

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


**State:** source-free launch plan only. P01 has not been allocated, no campaign/manifest exists yet, and no ARC request or current-interface observation has been made.

## Fixed scope and limits

- P01 is a diagnostic-only initial attempt. It performs no screening, candidate import, final-event creation, or PRISMA identification accounting.
- Use exactly one semantic query: [`queries/B1.aiaa-allfield.txt`](queries/B1.aiaa-allfield.txt). B1 is the non-pair `P AND M_H` partition. Do not substitute another query to obtain a convenient count.
- **Maximum source operations: 2.** Operation 1 is the required count-only health/controls operation. Operation 2 is conditional, bounded retrieval/export diagnostics for the same B1 query. No operation is reissued after failure in P01.
- Fixed P01 retrieval cap: **20 source records** (one ARC page). Run operation 2 only when operation 1 reports an exact positive total from 1 through 20 inclusive. A zero or a total above 20 is a valid reason not to run operation 2; it is not a failure and must not be replaced by another query.
- Do not invoke `--require-complete` in P01. The current adapter's complete contract fixes `--max-source-total 100`, two passes, exact dates, a 20-second timeout, zero page delay, a visible owned browser, and enough pages/limit to exhaust that cap. P01 is deliberately a smaller non-strict diagnostic and cannot claim completeness or report readiness.
- Use the pilot execution date as `PILOT_DATE` for `--date-end`. It is an explicitly labelled diagnostic upper bound, not P-001 or the final common cutoff.
- Global pacing: one attached sequential lease; no parallel source processes; wait 3 seconds between the two source operations if operation 2 is eligible. Same-tab busy reissue policy: zero retries. The adapter's finite passive readiness wait is bounded by `--timeout 20`; it never clicks, reloads, solves, or bypasses a challenge.

## Runtime allocation before source work

The source is brand new. Do not commit a campaign or completed attempt now and do not fabricate a source result. At runtime, before the lease or any source operation, set `RESTRICTED` to the approved restricted location outside this source packet and run this exact offline allocation block:

```bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d10-aiaa-arc"
: "${RESTRICTED:?Set RESTRICTED to the approved restricted diagnostic directory}"
NOW="$(date -u +%Y%m%dT%H%M%S%z)"
CAMPAIGN_ID="S-D10-C01-${NOW}"
ATTEMPT_ID="S-D10-P01-${NOW}"
PILOT_DATE="${NOW:0:4}-${NOW:4:2}-${NOW:6:2}"
PROTOCOL_COMMIT="$(git -C "$ROOT" rev-parse --verify HEAD)"
install -d -m 700 "$RESTRICTED"
python3 "$ROOT/SLR/SLR1/scripts/initialize_aiaa_arc_pilot.py" \
  --root "$ROOT" \
  --now "$NOW" \
  --protocol-commit "$PROTOCOL_COMMIT"
```

The source-specific initializer reads `SLR/SLR1/searches/templates/pilot-campaign.template.json` and `SLR/SLR1/searches/templates/pilot-manifest.template.json`, computes the current local protocol/dictionary fingerprints, creates the new `pilots/$ATTEMPT_ID/` directory, and writes one mutable pre-run manifest plus one `campaign.json`. It materializes the exact `S-D10`/`aiaa-arc` IDs, the frozen 12-gate catalog below, diagnostic-only flags, zero imported records, a zero-retry policy, and one initial attempt with `predeclared_maximum=2`; every gate has `status=untested` and empty evidence, and the manifest has no execution, check, artifact, source total, or bibliographic result. The schema-required campaign terminal object is only a pre-run allocation placeholder, not source evidence or a result, and is replaced after the attached phase. The scaffold is not sealed or checkpointed until the attached phase reaches a terminal outcome. The receipt and every operation output name must be new and absent; never pre-create the adapter output, its non-mergeable sidecar, a marker, or a native-export destination. The initializer is source-free and must not be run now.

After the attached phase, seal the manifest/evidence files only after it reaches a terminal outcome. Hash every immutable file into the campaign checkpoint, carry no evidence from another source, and record a blocked/failed/null outcome rather than a partial prefix when a gate fails.

Stable acceptance-gate IDs and P01's prospective evidence are:

| Gate | P01 evidence or disposition |
|---|---|
| `G-SOURCE-BOUNDARY` | Protocol boundary plus H-001 source-route health; not passed by documentation alone. |
| `G-QUERY-TRANSPORT` | OP-01 exact B1 cell, `field1=AllField`, `text1`, and retained route/query controls. |
| `G-FIELD-BOUNDARY` | OP-01 visible/current route and AllField control; otherwise `untested`/`blocked`. |
| `G-CONTROLLED-VOCABULARY` | No descriptor is used; current Keyword/indexed-term behavior remains `untested`. |
| `G-DATE-CONTROL` | OP-01 month/date parameters and visible date/control evidence under `PILOT_DATE`; not P-001. |
| `G-LANGUAGE-CONTROL` | No language filter is imposed; current native language behavior remains `untested`. |
| `G-CONTENT-CONTROL` | OP-01 all-content route/no convenience limit; current control behavior remains subject to live validation. |
| `G-RETRIEVAL` | OP-02 only, and only if OP-01 total is 1–20; otherwise remains `untested`. |
| `G-PAGINATION-CONTROL` | OP-01 first-page range/20-row control; one page cannot establish complete pagination. |
| `G-PAGE-IDENTITY` | OP-01 DOI-row evidence and OP-02 DOI/RIS reconciliation if reached; missing/duplicate/mismatched DOI fails. |
| `G-COMPLETENESS` | Explicitly `untested`: P01 never invokes strict complete mode. |
| `G-FAILURE-BEHAVIOR` | Safe null/zero, challenge/busy, output, and cleanup receipts from the attempted operation. |

## Shared browser health and lease

Before source work, the controller records a safe health preflight: the sole shared CfT service and one process/profile assertion, browser epoch and provenance, `127.0.0.1:9222` endpoint, protected broker anchor, adapter-owned-page baseline, AC/power state, process-scoped `caffeinate -dims`, and the actual Sleep/Wake result. A health, anchor, version, sleep, or profile/process failure is a hard stop before OP-01. Do not launch, restart, inspect, or configure a browser; do not acquire a second lease or use another endpoint/profile.

Run the complete attached phase, including both conditional operations and cleanup, only through this shape (substitute the runtime variables once). The `env` handoff is deliberate: variables in the controller shell are otherwise not guaranteed to exist in the attached child.

```bash
caffeinate -dims uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py \
  --owner "$ATTEMPT_ID" \
  --source aiaa-arc \
  --receipt "$PACKET/live-phase-receipt.json" \
  --wait 30 \
  --lease-timeout 300 \
  -- env \
    ROOT="$ROOT" PACKET="$PACKET" RESTRICTED="$RESTRICTED" \
    ATTEMPT_ID="$ATTEMPT_ID" PILOT_DATE="$PILOT_DATE" \
    bash -ceu '
set -euo pipefail
: "${ROOT:?ROOT was not handed to the attached child}"
: "${PACKET:?PACKET was not handed to the attached child}"
: "${RESTRICTED:?RESTRICTED was not handed to the attached child}"
: "${ATTEMPT_ID:?ATTEMPT_ID was not handed to the attached child}"
: "${PILOT_DATE:?PILOT_DATE was not handed to the attached child}"
ADAPTER="$ROOT/../agent-tools/academic-research/skills/academic-search/scripts/search_aiaa_arc.py"
QUERY_FILE="$PACKET/queries/B1.aiaa-allfield.txt"
QUERY="$(cat "$QUERY_FILE")"
OP1="$RESTRICTED/op-01-count-b1.json"
OP1_DIAGNOSTIC="${OP1%.json}.NON_MERGEABLE_FAILURE.json"
OP2="$RESTRICTED/op-02-retrieval-b1.json"
OP2_DIAGNOSTIC="${OP2%.json}.NON_MERGEABLE_FAILURE.json"

fail() {
  printf "P01 fail closed: %s\n" "$*" >&2
  exit 1
}
absent() {
  [[ ! -e "$1" && ! -L "$1" ]] || fail "path already exists: $1"
}
regular_file() {
  [[ -f "$1" && ! -L "$1" ]] || fail "expected a new regular file: $1"
}
marker_for() {
  printf "%s/.%s.ARC_COMMIT.json" "$(dirname "$1")" "$(basename "$1")"
}

for path in \
  "$OP1" "$OP1_DIAGNOSTIC" "$(marker_for "$OP1")" \
  "$OP2" "$OP2_DIAGNOSTIC" "$(marker_for "$OP2")"; do
  absent "$path"
done

# The adapter non-strict main path intentionally emits a record-free
# diagnostic sidecar. Validate only its aggregate source-run proof; never read
# a bibliographic prefix from the sidecar.
validate_diagnostic() {
  local mode="$1"
  local path="$2"
  regular_file "$path" || return 1
  jq -e --arg mode "$mode" --arg query "$QUERY" '\''
    def exact_int: (type == "number") and (floor == .) and (. >= 0);
    . as $root
    | ($root.output_metadata) as $meta
    | ($meta.source_run_accounting) as $run
    | (
        ($root | type == "object")
        and ($meta | type == "object")
        and ($run | type == "object")
        and ($root.diagnostic_kind == "NON_MERGEABLE_FAILURE")
        and ($root.private_diagnostic == true)
        and ($root.do_not_merge == true)
        and ($root.merge_eligible == false)
        and ($root.publication_state == "normalized_output_not_published")
        and ($root.query == $query)
        and (($root.results | type) == "array")
        and (($root.results | length) == 0)
        and ($root.normalized_results_omitted == true)
        and ($root.normalized_csv_omitted == true)
        and ($root.native_export_omitted == true)
        and (($root.total | exact_int))
        and ($root.observed_total == $root.total)
        and ($root.observed_pages == 1)
        and ($root.observed_results | exact_int)
        and ($root.pages_retrieved == 1)
        and ($meta.status == "non_mergeable_diagnostic")
        and ($meta.merge_eligible == false)
        and ($meta.publication_precommit_eligible == false)
        and ($meta.records_omitted_for_diagnostic == true)
        and ($meta.source_total == $root.total)
        and ($meta.total_is_exact == true)
        and ($meta.count_only == ($mode == "count"))
        and ($meta.execution_completion_status ==
          (if $mode == "count" then "count_only" else "partial" end))
        and ($run.source_total == $root.total)
        and ($run.total_is_exact == true)
        and ($run.completion ==
          (if $mode == "count" then "count_only" else "partial" end))
        and ($run.count_only == ($mode == "count"))
        and ($run.pages_retrieved == 1)
        and ($run.records_retained | exact_int)
        and ($run.source_entries_retrieved | exact_int)
        and ($run.source_document_ids_seen | exact_int)
        and ($run.export_preflight_records | exact_int)
        and (
          ($mode == "count"
            and $root.observed_results == 0
            and $run.records_retained == 0
            and $run.source_entries_retrieved == 0
            and $run.export_preflight_records == 0
            and $run.source_document_ids_seen ==
              (if $root.total < 20 then $root.total else 20 end))
          or
          ($mode == "retrieval"
            and $root.observed_results == $run.records_retained
            and $run.records_retained <= $root.total
            and $run.source_entries_retrieved == $root.total
            and $run.source_document_ids_seen == $root.total
            and $run.export_preflight_records == 1
            and ($run.client_exact_date_exclusions | exact_int)
            and $run.records_retained + $run.client_exact_date_exclusions == $root.total)
        )
      )
  '\'' "$path" >/dev/null
}

OP1_STATUS=0
uv run "$ADAPTER" \
  --query "$QUERY" \
  --date-start 2011-01-01 --date-end "$PILOT_DATE" \
  --limit 20 --max-pages 1 --passes 1 \
  --timeout 20 --page-delay-seconds 0 \
  --max-source-total 100 --count-only \
  --cdp-url http://127.0.0.1:9222 \
  --output-path "$OP1" || OP1_STATUS=$?
(( OP1_STATUS == 0 )) || fail "OP-01 count-only invocation exited $OP1_STATUS"
absent "$OP1"
absent "$(marker_for "$OP1")"
validate_diagnostic count "$OP1_DIAGNOSTIC" || fail "OP-01 sidecar is not an exact count-only diagnostic"
TOTAL="$(jq -er '\''.total | select(type == "number" and floor == . and . >= 0)'\'' "$OP1_DIAGNOSTIC")"

if (( TOTAL >= 1 && TOTAL <= 20 )); then
  sleep 3
  OP2_STATUS=0
  uv run "$ADAPTER" \
    --query "$QUERY" \
    --date-start 2011-01-01 --date-end "$PILOT_DATE" \
    --limit "$TOTAL" --max-pages 1 --passes 1 \
    --timeout 20 --page-delay-seconds 0 \
    --max-source-total 100 \
    --cdp-url http://127.0.0.1:9222 \
    --output-path "$OP2" || OP2_STATUS=$?
  # A successful bounded non-count-only diagnostic returns 1 from main because
  # strict publication was not requested. That status is accepted only with
  # the expected create-only, record-free aggregate sidecar.
  (( OP2_STATUS == 1 )) || fail "OP-02 invocation had unexpected exit $OP2_STATUS"
  absent "$OP2"
  absent "$(marker_for "$OP2")"
  validate_diagnostic retrieval "$OP2_DIAGNOSTIC" || \
    fail "OP-02 did not produce the expected record-free diagnostic sidecar"
else
  printf "OP-02 not run: exact B1 total=%s is outside the fixed 1..20 pilot cap.\n" "$TOTAL" >&2
fi
'
```

The command is an execution skeleton, not a live claim. `ROOT`, `PACKET`, `RESTRICTED`, `ATTEMPT_ID`, and `PILOT_DATE` are both set at allocation and handed explicitly to the child above. `--cdp-url` is the only endpoint flag. Do not add `--fresh-browser`, `--headless`, `--chrome-executable`, `--target-id`, or `--result-url`: the normal shared route creates its own page in the shared context. If the adapter itself proves that the shared endpoint has multiple ambiguous contexts or cannot create/close its owned page, stop and record that technical blocker; do not select a target by position or invent a result URL.

## Operation 1 — count-only B1 health and visible controls

`OP-01-COUNT-B1` is the first and required source operation. The exact input is the bytes of `queries/B1.aiaa-allfield.txt`, submitted as `field1=AllField`/`text1` by the adapter. It is count-only and must retain no records. On a successful count-only invocation, the adapter returns exit 0 and creates only `op-01-count-b1.NON_MERGEABLE_FAILURE.json`; derive that path from `OP1` by removing its `.json` suffix before appending `.NON_MERGEABLE_FAILURE.json`. Validate that regular, non-symlink sidecar's diagnostic kind, `count_only` completion, exact total, and record-free/aggregate accounting before reading `.total` to decide whether OP-02 is eligible.

The operation must check, in the current rendered UI and safe adapter receipt where available:

- ARC normal `/action/doSearch` route and no unsafe redirect;
- exact AllField query/control retention, with no silent rewrite or dropped `text1`;
- lower date `2011-01-01` and runtime diagnostic upper date, including the source month mapping;
- all-content/default access state without a discovery content/publication restriction;
- visible Relevance ordering and fixed page size 20;
- one exact rendered `Search Results (N)` total, first-page range, hydrated DOI selectors, and the native explicit-zero state if `N=0`; and
- no challenge, login/access state, syntax error, generic error, missing/conflicting total, short/duplicate DOI page, or output collision.

A successful exact native zero is `0`. A positive OP-01 total is source-reported and is not a retrieved or complete count. Any failure is `null`, zero retrieved records, no import, and a terminal stop. Do not run OP-02 after a null, challenge, busy, syntax, route, control, total, range, or DOI-row failure.

## Operation 2 — conditional bounded retrieval/export diagnostic

Run `OP-02-RETRIEVAL-B1` only when OP-01 has an exact positive total from 1 through 20 and all required health/route/control checks passed. Use the same query and date bound, `--limit TOTAL`, one page, one pass, the same shared endpoint, and no strict flag. The normal ARC adapter's visible per-record Tools → Download citation → RIS flow is the export diagnostic; it must reconcile each returned RIS record one-to-one to the rendered DOI sequence. The successful non-count-only, non-strict adapter path intentionally writes only the create-only record-free `op-02-retrieval-b1.NON_MERGEABLE_FAILURE.json` sidecar and exits 1 because strict publication was not requested. The command captures that bounded exit and accepts only exit 1 plus the expected sidecar's `execution_completion_status=partial`, exact source total, source-entry/DOI/export aggregate evidence, and empty `.results`; it never accepts or reads a bibliographic prefix. The normalized output, commit marker, and native directory must remain absent. Do not force `--require-complete`.

Stop immediately, without a retry or a fallback query, on any other exit/sidecar outcome, changed total/order/range/control, page shortfall, missing/duplicate DOI, record-route mismatch, export challenge/access page, non-RIS or malformed output, DOI/RIS mismatch, timeout, output collision, or any owned-page/anchor/lease cleanup failure. Keep `total=null` for every such failed operation and retain no prefix. A result count of 0 is not inferred from an error, and no diagnostic sidecar permits import.

## Terminal cleanup and checkpoint

After the attached child exits, the controller verifies the immutable lease receipt says the lease was acquired and released, release verification succeeded, the broker anchor was preserved, the adapter-owned page(s) were closed, and no source writer remains. A user stop is `cancelled`, not a provider failure; unresolved cleanup keeps supervision active and blocks checkpoint completion. Only then write the sanitized manifest, evidence index, and campaign checkpoint with exact hashes. Preserve unaffected `untested`/passed/failed gate states according to the shared campaign rules; do not self-accept this brand-new source.

P01's smallest next action after a clean offline preflight is the one bounded attached phase above. Any need to change query semantics, source/field boundary, date/language/content limits, identity rule, pair rule, or completeness/accounting rule is a `human_methodological` decision and is not made by this plan.
