report:
	python3 ../scripts/generate_extraction_report.py
	pdflatex extraction_findings.tex
	pdflatex extraction_findings.tex

pdf: report

clean:
	rm -f *.aux *.log *.out *.toc *.lof *.lot extraction_findings.pdf

.PHONY: report pdf clean
