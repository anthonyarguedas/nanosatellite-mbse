# Pilot 003

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py`

## Objective

Test a safely bounded local-harvest route at the 2026-08-29 cutoff and audit local coverage, attachments, checkpoint or resume, and literal versus wildcard matching.

## Runs

- [`local-harvest-cutoff.json`](searches/local-harvest-cutoff.json)
- [`local-behavior-fixture-audit.json`](searches/local-behavior-fixture-audit.json)

## Result

- [x] Document a source limitation

The live root category-0 route stopped on a public category-export timeout with `max-harvest-events=500`. It preserved a restart checkpoint at event index `0`, no total, and no records. This is a source failure, not zero coverage, and the cutoff stop rule prevented a retry. The offline fixture audit separately verified two matching snapshots, attachment hash/MIME/size/text evidence, resume from a missing event, and a wildcard superset with added completions. The local method covers Events, Contributions, and Materials only. Neither the fixture nor the scoped local route establishes complete category-0 coverage.
