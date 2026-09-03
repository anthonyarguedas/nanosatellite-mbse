# Source name

PSR final searches saved in commit: NA
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_<source>.py`

Save primary searches and any forward citation searches in `final-searches/`. Save PSR searches in `psr-searches/` only for Scopus and Web of Science. Name each artifact with its query ID or citation seed report ID.

Every CLI event must save `<name>.search-page.png` and `<name>.results-page.png` beside its JSON. The adapter must provide no screenshot opt-out. A missing screenshot must fail the event. The JSON and screenshots are authoritative for event details.

## Fixed source configuration

- Source or collection:
- Interface: Web
- Platform:
- URL:
- Search field or route:
- Main evidence window: 2011-01-01 through the common cutoff.
- Language:
- Publication type:
- Database or collection selection:
- Other limits:

## Source translation

Use the concept membership, compound definitions, and nine direct partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#search-streams-and-set-construction).

- Literal `L(s)`:
- Atom `A(s)`:
- Boolean:
- Ordinary block `F(S)`:
- Controlled vocabulary decision: State whether to use a supplement and why.
- Wildcard decision: State the exact accepted scope or state that wildcards are excluded, and explain why.
- Source limitation:

## Execution

Treat any option that skips or hides abstracts as pilot-only. Require abstract capture for final and corrective searches.

Describe only the accepted source cells, controls, capture contract, and reconciliation steps. Keep run history in the numbered evidence directories and [the readiness audit](../readiness-audit.md).
