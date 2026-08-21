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

## Required guideline sections

Use [`templates/source-guideline.md`](templates/source-guideline.md). Direct-source acceptance requires guidance for A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2. Local-source acceptance requires complete candidate and tag rules for P, E, M, `G_model`, `G_structure`, C1, R, and T2.

## Pilot acceptance gate

A supervising reviewer, not the drafting subagent, accepts a pilot only after:

- the manifest validates and all required checks are evidenced or explicitly blocked;
- source boundary, current interface, fields, controls, expansion, controlled-vocabulary or indexed-term availability and mappings, date/language handling, limits, pagination/export, stable identity, completeness, and failure behavior have been tested;
- every direct partition or local rule has an exact specification and evidence linkage;
- no screening or candidate import occurred;
- the reusable guideline distinguishes observed behavior from official documentation and remaining uncertainty;
- any semantic change has been committed to the protocol before a final search; and
- `search-log.md`, the Part 2 source index, and `TASKS.md` have been reconciled serially.

## Subagent write boundary

A source-pilot subagent may edit only its assigned source packet and, when explicitly authorized, source-specific scripts under `SLR/SLR1/scripts/`. It must not edit `TASKS.md`, `search-log.md`, any `protocol*.md`, dictionaries, crosswalks, schemas, another source packet, or `final-events/`.
