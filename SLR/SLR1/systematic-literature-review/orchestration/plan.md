# Orchestration plan: convert SLR1 scoping review into Systems Engineering SLR manuscript sections

## End goal
Produce a first-pass systematic literature review manuscript in `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex`, using the Wiley Systems Engineering template, that contains **methodology, results, and a first-pass discussion only**. Do not write an introduction, abstract, or conclusion. The manuscript must follow the structure and review conventions of the 2026 Buruso et al. Systems Engineering reference SLR, including PRISMA-style flow reporting, structured selection/extraction methodology, quantitative/qualitative synthesis, and a gaps/opportunities discussion.

## Key source material
- Existing scoping-review synthesis: `SLR/SLR1/scoping-review/scoping-review.tex`
- Existing scoping-review figures/data/scripts: `SLR/SLR1/scoping-review/figures/`, `SLR/SLR1/scoping-review/data/`, `SLR/SLR1/scoping-review/scripts/generate_extraction_report.py`
- Review protocol: `SLR/SLR1/protocol.md`
- Search/screening/retrieval artifacts: `SLR/SLR1/search-log.md`, `SLR/SLR1/screening.md`, `SLR/SLR1/pdf-status.md`, `SLR/SLR1/corpus*.json`, `SLR/SLR1/extraction.json`, `SLR/SLR1/extractions/*.json`
- Target template: `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex`
- Reference SLR: `incose-journal-research/Systems Engineering - 2026 - Buruso - Model‐Based Systems Engineering in Space Applications  A Comprehensive Literature.md`

## Strategic framing
The 2026 reference SLR already covers broad space-MBSE methodology, languages, tools, and lifecycle phases. This SLR must therefore avoid overclaiming novelty in general MBSE enabler taxonomy. It should present methods/languages/tools concisely as context and focus the results/discussion on the gap the reference review highlights:

1. **Value-driven MBSE for nanosatellite/CubeSat contexts**: Are claimed benefits tied to mission objectives, deliverables, governance, ROI, decision criteria, or measurable value?
2. **EPS and resource-constrained nanosatellite tailoring**: How much evidence is EPS-specific versus system-level/power-budget-adjacent?
3. **V&V linkage before physical development**: Are verification procedures, test cases, parametric checks, simulations, or verification matrices linked to model artifacts rather than stated generically?

## Manuscript shape
Use the Wiley template but replace placeholder content. Keep front matter minimal/placeholders if unavoidable for template validity, but the body should start with `\section{Methodology}` and include no drafted intro/conclusion. Planned body:

1. `Methodology`
   - Protocol and research questions
   - Information sources and search strategy
   - Selection process and eligibility criteria
   - Data extraction and quality appraisal
   - Synthesis strategy (quantitative counts + qualitative gap mapping; no broad novelty claim on languages/tools)
   - Validity / limitations of review method
2. `Results`
   - Search, screening, retrieval, and extraction flow (PRISMA-style figure and counts)
   - Study characteristics and quality overview
   - Modeling focus and EPS relevance
   - MBSE methods/languages/tools (concise, contextual)
   - Claimed outcomes and strength of value evidence
   - V&V linkage and pre-physical verification mechanisms
   - Gap mapping against Buruso et al. gaps
3. `Discussion` (first pass)
   - What remains uncovered after the 2026 broad space-MBSE SLR
   - Value-driven MBSE is weakly evidenced in nanosatellite MBSE
   - V&V linkage exists mostly as parametric/simulation/traceability fragments, rarely as an integrated EPS verification thread
   - Lightweight nanosatellite MBSE needs an adoption/evaluation playbook
   - Threats to validity and implications for future work (but no conclusion section)

## Delegated issues
1. Reference-structure and positioning analysis: identify exactly what to emulate from Buruso et al. and what to avoid duplicating.
2. Data-artifact generation: produce systematic-review figures/tables/data summaries focused on value evidence, EPS relevance, V&V linkage, and gap mapping.
3. Methodology draft: write a self-contained LaTeX section using protocol/search/screening/extraction artifacts and reference-SLR style.
4. Results draft: write a self-contained LaTeX results section using generated data and existing scoping-review evidence, with methods/languages/tools concise.
5. Discussion draft: write a self-contained LaTeX first-pass discussion centered on value-driven MBSE and V&V linkage gaps.
6. Integration and validation: assemble final Wiley-template `.tex`, bibliography, figures, and compile/lint if possible.

## Coordination rules for subagents
- Do not push.
- Prefer not to commit; leave changes for orchestrator approval.
- Avoid editing the final target `.tex` until the integration issue. Draft subagents should write fragments in `SLR/SLR1/systematic-literature-review/drafts/`.
- Data subagent should write generated support files under `SLR/SLR1/systematic-literature-review/data/` and `.../figures/`, without modifying scoping-review outputs.
- Cite corpus studies using stable keys from each extraction's `bibtex` field (`paper-0001`, etc.) and cite the reference SLR as `Buruso2026MBSESpace`.
- Preserve all claims as evidence-based; distinguish unsupported/weak/moderate evidence.

## Acceptance criteria
- `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex` contains polished Methodology, Results, and Discussion draft sections and no body Introduction/Conclusion.
- Includes a PRISMA-style figure or reused equivalent, with counts: 199 raw records, 118 duplicates removed, 81 screened, 37 excluded, 44 sought, 4 inaccessible, 40 extracted.
- Contains concise method/language/tool results and expanded value-evidence/V&V/gap-mapping results.
- Contains a first-pass discussion that explicitly positions this review relative to Buruso et al. (2026).
- Bibliography exists and includes all cited corpus studies plus Buruso et al. reference.
- Generated issue files are cleaned up from the final working tree after completion.
