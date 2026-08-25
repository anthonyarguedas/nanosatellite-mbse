# S-D08 P01 execution plan — ProQuest Dissertations & Theses Global

**State:** launch-ready plan only. Do not execute this file during source-free preparation. No campaign, attempt, source total, or live observation exists yet.

## Runtime identity and campaign creation

At the actual start of P01, the controller creates both identifiers from the runtime start timestamp (including the local numeric offset), for example:

- `campaign_id = S-D08-C01-YYYYMMDDThhmmss+ZZZZ`;
- `attempt_id = S-D08-P01-YYYYMMDDThhmmss+ZZZZ`.

Do not copy an example timestamp or pre-create an attempt now. Allocate the runtime namespaces once:

```bash
ROOT="$(git rev-parse --show-toplevel)"
STAMP="$(date '+%Y%m%dT%H%M%S%z')"
ATTEMPT_ID="S-D08-P01-$STAMP"
CAMPAIGN_ID="S-D08-C01-$STAMP"
PILOT_DATE="$(date '+%F')"
PACKET="$ROOT/SLR/SLR1/searches/sources/s-d08-proquest-pqdt/pilots/$ATTEMPT_ID"
RESTRICTED="$ROOT/.searches/s-d08-proquest-pqdt/$ATTEMPT_ID"
test ! -e "$PACKET" && test ! -e "$RESTRICTED"
mkdir -p "$PACKET/receipts" "$RESTRICTED/outputs"
```

Before source work, copy the shared `templates/pilot-campaign.template.json` and `templates/pilot-manifest.template.json`, render them for `task_id=S-D08`, `source_id=proquest-pqdt`, `method_type=direct`, and bind the current protocol and dictionary SHA-256 fingerprints. The initial campaign is `in_progress`, diagnostic-only, no-screening, no-import, and has exactly one `initial` attempt. The manifest is created before the first browser action and remains immutable after the attempt.

Campaign bounds are predeclared: one P01 attempt, at most one later `technical_corrective` attempt, zero automatic methodological revisions, at most 16 source operations in this attempt, and no source-operation reissue. Use retry policy `RP-D08-P01-NONE` (`maximum_retries=0`, no busy reissue, no challenge reissue). A proposed change to query semantics, source/field boundary, date/language/content restriction, identity, capture, completeness, or PRISMA accounting is `human_methodological`, not a technical retry.

## Offline preflight (must finish before the lease)

1. Confirm `guideline.md`, `translation-spec.json`, and this exact query-file set are present and SHA-256-bound in the packet: `queries/A1.proquest-noft.txt`, `queries/A2.proquest-noft.txt`, `queries/A3.proquest-noft.txt`, `queries/B1.proquest-noft.txt`, `queries/B2.proquest-noft.txt`, `queries/BG1.proquest-noft.txt`, `queries/BG2.proquest-noft.txt`, `queries/BC1.proquest-noft.txt`, and `queries/BT2.proquest-noft.txt`. Do not edit the protocol, dictionary, crosswalk, shared logs, or another source packet.
2. Run the source-free packet test, the focused ProQuest/PQDT adapter tests, and both adapter `--help` commands. Confirm no output, receipt, campaign, manifest, screening, or import artifact already exists in the P01 namespace.
3. Set `PILOT_DATE` to the actual execution date `2026-08-25` for this planned overnight launch. The diagnostic bound is inclusive `2011-01-01` through `2026-08-25`; because PQDT's adapter has no separate date/language flags, the trusted runner appends `YR(2011-2026) AND LA(English)` to each diagnostic query. This is not P-001 and is not a final common cutoff.
4. Obtain the controller's shared-CfT health/provenance record, global ProQuest pacing decision, and supervised owner. The plan has no extra passive wait and no busy reissue policy.

## Shared lease and trusted runner

The complete live phase is sequentially run through exactly one new receipt and the shared loopback CfT lease. The runner never launches Chrome; it invokes the existing trusted PQDT adapter and the read-only field/thesaurus probe, one owned page at a time:

