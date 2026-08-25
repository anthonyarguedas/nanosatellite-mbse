# P03 execution plan — S-D04 Engineering Village

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


**Status:** source-free launch bundle; no live observation is made here. This plan is for the existing campaign `S-D04-C01-20260824T161325-0400` and its controller-authorized next technical attempt `S-D04-P03-<timestamp>`. It does not create a completed attempt, accept the source, run a final search, screen, or import records.

## Fixed accounting and scope

- The attempt has a **maximum of two campaign source operations**. This is not raised by the paired diagnostic implementation.
- **Operation 1** is exactly one corrected non-query route projection using `engineering_village_route_probe.py`.
- **Operation 2** is exactly one logical paired event, `P03-OP02-PAIRED-DIAGNOSTIC`. It contains two explicitly counted component requests, one Compendex request and one Inspec request, made sequentially by `engineering_village_paired_diagnostic.py`. The receipt records `campaign_source_operation_count=1`, `database_requests_planned=2`, and the performed request count. The two database requests are implementation components of the one predeclared paired event, not operations 3 and 4.
- The component calls use the existing local `search_compendex.py` and `search_inspec.py` adapters, one adapter-owned page at a time, with exactly `limit=1`, `max_pages=1`, `require_complete=false`, `search_mode=expert` (fixed by the wrappers), `timeout_seconds=45`, `page_delay_seconds=0.25`, `cdp_url=http://127.0.0.1:9222`, no target/result URL, and no fresh-browser flags. The runner retains only safe count/control/provenance metadata and discards returned records in memory; it never performs full retrieval or writes adapter JSON/CSV/RIS artifacts, screening, or import.
- Separate Compendex and Inspec selections, sources, row-provenance summaries, and exact totals are retained independently. A combined paired total is **not** inferred by adding two independent totals; the receipt records `paired=null` unless a future source-specific observation proves a combined total route. This is an operational diagnostic interpretation only and does not revise the paired source boundary or any query semantics.
- Use only the current nine query files as already drafted. P03 submits **only** `queries/B1.ev-expert.txt` for the bounded adapter diagnostic after operation 1 passes. A1, A2, A3, B2, BG1, BG2, BC1, and BT2 are not submitted.
- The diagnostic publication-date bound is lower-inclusive `2011-01-01` and upper-inclusive the runtime `PILOT_DATE`. The current adapter exposes year controls, so the runner passes `year_start=2011` and `year_end=PILOT_DATE.year` and records exact day precision as `untested`; it does not claim a day-precise source filter. This is a pilot-date diagnostic bound only, not P-001 or a final common cutoff.
- No language, publication-type, access, peer-review, venue, content-type, major-topic, or other prohibited limit is added. No controlled-vocabulary term, query cell, pair rule, source boundary, recall rule, completeness definition, or PRISMA accounting is changed.

## Gates and conditional transitions

1. Carry forward only the immutable construction/ownership evidence already listed by the campaign: `G-TRANSLATION-INTEGRITY` and the P02 `G-OWNED-PAGE` mechanics. They do not imply current source access.
2. Operation 1 must return a healthy stabilized projection, including the expected paired Expert route, expected title, paired Compendex/Inspec controls checked, query field, no access/login/challenge/syntax marker, and verified owned-page/target cleanup with the protected anchor unchanged. This supports the P03 `G-ROUTE-PROJECTION` decision. A nonzero exit, unhealthy receipt, or cleanup uncertainty ends the attempt before any source query.
3. Only after operation 1 passes, operation 2 runs once. The paired receipt must show both planned database requests and, on success, two performed requests, one each for `compendex` and `inspec`, with independent exact totals or an explicit native zero, selection mask/control evidence, and no retained records. This is diagnostic evidence for `G-ADAPTER-DIAGNOSTIC` and the count/control portion of `G-SOURCE-ACCESS`; it is not a completeness or final-source acceptance gate.
4. `G-PAIRED-PROVENANCE`, pagination, stable identity, RIS reconciliation, completeness, all nine query translations, thesaurus/indexed-term behavior, and `S-C01` remain untested because P03 stops before full retrieval. No gate is marked passed from a null, an adapter error, a retrieved-count fallback, or an unverified prefix.

A positive exact `0` is accepted only when the adapter reports the native zero state with exact-total and selected-database/control evidence. Any access, challenge, login, syntax, route, query-echo, control, total, pagination, provenance, export, browser, timeout, or cleanup discrepancy is `total=null`; no partial prefix is retained. There is no retry or same-tab reissue in P03.

## Source-free preflight

Run these checks before allocating the runtime attempt. They do not attach to Chrome or contact Engineering Village:

```bash
ROOT=/Users/antho/nanosatellite-mbse
TOOLS=/Users/antho/agent-tools

cd "$TOOLS/academic-research/skills/academic-search"
uv run pytest -q \
  tests/test_prisma_remediation.py \
  tests/test_prisma_complex_source_adapters.py
sha256sum \
  scripts/_engineering_village_search.py \
  scripts/search_compendex.py \
  scripts/search_inspec.py

cd "$ROOT"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  SLR/SLR1/scripts/test_engineering_village_route_probe.py \
  SLR/SLR1/scripts/test_engineering_village_paired_diagnostic.py
PYTHONDONTWRITEBYTECODE=1 python3 \
  SLR/SLR1/scripts/engineering_village_route_probe.py --help >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 \
  SLR/SLR1/scripts/engineering_village_paired_diagnostic.py --help >/dev/null
uv run SLR/SLR1/scripts/validate_search_infrastructure.py --mode pre-final
```

