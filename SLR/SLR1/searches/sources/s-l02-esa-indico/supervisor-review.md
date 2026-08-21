# Supervising review — S-L02 ESA Indico

- **Reviewed:** 2026-08-21
- **Pilot:** `S-L02-P01-20260821T000344-0400`
- **Reviewer role:** primary orchestration agent; this is not independent human review
- **Disposition:** **retain as a successful diagnostic, but do not accept the local-harvest guideline yet**

## Review performed

The supervisor read the guideline, local-method specification, manifest, observations, evidence index, safe summaries, and selected raw diagnostics. The manifest validates against `slr1-pilot-manifest/v1`; all packet JSON parses; listed artifact hashes reconcile; changes stay inside the assigned source packet; and no screening or candidate import occurred.

The pilot independently supports classifying ESA Indico as a local-harvest source. It also establishes the existence of public event, contribution/subcontribution search types, attachments, event notes, opaque search cursors, `total=-1`, usable event/category exports, stable child identifiers in bounded examples, protected folders, and public file routes.

## Why acceptance is withheld

The draft correctly reports that it has not proved a complete public source universe. In particular, it has not established root-category recursion and caps, undated-object handling, two complete root ledgers, all-event timetable/note reconciliation, a live sub-contribution example, or complete file/archive parsing. Those are required coverage properties, not optional final-run preflights.

Two specification choices also require an explicit decision before acceptance:

1. **Public event notes:** the pilot found a public text-bearing route not named explicitly in the task. The next revision must either include it as part of the full Indico event universe or commit a source-boundary rationale for excluding it.
2. **Explicit-pair semantics:** `local-method-spec.json` currently operationalizes dictionary pairs as either-order matches separated by zero through three tokens. That is a draft implementation choice, not yet demonstrated to be semantically equivalent to the protocol's “explicitly paired” language. The next revision must validate or revise this rule and document whether a protocol clarification is needed.

## Required next pilot

A follow-up may be focused rather than repeating all diagnostics. It must close the U1–U4 universe/material gates, resolve the two decisions above, test the final deterministic matcher against controlled fixtures, and produce a complete two-pass source-ledger receipt. Until then:

- keep `guideline.md` and `local-method-spec.json` in draft status;
- keep task `S-L02` open;
- do not create a final ESA event or import any prefix; and
- treat any attempted incomplete harvest as `total=null`.

The diagnostic itself is methodologically successful: withholding acceptance avoids the hidden completeness assumption the pilot was intended to detect.
