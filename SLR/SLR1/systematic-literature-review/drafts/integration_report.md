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
- Abstract-scope check: passed; no `abstract` environment is present in the scoped draft.
- Citation-to-bibliography check: passed; no cited keys missing from `converted_to_latex.bib`.
- Figure existence check: passed; all referenced figures exist under `figures/`.

LaTeX tooling check after adding local Wiley support files:

- `wiley-article.cls` is present in `SLR/SLR1/systematic-literature-review/`.
- Added local `rss.bst` so the class's `alpha-refs` bibliography style resolves. The local file is a copy of TeX Live's `plainnat.bst`, used under the `rss.bst` name expected by the Wiley class.
- Made the `\@combinedblfloats` patch conditional so the manuscript compiles with the supplied Wiley class even when that internal macro is unavailable.
- Removed the duplicate explicit `\bibliographystyle{plainnat}` from the manuscript because the Wiley class already writes `\bibliographystyle{rss}` for `alpha-refs`.
- Direct Wiley-template build command run in `SLR/SLR1/systematic-literature-review/`:
  - `latexmk -pdf -interaction=nonstopmode -halt-on-error "Systems Engineering Template.tex"`
- Result: passed. Output PDF: `SLR/SLR1/systematic-literature-review/Systems Engineering Template.pdf` (17 pages).
- Remaining messages are non-fatal typography/BibTeX warnings: overfull/underfull boxes, font substitutions, and sparse venue metadata for several extraction-derived BibTeX entries.

## Known limitations

- The bibliography style is a local compatibility shim (`rss.bst` copied from `plainnat.bst`) because the Wiley class references `rss.bst` but the local TeX installation does not provide it.
- Several BibTeX entries have sparse venue metadata because the corresponding extraction JSON fields reported no exact venue/journal; they are included so every corpus/cited key resolves.
- The manuscript remains a first-pass draft and intentionally omits the abstract, introduction, and conclusion per issue scope.
