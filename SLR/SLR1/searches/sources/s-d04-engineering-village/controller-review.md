# Controller review — Engineering Village pilot P01

**Reviewed:** 2026-08-24T12:58:53-04:00  
**Disposition:** P01 blocked and not accepted; corrective P02 authorized by the review owner at 2026-08-24T13:06:25-04:00; no final search authorized.

This is a controller review, not an approval record. The diagnostic pilot remains [`S-D04-P01-20260824T123301-0400`](pilots/S-D04-P01-20260824T123301-0400/). The review owner explicitly authorized the narrowly scoped P02 described below.

## Independent validation

Controller checks passed for:

- every tracked packet JSON file;
- the pilot manifest against the Draft 2020-12 schema with format checking;
- all 24 manifest artifact paths and SHA-256 values;
- all 34 evidence-index paths and SHA-256 values;
- all local Markdown links;
- exact-byte agreement among the nine query files, `translation-spec.json`, and the literal audit;
- all nine required partition IDs, explicit terminal line feeds, and declared null/zero accounting;
- no retained source record, RIS body, result prefix, session/search identifier, cookie, credential, or raw target ID;
- diagnostic-only, no-screening, no-import, and no-final-event invariants;
- `git diff --check`; and
- the shared new-run infrastructure validator.

The dedicated browser had matching runtime/on-disk Chrome `151.0.7922.174`, AC power, active process-scoped `caffeinate -dims` assertions, and no recorded Sleep/Wake event in the live-source window. The postflight health check passed. These checks do not cure the anchor-continuity failure below.

## Source and implementation classification

### E01

E01 is a valid fail-closed diagnostic artifact. The adapter returned its safe “left the authorized Engineering Village search host” error before a reconciled result. Paired, Compendex, and Inspec totals are therefore all `null`; zero records were retained. It is neither an explicit source zero nor evidence of a complete or partial result set.

The safe error omits the final URL class by design. E01 alone cannot distinguish a normal access/redirect boundary from an adapter-owned-page lifecycle defect. For the Engineering Village adapter, **`code_issue=unresolved`** remains the correct classification. The 19 passing focused offline tests do not resolve current live behavior.

### E02 and anchor continuity

E02 must not be used as proof of source access, field behavior, or adapter behavior:

1. it occurred after E01’s terminal unreconciled state, when the source-pilot contract required the subagent to stop;
2. its browser command called the generic harness `new_tab(...)` while the only controlled page was the controller’s new-tab anchor;
3. the current harness implementation intentionally reuses a controlled blank/New Tab page rather than creating a distinct target in that condition (`internet/skills/browser/scripts/lib/browser_harness/helpers.py`, `new_tab`, external repository commit `e720192855f8b5356d92fff23caeb6b8f66bbaf4`); and
4. postflight proves that the same controller anchor target survived but changed from the new-tab URL class to Engineering Village Expert Search. The attempted structured JavaScript inspection also returned only `{}` and established no controls.

Accordingly, the E02 **pilot implementation issue is `true` and its cause is resolved**: an anchor-reusing helper was incompatible with this pilot’s preserve-anchor contract. This does not demonstrate an Engineering Village source failure or an Engineering Village adapter defect, and it does not require changing the general browser helper. A corrective pilot must create a demonstrably distinct owned page and must never use this helper while its reuse condition holds.

## Methodological review

P01 supports no protocol semantic change and no accepted source method.

- The nine root queries are offline, literal-complete drafts only. No live parser, field, phrase, token, stemming, wildcard, proximity, or length behavior was established.
- The broader co-occurrence constructions in pair-bearing drafts are not accepted implementations of the same-field, at-most-five-intervening-token rule.
- Paired source controls, row-level Compendex/Inspec provenance, separate counts, date/language controls, Ei and Inspec thesauri, export, stable identity, pagination, completeness, and explicit zero remain untested.
- The Compendex/Inspec stage of `S-C01` remains wholly unstarted.
- `S-D04`, `TASKS.md`, `search-log.md`, and the Part 2 source index must remain pending.

## Decision required

The review owner retained P01 as blocked evidence and explicitly authorized a new immutable P02 with the following scope:

1. use a fresh dedicated Engineering Village browser/profile or gracefully restart the P01 browser before preflight; never continue from its navigated anchor;
2. complete the full browser/version/power/anchor preflight and preserve the new anchor;
3. use explicit Playwright/CDP target creation—not generic `new_tab(...)`—to create one distinct owned page;
4. navigate that owned page once to the paired Expert route and retain only safe response status, final URL class, expected-host/path, access/challenge categories, and paired-control/query-field booleans;
5. close only the owned page and prove the controller anchor is unchanged;
6. only if that gate is healthy, run one current-adapter short paired diagnostic under a predeclared stop rule to distinguish a transient E01 condition from a reproducible adapter discrepancy;
7. stop immediately after that diagnostic, with `total=null` and no prefix on any failure; and
8. do not run A1–BT2, thesaurus work, export/completeness work, or `S-C01` in this corrective pilot.

If a healthy independent owned-page gate and the current adapter then conflict reproducibly, classify the adapter issue `true` and require a separate code-fix subagent and committed implementation before any further source pilot. If the adapter succeeds, classify E01 as a non-reproduced transient/access transition without retroactively accepting P01.
