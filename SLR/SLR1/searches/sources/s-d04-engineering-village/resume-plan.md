# Resume plan — S-D04-C01-20260824T161325-0400

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). Use an agent-driven `X` exploration session to understand/fix an unknown or failing real interface; allocate an immutable `P` evidence attempt only after the route and implementation work live. Any broader offline-suite prerequisite below is superseded.


**Status:** `technically_blocked`. No new human authorization is required for this technical attempt.

## Carries forward

- `G-TRANSLATION-INTEGRITY` from P01 [`translation-literal-audit.json`](pilots/S-D04-P01-20260824T123301-0400/translation-literal-audit.json), SHA-256 `df218ce4ab6ff5c07270bbac5e40f7b215bd5d0791bb68a46b06e07590b76d06`; the route/projection repair cannot alter the offline draft audit.
- `G-OWNED-PAGE` remains proven by P02 [`g01-safe-receipt.json`](pilots/S-D04-P02-20260824T130842-0400/g01-safe-receipt.json), SHA-256 `c59aaf64fcda1206c57310ab4aae8ac66a8205056294cb7a6b707d06a9f87099`. It proves mechanics only and **does not claim source access**.

## Next immutable attempt

- Allocate `S-D04-P03-<timestamp>` as `controller_technical`; no new human authorization is required.
- **Source-operation maximum: 2.** Follow [`p03-execution-plan.md`](p03-execution-plan.md): operation 1 is one corrected stabilized route/access projection; only if healthy, operation 2 is one paired event. The paired runner makes exactly two explicitly counted sequential component requests (Compendex then Inspec) inside that one campaign operation, with separate totals/provenance and no inferred combined total.
- Do **not** rerun owned-page mechanics, query families A1–BT2, thesaurus, export, provenance/completeness, or S-C01. A failed projection ends source work.

## Shared browser and acceptance

Use the exclusive global shared CfT lease at `127.0.0.1:9222`, with a new per-attempt receipt, protected-anchor preservation, and owned-page cleanup. The attached `engineering_village_paired_diagnostic.py` is bounded to count/control evidence and retains no records; no full retrieval or acceptance is implied by P02 or by a diagnostic result.
