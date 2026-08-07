## Observed interface

**Observed 2026-08-06, America/Toronto (EDT, UTC−04:00).** No credentials, full text, saved searches, or account actions used.

- **Provider/platform:** Elsevier B.V. — **Engineering Village**; database **Compendex**.
- **Quick Search:** requested `https://www.engineeringvillage.com/search/quick.url?database=1`, redirected to `https://www.engineeringvillage.com/app/search/quick/?database=1`
- **Expert Search:** `https://www.engineeringvillage.com/search/expert.url?database=1`
- **Quick vs Expert**
  - Quick is a visual general-search builder: field dropdown, “Add search field,” “Add year range,” and database drawer.
  - Expert has one query textarea plus Database, Date, Sort, Autostemming, Search codes, and Browse indexes. Use **Expert** for the frozen strategies.
- **Compendex-only selection**
  - Expert: select **Compendex** only; leave **All**, **Inspec**, and **Knovel** unchecked (`Compendex` value `1`).
  - Quick: click **“Compendex selected”** → Available databases drawer → tick **Select Compendex** only; leave All/Inspec/Knovel clear.
  - No venue/source-title restriction was used.

## Tested syntax and controls

**Observed accepted Expert syntax**

- Boolean: uppercase `AND`, `OR`; nested parentheses accepted.
- Phrases: double quotes accepted, e.g. `"model-based systems engineering"`.
- Wildcard: `nanosat*` accepted.
- Field syntax: `(terms WN CODE)`.
- Expert code table showed:
  - `KY` = Subject/Title/Abstract
  - `YR` = Publication year
  - `LA` = Language
  - `DT` = Document type
  - `c` = Compendex
- `(cpx WN DB)` was accepted in every pilot, although `DB` was **not** displayed in the current Search codes table. Treat its database-guard semantics as not independently proven; retain UI Compendex-only selection.

**Index-generated filters**

```text
(({English}) WN LA)

(({JA}) WN DT) OR (({CA}) WN DT) OR (({CP}) WN DT) OR (({CH}) WN DT)
```

Document-type index values observed: `BK` Book; `CA` Conference article; `CH` Chapter; `CP` Conference proceeding; `DS` Dissertation; `IP` Article in Press; `JA` Journal article; `PA` Patents (before 1970); `RC` Report chapter; `RR` Report review; `UP` Unpublished paper.

**Controls**

- Date tab: Published range, start years 1884–2026; end supports `Latest` (`*`); separate Updates control offers 1–4 weeks.
- `2011-* WN YR` was accepted.
- Autostemming was initially checked (“Turn autostemming off”).
  - 19:59 EDT, `(nanosatellite WN KY) AND (2011-* WN YR) AND (cpx WN DB)`:
    - autostemming off: **3,708**
    - autostemming on: **2,365**
  - `nanosat*` with autostemming off: **3,870**.
  - Observation only: state materially changes retrieval; set and log it explicitly.
- Result display options: 25, 50, 100/page.
- Sort options: Relevance; Date oldest/newest; Author A–Z/Z–A; Source A–Z/Z–A; Publisher A–Z/Z–A.
- Pagination test on C-B2: 42 records = 2 pages at 25/page; selecting 50/page gave 1 page; Next Page reached page 2/2. Date(Newest) selected successfully with `sort=yr&sortdir=dw`.

## Pilot counts

All are `pilot_not_candidate_search`, not candidate-set results. Compendex only; autostemming **on**; types `JA|CA|CP|CH`.

| Pilot | EDT interval | Displayed total | Pages |
|---|---:|---:|---:|
| Raw plan C-B1, no DT block and unbraced `English WN LA` | ~19:46 | 72 | 3 |
| C-B1, validated type/language implementation | 19:55:31–19:55:36 | 68 | 3 |
| C-A1 | 19:56:00–19:56:05 | 3 | 1 |
| C-A2 | 19:56:05–19:56:10 | 4 | 1 |
| C-B2 | 19:56:42–19:56:47 | 42 | 2 |
| C-V1 | 19:57:32–19:57:37 | 1 | 1 |
| C-O1 | 19:57:37–19:57:42 | 1 | 1 |

