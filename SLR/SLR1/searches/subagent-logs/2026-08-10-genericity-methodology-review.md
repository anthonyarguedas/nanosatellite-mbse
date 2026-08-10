# Model-assisted bounded-genericity methodology review

- **Date:** 2026-08-10
- **Classification:** protocol-design review; no search, screening, candidate, or evidence activity
- **Reviewer:** Pi subagent using `openai-codex/gpt-5.6-terra`; not a human assessor or information specialist

The subagent read the frozen version-1.2 protocol and query plan under the anti-anchoring restrictions. The text below is its recommendation to the parent agent; the integrated version-1.3 protocol is authoritative where wording differs.

## Proposed v1.3 status

Record v1.3 prospectively, dated before any valid final discovery search, superseding v1.2 and requiring fresh v1.3 authorization. State that eligibility, Route A/B, RQ2, RQ3, sources, and mandatory baseline searches are unchanged.

## 1. Definitions

> **Genericity** is bounded transferability: the extent to which an identified EPS MBSE artifact’s documented core can be adopted or tailored for stated target contexts within a declared applicability envelope. It is not an intrinsic property of a language, tool, paper, or model diagram.

- **Reusable EPS MBSE artifact:** A source-identifiable structured-model asset, or documented package of assets, containing or explicitly bound to a qualifying EPS thread and its modeled relations. Examples include a reference/template model, model library, profile with EPS elements, model pattern, interface contract, or parametric-model bundle. Public availability is not required.
- **Method/workflow:** A reusable modeling process, toolchain, transformation procedure, or guidance. It may be reported under RQ1, but is not artifact genericity unless persistent EPS model content and its lineage are identified.
- **Declared applicability envelope (DAE):** Source-locatable intended target contexts, purpose, boundaries, dependencies, and exclusions for reuse. It may be assembled from explicit statements in several locations, but reviewer inference cannot fill missing dimensions. An observed mission alone is not a DAE.
- **Minimum DAE:** Intended target class/context; intended lifecycle use or decision; EPS/model boundary and abstraction; and at least one material condition, required input/dependency, or exclusion.
- **Demonstrated coverage:** The actual target contexts within the DAE for which reuse/tailoring and assurance are reported. It is a subset of the DAE unless full coverage is directly shown.
- **Tailoring:** A source-described configuration, parameterization, selection, specialization, extension, deletion/substitution, interface mapping, transformation, or explicitly justified unchanged adoption. A parameter sweep within one unchanged mission model is analysis, not cross-context tailoring.
- **Claim versus demonstration:** “Generic,” “reusable,” “template,” etc. are author claims. Demonstrated bounded reuse requires traceable common artifact lineage, materially distinct target contexts within the DAE, documented tailoring or justified as-is adoption, and post-tailoring assurance.
- **Genericity versus reporting quality:** A genericity tier is a non-compensatory evidence classification, not a quality score. Good reporting, venue, openness, or model availability cannot supply a missing envelope, common core, transfer, assurance, or independence condition. Conversely, a high tier does not erase reporting limitations.

No tier establishes universal applicability.

## 2. RQ structure

Keep RQ1–RQ3. Add this nested RQ1 question:

> **RQ1-G — bounded reuse and tailoring.** For each eligible EPS model thread, what, if any, reusable EPS MBSE artifact and artifact lineage is reported; what declared applicability envelope, reusable core, variation points, dependencies, and tailoring pathway does it have; which target-context applications and post-tailoring assurances are reported; and at what non-compensatory evidence tier is bounded reuse supported?

RQ1-G is an RQ1 analytic stratum, not a fourth co-primary question and not an eligibility requirement.

## 3. Genericity profile and tiers

Use an artifact-lineage-level profile; do not sum items.

