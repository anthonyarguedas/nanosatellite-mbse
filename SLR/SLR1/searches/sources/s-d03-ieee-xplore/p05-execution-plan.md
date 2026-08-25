# P05 execution plan — IEEE Xplore

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


**Status:** source-free launch bundle for the existing `S-D03-C01` campaign. This plan is diagnostic only and is governed by `D-TECH-NEXT-P05`. It adds no attempt record before runtime, makes no live claim, preserves the review owner's separately recorded `D-METHOD-NEAR6` authorization, and does not rerun P01–P04 work.

## Fixed scope and bounds

- Preserve `campaign.json`, the immutable P01–P04 attempts, the authorized `G-NEAR-METHOD` decision, the current dictionary/protocol fingerprints, the exact nine query files, and `translation-spec.json`.
- Allocate exactly one new runtime attempt, `S-D03-P05-<YYYYMMDDThhmmss-offset>`, as `controller_technical`. The complete phase has a maximum of **four source operations**, in the order below. There are no retries or alternate queries.
- Use only `queries/A1.ieee-query.txt`, byte-for-byte, for P05 source operations. Do not use the P03 split/control files and do not submit A2, A3, B1, B2, BG1, BG2, BC1, or BT2 again. No NEAR/6 diagnostic, S-C01 work, screening, import, export, or final event is in scope.
- Set `PILOT_DATE` once at runtime to the actual local calendar date (the scheduled launch date is `2026-08-25`) and derive `PILOT_YEAR` from it. The visible IEEE publication-year diagnostic is **2011 through `PILOT_YEAR` inclusive**. This is an execution-date diagnostic bound only, never `P-001`, a final cutoff, or a discovery restriction adopted by the review.
- A source-reported total is retained only after the adapter's exact rendered query/control echo and total invariant succeeds. A native rendered no-results page is `0`; access, challenge, busy, source, control, parser, or reconciliation failure is `null`, never zero. All operations retain zero records in review storage; operation 4's restricted raw records are not screening or import input.
- The Language probe inventories controls only. It must not select, check, apply, or infer an English limit. The conservative disposition remains no discovery language restriction and screening-time full-report language determination unless a later authorized method establishes otherwise.

## Required runtime lifecycle

Create the attempt ID and all destinations at runtime, after source-free preflight and before the lease. Do not pre-create output or receipt files and do not reuse a path:

```bash
ROOT=/Users/antho/nanosatellite-mbse
STAMP="$(date '+%Y%m%dT%H%M%S%z')"
ATTEMPT_ID="S-D03-P05-$STAMP"
PILOT_DATE="$(date '+%F')"
PILOT_YEAR="${PILOT_DATE%%-*}"
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d03-ieee-xplore/pilots/$ATTEMPT_ID"
RESTRICTED="$ROOT/.searches/s-d03-ieee-xplore-restricted/$ATTEMPT_ID"
mkdir -p "$PACKET" "$RESTRICTED"

LEASE=/Users/antho/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py
ADAPTER=/Users/antho/agent-tools/academic-research/skills/academic-search/scripts/search_ieee_xplore.py
PROBE="$ROOT/SLR/SLR1/scripts/ieee_language_control_probe.py"
Q_A1="$ROOT/SLR/SLR1/searches/sources/s-d03-ieee-xplore/queries/A1.ieee-query.txt"
LIVE_RECEIPT="$PACKET/browser-lease-receipt.json"
OP1="$RESTRICTED/op-01-year-a1.json"
OP2="$RESTRICTED/op-02-content-a1.json"
OP3="$RESTRICTED/op-03-language-control.json"
OP4="$RESTRICTED/op-04-bounded-completeness-a1.json"
```

The attached trusted local runner is the existing adapter/probe command under the one lease below. It must not launch Chrome, choose a profile, change a port, or acquire another lease. The only browser endpoint is exactly `http://127.0.0.1:9222`; the adapter and probe each create and close one owned page. Use no `--fresh-browser`, `--headless`, `--chrome-executable`, or alternate `--target-id`.