## Exact recommended query implementation

Use this literal suffix on each strategy, with Expert UI also set to Compendex-only and Published 2011–Latest:

```text
F =  AND (2011-* WN YR) AND (({English}) WN LA) AND (cpx WN DB) AND ((({JA}) WN DT) OR (({CA}) WN DT) OR (({CP}) WN DT) OR (({CH}) WN DT))
```

The following were accepted exactly as `core + F`:

```text
C-A1 core =
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY)

C-A2 core =
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella) WN KY)

C-B1 core =
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY)

C-B2 core =
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") WN KY) AND ((requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) WN KY)

C-V1 core =
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((verification OR validation OR traceab* OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure") WN KY)

C-O1 core =
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((reliab* OR "mission assurance" OR reproduc* OR reuse OR reusable OR integrab* OR interoperab* OR traceab* OR benefit* OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licen* OR adoption) WN KY)
```

## Export / CSV compatibility

**Observed**

- Download modal formats: EndNote/RIS, BibTeX, ASCII, CSV, Excel, PDF, RTF.
- Outputs: Current page view, Citation, Abstract, Detailed record.
- Modal says selected-record basket maximum is **5,000**; this is an observed session-basket limit, not independently proven as per-file export capacity.
- Session selections persist only until session end unless registering/signing in.
- Filename prefix allows only letters, digits, and underscores.

**CSV pilot result**

- Selected one pilot record through normal UI; chose **My PC → CSV → Detailed record**.
- The normal UI performed the selected-record lookup successfully, then opened a transient blank target; no download event, file, or persistent target appeared.
- Therefore:
  - `/tmp/slr1-compendex-pilot.csv`: **not created**
  - native headers / native row count: **unavailable**
  - `/tmp/slr1-compendex-normalized.csv`: **not created**
  - `/tmp/slr1-compendex-merged.json`: **not created**
  - RIS was not attempted/preserved.

**Merge-script observation**

`merge_search_results.py` directly accepts the requested normalized headers: `Search source`, `Query`, `Rank`, `Paper ID`, `DOI`, `Title`, `Authors`, `Publication year`, `Abstract`, `Citation count`, `URL`, `Open access PDF`. It also recognizes likely Compendex native aliases such as Accession number, Document title, Author(s), and Digital Object Identifier. No merge test was run because no normal UI export file materialized.

## Recommended plan edits

1. Replace the vague Compendex type-limit instruction with the explicit `F` suffix above.
2. Record both restrictions: Expert UI Published=2011–Latest **and** `(2011-* WN YR)`.
3. Explicitly require Autostemming=on for the current validated versions, and preserve that state in the search summary/log.
4. Treat Compendex-only UI selection as the primary database restriction; retain `(cpx WN DB)` as accepted syntax but document that the current code table does not list `DB`.
5. State baseline types as `JA`, `CA`, `CP`, `CH`; decide prospectively whether `IP` should ever be included.
6. Set a declared sort and page size for final retrieval; pilots used Relevance/25 by default, while Date(Newest) and 50/100 were validated.
7. Add an export preflight: before final execution, an authorized operator must confirm that normal CSV Detailed export actually creates a local file and then run the prescribed normalization/merge test.

## Unresolved limitations

- Search access worked; no CAPTCHA or authentication wall appeared. The export failure is **not** a zero-result condition.
- The browser-visible export flow did not create a file, so headers, native CSV compatibility, and merge compatibility remain unvalidated.
- `(cpx WN DB)` is syntactically accepted but was not semantically compared against an all-database search, to preserve the Compendex-only requirement.
- Counts are live pilot observations and must be rerun after authorization.
- I did not modify repository files.
