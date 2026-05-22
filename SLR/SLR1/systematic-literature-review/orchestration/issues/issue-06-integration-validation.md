# Issue 06: Integrate final manuscript and validate

## Goal
Assemble the generated/drafted components into the Wiley Systems Engineering template at `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex`, add bibliography entries, ensure figures paths work, and run validation/compilation checks where possible.

## Context
Previous issues should have produced:
- `drafts/reference_positioning.md`
- `drafts/methodology.tex`
- `drafts/results.tex`
- `drafts/discussion.tex`
- `drafts/results_tables.tex`
- figures/data under `SLR/SLR1/systematic-literature-review/figures/` and `.../data/`

The final manuscript should include methodology, results, and a first-pass discussion only. Do not add an introduction, full abstract, or conclusion. The template may need minimal metadata placeholders, but delete generic help text and example objects.

## Required inputs to read
- `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex`
- All draft fragments under `SLR/SLR1/systematic-literature-review/drafts/`
- `SLR/SLR1/extractions/*.json` for bibtex fields
- Reference SLR metadata from `incose-journal-research/Systems Engineering - 2026 - Buruso - Model‐Based Systems Engineering in Space Applications  A Comprehensive Literature.md`

## Required outputs
1. Overwrite/update `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex` with a clean Wiley-template manuscript draft.
2. Write/update `SLR/SLR1/systematic-literature-review/bibliography/converted_to_latex.bib` with:
   - all cited `paper-####` BibTeX entries from extraction JSON files, or all 40 extracted corpus entries for simplicity;
   - a BibTeX entry for Buruso et al. 2026 with key `Buruso2026MBSESpace`.
3. Ensure all included figures are under `SLR/SLR1/systematic-literature-review/figures/` and referenced with paths compatible with the template's `\graphicspath{{figures/}}`.
4. Run a validation check:
   - At minimum grep/check that placeholder template text is gone, body contains no `\section{Introduction}` or `\section{Conclusion}`, and citations have bibliography entries.
   - If LaTeX tooling/class is available, run `latexmk` or `pdflatex` in `SLR/SLR1/systematic-literature-review/` and record result.
5. Write `SLR/SLR1/systematic-literature-review/drafts/integration_report.md` summarizing what was integrated and any compile limitations.

## Constraints
- Do not push.
- Do not commit unless explicitly instructed by the orchestrator; leave changes for review.
- Preserve the user's requested scope: methodology, results, discussion only.
