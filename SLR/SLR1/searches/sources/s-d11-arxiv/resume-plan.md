# Resume plan — S-D11-C01 / initial P01

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


**Status:** `not_started`. This brand-new arXiv source has no campaign, manifest, pilot directory, attempt, receipt, source total, or live observation. Do not fabricate one and do not treat this plan as an attempt.

## Next runtime allocation

1. Allocate a fresh `S-D11-P01-<UTC timestamp+0000>` initial attempt and `S-D11-C01-<UTC timestamp+0000>` campaign at runtime from the shared campaign/manifest templates, as specified in [`p01-execution-plan.md`](p01-execution-plan.md).
2. Use one complete shared CfT lease at `127.0.0.1:9222`, one new per-attempt lease receipt, the single proven shared context, and the trusted local runner. The normal route creates its own page and does not require an existing arXiv target. Do not launch a browser or create a fresh profile, port, or lease per cell.
3. Run at most 11 sequential source operations: nine count-only cells, one conditional two-record metadata/abstract diagnostic, and one conditional second-page diagnostic. Do not retry a failed operation.
4. Use the actual UTC execution year only as the labelled submitted-date pilot diagnostic bound. P-001 remains unresolved; no arXiv posting date is a formal publication date.

## Stop and checkpoint rules

- Stop on any lease/anchor/health/target/cleanup failure, challenge/login/CAPTCHA, busy/service state, timeout, query/control rewrite, malformed total/range, missing or duplicate ID/version route, abstract/pagination mismatch, nonzero adapter exit, or output collision.
- A successful native no-results page is `0`; count-only positive totals retain zero rows by design; every failure is `null` and discards its prefix. No screening, import, merge, or final event is allowed.
- If P01 is blocked or cancelled, preserve its immutable receipts and runner output, update the runtime campaign narrowly, and leave all unexercised gates untested. A later technical correction must receive a new attempt ID and must preserve query semantics; do not reissue the failed source operation in the same attempt.
- If P01 completes, create/hash the immutable manifest and evidence index after verified cleanup/release, checkpoint the campaign, run the shared validator, and review acceptance. No result enters `final-events/`.

No prior arXiv gate or evidence is available to carry forward.
