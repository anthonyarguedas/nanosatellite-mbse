# P06 execution plan — NASA Technical Reports Server (NTRS)

> **Current validation policy:** Follow the [live-first source-pilot policy](../../live-first-validation-policy.md). It supersedes any broader offline-suite prerequisite below: run only the minimum launch gate, inspect failures on the real owned page, patch technical defects immediately, and retest live after minimal changed-path checks.


This plan prospectively authorizes exactly one `controller_technical` P06 under
`S-D13-C01-20260824T161325-0400`. It preserves P01–P05 and makes no
methodological change. The only live phase is one attached canonical shared-CfT
lease with at most two sequential operations.

## Allocation and immutable scope

- Attempt: `S-D13-P06-20260825T141120-0400`.
- Decision: `D-TECH-NEXT-P06`, controller-technical, maximum two source-phase
  operations, no human authorization required.
- Source: the public NTRS normal rendered first-party UI only.
- No API, HTTP/API probe, direct endpoint, page-side fetch/XHR, fallback,
  retry, second query, partition, date control, detail visit, export,
  completeness pass, screening, candidate import, prefix retention, or final
  event is permitted.
- The immutable diagnostic input is the existing P03 query file
  `pilots/S-D13-P03-20260824T125840-0400/queries/G01-minimal-nanosatellite.txt`.
  Its bytes must be exactly `nanosatellite` (13 UTF-8 bytes), SHA-256
  `3fc7d31e9abb58d42acd5c95a9549835545de822d0843e28265c6979b1a466d4`.
  P03 and its query are not edited or copied into a new query file.
- The health operation is record-free and is a prerequisite, not a search
  result. The adapter operation is diagnostic count-only and cannot be merged.

## Fixed operation order and gates

1. **`NTRS-P06-SOURCE-HEALTH`** — exactly one owned-page navigation to the
   public NTRS root through `ntrs_source_health_probe.py`:
   `--execute --cdp-url http://127.0.0.1:9222 --timeout-seconds 30
   --stabilization-interval-seconds 0.2`. It must produce a record-free
   receipt with one navigation, a 2xx normal source route, source identity,
   visible search surface, two stable samples, no challenge/access/login/
   busy/error state, null source total, zero records, and verified owned-page
   cleanup. Any other result stops P06; operation 2 is not invoked.
2. **`NTRS-P06-RENDERED-G01`** — only after operation 1 passes, invoke the
   current d872f59-pinned rendered adapter once with exactly:
   `--query nanosatellite --limit 1 --max-pages 1 --count-only
   --skip-full-abstracts --timeout 90 --page-delay-seconds 0
   --detail-delay-seconds 0 --cdp-url http://127.0.0.1:9222`. No year/date
   option, `--require-complete`, CSV, detail, export, or alternate route is
   allowed. A positively reconciled rendered total or native explicit zero is
   diagnostic only; an error is record-free with `total=null`.

The full browser-backed phase, including both operations, cleanup, and lease
release, runs attached through exactly:

```text
caffeinate -dims uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py \
  --owner S-D13-P06-20260825T141120-0400 \
  --source ntrs \
  --receipt .searches-d13-ntrs/S-D13-P06-20260825T141120-0400/browser-lease-receipt.json \
  --wait 30 --lease-timeout 600 -- COMMAND...
```

The command after `--` is a trusted local adapter/probe client. It must use the
canonical endpoint and shared profile supplied by the lease and must create
and close only adapter-owned pages. The protected broker anchor is never
navigated or closed. A three-second passive interval between the two distinct
operations is allowed as pacing only; it is not a retry and does not authorize
an additional source request.

## Source-free gates before the lease

Before acquiring the lease, verify and record:

- complete source-pilot/controller/checklist reading and evidence plan;
- exact 13-byte query bytes and SHA-256;
- current shared adapter commit exactly `d872f59f5f20913fbd0ef4de16ea2ab79a6bc883`;
- current `search_ntrs.py` and focused test hashes, plus helper/domain-note
  hashes;
- d872f59 focused NTRS tests (38), health-probe tests (14), both CLI help
  checks, `uv run ...validate_search_infrastructure.py --mode pre-final`, and
  `git diff --check`;
- clean adapter-specific status in the shared checkout (unrelated shared
  dirty paths are not edited); and
- read-only canonical browser status: one current proven CfT epoch, matching
  runtime/on-disk version, one inert anchor, one top-level profile owner, and a
  free lease. Record only sanitized health facts.

No source work begins if any deterministic source-free check fails. Correct a
source-free packet/check issue before the lease; do not consume a live
operation for it.

## Terminal handling and immediate investigation rule

Stop after the first terminal source condition. Preserve every output and the
lease/cleanup result under this P06 packet/restricted namespace. Never turn a
failure, blank/loading state, challenge, access state, or adapter error into
zero, and never retain a partial prefix. If a technical failure occurs,
remain attached until cleanup/release is verified, then immediately perform a
source-free investigation using the record-free artifact, current d872f59
source/tests, and bounded allowlisted browser status only when needed to
classify browser/lease state. Record the concrete failure stage and the
smallest behavior-preserving repair or confirmed absence of an additional
repair; do not stop at an unqualified “diagnosis required.” Do not reissue the
failed source operation and do not allocate another source operation inside
P06.

If operation 2 succeeds, retain only a compact record-free rendered summary
and the exact count/zero classification; do not retain rows or abstracts. If
it fails, retain `total=null`, zero retrieved/imported records, and the
failure stage. In all cases screening, candidate import, PRISMA identification,
source acceptance, and final-event creation remain false.