```bash
cd "$ROOT"
caffeinate -dims uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py \
  --owner "$ATTEMPT_ID" \
  --source proquest-pqdt \
  --receipt "SLR/SLR1/searches/sources/s-d08-proquest-pqdt/pilots/$ATTEMPT_ID/receipts/shared-lease.json" \
  --lease-timeout 900 \
  -- \
  uv run SLR/SLR1/scripts/proquest_pilot_runner.py \
    --source proquest-pqdt \
    --packet-root SLR/SLR1/searches/sources/s-d08-proquest-pqdt \
    --output-dir "$RESTRICTED/outputs" \
    --pilot-date "$PILOT_DATE" \
    --cdp-url http://127.0.0.1:9222 \
    --adapter-root ~/agent-tools/academic-research/skills/academic-search/scripts \
    --probe-script SLR/SLR1/scripts/proquest_field_thesaurus_probe.py \
    --execute
```



There is no `--fresh-browser`, `--headless`, profile override, alternate port, generic tab command, detached child, or second lease. The runner uses `search_pqdt.py` from agent-tools commit `17a64bf`, `--cdp-url http://127.0.0.1:9222`, `--timeout 30`, `--page-delay-seconds 0.2`, and `--detail-delay-seconds 0.2`. Field and partition operations use `--count-only --limit 1 --max-pages 1`. The conditional final operation uses `--require-complete --limit 40 --max-pages 2` only when the reconciled A1 count is 1–40. Each query is the exact file text followed by `AND YR(2011-2026) AND LA(English)`. The probe uses one owned page and projects only allowlisted field/thesaurus counts and booleans. Licensed dissertation metadata outputs are create-only under `$RESTRICTED/outputs/`, outside Git; the runner ledger is `$RESTRICTED/outputs/runner-ledger.json`; the lease receipt is the distinct rights-safe packet path above. After release, index only safe aggregate ledger/receipt hashes in the manifest; never copy a diagnostic record into Git.

The runner makes no retry. Its fixed sequence stops on the first nonzero adapter/probe result and writes only safe operation status. The adapter's finite 30-second readiness/interaction timeout is the maximum per operation; no `--wait` is declared. Global pacing is sequential with at least 0.2 seconds between source-page operations, subject to the controller's stricter domain pacing decision.

## Exact operation ledger and cap

The cap is **16 source operations**, in this exact order. This is deliberately a small bounded metadata diagnostic, not a completeness run.

| Order | Operation ID | Entry point and exact operation | Purpose / gates |
|---:|---|---|---|
| 1 | `O01-FIELD-THESAURUS-UI` | `uv run SLR/SLR1/scripts/proquest_field_thesaurus_probe.py --source proquest-pqdt --execute` under the same lease | Read one exact PQDT selection and normal Command Line surface; count visible title/abstract/subject/index/thesaurus controls without retaining page text. `G-SOURCE-BOUNDARY`, `G-FIELD-BOUNDARY`, `G-CONTROLLED-VOCABULARY`. |
| 2 | `O02-FIELD-TI` | `search_pqdt.py --query 'TI("CubeSat") AND YR(2011-2026) AND LA(English)' --count-only --limit 1 --max-pages 1 --timeout 30 --page-delay-seconds 0.2 --detail-delay-seconds 0.2` | Record-free dissertation title-field diagnostic. `G-QUERY-TRANSPORT`, `G-FIELD-BOUNDARY`, `G-DATE-CONTROL`, `G-LANGUAGE-CONTROL`, `G-CONTENT-CONTROL`. |
| 3 | `O03-FIELD-AB` | Same flags with `AB("CubeSat")` | Record-free abstract-field diagnostic. Same gates. |
| 4 | `O04-FIELD-SU` | Same flags with `SU("CubeSat")` | Record-free subject-field behavior diagnostic. `G-FIELD-BOUNDARY`, `G-CONTROLLED-VOCABULARY`. |
| 5 | `O05-FIELD-IF` | Same flags with `IF("CubeSat")` | Record-free indexed-term behavior diagnostic. `G-FIELD-BOUNDARY`, `G-CONTROLLED-VOCABULARY`. |
| 6 | `O06-FIELD-NOFT` | Same flags with `NOFT("CubeSat")` | Record-free free-text/metadata comparator. `G-QUERY-TRANSPORT`, `G-FIELD-BOUNDARY`. |
| 7–15 | `O07-PARTITION-A1` through `O15-PARTITION-BT2` | For each exact file, in schedule order, pass `--query "$(cat queries/<ID>.proquest-noft.txt) AND YR(2011-2026) AND LA(English)" --count-only --limit 1 --max-pages 1 --timeout 30 --page-delay-seconds 0.2 --detail-delay-seconds 0.2` | Exercise all nine exact translations with zero retained records. `G-QUERY-TRANSPORT`, `G-FIELD-BOUNDARY`, date/language/content controls, and source failure behavior. |
| 16 | `O16-STRICT-A1` | Exact A1 plus the same suffix with `--require-complete --limit 40 --max-pages 2 --timeout 30 --page-delay-seconds 0.2 --detail-delay-seconds 0.2` | Run only if O07 reports an exact total of 1–40. Require two exhaustive passes with identical ordered numeric IDs. `G-RETRIEVAL`, `G-PAGINATION-CONTROL`, `G-PAGE-IDENTITY`, `G-COMPLETENESS`. |

