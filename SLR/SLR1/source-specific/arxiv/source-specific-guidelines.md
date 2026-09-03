# arXiv

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_arxiv.py`

Save final JSON files in `final-searches/` by query ID and source cell. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Full multidisciplinary arXiv repository
- URL: https://arxiv.org/search/advanced
- Field: All fields in repeatable Advanced Search rows
- Evidence window: Use inclusive 2011-01-01 through the common cutoff and select original submission date. The adapter converts the upper bound to arXiv's next day exclusive endpoint.
- Ordering: Submission date, oldest first
- Versions: Exclude older versions from discovery results. Retain the bare ID and any shown version suffix.
- Language: Apply no source filter. Confirm English during screening.
- Publication type: Apply no additional type, peer review, access, or full text filter.
- Classification: Search all categories and include cross listed records.

## Source translation

Use the concepts, compound definitions, and nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule).

- Literal `L(s)`: Preserve spelling, punctuation, and spacing inside straight double quotes.
- Ordinary block `F(S)`: Join every literal with uppercase `OR` in one All fields row. Do not type parentheses in the row.
- Conjunction: Put each factor in a separate row and select outer `AND`.
- Controlled vocabulary decision: Add no category term. The arXiv category taxonomy is a classification hierarchy, not a discovery thesaurus, and no complete concept mapping has been validated.
- Wildcard decision: Use no wildcard. The tested wildcard had only a zero count comparison, and source behavior depends on field analyzers. It has no stable ID no loss proof.

## Execution

Run `A1`, `A3`, `B1`, `B2`, `BC1`, and `BT2` as one cell each. Split `A2` into its unchanged `M_H` and `M_B` branches. Split `BG1` and `BG2` by their declared compound branches. This gives 12 cells. Capture complete rendered records through native More controls. Exhaust every cell twice and require equal totals and ordered bare ID ledgers. A failure retains `total: null`. See [the readiness audit](../readiness-audit.md) for the result bound.
