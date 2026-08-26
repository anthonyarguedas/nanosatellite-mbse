# Web of Science X09 local-proxy setup failure

- **Session ID:** `S-D02-X09-20260826T103110-0400`
- **Source:** Web of Science Core Collection
- **Started / ended:** 2026-08-26T10:31:58-04:00 / 2026-08-26T10:31:58-04:00
- **Lease receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `ea3206fce5ed7a5380c967b73f1bb3b974571d58eb2b5fd5ed497f08f121bc98`
- **Diagnostic only:** yes; no submit, screening, import, gate claim, or final event

The recorder-owned page received HTTP 407 on the intended Basic Search route and stopped before readiness after 0.36 seconds. It recorded zero UI actions and zero source submits, so total is `null`, not zero. The operator then identified and disabled an unintended local proxy; X10 subsequently reached the same route with HTTP 200. X09 is therefore a local technical setup failure, not Web of Science access evidence.

The owned page closed, the inert baseline was preserved, and the canonical lease released with `cleanup=verified-clean`. No interaction recipe or evidence plan is frozen from X09.