Before the four source operations, the controller must complete the shared browser version/epoch, protected-anchor, power/sleep, pacing, and target health preflight. After them, it must verify owned-page cleanup, anchor preservation, power/sleep, and verified lease release. A challenge or busy state is classified and stopped; neither is solved, bypassed, reissued, or escaped by a new page/profile/browser.

## Exactly four conditional source operations

Every row is one source operation. Run the next row only when the preceding row has a healthy exact result; otherwise stop and record later rows as blocked/not run. The adapter's finite readiness polling is internal to its one invocation and is not a source retry.

| Order | Gate and operation | Exact input and flags | Pass condition and transition |
|---|---|---|---|
| 1 | `G-YEAR-CONTROL` — visible year control | Adapter `$ADAPTER`; `--query "$(cat "$Q_A1")"`; `--year-start 2011 --year-end "$PILOT_YEAR"`; `--limit 10 --max-pages 1 --count-only`; `--timeout 60 --page-delay-seconds 1 --cdp-url http://127.0.0.1:9222 --output-path "$OP1"` | Exact A1 echo, visible year application/readback, exact numeric total, Relevance, no records, and verified cleanup. A native zero does not prove a usable dependent control and stops P05. On success, run operation 2. |
| 2 | `G-CONTENT-CONTROL` — visible multiple content type control | Adapter with the exact same A1/year/count-only flags and `--content-types Journals Conferences`, output `$OP2` | Exact A1/year/content echo, visible Journals-plus-Conferences selection/application, exact numeric total, no records, and verified cleanup. Do not adopt the content restriction. A native zero is recorded as zero but cannot support the language or completeness transition. On success with a nonzero total, run operation 3. |
| 3 | `G-LANGUAGE-CONTROL` — rendered Language inventory | Review-specific `$PROBE --execute --query "$(cat "$Q_A1")" --year-start 2011 --year-end "$PILOT_YEAR" --content-type Journals --content-type Conferences --timeout 60 --poll-interval 0.2 --cdp-url http://127.0.0.1:9222 --output-path "$OP3"` | The probe's one owned page must show exact query/year/content route state and an unambiguous visible Language facet with its option count, exactly one visible English option, and at most one Apply control. It must report `language_selection_attempted=false` and `english_limit_applied=false`. It never selects English. Challenge, busy, missing/ambiguous controls, inherited language selection, or projection failure stops P05. On success, run operation 4 if its bounded total rule permits. |
| 4 | `G-COMPLETENESS` — one bounded exact-A1 capture | Read the exact operation-2 total from `$OP2`. If `TOTAL` is an integer in **1..40**, set `PAGES=$(( (TOTAL + 9) / 10 ))` and invoke the adapter once with exact A1, `--year-start 2011 --year-end "$PILOT_YEAR" --content-types Journals Conferences --limit "$TOTAL" --max-pages "$PAGES" --page-size 10`; use `--timeout 60 --page-delay-seconds 1 --detail-delay-seconds 1 --cdp-url http://127.0.0.1:9222 --output-path "$OP4"`. | Exact control/total stability, complete rendered pagination, nonempty unique article-number identities, matching card/range/total accounting, matching rendered detail/title reconciliation, and verified cleanup. If `TOTAL=0` or outside 1..40, do not issue an adaptive query: record this bounded completeness gate as not run/blocked. This one pass is diagnostic evidence only; it does not select a final capture method or establish two-pass equivalence. |

The operation-4 adapter output is restricted and must not be copied to a candidate register, screening store, merge input, or final event. The controller records its safe aggregate outcome and restricted path in the runtime manifest/evidence index only after the child exits.

## Lease command and serial pacing

Run the four rows sequentially inside one complete lease. The controller supplies the actual runtime variables above and the unique `$LIVE_RECEIPT`; no adapter invocation may be detached or run outside this child:

