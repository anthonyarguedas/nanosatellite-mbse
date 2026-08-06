# Query Search Plan: EPS MBSE in CubeSat/Nanosatellite Development

- **Review run:** `eps-mbse-slr-2026`
- **Protocol:** `protocol.md`, version `1.0`, frozen 2026-08-06
- **Planned evidence window:** 2013 through the date each search is run in 2026
- **Primary databases:** Scopus and IEEE Xplore
- **Search unit:** one exact source-specific query plus its year, language, publication-type, pagination, and retrieval-limit settings

## 1. Purpose and scope

Build a new, independently discovered candidate set for full-text retrieval. The search must support both:

- **Stream A — EPS-explicit:** population × EPS × structured-system-model/MBSE concepts; and
- **Stream B — embedded-thread recall:** population × structured-system-model/MBSE concepts without a mandatory EPS term.

Search sensitivity is broader than final scientific eligibility. Route A/Route B status and the required EPS anchor, model anchor, and explicit bridge are full-text decisions, not metadata assumptions.

## 2. Anti-anchoring and provenance rules

1. Do not inspect Git history, deleted legacy search/corpus/extraction files, or retained source Markdown/PDFs while formulating or screening the independent primary-database search set.
2. Save every raw run, including zero-result, failed, malformed, and overbroad pilots. A failed request is not a zero-result search.
3. Read each complete saved JSON after every run; record both source-reported `total` and records actually retrieved.
4. Give every artifact a new-run query ID and record source, exact query, filters, run date/time, limits/pages, status, assessment, and successor/predecessor refinement.
5. Do not import legacy IDs. Assign `eps-mbse-slr-2026-r####` IDs only after final merge/deduplication. A prior ID may later be recorded only as `legacy_corpus_id` after an independently rediscovered report is matched.
6. The retained `markdown/` and `pdfs/` directories are retrieval caches only. Match against them after independent discovery and screening.

## 3. Eligibility-related search filters

- **Years:** 2013 through search date (inclusive).
- **Language:** English where the database supports a reliable filter; otherwise screen language.
- **Publication types:** journal articles, conference/proceedings papers, and research chapters in edited scholarly proceedings/volumes. Do not intentionally limit to open access.
- **Population:** orbital CubeSat/nanosatellite-class work. `PocketQube`, `picosatellite`, `CanSat`, and generic larger small-satellite work are not positive search concepts; exclude them only during screening unless a precision refinement is demonstrably needed and documented.
- **Outcome and V&V terms:** optional supplementary concepts, never mandatory across the whole search.

## 4. Concept blocks

### P — population

`CubeSat`, `CubeSats`, `cube sat`, `nanosatellite`, `nanosatellites`, `nano-satellite`, `nano-satellites`, `nano satellite`, `nanosat*`, and source-validated spelling variants.

Do not use unqualified `small satellite` in the primary baseline because it greatly expands beyond the separable nanosatellite population. It may be tested in a logged sensitivity probe combined with highly specific MBSE and EPS concepts.

### E — EPS

High-specificity terms:

- `electrical power system`, `electric power system`, `electrical power subsystem`, `electric power subsystem`, `EPS`, `power subsystem`, `electrical architecture`, `power architecture`, `PCDU`, `PMAD`.

Functional/analysis terms:

- `power budget`, `energy budget`, `energy balance`, `power generation`, `solar array`, `battery`, `energy storage`, `power conditioning`, `power distribution`, `power management`, `power interface`, `power mode`, `load profile`.

Bare `EPS` is always intersected with both population and model blocks to suppress unrelated acronym senses.

### M — structured system model / MBSE

- `model-based systems engineering`, `model based systems engineering`, `MBSE`, `SysML`, `systems modeling language`, `system model`, `systems model`, `system modeling`, `systems modelling`, `reference model`, `digital engineering`, `Arcadia`, `Capella`, `object-oriented systems model`.

Broad `model-based` or `simulation` is insufficient alone. When broad model terms are used, combine them with a systems-engineering relation/concern block such as requirements, function/behavior, architecture, interfaces, traceability, parametrics, verification, or validation.

### O/V — optional outcome and V&V probes

- Outcomes: `reliab*`, `mission assurance`, `reproduc*`, `reuse`, `reusable`, `integrab*`, `interoperab*`, `traceab*`, `interface consistency`, `lifecycle continuity`.
- V&V: `verification`, `validation`, `V&V`, `requirements-in-the-loop`, `model checking`, `virtual integration`, `SIL`, `software-in-the-loop`, `HIL`, `hardware-in-the-loop`, `test case`, `test procedure`, `model-to-test`.

## 5. Planned Scopus pilots

Use Scopus `TITLE-ABS-KEY` for concept blocks, `PUBYEAR` through the script's year options, English, and document types `ar`, `cp`, and `ch`. The strings below are starting pilots; every syntax correction or precision refinement must be logged verbatim.

