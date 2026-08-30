# Scopus Pilot 003 helpers

These helpers import `../pilot_schedule/queries.py`. They do not keep a second concept list.

The default read-only adapter is `$HOME/agent-tools/internet/skills/browser/scripts/search_scopus.py`. Set `SCOPUS_ADAPTER` when the adapter is installed elsewhere.

- `build_plan.py` writes the literal 13-event pilot plan.
- `run_events.py` invokes the read-only Scopus adapter under the shared browser.
- `focused_adapter.py` is a pilot-local Monaco text-entry recovery harness. It preserves exact native readback before Search and uses the pinned adapter's repaired abstract follow-up.
- `build_unions.py`, `investigate_large_sets.py`, and `audit_local_pairs.py` create the linked audit receipts.
- `follow_up_abstracts.py` retrieves native abstracts only for IDs already in a complete union. Its batch failures remain explicit.
- `split_lossless_cells.py` and `run_nested_cells.py` preserve parent OR factors while recording source-cell recovery failures.
- `validate_pilot.py` checks JSON, membership, controls, safe error receipts, the focused adapter, and the source guideline.

All outputs remain pilots. None writes to `final-searches/`.
