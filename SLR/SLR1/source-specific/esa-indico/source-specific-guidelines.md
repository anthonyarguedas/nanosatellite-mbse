# ESA Indico

Last pilot saved in commit: 61efaed6dee07616a3ca33bf30078098878e5eb8
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. A compact persisted failure may omit attachment or candidate-snapshot detail. A linked pilot receipt must distinguish that omission from a source value. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: ESA Indico
- Interface: Web
- Platform: European Space Agency Indico
- URL: https://indico.esa.int/
- Search field or local route: Complete bounded local harvest from category 0 with the deterministic local matcher. Do not use rendered `q` as a Boolean search.
- Main evidence window: Do not restrict the harvest by event date. Apply the evidence window to candidate reports after retrieval.
- Language: ESA exposes no Language filter or language parameter. Apply no source language filter and determine English from the full text during screening.
- Publication type: ESA exposes event, contribution, and material groups rather than a lossless eligible report type filter. Apply no type, peer-review, access, or full-text-availability filter.
- Database or collection selection: Category 0 across Events, Contributions, Subcontributions, and Materials. Preserve stable attachment IDs, parent scope, folder IDs, declared metadata, protection or access metadata, and exact public download URLs.
- Other shared limits: The local-harvest deadline defaults to 1,200 seconds and must stay within the adapter's 5 to 1,800 second bound. Each browser request remains bounded to 300 seconds. Keep root and event exports sequential. The complete ledger accepts at most 10,000 events, 50,000 normalized metadata records, and 64 MB of canonical sidecar JSON. Source JSON stays under 100 MB. Standard local and complete mode makes no attachment body request.

## Durable local-harvest recovery

A complete metadata harvest requires two matching ordered category-0 event
snapshots, every event export, and complete normalized Event, Contribution,
Subcontribution, and Material metadata. Attachment metadata includes a stable
attachment ID, parent event scope, folder ID, title, filename, description,
MIME, size, checksum when supplied, modified date, protection or access
metadata, and the exact public download URL. Attachment byte or text access is
not a completion, merge, or matching condition. Notes and Categories are not
covered by the local harvest. Do not use a successful Events, Contributions,
and Materials run to claim Notes or Categories coverage.

The local matcher uses only declared metadata. Events and Contributions use
title, description, and keywords. Materials use title, filename, and
description. Phrase and proximity matching stays within one declared field.
It never uses attachment bytes, extracted text, a hash, MIME, or a retrieval
status. A record with insufficient content remains a metadata candidate. The
screening workflow decides full text access, language, and eligibility.

A failed metadata harvest is not mergeable. Its compact JSON artifact has only
a path-free checkpoint descriptor in `failure_diagnostics`. The durable sibling
sidecar is published with the JSON and terminal marker as one create-only
transaction. Staged JSON and CSV bytes are fsynced, the authorized output
directory is fsynced after each required hard link, and the terminal marker is
linked last. Resume only with `--resume-from` or `--resume-state-path` against
the marker-bound failure artifact or sidecar. ESA adapter v8 requires its
registered terminal marker. A markerless ESA artifact is not accepted for
merge or resume. The adapter checks the sidecar hash and schema, deterministic
sibling basename, exact bounded expression, category, compatible effective
controls, ordered candidate IDs, contiguous completed prefix, route and source
ID linkage, and metadata digest before it retries work. Every non-deadline
control must match. The total deadline may only increase. It re-exports
completed event metadata. It makes no attachment body request during resume.

A successful v8 harvest publishes a separate marker-bound metadata ledger with
the compact query result. The ledger retains every normalized Event,
Contribution, Subcontribution, and Material record, including records that do
not match the current expression. It retains stable identities, attachment
parent and folder identity, public URLs, declared MIME, size, checksum, access
state, both root snapshot ledgers and hashes, event-export witnesses, source
ordering, controls, and matcher scope. It contains no attachment body or
extracted content. Merge, report, source-union, and event gates recompute the
ledger evidence and match compact result IDs against it.

The sidecar retains bounded normalized metadata, source states, and the next
event index. It never retains response bodies, attachment bytes, extracted
attachment text, content cache entries, cookies, session data, raw headers,
browser or CDP identifiers, local paths, or temporary filenames. A missing
sidecar, changed marker, mismatched hash, changed query, changed category, or
changed non-deadline control is a failure that is not mergeable. A shorter
deadline also fails. An explicit deadline extension is the only compatible
control change. It is not a restart shortcut.

Retry only public timeout or connection failures and HTTP 408, 429, 500, 502,
503, and 504 for category and event metadata routes. Honor a bounded
`Retry-After` and the shared source-wide 429 backoff. Do not infer a negative
match from a protected, missing, redirected, oversized, unsupported, or
unparseable attachment body. Retain its metadata and a downstream retrieval
status when known. Malformed or contradictory attachment identity or metadata
remains a strict metadata error. Optional bounded content extractors are
outside search execution. They are diagnostic or downstream enrichment only.
Their output and failure state cannot change source totals, candidate IDs,
local matches, metadata completion, merge eligibility, or report readiness.

