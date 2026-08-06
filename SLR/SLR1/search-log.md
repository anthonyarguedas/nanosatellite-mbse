# Search Log

Topic: Model-Based Systems Engineering for nanosatellite electrical power systems (EPS)
Review run: `eps-mbse-slr-2026`
Review dir: `SLR/SLR1`
Integrated corpus-search log generated: 2026-08-06T16:00:48Z

## Protocol reuse
- Reused `protocol.md` v1.0 (approved/frozen 2026-08-06) and `query-search-plan.md`; scope and eligibility rules were not redefined.
- The protocol-controlled two-stream design was retained: Stream A required population × EPS × MBSE/system-model concepts; Stream B deliberately omitted an EPS term to recover embedded threads.
- The approval record is integrated in `protocol.md`; no separate approval file was used.
- Anti-anchoring sequence: only final accepted new-run source artifacts were copied to `searches/merge-inputs/`, merged, deterministically deduplicated, and frozen before any retained Markdown/PDF cache inspection.

## Search strategy notes
- Primary databases: Scopus and IEEE Xplore. Supplementary sources: Semantic Scholar and Google Scholar targeted discovery only, not exhaustive searches.
- Common evidence window: 2013–2026 inclusive; no open-access filter. Scopus used English + `ar/cp/ch`; IEEE used English + Journals/Conferences/Books. Source-specific pagination/limits are preserved in `searches/search-manifest.json` and raw artifacts.
- Stream A concepts: CubeSat/nanosatellite population × EPS names/functions/budgets/components × MBSE/structured-system-model terms. Stream B concepts: population × MBSE/language or structured-model + systems-engineering relation terms, without mandatory EPS.
- Outcome and V&V terms were sensitivity probes only, never baseline gates. The coverage-gap audit tested model-driven/model-centric wording, OOSEM/OPM, digital thread/twin, executable/model integration, EPS control/interface terms, and source-observed conceptual/integrated-concurrent wording.
- Scopus metadata supplied blank abstracts/authors across its runs. Those gaps were preserved and treated as missing metadata during title/abstract screening, not as negative evidence.

## Final accepted candidate-input query set

| ID | Database | Stream | Raw artifact | Source total | Bibliographic records retrieved | Why retained |
|---|---|---|---|---:|---:|---|
| S-A1 | Scopus | A | `searches/scopus/S-A1_pilot_r1.json` | 3 | 3 | Final accepted EPS-name × MBSE primary query. |
| S-A2 | Scopus | A | `searches/scopus/S-A2_pilot_r1.json` | 8 | 8 | Final accepted functional EPS/power-energy × system-model primary query. |
| S-B3 | Scopus | B | `searches/scopus/S-B3_pilot-systems-engineering-relation.json` | 63 | 63 | Final accepted systems-engineering-relation Stream-B query. |
| S-B4 | Scopus | B | `searches/scopus/S-B4_pilot-population-wildcard.json` | 58 | 58 | Final accepted structured-model wildcard Stream-B query. |
| S-B1r1 | Scopus | B | `searches/scopus/S-B1r1_pilot-population-wildcard.json` | 79 | 79 | Final accepted population-wildcard Stream-B query. |
| I-A1-F1 | IEEE Xplore | A | `searches/ieee-xplore/I-A1-F1-full.json` | 4 | 4 | Final accepted EPS-name × MBSE query. |
| I-A2-F1 | IEEE Xplore | A | `searches/ieee-xplore/I-A2-F1-full.json` | 2 | 2 | Final accepted functional EPS/power-energy query. |
| I-B1-F1 | IEEE Xplore | B | `searches/ieee-xplore/I-B1-F1-full.json` | 37 | 37 | Final accepted EPS-free MBSE Stream-B query. |
| I-B2-F1 | IEEE Xplore | B | `searches/ieee-xplore/I-B2-F1-full.json` | 41 | 41 | Final accepted EPS-free structured-model Stream-B query. |
| I-A4-F1 | IEEE Xplore | A | `searches/ieee-xplore/I-A4-F1-full.json` | 4 | 4 | Final accepted budget-wording Stream-A query. |
| I-A5-F1 | IEEE Xplore | A | `searches/ieee-xplore/I-A5-F1-full.json` | 2 | 2 | Final accepted EPS-component Stream-A query. |
| S-CG-M3 | Scopus | B | `searches/coverage-gap/S-CG-M3-P1-digital-thread-twin-stream-b.json` | 21 | 21 | Final retained broad digital-thread/digital-twin Stream-B coverage input. |
| I-CG-M3 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M3-F1-digital-thread-twin-stream-b-full.json` | 19 | 19 | Final retained broad digital-thread/digital-twin Stream-B coverage input. |
| S-CG-M3R1 | Scopus | B | `searches/coverage-gap/S-CG-M3R1-P1-digital-thread-twin-structured-stream-b.json` | 7 | 7 | Final retained structured digital-twin Stream-B refinement. |
| S-CG-M4R1 | Scopus | B | `searches/coverage-gap/S-CG-M4R1-P1-executable-integration-structured-stream-b.json` | 2 | 2 | Final retained executable/model-integration precision-refinement input. |
| S-CG-M5 | Scopus | B | `searches/coverage-gap/S-CG-M5-P1-model-based-conceptual-design-stream-b.json` | 1 | 1 | Final retained exact conceptual-design Stream-B input. |
| I-CG-M6 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M6-F1-integrated-concurrent-modeling-stream-b-full.json` | 1 | 1 | Final retained exact integrated/concurrent-modeling Stream-B input. |

### Exact final queries and filters

Scopus final inputs used `TITLE-ABS-KEY` query syntax with `LANGUAGE(english)`, `(DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))`, and script years 2013–2026 (the script appended `PUBYEAR AFT 2012 AND PUBYEAR BEF 2027`). IEEE final inputs used the displayed parenthesized Boolean query with years 2013–2026, English, and Journals/Conferences/Books; every full run used limit/page-size/max-pages 100/100/1. Coverage-gap Scopus used limit/max-pages 100/4 and coverage-gap IEEE used 100/100/1.

<details><summary>S-A1 — Scopus / Stream A — `searches/scopus/S-A1_pilot_r1.json`</summary>

Exact query submitted to the source script:

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

