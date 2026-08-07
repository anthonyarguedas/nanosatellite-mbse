# Population-term syntax/count audit — pre-freeze

**Status:** complete; `pilot_not_candidate_search` only. No records were screened, retained, exported, or used as evidence.

## Scope

Narrow audit of the frozen population spelling variants in Compendex and Wiley Online Library, with a Scopus web-UI syntax cross-check only if already-authorized normal web access is present. This report will distinguish live observed facts from inferences and will not modify the protocol, query plan, or main search log.

## Frozen conceptual variants

`CubeSat`, `CubeSats`, `"cube sat"`, `nanosatellite`, `nanosatellites`, `nanosat*`, `"nano-satellite"`, `"nano-satellites"`, and `"nano satellite"`.

## Run ledger

**Started:** 2026-08-07 09:13:58 EDT (UTC−04:00).  All activity below is a live, visible-browser `pilot_not_candidate_search`; no records were opened for screening, retained, exported, or treated as evidence. No credential was requested or entered, and no planned Scopus API request or API credential was used.

**Planned controls to verify and log:**

- Compendex/Engineering Village Expert Search: Compendex only; autostemming OFF (the UI action labelled **Turn autostemming off** checked); Relevance; 100/page; no document-type filter; Published = 2011–Latest and literal suffix `AND (2011-* WN YR) AND (({English}) WN LA)`.
- Wiley Online Library Advanced Search: entire Wiley Online Library; one `Anywhere` / `AllField` row; January 2011–August 2026; no venue, type, OA, subject, or language restriction; record `Articles & Chapters` and `Collections` separately.
- Scopus: normal web UI only, if already-authorized access is present; syntax cross-check only, not the planned API execution.

## Exact population blocks under audit

| Platform | Current P block | Revised P block tested/recommended if accepted |
|---|---|---|
| Compendex | `((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY)` | `((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") WN KY)` |
| Wiley | `(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite")` | `(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite")` |
| Scopus | `TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite")` | `TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite")` |

## Live observations

