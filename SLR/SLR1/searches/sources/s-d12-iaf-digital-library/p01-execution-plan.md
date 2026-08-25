# S-D12 P01 execution plan

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


**Status:** launch bundle only. P01 has not run. This source is new: the
controller must create the first campaign and manifest at runtime from the
shared templates before any source request. No campaign, attempt, observation,
screening record, or candidate import is pre-created here.

## Runtime allocation and preflight

Run from the `nanosatellite/` repository root, serially, with no network during
offline preflight:

1. Confirm the protocol and dictionary are unchanged and record their SHA-256
   fingerprints. Confirm the source packet has the nine partition entries and
   all query files are present, UTF-8, and at most 499 characters excluding
   their terminal LF. Validate the translation algebra before source work.
2. Create a fresh UTC timestamp and verify that no prior path uses it:
   `STAMP=<UTC YYYYMMDDThhmmss+0000>`,
   `CAMPAIGN_ID=S-D12-C01-$STAMP`, and
   `ATTEMPT_ID=S-D12-P01-$STAMP`. Do not reuse an ID or output path.
3. Copy and instantiate `searches/templates/pilot-campaign.template.json` and
   `searches/templates/pilot-manifest.template.json` into
   `SLR/SLR1/searches/sources/s-d12-iaf-digital-library/` only at runtime.
   Set task `S-D12`, source `iaf-digital-library`, method `direct`, the two
   runtime IDs, current protocol/dictionary fingerprints, diagnostic-only
   flags, and the initial attempt allocation. Write and validate the manifest
   before the first source operation, then checkpoint the campaign after the
   attempt. Do not claim completion merely because the files validate.
4. Create unique absent directories under
   `pilots/$ATTEMPT_ID/{outputs,receipts}`. Outputs are create-only: if any
   destination or terminal marker already exists, stop before source work.
5. Use the current public HTTP adapter only:
   `../agent-tools/academic-research/skills/academic-search/scripts/search_iaf_digital_library.py`.
   Do not use a browser, CfT lease, API route, event restriction, credentials,
   profile, or alternate port.

The adapter is source-free tested with `python3` before P01. A later operator
may use `uv run` for its PEP 723 dependencies; the exact adapter flags below
are the contract. No command below is to be run during this preparation.

## Diagnostic bound and fixed policy

Set `PILOT_YEAR=$(date -u +%Y)` at runtime. The diagnostic date controls are
`--year-start 2011 --year-end "$PILOT_YEAR"`. They are inclusive
**client-side publication-year** controls, not the common evidence cutoff and
not a final exact-date claim. The adapter must leave the executed `q` text
unchanged and report the source total before year exclusions. Do not pass
`--event-code`; the default full-library boundary is required.

Every invocation uses:

```text
--limit 1 --max-pages 1 --timeout 20 --request-delay-seconds 1 --retries 1
```

This permits at most one same-operation retry for a transient status/network
failure. The adapter's finite retry delay is bounded; it never retries a
challenge or access denial. All four operations are sequential. The P01
maximum is **four adapter source operations** and, because the last operation
can make one search request plus one detail request, **ten HTTP request
attempts** in total (2 + 2 + 2 + 4). `--count-only` operations make no detail
request. The controller writes one safe receipt at each listed receipt path;
receipts contain operation status/counts and no credentials, cookies, or
session values.

## Exact operation order

`ADAPTER=../agent-tools/academic-research/skills/academic-search/scripts/search_iaf_digital_library.py`
and `PACKET=SLR/SLR1/searches/sources/s-d12-iaf-digital-library` are relative
to the repository root. The controller substitutes the runtime attempt path
for `$PILOTS`.

1. **Health / public-route count** — query exactly
   `$(cat "$PACKET/diagnostics/health-query.txt")`, with `--count-only`, and
   write only to `$PILOTS/outputs/01-health.json`; receipt:
   `$PILOTS/receipts/01-health.json`. A positive or explicit native zero is a
   transport observation; it is not a review result.
2. **Planned-query echo and count** — query exactly the first cell
   `$(cat "$PACKET/queries/A1.iaf.txt")`, with `--count-only` and the
   diagnostic year flags, to `$PILOTS/outputs/02-A1-count.json`; receipt:
   `$PILOTS/receipts/02-A1-count.json`. This is one shard only and is not the
   A1 partition total.
3. **Explicit-zero diagnostic** — query exactly
   `$(cat "$PACKET/diagnostics/explicit-zero-query.txt")`, with `--count-only`,
   to `$PILOTS/outputs/03-explicit-zero.json`; receipt:
   `$PILOTS/receipts/03-explicit-zero.json`. The expected condition is an
   exact native no-results summary; any rewrite, error, challenge, or
   unreconciled response is not zero.
