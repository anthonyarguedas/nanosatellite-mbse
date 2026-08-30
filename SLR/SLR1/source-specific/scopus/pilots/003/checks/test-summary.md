# Pilot 003 checks

Run after the final union and abstract-follow-up receipts were written:

- `python3 scripts/pilot_schedule/test_queries.py` — 6 passed.
- `python3 scripts/scopus_pilot003/validate_pilot.py .../validation-final.json` — parsed 384 JSON artifacts; confirmed schedule membership, main/PSR controls, 88 null-total safe failures, focused adapter marker, source guideline, 327 main IDs, 111 main native abstracts, and 24 completed-PSR-subunion abstracts.
- `uv run scripts/scopus_pilot003/focused_adapter.py --help` — imports the pinned read-only Scopus adapter.
- `python3 /Users/antho/agent-tools-worktrees/slr-integration/internet/skills/browser/scripts/verify_academic_source_documentation.py` — verified 15 source/note pairs across 19 dimensions.
- `python3 -m json.tool` on the final union and validation receipt — passed.
- `git diff --check` — passed before staging; staged check is repeated before commit.
