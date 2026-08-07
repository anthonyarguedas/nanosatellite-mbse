# Wiley Online Library interface-validation report

**Run:** 2026-08-06, EDT (UTC−04:00).<br>
**Scope:** live UI only; no login, saved search, citation-file export, or full-text download. No repository files edited.

## Observed interface

- **Provider/platform:** Wiley Online Library (Wiley), `https://onlinelibrary.wiley.com/`
- **Advanced search:** `https://onlinelibrary.wiley.com/search/advanced`
- **Search endpoint:** GET `https://onlinelibrary.wiley.com/action/doSearch`
- An initial Cloudflare “Performing security verification” screen completed automatically after ~15 seconds; no user action was required.
- The UI showed `Login / Register`; no account was used.

### Search fields and syntax — observed

| UI label | Native field value |
|---|---|
| Anywhere | `AllField` |
| Title | `Title` |
| Author | `Contrib` |
| Keywords | `Keyword` |
| Abstract | `Abstract` |
| Author Affiliation | `Affiliation` |
| Funding Agency | `FundingAgency` |

Three Context Search rows are initially available. The server rendered non-empty rows as `AND`-combined. A field probe submitted:

```text
field1=Title; text1=CubeSat
field2=Abstract; text2=MBSE
```

and the server rendered:

```text
[Publication Title: cubesat] AND [Abstract: mbse]
```

with **2** Articles & Chapters results.

The live Search Tips state:

- `AND` (also `+` or `&`), `OR`, and `NOT` (also `-`) are supported; word operators must be uppercase.
- Unseparated terms default to `AND`.
- Double quotes make an exact phrase.
- `?` = one character; `*` = zero or more characters.
- Wildcards cannot begin a term and cannot appear inside quoted phrases.
- Parenthesized Boolean groups, quoted hyphenated phrases, and `nanosat*` were accepted in pilots. The server preserved the intended Boolean grouping in its normalized search title.
- **No precedence rule was documented**: retain explicit parentheses.

### Date/content controls — observed

- Advanced UI: All Dates; Last Month/6 Months/Year; or Custom Range with month/year only.
- Native custom-range parameters: `AfterMonth`, `AfterYear`, `BeforeMonth`, `BeforeYear`.
- `2011-01` through `2026-08` was normalized by Wiley to:

```text
Earliest: (01/01/2011 TO 08/31/2026)
```

- There was **no language control** and no pre-search content-type control.
- Results separate `Articles & Chapters` (`content=articlesChapters&target=default`) from `Collections` (`content=collections&target=collections`).
- Dynamic facets included Publication Type (`PubType=journal` / `PubType=book`), Access Status, Subjects, Published in, and Author. Do not baseline-restrict these.

## Pilot log — observed counts only

All Stream pilots used `field1=AllField` / **Anywhere**, blank fields 2–3, Custom Range January 2011–August 2026, no venue, OA, subject, publication-type, or language restriction.

### W-A1 — Stream A
**Submitted:** 2026-08-06 19:25:08 EDT

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

**Displayed:** `7 results`; `Articles & Chapters (7)`.

### W-B1 — Stream B
**Run:** 2026-08-06 19:27:59–19:28:20 EDT

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

**Displayed:** `44 results`; `Articles & Chapters (44)` plus separate `Collections (1)`.

### W-V1 — optional V&V probe
**Run:** 2026-08-06 19:33:32–19:33:52 EDT

```text
(CubeSat OR nanosatellite OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

**Displayed:** `17 results`; `Articles & Chapters (17)`; `Collections (1)`.

This 690-character one-line Boolean was accepted.

### W-O1 — optional outcome/burden probe
**Run:** 2026-08-06 19:34:23–19:34:43 EDT

```text
(CubeSat OR nanosatellite OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR "mission assurance" OR reproducibility OR reuse OR reusable OR integrability OR interoperability OR traceability OR benefit OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR adoption)
```

**Displayed:** `21 results`; `Articles & Chapters (21)`; `Collections (1)`.

These are interface snapshots, **not** screened candidates or the SLR result set.

## Pagination and export — observed

- Default pagination is `pageSize=20`, zero-indexed `startPage`.
- W-B1 had three Articles & Chapters pages: 20, 20, and 4 records.
- Generated page URLs use, e.g., `...&pageSize=20&startPage=1`.
- A direct navigation to the generated page URL rendered the correct page. One AJAX click changed the URL but initially retained page-1 DOM in this harness; validate active page and rendered records before preserving each page.
- Export modal is page-scoped: W-B page 2 exposed exactly **20** selectable records. Selecting all produced `20 of 20 articles/chapters` and enabled Next.
- Formats: Plain Text, RIS, EndNote, BibTex, Medlars, RefWorks.
- Export form posts to `/action/downloadCitation` and included `include=abs`.
- Citation Help states Direct Import downloads a citation file; Indirect Import displays copy/paste metadata.
- No actual export was triggered. Thus, **20 is a tested safe batch, not a confirmed hard maximum**.

## Recommended exact plan edits — inference from observations

Add an interface-validated Wiley subsection to §9:

```markdown
**Validated interface (2026-08-06):** Wiley Online Library advanced search,
`https://onlinelibrary.wiley.com/search/advanced`, submitting GET requests to
`https://onlinelibrary.wiley.com/action/doSearch`.

Use the UI field `Anywhere` (`fieldN=AllField`) rather than claiming a
TITLE-ABS-KEY-equivalent field. Enter Boolean operators in uppercase, retain
explicit parentheses, quote exact phrases, and use `*` only within unquoted,
non-leading terms.

For a one-line run, submit the verbatim W-A/W-B string as `text1` with
`field1=AllField`. The source-native date controls are
`AfterMonth=1`, `AfterYear=2011`, `BeforeMonth=<run month>`,
`BeforeYear=<run year>`. Record the server-normalized end date, which is the
last day of the selected ending month.

A validated fallback is multi-row advanced search: place P, E, and M OR-blocks
in `text1`, `text2`, and `text3`, respectively, each with `fieldN=AllField`;
Wiley AND-combines non-empty rows. For Stream B, use P in row 1 and M in row 2.
Live-pilot the final strings before accepting this as source-equivalent to the
one-line form.

Do not apply `PubType`, access-status, subject, title, journal, or language
restrictions to the baseline. Preserve the `Articles & Chapters` result set
(`content=articlesChapters&target=default`) and separately log the Collections
tab/count. Screen language and publication type afterward.

Use generated URLs with `pageSize=20&startPage=0,1,...`; verify each rendered
page and reconcile page records with the active-tab count. Record sort
(default Relevance; UI exposes Date as `sortBy=Earliest`).

Use RIS exports in page-scoped batches of 20 as the tested safe procedure.
Do not claim CSV support or an export ceiling absent a fresh live test.
```

## Unresolved limitations

- `Anywhere` is labelled broadly, but the UI does not define its exact metadata/full-text coverage; separate Abstract and Keywords fields exist, but all-field coverage was not independently proven.
- No reliable language facet was exposed.
- Month-only date control overshoots the actual run date to month-end; record this and screen any future-dated records.
- A maximum one-line query length and export batch ceiling were not established.
- Counts are dynamic and include noneligible material types; they must not be used as inclusion counts.
