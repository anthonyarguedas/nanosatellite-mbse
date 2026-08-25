# Evidence-pilot subagent contract

You are assigned exactly one frozen SLR1 evidence attempt. Read `SLR/SLR1/AGENTS.md`, `searches/README.md`, [`two-mode-validation-policy.md`](../two-mode-validation-policy.md), the browser checklist when applicable, the source's frozen exploration record, campaign, and exact evidence plan.

## Preconditions

- A working live route, interaction recipe, adapter/helper commit, query/control semantics, output contract, and expected evidence must already be frozen from exploration mode.
- Pass only the minimum launch gate: exact query bytes, command startup, create-only paths, manifest/receipt shape, and browser health. Do not run broad suites.
- If those prerequisites are absent, stop and return the source to exploration; do not improvise inside evidence mode.

## Execution

- This is a deterministic diagnostic evidence attempt, not a final search or screening.
- Use only the normal authorized source/interface and exact frozen operation plan.
- For browser work, run the complete attached phase through the canonical shared lease. Create/close only owned pages and never mutate the protected anchor.
- Do not patch selectors, waits, adapters, or scripts during the evidence attempt. A technical failure is preserved once and handed back to exploration mode with the most informative safe evidence available.
- Distinguish transient challenge, busy, loading, explicit zero, and technical/source failure. Passive challenge wait is allowed only under the frozen finite policy; never solve or bypass it.
- Record every source action, exact controls, totals, stable IDs, pagination/coverage, zero versus `null`, cleanup, and hashes.
- Retain no relevance classification, screening decision, candidate import, or final event.

## Write boundary

Write only the assigned evidence packet. Do not edit implementation code, campaign integration files, protocols, dictionaries, crosswalks, another source packet, or `final-events/`. The controller checkpoints `campaign.json` after reviewing your immutable attempt.

## Final summary

Report attempt outcome; operations/cap; passed, failed, and dependent gates; totals/zero/null; identity/coverage evidence; challenge/busy/loading behavior; cleanup/lease status; implementation commit; whether failure is technical or methodological; and whether the controller should checkpoint or return to exploration.
