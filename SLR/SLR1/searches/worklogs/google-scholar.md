# Google Scholar Targeted-Fallback Worklog

- **Review run:** `eps-mbse-slr-2026`
- **Database/source:** Google Scholar, via the academic-search `search_google_scholar.py` script invoked with `uv run`
- **Search date:** 2026-08-06 UTC
- **Delegated scope:** targeted supplementary discovery/recovery only. No merge, deduplication, screening, retrieval, citation chasing, or eligibility decision was performed.

## Protocol, plan, and anti-anchoring controls applied

- Read `SLR/SLR1/protocol.md`, `SLR/SLR1/query-search-plan.md`, and the NEW-RUN primary search worklogs `searches/worklogs/scopus.md` and `searches/worklogs/ieee-xplore.md` before searching.
- Used only terminology and lineages exposed by the new Scopus/IEEE metadata to formulate these targeted fallback probes. No Git history, deleted legacy material, retained `markdown/`, retained `pdfs/`, legacy candidate records, or legacy screening/extraction information was inspected.
- The output directory was resolved before the first write as `/Users/antho/nanosatellite-mbse/SLR/SLR1/searches/google-scholar` and matched the intended review path.
- Searches were issued in two three-query batches. They are targeted, phrase-rich supplementary probes, **not** an exhaustive Google Scholar search.

## Common execution and rank-selection rule

Every attempted query used:

- Inclusive years: **2013–2026**.
- `--limit 20 --max-pages 2`. The script retrieves at most 10 Scholar ranks per page, so this is a deterministic cap of ranks **1–20**, in source order.
- The cap was chosen to keep an unofficial, scrape-based supplementary source auditable and bounded while retaining the full top-20 rank window for a targeted fallback. It is not a random sample and does not replace the primary-database search.
- Had a usable UI-estimated total exceeded roughly 70, the query would have been narrowed and rerun before any candidate use. No query reached a Scholar results page, so no overbreadth decision could be made.
- `total` is reported below only when surfaced by the source/script from the Scholar UI header. `null`/“unavailable” is a **service failure**, not zero results. Every successful result would have been retained in its returned rank order; no secondary title selection rule was applied.

## Query register

`Date/time` is the UTC failure-completion timestamp saved in the explicit error artifact; the source did not produce a normal result JSON or a UI count. Each error JSON contains the exact query, filters, requested cap, exit code, empty normalized result array, and full error message. The paired `.stderr.log` preserves the tool's raw diagnostic output.