| Gate | Minimum evidence |
|---|---|
| **A — Artifact/lineage** | Identifiable EPS-relevant artifact and source-locatable lineage across any claimed instances. Same tool, authors, topic, or terminology is insufficient. |
| **E — Envelope** | Minimum DAE, with each component and source location retained. |
| **C — Core and variation design** | Identified retained core plus variation points/tailoring rules and prerequisites; alternatively, an explicit bounded “reuse as-is” rule. |
| **T — Transfer/tailoring** | Actual applications in target-context tuples; retain what changed, what core remained, and why. Two contexts must differ on a material DAE dimension. |
| **P — Post-tailoring assurance** | For each context credited toward demonstration: the tailored configuration is identifiable; an intended-use-relevant criterion/oracle is reported; a post-tailoring check is executed; and a result/verdict is reported. A syntax/build check alone is insufficient. |
| **I — Independence** | A separately mapped implementation/evaluation family, with source-supported separate adoption or evaluation. Companion reports, shared underlying implementations, and unclear relationships do not qualify. |

Code each gate as `demonstrated`, `partial`, `not_reported`, `uncertain`, `none`, or narrowly defined `not_applicable`, with evidence locations. `partial`, `not_reported`, `uncertain`, and inference-only evidence fail a required gate. Explicit unchanged adoption may satisfy tailoring only when its conditions and rationale are reported; it never waives envelope or assurance.

| Tier | Minimum conditions | Interpretation |
|---|---|---|
| `NA` | No identifiable EPS model artifact; method/workflow only | Do not rate artifact genericity; report workflow reuse separately. |
| `G0` | Artifact identified, but no reuse/genericity indication | No evidence reported; not evidence of non-reusability. |
| `G1` | Artifact plus an author claim or traceable but unbounded reuse indication | Claim/indication only; preserve any observed use, but do not call it demonstrated bounded reuse. |
| `G2` | `A ∧ E ∧ C` | Specified prospective bounded reuse design; actual transfer is not yet shown. |
| `G3` | `G2 ∧ T(≥2 distinct contexts) ∧ P` | Demonstrated bounded reuse, potentially within one implementation family. |
| `G4` | `G3 ∧ I` | Independently corroborated bounded reuse. Strongest tier, still limited to the demonstrated subset of the DAE. |

A broader DAE does not earn a higher tier. Tiers describe evidence strength, not envelope breadth or model quality.

For dependence:
- Add a distinct artifact-lineage registry; do not equate it with report family.
- Collapse companion reports and shared implementations to one transfer/assurance occurrence.
- A single report can contribute multiple contexts only where separate instantiated applications are documented.
- If lineage or independence is unclear, do not merge records or award `G3`/`G4`.

Post-tailoring assurance may cross-link to RQ3, but becomes a direct RQ3 record only if the existing EPS target–bridge–V&V rule is met.

## 4. `protocol.md` amendment map

| Section | v1.3 amendment |
|---|---|
| Header, status, amendment record | Set v1.3; state prospective timing, no valid final discovery search, v1.2 superseded, and new authorization required. |
| Review objective | Add bounded artifact reuse: DAE, core/variation, tailoring, observed transfer, assurance, and evidence tier. State no universal applicability conclusion. |
| PICOC RQ1 row | Add artifact identity/lineage, DAE, core, variation, tailoring footprint, demonstrated coverage, assurance, and genericity tier to RQ1 outcomes. |
| Research questions | Retain RQ1–RQ3; insert RQ1-G exactly as above. |
| Operational definitions | Add the definitions above after MBSE qualification. State that genericity status, artifact availability, and tier are not inclusion criteria. |
| Inclusion/screening | No scientific eligibility change. Create RQ1-G profiles only after Route A/B inclusion. A generic whole-spacecraft claim still needs EPS-specific artifact/thread evidence. |
| Units and IDs | Add: (6) reusable EPS artifact lineage; (7) tailoring/application instance. Link both to threads, reports, and report families. Keep PRISMA counts at record/report level. |
| Quality | Preserve items 1–12. Add a separate, non-scored genericity-evidence audit for A/E/C/T/P/I. Do not add its fields to a numerical quality total. |
| Extraction | Add artifact scope/type/version/lineage; claim wording and claim object; DAE dimensions; core/variation points; tailoring-event records; context tuples; retained core; inputs, roles, tooling, effort and trade-offs; assurance criterion/method/result/timing; independence/family evidence; tier and unmet gates. |
| Calibration | Calibrate method-only versus artifact, DAE versus observed case, scenario sweep versus tailoring, same-family duplication, unchanged adoption, assurance versus RQ3 V&V, and `G2/G3/G4` boundaries. Second-check all lineage merges and `G3/G4` assignments. |
| Synthesis | Add RQ1-G evidence maps by lineage, DAE, demonstrated contexts, tailoring operation, assurance, family dependence, and tier. Report claims, specified designs, demonstrated reuse, and independent corroboration separately. |
| Conclusion confidence | Do not map G-tiers mechanically to current higher/moderate/lower confidence labels. Consider tier, reporting quality, directness, dependence, and missingness narratively. |
| Reporting/artifacts | Add a lineage registry, tailoring-instance table, genericity profile appendix, and a claim-to-evidence table. Report all denominators separately: lineages, applications, report families, reports, and threads. |

