#!/bin/bash
set -euo pipefail
HEALTH="$1"
ADAPTER="$2"
TEST_QUERY="$3"
RESTRICTED="$4"

# Operation 1: exactly one record-free source-health root navigation.
set +e
uv run "$HEALTH" --execute \
  --cdp-url http://127.0.0.1:9222 \
  --timeout-seconds 30 \
  --stabilization-interval-seconds 0.2 \
  --output-path "$RESTRICTED/op-01-source-health.json"
HEALTH_STATUS=$?
set -e
python3 - "$HEALTH_STATUS" "$RESTRICTED/op-01-source-health.json" <<'PY'
import json
import pathlib
import sys
status = int(sys.argv[1])
path = pathlib.Path(sys.argv[2])
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
PY

# Distinct passive pacing; never a retry or source reissue.
sleep 3

# Operation 2: one exact 13-byte nanosatellite count-only rendered query.
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
exit "$ADAPTER_STATUS"
