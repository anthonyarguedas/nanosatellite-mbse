# Source-pilot subagent contract

You are assigned exactly one SLR1 source-pilot task. Read `SLR/SLR1/AGENTS.md`, all of `SLR/SLR1/searches/README.md`, the relevant task in `SLR/SLR1/TASKS.md`, and every linked protocol section before acting.

Constraints:

- This is a focused diagnostic pilot, not a final search and not screening.
- Use only the normal authorized interface or prospectively validated public/native route. Never bypass access controls.
- Test current behavior; do not treat existing adapters, prior diagnostics, or model memory as proof.
- Determine whether the source has a genuine controlled vocabulary or distinct indexed-term field. Where available, inspect scope, hierarchy and known-record descriptors, and test them only as OR supplements to the mapped free-text concept; otherwise document that none is usable.
- Save only inside the assigned source packet. Do not edit shared integration files.
- Do not retain or classify records beyond the minimum diagnostic metadata needed to test totals, pagination, stable identity, and completeness.
- Mark unknown behavior unknown. Stop and report `blocked` on login, CAPTCHA, challenge, source-boundary ambiguity, or unreconciled behavior.
- Ask for a final summary containing: status; files changed; tested requirements; untested/blocked items; evidence paths; semantic/protocol impact; and human verification still required.