| ID | Batch; stream / purpose | Exact query | Years; date/time UTC | Raw artifact(s) | UI-estimated total | Retrieved count and ranks | Assessment; retained for merge |
|---|---|---|---|---|---:|---|---|
| GS-A1 | Batch 1; **Stream A** EPS-explicit structured-model recovery | <code>("CubeSat" OR nanosatellite) ("electrical power system" OR "power subsystem" OR "electrical architecture") ("model-based systems engineering" OR MBSE OR SysML)</code> | 2013–2026; 2026-08-06T14:34:51Z | `SLR/SLR1/searches/google-scholar/GS-A1_eps-explicit-structured-model.error.json`; `.stderr.log` | unavailable (`null`) | 0; no ranks delivered | `Cannot Fetch from Google Scholar` before rank 1/UI header. Precision and breadth could not be assessed. **No** — error artifact only, no candidate records. |
| GS-B1 | Batch 1; **Stream B** embedded-thread recall, deliberately EPS-free | <code>("CubeSat" OR nanosatellite) ("model-based systems engineering" OR MBSE OR SysML) ("systems architecture" OR "system model" OR requirements OR interfaces)</code> | 2013–2026; 2026-08-06T14:33:59Z | `SLR/SLR1/searches/google-scholar/GS-B1_eps-free-embedded-thread.error.json`; `.stderr.log` | unavailable (`null`) | 0; no ranks delivered | `Cannot Fetch from Google Scholar` before rank 1/UI header. This query intentionally did **not** require EPS, outcomes, or V&V. **No** — error artifact only, no candidate records. |
| GS-P1 | Batch 1; proceedings/chapter recovery, allowed exact-title check | <code>"Validation and verification of MBSE compliant CubeSat reference model"</code> | 2013–2026; 2026-08-06T14:35:03Z | `SLR/SLR1/searches/google-scholar/GS-P1_chapter-exact-title-recovery.error.json`; `.stderr.log` | unavailable (`null`) | 0; no ranks delivered | `Cannot Fetch from Google Scholar` before rank 1/UI header. The exact title was exposed by new Scopus metadata (the 2017 Springer chapter), so its use complies with the exact-title restriction. **No** — error artifact only, no candidate records. |
| GS-R1 | Batch 2; reference-model lineage recovery | <code>("CubeSat System Reference Model" OR "CubeSat MBSE reference model") (SysML OR verification OR "mission engineering")</code> | 2013–2026; 2026-08-06T14:38:13Z | `SLR/SLR1/searches/google-scholar/GS-R1_reference-model-lineage.error.json`; `.stderr.log` | unavailable (`null`) | 0; no ranks delivered | `Cannot Fetch from Google Scholar` before rank 1/UI header. Targets the reference-model lineage without imposing an EPS term. **No** — error artifact only, no candidate records. |
| GS-V1 | Batch 2; **Stream A** EPS traceability / V&V sensitivity recovery | <code>("CubeSat" OR nanosatellite) ("power subsystem" OR "electrical power system") (traceability OR verification OR validation) ("model-based systems engineering" OR MBSE OR SysML)</code> | 2013–2026; 2026-08-06T14:38:02Z | `SLR/SLR1/searches/google-scholar/GS-V1_eps-traceability-vv.error.json`; `.stderr.log` | unavailable (`null`) | 0; no ranks delivered | `Cannot Fetch from Google Scholar` before rank 1/UI header. V&V is used only in this targeted sensitivity probe, not as a gate in the baseline streams. **No** — error artifact only, no candidate records. |
| GS-D1 | Batch 2; digital-engineering / interoperability terminology recovery, EPS-free | <code>("CubeSat" OR nanosatellite) ("digital engineering" OR "data formalization" OR "semantic web") ("model-based systems engineering" OR MBSE OR SysML)</code> | 2013–2026; 2026-08-06T14:38:29Z | `SLR/SLR1/searches/google-scholar/GS-D1_digital-engineering.error.json`; `.stderr.log` | unavailable (`null`) | 0; no ranks delivered | `Cannot Fetch from Google Scholar` before rank 1/UI header. This deliberately EPS-free recovery query targets digital-engineering terminology. **No** — error artifact only, no candidate records. |

## Retrieved-rank audit

There are no omitted ranks: every one of the six requests failed before Scholar returned a rank-1 record or a UI result-count header.

| Query IDs | Requested rank window | Delivered Scholar ranks | Result-rank selection status |
|---|---|---|---|
| GS-A1, GS-B1, GS-P1, GS-R1, GS-V1, GS-D1 | 1–20, source order | none | No records were available to select, exclude, or retain. `results_retrieved: 0` in each error artifact is not an endpoint-reported zero-hit result. |

## Primary-metadata-derived coverage rationale

The following new-primary signals guided the six queries; they are terminology/coverage observations only, not screening decisions:

| Required gap / lineage | New primary metadata signal used | Targeted Scholar query |
|---|---|---|
| EPS-primary models and electrical architecture | 2023 **“Open-source CubeSat MBSE Approach to Address Traceability: Power Subsystem”**; 2025 electrical-architecture and in-situ power-system modelling titles | GS-A1 |
| Embedded EPS-thread recall | New whole-spacecraft CubeSat/nanosatellite MBSE, system-model, behavior, requirements, and interface records | GS-B1 (no EPS requirement) |
| Weakly indexed proceedings/chapters | New Scopus result **“Validation and verification of MBSE compliant CubeSat reference model”** (2017 Springer chapter) | GS-P1 |
| Reference-model/template/reuse lineage | New 2015–2026 CubeSat MBSE/CSRM interim, application, mission-engineering, and metamodel titles | GS-R1 |
| EPS traceability and pre-physical V&V wording | New primary power-subsystem traceability title and reference-model V&V title | GS-V1 |
| Digital-engineering/toolchain terminology | New data-formalization, information-exchange, digital-engineering, and semantic-web CubeSat titles | GS-D1 |

