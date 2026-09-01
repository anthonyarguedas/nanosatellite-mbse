# Open Access Theses and Dissertations

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`

Save the final shared population artifact in `final-searches/` as `P-shared.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Open Access Theses and Dissertations (OATD)
- Interface: Web
- Platform: OATD
- URL: https://oatd.org/oatd/search
- Search field or local route: Raw basic `q` across the source-advertised metadata scope.
- Main evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. The adapter expands years to calendar bounds. Screen the cutoff year against the exact cutoff if needed.
- Language: A dated technical healthy-route check confirmed the native English metadata option `English` with source value `(en OR eng OR english)`. Apply it only when that event has an exact source-rendered route/query readback. Otherwise leave the event unrun or failed rather than assuming the control applied. This metadata restriction does not prove report language. Full-text screening remains authoritative.
- Publication type: OATD is ETD-scoped, but apply no degree, level, completion, peer-review, availability, access, or full-text filter. Metadata can include incomplete, undergraduate, or abstract-only work. Resolve those statuses during screening.
- Database or collection selection: Full OATD index with no country, university, degree, level, or Creative Commons restriction.
- Other shared limits: None.

## Selected final route

This route is a no-loss protocol amendment. Every main partition contains `P`. Under the same English and year controls, each partition ID set is a subset of the `P` ID set. The final source candidate union is therefore the complete stable-ID set returned by one bounded `P` search. It is not a source-reported union of the nine partitions.

Submit this exact 26-literal `P` query as raw `q`:

```text
("CubeSat" OR "CubeSats" OR "cube sat" OR "cube sats" OR "cube-sat" OR "cube-sats" OR "cube satellite" OR "cube satellites" OR "nanosat" OR "nanosats" OR "nanosatellite" OR "nanosatellites" OR "nano-sat" OR "nano-sats" OR "nano sat" OR "nano sats" OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites" OR "SmallSat" OR "SmallSats" OR "small satellite" OR "small satellites" OR "small sat" OR "small sats")
```

Apply `English` with source value `(en OR eng OR english)`. Apply `--year-start 2011 --year-end <cutoff-year>`. Require an exact rendered query echo for that event. The exact cutoff day remains a screening and local date-accounting check for records in the cutoff year.

Run `search_oatd.py --shared-population-harvest` with an `oatd-local-matching-plan/v1` plan and a checkpoint path. The plan supplies each named expression, its SHA-256, and a plan SHA-256. Set `--limit` and `--max-pages` high enough to cover the observed source total and selected native page size. The adapter uses two complete source-rendered `P` card-ID passes. It hydrates each unique Record Details page once through a separate owned detail page. It saves only path-free normalized public metadata, completed IDs, controls, and ID digests in the checkpoint. A resumed run validates every completed normalized detail record before it can skip retrieval and obtains fresh complete ID snapshots before publication.

The visible Record Details Publication Date is retained as `publicationDateReadback` evidence. For a run with a year control, its status is `within_bounds`, `absent_unresolved`, or `visible_date_conflicts_with_source_filter`. It never removes or blocks a returned `P` card. The exact rendered source query echo and its `pub_dt` clause separately prove the source controls.

Retain every `P` ID and every hydrated `P` record. Apply the nine schedule expressions below only as local annotations and screening priorities. Local matches, visible-field nonmatches, and missing-field states remain auditable. A local negative never removes a `P` record until source-analyzer equivalence and complete field visibility are proved. Local match counts are not native OATD partition totals and are not exact original partition unions.

The adapter normalizes visible local fields with Unicode NFKC, case folding, and lexical boundaries. It supports the documented Boolean, quoted phrase, field, and two-order `~5` forms. This approximation does not prove OATD analyzer, slop, direction, default-field, or discipline coverage equivalence.

A fresh count observation on 2026-08-30 reported 1,249 records for this controlled `P` route. That was a dated feasibility observation. It is not a permanent source count.

## Local schedule annotation translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). The local plan retains every listed literal, named field, pair order, and Boolean relation. It uses no wildcard or unrequested variant expansion.

- Literal `L(s)`: Use one straight double-quoted literal.
- Boolean: Use uppercase `AND`, `OR`, and `NOT` with explicit parentheses.
- Block `F(S)`: join every ordinary member with OR and fully parenthesize the block.
- Pair `PAIR(a,b)`: retain both `field:("a b"~5)` and `field:("b a"~5)` for `title`, `author`, `abstract`, `publisher`, `subject`, and `discipline`.
- Paired blocks: retain every fixed phrase and every declared `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement. Free text remains mandatory.

## Local schedule annotations

The table identifies local plan expressions. It no longer defines nine final source submissions.

| ID | Source construction |
|---|---|
| `A1` | `F(P) AND F(E_H) AND F(M_H)` |
| `A2` | `F(P) AND F(E_F) AND (F(M_H) OR F(M_B))` |
| `A3` | `F(P) AND F(E_H) AND F(M_B)` |
| `B1` | `F(P) AND F(M_H)` |
| `B2` | `F(P) AND F(M_B) AND F(R)` |
| `BG1` | `F(P) AND F(G_model)` |
| `BG2` | `F(P) AND F(G_structure)` |
| `BC1` | `F(P) AND F(C1)` |
| `BT2` | `F(P) AND F(M_B) AND F(T2)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): `A1` count-only succeeded with total `1`. `BG1` was a complete named-field translation, but OATD did not become ready within the bounded request. Do not treat it as zero or syntax success, and do not use the artifact as a final search.
- [x] [Pilot 002](pilots/002/pilot.md): the unchanged one-page `BG1` retry again failed readiness with no total. The stop rule left English `A1` and wildcard checks unrun.
- [Pilot 003](pilots/003/pilot.md): the canonical shared browser completed a healthy route and exact English readback, then attempted the first lossless cell in every partition under a 20-invocation round-robin budget. Six cells completed strict capture and three had explicit source failures. All incomplete partition totals and unions remain null. The 2,029-cell plan is retired for final use. Retain it only as diagnostic evidence for Pilot 003. This is not a final search.
