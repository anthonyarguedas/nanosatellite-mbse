# Resume plan — S-D05-C01-20260824T161325-0400

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


**Status:** `technically_blocked`. No new human authorization is required for this technical attempt.

## Carries forward

- Preserve `G-OUTPUT-SAFETY` from P02 [`adapter-verification.json`](pilots/S-D05-P02-20260824T134448-0400/adapter-verification.json), SHA-256 `62ee00b0266be3b99292b9ea83a52f10c37d37af85add5333c3f0dfc0874e307`.
- Preserve `G-QUERY-CONSTRUCTION` from P02 [`query-regeneration-audit.json`](pilots/S-D05-P02-20260824T134448-0400/query-regeneration-audit.json), SHA-256 `79487ace35ec664a436e904641c35ea38455229e5b0c326a00bf5f712eafbd5f`.
- There is **no prior Wiley source behavior**: P01 and P02 made zero Wiley requests.

## Next immutable attempt

- Allocate `S-D05-P03-<timestamp>` as `controller_technical`; no new human authorization is required.
- **Source-operation maximum: 4.** Follow the exact conditional operations and stop rules in [`p03-execution-plan.md`](p03-execution-plan.md): run the first record-free live health gate, then only its predeclared interface/parser/control/completeness diagnostics when every prior gate passes.
- Do **not** rerun the old clobber test as a source operation, use a dedicated stale endpoint, treat source-free evidence as source behavior, submit final cells prematurely, screen, import, or create a final event.

## Shared browser and acceptance

Every browser phase requires the exclusive global shared CfT lease at `127.0.0.1:9222`, its immutable receipt, protected-anchor preservation, and owned-page cleanup. Acceptance still requires observed live route/field/parser/pair/control/identity/export/completeness evidence; no methodological decision is proposed here.