`cat` above is only an exact local UTF-8 file read; the trusted runner performs the equivalent read and does not alter the query. No query file is split, narrowed, or rewritten. The final runner ledger must show `performed <= 16`, with no operation after a stop. PQDT count outputs retain no records. If A1 is zero or above 40, O16 is recorded `not_run`; do not substitute another query or treat the skip as source failure.

## Conditional transitions and hard stops

- Proceed from O01 only if the source is HTTPS `www.proquest.com`, the exact PQDT product/route is proven, exactly one allowlisted PQDT database is selected, and the probe's owned page is closed. Any ATAI/other selection, combined PQDT labels, login/access state, challenge, unsafe route, or unverified cleanup stops P01 with `total=null` for that operation.
- Proceed from O02 to O06 only if the adapter proves the exact selected source, exact query echo, visible controls, and a reconciled positive total or explicit native zero. A syntax/error/loading/access/challenge/busy state is not zero and stops the attempt; there is no automatic reissue.
- Proceed to the nine partition operations only if the field diagnostics finish without a stop. A source-native field error is evidence that the field candidate is unvalidated, not permission to substitute `NOFT` or silently narrow a partition.
- Run O16 only if all nine partition diagnostics complete and O07's reconciled A1 total is 1–40. Both strict passes must exhaust the total and agree in ordered numeric IDs; otherwise fail closed with no mergeable prefix. A zero or total above 40 records O16 as not run.
- A challenge is passively observed only within the adapter's finite 30-second timeout; never solve, evade, refresh, rotate, or retry it. A busy condition receives no reissue under `RP-D08-P01-NONE`; record it as busy/failed and stop. Operator termination is `cancelled`, not provider failure.
- At termination, cancel and collect every child, close only adapter/probe-owned pages while still attached, verify the broker anchor and baseline target set are preserved, verify the shared lease release, and write the immutable terminal/cleanup evidence. If cleanup or release cannot be verified, keep supervision active and report unresolved cleanup; do not mark the attempt complete.

## Gate and handoff rules

The runtime manifest must list the shared direct-source gates: `G-SOURCE-BOUNDARY`, `G-QUERY-TRANSPORT`, `G-FIELD-BOUNDARY`, `G-CONTROLLED-VOCABULARY`, `G-DATE-CONTROL`, `G-LANGUAGE-CONTROL`, `G-CONTENT-CONTROL`, `G-RETRIEVAL`, `G-PAGINATION-CONTROL`, `G-PAGE-IDENTITY`, `G-COMPLETENESS`, and `G-FAILURE-BEHAVIOR`. Each operation cites only the gates it actually exercises. `G-COMPLETENESS` can pass for bounded A1 only if O16 runs and both strict passes validate; otherwise it remains `untested` or fails narrowly. This does not establish final completeness for the other eight partitions. Subject/index/thesaurus evidence that is absent remains `untested`, not zero and not a usable descriptor.

All nine source totals are recorded separately by partition and never combined with ATAI. An explicit zero is `0`; any failure, unavailable total, short/partial page, or unobserved behavior is `null`. No screening, candidate import, PRISMA final event, cross-source union, or D07 provenance is permitted. The controller checkpoints the campaign only after the immutable manifest and evidence are written. This plan ends after P01 and requests a bounded technical corrective attempt only for behavior-preserving issues; a semantic or completeness-rule change is referred to the review owner.
