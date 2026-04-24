# SLR1 scoping review report

Generated artifacts for the SLR1 scoping-review report.

From this directory, regenerate everything from the maintained protocol/extraction data with:

```bash
python3 scripts/generate_extraction_report.py
```

From this directory, compile the PDF with:

```bash
pdflatex scoping-review.tex
pdflatex scoping-review.tex
```

The generator uses deterministic numeric, categorical, and keyword-based rules.

Key outputs:
- `scoping-review.tex` -- LaTeX report
- `figures/` -- regenerated charts as PDF and PNG
- `data/studies.csv` -- study-level derived classifications
- `data/category_counts.csv` -- category counts and members
- `data/study_classifications.json` -- JSON audit trail for derived categories
