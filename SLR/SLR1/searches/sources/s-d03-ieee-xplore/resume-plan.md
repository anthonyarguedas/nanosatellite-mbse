# Resume plan — S-D03-C01-20260824T161325-0400

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


**Status:** `technically_blocked`; the review owner authorized `D-METHOD-NEAR6` on 2026-08-25. P05 is immutable and consumed, and its one controller-technical successor P06 is now preserved as a failed technical attempt.

## Carries forward

- `G-FIELD-PARSER` from P02 [`execution-ledger.json`](pilots/S-D03-P02-20260824T105020-0400/execution-ledger.json), SHA-256 `eb4ba30d01078da885fb3f206ea38154cfd02f42965ab090d2eb5379bae5422c`. The year-control diagnosis cannot affect its individually fielded All Metadata/parser evidence.
- P04 preserves `G-ADAPTER-COUNT`, `G-TRANSLATION-ALGEBRA`, `G-NEAR-SYNTAX`, and all nine diagnostic partition counts; P05 must not rerun those counts or prior field/parser evidence unless the new adapter behavior demonstrates they are affected.
- `G-NEAR-METHOD` is passed: [`human-review.md`](human-review.md) accepts `NEAR/6` as the conservative broader same-field fallback without claiming exact equivalence.

## P06 outcome and next mode

- P06 (`S-D03-P06-20260825T135127-0400`) used exact A1 and failed the visible year-control evidence gate with `total=null`: the projection saw five cards beside a stale/singleton summary. Content, language, and completeness were not run.
- Do not allocate another evidence attempt yet. Open `S-D03-X01-<timestamp>` in **exploration mode** with a strong interactive browser agent. Keep one owned page, retain a restricted screenshot and bounded visible-summary/control projection, observe the full loading/hydration transition, repair the summary/year state machine, and prove the interaction live with a small sentinel query.
- Freeze a new adapter commit and year-control recipe only after the real page reconciles. Then propose one deterministic evidence attempt for year, content, language, and completeness. Do not rerun partitions, NEAR/6, S-C01, or export during exploration.

## Shared browser and acceptance

Every browser phase must hold the global shared CfT lease at `127.0.0.1:9222`, record its receipt, preserve the broker anchor, and close only its owned page. Acceptance still depends on a valid year control, its declared dependent controls/completeness evidence, the resolved NEAR/6 decision, and all diagnostic/no-import invariants.
