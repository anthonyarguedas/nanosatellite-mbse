# P04 execution plan — OATD corrected advanced-form diagnostic

**Status:** source-free launch plan; no P04 source operation has been run.  This is
`D-TECH-NEXT-P04`, a controller-authorized technical corrective attempt under
campaign `S-D09-C01-20260824T161325-0400`.  It does not change the protocol,
concept dictionary, translation, field boundary, limits, recall, completeness
rule, or PRISMA accounting.

## Fixed scope and carried gates

- Allocate one new runtime attempt ID of the form
  `S-D09-P04-<YYYYMMDDThhmmss-offset>`.  Do not reuse
  `S-D09-P03-20260824T130849-0400` and do not call this a retry of P03 E-002.
- The entire live phase is one attached child under the one shared CfT lease at
  `http://127.0.0.1:9222`.  Do not launch or select a browser, profile, port, or
  second lease.  The historical P03 endpoint `9234` is not permitted.
- This phase has a **maximum of three source operations**: one corrected native
  advanced-form submission and, only after a positively identified safe busy
  state, at most two same-page busy reissues.  The reissues are internal to the
  one probe invocation, not new pilot executions.  There is no second distinct
  query, planned-cell submission, Record Details visit, strict traversal, CSV,
  screening, candidate import, or final event.
- Carry forward, without re-testing or changing their evidence, the existing
  `G-BOUNDARY`, `G-QUERY-CONSTRUCTION`, `G-BASIC-PARSER`, `G-BASIC-COUNT`, and
  `G-V3-HEALTH` gates.  The controller must retain their exact existing paths
  and SHA-256 values in `campaign.json`.
- P04 targets only `G-ADVANCED-FORM` and, conditionally, `G-BUSY-RECOVERY`.
  `G-PAIR-SEMANTICS` remains blocked; BG1, BG2, BC1, and BT2 remain
  final-use-prohibited.  No result from this diagnostic makes any pair-bearing
  query usable.  P04 does not establish controlled vocabulary, date/language/
  content behavior, retrieval, identity, or completeness.
- P03's failed E-002 evidence remains immutable and is not overwritten or
  reinterpreted.  The corrected probe's in-context cleanup and bounded state
  machine are the only P04 technical correction.

## Exact recovered input and query-file disposition

The P03 immutable evidence that supplies these values is
`pilots/S-D09-P03-20260824T130849-0400/manifest.json` (E-002's exact
operation and `fields`), corroborated by its `observations.md` execution table
and the `P03_live_validation` section of `translation-spec.json`.  It records:

- exact query: `CubeSat AND SysML`
- exact visible/native field label: `title` (lowercase)

These values are used verbatim.  No new diagnostic cell is invented and no
normative query file is regenerated or submitted.  The nine logical query
partitions remain the current files, with BT2's required lossless physical
shards:

```text
queries/A1.oatd-basic.txt
queries/A2.oatd-basic.txt
queries/A3.oatd-basic.txt
queries/B1.oatd-basic.txt
queries/B2.oatd-basic.txt
queries/BG1.oatd-basic.txt
queries/BG2.oatd-basic.txt
queries/BC1.oatd-basic.txt
queries/BT2-01.oatd-basic.txt
queries/BT2-02.oatd-basic.txt
queries/BT2-03.oatd-basic.txt
queries/BT2-04.oatd-basic.txt
```

P04 passes the recovered query inline to the probe; `query_file=none` for the
single diagnostic operation.  Every file above is read-only for this phase.

## Runtime allocation, date bound, and unique paths

At runtime, from the current nanosatellite working tree, create the ID and
both attempt directories before any source activity.  Abort on either path
collision; never delete, reuse, or overwrite an old attempt.

```bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
STAMP="$(TZ=America/New_York date '+%Y%m%dT%H%M%S%z')"
ATTEMPT_ID="S-D09-P04-${STAMP}"
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d09-oatd/pilots/$ATTEMPT_ID"
RESTRICTED="$ROOT/.searches/s-d09-oatd-restricted/$ATTEMPT_ID"
PILOT_DATE="$(TZ=America/New_York date '+%Y-%m-%d')"

mkdir -p "$ROOT/SLR/SLR1/searches/sources/s-d09-oatd/pilots" \
         "$ROOT/.searches/s-d09-oatd-restricted"
test ! -e "$PACKET" && test ! -e "$RESTRICTED"
mkdir "$PACKET" "$RESTRICTED"

LEASE="$ROOT/../agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py"
PROBE="$ROOT/SLR/SLR1/scripts/oatd_advanced_form_probe.py"
LEASE_RECEIPT="$RESTRICTED/${ATTEMPT_ID}.shared-lease-receipt.json"
PROBE_OUTPUT="$RESTRICTED/${ATTEMPT_ID}.advanced-title-receipt.json"
LEDGER="$RESTRICTED/${ATTEMPT_ID}.source-operation-ledger.json"
```

