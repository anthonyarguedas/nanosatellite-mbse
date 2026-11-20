# Published mission evidence and COTS case studies

## Live execution

From the repository root, with Python 3.12:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 final_report/fig/cots-case-study.py
```

The driver executes 14 automatic catalogue queries for MOP-11 and records 149 checks. It supplies no candidate list. A second public Requirement evaluation in a separate mission records the false or unresolved conditions of excluded reference parts. Expected values and verdicts come from `independent_cots_reference.py`, which imports only decimal arithmetic and uses facts transcribed from the original mission and manufacturer PDFs. It reads no catalogue tables and calls no framework calculation functions.

The checks compare purchased-cell targets, selected ratings, conditions, verdicts and inclusion or exclusion. They also compare mission definitions, catalogue engineering records and framework/catalogue file hashes before and after every query. Generated class caches are outside that engineering-record comparison.

For a deterministic replay:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 final_report/fig/cots-case-study.py --output /tmp/cots-case-replay
```

The five generated JSON records must match the corresponding records in this directory byte for byte when using the same source and framework versions. The summary records the framework commit and source hashes, including uncommitted implementation changes. The live cases do not modify framework code or catalogue data.

The same execution records MOP-10 catalogue inspection by inherited CSRM EPS hardware type. All five hardware types meet the minimum of five products, so this measure is verified. Counts use distinct manufacturer/part-number pairs. All 147 products have source datasheet links.

## Original documents

`independent_cots_reference.py` records each original PDF URL, cache location, page range and SHA-256. The original PDFs must be present at those locations before execution. They are a local source cache, separate from the report figures. Retrieve missing originals from the recorded URLs and check their hashes. GitHub mission sources use pinned revisions. The four manufacturer PDF hashes also match the catalogue's source register.

The inputs preserve the differences between the 2019 OreSat Alta/3300 mAh configuration and later XTE-SF/Tenergy hardware. Four independent 2S packs are retained when later cells are assessed against the earlier budget. The solar comparison replaces the budget's two illuminated Alta modules with two later two-cell modules. Branch current sharing is not inferred. BIRDS storage DoD, delivery efficiency and mean solar projection are explicit assessment assumptions. The report gives every numerical input.

All baseline reference parts are included. Stricter budgets exclude all four. Missing mission retention or minimum solar power ratings leave four queries unresolved. At the selected 1e15 1 MeV electrons/cm² condition, 3G30A remains eligible and XTE-SF does not. These are property screens, not flight or lifetime qualification.

## Source crops

Install PyMuPDF in an isolated environment, then run:

```sh
python3 final_report/fig/case-study-source-crops.py
```

The generator produces 14 PDF crops and `source-evidence.json`. The manifest records original URLs and hashes, page numbers, crop rectangles, extracted source text where available, and the MOPs supported. It preserves original colours and markings. It does not redraw data, alter labels or replace source values. Separate nonadjacent excerpts remain separate panels.

The six report figures cover both published power budgets, battery arrangements, condition-qualified solar ratings, the 2016 OreSat mass estimates and the labelled Maya-2 I–V and power plots. The last three also anchor existing MOP-12, MOP-14, MOP-16 and MOP-18 results. Their earlier numerical case suite was not rerun for this update.

`mop11-evidence.tex` and `source-figures.tex` are the concise report-facing evidence. All essential inputs, assumptions, equations, numerical results and limitations are in the compiled report. The JSON and Python records support reproducibility and are not required to read the report.
