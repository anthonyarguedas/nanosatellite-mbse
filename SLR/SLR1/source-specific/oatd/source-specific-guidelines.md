# Open Access Theses and Dissertations

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`

Save gate evidence in `final-searches/gates/` and the hydrated source union as `final-searches/hydrated-union.json`. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Full OATD index
- URL: https://oatd.org/oatd/search
- Field: Raw basic `q` over the advertised metadata scope
- Evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen cutoff year records against the exact common cutoff.
- Language: Apply the native `English` value `(en OR eng OR english)` and require exact route readback. Confirm report language during screening.
- Publication type: OATD is ETD scoped. Apply no degree, level, completion, peer review, access, availability, or full text filter.
- Collection: Apply no country, university, license, or Creative Commons restriction.

## Accepted source gates

Use this exact union:

```text
(P AND M_H)
OR (P AND M_B AND E_F)
OR (P AND M_B AND E_H)
OR (P AND M_B AND R)
OR (P AND M_B AND T_precise)
OR (P AND G_model)
OR (P AND G_structure)
OR (P AND C1)
```

It is algebraically equal to the nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule). Do not use a broad population only detail route.

## Translation decisions

- Literal `L(s)`: One straight double quoted literal.
- Boolean: Use uppercase `AND` and `OR` with full parentheses.
- Controlled vocabulary decision: Add no supplement. OATD exposes no named controlled vocabulary, descriptor mapping, hierarchy, or expansion control.
- Wildcard decision: Use no wildcard. The source has no complete no loss wildcard comparison for this route, and the exact eight gate workload is already bounded.

## Execution

Apply the same English and year controls to all eight gates. Capture two complete card ID passes per gate and reconcile their stable ID sets. Build the deduplicated union before opening Record Details. Hydrate each unique ID once, then repeat every gate and require equal confirming sets. Preserve gate provenance and visible publication date status. A local negative annotation never removes a source card. One failed detail, gate, or screenshot leaves the complete source union null. See [the readiness audit](../readiness-audit.md) for the result bound.