Resolve `LEASE` to the supervisor-supplied shared lease script if the checked
out root is not adjacent to `agent-tools`; do not replace it with another
wrapper.  The three paths above are create-only and include the runtime ID.
Do not pre-create either receipt or the probe output.  The probe reserves its
output with exclusive creation; the lease wrapper receives a new per-attempt
`--receipt` path.

`PILOT_DATE` is the local `America/New_York` date recorded in the restricted
request ledger and manifest as the **pilot-date diagnostic bound**.  This
advanced-form operation supplies no earliest/latest date value (the current
probe has no date flags); the bound is therefore not applied to the submitted
query and is not a final cutoff.  Do not invent date semantics or alter the
protocol to apply it.  Any nonblank/default date state that prevents the
predeclared form projection from reconciling is a hard stop, not a reason to
add a date control.

## Offline gates before lease acquisition

Run all of the following without a browser, provider, network, or lease.  Do
not proceed to the live phase if any command fails.  Use
`PYTHONDONTWRITEBYTECODE=1` so the focused test does not modify tracked cache
files.

```bash
cd "$ROOT"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  SLR.SLR1.scripts.test_oatd_advanced_form_probe
PYTHONDONTWRITEBYTECODE=1 python3 "$PROBE" --help
shasum -a 256 "$PROBE" \
  SLR/SLR1/scripts/test_oatd_advanced_form_probe.py
PYTHONDONTWRITEBYTECODE=1 uv run --offline \
  SLR/SLR1/scripts/validate_search_infrastructure.py --mode pre-final
git diff --check
```

The current source-free probe run is expected to pass 41 tests.  The current
probe and focused-test hashes to record before a live phase are:

```text
3786af4a21d8b9d839797e47598359ecf6aba2993a6cc0cc014978487279a2b5  oatd_advanced_form_probe.py
43a071e4ef032bfe1557b3dea0e710dad44a3ee9f532e31939ac405db24c71d9  test_oatd_advanced_form_probe.py
```

Also verify offline that the query files and current campaign are unchanged
from the carried checkpoint.  No source-free test is a live OATD claim.

## Controller preflight and lease command

Before the source command, the controller completes the shared browser-live
checklist and records: the unique owner/receipt, global OATD pacing decision,
exactly one CfT process using the supervisor profile, browser epoch and
runtime/on-disk version equality, healthy protected broker anchor, AC power,
process-scoped `caffeinate -dims`, and no actual Sleep/Wake/DarkWake event in
the preflight interval.  A failed health, anchor, power, sleep, process,
profile, version, or lease check means zero source operations.

The controller must have confirmed at least 60 seconds of global OATD quiet
interval since the preceding OATD source operation.  `--wait 60` below is the
predeclared global pacing wait; it is not permission for another query.  Run
the whole phase, including cleanup and release, exactly through this lease:

```bash
caffeinate -dims uv run --offline "$LEASE" \
  --owner "$ATTEMPT_ID" \
  --source oatd \
  --receipt "$LEASE_RECEIPT" \
  --wait 60 \
  --lease-timeout 360 \
  -- \
  uv run --offline "$PROBE" \
    --execute \
    --cdp-url http://127.0.0.1:9222 \
    --query 'CubeSat AND SysML' \
    --field-label 'title' \
    --timeout-seconds 180 \
    --poll-interval-seconds 0.2 \
    --busy-retries 2 \
    --busy-retry-delay-seconds 30 \
    --output-path "$PROBE_OUTPUT"
```

The probe is the source-specific attached Playwright runner.  It creates one
owned sibling page, navigates only that page to the normal OATD home form,
selects the exact `title` option, fills the exact nonblank query, read-backs
both controls, verifies the canonical HTTPS native GET form and one visible
native submitter, and submits through the guarded native click.  It does not
use a static request, API, blank advanced submission, access-control action,
record/detail route, full-text route, or `browser_harness new_tab`.

`--timeout-seconds 180` is one absolute finite deadline shared by native click
and post-submit observation.  It is deliberately longer than the first
30-second busy wait and can contain both preauthorized waits (30 seconds,
then 60 seconds), their rechecks, and at most two reissues.  Never extend it
or raise the two-reissue budget.  The 360-second lease limit is only a finite
supervision bound for the complete phase and does not authorize more source
work.

## Operation order and accounting

