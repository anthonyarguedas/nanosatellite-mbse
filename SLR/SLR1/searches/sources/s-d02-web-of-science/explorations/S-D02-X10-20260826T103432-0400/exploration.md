# Web of Science X10 human-demonstration exploration

- **Session ID:** `S-D02-X10-20260826T103432-0400`
- **Source:** Web of Science Core Collection
- **Started / ended:** 2026-08-26T10:34:53-04:00 / 2026-08-26T10:36:52-04:00
- **Controller / operator:** Pi controller / review owner operating the visible interface
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `bc86e1366c473094b7bb1f4262bda8a763267f92ef6032498cf834af01589e66`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event
- **Terminal status:** operator completed demonstration; owned-page cleanup and lease release verified

## Question and starting state

Earlier agent exploration could not reliably establish the English and publication-date controls. X10 recorded a human demonstration on one leased owned page after the operator disabled an unintended local proxy. The start route returned HTTP 200 and hydrated the normal Basic Search interface without challenge or busy state.

The operation used the seven-byte count-only sentinel `CubeSat` (SHA-256 `f4d8581ea796810254a292e207a7e3f680c3b60f6d41ca16d9ec7f5a68225023`). Input values were not retained by the recorder. No result card, record identity, record link, export, screening decision, or candidate import was captured.

## Demonstrated visible sequence

1. Leave the default Topic row in place and enter the sentinel.
2. Activate **Add date range**.
3. Activate **Publication Date**.
4. In the grouped timespan menu choose **Custom**; only then use the stable `data-ta=search-timespan-start-input` and `data-ta=search-timespan-end-input` controls.
5. Enter the diagnostic lower and upper dates, each observed only as a ten-character redacted value.
6. Activate **Add row**.
7. Open the new row's **Select search field, All Fields** combobox and choose **Language**.
8. Open the row value control and choose **English**.
9. Activate the visible Search button once.

The page transitioned in the same tab to the expected summary-route family, page 1, Relevance. The bounded aggregate surface reported total 4,697. The recorder observed no DOM `submit` event because this control uses a SPA click transition; the source-operation ledger therefore counts the demonstrated Search activation and resulting summary transition as one submit-equivalent source operation.

## Technical findings and implementation

- The current date menu requires the explicit **Custom** option before the date inputs are usable. The previous helper stopped after selecting Publication Date.
- The demonstrated working order is date setup first, then the Language row. X08's reverse order failed before reaching the date surface.
- Child spans inside **Add date range**, **Add row**, field combobox, and Search buttons made the first generated draft structurally brittle. Recorder hardening now promotes the nearest actionable composed-path control and recognizes stable `data-ta` attributes.
- The restricted original stream contains only bounded controls, but its final whole-page control projection included recommendation-control labels and an opaque summary-path segment. Canonical recorder commit `d7cc5f9` now excludes result/recommendation regions, suppresses raw titles, and redacts opaque path segments. The raw X10 stream remains restricted and is not an acceptance artifact.
- Review probe commit `f62c6a9` adds the demonstrated Custom selection, waits for both stable date inputs, and changes setup order to date before language.
- Minimal changed-path check: `uv run SLR/SLR1/scripts/test_wos_core_pilot_probe.py` — 17 tests passed.

## Recorder result

The recorder used exploration implementation `f696c76` and produced 126 bounded events, 33 raw UI actions collapsed to 22 draft actions, no challenge interval, no busy state, no retained input values, and verified owned-page cleanup. A post-session hardened draft was generated with semantic controls for **Add date range**, **Publication Date**, **Custom**, **Add row**, **Language**, **English**, and Search. Drafts remain diagnostic and are not executable evidence plans.

## Remaining unknowns and next step

X10 demonstrated the human interaction route, but it did not independently project the final friendly-display text needed to prove that Topic, Publication Date, and English were all submitted. It also did not reopen the editions picker or validate result-card hydration, page size, stable identity, export, or completeness.

Run one new automated exploration replay of commit `f62c6a9` with the same sentinel and one source operation. Require exact control readback, final friendly-display Topic/Publication Date/English and no Document Type, aggregate total reconciliation, and verified cleanup. Only a successful replay can freeze an evidence-mode plan; X10 itself passes no gate.
