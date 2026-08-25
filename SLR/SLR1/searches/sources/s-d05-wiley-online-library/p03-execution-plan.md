# P03 execution plan — Wiley Online Library

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


This is the source-free plan for `S-D05-P03-<timestamp>`. It is governed by `D-TECH-NEXT-P03`, is diagnostic only, and needs no new human authorization.

## Fixed scope

- Use the shared CfT lease, profile, and `http://127.0.0.1:9222` for the entire attached phase.
- Run at most four Wiley adapter invocations. An adapter's internal two-pass reconciliation is part of one invocation.
- Use the existing `AllField` query files without regeneration or semantic edits.
- Use `Articles & Chapters`, except for the one explicit `Collections` route check.
- Use `Earliest` sorting and the pilot execution date as the diagnostic upper date bound. This is not `P-001` or a final cutoff.
- Do not screen, import, merge, create a final event, submit pair-bearing cells, or choose a fallback query.
- Do not retry a failed operation in this attempt.

## Conditional operations

| Operation | Query | Mode | Gate evidence | Condition |
| --- | --- | --- | --- | --- |
| 1 | `queries/B1.wiley-allfield.txt` | Articles & Chapters, count only | `G-LIVE-HEALTH`; route, exact echo, total, and controls | Run first; stop on failure |
| 2 | `queries/A1.wiley-allfield.txt` | Articles & Chapters, count only | `G-LIVE-INTERFACE`; long-query parser and controls | Only after operation 1 passes |
| 3 | `queries/B1.wiley-allfield.txt` | Collections, count only | `G-LIVE-INTERFACE`; separate content boundary and total | Only after operation 2 passes |
| 4 | `queries/B1.wiley-allfield.txt` | Articles & Chapters, exact-total two-pass retrieval and native RIS | `G-LIVE-COMPLETENESS`; pagination, DOI identity, ordered-pass, JSON/CSV/RIS reconciliation | Only after operations 1–3 pass and the operation-1 total is 1–40 |

For operation 4, set `--limit` to the exact operation-1 total and `--max-pages` to `ceil(total / 20)`. If the total is zero or greater than 40, record operation 4 as not run. Do not select another query to obtain a convenient count.

## Stop conditions

Stop the phase without another source invocation on any:

- lease, browser version, anchor, power/sleep, owned-page cleanup, or release failure;
- login, CAPTCHA, challenge, service error, syntax error, query rewrite, dropped control, wrong route, missing/conflicting total, or output collision;
- stale/short page, duplicate or missing DOI, pass drift, or RIS mismatch; or
- nonzero adapter exit.

A failure remains `total=null` unless the adapter positively reconciles a native zero. No partial prefix is imported.

## Source-free preflight

Before allocating the live phase:

```bash
cd /Users/antho/agent-tools/academic-research/skills/academic-search
uv run pytest -q \
  tests/test_search_wiley_online_library.py \
  tests/test_output_transaction_safety.py

shasum -a 256 \
  scripts/search_wiley_online_library.py \
  tests/test_search_wiley_online_library.py
```

Expected current hashes:

```text
b0008d8ebda803dca6f4312236d95dc5e66ae2fce3397f28ddb3983f457222a0  search_wiley_online_library.py
40ad9b947deea9a8fbdda538ebd787ffc9bf2c833526cf3fe644ea523d558778  test_search_wiley_online_library.py
```

The focused suite currently passes `29 tests, 20 subtests`.

## Attached live-phase skeleton

Replace the timestamp once, create the two new directories, and set `PILOT_DATE` to the actual local execution date. Do not pre-create receipt, output, marker, CSV, or RIS files.

```bash
ROOT=/Users/antho/nanosatellite-mbse
ATTEMPT_ID='S-D05-P03-<timestamp>'
PILOT_DATE='<YYYY-MM-DD>'

PACKET="$ROOT/SLR/SLR1/searches/sources/s-d05-wiley-online-library/pilots/$ATTEMPT_ID"
RESTRICTED="$ROOT/.searches/s-d05-wiley-restricted/$ATTEMPT_ID"
mkdir -p "$PACKET" "$RESTRICTED"

LEASE=/Users/antho/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py
ADAPTER=/Users/antho/agent-tools/academic-research/skills/academic-search/scripts/search_wiley_online_library.py
Q_B1="$ROOT/SLR/SLR1/searches/sources/s-d05-wiley-online-library/queries/B1.wiley-allfield.txt"
Q_A1="$ROOT/SLR/SLR1/searches/sources/s-d05-wiley-online-library/queries/A1.wiley-allfield.txt"

caffeinate -dims uv run "$LEASE" \
  --owner "$ATTEMPT_ID" \
  --source wiley-online-library \
  --receipt "$PACKET/live-phase-receipt.json" \
  --wait 30 \
  --lease-timeout 600 \
  -- bash -ceu '
    set -euo pipefail

    run_count() {
      query_file="$1"; output="$2"; content="$3"
      uv run "'"$ADAPTER"'" \
        --query "$(cat "$query_file")" \
        --date-start 2011-01-01 --date-end "'"$PILOT_DATE"'" \
        --content "$content" --sort Earliest \
        --limit 20 --max-pages 1 --passes 1 \
        --timeout 90 --page-delay-seconds 1 \
        --max-source-total 5000 --count-only \
        --cdp-url http://127.0.0.1:9222 \
        --output-path "$output"
    }

    OP1="'"$RESTRICTED"'/op-01-health-b1.json"
    OP2="'"$RESTRICTED"'/op-02-parser-a1.json"
    OP3="'"$RESTRICTED"'/op-03-collections-b1.json"

    run_count "'"$Q_B1"'" "$OP1" articlesChapters
    sleep 3
    run_count "'"$Q_A1"'" "$OP2" articlesChapters
    sleep 3
    run_count "'"$Q_B1"'" "$OP3" collections
    sleep 3

    TOTAL="$(jq -er ".total | numbers" "$OP1")"
    if (( TOTAL >= 1 && TOTAL <= 40 )); then
      PAGES=$(( (TOTAL + 19) / 20 ))
      uv run "'"$ADAPTER"'" \
        --query "$(cat "'"$Q_B1"'")" \
        --date-start 2011-01-01 --date-end "'"$PILOT_DATE"'" \
        --content articlesChapters --sort Earliest \
        --limit "$TOTAL" --max-pages "$PAGES" --passes 2 \
        --timeout 90 --page-delay-seconds 1 \
        --expected-source-total "$TOTAL" --max-source-total 5000 \
        --require-complete --cdp-url http://127.0.0.1:9222 \
        --output-path "'"$RESTRICTED"'/op-04-complete-b1.json" \
        --csv-output-path "'"$RESTRICTED"'/op-04-complete-b1.csv" \
        --native-export-dir "'"$RESTRICTED"'/op-04-native-ris"
    else
      printf "Operation 4 not run: B1 total was %s, outside 1..40.\n" "$TOTAL" >&2
    fi
  '
```

After the child exits, verify the attempt receipt says `released` with successful cleanup before interpreting any source artifact. Then create the immutable manifest/evidence index, update `campaign.json`, and rerun the shared validator.