# Integration report: Issue 06

## Integrated manuscript

- Replaced `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex` with a clean scoped Wiley-template draft.
- Integrated the drafted LaTeX body sections from:
  - `drafts/methodology.tex`
  - `drafts/results.tex`
  - `drafts/discussion.tex`
- Preserved the requested scope: the body contains `Methodology`, `Results`, and `Discussion` only. No `\section{Introduction}` or `\section{Conclusion}` was added.
- Removed the original template help text, example figure/table, generic sample citations, acknowledgements guidance, conflict-of-interest guidance, and stray `\end{CJK}`.
- Kept only minimal metadata placeholders for author/correspondence/funding; no abstract environment is present in the final scoped draft.

## Bibliography

- Created `SLR/SLR1/systematic-literature-review/bibliography/converted_to_latex.bib`.
- Added BibTeX entries for all 40 extracted corpus JSON files under `SLR/SLR1/extractions/*.json` using keys `paper-####`.
- Added the reference SLR entry `Buruso2026MBSESpace` using metadata from the Buruso et al. 2026 Systems Engineering article:
  - journal: `Systems Engineering`
  - year: `2026`
  - pages: `1--43`
  - DOI: `10.1002/sys.70051`
- Final manuscript citation check: 24 cited keys, 41 bibliography entries, 0 missing cited entries.

## Figures

- Set `\graphicspath{{figures/}}` in the manuscript preamble.
- Updated integrated figure references to use figure basenames compatible with that graphics path:
  - `prisma_flow`
  - `eps_relevance_counts`
  - `claim_evidence_by_outcome`
  - `vv_linkage_counts`
  - `gap_mapping_counts`
- Validation found all five referenced figures under `SLR/SLR1/systematic-literature-review/figures/`.

## Validation results

Static checks run from repository root:

- Placeholder/template text check: passed; no original template placeholders were found.
- Section scope check: passed; no `\section{Introduction}` or `\section{Conclusion}` present.
- Citation-to-bibliography check: passed; no cited keys missing from `converted_to_latex.bib`.
- Figure existence check: passed; all referenced figures exist under `figures/`.

LaTeX tooling check:

- `latexmk` and `pdflatex` are installed.
- Direct Wiley-template build command run in `SLR/SLR1/systematic-literature-review/`:
  - `latexmk -pdf -interaction=nonstopmode -halt-on-error "Systems Engineering Template.tex"`
- Result: failed before manuscript processing because the local TeX installation does not provide `wiley-article.cls` (`kpsewhich wiley-article.cls` returned no path; LaTeX error: `File 'wiley-article.cls' not found`).
- A temporary local article-class fallback syntax check was also run with Wiley macros stubbed only for validation; it completed and produced a PDF, with non-fatal BibTeX warnings about several extraction records whose venue/journal fields were not reported in the JSON metadata.

## Known limitations

- The final file intentionally preserves the Wiley `wiley-article` document class, so full compilation requires adding the Wiley class/template support files to the LaTeX environment or project directory.
- Several BibTeX entries have sparse venue metadata because the corresponding extraction JSON fields reported no exact venue/journal; they are included so every corpus/cited key resolves.
- The manuscript remains a first-pass draft and intentionally omits the abstract, introduction, and conclusion per issue scope.
