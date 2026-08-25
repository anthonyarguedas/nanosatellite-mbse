#!/bin/bash
# Corrected attached P04 child bundle. The file form avoids nested shell/heredoc
# quoting in the lease command and preserves the exact P03 scope/stop ladder
# under the new immutable P04 identity.
set -euo pipefail

: "${ROUTE:?ROUTE is required}"
: "${PAIRED:?PAIRED is required}"
: "${ROUTE_RECEIPT:?ROUTE_RECEIPT is required}"
: "${PAIRED_RECEIPT:?PAIRED_RECEIPT is required}"
: "${LIVE_PREFLIGHT:?LIVE_PREFLIGHT is required}"
: "${QUERY_B1:?QUERY_B1 is required}"
: "${ADAPTER_DIR:?ADAPTER_DIR is required}"
: "${ATTEMPT_ID:?ATTEMPT_ID is required}"
: "${PILOT_DATE:?PILOT_DATE is required}"

python3 - "$LIVE_PREFLIGHT" <<'PY'
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(args):
    completed = subprocess.run(args, text=True, capture_output=True, check=False)
    return completed.returncode, completed.stdout


battery_code, battery = run(["pmset", "-g", "batt"])
assertion_code, assertions = run(["pmset", "-g", "assertions"])
caffeinate_code = subprocess.run(
    ["pgrep", "-x", "caffeinate"], capture_output=True, check=False
).returncode
receipt = {
    "schema_version": "slr1-engineering-village-live-preflight/v1",
    "captured_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    "phase_start_utc": os.environ.get("PHASE_START_UTC"),
    "browser_epoch": os.environ.get("BH_BROWSER_LEASE_EPOCH"),
    "endpoint": "http://127.0.0.1:9222",
    "profile_path": os.environ.get("BH_BROWSER_LEASE_PROFILE"),
    "power": {
        "query_succeeded": battery_code == 0,
        "source": "AC Power" if "Now drawing from 'AC Power'" in battery else "not_ac_or_unavailable",
    },
    "caffeinate": {
        "command": "caffeinate -dims",
        "assertions_query_succeeded": assertion_code == 0,
        "prevent_system_sleep_present": "PreventSystemSleep             1" in assertions,
        "process_name_observed": caffeinate_code == 0,
    },
    "source_work_started": False,
    "retention_exclusions": [
        "raw_pmset_output",
        "process_id",
        "process_command",
        "browser_target_identifier",
        "browser_url",
        "source_page_content",
    ],
}
Path(sys.argv[1]).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if not (
    receipt["power"]["query_succeeded"]
    and receipt["power"]["source"] == "AC Power"
    and receipt["caffeinate"]["assertions_query_succeeded"]
    and receipt["caffeinate"]["prevent_system_sleep_present"]
    and receipt["caffeinate"]["process_name_observed"]
):
    raise SystemExit(97)
PY

# Operation 1: exactly one corrected route projection.
uv run "$ROUTE" \
  --execute \
  --cdp-url http://127.0.0.1:9222 \
  --timeout-seconds 45 \
  --stabilization-interval-seconds 0.2 \
  --output-path "$ROUTE_RECEIPT"

jq -e \
  '.result.status == "healthy" and
   .result.observations_accepted == true and
   .ownership.owned_page_closed == true and
   .ownership.owned_target_disappeared == true and
   .ownership.baseline_pages_preserved == true and
   .ownership.baseline_target_set_preserved == true' \
  "$ROUTE_RECEIPT" >/dev/null

sleep 2

# Operation 2: exactly one paired event, Compendex then Inspec.
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

jq -e \
  '.result.status == "complete" and
   .result.count_control_evidence_complete == true and
   .accounting.campaign_source_operation_count == 1 and
   .accounting.campaign_source_operation_maximum == 1 and
   .accounting.database_requests_planned == 2 and
   .accounting.database_requests_performed == 2 and
   ([.database_requests[].database] | sort) == ["compendex", "inspec"] and
   .result.records_retained == 0' \
  "$PAIRED_RECEIPT" >/dev/null
