# Issue 03: Draft Methodology section in LaTeX

## Goal
Draft a self-contained `Methodology` section in LaTeX for the systematic literature review, following the reference SLR's review-method style while using our actual protocol/search/screening/extraction artifacts.

## Context
The final manuscript will be in `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex`, but this issue should only write a fragment. The user requested methodology, results, and first-pass discussion only; no introduction, abstract, or conclusions.

The reference SLR's method sections include: review method/proposed method, research questions, information sources/search strategy, selection process, inclusion/exclusion criteria, review procedure/data collection, synthesis strategy, inter-rater reliability/validity. Our review does not appear to have an inter-rater reliability exercise; if not present, discuss quality appraisal and extraction consistency instead of inventing it.

## Required inputs to read
- `SLR/SLR1/protocol.md`
- `SLR/SLR1/search-log.md`
- `SLR/SLR1/screening.md`
- `SLR/SLR1/pdf-status.md`
- `SLR/SLR1/corpus.json`, `SLR/SLR1/corpus_accessible.json`, `SLR/SLR1/extraction.json`
- `SLR/SLR1/scoping-review/scoping-review.tex`, especially its search flow and extraction synthesis wording.
- `SLR/SLR1/systematic-literature-review/drafts/reference_positioning.md` if it exists.

## Required output
Write `SLR/SLR1/systematic-literature-review/drafts/methodology.tex`.

Include LaTeX subsections roughly:
- `\section{Methodology}`
- `\subsection{Protocol and research questions}`
- `\subsection{Information sources and search strategy}`
- `\subsection{Selection process and eligibility criteria}`
- `\subsection{Data extraction and quality appraisal}`
- `\subsection{Synthesis strategy}`
- `\subsection{Review validity}`

Must include:
- The three RQs from `protocol.md`.
- The PRISMA counts: 199 raw merged records, 118 duplicates removed, 81 unique records screened, 37 excluded during screening, 44 reports sought, 4 not retrieved/inaccessible, 40 extracted.
- Eligibility criteria tailored to nanosatellite/CubeSat and MBSE/EPS/V&V scope.
- Synthesis emphasis: concise enabler taxonomy; main synthesis on value evidence and V&V linkage.
- Cite reference SLR as `\cite{Buruso2026MBSESpace}` only for positioning/methodological comparison, not as evidence about our corpus.

## Constraints
- Do not edit `Systems Engineering Template.tex`.
- Do not commit or push.
- Do not invent searches or reliability tests not documented in the artifacts.
