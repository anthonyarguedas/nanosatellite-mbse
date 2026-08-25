---
task_id: S-L02
source_id: esa-indico
source_name: ESA Indico
method_type: local_harvest
status: draft_ready_for_supervisor_review
guideline_version: 0.2.0
validated_at: null
protocol_commit: 38ab61287443693ddabdd4bb855d535a4585ae35
accepted_pilot_ids: []
---

# Source-specific guideline: ESA Indico local harvest — draft

> **Draft; not accepted.** This packet does not complete `S-L02`, authorize a final event, screen a record, or import a candidate. P01 and P02 remain immutable historical partial diagnostics. P03 adds current, bounded observations only. The source-free P04 launch bundle is [`p04-execution-plan.md`](p04-execution-plan.md) with [`resume-plan.md`](resume-plan.md); no P04 live observation exists yet. A supervising reviewer must decide whether the draft is sufficiently validated for acceptance and must separately authorize any final run.

## 1. Source boundary and access route

ESA Indico is the sole **local-harvest** source. Its public one-box search is not a lossless Boolean implementation and must never be described as a Boolean-query source.

The intended final boundary is the full public ESA Indico population visible at a frozen snapshot: events, contributions, documented subcontributions when present, event/contribution materials, and confirmed public PDF attachments. The proposed deterministic route chain is:

1. root category export: `/export/categ/0.json?from={date}&to={date}`;
2. event export: `/export/event/{event_id}.json?detail=subcontributions`;
3. static event page: `/event/{event_id}/`;
4. every static contribution owner page: `/event/{event_id}/contributions/{contribution_id}/`; and
5. every separately confirmed public direct PDF route.

P03 materially improves, but does not prove, the root route:

- In November 2023, category 0 returned the exact union of separately queried categories 5 and 6 (eight event IDs). This is a bounded root/component observation, **not** evidence that category 0 recursively covers every public descendant for all time.
- Exact one-day requests behaved as inclusive event-period overlap in this sample: event 472 occurred on 16 November but not 17 November; event 467 occurred on both 16 and 17 November; three long-running events remained on 18 November. A source event date is still not a publication date.
- `1900-01-01` and `2100-01-01` were accepted as bounded zero inputs, so they are candidate sentinels only. A 2020–2024 root probe returned 148 rows with `count=148` in two identical ordered/hash passes. The current response had no usable `complete` flag, so this is not a no-cap or all-time proof.

Official documentation describes category-export URL shape and a `from`/`to` example, but does not document recursive-root behavior, overlap semantics, pagination/caps, or source sentinels. The current Indico category-model documentation confirms that category hierarchies exist, but does not establish ESA's exporter behavior. See [P03 documentation review](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/official-documentation-review.json), [root/component comparison](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/category-root-component-scope-comparison.json), and [cap probe](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/root-cap-probe-2020-2024-reconciliation.json).

Use anonymous public GET only: no credentials, cookies, API key, redirects, HEAD coverage checks, challenge bypass, or login handling. A no-redirect 3xx/401/403/418/challenge is never a source zero. Retain no response body, header, redirect target/query, cookie, token, or browser-tab URL in Git.

## 2. Interface and field behavior

### Public search

The one-box endpoint remains diagnostic only:

- P01 observed `MBSE` event hits while `MBSE AND CubeSat` and `MBSE OR CubeSat` were source zeros. This is sufficient to reject a lossless Boolean characterization, not to infer a complete grammar.
- P01 observed different results for hyphenated versus spaced wording and unavailable (`-1`) totals for several contribution probes. Native punctuation, stemming, expansion, acronym-boundary, field, proximity, and nesting behavior are not used by this method.
- `total=-1` means unavailable, never zero. One-box zeros never become local-harvest source totals.

### Export detail, sessions, and nested records

Official Indico exporter documentation identifies `detail=subcontributions` and case-sensitive `subContributions`; lowercase `subcontributions` is only a compatibility fallback when the documented field is absent. P03 tested a session-bearing event: `detail=subcontributions` produced 62 contribution IDs, exactly the union of the `detail=sessions` top-level and session-held contribution IDs. This validates the selected export for that representative session structure, not all event types ([receipt](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-407-detail-coverage.json)).

