# Issue 01: Analyze reference SLR structure and positioning

## Goal
Create a concise but actionable analysis of how the 2026 Buruso et al. Systems Engineering SLR is structured, what elements our nanosatellite MBSE SLR should emulate, and where our SLR should deliberately differ to avoid duplicating already-covered broad MBSE enabler findings.

## Context
The user wants to convert `SLR/SLR1/scoping-review/scoping-review.tex` into a systematic literature review using `SLR/SLR1/systematic-literature-review/Systems Engineering Template.tex`. The target journal is Systems Engineering. A highly relevant 2026 reference SLR is stored at:

`incose-journal-research/Systems Engineering - 2026 - Buruso - Model‐Based Systems Engineering in Space Applications  A Comprehensive Literature.md`

User insight: the reference SLR's gaps table motivates this review, but broad insights about methods and modeling languages are already covered. Our review must present those concisely and focus on value-driven MBSE in nanosatellite contexts and proper V&V linkage.

## Required inputs to read
- The reference SLR markdown above, especially sections 2, 3, 4, 5 and Table 5.
- `SLR/SLR1/scoping-review/scoping-review.tex` for what our scoping review already contains.
- `SLR/SLR1/protocol.md` for our RQs and extraction fields.

## Output
Write `SLR/SLR1/systematic-literature-review/drafts/reference_positioning.md` with:
1. A section-by-section outline of Buruso et al.'s review structure that is relevant to our methodology/results/discussion.
2. A mapping from Buruso Table 5 gaps to this SLR's unique contribution.
3. Recommended body outline and subsection titles for our manuscript (no intro, no abstract, no conclusion).
4. Specific cautions: which broad methods/languages/tools claims should be concise because Buruso already covers them.
5. Suggested citation phrasing for positioning this review relative to Buruso et al. Use citation key `Buruso2026MBSESpace`.

## Constraints
- Do not edit `Systems Engineering Template.tex`.
- Do not commit or push.
