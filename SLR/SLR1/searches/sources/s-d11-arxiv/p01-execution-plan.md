# P01 execution plan — arXiv Advanced Search

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


**Status:** source-free launch plan for brand-new source `S-D11-P01-<UTC timestamp>`. No campaign, manifest, attempt, receipt, count, zero, failure, or observation is pre-created by this commit. P01 is diagnostic only and must not screen, import, merge, or create a final event.

## Fixed scope and invariants

- Use only the full arXiv repository through the normal rendered Advanced Search page and the current owned-page adapter at `academic-research/skills/academic-search/scripts/search_arxiv.py`.
- Use the exact nine UTF-8 query cells and the exact all-fields translations in [`translation-spec.json`](translation-spec.json). Do not add S-C01 candidates, wildcards, category descriptors, language filters, publication-type filters, access filters, or a narrower query.
- Use `date-filter_by=date_range`, `date-date_type=submitted_date`, lower year `2011`, and the actual P01 UTC execution **year** as the upper diagnostic bound. Record this as a pilot-date submitted-year diagnostic bound only; it is not P-001, not an exact day cutoff, and not a publication-date claim.
- Run all source operations sequentially in one attached browser-lease phase. The runner permits at most **11 source operations**: nine count-only cells, one conditional two-record metadata/abstract diagnostic, and one conditional two-page pagination diagnostic.
- Keep `diagnostic_only=true`, `screening_performed=false`, `candidate_import_permitted=false`, and `candidate_records_imported=0`. Count-only rows and metadata/abstract rows are not candidates.
- Use the stable bare arXiv ID for source identity. Preserve an explicitly rendered `vN` suffix separately; never infer `v1`, use DOI/title/rank as an identity fallback, or merge a preprint with a formal report during P01.
- Treat the visible Submitted date and submitted-year projection as arXiv metadata. **Never treat an arXiv posting/submission date as another source's publication date.**

## Runtime campaign and manifest creation

P01 is a brand-new source. Before any source work, the controller must create the initial campaign and manifest at runtime from:

- `SLR/SLR1/searches/templates/pilot-campaign.template.json`; and
- `SLR/SLR1/searches/templates/pilot-manifest.template.json`.

Do not copy a completed campaign from another source and do not commit these runtime artifacts in the launch bundle. Replace the template identity fields with the values below, compute the protocol and dictionary SHA-256 fingerprints from the current workspace, and write only under the new attempt directory:

```text
TASK_ID=S-D11
SOURCE_ID=arxiv
METHOD_TYPE=direct
CAMPAIGN_ID=S-D11-C01-<YYYYMMDDThhmmss+0000>
ATTEMPT_ID=S-D11-P01-<YYYYMMDDThhmmss+0000>
```

The initial campaign must contain exactly one `initial` attempt, the frozen 12-gate catalog from the shared validator, `status=in_progress`, an empty operation/evidence list before live work, the shared null retry policy (`maximum_retries=0`), and the fixed source-operation maximum of 11. Its diagnostic/import flags remain false/zero. The initial manifest must use the same runtime IDs, `method_type=direct`, `source_id=arxiv`, normal rendered Advanced Search interface, unauthenticated/public route, and no fabricated execution, count, artifact, or evidence entries. Finalize and hash the immutable manifest only with the actual terminal outcome and receipts; update `campaign.json` only after the supervised phase. Do not create a fake completed campaign or attempt.

The controller then creates the runtime-only directories (not final-events):

```bash
ROOT="$(git rev-parse --show-toplevel)"
AGENT_TOOLS="$(cd "$ROOT/../agent-tools" && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%S)+0000"
ATTEMPT_ID="S-D11-P01-$STAMP"
PILOT_YEAR="$(date -u +%Y)"
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d11-arxiv"
ATTEMPT_DIR="$PACKET/pilots/$ATTEMPT_ID"
OUTPUT_ROOT="$ATTEMPT_DIR/outputs"
mkdir -p "$OUTPUT_ROOT" "$ATTEMPT_DIR/receipts" "$ATTEMPT_DIR/logs"
```

Use the same `ATTEMPT_ID` for the campaign, manifest, runner receipt, lease receipt, output directory, and every evidence link. If the ID or any destination already exists, stop and allocate a new timestamp; never overwrite an attempt.

## Source-free preflight

Run these commands before acquiring a browser lease. They make no provider request:

