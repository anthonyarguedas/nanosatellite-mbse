# NASA Technical Reports Server

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ntrs.py`

Save final JSON files in `final-searches/` by query ID. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: NASA Technical Reports Server
- URL: https://ntrs.nasa.gov/search
- Field: General `q` over metadata and indexed document text
- Evidence window: Use exact `--date-start 2011-01-01 --date-end <cutoff>` bounds.
- Language: Apply no source filter. Confirm English during screening.
- Publication type: Apply no type, peer review, access, distribution, collection, subject, keyword, or full text filter. The Type vocabulary and missing assignments do not prove a lossless eligible union.
- Collection: Full public NTRS database.

## Source translation

Use the concepts, compounds, and nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule). Use `+` for `AND`, `|` for `OR`, and full parentheses. Use no proximity or pair expansion.

- Literal `L(s)`: One straight double quoted token or ordered phrase.
- Controlled vocabulary decision: Add no supplement. Subject Category and Keyword values are exact strings, but the route exposes no proved NASA Thesaurus descriptor, hierarchy, or expansion contract.
- Wildcard decision: Use only the validated standalone families below. Complete literal and wildcard canonical ID sets were equal in all nine partitions. A broader phrase and acronym compression lost literal records.

Accepted wildcard families:

- Population: `CubeSat*`, `nanosat*`, and `SmallSat*` for their declared families.
- Relationship block: `requirement*`, `function*`, `behavior*`, `behaviour*`, `architectur*`, `interface*`, `trace*`, `allocat*`, `constraint*`, `parametric*`, `analys*`, `design*`, `decision*`, `tradeoff*`, `verif*`, and `validat*` for matching declared forms.
- Structure block: `metamodel*` for `metamodel` and `metamodels`.
- Tailoring block: `tailor*`, `customiz*`, `customis*`, `parameteriz*`, `parameteris*`, and `instantiat*` for their declared forms.

Keep phrases, acronyms, punctuation variants, and every other term literal. `--skip-full-abstracts` and `--no-full-abstracts` are for pilots and diagnostics only. Final and corrective searches must pass `--full-abstracts` because list-only metadata is the adapter default. Final events require stable pre-submit and post-submit states plus two complete matching passes. See [the readiness audit](../readiness-audit.md) for the result bound.
