# Open Access Theses and Dissertations

Final searches saved in commit: 9d5f6428612f6b8cc86462a27f08c563cb58fb8f
Source excluded from review due to search failure in commit: NA
Current final execution: [`corrective-013`](final-searches/corrective-013/), a declared continuation of the 16 complete initial passes in `corrective-009` and ten validated details in `corrective-012`. Its assessment and validation report determine completion.
Earlier failure assessment: [`final-searches/final-failure-assessment.json`](final-searches/final-failure-assessment.json). The [code audit](final-searches/code-audit/) supersedes its claim that the search endpoint is wholly unavailable.

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`
Browser profile: Shared `chrome-automation` profile through loopback CDP port 9222. Final source attempts used this profile exclusively.

Save this continuation's gate evidence in `final-searches/corrective-013/gates/` and its source union as `final-searches/corrective-013/hydrated-union.json`. Keep prior attempts intact. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Full OATD index
- URL: https://oatd.org/oatd/search
- Field: Raw basic `q` over the advertised metadata scope. Preserve the native basic form's `form=basic` parameter with all English and year clauses still inside `q`. Use actual native form submission for every pass. Direct URL navigation returned HTTP 500 for the first gate without this parameter and for the tailoring gate even with it. Native form submission returned 17 and 0 records respectively with exact query readback. The backend cause remains unknown.
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

Apply the same English and year controls to all eight gates. Capture two complete card ID passes per gate and reconcile their stable ID sets. Build the deduplicated union before opening Record Details. Hydrate each unique ID once, then repeat every gate and require equal confirming sets. Preserve gate provenance and visible publication date status. A local negative annotation never removes a source card. One failed detail, gate, or screenshot leaves the complete source union null. Save nonmergeable progress after every pass and a rendered error screenshot on failure. See [Pilot 007](pilots/007/pilot.md) for the earlier result bound.

## Abstracts and publication types

Capture the entire rendered Abstract cell, preserving paragraph boundaries. Activate the native Record Details link with Enter and wait explicitly for the detail navigation. On HTTP 500 or 504, allow one alternate stable-ID lookup with empty `q` after 120 seconds. Both modes require exact Record ID and title checks. A bounded comparison recovered identical MIT metadata with empty `q`. Another record required the native display context. Cached Back uses commit and validated source state. All discovery searches retain the complete planned queries and controls. Retain validated final passes and detail checkpoints across the declared continuation. Reopen exact gate contexts to observe the source IDs, verify equal ID sets, and require all eight confirming passes after hydration. No population-only harvest or additional discovery query is introduced. OATD truncates some abstracts near 3,072 characters, even on Record Details. Flag these as `truncated_in_oatd`. Keep absent abstracts explicit. A nonempty abstract alone does not prove completeness.

Preserve the ETD source scope separately from native Degree, Degree Level, and any Type field. Capture the observed `Discipline/Department` label as well as `Department/Discipline`. Keep native language and issued date metadata. These values do not assign reviewer screening codes.

Retrieve full abstracts from linked institutional repository metadata for truncated or absent OATD abstracts when available. Save this enrichment separately with record IDs, original OATD text, repository provenance, and exact text hashes. It must retain the complete confirmed OATD record set. It adds no discovery records and removes none.
