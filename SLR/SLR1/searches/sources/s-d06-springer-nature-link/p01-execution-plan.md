# S-D06 P01 execution plan — Springer Nature Link

> **Current validation policy:** Follow the [live-first source-pilot policy](../../live-first-validation-policy.md). It supersedes any broader offline-suite prerequisite below: run only the minimum launch gate, inspect failures on the real owned page, patch technical defects immediately, and retest live after minimal changed-path checks.


**Status:** source-free launch plan; no attempt has been run. The controller creates the initial campaign and manifest at runtime. This plan is diagnostic-only and does not authorize screening, candidate import, a final event, or a native CSV claim.

## Fixed scope and bounds

- **Attempt:** create `S-D06-P01-<YYYYMMDDThhmmss-offset>` once at runtime from the local clock. Do not reuse an ID. Create campaign `S-D06-C01-<same timestamp>` for this brand-new source.
- **Maximum adapter invocations/source operations:** 4, strictly serial: health count, A1 count, native-zero count, and conditional A1 complete diagnostic. The fourth invocation is not made unless the A1 count is a positive total at or below **40**.
- **Maximum source navigation under operation 4:** at most two rendered search pages per pass, two ordered passes, and at most 40 exact canonical detail pages. No export request.
- **Source and field:** full Springer Nature Link normal rendered search, Link Keywords, through `search_springer_link.py`; no content, access, subject, brand, venue, or supplementary-file facet.
- **Date/language:** `--date-start 2011-01-01 --date-end "$PILOT_DATE"` with `--language En` on every operation. `$PILOT_DATE` is the actual pilot execution date and is a diagnostic bound only, never `P-001` or a final cutoff.
- **Ordering/page controls:** `--sort relevance`, fixed adapter page size 20, `--max-pages 1` for count operations, and a calculated `ceil(total/20)` for operation 4.
- **Pacing/waits:** acquire the lease with `--wait 30 --lease-timeout 600`; use `--timeout 90` and `--page-delay-seconds 1`; sleep 3 seconds between completed adapter invocations. The global Springer pacing decision is “one serialized phase, three seconds between operations, no automatic same-tab busy reissue.” The adapter's passive challenge wait is bounded by its 90-second timeout; no challenge-solving or retry is permitted.
- **Outputs:** create a unique attempt directory and a unique `restricted/` output directory at runtime. Count-only base paths produce the adapter's `.NON_MERGEABLE_DIAGNOSTIC.json` sidecars. Operation 4, if successful, produces only its strict JSON and terminal `.SPRINGER_COMMIT.json` marker. The lease receipt is a new path in the attempt directory. Do not pre-create any output, marker, or receipt.
- **No native CSV:** do not pass `--native-csv-output-path`. Strict complete mode rejects it, and the current adapter's native schema is not pinned or reconciled.

## Offline preflight (before a lease)

Run from the isolated `agent-tools` worktree and do not contact Springer:

```bash
cd "$HOME/agent-tools/academic-research/skills/academic-search"
uv run pytest -q \
  tests/test_search_springer_link.py \
  tests/test_output_transaction_safety.py \
  tests/test_browser_challenge_waits.py
uv run scripts/search_springer_link.py --help
```

The focused test must exercise the current adapter's URL/control construction, exact rendered-page reconciliation, native-zero versus challenge failure, canonical identity, strict complete contract, and create-only/no-clobber behavior. `--help` must return successfully without opening Chrome. Record the test command and immutable script/test hashes in the runtime manifest/evidence index.

## Runtime bootstrap (required; do not fabricate it now)

The source packet currently has no `campaign.json` and no pilot manifest because this is a brand-new source. Before any source operation, the controller must:

1. set `ROOT="$(git rev-parse --show-toplevel)"`, `STAMP="$(date +%Y%m%dT%H%M%S%z)"`, `ATTEMPT_ID="S-D06-P01-$STAMP"`, and `CAMPAIGN_ID="S-D06-C01-$STAMP"`; reject a collision and never edit an existing attempt;
2. create `SLR/SLR1/searches/sources/s-d06-springer-nature-link/pilots/$ATTEMPT_ID/restricted/` and reserve the new receipt path;
3. instantiate a fresh campaign from `SLR/SLR1/searches/templates/pilot-campaign.template.json`, not from another source or an example campaign: set the new IDs, task `S-D06`, source `springer-nature-link`, method `direct`, current protocol/dictionary fingerprints, `diagnostic_only=true`, zero screening/import, one initial attempt, four-operation maximum, zero automatic retries, and all 12 required catalog gates initially `untested`;
4. instantiate `manifest.json` from `SLR/SLR1/searches/templates/pilot-manifest.template.json`, set the same new IDs, source/interface, current protocol commit, and diagnostic-only flags, and leave its executions/checks/artifacts empty until each operation actually completes; and
5. validate the instantiated schema shape before source work, then checkpoint only actual operation evidence and hashes. The initial campaign must not contain fabricated totals, passed gates, completed operations, or historical attempts.

