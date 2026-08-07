# NTRS revised P×M matrix validation

**Status:** `pilot_not_candidate_search` completed; pre-freeze syntax/count/pagination and local-tag validation only. **No record was screened, classified as a candidate, retained for discovery, retrieved as full text, or used as evidence.** This is not a final search and must be rerun after authorization.

- **Review run:** `eps-mbse-slr-2026`
- **Source/interface:** NASA Technical Reports Server (NTRS), public citations API `POST https://ntrs.nasa.gov/api/citations/search`; normal UI cross-check `https://ntrs.nasa.gov/search`
- **Matrix API run:** 2026-08-07 11:24:17.289859–11:27:54.254357 EDT (UTC−04:00), corresponding to 2026-08-07 15:24:17.289859–15:27:54.254357 UTC
- **Post-run raw/archive verification:** 2026-08-07 11:30:15.182005 EDT (UTC−04:00) / 15:30:15.182005 UTC
- **Date body in every cell:** `published.gte: 2011-01-01`; `published.lte: 2026-08-07`
- **Raw archive (Git-ignored):** `.searches/eps-mbse-slr-2026/press-fix-pilots/2026-08-07/ntrs-revised/`
- **Raw manifest:** 458 non-self-referential entries; `raw-manifest.json` SHA-256 `6a39421df2e5797e47b3b34e67be71330afd7ebf851c02d88862c228a89b1a9a` (also recorded in `raw-manifest.sha256`)

## Corrected separate-cell specification

This resolves only PRESS MAJOR-01, MAJOR-03, MAJOR-04, MINOR-03, and SUGGESTION-01 for NTRS. The cells used no Boolean `AND`/`OR`, parentheses, wildcard, or field syntax. Every compact request body, response, timestamp, and checksum is preserved under the raw archive. The body shape was:

```json
{"q":"<one P_N term> <one M_N term>","published":{"gte":"2011-01-01","lte":"2026-08-07"},"page":{"size":100,"from":0}}
```

```text
P_N = {CubeSat, CubeSats, nanosatellite, "nano-satellite", nanosat, "nano satellites"}
M_N = {MBSE, "model-based systems engineering", "model based systems engineering",
       "model-based system engineering", "model based system engineering", SysML,
       "systems modeling language", "system model", "systems model", "system modeling",
       "systems modeling", "system modelling", "systems modelling", "reference model",
       "digital engineering", Arcadia, Capella, "object-oriented systems model"}
```

The complete matrix, not a sample, was executed: `6 P × 18 M = 108` N-B diagnostic cells. The two added P terms, unquoted `nanosat` and quoted `"nano satellites"`, were each tested against all 18 M terms. Every expanded M term was tested against all six P terms. No mandatory N-A matrix was run: `mandatory N-A = 0`. This adopts SUGGESTION-01 only after securing the full N-B matrix; the full-E operation below is a local subset tag and cannot add a discovery event.

## API reconciliation and no-screening aggregates

All 108 saved API JSON pages were reopened, parsed, and reconciled. Each cell fit one `size:100` page, returned exactly its `stats.total`, and had nonempty, nonduplicate IDs within that cell. The independent post-run verifier confirmed the exact 108-query cross-product, body date/page shape, and raw-page arithmetic.

- Cells attempted / completed / failed: **108 / 108 / 0**
- Pages reconciled: **108 / 108**; all API calls were HTTP 200 on `try-01` (no retries)
- Total-change snapshot restarts: **0**
- Simple overlapping cell sum: **39 source-reported / 39 retrieved**
- ID-deduplicated N-B aggregate: **6 unique NTRS IDs** from 39 discovery events; **33** overlapping events removed only for this aggregate

This aggregate is not a candidate corpus. A dated zero is a valid source result and does not establish spelling or semantic equivalence.

`total/retrieved` for every exact cell:

| M | Exact M term | P01 `CubeSat` | P02 `CubeSats` | P03 `nanosatellite` | P04 `"nano-satellite"` | P05 `nanosat` | P06 `"nano satellites"` |
|---|---|---:|---:|---:|---:|---:|---:|
| M01 | `MBSE` | 4/4 | 0/0 | 1/1 | 0/0 | 1/1 | 0/0 |
| M02 | `"model-based systems engineering"` | 2/2 | 1/1 | 1/1 | 0/0 | 1/1 | 0/0 |
| M03 | `"model based systems engineering"` | 2/2 | 1/1 | 1/1 | 0/0 | 1/1 | 0/0 |
| M04 | `"model-based system engineering"` | 3/3 | 0/0 | 1/1 | 0/0 | 1/1 | 0/0 |
| M05 | `"model based system engineering"` | 3/3 | 0/0 | 1/1 | 0/0 | 1/1 | 0/0 |
| M06 | `SysML` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| M07 | `"systems modeling language"` | 2/2 | 0/0 | 1/1 | 0/0 | 1/1 | 0/0 |
| M08 | `"system model"` | 3/3 | 0/0 | 1/1 | 0/0 | 1/1 | 0/0 |
| M09 | `"systems model"` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| M10 | `"system modeling"` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| M11 | `"systems modeling"` | 2/2 | 0/0 | 1/1 | 0/0 | 1/1 | 0/0 |
| M12 | `"system modelling"` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| M13 | `"systems modelling"` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| M14 | `"reference model"` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| M15 | `"digital engineering"` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| M16 | `Arcadia` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| M17 | `Capella` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| M18 | `"object-oriented systems model"` | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |

`run-report.json` and `post-run-archive-validation.json` retain every cell ID, exact query, body path/hash, total/retrieved result, response checksum, and raw page path.

## Normal-UI form cross-check

The normal public UI returned HTTP 200 and reflected each submitted query exactly. Its server-rendered aggregate total was extracted only from saved UI HTML; no individual result was inspected. The normal-UI URL had no documented publication-date control supplied, so its displayed total is a syntax/display check rather than an asserted equivalence to the date-limited API total.

| UI check | Exact query | UI embedded total | Date-limited API total | Result |
|---|---|---:|---:|---|
| UI-01 | `CubeSat MBSE` | 5 | 4 | Accepted syntax/display; no total-equivalence claim |
| UI-02 | `nanosat MBSE` | 1 | 1 | Accepted syntax/display |
| UI-03 | `"nano satellites" "systems modeling language"` | 0 | 0 | Accepted syntax/display |
| UI-04 | `CubeSat "object-oriented systems model"` | 0 | 0 | Accepted syntax/display |

The first client pass parsed standard HTML entities but not NTRS's literal SSR `&q;` quotation serialization, so its initial UI totals were null. The saved UI pages were reopened and parsed offline by the post-run verifier, which recovered the totals above without a network rerun. This was a client-reporting correction, not an API/source failure.

## Full corrected E local-tag and subset validation

The current dictionary/matcher were used unchanged:

- Dictionary SHA-256: `1b2416c22840bd780d9b47f3ff81c6fd6466f13d52ee9d2ca7b429161a4232ab`
- Matcher SHA-256: `895d7e8fb333d1ce684cda02e6ca795f6fbc29ee70a16cc894c5d8eaaa0203eb`
- Regression fixtures: **10/10 passed**; report SHA-256 `9ae0a8c6d92e7f2ae32ead7afae1940a993cb88911e85978b14cdd47cfe74c9d`
- Full-E self-test: **25/25 E term IDs/forms passed**, including both subsystem phrases, `power mode`/`power modes`, and `battery`/`batteries`

Every one of the six deduplicated N-B metadata records was submitted to the matcher using every string leaf in every archived source-record representation. No attachment or full-text retrieval occurred. All six completed:

```text
B = 6 unique IDs from completed P×M cells
A = 1 of those B IDs with one or more local full-E metadata tags
A ∩ B = 1
B-only = 5
A-only = 0
A ∪ B = 6
A ⊆ B = true
```

`A` is only an EPS-explicit metadata tag within `B`: it is not a source-unique discovery stream, candidate decision, or substitute for later screening. This validates the MAJOR-04/MINOR-03/SUGGESTION-01 design without reviving N-A cells.

## Runtime, client, failures, and inspection

| Item | Value |
|---|---|
| Runtime | Python 3.13.5 via `uv 0.9.28 (0e1351e40 2026-01-29)`; macOS-26.5.2-arm64; OpenSSL 3.0.16 |
| HTTP client | Standard-library `urllib.request.urlopen`; 60-second timeout; 0.30-second inter-page/cell delay; up to three retries after an initial retryable failure |
| Matrix client | `ntrs_revised_pilot_client.py` SHA-256 `12a81430e6ba614e1ad0dabe348976e81dbc31a798487975f8e167e46454f036` |
| Post-run verifier | `post_run_archive_verify.py` SHA-256 `389f4fbd7cd0247ab2390f920e60084e1801f402e2f2767470c81e9fa1cfc9f0` |
| Academic-search NTRS reference client read | `search_ntrs.py` SHA-256 `b2a51f682fecd5acf19dc8730fb636cdaba3957372f331ead67ae96b0a115f4d` |
| Source/API failures | None: 108/108 complete, 0 HTTP/transport/JSON/page failures, 0 retries, 0 total changes |
| Final inspection | Passed: 108 request bodies; 108 raw response pages; 108/108 exact expected P×M queries; all pages reconciled; full-E and structural-subset checks passed |

No tracked strategy, protocol, dictionary, matcher, search log, or other tracked artifact was modified by this work. The raw archive is Git-ignored; this validation log is the only tracked work product. No commit was made.