```bash
ROOT="$(git rev-parse --show-toplevel)"
AGENT_TOOLS="$(cd "$ROOT/../agent-tools" && pwd)"
cd "$AGENT_TOOLS/academic-research/skills/academic-search"
uv run --offline pytest -q tests/test_search_arxiv_browser.py

cd "$ROOT"
uv run --offline pytest -q SLR/SLR1/scripts/test_arxiv_p01_runner.py
uv run --offline SLR/SLR1/scripts/validate_search_infrastructure.py --mode pre-final
uv run --offline "$AGENT_TOOLS/academic-research/skills/academic-search/scripts/search_arxiv.py" --help >/dev/null
python3 SLR/SLR1/scripts/arxiv_p01_runner.py --help >/dev/null

sha256sum \
  "$AGENT_TOOLS/academic-research/skills/academic-search/scripts/search_arxiv.py" \
  "$AGENT_TOOLS/academic-research/skills/academic-search/tests/test_search_arxiv_browser.py" \
  SLR/SLR1/scripts/arxiv_p01_runner.py \
  SLR/SLR1/searches/sources/s-d11-arxiv/translation-spec.json \
  SLR/SLR1/searches/sources/s-d11-arxiv/queries/*.arxiv-advanced.txt
```

Record the exact adapter/test hashes and the preflight result in the runtime manifest/evidence index. A failed offline test, changed query hash, validator failure, or adapter help failure stops P01 before any lease.

## Operation order and gates

`arxiv_p01_runner.py` is the trusted local runner. It reads the exact query files, invokes the adapter with fixed attached-browser flags, writes unique JSON/log paths, stops on the first failed operation, and writes one runner receipt. It never launches Chrome, chooses a browser/profile/port, screens records, imports records, or writes CSV.

| Order | Operation | Query and flags | Maximum | Gate/evidence purpose | Transition |
| --- | --- | --- | ---: | --- | --- |
| 1–9 | Count-only translation checks in this exact order: `A1`, `A2`, `A3`, `B1`, `B2`, `BG1`, `BG2`, `BC1`, `BT2` | Each corresponding `queries/<ID>.arxiv-advanced.txt`; `--count-only --limit 1 --max-pages 1 --skip-full-abstracts`; all-fields; `--year-start 2011 --year-end $PILOT_YEAR` | 9 | Query transport/echo, all-fields boundary, submitted-year controls, fixed unfiltered controls, explicit positive/zero/failure accounting; translation-specific totals | Run the next cell only after the previous output is a reconciled count-only success or explicit zero. Stop on failure, challenge, busy/service state, rewrite, or output error. |
| 10 | Small metadata/abstract diagnostic | The first positive count in fixed order `B1, A1, A2, A3, B2, BG1, BG2, BC1, BT2`; `--limit 2 --max-pages 1` with full abstracts enabled; same date/field controls | 1 | At most two rendered rows: title, authors, stable base ID, optional explicit version, submitted-date label, native abstract/More behavior, canonical abstract/PDF routes, and bounded retrieval | Run only when all nine counts succeeded and at least one total is positive. If all nine are explicit zero, record “not run: no positive diagnostic set” and do not invent a record. Stop on any mismatch or failure. |
| 11 | Conditional pagination diagnostic | The selected operation-10 query only; `--limit 101 --max-pages 2 --skip-full-abstracts`; same controls | 1 | Native page-size/range/Next behavior and stable IDs across a second rendered page; no abstract fan-out | Run only when operation 10's source total is greater than 100, because the adapter selects native page size 100 for this bound. If total is 100 or less, record “not run: no natural second page under the fixed bound”; do not substitute another query or claim pagination passed. |

Count-only `source_reported_total > 0` is a positive count with zero retained records, not a zero-result search. A native no-results page with exact controls is `explicit_zero` and total `0`. Any adapter nonzero exit or missing/malformed output is `failed` with total `null`; the runner stops and never interprets a partial prefix.

The count operations can support source boundary, query transport, all-fields control, date-control, and no-discovery-limit observations only when the rendered evidence proves them. The metadata operation can support bounded retrieval and row identity/version/abstract diagnostics. The pagination operation can support only the exercised page transition. Controlled-vocabulary absence, language semantics, exact date/version eligibility, two-pass final completeness, and any unexercised gate remain `untested`; do not mark them passed from offline code or a count.

## Exact attached shared-lease phase

Use one new immutable lease receipt for the complete phase. Do not acquire one lease per query, do not use another wrapper, and do not pass a browser/profile/port override. The normal shared route uses the adapter's single proven shared context and creates its own page; it does not require or navigate an existing arXiv target. An optional `--target-id` remains available only when the controller already has a separately authorized arXiv page and deliberately chooses that proof route; it is not part of P01.