4. **Bounded retrieval / identity probe (conditional)** — only if operation 2
   returned a successful positive source total, rerun the exact first A1 cell
   without `--count-only`, with the diagnostic year flags, to
   `$PILOTS/outputs/04-A1-retrieval.json`; receipt:
   `$PILOTS/receipts/04-A1-retrieval.json`. It may retain at most one
   diagnostic detail record. It does not establish complete A1 retrieval.
   If operation 2 is an explicit zero, record operation 4 as not run and end
   the attempt after the zero check.

The command shape for each operation is:

```text
uv run "$ADAPTER" --query "$(cat QUERY_FILE)" [--count-only] \
  [--year-start 2011 --year-end "$PILOT_YEAR"] \
  --limit 1 --max-pages 1 --timeout 20 --request-delay-seconds 1 --retries 1 \
  --output-path "$PILOTS/outputs/UNIQUE-NAME.json"
```

Do not add `--csv-output-path` to this diagnostic phase. Do not redirect an
adapter error into a zero. The adapter's normalized JSON/error artifact and
the controller receipt are both diagnostic-only.

## Capability gates and transitions

Record the following gate disposition in the runtime campaign; a P01 result
supports a gate only when the stated observation is actually present:

| Gate | P01 operation/evidence | P01 limit |
|---|---|---|
| `G-SOURCE-BOUNDARY` | 01 plus source-route/echo evidence | Full collection coverage remains untested. |
| `G-QUERY-TRANSPORT` | 02 exact query echo | Only one shard is exercised. |
| `G-FIELD-BOUNDARY` | 02 query-route evidence | Unqualified field scope and cross-field behavior remain untested. |
| `G-CONTROLLED-VOCABULARY` | Offline packet declaration; no live descriptor claim | No accepted descriptor. |
| `G-DATE-CONTROL` | 02 and, if run, 04 retained year settings | Year-only client filtering is not exact P-001 date validation. |
| `G-LANGUAGE-CONTROL` | None | No native English control is adopted; screening remains required. |
| `G-CONTENT-CONTROL` | None | No prohibited discovery limit is adopted. |
| `G-RETRIEVAL` | 04 only if positive and detail reconciles | One bounded detail is not complete retrieval. |
| `G-PAGINATION-CONTROL` | 01/02 one-page range and fixed-page-size checks | No exhaustive traversal or stable order proof. |
| `G-PAGE-IDENTITY` | 04 card/detail event-paper reconciliation | Only one identity, if any. |
| `G-COMPLETENESS` | None accepted by P01 | Requires complete cell traversal and two-pass/equivalent proof. |
| `G-FAILURE-BEHAVIOR` | 03 plus adapter fail-closed artifacts | Challenge and all failure classes remain conditional unless observed. |

Transitions are strict:

- A challenge, login, CAPTCHA, redirect, access denial, unsafe route, query
  rejection, malformed page, changed echo/total/range, duplicate identity,
  detail mismatch, or exhausted transient retry sets the affected total to
  `null`, stops source writing, and stops the attempt. Do not reissue a failed
  source operation in the same attempt.
- If operation 1 fails, do not run operations 2–4. If operation 2 fails or has
  `total=null`, do not use operation 3 to mask it. If operation 3 is not an
  exact native zero, do not run operation 4. A persistent busy response is a
  failure after the one permitted same-request retry; a challenge is never
  retried.
- If operation 4 is reached, retain only the adapter's reconciled diagnostic
  record. A short page, limit stop, year exclusion, or one-pass traversal is
  `partial`, never complete. No P01 record is screened or imported.
- On every stop, write the immutable manifest terminal outcome and receipt
  references, verify no adapter child remains, and checkpoint the campaign.
  Do not create a second attempt unless a controller later allocates it with a
  new timestamp and an explicit technical correction; a methodological change
  requires the owner.

## Post-P01 boundary

The 664 exact cells in `translation-spec.json` are the only planned direct
partitions. A later accepted final phase must execute every cell serially,
retain a unique create-only artifact and receipt per cell/pass, and reconcile
stable `(event_code, paper_number)` IDs only after all cells are complete. Any
failed cell makes its partition incomplete and imports no prefix. The current
adapter's bounded one-pass P01 is not a final-search completeness runner.

No final event may use the pilot-year upper bound. Before any final event,
resolve P-001 and the exact-date/local-filter treatment, validate current
field and pair semantics, establish stable ordering and two-pass completeness,
and update the campaign/guideline through the shared controller process. This
source phase must remain serial and must not overlap another live source phase
under current policy.