The runtime campaign's required gate catalog is:

`G-SOURCE-BOUNDARY`, `G-QUERY-TRANSPORT`, `G-FIELD-BOUNDARY`, `G-CONTROLLED-VOCABULARY`, `G-DATE-CONTROL`, `G-LANGUAGE-CONTROL`, `G-CONTENT-CONTROL`, `G-RETRIEVAL`, `G-PAGINATION-CONTROL`, `G-PAGE-IDENTITY`, `G-COMPLETENESS`, `G-FAILURE-BEHAVIOR`.

## Exact inputs

```bash
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d06-springer-nature-link"
PILOT="$PACKET/pilots/$ATTEMPT_ID"
OUT="$PILOT/restricted"
ADAPTER="$HOME/agent-tools/academic-research/skills/academic-search/scripts/search_springer_link.py"
LEASE="$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py"
Q_B1="$PACKET/queries/B1.springer-link-keywords.txt"
Q_A1="$PACKET/queries/A1.springer-link-keywords.txt"
Q_ZERO="$PACKET/diagnostics/native-zero-control.springer-link-keywords.txt"
PILOT_DATE="$(date +%F)"
RECEIPT="$PILOT/live-phase-receipt.json"
OP1="$OUT/op-01-health-b1.json"
OP2="$OUT/op-02-a1-transport.json"
OP3="$OUT/op-03-native-zero.json"
OP4="$OUT/op-04-a1-complete.json"
```

`Q_B1` and `Q_A1` are the exact UTF-8 packet files. `Q_ZERO` is a non-normative, impossible-marker control only; it is not a review concept, partition, or candidate query.

## Ordered attached live phase

Run the whole phase, including health, all conditional source work, and cleanup, through exactly one shared lease. Use an attached trusted local runner; do not launch Chrome, configure a profile, use another port, or use a fresh browser:

```bash
caffeinate -dims uv run "$LEASE" \
  --owner "$ATTEMPT_ID" \
  --source springer-nature-link \
  --receipt "$RECEIPT" \
  --wait 30 \
  --lease-timeout 600 \
  -- bash -ceu '
    set -euo pipefail

    run_count() {
      local query_file="$1" output_path="$2"
      uv run "'$ADAPTER'" \
        --query "$(cat "$query_file")" \
        --date-start 2011-01-01 --date-end "'$PILOT_DATE'" \
        --language En --sort relevance \
        --limit 20 --max-pages 1 --passes 1 \
        --timeout 90 --page-delay-seconds 1 \
        --count-only \
        --cdp-url http://127.0.0.1:9222 \
        --output-path "$output_path"
    }

    # OP1: browser/source health and a short valid review query.  A rendered
    # native zero is a successful health observation; null/error is a stop.
    run_count "'$Q_B1'" "'$OP1'"
    sleep 3

    # OP2: the exact A1 translation, Link Keywords transport, English, and
    # diagnostic date controls.  Stop unless the count-only artifact is exact.
    run_count "'$Q_A1'" "'$OP2'"
    sleep 3

    # OP3: one safe source-native explicit-zero control.  Stop if the adapter
    # cannot prove Link's visible no-results state; never reinterpret a blank,
    # challenge, or error page as zero.
    run_count "'$Q_ZERO'" "'$OP3'"
    sleep 3

    # OP4: only a bounded identity/pagination/completeness diagnostic.  The
    # count is read from the adapter's immutable count-only sidecar, not from
    # memory or a partial page.
    # The adapter inserts the diagnostic suffix before `.json`.
    OP2_DIAGNOSTIC="'${OP2%.json}.NON_MERGEABLE_DIAGNOSTIC.json'"
    test -f "$OP2_DIAGNOSTIC"
    TOTAL="$(jq -er 'select(.diagnostic_kind == "NON_MERGEABLE_SPRINGER_DIAGNOSTIC" and .merge_eligible == false and (.results | length) == 0) | .total | numbers' "$OP2_DIAGNOSTIC")"
    if (( TOTAL >= 1 && TOTAL <= 40 )); then
      PAGES=$(( (TOTAL + 19) / 20 ))
      uv run "'$ADAPTER'" \
        --query "$(cat "'$Q_A1'")" \
        --date-start 2011-01-01 --date-end "'$PILOT_DATE'" \
        --language En --sort relevance \
        --limit "$TOTAL" --max-pages "$PAGES" --passes 2 \
        --timeout 90 --page-delay-seconds 1 \
        --require-complete \
        --cdp-url http://127.0.0.1:9222 \
        --output-path "'$OP4'"
    else
      printf 'OP4 not run: exact A1 count %s is outside the fixed pilot cap 1..40.\n' "$TOTAL" \
        > "'$PILOT'/op-04-not-run.txt"
    fi
  '
```

