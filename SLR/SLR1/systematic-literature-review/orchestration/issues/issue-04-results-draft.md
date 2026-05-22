# Issue 04: Draft Results section in LaTeX

## Goal
Draft the systematic review `Results` section in LaTeX. Present broad methods/languages/tools findings concisely, and emphasize value-driven MBSE evidence and V&V linkage in nanosatellite/EPS contexts.

## Context
Existing scoping-review text has many broad tables/figures. The reference SLR from Buruso et al. already covers broad MBSE methods/languages/tools in space applications, so our results should not spend too much space on those except to situate this nanosatellite corpus. Our unique results are in the extraction schema fields for claims, evidence strength, governance/ROI, EPS relevance, and verification-specific model linkage.

## Required inputs to read
- `SLR/SLR1/scoping-review/scoping-review.tex`
- `SLR/SLR1/extraction.json`
- Representative extractions, especially core/EPS/V&V relevant papers:
  - `SLR/SLR1/extractions/paper-0026.json` (EPS-specific/open-source traceability)
  - `paper-0001`, `paper-0003`, `paper-0008`, `paper-0015`, `paper-0023`, `paper-0034`, `paper-0053`, `paper-0059`, `paper-0063`, `paper-0077`, `paper-0078`, `paper-0079`, `paper-0080` as available
- Generated artifacts from Issue 02 if present:
  - `SLR/SLR1/systematic-literature-review/drafts/data_summary.md`
  - `SLR/SLR1/systematic-literature-review/drafts/results_tables.tex`
  - CSVs/figures under `SLR/SLR1/systematic-literature-review/data/` and `.../figures/`

## Required output
Write `SLR/SLR1/systematic-literature-review/drafts/results.tex`.

Include LaTeX subsections roughly:
- `\section{Results}`
- `\subsection{Search, screening, retrieval, and extraction flow}` (reference local PRISMA figure)
- `\subsection{Study characteristics and quality}`
- `\subsection{Modeling focus and EPS relevance}`
- `\subsection{MBSE approaches, languages, and toolchains}` (concise)
- `\subsection{Claimed outcomes and value-evidence strength}`
- `\subsection{Verification and validation linkage}`
- `\subsection{Gap mapping}`

Must include:
- PRISMA figure includegraphics path local to systematic review, e.g. `figures/prisma_flow.pdf`.
- Counts from current scoping review and generated artifacts.
- Specific examples with citations to study keys where useful, e.g. `\cite{paper-0026}`.
- Clear language separating claims from demonstrated evidence.
- No discussion/conclusion language beyond results interpretation.

## Constraints
- Do not edit `Systems Engineering Template.tex`.
- Do not commit or push.
- If Issue 02 artifacts are absent, compute needed counts directly from `extraction.json`/per-study JSON and note that in your output comments.