```bash
ROOT="$(git rev-parse --show-toplevel)"
AGENT_TOOLS="$(cd "$ROOT/../agent-tools" && pwd)"
ATTEMPT_ID='S-D11-P01-<runtime timestamp>'
PILOT_YEAR='<actual UTC execution year>'
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d11-arxiv"
ATTEMPT_DIR="$PACKET/pilots/$ATTEMPT_ID"
OUTPUT_ROOT="$ATTEMPT_DIR/outputs"
LEASE_RECEIPT="$ATTEMPT_DIR/receipts/shared-lease.json"
RUNNER_RECEIPT="$ATTEMPT_DIR/receipts/runner.json"
LEASE="$AGENT_TOOLS/internet/skills/browser/scripts/run_with_browser_lease.py"
ADAPTER="$AGENT_TOOLS/academic-research/skills/academic-search/scripts/search_arxiv.py"
RUNNER="$ROOT/SLR/SLR1/scripts/arxiv_p01_runner.py"

caffeinate -dims uv run "$LEASE" \
  --owner "$ATTEMPT_ID" \
  --source arxiv \
  --receipt "$LEASE_RECEIPT" \
  --lease-timeout 900 \
  -- python3 "$RUNNER" \
    --packet "$PACKET" \
    --output-root "$OUTPUT_ROOT" \
    --runner-receipt "$RUNNER_RECEIPT" \
    --attempt-id "$ATTEMPT_ID" \
    --pilot-year "$PILOT_YEAR" \
    --adapter "$ADAPTER" \
    --timeout 30 \
    --page-delay-seconds 0.2
```

The wrapper's complete phase includes health checks, the runner and all child adapter invocations, finite waits, cleanup, and verified lease release. The controller must verify before interpreting outputs:

- the fixed endpoint `127.0.0.1:9222`, one CfT process/profile assertion, browser epoch/version, protected broker-anchor preservation, and power/sleep checks;
- the attached trusted runner, one unambiguous shared browser context, and adapter-owned-page creation;
- one adapter-owned page at a time, no mutation of the broker anchor, and verified closure of every owned page;
- global arXiv pacing decision, sequential operation order, 30-second adapter timeout, 0.2-second inter-page delay, no automatic reissue, and no fresh browser/profile/port; and
- the lease receipt's acquisition, terminal outcome, release, and verified release.

The current adapter's finite state poll may observe a normal browser challenge without interacting with it. A challenge, login, CAPTCHA, anti-automation page, busy/service page, timeout, or access failure is not retried automatically. Keep the same page until the finite timeout/cleanup decision, then stop; never rotate identity or reissue a failed source operation. A user stop is `cancelled`, not a provider failure, and requires child collection, owned-page closure, anchor preservation, and verified lease release.

## Output and checkpoint procedure

The runner writes only unique attempt-local outputs and logs:

```text
pilots/<ATTEMPT_ID>/
├── outputs/A1.count.json ... outputs/BT2.count.json
├── outputs/<selected>.metadata-abstract.json       # conditional
├── outputs/<selected>.pagination.json               # conditional
├── outputs/*.log
└── receipts/runner.json
```

The lease wrapper writes the distinct `receipts/shared-lease.json`. Do not request `--csv-output-path`; count-only and pilot diagnostics are non-mergeable. Abstract and metadata captures remain diagnostic and rights-controlled; if a capture cannot be committed safely, keep it outside Git and record only its safe evidence index/hash.

After the supervised child exits:

1. Verify the lease receipt, runner receipt, owned-page cleanup, anchor preservation, and release before reading source totals.
2. If the phase failed or was cancelled, record every failed/conditional operation with `total=null` where required, discard all prefixes, set campaign status narrowly (`technically_blocked`, `cancelled`, or `in_progress` as applicable), and import zero records.
3. If a count output reports an exact native zero, record `explicit_zero` and `0`; do not convert it to failure or use it to screen.
4. Create the immutable manifest/evidence index from the runtime templates, hash every retained diagnostic artifact, and checkpoint `campaign.json`. Carry forward only exact-hash evidence for unaffected passed gates; a failed gate invalidates only declared dependents.
5. Run the shared validator again. P01 cannot be accepted unless every required gate has current observed/documented evidence, all nine cells are accounted for, failure/zero behavior is explicit, no methodological decision is pending, and no screening/import occurred.
6. Leave `final-events/` untouched. P01 results never become PRISMA identification records or candidates.

## Hard stops

Stop source work immediately, without another source operation, on any of:

- failed offline test/validator, missing query, query hash drift, ID collision, output collision, or runner bound violation;
- lease, browser epoch/version, profile/process, endpoint, broker-anchor, power/sleep, shared-context, or cleanup/release failure;
- non-arXiv route, login/challenge/CAPTCHA/anti-automation state, busy/service error, timeout, nonzero adapter exit, or untrusted child;
- query rewrite, missing exact all-fields echo, changed operator/date/classification/abstract/page/sort control, malformed total/range, hidden cap, short/stale page, changed total, missing/duplicate/conflicting base ID or version route, native abstract expansion failure, or page sequence mismatch;
- any request to use a fresh browser/profile/port, API fallback, source category restriction, English/publication-type/access filter, wildcard, narrower query, alternate date interpretation, or screen/import a record; or
- inability to verify that every failed/blocked/cancelled operation wrote no importable prefix and that the shared lease was released.

A late optional pagination diagnostic not run because its predeclared total condition is false does not erase successful count/metadata evidence; it remains explicitly untested and does not make the source accepted.
