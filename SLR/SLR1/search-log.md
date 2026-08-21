# New-run search log

- **Review:** SLR1 restart
- **Created:** 2026-08-20
- **Time-zone convention:** Record RFC 3339 timestamps with the observed offset; also record UTC when an adapter supplies it.
- **Normative strategy:** [`protocol-discovery-and-appraisal.md`](protocol-discovery-and-appraisal.md#search-strategy)
- **Artifact layout:** [`searches/README.md`](searches/README.md)

This is the chronological PRISMA-S index for the new run. Detailed source behavior, exact executed strings, controls, counts, checks, and evidence live in version-controlled source packets and are incorporated here by link. Pilot records are diagnostic only: they are not candidates, final discovery events, or screening inputs.

## Infrastructure events

| Date and time | Event | Disposition | Artifacts |
|---|---|---|---|
| 2026-08-20 | New-run search infrastructure created from the current protocol under `S-001`; no earlier-run search artifacts restored. | Deterministic validation passed; committed before the first pilot. | [`searches/`](searches/) |
| 2026-08-21 | Preliminary PRESS revision expanded P/E/M/R text words, defined phrase/acronym/pair behavior, removed the redundant V1/O1 discovery partitions, and added controlled-vocabulary pilot requirements. | No final search was affected; the strategy now has nine direct partitions and source translations remain pending regeneration. Infrastructure validation passed. | [`protocol-discovery-and-appraisal.md`](protocol-discovery-and-appraisal.md#search-strategy); [`searches/search-concept-dictionary.json`](searches/search-concept-dictionary.json); [`TASKS.md`](TASKS.md) |
| 2026-08-21 | Follow-up PRESS revision added missing population, EPS, structured-model, relationship, and reusable-artifact inflections and defined the `S-C01` candidate-MBSE-terminology test. | No pilot or final search was affected. Candidate terminology remains non-normative until `S-C01` supports and a committed protocol amendment accepts it; source translations are still pending. | [`protocol-discovery-and-appraisal.md`](protocol-discovery-and-appraisal.md#candidate-mbse-terminology-test); [`searches/search-concept-dictionary.json`](searches/search-concept-dictionary.json); [`TASKS.md`](TASKS.md) |

## Pilot events

| Pilot ID | Task | Source or method | Started | Status | Source packet and manifest | Acceptance note |
|---|---|---|---|---|---|---|

## Final search events

No final event has been run. Populate this section only under `R-002`, after its dependencies are complete.

## Failures

No pilot or final-source failure has yet been integrated. A failed final event must have `total: null`, import no partial prefix, and be recorded under the failure-register schema.
