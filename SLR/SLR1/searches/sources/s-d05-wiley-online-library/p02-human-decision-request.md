# P02 deferred human decision — Wiley Online Library

**Not an approval record.** P02 is blocked and `accepted_pilot_ids` remains empty.

## Decision after controller validation

- **Question:** After controller-owned recovery of the stale dedicated browser endpoint and a new healthy controller preflight, should the review owner authorize one new immutable Wiley diagnostic pilot?
- **Recommendation:** Do not authorize a final search. If the controller validates the P02 packet and restores the dedicated environment, authorize only a replacement diagnostic scope that begins with the required count-only health gate and retains every live validation requirement blocked in P02.
- **Evidence:** [`p02-controller-handoff.md`](p02-controller-handoff.md), [`browser-preflight-failure.json`](pilots/S-D05-P02-20260824T134448-0400/browser-preflight-failure.json), and [`adapter-verification.json`](pilots/S-D05-P02-20260824T134448-0400/adapter-verification.json).

## Deferred methodological decisions

- **[untested]** Whether Anywhere/AllField is an acceptable one-field route; how pair semantics can meet the unordered <=5-token same-field requirement; and whether any controlled/indexed-term supplement exists.
- **[untested]** Current parser, phrase/punctuation/acronym/wildcard/expansion behavior; date/language/order/route/total controls; and export/identity/completeness behavior.
- **[protocol]** No source translation is accepted, no protocol semantic change is proposed, and `P-001` remains unresolved.
