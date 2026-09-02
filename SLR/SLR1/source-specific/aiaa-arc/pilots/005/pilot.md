# Pilot 005: direct post-proximity Boolean translation

Pilot 005 is diagnostic. It is not a final search. It uses 2011-01-01 through 2026-08-29 and retains only non-mergeable artifacts.

## Objective

Test whether commit `3194156e90497186664260a8e86435e78d2e2aa1` permits a direct, recall-safe AIAA ARC translation after removal of cross-source pair and proximity rules.

The proposed translation places each complete partition in one `Anywhere` (`AllField`) row. It uses quoted literals, fully parenthesized uppercase `AND` and `OR`, and the protocol's named compound blocks. It uses no proximity, pair expansion, wildcard, metadata field restriction, language filter, publication type filter, Topic filter, or access restriction.

The [predeclared event plan](searches/event-plan.json) contains the exact queries and hashes. The [assessment](searches/assessment.json) records all findings and decisions.

## Direct schedule

ARC accepted all nine direct one-row Anywhere expressions. Each artifact retains the exact source-observed row, inclusive source-month controls, and exact reported total.

| ID | Query characters | Source total |
|---|---:|---:|
| A1 | 2,772 | 492 |
| A2 | 3,437 | 1,541 |
| A3 | 2,154 | 472 |
| B1 | 1,870 | 1,388 |
| B2 | 2,116 | 1,028 |
| BG1 | 2,234 | 45 |
| BG2 | 1,746 | 3,584 |
| BC1 | 1,219 | 152 |
| BT2 | 1,822 | 437 |

Independent count repeats returned `45`, `3,584`, `152`, and `437` again for BG1, BG2, BC1, and BT2. The direct BT2 query replaced the historical 7,679-character pair-expanded remainder. It executed in one cell and reduced that historical length by 5,857 characters.

The historical broad-pair BG1 returned 8,088. The current direct BG1 returned 45, a 99.44% search-burden reduction. The concept definition changed, so this comparison does not claim set equality.

## Ordered phrase gate

BG2 remained large. Its fixed branch returned 3,571 of the complete 3,584 results. The single literal `reference architecture` returned 3,536.

The triggered [phrase plan](searches/phrase-event-plan.json) checked whether ARC was flattening quoted phrases into unordered conjunctions. In the known item's title:

- quoted contiguous `CubeSat Model` and `Reference Model` each returned `1`
- quoted noncontiguous `CubeSat Reference` returned `0`
- quoted reversed `Reference CubeSat` returned `0`
- explicit `CubeSat AND Reference` returned `1`

For the population search, quoted `reference architecture` returned `3,536`, explicit `reference AND architecture` returned `5,635`, and reversed quoted `architecture reference` returned `9`. These bounded controls support straight double quotes as ordered phrases. The large BG2 result comes from ARC's Anywhere coverage rather than phrase flattening.

## Known-item recall

DOI `10.2514/6.2015-4474` remains source-located in A2, B1, B2, and BC1 under the current protocol. Direct DOI-bounded checks retrieved it in all four partitions.

The current PDF has no `T_precise` literal. Its superseded `adapted`/`model` pair no longer creates BT2 membership. This changes the applicable known-item set from Pilot 004 without creating a recall failure.

## Precision investigation

The over-100 trigger applied to BG2, BC1, and BT2. The [branch plan](searches/threshold-event-plan.json) and [BG2 fixed-literal plan](searches/bg2-fixed-event-plan.json) found:

- BG1 is below 100. Its fixed branch accounts for 44 of 45 results.
- BG2 is driven by `G_structure_fixed`, mainly `reference architecture`.
- BC1's fixed branch returns 152. The DSL branch returns 1 overlapping event.
- BT2's seven morphology groups each return between 54 and 181 events. Their overlapping union is 437.

Rendered-title previews found all scheduled factors in 0 of 45 BG1 titles, 0 of the first 100 BG2 titles, 1 of the first 100 BC1 titles, and 0 of the first 100 BT2 titles. These are visibility warnings. ARC may match full text or hidden indexed content.

The new protocol resolves the semantic and recall issues that forced the earlier fielded proposal. Precision remains partly unresolved. BG2 in particular remains a large screening set. No proved no-loss metadata, language, type, Topic, or access filter is available.

## Decision

- Accept the prospective direct one-row Anywhere translation for all nine partitions.
- Retire proximity fallback syntax and local pair checks.
- Retire the Pilot 003 and 004 metadata field union as the canonical translation. It may serve only as a nonexcluding screening priority lane.
- Retire the four historical BT2 pair subcells. A future source length failure may use a newly planned Boolean cell split that preserves the current ordinary blocks.
- Keep no language, publication type, Topic, wildcard, access, peer-review, or full-text-availability filter.
- Keep this pilot separate from the final corpus. A final run still requires complete source-month partitioning, exact-day treatment, native export, and final-search artifacts.

## Retained failures

Thirteen null preview or count attempts remain as `NON_MERGEABLE_FAILURE` artifacts. Exact retries recovered every event. No failure was converted to zero. The failures mainly occurred during ARC preview or citation-form handling and did not affect the repeated schedule totals.

## Reproduction

Review-specific scripts are under [`SLR/SLR1/scripts/aiaa_arc_pilot005`](../../../../scripts/aiaa_arc_pilot005). The offline build and validation commands are:

```bash
PYTHONPATH=SLR/SLR1/scripts/aiaa_arc_pilot005 \
python3 SLR/SLR1/scripts/aiaa_arc_pilot005/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/aiaa-arc/pilots/005 \
  --output SLR/SLR1/source-specific/aiaa-arc/pilots/005/searches/assessment.json

PYTHONPATH=SLR/SLR1/scripts/aiaa_arc_pilot005 \
python3 SLR/SLR1/scripts/aiaa_arc_pilot005/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/aiaa-arc/pilots/005 \
  --guideline SLR/SLR1/source-specific/aiaa-arc/source-specific-guidelines.md \
  --pilot-document SLR/SLR1/source-specific/aiaa-arc/pilots/005/pilot.md \
  --output SLR/SLR1/source-specific/aiaa-arc/pilots/005/searches/validation-report.json
```

Live source events must run through the shared browser launcher. The source artifacts and run receipts under `searches/` retain all successful and failed attempts.
