# Coverage-Gap Audit Worklog

- **Review run:** `eps-mbse-slr-2026`
- **Delegated scope:** cross-database terminology/coverage audit only; no shared merge, screening, retrieval, citation chasing, or edits to shared review artifacts.
- **Search date:** 2026-08-06
- **Sources executed here:** Scopus and IEEE Xplore, exclusively through the `academic-search` skill scripts invoked with `uv run`.

## Inputs, boundaries, and comparator

I read `protocol.md`, `query-search-plan.md`, and all four NEW-RUN worklogs before probing. I used only newly returned Scopus/IEEE final-input metadata to formulate or assess probes. I did **not** inspect Git history, deleted/legacy material, `SLR/SLR1/markdown`, `SLR/SLR1/pdfs`, `merged_candidates.json`, `screening.md`, or `corpus.json`.

The output directory was verified before every write as:

```text
/Users/antho/nanosatellite-mbse/SLR/SLR1/searches/coverage-gap
```

The novelty comparator is deliberately limited to these eleven NEW primary-input files:

- Scopus: `S-A1_pilot_r1.json`, `S-A2_pilot_r1.json`, `S-B1r1_pilot-population-wildcard.json`, `S-B3_pilot-systems-engineering-relation.json`, `S-B4_pilot-population-wildcard.json`
- IEEE Xplore: `I-A1-F1-full.json`, `I-A2-F1-full.json`, `I-A4-F1-full.json`, `I-A5-F1-full.json`, `I-B1-F1-full.json`, `I-B2-F1-full.json`

That comparator contains 301 raw occurrences, 106 distinct nonempty normalized DOIs, and 143 normalized titles. Identity order was normalized DOI, same-source `paperId`, normalized title + year, then normalized-title fallback. No legacy or shared-merge record was used. Machine-readable comparator outputs are `searches/coverage-gap/novelty-comparison.json` and `searches/coverage-gap/final-input-summary.json`.

## Coverage assessment and probe decisions

| Cluster | Existing primary coverage | Audit decision and result |
|---|---|---|
| Model-driven/model-centric systems engineering; singular *model-based system engineering* | Primary strings had plural MBSE wording but not these exact variants. | **Justified M1 probe.** Scopus returned 66/66 and IEEE 8/8, all already in the new primary comparator. The variants do not add an identity at this snapshot. |
| OOSEM; object-oriented systems engineering method; Object-Process Methodology/OPM | Plan only had `object-oriented systems model`; IEEE `I-B4` had zero for that narrower phrase. | **Justified M2 probe.** It exposed an ambiguous `OPM` acronym route, not a title/abstract-confirmed OOSEM/OPM record. Its nonduplicate Scopus records included an optically pumped magnetometer false-positive and an independently recoverable `model-based conceptual design` phrase; M2 is not a final input. |
| Digital thread/digital twin | `digital engineering` was covered, and a digital-twins title already appeared, but neither baseline had a digital-thread/twin term. | **Justified M3 probe.** It returned 21 Scopus and 19 IEEE records with 15 and 18 primary-novel occurrences, respectively. Counts remained manageable; because Stream B is intentionally EPS-free and metadata often omit embedded EPS anchors, the broad M3 files are retained for later screening. |
| Digital twin with a stronger structured-model guard | The broad M3 result list contained expected source noise. Tightening only the systems-model block must not erase the broader Stream-B recall route. | **Justified M3R1 refinement.** The Scopus form added one primary-novel digital-twin identity not in broad M3; the IEEE form was fully primary-duplicate. The Scopus M3R1 file is retained alongside M3. |
| Direct EPS × digital twin/thread | Needed to audit whether an EPS-primary digital-twin route was hidden by the EPS-free B stream. | **Justified Stream-A sensitivity M3A-R1.** Scopus source total was zero; IEEE returned one record, already in `I-CG-M3-F1`. It is audit/provenance evidence, not a separate merge input. |
| Executable architecture/model integration | Baselines covered MBSE/system model but not exact executable/model-integration transformation wording. | **Justified M4 pilot.** The initial executable/co-simulation composite was poor precision (stand-alone control/simulation records), so it was **not** retained. M4R1 removed the broad co-simulation/executable-model alternatives; its Scopus form contributed one primary-novel record and is retained. IEEE M4R1 was fully primary-duplicate. |
| Source-observed model-based conceptual design | `Applying the model-based conceptual design approach ...` was exposed by the M2 pilot and is not an original primary wording. | **Justified M5 probe.** Scopus precisely returned that one primary-novel record; IEEE had a true zero. The Scopus file is retained. |
| Source-observed integrated/concurrent modeling | The M4 pilot exposed the 2020 Team Xc integrated/concurrent-modeling title. | **Justified M6 probe.** Exact source-observed wording returned a primary duplicate in Scopus and the new Team Xc record in IEEE. The IEEE file is retained. |
| EPS control/interface/bus/protection/margin terminology | Primary A already covered system/subsystem, architecture, PCDU/PMAD, budget, generation/storage, conditioning/distribution, management/interface, plus IEEE component refinements. | **Justified E1 sensitivity.** Scopus returned one existing primary record; IEEE reported a successful zero. No additional EPS-only/circuit/simulation expansion is justified. |
| Source-observed `object-oriented functional modeling` | An IEEE final primary record already had this title. | **No redundant rerun.** It was demonstrably captured by the primary final metadata. |

