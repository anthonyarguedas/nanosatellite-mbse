# Resume plan — S-D09-C01-20260824T161325-0400

> **Current validation policy:** Follow the [live-first source-pilot policy](../../live-first-validation-policy.md). It supersedes any broader offline-suite prerequisite below: run only the minimum launch gate, inspect failures on the real owned page, patch technical defects immediately, and retest live after minimal changed-path checks.


**Status:** `technically_blocked`. Exactly one additional controller-technical
successor is prospectively authorized by `D-TECH-NEXT-P05`; no attempt ID,
lease, browser phase, or source operation exists yet. No new human
methodological authorization is required.

## Carries forward

- `G-BOUNDARY` from P01 [`official-source-documentation-receipt.json`](pilots/S-D09-P01-20260823T232059-0400/official-source-documentation-receipt.json), SHA-256 `c8674a1d8064e5092399d7cf3d041de40de7272959eff3ca11f19ed6c20781ce`.
- `G-BASIC-PARSER`, `G-BASIC-COUNT`, and `G-QUERY-CONSTRUCTION` from P02, including [`observations.md`](pilots/S-D09-P02-20260824T105026-0400/observations.md) SHA-256 `10fda2b860863e9b8a574486d8e34d45abd326b024b7a6d047296e37cc7a4133` and [`evidence-index.json`](pilots/S-D09-P02-20260824T105026-0400/evidence-index.json) SHA-256 `bf8a651955d125a33f4e12a77871e548cdb6322a3cf22519f1230c7d30d82d13`.
- Preserve P03 `G-V3-HEALTH` from [`evidence-index.json`](pilots/S-D09-P03-20260824T130849-0400/evidence-index.json), SHA-256 `a3ba5e55ce4a067d5de55c07e791f06b17218806218da03708a77d381194b674`.
- Preserve P04's challenge-before-submission null failure and its verified
  cleanup; do not reinterpret or reissue P04 O-001.

## One prospective technical successor

- Allocate exactly one fresh `S-D09-P05-<timestamp>` at runtime as
  `controller_technical`; the placeholder is not an attempt ID and is not
  created by this source-free change.
- **Source-operation maximum: 3:** one corrected advanced-form diagnostic,
  then at most two existing same-page busy reissues. Passive challenge polls
  are not source operations or busy retries.
- Before the one native submission, retain the same owned page and poll only
  its DOM at a fixed 0.2-second cadence for at most 30 seconds total. Do not
  click, reload, navigate, submit, solve, or bypass the challenge. Continue
  the original single guarded native submission only when the canonical
  advanced form appears. Persistent challenge or transition to login/access/
  CAPTCHA fails `null` with no retry or prefix.
- Preserve the existing post-submit busy policy: waits of 30 and 60 seconds,
  an exclusive safe busy state, and at most two canonical same-page reissues
  under the shared absolute 180-second deadline. If busy clears during a wait,
  do not reissue.
- Do **not** rerun P02 basic parser/count gates, P03 health, P04 O-001, planned
  cells, Record Details, strict traversal, CSV, or pair-completeness work.

The complete source-free launch procedure and hard stops are in
[`p05-execution-plan.md`](p05-execution-plan.md). No live phase is authorized
by this plan text alone; the controller must first pass its offline gates and
then allocate the one immutable successor ID.

## Shared browser and acceptance

Use the exclusive global shared CfT lease at `127.0.0.1:9222`, a new receipt,
protected-anchor preservation, and in-context owned-page cleanup. Acceptance
remains dependent on a reconciled advanced result, any exercised busy recovery,
and later pair/control/detail/completeness evidence; no screening, import, or
final event is permitted.
