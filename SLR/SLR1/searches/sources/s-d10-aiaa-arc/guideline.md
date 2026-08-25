---
task_id: S-D10
source_id: aiaa-arc
source_name: AIAA Aerospace Research Central (ARC)
method_type: direct
status: draft_p01_unvalidated
guideline_version: 0.1.0
validated_at: null
protocol_commit: b25b91fe63d77490be1a52aaf93d4d09c2836e4d
accepted_pilot_ids: []
---

# Source-specific guideline: AIAA Aerospace Research Central (ARC)

> **Two-mode validation:** Apply the [current policy](../../two-mode-validation-policy.md). First use agent-driven exploration to make the real interface work; then use a separate frozen deterministic evidence attempt. Exploration findings guide implementation but do not pass acceptance gates.


> **Draft only; final use is prohibited.** This source is brand new in this packet. No ARC pilot has been run here, no current-interface behavior is claimed, and no campaign or attempt is checkpointed. The initial campaign and manifest must be instantiated from the shared templates at runtime immediately before P01 source work.

## 1. Source boundary and access route

- **[protocol]** S-D10 is the separate required event for the full publisher-hosted AIAA Aerospace Research Central collection. Keep its source total separate from every other source; do not substitute an AIAA paper page, another index, or a narrower publication set.
- **[official_documentation]** The local ARC domain note identifies the normal Advanced Search route as `https://arc.aiaa.org/search/advanced`, with its normal GET action at `/action/doSearch`; it documents `field1=AllField` as the Anywhere field. This is local documentation, not a P01 current-interface observation.
- **[inferred from adapter code]** `search_aiaa_arc.py` attaches to the shared loopback CDP endpoint by default, creates an adapter-owned page, and leaves an operator page untouched. The normal shared owned-page route does not require `--target-id` or `--result-url`. P01 must stop if the adapter reports ambiguous browser contexts, an unsafe route, or any ownership/cleanup failure; it must not add a target ID or result URL as an improvised workaround.
- **[untested]** Current anonymous/authorized access, collection boundary as rendered, route reachability, challenge state, and any login or institutional-access requirement.

## 2. Interface and field behavior

- **[official_documentation]** The local ARC note lists `AllField`, `Title`, `Contrib`, `Keyword`, `Abstract`, and `Affiliation` as documented Advanced Search field choices. The translation in [`translation-spec.json`](translation-spec.json) uses only `field1=AllField` and places the exact cell in `text1`.
- **[inferred]** The nine cells use fully parenthesized uppercase `AND`/`OR` Boolean expressions and one double-quoted atom for every finite dictionary literal. This is a source-native syntax candidate generated offline, not accepted parser evidence.
- **[untested]** Current query echo or rewrite, Boolean precedence, phrase order, punctuation and hyphen normalization, acronym token boundaries, case, stemming, lemmatization, automatic expansion, wildcard behavior, malformed-query handling, proximity, and query-length limits.
- **[untested]** A genuine controlled vocabulary or usable indexed-term supplement. A visible/documented `Keyword` field is not by itself a thesaurus, descriptor assignment, hierarchy, scope note, or explosion facility. No descriptor is accepted; free text remains mandatory and generic `systems engineering` cannot replace `M_H`.

## 3. Translation approach

[`translation-spec.json`](translation-spec.json) is the exact offline translation specification. It maps the current dictionary's nine direct partitions to one lossless UTF-8 AllField cell each:

- `A1`, `A2`, `A3` — Stream A;
- `B1`, `B2` — core Stream B; and
- `BG1`, `BG2`, `BC1`, `BT2` — expanded Stream B.