No outcome or V&V term was made a universal gate. All B-stream probes below are EPS-free. The only EPS-required probes are `E1` and Stream-A `M3A-R1`.

## Common filters and execution rules

- **Scopus:** query-level `LANGUAGE(english)` and `(DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))`; script `--year-start 2013 --year-end 2026 --limit 100 --max-pages 4`; no OA filter. Every nonzero Scopus probe total was at most 66 and fully retrieved in its pilot artifact.
- **IEEE Xplore:** `--year-start 2013 --year-end 2026 --content-types Journals Conferences Books --language English`; no OA filter. Each `C1` used `--count-only --limit 1 --page-size 1 --max-pages 1`. Each accepted/nonzero `F1` used `--limit 100 --page-size 100 --max-pages 1`, enough to retrieve its full reported total.
- Every saved JSON was read after writing. IEEE count-only artifacts intentionally have `results_retrieved: 0` despite a nonzero source total. `S-CG-M3A-R1` has Scopus `total: 0` but one all-empty placeholder object; it supplies **zero bibliographic records**, not one candidate.

## Exact probe register

All timestamps below are the saved `extracted_at` values (Scopus local timestamp format; IEEE UTC offset format). `C1` is a count-only artifact and `F1` is a full-result artifact.

### CG-M1 — model-driven/model-centric and singular model-based system engineering (Stream B)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("model-driven systems engineering" OR "model driven systems engineering" OR "model-centric systems engineering" OR "model centric systems engineering" OR "model-based system engineering" OR "model based system engineering") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("model-driven systems engineering" OR "model driven systems engineering" OR "model-centric systems engineering" OR "model centric systems engineering" OR "model-based system engineering" OR "model based system engineering")
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-M1-P1 | `2026-08-06T10:47:03.939155` | `coverage-gap/S-CG-M1-P1-model-centric-driven-stream-b.json` | 66 / 66 | Success; fully retrieved, manageable but duplicate-heavy; 66 primary duplicates, 0 novel. Not retained. |
| I-CG-M1-C1 | `2026-08-06T14:47:01.889500+00:00` | `coverage-gap/I-CG-M1-C1-model-centric-driven-stream-b-count.json` | 8 / 0 | Success count. |
| I-CG-M1-F1 | `2026-08-06T14:47:52.893664+00:00` | `coverage-gap/I-CG-M1-F1-model-centric-driven-stream-b-full.json` | 8 / 8 | Success; all eight DOI-match primary records; 0 novel. Not retained. |

### CG-M2 — OOSEM / object-process methodology / OPM (Stream B)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY(OOSEM OR "object-oriented systems engineering method" OR "object oriented systems engineering method" OR "object-process methodology" OR "object process methodology" OR OPM) AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric*) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND (OOSEM OR "object-oriented systems engineering method" OR "object oriented systems engineering method" OR "object-process methodology" OR "object process methodology" OR OPM) AND ("systems engineering" OR "system engineering" OR requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric)
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-M2-P1 | `2026-08-06T10:47:01.377546` | `coverage-gap/S-CG-M2-P1-oosem-opm-stream-b.json` | 4 / 4 | Success; two primary duplicates and two primary-novel records. No returned title evidences OOSEM/OPM; `OPM` is confounded by optically pumped magnetometer. Not retained; the source-observed conceptual-design record was separately verified by M5. |
| I-CG-M2-C1 | `2026-08-06T14:47:01.890474+00:00` | `coverage-gap/I-CG-M2-C1-oosem-opm-stream-b-count.json` | 2 / 0 | Success count. |
| I-CG-M2-F1 | `2026-08-06T14:47:52.881469+00:00` | `coverage-gap/I-CG-M2-F1-oosem-opm-stream-b-full.json` | 2 / 2 | Success; both DOI-match primary records; 0 novel. Not retained. |

