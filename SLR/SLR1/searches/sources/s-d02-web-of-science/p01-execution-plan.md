# S-D02 P01 execution plan — Web of Science Core Collection

> **Current validation policy:** Follow the [live-first source-pilot policy](../../live-first-validation-policy.md). It supersedes any broader offline-suite prerequisite below: run only the minimum launch gate, inspect failures on the real owned page, patch technical defects immediately, and retest live after minimal changed-path checks.


**Status:** planned, source-free, not executed. **Attempt kind:** initial. **Source operation maximum:** 1 query submission. **Query:** `queries/A1.wos-topic.txt` only (non-pair). **Probe:** `SLR/SLR1/scripts/wos_core_pilot_probe.py`. **Pilot upper bound:** the attempt's execution date; the example below uses `2026-08-25`. It is not `P-001` and is not a final cutoff.

## Runtime allocation and paths

Before any source action, generate the timestamp and paths exactly once:

```bash
ROOT="$(git rev-parse --show-toplevel)"
STAMP="$(date '+%Y%m%dT%H%M%S%z')"
CAMPAIGN_ID="S-D02-C01-$STAMP"
ATTEMPT_ID="S-D02-P01-$STAMP"
PILOT_DATE="$(date '+%F')"
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d02-web-of-science/pilots/$ATTEMPT_ID"
test ! -e "$PACKET"
mkdir -p "$PACKET"
```

Create `campaign.json` and `$PACKET/manifest.json` from `SLR/SLR1/searches/templates/pilot-campaign.template.json` and `SLR/SLR1/searches/templates/pilot-manifest.template.json`, replacing all fixture identities, source/method fields, fingerprints, gate states, operation counts, and terminal placeholders rather than retaining example evidence. `$PACKET` is the unique P01 output namespace. Create new, absent `$PACKET/shared-lease-receipt.json` and `$PACKET/wos-probe-receipt.json` paths; do not pre-create either receipt. `PILOT_DATE` is the pilot-date diagnostic upper bound only. The timestamp is reused in every identity and path. This is a brand-new source: no completed campaign or attempt is pre-created in this packet.

## Exact order and bounds

1. Complete the shared-CfT preflight and record owner, source, browser epoch/provenance, broker-anchor health, power/sleep state, global pacing decision, and the one new lease receipt path. Stop if any preflight fact is unavailable.
2. Acquire exactly one shared lease and run one attached trusted local runner at `127.0.0.1:9222`. Do not launch a browser, use a fresh profile/port, create another tab, or call another endpoint.
3. The probe creates one owned page and navigates once to the normal Basic Search route. It verifies Core Collection, the current all-editions picker (Select All plus every current edition checked), Topic, Publication Date, English, and absence of Document Type.
4. It fills the exact A1 Topic query and the diagnostic date range `2011-01-01` through the attempt execution date, then performs exactly one visible native submit. No query retry, challenge retry, export, record open, Next click, or final retrieval is allowed.
5. The probe passively polls under a 60-second absolute bound. It accepts only the exact native zero or a summary state with positive total, submitted-control checks, page size 50, page 1 identity, and two equal expected lazy-card cardinality samples. It records aggregate stable-ID availability and Export-control presence without retaining IDs, result text, URLs, or records.
6. On challenge/busy/access/parser/timeout/control/card/identity/cleanup failure, stop with `total=null`; do not turn a failure into zero. Close the owned page while still attached and verify target disappearance, baseline preservation, and exact target-set restoration before lease release.
7. The controller writes/checkpoints the immutable manifest and campaign evidence. Keep the attempt diagnostic-only with zero screening and zero candidate imports.

## Runner invocation

Run only this shape from `$ROOT`, with the runtime variables above. `caffeinate -dims` supervises the complete attached lease child, and `uv run` invokes the non-executable PEP 723 probe safely:

```bash
cd "$ROOT"
caffeinate -dims uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py \
  --owner "$ATTEMPT_ID" \
  --source wos-core \
  --receipt "$PACKET/shared-lease-receipt.json" \
  --wait 30 \
  --lease-timeout 120 \
  -- \
  uv run SLR/SLR1/scripts/wos_core_pilot_probe.py \
    --execute \
    --query-file SLR/SLR1/searches/sources/s-d02-web-of-science/queries/A1.wos-topic.txt \
    --date-upper "$PILOT_DATE" \
    --receipt "$PACKET/wos-probe-receipt.json" \
    --timeout-seconds 60 \
    --poll-interval-seconds 0.25
```

The wrapper receipt and probe receipt are distinct new files. The probe's `--receipt` is not reused on a corrective attempt.

## Gate coverage and conditional transitions

P01 can provide bounded evidence toward `G-SOURCE-BOUNDARY`, `G-QUERY-TRANSPORT`, `G-FIELD-BOUNDARY`, `G-DATE-CONTROL`, `G-LANGUAGE-CONTROL`, `G-CONTENT-CONTROL` (no Document Type), and the diagnostic portions of `G-FAILURE-BEHAVIOR`, `G-PAGINATION-CONTROL`, `G-PAGE-IDENTITY`, and `G-RETRIEVAL`. It cannot by itself pass final `G-COMPLETENESS`, stable identity, export reconciliation, controlled-vocabulary behavior, or final retrieval.

- **Native zero:** record explicit zero only when the exact alert and submitted-control checks pass; no lazy-card work follows.
- **Summary:** continue only when route/page/total/control checks pass; hydrate only the current page. A short card set, page drift, absent total, or missing control echo is null and terminal.
- **Challenge or busy:** preserve the same page, perform no reissue, and stop. No finite retry is authorized for P01.
- **Any cleanup or lease-release uncertainty:** keep supervision active and report unresolved cleanup; never accept the observation or detach an orphan.
- **Pair-bearing cells, descriptors, other eight partitions, final retrieval/export:** not run by P01. `NEAR/6` remains unvalidated and no methodological choice is made here.

No live claim, completeness claim, screening decision, candidate import, or protocol change is made by this plan.
