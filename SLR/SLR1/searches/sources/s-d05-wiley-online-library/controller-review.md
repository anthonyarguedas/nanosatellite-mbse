# Controller review — Wiley Online Library P01

**Reviewed:** 2026-08-24

**Disposition:** blocked; not accepted; no P02 or final search authorized.

P01 remains immutable at [`S-D05-P01-20260824T124916-0400`](pilots/S-D05-P01-20260824T124916-0400/). This review is not an approval record.

## Independent validation

The controller independently confirmed:

- the manifest passes the tracked schema with format checking and retains the diagnostic-only, no-screening, no-import, blocked, null-total, and zero-record invariants;
- every packet JSON file parses, every indexed evidence hash resolves, all local Markdown links resolve, and `git diff --check` passes;
- all nine draft cells reproduce the v4 partition expressions, contain exactly the expected quoted literals and pair cross-products, contain no wildcard or extra term, and match their recorded hashes and lengths;
- pair-bearing cells remain explicitly final-use-prohibited and no source total is claimed;
- the event log contains no Wiley query invocation or `/action/doSearch` request, the restricted-capture ledger is empty, and `final-events/` remains untouched;
- the exact preflight anchor survived the complete controller window as the sole page target; launcher/version checks passed, AC power and open-clamshell state were observed, and no actual Sleep/Wake/DarkWake event occurred; and
- the shared search-infrastructure validator passes.

The controller independently reproduced the output defect against adapter SHA-256 `360ac76f2f0d3530660ce868523eeb4caab809f2e5fd6bcc39da513652bf1205`: both pre-existing JSON and CSV sentinels were replaced without a browser or network request.

A durable ignored copy of the controller preflight/postflight evidence is at `.searches/s-d05-wiley-controller/S-D05-P01-20260824T124916-0400/`. Its `SHA256SUMS` file has SHA-256 `0cdaf69526bdff78d1d1d4648e49ac079f464472df8ab2b09947d1daec5e3952`.

## Implementation classification

`code_issue=true` is confirmed for P01. Replacing an existing normal result or error destination can destroy an immutable pilot/final-event artifact. This is an implementation defect, not a Wiley source failure and not a zero result. Stopping before source use was correct.

No live claim about Wiley's boundary, fields, parser, phrases, expansion, pair handling, controlled/indexed terms, date or language controls, tabs, totals, pagination, identity, export, or completeness is accepted.

## Separate code-only remediation

A separate worktree subagent committed the scoped remediation without any browser, network, Wiley, or source operation:

- **commit:** `c8be56c87fe17f413de7c083b49f3bfebfca5bc7` (`Refuse Wiley output clobbers`)
- **base:** `702063f1aedf36337e1233e31e9cb083bd38c7c1`
- **branch:** `wiley-no-clobber-20260824-131248-21819-19860`
- **adapter SHA-256:** `e340e649038e75fd6ada684f708940b6f4eec4b844a59c9e0697a9f25179ff8d`
- **test SHA-256:** `aa81bc0e7eb97870cf243c4f7a2de80ae16500046c0cc4946d5edcace4bc08c0`

The patch changes only the Wiley adapter and a new Wiley-focused test file. It rejects existing files and symlinks before source work, stages success and error outputs beside their destinations, publishes with atomic create-if-absent hard links, and rolls back only identity-matching artifacts if a JSON/CSV pair cannot complete. It does not change query, browser, source-control, retrieval, RIS, or PRISMA semantics. It fails closed on a filesystem that cannot create hard links.

Independent controller runs passed:

- 41 focused/relevant tests plus 2 subtests;
- the complete academic-search suite: 145 tests plus 60 subtests;
- `py_compile`, Ruff lint, and `git diff --check`.

This commit is a code-only candidate, not live source validation and not acceptance of P01.

## Methodological impact

P01 supports no protocol semantic change. Its draft translations are construction evidence only. `S-D05`, `TASKS.md`, `search-log.md`, and the Part 2 source index must remain pending. `P-001` remains unresolved; the P01 date is not a common cutoff.

## Decision required

The review owner must decide whether to authorize one corrective P02 using exactly adapter commit `c8be56c87fe17f413de7c083b49f3bfebfca5bc7`.

Recommended P02 scope:

1. repeat the dedicated browser/power/version/anchor preflight and verify the pinned adapter/test hashes;
2. run one small health gate, stopping on access, rewrite, source, or implementation failure;
3. if healthy, test the current full-platform boundary, Articles & Chapters and Collections routes, field inventory, parser contrasts, query echo, expansion, proximity/same-field behavior, controlled/indexed-term surfaces, date/language controls, ordering, page size, totals, and explicit zero;
4. regenerate and submit every supported A1–BT2 cell count-only only after its parser, field, pair, and length gates pass;
5. exercise a naturally bounded two-page, two-pass stable-identity and page-scoped RIS export method without screening relevance; and
6. stop after P02 without self-approval, retry, final search, screening, candidate import, central integration, or commit.

**Human decision:** the review owner authorized this exact P02 scope at 2026-08-24T13:34:55-04:00. The authorization does not alter P01 or permit a final search or automatic retry.