- **Compendex setup observed, 2026-08-07 09:15:49 EDT (UTC−04:00):** the normal Engineering Village Expert Search was accessible without a credential prompt. The visible UI showed Compendex checked and All/Inspec/Knovel clear; Published **2011 to Latest**; Relevance selected; and the checkbox whose label is **Turn autostemming off** checked (therefore autostemming OFF). No document-type control/filter was selected. No export.
- **Compendex current C-B1 preliminary result observed, 2026-08-07 09:16:33 EDT (UTC−04:00):** the exact current string was accepted and echoed in the normal result header: `((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)`. It reported **72 records**, `1 of 3 pages`, in Compendex for `2011-latest`. This submission used the observed Compendex/date/sort/autostemming/no-type controls above, but the results display was still its initial **25/page**; it was repeated after setting **100/page**, so this preliminary value is not used as the controlled comparison.
- **Compendex controlled current C-B1 result observed, 2026-08-07 09:19:17 EDT (UTC−04:00):** with the exact same accepted/echoed string, Compendex only, Published = 2011–Latest, literal `YR`/braced-English suffix, autostemming OFF, Relevance, **100/page**, and no document-type filter, the UI reported **72 records**, `1 of 1 pages`. This is the current-count comparator.
- **Compendex revised C-B1 observed, 2026-08-07 09:20:12 EDT (UTC−04:00):** the UI accepted and echoed `((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)`. Under the same Compendex-only, Published 2011–Latest, literal suffix, autostemming-OFF, Relevance, 100/page, no-document-type-filter controls, it reported **76 records**, `1 of 1 pages`: **+4** versus the controlled current C-B1 count of 72. No export or record-level assessment occurred.
- **Compendex revised C-V1 observed, 2026-08-07 09:21:01 EDT (UTC−04:00):** the Expert UI accepted and echoed the exact string `((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((verification OR validation OR traceab* OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure") WN KY) AND (2011-* WN YR) AND (({English}) WN LA)`. With the same controls, it reported **1 record**, `1 of 1 pages`. This is a syntax/count test only; it is not a current-versus-revised comparison.
- **Compendex revised C-O1 observed, 2026-08-07 09:21:54 EDT (UTC−04:00):** the Expert UI accepted and echoed the exact string `((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((reliab* OR "mission assurance" OR reproduc* OR reuse OR reusable OR integrab* OR interoperab* OR traceab* OR benefit* OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licen* OR adoption) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)`. With the same controls, it reported **1 record**, `1 of 1 pages`. The UI separately offered an unselected “Are you searching for” alternative that altered `PCDU OR PMAD OR EPS`; this was neither clicked nor treated as accepted rewriting. This is a syntax/count test only; it is not a current-versus-revised comparison.
- **Wiley setup observed, 2026-08-07 09:23:05 EDT (UTC−04:00):** the existing normal Wiley Online Library Advanced Search tab was available without a credential action. `field1=AllField`/Anywhere was selected; `text2` and `text3` were blank; the publication/venue field was blank; Custom Range was set to **January 2011 through August 2026** (`AfterMonth=1`, `AfterYear=2011`, `BeforeMonth=8`, `BeforeYear=2026`). No venue, type, OA, subject, or language restriction was set. The UI exposes three initial rows, so “one row” here means only row 1 is non-empty.
- **Wiley current W-B1 observed, 2026-08-07 09:23:49 EDT (UTC−04:00):** submitted exactly in the one non-empty Anywhere/`AllField` row: `(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)`. The normal UI accepted it and its generated GET URL retained `field1=AllField`, that complete `text1`, blank `field2`/`text2` and `field3`/`text3`, and the January-2011/August-2026 parameters. The server-normalized title lowercased unquoted terms, expanded each to an `[Articles & Chapters: …]` clause, retained quoted phrases/wildcard and Boolean grouping, and displayed `[Earliest: (01/01/2011 TO 08/31/2026)]`; no material rewrite was observed. The active default **Articles & Chapters** tab reported **44**; separate **Collections** reported **1**; sort displayed **Relevance**. No export or record-level assessment occurred.
- **Wiley revised W-B1 observed, 2026-08-07 09:25:56 EDT (UTC−04:00):** submitted exactly in the same one-row/settings route: `(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)`. The generated URL retained that complete `text1`, `field1=AllField`, blank rows 2–3, and `AfterMonth=1&AfterYear=2011&BeforeMonth=8&BeforeYear=2026`. The accepted server-normalized title retained the added `[Articles & Chapters: 'nano-satellites']` clause, lowercased unquoted terms, and displayed the same `[Earliest: (01/01/2011 TO 08/31/2026)]`; no material rewrite was observed. **Articles & Chapters = 44; Collections = 1; Relevance.** Thus the revised count change is **0** in each tab (44→44 and 1→1). No export or record-level assessment occurred.
- **Wiley revised W-V1 observed, 2026-08-07 09:27:17 EDT (UTC−04:00):** the one non-empty `AllField` row accepted `(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")`. The generated URL preserved the query/settings; the normalized title retained the added `nano-satellites` clause and rendered terms as `[Articles & Chapters: …]` with the same month-end date display. **Articles & Chapters = 17; Collections = 1; Relevance.** This is a syntax/count test only, not a current-versus-revised comparison; no export or record-level assessment occurred.
- **Wiley revised W-O1 observed, 2026-08-07 09:28:48 EDT (UTC−04:00):** the one non-empty `AllField` row accepted `(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR "mission assurance" OR reproducibility OR reuse OR reusable OR integrability OR interoperability OR traceability OR benefit OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR adoption)`. The generated URL preserved the query/settings; the normalized title retained the added `nano-satellites` clause and rendered terms as `[Articles & Chapters: …]` with the same month-end date display. **Articles & Chapters = 21; Collections = 1; Relevance.** This is a syntax/count test only, not a current-versus-revised comparison; no export or record-level assessment occurred.
- **Scopus setup observed, 2026-08-07 09:30:00 EDT (UTC−04:00):** normal Scopus Advanced Search loaded in the existing browser session and visibly stated **“Brought to you by Bibliothèque ÉTS.”** The UI exposed the Advanced query textbox and documented `TITLE-ABS-KEY` in its Field codes. No sign-in, credential request, Scopus API endpoint/credential use, saved-search action, export, or record-level assessment was made. The following is strictly a web-UI syntax/count cross-check, not the planned Scopus API execution.
- **Scopus revised S-B1 web-UI cross-check observed, 2026-08-07 09:30:45 EDT (UTC−04:00):** submitted exactly: `TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027`. The normal UI accepted it and displayed the equivalent spaced form with `PUBYEAR > 2010` and `PUBYEAR < 2027`; the revised spelling clauses were retained. It reported **80 documents found**. This observed count is **web-UI syntax/count cross-check only**, not a planned API result and not an SLR candidate set; no export or record-level assessment occurred.
- **Scopus current S-B1 web-UI comparator observed, 2026-08-07 09:32:32 EDT (UTC−04:00):** after clearing a stale advanced-query textbox (an immediately preceding concatenated query was rejected as invalid syntax and is not a count), submitted exactly: `TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027`. The normal UI accepted it, rendered `AFT`/`BEF` as `>`/`<`, and reported **75 documents found**. Under this same web-UI-only cross-check, revised versus current is **80 − 75 = +5 documents**. Neither count is a planned API result, candidate set, screened set, or evidence.

## Consolidated observed counts

All values below are live UI observations from the stated time/timezone and controls above, not screening or evidence counts.

