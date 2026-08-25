# Human decision — Wiley Online Library

**Not an approval record.** P01 remains blocked, `accepted_pilot_ids` remains empty, and no final search is authorized.

## H-WILEY-01 — Corrective P02 authorization

- **Decision:** **Authorized** by the review owner at 2026-08-24T13:34:55-04:00.
- **Scope:** One corrective Wiley P02 using code-only candidate commit `c8be56c87fe17f413de7c083b49f3bfebfca5bc7` and the exact scope in [`controller-review.md`](controller-review.md#decision-required).
- **Evidence:** P01 independently reproduced the old adapter's output overwrite defect; the separate candidate fix passed 145 tests plus 60 subtests and controller review without browser/network/source use.
- **Boundary:** P01 remains blocked and immutable. This authorizes P02 only; it does not approve a final search, screening, candidate import, automatic retry, protocol change, central integration, or P01 itself.

Decisions about Anywhere/AllField semantics, pair handling, controlled/indexed terms, and the final translation remain deferred until P02 supplies current source evidence.
