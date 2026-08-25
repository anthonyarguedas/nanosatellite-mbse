# P04 execution plan — NASA Technical Reports Server (NTRS)

This is the exact source-free launch plan for the next existing-campaign attempt,
`S-D13-P04-<runtime timestamp>`. It is diagnostic only. It preserves the
immutable P01/P02 API failures and P03 rendered-navigation failure; it does not
accept the source method, change the dictionary, or make a methodological
decision.

## Fixed allocation and hard limits

- Use the existing campaign in [`campaign.json`](campaign.json). At runtime,
  create one fresh attempt ID in the existing `pilots/` namespace and a fresh
  attempt directory; do not edit or rewrite P01, P02, or P03.
- The source-operation maximum is **two**, in this order: (1) source-health
  precheck; (2) one conditional rendered reachability/navigation classification.
  The health probe performs one root navigation. The adapter operation performs
  one bounded count-only minimal-query invocation. No retry, second query,
  partition, export, detail visit, completeness pass, screening, candidate
  import, or final event is permitted.
- Hold exactly one shared CfT lease at `http://127.0.0.1:9222` for both
  operations. Use the trusted local lease runner and its new per-attempt
  `--receipt`; do not launch a browser, create a profile, select another port,
  or use an API/HTTP route. Each operation creates and closes one owned page;
  they are sequential, never concurrent.
- `PILOT_DATE` is created from the local execution date and recorded as the
  pilot-date diagnostic bound for the attempt ledger only. It is **not sent as a date filter**: the
  historical P03 minimal gate intentionally sent no date control before the
  visible date surface was known. It is not P-001 or a final cutoff.
- A challenge, login/access page, busy/rate-limit state, gateway/source error,
  lease/anchor/power failure, output collision, nonzero adapter exit, or failed
  cleanup/release is terminal. Do not wait through or bypass a challenge, and
  do not reissue a failed operation. Unobserved totals remain `null`; only a
  positively reconciled native zero may be recorded as zero.

## Runtime attempt and immutable inputs

Run the following only after the controller has completed its normal local
browser preflight and allocated the attempt. The manifest is created at runtime
from the shared pilot-manifest template and linked to the existing campaign;
no P04 pilot directory, receipt, or output is pre-created here.

```bash
set -euo pipefail

ROOT=/Users/antho/nanosatellite-mbse
TOOLS=/Users/antho/agent-tools
ATTEMPT_ID="S-D13-P04-$(date +%Y%m%dT%H%M%S%z)"
PILOT_DATE="$(date +%F)"
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d13-nasa-ntrs/pilots/$ATTEMPT_ID"
RESTRICTED="$ROOT/.searches-d13-ntrs/$ATTEMPT_ID"
mkdir -p "$PACKET" "$RESTRICTED"
test ! -e "$PACKET/manifest.json"
test ! -e "$RESTRICTED/browser-lease-receipt.json"
test ! -e "$RESTRICTED/op-01-source-health.json"
test ! -e "$RESTRICTED/op-02-rendered-g01.json"

HEALTH="$ROOT/SLR/SLR1/scripts/ntrs_source_health_probe.py"
ADAPTER="$TOOLS/academic-research/skills/academic-search/scripts/search_ntrs.py"
LEASE="$TOOLS/internet/skills/browser/scripts/run_with_browser_lease.py"
TEST_QUERY="$ROOT/SLR/SLR1/searches/sources/s-d13-nasa-ntrs/pilots/S-D13-P03-20260824T125840-0400/queries/G01-minimal-nanosatellite.txt"
EXPECTED_QUERY_SHA256=3fc7d31e9abb58d42acd5c95a9549835545de822d0843e28265c6979b1a466d4

python3 - "$TEST_QUERY" "$EXPECTED_QUERY_SHA256" <<'PY'
import hashlib
import pathlib
import sys
path, expected = pathlib.Path(sys.argv[1]), sys.argv[2]
raw = path.read_bytes()
if hashlib.sha256(raw).hexdigest() != expected or raw != b"nanosatellite\n":
    raise SystemExit("immutable P03 minimal query mismatch")
PY

set +e
caffeinate -dims uv run "$LEASE" \
  --owner "$ATTEMPT_ID" \
  --source ntrs \
  --receipt "$RESTRICTED/browser-lease-receipt.json" \
  --wait 30 \
  --lease-timeout 600 \
  -- bash -ceu "$(cat <<'CHILD_SCRIPT'
    set -euo pipefail
    HEALTH="$1"; ADAPTER="$2"; TEST_QUERY="$3"; RESTRICTED="$4"

    # Operation 1 — exactly one record-free source-health navigation.
    set +e
    uv run "$HEALTH" --execute \
      --cdp-url http://127.0.0.1:9222 \
      --timeout-seconds 30 \
      --stabilization-interval-seconds 0.2 \
      --output-path "$RESTRICTED/op-01-source-health.json"
    HEALTH_STATUS=$?
    set -e
    python3 -c '
import json
import pathlib
import sys
status, path = int(sys.argv[1]), pathlib.Path(sys.argv[2])
if status != 0:
    raise SystemExit("operation 1 did not pass; operation 2 is not authorized")
receipt = json.loads(path.read_text(encoding="utf-8"))
nav = receipt.get("navigation", {})
result = receipt.get("result", {})
if not (
    result.get("healthy") is True
    and result.get("observations_accepted") is True
    and receipt.get("record_free") is True
    and receipt.get("source_total") is None
    and receipt.get("records_observed") == 0
    and receipt.get("navigation_attempt_count") == 1
    and nav.get("response_status_class") == "2xx"
    and nav.get("route_class") == "normal_source_route"
    and nav.get("source_identity") is True
    and nav.get("search_control_present") is True
    and nav.get("stable_samples") >= 2
    and not any(nav.get(name) is True for name in (
        "challenge_detected", "access_detected", "login_detected",
        "busy_detected", "error_detected",
    ))
):
    raise SystemExit("operation 1 receipt did not satisfy G-SOURCE-HEALTH")
' "$HEALTH_STATUS" "$RESTRICTED/op-01-source-health.json"

    # Pacing is passive only; it is not a source retry.
    sleep 3

    # Operation 2 — the existing P03 minimal rendered query, count-only.
    # No date, partition, detail, export, or completeness flag is allowed.
    set +e
    uv run "$ADAPTER" \
      --query "$(cat "$TEST_QUERY")" \
      --limit 1 \
      --max-pages 1 \
      --count-only \
      --skip-full-abstracts \
      --timeout 90 \
      --page-delay-seconds 0 \
      --detail-delay-seconds 0 \
      --cdp-url http://127.0.0.1:9222 \
      --output-path "$RESTRICTED/op-02-rendered-g01.json"
    ADAPTER_STATUS=$?
    set -e
    test -s "$RESTRICTED/op-02-rendered-g01.json"
    # Preserve the adapter record-free success or null-total failure artifact;
    # its exit status is the terminal classification for this operation.
    exit "$ADAPTER_STATUS"
CHILD_SCRIPT
)" _ "$HEALTH" "$ADAPTER" "$TEST_QUERY" "$RESTRICTED"
LEASE_STATUS=$?
set -e

# Do not interpret either artifact until the lease runner reports verified
# cleanup/release. Then create the immutable P04 manifest/evidence index and
# run the shared validator; no source operation follows this command.
python3 - "$RESTRICTED/browser-lease-receipt.json" <<'PY'
import json
import pathlib
import sys
receipt = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
if receipt.get("state") != "released" or receipt.get("cleanup") != "verified-clean":
    raise SystemExit("shared CfT lease release/cleanup was not verified")
PY
exit "$LEASE_STATUS"
```

