# Pilot 005: Link to Nature canonical metadata mapping

Required changes were applied in commit: 49c0cca95b2f4d5551a0d1cb5ce24dc01a8ba7b8

Export method: adapter version 11 at `~/agent-tools/internet/skills/browser/scripts/search_springer_link.py`. This is a bounded detail-route diagnostic. It is not a search or final-search artifact.

## Objective

Validate the canonical metadata relationship observed by Pilot 004 while keeping the Springer Link card path as the record identity and detail source.

The [event plan](searches/event-plan.json) fixes the source card path, visible title, expected Nature canonical URL, zero-redirect route, abstract requirement, and no-status-check rule.

## Adapter repair

Adapter version 11 allows this exact mapping:

```text
https://link.springer.com/article/10.1038/<suffix>
<link rel="canonical" href="https://www.nature.com/articles/<suffix>">
```

The mapping applies only when:

- the browser remains on the exact Link article route
- the Link DOI prefix is `10.1038`
- the Nature canonical path has the same DOI suffix
- both URLs use their exact HTTPS hosts and default ports
- the URLs contain no credentials, query, or fragment
- the visible Link H1 matches the search-card title

The adapter keeps the Link card path as identity. It reads the abstract and publication date from Link. It does not navigate to Nature.

The adapter no longer uses the final navigation response status as an acceptance condition. It still uses the final response object to inspect the main-frame request chain. Rendered access, route, title, abstract, canonical, and date validation remains active. Intermediate redirect hops still require a valid redirect chain.

## Live result

The [live adapter validation](searches/adapter-validation.json) passed with:

- final URL `https://link.springer.com/article/10.1038/s44359-026-00173-2`
- zero redirects
- no navigation alias
- canonical metadata URL `https://www.nature.com/articles/s44359-026-00173-2`
- matching visible title
- a visible 1,365-character Link abstract
- exact Link publication date `2026-05-26`
- no request to the Nature URL
- successful owned-page cleanup

## Decision

Accept the exact Link 10.1038 to Nature article canonical metadata mapping. The external canonical-link blocker from Pilot 004 is resolved. [Pilot 006](../006/pilot.md) later validated exact-day handling and strict complete publication in shared Chrome.

## Reproduction

```bash
PYTHONPATH=SLR/SLR1/source-specific/springer-nature-link/scripts/springer_nature_link_pilot005 \
uv run SLR/SLR1/source-specific/springer-nature-link/scripts/springer_nature_link_pilot005/validate_mapping.py
```
