# Scopus candidate-terminology preflight observations

- **Pilot:** `S-D01-P11-20260823T144717-0400`
- **Status:** failed before source work; no query, register freeze, screening, or import.
- **Observed:** adapter/test hashes, 27 focused tests, browser version, one `about:blank` controller anchor, AC power, and process-scoped sleep protection all passed.
- **Controller incident:** the local gate incorrectly required the whole `agent-tools` repository HEAD to equal approved adapter commit `9aef2155…`. HEAD had advanced to an unrelated notification commit while that approved commit remained an ancestor and the Scopus files were unchanged and clean.
- **Disposition:** preserve this preflight-only failure. P12 corrected only that gate under a new pilot ID. The generated `postflight.json` could not mark the anchor present because the runner raised before returning its ID; [`browser-targets-postflight.json`](browser-targets-postflight.json) is the controlling observation and shows the original anchor intact.