## Operation gates and terminal interpretation

| Operation | Entry point and exact mode | Gate | Conditional transition |
|---|---|---|---|
| 1 | `ntrs_source_health_probe.py --execute --cdp-url http://127.0.0.1:9222 --timeout-seconds 30 --stabilization-interval-seconds 0.2 --output-path <unique op-01 receipt>`; one navigation to the public root, fixed DOM projection, no query | `G-SOURCE-HEALTH`: 2xx response, normal NTRS root/search route, source identity and visible search surface, two equal passive samples, no challenge/access/login/busy/error, record-free receipt, owned-page cleanup | Only a passing receipt authorizes operation 2; every other result stops the attempt with no adapter invocation |
| 2 | Current rendered `search_ntrs.py` with the exact existing P03 `G01-minimal-nanosatellite.txt` (`nanosatellite`), `--limit 1 --max-pages 1 --count-only --skip-full-abstracts --timeout 90`, no date, CSV, detail, export, `--require-complete`, or partition file | `G-BROWSER-ADAPTER-SAFETY` is source-free preflight; `G-RENDERED-NAVIGATION` classifies the one adapter result. A successful count-only artifact may contain an exact positive total or explicit zero; a navigation/access/parse failure remains record-free with `total=null` | Stop immediately after this one result. Do not retry, run A1/B1/etc., retrieve details, export, or claim completeness |

The health receipt is a precondition, not a search result. The adapter's
count-only output is diagnostic and cannot enter screening, candidate import,
PRISMA identification, or a final event. P01/P02 API evidence remains
historical null failure evidence; this plan neither calls that route nor
reclassifies it.

## Source-free preflight and postflight checks

Before the attached phase, run only local checks:

```bash
cd /Users/antho/agent-tools/academic-research/skills/academic-search
python3 -m unittest -q tests/test_search_ntrs.py
python3 /Users/antho/nanosatellite-mbse/SLR/SLR1/scripts/test_ntrs_source_health_probe.py
python3 scripts/search_ntrs.py --help >/dev/null
python3 /Users/antho/nanosatellite-mbse/SLR/SLR1/scripts/ntrs_source_health_probe.py --help >/dev/null
```

The controller must also verify the shared lease receipt, anchor
preservation, owned-page cleanup, and release before creating any immutable P04
manifest/evidence links. A failed postflight invalidates the attempt even if a
source page appeared healthy. No live claim is made by this plan.
