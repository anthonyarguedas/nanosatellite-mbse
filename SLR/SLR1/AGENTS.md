`~/agent-tools/academic-research/skills/academic-search/scripts/` contains scripts to search the various academic search engines used in this review.

The above scripts are general-purpose searches.
If new, review-specific scripts need to be created, put them in `SLR/SLR1/scripts/`.

Any metadata not automatically saved by the scripts must be recorded separately, to maintain PRISMA-S compliance.

Use plain English for writing.
Prefer linking to another section or file before duplicating information.

Track tasks in `SLR/SLR1/TASKS.md`, mentioning explicitly which files need to be updated when the task is completed to maintain all documentation up-to-date.

For source pilots:

- Read `searches/README.md` and use the tracked templates and schemas.
- Pilot only the assigned source. Do not screen records or import pilot records into the review.
- Store reusable source instructions in the source packet and dated diagnostic evidence under its `pilots/` directory. Keep `final-events/` untouched until `R-002`.
- Treat unverified behavior as unknown or blocked; do not infer current interface behavior from memory or from an earlier run.
- A subagent may draft a guideline but may not accept it, mark a task complete, or edit shared integration files (`TASKS.md`, `search-log.md`, `protocol*.md`, crosswalks, dictionaries, or schemas). The supervising agent performs those steps after review.