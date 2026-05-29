# SLR1 extraction staleness audit after codebook v1.1

Date: 2026-05-28

Scope: `SLR/SLR1/protocol.md`, `SLR/SLR1/extraction_codebook.json`, `SLR/SLR1/corpus_accessible.json`, `SLR/SLR1/extractions/*.json`, `SLR/SLR1/extraction.json`, and `SLR/SLR1/sources.bib`.

No search or retrieval was rerun.

## Staleness found before repair

- `extraction_codebook.json` is now `codebook_version = 1.1`.
- `extraction.json` still declared `codebook_version = 1.0` and `controlled_field_count = 45`.
- All 40 individual extraction files parsed and matched the accessible corpus, but their `structured_code_summary` covered only the v1.0 controlled fields.
- Missing from 40/40 extractions:
  - `eps_verification_specific.ivv_integration_level`
  - `claimed_outcomes_value_mechanisms_evidence[].reliability_subtype`
- `mbse_objective_scope_artifacts.generality_reuse_mechanism` remained syntactically valid, but was semantically stale: none of the five v1.1 labels had been used.
- Other controlled values/statuses were valid against the v1.1 codebook. Limitation flags had assessments with rationale/evidence.
- Coverage was complete: 40/40 accessible corpus records had extraction files and 40 BibTeX entries existed in `sources.bib`.

## Repair method

A first scripted repair identified and filled the missing v1.1 fields. Because the new categories require paper-level reasoning, this was followed by a full per-paper siloed subagent pass.

For each of the 40 studies, a `pi -p --model openai-codex/gpt-5.5 --thinking xhigh --no-session` subagent reviewed only:

- `SLR/SLR1/protocol.md`
- `SLR/SLR1/extraction_codebook.json`
- that paper's markdown file
- that paper's current extraction file

Each subagent returned a JSON patch focused only on:

1. `mbse_objective_scope_artifacts.generality_reuse_mechanism`
2. `eps_verification_specific.ivv_integration_level`
3. `claimed_outcomes_value_mechanisms_evidence[].reliability_subtype`
4. claim-level `reliability_subtype` assignments

Subagent review artifacts are stored in `SLR/SLR1/extractions/v1_1_subagent_reviews/`.

## Repair applied

- Updated all 40 `SLR/SLR1/extractions/paper-*.json` files using the per-paper subagent patches.
- Added/refined `eps_verification_specific.ivv_integration_level` in each `structured_code_summary` and full `extraction.eps_verification_specific` section.
- Added/refined `claimed_outcomes_value_mechanisms_evidence[].reliability_subtype` in each `structured_code_summary` and claim-level `reliability_subtype` coding in full claim-evidence records.
- Re-coded `mbse_objective_scope_artifacts.generality_reuse_mechanism` with the expanded v1.1 label set where the paper-level reasoning supported it.
- Rebuilt `SLR/SLR1/extraction.json` from the repaired individual extractions with `codebook_version = 1.1` and `controlled_field_count = 47`.
- Left `SLR/SLR1/sources.bib` unchanged; it already contained 40 final-source entries.

Normalization note: claim-level `reliability_subtype` retains `not applicable` where appropriate. The aggregate `structured_code_summary` field lists only substantive reliability/reliability-adjacent subtypes when any are present, so aggregate counts remain interpretable for synthesis.

## Post-repair validation

Automated validation passed:

- JSON parsed for `extraction.json`, `extraction_codebook.json`, `corpus_accessible.json`, all 40 individual extraction JSON files, and all 40 subagent review JSON outputs.
- 0 missing v1.1 controlled fields across individual extractions.
- 0 invalid controlled values.
- 0 invalid statuses.
- 0 extra `structured_code_summary` keys outside the v1.1 codebook.
- 0 selected controlled codes missing rationale/evidence/confidence.
- 0 claim records missing `reliability_subtype`.
- Limitation flag assessments remain valid.
- Accessible corpus coverage remains 40/40, with tier counts unchanged: 21 core and 19 supporting.

## New aggregate counts after per-paper subagent repair

### IVV integration level

- `simulation-in-the-loop`: 12
- `none/not reported`: 10
- `executable/model-based checks`: 6
- `trace-linked verification artifacts`: 5
- `model-contained verification artifacts`: 2
- `separate document only`: 1
- `software/hardware-in-the-loop`: 1

Two papers have status `not_applicable` with no selected IVV value; one paper with status `not_reported` has no selected value.

### Reliability subtype

- `model consistency/reliability`: 34
- `mission assurance`: 29
- `defect/error reduction`: 11
- `system/mission reliability`: 10
- `process reliability`: 8
- `generic reliability claim`: 2
- `EPS reliability`: 2

### v1.1 generality/reuse labels

- `high-level abstraction`: 33
- `mission-agnostic architecture`: 22
- `specific-mission model with reusable method only`: 14
- `interface-focused model`: 12
- `low-dynamics / non-detailed-behavior model`: 10

## Repaired artifacts

- `SLR/SLR1/extraction.json`
- `SLR/SLR1/extractions/paper-*.json`
- `SLR/SLR1/extractions/v1_1_subagent_reviews/`
- `SLR/SLR1/extraction_staleness_audit.md`
