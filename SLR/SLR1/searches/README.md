# Search artifact contract

This directory contains only artifacts created anew for the SLR1 restart. The concept blocks and Boolean schedule in Part 2 are normative.

## Layout

```text
searches/
├── search-concept-dictionary.json
├── source-interface-prisma-crosswalk.json
├── schemas/
├── templates/
├── sources/<task-id>-<source-slug>/
│   ├── guideline.md
│   ├── translation-spec.json          # direct sources
│   ├── queries/                       # exact UTF-8 source-native text
│   ├── local-method-spec.json         # local-harvest sources
│   ├── prior-diagnostics/             # explicitly non-accepted observations
│   └── pilots/<pilot-id>/
│       ├── manifest.json
│       ├── observations.md
│       └── evidence-index.json
└── final-events/                       # untouched until R-002
```

Directory names use lowercase task IDs, for example `s-d01-scopus` and `s-l02-esa-indico`. Pilot IDs use `<TASK>-P<NN>-<YYYYMMDDThhmmss-offset>` with filesystem-safe timestamps.

## Separation rules

1. A pilot is diagnostic only. Set `diagnostic_only=true`, `screening_performed=false`, and `candidate_import_permitted=false` in its manifest.
2. Never copy a pilot result into `final-events/`, screening data, or the candidate corpus.
3. Keep exact queries in plain UTF-8 files. `translation-spec.json` maps each semantic partition to one or more source-native query cells and records lossless unions.
4. `guideline.md` contains the reusable operating method, not a chronological narration.
5. Pilot manifests and evidence contain observations. Every behavioral claim must be labelled `observed`, `official_documentation`, `inferred`, or `untested`; inferred or untested behavior cannot satisfy acceptance.
6. Record explicit source zero as zero. Access, syntax, transport, pagination, reconciliation, or completeness failures use `null`; never import a partial prefix.
7. Keep restricted or copyrighted captures outside Git when rights require it. Track a safe evidence index, checksum, access classification, and secure-location reference instead.
8. `final-events/` remains empty until task `R-002` is authorized.

## Browser-backed macOS preflight

Before a browser-backed pilot, the supervising controller must:

1. wrap the complete pilot process in `caffeinate -dims` and record the resulting sleep assertions;
2. run the dedicated Chrome launcher's read-only health check, reconcile a missing page anchor through the normal launcher, and rerun the read-only check;
3. require runtime and on-disk browser versions to match, stopping for a graceful dedicated-browser restart on mismatch rather than force-quitting or continuing;
4. record power source and check the pilot window for actual Sleep/Wake events; restart the dedicated browser before source work when it has survived a system sleep or fails a fresh health probe; and
5. preserve the controller-created anchor page while each adapter creates and closes only its own page.

`caffeinate` does not override clamshell sleep: keep the lid open during a pilot. Do not run competing browser controllers against the same profile. Prefer a separately identified, non-auto-updating Chrome for Testing bundle for long-running automation so the normal Chrome Dock item, profile, and updater remain isolated.

## Required guideline sections

Use [`templates/source-guideline.md`](templates/source-guideline.md). Direct-source acceptance requires guidance for A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2. Local-source acceptance requires complete candidate and tag rules for P, E, M, `G_model`, `G_structure`, C1, R, and T2.

## Pilot lifecycle and handoff

Use one serialized gate for every source or corrective retry:

1. **Pilot:** the subagent executes one assigned diagnostic scope, writes a new immutable pilot ID and draft source-packet updates, then stops. It may not approve itself, retry automatically, or start another source.
2. **Controller review:** the supervising agent validates schemas, evidence, rights boundaries, failure accounting, and the draft guideline. It classifies any implementation issue as `true`, `false`, or `unresolved`. A demonstrated code defect goes to a separate code-fix subagent and commit before a newly authorized pilot ID; never overwrite the failed pilot.
3. **Human decision:** the controller presents only the methodological choices requiring judgment, each with a recommendation, evidence links, and deferred items. The review owner approves, rejects, or requests a scoped revision.
4. **Commit and integrate:** the Git commit containing the approved source packet is the approval record; pin any external adapter by commit. Do not maintain a separate approval-hash ledger. The controller then reconciles `search-log.md`, the Part 2 source index, and `TASKS.md` serially.
5. **Next pilot:** start only after the preceding pilot has an approval commit, an explicit human-authorized corrective-retry scope, or a recorded blocked disposition. The next prompt cites the governing protocol, source-packet, and implementation commits.

When date controls need testing before `P-001`, use the pilot execution date as a clearly labelled diagnostic upper bound. `P-001` remains required only before the first final search; a pilot bound is never the common cutoff and pilot records are never imported.

## Pilot acceptance gate

The review owner, not the drafting subagent or supervising AI, accepts a pilot only after:

- the manifest validates and all required checks are evidenced or explicitly blocked;
- source boundary, current interface, fields, controls, expansion, controlled-vocabulary or indexed-term availability and mappings, date/language handling, limits, pagination/export, stable identity, completeness, and failure behavior have been tested;
- every direct partition or local rule has an exact specification and evidence linkage;
- no screening or candidate import occurred;
- the reusable guideline distinguishes observed behavior from official documentation and remaining uncertainty;
- any semantic change has been committed to the protocol before a final search;
- the human decision and any implementation commit are recorded by the approval commit, without a separate approval-hash ledger; and
- `search-log.md`, the Part 2 source index, and `TASKS.md` have been reconciled serially.

## Subagent write boundary

A source-pilot subagent may edit only its assigned source packet and, when explicitly authorized, source-specific scripts under `SLR/SLR1/scripts/`. It must not edit `TASKS.md`, `search-log.md`, any `protocol*.md`, dictionaries, crosswalks, schemas, another source packet, or `final-events/`.
