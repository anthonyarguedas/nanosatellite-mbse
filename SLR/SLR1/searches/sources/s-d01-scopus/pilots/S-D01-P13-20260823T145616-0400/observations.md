# Scopus candidate-terminology test observations — register and first execution window

- **Pilot:** `S-D01-P13-20260823T145616-0400`
- **Status:** partial, continued prospectively by `S-D01-P14-20260823T150131-0400`.
- **Boundary:** diagnostic only; no screening, candidate import, final event, or protocol-term addition.

## Register and baseline

Eleven field-location checks completed. The six confirmed eligible known reports and five contrasts were frozen at **2026-08-23T14:57:32-04:00**, before Q00. The frozen hash is `6d90545006c2bde939a9daa20b0ad51689d20b6bb2794df430c3ecd9e3a312ee`. Q00 then retrieved all **155** current `B1 OR B2` identities. All six known reports were present.

## Completed candidate executions

- model-based engineering: 3 total; 2 unique to Q00; R variant also 3/2.
- model-driven engineering: 5 total; all 5 unique; R variant unchanged.
- model-based design: 8 total; 6 unique; R variant unchanged.
- model-driven design: Q04 was a native explicit zero.

The runner incorrectly treated Q04's valid `stopped_reason=zero_results` as incomplete after the source output had completed. [`q04-explicit-zero-controller-correction.json`](q04-explicit-zero-controller-correction.json) records the correction. P14 began with Q04R and did not rerun Q04. The original system-log command also used a timestamp syntax that macOS rejected; [`system-log-controller-correction.json`](system-log-controller-correction.json) indexes the successful retrospective exact-window checks, both with zero matching events.