The current adapter implementation is the local pinned `engineering_village_search` implementation plus its two wrappers. The focused tests are implementation evidence only; no live claim follows from them.

## Runtime allocation and exact operation order

The owner/operator creates the attempt identifier once at runtime and never reuses an attempt directory. For an existing campaign, do not edit `campaign.json` or fabricate a manifest before live work; create the initial attempt packet/manifest from the shared campaign templates at runtime if the live phase is actually authorized.

```bash
ROOT=/Users/antho/nanosatellite-mbse
TOOLS=/Users/antho/agent-tools
ATTEMPT_ID="S-D04-P03-$(date +%Y%m%dT%H%M%S%z)"
PILOT_DATE="$(date +%F)"
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d04-engineering-village/pilots/$ATTEMPT_ID"
RESTRICTED="$ROOT/.searches/s-d04-engineering-village-restricted/$ATTEMPT_ID"
mkdir -p "$(dirname "$PACKET")" "$(dirname "$RESTRICTED")"
mkdir "$PACKET" "$RESTRICTED"

LEASE="$TOOLS/internet/skills/browser/scripts/run_with_browser_lease.py"
ROUTE="$ROOT/SLR/SLR1/scripts/engineering_village_route_probe.py"
PAIRED="$ROOT/SLR/SLR1/scripts/engineering_village_paired_diagnostic.py"
ADAPTER_DIR="$TOOLS/academic-research/skills/academic-search/scripts"
QUERY_B1="$ROOT/SLR/SLR1/searches/sources/s-d04-engineering-village/queries/B1.ev-expert.txt"
ROUTE_RECEIPT="$PACKET/op-01-route-projection.json"
PAIRED_RECEIPT="$PACKET/op-02-paired-diagnostic.json"
LEASE_RECEIPT="$PACKET/lease-receipt.json"

export ROOT TOOLS ATTEMPT_ID PILOT_DATE ROUTE PAIRED ADAPTER_DIR QUERY_B1
export ROUTE_RECEIPT PAIRED_RECEIPT

# The lease is the only browser allocation. It is the shared CfT endpoint,
# not a fresh browser/profile/port. The child commands are strictly serial.
caffeinate -dims uv run "$LEASE" \
  --owner "$ATTEMPT_ID" \
  --source engineering-village \
  --receipt "$LEASE_RECEIPT" \
  --wait 30 \
  --lease-timeout 600 \
  -- bash -ceu '
    set -euo pipefail

    # Operation 1: one owned page, one normal navigation, no query submit.
    uv run "$ROUTE" \
      --execute \
      --cdp-url http://127.0.0.1:9222 \
      --timeout-seconds 45 \
      --stabilization-interval-seconds 0.2 \
      --output-path "$ROUTE_RECEIPT"

    jq -e "
      .result.status == \"healthy\" and
      .result.observations_accepted == true and
      .ownership.owned_page_closed == true and
      .ownership.owned_target_disappeared == true and
      .ownership.baseline_pages_preserved == true and
      .ownership.baseline_target_set_preserved == true" \
      "$ROUTE_RECEIPT" >/dev/null

    # Fixed passive pacing between the two source operations.
    sleep 2

    # Operation 2: one paired event. The runner fixes limit=1/max-pages=1,
    # calls Compendex then Inspec once each, and retains no result records.
    uv run "$PAIRED" \
      --execute \
      --attempt-id "$ATTEMPT_ID" \
      --cdp-url http://127.0.0.1:9222 \
      --query-file "$QUERY_B1" \
      --pilot-date "$PILOT_DATE" \
      --timeout-seconds 45 \
      --adapter-page-delay-seconds 0.25 \
      --inter-database-delay-seconds 2 \
      --adapter-dir "$ADAPTER_DIR" \
      --output-path "$PAIRED_RECEIPT"
  '
```

After the child exits, verify the lease receipt reports successful release and cleanup before interpreting either source receipt. For a complete operation-2 diagnostic receipt, also verify:

```bash
jq -e "
  .result.status == \"complete\" and
  .result.count_control_evidence_complete == true and
  .accounting.campaign_source_operation_count == 1 and
  .accounting.campaign_source_operation_maximum == 1 and
  .accounting.database_requests_planned == 2 and
  .accounting.database_requests_performed == 2 and
  ([.database_requests[].database] | sort) == [\"compendex\", \"inspec\"] and
  .result.records_retained == 0" \
  "$PAIRED_RECEIPT" >/dev/null
```

The route receipt and paired receipt are create-only unique packet metadata. The current bounded adapter may perform its normal in-memory one-record RIS reconciliation, but the runner writes no adapter JSON/CSV/RIS artifact and retains no record. If an operation fails, preserve its receipt, leave totals null unless the native-zero rule was positively met, and stop. Only after verified browser cleanup/release may the owner create the immutable manifest/evidence index and update the existing campaign accounting; P03 must remain diagnostic, blocked/unaccepted unless a later authorized review says otherwise.

## Hard stops

Stop the phase without another source request on any lease acquisition/release or receipt failure; unexpected context/target state; anchor mutation; route/control/query-field/access/login/challenge/CAPTCHA/busy/service-error/syntax failure; adapter entry-point/load failure; nonzero adapter exit; output collision; timeout; missing/conflicting/null total; selected-database or provenance mismatch; or any attempt to paginate beyond the fixed first page, export beyond the adapter's one-record diagnostic reconciliation, retain a record prefix, screen, import, run another query, or run another source operation. Do not retry a failed database request, do not invoke the combined adapter in addition to the two component requests, and do not start a final search from this plan.