Pilot 005 and every file beneath `pilots/005/` are immutable historical
evidence. Do not edit, compact, or resume from its old embedded checkpoint.
Pilot 005 records an overstrict v7 attachment-content failure. It does not
prove a live platform coverage failure or zero results. See the
[metadata-only contract supersession note](metadata-only-contract-supersession.md).
Run
`../../scripts/esa_indico_pilot005/validate_pilot.py` before relying on the
historical receipt boundary. The validator is read-only. It checks `git diff
HEAD` and porcelain status, including staged and untracked entries, for the
Pilot 005 tree and rejects symlink or nonregular evidence before parsing it.

## Source translation

Use the exact concept membership and compound Boolean declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared compound. Keep exact local expressions normative and use no wildcard in them. A diagnostic candidate may use only the local trailing one-token `*`, which adds broader recall and requires set evidence before adoption. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal. The local matcher tokenizes it with NFKC, case folding, and lexical boundaries.
- Atom `A(s)`: `L(s)` in the local matcher expression.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Compound blocks: Render `F(G_model)` as `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))`. Render `F(G_structure)` as `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))`. Render `F(C1)` as `F(C1_fixed) OR F(G_DSL)`. Fully parenthesize each compound. No proximity or pair expansion is used.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitations: Rendered `q` is a prefix-AND search and cannot express the Boolean schedule. ESA exposes no Language control, and event/contribution/material groups do not map losslessly to the shared eligible report types. Use the bounded local metadata harvest for exact Boolean and phrase matching. Pilots 003 and 004 timed out at the category-0 event-universe route. Pilot 005 failed under the superseded v7 attachment-content rule. Pilot 006 completed the v8 metadata route with two matching 440-event snapshots and 16,517 normalized records. Its exact A1 expression matched zero records. Pilot 007 then executed all nine current expressions over that fixed ledger. The schedule returned 24 distinct metadata records. This establishes schedule behavior on the fixed corpus and does not complete the final search.
- Unavailable controls: ESA has no source-side date limiter, rendered phrase/proximity control, or lossless type/access/full-text filter. Its Category tree is an organizational scope rather than controlled vocabulary. No descriptor supplement, hierarchy explosion, or vocabulary restriction is applied. ESA has no native complete search export. The local public category and event metadata export is used only under its two-root-snapshot and complete-metadata contract. Attachment download routes are retained for downstream retrieval, not fetched for search execution.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render them with the source operators above. `F(G_model)`, `F(G_structure)`, and `F(C1)` use the exact compound definitions above. `F(T_precise)` is an ordinary literal block.

| ID | Source construction |
|---|---|
| `A1` | `F(P) AND F(E_H) AND F(M_H)` |
| `A2` | `F(P) AND F(E_F) AND (F(M_H) OR F(M_B))` |
| `A3` | `F(P) AND F(E_H) AND F(M_B)` |
| `B1` | `F(P) AND F(M_H)` |
| `B2` | `F(P) AND F(M_B) AND F(R)` |
| `BG1` | `F(P) AND F(G_model)` |
| `BG2` | `F(P) AND F(G_structure)` |
| `BC1` | `F(P) AND F(C1)` |
| `BT2` | `F(P) AND F(M_B) AND F(T_precise)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): exact local A1, BG1, and `NEAR/5` parsing passed. The shorter wildcard candidate remains unaccepted because it broadens recall.
- [x] [Pilot 002](pilots/002/pilot.md): rendered `q` cannot express the Boolean schedule, and ESA exposes no Language filter.
- [x] [Pilot 003](pilots/003/pilot.md): category-0 harvest timed out before event retrieval. Fixture checks passed but do not establish source coverage.
- [x] [Pilot 004](pilots/004/pilot.md): the fresh category-0 event-universe retry timed out before an HTTP response. It is systematic endpoint evidence, not zero coverage.
- [Pilot 005](pilots/005/pilot.md): immutable evidence of an overstrict v7 attachment-content failure. One repaired category-0 local attempt reached attachment collection but failed before local matching and root confirmation. All nine exact schedule expressions are bound to the same historical failure through null receipts. This does not prove live platform coverage failure or zero results. It does not complete the source or a final search.
- [x] [Pilot 006](pilots/006/pilot.md): the repaired v8 metadata route completed exact A1 over two matching 440-event snapshots and 16,517 normalized records. A1 returned a verified zero.
- [x] [Pilot 007](pilots/007/pilot.md): all nine current expressions ran over the marker-bound Pilot 006 ledger. The partition totals were A1 0, A2 0, A3 0, B1 22, B2 2, BG1 0, BG2 1, BC1 2, and BT2 0. Their union contained 24 distinct metadata records. The final search remains unexecuted.
