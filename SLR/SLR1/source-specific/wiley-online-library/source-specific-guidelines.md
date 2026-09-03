# Wiley Online Library

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_wiley_online_library.py`

Save primary final searches in `final-searches/` and name each JSON artifact with its query ID, such as `A1.json`. Adapter version 12 always saves `A1.search-page.png` and `A1.results-page.png` beside that JSON. There is no screenshot opt-out. A successful event requires both PNGs and their hashes, dimensions, and privacy receipt in the JSON.

The JSON and its sibling screenshots are authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Wiley Online Library
- Interface: Web
- Platform: Wiley Online Library
- URL: https://onlinelibrary.wiley.com/search/advanced
- Search field or local route: One Advanced Search `Anywhere` (`AllField`) row.
- Main evidence window: Use `--date-start 2011-01-01 --date-end <cutoff>`. The script applies source month bounds and checks exact retained dates.
- Language: Wiley exposes no Language field or facet on this route. Full-text screening must confirm English.
- Publication type: `articlesChapters` is the source record-family boundary. Do not narrow with `PubType`. It cannot safely replace that route. Do not apply peer-review, access, or full-text-availability limits.
- Database or collection selection: Full Wiley platform. Use the Articles & Chapters route for bibliographic records. Do not treat Collections as records.
- Other shared limits: None.
- Pilot 003 diagnostic capture: the normal native-RIS adapter failed with `total: null` (unrecognizable RIS or a missing Export Citations control). Its non-mergeable two-pass rendered DOI/source-ID ledgers are pilot evidence only. They are not a final bibliographic export or a substitute for native capture.

## Source translation

Use the exact concept membership and Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Every current term is an ordinary token or ordered phrase. The current schedule uses no proximity operator, pair expansion, or local pair test. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal except the three accepted unquoted trailing-`*` population atoms below.
- Atom `A(s)`: `L(s)` inside the single Anywhere row.
- Boolean: Use uppercase `AND` and `OR` with explicit parentheses.
- Ordinary block `F(S)`: join every atom in `S` with source `OR` and fully parenthesize the result.
- Compound blocks: render the protocol definitions directly. Use `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))` for `G_model`. Use `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))` for `G_structure`. Use `F(C1_fixed) OR F(G_DSL)` for `C1`.
- Accepted population compression: in every partition, replace `"CubeSat" OR "CubeSats"`, `"nanosat" OR "nanosats" OR "nanosatellite" OR "nanosatellites"`, and `"SmallSat" OR "SmallSats"` with `CubeSat*`, `nanosat*`, and `SmallSat*`. Preserve every other punctuation, spacing, phrase, and spelling literal. Prefer this shorter rendering. Pilot 004 found the same complete source IDs in the same order for all nine literal and wildcard partition unions. There were no wildcard-only IDs.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Cell plan: use one direct query for every partition except `A2`. Implement `A2` as the lossless union of `F(P) AND F(E_F) AND F(M_H)` and `F(P) AND F(E_F) AND F(M_B)`. With the accepted population compression, every current source cell is at most 2,685 characters. Keep the prospective 2,700-character ceiling. Pilot 004 retained the 2,770-character literal A1 only as the historically accepted comparison baseline.
- Date reconciliation: Wiley applies the enclosing source month. Final collection must reconcile the source-month total and DOI ledger with exact-day client exclusions from visible `First published` dates.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render them with the source operators and compound definitions above.

| ID | Source construction |
|---|---|
| `A1` | `F(P) AND F(E_H) AND F(M_H)` |
| `A2` | `F(P) AND F(E_F) AND (F(M_H) OR F(M_B))` |
| `A3` | `F(P) AND F(E_H) AND F(M_B)` |
| `B1` | `F(P) AND F(M_H)` |
| `B2` | `F(P) AND F(M_B) AND F(R)` |
| `BG1` | `F(P) AND F(G_model)` |
| `BG2` | `F(P) AND F(G_structure)` |
| `BC1` | `F(P) AND F(C1)` |
| `BT2` | `F(P) AND F(M_B) AND F(T_precise)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` and historical `BG1` count-only diagnostics completed with exact query and date-control readback. Totals were `21` and `8`. The later protocol change supersedes its pair-based `BG1` translation.
- [x] [Pilot 002](pilots/002/pilot.md): literal and three-family wildcard A1 runs each returned 21 Articles & Chapters records with the same ordered 21 DOI IDs. It accepted the compression for A1. Pilot 004 later tested and accepted it across the full current schedule. No Language or `PubType` limiter was available or applied.
- [Pilot 003](pilots/003/pilot.md): all nine superseded pair-based schedule entries were attempted with exact-day/source-month reconciliation. A1, A2 (3 cells), A3, B1, BG2, BC1 (3 cells), and BT2 (9 cells) have complete non-mergeable DOI/source-ID ledgers. B2 and BG1 retain null-total failures. Native RIS capture was not accepted for a final Wiley run.
- [x] [Pilot 004](pilots/004/pilot.md): all 20 predeclared current-schedule comparison events completed. The literal and three-wildcard versions had identical complete ordered DOI unions in every partition. Current union totals are A1 21, A2 129, A3 60, B1 86, B2 236, BG1 8, BG2 32, BC1 60, and BT2 137. Adapter version 12 also passed a live no-opt-out screenshot smoke. The pilot validates 42 sibling PNGs.
- [x] [Pilot 005](pilots/005/pilot.md): all ten current source cells completed two matching ordered DOI passes. It reconciled 780 source records from 53 page-scoped native RIS downloads and validated 20 mandatory screenshots. B2 completed with 236 records across 12 pages per pass. BT2 completed with 137 records across seven pages per pass. The A2 union contains 129 DOIs. One month-precision date remains unresolved and retained.

## Recovery boundary after Pilot 003

Pilot 003 is a historical immutable record. Do not edit its saved searches, ledgers, unions, assessment, or conclusions to reflect later adapter work. The historical B2 null-total failure remains in that pilot. A separate post-authorization diagnostic using the version 9 baseline completed two matching rendered DOI passes with 236 IDs for B2. Pilot 004 independently obtained the same current B2 total and two complete ordered passes. This shows that the B2 authorization obstacle is solved for bounded rendered diagnostics. It does not replace the historical failure and it does not claim native target-query RIS completion.

Pilot 004 resolves BG1's current rendered DOI snapshot for diagnostic use. It does not reinterpret Pilot 003. Pilot 005 establishes native RIS readiness for BG1 and every other current source cell. A final BG1 run must still begin with the ordinary Advanced Search preflight, two complete matching passes from page zero, exact native RIS reconciliation, both mandatory screenshots, and a new create-only output. No page resume, pass resume, prior DOI ledger, prior hash, browser page, download, screenshot, or native staging state may be reused.

The collector uses a configurable adapter path and verifies the installed adapter's explicit version-12 capability declaration before importing Playwright, opening a browser, or calling version-12 interfaces. A version-9 authorization baseline remains historical evidence only. The collector uses an exact caller-authorized Wiley target when supplied through `--target-id` or `WILEY_AUTHORIZED_TARGET_ID`. That target binds one shared context only. Each attempt creates and closes a distinct owned page, and it reasserts that the user target was not changed. Target-less use is accepted only for one unambiguous Wiley context and page. The collector never persists target IDs.

Adapter version 12 treats unmatched page-worker wrappers as telemetry because Playwright and CDP do not provide one-to-one worker event delivery. It continues ordinary HTTPS background subresources during exact control activation. Top-level navigation, popup, WebSocket, source query, citation POST, DOI, and RIS checks remain enforced. The exact `sortBy=Earliest` URL is authoritative when the cosmetic Date menu is absent. A stale visible zero shell is ignored only when the positive total, expected card count, and stable IDs all reconcile. The adapter consumes a completed in-memory download response before filesystem fallback and caps the private fallback at five seconds.

The collector and adapter may make bounded isolated snapshot attempts only for `WileySnapshotChangedError` reason codes `source_total_changed` or `ordered_ids_changed`. An active Collections page beyond the verified cap is a nonretryable capability or protocol error. Incomplete cards, changed source controls, and substantive readback drift remain nonretryable. Each attempt gets fresh in-memory state. Access, challenge, syntax, malformed RIS, DOI reconciliation, screenshot, output, and publication failures do not retry within an attempt. Failed attempts never contribute source IDs, records, totals, hashes, RIS bytes, screenshots, query text, URLs, DOM, response text, cookies, tokens, or paths to a later result.