### CG-M3 — digital thread/digital twin with a systems-concern guard (Stream B)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR "system model" OR "systems model" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric*) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND ("systems engineering" OR "system engineering" OR "system model" OR "systems model" OR requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric)
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-M3-P1 | `2026-08-06T10:47:01.487958` | `coverage-gap/S-CG-M3-P1-digital-thread-twin-stream-b.json` | 21 / 21 | Success; 6 primary duplicates, 15 primary-novel occurrences. Retained as final Stream-B input. |
| I-CG-M3-C1 | `2026-08-06T14:47:01.902425+00:00` | `coverage-gap/I-CG-M3-C1-digital-thread-twin-stream-b-count.json` | 19 / 0 | Success count. |
| I-CG-M3-F1 | `2026-08-06T14:47:53.103417+00:00` | `coverage-gap/I-CG-M3-F1-digital-thread-twin-stream-b-full.json` | 19 / 19 | Success; 1 primary duplicate, 18 primary-novel occurrences. Retained as final Stream-B input. |

### CG-M4 — initial executable/model-integration pilot (Stream B; rejected for precision)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("executable architecture" OR "executable system architecture" OR "executable model" OR "executable system model" OR "model integration" OR "model-integrated" OR "model-to-model transformation" OR "model to model transformation" OR "co-simulation" OR cosimulation) AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR "system model" OR "systems model" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric*) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("executable architecture" OR "executable system architecture" OR "executable model" OR "executable system model" OR "model integration" OR "model-integrated" OR "model-to-model transformation" OR "model to model transformation" OR "co-simulation" OR cosimulation) AND ("systems engineering" OR "system engineering" OR "system model" OR "systems model" OR requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric)
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-M4-P1 | `2026-08-06T10:48:43.366160` | `coverage-gap/S-CG-M4-P1-executable-integration-stream-b.json` | 7 / 7 | Success; 2 primary duplicates, 5 primary-novel occurrences. Co-simulation/executable-model alternatives exposed stand-alone control, hardware, and simulation noise. Superseded by M4R1/M6; not retained. |
| I-CG-M4-C1 | `2026-08-06T14:48:44.086780+00:00` | `coverage-gap/I-CG-M4-C1-executable-integration-stream-b-count.json` | 8 / 0 | Success count. |
| I-CG-M4-F1 | `2026-08-06T14:49:04.871423+00:00` | `coverage-gap/I-CG-M4-F1-executable-integration-stream-b-full.json` | 8 / 8 | Success; 2 primary duplicates, 6 primary-novel occurrences, predominantly standalone non-MBSE technical material. Superseded; not retained. |

### CG-E1 — omitted EPS control/interface terminology (Stream A)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("battery management" OR "battery management system" OR "power distribution unit" OR "power conditioning and distribution" OR "power management and distribution" OR "power regulation" OR "voltage regulation" OR "power protection" OR "power monitoring" OR "power mode" OR "power modes" OR "power margin" OR "energy margin" OR "electrical bus" OR "power bus" OR "electrical harness" OR "fault management") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR "model-driven systems engineering" OR "model driven systems engineering" OR "model-centric systems engineering" OR "model centric systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("battery management" OR "battery management system" OR "power distribution unit" OR "power conditioning and distribution" OR "power management and distribution" OR "power regulation" OR "voltage regulation" OR "power protection" OR "power monitoring" OR "power mode" OR "power modes" OR "power margin" OR "energy margin" OR "electrical bus" OR "power bus" OR "electrical harness" OR "fault management") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR "model-driven systems engineering" OR "model driven systems engineering" OR "model-centric systems engineering" OR "model centric systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-E1-P1 | `2026-08-06T10:48:43.366082` | `coverage-gap/S-CG-E1-P1-eps-control-interface-stream-a.json` | 1 / 1 | Success; DOI-match primary record; 0 novel. Not retained. |
| I-CG-E1-C1 | `2026-08-06T14:48:45.109823+00:00` | `coverage-gap/I-CG-E1-C1-eps-control-interface-stream-a-count.json` | 0 / 0 | Successful endpoint-reported zero, not a failure; no full run warranted. |