The query files are [`queries/A1.aiaa-allfield.txt`](queries/A1.aiaa-allfield.txt), [`queries/A2.aiaa-allfield.txt`](queries/A2.aiaa-allfield.txt), [`queries/A3.aiaa-allfield.txt`](queries/A3.aiaa-allfield.txt), [`queries/B1.aiaa-allfield.txt`](queries/B1.aiaa-allfield.txt), [`queries/B2.aiaa-allfield.txt`](queries/B2.aiaa-allfield.txt), [`queries/BG1.aiaa-allfield.txt`](queries/BG1.aiaa-allfield.txt), [`queries/BG2.aiaa-allfield.txt`](queries/BG2.aiaa-allfield.txt), [`queries/BC1.aiaa-allfield.txt`](queries/BC1.aiaa-allfield.txt), and [`queries/BT2.aiaa-allfield.txt`](queries/BT2.aiaa-allfield.txt). Every file is one terminal-LF UTF-8 cell generated from `slr1-search-concepts/v4`; no candidate terminology, wildcard compression, term deletion, or semantic narrowing was introduced. All cells are below the adapter's offline 50,000-character input ceiling, so no shard is required.

- **[untested]** ARC parser acceptance and field scope for every cell. No source total is assigned in the specification.
- **[blocked]** `BG1`, `BG2`, `BC1`, and `BT2` retain explicit Boolean pair cross-products only to preserve every literal. A Boolean conjunction is broader than the required unordered same-field pair with at most five intervening lexical tokens. Do not use a pair-bearing cell for a final search until ARC-native pair semantics or a recall-preserving same-field construction is validated; if neither is possible, record the limitation and apply exact local matching only where retained fields permit it.

## 4. Controls and common limits

- **[protocol]** The evidence window starts at 2011-01-01 and ends at the exact common cutoff selected under P-001. P-001 remains unresolved.
- **[inferred]** P01 uses the actual pilot execution date as a diagnostic upper bound only. The adapter maps exact dates to ARC month controls and records an exact-day disposition for retrieved RIS dates; this pilot bound is not P-001 and must never be reused as the final cutoff.
- **[protocol]** Do not impose a native-English, publication-type, access, peer-review, venue, content-type, major-topic, or convenience limit during discovery. ARC's all-content `access=on` route is a route control, not a scientific eligibility restriction. Full-report English status remains a screening/retrieval decision.
- **[inferred from adapter code]** The adapter expects visible Relevance ordering and a fixed 20-record page, and records the exact rendered `Search Results (N)` total before any client-side exact-day exclusion. Current visible control behavior, date precision, native zero state, and source caps remain untested.

## 5. Retrieval, pagination, and export

- **[planned]** P01 first runs one count-only `B1` operation. It retains no bibliographic rows and tests only a first rendered page, exact total, route/date/control evidence, and DOI-row hydration.
- **[inferred from adapter code]** A conditional bounded retrieval diagnostic can use the same non-pair `B1` cell when the count is between 1 and the fixed P01 cap of 20. The adapter follows the normal visible per-record Tools → Download citation → RIS flow and reconciles returned RIS to rendered DOI values. It does not use ARC's formatted bulk citation modal as a RIS route.
- **[untested]** Current page transitions, source-total/range reconciliation, ordering stability, DOI coverage, visible citation form, RIS bytes, export selection, and native export behavior. Non-strict P01 output is diagnostic and non-mergeable; it is not a final normalized output or import source. Do not force the adapter's fixed-cap `--require-complete` contract during P01.
- **[protocol]** Keep any licensed source captures or native exports outside Git in the approved restricted location. Store only safe receipts and hashes in the packet after the attempt.

## 6. Stable identity and completeness

- **[inferred]** ARC DOI values are the adapter's proposed stable record identity. A successful bounded diagnostic must find exactly one nonempty DOI per rendered row and reconcile each retained RIS record to that DOI. A missing, duplicate, changed, or mismatched DOI is a failure, not a guessed fallback.
- **[untested]** DOI persistence and uniqueness across pages, stable Relevance order, full pagination, two-pass agreement, exact source-total exhaustion, and any DOI-less fallback.
- **[protocol]** A final event requires every accepted partition to retrieve the complete source result set and, where stable order is exposed, two complete identical ordered-ID passes. P01's one-pass bounded diagnostic cannot establish completeness and cannot import a prefix.

## 7. Failure and zero rules

