## Observations

- **C-B1 setting validated** (`pilot_not_candidate_search`).
  - Displayed count: **72 records**
  - Time: **2026-08-06T20:12:09-0400 (EDT)**
  - Server summary: **“72 records found in Compendex for 1884-2026”**
  - UI state confirmed: Compendex-only, Relevance, 100/page, “Turn autostemming off” checked, and no `WN DT`/`WN DB` clause.

- Normal UI export: selected **1** record; **My PC → CSV → Detailed record**.
  - Native file saved unchanged as `/tmp/slr1-compendex-pilot.csv`.
  - Native CSV: **29 headers**, **1 data row**; required provenance fields `Search source`, `Query`, and `Rank` were absent.
  - Download behavior was set to `/tmp` with events enabled and events drained. The UI click emitted `Page.windowOpen` for `/delivery/download/submit.url`; no download-progress events arrived, but the CSV appeared in `/tmp`.
  - The UI permits only letters/numbers/underscores in its prefix, so the browser-generated file was renamed unchanged to the requested hyphenated filename.

- Created `/tmp/slr1-compendex-normalized.csv` and merged it to `/tmp/slr1-compendex-merged.json`.
  - Source preserved: **Compendex → compendex**
  - Exact query preserved: **yes**
  - Rank preserved: **1**
  - Raw / unique: **1 / 1**

## Recommended plan wording

> For the authorized C-B1 run, use Engineering Village Expert Search with Compendex only, Relevance sorting, 100 results per page, and “Turn autostemming off” checked. Append the literal suffix ` AND (2011-* WN YR) AND (({English}) WN LA)` to the C-B1 core; do not add a document-type or `WN DB` clause. Record the server summary verbatim and audit exported years, because the displayed server range was `1884-2026` despite the literal year clause. Label this interface observation `pilot_not_candidate_search`.
