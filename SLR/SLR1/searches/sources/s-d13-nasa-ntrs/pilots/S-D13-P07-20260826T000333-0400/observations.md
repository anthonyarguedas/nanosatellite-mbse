# S-D13 P07 deterministic evidence observations

**Status:** failed closed at the rendered count reconciliation gate; diagnostic only; not accepted.

- Attempt `S-D13-P07-20260826T000333-0400` executed the two-operation plan frozen by `S-D13-X02-20260825T225903-0400` against worktree commit `4abae7c2c8f06630a3a13bac66c21b251d5360ca` and adapter SHA-256 `a870b87473e2fd46e0b7081726e7c5a811342c4595b8713b5225d284e3460d0c`. No implementation was patched during evidence mode.
- Operation 1 passed: one record-free public-root navigation returned a 2xx normal source route, source identity, one visible search surface, two stable healthy samples, and verified owned-page cleanup.
- Operation 2 submitted exact 13-byte `nanosatellite` once in count-only mode. The adapter reported exact input readback, Relevance, page size 25, and a total of 646,789—the unchanged unfiltered pre-submit aggregate observed in X02—rather than a changed query result. It therefore published a stale state as success. Under the frozen invariant, the accepted total is `null`, not 646,789 or zero. Zero records were retained or imported.
- This is a controller-technical adapter state-reconciliation failure, not a provider failure and not a methodological uncertainty. P07 is preserved once and NTRS returns to exploration; no evidence retry is authorized from this packet.
- The canonical lease was released with `cleanup=verified-clean`; its one inert broker anchor was preserved and no orphan remained. The phase ran under `caffeinate -dims` on AC power. Exact-window checks found no Sleep/Wake/DarkWake event and no System Information/About This Mac process or launchservices CHECKIN.
- No API, date, fallback, partition, detail, export, screening, candidate import, partial prefix, or final event occurred.