- **[protocol]** A successful native ARC zero is `total=0` only when the rendered page explicitly and reproducibly reports zero with no result rows or identifiers. Access, challenge, login, syntax, query rewrite, control, total, range, page, identity, export, parsing, or completeness failures require `total=null`; no partial prefix is imported.
- **[inferred from adapter code]** The adapter passively waits only within its finite `--timeout`; it does not solve, click, reload, or bypass a challenge. P01 preauthorizes no same-tab busy reissue. A challenge or ordinary busy/service state that does not resolve inside the declared bound stops the attempt and remains null.
- **[planned]** Every operation has a unique absent output path. The adapter derives its record-free sidecar by removing the requested `.json` suffix and appending `.NON_MERGEABLE_FAILURE.json` (for example, `op-01-count-b1.NON_MERGEABLE_FAILURE.json`). The sidecar is the only accepted P01 output; a successful non-count-only non-strict diagnostic has the intentional adapter exit 1 and is accepted only with its validated record-free aggregate sidecar. Collisions, symlinks, marker collisions, any other exit/sidecar outcome, or unverified cleanup are hard stops.

## 8. Final-run procedure

Do not execute a final ARC event from this draft. Before R-002, complete and accept the campaign, resolve any methodological decision, complete P-001, and revalidate all required gates. The later operator must:

1. create a new final-run manifest under the shared protocol and obtain the shared CfT lease at `127.0.0.1:9222`;
2. verify the fixed browser/profile/anchor/power/sleep health and one owned-page cleanup contract;
3. run every accepted partition with the exact common cutoff, validated AllField/parser/pair/controlled-term behavior, and no prohibited discovery limits;
4. reconcile source totals, visible ranges, fixed ordering/page controls, DOI identity, visible RIS export, and two complete ordered passes; and
5. preserve only complete successful artifacts for later PRISMA accounting. Never screen, import, create a final event, or treat P01 artifacts as candidates.

The detailed bounded initial order, flags, conditions, pacing, and hard stops are in [`p01-execution-plan.md`](p01-execution-plan.md).

## 9. Validation evidence

- **[observed offline]** The nine query files and [`translation-spec.json`](translation-spec.json) were generated from the current dictionary without a source request. Their hashes and byte lengths are recorded in the specification.
- **[observed offline]** The existing adapter is [`search_aiaa_arc.py`](../../../../../../agent-tools/academic-research/skills/academic-search/scripts/search_aiaa_arc.py) in the sibling isolated `agent-tools` worktree. Its CLI/output preflight is covered by the focused offline AIAA test file in that worktree; no live claim is made. The source-specific [`initialize_aiaa_arc_pilot.py`](../../../scripts/initialize_aiaa_arc_pilot.py) is an offline runtime materializer only; it creates no campaign or attempt until the controller invokes it at runtime.
- **[untested]** No campaign, immutable attempt manifest, live lease receipt, browser health receipt, source operation, current interface observation, source total, record, or accepted gate exists yet. `accepted_pilot_ids` remains empty.
- **[planned]** The controller will create `campaign.json`, the P01 manifest, the evidence index, and sanitized cleanup/release receipts at runtime from the shared templates, then checkpoint only immutable evidence actually produced by P01.

## 10. Remaining limits and protocol impact

- **[untested]** All current ARC source behavior remains unresolved: access, parser, field boundary, controlled/indexed terms, pair semantics, date/language/content controls, pagination, DOI identity, export, and completeness.
- **[blocked]** P01 is intentionally diagnostic-only and does not establish a report-ready run. The adapter's strict complete mode has fixed 100-record, five-page, two-pass, 20-second, zero-delay, exact-date flags; those are not forced in the initial pilot.
- **[protocol]** No concept, query relationship, source boundary, date/language/content limit, recall rule, completeness definition, or PRISMA accounting rule is changed. No source-specific fallback has been silently selected.

## Future browser operations

Historical local domain notes are not instructions to launch a fresh browser or to claim current behavior. Every future browser phase uses the shared CfT lease at `127.0.0.1:9222`, one supervised sequential phase, one adapter-owned route at a time, no fresh browser/profile/port, explicit challenge/busy disposition, and verified cleanup/release.
