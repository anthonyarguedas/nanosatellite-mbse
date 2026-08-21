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
| `S-D01-P01-20260820T234301-0400` | `S-D01` | Scopus | 2026-08-21T03:43:01Z | Blocked; `total=null`; skip for now | [packet](searches/sources/s-d01-scopus/) · [manifest](searches/sources/s-d01-scopus/pilots/S-D01-P01-20260820T234301-0400/manifest.json) | [Supervising review](searches/sources/s-d01-scopus/supervisor-review.md) withheld acceptance after the authorized owned-tab route failed before a recognizable result state. Task remains open. |
| `S-D13-P01-20260821T034216+0000` | `S-D13` | NASA Technical Reports Server | 2026-08-21T03:42:59Z | Diagnostic complete; worker manifest conservatively `partial` | [packet](searches/sources/s-d13-ntrs/) · [manifest](searches/sources/s-d13-ntrs/pilots/S-D13-P01-20260821T034216+0000/manifest.json) | [Supervising review](searches/sources/s-d13-ntrs/supervisor-review.md) accepted guideline v1.0.0 and all 11 translations; P-001 and final preflight remain mandatory. |
| `S-L02-P01-20260821T000344-0400` | `S-L02` | ESA Indico local harvest | 2026-08-20T23:42:30-04:00 | Blocked; revise local method | [packet](searches/sources/s-l02-esa-indico/) · [manifest](searches/sources/s-l02-esa-indico/pilots/S-L02-P01-20260821T000344-0400/manifest.json) | [Supervising review](searches/sources/s-l02-esa-indico/supervisor-review.md) confirmed local-source classification but withheld acceptance pending universe, child-route, material, event-note, and pair-rule resolution. |
| `S-D03-P01-20260821T003654-0400` | `S-D03` | IEEE Xplore | 2026-08-21T00:36:54-04:00 | Blocked; `total=null`; skip for now | [packet](searches/sources/s-d03-ieee-xplore/) · [manifest](searches/sources/s-d03-ieee-xplore/pilots/S-D03-P01-20260821T003654-0400/manifest.json) | A depth-2 worker stopped before source navigation when its browser harness had no active connection; [supervising review](searches/sources/s-d03-ieee-xplore/supervisor-review.md) retained only provisional query files and kept the task open. |
| `S-D09-P01-20260821T043952+0000` | `S-D09` | OATD | 2026-08-21T04:38:28Z | Blocked; `total=null`; skip for now | [packet](searches/sources/s-d09-oatd/) · [manifest](searches/sources/s-d09-oatd/pilots/S-D09-P01-20260821T043952+0000/manifest.json) | A depth-2 worker stopped after a Cloudflare challenge; [supervising review](searches/sources/s-d09-oatd/supervisor-review.md) withheld acceptance and kept the task open. |
| `S-D12-P01-20260821T043836+0000` | `S-D12` | IAF Digital Library | 2026-08-21T04:38:47Z | Diagnostic complete; worker manifest conservatively `partial` | [packet](searches/sources/s-d12-iaf-digital-library/) · [manifest](searches/sources/s-d12-iaf-digital-library/pilots/S-D12-P01-20260821T043836+0000/manifest.json) | [Depth-1 supervising review](searches/sources/s-d12-iaf-digital-library/supervisor-review.md) accepted guideline v1.0.0 and a 48-cell lossless translation under the normal 500-character input constraint. |
| `S-D11-P01-20260821T045351+0000` | `S-D11` | arXiv | 2026-08-21T04:53:51Z | Blocked after 8 of 15 cells; skip for now | [packet](searches/sources/s-d11-arxiv/) · [manifest](searches/sources/s-d11-arxiv/pilots/S-D11-P01-20260821T045351+0000/manifest.json) | A depth-2 worker stopped when a visible multi-row control became unavailable; [supervising review](searches/sources/s-d11-arxiv/supervisor-review.md) withheld acceptance and retained the unbounded-discovery/version-history date finding for follow-up. |

## Final search events

No final event has been run. Populate this section only under `R-002`, after its dependencies are complete.

## Failures

No pilot or final-source failure has yet been integrated. A failed final event must have `total: null`, import no partial prefix, and be recorded under the failure-register schema.
