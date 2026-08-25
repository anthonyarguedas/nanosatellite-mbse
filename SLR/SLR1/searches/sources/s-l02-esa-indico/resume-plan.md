# Resume plan — S-L02-P04 ESA Indico

**Status:** `controller_technical` launch bundle prepared; no P04 attempt has run. No campaign or attempt is fabricated in Git because this source has historical P01–P03 manifests but no checkpointed campaign.

## Preserved evidence

- Keep P01, P02, and P03 immutable. P03 remains diagnostic only and does not prove category-0 recursion/cap absence, a non-empty nested route, a real irregular/external route, terminal non-PDF coverage, or final two-pass completeness.
- Preserve the current `local-method-spec.json`, dictionary SHA-256 `61526b5d617a2af332aa3bb5d2a57b01dce60988c321d5c6deb807549fca076f`, nine local partition contracts, and the current harvester/tests. The new `--max-attachments` bound and nested-receipt check are behavior-preserving safety/validation fixes only.

## Next immutable attempt

- Allocate `S-L02-P04-<timestamp>` and `S-L02-C01-<timestamp>` at runtime from the shared campaign and manifest templates, before any ESA request.
- Use [`p04-execution-plan.md`](p04-execution-plan.md) exactly. The source-operation maximum is **2**: the fixed twelve-event shape scan, then at most two selected-event owner/material traversals and at most one nested plus one irregular receipt test inside that second operation.
- Use the HTTP-only current harvester with 45-second request timeouts, 0.5-second minimum pacing, two retryable-status retries, no redirect following, no browser/CDP, no PDFs/OCR, no matching, no screening, and no import.
- The twelve IDs are fixed to the next twelve after P03's first twelve: `453 448 373 379 387 340 262 416 438 430 334 425`. Do not widen the sample or start an all-time census.

## Conditional terminal branches

1. **Shape scan failure:** stop with null totals and no second operation. Preserve the exact failure; do not retry in the attempt.
2. **No nested and no irregular target:** stop after the successful bounded scan. State only that the inspected twelve exports contained no target; nested and irregular behavior remain unobserved. This is a reviewer handoff, not a source zero.
3. **One or both targets found:** run the selected-event traversal. Any missing owner/material/identity/access gate leaves coverage null and stops further source requests.
4. **Nested queue:** validate one receipt only if it contains a real observed material route and a content-safe coverage hash. Otherwise leave the nested gate incomplete.
5. **Irregular queue:** validate one receipt only for terminal extracted/manual text. Unsupported, inaccessible, or unresolved material remains queued/incomplete and is never silently treated as no-match.

After either branch, create the immutable attempt manifest/evidence index, update the newly initialized campaign once, run focused ESA tests plus the shared validator, and stop. P04 cannot accept ESA or authorize a final search; the remaining root-boundary, two-pass census, PDF/non-PDF, date cutoff, and supervisor-review blockers continue to apply.
