# NTRS X03 live diagnostic

- Status: outer guardian deadline after child deliverables; lease released with `cleanup=verified-clean`; X diagnostic only.
- Query: SHA-256 `3fc7d31e9abb58d42acd5c95a9549835545de822d0843e28265c6979b1a466d4`; exact echo: `None`.
- Submit count: `0`; root navigation count: `1`.
- Pre/post aggregate: `None` -> `None`; comparator: `null`; changed-state: `False`; post total category: `null`.
- Controls: visible/canonical ordering `None` / `None`; page size `None`.
- One-page count-only, no dates; card count `None`; Next `{'post_submit': None, 'pre_submit': None}`.
- Poll category: `pre_submit_control_projection_failure`.
- Implementation: commit `f444346a586abc23142bd5dda69718791948b853`, SHA-256 `91431f75fa8eebc35dec502c8a5fdee95b3babfa2e85aff14e00eaddf690dd0d`.
- Repair recorded: the X-only runner incorrectly called `parse_visible_controls(..., require_complete=True)` for a count-only/no-date operation; use `require_complete=False` before the next live retest. The f444 changed-aggregate guard was not reached.
- No records, screening, import, gate, or final search was performed.
- Cleanup: owned page closed `True`; baseline preservation count match `True`.
- P08 freeze: `False` (`None`); no dates, partitions, details, export, or completeness.
- This diagnostic does not claim acceptance.

- Outer lease receipt SHA-256 `2ba4241bc0e4d3ec4af8040ccb721f02fbdc694fd826439791f062a979a98f32`; one inert anchor preserved; no orphan. The phase used `caffeinate -dims`; exact-window checks found no Sleep/Wake/DarkWake or System Information/About This Mac launch. Child exit 124 occurred after cleanup/files and is operator/guardian timing, not provider failure.