RQ2 and RQ3 safeguards remain unchanged. Tailoring burdens enter direct RQ2 only under the current explicit EPS-thread attribution rule.

## 5. Discovery/search

No mandatory discovery change is needed. Stream B already avoids an EPS requirement, and its broad structured-model block is the appropriate protection against metadata omission and self-label bias. Making “generic,” “reusable,” or “tailoring” mandatory would reduce recall and privilege author terminology.

A `P AND M AND genericity-term` query is a subset of Stream B and is not a recall expansion. If a supplemental probe is desired, make it append-only:

- `P AND (existing M OR M-G)` with **no EPS requirement**;
- conservative `M-G` concepts: `"reference architecture"`, `"domain model"`, `"model template"`, `"model library"`, `"model pattern"`, `"model profile"`, `"variation point"`, `"product line"`, and model-proximate `reus*`, `tailor*`, `configur*`, `instantiat*`, `speciali[sz]*`, or `adapt*`;
- avoid bare `generic`, `general*`, `framework`, `architecture`, or `profile`;
- log it as a supplementary Stream-B recall probe, preserve source-specific syntax/count testing, and screen normally.

Update `query-search-plan.md` version references and add RQ1-G to the coverage audit, but do not alter the seven-source baseline or eligibility.

## 6. Risks and prohibited wording

Key risks:

- Treating a generic workflow, tool, repository, or SysML profile as a generic EPS model artifact.
- Treating whole-spacecraft reuse as EPS reuse without thread-specific evidence.
- Inferring an envelope from a single mission, omitted details, or reviewer expertise.
- Counting scenarios, revisions, papers, or companion reports as independent reuse cases.
- Treating open availability, peer review, model execution, or flight evidence in one case as proof of transferability.
- Calling a post-tailoring check RQ3 V&V when the existing target–bridge–method rule is unmet.
- Inferring RQ2 benefit, lower effort, reproducibility, or interoperability from a genericity tier.

Do not write:

- “the model is generic” without its artifact scope, DAE, tier, and demonstrated contexts;
- “proven generic,” “universal,” or “applicable to all CubeSats/nanosatellites”;
- “genericity score” or a percentage implying a continuous intrinsic property;
- “no reported tailoring means no tailoring was needed”;
- “two reports demonstrate independent replication”;
- “successful simulation verifies genericity”;
- “genericity produced a benefit” without an eligible RQ2 record.

Use: “`G3` evidence supports bounded reuse of [artifact scope] in [demonstrated contexts], within the stated DAE.”

### Parent-agent summary

Adopt a prospective v1.3 with nested RQ1-G, artifact-lineage and tailoring-instance units, and a non-additive A/E/C/T/P/I profile. Use `NA`, `G0`–`G4` to separate claims, specified reuse designs, within-family demonstrated reuse, and independently corroborated bounded reuse. Keep eligibility and RQ2/RQ3 unchanged; at most add a logged append-only terminology probe.

**Subsequent parent disposition:** later no-screening opaque-ID pilots demonstrated source-specific additions outside fresh core-B sets. The authorized parent protocol therefore converted precise G1/G2, conservative C1, and source-applicable T2 into separately provenance-coded Stream-B recall partitions without changing eligibility or treating their retrieval as genericity evidence. The final protocol/query plan supersede this report's initial “no mandatory discovery change” recommendation.
