# NTRS X04 changed-aggregate adapter retest

- **Session:** `S-D13-X04-20260826T014933-0400`
- **Mode:** X diagnostic only
- **Implementation:** worktree HEAD `20b948ca1df7c51a28bebbe9221b6570ead7ee7c`; NTRS fix `f444346a586abc23142bd5dda69718791948b853`; adapter SHA-256 `91431f75fa8eebc35dec502c8a5fdee95b3babfa2e85aff14e00eaddf690dd0d`

One owned-page count-only invocation used exact 13-byte `nanosatellite`, no date, limit 1/max-pages 1, Relevance, and page size 25. The repaired adapter recorded the settled unfiltered pre-submit aggregate internally, performed one visible submit, rejected stale transitional state, and returned the changed reconciled total **134** with exact executed query, one page, zero retained records, post-submit Relevance verification, and page size 25.

The canonical lease released with `cleanup=verified-clean`, one inert anchor, no orphan, and zero exact-window Sleep/Wake/DarkWake or System Information/About This Mac launches. No API, partition, date, detail, export, screening, import, gate claim, or final event occurred.

## Frozen proposed P08

Freeze the existing two-operation plan against this adapter hash: one record-free source-health navigation, then one conditional exact nanosatellite count-only submit. Require exact query readback, changed pre/post aggregate or native zero, Relevance, page size 25, zero retained records, and verified cleanup/release. Any stale aggregate, contradiction, challenge, publication, or cleanup failure is `total=null` and returns NTRS to exploration. No API/date/partition/detail/export/retry is authorized.
