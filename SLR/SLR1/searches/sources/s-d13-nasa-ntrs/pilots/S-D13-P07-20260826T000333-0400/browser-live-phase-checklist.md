# Shared CfT browser live-phase checklist — S-D13-P07-20260826T000333-0400

## Offline and authorization

- [x] Mode: evidence; campaign `S-D13-C01-20260824T161325-0400`; controller-technical.
- [x] X02 frozen route, exact query bytes, pinned adapter hash, command startup, create-only outputs, receipt shape, and browser health verified; no broad suite run.
- [x] OWNER `S-D13-P07-20260826T000333-0400`; SOURCE `ntrs`; authoritative immutable receipt `.searches-d13-ntrs/S-D13-P07-20260826T000333-0400/browser-lease-receipt.json`.
- [x] Finite policy: two operations, one conditional submit, 90-second adapter deadline, no retry/fallback/API/date/partition.

## Shared browser boundary

- [x] Complete phase ran attached through the canonical lease wrapper under `caffeinate -dims`; endpoint `127.0.0.1:9222`, canonical profile, one CfT process, one protected inert anchor.
- [x] Probe and adapter created/closed only owned pages; no generic tab command or baseline mutation.
- [x] Frozen helper path used no raw OS-level key injection or explicit `nativeVirtualKeyCode`.
- [x] Runtime/on-disk CfT versions remained `152.0.7977.54`; browser epoch remained `uaShS7G1rXVB9KQFA1A6iw6LznsLaesk`.

## Outcome and cleanup

- [x] Source health passed; exact sentinel was submitted once.
- [x] Frozen changed-aggregate invariant failed: the adapter accepted stale unfiltered total 646,789. Evidence total is `null`; zero records retained/imported.
- [x] Condition: technical adapter publication failure; no challenge, busy, access, or provider failure observed.
- [x] Lease state `released`, cleanup `verified-clean`, anchor preserved, no orphan.
- [x] AC power and process-scoped sleep protection recorded; zero exact-window Sleep/Wake/DarkWake events.
- [x] No pre/post System Information or About This Mac process and zero exact-window launchservices CHECKIN events.
- [x] No screening, import, partial prefix, acceptance, or final event. Return to exploration; do not debug selectors or patch inside P07.