### CG-M3R1 — digital thread/twin with structured-model wording (Stream B refinement)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering")
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-M3R1-P1 | `2026-08-06T10:52:13.139641` | `coverage-gap/S-CG-M3R1-P1-digital-thread-twin-structured-stream-b.json` | 7 / 7 | Success; 6 primary duplicates and 1 primary-novel record (`Test and Evaluation of AI/ML Enhanced Digital Twin`) absent from broad Scopus M3. Retained. |
| I-CG-M3R1-C1 | `2026-08-06T14:52:13.720517+00:00` | `coverage-gap/I-CG-M3R1-C1-digital-thread-twin-structured-stream-b-count.json` | 3 / 0 | Success count. |
| I-CG-M3R1-F1 | `2026-08-06T14:52:48.213596+00:00` | `coverage-gap/I-CG-M3R1-F1-digital-thread-twin-structured-stream-b-full.json` | 3 / 3 | Success; all primary duplicates. Audit-only, not a separate input. |

### CG-M3A-R1 — direct EPS × digital thread/twin sensitivity (Stream A)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS OR "power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND TITLE-ABS-KEY("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS OR "power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR battery OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND ("digital thread" OR "digital threads" OR "digital twin" OR "digital twins") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering")
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-M3A-R1-P1 | `2026-08-06T10:52:13.107511` | `coverage-gap/S-CG-M3A-R1-P1-eps-digital-thread-twin-stream-a.json` | 0 / 0 | Successful Scopus zero. The raw array's single blank placeholder is not a result; no full successor needed. |
| I-CG-M3A-R1-C1 | `2026-08-06T14:52:13.770130+00:00` | `coverage-gap/I-CG-M3A-R1-C1-eps-digital-thread-twin-stream-a-count.json` | 1 / 0 | Success count. |
| I-CG-M3A-R1-F1 | `2026-08-06T14:52:48.215024+00:00` | `coverage-gap/I-CG-M3A-R1-F1-eps-digital-thread-twin-stream-a-full.json` | 1 / 1 | Success; record is already in retained `I-CG-M3-F1`; audit-only provenance, not a separate input. |

### CG-M4R1 — executable/model-integration precision refinement (Stream B)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("executable architecture" OR "executable system architecture" OR "executable system model" OR "model integration" OR "model-integrated" OR "model-to-model transformation" OR "model to model transformation" OR "integrated modeling" OR "integrated modelling" OR "integrated model") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "systems engineering" OR "system engineering") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("executable architecture" OR "executable system architecture" OR "executable system model" OR "model integration" OR "model-integrated" OR "model-to-model transformation" OR "model to model transformation" OR "integrated modeling" OR "integrated modelling" OR "integrated model") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "systems engineering" OR "system engineering")
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-M4R1-P1 | `2026-08-06T10:52:12.973646` | `coverage-gap/S-CG-M4R1-P1-executable-integration-structured-stream-b.json` | 2 / 2 | Success; one primary duplicate and one primary-novel record (`Probabilistic methods for nanosatellite engineering: A lasercom case study`). Retained conservatively as Stream B; protocol screening must test any EPS thread. |
| I-CG-M4R1-C1 | `2026-08-06T14:52:13.786659+00:00` | `coverage-gap/I-CG-M4R1-C1-executable-integration-structured-stream-b-count.json` | 3 / 0 | Success count. |
| I-CG-M4R1-F1 | `2026-08-06T14:52:48.341418+00:00` | `coverage-gap/I-CG-M4R1-F1-executable-integration-structured-stream-b-full.json` | 3 / 3 | Success; all primary duplicates. Audit-only, not a separate input. |

### CG-M5 — source-observed model-based conceptual design (Stream B)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("model-based conceptual design" OR "model based conceptual design") AND TITLE-ABS-KEY("systems engineering" OR "system engineering" OR requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric*) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("model-based conceptual design" OR "model based conceptual design") AND ("systems engineering" OR "system engineering" OR requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric)
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-M5-P1 | `2026-08-06T10:53:57.532948` | `coverage-gap/S-CG-M5-P1-model-based-conceptual-design-stream-b.json` | 1 / 1 | Success; primary-novel title/year identity. Retained. |
| I-CG-M5-C1 | `2026-08-06T14:53:57.937552+00:00` | `coverage-gap/I-CG-M5-C1-model-based-conceptual-design-stream-b-count.json` | 0 / 0 | Successful endpoint-reported zero; no full successor needed. |

