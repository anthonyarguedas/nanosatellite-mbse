# S-D03 P06 observations

**Status:** failed closed at the first conditional operation; diagnostic only; not accepted. P05's source-bearing attempt remains immutable and consumed. P06 is the one controller-technical successor and no further attempt was allocated.

## Scope and safeguards

- Attempt: `S-D03-P06-20260825T135127-0400`; maximum four conditional source operations; one attached canonical lease.
- Only exact `queries/A1.ieee-query.txt` was submitted. Its SHA-256 is `bf8caf009e189c1869619b399fc43629a7f4ad96bbd111587214351e8d2cce01`.
- `diagnostic_only=true`, `screening_performed=false`, and `candidate_import_permitted=false` applied throughout. No records were screened, imported, exported, used for S-C01, or sent to a final event.
- No partition, NEAR/6, S-C01, export, or unrelated record operation was run. P01–P05 and `D-METHOD-NEAR6` were not modified.

## Browser phase and cleanup

- The preflight status was healthy for the dedicated CfT at the canonical endpoint, with one inert broker anchor, the expected epoch/version, a free lease, and no guardian/orphan condition.
- The complete phase ran attached under the required `caffeinate -dims` canonical lease wrapper with `--lease-timeout 600`; each source adapter/probe timeout was 60 seconds. The wrapper receipt records the unchanged browser epoch, expected profile/endpoint, child exit 1, verified-clean owned-target cleanup, and released lease.
- The postflight status confirms one preserved anchor, healthy CfT, verified owned-page closure and lease release. AC power remained at 100%; the phase-window log contained zero Sleep, Wake, and DarkWake events. See `browser-status-receipt.json`, `browser-cleanup-receipt.json`, and `browser-lease-release-receipt.json`.
- No challenge, login, busy/rate-limit, access, or source-service condition was observed.

## Conditional operation ledger

1. **`G-YEAR-CONTROL` / `P06-op-01-year-a1` — failed closed.** The exact A1 echo and both visible year readbacks were observed, and Apply was clicked once. The patched wait passively polled the same owned page; it did not reload, resubmit, click Apply again, or use blind stabilization sleep. The safe projection recorded exact query echo, a year-range mismatch, the singleton summary, five cards, no active page-size/page controls, and Relevance. It observed zero `Loading results`/transitional polls and three repeated contradictory polls, then returned `IEEEProtocolError` at `year_post_click_stabilization`. The total is `null`, not zero; pages and records retrieved are zero and no partial prefix was retained.
2. **`G-CONTENT-CONTROL` — not run.** The year dependency was not healthy.
3. **`G-LANGUAGE-CONTROL` — not run.** The probe did not run; no language selection or English limit was attempted.
4. **`G-COMPLETENESS` — not run.** No operation-2 total existed and no bounded capture was issued.

The attempt therefore performed one source operation of four authorized maximum, with source total `null` and records retrieved/imported `0/0`.

## Immediate source-free technical investigation

The live failure was preserved in the restricted adapter artifact and the safe aggregate receipt. The assigned scripts were then inspected and exercised without source access or a new lease:

- Agent-tools main was `d872f59f5f20913fbd0ef4de16ea2ab79a6bc883`, containing the trusted IEEE fix commit `f76610f12bb6f832244ea49d93d0c4d8add8116e`. The current adapter, focused test, and new IEEE domain note matched their exact `f76610f` hashes: `8523083554e27b7d6117f9ce1840867883db2e6b9b812d7d83dce6f4cf8bcca0`, `0573a7183894b2550511bca7dd0a900f74feb6f04bf260ae6aa2a9cf5bbaf111`, and `ce02c2e0e7bb275211e184d791e763519211a98095a62df206388e263ccaf3eb`.
- The focused IEEE adapter suite passed **26 tests and 10 subtests** after the live failure. The language-probe suite passed **8 tests**.
- The source-free regression specifically covering twenty `Loading results` polls followed by a stable five-card result passed. The regression specifically covering a stable repeated contradiction also passed and confirms the prescribed bounded terminal behavior after three repeated contradictions. Thus the patch's offline wait contract is intact; this live receipt did not observe the Loading projection that the patch tolerates.
- The remaining technical issue is **`code_issue=unresolved`**: the safe live evidence establishes a repeated rendered range mismatch before a reconciled result, but source-free evidence cannot distinguish an IEEE state/selector behavior from an adapter invariant failure. No unsupported code edit was made to the shared dirty agent-tools checkout, and the failed source operation was not reissued.

## Disposition and next action

P06 remains a failed technical diagnostic and the campaign remains technically blocked. No methodological decision is pending and no human authorization is needed for the recorded technical diagnosis. The next action is source-free isolation/repair of the year-control rendered-range invariant before any separately authorized future live work; do not allocate another attempt from this P06 packet or import any prefix.