```bash
caffeinate -dims uv run "$LEASE" \
  --owner "$ATTEMPT_ID" \
  --source ieee-xplore \
  --receipt "$LIVE_RECEIPT" \
  --wait 30 \
  --lease-timeout 900 \
  -- bash -ceu '
    set -euo pipefail
    run_count() {
      query_file="$1"; output="$2"; shift 2
      uv run "'"$ADAPTER"'" \
        --query "$(cat "$query_file")" \
        --timeout 60 --page-delay-seconds 1 --detail-delay-seconds 1 \
        --cdp-url http://127.0.0.1:9222 --output-path "$output" "$@"
    }

    run_count "'"$Q_A1"'" "'"$OP1"'" \
      --year-start 2011 --year-end "'"$PILOT_YEAR"'" \
      --limit 10 --max-pages 1 --count-only
    sleep 3

    run_count "'"$Q_A1"'" "'"$OP2"'" \
      --year-start 2011 --year-end "'"$PILOT_YEAR"'" \
      --content-types Journals Conferences \
      --limit 10 --max-pages 1 --count-only
    sleep 3

    uv run "'"$PROBE"'" --execute \
      --query "$(cat "'"$Q_A1"'")" \
      --year-start 2011 --year-end "'"$PILOT_YEAR"'" \
      --content-type Journals --content-type Conferences \
      --timeout 60 --poll-interval 0.2 \
      --cdp-url http://127.0.0.1:9222 --output-path "'"$OP3"'"
    sleep 3

    TOTAL="$(jq -er '.total | numbers' "'"$OP2"'")"
    if (( TOTAL >= 1 && TOTAL <= 40 )); then
      PAGES=$(( (TOTAL + 9) / 10 ))
      run_count "'"$Q_A1"'" "'"$OP4"'" \
        --year-start 2011 --year-end "'"$PILOT_YEAR"'" \
        --content-types Journals Conferences \
        --limit "$TOTAL" --max-pages "$PAGES" --page-size 10
    else
      printf 'G-COMPLETENESS not run: operation-2 total outside 1..40.\n' >&2
    fi
  '
```

The wrapper's one `--receipt` is new for this attempt. The four output paths are distinct and create-only. `sleep 3` is the predeclared serial pacing; there is no retry after a nonzero exit. If the wrapper or any child exits nonzero, preserve all null/zero distinctions, stop immediately, and do not run a later row.

## Hard stops and runtime checkpoint

Stop source writing immediately on lease acquisition/release, browser epoch/version, anchor, power/sleep, target ownership, output collision, query rewrite, missing/changed control, challenge/login, busy/rate-limit, service error, null/unreconciled total, parser/selector error, duplicate/missing identity, detail mismatch, short/stale page, changed pagination total, incomplete cleanup, or nonzero child exit. Do not reinterpret a failure as zero and do not retain/import a partial prefix.

After verified release, create the immutable `manifest.json`, `observations.md`, and `evidence-index.json` under `$PACKET` from the safe aggregate outcomes and the restricted inventory. Bind the runtime attempt ID and hashes to the existing campaign only; do not alter prior attempts, central accounting, protocol/dictionary/crosswalk files, or the authorized NEAR/6 decision. A failed or blocked P05 remains diagnostic and cannot authorize IEEE S-C01 or a final search.

## Offline preflight

From the two isolated worktrees, before requesting a lease:

```bash
cd /Users/antho/agent-tools/academic-research/skills/academic-search
uv run pytest -q \
  tests/test_search_ieee_xplore_browser.py

python3 /Users/antho/nanosatellite-mbse/SLR/SLR1/scripts/test_ieee_language_control_probe.py
python3 /Users/antho/nanosatellite-mbse/SLR/SLR1/scripts/ieee_language_control_probe.py --help >/dev/null
shasum -a 256 \
  scripts/search_ieee_xplore.py \
  tests/test_search_ieee_xplore_browser.py \
  /Users/antho/nanosatellite-mbse/SLR/SLR1/scripts/ieee_language_control_probe.py \
  /Users/antho/nanosatellite-mbse/SLR/SLR1/scripts/test_ieee_language_control_probe.py
```

These tests are source-free. A passing suite and CLI help establish launch readiness of the adapter/probe mechanics only; they do not establish current IEEE behavior or a live gate.
