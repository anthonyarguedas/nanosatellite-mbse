report:
	python3 scripts/generate_extraction_report.py
	pdflatex scoping-review.tex
	pdflatex scoping-review.tex

pdf: report

clean:
	rm -f *.aux *.log *.out *.toc *.lof *.lot scoping-review.pdf

.PHONY: report pdf clean
