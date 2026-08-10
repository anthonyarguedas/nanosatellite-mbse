# Opaque-ID search-refinement pilot report

**Classification:** `pilot_not_candidate_search`
**Scope:** Scopus and IEEE Xplore only; 2011–2026 plus a mechanical exact-current-day cutoff; English; no publication/content-type filter.
**Assessment:** model-assisted; no human information specialist; no relevance screening. Opaque IDs are retrieval-control tokens only and are never candidates or evidence.

## Query execution

`source total / retrieved pass 1,pass 2` is shown below. A failure is not a zero-result search. Exact source-native queries follow the table.

| Query | Source | Role | Source total / retrieved p1,p2 | Status |
|---|---|---|---:|---|
| `S-G1R0` | Scopus | precise_artifact_cluster_without_legacy_relation_block | failure | `failure` |
| `S-G2R0` | Scopus | structural_artifact_cluster_without_legacy_relation_block | failure | `failure` |
| `S-A1R0` | Scopus | central_asset_cluster_without_legacy_relation_block | failure | `failure` |
| `S-T2R0` | Scopus | candidate_generating_tailoring_relation_expansion_without_old_B2_relation_block | failure | `failure` |
| `S-X1` | Scopus | prospective_combined_expanded_B2 | failure | `failure` |
| `I-G1R0` | IEEE Xplore | precise_artifact_cluster_without_legacy_relation_block | 0 / 0,0 | `success` |
| `I-G2R0` | IEEE Xplore | structural_artifact_cluster_without_legacy_relation_block | 7 / 7,7 | `success` |
| `I-A1R0` | IEEE Xplore | central_asset_cluster_without_legacy_relation_block | 22 / 22,22 | `success` |
| `I-T2R0` | IEEE Xplore | candidate_generating_tailoring_relation_expansion_without_old_B2_relation_block | 22 / 22,22 | `success` |
| `I-X1` | IEEE Xplore | prospective_combined_expanded_B2 | 59 / 59,59 | `success` |

## Exact source-native strings

### `S-G1R0` — Scopus

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture") AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

P AND G1 precise artifacts. No old B2 relation block is present.

### `S-G2R0` — Scopus

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture))) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

P AND G2 structural artifacts. No old B2 relation block is present.

### `S-A1R0` — Scopus

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model"))) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

P AND conservative central-asset phrases. Ambiguous library/pattern/profile/language concepts are never bare.

### `S-T2R0` — Scopus

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY(((reuse OR reused OR reusable OR reusing OR tailor* OR customiz* OR customis* OR configur* OR parameteriz* OR parameteris* OR instantiat* OR variability OR "variation point" OR specializ* OR specialis*) AND (model OR models OR architecture OR architectures)) OR (adapt* AND (model OR models OR architecture OR architectures))) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

P AND old B2 structured-model block AND model/architecture-coupled tailoring block; no old B2 relation block.

### `S-X1` — Scopus

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY(("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") OR ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture") OR ("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))) AND TITLE-ABS-KEY((requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) OR (((reuse OR reused OR reusable OR reusing OR tailor* OR customiz* OR customis* OR configur* OR parameteriz* OR parameteris* OR instantiat* OR variability OR "variation point" OR specializ* OR specialis*) AND (model OR models OR architecture OR architectures)) OR (adapt* AND (model OR models OR architecture OR architectures)))) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

P AND (old B2 M OR G1/G2 precise M-G artifacts) AND (old B2 R OR tailoring R). A1 is intentionally outside this M-G combined form.

### `I-G1R0` — IEEE Xplore

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture")
```

P AND G1 precise artifacts. No old B2 relation block is present.

### `I-G2R0` — IEEE Xplore

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))
```

P AND G2 structural artifacts. No old B2 relation block is present.