The restricted ledger uses the following fixed accounting.  Home-page loading,
form inspection, cleanup, and lease health are part of the one diagnostic
invocation; they are not additional query cells.  `total=null` is recorded for
a failure or an unreconciled state.  Only a positively reconciled native
result may supply a source total, and a native zero is zero only when the
probe classifies `zero_observed`.

| Operation | Predeclared action | Maximum and transition |
|---|---|---|
| O-001 | One corrected nonblank native advanced GET submission: query `CubeSat AND SysML`, field label `title`; output `$PROBE_OUTPUT`. | Always first and only distinct diagnostic. If pre-submit mapping, native safety, transport, challenge, access, syntax, or cleanup fails, stop with no reissue. |
| O-002 | Same owned page, only after O-001 yields an exclusive `busy_retry_safe` post-submit state; wait at most 30 seconds, recheck, and reissue only the in-memory canonical allowlisted GET controls. | At most one reissue. If busy clears during the wait, do not reissue. If the recheck is challenge/access/syntax/result/unsafe or the 180-second deadline expires, stop. |
| O-003 | Same owned page, only after O-002's reissued state again yields an exclusive safe busy state; wait at most 60 seconds, recheck, and reissue the same canonical controls once. | At most one second reissue. After it, or on any terminal state/deadline, stop. No O-004 exists. |

The ledger records for each possible operation: operation ID, exact query and
field, whether it was dispatched, start/end timestamps, mode, source total or
`null`, result classification, recovery wait(s), busy retries attempted and
completed, output path, and marker/CSV status (`not_applicable` for this probe).
The initial native submission and both possible reissues remain one owned-page
sequence; a reissue never opens a new page or starts a new lease.

## Conditional transitions and result interpretation

- A challenge, CAPTCHA, login/verification page, access denial, syntax/error
  state, noncanonical route, missing source identity, non-exact form readback,
  or unverified busy page is never retried. Keep the same page for passive
  observation and cleanup; do not click, reload, solve, or bypass a challenge.
- A busy state is eligible for recovery only when it is exclusive (not also a
  challenge, access, syntax, or result state) and the canonical advanced route,
  OATD identity, and exact query/field readback are all true. The probe waits
  in that page, rechecks it, and uses only the prevalidated form controls to
  construct the canonical retry URL in memory. It never copies a mutable
  destination or generic form payload.
- A busy page that clears during either 30- or 60-second wait continues on the
  same page without an extra request. A persistent busy state consumes one
  reissue slot per reissue; a third reissue is forbidden.
- A reconciled range, singleton, or native no-match result ends the operation.
  The result is diagnostic aggregate evidence only: it does not validate pair
  semantics, enable planned cells, or authorize screening/import. If cleanup
  is not verified, the final accounted total is `null` even if a result was
  briefly observed.
- A post-submit timeout, navigation failure, exhausted busy budget, or any
  unreconciled result is terminal for P04. It is not a source zero and no
  partial result is retained or imported.

## Same-page cleanup and hard stops

The probe must finish cleanup while the Playwright connection is still live.
It may close only its target proven new after baseline comparison; it must
verify target disappearance, preservation of the exact pre-create target set
(including non-page targets), preservation of every baseline page, and then
verified lease release. The broker anchor is never navigated or closed.

Stop source work immediately, with no new source operation, on any of the
following:

- missing/colliding create-only path, failed offline gate, missing lease
  receipt, failed shared-CfT/power/sleep/anchor/version/process preflight, or
  failed lease acquisition/release;
- an owned page that is not distinct or cannot be proven as a new target;
- any form/field/submitter mapping mismatch, nonblank readback mismatch,
  unsafe native action, route redirect, challenge, access state, syntax state,
  transport exception, or result that cannot be reconciled under the allowlist;
- any busy state that is not exclusive and safe, a third reissue request, a
  wait beyond 30 then 60 seconds, or the absolute 180-second deadline;
- page-close, target-disappearance, baseline-preservation, cancellation, or
  cleanup verification failure; keep controller supervision active if cleanup
  is unresolved;
- any request to open a new page, use port 9234, use a fresh browser/profile,
  mutate the anchor, follow Record Details/full text, create CSV/marker output,
  submit a planned cell, screen, import, or update central integration files.

After the child exits, the controller verifies the lease receipt says released
and cleanup succeeded, reads both JSON receipts fully, and records the final
Sleep/Wake/DarkWake check. Only then may it create the restricted operation
ledger and the tracked P04 manifest/observations/evidence index. A blocked,
failed, or cancelled P04 has no importable prefix and does not alter the
campaign's carried gates; the controller alone checkpoints the new attempt.
