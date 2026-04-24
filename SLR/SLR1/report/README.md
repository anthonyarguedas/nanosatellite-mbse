# SLR1 extraction findings report

Generated artifacts for the extraction findings report.

Regenerate everything from the maintained protocol/extraction data with:

```bash
python3 ../scripts/generate_extraction_report.py
```

From this directory, compile the PDF with:

```bash
pdflatex extraction_findings.tex
pdflatex extraction_findings.tex
```

The generator uses deterministic numeric, categorical, and keyword-based rules only; no embedding model is used.

Key outputs:
- `extraction_findings.tex` -- LaTeX report
- `figures/` -- regenerated charts as PDF and PNG
- `data/studies.csv` -- study-level derived classifications
- `data/category_counts.csv` -- category counts and members
- `data/study_classifications.json` -- JSON audit trail for derived categories