### `I-A1R0` — IEEE Xplore

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model")))
```

P AND conservative central-asset phrases. Ambiguous library/pattern/profile/language concepts are never bare.

### `I-T2R0` — IEEE Xplore

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (((reuse OR reused OR reusable OR reusing OR tailor OR tailored OR tailoring OR customize OR customized OR customizing OR customization OR customise OR customised OR customising OR customisation OR configure OR configured OR configuring OR configuration OR parameterize OR parameterized OR parameterizing OR parameterization OR parameterise OR parameterised OR parameterising OR parameterisation OR instantiate OR instantiated OR instantiating OR instantiation OR variability OR "variation point" OR specialize OR specialized OR specializing OR specialization OR specialise OR specialised OR specialising OR specialisation) AND (model OR models OR architecture OR architectures)) OR ((adapt OR adapted OR adapting OR adaptation) AND (model OR models OR architecture OR architectures)))
```

P AND old B2 structured-model block AND model/architecture-coupled tailoring block; no old B2 relation block.

### `I-X1` — IEEE Xplore

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND (("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") OR ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture") OR ("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))) AND ((requirement OR requirements OR function OR functions OR behavior OR behaviors OR behaviour OR behaviours OR architecture OR architectures OR interface OR interfaces OR traceability OR parametric OR parametrics OR verification OR validation) OR (((reuse OR reused OR reusable OR reusing OR tailor OR tailored OR tailoring OR customize OR customized OR customizing OR customization OR customise OR customised OR customising OR customisation OR configure OR configured OR configuring OR configuration OR parameterize OR parameterized OR parameterizing OR parameterization OR parameterise OR parameterised OR parameterising OR parameterisation OR instantiate OR instantiated OR instantiating OR instantiation OR variability OR "variation point" OR specialize OR specialized OR specializing OR specialization OR specialise OR specialised OR specialising OR specialisation) AND (model OR models OR architecture OR architectures)) OR ((adapt OR adapted OR adapting OR adaptation) AND (model OR models OR architecture OR architectures))))
```

P AND (old B2 M OR G1/G2 precise M-G artifacts) AND (old B2 R OR tailoring R). A1 is intentionally outside this M-G combined form.

## Reconciliation and opaque-ID comparison

### Scopus

No successful refinement snapshot was available for comparison; retained failure artifacts document why.

### IEEE Xplore

| Query | Raw retrieved | Raw overlap prior B1∪B2 | Raw G-only | Current-day on/before | Current-day G-only | Unresolved date | After cutoff |
|---|---:|---:|---:|---:|---:|---:|---:|
| `I-G1R0` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `I-G2R0` | 7 | 1 | 6 | 6 | 6 | 1 | 0 |
| `I-A1R0` | 22 | 16 | 6 | 21 | 6 | 1 | 0 |
| `I-T2R0` | 22 | 16 | 6 | 19 | 6 | 3 | 0 |
| `I-X1` | 59 | 47 | 12 | 56 | 12 | 3 | 0 |

Pairwise raw-ID overlap among successful refinements:

| First | Second | Intersection | First-only | Second-only | Jaccard |
|---|---|---:|---:|---:|---:|
| `I-G1R0` | `I-G2R0` | 0 | 0 | 7 | 0.000 |
| `I-G1R0` | `I-A1R0` | 0 | 0 | 22 | 0.000 |
| `I-G1R0` | `I-T2R0` | 0 | 0 | 22 | 0.000 |
| `I-G1R0` | `I-X1` | 0 | 0 | 59 | 0.000 |
| `I-G2R0` | `I-A1R0` | 1 | 6 | 21 | 0.036 |
| `I-G2R0` | `I-T2R0` | 1 | 6 | 21 | 0.036 |
| `I-G2R0` | `I-X1` | 7 | 0 | 52 | 0.119 |
| `I-A1R0` | `I-T2R0` | 7 | 15 | 15 | 0.189 |
| `I-A1R0` | `I-X1` | 17 | 5 | 42 | 0.266 |
| `I-T2R0` | `I-X1` | 22 | 0 | 37 | 0.373 |

X1 versus the requested partition union (prior B2 ∪ G1 ∪ G2 ∪ T2; A1 excluded): X1=59; partition union=59; X1 outside union=0; subset=True.

## Query-design interpretation

- `G1R0`, `G2R0`, and `A1R0` intentionally omit the old B2 relation block. They test precise artifact wording without allowing a generic relation word to gate retrieval.
- `T2R0` is the candidate-generating tailoring expansion requested here: it retains old B2's structured-model block but replaces the old B2 relation requirement with a model/architecture-coupled tailoring block. `adapt*`/adaptation is confined to that coupled branch. IEEE uses finite explicit forms rather than wildcard assumptions.
- `X1` is a prospective relation-gated expanded-B2 form, not a replacement for the relation-free artifact probes. It deliberately uses G1/G2 (not A1) in the requested `M-G` branch so its set can be tested against prior B2 ∪ G1 ∪ G2 ∪ T2.
- A tautology risk remains wherever an old B2 relation term such as `architecture`/`architectur*` is paired with `reference architecture`: the same phrase can satisfy both sides of a Boolean conjunction. The relation-free precise G2 probe is therefore more defensible for artifact recall. For a future relation-dependent strategy, split the clauses and exclude the self-satisfying relation term for the affected artifact branch (or use proximity/field evidence only if source syntax has been validated), rather than treating co-occurrence as an explicit model relation.
- These counts and overlaps are source-ID retrieval diagnostics only. No title, abstract, result record, relevance, eligibility, report identity, or evidence was inspected or inferred.

## Successful Scopus follow-up and final search-design disposition

A separate configured-runtime follow-up subsequently completed all five Scopus refinements with the same no-screening, no-type, two-pass, exact-day controls. The failed attempts above remain failures rather than being overwritten.

| Scopus query | Total / pass 1, pass 2 | Opaque IDs outside fresh 126-ID B1∪B2 |
|---|---:|---:|
| relation-free G1 | 5 / 5,5 | 4 |
| relation-free G2 | 8 / 8,8 | 6 |
| C1 central assets | 24 / 24,24 | 7 |
| T2 model-coupled tailoring | 26 / 26,26 | 2 |
| rejected combined X1 | 81 / 81,81 | 11 |

No Scopus result was removed or unresolved at the 2026-08-10 cutoff. X1 did not equal its requested component union (X1 81 versus union 82; one G1 opaque ID was absent), so it is not a replacement. A separate architecture-safe split `P AND ((G_M AND R_ALL) OR (G_A AND R_NO_ARCH))` also completed at 12/12 in two passes with 9 additions, proving the corrected syntax works; relation-free G1/G2 remain the preferred final recall partitions because they do not require metadata R wording.

The parent protocol therefore retains relation-free G1/G2, C1, and T2 as separately provenance-coded Scopus/IEEE Stream-B expansions. Retrieval is not a relevance, eligibility, artifact, tailoring, or genericity finding. Exact authoritative final strings are in `query-search-plan.md`; the exploratory X1 and unsplit G×R forms are superseded.

## Preservation

At the version-1.3 freeze, the non-secret request template SHA-256 is `ea14abd3f3cfc6ff523a0d7297eeadd6625f7ea9a9e42ac003cd3bf12cc2120b` and the reconciler SHA-256 is `31ec4e6198d9aac027cfecd68357bf791e64b96fdcdc59f4fe852c4084c4b016`.

Each successful query has two complete ordered-ID passes, page-level request descriptors, raw-response checksums without raw response persistence, reconciliation JSON, and a run manifest. Failures are retained under their query-run paths (the accepted retry is `retry-02/runs/<query-id>/failure.json`). `aggregate.json` preserves opaque-ID overlap sets; `manifest.json` and `checksums.sha256` provide top-level integrity information.

## Execution-attempt note

The initial local opaque-ID adapter attempt is retained under `attempt-01-failed/` and `runs/`. It failed before IEEE payload parsing because of a narrow bytes-case guard defect; it was repaired without changing any query or reconciliation rule. `retry-02/` is the accepted execution for this pilot. Scopus remained unavailable because the required secure `SCOPUS_API_KEY` was absent; all five Scopus query failures are retained and are not zeros. No failed or partial snapshot was merged or screened.