### S-A1 — explicit EPS names × explicit MBSE/language

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-A2 — EPS analyses/interfaces × structured system model

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-B1 — embedded-thread baseline with explicit MBSE/languages

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-B2 — embedded-thread structured-model expansion

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY(requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-V1 — EPS-linked V&V sensitivity probe

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND TITLE-ABS-KEY(verification OR validation OR traceab* OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR SIL OR HIL OR "test case" OR "test procedure") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-O1 — priority-outcome sensitivity probe

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND TITLE-ABS-KEY(reliab* OR "mission assurance" OR reproduc* OR reuse OR reusable OR integrab* OR interoperab* OR traceab*) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

## 6. Planned IEEE Xplore pilots

Use unfielded Boolean metadata search, inclusive years 2013–2026, language `English`, and content types `Journals`, `Conferences`, and `Books`. First run `--count-only`; retrieve the complete result set for each accepted query up to its reported total. Confirm that the endpoint parsed Boolean syntax by inspecting full result lists.

### I-A1

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### I-A2

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("power budget" OR "energy budget" OR "energy balance" OR "solar array" OR battery OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

### I-B1

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### I-B2

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering") AND (requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric OR verification OR validation)
```

### I-V1

```text
(CubeSat OR nanosatellite OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR SIL OR HIL OR "test case" OR "test procedure")
```

### I-O1

```text
(CubeSat OR nanosatellite OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR "mission assurance" OR reproducibility OR reuse OR reusable OR integrability OR interoperability OR traceability)
```

## 7. Supplementary discovery plan

Run supplementary searches only after the independent Scopus/IEEE merge exposes terminology and coverage gaps. The use of arXiv, Semantic Scholar or Google Scholar is forbidden.

### Citation searching

Backward/forward chasing is not part of title/abstract corpus construction until full-text inclusions exist. After full-text screening, chase every included report and relevant secondary review iteratively as required by the protocol, with new candidates rescreened and newly included reports chased. Keep this phase separate in the search log.

## 8. Iteration and count rules

1. Run two or three pilots at a time per source.
2. Count before full retrieval where supported.
3. A query around 30–70 hits is normally manageable. Do not narrow solely to meet that heuristic if doing so removes a prespecified concept; instead partition by EPS or model concept and retrieve all partitions.
4. If a query is overbroad, inspect a sample and refine using field restrictions or structured-model relations—not outcome presence, open-access status, or legacy titles.
5. If a query is too narrow, relax one concept variant at a time and log the effect.
6. Retrieve all records for every final accepted primary-database query, subject only to documented source/API limits.
7. Compare Stream A and Stream B unique yield after deduplication. A broad Stream B query cannot be dropped merely because most records lack EPS terms in metadata.

## 9. Merge, deduplication, and screening

- Merge final accepted runs by normalized DOI, then source ID, then manually confirmed normalized title–author–year.
- Preserve every discovery event: source, query ID, exact query, raw file, rank, and search stream.
- Keep conflicting metadata and document how the preferred value was selected.
- Title/abstract tiers follow the protocol:
  - `core`: clear EPS-primary MBSE or likely explicit EPS thread;
  - `supporting`: plausible CubeSat/nanosatellite structured-system MBSE requiring full text to test for an embedded EPS thread;
  - `rejected`: clearly fails population, publication/date/language, or structured-system-model scope.
- Do not reject a Stream B record solely because EPS/power is absent from its title or abstract.
- Report secondary reviews separately for terminology and citation chasing; do not place them in the primary-evidence corpus.

## 10. Coverage audit and deferred retained-file recall check

Audit at least these concept clusters without using old screening decisions:

- EPS-primary structured models and power/electrical architecture;
- parametric power/energy budgets bound to system models;
- whole-spacecraft SysML/MBSE with possible embedded EPS allocation/interface threads;
- reference/template/domain models and reuse/tailoring;
- digital-engineering/toolchain transformations and interoperability;
- requirements traceability and model-derived V&V;
- executable pre-physical checks, virtual integration, SIL/HIL, and model-to-test continuity;
- conference/proceedings and edited-volume chapters that may be weakly indexed.

Only after the independent candidate set is frozen, compare its normalized DOI/title metadata with the retained `markdown/` and `pdfs/` cache. Record found/not-found status and the independent discovery event for matches. Use misses only to design logged concept-level recall probes; a retained file cannot enter the corpus without rediscovery or protocol-compliant citation chasing.

## 11. Planned artifacts

```text
SLR/SLR1/
  protocol.md
  query-search-plan.md
  search-log.md
  screening.md
  corpus.json
  searches/
    scopus/
    ieee-xplore/
    worklogs/
    merged_candidates.json
    search-manifest.json
    deduplication-report.json
    retained-file-recall-audit.json
    subagent-logs/
```

## 12. Search-stage stopping rule

The bibliographic search and title/abstract corpus stage is complete only when:

- both streams have final accepted runs in both primary databases or a documented source failure;
- all final-query records available within documented source limits have been saved and read;
- required concept clusters and publication types have been audited;
- supplementary searches address observed indexing/coverage gaps;
- Stream A/Stream B and source-unique yields are known;
- additional query refinements are predominantly duplicates or irrelevant records;
- the merged candidate set, screening log, and retrieval corpus pass provenance and count checks; and
- the independent candidate set has undergone the deferred retained-file recall audit.

Citation chasing remains a later search phase tied to full-text inclusions and must not be falsely reported as complete at the corpus-construction stage.
