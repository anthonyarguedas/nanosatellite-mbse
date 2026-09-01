# ESA metadata-only contract supersession

The current ESA contract uses the browser adapter v8 category-0 metadata harvest. It requires two matching root snapshots, every event export, a full metadata ledger, and its terminal marker. It does not fetch attachment bodies during search.

Pilot 003 and Pilot 005 content requirements describe historical adapter behavior. The prior attachment-content requirement is superseded by the metadata-only contract. Historical pilot evidence remains unchanged. It cannot establish current source coverage, completion, or zero results.

The full ledger retains normalized Event, Contribution, Subcontribution, and Material metadata. It includes unmatched attachment metadata and declared access state. Merge, reports, source unions, and event validation accept only the marker-bound v8 ledger.
