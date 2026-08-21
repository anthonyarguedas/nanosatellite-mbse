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

## Pilot events

| Pilot ID | Task | Source or method | Started | Status | Source packet and manifest | Acceptance note |
|---|---|---|---|---|---|---|

## Final search events

No final event has been run. Populate this section only under `R-002`, after its dependencies are complete.

## Failures

No pilot or final-source failure has yet been integrated. A failed final event must have `total: null`, import no partial prefix, and be recorded under the failure-register schema.
