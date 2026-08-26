# Web of Science X04 hydrated-control exploration

- **Session:** `S-D02-X04-20260826T012713-0400`
- **Mode:** X diagnostic only; no campaign/evidence/final search
- **Implementation:** review commit `37212ec` atop hydration runner commit `cd1dd58`; runner SHA-256 `9ee121dc4f1f589e3284ed18842b99e20126b896a5a5ccde543c179271597d84`

One owned page navigated once to the normal Core Collection Basic Search route. The new passive hydration gate returned after two polls, but the subsequent visible-control preparation stopped with `edition_picker_not_observed`. No query was submitted or reissued; source-operation submit count is zero and the accepted total is `null`, not zero. This isolates the next technical question to the current all-editions control surface after hydration; no source access/challenge/busy result is inferred.

The runner retained only aggregate booleans/counters. No record, identifier, title, DOM, screenshot, screening, import, gate claim, or final event occurred. The owned page/target disappeared, baseline pages and target set were preserved, and the canonical lease released with `cleanup=verified-clean`; exact-window Sleep/Wake/DarkWake and System Information/About This Mac checks were zero.

**No freeze.** A later strong interactive X must screenshot and semantically inspect the hydrated database/edition control on the same owned page, then patch/retest before any one-submit evidence route is frozen.
