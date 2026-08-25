# Scopus candidate-terminology register-check observations

- **Pilot:** `S-D01-P12-20260823T145520-0400`
- **Status:** partial; one successful count-only register check, then a controller stop.
- **Observed source result:** RC-K01 returned exact total 1 for the registered DOI plus `ABS("model-based engineering")`; no records were retained by design.
- **Controller incident:** the source adapter correctly labelled a nonzero count-only artifact `status=count_only`. The local runner incorrectly required `status=success` and stopped. This was not a query, access, adapter, total, or completeness failure.
- **Disposition:** no register was frozen and no Q00/candidate-family query ran. P13 restarted all register checks under a new ID after correcting only the local validator.
