# Issue 02: Generate systematic-review data artifacts for value/V&V focus

## Goal
Create data summaries, figures, and LaTeX-ready table snippets for the systematic review's Results section, emphasizing value-driven MBSE evidence, EPS/nanosatellite relevance, pre-physical V&V linkage, and gap mapping.

## Context
Existing scoping review outputs already provide broad categories and figures under `SLR/SLR1/scoping-review/`. For the new SLR, broad methods/languages/tools should be concise. The new emphasis is:
- Value-driven MBSE in nanosatellite/CubeSat contexts.
- Evidence strength for claimed outcomes (reliability, reproducibility, integrability, traceability, cost/schedule, governance/ROI).
- EPS-specific or power-budget relevance.
- Verification and validation artifacts linked to models before physical development.
- Gap mapping inspired by Buruso et al. Table 5.

## Required inputs to read/use
- `SLR/SLR1/extraction.json`
- `SLR/SLR1/extractions/*.json`
- `SLR/SLR1/protocol.md`
- `SLR/SLR1/scoping-review/data/*.csv` and `SLR/SLR1/scoping-review/scoping-review.tex` for existing counts to reuse/verify.
- Reference SLR Table 5 in `incose-journal-research/Systems Engineering - 2026 - Buruso - Model‐Based Systems Engineering in Space Applications  A Comprehensive Literature.md`.

## Required outputs
1. A script at `SLR/SLR1/systematic-literature-review/scripts/generate_slr_artifacts.py` that reads the extraction JSON files and regenerates the outputs below.
2. CSV files under `SLR/SLR1/systematic-literature-review/data/`:
   - `study_characteristics.csv`
   - `eps_relevance_counts.csv`
   - `approach_classification_counts.csv`
   - `claim_evidence_by_outcome.csv`
   - `vv_linkage_counts.csv`
   - `gap_mapping_counts.csv`
   - `top_value_claims.csv` (highest-confidence/value-relevant claim records with study id, claim, category, evidence type, confidence)
3. Figures under `SLR/SLR1/systematic-literature-review/figures/` as PDF and PNG where practical:
   - `prisma_flow` (can copy or regenerate from scoping-review, but path must be local to systematic review)
   - `eps_relevance_counts`
   - `claim_evidence_by_outcome`
   - `vv_linkage_counts`
   - `gap_mapping_counts`
4. LaTeX snippets under `SLR/SLR1/systematic-literature-review/drafts/`:
   - `results_tables.tex` containing compact `table` or `longtable` environments for the key counts.
   - `data_summary.md` describing generated outputs, exact counts, and any assumptions.

## Constraints
- Do not edit `Systems Engineering Template.tex`.
- Do not modify scoping-review source/output files.
- Do not commit or push.
- Use deterministic processing only; no internet required.