No non-empty `subContributions` record was found in 19 successful bounded P03 export-shape observations; one additional sampled event failed closed because one attachment ID had conflicting title metadata ([failure receipt](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-321-export-identity-failure.json)). Do not invent a nested owner/material URL. If any non-empty nested record appears in a final run, generate the bounded manual/browser queue and treat coverage as `null` until a validated owner/material receipt resolves it.

P02 confirmed a legacy `material[].resources[]` object with event ownership. Generic `keywords` are not a controlled vocabulary. No descriptor, index-term field, thesaurus, scope note, hierarchy, or explosion control is validated; no controlled vocabulary is emulated.

## 3. Translation approach and local candidate rule

There is no ESA Boolean translation. The exact local contract is [`local-method-spec.json`](local-method-spec.json), bound to the current concept-dictionary SHA-256. The script requires `--expected-dictionary-sha256` whenever matching is requested and halts on a mismatch.

It deterministically implements `P`, `E_H`, `E_F`, `E`, `M_H`, `M_B`, `M`, `G_model`, `G_structure`, `C1`, independent `R`, and `T2` from the dictionary. It uses NFKC/casefolding, literal lexical tokens, ordered phrases, standalone acronym boundaries, and unordered pair spans with at most five intervening lexical tokens. It does not add synonyms, wildcards, stemming, source expansion, or controlled terms. An architecture span consumed by an artifact expression cannot satisfy independent `R`.

**ESA PDF-content gate:** Event metadata, contribution metadata, keyword values, attachment metadata, and filenames are retained as distinct auditable routes but are `candidate_eligible=false`. They may show diagnostic raw matches only. A candidate partition can be emitted only by one terminal, confirmed public PDF full-text route or its completed OCR full-text route. A public non-PDF remains fully ledgered and needs terminal routing, but cannot itself emit an ESA candidate under this PDF-content constraint unless a future approved route first establishes it as a confirmed PDF. Required terms never combine across event, contribution, attachment, PDF, non-PDF, or separate keyword-value routes.

For each candidate-eligible PDF/OCR document route:

- `core_B = P AND M`;
- `stream_A_tag = P AND E AND M`;
- expansions are `BG1 = P AND G_model`, `BG2 = P AND G_structure`, and `BC1 = P AND C1`; and
- `R`, `T2`, `B2_equivalent`, and `BT2_equivalent` remain independent tags.

The candidate union is `core_B OR BG1 OR BG2 OR BC1`. Raw diagnostic matches, candidate-eligible route counts, source-object unions, partition intersections, tags, and route provenance remain separate. Matching is discovery only and cannot determine eligibility, language, date, publication type, or an included report.

## 4. Controls and common limits

- **Evidence window:** `P-001` has not set the common cutoff. No final run may start. Source event/attachment dates are preserved metadata only and are not used as publication-date limits.
- **Language:** no native English filter. Event metadata cannot prove report language.
- **Discovery limits:** do not filter on publication type, venue, peer review, access, subject, or material type. Public non-PDF and irregular/external material is never silently dropped.
- **HTTP:** anonymous no-redirect GET; at least 0.5 seconds between requests; at most two bounded retries for 408/425/429/5xx. Use GET rather than HEAD: P01 observed HEAD 400 where GET succeeded.
- **Access dispositions:**
  - an explicit protected item is terminal non-public;
  - a static-only/unknown-protection direct link that gets a no-redirect login/restriction result is terminal non-public, not a PDF or zero;
  - an exporter-declared-unprotected item that gets that result is a public-boundary conflict and fails coverage;
  - an unresolved static link, bad media/signature, redirect, parser failure, or access failure is never a match or zero.

P03 rechecked the two historical static-only event-472 links: both remained 302/restricted and were explicitly excluded from the public-PDF path, while 13 other attachment routes were confirmed public PDFs.

## 5. Retrieval, reconciliation, PDF/OCR, and queue procedure

