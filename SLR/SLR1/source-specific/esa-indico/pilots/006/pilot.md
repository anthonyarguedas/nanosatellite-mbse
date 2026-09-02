# Pilot 006

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py`, adapter v8, through `uv run` and an invocation-owned headless browser.

## Objective

Repair the bounded metadata-harvest blockers exposed by the earlier pilots and complete one exact category-0 A1 pilot with two matching root snapshots, every event export, local matching, and marker-bound publication.

## Runs

- [`A1-r15.json`](searches/A1-r15.json): completed exact A1 result.
- [`A1-r15.csv`](searches/A1-r15.csv): normalized zero-row CSV.
- [Full metadata ledger](searches/.A1-r15.json.ESA_INDICO_METADATA_LEDGER.json): marker-bound Event, Contribution, Subcontribution, and Material metadata.
- [Terminal marker](searches/.A1-r15.json.ESA_INDICO_HARVEST_COMMIT.json): transaction binding for the JSON, CSV, and ledger.

## Result

- [x] Change source controls or controlled vocabulary

The repaired v8 route completed on 2026-09-02. Two ordered category-0 snapshots agreed on 440 public events. All 440 event exports produced 16,517 normalized metadata records: 440 Events, 8,922 Contributions, 17 Subcontributions, and 7,138 Materials. No attachment body was requested.

The exact A1 local expression matched 0 records. This is a proven zero for A1 within the completed metadata universe. It is not a zero-event or zero-record source total. The compact artifact is complete, merge eligible, and PRISMA run ready. The marker-bound ledger passed the strict merge loader and the PRISMA report input gate.

The fixes align the adapter with live Indico metadata. They cover Chrome for Testing discovery, identity-only root snapshots, restart checkpoints, bounded deadline extension, public contribution and subcontribution IDs, MD5 declarations, deprecated link aliases, encoded filename characters, long descriptions, matcher capacity, and full-ledger publication. The bounded harvest deadline now defaults to 1,200 seconds and accepts up to 1,800 seconds. Each request remains capped at 300 seconds.

This pilot validates the complete route and A1 only. The other eight planned partitions still require execution before the ESA final search is complete.
