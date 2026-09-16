# Nanosatellite EPS V&V evidence pilot

Files:

- `evidence.md`: cited synthesis and evidence assessment
- `evidence.csv`: machine-readable evidence records
- `presentation.tex`: 16:9 LaTeX Beamer source
- `presentation.pdf`: compiled 23-slide presentation
- `source-images.md`: provenance for every copied source graphic
- `assets/`: source graphics used in the deck

Build the presentation with XeLaTeX:

```bash
cd embeddings/vv-synthesis
latexmk -xelatex -interaction=nonstopmode -halt-on-error presentation.tex
```

The deck has no author, date, footer, or slide numbers. Each content slide contains a title used as a graphic caption.
