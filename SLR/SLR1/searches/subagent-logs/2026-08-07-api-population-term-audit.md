# API population-term audit — IEEE Xplore, NTRS, and Scopus transport

**Status:** complete; `pilot_not_candidate_search` only. No record was screened, retained as a candidate, or used as evidence.

- **Run date:** 2026-08-07, EDT (UTC−04:00)
- **Raw pilot archive:** `.searches/eps-mbse-slr-2026/term-variant-pilots/2026-08-07/`
- **Archive manifest:** 85 files; SHA-256 `12b249a440bda72b4ba2a74b82e90ff3e74f23aeb9aea63a8e3dd4f37e9a8f68`
- **Purpose:** test population-spelling coverage before freezing source-native queries, not identify the evidence corpus.

## IEEE Xplore

The IEEE JSON search interface was tested with years 2011–2026, content types Journals/Conferences/Books, English, and `--count-only`. The revised population block was:

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite")
```

| Pilot | Current count | Revised count | Observation |
|---|---:|---:|---|
| I-B1 | 38 | 38 | Revised block accepted; no count change |
| I-V1 | prior pilot 1 | 1 | Revised block accepted |
| I-O1 | prior pilot 4 | 4 | Revised block accepted |

Counts are interface diagnostics only. Equal totals do not prove equal sets. The accepted revised block should be used consistently in all six final IEEE expressions.

## NASA NTRS

The public citations API was queried with `published.gte=2011-01-01`, `published.lte=2026-08-07`, `page.size=100`, and no Boolean operators. A finite diagnostic matrix tested eight population spellings against all seven planned `M_N` terms (56 B-stream cells). All responses were HTTP 200 and were exhausted within one page.

| Population term | Sum across seven cells | Unique NTRS IDs across cells | Decision |
|---|---:|---:|---|
| `CubeSat` | 11 | 5 | Retain |
| `CubeSats` | 2 | 1 | **Add: one source-unique record was not retrieved by the existing population terms** |
| `"cube sat"` | 0 | 0 | Do not add to the mandatory NTRS matrix at this time |
| `nanosatellite` | 4 | 1 | Retain |
| `nanosatellites` | 0 | 0 | Do not add at this time |
| `"nano-satellite"` | 0 | 0 | Retain as a prespecified source term despite the current zero yield |
| `"nano-satellites"` | 0 | 0 | Do not add at this time |
| `"nano satellite"` | 0 | 0 | Do not add at this time |

The zero-yield omitted spellings are dated source observations, not semantic claims of equivalence. They remain represented in the Boolean bibliographic sources and may be retested if NTRS changes or a recall miss triggers a probe. Adding `CubeSats` changes `P_N` from three to four terms: N-B becomes 28 cells (`4×7`), N-A becomes 108 cells (`4×9×3`), and the mandatory NTRS baseline becomes **136 cells** rather than 102.

## Scopus API initial failure and institutional-network retry

Two initial Scopus Search API attempts—current and revised S-B1 population blocks—both returned an invalid-API-key response at approximately 01:14:58 EDT. The client nevertheless wrote empty JSON shells with `total: 0`; those totals are invalid and must not be logged as source results. The failure is preserved in `scopus/auth-failure.json`.

After institutional network access became available, the same `COMPLETE`-view client successfully reran both queries at approximately 09:44 EDT. The original S-B1 returned **75** and the revised S-B1 returned **80**, each with one requested diagnostic record and one page reconciled. These API totals match the independent normal-web-UI syntax comparison documented in [`2026-08-07-population-term-audit.md`](2026-08-07-population-term-audit.md). The revised population block therefore has both source-native API and web-UI acceptance, with +5 dynamic results in the matched comparison. All attempts remain pilots; final execution still requires a fresh authentication/count/retrieval preflight after authorization.

## Resulting source-specific decision

Use all accepted frozen population spellings in Scopus, Web of Science, IEEE Xplore, Compendex, and Wiley. ESA matching continues to use the complete frozen dictionary. NTRS uses the source-tested finite set:

```text
P_N = {CubeSat, CubeSats, nanosatellite, "nano-satellite"}
```

Every accepted final strategy must still be rerun after authorization. The successful institutional-network retry resolves the pilot authentication blocker, but no pilot count can be reused as a final Scopus result.
