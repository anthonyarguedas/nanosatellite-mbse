# S-D04-P04 observations

**Attempt:** `S-D04-P04-20260825T114742-0400`
**Campaign:** `S-D04-C01-20260824T161325-0400`
**Decision:** `D-TECH-NEXT-P04` (`controller_technical`, prospectively authorized before allocation)
**Terminal outcome:** `completed` for the assigned bounded diagnostic; no final-search acceptance
**Source operations:** 2 of 2 maximum

## Authorization and source-free gate

- **[observed]** The controller extended the finite behavior-preserving technical allocation by exactly one P04 before allocation. The updated campaign bound is three additional/technical corrective attempts: P02 and the consumed P03 lease/setup incident account for two, and exactly P04 remains. The per-attempt maximum remains two source operations. No methodological authorization was sought or needed.
- **[observed]** The corrected file-based P04 child passed `bash -n`, static one-route/one-paired-operation checks, the local 33-test focused suite, the external 20-test/35-subtest adapter suite, both CLI help checks, the nine-partition exact-byte audit, and the shared infrastructure validator before the lease.
- **[observed]** The P04 child uses the same P03 operation ladder and stop rules under a new immutable identity. It submits only `B1.ev-expert.txt`; it does not invoke any other query family, thesaurus, export, completeness, screening, import, or `S-C01` action.

## Shared CfT and live result

- **[observed]** Independent read-only preflight found the canonical Chrome for Testing endpoint `http://127.0.0.1:9222`, canonical profile, one protected inert anchor, matching runtime/on-disk version `152.0.7977.54`, browser epoch `bldqawxcF3fqkU-S9IBNeLhNxQf0jcIT`, released lease, and no orphan child/group. AC power was available.
- **[observed]** The attached child reached its live preflight under process-scoped `caffeinate -dims`: AC power, sleep assertion, and process observation all passed.
- **[observed]** Operation 1 (`P04-OP01-ROUTE-PROJECTION`) made exactly one owned-page navigation. The stabilized safe projection was healthy: HTTP 200, public paired Expert route, expected title/host/path, Compendex and Inspec controls present and checked, query field present, and no access, login, challenge, or syntax marker. The owned target was distinct, closed, disappeared, and the baseline page/target set was preserved.
- **[observed]** Operation 2 (`P04-OP02-PAIRED-DIAGNOSTIC`) ran only after the healthy route gate. It made exactly one logical paired event with two sequential component requests: Compendex first, then Inspec. Each request was bounded to one rendered page/one adapter record and retained no record. Compendex reported exact total `83`; Inspec reported exact total `46`; the paired total remains `null` because no combined total was inferred. Each selected-database mask and source/provenance summary was independently observed (`compendex` mask `1`, `inspec` mask `2`; one adapter record/25 rows seen per database).
- **[observed]** No challenge, busy response, login, CAPTCHA, syntax error, retry, provider failure, export, source-record capture, or partial prefix occurred. The adapter event stopped after count/control/provenance evidence.

## Cleanup, postflight, and accounting

- **[observed]** The attached lease exited `0`; the raw lease receipt reports `cleanup=verified-clean`, `state=released`, child exit `0`, one protected anchor before/after, and unchanged browser epoch/profile/endpoint. Sanitized cleanup and release receipts independently verify owned-page closure, anchor preservation, and controller release.
- **[observed]** The timestamp-bounded postflight power/log audit found AC power and zero Sleep/Wake markers in both checked sources. The read-only `start_chrome.py --check` also passed after release.
- **[observed]** A separate read-only `run_with_browser_lease.py --status --receipt` postflight view returned status `1` because its browser epoch receipt was stale/missing after release, while it still observed one page/anchor, released lease state, and no orphan. This is retained as a narrow controller/infrastructure metadata warning; it does not contradict the verified lease cleanup/release or the successful source receipts, and no browser launch/restart/configuration was attempted.
- **[observed]** Paired, Compendex, and Inspec totals are respectively `null`, `83`, and `46`; `records_retrieved_by_adapter=1` for each component and `records_retained=0`, `records_imported=0`. The paired total is deliberately not the arithmetic sum.

## Gates and carry-forward

- **Passed:** `G-TRANSLATION-INTEGRITY` carried from P01 by exact hash; `G-OWNED-PAGE` carried from P02 by exact hash; P04 `G-ROUTE-PROJECTION`; P04 `G-ADAPTER-DIAGNOSTIC`; bounded source access/control and paired provenance/count evidence.
- **Still unaccepted/untested:** source-native field semantics, parser echo and syntax behavior beyond the route projection, proximity/same-field semantics, date day precision, language handling, thesauri/indexed terms, pagination, export/RIS reconciliation, stable identity, full retrieval, two-pass completeness, all other query partitions, and `S-C01`.
- **[observed]** The successful bounded diagnostic does not accept the Engineering Village guideline or authorize a final event. It establishes only the recorded route and current-adapter count/control/provenance observations.

## Technical and methodological decisions

- **Code issue:** `false` for the current adapter within this bounded diagnostic: both pinned component entry points returned safe exact-count, selected-database, and provenance metadata. The historical P03 controller launch-wrapper issue remains a consumed `true` setup incident and was corrected by the file-based child. The stale postflight status view is a controller receipt-health warning, not a provider or adapter failure.
- **Methodological decision:** none. No concept, query bytes, field/source boundary, limits, identity/completeness meaning, candidate terminology, or PRISMA accounting changed.
- **Semantic impact:** none; this is controller technical evidence only.

**Explicitly:** no screening, relevance classification, candidate import, final event, or final-search record occurred.

**Next action:** preserve P03 and P04 immutably, keep the campaign diagnostic/blocked pending the remaining source-method gates and `S-C01`, and do not allocate another technical attempt under the finite P04 authorization.
