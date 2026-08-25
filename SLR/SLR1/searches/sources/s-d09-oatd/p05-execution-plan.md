# P05 execution plan — OATD transient-challenge technical successor

**Status:** source-free prospective launch plan only. `D-TECH-NEXT-P05` authorizes
exactly one controller-technical successor under campaign
`S-D09-C01-20260824T161325-0400`; it does not allocate an attempt ID, acquire a
lease, contact OATD, or create a pilot directory or receipt. P04 and all earlier
attempts remain immutable and are not reissued.

## Fixed scope and accounting

- At runtime, allocate one fresh `S-D09-P05-<runtime timestamp>` attempt as
  `technical_corrective`. Do not materialize that placeholder now and do not
  reuse `S-D09-P04-20260825T110122-0400` or its O-001.
- The successor has a maximum of **three source operations**: O-001 is one
  corrected nonblank native advanced-form diagnostic; O-002 and O-003 are
  conditional same-page busy reissues only after an exclusive, positively
  identified post-submit busy state. There is no fourth operation, planned
  cell, Record Details visit, strict traversal, export, screening, import, or
  final event.
- Passive challenge observations are not source-operation reissues. The probe
  keeps the same adapter-owned page and uses only DOM projections during the
  challenge window: no click, reload, navigation, submit, CAPTCHA interaction,
  login, bypass, or challenge solving.
- The pre-submit challenge policy is `RP-D09-CHALLENGE-WAIT-01`: at most **30
  seconds total**, with a fixed **0.2-second cadence**, under the same absolute
  operation deadline as the native click and post-submit observation. If the
  canonical advanced form appears, the probe continues the already prepared
  operation and permits exactly one guarded native submission. A persistent
  challenge, or a transition to login/access/CAPTCHA, fails with
  `total=null`, no prefix, and no retry. A busy or syntax state before
  submission also fails without a reissue.
- The existing post-submit busy policy is unchanged: `RP-D09-BUSY-01`, waits of
  30 and 60 seconds, at most two canonical same-page GET reissues, and one
  run-wide busy budget. If busy clears during a wait, do not reissue. Challenge
  observations never enter that budget.

## Carried gates and hard stops

Carry forward unchanged, by the existing campaign paths and hashes,
`G-BOUNDARY`, `G-QUERY-CONSTRUCTION`, `G-BASIC-PARSER`, `G-BASIC-COUNT`, and
`G-V3-HEALTH`. The successor targets only `G-ADVANCED-FORM` and, if reached,
`G-BUSY-RECOVERY`; `G-PAIR-SEMANTICS` and every pair-bearing expansion remain
blocked and final-use-prohibited.

Stop immediately with a null total and no prefix on any form/control mismatch,
unsafe route, failed safety proof, access/login/CAPTCHA state, persistent
challenge, syntax state, transport failure, non-exclusive busy state, expired
30-second challenge budget, expired absolute deadline, cleanup failure, or
lease-release failure. Preserve the same page for passive observation and
cleanup. Never directly reissue P04 E-001 or P04 O-001.

## Source-free gates before any later allocation

Run these checks without a browser, lease, provider, network, source operation,
or attempt-directory creation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  SLR.SLR1.scripts.test_oatd_advanced_form_probe
PYTHONDONTWRITEBYTECODE=1 python3 SLR/SLR1/scripts/oatd_advanced_form_probe.py --help
PYTHONDONTWRITEBYTECODE=1 uv run --offline \
  SLR/SLR1/scripts/validate_search_infrastructure.py --mode pre-final
git diff --check
```

The focused suite must include challenge-clears, challenge-persists,
challenge-to-access, no-premature-submit, and absolute-deadline accounting
coverage. A failed deterministic gate is a source-free technical stop; do not
allocate an attempt ID or present it as a source result.

## Later live-phase boundary (not executed by this change)

After the source-free gates pass and a controller allocates the new immutable
ID, use only the shared CfT lease at `http://127.0.0.1:9222`, one owned sibling
page, and the normal rendered OATD route. The prospective probe invocation is:

```bash
uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py \
  --owner "$ATTEMPT_ID" --source oatd --receipt "$LEASE_RECEIPT" \
  --wait 60 --lease-timeout 360 -- \
  uv run --offline "$PROBE" --execute \
    --cdp-url http://127.0.0.1:9222 \
    --query 'CubeSat AND SysML' --field-label 'title' \
    --timeout-seconds 180 --poll-interval-seconds 0.2 \
    --challenge-wait-seconds 30 \
    --challenge-poll-interval-seconds 0.2 \
    --busy-retries 2 --busy-retry-delay-seconds 30 \
    --output-path "$PROBE_OUTPUT"
```

The 180-second deadline is absolute across the passive challenge wait, the
single native submission, post-submit polls, the existing 30/60-second busy
waits, and any reissues. The lease timeout is only supervision; it does not
extend source work. After verified owned-page cleanup and lease release, create
the immutable successor manifest, observations, and evidence index. Record
challenge passive-poll counts separately from busy reissue attempted/completed
counts. A blocked or failed successor remains diagnostic and cannot authorize a
final OATD event.