| Platform/run | Current | Revised | Observed change / note |
|---|---:|---:|---|
| Compendex C-B1 | 72 records | 76 records | **+4**; controlled comparison, Compendex only, 2011–Latest, literal year/language suffix, autostemming OFF, Relevance, 100/page, no document-type filter |
| Compendex C-V1 | — | 1 record | revised-P syntax/count test only |
| Compendex C-O1 | — | 1 record | revised-P syntax/count test only |
| Wiley W-B1 — Articles & Chapters | 44 | 44 | **0**; same one-row/AllField, January 2011–August 2026, Relevance |
| Wiley W-B1 — Collections | 1 | 1 | **0**; logged separately, not combined with articles/chapters |
| Wiley W-V1 | — | Articles & Chapters 17; Collections 1 | revised-P syntax/count test only |
| Wiley W-O1 | — | Articles & Chapters 21; Collections 1 | revised-P syntax/count test only |
| Scopus S-B1 normal web UI | 75 documents | 80 documents | **+5**; syntax/count cross-check only, **not** planned API execution |

## Observed facts versus inference

### Observed

- The exact revised P blocks below were accepted in the stated normal browser interfaces. Compendex echoed the submitted strings; Wiley retained the new phrase in its normalized AllField title; Scopus retained it while rendering `AFT`/`BEF` as `>`/`<`.
- Under matched C-B1 controls, Compendex changed from 72 to 76. Under matched W-B1 settings, Wiley's displayed tab totals remained 44 Articles & Chapters and 1 Collection. Under matched normal-UI S-B1 syntax, Scopus changed from 75 to 80.
- Wiley's month-only range was server-normalized to 01/01/2011–08/31/2026. No restriction beyond the stated baseline was applied.
- Institutional Scopus web access was present in this browser session. The previous local Scopus API authentication failure is an authentication/entitlement failure, **not a zero result**.

### Inference and recommendation

- The additional Compendex and Scopus totals are compatible with the added spellings matching material under those platform-specific queries. They do **not** identify particular records, establish recall or precision, or prove a stable effect in a later authorized final run.
- Wiley's equal tab totals do **not** prove identical result sets; no set comparison, export, or record-level inspection was performed.
- Recommend the exact revised P blocks below for the pre-freeze text, subject to the project's normal change-control decision. That recommendation is based on accepted syntax and the limited count audit only. It does not authorize final discovery, screening, evidence use, or substitution of Scopus web UI for the planned API execution.

## Exact recommended final population blocks

```text
Compendex
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") WN KY)

Wiley Online Library
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite")

Scopus
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite")
```

## Insertion-ready search-log wording

```markdown
### 2026-08-07 — Population-spelling pre-freeze audit (`pilot_not_candidate_search`)

No records were screened, retained, exported, or used as evidence. This audit did not modify the protocol, query plan, or final search log.

- **Compendex / Engineering Village Expert Search (EDT, UTC−04:00):** Compendex only; Published 2011–Latest; suffix `AND (2011-* WN YR) AND (({English}) WN LA)`; **Turn autostemming off** checked; Relevance; 100/page; no document-type filter. Current C-B1 = 72 records; revised C-B1, with P = `((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") WN KY)`, = 76 records (+4). Revised C-V1 = 1 and revised C-O1 = 1 (syntax/count tests only). No export.
- **Wiley Online Library Advanced Search (EDT, UTC−04:00):** entire Wiley Online Library; one non-empty Anywhere/`AllField` row; `AfterMonth=1&AfterYear=2011&BeforeMonth=8&BeforeYear=2026`; no venue/type/OA/subject/language restriction; Relevance. Current versus revised W-B1: Articles & Chapters 44→44 and Collections 1→1. Revised W-V1: Articles & Chapters 17, Collections 1; revised W-O1: Articles & Chapters 21, Collections 1. Wiley accepted the revised phrase and normalized the date to 01/01/2011–08/31/2026. No export.
- **Scopus normal web UI (EDT, UTC−04:00; syntax cross-check only—not planned API execution):** with unchanged M/language/document-type blocks and `PUBYEAR AFT 2010 AND PUBYEAR BEF 2027`, current S-B1 = 75 documents and revised S-B1 P = `TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite")` = 80 documents (+5). The UI rendered `AFT`/`BEF` as `>`/`<`. No Scopus API endpoint/credential, export, screening, or evidence action was used. Earlier local API authentication failure is not a zero result.
```

## Completion and limitations

**Completed:** 2026-08-07 09:34:51 EDT (UTC−04:00).

- This audit did not edit any main protocol, query-plan, or search-log file.
- The four Compendex/Wiley sensitivity probes were revised-P syntax/count tests; only C-B1, W-B1, and the Scopus web-UI S-B1 cross-check have old/new count comparisons in this audit.
- Dynamic source counts, Wiley's month-end date normalization, and potential set differences mean authoritative discovery still requires the prospectively authorized final executions and their prescribed provenance handling. At completion of this browser audit, the Scopus UI check did not itself validate the API route. A subsequent institutional-network API pilot successfully reproduced current S-B1 = 75 and revised S-B1 = 80 with `COMPLETE` view; see [`2026-08-07-api-population-term-audit.md`](2026-08-07-api-population-term-audit.md). Final API authentication and complete retrieval must still be rerun after authorization.