### CG-M6 — source-observed integrated/concurrent modeling (Stream B)

**Scopus exact query**

```text
TITLE-ABS-KEY(cubesat* OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("integrated and concurrent modeling" OR "integrated and concurrent modelling" OR "concurrent modeling" OR "concurrent modelling") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

**IEEE exact query**

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("integrated and concurrent modeling" OR "integrated and concurrent modelling" OR "concurrent modeling" OR "concurrent modelling") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "model integration" OR "model-integrated" OR "systems engineering" OR "system engineering")
```

| Execution | Time | Artifact | Source total / bibliographic records | Status and assessment |
|---|---|---|---:|---|
| S-CG-M6-P1 | `2026-08-06T10:54:54.162373` | `coverage-gap/S-CG-M6-P1-integrated-concurrent-modeling-stream-b.json` | 1 / 1 | Success; primary duplicate (`Concurrent Model-Based Approach for CubeSat Mission Design`). Audit artifact only. |
| I-CG-M6-C1 | `2026-08-06T14:54:54.777266+00:00` | `coverage-gap/I-CG-M6-C1-integrated-concurrent-modeling-stream-b-count.json` | 1 / 0 | Success count. |
| I-CG-M6-F1 | `2026-08-06T14:55:07.679297+00:00` | `coverage-gap/I-CG-M6-F1-integrated-concurrent-modeling-stream-b-full.json` | 1 / 1 | Success; primary-novel Team Xc identity. Retained. |

## Final candidate-input files for integration

These are raw search inputs only, **not screened inclusions**. They preserve the deliberately EPS-free Stream-B recall route and must be passed through the normal shared deduplication/screening workflow.

| ID | Source / stream | File | Raw records | Primary duplicates | Primary-novel occurrences |
|---|---|---|---:|---:|---:|
| S-CG-M3 | Scopus / B | `searches/coverage-gap/S-CG-M3-P1-digital-thread-twin-stream-b.json` | 21 | 6 | 15 |
| I-CG-M3 | IEEE Xplore / B | `searches/coverage-gap/I-CG-M3-F1-digital-thread-twin-stream-b-full.json` | 19 | 1 | 18 |
| S-CG-M3R1 | Scopus / B | `searches/coverage-gap/S-CG-M3R1-P1-digital-thread-twin-structured-stream-b.json` | 7 | 6 | 1 |
| S-CG-M4R1 | Scopus / B | `searches/coverage-gap/S-CG-M4R1-P1-executable-integration-structured-stream-b.json` | 2 | 1 | 1 |
| S-CG-M5 | Scopus / B | `searches/coverage-gap/S-CG-M5-P1-model-based-conceptual-design-stream-b.json` | 1 | 0 | 1 |
| I-CG-M6 | IEEE Xplore / B | `searches/coverage-gap/I-CG-M6-F1-integrated-concurrent-modeling-stream-b-full.json` | 1 | 0 | 1 |

Final-input totals: **51** raw bibliographic occurrences; **14** primary-duplicate occurrences; **37** primary-novel occurrences; **31** unique primary-novel identities after deduplicating the retained gap inputs against one another. `final-input-summary.json` is the machine-readable manifest.

The full-result file `I-CG-M3A-R1-F1-eps-digital-thread-twin-stream-a-full.json` is retained as direct Stream-A audit evidence only: its single record is already present in `I-CG-M3-F1`. The IEEE M3R1/M4R1 full files are likewise audit-only because they contain no primary-novel identity.

## Novelty result and new identities

The following are the **31 metadata identities absent from the new primary final-input union**. This is an identity result, not a title/abstract or full-text eligibility decision. Several are visibly likely to be rejected later; they remain in the raw Stream-B candidate set so that protocol screening, not this coverage audit, makes the final decision.