For a final run, first obtain supervisor approval of a root-universe/cap calibration. Freeze the source snapshot, lower/upper calendar sentinels, partition plan, dictionary hash, protocol commit, software versions, and secure workspace reference. Require `count == results.length`, stable non-empty IDs, and event-path agreement for every category window. Preserve every overlapping occurrence and reconcile the event-ID union. Calibrate at least one broad parent window against the union of smaller overlapping child windows; an absent/null `complete` flag cannot substitute for this check.

For every event, require one `detail=subcontributions` result for the requested ID, fetch the static event page and **every** exported contribution owner page, and merge export/static attachment ledgers by stable attachment ID, owner, and canonical path. Preserve export-declared-unprotected IDs separately from the all-route union. Any missing owner-page attachment, conflicting owner/path/metadata, malformed route, or changed content fails that event. P03's event-321 metadata conflict is an observed example of this failure rule.

Probe every same-origin direct material by anonymous no-redirect GET before assigning a public material type. For every confirmed public PDF, separately:

1. GET it with no redirect; validate `application/pdf` and `%PDF-`;
2. save bytes only outside Git; SHA-256 the bytes;
3. run deterministic UTF-8 `pdftotext`; and
4. if deterministic text is empty, run exactly:

```bash
uv run ~/agent-tools/processing/skills/pdf-to-markdown/scripts/pdf_to_markdown.py --input <secure-pdf> --output-path <outside-git-output-dir> --image-mode keep
```

Store only stable IDs, route paths, checksums, byte/count summaries, parser/OCR state, and logical secure references in Git. Strip converter YAML frontmatter before matching OCR body text. The OCR body must reconcile one-to-one to a content-safe completion receipt containing queue ID, PDF checksum, terminal outcome, identified operator, OCR-body hash, and byte count; the script rejects an unmatched OCR file. Any download, checksum, parser, OCR, or reconciliation failure leaves coverage `null`.

P03 completed this entire bounded public-PDF route for event 472: 15 contribution pages, 15 all-route attachments, 13 confirmed public PDFs, 11 non-empty deterministic parses, two completed OCR routes, zero remaining manual items, and matching only after terminal coverage ([summary](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-472-complete-public-pdf-ocr-summary.json), [exact-command OCR receipts](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-472-ocr-exact-command-completion-receipts.json)). This is not a final event and its zero candidate result is not an ESA source zero.

Every public non-PDF needs a supported deterministic extractor or a replayable manual/LLM terminal-text queue. P03 fully traversed event 407's event page and 62 contribution owner pages, reconciled 112 attachments, and no-redirect classified 28 public videos as non-PDF. It generated all 28 queues. A content-free receipt for one video with `unsupported_media_no_text_extractor` was rejected as incomplete by the validator; the route was not silently treated as no-match ([summary](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-407-nonpdf-owner-reconciliation-summary.json), [validation](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-407-nonpdf-7873-receipt-validation.json)). No irregular/external export route was observed in the bounded successful P03 scans; the failure-closed queue remains required for one if encountered.

## 6. Stable identity and completeness

Use:

- event: `event_id`;
- contribution: `event_id:db_id` where available, otherwise `contribution_id` or `id`;
- subcontribution: `event_id:parent_contribution_id:subcontribution_id`;
- attachment: attachment ID **plus** owner and canonical path; and
- full-text document: attachment identity plus exact PDF checksum and route type.

A repeated ID with a different owner, path, relevant metadata, or byte hash is a failure, not a deduplication shortcut. Keep raw discovery occurrences and route provenance until all pass-level checks are complete.

A final event requires two fresh anonymous passes with equal category counts/order, event/contribution/subcontribution IDs, export/all-route attachment ledgers, direct-PDF checksums, parser/OCR/manual terminal states, and PDF-only matching output. A changed/disappeared object requires a new snapshot and a `null` failure rather than merging a prefix.

P03's complete event-472 route validates the terminal PDF/OCR mechanism once. It does **not** replace the required final two-pass census or the final all-public source-universe proof.

## 7. Failure and zero rules

