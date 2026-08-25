---
task_id: S-D04
source_id: engineering-village-compendex-inspec
source_name: Compendex and Inspec through Engineering Village
method_type: direct
status: draft_blocked
guideline_version: 0.1.0
validated_at: null
protocol_commit: 8ebc1c162e919d1e8dcdb815a573d14dc0459dce
accepted_pilot_ids: []
---

# Source-specific guideline: Compendex and Inspec through Engineering Village

**DRAFT — blocked and not accepted for a final search.** Claim labels are **[observed]**, **[official_documentation]**, **[inferred]**, and **[untested]**. No pilot record was screened or imported.

## 1. Source boundary and access route

- **[inferred]** `S-D04` is one deliberate Engineering Village event with **Compendex and Inspec selected together**, while preserving each database's row-level provenance and separate count. It is not a Compendex-only event and it must not include All databases or Knovel.
- **[observed]** E01 invoked the pinned Engineering Village adapter in paired `compendex inspec` Expert mode, using only its normal rendered-route/RIS workflow. It stopped before a reconciled result page with an ownership/source-host error; it produced no source total, row, identifier, or RIS export. See [`E01-paired-known-title.status.txt`](pilots/S-D04-P01-20260824T123301-0400/E01-paired-known-title.status.txt) and [stderr](pilots/S-D04-P01-20260824T123301-0400/E01-paired-known-title.stderr.txt).
- **[observed]** E02 reached the public Expert Search route title without submitting a query. The controller anchor target remained present but its URL class changed from the preflight new-tab class; no further source interaction, navigation, restoration, or closure was attempted. See [`browser-postflight.json`](pilots/S-D04-P01-20260824T123301-0400/browser-postflight.json).
- **[untested]** Current authorization to retrieve paired search results, retained paired selection, source scope summary, row-level labels, separate totals, and source-boundary reconciliation are not established. This is not recorded as a login, CAPTCHA, or explicit source denial because none was observed.

## 2. Interface and field behavior

- **[observed]** The public Expert Search route loaded by title only; no current query field/control/field-scope observation is accepted from it.
- **[untested]** Exact free-text field(s); Expert syntax; parentheses and precedence; quoted phrases; punctuation and hyphen handling; token-boundary behavior for acronyms; wildcard behavior; stemming, lemmatization, or expansion; query echo/rewrite; proximity; query length; and source syntax-failure behavior all remain unvalidated.
- **[untested]** Separate genuine Compendex and Inspec thesaurus/indexed-term surfaces, scope notes, hierarchy/narrower terms, explosion/mapping, and known-record descriptor assignment were not inspected. No descriptor is accepted. A generic systems-engineering term could never satisfy MBSE by itself.
- **[official_documentation]** No current official documentation was successfully collected in this blocked pilot. The local adapter/domain note is implementation context, not accepted source documentation.

## 3. Translation approach

- **[observed]** [`translation-spec.json`](translation-spec.json) maps A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2 to one UTF-8 draft cell each. [`translation-literal-audit.json`](pilots/S-D04-P01-20260824T123301-0400/translation-literal-audit.json) verifies that every required dictionary literal is present and no S-C01 candidate term was added.
- **[inferred]** The cells use fully parenthesized Boolean groups and quoted literals as a prospective unqualified Expert Search free-text form. They are not accepted current source-native translations because E01 did not reach a parser-confirmed result page.
- **[inferred]** Pair cells use broader left-group/right-group Boolean co-occurrence only to preserve every literal offline. They do **not** implement or prove the required unordered, same-field, <=5-intervening-token rule. A later pilot must validate a native proximity form or a documented non-lossy same-field fallback before accepting BG1, BG2, BC1, or BT2.
- **[untested]** Query-length support is unknown. No cell was split; a later observed limit requires a prospective lossless stable-identity union with every cell completed independently.

## 4. Controls and common limits

- **[inferred]** A later diagnostic may test 2011-01-01 through 2026-08-24 only as a pilot-execution-date upper bound. It is not P-001 or a final common cutoff.
- **[untested]** Source-side date precision, English/language controls, source deduplication state, ordering, and source-reported versus client-side filtering were not tested.
- **[inferred]** The draft adopts no publication-type, access, peer-review, venue, content-type, or major-topic discovery limit. A source boundary does not prove report language or publication type.

## 5. Retrieval, pagination, and export