Effective source query after script-applied year clauses:

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027
```

Applied filters/retrieval settings: `{"document_types": ["ar", "cp", "ch"], "language": "English", "limit": 250, "max_pages": 10, "open_access_filter": false, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T10:14:22.000348`

Raw output metadata: `{"extracted_at": "2026-08-06T10:14:22.000348"}`

</details>

<details><summary>S-A2 — Scopus / Stream A — `searches/scopus/S-A2_pilot_r1.json`</summary>

Exact query submitted to the source script:

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

Effective source query after script-applied year clauses:

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027
```

Applied filters/retrieval settings: `{"document_types": ["ar", "cp", "ch"], "language": "English", "limit": 250, "max_pages": 10, "open_access_filter": false, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T10:14:22.074973`

Raw output metadata: `{"extracted_at": "2026-08-06T10:14:22.074973"}`

</details>

<details><summary>S-B3 — Scopus / Stream B — `searches/scopus/S-B3_pilot-systems-engineering-relation.json`</summary>

Exact query submitted to the source script:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

Effective source query after script-applied year clauses:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027
```

Applied filters/retrieval settings: `{"document_types": ["ar", "cp", "ch"], "language": "English", "limit": 300, "max_pages": 12, "open_access_filter": false, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T10:16:45.931430`

Raw output metadata: `{"extracted_at": "2026-08-06T10:16:45.931430"}`

</details>

<details><summary>S-B4 — Scopus / Stream B — `searches/scopus/S-B4_pilot-population-wildcard.json`</summary>

Exact query submitted to the source script:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY(requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

Effective source query after script-applied year clauses:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY(requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027
```

Applied filters/retrieval settings: `{"document_types": ["ar", "cp", "ch"], "language": "English", "limit": 300, "max_pages": 12, "open_access_filter": false, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T10:18:08.568578`

Raw output metadata: `{"extracted_at": "2026-08-06T10:18:08.568578"}`

</details>

<details><summary>S-B1r1 — Scopus / Stream B — `searches/scopus/S-B1r1_pilot-population-wildcard.json`</summary>

Exact query submitted to the source script:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

Effective source query after script-applied year clauses:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027
```

Applied filters/retrieval settings: `{"document_types": ["ar", "cp", "ch"], "language": "English", "limit": 300, "max_pages": 12, "open_access_filter": false, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T10:19:44.001367`

Raw output metadata: `{"extracted_at": "2026-08-06T10:19:44.001367"}`

</details>

<details><summary>I-A1-F1 — IEEE Xplore / Stream A — `searches/ieee-xplore/I-A1-F1-full.json`</summary>

Exact query submitted to the source script:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

Effective source query:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

Applied filters/retrieval settings: `{"content_types": ["Journals", "Conferences", "Books"], "language": "English", "limit": 100, "max_pages": 1, "open_access_filter": false, "page_size": 100, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T14:14:07.617082+00:00`

Raw output metadata: `{"count_only": false, "extracted_at": "2026-08-06T14:14:07.617082+00:00", "max_pages": 1, "page_size": 100, "refinements": ["ContentType:Journals", "ContentType:Conferences", "ContentType:Books", "Language:English"], "requested_limit": 100, "source": "IEEE Xplore", "source_endpoint": "https://ieeexplore.ieee.org/rest/search", "source_records_retrieved": 4, "status": "success", "stopped_reason": "short_page", "year_end": 2026, "year_start": 2013}`

</details>

<details><summary>I-A2-F1 — IEEE Xplore / Stream A — `searches/ieee-xplore/I-A2-F1-full.json`</summary>

Exact query submitted to the source script:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("power budget" OR "energy budget" OR "energy balance" OR "solar array" OR battery OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

Effective source query:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("power budget" OR "energy budget" OR "energy balance" OR "solar array" OR battery OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

Applied filters/retrieval settings: `{"content_types": ["Journals", "Conferences", "Books"], "language": "English", "limit": 100, "max_pages": 1, "open_access_filter": false, "page_size": 100, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T14:14:07.703616+00:00`

Raw output metadata: `{"count_only": false, "extracted_at": "2026-08-06T14:14:07.703616+00:00", "max_pages": 1, "page_size": 100, "refinements": ["ContentType:Journals", "ContentType:Conferences", "ContentType:Books", "Language:English"], "requested_limit": 100, "source": "IEEE Xplore", "source_endpoint": "https://ieeexplore.ieee.org/rest/search", "source_records_retrieved": 2, "status": "success", "stopped_reason": "short_page", "year_end": 2026, "year_start": 2013}`

</details>

<details><summary>I-B1-F1 — IEEE Xplore / Stream B — `searches/ieee-xplore/I-B1-F1-full.json`</summary>

Exact query submitted to the source script:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

Effective source query:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

Applied filters/retrieval settings: `{"content_types": ["Journals", "Conferences", "Books"], "language": "English", "limit": 100, "max_pages": 1, "open_access_filter": false, "page_size": 100, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T14:14:08.039250+00:00`

Raw output metadata: `{"count_only": false, "extracted_at": "2026-08-06T14:14:08.039250+00:00", "max_pages": 1, "page_size": 100, "refinements": ["ContentType:Journals", "ContentType:Conferences", "ContentType:Books", "Language:English"], "requested_limit": 100, "source": "IEEE Xplore", "source_endpoint": "https://ieeexplore.ieee.org/rest/search", "source_records_retrieved": 37, "status": "success", "stopped_reason": "short_page", "year_end": 2026, "year_start": 2013}`

</details>

<details><summary>I-B2-F1 — IEEE Xplore / Stream B — `searches/ieee-xplore/I-B2-F1-full.json`</summary>

Exact query submitted to the source script:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering") AND (requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric OR verification OR validation)
```

Effective source query:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering") AND (requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric OR verification OR validation)
```

Applied filters/retrieval settings: `{"content_types": ["Journals", "Conferences", "Books"], "language": "English", "limit": 100, "max_pages": 1, "open_access_filter": false, "page_size": 100, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T14:14:50.229168+00:00`

Raw output metadata: `{"count_only": false, "extracted_at": "2026-08-06T14:14:50.229168+00:00", "max_pages": 1, "page_size": 100, "refinements": ["ContentType:Journals", "ContentType:Conferences", "ContentType:Books", "Language:English"], "requested_limit": 100, "source": "IEEE Xplore", "source_endpoint": "https://ieeexplore.ieee.org/rest/search", "source_records_retrieved": 41, "status": "success", "stopped_reason": "short_page", "year_end": 2026, "year_start": 2013}`

</details>

<details><summary>I-A4-F1 — IEEE Xplore / Stream A — `searches/ieee-xplore/I-A4-F1-full.json`</summary>

Exact query submitted to the source script:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ((power AND budget) OR (energy AND budget) OR "budget calculation" OR "budget calculating" OR "power calculation" OR "energy calculation") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

Effective source query:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ((power AND budget) OR (energy AND budget) OR "budget calculation" OR "budget calculating" OR "power calculation" OR "energy calculation") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

Applied filters/retrieval settings: `{"content_types": ["Journals", "Conferences", "Books"], "language": "English", "limit": 100, "max_pages": 1, "open_access_filter": false, "page_size": 100, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T14:16:38.114203+00:00`

Raw output metadata: `{"count_only": false, "extracted_at": "2026-08-06T14:16:38.114203+00:00", "max_pages": 1, "page_size": 100, "refinements": ["ContentType:Journals", "ContentType:Conferences", "ContentType:Books", "Language:English"], "requested_limit": 100, "source": "IEEE Xplore", "source_endpoint": "https://ieeexplore.ieee.org/rest/search", "source_records_retrieved": 4, "status": "success", "stopped_reason": "short_page", "year_end": 2026, "year_start": 2013}`

</details>

<details><summary>I-A5-F1 — IEEE Xplore / Stream A — `searches/ieee-xplore/I-A5-F1-full.json`</summary>

Exact query submitted to the source script:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("solar panel" OR "battery management" OR "battery management system" OR "power generation" OR "power conversion" OR "power distribution unit" OR "power conditioning and distribution" OR "power management and distribution") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

Effective source query:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("solar panel" OR "battery management" OR "battery management system" OR "power generation" OR "power conversion" OR "power distribution unit" OR "power conditioning and distribution" OR "power management and distribution") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

Applied filters/retrieval settings: `{"content_types": ["Journals", "Conferences", "Books"], "language": "English", "limit": 100, "max_pages": 1, "open_access_filter": false, "page_size": 100, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T14:18:40.923436+00:00`

Raw output metadata: `{"count_only": false, "extracted_at": "2026-08-06T14:18:40.923436+00:00", "max_pages": 1, "page_size": 100, "refinements": ["ContentType:Journals", "ContentType:Conferences", "ContentType:Books", "Language:English"], "requested_limit": 100, "source": "IEEE Xplore", "source_endpoint": "https://ieeexplore.ieee.org/rest/search", "source_records_retrieved": 2, "status": "success", "stopped_reason": "short_page", "year_end": 2026, "year_start": 2013}`

</details>

<details><summary>S-CG-M3 — Scopus / Stream B — `searches/coverage-gap/S-CG-M3-P1-digital-thread-twin-stream-b.json`</summary>

Exact query submitted to the source script:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR "system model" OR "systems model" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric*) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

Effective source query after script-applied year clauses:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR "system model" OR "systems model" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric*) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027
```

Applied filters/retrieval settings: `{"document_types": ["ar", "cp", "ch"], "language": "English", "limit": 100, "max_pages": 4, "open_access_filter": false, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T10:47:01.487958`

Raw output metadata: `{"extracted_at": "2026-08-06T10:47:01.487958"}`

</details>

<details><summary>I-CG-M3 — IEEE Xplore / Stream B — `searches/coverage-gap/I-CG-M3-F1-digital-thread-twin-stream-b-full.json`</summary>

Exact query submitted to the source script:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND ("systems engineering" OR "system engineering" OR "system model" OR "systems model" OR requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric)
```

Effective source query:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND ("systems engineering" OR "system engineering" OR "system model" OR "systems model" OR requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric)
```

Applied filters/retrieval settings: `{"content_types": ["Journals", "Conferences", "Books"], "language": "English", "limit": 100, "max_pages": 1, "open_access_filter": false, "page_size": 100, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T14:47:53.103417+00:00`

Raw output metadata: `{"count_only": false, "extracted_at": "2026-08-06T14:47:53.103417+00:00", "max_pages": 1, "page_size": 100, "refinements": ["ContentType:Journals", "ContentType:Conferences", "ContentType:Books", "Language:English"], "requested_limit": 100, "source": "IEEE Xplore", "source_endpoint": "https://ieeexplore.ieee.org/rest/search", "source_records_retrieved": 19, "status": "success", "stopped_reason": "short_page", "year_end": 2026, "year_start": 2013}`

</details>

<details><summary>S-CG-M3R1 — Scopus / Stream B — `searches/coverage-gap/S-CG-M3R1-P1-digital-thread-twin-structured-stream-b.json`</summary>

Exact query submitted to the source script:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

Effective source query after script-applied year clauses:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027
```

Applied filters/retrieval settings: `{"document_types": ["ar", "cp", "ch"], "language": "English", "limit": 100, "max_pages": 4, "open_access_filter": false, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T10:52:13.139641`

Raw output metadata: `{"extracted_at": "2026-08-06T10:52:13.139641"}`

</details>

<details><summary>S-CG-M4R1 — Scopus / Stream B — `searches/coverage-gap/S-CG-M4R1-P1-executable-integration-structured-stream-b.json`</summary>

Exact query submitted to the source script:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("executable architecture" OR "executable system architecture" OR "executable system model" OR "model integration" OR "model-integrated" OR "model-to-model transformation" OR "model to model transformation" OR "integrated modeling" OR "integrated modelling" OR "integrated model") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "systems engineering" OR "system engineering") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

Effective source query after script-applied year clauses:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("executable architecture" OR "executable system architecture" OR "executable system model" OR "model integration" OR "model-integrated" OR "model-to-model transformation" OR "model to model transformation" OR "integrated modeling" OR "integrated modelling" OR "integrated model") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "systems engineering" OR "system engineering") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027
```

Applied filters/retrieval settings: `{"document_types": ["ar", "cp", "ch"], "language": "English", "limit": 100, "max_pages": 4, "open_access_filter": false, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T10:52:12.973646`

Raw output metadata: `{"extracted_at": "2026-08-06T10:52:12.973646"}`

</details>

<details><summary>S-CG-M5 — Scopus / Stream B — `searches/coverage-gap/S-CG-M5-P1-model-based-conceptual-design-stream-b.json`</summary>

Exact query submitted to the source script:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("model-based conceptual design" OR "model based conceptual design") AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric*) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

Effective source query after script-applied year clauses:

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("model-based conceptual design" OR "model based conceptual design") AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric*) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027
```

Applied filters/retrieval settings: `{"document_types": ["ar", "cp", "ch"], "language": "English", "limit": 100, "max_pages": 4, "open_access_filter": false, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T10:53:57.532948`

Raw output metadata: `{"extracted_at": "2026-08-06T10:53:57.532948"}`

</details>

<details><summary>I-CG-M6 — IEEE Xplore / Stream B — `searches/coverage-gap/I-CG-M6-F1-integrated-concurrent-modeling-stream-b-full.json`</summary>

Exact query submitted to the source script:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("integrated and concurrent modeling" OR "integrated and concurrent modelling" OR "concurrent modeling" OR "concurrent modelling") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering")
```

Effective source query:

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("integrated and concurrent modeling" OR "integrated and concurrent modelling" OR "concurrent modeling" OR "concurrent modelling") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering")
```

Applied filters/retrieval settings: `{"content_types": ["Journals", "Conferences", "Books"], "language": "English", "limit": 100, "max_pages": 1, "open_access_filter": false, "page_size": 100, "years": "2013-2026 inclusive"}`

Saved source timestamp: `2026-08-06T14:55:07.679297+00:00`

Raw output metadata: `{"count_only": false, "extracted_at": "2026-08-06T14:55:07.679297+00:00", "max_pages": 1, "page_size": 100, "refinements": ["ContentType:Journals", "ContentType:Conferences", "ContentType:Books", "Language:English"], "requested_limit": 100, "source": "IEEE Xplore", "source_endpoint": "https://ieeexplore.ieee.org/rest/search", "source_records_retrieved": 1, "status": "success", "stopped_reason": "short_page", "year_end": 2026, "year_start": 2013}`

</details>

## Query log: all new-run artifacts

The complete per-artifact exact query and request metadata are machine-readable in `searches/search-manifest.json`; the corresponding raw JSON/error file remains the source of record. `—` means no source total was supplied—not zero hits. `success_count_only` deliberately retrieves zero candidate records while obtaining an IEEE total.

| ID | Database | Stream | Artifact | Kind / status | Source total | Bibliographic records | Retained? | Assessment / worklog |
|---|---|---|---|---|---:|---:|---|---|
| S-A1-preflight | Scopus | A | `searches/scopus/S-A1_preflight-path-validation-failure.json` | preflight_failure / failed_preflight_no_api_request | — | 0 | no | Local path validation failed before an API request; retry S-A1 succeeded. ([worklog](searches/worklogs/scopus.md)) |
| S-A2-preflight | Scopus | A | `searches/scopus/S-A2_preflight-path-validation-failure.json` | preflight_failure / failed_preflight_no_api_request | — | 0 | no | Local path validation failed before an API request; retry S-A2 succeeded. ([worklog](searches/worklogs/scopus.md)) |
| S-B1-preflight | Scopus | B | `searches/scopus/S-B1_preflight-path-validation-failure.json` | preflight_failure / failed_preflight_no_api_request | — | 0 | no | Local path validation failed before an API request; retry S-B1 succeeded. ([worklog](searches/worklogs/scopus.md)) |
| S-A1 | Scopus | A | `searches/scopus/S-A1_pilot_r1.json` | search_result / success | 3 | 3 | yes | Final accepted EPS-name × MBSE primary query. ([worklog](searches/worklogs/scopus.md)) |
| S-A2 | Scopus | A | `searches/scopus/S-A2_pilot_r1.json` | search_result / success | 8 | 8 | yes | Final accepted functional EPS/power-energy × system-model primary query. ([worklog](searches/worklogs/scopus.md)) |
| S-B1 | Scopus | B | `searches/scopus/S-B1_pilot_r1.json` | search_result / success | 74 | 74 | no | Superseded by population-wildcard refinement S-B1r1. ([worklog](searches/worklogs/scopus.md)) |
| S-B2 | Scopus | B | `searches/scopus/S-B2_pilot.json` | search_result / success | 53 | 53 | no | Superseded by retained B3/B4 alternatives. ([worklog](searches/worklogs/scopus.md)) |
| S-V1 | Scopus | A sensitivity | `searches/scopus/S-V1_pilot.json` | search_result / success | 1 | 1 | no | V&V sensitivity; baseline duplicate. ([worklog](searches/worklogs/scopus.md)) |
| S-O1 | Scopus | A sensitivity | `searches/scopus/S-O1_pilot.json` | search_result / success | 2 | 2 | no | Outcome sensitivity; baseline duplicates. ([worklog](searches/worklogs/scopus.md)) |
| S-A3 | Scopus | A refinement | `searches/scopus/S-A3_pilot-explicit-mbse-functional-eps.json` | search_result / success | 3 | 3 | no | Precision refinement; duplicate-only. ([worklog](searches/worklogs/scopus.md)) |
| S-A4 | Scopus | A refinement | `searches/scopus/S-A4_pilot-structured-bridge-eps.json` | search_result / success | 2 | 2 | no | Structured-bridge refinement; duplicate-only. ([worklog](searches/worklogs/scopus.md)) |
| S-B3 | Scopus | B | `searches/scopus/S-B3_pilot-systems-engineering-relation.json` | search_result / success | 63 | 63 | yes | Final accepted systems-engineering-relation Stream-B query. ([worklog](searches/worklogs/scopus.md)) |
| S-A5 | Scopus | A refinement | `searches/scopus/S-A5_pilot-population-wildcard.json` | search_result / success | 3 | 3 | no | Wildcard check identical to S-A1. ([worklog](searches/worklogs/scopus.md)) |
| S-B4 | Scopus | B | `searches/scopus/S-B4_pilot-population-wildcard.json` | search_result / success | 58 | 58 | yes | Final accepted structured-model wildcard Stream-B query. ([worklog](searches/worklogs/scopus.md)) |
| S-A2r1 | Scopus | A refinement | `searches/scopus/S-A2r1_pilot-population-wildcard.json` | search_result / success | 8 | 8 | no | Wildcard check identical to S-A2. ([worklog](searches/worklogs/scopus.md)) |
| S-B1r1 | Scopus | B | `searches/scopus/S-B1r1_pilot-population-wildcard.json` | search_result / success | 79 | 79 | yes | Final accepted population-wildcard Stream-B query. ([worklog](searches/worklogs/scopus.md)) |
| S-A6 | Scopus | A population sensitivity | `searches/scopus/S-A6_pilot-small-satellite-explicit-eps-sensitivity.json` | search_result / success | 1 | 1 | no | Small-satellite sensitivity; duplicate. ([worklog](searches/worklogs/scopus.md)) |
| S-A7 | Scopus | A population sensitivity | `searches/scopus/S-A7_pilot-small-satellite-functional-eps-sensitivity.json` | search_result / success | 2 | 2 | no | Small-satellite sensitivity; no additional target-population candidate. ([worklog](searches/worklogs/scopus.md)) |
| I-A1-C1 | IEEE Xplore | A | `searches/ieee-xplore/I-A1-C1-count.json` | count_only / success_count_only | 4 | 0 | no | Count-only predecessor of full I-A1-F1. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A1-F1 | IEEE Xplore | A | `searches/ieee-xplore/I-A1-F1-full.json` | full_result / success | 4 | 4 | yes | Final accepted EPS-name × MBSE query. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A2-C1 | IEEE Xplore | A | `searches/ieee-xplore/I-A2-C1-count.json` | count_only / success_count_only | 2 | 0 | no | Count-only predecessor of full I-A2-F1. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A2-F1 | IEEE Xplore | A | `searches/ieee-xplore/I-A2-F1-full.json` | full_result / success | 2 | 2 | yes | Final accepted functional EPS/power-energy query. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-B1-C1 | IEEE Xplore | B | `searches/ieee-xplore/I-B1-C1-count.json` | count_only / success_count_only | 37 | 0 | no | Count-only predecessor of full I-B1-F1. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-B1-F1 | IEEE Xplore | B | `searches/ieee-xplore/I-B1-F1-full.json` | full_result / success | 37 | 37 | yes | Final accepted EPS-free MBSE Stream-B query. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-B2-C1 | IEEE Xplore | B | `searches/ieee-xplore/I-B2-C1-count.json` | count_only / success_count_only | 41 | 0 | no | Count-only predecessor of full I-B2-F1. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-B2-F1 | IEEE Xplore | B | `searches/ieee-xplore/I-B2-F1-full.json` | full_result / success | 41 | 41 | yes | Final accepted EPS-free structured-model Stream-B query. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-V1-C1 | IEEE Xplore | A sensitivity | `searches/ieee-xplore/I-V1-C1-count.json` | count_only / success_count_only | 1 | 0 | no | V&V sensitivity count. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-V1-F1 | IEEE Xplore | A sensitivity | `searches/ieee-xplore/I-V1-F1-full.json` | full_result / success | 1 | 1 | no | V&V sensitivity duplicate of final primary identities. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-O1-C1 | IEEE Xplore | A sensitivity | `searches/ieee-xplore/I-O1-C1-count.json` | count_only / success_count_only | 2 | 0 | no | Outcome sensitivity count. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-O1-F1 | IEEE Xplore | A sensitivity | `searches/ieee-xplore/I-O1-F1-full.json` | full_result / success | 2 | 2 | no | Outcome sensitivity duplicates final primary identities. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A3-C1 | IEEE Xplore | A refinement | `searches/ieee-xplore/I-A3-C1-count.json` | count_only / success_count_only | 2 | 0 | no | Structured-model refinement count. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A3-F1 | IEEE Xplore | A refinement | `searches/ieee-xplore/I-A3-F1-full.json` | full_result / success | 2 | 2 | no | Refinement duplicate of I-A1. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A4-C1 | IEEE Xplore | A | `searches/ieee-xplore/I-A4-C1-count.json` | count_only / success_count_only | 4 | 0 | no | Count-only predecessor of full I-A4-F1. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A4-F1 | IEEE Xplore | A | `searches/ieee-xplore/I-A4-F1-full.json` | full_result / success | 4 | 4 | yes | Final accepted budget-wording Stream-A query. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-B3-C1 | IEEE Xplore | B sensitivity | `searches/ieee-xplore/I-B3-C1-count.json` | count_only / success_count_only | 2 | 0 | no | Population-spelling sensitivity count. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-B3-F1 | IEEE Xplore | B sensitivity | `searches/ieee-xplore/I-B3-F1-full.json` | full_result / success | 2 | 2 | no | Population-spelling sensitivity duplicate. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A5-C1 | IEEE Xplore | A | `searches/ieee-xplore/I-A5-C1-count.json` | count_only / success_count_only | 2 | 0 | no | Count-only predecessor of full I-A5-F1. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A5-F1 | IEEE Xplore | A | `searches/ieee-xplore/I-A5-F1-full.json` | full_result / success | 2 | 2 | yes | Final accepted EPS-component Stream-A query. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A6-C1 | IEEE Xplore | A refinement | `searches/ieee-xplore/I-A6-C1-count.json` | count_only / success_count_only | 5 | 0 | no | Broader electrical-power sensitivity count. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-A6-F1 | IEEE Xplore | A refinement | `searches/ieee-xplore/I-A6-F1-full.json` | full_result / success | 5 | 5 | no | Poor-precision duplicate/noisy refinement. ([worklog](searches/worklogs/ieee-xplore.md)) |
| I-B4-C1 | IEEE Xplore | B sensitivity | `searches/ieee-xplore/I-B4-C1-count.json` | count_only / success_zero | 0 | 0 | no | Successful endpoint-reported zero; no full successor. ([worklog](searches/worklogs/ieee-xplore.md)) |
| SS-A1-P1 | Semantic Scholar | A | `searches/semantic-scholar/SS-A1-P1-cubesat-eps-mbse.json` | service_failure_artifact / service_failure_http_403 | — | 0 | no | HTTP 403 before page 1; no source total or records. ([worklog](searches/worklogs/semantic-scholar.md)) |
| SS-A2-P1 | Semantic Scholar | A | `searches/semantic-scholar/SS-A2-P1-nanosatellite-power-sysml.json` | service_failure_artifact / service_failure_http_403 | — | 0 | no | HTTP 403 before page 1; no source total or records. ([worklog](searches/worklogs/semantic-scholar.md)) |
| SS-A3-P1 | Semantic Scholar | A | `searches/semantic-scholar/SS-A3-P1-cubesat-mbse-budget.json` | service_failure_artifact / service_failure_http_403 | — | 0 | no | HTTP 403 before page 1; no source total or records. ([worklog](searches/worklogs/semantic-scholar.md)) |
| SS-A4-P1 | Semantic Scholar | A | `searches/semantic-scholar/SS-A4-P1-cubesat-reference-model-electrical-power.json` | service_failure_artifact / service_failure_http_403 | — | 0 | no | HTTP 403 before page 1; no source total or records. ([worklog](searches/worklogs/semantic-scholar.md)) |
| SS-B1-P1 | Semantic Scholar | B | `searches/semantic-scholar/SS-B1-P1-nanosatellite-mbse.json` | service_failure_artifact / service_failure_http_403 | — | 0 | no | HTTP 403 before page 1; no source total or records. ([worklog](searches/worklogs/semantic-scholar.md)) |
| SS-V1-P1 | Semantic Scholar | A sensitivity | `searches/semantic-scholar/SS-V1-P1-cubesat-sysml-verification-power.json` | service_failure_artifact / service_failure_http_403 | — | 0 | no | HTTP 403 before page 1; no source total or records. ([worklog](searches/worklogs/semantic-scholar.md)) |
| SS-A5-R1 | Semantic Scholar | A | `searches/semantic-scholar/SS-A5-R1-cubesat-power-budget-interface-sysml.json` | service_failure_artifact / service_failure_http_403 | — | 0 | no | HTTP 403 before page 1; no source total or records. ([worklog](searches/worklogs/semantic-scholar.md)) |
| SS-B2-R1 | Semantic Scholar | B | `searches/semantic-scholar/SS-B2-R1-cubesat-system-reference-model.json` | service_failure_artifact / service_failure_http_403 | — | 0 | no | HTTP 403 before page 1; no source total or records. ([worklog](searches/worklogs/semantic-scholar.md)) |
| SS-B3-R1 | Semantic Scholar | B | `searches/semantic-scholar/SS-B3-R1-cubesat-digital-engineering-requirements-traceability.json` | service_failure_artifact / service_failure_http_403 | — | 0 | no | HTTP 403 before page 1; no source total or records. ([worklog](searches/worklogs/semantic-scholar.md)) |
| GS-A1 | Google Scholar | A | `searches/google-scholar/GS-A1_eps-explicit-structured-model.error.json` | service_failure_artifact / service_failure_before_rank_1 | — | 0 | no | Cannot Fetch from Google Scholar before rank 1/UI total. ([worklog](searches/worklogs/google-scholar.md)) |
| GS-B1 | Google Scholar | B | `searches/google-scholar/GS-B1_eps-free-embedded-thread.error.json` | service_failure_artifact / service_failure_before_rank_1 | — | 0 | no | Cannot Fetch from Google Scholar before rank 1/UI total. ([worklog](searches/worklogs/google-scholar.md)) |
| GS-P1 | Google Scholar | recovery | `searches/google-scholar/GS-P1_chapter-exact-title-recovery.error.json` | service_failure_artifact / service_failure_before_rank_1 | — | 0 | no | Cannot Fetch from Google Scholar before rank 1/UI total. ([worklog](searches/worklogs/google-scholar.md)) |
| GS-R1 | Google Scholar | B recovery | `searches/google-scholar/GS-R1_reference-model-lineage.error.json` | service_failure_artifact / service_failure_before_rank_1 | — | 0 | no | Cannot Fetch from Google Scholar before rank 1/UI total. ([worklog](searches/worklogs/google-scholar.md)) |
| GS-V1 | Google Scholar | A sensitivity | `searches/google-scholar/GS-V1_eps-traceability-vv.error.json` | service_failure_artifact / service_failure_before_rank_1 | — | 0 | no | Cannot Fetch from Google Scholar before rank 1/UI total. ([worklog](searches/worklogs/google-scholar.md)) |
| GS-D1 | Google Scholar | B recovery | `searches/google-scholar/GS-D1_digital-engineering.error.json` | service_failure_artifact / service_failure_before_rank_1 | — | 0 | no | Cannot Fetch from Google Scholar before rank 1/UI total. ([worklog](searches/worklogs/google-scholar.md)) |
| S-CG-M1-P1 | Scopus | B | `searches/coverage-gap/S-CG-M1-P1-model-centric-driven-stream-b.json` | search_result / success | 66 | 66 | no | Duplicate-only model-centric/driven probe. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M1-C1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M1-C1-model-centric-driven-stream-b-count.json` | count_only / success_count_only | 8 | 0 | no | Count-only predecessor; duplicate-only full result. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M1-F1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M1-F1-model-centric-driven-stream-b-full.json` | full_result / success | 8 | 8 | no | Duplicate-only model-centric/driven probe. ([worklog](searches/worklogs/coverage-gap.md)) |
| S-CG-M2-P1 | Scopus | B | `searches/coverage-gap/S-CG-M2-P1-oosem-opm-stream-b.json` | search_result / success | 4 | 4 | no | OOSEM/OPM acronym-confounded audit probe. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M2-C1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M2-C1-oosem-opm-stream-b-count.json` | count_only / success_count_only | 2 | 0 | no | Count-only predecessor; duplicate-only full result. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M2-F1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M2-F1-oosem-opm-stream-b-full.json` | full_result / success | 2 | 2 | no | Duplicate-only OOSEM/OPM probe. ([worklog](searches/worklogs/coverage-gap.md)) |
| S-CG-M3 | Scopus | B | `searches/coverage-gap/S-CG-M3-P1-digital-thread-twin-stream-b.json` | search_result / success | 21 | 21 | yes | Final retained broad digital-thread/digital-twin Stream-B coverage input. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M3-C1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M3-C1-digital-thread-twin-stream-b-count.json` | count_only / success_count_only | 19 | 0 | no | Count-only predecessor of retained I-CG-M3. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M3 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M3-F1-digital-thread-twin-stream-b-full.json` | full_result / success | 19 | 19 | yes | Final retained broad digital-thread/digital-twin Stream-B coverage input. ([worklog](searches/worklogs/coverage-gap.md)) |
| S-CG-M4-P1 | Scopus | B | `searches/coverage-gap/S-CG-M4-P1-executable-integration-stream-b.json` | search_result / success | 7 | 7 | no | Superseded poor-precision executable/co-simulation probe. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M4-C1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M4-C1-executable-integration-stream-b-count.json` | count_only / success_count_only | 8 | 0 | no | Count-only predecessor; superseded poor-precision probe. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M4-F1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M4-F1-executable-integration-stream-b-full.json` | full_result / success | 8 | 8 | no | Superseded poor-precision executable/co-simulation probe. ([worklog](searches/worklogs/coverage-gap.md)) |
| S-CG-E1 | Scopus | A | `searches/coverage-gap/S-CG-E1-P1-eps-control-interface-stream-a.json` | search_result / success | 1 | 1 | no | EPS control/interface sensitivity duplicate. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-E1-C1 | IEEE Xplore | A | `searches/coverage-gap/I-CG-E1-C1-eps-control-interface-stream-a-count.json` | count_only / success_zero | 0 | 0 | no | Successful endpoint-reported zero; no full successor. ([worklog](searches/worklogs/coverage-gap.md)) |
| S-CG-M3R1 | Scopus | B | `searches/coverage-gap/S-CG-M3R1-P1-digital-thread-twin-structured-stream-b.json` | search_result / success | 7 | 7 | yes | Final retained structured digital-twin Stream-B refinement. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M3R1-C1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M3R1-C1-digital-thread-twin-structured-stream-b-count.json` | count_only / success_count_only | 3 | 0 | no | Count-only predecessor; full result audit-only duplicate. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M3R1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M3R1-F1-digital-thread-twin-structured-stream-b-full.json` | full_result / success | 3 | 3 | no | Audit-only primary duplicate. ([worklog](searches/worklogs/coverage-gap.md)) |
| S-CG-M3A-R1 | Scopus | A | `searches/coverage-gap/S-CG-M3A-R1-P1-eps-digital-thread-twin-stream-a.json` | search_result / success_zero | 0 | 0 bibliographic (1 serialized) | no | Successful Scopus zero; one blank placeholder is not bibliographic. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M3A-R1-C1 | IEEE Xplore | A | `searches/coverage-gap/I-CG-M3A-R1-C1-eps-digital-thread-twin-stream-a-count.json` | count_only / success_count_only | 1 | 0 | no | Count-only predecessor; full result audit-only duplicate. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M3A-R1 | IEEE Xplore | A | `searches/coverage-gap/I-CG-M3A-R1-F1-eps-digital-thread-twin-stream-a-full.json` | full_result / success | 1 | 1 | no | Audit-only duplicate represented by retained I-CG-M3. ([worklog](searches/worklogs/coverage-gap.md)) |
| S-CG-M4R1 | Scopus | B | `searches/coverage-gap/S-CG-M4R1-P1-executable-integration-structured-stream-b.json` | search_result / success | 2 | 2 | yes | Final retained executable/model-integration precision-refinement input. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M4R1-C1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M4R1-C1-executable-integration-structured-stream-b-count.json` | count_only / success_count_only | 3 | 0 | no | Count-only predecessor; full result audit-only duplicate. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M4R1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M4R1-F1-executable-integration-structured-stream-b-full.json` | full_result / success | 3 | 3 | no | Audit-only primary duplicate. ([worklog](searches/worklogs/coverage-gap.md)) |
| S-CG-M5 | Scopus | B | `searches/coverage-gap/S-CG-M5-P1-model-based-conceptual-design-stream-b.json` | search_result / success | 1 | 1 | yes | Final retained exact conceptual-design Stream-B input. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M5-C1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M5-C1-model-based-conceptual-design-stream-b-count.json` | count_only / success_zero | 0 | 0 | no | Successful endpoint-reported zero; no full successor. ([worklog](searches/worklogs/coverage-gap.md)) |
| S-CG-M6-P1 | Scopus | B | `searches/coverage-gap/S-CG-M6-P1-integrated-concurrent-modeling-stream-b.json` | search_result / success | 1 | 1 | no | Audit-only primary duplicate. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M6-C1 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M6-C1-integrated-concurrent-modeling-stream-b-count.json` | count_only / success_count_only | 1 | 0 | no | Count-only predecessor of retained I-CG-M6. ([worklog](searches/worklogs/coverage-gap.md)) |
| I-CG-M6 | IEEE Xplore | B | `searches/coverage-gap/I-CG-M6-F1-integrated-concurrent-modeling-stream-b-full.json` | full_result / success | 1 | 1 | yes | Final retained exact integrated/concurrent-modeling Stream-B input. ([worklog](searches/worklogs/coverage-gap.md)) |
| coverage-gap-final-input-summary | Coverage-gap audit | — | `searches/coverage-gap/final-input-summary.json` | generated_input_summary / generated_audit_artifact | — | 0 | no | Lists final retained coverage-gap source files; itself is not a candidate input. ([worklog](searches/worklogs/coverage-gap.md)) |
| coverage-gap-novelty-comparison | Coverage-gap audit | — | `searches/coverage-gap/novelty-comparison.json` | generated_comparison / generated_audit_artifact | — | 0 | no | Generated primary-novelty comparator; not a candidate input. ([worklog](searches/worklogs/coverage-gap.md)) |

## Refinements, failures, and source handling

- **Scopus:** Three initial path-validation preflights (S-A1/S-A2/S-B1) failed locally before any API request; they are not zero-result searches. Portable validation was applied and all actual Scopus requests completed. S-B1r1 replaced S-B1 after the wildcard added five records; S-B3 and S-B4 retained alternative structured/relations coverage. Stream-A wildcard checks and outcome/V&V/small-satellite probes were duplicate-only or not target-population additions.
- **IEEE Xplore:** Planned A1/A2/B1/B2 full runs and retained A4/A5 refinement full runs were complete; all final totals fit one 100-record page. Count-only runs are audit artifacts, not candidate input. I-B4 and selected coverage probes are true endpoint-reported zeros, distinct from failures. Refinements A3/A6/B3 and V&V/outcome full probes were duplicate-only/noisy and not merged.
- **Semantic Scholar:** all 9 varied probes failed with HTTP 403 before page 1. Its script serialized empty fallback JSON; post-integration QA annotated each artifact explicitly as `service_failure_http_403` with `source_total_reported: false`. The source total is recorded as `—`, not zero, and no Semantic Scholar record was merged.
- **Google Scholar:** all 6 targeted fallback/recovery queries failed before rank 1/UI total (`Cannot Fetch from Google Scholar`). They are `service_failure_before_rank_1`, not zero hits. No Google Scholar record was merged.
- **Coverage gap:** M1 and IEEE refinements were duplicate-only; M2 was OPM acronym noise; initial M4 co-simulation/executable wording was too imprecise and superseded. Retained M3/M3R1/M4R1/M5/M6 coverage files preserved the EPS-free Stream-B recall route. Direct EPS digital-twin and EPS control/interface sensitivities did not add an independent candidate input.

## Coverage audit

| Lineage / concept cluster | Representative expected/new-run signal | Found in independently merged candidates? | Found in screened retrieval corpus? | Recall risk / interpretation |
|---|---|---|---|---|
| EPS-primary structured models and electrical architecture | `Open-source CubeSat MBSE ... Power Subsystem`; `CONCURRENT ENGINEERING PROCESS FOR ELECTRICAL ARCHITECTURE ...` | Yes | Yes (core) | Strong direct metadata coverage; full text still tests structured EPS relations. |
| Parametric power/energy budgets bound to models | `Applying Model-Based Systems Engineering on CubeSat Budget Calculating`; MBSE CubeSat mission simulation | Yes | Yes (core) | Direct power/energy terms are sparse and source abstracts can be truncated/missing. |
| Whole-spacecraft SysML/MBSE with potential embedded EPS | CubeSat behavior, RAX, risk, EIRSAT-1 system-model records | Yes | Yes (supporting) | EPS anchor/bridge often absent from metadata, by design of Stream B. |
| Reference/template/reuse lineage | CubeSat System Reference Model interim/application/development/mission-engineering series | Yes | Yes (supporting) | Multiple reports may be lineage-related; full text must identify distinct EPS threads and avoid double counting. |
| Digital engineering, interoperability, transformations | Docs-as-code, semantic-web/data-formalization, information-exchange records | Yes | Yes (supporting) | Digital-engineering labels alone do not establish EPS linkage. |
| Requirements traceability and model-derived V&V | Power-subsystem traceability and MBSE-compliant CubeSat reference-model V&V | Yes | Yes (core/supporting) | Direct EPS target–bridge–V&V evidence remains a full-text question. |
| Digital thread/twin and executable/concurrent modeling | Retained M3/M3R1/M4R1/M5/M6 inputs | Yes (39 candidates with any coverage-gap provenance; 31 coverage-only) | Mixed; conservative supporting plus clear rejects | Broad digital-twin results are noisy; retained to avoid metadata-driven loss of embedded threads. |
| Proceedings/chapters and weak indexing | IEEE AERO/SysCon and Scopus chapter/proceedings records | Yes | Yes | Supplementary source failures leave residual conference/chapter recall risk. |
| Post-freeze retained-cache diagnostic only | Cache-only EPS/electrical-power filenames/metadata (architecture, storage, converters) | No new candidate added | No | Potential terminology/indexing diagnostic only; metadata cannot establish MBSE and some signals are excluded CanSat/PocketQube/standalone work. Logged in `searches/retained-file-recall-audit.json`; no silent query expansion. |

## Merge and deduplication

- Isolated inputs: 17 final accepted artifacts (9 Scopus and 8 IEEE Xplore; 11 primary-source + 6 retained coverage-gap files).
- Raw bibliographic occurrences: 352 (Scopus 242; IEEE Xplore 110; primary 301; coverage gap 51).
- Stock merger invocation completed on `searches/merge-inputs/`: 352 raw → 174 unique. Its IEEE source inference labeled 110 raw events `unknown`; deterministic correction restored the source inventory without changing the 174 identity count.
- Deterministic pass: DOI stage 352 → 206; same-source paperId stage → 174; manually confirmed title+year and title-only fallback each added 0 merges. Final: 174 unique; 178 duplicate occurrences removed.
- Provenance preserves source, query ID, exact query, original raw artifact, isolated copy, stream, phase, rank, and raw source record. Metadata conflicts and preference rules are in `searches/merged_candidates.json` and `searches/deduplication-report.json`.
- Independent freeze: `searches/independent-candidate-freeze.json`, candidate SHA-256 `215d31f22a636cee9f807e5d6b06196954388a8b8b6f414660f5a0c94440ed75`. No legacy candidate/ID/cache item entered the merged set.

## Stream and source unique yield

| Measure | Count |
|---|---:|
| Stream A raw occurrences | 23 |
| Stream B raw occurrences | 329 |
| Unique candidates with Stream A provenance | 18 |
| Unique candidates with Stream B provenance | 170 |
| Stream-A-only unique candidates | 4 |
| Stream-B-only unique candidates | 156 |
| Found by both A and B | 14 |
| Scopus-only unique candidates | 99 |
| IEEE-Xplore-only unique candidates | 40 |
| Found in both primary sources | 35 |

## Title/abstract screening handoff

- Every independently merged candidate received one decision: 6 core, 86 supporting, 82 rejected; 5 secondary/background records are separately retained for future citation chasing.
- `corpus.json` has 92 retrieval candidates only, all `pending_full_text_eligibility`. Route A/Route B, EPS anchors/bridges, final publication type/language, and V&V/outcome evidence are explicitly deferred.

## Deferred retained-cache recall check

- Performed only after the independent freeze and screening. Metadata-only inspection saw 202 retained cache files; 116 cache files matched 35 independently rediscovered reports (5 core; 30 supporting).
- 83 cache files were unmatched/ambiguous and remain cache-only. See `legacy-known-item-register.md` and `searches/retained-file-recall-audit.json`; these did not contribute records, IDs, screening decisions, or evidence.

## Post-freeze RQ1 answerability audit

- **Date:** 2026-08-06. An independent subagent audited all 92 kept records against the RQ1 representation, purpose, input/assumption, abstraction, and reuse/tailoring fields in protocol v1.0. See `searches/integration/rq1-answerability-audit.md` and its machine-readable companion.
- **Prospective source restriction:** the researcher directed that Semantic Scholar and Google Scholar not be used for this audit or future agent-assisted work. This is a prospective operational restriction relative to protocol v1.0's supplementary-source plan; historical failed-attempt artifacts remain only as provenance and were not consulted as audit evidence. Only Scopus and IEEE Xplore were used.
- Three concept probes per primary source tested inputs/assumptions, reuse/tailoring, and abstraction/fidelity. IEEE Xplore used count-only predecessors, giving nine saved raw artifacts in total. Exact queries, filters, source totals, retrieval totals, and hashes are in `searches/rq1-answerability-audit/worklog.md`.
- Six full probes retrieved 107 occurrences: 95 frozen-set duplicates and 12 irrelevant occurrences, with **zero new plausible candidates**. The probes therefore remain isolated coverage evidence and do not alter the frozen 174 candidates or 92-record corpus.
- Audit verdict: the corpus is probably sufficient for an exploratory map of representations, purposes, input types, abstraction, and reuse/tailoring, but all remain full-text dependent. Detailed input reporting, deliberate omissions, and demonstrated rather than intended reuse are specifically at risk.

## Stopping rationale

- Both primary databases completed final accepted Stream-A and deliberately EPS-free Stream-B inputs. All records available within documented source limits were saved/read by specialists, and the retained final input set was isolated and fully merged.
- Planned sensitivity/refinement work covered the prespecified model, EPS, V&V, outcome, population, digital-thread/twin, executable/integration, and proceedings/chapter clusters. Recent refinements were predominantly duplicate-only, zero, or clearly noisy; coverage-gap additions were bounded and screened.
- Supplementary failures are documented as unresolved access limitations, not negative evidence. They remain a recall risk, as do opaque IEEE matching, sparse Scopus metadata, and cache-only terminology signals.
- This closes the corpus-search/title-abstract stage, not the review's full search lifecycle. Protocol-required backward/forward citation chasing starts only from full-text-included reports and relevant secondary reviews; it is explicitly deferred and must not be reported as complete here.
- If the review's final search date extends beyond 2026-08-06, run an update search before final evidence closure.