| DOI or title/year key | Title | Retained-query provenance |
|---|---|---|
| `10.1109/EuCNC/6GSummit68295.2026.11577315` | 6GStarLab: An Open, Containerized In-Orbit Laboratory for Reconfigurable 6G Experiments | I-CG-M3 |
| title/year | A FLAT-SAT PLATFORM FOR THE DEVELOPMENT AND TESTING OF THE 3U HERMES CONSTELLATION SATELLITES (2023) | S-CG-M3 |
| `10.1109/MetroAeroSpace64938.2025.11114511` | A solar sail-propelled SmallSat mission to Phobos: Gravitational field uncertainties, trajectory design, and situational awareness | I-CG-M3 |
| `10.52202/078366-0034` | ADVANCING DIGITAL TWIN IMPLEMENTATION FOR CUBESATS: INTEGRATING THEORETICAL INSIGHTS WITH REAL-WORLD APPLICATIONS | S-CG-M3 |
| `10.52202/083084-0123` | AI-Driven Fault Detection and Autonomous Recovery in CubeSat Constellations | S-CG-M3 |
| `10.1109/ICIRCA69024.2026.11570308` | An Adaptive Edge-AI-Enabled Ionizing Radiation Sensing Architecture for Distributed Nanosatellite and Autonomous Micro-Platform Systems | S-CG-M3; I-CG-M3 |
| `10.52202/083091-0037` | An Advanced Simulation Framework for Sail-Driven Spacecraft Dynamics and Control | S-CG-M3 |
| title/year | Applying the model-based conceptual design approach to ADCS development: A case study of a CubeSat swarm mission (2019) | S-CG-M5 |
| `10.1109/JSTARS.2025.3610288` | DADOS: Decentralized Autonomous Disaster Observation System | I-CG-M3 |
| title/year | HERMES ADCS: FROM SYSTEM DESIGN TO PRE-FLIGHT VERIFICATION AND TESTING (2023) | S-CG-M3 |
| `10.3390/aerospace11080688` | Implementation of a 6U CubeSat Electrical Power System Digital Twin | S-CG-M3 |
| `10.1109/MEMAT68155.2025.11434023` | Implementation of a Visualization Platform for Integrated Electronic Digitalization Technology of Micro-Nano Satellites Based on Cesium | I-CG-M3 |
| `10.1109/SPACE63117.2024.10667871` | Level- 1 Digitally Twinned 1U CubeSat (DT1UC) - concept to reality | S-CG-M3; I-CG-M3 |
| `10.1109/IROS47612.2022.9981525` | Multi-Phase Multi-Modal Haptic Teleoperation | I-CG-M3 |
| `10.1109/CAMA62287.2024.10986039` | Multiple Scattering Analysis Within Swarms of CubeSats Devoted to GNSS Reflectometry | S-CG-M3; I-CG-M3 |
| `10.1109/AERO47225.2020.9172256` | Numerical Predictions for On-Orbit Ionospheric Aerodynamics Torque Experiment | S-CG-M3; I-CG-M3 |
| `10.1109/AERO63441.2025.11068739` | On-Orbit Performance and Lessons Learned for Autonomous Angles-Only Navigation of a Satellite Swarm | S-CG-M3; I-CG-M3 |
| `10.52202/078365-0173` | PERCEPTION DATA SYSTEM FOR SATELLITE MONITORING OF STRATEGIC ASSETS | S-CG-M3 |
| `10.2514/6.2017-0400` | Probabilistic methods for nanosatellite engineering: A lasercom case study | S-CG-M4R1 |
| `10.1002/9783527837427.ch26` | Quantum Communication Networks for 6G | I-CG-M3 |
| `10.1109/JSAC.2026.3700576` | Quantum Machine Learning for Wireless-Powered UAV Positioning in 6G Digital Twin SAGIN With Cooperative Nano-Satellite Constellations | I-CG-M3 |
| `10.1109/AERO47225.2020.9172523` | Rapid SmallSat Mission Formulation: Integrated and Concurrent Modeling in JPL's Team Xc | I-CG-M6 |
| `10.1109/ICSADL67539.2026.11451893` | Revolution of AI and ML Methods in Aerospace Engineering and Systems | I-CG-M3 |
| `10.1109/AERO66936.2026.11519985` | RISs as Enablers for Adaptive and Modular Space Communication Architectures | I-CG-M3 |
| `10.1109/AERO58975.2024.10521316` | Scaling Software Security Analysis to Satellites: Automated Fuzz Testing and Its Unique Challenges | I-CG-M3 |
| title/year | Space Factory 4.0 - New processes for the robotic assembly of modular satellites on an in-orbit platform based on Industrie 4.0 approach (2018) | S-CG-M3 |
| `10.23919/EuCAP63536.2025.10999630` | Synthesis and Validation of Wideband Excitation Coefficients in Plane Wave Generator Systems | I-CG-M3 |
| `10.3390/systems13080656` | Test and Evaluation of AI/ML Enhanced Digital Twin | S-CG-M3R1 |
| `10.1109/ACCESS.2022.3215154` | The State of the Art of Information Integration in Space Applications | I-CG-M3 |
| `10.1109/iSpaRo66239.2025.11436987` | Toward Learning-Based Power Subsystem Simulation for Scalable Digital Twins in Distributed Space Systems | S-CG-M3; I-CG-M3 |
| `10.52202/083098-0025` | Validation of Alba CubeSat's Thermal Model: from simulations to experimental testing | S-CG-M3 |