- **[untested]** Current page-size options, sort behavior, paired row provenance, pagination, native RIS/export controls/cap, export-to-row reconciliation, rights boundary, and source caps were not reached.
- **[inferred]** A later successful paired event must retain only safe diagnostic metadata in Git and keep licensed rows/RIS/raw captures under the source/pilot-specific restricted root. It must distinguish portal totals from retrieved rows and retain no partial prefix.
- **[observed]** The restricted-capture ledger records zero captures because E01 stopped before source results or export. See [`restricted-capture-ledger.json`](pilots/S-D04-P01-20260824T123301-0400/restricted-capture-ledger.json).

## 6. Stable identity and completeness

- **[untested]** No stable Engineering Village/Compendex/Inspec identifier, missing-ID behavior, duplicate-source-record behavior, cross-database identity relationship, or page order was observed.
- **[inferred]** A final event needs database-scoped stable accessions, one-to-one row/RIS reconciliation, separate Compendex/Inspec ledgers and counts, unchanged total/order, and two complete passes or an equivalent validated proof. DOI/title fallback must not hide a missing source ID.

## 7. Failure and zero rules

- **[observed]** E01 is a failed/blocked diagnostic with `total=null` and zero records retained. Its adapter-safe error is not an explicit source zero.
- **[inferred]** Treat access, login/challenge, source-boundary, query, control, total, range, page, provenance, RIS/export, parsing, identity, or completeness discrepancies as `total=null`; preserve only safe evidence and import no prefix.
- **[inferred]** Record `total=0` only after an explicit, reproducible native zero with confirmed paired source selection and controls. Never infer a Compendex or Inspec zero from a combined prefix or an adapter error.

## 8. Final-run procedure

Do not execute a final event from this guideline.

1. **[inferred]** Obtain controller/human approval for a fresh, isolated browser preflight because this pilot has an unreconciled owned-page/source-host discrepancy and anchor URL-class incident.
2. **[inferred]** In a new authorized pilot, validate the paired Expert controls, field scope/syntax, parser echo, proximity, date/language controls, separate thesaurus/indexed-term mappings, explicit zero, and safe failure behavior before any final cells.
3. **[inferred]** Validate a nonzero paired result's row-level Compendex/Inspec provenance, separate counts, page-size/order, native RIS route/cap, IDs, and two-pass completeness without source deduplication masking provenance.
4. **[inferred]** Only after those gates, execute each accepted A1–BT2 cell under the eventual P-001 cutoff, preserve complete database-scoped identity ledgers/cell totals, and reconcile lossless unions. Pilot results remain diagnostic and never enter final-events or screening.

## 9. Validation evidence

- **[observed]** The blocked pilot manifest and safe evidence are under [`pilots/S-D04-P01-20260824T123301-0400/`](pilots/S-D04-P01-20260824T123301-0400/), especially [`controller-preflight-summary.json`](pilots/S-D04-P01-20260824T123301-0400/controller-preflight-summary.json), [`adapter-assessment.json`](pilots/S-D04-P01-20260824T123301-0400/adapter-assessment.json), and [`browser-postflight.json`](pilots/S-D04-P01-20260824T123301-0400/browser-postflight.json).
- **[observed]** The external adapter is pinned in [`adapter-provenance-preflight.txt`](pilots/S-D04-P01-20260824T123301-0400/adapter-provenance-preflight.txt); its focused offline suite passed 19 tests in [`focused-adapter-tests.stdout.txt`](pilots/S-D04-P01-20260824T123301-0400/focused-adapter-tests.stdout.txt). That does not validate the live portal.
- **[observed]** `code_issue=unresolved`, not true or false: the safe adapter error omits the final URL class, and the direct title-only route observation cannot distinguish a native redirect/access boundary from an adapter-owned-page lifecycle defect. No patch was made.
- **[observed]** S-C01 has not begun: no frozen local register, B1∪B2 baseline, candidate-family query, term-use coding, screening, or import exists. See [`candidate-stage-status.json`](pilots/S-D04-P01-20260824T123301-0400/candidate-stage-status.json).

## 10. Remaining limits and protocol impact

- **[observed]** This pilot is blocked by unreconciled source-boundary/adapter-owned-page behavior. The preflight anchor target remained, but its URL class changed, which requires controller/human operational review before another browser pilot.
- **[untested]** All source acceptance requirements beyond literal-completeness of the offline drafts remain untested, including all nine source cells, paired counts/provenance, controls, controlled vocabulary, pagination/export, identity, completeness, and candidate terminology.
- **[inferred]** No protocol semantic change is proposed. The dictionary/Boolean schedule and candidate terminology remain unchanged; the limitation is interface/operational validation, not a basis to change scope or terms.

## Future browser operations

Historical per-source endpoint/profile facts remain immutable evidence. All future browser phases use the global shared CfT lease at `127.0.0.1:9222`; do not reinterpret historical observations.