The quoted paths above are illustrative expansions from the runtime variables; the controller must substitute the one immutable `STAMP` before invoking the phase. The command has no retry loop. The adapter creates and closes only its owned page. The lease receipt must show acquisition, pre/post browser health, source actions, target cleanup, and verified release before any result is interpreted.

## Gate mapping and transitions

| Operation | Exact input/mode | Gates it can support | Transition |
| --- | --- | --- | --- |
| OP1 | `B1`, count-only, `En`, diagnostic dates, relevance | `G-SOURCE-BOUNDARY`; preliminary `G-QUERY-TRANSPORT`; `G-FAILURE-BEHAVIOR` for rendered access/zero distinction | Run first. Any lease/browser/source/challenge/control/total failure stops all source work. |
| OP2 | `A1`, count-only, same English/date controls | `G-QUERY-TRANSPORT`, `G-FIELD-BOUNDARY`, `G-DATE-CONTROL`, `G-LANGUAGE-CONTROL`, and the no-facet `G-CONTENT-CONTROL` boundary | Run only after OP1. `total` must be a nonnegative exact rendered total; `null` stops. |
| OP3 | non-normative native-zero marker, count-only | `G-FAILURE-BEHAVIOR` only if Link's explicit native no-results state is positive and consistent | Run only after OP2. Expected `total=0`; any other result is `null`/failure and stops. |
| OP4 | `A1`, exact total, `--require-complete`, two passes, no CSV | `G-RETRIEVAL`, `G-PAGINATION-CONTROL`, `G-PAGE-IDENTITY`, `G-COMPLETENESS` | Run only when OP2 `total` is 1..40. If 0 or >40, record the declared not-run condition; do not substitute another query. |

`G-CONTROLLED-VOCABULARY` is intentionally untested by this minimal sequence. A P01 cannot accept the source guideline by itself; it hands the controller the exact remaining gate status. Pair-bearing expansion cells are likewise not submitted in P01.

## Hard stops and terminal accounting

Stop the current source operation and do not reissue it on any of:

- missing/unhealthy shared CfT epoch, profile/process assertion, broker anchor, power/sleep check, lease, receipt, or owned-page cleanup/release;
- login, CAPTCHA, client challenge, access denial, or persistent busy state; only the declared finite passive wait is allowed, and no automatic same-tab busy reissue is authorized;
- query rewrite, missing exact echo, wrong Link Keywords boundary, dropped/changed English or date control, changed sort, prohibited facet, malformed source state, conflicting totals, or native-zero ambiguity;
- stale/short page, range/Next arithmetic mismatch, duplicate/missing canonical path, detail-route/title/abstract parsing mismatch, ordered-pass drift, unresolved exact date, source cap, or incomplete traversal;
- nonzero adapter exit or any output/receipt collision. Never delete or overwrite a create-only artifact to recover.

On any stop, preserve `total=null` except for a positively reconciled native zero, set `records_retrieved=0` for the failed operation, stop source writing, and record the narrow terminal category (`access_blocked`, `provider_failure`, `technical`, or `cancelled`) in the manifest/campaign. A user stop is `cancelled`, not a provider failure. Verify owned-page closure, broker-anchor preservation, and lease release before ending supervision. No pilot result is screened or imported.

After cleanup, create the immutable evidence index and final manifest from actual files, hash each operation sidecar/strict output and the lease receipt, update the campaign checkpoint, and run the shared validator. Do not self-accept the campaign or edit `TASKS.md`, `search-log.md`, any protocol, dictionary, crosswalk, schema, or another source packet.
