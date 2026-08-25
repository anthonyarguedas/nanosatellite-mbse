# Scopus candidate-terminology test observations — completion

- **Pilot:** `S-D01-P14-20260823T150131-0400`, continuing the frozen P13 test without rerunning a successful source execution.
- **Status:** Scopus portion complete; global `S-C01` remains pending Web of Science, IEEE Xplore, and Compendex/Inspec.
- **Boundary:** diagnostic term-use audit only; no review screening, candidate import, final event, or normative query change.
- **Window:** 2026-08-23T15:03:14-04:00 to 2026-08-23T15:08:59-04:00 for live work; offline reconciliation followed.

## Counts and unique audit

Q00's current `B1 OR B2` union had **155** complete stable identities. Values below are **source total / identities unique to Q00**. Term-use codes are **qualifying / ambiguous / nonqualifying** among audited unique records.

| Family | Candidate | Primary | With R | Audit codes |
|---|---|---:|---:|---:|
| F01 | model-based engineering | 3 / 2 | 3 / 2 | 0 / 1 / 1 |
| F02 | model-driven engineering | 5 / 5 | 5 / 5 | 1 / 0 / 4 |
| F03 | model-based design | 8 / 6 | 8 / 6 | 0 / 1 / 5 |
| F04 | model-driven design | 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| F05 | MBE acronym | 2 / 2 | 0 / 0 | 0 / 0 / 2 |
| F06 | MDE acronym | 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| F07 | MBD acronym | 4 / 4 | 4 / 4 | 0 / 0 / 4 |
| F08 | digital thread | 3 / 1 | 3 / 1 | 0 / 0 / 1 |
| F09 | digital twin | 46 / 35 | 40 / 29 | 6 / 4 / 25 |
| F10 | MagicGrid method | 0 / 0 | — | 0 / 0 / 0 |
| F11 | Harmony-SE method | 0 / 0 | — | 0 / 0 / 0 |
| F12 | RFLP acronym | 1 / 0 | 1 / 0 | 0 / 0 / 0 |
| F13 | expanded requirements-functional-logical-physical wording | 0 / 0 | — | 0 / 0 / 0 |
| F14 | Cameo Systems Modeler | 1 / 0 | — | 0 / 0 / 0 |
| F15 | MagicDraw | 1 / 0 | — | 0 / 0 / 0 |
| F16 | full Rhapsody names | 0 / 0 | — | 0 / 0 / 0 |
| F17 | Vitech CORE | 0 / 0 | — | 0 / 0 / 0 |
| F18 | Vitech GENESYS | 0 / 0 | — | 0 / 0 / 0 |
| F19 | OpenMBEE | 0 / 0 | — | 0 / 0 / 0 |
| F20 | Enterprise Architect | 1 / 0 | 1 / 0 | 0 / 0 / 0 |
| F21 | System Composer | 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| F22 | Modelio | 0 / 0 | — | 0 / 0 / 0 |
| F23 | Cameo short form | 2 / 0 | 2 / 0 | 0 / 0 / 0 |
| F24 | Rhapsody short form | 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| F25 | CORE short form | 307 / 298 | 273 / 264 | 0 / 0 / 50 |
| F26 | GENESYS short form | 1 / 1 | 1 / 1 | 0 / 0 / 1 |

Every unique set of 50 or fewer was audited in full. `CORE` had 307 total and 298 unique; the frozen Python `random.Random(7192584218202250015)` frame selected 50 without replacement. All six known and five contrast records were also inspected through the frozen field checks and recovery ledger, whether they overlapped Q00 or a candidate-unique set. The full `Vitech CORE` query was zero. All 50 sampled short-form uses were ordinary words, components/processors/materials, Core Flight System references, or unrelated products.

## Candidate rendering behavior

All prescribed hyphenated and spaced phrase forms were retained explicitly as Scopus loose phrases; no candidate was wildcard-compressed or silently stemmed away. This uses the already approved Scopus punctuation/lemmatization evidence while keeping each cross-source spelling visible in the exact query files. Acronyms, one-token products, and short forms used exact braces. In the bounded contrast check, exact `{CORE}` did not retrieve the hyphen-bound `multi-core` occurrence, while the live short-form query still returned 307 semantically ambiguous standalone uses. Exact token rendering therefore controlled substring/punctuation expansion but did not solve ordinary-word, unrelated-acronym, or wrong-product ambiguity. Full names remained separate from short forms throughout.

## Scopus-stage disposition

- **Carry forward, still non-normative:** `model-driven engineering` / `model driven engineering`, and `digital twin` / `digital twins`. Each recovered at least one qualifying structured-system-model context missed by Q00. Both are broad; if the later cross-source decision accepts them, the Scopus evidence supports placement only in `M_B` with independent `R`, not `M_H`.
- **No Scopus support for addition:** every other prespecified candidate. Important mechanisms were MBE as *mean bias error*, MBD as *Multi Mission Bus Demonstrator*, GENESYS as Keysight RF software, CORE as an ordinary word/product, component/control/software models, stand-alone simulations, supply-chain digital threads, and proceedings/container aggregation.
- All six eligible known reports were already recovered by Q00. RFLP, Cameo Systems Modeler, MagicDraw, Enterprise Architect, and Cameo therefore added no known-item recall in Scopus.

The identifier-level codes and reasons are in [`candidate-term-use-audit.json`](candidate-term-use-audit.json); exact counts and hashes are in [`candidate-family-results.json`](candidate-family-results.json). Licensed abstracts remain only in the ignored restricted directory. The protocol and dictionary remain unchanged because a Scopus-only carry-forward result cannot pre-empt the required cross-source decision.