## Refinement lineage and failure handling

1. **Initial targeted set.** GS-A1, GS-B1, and GS-P1 were independent first-pass queries for the EPS-explicit, EPS-free embedded-thread, and proceedings/chapter gaps. GS-P1 is the only exact-title query; its title was exposed by NEW Scopus metadata, not by retained/legacy files.
2. **Continuation after failure.** All three Batch-1 attempts ended in the same Scholar access failure. To complete the prespecified targeted coverage rather than silently drop gaps, GS-R1, GS-V1, and GS-D1 were then attempted as a second independent batch.
3. **No data-driven refinement was possible.** All six requests failed before a UI estimate, result snippet, or rank was returned. A service failure is neither evidence that a query was too broad/narrow nor a basis to invent a refinement. No same-query retry, CAPTCHA/bot-protection bypass, browser automation workaround, regular-web substitute, or outcome/EPS restriction was attempted.
4. **Final targeted set for this source.** There are no accepted Scholar candidate-result files. The six error artifacts remain the complete audit record for the attempted set; none is a merge input.

## Novel-title comparison against NEW primary metadata

The intended comparator was the normalized title union from the new retained Scopus and IEEE result files documented in their worklogs, not any legacy corpus. Because Scholar supplied no title records:

| Query IDs | Scholar titles available for comparison | Exact/normalized matches to new primary metadata | Scholar-novel titles | Interpretation |
|---|---:|---:|---:|---|
| GS-A1, GS-B1, GS-P1, GS-R1, GS-V1, GS-D1 | 0 | 0 | 0 | No comparison was possible. These zeros mean “no source response,” not “no novel literature.” |

No Scholar record was therefore labeled duplicate, novel, core, supporting, or rejected. The integration agent must not interpret the absence of Scholar titles as negative evidence against any of the targeted lineages.

## JSON validation and counts

- Validated all **6** saved `*.error.json` artifacts with `jq` after readback. Each is a parseable object with the required query ID/string, years, deterministic cap, `status: "service_failure"`, `total: null`, `results_retrieved: 0`, an empty `results` array, numeric exit code, and nonempty error text.
- Normal Scholar result JSON files: **0**. The source script exited nonzero before it could write one; an explicit valid error JSON was created for every failed query instead.
- Attempted queries: **6**; successful Scholar responses: **0**; documented service failures: **6**; source UI totals available: **0/6**; returned ranked records: **0**; candidate records retained for later merge: **0**.

## Source limitations, risks, and stopping rationale

- Every request ended with the `scholarly` message **`Cannot Fetch from Google Scholar.`** The diagnostics also note a Firefox-manager fallback before the fetch failure. The evidence does not distinguish rate limiting/blocking, a temporary Scholar access failure, or an execution-environment network/browser issue, so all six are conservatively classified as **service failures**.
- No source UI header was reached, so no Scholar total estimate, pagination behavior, snippets, citation counts, proceedings/chapter metadata, or ranked candidate title could be assessed. Nothing was treated as a zero-result search.
- The failure leaves unresolved supplementary recall risk for poorly indexed proceedings/chapters, the CubeSat System Reference Model lineage, EPS traceability/V&V, and digital-engineering terminology. The completed new Scopus and IEEE runs, later full-text screening, and protocol-required citation chasing remain important mitigations. A later, normal-access Scholar rerun can reuse these exact query IDs/strings and the rank cap.
- Stopping this delegated slice is justified because all six planned, distinct concept-gap probes were attempted in the required two batches and every request failed before retrieval. Additional immediate requests would be repetitive access attempts rather than evidence-based query refinement and could exacerbate an unofficial-service block. No CAPTCHA or bot-protection bypass was attempted.
