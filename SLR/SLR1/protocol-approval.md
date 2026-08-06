# Protocol Approval and Version Record

- **Review run:** `eps-mbse-slr-2026`
- **Frozen protocol version:** `1.0`
- **Approval/search authorization date:** 2026-08-06
- **Protocol file:** `SLR/SLR1/protocol.md`
- **SHA-256 at freeze:** `075df71df831f0e568e433ae87de7306a0abf39b3f8de7f7e48d1acfdf6368e2`
- **Branch:** `slr1-1.0-restart`

## Authorization

The researcher supplied the `1.0-draft`, identified its material design choices, directed that the review be restarted on a new branch, and explicitly authorized production of the query plan and commencement of new searches. That instruction is treated as approval to freeze version `1.0` before searching.

## Pre-search review of the identified choices

1. **PocketQube/picosatellite-only exclusion — retained.** It is consistent with the stated CubeSat/nanosatellite population. Mixed studies remain eligible only when CubeSat/nanosatellite evidence is separable. Search terms will not deliberately target excluded platforms.
2. **Open RQ2 outcome set — retained.** This avoids outcome-reporting bias. Reliability/mission assurance, reproducibility/reuse, and integrability/interoperability remain priority strata; other outcomes require the same explicit EPS-thread attribution and evidence coding.
3. **Tiering incomplete V&V records — retained.** A reported EPS target, explicit model-to-V&V bridge, and V&V method/intent/artifact establish the lowest linked tier. Missing criterion, execution, verdict, or timing is preserved as missing evidence and cannot be promoted to a higher tier.
4. **Broad Stream B — retained.** It is necessary because embedded EPS threads may be absent from metadata. Query partitioning, source-specific count pilots, conservative title/abstract retention, and separate unique-yield accounting will control workload without imposing an EPS keyword at this stage.
5. **New extraction for every included report — retained.** Legacy extraction and synthesis files were removed. Retained source Markdown/PDF files may be reused only after a report is independently rediscovered and newly screened.

## Anti-anchoring controls

- Legacy search results, screening, corpora, codebook, extractions, scoping review, and manuscript were removed before the new search.
- `SLR/SLR1/markdown/` and `SLR/SLR1/pdfs/` were retained as a source-file cache but are outside the search evidence base.
- Retained source files will not supply candidates, eligibility decisions, IDs, or extracted data.
- A legacy known-item/retained-file match audit is deferred until the independent primary-database candidate set has been merged. Matches then serve only as recall and retrieval checks.
- No old corpus or extraction data may be reconstructed from Git history during the new search or screening pass.

## Deviations

None at search start. Any later protocol change must be entered prospectively with date, rationale, affected artifacts, and protocol version.
