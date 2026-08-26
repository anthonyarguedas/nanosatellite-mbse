# OATD X14 human-demonstration and recurring challenge

- **Session ID:** `S-D09-X14-20260826T102356-0400`
- **Source:** Open Access Theses and Dissertations (OATD)
- **Started / ended:** 2026-08-26T10:24:30-04:00 / 2026-08-26T10:28:12-04:00
- **Controller / operator:** Pi controller / review owner operating the visible interface
- **Lease receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `e9cb14e9727e674116aa22878ab214d002052c5bfc597e6da7d68851b6a8e9bc`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event

The recorder opened the normal OATD home, became ready without a challenge, and captured a human demonstration through the visible advanced-search controls and one native submit. It retained no input values, result records, identifiers, links, or screening decisions.

At 92.007 seconds after recorder start, a click-required access challenge became continuously observable. The same page was passively polled once per second. It did not clear during 130.528 seconds and 128 observations before the operator requested stop. The raw stream contains 16 operator actions while the challenge was present; these are diagnostic only and must never be replayed. Canonical recorder commit `9221297` and later automatically exclude every challenge-time action from generated automation. A derived pre-challenge draft contains 23 actions and no challenge selector.

The operator later reported that, outside this recorded phase, a challenge cleared automatically but was followed by a **Please slow down** condition. That report is not browser evidence from X14, but it supports treating OATD as currently transient/unstable rather than inaccessible or zero. Do not open a new OATD page to escape the condition or run an immediate retry; respect source pacing.

The owned page closed, the inert anchor was preserved, and the lease released with `cleanup=verified-clean`. Total remains `null`. The pre-challenge interaction stream may guide selectors, but no OATD evidence plan is frozen while the recurring access/busy behavior remains unresolved.
