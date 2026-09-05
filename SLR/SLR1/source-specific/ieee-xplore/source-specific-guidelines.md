# IEEE Xplore

Final searches saved in commit: 8ace92319f64ac5dbc92a4775c94ffefc39486cd
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py`

Save final JSON files in `final-searches/` by query ID. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: IEEE Xplore Documents
- URL: https://ieeexplore.ieee.org/search/advanced
- Field: Individually fielded All Metadata atoms
- Evidence window: Use `--publication-date-start 2011-01-01 --publication-date-end <cutoff>`. The adapter applies the native year envelope and reconciles exact visible publication dates.
- Language: Apply no source filter. No reliable language field or facet is available. Confirm English during screening.
- Publication type: Apply no type, peer review, access, or full text filter. The content taxonomy does not prove complete assignment to a lossless eligible union.
- Scope and ordering: Documents, All Results, blank Search Within, and Oldest.

## Source translation

Use the concepts, compounds, and nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule).

- Literal `L(s)`: One straight double quoted literal.
- Atom `A(s)`: `("All Metadata":L(s))`.
- Ordinary block `F(S)`: Join every atom with uppercase `OR` and full parentheses.
- Compounds: Expand every nested `AND` and `OR` before submission. Do not use a grouped field wrapper.
- Controlled vocabulary decision: Add no supplement. IEEE exposes several indexed vocabularies, but this review has no complete concept mapping, assignment proof, or marginal recall comparison for them. Free text remains mandatory.
- Wildcard decision: Use no wildcard. IEEE permits only ten wildcards per search. The candidate would consume the full allowance and has no complete stable ID no loss comparison. The complete literal route is accepted.

## Execution

`--skip-full-abstracts` and `--no-full-abstracts` are for pilots and diagnostics only. Do not use them for final or corrective searches. On each rendered document page, activate a visible **Show More** abstract control before capture. Record `abstract_full_text_status` and fail if the collapsed 2,003 character preview remains. Record the visible result card publication type in `documentType`.

Run one expression per partition. Keep each request within the validated 7,800 byte target envelope. Use compact space encoding and safe parentheses only when percent component encoding would exceed that envelope. Preserve the decoded parameter sequence. Use 20 second page and detail delays for final runs. This cadence keeps rendered document requests within the source observed challenge free window, including page and pass transitions.

Before changing a Year widget, accept a disabled interval only when its complete available range lies inside the requested window. Record the requested range and contained source interval separately. Any real narrowing, ambiguous widget, or changed token fails with `total: null`.

Use the active native page size when it can exhaust the event within `--max-pages`. Final events require two complete passes with equal totals, controls, and stable ID sets. Order differences are audit evidence and do not replace set equality. See [the readiness audit](../readiness-audit.md) for the result bound.