A zero is valid only for a complete reconciled **declared bounded operation** whose native count is exactly zero. P03's two sentinel zeros are bounded interface observations, not source totals. `total=-1`, a cap ambiguity, an access issue, an unreconciled material, a queue failure, or a partial prefix is never zero.

Set coverage/source total to `null` and import nothing when any root-boundary, cap/calibration, count/row, identity, owner-page, material, access-conflict, direct-PDF, checksum, parser/OCR, manual receipt, or A/B reconciliation requirement fails. An explicit non-public protected/restricted disposition is retained in the ledger; it does not become a public PDF. A public non-PDF without terminal routing remains coverage `null`. The observed event-321 conflicting attachment title is an explicit identity failure, not a correction to be silently merged.

## 8. Final-run procedure

Do not execute before `P-001`, guideline acceptance, root-boundary/cap approval, and `R-002` authorization.

1. Freeze protocol/dictionary hashes, cutoff, snapshot, source sentinels, window plan, tool versions, and secure storage.
2. Calibrate root windows, then run and reconcile category pass A. Halt on any count/row, cap, identity, or boundary failure.
3. For every event, request `detail=subcontributions`, check any sessions calibration rule specified for the run, fetch static event and every contribution owner page, and reconcile every material identity.
4. No-redirect probe all direct routes. Classify public PDF, public non-PDF, terminal non-public, and declared-public access conflict separately.
5. Download/hash/extract/OCR every confirmed public PDF. Resolve every public non-PDF, irregular/external, and nested queue to a terminal receipt. Match only eligible terminal PDF/OCR text routes after complete coverage.
6. Repeat the full operation as pass B from a fresh anonymous client. Require exact declared reconciliation; otherwise record `null` and no import.
7. Only after every gate passes may the authorized operator create final-event artifacts. Candidate discovery then remains subject to normal later screening.

## 9. Validation evidence

P01/P02 remain limited historical/correction evidence. P03 is a new current-run, diagnostic-only packet:

- [official documentation review](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/official-documentation-review.json);
- [root-date and cap reconciliation](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/category-root-window-reconciliation.json) and [148-row cap probe](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/root-cap-probe-2020-2024-reconciliation.json);
- [sessions/subcontributions coverage check](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-407-detail-coverage.json);
- [complete bounded PDF/OCR route](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-472-complete-public-pdf-ocr-summary.json) with [exact-command OCR receipts](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-472-ocr-exact-command-completion-receipts.json);
- [public non-PDF queue/failure check](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-407-nonpdf-owner-reconciliation-summary.json); and
- [event-321 identity failure](pilots/S-L02-P03-20260823T135313-0400/safe-receipts/event-321-export-identity-failure.json).

The focused implementation tests in [`SLR/SLR1/scripts/test_esa_indico_local_harvest.py`](../../../scripts/test_esa_indico_local_harvest.py) test the code's deterministic behavior, including dictionary locking, PDF-only candidate gating, access dispositions, OCR ingestion, bounded attachment prefixes, nested-route receipt requirements, and queue rejection. They do not prove live source-wide completeness. The compatibility [`translation-spec.json`](translation-spec.json) and nine `queries/*.esa-local.txt` files are audit contracts only: ESA's one-box interface has no accepted Boolean translation, and the normative local matcher remains `local-method-spec.json`.

## 10. Remaining limits and protocol impact

No concept block, Boolean relationship, planned source, evidence window, or eligibility rule changes here. ESA remains a local-harvest source. The PDF-only candidate gate is a source-specific implementation safeguard required by ESA's material behavior; a supervisor should confirm it before acceptance.

The remaining acceptance/final-run blockers are: all-public category-0 recursion and sentinel/cap proof; final two-pass all-time census; a non-empty nested-material route; terminal routing for all public non-PDF and a real irregular/external route; resolution/failure handling for every identity conflict; final two-pass PDF/OCR coverage; `P-001`; and supervisor acceptance. P04 is deliberately limited to the fixed twelve-event nested/irregular shape search and at most two selected-event queue traversals in [`p04-execution-plan.md`](p04-execution-plan.md); it must not widen into a census. Until the blockers are resolved, report ESA as a draft diagnostic method, never as a completed source or a partial final prefix.
