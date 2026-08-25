# Controller review — Engineering Village corrective pilot P02

**Reviewed:** 2026-08-24T13:39:37-04:00  
**Disposition:** blocked; not accepted; no P03 or final search authorized.

This is a controller review, not an approval record. P02 remains immutable at [`S-D04-P02-20260824T130842-0400`](pilots/S-D04-P02-20260824T130842-0400/).

## Independent validation

Controller checks passed for:

- all 21 tracked P02 JSON files;
- the manifest against the Draft 2020-12 schema with format checking;
- all seven manifest artifact paths and SHA-256 values;
- all 28 evidence-index paths and SHA-256 values;
- the restricted-inventory path and checksum;
- all local Markdown links;
- null accounting for paired, Compendex, and Inspec totals and zero retained records;
- diagnostic-only, no-screening, no-import, and no-final-event invariants;
- no retained raw anchor ID, websocket URL, credential, cookie, session/search identifier, source record, export, or result prefix;
- the unchanged Part 2 context and fixed P02 write boundary;
- `git diff --check`; and
- the shared search-infrastructure validator.

The dedicated browser had matching Chrome runtime/on-disk versions, AC power, active process-scoped sleep assertions, and no bounded Sleep/Wake marker. Postflight independently proved that the original controller anchor remained the sole New Tab page.

## Gate and implementation classification

### G01

G01 successfully resolved P01’s anchor-handling problem. It proved one browser context, one private controller New Tab anchor, one distinct `context.new_page()` target, one route-navigation attempt, closure of only the owned page, and restoration to the unchanged sole anchor.

The navigation returned HTTP 200, but the immediate safe JavaScript projection raised during the inspection phase. The receipt therefore correctly records no final host/path, access state, title, source control, or query-field observation. HTTP status alone cannot satisfy the gate.

The projection source parses successfully as JavaScript in an independent offline syntax check. The underlying live runtime cause remains unknown because the P02 script intentionally collapsed the exception to `safe_inspection_failed`. A transient execution-context replacement after `domcontentloaded` is plausible but unproved.

The **P02 pilot-local probe implementation issue is `true`**: it attempted the safe projection only once, immediately after `domcontentloaded`, and retained no bounded passive stabilization or fixed runtime-failure subclass. Consequently it could not distinguish a transient client-rendered context replacement from a durable page/runtime failure. This classification concerns the P02 diagnostic implementation, not Engineering Village and not the current search adapter.

### G02 and adapter

G02 correctly did not run because G01 was not healthy. Adapter invocation count is zero, no source query was submitted, and all source totals remain `null`.

For the current Engineering Village adapter, **`code_issue=unresolved`** remains correct. P02 neither reproduced nor cleared P01 E01, and no source/access failure was established.

## Methodological impact

P02 supports no protocol semantic change and no accepted source method. It establishes only safe owned-page/anchor mechanics. Paired controls and checked states, source access, fields and syntax, date/language controls, Ei and Inspec thesauri, row provenance, separate counts, export, identity, pagination, completeness, explicit zero, A1–BT2, and `S-C01` all remain untested. `S-D04` and all central status files must remain pending.

## Decision required

No retry is authorized by this review. If the review owner wants to continue, the smallest defensible next sequence is:

1. a separate offline code-fix/review step for a prospective owned-page probe that preserves P02’s one-navigation rule but adds a bounded passive post-navigation stabilization loop, retries only execution-context replacement/ongoing-navigation inspection failures without reloading, classifies `page.url` safely in Python, and records fixed error subclasses without raw exception or URL leakage;
2. focused offline tests for distinct-page ownership, anchor preservation, safe URL classification, transient inspection retry, persistent bounded failure, and no second navigation;
3. after that implementation is reviewed and pinned, explicit human authorization for a new immutable P03 on a fresh dedicated browser;
4. P03 runs the corrected non-query gate once and, only if healthy, the same one authorized current-adapter paired diagnostic; then stops without A1–BT2, thesaurus, completeness, or `S-C01` work.

A healthy corrected gate followed by the same P01 adapter host/lifecycle failure would make the adapter issue `true` and require a separate adapter fix before further source work. A successful adapter invocation would classify P01 E01 as a non-reproduced transient without retroactively accepting either earlier pilot.
