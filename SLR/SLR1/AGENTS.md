`~/agent-tools/academic-research/skills/academic-search/scripts/` contains scripts to search the various academic search engines used in this review.

The above scripts are general-purpose searches.
If new, review-specific scripts need to be created, put them in `SLR/SLR1/scripts/`.

If necessary, for PDF-to-Markdown conversion use `~/agent-tools/processing/skills/pdf-to-markdown/scripts/pdf_to_markdown.py` with `--image-mode keep`.

Any metadata not automatically saved by the scripts must be recorded separately, to maintain PRISMA-S compliance.

Use plain English for writing.
Prefer linking to another section or file before duplicating information.

Controllers track tasks in `SLR/SLR1/TASKS.md` and keep the named documentation synchronized; role-specific subagents follow their assigned write boundary.

For source pilots, read and follow `searches/README.md`, [`searches/two-mode-validation-policy.md`](searches/two-mode-validation-policy.md), and the assigned role template. Use two modes: agent-driven exploration first for unknown/failing interfaces, then a separate frozen deterministic evidence attempt. Do not delay exploration for broad offline suites, and do not treat exploration as acceptance evidence. Keep role-specific browser, workflow, authorization, evidence, and write-boundary instructions there rather than duplicating them here.