The exact raw metadata, including unlisted `paperId`s, years, and cross-source provenance, are in `searches/coverage-gap/final-input-summary.json`. Especially relevant metadata-level recall signals are the 2024 `Implementation of a 6U CubeSat Electrical Power System Digital Twin`, the 2025 power-subsystem digital-twin record, the source-observed conceptual-design record, and the Team Xc integrated/concurrent-modeling record. None is asserted here to meet the protocol's full-text EPS-anchor/model-anchor/bridge rule.

## Rejected or audit-only probes

- **M1:** both databases were entirely primary-duplicate; no model-centric/driven/singular-MBSE candidate was added.
- **M2:** the OPM acronym was ambiguous; no returned title/available abstract confirmed OOSEM, Object-Process Methodology, or an OPM systems method. The isolated source-observed conceptual-design wording was rerun cleanly as M5.
- **M4 initial:** adding `executable model` and `co-simulation` admitted stand-alone control, electronics, and simulation records. M4R1 removed those broad alternatives; its IEEE counterpart was fully redundant.
- **E1:** Scopus's sole result was already primary; IEEE was a true filtered zero. Further expansion into circuit, component, simulation, or generic electrical-power literature is not justified.
- **M3A-R1:** direct EPS sensitivity returned no Scopus record and one IEEE record already present via the retained B query. It remains an audit/provenance artifact only.
- **M3R1/M4R1 IEEE counterparts and M6 Scopus counterpart:** fully primary-duplicate; retained as audit artifacts rather than additional merge inputs.

## Validation and source limitations

- All 30 JSON artifacts in `searches/coverage-gap/` parse. Every saved query result/count artifact was read after saving. The two generated comparison JSON files were also read after writing.
- No coverage-probe database request failed. IEEE's `E1` and `M5` zeros are endpoint-reported successful zeros, not errors. Scopus M3A-R1 is also a source total zero, with the noted blank-placeholder normalization quirk.
- A first local attempt to regenerate `final-input-summary.json` failed before writing because of a Map-key typo in the local comparison helper. It made no database request and did not overwrite an artifact; the corrected run succeeded, was read back, and produced the counts reported above.
- Scopus continues to expose empty abstracts/authors in these metadata artifacts. IEEE uses an unfielded endpoint and often truncates abstracts; it can return records whose visible metadata do not make the Boolean match transparent. Consequently, novelty is bibliographic only and later screening must not infer MBSE qualification, an EPS anchor, an EPS bridge, an outcome claim, or V&V from these records.
- Broad digital-twin metadata are noisy by nature. Several primary-novel records are plainly likely wrong population, wrong subsystem, secondary, or stand-alone analysis/simulation; this is expected Stream-B screening workload, not evidence membership.
- Semantic Scholar remains unavailable after documented HTTP 403 failures, and Google Scholar remains unavailable after documented fetch failures. Those are unresolved supplementary recall risks, not zero-result sources.

## Stopping rationale

All specifically requested structured-system-model families were tested in both primary sources where syntax permitted: model-driven/model-centric variants, OOSEM/OPM, digital thread/twin, executable/model integration, direct EPS digital twin, and source-observed conceptual/integrated-concurrent modeling. The EPS control/interface sensitivity also completed in both sources without identifying a novel primary identity. Refinements removed the only clear broadening route (`co-simulation`/stand-alone technical simulation) while retaining the protocol-mandated EPS-free Stream-B recall path. Model-centric/driven and IEEE refined integrations were duplicate-only; OPM was acronym-noise; further variants would mainly recycle baseline MBSE/system-model results or broaden into disallowed stand-alone technical literature. No protocol or eligibility-criteria amendment is indicated. Remaining recall risk is limited to opaque database matching, metadata sparsity, unavailable supplementary sources, later full-text screening, and protocol-required citation chasing.
