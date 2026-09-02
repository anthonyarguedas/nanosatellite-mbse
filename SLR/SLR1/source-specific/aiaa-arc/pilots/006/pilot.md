# Pilot 006: factor-wise metadata field union

Pilot 006 is diagnostic. It is not a final search. It uses 2011-01-01 through 2026-08-29 and retains only non-mergeable artifacts.

## Objective

Test whether Title, Keywords, and Abstract can replace Anywhere while preserving cross-field combinations between protocol factors.

For every literal or ordered phrase:

```text
META(s) = Title(L(s)) OR Keywords(L(s)) OR Abstract(L(s))
```

Each protocol expression was rebuilt from `META` atoms. ARC combines visible Advanced Search rows with `AND`, so the outer field `OR` was implemented as a union over every field assignment. Factors assigned to the same field were grouped with explicit `AND` in one row.

This is a factor-wise union. It allows `P` in Title and another factor in Abstract. It does not require the complete query to match one field.

The [expanded Stream B plan](searches/event-plan.json) declared 108 cells. The triggered [Stream A and core Stream B extension](searches/core-event-plan.json) declared 117 cells. All 225 cells were planned before their source calls.

## Complete execution

Every cell returned at most 26 records. Every successful JSON retains all reported result cards and exact source-observed field rows. The [assessment](searches/assessment.json) reconciles each source event and canonical DOI.

| ID | Cells | Positive cells | Cell-event sum | DOI union | Anywhere total |
|---|---:|---:|---:|---:|---:|
| A1 | 27 | 4 | 4 | 1 | 492 |
| A2 | 27 | 9 | 9 | 1 | 1,541 |
| A3 | 27 | 2 | 2 | 1 | 472 |
| B1 | 9 | 9 | 87 | 37 | 1,388 |
| B2 | 27 | 22 | 67 | 17 | 1,028 |
| BG1 | 36 | 0 | 0 | 0 | 45 |
| BG2 | 36 | 2 | 4 | 2 | 3,584 |
| BC1 | 9 | 1 | 3 | 3 | 152 |
| BT2 | 27 | 6 | 12 | 1 | 437 |

The deduplicated schedule union contains 47 canonical DOIs. The cell-event sums include overlap and ARC virtual-collection manifestations.

## Recall findings

The known eligible DOI `10.2514/6.2015-4474` is source-located in A2, B1, B2, and BC1 under the current protocol.

| Applicable partition | Retrieved by metadata union |
|---|---|
| A2 | No |
| B1 | Yes |
| B2 | No |
| BC1 | Yes |

The metadata route therefore failed its observed known-item gate. The sentinel's functional EPS and relationship evidence occurs outside the metadata combination required by A2 and B2.

Pilot 005 captured the complete 45-event BG1 Anywhere result as 44 canonical DOIs. Pilot 006 returned zero BG1 metadata records. This supplies a complete observed set comparison. All 44 canonical Anywhere records were absent from the metadata union. Their eligibility remains unclassified, so they cannot be discarded as noise.

## Decision

- The factor-wise construction is technically valid and fully executable.
- The route reduces the nine-partition candidate set to 47 canonical DOIs.
- Reject it as a replacement for the direct Anywhere translation. It missed the known eligible sentinel in A2 and B2.
- Retain it as a nonexcluding screening-priority lane.
- Keep the direct one-row Anywhere route from Pilot 005 as the canonical source search.
- Apply no language, publication type, Topic, wildcard, access, peer-review, or full-text-availability filter.

## Mandatory screenshots and adapter repair

AIAA adapter v5 now derives these sibling files from every requested JSON path:

```text
<stem>.search-page.png
<stem>.results-page.png
```

The first PNG captures the fully configured Advanced Search page before submission. The second captures the hydrated first result page after native controls. Both are full-page images. Visible email elements are masked. JSON metadata retains each filename, SHA-256 digest, dimensions, and privacy evidence. The CLI exposes no screenshot opt-out.

Pilot 006 verified both screenshots for all 225 successful JSON artifacts, for 450 required screenshots. Failed attempts retained another 23 partial or complete screenshots, giving 473 PNGs in the pilot directory.

The initial formatted-citation preview encountered records without a usable bulk citation form. Adapter v5 added a card-only preview mode for stable rendered-card capture without formatted citations, RIS, or abstracts. The mode remains non-mergeable. Thirteen source failures are retained, and exact retries recovered every cell. No failure became zero.

## Limits

- Metadata-only searching cannot retrieve a required factor found only in ARC full text or hidden indexing.
- Anywhere totals count source events, while metadata unions use canonical DOI identity. Their ratios describe workload rather than formal recall.
- The pilot uses inclusive native months before exact-day exclusions.
- Rendered cards and screenshots cannot enter the final corpus.
- A final search still requires complete source-month partitioning, exact-day treatment, native export, and final-search artifacts.

## Reproduction

Review scripts are under [`SLR/SLR1/scripts/aiaa_arc_pilot006`](../../../../scripts/aiaa_arc_pilot006). The offline assessment and validation commands are:

```bash
PYTHONPATH=SLR/SLR1/scripts/aiaa_arc_pilot006 \
python3 SLR/SLR1/scripts/aiaa_arc_pilot006/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/aiaa-arc/pilots/006 \
  --pilot005-root SLR/SLR1/source-specific/aiaa-arc/pilots/005 \
  --output SLR/SLR1/source-specific/aiaa-arc/pilots/006/searches/assessment.json

PYTHONPATH=SLR/SLR1/scripts/aiaa_arc_pilot006 \
python3 SLR/SLR1/scripts/aiaa_arc_pilot006/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/aiaa-arc/pilots/006 \
  --pilot005-root SLR/SLR1/source-specific/aiaa-arc/pilots/005 \
  --guideline SLR/SLR1/source-specific/aiaa-arc/source-specific-guidelines.md \
  --pilot-document SLR/SLR1/source-specific/aiaa-arc/pilots/006/pilot.md \
  --output SLR/SLR1/source-specific/aiaa-arc/pilots/006/searches/validation-report.json
```

Live source calls must run through the shared browser launcher. The event plans, immutable retries, source receipts, screenshots, and run receipts are under `searches/`.
