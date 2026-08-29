# Source Name

Last pilot saved in commit: NA
PSR final searches saved in commit: NA
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_template.py`

Final searches are saved to `source-specific/template/final-searches/`, both for discovery and citation chasing (for Scopus and WoS only).
Name each search artifact with the cross-source query schedule ID (`A1.json`, `A2.json`), PSR query schedule ID (`PSR1.json`) (Scopus and WoS only) or seed paperID in the case of citation chasing events (`<paperID>.json`) (Scopus and WoS only).

The script above automatically saves the required search event metadata, including failures and a final search/citation chasing label.

A single search event failure does not warrant excluding the source from the review, only systematic failures that conflict with inclusion/exclusion criteria.

Search rationales and strategies are linked to the cross-source query schedule, so they are not source-specific.

## Filters applied in the UI
- Date:
- Language:
- Publication Type:
- Database or collection:
- Interface: Web
- URL:
- Other that are shared between all queries

### Special filters applied in the UI for PSR searches

For Scopus and WoS only.

## Search behavior
- stemming, lemmatization, automatic expansion, wildcard behavior
- pagination, result ordering, stable identifiers, and source limits

## Controlled vocabulary used in the UI
- any controlled-vocabulary or indexed-term fields, descriptors, hierarchies, and explosion settings

### Special controlled vocabulary used in the UI for PSR searches

For Scopus and WoS only.

## Filters applied within query
`write query prefix or suffix here, that is shared between all queries`

### Special filters applied within query for PSR searches

For Scopus and WoS only.

## Population and EPS blocks
## MBSE and relationship blocks
## Artifact and tailoring blocks
## Additional concept blocks for PSR (Scopus and WoS only)

Write source-specific translations of the blocks here.
They could be a single query string or multiple strings applied to multiple fields. Note the name of each field.

## Query schedule

Write the table here.

### PSR query schedule
For Scopus and WoS only.

## Pilots

- [ ] [Pilot consecutive number](source-specific/template/pilots/template/pilot.md) Mark it done when the changes resulting from the pilot are commited, or if it ends without changes needed. Pilots can also be run for PSR searches.